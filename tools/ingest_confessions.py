#!/usr/bin/env python3
"""Build Confessions Latin + Pusey English from fetched public-domain sources.

Latin: The Latin Library HTML (O'Donnell electronic text), already fetched to
content/confessions/sources/latin/conf{1-13}.html.

English: E. B. Pusey, Project Gutenberg #3296, at
content/confessions/sources/english/pusey.txt.

Writes:
  content/confessions/latin.md              (authoritative Latin; app never edits)
  content/confessions/renderings/pusey.json (merged onto the scaffold by work.ts)

Does not edit scaffold.ts. After latin.md changes:

    python tools/ingest_latin.py --work confessions --scaffold
    python tools/ingest_confessions.py --english

Usage:
    python tools/ingest_confessions.py            # latin.md + pusey.json
    python tools/ingest_confessions.py --latin
    python tools/ingest_confessions.py --english
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "content" / "confessions"
SOURCES = WORK / "sources"
LATIN_DIR = SOURCES / "latin"
ENGLISH = SOURCES / "english" / "pusey.txt"
RENDERINGS = WORK / "renderings"

NUM_ONLY = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
NUM_START = re.compile(r"^(\d+)\.(\d+)\.(\d+)\s+(.*)$", re.S)
COMMENTARY = re.compile(r"\s*commentary on \d+\.\d+\.\d+\s*", re.I)
FOOTER = re.compile(
    r"\s*Augustine\s+Christian\s+Latin\s+The\s+Latin\s+Library\s+The\s+Classics\s+Page\s*$",
    re.I,
)
TAG = re.compile(r"<[^>]+>")
BOOK_HEAD = re.compile(r"^BOOK\s+([IVX]+)\s*$")
PG_START = "*** START OF THE PROJECT GUTENBERG"
PG_END = "*** END OF THE PROJECT GUTENBERG"

ROMAN = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7,
    "VIII": 8, "IX": 9, "X": 10, "XI": 11, "XII": 12, "XIII": 13,
}

EXPECTED_CHAPTERS = {
    1: 20, 2: 10, 3: 12, 4: 16, 5: 14, 6: 16, 7: 21,
    8: 12, 9: 13, 10: 43, 11: 31, 12: 32, 13: 38,
}

LATIN_HEADER = """\
# Confessiones Sancti Augustini

