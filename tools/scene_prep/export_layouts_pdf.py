"""Export the two original and five proposed floor plans to a seven-page PDF."""

import argparse
import io
from collections import defaultdict
from pathlib import Path

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from build_layout_visualization import DATA, get_scenes


FONT_CJK = "DroidCJK"
FONT_LATIN = "DejaVuSans"
FONT_FALLBACK = "UMing"
GLYPHS = {}
INK = colors.HexColor("#183047")
MUTED = colors.HexColor("#526478")
RULE = colors.HexColor("#D8E1E8")
PAGE_BG = colors.HexColor("#F4F7FA")
ACCENT_ORIGINAL = colors.HexColor("#345B98")
ACCENT_PROPOSED = colors.HexColor("#0A806F")
ROOMS = ["#DBEAF4", "#E3F1E7", "#FAEBD9", "#EEE8F6", "#DCEFEB", "#F9E6EB"]
PAGE_W, PAGE_H = A4
PLOT = (42, 345, PAGE_W - 84, 390)
LEGEND_LEFT = 46
LEGEND_RIGHT = PAGE_W / 2 + 8
LEGEND_COL_W = PAGE_W / 2 - 65


def font_for(char):
    code = ord(char)
    if code < 128 and code in GLYPHS[FONT_LATIN]:
        return FONT_LATIN
    if code in GLYPHS[FONT_CJK]:
        return FONT_CJK
    if code in GLYPHS[FONT_LATIN]:
        return FONT_LATIN
    return FONT_FALLBACK


def text_width(value, size):
    return sum(pdfmetrics.stringWidth(char, font_for(char), size) for char in str(value))


def draw_text(c, value, x, y, size, align="left"):
    value = str(value)
    if align == "center":
        x -= text_width(value, size) / 2
    elif align == "right":
        x -= text_width(value, size)
    t = c.beginText(x, y)
    current_font = None
    chunk = ""
    for char in value:
        font = font_for(char)
        if font != current_font and chunk:
            t.setFont(current_font, size)
            t.textOut(chunk)
            chunk = ""
        current_font = font
        chunk += char
    if chunk:
        t.setFont(current_font, size)
        t.textOut(chunk)
    c.drawText(t)


def text_fit(c, value, x, y, max_width, size=9.5, min_size=7):
    while size > min_size and text_width(value, size) > max_width:
        size -= 0.25
    draw_text(c, value, x, y, size)


def wrap_text(value, max_width, font_size):
    lines = []
    line = ""
    for char in value:
        if text_width(line + char, font_size) > max_width and line:
            lines.append(line)
            line = char
        else:
            line += char
    if line:
        lines.append(line)
    return lines


def draw_header(c, scene, page_index):
    accent = ACCENT_ORIGINAL if scene["kind"] == "original" else ACCENT_PROPOSED
    c.setFillColor(PAGE_BG)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(accent)
    c.rect(0, PAGE_H - 7, PAGE_W, 7, fill=1, stroke=0)
    c.setFillColor(accent)
    draw_text(c, "数据集场景" if scene["kind"] == "original" else "规划环境 · 设计初稿", 42, PAGE_H - 31, 9.5)
    c.setFillColor(INK)
    draw_text(c, scene["title"], 42, PAGE_H - 57, 18)
    c.setFillColor(MUTED)
    for i, line in enumerate(wrap_text(scene["note"], PAGE_W - 84, 9.2)[:2]):
        draw_text(c, line, 42, PAGE_H - 75 - i * 12, 9.2)
    c.setFillColor(colors.white)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.7)
    c.roundRect(36, 337, PAGE_W - 72, 405, 9, fill=1, stroke=1)
    c.roundRect(36, 66, PAGE_W - 72, 262, 9, fill=1, stroke=1)
    c.setFillColor(INK)
    draw_text(c, "图例", 49, 307, 11)
    c.setStrokeColor(RULE)
    c.line(49, 298, PAGE_W - 49, 298)
    c.setFillColor(MUTED)
    draw_text(c, "原有场景按数据集绘制；新场景是二维方案，尚未通过仿真验证。", 42, 43, 8.5)
    draw_text(c, f"{page_index} / 7", PAGE_W - 42, 43, 8.5, align="right")


