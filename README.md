# Bernard study reader

A local TypeScript reader for Bernard of Clairvaux, *De gradibus humilitatis et superbiae*. Latin is the index. Two English columns show how a period is split or a word is softened.

This file is also a bookmark for where the work stopped.

> **Expanding to more works?** The plan to turn this into a multi-work library
> (psalter, Augustine's *Confessions*, Bernard's *Sermones in Cantica*) lives
> in [`docs/roadmap.md`](docs/roadmap.md) — one step at a time.

## Do not edit

`01_steps_of_humility_and_pride.md` is the author’s PL extract. The app does not read it. Leave it unchanged.

App Latin lives in `content/gradibus/latin.md` (same extract, plus retractatio, missing §§, and a few filled lacunae from SBO 3). Verify that file against the PDFs before treating it as final.

## Where things are

| Path | Role |
| --- | --- |
| `content/gradibus/latin.md` | Working Latin for the reader |
| `content/schema.ts` | Segment / paragraph / chapter types |
| `content/gradibus/parts/*.ts` | De gradibus chapters (Latin, Mills 1929, close English, crux notes) |
| `content/gradibus/work.ts` | Assembles the De gradibus work |
| `content/gradibus/lexicon/*.json` | Per-work word list + glossary (`forms`, `analyses`, `lexicon`, `overrides`) |
| `content/works.ts` | Library registry (`works`, `getWork`, `allChapters`) |
| `app/src/` | Web UI (Read / Study, click-to-align) |
| `electron/` | Thin desktop shell |
| `tools/extract_wordlist.py` | Builds `forms.json` |
| `tools/analyze_wordlist.py` | Runs Whitaker over that list |
| `tools/analyze-in-docker.sh` | Runs the analyzer inside the Whitaker image |
| `services/whitaker-server/` | MCP wrapper around Whitaker’s Words (Docker) |

## Run the reader

```bash
npm install
npm run dev
```

Open the URL Vite prints. On this machine Vite bound to `http://localhost:5173/` (IPv6 localhost). `127.0.0.1` may not answer.

- **Read**: Latin plus one English (Mills or close).
- **Study**: Latin \| Mills 1929 \| close English. Click a sentence; the same segment highlights in every column. A note opens only on a crux.
- Latin search in the top bar. `j` / `k` change chapter.

Desktop later: `npm run electron:dev`. After `npm run build`, `npm start` opens the built files.

## Texts in the columns

- **Latin**: PL 182, with gaps in the author’s file supplied from SBO 3 for the app only.
- **Mills**: Barton R. V. Mills, *The Twelve Degrees of Humility and Pride* (SPCK / Macmillan, 1929). Public domain in the US. Mills used the Cambridge *Select Treatises* Latin, which sometimes differs from Migne.
- **Close English**: written for this tool, so Bernard’s clauses and stems stay visible. It is not a second literary version.

Psalter columns (switch Work → The Psalms): Latin Gallican; Coverdale 1662 BCP (Hebrew numbering, loose verse alignment); Douay-Rheims Challoner as the 1:1 close column.

Burch (1940) and Conway (Cistercian Fathers) are not ingested.

Later pride chapters sometimes use close English in the Mills slot. Check those against the 1929 book.

## Word analysis (in progress)

Plan: do not ship a general dictionary, and do not call Whitaker on every click. Analyze this treatise once (~3,300 forms) and look the answers up locally.

1. **Extract** (done). `npm run lexicon:extract` → `content/gradibus/lexicon/forms.json` (3,311 forms, 9,114 tokens). *Vnde* is queried as `unde`; *charitas* as `caritas`.
2. **Analyze** (next). Start Docker Desktop, build or reuse the Whitaker image, then:

   ```bash
   cd services/whitaker-server
   docker build -t whitaker-mcp -f Dockerfile.whitaker-server .
   cd ../..
   bash tools/analyze-in-docker.sh
   ```

   Smoke test of the 20 most frequent words: `bash tools/analyze-in-docker.sh 20`.

   If the image has another name: `WHITAKER_IMAGE=your-name bash tools/analyze-in-docker.sh`.

   That writes `content/gradibus/lexicon/analyses.json`.

3. **Not started.** Tighten the Whitaker parse (lemma, morphology, gloss). Review misses and about twenty Bernard stems (*humilitas*, *charitas*, *curiositas*, *miser* / *misericordia*, …). Then add click-a-word in the UI, as a second gesture so it does not fight sentence alignment.

The MCP server (`python whitaker_server.py`) is for Cursor / an agent. The batch job calls the Words binary inside the same image and does not need MCP left running.

## Ingesting a new work

To add *Psalter*, *Confessions*, or *Sermones in Cantica*, you do not hand-type the
`parts/*.ts` skeleton. The harness reads the work's authoritative
`content/<work>/latin.md` and derives the parts → chapters → paragraphs structure:

```bash
npm run ingest:verify     # dry-run: does the derived skeleton match existing parts/?
npm run ingest:scaffold   # write content/<work>/scaffold.ts, Latin filled
npm run ingest:psalter-english  # fill Coverdale + Douay onto the psalter scaffold
```

The scaffold leaves each segment's `translations` (per work `TranslationId`) and
`notes` blank; you then split it into `parts/*.ts` and fill renderings + crux
notes, keeping `latin.md` untouched. The psalter is the exception: English is
merged at load from `content/psalter/renderings/` so regenerating `scaffold.ts`
does not wipe Coverdale / Douay. If a work's editorial division differs from
the literal `## Caput N` markers (as in De gradibus, where Caput III's marker sits
two paragraphs early), record the boundary in `content/<work>/ingest.json`, e.g.
`{ "chapter_starts": { "cap-4": "p11" } }`.

## Still open

- Verify `content/gradibus/latin.md` against the PDFs.
- Check Mills, especially later pride chapters.
- Generate `analyses.json` (Docker was not running when the extractor was written).
- Word popup in the reader, after the lexicon exists.
