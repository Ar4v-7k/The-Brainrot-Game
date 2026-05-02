import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pygame

from brainrotmon.game.assets import AssetStore
from brainrotmon.game.creatures import CREATURES


OUT_PATH = ROOT / "brainrotmon" / "tmp_debug" / "battle_sprite_preview.png"
BOXES = {"enemy": (108, 92), "player": (97, 82)}


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    assets = AssetStore()
    keys = list(CREATURES.keys())
    cell_w = 140
    cell_h = 136
    sheet = pygame.Surface((cell_w * len(keys), cell_h * 2), pygame.SRCALPHA)
    sheet.fill((11, 14, 20))
    font = pygame.font.SysFont("arial", 12, bold=True)
    tiny = pygame.font.SysFont("arial", 10)

    for col, key in enumerate(keys):
        for row, variant in enumerate(("enemy", "player")):
            cell = pygame.Rect(col * cell_w, row * cell_h, cell_w, cell_h)
            pygame.draw.rect(sheet, (29, 35, 49), cell.inflate(-8, -8), border_radius=10)
            pygame.draw.rect(sheet, (105, 120, 155), cell.inflate(-8, -8), 2, border_radius=10)
            label = font.render(f"{key} {variant}", True, (241, 236, 222))
            sheet.blit(label, (cell.x + 12, cell.y + 10))
            box_w, box_h = BOXES[variant]
            frame = assets.creature_battle.get(key, {}).get(variant, [pygame.Surface((1, 1), pygame.SRCALPHA)])[0]
            rect = frame.get_rect(center=(cell.centerx, cell.y + 76))
            sheet.blit(frame, rect.topleft)
            meta = tiny.render(f"{frame.get_width()}x{frame.get_height()}", True, (212, 191, 104))
            sheet.blit(meta, (cell.x + 12, cell.bottom - 24))
            pygame.draw.rect(sheet, (60, 70, 94), pygame.Rect(cell.centerx - box_w // 2, cell.y + 76 - box_h // 2, box_w, box_h), 1)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet, str(OUT_PATH))
    pygame.quit()
    print(OUT_PATH)


if __name__ == "__main__":
    main()
