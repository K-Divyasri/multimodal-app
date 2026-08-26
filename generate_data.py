"""Generate the sample images this project teaches on.

Every pixel is chosen by hand, so the features `visionqa.features` extracts
from them are EXACT and safe to assert in tests, notebooks, and labs -- no
photo you download will ever be this predictable. Run this once:

    python generate_data.py

Six images, each isolating one lesson:

    bright_sky.png       pale, landscape        -> brightness "bright";
                          dominant-color naively snaps to "white" (a light
                          blue nearest-matches white before it matches blue --
                          the honest blind spot of nearest-palette color naming)
    dark_night.png        near-black, portrait   -> brightness "dark", color "black"
    forest_green.png      saturated green, square-> brightness "medium", color "green" (a clean match)
    solid_orange.png      saturated orange       -> brightness "medium", color "orange" (a clean match)
    checkerboard.png      alternating black/white-> high edge density, contrasts the solids
    receipt_table.png     white bg + grid lines  -> 4 rows x 3 columns, for table extraction
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

OUT = Path(__file__).parent / "data"


def _solid(width: int, height: int, rgb: tuple[int, int, int]) -> Image.Image:
    return Image.new("RGB", (width, height), rgb)


def make_bright_sky() -> Image.Image:
    return _solid(200, 120, (200, 225, 245))


def make_dark_night() -> Image.Image:
    return _solid(100, 160, (12, 12, 18))


def make_forest_green() -> Image.Image:
    return _solid(150, 150, (60, 150, 60))


def make_solid_orange() -> Image.Image:
    return _solid(120, 120, (230, 140, 40))


def make_checkerboard(size: int = 160, cell: int = 20) -> Image.Image:
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    for y in range(0, size, cell):
        for x in range(0, size, cell):
            if ((x // cell) + (y // cell)) % 2 == 0:
                arr[y : y + cell, x : x + cell] = 255
    return Image.fromarray(arr)


def make_receipt_table(rows: int = 4, cols: int = 3, cell_w: int = 100, cell_h: int = 50) -> Image.Image:
    width, height = cell_w * cols, cell_h * rows
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    for c in range(cols + 1):
        x = min(c * cell_w, width - 1)
        draw.line([(x, 0), (x, height - 1)], fill=(0, 0, 0), width=3)
    for r in range(rows + 1):
        y = min(r * cell_h, height - 1)
        draw.line([(0, y), (width - 1, y)], fill=(0, 0, 0), width=3)
    return img


IMAGES = {
    "bright_sky.png": make_bright_sky,
    "dark_night.png": make_dark_night,
    "forest_green.png": make_forest_green,
    "solid_orange.png": make_solid_orange,
    "checkerboard.png": make_checkerboard,
    "receipt_table.png": make_receipt_table,
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, builder in IMAGES.items():
        img = builder()
        img.save(OUT / name)
        print(f"wrote {OUT / name}  ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
