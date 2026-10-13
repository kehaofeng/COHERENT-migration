"""Build source-labelled diagrams for reading env0/task1 without running Isaac Sim."""

from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output/learning/env0_task1"
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
BG = "#F7F9FC"
INK = "#183047"
MUTED = "#52667A"
BLUE = "#DDECF9"
GREEN = "#E1F3E8"
YELLOW = "#FFF2CE"
LINE = "#9DB0C2"


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT, size)


def canvas(title, subtitle):
    im = Image.new("RGB", (1600, 920), BG)
    d = ImageDraw.Draw(im)
    d.text((74, 48), title, font=font(45, True), fill=INK)
    d.text((76, 114), subtitle, font=font(23), fill=MUTED)
    return im, d


def card(d, box, fill, outline=LINE, radius=25, width=2):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def arrow(d, start, end, color="#467BA9", width=7):
    d.line([start, end], fill=color, width=width)
    x1, y1 = start
    x2, y2 = end
    if abs(x2 - x1) >= abs(y2 - y1):
        sign = 1 if x2 > x1 else -1
        tip = [(x2, y2), (x2 - sign * 22, y2 - 12), (x2 - sign * 22, y2 + 12)]
    else:
        sign = 1 if y2 > y1 else -1
        tip = [(x2, y2), (x2 - 12, y2 - sign * 22), (x2 + 12, y2 - sign * 22)]
    d.polygon(tip, fill=color)


def task_diagram(task):
    nodes = {n["id"]: n for n in task["init_graph"]["nodes"]}
    edges = task["init_graph"]["edges"]
    needed = {(22, 3, "ON"), (22, 2, "INSIDE"), (13, 5, "ON"), (55, 13, "ON")}
    actual = {(e["from_id"], e["to_id"], e["relation_type"]) for e in edges}
    assert needed <= actual
    assert nodes[26]["prefab_name"] == "bread_1"
    assert not any(e["from_id"] == 26 and e["relation_type"] in {"ON", "INSIDE"} for e in edges)

    im, d = canvas("读懂 env0 / task1", "这是任务关系图：只表达数据写明的初始关系与目标，不代表真实房间形状、尺寸或坐标。")
    card(d, (70, 205, 680, 665), BLUE)
    card(d, (920, 205, 1530, 665), GREEN)
    d.text((104, 231), "儿童房  childroom_0", font=font(31, True), fill=INK)
    d.text((954, 231), "客厅  livingroom_0", font=font(31, True), fill=INK)

    # A schematic quadrotor and its carried basket.
    d.ellipse((320, 365, 435, 445), fill="#5F9CCD", outline="#356A96", width=3)
    for cx, cy in ((289, 344), (466, 344), (289, 467), (466, 467)):
        d.line((377, 407, cx, cy), fill="#356A96", width=8)
        d.ellipse((cx - 24, cy - 24, cx + 24, cy + 24), fill="#B8DBF4", outline="#356A96", width=3)
    d.rounded_rectangle((332, 468, 423, 510), radius=9, fill="#D1A97E", outline="#8E6C4F", width=3)
    d.text((115, 286), "无人机  quadrotor_0（ID 22）", font=font(27, True), fill=INK)
    d.text((120, 555), "初始：在儿童房地面上", font=font(27), fill=INK)
    d.text((120, 602), "篮筐  quadrotor_0_basket（ID 25）", font=font(23), fill=MUTED)

    # The table and sunglasses are only symbols, not model previews.
    d.rounded_rectangle((1112, 380, 1402, 408), radius=9, fill="#B5835B", outline="#855638", width=3)
    d.rectangle((1147, 408, 1170, 523), fill="#996846")
    d.rectangle((1346, 408, 1369, 523), fill="#996846")
    d.ellipse((1204, 347, 1251, 377), outline="#293D54", width=6)
    d.ellipse((1262, 347, 1309, 377), outline="#293D54", width=6)
    d.line((1251, 357, 1262, 357), fill="#293D54", width=6)
    d.text((955, 304), "太阳镜  sunglasses_0（ID 55）", font=font(25), fill=INK)
    d.text((961, 555), "餐桌  diningtable_0（ID 13）", font=font(27, True), fill=INK)
    d.text((961, 602), "初始：太阳镜在餐桌上", font=font(26), fill=INK)

    arrow(d, (696, 416), (902, 416))
    card(d, (694, 338, 906, 392), YELLOW, radius=13)
    d.text((705, 346), "目标：落在餐桌上", font=font(23, True), fill=INK)

    card(d, (70, 714, 1530, 838), "#F0F2F5")
    d.text((102, 737), "面包 bread_1（ID 26）", font=font(27, True), fill=INK)
    d.text((490, 741), "任务列出了它，但没有给出 ON / INSIDE 初始放置关系。", font=font(25), fill=MUTED)
    d.text((76, 866), "来源：env/env0.json 中 task_id=1 的 init_graph 与 task_goal。图形均为示意符号。", font=font(20), fill=MUTED)
    im.save(OUT / "01-task-relations.png")


