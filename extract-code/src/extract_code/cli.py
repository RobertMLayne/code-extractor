"""CLI entry point."""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .extractor import extract_all
from .parser import load_conversations

__all__ = ["main"]


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="extract-code",
        description="Extract triple‑backtick code blocks from ChatGPT HTML/JSON exports."
    )
    p.add_argument("html", type=Path, help="Path to exported HTML file")
    p.add_argument("output", type=Path, help="Destination directory")
    p.add_argument("--workers", type=int, default=1, help="Thread workers (I/O bound)")
    p.add_argument("--deduplicate", action="store_true", help="Skip identical snippets")
    p.add_argument("--no-overwrite", dest="overwrite", action="store_false", help="Never clobber existing files")
    p.add_argument("--no-add-comment", dest="add_comment", action="store_false", help="Omit provenance header")
    p.add_argument("-v", "--verbose", action="count", default=0, help="Increase verbosity (-v, -vv)")
    return p


def _setup_log(levels: int) -> None:
    lvl = logging.WARNING - 10 * min(levels, 2)
    logging.basicConfig(format="%(levelname)s: %(message)s", level=lvl)


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)
    _setup_log(args.verbose)

    convos = load_conversations(args.html)
    total = extract_all(
        convos,
        args.output,
        workers=args.workers,
        deduplicate=args.deduplicate,
        overwrite=args.overwrite,
        add_comment=args.add_comment,
    )
    print(f"Extraction complete – {total} files written.")


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv[1:])
