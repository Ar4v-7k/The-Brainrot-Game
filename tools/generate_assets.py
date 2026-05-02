import math
import os
import struct
import sys
import wave
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

try:
    import pygame
except ImportError as exc:
    raise SystemExit(
        "Pygame is required to generate assets. Run: python3 -m pip install -r requirements.txt"
    ) from exc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from game.creatures import CREATURES
from game.idle_manifest import IDLE_MANIFEST
from game.move_anim_manifest import MOVE_ANIM_MANIFEST
from tools.build_retro_overworld_assets import main as build_retro_overworld_assets
from tools.generate_move_anims import generate_move_anims
from tools.process_idle_strip import content_rect, fill_small_holes, process as process_idle_strip

SPRITES = ROOT / "assets" / "sprites"
SOUNDS = ROOT / "assets" / "sounds"
SOURCE_IDLE_V7 = ROOT / "assets" / "source_sheets" / "brainrot_idles_v7"
BATTLE_IDLE_VARIANTS = {
    "enemy": (108, 92),
    "player": (97, 82),
}


def ensure_dirs():
    for path in (
        SPRITES / "creatures",
        SPRITES / "creature_anim",
        SPRITES / "creature_battle",
        SPRITES / "move_anim",
        SPRITES / "player",
        SPRITES / "overworld",
        SPRITES / "tiles",
        SPRITES / "ui",
        SOUNDS,
    ):
        path.mkdir(parents=True, exist_ok=True)


def save(surface, path):
    pygame.image.save(surface, str(path))


def save_if_missing(surface, path):
    if not path.exists():
        save(surface, path)


def px(surface, color, rect):
    pygame.draw.rect(surface, color, rect)


def outline(surface, points, fill, border=(31, 29, 43), width=3):
    pygame.draw.polygon(surface, border, points)
    inner = []
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    for x, y in points:
        inner.append((int(cx + (x - cx) * 0.86), int(cy + (y - cy) * 0.86)))
    pygame.draw.polygon(surface, fill, inner)


def creature_canvas():
    s = pygame.Surface((64, 64), pygame.SRCALPHA)
    return s


def draw_eye(s, x, y):
    pygame.draw.rect(s, (255, 255, 255), (x, y, 8, 8))
    pygame.draw.rect(s, (31, 29, 43), (x + 4, y + 2, 3, 5))


def draw_spaghettimon():
    s = creature_canvas()
    for i, color in enumerate([(255, 222, 118), (255, 189, 75), (255, 234, 151)]):
        pygame.draw.arc(s, color, (8 + i * 3, 13 + i * 2, 42, 34), 0.2, 5.6, 5)
        pygame.draw.arc(s, (31, 29, 43), (7 + i * 3, 12 + i * 2, 44, 36), 0.2, 5.6, 1)
    pygame.draw.circle(s, (231, 73, 64), (33, 31), 17)
    pygame.draw.circle(s, (255, 106, 84), (29, 27), 8)
    pygame.draw.circle(s, (31, 29, 43), (33, 31), 18, 3)
    draw_eye(s, 22, 24)
    draw_eye(s, 37, 24)
    pygame.draw.rect(s, (31, 29, 43), (29, 40, 9, 3))
    pygame.draw.rect(s, (255, 245, 214), (30, 40, 2, 2))
    return s


def draw_mozzarellion():
    s = creature_canvas()
    pygame.draw.ellipse(s, (31, 29, 43), (10, 13, 45, 41))
    pygame.draw.ellipse(s, (248, 247, 224), (13, 15, 39, 36))
    pygame.draw.ellipse(s, (255, 255, 255), (20, 10, 28, 19))
    pygame.draw.rect(s, (248, 247, 224), (18, 38, 9, 16))
    pygame.draw.rect(s, (248, 247, 224), (39, 37, 9, 17))
    pygame.draw.rect(s, (31, 29, 43), (18, 51, 9, 4))
    pygame.draw.rect(s, (31, 29, 43), (39, 51, 9, 4))
    draw_eye(s, 22, 27)
    draw_eye(s, 38, 27)
    pygame.draw.rect(s, (235, 86, 115), (30, 40, 7, 3))
    pygame.draw.circle(s, (255, 222, 118), (47, 20), 5)
    return s


def draw_pastaflame():
    s = creature_canvas()
    outline(s, [(32, 5), (48, 24), (43, 53), (20, 55), (13, 27)], (255, 111, 64))
    outline(s, [(31, 13), (42, 28), (38, 47), (24, 49), (20, 29)], (255, 202, 87), width=2)
    pygame.draw.circle(s, (239, 71, 111), (32, 35), 15)
    pygame.draw.circle(s, (31, 29, 43), (32, 35), 16, 3)
    draw_eye(s, 22, 30)
    draw_eye(s, 37, 30)
    pygame.draw.rect(s, (31, 29, 43), (27, 43, 11, 3))
    pygame.draw.line(s, (255, 245, 214), (13, 22), (5, 18), 3)
    pygame.draw.line(s, (255, 245, 214), (49, 24), (58, 20), 3)
    return s


