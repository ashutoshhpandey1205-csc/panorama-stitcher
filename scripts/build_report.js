const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, ImageRun,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  AlignmentType, PageBreak, LevelFormat, convertInchesToTwip,
} = require("docx");

const ROOT = path.resolve(__dirname, "..");
const DIAG = path.join(ROOT, "docs", "diagrams");
const SHOT = path.join(ROOT, "docs", "screenshots");

function img(file, widthPx, dir = DIAG) {
  const data = fs.readFileSync(path.join(dir, file));
  const scale = widthPx / (file.includes("workflow") ? 2160 :
                            file.includes("panorama_output") || file.includes("feature_matches") ? 1 : 1800);
  return data;
}

function imageParagraph(dir, file, origW, origH, targetW) {
  const data = fs.readFileSync(path.join(dir, file));
  const targetH = Math.round(origH * (targetW / origW));
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
    children: [
      new ImageRun({ data, transformation: { width: targetW, height: targetH }, type: file.endsWith(".png") ? "png" : "jpg" }),
    ],
  });
}

function h1(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 150 } });
}
function h2(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 } });
}
function p(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 120 } });
}
function bullet(text) {
  return new Paragraph({ text, bullet: { level: 0 }, spacing: { after: 60 } });
}
function caption(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 240 },
    children: [new TextRun({ text, italics: true, size: 20, color: "555555" })],
  });
}

function simpleTable(headerRow, rows) {
  const colCount = headerRow.length;
  const colWidth = Math.floor(9000 / colCount);
  const mkCell = (text, isHeader) => new TableCell({
    width: { size: colWidth, type: WidthType.DXA },
    shading: isHeader ? { type: ShadingType.CLEAR, fill: "D9E2F3" } : undefined,
    children: [new Paragraph({ children: [new TextRun({ text, bold: isHeader })] })],
  });
  return new Table({
    width: { size: 9000, type: WidthType.DXA },
    columnWidths: Array(colCount).fill(colWidth),
    rows: [
      new TableRow({ children: headerRow.map((t) => mkCell(t, true)) }),
      ...rows.map((r) => new TableRow({ children: r.map((t) => mkCell(t, false)) })),
    ],
  });
}

const children = [];

