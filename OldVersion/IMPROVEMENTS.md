# Improvements

The continuous-improvement loop's report file. One entry per cycle, newest at
the top, written by Phase 6 of
[`.claude/skills/continuous-improvement/SKILL.md`](.claude/skills/continuous-improvement/SKILL.md).

Two rules for this file:

- **Newest first, and old entries are never rewritten.** Append at the top and
  leave the rest alone. The record of what the loop believed at the time is part
  of what the file is for, mistakes included.
- **This is the loop's public record.** The audit logs, the council verdicts and
  the defect register live in `.improvement/`, which is gitignored and dies with
  the machine. What survives a clone is this file and the `Loop-Cycle:` /
  `Loop-Full-Audit:` trailers on the commits.

Cycles 1 and 2 ran before this file existed. They are reconstructed from the
commit trailers and the defect register, and they are marked as reconstructed.
Nothing in them is invented. Where a trailer's number disagrees with a later
measurement, both are shown rather than one being quietly preferred.

---

## Not a cycle: the bench was proved, and a tripwire tripped, 2026-09-17

Not a cycle. No `Loop-Cycle:` trailer, so the count stays at 10. Follows the
entry below, which installed the bench and wrote Phase 8; this one ran the pass
once and read the counters honestly.

**Shipped:** nothing to the site. Nothing to the loop either, beyond two traps
and one measurement rule added to the skill.

**The pass was proved once, not only written.** A procedure that has never
executed is D-014, so the bench was a dry run the same day it was written, on the
real homepage, shipping nothing. Two things came out of it that reading could not
have produced.

First, **`.improvement/canvas.html` did not exist.** The skill had been
describing it as the instrument Phase 8 runs on — "generalising
`.improvement/band.html` into a `.improvement/canvas.html`" — while no such file
was on disk. It exists now: the page's real stylesheet, the real box, both
themes, the modes the procedure calls for (thumbnail, flip, desaturate, between
neighbours), and a `canvas-ready` flag on the title so a driver cannot
photograph a half-decoded image.

Second, **it produced a named fault, not a preference.** The subject was
`index.html`'s closing section, which is genuinely flat: a centred heading and a
pill in a wide white field with the lower half inert void. Pass 1's fault — the
light sat 62 px under the arc's apex where the arc's own belly was 130 px down,
so the arc read as a stroke laid over a gradient rather than a form holding a
light. Pass 2 moved the light into the belly. The loop closes: look, name,
change, re-render.

**The dry run caught its own instrument lying**, which is cycle 2's lesson
arriving again from a new direction. The first measurement found the arc by
"pixels more red than blue". That worked until the light behind it got stronger,
at which point the same test started counting the *light* as stroke and reported
the apex 115 px lower — a revision appearing to have moved something it never
touched. Subtracting a median-filtered copy of the image isolates the thin stroke
properly, and the check that proved it is now in the skill: **measure an element
the change cannot affect — if it did not move, its number must not move either.**
The skill also now records that the eye is worse than the number at symmetry and
better than it at meaning: the first fault was called by looking, and the
measurement then showed the arc was symmetric to 0.0 px.

**The tripwire is tripped, for the first time.** Improvement commits since the
last full audit stand at **13** — ten carrying a `Loop-Cycle:` trailer, plus
`e9a3075` (D-013), `68ad20c` (D-014) and `1a42daf` (D-015) — against a tripwire
of 12, and no full audit has ever run. **The next cycle runs Phase 7 before
anything else**, and a tripped budget outranks a creativity trigger. Recorded in
the budget table and here rather than left for Phase 0 to discover, because "the
count reached the tripwire and nothing ran" is D-014 exactly, and repeating it in
the commit that fixed it would be a poor joke.

**Budgets, re-measured:** repo weight 2.50 MB against 2.47 MB last written, all
of the movement being the skill's own rewrite, which is what that row measures.
Home critical path 169 KB, unchanged. Off-site runtime requests still 0.

**Open:** S1 0, S2 0, S3 3 — D-010, D-011 (deferred), D-012. Unmoved.

