import argparse
import os
from collections import Counter, deque
from pathlib import Path

import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


def content_rect(surface):
    mask = pygame.mask.from_surface(surface, 1)
    rects = mask.get_bounding_rects()
    if not rects:
        return pygame.Rect(0, 0, surface.get_width(), surface.get_height())
    rect = rects[0].copy()
    for other in rects[1:]:
        rect.union_ip(other)
    return rect


def slice_bounds(sheet, frames):
    w, h = sheet.get_size()
    cell_w = w // frames
    occupancy = []
    for x in range(w):
        count = 0
        for y in range(h):
            if sheet.get_at((x, y)).a:
                count += 1
        occupancy.append(count)
    bounds = [0]
    search = max(16, cell_w // 7)
    for idx in range(1, frames):
        expected = idx * cell_w
        lo = max(bounds[-1] + 1, expected - search)
        hi = min(w - 1, expected + search)
        if lo >= hi:
            bounds.append(expected)
            continue
        band = occupancy[lo : hi + 1]
        minimum = min(band)
        candidates = [lo + offset for offset, value in enumerate(band) if value == minimum]
        best = min(candidates, key=lambda x: abs(x - expected))
        bounds.append(best)
    bounds.append(w)
    return bounds


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


def remove_flat_bg(surface, key_colors, threshold=38):
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
            for kr, kg, kb in key_colors:
                key = pygame.Color(kr, kg, kb)
                if is_chroma_key(key) and color_distance(px, key) <= threshold:
                    out.set_at((x, y), pygame.Color(0, 0, 0, 0))
                    break
    return out


def remove_small_islands(surface):
    mask = pygame.mask.from_surface(surface, 1)
    components = mask.connected_components()
    if not components:
        return surface
    largest = max(component.count() for component in components)
    minimum = max(24, int(largest * 0.008))
    out = surface.copy()
    for component in components:
        if component.count() >= minimum:
            continue
        for rect in component.get_bounding_rects():
            for x in range(rect.x, rect.right):
                for y in range(rect.y, rect.bottom):
                    if component.get_at((x, y)):
                        out.set_at((x, y), pygame.Color(0, 0, 0, 0))
    return out


def remove_edge_leaks(surface):
    mask = pygame.mask.from_surface(surface, 1)
    components = mask.connected_components()
    if not components:
        return surface
    largest = max(component.count() for component in components)
    out = surface.copy()
    w, h = surface.get_size()
    for component in components:
        rects = component.get_bounding_rects()
        rect = rects[0].copy()
        for other in rects[1:]:
            rect.union_ip(other)
        touches_edge = rect.left <= 0 or rect.top <= 0 or rect.right >= w or rect.bottom >= h
        if not touches_edge or component.count() >= int(largest * 0.22):
            continue
        for rect in rects:
            for x in range(rect.x, rect.right):
                for y in range(rect.y, rect.bottom):
                    if component.get_at((x, y)):
                        out.set_at((x, y), pygame.Color(0, 0, 0, 0))
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


def process(input_path, key, phase, outdir, frames=6):
    pygame.init()
    pygame.display.set_mode((1, 1))
    img = pygame.image.load(str(input_path)).convert_alpha()
    w, h = img.get_size()
    clean_sheet = remove_flat_bg(img, [(255, 0, 255), (0, 255, 0)], threshold=42)
    bounds = slice_bounds(clean_sheet, frames)
    raw = []
    for i in range(frames):
        x0 = bounds[i]
        x1 = bounds[i + 1]
        frame = pygame.Surface((x1 - x0, h), pygame.SRCALPHA)
        frame.blit(img, (0, 0), (x0, 0, x1 - x0, h))
        clean = remove_flat_bg(frame, [(255, 0, 255), (0, 255, 0)], threshold=42)
        clean = remove_small_islands(clean)
        clean = remove_edge_leaks(clean)
        clean = fill_small_holes(clean)
        raw.append(clean)

    rects = [content_rect(frame) for frame in raw]
    frame_w = max(x1 - x0 for x0, x1 in zip(bounds, bounds[1:]))
    target_mid_x = frame_w // 2
    target_bottom = max(rect.bottom for rect in rects)
    normalized = []
    margin = 24
    canvas_w = frame_w + margin * 2
    canvas_h = h + margin * 2
    for frame, rect in zip(raw, rects):
        canvas = pygame.Surface((canvas_w, canvas_h), pygame.SRCALPHA)
        dx = margin + target_mid_x - rect.centerx
        dy = margin + target_bottom - rect.bottom
        canvas.blit(frame, (dx, dy))
        normalized.append(canvas)

    unions = [content_rect(frame) for frame in normalized]
    min_x = min(r.x for r in unions)
    min_y = min(r.y for r in unions)
    max_r = max(r.right for r in unions)
    max_b = max(r.bottom for r in unions)
    pad = 8
    crop_rect = pygame.Rect(
        max(0, min_x - pad),
        max(0, min_y - pad),
        min(canvas_w - max(0, min_x - pad), max_r - min_x + pad * 2),
        min(canvas_h - max(0, min_y - pad), max_b - min_y + pad * 2),
    )

    outdir.mkdir(parents=True, exist_ok=True)
    for old in outdir.glob(f"{key}_{phase}_*.png"):
        old.unlink()
    for i, frame in enumerate(normalized):
        out = pygame.Surface((crop_rect.width, crop_rect.height), pygame.SRCALPHA)
        out.blit(frame, (0, 0), crop_rect)
        pygame.image.save(out, str(outdir / f"{key}_{phase}_{i}.png"))
    pygame.quit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--phase", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--frames", type=int, default=6)
    args = parser.parse_args()
    process(Path(args.input), args.key, args.phase, Path(args.outdir), args.frames)


if __name__ == "__main__":
    main()
