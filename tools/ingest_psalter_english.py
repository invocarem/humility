#!/usr/bin/env python3
"""Fill the psalter's Coverdale + Douay-Rheims (Challoner) renderings.

Latin in content/psalter/latin.md (and the generated scaffold) is the index.
This script does not edit latin.md or scaffold.ts. It writes verse-keyed JSON
under content/psalter/renderings/, which work.ts merges on at load time.

Sources (fetched into content/psalter/sources/, gitignored):
  verses.json     isaacronan/douay-rheims-json (Gutenberg #8300 Challoner)
  psalms_1.html … psalms_5.html   Lynda Howell 1662 BCP Coverdale psalter

Usage:
    python tools/ingest_psalter_english.py
"""

from __future__ import annotations

import html
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PSALTER = ROOT / "content" / "psalter"
SOURCES = PSALTER / "sources"
RENDERINGS = PSALTER / "renderings"

TITLE_START = re.compile(
    r"^(In finem|Psalmus|Canticum|Alleluia|Tituli inscriptio|Oratio |"
    r"Intellectus|Ipsi David|Idithun|Pro |In hymnis|In carminibus)",
    re.I,
)

DROP_CAP = re.compile(
    r'<img[^>]*\balt="([^"]+)"[^>]*>',
    re.I,
)
PSALM_HEAD = re.compile(
    r'<a name="(\d+)">Psalm\s+\1\s*</a>',
    re.I,
)
BR = re.compile(r"<br\s*/?>", re.I)
TAG = re.compile(r"<[^>]+>")
VERSE_NUM = re.compile(r"^(\d+)\.\s+(.*)$")


def parse_latin(path: Path) -> dict[int, dict[int, str]]:
    psalms: dict[int, dict[int, str]] = {}
    current: int | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^## Psalmus (\d+)\s*$", line)
        if heading:
            current = int(heading.group(1))
            psalms[current] = {}
            continue
        verse = re.match(r"^(\d+)\.\s+(.*)$", line)
        if verse and current is not None:
            psalms[current][int(verse.group(1))] = verse.group(2).strip()
    return psalms


def strip_titles(text: str) -> str:
    remaining = text.strip()
    while remaining and TITLE_START.match(remaining):
        match = re.match(r"^[^.]+\.\s*", remaining)
        if not match:
            return ""
        remaining = remaining[match.end() :].strip()
    return remaining


def is_title_only(text: str) -> bool:
    return strip_titles(text) == ""


def load_douay_raw() -> dict[int, dict[int, str]]:
    verses_path = SOURCES / "verses.json"
    if not verses_path.is_file():
        raise SystemExit(
            f"Missing {verses_path}. Download isaacronan/douay-rheims-json "
            "verses.json into content/psalter/sources/"
        )
    data = json.loads(verses_path.read_text(encoding="utf-8"))
    out: dict[int, dict[int, str]] = defaultdict(dict)
    for row in data:
        if row.get("booknumber") != 21:
            continue
        out[int(row["chapternumber"])][int(row["versenumber"])] = row["text"].strip()
    return {k: dict(v) for k, v in out.items()}


def remap_continued(verses: dict[int, str]) -> dict[int, str]:
    """Psalm 115 / 147: Challoner sometimes keeps Hebrew continuation numbers."""
    keys = sorted(verses)
    if not keys:
        return verses
    if keys[0] == 1:
        return verses
    origin = keys[0]
    return {num - origin + 1: verses[num] for num in keys}


def split_once(text: str, marker: str) -> tuple[str, str]:
    idx = text.find(marker)
    if idx < 0:
        raise ValueError(f"split marker not found: {marker!r} in {text[:80]!r}")
    left = text[:idx].rstrip(" :;.")
    right = text[idx:].lstrip(" :;")
    right = right[0].upper() + right[1:] if right else right
    return left + ".", right


