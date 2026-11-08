#!/usr/bin/env python3
"""Convert original vector Matrix banner to a portable, looping GIF.

The editable SVG remains the source. Falling code moves; typography stays still.
"""
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET

import cairosvg
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "matrix-rain.svg"
DEST = ROOT / "assets" / "matrix-rain.gif"
SVG_NS = "{http://www.w3.org/2000/svg}"
FRAME_COUNT = 36
FRAME_DURATION_MS = 200


def convert(source=SOURCE, dest=DEST, frame_count=FRAME_COUNT):
    root = ET.parse(source).getroot()
    columns = [elem for elem in root.iter(f"{SVG_NS}g") if elem.attrib.get("class") == "rain"]
    if len(columns) < 5:
        raise ValueError("Matrix source is missing falling code columns")
    frames = []
    for frame in range(frame_count):
        for i, column in enumerate(columns):
            # A periodic cycle keeps the loop visually continuous.
            phase = ((frame + i * 11) % frame_count) / frame_count
            offset = -290 + 630 * phase
            column.set("transform", f"translate(0 {offset:.2f})")
        png = cairosvg.svg2png(bytestring=ET.tostring(root, encoding="utf-8"), output_width=960)
        frames.append(Image.open(BytesIO(png)).convert("RGB"))

    # Shared palette reduces color flicker and file size.
    master = frames[0].quantize(colors=112, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    quantized = [master] + [frame.quantize(palette=master, dither=Image.Dither.NONE) for frame in frames[1:]]
    dest.parent.mkdir(parents=True, exist_ok=True)
    quantized[0].save(
        dest, save_all=True, append_images=quantized[1:],
        loop=0, duration=FRAME_DURATION_MS, optimize=True, disposal=2,
    )
    with Image.open(dest) as check:
        if getattr(check, "n_frames", 0) != frame_count:
            raise RuntimeError("Generated Matrix GIF has an unexpected frame count")
    print(f"Generated {dest} ({dest.stat().st_size} bytes, {frame_count} frames)")


if __name__ == "__main__":
    convert()
