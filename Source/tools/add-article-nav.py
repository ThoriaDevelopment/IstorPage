#!/usr/bin/env python3
"""add-article-nav.py - the continue-reading pair on every carried page.

    python Source/tools/add-article-nav.py [--check] [OldVersion]

Seventy-five articles with a generated directory, and nothing joining one article
to the next. A reader who arrives at "What is a local LLM?" from a search result
finishes it and lands on a footer of six site-wide links: Home, All pages,
Compare, Changelog, GitHub, Repository. The library is the site's substance and
the page that holds it is a dead end, which is the one navigational thing every
documentation library a reader has ever used gets right.

FOUR DECISIONS:

* **The order is the index's order, not a list kept here.** This tool imports
  `make-library-index.py` and reads its GROUPS rule and its `group_of()`, so the
  sequence a reader walks is the sequence the directory shows, and a page added
  tomorrow joins the walk by matching a slug prefix like every other page. A
  second hand-kept ordering would be the one that goes stale.
* **It edits the pages, and the build still copies them verbatim.** `copy_library`
  in `build-site.py` is documented as zero rewrites, and that is worth keeping:
  the library is carried, not re-rendered, so what a reader gets is the file a
  reviewer read. The navigation therefore lives in `OldVersion/`, the same place
  the header's theme control went in, and this tool is committed so the next page
  can be given its pair with one command.
* **The walk is continuous, and the label says which group you are crossing into.**
  A group's last page leads to the next group's first, because a reader who
  finishes the vocabulary pages wants the next question rather than the directory
  again. The small line above each title names the group the neighbour is in, so
  crossing is announced rather than silent. The first and last page of the walk
  simply have one link each.
* **It is idempotent and it refuses to guess.** An existing block is replaced
  rather than duplicated, a page with no footer raises instead of being skipped,
  and a page whose slug no group claims raises in the index generator's own voice
  rather than being left out of the walk.

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

# The pair goes at the END OF THE ARTICLE, inside <main> and before the footer,
# because it is part of the reading rather than part of the site furniture. The
# same close-of-article slot every documentation library uses.
ARTICLE_END = "  </main>"
BLOCK = re.compile(r'  <nav class="page-next"[^>]*>.*?</nav>\n\n', re.S)


def reading_order() -> list[tuple[str, str, str]]:
    """Every article as (slug, title, group), in the order a reader walks them."""
    titles = {slug: index.entry(slug)[0] for slug in index.library_slugs()}
    out: list[tuple[str, str, str]] = []
    for heading, _prefixes, _blurb in index.GROUPS:
        group = sorted((s for s in titles if index.group_of(s) == heading),
                       key=lambda s: titles[s].lower())
        out += [(slug, titles[slug], heading) for slug in group]
    if len(out) != len(titles):
        raise index.MissingCopy("a slug is claimed by no group; the walk would skip it")
    return out


def block(prev: tuple[str, str, str] | None,
          nxt: tuple[str, str, str] | None) -> str:
    """The pair, as markup the library's own stylesheet draws."""
    out = ['  <nav class="page-next" aria-label="Keep reading">']
    # Previous first in the DOM, and that is a layout decision rather than a
    # reading one: the pair is a space-between flex row, so on a wide screen the
    # next page is pushed to the right, and on a narrow one where the two wrap,
    # the order a reader meets is the order they came in. Written the other way
    # round, a phone showed "next" above "previous", which is the wrong way to
    # walk backwards.
    if prev:
        slug, title, heading = prev
        out += [
            '    <a class="page-next-link" href="/%s/" rel="prev">' % slug,
            '      <span class="page-next-where">Previous in %s</span>' % heading,
            '      %s</a>' % title,
        ]
    if nxt:
        slug, title, heading = nxt
        out += [
            '    <a class="page-next-link is-next" href="/%s/" rel="next">' % slug,
            '      <span class="page-next-where">Next in %s</span>' % heading,
            '      %s</a>' % title,
        ]
    out.append("  </nav>")
    return "\n".join(out) + "\n\n"


def rewrite(page: str, slug: str, nav: str) -> str:
    if ARTICLE_END not in page:
        raise index.MissingCopy(
            f"{slug}: no {ARTICLE_END!r} to put the pair in front of. Every "
            f"carried page ends its article that way; a page that does not is "
            f"not a carried page.")
    page = BLOCK.sub("", page)
    at = page.index(ARTICLE_END)
    return page[:at] + nav + page[at:]


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    args = [a for a in argv[1:] if not a.startswith("--")]
    check = "--check" in argv
    root = pathlib.Path(args[0]) if args else LEGACY

    order = reading_order()
    changed: list[str] = []
    total_delta = 0
    for i, (slug, _title, _group) in enumerate(order):
        prev = order[i - 1] if i else None
        nxt = order[i + 1] if i + 1 < len(order) else None
        path = root / slug / "index.html"
        page = path.read_text(encoding="utf-8")
        want = rewrite(page, slug, block(prev, nxt))
        if want == page:
            continue
        changed.append(slug)
        total_delta += len(want.encode("utf-8")) - len(page.encode("utf-8"))
        if not check:
            path.write_bytes(want.encode("utf-8"))   # LF on every platform

    if check:
        if changed:
            print(f"DIFFERS: {len(changed)} page(s) need their pair rewritten: "
                  f"{', '.join(changed[:6])}{' ...' if len(changed) > 6 else ''}",
                  file=sys.stderr)
            return 1
        print(f"every page carries its pair: {len(order)} pages, {len(order)} checked")
        return 0

    print(f"{len(changed)} page(s) rewritten, {total_delta:+,} B across the library "
          f"({len(order)} in the walk)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
