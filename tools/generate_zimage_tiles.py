#!/usr/bin/env python3
"""
Generate 100 tiles in 5 images using Pollinations zimage model.
Each image: 4x5 grid = 20 tiles, 512x640 pixels total.
"""
from __future__ import annotations

import argparse
import io
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = Path("/Users/aravsharma/Desktop/brainrotmon_final_tilesets")

TILE_SIZE = 128
TILES_ACROSS = 4
TILES_DOWN = 5
TILES_PER_IMAGE = TILES_ACROSS * TILES_DOWN
NUM_IMAGES = 5
TOTAL_TILES = 100


TILE_PROMPTS = [
    # IMAGE 1 - Grass & Basic Terrain (tiles 0-19)
    "fresh bright green grass with soft blade texture, pixel art top-down terrain tile, 8-bit style",
    "medium green grass slightly darker, pixel art top-down terrain tile, 8-bit style",
    "dark rich green grass thick and lush, pixel art top-down terrain tile, 8-bit style",
    "patchy grass with bare dirt showing, pixel art top-down terrain tile, 8-bit style",
    "tall wild grass with blades poking up, pixel art top-down terrain tile, 8-bit style",
    "worn grass path with dirt showing, pixel art top-down terrain tile, 8-bit style",
    "dead yellowed grass dry, pixel art top-down terrain tile, 8-bit style",
    "grass with white daisy cluster, pixel art top-down terrain tile, 8-bit style",
    "grass with red flowers, pixel art top-down terrain tile, 8-bit style",
    "grass with yellow sunflowers, pixel art top-down terrain tile, 8-bit style",
    "grass with purple wildflowers, pixel art top-down terrain tile, 8-bit style",
    "grass with pink blossoms, pixel art top-down terrain tile, 8-bit style",
    "packed warm brown dirt, pixel art top-down terrain tile, 8-bit style",
    "muddy dark wet dirt, pixel art top-down terrain tile, 8-bit style",
    "dry cracked earth, pixel art top-down terrain tile, 8-bit style",
    "rocky dirt with pebbles, pixel art top-down terrain tile, 8-bit style",
    "freshly turned dark soil, pixel art top-down terrain tile, 8-bit style",
    "hard baked pale clay, pixel art top-down terrain tile, 8-bit style",
    "dirt path with wheel ruts, pixel art top-down terrain tile, 8-bit style",
    "dirt with boot print, pixel art top-down terrain tile, 8-bit style",

    # IMAGE 2 - Stone & Paths (tiles 20-39)
    "grey cobblestone with dark grout lines, pixel art top-down terrain tile, 8-bit style",
    "worn cobblestone faded, pixel art top-down terrain tile, 8-bit style",
    "mossy cobblestone with green moss, pixel art top-down terrain tile, 8-bit style",
    "cracked cobblestone split, pixel art top-down terrain tile, 8-bit style",
    "smooth cut stone slabs regular pattern, pixel art top-down terrain tile, 8-bit style",
    "ancient overgrown stone path with weeds, pixel art top-down terrain tile, 8-bit style",
    "pale limestone path bright clean, pixel art top-down terrain tile, 8-bit style",
    "dark basalt stone path smooth, pixel art top-down terrain tile, 8-bit style",
    "stepping stones in grass, pixel art top-down terrain tile, 8-bit style",
    "cobblestone with flowers, pixel art top-down terrain tile, 8-bit style",
    "warm golden dry sand with ripples, pixel art top-down terrain tile, 8-bit style",
    "dark wet sand near water, pixel art top-down terrain tile, 8-bit style",
    "pale white sand fine, pixel art top-down terrain tile, 8-bit style",
    "coarse brown sand with pebbles, pixel art top-down terrain tile, 8-bit style",
    "sand with small shells, pixel art top-down terrain tile, 8-bit style",
    "sand with footprints, pixel art top-down terrain tile, 8-bit style",
    "wind-rippled sand pattern, pixel art top-down terrain tile, 8-bit style",
    "desert red-orange sand hot, pixel art top-down terrain tile, 8-bit style",
    "sand with desert rocks, pixel art top-down terrain tile, 8-bit style",
    "sand with dry twigs, pixel art top-down terrain tile, 8-bit style",

    # IMAGE 3 - Snow, Ice, Cave (tiles 40-59)
    "fresh clean white snow, pixel art top-down terrain tile, 8-bit style",
    "packed grey-white snow with icy sheen, pixel art top-down terrain tile, 8-bit style",
    "snow with boot tracks, pixel art top-down terrain tile, 8-bit style",
    "snow melting showing grass beneath, pixel art top-down terrain tile, 8-bit style",
    "smooth pale blue ice mirror, pixel art top-down terrain tile, 8-bit style",
    "cracked ice with fissures, pixel art top-down terrain tile, 8-bit style",
    "thin ice with water beneath, pixel art top-down terrain tile, 8-bit style",
    "frost pattern crystals, pixel art top-down terrain tile, 8-bit style",
    "snow with snow-covered rock, pixel art top-down terrain tile, 8-bit style",
    "snow with frozen leaf, pixel art top-down terrain tile, 8-bit style",
    "dark rough cave stone floor, pixel art top-down terrain tile, 8-bit style",
    "wet cave floor with puddle, pixel art top-down terrain tile, 8-bit style",
    "gravel cave floor with stones, pixel art top-down terrain tile, 8-bit style",
    "ancient tile cave floor mosaic, pixel art top-down terrain tile, 8-bit style",
    "solid cave rock wall jagged, pixel art top-down terrain tile, 8-bit style",
    "cave wall with water and moss, pixel art top-down terrain tile, 8-bit style",
    "cave wall with glowing crystal, pixel art top-down terrain tile, 8-bit style",
    "cave floor with crack, pixel art top-down terrain tile, 8-bit style",
    "cave floor with fossil, pixel art top-down terrain tile, 8-bit style",
    "cave floor with bones dark, pixel art top-down terrain tile, 8-bit style",

    # IMAGE 4 - Ruin, Water edges, Vegetation (tiles 60-79)
    "cracked ancient stone mosaic floor, pixel art top-down terrain tile, 8-bit style",
    "worn overgrown ruin stone floor, pixel art top-down terrain tile, 8-bit style",
    "ancient ruin tile with carved symbol, pixel art top-down terrain tile, 8-bit style",
    "ruin floor with grass in cracks, pixel art top-down terrain tile, 8-bit style",
    "ancient marble floor cracked elegant, pixel art top-down terrain tile, 8-bit style",
    "ruin floor with fallen stone block, pixel art top-down terrain tile, 8-bit style",
    "desert ruin floor covered in sand, pixel art top-down terrain tile, 8-bit style",
    "dark ominous dungeon floor with glow, pixel art top-down terrain tile, 8-bit style",
    "volcanic rock floor with red glow, pixel art top-down terrain tile, 8-bit style",
    "magical glowing floor with symbols, pixel art top-down terrain tile, 8-bit style",
    "small round leafy green bush, pixel art top-down terrain tile, 8-bit style",
    "large dense green bush, pixel art top-down terrain tile, 8-bit style",
    "berry bush with red berries, pixel art top-down terrain tile, 8-bit style",
    "berry bush with orange berries, pixel art top-down terrain tile, 8-bit style",
    "snowy bush covered in white, pixel art top-down terrain tile, 8-bit style",
    "thorny dry brown bush, pixel art top-down terrain tile, 8-bit style",
    "tropical colorful bush with flowers, pixel art top-down terrain tile, 8-bit style",
    "small desert succulent, pixel art top-down terrain tile, 8-bit style",
    "small red flower in grass, pixel art top-down terrain tile, 8-bit style",
    "yellow sunflower in grass, pixel art top-down terrain tile, 8-bit style",

    # IMAGE 5 - More vegetation, trees, objects (tiles 80-99)
    "white daisy cluster in grass, pixel art top-down terrain tile, 8-bit style",
    "purple flower delicate, pixel art top-down terrain tile, 8-bit style",
    "blue wildflower small, pixel art top-down terrain tile, 8-bit style",
    "pink blossom pretty, pixel art top-down terrain tile, 8-bit style",
    "cactus small desert plant, pixel art top-down terrain tile, 8-bit style",
    "tomato vine with red tomatoes, pixel art top-down terrain tile, 8-bit style",
    "tree stump with rings mossy, pixel art top-down terrain tile, 8-bit style",
    "hollow stump with dark opening, pixel art top-down terrain tile, 8-bit style",
    "fallen log mossy on grass, pixel art top-down terrain tile, 8-bit style",
    "pile of small sticks and branches, pixel art top-down terrain tile, 8-bit style",
    "small rounded grey rock in grass, pixel art top-down terrain tile, 8-bit style",
    "medium mossy rock dark green, pixel art top-down terrain tile, 8-bit style",
    "large boulder fills most of tile, pixel art top-down terrain tile, 8-bit style",
    "rock pile several rocks stacked, pixel art top-down terrain tile, 8-bit style",
    "oak tree round canopy bright green, pixel art top-down terrain tile, 8-bit style",
    "pine tree dark triangular pointed, pixel art top-down terrain tile, 8-bit style",
    "palm tree tropical large fronds, pixel art top-down terrain tile, 8-bit style",
    "dead tree bare grey branches, pixel art top-down terrain tile, 8-bit style",
    "autumn tree orange red yellow leaves, pixel art top-down terrain tile, 8-bit style",
    "snowy tree white on branches, pixel art top-down terrain tile, 8-bit style",
]


