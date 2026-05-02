from __future__ import annotations

from typing import Iterable, List, Tuple

import pygame

from .settings import COLORS


def make_font(size: int, bold: bool = False) -> pygame.font.Font:
    return pygame.font.SysFont("couriernew", size, bold=bold)


def draw_text(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    pos: Tuple[int, int],
    color=COLORS["white"],
    align: str = "topleft",
    shadow: bool = True,
) -> pygame.Rect:
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    setattr(rect, align, pos)
    if shadow:
        shadow_img = font.render(text, True, COLORS["shadow"])
        shadow_rect = shadow_img.get_rect()
        setattr(shadow_rect, align, (pos[0] + 1, pos[1] + 1))
        surface.blit(shadow_img, shadow_rect)
    surface.blit(rendered, rect)
    return rect


def wrap_text(font: pygame.font.Font, text: str, max_width: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    line = ""
    for word in words:
        test = f"{line} {word}".strip()
        if font.size(test)[0] <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def ellipsize_text(font: pygame.font.Font, text: str, max_width: int) -> str:
    if font.size(text)[0] <= max_width:
        return text
    trimmed = text
    while trimmed and font.size(trimmed + "...")[0] > max_width:
        trimmed = trimmed[:-1]
    return (trimmed + "...") if trimmed else "..."


def draw_window(
    surface: pygame.Surface,
    rect: pygame.Rect,
    fill=COLORS["panel"],
    stroke=COLORS["stroke"],
    accent=COLORS["panel_3"],
) -> None:
    pygame.draw.rect(surface, COLORS["shadow"], rect.move(2, 2))
    pygame.draw.rect(surface, fill, rect)
    pygame.draw.rect(surface, COLORS["cream"], rect.inflate(-4, -4), 1)
    pygame.draw.rect(surface, accent, rect.inflate(-2, -2), 1)
    pygame.draw.rect(surface, stroke, rect, 2)


def draw_choice_box(
    surface: pygame.Surface,
    rect: pygame.Rect,
    selected: bool = False,
    dim: bool = False,
) -> None:
    fill = COLORS["panel_2"] if not dim else (177, 168, 135)
    stroke = COLORS["select"] if selected else COLORS["stroke_dim"]
    pygame.draw.rect(surface, fill, rect)
    pygame.draw.rect(surface, stroke, rect, 1 if not selected else 2)
    if selected:
        pygame.draw.rect(surface, (183, 145, 61), rect.inflate(-5, -5), 1)
        pygame.draw.polygon(
            surface,
            COLORS["select"],
            [(rect.x + 4, rect.centery), (rect.x + 9, rect.y + 4), (rect.x + 9, rect.bottom - 4)],
        )


def draw_meter(
    surface: pygame.Surface,
    rect: pygame.Rect,
    ratio: float,
    fill,
    back=COLORS["panel"],
    stroke=COLORS["stroke"],
) -> None:
    ratio = max(0.0, min(1.0, ratio))
    pygame.draw.rect(surface, COLORS["black"], rect.move(1, 1))
    pygame.draw.rect(surface, back, rect)
    inner = rect.inflate(-4, -4)
    inner.width = max(0, int(inner.width * ratio))
    if inner.width:
        pygame.draw.rect(surface, fill, inner)
        if inner.height > 3:
            pygame.draw.line(surface, COLORS["white"], (inner.x, inner.y), (inner.right - 1, inner.y), 1)
    pygame.draw.rect(surface, stroke, rect, 1)


def draw_backdrop(surface: pygame.Surface) -> None:
    width, height = surface.get_size()
    for y in range(height):
        t = y / max(1, height - 1)
        color = (
            int(COLORS["bg_top"][0] * (1 - t) + COLORS["bg_bottom"][0] * t),
            int(COLORS["bg_top"][1] * (1 - t) + COLORS["bg_bottom"][1] * t),
            int(COLORS["bg_top"][2] * (1 - t) + COLORS["bg_bottom"][2] * t),
        )
        pygame.draw.line(surface, color, (0, y), (width, y))
    for y in range(0, height, 8):
        pygame.draw.line(surface, (95, 150, 97), (0, y), (width, y))


def draw_list(
    surface: pygame.Surface,
    font: pygame.font.Font,
    items: Iterable[str],
    origin: Tuple[int, int],
    selected: int,
    width: int,
    row_h: int = 24,
) -> None:
    x, y = origin
    for idx, label in enumerate(items):
        rect = pygame.Rect(x, y + idx * row_h, width, row_h - 2)
        draw_choice_box(surface, rect, selected=idx == selected)
        draw_text(
            surface,
            font,
            label,
            (rect.x + 10, rect.y + rect.height // 2),
            COLORS["cream"],
            align="midleft",
        )
