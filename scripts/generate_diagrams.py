"""
generate_diagrams.py
---------------------
Generates the system architecture, workflow, and UML-style diagrams
used in the project report, as PNG files under docs/diagrams/.
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path as MplPath

OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "diagrams"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BOX_FACE = "#EAF3FB"
BOX_EDGE = "#2C5F8A"
ACCENT_FACE = "#FDEEDC"
ACCENT_EDGE = "#B5651D"
TEXT_COLOR = "#1A1A1A"


def draw_box(ax, xy, w, h, text, subtext=None, face=BOX_FACE, edge=BOX_EDGE, fontsize=11):
    box = FancyBboxPatch(
        xy, w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.4, edgecolor=edge, facecolor=face,
    )
    ax.add_patch(box)
    cx, cy = xy[0] + w / 2, xy[1] + h / 2
    if subtext:
        ax.text(cx, cy + h * 0.14, text, ha="center", va="center",
                 fontsize=fontsize, fontweight="bold", color=TEXT_COLOR)
        ax.text(cx, cy - h * 0.22, subtext, ha="center", va="center",
                 fontsize=fontsize - 2, color="#444444")
    else:
        ax.text(cx, cy, text, ha="center", va="center",
                 fontsize=fontsize, fontweight="bold", color=TEXT_COLOR)


def draw_arrow(ax, start, end, label=None, color="#333333"):
    arrow = FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=16,
        linewidth=1.3, color=color,
    )
    ax.add_patch(arrow)
    if label:
        mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
        ax.text(mx, my + 0.15, label, ha="center", va="bottom", fontsize=9, color="#333333")


def new_axis(figsize):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, figsize[0])
    ax.set_ylim(0, figsize[1])
    ax.axis("off")
    return fig, ax


def system_architecture_diagram():
    fig, ax = new_axis((10, 5))

    draw_box(ax, (0.4, 3.4), 2.0, 1.0, "Input images", "(folder of JPG/PNG)")
    draw_box(ax, (3.0, 3.4), 2.2, 1.0, "Feature Matching", "SIFT / ORB + ratio test", face=ACCENT_FACE, edge=ACCENT_EDGE)
    draw_box(ax, (5.8, 3.4), 2.2, 1.0, "Homography", "RANSAC estimation", face=ACCENT_FACE, edge=ACCENT_EDGE)
    draw_box(ax, (5.8, 1.6), 2.2, 1.0, "Stitcher", "Warp + feather blend", face=ACCENT_FACE, edge=ACCENT_EDGE)
    draw_box(ax, (3.0, 1.6), 2.2, 1.0, "Metrics", "CSV: matches, inliers, time")
    draw_box(ax, (0.4, 1.6), 2.0, 1.0, "Output", "panorama.jpg + metrics.csv")

    draw_arrow(ax, (2.4, 3.9), (3.0, 3.9))
    draw_arrow(ax, (5.2, 3.9), (5.8, 3.9))
    draw_arrow(ax, (6.9, 3.4), (6.9, 2.6))
    draw_arrow(ax, (5.8, 2.1), (5.2, 2.1))
    draw_arrow(ax, (3.0, 2.1), (2.4, 2.1))

    ax.text(5.0, 4.85, "System Architecture — Panorama Stitcher", ha="center", fontsize=14, fontweight="bold")
    ax.text(5.0, 0.9, "CLI (src/cli.py) orchestrates all modules; config/default_config.json supplies parameters",
             ha="center", fontsize=9, color="#555555")

    fig.tight_layout()
    fig.savefig(OUT_DIR / "system_architecture.png", dpi=180)
    plt.close(fig)


def workflow_diagram():
    fig, ax = new_axis((12, 3.2))

    steps = [
        ("Load images", "from --input-dir"),
        ("Detect & match\nfeatures", "per consecutive pair"),
        ("Estimate\nhomography", "RANSAC"),
        ("Warp & blend", "feather / overwrite"),
        ("Write outputs", "panorama.jpg,\nmetrics.csv"),
    ]
    x = 0.3
    w, h = 2.0, 1.4
    positions = []
    for title, sub in steps:
        draw_box(ax, (x, 0.9), w, h, title, sub, fontsize=10)
        positions.append((x, x + w))
        x += w + 0.35

    for i in range(len(positions) - 1):
        draw_arrow(ax, (positions[i][1], 1.6), (positions[i + 1][0], 1.6))

    ax.text(6.0, 2.8, "Process Workflow", ha="center", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "workflow.png", dpi=180)
    plt.close(fig)


def class_diagram():
    fig, ax = new_axis((10, 6))

    def class_box(xy, w, h, title, attrs, methods):
        x, y = xy
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.03",
                               linewidth=1.3, edgecolor=BOX_EDGE, facecolor=BOX_FACE)
        ax.add_patch(box)
        ax.plot([x, x + w], [y + h - 0.4, y + h - 0.4], color=BOX_EDGE, linewidth=1)
        divider_y = y + h - 0.4 - (len(attrs) * 0.28 + 0.15)
        ax.plot([x, x + w], [divider_y, divider_y], color=BOX_EDGE, linewidth=1)

        ax.text(x + w / 2, y + h - 0.2, title, ha="center", va="center", fontsize=11, fontweight="bold")
        for i, a in enumerate(attrs):
            ax.text(x + 0.15, y + h - 0.6 - i * 0.28, a, ha="left", va="center", fontsize=8.5)
        for i, m in enumerate(methods):
            ax.text(x + 0.15, divider_y - 0.25 - i * 0.28, m, ha="left", va="center", fontsize=8.5)

    class_box((0.3, 4.2), 2.7, 1.7, "FeatureMatcher",
               ["- method: str", "- ratio_thresh: float"],
               ["+ detect_and_compute()", "+ match()", "+ draw_matches()"])

    class_box((3.5, 4.2), 2.7, 1.7, "MatchResult",
               ["- keypoints1", "- keypoints2", "- good_matches"],
               ["(dataclass)"])

    class_box((6.7, 4.2), 2.7, 1.7, "HomographyResult",
               ["- matrix", "- inlier_mask", "- inlier_count"],
               ["+ inlier_ratio()"])

    class_box((0.3, 1.6), 2.9, 1.9, "PanoramaStitcher",
               ["- matcher: FeatureMatcher", "- blend_mode: str"],
               ["+ stitch(images)", "- _stitch_pair()"])

    class_box((3.6, 1.6), 2.9, 1.9, "StitchStats",
               ["- pair_index", "- good_match_count", "- inlier_ratio"],
               ["(dataclass)"])

    class_box((6.9, 1.6), 2.7, 1.9, "PanoramaResult",
               ["- image: ndarray", "- stats: List[StitchStats]"],
               ["(dataclass)"])

    draw_arrow(ax, (3.0, 5.0), (3.5, 5.0), "uses")
    draw_arrow(ax, (6.2, 5.0), (6.7, 5.0), "produces")
    draw_arrow(ax, (1.7, 4.2), (1.7, 3.5), "uses")
    draw_arrow(ax, (3.2, 2.5), (3.6, 2.5), "produces")
    draw_arrow(ax, (6.5, 2.5), (6.9, 2.5), "aggregates into")

    ax.text(5.0, 5.95, "Class / Component Diagram", ha="center", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "class_diagram.png", dpi=180)
    plt.close(fig)


def use_case_diagram():
    fig, ax = new_axis((8, 5.6))

    # Actor (stick figure, simplified)
    ax_cx, ax_cy = 1.0, 2.5
    ax.add_patch(plt.Circle((ax_cx, ax_cy + 1.0), 0.25, fill=False, linewidth=1.5, edgecolor="#1A1A1A"))
    ax.plot([ax_cx, ax_cx], [ax_cy + 0.75, ax_cy + 0.1], color="#1A1A1A", linewidth=1.5)
    ax.plot([ax_cx - 0.35, ax_cx + 0.35], [ax_cy + 0.55, ax_cy + 0.55], color="#1A1A1A", linewidth=1.5)
    ax.plot([ax_cx, ax_cx - 0.3], [ax_cy + 0.1, ax_cy - 0.3], color="#1A1A1A", linewidth=1.5)
    ax.plot([ax_cx, ax_cx + 0.3], [ax_cy + 0.1, ax_cy - 0.3], color="#1A1A1A", linewidth=1.5)
    ax.text(ax_cx, ax_cy - 0.55, "User", ha="center", fontsize=10, fontweight="bold")

    use_cases = [
        ("Provide overlapping\nimages", 5.0),
        ("Run stitching\npipeline (CLI)", 4.0),
        ("View stitched\npanorama", 3.0),
        ("Review match/inlier\nmetrics (CSV)", 2.0),
        ("Configure matcher\n& blend mode", 1.0),
    ]
    for text, y in use_cases:
        ellipse = plt.matplotlib.patches.Ellipse((5.2, y), 3.2, 0.75, facecolor=ACCENT_FACE, edgecolor=ACCENT_EDGE, linewidth=1.3)
        ax.add_patch(ellipse)
        ax.text(5.2, y, text, ha="center", va="center", fontsize=9)
        draw_arrow(ax, (1.35, ax_cy), (3.6, y))

    ax.text(4.0, 5.85, "Use Case Diagram", ha="center", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "use_case_diagram.png", dpi=180)
    plt.close(fig)


def sequence_diagram():
    fig, ax = new_axis((10, 6))

    actors = ["User", "CLI", "PanoramaStitcher", "FeatureMatcher", "Homography"]
    xs = [0.8, 2.6, 4.8, 7.0, 9.0]
    for actor, x in zip(actors, xs):
        draw_box(ax, (x - 0.7, 5.2), 1.4, 0.5, actor, fontsize=9)
        ax.plot([x, x], [0.3, 5.2], linestyle="--", color="#999999", linewidth=1)

    messages = [
        (0, 1, 4.7, "run CLI command"),
        (1, 2, 4.2, "stitch(images)"),
        (2, 3, 3.7, "match(img_i, img_j)"),
        (3, 2, 3.3, "MatchResult"),
        (2, 4, 2.8, "estimate_homography()"),
        (4, 2, 2.4, "HomographyResult"),
        (2, 2, 1.9, "warp + feather blend"),
        (2, 1, 1.4, "PanoramaResult"),
        (1, 0, 1.0, "panorama.jpg + metrics.csv"),
    ]
    for src, dst, y, label in messages:
        if src == dst:
            ax.annotate("", xy=(xs[src] + 0.5, y - 0.15), xytext=(xs[src], y),
                        arrowprops=dict(arrowstyle="-|>", color="#333333", linewidth=1.2))
            ax.text(xs[src] + 0.55, y - 0.08, label, fontsize=8, va="center")
        else:
            draw_arrow(ax, (xs[src], y), (xs[dst], y), label)

    ax.text(5.0, 5.95, "Sequence Diagram — Stitching a Pair of Images", ha="center", fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "sequence_diagram.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    system_architecture_diagram()
    workflow_diagram()
    class_diagram()
    use_case_diagram()
    sequence_diagram()
    print("Diagrams written to", OUT_DIR)
