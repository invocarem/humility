# Lectio

A local Latin reader. Latin is the index; English sits beside it.

Works in the library today:

1. Bernard of Clairvaux, *De gradibus humilitatis et superbiae*
2. The Gallican Psalter
3. The Rule of St Benedict
4. Augustine, *Confessiones*

Planned next works (see [`docs/roadmap.md`](docs/roadmap.md)): the Vulgate
New Testament (Gospels first, then Paul, one work) and Bernard’s *Sermones in
Cantica*. That file is the working plan (current step, verify checklists).
This README is the reader bookmark: how to run the app, where the texts live,
and how to rebuild the lexicon.

## Do not edit

`content/<work>/latin.md` is the authoritative Latin. The app never writes it.

`01_steps_of_humility_and_pride.md` is the author’s PL extract for *De
gradibus*. The app does not read it. Leave it unchanged. App Latin for that
work lives in `content/gradibus/latin.md` (same extract, plus retractatio,
missing §§, and a few filled lacunae from SBO 3). Verify that file against the
PDFs before treating it as final.

## Where things are

| Path | Role |
| --- | --- |
| `content/works.ts` | Library registry (`works`, `getWork`, `allChapters`) |
| `content/schema.ts` | Segment / paragraph / chapter types |
| `content/gradibus/` | *De gradibus* (`latin.md`, `parts/*.ts`, Mills + close, lexicon) |
| `content/psalter/` | Gallican psalter (`latin.md`, scaffold, Coverdale/Douay) |
| `content/rule/` | Rule of St Benedict (`latin.md`, scaffold, Verheyen, lexicon) |
| `content/confessions/` | Augustine, *Confessiones* (`latin.md`, scaffold, Pusey, lexicon) |
| `content/confessions/` | Augustine, *Confessiones* (`latin.md`, scaffold, Pusey, lexicon) |
| `content/<work>/lexicon/` | Closed word list (`forms.json`, gitignored `analyses.json`, `lexicon.json`, `overrides.json`) |
| `content/<work>/lexicon/README.md` | Per-work vocabulary pipeline |
| `app/src/` | Web UI (Read / Study, click-to-align, click-a-word) |
| `electron/` | Thin desktop shell |
| `tools/extract_wordlist.py` | `latin.md` → `forms.json` |
| `tools/analyze-in-docker.sh` | Whitaker over that list → `analyses.json` |
| `tools/parse_analyses.py` | `analyses.json` → base `lexicon.json` |
| `tools/apply_overrides.py` | `overrides.json` → curated cards on `lexicon.json` |
| `services/whitaker-server/` | Whitaker’s Words image (batch job + MCP for Cursor) |

## Run the reader

```bash
npm install
npm run dev
```

Open the URL Vite prints. On this machine Vite bound to `http://localhost:5173/`
(IPv6 localhost). `127.0.0.1` may not answer.

- **Work** in the header switches treatise / psalter / Rule / Confessions.
- **Read**: Latin plus one English column.
- **Study**: Latin and the English columns side by side. Click a sentence; the
  same segment highlights in every column. A note opens only on a crux.
- Click a **Latin word** for the work’s lexicon (curated gloss if one exists,
  otherwise Whitaker). Clicking between words still aligns English.
- Latin search in the top bar. `j` / `k` change chapter.

Desktop later: `npm run electron:dev`. After `npm run build`, `npm start` opens
the built files.

## Texts in the columns

- **De gradibus — Latin**: PL 182, with gaps in the author’s file supplied from
  SBO 3 for the app only.
- **Mills**: Barton R. V. Mills, *The Twelve Degrees of Humility and Pride*
  (SPCK / Macmillan, 1929). Public domain in the US. Mills used the Cambridge
  *Select Treatises* Latin, which sometimes differs from Migne.
- **Close English**: written for this tool, so Bernard’s clauses and stems stay
  visible. It is not a second literary version.

Psalter (Work → The Psalms): Latin Gallican; Coverdale 1662 BCP (Hebrew
numbering, loose verse alignment); Douay-Rheims Challoner as the 1:1 close
column.

Rule (Work → The Rule of St Benedict): Latin from `content/rule/latin.md`;
Boniface Verheyen 1949 as the English column. A hand-written `close` column is
still to come. Verheyen’s paragraphs are finer than the working Latin, so
several English paragraphs may sit in one numbered Latin block.