*App working text: Augustine, Confessiones (13 books), from The Latin Library \
(O'Donnell electronic text, Skutella 1934 as reprinted Juergens–Schaub 1981, \
with O'Donnell's corrections). Submitted to TLL by James J. O'Donnell. Public-domain \
Augustine; all-lowercase as in that edition; ae/oe written without ligatures. \
For the study reader only; the app never edits this file.*

---
"""


class Paragraphs(HTMLParser):
    """Collect visible <p> text, skipping TLL chrome."""

    SKIP_CLASS = {"pagehead", "border", "citation"}

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._buf: list[str] = []
        self._skip = False
        self._in_p = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table":
            self._skip = True
            return
        if tag != "p":
            if tag == "br" and self._in_p:
                self._buf.append(" ")
            return
        self._in_p = True
        self._buf = []
        classes = (dict(attrs).get("class") or "").split()
        self._skip = any(c in self.SKIP_CLASS for c in classes)

    def handle_endtag(self, tag: str) -> None:
        if tag != "p":
            return
        text = " ".join("".join(self._buf).split())
        text = COMMENTARY.sub(" ", text)
        text = TAG.sub(" ", text)
        text = html_lib.unescape(text)
        text = text.replace("<", " ").replace(">", " ")
        text = re.sub(r"\s+", " ", text).strip()
        text = text.strip(" \t\n\r\"")
        if not self._skip and text:
            self.parts.append(text)
        self._in_p = False
        self._buf = []

    def handle_data(self, data: str) -> None:
        if self._in_p:
            self._buf.append(data)


def parse_book_html(path: Path, book: int) -> list[tuple[int, int, int, str]]:
    """Return [(book, caput, pl_n, latin), ...] in order."""
    raw = path.read_text(encoding="latin-1", errors="replace")
    parser = Paragraphs()
    parser.feed(raw)

    out: list[tuple[int, int, int, str]] = []
    pending: tuple[int, int, int] | None = None

    def flush(body: str) -> None:
        nonlocal pending
        if pending is None:
            return
        b, c, n = pending
        text = FOOTER.sub("", re.sub(r"\s+", " ", body).strip()).strip()
        if text:
            out.append((b, c, n, text))
        pending = None

    current_body = ""
    for part in parser.parts:
        text = COMMENTARY.sub("", part).strip()
        text = FOOTER.sub("", text).strip()
        if not text:
            continue
        only = NUM_ONLY.match(part)
        start = NUM_START.match(part)
        if only:
            flush(current_body)
            current_body = ""
            pending = (int(only.group(1)), int(only.group(2)), int(only.group(3)))
            continue
        if start:
            flush(current_body)
            current_body = start.group(4).strip()
            pending = (int(start.group(1)), int(start.group(2)), int(start.group(3)))
            continue
        if pending is None:
            # Orphan (TLL chrome, hymn wrap before a number). Skip unless we
            # already have a body to extend.
            if out and not current_body:
                b, c, n, prev = out[-1]
                out[-1] = (b, c, n, (prev + " " + part).strip())
            continue
        current_body = (current_body + " " + part).strip() if current_body else part
    flush(current_body)

    # Drop sections whose book number doesn't match the file (safety).
    out = [row for row in out if row[0] == book]
    return out


def write_latin(books: dict[int, list[tuple[int, int, int, str]]]) -> Path:
    lines = [LATIN_HEADER.rstrip(), ""]
    for book in range(1, 14):
        rows = books[book]
        last_cap: int | None = None
        for _b, cap, n, text in rows:
            if cap != last_cap:
                if last_cap is not None:
                    lines.append("---")
                    lines.append("")
                lines.append(f"## Liber {book} Caput {cap}")
                lines.append("")
                last_cap = cap
            lines.append(f"{n}. {text}")
            lines.append("")
        lines.append("---")
        lines.append("")
    path = WORK / "latin.md"
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def parse_latin_md(path: Path) -> dict[str, dict[str, str]]:
    """chapter key '1.5' -> { '5': latin, '6': latin }."""
    chapters: dict[str, dict[str, str]] = {}
    current: str | None = None
    heading = re.compile(r"^##\s+Liber\s+(\d+)\s+Caput\s+(\d+)\s*$")
    verse = re.compile(r"^(\d+)\.\s+(.*)$")
    for line in path.read_text(encoding="utf-8").splitlines():
        h = heading.match(line)
        if h:
            current = f"{h.group(1)}.{h.group(2)}"
            chapters[current] = {}
            continue
        v = verse.match(line)
        if v and current is not None:
            chapters[current][v.group(1)] = v.group(2).strip()
    return chapters


def pusey_books(path: Path) -> dict[int, list[str]]:
    text = path.read_text(encoding="utf-8")
    start = text.find(PG_START)
    if start == -1:
        raise SystemExit(f"No Gutenberg start marker in {path}")
    end = text.find(PG_END)
    body = text[start : end if end != -1 else None]
    match = re.search(r"^BOOK I\s*$", body, re.M)
    if not match:
        raise SystemExit(f"No BOOK I heading in {path}")
    body = body[match.start() :]
    chunks = re.split(r"^BOOK\s+([IVX]+)\s*$", body, flags=re.M)
    out: dict[int, list[str]] = {}
    i = 1
    while i < len(chunks):
        numeral = chunks[i]
        content = chunks[i + 1] if i + 1 < len(chunks) else ""
        book = ROMAN.get(numeral)
        if book is None:
            raise SystemExit(f"Unknown BOOK numeral {numeral}")
        paras: list[str] = []
        for raw in re.split(r"\n\s*\n", content):
            para = re.sub(r"\s+", " ", raw).strip()
            if not para or BOOK_HEAD.match(para):
                continue
            paras.append(para)
        out[book] = paras
        i += 2
    return out


def is_fragment(text: str) -> bool:
    """Gutenberg often breaks verse quotations onto their own short lines."""
    s = text.strip()
    if not s:
        return True
    if s.upper() == "GRATIAS TIBI DOMINE":
        return True
    if len(s) < 130:
        return True
    if s.startswith(('"', "'")) and len(s) < 400:
        return True
    return False


def merge_to_count(paras: list[str], target: int) -> list[str]:
    """Join quote fragments, then any leftover extras from the end of the book.

    Extras in Pusey are almost always verse lines late in a book. Merging the
    globally shortest paragraph would glue an early caput onto its neighbour.
    """
    items = list(paras)
    i = 1
    while i < len(items):
        if is_fragment(items[i]):
            items[i - 1] = (items[i - 1] + " " + items[i]).strip()
            del items[i]
            continue
        i += 1
    while len(items) > target:
        items[-2] = (items[-2] + " " + items[-1]).strip()
        del items[-1]
    return items


SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'])")


def split_to_count(paras: list[str], target: int) -> list[str]:
    """Split the longest sentence-bearing paragraphs until `target` items."""
    items = list(paras)
    while len(items) < target:
        best_i = -1
        best_at = -1
        best_len = 0
        for i, para in enumerate(items):
            marks = list(SENTENCE.finditer(para))
            if not marks:
                continue
            mid = len(para) / 2
            at = min(marks, key=lambda m: abs(m.start() - mid)).start()
            left, right = para[:at].strip(), para[at:].strip()
            if len(left) < 80 or len(right) < 80:
                continue
            if len(para) > best_len:
                best_len = len(para)
                best_i = i
                best_at = at
        if best_i < 0:
            break
        para = items[best_i]
        items[best_i : best_i + 1] = [para[:best_at].strip(), para[best_at:].strip()]
    return items


def partition(items: list[str], n: int) -> list[str]:
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


def align_book(english: list[str], latin_ns: list[str]) -> tuple[list[str], str]:
    target = len(latin_ns)
    src = list(english)
    note = f"Pusey {len(src)} paras → Latin {target}"
    if len(src) > target:
        src = merge_to_count(src, target)
        note += f" (merged to {len(src)})"
    if len(src) < target:
        src = split_to_count(src, target)
        note += f" (split to {len(src)})"
    if len(src) != target:
        src = partition(src, target)
        note += " then partitioned"
    return src, note


def write_pusey(latin: dict[str, dict[str, str]], english: dict[int, list[str]]) -> Path:
    # Flatten Latin in book order so we can align per book, then re-key by chapter.
    by_book: dict[int, list[tuple[str, str]]] = {i: [] for i in range(1, 14)}
    for key in sorted(latin, key=lambda k: tuple(map(int, k.split(".")))):
        book = int(key.split(".")[0])
        for n, _text in latin[key].items():
            by_book[book].append((key, n))

    aligned: dict[str, dict[str, str]] = {key: {} for key in latin}
    notes: list[str] = []
    for book in range(1, 14):
        slots = by_book[book]
        groups, note = align_book(english.get(book, []), [n for _k, n in slots])
        notes.append(f"book {book}: {note}")
        for (key, n), text in zip(slots, groups):
            aligned[key][n] = text

    payload = {
        "source": (
            "E. B. Pusey, The Confessions of Saint Augustine (1838). "
            "Public domain (Project Gutenberg #3296). English paragraphs are "
            "aligned to the PL numbered blocks in latin.md; quote-line breaks "
            "in the Gutenberg text are joined, and a few books are split or "
            "merged so the counts match."
        ),
        "chapters": aligned,
    }
    RENDERINGS.mkdir(parents=True, exist_ok=True)
    out = RENDERINGS / "pusey.json"
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
    sample = aligned.get("1.1", {}).get("1", "")[:80]
    print(f"I.1 §1: {sample}")
    return out


def build_latin() -> dict[int, list[tuple[int, int, int, str]]]:
    books: dict[int, list[tuple[int, int, int, str]]] = {}
    for i in range(1, 14):
        path = LATIN_DIR / f"conf{i}.html"
        if not path.is_file():
            raise SystemExit(f"Missing {path}. Fetch The Latin Library conf{i}.shtml first.")
        rows = parse_book_html(path, i)
        books[i] = rows
        caps = sorted({r[1] for r in rows})
        paras = [r[2] for r in rows]
        expected = EXPECTED_CHAPTERS[i]
        print(
            f"  book {i}: {len(rows)} paragraphs, capita {caps[0]}–{caps[-1]} "
            f"(n={len(caps)}, expected {expected}), PL {min(paras)}–{max(paras)}"
        )
        missing = set(range(1, expected + 1)) - set(caps)
        if missing:
            print(f"    missing capita: {sorted(missing)}")
        if paras != list(range(paras[0], paras[-1] + 1)):
            gap = [n for n in range(paras[0], paras[-1] + 1) if n not in paras]
            print(f"    PL gaps: {gap}")
    path = write_latin(books)
    total = sum(len(v) for v in books.values())
    chapters = sum(len({r[1] for r in v}) for v in books.values())
    print(f"Wrote {path.relative_to(ROOT)} ({chapters} capita, {total} paragraphs)")
    return books


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--latin", action="store_true")
    ap.add_argument("--english", action="store_true")
    args = ap.parse_args()
    do_latin = args.latin or not args.english
    do_english = args.english or not args.latin

    if do_latin:
        print("ingest confessions: Latin from The Latin Library HTML")
        build_latin()

    if do_english:
        latin_md = WORK / "latin.md"
        if not latin_md.is_file():
            raise SystemExit(f"Missing {latin_md}; run with --latin first")
        if not ENGLISH.is_file():
            raise SystemExit(f"Missing {ENGLISH}")
        print("ingest confessions: Pusey from Gutenberg #3296")
        write_pusey(parse_latin_md(latin_md), pusey_books(ENGLISH))


if __name__ == "__main__":
    main()