def draw_cappucciclown():
    s = creature_canvas()
    pygame.draw.rect(s, (31, 29, 43), (14, 18, 38, 36), border_radius=8)
    pygame.draw.rect(s, (159, 91, 72), (17, 22, 32, 29), border_radius=7)
    pygame.draw.ellipse(s, (255, 255, 255), (17, 10, 31, 18))
    pygame.draw.circle(s, (239, 71, 111), (33, 34), 6)
    draw_eye(s, 21, 27)
    draw_eye(s, 39, 27)
    pygame.draw.rect(s, (31, 29, 43), (27, 43, 13, 2))
    pygame.draw.rect(s, (63, 167, 245), (10, 47, 14, 8))
    pygame.draw.rect(s, (255, 202, 87), (41, 47, 14, 8))
    pygame.draw.rect(s, (31, 29, 43), (7, 49, 19, 5))
    pygame.draw.rect(s, (31, 29, 43), (40, 49, 19, 5))
    return s


def draw_gondoloblin():
    s = creature_canvas()
    pygame.draw.ellipse(s, (31, 29, 43), (10, 17, 43, 34))
    pygame.draw.ellipse(s, (68, 183, 150), (13, 19, 37, 29))
    pygame.draw.polygon(s, (31, 29, 43), [(13, 25), (3, 18), (11, 35)])
    pygame.draw.polygon(s, (31, 29, 43), [(50, 25), (61, 18), (53, 35)])
    pygame.draw.polygon(s, (68, 183, 150), [(13, 27), (6, 22), (12, 33)])
    pygame.draw.polygon(s, (68, 183, 150), [(50, 27), (58, 22), (52, 33)])
    draw_eye(s, 22, 29)
    draw_eye(s, 38, 29)
    pygame.draw.rect(s, (31, 29, 43), (27, 42, 12, 3))
    pygame.draw.line(s, (139, 87, 62), (8, 55), (56, 46), 4)
    pygame.draw.line(s, (255, 245, 214), (7, 55), (56, 46), 1)
    return s


def draw_risottornado():
    s = creature_canvas()
    for r, c in [(25, (209, 235, 142)), (20, (255, 245, 214)), (14, (242, 218, 110))]:
        pygame.draw.circle(s, (31, 29, 43), (32, 32), r + 2)
        pygame.draw.circle(s, c, (32, 32), r)
    for angle in (0, 120, 240):
        x = 32 + int(math.cos(math.radians(angle)) * 22)
        y = 32 + int(math.sin(math.radians(angle)) * 16)
        pygame.draw.circle(s, (255, 255, 255), (x, y), 5)
        pygame.draw.circle(s, (31, 29, 43), (x, y), 5, 1)
    draw_eye(s, 22, 27)
    draw_eye(s, 38, 27)
    pygame.draw.rect(s, (31, 29, 43), (27, 41, 12, 3))
    pygame.draw.arc(s, (63, 167, 245), (7, 11, 49, 45), 0.1, 5.5, 3)
    return s


def generate_creatures():
    drawers = {
        "spaghettimon": draw_spaghettimon,
        "mozzarellion": draw_mozzarellion,
        "pastaflame": draw_pastaflame,
        "cappucciclown": draw_cappucciclown,
        "gondoloblin": draw_gondoloblin,
        "risottornado": draw_risottornado,
    }
    for key, drawer in drawers.items():
        save_if_missing(drawer(), SPRITES / "creatures" / f"{key}.png")
    for key, creature in CREATURES.items():
        path = SPRITES / "creatures" / f"{key}.png"
        if path.exists():
            continue
        save(draw_generated_brainrot(key, creature.kind), path)


