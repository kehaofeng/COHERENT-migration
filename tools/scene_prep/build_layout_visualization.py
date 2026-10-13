"""Build a self-contained, read-only seven-layout diagram from local scene data."""

import argparse
import json
from collections import defaultdict
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "OmniGibson/omnigibson/data/og_dataset"
TEMPLATE = ROOT / "scene_prep/layout_visualization.template.html"

ROOM_ZH = {
    "living_room": "客厅", "bedroom": "卧室", "childs_room": "儿童房",
    "kitchen": "厨房", "dining_room": "餐厅", "bathroom": "浴室",
    "closet": "储物间", "corridor": "走廊", "empty_room": "空房间",
    "staircase": "楼梯间", "grocery_store": "超市", "bar": "吧台区",
    "garage": "车库",
    "livingroom": "客厅", "childroom": "儿童房", "utility room": "杂物间",
    "grocery store": "超市", "restaurant": "餐厅", "lower livingroom": "下生活区",
    "upper livingroom": "上生活区", "garden": "花园",
}

OBJECT_ZH = {
    "bed": "床", "sofa": "沙发", "breakfast_table": "早餐桌",
    "coffee_table": "咖啡桌", "coffee table": "咖啡桌", "fridge": "冰箱", "stove": "炉灶",
    "microwave": "微波炉", "grocery_shelf": "货架", "bar": "吧台",
    "cash_register": "收银机", "cash register": "收银机", "pedestal_table": "展台",
    "pedestal table": "展台", "grocery shelf": "货架",
    "checkout_counter": "收银台", "checkout counter": "收银台", "dining table": "餐桌", "high kitchen table": "高厨房桌",
    "grill": "烤架", "lawn": "草坪", "swing": "秋千", "stairs": "楼梯",
    "kitchen table": "厨房桌", "high table": "高桌", "cabinet": "柜子",
    "chair": "椅子", "low bookshelf": "书架", "sink": "水槽",
    "burner": "炉灶", "trash can": "垃圾桶", "storage shelf": "储物架",
    "packing box": "包装箱", "display table": "展示桌", "display bin": "展示箱",
    "shopping basket": "购物篮", "bucket": "水桶", "carton": "纸箱",
    "ottoman": "脚凳", "bar counter": "吧台", "coffee maker": "咖啡机",
    "bottom cabinet": "矮柜", "car": "汽车", "lawn table": "草坪桌",
    "swing": "秋千", "swing table": "秋千桌", "grill table": "烧烤桌",
    "grill": "烤架", "mailbox": "邮箱", "garage table": "车库桌",
}


