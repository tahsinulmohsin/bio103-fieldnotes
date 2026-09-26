export type Semester = "fall2026" | "fall2025";

export type Slide = {
  id: string;
  number: number;
  /** The slide's own heading, or "Slide N" when it has none. */
  title: string;
  /** The slide's own text, re-flowed into bullet items. */
  notes: string[];
  /** Indent level (0–2) per note, when the deck marks sub-bullets. */
  noteLevels?: number[];
  tables?: string[][][];
  image: string;
  width: number;
  height: number;
  isReferenceOnly: boolean;
  ocrText?: string;
  /** Written to explain the slide; labelled as such and never used for practice. */
  explanation?: string;
};
export type Source = {
  file: string;
  url: string;
  /** PDF rendering of a PowerPoint deck, for page links. */
  previewUrl?: string;
  sha256: string;
  kind: string;
  pageCount: number;
};
export type Flashcard = {
  id: string;
  term: string;
  definition: string;
  slideId: string;
  page: number;
};
export type Question = {
  id: string;
  type: "term" | "definition" | "cloze";
  prompt: string;
  /** Slide line shown under the prompt, with the answer blanked. */
  quote?: string;
  options: string[];
  correctIndex: number;
  explanation: string;
  slideId: string;
  page: number;
  sourceQuote: string;
  sourceCardId: string;
};
export type ShortAnswer = {
  id: string;
  type: "compare" | "points" | "define";
  prompt: string;
  /** Model answer, always literal slide text. */
  answer: { columns?: string[]; rows?: string[][]; points?: string[]; text?: string };
  slideId: string;
  page: number;
};
type ModuleBase = {
  id: string;
  number: number;
  title: string;
  lectureLabel: string;
  category: string;
  description: string;
  source: Source;
  cover: string;
};
/** Everything a lecture needs once opened; fetched on demand. */
export type Module = ModuleBase & {
  slides: Slide[];
  flashcards: Flashcard[];
  quiz: Question[];
  shortAnswers: ShortAnswer[];
};
export type SlideSummary = Pick<Slide, "id" | "number" | "title" | "isReferenceOnly" | "image">;
/** What the contents, search and progress screens need; sent with the page. */
export type ModuleSummary = ModuleBase & {
  slides: SlideSummary[];
  flashcardIds: string[];
  /** Flashcard terms, for search. */
  terms: string[];
  quizCount: number;
  shortAnswerCount: number;
};
export type CourseStats = {
  moduleCount: number;
  slideCount: number;
  referencePageCount: number;
  flashcardCount: number;
  quizCount: number;
  explanationCount: number;
  shortAnswerCount: number;
  ocrPageCount: number;
};
export type Course = {
  version: string;
  semester: Semester;
  title: string;
  term: string;
  instructor: string;
  institution: string;
  sourcePolicy: string;
  stats: CourseStats;
  modules: Module[];
  references: Module[];
};
export type CourseIndex = Omit<Course, "modules" | "references"> & {
  modules: ModuleSummary[];
  references: { id: string; title: string; source: Source }[];
};
export type ModuleProgress = {
  /** Slide ids viewed. */
  read: string[];
  /** Card ids marked "Got it". */
  known: string[];
  /** Card ids marked "Again" and not yet recalled since. */
  again: string[];
  /** Multiple-choice question ids answered wrongly and not yet answered right since. */
  missed: string[];
  /** Short-answer ids the student marked as missed. */
  shortMissed: string[];
  bestScore: number | null;
  attempts: number;
  lastSlide: number;
};
export type Progress = {
  version: 1;
  modules: Record<string, ModuleProgress>;
  lastModule: string | null;
};
export const blankModule = (): ModuleProgress => ({
  read: [],
  known: [],
  again: [],
  missed: [],
  shortMissed: [],
  bestScore: null,
  attempts: 0,
  lastSlide: 0,
});
