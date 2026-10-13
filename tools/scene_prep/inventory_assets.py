"""Index dataset entry files, a selected scene and literal demo config fields."""

import argparse
import ast
from pathlib import Path

from common import DATASET, REPO_ROOT, dataset_entry, fingerprint, read_json, relative, write_json


def static_value(node, text):
    """Literal fields only. Preserve dynamic expressions, never eval/import them."""
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError):
        if isinstance(node, ast.Dict):
            result = {}
            for key, value in zip(node.keys, node.values):
                if key is not None and isinstance(key, ast.Constant) and isinstance(key.value, str):
                    result[key.value] = static_value(value, text)
            return result
        if isinstance(node, (ast.List, ast.Tuple)):
            return [static_value(v, text) for v in node.elts]
        return {"unresolved_expression": ast.get_source_segment(text, node), "line": node.lineno}


def read_demo(path, root):
    text = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(text)
    config, sources = {}, {}
    for statement in tree.body:
        if not isinstance(statement, ast.Assign):
            continue
        for target in statement.targets:
            if not isinstance(target, ast.Subscript) or not isinstance(target.value, ast.Name) or target.value.id != "cfg":
                continue
            try:
                key = ast.literal_eval(target.slice)
            except (ValueError, TypeError):
                continue
            config[key] = static_value(statement.value, text)
            sources[key] = {"path": relative(path, root), "line": statement.lineno}
    return {"source": relative(path, root), "sha256": fingerprint(path),
            "sections": config, "section_sources": sources,
            "note": "只读取字面量；未解析的表达式不能用作实际坐标。"}


def read_scene(path, root):
    data = read_json(path)
    info = data["objects_info"]["init_info"]
    states = data["state"]["object_registry"]
    items = []
    for name, record in sorted(info.items()):
        args = record["args"]
        state = states.get(name, {})
        rooms = args.get("in_rooms") or []
        if isinstance(rooms, str):
            rooms = [rooms]
        items.append({
            "name": name, "args": args, "rooms": rooms,
            "position": state.get("root_link", {}).get("pos"),
            "orientation": state.get("root_link", {}).get("ori"),
            "joints": state.get("joints", {}),
            "state_exists": name in states,
            "asset": dataset_entry(root, args.get("category"), args.get("model")) if not args.get("usd_path") else {"explicit_usd_path": args["usd_path"], "entry_status": "requires_explicit_path_check"},
            "source": {"path": relative(path, root), "json_key": "objects_info.init_info." + name},
        })
    return {"source": relative(path, root), "sha256": fingerprint(path), "objects": items,
            "state_only_names": sorted(set(states) - set(info)),
            "rooms": sorted({r for item in items for r in item["rooms"]})}


def build_inventory(root, scene, demo, output):
    base = Path(root) / DATASET / "objects"
    if not base.is_dir():
        raise FileNotFoundError("找不到模型库目录：%s" % base)
    models = []
    for category in sorted(p for p in base.iterdir() if p.is_dir() and not p.name.startswith(".")):
        for model in sorted(p for p in category.iterdir() if p.is_dir() and not p.name.startswith(".")):
            models.append(dataset_entry(root, category.name, model.name))
    result = {
        "schema_version": 1, "dataset_path": DATASET.as_posix(),
        "key_file_exists": (Path(root) / "OmniGibson/omnigibson/data/omnigibson.key").is_file(),
        "models": models, "scene": read_scene(scene, root), "demo": read_demo(demo, root),
        "scope": "入口文件存在性和配置字段；未解析加密模型内部依赖，未验证三维加载。",
    }
    write_json(output, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--scene", default="OmniGibson/Benchmark/tasks/Merom_1_int_best.json")
    parser.add_argument("--demo", default="OmniGibson/Benchmark/tasks/Merom_1_int_Task1.py")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or args.repo_root / "scene_prep/inventories/merom_inventory.json"
    result = build_inventory(args.repo_root, args.repo_root / args.scene, args.repo_root / args.demo, output)
    print("已扫描 %d 个模型目录、%d 个场景对象：%s" % (len(result["models"]), len(result["scene"]["objects"]), output))


if __name__ == "__main__":
    main()
