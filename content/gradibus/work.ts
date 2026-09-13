import type { Work } from "../schema";
import { preface, retractatio } from "./parts/front";
import { chaptersEarly } from "./parts/humility-early";
import { chaptersLater } from "./parts/humility-later";
import { prideChapters } from "./parts/pride";

export const gradibus: Work = {
  id: "gradibus",
  title: "The Steps of Humility and Pride",
  latinTitle: "De gradibus humilitatis et superbiae",
  source:
    "Working Latin in content/latin.md (PL 182 with SBO supplements). Author file 01_steps_of_humility_and_pride.md is left unchanged.",
  edition: "PL 182, coll. 941–972, with lacunae supplied from SBO 3 (Leclercq–Rochais)",
  translations: [
    {
      id: "mills",
      label: "Mills, 1929",
      year: 1929,
      note: "Barton R. V. Mills, The Twelve Degrees of Humility and Pride (SPCK / Macmillan). Public domain in the US. Mills used the Cambridge Select Treatises Latin, which sometimes differs from Migne.",
    },
    {
      id: "close",
      label: "Close English",
      note: "A clause-tracking rendering written for this reader, so Bernard’s order and word-stems stay visible against Mills’s smoother 1929 prose.",
    },
  ],
  parts: [
    {
      id: "front",
      title: "Front",
      chapters: [retractatio, preface],
    },
    {
      id: "humility",
      title: "Part I — Toward truth",
      chapters: [...chaptersEarly, ...chaptersLater],
    },
    {
      id: "pride",
      title: "Part II — Twelve degrees of pride",
      chapters: prideChapters,
    },
  ],
};
