from __future__ import annotations

import json
from dataclasses import dataclass
import math
from pathlib import Path
import random
from typing import Callable, Dict, List, Optional, Tuple

import pygame

from .adventure_data import BADGES, ITEMS, MAPS, MAP_POIS, STARTERS, TILE_WALKABLE, WATER_TILES, ENCOUNTER_TILES
from .assets import AssetStore
from .audio import Audio
from .battle import BattleEvent, BattleResult, BattleSession
from .creatures import CREATURES, ENCOUNTER_KEYS
from .idle_manifest import IDLE_MANIFEST
from .move_anim_manifest import MOVE_ANIM_MANIFEST
from .settings import (
    COLORS,
    RENDER_SCALE,
    TITLE,
    VIEWPORT_HEIGHT,
    VIEWPORT_WIDTH,
    VIEWPORT_X,
    VIEWPORT_Y,
    VIRTUAL_HEIGHT,
    VIRTUAL_WIDTH,
)
from .rpg_rules import xp_to_next
from .state import AdventureState, CreatureInstance, PlayerAppearance, ProfileState, RunState, SaveBundle, SettingsState
from .storage import Storage
from .ui import draw_backdrop, draw_choice_box, draw_meter, draw_text, draw_window, ellipsize_text, make_font, wrap_text


TILE_CHAR_TO_NAME = {
    ".": "grass_light",
    "g": "grass_tall",
    "f": "flower_red",
    "r": "dirt_path",
    "=": "stone_cobble",
    "s": "sand_dry",
    "~": "water_ocean",
    "#": "wall_stone",
    "B": "wall_dark",
    "D": "door_wood",
    "H": "wall_wood",
    "S": "sign_wood",
    "T": "tree_oak_TL",
    "i": "ice_smooth",
    "d": "cave_floor",
    "j": "jungle_floor",
    "R": "ruin_floor",
    "m": "cave_wall",
    "x": "warp_tile",
    "c": "cave_floor",
    "o": "sand_dry",
}

TILE_SIZE = 16
TILE_IN_SHEET = 32

_missing_tile_log: set = set()


def _load_tileset() -> pygame.Surface:
    tileset_path = Path(__file__).parent.parent / "assets" / "sprites" / "overworld" / "tileset.png"
    return pygame.image.load(str(tileset_path)).convert_alpha()


def _load_tile_index() -> Dict[str, Tuple[int, int]]:
    index_path = Path(__file__).parent.parent / "assets" / "sprites" / "overworld" / "tileset_index.json"
    raw = json.loads(index_path.read_text())
    index = {key: (int(val[0]), int(val[1])) for key, val in raw.items()}
    index["grass_light"] = index.get("batch1_tile_0_0", (0, 0))
    index["grass_tall"] = index.get("batch1_tile_0_7", (0, 7))
    index["flower_red"] = index.get("batch1_tile_0_8", (0, 8))
    index["dirt_path"] = index.get("batch1_tile_1_0", (1, 0))
    index["stone_cobble"] = index.get("batch1_tile_2_0", (2, 0))
    index["sand_dry"] = index.get("batch1_tile_3_0", (3, 0))
    index["water_ocean"] = index.get("batch1_tile_8_0", (8, 0))
    index["wall_stone"] = index.get("batch3_tile_1_0", (11, 16))
    index["wall_dark"] = index.get("batch3_tile_1_7", (12, 23))
    index["door_wood"] = index.get("batch3_tile_3_1", (12, 17))
    index["wall_wood"] = index.get("batch3_tile_0_0", (11, 0))
    index["sign_wood"] = index.get("batch4_tile_6_0", (24, 0))
    index["tree_oak_TL"] = index.get("batch2_tile_0_0", (6, 0))
    index["ice_smooth"] = index.get("batch1_tile_4_7", (4, 7))
    index["cave_floor"] = index.get("batch1_tile_6_1", (3, 1))
    index["jungle_floor"] = index.get("batch1_tile_5_0", (2, 16))
    index["ruin_floor"] = index.get("batch1_tile_7_0", (3, 16))
    index["cave_wall"] = index.get("batch1_tile_6_8", (3, 8))
    index["warp_tile"] = index.get("batch1_tile_11_5", (5, 21))
    return index


_tileset_cache: pygame.Surface | None = None
_tile_index_cache: Dict[str, Tuple[int, int]] = {}


def draw_tile(surface: pygame.Surface, rect: pygame.Rect, char: str, x: int, y: int, night: bool, t: float, assets: AssetStore) -> None:
    global _tileset_cache, _tile_index_cache

    if _tileset_cache is None:
        _tileset_cache = _load_tileset()
    if not _tile_index_cache:
        _tile_index_cache = _load_tile_index()

    tile_name = TILE_CHAR_TO_NAME.get(char, "grass_light")

    tile_pos = _tile_index_cache.get(tile_name)
    if tile_pos is None:
        if tile_name not in _missing_tile_log:
            _missing_tile_log.add(tile_name)
            print(f"[draw_tile] Missing tile: {tile_name!r}")
        tile_name = "grass_light"
        tile_pos = _tile_index_cache.get(tile_name, (0, 0))

    row, col = tile_pos
    src_x = col * TILE_IN_SHEET
    src_y = row * TILE_IN_SHEET

    tile_crop = _tileset_cache.subsurface(pygame.Rect(src_x, src_y, TILE_IN_SHEET, TILE_IN_SHEET)).copy()
    scaled = pygame.transform.scale(tile_crop, (TILE_SIZE, TILE_SIZE))
    surface.blit(scaled, rect.topleft)

    if char == "x":
        pygame.draw.polygon(surface, COLORS["select"], ((rect.centerx, rect.y + 4), (rect.x + 5, rect.y + 10), (rect.right - 5, rect.y + 10)))
        pygame.draw.line(surface, COLORS["stroke"], (rect.centerx, rect.y + 4), (rect.centerx, rect.bottom - 4), 1)
    if night:
        tint = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        tint.fill((18, 38, 82, 82))
        surface.blit(tint, rect.topleft)


@dataclass(frozen=True)
class MoveVisual:
    motion: str
    projectile: str
    sprite: str
    color: Tuple[int, int, int]
    accent: Tuple[int, int, int]


MOVE_VISUALS: Dict[str, MoveVisual] = {
    "fork_flick": MoveVisual("jab", "fork", "slash", COLORS["stroke"], COLORS["gold"]),
    "sauce_splash": MoveVisual("whip", "sauce_arc", "water", (214, 76, 58), COLORS["gold"]),
    "al_dente_slam": MoveVisual("slam", "none", "burst", COLORS["gold"], (201, 124, 68)),
    "meatball_panic": MoveVisual("toss", "meatball", "burst", (131, 76, 54), COLORS["red"]),
    "drum_knock": MoveVisual("drum_hit", "stick", "slash", COLORS["gold"], COLORS["red"]),
    "sahur_burst": MoveVisual("beat", "sound_ring", "wind", COLORS["gold"], COLORS["red"]),
    "tung_roll": MoveVisual("roll", "drum_spin", "dust", (173, 116, 70), COLORS["gold"]),
    "midnight_march": MoveVisual("march", "step_wave", "burst", COLORS["gold"], COLORS["red"]),
    "pirouette_pour": MoveVisual("spin", "coffee_arc", "sparkle", (169, 112, 72), COLORS["cream"]),
    "foam_ribbon": MoveVisual("ribbon", "foam_ribbon", "water", COLORS["cream"], COLORS["teal"]),
    "arabesque_roast": MoveVisual("arabesque", "roast_arc", "fire", (243, 134, 67), COLORS["gold"]),
    "finale_froth": MoveVisual("finale", "froth_bloom", "sparkle", COLORS["cream"], COLORS["gold"]),
    "sneaker_snap": MoveVisual("jab", "none", "slash", COLORS["cream"], COLORS["teal"]),
    "tralala_wave": MoveVisual("beat", "sound_ring", "wind", COLORS["teal"], COLORS["cream"]),
    "reef_rush": MoveVisual("roll", "none", "water", COLORS["teal"], COLORS["gold"]),
    "coral_chorus": MoveVisual("finale", "froth_bloom", "sparkle", COLORS["teal"], COLORS["gold"]),
    "silent_sip": MoveVisual("jab", "none", "slash", COLORS["cream"], COLORS["stroke"]),
    "crema_dagger": MoveVisual("toss", "roast_arc", "slash", COLORS["gold"], COLORS["cream"]),
    "shadow_roast": MoveVisual("arabesque", "none", "fire", COLORS["red"], COLORS["gold"]),
    "espresso_exit": MoveVisual("spin", "coffee_arc", "sparkle", COLORS["gold"], COLORS["cream"]),
    "orbit_kick": MoveVisual("roll", "none", "burst", COLORS["gold"], COLORS["cream"]),
    "milky_way_moo": MoveVisual("beat", "sound_ring", "wind", COLORS["cream"], COLORS["gold"]),
    "ring_charge": MoveVisual("roll", "drum_spin", "sparkle", COLORS["gold"], COLORS["teal"]),
    "nova_hoof": MoveVisual("slam", "none", "burst", COLORS["gold"], COLORS["red"]),
    "runway_rush": MoveVisual("roll", "none", "slash", COLORS["gold"], COLORS["red"]),
    "bomb_burst": MoveVisual("toss", "meatball", "burst", COLORS["red"], COLORS["gold"]),
    "croco_cannon": MoveVisual("beat", "drum_spin", "dust", COLORS["gold"], COLORS["red"]),
    "tail_rotor": MoveVisual("march", "none", "wind", COLORS["teal"], COLORS["gold"]),
    "cooler_kick": MoveVisual("jab", "none", "slash", COLORS["cream"], COLORS["teal"]),
    "frost_spit": MoveVisual("toss", "foam_ribbon", "water", COLORS["teal"], COLORS["cream"]),
    "ice_box_crash": MoveVisual("slam", "none", "burst", COLORS["cream"], COLORS["gold"]),
    "desert_chill": MoveVisual("beat", "sound_ring", "wind", COLORS["teal"], COLORS["gold"]),
    "branch_bonk": MoveVisual("drum_hit", "none", "slash", COLORS["gold"], COLORS["teal"]),
    "pinecone_pop": MoveVisual("toss", "meatball", "dust", COLORS["gold"], COLORS["red"]),
    "brrr_blast": MoveVisual("beat", "sound_ring", "wind", COLORS["cream"], COLORS["teal"]),
    "mossy_mayhem": MoveVisual("slam", "none", "burst", COLORS["teal"], COLORS["gold"]),
    "peel_jab": MoveVisual("jab", "none", "slash", COLORS["gold"], COLORS["cream"]),
    "banana_boomerang": MoveVisual("toss", "coffee_arc", "sparkle", COLORS["gold"], COLORS["teal"]),
    "monkey_mash": MoveVisual("roll", "none", "burst", COLORS["gold"], COLORS["red"]),
    "bananini_barrage": MoveVisual("finale", "froth_bloom", "sparkle", COLORS["gold"], COLORS["cream"]),
    "scurry_slice": MoveVisual("jab", "none", "slash", COLORS["gold"], COLORS["red"]),
    "crust_comet": MoveVisual("toss", "sauce_arc", "fire", COLORS["red"], COLORS["gold"]),
    "mozza_mob": MoveVisual("beat", "sound_ring", "sparkle", COLORS["cream"], COLORS["gold"]),
    "oven_ambush": MoveVisual("slam", "none", "burst", COLORS["red"], COLORS["gold"]),
    "layer_lash": MoveVisual("whip", "none", "slash", COLORS["gold"], COLORS["red"]),
    "ricotta_rattle": MoveVisual("toss", "foam_ribbon", "water", COLORS["cream"], COLORS["teal"]),
    "coil_crush": MoveVisual("roll", "none", "burst", COLORS["gold"], COLORS["red"]),
    "bake_coil": MoveVisual("finale", "roast_arc", "fire", COLORS["red"], COLORS["gold"]),
    "scoop_smack": MoveVisual("jab", "none", "slash", COLORS["cream"], COLORS["teal"]),
    "frost_swirl": MoveVisual("spin", "foam_ribbon", "water", COLORS["teal"], COLORS["cream"]),
    "sundae_slide": MoveVisual("roll", "none", "sparkle", COLORS["cream"], COLORS["gold"]),
    "brain_freeze": MoveVisual("beat", "sound_ring", "wind", COLORS["teal"], COLORS["cream"]),
    "kernel_kick": MoveVisual("jab", "none", "slash", COLORS["gold"], COLORS["cream"]),
    "corn_quake": MoveVisual("slam", "none", "burst", COLORS["gold"], COLORS["red"]),
    "golden_roar": MoveVisual("beat", "sound_ring", "wind", COLORS["gold"], COLORS["cream"]),
    "polenta_meteor": MoveVisual("toss", "meatball", "fire", COLORS["gold"], COLORS["red"]),
    "string_sting": MoveVisual("ribbon", "none", "slash", COLORS["cream"], COLORS["gold"]),
    "ganache_glint": MoveVisual("toss", "coffee_arc", "sparkle", COLORS["gold"], COLORS["cream"]),
    "puppet_pivot": MoveVisual("spin", "none", "sparkle", COLORS["cream"], COLORS["teal"]),
    "marzipan_mirage": MoveVisual("finale", "froth_bloom", "sparkle", COLORS["cream"], COLORS["gold"]),
    "crown_crimp": MoveVisual("jab", "none", "slash", COLORS["gold"], COLORS["cream"]),
    "sauce_decree": MoveVisual("toss", "sauce_arc", "fire", COLORS["red"], COLORS["gold"]),
    "noble_fold": MoveVisual("roll", "none", "burst", COLORS["gold"], COLORS["cream"]),
    "ravioli_reign": MoveVisual("finale", "froth_bloom", "sparkle", COLORS["gold"], COLORS["cream"]),
    "link_lash": MoveVisual("whip", "none", "slash", COLORS["gold"], COLORS["red"]),
    "pepper_spear": MoveVisual("toss", "roast_arc", "fire", COLORS["red"], COLORS["gold"]),
    "grill_grind": MoveVisual("roll", "none", "burst", COLORS["gold"], COLORS["red"]),
    "coliseum_sear": MoveVisual("beat", "sound_ring", "fire", COLORS["red"], COLORS["gold"]),
    "crust_cudgel": MoveVisual("jab", "none", "slash", COLORS["gold"], COLORS["teal"]),
    "olive_order": MoveVisual("toss", "meatball", "dust", COLORS["teal"], COLORS["gold"]),
    "toast_takedown": MoveVisual("slam", "none", "burst", COLORS["gold"], COLORS["red"]),
    "boss_banquet": MoveVisual("finale", "froth_bloom", "sparkle", COLORS["cream"], COLORS["gold"]),
    "toast_tread": MoveVisual("roll", "none", "burst", COLORS["gold"], COLORS["red"]),
    "tomato_mortar": MoveVisual("toss", "sauce_arc", "fire", COLORS["red"], COLORS["gold"]),
    "garlic_guard": MoveVisual("drum_hit", "none", "slash", COLORS["cream"], COLORS["gold"]),
    "bruschetta_barrage": MoveVisual("beat", "sound_ring", "burst", COLORS["red"], COLORS["gold"]),
    "curd_claw": MoveVisual("jab", "none", "slash", COLORS["cream"], COLORS["gold"]),
    "stretch_beam": MoveVisual("ribbon", "foam_ribbon", "water", COLORS["cream"], COLORS["teal"]),
    "pride_pounce": MoveVisual("roll", "none", "burst", COLORS["cream"], COLORS["gold"]),
    "melt_majesty": MoveVisual("finale", "froth_bloom", "sparkle", COLORS["gold"], COLORS["cream"]),
}

