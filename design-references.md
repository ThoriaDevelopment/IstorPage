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