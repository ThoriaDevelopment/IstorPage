# IstorPage

The source for **istor.fyi**, the marketing site for **Istor**, a local, offline,
no-telemetry AI research notebook built by **Thoria**.

A new agent or harness picking this project up should read this file first. It says where the
persistent memory lives and what is in it, and it points at the documents that actually govern
the build.

## Agent memory: where it is

    %USERPROFILE%\.claude\projects\C--Projects-Istor-IstorPage\memory\

On this machine that resolves to `C:\Users\<you>\.claude\projects\C--Projects-Istor-IstorPage\memory\`.
The folder sits outside this repository and git here does not track it.

The folder name is derived from the project path: `C:\Projects\Istor\IstorPage` becomes
`C--Projects-Istor-IstorPage` with the separators replaced by dashes. That rule holds for any
project, so the same construction finds the memory for any other checkout.

If that folder is missing or empty, the harness is starting fresh and there is nothing to read.
The memory is not a build input: nothing in `Source/tools/` reads it.

### What is in it

- **`MEMORY.md` is the index.** One line per note. It is loaded into context at the start of
  every session, so it is a table of contents and never a place for content.
- **Every other file is one note holding one fact.** YAML frontmatter (`name`, `description`,
  `metadata.type`, `metadata.originSessionId`, `metadata.modified`), then a short body.
- **`metadata.type` is one of four values:**
  - `user`: who the user is, their role, expertise or preferences.
  - `feedback`: guidance on how to work, including the reason it was given.
  - `project`: ongoing work, goals or constraints that the code and git history cannot tell you.
  - `reference`: pointers to external resources, or measured values recorded from somewhere else.
- **Notes link to each other as `[[name]]`**, where `name` is the other note's `name:` slug.
- Two conventions in the bodies: `**Why:**` and `**How to apply:**` lines on `feedback` notes,
  and absolute dates rather than "yesterday" or "last week".

### The notes, one line each

| File | Type | What it holds |
|---|---|---|
| `developer-thoria.md` | user | Thoria is the developer of Istor; their information is at `https://thoria.fyi`, and they own the `ThoriaDevelopment` GitHub org holding both repos (site and product). Attribution and contact details must come from thoria.fyi rather than be invented. Pronouns are not stated, so they/them. |
| `thoria-working-directives.md` | feedback | How Thoria wants the work done. **Copy:** every string a visitor can read goes through the `humanizer` skill, and no em or en dashes in the site's own text; curly quotes are kept deliberately. **Questions:** prefer the question tool over asking in prose. **Unattended runs:** when Thoria says they are going to sleep, ask nothing, finish a goal and immediately set the next one, make the decisions yourself, commit and push are pre-authorised, and audit the work as you make it rather than adding without checking. |
| `istor-product-brief.md` | project | What Istor is and who it is for: a local, offline, no-telemetry AI notebook that makes 2B to 9B models accurate by removing hallucination and the false "that does not exist outside the training cutoff". Audience is researchers and academics plus writers and knowledge workers. **Primary action is download/install.** One landing page now, built so more pages can be added later. Light default, the og-card's teal for the close, azure accent, GFS Didot display over Inter body. |
| `istor-project-locations.md` | reference | Where everything lives, and the two naming traps. `istor.fyi` is the live site; `IstorPage` is the website repo; `Istor` is the **product** repo, a different thing. `C:\Projects\Istor` is the umbrella and `C:\Projects\Istor\Source` is the *application's* checkout, so bare "Source" means two different directories. The canonical origin is the root `https://istor.fyi/`, which is a build input rather than a deployment detail, because `og:image` must be absolute. |
| `istorpage-redesign-scope.md` | project | The from-scratch rebuild: new work in `Source/`, the old live site parked in `OldVersion/`, and `References/` holding the five screen recordings that are the design inputs. |
| `oldversion-is-not-context.md` | feedback | Nothing in `OldVersion/` is a fact, constraint or precedent unless Thoria points at it: not its `AGENTS.md`, not its `istor-brand` skill, not `DESIGN.md`. Its self-declared authority ("Part 1 is this site's own law and outranks everything else") is the trap, because reading it turns old choices into constraints. Raise a rule worth keeping as a proposal instead. |
| `webpage-and-app-design-are-independent.md` | project | The website and the app have independent design decisions and neither governs the other. `C:\Projects\Istor\design\DESIGN_PHILOSOPHY.md` is about the **application** and is not an input to site work. The reverse holds too. Shared decisions get raised as proposals. |
| `istorpage-design-plan-v2.md` | project | `SITE_DESIGN_PLAN_V2.md` is the governing spec. v1's precedence rule is retired, so disagreement is settled by measurement rather than by rank. Records the three deliberate deviations of the built page from v2: vertical full-width bands instead of a diptych, the witness living on the hero replica rather than a bitmap, and the ring-plate act. |
| `v1-plan-forbade-the-genre.md` | project | Why v1 was rejected: its own text bans the genre's devices. Section 8 Principle 2 forbids any response to a click ("no accordion, no tab, no disclosure"), section 8 Motion says everything else is static, section 7 caps the page at three bitmaps. Thoria, 2026-09-19: *"we just created a blog post. How? Why?"* The generalisable lesson is that the old verification suite was 53 green assertions on a page that read as an essay, and no assertion could detect "this is not what we were aiming for". |
| `istorpage-build-plan.md` | project | `SITE_BUILD_PLAN.md` owns order of work, repo layout, generators, publishing and the copy deck. Publishing is GitHub Actions to an uploaded Pages artifact, so `OldVersion/`, `References/`, `Documentation/` and `Assets/` are unpublished by construction. The 75-page library is carried, the three path collisions are settled (`/index.html`, `/styles.css`, `/favicon.ico`), and the texture ships unchanged at 1,542,136 B / sha256 `3c07a279...f3451`. Pre-redesign history exists only locally as tag `site-v1`. |
| `reference-niche-analysis.md` | project | The five references and the niche: BreezyCourses, Freebuff, Gamma, Gemini Notebook, Tempo. The genre sells by showing a dark app window with no illustration and no stock photography, and its shared architecture runs sticky nav, 3 to 7 word hero, framed screenshot, alternating features, social proof, FAQ, giant wordmark, minimal footer. Also the verified technical layer: **no animation library and no scroll-timeline API on any of the five**, page weights from 13.80 MB (Gamma) down to 2.12 MB (Freebuff), container widths converging at 1150 to 1300px, and three different constructions of the giant footer wordmark. |
| `istor-brand-assets.md` | reference | The salvageable brand assets and their limits. Two disjoint GFS Didot subsets: `istor-wordmark.woff2` carries 16 codepoints and sets **only** the Greek wordmark, while `fonts/gfs-didot.woff2` has 219 glyphs and no Greek. Locked wordmark PNGs at 501x177, ink `#171717` with dot `#D93A3A` light and `#FAFAFA` with `#4DA3FF` dark. Icons `istor-page.svg` (>=48px) and `istor-eye.svg` (<=32px). The `var()` re-inking contract **works for inline SVG only**; an `<img>` instance on a dark ground renders near-black on near-black. |
| `istor-app-interface-palette.md` | reference | Measured colours and layout grammar of the app. Light: rails `#FAFAFA`, fill `#F4F6F8`, hairline `#D3D3D4`, ink `#171717`, and azure `#0066CC` as the only interactive colour. Status: waiting `#B35208`, ready `#4BB581` (dot only, 2.6:1, never text), coral `#E85B5C` for unverified, which fails AA. Black theme: rails `#0A0A0A`, centre `#0B0C0F`, fill `#10141B`, text `#E5E8EE`, accent `#4DA3FF`, and **no column rules at all**, separation is a hue shift. Three columns measured 180 / 594 / 185 CSS px. The witness is a popover anchored to the citation mark. |
| `istor-answer-mechanics.md` | project | How the app actually answers, evidenced from a real run. The grounding gate runs first and writes `Gate decision: band=Direct calibrated=0.0 raw_confidence=0 pass_used=0 rationale=Some("Local library already answers this question")`. `band=Direct` is hybrid retrieval `top_k=4` widened to 8 on weak fusion; `band=Research` is SERP then fetch then summarise with honest failures (`status (403) -> drop`). Claims carry `[^ist-N]` footnotes, and citations retro-fitted by the small model are marked **unverified**, meaning provenance rather than "unsupported". Also the corrections: `powercell` was never a component, and the dark terminal shots are the **dev debug screen**, so the site shows the app's own `Thoughts` disclosure instead. No model name is printed on the page. |
| `screenshots-are-source-material.md` | feedback | Raw captures are source material, not figures. The crop and polish is the agent's to make, and nothing ships uncropped, so geometry drift between captures (hairlines at 676 to 797, status dots at 138 vs 208, heights 1012 to 1018) stops being blocking. **Never propose a re-shoot to fix framing**: check whether the region already exists in the set. Specify source file, crop box and polish steps instead. |
| `istor-site-artwork.md` | project | The site's ground, icons and one drawn figure, all generated deterministically with the scripts checked in. Ground is `ground-grain.png` at **451 bytes** from `make-ground.py`, fixed seed `20260918` because magick noise is not stable across versions. The five icons are **Lucide's own files, not redrawn**, from `lucide-react` 1.31.0, and `FilePlus2` is only an alias. The one figure is `Source/figures/calendar-ring.svg`, 1,318 B / 694 gzipped, from `make-calendar-ring.py`, with 354 holes 1.0169 degrees apart against 355 at 1.0141 degrees. Exactly one soft shadow is pre-approved, under the app window. |
| `istor-site-compute-budget.md` | project | The website must "just work fine with at least GTX 1650 (4gb vram)" (Thoria), and that is the **website's** budget, not the app's. Two builds of one page, declared rather than scripted: the main one, and a lighter one for phones via media queries and `<picture>` sources with **no detection script**. The app's minimum spec is deliberately unpublished, because the requirement follows a model picker the reader has not touched yet. Istor ships with no model: Ollama or llama.cpp is the requirement. |
| `local-toolchain.md` | reference | Blender 5.2.1 LTS and Inkscape 1.4.4 are installed, off the original PATH; ffmpeg 7.1, ImageMagick 7.1.2 as `magick`, Python 3.14.4, Node 24.14.1, git. **`command -v` is not an installation check** and once produced a wrong "not installed" report. Never use `setx` for PATH (it truncates at 1024 chars; the raw User PATH is 1264) and use `magick`, never `convert`, which on Windows is the FAT-to-NTFS tool. |
| `toolkit-audit-2026-09-18.md` | project | The working set. Playwright MCP was removed as a duplicate of Chrome DevTools (config backup at `%USERPROFILE%\claude-json-backup-before-playwright-removal.json`). Figma MCP is kept but costs 37 tools, about 24 of them irrelevant to a website. Also the Claude Code config gotcha: settings resolve per top-level key and **maps do not merge**, so a project `enabledPlugins` with two entries disables the rest. |
| `tooling-known-defects.md` | reference | Verified defects in the installed skills. `web-quality-skills:accessibility` defines large text in px where WCAG says pt, which would let 18px body pass at 3:1. `humanizer` bans em and en dashes and prescribes straight quotes while `microtypography` mandates en dashes and calls straight quotes typewriter marks, so one pipeline cannot satisfy both. `hierarchy-and-scale` and `editorial-web-typography` disagree about the baseline grid, and measure ceilings are unreconciled at 80 vs 85 CPL. APCA has no legal standing and must not be the conformance gate. `ux-design` embeds Amazon affiliate links. |

