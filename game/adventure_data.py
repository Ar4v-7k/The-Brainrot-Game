from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


TilePos = Tuple[int, int]


@dataclass(frozen=True)
class ItemDef:
    key: str
    name: str
    kind: str
    desc: str
    price: int = 0
    power: int = 0


@dataclass(frozen=True)
class WarpDef:
    x: int
    y: int
    target_map: str
    target_x: int
    target_y: int
    label: str = ""
    required_flag: str = ""


@dataclass(frozen=True)
class NPCDef:
    key: str
    name: str
    x: int
    y: int
    lines: Tuple[str, ...]
    facing: str = "down"
    flag: str = ""
    night_lines: Tuple[str, ...] = ()


@dataclass(frozen=True)
class SignDef:
    x: int
    y: int
    lines: Tuple[str, ...]


@dataclass(frozen=True)
class PickupDef:
    key: str
    item_key: str
    x: int
    y: int
    amount: int = 1
    hidden: bool = False


@dataclass(frozen=True)
class BerryTreeDef:
    key: str
    berry_key: str
    x: int
    y: int
    amount: int = 2


@dataclass(frozen=True)
class TrainerDef:
    key: str
    name: str
    x: int
    y: int
    team: Tuple[Tuple[str, int], ...]
    lines: Tuple[str, ...]
    reward: int
    trainer_class: str = "Trainer"
    badge: str = ""
    story_flag: str = ""


@dataclass(frozen=True)
class VisibleEncounterDef:
    key: str
    creature_key: str
    x: int
    y: int
    level: int
    lines: Tuple[str, ...]
    boss: bool = False
    capture_allowed: bool = True
    story_flag: str = ""


@dataclass(frozen=True)
class ShopDef:
    key: str
    name: str
    x: int
    y: int
    items: Tuple[str, ...]


@dataclass(frozen=True)
class MapDef:
    key: str
    name: str
    kind: str
    tiles: Tuple[str, ...]
    music: str = "field"
    encounter_table: Tuple[Tuple[str, int, int], ...] = ()
    warps: Tuple[WarpDef, ...] = ()
    npcs: Tuple[NPCDef, ...] = ()
    signs: Tuple[SignDef, ...] = ()
    pickups: Tuple[PickupDef, ...] = ()
    berries: Tuple[BerryTreeDef, ...] = ()
    trainers: Tuple[TrainerDef, ...] = ()
    visibles: Tuple[VisibleEncounterDef, ...] = ()
    shops: Tuple[ShopDef, ...] = ()
    healers: Tuple[TilePos, ...] = ()
    story: Tuple[str, ...] = ()

    @property
    def width(self) -> int:
        return len(self.tiles[0])

    @property
    def height(self) -> int:
        return len(self.tiles)

    def tile_at(self, x: int, y: int) -> str:
        if y < 0 or y >= self.height or x < 0 or x >= self.width:
            return "#"
        return self.tiles[y][x]


ITEMS: Dict[str, ItemDef] = {
    "pasta_capsule": ItemDef("pasta_capsule", "Pasta Capsule", "capture", "Catches wild Brainrotmon.", 200),
    "tomato_tonic": ItemDef("tomato_tonic", "Tomato Tonic", "heal", "Restores 24 HP.", 300, 24),
    "espresso_drop": ItemDef("espresso_drop", "Espresso Drop", "status", "Wakes up a drowsy team member.", 120),
    "crema_berry": ItemDef("crema_berry", "Crema Berry", "berry", "Held or used to restore 12 HP.", 40, 12),
    "zesty_berry": ItemDef("zesty_berry", "Zesty Berry", "berry", "Held or used to clear weak static.", 60),
    "noodle_charm": ItemDef("noodle_charm", "Noodle Charm", "held", "Held item. Slightly boosts Noodle-style moves.", 700),
    "signal_shard": ItemDef("signal_shard", "Signal Shard", "evo", "A strange evolution shard from old towers.", 1200),
    "ancient_gear": ItemDef("ancient_gear", "Ancient Gear", "key", "Tunes ancient doors and broken broadcast locks."),
    "dark_lamp": ItemDef("dark_lamp", "Dark Lamp", "key", "Lets you cross blackout roads."),
    "surfboard_pass": ItemDef("surfboard_pass", "Surfboard Pass", "key", "Lets you cross coast water lanes."),
}


BADGES = (
    "Cargo Badge",
    "Crema Badge",
    "Neon Badge",
    "Coliseum Badge",
    "Gelato Badge",
    "Siren Badge",
    "Viral Badge",
    "Spire Badge",
)


STARTERS = ("ballerinacappuccina", "spaghettimon", "tungtungsahur")


