#!/usr/bin/env python3
"""Merge curated Bernard gloss overrides into lexicon.json.

Reads content/lexicon/overrides.json (hand-authored dictionary cards) and
content/lexicon/lexicon.json (the Whitaker-derived base from
tools/parse_analyses.py), then writes lexicon.json back with an `edited`
card attached to each matching entry.  The reader prefers `edited.gloss`
when present.

Re-running is idempotent: any existing `edited` field is first removed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEXICON = ROOT / "content" / "lexicon" / "lexicon.json"
OVERRIDES = ROOT / "content" / "lexicon" / "overrides.json"


def main() -> None:
    lexicon = json.loads(LEXICON.read_text(encoding="utf-8"))
    overrides = json.loads(OVERRIDES.read_text(encoding="utf-8"))["entries"]

    entries = lexicon["entries"]
    by_key = {e["key"]: e for e in entries}

    missing = sorted(k for k in overrides if k not in by_key)
    applied = 0
    for e in entries:
        e.pop("edited", None)
        card = overrides.get(e["key"])
        if card:
            e["edited"] = dict(card)
            e["curated"] = True
            applied += 1

    lexicon["curated_count"] = applied
    LEXICON.write_text(json.dumps(lexicon, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"lexicon.json: {len(entries)} entries, {applied} curated")
    if missing:
        print(f"WARN: override keys with no lexicon entry ({len(missing)}): {missing}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
