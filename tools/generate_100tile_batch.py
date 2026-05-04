#!/usr/bin/env python3
"""
Generate 100-tile batches (10x10 grid = 1280x1280) for Brainrotmon.
Each tile generated individually via Pollinations API with model=flux.
After all 100 tiles generated, stitch into a single 1280x1280 sheet.
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


TILE_PROMPTS = [
    # ROW 1 — Basic grass (10 tiles)
    "Single seamless top-down pixel art terrain tile: fresh bright green grass with soft blade texture and warm highlights, warm cozy RPG style, Stardew Valley quality, 128x128",
    "Single seamless top-down pixel art terrain tile: medium green grass slightly darker, denser blades, small shadow at base, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: dark rich green grass, thick and lush, moist-looking, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: patchy grass with warm bare dirt showing through gaps, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: tall wild grass with visible taller blades poking up, bright green, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: worn grass path, blades rubbed away showing warm dirt underneath, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: dead yellowed grass with brown brittle tips, dry, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: grass with tiny white daisy cluster sitting in center, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: grass with small clover leaves scattered, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: grass with small insects or bugs visible, warm cozy RPG style, 128x128",

    # ROW 2 — Flower grass (10 tiles)
    "Single seamless top-down pixel art terrain tile: grass with small red flowers scattered across it, warm cozy RPG style, Stardew Valley quality, 128x128",
    "Single seamless top-down pixel art terrain tile: grass with yellow sunflower-like blooms, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: grass with pink blossom flowers, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: grass with purple wildflowers, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: grass with blue bell flowers, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: grass with orange flowers, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: grass with mixed colorful flower cluster, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: grass with espresso-brown flowers unique to Rotria, warm dark petals, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: grass with white tulips, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: grass with lavender flowers, soft purple, warm cozy RPG style, 128x128",

    # ROW 3 — Dirt and earth (10 tiles)
    "Single seamless top-down pixel art terrain tile: packed warm brown dirt, smooth worn texture, warm cozy RPG style, Stardew Valley quality, 128x128",
    "Single seamless top-down pixel art terrain tile: muddy dark wet dirt with slight shine and footprint impressions, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: dry cracked earth with deep fissure lines across surface, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: rocky dirt with small pebbles scattered, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: freshly turned dark soil like a garden, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: hard baked pale clay, very dry and pale tan, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: dirt path center tile, wheel ruts worn in, warm earthy brown, 128x128",
    "Single seamless top-down pixel art terrain tile: dirt with a single boot print pressed into it, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: dark rich soil, almost black-brown, fertile look, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: sandy dirt mixture, light brown, warm cozy RPG style, 128x128",

    # ROW 4 — Cobblestone paths (10 tiles)
    "Single seamless top-down pixel art terrain tile: grey cobblestone with rounded stones and dark grout lines between them, warm cozy RPG style, Stardew Valley quality, 128x128",
    "Single seamless top-down pixel art terrain tile: worn cobblestone, same stones but more faded and uneven, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: mossy cobblestone with green moss growing in the grout gaps, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: cracked cobblestone with a visible split across several stones, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: smooth cut stone slabs in regular rectangular pattern, cool grey, 128x128",
    "Single seamless top-down pixel art terrain tile: ancient overgrown stone path with small weeds growing in cracks, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: pale limestone path, bright and clean, slightly yellow-white, 128x128",
    "Single seamless top-down pixel art terrain tile: dark basalt stone path, almost black, smooth, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: cobblestone with moss and small flowers growing, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: stepping stones in grass, flat stones surrounded by grass, warm cozy RPG style, 128x128",

    # ROW 5 — Sand (10 tiles)
    "Single seamless top-down pixel art terrain tile: warm golden dry sand with ripple lines across surface, warm cozy RPG style, Stardew Valley quality, 128x128",
    "Single seamless top-down pixel art terrain tile: dark wet sand near water with subtle shine, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: pale white sand very fine and light, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: coarse brown sand with tiny pebble texture, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: sand with small shells visible on surface, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: sand with footprint impressions pressed in, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: wind-rippled sand with wave pattern, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: desert red-orange sand warm and hot looking, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: sand with small desert rocks scattered, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: sand with desert plant remains, dry twigs, warm cozy RPG style, 128x128",

    # ROW 6 — Snow and ice (10 tiles)
    "Single seamless top-down pixel art terrain tile: fresh clean white snow with faint blue shadow in dips, warm cozy RPG style, Stardew Valley quality, 128x128",
    "Single seamless top-down pixel art terrain tile: packed compressed grey-white snow with icy sheen, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: snow with boot tracks crossing diagonally, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: snow melting at edges showing green grass beneath, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: smooth pale blue ice mirror-like with soft reflection lines, 128x128",
    "Single seamless top-down pixel art terrain tile: cracked ice with dark fissure lines spreading, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: thin ice with darker water visible beneath, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: frost pattern like lace crystals on a pale surface, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: snow with small snow-covered rock, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: snow with frozen leaf frozen in ice, warm cozy RPG style, 128x128",

    # ROW 7 — Cave and underground (10 tiles)
    "Single seamless top-down pixel art terrain tile: dark rough cave stone floor, very dark grey-brown, warm cozy RPG style, Stardew Valley quality, 128x128",
    "Single seamless top-down pixel art terrain tile: wet cave floor with moisture sheen and puddle, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: gravel cave floor with small loose stones, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: ancient tile cave floor like old civilisation, faded mosaic, 128x128",
    "Single seamless top-down pixel art terrain tile: solid cave rock wall, jagged craggy texture, darkest tile, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: cave wall with water seeping through and moss, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: cave wall with embedded glowing blue crystal, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: cave floor with small crack down the center, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: cave floor with fossil imprint in stone, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: cave floor with bones or skeleton remains, dark atmospheric, 128x128",

    # ROW 8 — Ruin and ancient (10 tiles)
    "Single seamless top-down pixel art terrain tile: cracked ancient stone mosaic floor with faded painted colors, warm cozy RPG style, Stardew Valley quality, 128x128",
    "Single seamless top-down pixel art terrain tile: worn overgrown ruin stone floor with small plants growing in gaps, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: ancient ruin tile with carved symbol faintly visible, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: ruin floor with short grass growing through cracks, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: ancient marble floor cracked but still elegant, cream colored, 128x128",
    "Single seamless top-down pixel art terrain tile: ruin floor with fallen stone block sitting on it, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: desert ruin floor covered in fine sand, part buried, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: final dungeon floor dark and ominous, ancient stone with faint glow, 128x128",
    "Single seamless top-down pixel art terrain tile: volcanic rock floor, dark with red-orange glow cracks, warm cozy RPG style, 128x128",
    "Single seamless top-down pixel art terrain tile: magical glowing floor tile with arcane symbols, soft blue-green glow, 128x128",
]


def generate_tile(prompt: str, out_path: Path, model: str, seed: int, width: int = 128, height: int = 128, timeout: int = 120) -> Path:
    """Generate a single tile via Pollinations API."""
    params = {
        "width": str(width),
        "height": str(height),
        "model": model,
        "seed": str(seed),
        "nologo": "true",
        "safe": "true",
    }
    url = f"https://image.pollinations.ai/prompt/{quote(prompt)}?{urlencode(params)}"
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


def stitch_tiles(tile_dir: Path, output_path: Path, tiles_per_row: int = 10, tile_size: int = 128):
    """Stitch individual tiles into a single sheet."""
    tiles = sorted(tile_dir.glob("tile_*.png"))
    if not tiles:
        raise ValueError(f"No tiles found in {tile_dir}")

    cols = tiles_per_row
    rows = (len(tiles) + cols - 1) // cols

    sheet = Image.new("RGBA", (cols * tile_size, rows * tile_size), (0, 0, 0, 255))

    for idx, tile_path in enumerate(tiles):
        row = idx // cols
        col = idx % cols
        tile = Image.open(tile_path).convert("RGBA")
        if tile.size != (tile_size, tile_size):
            tile = tile.resize((tile_size, tile_size), Image.Resampling.LANCZOS)
        sheet.paste(tile, (col * tile_size, row * tile_size))

    sheet.save(output_path)
    print(f"Stitched {len(tiles)} tiles into {output_path}")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate 100-tile batch for Brainrotmon.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--batch-name", default="batch_1a_grass_terrain")
    parser.add_argument("--model", default="flux", help="Pollinations model (flux for Flux Schnell)")
    parser.add_argument("--seed", type=int, default=7072026)
    parser.add_argument("--delay", type=float, default=12.0, help="Delay between requests in seconds")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--skip-existing", action="store_true", help="Skip tiles that already exist")
    parser.add_argument("--stitch-only", action="store_true", help="Only stitch existing tiles, don't generate")
    args = parser.parse_args()

    out_dir = args.out_dir / args.batch_name
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.stitch_only:
        output_sheet = args.out_dir / f"{args.batch_name}_1280x1280.png"
        stitch_tiles(out_dir, output_sheet)
        return

    print(f"Generating {len(TILE_PROMPTS)} tiles for {args.batch_name}")
    print(f"Output directory: {out_dir}")

    for idx, prompt in enumerate(TILE_PROMPTS):
        tile_path = out_dir / f"tile_{idx:03d}.png"

        if args.skip_existing and tile_path.exists():
            print(f"Skipping tile_{idx:03d} (exists)")
            continue

        seed = args.seed + idx
        print(f"Generating tile_{idx:03d} (seed={seed})...", end=" ", flush=True)

        try:
            generate_tile(prompt, tile_path, model=args.model, seed=seed, timeout=args.timeout)
            print("done")
        except (HTTPError, URLError, TimeoutError, ConnectionError, OSError, RuntimeError) as exc:
            print(f"FAILED: {exc}")
            continue

        if idx < len(TILE_PROMPTS) - 1:
            time.sleep(args.delay)

    output_sheet = args.out_dir / f"{args.batch_name}_1280x1280.png"
    stitch_tiles(out_dir, output_sheet)
    print(f"\nBatch complete: {output_sheet}")


if __name__ == "__main__":
    main()