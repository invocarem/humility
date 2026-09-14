# Roadmap — from one treatise to a multi-work library

Working plan to turn this single-work reader (*De gradibus humilitatis et
superbiae*) into a small library of Latin + translation + analyses works:

1. **Bernard, De gradibus humilitatis et superbiae** — done, reused as the
   reference implementation.
2. **Benedictine Psalter** (Vulgate Gallican + Coverdale / close English) —
   first new work; cheapest to prove the mechanics.
3. **Rule of St Benedict** (Regula Benedicti; Latin + Verheyen / close English) —
   single, regular 73-chapter rule; second-cheapest proof of the mechanics and
   the natural companion to *De gradibus* (its ch. 7 degrees of humility are the
   ancestor of Bernard's ladder).
4. **Augustine, Confessions** (PL 32 + a public-domain English + close) —
   the big editorial lift, attempted after the machinery is hardened.
5. **Bernard, Sermones in Cantica** (a big editorial effort; mostly `close`
   renderings).

The existing machinery already generalizes: the analyses pipeline
(`tools/analyze_wordlist.py` → `parse_analyses.py` → `apply_overrides.py`) and
the reader's click-a-word + sentence-alignment are work-agnostic. Only a few
things are hard-coded to one book, and this roadmap de-hardcodes them one step
at a time.

---

## How to use this file

- We work **one step at a time**, top to bottom. A step is only *done* when its
  **Verify** bullet passes and the app shows **no regression** on *De gradibus*.
- When a step is finished, set its checkbox to `[x]` and move the **Current**
  line at the top to the next step. Commit after each step.
- **No code change until a step is started.** This file is the plan; it is not
  itself an implementation.

**Current step:** **Step 8** — Work #4: Augustine, Confessions (Latin + Pusey are in; close column and further stem cards still open).

---

## Step 1 — Introduce `WorkId` + a works registry; clean up *De gradibus*

**Status: DONE.** ✔ Reviewed below; the reader now resolves the active work from
the registry with no behavior change.

Goal: make "one work" an explicit, identified thing instead of global constants,
so the code can later hold several works. No visible behavior change — the app
must render *De gradibus* exactly as it does today.

Changes:
- `content/schema.ts`: add a `WorkId` union type (`"gradibus" | "psalter" |
  "confessions" | "cantica"`, order by roadmap). Add `id: WorkId` and an
  `edition` (provenance) field to `Work`.
- Replace the single `content/work.ts` `export const work` with a **registry**,
  e.g. `content/works.ts` exporting `works: Work[]`, `getWork(id)`,
  `defaultWorkId`, and `allChapters(workId)` / `findChapter(workId, id)`. Keep
  `work.ts` for now only as a thin re-export so tests/imports don't break, or
  migrate importers in the same step.
- `app/src/main.ts`: add `state.workId`; resolve the active work from the
  registry instead of the global `work` (lines using `work.parts`,
  `work.latinTitle`, `allChapters()`). Default to `defaultWorkId`.
- **Id namespacing — DECISION (defer the rename).** Ids only need to be unique
  *within* the active rendered work (selection/scroll/search/TOC resolve against
  the single work), and with one work today there is no collision — so existing
  *gradibus* ids are **left unchanged**. Going forward every new work MUST prefix
  its chapter/segment ids with its `WorkId` (e.g. `psalter:1`, `confessions:15`)
  so concatenated works can never collide. If a later step ever renders multiple
  works together, prefix the *gradibus* ids in one sweep (callers are all via
  `@content/works` + `findChapter`).

Files: `content/schema.ts` (WorkId + `id`/`edition`), `content/works.ts` (new
registry), `content/gradibus/work.ts` (assembles the work, was `content/work.ts`),
`content/gradibus/parts/*.ts` (moved from `content/parts/`), `app/src/main.ts`
(`state.workId` + registry reads).

Verify (all green):
- [x] `npm run build` (tsc + vite) is green.
- [x] Launching the app targets the default work and shows *De gradibus*
      identical to before (TOC, sentence alignment, crux drawer, click-a-word,
      search, `j`/`k`).

Done when: a work is identified by `WorkId`, lives in a registry, and the
reader reads the active work from state — with zero visual/behavioral change. ✔

---

## Step 2 — Per-work active state + a work switcher

**Status: DONE.** ✔ A `Work` dropdown in the top bar, populated from `works`.

Goal: the reader can switch the active work, even while only *De gradibus* is
registered. This proves the registry drives the UI.
- Add a minimal work selector (e.g. a dropdown in the top bar) populated from
  `works`.
- Switching resets chapter/selection to that work's first chapter and keeps
  search within the active work.

Also done here: retitled the app **Lectio — patristic & biblical Latin reader**
(top-bar brand + browser `<title>` in `index.html`).

Verify:
- [x] `npm run build` green; *De gradibus* works exactly as before via the
  default, and the selector lists (for now) one entry.

---

## Step 3 — Generalize translations (per-work rendering list)

**Status: DONE.** ✔ `Segment` now stores `translations: Record<TranslationId, string>`;
the reader renders one pane per entry in `Work.translations`.

Goal: replace the fixed two-column assumption with a per-work translation
catalogue, so later works can have their own named renderings (e.g. *Coverdale
1540* + *close* for the psalter; *Pusey* + *close* for Augustine).
- Today `RenderingId = "mills" | "close"` is baked into `Segment`
  (`latin, mills, close`). Move toward `Segment { latin, translations:
  Record<TranslationId,string>, notes? }` with `TranslationId`/`TranslationMeta`
  defined per work.
- Keep *De gradibus*'s two renderings (`mills`, `close`) working — same columns,
  same behavior.
- This is a type-level refactor touching `schema.ts`, `content/gradibus/parts/*.ts` (the
  `segment()`/`one()` helpers), and the reader panes.

How it was done: `RenderingId` was dropped; `TranslationId = string`. The
`segment()`/`one()` builders keep their positional `(id, latin, mills, close,
notes?)` signature and simply store a `translations: { mills, close }` map, so
the ~58 part callsites needed **zero changes**. Panes and the read-mode picker
are populated from `activeWork().translations` (order + label + id), so a new
work that adds, say, `coverdale` under its own `translations` list renders it
automatically. The read-mode picker buttons show each translation's `id`.

Verify:
- [x] Study/Read modes render the same two English columns for *De gradibus*
      before and after.

---

## Step 4 — Generalize the analyses pipeline to per-work lexicon

**Status: DONE.** ✔ All four pipeline scripts now take `--work` and resolve
`content/<work>/lexicon/`; *De gradibus* lexicon lives under
`content/gradibus/lexicon/`; the reader loads only the active work's lexicon.

Goal: each work gets its own closed word list + glossary, so glosses and the
dict popup stay per-work (e.g. *caritas* deserves a different note in the
psalter than in *De gradibus*).
- Give the extract/analyze/parse/curate scripts a work argument
  (`--work gradibus | psalter | …`) that resolves a per-work content + lexicon
  path, e.g. `content/<work>/lexicon/`.
- Keep the default (`--work gradibus`) producing the current
  `content/lexicon/*` output (or move it to `content/gradibus/lexicon/` once,
  and update the README + `.gitignore`).
- The downloadable artifacts (`forms.json`/`analyses.json`) remain gitignored
  per work; `overrides.json` + `lexicon.json` remain tracked per work.

Verify:
- [x] `bash tools/analyze-in-docker.sh 20 --work gradibus` reproduces the
      current 20-word smoke test (0 misses); `npm run lexicon:curate` still
      merges the 54 Bernard cards (and `lexicon:extract` still yields 3,311
      forms / 9,114 tokens).

---

## Step 5 — Ingestion / segmentation harness for large texts

Goal: stop hand-typing `parts/*.ts` for 150 psalms / 13 books / 86 sermons.
- Reuse/extend `tools/extract_wordlist.py`'s markdown-stripping and numbering
  logic into a generic importer per work: read `content/<work>/latin.md`,
  emit paragraphs, then scaffold `Segment` shells.
- Establish the authoring workflow: scaffold Latin → fill translation
  renderings → add crux notes. Keep `latin.md` authoritative and untouched by
  the app, exactly as today.

**Status: DONE.** ✔ `tools/ingest_latin.py` parses `content/<work>/latin.md`
into the parts → chapters → numbered-paragraph skeleton and can emit a
`scaffold.ts` starting point (Latin filled, translations + crux notes blank).
Per-work `content/<work>/ingest.json` may override a chapter boundary (the
De gradibus `## Caput III` marker sits two paragraphs early; `cap-4` is set to
start at §11). Scripts: `npm run ingest:verify` / `npm run ingest:scaffold`.
Authoring flow: scaffold Latin → fill renderings → add crux notes.

Verify:
- [x] Harness regenerates the current *De gradibus* structure cleanly (a dry
      re-scaffold that matches the existing `parts/`). — `python
      tools/ingest_latin.py --work gradibus` reports all 25 chapters /
      62 paragraphs matching `content/gradibus/parts/` (chapters retractatio,
      praefatio, cap-1…cap-22, admonitio; paragraphs r1–r4, pref, p1–p57). The
      generated `scaffold.ts` also type-checks against the reader's `Chapter`
      schema.

---

## Step 6 — Work #2: Benedictine Psalter

Recommended first new work (short, regular, PD source + PD close-faithful
English).
- Latin: the office is the **Vulgate Gallican (iuxta LXX)**. Ingest Psalms
  1–150 (accent/antiphon matter can come later).
- English: **Coverdale's 1540 Prayer Book psalter** (public domain, famously
  close and rhythmic — a natural fit for the `close` ethos) as one rendering,
  plus the reader's hand-written `close` for the stem-tracking column.