def draw_marker(c, x, y, label, kind="object", accent=ACCENT_PROPOSED):
    c.setLineWidth(0.8)
    c.setStrokeColor(colors.white)
    if kind == "room":
        c.setFillColor(colors.white)
        c.setStrokeColor(accent)
        c.roundRect(x - 8, y - 8, 16, 16, 3, fill=1, stroke=1)
        c.setFillColor(accent)
    elif kind == "door":
        c.setFillColor(colors.HexColor("#BD6E24"))
        c.roundRect(x - 9, y - 8, 18, 16, 3, fill=1, stroke=0)
        c.setFillColor(colors.white)
    elif kind == "agent":
        c.setFillColor(colors.HexColor("#49607A"))
        path = c.beginPath()
        path.moveTo(x, y + 10)
        path.lineTo(x - 10, y - 8)
        path.lineTo(x + 10, y - 8)
        path.close()
        c.drawPath(path, fill=1, stroke=0)
        c.setFillColor(colors.white)
    else:
        c.setFillColor(accent)
        c.circle(x, y, 9, fill=1, stroke=0)
        c.setFillColor(colors.white)
    draw_text(c, str(label), x, y - 2.8, 7.2, align="center")


def draw_legend(c, left_sections, right_sections, accent):
    for column_x, sections in [(LEGEND_LEFT, left_sections), (LEGEND_RIGHT, right_sections)]:
        y = 291
        for title, entries in sections:
            c.setFillColor(accent)
            draw_text(c, f"{title}  {len(entries)}", column_x, y, 9.5)
            y -= 17
            for number, label, name in entries:
                c.setFillColor(INK)
                text_fit(c, f"{number}  {label}", column_x, y, LEGEND_COL_W, 9.2, 8)
                if name:
                    c.setFillColor(MUTED)
                    text_fit(c, name, column_x + 17, y - 9, LEGEND_COL_W - 17, 7.2, 6.3)
                y -= 17
            y -= 2
        if y < 68:
            raise ValueError(f"Legend overflows page: y={y:.1f}")


def original_map_image(scene, model):
    source = Image.open(DATA / "scenes" / model / "layout/floor_insseg_0.png")
    factor = source.width / scene["size"][0]
    x0, y0, x1, y1 = scene["bounds"]
    crop = source.crop(tuple(round(v * factor) for v in (x0, y0, x1, y1))).convert("P")
    palette = [248, 250, 252] * 256
    for i, room in enumerate(scene["rooms"]):
        rgba = colors.HexColor(ROOMS[i % len(ROOMS)])
        rgb = [round(rgba.red * 255), round(rgba.green * 255), round(rgba.blue * 255)]
        palette[room["id"] * 3:room["id"] * 3 + 3] = rgb
    crop.putpalette(palette)
    rgb = crop.convert("RGB")
    rgb.thumbnail((1800, 1800), Image.LANCZOS)
    stream = io.BytesIO()
    rgb.save(stream, "PNG")
    stream.seek(0)
    return ImageReader(stream)


def original_page(c, scene, model):
    x0, y0, x1, y1 = scene["bounds"]
    panel_x, panel_y, panel_w, panel_h = PLOT
    scale = min((panel_w - 22) / (x1 - x0), (panel_h - 22) / (y1 - y0))
    width, height = (x1 - x0) * scale, (y1 - y0) * scale
    ox = panel_x + (panel_w - width) / 2
    oy = panel_y + (panel_h - height) / 2
    c.drawImage(original_map_image(scene, model), ox, oy, width, height)

    def xy(point):
        return ox + (point[0] - x0) * scale, oy + height - (point[1] - y0) * scale

    for room in scene["rooms"]:
        draw_marker(c, *xy(room["xy"]), room["id"], "room", ACCENT_ORIGINAL)
    for i, obj in enumerate(scene["objects"], 1):
        draw_marker(c, *xy(obj["xy"]), i, "object", ACCENT_ORIGINAL)
    draw_legend(c,
        [("房间", [(r["id"], r["label"], r["name"]) for r in scene["rooms"]])],
        [("主要家具", [(i, o["label"], o["name"]) for i, o in enumerate(scene["objects"], 1)])],
        ACCENT_ORIGINAL)


