# DESIGN.md · istor.fyi design reference

The design facts a redesign needs, in one place, so they do not have to be
re-derived from `styles.css` every time and so guideline knowledge lives in the
repository rather than in a plugin that may be abandoned next quarter.

**Read `README.md` first.** It holds the site's laws. `.claude/skills/istor-brand/SKILL.md`
holds the brand law and the approved patterns. `design-references.md` holds the
reference sites and what was adopted from each. This file is the measured
inventory underneath all three.

Last measured: 2026-09-18.

---

## 1 · Where things live

| What | Where |
|---|---|
| Design tokens (all of them) | `styles.css`, lines 30–110 |
| Fonts (bundled, three faces) | `assets/fonts/` |
| Brand master | `brand/istor-page.svg` |
| Brand wordmark | `brand/istor-wordmark.woff2`, `brand/wordmark-{light,dark}.png` |
| Generated-asset law | `tools/README.md` |
| Texture provenance | `assets/textures/SOURCE.md` |

There is no build step and no preprocessor. `styles.css` is the source.

---

## 2 · The token contract

Every token is defined in the bare `:root`, and the dark world only redefines
them. Components read tokens and never raw colors.

**The dark block is defined twice on purpose.** Once under
`:root[data-theme="dark"]` (line 64) and once, byte-identically, inside
`@media (prefers-color-scheme: dark)` under `:root:not([data-theme="light"])`
(line 88). The duplicate exists so the page paints correctly before JavaScript
runs. **Editing one without the other is the single easiest way to regress this
site.** An explicit light choice still wins over the media query.

| Token | Light | Dark | Role |
|---|---|---|---|
| `--canvas` | `#FFFFFF` | `#0A0A0A` | page ground |
| `--subtle` | `#FAFAFA` | `#141414` | raised ground |
| `--ink` | `#171717` | `#EDEDED` | headings, primary text |
| `--mist` | `#6E6A66` | `#A5A19B` | **body copy, captions, links** |
| `--hairline` | `#E9E4DE` | `#242424` | borders and rules only |
| `--witness` | `#D93A3A` | `#4DA3FF` | the accent. Red on light, blue on dark |
| `--dot` | `#D93A3A` | `#4DA3FF` | the citation dot. Follows the ground-law |
| `--cite-ink` | `#0E7490` | `#56C0EC` | citation text |
| `--cite-wash` | `rgba(14,116,144,0.12)` | `rgba(86,192,236,0.16)` | citation chip ground |
| `--g1` | `#D93A3A` | `#4DA3FF` | gradient highlight, first stop |
| `--g2` | `#CE7F14` | `#3ED6C4` | gradient highlight, second stop |
| `--btn-shade` | `rgba(10,10,10,0.32)` | `transparent` | darkens the grad button so white text clears 4.5:1 on the warm end |
| `--max` | `68rem` | same | content max width |
| `--ease-out` | `cubic-bezier(0.22, 1, 0.36, 1)` | same | the one curve every entrance uses |

The mark has its own separate four-variable contract (`--mark-ink`,
`--mark-paper`, `--mark-iris`, `--mark-pupil`), documented in
`.claude/skills/istor-brand/SKILL.md`. It is not in `styles.css`.

**There is no spacing scale and no radius scale.** Radii are hardcoded at
`999px`, `1.25rem`, `0.75rem`, `0.5rem`, `6px`, `4px`, `2px` and two asymmetric
page-mark radii (`6px 26px 6px 6px` and `26px 6px 6px 6px`). If the redesign
wants a spacing or radius system, it is being introduced, not inherited.

---

## 3 · Measured contrast

Two models, because they disagree and the disagreement is the useful part.

**WCAG 2.2 is what governs compliance.** APCA is a WCAG 3 draft and is not
normative, but it models perception better at small sizes and in dark mode.

### WCAG 2.2 ratios

