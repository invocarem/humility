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
  parts: [
    {
      id: "prologus",
      title: "Prologus",
      chapters: renderedChapters.filter((chapter) => chapter.id === "rule:prologus"),
    },
    {
      id: "foundations",
      title: "Capitula 1–7",
      chapters: numbered(1, 7),
    },
    {
      id: "office",
      title: "Capitula 8–20",
      chapters: numbered(8, 20),
    },
    {
      id: "community",
      title: "Capitula 21–73",
      chapters: numbered(21, 73),
    },
  ],
};
