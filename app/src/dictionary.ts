import gradibusLexicon from "@content/gradibus/lexicon/lexicon.json";
import psalterLexicon from "@content/psalter/lexicon/lexicon.json";
import ruleLexicon from "@content/rule/lexicon/lexicon.json";
import confessionsLexicon from "@content/confessions/lexicon/lexicon.json";
import type { WorkId } from "@content/schema";

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

function buildByKey(payload: LexiconPayload): Map<string, Entry> {
  const byKey = new Map<string, Entry>();
  for (const entry of payload.entries) {
    byKey.set(entry.key, entry);
  }
  return byKey;
}

/**
 * Per-work lexicon registry. Add a work here once content/<work>/lexicon/lexicon.json
 * exists; the lookup below then resolves clicks against that work only, so glosses
 * stay work-specific (e.g. caritas in the psalter vs De gradibus).
 */
const lexicons: Partial<Record<WorkId, LexiconPayload>> = {
  gradibus: gradibusLexicon as unknown as LexiconPayload,
  psalter: psalterLexicon as unknown as LexiconPayload,
  rule: ruleLexicon as unknown as LexiconPayload,
  confessions: confessionsLexicon as unknown as LexiconPayload,
};

const byKeyByWork = new Map<WorkId, Map<string, Entry>>();
for (const [workId, payload] of Object.entries(lexicons)) {
  if (payload) {
    byKeyByWork.set(workId as WorkId, buildByKey(payload));
  }
}

/** Normalise a clicked token to a lexicon key (lowercase, punctuation stripped). */
export function normalise(word: string): string {
  return word
    .trim()
    .toLowerCase()
    .replace(/^[\W_]+|[\W_]+$/g, "");
}

export function lookup(raw: string, workId: WorkId = "gradibus"): Entry | undefined {
  const key = normalise(raw);
  const byKey = byKeyByWork.get(workId);
  return key && byKey ? byKey.get(key) : undefined;
}

/** The preferred short gloss: the curated card first, else Whitaker's first sense. */
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
  return entry.senses?.map((s) => s.gloss).filter(Boolean) ?? [];
}
