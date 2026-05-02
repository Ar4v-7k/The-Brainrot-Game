import argparse
import os
from pathlib import Path

import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


KEY_COLORS = (
    (255, 0, 255),
    (0, 255, 0),
    (245, 245, 245),
    (255, 255, 255),
)


def remove_flat_bg(surface, threshold=42):
    out = surface.copy()
    w, h = out.get_size()
    for x in range(w):
        for y in range(h):
            px = out.get_at((x, y))
            if px.r > 165 and px.b > 165 and px.g < 135 and abs(px.r - px.b) < 100:
                out.set_at((x, y), pygame.Color(0, 0, 0, 0))
                continue
            for kr, kg, kb in KEY_COLORS:
                if abs(px.r - kr) + abs(px.g - kg) + abs(px.b - kb) <= threshold:
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


def crop_to_rect(surface, rect):
    out = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    out.blit(surface, (0, 0), rect)
    return out


def process(input_path, keys, outdir, cols=4, rows=None, pad=10):
    rows = rows or len(keys)
    if rows != len(keys):
        raise ValueError("rows must match number of keys")

    pygame.init()
    pygame.display.set_mode((1, 1))
    img = pygame.image.load(str(input_path)).convert_alpha()
    cell_w = img.get_width() // cols
    cell_h = img.get_height() // rows

    outdir.mkdir(parents=True, exist_ok=True)
    for row, key in enumerate(keys):
        frames = []
        rect = None
        for col in range(cols):
            x0 = col * cell_w
            y0 = row * cell_h
            x1 = img.get_width() if col == cols - 1 else (col + 1) * cell_w
            y1 = img.get_height() if row == rows - 1 else (row + 1) * cell_h
            frame = pygame.Surface((x1 - x0, y1 - y0), pygame.SRCALPHA)
            frame.blit(img, (0, 0), (x0, y0, x1 - x0, y1 - y0))
            frame = remove_flat_bg(frame)
            frames.append(frame)
            frame_rect = content_rect(frame)
            rect = frame_rect if rect is None else rect.union(frame_rect)

        rect.x = max(0, rect.x - pad)
        rect.y = max(0, rect.y - pad)
        rect.width = min(cell_w - rect.x, rect.width + pad * 2)
        rect.height = min(cell_h - rect.y, rect.height + pad * 2)

        for i, frame in enumerate(frames):
            cropped = crop_to_rect(frame, rect)
            pygame.image.save(cropped, str(outdir / f"{key}_idle_{i}.png"))
    pygame.quit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--keys", required=True, help="Comma-separated creature keys, one row each.")
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--cols", type=int, default=4)
    args = parser.parse_args()
    keys = [key.strip() for key in args.keys.split(",") if key.strip()]
    process(Path(args.input), keys, Path(args.outdir), cols=args.cols)


if __name__ == "__main__":
    main()
