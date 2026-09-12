import lexiconData from "@content/lexicon/lexicon.json";

export interface Edited {
  lemma?: string;
  pos?: string;
  gloss: string;
  note?: string;
}

export interface Sense {
  lemma?: string;
  pos?: string;
  gloss: string;
}

export interface Entry {
  key: string;
  form: string;
  query: string;
  count?: number;
  first?: number | string | null;
  pos?: string[];
  senses?: Sense[];
  no_gloss?: boolean;
  curated?: boolean;
  edited?: Edited;
}

interface LexiconPayload {
  entries: Entry[];
}

const payload = lexiconData as unknown as LexiconPayload;
const byKey = new Map<string, Entry>();
for (const entry of payload.entries) {
  byKey.set(entry.key, entry);
}

/** Normalise a clicked token to a lexicon key (lowercase, punctuation stripped). */
export function normalise(word: string): string {
  return word
    .trim()
    .toLowerCase()
    .replace(/^[\W_]+|[\W_]+$/g, "");
}

export function lookup(raw: string): Entry | undefined {
  const key = normalise(raw);
  return key ? byKey.get(key) : undefined;
}

/** The preferred short gloss: the curated Bernard card first, else Whitaker's first sense. */
export function glossFor(entry: Entry): string {
  if (entry.edited?.gloss) {
    return entry.edited.gloss;
  }
  return entry.senses?.[0]?.gloss ?? (entry.no_gloss ? "(no gloss)" : "");
}

/** The preferred lemma: the curated card's lemma, else the first sense's lemma, else the key. */
export function lemmaFor(entry: Entry): string {
  if (entry.edited?.lemma) {
    return entry.edited.lemma;
  }
  return entry.senses?.[0]?.lemma ?? entry.key;
}

/** All distinct(ish) gloss senses as lines; curated note appended last. */
export function sensesFor(entry: Entry): string[] {
  const lines = entry.senses?.map((s) => s.gloss).filter(Boolean) ?? [];
  return lines;
}