def draw_generated_brainrot(key, kind):
    palette = generated_palette(key, kind)
    s = creature_canvas()
    body = palette[0]
    accent = palette[1]
    light = palette[2]
    dark = (24, 20, 30)
    seed = sum((idx + 1) * ord(ch) for idx, ch in enumerate(key))
    mode = seed % 8
    pygame.draw.ellipse(s, dark, (10, 13, 44, 42))
    if mode == 0:
        pygame.draw.ellipse(s, body, (13, 16, 38, 34))
        pygame.draw.circle(s, accent, (43, 20), 8)
        pygame.draw.rect(s, body, (20, 44, 9, 12), border_radius=3)
        pygame.draw.rect(s, body, (37, 44, 9, 12), border_radius=3)
    elif mode == 1:
        pygame.draw.rect(s, body, (15, 17, 34, 33), border_radius=9)
        pygame.draw.circle(s, accent, (20, 15), 8)
        pygame.draw.circle(s, accent, (46, 16), 7)
        pygame.draw.rect(s, light, (23, 8, 20, 10), border_radius=5)
    elif mode == 2:
        pygame.draw.polygon(s, body, [(32, 8), (52, 30), (43, 55), (19, 55), (11, 30)])
        pygame.draw.circle(s, accent, (32, 29), 12)
        pygame.draw.rect(s, light, (25, 47, 16, 7), border_radius=3)
    elif mode == 3:
        pygame.draw.ellipse(s, body, (9, 22, 47, 25))
        pygame.draw.polygon(s, accent, [(16, 25), (4, 17), (10, 36)])
        pygame.draw.polygon(s, accent, [(49, 25), (61, 17), (55, 36)])
        pygame.draw.rect(s, body, (22, 40, 21, 14), border_radius=5)
    elif mode == 4:
        pygame.draw.circle(s, body, (32, 31), 23)
        for angle in range(0, 360, 60):
            x = 32 + int(math.cos(math.radians(angle)) * 24)
            y = 31 + int(math.sin(math.radians(angle)) * 18)
            pygame.draw.circle(s, accent, (x, y), 5)
    elif mode == 5:
        pygame.draw.rect(s, body, (12, 20, 42, 28), border_radius=6)
        pygame.draw.rect(s, accent, (17, 13, 32, 12), border_radius=5)
        pygame.draw.line(s, light, (15, 48), (8, 56), 4)
        pygame.draw.line(s, light, (49, 48), (57, 56), 4)
    elif mode == 6:
        pygame.draw.ellipse(s, body, (16, 10, 32, 44))
        pygame.draw.arc(s, accent, (8, 24, 48, 24), 0, math.pi, 4)
        pygame.draw.circle(s, light, (32, 16), 5)
    else:
        pygame.draw.ellipse(s, body, (14, 12, 36, 40))
        pygame.draw.polygon(s, accent, [(24, 12), (32, 4), (40, 12)])
        pygame.draw.rect(s, light, (20, 43, 25, 7), border_radius=3)
    draw_eye(s, 22, 27)
    draw_eye(s, 38, 27)
    pygame.draw.rect(s, dark, (27, 41, 12, 3))
    return apply_outline(s)


def generated_palette(key, kind):
    seed = sum(ord(ch) for ch in key + kind)
    palettes = [
        ((236, 86, 80), (255, 205, 90), (255, 240, 170)),
        ((80, 176, 118), (255, 210, 96), (204, 255, 200)),
        ((91, 146, 222), (121, 229, 220), (220, 245, 255)),
        ((167, 111, 211), (255, 166, 221), (245, 222, 255)),
        ((198, 135, 75), (255, 235, 170), (255, 246, 219)),
        ((220, 220, 235), (101, 190, 255), (255, 255, 255)),
        ((250, 179, 75), (234, 91, 112), (255, 238, 170)),
        ((90, 88, 112), (120, 255, 180), (215, 255, 238)),
    ]
    if "Signal" in kind:
        return ((82, 128, 238), (91, 255, 203), (236, 246, 255))
    if "Ancient" in kind:
        return ((190, 151, 90), (95, 222, 188), (255, 237, 180))
    if "Frost" in kind:
        return ((180, 225, 245), (98, 179, 255), (255, 255, 255))
    if "Shadow" in kind:
        return ((76, 70, 100), (234, 91, 112), (220, 210, 245))
    return palettes[seed % len(palettes)]


