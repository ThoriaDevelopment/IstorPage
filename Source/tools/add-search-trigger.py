#!/usr/bin/env python3
"""add-search-trigger.py - the search trigger in every carried page's header.

    python Source/tools/add-search-trigger.py [--check] [OldVersion]

The library can be searched from one page - the directory's own find field, which
finds what is on the directory. This puts the way into every page: a trigger in the
header, and the one script that opens the palette over any page in the library.

FIVE DECISIONS, in the shape this repository's other carried-page tool uses:

* **It ships as a link, and the script upgrades it.** The trigger is
  `<a href="/library/">`, so a reader whose script does not run gets the directory
  instead of a button that does nothing, and search.js turns it into a button that
  opens a dialog only when it is actually there to do so.
* **It is authored, not injected.** The trigger is in the page's own HTML where a
  reviewer can read it, rather than assembled at runtime by the script. The one
  thing that must not be in the HTML is the dialog itself, which would be seventy-five
  copies of a widget; that belongs to the script.
* **It edits OldVersion/, and the build still copies the pages verbatim.** The
  library is carried rather than re-rendered, so the markup lives in the source.
* **One markup constant, replaced rather than appended.** Running this twice leaves
  the page as it was, and editing the constant below moves every page to the new
  markup at the next run. A second copy of the markup in this file would be the one
  that goes stale.
* **It refuses to guess.** A page with no header, or no theme script to sit beside,
  raises instead of being skipped quietly: a page with no trigger is a page outside
  the search, and that is a fact somebody should have to look at.

Standard library only.
"""

from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEGACY = ROOT / "OldVersion"

_spec = importlib.util.spec_from_file_location(
    "make_library_index", HERE / "make-library-index.py")
assert _spec and _spec.loader
index = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(index)

# The trigger, exactly, with its continuation lines indented relative to the first.
# One copy, so there is nothing to keep in step.
# `aria-label` rather than relying on the text: below 560px the rule in
# /styles.css hides the word, leaving a glyph, and a link with no accessible name
# is a link a screen reader announces as its href. The label contains the visible
# word, which is what "label in name" asks for.
TRIGGER = """<a class="search-open" href="/library/" data-search-open
  aria-label="Search every page" title="Search every page, or press /">
  <svg class="search-glyph" viewBox="0 0 20 20" aria-hidden="true">
    <circle cx="8.6" cy="8.6" r="5.2" />
    <path d="M12.6 12.6 L17 17" />
  </svg>
  <span class="search-word">Search</span>
  <kbd aria-hidden="true">/</kbd>
</a>"""


def trigger_at(indent: str) -> str:
    """The trigger block, sitting at the header's own indentation."""
    return "\n".join(indent + line if line else line
                      for line in TRIGGER.split("\n"))


EXISTING_TRIGGER = re.compile(
    r'[ \t]*<a class="search-open".*?</a>', re.S)

# Where the trigger goes: the theme control is the header's own first interactive
# element, and the trigger belongs on its left, next to the wordmark, where a
# header's search always sits.
ANCHOR = '<button class="theme-toggle"'

# The one deferred script per page. search.js is added after it, so the theme
# guard and the theme control keep their order.
THEME_JS = '<script src="/theme.js" defer></script>'
SEARCH_JS = '\n  <script src="/search.js" defer></script>'


def rewrite(page: str, slug: str) -> str:
    """The page with the trigger in its header and the palette's script in its head."""
    if 'class="page-head"' not in page:
        raise index.MissingCopy(
            f"{slug}: no page header. Every carried page opens with one, and a page "
            f"with no header has nowhere to put the way into the search.")
    if THEME_JS not in page:
        raise index.MissingCopy(
            f"{slug}: no `{THEME_JS}` to put the palette's script beside. The two "
            f"are the page's deferred scripts and they are added together.")

    header_at = page.index('<header class="page-head"')
    if EXISTING_TRIGGER.search(page):
        # A page that already carries one gets the new markup, wherever a reader
        # last put it, rather than a second trigger beside the first.
        indent = " " * (len(EXISTING_TRIGGER.search(page).group(0)) -
                         len(EXISTING_TRIGGER.search(page).group(0).lstrip()))
        page = (page[:header_at] +
                EXISTING_TRIGGER.sub(trigger_at(indent), page[header_at:], count=1))
    else:
        at = page.index(ANCHOR)
        line_start = page.rindex("\n", 0, at) + 1
        indent = page[line_start:at]
        page = (page[:line_start] + trigger_at(indent) + "\n" + page[line_start:])

    if '<script src="/search.js" defer></script>' not in page:
        page = page.replace(THEME_JS, THEME_JS + SEARCH_JS, 1)
    return page


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    args = [a for a in argv[1:] if not a.startswith("--")]
    check = "--check" in argv
    root = pathlib.Path(args[0]) if args else LEGACY

    slugs = index.library_slugs()
    changed: list[str] = []
    total_delta = 0
    for slug in slugs:
        path = root / slug / "index.html"
        page = path.read_text(encoding="utf-8")
        try:
            want = rewrite(page, slug)
        except index.MissingCopy as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if want == page:
            continue
        changed.append(slug)
        total_delta += len(want.encode("utf-8")) - len(page.encode("utf-8"))
        if not check:
            path.write_bytes(want.encode("utf-8"))   # LF on every platform

    if check:
        if changed:
            print(f"DIFFERS: {len(changed)} page(s) need the trigger: "
                  f"{', '.join(changed[:6])}{' ...' if len(changed) > 6 else ''}",
                  file=sys.stderr)
            return 1
        print(f"every page carries the search trigger: {len(slugs)} pages checked")
        return 0

    print(f"{len(changed)} page(s) given the trigger, {total_delta:+,} B across the "
          f"library ({len(slugs)} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