def generate_grid(prompts: list[str], out_path: Path, model: str, seed: int, 
                  tiles_across: int = 4, tiles_down: int = 5, tile_size: int = 128,
                  timeout: int = 120) -> Path:
    width = tiles_across * tile_size
    height = tiles_down * tile_size

    prompt_text = " | ".join(prompts)
    full_prompt = f"Pixel art RPG tileset grid: {prompt_text}. Pure black background #000000. 4x5 grid layout, 20 tiles. Each tile {tile_size}x{tile_size} pixels. Clean pixel art style, crisp edges, limited palette, 8-bit retro game aesthetic. Stardew Valley quality."

    params = {
        "width": str(width),
        "height": str(height),
        "model": model,
        "seed": str(seed),
        "nologo": "true",
        "safe": "true",
    }
    url = f"https://image.pollinations.ai/prompt/{quote(full_prompt)}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": "brainrotmon-tile-generator/1.0"})

    with urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        data = response.read()

    if not data or not content_type.startswith("image/"):
        raise RuntimeError(f"Pollinations returned {content_type or 'empty response'}")

    image = Image.open(io.BytesIO(data)).convert("RGBA")
    if image.size != (width, height):
        image = image.resize((width, height), Image.Resampling.LANCZOS)

    image.save(out_path)
    return out_path


