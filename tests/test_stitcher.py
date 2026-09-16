from pathlib import Path

import cv2
import pytest

from src.stitcher import PanoramaStitcher

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_images"


def load_sample_images():
    paths = sorted(SAMPLE_DIR.glob("frame_*.jpg"))
    return [cv2.imread(str(p)) for p in paths]


@pytest.mark.skipif(not SAMPLE_DIR.exists(), reason="sample_images/ not generated yet")
class TestPanoramaStitcher:
    def test_stitch_requires_at_least_two_images(self):
        stitcher = PanoramaStitcher()
        images = load_sample_images()
        with pytest.raises(ValueError):
            stitcher.stitch(images[:1])

    def test_stitch_two_sample_frames_produces_wider_output(self):
        stitcher = PanoramaStitcher(matcher_method="sift", blend_mode="feather")
        images = load_sample_images()
        assert len(images) >= 2

        result = stitcher.stitch(images[:2])
        assert result.image.shape[1] > images[0].shape[1]
        assert len(result.stats) == 1
        assert result.stats[0].inlier_ratio > 0.5

    def test_stitch_all_sample_frames_chains_correctly(self):
        stitcher = PanoramaStitcher(matcher_method="sift", blend_mode="feather")
        images = load_sample_images()

        result = stitcher.stitch(images)
        assert len(result.stats) == len(images) - 1
        # Panorama should be noticeably wider than any single input frame
        assert result.image.shape[1] > max(im.shape[1] for im in images)

    def test_overwrite_blend_mode_runs_without_error(self):
        stitcher = PanoramaStitcher(matcher_method="orb", blend_mode="overwrite")
        images = load_sample_images()[:2]
        result = stitcher.stitch(images)
        assert result.image is not None
