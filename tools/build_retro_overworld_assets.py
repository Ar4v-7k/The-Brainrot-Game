from __future__ import annotations

import json
import os
import random
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

import pygame


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "overworld"
AI_TILE_SOURCES = (
    ROOT / "assets" / "source_sheets" / "hf_tileset_v1" / "imagegen_tileset_source.png",
    ROOT / "assets" / "source_sheets" / "adventure_retro_v1" / "tile_building_sheet_retro_v1.png",
    ROOT / "assets" / "sprites" / "overworld" / "tile_building_sheet_retro_v1.png",
)
TILE = 16
COLS = 32
ROWS = 32


CORE_LAYOUT = [
    ["grass_light", "grass_dark", "path_dirt", "path_stone", "water_still", "water_wave", "sand", "snow"],
    ["tree_top_left", "tree_top_right", "tree_bot_left", "tree_bot_right", "wall_stone", "wall_dark", "door_closed", "door_open"],
    ["flower_patch", "tall_grass", "cave_floor", "cave_wall", "ice_floor", "jungle_floor", "desert_floor", "ruin_floor"],
    ["house_roof", "house_wall", "fence_h", "fence_v", "sign_post", "counter_shop", "bed", "chest"],
]


TILE_CATEGORIES = (
    ("ground_grass", 80),
    ("ground_path_dirt", 60),
    ("ground_path_stone", 45),
    ("ground_sand", 30),
    ("ground_snow", 30),
    ("ground_ice", 25),
    ("ground_cave", 40),
    ("ground_ruin", 35),
    ("ground_jungle", 35),
    ("ground_desert", 25),
    ("water_still_variant", 24),
    ("water_wave_variant", 28),
    ("water_edge", 28),
    ("waterfall", 16),
    ("vegetation_tree", 80),
    ("vegetation_grass", 30),
    ("vegetation_flower", 24),
    ("vegetation_bush", 28),
    ("vegetation_special", 24),
    ("building_wall", 70),
    ("building_roof", 58),
    ("building_door", 24),
    ("building_window", 24),
    ("building_fence", 24),
    ("building_rotria", 32),
    ("object_rock", 30),
    ("object_cliff", 36),
    ("object_bridge", 20),
    ("object_item", 24),
    ("object_berry", 20),
    ("object_market", 16),
    ("object_signal", 24),
    ("interior_floor", 32),
    ("interior_wall", 32),
    ("interior_furniture", 42),
    ("interior_lab", 20),
    ("interior_shop", 18),
    ("special_warp", 12),
    ("special_night", 16),
    ("special_corrupt", 36),
)


PALETTES = {
    "grass": [(142, 199, 101), (105, 174, 78), (75, 139, 66), (48, 95, 55)],
    "path": [(198, 163, 95), (167, 126, 72), (130, 92, 56), (93, 69, 50)],
    "stone": [(164, 160, 143), (126, 125, 119), (85, 88, 92), (52, 58, 64)],
    "water": [(83, 166, 218), (50, 125, 194), (33, 83, 154), (202, 238, 245)],
    "sand": [(223, 203, 124), (204, 170, 96), (172, 131, 76), (245, 231, 160)],
    "snow": [(236, 246, 246), (186, 223, 232), (139, 188, 215), (92, 139, 178)],
    "dark": [(79, 76, 88), (56, 55, 69), (35, 38, 50), (21, 24, 34)],
    "ruin": [(143, 129, 102), (111, 101, 88), (76, 74, 70), (181, 167, 120)],
    "jungle": [(56, 143, 70), (39, 103, 59), (27, 76, 51), (151, 196, 87)],
    "roof": [(201, 88, 76), (157, 65, 68), (99, 48, 57), (236, 141, 93)],
    "wall": [(217, 188, 135), (179, 139, 96), (123, 91, 75), (246, 221, 166)],
    "wood": [(153, 99, 55), (111, 72, 49), (75, 50, 42), (211, 145, 81)],
}


def rect(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], color: tuple[int, int, int]) -> None:
    draw.rectangle(xy, fill=color)


def sprinkle(draw: ImageDraw.ImageDraw, rng: random.Random, colors: list[tuple[int, int, int]], count: int) -> None:
    for _ in range(count):
        x = rng.randrange(TILE)
        y = rng.randrange(TILE)
        color = rng.choice(colors)
        if rng.random() < 0.18:
            rect(draw, (x, y, min(TILE - 1, x + 1), y), color)
        else:
            draw.point((x, y), fill=color)


