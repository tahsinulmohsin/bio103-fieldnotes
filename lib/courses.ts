// Server-side access to the built course files. Client components receive only the
// lightweight index from here; a lecture's full content is served per lecture by
// app/course-data/[semester]/[module]/route.ts when it is opened.
import fall2025 from "@/data/course-fall2025.json";
import fall2026 from "@/data/course-fall2026.json";
import type { Course, CourseIndex, Module, Semester } from "@/lib/types";

export const courses: Record<Semester, Course> = {
  fall2026: fall2026 as unknown as Course,
  fall2025: fall2025 as unknown as Course,
};

export function courseIndex(course: Course): CourseIndex {
  const { modules, references, ...meta } = course;
  return {
    ...meta,
    modules: modules.map(({ slides, flashcards, quiz, shortAnswers, ...m }) => ({
      ...m,
      slides: slides.map(({ id, number, title, isReferenceOnly, image }) => ({
        id,
        number,
        title,
        isReferenceOnly,
        image,
      })),
      flashcardIds: flashcards.map((c) => c.id),
      terms: flashcards.map((c) => c.term),
      quizCount: quiz.length,
      shortAnswerCount: shortAnswers.length,
    })),
    references: references.map(({ id, title, source }) => ({ id, title, source })),
  };
}

/** A lecture as the browser needs it: no raw extraction text or provenance offsets. */
export function moduleForClient(semester: Semester, id: string): Module | null {
  const found = courses[semester].modules.find((m) => m.id === id);
  if (!found) return null;
  return {
    ...found,
    slides: found.slides.map((s) => {
      const { rawText: _raw, imageSha256: _hash, textExtraction: _how, ...slide } = s as typeof s & {
        rawText?: string;
        imageSha256?: string;
        textExtraction?: string;
      };
      return slide;
    }),
    flashcards: found.flashcards.map(({ id, term, definition, slideId, page }) => ({
      id,
      term,
      definition,
      slideId,
      page,
    })),
  };
}
