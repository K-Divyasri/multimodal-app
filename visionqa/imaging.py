"""Load an image as plain numbers, and encode one for sending to an LLM.

Every other module in this package works with a numpy array, never a Pillow
`Image` object. That is a deliberate seam: it means `features.py` and
`tables.py` can be tested with arrays you build by hand in a unit test,
with no image file and no Pillow round-trip required.
"""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path

import numpy as np
from PIL import Image


def load_rgb_array(path: str | Path) -> np.ndarray:
    """Read an image file into an (height, width, 3) uint8 numpy array."""
    with Image.open(path) as img:
        return np.array(img.convert("RGB"))


def to_base64_data_uri(path: str | Path) -> str:
    """Encode an image file as a `data:` URI -- the format vision APIs expect
    when you are not hosting the image somewhere with a public URL.
    """
    path = Path(path)
    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"