def make_tile(name: str, seed: int) -> Image.Image:
    rng = random.Random(seed * 9973 + sum(ord(c) for c in name))
    img = Image.new("RGBA", (TILE, TILE), (255, 0, 255, 0))
    draw = ImageDraw.Draw(img)

    if name in ("grass_light", "grass_dark", "flower_patch", "tall_grass"):
        pal = PALETTES["grass"]
        base = pal[0] if name != "grass_dark" else pal[1]
        rect(draw, (0, 0, 15, 15), base)
        sprinkle(draw, rng, pal[1:] + [(177, 220, 108)], 34)
        if name == "tall_grass":
            for x in range(1, 16, 3):
                draw.line((x, 14, x + rng.choice([-1, 0, 1]), 4), fill=pal[3], width=1)
                draw.line((x + 1, 15, x + 2, 6), fill=pal[1], width=1)
        if name == "flower_patch":
            for x, y, c in ((3, 5, (234, 92, 116)), (9, 10, (255, 219, 92)), (12, 4, (111, 171, 232))):
                draw.point((x, y), fill=c)
                draw.point((x + 1, y), fill=c)
    elif name in ("path_dirt", "path_stone"):
        pal = PALETTES["path"] if name == "path_dirt" else PALETTES["stone"]
        rect(draw, (0, 0, 15, 15), pal[0])
        sprinkle(draw, rng, pal[1:], 40)
        if name == "path_stone":
            for x in range(0, 16, 5):
                draw.line((x, 0, x + 3, 15), fill=pal[2])
            draw.line((0, 8, 15, 8), fill=pal[2])
    elif name in ("water_still", "water_wave"):
        pal = PALETTES["water"]
        rect(draw, (0, 0, 15, 15), pal[1])
        for y in (4, 9, 13):
            off = rng.randrange(4)
            draw.arc((off, y - 2, off + 9, y + 3), 0, 180, fill=pal[3], width=1)
            if name == "water_wave":
                draw.arc((off + 7, y - 1, off + 16, y + 4), 0, 180, fill=pal[0], width=1)
    elif name in ("sand", "snow", "ice_floor", "desert_floor"):
        key = "snow" if name in ("snow", "ice_floor") else "sand"
        pal = PALETTES[key]
        rect(draw, (0, 0, 15, 15), pal[0])
        sprinkle(draw, rng, pal[1:], 30)
        if name == "ice_floor":
            draw.line((2, 3, 13, 12), fill=pal[2])
            draw.line((12, 2, 5, 15), fill=pal[1])
    elif name.startswith("tree_"):
        pal = PALETTES["jungle"]
        rect(draw, (0, 0, 15, 15), pal[1])
        sprinkle(draw, rng, [pal[0], pal[2], pal[3]], 45)
        if "bot" in name:
            rect(draw, (6 if "left" in name else 0, 5, 15 if "right" in name else 9, 15), PALETTES["wood"][1])
            sprinkle(draw, rng, [pal[0], pal[2]], 15)
    elif name in ("wall_stone", "wall_dark", "cave_wall", "cave_floor", "ruin_floor", "jungle_floor"):
        key = "dark" if name in ("wall_dark", "cave_wall", "cave_floor") else "ruin" if name == "ruin_floor" else "jungle"
        pal = PALETTES[key]
        rect(draw, (0, 0, 15, 15), pal[0])
        sprinkle(draw, rng, pal[1:], 36)
        if "wall" in name:
            rect(draw, (0, 0, 15, 2), pal[2])
            rect(draw, (0, 13, 15, 15), pal[2])
            for x in range(0, 16, 8):
                draw.line((x, 0, x, 15), fill=pal[2])
    elif name in ("door_closed", "door_open"):
        rect(draw, (0, 0, 15, 15), PALETTES["wall"][1])
        rect(draw, (4, 3, 11, 15), PALETTES["wood"][1])
        rect(draw, (5, 4, 10, 15), PALETTES["wood"][0] if name == "door_closed" else (42, 34, 31))
        draw.point((10, 9), fill=(242, 206, 91))
    elif name in ("house_roof", "house_wall"):
        pal = PALETTES["roof"] if name == "house_roof" else PALETTES["wall"]
        rect(draw, (0, 0, 15, 15), pal[0])
        for y in range(3, 16, 4):
            draw.line((0, y, 15, y), fill=pal[1])
        sprinkle(draw, rng, pal[1:], 20)
    elif name in ("fence_h", "fence_v", "sign_post", "counter_shop", "bed", "chest"):
        rect(draw, (0, 0, 15, 15), PALETTES["grass"][0])
        wood = PALETTES["wood"]
        if name == "fence_h":
            rect(draw, (0, 6, 15, 8), wood[1])
            rect(draw, (3, 2, 5, 13), wood[2])
            rect(draw, (11, 2, 13, 13), wood[2])
        elif name == "fence_v":
            rect(draw, (6, 0, 8, 15), wood[1])
            rect(draw, (2, 3, 13, 5), wood[2])
            rect(draw, (2, 11, 13, 13), wood[2])
        elif name == "sign_post":
            rect(draw, (3, 2, 12, 8), (229, 191, 105))
            rect(draw, (4, 3, 11, 7), (119, 75, 49))
            rect(draw, (7, 8, 8, 15), wood[2])
        elif name == "counter_shop":
            rect(draw, (1, 8, 14, 15), wood[0])
            rect(draw, (1, 7, 14, 9), (236, 204, 120))
        elif name == "bed":
            rect(draw, (2, 3, 13, 14), (93, 138, 212))
            rect(draw, (3, 4, 12, 7), (240, 239, 214))
        else:
            rect(draw, (3, 5, 12, 13), wood[0])
            rect(draw, (2, 4, 13, 7), wood[3])
            rect(draw, (7, 8, 9, 10), (250, 221, 86))
    else:
        family = rng.choice(list(PALETTES.values()))
        rect(draw, (0, 0, 15, 15), family[0])
        sprinkle(draw, rng, family[1:], 28 + seed % 26)
        if seed % 5 == 0:
            draw.line((0, seed % 16, 15, (seed * 3) % 16), fill=family[-1])
        if seed % 7 == 0:
            rect(draw, (seed % 12, (seed * 5) % 12, seed % 12 + 2, (seed * 5) % 12 + 2), family[2])
    return img


