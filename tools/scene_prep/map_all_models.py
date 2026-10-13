"""Build a five-environment model review table without choosing models by guesswork."""

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

from common import DATASET, REPO_ROOT, audit_sources, cell, dataset_entry, read_json, write_json
from inventory_assets import read_demo


NON_DATASET = {"Rooms", "Floor", "Region", "Agents", "AgentTool"}


def report_aliases(path):
    """Read the *candidate* category names recorded in the earlier human report."""
    aliases = defaultdict(list)
    if not path.is_file():
        return {}
    section = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[:4]
        if section not in ("## 二", "## 三", "## 四") or not line.startswith("|"):
            continue
        columns = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(columns) < 2:
            continue
        names = re.findall(r"`([^`]+)`", columns[0])
        categories = re.findall(r"`([^`]+)`", columns[1])
        if names and categories:
            key = names[-1].casefold().strip()
            for category in categories:
                if category not in aliases[key]:
                    aliases[key].append(category)
    return dict(aliases)


def catalog_models(root):
    base = Path(root) / DATASET / "objects"
    if not base.is_dir():
        raise FileNotFoundError(base)
    catalog = {}
    for category in sorted(p for p in base.iterdir() if p.is_dir() and not p.name.startswith(".")):
        models = []
        for folder in sorted(p for p in category.iterdir() if p.is_dir() and not p.name.startswith(".")):
            entry = dataset_entry(root, category.name, folder.name)
            models.append({"model": folder.name, "entry_status": entry["entry_status"],
                           "entry_files": entry["entry_files"]})
        catalog[category.name] = models
    return catalog


def make_key(env, planning_category, planning_name):
    return "|".join((env, planning_category, planning_name))


def existing_config_evidence(root):
    """Find exact instance-name matches; no task-to-scene relationship is assumed."""
    directory = Path(root) / "OmniGibson/Benchmark/tasks"
    evidence = defaultdict(list)
    scene_paths = list(directory.glob("*.json"))
    scene_paths.extend((Path(root) / DATASET / "scenes").glob("*/json/*_best.json"))
    for path in sorted(scene_paths):
        data = read_json(path)
        for name, record in data.get("objects_info", {}).get("init_info", {}).items():
            args = record.get("args", {})
            if args.get("category") and args.get("model"):
                evidence[name].append({"category": args["category"], "model": args["model"],
                                       "source": path.relative_to(root).as_posix(),
                                       "source_key": f"objects_info.init_info.{name}.args"})
    for path in sorted(directory.glob("*_Task1.py")):
        if path.name.startswith("defaults_"):
            continue
        demo = read_demo(path, root)
        for obj in demo["sections"].get("objects", []):
            if not isinstance(obj, dict) or not all(isinstance(obj.get(k), str) for k in ("name", "category", "model")):
                continue
            evidence[obj["name"]].append({"category": obj["category"], "model": obj["model"],
                                          "source": path.relative_to(root).as_posix(),
                                          "source_key": "cfg['objects']"})
    return dict(evidence)


def collect_nodes(root):
    grouped = {}
    problems = []
    task_count = 0
    node_count = 0
    for env_number in range(5):
        env = f"env{env_number}"
        for source_index, task in enumerate(read_json(Path(root) / "env" / f"{env}.json")):
            task_count += 1
            ids = Counter(node["id"] for node in task["init_graph"]["nodes"])
            for node_id, count in ids.items():
                if count > 1:
                    problems.append({"code": "duplicate_node_id", "env": env,
                                     "task_id": task["task_id"], "node_id": node_id,
                                     "count": count})
            for node_index, node in enumerate(task["init_graph"]["nodes"]):
                node_count += 1
                key = make_key(env, node["category"], node["prefab_name"])
                row = grouped.setdefault(key, {
                    "key": key, "env": env, "planning_category": node["category"],
                    "planning_name": node["prefab_name"], "class_names": [],
                    "occurrences": [], "properties": [], "states": [],
                })
                if node["class_name"] not in row["class_names"]:
                    row["class_names"].append(node["class_name"])
                for field in ("properties", "states"):
                    for value in node.get(field, []):
                        if value not in row[field]:
                            row[field].append(value)
                row["occurrences"].append({"task_id": task["task_id"],
                                           "source_index": source_index, "node_id": node["id"],
                                           "node_index": node_index})
    return grouped, problems, task_count, node_count


