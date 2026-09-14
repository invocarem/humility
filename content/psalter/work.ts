import type { Chapter, Segment, Work } from "../schema";
import { scaffoldChapters } from "./scaffold";
import coverdale from "./renderings/coverdale.json";
import douay from "./renderings/douay.json";

/**
 * The Psalter is wired to the auto-generated Latin scaffold. English columns
 * are merged from content/psalter/renderings/ (Coverdale 1662 BCP + Douay-
 * Rheims Challoner) so regenerating scaffold.ts does not wipe them.
 *
 * Coverdale uses Hebrew numbering; psalm_map.json plus title-skipping give
 * loose verse alignment. Douay follows Vulgate numbering and is 1:1 with
 * the Gallican Latin. Keep latin.md authoritative.
 */

type RenderingFile = {
  source: string;
  psalms: Record<string, Record<string, string>>;
};

function applyRenderings(chapters: Chapter[]): Chapter[] {
  const cov = (coverdale as RenderingFile).psalms;
  const dr = (douay as RenderingFile).psalms;
  return chapters.map((chapter) => {
    const psalm = String(chapter.number ?? "");
    return {
      ...chapter,
      paragraphs: chapter.paragraphs.map((paragraph) => ({
        ...paragraph,
        segments: paragraph.segments.map(
          (segment): Segment => ({
            ...segment,
            translations: {
              coverdale: cov[psalm]?.[paragraph.n ?? ""] ?? "",
              douay: dr[psalm]?.[paragraph.n ?? ""] ?? "",
            },
          }),
        ),
      })),
    };
  });
}

const renderedChapters = applyRenderings(scaffoldChapters);

// Book boundaries by psalm (Gallican/Vulgate numbering).
const BOOKS: Array<[string, string, [number, number]]> = [
  ["book1", "Liber I (Psalmi 1–41)", [1, 41]],
  ["book2", "Liber II (Psalmi 42–72)", [42, 72]],
  ["book3", "Liber III (Psalmi 73–89)", [73, 89]],
  ["book4", "Liber IV (Psalmi 90–106)", [90, 106]],
  ["book5", "Liber V (Psalmi 107–150)", [107, 150]],
];

function chaptersIn(lo: number, hi: number): Chapter[] {
  return renderedChapters.filter(
    (chapter) => chapter.number !== undefined && chapter.number >= lo && chapter.number <= hi,
  );
}

export const psalter: Work = {
  id: "psalter",
  title: "The Psalms (Gallican Psalter)",
  latinTitle: "Psalterium Gallicanum",
  source:
    "Working Latin in content/psalter/latin.md (Vulgata Clementina, iuxta LXX). The app never edits this file.",
  edition: "Vulgata Clementina — Psalterium Gallicanum (iuxta LXX), the office psalter of the Benedictine and Roman Divine Office.",
  translations: [
    {
      id: "coverdale",
      label: "Coverdale, 1662",
      year: 1540,
      note: "Miles Coverdale's Great Bible psalter as printed in the 1662 Book of Common Prayer. Public domain. Translated from the Hebrew (Masoretic numbering), so it does not verse-align with the Gallican-Latin index wherever the Septuagint and Hebrew texts split or merge verses. psalm_map.json documents the psalm-level LXX↔Hebrew numbering splits. Treat this column as the literary/rhythmic voice with loose alignment.",
    },
    {
      id: "douay",
      label: "Douay-Rheims (Challoner) — close",
      year: 1750,
      note: "Douay-Rheims, Challoner revision (1749–52), in Vulgate (= Gallican/Septuagint) numbering. Public domain (Project Gutenberg #8300). Because it translates the Vulgate it aligns 1:1 with the working Gallican Latin — same psalms, same verses — making it the aligned 'close' companion to Coverdale.",
    },
  ],
  parts: BOOKS.map(([id, title, [lo, hi]]) => ({
    id,
    title,
    chapters: chaptersIn(lo, hi),
  })),
};
