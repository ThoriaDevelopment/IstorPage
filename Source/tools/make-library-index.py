#!/usr/bin/env python3
"""make-library-index.py - the door to the carried library, generated.

    python Source/tools/make-library-index.py [_site] [--check]

The landing page closes with "There are seventy-five other pages about local AI
on this site. These are the ones to start with", and then shows sixteen of them.
The other fifty-nine had no door: a reader who wanted more had to guess a slug or
read the sitemap, and the crawlers that already read `llms.txt` were better served
than the people the site is for. This builds that door.

FOUR DECISIONS, and each is a way this file could have gone wrong:

* **It is generated from the pages, not maintained beside them.** Every title and
  every summary is the page's own `<title>` and `name="description"`, read from
  `OldVersion/` — the same files the build copies. A hand-typed index is a second
  copy of seventy-five facts, and the second copy is the one that goes stale. It
  cannot drift because there is nothing to keep in step.
* **The grouping is derived from the slug, and an unmatched slug STOPS the
  build.** The groups are the question forms the slugs already encode (what-is,
  how/why, can/does/is, local-ai, vs, changelog), which is a rule about the
  library's own naming rather than a list of seventy-five placements. A page that
  fits no rule raises, exactly as `make-sitemap.py` raises on a page with no
  date: a directory that silently omits a page is worse than one that fails.
* **The header and footer are lifted verbatim from a real library page**, so the
  index cannot look almost like the library. One line is dropped from the lifted
  footer — the link back to this page, which is the one link that cannot be on it.
* **It carries no new stylesheet.** The page links `/styles.css`, the library's
  own file, and the handful of rules the list needs were added there so the index
  is drawn by the same tokens as the pages it lists.

Standard library only.
"""

from __future__ import annotations

import html
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEGACY = ROOT / "OldVersion"
SITE = ROOT / "_site"

# The library's own directories that are not pages. `lib.py` in the plan's terms;
# build-site.py calls the same idea NOT_A_PAGE.
NOT_AN_ARTICLE = {"assets", "brand", "tools"}

# The groups, in reading order. `prefixes` is matched against the slug, longest
# first, and the first group that matches wins — so `local-ai-vs-cloud-ai` lands
# in "Using it for your own work" rather than in the comparisons, which is where
# the landing page's reading list puts it too.
GROUPS: list[tuple[str, tuple[str, ...], str]] = [
    ("What it is", (
        "what-is-", "what-does-", "what-formats-",
    ), "The vocabulary: one page per term, each defined plainly and then placed "
       "against the thing it is usually confused with."),
    ("How it works, and why it behaves that way", (
        "how-document-", "how-much-", "why-",
    ), "The machinery behind an answer, and the behaviour that surprises people "
       "when a model gets something wrong."),
    ("How to do it", (
        "how-to-",
    ), "Tasks, start to finish."),
    ("Whether it can", (
        "can-", "does-", "is-",
    ), "Capability questions, answered with the limits attached rather than the "
       "headline alone."),
    ("Using it for your own work", (
        "local-ai-", "private-", "research-ai-", "run-research-",
    ), "What it is like in a literature review, a lecture hall, a field notebook, "
       "or a PDF you would rather not upload."),
    ("Compared with other tools", (
        "vs-",
    ), "Side-by-side tables, including where the other tool wins."),
    ("The project log", (
        "changelog",
    ), "What has shipped, newest first."),
]

TITLE = re.compile(r"<title>(.*?)</title>", re.S)
DESC = re.compile(r'<meta name="description" content="(.*?)"\s*/>', re.S)
HEAD = re.compile(r"<header class=\"page-head\">.*?</header>", re.S)
FOOT = re.compile(r"<footer class=\"page-foot\">.*?</footer>", re.S)
THEME_SCRIPT = re.compile(r"<script>\s*\(function \(\) \{.*?</script>", re.S)
# The library's one deferred script: the theme control's behaviour. The index
# lifts it rather than naming the file a second time, for the same reason it
# lifts the header — the button the header supplies is inert without this file,
# and a lift that cannot find it raises instead of shipping that button dead.
THEME_JS = re.compile(r'<script src="/theme\.js" defer></script>')


class MissingCopy(Exception):
    """A page with no title, no summary, or a slug no group claims."""


def library_slugs() -> list[str]:
    return sorted(d.name for d in LEGACY.iterdir()
                  if d.is_dir() and (d / "index.html").is_file()
                  and d.name not in NOT_AN_ARTICLE)


def entry(slug: str) -> tuple[str, str]:
    """One page's (title, summary), from the page itself."""
    text = (LEGACY / slug / "index.html").read_text(encoding="utf-8")
    t = TITLE.search(text)
    d = DESC.search(text)
    if not t or not d:
        raise MissingCopy(f"{slug}: no <title> or name=\"description\" to quote")
    return html.unescape(t.group(1)).strip(), html.unescape(d.group(1)).strip()


