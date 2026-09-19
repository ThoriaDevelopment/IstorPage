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
   *light* app window on teal is a lit object. The app ships both themes, so both are real product
   material, and §3.4 makes the pairing a rule rather than a decoration.
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

Eleven acts, ≈11–13 viewports. The genre runs 7–16. Every headline is 3–7 words; every body
paragraph is 2–4 lines (genre rule, no exceptions across five sites).

Compositions are named **C1–C5** and defined in §3. The page alternates them deliberately — the
report ranks alternation **#12**, and notes that Gemini Notebook, competent and entirely
non-alternating, *"is the least memorable of the five despite having the best single element."*

| # | Act | Composition | Ground | Product shown |
|---|---|---|---|---|
| 1 | Nav — sticky | — | paper | — |
| 2 | **Hero** — "It shows you what it saw." | **C1** field-full | teal | DOM replica, **animated** |
| 3 | **The gate** — "It checks what you gave it." | **C2** split, field right | paper + teal | `exhibit-10` |
| 4 | **The passage** — "Every claim points at a passage." | **C4** band | teal | `exhibit-11`, interactive |
| 5 | **The reading** — "You can watch it decide." | **C2** split, field left | paper + teal | `exhibit-12` |
| 6 | **The dispute** — "It keeps the disagreements." | **C2** split, field right, portrait | paper + teal | `exhibit-13` |
| 7 | **The machine** — "Nothing leaves your machine." | **C3** diptych | paper | `exhibit-14` + `exhibit-15` |
| 8 | **The workspace** — "A library, notes, and the source." | three-up | paper | icons, not images |
| 9 | **The evidence** — "The numbers it reasoned to." | band | paper | — (§9) |
| 10 | **Questions** — accordion | two-column | paper | — |
| 11 | **The name** — "It is not finished." | **C5** poster | teal | `exhibit-16`, occluding |

### 2.1 Nav — sticky

```
┌────────────────────────────────────────────────────────────────────┐
│  ἰστωρ.        How it answers · On your machine · Questions   [ Follow the build ] │
└────────────────────────────────────────────────────────────────────┘
   ↑ hairline fades in on scroll (M1)          ↑ the genre's persistent CTA
```

Four of five references are sticky; each gains a 1px hairline once scrolled. Breezy skips it and,
the report notes, *"reads more like a brochure than an app as a result."* Height ≈68px. Links are
anchor links into acts 4, 7 and 10 — the page's only real navigation, replacing v1's arrangement
where the only nav was painted *inside a screenshot*.

### 2.2 Hero — C1

```
╔════════════════════════════════════════════════════════════════════╗
║  ░░░░░░░░░░░░░ deep teal field, full-bleed ░░░░░░░░░░░░░░░░░░░░░░░  ║
║                                                                    ║
║                 It shows you what it saw.                          ║  94px, GFS Didot, 1.06
║                                                                    ║
║        A local notebook that answers only from what you gave it,   ║  21px, 1 line
║        and points at the passage behind every claim.               ║
║                                                                    ║
║                    [ Follow the build ]                            ║  azure pill
║                                                                    ║
║        ┌──────────────────────────────────────────────┐            ║
║        │  the app window — 959px, light theme          │            ║  ← M2 plays here
║        │  (live DOM replica; the sequence runs once)   │            ║
║        └──────────────────────────────────────────────┘            ║
║                     ↑ 64px field padding                           ║
╚════════════════════════════════════════════════════════════════════╝
```

The hero **is** the product doing something, so there is no separate "product demo" section — the
genre's usual second act is folded into the first. Headline is v1's, unchanged: it is six words,
it is the page's own `<title>`, and it is the most distinctive sentence the brand owns.

**Why a DOM replica and not a bitmap here.** It is resolution-independent at 959px (sharper than
any capture), it weighs nothing, and — decisively — **it can move**, which is what §1's motion
thesis requires and what no reference can do. The fidelity constraint is absolute: the replica must
match the captures. v1 verified its geometry exactly (`180px 594px 185px` = 959px). **Any
divergence from the captures is a bug, not a design choice.** Fallback if it cannot be made
faithful: `Black/verifiedsource.png`.

### 2.3 The gate — C2

```
   ┌────────────────────────────┐   ╔═════════════════════════╗
   │ It checks what you          │   ║ ░ teal field ░          ║
   │ gave it.                    │   ║  ┌───────────────────┐  ║
   │                             │   ║  │  exhibit-10       │  ║
   │ Before it searches          │   ║  │  the question and  │  ║
   │ anywhere else, it reads     │   ║  │  the whole answer  │  ║
   │ what is already in your     │   ║  └───────────────────┘  ║
   │ library. Sources you        │   ║                         ║
   │ imported are the only       │   ║   the "Thoughts ⌄ /     ║
   │ ones an answer may cite.    │   ║   Drafting the answer"  ║
   │                             │   ║   collapse tells the    ║
   │                             │   ║   story in one glance   ║
   └────────────────────────────┘   ╚═════════════════════════╝
        488px on paper                    688px field, 560px window
```

