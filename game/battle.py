from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import List, Optional

from .creatures import ENCOUNTER_KEYS, MoveDef
from .rpg_rules import effectiveness, move_type
from .state import CreatureInstance, RunState

ATTACK_DURATIONS = {
    "fork_flick": 0.46,
    "sauce_splash": 0.74,
    "al_dente_slam": 0.68,
    "meatball_panic": 0.82,
    "drum_knock": 0.46,
    "sahur_burst": 0.72,
    "tung_roll": 0.80,
    "midnight_march": 0.90,
    "pirouette_pour": 0.66,
    "foam_ribbon": 0.70,
    "arabesque_roast": 0.76,
    "finale_froth": 0.84,
    "sneaker_snap": 0.48,
    "tralala_wave": 0.72,
    "reef_rush": 0.78,
    "coral_chorus": 0.88,
    "silent_sip": 0.44,
    "crema_dagger": 0.68,
    "shadow_roast": 0.72,
    "espresso_exit": 0.80,
    "orbit_kick": 0.56,
    "milky_way_moo": 0.72,
    "ring_charge": 0.82,
    "nova_hoof": 0.76,
    "runway_rush": 0.74,
    "bomb_burst": 0.82,
    "croco_cannon": 0.86,
    "tail_rotor": 0.78,
    "cooler_kick": 0.48,
    "frost_spit": 0.70,
    "ice_box_crash": 0.78,
    "desert_chill": 0.82,
    "branch_bonk": 0.46,
    "pinecone_pop": 0.70,
    "brrr_blast": 0.78,
    "mossy_mayhem": 0.82,
    "peel_jab": 0.44,
    "banana_boomerang": 0.70,
    "monkey_mash": 0.76,
    "bananini_barrage": 0.84,
    "scurry_slice": 0.44,
    "crust_comet": 0.70,
    "mozza_mob": 0.74,
    "oven_ambush": 0.78,
    "layer_lash": 0.72,
    "ricotta_rattle": 0.70,
    "coil_crush": 0.78,
    "bake_coil": 0.84,
    "scoop_smack": 0.44,
    "frost_swirl": 0.80,
    "sundae_slide": 0.76,
    "brain_freeze": 0.74,
    "kernel_kick": 0.46,
    "corn_quake": 0.78,
    "golden_roar": 0.74,
    "polenta_meteor": 0.82,
    "string_sting": 0.70,
    "ganache_glint": 0.70,
    "puppet_pivot": 0.80,
    "marzipan_mirage": 0.84,
    "crown_crimp": 0.46,
    "sauce_decree": 0.70,
    "noble_fold": 0.78,
    "ravioli_reign": 0.84,
    "link_lash": 0.72,
    "pepper_spear": 0.70,
    "grill_grind": 0.76,
    "coliseum_sear": 0.78,
    "crust_cudgel": 0.46,
    "olive_order": 0.70,
    "toast_takedown": 0.78,
    "boss_banquet": 0.84,
    "toast_tread": 0.76,
    "tomato_mortar": 0.70,
    "garlic_guard": 0.46,
    "bruschetta_barrage": 0.78,
    "curd_claw": 0.46,
    "stretch_beam": 0.72,
    "pride_pounce": 0.76,
    "melt_majesty": 0.84,
}

HIT_DURATIONS = {
    "fork_flick": 0.38,
    "sauce_splash": 0.48,
    "al_dente_slam": 0.56,
    "meatball_panic": 0.60,
    "drum_knock": 0.40,
    "sahur_burst": 0.50,
    "tung_roll": 0.56,
    "midnight_march": 0.62,
    "pirouette_pour": 0.42,
    "foam_ribbon": 0.48,
    "arabesque_roast": 0.54,
    "finale_froth": 0.60,
    "sneaker_snap": 0.40,
    "tralala_wave": 0.50,
    "reef_rush": 0.56,
    "coral_chorus": 0.62,
    "silent_sip": 0.38,
    "crema_dagger": 0.48,
    "shadow_roast": 0.54,
    "espresso_exit": 0.58,
    "orbit_kick": 0.44,
    "milky_way_moo": 0.52,
    "ring_charge": 0.60,
    "nova_hoof": 0.58,
    "runway_rush": 0.56,
    "bomb_burst": 0.60,
    "croco_cannon": 0.62,
    "tail_rotor": 0.56,
    "cooler_kick": 0.40,
    "frost_spit": 0.50,
    "ice_box_crash": 0.58,
    "desert_chill": 0.60,
    "branch_bonk": 0.40,
    "pinecone_pop": 0.50,
    "brrr_blast": 0.56,
    "mossy_mayhem": 0.60,
    "peel_jab": 0.38,
    "banana_boomerang": 0.50,
    "monkey_mash": 0.56,
    "bananini_barrage": 0.60,
    "scurry_slice": 0.38,
    "crust_comet": 0.50,
    "mozza_mob": 0.52,
    "oven_ambush": 0.58,
    "layer_lash": 0.50,
    "ricotta_rattle": 0.50,
    "coil_crush": 0.56,
    "bake_coil": 0.60,
    "scoop_smack": 0.38,
    "frost_swirl": 0.58,
    "sundae_slide": 0.56,
    "brain_freeze": 0.52,
    "kernel_kick": 0.40,
    "corn_quake": 0.58,
    "golden_roar": 0.52,
    "polenta_meteor": 0.60,
    "string_sting": 0.48,
    "ganache_glint": 0.50,
    "puppet_pivot": 0.56,
    "marzipan_mirage": 0.60,
    "crown_crimp": 0.40,
    "sauce_decree": 0.50,
    "noble_fold": 0.56,
    "ravioli_reign": 0.60,
    "link_lash": 0.50,
    "pepper_spear": 0.50,
    "grill_grind": 0.56,
    "coliseum_sear": 0.56,
    "crust_cudgel": 0.40,
    "olive_order": 0.50,
    "toast_takedown": 0.58,
    "boss_banquet": 0.60,
    "toast_tread": 0.56,
    "tomato_mortar": 0.50,
    "garlic_guard": 0.40,
    "bruschetta_barrage": 0.56,
    "curd_claw": 0.40,
    "stretch_beam": 0.50,
    "pride_pounce": 0.56,
    "melt_majesty": 0.60,
}


