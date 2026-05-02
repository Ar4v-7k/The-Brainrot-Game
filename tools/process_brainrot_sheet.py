import argparse
import os
from collections import Counter, deque
from pathlib import Path

import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


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
    return color.r > 180 and color.b > 180 and color.g < 100


def remove_background(surface, threshold=48):
    w, h = surface.get_size()
    refs = border_reference_colors(surface)
    out = surface.copy()
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
        if min(color_distance(px, ref) for ref in refs) <= threshold:
            out.set_at((x, y), pygame.Color(0, 0, 0, 0))
            q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    for x in range(w):
        for y in range(h):
            px = out.get_at((x, y))
            if px.a and (
                is_magenta_key(px)
                or any(is_chroma_key(ref) and color_distance(px, ref) <= 90 for ref in refs)
            ):
                out.set_at((x, y), pygame.Color(0, 0, 0, 0))
    return out


def crop_alpha(surface, pad=22):
    mask = pygame.mask.from_surface(surface, 1)
    rects = mask.get_bounding_rects()
    if not rects:
        return surface
    rect = rects[0]
    x = max(0, rect.x - pad)
    y = max(0, rect.y - pad)
    w = min(surface.get_width() - x, rect.width + pad * 2)
    h = min(surface.get_height() - y, rect.height + pad * 2)
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    out.blit(surface, (0, 0), (x, y, w, h))
    padded = pygame.Surface((out.get_width() + pad * 2, out.get_height() + pad * 2), pygame.SRCALPHA)
    padded.blit(out, (pad, pad))
    return padded


def clean_single_image(input_path, output_path, pad=22):
    surface = pygame.image.load(str(input_path)).convert_alpha()
    clean = crop_alpha(remove_background(surface), pad)
    pygame.image.save(clean, str(output_path))
    return clean


def split_sheet(input_path, keys, outdir, finaldir):
    pygame.init()
    pygame.display.set_mode((1, 1))
    sheet = pygame.image.load(str(input_path)).convert_alpha()
    w, h = sheet.get_size()
    count = len(keys)
    col_w = w // count
    for i, key in enumerate(keys):
        x0 = i * col_w
        x1 = w if i == count - 1 else (i + 1) * col_w
        panel = pygame.Surface((x1 - x0, h), pygame.SRCALPHA)
        panel.blit(sheet, (0, 0), (x0, 0, x1 - x0, h))
        clean = crop_alpha(remove_background(panel))
        pygame.image.save(clean, str(outdir / f"{key}.png"))
        pygame.image.save(clean, str(finaldir / f"{key}.png"))
    pygame.quit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--keys", nargs="+", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--finaldir", required=True)
    args = parser.parse_args()
    split_sheet(Path(args.input), args.keys, Path(args.outdir), Path(args.finaldir))


if __name__ == "__main__":
    main()
