# istor.fyi — design plan

Draft 2 · 2026-09-18 · for Thoria

Basis: the five references in `References/`, the locked assets in `Assets/brand/`, the
brief, and the **35 screenshots** in `Assets/Istor Screenshots/Black/` and `White/`.
Colour values below marked *(measured)* were sampled from those screenshots, not guessed.

**Draft 2 is the direction, settled in sixteen answers on 2026-09-18, then revised by three
further passes of four the same day.** Read §0 first — it changed, and the change is a
subtraction. §9's first table lists every reversal and what it cost; the second lists the
sixteen answers and what each one changed; the third lists what the four **verified-source**
captures broke; the fourth lists what **Thoria's four answers** changed — the two-model
mechanic, the hero's theme, and the Viewer; the fifth lists the four after those, which set the
**quality target, the compute budget, and what the page may say about the model**; and the sixth
lists the last three, which **close the plan**. The tables after the second are the newest and
least certain edits in the document.

**§7 ends with the artwork and the head** — the ground, the icon set, the one drawn figure, the
favicons and card, and the `<head>` itself. Everything in it is generated, deterministic, and
measured: a 451-byte grain tile and a 1,318-byte plate, with the generator scripts checked in
beside them. **The head is the newest part of the document and the last gap it had** — an OG
image needs an absolute URL, so the canonical origin turned out to be a build input.

**§3 closes with the whole page drawn in seven frames** — the hero at working size was already
there, and this is the rest of it, in order, ending with the lighter build. It is the only part
of the document that shows two claims side by side, and it immediately found two faults in §3
that prose had carried for several revisions: the rail's rows were called "eight movements" when
only six are labelled, and the hero's wireframe still drew the app's source-status dot in a slot
where the page draws nothing. Both are corrected, and §9's first table records why.

---

## 0. The idea in one paragraph

Istor's whole claim is that a small model can be trusted **because you can point at what it
read**. The app already behaves this way: every sentence carries a footnote, and every
footnote opens the source it came from. The name says the same thing — ἵστωρ, "one who has
seen" — and the mark is an eye on a page. So there is nothing to invent. The site's job is
to *show* that, in the first screen.

**And it is not only "which source" — it is "which model".** Istor runs **two models**, and the
division of labour between them is the strongest single fact in the product. One is small and
heavily instructed, and its job is to make the fast calls. Thoria, 2026-09-18:

> *"1 is the cheaper model which is heavily instructed. It makes decisions quickly. Like when
> web search is open, it decides if the local sources is enough, if yes it just uses local
> sources. That's not the only thing it does, but it's the main one."*

So **the grounding gate is the cheap model's job.** The reason this product can answer a
question with no network at all is that a small, fast, cheap model is asked a cheap question
first — *do the documents already in the library settle this?* — and when it says yes, the
answering model never touches the network. That reframes the whole pitch: the gate is not a
clever architecture, it is one model being asked to be decisive so another can be slow.

The other thing that cheap model does is on the citation path. The answering model writes the
answer and usually cites as it goes; when it drops a citation, the cheap model retro-fits one —
a deliberate latency trade, since making the reader wait on the slower model is worse than
attaching a citation quickly. A citation it attached is marked **"Unverified — check the
source."** So the app discloses the *provenance of the number*, not just its target. **Draft 1
did not have any of this, because I had misunderstood what "Unverified" meant** — I had it as
"the source doesn't support this claim", which is a different and much more ordinary thing.
See §5 movement 3.

**The landing page opens as an Istor window, and then stops being one.** The first movement is
the app's own three columns, at the app's own measured widths: the **Library rail** on the
left, the reading column in the middle, and the **Notes rail** on the right — with the witness
card drawn open over the answer, anchored to the citation it belongs to, exactly as the app
draws it. After that the rails go quiet and the page relaxes into a single reading column for
the remaining seven movements. The window is a *frame*, not the spine.

**The notes rail is not decoration and it is not the witness.** An earlier draft put an
invented "Witness panel" in that column. The app has no such panel; its right column is the
notebook, and the witness is a popover. Keeping the real rail fixes a lie (§3) *and* buys
something: the notebook stops being a claim in movement 6 and becomes visible in the first
screen, holding the very note that the hero's answer is about.

**And nothing on the page responds to a click.** This was the largest reversal in draft 2 and
it is deliberate: the conceit is carried by the layout alone, which costs no JavaScript, no
animation library, and nothing on a weak phone. Two consequences follow immediately, and both
are corrections rather than losses:

- **The citation marks stop being buttons.** With nothing behind them, a focusable control
  that does nothing is worse than plain text — a keyboard user tabs to a dead element. They
  become superscript numerals with the source named in visually-hidden text. The **one** mark
  the open card belongs to keeps the app's filled azure disc, as a *static* state.
- **The line *"Click a number to see the passage it came from"* is cut.** There is nothing to
  click. The card is simply already open, and the mark it belongs to is shown active, so the
  mechanism is legible by looking rather than by doing.

---

## 1. Colour

The palette is the product's own. Nine values, no more — four neutrals, one hairline, two
blues, one ink, and one verdict.