def build(root, selections):
    root = Path(root)
    catalog = catalog_models(root)
    aliases = report_aliases(root / "Check Result1.md")
    known_configs = existing_config_evidence(root)
    grouped, problems, task_count, node_count = collect_nodes(root)
    choices = selections.get("selections", {})
    unknown_keys = sorted(set(choices) - set(grouped))
    for key in unknown_keys:
        problems.append({"code": "unknown_selection_key", "key": key})
    rows = []
    for key, row in sorted(grouped.items()):
        if row["planning_category"] in NON_DATASET:
            row.update({"mapping_status": "non_dataset_entity", "candidate_categories": [],
                        "candidate_models": [], "selection": choices.get(key),
                        "note": "房间/区域/机器人或工具需单独映射，不应强行对应普通物品模型。"})
            if choices.get(key):
                problems.append({"code": "selection_for_non_dataset_entity", "key": key})
            rows.append(row)
            continue
        categories = []
        for class_name in row["class_names"]:
            direct = class_name.lower().replace(" ", "_")
            if direct in catalog and direct not in categories:
                categories.append(direct)
            for alias in aliases.get(class_name.casefold().strip(), []):
                if alias in catalog and alias not in categories:
                    categories.append(alias)
        candidates = [f"{category}/{item['model']}" for category in categories
                      for item in catalog[category] if item["entry_status"] == "found"]
        name_code_matches = [ref for ref in candidates if ref.split("/", 1)[1] in row["planning_name"].split("_")]
        exact_evidence = []
        for item in known_configs.get(row["planning_name"], []):
            entry = dataset_entry(root, item["category"], item["model"])
            exact_evidence.append({**item, "entry_status": entry["entry_status"],
                                   "entry_files": entry.get("entry_files", []),
                                   "note": "仿真配置中同名实例使用过该模型；尚未证明它属于这个规划环境。"})
            if entry["entry_status"] == "found":
                ref = f"{item['category']}/{item['model']}"
                if ref not in candidates:
                    candidates.insert(0, ref)
                if item["category"] not in categories:
                    categories.insert(0, item["category"])
        configured_refs = {f"{item['category']}/{item['model']}" for item in exact_evidence
                           if item["entry_status"] == "found"}
        evidence_conflict = bool(name_code_matches and configured_refs and
                                 not set(name_code_matches).intersection(configured_refs))
        choice = choices.get(key)
        status = "needs_model_selection" if candidates else "no_model_candidate"
        if choice is not None:
            selected_category = choice.get("category")
            selected_model = choice.get("model")
            evidence = choice.get("evidence")
            if (selected_category and selected_model and evidence and
                    dataset_entry(root, selected_category, selected_model)["entry_status"] == "found"):
                selected_ref = f"{selected_category}/{selected_model}"
                status = "source_backed" if selected_ref in configured_refs else "selection_recorded"
            else:
                status = "invalid_selection"
                problems.append({"code": "invalid_selection", "key": key})
        row.update({"candidate_categories": categories, "candidate_models": candidates,
                    "candidate_count": len(candidates), "name_code_matches": name_code_matches,
                    "explicit_config_evidence": exact_evidence,
                    "name_code_config_conflict": evidence_conflict,
                    "selection": choice,
                    "mapping_status": status,
                    "candidate_basis": "同名数据集类别或 Check Result1.md 中列出的候选类别；不是最终选型。"})
        rows.append(row)
    return {"schema_version": 1, "scope": "五个环境的规划物体与数据集模型对应；不选场景或坐标，不验证仿真加载。",
            "sources": audit_sources(root), "model_catalog": catalog,
            "rows": rows, "problems": problems,
            "summary": {"tasks": task_count, "node_occurrences": node_count,
                        "unique_mapping_keys": len(rows),
                        "statuses": dict(Counter(row["mapping_status"] for row in rows)),
                        "rows_with_exact_name_config_evidence": sum(bool(row.get("explicit_config_evidence")) for row in rows),
                        "rows_with_valid_name_code_candidate": sum(bool(row.get("name_code_matches")) for row in rows),
                        "name_code_config_conflicts": sum(row.get("name_code_config_conflict", False) for row in rows),
                        "graph_problems": len([p for p in problems if p["code"] == "duplicate_node_id"])}}


