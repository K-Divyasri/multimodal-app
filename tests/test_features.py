import numpy as np

from visionqa.features import (
    ImageFeatures,
    brightness_label,
    dominant_color,
    edge_density,
    extract_features,
    luminance,
    nearest_color_name,
    orientation,
)


def test_nearest_color_name_exact_hits():
    assert nearest_color_name((0, 0, 0)) == "black"
    assert nearest_color_name((255, 255, 255)) == "white"
    assert nearest_color_name((34, 139, 34)) == "green"


def test_luminance_black_and_white():
    black = np.zeros((4, 4, 3), dtype=np.uint8)
    white = np.full((4, 4, 3), 255, dtype=np.uint8)
    assert luminance(black) == 0.0
    assert luminance(white) == 255.0


def test_brightness_label_buckets():
    assert brightness_label(10) == "dark"
    assert brightness_label(120) == "medium"
    assert brightness_label(230) == "bright"
    # boundaries are exclusive on the dark/bright side
    assert brightness_label(70) == "medium"
    assert brightness_label(180) == "medium"


def test_orientation():
    assert orientation(200, 100) == "landscape"
    assert orientation(100, 200) == "portrait"
    assert orientation(150, 150) == "square"


def test_edge_density_flat_image_is_zero():
    flat = np.full((10, 10), 100.0)
    assert edge_density(flat) == 0.0


def test_edge_density_checkerboard_beats_flat():
    flat = np.full((20, 20), 100.0)
    checker = np.zeros((20, 20))
    checker[::2, ::2] = 255
    checker[1::2, 1::2] = 255
    assert edge_density(checker) > edge_density(flat)


def test_dominant_color_uniform_array():
    green = np.zeros((5, 5, 3), dtype=np.uint8)
    green[:, :] = (34, 139, 34)
    assert dominant_color(green) == "green"


def test_extract_features_end_to_end():
    arr = np.zeros((120, 200, 3), dtype=np.uint8)
    arr[:, :] = (60, 150, 60)
    f = extract_features(arr)
    assert isinstance(f, ImageFeatures)
    assert f.width == 200 and f.height == 120
    assert f.orientation == "landscape"
    assert f.brightness == "medium"
    assert f.dominant_color == "green"
    assert f.edge_density == 0.0