**Blocked:** nothing.

---

## Not a cycle: the loop gained a making pass, 2026-09-17

Not a cycle, and no `Loop-Cycle:` trailer, so the count stays at 10. Recorded
because the next agent needs to know why the skill changed and what is now on the
machine.

**Shipped:** nothing to the site. One S1 defect was in the loop's own design.

**D-015, S1 — the loop could not choose visual work, and had no counter that
would ever have noticed.** `svg`, `illustration`, `icon` and `draw` appeared
**zero times** in the entire skill. Blender appeared once in Phase 3's asset
parenthetical and once in a tool connector reading *"Not installed; propose it
when an idea genuinely needs it"*; ffmpeg's read *"Not installed."* The install
gate said installing was Thoria's call, so a visual idea arrived at the council
as a sentence priced by an agent that had never produced one, against repairs
whose cost it knew exactly — and lost every time. The `one genuine bet per cycle`
obligation could then be carried forward forever, honourably, with **nothing
counting it**. Neither reconstructed cycle recorded a bet and nothing noticed.

That is the exact shape of D-014: a thing that never happens because no counter
exists to make it happen. D-014 was a pass that had never run in 131 commits.
This was a capability that could not run at all.

**The fix: Phase 8, the creativity pass.** Shaped like Phase 7 — its own scope,
procedure, verdicts, report and trailer — and triggered three ways: Thoria asks,
three cycles carry the bet unspent (now counted in a new `Loop-Bet:` trailer), or
the register has nothing left worth fixing. A tripped budget still outranks it:
audit before you make.

The load-bearing difference is the council. **On this pass it is a critique, not
a gate.** Truth and Fit still kill an artefact outright — nothing polishes a lie
or a wrong-site idea — but everything that clears them gets **one change** and a
return to the bench rather than a kill vote. Killing stays legal and must be
argued with the fault that survived revision; "I don't like it" is taste, which
Doctrine 8 already forbade as a verdict.

**The bench, which is the other half.** A pass with no tools is a pass that
produces prose about pictures. Verified installed and working the same day:

| | | |
|---|---|---|
| Blender | 5.2.1 LTS | headless via `blender -b -P` |
| Inkscape | 1.4.4 | rasterised a real SVG to PNG in the check |
| ImageMagick | 7.1.2-31 Q16-HDRI | delegates `webp heic jpeg png lcms` |

ffmpeg 7.1, Python 3.14.4 (PIL/numpy/scipy/matplotlib) and Node 24 were already
present. **The ImageMagick delegate claim was the one thing asserted before it
was proved, so it was proved**: a real 324-byte `.avif` was encoded, through the
`heic` delegate rather than an `avif` one. The full delegate line, read rather
than skimmed, also turned up `lcms` and `rsvg`: `lcms` lifts D-011's tooling
blocker, and `rsvg` means `magick` rasterises SVG on its own, proved by drawing a
real 64px SVG to a 1,932-byte PNG.

Two tools were considered and deliberately **not** installed, so nobody
re-litigates them: `rsvg-convert` (no winget package; MSYS2 is a large surface
for one binary, and the capability is already on the bench three ways — Inkscape,
headless Chrome, and that `rsvg` delegate, so installing the standalone binary
would buy a name rather than a capability) and `cwebp`/`avifenc` (redundant —
`magick` links libwebp and libheif).

**The trap worth naming loudly.** `convert` on this machine is
`C:\WINDOWS\system32\convert`, the FAT→NTFS filesystem tool, which answers *"Must
specify a file system"*. It is not ImageMagick, and a plausible-looking
`convert /FS:NTFS C:` does real damage. ImageMagick 7 installs the `magick` name
partly so this collision cannot happen. **Use `magick`, never `convert`.**

**Two smaller traps, both observed rather than predicted.** PATH does not refresh
in a running shell, so `magick` read "not found" in the very session that
installed it while the machine PATH already carried its directory — and Inkscape
and Blender are on no PATH at all, which is why the skill's table gives absolute
paths. And `ffmpeg` here is the gyan.dev **essentials** build, so the codec list
is a real limit to check with `ffmpeg -encoders` rather than assume.