IDLE_POSES = {
    "noodle": [(-1, 0, 1.00, 1.00), (1, -1, 1.03, 0.99), (2, 1, 0.99, 1.03), (0, 0, 1.01, 1.00)],
    "heavy": [(0, 0, 1.00, 1.00), (0, -1, 1.02, 0.98), (0, 1, 0.98, 1.03), (0, 0, 1.00, 1.01)],
    "flame": [(0, 0, 1.00, 1.00), (-1, -1, 1.01, 0.98), (1, 0, 0.99, 1.03), (0, -1, 1.02, 0.99)],
    "jitter": [(-1, 0, 1.00, 1.00), (1, -1, 1.00, 1.00), (-1, 1, 1.00, 1.00), (1, 0, 1.00, 1.00)],
    "sneak": [(0, 0, 1.00, 1.00), (1, -1, 1.01, 0.99), (2, 0, 1.00, 1.00), (1, 1, 0.99, 1.01)],
    "hover": [(0, 0, 1.00, 1.00), (0, -2, 1.00, 1.00), (0, 0, 1.00, 1.02), (0, 1, 0.99, 1.00)],
    "rat": [(0, 0, 1.00, 1.00), (1, -1, 1.01, 1.00), (-1, 0, 1.00, 1.00), (1, 1, 1.00, 1.00)],
    "coil": [(0, 0, 1.00, 1.00), (-1, 0, 1.02, 0.99), (1, 0, 0.98, 1.03), (0, 1, 1.00, 1.00)],
    "melt": [(0, 0, 1.00, 1.00), (0, 1, 0.99, 1.03), (0, 2, 0.98, 1.04), (0, 0, 1.00, 1.00)],
    "tank": [(0, 0, 1.00, 1.00), (0, -1, 1.01, 0.99), (0, 1, 0.99, 1.02), (0, 0, 1.00, 1.00)],
    "drum": [(0, 0, 1.00, 1.00), (0, -1, 1.02, 0.98), (1, 1, 0.99, 1.03), (-1, 0, 1.01, 0.99)],
    "plane": [(0, 0, 1.00, 1.00), (2, -1, 1.00, 1.00), (0, 0, 1.00, 1.00), (-2, 1, 1.00, 1.00)],
    "ballet": [(0, 0, 1.00, 1.00), (-1, -2, 1.01, 0.99), (1, 0, 1.00, 1.01), (0, 1, 0.99, 1.00)],
    "singer": [(0, 0, 1.00, 1.00), (1, -1, 1.01, 0.99), (0, 0, 1.00, 1.01), (-1, 1, 1.00, 1.00)],
    "camel": [(0, 0, 1.00, 1.00), (1, -1, 1.00, 1.00), (0, 1, 1.00, 1.02), (-1, 0, 1.00, 1.00)],
    "boss": [(0, 0, 1.00, 1.00), (0, -1, 1.02, 0.99), (0, 0, 1.00, 1.01), (0, 1, 0.99, 1.01)],
    "royal": [(0, 0, 1.00, 1.00), (0, -1, 1.01, 0.99), (0, 0, 1.00, 1.01), (0, 1, 1.00, 1.00)],
    "gladiator": [(0, 0, 1.00, 1.00), (-1, -1, 1.02, 0.99), (1, 0, 0.99, 1.02), (0, 1, 1.00, 1.00)],
    "kaiju": [(0, 0, 1.00, 1.00), (0, -1, 1.02, 0.99), (0, 1, 0.99, 1.03), (0, 0, 1.00, 1.00)],
    "puppet": [(0, 0, 1.00, 1.00), (1, -1, 1.01, 1.00), (-1, 1, 1.00, 1.01), (1, 0, 1.00, 1.00)],
}


def apply_outline(surface, color=(22, 16, 24)):
    mask = pygame.mask.from_surface(surface, 10)
    edge = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
    out = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        out.blit(edge, (dx, dy))
    out.blit(surface, (0, 0))
    return out


def crispify(surface):
    scaled_down = pygame.transform.scale(surface, (64, 64))
    scaled_up = pygame.transform.scale(scaled_down, surface.get_size())
    return apply_outline(scaled_up)


def blit_center(surface, sprite, dx=0, dy=0):
    x = (surface.get_width() - sprite.get_width()) // 2 + dx
    y = (surface.get_height() - sprite.get_height()) // 2 + dy
    surface.blit(sprite, (x, y))
    return x, y


def add_idle_accent(surface, style, frame_index):
    pale = (255, 244, 204)
    warm = (255, 179, 92)
    aqua = (132, 227, 255)
    pink = (255, 154, 212)
    steam = (240, 244, 252)
    dust = (215, 186, 118)
    if style == "noodle":
        pygame.draw.arc(surface, pale, (28 + frame_index, 8, 20, 12), 0.4, 2.7, 2)
    elif style == "flame":
        pygame.draw.circle(surface, warm, (50, 13 + (frame_index % 2)), 2)
        pygame.draw.circle(surface, (255, 91, 58), (44, 8 + ((frame_index + 1) % 2)), 2)
    elif style == "jitter":
        pygame.draw.circle(surface, pink, (16 + frame_index * 2, 20), 1)
        pygame.draw.circle(surface, aqua, (78 - frame_index * 2, 24), 1)
    elif style == "hover":
        pygame.draw.arc(surface, aqua, (19, 69 - frame_index, 58, 14), 0.2, 2.9, 2)
    elif style == "melt":
        pygame.draw.rect(surface, steam, (42, 79 + frame_index, 4, 6), border_radius=2)
    elif style == "drum":
        pygame.draw.line(surface, warm, (16, 42), (8 + frame_index * 2, 42), 2)
        pygame.draw.line(surface, warm, (80, 42), (88 - frame_index * 2, 42), 2)
    elif style == "plane":
        pygame.draw.line(surface, steam, (10, 24), (0, 22 + frame_index), 2)
        pygame.draw.line(surface, steam, (10, 30), (0, 29 + frame_index), 1)
    elif style == "ballet":
        pygame.draw.circle(surface, pale, (72, 18 + frame_index), 2)
        pygame.draw.circle(surface, pale, (22, 66 - frame_index), 1)
    elif style == "singer":
        pygame.draw.arc(surface, steam, (74, 16 + frame_index, 10, 12), 0.0, 5.0, 2)
    elif style == "camel":
        pygame.draw.circle(surface, dust, (22, 80), 2)
        pygame.draw.circle(surface, dust, (74, 79 - frame_index), 1)
    elif style == "royal":
        pygame.draw.circle(surface, pale, (74, 12 + (frame_index % 2)), 2)
    elif style == "kaiju":
        pygame.draw.circle(surface, dust, (24, 82), 2)
        pygame.draw.circle(surface, dust, (72, 82), 2)
    elif style == "puppet":
        pygame.draw.line(surface, steam, (36, 0), (36 + frame_index, 16), 1)
        pygame.draw.line(surface, steam, (60, 0), (60 - frame_index, 16), 1)


