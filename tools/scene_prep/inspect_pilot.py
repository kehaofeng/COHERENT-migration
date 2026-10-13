"""Build a reproducible, source-backed review worksheet without running simulation."""

import argparse
import ast
from collections import Counter
from pathlib import Path

from common import REPO_ROOT, cell, dataset_entry, fingerprint, read_json, relative, write_json
from extract_task_entities import extract
from inventory_assets import build_inventory, static_value


RELATIONS_ZH = {"ON": "在……上面", "INSIDE": "在……里面", "LEADING TO": "连接房间", "WITH": "携带工具"}


def reference_coordinates(path, root):
    text = path.read_text(encoding="utf-8")
    result = {}
    for statement in ast.parse(text).body:
        if not isinstance(statement, ast.Assign):
            continue
        for target in statement.targets:
            if isinstance(target, ast.Name) and target.id in ("birthpose", "landpose", "roompose", "articulations"):
                result[target.id] = {"value": static_value(statement.value, text),
                                     "source": relative(path, root), "line": statement.lineno}
    return result


def make_candidates(entity, inventory, review, root):
    category = entity["category"]
    objects = inventory["scene"]["objects"]
    sections = inventory["demo"]["sections"]
    room_aliases = review["room_alias_candidates"]
    rooms = [room_aliases.get(r, r) for r in entity["inferred_rooms"]]
    note = review["node_notes"].get(str(entity["id"]), {})
    categories = review["category_candidates"].get(entity["class_name"], [entity["class_name"].replace(" ", "_")])
    candidates = []
    if category == "Rooms":
        name = room_aliases.get(entity["prefab_name"])
        if name in inventory["scene"]["rooms"]:
            candidates.append({"kind": "room", "name": name, "source": inventory["scene"]["source"],
                               "note": "只确认该房间标签出现在场景中，区域边界尚未验证。"})
    elif category == "Agents":
        agents = sections.get("agents", [])
        matches = [a for a in agents if a.get("name") == entity["prefab_name"]]
        if not matches and entity["class_name"].replace(" ", "_") == "robot_arm":
            matches = [a for a in agents if a.get("type") == "FrankaAgent"]
        for agent in matches:
            asset = review["agent_asset_references"].get(agent["type"], {})
            candidates.append({"kind": "agent", "name": agent["name"], "config": agent,
                               "reuse_instance": agent["name"] == entity["prefab_name"],
                               "asset_reference": asset,
                               "entry_exists": (Path(root) / asset["entry"]).is_file() if asset.get("entry") else False,
                               "source": inventory["demo"]["section_sources"]["agents"]})
    elif category == "AgentTool":
        asset = review["agent_asset_references"]["QuadrotorAgent"]
        candidates.append({"kind": "embedded_tool", "name": "无人机资产中的篮筐（子物体路径待核对）",
                           "asset_reference": asset, "entry_exists": (Path(root) / asset["entry"]).is_file()})
    else:
        preferred = note.get("preferred_scene_names", [])
        if category == "Floor":
            categories = ["floors"]
        for obj in objects:
            eligible = obj["name"] in preferred if preferred else obj["args"].get("category") in categories
            if not eligible:
                continue
            # Generic furniture/floor candidates are narrowed by the planning room.
            if not preferred and rooms and not set(rooms).intersection(obj["rooms"]):
                continue
            candidates.append({"kind": "scene_object", "name": obj["name"], "asset": obj["asset"],
                               "position": obj["position"], "orientation": obj["orientation"],
                               "bounding_box": obj["args"].get("bounding_box"),
                               "scene_rooms": obj["rooms"], "planning_room_match": bool(set(rooms).intersection(obj["rooms"])) if rooms else None,
                               "source": obj["source"]})
        for obj in sections.get("objects", []):
            if obj.get("name") not in preferred and obj.get("name") != entity["prefab_name"]:
                continue
            candidates.append({"kind": "demo_object", "name": obj["name"], "config": obj,
                               "source": inventory["demo"]["section_sources"]["objects"],
                               "note": "动态路径和位姿表达式保持原样，未当作有效数值配置。"})
    # Preserve every available model candidate. Only Markdown summaries truncate lists.
    models = [] if category in ("Rooms", "Floor", "Agents", "AgentTool") else [m for m in inventory["models"] if m["category"] in categories]
    return candidates, models


