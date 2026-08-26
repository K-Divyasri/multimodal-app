"""Turn a grid of pixels into a handful of numbers a rule can act on.

This is the entire "understanding" the offline backend has: brightness,
orientation, a dominant color guessed by nearest-neighbour against a small
named palette, and a rough edge-density score. No neural network, no
training, no download -- just arithmetic on the pixel array. It is enough to
answer simple questions honestly, and it is DELIBERATELY too little to
understand a photo the way a person (or a real vision model) does. Where it
breaks is exactly where the lesson is.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# A small named palette. We snap the image's average color to whichever palette
# entry is nearest in RGB distance. This is a crude, well-known technique
# (nearest-centroid color naming) -- good enough for saturated colors, and
# happily wrong for pale or dark ones, which is the point: see
# `knowledge/06_the_dominant_color_blind_spot.md`.
PALETTE: dict[str, tuple[int, int, int]] = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "gray": (128, 128, 128),
    "red": (200, 30, 30),
    "green": (34, 139, 34),
    "blue": (70, 130, 220),
    "yellow": (220, 200, 40),
    "orange": (230, 140, 40),
    "purple": (130, 60, 160),
    "brown": (120, 80, 50),
}


def nearest_color_name(rgb: tuple[float, float, float]) -> str:
    """The palette entry closest to `rgb` in squared Euclidean distance."""
    best_name, best_dist = "black", float("inf")
    for name, (r, g, b) in PALETTE.items():
        dist = (rgb[0] - r) ** 2 + (rgb[1] - g) ** 2 + (rgb[2] - b) ** 2
        if dist < best_dist:
            best_dist, best_name = dist, name
    return best_name


def luminance(rgb_array: np.ndarray) -> float:
    """Average perceptual brightness, using the standard ITU-R BT.601 luma
    weights (green looks brighter to the human eye than red or blue, so it
    counts for more). Returns a number 0 (black) to 255 (white).
    """
    r, g, b = rgb_array[..., 0], rgb_array[..., 1], rgb_array[..., 2]
    return float((0.299 * r + 0.587 * g + 0.114 * b).mean())


def brightness_label(lum: float) -> str:
    """Bucket a luminance value into a word a question-answerer can use."""
    if lum < 70:
        return "dark"
    if lum > 180:
        return "bright"
    return "medium"


def orientation(width: int, height: int) -> str:
    """landscape (wider than tall), portrait (taller than wide), or square."""
    ratio = width / height
    if ratio > 1.2:
        return "landscape"
    if ratio < 0.83:
        return "portrait"
    return "square"


def edge_density(gray: np.ndarray) -> float:
    """A tiny stand-in for edge detection: how much do neighbouring pixels
    differ, on average? A flat color has almost no edges (near 0); a
    checkerboard or a busy photo has a lot (closer to 1). Real edge detectors
    (Sobel, Canny) do this with more care about direction and noise, but the
    core idea -- "edges are where brightness changes fast" -- is the same.
    """
    gx = np.diff(gray.astype(float), axis=1)
    gy = np.diff(gray.astype(float), axis=0)
    magnitude = np.sqrt(gx[:-1, :] ** 2 + gy[:, :-1] ** 2)
    return float(magnitude.mean() / 255.0)


def dominant_color(rgb_array: np.ndarray) -> str:
    """Average every pixel's color, then name the closest palette entry."""
    mean_rgb = rgb_array.reshape(-1, 3).mean(axis=0)
    return nearest_color_name(mean_rgb)


@dataclass(frozen=True)
class ImageFeatures:
    """Everything the offline backend knows about one image."""

    width: int
    height: int
    aspect_ratio: float
    orientation: str
    luminance: float
    brightness: str
    dominant_color: str
    edge_density: float


def extract_features(rgb_array: np.ndarray) -> ImageFeatures:
    """Compute every feature from an already-loaded (H, W, 3) array.

    Takes an array, not a path, so tests can build a tiny array by hand and
    check the math directly -- no image file needed. `imaging.load_rgb_array`
    is the one place that turns a file into this array.
    """
    height, width = rgb_array.shape[0], rgb_array.shape[1]
    gray = rgb_array.mean(axis=2)
    lum = luminance(rgb_array)
    return ImageFeatures(
        width=width,
        height=height,
        aspect_ratio=round(width / height, 3),
        orientation=orientation(width, height),
        luminance=round(lum, 2),
        brightness=brightness_label(lum),
        dominant_color=dominant_color(rgb_array),
        edge_density=round(edge_density(gray), 4),
    )


def extract_features_from_path(path) -> ImageFeatures:
    """Convenience wrapper: load a file, then extract its features."""
    from .imaging import load_rgb_array  # local import avoids a cycle at module load

    return extract_features(load_rgb_array(path))
