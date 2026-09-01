# Design references: pages Thoria likes, and why

Living document. One section per reference site, in the order Thoria shared
them. The stated "what I liked" is the load-bearing part. The "structure
notes" record what we observed on the live page, and "what this means for
Istor" is the translation. Last updated 2026-09-01.

Governing principle (Thoria, 2026-09-01): the application's design laws do
not carry over to the website. The site is its own brief, optimized for two
things: SEO and dwell time. The visitor should feel like they want to stay
on the page.

---

## 1. notebook.google (Gemini Notebook)

### What Thoria liked (stated)

1. The hero headline, "Understand Anything", highlights the word *Anything*
   with a gradient in an otherwise modern, minimal page. The gradient is the
   single moment of color, and everything around it stays quiet.
2. The top bar structure: the logo mark and application name sit on the left.
   On the right are `Overview`, `Plans`, social links (Discord, Reddit, X as
   small icons), and a distinct "Get the App" action pinned top right. The
   CTA is separated from the plain nav links, so it reads as *the* action.
3. The feature grid is borderless and open: no visible borders, no
   color-changing outlines on hover. Separation is done purely by whitespace
   and the background itself. Icons are line-art vector style, unboxed and
   floating, with no container tile behind them, and they stand out because
   they carry color on an otherwise minimal page.

### Structure notes (observed on the live page)

- Top bar: logo and name on the left. The right side goes plain links,
  then social icons, then the distinct CTA. Sticky, quiet, no background fill.
- Page flow, top to bottom:
  1. Hero: H1 with a gradient on one word, a one sentence subline, and a
     single CTA button.
  2. Feature showcase: alternating rows, a text block (small icon, heading,
     paragraph) beside a product visual.
  3. "How people are using...": three column grid, line-art icons, no
     borders, generous whitespace.
  4. Press and quote wall: cards with a quote and a source logo.
  5. Privacy statement: one large centered claim in its own band.
  6. FAQ: accordion list.
  7. Footer: minimal, logo and legal links.
- Type: geometric sans, large H1, tight small body. Ground is white or near
  white throughout.

### What this means for Istor

- Adopted from this reference (Thoria approved): the top bar skeleton, with
  the istor page mark and ἵστωρ wordmark on the left and a small number of
  plain links plus one distinct download CTA on the right. Also the three
  feature grid, the "How people are using..." pattern: three columns,
  line-art floating icons, no borders, generous whitespace.
- Not adopted: the alternating showcase rows with product visuals. Thoria has
  decided against showcase visuals entirely.
- Gradient highlight, law from Thoria 2026-09-01: the highlight is text, so
  it uses two colors per ground that blend into a good gradient. Light theme
  uses 2 colors that gradient well under a white background. Dark theme uses
  2 colors that gradient well under a black background. The two pairs are
  independent, with no requirement that they share a hue with each other or
  with the mark. Specific hues get chosen when the hero is designed, and
  contrast on the ground is the test.

### Conflicts and open questions

- Borrow only the patterns Thoria named. NotebookLM's press quote wall,
  Plans link, and AI vendor branding are their furniture, not ours.
- Specific gradient hues are open until hero design. The structure of the
  law, 2 colors per ground blend tested on the actual background, is locked.

---

## 2. elicit.com

### What Thoria loved (stated)

The "Stand on the shoulders of giants" band and its gradients: the page goes
from a minimalized white background to texture, artistic and editorial for a
second, then back. That one band takes the attention and hooks the visitor.
The lesson is contrast of worlds. A minimal page earns a huge payoff from one
crafted, textured moment.

### Structure notes (observed on the live page)

- Ground: warm off-white, in the cream family rather than pure white. Serif
  display headlines and sans body. The serif carries the editorial feel.
- Small mono uppercase eyebrows with wide letter spacing ("TRUSTED BY OVER 5
  MILLION RESEARCHERS..."), and small pill labels for section eyebrows
  ("FEATURES").
- The giants band: a full width dark teal panel with an organic generated
  texture, a grain or Turing pattern feel. Headline in the serif, a one
  sentence subline, nothing else. Editorial, quiet, heavy.
- Features section, "Research takes many forms": the left third is the
  explanation (eyebrow pill, serif heading, paragraph) and the right two
  thirds is the visual explanation (icon compositions and imagery). The
  1/3 to 2/3 split repeats for each feature.

### What this means for Istor

- The texture band pattern: adopt it. Exactly one section on istor.fyi should
  break the minimal ground with texture, art or editorial treatment and then
  snap back. It is the hook moment, so place it deliberately. Candidates are
  the privacy claim band or a grounding metaphor band, with final placement
  decided at design time.
- The 1/3 to 2/3 feature split: adopted as the feature section layout. It may
  combine with notebook.google's three feature grid depending on the final
  structure, and both are approved vocabulary.
- Warm biased cream grounds and the serif display with sans body pairing are
  now part of the site's vocabulary, from Thoria's stated preference for
  texture and the observed craft of the site they chose.

---

## 3. answerthis.io

### What Thoria LOVED (stated)

1. Color play on textured backgrounds: textured, grainy grounds introduce
   color, and text picks those colors up, pink to blue to brown to pink
   again, effortlessly. Color is introduced by texture, not by flat blocks.
2. The auto rotating list in "Your Research Stays Yours": a pink line is the
   progress bar and it always runs. When it reaches the end, the list scrolls
   to the next item. Timed, automatic, no clicking.
3. The FAQ as a separate box in the middle, "We Have Answers To Your
   Questions": the accordion lives in its own distinct box, visibly a
   different part of the page.
4. The ending gradient and clickable text: the final section uses a gradient,
   and the interactable text feels like part of the design. In Thoria's
   words, "the interactable parts are a part of the design."

### Structure notes (observed on the live page)

- FAQ box: a large dark rounded box, centered, with its own heading, "Your
  Questions Answered.", and accordion rows with plus and minus marks. The
  box in page contrast is what makes it read as a section.
- Final CTA: a soft rounded panel with headline, subline, and a gradient
  treated clickable CTA. Then a footer that itself is a large gradient, pink
  fading into deep maroon, with plain columns of clickable text.
- Textured color fields: photographic and noise textures tinted pink, brown
  and blue. Headings and links reuse those hues as text colors.

### What this means for Istor

- Texture introduces color and text borrows it. When istor.fyi brings in
  color beyond ink and witness, it arrives through texture (grain, noise,
  generated fields) and then shows up as text and link colors, never as flat
  colored boxes. This is the approved way to broaden the palette.
- Auto rotating list with a progress line: approved mechanism, and a
  candidate for the privacy band or a claims and citations section. For
  example, rotating claims like "Your sources never leave this machine",
  with the witness colored line as the progress bar. Red line on light, blue
  line on dark.
- FAQ in its own box: approved. The accordion sits in a distinct centered box
  rather than as bare rows on the ground.
- Interactables are design: links and CTAs get the gradient and textural
  treatment, so interactive elements feel part of the composition rather than
  bolts on it.