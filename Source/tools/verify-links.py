#!/usr/bin/env python3
"""Assert that istor.fyi's artifact holds together — Stage 9's checks 4 to 9.

    python Source/tools/verify-links.py [_site]

`verify-budget.py` runs checks 1-3 and asks whether the bytes are right. This
one asks whether the SITE is right: that nothing points at a file that is not
there, that the new page keeps the promises §8 makes about behaviour, that the
colours still measure what the design plan says they measure, that no character
falls out of its font, that the home page really is the new one, and that the 75
carried pages survived the crossing.

    4  Every internal href/src resolves inside _site/ — 120 files, and in
       particular the library's relative `assets/fonts/...`, which is the one
       asset a deploy of this shape loses without noticing.
    5  No behaviour — ON THE LANDING PAGE ONLY. Scoped deliberately: all 75
       legacy pages carry an inline script and are published as they are.
    6  Contrast — the six ratios §1 states, recomputed from the tokens in the
       stylesheet, so a token edit cannot leave a comment behind.
    7  Codepoints — every RENDERED non-ASCII character is inside a declared
       `unicode-range`, or is on the one-entry allow-list below.
    8  The home page is the new one. This is the guard for §1.3's silent
       failure, and the reason the assembler copies by allowlist.
    9  Library integrity — 75 pages, the library's /styles.css, self-canonicals,
       the brand files, and the sitemap/llms.txt cross-check both ways.

Three of these are stronger than the plan asks, because the checks are cheap and
the failure they prevent is not:

* **Check 4 also verifies fragments.** `#how-it-answers` is in the page's own
  nav and `#m-fold` is in all 75 library pages; a href that resolves to a file
  but not to an id is still a broken link.
* **Check 6 recomputes from the tokens rather than trusting the table**, and
  asserts the two documented FAILURES as well (the #767676 floor, the rejected
  dark citation pair). A number in a comment that nothing recomputes is a number
  that is wrong within a month — this file was written after finding three.
* **The artifact must be LF-only.** A CRLF `sitemap.xml` already shipped once,
  and the byte-identity test that should have caught it compared decoded strings
  and passed. Check it here, on bytes.

Standard library only — no `pip install` in CI.
"""

from __future__ import annotations

import html as htmllib
import importlib.util
import json
import pathlib
import math
import re
import sys
import unicodedata

HERE = pathlib.Path(__file__).resolve().parent

# The library index generator, loaded the same way build-site.py loads it: a
# hyphenated filename cannot be imported by name. The continue-reading walk is
# asserted against the same GROUPS rule that built the directory, so the two
# cannot disagree about where an article's neighbours are.
_spec = importlib.util.spec_from_file_location(
    "make_library_index", HERE / "make-library-index.py")
assert _spec and _spec.loader
make_library_index = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(make_library_index)

# ---------------------------------------------------------------- expectations
# A library page is a directory at the artifact root holding an index.html.
# These four are directories at the root that are NOT pages.
# Directories in the artifact that are assets rather than pages.
NOT_A_PAGE = {"fonts", "img", "assets", "brand"}
# A directory in the artifact that holds a page but is not one of the 75 carried
# articles: the library's own index at /library/. It is checked like any other
# page — its 75 links are resolved by check 4 below — but it is not an article,
# so it does not move LIBRARY_PAGES.
NOT_AN_ARTICLE = {"library"}
LIBRARY_TOC = NOT_A_PAGE | NOT_AN_ARTICLE

# The authored page, as a path from the repo root. Every other check in this file
# reads the ARTIFACT; the momentum clause reads the SOURCE, because the notes that
# quote the mechanism's constants are markup comments and `inline_markup()` strips
# them on the way into the build. Prose in the source, behavior in the artifact.
SOURCE = pathlib.Path("Source")

LIBRARY_PAGES = 75
# §1.1: /styles.css is the library's file. This number is also in budget.json, and
# the duplication is deliberate: the two tools read the same artifact by different
# routes, so a size that only one of them knows about is itself the finding.
LIBRARY_STYLES_BYTES = 70301          # 50,980 to 55,112 on 2026-09-20: the
                                      # metric-matched fallback faces and the
                                      # measurement that chose them, so the swap
                                      # does not move the page on a slow link;
                                      # 55,701 on 2026-09-21: the library brands
                                      # its text selection, light and dark chips;
                                      # 56,514 the same night: cross-document view
                                      # transitions join the two worlds, wordmark
                                      # named on both sides;
                                      # 58,263 the next morning: the library's
                                      # blocks arrive on the landing's clock, one
                                      # multiplier in this shared stylesheet and
                                      # the fold test in the shared script;
                                      # 59,140 the same morning: the seven group
                                      # marks get their one sizing rule here,
                                      # because 76 pages draw them and a rule
                                      # copied into 75 pages stops agreeing;
                                      # 67,945 that same day: the search palette —
                                      # the header trigger's rule, the dialog's
                                      # own type and grounds, and the four
                                      # measured ratios that chose the mark's
                                      # colour over the accent it was drawn in,
                                      # which verify-links recomputes;
                                      # 70,301 later that day: the temperature
                                      # page's slider, one component — the
                                      # control's own type, its platform accent
                                      # and the guard that keeps it off the
                                      # printed sheet
ARTIFACT_FILES = 147                  # 138 + the four phone crops' 16 files + the library
                                      # index, less exhibit-12's eight retired exports
                                      # (9 exhibits x 4 files = 36, was 3 x 6 = 18) + /theme.js
                                      # - 4 on 2026-09-21: exhibit-13 retired, act 5's table
                                      # now a DOM replica (the second exhibit to make that move)
                                      # + 2 on 2026-09-21: /search.js and /search-index.json,
                                      # the patch of library a reader can search from
                                      # any page in it
                                      # + 1 on 2026-09-21: /temperature-dial.js, the
                                      # temperature page's control — the first file
                                      # here that is one page's rather than every
                                      # page's, which is why the budget names it

# Check 8's marker. If the assembler ever globs OldVersion/ instead of copying by
# allowlist, the previous home page ships at this path and every other check here
# still passes. This string is the only thing standing between that and a deploy.
HOME_MARKER = "It shows you what it saw"

# Check 7. EMPTY, and that is a v2 result rather than an omission.
#
# Under v1 this held U+2192 (RIGHTWARDS ARROW), which the copy deck spelled eight
# times and which no shipped subset carried — Inter's 230 glyphs have no arrow,
# and neither Didot file does. `unicode-range` chooses among files that HAVE a
# glyph, so declaring it would render tofu; falling through to the system stack
# was correct.
#
# v2's copy deck has no arrow, so nothing falls through and the set is empty.
# The check still asserts it EXACTLY rather than dropping the assertion: an empty
# allow-list that must stay empty is what catches the next unsubsetted codepoint,
# and a check deleted for being empty would catch nothing at all.
FALLS_THROUGH: dict[int, str] = {}

# Check 6. v2's §4, and every figure below was MEASURED from this stylesheet's
# own tokens rather than transcribed from the plan — a plan's rounded figure is a
# description of a ratio, and this is the ratio.
#
# Two pairs are worth reading:
#   * --on-azure on --azure is the CTA, so it is the one ratio a visitor reads
#     text through on every screen of the page.
#   * text in the field is measured against --field-hi, the gradient's LIGHTEST
#     stop. Light text on a lighter ground is the worst case; measuring it
#     against --field-base would assert the easiest one and call it the hardest.
CONTRAST = [
    ("--ink", "--paper", 17.04, "§4: all text on paper"),
    ("--ink-2", "--paper", 5.71, "§4: secondary text on paper"),
    ("--azure", "--paper", 5.33, "§4: the accent on paper"),
    ("--on-azure", "--azure", 5.57, "§4: the CTA's ink on the CTA's fill"),
    ("--coral", "--paper", 5.32, "§4: the mark's artwork before it re-inks"),
    ("--field-ink", "--field-hi", 11.58, "§4: text in the field, worst case"),
    ("--field-ink-2", "--field-hi", 6.07, "§4: secondary text in the field"),
    ("--azure-lift", "--field-hi", 5.19, "§4: the accent in the field, worst case"),
    ("--cite-ink", "--cite-wash", 4.74, "§4: the citation numeral on its wash"),
    ("--on-azure-lift", "--azure-lift-hi", 7.72, "§4: the CTA's ink, hovered"),
    # M9's chips are the one control drawn in the WINDOW's scope rather than the
    # page's, so these two are hex literals for the reason above: the pane is
    # dark in both themes, and `--ink-2` resolves differently inside `.win`.
    ("#8B9199", "#111620", 5.70,
     "the hero chip's label at rest, on the pane's LIGHTEST stop"),
    ("#E5E8EE", "#303033", 10.72,
     "the hero chip's label on the active question, on --fill-card over the pane"),
]

# Asserted to FAIL, so the reasons recorded beside the tokens cannot rot into
# descriptions of pairs that would actually have been fine.
CONTRAST_BELOW_AA = [
    ("--azure-lift", "--cite-wash", 2.23, "why the citation wash keeps the light blue"),
    ("--on-azure", "--azure-lift", 2.63, "why the chip fills with --azure, not --azure-lift"),
    ("--state-ready", "--paper", 2.45, "why --state-ready is a DOT and never text"),
]

AA_NORMAL = 4.5

EXTERNAL_SCHEMES = ("http://", "https://", "mailto:", "tel:", "data:", "//")


class Report:
    """Collects pass/fail lines so one run reports everything, not just the first.

    Deliberately a copy of verify-budget.py's: the two scripts are separate
    entry points named by the build plan, and a shared module for fifteen lines
    would be a third file to keep in step with both.
    """

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


# ------------------------------------------------------------------- text prep

def strip_css_comments(text: str) -> str:
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def rendered_text(page: str) -> str:
    """The page with its comments gone, what a font could actually be asked for.

    Comments are stripped and the `<style>` block is KEPT, because CSS reaches
    the screen through `content:` as surely as markup does: the `.pipe` arrows
    on this page exist only as `content: "→"`. Check 7 counts those.
    """
    return strip_css_comments(strip_html_comments(page))


def visible_text(page: str) -> str:
    """Return visitor-facing HTML text, excluding code, styles and comments."""
    text = re.sub(r"<script\b.*?</script>", "", page, flags=re.S | re.I)
    text = re.sub(r"<style\b.*?</style>", "", text, flags=re.S | re.I)
    text = strip_html_comments(text)
    return re.sub(r"<[^>]+>", " ", text)


# --------------------------------------------------------------- the plan, as data

REPO = HERE.parent.parent                  # the checkout, from Source/tools/
PLAN_DOC = REPO / "Documentation" / "SITE_DESIGN_PLAN_V2.md"
DOCUMENTS = [PLAN_DOC, REPO / "README.md", REPO / "Documentation" / "OVERNIGHT_GOALS.md"]

# The string that makes §2's table THE TABLE: a reformat that breaks this line is a
# failure to re-point the check, not a silent skip. It is the header of the table
# that maps every act to its anchor id, its built headline and its exhibit.
PLAN_TABLE_HEAD = "| # | Act, by anchor id |"


def norm_text(s: str) -> str:
    """One comparable form for a string that exists in two files.

    NFC because act 11's heading is a Greek word carrying a breathing mark and an
    iota subscript: the same word written from a different keyboard can be a
    different byte sequence, and that would be a failure with nothing wrong behind
    it, which is how a check earns the reputation that gets it deleted.
    """
    s = htmllib.unescape(re.sub(r"<[^>]+>", "", s))
    return unicodedata.normalize("NFC", re.sub(r"\s+", " ", s)).strip()


def plan_act_rows() -> list[list[str]] | None:
    """§2's table as data: one row of cells per numbered act.

    None means the document or the table's header is gone. Callers report that as a
    failure rather than skipping, because a check that goes quiet when its subject
    is renamed is worse than no check: nothing else in this file reads the plan.
    """
    if not PLAN_DOC.exists():
        return None
    rows: list[list[str]] = []
    inside = False
    for line in PLAN_DOC.read_text(encoding="utf-8").splitlines():
        if line.startswith(PLAN_TABLE_HEAD):
            inside = True
            continue
        if inside:
            if not line.startswith("|"):
                break
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and cells[0].isdigit():
                rows.append(cells)
    return rows or None


# ------------------------------------------------------------------ css parsing

def css_rules(text: str, inside: str = "") -> list[tuple[str, str, str]]:
    """Every rule as (selector, body, enclosing at-rule), comments removed.

    A small recursive walk rather than a regex: the reduced-motion block nests
    rules inside an @media, and check 5 has to know whether a declaration is in
    there. No declaration on this page contains a brace or a quoted brace, so
    counting braces is sound for this input; it would not be for all CSS.
    """
    text = strip_css_comments(text)
    rules: list[tuple[str, str, str]] = []
    i = 0
    while True:
        j = text.find("{", i)
        if j < 0:
            return rules
        close = text.find("}", i)
        if 0 <= close < j:                      # stray `}` — skip it
            i = close + 1
            continue
        prelude = text[i:j].strip()
        depth, m = 1, j + 1
        while m < len(text) and depth:
            if text[m] == "{":
                depth += 1
            elif text[m] == "}":
                depth -= 1
            m += 1
        body = text[j + 1:m - 1]
        if prelude.startswith("@"):
            inner = f"{inside} {prelude}".strip()
            rules += css_rules(body, inner)
        else:
            rules.append((prelude, body, inside))
        i = m


def declarations(body: str) -> list[tuple[str, str]]:
    """(property, value) pairs from one rule body, `!important` kept."""
    out = []
    for chunk in body.split(";"):
        if ":" not in chunk:
            continue
        prop, value = chunk.split(":", 1)
        out.append((prop.strip().lower(), value.strip()))
    return out


def token_block(css: str, selector: str) -> dict[str, str]:
    """The custom properties declared by one selector, as written."""
    for sel, body, inside in css_rules(css):
        if sel == selector and not inside:
            out = {}
            for prop, value in declarations(body):
                if prop.startswith("--"):
                    out[prop] = value
            return out
    return {}


def hex_of(value: str, tokens: dict[str, str], depth: int = 0) -> str | None:
    """Resolve a token or hex literal to #RRGGBB, following var() aliases."""
    value = value.strip()
    m = re.fullmatch(r"var\(\s*(--[a-z0-9-]+)\s*\)", value)
    if m:
        if depth > 8 or m.group(1) not in tokens:
            return None
        return hex_of(tokens[m.group(1)], tokens, depth + 1)
    m = re.fullmatch(r"#([0-9A-Fa-f]{6})", value)
    return f"#{m.group(1).upper()}" if m else None


# ------------------------------------------------------------------- contrast

def _channel(c: int) -> float:
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex6: str) -> float:
    h = hex6.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# -------------------------------------------------------------- unicode ranges

def declared_codepoints(css: str) -> set[int]:
    """Every codepoint the stylesheet's `unicode-range`s claim, as a set.

    The union across faces, not per face: a character is reachable if ANY
    shipped file can draw it, and which file is chosen is the browser's business.
    """
    out: set[int] = set()
    for value in re.findall(r"unicode-range\s*:([^;}]+)", strip_css_comments(css)):
        for part in value.split(","):
            part = part.strip()
            if not part.upper().startswith("U+"):
                continue
            body = part[2:].strip()
            if "?" in body:                      # wildcard form, unused here
                lo = int(body.replace("?", "0"), 16)
                out.update(range(lo, lo + 16 ** body.count("?")))
            elif "-" in body:
                a, b = body.split("-", 1)
                out.update(range(int(a, 16), int(b, 16) + 1))
            else:
                out.add(int(body, 16))
    return out


# ------------------------------------------------------------------ references

ATTR = re.compile(
    r"""\b(?:href|src)\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.I
)
SRCSET = re.compile(r"""\bsrcset\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.I)
CSS_URL = re.compile(r"""url\(\s*(?:"([^"]*)"|'([^']*)'|([^)'"]+))\s*\)""", re.I)


