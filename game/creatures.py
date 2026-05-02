from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class MoveDef:
    name: str
    power: int
    accuracy: int
    flavor: str
    anim_key: str


@dataclass(frozen=True)
class EvolutionDef:
    evolves_to: str
    level_required: int
    flavor: str = ""


@dataclass(frozen=True)
class CreatureDef:
    key: str
    name: str
    kind: str
    max_hp: int
    attack: int
    defense: int
    moves: List[MoveDef]
    capture_rate: float
    description: str
    evolution: Optional[EvolutionDef] = None


CREATURES: Dict[str, CreatureDef] = {
    "spaghettimon": CreatureDef(
        "spaghettimon",
        "Spaghettimon",
        "Noodle",
        36,
        8,
        5,
        [
            MoveDef("Fork Flick", 8, 100, "Quick noodle crack.", "fork_flick"),
            MoveDef("Sauce Splash", 11, 95, "Tomato blast.", "sauce_splash"),
            MoveDef("Al Dente Slam", 14, 90, "Firm pasta body hit.", "al_dente_slam"),
            MoveDef("Meatball Panic", 17, 85, "Heavy panic swing.", "meatball_panic"),
        ],
        0.42,
        "Sauce-faced noodle brute. Loud and wild.",
        None,
    ),
    "tungtungsahur": CreatureDef(
        "tungtungsahur",
        "Tungtung Sahur",
        "Rhythm/Wood",
        38,
        9,
        5,
        [
            MoveDef("Drum Knock", 8, 100, "Wake-up tap.", "drum_knock"),
            MoveDef("Sahur Burst", 11, 96, "Percussion shock.", "sahur_burst"),
            MoveDef("Tung Roll", 15, 91, "Charging drum combo.", "tung_roll"),
            MoveDef("Midnight March", 18, 84, "Street-shaking rhythm rush.", "midnight_march"),
        ],
        0.30,
        "Living dawn drum totem. Loud and wooden.",
        None,
    ),
    "ballerinacappuccina": CreatureDef(
        "ballerinacappuccina",
        "Ballerina Cappuccina",
        "Foam/Grace",
        33,
        8,
        6,
        [
            MoveDef("Pirouette Pour", 8, 100, "Neat spin strike.", "pirouette_pour"),
            MoveDef("Foam Ribbon", 10, 97, "Soft-looking slice.", "foam_ribbon"),
            MoveDef("Arabesque Roast", 14, 91, "Elegant heat lash.", "arabesque_roast"),
            MoveDef("Finale Froth", 17, 85, "Recital-ending surge.", "finale_froth"),
        ],
        0.34,
        "Whimsical foam prima. Graceful and absurd.",
        None,
    ),
    "tralalerotralala": CreatureDef(
        "tralalerotralala",
        "Tralalero Tralala",
        "Sneaker/Shark",
        37,
        9,
        5,
        [
            MoveDef("Sneaker Snap", 8, 100, "Fast shoe bite.", "sneaker_snap"),
            MoveDef("Tralala Wave", 11, 96, "Singing surf blast.", "tralala_wave"),
            MoveDef("Reef Rush", 15, 91, "Blue rush tackle.", "reef_rush"),
            MoveDef("Coral Chorus", 18, 84, "Big opera reef boom.", "coral_chorus"),
        ],
        0.31,
        "Sneakered opera shark. Loud, fast, ridiculous.",
        None,
    ),
    "cappuccinoassassino": CreatureDef(
        "cappuccinoassassino",
        "Cappuccino Assassino",
        "Crema/Blade",
        34,
        10,
        5,
        [
            MoveDef("Silent Sip", 8, 100, "Quiet cut-in strike.", "silent_sip"),
            MoveDef("Crema Dagger", 11, 95, "Foam knife throw.", "crema_dagger"),
            MoveDef("Shadow Roast", 14, 92, "Dark roast slash.", "shadow_roast"),
            MoveDef("Espresso Exit", 17, 86, "Blink-fast brew finisher.", "espresso_exit"),
        ],
        0.28,
        "Stealth killer brew. Smooth foam, sharp finish.",
        None,
    ),
    "vaccasaturnosaturnita": CreatureDef(
        "vaccasaturnosaturnita",
        "Vacca Saturno Saturnita",
        "Cosmic/Milk",
        40,
        8,
        7,
        [
            MoveDef("Orbit Kick", 8, 100, "Ringed boot to chin.", "orbit_kick"),
            MoveDef("Milky Way Moo", 10, 97, "Space moo shockwave.", "milky_way_moo"),
            MoveDef("Ring Charge", 14, 92, "Saturn ring launch.", "ring_charge"),
            MoveDef("Nova Hoof", 17, 86, "Star-hoof crash.", "nova_hoof"),
        ],
        0.24,
        "Sleepy ringed space cow. Heavy and strange.",
        None,
    ),
    "bombardirocrocodilo": CreatureDef(
        "bombardirocrocodilo",
        "Bombardiro Crocodilo",
        "Bomber/Reptile",
        39,
        9,
        6,
        [
            MoveDef("Runway Rush", 8, 100, "Fast taxi slam.", "runway_rush"),
            MoveDef("Bomb Burst", 11, 95, "Explosive egg drop.", "bomb_burst"),
            MoveDef("Croco Cannon", 15, 90, "Armored launch strike.", "croco_cannon"),
            MoveDef("Tail Rotor", 18, 84, "Whirling finisher.", "tail_rotor"),
        ],
        0.27,
        "Warplane croc menace. Loud, fast, dangerous.",
        None,
    ),
    "frigocamelo": CreatureDef(
        "frigocamelo",
        "Frigo Camelo",
        "Ice/Desert",
        41,
        8,
        7,
        [
            MoveDef("Cooler Kick", 8, 100, "Cold hoof thump.", "cooler_kick"),
            MoveDef("Frost Spit", 10, 97, "Chilled spit shot.", "frost_spit"),
            MoveDef("Ice Box Crash", 14, 92, "Fridge-body crush.", "ice_box_crash"),
            MoveDef("Desert Chill", 17, 86, "Frozen dune wave.", "desert_chill"),
        ],
        0.25,
        "Refrigerator camel hybrid. Cold hump, hot attitude.",
        None,
    ),
    "brrbrrpatapim": CreatureDef(
        "brrbrrpatapim",
        "Brr Brr Patapim",
        "Forest/Winter",
        36,
        9,
        6,
        [
            MoveDef("Branch Bonk", 8, 100, "Wooden smack.", "branch_bonk"),
            MoveDef("Pinecone Pop", 11, 96, "Spiky cone launch.", "pinecone_pop"),
            MoveDef("Brrr Blast", 14, 91, "Cold forest boom.", "brrr_blast"),
            MoveDef("Mossy Mayhem", 17, 85, "Wild root finisher.", "mossy_mayhem"),
        ],
        0.29,
        "Snowy woodland freak. Chattery, jumpy, mean.",
        None,
    ),
    "chimpanzinibananini": CreatureDef(
        "chimpanzinibananini",
        "Chimpanzini Bananini",
        "Banana/Prank",
        35,
        10,
        5,
        [
            MoveDef("Peel Jab", 8, 100, "Quick peel poke.", "peel_jab"),
            MoveDef("Banana Boomerang", 11, 95, "Curved banana throw.", "banana_boomerang"),
            MoveDef("Monkey Mash", 14, 91, "Hyper primate pummel.", "monkey_mash"),
            MoveDef("Bananini Barrage", 17, 86, "Ridiculous fruit storm.", "bananini_barrage"),
        ],
        0.32,
        "Banana chimp prankster. Fast hands, zero dignity.",
        None,
    ),
    "pizzaratto": CreatureDef(
        "pizzaratto",
        "Pizzaratto",
        "Street/Cheese",
        35,
        9,
        5,
        [
            MoveDef("Scurry Slice", 8, 100, "Rat-fast crust cut.", "scurry_slice"),
            MoveDef("Crust Comet", 11, 95, "Flying pizza wedge.", "crust_comet"),
            MoveDef("Mozza Mob", 14, 91, "Cheese riot burst.", "mozza_mob"),
            MoveDef("Oven Ambush", 17, 86, "Hot alley crash.", "oven_ambush"),
        ],
        0.33,
        "Street pizza rat. Greasy, quick, unashamed.",
        None,
    ),
    "lasagnaconda": CreatureDef(
        "lasagnaconda",
        "Lasagnaconda",
        "Layer/Serpent",
        39,
        8,
        6,
        [
            MoveDef("Layer Lash", 8, 100, "Ribbon-pan whip.", "layer_lash"),
            MoveDef("Ricotta Rattle", 11, 96, "Creamy shake shot.", "ricotta_rattle"),
            MoveDef("Coil Crush", 15, 91, "Heavy tray squeeze.", "coil_crush"),
            MoveDef("Bake Coil", 18, 85, "Oven-hot finishing curl.", "bake_coil"),
        ],
        0.29,
        "Stacked pasta serpent. Slow glare, brutal squeeze.",
        None,
    ),
    "gelatitan": CreatureDef(
        "gelatitan",
        "Gelatitan",
        "Gelato/Frost",
        38,
        8,
        6,
        [
            MoveDef("Scoop Smack", 8, 100, "Cold cone pop.", "scoop_smack"),
            MoveDef("Frost Swirl", 11, 96, "Spinning gelato ribbon.", "frost_swirl"),
            MoveDef("Sundae Slide", 14, 92, "Melty rush attack.", "sundae_slide"),
            MoveDef("Brain Freeze", 17, 86, "Chilling final blast.", "brain_freeze"),
        ],
        0.30,
        "Titan scoop monster. Sweet face, freezing body.",
        None,
    ),
    "polentazilla": CreatureDef(
        "polentazilla",
        "Polentazilla",
        "Corn/Kaiju",
        42,
        9,
        7,
        [
            MoveDef("Kernel Kick", 8, 100, "Stubby kaiju boot.", "kernel_kick"),
            MoveDef("Corn Quake", 11, 96, "Ground-shaking mash.", "corn_quake"),
            MoveDef("Golden Roar", 14, 91, "Cornfield shockwave.", "golden_roar"),
            MoveDef("Polenta Meteor", 18, 85, "Hot slab from sky.", "polenta_meteor"),
        ],
        0.24,
        "Chunky corn kaiju. Heavy steps, louder stomach.",
        None,
    ),
    "macaronocchio": CreatureDef(
        "macaronocchio",
        "Macaronocchio",
        "Puppet/Sugar",
        36,
        9,
        6,
        [
            MoveDef("String Sting", 8, 100, "Snap-forward jab.", "string_sting"),
            MoveDef("Ganache Glint", 11, 95, "Sweet blade toss.", "ganache_glint"),
            MoveDef("Puppet Pivot", 14, 91, "Twisting marionette rush.", "puppet_pivot"),
            MoveDef("Marzipan Mirage", 17, 86, "Stage-filling sugar bloom.", "marzipan_mirage"),
        ],
        0.28,
        "Sugary puppet schemer. Pretty face, crooked strings.",
        None,
    ),
    "raviolord": CreatureDef(
        "raviolord",
        "Raviolord",
        "Royal/Pasta",
        38,
        9,
        6,
        [
            MoveDef("Crown Crimp", 8, 100, "Royal snap strike.", "crown_crimp"),
            MoveDef("Sauce Decree", 11, 95, "Commanding sauce shot.", "sauce_decree"),
            MoveDef("Noble Fold", 14, 91, "Heavy ravioli rush.", "noble_fold"),
            MoveDef("Ravioli Reign", 17, 86, "Courtwide pasta bloom.", "ravioli_reign"),
        ],
        0.31,
        "Stuffed pasta king. Regal stare, rich sauce.",
        None,
    ),
    "salsicciator": CreatureDef(
        "salsicciator",
        "Salsicciator",
        "Sausage/Arena",
        39,
        9,
        6,
        [
            MoveDef("Link Lash", 8, 100, "Snapping chain whip.", "link_lash"),
            MoveDef("Pepper Spear", 11, 95, "Seasoned spear throw.", "pepper_spear"),
            MoveDef("Grill Grind", 14, 91, "Hot arena rush.", "grill_grind"),
            MoveDef("Coliseum Sear", 17, 86, "Roaring stadium burn.", "coliseum_sear"),
        ],
        0.29,
        "Arena sausage brute. Proud, greasy, brutal.",
        None,
    ),
    "crostinoboss": CreatureDef(
        "crostinoboss",
        "Crostinoboss",
        "Toast/Boss",
        37,
        9,
        6,
        [
            MoveDef("Crust Cudgel", 8, 100, "Bossy bread smack.", "crust_cudgel"),
            MoveDef("Olive Order", 11, 96, "Olive shot command.", "olive_order"),
            MoveDef("Toast Takedown", 14, 91, "Heavy crostini drop.", "toast_takedown"),
            MoveDef("Boss Banquet", 17, 85, "Mob feast finisher.", "boss_banquet"),
        ],
        0.30,
        "Crunchy mob capo. Slick grin, hard crust.",
        None,
    ),
    "bruschettank": CreatureDef(
        "bruschettank",
        "Bruschettank",
        "Toast/Tank",
        41,
        8,
        7,
        [
            MoveDef("Toast Tread", 8, 100, "Rolling toast crush.", "toast_tread"),
            MoveDef("Tomato Mortar", 11, 95, "Lobbed tomato blast.", "tomato_mortar"),
            MoveDef("Garlic Guard", 14, 92, "Shielding clove bash.", "garlic_guard"),
            MoveDef("Bruschetta Barrage", 17, 86, "Tank-top topping storm.", "bruschetta_barrage"),
        ],
        0.26,
        "Armored bruschetta tank. Crunchy hull, loud topping.",
        None,
    ),
    "mozzarellion": CreatureDef(
        "mozzarellion",
        "Mozzarellion",
        "Cheese/Pride",
        40,
        8,
        7,
        [
            MoveDef("Curd Claw", 8, 100, "Quick cheese claw.", "curd_claw"),
            MoveDef("Stretch Beam", 11, 96, "Elastic cheese ribbon.", "stretch_beam"),
            MoveDef("Pride Pounce", 14, 91, "Mane-first body hit.", "pride_pounce"),
            MoveDef("Melt Majesty", 17, 86, "Glorious molten finish.", "melt_majesty"),
        ],
        0.27,
        "Noble cheese lion. Proud mane, soft center.",
        None,
    ),
}

