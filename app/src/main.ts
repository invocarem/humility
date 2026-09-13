import { allChapters, defaultWorkId, getWork } from "@content/works";
import type { Chapter, CruxNote, RenderingId, Segment, WorkId } from "@content/schema";
import { glossFor, lemmaFor, lookup, normalise, sensesFor } from "./dictionary";
import "./styles.css";

type Mode = "read" | "study";

const root: HTMLElement =
  document.querySelector("#app") ??
  (() => {
    throw new Error("Missing #app");
  })();

const state = {
  workId: defaultWorkId as WorkId,
  mode: "study" as Mode,
  english: "mills" as RenderingId,
  chapterId: allChapters(getWork(defaultWorkId))[0]?.id ?? "",
  selected: null as string | null,
  query: "",
};

function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

/** Word-token boundary regexp (Latin letters, incl. accented, plus apostrophes). */
const WORD_RE = /([A-Za-z\u00C0-\u024F''\u2019]+)/g;

/** Escape `text`, then wrap each Latin word in a clickable `<span class="w">`. */
function latinTokenHtml(text: string): string {
  return escapeHtml(text).replace(WORD_RE, `<span class="w" data-word="$1">$1</span>`);
}

function activeWork() {
  return getWork(state.workId);
}

function chapters(): Chapter[] {
  return allChapters(activeWork());
}

function currentChapter(): Chapter {
  return chapters().find((chapter) => chapter.id === state.chapterId) ?? chapters()[0];
}

function findSegment(id: string): Segment | undefined {
  for (const chapter of chapters()) {
    for (const paragraph of chapter.paragraphs) {
      for (const segment of paragraph.segments) {
        if (segment.id === id) {
          return segment;
        }
      }
    }
  }
  return undefined;
}

function notesFor(id: string): CruxNote[] {
  return findSegment(id)?.notes ?? [];
}

function segmentHtml(segment: Segment, field: "latin" | "mills" | "close"): string {
  const selected = segment.id === state.selected ? " selected" : "";
  const flag = segment.notes?.length ? `<sup class="note-flag">n</sup>` : "";
  const body = field === "latin" ? latinTokenHtml(segment[field]) : escapeHtml(segment[field]);
  return `<span class="segment${selected}" data-id="${escapeHtml(segment.id)}">${body}${flag}</span> `;
}

function pane(label: string, field: "latin" | "mills" | "close", extraClass: string): string {
  const chapter = currentChapter();
  const blocks = chapter.paragraphs
    .map((paragraph) => {
      const n = paragraph.n ? `<span class="para-n">${escapeHtml(paragraph.n)}</span> ` : "";
      const body = paragraph.segments.map((segment) => segmentHtml(segment, field)).join("");
      return `<p class="paragraph" id="${field}-${escapeHtml(paragraph.id)}">${n}${body}</p>`;
    })
    .join("");

  return `
    <section class="pane ${extraClass}">
      <div class="pane-label">${escapeHtml(label)}</div>
      <article class="chapter-block">
        <h2 class="chapter-title">${escapeHtml(chapter.title)}</h2>
        ${chapter.heading ? `<p class="chapter-heading">${escapeHtml(chapter.heading)}</p>` : ""}
        ${blocks}
      </article>
    </section>
  `;
}

function tocHtml(): string {
  const needle = state.query.trim().toLowerCase();
  return activeWork()
    .parts.map((part) => {
      const links = part.chapters
        .map((chapter) => {
          const hit =
            !needle ||
            chapter.title.toLowerCase().includes(needle) ||
            (chapter.heading ?? "").toLowerCase().includes(needle) ||
            chapter.paragraphs.some((paragraph) =>
              paragraph.segments.some((segment) => segment.latin.toLowerCase().includes(needle)),
            );
          if (!hit) {
            return "";
          }
          const active = chapter.id === state.chapterId ? " active" : "";
          return `<a class="${active}" href="#${escapeHtml(chapter.id)}" data-chapter="${escapeHtml(chapter.id)}">${escapeHtml(chapter.title)}</a>`;
        })
        .join("");
      if (!links) {
        return "";
      }
      return `<div class="part-label">${escapeHtml(part.title)}</div>${links}`;
    })
    .join("");
}

