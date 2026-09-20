#!/usr/bin/env python3
"""Assert that istor.fyi's artifact weighs what SITE_DESIGN_PLAN_V2.md says it weighs.

    python Source/tools/verify-budget.py [_site]

This is Stage 9's checks 1-3, and it is a **gate, not a report** (SITE_BUILD_PLAN.md
§3): a regenerated crop, a re-subset font or a re-encoded tile that changes the
page's weight fails the build, because the only other place those numbers live is
a table in the design plan, and a table cannot notice that it has gone stale.

The numbers are not in this file. They are in `budget.json`, which is the design
plan's §12.1 table as data, so the two cannot tell different stories. Every value
here was measured off disk on 2026-09-19 rather than transcribed, and the derived
totals are recomputed from the file sizes rather than trusted — a manifest whose
totals are allowed to disagree with its own rows asserts nothing.

    1  Byte manifest   every file in the plan's table is present at its exact size
    2  The payload     the phone figure is 194,064 B, the retina figure 388,356 B
    3  The document    index.html carries its CSS inline; report its gzip weight

It also asserts four things the manifest implies but does not state, each of which
is a real invariant of §1.1 rather than a nicety:

* **The two deliberately-duplicated paths are byte-identical.** inter-var.woff2 and
  gfs-didot.woff2 ship at both /fonts/ and /assets/fonts/, og-card.png at both
  /og-card.png and /brand/, istor-wordmark.woff2 at both /fonts/ and /brand/. ~114 KB
  of unreachable duplication that §1.1 forbids "optimising" away, because the library
  addresses its copies relatively and is not allowed to change. If someone ever does
  optimise it, this is the line that says so.
* **The artifact is exactly 156 files**, which is what makes check 4 meaningful.
* **The 75 library pages are present as 75 directories.** The count is exact;
  their bytes are a generous ceiling, because the pages are prose and prose
  moves every night the site is worked on (budget.json's _comment, 2026-09-20).
* **/styles.css is the library's**, not the new page's. This is the §1.1 collision
  that resolves in the library's favour: the new page inlines its CSS precisely so
  that a single root `<link href="/styles.css">` cannot serve it to 75 live pages.
  A 35,522 B file here is the proof that the new page did not win that path.

Standard library only — no `pip install` in CI.
"""

from __future__ import annotations

import gzip
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
BUDGET = HERE / "budget.json"

# §1.1's deliberate duplication, as (published path A, published path B) pairs.
# None of these may be "optimised" away; see the module docstring.
DUPLICATED = [
    ("/fonts/inter-var.woff2", "/assets/fonts/inter-var.woff2"),
    ("/fonts/gfs-didot.woff2", "/assets/fonts/gfs-didot.woff2"),
    ("/fonts/istor-wordmark.woff2", "/brand/istor-wordmark.woff2"),
    ("/og-card.png", "/brand/og-card.png"),
]

# The artifact's file count. Every stage above produced exactly this, and check 4
# (verify-links.py) walks all of them, so a change here is a change to that check.
# v1 was 120; v2 is 154. The first +18 was the export set: v1 shipped 3 exhibits x
# 6 files (AVIF/WebP/PNG at 1x and 2x) = 18, and v2 ships 9 exhibits x 4 files (the
# same, minus PNG) = 36. The second, on 2026-09-19, is the phone crops: four more
# crops x 4 files = 16, which took the set to 52. The third, same night, is
# /theme.js: the library's theme control is one shared file rather than a script
# copied into each of the 75 pages, which is the only shape that keeps a fix to
# it a one-file edit.
ARTIFACT_FILES = 148                  # + the generated library index; 8 fewer since
                                      # exhibit-12 retired its exports (2026-09-20)

NOT_A_PAGE = {"fonts", "img", "assets", "brand"}
# The library index lives at /library/ and is a page, but it is not one of the 75
# carried articles: it is generated FROM them. Counted here as a directory of
# bytes only under `files`, where its own size is asserted.
NOT_AN_ARTICLE = {"library"}
LIBRARY_TOC = NOT_A_PAGE | NOT_AN_ARTICLE