RAW_FACING: Dict[str, str] = {
    "spaghettimon": "right",
    "tungtungsahur": "left",
    "ballerinacappuccina": "right",
    "tralalerotralala": "left",
    "cappuccinoassassino": "right",
    "vaccasaturnosaturnita": "left",
    "bombardirocrocodilo": "left",
    "frigocamelo": "left",
    "brrbrrpatapim": "left",
    "chimpanzinibananini": "right",
    "raviolord": "right",
    "salsicciator": "right",
    "crostinoboss": "right",
    "bruschettank": "right",
    "mozzarellion": "right",
}


def creature_flip_for_actor(key: str, actor: str) -> bool:
    raw = RAW_FACING.get(key, "right")
    want = "left" if actor == "enemy" else "right"
    return raw != want


CONTACT_MOTIONS = {
    "jab",
    "whip",
    "slam",
    "drum_hit",
    "roll",
    "march",
    "spin",
    "ribbon",
    "arabesque",
    "finale",
}


class Scene:
    transparent = False

    def __init__(self, game: "Game"):
        self.game = game
        self.small = make_font(11)
        self.font = make_font(14)
        self.big = make_font(24, bold=True)

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pass


class Game:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.virtual = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT)).convert()
        self.storage = Storage()
        bundle = self.storage.load_bundle()
        self.settings: SettingsState = bundle.settings
        self.profile: ProfileState = bundle.profile
        self.assets = AssetStore(autoload=False)
        self.audio = Audio()
        self.sync_audio()
        self.run: Optional[RunState] = None
        self.adventure: Optional[AdventureState] = None
        self.adventure_battle_context: Optional[dict] = None
        self.scenes: List[Scene] = []
        self.push_scene(BootScene(self))

    def sync_audio(self) -> None:
        enabled = self.settings.sfx_on
        self.audio.configure(enabled=enabled, master=1.0 if enabled else 0.0)

    def push_scene(self, scene: Scene) -> None:
        self.scenes.append(scene)
        scene.on_enter()

    def pop_scene(self) -> None:
        if self.scenes:
            scene = self.scenes.pop()
            scene.on_exit()

    def replace_scene(self, scene: Scene) -> None:
        while self.scenes:
            old = self.scenes.pop()
            old.on_exit()
        self.push_scene(scene)

    def top_scene(self) -> Scene:
        return self.scenes[-1]

    def save_bundle(self) -> None:
        self.storage.save_bundle(SaveBundle(self.settings, self.profile))

    def save_run(self) -> None:
        if self.run:
            self.run.normalize()
            self.storage.save_run(self.run)

    def save_adventure(self) -> None:
        if self.adventure:
            self.adventure.normalize()
            self.storage.save_adventure(self.adventure)

    def begin_new_run(self, slot: int, starter_key: str) -> None:
        seed = random.randint(1000, 999999)
        self.run = RunState(
            slot=slot,
            seed=seed,
            wave=1,
            wins=0,
            money=0,
            starter_key=starter_key,
            party=[CreatureInstance(starter_key, 3)],
            collection=[starter_key],
        )
        self.run.normalize()
        self.profile.total_runs += 1
        self.profile.unlock(starter_key)
        self.save_bundle()
        self.save_run()

    def load_run(self, slot: int) -> bool:
        run = self.storage.load_run(slot)
        if run is None:
            return False
        self.run = run
        return True

    def begin_adventure(self, slot: int, name: str, appearance: PlayerAppearance, starter_key: str) -> None:
        seed = random.randint(1000, 999999)
        starter = CreatureInstance(starter_key, 5)
        starter.ability = ability_for(starter_key)
        starter.held_item = "crema_berry"
        starter.ensure_hp()
        self.adventure = AdventureState(
            slot=slot,
            seed=seed,
            player_name=(name or "ARAV").upper()[:10],
            appearance=appearance,
            starter_key=starter_key,
            party=[starter],
            caught=[starter_key],
            seen=[starter_key],
            quests={
                "main": "Earn the Cargo Badge in Pasta Port.",
                "scroll": "Investigate Team Scroll rumors near the docks.",
            },
        )
        self.profile.total_runs += 1
        self.profile.unlock(starter_key)
        self.save_bundle()
        self.save_adventure()

    def load_adventure(self, slot: int) -> bool:
        adventure = self.storage.load_adventure(slot)
        if adventure is None:
            return False
        self.adventure = adventure
        return True

    def start_adventure_battle(self, context: dict) -> None:
        if self.adventure is None:
            return
        enemy_key = context.get("enemy_key", "spaghettimon")
        enemy_level = int(context.get("enemy_level", max(2, self.adventure.active_creature().level)))
        enemy = CreatureInstance(enemy_key, enemy_level)
        enemy.ability = ability_for(enemy_key)
        enemy.ensure_hp()
        self.adventure.mark_seen(enemy_key)
        self.adventure_battle_context = dict(context)
        self.run = RunState(
            slot=self.adventure.slot,
            seed=random.randint(1000, 999999),
            wave=max(1, self.adventure.story_chapter + 1),
            wins=0,
            money=self.adventure.money,
            starter_key=self.adventure.starter_key,
            active_index=self.adventure.active_index,
            party=[unit.copy() for unit in self.adventure.party],
            collection=list(self.adventure.caught),
            inventory={
                "Pasta Capsule": self.adventure.bag.get("pasta_capsule", 0),
                "Tomato Tonic": self.adventure.bag.get("tomato_tonic", 0),
            },
            current_enemy=enemy,
        )
        self.replace_scene(AdventureBattleScene(self))

    def clear_run(self) -> None:
        if self.run:
            self.storage.delete_run(self.run.slot)
            self.run = None

    def complete_run(self) -> None:
        if not self.run:
            return
        self.profile.best_wave = max(self.profile.best_wave, self.run.wave)
        self.save_bundle()
        self.storage.delete_run(self.run.slot)
        self.run = None

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        if not self.scenes:
            return
        self.top_scene().handle_events(events)

    def update(self, dt: float) -> None:
        if not self.scenes:
            return
        self.top_scene().update(dt)

    def draw(self) -> None:
        self.virtual.fill(COLORS["black"])
        start = 0
        for idx, scene in enumerate(self.scenes):
            if not scene.transparent:
                start = idx
        for scene in self.scenes[start:]:
            scene.draw(self.virtual)
        self.screen.fill(COLORS["matte"])
        scaled = pygame.transform.scale(self.virtual, (VIEWPORT_WIDTH, VIEWPORT_HEIGHT))
        self.screen.blit(scaled, (VIEWPORT_X, VIEWPORT_Y))


class BootScene(Scene):
    def __init__(self, game: Game):
        super().__init__(game)
        self.loader = self.game.assets.iter_load()
        self.done = 0
        self.total = 1
        self.label = "boot"
        self.finished = False
        self.hold = 0.0
        self.t = 0.0

    def update(self, dt: float) -> None:
        self.t += dt
        if not self.finished:
            for _ in range(10):
                try:
                    self.done, self.total, self.label = next(self.loader)
                except StopIteration:
                    self.finished = True
                    break
        else:
            self.hold += dt
            if self.hold >= 0.25:
                self.game.replace_scene(TitleScene(self.game))

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.game.assets.get_runtime("title_bg"), (0, 0))
        card = self.game.assets.get_runtime("title_card")
        if card:
            surface.blit(card, (18, 28))
        draw_text(surface, self.big, "BRAINROTMON", (32, 44), COLORS["cream"], shadow=False)
        draw_text(surface, self.font, "Rebooting battle cartridge", (32, 66), COLORS["cream"])

        preview = None
        if self.game.assets.creatures:
            key = list(self.game.assets.creatures.keys())[int(self.t * 3) % len(self.game.assets.creatures)]
            preview = self.game.assets.creatures[key]
        if preview:
            sprite = fit_sprite(preview, 84, 84)
            surface.blit(sprite, (surface.get_width() - 112, 34))

        bar = pygame.Rect(32, 128, surface.get_width() - 64, 18)
        draw_meter(surface, bar, self.done / max(1, self.total), COLORS["gold"], back=COLORS["panel_2"])
        draw_text(surface, self.font, f"{int(self.done / max(1, self.total) * 100):02d}%", bar.center, COLORS["cream"], align="center")
        draw_text(surface, self.small, self.label.replace(".", " / "), (32, 156), COLORS["stroke"])
        draw_text(surface, self.small, "Local-first load. No web junk.", (32, 186), COLORS["stroke_dim"])


class TitleScene(Scene):
    def __init__(self, game: Game):
        super().__init__(game)
        self.options = ["Continue", "New Run", "Collection", "Settings", "Quit"]
        self.selected = 0
        self.t = 0.0

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.options)
                self.game.audio.play("menu")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.options)
                self.game.audio.play("menu")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.activate()
            elif event.key == pygame.K_c:
                self.game.push_scene(RosterScene(self.game, mode="collection"))

    def activate(self) -> None:
        choice = self.options[self.selected]
        if choice == "Continue":
            if not any(self.game.storage.list_adventure_slots().values()):
                self.game.audio.play("hit")
                return
            self.game.replace_scene(SaveSelectScene(self.game, mode="continue"))
        elif choice == "New Run":
            self.game.replace_scene(SaveSelectScene(self.game, mode="new"))
        elif choice == "Collection":
            self.game.push_scene(RosterScene(self.game, mode="collection"))
        elif choice == "Settings":
            self.game.push_scene(SettingsScene(self.game))
        else:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, dt: float) -> None:
        self.t += dt

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.game.assets.get_runtime("title_bg"), (0, 0))
        self._draw_showcase(surface)
        card = self.game.assets.get_runtime("title_card")
        if card:
            surface.blit(card, (18, 16))
        draw_text(surface, self.big, "BRAINROTMON", (32, 33), COLORS["cream"], shadow=False)
        draw_text(surface, self.font, "Pasta Panic Reloaded", (32, 55), COLORS["gold"])

        menu_rect = pygame.Rect(18, 88, 136, 116)
        draw_window(surface, menu_rect)
        for idx, label in enumerate(self.options):
            item_rect = pygame.Rect(menu_rect.x + 10, menu_rect.y + 10 + idx * 20, menu_rect.width - 20, 18)
            draw_choice_box(surface, item_rect, selected=idx == self.selected, dim=label == "Continue" and not any(self.game.storage.list_adventure_slots().values()))
            draw_text(surface, self.font, label, item_rect.center, COLORS["cream"], align="center")

        info_rect = pygame.Rect(168, 148, 198, 56)
        draw_window(surface, info_rect, fill=COLORS["panel_2"])
        draw_text(surface, self.small, f"Runs {self.game.profile.total_runs}", (178, 160), COLORS["stroke"])
        draw_text(surface, self.small, f"Wins {self.game.profile.total_wins}", (178, 174), COLORS["stroke"])
        draw_text(surface, self.small, f"Best Wave {self.game.profile.best_wave}", (178, 188), COLORS["stroke"])

        draw_text(surface, self.small, "Arrows move. Enter pick. C collection.", (18, 206), COLORS["stroke_dim"])

    def _draw_showcase(self, surface: pygame.Surface) -> None:
        left_key = "tungtungsahur" if "tungtungsahur" in self.game.assets.creature_anim else list(CREATURES.keys())[0]
        right_key = "ballerinacappuccina" if "ballerinacappuccina" in self.game.assets.creature_anim else list(CREATURES.keys())[1]
        draw_creature(surface, self.game.assets, left_key, (222, 112), "idle", self.t, flip=False, scale=1.15)
        draw_creature(surface, self.game.assets, right_key, (312, 94), "idle", self.t + 0.6, flip=True, scale=1.12)
        pygame.draw.ellipse(surface, COLORS["field_dark"], (180, 144, 70, 16))
        pygame.draw.ellipse(surface, COLORS["field_dark"], (274, 126, 70, 16))