// ---------- COVER PAGE ----------
children.push(
  new Paragraph({ text: "", spacing: { before: 2000 } }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Panorama Stitcher", bold: true, size: 56 })],
    spacing: { after: 200 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "A Feature-Matching and Homography-Based Image Stitching Pipeline", size: 28 })],
    spacing: { after: 600 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Course Project Report", size: 24, bold: true })],
    spacing: { after: 100 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "CSE3010 — Computer Vision", size: 24 })],
    spacing: { after: 100 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "VIT Bhopal University", size: 22 })],
    spacing: { after: 800 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Submitted by: [Your Name]", size: 22 })],
    spacing: { after: 60 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Registration Number: [Your Reg. No.]", size: 22 })],
    spacing: { after: 60 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Program: B.Tech, Artificial Intelligence & Machine Learning", size: 22 })],
    spacing: { after: 60 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Submission Date: [DD Month YYYY]", size: 22 })],
    spacing: { after: 60 },
  }),
  new Paragraph({ children: [new PageBreak()] }),
);

// ---------- 1. INTRODUCTION ----------
children.push(h1("1. Introduction"));
children.push(p(
  "Combining multiple overlapping photographs of a wide scene into one seamless panoramic image is a classic and well-studied problem in computer vision. It brings together several core topics from this course: local feature detection and description, robust geometric estimation, and image warping/blending. This project implements a complete, from-scratch panorama stitching pipeline in Python using OpenCV's low-level primitives (rather than its built-in high-level Stitcher class), so that every stage of the pipeline — feature matching, homography estimation, and blending — is explicit, inspectable, and directly traceable back to the syllabus concepts it demonstrates."
));
children.push(p(
  "The tool is fully driven from the command line, accepts any folder of overlapping images as input, and reports quantitative diagnostics (match counts, RANSAC inlier ratios, and runtime) for every image pair it stitches, in addition to producing the final panorama image."
));

// ---------- 2. PROBLEM STATEMENT ----------
children.push(h1("2. Problem Statement"));
children.push(p(
  "Manually aligning and blending overlapping photographs is tedious and imprecise when done by hand — it requires accurately identifying corresponding points between images, computing the geometric transformation that relates them, and seamlessly merging the overlapping regions without visible ghosting or seams. This project automates that entire process: given a folder of overlapping images captured by panning a camera across a scene, the system detects corresponding features between consecutive images, robustly estimates the geometric transformation (homography) relating them using RANSAC, and warps and blends the images onto a single shared canvas to produce one seamless panorama."
));

// ---------- 3. FUNCTIONAL REQUIREMENTS ----------
children.push(h1("3. Functional Requirements"));
children.push(p("The system implements three major functional modules, each with a clear input/output contract:"));
children.push(simpleTable(
  ["Module", "Input", "Output"],
  [
    ["1. Feature Matching (src/feature_matching.py)", "Two images (grayscale or BGR)", "Filtered list of corresponding keypoint pairs (good matches)"],
    ["2. Homography Estimation (src/homography.py)", "Matched keypoint pairs", "3x3 homography matrix, RANSAC inlier mask, inlier ratio"],
    ["3. Stitching & Blending (src/stitcher.py)", "Sequence of 2+ images", "Single blended panorama image + per-pair statistics"],
  ]
));
children.push(new Paragraph({ text: "", spacing: { after: 150 } }));
children.push(p("Additional functional capabilities:", { bold: true }));
children.push(bullet("Reporting/analytics module (src/metrics.py) exports per-pair match counts, inlier ratios, and total runtime to a CSV file."));
children.push(bullet("Configurable pipeline via a JSON config file (config/default_config.json) or CLI flags — feature detector (SIFT/ORB), blend mode (feather/overwrite), ratio-test threshold, and RANSAC reprojection threshold."));
children.push(bullet("Synthetic sample-image generator (scripts/generate_sample_images.py) so the tool is testable and demonstrable without any external dataset."));
children.push(bullet("Logical workflow: the CLI (src/cli.py) loads images from a directory in filename order, orchestrates the three modules sequentially across the whole set, and writes the final panorama and metrics to disk."));

// ---------- 4. NON-FUNCTIONAL REQUIREMENTS ----------
children.push(h1("4. Non-Functional Requirements"));
children.push(simpleTable(
  ["Requirement", "How it is addressed"],
  [
    ["Performance", "Stitches 4 images (SIFT, feather blending) in well under 1 second on a standard CPU; ORB is offered as a faster alternative for larger image sets."],
    ["Reliability", "Automated pytest suite (11 tests) validates feature matching, homography accuracy on known transformations, and end-to-end stitching correctness."],
    ["Usability", "Single CLI entry point with clear flags, sensible defaults via a config file, and descriptive log messages at each pipeline stage."],
    ["Error handling", "Explicit, descriptive exceptions for: too few images supplied, unreadable image files, insufficient feature matches, and RANSAC failing to find a consensus homography — each with an actionable message."],
    ["Maintainability", "Pipeline is split into independent, single-responsibility modules (matching, homography, stitching, metrics, CLI) connected by typed dataclasses, so any stage can be modified or replaced without touching the others."],
    ["Logging/monitoring", "Structured logging (Python logging module) reports per-pair match/inlier statistics and total runtime on every run; --verbose enables debug-level output."],
  ]
));

// ---------- 5. SYSTEM ARCHITECTURE ----------
children.push(h1("5. System Architecture"));
children.push(p(
  "The pipeline is organized as a linear sequence of independent stages, orchestrated by the CLI layer. Images flow from disk, through feature matching and homography estimation, into the stitcher, and back out to disk as a panorama plus a metrics report."
));
// System architecture
children.push(imageParagraph(DIAG, "system_architecture.png", 1800, 900, 580));
children.push(caption("Figure 1: System architecture of the panorama stitching pipeline."));

// ---------- 6. DESIGN DIAGRAMS ----------
children.push(h1("6. Design Diagrams"));

children.push(h2("6.1 Use Case Diagram"));
children.push(imageParagraph(DIAG, "use_case_diagram.png", 1440, 1007, 480));
children.push(caption("Figure 2: Use case diagram showing how a user interacts with the system."));

children.push(h2("6.2 Workflow Diagram"));
children.push(imageParagraph(DIAG, "workflow.png", 2160, 576, 580));
children.push(caption("Figure 3: End-to-end process workflow, from loading images to writing outputs."));

children.push(h2("6.3 Sequence Diagram"));
children.push(imageParagraph(DIAG, "sequence_diagram.png", 1800, 1080, 560));
children.push(caption("Figure 4: Sequence diagram for stitching a single pair of images."));

children.push(h2("6.4 Class / Component Diagram"));
children.push(imageParagraph(DIAG, "class_diagram.png", 1800, 1080, 560));
children.push(caption("Figure 5: Class/component diagram showing the core classes and their relationships."));

children.push(h2("6.5 Database / Storage Design"));
children.push(p(
  "Not applicable. This project is a stateless image-processing pipeline — it reads image files from an input directory and writes an output image plus a CSV metrics file; no persistent database or schema is used."
));

// ---------- 7. DESIGN DECISIONS & RATIONALE ----------
children.push(h1("7. Design Decisions & Rationale"));
children.push(bullet("Manual pipeline over cv2.Stitcher: OpenCV ships a high-level Stitcher class that hides the entire pipeline behind one function call. Implementing feature matching, homography estimation, and blending manually was chosen instead so each syllabus concept (SIFT/ORB, RANSAC, homography, warping) is explicit, testable, and gradable as a distinct module, rather than a single opaque call."));
children.push(bullet("SIFT as the default detector, ORB as an alternative: SIFT gives more reliable matches on textured/synthetic scenes and is patent-free since 2020, making it the safer default; ORB is exposed as a faster, still-usable alternative for larger image sets or lower-powered machines."));
children.push(bullet("RANSAC over least-squares fitting: raw keypoint matches always contain outliers (mismatches). RANSAC was chosen specifically because it can estimate a correct homography even when a large fraction of the matches are wrong, which is essential for real photographs."));
children.push(bullet("Feather blending over hard overwrite: naively overwriting one warped image on top of another produces a visible seam wherever brightness differs between shots. Distance-transform feathering blends the overlap region proportionally to each pixel's distance from its image's edge, producing a smoother seam. A simple 'overwrite' mode is retained as a fast fallback."));
children.push(bullet("Sequential (pairwise) stitching over global bundle adjustment: for a small number of images captured in sequence, chaining pairwise homographies (image 1→2→3→...) is simpler to implement and reason about than a full global bundle-adjustment optimization, at the cost of some accumulated drift over many images — an accepted trade-off given the scope of this project."));
children.push(bullet("Synthetic sample-image generator: rather than depending on an external/downloaded dataset (which raises both reproducibility and academic-integrity concerns), a script generates deterministic, reproducible overlapping test images from scratch, letting anyone re-run the exact same test conditions."));

// ---------- 8. IMPLEMENTATION DETAILS ----------
children.push(h1("8. Implementation Details"));
children.push(p("Language & libraries: Python 3.10+, OpenCV (opencv-contrib-python) for SIFT/ORB/RANSAC/warping, NumPy for array operations, and pytest for testing.", { bold: false }));
children.push(h2("8.1 Feature Matching (src/feature_matching.py)"));
children.push(p("The FeatureMatcher class wraps OpenCV's SIFT_create()/ORB_create() detectors. For each image pair, keypoints and descriptors are computed independently, then matched with a brute-force matcher (cv2.BFMatcher) using k-nearest-neighbours (k=2). Lowe's ratio test discards ambiguous matches, keeping only correspondences where the best match is meaningfully closer than the second-best (ratio_thresh, default 0.75)."));
children.push(h2("8.2 Homography Estimation (src/homography.py)"));
children.push(p("The filtered matches' pixel coordinates are passed to cv2.findHomography with the RANSAC method and a configurable reprojection threshold (default 4.0 px). The function returns the 3x3 homography matrix and a boolean inlier mask, from which the inlier count and inlier ratio are derived — the primary quality metric reported for each stitched pair."));
children.push(h2("8.3 Stitching & Blending (src/stitcher.py)"));
children.push(p("For each new image, the canvas bounds needed to fit both the current panorama and the newly warped image are computed from their transformed corner points. Both images are warped onto this shared canvas (cv2.warpPerspective), and the overlapping region is blended using a distance-transform-weighted average (feather mode) or a simple mask-based overwrite (overwrite mode). This repeats sequentially across the full image sequence."));
children.push(h2("8.4 CLI & Configuration (src/cli.py, config/default_config.json)"));
children.push(p("argparse defines all command-line flags; a JSON config file supplies defaults that CLI flags can override. The CLI loads images from a directory (sorted by filename), runs the stitcher, times the run, writes the panorama image and an optional metrics CSV, and logs per-pair diagnostics."));

// ---------- 9. SCREENSHOTS / RESULTS ----------
children.push(h1("9. Screenshots / Results"));
children.push(p("The pipeline was run on 4 synthetically generated overlapping frames (via scripts/generate_sample_images.py) with the default SIFT + feather-blend configuration."));
children.push(imageParagraph(SHOT, "feature_matches_demo.jpg", 1142, 500, 560));
children.push(caption("Figure 6: Feature matches (SIFT + ratio test) found between two overlapping sample frames — 23 good matches out of 89 raw matches."));
children.push(imageParagraph(SHOT, "panorama_output.jpg", 1570, 506, 560));
children.push(caption("Figure 7: Final stitched panorama produced from 4 overlapping sample frames."));
children.push(p("Per-pair diagnostics reported for this run:", { bold: true }));
children.push(simpleTable(
  ["Pair", "Raw matches", "Good matches", "Inliers", "Inlier ratio"],
  [
    ["1 → 2", "89", "23", "14", "60.9%"],
    ["2 → 3", "115", "40", "22", "55.0%"],
    ["3 → 4", "125", "54", "30", "55.6%"],
  ]
));
children.push(new Paragraph({ text: "", spacing: { after: 100 } }));
children.push(p("Total stitching time for all 4 frames: 0.84 seconds."));

// ---------- 10. TESTING APPROACH ----------
children.push(h1("10. Testing Approach"));
children.push(p("The project includes an automated pytest suite of 11 unit and integration tests across three files:"));
children.push(bullet("tests/test_feature_matching.py — verifies unsupported detector methods are rejected, keypoints are found in a textured image, matching an image against itself yields many confident matches, and the ratio test reduces raw matches to a smaller good-match set."));
children.push(bullet("tests/test_homography.py — verifies homography estimation raises an error with too few matches, recovers an identity-like transform when an image is matched against itself, and correctly recovers a known pure-translation transform applied to a test image."));
children.push(bullet("tests/test_stitcher.py — verifies stitching requires at least 2 images, that stitching two or all sample frames produces a wider output image with a high inlier ratio, and that both blend modes (feather and overwrite) run without error."));
children.push(p("All 11 tests pass. The translation-recovery test is a particularly meaningful correctness check: a synthetic image is shifted by a known (x, y) offset, and the recovered homography's translation terms are asserted to match that known offset within a small tolerance — directly validating that the geometric estimation is correct, not just that the code runs without crashing."));
children.push(p("Run with: pytest tests/ -v", { italics: true }));

// ---------- 11. CHALLENGES FACED ----------
children.push(h1("11. Challenges Faced"));
children.push(bullet("Canvas sizing for warped images: computing the correct output canvas size and translation offset so that a warped image with negative coordinates (extending left of or above the current panorama) is still fully visible required careful corner-point transformation and bounding-box math."));
children.push(bullet("Seam visibility: an initial hard-overwrite blend produced a visible brightness seam between images. Implementing distance-transform feathering resolved this, at the cost of extra computation per stitched pair."));
children.push(bullet("Accumulated perspective drift: because images are stitched sequentially (pairwise) rather than with global bundle adjustment, later images in a long sequence can accumulate a small perspective skew relative to the first image — visible as a slight tilt at the far edge of the panorama in the results shown in Section 9. This is a known limitation of pairwise chaining and is discussed further in Section 13."));
children.push(bullet("Generating reliable test images without a real camera: to keep the project reproducible and independent of any external dataset, a synthetic scene generator was built that scatters distinctive shapes over a textured background and crops overlapping windows from it — this needed enough visual texture and variety for SIFT/ORB to find reliable keypoints, which took some tuning of shape count and size."));

// ---------- 12. LEARNINGS & KEY TAKEAWAYS ----------
children.push(h1("12. Learnings & Key Takeaways"));
children.push(bullet("Hands-on experience with the full classical feature-matching-to-geometric-alignment pipeline (SIFT/ORB, ratio test, RANSAC, homography) rather than just the theory covered in lectures."));
children.push(bullet("Understanding why robust estimation (RANSAC) is essential in real-world computer vision — raw feature matches are noisy, and a naive least-squares fit would be thrown off by even a handful of incorrect matches."));
children.push(bullet("Appreciating the practical difference between a mathematically correct homography and a visually seamless panorama — blending strategy matters as much as geometric accuracy for a good final result."));
children.push(bullet("Experience structuring a computer vision project into clean, independently testable modules connected by simple data contracts (dataclasses), rather than one monolithic script."));

// ---------- 13. FUTURE ENHANCEMENTS ----------
children.push(h1("13. Future Enhancements"));
children.push(bullet("Global bundle adjustment across all images simultaneously, instead of sequential pairwise chaining, to eliminate accumulated perspective drift in long image sequences."));
children.push(bullet("Automatic exposure/color correction across stitched images to handle photos taken with different camera exposure settings."));
children.push(bullet("Cylindrical or spherical projection to support full 360-degree panoramas rather than planar homography stitching alone."));
children.push(bullet("Multi-band (Laplacian pyramid) blending for even smoother seams than distance-transform feathering, particularly for high-frequency textures."));
children.push(bullet("Automatic detection of the best image ordering, instead of relying on filename order, using pairwise match-quality scoring."));

// ---------- 14. REFERENCES ----------
children.push(h1("14. References"));
children.push(bullet("R. Szeliski, Computer Vision: Algorithms and Applications, Springer-Verlag London Limited, 2011. (CSE3010 prescribed textbook)"));
children.push(bullet("R. Hartley and A. Zisserman, Multiple View Geometry in Computer Vision, 2nd Edition, Cambridge University Press, 2004. (CSE3010 reference textbook)"));
children.push(bullet("OpenCV Documentation — Feature Matching and Homography: https://docs.opencv.org/4.x/d1/de0/tutorial_py_feature_homography.html"));
children.push(bullet("OpenCV Documentation — cv2.findHomography and RANSAC: https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html"));
children.push(bullet("D. G. Lowe, \"Distinctive Image Features from Scale-Invariant Keypoints,\" International Journal of Computer Vision, 2004. (SIFT and the ratio test)"));
children.push(bullet("CSE3010 Computer Vision course syllabus, VIT Bhopal University (Modules 2 and 3: Depth Estimation and Multi-Camera Views; Feature Extraction and Image Segmentation)."));

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Calibri", size: 22 } } },
  },
  numbering: {
    config: [{ reference: "bullet-list", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: convertInchesToTwip(0.25), hanging: convertInchesToTwip(0.25) } } } }] }],
  },
  sections: [
    {
      properties: { page: { size: { width: 12240, height: 15840 } } },
      children,
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(path.join(ROOT, "docs", "Project_Report.docx"), buffer);
  console.log("Report written to docs/Project_Report.docx");
});