def build_tileset() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGBA", (COLS * TILE, ROWS * TILE), (255, 0, 255, 0))
    index: dict[str, list[int]] = {}
    used = set()
    for row, names in enumerate(CORE_LAYOUT):
        for col, name in enumerate(names):
            sheet.paste(make_tile(name, row * 8 + col), (col * TILE, row * TILE))
            index[name] = [row, col]
            used.add((row, col))

    detail_id = 0
    for row in range(ROWS):
        for col in range(COLS):
            if (row, col) in used:
                continue
            name = f"detail_{detail_id:04d}"
            sheet.paste(make_tile(name, 100 + detail_id), (col * TILE, row * TILE))
            index[name] = [row, col]
            detail_id += 1

    sheet.save(OUT / "tileset.png")
    (OUT / "tileset_index.json").write_text(json.dumps(index, indent=2))


def draw_person(draw: ImageDraw.ImageDraw, x: int, y: int, facing: str, frame: int, shirt, hair, skin, accent) -> None:
    leg = frame - 1
    draw.rectangle((x + 5, y + 2, x + 10, y + 7), fill=skin)
    draw.rectangle((x + 4, y + 1, x + 11, y + 3), fill=hair)
    if facing == "up":
        draw.rectangle((x + 4, y + 2, x + 11, y + 5), fill=hair)
    elif facing == "left":
        draw.point((x + 5, y + 5), fill=(35, 32, 32))
    elif facing == "right":
        draw.point((x + 10, y + 5), fill=(35, 32, 32))
    else:
        draw.point((x + 6, y + 5), fill=(35, 32, 32))
        draw.point((x + 9, y + 5), fill=(35, 32, 32))
    draw.rectangle((x + 4, y + 8, x + 11, y + 12), fill=(35, 32, 32))
    draw.rectangle((x + 5, y + 8, x + 10, y + 12), fill=shirt)
    draw.rectangle((x + 4, y + 9, x + 5, y + 11), fill=accent)
    draw.rectangle((x + 10, y + 9, x + 11, y + 11), fill=accent)
    draw.rectangle((x + 5 + min(0, leg), y + 13, x + 6 + min(0, leg), y + 15), fill=(42, 54, 91))
    draw.rectangle((x + 9 + max(0, leg), y + 13, x + 10 + max(0, leg), y + 15), fill=(42, 54, 91))


def make_walk(path: Path, shirt, hair, skin, accent) -> None:
    sheet = Image.new("RGBA", (TILE * 3, TILE * 4), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)
    for row, facing in enumerate(("down", "up", "left", "right")):
        for frame in range(3):
            draw_person(draw, frame * TILE, row * TILE, facing, frame, shirt, hair, skin, accent)
    sheet.save(path)


