from pathlib import Path

from visionqa import cli

DATA = Path(__file__).parent.parent / "data"


def test_cli_describe(capsys):
    rc = cli.main(["describe", str(DATA / "forest_green.png")])
    out = capsys.readouterr().out
    assert rc == 0
    assert "green" in out


def test_cli_ask_offline(capsys):
    rc = cli.main(["ask", str(DATA / "dark_night.png"), "how bright is this?"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "dark" in out.lower()


def test_cli_ask_real_without_key_soft_fails(monkeypatch, capsys):
    for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    rc = cli.main(["ask", str(DATA / "forest_green.png"), "what is this?", "--real"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "no API key found" in out


def test_cli_extract_table_writes_csv(tmp_path, capsys):
    out_path = tmp_path / "table.csv"
    rc = cli.main(["extract-table", str(DATA / "receipt_table.png"), "--out", str(out_path)])
    assert rc == 0
    assert out_path.exists()
    assert "cell_r0_c0" in out_path.read_text()
