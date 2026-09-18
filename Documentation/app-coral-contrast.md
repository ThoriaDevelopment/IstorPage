# The app's coral status line fails AA

**An app-side defect, written up from the site's measurements.** This document lives in the
site repo because that is where the numbers were taken; the fix belongs to the app, and nothing
here changes the site. Flagged by Thoria on 2026-09-18: *"Write it up for the app."*

## The string

> Unverified — check the source.

It renders in the witness popover, under the source title, whenever a citation was retro-fitted
by the triage model rather than written by the answering model. Measured in
`Assets/Istor Screenshots/White/Question1.png` and again in the same moment captured four times
in `Black/` and `White/`.

## The measurement

Sampled from the darkest saturated pixels of the rendered line, not from source:

| | value | on white | verdict |
|---|---|---|---|
| the line as rendered | `#E85B5C` | **3.45:1** | fails AA small text (4.5:1) |
| the iris it is drawn from | `#F2726F` | **2.83:1** | fails AA and AA large |

Anti-aliasing runs between the two, so no sampling of that line clears the floor. Hue is
≈360°, saturation ≈75%, lightness 63% — a *light* coral, which is why it reads as decoration
and not as a warning at the size it is set.

## Why it is worth fixing rather than accepting

**This is the one string in the product that carries the honesty claim.** The rest of the app
is careful about provenance — the gate, the bands, the citation contract — and this line is
where a reader is told that a number was put there by a different model than the one that wrote
the sentence. If it is the hardest string on screen to read, the claim it makes is the one that
gets missed.

It is also the only *verdict* in the interface, and the interface already establishes that
verdicts are not carried by colour alone (the witness pairs its quote with a left rule). The
coral line has no such companion, so the state rests entirely on a hue that fails contrast.

## The fix, hue-preserving

Hold the hue and drop the lightness — the same move the site made, and the reason the site's
value is not simply a darker coral picked by eye:

| | hue | L | on white | on `#FAFAFA` |
|---|---|---|---|---|
| app, current | 359.9° | 63% | 3.45:1 | — |
| **proposed `--coral-ink` `#C7292A`** | **359.6°** | **47%** | **5.56:1** | **5.32:1** |

Hue moves 0.3° and lightness 16 points, so it still reads as the same coral family as the iris
and the wordmark's dot — it is the same colour, held at a legible weight.

**5.56:1 is not an accident.** It lands within a hundredth of the app's own accent `#0066CC`
(5.57:1) on the same ground, so a verdict never outweighs the citation it is attached to. A
warning that shouts louder than the thing it warns about gets read as an error state.

**Pair it with a rule.** The site sets it against a hairline so the state is never carried by
colour alone — worth doing in the app for the same reason the popover's quote already has one.

## What is *not* being asked

- **The other status colours are fine.** Amber `#B35208` is 5.1:1 and safe as text. Green
  `#4BB581` is 2.6:1 and is a **dot only, never text** — that constraint is already respected
  in every capture, so it is not a defect.
- **The iris and the wordmark's dot are fine.** Coral as *artwork* at display size has no
  contrast floor to clear; only this line, set at UI text size, does.
- **No change to the site.** `--coral-ink` `#C7292A` is already what the site ships, so if the
  app adopts it the two agree by construction rather than by coincidence.

## Status

**Open, app-side.** Not a site blocker — the site does not inherit the app's value and is
already compliant. This note exists so the measurement is not lost, and so the fix is a
one-line token change rather than a re-derivation.
