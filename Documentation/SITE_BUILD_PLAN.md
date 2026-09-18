# Istor landing page — build plan

`Documentation/SITE_DESIGN_PLAN.md` is the specification. It decides what the page is, what it
says, which colours and sizes it uses, and why. **This document does not decide any of that.** It
says in what order the page gets built, where each file lives, what machine checks the result, and
what every string on the page actually reads. Where the two disagree, the design plan is right and
this one is wrong.

It is a build plan for **one page** — the landing page the design plan specifies — plus the carriage
of the **75-page content library** that already lives at `istor.fyi`. It is not a plan for
redesigning that library; §5 decides that it ships as it is, and says why.

---

## 0. Scope

**In scope:** the repository layout, the assembler, the two generators that do not exist yet, the
publishing workflow, the verification gates, and the copy deck.

**Out of scope, named so it is not silently assumed:**

| | |
|---|---|
| Any design decision | the design plan owns all of them (§8 principles included) |
| **Redesigning the 75 legacy content pages** | **carried verbatim, decided §5.** They ship exactly as they are — no typography change, no cleanup, no rewrites. Redesigning them is a later, separate job |
| The app | `C:\Projects\Istor\Source` is read-only for website work |
| A framework, a bundler, a CMS | the page is hand-written HTML and one stylesheet |
| Analytics, tag manager, consent banner | forbidden by the design plan's head, §7 |
| Regenerating artwork in CI | artwork is generated locally and committed; CI only asserts it (§3, Stage 0) |

**The one architectural rule this plan adds.** Generators are local tools; their outputs are
committed. The workflow never runs `magick`, Inkscape or Blender — it copies, splices, generates
`sitemap.xml`, and asserts byte sizes. That keeps CI fast, dependency-free, and incapable of
silently producing a page different from the one that was reviewed.

---

## 1. What deploys, and from where

### 1.1 The published artifact

`https://istor.fyi/` at the root *(settled, design plan §7)*. The artifact is **120 files**: **30**
that are the new page and its own assets, **89** carried library files, and the generated
`sitemap.xml`. The two groups are kept apart in the table because the split is what §5 decides.

**Group 1 — the new page, 30 files.**

| published path | source | produced by |
|---|---|---|
| `/index.html` | `Source/index.html` | assembler: splices in the icon sprite, the plate **and the stylesheet** |
| `/404.html` | `Source/404.html` | hand-written |
| `/llms.txt` | `Source/llms.txt` | carried from `OldVersion/llms.txt` with the Home entry rewritten (§5) |
| `/CNAME` | `Source/CNAME` | `istor.fyi`, 9 B — **moved** out of `OldVersion/` |
| `/favicon.ico` | generated | `make-favicons.py`, checked in |
| `/icon.svg` | generated | `make-favicons.py`, checked in |
| `/apple-touch-icon.png` | generated | `make-favicons.py`, checked in |
| `/og-card.png` | `Assets/brand/og-card.png` | copied, 123,199 B, locked. **Also ships at `/brand/og-card.png` for the library — deliberate, see below** |
| `/fonts/inter-var.woff2` | `Assets/fonts/` | copied, 48,256 B |
| `/fonts/gfs-didot.woff2` | `Assets/fonts/` | copied, 14,540 B |
| `/fonts/istor-wordmark.woff2` | `Assets/brand/` | copied, 1,892 B |
| `/img/ground-grain.png` | `Assets/textures/` | copied, 451 B |
| `/img/exhibit-07-viewer.{avif,webp,png}` × 1× and `@2x` | `Assets/Exports/` | copied, 6 files |
| `/img/exhibit-08-library-rail.{avif,webp,png}` × 1× and `@2x` | `Assets/Exports/` | copied, 6 files |
| `/img/exhibit-09-settings-research.{avif,webp,png}` × 1× and `@2x` | `Assets/Exports/` | copied, 6 files |

**Note there is no `/styles.css` in this group.** The new page's CSS is authored at
`Source/styles.css` and **inlined into `index.html` at build time** (§3, Stage 1) — so it is not a
published file of its own, and the path at the origin belongs to the library. An earlier draft of
this table listed `/styles.css` twice, once per group, which was the collision stated as if it were
already resolved.

**Group 2 — the carried library, 89 files.**

| published path | source | produced by |
|---|---|---|
| `/<slug>/index.html` × 75 | `OldVersion/<slug>/` | **copied verbatim — zero rewrites** |
| `/styles.css` | `OldVersion/styles.css` | copied, 35,522 B — the library's own, at the path it has always had |
| `/assets/fonts/*` × 3 | `OldVersion/assets/fonts/` | fraunces-600 (18,096 B), gfs-didot (14,540 B), inter-var (48,256 B) |
| `/assets/textures/fabric-texture.jpg`, `/assets/textures/SOURCE.md` | `OldVersion/assets/textures/` | copied, 1,542,136 B and 3,883 B |
| `/brand/*` × 6 | `OldVersion/brand/` | copied: all 75 pages reference `/brand/istor-page.svg` and `/brand/og-card.png` |
| `/robots.txt` | `OldVersion/robots.txt` | **carried unchanged**, 688 B — a stance document, §3 Stage 8 |
| `/08eaa6e8b97d4b94943057b2c49bd712.txt` | `OldVersion/` | carried: the IndexNow key, 32 hex chars |

**And one generated file:** `/sitemap.xml`, written from the artifact's own file list — **76
entries**, the 75 library pages plus the home page (§3, Stage 8).

Appendix B is the same list with every byte size the build asserts.

**The three collisions the library brings, and how each is settled.** Adding 75 live pages to a
new site is not a copy operation; there are exactly three places where the two want the same path.

| collision | who wins | why |
|---|---|---|
| **`/index.html`** | the new page | `OldVersion/index.html` is the *previous* home page and it wants the same path. **This is the one way to break the deploy**, so the assembler copies the library **by directory, never by wildcard from `OldVersion/`'s root**, and Stage 9 asserts `_site/index.html` is the new page by marker string |
| **`/styles.css`** | the **library** | the new page **inlines its CSS** in `<head>` (§3, Stage 1). That is a deliberate choice, not an oversight: it touches none of the 75 live files, it removes the landing page's only render-blocking request, and the design plan's head (§7) specifies no stylesheet link — so nothing is being overridden. The library keeps the path it has always had |
| **`/favicon.ico`** | the **new** one | all 75 pages reference `/favicon.ico`; the generated one is the same brand mark, so the library inherits the new favicon rather than losing it. Same for `/brand/istor-page.svg`, which is untouched |

**Four files deliberately ship at two paths each, and this is the one place the artifact
double-counts.**

- `inter-var.woff2` and `gfs-didot.woff2`: `/fonts/` for the new page, `/assets/fonts/` for the
  library — because the legacy stylesheet addresses them **relatively** (`url("assets/fonts/…")`
  against the stylesheet's own location, not the document's) and rewriting it is a change to a live
  file for no gain.
- `og-card.png`: `/og-card.png` for the new head (§7 specifies that absolute URL) and
  `/brand/og-card.png` for the library's 75 references.
- `istor-wordmark.woff2`: `/fonts/` for the new page and `/brand/istor-wordmark.woff2`, where it
  already lived as a brand asset.

**No visitor ever fetches both copies of anything** — they are on different pages, and the new home
page requests zero library bytes. **Do not "optimise" any of these away: it breaks the library**,
which is the group that does not get to change. The cost is ~114 KB of unreachable duplication in
the artifact, which is cheaper than the alternative by a wide margin.
- `OldVersion/script.js` (18,740 B) is **orphaned**: not one of the 75 pages references it. It is
  not published. Nor are `OldVersion/404.html` (the new one supersedes it), `OldVersion/favicon.ico`
  (the generated one supersedes it), the library's design documents (`DESIGN.md`, `AGENTS.md`,
  `TOOLING.md`, `IMPROVEMENTS.md`, `README.md`, `design-references.md`) or `OldVersion/tools/`.

**Nothing else is published.** `Documentation/`, `References/`, most of `OldVersion/`, and almost
all of `Assets/` do not appear in the artifact — not by exclusion rules, but because the assembler
copies from an explicit allowlist and never by wildcard. That is the reason for the artifact model
in §2: a branch-based Pages deploy publishes the whole repository, and this repository is a working
directory with the previous site, its design notes, and five screen recordings in it.

### 1.2 The working tree

```
IstorPage/
  Source/                        ← everything authored, and every generator
    index.html  styles.css  404.html  robots.txt  llms.txt  CNAME
    figures/calendar-ring.svg    ← exists, 1,318 B
    tools/bench.py               ← exists: resolves the off-PATH binaries
    tools/make-ground.py         ← exists
    tools/make-calendar-ring.py  ← exists
    tools/make-favicons.py       ← to write (§3, Stage 4)
    tools/make-icon-sprite.py    ← to write (§3, Stage 3)
    tools/build-site.py          ← to write (§1.3); calls make-sitemap.py
    tools/make-sitemap.py        ← **exists**, 2026-09-18: generates sitemap.xml
    tools/verify-budget.py       ← to write: the manifest and the payload (§3, Stage 9)
    tools/verify-links.py        ← to write: targets, no-JS, contrast, codepoints
    tools/budget.json            ← **exists**, 2026-09-18: the asserted sizes, measured
    tools/sitemap-dates.json     ← **exists**, 2026-09-18: path → lastmod + changefreq,
                                   ordered. Seeded from OldVersion/sitemap.xml — the only
                                   copy of those 76 dates (see the note below)
  Assets/                        ← binaries: fonts, brand, exports, textures, screenshots
  Documentation/                 ← the design plan, this plan, app-coral-contrast.md
  OldVersion/                    ← the previous site. Its library (75 pages, /styles.css, /assets/,
                                   /brand/) IS published — carried verbatim (§5); the rest is not
  References/                    ← reference only; never assembled
  _site/                         ← the artifact, built; gitignored
```

`Source/` is authored; `Assets/` is a library of measured, already-produced material. Keeping them
apart is why the assembler exists rather than the page simply sitting at the repository root.

**Three of those files were written on 2026-09-18, and one of them is a rescue rather than a build
step.** `sitemap-dates.json` holds the 76 `lastmod` dates and `changefreq` values that existed only
inside `OldVersion/sitemap.xml` — the file generation is about to supersede. **Verify this file
exists before regenerating anything**, because regenerating without it produces a sitemap with no
dates at all, and `make-sitemap.py` will say so rather than guess (`MissingDate`).

`make-sitemap.py` is written as its own module with a `build(pages, dates)` function, and
`build-site.py` imports it — rather than the generation living inline in the assembler. That is
because it is the one generator with a **test**: run it against the existing
`OldVersion/sitemap.xml` and it must reproduce it byte for byte, which is Stage 8's done-condition.
A function that can be called in isolation is what makes that test one line.

