import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pygame

from brainrotmon.game.assets import AssetStore
from brainrotmon.game.audio import Audio
from brainrotmon.game.creatures import Battler, CREATURES
from brainrotmon.game.scenes import BattleScene, Game
from brainrotmon.game.settings import SCREEN_HEIGHT, SCREEN_WIDTH


def latest_rect(scene, name):
    for rect_name, rect in reversed(scene.debug_rects):
        if rect_name == name:
            return rect
    return None


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    game = Game(screen, AssetStore(), Audio())
    screen_rect = screen.get_rect()
    keys = list(CREATURES)
    failures = []

    for index, player_key in enumerate(keys):
        enemy_key = keys[(index + 7) % len(keys)]
        game.state.party = [Battler(CREATURES[player_key], level=2)]
        battle = BattleScene(game, enemy_key)

        player_anchors = set()
        enemy_anchors = set()
        for step in range(12):
            battle.t = step / 12
            battle.draw(screen)
            for name, rect in battle.debug_rects:
                if not screen_rect.contains(rect):
                    failures.append(f"{player_key} vs {enemy_key}: {name} out of screen {rect}")
            player_rect = latest_rect(battle, player_key)
            enemy_rect = latest_rect(battle, enemy_key)
            if player_rect:
                player_anchors.add(player_rect.midbottom)
            if enemy_rect:
                enemy_anchors.add(enemy_rect.midbottom)

        if len(player_anchors) > 1:
            failures.append(f"{player_key}: player idle anchor drifted {sorted(player_anchors)}")
        if len(enemy_anchors) > 1:
            failures.append(f"{enemy_key}: enemy idle anchor drifted {sorted(enemy_anchors)}")

        battle.damage(battle.player, battle.enemy, battle.player.moves[0])
        for step in range(8):
            battle.t = 1 + step / 12
            battle.draw(screen)
            for name, rect in battle.debug_rects:
                if not screen_rect.contains(rect):
                    failures.append(f"{player_key} attack: {name} out of screen {rect}")

    pygame.quit()
    if failures:
        print("\n".join(failures))
        raise SystemExit(1)
    print(f"battle_layout_ok creatures={len(keys)}")


if __name__ == "__main__":
    main()
