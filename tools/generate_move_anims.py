from __future__ import annotations

import math
import os
import sys
from collections import deque
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from game.creatures import CREATURES
from tools.generate_move_fx import BUILDERS as EFFECT_BUILDERS
from tools.process_anim_strip import process as process_anim_strip

SPRITES = ROOT / "assets" / "sprites"
CREATURES_DIR = SPRITES / "creatures"
MOVE_ANIM_DIR = SPRITES / "move_anim"
SOURCE_ROOT = ROOT / "assets" / "source_sheets" / "move_anims_v1"
SOURCE_BODY = SOURCE_ROOT / "body"
SOURCE_EFFECT = SOURCE_ROOT / "effect"
SOURCE_PROJECTILE = SOURCE_ROOT / "projectile"
AI_PROJECTILE_SHEET = Path(
    "/Users/aravsharma/.codex/generated_images/019dcb13-4e22-7bd2-a0f2-194ac5b58ba3/"
    "ig_0886b5d7ef325fbc0169f17340cef08199a85d5a6a82448ee5.png"
)

FRAMES = 6
CELL = 112

BORDER = (18, 15, 24)
NOODLE = (255, 215, 102)
NOODLE_HI = (255, 242, 180)
SAUCE = (224, 74, 58)
SAUCE_HI = (255, 135, 97)
MEAT = (132, 82, 56)
WOOD = (152, 101, 65)
WOOD_HI = (214, 171, 119)
BEAT = (255, 206, 89)
DRUM_RED = (228, 72, 62)
FOAM = (248, 244, 232)
FOAM_HI = (255, 255, 255)
COFFEE = (158, 109, 78)
LATTE = (216, 177, 121)
TEAL = (121, 229, 220)
FIRE = (249, 130, 58)
GOLD = (255, 205, 90)

MOVE_TO_CREATURE = {}
for creature in CREATURES.values():
    for move in creature.moves:
        MOVE_TO_CREATURE.setdefault(move.anim_key, creature.key)

PROJECTILE_MOVES = {
    "sauce_splash",
    "meatball_panic",
    "sahur_burst",
    "tung_roll",
    "midnight_march",
    "pirouette_pour",
    "foam_ribbon",
    "arabesque_roast",
    "finale_froth",
    "tralala_wave",
    "coral_chorus",
    "crema_dagger",
    "espresso_exit",
    "milky_way_moo",
    "ring_charge",
    "bomb_burst",
    "croco_cannon",
    "frost_spit",
    "desert_chill",
    "pinecone_pop",
    "brrr_blast",
    "banana_boomerang",
    "bananini_barrage",
    "crust_comet",
    "mozza_mob",
    "ricotta_rattle",
    "bake_coil",
    "frost_swirl",
    "brain_freeze",
    "golden_roar",
    "polenta_meteor",
    "ganache_glint",
    "marzipan_mirage",
    "sauce_decree",
    "ravioli_reign",
    "pepper_spear",
    "coliseum_sear",
    "olive_order",
    "boss_banquet",
    "tomato_mortar",
    "bruschetta_barrage",
    "stretch_beam",
    "melt_majesty",
}

AI_PROJECTILE_BANDS = {
    "sauce_splash": (59, 168),
    "meatball_panic": (245, 352),
    "sahur_burst": (404, 566),
    "tung_roll": (626, 735),
    "midnight_march": (774, 920),
    "pirouette_pour": (956, 1061),
    "foam_ribbon": (1110, 1200),
    "arabesque_roast": (1229, 1347),
    "finale_froth": (1368, 1496),
}

