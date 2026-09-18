#!/usr/bin/env python3
"""Extract the five Lucide glyphs the landing page draws, as one inline sprite.

Why this exists
---------------
The page needs five icons and must not fetch them. Stage 3 of
SITE_BUILD_PLAN.md settles that as an inline `<symbol>` sprite: five symbols,
zero requests, no `<img>`, every glyph in `currentColor` in both themes.

The glyphs are **not redrawn**. They are Lucide's own files, read out of the
app's own dependency, so the site and the product draw byte-identical
geometry. `C:\\Projects\\Istor\\Source` depends on `lucide-react`; this script
resolves it, reads the five `__iconNode` arrays, and emits them.

Two traps, both verified on disk 2026-09-18:

* **`FilePlus2` is an alias, not a file.** `file-plus-2.mjs` is 264 bytes of
  `export { default } from './file-plus-corner.mjs';`. The app imports the
  alias; the file that actually holds the geometry is `file-plus-corner.mjs`.
  A Lucide bump can drop the alias, so `ICONS` names the canonical file and
  this script fails loudly rather than emitting an empty symbol.
* **`__iconNode` carries a React-only `key`** on every child, and no stroke
  attributes at all — only `d` / `cx` / `cy` / `r` / `width` / `height` / `x` /
  `y` / `rx` / `ry`. The `key` is dropped here; stroke is set once, by the
  `.i` wrapper in styles.css, at 24px viewBox and `stroke-width: 2`. Do not
  chase 1.5 — that was a misreading of a 2x screenshot.

Lucide is ISC, so the page carries a provenance line: the footer's
*Icons from Lucide, ISC*.

Usage
-----
    python Source/tools/make-icon-sprite.py            # write icons.svg.partial
    python Source/tools/make-icon-sprite.py --check    # verify it is current

Output goes to `Source/icons.svg.partial`, which `build-site.py` splices into
`index.html` at the `<!--#include icons-->` marker. Run this **locally** and
commit the result: CI never regenerates artwork, and `verify-budget.py` is what
catches a stale regeneration.

Standard library only.
"""

from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
SOURCE = HERE.parent           # IstorPage/Source
OUT = SOURCE / "icons.svg.partial"

# Where lucide-react actually lives. The app is a sibling of IstorPage under
# C:\Projects\Istor, so it is three levels up and back down; the candidates
# after it are for a checkout that has moved or a second machine.
ICON_DIR_CANDIDATES = [
    HERE.parents[2] / "Source" / "node_modules" / "lucide-react" / "dist" / "esm" / "icons",
    SOURCE / "node_modules" / "lucide-react" / "dist" / "esm" / "icons",
]

# symbol id -> (canonical lucide filename, the page's own name for the glyph).
# The id is what index.html writes after `#`; the name is what the plan's table
# calls it, kept here so the two cannot drift apart unnoticed.
ICONS: dict[str, tuple[str, str]] = {
    "i-search":    ("search.mjs",           "magnifier, in `Filter sources…` and `Filter notes…`"),
    "i-page-plus": ("file-plus-corner.mjs", "page-plus, in `Add source` and `New note`"),
    "i-copy":      ("copy.mjs",             "copy control, under every answer"),
    "i-save-note": ("file-text.mjs",        "save-as-note control, under every answer"),
    "i-pencil":    ("pencil.mjs",           "the Viewer's pencil"),
}

# Attribute order in the emitted SVG. Lucide's objects are in source order, but
# pinning the order here means a Lucide reordering cannot show up as a diff.
ATTR_ORDER = ["d", "cx", "cy", "r", "x", "y", "width", "height", "rx", "ry"]


class IconSourceMissing(Exception):
    """lucide-react is not where this script expects it."""


# --------------------------------------------------------------------------
# A very small JavaScript reader.
#
# The `__iconNode` arrays hold only string and number literals, so a full JS
# parser would be absurd — but two of the five files wrap their objects across
# lines, and a `d` attribute contains characters no regex can safely stop on.
# So this walks the text with a cursor and handles strings properly.
# --------------------------------------------------------------------------

ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"', "'": "'"}


def _read_string(text: str, i: int) -> tuple[str, int]:
    """`text[i]` is a quote. Return (value, index just past the closing quote)."""
    quote = text[i]
    i += 1
    out: list[str] = []
    while i < len(text):
        ch = text[i]
        if ch == "\\":
            nxt = text[i + 1]
            out.append(ESCAPES.get(nxt, nxt))
            i += 2
            continue
        if ch == quote:
            return "".join(out), i + 1
        out.append(ch)
        i += 1
    raise ValueError("unterminated string literal in icon source")


def _skip_ws(text: str, i: int) -> int:
    while i < len(text) and text[i] in " \t\r\n":
        i += 1
    return i


def _read_object(text: str, i: int) -> tuple[dict[str, str], int]:
    """`text[i]` is `{`. Return (pairs in source order, index past the `}`)."""
    pairs: dict[str, str] = {}
    i = _skip_ws(text, i + 1)
    while i < len(text) and text[i] != "}":
        if text[i] == ",":
            i = _skip_ws(text, i + 1)
            continue
        key_start = i
        while text[i] not in ":":
            i += 1
        key = text[key_start:i].strip().strip('"\'')
        i = _skip_ws(text, i + 1)
        if text[i] in "\"'":
            value, i = _read_string(text, i)
        else:
            value_start = i
            while text[i] not in ",}":
                i += 1
            value = text[value_start:i].strip()
        pairs[key] = value
        i = _skip_ws(text, i)
    return pairs, i + 1


