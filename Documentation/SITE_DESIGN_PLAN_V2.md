# SITE_DESIGN_PLAN_V2 — istor.fyi

**Status:** specification. Supersedes `SITE_DESIGN_PLAN.md` (v1, 1,782 lines) wherever the two
disagree, and the precedence rule that made v1 unarguable is retired with it (see §13).
**Written:** 2026-09-19, after Thoria rejected v1: *"Our site is literally plain text with
screenshots… we just created a blog post. How? Why? Also, how did we not add a single animation?"*

**Evidence this plan is built on** — both are on disk and both are measured, not estimated:

| Document | What it supplies |
|---|---|
| `.improvement/ref-analysis/REPORT.md` | Five reference recordings, frame-analysed. Section architecture, sampled hexes, measured geometry, motion probes, and a ranked account of what is actually doing the work. |
| `.improvement/assets/CATALOGUE.md` | All 36 app captures catalogued, with measured window geometry, sampled app palette, a ranked shortlist, and six crops already written to `.improvement/assets/crops/`. |

**Two decisions Thoria made 2026-09-19** that this plan implements and does not re-open:

1. **The primary CTA is "Follow the build" → `https://github.com/ThoriaDevelopment/Istor`.** The
   product repo is empty (`size: 0`, no releases, no tags, no files — verified against the GitHub
   API), so there is no download to offer. The slot is designed once and swaps by one line when a
   release exists (§10.3).
2. **Imagery is built on the 36 captures we have**, plus an appendix of captures that would
   improve the page and block nothing (Appendix B).

---

## §0 · Why v2 exists

v1 did not fail at execution. Its tokens, grid and measure reproduce on the live page exactly.
**v1 failed as a target**, and it said so itself, in three lines that between them forbid
everything the reference genre is made of:

| v1 says | The genre does |
|---|---|
| §8 P2: *"**Nothing on the page responds to a click.** No behavioural JavaScript, no accordion, no tab, no disclosure. Static layout was the decision."* | Sticky navs, accordions, hover states, dropdowns — in all five |
| §8: *"One moment in the whole page… **Everything else is static.**"* | Tempo alone ships **124 `@keyframes`**; all five animate |
| §7: *"the app ships as an image only where its **form** is the argument"* → *"**three bitmaps, not ten**"* | The product appears **4–7×** per page |

Compounding it: the precedence rule (*where the two plans disagree, the design plan wins*) made
obedience feel like correctness, and each individual decision — "one re-ink script", "no bitmap in
the close", the 85 KB budget — was defensible alone. Nobody summed them. The markup is the receipt:
the shipped page has **9 `<section>`s and 8 carry the bare class `m`.** One section shape, nine
times.

**And the verification was a compliance suite.** 53 assertions on bytes, links, contrast and
accessibility, all green, on a page that reads as an essay. None of them can detect "this is not
what we were aiming for." v2 changes what gets asserted: §12 adds a *composition* gate, not only a
byte gate.

**v2 keeps v1's substance and discards its austerity.** Kept: plain words, accuracy leads, nothing
unverifiable, one accent across two worlds, the citation as the argument, the Greek wordmark, GFS
Didot. Discarded: the ban on interaction, the ban on motion, and the three-bitmap ceiling.

---

## §1 · The thesis

> **The app window sits in the deep teal field. Every time.**

The genre's single most load-bearing property is not a style — it is **one dominant compositional
idea, enforced across every section without deviation**. Tempo = a gradient field behind every
product shot. Freebuff = black with exactly one green. Gamma = one pastel illustration language.
The report ranks this **#10 of 15** and calls it *"what separates the sites that look designed from
the sites that look assembled."*

Tempo's version of it is measurable: field **84% viewport width**, insets 8% each side, window
**74% vw** inside it, **≈65px CSS** padding, **28px** top radius. That is precisely the device.

**We already own the field.** The og-card's ground is a *locked brand asset* — a deep teal radial,
measured today across eleven sample points:

| Sample | Hex |
|---|---|
| x85 y15 — brightest | `#163234` |
| x50 y5 | `#11282B` |
| x20 y20 | `#101F23` |
| edges (four samples) | `#0E1E22` |

So the page's dominant idea costs no invention: **the brand's own ground becomes the stage the
product stands on.** Not a tint, not a wash — the locked asset, used structurally.

Three consequences follow, and they are the whole design:

1. **It gives the page a system instead of a style.** Every product moment resolves the same way,
   so the page reads as designed rather than assembled — the exact property v1 lacked.
2. **It makes the app window an object on a surface.** A dark app window on paper is a hole; a
   *light* app window on teal is a lit object. The app ships both themes and the captures use both, so
   what actually makes a window read as an object is its **separator** rather than its theme: a 1px
   seam with a field-tuned shadow where the ground is a field, and a paper-tuned shadow alone where it
   is paper (§3.4, which is measured and was rewritten when the pairing turned out not to hold).
3. **It is honest.** The teal is already the brand's, and the themes are already the app's. Nothing
   here is invented to look like a designed page.

**The motion thesis, which is separate and equally load-bearing.** The report's #9 ranked item is
*"the product is shown DOING something, large enough to read"* — and it is blunt about the stakes:
*"a beautifully shadowed card containing an illegible blur is worse than no card."* #14 adds that a
motion budget must match what the product *is*. Istor's product **is a sequence**: a grounding gate,
then the reading, then an answer whose every claim points at a passage. We already wrote the
sentence — *"You can watch it decide."* So the page **performs the sequence** rather than describing
it. That is not decoration bolted onto v1; it is the argument.

And it is the one open move in this genre. The report's closing note: **none of the five puts a
video player on the product**, and Breezy's hero card — which advances through an app session —
is the only place the product moves at all. Our hero is a **live DOM replica**, not a bitmap, so we
can do that better than a video: the product moving on the page, with no player chrome.

---

## §2 · Section architecture

**Twelve acts in `<main>`**, ≈14 viewports, plus the sticky nav and the poster close. The genre runs
7–16, and every body paragraph on this page is 2–4 lines (genre rule, no exceptions across five
sites).

The genre's other rule is headline length, **3–7 words**. Measured on the built page, the ten real
headlines run **6, 6, 6, 5, 6, 3, 5, 3, 6, 4** words; the remaining two "headings" are a section
label ("Questions") and a word being defined ("ἵστωρ"), where a word count does not apply. Act 2's
twelve-word headline was the one that broke the rule, and its fix (2026-09-20) is the split every
other act already uses: the headline is "It checks what you already gave it." and its second clause
opens the lede as "Before it looks anywhere else."

Compositions are named **C1–C5** and defined in §3. The page alternates them deliberately — the
report ranks alternation **#12**, and notes that Gemini Notebook, competent and entirely
non-alternating, *"is the least memorable of the five despite having the best single element."*

This table is **measured from the built page, not remembered from the brief**, and `verify-links.py`
asserts the parts of it a static check can hold: that there are **twelve** acts, that the grounds run
`DPPPPPDPPPPD` with no run longer than five, and that the four C2 acts alternate the side the field
sits on — right, left, right, left. It said "Eleven acts" and enumerated ten for a week while the
page shipped twelve, and nothing noticed, because the gate counted sections against a floor of ten.

**The act names below are the anchor ids.** That makes them the durable handle rather than a
nickname: `#the-library` is in the nav, in the hero's own rail and in the ring's plate, so renaming
one breaks navigation, which the link gate already catches. Three acts carry no id (4, 5 and 12)
because nothing links to them. The headline column is each act's real `<h2>`, copied from the built
page. The paraphrases it used to carry were shortened by hand and never checked: act 2's is twelve
words and the table gave seven, which is how a headline that breaks the genre's length rule passed
review for a week as one that kept it.

| # | Act, by anchor id | Headline, as built | Composition | Ground | Product shown |
|---|---|---|---|---|---|
| — | nav — `#nav` | — | sticky bar, 1px hairline on scroll | paper | — |
| 1 | hero — `#what-it-is` | It shows you what it saw. | **C1** field-full | teal | the app window as a live **DOM replica**, animated |
| 2 | the gate — `#how-it-answers` | It checks what you already gave it. | **C2** split, field **right** | paper + teal | `exhibit-10` |
| 3 | the passage — `#the-passage` | Every claim points at a passage. | **C2** split, field **left** | paper + teal | `exhibit-11`, the witness |
| 4 | the reading — no id | You can watch it decide. | **C2** split, field **right** | paper + teal | the live reading log (DOM) |
| 5 | the dispute — no id | It marks what nobody knows yet. | **C2** split, field **left** | paper + teal | the live dispute table (DOM, 2026-09-21) |
| 6 | the machine — `#on-your-machine` | On your machine. | **C3** diptych, one inset field | paper + teal | `exhibit-14` + `exhibit-15` |
| 7 | the workspace — `#the-library` | The library is the interface. | **C4** band | teal | `exhibit-16` + `exhibit-17` |
| 8 | the stop — `#where-it-stops` | Where it stops. | plate, drawing bleeds, no window | paper | the calendar-ring plate, generated |
| 9 | the evidence — `#the-evidence` | What it did, and how well. | measure, then ruler and one exhibit | paper | `exhibit-18` |
| 10 | questions — `#questions` | Questions | one column, 46rem, exclusive accordion | paper | — |
| 11 | the name — `#the-name` | ἵστωρ | close measure, no exhibit | paper | — |
| 12 | the close — no id | Istor is not finished. | **C5** poster | teal | the wordmark, occluded by the horizon |

Four of the twelve are C2, and they are acts 2–5: field right, left, right, left. That is the
zig-zag the report's #12 is about, and it is why the four paired acts are the page's first half.
The second half has no field to flip, and carries its rhythm with the measure instead — the band at
act 7, the ring's full-bleed line drawing at act 8, the ruler and one screenshot at act 9. The grounds change four
times, which is more than four of the five references manage: Breezy is one flat blue throughout,
Tempo is black throughout, Freebuff is black with photographic bookends, and Gemini Notebook is white
throughout and is called the least memorable of the five for it.

### 2.0 How these subsections are derived

They are **§2.1 to §2.13 — the nav, then the twelve acts in built order**, one subsection each. That
was not true before this pass. §2.3's diagram gave the C2 boxes as 488/688/560 when they are
480/696/600; §2.4 called act 3 a "C4 band" when it is a **C2** split; §2.5 called act 4 "mirrored"
where the measurable fact is that its field is on the right; §2.6 gave the portrait window as 360×470
when its file is 430×480; §2.7's diptych was one field the width of `--field` in the definition and
the width of `--page` on the page; §2.8 specified a three-up with icons that the build rejects by
measurement (§2.8 gives the reason); §2.9 bundled three acts into one subsection with a paragraph of
pointers; and **acts 8 and 12 had no subsection at all**, so the ring — the one drawing generated
from the app's own answer — and the poster were the two acts the plan never described. The subsection
numbers happened to line up with the act numbers; almost nothing under them did.

Each subsection was written from the built markup rather than from the brief: the `<section>` class
list, the exact `<h2>`, the DOM order of `.body` against `.field` (which is what the side alternation
actually is, `is-flip` moving the field to column 1), the boxes measured at 1440, and the ids of the
exhibits the act carries. Where the build departs from what this plan originally specified, the
reason is recorded here rather than left in a markup comment that a reader of the plan will never
open. The one number that is a measurement rather than a token is named with what produced it.

### 2.1 Nav — sticky

```
┌────────────────────────────────────────────────────────────────────┐
│  ἰστωρ.        How it answers · On your machine · Questions   [ Follow the build ] │
└────────────────────────────────────────────────────────────────────┘
   ↑ hairline + paper surface arrive on scroll (M1)   ↑ the genre's persistent CTA
   2px reading progress, under the bar, scaled X
```

Four of five references are sticky, and each gains a 1px hairline once scrolled. Breezy skips it and,
the report notes, *"reads more like a brochure than an app as a result."* Height is **68px**, the
`--nav-h` token, which is also how far the hero's field is pulled up under the bar: two numbers that
must agree are one number.

The three links are anchors into the built acts 2, 6 and 10 — "How it answers", "On your machine" and
"Questions" — and the mark links back to the hero. This is not the page's only navigation (§2.2's rail
is the other) but it is the only one that persists, and it replaces v1's arrangement where the only
nav was painted *inside a screenshot*. It also carries the page's one scroll indicator: a 2px
`--azure` line under the bar, scaled on X, which the stylesheet calls *"a quiet orientation cue, not a
second navigation system."*

**The bar has two surfaces, and the change is content rather than paint.** While the nav is inside the
hero's field it owns no surface at all — no background, no blur, no hairline — with its mark and links
switched to the field's ink and its CTA to `--azure-lift`. Paper, blur and hairline arrive together
once the field has scrolled past (`.nav.over-field`; §4 defines the two accents, because an accent
that has to survive on teal cannot be the one that was chosen for paper).
A reader whose browser never runs a script keeps the paper state throughout, which is the safe way to
be wrong.

### 2.2 Hero — C1

```
╔════════════════════════════════════════════════════════════════════╗
║  ░░░░░░░░░░░░░ deep teal field, full-bleed ░░░░░░░░░░░░░░░░░░░░░░░  ║
║                                                                    ║
║                 It shows you what it saw.                          ║  94px, GFS Didot, 1.06
║                                                                    ║
║        Local. Offline. Every claim points at its passage.            ║  one line, genre rule
║                                                                    ║
║      [ Follow the build ]    See the evidence ⌄                    ║  azure pill + scroll cue
║                                                                    ║
║        ┌──────────────────────────────────────────────┐            ║
║        │  the app window — 959px, live DOM replica     │            ║  ← M2 plays here
║        │  180px rail │ 594px answer pane │ 185px rail  │            ║
║        └──────────────────────────────────────────────┘            ║
║                     ↑ 48px field padding (--field-pad)             ║
╚════════════════════════════════════════════════════════════════════╝
```

The hero **is** the product doing something, so there is no separate "product demo" section — the
genre's usual second act is folded into the first. The headline is v1's, unchanged: six words, the
page's own `<title>`, and the most distinctive sentence the brand owns — and its key phrase,
"what it saw", now carries the page's one accent (`--azure-lift` on the field, 5.19:1; the light
`--azure` would be 2.9:1 here), the way the genre lifts its key phrase. The lede is **one line**:
"Local. Offline. Every claim points at its passage." It replaced 42 words that read as a seven-line
wall at phone width; the genre's subheads run one line (Freebuff's is six words), the full value
proposition is acts 2 and 3's job, and the new line's last clause is act 3's own headline, so the
vocabulary stays the page's.

**The left rail is a real navigation.** It is a `<nav aria-label="Sections of this page">` carrying
seven in-page links — What it is, How it answers, The passage, On your machine, The evidence,
Questions, ἵστωρ — so the page's map is drawn *by* the replica rather than beside it, and the first
thing a visitor can operate is the app. Every one of those anchors resolves in the link gate, which is
what keeps the device from becoming a decoration that lies.

**The two reserved answers are disclosures, not script.** "Who made it?" and "What do the inscriptions
say?" sit in their own `<details>` inside the replica's answer pane, so a reader whose browser never
ran a script can still open the second and read the refusal — the one place on the page where a
visitor watches *it says so when it cannot* happen. With script, M10 moves each answer out of its
shell into the pane once the app can answer for them, and hides the shell.