**That test passes.** Verified 2026-09-18, before the file was superseded: `make-sitemap.py
OldVersion/sitemap.xml` reports `byte-identical: 11,052 B, 76 urls`, exit 0. Its three guards were
exercised too — a page with no date raises `MissingDate`, a date for a page that no longer exists
raises `ValueError`, and the output order depends only on the dates file, not on the caller's input
order. So the generator is not merely asserted to be faithful; it was shown to be.

`budget.json` was likewise **measured from disk, not transcribed**, and its three totals came out at
exactly the design plan's byte-exact figures: 85,345 B phone, 113,870 B retina, 702,015 B for the
eighteen exports. All 23 copied binaries and all 14 library shared files matched Appendix B on the
first run — which is the check that Appendix B itself is right.

**A naming note, not a change.** `OldVersion/` is now an inaccurate name — part of it ships. But
renaming it means touching paths in the design documents, the memory, and the assembler, and buys
nothing the reader does not already have from §5. It stays `OldVersion/`, and this plan says plainly
what of it is live. If it is renamed later, `SITE_SOURCE_LEGACY` in the assembler is the only code
that changes.

### 1.3 The assembler — one script, used locally and in CI

`Source/tools/build-site.py`, standard library only, no arguments worth remembering:

1. reads `Source/`, writes `_site/`;
2. copies the fonts, the ground tile, the eighteen exhibit files and `og-card.png` from `Assets/`
   into their published paths;
3. **copies the carried library in — by directory, from an explicit allowlist, never by wildcard**
   (see below);
4. splices three things into `index.html` at three `<!--#include-->` markers — the compiled
   `Source/styles.css` into the head, `figures/calendar-ring.svg`, and the five `<symbol>`
   elements — so a regenerated figure or stylesheet cannot be forgotten in a hand-paste;
5. generates `sitemap.xml` from the file list it just wrote — which now means **76 entries, not
   one**, because the file list contains 75 library pages as well as the new home page. **`lastmod`
   comes from the checked-in `tools/sitemap-dates.json`, never from mtimes or from a fresh
   timestamp** (§3, Stage 8), and a page with no entry in that file fails the build;
6. prints a file count and the total.

**The library copy rule, stated as three lines of code-shape because it is the one way to break
the deploy:**

```python
# The library, by directory. NEVER glob OldVersion/* — OldVersion/index.html is the OLD home
# page and it would silently overwrite the NEW one at the same published path.
LIBRARY = sorted(d for d in LEGACY.iterdir() if (d / "index.html").exists() and d.name not in EXCLUDE)
copy(LEGACY / "styles.css", SITE / "styles.css")     # the library's; the new page inlines its CSS
copy_tree(LEGACY / "assets", SITE / "assets")
copy_tree(LEGACY / "brand",  SITE / "brand")
```

`EXCLUDE` is `{"assets", "brand", "tools"}` — the three non-page directories — and the
`(d / "index.html").exists()` test is what makes the rule survive a new directory being added under
`OldVersion/` without a wildcard ever running. **No file inside the 75 pages is rewritten.** Zero
edits, which is what makes this reversible: reverting the library is deleting five lines.

**And CI asserts the guard rather than trusting it.** `verify-links.py` checks that
`_site/index.html` contains the new page's marker string (the `<h1>` text, *It shows you what it
saw*) and fails the build if it finds the previous home page there instead. That check exists
because the failure mode is silent: a wildcard copy publishes a complete, valid, working site
serving the wrong home page, and every other check would pass.

**The same script makes the local preview and CI's artifact**, so what is reviewed locally is
byte-identical to what deploys. Preview with `python -m http.server` inside `_site/` — absolute
paths like `/fonts/inter-var.woff2` then resolve exactly as they will in production, which a
`file://` open would not do.

---

## 2. The publishing pipeline

**Decided: a GitHub Actions workflow that uploads a Pages artifact.** `actions/upload-pages-artifact`
takes a directory; only that directory becomes the site. `References/`, `Documentation/`, almost all
of `OldVersion/` and almost all of `Assets/` are unpublished by construction rather than by a
`.gitignore` someone has to remember to extend. The exception is the carried library, and it is
unpublished-by-default too: the assembler copies 75 named directories, not a folder.

Appendix C is the workflow verbatim. Its shape:

| job | what it does |
|---|---|
| `build` | checkout → `python Source/tools/build-site.py` → **`verify-budget.py _site`** → **`verify-links.py _site`** → `configure-pages@v5` → upload `_site/` |
| `deploy` | `actions/deploy-pages@v4` |

**The budget check is a gate, not a report.** `verify-budget.py` fails the build when any asserted
file's size has moved, so a regenerated crop or a re-subset font cannot quietly make the page
heavier than the design plan says it is. Updating the page's weight becomes a two-file commit —
`budget.json` and the design plan's table — which is the friction the honesty claim is worth.

**Prerequisites, all outside the repository:**

| # | what | note |
|---|---|---|
| 1 | ~~a remote for this directory~~ | **RESOLVED 2026-09-18 — it is a fresh repository.** No `.git` exists, so this cannot be a clone of `ThoriaDevelopment/IstorPage`; Stage 0 does `git init`, adds `origin`, and stops before the first push |
| 2 | `git init` and a first commit | this directory has never been under version control |
| 3 | Pages source set to **GitHub Actions** | Settings → Pages → Source. With the default (a branch) the workflow's artifact is ignored and the deploy silently does nothing |
| 4 | `CNAME` at the root | moved from `OldVersion/CNAME` (9 B). Without it the custom domain is dropped on the first deploy |

**Two things that are *not* needed, and someone will otherwise add them:**

- **No `.nojekyll`.** Jekyll only runs on branch-based Pages builds. The artifact path skips the
  Jekyll pipeline entirely, so the file would be cargo.
- **No `gh-pages` branch.** `deploy-pages` publishes the artifact directly.

---

## 3. Build stages

Ten stages. Each ends in a state that can be looked at, and each says what "done" means.

### Stage 0 — Establish the repository, and clear the decks

**Resolved 2026-09-18: this is a fresh repository, and the first push is its own gated step.**

`git init` in `C:\Projects\Istor\IstorPage`. The directory holds no `.git` at all, and a clone of
`ThoriaDevelopment/IstorPage` would necessarily have one — so **this directory cannot be that
clone**, and §2's prerequisite 1 resolves to *fresh*, not *existing working copy*. Then:

- add `github.com/ThoriaDevelopment/IstorPage` as **`origin`** — recorded as the website repo, and
  the name is the only thing linking the two;
- `.gitignore` with `_site/` and `Source/tools/__pycache__/`; `CNAME` copied into `Source/`;
- commit, and **stop.**

**The push is deliberately not part of Stage 0**, because it is the one irreversible action in this
plan and the local fact does not settle the remote one: *"this directory is not a clone"* says
nothing about whether `origin` already holds history. Run `git ls-remote origin` and read what is
there before the first `git push`; if the remote is populated, this becomes a merge decision rather
than a push.

**And this step is preservation, not housekeeping.** Nothing in this directory has ever been under
version control, which has already cost the project once: `assets/textures/SOURCE.md` records the
5184×3456 camera original of the privacy band as living at git blob
`6c752295e76bfc5cc340240516fc67b0f73dd53f` — **in a repository that does not exist here**, so the
source of record for the site's one photograph is currently unreachable. The screenshots in
`Assets/`, `OldVersion/` and `References/` are in the same position. The first commit is what stops
that list from growing.

**One housekeeping item, stated carefully because an earlier draft of this plan got it wrong.**
`Assets/fonts/fraunces-600.woff2` — the subset sitting where a builder would go looking for the
landing page's fonts — **is already gone**; `Assets/fonts/` holds exactly the two files the design
plan names, and the landing page loads two fonts. That is *not* the same as Fraunces being unused:
a copy lives at `OldVersion/assets/fonts/fraunces-600.woff2` and the legacy `styles.css` declares
`@font-face` for it, so **carrying the library (§5) means carrying the font**. Nothing is deleted
from `OldVersion/`. Checked, not assumed.

**Done when:** `git status` is clean, and `Assets/fonts/` has two files in it.

### Stage 1 — Tokens

`Source/styles.css`, top of file: the nine-value palette of design plan §1 as custom properties,
plus the Black theme's five swaps scoped to `.win`, and the dark world's two.

- Every value is transcribed from the design plan's table. `--azure-deep` `#0073E6` and
  `--coral-ink` `#C7292A` are **derived values with stated reasons** and are not to be re-derived.
- The Black window's separation is a **ground change**: `.win` and `.win-center` carry the two
  grounds and **no column border is drawn**. `#0A0A0A` → `#0B0C0F` is R+1 G+2 B+5, and a `1px`
  `--rule` there would be the replica inventing a line the app does not draw.
- Radius is three tokens, not one: `--r-window: 0`, `--r-card: 4px`, `--r-bubble: 8px`.

**This file is authored as a separate stylesheet and *inlined* into `index.html` by the assembler
(§1.3).** It is not published as a `<link>`. That is the reason `/styles.css` at the origin still
belongs to the carried library (§1.1) — one authoring file, one published path each, and no rename
of a live file. Preview and production are the same either way, because the inline is produced by
the same build that produces the page.

**Done when:** every colour and radius on the page resolves to a token, and no hex literal appears
outside the `:root` blocks.

### Stage 2 — Type

Three `@font-face` blocks for two faces — GFS Didot declared **once as a family with two
`unicode-range`s**, from `fonts/gfs-didot.woff2` (Latin, 219 glyphs) and
`brand/istor-wordmark.woff2` (the 16-codepoint subset). The scale is design plan §2's table.

The wordmark's range is exactly these 16 codepoints — it sets ἵστωρ and the variants the brand
already uses, and nothing else:

```
U+0020  U+002E                                    space, period
U+0301  U+0314                                    combining acute, combining rough breathing
U+03B9  U+03C3  U+03C4  U+03C9  U+03C1            ι σ τ ω ρ — the letters, decomposed
U+1F35                                             ἵ — the same iota, precomposed
U+03AF  U+03CE  U+1F31  U+1F61  U+1F65  U+1FE5    ί ώ ἱ ὡ ὥ ῥ
```

> **Corrected 2026-09-18, during the build.** This list as first written had **fifteen** entries
> and claimed sixteen: it omitted **`U+03B9` (ι)**. It was caught by doing what the paragraph
> below asks — dumping the font's own `cmap` rather than trusting the transcription — and the
> real table has exactly 16 codepoints, of which `U+03B9` is one. The omission was not cosmetic.
> `U+0314` and `U+0301` are in the subset so that a **decomposed** iota-with-rough-breathing-and-
> acute can render at all, and a decomposed sequence needs its base letter: without `U+03B9` that
> spelling falls through *both* Didot faces and lands in Georgia, which is the precise silent
> fallback the paragraph below is about. `U+1F35` is the precomposed form of the same letter, and
> the subset carries both because the brand already uses both. **The `cmap` is the authority, not
> this table** — the table is now a transcription of it and should be re-checked against it.

