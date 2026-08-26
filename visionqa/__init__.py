"""visionqa - a from-scratch multimodal (vision) app: describe, ask, extract tables.

Two things live side by side in this package, on purpose:

    OFFLINE   pure numpy/Pillow feature extraction + rule-based answers. No key,
              no network, no download. It cannot understand a photo the way a
              real vision model can -- it can only report pixel-level facts
              (brightness, dominant color, orientation, edge density) and
              answer questions that map onto those facts.
    REAL      the same question, and the same image, sent to an actual
              vision-capable LLM (Claude, Gemini, GPT-4o -- anything LiteLLM
              can reach) that actually *sees* the picture.

The gap between the two is not a bug to hide -- it is the lesson. Watch the
offline path confidently call a pale sky-blue image "white" (nearest palette
match) while the real model correctly says "a light blue sky." That gap is
why the field builds real vision models instead of pixel statistics, and
being able to name the gap is worth more in an interview than reciting
"multimodal models are powerful."
"""

from __future__ import annotations

__all__ = ["__version__", "DEFAULT_VISION_MODEL"]

__version__ = "0.1.0"

# Free-first default: Gemini's flash model reads images and has a generous free
# tier. Override with the VISION_MODEL env var, e.g. "anthropic/claude-opus-4-8".
DEFAULT_VISION_MODEL = "gemini/gemini-1.5-flash"
