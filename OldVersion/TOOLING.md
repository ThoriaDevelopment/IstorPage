# TOOLING.md · what the agent can actually reach

The cheatsheet. What is installed, what each piece is for, and the exact command
for the pieces that are not installed yet. Read this instead of re-deriving the
toolset from scratch.

Set up 2026-09-18. **Read `AGENTS.md` first** — that is the law for editing this
repository. This file is only about the instruments.

---

## 1 · MCP servers

| Name | Transport | What it is for |
|---|---|---|
| `figma` | HTTP, `https://mcp.figma.com/mcp` | Read and write real Figma files. Design system search, Code Connect, screenshot a node, push a page into Figma. |
| `playwright` | stdio, `cmd /c npx -y @playwright/mcp@latest` | Drive a browser: click, snapshot, screenshot. General automation. |
| `chrome-devtools` | stdio, `cmd /c npx -y chrome-devtools-mcp@latest --no-performance-crux --no-usage-statistics` | **The measurement instrument.** Performance traces, network log, Lighthouse, CSS inspection. This is the one that proves the site's budgets. |
| `accesslint` | stdio, shipped by the `accesslint` plugin | Accessibility scan, inspect and diff. |

All four are user scope, so they are available in `C:\Projects\Istor\Source` too.

### Why `chrome-devtools` is configured the way it is

- `--no-performance-crux` stops performance traces from sending URLs to Google's
  CrUX API. On a site whose first law is that nothing leaves the reader's machine,
  shipping page URLs to a third party from the measuring tool would be absurd.
- `--no-usage-statistics` opts out of Google's usage telemetry. Same reason. It is
  on by default.
- `cmd /c` wrapping is not decoration. Google's own Windows troubleshooting doc
  documents it: `npx` invoked from inside another process on Windows needs it.
- Verified: package `chrome-devtools-mcp` 1.9.0, Apache-2.0, Google LLC, engines
  `^20.19.0 || ^22.12.0 || >=23`, so Node 24.14.1 is in range.

### Measuring the zero-request law

The site makes **zero network requests at runtime**. That is the first law in
`README.md` and it is currently verified by nothing. Here is how to prove it.

**Do not audit over `file://`.** It gives the page an opaque origin, so
`fetch` and XHR to sibling files fail under CORS for reasons that have nothing to
do with the site. You would be measuring the harness. Serve over localhost:

```sh
python -m http.server 8000 --directory .
```

Then, with the browser on `http://127.0.0.1:8000`:

1. `navigate_page`, let it settle.
2. `list_network_requests` with `resourceTypes` narrowed to `fetch` and `xhr`.
   Anything there is a runtime request and is a defect. The document, stylesheet,
   font and image loads are the initial load, which is allowed to exist.
3. `evaluate_script` running `performance.getEntriesByType('resource')` and
   reporting each entry's `initiatorType` and `startTime`. This separates pre-load
   from post-load precisely, which the network log alone does not.
4. **The strongest test is positive, not observational.** Start a second server
   that only permits the local origin:

   ```
   claude mcp add chrome-devtools-airgap --scope user -- \
     cmd /c npx -y chrome-devtools-mcp@latest --no-performance-crux \
     --no-usage-statistics --allowedUrlPattern "http://127.0.0.1:*"
   ```

   `--allowedUrlPattern` needs Chrome 149+, and this machine has Chrome 151, so it
   is available. If the page renders and works with every non-local origin
   blocked, the law holds by construction. **This variant is untested here**; the
   server detaches from targets whose URL is not allowed, so confirm it still
   reaches the page before trusting a pass.

`lighthouse_audit` deliberately excludes performance. Use
`performance_start_trace` for LCP, INP and CLS.

---

## 2 · Penpot

**Status: not connected. One command remains, and it needs a key only Thoria can
generate.**

Penpot is a browser design tool. Its MCP server is hosted, so there is nothing to
install and no Docker involved:

```sh
claude mcp add --transport http penpot \
  "https://design.penpot.app/mcp/stream?userToken=YOUR_MCP_KEY"
```

Get `YOUR_MCP_KEY` from **design.penpot.app → Your account → Integrations → MCP
Server**. It is shown once. Then open a file in Penpot and connect the plugin via
**File → MCP Server → Connect**.

Verified 2026-09-18 against the live endpoint, not the docs:

- `initialize` and `tools/list` both answer. `serverInfo` is
  `{"name":"penpot","version":"1.0.0"}`.
