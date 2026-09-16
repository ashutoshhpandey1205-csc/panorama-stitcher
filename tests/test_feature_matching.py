import numpy as np
import pytest

from src.feature_matching import FeatureMatcher


def make_textured_image(width=300, height=300, seed=0):
    rng = np.random.default_rng(seed)
    img = np.full((height, width, 3), 230, dtype=np.uint8)
    for _ in range(25):
        cx, cy = rng.integers(20, width - 20), rng.integers(20, height - 20)
        r = int(rng.integers(8, 20))
        color = tuple(int(c) for c in rng.integers(0, 200, size=3))
        img = img.copy()
        import cv2
        cv2.circle(img, (cx, cy), r, color, -1)
    return img


class TestFeatureMatcher:
    def test_rejects_unsupported_method(self):
        with pytest.raises(ValueError):
            FeatureMatcher(method="not-a-real-method")

    def test_detect_and_compute_finds_keypoints(self):
        matcher = FeatureMatcher(method="orb")
        img = make_textured_image(seed=1)
        keypoints, descriptors = matcher.detect_and_compute(img)
        assert len(keypoints) > 0
        assert descriptors is not None

    def test_match_same_image_gives_many_good_matches(self):
        matcher = FeatureMatcher(method="orb")
        img = make_textured_image(seed=2)
        result = matcher.match(img, img)
        # Matching an image against itself should find plenty of confident matches
        assert len(result.good_matches) > 10

    def test_match_returns_fewer_good_than_raw(self):
        matcher = FeatureMatcher(method="orb", ratio_thresh=0.5)
        img1 = make_textured_image(seed=3)
        img2 = make_textured_image(seed=4)
        result = matcher.match(img1, img2)
        assert len(result.good_matches) <= result.raw_match_count