function drawerHtml(): string {
  if (!state.selected) {
    return "";
  }
  const notes = notesFor(state.selected);
  if (!notes.length) {
    return "";
  }
  const items = notes
    .map(
      (note) => `
        <div>
          <div class="kind">${escapeHtml(note.kind)}</div>
          <h3>${escapeHtml(note.title)}</h3>
          <p>${escapeHtml(note.body)}</p>
        </div>
      `,
    )
    .join("");
  return `<aside class="drawer">${items}</aside>`;
}

function dictCardHtml(wordRaw: string): string {
  const key = normalise(wordRaw);
  const entry = lookup(wordRaw);
  if (!entry) {
    return `<div class="dict-empty">No dictionary entry for <em>${escapeHtml(key)}</em>.</div>`;
  }
  const lemma = lemmaFor(entry);
  const pos = entry.edited?.pos ?? entry.senses?.[0]?.pos ?? (entry.pos?.[0] ?? "");
  const curated = entry.edited ? `<span class="curated-tag">curated</span>` : "";
  const gloss = `<p class="dict-gloss">${escapeHtml(glossFor(entry))}</p>`;
  const note = entry.edited?.note ? `<p class="dict-note">${escapeHtml(entry.edited.note)}</p>` : "";
  const extra = sensesFor(entry);
  const more =
    extra.length > 1
      ? `<details class="dict-more"><summary>${extra.length} Whitaker senses</summary>${extra
          .map((s) => `<p>${escapeHtml(s)}</p>`)
          .join("")}</details>`
      : "";
  const count = entry.count != null ? `<div class="dict-count">${escapeHtml(String(entry.count))}× in this text</div>` : "";
  return `
    <div class="dict-head">
      <span class="dict-word">${escapeHtml(entry.key)}</span>
      ${pos ? `<span class="dict-pos">${escapeHtml(pos)}</span>` : ""}
      ${curated}
    </div>
    <div class="dict-lemma">${escapeHtml(lemma)}${count ? ` · ${count}` : ""}</div>
    ${gloss}
    ${note}
    ${more}
  `;
}

function showDict(wordRaw: string, anchor: HTMLElement): void {
  const el = root.querySelector<HTMLElement>("#dict");
  if (!el) {
    return;
  }
  el.innerHTML = dictCardHtml(wordRaw);
  el.hidden = false;
  const margin = 10;
  const rect = anchor.getBoundingClientRect();
  const width = Math.min(360, window.innerWidth - margin * 2);
  let left = Math.max(margin, Math.min(rect.left, window.innerWidth - width - margin));
  let top = rect.bottom + margin;
  const estHeight = el.offsetHeight || 220;
  if (top + estHeight > window.innerHeight - margin) {
    top = Math.max(margin, rect.top - estHeight - margin);
  }
  el.style.width = `${width}px`;
  el.style.left = `${left}px`;
  el.style.top = `${top}px`;
}

function hideDict(): void {
  const el = root.querySelector<HTMLElement>("#dict");
  if (el) {
    el.hidden = true;
  }
}

function readerPanes(): string {
  const englishLabel = state.english === "mills" ? "Mills, 1929" : "Close English";
  if (state.mode === "study") {
    return `${pane("Latin", "latin", "latin")}${pane("Mills, 1929", "mills", "english mills")}${pane("Close English", "close", "english close")}`;
  }
  return `${pane("Latin", "latin", "latin")}${pane(englishLabel, state.english, `english ${state.english}`)}`;
}

function render(): void {
  const readerClass = state.mode === "study" ? "study" : "read";

  root.innerHTML = `
    <div class="app">
      <header class="topbar">
        <div class="brand">
          Bernard reader
          <small>${escapeHtml(activeWork().latinTitle)}</small>
        </div>
        <div class="modes">
          <button data-mode="read" aria-pressed="${state.mode === "read"}">Read</button>
          <button data-mode="study" aria-pressed="${state.mode === "study"}">Study</button>
        </div>
        <div class="english-pick" ${state.mode === "study" ? "hidden" : ""}>
          <button data-english="mills" aria-pressed="${state.english === "mills"}">Mills</button>
          <button data-english="close" aria-pressed="${state.english === "close"}">Close</button>
        </div>
        <label class="search">
          <span>Search Latin</span>
          <input type="search" value="${escapeHtml(state.query)}" placeholder="phrase or word" />
        </label>
        <div class="nav-tools">
          <button data-nav="-1">Previous</button>
          <button data-nav="1">Next</button>
        </div>
      </header>
      <div class="shell">
        <nav class="toc">
          <h2>Contents</h2>
          ${tocHtml()}
        </nav>
        <main class="reader ${readerClass}">
          ${readerPanes()}
        </main>
      </div>
      ${drawerHtml()}
      <aside class="dict" id="dict" hidden></aside>
      <footer class="statusbar">
        Latin is the index. Click a sentence to align the English. Notes open only on a crux.
      </footer>
    </div>
  `;

  bind();
}