def build_idle_frame(base, style, frame_index):
    frame = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    dx, dy, sx, sy = IDLE_POSES.get(style, IDLE_POSES["hover"])[frame_index]
    sw = max(8, int(base.get_width() * sx))
    sh = max(8, int(base.get_height() * sy))
    sprite = pygame.transform.scale(base, (sw, sh))
    blit_center(frame, sprite, dx, dy)
    add_idle_accent(frame, style, frame_index)
    return apply_outline(frame)


def generate_idle_frames():
    processed = set()
    if SOURCE_IDLE_V7.exists():
        for key in CREATURES:
            strip = SOURCE_IDLE_V7 / f"{key}.png"
            if strip.exists():
                existing = list((SPRITES / "creature_anim").glob(f"{key}_idle_*.png"))
                if len(existing) >= 6:
                    processed.add(key)
                    continue
                process_idle_strip(strip, key, SPRITES / "creature_anim", frames=6)
                processed.add(key)
    if not pygame.get_init():
        pygame.init()
    if not pygame.display.get_init():
        pygame.display.init()
    pygame.display.get_surface() or pygame.display.set_mode((1, 1))
    for key in CREATURES:
        existing = list((SPRITES / "creature_anim").glob(f"{key}_idle_*.png"))
        if key in processed or len(existing) >= 6:
            continue
        base_path = SPRITES / "creatures" / f"{key}.png"
        if not base_path.exists():
            continue
        meta = IDLE_MANIFEST.get(key, {"style": "hover"})
        base = crispify(pygame.image.load(str(base_path)).convert_alpha())
        save(base, base_path)
        poses = IDLE_POSES.get(meta.get("style", "hover"), IDLE_POSES["hover"])
        for frame_index in range(6):
            idle_frame = build_idle_frame(base, meta["style"], frame_index % len(poses))
            save(idle_frame, SPRITES / "creature_anim" / f"{key}_idle_{frame_index}.png")


def crop_to_content(surface):
    rect = content_rect(surface)
    out = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    out.blit(surface, (0, 0), rect)
    return out, rect


def fill_battle_pinholes(surface, max_area=24, max_span=5):
    w, h = surface.get_size()
    seen = [[False] * h for _ in range(w)]
    out = surface.copy()
    for x in range(w):
        for y in range(h):
            if seen[x][y] or out.get_at((x, y)).a != 0:
                continue
            stack = [(x, y)]
            seen[x][y] = True
            points = []
            touches_edge = False
            while stack:
                cx, cy = stack.pop()
                points.append((cx, cy))
                if cx == 0 or cy == 0 or cx == w - 1 or cy == h - 1:
                    touches_edge = True
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < w and 0 <= ny < h and not seen[nx][ny] and out.get_at((nx, ny)).a == 0:
                        seen[nx][ny] = True
                        stack.append((nx, ny))
            if touches_edge or len(points) > max_area:
                continue
            xs = [pt[0] for pt in points]
            ys = [pt[1] for pt in points]
            if (max(xs) - min(xs) + 1) > max_span or (max(ys) - min(ys) + 1) > max_span:
                continue
            out = fill_small_holes(out, max_area=max_area)
            return fill_battle_pinholes(out, max_area=max_area, max_span=max_span)
    return out


