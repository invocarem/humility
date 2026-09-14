import type { Chapter, Work } from "../schema";
import { scaffoldChapters } from "./scaffold";

/**
 * The Psalter is wired directly to the auto-generated scaffold for now
 * (Latin filled, translations still blank). Book grouping follows the
 * traditional five-fold division of the Psalter; chapters are the scaffold's
 * `psalter:1`..`psalter:150`.
 *
 * Next: fill the `coverdale` rendering from the PD 1540 Prayer-Book psalter
 * and the hand-written `close`, then (optionally) split `scaffoldChapters`
 * into per-book `parts/*.ts` files. Keep latin.md authoritative.
 */

// Book boundaries by psalm (Gallican/Vulgate numbering).
const BOOKS: Array<[string, string, [number, number]]> = [
  ["book1", "Liber I (Psalmi 1–41)", [1, 41]],
  ["book2", "Liber II (Psalmi 42–72)", [42, 72]],
  ["book3", "Liber III (Psalmi 73–89)", [73, 89]],
  ["book4", "Liber IV (Psalmi 90–106)", [90, 106]],
  ["book5", "Liber V (Psalmi 107–150)", [107, 150]],
];

function chaptersIn(lo: number, hi: number): Chapter[] {
  return scaffoldChapters.filter(
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
      label: "Coverdale, 1540",
      year: 1540,
      note: "Miles Coverdale's Great Bible psalter, public domain. Famous for being close, faithful and rhythmic — a natural fit for this reader.",
    },
    {
      id: "close",
      label: "Close English",
      note: "A clause-tracking rendering written for this reader, so the Latin word-stems and psalm line order stay visible against Coverdale's smoother prose.",
    },
  ],
  parts: BOOKS.map(([id, title, [lo, hi]]) => ({
    id,
    title,
    chapters: chaptersIn(lo, hi),
  })),
};
