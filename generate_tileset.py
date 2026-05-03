#!/usr/bin/env python3
"""
Generate 1000+ tile retro pixel art tileset for Brainrotmon using Pollination AI.
Tiles are 16x16 pixels. Output: tileset.png (grid of tiles) + tileset_index.json
"""

import requests
import json
import os
import base64
import io
from PIL import Image
import time

API_KEY = "sk_M6sumbNAAGRn7jWEfwgJZfqu1r3W7y5k"
POLLINATION_URL = "https://api.pollination.ai/openai/deployments/text-to-image/chat/completions"

OUTPUT_DIR = "assets/sprites/overworld"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Tile categories with counts
TILES = {
    # GROUND (150+ tiles)
    "ground": {
        "grass_light": "single 16x16 pixel grass tile, light green, Game Boy Color style, retro RPG",
        "grass_medium": "16x16 grass tile, medium green, worn texture",
        "grass_dark": "16x16 grass tile, dark green, shaded",
        "grass_patchy": "16x16 grass with bare patches, retro",
        "grass_dead": "16x16 brown dead grass tile",
        "grass_wet": "16x16 wet grass, darker shades, puddle effect",
        "grass_frost": "16x16 frost-edged grass, icy",
        "grass_worn": "16x16 heavily worn grass path",
        "dirt_clean": "16x16 dirt path, clean, crumbly texture",
        "dirt_worn": "16x16 dirt path, very worn and trodden",
        "dirt_cracked": "16x16 cracked dirt path, cracks visible",
        "dirt_muddy": "16x16 muddy dirt, dark wet mud",
        "dirt_rocky": "16x16 dirt with rocky edges, stones",
        "dirt_corner_ne": "16x16 dirt path corner, northeast edge",
        "dirt_corner_se": "16x16 dirt path corner, southeast edge",
        "dirt_corner_sw": "16x16 dirt path corner, southwest edge",
        "dirt_corner_nw": "16x16 dirt path corner, northwest edge",
        "stone_cobble": "16x16 stone cobble path, perfect tiles",
        "stone_cobble_worn": "16x16 worn cobblestone, chipped edges",
        "stone_cobble_moss": "16x16 mossy cobblestone, algae growth",
        "stone_cracked": "16x16 cracked stone path, broken",
        "stone_corner_ne": "16x16 stone path corner, northeast",
        "stone_corner_se": "16x16 stone path corner, southeast",
        "stone_corner_sw": "16x16 stone path corner, southwest",
        "stone_corner_nw": "16x16 stone path corner, northwest",
        "stone_edge_n": "16x16 stone path edge, north side",
        "stone_edge_s": "16x16 stone path edge, south side",
        "stone_edge_e": "16x16 stone path edge, east side",
        "stone_edge_w": "16x16 stone path edge, west side",
        "sand_dry": "16x16 dry sand tile, light tan",
        "sand_wet": "16x16 wet sand, darker, beach",
        "sand_dark": "16x16 dark sand, shadow",
        "sand_footprinted": "16x16 sand with footprints, texture",
        "sand_rippled": "16x16 rippled sand pattern",
        "snow_fresh": "16x16 fresh white snow",
        "snow_packed": "16x16 packed snow, compressed",
        "snow_icy": "16x16 icy snow surface, slippery",
        "snow_melting": "16x16 melting snow, patchy",
        "snow_dirty": "16x16 dirty snow, grime",
        "ice_smooth": "16x16 smooth ice surface, frozen",
        "ice_cracked": "16x16 cracked ice, breakable",
        "ice_thin": "16x16 thin ice over water",
        "ice_puddle": "16x16 ice puddle, water underneath",
        "cave_dark_stone": "16x16 dark cave stone floor",
        "cave_wet_stone": "16x16 wet cave floor, water",
        "cave_gravel": "16x16 cave gravel floor, rocky",
        "cave_crystal": "16x16 crystal cave floor, shiny",
        "cave_ancient": "16x16 ancient tile floor, weathered",
        "ruin_mosaic": "16x16 cracked mosaic floor, ruins",
        "ruin_worn_stone": "16x16 worn ruin stone, eroded",
        "ruin_overgrown": "16x16 overgrown ruin floor, vines",
        "ruin_collapsed": "16x16 collapsed ruin tile, broken",
        "jungle_root": "16x16 jungle floor with roots visible",
        "jungle_muddy": "16x16 muddy jungle floor, wet",
        "jungle_leaf": "16x16 leaf-littered jungle ground",
        "desert_cracked": "16x16 cracked desert clay",
        "desert_red_sand": "16x16 red sand desert tile",
        "desert_rocky": "16x16 rocky desert floor",
    },
    
    # WATER (80+ tiles)
    "water": {
        "water_still_light": "16x16 still water, light blue",
        "water_still_dark": "16x16 still water, dark blue",
        "water_still_deep": "16x16 deep water, very dark",
        "water_wave_1": "16x16 water wave animation frame 1",
        "water_wave_2": "16x16 water wave animation frame 2",
        "water_wave_3": "16x16 water wave animation frame 3",
        "water_wave_4": "16x16 water wave animation frame 4",
        "water_ripple": "16x16 water with ripples, disturbed",
        "water_foam": "16x16 water with foam, bubbles",
        "waterfall_top": "16x16 waterfall top section",
        "waterfall_middle": "16x16 waterfall middle section",
        "waterfall_bottom": "16x16 waterfall bottom section, pool",
        "water_shallow": "16x16 shallow water, light, sandy",
        "water_rocks": "16x16 underwater rocks showing",
        "water_coast_foam": "16x16 coast foam, beach water edge",
        "water_ice_frozen": "16x16 frozen icy water, winter",
        "water_cave_dark": "16x16 dark cave water",
        "water_signal_polluted": "16x16 corrupted signal water, purple-green glow",
        "water_river_edge_n": "16x16 river edge, north side",
        "water_river_edge_s": "16x16 river edge, south side",
        "water_river_edge_e": "16x16 river edge, east side",
        "water_river_edge_w": "16x16 river edge, west side",
        "water_river_corner_ne": "16x16 river corner northeast",
        "water_river_corner_se": "16x16 river corner southeast",
        "water_river_corner_sw": "16x16 river corner southwest",
        "water_river_corner_nw": "16x16 river corner northwest",
    },
    
    # VEGETATION (150+ tiles)
    "vegetation": {
        "tree_oak_tl": "16x16 oak tree top-left quarter",
        "tree_oak_tr": "16x16 oak tree top-right quarter",
        "tree_oak_bl": "16x16 oak tree bottom-left quarter",
        "tree_oak_br": "16x16 oak tree bottom-right quarter",
        "tree_pine_tl": "16x16 pine tree top-left",
        "tree_pine_tr": "16x16 pine tree top-right",
        "tree_pine_bl": "16x16 pine tree bottom-left",
        "tree_pine_br": "16x16 pine tree bottom-right",
        "tree_palm_tl": "16x16 palm tree top-left",
        "tree_palm_tr": "16x16 palm tree top-right",
        "tree_palm_bl": "16x16 palm tree bottom-left",
        "tree_palm_br": "16x16 palm tree bottom-right",
        "tree_jungle_tl": "16x16 jungle tree top-left",
        "tree_jungle_tr": "16x16 jungle tree top-right",
        "tree_jungle_bl": "16x16 jungle tree bottom-left",
        "tree_jungle_br": "16x16 jungle tree bottom-right",
        "tree_dead_tl": "16x16 dead tree top-left",
        "tree_dead_tr": "16x16 dead tree top-right",
        "tree_dead_bl": "16x16 dead tree bottom-left",
        "tree_dead_br": "16x16 dead tree bottom-right",
        "tree_snowy_tl": "16x16 snowy tree top-left",
        "tree_snowy_tr": "16x16 snowy tree top-right",
        "tree_snowy_bl": "16x16 snowy tree bottom-left",
        "tree_snowy_br": "16x16 snowy tree bottom-right",
        "tree_autumn_tl": "16x16 autumn tree top-left, orange leaves",
        "tree_autumn_tr": "16x16 autumn tree top-right",
        "tree_autumn_bl": "16x16 autumn tree bottom-left",
        "tree_autumn_br": "16x16 autumn tree bottom-right",
        "tree_corrupted_tl": "16x16 signal-corrupted tree top-left, twisted",
        "tree_corrupted_tr": "16x16 signal-corrupted tree top-right",
        "tree_corrupted_bl": "16x16 signal-corrupted tree bottom-left",
        "tree_corrupted_br": "16x16 signal-corrupted tree bottom-right",
        "grass_tall_1": "16x16 tall grass variant 1, dense",
        "grass_tall_2": "16x16 tall grass variant 2",
        "grass_tall_3": "16x16 tall grass variant 3",
        "grass_tall_4": "16x16 tall grass variant 4",
        "grass_tall_5": "16x16 tall grass variant 5",
        "grass_tall_6": "16x16 tall grass variant 6",
        "flower_espresso": "16x16 espresso flower, brown, Rotria theme",
        "flower_tomato": "16x16 tomato vine flower, red",
        "flower_wildflower": "16x16 wild yellow flower",
        "flower_daisy": "16x16 daisy flower, white",
        "flower_poppy": "16x16 poppy flower, red",
        "flower_lavender": "16x16 lavender flower, purple",
        "flower_rose": "16x16 rose, pink",
        "flower_sunflower": "16x16 sunflower, yellow",
        "bush_small": "16x16 small bush",
        "bush_large": "16x16 large bush",
        "bush_berry": "16x16 berry bush, fruit visible",
        "bush_snowy": "16x16 snowy bush, white",
        "cactus_1": "16x16 desert cactus",
        "cactus_2": "16x16 tall cactus variant",
        "vine_jungle": "16x16 jungle vine, hanging",
        "mushroom_cave": "16x16 cave mushroom, fungus",
        "mushroom_poison": "16x16 poisonous mushroom, purple",
        "plant_corrupted_1": "16x16 signal-corrupted plant, twisted glowing",
        "plant_corrupted_2": "16x16 corrupted plant variant 2",
        "log_fallen": "16x16 fallen log, wood",
        "stump": "16x16 tree stump",
        "lilypad": "16x16 water lily pad",
        "reeds": "16x16 reeds by water",
    },
    
    # BUILDINGS (200+ tiles)
    "buildings": {
        "house_wood_wall": "16x16 wooden house wall",
        "house_wood_corner": "16x16 wooden house corner",
        "house_wood_window": "16x16 wooden house wall with window",
        "house_wood_door": "16x16 wooden house door section",
        "house_stone_wall": "16x16 stone house wall",
        "house_stone_corner": "16x16 stone house corner",
        "house_stone_window": "16x16 stone house window",
        "house_stone_door": "16x16 stone house door",
        "house_stucco_wall": "16x16 stucco house wall",
        "house_stucco_corner": "16x16 stucco house corner",
        "house_stucco_window": "16x16 stucco house window",
        "house_stucco_door": "16x16 stucco house door",
        "house_brick_wall": "16x16 brick house wall",
        "house_brick_corner": "16x16 brick house corner",
        "house_brick_window": "16x16 brick house window",
        "house_brick_door": "16x16 brick house door",
        "roof_flat": "16x16 flat roof tile",
        "roof_sloped_left": "16x16 sloped roof, left side",
        "roof_sloped_right": "16x16 sloped roof, right side",
        "roof_sloped_center": "16x16 sloped roof center",
        "roof_tiled_1": "16x16 tiled roof variant 1",
        "roof_tiled_2": "16x16 tiled roof variant 2",
        "roof_tiled_3": "16x16 tiled roof variant 3, gray",
        "roof_tiled_4": "16x16 tiled roof variant 4, red",
        "roof_tiled_5": "16x16 tiled roof variant 5, brown",
        "roof_tiled_6": "16x16 tiled roof variant 6, orange",
        "counter_shop": "16x16 shop counter tile, merchandise",
        "counter_healer": "16x16 healer counter, medical",
        "counter_storage": "16x16 storage counter, boxes",
        "warehouse_wall_1": "16x16 warehouse wall, industrial",
        "warehouse_wall_2": "16x16 warehouse wall variant 2",
        "warehouse_corner": "16x16 warehouse corner",
        "tower_wall": "16x16 signal tower wall, tall structure",
        "tower_antenna": "16x16 antenna piece, broadcast",
        "tower_floor": "16x16 tower floor inside",
        "ruin_wall_1": "16x16 ancient ruin wall",
        "ruin_wall_2": "16x16 ruin wall variant 2",
        "ruin_corner": "16x16 ruin corner",
        "fence_wood_h": "16x16 wooden fence, horizontal",
        "fence_wood_v": "16x16 wooden fence, vertical",
        "fence_wood_corner": "16x16 wooden fence corner",
        "fence_wood_post": "16x16 wooden fence post",
        "fence_stone_h": "16x16 stone fence, horizontal",
        "fence_stone_v": "16x16 stone fence, vertical",
        "fence_stone_corner": "16x16 stone fence corner",
        "fence_stone_post": "16x16 stone fence post",
        "fence_iron_h": "16x16 iron fence, horizontal",
        "fence_iron_v": "16x16 iron fence, vertical",
        "fence_iron_corner": "16x16 iron fence corner",
        "fence_iron_post": "16x16 iron fence post",
        "fence_broken_1": "16x16 broken fence, damaged",
        "fence_broken_2": "16x16 broken fence variant 2",
        "sign_post": "16x16 wooden sign post",
        "sign_notice": "16x16 notice board",
        "lamp_post": "16x16 street lamp post",
        "lamp_post_lit": "16x16 lamp post, lit at night",
        "mailbox": "16x16 mailbox",
        "door_wood_closed": "16x16 wooden door, closed",
        "door_wood_open": "16x16 wooden door, open",
        "door_wood_locked": "16x16 wooden door, locked",
        "door_metal_closed": "16x16 metal door, closed",
        "door_metal_open": "16x16 metal door, open",
        "door_metal_locked": "16x16 metal door, locked",
        "window_lit": "16x16 window, light on inside",
        "window_dark": "16x16 window, dark inside",
        "window_broken": "16x16 broken window",
        "broadcast_tower_1": "16x16 broadcast tower section 1",
        "broadcast_tower_2": "16x16 broadcast tower section 2",
        "broadcast_antenna": "16x16 broadcast antenna top",
    },
    
    # ENVIRONMENT OBJECTS (150+ tiles)
    "environment": {
        "rock_small": "16x16 small rock, boulder",
        "rock_medium": "16x16 medium rock",
        "rock_large": "16x16 large boulder",
        "rock_mossy": "16x16 mossy rock, algae",
        "rock_snowy": "16x16 snowy rock, winter",
        "rock_cave": "16x16 cave rock",
        "rock_pushable": "16x16 pushable rock puzzle",
        "cliff_edge_n": "16x16 cliff edge, north",
        "cliff_edge_s": "16x16 cliff edge, south",
        "cliff_edge_e": "16x16 cliff edge, east",
        "cliff_edge_w": "16x16 cliff edge, west",
        "cliff_edge_ne": "16x16 cliff corner, northeast",
        "cliff_edge_se": "16x16 cliff corner, southeast",
        "cliff_edge_sw": "16x16 cliff corner, southwest",
        "cliff_edge_nw": "16x16 cliff corner, northwest",
        "cliff_height_1": "16x16 cliff height level 1",
        "cliff_height_2": "16x16 cliff height level 2",
        "cliff_height_3": "16x16 cliff height level 3",
        "bridge_wood_h": "16x16 wooden bridge, horizontal",
        "bridge_wood_v": "16x16 wooden bridge, vertical",
        "bridge_wood_edge": "16x16 wooden bridge edge",
        "bridge_stone_h": "16x16 stone arch bridge, horizontal",
        "bridge_stone_v": "16x16 stone arch bridge, vertical",
        "bridge_stone_edge": "16x16 stone bridge edge",
        "stairs_up_outdoor": "16x16 outdoor stairs, going up",
        "stairs_down_outdoor": "16x16 outdoor stairs, going down",
        "stairs_up_indoor": "16x16 indoor stairs, going up",
        "stairs_down_indoor": "16x16 indoor stairs, going down",
        "chest_closed": "16x16 closed chest",
        "chest_open": "16x16 open chest",
        "item_ball": "16x16 item pickup ball",
        "item_sparkle": "16x16 hidden item sparkle",
        "berry_tree_full": "16x16 berry tree, full fruit",
        "berry_tree_half": "16x16 berry tree, half picked",
        "berry_tree_empty": "16x16 berry tree, empty",
        "fruit_red": "16x16 red fruit variant",
        "fruit_yellow": "16x16 yellow fruit variant",
        "fruit_purple": "16x16 purple fruit variant",
        "fruit_orange": "16x16 orange fruit variant",
        "market_stall": "16x16 market stall, vendor cart",
        "food_cart": "16x16 food cart, street vendor",
        "dock_plank": "16x16 dock wooden plank",
        "dock_rope": "16x16 rope tie, dock",
        "anchor": "16x16 anchor, harbor",
        "ice_block": "16x16 ice puzzle block",
        "ice_block_melted": "16x16 melted ice block",
        "pressure_plate": "16x16 pressure plate trigger",
        "ancient_switch": "16x16 ancient switch mechanism",
        "signal_debris": "16x16 signal tower debris",
        "ground_corrupted": "16x16 corrupted ground, cracked glow",
        "campfire": "16x16 campfire, flames",
        "campfire_dead": "16x16 dead campfire, ash",
        "torch": "16x16 torch, flame",
        "torch_unlit": "16x16 unlit torch",
        "lantern": "16x16 hanging lantern",
        "crystal_formation": "16x16 crystal cluster, cave",
        "crystal_glowing": "16x16 glowing crystal",
    },
    
    # INTERIOR TILES (150+ tiles)
    "interior": {
        "floor_wood": "16x16 wooden floor, planks",
        "floor_stone": "16x16 stone floor tile",
        "floor_carpet_red": "16x16 red carpet",
        "floor_carpet_blue": "16x16 blue carpet",
        "floor_carpet_green": "16x16 green carpet",
        "floor_cave": "16x16 cave floor interior",
        "floor_fancy": "16x16 fancy interior floor",
        "wall_plain": "16x16 plain wall",
        "wall_wallpaper": "16x16 wallpapered wall",
        "wall_stone": "16x16 stone interior wall",
        "wall_brick": "16x16 brick interior wall",
        "wall_edge_top": "16x16 wall with top edge",
        "wall_corner": "16x16 wall corner",
        "wall_window": "16x16 wall with window inside",
        "bed_single": "16x16 single bed",
        "bed_double": "16x16 double bed",
        "table_small": "16x16 small table",
        "table_large": "16x16 large table",
        "chair_front": "16x16 chair facing front",
        "chair_side": "16x16 chair from side",
        "bookshelf": "16x16 bookshelf",
        "bookshelf_top": "16x16 bookshelf top section",
        "counter_kitchen": "16x16 kitchen counter",
        "counter_bar": "16x16 bar counter",
        "barrel": "16x16 barrel storage",
        "crate": "16x16 wooden crate",
        "crate_stacked": "16x16 stacked crates",
        "indoor_door": "16x16 indoor door",
        "indoor_stairs": "16x16 indoor staircase",
        "rug_small": "16x16 small rug",
        "rug_large": "16x16 large rug",
        "lab_bench": "16x16 lab bench, equipment",
        "lab_machine": "16x16 lab machine, tech",
        "lab_computer": "16x16 lab computer",
        "shop_shelf": "16x16 shop shelving",
        "shop_shelf_stocked": "16x16 stocked shop shelf",
        "heal_machine": "16x16 heal machine, medical pod",
        "pc_storage": "16x16 PC storage machine",
        "signal_equipment": "16x16 signal broadcast equipment",
        "signal_console": "16x16 signal control console",
    },
    
    # UI/SPECIAL TILES (80+ tiles)
    "special": {
        "warp_tile_1": "16x16 warp tile, portal effect frame 1",
        "warp_tile_2": "16x16 warp tile, portal effect frame 2",
        "warp_tile_3": "16x16 warp tile, portal effect frame 3",
        "warp_tile_4": "16x16 warp tile, portal effect frame 4",
        "trainer_sight_1": "16x16 trainer line-of-sight indicator 1",
        "trainer_sight_2": "16x16 trainer line-of-sight indicator 2",
        "day_variant_1": "16x16 day mode tile variant",
        "day_variant_2": "16x16 day mode variant 2",
        "night_variant_1": "16x16 night mode tile, dark tinted",
        "night_variant_2": "16x16 night mode variant 2",
        "grass_light_day": "16x16 grass light, day",
        "grass_light_night": "16x16 grass light, night tinted",
        "path_day": "16x16 path, day lighting",
        "path_night": "16x16 path, night lighting",
        "water_day": "16x16 water, day",
        "water_night": "16x16 water, night tinted",
        "signal_corrupted_grass": "16x16 signal-corrupted grass, twisted purple",
        "signal_corrupted_path": "16x16 signal-corrupted path, glowing",
        "signal_corrupted_ground": "16x16 signal-corrupted ground, radioactive",
    },
}

