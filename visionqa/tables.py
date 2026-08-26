"""The stretch goal: screenshot of a table -> structured rows -> CSV.

Split the same way as everything else in this package, and the split matters
more here than anywhere else:

    OFFLINE   find the grid LINES (rows and columns of mostly-dark pixels) and
              report how many rows and columns exist. It can tell you the
              table's *shape* with no key and no model. It cannot read a
              single character of the table's *contents* -- there is no pixel
              trick for "what does this cell say," only real OCR or a real
              vision model can do that.
    REAL      hand the whole image to a vision model and ask it to transcribe
              the table as JSON, which we then write out as CSV.

That gap -- structure vs. content -- is worth stating out loud in an
interview: cheap heuristics often get you the easy 80% (bounding boxes,
layout, counts) and the expensive 20% (actually reading it) is where you
reach for a real model.
"""

from __future__ import annotations

import csv
import io
import json
import os
import re

import numpy as np

from . import DEFAULT_VISION_MODEL
from .imaging import load_rgb_array, to_base64_data_uri

DARK_THRESHOLD = 100  # a grayscale value below this counts as "ink", not paper
MIN_LINE_COVERAGE = 0.6  # a row/column must be this dark-fraction to count as a grid line


def _dark_fraction_per_row(gray: np.ndarray) -> np.ndarray:
    return (gray < DARK_THRESHOLD).mean(axis=1)


def _dark_fraction_per_col(gray: np.ndarray) -> np.ndarray:
    return (gray < DARK_THRESHOLD).mean(axis=0)


def _collapse_to_lines(dark_fraction: np.ndarray) -> list[int]:
    """Indices that clear the coverage bar, with adjacent hits merged into one.

    A drawn line is a few pixels thick, so without merging we'd count one
    real line as three or four "lines" in a row.
    """
    hits = [i for i, frac in enumerate(dark_fraction) if frac > MIN_LINE_COVERAGE]
    lines: list[int] = []
    for i in hits:
        if not lines or i - lines[-1] > 2:
            lines.append(i)
    return lines


def detect_grid(rgb_array: np.ndarray) -> tuple[int, int]:
    """Count grid lines and return (n_rows, n_cols). N lines make N-1 cells."""
    gray = rgb_array.mean(axis=2)
    row_lines = _collapse_to_lines(_dark_fraction_per_row(gray))  # horizontal lines
    col_lines = _collapse_to_lines(_dark_fraction_per_col(gray))  # vertical lines
    n_rows = max(len(row_lines) - 1, 0)
    n_cols = max(len(col_lines) - 1, 0)
    return n_rows, n_cols


def extract_table_offline(image_path) -> list[list[str]]:
    """Find the table's shape; fill cells with placeholders (no OCR here)."""
    n_rows, n_cols = detect_grid(load_rgb_array(image_path))
    return [[f"cell_r{r}_c{c}" for c in range(n_cols)] for r in range(n_rows)]


def extract_table_real(image_path, model: str | None = None) -> list[list[str]]:
    """Ask a real vision model to transcribe the table as JSON rows."""
    from litellm import completion  # noqa: PLC0415

    model = model or os.environ.get("VISION_MODEL", DEFAULT_VISION_MODEL)
    data_uri = to_base64_data_uri(image_path)
    prompt = (
        "Read the table in this image. Reply with ONLY a JSON array of rows, each "
        'row a JSON array of cell strings, e.g. [["Item","Price"],["Coffee","4.00"]]. '
        "No other text."
    )
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_uri}},
            ],
        }
    ]
    resp = completion(model=model, messages=messages, temperature=0)
    raw = resp.choices[0].message.content or "[]"
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        return []
    try:
        rows = json.loads(match.group(0))
    except json.JSONDecodeError:
        return []
    return rows if isinstance(rows, list) else []


def extract_table(image_path, *, offline: bool = True, model: str | None = None) -> list[list[str]]:
    """The one function callers use, same offline/real split as `qa.ask`."""
    from .qa import has_api_key

    if offline or not has_api_key():
        return extract_table_offline(image_path)
    return extract_table_real(image_path, model)


def rows_to_csv(rows: list[list[str]]) -> str:
    """Turn a list-of-lists into CSV text."""
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    for row in rows:
        writer.writerow(row)
    return buf.getvalue()
