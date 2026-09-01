# Design references — pages Thoria likes, and why

Living document. One section per reference site, in the order Thoria shared
them. The stated "what I liked" is the load-bearing part; the "structure
notes" are what we observed on the live page; "what this means for Istor" is
the translation. Last updated 2026-09-01.

**Governing principle (Thoria, 2026-09-01):** the application's design laws
do *not* carry over to the website. The site is its own brief, optimized for
two things: **SEO** and **dwell time** — the visitor should feel like they
want to stay on the page.

---

## 1. notebook.google (Gemini Notebook)

### What Thoria liked (stated)

1. **Hero headline — "Understand Anything"** — with the word *Anything*
   highlighted using a gradient, inside an otherwise modern, minimal page.
   The gradient is the single moment of color; everything around it stays
   quiet.
2. **The top bar structure**:
   - left: logo mark, then the application name;
   - right: `Overview`, `Plans`, social links (Discord / Reddit / X as small
     icons), and a distinct **"Get the App"** action pinned top-right.
   - The CTA is separated from the plain nav links — it reads as *the* action.
3. **The feature grid — borderless and open**:
   - no visible borders, no color-changing outlines on hover; separation is
     done purely by whitespace and the background itself;
   - icons are line-art vector style, "unboxed and floating" (no container
     tile behind them), and they stand out because they carry color on an
     otherwise minimal page.

### Structure notes (observed on the live page)

- Top bar: logo + name left; right side ordered plain links → social icons →
  distinct CTA. Sticky, quiet, no background fill.
- Page flow top → bottom:
  1. Hero: H1 ("Understand Anything" — gradient on one word), one-sentence
     subline, single CTA button.
  2. Feature showcase: alternating rows — text block (small icon, heading,
     paragraph) beside a product visual.
  3. "How people are using …" — three-column grid, line-art icons, no
     borders, generous whitespace.
  4. Press/quote wall — cards with quote + source logo.
  5. Privacy statement — large centered claim, its own band.
  6. FAQ — accordion list.
  7. Footer: minimal, logo + legal links.
- Type: geometric sans, large H1, tight small body. Ground is white/near-
  white throughout.

### What this means for Istor

- **Adopted from this reference** (Thoria approved): the **top bar** skeleton
  — istor page mark + ἵστωρ wordmark left; right side a small number of plain
  links, then one distinct download CTA top-right — and the **three-feature
  grid** (the "How people are using …" pattern): three columns, line-art
  floating icons, no borders, generous whitespace.
- **Not adopted**: the alternating showcase rows with product visuals —
  Thoria has decided against showcase visuals entirely.
- **Gradient highlight (law, Thoria 2026-09-01)**: the highlight is *text*,
  so it uses **two colors per ground that blend into a good gradient**:
  - light theme: 2 colors that gradient well **under a white background**;
  - dark theme: 2 colors that gradient well **under a black background**.
  The two pairs are independent — no requirement that they share a hue with
  each other or with the mark. Specific hues get chosen when the hero is
  designed (contrast on the ground is the test).

### Conflicts & open questions

- Borrow only the *patterns* Thoria named. NotebookLM's press-quote wall,
  Plans link, and AI-vendor branding are their furniture, not ours.
- Specific gradient hues are open until hero design; the *structure* of the
  law (2 colors per ground, blend-tested on the actual background) is locked.

---

## 2. elicit.com

### What Thoria loved (stated)

- The **"Stand on the shoulders of giants"** band and its gradients: the page
  goes from a minimalized white background to **texture, artistic, editorial
  for a second** — then back. That one band takes the attention and hooks the
  visitor. The lesson: *contrast of worlds*. A minimal page earns a huge
  payoff from one crafted, textured moment.

### Structure notes (observed on the live page)

- Ground: warm off-white (cream family, not pure white). Serif display
  headlines + sans body — the serif carries the editorial feel.
- Small mono uppercase eyebrows with wide letter-spacing ("TRUSTED BY OVER 5
  MILLION RESEARCHERS…"), small pill labels for section eyebrows ("FEATURES").
- The giants band: full-width **dark teal panel with an organic generated
  texture** (grain/Turing-pattern feel) — headline in the serif, one-sentence
  subline, nothing else. Editorial, quiet, heavy.
- Features section ("Research takes many forms"): **left ⅓ = the explanation**
  (eyebrow pill, serif heading, paragraph), **right ⅔ = the visual
  explanation** (icon compositions / imagery). The 1/3–2/3 split repeats per
  feature.

### What this means for Istor

- **The texture band pattern**: adopt — exactly one section on istor.fyi
  should break the minimal ground with texture/art/editorial treatment and
  snap back. It's the "hook" moment; place it deliberately (candidate: the
  privacy claim band or a grounding metaphor band — final placement at design
  time).
- **The 1/3–2/3 feature split**: adopted as the feature-section layout (this
  may combine with notebook.google's three-feature grid depending on final
  structure — both are approved vocabulary).
- Warm-biased cream grounds and serif-display/sans-body pairing are now part
  of the site's vocabulary (Thoria's stated preference for texture + the
  observed craft of the site they chose).

---

## 3. answerthis.io

### What Thoria LOVED (stated)

1. **Color play on textured backgrounds**: textured (grainy/noisy) grounds
   introduce color, and text picks those colors up — pink → blue → brown →
   pink again, *effortlessly*. Color is introduced by texture, not by flat
   blocks.
2. **The auto-rotating list in "Your Research Stays Yours"**: a **pink line is
   the progress bar** that always runs; when it reaches the end, the list
   scrolls to the next item. Timed, automatic, no clicking.
3. **The FAQ as a separate box in the middle** ("We Have Answers To Your
   Questions"): the accordion lives in its own distinct box — visibly a
   different part of the page.
4. **The ending gradient + clickable text**: the final section uses a gradient
   and the interactable text feels like part of the design — "the
   interactable parts are a part of the design."

### Structure notes (observed on the live page)

- FAQ box: large dark rounded box, centered, with its own heading ("Your
  Questions Answered.") and accordion rows (＋ / −). The box-in-page contrast
  is what makes it read as a section.
- Final CTA: soft rounded panel with headline, subline, gradient-treated
  clickable CTA — then a footer that itself is a large gradient (pink fading
  into deep maroon) with plain columns of clickable text.
- Textured color fields: photographic/noise textures tint pink/brown/blue;
  headings and links reuse those hues as text colors.

### What this means for Istor

- **Texture introduces color; text borrows it.** When istor.fyi brings in
  color beyond ink+witness, it arrives through texture (grain, noise,
  generated fields) and then shows up as text/link colors — never as flat
  colored boxes. This is the approved way to broaden the palette.
- **Auto-rotating list with a progress line**: approved mechanism, candidate
  for the privacy band or a claims/citations section (e.g., rotating claims:
  "Your sources never leave this machine" → "…" with the witness-colored line
  as the progress bar). Red line on light / blue line on dark.
- **FAQ in its own box**: approved — the accordion sits in a distinct centered
  box, not as bare rows on the ground.
- **Interactables are design**: links/CTAs get the gradient/textural
  treatment so interactive elements feel part of the composition, not bolts
  on it.