TILE_WALKABLE = {
    ".",
    "g",
    "f",
    "r",
    "s",
    "i",
    "d",
    "R",
    "m",
    "c",
    "j",
    "o",
    "=",
    "D",
    "x",
}
ENCOUNTER_TILES = {"g", "j", "c", "s", "o", "R", "d"}
WATER_TILES = {"~"}


AREA_CHAIN = (
    ("starter_village", "Starter Village", "town", "village"),
    ("route_1", "Route 1: Noodle Path", "route", "field"),
    ("pasta_port", "Pasta Port", "town", "port"),
    ("tomato_fields", "Tomato Fields", "route", "farm"),
    ("espresso_quarter", "Espresso Quarter", "town", "city"),
    ("crema_bridge", "Crema Bridge", "route", "bridge"),
    ("drumwood_forest", "Drumwood Forest", "dungeon", "forest"),
    ("drumwood_shrine", "Drumwood Shrine", "dungeon", "ruins"),
    ("static_road", "Static Road", "route", "static"),
    ("neon_feed_city", "Neon Feed City", "town", "neon"),
    ("broadcast_tower", "Broadcast Tower", "dungeon", "tower"),
    ("market_mile", "Market Mile", "route", "market"),
    ("coliseum_market", "Coliseum Market", "town", "market"),
    ("olive_hills", "Olive Hills", "route", "hills"),
    ("gelato_pass", "Gelato Pass", "route", "snow"),
    ("freezer_cavern", "Freezer Cavern", "dungeon", "ice"),
    ("salt_coast", "Salt Coast", "route", "coast"),
    ("siren_pier", "Siren Pier", "town", "coast"),
    ("ruin_steps", "Ruin Steps", "route", "ruins"),
    ("static_abbey", "Static Abbey Ruins", "dungeon", "ruins"),
    ("vinewire_jungle", "Vinewire Jungle", "route", "forest"),
    ("viral_village", "Viral Village", "town", "dream"),
    ("blackout_trail", "Blackout Trail", "route", "dark"),
    ("signal_spire_city", "Signal Spire City", "town", "spire"),
    ("signal_spire", "Signal Spire", "dungeon", "tower"),
    ("crown_road", "Crown Road", "route", "final"),
    ("ancient_core", "Ancient Core", "dungeon", "ancient"),
    ("rotria_league", "Rotria League", "league", "league"),
)


ENCOUNTER_POOLS: Dict[str, Tuple[Tuple[str, int, int], ...]] = {
    "field": (("pizzaratto", 2, 4), ("spaghettimon", 2, 5), ("chimpanzinibananini", 3, 5)),
    "farm": (("pizzaratto", 4, 7), ("lasagnaconda", 5, 8), ("polentazilla", 6, 8)),
    "port": (("tralalerotralala", 3, 6), ("pizzaratto", 3, 6), ("bruschettank", 4, 7)),
    "city": (("cappuccinoassassino", 6, 9), ("ballerinacappuccina", 6, 9), ("pizzaratto", 5, 8)),
    "bridge": (("tralalerotralala", 8, 11), ("salsicciator", 8, 12), ("mozzarellion", 9, 12)),
    "forest": (("brrbrrpatapim", 10, 14), ("jungletungtungsahur", 12, 15), ("chimpanzinibananini", 10, 14)),
    "ruins": (("macaronocchio", 13, 17), ("raviolord", 14, 18), ("crostinoboss", 15, 19)),
    "static": (("vaccasaturnosaturnita", 15, 19), ("cappuccinoassassino", 14, 18), ("trendalina", 15, 20)),
    "neon": (("cappuccinoassassino", 17, 21), ("streamonello", 18, 22), ("pizzaratto", 17, 21)),
    "tower": (("streamonello", 20, 26), ("glitchocchio", 22, 28), ("vaccasaturnosaturnita", 21, 27)),
    "market": (("salsicciator", 21, 26), ("crostinoboss", 22, 27), ("bruschettank", 22, 28)),
    "hills": (("polentazilla", 24, 29), ("raviolord", 24, 30), ("lasagnaconda", 25, 30)),
    "snow": (("frigocamelo", 26, 32), ("gelatitan", 27, 33), ("brrbrrpatapim", 28, 33)),
    "ice": (("gelatitan", 30, 36), ("frigocamelo", 30, 36), ("frostbytefrappe", 31, 37)),
    "coast": (("tralalerotralala", 31, 38), ("mozzarellion", 32, 39), ("sirenacannolo", 33, 40)),
    "dream": (("macaronocchio", 36, 42), ("glitchocchio", 37, 43), ("ballerinacappuccina", 36, 42)),
    "dark": (("cappuccinoassassino", 38, 45), ("glitchocchio", 40, 46), ("shadowpanino", 40, 47)),
    "spire": (("glitchocchio", 42, 50), ("streamonello", 43, 50), ("vaccasaturnosaturnita", 44, 51)),
    "final": (("raviolord", 48, 55), ("polentazilla", 49, 55), ("mozzarellion", 50, 56)),
    "ancient": (("signaldrago", 54, 60), ("ancientlasagna", 54, 60), ("glitchocchio", 52, 58)),
    "league": (("raviolord", 56, 62), ("signaldrago", 58, 64), ("ancientlasagna", 58, 64)),
}


