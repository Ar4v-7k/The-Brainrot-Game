from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

from .creatures import CREATURES, CreatureDef


@dataclass
class SettingsState:
    music_on: bool = True
    sfx_on: bool = True
    idle_on: bool = True
    battle_speed: int = 1
    text_speed: int = 1

    @classmethod
    def from_dict(cls, payload: Optional[dict]) -> "SettingsState":
        if not payload:
            return cls()
        return cls(
            music_on=payload.get("music_on", True),
            sfx_on=payload.get("sfx_on", True),
            idle_on=payload.get("idle_on", True),
            battle_speed=int(payload.get("battle_speed", 1)),
            text_speed=int(payload.get("text_speed", 1)),
        )


@dataclass
class ProfileState:
    total_runs: int = 0
    total_wins: int = 0
    best_wave: int = 1
    unlocked: List[str] = field(default_factory=list)
    seen: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: Optional[dict]) -> "ProfileState":
        if not payload:
            return cls()
        return cls(
            total_runs=int(payload.get("total_runs", 0)),
            total_wins=int(payload.get("total_wins", 0)),
            best_wave=int(payload.get("best_wave", 1)),
            unlocked=list(payload.get("unlocked", [])),
            seen=list(payload.get("seen", [])),
        )

    def unlock(self, key: str) -> None:
        if key not in self.unlocked:
            self.unlocked.append(key)
        self.mark_seen(key)

    def mark_seen(self, key: str) -> None:
        if key not in self.seen:
            self.seen.append(key)


@dataclass
class CreatureInstance:
    key: str
    level: int = 1
    hp: Optional[int] = None
    xp: int = 0
    held_item: str = ""
    status: str = ""
    ability: str = ""

    @classmethod
    def from_dict(cls, payload: dict) -> "CreatureInstance":
        return cls(
            key=payload["key"],
            level=int(payload.get("level", 1)),
            hp=payload.get("hp"),
            xp=int(payload.get("xp", 0)),
            held_item=payload.get("held_item", ""),
            status=payload.get("status", ""),
            ability=payload.get("ability", ""),
        )

    @property
    def creature(self) -> CreatureDef:
        return CREATURES[self.key]

    @property
    def name(self) -> str:
        return self.creature.name

    @property
    def kind(self) -> str:
        return self.creature.kind

    def max_hp(self) -> int:
        return self.creature.max_hp + max(0, self.level - 1) * 3

    def attack_stat(self) -> int:
        return self.creature.attack + self.level

    def defense_stat(self) -> int:
        return self.creature.defense + max(0, self.level - 1)

    def ensure_hp(self) -> None:
        if self.hp is None:
            self.hp = self.max_hp()
        else:
            self.hp = max(0, min(self.max_hp(), int(self.hp)))

    def heal_full(self) -> None:
        self.hp = self.max_hp()

    def heal(self, amount: int) -> int:
        self.ensure_hp()
        old = self.hp or 0
        self.hp = min(self.max_hp(), old + amount)
        return self.hp - old

    def take_damage(self, amount: int) -> int:
        self.ensure_hp()
        old = self.hp or 0
        self.hp = max(0, old - amount)
        return old - self.hp

    def is_down(self) -> bool:
        self.ensure_hp()
        return (self.hp or 0) <= 0

    def copy(self) -> "CreatureInstance":
        return CreatureInstance(self.key, self.level, self.hp, self.xp, self.held_item, self.status, self.ability)