class SaveSelectScene(Scene):
    def __init__(self, game: Game, mode: str):
        super().__init__(game)
        self.mode = mode
        self.selected = 0
        self.confirm_slot: Optional[int] = None
        self.slots = self.game.storage.list_adventure_slots()

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % 3
                self.confirm_slot = None
                self.game.audio.play("menu")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % 3
                self.confirm_slot = None
                self.game.audio.play("menu")
            elif event.key == pygame.K_ESCAPE:
                self.game.replace_scene(TitleScene(self.game))
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.activate()

    def activate(self) -> None:
        slot_id = self.selected + 1
        run = self.slots.get(slot_id)
        if self.mode == "continue":
            if run is None:
                self.game.audio.play("hit")
                return
            self.game.load_adventure(slot_id)
            self.game.replace_scene(AdventureScene(self.game))
            return
        if run is not None and self.confirm_slot != slot_id:
            self.confirm_slot = slot_id
            self.game.audio.play("hit")
            return
        self.game.replace_scene(CharacterCreatorScene(self.game, slot_id))

    def draw(self, surface: pygame.Surface) -> None:
        draw_backdrop(surface)
        title = "CONTINUE RUN" if self.mode == "continue" else "NEW RUN SLOT"
        draw_text(surface, self.big, title, (18, 18), COLORS["cream"])
        draw_text(surface, self.small, "Pick slot. Filled slot on new run needs one more Enter.", (18, 36), COLORS["stroke_dim"])
        for idx in range(3):
            slot_id = idx + 1
            panel = self.game.assets.get_runtime("slot_panel").copy()
            rect = panel.get_rect(topleft=(18, 62 + idx * 50))
            surface.blit(panel, rect)
            pygame.draw.rect(surface, COLORS["gold"] if idx == self.selected else COLORS["stroke_dim"], rect, 2, border_radius=8)
            draw_text(surface, self.font, f"SLOT {slot_id}", (rect.x + 12, rect.y + 12), COLORS["cream"])
            run = self.slots.get(slot_id)
            if run is None:
                draw_text(surface, self.small, "Empty save", (rect.x + 84, rect.y + 13), COLORS["stroke_dim"])
            else:
                draw_text(surface, self.small, run.player_name, (rect.x + 84, rect.y + 8), COLORS["stroke"])
                draw_text(surface, self.small, f"{MAPS.get(run.map_key, MAPS['starter_village']).name}  Badges {len(run.badges)}", (rect.x + 84, rect.y + 22), COLORS["stroke"])
            if self.confirm_slot == slot_id:
                draw_text(surface, self.small, "Overwrite?", (rect.right - 70, rect.y + 13), COLORS["red"])
        draw_text(surface, self.small, "Esc back", (18, 204), COLORS["stroke_dim"])


class RosterScene(Scene):
    transparent = False

    def __init__(self, game: Game, mode: str, slot: int = 0):
        super().__init__(game)
        self.mode = mode
        self.slot = slot
        self.keys = list(ENCOUNTER_KEYS)
        self.selected = 0
        self.scroll = 0
        self.visible = 8
        self.t = 0.0

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = max(0, self.selected - 1)
                self._sync_scroll()
                self.game.audio.play("menu")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = min(len(self.keys) - 1, self.selected + 1)
                self._sync_scroll()
                self.game.audio.play("menu")
            elif event.key == pygame.K_ESCAPE:
                if self.mode == "starter":
                    self.game.replace_scene(SaveSelectScene(self.game, mode="new"))
                else:
                    self.game.pop_scene()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.mode == "starter":
                    key = self.keys[self.selected]
                    self.game.begin_new_run(self.slot, key)
                    self.game.replace_scene(BattleScene(self.game))

    def _sync_scroll(self) -> None:
        if self.selected < self.scroll:
            self.scroll = self.selected
        elif self.selected >= self.scroll + self.visible:
            self.scroll = self.selected - self.visible + 1

    def update(self, dt: float) -> None:
        self.t += dt

    def draw(self, surface: pygame.Surface) -> None:
        draw_backdrop(surface)
        title = "PICK STARTER" if self.mode == "starter" else "BRAINROT INDEX"
        draw_text(surface, self.big, title, (18, 18), COLORS["cream"])
        left = pygame.Rect(18, 44, 124, 156)
        right = pygame.Rect(150, 44, 216, 156)
        draw_window(surface, left)
        draw_window(surface, right)
        for idx, key in enumerate(self.keys[self.scroll : self.scroll + self.visible]):
            actual = self.scroll + idx
            item = CREATURES[key]
            row = pygame.Rect(left.x + 8, left.y + 8 + idx * 18, left.width - 16, 16)
            selected = actual == self.selected
            locked = self.mode != "starter" and key not in self.game.profile.unlocked
            draw_choice_box(surface, row, selected=selected, dim=locked)
            draw_text(surface, self.small, ellipsize_text(self.small, item.name, 112), (row.x + 8, row.y + 8), COLORS["cream"], align="midleft")
        current = CREATURES[self.keys[self.selected]]
        portrait = self.game.assets.creatures[current.key]
        portrait_box = pygame.Rect(right.x + 10, right.y + 10, 90, 86)
        info_x = portrait_box.right + 10
        info_w = right.right - info_x - 10
        desc_box = pygame.Rect(right.x + 10, right.y + 102, 90, 44)
        moves_box = pygame.Rect(info_x, right.y + 74, info_w, 72)

        draw_choice_box(surface, portrait_box)
        portrait = fit_sprite(portrait, portrait_box.width - 8, portrait_box.height - 8)
        surface.blit(portrait, portrait.get_rect(center=portrait_box.center))

        name_lines = wrap_text(self.small, current.name, info_w - 6)
        name_y = right.y + 12
        for idx, line in enumerate(name_lines[:2]):
            draw_text(surface, self.small, line, (info_x, name_y + idx * 12), COLORS["cream"])
        info_y = name_y + len(name_lines[:2]) * 12
        draw_text(surface, self.small, current.kind, (info_x, info_y), COLORS["gold"])
        draw_text(surface, self.small, f"HP {current.max_hp}  ATK {current.attack}", (info_x, info_y + 14), COLORS["stroke"])
        draw_text(surface, self.small, f"DEF {current.defense}", (info_x, info_y + 26), COLORS["stroke"])
        if self.mode != "starter":
            status = "Unlocked" if current.key in self.game.profile.unlocked else "Seen" if current.key in self.game.profile.seen else "Unknown"
            draw_text(surface, self.small, status, (info_x, info_y + 40), COLORS["teal"])

        draw_choice_box(surface, desc_box)
        desc_lines = wrap_text(self.small, current.description, desc_box.width - 10)
        for idx, line in enumerate(desc_lines[:3]):
            draw_text(surface, self.small, line, (desc_box.x + 5, desc_box.y + 5 + idx * 11), COLORS["stroke"])

        draw_choice_box(surface, moves_box)
        draw_text(surface, self.small, "Moves", (moves_box.x + 5, moves_box.y + 5), COLORS["stroke_dim"])
        for idx, move in enumerate(current.moves[:4]):
            draw_text(surface, self.small, f"{idx + 1}. {move.name}", (moves_box.x + 5, moves_box.y + 18 + idx * 12), COLORS["cream"])
        footer = "Enter start run" if self.mode == "starter" else "Esc back"
        draw_text(surface, self.small, footer, (18, 204), COLORS["stroke_dim"])


class SettingsScene(Scene):
    transparent = True

    def __init__(self, game: Game):
        super().__init__(game)
        self.selected = 0
        self.items = ["SFX", "Idle Anim", "Battle Speed", "Text Speed"]

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.items)
                self.game.audio.play("menu")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.items)
                self.game.audio.play("menu")
            elif event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d, pygame.K_RETURN, pygame.K_SPACE):
                self.bump()
            elif event.key == pygame.K_ESCAPE:
                self.game.sync_audio()
                self.game.save_bundle()
                self.game.pop_scene()

    def bump(self) -> None:
        idx = self.selected
        if idx == 0:
            self.game.settings.sfx_on = not self.game.settings.sfx_on
        elif idx == 1:
            self.game.settings.idle_on = not self.game.settings.idle_on
        elif idx == 2:
            self.game.settings.battle_speed = 1 if self.game.settings.battle_speed >= 3 else self.game.settings.battle_speed + 1
        else:
            self.game.settings.text_speed = 1 if self.game.settings.text_speed >= 3 else self.game.settings.text_speed + 1
        self.game.sync_audio()
        self.game.save_bundle()
        self.game.audio.play("menu")

    def draw(self, surface: pygame.Surface) -> None:
        shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 150))
        surface.blit(shade, (0, 0))
        panel = pygame.Rect(74, 44, 236, 128)
        draw_window(surface, panel)
        draw_text(surface, self.big, "SETTINGS", (panel.centerx, panel.y + 14), COLORS["cream"], align="center")
        values = [
            "ON" if self.game.settings.sfx_on else "OFF",
            "ON" if self.game.settings.idle_on else "OFF",
            f"x{self.game.settings.battle_speed}",
            f"x{self.game.settings.text_speed}",
        ]
        for idx, label in enumerate(self.items):
            row = pygame.Rect(panel.x + 14, panel.y + 40 + idx * 18, panel.width - 28, 16)
            draw_choice_box(surface, row, selected=idx == self.selected)
            draw_text(surface, self.small, label, (row.x + 8, row.y + 8), COLORS["cream"], align="midleft")
            draw_text(surface, self.small, values[idx], (row.right - 8, row.y + 8), COLORS["gold"], align="midright")
        draw_text(surface, self.small, "Esc close", (panel.centerx, panel.bottom - 10), COLORS["stroke_dim"], align="center")


class PartyScene(Scene):
    transparent = True

    def __init__(self, game: Game, on_pick: Optional[Callable[[int], None]] = None):
        super().__init__(game)
        self.on_pick = on_pick
        self.selected = 0

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        run = self.game.run or self.game.adventure
        if run is None:
            self.game.pop_scene()
            return
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(run.party)
                self.game.audio.play("menu")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(run.party)
                self.game.audio.play("menu")
            elif event.key == pygame.K_ESCAPE:
                self.game.pop_scene()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.on_pick:
                    self.on_pick(self.selected)
                elif self.game.adventure:
                    self.game.adventure.active_index = self.selected
                    self.game.save_adventure()
                self.game.pop_scene()

    def draw(self, surface: pygame.Surface) -> None:
        run = self.game.run or self.game.adventure
        if run is None:
            return
        shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 160))
        surface.blit(shade, (0, 0))
        panel = pygame.Rect(44, 28, 296, 160)
        draw_window(surface, panel)
        draw_text(surface, self.big, "PARTY", (panel.centerx, panel.y + 12), COLORS["cream"], align="center")
        for idx, unit in enumerate(run.party):
            row = pygame.Rect(panel.x + 14, panel.y + 38 + idx * 18, panel.width - 28, 16)
            draw_choice_box(surface, row, selected=idx == self.selected, dim=unit.is_down())
            draw_text(surface, self.small, ellipsize_text(self.small, unit.name, 102), (row.x + 8, row.y + 8), COLORS["cream"], align="midleft")
            draw_text(surface, self.small, f"Lv {unit.level}", (row.x + 118, row.y + 8), COLORS["stroke"], align="midleft")
            draw_text(surface, self.small, f"{unit.hp}/{unit.max_hp()}", (row.right - 8, row.y + 8), COLORS["gold"], align="midright")


class RewardScene(Scene):
    def __init__(self, game: Game, outcome: str, captured_key: str = ""):
        super().__init__(game)
        self.outcome = outcome
        self.captured_key = captured_key
        self.selected = 0
        self.rewards = self._build_rewards()

    def _build_rewards(self) -> List[dict]:
        run = self.game.run
        if run is None:
            return []
        rewards = [
            {"name": "+2 Capsules", "desc": "More capture ammo.", "kind": "capsules"},
            {"name": "+1 Tonic", "desc": "Patch team mid-run.", "kind": "tonic"},
            {"name": "Heal Party", "desc": "Top everyone off.", "kind": "heal"},
            {"name": "Lead +1", "desc": "Boost active brainrot.", "kind": "level"},
            {"name": "+25 Cash", "desc": "Plain safe payout.", "kind": "cash"},
        ]
        if run.current_enemy and len(run.party) < 6:
            rewards.insert(2, {"name": "Recruit Enemy", "desc": run.current_enemy.name, "kind": "recruit"})
        return rewards[:3]

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected = (self.selected - 1) % len(self.rewards)
                self.game.audio.play("menu")
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected = (self.selected + 1) % len(self.rewards)
                self.game.audio.play("menu")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.apply_reward()

    def apply_reward(self) -> None:
        run = self.game.run
        if run is None:
            self.game.replace_scene(TitleScene(self.game))
            return
        reward = self.rewards[self.selected]
        kind = reward["kind"]
        if kind == "capsules":
            run.inventory["Pasta Capsule"] = run.inventory.get("Pasta Capsule", 0) + 2
        elif kind == "tonic":
            run.inventory["Tomato Tonic"] = run.inventory.get("Tomato Tonic", 0) + 1
        elif kind == "heal":
            run.heal_party_full()
        elif kind == "level":
            run.active_creature().level += 1
            run.active_creature().heal_full()
        elif kind == "cash":
            run.money += 25
        elif kind == "recruit" and run.current_enemy:
            run.add_creature(run.current_enemy.key, run.current_enemy.level)
            self.game.profile.unlock(run.current_enemy.key)
        run.last_reward = reward["name"]
        run.current_enemy = None
        run.wave += 1
        self.game.save_bundle()
        self.game.save_run()
        self.game.replace_scene(BattleScene(self.game))

    def draw(self, surface: pygame.Surface) -> None:
        draw_backdrop(surface)
        draw_text(surface, self.big, "PICK REWARD", (18, 18), COLORS["cream"])
        subtitle = "Captured clean." if self.outcome == "captured" else "Wave cleared."
        draw_text(surface, self.small, subtitle, (18, 36), COLORS["stroke_dim"])
        for idx, reward in enumerate(self.rewards):
            rect = pygame.Rect(18 + idx * 116, 60, 100, 124)
            card = self.game.assets.get_runtime("reward_card").copy()
            surface.blit(card, rect)
            if idx == self.selected:
                pygame.draw.rect(surface, COLORS["gold"], rect.inflate(4, 4), 2, border_radius=12)
            draw_text(surface, self.font, reward["name"], (rect.centerx, rect.y + 18), COLORS["cream"], align="center")
            lines = wrap_text(self.small, reward["desc"], 74)
            for line_idx, line in enumerate(lines[:4]):
                draw_text(surface, self.small, line, (rect.centerx, rect.y + 50 + line_idx * 12), COLORS["stroke"], align="center")


class GameOverScene(Scene):
    def __init__(self, game: Game, wave: int, wins: int):
        super().__init__(game)
        self.wave = wave
        self.wins = wins

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                self.game.replace_scene(TitleScene(self.game))

    def draw(self, surface: pygame.Surface) -> None:
        draw_backdrop(surface)
        panel = pygame.Rect(74, 54, 236, 96)
        draw_window(surface, panel)
        draw_text(surface, self.big, "RUN OVER", (panel.centerx, panel.y + 18), COLORS["red"], align="center")
        draw_text(surface, self.font, f"Wave {self.wave}", (panel.centerx, panel.y + 48), COLORS["cream"], align="center")
        draw_text(surface, self.font, f"Wins {self.wins}", (panel.centerx, panel.y + 66), COLORS["gold"], align="center")
        draw_text(surface, self.small, "Enter back to title", (panel.centerx, panel.bottom - 12), COLORS["stroke_dim"], align="center")


