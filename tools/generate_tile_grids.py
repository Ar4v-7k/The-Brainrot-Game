#!/usr/bin/env python3
"""
Generate tiles in batches (multiple tiles per API call) for Brainrotmon.
Each image contains a grid of tiles, then we cut them apart.
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
TILES_PER_ROW = 10
TILES_PER_COL = 10
TOTAL_TILES = 100


TILE_PROMPTS = [
    # ROW 1 — Basic grass (10 tiles)
    "fresh bright green grass with soft blade texture and warm highlights, pixel art top-down terrain tile, Stardew Valley quality",
    "medium green grass slightly darker, denser blades, small shadow at base, pixel art top-down terrain tile",
    "dark rich green grass, thick and lush, moist-looking, pixel art top-down terrain tile",
    "patchy grass with warm bare dirt showing through gaps, pixel art top-down terrain tile",
    "tall wild grass with visible taller blades poking up, bright green, pixel art top-down terrain tile",
    "worn grass path, blades rubbed away showing warm dirt underneath, pixel art top-down terrain tile",
    "dead yellowed grass with brown brittle tips, dry, pixel art top-down terrain tile",
    "grass with tiny white daisy cluster sitting in center, pixel art top-down terrain tile",
    "grass with small clover leaves scattered, pixel art top-down terrain tile",
    "grass with small insects or bugs visible, pixel art top-down terrain tile",

    # ROW 2 — Flower grass (10 tiles)
    "grass with small red flowers scattered across it, pixel art top-down terrain tile, Stardew Valley quality",
    "grass with yellow sunflower-like blooms, pixel art top-down terrain tile",
    "grass with pink blossom flowers, pixel art top-down terrain tile",
    "grass with purple wildflowers, pixel art top-down terrain tile",
    "grass with blue bell flowers, pixel art top-down terrain tile",
    "grass with orange flowers, pixel art top-down terrain tile",
    "grass with mixed colorful flower cluster, pixel art top-down terrain tile",
    "grass with espresso-brown flowers unique to Rotria, warm dark petals, pixel art top-down terrain tile",
    "grass with white tulips, pixel art top-down terrain tile",
    "grass with lavender flowers, soft purple, pixel art top-down terrain tile",

    # ROW 3 — Dirt and earth (10 tiles)
    "packed warm brown dirt, smooth worn texture, pixel art top-down terrain tile, Stardew Valley quality",
    "muddy dark wet dirt with slight shine and footprint impressions, pixel art top-down terrain tile",
    "dry cracked earth with deep fissure lines across surface, pixel art top-down terrain tile",
    "rocky dirt with small pebbles scattered, pixel art top-down terrain tile",
    "freshly turned dark soil like a garden, pixel art top-down terrain tile",
    "hard baked pale clay, very dry and pale tan, pixel art top-down terrain tile",
    "dirt path center tile, wheel ruts worn in, warm earthy brown, pixel art top-down terrain tile",
    "dirt with a single boot print pressed into it, pixel art top-down terrain tile",
    "dark rich soil, almost black-brown, fertile look, pixel art top-down terrain tile",
    "sandy dirt mixture, light brown, pixel art top-down terrain tile",

    # ROW 4 — Cobblestone paths (10 tiles)
    "grey cobblestone with rounded stones and dark grout lines between them, pixel art top-down terrain tile, Stardew Valley quality",
    "worn cobblestone, same stones but more faded and uneven, pixel art top-down terrain tile",
    "mossy cobblestone with green moss growing in the grout gaps, pixel art top-down terrain tile",
    "cracked cobblestone with a visible split across several stones, pixel art top-down terrain tile",
    "smooth cut stone slabs in regular rectangular pattern, cool grey, pixel art top-down terrain tile",
    "ancient overgrown stone path with small weeds growing in cracks, pixel art top-down terrain tile",
    "pale limestone path, bright and clean, slightly yellow-white, pixel art top-down terrain tile",
    "dark basalt stone path, almost black, smooth, pixel art top-down terrain tile",
    "cobblestone with moss and small flowers growing, pixel art top-down terrain tile",
    "stepping stones in grass, flat stones surrounded by grass, pixel art top-down terrain tile",

    # ROW 5 — Sand (10 tiles)
    "warm golden dry sand with ripple lines across surface, pixel art top-down terrain tile, Stardew Valley quality",
    "dark wet sand near water with subtle shine, pixel art top-down terrain tile",
    "pale white sand very fine and light, pixel art top-down terrain tile",
    "coarse brown sand with tiny pebble texture, pixel art top-down terrain tile",
    "sand with small shells visible on surface, pixel art top-down terrain tile",
    "sand with footprint impressions pressed in, pixel art top-down terrain tile",
    "wind-rippled sand with wave pattern, pixel art top-down terrain tile",
    "desert red-orange sand warm and hot looking, pixel art top-down terrain tile",
    "sand with small desert rocks scattered, pixel art top-down terrain tile",
    "sand with desert plant remains, dry twigs, pixel art top-down terrain tile",

    # ROW 6 — Snow and ice (10 tiles)
    "fresh clean white snow with faint blue shadow in dips, pixel art top-down terrain tile, Stardew Valley quality",
    "packed compressed grey-white snow with icy sheen, pixel art top-down terrain tile",
    "snow with boot tracks crossing diagonally, pixel art top-down terrain tile",
    "snow melting at edges showing green grass beneath, pixel art top-down terrain tile",
    "smooth pale blue ice mirror-like with soft reflection lines, pixel art top-down terrain tile",
    "cracked ice with dark fissure lines spreading, pixel art top-down terrain tile",
    "thin ice with darker water visible beneath, pixel art top-down terrain tile",
    "frost pattern like lace crystals on a pale surface, pixel art top-down terrain tile",
    "snow with small snow-covered rock, pixel art top-down terrain tile",
    "snow with frozen leaf frozen in ice, pixel art top-down terrain tile",

    # ROW 7 — Cave and underground (10 tiles)
    "dark rough cave stone floor, very dark grey-brown, pixel art top-down terrain tile, Stardew Valley quality",
    "wet cave floor with moisture sheen and puddle, pixel art top-down terrain tile",
    "gravel cave floor with small loose stones, pixel art top-down terrain tile",
    "ancient tile cave floor like old civilisation, faded mosaic, pixel art top-down terrain tile",
    "solid cave rock wall, jagged craggy texture, darkest tile, pixel art top-down terrain tile",
    "cave wall with water seeping through and moss, pixel art top-down terrain tile",
    "cave wall with embedded glowing blue crystal, pixel art top-down terrain tile",
    "cave floor with small crack down the center, pixel art top-down terrain tile",
    "cave floor with fossil imprint in stone, pixel art top-down terrain tile",
    "cave floor with bones or skeleton remains, dark atmospheric, pixel art top-down terrain tile",

    # ROW 8 — Ruin and ancient (10 tiles)
    "cracked ancient stone mosaic floor with faded painted colors, pixel art top-down terrain tile, Stardew Valley quality",
    "worn overgrown ruin stone floor with small plants growing in gaps, pixel art top-down terrain tile",
    "ancient ruin tile with carved symbol faintly visible, pixel art top-down terrain tile",
    "ruin floor with short grass growing through cracks, pixel art top-down terrain tile",
    "ancient marble floor cracked but still elegant, cream colored, pixel art top-down terrain tile",
    "ruin floor with fallen stone block sitting on it, pixel art top-down terrain tile",
    "desert ruin floor covered in fine sand, part buried, pixel art top-down terrain tile",
    "final dungeon floor dark and ominous, ancient stone with faint glow, pixel art top-down terrain tile",
    "volcanic rock floor, dark with red-orange glow cracks, pixel art top-down terrain tile",
    "magical glowing floor tile with arcane symbols, soft blue-green glow, pixel art top-down terrain tile",
]


def generate_grid(prompts: list[str], out_path: Path, model: str, seed: int, 
                  tiles_across: int = 5, tiles_down: int = 2, tile_size: int = 128,
                  timeout: int = 120) -> Path:
    """Generate a grid of tiles in a single image via Pollinations API."""
    width = tiles_across * tile_size
    height = tiles_down * tile_size

    prompt_text = " | ".join(prompts)
    full_prompt = f"Pixel art tileset grid: {prompt_text}. Pure black background #000000. No gaps between tiles. Each tile {tile_size}x{tile_size} pixels. Warm cozy RPG Stardew Valley style."

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


def cut_grid(grid_path: Path, out_dir: Path, tiles_across: int = 5, tiles_down: int = 2, tile_size: int = 128, start_index: int = 0):
    """Cut a grid image into individual tiles."""
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
            print(f"  Saved tile_{idx:03d}.png")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate tiles in grids for Brainrotmon.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--batch-name", default="batch_1a_grass_terrain")
    parser.add_argument("--model", default="flux")
    parser.add_argument("--seed", type=int, default=7072026)
    parser.add_argument("--delay", type=float, default=12.0)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--tiles-per-image", type=int, default=10, help="Tiles per grid image (5x2=10 recommended)")
    parser.add_argument("--skip-existing", action="store_true", help="Skip tiles that already exist")
    args = parser.parse_args()

    out_dir = args.out_dir / args.batch_name
    out_dir.mkdir(parents=True, exist_ok=True)

    tiles_per_image = args.tiles_per_image
    if tiles_per_image == 10:
        tiles_across, tiles_down = 5, 2
    elif tiles_per_image == 6:
        tiles_across, tiles_down = 3, 2
    else:
        tiles_across, tiles_down = 5, 2

    num_images = (TOTAL_TILES + tiles_per_image - 1) // tiles_per_image

    print(f"Generating {TOTAL_TILES} tiles in {num_images} images ({tiles_across}x{tiles_down} grid each)")
    print(f"Output: {out_dir}\n")

    for img_idx in range(num_images):
        start_tile = img_idx * tiles_per_image
        end_tile = min(start_tile + tiles_per_image, TOTAL_TILES)

        if args.skip_existing:
            existing_count = sum(1 for i in range(start_tile, end_tile) if (out_dir / f"tile_{i:03d}.png").exists())
            if existing_count == (end_tile - start_tile):
                print(f"Skipping grid_{img_idx:02d} (all {tiles_per_image} tiles exist)")
                continue

        prompts = TILE_PROMPTS[start_tile:end_tile]

        grid_path = out_dir / f"grid_{img_idx:02d}.png"
        seed = args.seed + img_idx

        print(f"Generating grid_{img_idx:02d} (tiles {start_tile}-{end_tile-1}, seed={seed})...")

        try:
            generate_grid(prompts, grid_path, model=args.model, seed=seed,
                          tiles_across=tiles_across, tiles_down=tiles_down, tile_size=TILE_SIZE, timeout=args.timeout)
            print("  Done, cutting into tiles...")
            cut_grid(grid_path, out_dir, tiles_across, tiles_down, TILE_SIZE, start_tile)
        except (HTTPError, URLError, TimeoutError, ConnectionError, OSError, RuntimeError) as exc:
            print(f"  FAILED: {exc}")
            continue

        if img_idx < num_images - 1:
            time.sleep(args.delay)

    print(f"\n✓ Batch complete: {out_dir}")
    print(f"  {TOTAL_TILES} individual tiles generated")


if __name__ == "__main__":
    main()