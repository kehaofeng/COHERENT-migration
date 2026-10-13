"""Extract one task, keeping all nodes including non-goal background entities."""

import argparse
import re
from pathlib import Path

from common import REPO_ROOT, audit_sources, cell, fingerprint, graph_issues, inferred_rooms, load_task, relative, write_json


def extract(root, env, task_id, output):
    source, index, task = load_task(root, env, task_id)
    edges = task["init_graph"]["edges"]
    goal_ids = {int(x) for g in task["task_goal"] for x in re.findall(r"\((\d+)\)", g)}
    entities = []
    for node in task["init_graph"]["nodes"]:
        outgoing = [e for e in edges if e["from_id"] == node["id"]]
        entities.append({**node,
            "key": "%s/task%d/node%d" % (env, task_id, node["id"]),
            "in_goal": node["id"] in goal_ids,
            "inferred_rooms": inferred_rooms(node["id"], task),
            "initial_relations": outgoing,
            "has_initial_placement_relation": any(e["relation_type"] in ("ON", "INSIDE") for e in outgoing),
        })
    result = {
        "schema_version": 1, "env": env, "task_id": task_id, "source_index": index,
        "source": relative(source, root), "source_sha256": fingerprint(source),
        "goal_instruction": task["goal_instruction"], "task_goal": task["task_goal"],
        "entities": entities, "edges": edges, "graph_issues": graph_issues(task),
    }
    output = Path(output)
    write_json(output / "task_entities.json", result)
    write_json(output / "source_audit.json", audit_sources(root))
    names = {n["id"]: n["class_name"] for n in entities}
    lines = ["# %s / task%d 规划物品与初始关系" % (env, task_id), "",
             "目标：" + "；".join(task["goal_instruction"]), "",
             "此清单保留全部节点。房间、地面和机器人也在其中，不能把节点总数当作普通物品数。", "",
             "关系词：ON＝在上面；INSIDE＝在里面；LEADING TO＝门连接到房间；WITH＝带有工具。", "",
             "| ID | 名称 | 规划标识 | 类型 | 初始关系 | 推得的房间 | 目标直接涉及 |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for n in entities:
        relations = ["%s → %s(%s)" % (e["relation_type"], names.get(e["to_id"], "缺失节点"), e["to_id"]) for e in n["initial_relations"]]
        lines.append("| " + " | ".join(cell(v) for v in [n["id"], n["class_name"], n["prefab_name"], n["category"], "; ".join(relations) or "未提供", ", ".join(n["inferred_rooms"]) or "未推得", "是" if n["in_goal"] else "否"]) + " |")
    lines.extend(["", "这份规划数据给的是初始关系。具体三维坐标应从选定场景读取或另行配置。", ""])
    (output / "task_entities.md").write_text("\n".join(lines), encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--env", default="env0")
    parser.add_argument("--task-id", type=int, default=1, help="数据中的 task_id，不是未经核对的列表下标")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or args.repo_root / ("scene_prep/inventories/%s_task%d" % (args.env, args.task_id))
    result = extract(args.repo_root, args.env, args.task_id, output)
    print("已提取 %d 个节点、%d 条关系：%s" % (len(result["entities"]), len(result["edges"]), output))
    return 1 if result["graph_issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