BODY_PROFILES = {
    "fork_flick": {
        "shift": [(-6, 2), (-3, 1), (4, -1), (10, -2), (5, 0), (0, 1)],
        "scale": [(0.95, 1.03), (0.98, 1.01), (1.02, 0.99), (1.08, 0.94), (1.01, 1.00), (1.00, 1.00)],
        "angle": [4, 2, -3, -8, -2, 0],
        "overlay": "fork",
    },
    "sauce_splash": {
        "shift": [(-8, 1), (-10, 0), (-5, -1), (5, -2), (12, -1), (4, 1)],
        "scale": [(0.94, 1.05), (0.92, 1.06), (0.98, 1.02), (1.06, 0.95), (1.08, 0.93), (1.00, 1.00)],
        "angle": [6, 8, 3, -4, -7, -1],
        "overlay": "sauce",
    },
    "al_dente_slam": {
        "shift": [(0, 4), (0, 1), (0, -6), (0, 2), (0, 6), (0, 2)],
        "scale": [(1.05, 0.92), (1.04, 0.95), (0.95, 1.10), (0.99, 1.02), (1.08, 0.92), (1.00, 1.00)],
        "angle": [0, 0, 0, 0, 0, 0],
        "overlay": "slam",
    },
    "meatball_panic": {
        "shift": [(-4, 0), (4, -3), (-6, 1), (8, -2), (-2, 2), (2, 0)],
        "scale": [(0.98, 1.01), (1.00, 1.00), (1.02, 0.99), (1.04, 0.97), (1.00, 1.00), (1.00, 1.00)],
        "angle": [-4, 5, -6, 7, -3, 0],
        "overlay": "meatball",
    },
    "drum_knock": {
        "shift": [(0, 2), (-2, 0), (2, -1), (7, -2), (2, -1), (0, 1)],
        "scale": [(0.98, 1.02), (0.98, 1.01), (1.00, 1.00), (1.05, 0.96), (1.01, 0.99), (1.00, 1.00)],
        "angle": [1, -2, 3, -5, -1, 0],
        "overlay": "mallet",
    },
    "sahur_burst": {
        "shift": [(0, 0), (0, -1), (0, -2), (0, -1), (0, 0), (0, 1)],
        "scale": [(0.96, 1.04), (1.02, 0.98), (1.06, 0.94), (1.04, 0.97), (1.00, 1.00), (1.00, 1.00)],
        "angle": [0, -2, 0, 2, 0, 0],
        "overlay": "burst",
    },
    "tung_roll": {
        "shift": [(-8, 0), (-4, -1), (4, 0), (10, 1), (4, 0), (0, 0)],
        "scale": [(1.03, 0.98), (1.05, 0.96), (1.07, 0.95), (1.10, 0.92), (1.04, 0.97), (1.00, 1.00)],
        "angle": [8, 4, -2, -8, -4, 0],
        "overlay": "roll",
    },
    "midnight_march": {
        "shift": [(-6, 2), (-1, -1), (5, 2), (10, -1), (5, 2), (0, 0)],
        "scale": [(0.99, 1.01), (1.02, 0.98), (0.99, 1.02), (1.03, 0.97), (1.00, 1.00), (1.00, 1.00)],
        "angle": [1, -1, 1, -2, 0, 0],
        "overlay": "march",
    },
    "pirouette_pour": {
        "shift": [(0, -2), (2, -4), (0, -5), (-2, -4), (0, -2), (0, 0)],
        "scale": [(0.97, 1.03), (0.94, 1.05), (0.92, 1.07), (0.95, 1.04), (0.98, 1.01), (1.00, 1.00)],
        "angle": [0, 12, 22, 12, 2, 0],
        "overlay": "coffee",
    },
    "foam_ribbon": {
        "shift": [(-3, 0), (-1, -1), (4, -2), (8, -1), (2, 0), (0, 0)],
        "scale": [(0.98, 1.01), (0.98, 1.02), (1.01, 0.99), (1.04, 0.97), (1.00, 1.00), (1.00, 1.00)],
        "angle": [-3, -8, -12, -4, 0, 0],
        "overlay": "ribbon",
    },
    "arabesque_roast": {
        "shift": [(-4, -1), (-1, -4), (5, -7), (10, -4), (5, -1), (0, 0)],
        "scale": [(0.98, 1.01), (0.95, 1.05), (0.92, 1.09), (0.97, 1.02), (1.00, 1.00), (1.00, 1.00)],
        "angle": [-4, -10, -16, -8, -2, 0],
        "overlay": "flame",
    },
    "finale_froth": {
        "shift": [(0, -1), (0, -3), (0, -5), (0, -3), (0, -1), (0, 0)],
        "scale": [(0.98, 1.02), (1.02, 0.99), (1.08, 0.93), (1.04, 0.96), (1.00, 1.00), (1.00, 1.00)],
        "angle": [0, 0, 0, 0, 0, 0],
        "overlay": "froth",
    },
}


