#!/usr/bin/env python3
"""Turn Whitaker's raw batch output into a structured, reader-ready lexicon.

Reads content/lexicon/analyses.json (the raw `words` output, one block per
unique form) and writes content/lexicon/lexicon.json with one structured
entry per form:

    {
      "key": "caritas",
      "form": "Caritas",
      "query": "caritas",
      "count": 9,
      "first": "R.2" | null,
      "pos": ["N", "V"],            # POS tags seen in the morphology lines
      "senses": [                   # one per Whitaker dictionary entry
        {"lemma": "caritas, caritatis", "pos": "N",
         "gloss": "love, affection; ...;"}
      ],
      "no_gloss": bool              # true when no dictionary gloss was found
    }

This is a pragmatic parser, not a full Whitaker emulator: Whitaker's output
is loose (empty lemmas on pronominal entries, pager noise, repeated blocks),
so the fields are best-effort and are meant to be reviewed, especially the
`no_gloss` entries and the Bernard stems.

Usage:
    python tools/parse_analyses.py          # parse
    python tools/parse_analyses.py --show    # also print a per-entry summary
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "content" / "lexicon" / "analyses.json"
OUT = ROOT / "content" / "lexicon" / "lexicon.json"

# Whitaker part-of-speech abbreviations used in the output.
POS_TOKENS = (
    "VPAR",
    "PREP",
    "PRON",
    "CONJ",
    "ADJ",
    "ADV",
    "NUM",
    "INTERJ",
    "EXCLAM",
    "TACKON",
    "N",
    "V",
)

# Pager / assistant noise that leaks into captured output.
NOISE_LINES = {
    "MORE - hit RETURN/ENTER to continue",
    "Unexpected exception in PAUSE",
    "*",
}

# A sense header carries a derivation code like [XXXAO] / [BXXAS].
_SENSE_CODE = re.compile(r"\[\s*[A-Z]{3,6}\s*\]")
# Split the code out of the rest of a sense-header line.
_LEADING = re.compile(r"(.*?)\s*\[\s*[A-Z]{3,6}\s*\]\s*(.*)$", re.DOTALL)


def is_sense_header(line: str) -> bool:
    return bool(_SENSE_CODE.search(line))


def extract_pos(text: str) -> str | None:
    """Return the first POS token found in `text`, else None."""
    for token in POS_TOKENS:
        if re.search(rf"\b{token}\b", text):
            return token
    return None


def parse_sense_header(line: str) -> tuple[str | None, str | None]:
    """Return (lemma, pos) from a sense-header line.

    Handles the shapes seen in the wild:
      'humilitas, humilitatis  N (3rd) F   [XXXBO]'   -> ('humilitas, humilitatis', 'N')
      'sum, esse, fui, futurus  V   [XXXAX]'          -> ('sum, esse, fui, futurus', 'V')
      'in  PREP  ABL   [XXXAX]'                       -> ('in', 'PREP')
      'hic, haec, hoc  PRON   [XXXAX]'                -> ('hic, haec, hoc', 'PRON')
      ' [XXXAO]'                                      -> (None, None)
    """
    m = _LEADING.match(line.strip())
    if not m:
        return None, None
    prefix = m.group(1).strip()
    if not prefix:
        return None, None
    # Leftmost POS token found as a whole word (word-boundary so the 'N' in
    # "Non.," is not mistaken for the POS tag N).
    pos_match = None
    pos_token: str | None = None
    for token in POS_TOKENS:
        mm = re.search(rf"\b{token}\b", prefix)
        if mm and (pos_match is None or mm.start() < pos_match.start()):
            pos_match = mm
            pos_token = token
    if pos_match is None:
        return prefix, None
    head = prefix[: pos_match.start()].strip()
    if not head:
        return None, pos_token
    # Inflected lemma keeps its commas; otherwise use the single headword
    # (drops declension residue like 'ABL' that follows the POS tag).
    return closed_class_lemma(head, pos_token), pos_token


def closed_class_lemma(head: str, pos: str | None) -> str | None:
    """Return the display lemma for a sense header's lead-in text."""
    if "," in head:
        return head
    # 'careor, careri, caritus sum' style (comma present) is handled above;
    # a bare headword like 'in' / 'hic' returns the first token.
    return head.split()[0] if head.split() else None