def write_outputs(result, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    catalog = result.pop("model_catalog")
    write_json(output / "model_catalog.json", catalog)
    write_json(output / "model_mapping.json", result)
    with (output / "model_mapping.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["对应键", "环境", "规划类别", "物体标识", "物体名称", "出现任务数", "候选模型数", "候选类别", "名称编号匹配模型", "原配置同名模型", "编号与原配置冲突", "状态", "已选类别", "已选模型", "依据"])
        for row in result["rows"]:
            choice = row["selection"] or {}
            writer.writerow([row["key"], row["env"], row["planning_category"], row["planning_name"],
                             ", ".join(row["class_names"]),
                             len({x["task_id"] for x in row["occurrences"]}),
                             row.get("candidate_count", 0), ", ".join(row["candidate_categories"]),
                             ", ".join(row.get("name_code_matches", [])),
                             ", ".join(sorted({f"{e['category']}/{e['model']}" for e in row.get("explicit_config_evidence", [])})),
                             "是" if row.get("name_code_config_conflict") else "",
                             row["mapping_status"], choice.get("category", ""),
                             choice.get("model", ""), choice.get("evidence", "")])
    summary = result["summary"]
    lines = ["# 五个环境的物体与模型对应进度", "",
             "本表只查找模型。现有场景可提供线索，但没有把任何规划环境绑定到某个场景。", "",
             f"- 任务：{summary['tasks']} 条；规划节点出现：{summary['node_occurrences']} 次。",
             f"- 按环境＋规划类别＋物体标识合并：{summary['unique_mapping_keys']} 项。",
             f"- 与原配置中的实例名完全相同且能追溯到模型的条目：{summary['rows_with_exact_name_config_evidence']} 项（仍需核对是否适用于规划环境）。",
             f"- 规划名字中的编号恰好存在于候选类别的条目：{summary['rows_with_valid_name_code_candidate']} 项（仅作为线索，不自动选定）。",
             f"- 名字编号与原配置实际模型不一致：{summary['name_code_config_conflicts']} 项，必须单独核对。",
             "- 旧报告的 210 项使用另一种去重方式，不与本表数量直接比较。", "",
             "| 状态 | 数量 | 含义 |", "| --- | ---: | --- |"]
    meanings = {"source_backed": "原配置中同名实例明确使用该模型，入口文件存在；仍需核对是否适用于规划物体",
                "selection_recorded": "已记录选型和依据，入口文件存在；仍需独立复核",
                "needs_model_selection": "找到一个或多个候选模型，尚未确认",
                "no_model_candidate": "当前类别规则下没有候选，需继续查找",
                "non_dataset_entity": "房间、区域、机器人或工具，需另一类资产对应"}
    for status, meaning in meanings.items():
        if summary["statuses"].get(status, 0):
            lines.append(f"| {status} | {summary['statuses'][status]} | {meaning} |")
    lines += ["", "## 各环境进度", "",
              "| 环境 | 对应条目 | 有原配置依据 | 待选模型 | 无候选 | 非普通模型 |",
              "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for env_number in range(5):
        env = f"env{env_number}"
        env_rows = [row for row in result["rows"] if row["env"] == env]
        counts = Counter(row["mapping_status"] for row in env_rows)
        lines.append(f"| {env} | {len(env_rows)} | {counts['source_backed']} | {counts['needs_model_selection']} | {counts['no_model_candidate']} | {counts['non_dataset_entity']} |")
    lines += ["", "完整逐项清单见 model_mapping.csv；每项的全部候选型号及出现任务见 model_mapping.json；模型入口文件见 model_catalog.json。",
              "候选类别来自同名目录及旧报告 Check Result1.md，均未自动确认为最终模型。", ""]
    if result["problems"]:
        lines += ["## 输入数据问题", ""]
        for problem in result["problems"]:
            lines.append("- " + cell(problem))
    (output / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--selections", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    selections = args.selections or args.repo_root / "scene_prep/config/model_selections.json"
    output = args.output or args.repo_root / "scene_prep/reports/all_env_models"
    result = build(args.repo_root, read_json(selections))
    write_outputs(result, output)
    print(f"已生成 {result['summary']['unique_mapping_keys']} 项物体对应表：{output}")
    print("状态：保留有依据的已记录选型；其余仅列候选，未验证三维加载。")


if __name__ == "__main__":
    main()
