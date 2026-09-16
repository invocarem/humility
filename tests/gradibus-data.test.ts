import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { gradibus } from "@content/gradibus/work";
import type { Paragraph, Work } from "@content/schema";
import { parseLatinMd } from "./parse-latin-md";

const LATIN_MD = resolve(process.cwd(), "content/gradibus/latin.md");

/**
 * Three-word openings transcribed from the PL 182 scans in `docs/*_MLT_*.pdf`.
 * These are not copied from latin.md: they exist to check that file.
 *
 * The four PDFs omit cols 939–940 (Retractatio) and 945–946 (mid-§6 through
 * the start of §10), and they print 953–954 twice (MLT_1-4 p.3 and MLT_5_8 p.3).
 */
const OPENINGS: Record<string, string> = {
  // MLT_1-4 p.1, cols 941–942
  pref: "Rogasti me, frater",
  p1: "Locuturus ergo de",
  p2: "Humilitatis vero talis",
  // MLT_1-4 p.2, cols 943–944
  p3: "Hanc itaque legem",
  p4: "Bonus cibus charitas",
  p5: "Primus ergo cibus",
  p6: "Dixi, ut potui",
  // MLT_1-4 p.4, cols 947–948 (945–946 are missing from the scans)
  p11: "Denique ut intelligas",
  p12: "Cum igitur videas",
  p13: "Sed jam ad",
  // MLT_5_8 p.1, cols 949–950
  p14: "Considerare libet, quam",
  p15: "Qui ergo plene",
  p16: "Humiliatus ergo Propheta",
  // MLT_5_8 p.2, cols 951–952
  p17: "Vide quam longe",
  p18: "Jam ad propositum",
  p19: "In his ergo",
  p20: "Interlucet hic mihi",
  // MLT_1-4 p.3 / MLT_5_8 p.3, cols 953–954
  p21: "Dei quippe Filius",
  p22: "Putas, hos gradus",
  p23: "Unde nimirum colligo",
  // MLT_5_8 p.4, cols 955–956
  p24: "Sed quid ego",
  p25: "Et hoc quidem",
  p26: "Libenter igitur et",
  p27: "Est ergo via",
  // MLT_9-12 p.1, cols 957–958
  p28: "Primus itaque superbiae",
  p29: "Duabus tamen ex",
  p30: "Tu quoque, o",
  // MLT_9-12 p.2, cols 959–960
  p31: "Sed et tu",
  p32: "Hoc est enim",
  p33: "Haec, inquam, iniquitas",
  // MLT_9-12 p.3, cols 961–962
  p34: "Sed jam audi",
  p35: "Seraphim namque aliis",
  p36: "O Lucifer, qui",
  p37: "Sic Joseph cum",
  p38: "Sed, quid de",
  // MLT_9-12 p.4, cols 963–964
  p39: "Monachus enim, qui",
  p40: "Proprium est superborum",
  p41: "At postquam vanitas",
  // MLT_13-16 p.1, cols 965–966
  p42: "Turpe est ei",
  p43: "Credit quod audit",
  p44: "Qui enim alios",
  p45: "Multis vero modis",
  p46: "Licet vero genera",
  // MLT_13-16 p.2, cols 967–968
  p47: "Gloriosa res humilitas",
  p48: "Hic nisi eum",
  p49: "Sciendum autem est",
  p50: "Post decimum itaque",
  // MLT_13-16 p.3, cols 969–970
  p51: "At postquam terribili",
  p52: "Pro tali jam",
  p53: "Disce et in",
  p54: "Duo etiam in",
  // MLT_13-16 p.4, cols 971–972
  p55: "Simili etiam forma",
  p56: "Absit autem a",
  p57: "Dicis forte, frater",
};

const MIN_RATIO = 0.5;
const MAX_RATIO = 3;

function norm(s: string): string {
  return s.replace(/\s+/g, " ").trim();
}

/** Fold print vs working-Latin spelling so a 3-word PDF pin can meet latin.md. */
function foldLatin(s: string): string {
  return norm(s)
    .toLowerCase()
    .replaceAll("æ", "ae")
    .replaceAll("j", "i")
    .replaceAll("v", "u")
    .replaceAll(/[,:;!?]/g, "");
}