- Per-work `overrides.json`: psalter-specific glosses (*misericordia*,
  *sabaoth*, *alleluia*, etc.).

Verify:
- [ ] Every psalm opens in both renderings; click-a-word + sentence alignment
      work end-to-end; a handful of psalter-stem cards are curated.
      Latin 1–150 + Douay (1:1) + Coverdale (loose, via `psalm_map.json`) are
      merged from `content/psalter/renderings/`. Stem cards still to curate.

---

## Step 7 — Work #3: Rule of St Benedict (Regula Benedicti)

Recommended **Work #3** — placed before the *Confessions* because it is a
single, regular, small work that re-proves the harness and the renderings flow
for cheap before the 13-book lift of Augustine. Thematically it belongs right
here too: this is a Benedictine family project (Bernard is a Cistercian), and
RB ch. 7 (*De humilitate*, the degrees/ladder of humility) is the direct
ancestor of *De gradibus* — same register, same key stems.

- Latin: the Regula Benedicti (PL 66). Prologue + 73 short chapters; ingest
  via `tools/ingest_latin.py`, where the `## Capitulum N` markers map cleanly
  (the prologue may need a boundary override in `content/rule/ingest.json`).
  For the app's working Latin, prefer a sound critical text (e.g. RB 1980 /
  de Vogüé SC 181–186) rather than trusting PL 66 verbatim; note provenance in
  the work's `edition` field.