**Verified once, locally, not in CI:** `pip install fonttools`, then dump both files' `cmap` and
assert the first has 219 Latin glyphs and **0 Greek codepoints**, and the second has exactly 16.
The design plan's claim that these are two files with two jobs rests on it, and a silent fallback
is the failure mode — at `--t-mark` a missing Greek glyph does not error, it renders ἵστωρ in
Georgia. *(Run 2026-09-18: 219 / 0 and 16 / 12 confirmed, and Inter at 230 / 0. The `cmap` dump
is also what found the missing `U+03B9` above, which is the argument for running it rather than
reading it.)*

- `font-display: swap` on all three; preload only Inter and Didot (design plan §7).
- Fallback stacks: `Inter, -apple-system, "Segoe UI", system-ui, sans-serif` and
  `"GFS Didot", Georgia, "Times New Roman", serif`.
- **The h1 is 68px Didot and Didot is not metric-compatible with Georgia**, so a swap reflows the
  largest type on the page. The preload plus a local-cache hit should make it invisible. If Stage 9
  measures a visible shift, the fix is a metric-matched fallback `@font-face` using
  `local("Georgia")` with `size-adjust` and `ascent-override` — not removing `swap`, which would
  trade a shift for invisible text.

**Done when:** the page renders identically with the two fonts blocked, in the right faces, with no
tofu.

### Stage 3 — The icon sprite, from Lucide

**The design plan now agrees with this stage; both were corrected on 2026-09-18.** §7 previously
said the five icons were "redrawn, not extracted", to a 16px grid at 1.5px stroke, because a 2×
capture cannot recover a stroke. That was right when a screenshot was the only source, and it is
**no longer true: the source is on disk**, so §7 was rewritten to say so and this stage is the
mechanic it points at. A future reader who finds the two in conflict should trust §7 — but there
is no longer anything to conflict with.

`C:\Projects\Istor\Source` depends on `lucide-react`, resolved to **1.31.0** in its lockfile under
`node_modules/`. The app's five site-relevant glyphs are Lucide's:

| the page's glyph | Lucide name | app module |
|---|---|---|
| the magnifier, in `Filter sources…` and `Filter notes…` | `Search` | `dist/esm/icons/search.mjs` |
| the page-plus, in `Add source` and `New note` | **`FilePlusCorner`** | `file-plus-corner.mjs` |
| the copy control under every answer | `Copy` | `copy.mjs` |
| the save-as-note control under every answer | `FileText` | `file-text.mjs` |
| the Viewer's pencil | `Pencil` | `pencil.mjs` |

**Two findings the extractor has to know.**

1. **`FilePlus2` is an alias, not a file.** The app imports `FilePlus2`, and in 1.31.0
   `file-plus-2.mjs` is nothing but `export { default } from './file-plus-corner.mjs'`. The
   canonical name is `FilePlusCorner`. Reference the canonical name and note the alias in a
   comment — a future Lucide bump can drop an alias, and the glyph would vanish from a page whose
   only symptom is a missing plus sign.
2. **The geometry is 24px at stroke 2, not 16px at 1.5.** Lucide's node data carries no stroke
   attributes at all — the `__iconNode` is bare `["path", {d: "…"}]` and `["circle", {cx, cy, r}]`
   pairs, with a React-only `key` that the extractor drops. Stroke is set once on the wrapper, so
   a 24-viewBox glyph rendered at the app's own 14 and 16 px draws at an effective **1.17 and
   1.33 px** — which is what the app actually looks like. Set `stroke-width: 2`, render at the
   app's sizes, and let the scale do the arithmetic. Do not chase 1.5.

`Source/tools/make-icon-sprite.py`: parse the five `__iconNode` arrays, drop every `key`, emit five
`<symbol id="i-search" viewBox="0 0 24 24">…</symbol>` into `Source/icons.svg.partial`, which
Stage 1.3's assembler splices into `index.html`. Wrapper:

```html
<svg class="i" aria-hidden="true" focusable="false"><use href="#i-search"/></svg>
```
```css
.i { fill: none; stroke: currentColor; stroke-width: 2;
     stroke-linecap: round; stroke-linejoin: round; }
```

**Provenance, on the page.** Lucide is ISC-licensed. The footer's small print carries one line —
*Icons from Lucide, ISC* — because a page that cites its own sources should cite these.

**And the design plan's rule still binds:** nothing on this page is an interactive icon, because
nothing on this page is interactive. Every glyph is either part of the window replica or a mark
beside its own word.

**Done when:** the sprite is one inline block, five symbols, zero requests, no `<img>`, and every
glyph renders in `currentColor` in both themes.

### Stage 4 — The head, the favicons, and the card

`Source/index.html`'s head is design plan §7's block, **verbatim** — title, description, canonical,
three favicon links, the OG block with `og:image:width`/`height`, and two font preloads. The
canonical origin is a build input: `og:image` must be absolute or the card silently never appears.

**`Source/styles.css` is inlined into this head at build time, and there is deliberately no
`<link rel="stylesheet">`** (§3, Stage 1). The design plan's head block specifies no stylesheet link,
and adding one would either collide with the library's `/styles.css` or force a rename of a file
75 live pages depend on. The assembler writes the compiled CSS into a `<style>` element at the
`<!--#include styles-->` marker; nothing about the head otherwise changes.

There is no producer script for the favicons today. `Source/tools/make-favicons.py`:

| output | from | note |
|---|---|---|
| `favicon.ico`, 16/32/48 | `Assets/brand/istor-eye.svg` | the master built for slots ≤32px |
| `icon.svg` | `Assets/brand/istor-page.svg` | **plus its own embedded `@media (prefers-color-scheme: dark)` block** |
| `apple-touch-icon.png`, 180×180 | `Assets/brand/istor-page.svg` | **opaque**, on `--paper`; iOS composites transparency onto black |

**The dark block inside `icon.svg` is the whole point of that file.** The mark's `var()` contract
works for inline SVG only — it cannot cross the `<img>` boundary, and a favicon sits on the far side
of it. So the standalone file replaces every `var()` with a literal and swaps the literals under a
media query *inside its own `<style>`*. Without it the tab icon is `#171717` ink on a dark tab
strip.

