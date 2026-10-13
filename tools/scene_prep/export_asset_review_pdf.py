"""Export a shareable five-environment layout and complete asset review PDF."""

import argparse
from collections import Counter, defaultdict
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from build_asset_visualization import build_data


ROOT = Path(__file__).resolve().parents[2]
PAGE_W, PAGE_H = landscape(A4)
LEFT, RIGHT = 36, PAGE_W - 36
FONT_LATIN = "ArialReview"
FONT_LATIN_BOLD = "ArialReviewBold"
FONT_CJK = "UMingCNReview"
GLYPHS = {}

BG = colors.HexColor("#F7F9FB")
PAPER = colors.white
INK = colors.HexColor("#17334B")
MUTED = colors.HexColor("#53697B")
RULE = colors.HexColor("#D9E3E9")
TEAL = colors.HexColor("#0A766E")
BLUE = colors.HexColor("#345E95")
AMBER = colors.HexColor("#AD6A1F")
PURPLE = colors.HexColor("#76609A")
ROOMS = ["#DDEBF6", "#E4F1EA", "#FAEBDD", "#EEE8F5", "#DDEDEC", "#F7E5EA"]
STATUS = {
    "source_backed": ("原配置有依据", TEAL),
    "needs_model_selection": ("待选模型", BLUE),
    "no_model_candidate": ("无当前候选", AMBER),
    "non_dataset_entity": ("需单独处理", PURPLE),
}
ZONE_NAMES = {
    "livingroom_0": "客厅", "bedroom_0": "卧室", "childroom_0": "儿童房",
    "kitchen_0": "厨房", "living_room_0": "客厅", "living_room_1": "上生活区",
    "utility_room_0": "杂物间", "grocery_store_0": "超市", "restaurant_0": "餐厅",
    "corridor_0": "走廊", "garden_0": "花园",
}


def register_fonts():
    pdfmetrics.registerFont(TTFont(FONT_LATIN, "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf"))
    pdfmetrics.registerFont(TTFont(FONT_LATIN_BOLD, "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf"))
    # SimSun is absent on this Linux host. AR PL UMing CN is a Song/Ming style serif.
    pdfmetrics.registerFont(TTFont(FONT_CJK, "/usr/share/fonts/truetype/arphic/uming.ttc", subfontIndex=0))
    for font in (FONT_LATIN, FONT_LATIN_BOLD, FONT_CJK):
        GLYPHS[font] = pdfmetrics.getFont(font).face.charToGlyph


def font_for(char, bold=False):
    latin = FONT_LATIN_BOLD if bold else FONT_LATIN
    return latin if ord(char) < 128 and ord(char) in GLYPHS[latin] else FONT_CJK


def width(value, size, bold=False):
    return sum(pdfmetrics.stringWidth(ch, font_for(ch, bold), size) for ch in str(value))


def text(c, value, x, y, size=9, color=INK, bold=False, align="left"):
    value = str(value)
    if align == "right":
        x -= width(value, size, bold)
    elif align == "center":
        x -= width(value, size, bold) / 2
    c.setFillColor(color)
    t = c.beginText(x, y)
    active = None
    run = ""
    for ch in value:
        font = font_for(ch, bold)
        if font != active and run:
            t.setFont(active, size)
            t.textOut(run)
            run = ""
        active = font
        run += ch
    if run:
        t.setFont(active, size)
        t.textOut(run)
    c.drawText(t)


def lines(value, max_width, size, bold=False):
    if not value:
        return []
    out, line = [], ""
    for ch in str(value):
        if ch == "\n":
            out.append(line)
            line = ""
        elif line and width(line + ch, size, bold) > max_width:
            out.append(line)
            line = ch
        else:
            line += ch
    if line:
        out.append(line)
    return out


def fitted(c, value, x, y, max_width, size=9, min_size=7, **kwargs):
    while size > min_size and width(value, size) > max_width:
        size -= .25
    text(c, value, x, y, size, **kwargs)