def _blank(width: int = 44, height: int = 26, fill: str = ".") -> List[List[str]]:
    rows = [[fill for _ in range(width)] for _ in range(height)]
    for x in range(width):
        rows[0][x] = "#"
        rows[-1][x] = "#"
    for y in range(height):
        rows[y][0] = "#"
        rows[y][-1] = "#"
    return rows


def _stamp(rows: List[List[str]], x: int, y: int, pattern: Tuple[str, ...]) -> None:
    for dy, line in enumerate(pattern):
        for dx, char in enumerate(line):
            if char != " " and 0 <= y + dy < len(rows) and 0 <= x + dx < len(rows[0]):
                rows[y + dy][x + dx] = char


def _rows(rows: List[List[str]]) -> Tuple[str, ...]:
    return tuple("".join(row) for row in rows)


def _building(rows: List[List[str]], x: int, y: int, w: int = 7, h: int = 5, door_x: int = 3) -> None:
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            rows[yy][xx] = "B"
    rows[y + h - 1][x + door_x] = "D"


def _add_tree_border(rows: List[List[str]], gaps: Tuple[Tuple[int, int], ...] = ()) -> None:
    height = len(rows)
    width = len(rows[0])
    gap_set = set(gaps)
    for x in range(width):
        if (x, 0) not in gap_set:
            rows[0][x] = "T"
        if (x, height - 1) not in gap_set:
            rows[height - 1][x] = "T"
    for y in range(height):
        if (0, y) not in gap_set:
            rows[y][0] = "T"
        if (width - 1, y) not in gap_set:
            rows[y][width - 1] = "T"


def _patch(rows: List[List[str]], x0: int, y0: int, w: int, h: int, tile: str) -> None:
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            if 0 <= y < len(rows) and 0 <= x < len(rows[0]):
                rows[y][x] = tile


def _line(rows: List[List[str]], points: Tuple[Tuple[int, int], ...], tile: str) -> None:
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        if x1 == x2:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                rows[y][x1] = tile
        elif y1 == y2:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                rows[y1][x] = tile


def _handcrafted_rows(key: str) -> Optional[List[List[str]]]:
    if key == "starter_village":
        rows = _blank(32, 24, ".")
        _add_tree_border(rows, gaps=((16, 23), (17, 23)))
        _line(rows, ((16, 23), (16, 16), (20, 16), (20, 11), (16, 11), (16, 5)), "r")
        _line(rows, ((7, 15), (26, 15)), "r")
        _building(rows, 12, 6, 10, 6, 8)
        _building(rows, 4, 12, 7, 5, 3)
        _building(rows, 23, 11, 6, 5, 2)
        _patch(rows, 3, 4, 7, 4, "f")
        _patch(rows, 22, 18, 7, 3, "g")
        rows[11][20] = "D"
        rows[15][8] = "H"
        rows[10][24] = "S"
        rows[23][16] = "x"
        return rows
    if key == "route_1":
        rows = _blank(52, 18, ".")
        _add_tree_border(rows, gaps=((0, 8), (51, 10)))
        _line(rows, ((0, 8), (7, 8), (7, 5), (17, 5), (17, 11), (31, 11), (31, 8), (42, 8), (42, 10), (51, 10)), "r")
        _patch(rows, 4, 11, 10, 5, "g")
        _patch(rows, 19, 2, 8, 5, "g")
        _patch(rows, 34, 12, 11, 4, "f")
        rows[5][17] = "S"
        rows[8][0] = "x"
        rows[10][51] = "x"
        return rows
    if key == "pasta_port":
        rows = _blank(38, 26, ".")
        _add_tree_border(rows, gaps=((0, 13), (37, 13)))
        _patch(rows, 1, 20, 36, 5, "~")
        _patch(rows, 6, 18, 11, 3, "=")
        _patch(rows, 22, 18, 9, 3, "=")
        _line(rows, ((0, 13), (11, 13), (11, 18)), "r")
        _line(rows, ((11, 13), (22, 13), (22, 18)), "r")
        _line(rows, ((22, 13), (37, 13)), "r")
        _building(rows, 5, 6, 8, 5, 3)
        _building(rows, 17, 5, 12, 6, 3)
        _building(rows, 30, 10, 6, 5, 2)
        rows[10][8] = "H"
        rows[10][20] = "D"
        rows[14][31] = "S"
        rows[13][0] = "x"
        rows[13][37] = "x"
        return rows
    if key == "drumwood_forest":
        rows = _blank(44, 30, "j")
        _add_tree_border(rows, gaps=((0, 14), (43, 14)))
        _line(rows, ((0, 14), (8, 14), (8, 6), (18, 6), (18, 18), (29, 18), (29, 9), (37, 9), (37, 14), (43, 14)), "r")
        _line(rows, ((18, 18), (18, 25), (26, 25), (26, 21), (34, 21)), "r")
        _patch(rows, 12, 10, 8, 6, "g")
        _patch(rows, 30, 3, 7, 4, "g")
        _patch(rows, 30, 20, 7, 5, ".")
        _patch(rows, 6, 20, 8, 5, "T")
        rows[14][0] = "x"
        rows[14][43] = "x"
        return rows
    if key == "neon_feed_city":
        rows = _blank(48, 30, ".")
        _add_tree_border(rows, gaps=((0, 14), (47, 14)))
        _line(rows, ((0, 14), (47, 14)), "=")
        _line(rows, ((24, 4), (24, 26)), "=")
        _line(rows, ((9, 22), (39, 22)), "=")
        _building(rows, 5, 6, 8, 5, 3)
        _building(rows, 17, 5, 10, 6, 5)
        _building(rows, 32, 6, 9, 5, 4)
        _building(rows, 8, 18, 8, 5, 3)
        _building(rows, 30, 18, 12, 6, 6)
        _stamp(rows, 36, 2, ("RRRRR", "R...R", "R...R", "RRDRR"))
        rows[10][8] = "H"
        rows[6][22] = "S"
        rows[14][0] = "x"
        rows[14][47] = "x"
        return rows
    if key == "signal_spire":
        rows = _blank(34, 30, "m")
        _line(rows, ((0, 15), (8, 15), (8, 8), (16, 8), (16, 22), (25, 22), (25, 11), (33, 11)), "R")
        _stamp(rows, 11, 10, ("RRRRRRRRRRRR", "R..m....m..R", "R..RRRRRR..R", "R..R....R..R", "R..R.dd.R..R", "R..R....R..R", "R..RRDRRR..R", "R..........R", "RRRRRRRRRRRR"))
        _patch(rows, 3, 3, 7, 4, "d")
        _patch(rows, 23, 4, 7, 5, "d")
        rows[15][0] = "x"
        rows[11][33] = "x"
        return rows
    return None