class BattleScene(Scene):
    def __init__(self, game: Game):
        super().__init__(game)
        if self.game.run is None:
            raise ValueError("BattleScene needs active run")
        self.session = BattleSession(self.game.run)
        self.run = self.game.run
        self.game.profile.mark_seen(self.run.current_enemy.key)
        self.game.save_bundle()
        self.command_labels = ["Fight", "Guard", "Item", "Party", "Run"]
        self.command_icons = {
            "Fight": "attack",
            "Guard": "defend",
            "Item": "item",
            "Party": "special",
            "Run": "run",
        }
        self.mode = "command"
        self.selected = 0
        self.queue: List[BattleEvent] = [
            BattleEvent("message", f"Wave {self.run.wave}. {self.run.current_enemy.name} stepped in.", duration=0.6)
        ]
        self.queue_timer = 0.0
        self.current_event: Optional[BattleEvent] = None
        self.pending_outcome = ""
        self.t = 0.0
        self.message = ""
        self.move_selected = 0
        self.item_selected = 0
        self.current_event_time = 0.0
        self.current_event_duration = 0.0

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        if self.queue or self.current_event:
            return
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if self.mode == "command":
                self._handle_command(event.key)
            elif self.mode == "moves":
                self._handle_moves(event.key)
            elif self.mode == "items":
                self._handle_items(event.key)

    def _handle_command(self, key: int) -> None:
        if key in (pygame.K_LEFT, pygame.K_a):
            self.selected = (self.selected - 1) % len(self.command_labels)
            self.game.audio.play("menu")
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.selected = (self.selected + 1) % len(self.command_labels)
            self.game.audio.play("menu")
        elif key in (pygame.K_UP, pygame.K_w):
            self.selected = (self.selected - 3) % len(self.command_labels)
            self.game.audio.play("menu")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.selected = (self.selected + 3) % len(self.command_labels)
            self.game.audio.play("menu")
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            choice = self.command_labels[self.selected]
            if choice == "Fight":
                self.mode = "moves"
                self.game.audio.play("menu")
            elif choice == "Guard":
                self._consume_result(self.session.guard(), "special")
            elif choice == "Item":
                self.mode = "items"
                self.game.audio.play("menu")
            elif choice == "Party":
                self.game.push_scene(PartyScene(self.game, on_pick=self._pick_party))
            else:
                self._consume_result(self.session.attempt_run(), "menu")

    def _handle_moves(self, key: int) -> None:
        moves = self.run.active_creature().creature.moves
        if key in (pygame.K_UP, pygame.K_w):
            self.move_selected = (self.move_selected - 1) % len(moves)
            self.game.audio.play("menu")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.move_selected = (self.move_selected + 1) % len(moves)
            self.game.audio.play("menu")
        elif key == pygame.K_ESCAPE:
            self.mode = "command"
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self._consume_result(self.session.use_move(self.move_selected), "attack")

    def _handle_items(self, key: int) -> None:
        items = ["Pasta Capsule", "Tomato Tonic", "Back"]
        if key in (pygame.K_UP, pygame.K_w):
            self.item_selected = (self.item_selected - 1) % len(items)
            self.game.audio.play("menu")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.item_selected = (self.item_selected + 1) % len(items)
            self.game.audio.play("menu")
        elif key == pygame.K_ESCAPE:
            self.mode = "command"
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            choice = items[self.item_selected]
            if choice == "Pasta Capsule":
                self._consume_result(self.session.throw_capsule(), "capture")
            elif choice == "Tomato Tonic":
                self._consume_result(self.session.use_tonic(), "special")
            else:
                self.mode = "command"

    def _pick_party(self, index: int) -> None:
        self._consume_result(self.session.switch_party(index), "menu")

    def _consume_result(self, result: BattleResult, sfx: str) -> None:
        self.game.audio.play(sfx)
        self.pending_outcome = result.outcome
        self.queue = list(result.events)
        self.current_event = None
        self.mode = "busy"
        self.game.save_run()

    def update(self, dt: float) -> None:
        self.t += dt
        if self.current_event is None and self.queue:
            self.current_event = self.queue.pop(0)
            speed = max(1, self.game.settings.text_speed)
            self.queue_timer = max(0.22, self.current_event.duration / speed)
            self.current_event_duration = self.queue_timer
            self.current_event_time = 0.0
            self.message = self.current_event.text
        elif self.current_event is not None:
            tick = dt * max(1, self.game.settings.battle_speed)
            self.current_event_time += tick
            self.queue_timer -= tick
            if self.queue_timer <= 0:
                self.current_event = None
                self.current_event_time = 0.0
                self.current_event_duration = 0.0
                if not self.queue:
                    self._finish_resolution()

    def _finish_resolution(self) -> None:
        outcome = self.pending_outcome
        self.pending_outcome = ""
        self.current_event = None
        if outcome in ("win", "captured"):
            self.run.wins += 1
            self.game.profile.total_wins += 1
            if outcome == "captured" and self.run.current_enemy:
                self.game.profile.unlock(self.run.current_enemy.key)
            self.game.save_bundle()
            self.game.save_run()
            self.game.replace_scene(RewardScene(self.game, outcome))
            return
        if outcome == "escaped":
            self.run.current_enemy = None
            self.run.wave += 1
            self.game.save_run()
            self.game.replace_scene(BattleScene(self.game))
            return
        if outcome == "loss":
            wave = self.run.wave
            wins = self.run.wins
            self.game.complete_run()
            self.game.replace_scene(GameOverScene(self.game, wave, wins))
            return
        self.mode = "command"

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.game.assets.get_runtime("battle_bg"), (0, 0))
        self._draw_field(surface)
        self._draw_status(surface)
        self._draw_command_box(surface)

    def _draw_field(self, surface: pygame.Surface) -> None:
        enemy_center = self._battle_center("enemy")
        player_center = self._battle_center("player")
        pygame.draw.ellipse(surface, COLORS["field_dark"], (248, 118, 84, 18))
        pygame.draw.ellipse(surface, COLORS["field_dark"], (48, 164, 108, 20))

        if self.game.assets.player_battle["idle"]:
            trainer = battle_anim_frame(self.game.assets.player_battle, "attack" if self._actor_anim("player") == "attack" else "idle", self.t)
            trainer = fit_sprite(trainer, 58, 58)
            surface.blit(trainer, (40, 146))

        enemy_phase = self._actor_anim("enemy")
        player_phase = self._actor_anim("player")
        enemy_time = self._actor_time("enemy")
        player_time = self._actor_time("player")
        enemy_move_key = self._actor_move_key("enemy")
        player_move_key = self._actor_move_key("player")
        enemy_attack_frames = self.game.assets.move_anim.get(enemy_move_key, {}).get("body", [])
        player_attack_frames = self.game.assets.move_anim.get(player_move_key, {}).get("body", [])
        enemy_attack_seq = MOVE_ANIM_MANIFEST.get(enemy_move_key, {}).get("body_seq")
        player_attack_seq = MOVE_ANIM_MANIFEST.get(player_move_key, {}).get("body_seq")
        event_progress = self._event_progress()
        draw_creature(
            surface,
            self.game.assets,
            self.run.current_enemy.key,
            enemy_center,
            enemy_phase,
            enemy_time,
            attack_frames=enemy_attack_frames,
            attack_sequence=enemy_attack_seq,
            attack_progress=event_progress,
            flip=creature_flip_for_actor(self.run.current_enemy.key, "enemy"),
            scale=1.0,
            stretch=self._actor_stretch("enemy"),
            shake=self._target_hit("enemy"),
            idle_on=self.game.settings.idle_on,
            battle_variant="enemy",
        )
        draw_creature(
            surface,
            self.game.assets,
            self.run.active_creature().key,
            player_center,
            player_phase,
            player_time,
            attack_frames=player_attack_frames,
            attack_sequence=player_attack_seq,
            attack_progress=event_progress,
            flip=creature_flip_for_actor(self.run.active_creature().key, "player"),
            scale=0.9,
            stretch=self._actor_stretch("player"),
            shake=self._target_hit("player"),
            idle_on=self.game.settings.idle_on,
            battle_variant="player",
        )
        self._draw_fx(surface)

    def _draw_status(self, surface: pygame.Surface) -> None:
        enemy = self.run.current_enemy
        player = self.run.active_creature()
        enemy_box = self.game.assets.get_runtime("stat_box")
        player_box = self.game.assets.get_runtime("stat_box")
        surface.blit(enemy_box, (18, 16))
        surface.blit(player_box, (240, 138))
        draw_text(surface, self.small, ellipsize_text(self.small, enemy.name, 102), (28, 24), COLORS["ink"], shadow=False)
        draw_text(surface, self.small, f"Lv {enemy.level}", (134, 24), COLORS["blue"], align="topright", shadow=False)
        draw_text(surface, self.small, ellipsize_text(self.small, player.name, 102), (250, 146), COLORS["ink"], shadow=False)
        draw_text(surface, self.small, f"Lv {player.level}", (356, 146), COLORS["blue"], align="topright", shadow=False)
        draw_meter(surface, pygame.Rect(28, 40, 102, 8), enemy.hp / max(1, enemy.max_hp()), hp_color(enemy), back=COLORS["panel"])
        draw_meter(surface, pygame.Rect(250, 162, 102, 8), player.hp / max(1, player.max_hp()), hp_color(player), back=COLORS["panel"])
        draw_text(surface, self.small, f"{player.hp}/{player.max_hp()}", (356, 176), COLORS["stroke"], align="topright")
        draw_text(surface, self.small, f"Wave {self.run.wave}", (356, 16), COLORS["stroke"], align="topright")
        draw_text(surface, self.small, f"Caps {self.run.inventory.get('Pasta Capsule', 0)}  Tonics {self.run.inventory.get('Tomato Tonic', 0)}", (356, 30), COLORS["stroke_dim"], align="topright")

        for idx, unit in enumerate(self.run.party[:6]):
            color = COLORS["red"] if unit.is_down() else COLORS["gold"] if idx == self.run.active_index else COLORS["stroke"]
            pygame.draw.circle(surface, color, (22 + idx * 10, 206), 3)

    def _draw_command_box(self, surface: pygame.Surface) -> None:
        box = self.game.assets.get_runtime("command_box")
        surface.blit(box, (6, 146))
        text_x = 18
        text_y = 156
        active = self.run.active_creature()
        prompts = (
            f"{active.name} is vibrating.",
            f"{active.name} has locked in.",
            f"{active.name} chose chaos.",
            f"{active.name} waits for your nonsense.",
        )
        prompt = self.message if (self.current_event or self.queue) else prompts[(self.run.wave + self.run.wins + len(active.name)) % len(prompts)]
        lines = wrap_text(self.small, prompt, 176)
        for idx, line in enumerate(lines[:3]):
            draw_text(surface, self.small, line, (text_x, text_y + idx * 12), COLORS["ink"], shadow=False)

        if self.current_event or self.queue:
            return
        if self.mode == "command":
            self._draw_command_menu(surface)
        elif self.mode == "moves":
            self._draw_move_menu(surface)
        elif self.mode == "items":
            self._draw_item_menu(surface)

    def _draw_command_menu(self, surface: pygame.Surface) -> None:
        origin_x = 220
        origin_y = 154
        for idx, label in enumerate(self.command_labels):
            col = idx % 2
            row = idx // 2
            rect = pygame.Rect(origin_x + col * 74, origin_y + row * 18, 68, 16)
            draw_choice_box(surface, rect, selected=idx == self.selected)
            icon_key = self.command_icons.get(label)
            if icon_key and icon_key in self.game.assets.ui:
                icon = fit_sprite(self.game.assets.ui[icon_key], 12, 12)
                surface.blit(icon, (rect.x + 5, rect.y + 2))
        draw_text(surface, self.small, label, (rect.x + 22, rect.y + 8), COLORS["ink"], align="midleft", shadow=False)

    def _draw_move_menu(self, surface: pygame.Surface) -> None:
        moves = self.run.active_creature().creature.moves
        for idx, move in enumerate(moves):
            rect = pygame.Rect(214, 152 + idx * 14, 146, 12)
            draw_choice_box(surface, rect, selected=idx == self.move_selected)
            draw_text(surface, self.small, move.name, (rect.x + 6, rect.y + 6), COLORS["ink"], align="midleft", shadow=False)
        move = moves[self.move_selected]
        draw_text(surface, self.small, f"PWR {move.power}  ACC {move.accuracy}", (214, 210), COLORS["blue"], shadow=False)

    def _draw_item_menu(self, surface: pygame.Surface) -> None:
        items = [
            f"Pasta Capsule x{self.run.inventory.get('Pasta Capsule', 0)}",
            f"Tomato Tonic x{self.run.inventory.get('Tomato Tonic', 0)}",
            "Back",
        ]
        for idx, label in enumerate(items):
            rect = pygame.Rect(214, 152 + idx * 16, 146, 14)
            draw_choice_box(surface, rect, selected=idx == self.item_selected)
            draw_text(surface, self.small, label, (rect.x + 6, rect.y + 7), COLORS["ink"], align="midleft", shadow=False)

    def _actor_anim(self, actor: str) -> str:
        event = self.current_event
        if event and event.kind in ("attack", "switch") and event.actor == actor:
            return "attack"
        return "idle"

    def _target_hit(self, actor: str) -> float:
        event = self.current_event
        if event and event.kind == "hit" and event.target == actor:
            return math.sin(self._event_progress() * math.pi)
        return 0.0

    def _actor_move_key(self, actor: str) -> str:
        event = self.current_event
        if not event or event.actor != actor or event.kind != "attack":
            return ""
        return event.effect

    def _actor_time(self, actor: str) -> float:
        event = self.current_event
        if event and event.kind in ("attack", "switch") and event.actor == actor:
            return self._event_progress() * 0.5
        return self.t

    def _event_progress(self) -> float:
        if not self.current_event_duration:
            return 0.0
        return max(0.0, min(1.0, self.current_event_time / self.current_event_duration))

    def _battle_center(self, actor: str) -> Tuple[int, int]:
        base_x, base_y = self._battle_anchor(actor)
        off_x, off_y = self._actor_offset(actor)
        return base_x + off_x, base_y + off_y

    def _battle_anchor(self, actor: str) -> Tuple[int, int]:
        return (292, 78) if actor == "enemy" else (104, 124)

    def _contact_lunge(self, actor: str, progress: float, stop_distance: float, arc: float = 0.0) -> Tuple[int, int]:
        target_actor = "enemy" if actor == "player" else "player"
        start_x, start_y = self._battle_anchor(actor)
        end_x, end_y = self._battle_anchor(target_actor)
        dx = end_x - start_x
        dy = end_y - start_y
        length = math.hypot(dx, dy) or 1.0
        nx = dx / length
        ny = dy / length
        wave = math.sin(progress * math.pi)
        # Contact attacks should get close to the target, not stop at a tiny fixed offset.
        # The numeric tuning passed by each move is treated as the remaining gap at peak lunge.
        travel = max(0.0, length - stop_distance) * wave
        return (
            int(nx * travel),
            int(ny * travel - arc * wave),
        )

    def _actor_offset(self, actor: str) -> Tuple[int, int]:
        event = self.current_event
        if not event or event.actor != actor or event.kind not in ("attack", "switch"):
            return (0, 0)
        if event.kind == "switch":
            wave = math.sin(self._event_progress() * math.pi)
            return ((-16 if actor == "player" else 16), int(-6 * wave))
        visual = MOVE_VISUALS.get(event.effect)
        if not visual:
            return (0, 0)
        p = self._event_progress()
        if visual.motion == "jab":
            return self._contact_lunge(actor, p, 48, arc=2)
        if visual.motion == "whip":
            if p < 0.35:
                back = math.sin((p / 0.35) * math.pi * 0.5)
                target_actor = "enemy" if actor == "player" else "player"
                start_x, start_y = self._battle_anchor(actor)
                end_x, end_y = self._battle_anchor(target_actor)
                dx = start_x - end_x
                dy = start_y - end_y
                length = math.hypot(dx, dy) or 1.0
                return (int((dx / length) * 18 * back), int((dy / length) * 18 * back))
            dash = math.sin(((p - 0.35) / 0.65) * math.pi)
            return self._contact_lunge(actor, dash, 50, arc=4)
        if visual.motion == "slam":
            wave = math.sin(p * math.pi)
            lx, ly = self._contact_lunge(actor, p, 58)
            return (lx, ly - int(20 * wave))
        if visual.motion == "toss":
            sign = 1 if actor == "player" else -1
            arc = math.sin(p * math.pi)
            return (int(24 * arc * sign), int(-10 * arc))
        if visual.motion == "drum_hit":
            beat = abs(math.sin(p * math.pi * 2.0))
            lx, ly = self._contact_lunge(actor, p, 44)
            return (lx, ly - int(4 * beat))
        if visual.motion == "beat":
            sign = 1 if actor == "player" else -1
            pulse = math.sin(p * math.pi)
            return (int(22 * pulse * sign), int(-8 * pulse))
        if visual.motion == "roll":
            wave = math.sin(p * math.pi * 2.5)
            lx, ly = self._contact_lunge(actor, p, 60)
            return (lx, ly + int(6 * wave))
        if visual.motion == "march":
            pulse = math.sin(p * math.pi * 3.0)
            lx, ly = self._contact_lunge(actor, p, 42)
            return (lx, ly + int(5 * abs(pulse) - 2))
        if visual.motion == "spin":
            wave = math.sin(p * math.pi)
            lx, ly = self._contact_lunge(actor, p, 40)
            return (lx, ly + int(6 * math.sin(p * math.tau)) - int(2 * wave))
        if visual.motion == "ribbon":
            lx, ly = self._contact_lunge(actor, p, 36)
            return (lx, ly - int(6 * math.sin(p * math.pi * 2.0)))
        if visual.motion == "arabesque":
            wave = math.sin(p * math.pi)
            lx, ly = self._contact_lunge(actor, p, 52)
            return (lx, ly - int(13 * wave))
        if visual.motion == "finale":
            wave = math.sin(p * math.pi)
            lx, ly = self._contact_lunge(actor, p, 34)
            return (lx, ly - int(14 * wave))
        return (0, 0)

    def _actor_stretch(self, actor: str) -> Tuple[float, float]:
        event = self.current_event
        if not event or event.actor != actor or event.kind not in ("attack", "switch"):
            return (1.0, 1.0)
        if event.kind == "switch":
            wave = math.sin(self._event_progress() * math.pi)
            return (1.0 + 0.06 * wave, 1.0 - 0.04 * wave)
        visual = MOVE_VISUALS.get(event.effect)
        if not visual:
            return (1.0, 1.0)
        p = self._event_progress()
        pulse = math.sin(p * math.pi)
        if visual.motion == "jab":
            return (1.0 + 0.18 * pulse, 1.0 - 0.10 * pulse)
        if visual.motion == "whip":
            return (1.0 + 0.22 * pulse, 1.0 - 0.12 * pulse)
        if visual.motion == "slam":
            return (1.0 - 0.12 * pulse, 1.0 + 0.18 * pulse)
        if visual.motion == "toss":
            return (1.0 - 0.08 * pulse, 1.0 + 0.12 * pulse)
        if visual.motion == "drum_hit":
            return (1.0 + 0.10 * pulse, 1.0 - 0.08 * pulse)
        if visual.motion == "beat":
            return (1.0 + 0.14 * pulse, 1.0 - 0.10 * pulse)
        if visual.motion == "roll":
            return (1.0 + 0.20 * pulse, 1.0 - 0.14 * pulse)
        if visual.motion == "march":
            return (1.0 + 0.10 * abs(math.sin(p * math.pi * 2.0)), 1.0 - 0.06 * pulse)
        if visual.motion == "spin":
            return (1.0 - 0.10 * pulse, 1.0 + 0.10 * pulse)
        if visual.motion == "ribbon":
            return (1.0 + 0.06 * pulse, 1.0 + 0.04 * pulse)
        if visual.motion == "arabesque":
            return (1.0 - 0.10 * pulse, 1.0 + 0.16 * pulse)
        if visual.motion == "finale":
            return (1.0 + 0.16 * pulse, 1.0 + 0.06 * pulse)
        return (1.0, 1.0)

    def _draw_fx(self, surface: pygame.Surface) -> None:
        event = self.current_event
        if not event:
            return
        if event.effect in MOVE_VISUALS and event.kind in ("attack", "hit"):
            self._draw_move_fx(surface, event)
            return
        if event.effect not in self.game.assets.fx:
            return
        fx = fit_sprite(self.game.assets.fx[event.effect], 42, 42)
        if event.kind == "capture":
            pos = (214, 80)
        elif event.target == "enemy":
            pos = (264, 66)
        else:
            pos = (92, 122)
        surface.blit(fx, fx.get_rect(center=pos))

    def _draw_move_fx(self, surface: pygame.Surface, event: BattleEvent) -> None:
        visual = MOVE_VISUALS.get(event.effect)
        if not visual:
            return
        p = self._event_progress()
        start = self._battle_center(event.actor)
        target_actor = event.target or ("enemy" if event.actor == "player" else "player")
        end = self._battle_center(target_actor)
        actor_key = self.run.current_enemy.key if event.actor == "enemy" else self.run.active_creature().key
        move_anim = self.game.assets.move_anim.get(event.effect, {})
        config = MOVE_ANIM_MANIFEST.get(event.effect, {})
        if event.kind == "attack":
            if move_anim.get("projectile"):
                delay = config.get("projectile_delay", 0.15)
                travel_p = max(0.0, min(1.0, (p - delay) / max(0.001, 1.0 - delay)))
                pos = projectile_point(start, end, travel_p, visual.projectile)
                self._draw_move_phase(
                    surface,
                    move_anim.get("projectile", []),
                    pos,
                    travel_p,
                    config.get("projectile_size", 76),
                    config.get("projectile_seq"),
                )
            else:
                self._draw_projectile_trail(surface, visual, start, end, p, fallback_only=True)
        else:
            if move_anim.get("effect"):
                self._draw_move_phase(
                    surface,
                    move_anim.get("effect", []),
                    end,
                    p,
                    config.get("effect_size", 78),
                    config.get("effect_seq"),
                )
            else:
                self._draw_impact(surface, visual, end, p)

    def _draw_move_phase(
        self,
        surface: pygame.Surface,
        frames: List[pygame.Surface],
        center: Tuple[int, int],
        progress: float,
        size: int,
        sequence: Optional[List[int]] = None,
        flip: bool = False,
    ) -> None:
        if not frames:
            return
        frame = seq_frame(frames, progress, sequence)
        sprite = fit_sprite(frame, size, size)
        if flip:
            sprite = pygame.transform.flip(sprite, True, False)
        surface.blit(sprite, sprite.get_rect(center=center))

    def _draw_projectile_trail(
        self,
        surface: pygame.Surface,
        visual: MoveVisual,
        start: Tuple[int, int],
        end: Tuple[int, int],
        p: float,
        fallback_only: bool = False,
    ) -> None:
        if visual.projectile == "none":
            if not fallback_only:
                ring = int(8 + 24 * math.sin(p * math.pi))
                pygame.draw.circle(surface, visual.accent, end, ring, 2)
            return
        if visual.projectile == "sound_ring":
            radius = int(6 + 26 * p)
            pygame.draw.circle(surface, visual.color, start, radius, 2)
            pygame.draw.circle(surface, visual.accent, start, max(1, radius - 6), 1)
            return
        if visual.projectile == "step_wave":
            for idx in range(4):
                foot_p = max(0.0, p - idx * 0.12)
                foot_x, foot_y = projectile_point(start, end, foot_p, "step_wave")
                pygame.draw.ellipse(surface, visual.color, (foot_x - 5, foot_y - 2 + (idx % 2) * 2, 10, 4), 1)
            return
        if fallback_only:
            return
        for idx in range(3):
            tail_p = max(0.0, p - idx * 0.10)
            tail_x, tail_y = projectile_point(start, end, tail_p, visual.projectile)
            pygame.draw.circle(surface, visual.accent, (tail_x, tail_y), max(1, 4 - idx), 1)

    def _draw_impact(self, surface: pygame.Surface, visual: MoveVisual, center: Tuple[int, int], p: float) -> None:
        radius = int(10 + 18 * math.sin(p * math.pi))
        pygame.draw.circle(surface, visual.accent, center, radius, 2)
        pygame.draw.circle(surface, visual.color, center, max(4, radius // 2), 1)
        for idx in range(6):
            angle = math.tau * idx / 6.0 + p * 0.6
            dist = 8 + int(14 * p)
            px = center[0] + int(math.cos(angle) * dist)
            py = center[1] + int(math.sin(angle) * dist)
            pygame.draw.line(surface, visual.color, center, (px, py), 1)
        sprite = self.game.assets.fx.get(visual.sprite)
        if sprite:
            fx = fit_sprite(sprite, 44, 44)
            surface.blit(fx, fx.get_rect(center=center))


def hp_color(unit: CreatureInstance):
    ratio = unit.hp / max(1, unit.max_hp())
    if ratio > 0.5:
        return COLORS["green"]
    if ratio > 0.2:
        return COLORS["gold"]
    return COLORS["red"]


def battle_anim_frame(frames: dict, phase: str, t: float) -> pygame.Surface:
    seq = frames.get(phase) or frames.get("idle") or []
    if not seq:
        return pygame.Surface((1, 1), pygame.SRCALPHA)
    idx = int(t * 4) % len(seq)
    return seq[idx]


def fit_sprite(image: pygame.Surface, max_w: int, max_h: int) -> pygame.Surface:
    width, height = image.get_size()
    if width <= 0 or height <= 0:
        return image
    scale = min(max_w / width, max_h / height)
    scale = max(scale, 0.1)
    size = (max(1, int(width * scale)), max(1, int(height * scale)))
    return pygame.transform.scale(image, size)


def anim_frame(assets: AssetStore, key: str, phase: str, t: float, idle_on: bool = True) -> pygame.Surface:
    bucket = assets.creature_anim.get(key, {})
    if phase == "attack" and bucket.get("attack"):
        frames = bucket["attack"]
        idx = min(len(frames) - 1, int((t % 0.5) * len(frames) / 0.5))
        return frames[idx]
    frames = bucket.get("idle") or [assets.creatures[key]]
    if not idle_on or len(frames) == 1:
        return frames[0]
    manifest = IDLE_MANIFEST.get(key, {"fps": 4.0, "sequence": list(range(len(frames)))})
    seq = manifest["sequence"]
    fps = manifest.get("fps", 4.0)
    idx = seq[int(t * fps) % len(seq)]
    idx = min(idx, len(frames) - 1)
    return frames[idx]


def battle_idle_frame(
    assets: AssetStore,
    key: str,
    variant: str,
    t: float,
    idle_on: bool = True,
) -> pygame.Surface:
    bucket = assets.creature_battle.get(key, {})
    frames = bucket.get(variant) or bucket.get("enemy") or []
    if not frames:
        return anim_frame(assets, key, "idle", t, idle_on=idle_on)
    if not idle_on or len(frames) == 1:
        return frames[0]
    manifest = IDLE_MANIFEST.get(key, {"fps": 4.0, "sequence": list(range(len(frames)))})
    seq = manifest["sequence"]
    fps = manifest.get("fps", 4.0)
    idx = seq[int(t * fps) % len(seq)]
    idx = min(idx, len(frames) - 1)
    return frames[idx]


def draw_creature(
    surface: pygame.Surface,
    assets: AssetStore,
    key: str,
    center,
    phase: str,
    t: float,
    attack_frames: Optional[List[pygame.Surface]] = None,
    attack_sequence: Optional[List[int]] = None,
    attack_progress: float = 0.0,
    flip: bool = False,
    scale: float = 1.0,
    stretch: Tuple[float, float] = (1.0, 1.0),
    shake: float = 0.0,
    idle_on: bool = True,
    battle_variant: Optional[str] = None,
) -> None:
    if phase == "attack" and attack_frames:
        sprite = seq_frame(attack_frames, attack_progress, attack_sequence)
    elif battle_variant:
        sprite = battle_idle_frame(assets, key, battle_variant, t, idle_on=idle_on)
    else:
        sprite = anim_frame(assets, key, phase, t, idle_on=idle_on)
    if not battle_variant or phase == "attack":
        max_w = int(108 * scale)
        max_h = int(92 * scale)
        sprite = fit_sprite(sprite, max_w, max_h)
    if stretch != (1.0, 1.0):
        sprite = pygame.transform.scale(
            sprite,
            (
                max(1, int(sprite.get_width() * stretch[0])),
                max(1, int(sprite.get_height() * stretch[1])),
            ),
        )
    if flip:
        sprite = pygame.transform.flip(sprite, True, False)
    x, y = center
    if shake:
        x += int(math.sin(t * 80) * 2)
    surface.blit(sprite, sprite.get_rect(center=(x, y)))


def projectile_point(
    start: Tuple[int, int],
    end: Tuple[int, int],
    progress: float,
    shape: str,
) -> Tuple[int, int]:
    p = max(0.0, min(1.0, progress))
    x = start[0] + (end[0] - start[0]) * p
    y = start[1] + (end[1] - start[1]) * p
    if shape in ("sauce_arc", "coffee_arc", "roast_arc"):
        y -= math.sin(p * math.pi) * 24
    elif shape == "meatball":
        y -= math.sin(p * math.pi) * 18
        x += math.sin(p * math.pi * 3.0) * 5
    elif shape == "drum_spin":
        y += math.sin(p * math.pi * 4.0) * 5
    elif shape == "step_wave":
        y += math.sin(p * math.pi * 6.0) * 3
    elif shape == "foam_ribbon":
        y += math.sin(p * math.pi * 2.0) * 10
    elif shape == "froth_bloom":
        y -= math.sin(p * math.pi) * 10
    return int(x), int(y)


def midpoint(a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[int, int]:
    return ((a[0] + b[0]) // 2, (a[1] + b[1]) // 2)


def seq_frame(
    frames: List[pygame.Surface],
    progress: float,
    sequence: Optional[List[int]] = None,
) -> pygame.Surface:
    if not frames:
        return pygame.Surface((1, 1), pygame.SRCALPHA)
    seq = sequence or list(range(len(frames)))
    index = min(len(seq) - 1, int(max(0.0, min(0.999, progress)) * len(seq)))
    frame_index = min(len(frames) - 1, seq[index])
    return frames[frame_index]


def draw_battle_bg(surface: pygame.Surface, t: float) -> None:
    draw_backdrop(surface)
    sky_rect = pygame.Rect(0, 0, surface.get_width(), 116)
    for y in range(sky_rect.height):
        blend = y / max(1, sky_rect.height - 1)
        color = (
            int(COLORS["sky"][0] * (1 - blend) + COLORS["bg_top"][0] * blend),
            int(COLORS["sky"][1] * (1 - blend) + COLORS["bg_top"][1] * blend),
            int(COLORS["sky"][2] * (1 - blend) + COLORS["bg_top"][2] * blend),
        )
        pygame.draw.line(surface, color, (0, y), (surface.get_width(), y))
    for idx in range(4):
        cloud_x = 24 + idx * 92 + int((t * 8 + idx * 9) % 18)
        cloud_y = 24 + (idx % 2) * 16
        pygame.draw.ellipse(surface, COLORS["cloud"], (cloud_x, cloud_y, 44, 14))
    pygame.draw.rect(surface, COLORS["sand"], (0, 118, surface.get_width(), 20))
    pygame.draw.rect(surface, COLORS["field_mid"], (0, 138, surface.get_width(), 78))
    for x in range(0, surface.get_width(), 16):
        pygame.draw.line(surface, COLORS["field_light"], (x, 160), (x + 8, 216), 1)


class CharacterCreatorScene(Scene):
    def __init__(self, game: Game, slot: int):
        super().__init__(game)
        self.slot = slot
        self.name = "ARAV"
        self.cursor = 0
        self.appearance = PlayerAppearance()
        self.fields = ["Name", "Body", "Skin", "Hair", "Outfit", "Accent", "Accessory", "Begin"]
        self.limits = {"Body": 2, "Skin": 4, "Hair": 5, "Outfit": 5, "Accent": 5, "Accessory": 4}

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            field = self.fields[self.cursor]
            if event.key in (pygame.K_UP, pygame.K_w):
                self.cursor = (self.cursor - 1) % len(self.fields)
                self.game.audio.play("menu")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.cursor = (self.cursor + 1) % len(self.fields)
                self.game.audio.play("menu")
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self._bump(field, -1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._bump(field, 1)
            elif event.key == pygame.K_BACKSPACE and field == "Name":
                self.name = self.name[:-1] or "A"
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if field == "Begin":
                    self.game.replace_scene(StarterPickScene(self.game, self.slot, self.name, self.appearance))
                else:
                    self._bump(field, 1)
            elif field == "Name" and event.unicode and event.unicode.isalnum() and len(self.name) < 10:
                if self.name == "ARAV":
                    self.name = ""
                self.name += event.unicode.upper()

    def _bump(self, field: str, amount: int) -> None:
        attr = field.lower()
        if field not in self.limits:
            return
        current = getattr(self.appearance, attr)
        setattr(self.appearance, attr, (current + amount) % self.limits[field])
        self.game.audio.play("menu")

    def draw(self, surface: pygame.Surface) -> None:
        draw_backdrop(surface)
        draw_text(surface, self.big, "CREATE TRAINER", (18, 16), COLORS["cream"])
        draw_text(surface, self.small, "Rotria Gear profile", (18, 36), COLORS["signal"])
        panel = pygame.Rect(18, 54, 174, 140)
        draw_window(surface, panel)
        values = [
            self.name,
            str(self.appearance.body + 1),
            str(self.appearance.skin + 1),
            str(self.appearance.hair + 1),
            str(self.appearance.outfit + 1),
            str(self.appearance.accent + 1),
            str(self.appearance.accessory + 1),
            "Choose starter",
        ]
        for idx, (label, value) in enumerate(zip(self.fields, values)):
            row = pygame.Rect(panel.x + 8, panel.y + 8 + idx * 16, panel.width - 16, 14)
            draw_choice_box(surface, row, selected=idx == self.cursor)
            draw_text(surface, self.small, label, (row.x + 12, row.y + 7), COLORS["cream"], align="midleft")
            draw_text(surface, self.small, value, (row.right - 6, row.y + 7), COLORS["gold"], align="midright")
        draw_trainer_sprite(surface, self.appearance, (292, 116), scale=4)
        draw_text(surface, self.small, "Type name. Arrows tune look. Enter confirms.", (18, 205), COLORS["stroke_dim"])


class StarterPickScene(Scene):
    def __init__(self, game: Game, slot: int, name: str, appearance: PlayerAppearance):
        super().__init__(game)
        self.slot = slot
        self.name = name
        self.appearance = appearance
        self.selected = 0
        self.t = 0.0

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected = (self.selected - 1) % len(STARTERS)
                self.game.audio.play("menu")
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected = (self.selected + 1) % len(STARTERS)
                self.game.audio.play("menu")
            elif event.key == pygame.K_ESCAPE:
                self.game.replace_scene(CharacterCreatorScene(self.game, self.slot))
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                starter_key = STARTERS[self.selected]
                self.game.begin_adventure(self.slot, self.name, self.appearance, starter_key)
                self.game.replace_scene(AdventureScene(self.game, intro=True))

    def update(self, dt: float) -> None:
        self.t += dt

    def draw(self, surface: pygame.Surface) -> None:
        draw_backdrop(surface)
        draw_text(surface, self.big, "CHOOSE PARTNER", (18, 16), COLORS["cream"])
        draw_text(surface, self.small, "Professor Menta watches the old radio blink.", (18, 36), COLORS["signal"])
        for idx, key in enumerate(STARTERS):
            rect = pygame.Rect(20 + idx * 118, 62, 104, 116)
            draw_window(surface, rect, fill=COLORS["panel_2"] if idx == self.selected else COLORS["panel"])
            if idx == self.selected:
                pygame.draw.rect(surface, COLORS["select"], rect.inflate(4, 4), 2)
            draw_creature(surface, self.game.assets, key, (rect.centerx, rect.y + 58), "idle", self.t, scale=0.68, idle_on=True)
            creature = CREATURES[key]
            draw_text(surface, self.small, creature.name, (rect.centerx, rect.bottom - 34), COLORS["cream"], align="center")
            draw_text(surface, self.small, creature.kind, (rect.centerx, rect.bottom - 19), COLORS["gold"], align="center")
        draw_text(surface, self.small, "Enter chooses. This starts the adventure.", (18, 205), COLORS["stroke_dim"])


class AdventureBattleScene(BattleScene):
    def __init__(self, game: Game):
        super().__init__(game)
        context = self.game.adventure_battle_context or {}
        kind = context.get("kind", "wild")
        name = context.get("trainer_name") or self.run.current_enemy.name
        if kind == "trainer":
            opening = f"{name} challenged you."
        elif kind == "leader":
            opening = f"Leader {name} guards a seal badge."
        elif kind == "boss":
            opening = f"{name} warped the signal."
        else:
            opening = f"Wild {self.run.current_enemy.name} appeared."
        self.queue = [BattleEvent("message", opening, duration=0.55)]

    def _handle_items(self, key: int) -> None:
        context = self.game.adventure_battle_context or {}
        if context.get("capture_allowed", True) is False:
            items = ["Pasta Capsule", "Tomato Tonic", "Back"]
            if key in (pygame.K_UP, pygame.K_w):
                self.item_selected = (self.item_selected - 1) % len(items)
                self.game.audio.play("menu")
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.item_selected = (self.item_selected + 1) % len(items)
                self.game.audio.play("menu")
            elif key == pygame.K_ESCAPE:
                self.mode = "command"
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                if items[self.item_selected] == "Pasta Capsule":
                    self.queue = [BattleEvent("message", "The Ancient Signal rejects capsules.", duration=0.4)]
                    self.pending_outcome = "ongoing"
                    self.mode = "busy"
                elif items[self.item_selected] == "Tomato Tonic":
                    self._consume_result(self.session.use_tonic(), "special")
                else:
                    self.mode = "command"
            return
        super()._handle_items(key)

    def _finish_resolution(self) -> None:
        if not self.game.adventure:
            super()._finish_resolution()
            return
        outcome = self.pending_outcome
        self.pending_outcome = ""
        self.current_event = None
        if outcome in ("", "ongoing"):
            self.mode = "command"
            return
        context = self.game.adventure_battle_context or {}
        adv = self.game.adventure
        adv.party = [unit.copy() for unit in self.run.party[:6]]
        adv.active_index = min(self.run.active_index, max(0, len(adv.party) - 1))
        adv.bag["pasta_capsule"] = self.run.inventory.get("Pasta Capsule", adv.bag.get("pasta_capsule", 0))
        adv.bag["tomato_tonic"] = self.run.inventory.get("Tomato Tonic", adv.bag.get("tomato_tonic", 0))
        for key in self.run.collection:
            adv.mark_seen(key)
        if outcome == "captured" and self.run.current_enemy:
            adv.mark_caught(self.run.current_enemy.key)
            if all(unit.key != self.run.current_enemy.key or unit.level != self.run.current_enemy.level for unit in adv.party + adv.boxes):
                adv.add_creature(self.run.current_enemy.key, self.run.current_enemy.level)
        if outcome in ("win", "captured"):
            self._apply_win_rewards(adv, context, outcome)
        elif outcome == "loss":
            adv.money = max(0, adv.money - max(20, adv.money // 8))
            adv.map_key = adv.spawn_map
            adv.x = adv.spawn_x
            adv.y = adv.spawn_y
            adv.heal_party_full()
            adv.last_message = "You blacked out and woke at the last healer."
        elif outcome == "escaped":
            adv.last_message = "You escaped cleanly."
        adv.normalize()
        self.game.run = None
        self.game.adventure_battle_context = None
        self.game.save_bundle()
        self.game.save_adventure()
        self.game.replace_scene(AdventureScene(self.game))

    def _apply_win_rewards(self, adv: AdventureState, context: dict, outcome: str) -> None:
        enemy = self.run.current_enemy
        if enemy:
            adv.mark_seen(enemy.key)
        kind = context.get("kind", "wild")
        reward = int(context.get("reward", 80 + (enemy.level if enemy else 1) * 12))
        if kind in ("trainer", "leader", "boss", "league"):
            adv.money += reward
        if context.get("trainer_id") and context["trainer_id"] not in adv.defeated_trainers:
            adv.defeated_trainers.append(context["trainer_id"])
        if context.get("visible_id"):
            adv.set_flag(f"visible_{context['visible_id']}")
        if context.get("story_flag"):
            adv.set_flag(context["story_flag"])
        if context.get("badge") and context["badge"] not in adv.badges:
            adv.badges.append(context["badge"])
            adv.story_chapter = max(adv.story_chapter, len(adv.badges))
            adv.quests["main"] = next_main_quest(adv)
        xp = int(context.get("xp", 12 + (enemy.level if enemy else 1) * 7))
        messages = grant_party_xp(adv, xp, active_only=kind == "wild")
        if messages:
            adv.last_message = " ".join(messages[:2])
        else:
            adv.last_message = "Battle won."


class AdventureScene(Scene):
    def __init__(self, game: Game, intro: bool = False):
        super().__init__(game)
        if self.game.adventure is None:
            raise ValueError("AdventureScene needs active adventure")
        self.dialog: List[str] = []
        self.menu: Optional[str] = None
        self.menu_index = 0
        self.shop_key = ""
        self.t = 0.0
        self.step_cooldown = 0.0
        self.map_zoom = 1.0
        self.map_pan = [0.0, 0.0]
        self.map_selected = 0
        if intro:
            self.dialog = [
                "Professor Menta: Rotria's towers are speaking again.",
                "Your badge quest is now more than sport. Listen, but do not obey the static.",
            ]
        elif self.game.adventure.last_message:
            self.dialog = [self.game.adventure.last_message]
            self.game.adventure.last_message = ""

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        adv = self.game.adventure
        if adv is None:
            return
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if self.dialog:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    self.dialog.pop(0)
                continue
            if self.menu == "region_map":
                self._handle_region_map_key(event.key)
                continue
            if self.menu:
                self._handle_menu_key(event.key)
                continue
            if event.key == pygame.K_m:
                self._open_region_map()
            elif event.key == pygame.K_b:
                self._open_menu("bag")
            elif event.key == pygame.K_d:
                self._open_menu("dex")
            elif event.key == pygame.K_q:
                self._open_menu("quests")
            elif event.key == pygame.K_j:
                self._open_menu("badges")
            elif event.key == pygame.K_p:
                self.game.push_scene(PartyScene(self.game))
            elif event.key in (pygame.K_ESCAPE, pygame.K_c):
                self.menu = "pause"
                self.menu_index = 0
                self.game.audio.play("menu")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._interact()
            elif event.key in (pygame.K_UP, pygame.K_w):
                self._try_move(0, -1, "up")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._try_move(0, 1, "down")
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self._try_move(-1, 0, "left")
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._try_move(1, 0, "right")

    def update(self, dt: float) -> None:
        self.t += dt
        self.step_cooldown = max(0.0, self.step_cooldown - dt)

    def _handle_menu_key(self, key: int) -> None:
        options = self._menu_options()
        if key in (pygame.K_ESCAPE, pygame.K_c):
            self.menu = None
            self.game.audio.play("menu")
        elif key in (pygame.K_UP, pygame.K_w):
            self.menu_index = (self.menu_index - 1) % len(options)
            self.game.audio.play("menu")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.menu_index = (self.menu_index + 1) % len(options)
            self.game.audio.play("menu")
        elif key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d) and self.menu == "shop":
            pass
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self._activate_menu(options[self.menu_index])

    def _handle_region_map_key(self, key: int) -> None:
        pois = self._poi_keys()
        if key in (pygame.K_ESCAPE, pygame.K_m, pygame.K_c):
            self.menu = None
            self.game.audio.play("menu")
        elif key in (pygame.K_EQUALS, pygame.K_PLUS):
            self.map_zoom = min(4.0, self.map_zoom + 0.25)
            self._clamp_map_pan()
        elif key in (pygame.K_MINUS, pygame.K_UNDERSCORE):
            self.map_zoom = max(1.0, self.map_zoom - 0.25)
            self._clamp_map_pan()
        elif key == pygame.K_r:
            self.map_zoom = 1.0
            self._center_region_map_on_player()
        elif key == pygame.K_TAB and pois:
            self.map_selected = (self.map_selected + 1) % len(pois)
            self._center_region_map_on_key(pois[self.map_selected])
        elif key in (pygame.K_LEFT, pygame.K_a):
            self.map_pan[0] -= 24
            self._clamp_map_pan()
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.map_pan[0] += 24
            self._clamp_map_pan()
        elif key in (pygame.K_UP, pygame.K_w):
            self.map_pan[1] -= 24
            self._clamp_map_pan()
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.map_pan[1] += 24
            self._clamp_map_pan()
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self._center_region_map_on_player()

    def _menu_options(self) -> List[str]:
        if self.menu == "bag":
            adv = self.game.adventure
            return [f"{ITEMS[key].name} x{amount}" for key, amount in adv.bag.items() if amount > 0] + ["Back"]
        if self.menu == "dex":
            adv = self.game.adventure
            return [f"Seen {len(adv.seen)} / Caught {len(adv.caught)}", "Habitat hints", "Back"]
        if self.menu == "quests":
            adv = self.game.adventure
            return [f"{name}: {text}" for name, text in adv.quests.items()] + ["Back"]
        if self.menu == "badges":
            adv = self.game.adventure
            return [badge if badge in adv.badges else "????" for badge in BADGES] + ["Back"]
        if self.menu == "map":
            return [MAPS[self.game.adventure.map_key].name, "Rotria route chain", "Back"]
        if self.menu == "shop":
            shop = self._current_shop()
            if not shop:
                return ["Back"]
            return [f"Buy {ITEMS[key].name} ${ITEMS[key].price}" for key in shop.items] + ["Back"]
        if self.menu == "storage":
            adv = self.game.adventure
            return [f"Party {len(adv.party)}/6", f"Box {len(adv.boxes)}", "Back"]
        return ["Party", "Bag", "Brainrotdex", "Quests", "Badges", "Map", "Save", "Settings", "Back"]

    def _activate_menu(self, option: str) -> None:
        adv = self.game.adventure
        if adv is None:
            return
        if option == "Back":
            self.menu = "pause" if self.menu != "pause" else None
            self.menu_index = 0
            return
        if self.menu == "pause":
            target = option.lower()
            if target == "party":
                self.game.push_scene(PartyScene(self.game))
                self.menu = None
            elif target == "settings":
                self.game.push_scene(SettingsScene(self.game))
                self.menu = None
            elif target == "save":
                self.game.save_adventure()
                self.dialog = ["Game saved to the Rotria Gear."]
                self.menu = None
            elif target == "map":
                self._open_region_map()
            else:
                self.menu = target if target != "brainrotdex" else "dex"
                self.menu_index = 0
        elif self.menu == "bag":
            key = self._bag_key_at(self.menu_index)
            if key:
                self._use_bag_item(key)
        elif self.menu == "shop":
            shop = self._current_shop()
            if not shop or self.menu_index >= len(shop.items):
                self.menu = None
                return
            item_key = shop.items[self.menu_index]
            item = ITEMS[item_key]
            if adv.money >= item.price:
                adv.money -= item.price
                adv.add_item(item_key)
                self.dialog = [f"Bought {item.name}."]
                self.game.save_adventure()
            else:
                self.dialog = ["Not enough cash."]

    def _bag_key_at(self, index: int) -> str:
        adv = self.game.adventure
        keys = [key for key, amount in adv.bag.items() if amount > 0]
        return keys[index] if 0 <= index < len(keys) else ""

    def _use_bag_item(self, key: str) -> None:
        adv = self.game.adventure
        item = ITEMS.get(key)
        if not adv or not item:
            return
        if item.kind in ("heal", "berry"):
            target = adv.active_creature()
            if adv.use_item(key):
                healed = target.heal(item.power or 12)
                self.dialog = [f"{target.name} restored {healed} HP."]
                self.game.save_adventure()
        elif item.kind == "held":
            target = adv.active_creature()
            if adv.use_item(key):
                target.held_item = key
                self.dialog = [f"{target.name} held {item.name}."]
                self.game.save_adventure()
        else:
            self.dialog = [item.desc]

    def _try_move(self, dx: int, dy: int, facing: str) -> None:
        adv = self.game.adventure
        if adv is None or self.step_cooldown > 0:
            return
        adv.facing = facing
        map_def = MAPS[adv.map_key]
        nx, ny = adv.x + dx, adv.y + dy
        if self._blocked(nx, ny):
            self.game.audio.play("hit")
            return
        adv.x, adv.y = nx, ny
        adv.steps += 1
        adv.clock_minutes = (adv.clock_minutes + 2) % (24 * 60)
        self.step_cooldown = 0.045
        self._check_warp()
        self._check_pickup(auto=True)
        self._check_trainer_sight()
        self._maybe_random_encounter(map_def)
        self.game.save_adventure()

    def _open_region_map(self) -> None:
        self.menu = "region_map"
        self.map_zoom = max(1.0, self.map_zoom)
        self._center_region_map_on_player()
        self.game.audio.play("menu")

    def _open_menu(self, menu: str) -> None:
        self.menu = menu
        self.menu_index = 0
        self.game.audio.play("menu")

    def _poi_keys(self) -> List[str]:
        return [key for key in MAPS if key in MAP_POIS]

    def _center_region_map_on_player(self) -> None:
        adv = self.game.adventure
        self._center_region_map_on_key(adv.map_key if adv else "starter_village")

    def _center_region_map_on_key(self, key: str) -> None:
        image = self.game.assets.get_adventure("rotria_map")
        if image.get_width() <= 1:
            self.map_pan = [0.0, 0.0]
            return
        px, py, _label = MAP_POIS.get(key, MAP_POIS["starter_village"])
        base = min(VIRTUAL_WIDTH / image.get_width(), VIRTUAL_HEIGHT / image.get_height())
        scaled_w = image.get_width() * base * self.map_zoom
        scaled_h = image.get_height() * base * self.map_zoom
        self.map_pan = [px * base * self.map_zoom - VIRTUAL_WIDTH / 2, py * base * self.map_zoom - VIRTUAL_HEIGHT / 2]
        self._clamp_map_pan(scaled_w, scaled_h)

    def _clamp_map_pan(self, scaled_w: Optional[float] = None, scaled_h: Optional[float] = None) -> None:
        image = self.game.assets.get_adventure("rotria_map")
        if image.get_width() <= 1:
            self.map_pan = [0.0, 0.0]
            return
        base = min(VIRTUAL_WIDTH / image.get_width(), VIRTUAL_HEIGHT / image.get_height())
        scaled_w = scaled_w if scaled_w is not None else image.get_width() * base * self.map_zoom
        scaled_h = scaled_h if scaled_h is not None else image.get_height() * base * self.map_zoom
        max_x = max(0.0, scaled_w - VIRTUAL_WIDTH)
        max_y = max(0.0, scaled_h - VIRTUAL_HEIGHT)
        self.map_pan[0] = max(0.0, min(max_x, self.map_pan[0]))
        self.map_pan[1] = max(0.0, min(max_y, self.map_pan[1]))

    def _blocked(self, x: int, y: int) -> bool:
        adv = self.game.adventure
        map_def = MAPS[adv.map_key]
        tile = map_def.tile_at(x, y)
        if tile in WATER_TILES:
            return "surfboard_pass" not in adv.bag
        if tile not in TILE_WALKABLE:
            return True
        for npc in map_def.npcs:
            if (npc.x, npc.y) == (x, y):
                return True
        for trainer in map_def.trainers:
            if trainer.key not in adv.defeated_trainers and (trainer.x, trainer.y) == (x, y):
                return True
        for visible in map_def.visibles:
            if not adv.has_flag(f"visible_{visible.key}") and (visible.x, visible.y) == (x, y):
                return True
        return False

    def _check_warp(self) -> None:
        adv = self.game.adventure
        map_def = MAPS[adv.map_key]
        for warp in map_def.warps:
            if (warp.x, warp.y) == (adv.x, adv.y):
                if warp.required_flag and not adv.has_flag(warp.required_flag):
                    self.dialog = ["The path is sealed by old static."]
                    return
                adv.map_key = warp.target_map
                adv.x = warp.target_x
                adv.y = warp.target_y
                adv.last_message = f"Entered {MAPS[adv.map_key].name}."
                self.dialog = [adv.last_message]
                return

    def _check_pickup(self, auto: bool = False) -> bool:
        adv = self.game.adventure
        map_def = MAPS[adv.map_key]
        for pickup in map_def.pickups:
            if pickup.key in adv.picked_items:
                continue
            if (pickup.x, pickup.y) == (adv.x, adv.y) and (auto or not pickup.hidden):
                adv.picked_items.append(pickup.key)
                adv.add_item(pickup.item_key, pickup.amount)
                self.dialog = [f"Found {ITEMS[pickup.item_key].name} x{pickup.amount}."]
                self.game.audio.play("capture")
                return True
        return False

    def _check_trainer_sight(self) -> None:
        adv = self.game.adventure
        map_def = MAPS[adv.map_key]
        for trainer in map_def.trainers:
            if trainer.key in adv.defeated_trainers:
                continue
            if abs(trainer.x - adv.x) + abs(trainer.y - adv.y) <= 2:
                first = trainer.team[0]
                self.dialog = list(trainer.lines)
                self.game.start_adventure_battle(
                    {
                        "kind": "leader" if trainer.badge else "trainer",
                        "trainer_id": trainer.key,
                        "trainer_name": trainer.name,
                        "enemy_key": first[0],
                        "enemy_level": first[1],
                        "reward": trainer.reward,
                        "badge": trainer.badge,
                        "story_flag": trainer.story_flag,
                    }
                )
                return

    def _maybe_random_encounter(self, map_def) -> None:
        adv = self.game.adventure
        if self.dialog or self.menu:
            return
        tile = map_def.tile_at(adv.x, adv.y)
        if tile not in ENCOUNTER_TILES or not map_def.encounter_table:
            return
        chance = 0.08 if adv.is_night() else 0.055
        rng = random.Random(adv.seed + adv.steps * 31 + len(adv.badges) * 997)
        if rng.random() > chance:
            return
        creature_key, low, high = rng.choice(map_def.encounter_table)
        level = rng.randint(low, high)
        self.game.start_adventure_battle({"kind": "wild", "enemy_key": creature_key, "enemy_level": level})

    def _interact(self) -> None:
        adv = self.game.adventure
        map_def = MAPS[adv.map_key]
        tx, ty = facing_tile(adv.x, adv.y, adv.facing)
        for healer in map_def.healers:
            if healer == (tx, ty) or healer == (adv.x, adv.y):
                adv.heal_party_full()
                adv.spawn_map = adv.map_key
                adv.spawn_x = adv.x
                adv.spawn_y = adv.y
                self.dialog = ["Team restored. The healer whispers: avoid dead air."]
                self.game.save_adventure()
                return
        for shop in map_def.shops:
            if (shop.x, shop.y) in ((tx, ty), (adv.x, adv.y)):
                self.shop_key = shop.key
                self.menu = "shop"
                self.menu_index = 0
                return
        for npc in map_def.npcs:
            if (npc.x, npc.y) == (tx, ty):
                self.dialog = list(npc.night_lines if adv.is_night() and npc.night_lines else npc.lines)
                return
        for sign in map_def.signs:
            if (sign.x, sign.y) == (tx, ty):
                self.dialog = list(sign.lines)
                return
        for berry in map_def.berries:
            if (berry.x, berry.y) == (tx, ty):
                count = adv.picked_berries.get(berry.key, 0)
                if count <= 0 or adv.steps - count > 120:
                    adv.add_item(berry.berry_key, berry.amount)
                    adv.picked_berries[berry.key] = adv.steps
                    self.dialog = [f"Picked {ITEMS[berry.berry_key].name} x{berry.amount}."]
                    self.game.save_adventure()
                else:
                    self.dialog = ["The berry branches are bare for now."]
                return
        for visible in map_def.visibles:
            if not adv.has_flag(f"visible_{visible.key}") and (visible.x, visible.y) == (tx, ty):
                self.dialog = list(visible.lines)
                self.game.start_adventure_battle(
                    {
                        "kind": "boss" if visible.boss else "wild",
                        "visible_id": visible.key,
                        "enemy_key": visible.creature_key,
                        "enemy_level": visible.level,
                        "story_flag": visible.story_flag,
                        "capture_allowed": visible.capture_allowed,
                        "reward": 500 + visible.level * 12,
                    }
                )
                return
        if self._check_pickup(auto=False):
            return
        if map_def.story:
            unseen_flag = f"story_{map_def.key}"
            if not adv.has_flag(unseen_flag):
                adv.set_flag(unseen_flag)
                self.dialog = list(map_def.story)
                self.game.save_adventure()
                return
        self.dialog = ["Nothing unusual here."]

    def _current_shop(self):
        adv = self.game.adventure
        if not adv:
            return None
        for shop in MAPS[adv.map_key].shops:
            if shop.key == self.shop_key or (shop.x, shop.y) == (adv.x, adv.y):
                return shop
        shops = MAPS[adv.map_key].shops
        return shops[0] if shops else None

    def draw(self, surface: pygame.Surface) -> None:
        adv = self.game.adventure
        map_def = MAPS[adv.map_key]
        draw_adventure_map(surface, map_def, adv, self.t, self.game.assets)
        self._draw_hud(surface, map_def)
        if self.menu:
            if self.menu == "region_map":
                self._draw_region_map(surface)
            else:
                self._draw_menu(surface)
        if self.dialog:
            self._draw_dialog(surface, self.dialog[0])

    def _draw_hud(self, surface: pygame.Surface, map_def) -> None:
        adv = self.game.adventure
        bar = pygame.Rect(4, 4, 376, 22)
        pygame.draw.rect(surface, COLORS["panel"], bar)
        pygame.draw.rect(surface, COLORS["stroke"], bar, 2)
        pygame.draw.rect(surface, COLORS["panel_3"], bar.inflate(-4, -4), 1)
        draw_text(surface, self.small, map_def.name, (10, 10), COLORS["ink"], align="midleft", shadow=False)
        day = "Night" if adv.is_night() else "Day"
        draw_text(surface, self.small, f"{day} {adv.time_label()}  ${adv.money}  Badges {len(adv.badges)}/8", (374, 10), COLORS["blue"], align="midright", shadow=False)

    def _draw_dialog(self, surface: pygame.Surface, text: str) -> None:
        rect = pygame.Rect(10, 154, 364, 52)
        draw_window(surface, rect)
        lines = wrap_text(self.small, text, rect.width - 22)
        for idx, line in enumerate(lines[:3]):
            draw_text(surface, self.small, line, (rect.x + 12, rect.y + 12 + idx * 12), COLORS["ink"], shadow=False)
        draw_text(surface, self.small, "Enter", (rect.right - 12, rect.bottom - 11), COLORS["blue"], align="midright", shadow=False)

    def _draw_menu(self, surface: pygame.Surface) -> None:
        options = self._menu_options()
        width = 224 if self.menu in ("quests", "bag", "shop") else 160
        rect = pygame.Rect(224 - max(0, width - 150), 30, width, min(176, 18 + len(options) * 18))
        shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        shade.fill((35, 42, 50, 92))
        surface.blit(shade, (0, 0))
        draw_window(surface, rect)
        title = self.menu.upper() if self.menu else "MENU"
        draw_text(surface, self.small, title, (rect.x + 10, rect.y + 9), COLORS["blue"], shadow=False)
        for idx, option in enumerate(options[:8]):
            row = pygame.Rect(rect.x + 8, rect.y + 24 + idx * 17, rect.width - 16, 15)
            draw_choice_box(surface, row, selected=idx == self.menu_index)
            draw_text(surface, self.small, ellipsize_text(self.small, option, row.width - 18), (row.x + 13, row.y + 7), COLORS["ink"], align="midleft", shadow=False)

    def _draw_region_map(self, surface: pygame.Surface) -> None:
        image = self.game.assets.get_adventure("rotria_map")
        shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        shade.fill((28, 32, 42, 226))
        surface.blit(shade, (0, 0))
        if image.get_width() <= 1:
            draw_window(surface, pygame.Rect(24, 64, 336, 72))
            draw_text(surface, self.font, "Rotria map art missing.", (192, 92), COLORS["cream"], align="center")
            return
        base = min(VIRTUAL_WIDTH / image.get_width(), VIRTUAL_HEIGHT / image.get_height())
        scale = base * self.map_zoom
        scaled_size = (max(1, int(image.get_width() * scale)), max(1, int(image.get_height() * scale)))
        scaled = pygame.transform.scale(image, scaled_size)
        self._clamp_map_pan(scaled_size[0], scaled_size[1])
        view = pygame.Rect(int(self.map_pan[0]), int(self.map_pan[1]), VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
        view.clamp_ip(scaled.get_rect())
        surface.blit(scaled, (0, 0), view)
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((255, 245, 196, 16))
        surface.blit(overlay, (0, 0))

        adv = self.game.adventure
        current_key = adv.map_key if adv else "starter_village"
        pois = self._poi_keys()
        for key in pois:
            px, py, kind = MAP_POIS[key]
            sx = int(px * scale - view.x)
            sy = int(py * scale - view.y)
            if not (-12 <= sx <= VIRTUAL_WIDTH + 12 and -12 <= sy <= VIRTUAL_HEIGHT + 12):
                continue
            active = key == current_key
            selected = pois and key == pois[self.map_selected % len(pois)]
            color = COLORS["select"] if active else COLORS["blue"] if selected else COLORS["stroke"]
            pygame.draw.circle(surface, COLORS["black"], (sx, sy), 6 if active else 5)
            pygame.draw.circle(surface, color, (sx, sy), 5 if active else 4)
            pygame.draw.circle(surface, COLORS["cream"], (sx, sy), 2)
            if selected or active:
                name = MAPS[key].name
                label = pygame.Rect(sx + 8, sy - 9, min(150, 14 + self.small.size(name)[0]), 18)
                if label.right > VIRTUAL_WIDTH:
                    label.right = sx - 8
                if label.y < 24:
                    label.y = 24
                pygame.draw.rect(surface, COLORS["panel"], label)
                pygame.draw.rect(surface, color, label, 1)
                draw_text(surface, self.small, ellipsize_text(self.small, name, label.width - 8), (label.x + 4, label.centery), COLORS["ink"], align="midleft", shadow=False)

        top = pygame.Rect(6, 5, 372, 24)
        pygame.draw.rect(surface, COLORS["panel"], top)
        pygame.draw.rect(surface, COLORS["stroke"], top, 2)
        draw_text(surface, self.small, "ROTRIA MAP", (14, 17), COLORS["ink"], align="midleft", shadow=False)
        draw_text(surface, self.small, f"x{self.map_zoom:.2f}", (370, 17), COLORS["blue"], align="midright", shadow=False)
        if adv:
            bottom = pygame.Rect(6, 186, 372, 24)
            pygame.draw.rect(surface, COLORS["panel"], bottom)
            pygame.draw.rect(surface, COLORS["stroke"], bottom, 2)
            draw_text(surface, self.small, f"Current: {MAPS[current_key].name}", (14, 194), COLORS["blue"], align="midleft", shadow=False)
            draw_text(surface, self.small, "M/Esc close  +/- zoom  Arrows pan  Tab POI  R reset", (14, 204), COLORS["ink"], align="midleft", shadow=False)


def draw_adventure_map(surface: pygame.Surface, map_def, adv: AdventureState, t: float, assets: AssetStore) -> None:
    tile = TILE_SIZE
    cam_x = max(0, min(map_def.width * tile - VIRTUAL_WIDTH, adv.x * tile - VIRTUAL_WIDTH // 2))
    cam_y = max(0, min(map_def.height * tile - VIRTUAL_HEIGHT, adv.y * tile - VIRTUAL_HEIGHT // 2))
    surface.fill((0, 6, 0))
    start_x = cam_x // tile
    start_y = cam_y // tile
    end_x = min(map_def.width, start_x + VIRTUAL_WIDTH // tile + 2)
    end_y = min(map_def.height, start_y + VIRTUAL_HEIGHT // tile + 2)
    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            rect = pygame.Rect(x * tile - cam_x, y * tile - cam_y, tile, tile)
            draw_tile(surface, rect, map_def.tile_at(x, y), x, y, adv.is_night(), t, assets)
    for pickup in map_def.pickups:
        if pickup.hidden or pickup.key in adv.picked_items:
            continue
        draw_world_icon(surface, (pickup.x * tile - cam_x + 8, pickup.y * tile - cam_y + 8), COLORS["gold"], "item")
    for berry in map_def.berries:
        draw_world_icon(surface, (berry.x * tile - cam_x + 8, berry.y * tile - cam_y + 8), COLORS["green"], "berry")
    for npc in map_def.npcs:
        draw_npc_sprite(surface, assets, npc.name, (npc.x * tile - cam_x + 8, npc.y * tile - cam_y + 12), t)
    for trainer in map_def.trainers:
        if trainer.key not in adv.defeated_trainers:
            draw_npc_sprite(surface, assets, trainer.trainer_class, (trainer.x * tile - cam_x + 8, trainer.y * tile - cam_y + 12), t, trainer=True)
    for visible in map_def.visibles:
        if not adv.has_flag(f"visible_{visible.key}"):
            draw_creature(surface, assets, visible.creature_key, (visible.x * tile - cam_x + 8, visible.y * tile - cam_y + 9), "idle", t, scale=0.23)
    draw_trainer_sprite(surface, assets, adv.appearance, (adv.x * tile - cam_x + 8, adv.y * tile - cam_y + 12), scale=1, facing=adv.facing, step=adv.steps)




def draw_world_icon(surface: pygame.Surface, center: Tuple[int, int], color, kind: str) -> None:
    if kind == "berry":
        pygame.draw.circle(surface, (16, 38, 21), center, 6)
        pygame.draw.circle(surface, color, (center[0] - 2, center[1] + 1), 3)
        pygame.draw.circle(surface, COLORS["gold"], (center[0] + 3, center[1] - 1), 2)
    else:
        pygame.draw.rect(surface, COLORS["black"], (center[0] - 4, center[1] - 4, 8, 8))
        pygame.draw.rect(surface, color, (center[0] - 3, center[1] - 5, 7, 7))


def draw_npc_sprite(surface: pygame.Surface, assets: AssetStore, name: str, center: Tuple[int, int], t: float, trainer: bool = False) -> None:
    sprite = assets.get_overworld("trainer_sprite" if trainer else "npc_base")
    if sprite.get_width() <= 1:
        pygame.draw.rect(surface, COLORS["red"] if trainer else COLORS["green"], (center[0] - 5, center[1] - 18, 10, 16))
        return
    frame = int(t / 0.6) % 3
    row = 0
    source = pygame.Rect(frame * 16, row * 16, 16, 16)
    dest = (center[0] - 8, center[1] - 16)
    surface.blit(sprite, dest, source)


def draw_trainer_sprite(
    surface: pygame.Surface,
    assets: AssetStore,
    appearance: PlayerAppearance,
    center: Tuple[int, int],
    scale: int = 1,
    facing: str = "down",
    step: int = 0,
) -> None:
    sprite = assets.get_overworld("player_walk")
    if sprite.get_width() <= 1:
        pygame.draw.rect(surface, COLORS["blue"], (center[0] - 5, center[1] - 18, 10, 16))
        return
    row = {"down": 0, "up": 1, "left": 2, "right": 3}.get(facing, 0)
    frame = step % 3
    source = pygame.Rect(frame * 16, row * 16, 16, 16)
    frame_surf = sprite.subsurface(source).copy()
    outfit_tints = ((0, 0, 0, 0), (50, 0, 0, 0), (0, 45, 0, 0), (45, 30, 0, 0), (32, 0, 45, 0))
    tint = pygame.Surface((16, 16), pygame.SRCALPHA)
    tint.fill(outfit_tints[appearance.outfit % len(outfit_tints)])
    frame_surf.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    if scale != 1:
        frame_surf = pygame.transform.scale(frame_surf, (16 * scale, 16 * scale))
    surface.blit(frame_surf, (center[0] - 8 * scale, center[1] - 16 * scale))


def facing_tile(x: int, y: int, facing: str) -> Tuple[int, int]:
    if facing == "up":
        return x, y - 1
    if facing == "down":
        return x, y + 1
    if facing == "left":
        return x - 1, y
    return x + 1, y


def ability_for(key: str) -> str:
    if "signal" in key or "glitch" in key or "stream" in key:
        return "Static Veil"
    if "gelato" in key or "frost" in key or "frigo" in key:
        return "Cold Snap"
    if "tung" in key or "drum" in key:
        return "Beat Guard"
    if "ballerina" in key or "grace" in CREATURES.get(key, CREATURES["spaghettimon"]).kind.lower():
        return "Clean Step"
    return "Rotria Grit"


def grant_party_xp(adv: AdventureState, xp: int, active_only: bool = False) -> List[str]:
    messages: List[str] = []
    targets = [adv.active_creature()] if active_only else [unit for unit in adv.party if not unit.is_down()]
    for unit in targets:
        unit.xp += xp
        while unit.xp >= xp_to_next(unit.level):
            unit.xp -= xp_to_next(unit.level)
            unit.level += 1
            old_max = unit.max_hp()
            unit.heal_full()
            messages.append(f"{unit.name} reached Lv {unit.level}.")
            evo = unit.creature.evolution
            if evo and unit.level >= evo.level_required and evo.evolves_to in CREATURES:
                unit.key = evo.evolves_to
                unit.heal_full()
                messages.append(f"It evolved into {unit.name}!")
            elif unit.level in (16, 32) and unit.key in AUTO_EVOLUTIONS:
                unit.key = AUTO_EVOLUTIONS[unit.key]
                unit.heal_full()
                messages.append(f"It evolved into {unit.name}!")
            if unit.max_hp() <= old_max:
                unit.hp = max(unit.hp or 1, unit.max_hp())
    return messages


AUTO_EVOLUTIONS = {
    "spaghettimon": "pastaflame",
    "ballerinacappuccina": "creamurai",
    "tungtungsahur": "jungletungtungsahur",
    "pizzaratto": "pizzawraith",
    "gelatitan": "gelatogolem",
    "macaronocchio": "glitchocchio",
    "raviolord": "ravioliraptor",
}


def next_main_quest(adv: AdventureState) -> str:
    chapters = [
        "Investigate Team Scroll in Pasta Port.",
        "Cross Crema Bridge toward Drumwood Forest.",
        "Clear Broadcast Tower in Neon Feed City.",
        "Win the Coliseum Market badge.",
        "Reach Freezer Cavern and silence the cold machine.",
        "Follow the sea signal at Siren Pier.",
        "Read the Static Abbey seal tablet.",
        "Climb Signal Spire and protect Rotria.",
        "Cross Crown Road to the Ancient Core.",
    ]
    return chapters[min(len(adv.badges), len(chapters) - 1)]
