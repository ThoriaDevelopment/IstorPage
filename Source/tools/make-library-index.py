#!/usr/bin/env python3
"""make-library-index.py - the door to the carried library, generated.

    python Source/tools/make-library-index.py [_site] [--check]

The landing page closes with "There are seventy-five other pages about local AI
on this site. These are the ones to start with", and then shows sixteen of them.
The other fifty-nine had no door: a reader who wanted more had to guess a slug or
read the sitemap, and the crawlers that already read `llms.txt` were better served
than the people the site is for. This builds that door.

FIVE DECISIONS, and each is a way this file could have gone wrong:

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
* **The find field is authored `hidden` and revealed by the page's one script.**
  Seventy-five entries is a list a reader can read and cannot search, so the list
  got a field. It ships hidden, which means a reader whose script does not run
  gets the whole directory rather than a box that filters nothing, and the script
  filters on each entry's own title and summary. Matching is deliberately dull:
  every word typed has to appear in the entry, all of them, in any order, which is
  a rule a reader can predict after using it twice. Ranking and fuzzing would be a
  search engine inside a page whose claim is that it does not need one.

Standard library only.
"""

from __future__ import annotations

import html
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIGURES = HERE.parent / "figures"
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


# The page's one script. The generator's docstring carries the reasoning; what
# repeats here is what a reader of the page can see for themselves. It is
# authored hidden and unhidden by this script, so an unscripted reader gets the
# whole directory and no dead field. Matching is a word-AND over each entry's own
# title and summary, because a rule a reader can predict beats a rank they cannot
# see. The query is kept in the URL, so a filtered view can be linked and
# reloaded. And a group heading that says "(6)" while showing two entries is a
# lie, so the headings count what is on screen.
FIND_SCRIPT = r"""  <script>
  (function () {
    var form = document.querySelector('.index-find');
    var field = document.getElementById('find');
    var said = document.querySelector('.index-said');
    if (!form || !field || !said) return;

    var groups = [].slice.call(document.querySelectorAll('.index-group'));
    var items = [].slice.call(document.querySelectorAll('.index-list li'));
    var jump = document.querySelector('.index-jump');
    var total = items.length;

    items.forEach(function (li) {
      li.setAttribute('data-hay', (li.textContent || '').toLowerCase());
    });

    function apply() {
      var query = field.value.trim();
      var words = query.toLowerCase().split(/\s+/).filter(Boolean);
      var shown = 0;

      /* The jump row is navigation for browsing, and a filtered list is not a list
         anybody is browsing. Leaving it up would also offer links to groups the
         query has just hidden. */
      if (jump) jump.hidden = !!query;

      items.forEach(function (li) {
        var hit = words.every(function (word) {
          return li.getAttribute('data-hay').indexOf(word) !== -1;
        });
        li.hidden = !hit;
        if (hit) shown++;
      });

      groups.forEach(function (group) {
        var head = group.querySelector('h2');
        /* The group's own count is read off the heading ONCE, into data
           attributes, so a second pass is arithmetic rather than a re-parse: a
           heading that already reads "(2 of 6)" does not match the pattern that
           produced it. */
        if (!head.dataset.total) {
          var counts = /^(.*) \((\d+)\)$/.exec(head.textContent);
          if (!counts) return;
          head.dataset.name = counts[1];
          head.dataset.total = counts[2];
        }
        var here = group.querySelectorAll('.index-list li:not([hidden])').length;
        head.textContent = head.dataset.name + ' (' +
          (query ? here + ' of ' + head.dataset.total : head.dataset.total) + ')';
        group.hidden = !here;
      });

      said.textContent = !query ? ''
        : shown ? shown + ' of ' + total + ' pages match "' + query + '".'
        : 'Nothing matches "' + query + '". Try a shorter word.';

      history.replaceState(null, '', location.pathname +
        (query ? '?q=' + encodeURIComponent(query) : ''));
    }

    form.hidden = false;
    var saved = /[?&]q=([^&]*)/.exec(location.search);
    if (saved) {
      try { field.value = decodeURIComponent(saved[1].replace(/\+/g, ' ')); } catch (e) {}
    }
    field.addEventListener('input', apply);
    form.addEventListener('submit', function (event) { event.preventDefault(); apply(); });

    /* The rows the reader can currently see, in reading order. Read fresh on every
       keystroke rather than cached: the list changes under the reader's fingers as
       they type, and a stale cache would walk into a hidden row. */
    function rows() {
      var out = [];
      items.forEach(function (li) {
        if (!li.hidden) out.push(li.querySelector('a'));
      });
      return out.filter(Boolean);
    }

    /* ONE FOCUS ORDER: the field, then every match, then the field again. Arrow
       keys move real focus to the link rather than a decorative highlight, so the
       reader's screen reader announces each page's title as they arrive, Enter
       activates it natively, and no ARIA listbox has to be layered over a list of
       links. Down and Up are each other's inverse, so a reader who overshoots
       presses the other arrow instead of hunting for the way back. */
    function walk(step) {
      var list = rows();
      if (!list.length) return false;
      var at = list.indexOf(document.activeElement);
      if (at === -1 && document.activeElement !== field) return false;
      var next = at === -1 ? (step > 0 ? 0 : list.length - 1) : at + step;
      if (next < 0 || next >= list.length) field.focus();
      else list[next].focus();
      return true;
    }

    document.addEventListener('keydown', function (event) {
      var t = event.target;
      var typing = t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' ||
                         t.isContentEditable);
      var plain = !event.metaKey && !event.ctrlKey && !event.altKey;

      /* `/` from anywhere on the page puts the caret in the field. A find box a
         reader has to click is a find box most readers never use, and the key is
         the one every reader of a directory already reaches for. */
      if (event.key === '/' && plain && !typing) {
        event.preventDefault();
        field.focus();
        field.select();
        return;
      }

      if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
        if (walk(event.key === 'ArrowDown' ? 1 : -1)) event.preventDefault();
        return;
      }

      /* A row has focus and the reader has started typing again, so the character
         belongs in the field rather than being swallowed by a link. */
      if (plain && document.activeElement !== field && rows().indexOf(document.activeElement) !== -1) {
        if (event.key.length === 1) {
          event.preventDefault();
          field.focus();
          field.value += event.key;
          apply();
        } else if (event.key === 'Backspace') {
          event.preventDefault();
          field.focus();
        }
      }
    });

    field.addEventListener('keydown', function (event) {
      if (event.key !== 'Escape') return;
      if (field.value) { field.value = ''; apply(); }
      else field.blur();
    });

    apply();
  })();
  </script>"""


