import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pygame

from brainrotmon.game.creatures import CREATURES
from brainrotmon.game.settings import SPRITES_DIR


def content_rect(surface):
    mask = pygame.mask.from_surface(surface, 1)
    rects = mask.get_bounding_rects()
    if not rects:
        return pygame.Rect(0, 0, 0, 0)
    rect = rects[0].copy()
    for other in rects[1:]:
        rect.union_ip(other)
    return rect


def mask_area(surface):
    return pygame.mask.from_surface(surface, 1).count()


def alpha_at(surface, point):
    return surface.get_at(point).a


def load_frames(key, root, frame_count):
    frames = []
    for index in range(frame_count):
        path = root / f"{key}_idle_{index}.png"
        if not path.exists():
            raise FileNotFoundError(path)
        frames.append(pygame.image.load(str(path)).convert_alpha())
    return frames


def validate_key(key, root, frame_count):
    frames = load_frames(key, root, frame_count)
    failures = []
    sizes = {frame.get_size() for frame in frames}
    if len(sizes) != 1:
        failures.append(f"{key}: frame sizes differ {sorted(sizes)}")
        return failures, frames

    w, h = frames[0].get_size()
    corners = ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))
    for index, frame in enumerate(frames):
        if any(alpha_at(frame, point) > 8 for point in corners):
            failures.append(f"{key}: frame {index} has nontransparent corner")

    rects = [content_rect(frame) for frame in frames]
    bottoms = [rect.bottom for rect in rects]
    centers = [rect.centerx for rect in rects]
    areas = [mask_area(frame) for frame in frames]
    if max(bottoms) - min(bottoms) > 2:
        failures.append(f"{key}: bottom anchor drifts {bottoms}")
    if max(centers) - min(centers) > 34:
        failures.append(f"{key}: center drifts {centers}")
    if min(areas) <= 0:
        failures.append(f"{key}: empty frame area {areas}")
    else:
        variance = (max(areas) - min(areas)) / min(areas)
        if variance > 0.38:
            failures.append(f"{key}: silhouette area variance {variance:.2f} {areas}")
    return failures, frames


def draw_contact_sheet(rows, out_path):
    cell_w = 132
    cell_h = 116
    label_w = 190
    pad = 12
    frame_count = max((len(frames) for _, frames in rows), default=0)
    width = label_w + cell_w * frame_count + pad * 2
    height = pad * 2 + cell_h * len(rows)
    sheet = pygame.Surface((width, height), pygame.SRCALPHA)
    sheet.fill((18, 22, 30, 255))
    font = pygame.font.SysFont("couriernew", 16, bold=True)
    tiny = pygame.font.SysFont("couriernew", 12)
    for row, (key, frames) in enumerate(rows):
        y = pad + row * cell_h
        name = CREATURES[key].name
        text = font.render(name, True, (235, 240, 248))
        sheet.blit(text, (pad, y + 22))
        sub = tiny.render(key, True, (145, 165, 190))
        sheet.blit(sub, (pad, y + 44))
        for index, frame in enumerate(frames):
            cell = pygame.Rect(label_w + index * cell_w, y, cell_w - 8, cell_h - 8)
            pygame.draw.rect(sheet, (28, 38, 52), cell)
            pygame.draw.rect(sheet, (67, 92, 120), cell, 1)
            scale = min((cell.width - 14) / frame.get_width(), (cell.height - 14) / frame.get_height())
            size = (max(1, int(frame.get_width() * scale)), max(1, int(frame.get_height() * scale)))
            preview = pygame.transform.scale(frame, size)
            rect = preview.get_rect(midbottom=(cell.centerx, cell.bottom - 7))
            sheet.blit(preview, rect.topleft)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet, str(out_path))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(SPRITES_DIR / "creature_anim"))
    parser.add_argument("--contact-sheet")
    parser.add_argument("--keys", help="Comma-separated creature keys. Defaults to all.")
    parser.add_argument("--frames", type=int, default=4)
    args = parser.parse_args()

    pygame.init()
    pygame.display.set_mode((1, 1))
    root = Path(args.root)
    rows = []
    failures = []
    keys = list(CREATURES)
    if args.keys:
        keys = [key.strip() for key in args.keys.split(",") if key.strip()]
    for key in keys:
        key_failures, frames = validate_key(key, root, args.frames)
        failures.extend(key_failures)
        rows.append((key, frames))
    if args.contact_sheet:
        draw_contact_sheet(rows, Path(args.contact_sheet))
    pygame.quit()

    if failures:
        print("\n".join(failures))
        raise SystemExit(1)
    print(f"idle_art_ok creatures={len(rows)}")


if __name__ == "__main__":
    main()
