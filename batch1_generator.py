#!/usr/bin/env python3
"""
BATCH 1 TILESET GENERATOR — Grass and Terrain (192 tiles)
Uses Pollination AI to generate 16x16 pixel tiles based on detailed descriptions.
Outputs: tileset_batch1.png (256x192 px grid) + tileset_batch1_index.json
"""

import requests
import json
import os
import io
from PIL import Image
import time

API_KEY = "sk_M6sumbNAAGRn7jWEfwgJZfqu1r3W7y5k"
POLLINATION_BASE_URL = "https://api.pollination.ai/openai/deployments/text-to-image/chat/completions"

OUTPUT_DIR = "assets/sprites/overworld"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TILE_SIZE = 16

# Batch 1: Grass and Terrain Tiles
BATCH_1_TILES = {
    "ROW_1_grass": [
        ("grass_fresh", "fresh bright green grass with small blade details and soft highlights"),
        ("grass_deep", "deeper richer green grass with denser blades and subtle base shadow"),
        ("grass_patchy", "patchy grass with warm dirt showing through gaps"),
        ("grass_dead", "dead yellowed dry grass with brown brittle tips"),
        ("grass_worn", "worn grass rubbed away to reveal dirt underneath"),
        ("grass_wet", "wet dark saturated green grass with slight moisture sheen"),
        ("grass_frost", "frost-tipped grass with tiny white crystals on blade tips"),
        ("grass_tall", "tall wild grass with visibly taller more chaotic blades"),
        ("grass_flower_red", "grass with small red flower accent"),
        ("grass_flower_yellow", "grass with small yellow flower accent"),
        ("grass_flower_white", "grass with tiny white daisy cluster"),
        ("grass_autumn_leaf", "grass with fallen autumn leaf on it"),
        ("grass_path_blend", "grass at edge of dirt path blending into it"),
        ("grass_corner", "grass corner piece where two edges meet"),
        ("grass_tuft", "thick clumped grass tuft"),
        ("grass_sparse", "sparse patchy grass barely covering dirt"),
    ],
    "ROW_2_dirt": [
        ("dirt_path", "packed warm brown dirt path with subtle texture"),
        ("dirt_muddy", "muddy dark wet dirt with slight shine and footprint impressions"),
        ("dirt_cracked", "cracked dry earth with deep fissure lines"),
        ("dirt_rocky", "rocky dirt with small pebbles scattered"),
        ("dirt_soft_soil", "soft soil recently turned like a garden"),
        ("dirt_clay", "hard baked clay pale tan color"),
        ("dirt_eroded", "eroded dirt with small ruts"),
        ("dirt_blend_n", "dirt blending into grass at north edge"),
        ("dirt_blend_s", "dirt blending into grass at south edge"),
        ("dirt_blend_w", "dirt blending into grass at west edge"),
        ("dirt_blend_e", "dirt blending into grass at east edge"),
        ("dirt_corner_nw", "dirt corner blend northwest"),
        ("dirt_corner_ne", "dirt corner blend northeast"),
        ("dirt_corner_sw", "dirt corner blend southwest"),
        ("dirt_corner_se", "dirt corner blend southeast"),
        ("dirt_footprint", "bare earth with a single boot print"),
    ],
    "ROW_3_stone": [
        ("stone_cobble", "grey cobblestone with rounded stones and dark grout lines"),
        ("stone_cobble_worn", "worn cobblestone with faded uneven stones"),
        ("stone_cobble_mossy", "mossy cobblestone with green moss in grout gaps"),
        ("stone_smooth", "smooth cut stone slabs regular rectangular pattern"),
        ("stone_cracked", "cracked cut stone with fissures"),
        ("stone_overgrown", "ancient overgrown stone path with weeds in cracks"),
        ("stone_flagstone", "flagstone irregular shaped natural stones"),
        ("stone_limestone", "pale limestone path bright and clean"),
        ("stone_basalt", "dark basalt stone almost black"),
        ("stone_sandstone", "sandstone path warm yellow-tan"),
        ("stone_edge_n", "cobblestone path edge blending to grass north"),
        ("stone_edge_s", "cobblestone path edge south"),
        ("stone_edge_w", "cobblestone path edge west"),
        ("stone_edge_e", "cobblestone path edge east"),
        ("stone_tjunction", "cobblestone T-junction"),
        ("stone_crossroads", "cobblestone crossroads"),
    ],
    "ROW_4_sand": [
        ("sand_dry", "warm golden dry sand with ripple lines"),
        ("sand_wet", "dark wet sand near water with subtle shine"),
        ("sand_pale", "pale white sand very fine"),
        ("sand_coarse", "coarse brown sand with tiny pebble texture"),
        ("sand_shell", "sand with small shell visible"),
        ("sand_footprint", "sand with footprint impressions"),
        ("sand_rippled", "wind-rippled sand with wave pattern"),
        ("sand_water_edge", "sand blending to water edge"),
        ("sand_foam", "wet sand with foam residue"),
        ("sand_pebbled", "dry sand with scattered pebble cluster"),
        ("sand_desert_red", "desert red-orange sand warm and hot"),
        ("sand_desert_pale", "desert pale cracked clay"),
        ("sand_desert_rocky", "desert sandy rock debris"),
        ("sand_cactus_shadow", "sandy ground with cactus shadow"),
        ("sand_lowtide", "beach sand at low tide"),
        ("sand_sparkle", "sand with buried item sparkle hint"),
    ],
    "ROW_5_snow": [
        ("snow_fresh", "fresh clean white snow with faint blue shadow in dips"),
        ("snow_packed", "packed compressed grey-white snow with icy sheen"),
        ("snow_tracks", "snow with boot tracks crossing it"),
        ("snow_animal_tracks", "snow with animal tracks"),
        ("snow_melting", "snow melting at edges showing grass beneath"),
        ("snow_dirty", "dirty grey snow near paths"),
        ("snow_drift", "deep snowdrift piled high"),
        ("ice_smooth", "smooth pale blue ice mirror-like with reflection lines"),
        ("ice_cracked", "cracked ice with dark fissure lines"),
        ("ice_thin", "thin ice with water visible beneath"),
        ("ice_snow_patch", "ice with snow patch on top"),
        ("ice_spreading_cracks", "ice with cracks spreading from center"),
        ("ice_puddle_melting", "frozen puddle slightly melted at edges"),
        ("ice_frost_pattern", "frost pattern like lace on ice"),
        ("ice_black", "black ice very dark reflective"),
        ("ice_slushy", "slushy melting ice mix of white and pale blue"),
    ],
    "ROW_6_jungle": [
        ("jungle_deep", "deep jungle floor rich dark green with leaf litter"),
        ("jungle_roots", "jungle floor with exposed roots weaving across"),
        ("jungle_muddy", "muddy jungle floor dark brown-green"),
        ("jungle_tropical_leaf", "jungle floor with fallen tropical leaf"),
        ("jungle_mushroom", "jungle floor with small mushroom cluster"),
        ("forest_autumn", "leaf-littered forest floor autumn leaves on dark earth"),
        ("forest_mossy", "mossy forest floor thick soft green moss"),
        ("forest_pine_needles", "forest floor with pine needles layer"),
        ("forest_damp", "dark damp forest floor near stream"),
        ("jungle_tiny_flower", "jungle floor with tiny colorful flower"),
        ("jungle_vine_covered", "vine-covered forest floor"),
        ("jungle_shadow", "jungle floor at edge of dense canopy shadow"),
        ("forest_clearing", "forest clearing floor lighter grass"),
        ("cave_transition", "cave mouth floor transition dark to light"),
        ("earth_ceiling", "underground earth ceiling dirt"),
        ("earth_root_cracked", "root-cracked earth where tree roots break ground"),
    ],
    "ROW_7_cave": [
        ("cave_stone_dark", "dark rough cave stone floor very dark grey-brown"),
        ("cave_wet", "wet cave floor with moisture sheen"),
        ("cave_gravel", "gravel cave floor small loose stones"),
        ("cave_crystal_glow", "crystal-lit cave floor faint blue glow from below"),
        ("cave_ancient_tile", "ancient tile cave floor like old civilisation"),
        ("cave_cracked", "cave floor with crack"),
        ("cave_stalactite_pool", "cave floor with small stalactite drip pool"),
        ("cave_scattered_pebbles", "cave floor with scattered pebbles"),
        ("cave_wall_jagged", "cave wall solid jagged dark rock"),
        ("cave_wall_seeping", "cave wall with water seeping through"),
        ("cave_wall_crystal", "cave wall with embedded glowing crystal"),
        ("cave_wall_crumbling", "cave wall crumbling"),
        ("cave_stalactite_tip", "cave ceiling stalactite tip hanging"),
        ("cave_column", "cave rock column pillar"),
        ("cave_soil_ceiling", "underground soil ceiling dark earth"),
        ("cave_void", "dark void black empty underground space"),
    ],
    "ROW_8_ruin": [
        ("ruin_mosaic", "cracked ancient stone mosaic floor faded colors"),
        ("ruin_overgrown", "worn overgrown ruin stone floor"),
        ("ruin_collapsed", "collapsed ruin floor with debris"),
        ("ruin_carved_symbol", "ancient ruin tile with carved symbol faintly visible"),
        ("ruin_grass_cracks", "ruin floor with grass growing through cracks"),
        ("ruin_flooded", "ruin stone floor partially flooded"),
        ("ruin_glowing_inscription", "ruin floor tile with glowing ancient inscription"),
        ("ruin_dark_weathered", "dark ruin floor very old and weathered"),
        ("ruin_sand_covered", "sand-covered ruin floor like excavation site"),
        ("ruin_dirt_edge", "ruin floor edge where it meets dirt"),
        ("ruin_marble", "ancient marble floor cracked but elegant"),
        ("ruin_obsidian", "obsidian black ancient floor"),
        ("ruin_signal_patterns", "ancient floor with signal-era carved patterns"),
        ("ruin_corner", "ruin floor corner piece"),
        ("ruin_fallen_block", "ruin floor with fallen stone block on it"),
        ("ruin_chamber", "underground ancient chamber floor"),
    ],
    "ROW_9_water": [
        ("water_still", "still calm dark navy blue water with soft light streaks"),
        ("water_wave_1", "water wave animation frame 1 pattern slightly shifted"),
        ("water_wave_2", "water wave frame 2 shifted more"),
        ("water_wave_3", "water wave frame 3 furthest shift completing loop"),
        ("water_wave_4", "water wave frame 4 returning"),
        ("water_deep", "deep dark navy water almost black with minimal highlight"),
        ("water_shallow", "shallow light blue water with sandy bottom texture beneath"),
        ("water_swamp", "murky swamp water dark green-brown"),
        ("water_crystal", "crystal clear water light blue you can see through"),
        ("water_rapids", "rapids fast-moving white-capped water"),
        ("water_whirlpool", "whirlpool water swirling pattern"),
        ("water_lily_pad", "water with lily pad floating"),
        ("water_reflection", "water reflection showing trees"),
        ("waterfall_top", "waterfall top where water begins to fall"),
        ("waterfall_middle", "waterfall middle vertical white streaks"),
        ("waterfall_bottom", "waterfall bottom mist and foam at base"),
    ],
    "ROW_10_shore": [
        ("shore_grass_n", "water meeting grass shore north edge"),
        ("shore_grass_s", "water meeting grass shore south edge"),
        ("shore_grass_w", "water meeting grass shore west edge"),
        ("shore_grass_e", "water meeting grass shore east edge"),
        ("shore_corner_nw", "water shore corner northwest"),
        ("shore_corner_ne", "water shore corner northeast"),
        ("shore_corner_sw", "water shore corner southwest"),
        ("shore_corner_se", "water shore corner southeast"),
        ("shore_foam_surf", "white foam surf where wave meets beach"),
        ("shore_rocky", "rocky shore water between stones"),
        ("shore_dock", "dock edge water meets wooden planks"),
        ("shore_mossy", "mossy stone shore"),
        ("shore_sandy", "sandy beach meeting water"),
        ("shore_ice", "ice edge meeting water"),
        ("shore_cave_water", "cave water dark underground pool edge"),
        ("shore_corrupted", "corrupted water dark purple-green murky"),
    ],
    "ROW_11_cliff": [
        ("cliff_face_n", "cliff face north side rocky drop"),
        ("cliff_face_s", "cliff face south side"),
        ("cliff_face_w", "cliff face west side"),
        ("cliff_face_e", "cliff face east side"),
        ("cliff_corner_nw", "cliff corner northwest"),
        ("cliff_corner_ne", "cliff corner northeast"),
        ("cliff_corner_sw", "cliff corner southwest"),
        ("cliff_corner_se", "cliff corner southeast"),
        ("cliff_edge_top_n", "cliff top edge north with grass above"),
        ("cliff_edge_top_s", "cliff top edge south"),
        ("cliff_waterfall", "cliff with waterfall coming down face"),
        ("cliff_vines", "cliff with hanging vines"),
        ("cliff_hillside", "rocky hillside angled stone"),
        ("cliff_plateau", "raised rock plateau edge"),
        ("cliff_cave_mouth", "cliff with cave mouth opening"),
        ("cliff_shadow", "cliff shadow underneath overhang"),
    ],
    "ROW_12_special": [
        ("special_corrupted_grass", "corrupted grass dark with purple-green organic glow"),
        ("special_corrupted_earth", "corrupted cracked earth purple light from fissures"),
        ("special_corrupted_puddle", "signal-corrupted puddle glowing purple-green"),
        ("special_dead_grass", "dead brown grass in corrupted zone"),
        ("special_corrupted_ruin", "corrupted ruin floor with organic glow"),
        ("special_warp_tile", "warp tile stone floor with golden glowing carved circle"),
        ("special_hidden_item", "hidden item tile normal-looking grass with barely-visible sparkle"),
        ("special_pressure_plate", "pressure plate stone tile with carved symbol"),
        ("special_pushable_rock", "pushable rock clearly different from normal rock"),
        ("special_trainer_sight", "trainer sight cone tile subtle directional indicator"),
        ("special_day_night_grass", "day-night transition grass slightly darker tinted version"),
        ("special_day_night_path", "day-night path darker tinted"),
        ("special_day_night_water", "day-night water darker tinted"),
        ("special_signal_static", "signal static ground cracked with green-purple energy"),
        ("special_ancient_seal", "ancient seal floor tile carved with geometric pattern"),
        ("special_final_dungeon", "final dungeon floor dark and ominous ancient"),
    ],
}

