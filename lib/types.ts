export type Slide = {
  id: string;
  number: number;
  title: string;
  rawText: string;
  paragraphs: string[];
  image: string;
  width: number;
  height: number;
  isReferenceOnly: boolean;
  ocrText?: string;
  polishedExplanation?: string;
  polishedTitle?: string;
};
export type Source = {
  file: string;
  url: string;
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
  prompt: string;
  options: string[];
  correctIndex: number;
  explanation: string;
  slideId: string;
  page: number;
  sourceQuote: string;
};
export type Module = {
  id: string;
  number: number;
  title: string;
  lectureLabel: string;
  category: string;
  description: string;
  source: Source;
  cover: string;
  slides: Slide[];
  flashcards: Flashcard[];
  quiz: Question[];
};
export type Course = {
  version: string;
  title: string;
  term?: string;
  instructor?: string;
  institution?: string;
  department?: string;
  sourcePolicy: string;
  stats: {
    moduleCount: number;
    slideCount: number;
    flashcardCount: number;
    quizCount: number;
    ocrPageCount?: number;
  };
  modules: Module[];
  references: { id: string; title: string; source: Source; slides: Slide[] }[];
};
export type ModuleProgress = {
  read: string[];
  known: string[];
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
  bestScore: null,
  attempts: 0,
  lastSlide: 0,
});
