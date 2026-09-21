#!/usr/bin/env python3
"""add-page-marks.py - the family mark beside every carried page's title.

    python Source/tools/add-page-marks.py [--check] [OldVersion]

The library's directory now gives each of its seven groups a mark, and a reader who
arrives at a page from a search result sees no sign of which family it belongs to.
This puts the group's mark beside the article's own `<h1>`, the same mark the
directory shows for that group, so a page announces its family and the two views of
the library agree.

FOUR DECISIONS, in the shape this repository's other carried-page tool uses:

* **The family is the index's, not a second list kept here.** This tool imports
  make-library-index.py and reads its `GROUPS` rule and its `group_of()`, exactly as
  add-article-nav.py does, so a page added tomorrow gets its mark by matching a slug
  prefix like every other page. A hand-kept mapping would be the one that goes stale.
* **The mark is an include marker, not pasted drawings.** Each page carries
  `<!--#include group-mark-<anchor>-->` inside its `<h1>`, and build-site.py's library
  include pass splices the real SVG from its generator, so a redrawn mark reaches all
  75 pages at the next build. Pasting the drawing would be 75 copies to re-paste.
* **It edits OldVersion/, and the build still copies the pages verbatim.** The library
  is carried rather than re-rendered, which is the rule this repository keeps saying is
  its spine, so the markup lives where a reviewer can read it.
* **It is idempotent and it refuses to guess.** An existing mark marker is replaced
  rather than duplicated, and a page with no `<h1>` raises in the index generator's own
  voice instead of being skipped quietly.

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

# Any mark marker already in the page, so a page that moves group is corrected rather
# than carried with two marks.
EXISTING = re.compile(r"<!--#include group-mark-[a-z0-9-]+-->")


def rewrite(page: str, slug: str, anchor: str) -> str:
    """The page with this group's mark as the first thing in its title."""
    marker = f"<!--#include group-mark-{anchor}-->"
    if "<h1>" not in page:
        raise index.MissingCopy(
            f"{slug}: no <h1> to put the mark in. Every carried page opens its "
            f"article with one; a page that does not is not a carried page.")
    if EXISTING.search(page):
        head = page[:page.index("<h1>")]
        rest = page[page.index("<h1>"):]
        return head + EXISTING.sub(marker, rest, count=1)
    return page.replace("<h1>", f"<h1>{marker}", 1)


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
        want = rewrite(page, slug, index.anchor(index.group_of(slug)))
        if want == page:
            continue
        changed.append(slug)
        total_delta += len(want.encode("utf-8")) - len(page.encode("utf-8"))
        if not check:
            path.write_bytes(want.encode("utf-8"))   # LF on every platform

    if check:
        if changed:
            print(f"DIFFERS: {len(changed)} page(s) need their mark: "
                  f"{', '.join(changed[:6])}{' ...' if len(changed) > 6 else ''}",
                  file=sys.stderr)
            return 1
        print(f"every page carries its group's mark: {len(slugs)} pages checked")
        return 0

    print(f"{len(changed)} page(s) given their mark, {total_delta:+,} B across the "
          f"library ({len(slugs)} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
