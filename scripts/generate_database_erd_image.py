from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "images" / "database-concept-erd.png"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "malgunbd.ttf" if bold else "malgun.ttf"
    return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size=size)


def wrap(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=face)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def box(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    title: str,
    rows: list[str],
    fill: str,
    stroke: str,
) -> None:
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=14, fill=fill, outline=stroke, width=3)
    draw.rectangle((x1, y1, x2, y1 + 42), fill=stroke)
    draw.text((x1 + 16, y1 + 8), title, font=font(21, True), fill="#ffffff")
    y = y1 + 58
    body = font(16)
    for row in rows:
        for line in wrap(draw, row, body, x2 - x1 - 32):
            draw.text((x1 + 16, y), line, font=body, fill="#2f2f2f")
            y += 23


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], label: str) -> None:
    routed_arrow(draw, [start, end], label)


def routed_arrow(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], label: str) -> None:
    color = "#5f6368"
    draw.line(points, fill=color, width=3, joint="curve")
    sx, sy = points[-2]
    ex, ey = points[-1]
    if abs(ex - sx) >= abs(ey - sy):
        wing = 12 if ex > sx else -12
        arrowhead = [(ex, ey), (ex - wing, ey - 7), (ex - wing, ey + 7)]
    else:
        wing = 12 if ey > sy else -12
        arrowhead = [(ex, ey), (ex - 7, ey - wing), (ex + 7, ey - wing)]
    draw.polygon(arrowhead, fill=color)
    mid = len(points) // 2
    lx = points[mid][0] - 28
    ly = points[mid][1] - 18
    draw.rounded_rectangle((lx - 8, ly - 4, lx + 72, ly + 22), radius=7, fill="#ffffff", outline="#d0d4da")
    draw.text((lx, ly), label, font=font(14, True), fill="#4d5156")


def main() -> None:
    image = Image.new("RGB", (1900, 1160), "#fbfaf7")
    draw = ImageDraw.Draw(image)
    draw.text((70, 45), "Lovv Concept ERD", font=font(34, True), fill="#1f2933")
    draw.text(
        (70, 92),
        "Core relationship map for users, recommendation flow, saved activity, and destination content.",
        font=font(18),
        fill="#5f6368",
    )

    users = (70, 165, 420, 335)
    auth = (520, 145, 900, 305)
    profile = (520, 365, 900, 555)
    themes = (990, 405, 1300, 555)
    recommend = (70, 455, 470, 685)
    activity = (570, 690, 980, 930)
    destinations = (1110, 675, 1510, 915)
    itineraries = (1140, 155, 1510, 345)

    box(draw, users, "users", ["Root account entity", "has many linked records"], "#fff4e6", "#e07a2f")
    box(draw, auth, "Auth & Roles", ["user_social_accounts", "user_roles", "roles"], "#eef6ff", "#4f8fd6")
    box(draw, profile, "Profile & Preferences", ["user_profiles", "user_preferences", "user_preference_themes"], "#eefaf0", "#4d9a61")
    box(draw, themes, "themes", ["selected by user_preference_themes"], "#f4f0ff", "#8a6fd1")
    box(draw, recommend, "Recommendation Flow", ["recommendation_requests", "recommendation_results", "itineraries"], "#fff9db", "#c89b21")
    box(draw, activity, "Saved Activity", ["saved_itineraries", "user_feedback", "bookmarks", "visit_records", "visit_ratings"], "#f5f7fa", "#7a869a")
    box(draw, destinations, "Destination Content", ["destinations", "attractions", "festivals", "visitor_statistics"], "#eaf8f7", "#2d9c93")
    box(draw, itineraries, "itineraries", ["created by recommendation_results", "targets destinations"], "#ffeef3", "#d65a7a")

    arrow(draw, (420, 245), (520, 225), "has")
    routed_arrow(draw, [(420, 295), (470, 295), (470, 455), (520, 455)], "owns")
    arrow(draw, (900, 475), (990, 475), "maps")
    arrow(draw, (250, 335), (250, 455), "requests")
    routed_arrow(draw, [(470, 570), (960, 570), (960, 120), (1140, 250)], "creates")
    arrow(draw, (1510, 250), (1510, 780), "targets")
    routed_arrow(draw, [(420, 320), (500, 320), (500, 790), (570, 790)], "saves")
    arrow(draw, (1110, 805), (980, 805), "feeds")

    draw.rounded_rectangle((1570, 665, 1830, 935), radius=12, fill="#ffffff", outline="#b9c0ca", width=2)
    for y, text in [
        (690, "destinations 1:N attractions"),
        (735, "destinations 1:N festivals"),
        (780, "destinations 1:N visitor_statistics"),
        (825, "users 1:N saved_itineraries"),
        (870, "visit_records 1:N visit_ratings"),
    ]:
        draw.ellipse((1590, y + 5, 1602, y + 17), fill="#e07a2f")
        draw.text((1615, y), text, font=font(16), fill="#374151")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
