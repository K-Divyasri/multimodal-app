from pathlib import Path

from visionqa import qa

DATA = Path(__file__).parent.parent / "data"


def test_answer_offline_color_question():
    result = qa.ask(DATA / "forest_green.png", "what color is this image?")
    assert result.offline is True
    assert "green" in result.text.lower()


def test_answer_offline_brightness_question():
    result = qa.ask(DATA / "dark_night.png", "is this a dark or bright photo?")
    assert "dark" in result.text.lower()


def test_answer_offline_orientation_question():
    result = qa.ask(DATA / "bright_sky.png", "is this landscape or portrait orientation?")
    assert "landscape" in result.text.lower()


def test_answer_offline_edge_question_distinguishes_busy_from_flat():
    busy = qa.ask(DATA / "checkerboard.png", "is this a busy or simple image?")
    flat = qa.ask(DATA / "solid_orange.png", "is this a busy or simple image?")
    assert "busy/complex" in busy.text
    assert "simple/flat" in flat.text


def test_answer_offline_unknown_question_falls_back_honestly():
    result = qa.ask(DATA / "receipt_table.png", "what does the second row say?")
    assert "only answer basic questions offline" in result.text
    assert "--real" in result.text


def test_ask_without_key_soft_falls_back_to_offline(monkeypatch):
    for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    result = qa.ask(DATA / "forest_green.png", "what color is this?", offline=False)
    assert result.offline is True


def test_ask_real_uses_the_fake_model(monkeypatch, fake_litellm):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key-for-test")
    result = qa.ask(DATA / "bright_sky.png", "what is in this image?", offline=False)
    assert result.offline is False
    assert "sky" in result.text.lower()


def test_describe_reads_like_a_paragraph():
    text = qa.describe(DATA / "forest_green.png")
    assert "150x150" in text
    assert "green" in text
    assert "medium" in text
