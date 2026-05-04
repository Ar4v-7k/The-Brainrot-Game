from __future__ import annotations

import argparse
import io
import re
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROMPT_FILE = Path("/Users/aravsharma/Downloads/brainrotmon_tileset_prompts_cleaned.txt")
DEFAULT_OUT_DIR = ROOT / "assets" / "source_sheets" / "pollinations_flux_schnell"


@dataclass(frozen=True)
class Job:
    key: str
    title: str
    prompt: str
    width: int
    height: int


SECTION_PATTERN = re.compile(r"(?m)^## (BATCH [1-5]) — ([^\n]+)\n")
SUBSECTION_PATTERN = re.compile(r"(?m)^### (BATCH 6[A-F]) — ([^\n]+)\n")


SIZES = {
    "batch_1": (1024, 1024),
    "batch_2": (1024, 1024),
    "batch_3": (1024, 1024),
    "batch_4": (1024, 1024),
    "batch_5": (1024, 1024),
    "batch_6a": (144, 192),
    "batch_6b": (576, 192),
    "batch_6c": (640, 128),
    "batch_6d": (960, 320),
    "batch_6e": (960, 320),
    "batch_6f": (512, 512),
}


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def parse_jobs(text: str) -> list[Job]:
    jobs: list[Job] = []
    batch_matches = list(SECTION_PATTERN.finditer(text))
    first_subsection = SUBSECTION_PATTERN.search(text)
    batch_end_limit = first_subsection.start() if first_subsection else len(text)
    for idx, match in enumerate(batch_matches):
        start = match.end()
        next_start = batch_matches[idx + 1].start() if idx + 1 < len(batch_matches) else batch_end_limit
        key = slug(match.group(1))
        width, height = SIZES[key]
        prompt = text[start:next_start].strip()
        jobs.append(Job(key, match.group(2).strip(), prompt, width, height))

    sub_matches = list(SUBSECTION_PATTERN.finditer(text))
    process_marker = text.find("# HOW TO PROCESS EACH BATCH")
    sub_end_limit = process_marker if process_marker != -1 else len(text)
    for idx, match in enumerate(sub_matches):
        start = match.end()
        next_start = sub_matches[idx + 1].start() if idx + 1 < len(sub_matches) else sub_end_limit
        key = slug(match.group(1))
        width, height = SIZES[key]
        prompt = text[start:next_start].strip()
        jobs.append(Job(key, match.group(2).strip(), prompt, width, height))
    return jobs


def generate_image(job: Job, out_dir: Path, model: str, seed: int, enhance: bool, private: bool, timeout: int) -> Path:
    params = {
        "width": str(job.width),
        "height": str(job.height),
        "model": model,
        "seed": str(seed),
        "enhance": str(enhance).lower(),
        "private": str(private).lower(),
        "nologo": "true",
        "safe": "true",
    }
    url = f"https://image.pollinations.ai/prompt/{quote(job.prompt)}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": "brainrotmon-asset-generator/1.0"})
    with urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        data = response.read()
    if not data or not content_type.startswith("image/"):
        raise RuntimeError(f"Pollinations returned {content_type or 'empty response'} for {job.key}")
    out_path = out_dir / f"{job.key}_{job.width}x{job.height}_seed{seed}.png"
    image = Image.open(io.BytesIO(data)).convert("RGBA")
    if image.size != (job.width, job.height):
        image = image.resize((job.width, job.height), Image.Resampling.LANCZOS)
    image.save(out_path)
    (out_dir / f"{job.key}_prompt.txt").write_text(job.prompt)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Brainrotmon tileset prompt batches through Pollinations image API.")
    parser.add_argument("--prompt-file", type=Path, default=DEFAULT_PROMPT_FILE)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--model", default="flux", help="Pollinations image model. Defaults to flux for Flux Schnell-style output.")
    parser.add_argument("--seed", type=int, default=7072026)
    parser.add_argument("--delay", type=float, default=16.0, help="Delay between requests; anonymous Pollinations limit is about 15s.")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--only", nargs="*", help="Optional job keys, e.g. batch_1 batch_6a")
    parser.add_argument("--list", action="store_true", help="List parsed jobs without generating.")
    parser.add_argument("--enhance", action="store_true")
    parser.add_argument("--public", action="store_true", help="Do not set private=true.")
    args = parser.parse_args()

    text = args.prompt_file.read_text()
    jobs = parse_jobs(text)
    if args.only:
        requested = set(args.only)
        jobs = [job for job in jobs if job.key in requested]
    if args.list:
        for job in jobs:
            print(f"{job.key}: {job.width}x{job.height} {job.title}")
        return
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for idx, job in enumerate(jobs):
        if idx:
            time.sleep(args.delay)
        seed = args.seed + idx
        print(f"Generating {job.key} ({job.width}x{job.height}) with model={args.model} seed={seed}")
        try:
            out_path = generate_image(
                job,
                args.out_dir,
                model=args.model,
                seed=seed,
                enhance=args.enhance,
                private=not args.public,
                timeout=args.timeout,
            )
        except (HTTPError, URLError, TimeoutError, ConnectionError, OSError, RuntimeError) as exc:
            print(f"FAILED {job.key}: {exc}")
            continue
        print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