def original_scene(scene_model, selected_names, title, note, object_file=None):
    layout = DATA / "scenes" / scene_model / "layout"
    src = Image.open(layout / "floor_insseg_0.png")
    img = src.resize((round(src.width / 10), round(src.height / 10)), Image.NEAREST)
    sem = Image.open(layout / "floor_semseg_0.png").resize(img.size, Image.NEAREST)
    categories = (DATA / "metadata/room_categories.txt").read_text().splitlines()
    runs = defaultdict(list)
    pixels = defaultdict(list)
    for y in range(img.height):
        x = 0
        while x < img.width:
            value = img.getpixel((x, y))
            start = x
            while x < img.width and img.getpixel((x, y)) == value:
                x += 1
            if value:
                runs[value].append(f"M{start} {y}h{x - start}v1h{start - x}z")
                pixels[value].extend((px, y) for px in range(start, x))

    all_points = [point for room_points in pixels.values() for point in room_points]
    xs = [point[0] for point in all_points]
    ys = [point[1] for point in all_points]
    bounds = [min(xs), min(ys), max(xs) + 1, max(ys) + 1]
    room_numbers = defaultdict(int)
    rooms = []
    for value in sorted(runs):
        points = pixels[value]
        point = points[len(points) // 2]
        sem_id = sem.getpixel(point)
        category = categories[sem_id - 1]
        room_number = room_numbers[category]
        room_numbers[category] += 1
        room_name = f"{category}_{room_number}"
        rooms.append({
            "id": value, "name": room_name,
            "label": f"{ROOM_ZH.get(category, category)} {room_number + 1}" if room_number else ROOM_ZH.get(category, category),
            "path": "".join(runs[value]), "xy": point,
        })

    scene_json = object_file or DATA / "scenes" / scene_model / "json" / f"{scene_model}_best.json"
    source = json.loads(scene_json.read_text())
    objects = []
    for name in selected_names:
        args = source["objects_info"]["init_info"][name]["args"]
        pos = source["state"]["object_registry"][name]["root_link"]["pos"]
        category = args["category"]
        objects.append({
            "name": name, "label": OBJECT_ZH.get(category, category),
            "xy": [round(img.width / 2 + pos[0] / 0.1, 1), round(img.height / 2 + pos[1] / 0.1, 1)],
        })
    return {"kind": "original", "title": title, "note": note, "size": list(img.size), "bounds": bounds, "rooms": rooms, "objects": objects}


def proposed_scenes():
    config = json.loads((ROOT / "scene_prep/config/scene_layouts_v1.json").read_text())
    scene_titles = {
        "env0": "env0 · 四房住宅", "env1": "env1 · 厨房与杂物间",
        "env2": "env2 · 超市", "env3": "env3 · 餐厅",
        "env4": "env4 · 双生活区与花园",
    }
    scenes = []
    for key, layout in config["environments"].items():
        source = json.loads((ROOT / layout["source"]).read_text())
        classes = {n["prefab_name"]: n["class_name"] for task in source for n in task["init_graph"]["nodes"]}
        objects = []
        for name, xy in layout["fixed"].items():
            cls = classes[name]
            objects.append({"name": name, "label": OBJECT_ZH.get(cls, cls), "xy": xy})
        for duplicate in layout.get("duplicate_node_instances", []):
            objects.append({"name": f"{duplicate['prefab_name']} [节点 {duplicate['node_id']}]", "label": "垃圾桶", "xy": duplicate["xy"]})
        zones = [{"name": name, "label": ROOM_ZH.get(classes.get(name, ""), name), "rect": rect}
                 for name, rect in layout["zones"].items()]
        subregions = [{"name": name, "label": "车库" if "garage" in name else "草坪", "rect": rect}
                      for name, rect in layout.get("subregions", {}).items()]
        scenes.append({
            "kind": "proposed", "title": scene_titles[key], "note": "设计初稿 · 位置是暂定的米制坐标，尚未进行三维加载或碰撞验证",
            "zones": zones, "subregions": subregions,
            "doors": [{"name": name, "xy": xy} for name, xy in layout["doors"].items()],
            "objects": objects,
            "agents": [{"name": name, "xy": xy} for name, xy in layout["agent_staging"].items()],
        })
    return scenes


def get_scenes():
    return [
        original_scene("Merom_1_int", [
            "bed_zrumze_0", "bed_zrumze_1", "sofa_xhxdqf_0",
            "breakfast_table_skczfi_0", "coffee_table_fqluyq_0",
            "fridge_xyejdx_0", "stove_rgpphy_0", "microwave_abzvij_0",
        ], "原有 1 · Merom_1_int", "数据集房间分割图 + 原任务场景文件中的主要家具位置",
            ROOT / "OmniGibson/Benchmark/tasks/Merom_1_int_best.json"),
        original_scene("house_double_floor_lower", [
            "car_supuws_0", "sofa_frlxgz_0", "coffee_table_koagbh_0",
            "fridge_xyejdx_0", "grill_sxfjac_0", "lawn_ogzsvf_0",
            "swing_yzhrgz_0", "stairs_tikozn_0",
        ], "原有 2 · house_double_floor_lower", "这张图按原任务的房屋物体文件和同名数据集底图绘制；但任务代码把 scene_model 写成 grocery_store_cafe，实际加载配置不一致",
            ROOT / "OmniGibson/Benchmark/tasks/house_double_floor_lower_best_Task1.json"),
        *proposed_scenes(),
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    scenes = get_scenes()
    rendered = TEMPLATE.read_text().replace("__SCENES_DATA__", json.dumps(scenes, ensure_ascii=False, separators=(",", ":")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    print(args.output)
    print(f"{len(scenes)} diagrams, {args.output.stat().st_size} bytes")


if __name__ == "__main__":
    main()