| Pair | Ratio | AA body (4.5:1) | AA large (3:1) | AAA body (7:1) |
|---|---|---|---|---|
| Light `--ink` / canvas | 17.93:1 | PASS | PASS | PASS |
| Light `--ink` / subtle | 17.18:1 | PASS | PASS | PASS |
| Light `--mist` / canvas | 5.36:1 | PASS | PASS | fail |
| Light `--mist` / subtle | 5.14:1 | PASS | PASS | fail |
| Light `--witness` / canvas | 4.55:1 | PASS | PASS | fail |
| Light `--cite-ink` / canvas | 5.36:1 | PASS | PASS | fail |
| Light `--cite-ink` / wash | 4.53:1 | PASS | PASS | fail |
| Light `--g1` / canvas | 4.55:1 | PASS | PASS | fail |
| **Light `--g2` / canvas** | **3.15:1** | **FAIL** | PASS | fail |
| Dark `--ink` / canvas | 16.91:1 | PASS | PASS | PASS |
| Dark `--ink` / subtle | 15.74:1 | PASS | PASS | PASS |
| Dark `--mist` / canvas | 7.70:1 | PASS | PASS | PASS |
| Dark `--mist` / subtle | 7.17:1 | PASS | PASS | PASS |
| Dark `--witness` / canvas | 7.54:1 | PASS | PASS | PASS |
| Dark `--cite-ink` / canvas | 9.57:1 | PASS | PASS | PASS |
| Dark `--cite-ink` / wash | 7.44:1 | PASS | PASS | PASS |
| Dark `--g1` / canvas | 7.54:1 | PASS | PASS | PASS |
| Dark `--g2` / canvas | 10.96:1 | PASS | PASS | PASS |

`--hairline` is excluded on purpose: it is a border, never text.

### APCA Lc

| Pair | Lc | APCA verdict |
|---|---|---|
| Light `--ink` / canvas | +104.7 | body, any size |
| Light `--mist` / canvas | +76.7 | **large text only, ≥18px** |
| Light `--witness` / canvas | +70.2 | headlines only, ≥19.5px |
| Light `--cite-ink` / canvas | +76.2 | large text only, ≥18px |
| Light `--cite-ink` / wash | +64.8 | headlines only, ≥24px |
| Light `--g2` / canvas | +58.2 | headlines only, ≥28px |
| Dark `--ink` / canvas | −96.0 | body, any size |
| Dark `--mist` / canvas | **−51.5** | **headlines only, ≥32px** |
| Dark `--witness` / canvas | −50.9 | headlines only, ≥32px |
| Dark `--cite-ink` / canvas | −62.0 | headlines only, ≥24px |

### What this actually means

**The site passes WCAG 2.2 AA for body text everywhere except `--g2` on white**,
which sits at 3.15:1 and is therefore large-text-only. `--g2` is a gradient stop
in the hero, where the text is the H1, so it is in bounds today. It becomes a
defect the moment that gradient is applied to anything at body size.

Three things worth deciding during the redesign, none of them bugs today:

1. **`--mist` carries primary body copy at 11–15px across the entire site**
   (`.loop-grid p`, `.story-copy p`, `.uses-grid p`, `.faq-box details > p`,
   `.showcase-note`, `.sm-tag`, `.sm-foot`, `.head-links a`, and more). WCAG
   passes it at 5.36:1, but by a margin of 0.86:1, and APCA places it in
   large-text territory. It is the lowest-contrast text token on the page and it
   is doing the most work. Darkening it, or reserving it for secondary text and
   setting body copy in `--ink`, is the single highest-leverage contrast change
   available.
2. **Dark mode and APCA disagree with WCAG's optimism.** Dark `--mist` scores
   7.70:1 under WCAG but Lc −51.5 under APCA, which is a large gap. The dark
   theme is not obviously broken, but it is perceptually weaker than the WCAG
   number suggests, and the two themes are not equivalent in comfort.
3. **Light `--witness` at 4.55:1 clears AA by 0.05:1.** Any nudge to that red
   breaks compliance. Treat it as pinned.

If a redesign changes any token, re-measure. The APCA skill is installed
(`~/.claude/skills/apca-contrast/`); run it with
`PYTHONIOENCODING=utf-8`, because the table output contains `≥` and dies on
Windows' default cp1252 stdout otherwise.

---

## 4 · Type

Three faces ship with the site. Nothing is requested at runtime.

| Face | File | Weight | Role |
|---|---|---|---|
| Inter | `inter-var.woff2` (48 KB) | 400–700 variable | `--font-sans` |
| Fraunces | `fraunces-600.woff2` (18 KB) | 600 only | `--font-display` |
| GFS Didot | `gfs-didot.woff2` (14 KB) | 400 only | the ἵστωρ wordmark |

### Two defects in the font stacks