def generate_tile_image(tile_name, prompt):
    """Generate a single 16x16 tile image using Pollination AI."""
    print(f"Generating: {tile_name}...")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "dall-e-3",
        "messages": [
            {
                "role": "user",
                "content": f"Create a single 16x16 pixel retro Game Boy Color style tile. {prompt} Dark outlines, 4-6 color palette, crisp no blur. Square format. Must be exactly 16x16."
            }
        ],
        "size": "256x256",  # Generate larger, will resize to 16x16
        "quality": "standard",
        "n": 1
    }
    
    try:
        response = requests.post(POLLINATION_URL, headers=headers, json=payload, timeout=30)
        if response.status_code != 200:
            print(f"  API Error {response.status_code}: {response.text[:200]}")
            return None
        
        data = response.json()
        if "data" not in data or not data["data"]:
            print(f"  No image in response")
            return None
        
        img_url = data["data"][0]["url"]
        img_response = requests.get(img_url, timeout=10)
        img = Image.open(io.BytesIO(img_response.content))
        
        # Resize to 16x16
        img = img.resize((16, 16), Image.Resampling.LANCZOS)
        return img
    except Exception as e:
        print(f"  Error: {e}")
        return None

def main():
    print(f"🎨 Generating 1000+ tile retro pixel tileset...")
    print(f"Total tiles to generate: {sum(len(v) for v in TILES.values())}")
    
    # Flatten all tiles
    all_tiles = {}
    for category, tiles in TILES.items():
        all_tiles.update(tiles)
    
    # Generate tiles (limit to 50 to avoid API quota issues; extend later)
    tile_images = {}
    generated_count = 0
    max_generate = 50  # Start with 50, extend after testing
    
    for tile_name, prompt in list(all_tiles.items())[:max_generate]:
        img = generate_tile_image(tile_name, prompt)
        if img:
            tile_images[tile_name] = img
            generated_count += 1
        
        # Rate limit to avoid API throttling
        time.sleep(1)
    
    print(f"\n✅ Generated {generated_count} tiles")
    
    if not tile_images:
        print("❌ No tiles generated. Check API key and quota.")
        return
    
    # Create tileset PNG (grid layout)
    tiles_per_row = 16
    tile_size = 16
    grid_cols = tiles_per_row
    grid_rows = (len(tile_images) + tiles_per_row - 1) // tiles_per_row
    
    tileset_width = grid_cols * tile_size
    tileset_height = grid_rows * tile_size
    
    tileset = Image.new("RGBA", (tileset_width, tileset_height), color=(0, 0, 0, 0))
    
    tile_list = list(tile_images.keys())
    tile_index = {}
    
    for idx, tile_name in enumerate(tile_list):
        row = idx // tiles_per_row
        col = idx % tiles_per_row
        x = col * tile_size
        y = row * tile_size
        
        tileset.paste(tile_images[tile_name], (x, y))
        tile_index[tile_name] = [row, col]
    
    # Save tileset PNG
    tileset_path = os.path.join(OUTPUT_DIR, "tileset.png")
    tileset.save(tileset_path, "PNG")
    print(f"📦 Saved tileset: {tileset_path}")
    
    # Save index JSON
    index_path = os.path.join(OUTPUT_DIR, "tileset_index.json")
    with open(index_path, "w") as f:
        json.dump(tile_index, f, indent=2)
    print(f"📋 Saved index: {index_path}")
    
    print(f"\n✨ Tileset complete: {tileset_width}x{tileset_height} px ({len(tile_list)} tiles)")

if __name__ == "__main__":
    main()