def build_sprites() -> None:
    make_walk(OUT / "player_walk.png", (65, 126, 216), (69, 45, 35), (224, 170, 120), (241, 205, 86))
    make_walk(OUT / "npc_base.png", (96, 173, 93), (82, 54, 38), (218, 164, 117), (231, 118, 94))
    make_walk(OUT / "trainer_sprite.png", (204, 75, 82), (49, 42, 58), (232, 180, 132), (246, 222, 104))


def _pygame_tile_names() -> list[str]:
    slots: list[str | None] = [None] * (COLS * ROWS)
    for row, core_row in enumerate(CORE_LAYOUT):
        for col, name in enumerate(core_row):
            slots[row * COLS + col] = name
    names: list[str] = []
    for prefix, count in TILE_CATEGORIES:
        for idx in range(count):
            names.append(f"{prefix}_{idx:03d}")
    bonus = 0
    for idx, current in enumerate(slots):
        if current is None:
            if names:
                slots[idx] = names.pop(0)
            else:
                slots[idx] = f"bonus_rotria_detail_{bonus:04d}"
                bonus += 1
    return [name or "bonus_rotria_detail_9999" for name in slots]


def _pg_rect(surface: pygame.Surface, xy: tuple[int, int, int, int], color: tuple[int, int, int]) -> None:
    x1, y1, x2, y2 = xy
    pygame.draw.rect(surface, color, pygame.Rect(x1, y1, x2 - x1 + 1, y2 - y1 + 1))


def _pg_sprinkle(surface: pygame.Surface, rng: random.Random, colors: list[tuple[int, int, int]], count: int) -> None:
    for _ in range(count):
        x = rng.randrange(TILE)
        y = rng.randrange(TILE)
        color = rng.choice(colors)
        if rng.random() < 0.2:
            pygame.draw.line(surface, color, (x, y), (min(TILE - 1, x + 1), y))
        else:
            surface.set_at((x, y), color)