def _make_town(idx: int, key: str, name: str, theme: str) -> MapDef:
    rows = _blank(fill=".")
    path_char = "m" if theme in ("market", "neon") else "r"
    for x in range(1, 43):
        rows[13][x] = path_char
    for y in range(1, 25):
        rows[y][21] = path_char
    for x in range(6, 14):
        for y in range(4, 8):
            rows[y][x] = "f"
    for x in range(30, 38):
        for y in range(17, 22):
            rows[y][x] = "f"
    _building(rows, 5, 9, 8, 5)
    _building(rows, 17, 5, 9, 6)
    _building(rows, 30, 8, 8, 5)
    _building(rows, 14, 17, 8, 5)
    rows[10][8] = "H"
    rows[6][20] = "S"
    if theme == "port" or theme == "coast":
        for x in range(1, 43):
            rows[23][x] = "~"
        for x in range(14, 31):
            rows[22][x] = "="
    if theme in ("neon", "spire"):
        _stamp(rows, 32, 3, ("RRRRR", "R...R", "R...R", "RRDRR"))
    if theme == "dream":
        _stamp(rows, 29, 3, ("fffffff", "f.....f", "f..R..f", "fffffff"))
    return _map_from_rows(idx, key, name, "town", theme, rows)


def _make_route(idx: int, key: str, name: str, theme: str) -> MapDef:
    fill = "s" if theme == "snow" else "o" if theme == "coast" else "d" if theme == "dark" else "."
    rows = _blank(fill=fill)
    road = "s" if theme == "snow" else "o" if theme == "coast" else "r"
    for x in range(1, 43):
        rows[13][x] = road
        if x % 5 != 0:
            rows[12][x] = road
    for x0, y0, w, h, tile in (
        (3, 3, 11, 7, "g"),
        (27, 4, 12, 6, "g"),
        (8, 17, 12, 6, "g"),
        (28, 17, 10, 5, "f"),
    ):
        if theme in ("forest", "dark"):
            tile = "j"
        elif theme in ("ruins", "final"):
            tile = "R"
        elif theme == "snow":
            tile = "s"
        elif theme == "coast":
            tile = "o"
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                if 0 < x < 43 and 0 < y < 25:
                    rows[y][x] = tile
    if theme in ("bridge", "coast"):
        for y in range(1, 25):
            rows[y][21] = "~"
        for y in range(11, 16):
            rows[y][21] = "="
    if theme in ("hills", "final"):
        for x in range(10, 35):
            rows[6][x] = "#"
            rows[20][x] = "#"
    return _map_from_rows(idx, key, name, "route", theme, rows)


