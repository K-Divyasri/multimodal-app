from pathlib import Path

from visionqa import tables

DATA = Path(__file__).parent.parent / "data"


def test_extract_table_offline_shape_matches_the_real_grid():
    rows = tables.extract_table_offline(DATA / "receipt_table.png")
    assert len(rows) == 4
    assert all(len(row) == 3 for row in rows)


def test_extract_table_offline_cells_are_placeholders_not_real_content():
    rows = tables.extract_table_offline(DATA / "receipt_table.png")
    # Honest about what it doesn't know: cells are labelled by position, not content.
    assert rows[0][0] == "cell_r0_c0"
    assert rows[3][2] == "cell_r3_c2"


def test_rows_to_csv():
    csv_text = tables.rows_to_csv([["Item", "Price"], ["Coffee", "4.00"]])
    assert csv_text == "Item,Price\nCoffee,4.00\n"


def test_extract_table_without_key_falls_back_to_offline(monkeypatch):
    for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    rows = tables.extract_table(DATA / "receipt_table.png", offline=False)
    assert rows[0][0] == "cell_r0_c0"  # offline placeholder shape, not real content


def test_extract_table_real_parses_model_json(monkeypatch, fake_litellm_table):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key-for-test")
    rows = tables.extract_table(DATA / "receipt_table.png", offline=False)
    assert rows == [["Item", "Price"], ["Coffee", "4.00"], ["Tea", "3.50"]]
    csv_text = tables.rows_to_csv(rows)
    assert "Coffee,4.00" in csv_text


def test_extract_table_real_handles_garbage_gracefully(monkeypatch):
    import sys
    import types

    def fake_completion(*, model, messages, temperature=0):
        class R:
            choices = [type("C", (), {"message": type("M", (), {"content": "no json here"})()})]

        return R()

    module = types.ModuleType("litellm")
    module.completion = fake_completion
    monkeypatch.setitem(sys.modules, "litellm", module)
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key-for-test")
    rows = tables.extract_table(DATA / "receipt_table.png", offline=False)
    assert rows == []
