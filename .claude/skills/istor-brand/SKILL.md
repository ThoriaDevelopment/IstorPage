---
name: istor-brand
description: Istor brand law for any design or frontend work on istor.fyi — the mark, the written mark, grounds, gradients, SEO and dwell-time goals, and copy discipline. Use when touching HTML/CSS, designing sections, choosing colors or type, or writing site copy.
---

# The Istor Website Law

Istor is a local-first, private research notebook: add sources, ask grounded
questions, read cited answers. The site is istor.fyi. Its job is to explain
what Istor is at a glance and to get the visitor to download.

The application's design laws do not govern the website. This site has its
own brief and is optimized for SEO and dwell time. The visitor should feel
like they want to stay. Everything below is locked unless Thoria says
otherwise, and open items are marked with a warning at the bottom.

## The mark

- Canonical master: `brand/istor-page.svg`. It is an outlined page with a
  dog-eared fold at 14% ink, a text rhythm of one line above and two below,
  and a centered almond eye.
- The mark re-inks through its CSS variable contract. Define all four, never
  hardcode over them:
  - `--mark-ink`, outline strokes and lines. Light: `#171717`, dark: `#FAFAFA`
  - `--mark-paper`, page interior. Light: `#FFFFFF`, dark: `#171717`
  - `--mark-iris`, eye iris. Light: `#F2726F`, dark: `#56C0EC`
  - `--mark-pupil`, pupil. Light: `#D93A3A`, dark: `#2E97F2`
- Ground-law: the eye and dot are red on light grounds and blue on dark.
  Never mix.
- The standalone eye cut, `istor-eye.svg`, is for tiny slots of 32px or
  smaller only. Never use it where the page mark fits.

## The written mark

- The name is the Greek word ἵστωρ in GFS Didot, followed by the citation
  dot. One trailing period, never decorative ellipses.
- The dot obeys the same ground-law: `#D93A3A` on light, `#4DA3FF` on dark.
- GFS Didot ships one weight. Use regular 400 only, because synthetic bold
  wrecks the hairline strokes. Set `lang="el"` on the element.
- The subset woff2 is bundled locally as `istor-wordmark.woff2`, never
  fetched from Google Fonts at runtime. Fallback stack: `Georgia, serif`.
- Didot runs small: nudge the font size one notch larger than the surrounding
  scale would suggest.

## Palette: grounds

- Light theme: white ground in the `#FFFFFF` family. Dark theme: black ground
  in the `#0A0A0A` family. Both themes are first class, and neither is an
  afterthought.
- Text and body copy stay near ink on light and near white on dark. Greys may
  carry a slight warm bias rather than pure mid grey.
- Beyond the mark's own colors, the site is free to introduce supporting
  hues. The constraint is per element: whatever sits on a ground must read
  well on that ground. The gradient law below is the pattern.

## The gradient highlight, law

The hero highlight is text, and it uses two colors per ground that blend into
a good gradient:

- Light theme: 2 colors that gradient well under a white background.
- Dark theme: 2 colors that gradient well under a black background.

The two pairs are independent. They need not share a hue with each other or
with the mark. The test is always on the actual background: contrast and
blend quality, judged in place. Specific hues are chosen at hero design time.

## Header, adopted pattern from notebook.google

- Left: the page mark and the ἵστωρ wordmark.
- Right: a small number of plain links, then one distinct download CTA pinned
  top right. The CTA reads as *the* action, visually separated from the plain
  links.
- Quiet and unobtrusive. The page content is the show.

## Features, adopted patterns from notebook.google and elicit.com

Two approved feature section layouts, with the final choice made at structure
time:

- Three columns, the "How people are using..." pattern. Line-art vector
  icons, floating and unboxed, with no tile or rounded-square badge behind
  them. Icons carry color to stand out on a minimal page.
- The 1/3 to 2/3 split, the Elicit pattern. The left third is the explanation
  (eyebrow pill, heading, paragraph) and the right two thirds is the visual
  explanation.

In both: no visible borders anywhere. Separation comes from whitespace and
the background itself, and there are no hover color-changing outlines.

## The texture band, adopted pattern from elicit.com

Exactly one section on the site breaks the minimal ground and goes textured,
artistic and editorial for a moment, then snaps back to the quiet ground.
This contrast of worlds is the hook. Craft it deliberately and place it where
the visitor's attention should lock. Final placement is decided at design
time.

## How color arrives, law from answerthis.io

Color beyond ink and witness enters through texture (grain, noise, generated
fields) and is then picked up as text and link colors. Never as flat colored
boxes. When a section needs color, texture introduces it first.

## Interactive elements are design, law from answerthis.io

Links, CTAs and other interactables get the design treatment (gradient text,
textural grounds) so they read as part of the composition, not as furniture
bolted on top of it.

## Two approved mechanisms, from answerthis.io

- Auto rotating list with a progress line: items rotate automatically. A thin
  witness colored line, red on light and blue on dark, runs as the progress
  bar and at its end the list advances. A candidate for the privacy band or a
  claims and citations section.
- FAQ in its own box: the accordion sits in a distinct centered box with its
  own heading, so the section visibly differs from the surrounding ground.

## SEO and dwell

- Semantic HTML first: one h1, descriptive title and meta description,
  canonical URL, Open Graph tags, and lang attributes (el for ἵστωρ).
- Fast by construction: no framework, no build step. Static HTML, CSS and
  bundled assets on GitHub Pages. Every asset pulled over the network is a
  runtime liability, so bundle locally.
- Write for a visitor deciding whether to stay: specific claims over vague
  slogans, breathing room over density.

## Copy

- Active voice. A control says what happens: "Download", then it downloads.
- The privacy claim is load-bearing: local model, local SQLite, and the only
  network traffic is the fetches the user triggers. Never soften or hedge it.
- Specific beats clever. Honest and doc-heavy.

## Writing style, law

- Keep dashes out of site copy. Prefer periods, commas and colons, and
  restructure sentences that reach for an em dash.
- Write like a person explaining their own product, not like a landing page
  template. When a draft sounds like marketing filler, rewrite it around the
  concrete claim it was gesturing at.

## Structure, open, agreed so far

- Stack: static HTML, CSS and bundled assets, published to GitHub Pages.
  The download button targets ThoriaDevelopment/Istor releases, the same host
  the updater trusts.
- Adopted sections so far: header, features (three column and/or 1/3 to 2/3),
  a texture band, FAQ in its own box, and a gradient ending with a treated
  CTA.
- No showcase visuals.
- Remaining page structure and detailed design direction are pending
  Thoria's patches. Do not invent pricing, roadmap, or screenshot sections
  until decided.