def _make_dungeon(idx: int, key: str, name: str, theme: str) -> MapDef:
    floor = "c" if theme in ("ice", "tower") else "R" if theme in ("ruins", "ancient") else "j"
    rows = _blank(fill=floor)
    for x in range(4, 40):
        rows[5][x] = "."
        rows[13][x] = "."
        rows[21][x] = "."
    for y in range(3, 23):
        rows[y][8] = "."
        rows[y][21] = "."
        rows[y][35] = "."
    for x in range(12, 18):
        for y in range(8, 12):
            rows[y][x] = "#"
    for x in range(25, 31):
        for y in range(15, 19):
            rows[y][x] = "#"
    if theme == "ice":
        for x in range(9, 35):
            rows[9][x] = "i"
            rows[17][x] = "i"
    if theme == "tower":
        _stamp(rows, 17, 9, ("RRRRRRRR", "R......R", "R..RR..R", "R......R", "RRRRRRRR"))
    if theme == "ancient":
        _stamp(rows, 16, 8, ("RRRRRRRRR", "R...d...R", "R..ddd..R", "R...d...R", "RRRRDRRRR"))
    return _map_from_rows(idx, key, name, "dungeon", theme, rows)


def _league(idx: int, key: str, name: str, theme: str) -> MapDef:
    rows = _blank(fill="m")
    for x in range(8, 36):
        for y in range(4, 22):
            rows[y][x] = "."
    for x in range(12, 32):
        rows[7][x] = "R"
        rows[18][x] = "R"
    for y in range(7, 19):
        rows[y][12] = "R"
        rows[y][31] = "R"
    rows[18][21] = "D"
    return _map_from_rows(idx, key, name, "league", theme, rows)


