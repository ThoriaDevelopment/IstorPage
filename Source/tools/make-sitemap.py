#!/usr/bin/env python3
"""Generate istor.fyi's sitemap.xml from the artifact's own file list.

The URL list is derived; the dates are NOT. Every entry needs a `lastmod`, and
those dates exist in exactly one place — `sitemap-dates.json`, seeded from
`OldVersion/sitemap.xml` before generation superseded it. There is no git
history here to read them from: this repository has never been under version
control, so a first commit would date every file the same day. Dates invented
from file mtimes would tell crawlers all 76 pages changed on every deploy.

So this module refuses to invent: a page with no entry in the dates file raises
`MissingDate`. That is deliberate — the failure has to be loud, because a page
shipping without a `lastmod` is invisible in every other check.

Standard library only. Used by build-site.py; also runnable directly, which is
how the byte-identity test in SITE_BUILD_PLAN.md §3 Stage 8 is performed:

    python Source/tools/make-sitemap.py OldVersion/sitemap.xml
"""

from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DATES = HERE / "sitemap-dates.json"

HEADER = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
)


class MissingDate(Exception):
    """A page in the artifact has no lastmod/changefreq in sitemap-dates.json."""


def load_dates(path: pathlib.Path = DATES) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build(pages, dates: dict | None = None) -> str:
    """Return sitemap.xml for `pages`, a collection of site paths.

    Paths are what the artifact actually contains — "/" for the home page,
    "/what-is-rag/" for a directory page. Output order is the dates file's
    order, so it is stable across runs and does not depend on how the artifact's
    file list happened to be walked.

    Raises MissingDate if any page is absent from the dates file, and ValueError
    if the dates file describes a page the artifact does not have (a stale entry
    is a page that was deleted without its date being removed).
    """
    dates = dates or load_dates()
    origin = dates["origin"].rstrip("/")
    rows = dates["pages"]

    dated = {r["path"]: r for r in rows}
    present = set(pages)

    missing = sorted(present - dated.keys())
    if missing:
        raise MissingDate(
            "no lastmod in sitemap-dates.json for: "
            + ", ".join(missing)
            + " — add an entry with the date you want search engines told"
        )

    stale = sorted(dated.keys() - present)
    if stale:
        raise ValueError(
            "sitemap-dates.json describes pages not in the artifact: " + ", ".join(stale)
        )

    blocks = []
    for row in rows:
        if row["path"] not in present:
            continue
        blocks.append(
            "  <url>\n"
            f"    <loc>{origin}{row['path']}</loc>\n"
            f"    <lastmod>{row['lastmod']}</lastmod>\n"
            f"    <changefreq>{row['changefreq']}</changefreq>\n"
            "  </url>"
        )
    return HEADER + "\n" + "\n".join(blocks) + "\n</urlset>"


def pages_from_sitemap(path: pathlib.Path) -> list[str]:
    """Read the page paths back out of an existing sitemap.xml. Used by the
    byte-identity test so the test does not depend on build-site.py existing."""
    import re

    text = path.read_text(encoding="utf-8")
    origin = load_dates()["origin"].rstrip("/")
    locs = re.findall(r"<loc>(.*?)</loc>", text)
    for loc in locs:
        if not loc.startswith(origin):
            raise ValueError(f"foreign origin in {path}: {loc}")
    return [loc[len(origin):] or "/" for loc in locs]


def _write_lf(path: pathlib.Path, text: str) -> None:
    """Write with LF on every platform.

    `write_text` translates "\\n" to os.linesep, so on Windows this file came
    out CRLF and 382 bytes heavier than the library's — one byte per line. The
    byte-identity test below did not catch it, because it compared decoded
    strings and universal-newline reading hides the difference. Both are fixed:
    the write is explicit, and the test now compares bytes.
    """
    path.write_bytes(text.encode("utf-8"))


def main(argv: list[str]) -> int:
    if len(argv) == 2:
        existing = pathlib.Path(argv[1])
        got = build(pages_from_sitemap(existing)).encode("utf-8")
        want = existing.read_bytes()
        if got == want:
            print(f"byte-identical: {existing} ({len(want)} B, "
                  f"{len(load_dates()['pages'])} urls)")
            return 0
        print(f"DIFFERS from {existing}", file=sys.stderr)
        for i, (a, b) in enumerate(zip(got.splitlines(), want.splitlines())):
            if a != b:
                print(f"  line {i + 1}:\n    got  {a!r}\n    want {b!r}", file=sys.stderr)
                break
        if len(got) != len(want):
            print(f"  {len(got)} B vs {len(want)} B — a whole-file difference "
                  "(newline convention?) rather than a content one", file=sys.stderr)
        return 1

    if len(argv) == 3:
        pages = [line.strip() for line in pathlib.Path(argv[1]).read_text().splitlines()
                 if line.strip()]
        _write_lf(pathlib.Path(argv[2]), build(pages))
        print(f"wrote {argv[2]}")
        return 0

    print(__doc__, file=sys.stderr)
    print("usage: make-sitemap.py <existing-sitemap.xml>          # byte-identity test",
          file=sys.stderr)
    print("       make-sitemap.py <pages.txt> <out-sitemap.xml>  # generate", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
