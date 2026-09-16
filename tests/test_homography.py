import cv2
import numpy as np
import pytest

from src.feature_matching import FeatureMatcher
from src.homography import estimate_homography


def make_textured_image(width=300, height=300, seed=0):
    rng = np.random.default_rng(seed)
    img = np.full((height, width, 3), 230, dtype=np.uint8)
    for _ in range(30):
        cx, cy = rng.integers(20, width - 20), rng.integers(20, height - 20)
        r = int(rng.integers(8, 20))
        color = tuple(int(c) for c in rng.integers(0, 200, size=3))
        cv2.circle(img, (cx, cy), r, color, -1)
    return img


class TestHomography:
    def test_raises_when_too_few_matches(self):
        matcher = FeatureMatcher(method="orb")
        img = make_textured_image(seed=5)
        result = matcher.match(img, img)
        result.good_matches = result.good_matches[:2]  # force too few
        with pytest.raises(RuntimeError):
            estimate_homography(result)

    def test_identity_like_homography_for_identical_images(self):
        matcher = FeatureMatcher(method="orb")
        img = make_textured_image(seed=6)
        match_result = matcher.match(img, img)
        homography_result = estimate_homography(match_result)

        # Matching an image against itself should yield an ~identity matrix
        H = homography_result.matrix / homography_result.matrix[2, 2]
        identity = np.eye(3)
        assert np.allclose(H, identity, atol=0.5)
        assert homography_result.inlier_ratio > 0.5

    def test_translated_image_recovers_translation(self):
        base = make_textured_image(seed=7, width=400, height=400)
        shift_x, shift_y = 30, 15
        translated = np.roll(base, shift=(shift_y, shift_x), axis=(0, 1))

        matcher = FeatureMatcher(method="orb")
        match_result = matcher.match(translated, base)
        homography_result = estimate_homography(match_result)

        H = homography_result.matrix / homography_result.matrix[2, 2]
        # H should map translated -> base, so translation terms ~ (-shift_x, -shift_y)
        assert abs(H[0, 2] - (-shift_x)) < 5
        assert abs(H[1, 2] - (-shift_y)) < 5