**The secondary CTA is a scroll cue, not a second button.** "See the evidence" is a diamond-tipped
link to act 9, which is the page's promise being checked by its own numbers.

**The field carries a world, and it is the mechanism (2026-09-20).** Every reference hero stands on
one: Tempo's product floats over a planet limb and Freebuff's over an illustrated landscape, both
cropped so the world reads as larger than the frame. This hero stood on a gradient — type, a window,
and nothing to look at on a 1440-wide field. A band 418px tall at the field's bottom edge now carries
the gearing: the mechanism's largest wheel, **223 teeth**, and two of its **48-tooth** wheels meshed on
the wheel's flanks. 223 is in the literature the page's library is built from and the page already
prints it as the Saros cycle's length; 48 is the count of the wheel that drives it in the published
reconstruction, so the numbers came from the same place the prose did.

The band's geometry is arithmetic rather than arrangement, and the interesting part is what it
refuses. The pinions' centres sit at y = 240 in the drawing so that neither wheel is cut by the
container's own box, because a layer's edge cuts a circle into a straight chord and a gear with a
flat side is a bug that looks like a style. The great wheel's pitch radius is 505, which puts its
crown at y = 40 — exactly the window's bottom edge, because 40 is `--world-overlap`, and the generator
READS that token out of the stylesheet rather than repeating it: two numbers that must agree can only
be one. Tangent is the point. The wheel's top meets the plate's edge, so the product touches the world
without either cutting the other, and the wheel then runs off the page's own bottom edge, which is
where a world should end. (The first placement put the crown 110px lower and a shot showed what that
looks like: a wheel floating under a plate, unrelated to it. One number, and it is the whole effect.)

The teeth are a **dash pattern**, not 223 paths: `stroke-dasharray` on a circle stroked at the tooth's
depth is what a cut tooth is, and it costs 90 bytes a wheel where the paths would have cost about 9 KB
of coordinates. The phase of each wheel is solved so a tooth's centre meets a gap's centre at each
mesh point, which is also what lets the drawing MOVE: the pattern is rigid with the wheel, the two
phases sum to a constant under a rotation of `R1/R2` in the opposite sense, and that relation is what
M14 drives — so the mechanism is a geared drawing and not a drawing of gears. `make-hero-gears.py
--self-test` asserts the invariant at 0°, 2°, 4° and 8° and asserts that flipping the pinion's sense
breaks it, because a check that cannot fail is not a check.

**The direction is asserted too, and from the drawing rather than from the script.** The generator's
self-test proves its own arithmetic with a flipped sense; nothing until now connected the *script's*
operator to the kind of pair the drawing holds. `verify-links.py` measures it from the figure: pitch
radii from the tooth circles the generator drew, centre distance from the pivots it placed, so a pair
sits either at R₁+R₂ (external, the pinions turning opposite ways) or at R₁−R₂ (internal, turning the
same way). The hero measures 613.70 = 505.00 + 108.70 and the close 526.28 = 720.00 − 193.72, which is
why the first world's pinions are negated in the script and the second's are not. Flip either sign, or
move either pivot so the pair is neither mesh, and the build fails by name. The witness is a file the
script never writes, so it is a second opinion and not a restatement — and a turn the reader can take to
any angle makes it load-bearing rather than decorative.

**Two pinions ride one wheel, and that is the drawing's choice rather than a claim about the train.**
Nothing on the page says which wheel drives which, the figure carries no title, no caption and
`aria-hidden`, and it is the one place in this artwork that is arranged rather than observed. The
record is in the generator's docstring, which is where this project keeps the things it decided.

The band is cropped, not scaled, below 420px of height: `xMinYMid slice` anchors the crop to the left,
so a 390-wide phone keeps a pinion meshing the rim rather than an empty stretch of arc, and the wheel
reads as a machine at both widths. Measured: the hero is 1,975px tall at 1440 and 2,454 at 390,
the band is 418 and 240 of that, and the band's top edge sits 40px up under the window's bottom edge,
so the two read as one object rather than as a strip below it. The SVG is 2,452 B and it arrives in `index.html`: 91,859 B raw and
23,729 B gzipped, against ceilings of 131,072 and 32,768.

**Why a DOM replica and not a bitmap here.** It is resolution-independent at 959px (sharper than
any capture), it weighs nothing, and — decisively — **it can move**, which is what §1's motion
thesis requires and what no reference can do. The fidelity constraint is absolute: the replica must
match the captures. v1 verified its geometry exactly (`180px 594px 185px` = 959px). **Any
divergence from the captures is a bug, not a design choice.** Fallback if it cannot be made
faithful: `Black/verifiedsource.png`.

### 2.3 The gate — C2

```
   ┌────────────────────────────┐   ╔═════════════════════════╗
   │ It checks what you already  │   ║ ░ field, 696 wide ░     ║
   │ gave it, before it looks    │   ║  ┌───────────────────┐  ║
   │ anywhere else.              │   ║  │  exhibit-10        │  ║
   │                             │   ║  │  600 wide, native  │  ║
   │ Before it answers, Istor    │   ║  └───────────────────┘  ║
   │ decides whether the         │   ║                         ║
   │ documents in your library   │   ║   the "Thoughts ⌄ /     ║
   │ already settle the question │   ║   Drafting the answer"  ║
   │                             │   ║   collapse tells the    ║
   │                             │   ║   story in one glance   ║
   └────────────────────────────┘   ╚═════════════════════════╝
     480px on paper (--col-text)    696px field (--field), 600px window
```

Measured at 1440: the text column is **480** wide at x=100, the field **696** at x=620, and the
exhibit inside it **600**, its file's own width (§3.1). This is the reference pattern for every C2
act below, and the only thing that changes between them is which side the field sits on.

The act's second paragraph is the part worth keeping: Istor runs **two** models, and the small,
heavily instructed one is asked the cheap question first — *is this already in the library?* — so the
large model is only spent when the answer genuinely is not there.

### 2.4 The passage — C2, split, field left, and the page's one interaction

This is a **C2 split like its neighbours, not the band this subsection used to claim** — the page's
only band is act 7. What makes the act load-bearing is **M4, the witness**, the single most
product-specific interaction available (§8.2): on `exhibit-11`, focusing or hovering a citation chip
marks the sentence it supports.

This is v1's own "witness" idea, which v1 then forbade by its no-click rule. It is the one place on
the page where a reader can do what the product does, and the same device the hero's replica has
already taught, so the page's one interaction is introduced before it is explained.

Its second paragraph earns the act: sometimes the answering model writes a good answer and forgets to
cite as it goes, and the page says what happens then rather than pretending it does not.

### 2.5 The reading — C2, split, field right

Act 4's exhibit is **the page's second DOM replica** since 2026-09-20, and it is the same argument
the hero's replica makes: the act's claim is that you watch it read, and a bitmap cannot be watched.
The log is transcribed line for line from the `exhibit-12` capture (Wikipedia on the mechanism and on
the wreck, nature.com, arXiv), including the row where nature.com came back as a refusal — which is
the most product-honest thing either replica shows: the log keeps what actually arrived, and does not
retry until the answer looks tidy. The capture is the source of that copy, not the exhibit: it stays
in the source tree, and its crop line is parked in make-exhibits.py with the reason.

Why the capture could go where the others cannot: the reading log is **text**, so a replica loses
nothing a crop held. It also deletes a phone problem rather than solving it — the capture needed an
art-directed 300px second crop to render the app's text at native size on a phone, and live text
reflows. Eight capture files left the set (185,174 B), and the act's claim stopped being an
illustration of a claim.

### 2.6 The dispute — C2, split, field left, and the page's only portrait exhibit

**The section v1 never had, and the most distinctive content in the whole capture set.**

`Black/Question2.png` is the **"What is Still Disputed" table** — twelve Issue/Status rows, of which
eight read *"The term is debated"*, plus the honest admissions: the exact construction date is
*"Only a range (150–100 BC) is known"*, the gear count *"At least 30"*, the calendar-ring holes
*"354 or 355"*. It closes: *"the precise classification and attribution remain subjects of
scholarly debate."*

An app that **keeps its disagreements instead of smoothing them** is the most credible thing on this
page, it is verified product behaviour, and no competitor page in the genre could copy it. It is
also the honest counterpart to the genre's social-proof slot: it is evidence, and it is the kind of
evidence only this product can offer.