### Some of those notes are stale

Memory records what was true when it was written, and it is written by an agent. None of the
following is wrong about the past, but each will mislead if read as current:

- **`istorpage-build-plan.md`** and **`istorpage-design-plan-v2.md`** both quote byte figures that
  have moved. They record the document at **62,543 B** and the artifact at **120 files /
  3,389,782 B**. As of 2026-09-19 the measured values are **62,856 B** and **138 files /
  3,861,931 B**. `Source/tools/budget.json` is the authority, and it is asserted on every build.
- **`istorpage-build-plan.md`** describes the site as live on v1, which v2 superseded.
- **`istorpage-redesign-scope.md`** describes `Source/`, `Documentation/`, `Assets/` and
  `.claude/` as empty and the directory as not a git checkout. All four are overtaken.
- **`oldversion-is-not-context.md`** says `OldVersion/` is parked. The repository was replaced
  wholesale on 2026-09-19 with 75 of its library pages carried to the root, so its current form
  may differ.
- **`istor-answer-mechanics.md`** quotes two CLI captures under
  `Assets/Istor Screenshots/UnCropped/` that **no longer exist**, and cites v1's design plan. Some
  of its content therefore cannot be re-verified against a file.
- **Capture counts disagree across three notes**: `istor-app-interface-palette` says 35,
  `istor-answer-mechanics` says 32, `screenshots-are-source-material` says 32, and the palette's
  own frontmatter says 13. Count the directory rather than trusting any of them.
