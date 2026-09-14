#!/usr/bin/env python3
"""Ingestion / segmentation harness for a work's Latin source.

Reads `content/<work>/latin.md` (the authoritative, never-app-edited source)
and derives the reader's structural skeleton: parts -> chapters -> numbered
paragraphs, mirroring the layout of the hand-authored `content/<work>/parts/*.ts`.
It can:

  * verify a dry re-scaffold against the existing hand-written parts/ (does the
    generated skeleton reproduce it?), and
  * write a `content/<work>/scaffold.ts` starting point (Latin filled,
    translations + crux notes left blank) for the author to assemble.

A chapter's paragraph run is taken from the chapter markers in `latin.md` — by
default `## Caput N` (Roman numerals, as in *De gradibus*). The marker scheme is
configurable per work through `content/<work>/ingest.json`, so the psalter can
declare `## Psalmus N` (decimal) without forking this file. Real treatises
sometimes place markers a couple of paragraphs off the editorial division the
curator wants; the same `ingest.json` may override a boundary so the separator
lands where the published division has it:

    { "chapter_starts": { "cap-4": "p11" } }   # cap-4 now begins at §11.

Per-work `ingest.json` shape (all keys optional; absent = gradibus defaults):

    {
      "parser": {
        "chapter_match": "^Psalmus\\s+(\\d+)\\s*$",  # regex vs heading (group 1 = number)
        "numeral": "decimal",                         # "roman" | "decimal"
        "id_prefix": "psalter",                       # chapter id prefix
        "id_sep": ":"                                 # "cap-1" vs "psalter:1"; two groups → N.M
      },
      "verify": {
        "chapter": "psalter:\\d+",                    # id grammar in parts/*.ts
        "paragraph": "p\\d+"
      },
      "chapter_starts": { ... }                       # optional boundary overrides
    }

Defaults reproduce *De gradibus* exactly (chapter id `cap-N`, matter chapters
`retractatio`/`praefatio`/`admonitio`, paragraphs `pN`/`rN`/`pref`), so a dry
re-verify remains the no-regression spec.

Usage:
    python tools/ingest_latin.py --work gradibus             # dry-run + verify
    python tools/ingest_latin.py --work psalter --scaffold   # write scaffold.ts
    python tools/ingest_latin.py --work rule --scaffold      # Prologus + 73 chapters
    python tools/ingest_latin.py --work confessions --scaffold  # 13 books, Liber N Caput M
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"

H2 = re.compile(r"^#{2,}\s+(.*)$")                 # chapter heading (## Caput I / ## Psalmus 1)
H1 = re.compile(r"^#\s+(.*)$")                      # document title / part marker
PARA_MARK = re.compile(r"^(R\.(\d+)|(\d+))\.\s+(.*)$")
EDITORIAL = re.compile(r"^\*")

# Roman numerals -> Arabic. Kept generous so later canon works (Sermones in
# Cantica, Book 86) reuse this parser without an edit.
ROMAN = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8,
    "IX": 9, "X": 10, "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15,
    "XVI": 16, "XVII": 17, "XVIII": 18, "XIX": 19, "XX": 20, "XXI": 21,
    "XXII": 22, "XXIII": 23, "XXIV": 24, "XXV": 25, "XXVI": 26, "XXVII": 27,
    "XXVIII": 28, "XXIX": 29, "XXX": 30, "XXXI": 31, "XXXII": 32, "XXXIII": 33,
    "XXXIV": 34, "XXXV": 35, "XXXVI": 36, "XXXVII": 37, "XXXVIII": 38,
    "XXXIX": 39, "XL": 40, "XLI": 41, "XLII": 42, "XLIII": 43, "XLIV": 44,
    "XLV": 45, "XLVI": 46, "XLVII": 47, "XLVIII": 48, "XLIX": 49, "L": 50,
    "LI": 51, "LII": 52, "LIII": 53, "LIV": 54, "LV": 55, "LVI": 56,
    "LVII": 57, "LVIII": 58, "LIX": 59, "LX": 60, "LXI": 61, "LXII": 62,
    "LXIII": 63, "LXIV": 64, "LXV": 65, "LXVI": 66, "LXVII": 67, "LXVIII": 68,
    "LXIX": 69, "LXX": 70, "LXXI": 71, "LXXII": 72, "LXXIII": 73, "LXXIV": 74,
    "LXXV": 75, "LXXVI": 76, "LXXVII": 77, "LXXVIII": 78, "LXXIX": 79,
    "LXXX": 80, "LXXXI": 81, "LXXXII": 82, "LXXXIII": 83, "LXXXIV": 84,
    "LXXXV": 85, "LXXXVI": 86, "LXXXVII": 87, "LXXXVIII": 88, "LXXXIX": 89,
    "XC": 90, "XCI": 91, "XCII": 92, "XCIII": 93, "XCIV": 94, "XCV": 95,
    "XCVI": 96, "XCVII": 97, "XCVIII": 98, "XCIX": 99, "C": 100,
}

# Default per-work parser config — the *De gradibus* conventions. A work's
# ingest.json may override chapter_match / numeral / id_prefix / id_sep.
DEFAULT_PARSER = {
    "chapter_match": r"Caput\s+([IVX]+)\s*$",
    "numeral": "roman",
    "id_prefix": "cap",
    "id_sep": "-",
}

# Id grammar the verify step reads back from parts/*.ts (gradibus defaults).
DEFAULT_VERIFY = {
    "chapter": r"(?:cap-\d+|retractatio|praefatio|admonitio)",
    "paragraph": r"(?:p\d+|r\d+|pref)",
}

# Un-numbered matter heading whose first word *is* the canonical chapter id.
MATTER_WORDS = {"retractatio", "praefatio", "admonitio"}

# An un-numbered single-paragraph chapter body keeps a conventional paragraph id
# distinct from its chapter id (e.g. Praefatio's body is id "pref", not "praefatio").
UNNUMBERED_PARA_ID = {"praefatio": "pref"}


@dataclass
class ParserCfg:
    chapter_match: re.Pattern
    numeral: str
    id_prefix: str
    id_sep: str


def _parse_numeral(tok: str, numeral: str) -> int | None:
    if numeral == "roman":
        return ROMAN.get(tok.upper())
    if tok.isdigit():
        return int(tok)
    return None


def chapter_id(text: str, cfg: ParserCfg) -> tuple[str, int | None]:
    """Chapter id (and optional number) for a `## Heading` line.

    Numbered chapters become `<prefix><sep><number>` (or `cap-N` / `psalter:1`).
    Two capturing groups (e.g. `Liber 1 Caput 5`) become `<prefix><sep>1.5`.
    Matter headings keep their own word id; anything else falls back to a slug.
    """
    m = cfg.chapter_match.match(text.strip())
    if m:
        groups = [g for g in m.groups() if g is not None]
        if len(groups) >= 2:
            book = _parse_numeral(groups[0], cfg.numeral)
            cap = _parse_numeral(groups[1], cfg.numeral)
            if book is None or cap is None:
                return "untitled", None
            return f"{cfg.id_prefix}{cfg.id_sep}{book}.{cap}", cap
        tok = groups[0]
        n = _parse_numeral(tok, cfg.numeral)
        if n is None:
            return "untitled", None
        return f"{cfg.id_prefix}{cfg.id_sep}{n}", n
    first = text.strip().split()[0].lower()
    if first in MATTER_WORDS:
        cid = first
    else:
        cid = re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-") or "untitled"
    # New works namespace unnumbered chapters (e.g. Prologus → rule:prologus).
    # Gradibus keeps grandfathered matter ids (id_sep "-").
    if cfg.id_sep == ":" and cfg.id_prefix:
        cid = f"{cfg.id_prefix}{cfg.id_sep}{cid}"
    return cid, None


def load_config(work: str) -> tuple[dict, ParserCfg, dict]:
    """Return (raw ingest.json, parser cfg, compiled verify grammar)."""
    path = CONTENT / work / "ingest.json"
    raw = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}

    pc = dict(DEFAULT_PARSER)
    pc.update(raw.get("parser", {}) or {})
    pc["chapter_match"] = re.compile(pc["chapter_match"])
    parser = ParserCfg(**pc)

    vc = dict(DEFAULT_VERIFY)
    vc.update(raw.get("verify", {}) or {})
    vc["chapter"] = re.compile(vc["chapter"])
    vc["paragraph"] = re.compile(vc["paragraph"])
    return raw, parser, vc


class Paragraph:
    def __init__(self, pid: str, n: str, latin: str):
        self.pid = pid
        self.n = n
        self.latin = latin


class Chapter:
    def __init__(self, cid: str, number: int | None, title: str, heading: str):
        self.cid = cid
        self.number = number
        self.title = title
        self.heading = heading
        self.paragraphs: list[Paragraph] = []
        self._head_candidate: str | None = None


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_latin(path: Path, cfg: ParserCfg) -> tuple[list[Chapter], list[str]]:
    """Return (chapters, part_titles) from latin.md, grouping paragraphs by the
    `## ... N` markers in source order."""
    chapters: list[Chapter] = []
    part_titles: list[str] = []

    def start_chapter(title: str):
        if chapters:
            finalize(chapters[-1])
        cid, number = chapter_id(title, cfg)
        chapters.append(Chapter(cid, number, title, ""))

    def finalize(ch: Chapter):
        if not ch.paragraphs and ch._head_candidate is not None:
            pid = UNNUMBERED_PARA_ID.get(ch.cid, ch.cid)
            ch.paragraphs.append(Paragraph(pid, "", ch._head_candidate))
            ch._head_candidate = None
        ch.heading = ch._head_candidate or ""

    seen_title = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line == "---" or EDITORIAL.match(line):
            continue
        m2 = H2.match(raw)
        if m2:
            start_chapter(m2.group(1).strip())
            continue
        m1 = H1.match(raw)
        if m1:
            if not seen_title:  # first h1 is the document title
                seen_title = True
            else:               # later h1 mark a new part (not a chapter)
                part_titles.append(m1.group(1).strip())
            continue
        if not chapters:
            continue  # orphan text before the first chapter; ignore
        pm = PARA_MARK.match(line)
        if pm:
            digit = pm.group(2) or pm.group(3)
            n = f"R.{digit}" if pm.group(2) else digit
            pid = f"r{digit}" if pm.group(2) else f"p{digit}"
            chapters[-1].paragraphs.append(Paragraph(pid, n, pm.group(4).strip()))
        else:
            ch = chapters[-1]
            if not ch.paragraphs:
                ch._head_candidate = (
                    (ch._head_candidate + " " + line).strip()
                    if ch._head_candidate else line
                )
            else:
                ch.paragraphs[-1].latin = (
                    ch.paragraphs[-1].latin + " " + line
                ).strip()
    if chapters:
        finalize(chapters[-1])
    return chapters, part_titles


def apply_chapter_starts(chapters: list[Chapter], overrides: dict) -> None:
    """Move chapter boundaries per ingest.json -> chapter_starts.

    Each entry {chapter_id: paragraph_id} makes that chapter begin at the named
    paragraph; earlier/purpose-built paragraphs re-flow to the chapters before
    it. Operates on the global paragraph order and keeps it monotonic."""
    starts = overrides.get("chapter_starts") or {}
    if not starts:
        return
    flat: list[Paragraph] = [p for ch in chapters for p in ch.paragraphs]
    index = {p.pid: i for i, p in enumerate(flat)}

    # final chapter boundaries (index into flat), one per chapter in order
    boundaries = {}  # chapter cid -> start index
    for ch in chapters:
        boundaries[ch.cid] = index[ch.paragraphs[0].pid]
    for cid, pid in starts.items():
        if pid not in index or cid not in boundaries:
            continue
        boundaries[cid] = index[pid]

    # reassemble; a chapter takes [bounds[i] : bounds[i+1])
    cids = [ch.cid for ch in chapters]
    bounds = [boundaries[c] for c in cids] + [len(flat)]
    for i, ch in enumerate(chapters):
        lo, hi = bounds[i], bounds[i + 1]
        if lo < 0 or hi < 0 or lo > hi or hi > len(flat):
            raise SystemExit(f"ingest: invalid boundary for {ch.cid}")
        ch.paragraphs = flat[lo:hi]


# ---------------------------------------------------------------------------
# Verification against existing hand-written parts
# ---------------------------------------------------------------------------

def existing_skeleton(work: str, verify: dict) -> list[tuple[str, list[str]]]:
    """Ordered [(chapter_id, [para ids])] for the work's parts/*.ts files."""
    ch_pat = verify["chapter"].pattern
    para_pat = verify["paragraph"].pattern
    tok = re.compile(
        r'id:\s*"(' + ch_pat + r')"'
        r'|ch\("(' + ch_pat + r')"'
        r'|"(' + para_pat + r')"'
    )
    skeleton: list[tuple[str, list[str]]] = []
    cur = None
    for path in sorted((CONTENT / work / "parts").glob("*.ts")):
        text = path.read_text(encoding="utf-8")
        for m in tok.finditer(text):
            if m.group(1) or m.group(2):  # chapter boundary
                group = m.group(1) or m.group(2)
                cur = [group, []]
                skeleton.append(cur)
            else:                          # paragraph id
                if cur is not None and m.group(3) not in cur[1]:
                    cur[1].append(m.group(3))
    return skeleton