def _pg_make_tile(name: str, seed: int) -> pygame.Surface:
    rng = random.Random(seed * 5381 + sum(ord(c) for c in name))
    tile = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    tile.fill((255, 0, 255, 0))
    lower = name.lower()

    if "water" in lower:
        pal = PALETTES["water"]
        tile.fill(pal[1])
        for y in (3 + seed % 3, 8, 13):
            pygame.draw.arc(tile, pal[3], pygame.Rect(rng.randrange(0, 6), y - 2, 10, 5), 0, math.pi if "math" in globals() else 3.14159, 1)
            if "wave" in lower or "fall" in lower:
                pygame.draw.arc(tile, pal[0], pygame.Rect(rng.randrange(4, 10), y - 1, 9, 5), 0, 3.14159, 1)
        if "edge" in lower:
            pygame.draw.line(tile, PALETTES["sand"][0], (0, 15), (15, 15))
    elif "snow" in lower or "ice" in lower:
        pal = PALETTES["snow"]
        tile.fill(pal[0])
        _pg_sprinkle(tile, rng, pal[1:], 22)
        if "ice" in lower:
            pygame.draw.line(tile, pal[2], (2, 3), (13, 12))
            pygame.draw.line(tile, pal[1], (11, 1), (5, 15))
    elif "sand" in lower or "desert" in lower:
        pal = PALETTES["sand"]
        tile.fill(pal[0])
        _pg_sprinkle(tile, rng, pal[1:], 28)
    elif "path_stone" in lower or "stone" in lower or "rock" in lower or "cliff" in lower:
        pal = PALETTES["stone"]
        tile.fill(pal[0])
        _pg_sprinkle(tile, rng, pal[1:], 36)
        pygame.draw.line(tile, pal[2], (0, seed % 16), (15, (seed * 3) % 16))
    elif "path_dirt" in lower or "dirt" in lower:
        pal = PALETTES["path"]
        tile.fill(pal[0])
        _pg_sprinkle(tile, rng, pal[1:], 42)
    elif "tree" in lower or "jungle" in lower or "vegetation" in lower or "grass" in lower or "flower" in lower or "bush" in lower:
        pal = PALETTES["jungle"] if "jungle" in lower or "tree" in lower else PALETTES["grass"]
        tile.fill(pal[0])
        _pg_sprinkle(tile, rng, pal[1:] + [pal[3]], 42)
        if "tree" in lower:
            _pg_rect(tile, (6, 5, 9, 15), PALETTES["wood"][1])
            pygame.draw.circle(tile, pal[1], (7, 6), 7)
            pygame.draw.circle(tile, pal[2], (11, 9), 5)
        if "flower" in lower:
            for _ in range(3):
                tile.set_at((rng.randrange(3, 14), rng.randrange(3, 14)), rng.choice(((238, 91, 112), (242, 211, 82), (91, 139, 212))))
    elif "roof" in lower or "building_roof" in lower:
        pal = PALETTES["roof"]
        tile.fill(pal[0])
        for y in range(2, 16, 4):
            pygame.draw.line(tile, pal[1], (0, y), (15, y))
        _pg_sprinkle(tile, rng, pal[1:], 18)
    elif "wall" in lower or "building" in lower or "house" in lower:
        pal = PALETTES["wall"]
        tile.fill(pal[0])
        _pg_sprinkle(tile, rng, pal[1:], 20)
        pygame.draw.rect(tile, pal[1], pygame.Rect(0, 0, 16, 3))
        if "door" in lower:
            _pg_rect(tile, (4, 3, 11, 15), PALETTES["wood"][1])
            tile.set_at((10, 9), (246, 216, 84))
    elif "door" in lower:
        tile.fill(PALETTES["wall"][1])
        _pg_rect(tile, (4, 2, 11, 15), PALETTES["wood"][1])
        tile.set_at((10, 9), (246, 216, 84))
    elif "fence" in lower or "bridge" in lower or "wood" in lower:
        tile.fill(PALETTES["grass"][0])
        _pg_rect(tile, (0, 6, 15, 8), PALETTES["wood"][1])
        _pg_rect(tile, (3, 2, 5, 13), PALETTES["wood"][2])
        _pg_rect(tile, (11, 2, 13, 13), PALETTES["wood"][2])
    elif "interior" in lower or "counter" in lower or "bed" in lower or "chest" in lower:
        tile.fill(PALETTES["wood"][0])
        _pg_sprinkle(tile, rng, PALETTES["wood"][1:], 24)
        if "bed" in lower:
            _pg_rect(tile, (2, 3, 13, 14), (93, 138, 212))
            _pg_rect(tile, (3, 4, 12, 7), (240, 239, 214))
        if "chest" in lower:
            _pg_rect(tile, (3, 5, 12, 13), PALETTES["wood"][1])
            _pg_rect(tile, (2, 4, 13, 7), PALETTES["wood"][3])
    elif "signal" in lower or "corrupt" in lower or "special" in lower:
        tile.fill((69, 55, 88))
        _pg_sprinkle(tile, rng, [(116, 83, 164), (82, 185, 98), (39, 31, 50), (198, 240, 108)], 44)
        pygame.draw.line(tile, (198, 240, 108), (0, seed % 16), (15, (seed * 5) % 16))
    else:
        pal = rng.choice(list(PALETTES.values()))
        tile.fill(pal[0])
        _pg_sprinkle(tile, rng, pal[1:], 32)
    return tile