- **`istor-brand-assets.md`** ends by saying coral is artwork and never a UI colour, which
  `istor-app-interface-palette` explicitly corrects after measuring coral as the app's
  unverified ink.
- **`istor-product-brief.md`** has a "Still unanswered" list that has since been closed, and
  refers to v1 as "the design plan".
- Several notes cite **sections 7 or 8 of v1 `SITE_DESIGN_PLAN.md`**. v2 governs now.

## Read this before trusting a note

Memory is not the specification. These are:

| Path | Role |
|---|---|
| `Documentation/SITE_DESIGN_PLAN_V2.md` | the specification, 782 lines |
| `Documentation/SITE_BUILD_PLAN.md` | how the site is built, 1,503 lines |
| `Source/index.html`, `Source/styles.css` | what actually ships |
| `Documentation/app-coral-contrast.md` | the site's accessible substitute for the app's coral |

v2 retires v1's precedence rule. Where a document and the built page disagree, the answer is
**measurement**, not which document outranks which. And where a note names a file, path, figure
or flag, verify it against the repository first.

Two standing rules for the copy, from Thoria: **every string a visitor can read goes through the
`humanizer` skill**, and **no em or en dashes in the site's own text**. The dashes inside the app
captures are the product's own punctuation and are left alone.

## Unattended improvement runner