def refs_in(path: pathlib.Path, text: str) -> list[str]:
    """Every URL a file asks the browser to fetch, in document order."""
    out: list[str] = []
    if path.suffix.lower() == ".css":
        for m in CSS_URL.finditer(strip_css_comments(text)):
            out.append(next(g for g in m.groups() if g is not None))
        return out
    if path.suffix.lower() not in (".html", ".htm"):
        return out
    for m in ATTR.finditer(text):
        out.append(htmllib.unescape(next(g for g in m.groups() if g is not None)))
    # srcset is a comma-separated list of "url descriptor" pairs.
    for m in SRCSET.finditer(text):
        raw = htmllib.unescape(next(g for g in m.groups() if g is not None))
        for item in raw.split(","):
            item = item.strip()
            if item:
                out.append(item.split()[0])
    return out


def resolve(site: pathlib.Path, ref: str, from_file: pathlib.Path
            ) -> tuple[pathlib.Path | None, str | None, bool]:
    """Resolve one URL against the artifact.

    Returns (target file, fragment, found). `found` is False for a path that is
    not in the artifact. A directory URL resolves to its index.html, and so does
    an extensionless one, because both forms are used in the library.
    """
    frag = None
    if "#" in ref:
        ref, frag = ref.split("#", 1)
    if ref == "":
        return from_file, frag, from_file.is_file()
    if ref.startswith("/"):
        target = site / ref.lstrip("/")
    else:
        target = from_file.parent / ref
    target = pathlib.Path(target)
    if target.is_dir():
        target = target / "index.html"
    elif not target.is_file() and not target.suffix:
        candidate = target / "index.html"
        if candidate.is_file():
            target = candidate
    return target, frag, target.is_file()


def ids_in(text: str) -> set[str]:
    """Every id= (and legacy name=) in a document, for fragment targets."""
    out = set(re.findall(r"""\bid\s*=\s*["']([^"']+)["']""", text))
    out |= set(re.findall(r"""\bname\s*=\s*["']([^"']+)["']""", text))
    return out


# ---------------------------------------------------------------------- checks

def check_4(rep: Report, site: pathlib.Path, docs: dict[pathlib.Path, str]) -> None:
    print("4  every internal href/src resolves")
    broken: list[str] = []
    refs = 0
    for path, text in docs.items():
        for ref in refs_in(path, text):
            if not ref or ref.startswith(EXTERNAL_SCHEMES) or ref.startswith("{"):
                continue
            refs += 1
            target, frag, found = resolve(site, ref, path)
            rel = path.relative_to(site).as_posix()
            if not found:
                broken.append(f"{rel} -> {ref}")
                continue
            if frag:
                # The fragment has to exist in whichever document it lands in.
                if frag not in ids_in(text if target == path
                                      else docs.get(target, target.read_text(
                                          encoding="utf-8", errors="replace"))):
                    broken.append(f"{rel} -> {ref} (no id=\"{frag}\")")
    if broken:
        for b in broken[:20]:
            rep.fail("broken reference", b)
        if len(broken) > 20:
            rep.fail("broken reference", f"and {len(broken) - 20} more")
    else:
        rep.ok(f"{refs} references across {len(docs)} documents",
               "every path and every fragment resolves")


def check_5(rep: Report, page: str) -> None:
    """The composition gate, and the page's behaviour contract.

    Order matters here: the composition assertions come FIRST, because they are
    the ones that would have caught v1.

    v1 passed 53 green assertions on a page that read as a blog post. Every one
    of them was true — every byte accounted for, every link resolving, every
    contrast pair measured, every heading in order — and not one of them could
    see that the result was nine identical sections of prose with three pictures
    in it. Green checks are not a design review.

    This check cannot judge whether the page is any *good*. It can fail a page
    that has quietly collapsed back into v1's shape, which is the failure that
    actually happened, and it is the only assertion in this file that is about
    the design rather than about the bytes.
    """
    print("\n5  composition, then behaviour (landing page only)")
    body = strip_html_comments(page)

    # ---- the composition gate (§3, §2) ------------------------------------
    acts = re.split(r"(?=<section\b)", body, flags=re.I)[1:]
    if len(acts) != 12:
        rep.fail("section count", f"{len(acts)} <section> elements — §2's architecture "
                                  f"has twelve acts, and a page that has collapsed back "
                                  f"to a handful is v1 again. An act added or removed is "
                                  f"§2's table's edit to make, in the same commit, which "
                                  f"is why this is exact rather than a floor")
    else:
        rep.ok("12 sections", "§2's acts are present")

    # ---- §2's table, read against the page ---------------------------------
    # This is the drift that actually happened, and it lasted a week: §2's table
    # listed ten acts under a prose line that said eleven, on a page that shipped
    # twelve, with every assertion in this file green — because the table is a
    # claim about this file and nothing here was reading it. Counting sections
    # cannot catch a table that describes a different page.
    #
    # So the table is read as DATA. Three things are asserted, and each is a way
    # the plan and the page can disagree while both look fine:
    #
    #   * the row count, which is the "eleven acts" bug itself;
    #   * each row's anchor id against the act's own `id`, because the ids are what
    #     the nav, the hero's rail and the ring's plate link to — the table is
    #     where a renamed one would be documented wrongly;
    #   * each row's headline against the act's real <h1>/<h2>, because the table
    #     paraphrased them, and a paraphrase is how a 12-word headline sat under a
    #     rule that allows seven.
    rows = plan_act_rows()
    if rows is None:
        rep.fail("§2's table is readable",
                 f"{PLAN_DOC.name} is missing, or its table no longer starts with "
                 f"{PLAN_TABLE_HEAD!r}. This check reads that table as data, so a "
                 f"reformat has to re-point it rather than pass quietly")
    elif len(rows) != len(acts):
        rep.fail("§2's table matches the page",
                 f"the plan lists {len(rows)} acts against {len(acts)} sections — the "
                 f"table and the page are describing different pages, which is the "
                 f"exact failure this check exists for")
    else:
        wrong_head, wrong_id, missing_ex = [], [], []
        for i, cells in enumerate(rows, start=1):
            chunk = acts[i - 1]
            m = re.search(r"<h[12]\b[^>]*>(.*?)</h[12]>", chunk, re.S | re.I)
            page_head = norm_text(m.group(1)) if m else "(no heading)"
            if page_head != norm_text(cells[2]):
                wrong_head.append(f"act {i}: plan {cells[2]!r} vs page {page_head!r}")
            want = re.search(r"#([A-Za-z][\w-]*)", cells[1])
            has = re.search(r"<section\b[^>]*\bid\s*=\s*[\"']([^\"']*)[\"']",
                            chunk, re.I)
            if want and (not has or has.group(1) != want.group(1)):
                wrong_id.append(f"act {i}: plan #{want.group(1)} vs page "
                                f"{'#' + has.group(1) if has else '(no id)'}")
            if not want and has:
                wrong_id.append(f"act {i}: plan says no id, page has #{has.group(1)}")
            product = cells[5] if len(cells) > 5 else ""
            for ex in sorted(set(re.findall(r"exhibit-\d+", product))):
                if f"/img/{ex}" not in body:
                    missing_ex.append(f"act {i}: {ex} is not on the page")
        if wrong_head:
            rep.fail("§2's headlines are the page's",
                     "; ".join(wrong_head) + " — the table has to quote the built "
                     "markup rather than paraphrase it, because the paraphrase is "
                     "where the length rule went unchecked")
        else:
            rep.ok("§2's headlines are the page's", f"{len(rows)} rows, read from the plan")
        if wrong_id:
            rep.fail("§2's anchor ids are the page's", "; ".join(wrong_id))
        else:
            rep.ok("§2's anchor ids are the page's", "every id in the table is on the act it names")
        if missing_ex:
            rep.fail("§2's exhibits are the page's", "; ".join(missing_ex))
        else:
            rep.ok("§2's exhibits are the page's", "every exhibit the table names is in the markup")

    # ---- the rhythm gate (§2, report #12) ---------------------------------
    # §2 opens by claiming the page alternates its compositions deliberately, and
    # the report ranks alternation #12 — its example is Gemini Notebook, called the
    # least memorable of the five "despite having the best single element".
    #
    # Nothing measured that claim until this block. What it cost is worth stating:
    # the gate counted sections while §2's table listed ten acts under a prose line
    # that said eleven, and the page had twelve. Every assertion was green and the
    # one document that describes the design described a different page. A claim
    # about a reader is not a claim about markup, but these two are read off the
    # built markup and are what makes the claim true:
    #
    #   * **The paired acts alternate side.** That is C2's entire contribution. Two
    #     in a row on the same side is the zig-zag collapsing into a column.
    #   * **No more than five consecutive acts share one ground.** The page measures
    #     D P P P P P D P P P P D — runs of five and four. The report's rule is
    #     "every third changes the ground or accent", and five is where this page
    #     lands, so five is the number asserted: the failure is a SIXTH paper act in
    #     a row, which is the run length the page's own evidence says reads as a
    #     list. Asserting three would fail a page that already works.
    ground, flips = [], []
    for chunk in acts:
        tag = re.search(r"<section\b[^>]*>", chunk, re.I)
        attr = ""
        if tag:
            cls = re.search(r"""\bclass\s*=\s*["']([^"']*)["']""", tag.group(0), re.I)
            attr = cls.group(1) if cls else ""
        ground.append("D" if re.search(r"\b(field|poster)\b", attr) else "P")
        if re.search(r"""\bclass\s*=\s*["'][^"']*\bsplit\b[^"']*["']""", chunk, re.I):
            flips.append(bool(re.search(
                r"""\bclass\s*=\s*["'][^"']*\bsplit\b[^"']*\bis-flip\b""", chunk, re.I)))
    sequence = "".join(ground)

    runs, cur = [], 1
    for i in range(1, len(ground)):
        if ground[i] == ground[i - 1]:
            cur += 1
        else:
            runs.append(cur)
            cur = 1
    runs.append(cur)
    longest = max(runs)
    if longest > 5:
        rep.fail("ground rhythm", f"{longest} acts in a row on one ground ({sequence}) — "
                                   f"§2's page has never run longer than five, and a "
                                   f"longer run is the page reading as a list")
    else:
        rep.ok("ground rhythm", f"{sequence} — longest run {longest}, alternates "
                                 f"{len(runs) - 1} times")

    same_side = [i for i in range(1, len(flips)) if flips[i] == flips[i - 1]]
    if len(flips) < 4 or same_side:
        rep.fail("C2 alternates side", f"{len(flips)} paired acts, sides "
                                       f"{[int(f) for f in flips]}"
                                       + (f", same side at {same_side}" if same_side else "")
                                       + " — §3's C2 is a zig-zag or it is a column")
    else:
        rep.ok("C2 alternates side", f"{len(flips)} paired acts, sides "
                                     f"{[int(f) for f in flips]}")

    # The five compositions are C1 field-full, C2 split, C3 pair, C4 band,
    # C5 poster. A page using one of them everywhere is a document; the whole
    # point of §3 is that the page alternates.
    # Scanned across every class attribute in the body, not just the ones on
    # <section>. C2's grid has to sit on a wrapper (the section is full-bleed and
    # the grid is inside the page's width), so a `split` that only ever appears on
    # an inner element is still the page using C2. The assertion is "the page uses
    # N of the five", which a document-shaped page fails either way.
    classes = set()
    for attr in re.findall(r"""\bclass\s*=\s*["']([^"']*)["']""", body, re.I):
        for name in ("field", "split", "pair", "band", "poster"):
            if re.search(rf"\b{name}\b", attr):
                classes.add(name)
    if len(classes) < 4:
        rep.fail("composition variety", f"{sorted(classes)} — §3 names five "
                                        f"compositions and the page must use at "
                                        f"least four of them")
    else:
        rep.ok(f"{len(classes)} compositions in use", ", ".join(sorted(classes)))

    # Nine exhibits, of which seven are captures. Act 4's is the DOM reading log
    # since 2026-09-20 and act 5's is the DOM dispute table since 2026-09-21, so
    # this asserts ALL halves rather than lowering the count: seven <picture>
    # elements, and the two live replicas that replaced the others. A count alone
    # would let a replacement slide back to a bitmap unnoticed, which is the one
    # thing this set of checks exists to prevent.
    pictures = len(re.findall(r"<picture\b", body, re.I))
    if pictures < 7:
        rep.fail("exhibit count", f"{pictures} <picture> elements — §6 ships seven captures")
    else:
        rep.ok(f"{pictures} exhibits", "§6's capture set is present")
    if 'class="win win-readlog"' not in body:
        rep.fail("the reading log", "act 4's live log is missing — §6.2 ships it as the "
                                    "page's second DOM replica, not a capture")
    else:
        rep.ok("the reading log", "act 4's exhibit is the live log, not a bitmap")
    if 'class="win win-dispute"' not in body:
        rep.fail("the dispute table", "act 5's live table is missing — §6.2 ships it as the "
                                      "page's third DOM replica, not a capture")
    else:
        rep.ok("the dispute table", "act 5's exhibit is the live table, not a bitmap")

    # v1 shipped the FAQ as a plain <dl> and wrote a comment explaining that an
    # accordion "would hide precisely the answers this audience came for". Every
    # reference site has one. This asserts the reversal stuck.
    if "<details" not in body:
        rep.fail("no <details>", "§12: the FAQ is an accordion on <details>, and "
                                 "v1's refusal to build one is what v2 reverses")
    else:
        rep.ok(f"{body.count('<details')} <details>",
               "the FAQ is a real disclosure, not a list")

    # And the hero's two reserved answers are among them, which is a claim about a
    # reader rather than about markup: the refusal demonstrates the promise the
    # rest of the page asks to be taken on trust, and it used to sit behind a
    # click that only script could answer. The audit's scriptless pass found that;
    # this keeps it found. Checked by walking the disclosure blocks rather than by
    # looking for the ids anywhere on the page, because the ids are also what the
    # chips point at once the script has moved the answers into the pane.
    reserved = ("ans-who", "ans-inscriptions")
    opened = set()
    for block in re.findall(r'<details class="hero-more"[^>]*>(.*?)</details>', page, re.S):
        for name in reserved:
            if f'id="{name}"' in block:
                opened.add(name)
    if opened == set(reserved):
        rep.ok("the hero's reserved answers are disclosures",
               "reachable with no script")
    else:
        rep.fail("the hero's reserved answers",
                 f"{sorted(set(reserved) - opened)} are not inside a `details.hero-more`, "
                 "so the refusal a reader is told to trust is unreachable with no script")

    if not re.search(r"position\s*:\s*sticky", page):
        rep.fail("no sticky element", "§9: the nav is sticky — v1's only nav was "
                                      "painted inside a screenshot")
    else:
        rep.ok("the nav is sticky", "§9")

    # §5: the display size is spent ONCE. v1 topped out at 68px and reused it;
    # the top tier of the reference set runs 5.3-6.4x over body, the two sites
    # that feel most web-default run 3.0-3.1x. One use is what buys the ratio.
    display_uses = len(re.findall(r"var\(\s*--t-display\s*\)", page))
    if display_uses != 1:
        rep.fail("display size", f"--t-display is used {display_uses} times — §5 "
                                 f"spends it once, on the h1")
    else:
        rep.ok("the display size is spent once")

    # ---- the behaviour contract ------------------------------------------
    #
    # v2 responds to clicks on purpose — the citation chips are operable and the
    # FAQ is a disclosure — so the v1 prohibition is gone. What replaces it is a
    # narrower rule: the page's ONE script must stay small, inline, and incapable
    # of being the reason anything works.
    # AMENDED 2026-09-21 for the library's search palette: the rule this check
    # keeps is that the page's OWN behaviour is one inline script that nothing
    # depends on, and that has not changed. What the landing now also carries is
    # one external, deferred file - /search.js, the same file all 75 carried pages
    # name - and the exception is written as a name rather than as a count, so a
    # second bundle, a CDN or a font loader cannot slip in behind it.
    scripts = re.findall(r"<script\b[^>]*>(.*?)</script>", body, re.S | re.I)
    tags = re.findall(r"<script\b[^>]*>", body, re.I)
    inline = [t for t in tags if not re.search(r"\bsrc\s*=", t, re.I)]
    external = [t for t in tags if re.search(r"\bsrc\s*=", t, re.I)]
    if len(inline) != 1:
        rep.fail("script count", f"{len(inline)} inline <script> tag(s) — the page's "
                                  f"own behaviour is exactly one")
    elif any('src="/search.js"' not in t for t in external):
        rep.fail("the page's one external script",
                 f"{', '.join(t.strip() for t in external if 'src=\"/search.js\"' not in t)}"
                 f" — the only external file this page may name is the library's "
                 f"search palette")
    elif len(external) > 1:
        rep.fail("the page's one external script",
                 f"{len(external)} <script src> tags, and /search.js is already the "
                 f"one exception")
    else:
        rep.ok("one inline <script> and one shared external one",
               "/search.js, deferred" if external else "no external script needs it")

    src = scripts[0] if scripts else ""

    # Event-handler ATTRIBUTES are still forbidden: they are the shape of
    # behaviour bolted onto markup. The script is scanned separately below, so a
    # variable named `onScroll` is not mistaken for an attribute.
    without_script = re.sub(r"<script\b.*?</script>", "", body, flags=re.S | re.I)
    bad = re.findall(r"\bon[a-z]+\s*=", without_script, re.I)
    if bad:
        rep.fail("event handler attribute", ", ".join(sorted(set(bad))))
    else:
        rep.ok("no event-handler attributes")

    if re.search(r"""\b(?:href|src)\s*=\s*["']\s*javascript:""", body, re.I):
        rep.fail("javascript: URL", "the page must not carry one")
    else:
        rep.ok("no javascript: URL")

    # Device sniffing is still forbidden — §16 declares the lighter build in
    # media queries and nowhere else. matchMedia itself is fine; matchMedia
    # asking about anything but the accessibility query is the same sniffing
    # wearing a different API.
    # The ban is on the UA string and the platform, not on measuring the
    # viewport. `getBoundingClientRect().top < innerHeight` asks "is this element
    # below the fold", which is a question about a position, not about a device —
    # and any layout consequence of the answer is still CSS's. Banning innerHeight
    # would have banned the one measurement the reveal needs while permitting the
    # sniffing the rule exists to stop.
    for needle in ("userAgent", "userAgentData", "navigator.platform"):
        if needle in src:
            rep.fail(f"the script uses {needle}",
                     "§16: the lighter build stays declared in media queries, "
                     "never sniffed at run time")
    for query in re.findall(r"""matchMedia\(\s*['"]([^'"]+)['"]""", src):
        if "prefers-reduced-motion" not in query:
            rep.fail("device detection in matchMedia", query)
    if "IntersectionObserver" not in src:
        rep.fail("the script's shape", "it reveals panels and reads scroll "
                                       "position through an IntersectionObserver")
    else:
        rep.ok("the script only observes and toggles")

    # EVERY transition and animation must sit inside the reduced-motion guard.
    # This is the assertion that replaces v1's "one transition, one target": the
    # rule is no longer *how much* motion there is but that all of it is
    # optional. A rule outside the guard runs for a visitor who asked it not to.
    outside: list[str] = []
    inside_count = 0
    for sel, rule_body, inside in css_rules(page):
        moving = [(p, v) for p, v in declarations(rule_body)
                  if p.startswith(("transition", "animation"))]
        if "prefers-reduced-motion" in inside:
            inside_count += len(moving)
        else:
            outside += [f"{sel} {{ {p}: {v} }}" for p, v in moving]
    if outside:
        for o in outside:
            rep.fail("motion outside the reduced-motion guard", o)
    else:
        rep.ok(f"{inside_count} motion declarations",
               "all of them inside @media (prefers-reduced-motion: no-preference)")
    if "prefers-reduced-motion" not in page:
        rep.fail("prefers-reduced-motion", "there is nothing to honour")


