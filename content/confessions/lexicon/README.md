# Build the Confessions vocabulary

This folder is the closed word list for Augustine's *Confessiones*. The study
reader looks words up here. It should not call Whitaker on every click, and it
should not ship a general dictionary.

The root `README.md` is the reader bookmark. `content/gradibus/lexicon/README.md`
is the same pipeline for Bernard; `content/psalter/lexicon/README.md` for the
psalter; `content/rule/lexicon/README.md` for the Rule. This file is only the
Confessions.

Every script takes `--work confessions`. The npm `lexicon:*` scripts default to
`gradibus`, so call Python (or the docker helper) with the flag.

## Status

| File | Status |
| --- | --- |
| `forms.json` | Done. 15,757 forms / 78,762 tokens from `content/confessions/latin.md`. |
| `analyses.json` | Done (generated, gitignored). Rebuild with the analyze job. |
| `lexicon.json` | Done. Parsed dictionary; starter overrides merged in. |
| `overrides.json` | Done as a **starter set** (confession, restless heart, memory, charity, habit, concupiscence, continence, temptation, truth, beauty, the garden cry). |

`content/confessions/latin.md` is the source. The app never edits it.

## 1. Extract

Host only. No Docker.

```bash
python tools/extract_wordlist.py --work confessions
```

Rebuild `forms.json` only after `content/confessions/latin.md` changes.

Each form keeps:

- `form` — as printed (O'Donnell lowercase: `magnus`, `domine`)
- `key` — lowercase in the file
- `query` — what Whitaker should see (`u` for `v`)
- `count`
- `first` — PL paragraph number when first seen

## 2. Analyze (gitignored)

Needs Docker and the Whitaker image.

```bash
bash tools/analyze-in-docker.sh --work confessions 20
bash tools/analyze-in-docker.sh --work confessions
```

Another image name: `WHITAKER_IMAGE=your-name bash tools/analyze-in-docker.sh --work confessions`.

That writes `analyses.json`. Do not leave `whitaker_server.py` running for this.

## 3. Parse

```bash
python tools/parse_analyses.py --work confessions
```

Same shape as the other lexicons: `pos`, `senses` (`lemma`, `pos`, `gloss`),
`no_gloss`. Leftovers are mostly names (*Alypius*, *Monnica*, *Manichaeus*)
and a few late spellings / source slips. Review those after curating.

## 4. Curate (starter applied)

Whitaker's glosses are classical. Confessions Latin often needs a different
card: *confessio* is both praise and admission of sin; *cor* is the restless
self; *memoria* is Book 10's inner hall; *continentia* is the gift of a
gathered will.

```bash
python tools/apply_overrides.py --work confessions
```

`overrides.json` maps a lexicon `key` to an `edited` card (`lemma?`, `pos?`,
`gloss`, `note?`). Re-running is safe: existing `edited` blocks are cleared
first. A missing key aborts.

The current file is a **starter**: the double sense of *confessio*, the
*inquietum cor*, memory, charity, habit, the three concupiscences, continence,
temptation, Truth, Beauty (*sero te amavi*), *tolle lege*, humility. Notes
cite Conf. book.chapter. Confirm those against `latin.md` before treating them
as final.

## 5. Reader

Same gesture as Bernard: click a Latin word for the popup.
`app/src/dictionary.ts` loads this work's `lexicon.json` and prefers
`edited.gloss` when present.

After either pipeline step:

```bash
python tools/parse_analyses.py --work confessions
python tools/apply_overrides.py --work confessions
```

## Scripts

| Script | Runs where |
| --- | --- |
| `tools/extract_wordlist.py --work confessions` | Host |
| `tools/analyze_wordlist.py --work confessions` | Inside the Whitaker container |
| `tools/analyze-in-docker.sh --work confessions` | Host; mounts the repo at `/work` |
| `tools/parse_analyses.py --work confessions` | Host; `analyses.json` → `lexicon.json` |
| `tools/apply_overrides.py --work confessions` | Host; merges `overrides.json` into `lexicon.json` |