def align_douay(
    latin: dict[int, dict[int, str]],
    raw: dict[int, dict[int, str]],
) -> tuple[dict[int, dict[int, str]], list[str]]:
    notes: list[str] = []
    aligned: dict[int, dict[int, str]] = {}

    for psalm in range(1, 151):
        douay = remap_continued(raw[psalm])
        lat = latin[psalm]
        out: dict[int, str] = {}

        if psalm == 15:
            for n in range(1, 10):
                out[n] = douay[n]
            out[10] = douay[10].rstrip(" :;") + " " + douay[11]
            notes.append("Ps 15: joined Douay 10–11 onto Latin 10")
        elif psalm == 19:
            for n in range(1, 9):
                out[n] = douay[n]
            left, right = split_once(douay[9], "O Lord, save the king")
            out[9], out[10] = left, right
            notes.append("Ps 19: split Douay 9 onto Latin 9–10")
        elif psalm == 28:
            for n in range(1, 10):
                out[n] = douay[n]
            left, right = split_once(douay[10], "The Lord will give strength")
            out[10], out[11] = left, right
            notes.append("Ps 28: split Douay 10 onto Latin 10–11")
        elif psalm == 42:
            left, right = split_once(
                douay[5], "why art thou sad, O my soul?"
            )
            out[1], out[2], out[3] = douay[1], douay[2], douay[3]
            out[4] = douay[4].rstrip(" :;") + " " + left
            out[5] = right.rstrip(" :;") + " " + douay[6]
            notes.append("Ps 42: split Douay 5 across Latin 4–5; appended 6")
        elif psalm == 125:
            for n in range(1, 6):
                out[n] = douay[n]
            out[6] = douay[6].rstrip(" :;") + " " + douay[7]
            notes.append("Ps 125: joined Douay 6–7 onto Latin 6")
        elif psalm == 135:
            for n in range(1, 26):
                out[n] = douay[n]
            out[26] = douay[26].rstrip(" :;") + " " + douay[27]
            notes.append("Ps 135: joined Douay 26–27 onto Latin 26")
        elif psalm == 150:
            for n in range(1, 5):
                out[n] = douay[n]
            left, right = split_once(douay[5], "let every spirit praise the Lord")
            out[5], out[6] = left, right
            notes.append("Ps 150: split Douay 5 onto Latin 5–6")
        elif psalm in (115, 147):
            out = douay
            notes.append(f"Ps {psalm}: remapped continued verse numbers to 1..{len(douay)}")
        else:
            out = douay

        missing = [n for n in lat if n not in out or not out[n].strip()]
        extra = [n for n in out if n not in lat]
        if missing or extra:
            notes.append(
                f"Ps {psalm}: ALIGN GAP latin={len(lat)} douay={len(out)} "
                f"missing={missing} extra={extra}"
            )
        # Drop extras so JSON keys match Latin verses only.
        aligned[psalm] = {n: out[n] for n in lat if n in out}
    return aligned, notes


DAY_HEAD = re.compile(
    r"<center>\s*<strong>.*?Day\s+\d+\..*?</strong>\s*</center>",
    re.I | re.S,
)
HEADING_INCIPIT = re.compile(
    r"^</strong>\.\s*(?:</center>\s*)?(?:<center>\s*)?<em>.*?</em>\s*</center>",
    re.I | re.S,
)
LATIN_INCIPIT = re.compile(
    r"<center>\s*<em>.*?</em>\s*</center>",
    re.I | re.S,
)
JUNK_LINE = re.compile(
    r"^(Day\s+\d+\.|Morning Prayer\.?|Evening Prayer\.?|The Psalms.*|\.)$",
    re.I,
)


def parse_coverdale_html(path: Path) -> dict[int, dict[int, str]]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    parts = re.split(r'(?=<a name="\d+">Psalm\s+\d+\s*</a>)', raw, flags=re.I)
    psalms: dict[int, dict[int, str]] = {}
    for part in parts:
        head = PSALM_HEAD.search(part)
        if not head:
            continue
        number = int(head.group(1))
        body = part[head.end() :]
        # Next psalm / trailing nav: cut at the next psalm anchor if split kept extra.
        nxt = PSALM_HEAD.search(body)
        if nxt:
            body = body[: nxt.start()]
        body = HEADING_INCIPIT.sub("\n", body, count=1)
        body = re.sub(r"^</strong>\.?\s*", "", body, count=1)
        body = DAY_HEAD.sub("\n", body)
        body = LATIN_INCIPIT.sub("\n", body)
        # Psalm 119 (and similar) restart a drop-cap at each octet; restore the letter.
        body = DROP_CAP.sub(lambda match: html.unescape(match.group(1)), body)
        body = BR.sub("\n", body)
        body = TAG.sub(" ", body)
        body = html.unescape(body)
        lines = [re.sub(r"\s+", " ", line).strip() for line in body.splitlines()]
        lines = [line for line in lines if line and not JUNK_LINE.match(line)]
        lines = [line for line in lines if not line.endswith("&c.") and not line.endswith("&c")]
        verses: dict[int, str] = {}
        pending = ""
        for line in lines:
            numbered = VERSE_NUM.match(line)
            if numbered:
                if pending:
                    verses[1] = pending
                    pending = ""
                verses[int(numbered.group(1))] = numbered.group(2).strip()
            elif not verses:
                pending = (pending + " " + line).strip() if pending else line
            else:
                implied = max(verses) + 1
                if implied not in verses:
                    verses[implied] = line
                else:
                    last = max(verses)
                    verses[last] = verses[last] + " " + line
        if pending and 1 not in verses:
            verses[1] = pending
        if 1 in verses:
            verses[1] = verses[1].lstrip(". ").strip()
        psalms[number] = verses
    return psalms


def load_coverdale() -> dict[int, dict[int, str]]:
    files = sorted(SOURCES.glob("psalms_*.html"))
    if len(files) < 5:
        raise SystemExit(
            f"Missing Coverdale HTML in {SOURCES} (need psalms_1.html … psalms_5.html)"
        )
    merged: dict[int, dict[int, str]] = {}
    for path in files:
        parsed = parse_coverdale_html(path)
        overlap = set(merged) & set(parsed)
        if overlap:
            raise SystemExit(f"Coverdale psalm overlap in {path.name}: {sorted(overlap)}")
        merged.update(parsed)
    missing = [n for n in range(1, 151) if n not in merged]
    if missing:
        raise SystemExit(f"Coverdale missing psalms: {missing}")
    return merged


