from __future__ import annotations

import math
import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame


ROOT = Path(__file__).resolve().parents[1]
MOVE_FX = ROOT / "assets" / "sprites" / "move_fx"
SIZE = 64
FRAMES = 6

BORDER = (17, 14, 24)
NOODLE = (255, 210, 96)
NOODLE_HI = (255, 238, 170)
SAUCE = (219, 69, 55)
SAUCE_HI = (255, 132, 90)
HERB = (86, 186, 77)
MEAT = (131, 81, 56)
WOOD = (145, 95, 60)
WOOD_HI = (201, 152, 104)
DRUM_RED = (221, 74, 61)
BEAT = (255, 201, 84)
FOAM = (248, 244, 232)
FOAM_HI = (255, 255, 255)
COFFEE = (161, 110, 79)
COFFEE_DARK = (106, 72, 52)
LATTE = (216, 176, 122)
TAN = (207, 168, 120)
TEAL = (121, 227, 219)
PINK = (255, 175, 219)
FIRE = (248, 126, 56)


def canvas() -> pygame.Surface:
    return pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)


def save(surface: pygame.Surface, path: Path) -> None:
    pygame.image.save(surface, str(path))


def save_phase(name: str, phase: str, frames: list[pygame.Surface]) -> None:
    for old in MOVE_FX.glob(f"{name}_{phase}_*.png"):
        old.unlink()
    for index, frame in enumerate(frames):
        save(frame, MOVE_FX / f"{name}_{phase}_{index}.png")


def line(surface: pygame.Surface, color, start, end, width: int = 2, border: bool = True) -> None:
    if border:
        pygame.draw.line(surface, BORDER, start, end, width + 2)
    pygame.draw.line(surface, color, start, end, width)


def circle(surface: pygame.Surface, color, center, radius: int, border: bool = True, width: int = 0) -> None:
    if border:
        pygame.draw.circle(surface, BORDER, center, radius + (1 if width == 0 else 0), 0 if width == 0 else width + 2)
    pygame.draw.circle(surface, color, center, radius, width)


def poly(surface: pygame.Surface, color, points, border: bool = True) -> None:
    if border:
        pygame.draw.polygon(surface, BORDER, points)
    pygame.draw.polygon(surface, color, points)


def strand(surface: pygame.Surface, points, color=NOODLE, hi=NOODLE_HI, width: int = 4) -> None:
    pygame.draw.lines(surface, BORDER, False, points, width + 2)
    pygame.draw.lines(surface, color, False, points, width)
    pygame.draw.lines(surface, hi, False, [(x, y - 1) for x, y in points], max(1, width - 2))