@dataclass
class RunState:
    slot: int
    seed: int
    wave: int = 1
    wins: int = 0
    money: int = 0
    starter_key: str = ""
    active_index: int = 0
    party: List[CreatureInstance] = field(default_factory=list)
    collection: List[str] = field(default_factory=list)
    inventory: Dict[str, int] = field(
        default_factory=lambda: {"Pasta Capsule": 5, "Tomato Tonic": 3}
    )
    current_enemy: Optional[CreatureInstance] = None
    last_reward: str = ""

    @classmethod
    def from_dict(cls, payload: dict) -> "RunState":
        current_enemy = payload.get("current_enemy")
        run = cls(
            slot=int(payload["slot"]),
            seed=int(payload["seed"]),
            wave=int(payload.get("wave", 1)),
            wins=int(payload.get("wins", 0)),
            money=int(payload.get("money", 0)),
            starter_key=payload.get("starter_key", ""),
            active_index=int(payload.get("active_index", 0)),
            party=[CreatureInstance.from_dict(item) for item in payload.get("party", [])],
            collection=list(payload.get("collection", [])),
            inventory={k: int(v) for k, v in payload.get("inventory", {}).items()},
            current_enemy=CreatureInstance.from_dict(current_enemy) if current_enemy else None,
            last_reward=payload.get("last_reward", ""),
        )
        run.normalize()
        return run

    def normalize(self) -> None:
        if not self.party and self.starter_key:
            self.party = [CreatureInstance(self.starter_key, 3)]
        for unit in self.party:
            unit.ensure_hp()
        if self.current_enemy:
            self.current_enemy.ensure_hp()
        if self.active_index >= len(self.party):
            self.active_index = 0
        if not self.collection and self.starter_key:
            self.collection = [self.starter_key]
        self.inventory.setdefault("Pasta Capsule", 0)
        self.inventory.setdefault("Tomato Tonic", 0)

    def active_creature(self) -> CreatureInstance:
        self.normalize()
        if not self.party:
            raise ValueError("RunState has no party")
        active = self.party[self.active_index]
        if not active.is_down():
            return active
        replacement = self.next_healthy_index()
        if replacement is not None:
            self.active_index = replacement
            return self.party[replacement]
        return active

    def next_healthy_index(self) -> Optional[int]:
        for idx, unit in enumerate(self.party):
            if not unit.is_down():
                return idx
        return None

    def has_healthy_party(self) -> bool:
        return self.next_healthy_index() is not None

    def add_to_collection(self, key: str) -> None:
        if key not in self.collection:
            self.collection.append(key)

    def add_creature(self, key: str, level: int) -> bool:
        self.add_to_collection(key)
        if len(self.party) >= 6:
            return False
        self.party.append(CreatureInstance(key, level))
        self.party[-1].ensure_hp()
        return True

    def heal_party_full(self) -> None:
        for unit in self.party:
            unit.heal_full()

    def party_names(self) -> str:
        if not self.party:
            return "-"
        return ", ".join(unit.name for unit in self.party[:3])

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SaveBundle:
    settings: SettingsState = field(default_factory=SettingsState)
    profile: ProfileState = field(default_factory=ProfileState)

    def to_dict(self) -> dict:
        return {"settings": asdict(self.settings), "profile": asdict(self.profile)}


@dataclass
class PlayerAppearance:
    body: int = 0
    skin: int = 1
    hair: int = 0
    outfit: int = 0
    accent: int = 0
    accessory: int = 0

    @classmethod
    def from_dict(cls, payload: Optional[dict]) -> "PlayerAppearance":
        if not payload:
            return cls()
        return cls(
            body=int(payload.get("body", 0)),
            skin=int(payload.get("skin", 1)),
            hair=int(payload.get("hair", 0)),
            outfit=int(payload.get("outfit", 0)),
            accent=int(payload.get("accent", 0)),
            accessory=int(payload.get("accessory", 0)),
        )