`Source/tools/background-runner.py` can start a fresh external coding-agent process for each rotating goal. It keeps one lock file, records stdout and stderr in `.improvement/BACKGROUND_RUNNER.log`, stops on failure by default, and never grants git permissions by itself.

Set the agent command once, then start it from the repository root:

    set ISTOR_AGENT_COMMAND=claude -p {prompt}
    python Source/tools/background-runner.py --forever --interval 30

Use `--cycles N` for a bounded run. Edit `Documentation/OVERNIGHT_GOALS.md` to change the goals. The runner is deliberately an adapter around the local agent CLI, because the repository cannot know which account, MCP connections or permissions the host has configured. Freebuff's current CLI is interactive only and does not expose a documented headless or print mode, so this runner cannot start a new Freebuff Desktop turn by itself. A real Freebuff bridge must be implemented in the Freebuff host or against an official Freebuff headless or SDK interface.

For a desktop-only fallback, `Source/tools/freebuff-continue.py` can focus the Freebuff window, click a configured relative chat-box position, paste `Please Continue`, and press Enter on a timer. It also accepts a cue file or cue command from an external sound detector. This helper uses Windows APIs only, so it does not need PyAutoGUI, but it must be calibrated with the chat box coordinates and should be tested with `--max-sends 1` first:

    python Source/tools/freebuff-continue.py --chat-x 0.50 --chat-y 0.90 --interval 300 --max-sends 1

The timer is the reliable mode. Freebuff does not currently expose a documented sound event or public Desktop control API, so the helper cannot safely identify Freebuff's sound cue by itself.

## Building it

    python Source/tools/build-site.py      # Source/ + Assets/ + OldVersion/ -> _site/
    python Source/tools/verify-budget.py   # every asserted byte size
    python Source/tools/verify-links.py    # every link in the artifact
    python -m http.server --directory _site 8080

CI runs the same checks and fails on any of them. `Source/tools/budget.json` asserts the
artifact's byte sizes exactly. When a number moves because the page changed, re-baseline it **by
measurement**, in the same commit as the change that moved it, and never by transcribing a figure
from another document.

## What is not published

The GitHub Actions workflow uploads a Pages artifact assembled from `Source/` plus an allowlist of
library directories. This file, `Documentation/`, `Assets/`, `References/`, `OldVersion/` and
`.improvement/` are all unpublished by construction.

The live work log for the redesign is not in the memory folder. It is in the ignored scratch
directory `.improvement/OVERNIGHT_LOG.md`.