def group_of(slug: str) -> str:
    for heading, prefixes, _blurb in GROUPS:
        if any(slug.startswith(p) for p in prefixes):
            return heading
    raise MissingCopy(
        f"{slug}: no group claims this slug. Add its prefix to GROUPS in "
        f"make-library-index.py rather than leaving it out of the index.")


def _lift(pattern: re.Pattern[str], text: str, what: str) -> str:
    m = pattern.search(text)
    if not m:
        raise MissingCopy(f"could not lift the library's {what} from a page")
    return m.group(0)


def build() -> str:
    slugs = library_slugs()
    if not slugs:
        raise MissingCopy("no library pages found — refusing to write an empty index")

    grouped: dict[str, list[tuple[str, str, str]]] = {h: [] for h, _p, _b in GROUPS}
    for slug in slugs:
        title, summary = entry(slug)
        grouped[group_of(slug)].append((slug, title, summary))

    # A real page supplies the header, the footer and the theme guard, so the
    # index is dressed by the library rather than by a copy of it.
    sample = (LEGACY / slugs[0] / "index.html").read_text(encoding="utf-8")
    head = _lift(HEAD, sample, "header")
    foot = _lift(FOOT, sample, "footer")
    theme = _lift(THEME_SCRIPT, sample, "theme guard")
    theme_js = _lift(THEME_JS, sample, "theme control script")
    # ...minus the link back to this page, which is the one link that cannot be
    # on it. Written as a removal rather than as an omission so the rest of the
    # footer stays byte-for-byte the library's.
    foot = re.sub(r"\s*<a href=\"/library/\">[^<]*</a>", "", foot)

    out: list[str] = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="utf-8" />',
        '  <meta name="viewport" content="width=device-width, initial-scale=1" />',
        '  <meta name="color-scheme" content="light dark" />',
        "  <title>Every page on istor.fyi, by subject</title>",
        '  <meta name="description" content="A directory of all '
        f'{len(slugs)} pages about local AI on istor.fyi, grouped by the kind of '
        'question each one answers." />',
        '  <link rel="canonical" href="https://istor.fyi/library/" />',
        '  <meta name="robots" content="index, follow" />',
        '  <meta property="og:type" content="website" />',
        '  <meta property="og:title" content="Every page on istor.fyi, by subject" />',
        '  <meta property="og:description" content="A directory of all '
        f'{len(slugs)} pages about local AI on istor.fyi, grouped by the kind of '
        'question each one answers." />',
        '  <meta property="og:url" content="https://istor.fyi/library/" />',
        '  <meta property="og:image" content="https://istor.fyi/brand/og-card.png" />',
        '  <meta name="twitter:card" content="summary_large_image" />',
        '  <meta name="twitter:image" content="https://istor.fyi/brand/og-card.png" />',
        '  <link rel="icon" type="image/svg+xml" href="/brand/istor-page.svg" />',
        '  <link rel="icon" type="image/x-icon" href="/favicon.ico" sizes="any" />',
        '  <meta name="theme-color" content="#FFFFFF" />',
        '  <meta name="theme-color" content="#0A0A0A" '
        'media="(prefers-color-scheme: dark)" />',
        "",
        "  " + theme,
        '  <link rel="stylesheet" href="/styles.css" />',
        "  " + theme_js,
        "</head>",
        "<body>",
        "",
        "  " + head,
        "",
        '  <main class="page page-index">',
        "    <h1>Every page on this site.</h1>",
        f'    <p class="lede">All {len(slugs)} pages about local AI on istor.fyi, '
        "grouped by the kind of question each one answers. Every title and every "
        "line under it is the page's own, read from the page.</p>",
    ]

    for heading, _prefixes, blurb in GROUPS:
        items = grouped[heading]
        if not items:
            continue
        items.sort(key=lambda row: row[1].lower())
        out += [
            "",
            f"    <h2>{html.escape(heading)} ({len(items)})</h2>",
            f'    <p class="index-blurb">{html.escape(blurb)}</p>',
            '    <ul class="index-list">',
        ]
        for slug, title, summary in items:
            out += [
                f'      <li><a href="/{slug}/">{html.escape(title)}</a>'
                f'<span class="index-desc">{html.escape(summary)}</span></li>',
            ]
        out.append("    </ul>")

    out += [
        "  </main>",
        "",
        "  " + foot,
        "",
        "</body>",
        "</html>",
        "",
    ]
    return "\n".join(out)


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    args = [a for a in argv[1:] if not a.startswith("--")]
    check = "--check" in argv
    try:
        page = build()
    except MissingCopy as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    out = pathlib.Path(args[0]) if args else SITE / "library" / "index.html"
    if check:
        want = out.read_bytes()
        got = page.encode("utf-8")
        if want == got:
            print(f"byte-identical: {out} ({len(got):,} B)")
            return 0
        print(f"DIFFERS from {out}: {len(got):,} B generated, {len(want):,} B on disk",
              file=sys.stderr)
        return 1

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(page.encode("utf-8"))   # LF on every platform, as the library is
    print(f"wrote {out} ({len(page.encode('utf-8')):,} B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