def prepare(root, config_path, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    review = read_json(config_path)
    env, task_id = review["env"], review["task_id"]
    task = extract(root, env, task_id, output / "inventories")
    inventory = build_inventory(root, root / review["base_scene"], root / review["demo"], output / "inventories/asset_inventory.json")
    reference = root / "OmniGibson/Benchmark/tasks/defaults_Merom_1_int_Task1.py"
    coords = reference_coordinates(reference, root) if reference.is_file() else {}
    write_json(output / "inventories/reference_coordinates.json", coords)
    rows, issues = [], list(task["graph_issues"])
    for entity in task["entities"]:
        notes = review["node_notes"].get(str(entity["id"]), {})
        candidates, models = make_candidates(entity, inventory, review, root)
        row = {
            "key": entity["key"], "node_id": entity["id"], "label_zh": notes.get("label_zh", entity["class_name"]),
            "planning_name": entity["prefab_name"], "planning_category": entity["category"],
            "in_goal": entity["in_goal"], "initial_relations": entity["initial_relations"],
            "initial_states": entity["states"], "required_properties": entity["properties"],
            "planning_rooms": entity["inferred_rooms"], "scene_or_demo_candidates": candidates,
            "model_candidates": models, "notes": notes.get("note", ""),
            "mapping_status": "candidate" if candidates or models else "unresolved",
            "selected_candidate": None, "placement_status": "not_confirmed", "runtime_status": "not_tested",
        }
        rows.append(row)
        if entity["category"] not in ("Rooms", "Doors") and not entity["has_initial_placement_relation"]:
            issues.append({"code": "missing_initial_relation", "node_id": entity["id"], "message": "规划图未说明初始支撑面或容器；需要补充摆放约定。"})
        for candidate in candidates:
            if candidate.get("planning_room_match") is False:
                issues.append({"code": "room_mismatch", "node_id": entity["id"], "message": "候选 %s 所在场景房间 %s 与规划房间 %s 不一致。" % (candidate["name"], candidate["scene_rooms"], entity["inferred_rooms"])})
        if entity["category"] == "Agents" and not any(c.get("reuse_instance") for c in candidates):
            issues.append({"code": "missing_agent_instance", "node_id": entity["id"], "message": "演示没有这台独立机器人；已有模型可作为新增实例的候选。"})
        if not candidates and not models:
            issues.append({"code": "no_candidate", "node_id": entity["id"], "message": "当前规则及来源中没有候选。"})
    draft = {"schema_version": 1, "env": env, "task_id": task_id, "goal": task["goal_instruction"],
             "base_scene": review["base_scene"], "base_scene_status": review["base_scene_status"],
             "scope": "完整规划图的候选工作表，不是可执行配置；未裁掉背景物品。",
             "source_hashes": {relative(config_path, root): fingerprint(config_path), task["source"]: task["source_sha256"], inventory["scene"]["source"]: inventory["scene"]["sha256"], inventory["demo"]["source"]: inventory["demo"]["sha256"], **{p: fingerprint(root / p) for p in review.get("evidence_files", []) if (root / p).is_file()}},
             "entities": rows, "issues": issues, "ready_to_generate": False}
    write_json(output / "mapping_candidates.json", draft)
    write_report(output, root, draft, task, inventory, review)
    return draft


def write_report(output, root, draft, task, inventory, review):
    rows = draft["entities"]
    counts = Counter(r["planning_category"] for r in rows)
    asset_counts = Counter(m["entry_status"] for m in inventory["models"])
    audit = read_json(output / "inventories/source_audit.json")
    label = {r["node_id"]: r["label_zh"] for r in rows}
    lines = ["# env0 / task1 首轮场景与资产核对", "",
             "目标：无人机降落到餐桌上。任务按 task_id=1 选取，源文件中的列表下标为 %d。" % task["source_index"], "",
             "**当前完成的是任务提取、候选场景核对和资产入口检查。正式三维任务配置尚未生成。** 所有候选均需按本任务初始条件确认，文件存在不代表模型已经加载成功。", "",
             "## 1. 本次结果", "",
             "- 保留全部 %d 个节点和 %d 条初始关系，目标直接涉及无人机 22 和餐桌 13。" % (len(rows), len(task["edges"])),
             "- 节点分类：" + "；".join("%s：%d" % item for item in counts.items()) + "。",
             "- 候选底图：Merom_1_int；场景 JSON 有 %d 个对象。这些包含墙、地板、家具等，不能与规划节点数直接比较。" % len(inventory["scene"]["objects"]),
             "- 全模型库扫描 %d 个模型目录，其中 %d 个找到 USD 入口、%d 个未找到约定入口。此数字不表示试点任务使用全部模型。" % (len(inventory["models"]), asset_counts["found"], asset_counts["missing"]),
             "- 根目录与 PEFA 的五份任务文件语义一致：%s。共 %d 条任务。" % ("是" if all(r["pefa_semantically_equal"] for r in audit) else "否，见 source_audit.json", sum(r["task_count"] for r in audit)),
             "- 未启动仿真，未调用规划模型接口。", "",
             "## 2. 最先要解决的差异", "",
             "1. **无人机起点不同。** 规划要求在儿童房；演示 cfg 的位置为 `[1.7745543718338013, 7, land_height]`，与 defaults 的客厅地面降落点对应，不能照搬。",
             "2. **规划有两台机械臂。** 演示只有 `franka_0`；卧室中的 `robot_arm_bedroom` 需要独立实例和出生位置。",
             "3. **餐桌的房间标签不同。** 规划餐桌在客厅，候选桌子在场景的 `dining_room_0`。需要明确是否把客餐厅合并为一个规划区域，或改变场景选择/布局。",
             "4. **面包初始位置未给出。** 任务仍包含面包及 HOT 状态，但没有其 ON/INSIDE 关系。不能套用别的任务中的位置。",
             "5. **床的编号不能照抄。** 规划 `bed_0` 在卧室、`bed_1` 在儿童房；候选场景中 `bed_zrumze_1` 才在卧室，`bed_zrumze_0` 在儿童房。",
             "6. **门、篮筐和高台需要单独核对。** 门应按连接房间匹配；篮筐可能已经包含在无人机资产内；高桌必须满足高度和支撑要求。", "",
             "## 3. 每个节点的对应工作表", "",
             "候选是待确认建议，不是已确认的复现对应关系。下表只显示少量候选；完整列表见 mapping_candidates.json。", "",
             "| ID | 物品/区域 | 规划名字 | 初始房间 | 已有场景或演示候选 | 模型库候选数 | 需要处理的事项 |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for row in rows:
        candidates = row["scene_or_demo_candidates"]
        display = "; ".join(c["name"] + ("（只复用模型，需新增实例）" if c.get("reuse_instance") is False else "") for c in candidates[:3])
        if len(candidates) > 3:
            display += "（另有 %d 个）" % (len(candidates) - 3)
        note = row["notes"] or ("核对初始关系后确认复用。" if candidates else "选定具体模型，补充摆放位置。")
        lines.append("| " + " | ".join(cell(v) for v in [row["node_id"], row["label_zh"], row["planning_name"], ", ".join(row["planning_rooms"]) or "未给出", display or "未找到直接对应", len(row["model_candidates"]), note]) + " |")
    lines.extend(["", "## 4. 已找到的坐标是什么", "",
                  "场景候选的 position 是底图中物体原有坐标，记录在 mapping_candidates.json。演示中的出生位置和降落点另存于 inventories/reference_coordinates.json。", "",
                  "例如餐桌的物体坐标和无人机降落坐标是两回事：前者用于摆桌子，后者用于让无人机到达桌面上方/表面。不能把桌子的根节点坐标直接当作降落点。", "",
                  "动态表达式以 unresolved_expression 保存。程序没有执行配置中的导入或函数，也没有把缺少的坐标填为零。", "",
                  "下面列出已有坐标的几个候选，便于直接查看。数字为场景原始 root_link 位置，单位按本项目的米制配置理解；它们不是物体表面位置或机器人操作点。表中保留四位小数，完整精度见 JSON。", "",
                  "| 规划物品 | 场景实例 | 实际模型类别/编号 | 原始位置 [X, Y, Z] |",
                  "| --- | --- | --- | --- |"])
    for row in rows:
        if row["node_id"] not in (11, 12, 13, 14, 27, 28):
            continue
        for c in row["scene_or_demo_candidates"]:
            if c["kind"] == "scene_object":
                lines.append("| " + " | ".join(cell(v) for v in [row["label_zh"], c["name"], c["asset"]["category"] + "/" + c["asset"]["model"], [round(v, 4) for v in c["position"]]]) + " |")
    lines.extend(["", "## 5. 程序检出的具体问题", ""])
    for issue in draft["issues"]:
        lines.append("- 节点 %s（%s）：%s" % (issue.get("node_id", "—"), label.get(issue.get("node_id"), "图结构"), issue["message"]))
    scene_missing = [o["name"] for o in inventory["scene"]["objects"] if o["asset"].get("entry_status") == "missing"]
    lines.extend(["", "底图内未找到约定资产入口的对象：" + ("、".join(scene_missing) if scene_missing else "本次未发现。"), "",
                  "## 6. 下一步操作顺序", "",
                  "1. 先决定餐桌所属规划区域和儿童房无人机起点；这些会影响本任务的初始布局。",
                  "2. 确认两张床、沙发、茶几、冰箱等候选；继续选定高台、柜子与小物品模型。",
                  "3. 在工作表中落实门连接、篮筐附属关系，以及缺失的第二台机械臂。",
                  "4. 补齐位置和状态后，再生成正式任务配置。服务器可用后检查碰撞、大小、支撑面和降落空间。", "",
                  "## 7. 相关文件", "",
                  "- [完整节点清单](inventories/task_entities.md)",
                  "- [完整候选与原始配置依据](mapping_candidates.json)",
                  "- [扫描目录、场景和演示配置](inventories/asset_inventory.json)",
                  "- [演示坐标原始表达式](inventories/reference_coordinates.json)",
                  "- [数据副本对照](inventories/source_audit.json)", ""])
    for p in review.get("evidence_files", []):
        if p.endswith(".png"):
            import os
            target = Path(os.path.relpath(root / p, output)).as_posix()
            lines.extend(["### 原项目已有画面：" + Path(p).name, "", "![原项目场景参考，不是本次生成的仿真结果](%s)" % target, ""])
    (output / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    config = args.config or args.repo_root / "scene_prep/config/env0_task1_review.json"
    output = args.output or args.repo_root / "scene_prep/reports/env0_task1"
    draft = prepare(args.repo_root, config, output)
    print("已生成 %d 个节点的候选工作表：%s" % (len(draft["entities"]), output / "README.md"))
    print("状态：候选待确认；没有生成可执行仿真配置。")


if __name__ == "__main__":
    main()