**Also changed**

- **`Loop-Bet:`** joins the per-commit trailers, alongside Cycle, Budget and
  Open. It reads `spent` or `carried N`, and it is what makes the bet obligation
  countable. This also resolves a real contradiction: the checklist said "four
  trailers" while the block described three.
- **Generated assets now ship their generator** under `tools/`, committed with
  the record in `assets/*/SOURCE.md`. A blob nobody can rebuild is a blob nobody
  can revise, and it dies with the machine exactly as `.improvement/` does.
- **The install rule changed.** Free asset-generation tools install without
  asking, and are recorded with their exact command in the same commit that first
  uses them. Paid, account-gated, licensed, over ~2 GB, or anything that would
  put a request on the wire at runtime still stops and asks.
- **Doctrine 16** — *taste is not a verdict; a named fault is.* The list sat at
  fifteen including the retired #11 tombstone, so the header now says retired
  entries do not count toward the fifteen: fourteen live, one slot used.
- Two anti-patterns added: making an artefact to fill a pass with no flat subject
  that asked for it, and committing a generated asset without its generator.
- `README.md` records the pass, the four trailers and `tools/`.

**`Loop-Bet:` starts at 0.** Cycles 1 and 2 are not counted as carried: they
never recorded a bet, so there is no data either way, and inferring a carry to
make the counter fire sooner would be rigging it. The count begins with the next
commit. That the first two cycles are simply unmeasurable is the finding.

**Open:** S1 0, S2 0, S3 3 — D-010, D-011 (deferred), D-012. D-011's tooling
blocker is lifted but its craft decision is still Thoria's.

**Blocked:** nothing.

---

## Not a cycle: the loop audited itself, 2026-09-17

Not a cycle, and no `Loop-Cycle:` trailer was written for it. This was an audit
of the loop rather than of the site, so the count stays at 10 and keeps meaning
what it says. It is recorded here because the next agent needs to know why the
skill changed.

**Shipped:** nothing to the site. Two S1 defects were in the loop's own rules.

**Fixes**

- **D-013** — two laws forbade a showcase section the homepage had been serving
  since 2026-09-01. `.claude/skills/istor-brand/SKILL.md` and
  `design-references.md` now record the scene as adopted and say the prohibition
  is superseded. Not a revert of the section: it is Thoria's own commit
  (`c89b126`), so the docs moved to reality and reality stayed.
- **D-014** — the structural cause, and the worse of the two. The
  doc-against-reality read lived only in Phase 7, and Phase 7 had never run:
  zero `Loop-Full-Audit:` trailers in 131 commits, against a tripwire of twelve
  improvement commits and a count of ten. That check now runs in Phase 1a, every
  cycle, whatever the scope. The skill and `.gitignore` were both untracked, so
  a fresh clone lost the loop, the register protection and the trailer
  convention; both are committed now. `.playwright-mcp/` was not gitignored, so
  the browser tool's profile was sitting in the tree and being counted by the
  loop's own shipped-weight command.

**Also changed, all inside the skill**

- The scope rule is operating rule 8 and leads Phase 0 and Phase 1a: the
  homepage is the creative surface, the 75 slug pages are audited and
  maintained. Ideas belong on `index.html`; fixes belong anywhere.
- The budget table was corrected. Slug pages said 76 and the tree has 75. Repo
  weight said 2.40 MB and the tree reads 2.47 MB, most of that difference being
  the skill's own rewrite, which is the clearest possible demonstration of what
  that row measures. The canonical commands were counting scratch: with no
  exclusions they read about 5.2 MB against a real 2.5 MB. `Baseline` became
  `Measured`, and a homepage-composition row was added whose tripwire is a
  written sentence rather than a retrospective.
- The trailer block is labelled an example, carries the `shipped` figure cycle 2
  was already writing, and states that `deferred` counts as open in `Loop-Open`.
