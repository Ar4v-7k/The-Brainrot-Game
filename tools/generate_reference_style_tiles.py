from __future__ import annotations

import argparse
import io
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = Path("/Users/aravsharma/Desktop/brainrotmon_reference_style_tiles/individual_tiles")


STYLE = (
    "single seamless top-down terrain texture tile only, full square filled edge to edge, "
    "lush RPG overworld reference style, rich varied greens and earthy browns, warm natural lighting, "
    "soft dark pixel outlines, painterly pixel art depth, subtle organic detail, tileable game ground texture, "
    "NOT a map, NOT a forest scene, NOT an object sprite, NOT a landscape, NOT isometric, "
    "NOT trees unless the tile name explicitly asks for trees, NOT pond unless water tile, "
    "NOT empty background, NOT border, NOT frame, NOT text"
)


@dataclass(frozen=True)
class TileJob:
    name: str
    prompt: str


BATCH_1: list[TileJob] = [
    TileJob("grass_light", "fresh bright green grass terrain, soft blade texture, warm highlights, full seamless ground tile"),
    TileJob("grass_medium", "medium green grass terrain, denser blades, subtle natural shadows, full seamless ground tile"),
    TileJob("grass_dark", "dark rich green lush grass terrain, moist-looking thick blades, full seamless ground tile"),
    TileJob("grass_patchy_dirt", "patchy grass terrain with warm bare dirt showing through organic gaps, full seamless ground tile"),
    TileJob("tall_grass", "tall wild grass terrain with visible taller bright blades, full seamless ground tile"),
    TileJob("worn_grass_path", "worn grass path terrain, blades rubbed away showing warm dirt underneath, full seamless ground tile"),
    TileJob("dead_yellow_grass", "dead yellowed dry grass terrain with brown brittle tips, full seamless ground tile"),
    TileJob("grass_daisies", "green grass terrain with tiny white daisy cluster accents, full seamless ground tile"),
    TileJob("grass_red_flowers", "green grass terrain with small red flowers scattered naturally, full seamless ground tile"),
    TileJob("grass_yellow_flowers", "green grass terrain with small yellow sunflower-like blooms, full seamless ground tile"),
    TileJob("grass_pink_flowers", "green grass terrain with soft pink blossom flowers, full seamless ground tile"),
    TileJob("grass_purple_flowers", "green grass terrain with purple wildflowers, full seamless ground tile"),
    TileJob("grass_blue_flowers", "green grass terrain with small blue bell flowers, full seamless ground tile"),
    TileJob("grass_orange_flowers", "green grass terrain with orange flowers, full seamless ground tile"),
    TileJob("grass_mixed_flowers", "green grass terrain with mixed colorful wildflower cluster, full seamless ground tile"),
    TileJob("grass_espresso_flowers", "green grass terrain with espresso-brown flowers unique to Rotria, warm dark petals, full seamless ground tile"),
]


def make_prompt(job: TileJob) -> str:
    return (
        f"Single square 128x128 source tile. {STYLE}. Tile content: {job.prompt}. "
        "The texture must fill the entire square edge to edge. No black padding. "
        "No border, no text, no labels, no grid, no UI. Orthographic top-down view. "
        "Crisp readable pixel art, suitable to downscale to 16x16 game tile."
    )


def generate(job: TileJob, out_dir: Path, model: str, seed: int, timeout: int) -> Path:
    prompt = make_prompt(job)
    params = {
        "width": "128",
        "height": "128",
        "model": model,
        "seed": str(seed),
        "nologo": "true",
        "private": "true",
        "safe": "true",
    }
    url = f"https://image.pollinations.ai/prompt/{quote(prompt)}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": "brainrotmon-reference-tile-generator/1.0"})
    with urlopen(request, timeout=timeout) as response:
        data = response.read()
    image = Image.open(io.BytesIO(data)).convert("RGBA")
    if image.size != (128, 128):
        image = image.resize((128, 128), Image.Resampling.LANCZOS)
    path = out_dir / f"{job.name}.png"
    image.save(path)
    (out_dir / f"{job.name}.txt").write_text(prompt)
    return path


def build_sheet(out_dir: Path, jobs: list[TileJob]) -> Path:
    cols = 8
    rows = (len(jobs) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * 128, rows * 128), (0, 0, 0, 255))
    for idx, job in enumerate(jobs):
        tile = Image.open(out_dir / f"{job.name}.png").convert("RGBA")
        row, col = divmod(idx, cols)
        sheet.paste(tile, (col * 128, row * 128))
    path = out_dir.parent / "reference_style_individual_tile_sheet.png"
    sheet.save(path)
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--model", default="sana")
    parser.add_argument("--seed", type=int, default=8890000)
    parser.add_argument("--delay", type=float, default=16.0)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--limit", type=int, default=len(BATCH_1))
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    jobs = BATCH_1[: args.limit]
    for idx, job in enumerate(jobs):
        if idx:
            time.sleep(args.delay)
        print(f"Generating {job.name}")
        path = generate(job, args.out_dir, args.model, args.seed + idx, args.timeout)
        print(f"Saved {path}")
    sheet = build_sheet(args.out_dir, jobs)
    print(f"Saved sheet {sheet}")


if __name__ == "__main__":
    main()
