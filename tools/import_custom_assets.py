import argparse
import os
import shutil
from collections import Counter, deque
from pathlib import Path

import pygame

from process_idle_strip import process as process_idle_strip

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

KEY_COLORS = (
    (255, 0, 255),
    (0, 255, 0),
)


def color_distance(a, b):
    return abs(a.r - b.r) + abs(a.g - b.g) + abs(a.b - b.b)


def border_reference_colors(surface):
    w, h = surface.get_size()
    samples = []
    for x in range(w):
        samples.append(surface.get_at((x, 0)))
        samples.append(surface.get_at((x, h - 1)))
    for y in range(h):
        samples.append(surface.get_at((0, y)))
        samples.append(surface.get_at((w - 1, y)))
    top = Counter((c.r, c.g, c.b) for c in samples).most_common(8)
    return [pygame.Color(r, g, b) for (r, g, b), _ in top]


def is_chroma_key(color):
    channels = (color.r, color.g, color.b)
    return max(channels) > 150 and max(channels) - sorted(channels)[1] > 70


def is_magenta_key(color):
    return color.r > 180 and color.b > 180 and color.g < 120


def remove_flat_bg(surface, threshold=82):
    out = surface.copy()
    w, h = out.get_size()
    refs = border_reference_colors(surface)
    visited = [[False] * h for _ in range(w)]
    q = deque()
    for x in range(w):
        q.append((x, 0))
        q.append((x, h - 1))
    for y in range(h):
        q.append((0, y))
        q.append((w - 1, y))
    while q:
        x, y = q.popleft()
        if x < 0 or y < 0 or x >= w or y >= h or visited[x][y]:
            continue
        visited[x][y] = True
        px = out.get_at((x, y))
        if px.a == 0:
            continue
        if min(color_distance(px, ref) for ref in refs) <= threshold or is_magenta_key(px):
            out.set_at((x, y), pygame.Color(0, 0, 0, 0))
            q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    for x in range(w):
        for y in range(h):
            px = out.get_at((x, y))
            if px.a == 0:
                continue
            if is_magenta_key(px):
                out.set_at((x, y), pygame.Color(0, 0, 0, 0))
                continue
            for kr, kg, kb in KEY_COLORS:
                key = pygame.Color(kr, kg, kb)
                if is_chroma_key(key) and color_distance(px, key) <= threshold:
                    out.set_at((x, y), pygame.Color(0, 0, 0, 0))
                    break
    return out


def content_rect(surface):
    mask = pygame.mask.from_surface(surface, 1)
    rects = mask.get_bounding_rects()
    if not rects:
        return pygame.Rect(0, 0, surface.get_width(), surface.get_height())
    rect = rects[0].copy()
    for other in rects[1:]:
        rect.union_ip(other)
    return rect


def crop_surface(surface, pad=10):
    rect = content_rect(surface)
    rect.x = max(0, rect.x - pad)
    rect.y = max(0, rect.y - pad)
    rect.width = min(surface.get_width() - rect.x, rect.width + pad * 2)
    rect.height = min(surface.get_height() - rect.y, rect.height + pad * 2)
    out = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    out.blit(surface, (0, 0), rect)
    return out


def fill_small_holes(surface, max_area=220):
    w, h = surface.get_size()
    seen = [[False] * h for _ in range(w)]
    out = surface.copy()
    for x in range(w):
        for y in range(h):
            if seen[x][y] or out.get_at((x, y)).a != 0:
                continue
            q = deque([(x, y)])
            seen[x][y] = True
            pts = []
            touch = False
            neighbors = Counter()
            while q:
                cx, cy = q.popleft()
                pts.append((cx, cy))
                if cx == 0 or cy == 0 or cx == w - 1 or cy == h - 1:
                    touch = True
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if not (0 <= nx < w and 0 <= ny < h):
                        continue
                    if out.get_at((nx, ny)).a == 0:
                        if not seen[nx][ny]:
                            seen[nx][ny] = True
                            q.append((nx, ny))
                    else:
                        c = out.get_at((nx, ny))
                        neighbors[(c.r, c.g, c.b, c.a)] += 1
            if touch or len(pts) > max_area or not neighbors:
                continue
            fill = max(neighbors.items(), key=lambda item: item[1])[0]
            color = pygame.Color(*fill)
            for px, py in pts:
                out.set_at((px, py), color)
    return out