- The scroll-reveal trap is named in Phase 5: a single full-page screenshot shows
  blocks at `opacity: 0` that a reader sees perfectly well, so the instrument
  produced the blank.
- Phase 6 now says where the report goes. This is that file.
- `.claude/settings.json` gained a SessionStart hook, so a new session picks the
  loop up instead of waiting to be told.

**Open:** S1 0, S2 0, S3 3 — D-010, D-011 (deferred), D-012. None of it moved by
this work.

**Blocked:** nothing.

---

## Cycle 2, 2026-09-17 — reconstructed

Reconstructed from the `Loop-Cycle: 2` trailers and the register. Five commits:
`1339b5d`, `f634411`, `491f864`, `5f65776`, `0afebbd`.

**Shipped**

- `1339b5d` Band texture: 12,829,123 bytes down to 1,542,136, chosen by SSIM at
  every measured box and DPR. Closed D-008.
- `f634411` Project log: four missing days written from `git log`, plus the
  ritual that keeps `/changelog/` current. Closed D-005.
- `491f864` Showcase: the notebook window is now one `role="img"` with a label,
  verified against Chromium's real accessibility tree. Closed D-007.
- `5f65776` Feature cards: the site's last hairline card removed, so the ground
  does the separating. Closed D-006.
- `0afebbd` README law 2: a `<noscript>` block belongs after the stylesheet
  link, recording cycle 1's D-009 as law.

**Found:** D-010, D-011 (both S3, the dark card ground and the Adobe RGB
profile), and D-012, which was found while writing the changelog ritual rather
than shipped with it.

**Two of the loop's own checkers were lying, and both were fixed before any of
their findings were believed.** The meta-description check stopped at the first
apostrophe inside `content="..."` and invented seven-character descriptions
across the fleet; a parser says all are unique, 125 to 239 characters. The first
link check read every absolute href as a page path and reported 225 broken
links, all of them assets that exist. This is where Doctrine 14 comes from.

**Budgets, verbatim from the trailer:** `pages 77/97, css 35/44KB, home
169/226KB, requests 0/0, shipped 2.40/15.9MB`

**Open at close:** S1 0, S2 0, S3 3.

**Next, as cycle 2 saw it:** the two deferred S3 items needed eyes, not
arithmetic.

---

## Cycle 1, 2026-09-17 — reconstructed

Reconstructed from the `Loop-Cycle: 1` trailers and the register. This is the
cycle that opened the register, so nothing was inherited. Five commits:
`29c19a7`, `988699f`, `4fac4bf`, `7d93a1a`, `a6d08ce`.

**Shipped**

- `29c19a7` A slug that never existed, linked from `what-is-reranking`: the one
  broken internal link in the fleet, found by resolving all 1,467 references.
  Closed D-001.
- `988699f` README law 4: the band's texture is the studio photograph Thoria
  supplied, not the ambientCG paper the law named. Closed D-002.
- `4fac4bf` 74 sub-pages dropped their FAQPage JSON-LD: 124,379 bytes of markup
  describing questions no reader could see, for a rich result Google had already
  deprecated and de-documented. Closed D-003. The homepage kept its block
  because its five questions are visibly on the page.
- `7d93a1a` Showcase: under reduced motion the sheet ends on its answer rather
  than a blank page. Closed D-004.
- `a6d08ce` `index.html`: the `<noscript>` block moved below the stylesheet, so
  with JS off a reader gets all four privacy claims instead of one. Closed D-009.
  This became README law 2.

**Found and carried:** D-005, D-006, D-007, D-008, all closed in cycle 2.

**A correction, kept rather than tidied.** The `Loop-Open:` trailer on `a6d08ce`
reads `S2 3`, which is one too many: D-004's fix was already verified when it was
written. History is not rewritten to hide a bookkeeping slip, and the register is
the source of truth.

**Budgets, verbatim from the trailer:** `pages 77/97, css 34/44KB, home
166/226KB, requests 0/0`

**Open at close:** S1 0, S2 3, S3 2.

**Next, as cycle 1 saw it:** the four findings it could not close in one pass.