@dataclass
class BattleEvent:
    kind: str
    text: str = ""
    actor: str = ""
    target: str = ""
    move_name: str = ""
    effect: str = ""
    value: int = 0
    duration: float = 0.45


@dataclass
class BattleResult:
    outcome: str
    events: List[BattleEvent] = field(default_factory=list)


class BattleSession:
    def __init__(self, run: RunState):
        self.run = run
        self.rng = random.Random(run.seed + run.wave * 9973)
        self.player_guard = False
        self.enemy_guard = False
        if self.run.current_enemy is None:
            self.run.current_enemy = self.spawn_enemy(self.run.wave)
        self.run.current_enemy.ensure_hp()
        self.run.active_creature().ensure_hp()

    def spawn_enemy(self, wave: int) -> CreatureInstance:
        pool = list(ENCOUNTER_KEYS)
        if self.run.starter_key in pool and len(pool) > 3:
            pool.remove(self.run.starter_key)
        key = pool[(wave * 7 + self.run.seed) % len(pool)]
        level = max(2, 2 + (wave - 1) // 2)
        unit = CreatureInstance(key, level)
        unit.ensure_hp()
        return unit

    def use_move(self, move_index: int) -> BattleResult:
        player = self.run.active_creature()
        enemy = self.run.current_enemy
        if enemy is None:
            return BattleResult("win", [BattleEvent("message", "No enemy present.")])
        moves = player.creature.moves
        if move_index < 0 or move_index >= len(moves):
            return BattleResult("ongoing", [BattleEvent("message", "Bad move slot.")])
        events = self._perform_attack(player, enemy, moves[move_index], "player", "enemy", self.enemy_guard)
        self.enemy_guard = False
        if enemy.is_down():
            return BattleResult("win", events)
        events.extend(self._enemy_turn())
        return BattleResult(self._outcome(), events)

    def guard(self) -> BattleResult:
        self.player_guard = True
        events = [BattleEvent("guard", "Guard up. Incoming hit weaker.", actor="player", duration=0.35)]
        events.extend(self._enemy_turn())
        return BattleResult(self._outcome(), events)

    def use_tonic(self) -> BattleResult:
        if self.run.inventory.get("Tomato Tonic", 0) <= 0:
            return BattleResult("ongoing", [BattleEvent("message", "No Tomato Tonic left.")])
        healed = self.run.active_creature().heal(max(14, self.run.active_creature().max_hp() // 3))
        self.run.inventory["Tomato Tonic"] -= 1
        events = [
            BattleEvent("item", "Tomato Tonic splashed.", actor="player", effect="sparkle", duration=0.45),
            BattleEvent("heal", f"{self.run.active_creature().name} healed {healed} HP.", actor="player", value=healed, duration=0.35),
        ]
        events.extend(self._enemy_turn())
        return BattleResult(self._outcome(), events)

    def throw_capsule(self) -> BattleResult:
        enemy = self.run.current_enemy
        if enemy is None:
            return BattleResult("win", [BattleEvent("message", "No enemy present.")])
        if self.run.inventory.get("Pasta Capsule", 0) <= 0:
            return BattleResult("ongoing", [BattleEvent("message", "No Pasta Capsule left.")])
        self.run.inventory["Pasta Capsule"] -= 1
        hp_ratio = (enemy.hp or enemy.max_hp()) / float(enemy.max_hp())
        capture_rate = enemy.creature.capture_rate + (1.0 - hp_ratio) * 0.45
        events = [BattleEvent("capture", "Pasta Capsule launched!", actor="player", effect="sparkle", duration=0.6)]
        if self.rng.random() <= capture_rate:
            self.run.add_creature(enemy.key, enemy.level)
            events.append(BattleEvent("message", f"{enemy.name} joined party.", actor="enemy", duration=0.45))
            return BattleResult("captured", events)
        events.append(BattleEvent("message", f"{enemy.name} busted out.", actor="enemy", duration=0.35))
        events.extend(self._enemy_turn())
        return BattleResult(self._outcome(), events)

    def attempt_run(self) -> BattleResult:
        events = [BattleEvent("message", "Tried to bolt.", actor="player", duration=0.3)]
        if self.rng.random() < 0.58:
            events.append(BattleEvent("message", "Escape clean.", actor="player", duration=0.35))
            return BattleResult("escaped", events)
        events.append(BattleEvent("message", "Escape failed.", actor="enemy", duration=0.35))
        events.extend(self._enemy_turn())
        return BattleResult(self._outcome(), events)

    def switch_party(self, index: int) -> BattleResult:
        if index < 0 or index >= len(self.run.party):
            return BattleResult("ongoing", [BattleEvent("message", "Bad party slot.")])
        unit = self.run.party[index]
        if unit.is_down():
            return BattleResult("ongoing", [BattleEvent("message", f"{unit.name} down already.")])
        if index == self.run.active_index:
            return BattleResult("ongoing", [BattleEvent("message", f"{unit.name} already out.")])
        self.run.active_index = index
        events = [BattleEvent("switch", f"Go {unit.name}!", actor="player", duration=0.5)]
        events.extend(self._enemy_turn())
        return BattleResult(self._outcome(), events)

    def _enemy_turn(self) -> List[BattleEvent]:
        enemy = self.run.current_enemy
        player = self.run.active_creature()
        if enemy is None or enemy.is_down():
            return []
        move = enemy.creature.moves[self.rng.randrange(len(enemy.creature.moves))]
        events = self._perform_attack(enemy, player, move, "enemy", "player", self.player_guard)
        self.player_guard = False
        if player.is_down():
            replacement = self.run.next_healthy_index()
            if replacement is not None:
                self.run.active_index = replacement
                events.append(BattleEvent("switch", f"{self.run.active_creature().name} jumps in.", actor="player", duration=0.45))
        return events

    def _perform_attack(
        self,
        attacker: CreatureInstance,
        defender: CreatureInstance,
        move: MoveDef,
        actor: str,
        target: str,
        guard_active: bool,
    ) -> List[BattleEvent]:
        events = [
            BattleEvent(
                "attack",
                f"{attacker.name} used {move.name}.",
                actor=actor,
                target=target,
                move_name=move.name,
                effect=self._effect_for(attacker, move),
                duration=ATTACK_DURATIONS.get(move.anim_key, 0.5),
            )
        ]
        if self.rng.randint(1, 100) > move.accuracy:
            events.append(BattleEvent("message", "Attack missed.", actor=actor, target=target, duration=0.3))
            return events
        raw = move.power + attacker.attack_stat() - max(1, defender.defense_stat() // 2)
        attack_type = move_type(move.anim_key, attacker.kind)
        type_multiplier, type_text = effectiveness(attack_type, defender.kind)
        damage = max(1, int((raw // 2 + self.rng.randint(0, 5)) * type_multiplier))
        if guard_active:
            damage = max(1, damage // 2)
        dealt = defender.take_damage(damage)
        if type_text:
            events.append(BattleEvent("message", type_text, actor=actor, target=target, duration=0.25))
        events.append(
            BattleEvent(
                "hit",
                f"{defender.name} took {dealt} damage.",
                actor=actor,
                target=target,
                effect=self._effect_for(attacker, move),
                value=dealt,
                duration=HIT_DURATIONS.get(move.anim_key, 0.35),
            )
        )
        if not defender.is_down() and defender.held_item == "crema_berry" and (defender.hp or 0) <= defender.max_hp() // 2:
            healed = defender.heal(12)
            defender.held_item = ""
            events.append(BattleEvent("heal", f"{defender.name}'s Crema Berry restored {healed} HP.", actor=target, target=target, effect="sparkle", duration=0.35))
        if not defender.is_down() and not defender.status:
            status = self._status_for(move.anim_key)
            if status and self.rng.random() < 0.12:
                defender.status = status
                events.append(BattleEvent("message", f"{defender.name} caught {status}.", actor=target, target=target, duration=0.3))
        if defender.is_down():
            events.append(BattleEvent("faint", f"{defender.name} folded.", actor=target, duration=0.45))
        return events

    def _effect_for(self, unit: CreatureInstance, move: MoveDef) -> str:
        return move.anim_key

    def _status_for(self, anim_key: str) -> str:
        lowered = anim_key.lower()
        if any(token in lowered for token in ("frost", "ice", "chill", "freeze")):
            return "frost"
        if any(token in lowered for token in ("signal", "wave", "shadow", "silent")):
            return "static"
        if any(token in lowered for token in ("sauce", "roast", "fire", "sear")):
            return "spice"
        return ""

    def _outcome(self) -> str:
        enemy = self.run.current_enemy
        if enemy is not None and enemy.is_down():
            return "win"
        if not self.run.has_healthy_party():
            return "loss"
        return "ongoing"