def generate_tile(tile_name, description):
    """Generate a single 16x16 tile using Pollination AI."""
    print(f"  {tile_name}...", end=" ", flush=True)
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Create a 16x16 pixel art game tile. {description}
Style: Pokemon HeartGold era RPG, warm painterly, soft dark outlines, earthy warm colors, crisp pixels, no blur.
Background: Pure black #000000. Output: PNG 16x16."""
    
    payload = {
        "model": "dall-e-3",
        "messages": [{"role": "user", "content": prompt}],
        "size": "256x256",
        "quality": "standard",
        "n": 1
    }
    
    try:
        response = requests.post(POLLINATION_BASE_URL, headers=headers, json=payload, timeout=30)
        if response.status_code != 200:
            print("❌")
            return None
        data = response.json()
        if "data" not in data or not data["data"]:
            print("❌")
            return None
        img_url = data["data"][0]["url"]
        img_response = requests.get(img_url, timeout=10)
        img = Image.open(io.BytesIO(img_response.content)).convert("RGBA")
        img = img.resize((16, 16), Image.Resampling.LANCZOS)
        print("✅")
        return img
    except Exception as e:
        print("❌")
        return None

def main():
    print("🎨 BATCH 1 GENERATOR — Grass & Terrain (192 tiles)\n")
    
    all_tiles = {}
    tile_index = {}
    generated = 0
    
    row_num = 0
    for row_key, row_tiles in BATCH_1_TILES.items():
        print(f"{row_key} ({len(row_tiles)} tiles):")
        for col_num, (tile_name, description) in enumerate(row_tiles):
            img = generate_tile(tile_name, description)
            if img:
                all_tiles[tile_name] = img
                tile_index[tile_name] = [row_num, col_num]
                generated += 1
            time.sleep(0.3)
        row_num += 1
        print()
    
    print(f"\n✅ Generated {generated}/192 tiles\n")
    
    if generated < 50:
        print("⚠️  Insufficient tiles. Check API.")
        return
    
    print("📦 Assembling tileset...")
    tileset = Image.new("RGBA", (256, 192), (0, 0, 0, 255))
    
    for tile_name, (row, col) in tile_index.items():
        if tile_name in all_tiles:
            x, y = col * 16, row * 16
            tileset.paste(all_tiles[tile_name], (x, y), all_tiles[tile_name])
    
    tileset_path = os.path.join(OUTPUT_DIR, "tileset_batch1.png")
    tileset.save(tileset_path, "PNG")
    print(f"💾 Saved: {tileset_path}")
    
    index_path = os.path.join(OUTPUT_DIR, "tileset_batch1_index.json")
    with open(index_path, "w") as f:
        json.dump(tile_index, f, indent=2)
    print(f"📋 Saved: {index_path}")
    
    print(f"\n✨ Complete: {generated} tiles, 256x192 px")

if __name__ == "__main__":
    main()
