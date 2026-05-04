from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


MAGENTA = (255, 0, 255, 255)
BLACK = (0, 0, 0, 255)
OUTLINE = (28, 21, 18, 255)
CACTUS = (75, 157, 82, 255)
CACTUS_DARK = (38, 105, 58, 255)
CACTUS_LIGHT = (132, 205, 103, 255)
SAND = (224, 177, 91, 255)
SAND_DARK = (166, 110, 52, 255)
BROWN = (118, 73, 40, 255)
CREAM = (244, 224, 166, 255)
WHITE = (245, 241, 215, 255)
RED = (198, 48, 50, 255)
BLUE = (90, 189, 220, 255)
YELLOW = (246, 213, 88, 255)


OUT_DIR = Path("/Users/aravsharma/Desktop/brainrotmon_final_tilesets/new_brainrots")
OUT_PATH = OUT_DIR / "lirili_larila_battle_sheet.png"

TITLE_H = 24
CANVAS_W = 96 * 6
ROW_HEIGHTS = [96, 96, 96, 96, 96, 32, 64, 32, 64, 96]
LINE_H = 1


def rect(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], fill) -> None:
    draw.rectangle(xy, fill=fill)


def ellipse(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], fill) -> None:
    draw.ellipse(xy, fill=fill)


def make_frame_base() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGBA", (48, 48), MAGENTA)
    return image, ImageDraw.Draw(image)