def check_6(rep: Report, css: str) -> None:
    print("\n6  contrast")
    # §1's table is the LIGHT theme's, so every pair resolves against `:root`.
    # Reading `.win` or `.world-dark` here is the easy mistake and it is a silent
    # one: `--ink` exists in all three blocks, so merging them turns the first
    # row into white-on-white and reports a confident 1.00:1. A pair that is
    # genuinely dark-scoped is written as a hex literal in the table above, with
    # its reason, rather than looked up.
    tokens = token_block(css, ":root")

    def resolve_token(name: str) -> str | None:
        """A token name or a literal hex -> #RRGGBB, following var() aliases."""
        return name.upper() if name.startswith("#") else hex_of(tokens.get(name, ""), tokens)

    for fg, bg, claimed, why in CONTRAST:
        a, b = resolve_token(fg), resolve_token(bg)
        if a is None or b is None:
            rep.fail(f"{fg} on {bg}", "could not resolve the pair to hex")
            continue
        got = contrast(a, b)
        dp = len(str(claimed).split(".")[1])
        if abs(got - claimed) > (0.005 if dp == 2 else 0.05):
            rep.fail(f"{fg} on {bg}",
                     f"{got:.2f}:1, §1 says {claimed}:1  ({a} on {b})  — {why}")
        else:
            rep.ok(f"{fg} on {bg}", f"{got:.2f}:1  ({a} on {b})")

    for fg, bg, claimed, why in CONTRAST_BELOW_AA:
        a, b = resolve_token(fg), resolve_token(bg)
        if a is None or b is None:
            rep.fail(f"{fg} on {bg}", "could not resolve the pair to hex")
            continue
        got = contrast(a, b)
        if got >= AA_NORMAL:
            rep.fail(f"{fg} on {bg}",
                     f"{got:.2f}:1 — it is above AA, so the token's justification "
                     f"({why}) is no longer true")
        elif abs(got - claimed) > 0.05:
            rep.fail(f"{fg} on {bg}", f"{got:.2f}:1, the comment says {claimed}:1")
        else:
            rep.ok(f"{fg} on {bg} still fails AA", f"{got:.2f}:1  — {why}")

    # The stylesheet's own promise, and it has to be read off the RULES: a scan
    # of raw lines finds every hex named inside a comment, which is most of them.
    strays = []
    for sel, body, inside in css_rules(css):
        for prop, value in declarations(body):
            if prop.startswith("--"):
                continue
            if re.search(r"#[0-9A-Fa-f]{3,8}\b|\brgba?\(", value):
                strays.append(f"{sel} {{ {prop}: {value} }}")
    if strays:
        for s in strays[:10]:
            rep.fail("colour outside a token", s)
    else:
        rep.ok("every colour is a token", "no hex or rgb() in a declaration")


def check_7(rep: Report, page: str, css: str) -> None:
    print("\n7  codepoints")
    declared = declared_codepoints(css)
    rendered = rendered_text(page)
    visible = visible_text(page)
    punctuation = sorted({c for c in visible if c in "—–"})
    if punctuation:
        rep.fail("visible dash punctuation", ", ".join(repr(c) for c in punctuation) +
                 " appears in visitor-facing text; use a comma, colon or full stop")
    else:
        rep.ok("visible copy has no em or en dash")

    # The stricter form, and it is only available now that the page ships without
    # its html comments. Visible text was the RULE; the whole document is the
    # measurement. It is worth having because four dashes used to survive in the
    # inlined stylesheet's header comment and one in the inline script: none of
    # them reaches a visitor, and every one of them makes an auditor scanning the
    # artifact for dashes stop and re-derive why it is allowed. A rule that needs
    # an exception explained is weaker than one that does not.
    somewhere = sorted({c for c in page if c in "—–"})
    if somewhere:
        rep.fail("em or en dash anywhere in the document",
                 ", ".join(repr(c) for c in somewhere) +
                 " — the landing page ships no comment that needs one")
    else:
        rep.ok("no em or en dash anywhere in the document",
               "comments and the inline script included")

    seen = sorted({ord(c) for c in rendered if ord(c) > 127})
    out_of_range = [c for c in seen if c not in declared and c not in FALLS_THROUGH]

    for c in out_of_range:
        rep.fail(f"U+{c:04X}",
                 "outside every declared unicode-range and not allow-listed — it "
                 "renders in a system face, not in a shipped subset")
    if not out_of_range:
        rep.ok(f"{len(seen)} rendered non-ASCII codepoints",
               "all inside a declared unicode-range")

    # The allow-list is asserted EXACTLY. A new entry is a decision, not a
    # convenience: it means a glyph the copy needs cannot be drawn by any subset.
    used = sorted(c for c in seen if c in FALLS_THROUGH)
    if used != sorted(FALLS_THROUGH):
        rep.fail("the fall-through allow-list",
                 f"{[f'U+{c:04X}' for c in used]} rendered, "
                 f"{[f'U+{c:04X}' for c in sorted(FALLS_THROUGH)]} allow-listed")
    else:
        for c in used:
            rep.ok(f"U+{c:04X} falls through by design", FALLS_THROUGH[c])


def check_8(rep: Report, page: str) -> None:
    print("\n8  the home page is the new one")
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S | re.I)
    # The marker is matched against the h1's TEXT: the h1 now carries an inline
    # span around "what it saw" (the hero's one accent), and a tag is not a
    # word. Same normalisation the copy gate's extractor uses.
    h1_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h1.group(1))).strip()         if h1 else ""
    if not h1 or HOME_MARKER not in h1_text:
        found = h1_text[:60] if h1 else "no <h1>"
        rep.fail("_site/index.html",
                 f"does not carry §1.3's marker. Found: {found!r}. The assembler "
                 f"copied the previous home page.")
    else:
        rep.ok("_site/index.html carries the new <h1>", h1_text)


