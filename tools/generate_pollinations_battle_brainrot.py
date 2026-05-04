from __future__ import annotations

import io
import os
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw, ImageFont


MAGENTA = (255, 0, 255, 255)
BLACK = (0, 0, 0, 255)
OUT_DIR = Path("/Users/aravsharma/Desktop/brainrotmon_final_tilesets/new_brainrots")
OUT_PATH = OUT_DIR / "pollinations_bombombini_gusini_battle_sheet.png"
ROWS_DIR = OUT_DIR / "pollinations_bombombini_gusini_rows"


@dataclass(frozen=True)
class RowJob:
    name: str
    width: int
    height: int
    prompt: str


CHARACTER = "Bombombini Gusini, chaotic goose bomber brainrot, white goose, orange beak, pilot goggles, bomber jacket, explosive tail feathers, mischievous angry eyes"
STYLE = "GBA Pokemon battle sprite pixel art, warm colors, dark outlines, expressive, crisp pixels, pure magenta #FF00FF background, no text"

ROWS = [
    RowJob("row_01_idle", 576, 96, f"6 frame horizontal sprite strip, idle loop, {CHARACTER}, breathing, swaying, goggles bounce, tail twitch, {STYLE}"),
    RowJob("row_02_honk_missile", 576, 96, f"6 frame horizontal sprite strip, Honk Missile attack, {CHARACTER}, windup, beak opens, tiny rocket fires, recoil, return stance, {STYLE}"),
    RowJob("row_03_bread_bomb", 576, 96, f"6 frame horizontal sprite strip, Bread Bomb attack, {CHARACTER}, pulls explosive bread loaf, winds up, throws, follow through, return stance, {STYLE}"),
    RowJob("row_04_wing_slap", 576, 96, f"6 frame horizontal sprite strip, Wing Slap attack, {CHARACTER}, crouch, wing windup, slap strike, motion smear, recover, {STYLE}"),
    RowJob("row_05_nest_dive", 576, 96, f"6 frame horizontal sprite strip, Nest Dive attack, {CHARACTER}, jump windup, leap, dive slam, feather burst, recover, {STYLE}"),
    RowJob("row_06_honk_projectile", 192, 32, "6 frame horizontal sprite strip, projectile only, tiny goose beak rocket spinning mid flight, 32x32 frames, pixel art, pure magenta #FF00FF background, no text"),
    RowJob("row_07_honk_impact", 384, 64, "6 frame horizontal sprite strip, impact effect only, orange yellow honk missile explosion with smoke, 64x64 frames, pixel art, pure magenta #FF00FF background, no text"),
    RowJob("row_08_bread_projectile", 192, 32, "6 frame horizontal sprite strip, projectile only, explosive bread loaf tumbling mid flight, 32x32 frames, pixel art, pure magenta #FF00FF background, no text"),
    RowJob("row_09_bread_impact", 384, 64, "6 frame horizontal sprite strip, impact effect only, bread crumb explosion with warm smoke, 64x64 frames, pixel art, pure magenta #FF00FF background, no text"),
    RowJob("row_10_flinch", 576, 96, f"6 frame horizontal sprite strip, hit flinch reaction, {CHARACTER}, gets hit, recoils, eyes wide, feathers fly, recovers, {STYLE}"),
]


def fetch_image(job: RowJob, model: str, seed: int, timeout: int) -> Image.Image:
    params = {
        "width": str(job.width),
        "height": str(job.height),
        "model": model,
        "seed": str(seed),
        "nologo": "true",
        "safe": "true",
    }
    api_key = os.environ.get("POLLINATIONS_API_KEY")
    if api_key:
        params["token"] = api_key

    url = f"https://image.pollinations.ai/prompt/{quote(job.prompt)}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": "brainrotmon-pollinations-generator/1.0"})
    with urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        data = response.read()
    if not content_type.startswith("image/"):
        raise RuntimeError(f"Pollinations returned {content_type or 'unknown content type'}")
    image = Image.open(io.BytesIO(data)).convert("RGBA")
    if image.size != (job.width, job.height):
        image = image.resize((job.width, job.height), Image.Resampling.NEAREST)
    return image


def draw_title(sheet: Image.Image) -> None:
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 9)
    except OSError:
        font = ImageFont.load_default()
    title = "Bombombini Gusini | Honk Missile | Bread Bomb | Wing Slap | Nest Dive"
    draw.text((4, 7), title, fill=BLACK, font=font)


def assemble(rows: list[Image.Image]) -> Image.Image:
    title_h = 24
    line_h = 1
    width = 576
    height = title_h + line_h + sum(row.height for row in rows) + line_h * (len(rows) - 1)
    sheet = Image.new("RGBA", (width, height), MAGENTA)
    draw_title(sheet)
    draw = ImageDraw.Draw(sheet)
    y = title_h
    draw.rectangle((0, y, width - 1, y), fill=BLACK)
    y += line_h
    for idx, row in enumerate(rows):
        sheet.paste(row, (0, y))
        y += row.height
        if idx != len(rows) - 1:
            draw.rectangle((0, y, width - 1, y), fill=BLACK)
            y += line_h
    return sheet


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ROWS_DIR.mkdir(parents=True, exist_ok=True)

    generated_rows: list[Image.Image] = []
    for idx, job in enumerate(ROWS):
        out_path = ROWS_DIR / f"{job.name}.png"
        if out_path.exists():
            image = Image.open(out_path).convert("RGBA")
            generated_rows.append(image)
            print(f"skip {job.name}")
            continue
        print(f"generate {job.name} {job.width}x{job.height}")
        try:
            image = fetch_image(job, model="zimage", seed=928000 + idx, timeout=240)
        except (HTTPError, URLError, TimeoutError, OSError, RuntimeError) as exc:
            print(f"failed {job.name}: {exc}")
            image = Image.new("RGBA", (job.width, job.height), MAGENTA)
        image.save(out_path)
        generated_rows.append(image)
        time.sleep(12)

    sheet = assemble(generated_rows)
    sheet.save(OUT_PATH)
    print(OUT_PATH)
    print(sheet.size)


if __name__ == "__main__":
    main()