def extract_components(sheet_path: Path):
    img = pygame.image.load(str(sheet_path)).convert_alpha()
    clean = remove_flat_bg(img)
    mask = pygame.mask.from_surface(clean, 1)
    components = mask.connected_components()
    boxes = []
    for comp in components:
        rects = comp.get_bounding_rects()
        rect = rects[0].copy()
        for other in rects[1:]:
            rect.union_ip(other)
        if rect.width * rect.height < 400:
            continue
        boxes.append(rect)
    boxes.sort(key=lambda r: (r.y, r.x))
    pieces = []
    for rect in boxes:
        surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        surf.blit(clean, (0, 0), rect)
        pieces.append(crop_surface(surf, pad=4))
    return pieces


def save_scaled(surface, out_path: Path, size=None):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if size:
        surface = pygame.transform.scale(surface, size)
    pygame.image.save(surface, str(out_path))


def fit_to_canvas(image_path: Path, out_path: Path, size):
    src = pygame.image.load(str(image_path)).convert_alpha()
    src_w, src_h = src.get_size()
    target_w, target_h = size
    src_ratio = src_w / src_h
    target_ratio = target_w / target_h
    if src_ratio > target_ratio:
        crop_w = int(src_h * target_ratio)
        rect = pygame.Rect((src_w - crop_w) // 2, 0, crop_w, src_h)
    else:
        crop_h = int(src_w / target_ratio)
        rect = pygame.Rect(0, (src_h - crop_h) // 2, src_w, crop_h)
    cropped = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    cropped.blit(src, (0, 0), rect)
    scaled = pygame.transform.scale(cropped, size)
    save_scaled(scaled, out_path)


def process_portrait(input_path: Path, raw_out: Path, live_out: Path):
    raw_out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(input_path, raw_out)
    src = pygame.image.load(str(input_path)).convert_alpha()
    clean = crop_surface(fill_small_holes(remove_flat_bg(src)), pad=14)
    save_scaled(clean, live_out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--ui-sheet", required=True)
    parser.add_argument("--battle-bg", required=True)
    parser.add_argument("--title-bg", required=True)
    parser.add_argument("--portrait", action="append", default=[], help="key=path")
    parser.add_argument("--idle", action="append", default=[], help="key=path")
    args = parser.parse_args()

    root = Path(args.root)
    assets_dir = root / "assets"
    runtime_dir = assets_dir / "sprites" / "runtime_ui"
    source_dir = assets_dir / "source_sheets" / "custom_v1"
    creature_dir = assets_dir / "sprites" / "creatures"
    anim_dir = assets_dir / "sprites" / "creature_anim"

    pygame.init()
    pygame.display.set_mode((1, 1))

    ui_sheet = Path(args.ui_sheet)
    (source_dir / "runtime_ui").mkdir(parents=True, exist_ok=True)
    shutil.copy2(ui_sheet, source_dir / "runtime_ui" / "ui_sheet_v1.png")
    pieces = extract_components(ui_sheet)
    if len(pieces) < 6:
        raise RuntimeError(f"Expected 6 UI components, got {len(pieces)}")
    names = [
        "title_card.png",
        "command_box.png",
        "stat_box.png",
        "slot_panel.png",
        "reward_card.png",
        "menu_button.png",
    ]
    sizes = {
        "title_card.png": (348, 58),
        "command_box.png": (372, 64),
        "stat_box.png": (142, 52),
        "slot_panel.png": (352, 44),
        "reward_card.png": (100, 124),
        "menu_button.png": (72, 18),
    }
    for piece, name in zip(pieces, names):
        save_scaled(piece, runtime_dir / name, sizes[name])

    fit_to_canvas(Path(args.battle_bg), runtime_dir / "battle_bg.png", (384, 216))
    fit_to_canvas(Path(args.title_bg), runtime_dir / "title_bg.png", (384, 216))
    shutil.copy2(args.battle_bg, source_dir / "runtime_ui" / "battle_bg_src.png")
    shutil.copy2(args.title_bg, source_dir / "runtime_ui" / "title_bg_src.png")

    for item in args.portrait:
        key, value = item.split("=", 1)
        process_portrait(
            Path(value),
            source_dir / "portraits" / f"{key}.png",
            creature_dir / f"{key}.png",
        )

    for item in args.idle:
        key, value = item.split("=", 1)
        src = Path(value)
        raw_out = source_dir / "idles" / f"{key}.png"
        raw_out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, raw_out)
        process_idle_strip(src, key, anim_dir, frames=6)

    pygame.quit()


if __name__ == "__main__":
    main()