**Portrait, and deliberately the only one.** `exhibit-13` is **430×480** (its file's own size, §6.4)
inside a 600px figure, so the window is taller than it is wide and breaks the page's landscape rhythm
in the one act whose subject is that something does not fit a tidy shape. Tempo uses a phone-shaped
mock for the same reason. It is also the smallest exhibit on the page, which is the trade: a portrait
crop at native scale is narrower than the field it sits in, and the whitespace that leaves is what
makes the act read as quieter than the four around it.

### 2.7 The machine — C3, in one inset field

The privacy claim needs **two** captures and no single one carries it: dark `settingsresearch.png`
shows *"Web research: off"* and *"Scrape (keyless, no service) — No API keys, no third-party search
API"*; light `settingsmodels.png` shows *"Ollama (default) — Local model server"* at
`http://localhost:11434` and the six model roles. The catalogue is explicit: *"Together they cover
the claim; neither alone does."* And they are one dark and one light, which is the diptych's argument
in one glance.

Measured at 1440: the field is **1240** (the full `--page`, not `--field` — this is C3, the inset
field, and it holds both windows in one surface because they are two halves of one claim), with the
two exhibits side by side at **400** and **396**, each at its file's own width rather than stretched
to fill. At 1080px and below the pair stacks instead of shrinking (§7.4 records the same failure mode
elsewhere: a window squeezed until its text is unreadable is worse than a window that moved).

### 2.8 The workspace — C4, the band, and why it is not the three-up

This subsection specified a genre-standard three-up with icons (Gamma, Gemini Notebook) and the build
**rejects it by measurement**, which is the one change here that is a decision rather than a
correction. Both captures are full-window views 1918px wide; halved into two ~470px panels, the app's
own 16–17px text would render at about 8px, which §1's first principle forbids — *legible or absent*.
A three-up has the same problem and adds icons that would have to stand for screens the reader cannot
read.

So act 7 is a **C4 band**: teal, full bleed, heading centred inside the field and the measure held to
`--measure`. Under it, the two windows are stacked at **959** each — full window width — with their
own captions and their own themes, dark (`exhibit-16-library`) then light (`exhibit-17-notes`). The
band is the one act where the interface is the whole argument, and the page gives it the full width
rather than a panel, which is why it is the widest thing on the page after the ring.

### 2.9 The stop — the ring, and the one act with no window

The act the plan never had a subsection for, and the only one whose illustration is **generated from
the product's own answer**: 355 slots on a 4.602px pitch, emitted by `make-calendar-ring.py` rather
than drawn by hand, so the drawing and the number act 10 quotes cannot drift apart. The markup's own
comment calls it *"a quiet act between two loud ones"*, and that is its job in the rhythm: its
neighbours are the teal band above it and the ruler and capture below it, and it is the only act whose
exhibit is line art rather than a window.

Measured at 1440: the `.plate` figure is **1240** wide and the `ring-plate` SVG inside it is **1463**,
that is **118% of the wrap**, pulled 9% past each edge and cropped by `overflow-x: clip` on the
section. So the drawing bleeds off both sides while the copy stays inside a **430px** column that sits
*inside* the arc, which is the one place on the page where type and artwork share the same space.
That column is also where the page's hardest measured clearance lives: the arc's `355` label and the
act's heading collided by 28.1 × 57.8px at 1440, and by more on wider windows, until the gap above the
copy was written as a fraction of the plate rather than a fixed 150px.

The copy is the page's two admissions in bold lead-ins — *"Where it refuses."* and *"Where it
genuinely ends."* — under a heading that names the act: **Where it stops.** The figcaption closes it:
354 and 355 holes are the same ring at this size, *"which is why the app prints both numbers and picks
neither."*

### 2.10 The evidence — the numbers, on paper

The genre has a social-proof slot. We have no users, logos or quotes, and inventing them would break
the page's own rule, so the slot holds **evidence instead of endorsement** (§9) — and every figure is
one the app printed, from a capture on this page.

It is the one act built as a **measure followed by an instrument**: a four-row `<dl>` (354.08 / 68% /
0.028 mm / 4) whose terms are the app's own numbers, then a **confidence ruler**, a 760px two-value
scale showing the fitted 354.08 and the still-possible 355, exposed as `role="img"` with a sentence
rather than as decoration. Then `exhibit-18`, at 600, the capture the first three figures came from.
This act is why the hero's secondary CTA points here: it is the page's promise being checked by its
own numbers, and the check includes the part that is wrong.

### 2.11 Questions — the accordion

One column, `max-width: 46rem`, seven `<details name="questions">` with the first `open`. The `name`
attribute makes it **exclusive** — opening one closes the other, which is the native version of the
genre's FAQ behaviour and needs no script. v1 shipped a plain `<dl>` and defended it in a comment:
*"an accordion would hide precisely the answers this audience came for."* The reversal is argued in
§8.3: the answers are one keystroke away rather than hidden, all five references have one, and
`<details>` works with script off.

The act's first answer is also the one the page's whole claim rests on (*"Does anything leave my
computer?"* — no), so it is the one that arrives already open.

**The boundary plate (2026-09-20).** This act was the last one on the page with **nothing to look
at**: seven disclosures, 323 words, no figure. It is also where four of the seven answers turn out to
be the same answer from four directions — what runs locally, what does not leave, what it needs
installed, and what it cannot do yet — and a drawing of a boundary says that in one look where prose
has to say it four times.

Every label in it is **a phrase these answers already use**: `your library`, `istor`, `ollama or
llama.cpp`, `the model you choose`, `web research`, `off until you turn it on`, `no account, no key`.
Nothing in the plate is new copy and nothing is a claim the act does not make in words a reader can
check, which is the rule the ring and the etymology plate follow too. The claim the figure adds is
structural rather than verbal: the three things run **inside** a hairline rectangle labelled `your
machine`, and the only wire that leaves it is crossed out in `--azure` — the plate's single accent,
on the figure's single assertion.

The act's one paragraph of synthesis above the accordion went with it, and the figcaption came down
to a single line (*"Four of the seven answers below are the same answer, and this is it."*) because
the plate now carries the rest. That sentence is the only part of the idea the drawing cannot show,
which is the division of labour the whole page is built on.

Generated, like the ring and the plate before it: `Source/tools/make-boundary.py` writes three
variants and all three are inlined rather than fetched — `boundary-wide.svg` (704×250, 2,259 B),
`boundary-mid.svg` (576×300, 2,308 B) and `boundary-tall.svg` (340×430, 2,295 B). **Three, and the
third one came out of a measurement rather than a taste call.** The plate's type is in user units, so
it scales with the figure: the wide drawing is 704 units across, and at a 641px viewport its 11.5px
glosses rendered at 9.4 and at 768, a tablet in portrait, at 10.8. The type-floor pass found it (see
§5.1). The fix could not be a font-size step, because the labels sit in boxes sized from their own
measured widths and bigger type would run out of them, and it could not be the tall plate, because a
340-wide drawing in a 720-wide column is a stamp in a field. So the row stays a row and the one part
that needed the wall's flank moves above it: MID keeps the three nodes side by side and puts the
outside stack over the wall, which brings the drawing's own width down to 576 and makes it 1:1 in
the whole band. The swap is at 783 rather than a round number, derived rather than chosen: the wide
drawing is 704 units and the page's gutters are 40 at each side, so 784 is the first window it fits
in at 1:1. The tall plate's type also steps UP in user units (17 and 13.5 against the wide
plate's 15 and 11.5), because a phone column is narrower than the drawing and the rendered size is
what matters.

The three are different diagrams rather than one drawing at three sizes: the stack sits beside the
wall, then above it, then the nodes read downward with the stack still above. All three sit on
`--rule` for the frame and the wire, `--card` inside the boxes, `--ink` for what is named and
`--ink-2` for every gloss, and enter on the standard `.reveal` panel treatment.

**What the first version got wrong, because it is the kind of mistake that ships.** Every node label
was drawn from its box's centre with no anchor set, so the wider of each name/gloss pair ran out
through the right wall of its own box — by 59 units in the wide plate and 60 in the tall one, with
the tall plate's glosses ending at x=326.9 inside a box that stops at 260.4. It survived two passes
because a figure whose text does not line up reads as *loosely typeset*, not as broken, and because
it was checked by looking at a screenshot at a size where the overflow was a few pixels. Three
things came out of finding it:

1. `text-anchor="middle"` is now an **attribute** in the generator. Anchoring is geometry: the box is
   centred on `cx`, so the label has to be, and a stylesheet rule that is missing or renamed should
   not be able to turn that into a defect.
2. **Every string's rendered width is a measured number in the generator** (`MEASURED`, in user units,
   taken off the rendered page with `camera.py measure`). The boxes are sized from those numbers, and
   `tw()` refuses a string that has no measurement, so adding copy without re-measuring fails the build
   instead of quietly drawing outside the box. `node()` refuses a label that does not keep 12 units
   inside its box, and `wide()` refuses a plate too narrow to run the wire outside the row.
3. The generator has a `--self-test` that calls every one of those guards once with an input that has
   to fail **and** once with the shipped layout, because a guard that fires on everything is as
   useless as one that fires on nothing, and only one of the two is easy to notice.

The plate's right margin is exactly 8 units and the wire's stop is **derived from the label stack**
rather than chosen: the plate is the width of its longest string, so the wire yields instead of the
copy running off the plate. That is also why the row keeps 14 units from the boundary's walls rather
than the 24 it started with — every unit of that air was a unit the label stack outside the wall did
not have.

### 2.12 The name — the word at display size, and the descent it carries

`<section class="act act-tight" id="the-name">`, whose 72px block padding is the only tight one on the
page. The heading is not a sentence but **the word being defined, at display size**: the h2 is ἵστωρ.

**The etymology plate (2026-09-20).** The act used to spend a paragraph naming the descent (*weyd-*,
*videre*, *wit*) and the change is a species swap rather than a decoration: a descent is a picture,
and prose is not the instrument for one. The single paragraph that went is the one the plate already
says, so the act's word count fell while the act gained its only visual, which is what the whole page
argues for everywhere else.

This was the last content act with **no figure at all**, on a page whose whole claim is that it shows
rather than tells. Every other act has a capture, a window, a ring or a poster; the act carrying the
brand's own etymology, the one story nobody else can tell, was the one with nothing to look at.

Like the ring, the plate is generated and not authored by hand — `Source/tools/make-etymology.py`
writes `Source/figures/etymology.svg` and `etymology-tall.svg`, and the generator's own docstring
carries the layout argument. Two variants, and the tall one is **not a scaled copy**: the same descent
read downward as a ledger, so a phone gets a composition instead of 5px glosses. That is the same
reason the exhibits art-direct their phone crops, and an SVG does not escape the reason by being
scalable.

The plate hangs on `--field.is-inset` and therefore takes the field's own inks, which the token block
already documents as AA pairs measured against `--field-hi`, the field's lightest stop: `--field-ink-2`
6.07:1 and `--azure-lift` 5.19:1. The structural ink is `--field-ink-2` rather than `--field-rule`,
because `--field-rule` over the field is about 1.3:1 and a rail nobody can see is not a quiet rail.
It carries one accent: the short rule under the word the tool is named after.

The plate enters with the panel treatment every other figure gets (M3's `opacity` and `translateY(24px)
scale(0.97)` on the `.reveal` / `.is-cold` pair), so the motion sits on the figure and never on the act's
prose.

What stays in prose is the turn — *"A witness is not the person who knows most; it is the person who
was there, and can say what they saw."* The brief's requirement is that the name gets a real section,
and it is placed immediately before the poster so the etymology is the last thing read before the mark
is drawn large.

### 2.13 The close — C5, the poster, and the occlusion

`<section class="poster">`, full-bleed teal, built as three layers in a stated order:

  1. **`.poster-mark`** — ἵστωρ at `clamp(72px, 22vw, 220px)`, the page's largest type by a factor of
     more than two over the h1, in `--azure-lift` on the field;
  2. **`.poster-horizon`** — an arc spanning `100vw` whose **apex is the wordmark's baseline**,
     `0.889` of the mark's own box, measured from the font's metric box and holding within a pixel
     from 390 to 1920. Its beads sit among the letters' feet and its arc passes through them, so the
     mark is *occluded* rather than placed on top of the artwork. Under the limb, **three concentric
     plates** (2026-09-20): hole rows at radii −38, −90 and −160 from the limb's, each lower and
     fainter than the one above, one dashed circle each, still all 355. The mechanism's stacked
     plates, as the depth cue both reference closes use (Freebuff's cloud banks, Tempo's
     atmosphere against the limb), in the poster's own material rather than a borrowed landscape;
  3. **the replica window**, then the act's `h2` and CTA, then `.reading`.

**The occlusion is the point, and it inverts the genre.** The reference sites put their artwork in
front of their wordmark; here the product overlaps the brand's lower third, so the mark passes behind
the window and stays half-visible — which is what *"it shows you what it saw"* means when the product
is the thing doing the showing. Everything readable or clickable is lifted above both layers, which is
a correctness requirement rather than a style: a positioned sibling paints over an unpositioned one,
and the footer's links would have disappeared.

Below it, `.reading`: three columns of four pages each, drawn from the 75-page carried library, with a
lede naming the count and a link to the directory. The markup's comment is the rule — *"a footer that
lists everything is a sitemap, and the author of a sitemap is a crawler. These are the sixteen this
page would hand to someone who had just read it."* The close merges v1's "the name" section with the
poster move, which is where it belongs.

---

## §3 · Composition system

### 3.1 The grid

All widths derive from one measured fact: **every capture is 1918px wide and is a 2× capture of a
959 CSS-px window.** So:

| Token | Value | Derivation |
|---|---|---|
| `--win-sm` | **600px** | crop ÷ 2 — the pane exhibits, at native app scale |
| `--win-lg` | **959px** | crop ÷ 2 — the full-window exhibits, and the replica |
| `--field-pad` | **48px** | inside a field, and between the pair's two windows |
| `--field` | **696px** | `--win-sm` + 2 × `--field-pad` |
| `--col-text` | **480px** | the C2 text column |
| `--gap` | **40px** | between the text column and the field |
| `--page` | **1240px** | genre range 1150–1300 |
| `--nav-h` | **68px** | the bar's height, and how far the hero is pulled under it |
| `--measure` | **66ch** | kept from v1; correct typography, not a style |
| `--gutter` | `clamp(20px, 5vw, 40px)` | |

This table used to read `--win` 959, `--field-pad` 64 and `--field` 1087. Those three numbers agree
with each other and with nothing else: 1087 is 959 + 128, which is the derivation you get by putting a
*full-window* exhibit inside a field, and no field on this page holds one. There is no bare `--win`
token; the pair is `--win-sm` for the panes and `--win-lg` for the windows, because they are two
different crops and a single name would invite exactly that substitution.

**The consequence is the most useful number in this plan.** An exhibit displayed at exactly
`crop_px ÷ 2` is **pixel-perfect at both 1× and 2× DPR, with no upscaling** — because the source is
a 2× capture. Legibility is preserved too: at that display width the app's own 16–17px text renders
at its true size. Every exhibit in Appendix A is sized this way. It is why v2 needs no new captures
to look right, and why its weight lands far below the genre (§12).

### 3.2 The five compositions

Each entry carries the boxes, measured at 1440 off the built page, so that the definition and the
page can be compared without opening either.

**C1 · field-full** — full-bleed teal; heading, subhead and CTA centred; the replica at `--win-lg`
(**959**) centred, 48px field padding inside. Used by the hero only. Its left rail is a real in-page
navigation (§2.2), which makes C1 the one composition with a second interactive layer inside it.

**C2 · split** — paper ground; text column **480** at x=100 beside an inset teal field **696**
(`--field` = `--win-sm` + 2 × `--field-pad`) holding a **600** window. Measured: the field sits at
x=620 in acts 2 and 4 and at x=100 in acts 3 and 5, and the side is the only thing that differs
between them. `is-flip` moves the field to column 1, so the side is content rather than a second class
name to keep in sync.

**C3 · diptych** — paper ground holding one inset teal field the full `--page` (**1240**) wide, with
two windows side by side at **400** and **396**, each at its file's own width rather than stretched to
a common number. One field, not two: the two captures are two halves of one claim. The pair stacks
below 1080px.

**C4 · band** — full-bleed teal; heading centred inside the field on the measure, at 88px of block
padding; then windows at `--win-lg` (**959**). Act 7 is the band, and it carries **two** of them,
stacked, each with its own caption and its own theme, because both are full-window captures: halved
into a side-by-side pair, the app's 16–17px text would render at about 8px (§2.8).

**C5 · poster** — full-bleed teal; three layers in a stated order: the giant wordmark
(`clamp(72px, 22vw, 220px)`) at the back, then a `100vw` horizon arc whose apex is the mark's
baseline at `0.889` of its own box, occluding the letters' feet, then the replica window and the
reading columns in front of both. The mark stays half-visible, which is the difference between an
occlusion and a cover (§2.13).

### 3.3 Radius, shadow, hairlines

The report ranks these **#1–#3 of the cheap, load-bearing signals** — and notes the shadow is
*"the single difference between 'a screenshot pasted on a page' and 'an object sitting on a
surface'."* All five references have it. v1 had none of the three.

| Token | Value | Source |
|---|---|---|
| `--r-field` | **28px** | Tempo's measured field radius |
| `--r-win` | **18px** | genre 17–22px |
| `--r-chip` | **10px** | genre 8–12px |
| `--r-cite` | **6px** | the app's own measured chip radius (5–6px) |
| `--shadow-field` | `0 24px 60px rgb(4 10 12 / .45)` | Breezy measured: ~9% darkening decaying over ≈50px CSS |
| `--shadow-paper` | `0 18px 44px rgb(16 24 27 / .14)` | the same effect retuned, because a shadow that dark over paper reads as a hole |
| `--rule` | `#E4E6E9` | measured: the app's light table separator |
| `--field-rule` | `rgb(255 255 255 / .10)` | 1px hairlines separating dark from dark |

**Hairlines are 1px, never heavy strokes.** Freebuff and Tempo separate black-on-black with a
hairline plus a 4% card lift. Nothing on this page uses a border thicker than 1px except the field
edge, which is a seam rather than a stroke.

### 3.4 The theme rule

This section used to state a rule and reason from it: *"light-theme windows stand on teal fields,
dark-theme windows stand on paper"*, therefore *"the window always contrasts its ground, so it always
reads as an object."* **The premise is false on the built page and the conclusion does not follow.**
Sampled from each exhibit's own title-bar pixels against the ground it stands on, six of the nine are
**dark windows on the teal field** — 10, 11, 12, 13, 14 and 16 — at **1.10 to 1.15:1**, which is no
contrast at all; the light pair (15 and 17) carry the contrast the old rule described, at 13.2:1 and
16.3:1.

> **The rule that holds is about the separator, not the theme.**

A window on a field is separated by the 1px `--field-rule` seam with `--shadow-field` under it; a
window on paper is separated by `--shadow-paper`. That is Tempo's measured technique (§3.3), and it is
the reason a near-black window can stand on a near-black ground and still read as an object. The
theme of each capture is whatever the app was in when it was taken, and the page does not recolour
evidence to fit a rule, so the pairing is a fact about the captures rather than a specification.

What must hold is that **every window carries the separator its ground calls for**, and that is now
measured rather than assumed. `audit-contrast.py` walks every window on every page, finds the ground by
walking the cascade for the first opaque background — not by looking for `.field`, which is the mistake
this section made — and compares the computed border and shadow against the tokens. Measured on the
built page: **11 windows, 10 on a dark ground and 1 on paper, 0 failures.** Two mutations are shown
failing: taking the seam off `.field .exhibit img` reports **8** windows without one, and giving the
paper window a seam reports **1**. The ground is found by luminance rather than by class for a reason:
a new dark band whose window never got a seam has to fail here rather than ship, which is exactly what
the old rule would have allowed.

### 3.5 The library's theme control

The 75 carried pages follow the reader's operating system and have done since they were built, and
`styles.css` has carried `.theme-toggle`, `.icon-sun` and `.icon-moon` rules the whole time. What
was missing was anything that *writes* a choice, so the explicit preference the stylesheet already
has a rule for ("an explicit light choice still wins over the media query") was unreachable. The
header now carries that control, and it writes the same `istor.site.theme` key the inline stamp
reads before first paint, so a choice survives the next page and never flashes.

It is one shared `/theme.js` rather than a script in each page, and the button is 143 B of markup
plus 44 B of script tag: **187 B per page, 14,025 B across the library**, asserted exactly. The
button is authored `hidden` and revealed by the script, so a reader whose scripting is blocked gets
the page they always had instead of a control that cannot act. Its two icons are Lucide's sun and
crescent carried as CSS masks rather than as inline SVG, because the same two glyphs written into 75
headers would be 24 KB for 16px of drawing. Contrast is measured on both grounds at the button's
own hover: 5.36:1 and 5.14:1 on the light grounds, 7.70:1 and 7.17:1 on the dark ones. Verified in a
browser rather than argued: a click on a machine set to dark stores `light`, and the next library
page arrives light.

### 3.6 The reader's own settings: print, and more contrast

Two promises a stylesheet makes to a reader nobody sees, and both failed silently
until this section existed.

**Print.** The library honoured `prefers-color-scheme: dark` and the landing page
has no dark theme at all, and both printed the same way: a dark system put near-white
ink on paper. Measured before the fix, by asking a browser what it would paint: 13 of
46 text elements on `/what-is-a-local-llm/`, and 17 of 185 on the home page,
resolved to ink above 0.55 luminance on a sheet that prints at 1.0. The landing page
needed no dark system for that, because its closing acts set `--field-ink` on deep
teal grounds and Chrome does not print backgrounds.

Each half now gets its own print token world: ink to `#000000`, the secondary inks
to printable greys, the accents to a printable blue and red, and the field inks down
to paper ink. `:root[data-theme]` is listed explicitly so a reader who chose a theme
in the header is printed on paper rather than in their choice. The two `--on-*` inks
are the exception that proves the rule about grounds: a control's ink was chosen
against its fill, so `.cta`, `.chip`, `.cite-btn` and the like carry
`print-color-adjust: exact` and keep the one small fill that has to survive. `.win`
keeps its own token block, so the replica answers with the **light** replica that
already exists as a designed object (§3.4). A link whose only life was to be clicked
prints its address after it, and internal links deliberately do not, because seventy
internal URLs under seventy internal links is noise on paper.

**More contrast.** The library has honoured `prefers-contrast: more` since it was
built and the landing page did not, which is an odd thing for one site to disagree
with itself about. Its `--ink-2` goes 5.71:1 to **9.41:1** on `--paper` and
`--ink-3`, which draws the rail and the scrollbar, goes 3.12:1 to **7.80:1**; the
field's secondary ink goes 6.07:1 to 9.20:1 on `--field-hi`. Those four pairs were
9.8:1 and 8.4:1 and 5.66:1 until the audit learned to emulate the state and measured
it (§12, the audit note): the first two were white-ground numbers, and the third
contradicted the token block that had it right.

Both are asserted rather than trusted. `verify-links.py` requires a block of each
kind in both halves, computes every text ink the print world declares against white
paper (worst 9.08:1), and every rule token too (worst 3.45:1). Six of its 51
assertions are these, and a seventh is the directory's keyboard (§3.8): the page tells
its reader in visible copy that `/` focuses the field and the arrow keys walk the
matches, which is a promise about behaviour and therefore the one kind the copy gate
cannot see. The contrast promise is the one that a verifier cannot fully
reach, because asserting a block exists is not the same as measuring it, which is
why the state is now emulated and measured by hand at §12.

### 3.7 Continue reading

Seventy-five articles, a generated directory, and until now nothing joining one article to the next:
a reader who arrived at "What is a local LLM?" from a search result finished it and met a footer of
six site-wide links. The library is the site's substance and every page in it was a dead end, which
is the one navigational thing every documentation library a reader has used gets right.

Every carried page now ends with a **previous** and a **next** neighbour, written by
`Source/tools/add-article-nav.py`, which imports `make-library-index.py`'s own `GROUPS` rule: the
walk a reader can take **is** the order the directory shows, and a page added tomorrow joins it by
matching a slug prefix like every other page. The walk is continuous across groups, and the small
uppercase line above each title names the group the neighbour is in, so crossing from the vocabulary
pages into the how-it-works pages is announced rather than silent. Two links at most; the first and
last page of the walk carry one each.

The pair is **written into `OldVersion/`, not injected by the build**, because `copy_library` is
documented as zero rewrites and that is worth keeping: the library is carried, not re-rendered, so
what a reader gets is the file a reviewer read. `rel="next"` and `rel="prev"` carry the same
relationship to a machine that the two links carry to an eye.

It costs **~431 B per page, 32,328 B across the library**, and it is asserted as a **walk** rather
than sampled: `verify-links.py` follows the links from the one page with no previous, requires that
they reach all 75 exactly once, and then follows them backwards from the end, because a broken
`prev` is invisible to a next-only check. Removing one pair makes that assertion fail with the
instruction to re-run the tool. That assertion is 1 of the 60 the link gate now carries.

### 3.8 The directory answers the keyboard

The directory lists all 75 pages and has had a find field since §3.6's night. What it did not have
was a keyboard path: a reader arriving from an article had to find the field with the mouse, and a
reader who filtered to three entries had to Tab into the list. So the page now teaches one gesture
and honours four. **`/` focuses the field** from anywhere on the page, unless the reader is already
typing. **The arrow keys walk the matches**, and each step moves *real focus* onto the entry's own
link rather than a decorative highlight: the reader's screen reader announces the page title as they
arrive, Enter activates it natively, and no ARIA listbox has to be layered over a list of links.
Down and Up are each other's inverse and the walk closes field-to-field, so a reader who overshoots
presses the other arrow instead of hunting for the way back. **Typing while a row has focus** puts the
character in the field and continues from there, which is what the reader was doing before they
walked away. **Escape** clears, and a second Escape leaves the field.

One thing was built and then removed: focusing the field when a URL arrives with `#find`. The footer
of every article links to `/library/` and not to a fragment, so nothing would ever have sent a reader
there, and a behaviour nothing triggers is worse than no behaviour at all. The visible hint is what
teaches the shortcut, which is the honest way for a page to say it is keyboard-ready.

The picked row is marked with a **rule drawn inside the row**, not a tint behind it, and that is a
measurement rather than a preference. An index entry's title is `--cite-ink` at 5.41:1 on the light
paper and its summary is `--mist` at 5.1:1: two passes with about half a step of margin. A `--witness`
tint darkens the ground under both and spends that margin, measured on the row itself: **8% costs 0.6**
and leaves the title at 4.78:1, and **12% leaves it at 4.50:1**, which is the bar for 16px type to the
second decimal. Both tints pass, so the tint was not a bug; it was a focus state spending a page's
whole contrast margin to say something a graphic says for nothing.

It costs **2,841 B of index and 1,614 B of stylesheet** (30,679 → 33,520 and 46,801 → 48,415), a
third of the index half being the comment that ships beside the script. It is asserted by name:
`verify-links.py` requires the three key names the hint teaches to appear in the page's own script,
because that hint is visible copy and the copy gate reads text rather than behaviour. Breaking the
walk in a copy of the artifact fails with `the hint promises ArrowUp and the script does not handle
it`, which is the sentence the check exists to print.

---

### 3.9 The directory carries its own map

Seventy-five entries in seven groups, and **forty of them are one group**. A reader who wants
*Compared with other tools* scrolls past all of it, and a reader scrolling through it has nothing on
screen that says which group they are still in. Two moves fix both, and neither is a new control.

The **jump row** is seven fragments, one per group, under the find field. It is static markup with
static links, so it works with no script at all, which matters here because everything else about the
page's navigation is scripted: the row is what a reader whose script never ran gets instead. The
script hides it while a query is live, because a link to a group the filter has just emptied is not
navigation, and the row's order is by group size descending, so the group a reader is most likely to
want to leave is the first chip.

The **group heading pins** to the top of the viewport while its own group is on screen. Sticky, not
fixed: it leaves when its group does, so the heading on screen is always the group the reader is
actually in. It carries an opaque ground and a hairline at its lower edge, and both are the
measurement rather than the decoration: with a transparent ground the entries scroll through the
heading, and with an opaque ground and no edge the entry underneath is cut through the middle of a
line, which reads as a rendering fault rather than as a bar. The first version had the ground and no
edge, and it took a screenshot of an entry sliding under it to say so. The 1px rule is the same
device the reference sites use to separate black from black.

Both are asserted by name in the link gate's 12th check, four assertions over two files, because
three of the four claims cannot be seen by reading one of them: the row names **every group its own
headings name and nothing else** (the two lists are built from one another by the generator, which is
exactly the coupling that survives a refactor in one of them); the row is **authored visible**, since
it is the no-script path and the way that fails is somebody adding `hidden` beside the find field's;
the pinned heading **declares a ground**; and the row is **listed as furniture in the print block**,
because a sheet of paper cannot use a fragment link. All four were shown failing before they were
trusted.

## §4 · Colour

Anchored in measurement at both ends — the brand's locked assets, and the app's own sampled palette.

| Token | Value | Where it comes from |
|---|---|---|
| `--paper` | `#FAFAFA` | **measured** — the app's own light rail |
| `--card` | `#FFFFFF` | measured — the app's light modal |
| `--ink` | `#16181B` | measured — the app's light body text |
| `--ink-2` | `#5F646B` | secondary; ≥4.5:1 on paper |
| `--ink-3` | `#8A8F96` | labels, captions |
| `--azure` | **`#0066CC`** | **measured** — the app's light accent, *and* brand step 1 |
| `--azure-lift` | **`#4DA3FF`** | brand step 2 — azure as it must appear on teal |
| `--azure-deep` | `#0073E6` | brand step 3 |
| `--coral` | `#C7292A` | the mark's artwork; the app's "unverified" warning |

**The teal field** — the og-card's measured radial, as a CSS gradient:

```css
--field-bg: radial-gradient(130% 120% at 78% 14%,
              #163234 0%, #11282B 34%, #0F2024 62%, #0E1E22 86%, #0C1B1E 100%);
--field-ink: #E9EDF0;          /* text in the field */
--field-ink-2: #9FB0B4;        /* secondary text in the field */
```

Stops are the four measured samples in their measured positions (brightest at x85 y15 → the
gradient's origin at 78% 14%; edges `#0E1E22`; a darker `#0C1B1E` only at the outermost falloff so
the field does not band at large sizes).

**Azure is the only interactive colour — in both themes.** The catalogue confirms the app holds to
this (*"No second accent exists in either theme"*), and the report ranks *"one accent colour used on
under 5% of pixels"* **#4**. Azure therefore appears on: the nav pill, the hero CTA, links, the
citation highlight, and the close's re-ink. **Nothing else, anywhere.**

**Coral keeps its single job** — the mark's artwork and the "unverified" state. It is not a second
accent and must not become one.

**No invented colour.** Every value above is either a locked brand asset or sampled from the app.
This is the discipline that makes §1's claim — *the look costs no invention* — true rather than
rhetorical.

---

## §5 · Type

Two faces, as v1 established, plus the wordmark subset. **Nothing changes about which faces; what
changes is the scale.**

- **Display: GFS Didot** (Latin subset). **Weight is not available — Regular only.** So emphasis is
  carried by *size, tracking and the field*, never by weight. This is a real constraint and the
  plan treats it as one: no bold display anywhere.
- **Body/UI: Inter** (variable).
- **The wordmark: `istor-wordmark.woff2`** — the Greek subset (16 codepoints). Used as live text in
  the nav, the field headers, and the close.

### 5.1 The scale, and the ratio that matters

The report's #11: *"make the biggest type much bigger, and use it once."* Gemini Notebook runs 6.4×
with its 90px size used for **exactly two words**; Gamma 5.3×, used once. **Breezy (3.1×) and
Freebuff (3.0×) are the two that feel most web-default.** v1 topped out at 68px used repeatedly.

| Token | Value | Use |
|---|---|---|
| `--t-label` | 13px | nav, captions, table labels |
| `--t-sm` | 15px | figcaptions, secondary |
| `--t-body` | **17px** | body |
| `--t-lede` | 21px | hero subhead, section intros |
| `--t-h3` | 26px | **unused.** Sized for the three-up heads that §2.8 rejects, and every `h3` on the page is a `.reading-head` at `--t-sm` |
| `--t-h2` | **34px** | section headings (genre 25–31) |
| `--t-display` | **`clamp(56px, 7.4vw, 94px)`** | **used exactly once — the hero** |

**And a floor under the bottom of it: nothing a reader has to read renders under 11px, at any width
from 320 to 1440.** That is not a WCAG number — WCAG sets a contrast ratio, not a size — it is this
site's own, and it is a rule about *rendered* pixels rather than declared sizes, which is what made it
worth measuring. Every figure on this page draws its type in user units inside an SVG, so the type
scales with the figure and its rendered size is a different number at every width; nothing had ever
measured that, and the first sweep found the site's smallest text at **7.66px**: the ring's `355`
label in a 390px window, where the plate renders at 0.589 of its units. It also found the boundary
plate's glosses at **9.0-10.8px** between 641 and 768 and the etymology ledger's at **9.8px** at 320.
All three are fixed — the ring's label steps up in user units below 560, the boundary plate gained a
third composition for the middle band, and the etymology's gloss column steps and shifts at 430 — and
`audit-contrast.py`'s type-floor pass asserts the floor at 13 widths now, so the class of defect is
measured rather than remembered. 6,489 texts, smallest 11.12px. The pass prints the size it found and
the count it measured, because its first version was written against the audit harness's own document
instead of the framed page and reported a clean pass over zero texts.

**Display ÷ body = 94 ÷ 17 = 5.5×.** In the genre's top tier, and reached by *raising the top*, not
by shrinking the body.

**That ratio was true at one width, and this table was right about the token while the stylesheet was
not.** `--t-display` was declared a second time inside `@media (max-width: 1080px)` as
`clamp(44px, 9vw, 62px)` — a different ladder for the same value, and the two disagreed at the
breakpoint by 27px, so the headline *popped* from 88.8px at 1200 to 62px at 1024 rather than stepping.
Measured against the 17px body, the step the report's #11 is about was 5.53× at 1440, 3.65× at 1024,
3.18× at 600 and **2.59× at 390** — under both sites the report calls web-default. The override is
gone and the single ladder above serves every width; it is continuous across 1080 (7.4vw of 1080 is
79.9), the desktop value is untouched at 94px, and the floor is 56px, which is 3.29×. The phone hero
was the case that decided it: at 44px the h1 was barely larger than the 21px lede beneath it, and a
type scale that stops outranking its own subhead on the screen most readers use is not a scale. That
the media query still does its actual job — scaling the page's furniture (field padding, act rhythm,
collapsed columns) rather than its type — is the reason deleting one declaration was the whole fix
rather than re-tuning a second clamp against the breakpoint that caused this.

### 5.2 Leading, tracking, measure

| | Value | Source |
|---|---|---|
| Display leading | **1.06** | Breezy measured ≈1.08; the report calls tight leading part of why type "looks typeset rather than default" |
| Body leading | **1.55** | **the app's own** answer-body leading, measured from the captures |
| Display tracking | `-0.02em` | since weight is unavailable, tracking does that work |
| Measure | **66ch** | kept |

---

## §6 · Imagery

### 6.1 The exhibition rule

> **Every exhibit shows the app doing the thing the section claims.**

Not a decorative screenshot. The gate section shows the gate; the reading section shows it reading;
the dispute section shows a disagreement kept. This is what makes the imagery *evidence* — and the
report's #15 is explicit that the tell of a bad page in this genre is *"half-legible fake text"*.
Every exhibit is a real capture of the real app on a real session, at its native resolution.

### 6.2 The exhibits

Full geometry in **Appendix A**. Nine exhibits: eight derived from captures in the 36, each cropped
so its display width is exactly `crop_px ÷ 2` (§3.1), and one built as DOM because its subject is
text and its act's claim is that you watch it happen.

| id | Proves | Source |
|---|---|---|
| `exhibit-10` | it answers from what you gave it | `Black/Question1.png` |
| `exhibit-11` | every claim points at a passage | `Black/verifiedsource.png` |
| `exhibit-12` | you can watch it decide | **DOM replica** — the log transcribed from `Black/FetchingPages.png` |
| `exhibit-13` | it keeps the disagreements | **DOM replica** (2026-09-21) — the table transcribed from `Black/Question2.png`; crop line parked in make-exhibits.py |
| `exhibit-14` | no network, no keys | `Black/settingsresearch.png` |
| `exhibit-15` | it runs on your machine | `White/settingsmodels.png` |
| `exhibit-16` | the library | `Black/Sourcesfullscreenmain.png` |
| `exhibit-17` | the notes | `White/notesfullscreenmain.png` |
| `exhibit-18` | the precision it reasoned to | `Black/Question3.png` |
| *hero* | the whole loop | **DOM replica** — not a bitmap |

### 6.3 Four captures must not ship

The catalogue flags them and this plan repeats it as a hard rule. `Black/verifiedsource1.png`,
`White/verifiedsource.png`, `White/verifiedsource2.png` and `White/Question1.png` **all have
expanded citation labels overprinting the answer body.** `Black/Thinking.png` and
`White/Answering.png` are effectively blank. None of these six ships.

*(The clean chip exists; the clean **expanded** chip does not — which is why §8.2's witness is built
from the DOM replica and the clean `verifiedsource.png`, not from a capture of an expansion.)*

### 6.4 Cropping, and who does it

Captures are **source material**. Crop bounds come from `.improvement/assets/CATALOGUE.md` §3 and are
measured **per file** — the catalogue's own warning is that *"the split is not constant"* (the
composer measures 399–1443, 399–1394 and 539–1310 across three files). The three-pane captures have
their own split (≈0–490 / 490–1410 / 1410–1918) and must not use the default.

