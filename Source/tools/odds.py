"""The odds that the temperature plate and the dial under it are both drawn from.

    (no command line: imported by make-temperature.py, build-site.py and verify-links.py)

WHY THIS IS A MODULE AND NOT A CONSTANT IN EACH FILE. `/what-is-temperature/` now has two
things made of the same four numbers: a plate with three fixed settings on it, and a
control the reader can drive. The moment those live in two files they are two answers
waiting to disagree, and the disagreement would be invisible - both would look right on
their own. So the candidates, the odds, the settings and the softmax over them are written
once, here, and the three callers import them:

  * make-temperature.py draws the plate from them,
  * build-site.py fills the control's table from them at build time,
  * verify-links.py recomputes them and compares them to what shipped.

THE CONTROL'S ARITHMETIC IS DONE HERE TOO, and that is the point of the table. The slider's
script does no maths at all: it reads a table of widths that was computed by this file at
build time, so what a reader drags and what the plate beside it drew cannot disagree. The
alternative - the same softmax written again in JavaScript - is a second implementation of
the one thing on this page a reader can check by hand.
"""

import math

# The four candidates for one next word, in the order a model would rank them, and the
# odds it holds. THE ORDER IS LOAD-BEARING: the plate compares the same four words in the
# same places across three bars, and the control's bar keeps that order at every setting,
# which is only true if the list is sorted once, here.
CANDIDATES = ("clear", "similar", "mixed", "vague")
LOGITS = (3.0, 2.6, 2.2, 1.8)

# The three settings the plate draws: the low end the page recommends for factual work,
# the middle most tools ship, and a high end for drafts.
SETTINGS = (0.5, 1.0, 2.0)

# The control's reach, and every position on it: near-zero to a setting the page calls
# high, in tenths, because a reader sets a slider in round numbers. The plate's three
# settings are all inside this range, which is asserted rather than intended, since a
# control that cannot reach a setting drawn above it would be nonsense.
STOP_STEP = 0.1
STOP_FIRST = 0.2
STOP_LAST = 2.0
STOPS = tuple(round(STOP_FIRST + STOP_STEP * i, 1)
              for i in range(int(round((STOP_LAST - STOP_FIRST) / STOP_STEP)) + 1))

# The control's own bar: a 300 unit band with the same paper between its segments as the
# plate's bars, so the two drawings read as one thing.
DIAL_BAND = 300.0
DIAL_GAP = 2.0
DIAL_HEIGHT = 22.0


def softmax(logits: tuple, temperature: float) -> tuple:
    """The odds the page is about: divide by the setting, then normalise.

    Written out rather than imported from a library because this file IS the model the
    drawing claims to be, and the checks run it a second time against what shipped.
    """
    scaled = [l / temperature for l in logits]
    hi = max(scaled)
    exps = [math.exp(s - hi) for s in scaled]
    total = sum(exps)
    return tuple(e / total for e in exps)


def shares(temperature: float) -> tuple:
    return softmax(LOGITS, temperature)


def free_width(band: float = DIAL_BAND, gap: float = DIAL_GAP) -> float:
    """A band minus the paper between its segments, which is what the shares divide."""
    return band - gap * (len(CANDIDATES) - 1)


def widths(temperature: float, band: float = DIAL_BAND, gap: float = DIAL_GAP) -> tuple:
    """One bar's segment widths at a setting, rounded to the hundredth of a unit.

    Rounded HERE rather than in the drawing, so the table the script reads and the widths
    the plate draws are the same numbers rather than two roundings of one number.
    """
    free = free_width(band, gap)
    return tuple(round(p * free, 2) for p in shares(temperature))


def table() -> list:
    """What the control reads on every drag: one row per position on the slider.

    Each row carries the widths AND the two percentages the readout prints, so the script
    has nothing to work out and a reader cannot see a number that was not computed with
    the bar under it. json.dumps writes it into the markup at build time.
    """
    out = []
    for t in STOPS:
        p = shares(t)
        out.append({"t": t, "w": list(widths(t)),
                    "top": round(p[0] * 100, 1), "last": round(p[-1] * 100, 1)})
    return out


# What a caller can rely on, asserted rather than assumed. The plate's settings have to be
# reachable from the control, and the odds have to be ranked: a table whose rows were
# unordered would draw bars that do not descend, and the control's legend is drawn once.
assert all(STOP_FIRST <= s <= STOP_LAST for s in SETTINGS), \
    "a setting the plate draws is out of the control's range"
assert all(a > b for a, b in zip(LOGITS, LOGITS[1:])), "the odds are not sorted"
assert abs(sum(shares(1.0)) - 1.0) < 1e-9, "the shares of a setting do not add up to one"
