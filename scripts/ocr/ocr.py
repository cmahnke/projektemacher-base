#!/usr/bin/env python

import argparse
import logging
import os
import pathlib
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from termcolor import cprint

sys.path.append(os.path.dirname(__file__))

from ocrlib import imageio
from ocrlib.engines import ENGINES
from ocrlib.hugo import collect_content_images, collect_input_images
from ocrlib.model import Doc, Meta, Source
from ocrlib.writers import WRITERS

logging.basicConfig(stream=sys.stdout, level=os.environ.get("LOGLEVEL", "INFO").upper())
logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT = "http://127.0.0.1:18931"


def build_parser():
    parser = argparse.ArgumentParser(prog="ocr.py", description="AI OCR for Hugo content images")
    parser.add_argument("--engine", "-e", default="hunyuanocr", help=f"OCR engine, one of: {', '.join(ENGINES.names())}")
    parser.add_argument("--model", "-m", default=None, help="model identifier passed to the engine/recorded in output")
    parser.add_argument("--quant", default=None, help="model quantization, recorded in output metadata")
    parser.add_argument("--format", "-f", default="json", help=f"output format, one of: {', '.join(WRITERS.names())}")
    parser.add_argument("--endpoint", default=os.environ.get("OCR_ENDPOINT", DEFAULT_ENDPOINT), help="engine endpoint URL")
    parser.add_argument("--tasks", nargs="*", default=None, help="engine tasks (hunyuanocr: spotting_json doc_parse)")
    parser.add_argument("--max-tokens", type=int, default=8192, help="max output tokens per task")
    parser.add_argument("--timeout", type=float, default=600.0, help="request timeout in seconds")
    parser.add_argument("--max-side", type=int, default=4000, help="downscale images to this maximum side before inference")
    parser.add_argument("--content", default=None, type=pathlib.Path, help="Hugo content directory (default: ./content)")
    parser.add_argument("--input", "-i", nargs="*", type=pathlib.Path, default=None, help="explicit image files or directories (skips Hugo discovery)")
    parser.add_argument("--output-dir", "-o", type=pathlib.Path, default=None, help="write results relative to this root instead of next to each image")
    parser.add_argument("--include-ext", default="jxl,jpg,jpeg", help="comma separated image extensions to process")
    parser.add_argument("--jobs", "-j", type=int, default=1, help="parallel image workers")
    parser.add_argument("--overwrite", action="store_true", help="process images that already have output files")
    parser.add_argument("--dry-run", action="store_true", help="only list images that would be processed")
    parser.add_argument("--plugin", action="append", default=[], help="module or path registering additional engines/writers")
    return parser


def resolve_include_ext(value):
    exts = set()
    for ext in value.split(","):
        ext = ext.strip().lower()
        if not ext:
            continue
        ext = ext if ext.startswith(".") else f".{ext}"
        if ext not in imageio.IMAGE_EXTENSIONS:
            raise SystemExit(f"Unsupported extension '{ext}', supported: {', '.join(sorted(imageio.IMAGE_EXTENSIONS))}")
        exts.add(ext)
    return exts


def discover(args):
    include_ext = resolve_include_ext(args.include_ext)
    if args.input:
        return collect_input_images(args.input, include_ext)
    content_dir = args.content or Path("./content")
    if not content_dir.exists():
        raise SystemExit(f"Content directory '{content_dir}' does not exist, pass --content or --input")
    site_root = content_dir.resolve().parent
    return collect_content_images(site_root, content_dir, include_ext)


def output_path(image: Path, group_root: str, args) -> Path:
    if args.output_dir is not None:
        try:
            rel = image.relative_to(group_root)
        except ValueError:
            rel = Path(image.name)
        return args.output_dir / rel.parent / f"{image.stem}.ocr.json"
    return image.with_name(f"{image.stem}.ocr.json")


def process_image(engine, writer, image: Path, destination: Path, args) -> int:
    start = time.time()
    vips_image = imageio.load(image)
    width, height = vips_image.width, vips_image.height
    dpi = imageio.dpi(vips_image)
    payload = imageio.to_image_bytes(vips_image, max_side=args.max_side)
    result = engine.recognize(payload, width, height, dpi)
    doc = Doc(
        source=Source(file=str(image), format=imageio.image_format(image), width=width, height=height, dpi=dpi),
        meta=Meta(engine=engine.name, model=args.model or result.model, engine_version=result.engine_version,
                  quant=args.quant, tasks=args.tasks, timestamp=time.strftime("%Y-%m-%dT%H:%M:%S%z"), extra=result.extra),
        blocks=result.blocks,
        text=result.text,
    )
    writer.write(doc, destination)
    words = sum(len(line.words) for block in doc.blocks for line in block.lines)
    cprint(f"Processed '{image}' -> '{destination}' ({len(doc.blocks)} blocks, {words} words, {time.time() - start:.1f}s)", "green")
    return 0


def main(argv) -> int:
    args = build_parser().parse_args(argv)
    for plugin in args.plugin:
        WRITERS.load_plugin(plugin)
        ENGINES.load_plugin(plugin)

    engine = ENGINES.get(args.engine)
    engine_kwargs = {"endpoint": args.endpoint, "model": args.model or "default", "max_tokens": args.max_tokens, "timeout": args.timeout}
    if args.tasks:
        engine_kwargs["tasks"] = args.tasks
    engine = engine(**engine_kwargs) if isinstance(engine, type) else engine
    writer = WRITERS.get(args.format)

    groups = discover(args)
    jobs = []
    for root, images in groups:
        for image in images:
            destination = output_path(image, root, args)
            if destination.exists() and not args.overwrite:
                logger.debug(f"Skipping '{image}', output exists")
                continue
            jobs.append((image, destination))

    if not jobs:
        cprint("Nothing to do, no images without existing output found", "yellow")
        return 0
    cprint(f"Processing {len(jobs)} image(s) with engine '{engine.name}'", "blue")

    if args.dry_run:
        for image, destination in jobs:
            print(f"{image} -> {destination}")
        return 0

    failures = 0
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(process_image, engine, writer, image, destination, args): (image, destination) for image, destination in jobs}
        for future in as_completed(futures):
            image, _ = futures[future]
            try:
                future.result()
            except Exception as e:
                failures += 1
                cprint(f"Failed to process '{image}': {e}", "red")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