def _read_icon_node(text: str, filename: str) -> list[tuple[str, dict[str, str]]]:
    """Parse the `__iconNode` array out of one Lucide module."""
    anchor = text.find("const __iconNode = [")
    if anchor < 0:
        raise ValueError(f"{filename}: no `const __iconNode = [` — format changed upstream")
    i = text.index("[", anchor)
    children: list[tuple[str, dict[str, str]]] = []
    i = _skip_ws(text, i + 1)
    while i < len(text) and text[i] != "]":
        if text[i] == ",":
            i = _skip_ws(text, i + 1)
            continue
        if text[i] != "[":
            raise ValueError(f"{filename}: expected `[` at offset {i}, found {text[i]!r}")
        i = _skip_ws(text, i + 1)
        tag, i = _read_string(text, i)
        i = _skip_ws(text, i)
        if text[i] != ",":
            raise ValueError(f"{filename}: expected `,` after tag {tag!r}")
        i = _skip_ws(text, i + 1)
        attrs, i = _read_object(text, i)
        i = _skip_ws(text, i)
        if text[i] != "]":
            raise ValueError(f"{filename}: expected `]` closing the {tag!r} entry")
        children.append((tag, attrs))
        i = _skip_ws(text, i + 1)
    if not children:
        raise ValueError(f"{filename}: __iconNode is empty")
    return children


def find_icon_dir(explicit: str | None = None) -> pathlib.Path:
    for cand in ([pathlib.Path(explicit)] if explicit else []) + ICON_DIR_CANDIDATES:
        if cand.is_dir():
            return cand
    tried = "\n".join(f"       {c}" for c in ICON_DIR_CANDIDATES)
    sys.exit(
        "error: could not find lucide-react's icons directory.\n"
        f"       Tried:\n{tried}\n"
        "       It ships with the app, not with this repository. Install the\n"
        "       app's dependencies, or pass --icons-dir <path>."
    )


def lucide_version(icon_dir: pathlib.Path) -> str:
    """Read the version off lucide-react's own package.json (2 levels up)."""
    for parent in icon_dir.parents:
        pkg = parent / "package.json"
        if pkg.is_file():
            try:
                return json.loads(pkg.read_text(encoding="utf-8")).get("version", "unknown")
            except (OSError, ValueError):
                return "unknown"
    return "unknown"


def render_child(tag: str, attrs: dict[str, str]) -> str:
    """One `<path …/>`, with `key` dropped and attributes in a fixed order."""
    ordered = [a for a in ATTR_ORDER if a in attrs]
    ordered += [a for a in attrs if a not in ATTR_ORDER and a != "key"]
    rendered = " ".join(f'{a}="{attrs[a]}"' for a in ordered)
    return f"<{tag} {rendered}/>" if rendered else f"<{tag}/>"


def build(icon_dir: pathlib.Path) -> str:
    version = lucide_version(icon_dir)
    symbols: list[str] = []
    for symbol_id, (filename, description) in ICONS.items():
        path = icon_dir / filename
        if not path.is_file():
            sys.exit(
                f"error: {filename} is missing from {icon_dir}\n"
                f"       ({symbol_id} — {description})\n"
                "       Lucide renamed or dropped it. Find the canonical file and\n"
                "       update ICONS; do not substitute a lookalike."
            )
        children = _read_icon_node(path.read_text(encoding="utf-8"), filename)
        body = "\n".join("  " + render_child(tag, attrs) for tag, attrs in children)
        symbols.append(
            f'<symbol id="{symbol_id}" viewBox="0 0 24 24">\n{body}\n</symbol>'
        )

    header = (
        "<!--\n"
        f"  Generated by Source/tools/make-icon-sprite.py from lucide-react {version}.\n"
        "  Do not edit: run the generator. Lucide is ISC-licensed; the page cites it\n"
        "  in the footer. Geometry is a 24px viewBox at stroke-width 2 — the stroke is\n"
        "  set once by the .i wrapper in styles.css, not per glyph.\n"
        "-->"
    )
    return header + "\n" + "\n".join(symbols) + "\n"


def main(argv: list[str]) -> int:
    explicit = None
    check = False
    for i, arg in enumerate(argv[1:], start=1):
        if arg == "--check":
            check = True
        elif arg == "--icons-dir":
            explicit = argv[i + 1]
        elif arg.startswith("--icons-dir="):
            explicit = arg.split("=", 1)[1]

    icon_dir = find_icon_dir(explicit)
    sprite = build(icon_dir)

    if check:
        if not OUT.is_file():
            print(f"MISSING: {OUT} — run the generator", file=sys.stderr)
            return 1
        # Bytes, not text. read_text() puts the file through universal-newline
        # decoding, so a CRLF copy of the right sprite compared equal to a
        # fresh LF extraction — the same blind spot make-sitemap.py had.
        if OUT.read_bytes() != sprite.encode("utf-8"):
            print(f"STALE: {OUT} differs from a fresh extraction", file=sys.stderr)
            return 1
        print(f"current: {OUT.name} ({len(sprite.encode())} B, {len(ICONS)} symbols)")
        return 0

    # Written as bytes, not text: `write_text` translates "\n" to os.linesep,
    # which made this file CRLF on Windows while the whole library is LF-only.
    OUT.write_bytes(sprite.encode("utf-8"))
    print(f"wrote {OUT.relative_to(HERE.parents[1])} "
          f"({len(sprite.encode())} B, {len(ICONS)} symbols, lucide-react "
          f"{lucide_version(icon_dir)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