def hebrew_for(psalm_map: dict[str, list[str]], gallican: int) -> list[int]:
    return [int(h) for h in psalm_map[str(gallican)]]


def coverdale_for_gallican(
    gallican: int,
    coverdale: dict[int, dict[int, str]],
    psalm_map: dict[str, list[str]],
) -> list[str]:
    hebrew = hebrew_for(psalm_map, gallican)
    # Shared Hebrew psalm split across two Gallican psalms.
    if gallican == 114:
        verses = coverdale[116]
        return [verses[n] for n in sorted(verses) if n <= 9]
    if gallican == 115:
        verses = coverdale[116]
        return [verses[n] for n in sorted(verses) if n >= 10]
    if gallican == 146:
        verses = coverdale[147]
        return [verses[n] for n in sorted(verses) if n <= 11]
    if gallican == 147:
        verses = coverdale[147]
        return [verses[n] for n in sorted(verses) if n >= 12]

    lines: list[str] = []
    seen: set[int] = set()
    for heb in hebrew:
        if heb in seen:
            continue
        seen.add(heb)
        verses = coverdale[heb]
        lines.extend(verses[n] for n in sorted(verses))
    return lines


def align_coverdale(
    latin: dict[int, dict[int, str]],
    coverdale: dict[int, dict[int, str]],
    psalm_map: dict[str, list[str]],
) -> tuple[dict[int, dict[int, str]], list[str]]:
    notes: list[str] = []
    aligned: dict[int, dict[int, str]] = {}
    for psalm in range(1, 151):
        lat = latin[psalm]
        english = coverdale_for_gallican(psalm, coverdale, psalm_map)
        out: dict[int, str] = {n: "" for n in lat}
        body_nums = [n for n, text in lat.items() if not is_title_only(text)]
        title_nums = [n for n in lat if n not in body_nums]
        assigned = 0
        for idx, n in enumerate(body_nums):
            if idx < len(english):
                out[n] = english[idx]
                assigned += 1
        extras = english[assigned:]
        if extras and body_nums:
            last = body_nums[min(assigned, len(body_nums)) - 1]
            out[last] = (out[last] + " " + " ".join(extras)).strip()
            notes.append(
                f"Ps {psalm}: appended {len(extras)} extra Coverdale verse(s) "
                f"onto Latin {last} (Coverdale {len(english)} vs body {len(body_nums)})"
            )
        elif len(english) < len(body_nums):
            notes.append(
                f"Ps {psalm}: Coverdale short ({len(english)} vs body {len(body_nums)}; "
                f"titles {title_nums})"
            )
        aligned[psalm] = out
    return aligned, notes


def dump_rendering(path: Path, source: str, psalms: dict[int, dict[int, str]]) -> None:
    payload = {
        "source": source,
        "psalms": {
            str(psalm): {str(verse): text for verse, text in verses.items()}
            for psalm, verses in sorted(psalms.items())
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    verses = sum(len(v) for v in psalms.values())
    filled = sum(1 for verses in psalms.values() for text in verses.values() if text.strip())
    print(f"Wrote {path.relative_to(ROOT)} ({filled}/{verses} verses filled)")


def main() -> None:
    latin = parse_latin(PSALTER / "latin.md")
    psalm_map = json.loads((PSALTER / "psalm_map.json").read_text(encoding="utf-8"))

    douay_raw = load_douay_raw()
    douay, douay_notes = align_douay(latin, douay_raw)
    dump_rendering(
        RENDERINGS / "douay.json",
        "Douay-Rheims, Challoner revision (1749–52). Public domain. "
        "Text from Project Gutenberg #8300 via isaacronan/douay-rheims-json. "
        "Verse numbers follow the Gallican/Vulgate index in latin.md; a handful "
        "of Challoner splits are joined or split to match that index.",
        douay,
    )

    coverdale_raw = load_coverdale()
    coverdale, cov_notes = align_coverdale(latin, coverdale_raw, psalm_map)
    dump_rendering(
        RENDERINGS / "coverdale.json",
        "Miles Coverdale, Book of Common Prayer Psalter (Great Bible / 1662 BCP). "
        "Public domain. Transcription: Lynda Howell, eskimo.com/~lhowell/bcp1662. "
        "Hebrew numbering mapped onto the Gallican index via psalm_map.json; "
        "title-only Latin verses are left blank; leftover Coverdale verses are "
        "appended to the last assigned Latin verse.",
        coverdale,
    )

    print("Douay notes:")
    for note in douay_notes:
        print(f"  {note}")
    print("Coverdale notes (count mismatches only):")
    for note in cov_notes:
        print(f"  {note}")

    empty_douay = [
        (p, v)
        for p, verses in douay.items()
        for v, text in verses.items()
        if not text.strip()
    ]
    if empty_douay:
        print(f"EMPTY douay cells: {empty_douay}")
    else:
        print("Douay: every Latin verse has English.")


if __name__ == "__main__":
    main()
