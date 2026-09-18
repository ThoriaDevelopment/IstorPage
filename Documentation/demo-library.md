# Demo library — Antikythera mechanism

For the site's hero screenshots. **Ten sources, one big topic, ten different angles**, chosen
so the answer *cannot* come from any single one of them.

Every URL below was checked on 2026-09-18 and returns **HTTP 200** to a plain browser-agent
request — no 403s, no paywalls, nothing the fetcher will have to drop. That matters: a 403 in
the middle of a demo run looks like a bug.

## Why this topic

It does four jobs at once:

1. **It is a genuine cross-source synthesis.** No single page answers the interesting
   question. The answer has to be assembled from a 2006 primary paper, a 2021 primary paper,
   a 2024 challenge to both, and the background cycles they all assume.
2. **It contains a live disagreement.** The 2024 Glasgow study argues the calendar ring had
   354 or 355 holes, i.e. it tracked the *lunar* calendar — overturning a century-old
   assumption. Tony Freeth (UCL), author of two of the other sources in this very library,
   called it "just wrong." A notebook that cites both sides of that, side by side, is
   demonstrating the product better than any feature list could.
3. **It reads as a real research project**, which is the audience — not a demo invented to
   flatter the product.
4. **It is Greek.** The mechanism is an ancient Greek artefact, and the wordmark is ἵστωρ.
   The tie is real and needs no explaining, which is the only kind of tie worth having.

## The ten

| # | angle | source | URL |
|---|---|---|---|
| 1 | The object, in overview | Wikipedia — *Antikythera mechanism* | `https://en.wikipedia.org/wiki/Antikythera_mechanism` |
| 2 | How it was found | Wikipedia — *Antikythera wreck* | `https://en.wikipedia.org/wiki/Antikythera_wreck` |
| 3 | The gearwork decoded — **primary** | Freeth et al., *Nature* 444 (2006) | `https://www.nature.com/articles/nature05357` |
| 4 | The planetary model — **primary** | Freeth et al., *Sci. Rep.* 11 (2021) | `https://www.nature.com/articles/s41598-021-84310-w` |
| 5 | The 2024 challenge — **primary** | Woan & Bayley, arXiv:2403.00040 | `https://arxiv.org/abs/2403.00040` |
| 6 | The institution's own account | University of Glasgow, June 2024 | `https://www.gla.ac.uk/news/archiveofnews/2024/june/headline_1086643_en.html` |
| 7 | The calendar it implements | Wikipedia — *Metonic cycle* | `https://en.wikipedia.org/wiki/Metonic_cycle` |
| 8 | How it predicted eclipses | Wikipedia — *Saros (astronomy)* | `https://en.wikipedia.org/wiki/Saros_(astronomy)` |
| 9 | The physical object today | National Archaeological Museum, Athens | `https://www.namuseum.gr/en/collections/` |
| 10 | The long-form account + the dispute | Smithsonian Magazine | `https://www.smithsonianmag.com/history/decoding-antikythera-mechanism-first-computer-180953979/` |

Note the deliberate **source-type mix**: four reference articles, three primary papers, one
institutional release, one museum collection record, one long-form feature. When the Witness
rail opens, the sources don't all look the same — which is the honest picture of research and
makes the rail worth looking at.

## Spares (all verified 200)

Use these to swap in if any of the ten reads badly once it's rendered, or to push the library
to 12–15 sources if a fuller rail looks better.

```
https://www.antikythera-mechanism.gr/antikythera-mechanism
https://www.worldhistory.org/article/1750/the-antikythera-mechanism/
https://www.atlasobscura.com/places/antikythera-mechanism
https://en.wikipedia.org/wiki/Ancient_Greek_astronomy
https://en.wikipedia.org/wiki/Hipparchus
https://en.wikipedia.org/wiki/Callippic_cycle
https://en.wikipedia.org/wiki/Exeligmos
https://en.wikipedia.org/wiki/Parapegma
```

Dropped, and why, so nobody re-tries them: `arstechnica.com` (405), `phys.org` (403),
`ucl.ac.uk` (403), `britishmuseum.org` (403), `science.org` (403), `pnas.org` (403),
`sciencedirect.com` (403), NYT (paywall), `livescience.com` and `newscientist.com` (404 on
the URLs tried).

## The four questions to ask — one per run

**Status: shot.** Thoria ran these on 2026-09-18 and the captures are in
`Assets/Istor Screenshots/Black/` and `White/`. Two things differ from the brief below, and
both are improvements:

- **The hero question is a fifth one, and it was not in this list.** *"Tell me about the
  cycles."* — the shortest question in the set and the app's best answer. It opens on *"The
  Antikythera mechanism incorporated several key astronomical cycles:"* and then gives the
  Metonic, Callippic and Saros cycles as three bold run-in paragraphs. It supersedes Run 2 for
  the hero, because Run 2's answer is a *report on a dispute* and this one is *the tool
  teaching something* — which is what a knowledge worker is actually buying.
- **Run 4 did not land any sources** — the library is still empty in `FetchingPages.png`, and
  the failed `nature.com` fetch is on screen. That was kept deliberately: an empty library is
  why going to the web is legible, and displaying a failed fetch is the honesty claim
  demonstrated rather than asserted.

Everything below is left as written, because it is the record of how the set was planned.

Shoot these in order. Together they cover every state the site needs to depict.

**Run 1 — should resolve as `band=Direct`.** Proves the library answers without touching the
network.
> How did the Antikythera mechanism predict eclipses?

*Expect:* sources 1, 3, 8 — and the Saros cycle has to be explained because the mechanism's
back dial encodes it.

**Run 2 — should also resolve as `band=Direct`, and it is the money shot.** The synthesis.
> What do we actually know about the Antikythera mechanism, and what is still disputed?

*Expect:* nearly every source, and the answer **must** present the 354/355-hole claim and
Freeth's objection as two cited positions, not one. If it does, that single screenshot is the
whole product argument. Use it for the hero.

**Run 3 — a narrow question with one right answer**, for the citation card's clearest example.
> How many holes did the Antikythera mechanism's calendar ring have?

*Expect:* a number, its uncertainty, and a citation to source 5 — the ideal case for showing
one citation chip resolving to one passage. **Shot** — and its answer's *"What Is Still
Disputed"* table turned out to be better than the citation example it was ordered for, so it
now carries §5's "where it stops" section too.

**Run 4 — should resolve as `band=Research`** (ask explicitly for the web).
> Search the web for the latest excavation work at the Antikythera shipwreck and add what you find.

*Expect:* the gate bypasses, the research loop runs, sources get added with green dots. This
is what the two-column gate section needs, and it's the only way to shoot the amber→green
status transition honestly.

## While shooting

- **Shoot all four runs twice — once in the White theme, once in the Black theme.** Same
  window size both times. The site uses the light captures in the body and the dark captures
  in the closing movement, so the app's own second theme becomes the page's dark world
  instead of a stylistic switch I invented.
- **Same window size for every capture**, and the same zoom level.
- The demo library is public web content, so nothing needs redacting. But **clear the `Hello`
  test note** and give the notes real titles first.
- Let all ten sources finish indexing before shooting, so the status dots are uniformly green
  — except in Run 4, where newly-added sources should be caught mid-transition.
