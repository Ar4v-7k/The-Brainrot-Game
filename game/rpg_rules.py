from __future__ import annotations

from typing import Dict, Tuple


TYPE_NAMES = (
    "Noodle",
    "Sauce",
    "Rhythm",
    "Wood",
    "Foam",
    "Grace",
    "Signal",
    "Ancient",
    "Street",
    "Frost",
    "Coast",
    "Shadow",
)


# Attacking type -> defending type -> multiplier.
TYPE_CHART: Dict[str, Dict[str, float]] = {
    "Noodle": {"Sauce": 1.25, "Frost": 1.25, "Coast": 0.8},
    "Sauce": {"Wood": 1.25, "Frost": 1.25, "Coast": 0.75},
    "Rhythm": {"Signal": 1.25, "Shadow": 1.15, "Wood": 0.85},
    "Wood": {"Coast": 1.25, "Signal": 0.8, "Sauce": 0.85},
    "Foam": {"Sauce": 1.15, "Shadow": 1.25, "Frost": 0.85},
    "Grace": {"Rhythm": 1.2, "Street": 1.15, "Wood": 0.85},
    "Signal": {"Grace": 1.2, "Coast": 1.15, "Ancient": 0.7},
    "Ancient": {"Signal": 1.35, "Shadow": 1.15, "Street": 0.8},
    "Street": {"Foam": 1.15, "Grace": 0.85, "Ancient": 0.85},
    "Frost": {"Wood": 1.25, "Coast": 1.15, "Sauce": 0.8},
    "Coast": {"Sauce": 1.2, "Street": 1.1, "Signal": 0.85},
    "Shadow": {"Grace": 1.25, "Signal": 1.15, "Foam": 0.75},
}


MOVE_TYPE_HINTS = {
    "sauce": "Sauce",
    "tomato": "Sauce",
    "roast": "Sauce",
    "fire": "Sauce",
    "tung": "Rhythm",
    "drum": "Rhythm",
    "sahur": "Rhythm",
    "march": "Rhythm",
    "branch": "Wood",
    "pine": "Wood",
    "moss": "Wood",
    "foam": "Foam",
    "froth": "Foam",
    "sip": "Foam",
    "pour": "Foam",
    "pirouette": "Grace",
    "arabesque": "Grace",
    "finale": "Grace",
    "orbit": "Ancient",
    "nova": "Ancient",
    "signal": "Signal",
    "wave": "Signal",
    "shadow": "Shadow",
    "silent": "Shadow",
    "frost": "Frost",
    "ice": "Frost",
    "chill": "Frost",
    "reef": "Coast",
    "coral": "Coast",
    "water": "Coast",
    "runway": "Street",
    "scurry": "Street",
    "boss": "Street",
}


def primary_type(kind: str) -> str:
    first = kind.split("/", 1)[0].strip()
    if first in TYPE_NAMES:
        return first
    aliases = {
        "Pasta": "Noodle",
        "Coffee": "Foam",
        "Crema": "Foam",
        "Ballet": "Grace",
        "Prank": "Street",
        "Market": "Street",
        "Ice": "Frost",
        "Forest": "Wood",
        "Cosmic": "Ancient",
        "Royal": "Ancient",
        "Toast": "Street",
        "Cheese": "Foam",
        "Bomber": "Street",
        "Desert": "Ancient",
    }
    return aliases.get(first, "Noodle")


def move_type(anim_key: str, attacker_kind: str) -> str:
    lowered = anim_key.lower()
    for token, type_name in MOVE_TYPE_HINTS.items():
        if token in lowered:
            return type_name
    return primary_type(attacker_kind)


def effectiveness(attack_type: str, defender_kind: str) -> Tuple[float, str]:
    defender_types = [part.strip() for part in defender_kind.split("/") if part.strip()]
    if not defender_types:
        defender_types = ["Noodle"]
    multiplier = 1.0
    for defender_type in defender_types:
        multiplier *= TYPE_CHART.get(attack_type, {}).get(defender_type, 1.0)
    if multiplier >= 1.3:
        text = "It hit the weak spot."
    elif multiplier >= 1.15:
        text = "It worked well."
    elif multiplier <= 0.75:
        text = "The effect was dulled."
    elif multiplier < 0.95:
        text = "It barely caught."
    else:
        text = ""
    return multiplier, text


def xp_to_next(level: int) -> int:
    return 18 + max(1, level) * 14