def draw_lirili(anim: str, frame: int) -> Image.Image:
    image, draw = make_frame_base()

    bob = [0, -1, -2, -1, 0, 1][frame]
    lean = 0
    arm_raise = 0
    trunk = 0
    eye_mode = "normal"
    dust = False

    if anim == "needle":
        lean = [-2, -2, 0, 2, 1, 0][frame]
        arm_raise = [0, -3, -6, -3, -1, 0][frame]
        trunk = [0, -1, -2, 2, 1, 0][frame]
    elif anim == "mirage":
        lean = [0, 1, 2, -1, 0, 0][frame]
        trunk = [0, 1, 2, 3, 1, 0][frame]
    elif anim == "stomp":
        bob = [0, -2, -4, 3, 1, 0][frame]
        lean = [0, -1, -1, 1, 0, 0][frame]
        dust = frame in (3, 4)
    elif anim == "spin":
        lean = [-3, 0, 3, 0, -2, 0][frame]
        arm_raise = [-4, 2, -4, 2, -2, 0][frame]
        trunk = [-2, 2, -2, 2, -1, 0][frame]
    elif anim == "flinch":
        lean = [0, 4, 5, 2, 1, 0][frame]
        bob = [0, -1, 1, 0, 0, 0][frame]
        eye_mode = "hurt" if frame in (1, 2, 3) else "normal"

    ox = lean
    oy = bob

    # Ground shadow and sandals.
    ellipse(draw, (13 + ox, 40, 35 + ox, 44), (72, 47, 34, 255))
    ellipse(draw, (14 + ox, 39 + oy, 24 + ox, 44 + oy), OUTLINE)
    ellipse(draw, (25 + ox, 39 + oy, 35 + ox, 44 + oy), OUTLINE)
    ellipse(draw, (15 + ox, 40 + oy, 23 + ox, 43 + oy), SAND)
    ellipse(draw, (26 + ox, 40 + oy, 34 + ox, 43 + oy), SAND)
    rect(draw, (17 + ox, 40 + oy, 21 + ox, 41 + oy), BROWN)
    rect(draw, (28 + ox, 40 + oy, 32 + ox, 41 + oy), BROWN)

    if dust:
        rect(draw, (6, 39, 10, 41), SAND)
        rect(draw, (38, 38, 43, 40), SAND)
        rect(draw, (4, 42, 7, 43), SAND_DARK)
        rect(draw, (42, 42, 46, 43), SAND_DARK)

    # Cactus body.
    ellipse(draw, (15 + ox, 15 + oy, 34 + ox, 41 + oy), OUTLINE)
    ellipse(draw, (17 + ox, 16 + oy, 32 + ox, 40 + oy), CACTUS)
    rect(draw, (23 + ox, 16 + oy, 25 + ox, 39 + oy), CACTUS_DARK)
    rect(draw, (19 + ox, 20 + oy, 20 + ox, 34 + oy), CACTUS_LIGHT)
    rect(draw, (28 + ox, 21 + oy, 29 + ox, 33 + oy), CACTUS_LIGHT)

    # Cactus arms.
    rect(draw, (9 + ox, 23 + oy + arm_raise, 16 + ox, 27 + oy + arm_raise), OUTLINE)
    rect(draw, (8 + ox, 18 + oy + arm_raise, 12 + ox, 27 + oy + arm_raise), OUTLINE)
    rect(draw, (10 + ox, 24 + oy + arm_raise, 16 + ox, 26 + oy + arm_raise), CACTUS)
    rect(draw, (9 + ox, 19 + oy + arm_raise, 11 + ox, 26 + oy + arm_raise), CACTUS)

    rect(draw, (32 + ox, 23 + oy - arm_raise, 39 + ox, 27 + oy - arm_raise), OUTLINE)
    rect(draw, (37 + ox, 18 + oy - arm_raise, 41 + ox, 27 + oy - arm_raise), OUTLINE)
    rect(draw, (32 + ox, 24 + oy - arm_raise, 38 + ox, 26 + oy - arm_raise), CACTUS)
    rect(draw, (38 + ox, 19 + oy - arm_raise, 40 + ox, 26 + oy - arm_raise), CACTUS)

    # Elephant-like head and ears.
    ellipse(draw, (13 + ox, 6 + oy, 36 + ox, 24 + oy), OUTLINE)
    ellipse(draw, (15 + ox, 8 + oy, 34 + ox, 23 + oy), CACTUS)
    ellipse(draw, (9 + ox, 11 + oy, 18 + ox, 22 + oy), OUTLINE)
    ellipse(draw, (31 + ox, 11 + oy, 40 + ox, 22 + oy), OUTLINE)
    ellipse(draw, (11 + ox, 13 + oy, 17 + ox, 21 + oy), CACTUS_DARK)
    ellipse(draw, (32 + ox, 13 + oy, 38 + ox, 21 + oy), CACTUS_DARK)

    # Trunk.
    draw.line((24 + ox, 20 + oy, 24 + ox + trunk, 29 + oy, 27 + ox + trunk, 33 + oy), fill=OUTLINE, width=5)
    draw.line((24 + ox, 20 + oy, 24 + ox + trunk, 29 + oy, 27 + ox + trunk, 33 + oy), fill=CACTUS, width=3)
    rect(draw, (27 + ox + trunk, 32 + oy, 30 + ox + trunk, 34 + oy), OUTLINE)
    rect(draw, (27 + ox + trunk, 32 + oy, 29 + ox + trunk, 33 + oy), CACTUS_LIGHT)

    # Face.
    if eye_mode == "hurt":
        draw.line((18 + ox, 14 + oy, 21 + ox, 17 + oy), fill=OUTLINE, width=1)
        draw.line((21 + ox, 14 + oy, 18 + ox, 17 + oy), fill=OUTLINE, width=1)
        draw.line((29 + ox, 14 + oy, 32 + ox, 17 + oy), fill=OUTLINE, width=1)
        draw.line((32 + ox, 14 + oy, 29 + ox, 17 + oy), fill=OUTLINE, width=1)
        rect(draw, (22 + ox, 19 + oy, 27 + ox, 20 + oy), RED)
    else:
        rect(draw, (18 + ox, 14 + oy, 21 + ox, 17 + oy), OUTLINE)
        rect(draw, (29 + ox, 14 + oy, 32 + ox, 17 + oy), OUTLINE)
        rect(draw, (19 + ox, 14 + oy, 19 + ox, 15 + oy), WHITE)
        rect(draw, (30 + ox, 14 + oy, 30 + ox, 15 + oy), WHITE)
        rect(draw, (22 + ox, 19 + oy, 27 + ox, 20 + oy), OUTLINE)
        rect(draw, (23 + ox, 20 + oy, 26 + ox, 20 + oy), RED)

    # Spines and flower.
    for sx, sy in [(20, 9), (27, 10), (18, 26), (30, 28), (24, 35)]:
        rect(draw, (sx + ox, sy + oy, sx + ox, sy + oy), WHITE)
    rect(draw, (23 + ox, 5 + oy, 25 + ox, 7 + oy), RED)
    rect(draw, (22 + ox, 6 + oy, 26 + ox, 6 + oy), RED)
    rect(draw, (24 + ox, 6 + oy, 24 + ox, 6 + oy), YELLOW)

    if anim == "mirage" and frame in (2, 3, 4):
        draw.arc((30, 10, 45, 25), 290, 70, fill=BLUE, width=1)
        draw.arc((33, 7, 48, 28), 290, 70, fill=YELLOW, width=1)
    if anim == "needle" and frame in (2, 3):
        draw.line((38, 21, 45, 18), fill=WHITE, width=2)
        rect(draw, (44, 17, 45, 18), CACTUS_LIGHT)
    if anim == "spin":
        draw.arc((5, 6, 43, 42), 20 + frame * 45, 120 + frame * 45, fill=YELLOW, width=1)

    return image.resize((96, 96), Image.Resampling.NEAREST)