| token | hex | role | contrast *(verified)* |
|---|---|---|---|
| `--paper` | `#FFFFFF` | the reading column | — |
| `--chrome` | `#FAFAFA` | both rails, titlebar, any recessed surface | — |
| `--fill` | `#F4F6F8` | the single neutral fill: message bubbles, terminal blocks, inline code | — |
| `--ink` | `#171717` | all text, all rules ≥2px | 17.9:1 on paper |
| `--ink-2` | `#5C5C5C` | secondary text, source metadata | 6.4:1 on chrome |
| `--azure` | `#0066CC` | **the accent** — the app's own colour for a citation, used here for citation marks (now static, §0) and for the links that do still lead somewhere | 5.57:1 on paper; white-on-azure buttons 5.57:1 |
| `--azure-lift` | `#4DA3FF` | the same blue on the dark ground | 6.6:1 on `#0D1D20` |
| `--coral-ink` | `#C7292A` | **the verdict ink** — one string on the whole page: *"Unverified — check the source."* Never decoration | 5.56:1 on paper, 5.32:1 on chrome |
| `--rule` | `#D3D3D4` | hairlines | *(measured — the app's own border)* |

**Floor on the neutral ramp.** `#767676` measures 4.35:1 on `--chrome` and fails AA. Do not
go lighter than `--ink-2`. If a value looks too quiet, lighten the *size*, not the colour.

**The app's second theme, measured — because the hero renders in it.** The window in movement 1
is the app's **Black** theme (Thoria's pick, 2026-09-18: *"verifiedsource.png as black looks the
best"*). Same run, same words, one token set swapped. Sampled from `Black/verifiedsource.png`:

| role | light | black |
|---|---|---|
| rails, titlebar | `--chrome` `#FAFAFA` | `#0A0A0A` |
| centre reading column | `--paper` `#FFFFFF` | `#0B0C0F` |
| the single fill — bubble, composer field | `--fill` `#F4F6F8` | `#10141B` |
| all text | `--ink` `#171717` | `#E5E8EE` |
| accent | `--azure` `#0066CC` | `--azure-lift` `#4DA3FF` *(already in the table)* |
| hairlines | `--rule` `#D3D3D4` | **none — see below** |

**The Black theme has no column rules, and this is not an oversight.** Measured across an empty
row: the light theme separates the centre column from the right rail with a 1px `#D3D3D4`
hairline, and Black separates them with **nothing at all** — `#0A0A0A` runs unbroken from the
rail through the boundary, and the structure is carried entirely by the centre column shifting
to `#0B0C0F`. That is R +1, G +2, **B +5**: a *hue* shift, not a lightness shift, which is why
it reads as depth rather than as a line. The DOM replica must reproduce it as a ground change,
not by drawing a rule that the app does not draw. Both themes are real product material; the
light one keeps its hairline (§3).

**Coral is the warning ink, not decoration** *(corrected in draft 2 — my first reading was
wrong).* I originally recorded `#D93A3A` / `#F2726F` as appearing in the mark's artwork only.
A second measurement of `White/Question1.png` disproves it: the source card renders
**"Unverified — check the source."** in coral, `(232,91,92)` ≈ `#E85B5C` — the same iris
family. So the app's semantics are **azure = interactive, green `#4BB581` = ready, amber
`#B35208` = working, coral = unverified**. The site inherits all four meanings and uses coral
in exactly one place: the witness card's verdict line — which marks **which of the app's two
models wrote the citation**, not whether the claim is supported (§5 movement 3). It does
**not** inherit the app's value — at `#E85B5C` the string measures **3.45:1** and fails AA.

So `--coral-ink` is `#C7292A`: the app's hue held at 359.6°, taken down to L47 until it clears
the floor. Two things worth noting about the number. It measures **5.56:1**, which is within a
hundredth of `--azure`'s 5.57:1 — the page's two colour-carrying inks have the same visual
weight, so a verdict never shouts louder than a citation. And it is still a *red*, not the
app's salmon: darkening had to go further than taste would prefer, which is the honest reason
the app's own coral is not reused. **The verdict is never carried by colour alone** — the
string sits against a rule, so it survives greyscale, colour blindness, and forced-colours
mode.

**The blue question is settled, and not by a coin flip.** The three blues in the assets are:

| source | value | hue / sat / light |
|---|---|---|
| app accent *(measured)* | `#0066CC` | 210° · 100% · **40%** |
| locked dark wordmark + og-card | `#4DA3FF` / `#4CA1FE` | 211° · 100% · **65%** |
| icon SVG's documented dark pair | `#56C0EC` / `#2E97F2` | **198°** · — · — |

The first two are **the same hue at two lightnesses** — one blue, two worlds. The third is a
different hue and is the outlier. Azure wins on evidence, not preference.

Consequence to accept: with azure, the icon's iris and pupil are within 2/255 of each other on
the dark ground, so the eye flattens to a single disc. **Decided: derive the pupil.**
`--azure-deep` = **`#0073E6`** — hue 210.0°, saturation 100%, lightness 45.1%, i.e. the exact
lightness midpoint between `#0066CC` (40%) and `#4DA3FF` (65%), holding the family's 100%
saturation. (An earlier note of mine suggested `#2E7FD6`; at 67% saturation it drops out of
the family. Use `#0073E6`.) Against the teal ground the iris reads 6.59:1 and the pupil
3.79:1 — a visible difference, and in the right direction, with the pupil darker than the
iris. One brand blue, three steps: `#0066CC` on white, `#4DA3FF` and `#0073E6` on dark.

**Functional colours**, borrowed from the app and used *only where the site depicts real app
state*, never as decoration: `#B35208` waiting (5.1:1 on paper — safe for text),
`#4BB581` ready (2.6:1 — **dot only, never text**; pair it with `--ink-2` if a label is
needed).

**The dark world** is the og-card's ground, and it closes the page: a radial from `#132E2F`
at the top-right down to `#0D1D20` at the edges. Hairlines there are
`rgb(255 255 255 / 0.12)` — an alpha, so the rule works over the gradient.

**This is not a stylistic choice — it is the app's own second theme.** The app ships both
White and Black themes. So the closing movement uses the **Black-theme capture** of the app,
the ground is the og-card's teal rather than a flat black, and the mark re-inks on the same
contract it already re-inks on inside the app. Shoot every demo run in both themes (see
`demo-library.md`) and the page's light half and dark half are the same product in its two
honest states. Most tokens are shared; five change per world — `--paper`, `--chrome`, `--ink`,
`--rule`, and `--azure` swapping to `--azure-lift`, which is the same blue at L65 because
`#0066CC` fails on a dark ground.

---

## 2. Type

Two faces. Both already on disk.

| file | what it actually is *(verified)* | job |
|---|---|---|
| `Assets/brand/istor-wordmark.woff2` | GFS Didot Regular, subset to **16 codepoints**: space, period, combining acute + rough breathing, and the letters of ἵστωρ | **the wordmark, only** |
| `Assets/fonts/gfs-didot.woff2` | GFS Didot Regular, **Latin only — 0 Greek codepoints**, 219 glyphs, incl. em dash, curly quotes, ellipsis | **display**: h1, h2, pull-quotes, numerals |
| `Assets/fonts/inter-var.woff2` | Inter, variable `wght 100–900`, Latin subset | **everything else** |

Both Didot files report `family: "GFS Didot"`. Declare them as **one family with two
`unicode-range`s**, so a heading mixing Latin and Greek resolves to the right file
automatically. `Assets/fonts/fraunces-600.woff2` is dropped — as agreed.

**Correction to an earlier note of mine.** I had written that the wordmark "ships as a font
file and can be set as live text at any size." That is true of
`brand/istor-wordmark.woff2` — but it can set **only the word ἵστωρ** (plus ί ώ ἱ ὡ ὥ ῥ
variants). The `fonts/gfs-didot.woff2` I had been treating as the wordmark's source contains
no Greek at all. Two files, two jobs. The good news is that this is exactly what a giant
footer wordmark needs, and it means **the footer wordmark and the Latin headlines are
literally the same typeface** — none of the three reference sites manage that.

**Weight is not available.** GFS Didot Regular is the only display weight, and there is no
italic. So hierarchy has to come from size, space, and measure — never from bold, never from
faux-bold. This is a constraint that helps: it rules out the commonest display default.

**Scale** (base 17px, ratio ≈1.2 with one large jump at display):

| token | size | line-height | face |
|---|---|---|---|
| `--t-xs` | 13px | 1.45 | Inter |
| `--t-sm` | 15px | 1.5 | Inter |
| `--t-base` | 17px | **1.65** | Inter |
| `--t-lede` | 20px | 1.55 | Inter |
| `--t-h3` | 22px | 1.35 | Inter, 600 |
| `--t-h2` | 30px | 1.2 | **Didot** |
| `--t-h2-lg` | 40px | 1.12 | **Didot** |
| `--t-h1` | 68px / 40px mobile | 1.05 | **Didot** |
| `--t-mark` | 176px → viewport-width | 0.9 | **wordmark subset** |

Letter-spacing: Inter body `0`; Inter headings `-0.01em`; Didot display `-0.005em` (a Didone
is already tight — do not add tracking). **No all-caps anywhere. No tracked-out labels.**

**One more Inter weight is in use, and it is the app's, not mine.** The hero answer's run-in
headings — `The Metonic cycle`, `The Callippic cycle` — are **Inter 600 at `--t-base`**, in the
middle of a regular-weight sentence on the same line (§3, §4). Bold here means "this is a
sub-topic of the answer", which is information. It is **not** the headline-accenting move:
the site never bolds a word inside a heading for emphasis. Bold exists in `--t-base` and
`--t-h3` only.

Measure: body text caps at **66ch**. The Didot pull-quotes may run to 74ch (serif, so slightly
longer, per *Elements of Typographic Style*).

---

## 3. Layout

### Desktop (≥1080px)

The three columns exist for the **first movement only**. From movement 2 on, everything below
sits in the centre reading column at the same measure, and the rails are empty ground.

Widths are the app's own, **measured** from the 2× captures and **identical in both themes**
(`White/verifiedsource.png`, `Black/verifiedsource.png`): **180 / 594 / 185** CSS px. The two
rails are near-equal, and the Library rail is resizable
and has a full-screen mode, so its width drifts between captures — **the hero picks this state
and says so**. Earlier drafts used 232/660/300, which came from an expanded state and is not
the default.

```
┌────────────────┬────────────────────────────────────┬──────────────────┐
│ Library     < >│                                    │ < >        Notes │
│ -------------  │                                    │ ---------------- │
│ ▸What it is    │      +---------------------------+ │ Filter notes...  │
│ How it answers │      | Tell me about the cycles. | │                  │
│ Where it stops │      +---------------------------+ │ ancient astron...│
│ On your machine│                                    │ The National A...│
│ ἵστωρ          │ Thoughts ▾                         │ The Saros cycle  │
│ Questions      │                                    │ The Metonic cy...│
│                │ The Antikythera mechanism          │ X-ray data fro...│
│ -------------- │ incorporated several key           │ Fragment C of ...│
│ [Read the      │ astronomical cycles:               │ Reconstruction...│
│   source]      │                                    │ Antikythera me...│
│                │ **The Metonic cycle** is an        │ Antikythera wr...│
│  --chrome      │ astronomical period of 19          │ Decoding Antik...│
│  1px --rule -> │ tropical years, almost exactly     │                  │
│                │ equal to 235 synodic lunar         │ ---------------- │
│                │ months or 6,940 days.              │ New note         │
│                │              +----------------+    │                  │
│                │   o ---------| Decoding       |    │                  │
│                │              | Antikythera    |    │                  │
│                │              | | "s lunar      |   │                  │
│                │              | |  theory,      |   │                  │
│                │              | |  replicating  |   │                  │
│                │              | |  the Moon"    |   │                  │
│                │              +----------------+    │                  │
│  --chrome      │                                    │  --chrome        │
│  1px --rule <- │                                    │  1px --rule <-   │
└────────────────┴────────────────────────────────────┴──────────────────┘
```

*Glyph legend, because the wireframe cannot draw them:* `▸` marks the current rail row **in the
diagram only** — on the page there is no glyph in that slot at all, and the row's ink is the
only marker. `o` is the citation's active state — the filled azure disc that anchors the popover
— `▾` is the `Thoughts` chevron, **which the site drops** (§4), and `< >` is the app's own
expand/collapse pair, which the site does not reproduce either. **`·`, the app's source-status
dot, appears nowhere in this wireframe and nowhere on the page**, and that is a correction rather
than an omission: the app puts it in the leading slot because its rows are *sources*, and sources
have fetch states, while these rows are *movements*, which have none. The glyph was copied across
from the app's rail during an early draft, where it would have been the one detail in the replica
that means nothing at all.

**The hero renders this in the app's Black theme** — Thoria's pick, 2026-09-18. The wireframe is
the light theme's, and it is still the right diagram because the *geometry* is identical in both;
what changes is the token set (§1's black column) and one structural fact: **the two
`1px --rule` markers in the diagram do not exist in Black.** There, `#0A0A0A` runs unbroken from
the left rail through to the notes rail, and the only thing marking a column edge is the centre
column's shift to `#0B0C0F`. The replica must show that as a ground change, not as a border it
would have to invent.

**And that is the whole page's structure in miniature:** the app's dark theme is what the site
shows as *product*, and the light paper is what the site uses for its own voice. All three
bitmaps in §7 are Black for the same reason. The app's default is light, and copy says so where
it matters — the site is showing a theme, not the only theme.

- **Left rail 180px**, `--chrome`, 1px `--rule` on its right edge. **This is the one place the
  replica is not a replica, and it is stated rather than glossed.** It borrows the Library
  rail's grammar — header, a list of rows with a leading slot, one action pinned at the foot in
  the position where the app has `Add source` — but its rows are **the page's six rail entries**,
  with the repo link at the foot. A reader needs a map, and the alternative — a rail full of
  invented source names — would be the small deception this section forbids. The current row is
  inked; the rest are `--ink-2`, and **that ink difference is the only marker: no numbers, no
  progress dots, no status dot** — the cut is recorded in §9's first table. The foot holds
  **one action**, `[Read the source]`, pointing at `github.com/ThoriaDevelopment/Istor` — **the
  same label the close uses for the same action**, because an action keeps its name through the
  flow (§6). The double meaning is free and deliberate: on a page whose whole argument is that
  you can check what the tool read, "the source" is the repository *and* the thing the citation
  points at.
- **Six rows, eight movements, and the difference is not a slip.** §5 runs eight movements but
  carries only six rail labels, because movements 2, 3 and 4 are *all* labelled **How it
  answers** — one label, three movements, one answer told in three steps. So the rail is a map of
  the argument's parts rather than a count of its movements, and a row stays inked while its
  movements run; the reader who is on movement 3 still sees **How it answers** current, which is
  the truth about where they are. An earlier draft of the bullet above called these rows "the
  page's **eight movements**", which would have drawn three rows carrying the same label. The
  full-page mockup below settled it — six is right — and it is worth recording that prose carried
  that sentence through several revisions while a wireframe killed it in one.
- **Centre column 594px**, `--paper`, **left-aligned, ragged right**. Nothing centred except
  the question bubble, which the app right-aligns at roughly three-quarters of the column with
  a ~17px right inset (§4) — that is the app's own quirk and the replica keeps it.
- **Right rail 185px — the product, unaltered.** The app's real Notes rail: `Filter notes...`,
  **ten real note titles** from the captured run, `New note` at the foot, every string taken
  from the capture. It is not a decorative panel and it is not the witness — **the witness is
  the popover**, drawn open over the answer and anchored to the citation it belongs to, which
  is how the app draws it. *The Metonic cycle* sits fourth in that list, on screen without
  scrolling, and it is the same cycle the hero's answer opens with — so the notebook is proved
  in the first screen rather than claimed in the sixth.

**One detail of the real window worth keeping, because it is not a default.** The two rail
headers **mirror each other**: `Library` sits left with its controls at the right edge, `Notes`
sits **right** with its controls at the left edge. Each panel's title faces outward, each
panel's controls face the centre. A site that put both titles on the left would look tidier and
would be wrong.

**The answer's own typography is the app's, and it is a real feature.** Each cycle opens with a
**bold run-in heading** — `The Metonic cycle`, `The Callippic cycle`, `The Saros cycle` — and
then the sentence continues in regular weight on the same line. That is how the product
structures a multi-part answer, it is visible in the capture, and the replica keeps it (§4).

**The card in that wireframe is the verified state**: source title, then **the quoted passage
it matched**, and **no verdict word** — because the app prints none. The coral
*"Unverified — check the source."* replaces the passage when the citation was fitted by the
fallback citer (§5 movement 3). Both states are real and measured; the hero uses the verified
one because that is what this run actually produced.

**The popover cannot be shipped as a crop.** All four captures of it were taken mid-fade — the
answer text bleeds visibly through the card — so it is rebuilt in DOM, and those captures are
the spec.

**The hero is built in DOM, not shipped as an image.** The answer surface, the question
bubble, the citation marks, the Notes rail and the witness popover are real elements, so they are selectable,
searchable, translatable and readable by a screen reader — and the page's heaviest image
disappears. That carries an obligation in the other direction: **the DOM surface must match
the app's measured metrics exactly** (§1, §3, §4), because a replica that is handsomer than
the product is a small deception. Hairlines at `--rule`, radius 0/4/8, `--fill` for the
bubble, spacing from the app's own rhythm. Where the app is imperfect, the replica is
imperfect the same way. **One exception, and it is measured: the Black theme has no column
hairlines at all** — the hero's window separates its three columns with a ground shift, and
drawing `--rule` there would be the replica inventing a detail (§1, §3).

**Radius rule — radius is functional, not a style.** `0` for the reading column and for any
product window (the app's window is square-cornered). `4px` for the witness popover. `8px` for
the two things the app rounds at 8: the question bubble and, on the site, the CTA button.
**Never 16px+.** No card kit, no uniform radius. Note there is **no composer field** on the
page — an input that cannot be typed into is the same lie as a button that does nothing (§0),
so the hero shows the question as a *bubble*, which is what the app renders after you ask.

**One shadow, and only one.** The app separates surfaces with hairlines, not elevation, and the
page follows it: one hairline colour, `--rule`, everywhere — **with a single named exception**,
the soft shadow under the app window in movement 1 *(Thoria pre-approved, 2026-09-18)*. The
window is the page's one object and everything else is a document; §7 carries the reasoning and
the lighter build drops it.

### Mobile and tablet (<1080px) — the same page, deliberately lighter

**Two builds of one page, and the difference is *declared*, not scripted** *(Thoria, 2026-09-18:
the desktop page is editorial, and it "changes into a lower computing required webpage whenever
we detect it's on phone or a tablet"*). The switch is made entirely by media queries and
`<picture>` sources — `@media (max-width: 1080px)`, `@media (pointer: coarse)`, and `media`
attributes on the image sources. **No detection script, no user-agent sniffing**, so principle 2
survives whole. That matters, because the obvious way to build "detect the device" is a
JavaScript branch, and this page has spent its entire design budget on not having one.

**What the lighter build drops**, each as one declaration:

- **The ground texture** (§7) — off, flat `--paper`. This is the largest runtime saving on the
  page, because a blend-mode texture is the one thing here a weak GPU genuinely pays for.
- **The drawn figure stays** (§7), and it is worth saying why, because the first draft of this
  list dropped it alongside the texture. The plate is static inline SVG drawn in `--rule` with
  no filter, no blend and no animation — ~694 bytes gzipped, no request, and a phone
  rasterises it as cheaply as it rasterises a table rule. Dropping it would also cost the page
  its argument on exactly the devices that read it last: "Where it stops" is the honesty
  section, and the ring is that section's evidence. *Same argument* is a claim this list has to
  keep. The only adaptation is geometric — the plate scales so its interior stays wider than
  the measure and bleeds past the 24px gutters, clipped by the section, which is how a ground
  behaves anyway.
- **The 2× images** — the `<picture>` set resolves to 1× only.
- **The closing movement's blend and blur layers** — replaced with flat teal.
- **Large display settings** — the wordmark stays (1.9 KB, and it is the identity), but type is
  re-measured so the page never ships glyph sizes the phone will not render.

Everything else stays. **A weaker device gets a plainer page, not a different page** — same
words, same order, same argument. That is also the honest reading of the reference set: four of
those five ship 2–13.8 MB and none of them degrades at all, which is the one place this page can
beat them without spending anything.

The layout consequences, unchanged from draft 2:

- The three columns become one, 24px gutters, measure still capped. **No sticky bar, no
  slide-up sheet, nothing to open** — a drawer would reintroduce exactly the interaction the
  page gave up, and the static decision applies here too.
- The witness popover **stops floating and becomes a block directly under the citation it
  belongs to**, `4px`, on `--chrome`. This is what the app already does when its rail is too
  narrow, and it reads better than a drawer because the source stays with the claim.
- The Notes rail is **not reproduced**. It is a panel for holding many notes, and on a phone
  one note — the one the answer is about — is the whole point. Its content survives as the
  note quoted in movement 6.
- The left rail's section list is **not reproduced**. It is navigation, and on a phone the
  page's own length is the navigation. The wordmark and the repo link move into the close.
- Figures are cropped **once**, to a width that survives 360px. No second mobile variant of
  each image — see §7.

### The whole page, in seven frames

**The wireframe at the top of this section is the hero at working size. This is the page at the
only scale that settles anything: all of it, in order.** Frames A–F run the whole document —
so the rail's six rows, the switch from three columns to one, the ground changes, the plate and
the close can be checked against §1, §5 and §6 without holding the document in your head — and
G is the lighter build. **The left margin names the ground:** `L` is `--paper`, `B` the app's
Black window, `T` the og-card's teal. **The glyph legend above governs these frames too**, and
so does its convention: **the frames draw the app as the app is**, and where the site drops
something the app has — the `Thoughts` chevron, the expand/collapse pair — the margin or the
caption says so, exactly as that legend does.

They were drawn *from* §1, §2, §3, §5 and §6 rather than invented, and they earned their place
by finding the two §3 faults corrected above — the "eight movements" line, which would have
drawn three rows carrying one label, and the stray `·` in a slot where the page draws nothing.
Both had survived several revisions, because prose never puts two claims side by side and a
wireframe does it in one line.

**A · the page skeleton** — the whole site is the app's three columns

```
              ├──── 180 ────┼────────── 594 ──────────┼──── 185 ────┤
              ┌─────────────┬──────────────────────────┬─────────────┐
              │   Library   │      reading column      │    Notes    │
              │    rail     │  66ch max, left-aligned  │    rail     │
              │  --chrome   │         --paper          │  --chrome   │
              └─────────────┴──────────────────────────┴─────────────┘
              └────────────────────── 959 ──────────────────────────┘
```

Because the two rails are near-equal — **180 vs 185**, measured — emptying them for movements
2–8 leaves a nearly symmetric 594px measure with a 5px asymmetry inherited from the app. The
page reads as a centred book column that happens to be the product's centre column.

**B · movement 1 — What it is** · the only movement with rails full of content

```
L ┌──────────────┬──────────────────────────────────────────┬─────────────┐
L │ Library   ‹ ›│                                          │‹ ›      Notes│
L │ ─────────────│                                          │─────────────│
L │ ▸What it is  │        ┌────────────────────────────┐    │Filter notes…│
L │ How it answers│       │ Tell me about the cycles.  │    │             │
L │ Where it stops│       └────────────────────────────┘    │ancient astro…│
L │ On your machine│                                         │The National…│
L │ ἵστωρ         │  ▾ Thoughts                              │The Saros cyc…│
L │ Questions    │  The Antikythera mechanism                │The Metonic c…│ ← same
L │              │  incorporated several key                 │X-ray data fr…│   cycle as
L │ ─────────────│  astronomical cycles:                     │Fragment C of…│   the answer
L │ [Read the    │                                           │Reconstructio…│
L │  source]     │  **The Metonic cycle** is an              │Antikythera m…│
L │              │  astronomical period of 19                │Antikythera w…│
L │              │  tropical years, almost exactly           │Decoding Anti…│
L │              │  equal to 235 synodic lunar         ⁴ ───┐│─────────────│
L │              │  months or 6,940 days.                   ││▤ New note   │
L │              │                                 ┌────────┘│             │
L │              │   ┌─────────────────────────────┴─────────┐            │
L │              │   │ Decoding Antikythera mechanism        │            │
L │              │   │ │ "s lunar theory, replicating the Moon"│           │
L │              │   └───────────────────────────────────────┘            │
L │              │                                          │             │
L │ --chrome    │             --paper                      │  --chrome   │
L └──────────────┴──────────────────────────────────────────┴─────────────┘
   ↑ h1 above this, Didot 68px: "It shows you what it saw."         ↑ ONE soft
   ↑ lede, Inter 20px: a hundred pages, one question                shadow, here
```

**The window is Black, not light** — `#0A0A0A` rails, `#0B0C0F` centre, `#10141B` bubble,
`#E5E8EE` text — and it **draws no column hairlines**: the whole separation is a hue shift
(R+1, G+2, B+5), so the replica must not draw the two rules a light-theme wireframe would want.
The `⁴` is an azure numeral. The card is the **verified** state — title, quoted passage, and no
verdict word, because the app prints none (§5 movement 1).

**C · movements 2–4 — How it answers** · one column, rails empty

```
L ┌──────────────┬──────────────────────────────────────────┬─────────────┐
L │              │                                          │             │
L │              │  The gate, in plain words.                │             │
L │              │  ─────────────────────────                │             │
L │              │  Before answering, it decides whether     │             │
L │              │  the documents you already gave it        │             │
L │              │  settle the question. If they do, it      │             │
L │              │  never goes online.                       │             │
L │              │                                           │             │
L │              │  ┌────────────────────┬──────────────────┐│             │
L │              │  │ band=Direct        │ band=Research    ││  ← --fill   │
L │              │  │ Local library      │ Explicit research││    --t-xs   │
L │              │  │ already answers    │ intent detected  ││             │
L │              │  │ this question →    │ → bypass gate    ││             │
L │              │  │ skip gate + web    │ → 3 queries      ││             │
L │              │  │ top=0.0364 →       │ Read en.wikipedia││             │
L │              │  │ widening top_k 4→8 │ Read nature.com  ││             │
L │              │  └────────────────────┴──────────────────┘│             │
L │              │  1 decide → 2 retrieve → 3 answer → 4 cite│             │
L │              │                                           │             │
L │              │  ── movement 3: the witness ──            │             │
L │              │  The claim → the source → and, only       │             │
L │              │  sometimes, a verdict.                    │             │
L │              │                                           │             │
L │              │   ┌ verified ──────────────┐ ┌ unverified ┐│             │
L │              │   │ Decoding Antikythera   │ │ Decoding   ││             │
L │              │   │ │ "s lunar theory,     │ │ Antikythera││             │
L │              │   │ │  replicating the Moon"│ │            ││             │
L │              │   │                        │ │ Unverified ││  ← --coral- │
L │              │   │ (no verdict word)      │ │ — check    ││    ink,     │
L │              │   └────────────────────────┘ │ the source.││    + a rule │
L │              │                              └────────────┘│             │
L │              │  ── movement 4: watch it decide ──        │             │
L │              │  ┌─────────────────────────────────────┐  │             │
L │              │  │ ▾ Drafting the answer               │  │  ← app's     │
L │              │  │ I need to synthesize information…   │  │    chevron,  │
L │              │  │ Known facts from the context:       │  │    dropped   │
L │              │  │  • Built around 150–100 BC      More│  │    (§7 ex. 2)│
L │              │  │  • At least 30 interlocking gears   │  │             │
L │              │  └─────────────────────────────────────┘  │             │
L └──────────────┴──────────────────────────────────────────┴─────────────┘
```

The `band=` block is quoted product output and deliberately names **no search provider** — the
app's own fetch log names only the sites it read (§5 movement 2). **Numbered markers appear here
and nowhere else on the page**, because the pipeline genuinely is a sequence and nothing else in
the document is (§4).

**D · movement 5 — Where it stops** · the honesty section, and the plate

```
L ┌──────────────┬──────────────────────────────────────────┬─────────────┐
L │              │  Where it refuses / where it ends.        │             │
L │              │                                           │             │
L │              │  ┌─────────────────────────┬─────────────┐│             │
L │              │  │ Issue                   │ Status      ││             │
L │              │  ├─────────────────────────┼─────────────┤│             │
L │              │  │ Exact date of           │ Only a range││             │
L │              │  │ construction            │ 150–100 BC  ││             │
L │              │  │ Exact number of gears   │ "At least   ││             │
L │              │  │                         │ 30"         ││             │
L │              │  │ Exact number of holes   │ 354 or 355  ││             │
L │              │  │ in the calendar ring    │             ││             │
L │              │  │ Identity of the inventor│ Archimedes  ││             │
L │              │  │                         │ or Hipparchu││             │
L │              │  │ Whether it qualifies as │ The term is ││             │
L │              │  │ a "computer"            │ debated     ││             │
L │              │  └─────────────────────────┴─────────────┘│             │
L │              │                                           │             │
L │              │      · · · · · · · · · · · · · · ·        │  ← the plate │
L │              │    ·                             ·        │    (below the│
L │              │   ·   the copy sits inside the    ·       │    frame, in │
L │              │  ·    ring, so no line crosses     ·      │    --rule,   │
L │              │  ·    the beads. The difference    ·      │    one azure │
L │              │  ·    is one you cannot see.       ·      │    hole at   │
L │              │   ·        355 ● 12 o'clock       ·       │    12 o'clock│
L │              │    ·                             ·        │             │
L │              │      · · · · · · · · · · · · · ·          │             │
L └──────────────┴──────────────────────────────────────────┴─────────────┘
```

**The plate is a ground, not a diagram** (§7): its centre is pushed below the section so the
interior holds the copy and the 355 beads read as an engraved band. It is drawn entirely in
`--rule`, so it costs no more contrast than a table rule — and that is the same argument that
keeps it in the lighter build (§3, mobile).

**E · movements 6–8 — On your machine, ἵστωρ, Questions**

```
L ┌──────────────┬──────────────────────────────────────────┬─────────────┐
L │              │  Nothing leaves. What you write stays     │             │
L │              │  yours.                                   │             │
L │              │  ┌─────────────────────────────────────┐  │             │
L │              │  │ Settings › Research                 │  │  ← exhibit 9│
L │              │  │ Web research       [ ●———]          │  │    the one  │
L │              │  │ Inbox watching     ~/.istor/inbox   │  │    switch   │
L │              │  │ Depth              Dynamic          │  │             │
L │              │  │ Search backend     SearXNG ▾        │  │             │
L │              │  └─────────────────────────────────────┘  │             │
L │              │  No account and no key are required.      │             │
L │              │                                           │             │
L │              │  ┌ The Metonic cycle ─ 136 words ──────┐  │  ← a real   │
L │              │  │ "is an astronomical period of 19    │  │    note,    │
L │              │  │  tropical years, almost exactly     │  │    the same │
L │              │  │  equal to 235 synodic lunar months" │  │    one the  │
L │              │  └─────────────────────────────────────┘  │    answer   │
L │              │                                           │    opened   │
L │              │  ἵστωρ                                     │    with     │
L │              │  from *weyd-, "to see" — one who has      │             │
L │              │  seen, and therefore one who can be       │             │
L │              │  believed.                                │             │
L │              │                                           │             │
L │              │  Does anything leave my computer?         │             │
L │              │  What hardware do I need?                 │  ← plain    │
L │              │  Which models can it use?                 │    list,    │
L │              │  Does it work with no internet at all?    │    nothing  │
L │              │  Is it open source? When does it come     │    opens    │
L │              │  out? Who builds it?                      │             │
L └──────────────┴──────────────────────────────────────────┴─────────────┘
```

Three movements share one frame because they are short and they are where the rails stay empty
for good. **The FAQ is a plain list and not an accordion** (§5 movement 8) — nothing on this
page opens, and on a page whose audience came for the hardware answer, hiding the answers is the
one interaction that could not be justified.

**F · the close** · ground switches, no rail entry

```
T ┌────────────────────────────────────────────────────────────────────────┐
T │  hairline  rgb(255 255 255 / .12)                                      │
T │                                                                        │
T │                        ◉  the mark re-inks                              │
T │                            coral → azure                               │
T │                                                                        │
T │        ┌──────────────────────────────────────────────────┐            │
T │        │                 Read the source                  │            │
T │        └──────────────────────────────────────────────────┘            │
T │        §6: the same rectangle becomes [ Download for Windows ]         │
T │        on --azure-lift at launch — same box, no redesign.              │
T │                                                                        │
T │       ἵ  σ  τ  ω  ρ  .        ← --t-mark, 176px → viewport-width       │
T │                                live text, the wordmark subset, lh 0.9  │
T │  ────────────────────────────────────────────────────────────────────  │
T │   GitHub     Contact     Guides     Thoria    ← links only, no separators │
T └────────────────────────────────────────────────────────────────────────┘
```

*(`Guides` added 2026-09-18 — it is the one link from this page into the 75-page carried library,
which the footer otherwise never reaches. `Guides` → `/local-ai-vs-cloud-ai/`, and its `href` moves
to a library index if one is ever built; the label does not.)*

*(`Contact` and `Thoria` both resolve to **https://thoria.fyi/** — there is no email address on
disk, and the developer's site is where their contact details are published. Two entries pointing
at one destination is a wart in a four-item strip; the one-token fix is to **drop `Contact`**, since
the wordmark above already names them and the byline already links. Not taken — flagged 2026-09-18.)*

Teal is the og-card's own ground (`#0D1D20`→`#132E2F`), so the card a scraper fetches and the
page's last movement are the same colour (§7). The mark's re-inking is the page's **only**
motion, and it is a colour change rather than a transform, so it survives `prefers-reduced-
motion` without a variant.

**G · phone** — same words, same order, plainer

```
L ┌────────────────────────────┐      ▸ three columns become one, 24px gutters
L │  It shows you what it saw. │      ▸ ground grain dropped, flat --paper
L │  ─────────────────────────  │      ▸ 2× images resolve to 1×
L │  a hundred pages, one       │      ▸ blend + blur replaced with flat teal
L │  question…                  │      ▸ the single shadow dropped
L │                             │      ▸ left rail's section list NOT reproduced
L │  ┌─ the window, one column ─┐│      ▸ Notes rail NOT reproduced
L │  │ Tell me about the cycles.││      ▸ the plate STAYS — inline SVG, no cost
L │  └──────────────────────────┘│      ▸ witness popover becomes a BLOCK under
L │  The Metonic cycle is an     │        the citation it belongs to, 4px,
L │  astronomical period of 19   │        on --chrome
L │  …                           │
L └────────────────────────────┘
```

Everything in the right-hand column of that frame is a **drop already listed above**, in the
same order — the frame exists so the list can be seen as a page rather than read as six
declarations. **The plate is the one item that survives**, and it is the one the first draft of
that list got wrong.

---

## 4. Type roles in the chrome

The site uses the app's own components as its components. Concretely:

- **The question bubble** — `--fill`, 8px radius, Inter 17, **right-aligned with a ~17px right
  inset**, at roughly three-quarters of the column's width. This is a real DOM element, not an
  image. The measurement is from the 2× captures (`White/verifiedsource.png`, and `#10141B` on
  `#0A0A0A` in the Black one — **same geometry in both**): the bubble runs CSS 311→757
  inside a centre column of 180→774. A left-aligned bubble would match the rest of the page and
  would be wrong.
- **Bold run-in headings inside the answer** — `The Metonic cycle`, `The Callippic cycle`, `The
  Saros cycle`, `The Exeligmos cycle`, each bold and continuing on the same line in regular weight.
  This is the app's own device for a multi-part answer, and it is why the hero's answer reads as a
  list without any list markup. Replica keeps it; the site does not introduce numbered headings
  here. *(Corrected 2026-09-18: this list said three. `Black/verifiedsource.png` carries **four** —
  the answer's fifth paragraph is a second sub-dial, `The Exeligmos cycle`, before the closing
  sentence on the pin-and-slot gearing.)*
- **The witness popover's quote** — the passage sits behind a **left rule**, italic, inside
  quotes, under the source title in ink. The rule is the app's, measured in the same capture;
  it is the only place on the page where a vertical rule is not a column edge.
- **Citation marks** — superscript Inter 13, `--azure`, sitting on a `#E3EEF9` wash *(both
  measured)*. **Not buttons.** With nothing behind them a focusable control is a trap for
  keyboard users, so they are `<sup>` with the source named in visually-hidden text —
  *"source 4, Decoding Antikythera mechanism"*. The **one** citation the popover is anchored
  to gets the app's own active treatment: a filled `--azure` disc, white numeral. That is a
  static state, not a hover state, and it is what ties the card to the claim.
- **The Thoughts disclosure** — a `--rule` hairline above, Inter 15, with the app's amber dot
  and a chevron. **It does not open** — the page is static, so the chevron is dropped and the
  disclosure is printed **already expanded**, as DOM, in the section where it is the subject
  (§5, movement 4). A disclosure control that does nothing is worse than no control.
- **The verification verdict — and what it actually means.** The app runs **two models**, and
  the smaller one makes the fast calls: its **main job is the grounding gate** — deciding whether
  the library already settles the question, so the answering model never goes online (§5,
  movement 2) — and the other thing it does is fit citations the answering model dropped. The
  answering model writes the answer and usually cites as it goes; when it omits a citation, the
  cheap model retro-fits one, because waiting on a slow model after the answer is already on
  screen would cost more than a fitted citation. A citation it fitted is marked
  *"Unverified — check the source."* in coral — **so the word is a statement about provenance,
  not about support.** It says *which of two models put the number there.* The site must never
  paraphrase it as "the source doesn't back this claim": that is a different claim and it is not
  what the product does (§5, movement 3).
  Set in `--coral-ink` against a rule, never colour alone (§1).
- **Source status** — a 6px dot and nothing else. `#B35208` waiting, `#4BB581` ready. Every
  capture shows green only, so the site uses green only; a mixed state is a shot Thoria does
  not have and an invented one is a lie (§7).
- **Quoted product output** — the one block of raw machine lines (§5, movement 2). Monospace,
  `--t-xs`, `--fill`. It is quoted evidence, so it is exempt from the plain-language rule;
  the prose around it is not.

---

## 5. The page, section by section

Rail labels in brackets. **Eight movements, six rail labels, then a close with no rail entry** —
movements 2, 3 and 4 share the one label *How it answers*, so the rail is a map of the argument's
parts and not a counter of its movements (§3).

**The order is the argument:** what it does → how it answers (three movements) → where it
stops → on your machine → the name → your questions. Accuracy leads; privacy and the notebook
follow as consequences. Each movement is short.

**(What it is)** — **Opens in prose, for a knowledge worker.** h1 in Didot: *It shows you what
it saw.* One line of Inter lede, plain, about an ordinary day — a hundred pages to read and one
question, a draft to check, a ticket that has been answered before. **No product jargon:** not
"grounding gate", not "band", not "chunk". Plain words, then the demonstration.

Then the app's own window, built in DOM (§3), **in the app's Black theme** — Thoria's pick
(2026-09-18): the **Library rail** on the left, the answer
surface in the middle, the **Notes rail** on the right — `Filter notes...` and ten real note
titles — with the **witness popover drawn open** over the answer and anchored to the citation
it belongs to, in its verified state: title, quoted passage, no verdict word. **The hero
question is *"Tell me about the cycles."*** — the shortest question
in the whole capture set and the one the app answered best, opening on *"The Antikythera
mechanism incorporated several key astronomical cycles"* and then the Metonic cycle in its own
words. It is a question a researcher would actually type, and its answer walks straight into
the note already sitting in the Notes rail — *The Metonic cycle*, fourth row, visible without
scrolling.

The example is **Antikythera** — the reader has just been told about their own working day and
is now shown the tool doing something *hard*, with ten sources and a live scholarly dispute
between two of them. That is the proof, not the pitch. **No instruction line** — "click a
number" describes something that does not happen.

**The hero's card is the verified state** — source title, quoted passage, no verdict word —
because that is what this run actually produced. The coral line arrives in movement 3, where
the mechanism that produces it is explained, so the reader meets it *after* they can
understand it.

**And the card changes theme with the window.** Inside the hero it is the app's Black card
(`#10141B` on `#0A0A0A`); in movement 3, where both states are rebuilt on paper, they are the
light card. That is not inconsistency — it is two real themes, both captured, each used where it
belongs: the product's dark surfaces inside the product's window, the site's paper outside it.

Everything after this movement is a single reading column. The rails are empty ground from
here on; the window was the frame, not the spine.

**(How it answers)** — **The gate, in plain words.** The thing no competitor has: before
answering, it decides whether the documents you already gave it settle the question — and if
they do, **it never goes online.** That is the whole reason the product works with no network,
and it is the one mechanism worth explaining slowly.

**And the decision is made by the small model** — this is the fact that makes the gate make
sense, and it is new (§0). Istor runs two models; the smaller, heavily-instructed one is the
decision-maker, and the gate is its main job. So "it never goes online" is not a heavyweight
architecture refusing to fetch — it is a cheap model being asked a cheap question first, and
answering it fast. Say that in one sentence. It converts the gate from a claim about design into
a claim about cost, which is the version a reader believes.

Explain it plainly, then show the real lines. **Plain prose, quoted output** — the sentences
are mine and ordinary; the block is the product's and untouched:

```
band=Direct                                band=Research
Local library already answers this         Explicit research intent detected
question → skip gate + web research        → bypass gate → 3 queries
top=0.0364 → widening top_k 4 → 8          Read en.wikipedia.org — Antikythera Mechanism
Retrieved 6 chunks from library            Read en.wikipedia.org — Antikythera Wreck
                                           Read nature.com
                                           Read arxiv.org — 2403
```

**Both columns are quotations, and they come from two different real surfaces.** The
`band=` decision lines are verbatim from a real run and keep the log's own vocabulary —
`band`, `top_k`, `chunks` — because a quotation that has been tidied is no longer evidence.
The right column is the fetch log from the app's own **`Thoughts`** panel
(`White/FetchingPages.png`, §7 exhibit 3), not from a terminal, so it is what a user actually
sees while the answer is being built.

Two honesties, both of which belong on the page as a caption rather than a disclaimer. The
**lines** are real; the **side-by-side arrangement is mine** — I laid two runs next to each
other to compare them, and saying so costs one clause. And the block **deliberately names no
search provider**: the app's live fetch log names only the sites it read, so the page does too,
and the question of which backend ships (§10.4) stops being load-bearing for this exhibit.
Do not restore a provider name to the block; if one is wanted in copy, confirm it first.

The pipeline **is** a sequence, so this is the one place where numbered markers are honest —
`1 decide → 2 retrieve → 3 answer → 4 cite`. Nowhere else.

**(How it answers, continued)** — **The witness.** Explain the footnote. Istor writes
`[^ist-N]` into the note; the app resolves it to a passage in a source you own or a page it
actually fetched — so a number in the answer is never attached to a source that isn't there.
State the two failures it removes, in the product's words: it will not invent a fact, and it
will not tell you something doesn't exist just because it falls outside a training cutoff.

The app already names this structure, and the section follows it: **the claim → the source →
and, only sometimes, a verdict.** Measured across `White/verifiedsource.png`,
`White/verifiedsource2.png` and `Black/verifiedsource.png`: a citation mark is an azure
underlined numeral, and the card is a plain popover floating over the answer, anchored to that
mark, carrying the **source title** in ink and then either

- **the quoted passage it matched** — *"Lunar theory, replicating the Moon"*, in italic inside
  quotes, and **no verdict word at all**; or
- the coral line **"Unverified — check the source."** and **no passage whatsoever.**

**And here is the reason, which is the strongest single fact in the product.** Istor runs
**two models**, with a division of labour rather than a hierarchy — and the smaller one is the
one that decides things. Thoria, 2026-09-18, first on the decision role:

> *"1 is the cheaper model which is heavily instructed. It makes decisions quickly. Like when
> web search is open, it decides if the local sources is enough, if yes it just uses local
> sources. That's not the only thing it does, but it's the main one."*

and then on the citation consequence:

> *"Since we are working with smaller models, sometimes the accurate model doesn't put
> citations in it's response. When this happens, a cheaper model comes in and find citations
> quickly to not make response time slower whilst still keeping the source. Since the citation
> was made by the cheaper model we put 'unverified'. Though it's still good."*

So the small model is the **triage model**, and the gate is its headline job (§5 movement 2):
it decides whether the library already answers the question, and that decision is why the
product can work with no network. The citation path is the same model doing the same kind of
work — the answering model writes the answer and usually cites as it goes; when it drops a
citation, the small model retro-fits one, a deliberate latency trade, since the answer is
already printed and waiting on a slow model would cost more than a fitted citation. A citation
it fitted is marked unverified. **The word is about provenance, not about support: it tells you
which of two models put the number there.**

**That is why this belongs on the page and not buried.** The interface already says *Unverified*
and declines to explain it; the explanation is a genuine, unusual, checkable design decision.
One cheap model is asked to be decisive so a better one can be slow — that single sentence is
more interesting than anything a feature list could say, and it is the only thing on this page a
competitor cannot copy without rebuilding their pipeline.

**This must not be paraphrased as "the source doesn't back the claim."** That is a different
statement, it is not what the product does, and writing it would be the exact failure this
page is built to avoid. The honest sentence is stranger and better: *the app tells you which of
its two models wrote the citation, and marks the one it isn't sure of.* Thoria's own gloss —
*"Though it's still good"* — is the correct tone: a disclosure, not an apology.

The card's anatomy makes this visible without a word of explanation, which is why it is worth
setting on the page at size. **The unverified card shows no quoted passage** — the quote is
replaced by the instruction to go and look. That is the observable difference, and it is stated
as measured. *(Why the passage is absent is my inference, not Thoria's statement — do not
publish a causal claim about it.)*

**~~And the gap that produces the whole mechanic is on screen too.~~ Cut — Thoria, 2026-09-18:
*"Nope, not needed."*** `White/Question1.png` answers *"How did the Antikythera mechanism
predict eclipses?"* and its first paragraph ends **`"and its directional orientation ."`** — a
space, a full stop, and no citation numeral, which is the answering model having dropped one.
It stays in this document as **evidence for the copy**, and it does not become an exhibit. The
hero is unaffected: it is a different run, and its opening line carries no citation mark simply
because the app's intro sentence never does.

Contrast: the app's coral ink measures 3.45:1 on white and fails AA at small size, so the site
uses **`--coral-ink` `#C7292A`**, 5.56:1, against a rule — colour is never the only signal. Do
not copy the app's value verbatim.

This section is mostly *one paragraph of the product's real output, set large*, with the
footnotes working and **both card states** rebuilt in DOM beneath it — verified first, unverified
second, the same source title swapped out (§3). The mechanism is legible by looking rather than
by clicking. This is the page's one bold moment, so it is the one place where the replica has to
be exact.

**(How it answers, continued)** — **You can watch it decide.** The exhibit is the app's own
**`Thoughts` disclosure**, printed expanded — no chevron, nothing to open (§4). I had this as
the terminal debug screen; the disclosure is strictly better and I changed it. Measured in
`White/Question1.png` and `Black/answering.png`, it reads **"Drafting the answer"**, then the
model's own reasoning — *"I need to synthesize information from the provided context,
distinguishing between established facts and areas of ongoing debate."* — then a headed list,
**"Known facts from the context:"**, then each retrieved chunk with a `More` expansion and its
source number.

Three reasons it wins over the terminal: it is the same evidence in the product's own
surface, so the reader recognises it rather than being shown a developer tool; it needs no
developer vocabulary explained; and it is captured in **both** themes. The gate block in
movement 2 keeps the one thing the terminal did uniquely — proof of the *decisions*, in the
log's own words.

Two rules for it:

- **Show the output, don't brand it.** The terminal block is the product's own log, quoted,
  with no tooling named around it. **`powercell` is not a component and never was** — it entered
  this document through a misspelling and then propagated through several sessions; Thoria's own
  account, 2026-09-18: *"I think I misspelled powercell which spiraled into a huge communication
  error between us."* What the dev debug screen actually is: the app booted from a shell, printing
  to it. **Name nothing about the shell.** *Taori*, on the other hand, is real and is what Istor
  is built with — **Rust and Taori may be named in the FAQ** if the reader asks what it's made
  of, which is the right place for it: an answer to a question, not a badge on the hero.
- **It is one of the two places where the site looks technical, so it must be small.** Set it
  at `--t-xs` in a `--fill` block, in a column narrower than the reading measure. Its job is
  to be *available as evidence*, not to be read line by line.

**(Where it stops)** — The honesty section, and the most differentiating one on the page.
Every reference in the set overclaims; this one says plainly where the tool ends. It covers
two different things and does not blur them:

- *Where it refuses* — it will not guess. If your sources don't cover it, it says so. That
  refusal is the feature, not a limitation.
- *Where it genuinely ends* — it is not a frontier model, and it will not out-reason one. It
  needs sources. Local means your machine's specs are part of the deal.

**The product has already written this section, and I should not rewrite it.** In
`White/Question2.png` the answer ends with a table headed **"What Is Still Disputed"**, two
columns, **Issue | Status**, twelve rows:

| Issue | Status |
|---|---|
| Exact date of construction | Only a range (150–100 BC) is known |
| Exact number of gears | "At least 30" — the exact count is uncertain |
| Exact number of holes in the calendar ring | 354 or 355 (354 is far more probable than 360) |
| Identity of the inventor | Archimedes or Hipparchus — both are candidates |
| Whether it qualifies as a "computer" *(+ calculator, clock, calendar, planetary calculator, solar calendar, lunar calendar, solar-lunar calendar)* | The term is debated |

Set that table as a **table**, not as a screenshot of one. It is the single most on-message
artefact in the whole product: an AI tool printing the list of things it does not know, and
refusing to pick a winner between its own sources. Nothing in the reference set does this.

*One fidelity note, because the hero has moved.* This table is transcribed from a different
run than the hero's — the calendar-ring hole-count question, not the cycles question. Since it
ships as live text with no window around it and no question above it, nothing is misrepresented;
but the section should not imply it is the same conversation. One clause says so, or the
question is simply not shown.

This section is also where the trust claim gets its proof: the repo is public, so "no
telemetry" is checkable rather than asserted.

**(On your machine)** — Two things, both true and neither oversold: **nothing leaves, and what
you write stays yours.** This is the movement where privacy and the notebook arrive — after
the accuracy claim, as consequences of it rather than as separate pitches.

*The proof is a settings dialog.* `Black/settingsresearch.png` shows Settings → Research:
*Web research — Allow outbound network fetches* as a **toggle**, *Inbox watching — Auto-import
new files from `~/.istor/inbox`*, *Depth = Dynamic*, and *Search backend — "Where research
finds web results — a SearXNG backend without a URL falls back to the keyless scrape chain"*.

**Corrected 2026-09-18: the dialog offers three backends and the capture shows one of them.**
Thoria: *"We use both SearXNG, Brave and Scraping (keyless). The default is SearXNG."* The
capture happens to have **Scrape** selected, which is why this paragraph used to say that was
the default — **it is not.** The crop still ships, because a switch is the argument and the
selection is real state; the caption simply must not call it the default, and **no provider is
named in copy** either way.

**And the claim Thoria authorised is narrower than "keyless", which makes it honest.** *"You can
claim it works without keys. It supports the no-telemetry claim."* Brave is the backend that
*would* take a key, so the claim has to be about what is **required** and not about what is
present: **no account and no key are required** — the default needs neither, and the keyless
scrape chain is what happens when there is no SearXNG instance to point at. Say it that way.
Do not write "no key is ever used", which Brave falsifies. This is the rare privacy claim that
is a control rather than a promise: nothing leaves until the user flips one switch, and when it
does leave there is no account and no service in the path. *Four words still do the work:
"keyless, no service."* Crop the dialog; it is the one piece of app chrome on the page worth
showing as chrome, because a switch is the argument.

*The notebook gets one exhibit.* A note, transcribed from the capture — measured, the note
titled **The Metonic cycle** at 136 words, real prose in the product's own hand. **This is the
same cycle the hero's answer opens with**, so the section can say the true and unusual thing:
the note the reader is looking at is the note the tool wrote while answering the question in
movement 1. That is what makes "notebook" a fact rather than a word, and it is the exhibit that
speaks most directly to a knowledge worker: the tool keeps what they worked out. Pair it with
the **Notes rail the reader already met in the hero** — so
the notebook claim is not being made twice, it is being *paid off*: the note in movement 1's
answer is the note in movement 6's exhibit. Beside it, the tight crop of the real **Library
rail** and its green status dots (exhibit 8) — the two sides of the product in one movement,
both real state, both real colour, and the rail crop is the only image on the page that shows
a rail as a rail rather than as the site's own navigation.

**Two words carry this section, and one sentence makes them concrete** *(confirmed by Thoria,
2026-09-18, and it is on screen)*. **Sources are what the model reads; notes are what you
write.** Sources are the library the gate decides on; notes are the reader's own prose, and they
are editable — as are sources. And the bridge between them is a button: **two icon controls sit
under every answer** — a copy glyph and a note glyph — and the second one **pulls the answer
straight into a note**. Measured in `White/verifiedsource.png` and `Black/verifiedsource.png`,
directly under the cycles answer. That is the sentence: *the answer becomes a note without
anyone retyping it.* It is the smallest fact in the product and the one a researcher will
recognise as the reason to switch, so it is worth one line and one small crop rather than a
paragraph.

*Then the requirement, plainly.* **It does not ship with a model, and that is the honest shape
of it** *(Thoria, 2026-09-18)*. What Istor requires is **Ollama or llama.cpp** already on the
machine. If Ollama is there it will recommend one; if that model isn't present, or the reader
would rather use another, they choose it themselves in Settings.

So the sentence leads in plain words — *it runs a small model on your own graphics card, and
you choose which* — and **no model name appears anywhere on the page** *(Thoria, 2026-09-18:
"Doesn't matter — copy stays generic")*. Three reasons, and any one would be enough: nothing
ships, so there is no default to name; a recommended model changes as better small models
appear, and a page that prints one goes stale on a schedule nobody controls; and an identifier
would be the only proper noun on the page that the reader cannot check against the product in
front of them. **The FAQ's "Which models can it use?" answers the same way** — the shape of it
is *a small model on your own graphics card, and you choose which* — so the page never prints a
name it cannot stand behind. The earlier draft's framing was wrong twice over: it presented a
fixed shipping default when there is none, and it printed an identifier the page has no reason
to carry.

**And "you choose" is a stronger claim than a default would be**, which is why it should be said
rather than glossed: a bundled model is a decision made *for* the reader, a model picker is a
decision handed *to* them — and on a page whose whole argument is that nothing happens on the
user's behalf without their knowing, that distinction is worth one clause. It also puts two
requirements on the page honestly: Istor needs a runtime the reader may not have, and the page
should say so rather than let them find out at the installer. **No RAM or VRAM figure — and
that is a decision, not an omission** *(Thoria, 2026-09-18)*: the page publishes no minimum.
The reason is the one already in this paragraph — **the requirement is a function of the model
the reader picks**, so any floor we printed would be a floor for a model they have not chosen
yet. §10.1 is closed on that reasoning rather than left waiting for a number.

**(ἵστωρ)** — The etymology, set as a real piece of writing rather than a trivia card. The
word at display size in the wordmark subset. *ἵστωρ*, from **\*weyd-**, "to see" — one who
has seen, and therefore one who can be believed. The mark is an eye on a page; the product
shows you what it saw. Three or four sentences, then stop. No "our name means…" framing.

**(Questions)** — The FAQ, **as a plain list rather than an accordion.** Same reason as
everything else: nothing on this page opens, and an accordion hides precisely the answers this
audience came for. Someone who wants the hardware answer should be able to read it, not
discover it. Questions worth asking: *Does anything leave my computer? / What hardware do I
need? / Which models can it use? / Does it work with no internet at all? / Is it open source?
/ When does it come out? / Who builds it?* Answers in **"we"**; name **Thoria** only where a
person is meant. **The Windows-only fact lives here**, plainly, rather than in the opening
(§6).

**And "What hardware do I need?" keeps its place, and gets a reason instead of a number.** The
page publishes no minimum *(Thoria, 2026-09-18)*, so the answer is the model picker: a small
model runs on modest hardware and a large one wants more, and which one you run is yours to
choose — so there is no single floor to print. That is a better answer than a floor would be,
because it is true for every reader and cannot go stale when the app changes. **It also keeps
the promise this page makes everywhere else:** a number we cannot stand behind is exactly what
§8's principle 8 says not to write.

**(close, no rail entry)** — Ground switches to the og-card's teal, hairlines become
`rgb(255 255 255 / .12)`, the icon re-inks to its dark contract (azure eye), the CTA slot is
at full size, and the giant **ἵστωρ.** closes the page as live text — the one convention kept
from the genre, because the asset is built for it. Then a thin footer strip: links only.

---

## 6. The CTA slot

There is no installer and no GitHub presence yet, so the CTA must be a **slot**: fixed
geometry, fixed ground, one object behind it. Only the contents change.

```js
{ state: 'prelaunch' | 'live',
  platforms: [{ id, label, url, available }] }
```

- **`prelaunch`** — no dead button, ever. The slot holds a plain sentence and **one real
  action available today: the public repo** (`github.com/ThoriaDevelopment/Istor`) — read it,
  star it, build it, under the label **`[Read the source]`**, which is the same label the hero's
  rail foot carries for the same action (§3). **No email capture, deliberately.** An email list puts a third-party
  service directly in the path of a product whose entire claim is that nothing leaves your
  machine; the page would be contradicting itself in its own call to action, and a visitor who
  noticed would be right to stop believing the rest. The repo is also the stronger proof —
  "no telemetry" stops being an assertion when the code is readable. Weaker as a funnel,
  stronger as evidence, and the evidence is the thing this page is selling.
- **`live`** — the same rectangle becomes `[ Download for Windows ]` on `--azure-lift` with
  **`--ink` text** (6.8:1 — measured; white on azure-lift is 2.6:1 and fails), with a smaller
  line beneath reading `Windows, for now. Linux and macOS after.` Platform-aware via UA, but it
  always *lists* all platforms rather than hiding them.

Same box, same ground, same rhythm, same position in the rail. No redesign at launch. The
platform line — `Windows installer first; Linux and macOS after` — appears here and in the
FAQ, and **not** in the opening, where it would lead a page about an offline AI notebook with
an OS compatibility note.

---

## 7. Images and the weight budget

**Rule: the app ships as an image only where its *form* is the argument; everywhere else it
ships as text.** A popover's edges, a rail's alignment, a toggle — those are pixels. An answer,
a fetch log, a table, a note — those are words, and words ship as DOM: they cost nothing, they
are selectable and searchable and readable by a screen reader, and they cannot be blurry on a
cheap phone. The CLI's own output is text for the same reason.

**The 35 captures in `Assets/Istor Screenshots/` are source material, not figures.** Thoria
confirmed this on 2026-09-18: they are uncropped raw screenshots, and each exhibit below is a
**crop I make and polish**. Two consequences worth stating, because both were raised as
objections and both are now moot:

- **Framing drift does not matter.** The captures were taken with the panels at different
  widths (the centre/right-rail hairline lands anywhere from CSS 676 to 797; the status-dot
  column at CSS 138 or 208) and at heights varying 1012–1018 px. Nothing ships uncropped, so
  nothing can jump.
- **Theme gaps do not block a section.** No single theme covers every screen — White has the
  whole Notes-fullscreen trio plus appearance and models settings, Black has the whole
  Sources-fullscreen trio plus data and research settings. A crop is one panel, so a section
  can take White for one exhibit and Black for another. **In the event, all three bitmaps are
  Black**, and that is now a decision rather than an accident: the hero renders in the app's
  Black theme (§1, §3), so the exhibits match the window. The light theme is not absent from
  the page — it is what the *site itself* is made of.

**The rule that decides which is which.** A capture becomes a **bitmap** only where *form* is
the argument — a popover's edges, a rail's alignment, a switch. Where *words* are the argument,
the capture is the **source of the text**, and the text ships as live DOM: selectable,
searchable, readable by a screen reader, and immune to crop truncation. That rule is what
makes the hero possible at all (§3), and it is why the page carries **three bitmaps, not ten**.

**And the verified-source captures removed one.** Draft 2 had a fourth bitmap for the Notes
rail. The hero now builds that rail in DOM, from the same run, so a second picture of it would
be the same object twice — and worse, a *still* of a rail the page already renders live. It is
gone, the notebook section keeps the note as text, and the budget drops with it.

| # | | Exhibit | Section | Source file | Crop / region | Polish |
|---|---|---|---|---|---|---|
| 1 | T | The answer surface — question bubble, `Thoughts`, the cycles answer with its bold run-in headings, citation marks, **and both rails** | What it is (hero) | `Black/verifiedsource.png` | whole client area, x 0–1918, y 30–1012 | **not a figure.** Rebuilt in DOM at the app's metrics **in the Black theme** (§1, §3); this capture is the spec and the source of every word. `White/verifiedsource.png` is the same run and remains the spec for anything the Black capture renders ambiguously |
| 2 | T | `Thoughts` expanded — "Drafting the answer" + "Known facts from the context:" | Watch it decide | `Black/answering.png` | centre column, x 700–1620, y 540–1012 | printed already expanded; chevron dropped; **the amber disclosure dot is kept** (cleanup 4) |
| 3 | T | The Research band from an empty library — fetch log incl. the failed `nature.com` fetch | Watch it decide | `White/FetchingPages.png` | centre column, x 700–1620, y 60–800 | transcribe the log; the `0 sources` pill and "No sources yet." are the claim and stay |
| 4 | T | What Is Still Disputed (Issue \| Status, 12 rows) | Where it stops | `White/Question2.png` | the table, x 780–1560, y 380–900 | **a real `<table>`**, 5 rows shown |
| 5 | T | The Metonic cycle note (136 words) | On your machine | `White/viewingsource-editingnotes.png` | the note panel | live prose. If the capture clips the note, this is text — set it in full |
| 6 | T | **The witness card, both states** — verified: title + quoted passage; unverified: title + **"Unverified — check the source."** | How it answers | `White/verifiedsource.png` (verified); `White/Question1.png` + `Black/verifiedsource.png` (unverified) | card only in each, ~x 840–1340, y 640–800 | **DOM, and it has to be**, because the popover is mid-fade in all four captures — the answer text bleeds through it. Those four are the spec. The verdict line is `--coral-ink` against a rule, never colour alone |
| 7 | B | The Viewer — a source's own text, verbatim, under its title | How it answers | `Black/Sourcesfullscreenview.png` | the panel, x 20–1900, y 60–900 | Black theme; pairs against exhibit 6 and doubles as the close's image. A bitmap because the claim is **chrome and form** — a document panel, in the app's own typography, holding raw markdown with its `#` intact. **The Viewer does have tabs — Thoria confirmed it 2026-09-18 — but no capture shows a tab row, so the exhibit shows the state that is captured** (title, pencil, `✕`, then the source's raw markdown) **and the row is not invented.** The old `Content` / `Fetched text` label is from the replaced `UnCropped/` set and must not be used (§10.10) |
| 8 | B | Library rail with source rows and green status dots | On your machine | `Black/verifiedsource.png` | rail only, x 0–360, y 60–1000 | **Black, same run and same theme as the hero** — so the one place the site *replaces* the rail (it becomes navigation, §3) can be shown against the real thing rather than described. Ten rows, `Add source` at the foot, green `#4BB581` dots only |
| 9 | B | Settings → Research | On your machine | `Black/settingsresearch.png` | the dialog, x 562–1400, y 205–801 | the one place OS/app chrome earns its keep — a switch is the argument. Black, and the close reuses it |

Plus the close: no bitmap. The dark movement reuses **exhibit 7 or 9** (both already Black), and
the giant **ἵστωρ.** is live text from the wordmark subset.

**Cleanup, before any of these go on the site:**

1. **Crop to the client area.** No desktop, no caption buttons, no rounded window shadow —
   except exhibit 9, where the dialog frame is the point. *This governs the **bitmaps'** edges
   only.* It does not forbid the page's own single hero shadow, which is separate and taken —
   see the shadow subsection at the end of this section, where I misread this rule as a
   conflict.
2. **Never ship a word as pixels if the word is the argument.** Exhibits 1–6 are text; they
   ship as DOM. That removes the truncation artefacts in the raw captures entirely — the
   Notes rail's `The National Archaeol…` never appears, because the title is typed, not cropped.
   Exhibit 8 is the one place a truncated app string legitimately ships, and it ships as
   `alt` text in full: *The National Archaeological Museum in Athens*.
3. **Never put two captures of different widths side by side.** If two figures must sit
   together, both are re-cropped to the same column width first.
4. **The two ambers are not the same amber.** *Source-status* dots are uniformly green
   (`#4BB581`, verified identical in both themes) — no capture shows an amber source, and the
   amber→green indexing transition exists nowhere in the set, so **exhibit 8 shows green and
   only green.** Do not invent a mixed-dot rail; mixed dots read as a bug. But the dot on the
   **`Thoughts` disclosure is a different component's marker**, it is amber in every capture
   that shows a disclosure, and it is reproduced (exhibit 2, §4). Keeping one and dropping the
   other is not inconsistency — it is two glyphs that happen to share a hue.
5. **Export AVIF + WebP + PNG, at 1× and 2×.** Done — see the measured budget below. The
   largest single file is `exhibit-07-viewer@2x.png` at 213 KB, and it is the PNG fallback that
   only a browser without AVIF *and* without WebP will ever request.
6. ~~Confirm `Qwen3.8-4B-Distill-GGUF` is the shipping default before it appears in copy.~~
   **Obsolete — there is no shipping default.** Istor *"doesn't ship with any model"*; `ollama`
   or `llama.cpp` is the requirement and the model is a recommendation the app makes if it
   finds one. **So no model name goes into copy at all**, and the constraint the item was
   protecting against cannot arise. §5's requirement paragraph carries the corrected wording.
7. **All three bitmaps carry a text alternative**, because all three contain words: the rail's
   ten source titles, the Viewer's passage, the dialog's five setting labels. A
   screen-reader user gets them as text even though a sighted user gets them as pixels. An app
   screenshot with `alt=""` is a hole in the page.

**Budget: measured, not estimated.** The three crops are **already produced** in
`Assets/Exports/`, at 1× and 2× in AVIF, WebP and PNG. **KB is decimal in this section — 1 KB =
1000 bytes** — because that is what a file listing, a browser's network panel and every CDN
report, and a budget table that mixes conventions is a budget table that lies:

| | 1× AVIF | 2× AVIF | 1× WebP |
|---|---|---|---|
| exhibit 7 · Viewer | 12.3 KB | 31.2 KB | 16.5 KB |
| exhibit 8 · Library rail | 3.7 KB | 8.6 KB | 4.7 KB |
| exhibit 9 · Settings | 4.2 KB | 8.9 KB | 4.2 KB |
| **total** | **20.2 KB** | **48.7 KB** | **25.4 KB** |

**Corrected 2026-09-18, and it was a real error rather than a rounding one.** This table and the
payload table below were reading the same files under **two different conventions** — the
bitmaps in binary KB and the fonts in decimal — which made the page's own total wrong by about a
kilobyte in each direction. The largest-file figure two items up (`213 KB`) had always been
decimal and was the one row that was right all along, which is how the mistake was found. Every
figure in this section is now decimal and the tables agree with `ls`.

A phone on 1× AVIF fetches **20 KB of images for the entire page**; a retina laptop
fetches 49 KB. The five references run 2.1–13.8 MB of images *each*, so the images are not where
this page's weight is and never were.

**The real payload is the type, and saying so is more useful than a ceiling.** A draft-2 version
of this section set a "150 KB image budget". It was a number I invented — 200 KB for four
bitmaps, moved to 150 KB when the fourth was cut — and measurement has now retired it, because
a ceiling the work already clears by 7× is not constraining a decision. What the page actually
costs a phone is:

| | what a phone fetches | retina |
|---|---|---|
| the three bitmaps (AVIF) | 20.2 KB | 48.7 KB |
| the ground tile, `ground-grain.png` | 0.5 KB | 0.5 KB |
| `inter-var.woff2` | 48.3 KB | 48.3 KB |
| `gfs-didot.woff2` | 14.5 KB | 14.5 KB |
| `istor-wordmark.woff2` | 1.9 KB | 1.9 KB |
| **total** | **85.4 KB** | **113.9 KB** |

The icons and the drawn figure are **inline SVG** — no request, and about 3 KB gzipped of
markup between them — so they add nothing to the image line. No JavaScript, no video, no
third-party request, no analytics. **Fonts are 76% of that** — one
file, Inter, is two and a half times all three images together **on the phone column**, and
about equal to all three on retina. So the low-spec-phone constraint
is stated against the real total, and the one decision it still leaves is worth naming:
**is the variable axis of `inter-var.woff2` worth 48 KB when the page uses three weights of it?**
Static subsets of 400 / 500 / 600 would cut that file substantially; a variable font keeps one
request and one cache entry. That is a real trade with a real cost, and it is the only place on
this page where weight is a choice rather than a consequence.

**Regeneration is deterministic.** Every crop is `magick <source> -crop WxH+X+Y +repage` with
the single hairline border in `--rule`, 2× downscaled for the 1× set, then AVIF q45 and WebP
q60. The crop boxes are in the table above; nothing is hand-placed. Self-host both woff2 files (they are 1.9 KB and 48 KB,
already local — no Google Fonts, no third party). No animation library. No scroll-timeline.

### Ground, icons, and one drawn figure — the artwork

**This is not "add illustration", and the distinction matters.** The five reference sites were
measured: **none of them uses illustration and none uses stock photography.** Their pages are a
dark app window and type. So the genre does not want pictures, and a page that added four
drawn figures to look editorial would be missing what actually makes Freebuff, BreezyCourses
and Tempo look the way they do. Read off them, it is three things Draft 2 had none of — a
ground that is not flat, an icon set drawn rather than borrowed, and marks for the browser
chrome — plus **one** drawn figure, which this page's subject hands over for free.

#### The ground is grain, never rules

`Assets/textures/ground-grain.png` — **451 bytes measured**, 128×128, shipped as
`background-size: 128px 128px` on the body. Generated by `Source/tools/make-ground.py`,
which is deterministic (fixed seed `20260918`) because `magick`'s noise is not stable across
versions and a ground that changes when the toolchain updates is not a ground.

Two speckle layers at 0.75% and 0.22% per pixel, at 7.5% and 4.5% alpha, **alpha-baked in
`--ink` (`#171717`)** — a `background-image` cannot be tinted by CSS, so the colour is in the
file, and one tile then sits on both `--paper` and `--chrome`. 0.97% of its pixels carry any
ink at all. Amplified eight times the structure is even and has no visible repeat; at the
strength it ships you can find it and cannot name it. Both knobs are in the script — raise
**alpha**, not density, if the built page reads flat.

**Grain only, and the reason is structural.** The hairline is this page's structural mark: it
draws the rails, the column edges, the section divisions, and the app window's own chrome. A
ruled ground is made of the same mark as the structure, and a page whose ground is hairlines
stops being able to say anything with a hairline. So the ground has no line in it.

**Black and teal get no ground.** Black because the app draws no rules there — Black's column
edges are a hue shift, not a border (§1) — so a texture would be inventing a surface the
product does not have. Teal because the close is one full-bleed moment and grain would soften
it. **The lighter build drops it** (§3), which is one file and one declaration.

#### The icons, and the finding is that the page needs five

I proposed ten traced app glyphs and eight leading-slot marks for the site's rail. **Both
numbers were wrong.**

**The eight rail marks are dropped.** The site's rail rows are the page's own movements, not
sources, so the app's leading slot — a `favicon` per source — does not transfer to them. Eight
bespoke marks for eight sections would be decoration, which §8 forbids, and the app's own Notes
rail, the one the hero shows in full, is **title-only** — so the page already has a precedent
for an unmarked list, in the product's own hand. **The leading slot stays empty.**

**Five glyphs, not ten**, because most of the app's vocabulary never reaches the page: the
exhibits are bitmaps, so glyphs inside them arrive as pixels for free, and §3 drops the rails'
expand/collapse controls, which is where much of it lives. What the page actually renders is
the magnifier in both `Filter sources…` and `Filter notes…`, the page-plus of `Add source` and
`New note`, the copy and save-as-note pair under every answer (§5 movement 6), and the Viewer's
pencil. Five symbols, `stroke: currentColor`, in one inline `<symbol>` sprite: **zero requests,
about 2 KB gzipped.**

**They are Lucide's own files, and the source is on disk.** *(Corrected 2026-09-18 — this section
said "redrawn, not extracted", to a 16px grid at 1.5px stroke, which was right while a 2× capture
was the only source. It is not any more: `C:\Projects\Istor\Source` depends on **`lucide-react`,
resolved to 1.31.0**, under `node_modules/dist/esm/icons/`. The five map to `Search`,
`FilePlusCorner`, `Copy`, `FileText` and `Pencil` — and **`FilePlus2` is an alias, not a file**,
which matters because the app imports the alias and a Lucide bump can drop it.)*

**The geometry is 24px at stroke 2, drawn at the app's own sizes.** Lucide's node data carries no
stroke attributes at all, so stroke is set once on the wrapper: a 24-viewBox glyph rendered at the
app's 14 and 16px draws at an effective **1.17 and 1.33px**, which is what the app actually looks
like. **Do not chase 1.5.** The full extractor contract — the alias, the bare `__iconNode`, the
wrapper — is Stage 3 of the build plan; what belongs here is the attribution it creates.

**And Lucide is ISC, so the page cites it.** The footer's small print carries *Icons from Lucide,
ISC* — a page that cites its own sources should cite these. This is the one provenance line the
page carries, and it is not decoration: the five glyphs are another project's work.

**And the rule that keeps an icon set from becoming decoration: nothing on this page is an
interactive icon, because nothing on this page is interactive** (§8, principle 2). A glyph here
can only be part of the DOM replica depicting the product, or an inline mark beside its own
word. No icon-only control, no lone glyph as a target — a page with no behaviour has no
affordance to icon.

#### One drawn figure, and the rule for drawing it

**Draw what is arithmetic, not what is scholarship.** The app's own captured answer prints four
things as numbers: the Metonic cycle as a **five-turn spiral dial**, the Saros as **223
months** with its **54-year Exeligmos** sub-dial, and the calendar ring as **354 or 355 holes**.
A generator given those numbers is exactly right. A gear train or a plate layout would be drawn
from memory — and the demo library was chosen precisely because this topic punishes that. So
only arithmetic gets drawn.

**The figure is the calendar ring, 355 holes, and it is placed in "Where it stops."**
`Source/figures/calendar-ring.svg` — **1,318 bytes, 694 gzipped** — generated by
`Source/tools/make-calendar-ring.py`. Beads at r=260 in a 24px band, 355 slots at a 4.602px
pitch, drawn as **one dashed `<circle>` rather than 355 elements**. `pathLength` is deliberately
*not* used: the dash arithmetic is literal in the file, so it cannot drift between renderers.
The disputed hole — the last of the 355 — is rotated to 12 o'clock and marked in `--azure` with
a radial tick and a `355` label.

**It is a ground, not a diagram, and that was a correction.** The first build centred a full
ring in the column: 500px of empty interior, and it read as a spinner. Pushed below the frame
and set behind the section's opening, the ring's interior holds the copy and the band becomes an
**engraved plate**. The copy sets to about **430px** inside it, so no line crosses the beads.
Below 1080px the plate keeps its interior wider than the measure and bleeds past the gutters,
clipped by the section — §3 owns that behaviour, and it is the only adaptation the figure needs.

**Its whole content is one dot, and that is the argument.** 354 holes are 1.0169° apart and 355
are 1.0141° — **0.0029° per hole.** The two rings are identical to the eye and always will be.
So drawing them side by side would prove nothing, and drawing them side by side while implying
otherwise would be exactly the overclaim this section exists to refuse. Instead: one ring, one
marked hole, and a caption that says **the difference is one you cannot see from here.** The
figure is the honesty section's own claim, at its true scale. The SVG is `aria-hidden="true"` —
the information is in the caption, as real text.

**And it does not become the page's second bold moment** (§8, principle 9). It is drawn entirely
in `--rule`, which is the hairline's own colour, so a plate the width of the column costs the page
no more contrast than a table rule does. The single azure hole is the second thing the eye finds
after the hero's citation, and it gets there by being the only non-hairline ink in a large quiet
field — not by being raised above it.

**The Metonic spiral and the Saros ring are specified and not placed, and no generator exists
for them — and that is now an answer, not a deferral.** The spiral was offered for the closing
movement and **declined** *(Thoria, 2026-09-18)*. The arithmetic above is all it would need, so
it stays viable if the page ever changes shape; it is off the page because the reference set
carries no illustration at all: **one figure placed where the argument is sharpest reads as an
editorial decision; four read as a house style.** The close in particular is one full-bleed
teal moment, and a second plate there would divide the thing the page ends on. The movements
already have their evidence — the hero's answer, the disputed table, the fetch log, the note,
the settings switch — and none of them needs a drawing to make its point.

#### Favicons and the card

- **`favicon.ico`** at 16/32/48, from `istor-eye.svg` — the master built for slots ≤32px.
- **`icon.svg`** from `istor-page.svg`, and **it carries its own `@media (prefers-color-scheme:
  dark)` block, because it has to.** The mark's `var()` contract works for inline SVG only — it
  cannot cross the `<img>` boundary, and a favicon sits on the far side of it. An SVG favicon is
  its own document, so the query goes *inside the file* rather than in the page's CSS. Without
  it the tab icon is near-black ink on a dark tab strip — the same failure already measured for
  `<img>` instances of this mark, where the ink renders `#171717` on a dark ground (§1).
- **`apple-touch-icon.png`** at 180×180, from `istor-page.svg`. No `mask-icon`.
- **`og-card.png` stays, unaltered** — locked, and now also load-bearing: its ground is the deep
  teal `#0D1D20`→`#132E2F`, and **§5's close uses that same teal.** The card and the page's last
  movement agree with each other, which is a better reason to keep it than that it was locked.
- **Neither the card nor the favicons is page weight.** 123 KB of `og-card.png` is fetched by a
  scraper and never by a visitor; the favicon is fetched once and cached. The budget table above
  is what a reader's browser actually pulls.

#### The head, and the one absolute URL

**This subsection was a gap until 2026-09-18, and the gap was load-bearing.** Everything above
names an `og-card.png`, a favicon set and a font subset — and the document specified no `<head>`
at all. A favicon and a font can be referenced relatively and get away with it. **An OG image
cannot:** a scraper resolves `og:image` against nothing, so a relative path is either dropped or
mis-resolved, and the card silently does not appear. That makes the canonical origin a build
input rather than a deployment detail.

**Deploy target, settled: `https://istor.fyi/` at the root** *(Thoria, 2026-09-18)*. Root rather
than a project subpath, which is the better of the two for this page specifically — every asset
path resolves from `/` with no prefix, so a file moved between directories cannot half-break, and
the OG URL needs no rewriting. **All site-absolute paths in this document assume it.**

```html
<html lang="en">
<title>Istor — it shows you what it saw</title>
<meta name="description" content="A local, private research notebook that runs entirely on
  your machine. Every answer carries the sources it read, and the ones it could not check.">

<link rel="canonical" href="https://istor.fyi/">

<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">

<meta property="og:type" content="website">
<meta property="og:url" content="https://istor.fyi/">
<meta property="og:title" content="Istor — it shows you what it saw">
<meta property="og:description" content="A local, private research notebook. Every answer
  carries the sources it read.">
<meta property="og:image" content="https://istor.fyi/og-card.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">

<link rel="preload" href="/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/gfs-didot.woff2" as="font" type="font/woff2" crossorigin>
```

- **The `<title>` is the h1, and that is deliberate.** §5 movement 1 opens on *It shows you what
  it saw.* The tab, the card's title and the page's first line are the same sentence, so the page
  agrees with itself wherever a reader meets it first. `Istor —` leads because the tab is where
  the name has to do its work; the h1 does not repeat it.
- **The description is the claim, not the category.** It says *local, private* and it says
  *carries the sources* — which is §8 principle 7's ordering in two clauses: accuracy first, then
  the consequences. No "the ultimate AI notebook", no "revolutionise your research".
- **`og:image:width` and `height` are declared** so the first share renders large rather than
  being guessed at.
- **Only two fonts are preloaded** — the two that render above the fold, Inter for the body and
  Didot for the h1. The wordmark subset is *not* preloaded: it is 1.9 KB and it appears once
  (§5 movement 7), so preloading it would spend a critical-path slot on the least urgent file on
  the page.
- **No `twitter:site`, no `og:site_name`, no author tags.** There is no account to attribute and
  no metadata worth inventing; `summary_large_image` plus the card is the whole requirement.
- **No analytics, no tag manager, no consent banner** — because there is nothing to consent to.
  This is the head where that claim is either true or quietly falsified, and it costs nothing to
  keep it true: the block above is the entire head.

#### And the shadow question, answered rather than dodged

§3 says **one shadow and no more**. Three of the five references — and the three named as
this page's quality target — separate their surfaces with soft elevation. That divergence is
real, so it should be a decision rather than a drift.

**The page takes the reference set's editorial register through line, ground and figure
instead:** a grain ground, an engraved plate, hairline structure, an icon set drawn to one
grid. Elevation is the one device the app does not own — it separates surfaces with hairlines
in the light theme and with a **hue shift** in Black (§1) — so a page that imitated the app's
window and then floated everything on drop shadows would be inventing a third grammar and
borrowing the reference set's instead of the product's. It also costs: a shadow is a repaint on
every scroll, on the cheapest device this page is meant to serve.

**And the exception is taken** *(Thoria, 2026-09-18)*. **Exactly one** soft shadow ships, under
the app window in **movement 1 only** — because the window is the page's one *object* and
everything else on the page is a document. Nothing else gets one, and the lighter build drops
it (§3) with the other blend and blur layers, so the cheapest device never pays for it.

**Correction, same day: §7 cleanup 1 never forbade it.** Cleanup 1 says "no rounded window
shadow", and that rule governs **the bitmaps** — it is an instruction about crop edges, not
about the page's CSS. I had written that cleanup 1 would have to change if the exception were
taken, which was a misreading: the two rules were never in conflict, and the page's single
shadow is a page treatment while the crops stay shadowless. A clause is added to cleanup 1 so
the next reader does not repeat the mistake.

---

## 8. Principles

1. **The page opens as an Istor window, and then stops being one.** The first movement is the
   app's three columns at the app's measured metrics. After that the rails go quiet and the
   page becomes a document. The conceit is an opening, not a costume worn to the footer.
2. **Nothing on the page responds to a click.** No behavioural JavaScript, no accordion, no
   tab, no disclosure. Static layout was the decision, and its consequences are taken rather
   than dodged: citation marks are `<sup>`, not buttons; the `Thoughts` disclosure prints
   already expanded; the FAQ is a visible list. **Nothing is lost by this** — a visitor who
   wants the hardware answer can read it instead of discovering it. **"Static" means no
   behaviour; it does not mean no adaptation.** The lighter build for phone and tablet (§3) is
   still part of this principle, because it is *declared* — media queries, `<picture>` sources
   — rather than *detected*. The moment the page needs to know what device it is on, it needs
   JavaScript, and this principle is what says no.

   **One script ships, and it is not an exception to this principle — it is the case this
   principle already covers.** *(Clarified 2026-09-18: read alone, "No behavioural JavaScript"
   says "no JavaScript", which the Motion paragraph below contradicts by specifying an
   `IntersectionObserver`. The reading was wrong rather than the paragraph, but the two should
   not have been left for a reader to reconcile — and the build plan's Stage 9 check 5 read it
   the wrong way, which is what surfaced it.)* The rule is about **behaviour** — anything that
   answers a user's action — and about **detection** — anything that asks what device it is on.
   The re-ink does neither: it reads scroll position, it answers nothing, and it never asks what
   it is running on. It ships inline, so it adds no request. And it is written so that its
   **absence is invisible**: the closing mark is authored in its dark contract, so a visitor
   whose script never runs sees the finished state rather than a stalled one.
3. **The page cites itself.** Every factual claim about the product points at its own
   provenance — to the app's own words, the repo file, the measured value. The mark is not
   interactive, but the structure is the argument: **the claim, the source behind it, and
   sometimes the verdict** — exactly as the app renders it, down to the fact that the verdict
   is about *which model wrote the citation*, not about whether the claim is true.
4. **One accent, two worlds.** A single blue, `#0066CC` on white and `#4DA3FF` on teal.
   **Coral is the warning ink** — the app's own "Unverified" colour — never decoration, and
   never a judgement on a claim, only on a citation's provenance. The
   site does not inherit the app's value: `#E85B5C` measures 3.45:1 and fails AA, so
   `--coral-ink` is `#C7292A`, 5.56:1, against a rule (§1).
5. **Weight is not available.** Didot Regular is the only display weight. Hierarchy comes from
   size, space and measure.
6. **Plain words only.** The site never says *grounding gate*, *band*, *chunk*, *RAG* or
   *retrieval*. It says *what it saw*, *the sources it read*, *where it stops*. The mechanism
   is the product's real advantage, and jargon is how it gets hidden from the people it is
   for. The one exemption is **quoted product output**, which is verbatim or it is nothing.
7. **Accuracy leads.** The first claim the page makes is that the answer can be checked, not
   that it is private, fast or local. Privacy is the easier sell and the weaker
   differentiator — every competitor claims it. Being *right*, and showing the work, is not
   claimed by anyone.
8. **Nothing is asserted that cannot be pointed at.** Where a number is unverified it is
   marked `[confirm]`, not filled in.
9. **Quiet everywhere, loud once.** The citation-and-witness moment is the only bold thing.
   **§7's plate is not a second one.** It is drawn in `--rule` — the hairlines' own ink — so it
   is the quietest mark on the page applied at scale, and its single azure hole is loud only
   because everything around it is a hairline. A ground made of the structure's own colour does
   not compete with the structure; it is what lets the one azure dot be the second thing you
   see without anything else being raised to meet it.

**Voice.** Sentence case. Active voice. No all-caps. No eyebrows above headings. No "A · B · C"
meta strings, no "WORD — fragment" labels, no "→" tacked onto link text. **Monospace only for
genuine terminal output** — never for labels or captions. That last one matters here: this
project has a terminal in it, and it is the obvious trap.

**Motion.** One moment in the whole page: as the closing movement crosses into the dark world,
the mark re-inks coral → azure. A ~15-line `IntersectionObserver` swaps `data-world="dark"` and
CSS does the rest. **Everything else is static.** `prefers-reduced-motion` makes it instant.

---

## 9. Review against the brief — what I changed, and why

| first instinct | problem | change |
|---|---|---|
| Progress dots in the left rail marking sections as read | decoration wearing the costume of information — the app's dots mean *source status*, and here they would mean nothing | **cut.** A plain current-section ink, no markers. The amber/green dot language is used in exactly one place: where the site depicts real app state. **The hero's wireframe went on drawing one anyway** — a `·` left in the leading slot, explained by a glyph legend that called it the source-status dot — and it survived until the seven-frame mockup (§3) put the rule and the drawing side by side. The wireframe no longer draws it, and the legend now says why the app's dot does not transfer: its rows are sources, which have fetch states, and these are movements, which do not |
| Calling the left rail's rows "the page's eight movements" | §5 does run eight movements, but movements 2, 3 and 4 all carry the one label **How it answers** — so eight rows would have put three identical labels in the rail, and a reader on movement 3 would see a different row inked from a reader on movement 4 | **changed** to **six rail entries**, in §3 and in the mockup, with the difference stated rather than glossed: the rail is a map of the argument's parts, not a count of its movements, and a row stays inked while its movements run |
| Auto-open citation `¹` on load, to teach the mechanism | a second orchestrated moment competing with the re-ink, for something a single written line does better | **cut.** The witness popover is simply already open over the hero answer, anchored to its citation, and one sentence says what it is |
| The CLI evidence as cropped screenshots of a terminal window | the niche's own move (Gamma ships a 1.9 MB MP4 to fake dynamism); costs megabytes, unselectable, invisible to assistive tech | **changed** to real text in `--fill` blocks. **Four** images instead of a dozen; budget drops from megabytes to <200 KB |
| A soft-shadowed rounded card behind the product shot — the SaaS-card kit | one radius and one grey shadow under everything is the single commonest generated-page tell, and it contradicts the app, which uses hairlines and square window corners | **changed** to a radius rule that varies by function (0 / 4 / 8, never 16+) and hairlines only, using the app's measured `#D3D3D4` |
| Treating the icon's documented sky-cyan as an open question to be voted on | it was framed as a tie between two blues | **resolved on evidence:** `#0066CC` and `#4DA3FF` are one hue at L40/L65. The sky-cyan pair is the outlier, not the alternative |
| Centred hero, headline over a screenshot | this is precisely the reference architecture, and it would make a sixth site that looks like the other five | **changed** to the left-aligned answer surface, with the page laid out as the app |
| The terminal debug screen as the "watch it decide" exhibit | it is a developer artefact, it needed `powercell`/`Taori` explained away, and the old captures it came from no longer exist | **changed** to the app's own `Thoughts` disclosure — same evidence, in the product's surface, captured in both themes, no developer names. The terminal keeps one small text block, for the gate decision only |
| Writing the "Where it stops" copy myself | the product had already written it better | **replaced** with the app's real **"What Is Still Disputed"** table, re-set as HTML |
| Asking for a re-shoot to fix framing drift and the theme gaps | the captures are raw source material; every exhibit is a crop or a transcription | **dropped.** Ten exhibits specified with source file and crop box in §7; nothing is re-shot |
| A hero built as one big product screenshot | the hero is the first thing anyone sees, and an image of text is the one thing this page cannot afford: it blurs, it cannot be selected or read aloud, it costs ~300 KB on the constraint that matters most, and it freezes the app's typography at capture time | **changed** to a DOM hero at the app's measured metrics — see §3. The capture is the spec, not the figure. The same reasoning turns five more exhibits from bitmaps into transcribed text |

**What is unchanged from the brief:** light default with the teal dark close; azure as the
site's accent; GFS Didot display + Inter body with Fraunces dropped; ἵστωρ as a real section;
the five references kept; one landing page that can grow without a redesign.

### The sixteen answers, and what each one changed

Settled in four batches on 2026-09-18. `Rec` marks the option I recommended, where that is
worth knowing.

| # | Decision | What it changed in this plan |
|---|---|---|
| 1 | **Static layout** for the app conceit | §0 rewritten from "the page cites itself" to "opens as an Istor window, **then stops being one**". Citations lose their buttons, the `Thoughts` disclosure loses its chevron, the FAQ loses its accordion, and the line *"Click a number to see the passage it came from"* is **cut**. Principle 2 |
| 2 | **The witness gets one section**, not a persistent rail | §3's right rail is the app's real Notes rail; the witness is a popover inside the hero and a movement of its own. It was never chrome |
| 3 | **Antikythera only** as the demo topic | `Documentation/demo-library.md` already holds the ten verified sources; no second topic anywhere |
| 4 | **Pure product voice** | "we" throughout; **Thoria** named only where a person is meant. No founder-voice section |
| 5 | **Eight movements**, FAQ included | §5 keeps all eight. The FAQ stays |
| 6 | **Point at the repo** for prelaunch | §6 rewritten: no email capture, repo as the one live action, and the reasoning recorded there so it is not relitigated |
| 7 | **Plain vocabulary only** | Principle 6. *Gate*, *band*, *chunk* banned from copy; the mechanism is named by what it does |
| 8 | **The rails fade out of the hero** | §0 and §3: the three columns are the opening, and after movement 1 the page relaxes into a document |
| 9 | **Keep the raw output, quoted** | §5 movement 2 keeps the two-column block verbatim, marked as quoted output and exempt from the plain-language rule. Its right column now comes from the app's live fetch panel, so **no search provider is named anywhere on the page** |
| 10 | **Honesty comes after the mechanism** | §5 orders the gate → the witness → **where it stops**, so the limits land as a consequence, not a disclaimer |
| 11 | **Mobile is the same page, one column** | §3 mobile rewritten: no sticky bar, no sheet, nothing to open |
| 12 | **Knowledge workers first** | §5 movement 1 rewritten to open in prose for a researcher; Antikythera proves rather than leads |
| 13 | **Prose opens, Antikythera proves** (`Rec`) | The hero's h1 is *It shows you what it saw.*, not the mechanism. The mechanism is the evidence, one step later |
| 14 | **The notebook gets an exhibit** (`Rec`) | §5 movement 6 gains the Metonic-cycle note + the Notes rail; §7 gains exhibits 5 and 9. Without this the page describes a chat app, not a notebook |
| 15 | **Accuracy leads** (`Rec`) | Principle 7, and the order of movement 1's claims |
| 16 | **Windows only where you act** (`Rec`) | The OS fact appears at the CTA and in the FAQ, **never** in the opening — a page about an offline AI notebook should not introduce itself with a compatibility note |

### And what changed when the verified-source captures arrived

Four new captures — `White/verifiedsource.png`, `White/verifiedsource2.png`,
`Black/verifiedsource.png`, `Black/verifiedsource1.png` — the same moment shot twice in each
theme. They invalidated two of the sixteen answers above, which is the point of taking them.

| what I had | what the captures show | change |
|---|---|---|
| The hero's right column is **the Witness** — a panel showing the source behind the answer | The right column is the app's **Notes** rail (`Filter notes...`, ten real note titles, `New note`). The witness is a **popover floating over the answer**, anchored to the citation it belongs to | **§3 rewritten.** The rail is now the product unaltered, and it proves the notebook claim in the first screen instead of the sixth. The invented panel is gone, along with the contradiction between §3's own fidelity rule and the thing it depicted |
| *"Unverified — check the source."* means **the source does not support the claim** | It means **a cheaper model wrote the citation.** Two models run, and the smaller one makes the fast calls: its main job is the **gate** — deciding whether the library already answers the question — and the other thing it does is retro-fit citations the answering model dropped, to keep latency down. Those are marked unverified | **§0, §4 and §5 movements 2 and 3 rebuilt** around Thoria's own two explanations. The card's anatomy is the evidence: verified shows the quoted passage, unverified shows the coral line and **no passage at all** |
| Widths 232 / 660 / 300 | **180 / 594 / 185** — the earlier numbers came from an expanded rail, not the default | §3 corrected, and the drift is stated rather than hidden |
| The hero question was the calendar-ring hole count | *"Tell me about the cycles."* — the app's own best answer, and its opening sentence lands on the Metonic cycle, which is the fourth note in the Notes rail | §5 movement 1 rewritten; the note/rail pairing is now literal rather than asserted |

**One thing the captures did *not* settle, and Thoria answered it directly:** whether the
two-model mechanic is published on istor.fyi at all. **It ships** (§10.7), and the answer went
further than the question — the cheap model's *main* job is not citations, it is the gate.
See below.

### And what Thoria's four answers changed

Asked on 2026-09-18, answered the same day. Three of the four moved something I had written;
one closed a question I had got wrong twice.

| question | answer | change |
|---|---|---|
| Publish the two-model mechanic? | **Yes** — and the division of labour is bigger than I had it. The cheap, heavily-instructed model *"makes decisions quickly… when web search is open, it decides if the local sources is enough, if yes it just uses local sources. That's not the only thing it does, but it's the main one."* | **§0, §4 and §5 movement 2 rewritten.** The gate is now the cheap model's headline job and the citation-fitting is its second — which turns the gate from an architectural claim into a cost claim, a stronger version. §5 movement 2 gained a paragraph; §5 movement 3 leads with the decision role and keeps the citation consequence as the payoff |
| Quote the dropped-citation gap? | **No** — *"not needed."* | §5 movement 3's instruction to exhibit `"and its directional orientation ."` is **struck**. It stays in the plan as evidence for the copy and stops being an exhibit. The hero is unaffected — different run, and the app's intro sentence never carries a citation |
| Which theme is the hero? | **Black** — *"verifiedsource.png as black looks the best in my opinion."* My question was badly put; the answer forks the page, so it was re-asked as a layout choice and settled as **light paper, dark window** | **The largest change of the four.** §1 gains a measured black token set; §3 states the hero renders in Black and that **Black has no column rules at all** — the boundary is a hue shift (`#0A0A0A` → `#0B0C0F`), not a hairline, so the replica must not draw one. §5 movement 1 and 3 follow. Exhibit 1 switches to `Black/verifiedsource.png`, **exhibit 8 is re-cropped from the Black run and re-exported**, and all three bitmaps are now Black — matching the window, with the light theme becoming the site's own material |
| Do the Viewer tabs exist? | **Yes, and more than I asked.** *"You can view both notes and sources, and you can edit both notes and sources. Sources is what the model uses to answer, notes is your own notes. You can instantly pull a response as a note by clicking the save button."* | §5 movement 6 gains the **sources-vs-notes** sentence and the **save button** — measured, two icon controls under every answer, the second one a note glyph, visible in both `verifiedsource.png` captures. But **no capture shows a tab row**, so exhibit 7 still ships the state that is captured and the old `Content` / `Fetched text` label stays off the page (§10.10) |

**The save button is the smallest and most useful of the four.** It is in a capture I had already
measured twice and never looked at the bottom of. It also happens to be the single most
persuasive detail for the audience: the answer becomes a note without anyone retyping it.

### And what Thoria's next answers changed

Four more, the same day, which between them set the page's quality target, its compute budget,
and what it may say about the model.

| question | answer | change |
|---|---|---|
| What model does Istor ship with? | **None.** *"It doesn't ship with any model. Ollama or llama.cpp is a requirement at the moment, and when you download istor, if you have ollama: it recommends `qwen3.8-4b-distill-gguf`… If you don't have them you just go to settings and chose a model of your own choice."* | §5's requirement paragraph rewritten: **it does not ship with a model, and that is the honest shape of it.** The page names no shipping default because there is none — `ollama` or `llama.cpp` is the requirement, the model is a recommendation the app makes if it can, and otherwise the reader picks. This retires §7's cleanup 6 |
| Do `powercell` and `Taori` appear on istor.fyi? | **`powercell` does not exist** — *"I think I misspelled powercell which spiraled into a huge communication error between us."* It entered this document through a misspelling and propagated through several sessions. *"We don't need to name powershell at all."* **Taori is real:** *"Taori is what the application is built with, so Rust & Taori might be named on a FAQ if needed."* | §5's requirement paragraph and §5 movement 2 corrected: **name nothing about the shell anywhere in copy.** Rust and Taori are permitted **in the FAQ only**, where a reader who wants the stack is already asking |
| How good does this page have to be, and what happens on a phone? | *"We want to create the website closer to the quality of Freebuff, BreezyCourses and Tempo. So, the idea is that it's very editorial, and changes into a lower computing required webpage whenever we detect it's on phone or a tablet."* | **§3's mobile section is now a second build, not a narrower one**, and it is *declared* — media queries and `<picture>` sources do the detecting, which is what Thoria described, without a script. §8 principle 2 gained *"Static means no behaviour; it does not mean no adaptation."* The editorial target is what §7's artwork subsection answers — and the five references' own measured habit is that **none of them uses illustration**, which is why that section adds ground, icons and one drawn figure rather than pictures |
| What hardware does the site have to survive? | *"For the main website, we don't have a set hardware spec, it just has to work perfectly fine with at least GTX 1650 (4gb vram), which is a fairly free scope."* Confirmed as **the website's budget, not the app's** | **The main build may keep its expensive surfaces** — blend and blur layers, 2× images, large display settings — because a GTX 1650-class machine is the floor, and that is a generous one for a document. The lighter build (§3) is what covers phones and tablets. **The app's own minimum spec was still open at this point** (§10.1) — this answer was about the site; *closed in the next table* |

**One ambiguity, flagged and then closed without resolving it — correctly.** The recommended
model was written twice as the identical string, `qwen3.8-4b-distill-gguf`, once as "it
recommends X and X". If two variants were meant — a size pair, the way these distill sets
usually ship — the second name is missing. I asked; Thoria's answer was **"Doesn't matter —
copy stays generic"**, which is the right close rather than a dodge: **no model name is printed
in copy at all**, so the missing half has no consequence for the page. It is recorded here as a
resolved non-issue rather than left looking like a loose end, and if the app's recommendation
ever does go on the page, the question comes back with it.

### And the four answers after those

Four more on 2026-09-18, asked as an `AskUserQuestion` pass. Between them: two items close, one
reverses a decision, and one corrects a measurement of mine.

| question | answer | change |
|---|---|---|
| Does istor.fyi state a minimum spec for the **app**? | **No.** *"No — leave it out."* The page publishes no RAM or VRAM figure, and the reason is the model picker: the requirement depends on the model the reader chooses, so any floor would be a floor for a model they have not picked | §10.1 **closes, both halves** — the site's floor is a GTX 1650 and the app's is deliberately unpublished. §5 movement 6's pending figure becomes a decision, and the FAQ's *"What hardware do I need?"* keeps its place and answers with the reason rather than a number |
| Should the closing movement get the **Metonic spiral** as a second drawn figure? | **No** — one figure only | §7's spiral stays specified, unplaced and ungenerated, and **stops being a standing offer**: it was declined, and the reason is recorded. The close is one full-bleed teal moment, and a plate there would divide the thing the page ends on |
| Pre-approve **one soft shadow** under the hero's app window, or keep the page shadowless? | **Pre-approved** — the exception is taken | §3's bare "no shadows" becomes "one shadow, and only one", and §7's shadow subsection moves from a conditional exception to a taken one. **§7 cleanup 1 needed no change** — it forbids the *capture's* rounded window shadow, not the page's CSS, which I had misread as a conflict; a clarifying clause is added so the next reader does not repeat it |
| Will copy **name the search backend**? | **No** — *"Doesn't need to be named."* But the keyless claim is authorised: *"We use both SearXNG, Brave and Scraping (keyless). The default is SearXNG… you can claim it works without keys. It supports the no-telemetry claim."* | §5 movement 6 rewritten: **no provider is named anywhere**, and the keyless claim is made about what is *required* rather than what is *present* — Brave would take a key, so the honest form is *no account and no key are required*, never *no key is ever used*. §10.4 closes. **And a correction:** the capture shows **Scrape** selected while the real default is **SearXNG** — I had published my own measurement as the product's default |

**The shadow answer is the one that changed the plan rather than closing a question**, and it is
worth saying why it was asked at all: §3 and the reference set genuinely disagreed, and a
disagreement left as a default is drift, not a decision. Taking the exception in advance is the
cheap version of settling it — one `box-shadow` on one element, dropped by the lighter build,
decided now rather than discovered by whoever builds the hero and finds it flat.

### And the last three, which close the plan

| question | answer | change |
|---|---|---|
| Where does the site deploy? | **`https://istor.fyi/` at the root** | §7 gains **the head**, which the document had been missing entirely — `<title>`, description, canonical, favicon links, the OG block, and two font preloads. **The gap was load-bearing:** an OG image needs an *absolute* URL, so the canonical origin was a build input rather than a deployment detail. Root also means every asset path resolves from `/` with no prefix, so a file moved between directories cannot half-break |
| Was a second model variant meant? | **"Doesn't matter — copy stays generic"** | §5 movement 6 **no longer prints a model name at all.** It had been printing `qwen3.8-4b-distill-gguf` as a small spec line, which contradicted the standing rule that no name goes in copy — a contradiction I had left in place rather than noticed. The FAQ answers *Which models can it use?* the same way, and the ambiguity is recorded as a resolved non-issue |
| Add an implementation section to close the plan? | **No** — design-only | §0–§10 stay as they are: the plan specifies, it does not schedule. The generators in `Source/tools/` are the only code it owns |

**The head was the last real gap, and it took a deployment answer to find it.** Worth noting how
it hid: this document discusses the OG card at length — its teal, its 123 KB, the fact that it is
locked — and never once asked where it would be served *from*. **A social card is the one asset
whose address must be absolute**, so the question the plan could not answer turned out to be the
one it had to answer first.

---

## 10. Open questions

1. **~~Hardware floor~~ Closed, and both halves of it.** Thoria, 2026-09-18: *"For the main
   website, we don't have a set hardware spec, it just has to work perfectly fine with at least
   GTX 1650 (4gb vram), which is a fairly free scope"* — confirmed as **the website's budget,
   not the app's.** So the site's floor is settled: the main build keeps its expensive
   surfaces, and the lighter build (§3) covers phones and tablets. **And the app's own minimum
   spec is not going on the page at all** *(Thoria's answer, the same day)*. The CLI's
   4B-at-Q4-with-32-offload-layers is evidence, not a minimum, and publishing a number would
   put a stale figure in front of the audience on the one claim this page is most careful
   about. **§5 says nothing about RAM or VRAM, and that is the decision rather than a gap.**
2. **~~Do the names `powercell` and `Taori` appear on istor.fyi?~~ Answered — and `powercell`
   was never a thing.** *"I think I misspelled powercell which spiraled into a huge
   communication error between us"* — it entered this document through a misspelling and
   propagated through several sessions before anyone caught it. *"We don't need to name
   powershell at all."* **Taori is real** — it is what the app is built with — and *"Rust &
   Taori might be named on a FAQ if needed."* So: **name nothing about the shell anywhere on
   the page**, and allow **Rust and Taori in the FAQ only.** §5's requirement paragraph and §5
   movement 2 are corrected, and the word `powercell` must not appear in any copy.
3. **~~The site's own build tool~~ Settled — any tooling, and the plan needs none.** Any tooling
   is acceptable per the brief, so this never was a preference question. The constraint is
   **two-tier rather than one** *(Thoria, 2026-09-18)*: the main build has to *"work perfectly
   fine with at least GTX 1650 (4gb vram)"*, and the lighter build (§3) is what serves phones
   and tablets. So the deciding factor is a budget — a generous one for the main build, a tight
   one for the second. **And the budget is not close:** nothing in the plan needs a bundler, a
   framework or a build step; the page is HTML, CSS, two fonts, three bitmaps, one ground tile,
   and inline SVG.
4. **~~The search backend's name in copy~~ Answered — three backends, none named, and one
   claim authorised.** Thoria, 2026-09-18: *"We use both SearXNG, Brave and Scraping (keyless).
   The default is SearXNG. Doesn't need to be named. But, you can claim it works without
   keys. It supports the no-telemetry claim."* So: **no provider is named anywhere on the
   page** — the exhibit quotes the app's live fetch log, which names only the sites it read,
   and the Settings crop speaks for itself. The page **does** make the keyless claim, scoped to
   what is *required* rather than what is *present*, because Brave would take a key. §5
   movement 6 is rewritten, including the correction that the capture shows **Scrape** selected
   while the real default is **SearXNG** — I had published my measurement as the default.
5. **The coral status line at 3.45:1 in the app — written up, app-side.** The site darkens it to
   `--coral-ink` `#C7292A` (5.56:1) and is compliant. **The app-side fix is now its own note:**
   `Documentation/app-coral-contrast.md` carries the measurement, the hue-preserving correction
   and the argument for why it is worth fixing rather than accepting. It is **not a site
   blocker** and nothing here depends on it — it is recorded so the fix is a one-line token
   change if Thoria takes it, rather than a re-derivation. It stays in this list because it is
   the only item still open, and it is worth seeing that it is the only one.
6. **~~Does the witness card have a positive verdict?~~ Answered — there isn't one.** The
   verified card carries **no verdict word at all**: source title, then the quoted passage,
   and nothing else. So the app's structure is *claim → source → and only sometimes a verdict*,
   and the site reproduces exactly that asymmetry rather than rounding it into three stable
   parts. §3's wireframe and §4 are corrected, and §5 movement 3 shows both states.
7. **~~Do we publish the two-model mechanic?~~ Answered — yes, and it is bigger than the
   question.** Thoria, 2026-09-18: the cheap, heavily-instructed model *"makes decisions
   quickly… when web search is open, it decides if the local sources is enough, if yes it just
   uses local sources. That's not the only thing it does, but it's the main one."* So the
   **gate is the cheap model's headline job** and retro-fitting citations is its second — one
   small model asked to be decisive so a better one can be slow. §0, §4, §5 movements 2 and 3
   rewritten; it is now the page's opening claim rather than a footnote to the coral line.
8. **~~Does the site quote the dropped-citation gap?~~ Answered — no.** *"Nope, not needed."*
   The `"and its directional orientation ."` gap in `White/Question1.png` stays in this
   document as evidence for the copy and **does not become an exhibit**. §5 movement 3's
   instruction to show it is struck. Nothing else changes: the hero is a different run, and its
   opening sentence carries no citation because the app's intro line never does.
9. **~~Which theme is the hero?~~ Answered — Black, on a light page.** Thoria preferred the
   Black capture, and my question was too compressed to be answerable, so it was re-asked as a
   layout choice: **the page keeps its light paper and the app window renders in the app's Black
   theme**, which forks into the changes tabled in §9 — a measured black token set in §1, the
   no-column-rules finding in §3, the hero and the card in §5 movement 1, and exhibit 8
   re-cropped from the Black run so all three bitmaps match the window.
10. **~~Are the Viewer's `Content` / `Fetched text` tabs real?~~ Answered — the tabs are real;
    the label is not, and the capture is not.** Thoria confirms both notes and sources can be
    viewed **and edited**, that sources are what the model reads while notes are the reader's
    own, and that a **save button pulls an answer straight into a note**. But no capture in the
    35 shows a tab row — I re-checked `White/viewingsource-editingnotes.png`,
    `Black/Sourcesfullscreenview.png` and `Black/SourcesFullScreenEditing.png` and each shows a
    title, two icons and the raw markdown — so **exhibit 7 ships the captured state and the row
    is not invented**, and the old `Content` / `Fetched text` label stays off the page. The
    capability goes into copy; the label waits for a capture. The save button is measured
    (two icons under the answer, the second a note glyph) and is now §5 movement 6's detail.

**Settled since the first draft:** the pupil (`#0073E6`, above); the demo library
(`Documentation/demo-library.md`, ten verified sources); the research-band exhibit (the
from-zero run, empty library and all — Thoria's choice, 2026-09-18); the "watch it decide"
exhibit (the `Thoughts` disclosure, not the terminal); the raw captures are source material to
be cropped and polished rather than figures, so framing drift never warrants a re-shoot; the
artwork in §7 — the **grain ground, five icons and one generated plate**, all deterministic,
with the generators in `Source/tools/`; the sixteen direction
answers of 2026-09-18, tabled in §9; the five corrections the verified-source captures
forced, tabled beneath them — **the Notes rail, the popover, the 180/594/185 widths, the
cycles question, and what "Unverified" actually means**; the four answers of the same day
that closed out §10 — **the two-model mechanic ships, the dropped-citation gap does not, the
hero renders in the app's Black theme on light paper, and the Viewer's tabs are real even
though no capture shows them**; and the four after those — **no model ships, `powercell` is
not a word, the page is editorial with a declared lighter build, and the main build's floor is
a GTX 1650**; and the four after those — **the app publishes no minimum spec at all, one figure
stays one figure, the hero's single shadow is pre-approved, and the keyless claim ships without
naming a backend.**

**And one item removed:** the prelaunch CTA action was an open question. It is not any more —
**the repo, and no email capture.** The reasoning is in §6; it is recorded there rather than
here so that it is answered once, in the place someone would otherwise ask it again.

**And the list is closed.** Nine of the ten items above are struck through; the tenth is the
app's coral status line, which is **written up and app-side** (`Documentation/app-coral-contrast.md`)
and depends on nothing in this plan. **No open item remains on the site itself**, and no
`[confirm]` marks remain anywhere in the document — every figure in it is either measured,
generated by a checked-in script, or a decision with a date and a name against it. What is left
to settle is a deployment, and the plan now names where that goes.