def _looks_empty_or_flat(tile: pygame.Surface) -> bool:
    non_transparent = 0
    colors: set[tuple[int, int, int]] = set()
    w, h = tile.get_size()
    for y in range(h):
        for x in range(w):
            r, g, b, a = tile.get_at((x, y))
            if a < 12:
                continue
            non_transparent += 1
            colors.add((r, g, b))
            if len(colors) > 8:
                return False
    if non_transparent < max(8, (w * h) // 24):
        return True
    return len(colors) <= 2


def _remove_magenta_key(tile: pygame.Surface) -> pygame.Surface:
    out = tile.copy()
    w, h = out.get_size()
    for y in range(h):
        for x in range(w):
            r, g, b, a = out.get_at((x, y))
            if a and r > 210 and g < 90 and b > 210:
                out.set_at((x, y), (0, 0, 0, 0))
    return out


def _load_ai_tiles() -> list[pygame.Surface]:
    for path in AI_TILE_SOURCES:
        if not path.exists():
            continue
        try:
            src = pygame.image.load(str(path)).convert_alpha()
        except pygame.error:
            continue
        # The generated source sheet is arranged on a 32px grid.
        cell = 32
        cols = src.get_width() // cell
        rows = src.get_height() // cell
        cells: list[pygame.Surface] = []
        for row in range(rows):
            for col in range(cols):
                sub = src.subsurface(pygame.Rect(col * cell, row * cell, cell, cell)).copy()
                tile = pygame.transform.scale(sub, (TILE, TILE))
                tile = _remove_magenta_key(tile)
                if _looks_empty_or_flat(tile):
                    continue
                cells.append(tile)
        if len(cells) >= COLS * ROWS:
            return cells[: COLS * ROWS]
        if cells:
            # If the source sheet has fewer unique usable cells than needed, repeat with simple
            # deterministic transforms so we still keep AI-origin pixels as the base.
            out: list[pygame.Surface] = []
            idx = 0
            while len(out) < COLS * ROWS:
                base = cells[idx % len(cells)]
                variant = base.copy()
                if idx % 4 == 1:
                    variant = pygame.transform.flip(base, True, False)
                elif idx % 4 == 2:
                    variant = pygame.transform.flip(base, False, True)
                elif idx % 4 == 3:
                    variant = pygame.transform.rotate(base, 180)
                out.append(variant)
                idx += 1
            return out
    return []


def _pg_draw_person(surface: pygame.Surface, x: int, y: int, facing: str, frame: int, shirt, hair, skin, accent) -> None:
    leg = frame - 1
    _pg_rect(surface, (x + 5, y + 2, x + 10, y + 7), skin)
    _pg_rect(surface, (x + 4, y + 1, x + 11, y + 3), hair)
    if facing == "up":
        _pg_rect(surface, (x + 4, y + 2, x + 11, y + 5), hair)
    elif facing == "left":
        surface.set_at((x + 5, y + 5), (35, 32, 32))
    elif facing == "right":
        surface.set_at((x + 10, y + 5), (35, 32, 32))
    else:
        surface.set_at((x + 6, y + 5), (35, 32, 32))
        surface.set_at((x + 9, y + 5), (35, 32, 32))
    _pg_rect(surface, (x + 4, y + 8, x + 11, y + 12), (35, 32, 32))
    _pg_rect(surface, (x + 5, y + 8, x + 10, y + 12), shirt)
    _pg_rect(surface, (x + 4, y + 9, x + 5, y + 11), accent)
    _pg_rect(surface, (x + 10, y + 9, x + 11, y + 11), accent)
    _pg_rect(surface, (x + 5 + min(0, leg), y + 13, x + 6 + min(0, leg), y + 15), (42, 54, 91))
    _pg_rect(surface, (x + 9 + max(0, leg), y + 13, x + 10 + max(0, leg), y + 15), (42, 54, 91))


def _pg_make_walk(path: Path, shirt, hair, skin, accent) -> None:
    sheet = pygame.Surface((TILE * 3, TILE * 4), pygame.SRCALPHA)
    sheet.fill((0, 0, 0, 0))
    for row, facing in enumerate(("down", "up", "left", "right")):
        for frame in range(3):
            _pg_draw_person(sheet, frame * TILE, row * TILE, facing, frame, shirt, hair, skin, accent)
    pygame.image.save(sheet, str(path))


def main_pygame() -> None:
    pygame.init()
    pygame.display.set_mode((1, 1))
    OUT.mkdir(parents=True, exist_ok=True)
    sheet = pygame.Surface((COLS * TILE, ROWS * TILE), pygame.SRCALPHA)
    sheet.fill((255, 0, 255, 0))
    index: dict[str, list[int]] = {}
    ai_tiles = _load_ai_tiles()
    for i, name in enumerate(_pygame_tile_names()):
        row, col = divmod(i, COLS)
        tile = _pg_make_tile(name, i)
        if i < len(ai_tiles):
            tile.blit(ai_tiles[i], (0, 0))
        sheet.blit(tile, (col * TILE, row * TILE))
        index[name] = [row, col]
    pygame.image.save(sheet, str(OUT / "tileset.png"))
    (OUT / "tileset_index.json").write_text(json.dumps(index, indent=2))
    _pg_make_walk(OUT / "player_walk.png", (65, 126, 216), (69, 45, 35), (224, 170, 120), (241, 205, 86))
    _pg_make_walk(OUT / "npc_base.png", (96, 173, 93), (82, 54, 38), (218, 164, 117), (231, 118, 94))
    _pg_make_walk(OUT / "trainer_sprite.png", (204, 75, 82), (49, 42, 58), (232, 180, 132), (246, 222, 104))
    source_note = "AI source sheet" if ai_tiles else "procedural fallback"
    print(f"Built 1024-tile overworld assets in {OUT} ({source_note})")


def main() -> None:
    main_pygame()


if __name__ == "__main__":
    main()
