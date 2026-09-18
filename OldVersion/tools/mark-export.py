#!/usr/bin/env python3
"""Rasterise the brand mark with its CSS variables resolved.

Why this exists
---------------
`brand/istor-page.svg` re-inks through a CSS custom-property contract, so the
same file serves the light and the dark world. Browsers resolve that. Nothing
else does.

Verified 2026-09-18, on this bench:

  * Inkscape 1.4.4 ignores `var()` in SVG presentation attributes, so the page
    fill falls back to black and the mark renders as a solid black shape.
  * ImageMagick 7.1.2 (librsvg delegate) renders almost nothing at all.
  * `xml.etree` parses the file happily once the comment bug is fixed, but
    parsing is not rendering.

Resolving the four variables to concrete colours first makes both render the
mark correctly. That step is the whole point of this script.

It also means the mark has no working generator without it, and `tools/README.md`
says a generated asset ships the script that made it. This is that script.

Usage
-----
    python tools/mark-export.py --theme light --width 512 -o out/mark-light.png
    python tools/mark-export.py --theme dark  --width 192 -o out/mark-dark.png

    # both worlds at the sizes the site actually uses
    python tools/mark-export.py --theme both --width 192

Notes
-----
* The mark is authored as strict XML and parsed as strict XML here, so a
  malformed comment fails loudly instead of silently rendering wrong. See the
  header of `brand/istor-page.svg` for the double-hyphen trap.
* `--ink`, `--paper`, `--iris` and `--pupil` override any single colour without
  touching the file, which is how you explore a new palette.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

import bench

# ElementTree is used only to prove the master is well-formed before Inkscape
# touches it. The input is a first-party file committed in this repository, so
# there is no untrusted document in play. defusedxml is preferred when it is
# installed, and its absence must not break the build, so it is optional rather
# than a hard dependency.
try:
    from defusedxml.ElementTree import ParseError as _ParseError
    from defusedxml.ElementTree import parse as _xml_parse

    _XML_BACKEND = "defusedxml"
except ImportError:
    from xml.etree.ElementTree import ParseError as _ParseError
    from xml.etree.ElementTree import parse as _xml_parse

    _XML_BACKEND = "stdlib"

REPO = Path(__file__).resolve().parent.parent
MASTER = REPO / "brand" / "istor-page.svg"

# The contract, as written in .claude/skills/istor-brand/SKILL.md.
# Light is the fallback already present in the master; dark is the lifted world.
PALETTES = {
    "light": {
        "mark-ink": "#171717",
        "mark-paper": "#FFFFFF",
        "mark-iris": "#F2726F",
        "mark-pupil": "#D93A3A",
    },
    "dark": {
        "mark-ink": "#FAFAFA",
        "mark-paper": "#171717",
        "mark-iris": "#56C0EC",
        "mark-pupil": "#2E97F2",
    },
}

def find_inkscape(explicit: str | None) -> str:
    """Inkscape is not on PATH on this machine; `bench` knows where it lives."""
    return bench.find("inkscape", explicit)


def check_master() -> None:
    """Fail loudly on malformed XML rather than rendering something wrong."""
    if not MASTER.exists():
        sys.exit(f"error: master not found at {MASTER}")
    try:
        _xml_parse(MASTER)
    except _ParseError as exc:
        sys.exit(
            f"error: {MASTER.name} is not well-formed XML: {exc}\n"
            "       An XML comment may not contain a double hyphen ('--').\n"
            "       See the comment block at the top of the file."
        )


def resolve(svg: str, colours: dict[str, str]) -> tuple[str, int]:
    """Replace `var(--mark-x, fallback)` with a concrete colour.

    Returns the resolved text and the number of substitutions made.
    """
    count = 0

    def sub(match: re.Match[str]) -> str:
        nonlocal count
        name, fallback = match.group(1), match.group(2)
        count += 1
        return colours.get(name, fallback)

    pattern = re.compile(r"var\(\s*--(mark-[a-z]+)\s*,\s*([^)]+?)\s*\)")
    return pattern.sub(sub, svg), count


def render(inkscape: str, svg_path: Path, out_path: Path, width: int) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [inkscape, "-w", str(width), "-o", str(out_path), str(svg_path)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0 or not out_path.exists():
        sys.stderr.write(proc.stdout + proc.stderr)
        sys.exit(f"error: Inkscape failed to render {svg_path.name}")
    if out_path.stat().st_size == 0:
        sys.exit(f"error: Inkscape wrote an empty file to {out_path}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Rasterise the Istor brand mark with CSS variables resolved."
    )
    ap.add_argument(
        "--theme",
        choices=["light", "dark", "both"],
        default="light",
        help="which ground the mark is drawn for (default: light)",
    )
    ap.add_argument(
        "--width", type=int, default=512, help="output width in px (default: 512)"
    )
    ap.add_argument(
        "-o",
        "--out",
        type=Path,
        help="output path. Required unless --theme both, which derives both names.",
    )
    ap.add_argument("--inkscape", help="path to the Inkscape binary")
    for key in ("ink", "paper", "iris", "pupil"):
        ap.add_argument(f"--{key}", help=f"override --mark-{key}")

    args = ap.parse_args()

    if args.theme != "both" and not args.out:
        ap.error("-o/--out is required unless --theme both is used")

    check_master()
    inkscape = find_inkscape(args.inkscape)
    source = MASTER.read_text(encoding="utf-8")

    themes = ["light", "dark"] if args.theme == "both" else [args.theme]

    overrides = {
        f"mark-{k}": v
        for k, v in (
            ("ink", args.ink),
            ("paper", args.paper),
            ("iris", args.iris),
            ("pupil", args.pupil),
        )
        if v
    }

    tmp_dir = REPO / ".mark-export.tmp"
    tmp_dir.mkdir(exist_ok=True)

    try:
        for theme in themes:
            colours = {**PALETTES[theme], **overrides}
            resolved, n = resolve(source, colours)

            if n == 0:
                sys.exit(
                    "error: no var(--mark-*) references found. The master's re-inking\n"
                    "       contract has changed; this script is now wrong."
                )

            staged = tmp_dir / f"istor-page.{theme}.svg"
            staged.write_text(resolved, encoding="utf-8")

            if args.theme == "both":
                out = (args.out or REPO / "brand") / f"istor-page-{theme}.png"
            else:
                out = args.out

            render(inkscape, staged, Path(out), args.width)
            print(
                f"{theme:<5} -> {out}  ({args.width}px, {n} variables resolved)"
            )
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
