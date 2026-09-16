/** Paragraph bodies from a work's latin.md, matching tools/ingest_latin.py grouping. */

const H1 = /^#\s+(.*)$/;
const H2 = /^#{2,}\s+(.*)$/;
const PARA_MARK = /^(R\.(\d+)|(\d+))\.\s+(.*)$/;
const EDITORIAL = /^\*/;
const UNNUMBERED_PARA_ID: Record<string, string> = { praefatio: "pref" };

export type LatinParagraph = { id: string; n: string; latin: string };

type ChapterAcc = {
  cid: string;
  heading: string;
  paragraphs: LatinParagraph[];
};

function chapterId(title: string): string {
  const first = title.trim().split(/\s+/)[0]?.toLowerCase() ?? "untitled";
  if (first === "conversio") return "admonitio";
  if (first === "retractatio" || first === "praefatio" || first === "admonitio") {
    return first;
  }
  return first;
}

function finalize(ch: ChapterAcc): void {
  if (!ch.paragraphs.length && ch.heading) {
    const pid = UNNUMBERED_PARA_ID[ch.cid] ?? ch.cid;
    ch.paragraphs.push({ id: pid, n: "", latin: ch.heading });
    ch.heading = "";
  }
}

/** Map paragraph id → latin body (whitespace later normalized by the caller). */
export function parseLatinMd(source: string): Map<string, string> {
  const chapters: ChapterAcc[] = [];
  let seenTitle = false;

  const startChapter = (title: string) => {
    if (chapters.length) finalize(chapters[chapters.length - 1]!);
    chapters.push({ cid: chapterId(title), heading: "", paragraphs: [] });
  };

  for (const raw of source.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line === "---" || EDITORIAL.test(line)) continue;
    const h2 = H2.exec(raw);
    if (h2) {
      startChapter(h2[1]!.trim());
      continue;
    }
    const h1 = H1.exec(raw);
    if (h1) {
      seenTitle = true;
      void seenTitle;
      continue;
    }
    if (!chapters.length) continue;
    const ch = chapters[chapters.length - 1]!;
    const pm = PARA_MARK.exec(line);
    if (pm) {
      const digit = pm[2] ?? pm[3]!;
      const n = pm[2] ? `R.${digit}` : digit;
      const id = pm[2] ? `r${digit}` : `p${digit}`;
      ch.paragraphs.push({ id, n, latin: pm[4]!.trim() });
    } else if (ch.paragraphs.length) {
      const last = ch.paragraphs[ch.paragraphs.length - 1]!;
      last.latin = `${last.latin} ${line}`.trim();
    } else {
      ch.heading = ch.heading ? `${ch.heading} ${line}` : line;
    }
  }
  if (chapters.length) finalize(chapters[chapters.length - 1]!);

  const out = new Map<string, string>();
  for (const ch of chapters) {
    for (const p of ch.paragraphs) out.set(p.id, p.latin);
  }
  return out;
}
