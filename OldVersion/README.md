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
   through the stylesheet's media query. Any `<noscript>` block goes
   *after* the stylesheet link: it is a stylesheet itself as far as the
   cascade is concerned, and at equal specificity the later rule wins,
   so a block in the head beats nothing and loses everything.
3. **Reduced motion is neutralized.** Every animation has an exit in
   the reduced-motion block.
4. **One textured band per page.** The privacy section is the single
   textured moment on the homepage, and the 404 panel is the single one
   on its own page. Its ground is a studio fabric photograph supplied to
   the project, fitted as one cover-sized crop at the file's natural
   aspect, with a plain dark scrim over it in CSS so light text stays
   readable across the weave. It is never tiled, stretched or recolored.
   The file that ships is a 2560px copy of the studio's 5184px original:
   same frame, same Adobe RGB profile, same pixels, metadata dropped,
   because the band is 639 CSS px tall behind a 75% scrim and the rest of
   the resolution was unseeable. Where the picture came from, the exact
   transform, and the measured proof the swap is invisible are recorded in
   `assets/textures/SOURCE.md`. Do not add a second texture elsewhere.
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

## The project log

`/changelog/` is written from repository history, never from memory. The
newest `<h2>` date on the page is the anchor, so the ritual is one command:

```bash
LAST=$(grep -o '<h2>[0-9-]*' changelog/index.html | head -1 | cut -c5-)
git log --since="$(date -d "$LAST + 1 day" +%F)T00:00:00" --reverse \
  --date=short --pretty='%ad %s'
```

Two details in it are deliberate, because each one fails silently:

- the anchor is the day *after* the newest entry, so the day already
  written is not printed a second time;
- the time is spelled out. With the date alone, `git log --since=2026-09-17`
  returns nothing even on a day that has commits in it, which would let the
  log claim a quiet day that never happened. The `T00:00:00` form is the one
  that is reliable here.

Then write one `<h2>` per day above the previous newest, bump the page's
`<lastmod>` in `sitemap.xml` to the newest date, and commit the log with the
work it describes. Pages whose visible content did not change keep their
date: a `lastmod` is a claim about the page, not about the file's mtime.

## Continuous improvement

`.claude/skills/continuous-improvement/SKILL.md` is a standing assignment: an
unbounded loop that audits the site, harvests ideas from reference sites, puts
them through a council, ships them one at a time, and verifies each one with its
own eyes before it counts as done. It commits directly to `main`, so its commits
are the site's commits. The creative surface is `index.html`; the slug pages
under folders are maintained rather than reinvented.

- **[`IMPROVEMENTS.md`](IMPROVEMENTS.md)** is its report file, newest cycle
  first. That is where to read what the loop has been doing.
- **`.improvement/`** is its scratch: audit logs, council verdicts, the defect
  register, the fleet checkers, the browser probes, and the artefacts a
  creativity pass made and did not ship. Gitignored, so it never ships. It also
  never crosses a clone, which is why the loop writes `Loop-Cycle:`,
  `Loop-Budget:`, `Loop-Open:` and `Loop-Bet:` trailers on its commits, plus
  `Loop-Full-Audit:` or `Loop-Creativity:` when one of those passes ran: the
  trailers are the only state that survives, and a missing register is not a
  clean site.
- **`tools/`** holds the generators for anything the site did not get from a
  camera or a designer. A generated asset ships the script that made it, because
  otherwise nobody can rebuild it. `assets/textures/SOURCE.md` is the convention
  it follows.
- **`.claude/settings.json`** carries a SessionStart hook that tells a new
  session the loop exists, so it restarts on its own instead of waiting to be
  asked. Removing that hook turns it off.

Beside its cycles it runs two triggered passes. A **full audit** (Phase 7) runs
when a budget trips: it judges the loop's own shipped work and reverts what did
not earn its cost. A **creativity pass** (Phase 8) runs when three cycles carry
the bet obligation unspent, or when the register runs dry, and it makes things
instead of describing them — Blender, Inkscape, ImageMagick, ffmpeg and Python,
all rendered at build time so the tool never reaches the reader. It is judged on
the specific faults it can name in its own work, not on taste.

The loop's rules live in the skill file, including the budget table it audits
itself against. Change how the site is measured and change it there in the same
commit, or the numbers stop meaning anything.

## Deploy

GitHub Pages, deploy from branch, `main` at root. The `CNAME` file
holds istor.fyi; DNS points it at the Pages endpoints. `404.html` is
picked up automatically and styles itself to match.

`08eaa6e8b97d4b94943057b2c49bd712.txt` at the root is the IndexNow key file. It
has to stay at the root, named exactly that, holding exactly that string, or the
site's IndexNow submissions stop verifying. It is not junk and it is not an
orphan.

## Brand

SVG masters, the two-tier icon set, and the Greek wordmark live in
`brand/`. The wordmark face is GFS Didot and ships with the page.