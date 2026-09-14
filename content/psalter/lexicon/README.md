# Build the psalter vocabulary

This folder is the closed word list for the Gallican Psalter (*Psalterium Gallicanum*). The study reader looks words up here. It should not call Whitaker on every click, and it should not ship a general dictionary.

The root `README.md` is the reader bookmark. `content/gradibus/lexicon/README.md` is the same pipeline for Bernard. This file is only the psalter.

Every script takes `--work psalter`. The npm `lexicon:*` scripts default to `gradibus`, so call Python (or the docker helper) with the flag.

## Status

| File | Status |
| --- | --- |
| `forms.json` | Done. 5,706 forms / 30,495 tokens from `content/psalter/latin.md`. |
| `analyses.json` | Done (generated, gitignored). Rebuild with the analyze job. |
| `lexicon.json` | Done. Parsed dictionary, 5,706 entries, 70 `no_gloss`. Whitaker only — overrides are **not merged yet**. |
| `overrides.json` | Done as a **starter set** (~53 cards). Not yet applied to `lexicon.json`. |

`content/psalter/latin.md` is the source. The app never edits it. `first` on each form is the Gallican/Vulgate psalm number from that file (`## Psalmus N`). Coverdale uses Hebrew numbering; that split belongs in `psalm_map.json`, not in this lexicon.

## 1. Extract (already run)

Host only. No Docker.

```bash
python tools/extract_wordlist.py --work psalter
```

Rebuild `forms.json` only after `content/psalter/latin.md` changes.

Each form keeps:

- `form` — as printed
- `key` — lowercase in the file
- `query` — what Whitaker should see (`v` → `u`)
- `count`
- `first` — psalm number when first seen

## 2. Analyze (already run; gitignored)

Needs Docker Desktop and the Whitaker image.

```bash
bash tools/analyze-in-docker.sh --work psalter 20
bash tools/analyze-in-docker.sh --work psalter
```

Another image name: `WHITAKER_IMAGE=your-name bash tools/analyze-in-docker.sh --work psalter`.

That writes `analyses.json`. Do not leave `whitaker_server.py` running for this. MCP is for Cursor. The batch script calls `words` inside the same image.

## 3. Parse (already run)

```bash
python tools/parse_analyses.py --work psalter
```

Same shape as the treatise lexicon: `pos`, `senses` (`lemma`, `pos`, `gloss`), `no_gloss`. There are about 70 forms Whitaker did not define — names, liturgical words (*alleluia* is overridden), and misses. Review those after curating.

## 4. Curate (overrides written, not applied)

Whitaker’s glosses are classical. Psalter Latin often needs a different card: *confessio* is praise, not guilt-confession; *misericordia* tracks Hebrew *ḥesed*.

```bash
python tools/apply_overrides.py --work psalter
```

`overrides.json` maps a lexicon `key` to an `edited` card (`lemma?`, `pos?`, `gloss`, `note?`). Re-running is safe: existing `edited` blocks are cleared first. A missing key aborts.

The current file is a **starter**: mercy, justice, iniquity, vanity, desire, salvation, truth, praise/confession, glory, sin, hope, fear, goodness, and a few office words (*alleluia*, *psalterium*, *cithara*, *iubilate*). Notes cite a first psalm and a familiar verse. Confirm those citations against Gallican `latin.md` before treating them as final, then add more stems and the remaining `no_gloss` forms.

Until you run `apply_overrides.py --work psalter`, the reader still shows Whitaker on click.

## 5. Reader

Same gesture as Bernard: click a Latin word for the popup. `app/src/dictionary.ts` loads this work’s `lexicon.json` and prefers `edited.gloss` when present.

After either pipeline step:

```bash
python tools/parse_analyses.py --work psalter
python tools/apply_overrides.py --work psalter
```

## Scripts

| Script | Runs where |
| --- | --- |
| `tools/extract_wordlist.py --work psalter` | Host |
| `tools/analyze_wordlist.py --work psalter` | Inside the Whitaker container |
| `tools/analyze-in-docker.sh --work psalter` | Host; mounts the repo at `/work` |
| `tools/parse_analyses.py --work psalter` | Host; `analyses.json` → `lexicon.json` |
| `tools/apply_overrides.py --work psalter` | Host; merges `overrides.json` into `lexicon.json` |