def check_gears(rep: Report, page: str) -> None:
    """The worlds turn now, and this is what has to stay true for them to mesh.

    Two facts live in two places and nothing else joins them. The DRAWINGS
    declare the tooth counts they were generated from (data-gear-a="223",
    data-gear-b="48-left"), and the SCRIPT declares the ratios it applies as the
    reader turns them (var RATIO = 223 / 48). Regenerate a drawing with a
    different count and the script keeps driving the old ratio - the mesh grinds
    at every angle, silently, with every other gate green. That is the failure
    class this file exists for, and the script's own comment already claims the
    fix: the counts are "written as counts rather than as radii so the two files
    cannot disagree". This is the assertion that makes the claim true.

    The second clause is the same argument one step on. The script rotates each
    group about ITS OWN data-*-cx/cy, read from the drawing, so a group that
    loses those attributes writes rotate(x NaN NaN) and the world stops turning
    with no error raised anywhere: the rAF keeps running and the attribute keeps
    being set, to nonsense. A pivot that cannot be parsed is that bug caught at
    build time.

    The third clause is the direction, and it is the one clause whose two
    witnesses are genuinely independent. WHICH WAY does the pinion turn? The
    script answers with an operator: the hero's pinions ride OUTSIDE the great
    wheel so their rotation is negated (-turn * RATIO), while the close's pinion
    rides INSIDE its crown and turns the same way (turn * CLOSE_RATIO). Nothing
    checked that. Flip either sign and the drawing still renders, the ratio
    still matches, the pivots still parse, and every gate stays green while one
    of the two worlds visibly grinds against its teeth.

    The witness is the drawing's own geometry, which cannot be told to lie: two
    meshing gears with the same module have pitch radii in their tooth counts'
    proportions, so a pair either sits at R1+R2 (external: they touch, turning
    opposite ways) or at R1-R2 (internal: one runs inside the other, turning the
    same way). That is measured here from the tooth circles the generator drew
    and the pivots it placed, and the script's sign has to agree with it. This
    is why the clause is worth its bytes: the geometry is not restating the
    script, it is a second opinion from a file the script never writes.
    """
    print("\nthe two worlds")

    def counts(attr: str) -> list[int]:
        return [int(v) for v in re.findall(attr + r"=\"(\d+)", page)]

    worlds = (
        ("hero", counts("data-gear-a"), counts("data-gear-b"),
         r"var RATIO = (\d+) / (\d+)"),
        ("close", counts("data-close-a"), counts("data-close-b"),
         r"var CLOSE_RATIO = (\d+) / (\d+)"),
    )
    for name, wheels, pinions, script_re in worlds:
        if not wheels or not pinions:
            rep.fail(f"the {name}'s gear train",
                     "no data-* tooth counts in the drawing: the script cannot "
                     "be checked against it, and something stopped emitting them")
            continue
        declared = (wheels[0], pinions[0])
        if len(set(wheels)) != 1 or len(set(pinions)) != 1:
            rep.fail(f"the {name}'s gear train",
                     f"its groups disagree with each other: {wheels} / {pinions}. "
                     "One train, one tooth count per gear.")
            continue
        script = re.search(script_re, page)
        if not script:
            rep.fail(f"the {name}'s ratio",
                     "the script no longer declares its ratio in the form this "
                     "check reads — teach it the new form, do not drop the check")
            continue
        told = (int(script.group(1)), int(script.group(2)))
        if told != declared:
            rep.fail(f"the {name}'s ratio is the drawing's",
                     f"the script drives {told[0]}:{told[1]} and the drawing was "
                     f"generated from {declared[0]}:{declared[1]} — every turn "
                     "would grind at every angle")
        else:
            rep.ok(f"the {name}'s ratio is the drawing's",
                   f"{declared[0]}:{declared[1]}, declared on both sides")

    bad = []
    for tag in re.findall(r"<g\b[^>]*data-(?:gear|close)-[ab][^>]*>", page):
        for axis in ("cx", "cy"):
            if not re.search(r'data-(?:gear|close)-' + axis + r'="[-\d.]+"', tag):
                bad.append(f"{re.search(r'data-(?:gear|close)-[ab][^=]*="[^"]*"', tag).group(0)} "
                           f"has no data-*-{axis}")
    if bad:
        for b in bad[:6]:
            rep.fail("a turned group's pivot", b + " — the script reads it from the drawing")
    else:
        rep.ok("every turned group carries its pivot",
               "cx and cy, so the rotation cannot be written around NaN")

    # ---- the direction, measured from the drawing and compared to the operator.
    # Every group has to be MEASURABLE, not merely present. A group whose tooth
    # circle goes missing is dropped from the comparison below, and with two
    # pinions in the hero the other one would keep the check passing while one
    # of them stopped being looked at at all - the exact shape of a check that
    # cannot fail. So an unmeasurable group is a failure in its own right.
    groups: dict[tuple[str, str], list[tuple[float, float, float]]] = {}
    unmeasured: list[str] = []
    for m in re.finditer(r"<g\b([^>]*data-(gear|close)-([ab])=\"[^\"]*\"[^>]*)>(.*?)</g>",
                         page, re.S):
        attrs, family, which, body = m.group(1), m.group(2), m.group(3), m.group(4)
        cx = re.search(r'data-(?:gear|close)-cx="([-\d.]+)"', attrs)
        cy = re.search(r'data-(?:gear|close)-cy="([-\d.]+)"', attrs)
        tooth = re.search(r'<circle\b[^>]*class="(?:gear|cg)-tooth"[^>]*\br="([\d.]+)"', body)
        label = re.search(r'data-(?:gear|close)-[ab]="[^"]*"', attrs).group(0)
        if not (cx and cy and tooth):
            unmeasured.append(label)
            continue
        groups.setdefault((family, which), []).append(
            (float(cx.group(1)), float(cy.group(1)), float(tooth.group(1))))
    for label in unmeasured:
        rep.fail(f"the pitch circle of {label}",
                 "the group has no tooth circle (or no pivot) to take a pitch "
                 "radius from, so which way it turns cannot be checked")

    # (script's ratio name, the negated form, the same-direction form)
    operators = {
        "hero": ("RATIO", r"-\s*turn \* RATIO", r"(?<![-\w])turn \* RATIO"),
        "close": ("CLOSE_RATIO", r"-\s*turn \* CLOSE_RATIO", r"(?<![-\w])turn \* CLOSE_RATIO"),
    }
    for world, family in (("hero", "gear"), ("close", "close")):
        big = groups.get((family, "a"), [])
        small = groups.get((family, "b"), [])
        if not big or not small:
            rep.fail(f"the {world}'s mesh direction",
                     "a group has no tooth circle to measure a pitch radius from, so "
                     "which way its pinion turns cannot be checked")
            continue
        r1 = big[0][2]
        for (x1, y1, _) in big:
            for (x2, y2, r2) in small:
                d = math.hypot(x2 - x1, y2 - y1)
                external, internal = abs(d - (r1 + r2)), abs(d - (r1 - r2))
                if min(external, internal) > 0.5:
                    rep.fail(f"the {world}'s mesh is a mesh",
                             f"the pivots are {d:.2f} apart while the pitch radii say "
                             f"{r1 + r2:.2f} (external) or {r1 - r2:.2f} (internal) - "
                             "neither, so one of the two moved without the other")
                    break
                kind = "external" if external < internal else "internal"
                name, negated_re, same_re = operators[world]
                negated = bool(re.search(negated_re, page))
                same = bool(re.search(same_re, page))
                if not (negated or same):
                    rep.fail(f"the {world}'s mesh direction",
                             f"the script no longer writes its pinion's turn in the form "
                             f"this check reads (a `turn * {name}` term) - teach it the "
                             "new form, do not drop the check")
                    break
                wants_negated = kind == "external"
                if negated != wants_negated:
                    rep.fail(f"the {world}'s pinion turns the way its geometry says",
                             f"the drawing measures an {kind} mesh ({d:.2f} = "
                             f"{r1:.2f} {'+' if wants_negated else '-'} {r2:.2f}), which "
                             + ("turns the pinion the OPPOSITE way" if wants_negated
                                else "turns the pinion the SAME way")
                             + ", and the script "
                             + ("turns it" if negated else "does not turn it")
                             + " that way: one of the two worlds would grind")
                else:
                    rep.ok(f"the {world}'s pinion turns the way its geometry says",
                           f"{kind}: {d:.2f} = {r1:.2f} "
                           f"{'+' if wants_negated else '-'} {r2:.2f}, and the script "
                           + ("negates" if negated else "does not negate") + " the ratio")
                break    # M22 - the dwell's tick is the drawing's pitch. The stillness clock steps
    # the wheel 360 over 223 degrees per tick, which is one tooth of the great
    # wheel the generator drew, and the page's comment says verify-links holds
    # that equality. A check that existed only in a comment is a wish, so here
    # it is: the constant the script multiplies its ticks by must be 360 over
    # the drawing's own declared tooth count, and the tick must go through the
    # same writer the scroll and the hand use (heroFreeTurn plus writeHero),
    # because a second writer would be a second source of truth for the angle.
    hero_teeth = counts("data-gear-a")
    dwell = re.search(r"var DWELL_TOOTH = 360 / (\d+)", page)
    if not dwell:
        rep.fail("the dwell's tooth is the drawing's",
                 "the script no longer declares its tick in the form this check "
                 "reads (var DWELL_TOOTH = 360 / N) - teach it the new form, do "
                 "not drop the check")
    elif not hero_teeth:
        rep.fail("the dwell's tooth is the drawing's",
                 "no hero tooth count to hold the constant against")
    else:
        n = int(dwell.group(1))
        if n != hero_teeth[0]:
            rep.fail("the dwell's tooth is the drawing's",
                     f"the dwell steps 360/{n} per tick and the great wheel was "
                     f"generated from {hero_teeth[0]} teeth - a tick would be "
                     "between the teeth, which is what a mesh must never do")
        else:
            rep.ok("the dwell's tooth is the drawing's",
                   f"360/{n} per still tick, the great wheel's own pitch")
    for frag, what in (("dwellArm();", "the scroll re-arms the dwell clock"),
                       ("dwellStop();", "the hand defers the dwell clock"),
                       ("heroFreeTurn += DWELL_TOOTH;",
                        "the tick goes through the one writer")):
        if frag not in page:
            rep.fail(what,
                     f"the page no longer contains {frag!r}, which the dwell's "
                     "claims are built on")
        else:
            rep.ok(what, "present")


def check_poster_mark(rep: Report, page: str, css: str) -> None:
    """The close's wordmark carries its own ground with it.

    The crown's tick ring passes at the letters' mid-height in full primary ink,
    because the wheel is the subject and does not dim for the type. The type
    brings the separation instead: a ::before layer behind the fill, spelled by
    `content: attr(data-mark)` and stroked in the field's own base colour. That
    spelling is the coupling this check exists for, because it fails in the
    worst way a CSS coupling can fail: rename the attribute in either file and
    `attr()` resolves to nothing, the halo silently disappears, and every other
    gate stays green while the letters go back to blue-on-pale.

    Three clauses: the paragraph's data-mark is the string the paragraph spells;
    the stylesheet's halo reads that attribute by name and sits BEHIND the fill
    (a rim painted over the letters would be the defect it exists to fix); and
    the print world remaps the stroke to paper, because the rim is the field's
    ground by construction and the print world strips that ground.
    """
    print("\nthe close's rim")
    mark = re.search(r'<p class="poster-mark"[^>]*>', page)
    if not mark:
        rep.fail("the close's rim", "the poster's mark is not in the artifact")
        return
    declared = re.search(r'data-mark="([^"]+)"', mark.group(0))
    body = re.search(r'<p class="poster-mark"[^>]*>(.*?)</p>', page, re.S)
    if not body:
        rep.fail("the close's rim", "the mark's body could not be read")
        return
    spelled = re.sub(r"<[^>]+>", "", body.group(1)).strip()
    if not declared:
        rep.fail("the close's rim",
                 "the mark carries no data-mark, so the halo's content: attr() "
                 "resolves to nothing and the rim is silently gone")
    elif declared.group(1) != spelled:
        rep.fail("the close's rim",
                 f"data-mark spells {declared.group(1)!r} and the mark spells "
                 f"{spelled!r} — the halo would draw the wrong word")
    else:
        rep.ok("the close's rim", f"the halo spells what the mark spells: {spelled!r}")

    rule = re.search(r"\.poster-mark::before\s*{([^}]*)}", css)
    if not rule:
        rep.fail("the close's rim", "the stylesheet draws no halo for the mark")
        return
    block = rule.group(1)
    if "attr(data-mark)" not in block:
        rep.fail("the close's rim",
                 "the halo no longer reads data-mark — renamed on one side of "
                 "this pair, it disappears without an error anywhere")
    elif "-webkit-text-stroke" not in block:
        rep.fail("the close's rim", "the halo layer carries no stroke to draw")
    elif "z-index: -1" not in block:
        rep.fail("the close's rim",
                 "the halo is not behind the fill — a rim painted over the "
                 "letterforms is the defect it exists to fix")
    else:
        rep.ok("the close's rim",
               "one halo layer, behind the fill, spelled by the attribute it "
               "shares with the paragraph")

    printed = css[css.index("@media print"):]
    if "-webkit-text-stroke-color" not in printed:
        rep.fail("the rim on paper",
                 "the print world never remaps the stroke, and the rim is the "
                 "field's ground by construction — a ground that cannot print "
                 "is not a ground")
    else:
        remap = re.search(r"\.poster-mark::before\s*{[^}]*-webkit-text-stroke-color:\s*([^;}]+)",
                          printed)
        if not remap or "paper" not in remap.group(1):
            rep.fail("the rim on paper",
                     f"the print world remaps the stroke to {remap.group(1).strip()!r} "
                     "if at all, and it has to be the sheet's own paper")
        else:
            rep.ok("the rim on paper", f"the halo prints as {remap.group(1).strip()}")


def check_momentum(rep: Report, source: str, page: str) -> None:
    """The numbers the notes quote, recomputed from the constants they describe.

    Every other clause in this file compares one artifact against another. This
    one compares the PAGE against its own account of itself, which is the only
    promise in the project that nothing was checking: the notes above the script
    state the wheel's speed cap and half-life, the sweep a hard flick carries,
    the time it takes to settle, and the degrees the reader's scroll maps to.
    Every one of those is arithmetic on constants in the file below them, and
    every one of them can quietly become a lie the moment somebody tunes the
    motion.

    It already had, twice. The notes said a flick "settles in under a second"
    while the arithmetic gave 1.13s at the cap of the day. And later the cap
    itself was wrong: 200 deg/s is 3.33 deg a frame, against a great wheel whose
    tooth pitch is 360/223 = 1.61 deg, so the fastest the wheel could be driven
    advanced 2.1 teeth between frames and the dashed teeth aliased into a strobe
    on 18% of the frames of an extreme throw. The cap is 96 now, which is one
    tooth a frame, and the last clause below holds it there against the tooth
    count the DRAWING declares rather than against a number written in the note.
    That is the whole point of the check: constants named once in the script, the
    quoted numbers read out of the prose, the derived quantities computed here,
    and the tune held against the artifact it draws. If the prose changes shape
    the check fails and says so rather than passing silently, which is how the
    ratio clause behaves too.
    """
    print("\nthe momentum the notes quote")

    named = re.search(r"var SPIN_CAP = ([\d.]+), SPIN_HALF = ([\d.]+), SPIN_MIN = ([\d.]+);",
                      source)
    if not named:
        rep.fail("the momentum is named once",
                 "the script no longer declares SPIN_CAP/SPIN_HALF/SPIN_MIN in the "
                 "form this check reads — teach it the new form, do not drop the check")
        return
    cap, half, floor = (float(g) for g in named.groups())
    rep.ok("the momentum is named once",
           f"cap {cap:g} deg/s, half-life {half:g}ms, settled under {floor:g} deg/s")

    # One cap and one half-life, used by every input. A second literal is how two
    # inputs start disagreeing about how fast the same wheel may turn.
    bare = [lit for lit in ("Math.max(-200", "Math.min(200", "dt / 160", "> 1.5")
            if lit in source.replace(named.group(0), "")]
    if bare:
        rep.fail("no second copy of a constant",
                 f"the script still writes {bare} beside the named values, so one "
                 "input can be tuned and the other not")
    else:
        rep.ok("no second copy of a constant",
               "every clamp and half-life reads SPIN_CAP / SPIN_HALF / SPIN_MIN")

    # The phrase wraps in the source, so the whitespace is written as whitespace
    # rather than as a space: a note that reflows must not read as a deleted note.
    quoted = re.findall(r"capped at ([\d.]+) deg/s and\s+halv\w*\s+every ([\d.]+)ms", source)
    if len(quoted) < 2:
        rep.fail("the notes quote the code's momentum",
                 f"{len(quoted)} note(s) state the cap and half-life where two should "
                 "(M18's for the hand, M19's for the flywheel) — either a note lost "
                 "the numbers or changed their wording past what this check reads")
    else:
        wrong = [(c, h) for c, h in quoted if (float(c), float(h)) != (cap, half)]
        if wrong:
            rep.fail("the notes quote the code's momentum",
                     f"the notes say {wrong} while the code says {cap:g} deg/s halving "
                     f"every {half:g}ms — a reader would be told the wrong wheel")
        else:
            rep.ok("the notes quote the code's momentum",
                   f"{len(quoted)} notes state {cap:g} deg/s and {half:g}ms, as the code does")

    # The sweep of a capped flick: the integral of v0 * 2^-(t/h) is v0*h/ln2.
    sweep = cap * (half / 1000) / math.log(2)
    said = re.findall(r"about ([\d.]+) degrees", source)
    if not said:
        rep.fail("the flick's sweep is the arithmetic's own",
                 "no note states the sweep in the form this check reads")
    elif abs(float(said[0]) - sweep) > 1:
        rep.fail("the flick's sweep is the arithmetic's own",
                 f"the note says about {said[0]} degrees and the constants give "
                 f"{sweep:.1f} — {cap:g} deg/s halving every {half:g}ms")
    else:
        rep.ok("the flick's sweep is the arithmetic's own",
               f"{cap:g} x {half / 1000:g}s / ln2 = {sweep:.1f}, and the note says about {said[0]}")

    # Settling: how long the cap takes to fall to the settle threshold. The note
    # said "under a second" until this clause was written; it is 1.13s.
    settle = (half / 1000) * math.log(cap / floor, 2)
    if re.search(r"settles (?:in |inside )?under a second", source):
        rep.fail("settling takes the time the note claims",
                 f"a note promises under a second and the constants give {settle:.2f}s "
                 f"({cap:g} deg/s to {floor:g} deg/s at a {half:g}ms half-life)")
    elif not re.search(r"settles (?:in |inside )about a second", source):
        rep.fail("settling takes the time the note claims",
                 "no note states the settling time in the form this check reads")
    else:
        rep.ok("settling takes the time the note claims",
               f"{cap:g} deg/s to {floor:g} deg/s at a {half:g}ms half-life is "
               f"{settle:.2f}s, which is the about a second the notes say")

    # The cap has to be slow enough that the teeth do not alias. A wheel that
    # advances more than one tooth pitch between frames does not read as fast:
    # it reads as still, or as turning backwards (the wagon-wheel effect), and
    # this page's whole subject is a toothed mechanism, so strobing is not a
    # performance cost but a wrong statement. The wheel turns because the reader
    # moved; the pitch is 360 / the count the DRAWING declares, so this clause
    # holds the tune against the artifact rather than against the note. 60Hz is
    # the worst case and the right one to check: a faster display steps less far
    # per frame, so a cap that survives 60 survives 120.
    #
    # The pinion needs no clause of its own, and that is the meshing fact rather
    # than an omission: a driven pair advances the SAME number of teeth, so the
    # pinion's 7.4 deg a frame against its 7.5 deg pitch (360/48) is the same
    # statement as the great wheel's. One inequality, both wheels.
    step = cap / 60.0
    for tag, attr in (("hero", "data-gear-a"), ("close", "data-close-a")):
        counts = [int(v) for v in re.findall(attr + r'="(\d+)"', page)]
        if not counts:
            rep.fail("the cap cannot outrun a tooth",
                     f"the {tag}'s drawing declares no tooth count, so the cap "
                     "cannot be held against it — that is the check, not a detail")
            continue
        pitch = 360.0 / counts[0]
        if step > pitch + 1e-9:
            rep.fail("the cap cannot outrun a tooth",
                     f"the {tag}'s wheel has {counts[0]} teeth, a pitch of "
                     f"{pitch:.2f} deg, and {cap:g} deg/s is {step:.2f} deg a frame "
                     f"({step / pitch:.2f} pitches, where 1 is the limit): the teeth "
                     "alias into a strobe, which is the wagon wheel, not speed")
        else:
            rep.ok("the cap cannot outrun a tooth",
                   f"{cap:g} deg/s is {step:.2f} deg a frame against the {tag} "
                   f"wheel's {pitch:.2f} deg pitch ({step / pitch:.2f} of one tooth)")

    # The two angle mappings, against the notes that state them in words.
    words = {w: i for i, w in enumerate(
        ("zero", "one", "two", "three", "four", "five", "six",
         "seven", "eight", "nine", "ten", "eleven", "twelve"), 0)}
    for label, expr, said_re, said in (
            ("the hero's scroll maps to the degrees its note states",
             r"window.scrollY / heroBottom\) \* (\d+)\) / 10",
             r"eight\s+degrees\s+across the whole", "eight"),
            ("the poster's scroll maps to the degrees its note states",
             r"closeTop\) / closeRange\)\) \* (\d+)\) / 10",
             r"one\s+(?:slow\s+)?degree\s+(?:of the crown\s+)?across the poster's",
             "one")):
        m = re.search(expr, source)
        if not m:
            rep.fail(label,
                     "the mapping no longer has the form this check reads — teach "
                     "it the new form, do not drop the check")
            continue
        degrees = float(m.group(1)) / 10
        if not re.search(said_re, source):
            rep.fail(label, f'the note no longer states "{said}" in words')
        elif abs(degrees - words[said]) > 1e-9:
            rep.fail(label,
                     f"the mapping is {degrees:g} degrees and the note says {said}")
        else:
            plural = "degree" if degrees == 1 else "degrees"
            rep.ok(label, f"{m.group(1)}/10 = {degrees:g} {plural}, and the note says {said}")


def check_9(rep: Report, site: pathlib.Path,
            docs: dict[pathlib.Path, str]) -> None:
    print("\n9  library integrity")
    pages = sorted(d for d in site.iterdir()
                   if d.is_dir() and (d / "index.html").is_file()
                   and d.name not in LIBRARY_TOC)
    if len(pages) != LIBRARY_PAGES:
        rep.fail("library page count",
                 f"{len(pages)}, expected {LIBRARY_PAGES}")
    else:
        rep.ok(f"{LIBRARY_PAGES} library pages present")

    styles = site / "styles.css"
    if not styles.is_file():
        rep.fail("/styles.css", "missing — 75 pages would render unstyled")
    elif styles.stat().st_size != LIBRARY_STYLES_BYTES:
        rep.fail("/styles.css",
                 f"{styles.stat().st_size:,} B, the library's file is "
                 f"{LIBRARY_STYLES_BYTES:,} B")
    else:
        rep.ok("/styles.css is the library's", f"{LIBRARY_STYLES_BYTES:,} B")

    # The directory tells its reader, in visible copy, that `/` focuses the field
    # and that the arrow keys walk the matches. That is a promise about behaviour,
    # which is the one kind this file's copy sibling cannot see: it reads text. So
    # the text is checked here against the script that has to keep it, by name.
    index = site / "library" / "index.html"
    script = docs.get(index, "")
    if "to search, then the arrow keys" in script:
        missing = [k for k in ("'/'", "ArrowDown", "ArrowUp") if k not in script]
        if missing:
            rep.fail("the directory's keyboard",
                     "the hint promises " + ", ".join(missing) + " and the script "
                     "does not handle it — a promise in visible copy, unkept")
        else:
            rep.ok("the directory's keyboard matches its own hint",
                   "slash, ArrowDown, ArrowUp")
    else:
        rep.fail("the directory's keyboard",
                 "/library/ no longer carries the hint that teaches the shortcut")

    lost = []
    for d in pages:
        text = docs.get(d / "index.html", "")
        m = re.search(r"""<link[^>]+rel=["']canonical["'][^>]*>""", text, re.I)
        if not m:
            lost.append(f"/{d.name}/ has no rel=canonical")
            continue
        href = re.search(r"""href=["']([^"']+)["']""", m.group(0), re.I)
        want = f"https://istor.fyi/{d.name}/"
        if not href or href.group(1).rstrip("/") + "/" != want:
            lost.append(f"/{d.name}/ canonicals to "
                        f"{href.group(1) if href else 'nothing'}, not {want}")
    if lost:
        for item in lost[:10]:
            rep.fail("self-canonical", item)
        if len(lost) > 10:
            rep.fail("self-canonical", f"and {len(lost) - 10} more")
    else:
        rep.ok(f"{len(pages)} self-canonicals intact")

    # The continue-reading pair, asserted as a WALK rather than sampled.
    #
    # Every carried article ends with a next and a previous link, written into it
    # by add-article-nav.py from the index generator's own grouping. Checking one
    # page's pair would pass while the chain had a hole in it, and a chain with a
    # hole is worse than no chain: a reader follows it and stops in the middle of
    # a library that claims seventy-five pages. So the walk is followed from the
    # one page that has no previous, and it has to reach every carried page
    # exactly once; then the same walk is followed backwards from the end. Two
    # directions because a broken prev is invisible to a next-only walk.
    step: dict[str, tuple[str | None, str | None]] = {}
    for d in pages:
        text = docs.get(d / "index.html", "")

        def href(rel: str, text: str = text) -> str | None:
            m = re.search(r'<a[^>]+href="/([^"/]+)/"[^>]*rel="%s"' % rel, text)
            return m.group(1) if m else None

        step[d.name] = (href("next"), href("prev"))

    starts = sorted(s for s, (_n, prev) in step.items() if prev is None)
    forward, cur = [], (starts[0] if len(starts) == 1 else None)
    while cur and cur not in forward:
        forward.append(cur)
        cur = step.get(cur, (None, None))[0]
    backward, cur = [], (forward[-1] if forward else None)
    while cur and cur not in backward:
        backward.append(cur)
        cur = step.get(cur, (None, None))[1]

    if (len(starts) != 1 or sorted(forward) != sorted(step)
            or sorted(backward) != sorted(step) or forward != backward[::-1]):
        rep.fail("the continue-reading walk",
                 f"{len(starts)} page(s) start the walk (one should), forwards "
                 f"reached {len(forward)} of {len(step)}, backwards reached "
                 f"{len(backward)}. Run Source/tools/add-article-nav.py.")
    else:
        crossing = sum(1 for i in range(1, len(forward))
                       if make_library_index.group_of(forward[i]) !=
                       make_library_index.group_of(forward[i - 1]))
        rep.ok(f"one walk through {len(forward)} articles",
               f"every page reached exactly once, both ways, {crossing} group "
               f"crossings")

    dash_pages = []
    for path, text in docs.items():
        if path.suffix.lower() not in (".html", ".htm"):
            continue
        punctuation = sorted({c for c in visible_text(text) if c in "—–"})
        if punctuation:
            dash_pages.append(f"/{path.relative_to(site).as_posix()}: " +
                              ", ".join(repr(c) for c in punctuation))
    if dash_pages:
        for item in dash_pages[:10]:
            rep.fail("visible dash punctuation", item)
        if len(dash_pages) > 10:
            rep.fail("visible dash punctuation", f"and {len(dash_pages) - 10} more pages")
    else:
        rep.ok("all published HTML copy has no em or en dash")

    for brand in ("brand/istor-page.svg", "brand/og-card.png"):
        if (site / brand).is_file():
            rep.ok(f"/{brand} present")
        else:
            rep.fail(f"/{brand}", "missing — §1.1 carries it for the library")

    # The two-sided page check: sitemap and llms.txt must name exactly the pages
    # that exist, and every page must carry a lastmod (§3, Stage 8).
    #
    # "Page" means a URL under istor.fyi that is the root or ends in a slash.
    # Both files also name non-pages — /styles.css and /favicon.ico in the
    # sitemap's neighbourhood, the GitHub release URL in llms.txt — and those
    # are not this check's business, so they are filtered by shape rather than
    # by an allowlist that would need editing every time a file is added.
    # Every page, the index included: this set is compared against the sitemap
    # and llms.txt, and both name /library/ now. `pages` above is the 75 carried
    # articles, which is a different question — whether the library is intact.
    all_pages = sorted(d for d in site.iterdir()
                       if d.is_dir() and (d / "index.html").is_file()
                       and d.name not in NOT_A_PAGE)
    have = {"/"} | {f"/{d.name}/" for d in all_pages}
    for name in ("sitemap.xml", "llms.txt"):
        path = site / name
        if not path.is_file():
            rep.fail(name, "missing from the artifact")
            continue
        text = path.read_text(encoding="utf-8")
        listed = set()
        for u in re.findall(r"https://istor\.fyi(/[^\s<>\"')\]]*)", text):
            u = u.split("#")[0]
            if u == "" or u.endswith("/"):
                listed.add(u or "/")
        missing = sorted(have - listed)
        extra = sorted(listed - have)
        if missing or extra:
            rep.fail(name, f"{len(listed)} pages listed of {len(have)} — "
                           f"missing {missing[:4]}, unknown {extra[:4]}")
        else:
            rep.ok(f"{name} names all {len(have)} pages",
                   f"{len(listed)} urls, both directions")

    sm = (site / "sitemap.xml").read_text(encoding="utf-8")
    entries = re.findall(r"<url>(.*?)</url>", sm, re.S)
    dateless = [re.search(r"<loc>([^<]+)</loc>", e).group(1)
                for e in entries if "<lastmod>" not in e]
    if dateless:
        rep.fail("lastmod", f"{len(dateless)} pages ship dateless: {dateless[:4]}")
    else:
        rep.ok(f"every page has a lastmod", f"{len(entries)} entries")


def check_newlines(rep: Report, site: pathlib.Path) -> None:
    print("\n   artifact integrity")
    # TEXT files only. A PNG, WebP or AVIF carries the bytes 0D 0A wherever the
    # compressor happened to emit them — scanning the images reports sixteen
    # CRLF "failures" that are JPEG coefficients, and the check stops being read.
    text_suffixes = {".html", ".htm", ".css", ".txt", ".xml", ".svg", ".js",
                     ".json", ".webmanifest"}
    crlf = [p.relative_to(site).as_posix()
            for p in site.rglob("*") if p.is_file()
            and p.suffix.lower() in text_suffixes
            and b"\r\n" in p.read_bytes()]
    if crlf:
        for name in crlf[:10]:
            rep.fail("CRLF", f"{name} — the repository is LF-only")
    else:
        rep.ok("the artifact is LF-only", "no CRLF in any text file")

    # The documents too, and the reason is not theoretical: a mutation script in
    # .improvement restored this plan with `write_text`, whose default newline
    # translation turned all 1381 lines CRLF, and nothing was watching the files
    # that are not the artifact. These three are read by hand and diffed on every
    # commit, so one of them arriving in CRLF is a diff of every line.
    doc_crlf = [p.relative_to(REPO).as_posix() for p in DOCUMENTS
                if p.exists() and b"\r\n" in p.read_bytes()]
    if doc_crlf:
        for name in doc_crlf:
            rep.fail("CRLF in a document", f"{name} — the repository is LF-only, and "
                                            f"a rewritten document is how this got "
                                            f"past a gate the first time")
    else:
        rep.ok("the documents are LF-only",
               f"{len([p for p in DOCUMENTS if p.exists()])} files")

    files = [p for p in site.rglob("*") if p.is_file()]
    if len(files) != ARTIFACT_FILES:
        rep.fail("artifact file count",
                 f"{len(files)} files, expected {ARTIFACT_FILES}")
    else:
        rep.ok("artifact file count", f"{ARTIFACT_FILES} files")


# ------------------------------------------------------------------------ main

def media_block(css: str, query: str) -> str:
    """The text inside `@media <query> { ... }`, by brace depth."""
    m = re.search(r"@media\s*" + query + r"\s*\{", css)
    if not m:
        return ""
    i, depth = m.end(), 1
    while i < len(css) and depth:
        if css[i] == "{":
            depth += 1
        elif css[i] == "}":
            depth -= 1
        i += 1
    return css[m.end():i - 1]


def check_page_marks(rep: Report, site: pathlib.Path, docs: dict) -> None:
    """Every carried page wears its own group's mark, and only its own.

    add-page-marks.py puts one include marker in each page's <h1> and the build
    splices the drawing in, so the built page is where this can be checked: the mark
    that arrived has to be the one its slug's group claims. Two ways this goes wrong
    and both look fine on the page a reader lands on: a page added by hand with no
    marker (it looks like every other page and belongs to no family), and a page whose
    marker kept an old group after the slug's prefix changed. The mapping is read from
    the index generator, so it is the same rule the directory uses.
    """
    print("\nthe pages' group marks")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "make_library_index", SOURCE / "tools" / "make-library-index.py")
        assert spec and spec.loader
        index = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(index)
    except Exception as exc:                       # noqa: BLE001 - reported, not raised
        rep.fail("the library's group marks",
                 f"make-library-index.py could not be loaded to read the groups: {exc}")
        return

    missing: list[str] = []
    wrong: list[str] = []
    counted = 0
    for slug in index.library_slugs():
        page = site / slug / "index.html"
        if not page.is_file():
            continue
        html = docs.get(page)
        if html is None:
            continue
        counted += 1
        want = index.anchor(index.group_of(slug))
        head = re.search(r"<h1>(.*?)</h1>", html, re.S)
        got = re.search(r'class="group-mark"[^>]*data-group="([a-z0-9-]+)"', head.group(1)) \
            if head else None
        if not got:
            missing.append(slug)
        elif got.group(1) != want:
            wrong.append(f"{slug} wears {got.group(1)} and belongs to {want}")

    if missing:
        rep.fail("every carried page wears its group's mark",
                 f"{len(missing)} page(s) carry none: {', '.join(missing[:4])} - "
                 "run python Source/tools/add-page-marks.py")
    elif wrong:
        rep.fail("every carried page wears its group's mark",
                 "; ".join(wrong[:3]))
    else:
        rep.ok("every carried page wears its group's mark",
               f"{counted} pages, each with the mark of the group its slug claims")


