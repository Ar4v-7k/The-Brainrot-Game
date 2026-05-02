from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import pygame

from .creatures import CREATURES
from .move_anim_manifest import MOVE_ANIM_MANIFEST
from .settings import COLORS, SOUNDS_DIR, SPRITES_DIR, VIRTUAL_HEIGHT, VIRTUAL_WIDTH


REQUIRED_FILES = [
    SOUNDS_DIR / "menu.wav",
    SOUNDS_DIR / "attack.wav",
    SOUNDS_DIR / "hit.wav",
    SOUNDS_DIR / "capture.wav",
    SPRITES_DIR / "runtime_ui" / "title_card.png",
    SPRITES_DIR / "runtime_ui" / "command_box.png",
    SPRITES_DIR / "runtime_ui" / "stat_box.png",
    SPRITES_DIR / "runtime_ui" / "slot_panel.png",
    SPRITES_DIR / "runtime_ui" / "reward_card.png",
    SPRITES_DIR / "runtime_ui" / "menu_button.png",
    SPRITES_DIR / "runtime_ui" / "title_bg.png",
    SPRITES_DIR / "runtime_ui" / "battle_bg.png",
    SPRITES_DIR / "overworld" / "tileset.png",
    SPRITES_DIR / "overworld" / "tileset_index.json",
    SPRITES_DIR / "overworld" / "player_walk.png",
    SPRITES_DIR / "overworld" / "npc_base.png",
    SPRITES_DIR / "overworld" / "trainer_sprite.png",
    SPRITES_DIR / "adventure" / "rotria_map.png",
]


def verify_assets() -> bool:
    missing = [path for path in REQUIRED_FILES if not path.exists()]
    for key in CREATURES:
        if not (SPRITES_DIR / "creatures" / f"{key}.png").exists():
            missing.append(SPRITES_DIR / "creatures" / f"{key}.png")
        for frame in range(6):
            for variant in ("enemy", "player"):
                baked = SPRITES_DIR / "creature_battle" / f"{key}_{variant}_{frame}.png"
                if not baked.exists():
                    missing.append(baked)
    for move_key, config in MOVE_ANIM_MANIFEST.items():
        for frame in range(6):
            body = SPRITES_DIR / "move_anim" / f"{move_key}_body_{frame}.png"
            effect = SPRITES_DIR / "move_anim" / f"{move_key}_effect_{frame}.png"
            if not body.exists():
                missing.append(body)
            if not effect.exists():
                missing.append(effect)
            if config["projectile_path"] != "none":
                projectile = SPRITES_DIR / "move_anim" / f"{move_key}_projectile_{frame}.png"
                if not projectile.exists():
                    missing.append(projectile)
    if missing:
        print("Assets missing. Run: python3 tools/generate_assets.py")
        for path in missing[:10]:
            print(f"  - {path}")
        return False
    return True


