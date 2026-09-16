# Panorama Stitcher

A command-line tool that stitches a folder of overlapping images into a single panoramic photo, built for the CSE3010 Computer Vision course project (VIT Bhopal).

It implements the full classical stitching pipeline from scratch on top of OpenCV's primitives — feature detection, descriptor matching, RANSAC homography estimation, and seam blending — rather than calling `cv2.Stitcher` directly.

## Overview

Given a set of photos taken by panning a camera across a scene (with ~30-50% overlap between consecutive shots), the tool:

1. Detects and matches keypoints between consecutive images (SIFT or ORB).
2. Estimates a robust homography between each pair using RANSAC.
3. Warps and feather-blends the images onto a shared canvas to produce one seamless panorama.
4. Logs match counts, inlier ratios, and timing for every stitched pair.

## Features

- Two selectable feature detectors: **SIFT** (default, more accurate) or **ORB** (faster, patent-free).
- RANSAC-based homography estimation with configurable reprojection threshold.
- Two blend modes: **feather** (distance-transform blending, smooth seams) or **overwrite** (fast, hard seams).
- Sequential multi-image stitching — works with 2 or more images, not just pairs.
- Per-pair diagnostics (raw matches, good matches, inliers, inlier ratio) exported to CSV.
- Fully configurable via a JSON config file or CLI flags.
- Synthetic sample-image generator, so the tool can be tested and demoed without any external dataset or internet access.
- Automated unit tests (11 tests) covering feature matching, homography estimation, and full-pipeline stitching.

## Technologies / Tools Used

- Python 3.10+
- OpenCV (`opencv-contrib-python`) — SIFT/ORB, RANSAC homography, warping
- NumPy
- pytest (testing)
- argparse (CLI)

## Project Structure

```
panorama-stitcher/
├── README.md
├── statement.md
├── requirements.txt
├── config/
│   └── default_config.json      # default matcher/blend/threshold settings
├── src/
│   ├── feature_matching.py      # Module 1: keypoint detection + matching
│   ├── homography.py            # Module 2: RANSAC homography + warping
│   ├── stitcher.py              # Module 3: canvas sizing + blending + orchestration
│   ├── metrics.py               # reporting: CSV of match/inlier stats + timing
│   └── cli.py                   # command-line entry point
├── scripts/
│   └── generate_sample_images.py  # generates synthetic overlapping test images
├── sample_images/                 # generated demo input images
├── tests/                         # pytest unit tests (11 tests)
├── docs/                          # architecture, workflow, and UML diagrams
└── outputs/                       # panorama + metrics written here at runtime
```

## Setup Instructions

### 1. Prerequisites

- Python 3.10 or later
- pip

### 2. Clone the repository

```bash
git clone https://github.com/<github-username>/panorama-stitcher.git
cd panorama-stitcher
```

### 3. Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Project

### Step 1 — Generate sample input images (optional, if you don't have your own photos)

```bash
python scripts/generate_sample_images.py --out-dir sample_images --num-images 4 --overlap 0.4
```

This creates 4 synthetic overlapping frames in `sample_images/` — no external dataset or internet access needed. If you'd rather use your own photos, just place 2 or more overlapping images (JPG/PNG) into a folder and point `--input-dir` at it (see below). Consecutive photos should overlap by roughly 30-50% and be taken with minimal parallax (rotate the camera around a fixed point rather than walking sideways).

### Step 2 — Run the stitcher

```bash
python -m src.cli --input-dir sample_images --output outputs/panorama.jpg --metrics-csv outputs/metrics.csv
```

This will:
- Load every image in `sample_images/` (sorted by filename),
- Stitch them sequentially into one panorama,
- Write the result to `outputs/panorama.jpg`,
- Write per-pair matching/inlier statistics to `outputs/metrics.csv`.

### CLI Options

| Flag | Description | Default |
|---|---|---|
| `--input-dir` | Folder of overlapping input images (required) | — |
| `--output` | Path to write the stitched panorama (required) | — |
| `--matcher` | `sift` or `orb` | `sift` (from config) |
| `--blend-mode` | `feather` or `overwrite` | `feather` (from config) |
| `--config` | Path to a JSON config file | `config/default_config.json` |
| `--metrics-csv` | Optional path to write per-pair stats as CSV | none |
| `--verbose` | Enable debug-level logging | off |

Example using ORB instead of SIFT, with a custom blend mode:

```bash
python -m src.cli --input-dir my_photos --output outputs/result.jpg --matcher orb --blend-mode overwrite
```

## Instructions for Testing

Run the full automated test suite (11 tests covering feature matching, homography estimation, and end-to-end stitching):

```bash
pytest tests/ -v
```

All tests use either synthetically generated in-memory images or the images in `sample_images/` — no manual setup required.

## Configuration

Default parameters live in `config/default_config.json`:

```json
{
  "matcher": "sift",
  "blend_mode": "feather",
  "ratio_thresh": 0.75,
  "ransac_reproj_thresh": 4.0
}
```

Any of these can be overridden per-run via CLI flags (matcher, blend-mode) or by editing/duplicating this file and passing `--config <path>`.

## Screenshots

See `docs/screenshots/` for example output: the stitched panorama, and a feature-match visualization showing correspondences found between two overlapping frames.

## Notes on Input Images

- Works best with photos that share consistent exposure/lighting and overlap by 30-50%.
- Photos should be taken by rotating the camera around a fixed point (or from far enough away that parallax is negligible) — pure translation between wildly different viewpoints will reduce match quality.
- If stitching fails with "Not enough good matches," try images with more overlap, better lighting/texture, or switch `--matcher` from `orb` to `sift`.
