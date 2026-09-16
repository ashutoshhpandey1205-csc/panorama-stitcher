"""
cli.py
------
Command-line entry point. Fully runnable from a terminal, no GUI required.

Example:
    python -m src.cli --input-dir sample_images --output outputs/panorama.jpg
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import cv2

from .metrics import timer, write_stats_csv
from .stitcher import PanoramaStitcher

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "default_config.json"


def load_config(config_path: Path) -> dict:
    with open(config_path) as f:
        return json.load(f)


def load_images(input_dir: Path, logger: logging.Logger):
    """Load all images from a directory, sorted by filename for deterministic order."""
    valid_ext = {".jpg", ".jpeg", ".png", ".bmp"}
    paths = sorted(p for p in input_dir.iterdir() if p.suffix.lower() in valid_ext)

    if len(paths) < 2:
        raise ValueError(
            f"Found only {len(paths)} image(s) in '{input_dir}'. "
            "Need at least 2 overlapping images to build a panorama."
        )

    images = []
    for p in paths:
        img = cv2.imread(str(p))
        if img is None:
            logger.warning("Skipping unreadable file: %s", p)
            continue
        images.append(img)

    logger.info("Loaded %d image(s) from %s", len(images), input_dir)
    return images


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Stitch a folder of overlapping images into a single panorama."
    )
    parser.add_argument(
        "--input-dir", required=True, type=Path,
        help="Directory containing the overlapping input images (processed in filename order).",
    )
    parser.add_argument(
        "--output", required=True, type=Path,
        help="Path to write the stitched panorama image to (e.g. outputs/panorama.jpg).",
    )
    parser.add_argument(
        "--matcher", choices=["sift", "orb"], default=None,
        help="Feature detector/descriptor to use. Overrides the config file default.",
    )
    parser.add_argument(
        "--blend-mode", choices=["feather", "overwrite"], default=None,
        help="Blending strategy for overlapping regions. Overrides the config file default.",
    )
    parser.add_argument(
        "--config", type=Path, default=DEFAULT_CONFIG_PATH,
        help="Path to a JSON config file (default: config/default_config.json).",
    )
    parser.add_argument(
        "--metrics-csv", type=Path, default=None,
        help="Optional path to write per-pair stitching metrics as CSV.",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable debug-level logging.",
    )
    return parser


def main(argv=None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="[%(levelname)s] %(message)s",
    )
    logger = logging.getLogger("panorama_stitcher")

    try:
        config = load_config(args.config)
    except FileNotFoundError:
        logger.error("Config file not found: %s", args.config)
        return 1

    matcher_method = args.matcher or config.get("matcher", "sift")
    blend_mode = args.blend_mode or config.get("blend_mode", "feather")
    ratio_thresh = config.get("ratio_thresh", 0.75)
    ransac_thresh = config.get("ransac_reproj_thresh", 4.0)

    try:
        images = load_images(args.input_dir, logger)
    except ValueError as e:
        logger.error(str(e))
        return 1

    stitcher = PanoramaStitcher(
        matcher_method=matcher_method,
        ratio_thresh=ratio_thresh,
        ransac_reproj_thresh=ransac_thresh,
        blend_mode=blend_mode,
    )

    logger.info(
        "Stitching %d images (matcher=%s, blend=%s)...",
        len(images), matcher_method, blend_mode,
    )

    try:
        with timer() as t:
            result = stitcher.stitch(images)
    except (RuntimeError, ValueError) as e:
        logger.error("Stitching failed: %s", e)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.output), result.image)
    logger.info("Panorama written to %s", args.output)

    for s in result.stats:
        logger.info(
            "Pair %d: %d good matches, %d inliers (%.1f%% inlier ratio)",
            s.pair_index, s.good_match_count, s.inlier_count, s.inlier_ratio * 100,
        )
    logger.info("Total stitching time: %.2fs", t["elapsed"])

    if args.metrics_csv:
        write_stats_csv(result.stats, t["elapsed"], args.metrics_csv)
        logger.info("Metrics written to %s", args.metrics_csv)

    return 0


if __name__ == "__main__":
    sys.exit(main())
