"""Generate the page's ground grain. Deterministic: fixed seed, no magick noise.

    python Source/tools/make-ground.py

Writes Assets/textures/ground-grain.png — one tile, 128x128, alpha-baked in the page's ink so it
sits on --paper AND --chrome without a tint channel (a background-image cannot be
recoloured by CSS). Grain only: no lines. The hairline is the page's structural
mark and a ruled ground would spend it.
"""

import random
from PIL import Image

SIZE = 128          # 1 CSS px per pixel; shipped with background-size: 128px 128px
SEED = 20260918     # the date the ground was specified
INK = (0x17, 0x17, 0x17)

# (probability per pixel, alpha) — coarse dots carry the tooth, fine dots keep it
# from reading as a regular grid. Both are well under the threshold at which a
# reader would call it a texture.
LAYERS = [
    (0.0075, 0.075),   # ~120 dots, the visible tooth
    (0.0022, 0.045),   # ~36 dots, breaks the rhythm
]

img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
px = img.load()

rng = random.Random(SEED)
for density, alpha in LAYERS:
    for y in range(SIZE):
        for x in range(SIZE):
            if rng.random() < density:
                a = int(round(255 * alpha))
                # accumulate rather than overwrite, so overlaps darken slightly
                r, g, b, old = px[x, y]
                px[x, y] = (INK[0], INK[1], INK[2], min(255, old + a))

img.save("../../Assets/textures/ground-grain.png", optimize=True)
print("Assets/textures/ground-grain.png written")
