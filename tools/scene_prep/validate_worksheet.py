"""Validate a review worksheet's completeness and freshness, not simulation readiness."""

import argparse
import math
from pathlib import Path

from common import REPO_ROOT, fingerprint, load_task, read_json, write_json


def validate(root, worksheet):
    draft = read_json(worksheet)
    problems = []
    for source, expected in draft.get("source_hashes", {}).items():
        path = Path(root) / source
        if not path.is_file() or fingerprint(path) != expected:
            problems.append("来源已变更或丢失，请重新生成：" + source)
    _, _, task = load_task(root, draft["env"], draft["task_id"])
    expected_ids = {n["id"] for n in task["init_graph"]["nodes"]}
    actual_ids = [r["node_id"] for r in draft["entities"]]
    if len(actual_ids) != len(set(actual_ids)):
        problems.append("对应表存在重复节点")
    if set(actual_ids) != expected_ids:
        problems.append("对应表没有完整覆盖原始任务节点")
    sources = {}
    for row in draft["entities"]:
        for candidate in row["scene_or_demo_candidates"]:
            for field, size in (("position", 3), ("orientation", 4)):
                if field not in candidate:
                    continue
                value = candidate[field]
                if not isinstance(value, list) or len(value) != size or not all(type(x) in (int, float) and math.isfinite(x) for x in value):
                    problems.append("节点 %s 的候选 %s 缺少合法 %s" % (row["node_id"], candidate["name"], field))
            # Re-check evidence so renamed/moved objects cannot survive stale reports.
            if candidate["kind"] == "scene_object":
                path = candidate["source"]["path"]
                if path not in sources:
                    sources[path] = read_json(Path(root) / path)
                original = sources[path]["objects_info"]["init_info"].get(candidate["name"])
                if original is None:
                    problems.append("候选已不在底图中：" + candidate["name"])
            asset_ref = candidate.get("asset_reference", {})
            if asset_ref.get("entry") and not (Path(root) / asset_ref["entry"]).is_file():
                problems.append("机器人资产入口丢失：" + asset_ref["entry"])
            for entry in candidate.get("asset", {}).get("entry_files", []):
                if not (Path(root) / entry).is_file():
                    problems.append("场景资产入口丢失：" + entry)
        for model in row["model_candidates"]:
            for entry in model.get("entry_files", []):
                if not (Path(root) / entry).is_file():
                    problems.append("候选模型入口丢失：" + entry)
    return {
        "worksheet_valid": not problems,
        "problems": sorted(set(problems)),
        "node_count": len(actual_ids),
        "ready_to_generate": False,
        "runtime_status": "not_tested",
        "note": "此检查仅验工作表结构、来源一致性和已记录文件；候选选择、状态、布局、加密内部依赖及实际加载仍待处理。",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--worksheet", type=Path)
    args = parser.parse_args()
    path = args.worksheet or args.repo_root / "scene_prep/reports/env0_task1/mapping_candidates.json"
    result = validate(args.repo_root, path)
    write_json(path.parent / "worksheet_validation.json", result)
    print("工作表检查：%s；正式配置：待补齐；三维加载：未验证" % ("通过" if result["worksheet_valid"] else "失败"))
    for problem in result["problems"]:
        print("- " + problem)
    return 0 if result["worksheet_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
