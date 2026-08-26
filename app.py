"""Streamlit demo: upload an image, see the offline features, ask a question.

Runs with no API key by default (the offline backend). Toggle "use a real
vision model" in the sidebar and paste a key to see the difference for
yourself -- most usefully on the pale sky-blue sample image, where the
offline backend confidently says "white."
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from PIL import Image

from visionqa import qa, tables
from visionqa.features import extract_features

st.set_page_config(page_title="VisionQA", page_icon=":frame_with_picture:")
st.title("VisionQA - a from-scratch multimodal app")
st.caption(
    "Upload an image, ask a question. Offline by default: no key, no upload, "
    "no cost. Flip the switch below to route through a real vision model."
)

use_real = st.sidebar.checkbox("Use a real vision model (needs an API key)", value=False)
if use_real:
    key = st.sidebar.text_input("API key (Gemini or Anthropic)", type="password")
    if key:
        import os

        os.environ.setdefault("GEMINI_API_KEY", key)
    st.sidebar.caption("Key is used for this session only; never stored or logged.")

uploaded = st.file_uploader("Upload a PNG or JPG", type=["png", "jpg", "jpeg"])

if uploaded:
    image_bytes = uploaded.getvalue()
    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    st.image(pil_image, caption=uploaded.name, use_container_width=True)

    import numpy as np

    features = extract_features(np.array(pil_image))
    st.subheader("Offline features (always computed, always free)")
    cols = st.columns(4)
    cols[0].metric("Size", f"{features.width}x{features.height}")
    cols[1].metric("Orientation", features.orientation)
    cols[2].metric("Brightness", features.brightness)
    cols[3].metric("Dominant color", features.dominant_color)
    st.caption(f"Luminance {features.luminance:.0f}/255, edge density {features.edge_density:.3f}")

    # Save to a temp path so the qa/table modules (which read files) can use it.
    import tempfile

    suffix = Path(uploaded.name).suffix or ".png"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name

    st.subheader("Ask a question")
    question = st.text_input("Question", value="What color is this image?")
    if st.button("Ask"):
        result = qa.ask(tmp_path, question, offline=not use_real)
        if use_real and result.offline:
            st.warning("No API key found - answered offline instead.")
        st.write(result.text)

    st.subheader("Extract a table (stretch goal)")
    st.caption("Best on a screenshot of a grid/table. Offline mode finds the shape only.")
    if st.button("Extract table"):
        rows = tables.extract_table(tmp_path, offline=not use_real)
        if rows:
            st.table(rows)
            st.download_button("Download CSV", tables.rows_to_csv(rows), file_name="table.csv")
        else:
            st.info("No grid detected in this image.")
else:
    st.info("Upload an image to get started, or try the sample images in `data/`.")