def line(surface, color, start, end, width=2):
    pygame.draw.line(surface, BORDER, start, end, width + 2)
    pygame.draw.line(surface, color, start, end, width)


def circle(surface, color, center, radius, border=True, width=0):
    if border:
        pygame.draw.circle(surface, BORDER, center, radius + (1 if width == 0 else 0), 0 if width == 0 else width + 2)
    pygame.draw.circle(surface, color, center, radius, width)


def ellipse(surface, color, rect, border=True, width=0):
    if border:
        pygame.draw.ellipse(surface, BORDER, rect.inflate(2, 2), 0 if width == 0 else width + 2)
    pygame.draw.ellipse(surface, color, rect, width)


def curve(surface, points, color, hi, width=4):
    pygame.draw.lines(surface, BORDER, False, points, width + 2)
    pygame.draw.lines(surface, color, False, points, width)
    if hi:
        pygame.draw.lines(surface, hi, False, [(x, y - 1) for x, y in points], max(1, width - 2))


def burst(surface, center, radius, color, spokes=8):
    cx, cy = center
    for idx in range(spokes):
        ang = math.tau * idx / spokes
        px = cx + int(math.cos(ang) * radius)
        py = cy + int(math.sin(ang) * radius)
        line(surface, color, center, (px, py), 2)


def fit_sprite(image, max_w, max_h):
    width, height = image.get_size()
    scale = min(max_w / width, max_h / height)
    return pygame.transform.scale(image, (max(1, int(width * scale)), max(1, int(height * scale))))


def clear_edge_black(surface, threshold=20):
    out = surface.copy()
    w, h = out.get_size()
    seen = [[False] * h for _ in range(w)]
    q = deque()
    for x in range(w):
        q.append((x, 0))
        q.append((x, h - 1))
    for y in range(h):
        q.append((0, y))
        q.append((w - 1, y))
    while q:
        x, y = q.popleft()
        if x < 0 or y < 0 or x >= w or y >= h or seen[x][y]:
            continue
        seen[x][y] = True
        c = out.get_at((x, y))
        if c.a == 0:
            continue
        if c.r <= threshold and c.g <= threshold and c.b <= threshold:
            out.set_at((x, y), pygame.Color(0, 0, 0, 0))
            q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return out


def transform_sprite(image, scale_xy, angle):
    width = max(1, int(image.get_width() * scale_xy[0]))
    height = max(1, int(image.get_height() * scale_xy[1]))
    scaled = pygame.transform.scale(image, (width, height))
    return pygame.transform.rotate(scaled, angle)