Uses Inkscape, resolved by the existing `bench.py` because it is not on `PATH`. Runs **locally**;
the three outputs are committed (Stage 0's rule). No `mask-icon`.

**Done when:** the tab shows the eye in both a light and a dark browser theme, and the page loads
with no font or favicon 404 in the network panel.

### Stage 5 — The hero replica

The page's one bold moment, and the one place the replica has to be exact. All of design plan §3,
§4 and §5 movement 1, in DOM.

**The measured numbers, as assertions rather than intentions:**

| | value | source |
|---|---|---|
| columns | **180 / 594 / 185** CSS px | measured, identical in both themes |
| question bubble | right-aligned, ~17px right inset, ~75% of column, 8px radius, `--fill` | CSS 311→757 inside 180→774 |
| witness popover | 4px radius, floats over the answer, anchored to its citation | all four captures are mid-fade, so the captures are the spec and a crop is impossible |
| window | 0 radius, one soft shadow (see §4) | square-cornered in the app |
| Black theme | rails `#0A0A0A`, centre `#0B0C0F`, fill `#10141B`, text `#E5E8EE`, accent `#4DA3FF` | measured |
| column separation | **no border** — the ground change is the separation | measured |
| rail headers | `Library` left with controls right; `Notes` right with controls left | the panels mirror; a site that left-aligns both is tidier and wrong |
| answer typography | bold run-in headings, `Inter 600` at `--t-base`, continuing on the same line | the app's device for a multi-part answer |
| citation marks | `<sup>`, Inter 13, `--azure` on a `#E3EEF9` wash; **not buttons** | keyboard users must not land on a dead control |
| the anchored citation | filled `--azure` disc, white numeral — a **static** state | ties the card to its claim |

**The left rail is the one place the replica is not a replica, and the design plan says so.** It
borrows the Library rail's grammar — header, rows, one action at the foot — but its rows are the
page's **six** rail entries and its foot is `[Read the source]`. Six, not eight: movements 2, 3 and
4 all carry the label *How it answers*, so a row stays inked while its movements run. The current
row is marked **by ink alone** — no numbers, no dots, no glyph in the leading slot.

**The right rail is the product, unaltered** — `Filter notes…`, ten real titles, `New note`. Two
notes on the ten titles:

- **Full titles go in the DOM; CSS ellipsis does the truncating.** The captures show
  `The National Archaeol…` because the rail is 185px wide, not because the title is short. Typing
  the full string and letting the same overflow rule the app uses truncate it keeps the rail real,
  keeps the text selectable, and puts the whole title in a screen reader's ear. §7 cleanup 2's
  reason for the alt-text exception on exhibit 8 applies here as a matter of course.
- Appendix A lists all ten and marks the two that cannot be recovered from the design document's
  own notes and must be read off `Black/verifiedsource.png`.

**Done when:** measured in the browser, the three columns are 180/594/185 at a 959px window,
the bubble's right inset is 17px, and a screenshot at 959px sits over the Black capture's client
area without a visible shift.

### Stage 6 — Movements 2 to 8

All of it is one reading column, measure capped at 66ch, left-aligned and ragged right. Nothing
centred, nothing in a card. In order, each from design plan §5:

| movement | what ships | the trap |
|---|---|---|
| 2 · the gate | plain prose, then the `band=` block as two quoted columns | keep the log's own vocabulary — `band`, `top_k`, `chunks` — because a tidied quotation is not evidence. Caption carries both honesties: the lines are real, the side-by-side arrangement is mine; and **no provider is named**, in the block or in copy |
| 3 · the witness | one paragraph of real output set large, then **both card states** rebuilt in DOM — verified first, unverified second | the coral line is `--coral-ink` against a rule, **never colour alone**. And it must not be paraphrased as "the source doesn't back the claim" — it says which of two models wrote the citation |
| 4 · watch it decide | the `Thoughts` disclosure printed **already expanded**, no chevron; the amber disclosure dot kept; the fetch log transcribed | it is one of the two places the page looks technical, so it is `--t-xs` in a `--fill` block narrower than the measure. **Name nothing about the shell** |
| 5 · where it stops | the two bullets, then **What Is Still Disputed as a real `<table>`** (5 rows of 12), then the plate | the table is from a different run than the hero's — one clause says so, or the question is not shown at all |
| 6 · on your machine | the settings crop, the note as live prose (136 words), the Library-rail crop, the two icon controls, the requirement paragraph | the crop must **not** call Scrape the default (it is SearXNG); the authorised claim is *no account and no key are required*, never *no key is ever used*, which Brave falsifies |
| 7 · ἵστωρ | 3–4 sentences at display size | set as writing, not a trivia card. No "our name means…" framing |
| 8 · questions | the FAQ as a **plain list**, seven questions, answers in "we" | an accordion would hide precisely the answers this audience came for |

**The pipeline is the one place numbered markers are honest** — `1 decide → 2 retrieve → 3 answer
→ 4 cite`. Nowhere else.

**Done when:** the whole page reads top to bottom with the rails gone quiet after movement 1, and no
section has introduced a card, a rounded corner above 8px, or a second shadow.

### Stage 7 — The close, and the lighter build

**The close.** Ground switches to the og-card's teal — a radial from `#132E2F` at the top-right to
`#0D1D20` at the edges. Hairlines become `rgb(255 255 255 / 0.12)`, an alpha, so the rule works
over the gradient. The mark re-inks to its dark contract (`--azure-lift` `#4DA3FF` iris,
`--azure-deep` `#0073E6` pupil). The CTA slot is at full size. The giant **ἵστωρ.** closes the page
as live text from the wordmark subset. Then a footer strip: links only, spaced, **no `·`
separators**, plus the Lucide line.

**The CTA slot**, from design plan §6. Prelaunch is the shipping state: no dead button, a plain
sentence, and one real action available today — the repo, under the label **`[Read the source]`**,
the same name the hero's rail foot uses. No email capture. When it goes live the same rectangle
becomes `[ Download for Windows ]` on `--azure-lift` with **`--ink` text** (6.8:1; white on
`--azure-lift` is 2.6:1 and fails).

**The lighter build** — same words, same order, same argument, declared not detected. No script, no
UA sniffing: `@media (max-width: 1080px)`, `@media (pointer: coarse)`, and `<picture>` sources.
The moment the page needs to know what device it is on, it needs JavaScript, and principle 2 says
no. What drops, each as one declaration:

- the ground texture → flat `--paper` (the largest runtime saving; a blend-mode texture is the one
  thing here a weak GPU genuinely pays for)
- the 2× sources → `<picture>` resolves to 1×
- the close's blend and blur layers → flat teal
- the hero shadow (it goes with the other blend layers)
- large display settings → type re-measured so nothing ships glyph sizes the phone will not render

**The plate stays**, and it is worth the sentence: it is static inline SVG in `--rule`, no filter,
no blend, ~694 B gzipped, no request. Dropping it would cost the honesty section its evidence on
exactly the devices that read it last. Its one adaptation is geometric — the interior stays wider
than the measure and bleeds past the 24px gutters, clipped by the section.

**Done when:** at 375×812 with coarse-pointer emulation, the network panel shows the document, one
1× AVIF and the font files — **and no separate CSS request**, because the landing page's stylesheet
rides inside the document (§3, Stage 1) — and the page still reads whole.

### Stage 8 — Aux files

Four aux files, and the library changes what each one is. It does not change *whether* they ship:
the library makes `sitemap.xml`, `llms.txt` and `robots.txt` more load-bearing than they were, not
less.

**`sitemap.xml` is generated, never hand-written.** The assembler writes it from the file list it
just produced, so it can never list a URL that is not in the artifact. **It now holds 76 entries,
not 1** — 75 library pages plus the home page.

**But "generated" is not the same as "derivable", and this is the part that is easy to get wrong.**
The existing `sitemap.xml` is not a bare list of URLs. Every one of its 76 entries carries a
`<lastmod>` — real, per-page dates like `2026-09-03`, `2026-09-02`, `2026-09-17` — and they are
**not alphabetical or in any derivable order**, and there is **no git history in this repository to
regenerate them from** (§2 prerequisite 2: this directory has never been under version control, so
after its first commit every file's date is the same day). A generator that invented `lastmod` from
file mtimes would tell crawlers that all 76 pages changed on every deploy, which is both false and
actively harmful.

**So the dates are carried as data, like `llms.txt`'s summaries.** `Source/tools/sitemap-dates.json`
is checked in, seeded from the existing `sitemap.xml`: an **ordered** list of path → date, home
page first, then the library in the order the file already uses. That file is the only place those
dates exist, and it is what makes the generator honest rather than merely tidy.

The rule that follows, and it is a real verification step: **every page in the artifact must appear
in `sitemap-dates.json`**, and a page with no entry **fails the build** rather than silently
shipping without a `lastmod`. A newly written page — a future library index, say — is added to that
file deliberately, with the date its author chooses.

**And the current hand-kept file is correct, which gives the generator a real test.** An earlier
draft of this plan asserted the sitemap's 76 `<loc>` entries had drifted from the directories.
**They have not.** There are 75 page directories (`ls -d */` returns 78 including `assets/`, `brand/`
and `tools/`), and 75 + home = the 76 the file lists. With `sitemap-dates.json` seeded from that
file and the order preserved, **regenerating it must reproduce today's 11,052 B file byte for
byte.** If it does not, the generator or the dates file is wrong — not the sitemap.

**`llms.txt` is carried, with one entry rewritten.** Its 75 per-page summaries are hand-written and
stay verbatim; the **Home** entry describes the previous home page and is rewritten for the new one.
The verification step is now two-sided and stricter than it was: every URL in `llms.txt` must exist
in the artifact, **and every one of the 76 pages in the artifact must appear in `llms.txt`** — which
is a real check for the first time, since there is now more than one page to be missing.

**`404.html`** — short, in the page's voice, one link home. Not the old site's, which is why the
library's copy is not carried: it would be shadowed at the same path anyway.

**`robots.txt` is carried unchanged** from `OldVersion/`. It is already a stance rather than a
default: everything allowed, the AI crawlers listed by name to make that a documented decision, and
a pointer to `llms.txt`. Nothing about the redesign or the carried library changes it. **The
IndexNow key file is carried unchanged too** — with the honest note that a key at the origin is
necessary and not sufficient; nothing here submits, and adding a submission step is a separate
decision (§5).

**Done when:** every URL in `sitemap.xml` and `llms.txt` resolves in `_site/`, the reverse holds
(76 pages, and each appears in both), and a regenerated `sitemap.xml` is **byte-identical to the
library's 11,052 B file** — which is the test that `sitemap-dates.json` was seeded correctly.

### Stage 9 — Verification, then first deploy

Ten checks. `verify-budget.py` runs 1–3, `verify-links.py` runs 4–9, and the accessibility pass
is the one thing that needs a browser.

| # | check | fails when |
|---|---|---|
| 1 | **Byte manifest** — every file in Appendix B is present at its exact size | a regenerated crop or font changed the page's weight without the design plan's table being updated |
| 2 | **The payload total** — bitmaps + tile + fonts, 1× and 2× | the phone figure is not 85,345 B or the retina figure is not 113,870 B |
| 3 | **The document** — gzipped `index.html` + inlined CSS | see the note below |
| 4 | **Every internal `href`/`src` resolves** inside `_site/` | a moved file half-breaks (the reason for root-relative paths). This now spans 120 files, so it is also the check that a library page's relative font URL still lands |
| 5 | **No behaviour — on the landing page only** | `_site/index.html` contains an `onclick`, a `javascript:` URL, a `transition`/`animation` outside focus **and outside the close's re-ink**, **more than one** `<script>`, or a `<script src>` of any kind. **Scoped deliberately: do not run this over the library.** All 75 legacy pages carry an inline `<script>`, and the carried library is published as it is — the claim this plan makes is about the new page, and asserting it site-wide would fail on correct content. **Exactly one inline script is permitted and expected** — see the note below |
| 6 | **Contrast** — recompute the nine tokens against their grounds | any of 17.9 / 6.4 / 5.57 / 6.6 / 5.56 / 5.32 has moved |
| 7 | **Codepoints** — every non-ASCII character in `index.html` falls inside a declared `unicode-range` | ἵστωρ would silently render in Georgia |
| 8 | **The home page is the new one** | `_site/index.html` does not contain the new `<h1>` marker, *It shows you what it saw*. **This is the guard for the one silent failure in the whole plan** (§1.3): a wildcard copy of `OldVersion/` publishes a complete, valid, working site serving the *previous* home page, and every other check here would pass |
| 9 | **Library integrity** — 75 `/<slug>/index.html` files are present; `/styles.css` is the legacy file at 35,522 B; every library page's `rel="canonical"` is still its own URL; `/brand/istor-page.svg` and `/brand/og-card.png` both exist | a library page is missing from the artifact, the new page's CSS took the `/styles.css` path, or a page lost its canonical. The canonical check is worth its line: all 75 already carry a correct self-canonical, and the only way they lose it is if something rewrites them — which nothing should. **Also: every page in the artifact has a `lastmod` in `sitemap.xml`**, which is the check that stops a page from quietly shipping dateless (§3, Stage 8) |
| 10 | **Accessibility** — an axe pass over the built page | a missing `alt`, a heading-order break, or a missing `lang`. Run over `_site/index.html`; extending it to the 75 legacy pages is a separate, larger job and not a launch gate |

**Note on check 5, and it is a correction this plan owes the design plan.** As first written,
check 5 failed `_site/index.html` for *any* `<script>` and for any transition outside focus. The
design plan §8 specifies the opposite: the page's one moment of motion is *"a ~15-line
`IntersectionObserver`"* that swaps `data-world="dark"` as the closing movement crosses into the
dark world, with `prefers-reduced-motion` making it instant. A transition with nothing to trigger
it is not a motion, and an `IntersectionObserver` cannot be written without a script, so the two
documents could not both be honoured as written. **Neither document flagged this.** Thoria settled
it on 2026-09-18: **the re-ink ships.** Check 5 is the one amended, rather than the design plan,
because the design plan is the specification and this check was the cruder statement. The
amendment is narrow, and every clause below is asserted by `verify-links.py`:

- **Exactly one `<script>`**, inline, with no `src` — so it adds no request and §7's payload
  arithmetic is unchanged.
- **It is not behavioural.** It does not respond to a click, a key or a pointer; it reads scroll
  position. §8 principle 2's *"Nothing on the page responds to a click"* survives intact, along
  with *"no accordion, no tab, no disclosure"*.
- **It is not device detection.** §8 principle 2 draws its line at *"the moment the page needs to
  know what device it is on"*: the lighter build stays declared — media queries and `<picture>`
  sources, no user-agent sniffing — and this script never asks.
- **The only `transition` outside focus is the closing mark's re-ink**, on its own colour and
  nothing else, and `prefers-reduced-motion: reduce` collapses it.
- **If the script never runs, the page is still correct.** The closing mark is authored in its
  dark contract, so the script's only job is to set the pre-crossing colour and animate out of it.
  Its absence is a missing animation, never a stalled or broken state.

**Note on check 3, and it is a gap in the design plan rather than in the build.** The design plan's
payload table counts the bitmaps, the tile and the fonts — **it does not count the document
itself**. `index.html` and `styles.css` are real weight, and they are the weight that arrives
first. The table stays as the design plan has it; this plan asserts the document separately and
reports both, so "85.4 KB" is never quoted as the whole cost of the page.

**Also worth knowing about that table:** its phone column is the sum of its own rounded rows
(20.2 + 0.5 + 48.3 + 14.5 + 1.9 = 85.4), while the byte-exact total is **85,345 B = 85.3 KB**. The
retina column agrees exactly either way (113,870 B = 113.9 KB). The rounding is presentation and
stays; the assertion is on bytes, and `budget.json` holds bytes.

Then: push, watch the first deploy, and confirm on the live origin that `istor.fyi` serves the new
page, that the CNAME held, and that a share of the URL renders the OG card.

**And confirm the library survived, on the live origin rather than in the artifact** — three URLs,
not 75 of them: the home page, one library page (any `vs-*`, whose relative font URL is the thing
most likely to break), and `sitemap.xml`. Then one more: fetch a library page and check the browser
does not report a 404 for a font, because a missing `fraunces-600.woff2` is **the** failure mode of
this deploy — it is referenced relatively by design, it is the one carried asset the new page does
not use, and it is therefore the one nobody notices is missing until the type falls back.

---

## 4. Two decisions and one tuning pass the built page makes

The design plan names three things that can only be settled against a real page. Two are genuine
decisions; the third is tuning.

**1. Is Inter's variable axis worth 48.3 KB when the page uses three weights of it?** Measure, do
not guess. Grep `styles.css` for the actual `font-weight` values in use; if only 400 and 600 render,
the third axis is dead weight. Then `fonttools varLib.instancer` to cut static 400 / 600 subsets
and compare. **Ship whichever is smaller, and only if a screenshot diff at both sizes is
pixel-identical.** The cost of statics is not bytes — it is a second request and a second preload
entry, so the comparison is *48.3 KB in one file* against *two files plus a preload line*.

**2. The grain's alpha.** The design plan's instruction is exact: **raise alpha, not density**, if
the built page reads flat. The two knobs are in `make-ground.py` (7.5% and 4.5% alpha, two layers).
Try 10% and 6%, look at both at 100% on a real screen, and keep the tile under about 600 B. A
texture you can find and cannot name is the target; a texture you can see is a pattern.

**3. The hero's one shadow — tuning, not a decision.** It is taken, not conditional *(Thoria
pre-approved, 2026-09-18)*: exactly one soft shadow, under the app window in movement 1 only,
because the window is the page's one object and everything else is a document. What is left is
three numbers. Start near `0 24px 48px -12px rgb(10 10 10 / 0.18)` and judge by one criterion:
**it must read as a window sitting above paper, not as a card floating above a page.** If it starts
reading as elevation, reduce the blur and the alpha together. The lighter build drops it.

---

## 5. The content library — carried, not retired

**Decided 2026-09-18, by Thoria: the library ships with the new home page.** *"All of these can be
used. The 76 URL sitemap is great for SEO, llms.txt is great for SEO, and IndexNow is also great
for SEO. These are all already configured things, so all we would have to do is just to add them
over."*

This section records what that means mechanically, because "just add them over" runs into three
path collisions and one file that wants the same name as the new home page. Each is resolved in
§1.1 and §1.3; this is the reasoning.

**First, a correction to an earlier draft of this section, because the wrong number was published
in it.** I wrote that `OldVersion/` holds **78 page directories** and that the sitemap's **76 URLs
had already drifted**. Both were wrong. `ls -d */` returns 78 entries, but three of them are
`assets/`, `brand/` and `tools/` — not pages. There are **75 page directories**, each with one
`index.html`, and **75 + the home page = 76 `<loc>`, which is exactly what `sitemap.xml` contains.
The sitemap is complete and correct. It has not drifted.** The lesson is worth keeping: the count
came from a directory listing that included non-page folders, and I asserted the drift rather than
diffing the two lists. It is diffed now.

**What the library is.** 75 pages: **7 head-to-head comparisons** (`vs-chatgpt`, `vs-notebooklm`, …),
**41 glossary entries** (`what-is-rag`, `what-is-a-gguf`, …) and **27 others** — five `why-*`, five
`can-*`, five `how-*`, six `local-ai-*`, a changelog and a few singles. Every one carries
`rel="canonical"` already pointing at itself, and every one already links densely to its siblings.
`llms.txt` (16,369 B) is a hand-written summary per page. `robots.txt` (688 B) is a written stance on
which AI crawlers are welcome. The IndexNow key file sits at the root. **This is a built
search-acquisition surface, and the new landing page is the only thing in the repository that links
to none of it.**

**The design plan does not mention the library** — it specifies the landing page, and it was written
before anyone read `OldVersion/`. It does not need to change for this: the library keeps its own
typography, its own CSS and its own pages, and nothing in the design plan governs them. What the
design plan governs is the one new file at `/`.

**Three collisions, all settled — the table is in §1.1.** In short: `/index.html` goes to the **new**
page (and the assembler copies the library by directory, never by wildcard, because
`OldVersion/index.html` is the *previous* home page and a wildcard would publish it over the new one
— the one silent way to break this deploy); `/styles.css` goes to the **library**, because the new
page inlines its CSS; `/favicon.ico` goes to the **new** one, and the library inherits it.

**Six files from `OldVersion/` do not ship**, and each for a reason: `index.html` (superseded),
`404.html` (superseded by the new one), `favicon.ico` (superseded, generated), `script.js`
(**orphaned — verified: not one of the 75 pages references it**, 18,740 B of dead code), the
library's own design documents (`DESIGN.md`, `AGENTS.md`, `TOOLING.md`, `IMPROVEMENTS.md`,
`README.md`, `design-references.md` — they are working documents, not site content), and
`OldVersion/tools/` (bench.py, mark-export.py, README.md — they stay in the repository, per the
convention that a generated asset ships the script that made it, but they are not served).