def burst(surface: pygame.Surface, center, radius: int, color, accent=None, spokes: int = 8) -> None:
    cx, cy = center
    for idx in range(spokes):
        ang = math.tau * idx / spokes
        dx = int(math.cos(ang) * radius)
        dy = int(math.sin(ang) * radius)
        line(surface, color, center, (cx + dx, cy + dy), 2)
    if accent:
        circle(surface, accent, center, max(3, radius // 2), width=1)


def blob(surface: pygame.Surface, center, rx: int, ry: int, color, accent=None) -> None:
    rect = pygame.Rect(0, 0, rx * 2, ry * 2)
    rect.center = center
    pygame.draw.ellipse(surface, BORDER, rect.inflate(2, 2))
    pygame.draw.ellipse(surface, color, rect)
    if accent:
        pygame.draw.ellipse(surface, accent, rect.inflate(-rx // 2, -ry // 2), 1)


def herb_bits(surface: pygame.Surface, points) -> None:
    for x, y in points:
        line(surface, HERB, (x - 2, y), (x + 2, y - 1), 1)
        line(surface, HERB, (x, y - 2), (x + 1, y + 2), 1)


def ring(surface: pygame.Surface, center, radius: int, color, width: int = 2) -> None:
    pygame.draw.circle(surface, BORDER, center, radius, width + 2)
    pygame.draw.circle(surface, color, center, radius, width)


def note(surface: pygame.Surface, center, color=BEAT) -> None:
    x, y = center
    circle(surface, color, (x, y + 5), 4)
    line(surface, color, (x + 3, y + 4), (x + 3, y - 8), 2)
    line(surface, color, (x + 3, y - 8), (x + 11, y - 5), 2)


def foam_swirl(surface: pygame.Surface, center, radius: int, color=FOAM) -> None:
    cx, cy = center
    pts = []
    for step in range(10):
        ang = 0.6 + step * 0.5
        r = radius - step
        pts.append((cx + int(math.cos(ang) * r), cy + int(math.sin(ang) * r)))
    strand(surface, pts, color, FOAM_HI, 3)


def mallet(surface: pygame.Surface, center, angle: float) -> None:
    cx, cy = center
    ex = cx + int(math.cos(angle) * 18)
    ey = cy + int(math.sin(angle) * 18)
    line(surface, WOOD_HI, (cx, cy), (ex, ey), 4)
    hx = ex + int(math.cos(angle) * 4)
    hy = ey + int(math.sin(angle) * 4)
    blob(surface, (hx, hy), 5, 4, FOAM, WOOD_HI)


def coffee_ribbon(surface: pygame.Surface, points, color=COFFEE, hi=LATTE, width: int = 4) -> None:
    strand(surface, points, color, hi, width)


def sauce_flame(surface: pygame.Surface, center, scale: float) -> None:
    cx, cy = center
    pts = [
        (cx, int(cy - 18 * scale)),
        (int(cx + 9 * scale), int(cy - 4 * scale)),
        (int(cx + 13 * scale), int(cy + 8 * scale)),
        (cx, int(cy + 18 * scale)),
        (int(cx - 11 * scale), int(cy + 7 * scale)),
        (int(cx - 8 * scale), int(cy - 6 * scale)),
    ]
    poly(surface, FIRE, pts)
    inner = [
        (cx, int(cy - 11 * scale)),
        (int(cx + 5 * scale), int(cy - 2 * scale)),
        (int(cx + 7 * scale), int(cy + 6 * scale)),
        (cx, int(cy + 11 * scale)),
        (int(cx - 6 * scale), int(cy + 5 * scale)),
        (int(cx - 4 * scale), int(cy - 4 * scale)),
    ]
    poly(surface, BEAT, inner, border=False)


def stomp_cracks(surface: pygame.Surface, center, length: int, color=WOOD_HI) -> None:
    cx, cy = center
    for dx, dy in ((-length, 4), (-length // 2, 8), (length, 5), (length // 2, 9)):
        line(surface, color, center, (cx + dx, cy + dy), 2)


def projectile_arc(x0: int, y0: int, x1: int, y1: int, p: float, lift: int) -> tuple[int, int]:
    x = x0 + (x1 - x0) * p
    y = y0 + (y1 - y0) * p - math.sin(p * math.pi) * lift
    return int(x), int(y)


def make_fork_flick():
    cast, impact = [], []
    for frame in range(FRAMES):
        p = frame / (FRAMES - 1)
        s = canvas()
        shaft_x = 13 + int(26 * p)
        line(s, NOODLE_HI, (10, 36), (shaft_x, 30), 4)
        for dy in (-6, -1, 4):
            line(s, FOAM, (shaft_x, 30 + dy), (shaft_x + 10, 27 + dy), 2)
        burst(s, (shaft_x + 12, 30), 4 + frame, BEAT, FOAM, 6)
        cast.append(s)

        h = canvas()
        burst(h, (32, 30), 9 + frame * 2, FOAM, BEAT, 8)
        for dy in (-6, -1, 4):
            line(h, NOODLE_HI, (26, 30 + dy), (38, 28 + dy), 2)
        impact.append(h)
    return cast, [], impact


def make_sauce_splash():
    cast, proj, impact = [], [], []
    for frame in range(FRAMES):
        p = frame / (FRAMES - 1)
        s = canvas()
        centers = [(16 + frame * 2, 38 - frame), (26 + frame * 2, 26), (36 + frame * 2, 38 + frame % 2)]
        for center in centers:
            blob(s, center, 7, 5, SAUCE, SAUCE_HI)
        herb_bits(s, [(22, 22), (34, 31), (28, 40)])
        cast.append(s)

        pr = canvas()
        cx, cy = projectile_arc(14, 38, 50, 20, p, 14)
        blob(pr, (cx, cy), 10, 7, SAUCE, SAUCE_HI)
        strand(pr, [(cx - 8, cy + 1), (cx - 2, cy - 4), (cx + 5, cy + 2)], NOODLE, NOODLE_HI, 3)
        herb_bits(pr, [(cx - 2, cy - 2), (cx + 4, cy + 1)])
        proj.append(pr)

        h = canvas()
        for center in ((20, 22), (32, 18), (42, 26), (18, 34), (32, 38), (45, 35)):
            blob(h, center, 6, 4, SAUCE, SAUCE_HI)
        strand(h, [(16, 30), (24, 28), (33, 34), (46, 30)], NOODLE, NOODLE_HI, 3)
        burst(h, (32, 29), 10 + frame * 2, SAUCE_HI, BEAT, 7)
        impact.append(h)
    return cast, proj, impact


def make_al_dente_slam():
    cast, impact = [], []
    for frame in range(FRAMES):
        p = frame / (FRAMES - 1)
        s = canvas()
        base_y = 42 - int(math.sin(p * math.pi) * 10)
        for idx, x in enumerate((15, 24, 34, 44)):
            h = 16 + idx * 3 + frame
            pygame.draw.rect(s, BORDER, (x, base_y - h, 6, h), border_radius=2)
            pygame.draw.rect(s, NOODLE, (x + 1, base_y - h + 1, 4, h - 2), border_radius=2)
        ring(s, (32, 46), 6 + frame, BEAT, 2)
        cast.append(s)

        h = canvas()
        for idx, x in enumerate((16, 24, 32, 40, 48)):
            line(h, TAN, (x, 38), (x + (-4 if x < 32 else 4), 52), 2)
        burst(h, (32, 37), 12 + frame * 2, NOODLE_HI, BEAT, 8)
        ring(h, (32, 42), 8 + frame * 2, TAN, 2)
        impact.append(h)
    return cast, [], impact


def make_meatball_panic():
    cast, proj, impact = [], [], []
    for frame in range(FRAMES):
        p = frame / (FRAMES - 1)
        s = canvas()
        orbit = [(24 + int(math.cos(a) * 10), 26 + int(math.sin(a) * 7)) for a in (p * math.tau, p * math.tau + 2.1, p * math.tau + 4.2)]
        for cx, cy in orbit:
            blob(s, (cx, cy), 7, 6, MEAT, SAUCE)
            circle(s, SAUCE, (cx - 1, cy - 1), 2, border=False)
        cast.append(s)

        pr = canvas()
        cx, cy = projectile_arc(14, 30, 50, 24, p, 10)
        blob(pr, (cx, cy), 9, 8, MEAT, SAUCE)
        for off in (-7, 0, 7):
            circle(pr, SAUCE_HI, (cx - off // 2, cy + off // 5), 1, border=False)
        ring(pr, (cx, cy), 6 + frame % 2, DRUM_RED, 1)
        proj.append(pr)

        h = canvas()
        blob(h, (32, 30), 12, 10, MEAT, SAUCE)
        burst(h, (32, 30), 10 + frame * 2, SAUCE_HI, DRUM_RED, 7)
        for center in ((18, 22), (46, 24), (18, 40), (47, 39)):
            circle(h, SAUCE, center, 3 + frame // 2)
        impact.append(h)
    return cast, proj, impact


def make_drum_knock():
    cast, impact = [], []
    for frame in range(FRAMES):
        angle = -1.2 + frame * 0.34
        s = canvas()
        mallet(s, (18, 40), angle)
        burst(s, (36, 22), 4 + frame, BEAT, WOOD_HI, 5)
        cast.append(s)

        h = canvas()
        for center in ((24, 26), (34, 20), (42, 30), (24, 38)):
            pygame.draw.rect(h, BORDER, (*center, 8, 5))
            pygame.draw.rect(h, WOOD, (center[0] + 1, center[1] + 1, 6, 3))
        burst(h, (32, 30), 10 + frame * 2, WOOD_HI, BEAT, 8)
        impact.append(h)
    return cast, [], impact


def make_sahur_burst():
    cast, proj, impact = [], [], []
    for frame in range(FRAMES):
        s = canvas()
        ring(s, (32, 32), 7 + frame * 3, BEAT, 2)
        ring(s, (32, 32), 3 + frame * 2, DRUM_RED, 1)
        note(s, (20, 22))
        note(s, (42, 24))
        cast.append(s)

        pr = canvas()
        x = 10 + frame * 8
        ring(pr, (x, 30), 8 + frame, BEAT, 2)
        ring(pr, (x, 30), 4 + frame, DRUM_RED, 1)
        note(pr, (x + 8, 18))
        proj.append(pr)

        h = canvas()
        burst(h, (32, 30), 12 + frame * 2, BEAT, DRUM_RED, 10)
        ring(h, (32, 30), 8 + frame * 2, FOAM, 1)
        impact.append(h)
    return cast, proj, impact


def make_tung_roll():
    cast, proj, impact = [], [], []
    for frame in range(FRAMES):
        s = canvas()
        ring(s, (32, 32), 10 + frame, WOOD, 4)
        ring(s, (32, 32), 5 + frame, WOOD_HI, 1)
        line(s, DRUM_RED, (24, 20), (40, 44), 2)
        line(s, BEAT, (40, 20), (24, 44), 2)
        cast.append(s)

        pr = canvas()
        x = 12 + frame * 8
        ring(pr, (x, 34), 10, WOOD, 4)
        ring(pr, (x, 34), 5, WOOD_HI, 1)
        line(pr, DRUM_RED, (x - 5, 27), (x + 5, 41), 2)
        line(pr, BEAT, (x + 5, 27), (x - 5, 41), 2)
        stomp_cracks(pr, (x, 45), 7, WOOD_HI)
        proj.append(pr)

        h = canvas()
        burst(h, (32, 36), 12 + frame * 2, WOOD_HI, BEAT, 8)
        stomp_cracks(h, (32, 39), 14 + frame * 2, WOOD_HI)
        impact.append(h)
    return cast, proj, impact


def make_midnight_march():
    cast, proj, impact = [], [], []
    for frame in range(FRAMES):
        s = canvas()
        for idx in range(3):
            x = 10 + frame * 3 + idx * 14
            pygame.draw.ellipse(s, BORDER, (x, 34 - idx % 2 * 4, 12, 6))
            pygame.draw.ellipse(s, BEAT, (x + 1, 35 - idx % 2 * 4, 10, 4))
            note(s, (x + 6, 20 + idx * 2), DRUM_RED)
        cast.append(s)

        pr = canvas()
        for idx in range(3):
            x = 8 + frame * 6 + idx * 9
            pygame.draw.ellipse(pr, BORDER, (x, 35 - idx % 2 * 3, 12, 5))
            pygame.draw.ellipse(pr, BEAT, (x + 1, 36 - idx % 2 * 3, 10, 3))
        burst(pr, (28 + frame * 2, 30), 5 + frame, DRUM_RED, BEAT, 5)
        proj.append(pr)

        h = canvas()
        stomp_cracks(h, (32, 38), 16 + frame * 2, BEAT)
        burst(h, (32, 32), 10 + frame * 2, DRUM_RED, BEAT, 8)
        impact.append(h)
    return cast, proj, impact


def make_pirouette_pour():
    cast, proj, impact = [], [], []
    for frame in range(FRAMES):
        ang = frame / FRAMES * math.tau
        s = canvas()
        ring(s, (32, 32), 8 + frame * 2, LATTE, 2)
        for off in (0, 2.1, 4.2):
            x = 32 + int(math.cos(ang + off) * 11)
            y = 32 + int(math.sin(ang + off) * 11)
            circle(s, FOAM, (x, y), 3)
        cast.append(s)

        pr = canvas()
        pts = []
        for step in range(5):
            p = frame / (FRAMES - 1) * 0.8 + step * 0.05
            x, y = projectile_arc(10, 38, 54, 18, min(1.0, p), 12)
            pts.append((x, y))
        coffee_ribbon(pr, pts, COFFEE, LATTE, 4)
        circle(pr, FOAM, pts[-1], 3)
        proj.append(pr)

        h = canvas()
        for off in (0, 1.7, 3.4, 5.1):
            x = 32 + int(math.cos(off) * (7 + frame))
            y = 30 + int(math.sin(off) * (7 + frame))
            circle(h, FOAM, (x, y), 3)
        burst(h, (32, 30), 8 + frame * 2, LATTE, FOAM, 8)
        impact.append(h)
    return cast, proj, impact


def make_foam_ribbon():
    cast, proj, impact = [], [], []
    for frame in range(FRAMES):
        s = canvas()
        pts = [(10, 38), (18, 25 - frame), (28, 35), (40, 22 + frame), (52, 30)]
        coffee_ribbon(s, pts, FOAM, TEAL, 4)
        for point in pts[1::2]:
            circle(s, FOAM_HI, point, 2, border=False)
        cast.append(s)

        pr = canvas()
        pts = []
        for step in range(7):
            x = 8 + frame * 6 + step * 7
            y = 32 + int(math.sin((step + frame) * 0.9) * 10)
            pts.append((x, y))
        coffee_ribbon(pr, pts, FOAM, TEAL, 4)
        proj.append(pr)

        h = canvas()
        for ang in range(0, 360, 60):
            rad = math.radians(ang + frame * 10)
            x = 32 + int(math.cos(rad) * 10)
            y = 30 + int(math.sin(rad) * 10)
            coffee_ribbon(h, [(32, 30), (x, y)], FOAM, TEAL, 3)
        burst(h, (32, 30), 8 + frame * 2, TEAL, FOAM, 6)
        impact.append(h)
    return cast, proj, impact


def make_arabesque_roast():
    cast, proj, impact = [], [], []
    for frame in range(FRAMES):
        s = canvas()
        sauce_flame(s, (28 + frame // 2, 32 - frame // 2), 1.0)
        line(s, FOAM, (18, 46), (44, 18), 2)
        cast.append(s)

        pr = canvas()
        cx, cy = projectile_arc(14, 42, 52, 22, frame / (FRAMES - 1), 14)
        sauce_flame(pr, (cx, cy), 0.9)
        proj.append(pr)

        h = canvas()
        burst(h, (32, 30), 11 + frame * 2, FIRE, BEAT, 8)
        sauce_flame(h, (32, 30), 0.8)
        impact.append(h)
    return cast, proj, impact


def make_finale_froth():
    cast, proj, impact = [], [], []
    for frame in range(FRAMES):
        s = canvas()
        for ang in (0, 1.7, 3.4, 5.1):
            x = 32 + int(math.cos(ang + frame * 0.2) * 12)
            y = 32 + int(math.sin(ang + frame * 0.2) * 10)
            circle(s, FOAM, (x, y), 4)
        burst(s, (32, 32), 6 + frame * 2, BEAT, FOAM, 6)
        cast.append(s)

        pr = canvas()
        cx, cy = projectile_arc(12, 34, 52, 24, frame / (FRAMES - 1), 8)
        for ang in (0, 2.1, 4.2):
            x = cx + int(math.cos(ang + frame * 0.3) * 7)
            y = cy + int(math.sin(ang + frame * 0.3) * 7)
            circle(pr, FOAM, (x, y), 3)
        circle(pr, BEAT, (cx, cy), 3)
        proj.append(pr)

        h = canvas()
        for ang in range(0, 360, 45):
            rad = math.radians(ang)
            x = 32 + int(math.cos(rad) * (10 + frame * 2))
            y = 30 + int(math.sin(rad) * (10 + frame * 2))
            circle(h, FOAM, (x, y), 3)
        burst(h, (32, 30), 10 + frame * 2, BEAT, FOAM, 8)
        impact.append(h)
    return cast, proj, impact


BUILDERS = {
    "fork_flick": make_fork_flick,
    "sauce_splash": make_sauce_splash,
    "al_dente_slam": make_al_dente_slam,
    "meatball_panic": make_meatball_panic,
    "drum_knock": make_drum_knock,
    "sahur_burst": make_sahur_burst,
    "tung_roll": make_tung_roll,
    "midnight_march": make_midnight_march,
    "pirouette_pour": make_pirouette_pour,
    "foam_ribbon": make_foam_ribbon,
    "arabesque_roast": make_arabesque_roast,
    "finale_froth": make_finale_froth,
}


def generate_move_fx() -> None:
    MOVE_FX.mkdir(parents=True, exist_ok=True)
    for key, builder in BUILDERS.items():
        cast, proj, impact = builder()
        save_phase(key, "cast", cast)
        save_phase(key, "impact", impact)
        if proj:
            save_phase(key, "proj", proj)
        else:
            for old in MOVE_FX.glob(f"{key}_proj_*.png"):
                old.unlink()


def main() -> None:
    pygame.init()
    pygame.display.set_mode((1, 1))
    generate_move_fx()
    pygame.quit()
    print("Generated custom move fx in assets/sprites/move_fx.")


if __name__ == "__main__":
    main()
