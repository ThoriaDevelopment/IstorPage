# assets/textures

## fabric-texture.jpg

Source: supplied to this project by Thoria for the istor.fyi privacy band
(commit 90eaa6e, "Privacy band: the tooth is now the studio fabric photo").
It is not a stock, scraped or CC0 asset; it is the studio's own photograph.

Provenance: camera original, 5184x3456, Canon EOS 7D, Adobe RGB (1998), shot
2019-12-27 per the file's own EXIF. The camera original is kept in git at blob
`6c752295e76bfc5cc340240516fc67b0f73dd53f`, which is where the proof below
reads it from:

```
git cat-file blob 6c752295e76bfc5cc340240516fc67b0f73dd53f > original.jpg
```

How it ships: the same frame, the same pixels, at the size the band can use.
2560x1707, JPEG quality 84, progressive, 4:2:2, 1,506 KB, 8.3x smaller than the
camera original. What changed, and what deliberately did not:

- resolution 5184x3456 to 2560x1707, one LANCZOS step, same 3:2 frame, so the
  cover crop selects the same region it always did;
- EXIF, XMP and Photoshop metadata dropped (about 40 KB; orientation was 1, so
  nothing about display depended on it). The camera details above are the copy
  of record;
- the Adobe RGB (1998) profile is **kept**. The pixels are not converted, so a
  colour-managed browser renders the band exactly as it rendered the original.
  Converting to sRGB would change the picture for anyone whose browser does not
  honour profiles, which is a craft decision, not a size decision: see backlog
  I-13;
- no recolouring, tiling or stretching, ever.

Why 2560x1707: it is the smallest raster and the lowest quality that keeps the
swap invisible at every band size the site can produce. The band box, measured
in the browser, is 639 CSS px tall at every width from 375 to 3825 px; the
widest real device raster asked for is 3825x639 (4K, DPR 1) and the tallest is
1125x2073 (a phone at DPR 3, where the cover crop uses the image's full height).
The choice was made by measurement, not by taste:

```
python .improvement/build-texture.py          # dry run: prints what it would write
python .improvement/build-texture.py --apply  # writes the shipped file
python .improvement/texture-proof.py          # verifies what ships, against the original
python .improvement/texture-proof.py --ladder # the size/quality ladder it was chosen from
```

The proof composites both files exactly as the page will — cover crop, resample
to the real device raster, then the flat `rgba(10, 16, 18, 0.75)` scrim — and
compares them with SSIM at every measured size:

| condition | SSIM mean | visible delta (0-255) |
| --- | --- | --- |
| phone 375x691 @1x | 0.9999 | 0.13 |
| phone 375x691 @3x | 0.9925 | 1.11 |
| tablet 753x628 @1x | 0.9999 | 0.11 |
| tablet 753x628 @2x | 0.9987 | 0.49 |
| laptop 1425x639 @1x | 0.9997 | 0.25 |
| laptop 1425x639 @2x | 0.9942 | 1.00 |
| desktop 1905x639 @1x | 0.9988 | 0.51 |
| wide 2545x639 @1x | 0.9963 | 0.92 |
| 4K 3825x639 @1x | 0.9904 | 1.29 |
| 404 panel 544x420 @1x | 0.9999 | 0.07 |
| 404 panel 544x420 @2x | 0.9998 | 0.18 |

End to end, in the browser rather than in the model: `.improvement/band.html`
renders the band's exact box and scrim with either file, and the two headless
Chrome screenshots taken with it came out at SSIM 0.9955, mean delta 0.94/255,
grain intact (luminance standard deviation 17.95 before, 18.14 after).

Where it is used, exactly twice:

- `styles.css`, `.privacy-inner`: one `background-size: cover` crop of the
  homepage privacy band, under a `rgba(10, 16, 18, 0.75)` scrim so the light
  text stays readable across the weave's bright patches. The photo itself is
  untouched: no tiling, no stretch, no recolor.
- `404.html`, `.panel`: the same treatment at panel size.

Any change to this file is a change to a law. `README.md` law 4, the comment
above `.privacy-inner` in `styles.css`, and this note all describe the same
picture, and they are rewritten together or not at all.