**Fraunces is carried, and an earlier claim of mine that it was already gone was misleading.**
`Assets/fonts/` does hold only two files — `gfs-didot.woff2` (14,540 B) and `inter-var.woff2`
(48,256 B) — so "drop Fraunces" *was* done for the new page, and the design plan is right that the
landing page loads two fonts. But **the legacy `styles.css` declares `@font-face` for Fraunces** and
points at `assets/fonts/fraunces-600.woff2`, which lives in `OldVersion/assets/fonts/`. Carrying the
library means carrying the font it needs. So: **dropped from the landing page, kept for the
library** — and that is what ships.

**What the new home page owes the library was one decision, and Thoria took it on 2026-09-18.** The
library links to itself 75 ways and the new page linked to none of it, which meant the strongest page
on the site passed nothing to the pages that earn the search traffic. **The one-line fix is taken:**
the footer in Appendix A now carries a fourth entry, `Guides` → `/local-ai-vs-cloud-ai/` — a page
that exists, whose `h1` is the question the home page argues. The full fix is still a library index
page, which is a new page and outside this plan's scope; when one exists the entry's `href` changes
and its label does not. Nothing in Stages 0–9 is blocked either way.

**The three SEO assets, and exactly what happens to each:**

| asset | what happens | edit required |
|---|---|---|
| `sitemap.xml` | **generated from the artifact's file list** — now 76 entries rather than one. Regenerating it reproduces today's file exactly, which is the check that the generator is right | none — the hand-kept file is superseded |
| `llms.txt` | **carried, with one entry rewritten.** Every one of its 75 per-page summaries stays verbatim; only the **Home** entry, which describes the previous home page, is rewritten for the new one | one entry |
| `robots.txt` | **carried verbatim** (688 B). It is a stance document, and the new page changes nothing it asserts | none |
| IndexNow key | **carried verbatim** at the root. Note that IndexNow only notifies on a submission — the key existing at the origin is necessary and not sufficient; nothing in this plan submits, and adding a submission step is a separate decision | none |

**This is reversible, and that mattered.** The library is five lines in the assembler (§1.3) and
75 untouched directories. Reverting it is deleting those five lines. And because no file inside the
75 pages is rewritten — the CSS is inlined into the new page rather than the library's stylesheet
being renamed — a revert does not leave the library half-migrated.

**Not blocking the build.** Stages 0–9 build and verify the landing page and the library together;
nothing above is waiting on an answer, and §6 is now empty. The footer link is taken; the IndexNow
submission step remains out of scope and is a separate decision.

---

## 6. What this plan was waiting on

Small, and all of it was a string or a value rather than a decision.

**Nothing.** Every item that was open when this plan was written closed on 2026-09-18, and **all of
them were recovered from the captures rather than assumed** — the strings were on disk the whole
time, in captures that render them full-width. Two of the four turned up a *third* fact that the
design plan gets wrong, and both are listed below.

| what | resolution | where it went |
|---|---|---|
| the two truncated note titles | **found.** `Black/Sourcesfullscreenmain.png` is the one capture that renders the source list full-width with no ellipsis, and it reads the strings out in full: **`ancient astronomical computer`** and **`X-ray data from the Antikythera mechanism's broken calendar ring`**. A *third* title was wrong in this plan's own draft — item 7 is **`Reconstruction of the missing front dial gearing of the Antikythera mechanism.`**, trailing period included, not the short form | Appendix A, hero's Notes rail |
| the answer's Callippic and Saros paragraphs | **found, plus one more.** `Black/verifiedsource.png` holds the whole answer verbatim. It carries **four** bold run-in headings — Metonic, Callippic, Saros **and Exeligmos**. The design plan's §5 listed three, so **§5 was corrected at source** (dated note, same day) rather than left for this plan to out-argue | Appendix A, hero's answer; design plan §5 |
| the footer's Contact target | **resolved:** `https://thoria.fyi/`. No address exists anywhere on disk and none is invented. `Contact` and `Thoria` necessarily resolve to the same origin; the one-token fix (drop `Contact`) is recorded as a design-plan amendment, not taken | Appendix A, footer |
| whether the remote in §2 prerequisite 1 is this directory | **resolved: fresh repository.** No `.git` exists, so it cannot be a clone. Stage 0 does `git init`, adds `origin`, and **gates the first push** — the local fact says nothing about the remote | §2, Stage 0 |
| ~~a footer link into the library~~ | **TAKEN** — `Guides` → `/local-ai-vs-cloud-ai/`, the fourth footer entry | §5, §6, Appendix A footer |

