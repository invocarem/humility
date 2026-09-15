import type { Chapter, Segment, Work } from "../schema";
import { scaffoldChapters } from "./scaffold";
import verheyen from "./renderings/verheyen.json";

/**
 * The Rule is wired to the auto-generated Latin scaffold. English is merged
 * from content/rule/renderings/verheyen.json so regenerating scaffold.ts does
 * not wipe it. Keep latin.md authoritative.
 *
 * Verheyen is paragraph-broken more finely than the working Latin; the ingest
 * joins English paragraphs onto those coarser numbered blocks. A hand-written
 * `close` column is still to come.
 */

type RenderingFile = {
  source: string;
  titles: Record<string, string>;
  chapters: Record<string, Record<string, string>>;
};

function chapterKey(chapter: Chapter): string {
  if (chapter.number !== undefined) {
    return String(chapter.number);
  }
  return chapter.id.includes(":") ? chapter.id.split(":").slice(1).join(":") : chapter.id;
}

function applyRenderings(chapters: Chapter[]): Chapter[] {
  const file = verheyen as RenderingFile;
  const eng = file.chapters;
  const titles = file.titles;
  return chapters.map((chapter) => {
    const key = chapterKey(chapter);
    return {
      ...chapter,
      heading: titles[key] ?? chapter.heading,
      paragraphs: chapter.paragraphs.map((paragraph) => ({
        ...paragraph,
        segments: paragraph.segments.map(
          (segment): Segment => ({
            ...segment,
            translations: {
              verheyen: eng[key]?.[paragraph.n ?? ""] ?? "",
            },
          }),
        ),
      })),
    };
  });
}

const renderedChapters = applyRenderings(scaffoldChapters);

function numbered(lo: number, hi: number): Chapter[] {
  return renderedChapters.filter(
    (chapter) => chapter.number !== undefined && chapter.number >= lo && chapter.number <= hi,
  );
}

// Thematic division of the Rule, in the spirit of De gradibus's editorial
// parts (meaningful boundaries + titles rather than bare ranges). Chapter
// headings themselves come from Verheyen's `titles` map (fed through
// applyRenderings), so this table only groups them.
const THEMATIC = [
  ["prologus", "Prologus", undefined, undefined],
  ["foundations", "Capitula 1–7 — The foundations of monastic life", 1, 7],
  ["office", "Capitula 8–20 — The Divine Office", 8, 20],
  ["discipline", "Capitula 21–30 — Community discipline and correction", 21, 30],
  ["care", "Capitula 31–37 — The cellarer and care of the weak", 31, 37],
  ["daily", "Capitula 38–57 — Reading, labour, and food", 38, 57],
  ["reception", "Capitula 58–66 — Reception and rank in the community", 58, 66],
  ["fraternal", "Capitula 67–73 — Fraternal correction and the epilogue", 67, 73],
] as const;

export const rule: Work = {
  id: "rule",
  title: "The Rule of St Benedict",
  latinTitle: "Regula Sancti Benedicti",
  source:
    "Working Latin in content/rule/latin.md (traditional monastic text). The app never edits this file.",
  edition:
    "The Latin Library, benedict.html — traditional monastic text of the Regula Benedicti (prologue + 73 chapters); ae/oe written without ligatures. A critical text (RB 1980 / de Vogüé) is still to be compared.",
  translations: [
    {
      id: "verheyen",
      label: "Verheyen, 1949",
      year: 1949,
      note: "Boniface Verheyen, The Holy Rule of St. Benedict (1949). Public domain (CCEL / Project Gutenberg). English paragraphs are joined onto the coarser numbered blocks in latin.md; they are not a 1:1 sentence alignment.",
    },
  ],
  parts: THEMATIC.map(([id, title, lo, hi]) => ({
    id,
    title,
    chapters:
      lo === undefined
        ? renderedChapters.filter((chapter) => chapter.id === "rule:prologus")
        : numbered(lo!, hi!),
  })),
};
