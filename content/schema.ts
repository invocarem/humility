/** A translation/rendering id. Defined per work via that work's `translations` list. */
export type TranslationId = string;

/** A library work. The id must be unique across the whole repository. */
export type WorkId = "gradibus" | "psalter" | "rule" | "confessions" | "cantica";

export type NoteKind = "word" | "syntax" | "theology" | "text";

export interface CruxNote {
  kind: NoteKind;
  title: string;
  body: string;
}

export interface Segment {
  id: string;
  latin: string;
  /** One rendering per translation. Keys are the work's TranslationId values. */
  translations: Record<TranslationId, string>;
  notes?: CruxNote[];
}

export interface Paragraph {
  id: string;
  n?: string;
  title?: string;
  segments: Segment[];
}

export interface Chapter {
  id: string;
  number?: number;
  title: string;
  heading?: string;
  paragraphs: Paragraph[];
}

export interface Part {
  id: string;
  title: string;
  chapters: Chapter[];
}

export interface TranslationMeta {
  id: TranslationId;
  label: string;
  year?: number;
  note: string;
}

export interface Work {
  id: WorkId;
  title: string;
  latinTitle: string;
  source: string;
  /** Short provenance line for the edition the Latin is taken from. */
  edition?: string;
  translations: TranslationMeta[];
  parts: Part[];
}

export function segment(
  id: string,
  latin: string,
  mills: string,
  close: string,
  notes?: CruxNote[],
): Segment {
  return { id, latin, translations: { mills, close }, ...(notes ? { notes } : {}) };
}

export function paragraph(
  id: string,
  n: string | undefined,
  segments: Segment[],
  title?: string,
): Paragraph {
  return { id, ...(n ? { n } : {}), ...(title ? { title } : {}), segments };
}

export function one(
  id: string,
  n: string | undefined,
  latin: string,
  mills: string,
  close: string,
  notes?: CruxNote[],
  title?: string,
): Paragraph {
  return paragraph(id, n, [segment(`${id}.1`, latin, mills, close, notes)], title);
}