**Two amendments the design plan now owes**, both found by reading captures rather than by reading
the document: §5's *three* run-in headings should be **four** (add *The Exeligmos cycle*), and §6's
footer carries `Contact` and `Thoria` as separate entries pointing at one destination. Neither
blocks the build — Appendix A is the copy of record and is correct as written — but the design plan
is the specification, so the two should not be left disagreeing with it.

Gate D1 is **closed** — the library is carried (§5). `OldVersion/script.js` is confirmed orphaned,
`fraunces-600.woff2` is confirmed required, and the sitemap is confirmed to have 76 correct
entries; the three were verified against disk rather than inferred.

Gate D1 is **closed** — the library is carried (§5). `OldVersion/script.js` is confirmed orphaned,
`fraunces-600.woff2` is confirmed required, and the sitemap is confirmed to have 76 correct
entries; the three were verified against disk rather than inferred.

---

## Appendix A — The copy deck

Every string the page renders, in reading order. Strings marked **[verbatim]** are quoted product
output or measured app chrome and must not be edited — a tidied quotation is not evidence.
Strings marked **[transcribed from …]** were read off the named capture and are **final**; the
citation is provenance, not a to-do, so if one of them ever disagrees with a later build of the
product the fix is to re-read that file and re-transcribe the string, never to tidy the quotation
in place. Everything else is final copy, written to the design plan's §5 and §8 principle 6, and
free to be argued with now rather than in HTML.

### Head

```
title        Istor — it shows you what it saw
description  A local, private research notebook that runs entirely on your machine. Every
             answer carries the sources it read, and the ones it could not check.
og:title     Istor — it shows you what it saw
og:desc      A local, private research notebook. Every answer carries the sources it read.
```
`og:image` is `https://istor.fyi/og-card.png` at 1200×630 — absolute, which is the whole reason the
origin is a build input.

### Left rail — six entries, one foot action

```
What it is          How it answers      Where it stops
On your machine     ἵστωρ               Questions
foot: Read the source  →  https://github.com/ThoriaDevelopment/Istor
```

### Movement 1 — What it is *(rail: What it is)*

> **# It shows you what it saw.**
>
> A hundred pages to get through and one question. Istor reads the documents you give it, answers
> from them, and shows you the passage behind every claim — and it says so when it cannot.

**The window.** Nothing in it is a screenshot; all of it is DOM (design plan §3).

Question bubble **[verbatim]**: `Tell me about the cycles.`

Left rail **[verbatim]**: `Library` · `Filter sources…` · source rows · `Add source`
Centre **[verbatim]**: `Thoughts` · the answer · two icon controls
Right rail **[verbatim]**: `Notes` · `Filter notes…` · the ten titles · `New note`

The answer **[transcribed verbatim from `Black/verifiedsource.png`]**. It is five paragraphs with
**four** bold run-in headings — Metonic, Callippic, Saros and **Exeligmos**; the design plan's §5
had listed three and was corrected the same day — and every paragraph is real prose from the
captured run:

> The Antikythera mechanism incorporated several key astronomical cycles:
>
> **The Metonic cycle** is an astronomical period of 19 tropical years, almost exactly equal to 235
> synodic lunar months or 6,940 days. Named after Athenian astronomer Meton, who introduced it in 432
> BC, the cycle relies on the coincidence that 19 solar years and 235 lunar months differ by only
> about two hours. Ancient civilisations used this relationship to align lunar calendars with the
> solar year by adding seven intercalary leap months over every 19-year period. It forms the
> structural foundation for the Hebrew calendar, traditional Babylonian timekeeping, and the
> Christian calculation of Easter dates. On the Antikythera mechanism, the Metonic cycle appears as a
> five-turn spiral dial on the upper rear plate, complete with individual month names from local
> Greek calendars and a sub-dial tracking Panhellenic athletic games like the Olympics [1].
>
> **The Callippic cycle** is a 76-year sub-dial on the upper rear dial of the Antikythera mechanism [4].
>
> **The Saros cycle** is a 223-month cycle used for eclipse prediction. The lower rear dial of the
> Antikythera mechanism tracks this 223-month Saros eclipse prediction cycle with a 54-year
> Exeligmos sub-dial [4]. Inscriptions on the Saros dial specify lunar and solar eclipse predictions
> down to the hour, along with eclipse characteristics and direction [4].
>
> **The Exeligmos cycle** is a 54-year sub-dial on the lower rear dial of the Antikythera mechanism [4].
>
> The mechanism's gearing incorporated a pin-and-slot mechanism that matches Hipparchus's lunar
> theory, replicating the Moon's variable velocity [4].

`civilisations` is British and stays as captured. `[1]` and `[4]` are the citation marks, and they
are the anchors the hero's popover and the movement-3 card both hang from — **[4] four times, [1]
once**, which is why the hero's card is the `[4]` one.

The bold run-in headings are `Inter 600` at `--t-base` continuing on the same line — the app's own
device for a multi-part answer, and the reason the replica keeps them (§4).

The ten note titles, in order — **all ten confirmed verbatim**, read off
`Black/Sourcesfullscreenmain.png`, which renders the same list full-width with no ellipsis and is the
only capture that does. **Full strings in the DOM; the ellipsis is CSS, not the text.**

```
1  ancient astronomical computer                                              ← the only lowercase, user-written title
2  The National Archaeological Museum in Athens
3  The Saros cycle
4  The Metonic cycle
5  X-ray data from the Antikythera mechanism's broken calendar ring            ← the apostrophe is the file's
6  Fragment C of the Antikythera mechanism
7  Reconstruction of the missing front dial gearing of the Antikythera mechanism.   ← trailing period, in the app
8  Antikythera mechanism
9  Antikythera wreck
10 Decoding Antikythera mechanism
```

**The rail is the exact reverse of the library.** The left rail orders these same ten
`Decoding… → ancient…`; the Notes rail orders them `ancient… → Decoding…` — newest note first. So the
two rails are one list read in opposite directions, and the rail can be generated from the library
order rather than typed twice.

Titles 1, 5 and 7 are the three that truncate identically in every rail capture
(`ancient astronomical c…`, `X-ray data from the An…`, `Reconstruction of the …`); 7 is also the
longest string in the set and the one that ends in a full stop.

*The Metonic cycle* is fourth — on screen without scrolling, and the same cycle the answer opens
with. That is the notebook proved in the first screen rather than claimed in the sixth.

**The witness card, verified state** — source title in ink, then the passage behind a left rule,
italic, in quotes; **no verdict word**:

```
Decoding Antikythera mechanism
  | "Hipparchus's lunar theory, replicating the Moon"
```

**The capture renders that excerpt starting mid-word.** `Black/verifiedsource1.png` — the popover
drawn open on the `[4]` anchor — shows the passage as `"s lunar theory, replicating the Moon"`: the
app clips the match context to a fixed width and the clip lands inside *Hipparchus's*. **The card
starts at the word instead**, because the app's own answer paragraph is the source of the words
(`…matches Hipparchus's lunar theory, replicating the Moon's variable velocity [4]`) and a card
beginning `"s lunar theory` reads as a typo rather than as a clip. Same words, same sentence, cut at
a word boundary — and the trailing `Moon` stops where the app's own excerpt stops.

Its citation mark is the filled `--azure` disc with a white numeral — a static state.

### Movement 2 — How it answers *(rail: How it answers)*

> **## It checks what you already gave it, before it looks anywhere else.**
>
> Before it answers, Istor decides whether the documents in your library already settle the
> question. If they do, it answers from them and never goes online — which is why the tool works
> with the network unplugged, and why it still works when the connection is there but you would
> rather it stayed quiet.
>
> The model making that decision is the small one. Istor runs two: the smaller, heavily instructed
> model is asked the cheap question first — *is this already answered here?* — so the better model
> can be slow, and can be right. It never goes online because nothing needed to, not because
> something refused to.

The two columns **[verbatim]** — the left from a real run's log, the right from the app's own
`Thoughts` panel:

```
band=Direct                                band=Research
Local library already answers this         Explicit research intent detected
question → skip gate + web research        → bypass gate → 3 queries
top=0.0364 → widening top_k 4 → 8          Read en.wikipedia.org — Antikythera Mechanism
Retrieved 6 chunks from library            Read en.wikipedia.org — Antikythera Wreck
                                           Read nature.com
                                           Read arxiv.org — 2403
```

Caption — **both honesties, in one clause each**:

> The lines are real. The side-by-side arrangement is ours: we laid two runs next to each other to
> compare them.

The pipeline, the page's only honest use of numbered markers:

```
1 decide  →  2 retrieve  →  3 answer  →  4 cite
```

### Movement 3 — The witness *(rail: How it answers)*

> **## Every claim points at a passage.**
>
> Istor writes a citation into the answer, and the app resolves it to a passage in a source you own
> or a page it actually fetched. So a number in the answer is never attached to a source that isn't
> there. Two failures go away: it will not invent a fact, and it will not tell you something does
> not exist because it falls outside a training cutoff.
>
> There is a third case, and it is the interesting one. Sometimes the answering model writes a good
> answer and forgets to cite as it goes. Rather than make you wait while a slower model redoes the
> work, Istor sends the small model to fit a citation quickly, and marks what it fitted:
> **Unverified — check the source.**
>
> That word is not a guess about whether the claim is true. It says which of the two models put the
> number there — and it tells you to go and look, which is the whole habit this tool is trying to
> build.

**Both card states**, verified first, unverified second, same source title swapped out:

```
verified                          unverified
Decoding Antikythera              Decoding Antikythera
  | "Hipparchus's lunar theory,     Unverified — check the source.
  |  replicating the Moon"
```

`Unverified — check the source.` **[verbatim]** in `--coral-ink` `#C7292A` against a rule — 5.56:1,
never colour alone. **The unverified card shows no quoted passage**; that is the observable
difference and it is stated as measured. *(Why the passage is absent is an inference, not Thoria's
statement — publish no causal claim about it.)*

### Movement 4 — You can watch it decide *(rail: How it answers)*

> **## You can watch it decide.**
>
> Open the disclosure above any answer and you can read what it did: the reasoning, then the
> passages it pulled, each with the source it came from. It is the same evidence the answer rests
> on, in the product's own words.

The disclosure **[transcribed verbatim from `Black/answering.png`]**, printed already expanded:

```
● Thoughts                                                                    ⌃
✎ Drafting the answer
  The user wants to know what is known about the Antikythera mechanism and what
  remains disputed. I need to synthesize information from the provided context,
  distinguishing between established facts and areas of ongoing debate.

  Known facts from the context:
  - Built around 150-100 BC
  - Discovered in 1901 off Antikythera
  - Contains at least 30 interlocking bronze gears in a wooden frame
  - Front dial: Greek zodiac, Egyptian calendar, Sun/Moon/planets
  - Upper rear dial: 19-year Metonic calendar + Panhellenic athletic games
  - Lower rear dial: 223-month Saros eclipse prediction
```

