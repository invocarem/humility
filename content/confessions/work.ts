import type { Chapter, Segment, Work } from "../schema";
import { scaffoldChapters } from "./scaffold";
import pusey from "./renderings/pusey.json";

/**
 * Confessions is wired to the auto-generated Latin scaffold. English is merged
 * from content/confessions/renderings/pusey.json so regenerating scaffold.ts
 * does not wipe it. Keep latin.md authoritative.
 *
 * A hand-written `close` column is still to come.
 */

type RenderingFile = {
  source: string;
  chapters: Record<string, Record<string, string>>;
};

function chapterKey(chapter: Chapter): string {
  return chapter.id.includes(":")
    ? chapter.id.split(":").slice(1).join(":")
    : String(chapter.number ?? "");
}

function applyRenderings(chapters: Chapter[]): Chapter[] {
  const file = pusey as RenderingFile;
  const eng = file.chapters;
  return chapters.map((chapter) => {
    const key = chapterKey(chapter);
    return {
      ...chapter,
      paragraphs: chapter.paragraphs.map((paragraph) => ({
        ...paragraph,
        segments: paragraph.segments.map(
          (segment): Segment => ({
            ...segment,
            translations: {
              pusey: eng[key]?.[paragraph.n ?? ""] ?? "",
            },
          }),
        ),
      })),
    };
  });
}

const renderedChapters = applyRenderings(scaffoldChapters);

const ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII"];

function bookOf(chapter: Chapter): number {
  const match = /^confessions:(\d+)\./.exec(chapter.id);
  return match ? Number(match[1]) : 0;
}

function chaptersIn(book: number): Chapter[] {
  return renderedChapters.filter((chapter) => bookOf(chapter) === book);
}

export const confessions: Work = {
  id: "confessions",
  title: "The Confessions",
  latinTitle: "Confessiones",
  source:
    "Working Latin in content/confessions/latin.md (The Latin Library, O'Donnell). The app never edits this file.",
  edition:
    "The Latin Library — O'Donnell electronic text of the Confessiones (Skutella 1934 as reprinted Juergens–Schaub 1981, with O'Donnell's corrections). All-lowercase as in that edition. A comparison with PL 32 is still to be made.",
  translations: [
    {
      id: "pusey",
      label: "Pusey, 1838",
      year: 1838,
      note: "E. B. Pusey, The Confessions of Saint Augustine (1838). Public domain (Project Gutenberg #3296). English paragraphs are aligned to the PL numbered blocks in latin.md; Gutenberg verse-line breaks are joined. A hand-written close column is still to come.",
    },
  ],
  parts: Array.from({ length: 13 }, (_, i) => {
    const book = i + 1;
    return {
      id: `book${book}`,
      title: `Liber ${ROMAN[book]}`,
      chapters: chaptersIn(book),
    };
  }),
};