- English: **Boniface Verheyen (1949)** as one rendering (public domain, on
  Project Gutenberg, close-faithful, chapter/verse aligned) + the reader's own
  `close` for the stem-tracking column.
- Per-work `overrides.json`: RB-specific glosses (*obedientia*, *obbedire*,
  *abbas/abbatissa*, *regula*, *obsequium*, *disciplina*, *humilitas*…).

Progress: Latin 74 chapters (Prologus + 1–73) are scaffolded from
`content/rule/latin.md`; Verheyen is merged from `content/rule/renderings/`.
Click-a-word uses `content/rule/lexicon/` (4,089 forms; starter
`overrides.json` applied). A second English column is still to come. Working
Latin is the Latin Library traditional text, not yet a critical edition.

Verify:
- [ ] All 73 chapters + prologue render in both English columns; click-a-word
      and sentence alignment work end-to-end; a first pass of RB-specific
      stems is curated.

---

## Step 8 — Work #4: Augustine, Confessions

- Latin: PL 32 (13 books); segment each book into its numbered paragraphs.
- English: a public-domain version (**Pusey 1838** or **Pilkington 1876**) as
  one rendering + the reader's `close`. Late/Christian Latin is already handled
  by the dictionary (*caritas* etc.).

Progress: Latin 13 books / 278 capita / 453 PL paragraphs are scaffolded from
`content/confessions/latin.md` (The Latin Library, O'Donnell electronic text,
not PL 32 verbatim). Pusey 1838 is merged from
`content/confessions/renderings/`. Click-a-word uses
`content/confessions/lexicon/` (15,757 forms; starter `overrides.json` applied).
A second English column is still to come.

Verify:
- [ ] All 13 books render with both English columns and dictionary lookups.
      Latin + Pusey are in; a `close` column is still to come.
- [x] Curate a first pass of Confessions-specific stems (*confessio*,
      *inquietum cor*, *memoria*, *tolle lege*, *sero te amavi*, …).
      Starter set in `overrides.json`; refine against latin.md.

---

## Step 9 — Work #5: Bernard, Sermones in Cantica

- Latin: PL 183. The largest editorial task.
- Translation: no widely-public-domain complete English exists (the classic
  1952 *Sermons on the Song of Songs* is copyrighted), so this rests almost
  entirely on the reader's own `close` renderings (plus any PD excerpts). Be
  explicit about provenance per sermon.

Verify:
- [ ] A pilot run of a few sermons (e.g. 1, 7, 23 on *osculum/osculare me*) with
      `close` renderings + curated Song keywords (*osculum*, *fides*, *sponsa*,
      *sponsus*, *amor*, …).

---

## Later (optional)

- Cross-work **global** search (currently search is within the active work).
- Cross-references between works (e.g. a psalm Bernard quotes → the psalter
  work; *De gradibus*'s *misericordia* → Confessions).
- Progressive enhancement per work: different fonts/columns, psalm numbering
  toggle (Hebrew vs LXX/Vulgate vs Septuagint), antiphon/office metadata.
- Code-split the big inlined lexicon JSON in the bundle (currently ~1.25 MB raw
  / 312 kB gzip) if it grows.

---

## Principles to keep

- **`latin.md` per work is authoritative and never edited by the app.** All
  segmentation lives in generated/scaffolded parts; the author's PL extract
  files stay untouched.
- **No general dictionary and no Whitaker on every click.** Analyze each work
  once, closed list, look up locally; curate glosses per work.
- **Batch Whitaker in Docker only**; the MCP server is for interactive use and
  is not needed to build a dictionary.
- **Backward compatibility of *De gradibus*** at every refactor step — it is the
  spec for the whole mechanism.