- **`"JetBrains Mono"` is named first in `--font-mono` and is never bundled or
  declared.** It is referenced roughly twenty times across the stylesheet and
  silently falls through to `ui-monospace`, then `Cascadia Code`, then Consolas.
  So every monospace element renders in a different face per machine. Either
  bundle it or drop it from the stack and name what actually renders.
- **`"Istor Wordmark"` appears in the display stack at `styles.css:201` and is
  never declared.** It sits behind `"GFS Didot"`, which is declared, so the
  wordmark renders correctly today. It is a dead entry, not a live bug.

### Sizes actually in use

`0.6875rem` (11px, ×4) · `0.75rem` (12px, ×11) · `0.8125rem` (13px, ×7) ·
`0.875rem` (14px, ×7) · `0.9375rem` (15px, ×13, the workhorse) · `1rem` ·
`1.0625rem` · `1.125rem` · `1.1875rem` · `1.25rem` · `1.3rem` · `1.5rem`,
plus six `clamp()` headlines.

This is not a scale. It is fourteen ad-hoc values, and the 1px-apart pairs
(13/14/15px, 17/18/19px) are indistinguishable to a reader while multiplying
the decisions. A redesign should collapse this to a real modular scale. Note
that GFS Didot runs small: the brand law says nudge it one notch larger than
the surrounding scale suggests.

---

## 5 · Known asset traps

- **The brand master does not rasterize outside a browser.** `brand/istor-page.svg`
  re-inks through CSS custom properties and neither Inkscape nor ImageMagick
  resolves `var()` in SVG presentation attributes. Inkscape renders the page as
  a solid black shape; ImageMagick renders nearly nothing. Resolving the four
  variables to concrete colors first makes it render correctly, verified.
  Browsers are unaffected. Any raster export pipeline needs that resolution
  step built in.
- **`magick`, never `convert`.** On Windows `convert` is
  `C:\WINDOWS\system32\convert`, the FAT-to-NTFS tool. `convert /FS:NTFS C:`
  does real damage.
- **SVGO strips `viewBox` by default.** Override `removeViewBox: false` or
  responsive SVG breaks.

---

## 6 · Authority, and what may be copied

The licence boundary matters more than it looks. Bundling text you have no
right to copy into a skill file relicenses the file.

**Safe to bundle:** USWDS (CC0, no attribution required) ·
GOV.UK Design System (OGL v3) · web.dev (CC BY 4.0) ·
The A11Y Project checklist (Apache-2.0) · Material Symbols (Apache-2.0) ·
Google Fonts (SIL OFL 1.1 — check the Reserved Font Name flag before modifying
and redistributing).

**Cite and link only:** WCAG 2.2 spec and Understanding docs (the W3C Document
Licence grants no right to create derivatives) · Apple HIG (all rights
reserved) · Fluent 2 guidance prose · Practical Typography (the licence page is
`legal.html`, not `license.html`) · Refactoring UI book text · Inclusive
Components (no licence stated, dormant since 2018).

**Viral, avoid:** MDN is CC BY-SA and would relicense anything it is merged
into.

**The pattern to use:** express principles in your own words and link to the
canonical source. That is what `AGENTS.md` in this repo does.

Reference links:
[WCAG 2.2](https://www.w3.org/TR/WCAG22/) ·
[WAI-ARIA APG](https://www.w3.org/WAI/ARIA/apg/) ·
[APCA](https://apcacontrast.com/) ·
[web.dev](https://web.dev/) ·
[USWDS](https://designsystem.digital.gov/) ·
[GOV.UK](https://design-system.service.gov.uk/) ·
[The A11Y Project](https://www.a11yproject.com/checklist/)

---

## 7 · Rules for the redesign

- **Measure before and after.** The site's CWV and zero-request budgets are not
  currently verified by any tooling. Make that a before/after step, not an
  assumption.
- **Do not add a second textured band.** One per page is the law.
- **Do not introduce a runtime dependency to solve a design problem.** Any
  external `<link>`, `@import`, or font CDN breaks the first law in `README.md`.
- **The gradient is two colors per ground, judged in place.** The pairs are
  independent between themes and need not share a hue with the mark.
- **Keep dashes out of site copy.** This is a copy law, and it applies to every
  string a redesign introduces.
- **Re-measure every token you touch.** Section 3 is a snapshot, not a
  guarantee.