Every crop is polished: tightened to remove dead space, because *"tighter is always stronger"* — the
rails carry no story, and the centre column is the image.

### 6.5 Formats, and the bug that would have squashed every one of them

Ship **AVIF + WebP**, 1× and 2×. PNG is dropped from the shipped set for v2: the genre's payloads
are 2.12–13.80 MB largely because they ship JPEG/PNG, and AVIF over flat UI is dramatically
smaller. The `<picture>` keeps `width`/`height` attributes so layout never shifts.

> **Correction carried from v1 — root-caused 2026-09-19.** v1's `exhibit-07` rendered **594×231**
> against a natural **941×231**: horizontally squashed to 0.631 while vertical stayed 1.0. Cause:
> the global rule is `img, svg, picture { display: block; max-width: 100% }` and **`height: auto`
> appears nowhere in the stylesheet except `.plate > svg`.** The `<img>` carries
> `width="941" height="231"`, so in a 594px column the width clamped and the height attribute held.
> Exhibits 08 (181px) and 09 (420px) fit their columns, which is why only one image was distorted —
> and why this would have silently squashed **every wide exhibit in v2**. Fix is one declaration:
> `height: auto` on the global rule.

---

## §7 · Motion

**No animation library.** The report verified zero requests for GSAP, ScrollTrigger, Lenis,
Locomotive, AOS, ScrollMagic, Framer Motion or Swiper **across all five references**. Everything
below is CSS plus one small `IntersectionObserver`. The budget this section carried, **≤ 4 KB of
shipped JS**, is now measured rather than remembered: `document.inline_js_bytes` in
`Source/tools/budget.json`, asserted by `verify-budget.py`. It read 5,599 B on 2026-09-19, of which
1,250 B was prose in `//` comments that shipped to every visitor and was parsed as script; that prose
moved into the note above the script, which the build strips. 5,010 B remained at that point, and the
overage over the ≤ 4 KB sentence is code for jobs this table did not have when the sentence was
written: the rail's current-section tracking (M1c), the close's parallax (M6), the hero's own controls
(M9), the act index's echo (M11), the reading log's stagger (M13) and the hero's mechanism (M14).
**Re-measured 2026-09-20: 8,596 B, the only place in this project where a number has grown without a
ceiling being re-derived, and it is recorded rather than smoothed: the ceiling (16,384 B) has been
catching growth rather than holding a measurement.**

