# The plates of istor.fyi - an auditor's guide

One page. Every drawing on it is generated, committed, and held to one rule:
**a drawn label is a phrase the page already prints.** The drawing is
arithmetic on the page's own words, never a second place the argument lives.
This guide lists every plate on the landing page, the prose each one
transcribes, and the command that proves each claim. Everything below
reproduces from a fresh clone of `main` with nothing else.

## The one-command audit

    python Source/tools/verify-all.py

Checks HEAD out into a temporary worktree, builds there, and runs every gate
against nothing but what the commit carries - one signed line per gate, the
worktree removed whatever happens. `--quick` skips the two headless audits,
`--report` files a signed markdown beside the audit JSONs (the directory is
created if absent). The claim above - a fresh clone, nothing else - was
executed, not just stated: cloned to an empty directory, `--report` run in
full, green (figures 189 | budget 24 | copy 7 | links 123 | contrast 0 below
AA across all twelve passes, the printed sheet included | motion 58/58) - and
re-executed at the handoff commit 5f13d67, green again in 5.4 minutes, so
the line the reader is standing on is the line that was proven.

## The individual gates

| Claim                                    | Command                                        |
|------------------------------------------|------------------------------------------------|
| Every figure is its generator's output   | `python Source/tools/verify-figures.py`        |
| Every drawn string is printed prose      | (inside verify-figures - the verbatim census)  |
| Every byte as the design plan has it     | `python Source/tools/verify-budget.py`         |
| No release claims in any published text  | `python Source/tools/verify-copy.py`           |
| Every link and artifact resolves         | `python Source/tools/verify-links.py`          |
| Contrast, type floor, print, separators  | `python Source/tools/audit-contrast.py --pages /` |
| The two worlds of motion, driven not read| `python Source/tools/audit-motion.py --jobs 4` |

The contrast audit measures all six theme states (`single-theme`,
`+contrast-more`, `+os-dark`, both combined, `+print-on`, plus the separator,
reduced-motion, layout and type-floor passes) and prints `0 below AA` in
each. The motion audit drives the page in both motion worlds; its own

## CI: the same gates, and a guard on what ships

Every push to `main` runs the figures, build, budget, links and copy gates on
the runner (`.github/workflows/deploy.yml`), then deploy-pages, then a
**post-deploy smoke test** that fetches the live site and asserts the
handoff markers in the served bytes (the chip relabel, the skip-link target,
`xml:lang="el"`, the curly-apostrophe typography, the figure apostrophes on a
library page). The gated path's one external dependency - `fonttools` plus
`brotli`, which make-didot-greek's WOFF2 encoder needs - is installed in the
workflow; the smoke test is what caught-and-would-catch a stale artifact
shipping quietly (it happened: three days of red deploys while local gates
stayed green, fixed 2026-09-26).
truthfulness is checkable with `audit-motion.py --self-test --family land`,
which doctors pages and demands the audit catch each doctoring.

## The plates, act by act

**Hero** - `hero-gears.svg` (decorative, `aria-hidden`, states nothing a
reader must trust from a picture) and the calendar arc behind the stop act's
copy (`calendar-ring.svg`, 355 holes at the caption's own 1.0141 degrees).

**Act 2, the gate** (#how-it-answers) - `gate-wide/tall.svg`, M46. The
decision the prose performs: the question, the small model's test
(*is this already answered here?*), and the two outcomes the act states -
*answers from them* / *never goes online*, *slow, and can be right* - with
the branch edges named **Yes**/**Not yet** exactly as the FAQ's answers
capitalize them, and the caption line *the cheap question goes first*.
The test node is the plate's one azure.

**Act 3, the passage** (#the-passage) - `unverified-wide/tall.svg`, M47. The
mark no capture shows: the small model fits a citation, **Unverified,**
**check the source.** sits on **a good answer**, and the one dashed line
runs open to **the passage behind the claim**. Caption: *That word is not a
guess about truth.* - the act's own sentence.

**Act 4/5** - the reading log and the dispute table are DOM, not drawings;
their honesty is that they are the page's own text.

**Act 7, the library** (#the-library) - `shelf-wide/tall.svg`, M45. The ten
documents as rows, transcribed from the page's notes rail, plus the footer
*every one of them a document on this machine*.

**Act 8, the stop** (#where-it-stops) - the ring declines to answer the
dispute; see the evidence act.

**Act 9, the evidence** (#the-evidence) - `two-rings` (354 and 355 on one
radius, an x12 lens, the dash pitches reproducing 360/354 and 360/355),
`parapegma` (forty-four keyed rows transcribed whole, damage brackets kept),
`rear-dials` (Metonic 5 turns / 235 slots, Saros 4 / 223), `exeligmos`
(three exact thirds, H = +8h, Iϛ = +16h, 8 + 8 + 8 = 24), `games-dial`
(four sectors, six games twice each, the one anticlockwise arrow),
`front-dial` (twelve zodiac sectors, the three recovered month names, the
two lights; the hole count left uncounted on purpose).

**Act 10, the questions** - `boundary-wide/mid/tall.svg`: the documents, the
app and the model inside; the wire that leaves is off.

**Act 11, the name** - `etymology.svg` / `etymology-tall.svg`: one root,
three descendants, the asterisk drawn where the page explains it.

**The close** - `close-gears.svg`, `poster-horizon.svg`, `poster-veil.svg`
(decorative).

## The two invariants worth probing by hand

1. **Verbatim.** Edit any string a plate draws to something the page does
   not print - say, add a word to a shelf footer - and
   `verify-figures.py` fails with the census naming the string. Edit the
   page instead, and the same gate catches the drawing left behind.
2. **Self-consistency.** Change anything without regenerating, and the
   byte-identity half of the same gate reports the first differing byte.
   The audit cannot be green over a page nobody can reproduce.

## Where the reasoning lives

Each generator's header records what the source states and what is
deliberately absent; each plate's ink grammar is its 14d block in
`Source/styles.css`; the per-milestone decisions, the gap-session
reconciliation, and every instrument lesson are in
`.improvement/OVERNIGHT_LOG.md` (M42-M49, then FINALIZATION).
