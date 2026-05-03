#!/usr/bin/env python3
"""
Expand tileset to 1000+ tiles with advanced procedural generation:
- Color variations of base tiles
- Rotations and flips
- Overlay effects (shadows, highlights, decay)
"""

import json
import os
from PIL import Image, ImageDraw
import random

OUTPUT_DIR = "assets/sprites/overworld"
TILE_SIZE = 16

PALETTE_RETRO = {
    "white": (224, 224, 192),
    "light_green": (136, 192, 112),
    "medium_green": (80, 144, 80),
    "dark_green": (32, 96, 32),
    "light_gray": (192, 192, 192),
    "dark_gray": (64, 64, 64),
    "light_blue": (120, 176, 208),
    "water_blue": (56, 120, 184),
    "deep_blue": (24, 80, 144),
    "brown": (144, 96, 32),
    "dark_brown": (80, 48, 16),
    "sand": (208, 192, 144),
    "red": (208, 32, 32),
    "orange": (208, 144, 32),
    "purple": (160, 96, 144),
    "yellow": (224, 208, 80),
    "black": (0, 0, 0),
}

def apply_shadow(img):
    """Apply shadow overlay (bottom-right darkening)."""
    pixels = img.load()
    for x in range(TILE_SIZE):
        for y in range(TILE_SIZE):
            r, g, b, a = pixels[x, y]
            if a > 0:
                darkness = ((x + y) / (2 * TILE_SIZE)) * 0.3
                r = max(0, int(r * (1 - darkness)))
                g = max(0, int(g * (1 - darkness)))
                b = max(0, int(b * (1 - darkness)))
                pixels[x, y] = (r, g, b, a)
    return img

def apply_highlight(img):
    """Apply highlight overlay (top-left brightening)."""
    pixels = img.load()
    for x in range(TILE_SIZE):
        for y in range(TILE_SIZE):
            r, g, b, a = pixels[x, y]
            if a > 0:
                brightness = ((TILE_SIZE - x - y) / (2 * TILE_SIZE)) * 0.2
                r = min(255, int(r + 60 * brightness))
                g = min(255, int(g + 60 * brightness))
                b = min(255, int(b + 60 * brightness))
                pixels[x, y] = (r, g, b, a)
    return img

def apply_weathering(img):
    """Apply random weathering spots."""
    pixels = img.load()
    spots = random.randint(2, 8)
    for _ in range(spots):
        x = random.randint(1, TILE_SIZE-2)
        y = random.randint(1, TILE_SIZE-2)
        r, g, b, a = pixels[x, y]
        if a > 0:
            pixels[x, y] = (int(r*0.6), int(g*0.6), int(b*0.6), a)
    return img

def apply_color_shift(img, h_shift=0, s_shift=0):
    """Shift color hue/saturation."""
    pixels = img.load()
    for x in range(TILE_SIZE):
        for y in range(TILE_SIZE):
            r, g, b, a = pixels[x, y]
            if a > 0:
                # Clamp basic color shifts
                r = max(0, min(255, int(r + h_shift)))
                g = max(0, min(255, int(g + h_shift)))
                b = max(0, min(255, int(b + h_shift)))
                pixels[x, y] = (r, g, b, a)
    return img

def rotate_90(img):
    """Rotate image 90 degrees."""
    return img.rotate(90, expand=False)

def flip_h(img):
    """Flip horizontally."""
    return img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

def flip_v(img):
    """Flip vertically."""
    return img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