**2026-09-21: the ceiling caught it, and the diagnosis was the one this section had already made
once.** By the night's end the shipped script measured **16,117 B against the 16,384 B ceiling — 267 B
of headroom — and 7,144 B of those bytes were whole-line `//` comments**: prose parsed as script on
every phone, in the exact channel that had produced the 1,250 B the note above the script was written
about. The rule was applied to the prose that existed then and not to the prose added since. The fix is
the third instance of an existing one: `inline_js()` in `build-site.py` strips whole-line comments on
the way in, as `inline_css()` strips the stylesheet's and `inline_markup()` the markup's, with the same
contract asserted on its own output and a second, independent line-filter implementation required to
agree with the regex before the build proceeds. Shipped script: **12,671 B of behavior**, ceiling
unchanged at 16,384 B — it was never the problem, and behavior that doubles still trips it. Momentum
for the hero's mechanism (M18) then fit under it, which is the point of a ceiling: it made the prose
question unavoidable instead of deferring it by 267 B.

**2026-09-21, later the same night: the strip paid for behavior rather than deferring it.** M18's
generalization into one factory serving both worlds, and M19's flywheel, brought the shipped script to
**14,919 B — 1,465 B under the 16,384 B ceiling** (14,482 B before M20, +437 B of shipped behavior and
no prose; 14,351 B before the charge gained its boundary) — so the growth this time was a feature bought with
prose that had been arriving on every phone to do nothing. The measured behavior behind M19, taken in
the browser rather than asserted at the time: a sustained throw charges the wheel and it coasts on past
the gesture before settling, a notched mouse-wheel read moves the wheel to *exactly* the position's
angle (0.00° of drift), and the pinion's ratio held at −4.6458 through the whole coast. Those figures
are asserted now, and the asserted ones are 14.1° charged and a further 14.4° of coast.

**2026-09-21, last: the momentum's three constants are named once, the notes are checked against them,
and the cap is held under a tooth.** `SPIN_CAP`, `SPIN_HALF = 160`, `SPIN_MIN = 1.5` now sit in one
place, read by the hand, the release and the flywheel, because three inputs writing their own literals
is how one of them gets tuned alone. The cap itself is **96 deg/s**, and that number came from the
drawing rather than from taste: 96/60 = 1.60° a frame at 60Hz against the great wheel's **1.614°**
tooth pitch (360/223), so the fastest this wheel is ever allowed to turn is **one tooth a frame**. The
cap was 200 until that was measured — 3.33° a frame, 2.1 pitches, a dashed tooth ring that aliased
into a strobe on **18% of the frames** of an extreme throw, which on a page whose subject is a toothed
mechanism is a false statement rather than a smoother animation. The pinion needs no number of its own:
a meshed pair advances the *same* count of teeth, so the pinion's 7.4° a frame against its 7.5° pitch
(360/48) is the same inequality, and the gate states it once.

The link gate recomputes what the notes claim from those constants — the flick's sweep (v₀h/ln2 =
**22.2°**, and the note says about 22), the settling time (96 → 1.5 deg/s at a 160 ms half-life is
**0.96 s**; the notes said "under a second" at the old cap when the arithmetic gave 1.13 s, which is
what the clause was written after), both angle mappings (80/10 = 8°, 10/10 = 1°), and now the cap
against the **tooth count the drawing declares**, read from the built page rather than from a note.
**88 assertions now**, and the clause was proven failable in twelve dimensions before it shipped: a
tuned cap, a tuned half-life, an inflated sweep, the old settling wording, a changed mapping, a bare
literal beside a named constant, a deleted note, the old cap restored, a cap one pitch past the limit,
a wheel regenerated to a different count, and a tooth count removed from either world, each failing by
name with the mismatch in the message.

**Testing the flywheel turned up a design flaw rather than a code one.** Speed measured *per event*
cannot tell a flick from a teleport: a mouse wheel hands over its whole 100px notch as one event, and so
does a PageDown, and so does a browser that coalesced several scrolls into a single delivery, and each
of those read as a fast gesture while the reader was making none. The first gate to be written read an
instantaneous speed and charged every one of them; the second decayed the speed by elapsed time, which
still charged a single 500px delivery. The third reads the speed over a **window of real time** and
requires **continued motion** in it: three samples spanning at least 60ms inside a 150ms window, so
only a stream of events (a trackpad flick, a wheel thrown hard) sustains, while a notch, a key or a
coalesced jump fails the test. The measured behaviour, driven through the handler with controlled
timings because this machine's compositor coalesces and stalls scroll events: a notched read of 600px
and two page-sized jumps move the wheel **0.00° beyond the position's angle**, and a sustained flick
charges ~10° and coasts, with the pinion's ratio held at −4.6458 at every sample. The gate fails in the
safe direction, which is the property worth naming: when the input is ambiguous the wheel is calm.
Writing it also caught a bug in its own window: trimming samples by count kept one old enough to belong
to a different gesture under the window's floor, and two page-sized jumps 400ms apart read as
1.75 px/ms of continued motion and charged 11°.

