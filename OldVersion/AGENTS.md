# Working rules for istor.fyi

Rules for any agent or person editing this repository. Use MUST / SHOULD /
NEVER as written.

This file has two parts. **Part 1** is this site's own law and outranks
everything else. **Part 2** is a working cheatsheet adapted from Vercel's Web
Interface Guidelines (MIT, https://github.com/vercel-labs/web-interface-guidelines),
filtered down to the rules that apply to a static site. **Part 3** lists the
upstream rules deliberately not applied here, so nobody reintroduces them by
accident.

---

## Part 1 · This site's law

Read `README.md` first. It is the canonical statement of the site's laws. The
short version, because every one of these has been broken by a well-meaning
edit at least once:

- **MUST: the site makes zero network requests at runtime.** No CDN, no Google
  Fonts, no analytics, no third-party anything. Every asset is bundled. A new
  `<link>` to an external host or a new `@import` is a regression, not a
  feature.
- **MUST: the site works without JavaScript.** Content, navigation and the
  download path all function with scripting off. Any `<noscript>` block goes
  *after* the stylesheet link, because at equal specificity the later rule wins.
- **MUST: reduced motion is neutralized, not merely shortened.** Motion is a
  garnish on a site that must read correctly standing still.
- **MUST: one textured band per page.** The fabric photograph is used exactly
  twice in the whole site (the privacy band and the 404 panel). It is never
  tiled, stretched or recolored, and it never appears a second time on one page.
- **MUST NOT fabricate quotes, testimonials, press logos, coverage, pricing or
  roadmap.** If it is not real and verifiable, it does not go on the page.
- **MUST: keep dashes out of site copy.** Prefer periods, commas and colons.
  Restructure the sentence rather than reaching for an em dash.
- **MUST: the mark obeys the ground-law.** Red eye on a light ground, blue on a
  dark ground. Never mixed.
- **MUST: keep the two theme blocks in sync.** `styles.css` defines the dark
  tokens twice on purpose: once under `:root[data-theme="dark"]` and once,
  byte-identically, inside `@media (prefers-color-scheme: dark)` under
  `:root:not([data-theme="light"])`. The duplicate exists so the page paints
  correctly before JavaScript runs. Update both or the pre-JS flash regresses.
- **MUST NOT touch `08eaa6e8b97d4b94943057b2c49bd712.txt`.** It is the IndexNow
  key. It stays at the root, named exactly that, holding exactly that string,
  or IndexNow submissions stop verifying.

The design brief and the adopted patterns live in
`.claude/skills/istor-brand/SKILL.md` and `design-references.md`. Read those
before designing anything.

### Assets

`tools/README.md` is the law for generated assets: **a generated asset ships
the script that made it.** New assets are produced by committed scripts, not by
hand, and not by a tool that left no trace.

Two known traps, both verified:

- **The brand master does not rasterize outside a browser.** `brand/istor-page.svg`
  re-inks through CSS custom properties, and neither Inkscape nor ImageMagick
  resolves `var()` inside SVG presentation attributes. Inkscape renders the page
  as a solid black shape; ImageMagick renders nearly nothing. Resolve the
  variables to concrete colors before rasterizing. Browsers are unaffected.
- **`magick`, never `convert`.** On Windows, `convert` is
  `C:\WINDOWS\system32\convert`, the FAT-to-NTFS tool, and
  `convert /FS:NTFS C:` does real damage.

---

## Part 2 · Web interface rules that apply here

Adapted from Vercel's Web Interface Guidelines (MIT). Framework-specific rules
have been removed; see Part 3.

### Keyboard

- MUST: Full keyboard support per [WAI-ARIA APG](https://www.w3.org/WAI/ARIA/apg/patterns/)
- MUST: Visible, unobscured focus rings (`:focus-visible`; group with `:focus-within`); sticky or fixed elements never cover focus
- NEVER: `outline: none` without a visible focus replacement

### Targets and input

- MUST: Hit target ≥24px, mobile ≥44px; if the visual is smaller, expand the hit area
- MUST: Mobile `<input>` font-size ≥16px, to prevent iOS zoom on focus
- NEVER: Disable browser zoom (`user-scalable=no`, `maximum-scale=1`)
- MUST: `touch-action: manipulation` to prevent double-tap zoom
- SHOULD: Set `-webkit-tap-highlight-color` to match the design

### State and navigation

- MUST: The URL reflects state. This site uses in-page anchors heavily, so deep links stay deep links
- MUST: Back and Forward restore scroll position
- MUST: Navigation uses `<a href>`, so Cmd/Ctrl-click and middle-click work
- NEVER: Use `<div onclick>` for navigation
- MUST: `scroll-margin-top` on headings, so anchors do not land under the sticky header

### Animation and motion

- MUST: Honor `prefers-reduced-motion`
- SHOULD: Prefer CSS. Here that is not a preference, it is the law: there is no animation library and no JavaScript-driven motion
- MUST: Animate compositor-friendly properties only (`transform`, `opacity`)
- NEVER: Animate layout properties (`top`, `left`, `width`, `height`)
- NEVER: `transition: all`. List the properties explicitly
- MUST: Correct `transform-origin`, so motion starts where it physically should
- MUST: SVG transforms go on a `<g>` wrapper with `transform-box: fill-box`
- SHOULD: Choose easing to match the change, and animate only to clarify cause and effect

### Layout

- SHOULD: Optical alignment. Adjust by a pixel when perception beats geometry
- MUST: Deliberate alignment to grid, baseline or edges. No accidental placement
- SHOULD: Balance icon and text lockups by weight, size, spacing and color
- MUST: Verify at mobile, laptop and ultra-wide widths
- MUST: Respect safe areas with `env(safe-area-inset-*)`
- MUST: No unwanted horizontal scrollbars. Fix the overflow
- SHOULD: Flex and grid for layout, never JS measurement

### Content and accessibility

- MUST: `<title>` matches the current context
- MUST: No dead ends. Always offer a next step or a way back
- MUST: Hierarchical `<h1>` to `<h6>`, and exactly one `<h1>` per page
- MUST: A "Skip to content" link
- MUST: Prefer native semantics (`button`, `a`, `label`, `table`) before reaching for ARIA
- MUST: Accurate `aria-label`; decorative elements get `aria-hidden`
- MUST: Icon-only controls have a descriptive `aria-label`
- MUST: Accessible names exist even when the visual omits a label
- MUST: Status is never carried by color alone. Add a redundant cue
- MUST: Design the empty, sparse, dense and error states
- MUST: Text containers survive long content. Flex children need `min-w-0` to allow truncation
- SHOULD: Curly quotes, and `text-wrap: balance` to avoid widows and orphans
- MUST: `font-variant-numeric: tabular-nums` where numbers are compared
- MUST: The `…` character, not three periods
- MUST: Locale-aware dates, times and numbers via `Intl`
- SHOULD: `translate="no"` on brand names, code tokens and identifiers, so auto-translation cannot garble them
- MUST: Non-breaking spaces in `10&nbsp;MB` and in brand names

### Forms

The site currently has no form. If one is ever added, these apply:

- NEVER: Block paste in `<input>` or `<textarea>`
- MUST: Accept free text and validate after, rather than blocking typing
- MUST: Errors inline next to their fields; on submit, focus the first error
- MUST: `autocomplete` plus a meaningful `name`, and the correct `type` and `inputmode`
- MUST: `autocomplete` and 2FA compatible; allow pasting codes
- MUST: No dead zones on checkboxes and radios; label and control share one hit target
- MUST: Trim values, to absorb trailing spaces

### Performance

- MUST: Measure under CPU and network throttling, and disable extensions that skew runtime numbers
- MUST: Preload above-fold images; lazy-load the rest
- MUST: Prevent layout shift with explicit image dimensions
- SHOULD: `<link rel="preload" as="font">` with `font-display: swap` for critical fonts
- SHOULD: `<video autoplay muted loop playsinline>` over an animated GIF, and always provide a reduced-motion still

### Dark mode and theming

- MUST: `color-scheme` set correctly for each theme
- SHOULD: `<meta name="theme-color">` matches the page background
- MUST: A native `<select>`, if one is ever added, needs explicit `background-color` and `color` for Windows

### Design

- SHOULD: Layered shadows, ambient plus direct
- SHOULD: Nested radii: child ≤ parent, concentric
- SHOULD: Hue consistency. Tint borders, shadows and text toward the background hue
- MUST: Meet contrast. Prefer [APCA](https://apcacontrast.com/) over the WCAG 2 ratio for perceptually judged text
- MUST: Increase contrast on `:hover`, `:active` and `:focus`
- SHOULD: Match browser UI to the background
- SHOULD: Avoid dark gradient banding. The site uses gradients, so this one is live: banding is the failure mode to watch for

---

## Part 3 · Upstream rules deliberately not applied here

These are real rules for real sites. They are wrong for this one. Do not
reintroduce them:

- **Hydration rules** (`value` with `onChange`, guarding date rendering against
  mismatch). There is no React and nothing hydrates.
- **Re-render tracking** (React DevTools, React Scan, controlled vs uncontrolled
  inputs, virtualizing lists over 50 items, batching layout reads and writes).
  There is no render loop to profile.
- **Optimistic UI and rollback.** There are no mutations. The site is read-only.
- **`<Link>` and framework routing.** Plain `<a href>` is correct here and
  needs no replacement.
- **Mutation latency targets** (POST/PATCH/DELETE under 500ms). No requests are
  made.
- **Password manager and 2FA compatibility.** No accounts on this site.
- **`<link rel="preconnect">` for CDN domains.** There are no CDN domains, and
  adding one would break the first law in Part 1.

If a redesign genuinely needs one of these, that is a decision for Thoria, not
a drive-by edit. Raise it rather than assuming.

---

*Part 2 adapted from Vercel's Web Interface Guidelines, MIT licensed,
https://github.com/vercel-labs/web-interface-guidelines. Where upstream and
this file disagree about what applies to istor.fyi, this file wins; where they
disagree about the underlying rule, upstream wins and this file has a bug.*
