"""Pure-Python helpers. Never import OmniGibson or execute task config files."""

import hashlib
import json
import re
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET = Path("OmniGibson/omnigibson/data/og_dataset")


def read_json(path):
    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream)


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def relative(path, root=REPO_ROOT):
    return Path(path).resolve().relative_to(Path(root).resolve()).as_posix()


def fingerprint(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cell(value):
    if isinstance(value, (list, dict)):
        value = json.dumps(value, ensure_ascii=False)
    return str(value).replace("|", "\\|").replace("\n", " ")


def load_task(root, env, task_id):
    if not re.fullmatch(r"env[0-4]", env):
        raise ValueError("环境必须是 env0 到 env4")
    path = Path(root) / "env" / (env + ".json")
    data = read_json(path)
    matches = [(i, t) for i, t in enumerate(data) if t.get("task_id") == task_id]
    if len(matches) != 1:
        raise ValueError("task_id 必须唯一存在；找到 %d 条" % len(matches))
    index, task = matches[0]
    return path, index, task


def graph_issues(task):
    nodes = task["init_graph"]["nodes"]
    edges = task["init_graph"]["edges"]
    counts = Counter(n["id"] for n in nodes)
    ids = set(counts)
    issues = []
    for node_id, count in counts.items():
        if count > 1:
            issues.append({"code": "duplicate_node", "node_id": node_id,
                           "message": "节点编号重复"})
    for edge in edges:
        if edge["from_id"] not in ids or edge["to_id"] not in ids:
            issues.append({"code": "dangling_edge", "edge": edge,
                           "message": "关系引用了不存在的节点"})
    for goal in task["task_goal"]:
        for raw_id in re.findall(r"\((\d+)\)", goal):
            if int(raw_id) not in ids:
                issues.append({"code": "dangling_goal", "node_id": int(raw_id),
                               "message": "目标引用了不存在的节点"})
    parents = {}
    for edge in edges:
        if edge["relation_type"] in ("ON", "INSIDE"):
            parents.setdefault(edge["from_id"], []).append(edge["to_id"])
    # ON/INSIDE cycles make placement undefined; duplicate routes to a room are valid.
    def cyclic(node_id, stack):
        if node_id in stack:
            return True
        return any(cyclic(p, stack | {node_id}) for p in parents.get(node_id, []))
    for node in nodes:
        if cyclic(node["id"], set()):
            issues.append({"code": "placement_cycle", "node_id": node["id"],
                           "message": "ON/INSIDE 关系存在循环"})
    return issues


def inferred_rooms(node_id, task):
    """Follow only ON and INSIDE; door connectivity does not place an object."""
    nodes = {n["id"]: n for n in task["init_graph"]["nodes"]}
    parents = {}
    for edge in task["init_graph"]["edges"]:
        if edge["relation_type"] in ("ON", "INSIDE"):
            parents.setdefault(edge["from_id"], []).append(edge["to_id"])
    rooms, seen = set(), set()
    def visit(current):
        if current in seen or current not in nodes:
            return
        seen.add(current)
        node = nodes[current]
        if node["category"] == "Rooms":
            rooms.add(node["prefab_name"])
        else:
            for parent in parents.get(current, []):
                visit(parent)
    visit(node_id)
    return sorted(rooms)


def audit_sources(root):
    rows = []
    for i in range(5):
        source = Path(root) / "env" / ("env%d.json" % i)
        copy = Path(root) / "src/experiment/PEFA/env" / source.name
        tasks = read_json(source)
        rows.append({
            "env": "env%d" % i, "task_count": len(tasks),
            "source": relative(source, root), "sha256": fingerprint(source),
            "pefa_copy_exists": copy.is_file(),
            "pefa_semantically_equal": read_json(copy) == tasks if copy.is_file() else False,
            "task_id_index_mismatches": [i for i, t in enumerate(tasks) if t.get("task_id") != i],
            "duplicate_task_ids": [k for k, v in Counter(t.get("task_id") for t in tasks).items() if v > 1],
        })
    return rows


def dataset_entry(root, category, model):
    """Check actual entry files, not a guessed ID from an instance name."""
    if not category or not model:
        return {"category": category, "model": model, "entry_status": "unresolved"}
    for value in (category, model):
        if not isinstance(value, str) or value in (".", "..") or "/" in value or "\\" in value:
            return {"category": category, "model": model, "entry_status": "invalid_identifier"}
    folder = DATASET / "objects" / category / model / "usd"
    plain = folder / (model + ".usd")
    encrypted = folder / (model + ".encrypted.usd")
    files = [str(p) for p in (plain, encrypted) if (Path(root) / p).is_file()]
    return {
        "category": category, "model": model,
        "logical_usd": plain.as_posix(), "entry_files": files,
        "entry_status": "found" if files else "missing",
        "dataset_loader_encrypted_entry_exists": (Path(root) / encrypted).is_file(),
        "runtime_status": "not_tested",
    }