def wash_over(wash: str, ground: str) -> str:
    """The colour a reader's eye gets where a translucent token sits on a ground.

    `rgba()` over `#RRGGBB`, in that order: the ground is opaque and the wash is
    not, so the compositing is multiplication and one subtraction. The existing
    `contrast()` above measures hex pairs, and this is what produces its second
    hex out of what the stylesheet actually declares.
    """
    m = re.fullmatch(r"rgba?\(([^)]+)\)", wash.strip())
    if m:
        parts = [p.strip() for p in m.group(1).split(",")]
        alpha = float(parts[3]) if len(parts) > 3 else 1.0
        body = [float(p) for p in parts[:3]]
    else:
        hexed = wash.strip().lstrip("#")
        body = [int(hexed[i:i + 2], 16) for i in (0, 2, 4)]
        alpha = 1.0
    under = ground.strip().lstrip("#")
    ground_rgb = [int(under[i:i + 2], 16) for i in (0, 2, 4)]
    out = [round(alpha * body[i] + (1 - alpha) * ground_rgb[i]) for i in range(3)]
    return "#%02X%02X%02X" % tuple(out)


def mark_ratios(tokens: dict[str, str], grounds: tuple[str, ...]) -> tuple[float, float] | None:
    """One token world's (ink on its wash, accent on its wash), or None.

    The wash is composited over each ground the mark can sit on - the dialog's own
    and a hovered row's - and the tighter figure is the one returned, because the
    tighter figure is the one a reader meets.
    """
    if "--cite-wash" not in tokens or "--ink" not in tokens:
        return None
    ink = accent = None
    for ground in grounds:
        if ground not in tokens:
            continue
        over = wash_over(tokens["--cite-wash"], tokens[ground])
        here = contrast(tokens["--ink"], over)
        ink = here if ink is None else min(ink, here)
        if "--cite-ink" in tokens:
            there = contrast(tokens["--cite-ink"], over)
            accent = there if accent is None else min(accent, there)
    return (ink, accent) if ink is not None else None


def palette_font_sizes(css: str, root: dict[str, str] | None = None) -> list[tuple[float, str]]:
    """Every font-size the palette's own selectors declare, as (px, selector).

    Three forms and all three matter: a rem is read at the root the site sets (16px,
    which is what the audit's own pass measures against), a px is itself, and a
    `var(--t-...)` is resolved through the file's own tokens - because the landing's
    stylesheet is written on a type scale, and a check that only understood literals
    would have measured two of its declarations and reported the floor as safe.
    """
    root = token_block(css, ":root") if root is None else root
    out: list[tuple[float, str]] = []
    for sel, body, inside in css_rules(css):
        if inside or not re.search(r"\.(palette|search-open)", sel):
            continue
        for prop, value in declarations(body):
            if prop != "font-size":
                continue
            seen = 0
            token = re.fullmatch(r"var\(\s*(--[a-z0-9-]+)\s*\)", value)
            while token and seen < 8:
                value = root.get(token.group(1), "")
                token = re.fullmatch(r"var\(\s*(--[a-z0-9-]+)\s*\)", value)
                seen += 1
            m = re.fullmatch(r"([\d.]+)(rem|px)", value.strip())
            if m:
                out.append((float(m.group(1)) * (16 if m.group(2) == "rem" else 1), sel))
    return out


def palette_class_names(css: str) -> set[str]:
    """The palette's class names, as selectors rather than as substrings.

    `search-open`, `search-glyph` and `search-word` by name rather than by prefix,
    because this page has other classes that begin with `search` - the app
    replica's - and a prefix would report them as half of a widget they belong to
    nothing.
    """
    names: set[str] = set()
    for sel, _body, inside in css_rules(css):
        if inside:
            continue
        names.update(re.findall(r"\.(palette[a-z0-9-]*|search-(?:open|glyph|word))",
                                sel))
    return names