class AssetStore:
    def __init__(self, autoload: bool = True):
        if not verify_assets():
            pygame.quit()
            sys.exit(1)
        self.loaded = False
        self.creatures: Dict[str, pygame.Surface] = {}
        self.creature_anim: Dict[str, Dict[str, List[pygame.Surface]]] = {}
        self.creature_battle: Dict[str, Dict[str, List[pygame.Surface]]] = {}
        self.player_battle: Dict[str, List[pygame.Surface]] = {"idle": [], "attack": []}
        self.ui: Dict[str, pygame.Surface] = {}
        self.fx: Dict[str, pygame.Surface] = {}
        self.move_anim: Dict[str, Dict[str, List[pygame.Surface]]] = {}
        self.runtime: Dict[str, pygame.Surface] = {}
        self.adventure: Dict[str, pygame.Surface] = {}
        self.overworld: Dict[str, pygame.Surface] = {}
        self.tile_index: Dict[str, Tuple[int, int]] = {}
        if autoload:
            for _done, _total, _label in self.iter_load():
                pass

    def _load_image(self, path: Path) -> pygame.Surface:
        return pygame.image.load(str(path)).convert_alpha()

    def _sorted_anim_paths(self, pattern: str) -> List[Path]:
        paths = list(SPRITES_DIR.glob(pattern))
        return sorted(paths, key=lambda path: int(path.stem.split("_")[-1]))

    def get_runtime(self, name: str) -> pygame.Surface:
        if name not in self.runtime:
            self.runtime[name] = self._make_runtime_fallback(name)
        return self.runtime[name]

    def get_adventure(self, name: str) -> pygame.Surface:
        if name not in self.adventure:
            return pygame.Surface((1, 1), pygame.SRCALPHA)
        return self.adventure[name]

    def get_overworld(self, name: str) -> pygame.Surface:
        if name not in self.overworld:
            return pygame.Surface((1, 1), pygame.SRCALPHA)
        return self.overworld[name]

    def _make_runtime_fallback(self, name: str) -> pygame.Surface:
        if name == "title_bg":
            surf = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
            surf.fill((16, 20, 33))
            for y in range(0, VIRTUAL_HEIGHT, 6):
                pygame.draw.line(surf, (36, 46, 74), (0, y), (VIRTUAL_WIDTH, y))
            return surf
        if name == "battle_bg":
            surf = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
            surf.fill((28, 46, 92))
            pygame.draw.rect(surf, (160, 132, 82), (0, 122, VIRTUAL_WIDTH, 28))
            pygame.draw.rect(surf, (72, 128, 70), (0, 150, VIRTUAL_WIDTH, VIRTUAL_HEIGHT - 150))
            return surf
        if name == "title_card":
            surf = pygame.Surface((VIRTUAL_WIDTH - 36, 58), pygame.SRCALPHA)
            pygame.draw.rect(surf, COLORS["panel"], surf.get_rect(), border_radius=8)
            pygame.draw.rect(surf, COLORS["gold"], surf.get_rect(), 2, border_radius=8)
            return surf
        if name == "command_box":
            surf = pygame.Surface((VIRTUAL_WIDTH - 12, 64), pygame.SRCALPHA)
            pygame.draw.rect(surf, COLORS["panel"], surf.get_rect(), border_radius=8)
            pygame.draw.rect(surf, COLORS["stroke"], surf.get_rect(), 2, border_radius=8)
            return surf
        if name == "stat_box":
            surf = pygame.Surface((142, 52), pygame.SRCALPHA)
            pygame.draw.rect(surf, COLORS["panel"], surf.get_rect(), border_radius=6)
            pygame.draw.rect(surf, COLORS["stroke"], surf.get_rect(), 2, border_radius=6)
            return surf
        if name == "slot_panel":
            surf = pygame.Surface((VIRTUAL_WIDTH - 32, 44), pygame.SRCALPHA)
            pygame.draw.rect(surf, COLORS["panel"], surf.get_rect(), border_radius=8)
            pygame.draw.rect(surf, COLORS["stroke_dim"], surf.get_rect(), 2, border_radius=8)
            return surf
        if name == "reward_card":
            surf = pygame.Surface((100, 124), pygame.SRCALPHA)
            pygame.draw.rect(surf, COLORS["panel"], surf.get_rect(), border_radius=8)
            pygame.draw.rect(surf, COLORS["gold"], surf.get_rect(), 2, border_radius=8)
            return surf
        if name == "menu_button":
            surf = pygame.Surface((72, 18), pygame.SRCALPHA)
            pygame.draw.rect(surf, COLORS["panel"], surf.get_rect(), border_radius=6)
            pygame.draw.rect(surf, COLORS["gold"], surf.get_rect(), 2, border_radius=6)
            return surf
        return pygame.Surface((8, 8), pygame.SRCALPHA)

    def iter_load(self):
        tasks: List[Tuple[str, str, Path]] = []
        tile_index_path = SPRITES_DIR / "overworld" / "tileset_index.json"
        if tile_index_path.exists():
            raw_index = json.loads(tile_index_path.read_text())
            self.tile_index = {key: (int(value[0]), int(value[1])) for key, value in raw_index.items()}
        for key in CREATURES:
            tasks.append((f"creature.{key}", "creatures", SPRITES_DIR / "creatures" / f"{key}.png"))
            for phase in ("idle", "attack"):
                for path in self._sorted_anim_paths(f"creature_anim/{key}_{phase}_*.png"):
                    tasks.append((f"anim.{key}.{phase}.{path.stem}", "anim", path))
            for variant in ("enemy", "player"):
                for path in self._sorted_anim_paths(f"creature_battle/{key}_{variant}_*.png"):
                    tasks.append((f"battle.{key}.{variant}.{path.stem}", "creature_battle", path))
        for phase in ("idle", "attack"):
            for path in self._sorted_anim_paths(f"player_battle/player_{phase}_*.png"):
                tasks.append((f"player.{phase}.{path.stem}", "player_battle", path))
        for name in (
            "attack",
            "defend",
            "special",
            "capture",
            "item",
            "run",
            "capsule",
            "tonic",
            "battle_menu_panel",
            "hp_bar_full",
        ):
            path = SPRITES_DIR / "ui" / f"{name}.png"
            if path.exists():
                tasks.append((f"ui.{name}", "ui", path))
        for name in ("slash", "burst", "swoosh", "fire", "water", "wind", "sparkle", "dust"):
            path = SPRITES_DIR / "fx" / f"{name}.png"
            if path.exists():
                tasks.append((f"fx.{name}", "fx", path))
        for path in sorted(SPRITES_DIR.glob("move_anim/*.png")):
            tasks.append((f"moveanim.{path.stem}", "move_anim", path))
        for name in (
            "title_card",
            "command_box",
            "stat_box",
            "slot_panel",
            "reward_card",
            "menu_button",
            "title_bg",
            "battle_bg",
        ):
            tasks.append((f"runtime.{name}", "runtime", SPRITES_DIR / "runtime_ui" / f"{name}.png"))
        for path in sorted(SPRITES_DIR.glob("adventure/*.png")):
            tasks.append((f"adventure.{path.stem}", "adventure", path))
        for path in sorted(SPRITES_DIR.glob("overworld/*.png")):
            tasks.append((f"overworld.{path.stem}", "overworld", path))

        total = len(tasks)
        done = 0
        for label, kind, path in tasks:
            image = self._load_image(path)
            if kind == "creatures":
                self.creatures[path.stem] = image
            elif kind == "anim":
                key, phase, _ = path.stem.rsplit("_", 2)
                bucket = self.creature_anim.setdefault(key, {"idle": [], "attack": []})
                bucket[phase].append(image)
            elif kind == "creature_battle":
                key, variant, _ = path.stem.rsplit("_", 2)
                bucket = self.creature_battle.setdefault(key, {"enemy": [], "player": []})
                bucket[variant].append(image)
            elif kind == "player_battle":
                phase = path.stem.split("_")[1]
                self.player_battle.setdefault(phase, []).append(image)
            elif kind == "ui":
                self.ui[path.stem] = image
            elif kind == "fx":
                self.fx[path.stem] = image
            elif kind == "move_anim":
                key, phase, _ = path.stem.rsplit("_", 2)
                bucket = self.move_anim.setdefault(key, {"body": [], "effect": [], "projectile": []})
                bucket.setdefault(phase, []).append(image)
            elif kind == "runtime":
                self.runtime[path.stem] = image
            elif kind == "adventure":
                self.adventure[path.stem] = image
            elif kind == "overworld":
                self.overworld[path.stem] = image
            done += 1
            yield done, total, label

        self.loaded = True
