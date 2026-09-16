# Problem Statement

## Problem Statement

Manually combining multiple overlapping photographs of a wide scene into a single seamless image is tedious and error-prone to do by hand — aligning edges, correcting perspective distortion, and blending exposure differences all require precise geometric computation. This project builds an automated panorama stitcher that takes a folder of overlapping photographs and produces a single combined image, using classical computer vision techniques for feature matching and geometric alignment (Modules 2 and 3 of the CSE3010 syllabus: feature extraction, homography estimation, and RANSAC).

## Scope of the Project

- Accepts 2 or more overlapping images of the same scene as input.
- Detects and matches distinctive keypoints between consecutive images (SIFT or ORB).
- Estimates the geometric transformation (homography) between each pair of images using RANSAC, discarding incorrect matches.
- Warps and blends the images onto a common canvas to produce one seamless panorama.
- Reports quantitative diagnostics (match counts, inlier ratios, runtime) for every stitched pair.
- Runs entirely from the command line, with no GUI dependency.
- Out of scope: real-time/video stitching, cylindrical or spherical projection for 360° panoramas, and exposure/color correction beyond basic seam blending.

## Target Users

- Students and instructors evaluating classical computer vision pipelines.
- Anyone wanting to combine a handful of overlapping photos (e.g. a wide landscape or a large document/whiteboard) into one image without commercial photo-editing software.

## High-Level Features

1. **Feature detection & matching** — SIFT/ORB keypoint detection with ratio-test filtered matching between overlapping images.
2. **Homography estimation** — RANSAC-based robust geometric alignment between each image pair.
3. **Stitching & blending** — canvas construction, perspective warping, and distance-transform feather blending to produce one seamless panorama, with a CSV report of matching/alignment quality for every pair.
