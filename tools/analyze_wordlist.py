#!/usr/bin/env python3
"""Run Whitaker over content/lexicon/forms.json.

Intended to run inside the whitaker-mcp image, where the Words binary exists:

    docker run --rm -v "${PWD}:/work" -w /work whitaker-mcp python tools/analyze_wordlist.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORMS = ROOT / "content" / "lexicon" / "forms.json"
OUT = ROOT / "content" / "lexicon" / "analyses.json"
WHITAKER_BIN = os.environ.get("WHITAKER_BIN", "/opt/whitakers-words/bin/words")
WHITAKER_DIR = os.environ.get("WHITAKER_DIR", "/opt/whitakers-words")


def call_whitaker(word: str) -> str:
    if not os.path.isfile(WHITAKER_BIN):
        raise SystemExit(
            f"Whitaker not found at {WHITAKER_BIN}. "
            "Run this script inside the whitaker Docker image."
        )
    proc = subprocess.run(
        [WHITAKER_BIN, word],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=WHITAKER_DIR,
    )
    if proc.returncode != 0:
        return f"Error: {proc.stderr.strip() or proc.returncode}"
    return proc.stdout


def analyze_one(entry: dict) -> dict:
    raw = call_whitaker(entry["query"])
    return {
        **entry,
        "raw": raw.strip(),
        "ok": not raw.startswith("Error:"),
    }


def main() -> None:
    if not FORMS.is_file():
        raise SystemExit(f"Missing {FORMS}. Run tools/extract_wordlist.py first.")
    data = json.loads(FORMS.read_text(encoding="utf-8"))
    forms = data["forms"]
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else len(forms)
    selected = forms[:limit]
    analyses = []
    for index, entry in enumerate(selected, start=1):
        analyses.append(analyze_one(entry))
        if index % 50 == 0 or index == len(selected):
            print(f"{index}/{len(selected)} {entry['form']}", flush=True)
    payload = {
        "source": data["source"],
        "engine": "whitakers-words",
        "form_count": len(analyses),
        "misses": sum(1 for item in analyses if not item["ok"]),
        "analyses": analyses,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} ({payload['misses']} misses)")


if __name__ == "__main__":
    main()