def cut_grid(grid_path: Path, out_dir: Path, tiles_across: int = 4, tiles_down: int = 5, 
             tile_size: int = 128, start_index: int = 0):
    grid = Image.open(grid_path).convert("RGBA")

    for row in range(tiles_down):
        for col in range(tiles_across):
            idx = start_index + row * tiles_across + col
            if idx >= TOTAL_TILES:
                break

            x = col * tile_size
            y = row * tile_size
            tile = grid.crop((x, y, x + tile_size, y + tile_size))
            tile_path = out_dir / f"tile_{idx:03d}.png"
            tile.save(tile_path)


def pixelate_tile(tile_path: Path, target_size: int = 32):
    tile = Image.open(tile_path).convert("RGBA")
    small = tile.resize((target_size, target_size), Image.Resampling.NEAREST)
    return small


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate 100 tiles in 5 images with zimage model.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--batch-name", default="batch_1_zimage")
    parser.add_argument("--model", default="zimage")
    parser.add_argument("--seed", type=int, default=7072026)
    parser.add_argument("--delay", type=float, default=20.0)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--pixelate", action="store_true", help="Pixelate tiles to 32x32 after generation")
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    out_dir = args.out_dir / args.batch_name
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating {TOTAL_TILES} tiles in {NUM_IMAGES} images ({TILES_ACROSS}x{TILES_DOWN} grid)")
    print(f"Model: {args.model}, Output: {out_dir}\n")

    for img_idx in range(NUM_IMAGES):
        start_tile = img_idx * TILES_PER_IMAGE
        end_tile = min(start_tile + TILES_PER_IMAGE, TOTAL_TILES)
        
        if args.skip_existing:
            existing = sum(1 for i in range(start_tile, end_tile) if (out_dir / f"tile_{i:03d}.png").exists())
            if existing == (end_tile - start_tile):
                print(f"Skip image_{img_idx:02d} (all {TILES_PER_IMAGE} tiles exist)")
                continue

        prompts = TILE_PROMPTS[start_tile:end_tile]
        grid_path = out_dir / f"grid_{img_idx:02d}.png"
        seed = args.seed + img_idx

        print(f"Generating grid_{img_idx:02d} (tiles {start_tile}-{end_tile-1})...", end=" ", flush=True)

        try:
            generate_grid(prompts, grid_path, model=args.model, seed=seed,
                          tiles_across=TILES_ACROSS, tiles_down=TILES_DOWN, tile_size=TILE_SIZE, 
                          timeout=args.timeout)
            print("done")
            cut_grid(grid_path, out_dir, TILES_ACROSS, TILES_DOWN, TILE_SIZE, start_tile)
        except Exception as e:
            print(f"FAILED: {e}")
            continue

        if img_idx < NUM_IMAGES - 1:
            time.sleep(args.delay)

    if args.pixelate:
        print("\nPixelating tiles to 32x32...")
        pixel_dir = out_dir / "pixelated"
        pixel_dir.mkdir(exist_ok=True)
        
        for i in range(TOTAL_TILES):
            tile_path = out_dir / f"tile_{i:03d}.png"
            if tile_path.exists():
                small = pixelate_tile(tile_path, 32)
                small.save(pixel_dir / f"tile_{i:03d}.png")
        
        print(f"Saved 32x32 pixelated tiles to {pixel_dir}")

    print(f"\n✓ Complete: {out_dir}")


if __name__ == "__main__":
    main()