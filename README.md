# Bernard study reader

A local TypeScript reader for Bernard of Clairvaux, *De gradibus humilitatis et superbiae*. Latin is the index. Two English columns show how a period is split or a word is softened.

This file is also a bookmark for where the work stopped.

## Do not edit

`01_steps_of_humility_and_pride.md` is the author’s PL extract. The app does not read it. Leave it unchanged.

App Latin lives in `content/latin.md` (same extract, plus retractatio, missing §§, and a few filled lacunae from SBO 3). Verify that file against the PDFs before treating it as final.

## Where things are

| Path | Role |
| --- | --- |
| `content/latin.md` | Working Latin for the reader |
| `content/schema.ts` | Segment / paragraph / chapter types |
| `content/parts/*.ts` | Aligned Latin, Mills 1929, close English, crux notes |
| `content/work.ts` | Assembles the treatise |
| `content/lexicon/forms.json` | Unique-word list extracted from `latin.md` (**done**) |
| `content/lexicon/analyses.json` | Whitaker output (**not generated yet**) |
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

Burch (1940) and Conway (Cistercian Fathers) are not ingested.

Later pride chapters sometimes use close English in the Mills slot. Check those against the 1929 book.

## Word analysis (in progress)

Plan: do not ship a general dictionary, and do not call Whitaker on every click. Analyze this treatise once (~3,300 forms) and look the answers up locally.

1. **Extract** (done). `npm run lexicon:extract` → `content/lexicon/forms.json` (3,311 forms, 9,114 tokens). *Vnde* is queried as `unde`; *charitas* as `caritas`.
2. **Analyze** (next). Start Docker Desktop, build or reuse the Whitaker image, then:

   ```bash
   cd services/whitaker-server
   docker build -t whitaker-mcp -f Dockerfile.whitaker-server .
   cd ../..
   bash tools/analyze-in-docker.sh
   ```

   Smoke test of the 20 most frequent words: `bash tools/analyze-in-docker.sh 20`.

   If the image has another name: `WHITAKER_IMAGE=your-name bash tools/analyze-in-docker.sh`.

   That writes `content/lexicon/analyses.json`.

3. **Not started.** Tighten the Whitaker parse (lemma, morphology, gloss). Review misses and about twenty Bernard stems (*humilitas*, *charitas*, *curiositas*, *miser* / *misericordia*, …). Then add click-a-word in the UI, as a second gesture so it does not fight sentence alignment.

The MCP server (`python whitaker_server.py`) is for Cursor / an agent. The batch job calls the Words binary inside the same image and does not need MCP left running.

## Still open

- Verify `content/latin.md` against the PDFs.
- Check Mills, especially later pride chapters.
- Generate `analyses.json` (Docker was not running when the extractor was written).
- Word popup in the reader, after the lexicon exists.
