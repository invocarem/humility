# Build the treatise vocabulary

This folder is the closed word list for *De gradibus humilitatis et superbiae*. The study reader should look words up here. It should not call Whitaker on every click, and it should not ship a general dictionary.

The root `README.md` is the reader bookmark. This file is only the vocabulary pipeline.

## Status

| File | Status |
| --- | --- |
| `forms.json` | Done. 3,311 forms / 9,114 tokens from `content/latin.md`. |
| `analyses.json` | Not generated yet. Next step. |

`01_steps_of_humility_and_pride.md` is not a source. Do not edit it. Re-extract from `content/latin.md` only.

## 1. Extract (already run)

Host only. No Docker.

```bash
npm run lexicon:extract
```

or `python tools/extract_wordlist.py`.

That script strips markdown, section numbers, and scripture citations. It does not guess lemma or case.

Each form keeps:

- `form` — as printed (`Vnde`, `charitas`)
- `key` — lowercase in the file
- `query` — what Whitaker should see (`unde`, `caritas`)
- `count`
- `first` — paragraph mark when first seen (`R.2`, `8`, …)

Rebuild `forms.json` only after `content/latin.md` changes.

## 2. Analyze (do this next)

Needs Docker Desktop and the Whitaker image (Words binary at `/opt/whitakers-words/bin/words`).

```bash
cd services/whitaker-server
docker build -t whitaker-mcp -f Dockerfile.whitaker-server .
cd ../..
bash tools/analyze-in-docker.sh 20
```

If that looks sane, run the full list (a few minutes):

```bash
bash tools/analyze-in-docker.sh
```

Another image name:

```bash
WHITAKER_IMAGE=your-name bash tools/analyze-in-docker.sh
```

That writes `analyses.json`: each form plus Whitaker’s raw output.

Do not leave `whitaker_server.py` running for this. MCP is for Cursor. The batch script calls `words` inside the same image.

## 3. After `analyses.json` exists

Not started.

- Parse Whitaker’s raw lines into lemma, part of speech, case/tense, and a short gloss.
- Review misses and the Bernard stems: *humilitas*, *superbia*, *charitas*, *curiositas*, *miser* / *misericordia*, *gradus*, *veritas*, *excessus*.
- Prefer a short Bernard gloss on those stems over Whitaker’s classical “love” for *caritas*.
- Only then add click-a-word in the reader, as a second gesture so it does not fight sentence alignment.

## Scripts

| Script | Runs where |
| --- | --- |
| `tools/extract_wordlist.py` | Host |
| `tools/analyze_wordlist.py` | Inside the Whitaker container |
| `tools/analyze-in-docker.sh` | Host; mounts the repo at `/work` |
