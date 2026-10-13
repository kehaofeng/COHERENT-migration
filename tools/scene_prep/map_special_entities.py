"""Map non-dataset planning nodes to layout or robot configuration work."""

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "scene_prep/reports/all_env_models/model_mapping.json"
LAYOUTS = ROOT / "scene_prep/config/scene_layouts_v1.json"
OUTPUT_JSON = ROOT / "scene_prep/config/special_entities_v1.json"
OUTPUT_MD = ROOT / "scene_prep/SPECIAL_ENTITIES_V1.md"

LABELS = {
    "Rooms": ("房间/语义区域", "room_region"),
    "Floor": ("地面", "floor_geometry"),
    "Region": ("子区域", "subregion"),
    "Agents": ("机器人", "robot_instance"),
    "AgentTool": ("机器人附属工具", "robot_attachment"),
}


def floor_zone(name, zones):
    candidates = (name.removesuffix("_floor"), name.replace("_floor_", "_"))
    return next((candidate for candidate in candidates if candidate in zones), None)


def build():
    report = json.loads(REPORT.read_text())
    layouts = json.loads(LAYOUTS.read_text())["environments"]
    result = []
    for row in report["rows"]:
        if row["mapping_status"] != "non_dataset_entity":
            continue
        env, category, name = row["env"], row["planning_category"], row["planning_name"]
        layout = layouts[env]
        label, kind = LABELS[category]
        item = {"key": row["key"], "env": env, "planning_name": name,
                "planning_category": category, "handling_type": kind,
                "handling_label": label, "source": layout["source"],
                "simulator_verified": False}
        if category == "Rooms":
            item.update({"layout_target": name, "provisional_rect_xyxy_m": layout["zones"][name],
                         "next_action": "将区域名映射到真实场景的房间语义；核对边界和连通性。"})
        elif category == "Floor":
            zone = floor_zone(name, layout["zones"])
            if zone is None:
                raise ValueError(f"Floor has no matching zone: {row['key']}")
            item.update({"layout_target": zone, "provisional_rect_xyxy_m": layout["zones"][zone],
                         "next_action": "为对应房间建立地面几何、碰撞面和材质；随后验证物体可放置。"})
        elif category == "Region":
            item.update({"layout_target": name, "provisional_rect_xyxy_m": layout["subregions"][name],
                         "next_action": "将子区域叠加到花园；核对地面形状、材质和其中的固定物体。"})
            if name == "lawn_ogzsvf_0":
                item.update({"original_scene_asset_hint": "lawn/ogzsvf",
                             "original_bounding_box_m": [46.0103, 23.1882, 0.0],
                             "evidence": "OmniGibson/Benchmark/tasks/house_double_floor_lower_best_Task1.json 同名对象"})
                item["next_action"] = "原场景有 lawn/ogzsvf，但原包围盒约 46 x 23 m，远大于暂定 4 x 4 m 草坪；需重新确定尺寸和用法。"
        elif category == "Agents":
            hint = "Crazyflie/cf2x_with_basket.usda (代码路径线索，文件与装载未验证)" if name.startswith("quadrotor") else (
                "Aliengo 机器人配置待核对" if name.startswith("aliengo") else "机械臂配置待核对；新增实例不能复用另一机械臂的名称")
            item.update({"layout_target": name, "provisional_xy_m": layout["agent_staging"][name],
                         "robot_asset_hint": hint,
                         "next_action": "确定机器人资产、独立实例名、三维初始姿态与控制配置；验证碰撞和可达性。"})
        else:
            item.update({"layout_target": "quadrotor_0", "attachment_asset_hint": "Crazyflie/cf2x_with_basket.usda (代码路径线索)",
                         "next_action": "先核对无人机 USD 是否已含篮子及其 prim；若已包含，不再额外生成自由篮子；验证连接与容纳能力。"})
        result.append(item)
    assert len(result) == 52, len(result)
    return result


def write_markdown(items):
    counts = Counter(item["handling_type"] for item in items)
    lines = [
        "# 需单独处理的 52 项：处理清单 v1", "",
        "这份清单将规划节点对应到二维布局或机器人配置工作。坐标和范围来自场景设计初稿，**不是已验证的三维姿态**。", "",
        "| 类型 | 数量 | 现在能确定的内容 | 后续验证 |", "| --- | ---: | --- | --- |",
        f"| 房间/语义区域 | {counts['room_region']} | 区域名与二维矩形 | 真实房间边界、门洞连通 |",
        f"| 地面 | {counts['floor_geometry']} | 所属房间与二维范围 | 地板几何、碰撞、材质 |",
        f"| 花园子区域 | {counts['subregion']} | 车库/草坪的二维范围；草坪有旧模型线索 | 地面形状和模型尺寸 |",
        f"| 机器人 | {counts['robot_instance']} | 独立名称与暂定 (x,y) | 资产、z/朝向、控制、可达性 |",
        f"| 无人机篮子 | {counts['robot_attachment']} | 父机器人是 `quadrotor_0` | USD 内篮子 prim、连接、容量 |",
        "", "## 处理顺序", "",
        "1. 先确认房间和地面的语义对应。房间节点不用普通物品模型；地面需要真实碰撞面。",
        "2. 再确认机器人资产及每台机器人的独立实例名和初始姿态。现有 (x,y) 只是工作位中心。",
        "3. 核对无人机资产是否已包含篮子。代码指向 `Crazyflie/cf2x_with_basket.usda`，但本机尚未证实该文件可加载；不要无条件再生成一个篮子。",
        "4. 特别核对 `lawn_ogzsvf_0`：旧场景确有 `lawn/ogzsvf`，但原包围盒约 46 x 23 m，不能直接塞进暂定 4 x 4 m 草坪区域。",
        "5. 在三维环境中按地面 → 单机器人 → 篮子 → 完整场景逐步验证尺寸、碰撞、容纳和可达性。",
        "", "## 逐项对应", "",
        "| 环境 | 规划节点 | 类型 | 暂定对应 | 当前可记录的范围/位置 | 后续动作 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in items:
        loc = item.get("provisional_rect_xyxy_m", item.get("provisional_xy_m", "挂在无人机上"))
        loc_text = ", ".join(str(v) for v in loc) if isinstance(loc, list) else loc
        lines.append(f"| {item['env']} | `{item['planning_name']}` | {item['handling_label']} | `{item['layout_target']}` | {loc_text} | {item['next_action']} |")
    lines += ["", "此清单不修改原始任务 JSON，也不把上述项目计入已确认普通物品模型。", ""]
    OUTPUT_MD.write_text("\n".join(lines))


def main():
    items = build()
    OUTPUT_JSON.write_text(json.dumps({"schema_version": 1, "status": "provisional_not_simulator_verified", "items": items}, ensure_ascii=False, indent=2) + "\n")
    write_markdown(items)
    print(f"{len(items)} entries -> {OUTPUT_JSON.relative_to(ROOT)}, {OUTPUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
