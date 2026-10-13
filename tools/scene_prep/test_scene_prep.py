"""Regression checks for real data-loss and false-confirmation risks."""

import json
import tempfile
import unittest
from pathlib import Path

from common import DATASET, REPO_ROOT, dataset_entry, graph_issues, inferred_rooms, load_task
from extract_task_entities import extract
from inventory_assets import read_demo, read_scene
from inspect_pilot import make_candidates
from map_all_models import build, report_aliases
from validate_worksheet import validate


class ScenePrepTests(unittest.TestCase):
    def test_encrypted_entry_and_mismatched_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / DATASET / "objects/kebab/ezgwob/usd/ezgwob.encrypted.usd"
            path.parent.mkdir(parents=True)
            path.touch()
            record = dataset_entry(tmp, "kebab", "ezgwob")
            self.assertEqual(record["entry_status"], "found")
            self.assertTrue(record["dataset_loader_encrypted_entry_exists"])
            self.assertEqual(dataset_entry(tmp, "kebab", "cewhbv")["entry_status"], "missing")

    def test_config_is_not_executed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "demo.py"
            path.write_text("raise RuntimeError('must not execute')\ncfg['objects'] = [{'name':'kebab_cewhbv_0','category':'kebab','model':'ezgwob','position':birthpose['kebab_cewhbv_0']}]\n")
            demo = read_demo(path, tmp)
            obj = demo["sections"]["objects"][0]
            self.assertEqual(obj["model"], "ezgwob")
            self.assertIn("unresolved_expression", obj["position"])

    def test_graph_validation_and_transitive_room(self):
        task = {"init_graph": {"nodes": [
            {"id": 0, "category": "Rooms", "prefab_name": "kitchen"},
            {"id": 1, "category": "Furniture", "prefab_name": "table"},
            {"id": 2, "category": "Food", "prefab_name": "bread"}],
            "edges": [{"from_id": 1, "to_id": 0, "relation_type": "INSIDE"},
                      {"from_id": 2, "to_id": 1, "relation_type": "ON"}]}, "task_goal": {}}
        self.assertEqual(inferred_rooms(2, task), ["kitchen"])
        task["init_graph"]["edges"].append({"from_id": 1, "to_id": 2, "relation_type": "ON"})
        self.assertIn("placement_cycle", {i["code"] for i in graph_issues(task)})
        task["init_graph"]["edges"].append({"from_id": 2, "to_id": 999, "relation_type": "ON"})
        task["init_graph"]["nodes"].append(task["init_graph"]["nodes"][0])
        task["task_goal"] = {"on_<bread>(2)_<missing>(999)": [1, []]}
        self.assertTrue({"duplicate_node", "dangling_edge", "dangling_goal"}.issubset({i["code"] for i in graph_issues(task)}))

    def test_extract_keeps_background_and_missing_bread_placement(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = extract(REPO_ROOT, "env0", 1, tmp)
            self.assertEqual(len(result["entities"]), 31)
            bread = next(n for n in result["entities"] if n["id"] == 26)
            self.assertFalse(bread["in_goal"])
            self.assertFalse(bread["has_initial_placement_relation"])
            self.assertEqual(next(n for n in result["entities"] if n["id"] == 22)["inferred_rooms"], ["childroom_0"])

    def test_scene_uses_args_model_not_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "scene.json"
            path.write_text(json.dumps({"objects_info": {"init_info": {"kebab_cewhbv_0": {"args": {"name": "kebab_cewhbv_0", "category": "kebab", "model": "ezgwob"}}}}, "state": {"object_registry": {"kebab_cewhbv_0": {"root_link": {"pos": [1, 2, 3], "ori": [0, 0, 0, 1]}}}}}))
            self.assertEqual(read_scene(path, tmp)["objects"][0]["asset"]["model"], "ezgwob")

    def test_task_id_not_assumed_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "env/env0.json"
            path.parent.mkdir()
            path.write_text(json.dumps([{"task_id": 42}]))
            self.assertEqual(load_task(tmp, "env0", 42)[1], 0)
            with self.assertRaises(ValueError):
                load_task(tmp, "env0", 0)

    def test_second_arm_is_not_bound_to_existing_arm(self):
        _, _, task = load_task(REPO_ROOT, "env0", 1)
        entity = next(n for n in task["init_graph"]["nodes"] if n["id"] == 50)
        entity = {**entity, "inferred_rooms": ["bedroom_0"]}
        review = json.loads((REPO_ROOT / "scene_prep/config/env0_task1_review.json").read_text())
        demo = read_demo(REPO_ROOT / review["demo"], REPO_ROOT)
        inventory = {"scene": {"objects": []}, "demo": demo, "models": []}
        candidates, _ = make_candidates(entity, inventory, review, REPO_ROOT)
        self.assertEqual(len(candidates), 1)
        self.assertFalse(candidates[0]["reuse_instance"])

    def test_stale_or_incomplete_worksheet_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "worksheet.json"
            path.write_text(json.dumps({"env": "env0", "task_id": 1, "source_hashes": {"env/env0.json": "stale"}, "entities": []}))
            result = validate(REPO_ROOT, path)
            self.assertFalse(result["worksheet_valid"])
            self.assertFalse(result["ready_to_generate"])
            self.assertGreaterEqual(len(result["problems"]), 2)

    def test_all_environment_mapping_preserves_ambiguous_source_and_does_not_guess_model(self):
        result = build(REPO_ROOT, {"selections": {}})
        self.assertEqual(result["summary"]["tasks"], 102)
        self.assertEqual(result["summary"]["node_occurrences"], 3069)
        self.assertEqual(result["summary"]["unique_mapping_keys"], 262)
        self.assertIn({"code": "duplicate_node_id", "env": "env3", "task_id": 18,
                       "node_id": 24, "count": 2}, result["problems"])
        rows = {row["key"]: row for row in result["rows"]}
        kebab = rows["env4|Food|kebab_cewhbv_0"]
        self.assertIn("kebab/ezgwob", kebab["candidate_models"])
        self.assertEqual(kebab["mapping_status"], "needs_model_selection")
        self.assertTrue(kebab["explicit_config_evidence"])
        self.assertEqual(kebab["name_code_matches"], ["kebab/cewhbv"])
        self.assertTrue(kebab["name_code_config_conflict"])
        apple = rows["env2|Fruit|apple_brkitw_0"]
        self.assertNotIn("apple/brkitw", apple["candidate_models"])
        self.assertEqual(apple["name_code_matches"], [])
        self.assertEqual(apple["mapping_status"], "needs_model_selection")

    def test_prior_aliases_remain_candidates(self):
        aliases = report_aliases(REPO_ROOT / "Check Result1.md")
        self.assertIn("milk_carton", aliases["milkbox"])
        self.assertIn("bread_slice", aliases["bread"])


if __name__ == "__main__":
    unittest.main()