def anchor(heading: str) -> str:
    """A group heading as a fragment. The jump row needs somewhere to jump to."""
    return re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")


def mark(heading: str) -> str:
    """The heading's own mark, read from its generator's output and inlined.

    The seven marks are one set drawn by make-group-marks.py, and this function is
    where the two halves meet: the file is named for the heading's anchor, so a group
    that was renamed would look for a mark that does not exist and this fails the
    build rather than shipping a heading with no mark. Inlining rather than linking is
    the page's own reason: an <img> is isolated from the page's colour, so a mark
    drawn in currentColor would arrive black.
    """
    path = FIGURES / f"group-mark-{anchor(heading)}.svg"
    if not path.is_file():
        raise SystemExit(f"make-library-index: no mark for the group {heading!r} - "
                         f"expected {path}. Run python Source/tools/make-group-marks.py.")
    return path.read_text(encoding="utf-8").strip() + "\n      "


# What the mark needs HERE and nowhere else: the heading becomes a flex row so a
# wrapped title keeps the mark on its first line, and a group under the pointer
# brightens its mark, which is the directory's one hover. The mark's SIZE and colour
# are in /styles.css, because 75 carried pages draw the same mark beside their h1.
MARK_CSS = """
    <style>
      .index-group h2 { display: flex; align-items: center; gap: 0.6rem; }
      .index-group:hover .group-mark,
      .index-group:focus-within .group-mark { color: var(--ink); }
    </style>"""


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
        "",
        '    <form class="index-find" role="search" hidden>',
        '      <label for="find">Find a page</label>',
        '      <input type="search" id="find" name="q" autocomplete="off"',
        '             spellcheck="false" placeholder="A term, a question, a subject" />',
        '      <p class="index-hint">Press <kbd>/</kbd> to search, then the arrow keys',
        '        to walk the matches.</p>',
        '      <p class="index-said" aria-live="polite"></p>',
        "    </form>",
    ]

    sections: list[str] = []
    present: list[tuple[str, int]] = []
    for heading, _prefixes, blurb in GROUPS:
        items = grouped[heading]
        if not items:
            continue
        items.sort(key=lambda row: row[1].lower())
        present.append((heading, len(items)))
        sections += [
            "",
            f'    <section class="index-group reveal" id="{anchor(heading)}">',
            f"      <h2>{mark(heading)}{html.escape(heading)} ({len(items)})</h2>",
            f'      <p class="index-blurb">{html.escape(blurb)}</p>',
            '      <ul class="index-list">',
        ]
        for slug, title, summary in items:
            sections += [
                f'        <li><a href="/{slug}/">{html.escape(title)}</a>'
                f'<span class="index-desc">{html.escape(summary)}</span></li>',
            ]
        sections += [
            "      </ul>",
            "    </section>",
        ]

    # The jump row, for the reader who is not searching anything in particular.
    # It is static markup with static links, so it works with no script, and the
    # script hides it when a query is live: a row of "jump to this group" links is
    # navigation for browsing a list, and a filtered list is not one. Long first,
    # because the largest group is the one a reader most needs to leave.
    out += [
        "",
        '    <nav class="index-jump" aria-label="Jump to a group">',
        "      <p>Jump to</p>",
        "      <ul>",
    ]
    for heading, count in sorted(present, key=lambda row: -row[1]):
        out += [
            f'        <li><a href="#{anchor(heading)}">{html.escape(heading)}</a></li>',
        ]
    out += [
        "      </ul>",
        "    </nav>",
    ]
    # The marks' own sizing, before the groups that use it.
    out += [MARK_CSS]
    out += sections
    out += [
        "  </main>",
        "",
        "  " + foot,
        "",
        FIND_SCRIPT,
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