function words(s: string): number {
  const t = norm(s);
  return t ? t.split(" ").length : 0;
}

function allParagraphs(work: Work): Paragraph[] {
  return work.parts.flatMap((part) => part.chapters.flatMap((ch) => ch.paragraphs));
}

function joinedLatin(p: Paragraph): string {
  return p.segments.map((s) => s.latin).join(" ");
}

function joinedTranslation(p: Paragraph, id: string): string {
  return p.segments.map((s) => s.translations[id] ?? "").join(" ");
}

describe("gradibus data", () => {
  const paragraphs = allParagraphs(gradibus);
  const byId = new Map(paragraphs.map((p) => [p.id, p]));
  const source = parseLatinMd(readFileSync(LATIN_MD, "utf8"));
  const translationIds = gradibus.translations.map((t) => t.id);

  it("has unique paragraph and segment ids, and p1–p57", () => {
    const paraIds = paragraphs.map((p) => p.id);
    expect(new Set(paraIds).size).toBe(paraIds.length);

    const segIds = paragraphs.flatMap((p) => p.segments.map((s) => s.id));
    expect(new Set(segIds).size).toBe(segIds.length);

    for (let n = 1; n <= 57; n++) {
      expect(byId.has(`p${n}`), `missing p${n}`).toBe(true);
    }
    expect(byId.has("pref")).toBe(true);
    for (let n = 1; n <= 4; n++) {
      expect(byId.has(`r${n}`), `missing r${n}`).toBe(true);
    }
  });

  it("gives every segment mills and close", () => {
    for (const p of paragraphs) {
      expect(p.segments.length, p.id).toBeGreaterThan(0);
      for (const s of p.segments) {
        for (const id of translationIds) {
          const text = s.translations[id];
          expect(text, `${s.id} ${id}`).toEqual(expect.any(String));
          expect(norm(text ?? ""), `${s.id} ${id} empty`).not.toBe("");
        }
      }
    }
  });

  it("matches latin.md for every paragraph", () => {
    const workIds = [...byId.keys()].sort();
    const sourceIds = [...source.keys()].sort();
    expect(workIds).toEqual(sourceIds);

    const mismatches: string[] = [];
    for (const [id, latin] of source) {
      const p = byId.get(id);
      if (!p) {
        mismatches.push(`${id}: missing from work`);
        continue;
      }
      const got = norm(joinedLatin(p));
      const want = norm(latin);
      if (got !== want) {
        const i = [...got].findIndex((ch, n) => ch !== want[n]);
        const slice = (s: string) => s.slice(Math.max(0, i - 24), i + 32);
        mismatches.push(`${id} @${i}: work “${slice(got)}” ≠ source “${slice(want)}”`);
      }
    }
    expect(mismatches).toEqual([]);
  });

  it("keeps mills and close in a word-count band of the Latin", () => {
    const failures: string[] = [];
    for (const p of paragraphs) {
      const latinN = words(joinedLatin(p));
      if (latinN === 0) {
        failures.push(`${p.id}: empty latin`);
        continue;
      }
      for (const id of translationIds) {
        const n = words(joinedTranslation(p, id));
        const ratio = n / latinN;
        if (ratio < MIN_RATIO || ratio > MAX_RATIO) {
          failures.push(
            `${p.id} ${id}: ${n} words vs latin ${latinN} (${ratio.toFixed(2)}x)`,
          );
        }
      }
    }
    expect(failures).toEqual([]);
  });

  it("pins three-word openings from the PL scans", () => {
    const mismatches: string[] = [];
    for (const [id, start] of Object.entries(OPENINGS)) {
      const p = byId.get(id);
      if (!p) {
        mismatches.push(`${id}: missing from work`);
        continue;
      }
      const got = foldLatin(joinedLatin(p));
      const want = foldLatin(start);
      if (!got.startsWith(want)) {
        mismatches.push(`${id}: latin.md “${norm(joinedLatin(p)).slice(0, 40)}” ≁ PDF “${start}”`);
      }
    }
    expect(mismatches).toEqual([]);
  });
});