- The tool surface is `execute_code`, `high_level_overview`, `penpot_api_info`,
  `export_shape`, `import_image`.
- The endpoint is stateful streamable HTTP and returns an `mcp-session-id`
  header you must echo back on later calls.

Three things that will bite:

- **Do not self-host.** There is no non-Docker path. Penpot's backend is Clojure
  and it needs PostgreSQL plus Redis or Valkey. Docker Compose, Kubernetes and
  Helm are the only official routes. The hosted free tier gives 8 team members,
  unlimited viewers, 10 GB storage and 7 day version history, which is ample for
  a marketing site mockup.
- **The local npx server is a trap on Windows.** `@penpot/mcp` is not a light
  launcher: its bin copies itself to a cache directory and runs
  `npx -y pnpm run bootstrap`, building every package from source. The `latest`
  npm tag is 2.15.4 while Penpot itself ships 2.17.x, and the plugin warns on any
  version mismatch. The npm tarball ships no README at all.
- **The remote server has no filesystem access.** `import_image` from a local path
  and `export_shape` to a local path are unavailable in remote mode. Download
  from Penpot and commit the file, or fall back to `figma`, which is already
  connected.

---

## 3 · Asset bench

Blender, Inkscape, ImageMagick, ffmpeg, Python, Node. `tools/bench.py` resolves
them and reports their state; `tools/README.md` is the law for generated assets.

```sh
python tools/bench.py
```

Note that **Blender and Inkscape are installed but not on PATH**, so nothing can
call them by bare name. `bench.find()` handles it.

---

## 4 · Design and quality skills

Installed at user level, so they apply in every repository, not just this one.

**Typography, 20 skills plus a `type` router**, from `jpoindexter/typography-skills`
(MIT). Relevant ones for this site: `typography-audit`, `typography-critique`,
`editorial-web-typography`, `hierarchy-and-scale`, `type-foundations`,
`typography-accessibility`, `font-loading-and-performance`, `microtypography`,
`responsive-typography`, `variable-fonts`.

**`apca-contrast`**, from `rhino-ty/apca-contrast-skill` (MIT). Stdlib only. Its
table output contains `≥`, which dies on Windows' default cp1252 stdout, so run it
as:

```sh
PYTHONIOENCODING=utf-8 python ~/.claude/skills/apca-contrast/scripts/apca.py ...
```

**`humanizer`** — pre-existing.

### Plugins

| Plugin | Marketplace | Verdict for this site |
|---|---|---|
| `web-quality-skills` | `addy-web-quality-skills` | Useful. Accessibility, best practices, Core Web Vitals, SEO. |
| `ux-design` | `wondelai-skills` | Useful as a thinking aid. Roughly 40 book-derived frameworks. |
| `design-assets` | `jezweb-skills` | Partly useful. Icon sets and favicons. Its image generator needs an API key and would send prompts off-machine. |
| `accesslint` | `accesslint` | Useful. Backed by the MCP server above. |
| `frontend-design`, `code-review`, `security-guidance`, `skill-creator` | `claude-plugins-official` | General purpose. |
| `kotlin-lsp`, `rust-analyzer-lsp` | `claude-plugins-official` | For `C:\Projects\Istor\Source`, not for this repository. |

### Deliberately not installed

Most of the design-skill ecosystem assumes React, Tailwind and Next.js. This site
is hand-written CSS with no build step, no framework, no runtime dependency and a
no-JavaScript requirement. Tailwind, shadcn, CSS-in-JS, JS animation and
framework Core Web Vitals skills are anywhere from useless to actively harmful
here. Do not add them because they are popular.

---

## 5 · Known traps

Both verified on this machine, both already recorded in `DESIGN.md` § 5.

- **The brand master does not rasterise outside a browser.** `brand/istor-page.svg`
  re-inks through CSS custom properties and neither Inkscape nor ImageMagick
  resolves `var()` in SVG presentation attributes. Use `tools/mark-export.py`,
  which resolves them first.
- **`magick`, never `convert`.** On Windows `convert` is
  `C:\WINDOWS\system32\convert`, the FAT-to-NTFS tool.
- **Keep generator stdout ASCII.** Windows consoles are cp1252 and raise
  `UnicodeEncodeError` on anything else.
- **Blender 5.x renamed the EEVEE enum** to `BLENDER_EEVEE`. The
  `BLENDER_EEVEE_NEXT` spelling raises `TypeError` on assignment.
