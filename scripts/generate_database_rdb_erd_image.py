from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "images" / "database-rdb-concept-erd.png"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "malgunbd.ttf" if bold else "malgun.ttf"
    return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size=size)


def centered(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], text: str, face: ImageFont.FreeTypeFont, fill: str) -> None:
    x1, y1, x2, y2 = xy
    bbox = draw.textbbox((0, 0), text, font=face)
    tx = x1 + ((x2 - x1) - (bbox[2] - bbox[0])) // 2
    ty = y1 + ((y2 - y1) - (bbox[3] - bbox[1])) // 2 - 2
    draw.text((tx, ty), text, font=face, fill=fill)


def table(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    title: str,
    rows: list[tuple[str, str, str]],
    fill: str,
    stroke: str,
    col_widths: tuple[int, int, int] = (96, 220, 52),
    row_h: int = 42,
) -> tuple[int, int, int, int]:
    x, y = xy
    width = sum(col_widths)
    height = row_h * (len(rows) + 1)
    x2, y2 = x + width, y + height
    draw.rectangle((x, y, x2, y2), fill=fill, outline=stroke, width=3)
    draw.rectangle((x, y, x2, y + row_h), fill="#fffaf5", outline=stroke, width=3)
    centered(draw, (x, y, x2, y + row_h), title, font(17, True), "#1f2933")

    cx = x
    for w in col_widths[:-1]:
        cx += w
        draw.line((cx, y + row_h, cx, y2), fill=stroke, width=2)

    for idx, (typ, name, key) in enumerate(rows):
        ry = y + row_h * (idx + 1)
        draw.line((x, ry, x2, ry), fill=stroke, width=2)
        draw.text((x + 14, ry + 11), typ, font=font(14), fill="#111827")
        draw.text((x + col_widths[0] + 14, ry + 11), name, font=font(14), fill="#111827")
        if key:
            centered(draw, (x2 - col_widths[2], ry, x2, ry + row_h), key, font(13, True), "#111827")
    return (x, y, x2, y2)


def line_with_label(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[int, int]],
    label: str,
    label_at: tuple[int, int],
    start_card: str,
    end_card: str,
) -> None:
    color = "#111111"
    draw.line(points, fill=color, width=3, joint="curve")
    lx, ly = label_at
    bbox = draw.textbbox((0, 0), label, font=font(13))
    label_x = lx - (bbox[2] - bbox[0]) // 2
    draw.rectangle(
        (label_x - 5, ly - 3, label_x + (bbox[2] - bbox[0]) + 5, ly + (bbox[3] - bbox[1]) + 7),
        fill="#ffffff",
    )
    draw.text((label_x, ly), label, font=font(13), fill="#111111")
    sx, sy = points[0]
    ex, ey = points[-1]
    draw.text((sx - 13, sy - 16), start_card, font=font(22, True), fill=color)
    draw.text((ex - 13, ey - 16), end_card, font=font(22, True), fill=color)


def main() -> None:
    image = Image.new("RGB", (1480, 1400), "#ffffff")
    draw = ImageDraw.Draw(image)
    draw.text((64, 42), "Lovv RDB Concept ERD", font=font(34, True), fill="#1f2933")
    draw.text((64, 88), "Users, social accounts, saved itineraries, itinerary items, and plan reactions.", font=font(18), fill="#5f6368")

    users = table(
        draw,
        (560, 130),
        "USERS",
        [
            ("uuid", "id", "PK"),
            ("string", "email", ""),
            ("string", "display_name", ""),
            ("string", "avatar_url", ""),
            ("datetime", "created_at", ""),
        ],
        "#fbf0fb",
        "#e754ff",
    )
    social = table(
        draw,
        (70, 520),
        "SOCIAL_ACCOUNTS",
        [
            ("uuid", "id", "PK"),
            ("uuid", "user_id", "FK"),
            ("string", "provider", ""),
            ("string", "provider_user_id", ""),
            ("datetime", "created_at", ""),
        ],
        "#eafff8",
        "#14d7c3",
    )
    itineraries = table(
        draw,
        (530, 450),
        "ITINERARIES",
        [
            ("uuid", "id", "PK"),
            ("uuid", "user_id", "FK"),
            ("string", "title", ""),
            ("text", "summary", ""),
            ("string", "duration_label", ""),
            ("string", "festival_choice", ""),
            ("string", "intensity_label", ""),
            ("json", "preference_snapshot", ""),
            ("text", "request_summary", ""),
            ("datetime", "saved_at", ""),
            ("datetime", "created_at", ""),
        ],
        "#fff6eb",
        "#ff8a2a",
    )
    items = table(
        draw,
        (430, 1030),
        "ITINERARY_ITEMS",
        [
            ("uuid", "id", "PK"),
            ("uuid", "itinerary_id", "FK"),
            ("int", "sort_order", ""),
            ("string", "time_slot", ""),
            ("string", "place_name", ""),
            ("string", "move_hint", ""),
            ("text", "recommendation_reason", ""),
        ],
        "#effcff",
        "#15c7dd",
    )
    reactions = table(
        draw,
        (990, 930),
        "PLAN_REACTIONS",
        [
            ("uuid", "id", "PK"),
            ("uuid", "user_id", "FK"),
            ("uuid", "itinerary_id", "FK"),
            ("string", "reaction_type", ""),
            ("datetime", "created_at", ""),
        ],
        "#f0fff5",
        "#27d96a",
    )

    ux1, uy1, ux2, uy2 = users
    sx1, sy1, sx2, sy2 = social
    ix1, iy1, ix2, iy2 = itineraries
    tx1, ty1, tx2, ty2 = items
    rx1, ry1, rx2, ry2 = reactions

    line_with_label(draw, [(ux1 - 10, uy1 + 170), (360, 340), (190, sy1 - 35), (190, sy1 - 10)], "has", (165, 430), "||", "o{")
    line_with_label(draw, [(ux1 + 170, uy2 + 14), (ux1 + 170, iy1 - 14)], "saves", (765, 405), "||", "o{")
    line_with_label(draw, [(ix1 + 155, iy2 + 14), (tx1 + 155, ty1 - 14)], "contains", (552, 980), "||", "o{")
    line_with_label(draw, [(ux2 + 10, uy1 + 170), (1230, 360), (1250, ry1 - 12)], "reacts", (1245, 600), "||", "o{")
    line_with_label(draw, [(ix2 + 10, iy2 - 25), (1095, 835), (1095, ry1 - 12)], "receives", (1125, 820), "||", "o{")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
