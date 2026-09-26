# Handoff: auditing the istor.fyi landing page

For the developer auditing this site. Everything below runs from a fresh clone
of `main` needing nothing but Python 3 and an installed Chrome. The date on
every claim in this file is 2026-09-26; each one was executed, not stated, and
the commands re-prove them.

## Start here: the one command

    python Source/tools/verify-all.py --report

Checks HEAD out into a temporary worktree, builds it there, and runs all seven
gates against nothing but what the commit carries - build, figures, budget,
copy, links, contrast, motion - then removes the worktree whatever happens.
Green in about 5.5 minutes. `--report` writes a signed markdown verdict into
`.improvement/audits/` (gitignored; the directory is created if absent) beside
the contrast and motion JSONs, stamped with the commit and time. Failing runs
write reports too. `--quick` skips the two browser audits for a ~15-second
mid-edit check. The fresh-clone path itself was executed on 2026-09-26:
clone to an empty directory, full run, green at `b80612a`.

## What each gate guarantees

| gate | asserts |
|---|---|
| build | the site compiles; every figure include has a page marker |
| figures (189) | every committed SVG is byte-identical to its generator's output; every drawn string is printed page prose or declared in its generator with its citation (the **census**); every label's measured extent lands inside its viewBox (the **extents gate**); every SVG parses as XML (well-formedness) |
| budget (24) | every byte size the design plan asserts, HTML/JS/gzip/figures |
| copy (7) | no em/en dashes in any visible string; the release-claim rule |
| links (123) | every link resolves; no colour outside a token; the act rhythm; LF-only files; the previous/next walk through all 75 articles |
| contrast | 0 below AA across twelve passes: light/dark x (plain, contrast-more), no-JS, the printed sheet, separators, reduced motion, layout CLS at slow fonts, and the type floor (11px rendered, 320-1440 plus the sheet) |
| motion (58) | the reduced-motion world is honest; arrivals get the authored clock; the counter keeps the rows' clock (median-of-gaps, jitter-immune); a page-sized jump is not a gesture; the harness's own self-test catches 54/54 doctored pages |

Negative tests are built in, not oral tradition: plant an unprinted phrase in
a figure and the census fails it; plant an unmeasured or overhanging label and
the extents gate fails it; break an SVG and the well-formedness check fails
it; doctor a page's motion and the self-test catches it.

## What the gates do NOT cover (hand-checked 2026-09-26)

The audits measure contrast, bytes, links, type, and motion. These dimensions
were probed by hand against the built page; the findings and the clean bills
are recorded in `.improvement/OVERNIGHT_LOG.md` (M52, M55, and the two
uncommitted-pass entries):

- **Screen-reader semantics**: all 226 Greek-text elements resolve to
  `lang="el"` (the parapegma's forty-four inscriptions, the zodiac signs, the
  month names, the site's own name); all seven exhibit images carry genuinely
  descriptive alt text; every displayed SVG is labelled or deliberately
  hidden; no heading-level skips; no bare links; all navs named; inputs
  labelled.
- **Keyboard flow**: the nav CTA's standdown removes it from tab order exactly
  while an equivalent action is on screen; a Tab into a cold reveal block
  scrolls to the element, fires the reveal, and shows it before the next Tab;
  zero positive tabindex anywhere.
- **Cold reads at 390px and 1440px**: no label outside its plate, no text
  past the viewport, no horizontal overflow.

## Where the reasoning lives

- `Documentation/PLATES_AUDIT_GUIDE.md` - every drawn plate, the exact prose
  it transcribes, and the command that proves each claim.
- `Source/tools/make-*.py` headers - what each drawing's source states, what
  it measures, and what it deliberately leaves absent.
- The `14d*` blocks in `Source/styles.css` - each plate's ink grammar and its
  per-ground remaps.
- `.improvement/OVERNIGHT_LOG.md` - the per-milestone reasoning, M42 through
  M55, including every gate defect the session found in its own instruments.

## Working-tree state at handoff

HEAD is green and self-contained; verify-all proves exactly that from the
commit. The gap session's curly-apostrophe figure work, the budget
re-baseline note and the design plan's nav-state record were landed at
`a7e460f` (verify-all green there), so the working tree now carries exactly
one deliberate rider:

- `Source/tools/freebuff-continue.py` - the operator's own macro-tuning edit;
  never commit it as part of site work.
- (untracked, session scaffolding): `AvailableTools.txt`, `.freebuff/`.
