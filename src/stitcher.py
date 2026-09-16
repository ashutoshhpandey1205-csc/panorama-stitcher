"""
stitcher.py
-----------
Module 3: Panorama assembly — canvas sizing, warping, and blending,
orchestrated across an arbitrary-length sequence of input images.
"""

from dataclasses import dataclass, field
from typing import List

import cv2
import numpy as np

from .feature_matching import FeatureMatcher
from .homography import estimate_homography, warp_image


@dataclass
class StitchStats:
    """Per-pair diagnostics collected while stitching, used for the report."""
    pair_index: int
    raw_match_count: int
    good_match_count: int
    inlier_count: int
    inlier_ratio: float


@dataclass
class PanoramaResult:
    """Final stitched panorama plus the stats gathered along the way."""
    image: np.ndarray
    stats: List[StitchStats] = field(default_factory=list)


def _corners(image: np.ndarray) -> np.ndarray:
    h, w = image.shape[:2]
    return np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)


def _canvas_bounds(base_image: np.ndarray, next_image: np.ndarray, H: np.ndarray):
    """Compute the bounding box (and translation) needed to fit both images."""
    base_corners = _corners(base_image)
    warped_corners = cv2.perspectiveTransform(_corners(next_image), H)
    all_corners = np.concatenate((base_corners, warped_corners), axis=0)

    x_min, y_min = np.floor(all_corners.min(axis=0).ravel()).astype(int)
    x_max, y_max = np.ceil(all_corners.max(axis=0).ravel()).astype(int)

    translation = np.array(
        [[1, 0, -x_min], [0, 1, -y_min], [0, 0, 1]], dtype=np.float64
    )
    canvas_size = (x_max - x_min, y_max - y_min)
    return translation, canvas_size


def _feather_blend(base: np.ndarray, warped: np.ndarray) -> np.ndarray:
    """
    Blend two same-size canvases using distance-transform feathering so the
    seam between overlapping regions isn't a hard edge.
    """
    base_mask = (cv2.cvtColor(base, cv2.COLOR_BGR2GRAY) > 0).astype(np.uint8)
    warped_mask = (cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY) > 0).astype(np.uint8)

    base_dist = cv2.distanceTransform(base_mask, cv2.DIST_L2, 5)
    warped_dist = cv2.distanceTransform(warped_mask, cv2.DIST_L2, 5)

    total = base_dist + warped_dist
    with np.errstate(divide="ignore", invalid="ignore"):
        alpha = np.where(total > 0, base_dist / total, 0.0)
    alpha = alpha[..., None]

    blended = base.astype(np.float32) * alpha + warped.astype(np.float32) * (1 - alpha)

    only_base = (base_mask == 1) & (warped_mask == 0)
    only_warped = (warped_mask == 1) & (base_mask == 0)
    blended[only_base] = base[only_base]
    blended[only_warped] = warped[only_warped]

    return np.clip(blended, 0, 255).astype(np.uint8)


class PanoramaStitcher:
    """Stitches a sequence of overlapping images into one panorama."""

    def __init__(
        self,
        matcher_method: str = "sift",
        ratio_thresh: float = 0.75,
        ransac_reproj_thresh: float = 4.0,
        blend_mode: str = "feather",
    ):
        self.matcher = FeatureMatcher(method=matcher_method, ratio_thresh=ratio_thresh)
        self.ransac_reproj_thresh = ransac_reproj_thresh
        if blend_mode not in ("feather", "overwrite"):
            raise ValueError("blend_mode must be 'feather' or 'overwrite'")
        self.blend_mode = blend_mode

    def _stitch_pair(self, base: np.ndarray, next_image: np.ndarray, pair_index: int):
        match_result = self.matcher.match(next_image, base)
        homography_result = estimate_homography(
            match_result, ransac_reproj_thresh=self.ransac_reproj_thresh
        )

        translation, canvas_size = _canvas_bounds(base, next_image, homography_result.matrix)
        combined_H = translation @ homography_result.matrix

        warped_next = warp_image(next_image, combined_H, canvas_size)
        warped_base = warp_image(base, translation, canvas_size)

        if self.blend_mode == "feather":
            result = _feather_blend(warped_base, warped_next)
        else:
            result = warped_base.copy()
            mask = cv2.cvtColor(warped_next, cv2.COLOR_BGR2GRAY) > 0
            result[mask] = warped_next[mask]

        stats = StitchStats(
            pair_index=pair_index,
            raw_match_count=match_result.raw_match_count,
            good_match_count=len(match_result.good_matches),
            inlier_count=homography_result.inlier_count,
            inlier_ratio=round(homography_result.inlier_ratio, 4),
        )
        return result, stats

    def stitch(self, images: List[np.ndarray]) -> PanoramaResult:
        if len(images) < 2:
            raise ValueError("Need at least 2 images to stitch a panorama.")

        panorama = images[0]
        all_stats = []
        for i in range(1, len(images)):
            panorama, stats = self._stitch_pair(panorama, images[i], pair_index=i)
            all_stats.append(stats)

        return PanoramaResult(image=panorama, stats=all_stats)