**Its provenance is worth stating, because it is the same conversation as movement 5's table.**
`Black/answering.png` is the answer *in progress* to *"What do we actually know…and what is still
disputed?"* — the run that produces the disputed table below. So the two exhibits are one
conversation, and neither is the hero's. That is exactly what the fidelity clause two movements down
is for.

Two details from the capture: the first sentence is the user-intent line (**the plan's earlier draft
of this block omitted it** — the disclosure opens with what the user asked for, then what it will
do), and the list runs past the panel's bottom edge, so the final item is the last one fully
visible. The amber dot is kept; the chevron is dropped, because it would open nothing.

### Movement 5 — Where it stops *(rail: Where it stops)*

> **## Where it stops.**
>
> Two different things, and we keep them apart.
>
> **Where it refuses.** It does not guess. If your sources do not cover your question, it says so.
> That refusal is the feature.
>
> **Where it genuinely ends.** It is not a frontier model and it will not out-reason one. It needs
> sources. And local means your machine's specifications are part of the deal.

The table **[transcribed from `White/Question2.png` — the same run as the disclosure above]**. The
capture's table has **twelve** rows; the page prints the **first five**, verbatim, as a real
`<table>`:

| Issue | Status |
|---|---|
| Exact date of construction | Only a range (150–100 BC) is known |
| Exact number of gears | "At least 30" — the exact count is uncertain |
| Exact number of holes in the calendar ring | 354 or 355 (354 is far more probable than 360) |
| Identity of the inventor | Archimedes or Hipparchus — both are candidates |
| Whether it qualifies as a "computer" | The term is debated |

The seven rows left off are the rest of the app's own list — calculator, clock, calendar, planetary
calculator, solar calendar, lunar calendar, solar-lunar calendar — each with `The term is debated`.
**They are cut for length, and the cut is honest**: the five kept are the five with a real status
rather than the same sentence seven times, and the page says nothing about the rest.

Fidelity clause, because the hero has moved:

> This table is from a different conversation than the one above.

The plate's caption — the figure's whole content is one dot, and that is the argument:

> 354 holes are 1.0169° apart. 355 are 1.0141°. At this size the two rings are the same ring, which
> is why the app prints both numbers and picks neither. **The difference is one you cannot see from
> here.**

The SVG itself is `aria-hidden="true"`; that caption is real text.

### Movement 6 — On your machine *(rail: On your machine)*

> **## On your machine.**
>
> Nothing leaves, and what you write stays yours. Those are two consequences of the section above
> rather than two separate promises.

Settings crop caption — **no provider named, and Scrape is not called the default**:

> Settings → Research. Web research is off until you turn it on. With it on, there is no account
> and no key to enter.

*The authorised claim is about what is **required**, never about what is present — Brave is the
backend that would take a key, so "no key is ever used" is false and must not be written.*

The note **[transcribed verbatim from `White/viewingsource-editingnotes.png`]**, 136 words, live
prose — the capture's own word count, shown in the panel's header beside the title:

> **The Metonic cycle**
>
> The Metonic cycle is an astronomical period of 19 tropical years, almost exactly equal to 235
> synodic lunar months or 6,940 days. Named after Athenian astronomer Meton, who introduced it in 432
> BC, the cycle relies on the coincidence that 19 solar years and 235 lunar months differ by only
> about two hours. Ancient civilisations used this relationship to align lunar calendars with the
> solar year by adding seven intercalary leap months over every 19-year period. It forms the
> structural foundation for the Hebrew calendar, traditional Babylonian timekeeping, and the
> Christian calculation of Easter dates. On the Antikythera mechanism, the Metonic cycle appears as a
> five-turn spiral dial on the upper rear plate, complete with individual month names from local
> Greek calendars and a sub-dial tracking Panhellenic athletic games like the Olympics.

**And it is word-for-word the hero's Metonic paragraph** — the same sentence, the same run, minus
the `[1]` citation mark. That is the pairing the whole hero rests on: the answer a reader is looking
at and the note sitting in the rail are not related, they are **the same text**, which is why
*The Metonic cycle* being the fourth row is a proof rather than a coincidence. The same capture also
holds the note's source, `Decoding Antikythera mechanism`, whose text is the passage the hero's
witness card quotes from.

Followed by the one true and unusual thing:

> This is the note Istor wrote while answering the question at the top of this page.

The two controls under every answer, and the sentence they earn:

> Two small controls sit under every answer. The second pulls it straight into a note — the answer
> becomes a note without anyone retyping it.

The requirement, plainly:

> **## What it needs.**
>
> Istor does not ship with a model. It uses Ollama or llama.cpp, which you install yourself. If you
> already have Ollama, Istor will suggest a small model; if you would rather run a different one,
> you choose it in Settings. Nothing is bundled, and nothing is downloaded on your behalf.

*No model name appears anywhere on this page. That is a decision, not an omission: nothing ships, so
there is no default to name, and a recommended model changes on a schedule nobody controls.*

### Movement 7 — ἵστωρ *(rail: ἵστωρ)*

> **## ἵστωρ**
>
> ἵστωρ is the old Greek word for a witness — one who has seen. It comes from the root \*weyd-, *to
> see*, which is also where the Latin *videre* and the English *wit* come from. A witness is not
> the person who knows most; it is the person who was there, and can say what they saw.
>
> That is the whole design of this tool. It does not know about the Antikythera mechanism. It read
> ten documents about it, and it can show you which one said what.

### Movement 8 — Questions *(rail: Questions)*

Plain list. Answers in "we"; **Thoria** named only where a person is meant.