def draw_needle_projectile(frame: int) -> Image.Image:
    image = Image.new("RGBA", (16, 16), MAGENTA)
    draw = ImageDraw.Draw(image)
    shift = frame % 3
    draw.polygon([(3 + shift, 8), (11 + shift, 4), (14 + shift, 8), (11 + shift, 12)], fill=OUTLINE)
    draw.polygon([(4 + shift, 8), (11 + shift, 5), (13 + shift, 8), (11 + shift, 11)], fill=CACTUS_LIGHT)
    rect(draw, (2, 7, 4, 8), WHITE)
    return image.resize((32, 32), Image.Resampling.NEAREST)


def draw_needle_impact(frame: int) -> Image.Image:
    image = Image.new("RGBA", (32, 32), MAGENTA)
    draw = ImageDraw.Draw(image)
    r = 4 + frame * 2
    cx, cy = 16, 16
    ellipse(draw, (cx - r, cy - r, cx + r, cy + r), OUTLINE)
    ellipse(draw, (cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2), SAND)
    for dx, dy in [(0, -13), (10, -8), (13, 2), (-11, 8), (-13, -3)]:
        draw.line((cx, cy, cx + dx, cy + dy), fill=CACTUS_LIGHT, width=2)
    if frame > 2:
        ellipse(draw, (6, 20, 11, 25), SAND_DARK)
        ellipse(draw, (22, 7, 27, 12), SAND_DARK)
    return image.resize((64, 64), Image.Resampling.NEAREST)


def draw_sound_projectile(frame: int) -> Image.Image:
    image = Image.new("RGBA", (16, 16), MAGENTA)
    draw = ImageDraw.Draw(image)
    color = BLUE if frame % 2 == 0 else YELLOW
    draw.arc((2, 4, 10, 12), 300, 60, fill=OUTLINE, width=2)
    draw.arc((4, 3, 14, 13), 300, 60, fill=color, width=2)
    rect(draw, (2, 7, 4, 9), WHITE)
    return image.resize((32, 32), Image.Resampling.NEAREST)


def draw_sound_impact(frame: int) -> Image.Image:
    image = Image.new("RGBA", (32, 32), MAGENTA)
    draw = ImageDraw.Draw(image)
    cx, cy = 16, 16
    for i, color in enumerate([OUTLINE, BLUE, YELLOW]):
        r = 5 + frame * 2 + i * 3
        draw.arc((cx - r, cy - r, cx + r, cy + r), 0, 360, fill=color, width=2)
    if frame in (3, 4, 5):
        rect(draw, (8, 15, 11, 18), WHITE)
        rect(draw, (22, 12, 25, 15), WHITE)
    return image.resize((64, 64), Image.Resampling.NEAREST)


def paste_row(sheet: Image.Image, y: int, frames: list[Image.Image]) -> None:
    x = 0
    for frame in frames:
        sheet.paste(frame, (x, y))
        x += frame.width


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    total_h = TITLE_H + LINE_H + sum(ROW_HEIGHTS) + LINE_H * (len(ROW_HEIGHTS) - 1)
    sheet = Image.new("RGBA", (CANVAS_W, total_h), MAGENTA)
    draw = ImageDraw.Draw(sheet)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 9)
    except OSError:
        font = ImageFont.load_default()
    title = "LIRILI LARILA | Moves: Desert Needle, Mirage Trumpet, Sandal Stomp, Cactus Spin"
    draw.text((4, 7), title, fill=BLACK, font=font)
    y = TITLE_H
    rect(draw, (0, y, CANVAS_W - 1, y), BLACK)
    y += LINE_H

    rows = [
        [draw_lirili("idle", i) for i in range(6)],
        [draw_lirili("needle", i) for i in range(6)],
        [draw_lirili("mirage", i) for i in range(6)],
        [draw_lirili("stomp", i) for i in range(6)],
        [draw_lirili("spin", i) for i in range(6)],
        [draw_needle_projectile(i) for i in range(6)],
        [draw_needle_impact(i) for i in range(6)],
        [draw_sound_projectile(i) for i in range(6)],
        [draw_sound_impact(i) for i in range(6)],
        [draw_lirili("flinch", i) for i in range(6)],
    ]

    for idx, row in enumerate(rows):
        paste_row(sheet, y, row)
        y += ROW_HEIGHTS[idx]
        if idx != len(rows) - 1:
            rect(draw, (0, y, CANVAS_W - 1, y), BLACK)
            y += LINE_H

    sheet.save(OUT_PATH)
    print(OUT_PATH)
    print(sheet.size)


if __name__ == "__main__":
    main()
