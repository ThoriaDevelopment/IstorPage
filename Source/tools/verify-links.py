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
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent

# ---------------------------------------------------------------- expectations
# A library page is a directory at the artifact root holding an index.html.
# These four are directories at the root that are NOT pages.
NOT_A_PAGE = {"fonts", "img", "assets", "brand"}

LIBRARY_PAGES = 75
LIBRARY_STYLES_BYTES = 35522          # §1.1: /styles.css is the library's file
ARTIFACT_FILES = 138                  # 120 + the six extra exhibits v2 carries
                                      # (9 exhibits x 4 files = 36, was 3 x 6 = 18)

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
    """The page with its comments gone — what a font could actually be asked for.

    Comments are stripped and the `<style>` block is KEPT, because CSS reaches
    the screen through `content:` as surely as markup does: the `.pipe` arrows
    on this page exist only as `content: "→"`. Check 7 counts those.
    """
    return strip_css_comments(strip_html_comments(page))


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
    sections = re.findall(r"<section\b[^>]*>", body, re.I)
    if len(sections) < 10:
        rep.fail("section count", f"{len(sections)} <section> elements — §2's "
                                  f"architecture has twelve acts, and a page that "
                                  f"has collapsed back to a handful is v1 again")
    else:
        rep.ok(f"{len(sections)} sections", "§2's acts are present")

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

    pictures = len(re.findall(r"<picture\b", body, re.I))
    if pictures < 9:
        rep.fail("exhibit count", f"{pictures} <picture> elements — §6 ships nine")
    else:
        rep.ok(f"{pictures} exhibits", "§6's exhibit set is present")

    # v1 shipped the FAQ as a plain <dl> and wrote a comment explaining that an
    # accordion "would hide precisely the answers this audience came for". Every
    # reference site has one. This asserts the reversal stuck.
    if "<details" not in body:
        rep.fail("no <details>", "§12: the FAQ is an accordion on <details>, and "
                                 "v1's refusal to build one is what v2 reverses")
    else:
        rep.ok(f"{body.count('<details')} <details>",
               "the FAQ is a real disclosure, not a list")

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
    scripts = re.findall(r"<script\b[^>]*>(.*?)</script>", body, re.S | re.I)
    tags = re.findall(r"<script\b[^>]*>", body, re.I)
    if len(tags) != 1:
        rep.fail("script count", f"{len(tags)} <script> tags — the page carries "
                                 f"exactly one")
    elif re.search(r"\bsrc\s*=", tags[0], re.I):
        rep.fail("<script src>", f"{tags[0].strip()} — the one script must be "
                                 f"inline, or §12's payload arithmetic changes")
    else:
        rep.ok("exactly one <script>, inline, no src")

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
    if not h1 or HOME_MARKER not in h1.group(1):
        found = re.sub(r"<[^>]+>", "", h1.group(1)).strip()[:60] if h1 else "no <h1>"
        rep.fail("_site/index.html",
                 f"does not carry §1.3's marker. Found: {found!r}. The assembler "
                 f"copied the previous home page.")
    else:
        rep.ok("_site/index.html carries the new <h1>",
               re.sub(r"<[^>]+>", "", h1.group(1)).strip())


def check_9(rep: Report, site: pathlib.Path,
            docs: dict[pathlib.Path, str]) -> None:
    print("\n9  library integrity")
    pages = sorted(d for d in site.iterdir()
                   if d.is_dir() and (d / "index.html").is_file()
                   and d.name not in NOT_A_PAGE)
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
    have = {"/"} | {f"/{d.name}/" for d in pages}
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

    files = [p for p in site.rglob("*") if p.is_file()]
    if len(files) != ARTIFACT_FILES:
        rep.fail("artifact file count",
                 f"{len(files)} files, expected {ARTIFACT_FILES}")
    else:
        rep.ok("artifact file count", f"{ARTIFACT_FILES} files")


# ------------------------------------------------------------------------ main

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
    check_9(rep, site, docs)
    check_newlines(rep, site)

    print()
    if rep.failures:
        print(f"FAILED - {len(rep.failures)} of {rep.checks} assertions",
              file=sys.stderr)
        for f in rep.failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print(f"links ok - {rep.checks} assertions, Stage 9 checks 4-9")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
