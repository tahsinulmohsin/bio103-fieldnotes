import {
  blankModule,
  type CourseIndex,
  type ModuleProgress,
  type ModuleSummary,
  type Progress,
  type Semester,
} from "@/lib/types";

export const storageKeys: Record<Semester, string> = {
  fall2026: "bio103-progress-fall2026",
  // Kept from the first version of the app so existing Fall 2025 progress survives.
  fall2025: "bio103-fieldnotes-v1",
};

type SlideList = { slides: { id: string; isReferenceOnly: boolean }[] };

export const fresh = (): Progress => ({ version: 1, modules: {}, lastModule: null });
export const teachingSlides = <T extends SlideList>(m: T) => m.slides.filter((s) => !s.isReferenceOnly);
export const readCount = (m: SlideList, p: ModuleProgress) =>
  teachingSlides(m).filter((s) => p.read.includes(s.id)).length;
export const percentRead = (m: SlideList, p: ModuleProgress) =>
  Math.round((readCount(m, p) / Math.max(1, teachingSlides(m).length)) * 100);
/** Index of the first unread slide, or the last one when everything has been read. */
export const nextUnread = (m: SlideList, p: ModuleProgress) => {
  const i = m.slides.findIndex((s) => !s.isReferenceOnly && !p.read.includes(s.id));
  return i === -1 ? Math.max(0, m.slides.length - 1) : i;
};
/** Items to revisit: cards marked Again, wrong answers, short answers marked missed. */
export const reviewCount = (p: ModuleProgress) => p.again.length + p.missed.length + p.shortMissed.length;

const unique = (values: unknown, allowed?: (id: string) => boolean): string[] =>
  Array.isArray(values)
    ? [...new Set(values.filter((v): v is string => typeof v === "string" && (!allowed || allowed(v))))]
    : [];

/** Read saved progress, dropping anything that no longer matches the course. */
export function restore(course: CourseIndex, storageKey: string): Progress {
  try {
    const raw = typeof window !== "undefined" ? localStorage.getItem(storageKey) : null;
    const saved = raw ? JSON.parse(raw) : null;
    if (saved?.version !== 1 || !saved.modules || typeof saved.modules !== "object") return fresh();
    const modules: Record<string, ModuleProgress> = {};
    for (const m of course.modules as ModuleSummary[]) {
      const p = saved.modules[m.id];
      if (!p || typeof p !== "object") continue;
      const slideIds = new Set(m.slides.map((s) => s.id));
      const cardIds = new Set(m.flashcardIds);
      modules[m.id] = {
        ...blankModule(),
        read: unique(p.read, (id) => slideIds.has(id)),
        known: unique(p.known, (id) => cardIds.has(id)),
        again: unique(p.again, (id) => cardIds.has(id)),
        // Question ids are checked when the lecture's questions load.
        missed: unique(p.missed),
        shortMissed: unique(p.shortMissed),
        bestScore:
          typeof p.bestScore === "number" && Number.isFinite(p.bestScore)
            ? Math.max(0, Math.min(100, p.bestScore))
            : null,
        attempts: Number.isInteger(p.attempts) ? Math.max(0, p.attempts) : 0,
        lastSlide: Number.isInteger(p.lastSlide) ? Math.max(0, Math.min(m.slides.length - 1, p.lastSlide)) : 0,
      };
    }
    return {
      version: 1,
      modules,
      lastModule: course.modules.some((m) => m.id === saved.lastModule) ? saved.lastModule : null,
    };
  } catch {
    return fresh();
  }
}
