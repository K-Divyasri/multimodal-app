"""Lock in the exact, hand-verified numbers for every generated sample image.

Every image in data/ was built pixel-by-pixel in generate_data.py, so these
numbers are not approximations -- they are the ground truth this whole
project (notebooks, labs, knowledge files) is allowed to assert against.
"""

from pathlib import Path

import pytest

from visionqa.features import extract_features_from_path
from visionqa.tables import detect_grid
from visionqa.imaging import load_rgb_array

DATA = Path(__file__).parent.parent / "data"


@pytest.mark.parametrize(
    "filename,width,height,orientation,brightness,color",
    [
        ("bright_sky.png", 200, 120, "landscape", "bright", "white"),
        ("dark_night.png", 100, 160, "portrait", "dark", "black"),
        ("forest_green.png", 150, 150, "square", "medium", "green"),
        ("solid_orange.png", 120, 120, "square", "medium", "orange"),
        ("checkerboard.png", 160, 160, "square", "medium", "gray"),
        ("receipt_table.png", 300, 200, "landscape", "bright", "white"),
    ],
)
def test_sample_image_features(filename, width, height, orientation, brightness, color):
    f = extract_features_from_path(DATA / filename)
    assert (f.width, f.height) == (width, height)
    assert f.orientation == orientation
    assert f.brightness == brightness
    assert f.dominant_color == color


def test_bright_sky_is_the_naive_color_naming_blind_spot():
    """A human calls this pale image "light blue sky." Nearest-palette naming
    calls it "white" because pale colors sit closer to white than to any
    saturated hue in our small palette. This is the honest limitation the
    whole project is built to demonstrate -- not a bug to quietly fix.
    """
    f = extract_features_from_path(DATA / "bright_sky.png")
    assert f.dominant_color == "white"  # the naive (and slightly wrong) answer


def test_checkerboard_has_more_edges_than_any_solid_image():
    checker = extract_features_from_path(DATA / "checkerboard.png")
    for name in ("bright_sky.png", "dark_night.png", "forest_green.png", "solid_orange.png"):
        solid = extract_features_from_path(DATA / name)
        assert checker.edge_density > solid.edge_density


def test_receipt_table_grid_is_four_by_three():
    n_rows, n_cols = detect_grid(load_rgb_array(DATA / "receipt_table.png"))
    assert (n_rows, n_cols) == (4, 3)