def clean_lines(raw: str) -> list[str]:
    out: list[str] = []
    for line in raw.splitlines():
        s = line.strip()
        if not s or s in NOISE_LINES:
            continue
        out.append(s)
    return out


def is_gloss_line(line: str) -> bool:
    # Whitaker's gloss lines are semicolon-separated; morphology lines are not.
    return ";" in line or "(" in line


def parse_entry(entry: dict) -> dict:
    forms_pos: list[str] = []
    senses: list[dict] = []
    current: dict | None = None

    for line in clean_lines(entry.get("raw", "")):
        if is_sense_header(line):
            # Flush the previous sense.
            if current is not None:
                if current["gloss"] or current["lemma"]:
                    senses.append(current)
            lemma, pos = parse_sense_header(line)
            current = {"lemma": lemma, "pos": pos, "gloss": ""}
            continue
        if is_gloss_line(line):
            if current is None:
                current = {"lemma": None, "pos": None, "gloss": ""}
            current["gloss"] = (current["gloss"] + " " + line).strip()
            continue
        # A morphology line: record its POS for the entry-level pos list.
        pos = extract_pos(line)
        if pos and pos not in forms_pos:
            forms_pos.append(pos)
    if current is not None and (current["gloss"] or current["lemma"]):
        senses.append(current)

    # De-dup senses that share lemma+gloss (Whitaker repeats them per analysis).
    seen: set[tuple[str, str]] = set()
    deduped: list[dict] = []
    for s in senses:
        g = " ".join(s["gloss"].split())
        key = (s["lemma"] or "", g)
        if key in seen:
            continue
        seen.add(key)
        lemma = s["lemma"]
        # Pronominal / closed-class senses have an empty lemma line; use the
        # word that was asked for as the display headword.
        if lemma is None:
            lemma = entry["key"]
        deduped.append({"lemma": lemma, "pos": s["pos"], "gloss": g})
    # An empty gloss string is not useful in a dictionary entry.
    deduped = [s for s in deduped if s["gloss"]]

    return {
        "key": entry["key"],
        "form": entry["form"],
        "query": entry["query"],
        "count": entry["count"],
        "first": entry.get("first"),
        "pos": forms_pos,
        "senses": deduped,
        "no_gloss": not deduped,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--show", action="store_true", help="print a compact summary")
    args = parser.parse_args()

    if not SRC.is_file():
        raise SystemExit(f"Missing {SRC.relative_to(ROOT)}. Run tools/analyze_wordlist.py first.")

    data = json.loads(SRC.read_text(encoding="utf-8"))
    entries = [parse_entry(e) for e in data["analyses"]]
    entries.sort(key=lambda e: e["count"], reverse=True)
    no_gloss = [e["key"] for e in entries if e["no_gloss"]]

    payload = {
        "source": str(SRC.relative_to(ROOT)),
        "engine": data.get("engine"),
        "form_count": len(entries),
        "no_gloss_count": len(no_gloss),
        "entries": entries,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(entries)} entries, {len(no_gloss)} with no gloss)")

    if args.show:
        print("\n--- top 15 by frequency ---")
        for e in entries[:15]:
            first = e["senses"][0] if e["senses"] else None
            gloss = (first["gloss"][:60] + "…") if first and first["gloss"] else ""
            print(f"{e['count']:>4}  {e['key']:<14} {(first['pos'] or '-'):<5} {gloss}")
        if no_gloss:
            print(f"\n--- {len(no_gloss)} with no gloss (need review) ---")
            print(", ".join(no_gloss))


if __name__ == "__main__":
    main()
