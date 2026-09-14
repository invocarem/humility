import type { Chapter, Work, WorkId } from "./schema";
import { gradibus } from "./gradibus/work";
import { psalter } from "./psalter/work";
import { rule } from "./rule/work";
import { confessions } from "./confessions/work";

/**
 * The library registry. Add a new work by giving it an `id` in
 * `content/<work>/work.ts` and appending it here. Keep it sorted by roadmap
 * order (gradibus — psalter — rule — confessions — cantica).
 */
export const works: Work[] = [gradibus, psalter, rule, confessions];

export const defaultWorkId: WorkId = "gradibus";

export function getWork(id: WorkId): Work {
  const work = works.find((entry) => entry.id === id);
  if (!work) {
    throw new Error(`Unknown work: ${id}`);
  }
  return work;
}

export function allChapters(work: Work): Chapter[] {
  return work.parts.flatMap((part) => part.chapters);
}

export function findChapter(work: Work, id: string): Chapter | undefined {
  return allChapters(work).find((chapter) => chapter.id === id);
}