### 2.4 The passage — C4 band, and the page's one interaction

The citations act gets the band because it is the product's core claim, and it carries **M4, the
witness** — the single most product-specific interaction available (§8.2). On the answer exhibit,
focusing or hovering a citation chip marks the sentence it supports.

This is v1's own "witness" idea, which v1 then forbade by its no-click rule. It is the one place on
the page where a reader can do what the product does.

### 2.5 The reading — C2, mirrored

`exhibit-12` is the domain-by-domain reading log — Wikipedia, Commons, archive.org, arXiv, Crossref,
Open Library. The catalogue calls it *"**Only capture that shows real domain-by-domain fetching**"*
and the reference report's #9 says legibility is what creates the impression of a real product. It
also gives the copy something v1 could only assert: the page can say *"you can watch it decide"* and
then show it deciding.

### 2.6 The dispute — C2, portrait

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

Portrait window (360×470) in the field, breaking the page's landscape rhythm deliberately — Tempo
uses a phone-shaped mock for the same reason.

### 2.7 The machine — C3 diptych

The privacy claim needs **two** captures and no single one carries it: dark `settingsresearch.png`
shows *"Web research: off"* and *"Scrape (keyless, no service) — No API keys, no third-party search
API"*; light `settingsmodels.png` shows *"Ollama (default) — Local model server"* at
`http://localhost:11434` and the six model roles. The catalogue is explicit: *"Together they cover
the claim; neither alone does."* And they are one dark and one light — which the §3.4 theme rule
makes a virtue rather than an accident.

### 2.8 The workspace — three-up

