# Build the Rule vocabulary

This folder is the closed word list for the *Regula Benedicti*. The study
reader looks words up here. It should not call Whitaker on every click, and it
should not ship a general dictionary.

The root `README.md` is the reader bookmark. `content/gradibus/lexicon/README.md`
is the same pipeline for Bernard; `content/psalter/lexicon/README.md` for the
psalter. This file is only the Rule.

Every script takes `--work rule`. The npm `lexicon:*` scripts default to
`gradibus`, so call Python (or the docker helper) with the flag.

## Status

| File | Status |
| --- | --- |
| `forms.json` | Done. 4,089 forms / 12,778 tokens from `content/rule/latin.md`. |
| `analyses.json` | Done (generated, gitignored). Rebuild with the analyze job. |
| `lexicon.json` | Done. Parsed dictionary, 4,089 entries; 101 curated cards merged in. |
| `overrides.json` | Done as a **starter set** (RB stems + the 41 `no_gloss` forms). |

`content/rule/latin.md` is the source. The app never edits it.

## 1. Extract (already run)

Host only. No Docker.

```bash
python tools/extract_wordlist.py --work rule
```

Rebuild `forms.json` only after `content/rule/latin.md` changes.

Each form keeps:

- `form` — as printed (`Obsculta`, `oboedientia`)
- `key` — lowercase in the file
- `query` — what Whitaker should see (`u` for `v`)
- `count`
- `first` — paragraph mark when first seen (`1`, `2`, …)

## 2. Analyze (already run; gitignored)

Needs Docker Desktop and the Whitaker image.

```bash
bash tools/analyze-in-docker.sh --work rule 20
bash tools/analyze-in-docker.sh --work rule
```

Another image name: `WHITAKER_IMAGE=your-name bash tools/analyze-in-docker.sh --work rule`.

That writes `analyses.json`. Do not leave `whitaker_server.py` running for this.

## 3. Parse (already run)

```bash
python tools/parse_analyses.py --work rule
```

Same shape as the other lexicons: `pos`, `senses` (`lemma`, `pos`, `gloss`),
`no_gloss`. There are 41 forms Whitaker did not define — late spellings
(*omnimo*, *antefana*, *obsculta*), office words (*Quirie*, *Eptaticum*), and
source slips (*humulitatis*, *sandala* for *scandala*). Review those after
curating.

## 4. Curate (starter applied)

Whitaker’s glosses are classical. RB Latin often needs a different card:
*regula* is the monastic Rule, not a straight-edge; *oratorium* is the chapel,
not an orator’s hall; *oboedientia* is the first degree of humility.

```bash
python tools/apply_overrides.py --work rule
```

`overrides.json` maps a lexicon `key` to an `edited` card (`lemma?`, `pos?`,
`gloss`, `note?`). Re-running is safe: existing `edited` blocks are cleared
first. A missing key aborts.

The current file is a **starter**: humility / obedience / abbot / Rule /
discipline / monastery / conversatio / stabilitas / charity / the four kinds
of monks / cellarer / silence / office words, plus all 41 `no_gloss` forms.
Notes cite RB chapter. Confirm those against `latin.md` before treating them
as final.

## 5. Reader

Same gesture as Bernard: click a Latin word for the popup.
`app/src/dictionary.ts` loads this work’s `lexicon.json` and prefers
`edited.gloss` when present.

After either pipeline step:

```bash
python tools/parse_analyses.py --work rule
python tools/apply_overrides.py --work rule
```

## Scripts

| Script | Runs where |
| --- | --- |
| `tools/extract_wordlist.py --work rule` | Host |
| `tools/analyze_wordlist.py --work rule` | Inside the Whitaker container |
| `tools/analyze-in-docker.sh --work rule` | Host; mounts the repo at `/work` |
| `tools/parse_analyses.py --work rule` | Host; `analyses.json` → `lexicon.json` |
| `tools/apply_overrides.py --work rule` | Host; merges `overrides.json` into `lexicon.json` |