function applySelection(id: string | null): void {
  state.selected = id;
  root.querySelectorAll(".segment.selected").forEach((node) => node.classList.remove("selected"));
  if (id) {
    root.querySelectorAll(`.segment[data-id="${CSS.escape(id)}"]`).forEach((node) => {
      node.classList.add("selected");
    });
  }
  const existing = root.querySelector(".drawer");
  const next = drawerHtml();
  if (existing && next) {
    existing.outerHTML = next;
  } else if (existing) {
    existing.remove();
  } else if (next) {
    root.querySelector(".app")?.insertAdjacentHTML("beforeend", next);
  }
}

function shiftChapter(delta: number): void {
  const list = chapters();
  const index = list.findIndex((chapter) => chapter.id === state.chapterId);
  const next = list[index + delta];
  if (next) {
    state.chapterId = next.id;
    state.selected = next.paragraphs[0]?.segments[0]?.id ?? null;
  }
}

function jumpToQuery(): void {
  const needle = state.query.trim().toLowerCase();
  if (!needle) {
    return;
  }
  for (const chapter of chapters()) {
    for (const paragraph of chapter.paragraphs) {
      for (const segment of paragraph.segments) {
        if (segment.latin.toLowerCase().includes(needle)) {
          state.chapterId = chapter.id;
          state.selected = segment.id;
          render();
          document.querySelector(".segment.selected")?.scrollIntoView({ block: "center", behavior: "auto" });
          return;
        }
      }
    }
  }
}

function bind(): void {
  root.querySelectorAll<HTMLButtonElement>("[data-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      state.mode = button.dataset.mode as Mode;
      render();
    });
  });

  root.querySelectorAll<HTMLButtonElement>("[data-english]").forEach((button) => {
    button.addEventListener("click", () => {
      state.english = button.dataset.english as RenderingId;
      render();
    });
  });

  root.querySelectorAll<HTMLButtonElement>("[data-nav]").forEach((button) => {
    button.addEventListener("click", () => {
      shiftChapter(Number(button.dataset.nav));
      render();
    });
  });

  root.querySelectorAll<HTMLAnchorElement>("[data-chapter]").forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      state.chapterId = link.dataset.chapter ?? state.chapterId;
      state.selected = currentChapter().paragraphs[0]?.segments[0]?.id ?? null;
      render();
    });
  });

  root.querySelectorAll<HTMLElement>(".segment").forEach((node) => {
    node.addEventListener("click", () => {
      const id = node.dataset.id ?? null;
      applySelection(id === state.selected ? null : id);
    });
  });

  root.querySelectorAll<HTMLElement>(".w").forEach((node) => {
    node.addEventListener("click", (event) => {
      event.stopPropagation();
      const word = node.dataset.word ?? node.textContent ?? "";
      showDict(word, node);
    });
  });

  const search = root.querySelector<HTMLInputElement>("input[type=search]");
  search?.addEventListener("input", () => {
    state.query = search.value;
    const toc = root.querySelector(".toc");
    if (toc) {
      toc.innerHTML = `<h2>Contents</h2>${tocHtml()}`;
      bindToc();
    }
  });
  search?.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      jumpToQuery();
    }
  });
}

function bindToc(): void {
  root.querySelectorAll<HTMLAnchorElement>("[data-chapter]").forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      state.chapterId = link.dataset.chapter ?? state.chapterId;
      state.selected = currentChapter().paragraphs[0]?.segments[0]?.id ?? null;
      render();
    });
  });
}

document.addEventListener("keydown", (event) => {
  const target = event.target as HTMLElement | null;
  if (target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA")) {
    return;
  }
  if (event.key === "j") {
    shiftChapter(1);
    render();
  }
  if (event.key === "k") {
    shiftChapter(-1);
    render();
  }
  if (event.key === "Escape") {
    applySelection(null);
    hideDict();
  }
});

render();
