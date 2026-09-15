# Plan — bring the coarse works up to *De gradibus*'s part structure

A companion to [`docs/roadmap.md`](roadmap.md). The roadmap tracks which works
are ingedted and their editorial progress; this file is the working plan for
one cross-cutting change: **giving psalter / rule / confessions the same
structural quality in their Parts as *De gradibus***, without touching
gradibus and without requiring any new translation authoring.

## Locked decisions (scope)

- **`De gradibus` is read-only — the frozen reference and spec.** No change of
  any kind to `content/gradibus/` (not content, not container, not ids). The
  roadmap's "backward compatibility of *De gradibus*" principle is taken
  literally: it is the model other works are measured against, never edited.
- **No `close` column is required for any work.** One public-domain translation
  is fine (Verheyen for the Rule, Pusey for the Confessions). Multiple
  translations already present (psalter's Coverdale + Douay) stay as they are.
  Adding a hand-written `close` voice is **out of scope** for this plan.
- **The change is about Parts structure and headings**, matching gradibus's
  pattern — meaningful part boundaries and titles, and curated per-chapter
  `heading`s — not about translation voices.
- **"Toward gradibus" means structure only (parts grouping + headings).**
  The coarse works keep their `scaffold.ts` + `renderings/*.json` pipeline;
  **no `parts/*.ts` files are created and no content is re-authored.** Matching
  gradibus's part *skeleton* is a `work.ts` `parts:` array edit plus a `titles`
  map for headings — a handful of lines per work. See "Why no parts files"
  below.

This is a plan, not an implementation. **No code change until a step is
started.**

---

## Motivation — the asymmetry today

gradibus's Parts are *editorial*: `front` (Retractatio + Preface), "Part I —
Toward truth", "Part II — Twelve degrees of pride" — boundaries and titles that
mirror Bernard's argument. The other works get their Parts from arithmetic over
chapter numbers:

| Work | Parts today | Nature |
| --- | --- | --- |
| psalter | five psalm-books `[1–41, 42–72, 73–89, 90–106, 107–150]` | mechanical range |
| rule | Prologus, `1–7`, `8–20`, `21–73` | coarse buckets (placeholder-ish titles) |
| confessions | thirteen books `book1..book13` | mechanical per-book |

The psalter's five Liber divisions and the Confessions' thirteen books are
*real* structures, so for those the gap is mainly **curated per-chapter
`heading`s** (gradibus has meaningful `heading:` on many chapters; the coarse
works are auto/empty) and the overall authored feel — where a part boundary
carries an editorial title rather than a bare range.

### Why no `parts/*.ts` files

gradibus has `parts/*.ts` because it is *hand-authored* — those files are where
its curated segments (Mills + `close` + crux notes) live, and `work.ts`'s
`parts:` array only references them. The coarse works already keep their
segments in `scaffold.ts` + `renderings/*.json`; their `work.ts` builds the
`parts:` array by filtering those chapters (`numbered(...)`, `chaptersIn(...)`,
by-book). So replicating gradibus's part *structure* is purely a question of
what that `parts:` array says — **no `parts/*.ts`, no content re-authoring, no
loosening of the regenerate-safe pipeline.** Creating hand-written `parts/*.ts`
would buy gradibus's per-segment authored voice, which is exactly what this plan
explicitly does not chase (see scope).

---

## Steps

### Step 1 — Decide which Part groupings/headings are worth curating

Survey each coarse work and decide, per work, whether the current grouping is
already the right editorial structure (psalter's five Liber, confessions'
thirteen books likely are) or should get editorial titles/boundaries (rule's
buckets are the main candidate — e.g. echoing RB's own thematic stretches).
Also list the chapters that deserve a curated `heading`.

Status: **OPEN** — a review pass over the three works, no code.

Verify:
- [ ] One-line rationale per work for keeping or reshaping each Part, recorded
      in this file or the work's `ingest.json` note.
- [ ] gradibus untouched and still rendering identically as the reference.

### Step 2 — Reshape Parts + headings in the three works only

Edit each coarse work's `work.ts` `parts:` (a single `parts:` array per work —
**no `parts/*.ts` files are created or touched**) so Parts carry editorial
titles and, where justified, tighter boundaries — modeled on gradibus's
`front`/Part I/Part II pattern. Per-chapter `heading`s are curated where Step 1
identified them. Note: headings already flow through the merge's `titles` map
for the Rule (`titles[key] ?? chapter.heading` in `work.ts`, fed from
`renderings/verheyen.json`); psalter/confessions have no `titles` map today,
so curating their headings means adding a per-work `titles` record to the
merge/renderings on their side. Translations are **left exactly as they are**
(single column is fine) — the `titles` change is headings only.

Status: **OPEN**

Verify:
- [ ] `npm run build` (tsc + vite) is green.
- [ ] No regression on *De gradibus* (renders identically).
- [ ] Each reshaped work: TOC shows the new Part titles; chapter nav works;
      sentence alignment, click-a-word, and search unaffected; every
      translation column unchanged.
- [ ] `latin.md` per work is untouched.

### Step 3 (optional, non-required) — Crux notes where a segment genuinely needs one

If a specific segment really demands a note, follow gradibus's
`word`/`syntax`/`theology`/`text` `CruxNote` pattern. This needs a home for
notes on the coarse works' pipeline (they currently hold none). Defer unless a
particular passage forces it.

Status: **OPEN / optional**

Verify:
- [ ] Any notes added key against segment ids and render in the crux drawer
      without affecting the translation columns.

---

## Principles to keep

- `latin.md` per work is authoritative and never written by the app.
- **`De gradibus` is the frozen spec** — read references from it, never write
  to it.
- No new translation authoring: a single public-domain translation per work is
  sufficient. Do not add `close` columns.
- No general dictionary and no Whitaker on every click — per-work closed
  lexicons, curated `overrides.json` (unchanged by this plan).
- Changes are additive to psalter/rule/confessions only; their existing
  translations and lexicons are preserved byte-for-byte.

## Out of scope (explicitly not in this plan)

- Any edit to `content/gradibus/` (content, container, or ids).
- Adding `close` columns.
- Hand-authoring `parts/*.ts` for the coarse works (gradibus-style per-segment
  curation). This plan only reshapes the `parts:` array in each coarse
  `work.ts`; no new `parts/*.ts` files.
- Pipeline-mechanics unification (scaffold derivation, `renderings/` refactor,
  id renames) — set aside; revisit only if the roadmap's work-library work ever
  needs the mechanics shared.