def verify(work: str, chapters: list[Chapter], cfg: ParserCfg, verify_cfg: dict) -> bool:
    exp = {cid: set(ids) for cid, ids in existing_skeleton(work, verify_cfg)}
    got = {ch.cid: {p.pid for p in ch.paragraphs} for ch in chapters}
    FRONT = ("retractatio", "praefatio")
    prefix = cfg.id_prefix + cfg.id_sep

    def order_key(cid: str):
        if cid in FRONT:
            return (0, FRONT.index(cid))
        if cid.startswith(prefix):
            try:
                return (1, int(cid[len(prefix):]))
            except ValueError:
                return (2, 0)
        return (2, 0)  # admonitio & anything else last

    all_cids = sorted(set(exp) | set(got), key=order_key)
    ok = True
    print(f"verify {work}: comparing scaffold skeleton vs existing parts/")
    for cid in all_cids:
        missing = exp.get(cid, set()) - got.get(cid, set())
        extra = got.get(cid, set()) - exp.get(cid, set())
        if missing or extra:
            ok = False
            mark = "?? "
        else:
            mark = "OK "
        print(f"  {mark}{cid:<16} existing {len(exp.get(cid, set())):>2}  "
              f"scaffold {len(got.get(cid, set())):>2}"
              + (f"  missing {sorted(missing)}" if missing else "")
              + (f"  extra {sorted(extra)}" if extra else ""))
    if ok:
        print("=> dry re-scaffold reproduces existing parts/ (chapters + paragraphs).")
    else:
        print("=> differences found (see above) — authorial layer aside.")
    return ok