CREATURES["jungletungtungsahur"] = CreatureDef(
    "jungletungtungsahur",
    "Jungle Tung Tung Sahur",
    "Wood/Rhythm",
    41,
    9,
    7,
    [
        MoveDef("Drum Knock", 8, 100, "Mossy wake-up tap.", "drum_knock"),
        MoveDef("Sahur Burst", 11, 96, "Canopy percussion shock.", "sahur_burst"),
        MoveDef("Tung Roll", 15, 91, "Charging jungle drum combo.", "tung_roll"),
        MoveDef("Midnight March", 18, 84, "Leaf-shaking rhythm rush.", "midnight_march"),
    ],
    0.22,
    "Older wild cousin of the starter Tung line. Jungle bark, louder heart.",
    None,
)


def _generated_move_set(base_key: str) -> List[MoveDef]:
    return list(CREATURES[base_key].moves)


_EXTRA_CREATURE_SPECS = [
    ("streamonello", "Streamonello", "Signal/Street", "A tiny streamer imp with a cracked halo of notifications.", "cappuccinoassassino"),
    ("trendalina", "Trendalina", "Signal/Grace", "A graceful trend spirit whose ribbons copy every move a second late.", "ballerinacappuccina"),
    ("glitchocchio", "Glitchocchio", "Signal/Shadow", "A puppet error that smiles one frame too late.", "macaronocchio"),
    ("signaldrago", "Signaldrago", "Signal/Ancient", "Legendary tower dragon made of old broadcasts and gold wire.", "vaccasaturnosaturnita"),
    ("ancientlasagna", "Ancient Lasagna", "Ancient/Noodle", "Layered ruin beast sealed under Rotria's first kitchens.", "lasagnaconda"),
    ("shadowpanino", "Shadow Panino", "Shadow/Street", "A sandwich-shaped rumor that waits under bad streetlights.", "crostinoboss"),
    ("frostbytefrappe", "Frostbyte Frappe", "Frost/Foam", "Cold cafe spirit whose cup frosts over when lies are told.", "gelatitan"),
    ("sirenacannolo", "Sirena Cannolo", "Coast/Grace", "A pastry siren that sings through sugar-shell waves.", "tralalerotralala"),
    ("cachecow", "Cache Cow", "Signal/Foam", "Stores every sound it hears and moo-replays them at dawn.", "vaccasaturnosaturnita"),
    ("modemozza", "Modemozza", "Signal/Cheese", "Cheese lion with a dial-up roar and a proud little mane.", "mozzarellion"),
    ("tagliatellimp", "Tagliatellimp", "Noodle/Shadow", "Noodle prankster that ties shoe laces into cursed bows.", "spaghettimon"),
    ("risottornado", "Risottornado", "Coast/Noodle", "A spinning bowl storm that leaves grains in perfect circles.", "tralalerotralala"),
    ("cappucciclown", "Cappucci Clown", "Foam/Street", "A clownish cup that juggles spoons with unsettling focus.", "ballerinacappuccina"),
    ("gondoloblin", "Gondoloblin", "Coast/Shadow", "Small canal goblin that rows backward and never apologizes.", "cappuccinoassassino"),
    ("pastaflame", "Pastaflame", "Sauce/Noodle", "Hot-headed noodle sprite with a candle-bright temper.", "spaghettimon"),
    ("limonelancer", "Limone Lancer", "Grace/Street", "Citrus duelist whose peel shield smells sharply heroic.", "salsicciator"),
    ("basilisketti", "Basilisketti", "Noodle/Wood", "Herb-serpent pasta that petrifies weak recipes.", "lasagnaconda"),
    ("mochamoth", "Mocha Moth", "Foam/Shadow", "Night cafe moth drawn to glowing espresso machines.", "cappuccinoassassino"),
    ("pepperoninja", "Pepperoninja", "Sauce/Shadow", "A silent slice that leaves spicy footprints.", "pizzaratto"),
    ("gnocchighost", "Gnocchi Ghost", "Ancient/Foam", "Soft dumpling spirit from abandoned village kitchens.", "macaronocchio"),
    ("arancinitank", "Arancini Tank", "Street/Sauce", "Golden rice armor with a molten center and zero chill.", "bruschettank"),
    ("tiramisufoe", "Tiramisu Foe", "Foam/Shadow", "Elegant dessert menace that stacks grudges in layers.", "raviolord"),
    ("ravioliraptor", "Ravioli Raptor", "Ancient/Noodle", "Stuffed fossil hunter revived by a signal shard.", "raviolord"),
    ("gelatogolem", "Gelato Golem", "Frost/Ancient", "Ancient scoop guardian that melts only for honest trainers.", "gelatitan"),
    ("pizzawraith", "Pizza Wraith", "Street/Shadow", "A haunted slice from the last open shop on Blackout Trail.", "pizzaratto"),
    ("espressoeel", "Espresso Eel", "Coast/Foam", "Fast canal eel that jolts water with bitter crema.", "tralalerotralala"),
    ("cannolizard", "Cannolizard", "Sauce/Coast", "Cream-tailed lizard that sunbathes on warm bakery tiles.", "frigocamelo"),
    ("polentapillar", "Polentapillar", "Wood/Noodle", "Cornmeal larva with the patience of a tiny kaiju.", "polentazilla"),
    ("zabaglionez", "Zabaglione Z", "Signal/Foam", "Dessert signal spirit that appears in menu static.", "streamonello"),
    ("focacciaphantom", "Focaccia Phantom", "Ancient/Street", "Old bread ghost stamped with forgotten league marks.", "crostinoboss"),
    ("tarantellatoad", "Tarantella Toad", "Rhythm/Coast", "Dancing toad that turns puddles into percussion.", "tungtungsahur"),
    ("maccarover", "Macca Rover", "Street/Signal", "Tiny delivery robot that lost its route and gained a soul.", "bruschettank"),
    ("creamurai", "Creamurai", "Grace/Shadow", "Foam-armored duelist with one perfectly quiet step.", "cappuccinoassassino"),
    ("laserlatti", "Laser Latti", "Signal/Foam", "Latte sprite that draws straight lines through fog.", "ballerinacappuccina"),
    ("biscottiborg", "Biscotti Borg", "Ancient/Signal", "A crunchy automaton from a tower older than towers.", "bruschettank"),
    ("oliveoracle", "Olive Oracle", "Ancient/Wood", "Sees tomorrow inside a jar of brine.", "crostinoboss"),
    ("marinaraptor", "Marina Raptor", "Coast/Sauce", "Fast coastal hunter with tomato-red fins.", "bombardirocrocodilo"),
    ("panettonepal", "Panettone Pal", "Foam/Grace", "Festive friend that hides rare berries in its hat.", "mozzarellion"),
    ("zestyzaza", "Zesty Zaza", "Street/Sauce", "Street snack trickster with lemon-bright eyes.", "chimpanzinibananini"),
    ("radioravioli", "Radio Ravioli", "Signal/Noodle", "Stuffed pasta receiver that hums lost badge songs.", "raviolord"),
    ("staticstag", "Static Stag", "Signal/Wood", "Forest guardian with antenna antlers.", "brrbrrpatapim"),
    ("moonmilkmare", "Moonmilk Mare", "Ancient/Foam", "Quiet cosmic horse that drinks moonlight from ruins.", "vaccasaturnosaturnita"),
    ("saltimboccaimp", "Saltimbocca Imp", "Street/Grace", "Leaps between rooftops and steals dramatic entrances.", "salsicciator"),
    ("nocturnoodle", "Nocturnoodle", "Shadow/Noodle", "Dark pasta ribbon seen only when the music stops.", "spaghettimon"),
    ("voltavongola", "Volta Vongola", "Signal/Coast", "Electric clam spirit that clicks like a metronome.", "tralalerotralala"),
    ("ruinrosetta", "Ruin Rosetta", "Ancient/Grace", "Stone flower that translates the old seal language.", "macaronocchio"),
    ("champignono", "Champignono", "Wood/Foam", "Mushroom chef that insists every cave needs garnish.", "brrbrrpatapim"),
]

