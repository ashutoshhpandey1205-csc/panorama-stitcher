"""
metrics.py
----------
Reporting / analytics module: writes per-pair stitching diagnostics
(match counts, inlier ratios, timing) to a CSV report, satisfying the
project's 'reporting or analytics' functional requirement.
"""

import csv
import time
from contextlib import contextmanager
from pathlib import Path
from typing import List

from .stitcher import StitchStats


@contextmanager
def timer():
    """Context manager that yields a callable returning elapsed seconds."""
    start = time.perf_counter()
    result = {"elapsed": 0.0}
    try:
        yield result
    finally:
        result["elapsed"] = time.perf_counter() - start


def write_stats_csv(stats: List[StitchStats], elapsed_seconds: float, output_path: Path):
    """Write per-pair stitching stats plus total runtime to a CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "pair_index", "raw_match_count", "good_match_count",
            "inlier_count", "inlier_ratio",
        ])
        for s in stats:
            writer.writerow([
                s.pair_index, s.raw_match_count, s.good_match_count,
                s.inlier_count, s.inlier_ratio,
            ])
        writer.writerow([])
        writer.writerow(["total_stitching_time_seconds", round(elapsed_seconds, 4)])
