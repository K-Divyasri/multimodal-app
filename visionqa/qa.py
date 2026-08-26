"""Answer a question about an image -- offline from pixel features, or for
real from a vision-capable LLM.

Two backends behind one function, same shape as every other project on this
roadmap: `ask(image, question, offline=True)` never hallucinates because it
only ever reports arithmetic on pixels; `ask(..., offline=False)` sends the
actual picture to a model that can read a menu, count objects, or describe a
scene -- things no amount of pixel statistics will ever do.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from . import DEFAULT_VISION_MODEL
from .features import ImageFeatures, extract_features_from_path
from .imaging import to_base64_data_uri

# Keyword -> which feature to report. Checked in this order, so put more
# specific keywords first if you add to this list (e.g. "portrait" before a
# generic catch-all).
_KEYWORD_ANSWERS: list[tuple[str, callable]] = [
    ("colour", lambda f: f"The dominant color is {f.dominant_color}."),
    ("color", lambda f: f"The dominant color is {f.dominant_color}."),
    ("bright", lambda f: f"The image is {f.brightness} (average brightness {f.luminance:.0f} out of 255)."),
    ("dark", lambda f: f"The image is {f.brightness} (average brightness {f.luminance:.0f} out of 255)."),
    ("portrait", lambda f: f"The image is {f.orientation}, {f.width}x{f.height} pixels."),
    ("landscape", lambda f: f"The image is {f.orientation}, {f.width}x{f.height} pixels."),
    ("orientation", lambda f: f"The image is {f.orientation}, {f.width}x{f.height} pixels."),
    ("resolution", lambda f: f"The image is {f.width}x{f.height} pixels."),
    ("dimension", lambda f: f"The image is {f.width}x{f.height} pixels."),
    ("size", lambda f: f"The image is {f.width}x{f.height} pixels."),
    ("complex", lambda f: _edge_sentence(f)),
    ("busy", lambda f: _edge_sentence(f)),
    ("edge", lambda f: _edge_sentence(f)),
    ("simple", lambda f: _edge_sentence(f)),
]

_EDGE_BUSY_THRESHOLD = 0.05


def _edge_sentence(f: ImageFeatures) -> str:
    verdict = "busy/complex" if f.edge_density > _EDGE_BUSY_THRESHOLD else "simple/flat"
    return f"Edge density is {f.edge_density:.3f}, which reads as {verdict}."


@dataclass
class Answer:
    """One response, tagged with which backend actually produced it."""

    text: str
    offline: bool


def has_api_key() -> bool:
    """True if a provider key is set, so the CLI/app can fail soft to offline."""
    keys = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY")
    return any(os.environ.get(k) for k in keys)


def answer_offline(question: str, features: ImageFeatures) -> str:
    """Match the question against known keywords; fall back to a summary.

    This can only answer questions that map onto a feature we actually
    compute. Ask it to read text in the image, count objects, or explain
    what's happening, and it hits the honest fallback below -- there is no
    pixel statistic for "what does this say."
    """
    q = question.lower()
    for keyword, responder in _KEYWORD_ANSWERS:
        if keyword in q:
            return responder(features)
    return (
        "I can only answer basic questions offline (color, brightness, size, "
        "orientation, edges). Here's what I can tell without a real vision "
        f"model: {features.width}x{features.height} {features.orientation} image, "
        f"{features.brightness}, dominant color {features.dominant_color}. "
        "Use --real for anything more (reading text, counting objects, describing a scene)."
    )


def answer_real(question: str, image_path, model: str | None = None) -> str:
    """Send the actual image and question to a real vision-capable model."""
    from litellm import completion  # noqa: PLC0415

    model = model or os.environ.get("VISION_MODEL", DEFAULT_VISION_MODEL)
    data_uri = to_base64_data_uri(image_path)
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": {"url": data_uri}},
            ],
        }
    ]
    resp = completion(model=model, messages=messages, temperature=0)
    return resp.choices[0].message.content or ""


def ask(image_path, question: str, *, offline: bool = True, model: str | None = None) -> Answer:
    """The one function callers use. Soft-fails to offline with no key.

        ask("photo.png", "what color is this?")                # offline
        ask("photo.png", "what does the sign say?", offline=False)  # real
    """
    if offline or not has_api_key():
        features = extract_features_from_path(image_path)
        return Answer(answer_offline(question, features), offline=True)
    return Answer(answer_real(question, image_path, model), offline=False)


def describe(image_path) -> str:
    """A one-paragraph offline summary -- what `--describe` prints."""
    f = extract_features_from_path(image_path)
    return (
        f"{f.width}x{f.height} pixels, {f.orientation} (aspect ratio {f.aspect_ratio}), "
        f"{f.brightness} (brightness {f.luminance:.0f}/255), "
        f"dominant color {f.dominant_color}, edge density {f.edge_density:.3f}."
    )