for index, (key, name, kind, description, base_key) in enumerate(_EXTRA_CREATURE_SPECS):
    if key in CREATURES:
        continue
    base = CREATURES[base_key]
    CREATURES[key] = CreatureDef(
        key,
        name,
        kind,
        base.max_hp + (index % 5) - 2,
        base.attack + (index % 3) - 1,
        base.defense + ((index + 1) % 3) - 1,
        _generated_move_set(base_key),
        max(0.12, min(0.45, base.capture_rate - 0.02 + (index % 4) * 0.015)),
        description,
        None,
    )


ENCOUNTER_KEYS: List[str] = list(CREATURES.keys())


class Battler:
    def __init__(self, creature: CreatureDef, level: int = 1):
        self.creature = creature
        self.level = level
        self.max_hp = creature.max_hp + (level - 1) * 3
        self.hp = self.max_hp
        self.attack = creature.attack + level
        self.defense = creature.defense + max(0, level - 1)
        self.defending = False
        self.moves = creature.moves

    @property
    def name(self) -> str:
        return self.creature.name

    def is_down(self) -> bool:
        return self.hp <= 0

    def signature_move(self) -> MoveDef:
        return self.moves[2]

    def evolution_target(self) -> Optional[EvolutionDef]:
        return self.creature.evolution

    def can_evolve(self) -> bool:
        evo = self.evolution_target()
        return evo is not None and self.level >= evo.level_required

    def evolution_ready_text(self) -> str:
        evo = self.evolution_target()
        if evo is None:
            return "No evolution set"
        if self.can_evolve():
            return f"Ready for {evo.evolves_to}"
        return f"Evolves at lv.{evo.level_required}"

    def evolve(self) -> bool:
        evo = self.evolution_target()
        if evo is None or not self.can_evolve() or evo.evolves_to not in CREATURES:
            return False
        current_hp_ratio = self.hp / self.max_hp if self.max_hp else 1
        self.creature = CREATURES[evo.evolves_to]
        self.max_hp = self.creature.max_hp + (self.level - 1) * 3
        self.hp = max(1, int(self.max_hp * current_hp_ratio))
        self.attack = self.creature.attack + self.level
        self.defense = self.creature.defense + max(0, self.level - 1)
        self.moves = self.creature.moves
        return True

    def heal(self, amount: int) -> int:
        old = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old

    def take_damage(self, amount: int) -> int:
        if self.defending:
            amount = max(1, amount // 2)
            self.defending = False
        self.hp = max(0, self.hp - amount)
        return amount
