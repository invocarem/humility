#!/usr/bin/env python3
"""Merge curated work gloss overrides into a work's lexicon.json.

Reads content/<work>/lexicon/overrides.json (hand-authored dictionary cards) and
content/<work>/lexicon/lexicon.json (the Whitaker-derived base from
tools/parse_analyses.py), then writes lexicon.json back with an `edited`
card attached to each matching entry.  The reader prefers `edited.gloss`
when present.

Re-running is idempotent: any existing `edited` field is first removed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", default="gradibus", help="work id (default: gradibus)")
    args = parser.parse_args()

    lexdir = CONTENT / args.work / "lexicon"
    lex = json.loads((lexdir / "lexicon.json").read_text(encoding="utf-8"))
    overrides = json.loads((lexdir / "overrides.json").read_text(encoding="utf-8"))["entries"]

    entries = lex["entries"]
    by_key = {e["key"]: e for e in entries}

    missing = sorted(k for k in overrides if k not in by_key)
    applied = 0
    for e in entries:
        e.pop("edited", None)
        e.pop("curated", None)
        card = overrides.get(e["key"])
        if card:
            e["edited"] = dict(card)
            e["curated"] = True
            applied += 1

    lex["curated_count"] = applied
    (lexdir / "lexicon.json").write_text(
        json.dumps(lex, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"lexicon.json: {len(entries)} entries, {applied} curated")
    if missing:
        print(f"WARN: override keys with no lexicon entry ({len(missing)}): {missing}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