def bake_battle_idle_frames():
    if not pygame.get_init():
        pygame.init()
    if not pygame.display.get_init():
        pygame.display.init()
    try:
        pygame.display.get_surface() or pygame.display.set_mode((1, 1))
    except pygame.error:
        pygame.display.set_mode((1, 1))
    for key in IDLE_MANIFEST:
        frame_paths = sorted((SPRITES / "creature_anim").glob(f"{key}_idle_*.png"), key=lambda path: int(path.stem.split("_")[-1]))
        if not frame_paths:
            continue
        raw_frames = [pygame.image.load(str(path)).convert_alpha() for path in frame_paths]
        cropped = [crop_to_content(frame) for frame in raw_frames]
        max_w = max(sprite.get_width() for sprite, _rect in cropped)
        max_h = max(sprite.get_height() for sprite, _rect in cropped)
        for variant, (box_w, box_h) in BATTLE_IDLE_VARIANTS.items():
            scale = min((box_w - 4) / max_w, (box_h - 4) / max_h)
            scale = max(scale, 0.1)
            for idx, (sprite, _rect) in enumerate(cropped):
                scaled = pygame.transform.scale(
                    sprite,
                    (
                        max(1, int(sprite.get_width() * scale)),
                        max(1, int(sprite.get_height() * scale)),
                    ),
                )
                canvas = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
                x = box_w // 2 - scaled.get_width() // 2
                y = box_h - 2 - scaled.get_height()
                canvas.blit(scaled, (x, y))
                # Source-art pinhole filling was useful for a tiny roster, but it is very
                # expensive once the adventure roster expands. The idle-strip processor
                # already removes background leaks and generated sprites are clean.
                save(canvas, SPRITES / "creature_battle" / f"{key}_{variant}_{idx}.png")


def tile_base(color):
    s = pygame.Surface((32, 32), pygame.SRCALPHA)
    s.fill(color)
    return s


def generate_tiles():
    grass = tile_base((81, 197, 92))
    for x in range(0, 32, 5):
        pygame.draw.line(grass, (49, 147, 72), (x, 31), (x + 4, 20), 1)
    save_if_missing(grass, SPRITES / "tiles" / "grass.png")

    path = tile_base((219, 181, 116))
    for x in range(0, 32, 8):
        for y in range(0, 32, 8):
            pygame.draw.rect(path, (197, 154, 98), (x + 1, y + 1, 2, 2))
    save_if_missing(path, SPRITES / "tiles" / "path.png")

    wall = tile_base((93, 84, 116))
    for y in range(0, 32, 8):
        pygame.draw.line(wall, (58, 52, 78), (0, y), (32, y), 2)
    for x in range(0, 32, 16):
        pygame.draw.line(wall, (58, 52, 78), (x, 0), (x, 32), 2)
    save_if_missing(wall, SPRITES / "tiles" / "wall.png")

    water = tile_base((63, 167, 245))
    for y in (8, 18, 28):
        pygame.draw.arc(water, (155, 218, 255), (0, y - 6, 18, 10), 0, math.pi, 2)
        pygame.draw.arc(water, (27, 113, 190), (14, y - 5, 18, 10), 0, math.pi, 2)
    save_if_missing(water, SPRITES / "tiles" / "water.png")

    flowers = grass.copy()
    for pos, c in [((8, 9), (239, 71, 111)), ((23, 14), (255, 202, 87)), ((15, 24), (255, 255, 255))]:
        pygame.draw.circle(flowers, c, pos, 2)
        pygame.draw.circle(flowers, (49, 147, 72), (pos[0], pos[1] + 3), 1)
    save_if_missing(flowers, SPRITES / "tiles" / "flowers.png")


def draw_player(direction, frame):
    s = pygame.Surface((32, 32), pygame.SRCALPHA)
    leg = frame * 2
    pygame.draw.rect(s, (31, 29, 43), (10, 9, 12, 17), border_radius=3)
    pygame.draw.rect(s, (63, 167, 245), (11, 10, 10, 13), border_radius=3)
    pygame.draw.rect(s, (31, 29, 43), (9, 4, 14, 9), border_radius=4)
    pygame.draw.rect(s, (255, 202, 87), (10, 5, 12, 7), border_radius=3)
    pygame.draw.rect(s, (239, 71, 111), (7, 7, 18, 3))
    pygame.draw.rect(s, (31, 29, 43), (9, 24, 5, 5 + leg))
    pygame.draw.rect(s, (31, 29, 43), (18, 24, 5, 7 - leg))
    if direction == "up":
        pygame.draw.rect(s, (31, 29, 43), (12, 6, 8, 3))
    elif direction == "left":
        pygame.draw.rect(s, (31, 29, 43), (10, 8, 3, 3))
    elif direction == "right":
        pygame.draw.rect(s, (31, 29, 43), (19, 8, 3, 3))
    else:
        pygame.draw.rect(s, (31, 29, 43), (12, 8, 3, 3))
        pygame.draw.rect(s, (31, 29, 43), (18, 8, 3, 3))
    return s


def generate_player():
    for direction in ("down", "up", "left", "right"):
        for frame in (0, 1):
            save_if_missing(
                draw_player(direction, frame),
                SPRITES / "player" / f"player_{direction}_{frame}.png",
            )