def save_strip(frames, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    strip = pygame.Surface((CELL * len(frames), CELL), pygame.SRCALPHA)
    for idx, frame in enumerate(frames):
        strip.blit(frame, (idx * CELL, 0))
    pygame.image.save(strip, str(path))


def load_portrait(key):
    image = pygame.image.load(str(CREATURES_DIR / f"{key}.png"))
    image = clear_edge_black(image)
    return fit_sprite(image, 74, 74)


def overlay(surface, name, frame_idx):
    p = frame_idx / (FRAMES - 1)
    if name == "fork":
        x = 62 + frame_idx * 3
        y = 42 - frame_idx
        line(surface, FOAM, (x - 10, y), (x, y), 3)
        for dy in (-5, 0, 5):
            line(surface, FOAM_HI, (x, y + dy), (x + 8, y + dy - 1), 2)
    elif name == "sauce":
        centers = [(74, 26 - frame_idx), (84, 34), (76, 44 + frame_idx // 2)]
        for cx, cy in centers:
            ellipse(surface, SAUCE, pygame.Rect(cx - 6, cy - 4, 12, 8))
            circle(surface, SAUCE_HI, (cx - 1, cy - 1), 1, border=False)
    elif name == "slam":
        ring_y = 84 + frame_idx
        pygame.draw.ellipse(surface, BORDER, (30, ring_y, 52, 12), 3)
        pygame.draw.ellipse(surface, GOLD, (31, ring_y + 1, 50, 10), 1)
    elif name == "meatball":
        ang = p * math.tau * 1.5
        for off in (0, 2.1, 4.2):
            cx = 56 + int(math.cos(ang + off) * 14)
            cy = 48 + int(math.sin(ang + off) * 10)
            circle(surface, MEAT, (cx, cy), 5)
            circle(surface, SAUCE, (cx - 1, cy - 1), 2, border=False)
    elif name == "mallet":
        x0 = 20 + frame_idx * 2
        y0 = 72 - frame_idx
        x1 = 38 + frame_idx * 4
        y1 = 50 - frame_idx * 2
        line(surface, WOOD_HI, (x0, y0), (x1, y1), 4)
        ellipse(surface, FOAM, pygame.Rect(x1 - 7, y1 - 6, 14, 12))
    elif name == "burst":
        for rad in (10 + frame_idx * 2, 18 + frame_idx * 2):
            pygame.draw.circle(surface, BORDER, (56, 42), rad, 3)
            pygame.draw.circle(surface, BEAT, (56, 42), rad, 1)
    elif name == "roll":
        pygame.draw.circle(surface, BORDER, (64, 56), 16 + frame_idx // 2, 4)
        pygame.draw.circle(surface, WOOD, (64, 56), 15 + frame_idx // 2, 2)
        line(surface, DRUM_RED, (54, 46), (74, 66), 2)
        line(surface, BEAT, (74, 46), (54, 66), 2)
    elif name == "march":
        for idx, x in enumerate((34, 52, 70)):
            ellipse(surface, BEAT, pygame.Rect(x + frame_idx * 2, 82 - idx % 2 * 4, 12, 6))
    elif name == "coffee":
        ang = p * math.tau
        for off in (0, 2.1, 4.2):
            cx = 56 + int(math.cos(ang + off) * 18)
            cy = 42 + int(math.sin(ang + off) * 10)
            circle(surface, FOAM, (cx, cy), 3)
        pygame.draw.circle(surface, BORDER, (56, 42), 18, 2)
        pygame.draw.circle(surface, LATTE, (56, 42), 18, 1)
    elif name == "ribbon":
        pts = [(22, 74), (38, 56 - frame_idx), (56, 72), (74, 44 + frame_idx), (90, 62)]
        curve(surface, pts, FOAM, TEAL, 4)
    elif name == "flame":
        cx = 74
        cy = 40 - frame_idx
        pts = [(cx, cy - 16), (cx + 10, cy - 3), (cx + 12, cy + 10), (cx, cy + 18), (cx - 10, cy + 8), (cx - 8, cy - 4)]
        pygame.draw.polygon(surface, BORDER, pts)
        pygame.draw.polygon(surface, FIRE, pts)
        inner = [(cx, cy - 10), (cx + 5, cy - 2), (cx + 6, cy + 7), (cx, cy + 11), (cx - 5, cy + 5), (cx - 3, cy - 3)]
        pygame.draw.polygon(surface, GOLD, inner)
    elif name == "froth":
        for ang in range(0, 360, 45):
            rad = math.radians(ang + frame_idx * 12)
            cx = 56 + int(math.cos(rad) * (10 + frame_idx))
            cy = 42 + int(math.sin(rad) * (8 + frame_idx))
            circle(surface, FOAM, (cx, cy), 3)
        burst(surface, (56, 42), 8 + frame_idx * 2, GOLD, 8)


def build_body_frames(move_key, creature_key):
    portrait = load_portrait(creature_key)
    profile = BODY_PROFILES[move_key]
    frames = []
    for idx in range(FRAMES):
        frame = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
        transformed = transform_sprite(portrait, profile["scale"][idx], profile["angle"][idx])
        tx = CELL // 2 - transformed.get_width() // 2 + profile["shift"][idx][0]
        ty = CELL // 2 - transformed.get_height() // 2 + profile["shift"][idx][1] + 4
        frame.blit(transformed, (tx, ty))
        overlay(frame, profile["overlay"], idx)
        frames.append(frame)
    return frames


def center_frames(frames):
    centered = []
    for frame in frames:
        out = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
        x = CELL // 2 - frame.get_width() // 2
        y = CELL // 2 - frame.get_height() // 2
        out.blit(frame, (x, y))
        centered.append(out)
    return centered


def extract_ai_projectile_strips():
    if not AI_PROJECTILE_SHEET.exists():
        return set()
    sheet = pygame.image.load(str(AI_PROJECTILE_SHEET)).convert_alpha()
    saved = set()
    for move_key, (y0, y1) in AI_PROJECTILE_BANDS.items():
        height = y1 - y0 + 1
        band = pygame.Surface((sheet.get_width(), height), pygame.SRCALPHA)
        band.blit(sheet, (0, 0), (0, y0, sheet.get_width(), height))
        pygame.image.save(band, str(SOURCE_PROJECTILE / f"{move_key}.png"))
        saved.add(move_key)
    return saved


def generate_move_anims():
    pygame.init()
    pygame.display.set_mode((1, 1))
    for path in (SOURCE_BODY, SOURCE_EFFECT, SOURCE_PROJECTILE, MOVE_ANIM_DIR):
        path.mkdir(parents=True, exist_ok=True)
    ai_projectiles = extract_ai_projectile_strips()

    for move_key, creature_key in MOVE_TO_CREATURE.items():
        body_strip = SOURCE_BODY / f"{move_key}.png"
        effect_strip = SOURCE_EFFECT / f"{move_key}.png"
        projectile_strip = SOURCE_PROJECTILE / f"{move_key}.png"

        if not body_strip.exists():
            body_frames = build_body_frames(move_key, creature_key)
            save_strip(body_frames, body_strip)
        process_anim_strip(body_strip, move_key, "body", MOVE_ANIM_DIR, frames=FRAMES)

        if not effect_strip.exists():
            _cast, proj_frames, impact_frames = EFFECT_BUILDERS[move_key]()
            effect_frames = center_frames(impact_frames)
            save_strip(effect_frames, effect_strip)
        else:
            proj_frames = []
        process_anim_strip(effect_strip, move_key, "effect", MOVE_ANIM_DIR, frames=FRAMES)

        if move_key in PROJECTILE_MOVES:
            if not projectile_strip.exists() and move_key not in ai_projectiles and proj_frames:
                projectile_frames = center_frames(proj_frames)
                save_strip(projectile_frames, projectile_strip)
            if projectile_strip.exists():
                process_anim_strip(projectile_strip, move_key, "projectile", MOVE_ANIM_DIR, frames=FRAMES)
        else:
            for old in MOVE_ANIM_DIR.glob(f"{move_key}_projectile_*.png"):
                old.unlink()
            if projectile_strip.exists():
                projectile_strip.unlink()

    pygame.quit()
    print("Generated move anim strips and processed sprites.")


if __name__ == "__main__":
    generate_move_anims()