Genre-standard three-up (Gamma, Gemini Notebook). Icons, not images: the library, the notes pane,
and the viewer. Reuses the **five Lucide icons already extracted** (24px viewBox, stroke 2, drawn at
the app's own 14/16px) — no new icon work, and the provenance stays as recorded.

### 2.9 The evidence, §2.10 Questions, §2.11 The name

See §9 for the evidence band, §8.3 for the accordion, and §1/§6 for the close. The close merges
v1's "the name" section (the brief: *"the name means 'one who has seen' and gets a real section"*)
with the poster move, which is where it belongs.

---

## §3 · Composition system

### 3.1 The grid

All widths derive from one measured fact: **every capture is 1918px wide and is a 2× capture of a
959 CSS-px window.** So:

| Token | Value | Derivation |
|---|---|---|
| `--win` | **959px** | 1918 ÷ 2 — the app window's **native** CSS width |
| `--field-pad` | **64px** | Tempo's measured ≈65px |
| `--field` | **1087px** | `--win` + 2 × `--field-pad` |
| `--page` | **1240px** | genre range 1150–1300 |
| `--measure` | **66ch** | kept from v1; correct typography, not a style |
| `--gutter` | `clamp(20px, 5vw, 64px)` | |

**The consequence is the most useful number in this plan.** An exhibit displayed at exactly
`crop_px ÷ 2` is **pixel-perfect at both 1× and 2× DPR, with no upscaling** — because the source is
a 2× capture. Legibility is preserved too: at that display width the app's own 16–17px text renders
at its true size. Every exhibit in Appendix A is sized this way. It is why v2 needs no new captures
to look right, and why its weight lands far below the genre (§12).

### 3.2 The five compositions

**C1 · field-full** — full-bleed teal; heading, subhead and CTA centred; window at `--win` centred,
64px padding inside. Used by the hero only.

**C2 · split** — paper text column **488px** (≈57ch) beside an inset teal field **688px** holding a
**560px** window. Alternates side; the side is part of the rhythm.

**C3 · diptych** — paper ground; one inset teal field `--field` wide containing two windows
side-by-side (dark + light), each ≈470px.

**C4 · band** — full-bleed teal; a wide 959px window spanning it; heading above, inside the field.

**C5 · poster** — full-bleed teal; the giant wordmark, with `exhibit-16` overlapping its lower third.

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
| `--shadow` | `0 24px 60px rgba(4,10,12,.45)` | Breezy measured: ~9% darkening decaying over ≈50px CSS |
| `--rule` | `#E4E6E9` | measured: the app's light table separator |
| `--rule-field` | `rgba(255,255,255,.10)` | 1px hairlines separating dark from dark |

**Hairlines are 1px, never heavy strokes.** Freebuff and Tempo separate black-on-black with a
hairline plus a 4% card lift. Nothing on this page uses a border thicker than 1px except the field
edge, which is a seam rather than a stroke.

### 3.4 The theme rule

> **Light-theme windows stand on teal fields. Dark-theme windows stand on paper.**

Both themes are real (the app ships White as default and Black as selectable), so this invents
nothing — and it turns a fact into a system: the window always *contrasts* its ground, so it always
reads as an object. In the field, a 1px `--rule-field` seam separates window from ground, which is
Tempo's measured technique. On paper the `--shadow` does the separating instead.

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
instruction to re-run the tool. That assertion is 1 of the 51 the link gate now carries.

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
| `--t-h3` | 26px | three-up heads |
| `--t-h2` | **34px** | section headings (genre 25–31) |
| `--t-display` | **`clamp(56px, 7.4vw, 94px)`** | **used exactly once — the hero** |

**Display ÷ body = 94 ÷ 17 = 5.5×.** In the genre's top tier, and reached by *raising the top*, not
by shrinking the body.

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

Full geometry in **Appendix A**. Nine exhibits, each derived from a capture in the 36, each cropped
so its display width is exactly `crop_px ÷ 2` (§3.1).

| id | Proves | Source |
|---|---|---|
| `exhibit-10` | it answers from what you gave it | `Black/Question1.png` |
| `exhibit-11` | every claim points at a passage | `Black/verifiedsource.png` |
| `exhibit-12` | you can watch it decide | `Black/FetchingPages.png` |
| `exhibit-13` | it keeps the disagreements | `Black/Question2.png` or `viewingnote-editingsource.png` |
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
moved into the note above the script, which the build strips. 5,010 B remain, and the overage is code
for three jobs this table did not have when the sentence was written: the rail's current-section
tracking (M1c), the close's parallax (M6), and the hero's own controls (M9).

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

### 7.4 Reduced motion

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
| `document.index_html_bytes` | exact, re-baselined to **62,469 B**; LF-only so platform-independent; **75,025 B** on 2026-09-19 after a night of work on the page, each step itemised in `budget.json`'s own note |
| `document.index_html_gzip_ceiling` | re-baselined to **18,400 B** with headroom — **never an equality** (the 2026-09-19 toolchain lesson); **20,480 B** after the reading list, at a round KiB rather than another 2.1% margin, so it stops being edited on every commit that touches the document |
| `document.inline_js_bytes` **(new)** | exact, and it exists because §7 carried a 4 KB JS budget that nothing measured: the page shipped 5,599 B, of which 1,250 B was `//` prose arriving with every document and being parsed as script. Figure is now **5,010 B** |
| `totals.phone_1x` / `retina_2x` | re-baselined over 9 exhibits: **194,064 B** / **388,356 B**, and again on 2026-09-19 over 9 exhibits **plus 4 phone crops** at **237,991 B** / **500,885 B** — the inventory grows while what a device *downloads* shrinks, because those four exhibits now serve a narrower crop below 430px |
| `totals.exports_all_*` | **renamed `exports_all_36`** and the `.png` suffix dropped from the sum, because PNG left the shipped set; **renamed again to `exports_all`** when the phone crops took the set from 36 files to 52 and the number in the name stopped being true |
| `ARTIFACT_FILES` | re-baselined to **138** (the whole +18 is 9 exhibits × 4 files against 3 × 6), then to **154** on 2026-09-19 (+16 = 4 phone crops × 4 files), then to **156** (+the generated library index, +`/theme.js`) |
| `library.*` **(new)** | the carried library as four numbers: `page_count` 75, `page_bytes` exact, `index_bytes` exact (generator output, so a change means a page or the generator changed), and the shared files by size. Pages are asserted as a count and a total rather than file by file, because their bytes move whenever anyone edits a summary |
| `verify-copy.py` **(new tool)** | Stage 9's checks 10 and 11: the humanizer pass as a rule rather than a memory, and §10.4's release-claim rule in both prose and tables. Both run a positive control before they trust their own silence, and an allow-list entry that stops matching fails the build |
| **`composition` (new)** | asserts the page has **≥ 10 sections, ≥ 4 distinct composition classes, ≥ 1 sticky element, ≥ 1 `<details>`, and ≤ 1 display-size element** |

That last gate is the point. v1 had 53 assertions and none could see that the page was nine identical
sections. **A composition gate is what would have caught it**, and it is the only gate here that
asserts the *design* rather than the bytes.

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

**It audits the states a render never shows, too.** §3.6 promises `prefers-contrast: more` on both
halves, and §3.4's theme architecture promises a dark world to a reader whose machine is dark and
who has stored no choice. Until 2026-09-19 only the *existence* of those rules was asserted, which is
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

Nothing is invented in the tool and no colour is written down there, which makes the failure mode
the honest one: **every emulated state prints how many of the page's own rules it found**, because
zero rules is a page that does not style the state, not a state that passed. The landing page is
audited in three states and the library in four, at 1440 and at 390, and all of them are clean under
AA, and none of them was clean by accident: a copy of the artifact with a bad contrast block reports
**61** failures under the emulated state and zero without it. Two of those states are the ones no
render had ever covered, and both now confirm what the stylesheet says rather than what it promises:
a dark machine with no stored choice gets the dark world (`--canvas` #0A0A0A, `--mist` #A5A19B), and
a stored light choice still wins on that same machine. The landing page reports **zero** rules for a
dark machine, which is also true of it: it ships one world and has no dark theme at all, which §3.4
and the print block both say in passing and nothing has ever questioned.

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
| `exhibit-12` | `Black/FetchingPages.png` | `1242x880+318+100` | 621×440 | crop D; the reading log |
| `exhibit-13` | `Black/viewingnote-editingsource.png` | `720x940+500+60` | 360×470 | crop B; portrait. Three-pane split — do not use the default |
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