Confessions (Work → The Confessions): Latin from `content/confessions/latin.md`
(The Latin Library, O’Donnell electronic text; 13 books, 278 capita). E. B.
Pusey 1838 as the English column (Project Gutenberg #3296). A hand-written
`close` column is still to come. Pusey’s paragraph breaks are joined onto the
PL numbered blocks; a few books merge or split so the counts match.

Burch (1940) and Conway (Cistercian Fathers) are not ingested.

Later pride chapters sometimes use close English in the Mills slot. Check those
against the 1929 book.

## Lexicon

Do not ship a general dictionary, and do not call Whitaker on every click.
Each work has a closed list: extract once, analyze once, look the answers up
locally.

Tracked files are `lexicon.json` (parsed dictionary the reader loads) and
`overrides.json` (hand-authored cards). `analyses.json` is Whitaker’s raw dump;
it is gitignored and rebuilt when you need it.

The `npm run lexicon:*` scripts default to *De gradibus*. For another work,
pass `--work rule`, `--work psalter`, or `--work confessions` to the Python /
docker helpers.

### Rebuild `analyses.json`

Needs Docker and the Whitaker image (Words at `/opt/whitakers-words/bin/words`).

```bash
cd services/whitaker-server
docker build -t whitaker-mcp -f Dockerfile.whitaker-server .
cd ../..

# smoke test, then the full list (a few minutes)
bash tools/analyze-in-docker.sh --work gradibus 20
bash tools/analyze-in-docker.sh --work gradibus
```

Same for the Rule, psalter, or Confessions: `--work rule` / `--work psalter` /
`--work confessions`. Another image
name: `WHITAKER_IMAGE=your-name bash tools/analyze-in-docker.sh --work …`.

That writes `content/<work>/lexicon/analyses.json`. Do not leave
`whitaker_server.py` running for this. MCP is for Cursor; the batch script
calls `words` inside the image.

Rebuild `forms.json` first only if `latin.md` changed:

```bash
python tools/extract_wordlist.py --work gradibus
```

### Parse and curate

```bash
python tools/parse_analyses.py --work gradibus   # analyses.json → lexicon.json
python tools/apply_overrides.py --work gradibus  # re-apply overrides.json
```

(`npm run lexicon:parse` / `lexicon:curate` are the same, for *De gradibus*
only.)

Per-work detail: `content/gradibus/lexicon/README.md`,
`content/rule/lexicon/README.md`, `content/psalter/lexicon/README.md`,
`content/confessions/lexicon/README.md`.

## Ingesting a new work

Do not hand-type the `parts/*.ts` skeleton. The harness reads
`content/<work>/latin.md` and derives parts → chapters → paragraphs:

```bash
npm run ingest:verify     # dry-run: does the derived skeleton match existing parts/?
npm run ingest:scaffold   # write content/<work>/scaffold.ts, Latin filled
# pass --work, e.g. python tools/ingest_latin.py --work rule --scaffold
npm run ingest:psalter-english  # fill Coverdale + Douay onto the psalter scaffold
npm run ingest:rule-english     # fill Verheyen onto the Rule scaffold
npm run ingest:confessions      # latin.md + Pusey from fetched TLL / Gutenberg sources
```

The scaffold leaves each segment’s `translations` and `notes` blank; you then
split it into `parts/*.ts` and fill renderings + crux notes, keeping `latin.md`
untouched. The psalter, the Rule, and the Confessions are the exception:
English is merged at load from `content/<work>/renderings/`, so regenerating
`scaffold.ts` does not wipe Coverdale / Douay / Verheyen / Pusey. If a work’s editorial division differs from
the literal `## Caput N` markers (as in *De gradibus*, where Caput III’s marker
sits two paragraphs early), record the boundary in `content/<work>/ingest.json`,
e.g. `{ "chapter_starts": { "cap-4": "p11" } }`.

## Still open

- Verify `content/gradibus/latin.md` against the PDFs.
- Check Mills, especially later pride chapters.
- Rule: a `close` English column; psalter: a first pass of stem cards.
- Confessions: a `close` English column; more stem cards; compare O’Donnell with PL 32.
- Next works: see [`docs/roadmap.md`](docs/roadmap.md).
