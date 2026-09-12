# Build the treatise vocabulary

This folder is the closed word list for *De gradibus humilitatis et superbiae*. The study reader should look words up here. It should not call Whitaker on every click, and it should not ship a general dictionary.

The root `README.md` is the reader bookmark. This file is only the vocabulary pipeline.

## Status

| File | Status |
| --- | --- |
| `forms.json` | Done. 3,311 forms / 9,114 tokens from `content/latin.md`. |
| `analyses.json` | Done (generated, gitignored). 3,311 forms, 0 misses. |
| `lexicon.json` | Done. Parsed dictionary, 3,311 entries; 54 curated (Bernard) cards merged in. |
| `overrides.json` | Done. Hand-authored Bernard glosses + the 18 `no_gloss` cards. |

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

`analyses.json` is a reproducible artifact and is gitignored (re-run the job to
rebuild it). The parsed dictionary `lexicon.json` is the tracked, edited file.

Do not leave `whitaker_server.py` running for this. MCP is for Cursor. The batch script calls `words` inside the same image.

## 3. Parse (done)

```bash
npm run lexicon:parse
```

or `python tools/parse_analyses.py` (add `--show` for a frequency summary).

`tools/parse_analyses.py` turns the raw `analyses.json` blocks into
`lexicon.json`: one entry per form with

- `key` / `form` / `query` / `count` / `first` (passthrough from `forms.json`)
- `pos` — the part-of-speech tags seen in Whitaker’s morphology lines
- `senses` — one per Whitaker dictionary entry: `lemma` (headword, e.g.
  `caritas, caritatis`), `pos`, and the `gloss` (Whitaker’s definition)
- `no_gloss` — true when Whitaker has no definition for the form

It is a pragmatic parser, not a full Whitaker emulator, so review the output
for: empty lemmas on pronominal words, Whitaker’s sense ordering (e.g. `est`
lists *edo* “eat” before *sum* “be”; `non` lists the noun *Nones* before the
adverb), and the ~18 `no_gloss` forms — mostly proper names (*Abraham*,
*Pharisaeus*, *Bernardi*, *Sion*, *Simon*, *Martha*, …) plus a few genuine
words (*grossescere*, *pedetentim*, *penultimo*) and extraction slips
(*oblivisicitur* for *obliviscitur*).

## 4. Curate (done)

Whitaker’s glosses are classical, not Bernardine. Layer your own dictionary
cards on top instead of editing the generated `lexicon.json` by hand.

```bash
npm run lexicon:curate
```

or `python tools/apply_overrides.py`.

`content/lexicon/overrides.json` maps a lexicon `key` to an `edited` card:

- `gloss` — short, treatise-faithful Bernard gloss (preferred over Whitaker’s)
- `note` — optional reference, quoted Latin, and context
- `lemma` / `pos` — optional; when omitted the entry keeps Whitaker’s

`tools/apply_overrides.py` merges every match into `lexicon.json` as an
`edited` block (and sets `curated: true`), which the reader shows on click.
Safe to re-run — existing `edited` blocks are cleared first, so re-parsing and
re-curating stays idempotent. A missing key aborts with a warning rather than
silently dropping a card.

Curated coverage:

- **Bernard stems**: *humilitas*, *superbia*, *charitas* (kept as the extract
  spells it, with a note that it is *caritas*), *curiositas*, *miser / miseria /
  misericordia*, *gradus*, *veritas*, *excessus* — prefer ring here.
- **The 18 `no_gloss` forms**: proper names (*Abraham*, *Pharisaeus*, *Bernardi*,
  *Godefride*, *Elias / Heliu*, *Sion*, *Absalon*, *Simon*, *Iona*, *Enoch*,
  *Martha*) and words (*mundicordes*, *inculpabiliter*, *pedetentim*,
  *penultimo*, *grossescere*). `oblivisicitur` is noted as a source slip for
  *obliviscitur* (to fix in `content/latin.md`).

## 5. Reader (done)

Click-a-word is a second gesture so it does not fight sentence alignment:

- clicking between words still aligns English (the existing `.segment` click);
- clicking a Latin word opens a dictionary popup.

`app/src/dictionary.ts` imports `lexicon.json` and exposes `lookup`,
`glossFor`, `lemmaFor`, `sensesFor`. `app/src/main.ts` tokenises each Latin
segment into `<span class="w">` elements and shows a fixed popup on word click
(shows `edited.gloss` when present, else Whitaker’s first sense).

Rebuild `lexicon.json` after either pipeline step:

```bash
npm run lexicon:parse   # regenerate base from analyses.json
npm run lexicon:curate  # re-apply Bernard cards
```

## Scripts

| Script | Runs where |
| --- | --- |
| `tools/extract_wordlist.py` | Host |
| `tools/analyze_wordlist.py` | Inside the Whitaker container |
| `tools/analyze-in-docker.sh` | Host; mounts the repo at `/work` |
| `tools/parse_analyses.py` | Host; `analyses.json` → `lexicon.json` |
| `tools/apply_overrides.py` | Host; merges `overrides.json` into `lexicon.json` |
| `app/src/dictionary.ts` | Reader; `lexicon.json` lookup + gloss helpers |
