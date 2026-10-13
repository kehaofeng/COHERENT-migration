"""Build the five-environment asset review visualization from local reports."""

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "scene_prep/reports/all_env_models/model_mapping.json"
LAYOUTS = ROOT / "scene_prep/config/scene_layouts_v1.json"
TEMPLATE = ROOT / "scene_prep/asset_visualization.template.html"

TITLES = {
    "env0": "四房住宅",
    "env1": "厨房与杂物间",
    "env2": "超市",
    "env3": "餐厅",
    "env4": "双生活区与花园",
}


def build_data():
    report = json.loads(REPORT.read_text())
    layouts = json.loads(LAYOUTS.read_text())["environments"]
    counts = {item["env"]: item["task_count"] for item in report["sources"]}
    environments = []
    for env, title in TITLES.items():
        layout = layouts[env]
        rows = []
        for row in report["rows"]:
            if row["env"] != env:
                continue
            selection = row.get("selection") or {}
            rows.append({
                "key": row["key"],
                "name": row["planning_name"],
                "category": row["planning_category"],
                "class": ", ".join(row["class_names"]),
                "tasks": len({o["task_id"] for o in row["occurrences"]}),
                "status": row["mapping_status"],
                "selected": "/".join(filter(None, (selection.get("category"), selection.get("model")))),
                "evidence": selection.get("evidence", ""),
                "candidates": row.get("candidate_models", []),
                "name_match": row.get("name_code_matches", []),
            })
        environments.append({
            "env": env,
            "title": title,
            "task_count": counts[env],
            "zones": layout["zones"],
            "subregions": layout.get("subregions", {}),
            "fixed": layout["fixed"],
            "doors": layout["doors"],
            "agents": layout["agent_staging"],
            "duplicates": layout.get("duplicate_node_instances", []),
            "rows": rows,
        })
    return environments


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    data = build_data()
    html = TEMPLATE.read_text().replace(
        "__ENVIRONMENTS_DATA__",
        json.dumps(data, ensure_ascii=False, separators=(",", ":")),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html)
    print(f"{args.output}: {len(data)} environments, {sum(len(e['rows']) for e in data)} entries, {len(html)} bytes")


if __name__ == "__main__":
    main()
