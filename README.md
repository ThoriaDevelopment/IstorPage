# IstorPage

The website for Istor, a local-first research notebook. It lives at
[istor.fyi](https://istor.fyi) and in this repository as plain files:
one HTML page, one stylesheet, one small script, and the assets they
reference. There is no framework, no build step, and nothing to
install to work on it.

## Preview locally

```
python -m http.server 8931
```

Then open http://localhost:8931/index.html. Any static file server
works; Python's is just the one that is already there.

## The laws

These are the rules the page is designed around. A change that breaks
one of them is a regression, even if it looks fine.

1. **Static, with zero network requests at runtime.** Everything a
   visitor's browser needs ships in this repository: fonts, texture,
   icons. The page makes no requests beyond its own files, ever.
2. **The page works without JavaScript.** The script only adds motion
   and state: entrance timing, the privacy rotator, the demo
   rebuild. With JavaScript off, every section is visible, the demo
   shows its first question's end state, and theme follows the OS
   through the stylesheet's media query.
3. **Reduced motion is neutralized.** Every animation has an exit in
   the reduced-motion block.
4. **One textured band per page.** The privacy section is the single
   textured moment. Its grain is real paper tooth (ambientCG Paper001,
   CC0), cropped and baked to carry the band's teal accent. Do not add
   a second texture elsewhere.
5. **No fabricated quotes.** No testimonials, no press logos, no
   invented coverage. If real press coverage arrives, it can be added
   with permission. Until then, nothing.
6. **The gradient is two colors per ground.** `--g1` and `--g2` swap
   per theme; components read tokens, never literals.

## Theme mechanics

Dark tokens live in two places on purpose: inside the dark media
query (guarded so an explicit light choice wins) and under
`:root[data-theme="dark"]`. A head script stamps `data-theme` before
first paint from the stored choice (`istor.site.theme` in
localStorage) or the OS preference. If you add a color, add it to the
token blocks, not to a component rule.

## Deploy

GitHub Pages, deploy from branch, `main` at root. The `CNAME` file
holds istor.fyi; DNS points it at the Pages endpoints. `404.html` is
picked up automatically and styles itself to match.

## Brand

SVG masters, the two-tier icon set, and the Greek wordmark live in
`brand/`. The wordmark face is GFS Didot and ships with the page.