def page_base(c, eyebrow, title, subtitle=None):
    c.setFillColor(BG)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(INK)
    c.rect(0, PAGE_H - 7, PAGE_W, 7, fill=1, stroke=0)
    text(c, eyebrow, LEFT, PAGE_H - 31, 9, TEAL, bold=True)
    text(c, title, LEFT, PAGE_H - 60, 20, INK, bold=True)
    if subtitle:
        text(c, subtitle, LEFT, PAGE_H - 78, 9, MUTED)
    c.setStrokeColor(RULE)
    c.line(LEFT, 39, RIGHT, 39)
    text(c, "COHERENT  /  五环境资产与布局核对", LEFT, 23, 8, MUTED)
    text(c, str(c.getPageNumber()), RIGHT, 23, 8, MUTED, align="right")


def stat(c, x, y, number, label, color=INK):
    text(c, number, x, y, 20, color, bold=True)
    text(c, label, x, y - 17, 9, MUTED)


def cover(c, envs):
    page_base(c, "PROJECT BRIEF  /  2026-10-11", "五个规划环境的资产与布局", "供场景与模型选型讨论使用  |  静态分析版本")
    all_rows = [row for env in envs for row in env["rows"]]
    total_tasks = sum(env["task_count"] for env in envs)
    counts = Counter(row["status"] for row in all_rows)
    for x, n, label, color in [
        (LEFT, len(envs), "规划环境", TEAL), (190, total_tasks, "任务", BLUE),
        (344, len(all_rows), "规划实体", INK), (506, counts["source_backed"], "有原配置依据", TEAL),
        (665, counts["needs_model_selection"], "待选模型", BLUE),
    ]:
        stat(c, x, PAGE_H - 128, n, label, color)

    y = PAGE_H - 192
    text(c, "环境概览", LEFT, y + 32, 10, TEAL, bold=True)
    for i, env in enumerate(envs):
        yy = y - i * 56
        c.setFillColor(PAPER)
        c.roundRect(LEFT, yy - 35, RIGHT - LEFT, 49, 5, fill=1, stroke=0)
        c.setFillColor(TEAL)
        c.roundRect(LEFT, yy - 35, 5, 49, 2, fill=1, stroke=0)
        text(c, env["env"], LEFT + 20, yy - 5, 12, INK, bold=True)
        text(c, env["title"], LEFT + 88, yy - 5, 11, INK)
        text(c, env["task_count"], 335, yy - 5, 11, INK)
        text(c, len(env["rows"]), 421, yy - 5, 11, INK)
        ct = Counter(row["status"] for row in env["rows"])
        label = f"依据 {ct['source_backed']}  /  待选 {ct['needs_model_selection']}  /  无候选 {ct['no_model_candidate']}  /  单独处理 {ct['non_dataset_entity']}"
        fitted(c, label, 510, yy - 5, RIGHT - 520, 9.3, 8, color=MUTED)

    text(c, "使用边界", LEFT, 92, 10, TEAL, bold=True)
    text(c, "布局坐标是二维草案；物体模型、尺寸、朝向、碰撞和机器人可达性仍需在三维仿真中核对。", LEFT, 75, 9, INK)
    text(c, "“有原配置依据”仍待加载核对；待选项仅列候选数量，完整候选型号见项目映射报告。", LEFT, 60, 9, MUTED)
    c.showPage()


def map_positions(env):
    grouped = defaultdict(list)
    for name, xy in env["fixed"].items():
        grouped[tuple(xy)].append(name)
    points = []
    positions = {}
    for i, (xy, names) in enumerate(grouped.items(), 1):
        tag = f"F{i}"
        points.append((tag, xy, "/".join(names), "fixed"))
        for name in names:
            positions[name] = tag
    for i, item in enumerate(env["duplicates"], len(points) + 1):
        tag = f"F{i}"
        name = item["prefab_name"]
        points.append((tag, item["xy"], f"{name} [节点 {item['node_id']}]", "fixed"))
        positions[f"{item['category']}|{name}"] = tag
    for i, (name, xy) in enumerate(env["doors"].items(), 1):
        tag = f"D{i}"
        points.append((tag, xy, name, "door"))
        positions[name] = tag
    for i, (name, xy) in enumerate(env["agents"].items(), 1):
        tag = f"R{i}"
        points.append((tag, xy, name, "agent"))
        positions[name] = tag
    return points, positions