def _map_from_rows(idx: int, key: str, name: str, kind: str, theme: str, rows: List[List[str]]) -> MapDef:
    prev_key = AREA_CHAIN[idx - 1][0] if idx > 0 else ""
    next_key = AREA_CHAIN[idx + 1][0] if idx < len(AREA_CHAIN) - 1 else ""
    width = len(rows[0])
    height = len(rows)
    mid_y = min(height - 2, max(1, height // 2))
    warps: List[WarpDef] = []
    if prev_key:
        rows[mid_y][0] = "x"
        prev_rows = _handcrafted_rows(prev_key)
        prev_width = len(prev_rows[0]) if prev_rows else 44
        prev_height = len(prev_rows) if prev_rows else 26
        warps.append(WarpDef(0, mid_y, prev_key, prev_width - 2, min(prev_height - 2, max(1, prev_height // 2)), "west"))
    if next_key:
        rows[mid_y][width - 1] = "x"
        next_rows = _handcrafted_rows(next_key)
        next_height = len(next_rows) if next_rows else 26
        warps.append(WarpDef(width - 1, mid_y, next_key, 1, min(next_height - 2, max(1, next_height // 2)), "east"))
    if key == "starter_village":
        rows[mid_y][width - 1] = "T"
        warps = [warp for warp in warps if warp.target_map != "route_1"]
        rows[height - 1][16] = "x"
        warps.append(WarpDef(16, height - 1, "route_1", 1, 8, "south"))
    if key == "route_1":
        warps = [WarpDef(warp.x, warp.y, warp.target_map, 16, 22, warp.label) if warp.target_map == "starter_village" else warp for warp in warps]
    if key == "starter_village":
        warps.append(WarpDef(20, 10, "prof_lab", 21, 20, "Professor's Lab"))
    if key == "pasta_port":
        warps.append(WarpDef(8, 10, "cargo_warehouse", 20, 21, "Cargo Warehouse"))
    if key == "neon_feed_city":
        warps.append(WarpDef(34, 6, "broadcast_tower", 21, 21, "Broadcast Tower"))
    if key == "gelato_pass":
        warps.append(WarpDef(35, 13, "freezer_cavern", 21, 21, "Freezer Cavern"))
    if key == "ruin_steps":
        warps.append(WarpDef(35, 13, "static_abbey", 21, 21, "Static Abbey"))
    if key == "signal_spire_city":
        warps.append(WarpDef(34, 6, "signal_spire", 21, 21, "Signal Spire"))
    if key == "crown_road":
        warps.append(WarpDef(35, 13, "ancient_core", 21, 21, "Ancient Core"))

    npcs = _default_npcs(idx, key, name, kind, theme)
    signs = (
        SignDef(3, 3, (name, "Rotria routes carry rumors, berries, and trouble.")),
        SignDef(min(width - 5, 39), min(height - 4, 22), ("Trainer Tip:", "Night changes wild Brainrotmon and some NPCs.")),
    )
    pickups = (
        PickupDef(f"{key}_pickup_1", "tomato_tonic", min(width - 4, 7), min(height - 4, 21), 1, hidden=False),
        PickupDef(f"{key}_hidden_1", "pasta_capsule", min(width - 5, 37), 4, 1, hidden=True),
    )
    berries = (
        BerryTreeDef(f"{key}_berry_1", "crema_berry", min(width - 4, 5), 5, 2),
        BerryTreeDef(f"{key}_berry_2", "zesty_berry", min(width - 5, 39), min(height - 5, 18), 2),
    ) if kind in ("route", "town") else ()
    trainers = _trainers_for(idx, key, theme, kind)
    visibles = _visibles_for(idx, key, theme)
    shops = ()
    healers = ()
    if kind == "town" or kind == "league":
        healers = ((min(width - 3, 8), min(height - 3, 10)),)
        shops = (ShopDef(f"{key}_shop", f"{name} Counter", min(width - 3, 20), min(height - 3, 6), ("pasta_capsule", "tomato_tonic", "espresso_drop", "crema_berry")),)
    return MapDef(
        key=key,
        name=name,
        kind=kind,
        tiles=_rows(rows),
        music=theme,
        encounter_table=ENCOUNTER_POOLS.get(theme, ENCOUNTER_POOLS["field"]),
        warps=tuple(warps),
        npcs=npcs,
        signs=signs,
        pickups=pickups,
        berries=berries,
        trainers=trainers,
        visibles=visibles,
        shops=shops,
        healers=healers,
        story=story_lines_for(key),
    )


def _default_npcs(idx: int, key: str, name: str, kind: str, theme: str) -> Tuple[NPCDef, ...]:
    area_rows = _handcrafted_rows(key)
    width = len(area_rows[0]) if area_rows else 44
    height = len(area_rows) if area_rows else 26
    custom_positions = {
        "starter_village": ((7, 15), (25, 15), (25, 19)),
        "route_1": ((10, 8), (34, 10), (23, 5)),
        "pasta_port": ((11, 18), (28, 18), (31, 13)),
        "drumwood_forest": ((8, 12), (30, 21), (36, 9)),
        "neon_feed_city": ((13, 14), (24, 22), (36, 14)),
        "signal_spire": ((8, 15), (16, 22), (25, 11)),
    }.get(key)
    if custom_positions:
        first_pos, second_pos, third_pos = custom_positions
    else:
        first_pos = (min(width - 3, 8), min(height - 3, 13)) if kind == "dungeon" else (min(width - 3, 12), min(height - 3, 11))
        second_pos = (min(width - 3, 21), min(height - 3, 13)) if kind == "dungeon" else (min(width - 3, 28), min(height - 3, 15))
        third_pos = (min(width - 3, 35 if kind != "dungeon" else 29), min(height - 3, 10 if kind != "dungeon" else 18))
    return (
        NPCDef(
            f"{key}_rumor",
            "Rumor Kid" if kind != "dungeon" else "Lost Scout",
            first_pos[0],
            first_pos[1],
            (
                f"{name} has its own static pattern.",
                "Listen close and the signal almost sounds like a voice.",
            ),
            night_lines=("At night the radio clicks without batteries.", "I do not like that at all."),
        ),
        NPCDef(
            f"{key}_guide",
            "Route Guide" if kind == "route" else "Local",
            second_pos[0],
            second_pos[1],
            (
                "Berry trees grow back after a rest.",
                "Team Scroll keeps asking kids to sell fake evolutions.",
            ),
            night_lines=("The same street feels longer after sunset.",),
        ),
        NPCDef(
            f"{key}_scroll_watcher",
            "Static Watcher" if kind == "dungeon" else "Berry Auntie",
            third_pos[0],
            third_pos[1],
            (
                "Team Scroll tried to recruit me. I said no.",
                "They took my berry tree anyway. Very normal behavior.",
            ),
            night_lines=("The towers hum at 3am. My Brainrotmon hums back.",),
        ),
    )


def _trainers_for(idx: int, key: str, theme: str, kind: str) -> Tuple[TrainerDef, ...]:
    area_rows = _handcrafted_rows(key)
    width = len(area_rows[0]) if area_rows else 44
    height = len(area_rows) if area_rows else 26
    if kind == "town":
        badge_index = {
            "pasta_port": 0,
            "espresso_quarter": 1,
            "neon_feed_city": 2,
            "coliseum_market": 3,
            "gelato_pass": 4,
            "siren_pier": 5,
            "viral_village": 6,
            "signal_spire_city": 7,
        }.get(key)
        if badge_index is not None:
            team_key = ("crostinoboss", "ballerinacappuccina", "streamonello", "salsicciator", "gelatitan", "tralalerotralala", "glitchocchio", "signaldrago")[badge_index]
            return (
                TrainerDef(
                    f"leader_{key}",
                    ("Dockmaster Ragu", "Prima Crema", "VJ Neon", "Mara Coliseo", "Gelato Nora", "Captain Sirena", "Somni Vale", "Warden Spire")[badge_index],
                    min(width - 3, 25),
                    min(height - 3, 13),
                    ((team_key, 8 + badge_index * 6),),
                    (
                        "A badge is not a prize. It is a seal key.",
                        "Show me your team can carry that weight.",
                    ),
                    600 + badge_index * 220,
                    trainer_class="Leader",
                    badge=BADGES[badge_index],
                    story_flag=f"badge_{badge_index + 1}",
                ),
            )
        return ()
    if key == "rotria_league":
        return (
            TrainerDef("league_1", "Elite Chef Basil", 16, 10, (("raviolord", 58), ("lasagnaconda", 59)), ("The league kitchen is closed to weak sauce.",), 2400, "Elite"),
            TrainerDef("league_2", "Champion Lira", 26, 10, (("signaldrago", 62), ("ancientlasagna", 64)), ("Rotria hears you. Answer with courage.",), 4200, "Champion", story_flag="league_clear"),
        )
    base = max(3, 2 + idx * 2)
    pool = ENCOUNTER_POOLS.get(theme, ENCOUNTER_POOLS["field"])
    return (
        TrainerDef(
            f"{key}_trainer_a",
            ("Courier", "Streamer", "Chef", "Hiker", "Archivist")[idx % 5] + f" {idx + 1}",
            min(width - 3, 16),
            min(height - 3, 12),
            ((pool[0][0], base),),
            ("I heard your footsteps sync with the static.", "Battle me before the signal does."),
            90 + idx * 35,
            trainer_class=("Courier", "Streamer", "Chef", "Hiker", "Archivist")[idx % 5],
        ),
        TrainerDef(
            f"{key}_trainer_b",
            ("Cafe Kid", "Dock Worker", "Scout", "Collector", "Scroll Grunt")[idx % 5] + f" {idx + 2}",
            min(width - 3, 31),
            min(height - 3, 17),
            ((pool[-1][0], base + 1),),
            ("Team Scroll says viral power is free.", "I say nothing free has clean edges."),
            110 + idx * 35,
            trainer_class=("Cafe Kid", "Dock Worker", "Scout", "Collector", "Scroll Grunt")[idx % 5],
        ),
    )


def _visibles_for(idx: int, key: str, theme: str) -> Tuple[VisibleEncounterDef, ...]:
    if key == "drumwood_forest":
        return (VisibleEncounterDef("jungle_tung_event", "jungletungtungsahur", 34, 8, 16, ("A wooden beat echoes from the leaves.", "Jungle Tung Tung Sahur stomps out!"), boss=True),)
    if key == "broadcast_tower":
        return (VisibleEncounterDef("tower_signal_boss", "glitchocchio", 21, 9, 28, ("The broadcast folds into a face.", "A corrupted Brainrotmon attacks!"), boss=True, capture_allowed=False, story_flag="tower_clear"),)
    if key == "ancient_core":
        return (VisibleEncounterDef("ancient_final", "signaldrago", 21, 10, 62, ("The Ancient Signal stops hiding.", "Rotria's old seal breaks open!"), boss=True, capture_allowed=False, story_flag="ancient_signal_quieted"),)
    if idx % 4 == 0 and idx > 0:
        area_rows = _handcrafted_rows(key)
        width = len(area_rows[0]) if area_rows else 44
        pool = ENCOUNTER_POOLS.get(theme, ENCOUNTER_POOLS["field"])
        return (VisibleEncounterDef(f"{key}_rare", pool[-1][0], min(width - 3, 36), 6, pool[-1][2] + 2, ("A rare Brainrotmon watches you.",), boss=False),)
    return ()


def story_lines_for(key: str) -> Tuple[str, ...]:
    story = {
        "starter_village": (
            "Professor Menta says the League badges are old seal keys.",
            "Your Rotria Gear crackles before it is even turned on.",
        ),
        "pasta_port": (
            "Team Scroll is moving stolen capsules through the docks.",
            "The Cargo Badge hums when the harbor tower blinks.",
        ),
        "drumwood_shrine": (
            "The tablet shows eight leaders standing around a black sun.",
            "One phrase repeats: when the feed wakes, do not answer alone.",
        ),
        "neon_feed_city": (
            "The tower broadcasts your rival's voice before they arrive.",
            "Team Scroll thinks they can sell the signal. The signal is selling them.",
        ),
        "static_abbey": (
            "The abbey reveals the Ancient Signal was not created. It was contained.",
            "Every badge is a lock. Every tower is a mistake.",
        ),
        "signal_spire": (
            "Team Scroll breaks the seal trying to force a viral evolution.",
            "Your rival steps into the static to prove they are stronger.",
        ),
        "ancient_core": (
            "The ruins breathe like a sleeping radio.",
            "Rotria asks for one final battle.",
        ),
        "rotria_league": (
            "The League is no longer just sport.",
            "The champion tests whether Rotria can trust you with its quiet.",
        ),
    }
    return story.get(key, ())


def build_maps() -> Dict[str, MapDef]:
    maps: Dict[str, MapDef] = {}
    for idx, (key, name, kind, theme) in enumerate(AREA_CHAIN):
        hand_rows = _handcrafted_rows(key)
        if hand_rows is not None:
            maps[key] = _map_from_rows(idx, key, name, kind, theme, hand_rows)
        elif kind == "town":
            maps[key] = _make_town(idx, key, name, theme)
        elif kind == "dungeon":
            maps[key] = _make_dungeon(idx, key, name, theme)
        elif kind == "league":
            maps[key] = _league(idx, key, name, theme)
        else:
            maps[key] = _make_route(idx, key, name, theme)
    maps["prof_lab"] = _important_interior(
        "prof_lab",
        "Professor Menta's Lab",
        "Professor Menta",
        ("Rotria's signal is old, not new.", "Choose a partner and keep notes in your Brainrotdex."),
        WarpDef(21, 23, "starter_village", 20, 11, "exit"),
    )
    maps["cargo_warehouse"] = _important_interior(
        "cargo_warehouse",
        "Cargo Warehouse",
        "Scroll Lookout",
        ("These crates are totally normal.", "Do not shake the one making monster noises."),
        WarpDef(20, 23, "pasta_port", 8, 11, "exit"),
        trainer=TrainerDef("scroll_cargo_admin", "Admin Hashtag", 20, 12, (("pizzaratto", 8), ("crostinoboss", 9)), ("Team Scroll ships trends before they expire.",), 480, "Team Scroll", story_flag="cargo_scroll_clear"),
    )
    return maps


def _important_interior(
    key: str,
    name: str,
    npc_name: str,
    lines: Tuple[str, ...],
    exit_warp: WarpDef,
    trainer: Optional[TrainerDef] = None,
) -> MapDef:
    rows = _blank(width=30, height=24, fill="m")
    for x in range(3, 27):
        for y in range(3, 21):
            rows[y][x] = "."
    rows[23][exit_warp.x] = "x"
    npcs = (NPCDef(f"{key}_npc", npc_name, 11, 10, lines),)
    trainers = (trainer,) if trainer else ()
    pickups = (PickupDef(f"{key}_desk_item", "signal_shard", 24, 6, 1),)
    return MapDef(
        key=key,
        name=name,
        kind="interior",
        tiles=_rows(rows),
        encounter_table=(),
        warps=(exit_warp,),
        npcs=npcs,
        signs=(SignDef(8, 5, (name, "Rotria records are stacked in careful little piles.")),),
        pickups=pickups,
        trainers=trainers,
    )


MAPS = build_maps()


# Pixel anchors for the generated 1536x1024 Rotria map artwork.
MAP_POIS: Dict[str, Tuple[int, int, str]] = {
    "starter_village": (176, 176, "Home"),
    "route_1": (244, 306, "Route"),
    "pasta_port": (164, 790, "Port"),
    "tomato_fields": (280, 420, "Fields"),
    "espresso_quarter": (744, 494, "City"),
    "crema_bridge": (526, 492, "Bridge"),
    "drumwood_forest": (466, 214, "Forest"),
    "drumwood_shrine": (642, 162, "Shrine"),
    "static_road": (878, 384, "Route"),
    "neon_feed_city": (746, 500, "City"),
    "broadcast_tower": (940, 230, "Tower"),
    "market_mile": (966, 518, "Route"),
    "coliseum_market": (1288, 118, "Market"),
    "olive_hills": (548, 722, "Hills"),
    "gelato_pass": (1070, 188, "Snow"),
    "freezer_cavern": (1164, 228, "Cave"),
    "salt_coast": (1298, 514, "Coast"),
    "siren_pier": (1360, 670, "Pier"),
    "ruin_steps": (420, 612, "Ruins"),
    "static_abbey": (444, 642, "Abbey"),
    "vinewire_jungle": (842, 730, "Jungle"),
    "viral_village": (928, 690, "Village"),
    "blackout_trail": (1050, 682, "Trail"),
    "signal_spire_city": (1120, 628, "City"),
    "signal_spire": (1130, 504, "Spire"),
    "crown_road": (765, 840, "Road"),
    "ancient_core": (1008, 792, "Core"),
    "rotria_league": (1290, 116, "League"),
    "prof_lab": (176, 176, "Lab"),
    "cargo_warehouse": (164, 790, "Warehouse"),
}