def code_diagram():
    im, d = canvas("代码是怎样读任务的", "两条静态分析支路都直接读取 env/*.json；模型候选表不是从单任务报告继续加工出来的。")
    card(d, (67, 320, 410, 560), BLUE)
    d.text((99, 356), "env/env0.json", font=font(32, True), fill=INK)
    d.text((99, 410), "任务原始数据", font=font(27), fill=INK)
    d.text((99, 465), "task_id = 1", font=font(26), fill=MUTED)

    card(d, (632, 214, 1068, 430), "#E8EEFA")
    d.text((660, 247), "extract_task_entities.py", font=font(28, True), fill=INK)
    d.text((660, 300), "选一条任务；遍历 nodes 和 edges", font=font(24), fill=INK)
    d.text((660, 352), "标出目标对象与初始关系", font=font(24), fill=INK)

    card(d, (632, 520, 1068, 736), "#E4F3EC")
    d.text((660, 553), "map_all_models.py", font=font(28, True), fill=INK)
    d.text((660, 606), "扫描五个 env、模型库及旧配置", font=font(24), fill=INK)
    d.text((660, 658), "列候选；记录有来源的选择", font=font(24), fill=INK)

    card(d, (1248, 214, 1533, 430), "#F3F4F7")
    d.text((1273, 248), "单任务报告", font=font(28, True), fill=INK)
    d.text((1273, 303), "task_entities.json", font=font(22), fill=INK)
    d.text((1273, 353), "task_entities.md", font=font(22), fill=INK)

    card(d, (1248, 520, 1533, 736), "#F3F4F7")
    d.text((1273, 554), "全量候选表", font=font(28, True), fill=INK)
    d.text((1273, 608), "model_mapping.json", font=font(22), fill=INK)
    d.text((1273, 657), "model_mapping.csv", font=font(22), fill=INK)

    arrow(d, (426, 392), (616, 321))
    arrow(d, (426, 496), (616, 626), color="#519474")
    arrow(d, (1084, 321), (1232, 321))
    arrow(d, (1084, 627), (1232, 627), color="#519474")
    d.text((68, 791), "这两条支路只读文件，不启动三维仿真。实际模型尺寸、碰撞和抓取仍待运行验证。", font=font(26, True), fill=INK)
    d.text((70, 858), "来源：tools/scene_prep/extract_task_entities.py 与 tools/scene_prep/map_all_models.py。", font=font(20), fill=MUTED)
    im.save(OUT / "02-code-flow.png")


def model_diagram():
    data = json.loads((ROOT / "scene_prep/reports/all_env_models/model_mapping.json").read_text(encoding="utf-8"))
    row = next(r for r in data["rows"] if r["key"] == "env0|Accessories|sunglasses_0")
    assert row["mapping_status"] == "needs_model_selection" and len(row["candidate_models"]) == 4
    im, d = canvas("一个物体名，可以对应多个三维模型", "以 env0 的 sunglasses_0 为例：目录扫描找到了候选，但当前没有人工确认的选型。")
    card(d, (70, 225, 520, 692), BLUE)
    d.text((104, 259), "规划中的物体", font=font(30, True), fill=INK)
    d.text((104, 335), "sunglasses_0", font=font(36, True), fill=INK)
    d.text((104, 407), "类别：Accessories", font=font(26), fill=INK)
    d.text((104, 464), "名称：sunglasses", font=font(26), fill=INK)
    d.text((104, 560), "这是任务里的一个实例", font=font(24), fill=MUTED)
    arrow(d, (538, 458), (648, 458))

    d.text((686, 220), "模型库中的 4 个候选", font=font(30, True), fill=INK)
    positions = [(680, 305), (1115, 305), (680, 502), (1115, 502)]
    for (x, y), ref in zip(positions, row["candidate_models"]):
        card(d, (x, y, x + 360, y + 152), "#E4F0F6")
        d.text((x + 26, y + 27), "?", font=font(55, True), fill="#4F7897")
        d.text((x + 79, y + 59), ref, font=font(24, True), fill=INK)

    card(d, (70, 736, 1530, 843), YELLOW)
    d.text((101, 760), "当前状态：needs_model_selection", font=font(28, True), fill=INK)
    d.text((790, 762), "下一步：看外形、尺寸、碰撞与任务适用性。", font=font(24), fill=INK)
    d.text((73, 865), "“?” 表示尚未预览，并不是模型真实外形。来源：scene_prep/reports/all_env_models/model_mapping.json。", font=font(20), fill=MUTED)
    im.save(OUT / "03-instance-vs-model.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tasks = json.loads((ROOT / "env/env0.json").read_text(encoding="utf-8"))
    matching = [task for task in tasks if task["task_id"] == 1]
    assert len(matching) == 1
    task_diagram(matching[0])
    code_diagram()
    model_diagram()
    print("Created:", *(str(path) for path in sorted(OUT.glob("*.png"))), sep="\n")


if __name__ == "__main__":
    main()