def draw_map_marker(c, x, y, tag, kind):
    if kind == "agent":
        p = c.beginPath()
        p.moveTo(x, y + 10)
        p.lineTo(x - 11, y - 9)
        p.lineTo(x + 11, y - 9)
        p.close()
        c.setFillColor(INK)
        c.drawPath(p, fill=1, stroke=0)
        label_color = PAPER
    elif kind == "door":
        c.setFillColor(AMBER)
        c.roundRect(x - 10, y - 9, 20, 18, 2, fill=1, stroke=0)
        label_color = PAPER
    else:
        c.setFillColor(TEAL)
        c.circle(x, y, 10, fill=1, stroke=0)
        label_color = PAPER
    text(c, tag, x, y - 2.5, 7.1, label_color, bold=True, align="center")


def map_page(c, env):
    c.bookmarkPage(env["env"])
    c.addOutlineEntry(f"{env['env']} {env['title']}", env["env"], level=0)
    page_base(c, f"ENVIRONMENT  /  {env['env'].upper()}", f"{env['title']} - 场景布局", "二维设计草案  |  图中标记可与后续资产清单的“布局”列对照")
    c.setFillColor(PAPER)
    c.roundRect(LEFT, 73, 490, 418, 7, fill=1, stroke=0)
    rects = list(env["zones"].values())
    minx, maxx = min(r[0] for r in rects), max(r[2] for r in rects)
    miny, maxy = min(r[1] for r in rects), max(r[3] for r in rects)
    scale = min(455 / (maxx - minx), 374 / (maxy - miny))
    plot_w, plot_h = (maxx - minx) * scale, (maxy - miny) * scale
    ox = LEFT + (490 - plot_w) / 2
    oy = 92 + (380 - plot_h) / 2
    def xy(point):
        return ox + (point[0] - minx) * scale, oy + (point[1] - miny) * scale
    for i, (name, r) in enumerate(env["zones"].items()):
        c.setFillColor(colors.HexColor(ROOMS[i % len(ROOMS)]))
        c.setStrokeColor(RULE)
        c.rect(*xy((r[0], r[1])), (r[2] - r[0]) * scale, (r[3] - r[1]) * scale, fill=1, stroke=1)
        label = "下生活区" if env["env"] == "env4" and name == "living_room_0" else ZONE_NAMES.get(name, name)
        text(c, label, *xy((r[0] + .17, r[3] - .36)), 9, INK)
    for i, (name, r) in enumerate(env["subregions"].items()):
        c.setFillColor(colors.HexColor(ROOMS[(i + 4) % len(ROOMS)]))
        c.setStrokeColor(MUTED)
        c.setDash(3, 3)
        c.rect(*xy((r[0], r[1])), (r[2] - r[0]) * scale, (r[3] - r[1]) * scale, fill=1, stroke=1)
        c.setDash()
        text(c, "车库" if "garage" in name else "草坪", *xy((r[0] + .15, r[3] - .32)), 8.5, INK)
    points, _ = map_positions(env)
    occupied = {tuple(point) for _, point, _, kind in points if kind == "fixed"}
    for tag, point, _, kind in points:
        px, py = xy(point)
        if kind == "agent" and tuple(point) in occupied:
            px += 13
            py += 13
        draw_map_marker(c, px, py, tag, kind)

    sidebar_x = 550
    counts = Counter(row["status"] for row in env["rows"])
    text(c, f"{env['env']}  /  {env['task_count']} 任务  /  {len(env['rows'])} 项", sidebar_x, 481, 11, INK, bold=True)
    y = 459
    for key in ("source_backed", "needs_model_selection", "no_model_candidate", "non_dataset_entity"):
        label, color = STATUS[key]
        c.setFillColor(color)
        c.circle(sidebar_x + 4, y + 2, 3.5, fill=1, stroke=0)
        text(c, f"{label}  {counts[key]}", sidebar_x + 14, y, 9, INK)
        y -= 19
    c.setStrokeColor(RULE)
    c.line(sidebar_x, y + 4, RIGHT, y + 4)
    y -= 16
    text(c, "布局标记", sidebar_x, y, 10, TEAL, bold=True)
    y -= 16
    for tag, _, name, kind in points:
        if y < 100:
            raise ValueError(f"Map legend overflow for {env['env']}")
        text(c, tag, sidebar_x, y, 8.1, INK, bold=True)
        fitted(c, name, sidebar_x + 31, y, RIGHT - sidebar_x - 34, 8.1, 6.8, color=MUTED)
        y -= 11.5
    text(c, "○ F 固定物体   □ D 门   △ R 机器人初始区", LEFT, 57, 8.5, MUTED)
    c.showPage()