# ---------------------------------------------------------------------------
# Scaffold TS emission
# ---------------------------------------------------------------------------

def js_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def emit_scaffold(work: str, chapters: list[Chapter], out: Path) -> None:
    lines = [
        f"// AUTO-GENERATED scaffold from content/{work}/latin.md.",
        "// The Latin here is authoritative in latin.md; do NOT hand-edit these strings.",
        f"// Regenerate: python tools/ingest_latin.py --work {work} --scaffold",
        "// Then split these chapters into parts/*.ts and fill translations + crux notes.",
        'import { paragraph, type Chapter } from "../schema";',
        "",
        "// Segment translations are re-keyed to this work's TranslationIds and filled by hand.",
        'const tl = (latin: string) => ({ latin, translations: {} as Record<string, string> });',
        "",
        "export const scaffoldChapters: Chapter[] = [",
    ]
    for ch in chapters:
        num = f"{ch.number}," if ch.number is not None else "undefined,"
        lines += [
            "  {",
            f"    id: {js_str(ch.cid)},",
            f"    number: {num}",
            f"    title: {js_str(ch.title)},",
            f"    heading: {js_str(ch.heading)},",
            "    paragraphs: [",
        ]
        for p in ch.paragraphs:
            lines += [
                f'      paragraph({js_str(p.pid)}, {js_str(p.n)}, [',
                f"        {{ id: {js_str(p.pid + '.1')}, ...tl({js_str(p.latin)}) }},",
                "      ]),",
            ]
        lines += ["    ],", "  },"]
    lines.append("];")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT)} ({len(chapters)} chapters, "
          f"{sum(len(c.paragraphs) for c in chapters)} paragraphs)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", default="gradibus")
    ap.add_argument("--scaffold", action="store_true")
    ap.add_argument("--skip-verify", action="store_true")
    args = ap.parse_args()

    _raw, parser, verify_cfg = load_config(args.work)

    latin = CONTENT / args.work / "latin.md"
    if not latin.is_file():
        raise SystemExit(f"Missing {latin}")
    chapters, part_titles = parse_latin(latin, parser)

    apply_chapter_starts(chapters, _raw)

    total = sum(len(c.paragraphs) for c in chapters)
    print(f"ingest {args.work}: {len(chapters)} chapters, {total} paragraphs "
          f"from {latin.relative_to(ROOT)}"
          + (f"; parts: {part_titles}" if part_titles else ""))

    if args.scaffold:
        emit_scaffold(args.work, chapters, CONTENT / args.work / "scaffold.ts")

    if not args.skip_verify:
        parts_dir = CONTENT / args.work / "parts"
        if not parts_dir.is_dir() or not any(parts_dir.glob("*.ts")):
            print(f"verify {args.work}: no parts/ yet, skip")
        else:
            verify(args.work, chapters, parser, verify_cfg)


if __name__ == "__main__":
    main()
