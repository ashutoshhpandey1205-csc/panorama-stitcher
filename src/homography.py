"""
homography.py
--------------
Module 2: Homography estimation via RANSAC and image warping.

Covers CSE3010 Module 2 syllabus topics: homography, RANSAC, and
projective transformation between two camera views of the same scene.
"""

from dataclasses import dataclass

import cv2
import numpy as np

from .feature_matching import MatchResult


@dataclass
class HomographyResult:
    """Container for a RANSAC-estimated homography and its diagnostics."""
    matrix: np.ndarray
    inlier_mask: np.ndarray
    inlier_count: int
    total_matches: int

    @property
    def inlier_ratio(self) -> float:
        if self.total_matches == 0:
            return 0.0
        return self.inlier_count / self.total_matches


MIN_MATCH_COUNT = 4  # a homography needs at least 4 point correspondences


def estimate_homography(
    match_result: MatchResult,
    ransac_reproj_thresh: float = 4.0,
) -> HomographyResult:
    """
    Estimate the homography mapping points in image1 to image2 using the
    good matches found by FeatureMatcher, robustly fit with RANSAC.
    """
    if len(match_result.good_matches) < MIN_MATCH_COUNT:
        raise RuntimeError(
            f"Not enough good matches to compute a homography "
            f"({len(match_result.good_matches)} found, need >= {MIN_MATCH_COUNT}). "
            "Try images with more overlap or a lower ratio threshold."
        )

    src_pts = np.float32(
        [match_result.keypoints1[m.queryIdx].pt for m in match_result.good_matches]
    ).reshape(-1, 1, 2)
    dst_pts = np.float32(
        [match_result.keypoints2[m.trainIdx].pt for m in match_result.good_matches]
    ).reshape(-1, 1, 2)

    H, mask = cv2.findHomography(
        src_pts, dst_pts, cv2.RANSAC, ransac_reproj_thresh
    )

    if H is None:
        raise RuntimeError("Homography estimation failed (RANSAC found no consensus).")

    mask = mask.ravel().astype(bool)
    return HomographyResult(
        matrix=H,
        inlier_mask=mask,
        inlier_count=int(mask.sum()),
        total_matches=len(match_result.good_matches),
    )


def warp_image(image: np.ndarray, H: np.ndarray, output_shape) -> np.ndarray:
    """Warp `image` into the target canvas size using homography H."""
    width, height = output_shape
    return cv2.warpPerspective(image, H, (width, height))
