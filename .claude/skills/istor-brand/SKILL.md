---
name: istor-brand
description: Istor brand law for any design or frontend work on istor.fyi — palette, mark usage, typography, motion, and copy discipline. Use when touching HTML/CSS, designing sections, choosing colors or type, or writing site copy.
---

# The Istor Brand Law

Istor is a local-first, private research notebook: add sources, ask grounded
questions, read cited answers. The brand is **the witness** — a document that
watches, and a name that grounds every claim. Everything below is locked
unless Thoria says otherwise. Open items are marked ⚠️ at the bottom.

## The mark

- Canonical master: `brand/istor-page.svg` — an outlined page, dog-eared fold
  at 14% ink, text rhythm 1 line above + 2 below, centered almond eye.
- The mark re-inks through its CSS-variable contract. Define all four, never
  hardcode over them:
  - `--mark-ink` — outline strokes and lines (light: `#171717`, dark: `#FAFAFA`)
  - `--mark-paper` — page interior (light: `#FFFFFF`, dark: `#171717`)
  - `--mark-iris` — eye iris (light: `#F2726F`, dark: `#56C0EC`)
  - `--mark-pupil` — pupil (light: `#D93A3A`, dark: `#2E97F2`)
- **Ground-law**: the eye/dot is red on light grounds, blue on dark. Never mix.
- The standalone eye cut (`istor-eye.svg`) is for tiny slots (≤32px) only —
  never use it where the page mark fits.

## The written mark

- The name is the Greek word **ἵστωρ** in GFS Didot, followed by the
  **citation dot** — one trailing period, never decorative ellipses.
- The dot obeys the same ground-law: `#D93A3A` on light, `#4DA3FF` on dark.
- GFS Didot ships one weight. **Regular 400 only** — synthetic bold wrecks
  the hairline strokes. Set `lang="el"` on the element.
- The subset woff2 is **bundled locally** (`istor-wordmark.woff2`), never
  fetched from Google Fonts at runtime. Fallback stack: `Georgia, serif`.
- Didot runs small: nudge the font-size one notch larger than the surrounding
  scale would suggest.

## Palette — paper and ink

- Grounds come from the mark, not from a landing-page template:
  - light: canvas `#FFFFFF`, subtle `#FAFAFA`, ink `#171717`
  - dark: canvas `#0A0A0A`, surface `#171717`, text `#EDEDED`
- The only accent is the witness pair (red/blue by ground). Never introduce a
  second accent, a gradient hero, or purple.
- Greys carry a slight warm bias (mist `#EDE9E4` territory), never pure mid-grey.

## Motion

- Near-zero motion is the design soul. The **only** sanctioned ambient motion
  is the breath on the mark: opacity 0.72 → 1, ~3.6s ease-in-out, infinite.
- Only `transform` and `opacity` are ever animated.
- Everything animating is gated by `prefers-reduced-motion: reduce`.
- No scroll-jacking, no parallax, no entrance-choreography.

## Design discipline

- No stock landing-page furniture: no purple-to-blue gradient hero, no
  `rounded-lg` everywhere, no emoji section markers, no centered-everything.
- Type scale is deliberate and small; headings get `text-wrap: balance`;
  body text stays near 65 characters.
- Theme is structured at the token level: complete light palette on bare
  `:root`, dark redefinition under `[data-theme="dark"]` / `prefers-color-scheme`,
  components read tokens only. No color may exist solely inside a theme block.
- Wide content scrolls inside its own container; the body never scrolls sideways.
- No telemetry of any kind, and nothing that implies otherwise.

## Copy

- Active voice; a control says what happens ("Download", then it downloads).
- The privacy claim is load-bearing: local model, local SQLite, only network
  traffic is the fetches the user triggers. Never soften or hedge it.
- Specific beats clever; house style is doc-heavy and honest.

## Structure (⚠️ open — agreed so far)

- Purpose: (1) explain what Istor is at a glance, (2) get the visitor to
  download. Both, because nobody downloads what they don't understand.
- Stack: no framework, no build step — static HTML + CSS + bundled assets,
  published to GitHub Pages. Download button targets
  `ThoriaDevelopment/Istor` releases (same host the updater trusts).
- Page structure and detailed design direction: **pending Thoria's direction**.
  Do not invent pricing, roadmap, or screenshot sections until decided.