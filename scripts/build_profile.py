#!/usr/bin/env python3
"""Keep the single GitHub profile graphic current and render its Matrix rain.

The committed SVG contains the editorial layout and vector-engraved captions.
This script changes only its 90-day data group, numeric count, date range and
the offscreen rain-column translations used for the GIF frames. All projects,
lettering and decorative details remain in the editable SVG.
"""
from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
import math
import os
import sys
import urllib.error
import xml.etree.ElementTree as ET

import cairosvg
from PIL import Image

from update_pulse import DAYS, get_days

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "profile-composite.svg"
DEST = ROOT / "assets" / "profile-composite.gif"
NS = "{http://www.w3.org/2000/svg}"
FRAME_COUNT = 28
FRAME_DURATION_MS = 180
ET.register_namespace("", "http://www.w3.org/2000/svg")


def update_activity(days: list[tuple]) -> None:
    if len(days) != DAYS or any(days[i][0] >= days[i + 1][0] for i in range(DAYS - 1)):
        raise ValueError("Expected 90 chronological days of GitHub contributions")

    tree = ET.parse(SOURCE)
    root = tree.getroot()
    chart = root.find(".//*[@id='contribution-bars']")
    total_label = root.find(".//*[@id='contribution-count']")
    date_label = root.find(".//*[@id='updated-range']")
    description = root.find(f"{NS}desc")
    if any(item is None for item in (chart, total_label, date_label, description)):
        raise RuntimeError("Composite SVG missing required data slots")

    counts = [int(count) for _, count in days]
    if any(count < 0 for count in counts):
        raise ValueError("Contribution counts cannot be negative")
    maximum = max(counts) or 1

    for element in list(chart):
        chart.remove(element)

    for index, count in enumerate(counts):
        x = 72 + index * 11.9
        height = (110 * math.sqrt(count / maximum)) if count else 0
        top = 572 - height
        if count:
            ET.SubElement(chart, f"{NS}line", {
                "x1": f"{x:.1f}", "y1": "572", "x2": f"{x:.1f}", "y2": f"{top:.1f}",
                "stroke": "#91e8aa", "stroke-width": "3.2", "stroke-linecap": "round"
            })
            ET.SubElement(chart, f"{NS}circle", {
                "cx": f"{x:.1f}", "cy": f"{top:.1f}", "r": "2.3", "fill": "#d1ffd0"
            })
        else:
            ET.SubElement(chart, f"{NS}line", {
                "x1": f"{x:.1f}", "y1": "572", "x2": f"{x:.1f}", "y2": "570",
                "stroke": "#416f56", "stroke-width": "2"
            })

    total_label.text = f"{sum(counts):,}"
    date_label.text = f"{days[0][0].isoformat()}  /  {days[-1][0].isoformat()}"
    description.text = (
        "One unified editorial graphic: Matrix rain, public contribution activity, "
        "and selected projects. "
        f"{sum(counts)} public contributions from {days[0][0]} through {days[-1][0]}."
    )
    tree.write(SOURCE, encoding="unicode", xml_declaration=False)


def render_gif() -> None:
    root = ET.parse(SOURCE).getroot()
    rain = [node for node in root.iter(f"{NS}g") if node.get("data-rain") == "1"]
    if len(rain) < 15:
        raise RuntimeError("Expected at least 15 animated rain columns")

    frames = []
    for index in range(FRAME_COUNT):
        for column in rain:
            col_index = int(column.get("data-index", "0"))
            # Deterministic scrolling; each strand wraps at a different time.
            phase = ((index + 7 * col_index) % FRAME_COUNT) / FRAME_COUNT
            y = -290 + 790 * phase
            column.set("transform", f"translate(0 {y:.1f})")

        png = cairosvg.svg2png(bytestring=ET.tostring(root, encoding="utf-8"), output_width=1050)
        frames.append(Image.open(BytesIO(png)).convert("RGB"))

    shared_palette = frames[0].quantize(colors=112, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    encoded = [shared_palette] + [
        img.quantize(palette=shared_palette, dither=Image.Dither.NONE) for img in frames[1:]
    ]
    encoded[0].save(
        DEST, save_all=True, append_images=encoded[1:], loop=0,
        duration=FRAME_DURATION_MS, optimize=True, disposal=2
    )
    with Image.open(DEST) as rendered:
        if rendered.n_frames != FRAME_COUNT:
            raise RuntimeError("Unexpected number of generated animation frames")
    print(f"Generated {DEST} with {FRAME_COUNT} frames ({DEST.stat().st_size:,} bytes)")


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        try:
            days = get_days(os.environ.get("GITHUB_USERNAME", "brittneyleighb"),
                            token, datetime.now(timezone.utc).date())
            update_activity(days)
            print("Updated the unified image from actual GitHub public contribution data.")
        except (RuntimeError, ValueError, OSError, urllib.error.URLError) as error:
            # Keep the last verified data, rather than inventing a replacement.
            print(f"WARNING: Could not refresh contribution data: {error}", file=sys.stderr)
    else:
        print("No GITHUB_TOKEN: using the last verified chart snapshot.", file=sys.stderr)

    render_gif()

    # Keep the branch preview as an SVG; use the animated version on the
    # published profile after the first successful GitHub Actions run.
    readme = ROOT / "README.md"
    body = readme.read_text(encoding="utf-8")
    updated = body.replace("assets/profile-composite.svg", "assets/profile-composite.gif")
    if updated != body:
        readme.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
