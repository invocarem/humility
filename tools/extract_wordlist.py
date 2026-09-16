#!/usr/bin/env python3
"""Build a unique-form list from a work's Latin source. No morphology.

Usage:
    python tools/extract_wordlist.py                 # default: content/gradibus/latin.md
    python tools/extract_wordlist.py --work psalter
    python tools/extract_wordlist.py --work rule
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"

SKIP_HEADING = re.compile(
    r"^(Retractatio|Praefatio|Caput|Admonitio|Conversio|Prologus|Capitulum|"
    r"Liber|Psalmus|Confessiones)\b",
    re.IGNORECASE,
)
EDITORIAL = re.compile(r"^\*")
PARA_MARK = re.compile(r"^(R\.\d+|\d+)\.\s+")
CITATION = re.compile(
    r"\("
    r"(?:(?:[IVX]+|[123])\s+)?"
    r"(?:"
    r"Marc|Luc|Ioan|Matth|Reg|Gen|Eccli|Hebr|Phil|Petr|Cor|Rom|"
    r"Coloss|Isai|Psal|Galat|Ierem|Act|Iob|num|cap"
    r")\.?"
    r"[^)]*"
    r"\)",
    re.IGNORECASE,
)
TOKEN = re.compile(r"[A-Za-z]+")
STEM_FIXES = (("charit", "carit"),)

# Leftovers from titles, notes, and stripped citations.
DROP = {
    "pl",
    "sbo",
    "leclercq",
    "rochais",
    "mlt",
    "pdf",
    "coll",
    "app",
    "working",
    "text",
    "bernar",
    "abbatis",
}


def normalize_query(form: str) -> str:
    query = form.lower().replace("j", "i").replace("v", "u")
    for old, new in STEM_FIXES:
        if query.startswith(old):
            query = new + query[len(old) :]
    return query


def clean_line(line: str) -> str:
    line = line.strip()
    if not line or line == "---":
        return ""
    if EDITORIAL.match(line):
        return ""
    if line.startswith("#"):
        rest = line.lstrip("#").strip()
        if SKIP_HEADING.match(rest):
            return ""
        line = rest
    line = PARA_MARK.sub("", line)
    line = CITATION.sub(" ", line)
    return line


def extract(text: str) -> dict:
    counts: Counter[str] = Counter()
    printed: dict[str, str] = {}
    first_n: dict[str, str] = {}
    current_n = ""

    for raw in text.splitlines():
        mark = PARA_MARK.match(raw.strip())
        if mark:
            current_n = mark.group(1)
        line = clean_line(raw)
        if not line:
            continue
        for token in TOKEN.findall(line):
            key = token.lower()
            if key in DROP or (len(key) == 1 and key not in {"a", "e", "o"}):
                continue
            counts[key] += 1
            printed.setdefault(key, token)
            first_n.setdefault(key, current_n)

    forms = []
    for key, count in counts.most_common():
        form = printed[key]
        forms.append(
            {
                "form": form,
                "key": key,
                "query": normalize_query(form),
                "count": count,
                "first": first_n.get(key) or None,
            }
        )
    return {
        "source": "",
        "form_count": len(forms),
        "token_count": sum(counts.values()),
        "forms": forms,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", default="gradibus", help="work id (default: gradibus)")
    args = parser.parse_args()

    source = CONTENT / args.work / "latin.md"
    out = CONTENT / args.work / "lexicon" / "forms.json"
    if not source.is_file():
        raise SystemExit(f"Missing {source.relative_to(ROOT)}")

    data = extract(source.read_text(encoding="utf-8"))
    data["source"] = str(source.relative_to(ROOT))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT)} ({data['form_count']} forms, {data['token_count']} tokens)")


if __name__ == "__main__":
    main()
