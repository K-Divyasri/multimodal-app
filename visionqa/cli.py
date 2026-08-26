"""Command-line front door.

    python -m visionqa describe photo.png
    python -m visionqa ask photo.png "what color is this?"
    python -m visionqa ask photo.png "what does the sign say?" --real
    python -m visionqa extract-table receipt.png
    python -m visionqa extract-table receipt.png --real --out table.csv

Offline by default, everywhere. `--real` routes through a vision-capable LLM
via LiteLLM and soft-falls back to offline with a note if no API key is set.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import qa, tables


def cmd_describe(args) -> int:
    print(qa.describe(args.image))
    return 0


def cmd_ask(args) -> int:
    result = qa.ask(args.image, args.question, offline=not args.real, model=args.model)
    if args.real and result.offline:
        print("[no API key found - falling back to offline mode]")
    print(result.text)
    return 0


def cmd_extract_table(args) -> int:
    rows = tables.extract_table(args.image, offline=not args.real, model=args.model)
    csv_text = tables.rows_to_csv(rows)
    print(csv_text, end="")
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(csv_text, encoding="utf-8")
        print(f"[wrote {args.out}]", file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="visionqa", description="A from-scratch multimodal vision app.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_desc = sub.add_parser("describe", help="offline one-paragraph summary of an image")
    p_desc.add_argument("image")
    p_desc.set_defaults(func=cmd_describe)

    p_ask = sub.add_parser("ask", help="ask a question about an image")
    p_ask.add_argument("image")
    p_ask.add_argument("question")
    p_ask.add_argument("--real", action="store_true", help="use a real vision model instead of offline rules")
    p_ask.add_argument("--model", help="override the LiteLLM model string")
    p_ask.set_defaults(func=cmd_ask)

    p_table = sub.add_parser("extract-table", help="turn a table screenshot into CSV")
    p_table.add_argument("image")
    p_table.add_argument("--real", action="store_true", help="use a real vision model instead of grid detection")
    p_table.add_argument("--model", help="override the LiteLLM model string")
    p_table.add_argument("--out", help="also write the CSV to this file")
    p_table.set_defaults(func=cmd_extract_table)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