> **## Questions**
>
> **Does anything leave my computer?**
> No. The model, the search and the reading all run on your machine. Web research is off until you
> turn it on in Settings, and when you do turn it on there is no account and no key to enter.
>
> **What hardware do I need?**
> It depends on the model you choose, which is why we do not print a number. A small model runs on
> a modest graphics card; a larger one wants more. Because the requirement follows the model, there
> is no single floor we could publish that would be true for everyone — so we would rather say that
> than pick one and be wrong for half the people reading it.
>
> **Which models can it use?**
> A small model running on your own graphics card, and you choose which. Istor needs Ollama or
> llama.cpp installed; if it finds Ollama it will suggest a model, and you can run any other one
> instead.
>
> **Does it work with no internet at all?**
> Yes, and that is the case it is built for. If the documents in your library already settle your
> question, Istor answers from them and never goes online. With no connection at all, the library
> still works in full.
>
> **Is it open source?**
> The code is at [github.com/ThoriaDevelopment/Istor](https://github.com/ThoriaDevelopment/Istor),
> and you can read all of it — including the parts that would be doing the phoning home, if there
> were any. That is the point of publishing it: "no telemetry" is a claim you can check rather than
> one you have to believe.
>
> **When does it come out?**
> Windows first, with Linux and macOS after. There is no date we are ready to put on it. The code is
> public today and the installer is the next thing.
>
> **Who builds it?**
> Thoria builds Istor. You can find them at [thoria.fyi](https://thoria.fyi).

*The Windows-only fact lives here — not in the opening, where it would lead a page about an offline
AI notebook with an OS compatibility note.*

### The close *(no rail entry)*

On the og-card's teal, hairlines at `rgb(255 255 255 / .12)`.

> **## Istor is not finished.**
>
> There is no installer yet. The code is public today and runs on Windows; Linux and macOS come
> after.
>
> **[ Read the source ]**  →  https://github.com/ThoriaDevelopment/Istor
>
> **ἵστωρ.**
>
> GitHub   Contact   Guides   Thoria   ·   Icons from Lucide, ISC

**The four `href`s, resolved** — no address is invented, and each target is a recorded fact:

| entry | href | why this one |
|---|---|---|
| `GitHub` | `https://github.com/ThoriaDevelopment/Istor` | the product's source — the same target the `[ Read the source ]` button above already uses, so the colophon agrees with the call to action |
| `Contact` | `https://thoria.fyi/` | the developer's own site is where their contact details are published. **It is the only contact channel that exists** — there is no email address anywhere on disk, and inventing one would put a fabricated fact on a page whose whole argument is that it does not overstate |
| `Guides` | `/local-ai-vs-cloud-ai/` | the library, above |
| `Thoria` | `https://thoria.fyi/` | a byline links to the person |

`Contact` and `Thoria` therefore resolve to the same origin. That is honest — both legitimately mean
"reach the developer" — but it is redundant in a four-item strip, and **the one-token fix is to drop
`Contact`**, since the wordmark directly above already names them and the byline already links.
Recorded as a design-plan amendment rather than taken here, because §6 specifies both entries
([thoria.fyi](https://thoria.fyi) is also the FAQ's own answer to *Who builds it?*, two blocks up).

A plain sentence and one real action, per design plan §6 — no slogan, and no email capture. The
repo is the stronger proof: "no telemetry" stops being an assertion when the code is readable.

**The fourth entry is taken, and it closes the library's dead end.** Without it the footer is
`GitHub Contact Thoria` — none of the three goes into the 75 carried pages — so the site's strongest
page would link to the library **zero** times while the library links back to it 75 times through its
own navigation. Thoria took the one-entry fix on 2026-09-18: **`Guides` → `/local-ai-vs-cloud-ai/`.**

`why-local-ai` was the name in this note's first draft and **it does not exist** — the plausible
targets were `local-ai-vs-cloud-ai`, `is-local-rag-private` and `run-research-ai-gtx-1650`, and the
first wins on both counts: it is the comparison the whole page argues, and its `h1` is already the
question a visitor arrives with (*Is local AI more private than cloud AI?*), so the label and the
destination agree. `Guides` is the honest word for it — the library is 75 of these — and it stays
honest until a library index page exists, at which point the entry's `href` changes and the label
does not.

Note the footer's own constraint from §6: links only, spaced, sentence case, no `·` between them —
the single `·` separates the colophon, which is why `Guides` sits with the three links and not after
it.

At launch the same rectangle becomes `[ Download for Windows ]` on `--azure-lift` with `--ink`
text, and a smaller line beneath: `Windows, for now. Linux and macOS after.`

### 404

> **## There is nothing at this address.**
>
> The page you asked for is not here. [Start from the front](https://istor.fyi/).

---

## Appendix B — The manifest, byte-exact

`Source/tools/budget.json` holds this table. `verify-budget.py` asserts it. Bytes are decimal KB
throughout, matching design plan §7's stated convention.

| published path | bytes |
|---|---|
| `og-card.png` | 123,199 |
| `fonts/inter-var.woff2` | 48,256 |
| `fonts/gfs-didot.woff2` | 14,540 |
| `fonts/istor-wordmark.woff2` | 1,892 |
| `img/ground-grain.png` | 451 |
| `img/exhibit-07-viewer.avif` | 12,313 |
| `img/exhibit-07-viewer@2x.avif` | 31,209 |
| `img/exhibit-07-viewer.webp` | 16,486 |
| `img/exhibit-07-viewer@2x.webp` | 55,810 |
| `img/exhibit-07-viewer.png` | 132,111 |
| `img/exhibit-07-viewer@2x.png` | 213,387 |
| `img/exhibit-08-library-rail.avif` | 3,722 |
| `img/exhibit-08-library-rail@2x.avif` | 8,631 |
| `img/exhibit-08-library-rail.webp` | 4,706 |
| `img/exhibit-08-library-rail@2x.webp` | 15,314 |
| `img/exhibit-08-library-rail.png` | 36,438 |
| `img/exhibit-08-library-rail@2x.png` | 49,715 |
| `img/exhibit-09-settings-research.avif` | 4,171 |
| `img/exhibit-09-settings-research@2x.avif` | 8,891 |
| `img/exhibit-09-settings-research.webp` | 4,164 |
| `img/exhibit-09-settings-research@2x.webp` | 13,000 |
| `img/exhibit-09-settings-research.png` | 32,538 |
| `img/exhibit-09-settings-research@2x.png` | 59,409 |

**The two asserted totals:**

| what a phone fetches (1× AVIF) | bytes | what a retina laptop fetches (2× AVIF) | bytes |
|---|---|---|---|
| three bitmaps | 20,206 | three bitmaps | 48,731 |
| ground tile | 451 | ground tile | 451 |
| three fonts | 64,688 | three fonts | 64,688 |
| **total** | **85,345** | **total** | **113,870** |

Design plan §7 prints these as 85.4 KB and 113.9 KB. Both are the sum of that table's rounded rows;
the phone column's byte-exact value is 85.3 KB, and §3 Stage 9 explains why the difference is
display rounding rather than an error.

The PNG set (201,087 B at 1×) is in the artifact for browsers with neither AVIF nor WebP, and is
never fetched by a browser that has either. `og-card.png` is fetched by scrapers and never by a
visitor.

**None of the above moves because the library ships.** These are the new page's own files, and every
assertion about them — 85,345 B on a phone, 113,870 B retina, 702,015 B for the eighteen exports — is
unchanged. A visitor to `/` never requests one byte of the library.

### Appendix B.2 — The carried library, measured

The 75 library pages are asserted as a **group**, not file by file: their bytes would change the
moment anyone edits a summary, and a 75-row table of page sizes would assert nothing worth failing a
build over. Shared assets are asserted byte-exact.

| what | count | bytes |
|---|---|---|
| `/<slug>/index.html` | **75** | 583,864 total — asserted as count + total, not per file |
| `/styles.css` | 1 | 35,522 |
| `/assets/fonts/` — fraunces-600, gfs-didot, inter-var | 3 | 80,892 |
| `/assets/textures/` — fabric-texture.jpg, SOURCE.md | 2 | 1,546,019 |
| `/brand/` — og-card.png, istor-page.svg, istor-wordmark.woff2, wordmark-dark.png, wordmark-light.png, istor-eye.svg | 6 | 154,617 |
| `/robots.txt`, IndexNow key | 2 | 720 |
| **library subtotal** | **89** | **2,401,634 ≈ 2.40 MB** |

Plus `sitemap.xml` (11,052 B today, generated) and **Group 1's 30 files**, for **120 total**. The
artifact is therefore **≈ 3.36 MB**, against ≈ 0.95 MB without the library. `llms.txt` is counted in
Group 1, not here, because only one entry in it is rewritten (§5) — but its 75 library summaries are
the reason it is verified two-sidedly in Stage 8.

**Two things in that table are worth a sentence, because both are surprising and only one is
actionable.**

1. **The texture is 1.47 MB — it is 61% of the library's entire weight, and one file is bigger than
   the whole new page.** `assets/textures/fabric-texture.jpg` is 1,542,136 B, referenced once in
   `styles.css` (line 1006) under `linear-gradient(rgba(10, 16, 18, 0.75), …)` — so **75% of it is
   painted over.** The new page's ground tile is 451 bytes and this plan spends a section on its
   restraint; the library ships 1.47 MB of texture that is mostly hidden by a dark gradient.

   **It is also governed by a law, and that is what decides this.** A first pass at this note called
   it "used on exactly one selector" and a "straight swap of one file — no CSS change and no HTML
   change." Both were wrong, and `assets/textures/SOURCE.md` is the file that says so:

   - it is used **twice** — `.privacy-inner` *and* `404.html .panel`, and the proof ladder below
     measures both;
   - it is **the studio's own photograph**, supplied by Thoria (Canon EOS 7D, 5184×3456, Adobe RGB
     (1998), shot 2019-12-27), not a stock or CC0 asset — so it is not a texture in the abstract,
     it is a picture someone took;
   - its size and quality were **chosen by a measured 11-condition SSIM ladder**, whose widest case
     is 4K at 3825×639 and whose tallest is a phone at DPR 3, and whose stated conclusion is that
     2560×1707 q84 is *"the smallest raster and the lowest quality that keeps the swap invisible at
     every band size the site can produce"*;
   - and **"any change to this file is a change to a law"**: `README.md` law 4, the comment above
     `.privacy-inner` in `styles.css` (lines 989–994), and `SOURCE.md` *"all describe the same
     picture, and they are rewritten together or not at all."* All three say the same sentence —
     *"a **2560px** copy of the 5184px original: same frame, same Adobe RGB profile, same pixels."*

   **So the candidates were re-scored against that ladder rather than against a recompression
   floor,** compositing each exactly as the page does (cover crop → resample to the real device
   raster → the flat scrim) and reporting SSIM, the metric `SOURCE.md` itself uses. The comparison
   is candidate-vs-shipped, so it is *error added on top of* the value that already shipped:

   | condition (SOURCE.md's own ladder) | raster | 1440×960 q72 | 2560×1707 q60 | already accepted |
   |---|---|---|---|---|
   | phone @1x | 375×691 | **0.8727** | 0.9833 | 0.9999 |
   | phone @3x | 1125×2073 | **0.9547** | 0.9891 | 0.9925 |
   | laptop @1x | 1425×639 | 0.9788 | 0.9888 | 0.9997 |
   | laptop @2x | 2850×1278 | **0.9592** | 0.9903 | 0.9942 |
   | wide @1x | 2545×639 | **0.9420** | 0.9844 | 0.9963 |
   | 4K @1x | 3825×639 | **0.9511** | 0.9883 | 0.9904 |
   | 404 panel @1x | 544×420 | 0.9631 | 0.9621 | 0.9999 |

   **The 1440×960 line fails, and the reason is geometry, not taste.** The band is 639 CSS px tall
   at every width, so `cover` at 4K draws whatever raster it is given across 3825 px: the shipped
   2560 is upscaled 1.49× there (0.669 px/CSS px) and the 1440 crop would be upscaled **2.66×**
   (0.376). It loses at six of the seven conditions — worst at phone @1x, **0.873 against a floor of
   0.9999** — and it contradicts all three documents at once, which is the one thing the law
   forbids. **It is not applied.**

   **The 33.5% line is the only one that keeps the law's own words true** — same frame, same profile,
   same *size*, so *"a 2560px copy … same pixels"* survives as a description, and its measured error
   (0.983–0.990 across the wide/laptop/4K cases) sits in the same family as the values the ladder
   already accepted. It still re-encodes the pixels, so it is **still a law change**: it needs
   `README.md` law 4, the `styles.css` comment and `SOURCE.md` rewritten together, and it needs its
   own ladder proof — which **cannot be run here**, because `.improvement/build-texture.py`,
   `.improvement/texture-proof.py` and `.improvement/band.html` do not exist in this tree, and the
   5184px camera original lives at a git blob in a repository that has never been under version
   control.

   **DECIDED — Thoria, 2026-09-18: *"Just leave the texture that way."* The file is not changed, and
   this is now settled rather than deferred.** Both candidates are closed: the 1440×960 crop because
   it fails the ladder it was measured against, and the q60 line because the saving is real but the
   proof is not regenerable in this tree and the law's three documents would all have to move
   together. **The texture ships byte-identical at 2560×1707 q84, 1,542,136 B** (sha256
   `3c07a279…`), which is also the state every measurement above was taken against — so no number in
   this appendix needs re-deriving. The 1.47 MB stays in the library's weight, and it stays with a
   reason: it is the studio's own photograph, its quality was chosen by a proof, and the saving
   available without a new proof is zero. **A future pass that can run the ladder — with the camera
   original and the three `.improvement/` scripts restored — may revisit the q60 line; nothing else
   should.**

   The 1280×854, 1600×1067 and WebP lines from the first pass are dropped: the first is visible, the
   second is dominated by the 2560 line, and the third is *larger* than the JPEG at the same size
   and would need a `styles.css` edit to reach.
2. **Fraunces is 18,096 B that only the library fetches**, and it is the carried asset with no
   counterpart in the new page (§5). It is not dead weight — the legacy `styles.css` declares
   `@font-face` for it and a missing file silently falls back — so it is the one carried asset whose
   absence would be invisible in every check except Stage 9's check 9 and the live-origin font
   check.

---

## Appendix C — The workflow, verbatim

`/.github/workflows/deploy.yml`

```yaml
name: Deploy istor.fyi

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Assemble the site
        run: python Source/tools/build-site.py

      - name: Assert the manifest and the payload
        run: python Source/tools/verify-budget.py _site

      - name: Assert that every link resolves
        run: python Source/tools/verify-links.py _site

      - uses: actions/configure-pages@v5

      - uses: actions/upload-pages-artifact@v3
        with:
          path: _site

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

**No `pip install`.** Both check scripts are standard library, so the build has no dependency that
can drift and nothing to cache. **No `magick`, no Inkscape, no Blender** — artwork is generated
locally and committed, and `verify-budget.py` is what catches a stale regeneration.

`verify-links.py` is the second small script this plan adds, covering Stage 9's checks 4–9:
internal targets resolve across all 120 files, `_site/index.html` is the new page (check 8's marker
string) and carries no script or handler, the nine contrast ratios still compute to the design
plan's numbers, every non-ASCII codepoint in the new page falls inside a declared `unicode-range`,
and the library is intact — 75 pages, `/styles.css` at 35,522 B, self-canonicals present.

**The workflow is unchanged by the carried library, and that is the point.** The library is not a
CI step; it is five lines inside `build-site.py`. CI's job is still to run the assembler once, assert
the manifest, assert the links, and upload `_site/`. If the library ever needs to come back out, the
workflow does not change at all.
