#!/usr/bin/env python3
"""Fill the Rule's Verheyen rendering from content/rule/verheyen.txt.

Latin in latin.md is the index. This does not edit latin.md or scaffold.ts.
It writes content/rule/renderings/verheyen.json, which work.ts merges on.

Verheyen is paragraph-broken more finely than the working Latin (many chapters
are a handful of long numbered blocks). English paragraphs for a chapter are
joined in order onto those Latin blocks, as evenly as possible.

Usage:
    python tools/ingest_rule_english.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULE = ROOT / "content" / "rule"
RENDERINGS = RULE / "renderings"

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
    "LXIX": 69, "LXX": 70, "LXXI": 71, "LXXII": 72, "LXXIII": 73,
}

HR = re.compile(r"^_+$")
CHAPTER = re.compile(r"^CHAPTER\s+([IVXLCDM]+)\s*$")
PROLOGUE = re.compile(r"^PROLOGUE\s*$")
INDEXES = re.compile(r"^Indexes\s*$", re.I)


def parse_latin(path: Path) -> dict[str, dict[int, str]]:
    chapters: dict[str, dict[int, str]] = {}
    current: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^##\s+(.*)$", line)
        if heading:
            title = heading.group(1).strip()
            cap = re.match(r"^Capitulum\s+(\d+)\s*$", title)
            current = cap.group(1) if cap else title.lower()
            chapters[current] = {}
            continue
        verse = re.match(r"^(\d+)\.\s+(.*)$", line)
        if verse and current is not None:
            chapters[current][int(verse.group(1))] = verse.group(2).strip()
    return chapters


def blocks(lines: list[str]) -> list[str]:
    """Join wrapped CCEL lines; split on blank lines."""
    paras: list[str] = []
    buf: list[str] = []
    for line in lines:
        if not line:
            if buf:
                paras.append(" ".join(buf))
                buf = []
            continue
        buf.append(line)
    if buf:
        paras.append(" ".join(buf))
    return paras


def parse_verheyen(path: Path) -> tuple[dict[str, list[str]], dict[str, str]]:
    raw = path.read_text(encoding="utf-8")
    lines = [re.sub(r"\s+", " ", line).strip() for line in raw.splitlines()]
    lines = ["" if HR.match(line) else line for line in lines]

    out: dict[str, list[str]] = {}
    titles: dict[str, str] = {}
    i = 0
    while i < len(lines) and not PROLOGUE.match(lines[i]):
        i += 1
    if i >= len(lines):
        raise SystemExit(f"No PROLOGUE heading in {path}")
    i += 1
    chunk: list[str] = []
    current = "prologus"

    def flush():
        paras = blocks(chunk)
        if current == "prologus":
            out[current] = paras
            return
        # First block after CHAPTER N is the English chapter title, not body.
        titles[current] = paras[0] if paras else ""
        out[current] = paras[1:] if len(paras) > 1 else []

    while i < len(lines):
        line = lines[i]
        if INDEXES.match(line):
            break
        ch = CHAPTER.match(line)
        if ch:
            flush()
            n = ROMAN.get(ch.group(1))
            if n is None:
                raise SystemExit(f"Unknown chapter numeral {ch.group(1)}")
            current = str(n)
            chunk = []
            i += 1
            continue
        chunk.append(line)
        i += 1
    flush()
    return out, titles


def split_ch4(items: list[str]) -> list[str]:
    """RB 4: Latin has three blocks (instruments 1–22, 23–62, 63–end + coda).

    Verheyen prints the 73 instruments as one wrapped paragraph, then the
    'Behold…' coda. Split the numbered list so each Latin block has English.
    """
    if not items:
        return ["", "", ""]
    body, *rest = items
    coda = " ".join(rest).strip()
    marks = list(re.finditer(r"\((\d+)\)\s+", body))
    starts = {int(m.group(1)): m.start() for m in marks}

    def slice_from(lo: int, hi: int | None) -> str:
        a = starts.get(lo)
        if a is None:
            return ""
        b = starts.get(hi) if hi is not None else len(body)
        if b is None:
            b = len(body)
        return body[a:b].strip()

    third = " ".join(p for p in (slice_from(63, None), coda) if p)
    return [slice_from(1, 23), slice_from(23, 63), third]


def split_ch7(items: list[str]) -> list[str]:
    """RB 7: Latin has 16 blocks; Verheyen has 18 paragraphs.

    The extras are splits *inside* Latin §3 (first degree: fear of God, then
    'God always seeth') and Latin §16 (twelfth degree + coda). Even-splitting
    from the start shoved Jacob's ladder into Latin §1 and shifted every
    later degree by one.
    """
    if len(items) != 18:
        return partition(items, 16)
    # Verheyen paragraph indices for each Latin 1..16.
    groups = [
        [0], [1], [2, 3], [4], [5], [6], [7], [8],
        [9], [10], [11], [12], [13], [14], [15], [16, 17],
    ]
    return [" ".join(items[i] for i in g).strip() for g in groups]


def partition(items: list[str], n: int) -> list[str]:
    """Split `items` into `n` contiguous groups, joined, as evenly as possible."""
    if n <= 0:
        return []
    if not items:
        return [""] * n
    base, extra = divmod(len(items), n)
    out: list[str] = []
    i = 0
    for k in range(n):
        take = base + (1 if k < extra else 0)
        if take == 0:
            out.append("")
        else:
            out.append(" ".join(items[i : i + take]).strip())
            i += take
    return out


def main() -> None:
    latin = parse_latin(RULE / "latin.md")
    english, titles = parse_verheyen(RULE / "verheyen.txt")

    missing = [k for k in latin if k not in english]
    extra = [k for k in english if k not in latin]
    if missing or extra:
        print(f"chapter key mismatch missing={missing} extra={extra}")

    aligned: dict[str, dict[str, str]] = {}
    notes: list[str] = []
    for key, verses in latin.items():
        nums = sorted(verses)
        src = english.get(key, [])
        if key == "4":
            groups = split_ch4(src)
        elif key == "7":
            groups = split_ch7(src)
        else:
            groups = partition(src, len(nums))
        aligned[key] = {str(n): groups[i] for i, n in enumerate(nums)}
        eng_n = len(english.get(key, []))
        if eng_n != len(nums):
            notes.append(
                f"ch {key}: Verheyen {eng_n} paras → Latin {len(nums)} blocks"
            )

    payload = {
        "source": (
            "Boniface Verheyen, The Holy Rule of St. Benedict (1949). "
            "Public domain (CCEL / Project Gutenberg). English paragraphs are "
            "joined onto the coarser numbered blocks in latin.md."
        ),
        "titles": titles,
        "chapters": aligned,
    }
    RENDERINGS.mkdir(parents=True, exist_ok=True)
    out = RENDERINGS / "verheyen.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    filled = sum(1 for ch in aligned.values() for t in ch.values() if t.strip())
    total = sum(len(ch) for ch in aligned.values())
    print(f"Wrote {out.relative_to(ROOT)} ({filled}/{total} Latin blocks filled)")
    empty = [
        f"{ch}:{n}"
        for ch, verses in aligned.items()
        for n, text in verses.items()
        if not text.strip()
    ]
    if empty:
        print(f"EMPTY cells: {empty}")
    print("Alignment notes:")
    for note in notes:
        print(f"  {note}")
    # smoke
    p1 = aligned.get("prologus", {}).get("1", "")[:80]
    c1 = aligned.get("1", {}).get("1", "")[:80]
    print(f"Prologus 1: {p1}")
    print(f"Cap. 1 §1: {c1}")


if __name__ == "__main__":
    main()
