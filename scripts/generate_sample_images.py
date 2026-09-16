"""
generate_sample_images.py
--------------------------
Generates a synthetic 'scene' with distinctive shapes and textures, then
crops overlapping horizontal windows out of it to simulate a panning camera.
This avoids needing external photos or downloaded datasets to demo/test
the stitcher, and gives deterministic, reproducible input images.

Usage:
    python scripts/generate_sample_images.py --out-dir sample_images --num-images 4
"""

import argparse
from pathlib import Path

import cv2
import numpy as np


def build_scene(width: int = 1600, height: int = 500, seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    scene = np.full((height, width, 3), 235, dtype=np.uint8)

    # Background texture: faint grid lines so feature detectors have corners to find
    for x in range(0, width, 40):
        cv2.line(scene, (x, 0), (x, height), (210, 210, 210), 1)
    for y in range(0, height, 40):
        cv2.line(scene, (0, y), (width, y), (210, 210, 210), 1)

    # Scatter distinctive shapes across the scene (gives SIFT/ORB strong keypoints)
    for _ in range(35):
        shape_type = rng.integers(0, 3)
        cx, cy = rng.integers(40, width - 40), rng.integers(40, height - 40)
        color = tuple(int(c) for c in rng.integers(0, 200, size=3))
        size = int(rng.integers(15, 35))

        if shape_type == 0:
            cv2.circle(scene, (cx, cy), size, color, -1)
        elif shape_type == 1:
            cv2.rectangle(scene, (cx - size, cy - size), (cx + size, cy + size), color, -1)
        else:
            pts = np.array([
                [cx, cy - size], [cx - size, cy + size], [cx + size, cy + size]
            ])
            cv2.fillPoly(scene, [pts], color)

    return scene


def crop_overlapping_windows(scene: np.ndarray, num_images: int, overlap_frac: float = 0.4):
    height, width = scene.shape[:2]
    window_width = int(width / (1 + (num_images - 1) * (1 - overlap_frac)))
    step = int(window_width * (1 - overlap_frac))

    crops = []
    for i in range(num_images):
        x_start = min(i * step, width - window_width)
        crop = scene[:, x_start:x_start + window_width]
        crops.append(crop)
    return crops


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=Path("sample_images"))
    parser.add_argument("--num-images", type=int, default=4)
    parser.add_argument("--overlap", type=float, default=0.4,
                         help="Fractional overlap between consecutive crops (0-1).")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    scene = build_scene(seed=args.seed)
    crops = crop_overlapping_windows(scene, args.num_images, args.overlap)

    for i, crop in enumerate(crops):
        out_path = args.out_dir / f"frame_{i:02d}.jpg"
        cv2.imwrite(str(out_path), crop)
        print(f"Wrote {out_path} ({crop.shape[1]}x{crop.shape[0]})")


if __name__ == "__main__":
    main()