def check_search(rep: Report, site: pathlib.Path, docs: dict) -> None:
    """The search palette: every page offers it, and what it reads is this build.

    Four claims, none of which the page a reader lands on can show:

    * **Every carried page carries the way in**, and the directory too. The trigger
      is an `<a href="/library/">` upgraded into a dialog by one deferred script, so
      a page that lost either half looks exactly like a page that has them: the link
      still goes somewhere, and nothing about the page changes until a reader clicks.
    * **The script fetches the file this build wrote**, by name, from the script
      rather than from a list here. A palette pointed at a path no build writes is a
      palette that opens, says "did not load", and looks like a bad connection.
    * **That file is the generator's output, byte for byte.** It is derived from the
      same 75 pages as the directory; a committed copy that drifted would answer
      searches with titles that no longer exist, and every other check would pass.
    * **The dialog the script builds is styled by the stylesheet the pages load.**
      The script names its own classes and the stylesheet draws them, and a rename on
      one side of that pair ships an unstyled widget, which is a change neither file
      can see on its own.
    """
    print("\nthe search palette")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "make_search_index", SOURCE / "tools" / "make-search-index.py")
        assert spec and spec.loader
        search = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(search)
        spec = importlib.util.spec_from_file_location(
            "make_library_index", SOURCE / "tools" / "make-library-index.py")
        assert spec and spec.loader
        index = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(index)
    except Exception as exc:                       # noqa: BLE001 - reported, not raised
        rep.fail("the search palette",
                 f"its generators could not be loaded: {exc}")
        return

    slugs = index.library_slugs()
    silent = []
    scriptless = []
    for slug in slugs:
        html = docs.get(site / slug / "index.html")
        if html is None:
            continue
        if "data-search-open" not in html:
            silent.append(slug)
        if '/search.js"' not in html:
            scriptless.append(slug)
    directory = docs.get(site / "library" / "index.html", "")
    # Both halves, because the index LIFTS the header and the script tags from a real
    # page: a generator that stopped lifting the palette's script would ship a
    # directory whose trigger navigated to the page it is already on, which looks
    # exactly like a working link. Found by driving the directory rather than by
    # reading it (`audit-palette.py`, whose Ctrl+K claim was the thing that failed).
    missing_directory = ("data-search-open" not in directory
                         or "/search.js" not in directory)
    # The landing too, and it is the one page whose trigger is authored rather than
    # written by the tool: its copy sits in the close, where the page hands the reader
    # sixteen of the site's seventy-five other pages. A build that dropped either half
    # there would leave a link to the directory and no way to search from it, which
    # looks exactly like the page working.
    landing_page = docs.get(site / "index.html", "")
    landing_silent = "data-search-open" not in landing_page
    landing_scriptless = "/search.js" not in landing_page

    if silent or scriptless or missing_directory or landing_silent or landing_scriptless:
        rep.fail("every page offers the search",
                 f"{len(silent)} page(s) with no trigger, {len(scriptless)} with no "
                 f"script" + (", the directory has neither" if missing_directory else "") +
                 (", and the landing one or the other"
                  if (landing_silent or landing_scriptless) else "") +
                 f" - run python Source/tools/add-search-trigger.py")
    else:
        rep.ok("every page offers the search",
               f"{len(slugs)} carried pages, the directory and the landing, trigger "
               f"and script")

    palette = site / "search.js"
    if not palette.is_file():
        rep.fail("/search.js", "missing — every page names it and nothing would load")
        return
    source = palette.read_text(encoding="utf-8")

    # ONE RULE, TWO SEARCHES. The directory's find field filters the list in front of
    # the reader and the palette searches the rest of the library, and they read
    # different text by design - an entry is its title and summary, the palette reads
    # headings too - but the WORD test has one implementation, in /search.js, which the
    # field calls. Two facts hold that together and neither can be seen from one file:
    # the generated page calls the name the script publishes, and the page does not
    # carry a second copy of the fold, which is the drift this is here to prevent.
    # Found by measurement rather than by reading: on the directory's own corpus the
    # plain rule showed 16 entries for "models" where the fold shows 42, and typing
    # "hallucinations" hid the page called "What is AI hallucination?" entirely.
    borrowed = "window.istorMatch ||" in directory
    called = "return match(text, word);" in directory
    published = "window.istorMatch =" in source
    fallback = "indexOf(word) !== -1" in directory
    copied = "'isation'" in directory or "FOLD_CAP" in directory
    generated = index.FIND_SCRIPT.strip() in directory
    if not (borrowed and called and published and fallback and generated) or copied:
        rep.fail("the directory's field borrows the palette's rule",
                 f"published {published}, borrowed {borrowed}, called {called}, "
                 f"own substring fallback {fallback}, its own copy of the table "
                 f"{copied}, and the generator's script verbatim {generated}")
    else:
        rep.ok("the directory's field borrows the palette's rule",
               "one implementation called by both searches, with the field's own "
               "substring test kept for the page where /search.js never loads")

    # ONE CORPUS, AS WELL AS ONE RULE. An entry in the directory carries a title and a
    # summary; the dialog reads those plus each section's heading and its first line,
    # so the same query used to be answered twice with different numbers - "parameters"
    # 1 entry against 9 pages, "models" 42 against 58. The field now reads each page's
    # own text out of the accessor /search.js publishes, and the entry's title and
    # summary stay as what is matched until that text arrives. The third fact is the
    # anti-drift one: the page must not name the index file itself, or it could fetch
    # and parse its own copy of the corpus and the two would be free to disagree again.
    reads_it = "window.istorIndex()" in directory
    owns_fallback = "over[url]) || li.getAttribute('data-hay')" in directory
    publishes_it = "window.istorIndex =" in source
    own_fetch = "search-index.json" in directory
    if not (reads_it and owns_fallback and publishes_it) or own_fetch:
        rep.fail("the directory's field reads the library's text",
                 f"published {publishes_it}, read {reads_it}, its own fallback "
                 f"{owns_fallback}, and a copy of the index path of its own "
                 f"{own_fetch}")
    else:
        rep.ok("the directory's field reads the library's text",
               "the same per-page text as the dialog, fetched through it, with the "
               "entry's own title and summary until it arrives")
    m = re.search(r"var INDEX = '([^']+)'", source)
    if not m:
        rep.fail("the palette's index path",
                 "search.js names no INDEX for the file it fetches")
        return

    shipped = site / m.group(1).lstrip("/")
    if not shipped.is_file():
        rep.fail("the palette's index path",
                 f"search.js fetches {m.group(1)} and no build writes it")
        return

    want = search.build()
    if shipped.read_bytes().decode("utf-8") != want:
        rep.fail("the search index is the generator's",
                 f"{m.group(1)} is not make-search-index.py's output - run "
                 f"python Source/tools/make-search-index.py")
    else:
        records = json.loads(want)
        urls = {r["url"] for r in records}
        # Read off the ARTIFACT's directories rather than off OldVersion's, which
        # is where the generator read them: two routes to one fact, so a page that
        # is published and not indexed is a failure here rather than an agreement
        # between a generator and itself.
        carried = {f"/{d.name}/" for d in site.iterdir()
                   if d.is_dir() and (d / "index.html").is_file()
                   and d.name not in LIBRARY_TOC}
        if urls != carried:
            rep.fail("the search index covers the published pages",
                     f"{len(urls)} record(s) against {len(carried)} published "
                     f"pages - no record for {sorted(carried - urls)[:3]}, records "
                     f"for {sorted(urls - carried)[:3]}")
        else:
            rep.ok("the search index is the generator's",
                   f"{len(records)} pages, {len(want.encode('utf-8')):,} B, "
                   f"fetched as {m.group(1)}")

    # ONE WIDGET, TWO STYLESHEETS, and this is where they are held together. The
    # landing inlines its stylesheet; the library links /styles.css; so the palette
    # has to be written in both, in each file's own token vocabulary. Everything
    # below is asked of both files, and the pair is the point: a rename that lands in
    # one file and not the other ships a widget that is styled on one side of the
    # site and naked on the other, which is a change neither file can see alone.
    built = sorted(set(re.findall(r"className = '([a-z0-9-]+)'", source)) |
                   {"search-open"})
    ids = sorted(set(re.findall(r"\.id = '([a-z0-9-]+)';", source)))

    library_path = site / "styles.css"
    library_css = (library_path.read_text(encoding="utf-8")
                   if library_path.is_file() else "")
    landing = site / "index.html"
    landing_html = landing.read_text(encoding="utf-8") if landing.is_file() else ""
    style = re.search(r"<style\b[^>]*>(.*?)</style>", landing_html, re.S | re.I)
    landing_css = style.group(1) if style else ""
    drawn = {"the landing's inlined copy": landing_css,
             "the library's /styles.css": library_css}

    for label, css in drawn.items():
        # A boundary rather than a substring: `.palette-where` is a prefix of
        # `.palette-where-gone`, so `in` would pass on a class renamed away.
        unstyled = [name for name in built + ids
                    if not re.search(r"[.#]%s(?![\w-])" % re.escape(name), css)]
        if unstyled:
            rep.fail("the palette's own classes",
                     f"{label} draws none of {', '.join(unstyled)}, which the script "
                     f"builds")
        else:
            rep.ok(f"the palette's own classes, {label}",
                   f"{len(built)} classes, {len(ids)} ids")

    # The same widget means the same names in both. Not the same rules - these files
    # hold different tokens - but the same vocabulary, or a reader who meets the
    # palette in the library would not recognise it on the landing.
    landing_names = palette_class_names(landing_css)
    library_names = palette_class_names(library_css)
    if landing_names != library_names:
        rep.fail("the two palettes draw the same classes",
                 f"only in one file: {sorted(landing_names ^ library_names)[:6]}. The "
                 f"names are one widget's, written twice in two vocabularies.")
    else:
        rep.ok("the two palettes draw the same classes",
               f"{len(library_names)} names in both files")

    # The mark's colour, derived rather than trusted, in each file from its own
    # tokens. Both stylesheets say the marked word takes the page's ink rather than
    # the accent its line is drawn in, and each gives a measurement as the reason - so
    # each is recomputed here. In the library the reason is that the accent fails
    # under the wash; on the landing it is that the same widget must mark a word the
    # same way in both places. One of those is a claim this file can refute.
    for label, css, worlds in (
            ("the library's /styles.css", library_css,
             ((":root", ("--canvas", "--subtle")),
              (':root[data-theme="dark"]', ("--canvas", "--subtle")))),
            ("the landing's inlined copy", landing_css,
             ((":root", ("--card",)),))):
        block = re.search(r"\.palette mark\s*\{(.*?)\}", css, re.S)
        if not block:
            rep.fail("the palette's mark", f"{label} draws no .palette mark")
            continue
        if "color: var(--ink)" not in block.group(1):
            rep.fail("the palette's mark",
                     f"{label} does not give the mark --ink, so the wash sits under "
                     f"the accent and the line loses the contrast its note measured")
            continue
        tightest, accent = None, None
        for selector, grounds in worlds:
            tokens = token_block(css, selector)
            got = mark_ratios(tokens, grounds)
            if not got:
                continue
            ink_here, accent_here = got
            tightest = ink_here if tightest is None else min(tightest, ink_here)
            if accent_here is not None:
                accent = accent_here if accent is None else min(accent, accent_here)
        if tightest is None:
            rep.fail("the palette's mark",
                     f"{label} declares no --cite-wash/--ink pair to measure the mark "
                     f"against, so this check is measuring nothing")
        elif tightest < 4.5:
            rep.fail("the palette's mark",
                     f"{label}: the page's ink on its own wash is {tightest:.2f}:1 - "
                     f"below the 4.5:1 a snippet has to clear")
        else:
            rep.ok(f"the palette's mark, {label}",
                   f"ink on the wash {tightest:.2f}:1, against {accent:.2f}:1 for the "
                   f"accent it replaced")

    # The library's own copy carries a reason the landing's cannot: there the accent
    # drops UNDER the bar on the row a reader is reading, and the note in that file
    # says so. If a token ever moves the accent back over it, the note is wrong.
    library_mark = mark_ratios(token_block(library_css, ":root"),
                               ("--canvas", "--subtle"))
    dark_mark = mark_ratios(token_block(library_css, ':root[data-theme="dark"]'),
                            ("--canvas", "--subtle"))
    accent = min([r[1] for r in (library_mark, dark_mark) if r and r[1] is not None],
                 default=None)
    if accent is not None and accent >= 4.5:
        rep.fail("the library's mark note",
                 f"the accent on the wash now measures {accent:.2f}:1, so the reason "
                 f"that file gives for taking --ink (that the accent drops under the "
                 f"4.5:1 bar) no longer holds - re-measure and rewrite the note")
    elif accent is not None:
        rep.ok("the library's mark note still holds",
               f"the accent it replaced measures {accent:.2f}:1 under the wash")

    # The type floor, for the one surface the contrast audit's pass cannot reach.
    # That pass walks real pages at 13 widths and multiplies every text by the scale
    # of the SVG it sits inside, which is the right instrument for everything a reader
    # can load - and this dialog only exists after a click, so it is held to the
    # site's 11px floor here instead, in both files.
    for label, css in drawn.items():
        typed = palette_font_sizes(css)
        if not typed:
            rep.fail("the palette's type floor",
                     f"{label} declares no font-size for the palette or its trigger, "
                     f"so this check is measuring nothing there")
        elif min(typed)[0] < 11:
            small = ", ".join(f"{sel} {px:.2f}px" for px, sel in sorted(typed)[:3])
            rep.fail("the palette's type floor",
                     f"{label} is under 11px at a 16px root: {small}. The audit's own "
                     f"pass cannot reach a dialog that only exists after a click.")
        else:
            rep.ok(f"the palette's type floor, {label}",
                   f"{len(typed)} sizes, smallest {min(typed)[0]:.2f}px "
                   f"({min(typed)[1]})")

    # The two tools that make this feature: the generator's own doctored-file
    # self-test, and the tool's own --check that every page still carries the
    # markup it would write. Both are cheap, both are the proof that the checks
    # above are checks rather than descriptions, and neither is worth a separate
    # run for a reader to remember.
    import subprocess
    for tool, args, what in (
            ("make-search-index.py", ["--self-test"], "self-test"),
            ("add-search-trigger.py", ["--check"], "--check")):
        done = subprocess.run([sys.executable, str(SOURCE / "tools" / tool), *args],
                              capture_output=True, text=True)
        said = ((done.stdout or "").strip() or (done.stderr or "").strip())
        said = said.splitlines()[-1] if said else ""
        if done.returncode == 0:
            rep.ok(f"{tool} {what}", said[:110])
        else:
            rep.fail(f"{tool} {what}", said[:300])


