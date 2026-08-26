"""Test setup: make `visionqa` importable and stub out the real-model path.

Root-level conftest so pytest adds this directory to sys.path -- `import
visionqa` works with no install step. `fake_litellm` installs a stand-in
`litellm` module so tests can exercise the real-vision code path (prompt
building, image encoding, JSON parsing) with no network and no API key.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

DATA = Path(__file__).parent / "data"


class _FakeMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class _FakeChoice:
    def __init__(self, content: str) -> None:
        self.message = _FakeMessage(content)


class _FakeResponse:
    def __init__(self, content: str) -> None:
        self.choices = [_FakeChoice(content)]


@pytest.fixture
def fake_litellm(monkeypatch):
    """A fake `litellm.completion()` returning a fixed reply, for --real tests."""

    def fake_completion(*, model, messages, temperature=0):
        return _FakeResponse("This looks like a light blue sky over a plain field.")

    module = types.ModuleType("litellm")
    module.completion = fake_completion
    monkeypatch.setitem(sys.modules, "litellm", module)
    return module


@pytest.fixture
def fake_litellm_table(monkeypatch):
    """A fake `litellm.completion()` that returns a JSON table, for extract-table tests."""

    def fake_completion(*, model, messages, temperature=0):
        return _FakeResponse('[["Item","Price"],["Coffee","4.00"],["Tea","3.50"]]')

    module = types.ModuleType("litellm")
    module.completion = fake_completion
    monkeypatch.setitem(sys.modules, "litellm", module)
    return module
