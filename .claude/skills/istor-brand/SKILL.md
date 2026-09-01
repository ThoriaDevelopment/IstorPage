---
name: istor-brand
description: Istor brand law for any design or frontend work on istor.fyi — the mark, the written mark, grounds, gradients, SEO and dwell-time goals, and copy discipline. Use when touching HTML/CSS, designing sections, choosing colors or type, or writing site copy.
---

# The Istor Website Law

Istor is a local-first, private research notebook: add sources, ask grounded
questions, read cited answers. The site is istor.fyi — its job is to (1)
explain what Istor is at a glance and (2) get the visitor to download.

**The application's design laws do not govern the website.** This site has
its own brief and is optimized for **SEO** and **dwell time** — the visitor
should feel like they want to stay. Everything below is locked unless Thoria
says otherwise; open items are marked ⚠️ at the bottom.

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

## Palette — grounds

- Light theme: white ground (`#FFFFFF` family). Dark theme: black ground
  (`#0A0A0A` family). Both themes are first-class; neither is an afterthought.
- Text and body copy stay near-ink on light / near-white on dark; greys may
  carry a slight warm bias rather than pure mid-grey.
- Beyond the mark's own colors, the site is free to introduce supporting
  hues — the constraint is per-element: whatever sits on a ground must
  read well **on that ground** (see the gradient law for the pattern).

## The gradient highlight (law)

The hero highlight is **text**, and it uses **two colors per ground that
blend into a good gradient**:

- light theme: 2 colors that gradient well **under a white background**;
- dark theme: 2 colors that gradient well **under a black background**.

The two pairs are independent — they need not share a hue with each other or
with the mark. The test is always on the actual background: contrast and
blend quality, judged in place. Specific hues are chosen at hero design time.

## Header (adopted pattern — notebook.google)

- Left: the page mark + the ἵστωρ wordmark.
- Right: a small number of plain links, then one distinct download CTA pinned
  top-right. The CTA reads as *the* action, visually separated from the plain
  links.
- Quiet and unobtrusive; the page content is the show.

## Feature grid (adopted pattern — notebook.google)

- Three columns ("How people are using …" pattern).
- Line-art vector icons, floating and unboxed — no tile, no rounded-square
  badge behind them. Icons carry color to stand out on a minimal page.
- **No visible borders anywhere** — separation comes from whitespace and the
  background itself; no hover color-changing outlines.

## SEO & dwell

- Semantic HTML first: one `h1`, descriptive `title`/`meta description`,
  canonical URL, Open Graph tags, `lang` attributes (el for ἵστωρ).
- Fast by construction: no framework, no build step — static HTML + CSS +
  bundled assets on GitHub Pages. Every asset pulled over the network is a
  runtime liability; bundle locally.
- Write for a visitor deciding whether to stay: specific claims over vague
  slogans, breathing room over density.

## Copy

- Active voice; a control says what happens ("Download", then it downloads).
- The privacy claim is load-bearing: local model, local SQLite, only network
  traffic is the fetches the user triggers. Never soften or hedge it.
- Specific beats clever; honest and doc-heavy.

## Structure (⚠️ open — agreed so far)

- Stack: static HTML + CSS + bundled assets, published to GitHub Pages.
  Download button targets `ThoriaDevelopment/Istor` releases (same host the
  updater trusts).
- Adopted sections so far: header, three-feature grid.
- No showcase visuals.
- Remaining page structure and detailed design direction: **pending Thoria's
  patches**. Do not invent pricing, roadmap, or screenshot sections until
  decided.