def model_info(row):
    status = row["status"]
    if status == "source_backed":
        note = "名称编号与原配置型号不同，需重点核对" if row["name"] == "kebab_cewhbv_0" else "旧任务同名配置线索；尚未验证加载"
        return f"原配置线索: {row['selected']}", note
    if status == "needs_model_selection":
        return f"待选模型 ({len(row['candidates'])} 个候选)", ""
    if status == "no_model_candidate":
        return "无当前候选", "需要继续寻找或制作资产"
    return "需单独处理", ""


def position_for(row, env, positions):
    if f"{row['category']}|{row['name']}" in positions:
        return positions[f"{row['category']}|{row['name']}"]
    if row["name"] in positions:
        return positions[row["name"]]
    if row["name"] in env["zones"] or row["name"] in env["subregions"]:
        return "区域"
    if row["category"] == "Floor":
        return "地面"
    return "按任务"


def table_header(c, env, part):
    page_base(c, f"ASSET REGISTER  /  {env['env'].upper()}", f"{env['title']} - 资产清单", f"第 {part} 页  |  共 {len(env['rows'])} 项  |  列出候选数与已有选型；未验证三维加载")
    c.setFillColor(PAPER)
    c.rect(LEFT, 68, RIGHT - LEFT, 422, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#E6EFF2"))
    c.rect(LEFT, 463, RIGHT - LEFT, 27, fill=1, stroke=0)
    for label, x in [("#", 43), ("物体标识 / 类名", 73), ("规划类别", 272), ("布局", 368), ("模型对应与依据 / 候选", 422), ("任务", 784)]:
        text(c, label, x, 472, 8.7, INK, bold=True)


def row_layout(row):
    name_lines = lines(row["name"], 187, 8.4)
    class_lines = lines(row["class"], 187, 7.5)
    category_lines = lines(row["category"], 87, 8)
    primary, detail = model_info(row)
    primary_lines = lines(primary, 342, 8.4)
    detail_lines = lines(detail, 342, 7.4)
    model_height = 10 + len(primary_lines) * 10 + (len(detail_lines) * 8.6 if detail_lines else 0)
    left_height = 9 + len(name_lines) * 9.5 + len(class_lines) * 8
    height = max(27, model_height, left_height, 9 + len(category_lines) * 10) + 3
    return height, name_lines, class_lines, category_lines, primary_lines, detail_lines


def draw_row(c, row, seq, y, env, positions, layout):
    height, names, classes, categories, primary, detail = layout
    c.setStrokeColor(RULE)
    c.setLineWidth(.45)
    c.line(LEFT, y - height, RIGHT, y - height)
    text(c, seq, 43, y - 13, 8, MUTED)
    yy = y - 13
    for line in names:
        text(c, line, 73, yy, 8.4, INK, bold=True)
        yy -= 9.5
    for line in classes:
        text(c, line, 73, yy - 1, 7.5, MUTED)
        yy -= 8
    yy = y - 13
    for line in categories:
        text(c, line, 272, yy, 8, INK)
        yy -= 10
    text(c, position_for(row, env, positions), 368, y - 13, 8, MUTED)
    status_color = STATUS[row["status"]][1]
    yy = y - 13
    for line in primary:
        text(c, line, 422, yy, 8.4, status_color, bold=True)
        yy -= 10
    for line in detail:
        text(c, line, 422, yy, 7.4, MUTED)
        yy -= 8.6
    text(c, row["tasks"], RIGHT - 12, y - 13, 8, INK, align="right")
    return y - height


def table_pages(c, env):
    _, positions = map_positions(env)
    part = 0
    y = 455
    for seq, row in enumerate(env["rows"], 1):
        layout = row_layout(row)
        if part == 0 or y - layout[0] < 75:
            if part:
                c.showPage()
            part += 1
            table_header(c, env, part)
            y = 458
        y = draw_row(c, row, seq, y, env, positions, layout)
    c.showPage()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    register_fonts()
    envs = build_data()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(args.output), pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle("五个规划环境 - 资产与布局核对")
    c.setAuthor("COHERENT scene preparation")
    cover(c, envs)
    for env in envs:
        map_page(c, env)
        table_pages(c, env)
    c.save()
    print(f"{args.output} ({c.getPageNumber() - 1} pages)")


if __name__ == "__main__":
    main()