@dataclass
class AdventureState:
    slot: int
    seed: int
    player_name: str = "ARAV"
    appearance: PlayerAppearance = field(default_factory=PlayerAppearance)
    map_key: str = "starter_village"
    x: int = 21
    y: int = 14
    facing: str = "down"
    spawn_map: str = "starter_village"
    spawn_x: int = 21
    spawn_y: int = 14
    starter_key: str = ""
    active_index: int = 0
    party: List[CreatureInstance] = field(default_factory=list)
    boxes: List[CreatureInstance] = field(default_factory=list)
    bag: Dict[str, int] = field(default_factory=lambda: {"pasta_capsule": 5, "tomato_tonic": 3})
    money: int = 600
    badges: List[str] = field(default_factory=list)
    quests: Dict[str, str] = field(default_factory=dict)
    flags: List[str] = field(default_factory=list)
    defeated_trainers: List[str] = field(default_factory=list)
    picked_items: List[str] = field(default_factory=list)
    picked_berries: Dict[str, int] = field(default_factory=dict)
    seen: List[str] = field(default_factory=list)
    caught: List[str] = field(default_factory=list)
    story_chapter: int = 0
    clock_minutes: int = 8 * 60
    steps: int = 0
    last_message: str = ""

    @classmethod
    def from_dict(cls, payload: dict) -> "AdventureState":
        adv = cls(
            slot=int(payload["slot"]),
            seed=int(payload["seed"]),
            player_name=payload.get("player_name", "ARAV"),
            appearance=PlayerAppearance.from_dict(payload.get("appearance")),
            map_key=payload.get("map_key", "starter_village"),
            x=int(payload.get("x", 21)),
            y=int(payload.get("y", 14)),
            facing=payload.get("facing", "down"),
            spawn_map=payload.get("spawn_map", "starter_village"),
            spawn_x=int(payload.get("spawn_x", 21)),
            spawn_y=int(payload.get("spawn_y", 14)),
            starter_key=payload.get("starter_key", ""),
            active_index=int(payload.get("active_index", 0)),
            party=[CreatureInstance.from_dict(item) for item in payload.get("party", [])],
            boxes=[CreatureInstance.from_dict(item) for item in payload.get("boxes", [])],
            bag={k: int(v) for k, v in payload.get("bag", {}).items()},
            money=int(payload.get("money", 600)),
            badges=list(payload.get("badges", [])),
            quests=dict(payload.get("quests", {})),
            flags=list(payload.get("flags", [])),
            defeated_trainers=list(payload.get("defeated_trainers", [])),
            picked_items=list(payload.get("picked_items", [])),
            picked_berries={k: int(v) for k, v in payload.get("picked_berries", {}).items()},
            seen=list(payload.get("seen", [])),
            caught=list(payload.get("caught", [])),
            story_chapter=int(payload.get("story_chapter", 0)),
            clock_minutes=int(payload.get("clock_minutes", 8 * 60)),
            steps=int(payload.get("steps", 0)),
            last_message=payload.get("last_message", ""),
        )
        adv.normalize()
        return adv

    def normalize(self) -> None:
        self.bag.setdefault("pasta_capsule", 0)
        self.bag.setdefault("tomato_tonic", 0)
        for unit in self.party:
            unit.ensure_hp()
            self.mark_seen(unit.key)
            self.mark_caught(unit.key)
        for unit in self.boxes:
            unit.ensure_hp()
            self.mark_seen(unit.key)
            self.mark_caught(unit.key)
        if self.active_index >= len(self.party):
            self.active_index = 0
        self.clock_minutes %= 24 * 60

    def active_creature(self) -> CreatureInstance:
        self.normalize()
        if not self.party:
            raise ValueError("AdventureState has no party")
        active = self.party[self.active_index]
        if not active.is_down():
            return active
        replacement = self.next_healthy_index()
        if replacement is not None:
            self.active_index = replacement
            return self.party[replacement]
        return active

    def next_healthy_index(self) -> Optional[int]:
        for idx, unit in enumerate(self.party):
            if not unit.is_down():
                return idx
        return None

    def has_healthy_party(self) -> bool:
        return self.next_healthy_index() is not None

    def heal_party_full(self) -> None:
        for unit in self.party:
            unit.heal_full()
            unit.status = ""

    def add_item(self, key: str, amount: int = 1) -> None:
        self.bag[key] = self.bag.get(key, 0) + amount

    def use_item(self, key: str, amount: int = 1) -> bool:
        if self.bag.get(key, 0) < amount:
            return False
        self.bag[key] -= amount
        return True

    def add_creature(self, key: str, level: int) -> bool:
        unit = CreatureInstance(key, level)
        unit.ensure_hp()
        self.mark_seen(key)
        self.mark_caught(key)
        if len(self.party) < 6:
            self.party.append(unit)
            return True
        self.boxes.append(unit)
        return False

    def mark_seen(self, key: str) -> None:
        if key and key not in self.seen:
            self.seen.append(key)

    def mark_caught(self, key: str) -> None:
        if key and key not in self.caught:
            self.caught.append(key)

    def has_flag(self, flag: str) -> bool:
        return bool(flag) and flag in self.flags

    def set_flag(self, flag: str) -> None:
        if flag and flag not in self.flags:
            self.flags.append(flag)

    def is_night(self) -> bool:
        hour = (self.clock_minutes // 60) % 24
        return hour >= 19 or hour < 6

    def time_label(self) -> str:
        hour = (self.clock_minutes // 60) % 24
        minute = self.clock_minutes % 60
        return f"{hour:02d}:{minute:02d}"

    def to_dict(self) -> dict:
        return asdict(self)
