"""
feature_matching.py
--------------------
Module 1: Feature detection and descriptor matching.

Covers CSE3010 Module 3 syllabus topics: keypoint detectors (SIFT/ORB),
descriptor matching, and ratio-test filtering of correspondences.
"""

from dataclasses import dataclass
from typing import List, Tuple

import cv2
import numpy as np


@dataclass
class MatchResult:
    """Container for the outcome of a feature-matching step between two images."""
    keypoints1: Tuple[cv2.KeyPoint, ...]
    keypoints2: Tuple[cv2.KeyPoint, ...]
    good_matches: List[cv2.DMatch]
    raw_match_count: int


class FeatureMatcher:
    """
    Detects keypoints/descriptors in two images and finds corresponding
    matches between them, filtered with Lowe's ratio test.
    """

    SUPPORTED_METHODS = ("sift", "orb")

    def __init__(self, method: str = "sift", ratio_thresh: float = 0.75):
        if method not in self.SUPPORTED_METHODS:
            raise ValueError(
                f"Unsupported feature method '{method}'. "
                f"Choose from {self.SUPPORTED_METHODS}."
            )
        self.method = method
        self.ratio_thresh = ratio_thresh
        self._detector = self._build_detector(method)

    @staticmethod
    def _build_detector(method: str):
        if method == "sift":
            return cv2.SIFT_create()
        return cv2.ORB_create(nfeatures=4000)

    def detect_and_compute(self, image: np.ndarray):
        """Return (keypoints, descriptors) for a grayscale or BGR image."""
        gray = image if image.ndim == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        keypoints, descriptors = self._detector.detectAndCompute(gray, None)
        if descriptors is None:
            raise RuntimeError(
                "No features detected in image. Try a higher-resolution "
                "or higher-contrast input image."
            )
        return keypoints, descriptors

    def match(self, image1: np.ndarray, image2: np.ndarray) -> MatchResult:
        """Detect features in both images and return filtered correspondences."""
        kp1, desc1 = self.detect_and_compute(image1)
        kp2, desc2 = self.detect_and_compute(image2)

        if self.method == "sift":
            norm = cv2.NORM_L2
        else:
            norm = cv2.NORM_HAMMING

        matcher = cv2.BFMatcher(norm)
        raw_matches = matcher.knnMatch(desc1, desc2, k=2)

        good_matches = []
        for pair in raw_matches:
            if len(pair) != 2:
                continue
            m, n = pair
            if m.distance < self.ratio_thresh * n.distance:
                good_matches.append(m)

        return MatchResult(
            keypoints1=tuple(kp1),
            keypoints2=tuple(kp2),
            good_matches=good_matches,
            raw_match_count=len(raw_matches),
        )

    def draw_matches(self, image1, image2, result: MatchResult, max_matches: int = 60):
        """Visualize the good matches for debugging / report screenshots."""
        return cv2.drawMatches(
            image1, result.keypoints1,
            image2, result.keypoints2,
            result.good_matches[:max_matches],
            None,
            flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
        )