def check_library_arrivals(rep: Report, site: pathlib.Path, docs: dict) -> None:
    """The library's arrivals, checked where driving a page cannot reach.

    M21 gives every library document the arrivals the landing has, out of a stylesheet
    and a script those documents share rather than the landing's inlined pair.
    audit-motion.py drives that: a cold block below the fold, the reader's pace choosing
    between the authored length and the shorter one, and a reduced-motion run where
    nothing is marked. Four facts sit outside any single run of it:

      * a marker authored into the HTML would hide real content from a reader whose
        script never runs, which is the failure this feature's own comment names and
        the one a hand-edited page would reintroduce;
      * the script measures the reader's travel over the arrival's authored length
        while the stylesheet animates for it, so one number lives in two files and no
        browser notices when they drift apart;
      * a page that marks a block and never loads the script has arrivals that cannot
        happen, and it looks exactly like a page that has none;
      * the rest of the family - a grid's staggered items are the library's own - has
        to keep reading the clock, because a rule left with a bare duration still
        animates and would silently stop being paced.
    """
    print("\nthe library's arrivals")
    css = docs.get(site / "styles.css")
    # theme.js is read from disk rather than from `docs`, which holds the pages and the
    # stylesheets; the script is the third file this feature depends on.
    script_path = site / "theme.js"
    script = script_path.read_text(encoding="utf-8") if script_path.is_file() else None
    if css is None or script is None:
        rep.fail("the library's arrivals ship at all",
                 "styles.css or theme.js is missing from the built site, and every "
                 "library document links both")
        return

    marked: list[pathlib.Path] = []
    authored: list[str] = []
    for p in sorted(docs):
        if p.suffix.lower() not in (".html", ".htm"):
            continue
        classes = re.findall(r'class="([^"]*)"', docs[p])
        if not any(re.search(r"\b(reveal|enter)\b", c) for c in classes):
            continue
        marked.append(p)
        if any(re.search(r"\bis-cold\b", c) for c in classes):
            authored.append(str(p.relative_to(site)))

    if not marked:
        rep.fail("no marker is authored hidden",
                 "no built page carries a reveal or enter marker at all, so the library "
                 "has the arrivals' machinery and nothing to arrive")
    elif authored:
        rep.fail("no marker is authored hidden",
                 f"{len(authored)} page(s) author `is-cold` in the markup "
                 f"({', '.join(authored[:3])}) - the class is the script's to add, and "
                 "authored it hides content from a reader whose script never runs")
    else:
        rep.ok("no marker is authored hidden",
               f"{len(marked)} marked pages, none of them carrying `is-cold` in the "
               "markup: the hidden state is only ever switched on by the script")

    # The landing is the one marked page that does not load the shared script, because
    # it inlines its own copy of the behaviour; that copy has to be there, since a
    # marker it could never mark would leave the landing's arrivals unreachable.
    stranded = [str(p.relative_to(site)) for p in marked
                if "theme.js" not in docs[p]
                and not (p == site / "index.html" and "is-cold" in docs[p])]
    if stranded:
        rep.fail("every page that marks a block can arrive",
                 f"{len(stranded)} marked page(s) load no script that could ever mark "
                 f"them: {', '.join(stranded[:3])} - their arrivals cannot happen, and "
                 "they look exactly like pages that have none")
    else:
        rep.ok("every page that marks a block can arrive",
               f"{len(marked)} marked pages: {len(marked) - 1} load /theme.js and the "
               "landing inlines its own copy of the same behaviour")

    # One number, two files: the script's window for the reader's travel and the
    # stylesheet's transition have to be the same length, or the pacing test measures a
    # window the arrival does not use.
    named = re.search(r"var ARRIVE_MS = (\d+);", script)
    entrance_rule = re.search(r"\.enter,\s*\.reveal\s*\{([^}]*)\}", css, re.S)
    entrance = (re.search(r"calc\(var\(--arrive\) \* (\d+)ms\)", entrance_rule.group(1))
                if entrance_rule else None)
    if not (named and entrance):
        rep.fail("the library's length is one number in two files",
                 "missing: " + ", ".join(n for n, m in
                 (("the script's ARRIVE_MS", named),
                  ("the .enter/.reveal transition", entrance_rule),
                  ("its length as a multiple of the clock", entrance)) if not m))
    elif named.group(1) != entrance.group(1):
        rep.fail("the library's length is one number in two files",
                 f"the script measures {named.group(1)}ms and the transition runs "
                 f"{entrance.group(1)}ms, so the reader's pace is tested against a "
                 "window the arrival does not use")
    else:
        rep.ok("the library's length is one number in two files",
               f"theme.js's ARRIVE_MS and the .enter/.reveal transition are both "
               f"{named.group(1)}ms")

    root = re.search(r":root\s*\{[^}]*?--arrive:\s*([\d.]+)\s*;", css, re.S)
    quick = re.search(r"\.reveal\.is-quick\s*\{[^}]*?--arrive:\s*([\d.]+)", css, re.S)
    if not root or float(root.group(1)) != 1:
        rep.fail("the library's clock resolves everywhere",
                 "no `--arrive: 1` at :root in the library's stylesheet - an undefined "
                 "custom property inside calc() makes the declaration invalid, so a "
                 "marker that missed the class would lose its transition entirely")
    elif not quick or not 0 < float(quick.group(1)) < 1:
        rep.fail("the library's clock resolves everywhere",
                 ".reveal.is-quick does not set --arrive to a fraction of the authored "
                 "clock, so the class the script adds would change nothing")
    else:
        rep.ok("the library's clock resolves everywhere",
               f"--arrive: 1 at :root, and {quick.group(1)} for a block the reader "
               "arrived at speed")

    # Named, not counted: a check that only counted `var(--arrive)` uses would stay
    # green while one rule lost its clock and another gained an extra one.
    required = (("calc(var(--arrive) * 700ms)", "the entrance itself"),
                ("calc(var(--arrive) * 80ms)", "a grid item's stagger"),
                ("calc(var(--arrive) * 160ms)", "the grid's third item"))
    lost = [name for expr, name in required if expr not in css]
    if lost:
        rep.fail("every timing in the library's family reads the clock",
                 f"these lost it: {', '.join(lost)} - a bare duration still animates "
                 "and would silently stop being paced")
    else:
        rep.ok("every timing in the library's family reads the clock",
               f"{len(required)} named timings, each a multiple of --arrive")


def check_10(rep: Report, page_css: str, library_css: str,
             notfound_css: str = "") -> None:
    """The two promises a stylesheet makes to a reader nobody sees.

    A reader prints the page, and a reader asks their system for more contrast.
    Both fail silently: without a print block, a reader whose system is dark prints
    the dark world's near-white ink onto white paper (measured before this block
    existed: 13 of 46 text elements on one article, 17 of 185 on the home page),
    and without a contrast block the reader who asked gets exactly what everyone
    else gets. So both are computed here rather than trusted, and the numbers are
    read out of the stylesheets rather than out of a comment about them.
    """
    print("\n10  the reader's own settings")

    for label, css in (("landing page", page_css), ("library", library_css),
                       ("not-found page", notfound_css)):
        got = media_block(css, r"print")
        if not got:
            rep.fail(f"{label} print block",
                     "no @media print — this half of the site prints its dark "
                     "inks onto white paper")
        else:
            rep.ok(f"{label} carries a print block")

        more = media_block(css, r"\(prefers-contrast:\s*more\)")
        if not more:
            rep.fail(f"{label} prefers-contrast: more",
                     "no block, so a reader who asks for more contrast is given "
                     "the same page as everyone else")
        else:
            rep.ok(f"{label} honours prefers-contrast: more")

    # The ink the print block promises, against the paper it will land on. Text
    # tokens at 4.5:1 or better, and the two that draw rules and rails at 3:1,
    # which is the same bar the screen version documents for a graphic.
    # Only the ROOT declarations of each print block, which is where the token
    # world is written. A print block can also redefine tokens for one component
    # (the landing page gives its replica the light window's own block), and those
    # are a component's internals rather than the paper's ink: `.win`'s `--rule`
    # is #E4E6E9 in both themes, so counting it here reported a 1.25:1 rule.
    printed = ""
    for css in (page_css, library_css, notfound_css):
        block = media_block(css, r"print")
        m = re.search(r":root[^{]*\{([^}]*)\}", block)
        printed += (m.group(1) if m else "")
    inks = re.findall(r"(--[a-z0-9-]+)\s*:\s*(#[0-9A-Fa-f]{6})\s*;", printed)
    text_tokens = {t for t, _v in inks if t in
                   ("--ink", "--ink-2", "--mist", "--cite-ink", "--azure",
                    "--field-ink", "--field-ink-2")}
    rule_tokens = {t for t, _v in inks if t in ("--hairline", "--rule", "--field-rule")}
    worst_text, worst_rule = 21.0, 21.0
    for token, value in inks:
        if token in text_tokens:
            worst_text = min(worst_text, contrast(value, "#FFFFFF"))
        elif token in rule_tokens:
            worst_rule = min(worst_rule, contrast(value, "#FFFFFF"))
    if not text_tokens:
        rep.fail("the print block's ink", "no text token declared in print")
    elif worst_text < 4.5:
        rep.fail("the print block's ink",
                 f"a text token is {worst_text:.2f}:1 on white paper, under 4.5")
    else:
        rep.ok("every print ink clears AA on white paper",
               f"worst {worst_text:.2f}:1")
    if rule_tokens:
        if worst_rule < 3:
            rep.fail("the print block's rules",
                     f"a rule token is {worst_rule:.2f}:1 on white paper, under 3")
        else:
            rep.ok("every printed rule is visible", f"worst {worst_rule:.2f}:1")


# The three selectors that mean "the dark world" in these two files. Named
# exactly, because a looser match reads the wrong blocks: the library's print
# block declares a light world under a selector LIST that contains
# `:root[data-theme="dark"]`, and counting that reported black ink as a dark
# token the first time this was written.
DARK_SELECTORS = (
    ':root[data-theme="dark"]',
    ':root:not([data-theme])',
    ':root:not([data-theme="light"])',
)


def dark_world(css: str) -> dict[str, set[str]]:
    """Every value a stylesheet gives each token in a dark world block.

    A SET of values, not one value, and that is the whole point: both files say
    the same thing twice, once under the media query that covers a reader with no
    script and once under the attribute the head stamp writes, and a check that
    read one block only would report a clean bill of health for a world where the
    other had drifted. The first version of this did exactly that, and the
    negative test that caught it is why the docstring names it.
    """
    out: dict[str, set[str]] = {}
    for selector, body in re.findall(r"([^{}@]*?)\{([^{}]*)\}", css):
        if " ".join(selector.split()) not in DARK_SELECTORS:
            continue
        for token, value in re.findall(
                r"(--[a-z0-9-]+)\s*:\s*(#[0-9A-Fa-f]{6})\s*;", body):
            out.setdefault(token, set()).add(value.lower())
    return out


def check_11(rep: Report, site: pathlib.Path, library_css: str) -> None:
    """The not-found page, whose reader is the one visitor who is already lost.

    The page used to answer a missing address with one link home, while 75 of the
    site's 76 pages are in the library. Three promises are asserted here and none
    of them can be read off a screenshot:

    * **It ships no comment.** It is the artifact's only hand-authored page that
      the assembler does not touch, so it was the only page still posting the
      reasoning behind its own markup: 4.6 KB of it. build-site.py strips it on
      the way in, and this reads the artifact rather than the tool, because a
      strip that ran on the wrong file would look exactly like one that worked.
    * **Its search needs no script.** The form's own action and method have to
      reach /library/?q=, which is a path the directory has read since it grew
      the find control. A page that only searched itself when its script ran
      would be a 404 that helps nobody, on the browsers where help is least.
    * **A lost reader still has somewhere to go with no script at all**, after
      the form, so no suggestion has to have appeared for the page to work.

    And one promise between two files: the dark world here is the library's dark
    world. They are separate stylesheets on purpose (this page is one screen and
    inlining the library's 48 KB for it would be the wrong kind of
    consistency), which is exactly how two token blocks drift apart.
    """
    print("\n11  the page for a missing address")
    path = site / "404.html"
    if not path.is_file():
        rep.fail("/404.html", "missing from the artifact")
        return
    page = path.read_text(encoding="utf-8")

    if "/*" in page or "<!--" in page:
        rep.fail("/404.html carries a comment",
                 "the only hand-authored page the assembler does not touch, so "
                 "its reasoning ships unless build-site.py strips it")
    else:
        rep.ok("/404.html ships with no comment in it")

    open_tag = re.search(r"<form[^>]*>", page)
    form = page[open_tag.start():(page.find("</form>", open_tag.start())
                                  if open_tag else 0)] if open_tag else ""
    missing = []
    if not re.search(r'action\s*=\s*"/library/"', form, re.I):
        missing.append('action="/library/"')
    if not re.search(r'method\s*=\s*"get"', form, re.I):
        missing.append('method="get"')
    if not re.search(r'name\s*=\s*"q"', form, re.I):
        missing.append('an input named "q"')
    if missing:
        rep.fail("the not-found page's search",
                 "no " + ", no ".join(missing) + ". Without all three a reader "
                 "whose script did not run types a query and lands nowhere")
    else:
        rep.ok("its search reaches the directory with no script")

    after = page[page.find("</form>"):] if "</form>" in page else page
    if re.search(r'href="/library/"', after):
        rep.ok("a link into the library follows the search", "no script needed")
    else:
        rep.fail("the way on from a missing address",
                 "nothing after the form links to /library/, so the only path out "
                 "of the page assumes its script ran")

    style = re.search(r"<style\b[^>]*>(.*?)</style>", page, re.S | re.I)
    mine = dark_world(style.group(1) if style else "")
    roles = {"--paper": "--canvas", "--field": "--subtle", "--ink": "--ink",
             "--ink-2": "--mist", "--rule": "--hairline", "--azure": "--cite-ink"}
    theirs = dark_world(library_css)
    drifted = []
    for token, their_token in roles.items():
        declared, installed = mine.get(token, set()), theirs.get(their_token, set())
        if declared and installed and declared - installed:
            drifted.append(f"{token} {sorted(declared)} against the library's "
                           f"{their_token} {sorted(installed)}")
    if not mine:
        rep.fail("the not-found page's dark world",
                 "no dark tokens at all, so a dark reader gets a white page")
    elif drifted:
        rep.fail("the not-found page's dark world",
                 "drifted from the library's: " + "; ".join(drifted))
    else:
        rep.ok("its dark world is the library's",
               f"{len(roles)} roles, same values")