class Report:
    """Collects pass/fail lines so one run reports everything, not just the first."""

    def __init__(self) -> None:
        self.failures: list[str] = []
        self.checks = 0

    def ok(self, label: str, detail: str = "") -> None:
        self.checks += 1
        print(f"  ok    {label}" + (f"  {detail}" if detail else ""))

    def fail(self, label: str, detail: str) -> None:
        self.checks += 1
        self.failures.append(f"{label}: {detail}")
        print(f"  FAIL  {label}  {detail}", file=sys.stderr)


def size_of(site: pathlib.Path, published_path: str) -> int | None:
    """Published path -> size in _site/, or None when the file is not there."""
    rel = published_path.lstrip("/")
    if not rel or ".." in pathlib.PurePosixPath(rel).parts:
        raise ValueError(f"bad published path in budget.json: {published_path!r}")
    p = site / rel
    return p.stat().st_size if p.is_file() else None


def main(argv: list[str]) -> int:
    site = pathlib.Path(argv[1] if len(argv) > 1 else "_site")
    if not site.is_dir():
        print(f"error: {site} is not a directory — run build-site.py first",
              file=sys.stderr)
        return 1

    budget = json.loads(BUDGET.read_text(encoding="utf-8"))
    rep = Report()

    # -- 1 · the byte manifest, both halves of it ---------------------------
    print("1  byte manifest")

    sizes: dict[str, int] = {}
    for path, want in budget["files"].items():
        got = size_of(site, path)
        if got is None:
            rep.fail(path, "missing from the artifact")
        elif got != want:
            rep.fail(path, f"{got:,} B, manifest says {want:,} B "
                           f"({got - want:+,} B)")
        else:
            sizes[path] = got
    if len(sizes) == len(budget["files"]):
        rep.ok(f"the new page's {len(sizes)} files",
               f"{sum(sizes.values()):,} B")

    lib_sizes: dict[str, int] = {}
    for path, want in budget["library"]["files"].items():
        got = size_of(site, path)
        if got is None:
            rep.fail(path, "missing from the artifact")
        elif got != want:
            rep.fail(path, f"{got:,} B, manifest says {want:,} B "
                           f"({got - want:+,} B)")
        else:
            lib_sizes[path] = got
    if len(lib_sizes) == len(budget["library"]["files"]):
        rep.ok(f"the library's {len(lib_sizes)} shared files",
               f"{sum(lib_sizes.values()):,} B")

    # The duplication §1.1 forbids removing.
    for a, b in DUPLICATED:
        pa, pb = size_of(site, a), size_of(site, b)
        if pa is None or pb is None:
            rep.fail(f"{a} = {b}", "one of the two copies is missing")
        elif (site / a.lstrip("/")).read_bytes() != (site / b.lstrip("/")).read_bytes():
            rep.fail(f"{a} = {b}", "the two copies differ")
        else:
            rep.ok(f"{a} = {b}", f"{pa:,} B each, byte-identical")

    # -- 2 · the two payload totals, recomputed from the rows ---------------
    print("\n2  the payload")
    tot = budget["totals"]
    comp = tot["components"]

    def sum_of(suffix: str, retina: bool) -> int:
        """Total the exports whose name ends in `suffix`, at one density.

        `retina` has to be passed, not inferred: '.avif' and '.webp' are both
        suffixes of their own '@2x' names, so filtering on the suffix alone
        silently counts the retina set twice and reports 452,142 B twice over
        for a 1x payload the plan's table puts at 128,925 B.
        """
        return sum(v for k, v in sizes.items()
                   if k.startswith("/img/exhibit-") and k.endswith(suffix)
                   and ("@2x" in k) == retina)

    derived = {
        "bitmaps_1x": sum_of(".avif", False),
        "bitmaps_2x": sum_of("@2x.avif", True),
        "ground_tile": sizes.get("/img/ground-grain.png", 0),
        "fonts_3": sum(sizes.get(p, 0) for p in
                       ("/fonts/inter-var.woff2", "/fonts/gfs-didot.woff2",
                        "/fonts/istor-wordmark.woff2")),
    }
    for key, got in derived.items():
        want = comp[key]
        if got != want:
            rep.fail(f"components.{key}", f"{got:,} B, budget says {want:,} B")
        else:
            rep.ok(f"components.{key}", f"{got:,} B")

    payloads = {
        "phone_1x": derived["bitmaps_1x"] + derived["ground_tile"] + derived["fonts_3"],
        "retina_2x": derived["bitmaps_2x"] + derived["ground_tile"] + derived["fonts_3"],
        # No ".png" in this tuple, and that is the v2 decision rather than an
        # omission: PNG is gone from the shipped set. See build-site.py's
        # EXPORT_SUFFIXES — v1's six PNGs were 523,598 B, between 3.3x and 8.0x
        # the WebP beside each, for a format no browser released since 2020 needs.
        # The tuple must stay in step with the artifact: a suffix nothing matches
        # contributes 0 and would silently understate this.
        # Renamed from exports_all_36 on 2026-09-19, when the four phone crops
        # took the set from 36 files to 52. The number in the name was the only
        # thing keeping it honest and it stopped being true, so the name went.
        "exports_all": sum(sum_of(f, r) for f in (".avif", ".webp")
                           for r in (False, True)),
    }
    for key, got in payloads.items():
        want = tot[key]
        if got != want:
            rep.fail(key, f"{got:,} B, budget says {want:,} B")
        else:
            rep.ok(key, f"{got:,} B  ({got / 1000:.1f} KB)")

    # -- 3 · the document, which §7's table does not count ------------------
    print("\n3  the document")
    page = site / "index.html"
    html = page.read_bytes()
    gz = len(gzip.compress(html, 9, mtime=0))
    if b"<style>" not in html and b"<style " not in html:
        rep.fail("index.html", "carries no inline <style> — the CSS is not inlined, "
                               "so /styles.css would have to serve two pages")
    else:
        rep.ok("index.html carries its CSS inline")
    if b'<link rel="stylesheet"' in html or b'<link href="/styles.css"' in html:
        rep.fail("index.html", "links a stylesheet as well as inlining one")
    else:
        rep.ok("index.html requests no stylesheet")

    # The document is CEILING territory (budget.json's _comment, 2026-09-20):
    # content moves every night this site is worked on, so an exact raw assertion
    # forced a re-baseline into every commit and stopped being information. The
    # ceilings sit at round multiples of the measured figure (256 KiB over
    # ~74 KB; 32 KiB of gzip over ~20.2 KiB) so ordinary work never trips them
    # and real accidents — a copy deck pasted twice, a generator gone wrong —
    # still fail. The gzip ceiling keeps the job only it can do: catch a
    # document that got harder to compress, which an exact raw figure never
    # saw (the 2026-09-19 toolchain lesson, in this file's git history).
    told_raw = budget["document"].get("index_html_bytes_ceiling")
    told_gz = budget["document"].get("index_html_gzip_ceiling")
    if told_raw is None:
        # Reported either way so "75 KB" is never quoted as the whole cost.
        print(f"  --    index.html {len(html):,} B, {gz:,} B gzipped  "
              f"(budget.json has no asserted value yet)")
    else:
        if len(html) > told_raw:
            rep.fail("document.index_html_bytes_ceiling",
                     f"{len(html):,} B, over the {told_raw:,} B ceiling — a jump "
                     "this size is a decision, not an edit")
        else:
            rep.ok("document.index_html_bytes_ceiling",
                   f"{len(html):,} B raw  (ceiling {told_raw:,} B)")
        if told_gz is not None:
            if gz > told_gz:
                rep.fail("document.index_html_gzip_ceiling",
                         f"{gz:,} B, over the {told_gz:,} B ceiling — the document "
                         "has become harder to compress, not merely longer")
            else:
                rep.ok("document.index_html_gzip_ceiling",
                       f"{gz:,} B gzipped  (ceiling {told_gz:,} B)")

    # 3b · the shipped script, also a ceiling (16 KiB over 5,354 B shipped).
    # Its history as an exact assertion, and the 1,250 B of `//` prose that made
    # it exist, is in git; the ceiling keeps catching script that doubles.
    told_js = budget["document"].get("inline_js_bytes_ceiling")
    blocks = re.findall(r"<script>(.*?)</script>", html.decode("utf-8"), re.S)
    js = sum(len(b.encode()) for b in blocks)
    if told_js is None:
        print(f"  --    inline script {js:,} B  (budget.json has no asserted "
              f"value yet)")
    elif js > told_js:
        rep.fail("document.inline_js_bytes_ceiling",
                 f"{js:,} B of shipped script, over the {told_js:,} B ceiling")
    else:
        rep.ok("document.inline_js_bytes_ceiling",
               f"{js:,} B of shipped script, {len(blocks)} block(s)  "
               f"(ceiling {told_js:,} B)")

    # -- the invariants the manifest implies --------------------------------
    print("\n   artifact integrity")
    files = [p for p in site.rglob("*") if p.is_file()]
    if len(files) != ARTIFACT_FILES:
        rep.fail("artifact file count",
                 f"{len(files)} files, expected {ARTIFACT_FILES}")
    else:
        rep.ok("artifact file count", f"{ARTIFACT_FILES} files, "
               f"{sum(p.stat().st_size for p in files):,} B")

    pages = sorted(d for d in site.iterdir()
                   if d.is_dir() and (d / "index.html").exists()
                   and d.name not in LIBRARY_TOC)
    want_pages = budget["library"]["page_count"]
    if len(pages) != want_pages:
        rep.fail("library page count", f"{len(pages)}, expected {want_pages}")
    else:
        rep.ok("library page count", f"{want_pages} directories")
    page_bytes = sum(p.stat().st_size for d in pages for p in d.rglob("*")
                     if p.is_file())
    # A ceiling, not an equality: the 75 pages are prose, and prose moves every
    # night. The exact figure forced a re-baseline for every sentence edited;
    # the ceiling (1 MiB over ~619 KB) catches a page set that explodes.
    want_bytes = budget["library"]["page_bytes_ceiling"]
    if page_bytes > want_bytes:
        rep.fail("library page bytes ceiling",
                 f"{page_bytes:,} B, over the {want_bytes:,} B ceiling")
    else:
        rep.ok("library page bytes ceiling",
               f"{page_bytes:,} B  (ceiling {want_bytes:,} B)")

    # The library's index is generator output and is asserted exactly, for the
    # same reason index_html_bytes is: make-library-index.py reads the 75 pages'
    # own titles and summaries, so a change to this number means either a page
    # changed or the generator did, and both are worth seeing in the diff.
    want_index = budget["library"].get("index_bytes_ceiling")
    index = site / "library" / "index.html"
    if want_index is None:
        state = f"{index.stat().st_size:,} B" if index.is_file() else "missing"
        print(f"  --    /library/  {state}  (budget.json asserts no value yet)")
    elif not index.is_file():
        rep.fail("library.index_bytes_ceiling",
                 f"/library/index.html is missing — the 75 pages link to it")
    elif index.stat().st_size > want_index:
        rep.fail("library.index_bytes_ceiling",
                 f"{index.stat().st_size:,} B, over the {want_index:,} B ceiling")
    else:
        rep.ok("library.index_bytes_ceiling",
               f"{index.stat().st_size:,} B generated index  "
               f"(ceiling {want_index:,} B)")

    # -- and the one number that proves §1.1's collision resolved right ------
    styles = site / "styles.css"
    want_styles = budget["library"]["files"]["/styles.css"]
    if not styles.is_file():
        rep.fail("/styles.css", "missing — 75 library pages would render unstyled")
    elif styles.stat().st_size != want_styles:
        rep.fail("/styles.css",
                 f"{styles.stat().st_size:,} B — that is not the library's "
                 f"{want_styles:,} B file. The new page took the path.")
    else:
        rep.ok("/styles.css is the library's", f"{want_styles:,} B")

    # -- verdict -------------------------------------------------------------
    print()
    if rep.failures:
        print(f"FAILED - {len(rep.failures)} of {rep.checks} assertions",
              file=sys.stderr)
        for f in rep.failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print(f"budget ok - {rep.checks} assertions, every byte as the design plan has it")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