def proposed_page(c, scene):
    rects = [z["rect"] for z in scene["zones"]]
    minx = min(r[0] for r in rects)
    miny = min(r[1] for r in rects)
    maxx = max(r[2] for r in rects)
    maxy = max(r[3] for r in rects)
    panel_x, panel_y, panel_w, panel_h = PLOT
    scale = min((panel_w - 24) / (maxx - minx), (panel_h - 24) / (maxy - miny))
    width, height = (maxx - minx) * scale, (maxy - miny) * scale
    ox = panel_x + (panel_w - width) / 2
    oy = panel_y + (panel_h - height) / 2

    def xy(point):
        return ox + (point[0] - minx) * scale, oy + (point[1] - miny) * scale

    for i, zone in enumerate(scene["zones"]):
        x0, y0, x1, y1 = zone["rect"]
        c.setFillColor(colors.HexColor(ROOMS[i % len(ROOMS)]))
        c.setStrokeColor(RULE)
        c.rect(*xy((x0, y0)), (x1 - x0) * scale, (y1 - y0) * scale, fill=1, stroke=1)
        c.setFillColor(INK)
        text_fit(c, zone["label"], *xy((x0 + 0.2, y1 - 0.35)), (x1 - x0) * scale - 12, 10.5, 8.5)
    for i, zone in enumerate(scene["subregions"]):
        x0, y0, x1, y1 = zone["rect"]
        c.setFillColor(colors.HexColor(ROOMS[(i + 4) % len(ROOMS)]))
        c.setStrokeColor(MUTED)
        c.setDash(3, 3)
        c.rect(*xy((x0, y0)), (x1 - x0) * scale, (y1 - y0) * scale, fill=1, stroke=1)
        c.setDash()
        c.setFillColor(INK)
        draw_text(c, zone["label"], *xy((x0 + 0.15, y1 - 0.35)), 9)

    grouped = defaultdict(list)
    for obj in scene["objects"]:
        grouped[tuple(round(v, 1) for v in obj["xy"])].append(obj)
    objects = list(grouped.items())
    for i, (point, _) in enumerate(objects, 1):
        draw_marker(c, *xy(point), i)
    for i, door in enumerate(scene["doors"], 1):
        draw_marker(c, *xy(door["xy"]), f"D{i}", "door")
    for i, agent in enumerate(scene["agents"], 1):
        px, py = xy(agent["xy"])
        if any(abs(px - xy(point)[0]) < 13 and abs(py - xy(point)[1]) < 13 for point, _ in objects):
            px += 13
            py -= 13
        draw_marker(c, px, py, f"R{i}", "agent")

    fixed = [
        (i, "、".join(x["label"] for x in values), " / ".join(x["name"] for x in values))
        for i, (_, values) in enumerate(objects, 1)
    ]
    doors = [(f"D{i}", "门", x["name"]) for i, x in enumerate(scene["doors"], 1)]
    agents = [(f"R{i}", "机器人", x["name"]) for i, x in enumerate(scene["agents"], 1)]
    split = (len(fixed) + 1) // 2 if doors else min(len(fixed), (len(fixed) + len(agents) + 1) // 2)
    left = [("固定物体", fixed[:split])]
    right = [("固定物体", fixed[split:])]
    if doors:
        left.append(("门", doors))
    right.append(("机器人初始区", agents))
    draw_legend(c, left, right, ACCENT_PROPOSED)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    pdfmetrics.registerFont(TTFont(FONT_CJK, "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"))
    pdfmetrics.registerFont(TTFont(FONT_LATIN, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont(FONT_FALLBACK, "/usr/share/fonts/truetype/arphic/uming.ttc", subfontIndex=0))
    for name in (FONT_CJK, FONT_LATIN, FONT_FALLBACK):
        GLYPHS[name] = pdfmetrics.getFont(name).face.charToGlyph
    args.output.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(args.output), pagesize=(PAGE_W, PAGE_H))
    c.setTitle("原有两个场景与五个规划环境 - 俯视布局")
    scenes = get_scenes()
    for index, scene in enumerate(scenes, 1):
        draw_header(c, scene, index)
        if scene["kind"] == "original":
            model = "Merom_1_int" if index == 1 else "house_double_floor_lower"
            original_page(c, scene, model)
        else:
            proposed_page(c, scene)
        c.showPage()
    c.save()
    print(args.output)


if __name__ == "__main__":
    main()
