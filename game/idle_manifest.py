PINGPONG_6 = [0, 1, 2, 3, 4, 5, 4, 3, 2, 1]

from .creatures import CREATURES

IDLE_MANIFEST = {
    "spaghettimon": {"style": "noodle", "fps": 4.0, "sequence": PINGPONG_6},
    "tungtungsahur": {"style": "drum", "fps": 4.0, "sequence": PINGPONG_6},
    "ballerinacappuccina": {"style": "ballet", "fps": 4.0, "sequence": PINGPONG_6},
    "tralalerotralala": {"style": "singer", "fps": 4.0, "sequence": PINGPONG_6},
    "cappuccinoassassino": {"style": "royal", "fps": 4.0, "sequence": PINGPONG_6},
    "vaccasaturnosaturnita": {"style": "kaiju", "fps": 4.0, "sequence": PINGPONG_6},
    "bombardirocrocodilo": {"style": "plane", "fps": 4.0, "sequence": PINGPONG_6},
    "frigocamelo": {"style": "camel", "fps": 4.0, "sequence": PINGPONG_6},
    "brrbrrpatapim": {"style": "gladiator", "fps": 4.0, "sequence": PINGPONG_6},
    "chimpanzinibananini": {"style": "rat", "fps": 4.0, "sequence": PINGPONG_6},
    "pizzaratto": {"style": "rat", "fps": 4.0, "sequence": PINGPONG_6},
    "lasagnaconda": {"style": "coil", "fps": 4.0, "sequence": PINGPONG_6},
    "gelatitan": {"style": "melt", "fps": 4.0, "sequence": PINGPONG_6},
    "polentazilla": {"style": "kaiju", "fps": 4.0, "sequence": PINGPONG_6},
    "macaronocchio": {"style": "puppet", "fps": 4.0, "sequence": PINGPONG_6},
    "raviolord": {"style": "royal", "fps": 4.0, "sequence": PINGPONG_6},
    "salsicciator": {"style": "gladiator", "fps": 4.0, "sequence": PINGPONG_6},
    "crostinoboss": {"style": "boss", "fps": 4.0, "sequence": PINGPONG_6},
    "bruschettank": {"style": "tank", "fps": 4.0, "sequence": PINGPONG_6},
    "mozzarellion": {"style": "heavy", "fps": 4.0, "sequence": PINGPONG_6},
}

_STYLE_ROTATION = (
    "noodle",
    "drum",
    "ballet",
    "singer",
    "royal",
    "kaiju",
    "plane",
    "camel",
    "gladiator",
    "rat",
    "coil",
    "melt",
    "tank",
    "puppet",
)

for _index, _key in enumerate(CREATURES):
    IDLE_MANIFEST.setdefault(
        _key,
        {"style": _STYLE_ROTATION[_index % len(_STYLE_ROTATION)], "fps": 4.0, "sequence": PINGPONG_6},
    )