def generate_ui():
    cap = pygame.Surface((210, 270), pygame.SRCALPHA)
    pygame.draw.circle(cap, (31, 29, 43), (105, 135), 84)
    pygame.draw.circle(cap, (245, 71, 111), (105, 135), 72)
    pygame.draw.rect(cap, (230, 230, 238), (88, 104, 34, 84), border_radius=14)
    pygame.draw.rect(cap, (245, 71, 111), (88, 104, 34, 42), border_radius=12)
    pygame.draw.circle(cap, (255, 255, 255), (84, 76), 14)
    pygame.draw.circle(cap, (255, 255, 255), (148, 206), 10)
    save_if_missing(cap, SPRITES / "ui" / "capsule.png")

    tonic = pygame.Surface((211, 270), pygame.SRCALPHA)
    pygame.draw.circle(tonic, (31, 29, 43), (106, 146), 80)
    pygame.draw.circle(tonic, (23, 196, 171), (106, 146), 67)
    pygame.draw.rect(tonic, (56, 39, 31), (87, 52, 38, 36), border_radius=8)
    pygame.draw.rect(tonic, (228, 204, 159), (92, 45, 28, 20), border_radius=7)
    pygame.draw.circle(tonic, (225, 47, 71), (106, 141), 26)
    pygame.draw.rect(tonic, (48, 160, 76), (100, 111, 12, 18), border_radius=6)
    save_if_missing(tonic, SPRITES / "ui" / "tonic.png")

    icon_specs = {
        "attack": ((145, 165), (234, 51, 75), [(75, 44), (106, 56), (70, 114), (48, 109)]),
        "defend": ((140, 164), (48, 175, 255), [(70, 34), (104, 56), (95, 112), (46, 112), (36, 56)]),
        "special": ((145, 165), (220, 85, 255), None),
        "capture": ((145, 165), (255, 195, 42), None),
        "item": ((143, 164), (26, 219, 179), None),
        "run": ((143, 164), (230, 236, 244), None),
    }
    for name, (size, color, polygon) in icon_specs.items():
        icon = pygame.Surface(size, pygame.SRCALPHA)
        w, h = size
        pygame.draw.polygon(
            icon,
            (31, 29, 43),
            [(w // 2, 6), (w - 18, 33), (w - 18, h - 35), (w // 2, h - 8), (18, h - 35), (18, 33)],
        )
        pygame.draw.polygon(
            icon,
            color,
            [(w // 2, 14), (w - 26, 38), (w - 26, h - 40), (w // 2, h - 16), (26, h - 40), (26, 38)],
            4,
        )
        if name == "special":
            pygame.draw.circle(icon, color, (w // 2, h // 2), 15)
            pygame.draw.line(icon, (255, 240, 255), (w // 2, 42), (w // 2, h - 42), 6)
            pygame.draw.line(icon, (255, 240, 255), (42, h // 2), (w - 42, h // 2), 6)
        elif name == "capture":
            pygame.draw.circle(icon, color, (w // 2, h // 2), 34, 7)
            pygame.draw.circle(icon, color, (w // 2, h // 2), 10)
            pygame.draw.line(icon, color, (w // 2 - 34, h // 2), (w // 2 + 34, h // 2), 5)
        elif name == "item":
            pygame.draw.rect(icon, color, (54, 52, 35, 52), border_radius=11)
            pygame.draw.rect(icon, (255, 255, 255), (62, 34, 19, 22), border_radius=7)
        elif name == "run":
            pygame.draw.circle(icon, (120, 133, 154), (68, 58), 13)
            pygame.draw.line(icon, (230, 236, 244), (69, 70), (80, 102), 7)
            pygame.draw.line(icon, (230, 236, 244), (80, 80), (102, 66), 7)
            pygame.draw.line(icon, (230, 236, 244), (78, 101), (98, 125), 7)
            pygame.draw.line(icon, (230, 236, 244), (73, 101), (53, 126), 7)
        else:
            pygame.draw.polygon(icon, (255, 245, 245), polygon)
        save_if_missing(icon, SPRITES / "ui" / f"{name}.png")

    hp = pygame.Surface((920, 105), pygame.SRCALPHA)
    pygame.draw.rect(hp, (17, 14, 26), (0, 24, 920, 48), border_radius=18)
    pygame.draw.rect(hp, (255, 70, 135), (0, 24, 920, 48), 4, border_radius=18)
    segments = [
        (20, 255, 106),
        (88, 255, 94),
        (176, 252, 72),
        (255, 208, 62),
        (255, 120, 56),
        (240, 64, 64),
    ]
    x = 38
    for color in segments:
        pygame.draw.rect(hp, color, (x, 35, 132, 24), border_radius=7)
        x += 138
    save_if_missing(hp, SPRITES / "ui" / "hp_bar_full.png")

    panel = pygame.Surface((765, 390), pygame.SRCALPHA)
    pygame.draw.rect(panel, (14, 17, 29), (12, 12, 741, 366), border_radius=24)
    pygame.draw.rect(panel, (255, 70, 135), (12, 12, 741, 366), 4, border_radius=24)
    save_if_missing(panel, SPRITES / "ui" / "battle_menu_panel.png")


def retro_panel(size, fill=(248, 239, 194), border=(38, 45, 69), accent=(91, 117, 176)):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    rect = surf.get_rect()
    pygame.draw.rect(surf, (41, 35, 36), rect.move(2, 2))
    pygame.draw.rect(surf, fill, rect)
    pygame.draw.rect(surf, (255, 248, 215), rect.inflate(-4, -4), 1)
    pygame.draw.rect(surf, accent, rect.inflate(-2, -2), 1)
    pygame.draw.rect(surf, border, rect, 2)
    return surf


def generate_runtime_ui():
    runtime = SPRITES / "runtime_ui"
    runtime.mkdir(parents=True, exist_ok=True)
    save(retro_panel((348, 58)), runtime / "title_card.png")
    save(retro_panel((372, 64)), runtime / "command_box.png")
    save(retro_panel((142, 52)), runtime / "stat_box.png")
    save(retro_panel((352, 44)), runtime / "slot_panel.png")
    save(retro_panel((100, 124)), runtime / "reward_card.png")
    save(retro_panel((72, 18)), runtime / "menu_button.png")

    title_bg = pygame.Surface((384, 216))
    for y in range(216):
        t = y / 215
        color = (
            int(124 * (1 - t) + 86 * t),
            int(190 * (1 - t) + 151 * t),
            int(220 * (1 - t) + 109 * t),
        )
        pygame.draw.line(title_bg, color, (0, y), (384, y))
    for x in range(0, 384, 16):
        pygame.draw.line(title_bg, (105, 169, 96), (x, 156), (x + 10, 216))
    pygame.draw.rect(title_bg, (222, 196, 117), (0, 132, 384, 20))
    pygame.draw.rect(title_bg, (116, 177, 82), (0, 152, 384, 64))
    save(title_bg, runtime / "title_bg.png")

    battle_bg = pygame.Surface((384, 216))
    battle_bg.fill((118, 188, 224))
    pygame.draw.rect(battle_bg, (222, 196, 117), (0, 118, 384, 22))
    pygame.draw.rect(battle_bg, (116, 177, 82), (0, 140, 384, 76))
    pygame.draw.ellipse(battle_bg, (154, 198, 106), (42, 116, 118, 28))
    pygame.draw.ellipse(battle_bg, (154, 198, 106), (236, 142, 118, 28))
    save(battle_bg, runtime / "battle_bg.png")


def write_wav(name, frequency=440, duration=0.14, kind="sine"):
    sample_rate = 22050
    frames = int(sample_rate * duration)
    path = SOUNDS / f"{name}.wav"
    with wave.open(str(path), "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        data = bytearray()
        for i in range(frames):
            t = i / sample_rate
            env = max(0, 1 - i / frames)
            if kind == "noise":
                value = ((i * 1103515245 + 12345) & 0xFFFF) / 32768 - 1
            elif kind == "square":
                value = 1 if math.sin(math.tau * frequency * t) > 0 else -1
            else:
                value = math.sin(math.tau * frequency * t)
            data.extend(struct.pack("<h", int(value * env * 12000)))
        wav.writeframes(bytes(data))


def generate_sounds():
    write_wav("menu", 660, 0.07)
    write_wav("attack", 220, 0.12, "square")
    write_wav("special", 880, 0.22)
    write_wav("hit", 120, 0.11, "noise")
    write_wav("capture", 523, 0.35)


def move_anims_complete():
    for move_key, config in MOVE_ANIM_MANIFEST.items():
        for frame in range(6):
            if not (SPRITES / "move_anim" / f"{move_key}_body_{frame}.png").exists():
                return False
            if not (SPRITES / "move_anim" / f"{move_key}_effect_{frame}.png").exists():
                return False
            if config["projectile_path"] != "none" and not (SPRITES / "move_anim" / f"{move_key}_projectile_{frame}.png").exists():
                return False
    return True


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    ensure_dirs()
    generate_creatures()
    generate_idle_frames()
    bake_battle_idle_frames()
    build_retro_overworld_assets()
    generate_tiles()
    generate_player()
    generate_ui()
    generate_runtime_ui()
    if not move_anims_complete():
        generate_move_anims()
    generate_sounds()
    pygame.quit()
    print("Generated Brainrotmon sprites and sounds in assets/.")


if __name__ == "__main__":
    main()