**The charge has a boundary, and the boundary was measured.** What a *session* does to the wheel is a
different question from what a gesture does to it, and a probe answered it: 24 sustained gestures down
the page left the wheel **484° from where its own scroll position says it should be**, 1.3 turns of
rotation. That is not extra motion but a **wrong statement** — the wheel is the reader's position on a
world, and past the hero the reader was looking at prose while the thing accumulated. Worse, it
accumulated *invisibly*: none of those eighteen gestures happened while the mechanism was on screen,
so the reader who scrolled back up found a wheel offset by turns for no reason they could have seen.
The flywheel now charges only while the world is on screen, `window.scrollY < heroBottom` — the same
measurement M14's mapping already reads, so it costs nothing — and the wheel is charged where it can be
watched being charged. Accumulation itself stays permanent, as the hand's is: a wheel keeps the rotation
it was given; what stops is being charged for gestures made somewhere else. The close stays out of it
entirely (M14b's ending is a settling). The motion audit asserts the pair directly: the same
gesture that charges **14.1°** at the hero charges **0.000°** 3,775px down.

**2026-09-21, last of the night: the arrivals keep the reader's own clock (M20).** The wheel became
pace-aware in M19 and every other arrival on the page was still timed for a reader who had stopped to
look. The numbers make that concrete: the plate's sequence runs **2s**, the reading log's counter
finishes **720 ms** after its block arrives, the windows take **700 ms** to land. At the **1.25 px/ms**
a flick sustains, two seconds is **2,500 px** of travel, so the sequence finishes four screens below
the reader and what crosses the viewport is its middle. The reference finding that started M19 says the
same thing from the other side: the best sites treat pace as a signal, an abbreviated entrance for the
fast scroll and the full one for the slow read.

The mechanism is one number, and that is the design: `--arrive` is declared at `:root` as **1** and
overridden to **0.3** on a block the script marks `is-quick`, and every duration, delay and stagger in
the arrival family is written as a multiple of it. Multiplication is why this is safe rather than
merely convenient: scaling a whole family by one factor cannot reorder it, so the frames still draw
before the holes roll and the tick still lands after its row, and the content is never paced at all.
The decision test is the inequality rather than a threshold anyone liked: the arrival runs `ARRIVE_MS`,
so a reader at `pace` px/ms covers `pace × ARRIVE_MS` in that time, and if that is further than the
screen the arrival ends off it (&gt;1.25 px/ms at 900px). The speed comes from the *same* sample buffer
the flywheel reads, because a reader's pace is already measured here once; the difference is the
question, not the data: the wheel asks whether the reader made a gesture (a teleport must not charge
it) while the arrivals ask only how fast the page is moving.

Measured by driving both paths, since a reveal fires once and one page load cannot be asked for both:
the same block arrives with `--arrive: 1` and **480 ms** rows when approached slowly, `is-quick` and
**0.3** / **144 ms** when flicked at, and the counter's own writes land **140 ms** apart slowly against
**40 ms** fast - the counter reading the property back rather than repeating 0.3, which is the one
number in the feature that could have been copied. The end state is identical on both paths (count,
row opacities, tick opacities), which is the claim the feature has to earn rather than a nice property
it happens to have.

The audit is **18 claims** now, and the shape of the change is checked statically in `verify-links.py`
(88 assertions): the `:root` default exists because an undefined custom property inside `calc()` is
invalid at computed-value time, which means *no* transition rather than a short one; six named timings
must each still read the clock, since a rule left with a bare duration animates correctly and simply
stops being paced; and the script must read the property rather than multiplying by 0.3 beside it. Ten
doctored pages prove the whole thing failable, including the first bug this feature shipped with for
one build - px per millisecond divided by 1000 as if it were px per second, which made the entire
feature dead code that looked alive.

**2026-09-21, the same morning: the library's blocks arrive too (M21).** M20 gave the landing's
arrivals the reader's own clock and left the other 78 documents strictly position-driven: their
figures and index groups appeared when they crossed the fold, at whatever speed the reader crossed
it. What the library was missing was not the animation. `.enter` and `.reveal` had been in its
stylesheet since it was written, with a comment claiming the element was authored visible and the
script switched the hidden state on - and the code did the opposite: the base rules *were* the hidden
state, no script ever existed, and the classes could not be triggered by anything. The fix is the
smallest one that makes the comment true: the stylesheet's base rules become the finished page, the
shared script adds `is-cold` to a block only when it sits below the fold at the moment the script
runs, and the same `--arrive` multiplier M20 multiplies through the landing's family now multiplies
through the library's. The fold test is why this is safe for a reader whose script runs at all, and
the pace inequality is the same inequality rather than a second one: the arrival runs `ARRIVE_MS`, so
a reader at `pace` px/ms covers `pace × ARRIVE_MS` in that time, and if that is further than the
screen the arrival ends off it.

The shape of the library is what made this a decision rather than a copy. Its 76 documents share one
stylesheet and one script (`/styles.css`, `/theme.js`) while the landing inlines both, so the landing's
inlined copy is not the library's to reuse and the two run beside each other rather than through each
other - checked, not assumed: the landing requests no stylesheet and loads no shared script, so no page
carries two scripts that could both mark the same block. Reduced motion is a separate answer here and a
larger one: under `prefers-reduced-motion: reduce` the script returns before anything is marked, so the
authored page *is* the finished page and a reader who asked for less motion is never shown a document
with pieces of it missing. Measured on the built index at 1440×900: **6 of 7** groups sit below the
fold and are cold while the seventh, at 630px, is not; the block that waits is cold at **opacity 0**
and displaced **14px**; the same block arrives at `--arrive: 1` / **0.7s** when approached at a
reading pace and `--arrive: 0.3` / **0.21s** when flicked at, with **7 links** and every list
opacity identical either way, the transform back to `none`; and with motion reduced the run reports
**0 cold, 0 quick, 0 hidden**.

The gates grew with it. The motion audit is **24 claims** now (was 18), five of them the library's own
and one its reduced run, driven on `/library/`; `verify-links.py` is **93 assertions** (was 88) and
holds the four facts no single browser run can see - that no marker is authored hidden in the markup
(the failure the stylesheet's comment names, and the one a hand-edited page would reintroduce), that
every page carrying a marker loads a script that could mark it (the landing inlines its own), that
the script's `ARRIVE_MS` and the stylesheet's transition are the same 
number in two files, and that the family's other timings still read the clock; and the self-test is
**15 doctored pages**, now runnable a family at a time. That last change was forced by the clock: the
landing's six patches took over nine minutes once each one paid for two browsers, so a patch now loads
only the page that can catch it - **78 seconds** for the landing family, 58 for the pacing pair, 48
for the library. The library's five patches are the fold test dropped, the inequality divided by 1000,
the quick clock declared but not applied, the hidden rule dropped, and the reduced-motion guard removed;
the second is in the list because the landing shipped that exact bug for one build in a copy of the
expression the library was about to repeat.

The shared files are exact-tiered in `budget.json` and were re-baselined on purpose: `/styles.css`
**56,514 to 58,263 B** and `/theme.js` **3,924 to 7,665 B**, most of the script's growth being the
reasoning that chose the mechanism, which is this repository's habit for code that could be got wrong
twice. Two instrument failures are worth keeping: the first probe of this feature went through a
harness that answers under Chrome's *virtual-time* clock, which does not deliver IntersectionObserver
notifications, and it reported a block sitting fully in view (top 400 of a 900px viewport) staying cold
for three seconds - a page cannot be that broken, and the harness said so in its own docstring; and the
second probe measured the one group that was *correctly* not cold, so both of its paths proved nothing.
A third failure was a gate catching this change rather than a bug: the index's jump-row check required
the group sections' class attribute to hold exactly `index-group`, and reported all seven groups as
missing the moment a `reveal` marker joined the list. The class list is a list.

The vocabulary is deliberately small and each item has a job. The report's #14 warning is respected:
Tempo-level motion on a page that does not need it *"reads as noise."*

| id | Motion | Trigger | Duration | Why |
|---|---|---|---|---|
| **M1** | Nav hairline fades in | scroll past hero | 200ms | genre: 4 of 5 |
| **M2** | **The hero sequence** | on load | ~4.5s, once | **the signature** — see below |
| **M3** | Window entrance | section enters | 700ms scale .97→1, +24px→0 | Tempo's *panel* entrance, **not** a text fade |
| **M4** | **The witness** | hover/focus a chip | 180ms | the product's own mechanism, made usable |
| **M5** | Disputed-table rows stagger | enters | 45ms apart | the content *is* a sequence |
| **M6** | Close: re-ink + occlusion | enters / scroll | 700ms + parallax | v1's one good moment, plus depth |
| **M7** | Accordion open/close | click | 320ms | §8.3 |
| **M8** | Link and button hover | hover | 160ms | genre baseline |
| **M9** | **The hero's question** | click a chip | the answer's own M2 | the window answers a second and third question, and the second is the refusal |
| **M11** | **The act index** | first scroll / act change | 160ms colour, 1.45x scale | the rail's echo at the viewport edge; the Awwwards device G36 took |
| **M12** | **The scribe** | plate enters | 900ms frames, 1,400ms roll, claim last | the ring is drawn the way its plates were made (§7.5) |
| **M13** | **The reading log fills in** | act 4 enters | 140ms apart, ticks last | the act's claim is that you watch it read (§7.6) |
| **M14** | **The hero's mechanism** | the reader's own scroll through the hero | 8° of the great wheel, 37° of each pinion | the world turns because the reader moved, not because the page did (§2.2) |
| **M18** | **Both worlds answer the hand** | dragging the ground (mouse or pen) | live, then momentum ≤96°/s halving every 160ms (one tooth a frame) | §2.2's world is a place, and a place can be taken hold of; one factory, one writer, one ratio |
| **M19** | **The flywheel** | the speed of the reader's own scroll, read over a window, **while the hero's band is on screen** | charged above 1 px/ms sustained across three samples spanning 60ms+ in a 150ms window; coasts ~14° past the gesture and settles in about a second | the world has mass: the fast gesture is charged and the slow read is left perfectly still (adaptive pace), and the angle keeps meaning the reader's position |
| **M20** | **The arrivals keep the reader's clock** | the pace the reader arrives at a block with | the family's timings scaled by `--arrive: 0.3` when the arrival would end off screen; the authored clock above 1.25 px/ms | the fast scroll gets an abbreviated entrance and the stopped read gets the whole thing; the order and the content never change |
| **M21** | **The library's blocks arrive** | the block crossing the fold, and the pace the reader fed it | the landing's clock, from the shared script: 700ms authored, 0.3 when the arrival would end off screen | the 78 carried documents get the craft the landing already had, and a reader who asked for less motion is never marked at all |

### 7.8 The library's figures

The 78 carried pages argued in prose while the landing argued in drawings, and the
six figures that now exist in the library are chosen by what a drawing can say that a
sentence cannot: **GGUF anatomy** (the file's fixed order, and that the weights are
nearly all of it), **quantization ladder**, **RAM budget**, **Q4_K_M anatomy**,
**citation anatomy** (2026-09-21): a real citation above an invented one, drawn with the
same geometry field for field and the same red on the locator, so the only thing the
drawing lets differ is what the locator leads to. The real record's line ends at a
document; the invented one's is dashed and leaves the frame, which is the open-edge
honesty marker the GGUF figure uses for the tensor band. The invented citation is
labelled as a fabrication in the caption, because a figure arguing that citations must
resolve cannot blur its own example. And **context window** (2026-09-21, the same
morning): the page's own line is "The window is not ignorance; it is a budget", and the
drawing is that budget. Four claimants share one bar - the standing instructions taking
their share first, the question, the few passages retrieval chose, and the answer being
written - with the shares in TOKENS against a real 8,192-token window and the note
saying "e.g." because the split is an illustration rather than a measurement of any
particular request. Two things only a plate can carry are drawn rather than stated: the
middle 40% of the budget is veiled, because a model reads the middle of a long context
least reliably, and the region past the ceiling is outlined, shrinking and fading
because text there is not compressed or remembered, it is absent. The first version of
that region filled it with --ink at fading opacity, which on a light page produced
three dark slabs HEAVIER than the budget they were supposed to have fallen out of; the
second gave three equal dashed boxes, which read as three more claims. A region that is
not there has to lose size as well as strength.

That plate also produced the tightest type on the site, and the floor is derived from
the measurement rather than chosen. The tall variant is 380 units wide and renders at
**280px in a 320px viewport** (0.737), 335px at 375, 440px at 480 and 520px at 560, so
11 / 0.737 = **14.9**, which is why its labels are **15 units**: at 14 the smallest one
rendered at **10.4px**, under the floor every other plate holds. `audit-contrast.py` now
visits the page, and its type pass reports the smallest text on it as **11.05px at
320px** across 13 widths, which is the plate sitting on its derived floor with nothing
to spare. The page joined that audit's default list for exactly this reason.

The discipline is the landing's, applied to a carried page: generated by a tool that
refuses to hand-edit, tokens rather than colors so both themes come free, two variants
because a 560-wide drawing in a 272px column sets 14-unit type at 11px and no font-size
step fixes that, and a type floor asserted per variant. The figures invoice their own
claims too: `verify-figures.py` runs each generator's self-test (**27 checks**) and
requires every committed figure to be its generator's current output, and the citation
figure checks the things a picture cannot: that both rows' fields share one geometry in
the emitted SVG (a figure that laid them out differently would argue the opposite), that
a wrapped title is still the whole title word for word, that no hex color crept in, and
that the tokens it borrows clear **4.5:1** against the canvas in both themes - read out
of the library stylesheet rather than copied, with --witness the tightest at **4.55:1**
in light. Measured in the built page: the tall variant ships at **0.985** scale on a
375px phone (13.8px labels) and the wide one at 640px on desktop.

### 7.1 M2 — the hero sequence, in detail

The page's argument, performed once. Ordered exactly as the product works:

1. the question bubble settles in — 200ms
2. *"Thoughts ⌄ / Drafting the answer"* — 300ms
3. the reading-log lines stagger in, 60ms apart — **this is the gate working**
4. the answer's paragraphs rise, 90ms stagger
5. **the citation chips appear last** — 40ms stagger

Total ≈4.5s, then it **rests and does not loop.** A loop would read as decoration; running once
reads as a demonstration. If the reader arrives mid-sequence, it completes rather than restarting.

### 7.2 M3 — why the text does not move

Every reference except Tempo reveals text with an opacity fade, and the report flags
*"fade-and-slide-up entrances on each section"* as the generic default. Tempo is the outlier: its
reveals are **panel entrances, not text fades.** v2 follows Tempo. **Text is static; the window
animates.** Cheaper, more distinctive, and it puts the motion on the product rather than on the
prose — which is §1's whole thesis.

### 7.3 M6 — the close

Two moves, and the second is the one the report says people skip (#13):

1. The giant `ἵστωρ` **re-inks coral → azure** over 700ms on intersection. v1's single moment,
   kept — it is the best idea in v1.
2. **`exhibit-16` overlaps the wordmark's lower third**, with a small parallax so the wordmark
   passes *behind* the product. Freebuff's hills pass in front of the wordmark; Tempo's planet limb
   passes in front. Ours inverts it: **the product occludes the brand.** Which is, precisely, what
   *"it shows you what it saw"* means.

### 7.4 M11 — the act index

One dot per anchored act, fixed at the right edge, revealed by the first scroll and driven by the
same M1c arithmetic that promotes the rail's rows: the dots mirror the rail's rows one for one, so
the current act is shared state, not a second tracker. The Awwwards staple on long scroll-story
pages (Cerebrium, Sharplink — the G36 pass), and Istor's page is exactly that shape. The dots sit
directly on whatever ground is under them, so rather than track grounds they wear the tokens that
hold on both extremes: `--ink-3` idle, `--azure-deep` current (§4 calls it the lightness midpoint of
the two accents — the accent built for this duality), the current dot scaled 1.45x so the emphasis
does not rest on colour alone. Hidden at ≤1080px, where the rail it echoes is hidden too and the
inset fields run nearly to the viewport edge; hidden in print, where there is no scroll position.
Authored `hidden` in the markup, so a reader whose script never ran gets nothing unusable.

### 7.5 M12 — the scribe

The stop act's ring draws itself in when the plate arrives, in the order the arithmetic itself has:
the two frame circles scribe (literal circumferences as dash lengths — 2π·272 = 1,709.0264 and
2π·248 = 1,558.23, no `pathLength`, the generator's own discipline), then the hole ring ROLLS
exactly one dash period (4.60177 = 0.02 + 4.581770, one hole-to-hole step; the pattern is
period-strict, so the end state is the identical drawing and the 355 count stays true), and the
azure claim — the only thing in the figure that is an argument — lands last, at 2s, when the
instrument that measures it is finished. Keyed to the plate joining the `.reveal` system: the cold
state holds the un-drawn start, a reader whose script never ran never sees it. The classes
(`ring-frame`, `ring-holes`, `ring-claim`) are emitted by `make-calendar-ring.py`, because the
figure carries "do not hand-edit".

### 7.6 M13 — the reading log fills in

Act 4's replica fills the way a fetch log fills: four rows arrive 140ms apart and each row's tick
lands 300ms after its own row, because that is the order the app works in — the page comes back, then
it is marked read. One shot, keyed to the same `.reveal`/`.is-cold` pair as every other entrance, and
the delays live on the base rule for the reason §7's M5 note gives. The tick is drawn in CSS (two
borders on a rotated box, the hero scroll cue's technique) rather than becoming a sixth glyph in an
icon set that holds five on purpose.

### 7.7 Reduced motion

**Every item above is wrapped in `@media (prefers-reduced-motion: no-preference)`.** Under
`reduce`, each element renders in its final state immediately, and M2 does not run — the hero shows
the settled answer. This is not optional and it is not a fallback style; it is the same page.

---

## §8 · Interaction

v1's Principle 2 forbade all of this. v2 requires it.

### 8.1 Nav

Sticky; anchor links to the passage, the machine, and the questions. Smooth scrolling honoured only
under `no-preference`.

### 8.2 The witness (M4) — the page's one interaction

On `exhibit-11`, each citation chip is a real focusable control. Hover or focus → the sentence it
supports is marked, and the chip lifts. Keyboard operable, `aria-describedby` linking chip to
sentence.

Built on the **DOM replica**, not a bitmap, because a bitmap cannot be hovered — and the captures of
the *expanded* chip are all defective (§6.3). This is where the hero's replica earns its keep a
second time.

### 8.3 Questions — a real accordion

`<details>`/`<summary>`, so it works with JavaScript off. Height transition 320ms under
`no-preference`; chevron rotates 200ms. Questions are the honest ones, and one of them is the
question the empty repo raises:

- Does it need a GPU?
- Does anything leave my machine?
- Where do my notes live?
- **Can I download it yet?** — answered plainly: not yet; the code is not published; *follow the
  build*.
- What does it cost?

### 8.4 Focus

Visible focus rings on every interactive element, `:focus-visible` only, using `--azure` on paper and
`--azure-lift` on the field. Contrast ≥3:1 against both grounds.

---

## §9 · The evidence band — what replaces social proof

The genre has a social-proof slot and **every reference fills it differently**: Freebuff with five
forms at once, Gamma with a logo strip and named testimonials, Gemini with press quotes, Tempo and
Breezy with none.

**We have none, and we may not invent one.** The brief's own rule — and v1's §8 P8 — is *nothing
unverifiable*, on a product whose selling point is that it does not overstate. There are no users to
count, no logos to borrow, no quotes to gather.

So the slot is filled with **evidence instead of endorsement**, and every number is taken from a
capture:

| Number | Claim | Source |
|---|---|---|
| **`0`** | accounts, API keys, or requests leaving the machine | `settingsresearch.png` — *"Scrape (keyless, no service)… No API keys, no third-party search API"* |
| **`0.028 mm`** | the radial variation it reasoned to | `Question3.png` |
| **`354.08`** | holes, at 68% credible, against the previously assumed 365 | `Question3.png` |
| **`12`** | disputed claims it kept rather than resolved | `Question2.png` |

This is the honest analogue of proof, and it is arguably stronger: a logo strip says *other people
like this*; this says **here is what it did, and you can check it.** The section is named for what it
is — *"The numbers it reasoned to."*

---

## §10 · Copy

### 10.1 What is kept

v1's copy deck is good and its voice is right: plain words, accuracy leads, nothing unverifiable,
the product speaking as itself. **All of it survives as voice.** v1's `<title>` — *"Istor — it shows
you what it saw"* — survives verbatim as the hero.

### 10.2 What changes

Headings become **3–7 words** (genre rule, no exceptions across five sites). v1's headings were
often full sentences — *"It checks what you already gave it, before it looks anywhere else."* The
sentence is good copy; it is not a heading. It becomes body, and the heading becomes
*"It checks what you gave it."*

Two sections are **new**, drawn from captures rather than invented:

- **The dispute** — *"It keeps the disagreements."* The entire section exists because
  `Question2.png` shows the app doing something we never wrote about.
- **The evidence** — §9.

### 10.3 The CTA slot

One component, two attributes. Today:

```html
<a class="cta" href="https://github.com/ThoriaDevelopment/Istor">Follow the build</a>
```

When a release exists, only the label and href change — to `Download for Windows` and the release
URL. The brief anticipated this (*"a swappable slot, not a hardcoded button"*, Windows-only for now),
and the slot is built to carry it.

### 10.4 A false claim v1 shipped, corrected

> **v1's call-to-action read `[ Read the source ]` and its footer described GitHub as *"the product's
> source"*. Both are false: the repository is empty** — `size: 0`, no releases, no tags, no files,
> verified against the GitHub API on 2026-09-19.

On a page whose whole argument is that it does not overstate, that is the worst possible error and
it is corrected here as a matter of record. **Nothing on istor.fyi may claim the source is
available until it is.** The repo's own description is real and may be quoted; its contents may not
be described.

That rule was written about one page and obeyed on one page. Audited across the whole artifact on
2026-09-19, the landing page was honest ("There is no installer yet, and the repository is public
and empty") while the 75 carried library pages offered a **Download** pointing at a releases page
GitHub reports as empty, eight comparison pages called Istor **open source** and **MIT licensed**,
and four comparison tables wrote **"Free, open source"** in Istor's Price cell. `llms.txt`, the
surface written for machine readers, repeated both claims. None of it was a decision; it was a rule
that lived in prose and was applied to whichever page somebody happened to open.

The rule is now check 11 of `verify-copy.py`, and it runs in CI beside the byte and link gates. It
reads the built artifact, not the sources: an openness term in the same sentence as the product's
name, an offer to download it, a link to a releases page, and — because a comparison table's cell
inherits its subject from the column header rather than from any sentence — each table's cells
paired with their own column. Both halves carry a positive control, and the table control plants a
false claim in the Istor column beside a true one about another product, so a detector that merely
finds an openness word in a table fails it. When the check was first run it failed on four tables
and a markdown link target (`istor.fyi` four words from "the open-source engine" in a sentence
about llama.cpp), which is what a first honest run of a new check should look like.

---

## §11 · What v2 keeps from v1

So the reversals in §13 are not read as a rejection of everything:

- The **copy deck's voice**, and the `<title>`.
- The **66ch measure**, the two-face system, the three font files, and **GFS Didot's missing weight**
  as a design constraint rather than a problem.
- **The five Lucide icons**, with their provenance (Lucide's own files at 24px viewBox, stroke 2,
  drawn at 14/16px — **not** redrawn).
- The **ground grain** tile, the **og-card teal**, the **eye mark**, the Greek wordmark.
- **The DOM replica's verified geometry** (`180px 594px 185px` = 959px).
- The **75-page library carry**, the CSS-inlining that keeps `/styles.css` the library's, the
  directory-allowlist assembler, and the byte-exact `budget.json` discipline.
- **The close's re-ink**, which was v1's single best idea.

---

## §12 · Weight, and the gates

### 12.1 Budget

Thoria's envelope was **2–5 MB**, chosen as what the reference look costs (four of the five sit
between 2.12 and 13.80 MB). **v2 lands below that envelope, and the reason is structural, not a
cut.** §3.1's rule — display every exhibit at exactly `crop_px ÷ 2` — means no asset is ever
upscaled or padded, and AVIF over flat UI is far smaller than the JPEG/PNG the reference sites ship.

The table below was written as an estimate when this plan was specified. **It is now measured**, off
the built artifact on 2026-09-19, and the file that asserts these numbers (`budget.json`) carries the
same figures — a change to one is a change to the other, in one commit. Three of the estimates were
low and are corrected here rather than left to disagree with the gate.

Re-measured 2026-09-19 after the phone crops, the library index and a night of work on the page.
The method, because a weight table whose method is not written down cannot be re-checked: **the
exhibit rows are the sum of the files themselves**; **the whole-page rows add the document, the three
fonts and the ground tile to one density of AVIF**, where a phone takes the art-directed phone crop
for the four wide exhibits in place of the wide one, which is what the `<picture>` elements say it
does; **the first-screen row** is the document, the fonts and the ground tile only, because every
exhibit is `loading="lazy"` and the first one sits below the fold. The desktop row reproduces the
previous figure byte-for-byte, which is the check that the method is the same one that produced it.

| | Estimate | **Measured** |
|---|---|---|
| Nine exhibits, AVIF 1×+2× | ≈ 400 KB | **594 KB** |
| Nine exhibits, WebP 1×+2× | ≈ 650 KB | **922 KB** |
| Fonts (3 files) | ≈ 65 KB | **63 KB** |
| Ground grain + og-card | ≈ 124 KB | **121 KB** |
| `index.html` incl. inline CSS | ≈ 55 KB | **72 KB** |
| **Artifact (everything shipped)** | **≈ 2.5–3.0 MB** | **4.17 MiB**, 156 files |
| **First screen** (document, 3 fonts, ground tile) | — | **135 KB** |
| **The whole page read, desktop** (AVIF 2×) | **≈ 550 KB** | **451 KB** |
| **The whole page read, phone** (AVIF 1×, with the phone crops) | **≈ 320 KB** | **217 KB** |

The three rows that moved most are worth reading rather than re-baselining. The exhibit rows rise
because four wide exhibits now carry a second, art-directed crop instead of none — the set is bigger
while **what a phone downloads falls, 257 KB to 217 KB**, which is the whole point of the change and
would be invisible in an inventory row alone. `index.html` is 10 KB heavier than the table's old
figure, spent across the acts rather than in one place, and `budget.json`'s own note itemises every
step of it. The artifact row gains the 30,679 B library index and its 155th file, plus the library's shared theme control, `/theme.js` at 3,924 B, which is the 156th and the only file added to this count without adding a page. The index is now 3,398 B longer than it was: seventy-five entries in one directory is a list a reader can read and cannot search, so the page carries a find field, authored `hidden` and unhidden by the page's own script so that a reader without scripting gets all seventy-five entries rather than a box that filters nothing, matching a word-AND over each entry's own title and summary and keeping the query in the URL. That last change also exposed a defect the same page had carried since it went up: its group blurbs were styled `--mist` and rendered in full ink, because `.page p, .page li` outranks a single class, which is why every index rule that describes a paragraph or a list item is now scoped to `.page-index`. Both the byte and the correction are itemised in `budget.json`'s own note. The estimate column
is left as it was written, so the gap between the estimate and the measurement stays legible: this
page is heavier than the plan guessed in the exhibit sets and much heavier in the document, and it is
still under Thoria's 2–5 MB envelope, with a first screen of 135 KB.

The two transfer rows are what one visitor actually downloads, and they are the rows that matter:
one density of the AVIF set, plus the three fonts, plus the ground tile, plus the document. Two
notes on how they are counted, because the estimates did not say. **A visitor picks one density**,
so the 1× and 2× sets are never both transferred — the estimate above them added the two together,
which is why it read higher than either real figure. And **`og-card.png` is not in these rows**: at
124 KB it is the largest single asset in the artifact, and the page never fetches it. It is fetched
by social scrapers reading `og:image`, once, off-site. Folding it into a page-transfer figure would
overstate every visitor's cost by roughly a third.

Two things this buys that the envelope would not have: the brief's hard constraint — *"the site must
stay viewable on low-spec phones"* — is met with room to spare, and it is met **by construction**
rather than by luck, since §3.1 guarantees phone renders the app's text at its native size and never
upscaled; and the page is **fast**, which in a genre where four of five sites take multiple megabytes
to show a hero is itself a differentiator.

**If the design wants more weight it may have it** — the envelope is not a target to hit. But v2 as
specified does not need it, and inflating a page to match a number would be the same mistake as v1's
85 KB, pointing the other way.

### 12.2 Gate changes

The build gates are re-baselined **by measurement, never transcription** — the v1 discipline holds.
`verify-budget.py` keeps its structure and gains:

| Gate | Change |
|---|---|
| `document.*` | **retiered as ceilings on 2026-09-20** (Thoria's call: the budget should be generous, not a re-baseline on every commit): `index_html_bytes_ceiling` **78,643 B** (256 KiB over a ~74 KB document), `index_html_gzip_ceiling` a round **32 KiB** (against ~20.2 KiB measured), `inline_js_bytes_ceiling` **16 KiB** (over 5,354 B shipped). The exact figures this replaces are in git history; the ceilings still catch the incidents the budget exists for — a copy deck pasted twice, a generator gone wrong, script that doubles — while ordinary content work ships without touching `budget.json` |
| `library.page_bytes_ceiling` / `index_bytes_ceiling` | **retiered as ceilings the same night**: **1 MiB** over ~619 KB of pages, **128 KiB** over the ~34 KB generated index. `page_count` stays exact: a missing page is a dead end for a reader. The shared files stay exact: a regenerated `theme.js` or recoloured stylesheet is a replacement, not a content edit |
| `totals.phone_1x` / `retina_2x` | re-baselined over 9 exhibits: **194,064 B** / **388,356 B**, and again on 2026-09-19 over 9 exhibits **plus 4 phone crops** at **237,991 B** / **500,885 B** — the inventory grows while what a device *downloads* shrinks, because those four exhibits now serve a narrower crop below 430px |
| `totals.exports_all_*` | **renamed `exports_all_36`** and the `.png` suffix dropped from the sum, because PNG left the shipped set; **renamed again to `exports_all`** when the phone crops took the set from 36 files to 52 and the number in the name stopped being true |
| `ARTIFACT_FILES` | re-baselined to **138** (the whole +18 is 9 exhibits × 4 files against 3 × 6), then to **154** on 2026-09-19 (+16 = 4 phone crops × 4 files), then to **156** (+the generated library index, +`/theme.js`). Stays exact: it caught stray screenshots twice |
| `type floor` **(new pass, 2026-09-20)** | walks **13 widths from 320 to 1440** and asserts that nothing a reader has to read renders under **11px**, multiplying each text's size by the scale of the SVG it sits inside, because a plate's type is in user units and its computed `font-size` is not the number a reader gets. 6,489 texts. It found the site's smallest text at **7.66px** (the ring's `355` at a 390px window), the boundary plate's glosses at **9.0-10.8** between 641 and 768 and the etymology ledger's at **9.8** at 320; all three are fixed. Its own first version measured the audit harness's document instead of the framed page and passed over **zero** texts, which is why the line prints the count it measured |
| `verify-figures.py` **(new tool, 2026-09-20)** | regenerates all seven figures in `Source/figures/` and compares each to the committed file **by bytes**, restoring the working tree whatever the comparison says, then runs each generator's own `--self-test` where it has one. 9 checks. The claim in `SITE_BUILD_PLAN.md` that `verify-budget.py` catches a stale regeneration was only half true: it catches a stale figure that moves the page's total past a ceiling, which is a much larger event than a figure three hundred bytes out of date, and this repository generates its artwork rather than storing it. It also fixed two generators that wrote to `../figures/`, a path that is right only when the tool is run from `Source/tools` and, from the repository root their own docstrings name, resolves to the repository's **parent** |
| `verify-copy.py` **(new tool)** | Stage 9's checks 10 and 11: the humanizer pass as a rule rather than a memory, and §10.4's release-claim rule in both prose and tables. Both run a positive control before they trust their own silence, and an allow-list entry that stops matching fails the build |
| `audit-motion.py` **(new tool, 2026-09-21)** | drives the page instead of reading it, and asserts **12 claims** about the two worlds: a notched read leaves the wheel where the scroll put it, a page-sized jump is not a gesture, a sustained flick charges it and it coasts and stops, the mesh ratio holds at every one of those moments, the hand turns it, a control keeps its own pointer, a touch is never taken, and with motion reduced the world is never written. A local tool with a non-zero exit, for the same reason `audit-contrast.py` is one. Its `--self-test` builds **five doctored pages** and requires each to fail the claim it breaks. The night's most expensive lesson lives in its docstring: `--virtual-time-budget`, the only thing that makes headless wait for a scenario, produces no animation frames and stalls outright on a page that requests them, so the harness **POSTs its answer back** and Chrome runs in real time |
| **`composition` (new)** | asserts the page has **≥ 10 sections, ≥ 4 distinct composition classes, ≥ 1 sticky element, ≥ 1 `<details>`, and ≤ 1 display-size element** |

That last gate is the point. v1 had 53 assertions and none could see that the page was nine identical
sections. **A composition gate is what would have caught it**, and it is the only gate here that
asserts the *design* rather than the bytes.

**Every figure in `Source/figures/` now has to be what its generator writes today.** Seven SVGs on
this page are generated, committed and inlined into the document, and each one carries a "do not
hand-edit" comment inside it that nothing checked. That failed twice in one session, both times
caught by luck: a hero placement that was edited in the generator and not in the figure, and a plate
whose box widths came from a measurement the shipped figure did not have. `verify-figures.py` closes
it, in the four steps a gate needs. It runs each generator in place; compares by **bytes**, because
`read_text()`/`write_text()` translate newlines and a CRLF copy of the right drawing compares equal to
a fresh LF one, which is the lesson `make-icon-sprite.py` learned first; **restores the working tree
whatever the comparison said**, including uncommitted work, because a check that leaves the workspace
modified is a check nobody runs twice; and runs each generator's `--self-test`, so the invariant tests
travel with the gate instead of living in whoever remembers them. It was shown failing before it was
trusted, on both branches: a figure with one byte appended (reported at the exact offset) and a figure
removed from the tree (reported as uncommitted, since the build inlines what it expects to find).

**The artifact total is a report and no longer a stale one.** 4.12 MiB was written before the
article navigation and the directory's find control landed, and nothing asserted it, which is how a
measured figure goes out of date without anybody seeing it: the artifact row is checked as a file
count, because page bytes move whenever anyone edits a sentence. It reads 4.17 MiB now, which is the
current artifact as measured, and it includes the not-found page's growth below.

`/404.html` is the one page the assembler does not touch, so it is the one page that had no rule of
its own, and two are written for it here. `build-site.py` strips the comments out of its `<style>`
and `<script>` blocks on the way into the artifact, with the same contract the inliner holds: no
comment left in the shipped page, and the page before and after equal with comments and all
whitespace removed. It was posting its own reasoning, 4.6 KB of the file's 10.2 KB. And
`verify-links.py` gains its 11th check, four assertions over the artifact: the strip ran; the page's
search is a plain form, with an action, a method and a field named `q`, because it has to reach
`/library/?q=` on a browser whose script never ran; a link into the library follows that form so the
page has a way on with no script at all; and its dark token world holds **the library's own values**,
role for role. That last assertion is between two files rather than inside one, and it needs to be,
because the page owns a stylesheet instead of sharing the library's, which is exactly how two token
blocks drift apart. Every one of those four was shown failing before it was trusted, including the
first version of the token check, which read one block of the two and reported a clean bill of health
for a world whose other copy had drifted.

The page is also in the contrast audit's default set now, so the artifact's six templates are all
measured instead of five. A page's worth of ink on a stylesheet of its own is the other way a template
goes unmeasured: not large, just separate. It is clean in all four states at 1440px, and its dark
states report **one** of the page's own media rules, which is the block being reached rather than
merely existing.

**A dark world on a page obliges it to answer a printer**, which is §3.6's rule meeting this page's
new one, and it cost an ordering bug to learn. The page now carries the library's print world and the
library's `prefers-contrast: more` values, and check 10 reads all three stylesheets instead of two
(57 assertions now, and the text-token vocabulary grew by `--ink-2` and `--azure` so the page's own
ink names are checked against white paper rather than skipped for having different names). The bug:
more contrast and paper pick different quiet inks, #C4C0B8 and #33322F, and a reader can be both, so
the later block wins where the two media match. Declared print-first, more contrast would have taken
it, printing a light grey on white at 2.2:1. The library has paper last for that reason and the page
now does too. It is verified the way this repository verifies a cascade: every conditional block is
unwrapped into the live page in file order, and with the dark world, more contrast and print all
active at once the computed ink is `#000000` on `#FFFFFF`.

**One audit is deliberately not a gate.** `Source/tools/audit-contrast.py` measures every text
element against WCAG AA, in both themes, by rendering each page in a sized iframe and walking it in
viewport-sized steps. It needs Chrome, and CI installs nothing, so running it there is not possible
without breaking the property that makes the gates trustworthy. It is a local tool with a non-zero
exit, run by hand after any change to a colour token, a ground or a face. Its first run found
exactly one failure in 166 elements, the confidence ruler's scale label at **3.12:1** where 15px
needs 4.5, and the bug was the token block rather than the rule: `--ink-3` was labelled "labels and
captions" while it is the app's own label grey, a fine graphic at that ratio and the wrong colour
for a sentence. The pixel sampler added the same night found two more that no flat-ground reading can
see, because both are type meeting the drawing: the closing paragraph's secondary ink measured
**4.31:1** against the horizon's halo at phone width, where the halo is lighter than the field's own
brightest stop, and the closing wordmark's pre-reveal coral measured **2.45:1** on the field's
lightest stop. Both were fixed in the ink, not in the tool. Grounds that are photographs, masks or
the app's own screenshots are reported as unmeasured, and every run prints how many viewports it
walked and how many elements it could not measure: a clean result that covered seven elements of a
long page is not a clean result.

**A second local tool drives the page rather than measuring it.** `Source/tools/audit-motion.py` asks
what the mechanism DOES when it is used, which is the one class of claim no build-time fact can reach:
a notched read leaves the wheel exactly where the scroll put it, a page-sized jump is not a gesture, a
sustained flick charges the wheel and it coasts and then stops, the hand turns it, a control keeps its
own pointer, a touch is never taken, and with motion reduced the world is never written at all.
**Twelve claims**, each of them a sentence this plan makes elsewhere, and each proven failable before
it shipped: five doctored copies of the built page, every one caught by the claim it breaks. Its own
first version could honestly assert nine of them, and the three it could not - the coast, the settle,
and the ratio through the coast - are exactly what the instrument change below recovered.

**That tool also cost the most to build, and for a reason worth recording.** It began on
`audit-contrast.py`'s harness, which reads its answer out of the DOM with `--dump-dom`. That fires at
load, so a scenario of eight seconds of gestures needs `--virtual-time-budget` to make the browser wait
at all - and under the virtual clock this renderer produces almost no animation frames: **four in three
seconds**, in old headless and new, with and without every frame switch worth trying, and with a running
CSS animation in the page to force invalidation. The momentum is advanced by `requestAnimationFrame`, so
the wheel would receive its charge and never turn; worse, a page that keeps requesting frames **stalls
the virtual clock** rather than finishing, and two self-test runs sat for the full 420-second subprocess
timeout instead of reporting anything. The fix was to change the question's plumbing rather than the
claim: the harness now POSTs the scenario's value back to the tool's own server and Chrome runs in
**real time**, where the waits are the waits a reader's browser makes. The first three claims that
version could assert are now twelve, and the one thing this arrangement gives up is that the tool
describes a real browser rather than a deterministic one - which is what the claims below are about
anyway, and why the events are still dispatched at instants the tool chooses rather than read from the
browser's own coalescing stream.

**It audits the states a render never shows, too.** §3.6 promises `prefers-contrast: more` on both
halves, and §3.5's theme control promises a dark world to a reader whose machine is dark and who has
stored no choice. Until 2026-09-19 only the *existence* of those rules was asserted, which is
a claim about the source rather than about the page, and for the dark one it was worse than that:
headless Chrome reports a light OS, so `:root:not([data-theme="light"])` had never been rendered by
anything. Chrome's command line has no switch for either feature, so the audit emulates them where a
browser resolves them, which is **two** places: the framed page's own matching `@media` rules are
unwrapped and appended where they would have landed, and the copy this run serves carries a
`matchMedia` patch installed before the page's first script. The second one is not a refinement. The
theme stamp asks `matchMedia('(prefers-color-scheme: dark)')` in the head and writes `data-theme`
from the answer, and an attribute outranks every media rule, so the first version emulated the
scheme in the cascade alone, matched the rule, injected it, and measured the LIGHT tokens: a clean
`ok` about a state it had never entered. The patch's own failure is the same lesson twice over, since
it threw on its first run (a Python string ate its backslashes) and the run said `ok` again, so now
a state whose patch did not install is an **error**, not a pass.

**It measures target size, which is the first question here about a finger rather than an eye.**
WCAG 2.5.8 asks for 24 by 24 CSS px, or two measured exceptions: a control inline in a run of text,
or one where no 24px-diameter circle centred on it reaches any other control. Twelve passes at phone
and desktop width cover 414 controls, 260 of them under 24px and every one excused, the tightest
clearance anywhere being **13.2px** past the required radius. The pass found no defect on the site,
and the reason to keep it is what it found in itself. Its nested-target exception read
`contains(a,b) || contains(b,a)` with each half testing x-overlap **and** y-overlap: that is
rectangle intersection, and the symmetric `||` makes the whole test "these two boxes touch", so every
overlapping pair was skipped before the circle was drawn. The pairs that overlap are the pairs the
exception exists to judge, so the check could not fail, and it reported `0 FAIL` on the real site and
on a copy whose directory had been collapsed to a dense column of 20px rows 16px apart. What caught
it was the negative test, then the same mutation reporting 69 failures once `encloses` meant
enclosure. The exception also had to learn what "inline" means: asking whether the target's parent
held more text granted it to seventy of the directory's ninety-one targets, because each entry is a
link followed by a block-level blurb, and a link that heads its own list item is not a word in a
sentence. It now requires a non-empty text node or an inline-level sibling, which is the run of text
the rule is about.

Nothing is invented in the tool and no colour is written down there, which makes the failure mode
the honest one: **every emulated state prints how many of the page's own rules it found**, because
zero rules is a page that does not style the state, not a state that passed. The landing page is
audited in three states and the library in four, at 1440 and at 390, and all of them are clean under
AA, and none of them was clean by accident: a copy of the artifact with a bad contrast block reports
**61** failures under the emulated state and zero without it. Two of those states are the ones no
render had ever covered, and both now confirm what the stylesheet says rather than what it promises:
a dark machine with no stored choice gets the dark world (`--canvas` #0A0A0A, `--mist` #A5A19B), and
a stored light choice still wins on that same machine. The landing page reports **zero** rules for a
dark machine, which is also true of it: it ships one world and has no dark theme at all, which §3.6
and the print block both say in passing and nothing has ever questioned.

**One more pass, and it answers a claim rather than a criterion.** The audit serves every page a
second time with its script elements removed, which is the only faithful way to ask a browser what a
reader whose script never ran is given: Chrome's own switch would disable the harness too, and the
harness is how anything gets measured. Its probe asks a different question, so it reports on its own
line: characters painted, links, controls, and every element present but invisible with the reason
and its first line. This site leans on script for its optional parts, and "optional" is a claim.
Across the six templates the inventory is short and every line in it is an affordance the page works
without: the hero's three ask chips, the witness tooltip's two spans, the directory's find control, and
the 404's suggestions. A scriptless reader of the directory gets 89 links and all seventy-five
entries, of the 404 a form that reaches `/library/?q=`, and a carried article hides nothing at all.

**It also found one thing that was not fine, and the fix is §3.6's own rule applied to the hero.** The
inventory distinguishes a closed disclosure from hidden content, because the two are different
findings: a page can hide prose from a reader without script, or it can put the prose one click away.
The hero's two reserved answers were hidden, and one of them is the refusal that demonstrates the
claim the rest of the page asks to be taken on trust. So each is authored inside a `<details>` whose
summary is the question the chip would have carried, and M10 moves the answer out of its shell and
hides the shell once a chip can answer for it. One copy of the prose, the same interaction as before,
and a reader whose script never ran can now watch the refusal happen. It costs **1,054 B of document
and 344 B of script**, both re-baselined by measurement, and the first version of it spent another
450 B shipping `/* */` prose inside the script before the reasoning moved up into the markup comment
where this repository keeps it, which is also what took the document back under its gzip ceiling. Two instrument traps are recorded in the tool, and both reported the
opposite of the truth: the probe ran against the harness's own document until it stopped shadowing
the `d` and `w` the harness passes in (0 characters, 0 links), and it called the hero's opening
after 1.8 seconds of animation invisible until it finished every animation before asking which
elements have a box.

Turning the feature on immediately found three numbers that were wrong in the stylesheet that
promises it. `Source/styles.css` recorded `--ink-2` going to 9.8:1 and `--ink-3` to 8.4:1 under
`more`; neither reproduces on any ground the page has, and the true pairs are **9.41:1** and
**7.80:1** on `--paper`. The old figures were white-ground numbers written beside a base pair
measured on `--paper`, and the field pair had drifted the same way, `5.66:1` where the token block
nine hundred lines above already said, correctly, `6.07:1`. All four are now the audited values, so
the comment and the tool assert the same thing.

The same night found the audit measuring a page half-way through its own entrance. The hero's answer
arrives as six children on a stagger with delays up to 1,780ms, and `both` holds a delayed animation
at `opacity: 0`, so a fixed settle is a bet on where the page's clock is and the tool lost it about
half the time: **163 text elements in one run, 150 in the next, same build, same width**, five
paragraphs and a citation a visitor reads and the audit walked past. The report printing its own
element count on every line is what made that visible at all. The fix advances the clock instead of
guessing at it, finishing every animation and transition through `document.getAnimations()`, which
needs no number that drifts when somebody retimes the page.

**Two passes were added on 2026-09-20, and the first one found a defect on its first run.** The
reduced-motion pass renders every page twice, once as a visitor gets it and once with
`--force-prefers-reduced-motion`, and compares the two renders: nothing may still be running in the
reduced render, and nothing may be invisible there that the settled ordinary render shows. Site wide:
**0 animations running**, and two elements hidden in both renders, which are the citation witnesses,
a hover affordance, so they are the baseline rather than findings and no whitelist is needed. The
switch is a browser flag and not a cascade trick on purpose: the site guards motion the opposite way
round from the colour states, and emulating it in the CSS measured the page in both states at once
and reported 16 animations running on a site that has none.

The layout pass holds **every `.woff2` response for 1,200ms** and asks what moves, because every other
measurement in this project is taken on a machine where the fonts arrive in 90ms, which is a machine
where a font swap cannot be seen at all. It reads Chrome's own Cumulative Layout Shift from an
observer the run writes into the head of the copy it serves, and it gates on **0.02**, a fifth of the
web-vitals "good" line of 0.1, chosen so the ceiling is above the site with room rather than set to
the site's own measured value.

What it found is the reason it exists. `/what-is-a-local-llm/` measured **0.0395**: the capsule
paragraph at the top is **5 lines in the fallback face and 6 in Inter**, so the whole document under
it jumped down by 27px when the font landed. The same 0.0395 appears with the fonts held 0ms and at
148ms, so this had always been happening on every slow connection and had simply never been measured.
The fix is the standard arithmetic one: the fallback faces are declared with `size-adjust` set to the
measured ratio between the real face's advance widths and the fallback's, `ascent-override` and
`descent-override` set to Inter's own metrics so inline boxes are the same height, and the real face
left first in every stack so nothing changes once it loads. The ratio computed from a long string is
**107.74%** for Segoe UI, and the value that ships is **104%**, because a width ratio is an average
and a line break is a discrete event: swept across every page with the fonts held, the worst shift is
0.0090 at 102%, **0.0039 at 104%**, 0.0661 at 106% and 0.0298 at 107.74%. Arial keeps its computed
106.64% because no machine here has Arial to measure, and the residual is named rather than rounded
away: two typefaces do not scale into each other glyph for glyph, so a wrap point can still differ.
The landing page was already at 0.0039 and keeps its own stylesheet, since its fonts are preloaded
and its stylesheet is inlined, which is the whole of why it was never the worst case. The page the fix
was aimed at went from 0.0395 to **0.0025**, and the worst page in the sample is now the 404 at
0.0081.

---

## §13 · What v2 supersedes in v1, explicitly

Listed so nothing is ambiguous. Each of these is a **reversal**, not an amendment.

| v1 | v2 |
|---|---|
| §8 P2 — nothing responds to a click | Sticky nav, accordion, the witness, focus states |
| §8 — "everything else is static" | Eight-item motion vocabulary (§7) |
| §7 — "three bitmaps, not ten" | Nine exhibits plus an animated hero (§6) |
| §8 "quiet everywhere, loud once" | The field is the argument; the display size is spent once, and the page is loud in the hero and the close |
| The precedence rule (*the design plan wins*) | **Retired.** v2 is the specification; the build plan is re-derived from it and disagreement is resolved by measurement |
| `[ Read the source ]` → an empty repo | *Follow the build* (§10.3), and §10.4's correction |

---

## Appendix A · The exhibit table

Display width is always `crop_px ÷ 2` (§3.1) — pixel-exact at 1× and 2×, no upscaling.
**Crop bounds must be re-measured per file** (§6.4); the values below are the catalogue's measured
starting points, not a substitute for measuring.

| id | Source | Measured crop | Display | Notes |
|---|---|---|---|---|
| `exhibit-10` | `Black/Question1.png` | centre pane, ≈1242×880 | 621×440 | question + full answer; the "Thoughts ⌄" collapse carries the gate story |
| `exhibit-11` | `Black/verifiedsource.png` | `1242x900+318+88` | 621×450 | crop A; `+318+150` starts on the answer and drops the bubble |
| ~~`exhibit-12`~~ | `Black/FetchingPages.png` | *retired 2026-09-20* | — | its log is DOM now (§2.5); the crop line is parked in make-exhibits.py |
| ~~`exhibit-13`~~ | `Black/Question2.png` | *retired 2026-09-21* | — | its table is DOM now (§2.5); the crop line is parked in make-exhibits.py |
| `exhibit-14` | `Black/settingsresearch.png` | `800x568+560+226` | 400×284 | crop C; modal pixel-for-pixel, no dimmed background |
| `exhibit-15` | `White/settingsmodels.png` | modal bounds — **measure at build** | ≈400×300 | the modal is content-sized; measure as crop C was |
| `exhibit-16` | `Black/Sourcesfullscreenmain.png` | `1918x620+0+44` | 959×310 | crop E; full window width, because the list is the point |
| `exhibit-17` | `White/notesfullscreenmain.png` | `1918x620+0+44` | 959×310 | crop F; pairs with 16 as a dark/light diptych |
| `exhibit-18` | `Black/Question3.png` | centre pane, ≈1242×880 | 621×440 | 354.08 / 0.028 mm — the rigour |

Six of these already exist in `.improvement/assets/crops/` and need only tightening and re-export.

## Appendix B · Captures that would improve the page, and block nothing

Listed so they can be shot when convenient. **No section in this plan depends on any of them.**

| Want | Why | Status |
|---|---|---|
| the reasoning trace **mid-stream** | M2 currently performs the sequence in the DOM; a real capture would let M5 use one | not captured |
| an **empty result** / "no answer found" | the app's honesty is a selling point and no frame shows it | not captured |
| the **import dialog** | "Add source" appears in many frames; the dialog never does | not captured |
| a **larger library** | every frame shows exactly 10 sources | not captured |
| a **narrow viewport** | every capture is 1918px; a phone composition must be designed, not cropped | not captured |
| the citation chip **expanded, cleanly** | all three attempts have labels overprinting the body (§6.3) | defective |

The brief records that `Documentation/demo-library.md` was written specifically so these could be
re-shot with the app's own demo sources.

## Appendix C · Open items

1. **`White/settingsmodels.png` modal bounds** — measured at build time, per Appendix A.
2. **The replica's fidelity audit** — every divergence from the captures is a bug (§2.2). Needs a
   side-by-side against `Black/verifiedsource.png` before ship.
3. **Hardware spec** — the brief records this as still unanswered (the CLI run used
   `Qwen3.8-4B-Distill-GGUF:Q4_K_M`, 32 GPU layers, 4096 context). The FAQ's *"Does it need a GPU?"*
   needs a real answer, and §12's `--` must not be filled with an invented one.
4. **Whether `powercell` / `Taori` are named on istor.fyi at all** — still open per the brief.