def check_13(rep: Report, site: pathlib.Path, docs: dict,
             library_css: str) -> None:
    """The temperature page's slider: the page and the script, and one set of odds.

    The library's only control a reader can drag, and the only page here that answers
    back. Five things have to hold, and each of them is about two files that cannot
    see each other:

    * **The page carries both halves.** The control is authored `hidden` and the
      script is what unhides it, so a page that lost the script ships a slider that
      cannot move, and a page without the markup leaves a script with nothing to
      drive. Only this page carries either, which is asserted: a copy pasted onto
      another page would be a control whose bar has no plate above it.
    * **The table the script reads is what `odds.py` computes**, recomputed here from
      the module the plate above it is drawn from. The script does no arithmetic on
      purpose, which is what makes this the only thing standing between the two.
    * **The bar the page shows before any script runs** is the table's row for the
      setting the slider starts on, and its widths add up to the free width the bar
      declares. That is what a reader gets in the second before the script arrives.
    * **The slider reaches the settings the plate draws.** A control that cannot get
      to a setting drawn above it is a picture of a control.
    * **The stylesheet draws the classes the markup uses** and takes the whole thing
      off the printed page. A rename on one side of that pair ships an unstyled
      widget, which is a failure neither file can see alone.

    What is NOT claimed: that the script moves the bar. That is behaviour, and
    behaviour is measured in a browser rather than read out of a file.
    """
    print("\n13  the temperature page's slider")
    page_path = site / "what-is-temperature" / "index.html"
    if not page_path.is_file():
        rep.fail("the slider", "/what-is-temperature/index.html is missing")
        return
    html = page_path.read_text(encoding="utf-8")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("odds", SOURCE / "tools" / "odds.py")
        assert spec and spec.loader
        odds = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(odds)
    except Exception as exc:                       # noqa: BLE001 - reported, not raised
        rep.fail("the slider", f"the odds module could not be loaded: {exc}")
        return
    carriers = [p for p, text in docs.items() if "data-temperature-dial" in text]
    # The script TAG, not the string: the stylesheet's own comment names this file
    # (it explains what unhides the control), and a check reading the bare name
    # reported the stylesheet as a page that loads it.
    namers = [p for p, text in docs.items()
              if re.search(r'<script[^>]+src="/temperature-dial\.js"', text)]
    if carriers != [page_path]:
        rep.fail("the slider's home",
                 f"{len(carriers)} pages carry the control and one should: "
                 f"{', '.join(str(p) for p in carriers) or 'none at all'}")
    elif namers != [page_path]:
        rep.fail("the slider and its script",
                 f"the control is on one page and the script is named by {len(namers)} "
                 f"({', '.join(str(p) for p in namers) or 'none'}) — a control with no "
                 "script is a slider that cannot move")
    else:
        rep.ok("the control and its script",
               "one page carries both, and /temperature-dial.js is what drives it")


    # The table, recomputed from the module the plate is drawn from. This is the whole
    # coupling: the script reads these numbers and does nothing to them.
    table = odds.table()
    # The control's markup, from its opening tag rather than from the attribute that
    # names it: that attribute sits after the container's own class, and starting the
    # slice on it left the container's class outside every question asked below.
    at = html.index("data-temperature-dial")
    blob = html[html.rindex("<", 0, at):]
    found = re.search(r"data-stops='([^']+)'", blob)
    if not found:
        rep.fail("the slider's table", "the control carries no table for the script to read")
    else:
        try:
            shipped = json.loads(found.group(1))
        except ValueError as exc:
            shipped = None
            rep.fail("the slider's table", f"the table is not readable: {exc}")
        if shipped is not None and shipped == table:
            rep.ok(f"the slider's table",
                   f"{len(table)} positions, {odds.STOPS[0]:g} to {odds.STOPS[-1]:g}, "
                   "recomputed from odds.py")
        elif shipped is not None:
            rep.fail("the slider's table",
                     "the page's table is not what odds.py computes")

    # The bar a reader sees before the script arrives, which is the table's default row.
    row = [r for r in table if abs(r["t"] - odds.SETTINGS[1]) < 1e-9][0]
    segs = re.findall(r'<rect data-seg="(\d+)" x="([0-9.]+)" y="0" width="([0-9.]+)" '
                      r'height="([0-9.]+)" fill="([^"]+)" fill-opacity="([0-9.]+)"', blob)
    free = float(re.search(r'data-free="([0-9.]+)"', blob).group(1))
    if len(segs) != len(odds.CANDIDATES):
        rep.fail("the slider's bar",
                 f"{len(segs)} segments are drawn for {len(odds.CANDIDATES)} candidates")
    elif any(abs(float(w) - row["w"][j]) > 0.01 for j, (_i, _x, w, _h, _f, _o)
             in enumerate(segs)):
        rep.fail("the slider's bar",
                 f"the drawn widths are not the table's row for {odds.SETTINGS[1]:g}")
    elif abs(sum(row["w"]) - free) > 0.05:
        rep.fail("the slider's bar",
                 f"the widths add up to {sum(row['w']):.2f} and the bar declares "
                 f"{free:.2f} of free width")
    else:
        rep.ok("the slider's bar",
               f"the odds at {odds.SETTINGS[1]:g} with no script at all")

    # The reach: every setting the plate above it draws, in the table's own steps.
    rng = re.search(r'type="range" min="([0-9.]+)" max="([0-9.]+)" step="([0-9.]+)" '
                    r'value="([0-9.]+)"', blob)
    if not rng:
        rep.fail("the slider's reach", "the control has no range on it")
    else:
        lo, hi, step, value = (float(v) for v in rng.groups())
        if lo > min(odds.SETTINGS) or hi < max(odds.SETTINGS):
            rep.fail("the slider's reach",
                     f"it runs {lo:g} to {hi:g} and the plate draws settings out to "
                     f"{min(odds.SETTINGS):g} and {max(odds.SETTINGS):g}")
        elif abs(step - odds.STOP_STEP) > 1e-9:
            rep.fail("the slider's reach",
                     f"it steps by {step:g} and the table is every {odds.STOP_STEP:g}")
        elif abs(value - odds.SETTINGS[1]) > 1e-9:
            rep.fail("the slider's reach",
                     f"it starts at {value:g} and the drawn bar is the table's "
                     f"{odds.SETTINGS[1]:g}")
        else:
            rep.ok("the slider's reach",
                   f"{lo:g} to {hi:g} by {step:g}, which covers every setting the "
                   "plate draws and starts on the drawn one")


    # Hidden, and the sentence naming the two candidates a reader watches.
    if "data-temperature-dial hidden" not in html:
        rep.fail("the slider's arrival",
                 "the control is not authored hidden — a reader without a script would "
                 "meet a slider that cannot move")
    else:
        rep.ok("the slider's arrival",
               "authored hidden, so the script is what puts it on the page")
    for word, what in ((odds.CANDIDATES[0], "the likeliest candidate"),
                       (odds.CANDIDATES[-1], "the least likely one")):
        span = re.search(r'data-readout="(%s)">([^<]*)<' % (
            "top" if word == odds.CANDIDATES[0] else "last"), html)
        if not span or word not in html:
            rep.fail("the slider's sentence",
                     f"the read-out does not name {what}, so the bar has no legend")
            break
    else:
        rep.ok("the slider's sentence",
               f"names {odds.CANDIDATES[0]} and {odds.CANDIDATES[-1]}, the two ends of "
               "the bar")

    # The stylesheet draws it, and takes it off the paper.
    # Read as a list of names rather than as an attribute holding one name: the
    # container carries its class beside `data-temperature-dial`, and a pattern
    # requiring the quote right after the name reported three of the four classes
    # while the page was correct.
    classes = sorted({c for attr in re.findall(r'class="([^"]*temperature-dial[^"]*)"', blob)
                      for c in attr.split()})
    missing = [c for c in classes if f".{c}" not in library_css]
    if missing:
        rep.fail("the slider's styling",
                 f"{', '.join(missing)} is in the markup and not in the stylesheet")
    else:
        rep.ok("the slider's styling",
               f"{len(classes)} classes drawn by /styles.css")
    printed = library_css[library_css.index("@media print"):]
    if ".temperature-dial" not in printed:
        rep.fail("the slider on paper",
                 "the print world still carries a control nobody can drag")
    else:
        rep.ok("the slider on paper", "the print block leaves the instrument out")


def check_12(rep: Report, site: pathlib.Path, library_css: str) -> None:
    """The directory's two ways between its seventy-five entries.

    Forty of them are one group, so the page offers a jump row and a heading that
    pins while its own group is on screen. Three of those four claims are in two
    different files and one of them cannot be seen at all:

    * The jump row names every group its own headings name, and nothing else. The
      two lists are built from one another by the generator, which is exactly the
      kind of coupling that survives a refactor in one of them and not the other.
    * The row is authored VISIBLE. It is static markup with static links, so a
      reader whose script never ran still gets a way between groups, and the way
      this fails is somebody adding `hidden` beside the find field's own.
    * The pinned heading declares a ground. A sticky heading with a transparent
      background is unreadable the moment an entry scrolls under it, and nothing
      about the source says so: the declaration is the whole promise.
    * The row does not print. It is navigation for a screen, and the library's
      print block is where a page's furniture is already listed.
    """
    print("\n12  the directory's ways between its groups")
    page = site / "library" / "index.html"
    if not page.is_file():
        rep.fail("/library/index.html", "missing from the artifact")
        return
    html = page.read_text(encoding="utf-8")

    # The class list is read as a list: the generator marks these groups with one
    # extra class for their arrival, and a pattern requiring the attribute to hold
    # exactly "index-group" would report every group as missing while the page was
    # perfectly correct.
    ids = set(re.findall(r'<section class="[^"]*\bindex-group\b[^"]*" id="([^"]+)"',
                         html))
    nav = re.search(r'(<nav class="index-jump"[^>]*>)(.*?)</nav>', html, re.S)
    hrefs = set(re.findall(r'href="#([^"]+)"', nav.group(2))) if nav else set()
    if not nav:
        rep.fail("the directory's jump row",
                 "no nav.index-jump in the page — forty entries in one group and "
                 "no way past them but the scroll wheel")
    elif "hidden" in nav.group(1):
        rep.fail("the directory's jump row",
                 "authored hidden, so a reader without script cannot use it: it is "
                 "links, and the script only ever hides it")
    elif hrefs == ids and hrefs:
        rep.ok(f"its jump row names all {len(ids)} groups", "and no others")
    else:
        rep.fail("the directory's jump row",
                 f"jumps to {sorted(hrefs - ids)} which are not groups, and misses "
                 f"{sorted(ids - hrefs)}")

    sticky = re.search(r"\.page-index \.index-group h2 \{(.*?)\}", library_css, re.S)
    body = sticky.group(1) if sticky else ""
    if not re.search(r"position:\s*sticky", body):
        rep.fail("the directory's pinned heading",
                 "no sticky group heading: while a reader scrolls forty entries "
                 "nothing on screen says which group they are in")
    elif not re.search(r"background:\s*var\(--canvas\)", body):
        rep.fail("the directory's pinned heading",
                 "sticky with no ground of its own, so the entries scroll through "
                 "the heading instead of under it")
    else:
        rep.ok("its group heading pins over its own group", "on an opaque ground")

    printed = media_block(library_css, r"print")
    if re.search(r"\.index-jump\s*[,{]|,\s*\n\s*\.index-jump", printed):
        rep.ok("the jump row does not print")
    else:
        rep.fail("the directory's print block",
                 ".index-jump is not listed as furniture, so a sheet of paper "
                 "carries a row of fragment links")


def check_arrival_clock(rep: Report, source: str, css: str) -> None:
    """The arrivals run on one clock, and the page says so in one place.

    M20's mechanism is a single custom property: every duration and delay in the
    arrival family is written as a multiple of --arrive, and the script switches it
    on the block when the reader arrived too fast to watch the arrival finish. The
    behaviour half of that is asserted by audit-motion.py, which drives both paths
    and compares them. What that cannot see is the SHAPE, and the shape is where
    this feature breaks quietly:

      * a rule left with a bare duration still animates correctly, it just stops
        being paced, and no browser test of the fast path would notice;
      * a script that repeated the multiplier instead of reading the property would
        pass every behaviour claim until the two numbers drifted apart - the same
        failure as two copies of the momentum's cap, which this file already checks;
      * an undefined custom property inside calc() is invalid at computed-value
        time, which means NO transition rather than a short one, so the default has
        to resolve everywhere and not only on the blocks that get the class.

    The required expressions below are the family's own timings, each written as a
    multiple. Naming them rather than counting them is the point: a check that only
    counted `var(--arrive)` uses would stay green while one rule lost its clock and
    another gained an extra one.
    """
    print("\nthe arrivals' clock")

    default = re.search(r":root\s*\{\s*--arrive:\s*([\d.]+)\s*;\s*\}", css)
    if not default:
        rep.fail("the arrival's clock has a default",
                 "no :root default for --arrive in the shipped stylesheet - an "
                 "undefined custom property in calc() makes the whole declaration "
                 "invalid, so a block that misses the class would lose its "
                 "transition entirely rather than keep the authored one")
        return
    if float(default.group(1)) != 1:
        rep.fail("the arrival's clock has a default",
                 f"the default is {default.group(1)} where the authored clock is 1")
    else:
        rep.ok("the arrival's clock has a default",
               "--arrive: 1 at :root, so every rule that reads it always resolves")

    quick = re.search(r"\.reveal\.is-quick\s*\{\s*--arrive:\s*([\d.]+)\s*;\s*\}", css)
    if not quick:
        rep.fail("the quick clock is a fraction of the authored one",
                 "no .reveal.is-quick override for --arrive: the class the script "
                 "adds would change nothing")
    elif not 0 < float(quick.group(1)) < 1:
        rep.fail("the quick clock is a fraction of the authored one",
                 f"--arrive: {quick.group(1)} is not a shortening the class can mean")
    else:
        rep.ok("the quick clock is a fraction of the authored one",
               f"--arrive: {quick.group(1)} for a block the reader arrived at speed")

    # Each of these is one timing in the family, and each is a step that cannot be
    # scaled without the others. The plate's 2s claim is the longest, the windows'
    # 700ms is the most common, and the rest are the staggers that make a block read
    # as a sequence rather than a single fade.
    required = (("calc(var(--arrive) * 700ms)", "the windows' 700ms entrance"),
                ("calc(var(--arrive) * 2000ms)", "the plate's 2s claim"),
                ("calc(var(--arrive) * 1400ms)", "the hole ring's roll"),
                ("calc(var(--arrive) * 480ms)", "a reading-log row"),
                ("calc(var(--arrive) * 720ms)", "the last tick's delay"),
                ("calc(var(--arrive) * 500ms)", "an evidence row"))
    lost = [name for expr, name in required if expr not in css]
    if lost:
        rep.fail("every timing in the family reads the clock",
                 f"these lost it: {', '.join(lost)} - a bare duration still animates "
                 "and would silently stop being paced")
    else:
        rep.ok("every timing in the family reads the clock",
               f"{len(required)} named timings, each a multiple of --arrive")

    # One copy of the multiplier, and it is not in the script. The counter is the
    # one thing the script times itself, and it has to keep the rows' clock, so it
    # reads the property back rather than repeating the number.
    if "getPropertyValue('--arrive')" not in source:
        rep.fail("the counter reads the clock rather than repeating it",
                 "the script no longer reads --arrive back off the block, so the "
                 "counter's chain has a timing of its own")
    elif re.search(r"\*\s*0\.3\b", source):
        rep.fail("the counter reads the clock rather than repeating it",
                 "the script multiplies by 0.3 as well, which is two numbers that "
                 "can drift apart")
    else:
        rep.ok("the counter reads the clock rather than repeating it",
               "the chain's steps are scaled by the property the stylesheet owns")

    # ARRIVE_MS is the arrival's authored length, and it is the counter's last step:
    # two facts that have to be one fact, since the pacing test measures the reader's
    # travel over exactly that window.
    named = re.search(r"var ARRIVE_MS = (\d+);", source)
    chain = re.search(r"var steps = \[\d+, \d+, \d+, ARRIVE_MS\];", source)
    used = re.search(r"pace \* ARRIVE_MS > window\.innerHeight", source)
    if not (named and chain and used):
        rep.fail("the arrival's length is named once and used where it claims",
                 "missing: " + ", ".join(n for n, m in
                 (("the constant", named), ("the chain's last step", chain),
                  ("the pacing inequality", used)) if not m))
    else:
        rep.ok("the arrival's length is named once and used where it claims",
               f"{named.group(1)}ms is the counter's last step and the window the "
               "reader's travel is measured over")


def main(argv: list[str]) -> int:
    # The Windows console is cp1252 by default, and this file's output is full of
    # section signs and em dashes. Reconfigure rather than strip them: the
    # verdict lines are the only thing a reader sees, and mojibake there wastes
    # more time than the encoding fix costs.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    site = pathlib.Path(argv[1] if len(argv) > 1 else "_site")
    if not site.is_dir():
        print(f"error: {site} is not a directory — run build-site.py first",
              file=sys.stderr)
        return 1

    page = (site / "index.html").read_text(encoding="utf-8")
    docs: dict[pathlib.Path, str] = {}
    for p in sorted(site.rglob("*")):
        if p.is_file() and p.suffix.lower() in (".html", ".htm", ".css"):
            docs[p] = p.read_text(encoding="utf-8", errors="replace")

    # The stylesheet lives inlined in the page; checks 6 and 7 read it from
    # there so they measure what ships, not what Source/ holds. A build that
    # failed to inline would already have failed verify-budget.py's check 3.
    style = re.search(r"<style\b[^>]*>(.*?)</style>", page, re.S | re.I)
    css = style.group(1) if style else page

    rep = Report()
    check_4(rep, site, docs)
    check_5(rep, page)
    check_6(rep, css)
    check_7(rep, page, css)
    check_8(rep, page)
    check_gears(rep, page)
    source_path = SOURCE / "index.html"
    if not source_path.is_file():
        rep.fail("the notes can be read at all",
                 f"{source_path} is missing, so nothing compares the code to the "
                 "numbers its notes quote")
    else:
        source = source_path.read_text(encoding="utf-8")
        check_momentum(rep, source, page)
        check_poster_mark(rep, page, css)
        # The arrivals' clock is read from the SHIPPED stylesheet, because that is
        # what a reader gets and what the check is about: a rule that lost its clock
        # in `Source/styles.css` would reach the page through the build.
        check_arrival_clock(rep, source, css)
    check_9(rep, site, docs)
    library_css = (site / "styles.css").read_text(encoding="utf-8")
    notfound = re.search(r"<style\b[^>]*>(.*?)</style>",
                         (site / "404.html").read_text(encoding="utf-8"), re.S | re.I)
    check_10(rep, css, library_css, notfound.group(1) if notfound else "")
    check_11(rep, site, library_css)
    check_12(rep, site, library_css)
    check_13(rep, site, docs, library_css)
    check_library_arrivals(rep, site, docs)
    check_page_marks(rep, site, docs)
    check_search(rep, site, docs)
    check_newlines(rep, site)

    print()
    if rep.failures:
        print(f"FAILED - {len(rep.failures)} of {rep.checks} assertions",
              file=sys.stderr)
        for f in rep.failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print(f"links ok - {rep.checks} assertions, Stage 9 checks 4-12")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