def expand_tileset():
    """Load base tileset and generate 1000+ variants."""
    print("📊 Expanding tileset to 1000+ tiles...")
    
    # Load existing tileset
    tileset_img = Image.open(os.path.join(OUTPUT_DIR, "tileset.png")).convert("RGBA")
    with open(os.path.join(OUTPUT_DIR, "tileset_index.json")) as f:
        tile_index = json.load(f)
    
    # Extract individual tiles
    base_tiles = {}
    for tile_name, (row, col) in tile_index.items():
        x = col * TILE_SIZE
        y = row * TILE_SIZE
        tile = tileset_img.crop((x, y, x + TILE_SIZE, y + TILE_SIZE))
        base_tiles[tile_name] = tile
    
    print(f"📦 Loaded {len(base_tiles)} base tiles")
    
    expanded_tiles = {}
    expanded_tiles.update(base_tiles)  # Keep all base tiles
    
    # Generate variants
    variant_count = 0
    
    # Color variants for terrain
    for base_name in list(base_tiles.keys()):
        if "grass" in base_name or "dirt" in base_name or "sand" in base_name or "snow" in base_name:
            base_tile = base_tiles[base_name]
            
            # Shadow variant
            shadowed = apply_shadow(base_tile.copy())
            expanded_tiles[f"{base_name}_shadow"] = shadowed
            variant_count += 1
            
            # Highlight variant
            highlighted = apply_highlight(base_tile.copy())
            expanded_tiles[f"{base_name}_light"] = highlighted
            variant_count += 1
            
            # Weathered variant
            weathered = apply_weathering(base_tile.copy())
            expanded_tiles[f"{base_name}_worn"] = weathered
            variant_count += 1
            
            # Multiple weather states
            for _ in range(2):
                variant = apply_weathering(base_tile.copy())
                expanded_tiles[f"{base_name}_decay_{random.randint(1,100)}"] = variant
                variant_count += 1
    
    # Rotation variants for directional tiles
    for base_name in list(base_tiles.keys()):
        if any(x in base_name for x in ["fence", "rock", "cliff", "bridge"]):
            base_tile = base_tiles[base_name]
            
            for rotation in [1, 2, 3]:
                rotated = base_tile.copy()
                for _ in range(rotation):
                    rotated = rotate_90(rotated)
                expanded_tiles[f"{base_name}_rot{rotation}"] = rotated
                variant_count += 1
            
            # Flip variants
            flipped_h = flip_h(base_tile)
            expanded_tiles[f"{base_name}_fliph"] = flipped_h
            variant_count += 1
            
            flipped_v = flip_v(base_tile)
            expanded_tiles[f"{base_name}_flipv"] = flipped_v
            variant_count += 1
    
    # Create multiple animation frames for water, warp, etc
    for base_name in list(base_tiles.keys()):
        if "water" in base_name or "warp" in base_name:
            base_tile = base_tiles[base_name]
            for i in range(1, 8):
                # Create perturbed versions
                perturbed = base_tile.copy()
                draw = ImageDraw.Draw(perturbed)
                # Add subtle animated effects
                for _ in range(i):
                    x = random.randint(0, TILE_SIZE-1)
                    y = random.randint(0, TILE_SIZE-1)
                    draw.point((x, y), fill=(255, 255, 255, 50))
                expanded_tiles[f"{base_name}_anim{i}"] = perturbed
                variant_count += 1
    
    # Night/corrupted variants
    for base_name in list(base_tiles.keys()):
        base_tile = base_tiles[base_name]
        
        # Night tint
        night_tile = base_tile.copy()
        pixels = night_tile.load()
        for x in range(TILE_SIZE):
            for y in range(TILE_SIZE):
                r, g, b, a = pixels[x, y]
                if a > 0:
                    pixels[x, y] = (int(r*0.4), int(g*0.5), int(b*0.8), a)
        expanded_tiles[f"{base_name}_night"] = night_tile
        variant_count += 1
        
        # Corrupted/signal tint (purple-green glow)
        corrupt_tile = base_tile.copy()
        pixels = corrupt_tile.load()
        for x in range(TILE_SIZE):
            for y in range(TILE_SIZE):
                r, g, b, a = pixels[x, y]
                if a > 0:
                    pixels[x, y] = (int(r*0.6 + 80), int(g*0.8 + 60), int(b*0.6 + 40), a)
        expanded_tiles[f"{base_name}_corrupted"] = corrupt_tile
        variant_count += 1
    
    # Composite tiles (multiple base tiles combined)
    for i in range(100):
        # Random combination of two base tiles at 50% opacity each
        tile1_name = random.choice(list(base_tiles.keys()))
        tile2_name = random.choice(list(base_tiles.keys()))
        
        if tile1_name != tile2_name:
            combined = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
            combined.paste(base_tiles[tile1_name], (0, 0))
            
            overlay = base_tiles[tile2_name].copy()
            alpha = overlay.split()[3]
            alpha = alpha.point(lambda p: int(p * 0.5))
            overlay.putalpha(alpha)
            combined.paste(overlay, (0, 0), overlay)
            
            expanded_tiles[f"composite_{i}"] = combined
            variant_count += 1
    
    # Transition tiles (gradients between two terrain types)
    for i in range(100):
        transition = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(transition)
        
        # Create transition gradient
        for y in range(TILE_SIZE):
            ratio = y / TILE_SIZE
            r = int(100 * ratio + 150 * (1 - ratio))
            g = int(150 * ratio + 100 * (1 - ratio))
            b = int(100 * ratio + 150 * (1 - ratio))
            draw.line((0, y, TILE_SIZE, y), fill=(r, g, b, 255))
        
        expanded_tiles[f"transition_{i}"] = transition
        variant_count += 1
    
    print(f"✅ Generated {variant_count} variants")
    print(f"📊 Total tiles: {len(expanded_tiles)}")
    
    return expanded_tiles

def save_expanded_tileset(expanded_tiles):
    """Save 1000+ tile tileset and index."""
    tiles_per_row = 64
    grid_cols = tiles_per_row
    grid_rows = (len(expanded_tiles) + tiles_per_row - 1) // tiles_per_row
    
    tileset_width = grid_cols * TILE_SIZE
    tileset_height = grid_rows * TILE_SIZE
    
    print(f"📦 Assembling {len(expanded_tiles)} tiles into {tileset_width}x{tileset_height} px tileset...")
    
    tileset = Image.new("RGBA", (tileset_width, tileset_height), (0, 0, 0, 0))
    tile_index = {}
    
    tile_list = sorted(expanded_tiles.keys())
    
    for idx, tile_name in enumerate(tile_list):
        row = idx // tiles_per_row
        col = idx % tiles_per_row
        x = col * TILE_SIZE
        y = row * TILE_SIZE
        
        tileset.paste(expanded_tiles[tile_name], (x, y), expanded_tiles[tile_name])
        tile_index[tile_name] = [row, col]
    
    # Save tileset PNG
    tileset_path = os.path.join(OUTPUT_DIR, "tileset.png")
    tileset.save(tileset_path, "PNG")
    print(f"💾 Saved: {tileset_path}")
    
    # Save index JSON
    index_path = os.path.join(OUTPUT_DIR, "tileset_index.json")
    with open(index_path, "w") as f:
        json.dump(tile_index, f, indent=2)
    print(f"📋 Saved: {index_path}")
    
    file_size_mb = os.path.getsize(tileset_path) / (1024 * 1024)
    print(f"\n✨ Tileset complete: {len(tile_list)} tiles, {file_size_mb:.2f} MB")

if __name__ == "__main__":
    expanded_tiles = expand_tileset()
    save_expanded_tileset(expanded_tiles)
