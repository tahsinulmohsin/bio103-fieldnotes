"use client";

import { useEffect, useRef, useState } from "react";
import {
  AnimatePresence,
  MotionConfig,
  motion,
  useReducedMotion,
} from "motion/react";
import {
  ArrowUpRight,
  ArrowRight,
  ArrowLeft,
  BookOpen,
  Check,
  CheckCheck,
  ChevronRight,
  Columns2,
  Download,
  Expand,
  FileText,
  GraduationCap,
  Layers3,
  LayoutGrid,
  Leaf,
  LockKeyhole,
  Menu,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  RotateCcw,
  Rows2,
  Search,
  Sparkles,
  Sun,
  Target,
  TrendingUp,
  X,
} from "lucide-react";
import {
  blankModule,
  type Course,
  type Module,
  type ModuleProgress,
  type Progress,
  type Slide,
} from "@/lib/types";

const STORAGE = "bio103-fieldnotes-v1";
const spring = {
  type: "spring" as const,
  stiffness: 420,
  damping: 35,
  mass: 0.7,
};
type Screen = "dashboard" | "library" | "progress" | "sources";
type Mode = "concepts" | "flashcards" | "quiz";
const fresh = (): Progress => ({ version: 1, modules: {}, lastModule: null });
const requiredSlides = (m: Module) =>
  m.slides.filter((s) => !s.isReferenceOnly);
const isUnlocked = (m: Module, p: ModuleProgress) =>
  requiredSlides(m).every((s) => p.read.includes(s.id));
const percent = (m: Module, p: ModuleProgress) =>
  Math.round(
    (requiredSlides(m).filter((s) => p.read.includes(s.id)).length /
      Math.max(1, requiredSlides(m).length)) *
      100,
  );
const number = (n: number) => String(n).padStart(2, "0");

function restore(course: Course, storageKey: string = STORAGE): Progress {
  try {
    const raw = typeof window !== "undefined" ? localStorage.getItem(storageKey) : null;
    const saved = raw ? JSON.parse(raw) : null;
    if (
      saved?.version !== 1 ||
      !saved.modules ||
      typeof saved.modules !== "object"
    )
      return fresh();
    const modules: Record<string, ModuleProgress> = {};
    for (const m of course.modules) {
      const p = saved.modules[m.id];
      if (!p || typeof p !== "object") continue;
      modules[m.id] = {
        read: Array.isArray(p.read)
          ? ([
              ...new Set(
                p.read.filter(
                  (id: unknown) =>
                    typeof id === "string" && m.slides.some((s) => s.id === id),
                ),
              ),
            ] as string[])
          : [],
        known: Array.isArray(p.known)
          ? ([
              ...new Set(
                p.known.filter(
                  (id: unknown) =>
                    typeof id === "string" &&
                    m.flashcards.some((c) => c.id === id),
                ),
              ),
            ] as string[])
          : [],
        bestScore:
          typeof p.bestScore === "number" && Number.isFinite(p.bestScore)
            ? Math.max(0, Math.min(100, p.bestScore))
            : null,
        attempts: Number.isInteger(p.attempts) ? Math.max(0, p.attempts) : 0,
        lastSlide: Number.isInteger(p.lastSlide)
          ? Math.max(0, Math.min(m.slides.length - 1, p.lastSlide))
          : 0,
      };
    }
    return {
      version: 1,
      modules,
      lastModule: course.modules.some((m) => m.id === saved.lastModule)
        ? saved.lastModule
        : null,
    };
  } catch {
    return fresh();
  }
}

export default function StudyApp({
  course: initialCourse,
  courseFall2026,
  courseFall2025,
}: {
  course?: Course;
  courseFall2026?: Course;
  courseFall2025?: Course;
}) {
  const [selectedSemester, setSelectedSemester] = useState<"fall2026" | "fall2025">("fall2026");
  const [screen, setScreen] = useState<Screen>("dashboard");
  const [activeId, setActiveId] = useState<string | null>(null);
  const [progress, setProgress] = useState<Progress>(fresh);
  const [loaded, setLoaded] = useState(false);
  const [storageError, setStorageError] = useState(false);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All topics");
  const [menu, setMenu] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const mainRef = useRef<HTMLElement>(null);
  const menuToggle = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    try {
      const savedSem = localStorage.getItem("bio103-selected-semester");
      if (savedSem === "fall2026" || savedSem === "fall2025") {
        setSelectedSemester(savedSem);
      }
    } catch {}
  }, []);

  const course =
    selectedSemester === "fall2026"
      ? (courseFall2026 || initialCourse!)
      : (courseFall2025 || initialCourse!);

  const storageKey =
    selectedSemester === "fall2026"
      ? "bio103-progress-fall2026"
      : "bio103-fieldnotes-v1";

  const switchSemester = (next: "fall2026" | "fall2025") => {
    setSelectedSemester(next);
    setActiveId(null);
    setCategory("All topics");
    setQuery("");
    try {
      localStorage.setItem("bio103-selected-semester", next);
    } catch {}
    const nextCourse =
      next === "fall2026"
        ? (courseFall2026 || initialCourse!)
        : (courseFall2025 || initialCourse!);
    const nextStorage =
      next === "fall2026" ? "bio103-progress-fall2026" : "bio103-fieldnotes-v1";
    setProgress(restore(nextCourse, nextStorage));
  };

  useEffect(() => {
    const isDark = document.documentElement.classList.contains("dark");
    setTheme(isDark ? "dark" : "light");
  }, []);

  const toggleTheme = () => {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    if (next === "dark") {
      document.documentElement.classList.add("dark");
      document.documentElement.setAttribute("data-theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      document.documentElement.setAttribute("data-theme", "light");
    }
    try {
      localStorage.setItem("bio103-theme", next);
    } catch {}
  };

  useEffect(() => {
    setProgress(restore(course, storageKey));
    setLoaded(true);
  }, [course, storageKey]);

  useEffect(() => {
    if (loaded)
      try {
        localStorage.setItem(storageKey, JSON.stringify(progress));
        setStorageError(false);
      } catch {
        setStorageError(true);
      }
  }, [progress, loaded, storageKey]);
  useEffect(() => {
    if (!menu) return;
    const buttons = Array.from(document.querySelectorAll<HTMLButtonElement>(".sidebar button"));
    buttons[0]?.focus();
    const trap = (event: KeyboardEvent) => {
      if (event.key !== "Tab") return;
      const first = buttons[0], last = buttons[buttons.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    };
    document.addEventListener("keydown", trap);
    return () => { document.removeEventListener("keydown", trap); menuToggle.current?.focus(); };
  }, [menu]);
  useEffect(() => {
    const close = (e: KeyboardEvent) => {
      if (e.key === "Escape") setMenu(false);
    };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, []);
  useEffect(() => {
    const readHash = () => {
      if (location.hash === "#main") return;
      const id = location.hash.replace("#module/", "");
      if (
        location.hash.startsWith("#module/") &&
        course.modules.some((m) => m.id === id)
      ) {
        setActiveId(id);
        setMenu(false);
      } else {
        setActiveId(null);
        const s = location.hash.slice(1);
        if (["dashboard", "library", "progress", "sources"].includes(s))
          setScreen(s as Screen);
      }
    };
    readHash();
    window.addEventListener("hashchange", readHash);
    return () => window.removeEventListener("hashchange", readHash);
  }, [course]);
  const go = (s: Screen) => {
    setScreen(s);
    setActiveId(null);
    setMenu(false);
    setQuery("");
    location.hash = s;
    window.scrollTo(0, 0);
    mainRef.current?.focus();
  };
  const open = (m: Module) => {
    setActiveId(m.id);
    setMenu(false);
    setProgress((p) => ({ ...p, lastModule: m.id }));
    location.hash = `module/${m.id}`;
    window.scrollTo(0, 0);
    mainRef.current?.focus();
  };
  const update = (id: string, fn: (p: ModuleProgress) => ModuleProgress) =>
    setProgress((p) => ({
      ...p,
      lastModule: id,
      modules: { ...p.modules, [id]: fn(p.modules[id] || blankModule()) },
    }));
  const active = course.modules.find((m) => m.id === activeId);
  const completed = course.modules.filter((m) =>
    isUnlocked(m, progress.modules[m.id] || blankModule()),
  ).length;
  const reviewed = course.modules.reduce(
    (n, m) =>
      n +
      requiredSlides(m).filter((s) =>
        (progress.modules[m.id]?.read || []).includes(s.id),
      ).length,
    0,
  );
  const total = course.modules.reduce(
    (n, m) => n + requiredSlides(m).length,
    0,
  );
  const known = Object.values(progress.modules).reduce(
    (n, p) => n + p.known.length,
    0,
  );
  const resume =
    course.modules.find((m) => m.id === progress.lastModule) ||
    course.modules[0];
  const categories = [
    "All topics",
    ...new Set(course.modules.map((m) => m.category)),
  ];
  const filtered = course.modules.filter(
    (m) =>
      (category === "All topics" || m.category === category) &&
      `${m.title} ${m.category} ${m.lectureLabel} ${m.slides.map((s) => s.title).join(" ")}`
        .toLowerCase()
        .includes(query.toLowerCase()),
  );
  const nav = [
    { id: "dashboard" as Screen, label: "Overview", icon: LayoutGrid },
    { id: "library" as Screen, label: "Your course", icon: BookOpen },
    { id: "progress" as Screen, label: "Study progress", icon: TrendingUp },
    { id: "sources" as Screen, label: "Source library", icon: FileText },
  ];
  const downloadProgress = () => {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(
      new Blob([JSON.stringify(progress, null, 2)], {
        type: "application/json",
      }),
    );
    a.download = "bio103-progress.json";
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  };
  return (
    <MotionConfig reducedMotion="user" transition={spring}>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      {menu && (
        <button
          className="sidebar-scrim"
          aria-label="Close navigation"
          onClick={() => setMenu(false)}
        />
      )}
      <aside className={`sidebar ${menu ? "is-open" : ""}`}>
        <button
          className="brand"
          onClick={() => go("dashboard")}
          aria-label="Fieldnotes overview"
        >
          <span className="brand-mark">
            <Leaf size={24} strokeWidth={1.6} />
          </span>
          <span>
            fieldnotes<span className="brand-dot">.</span>
          </span>
        </button>
        <div className="course-label">YOUR STUDY SPACE</div>
        <div className="course-switch">
          <span className="course-badge nsu-course-badge">
            <img
              src="/nsu-logo.svg"
              alt="North South University"
              className="course-nsu-img"
            />
          </span>
          <div>
            <strong>BIO103</strong>
            <span>Biology I · NSU</span>
          </div>
          <GraduationCap size={19} />
        </div>
        <div className="semester-selector" role="tablist" aria-label="Curriculum Semester">
          <button
            type="button"
            className={`semester-pill ${selectedSemester === "fall2026" ? "active" : ""}`}
            onClick={() => switchSemester("fall2026")}
            role="tab"
            aria-selected={selectedSemester === "fall2026"}
            title="Fall 2026: Prof. Dr. Md. Mahbubul Morshed (MBMD)"
          >
            <span className="semester-pill-badge">LATEST</span>
            <span>Fall 2026</span>
          </button>
          <button
            type="button"
            className={`semester-pill ${selectedSemester === "fall2025" ? "active" : ""}`}
            onClick={() => switchSemester("fall2025")}
            role="tab"
            aria-selected={selectedSemester === "fall2025"}
            title="Fall 2025: Dr. Md. Rakibul Islam (MRIS)"
          >
            <span>Fall 2025</span>
          </button>
        </div>
        <nav aria-label="Main navigation">
          {nav.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              className={`nav-item ${screen === id && !active ? "selected" : ""}`}
              onClick={() => go(id)}
              aria-current={screen === id && !active ? "page" : undefined}
            >
              <Icon size={19} />
              <span>{label}</span>
              {id === "library" && (
                <span className="nav-count">{course.modules.length}</span>
              )}
            </button>
          ))}
        </nav>
        <div className="sidebar-note">
          <span className="small-caps">A LITTLE, OFTEN.</span>
          <p>
            Understand it first.
            <br />
            Make it stick next.
          </p>
          <div className="mini-sequence">
            <BookOpen size={15} />
            <span />
            <Layers3 size={15} />
            <span />
            <Target size={15} />
          </div>
        </div>
        <div className="sidebar-bottom">
          <span className="avatar avatar-nsu">
            <img
              src="/nsu-logo.svg"
              alt="North South University"
              className="sidebar-nsu-img"
            />
          </span>
          <div>
            <strong>North South University</strong>
            <span>BIO103 · Lecture collection</span>
          </div>
        </div>
      </aside>
      <div className="app-shell">
        <header className="topbar">
          <div className="breadcrumb">
            <button
              className="mobile-menu icon-button"
              ref={menuToggle}
              aria-expanded={menu}
              aria-label="Open navigation"
              onClick={() => setMenu(true)}
            >
              <Menu size={21} />
            </button>
            <span>My workspace</span>
            <ChevronRight size={14} />
            <strong>
              {active ? active.title : nav.find((n) => n.id === screen)?.label}
            </strong>
          </div>
          <div className="topbar-right">
            <div
              className="top-semester-pill"
              title={`Active curriculum: ${course.title} · ${course.instructor || (selectedSemester === "fall2026" ? "MBMD" : "MRIS")}`}
            >
              <span className="semester-dot" />
              <span>{course.term || (selectedSemester === "fall2026" ? "Fall 2026" : "Fall 2025")} · {selectedSemester === "fall2026" ? "MBMD" : "MRIS"}</span>
            </div>
            <button
              type="button"
              className="theme-toggle-btn"
              onClick={toggleTheme}
              aria-label={
                theme === "dark"
                  ? "Switch to light appearance"
                  : "Switch to dark appearance"
              }
              title={theme === "dark" ? "Light appearance" : "Dark appearance"}
            >
              {theme === "dark" ? (
                <Sun size={16} strokeWidth={2.2} />
              ) : (
                <Moon size={16} strokeWidth={2.2} />
              )}
            </button>
            <div className="top-nsu-badge" title="North South University">
              <img
                src="/nsu-logo.svg"
                alt="North South University"
                className="top-nsu-img"
              />
              <span className="top-nsu-label">NSU</span>
            </div>
          </div>
        </header>
        <main
          id="main"
          ref={mainRef}
          tabIndex={-1}
          className={`main ${active ? "lesson-main" : ""}`}
        >
          {storageError && (
            <p role="status" className="storage-alert">
              Browser storage is unavailable. Progress lasts for this visit;
              export it from Study progress.
            </p>
          )}
          {!loaded ? (
            <div className="loading-state">Opening your study space…</div>
          ) : active ? (
            <LearningModule
              key={active.id}
              module={active}
              progress={progress.modules[active.id] || blankModule()}
              update={(fn) => update(active.id, fn)}
              back={() => go("library")}
            />
          ) : (
            <>
              {screen === "dashboard" && (
                <>
                  <div className="page-eyebrow">
                    BIO103 / BIOLOGY I · {course.term ? course.term.toUpperCase() : "FALL 2026"}
                  </div>
                  <div className="page-heading">
                    <div>
                      <h1>
                        A little curiosity.
                        <br />
                        <em>A clearer understanding.</em>
                      </h1>
                      <p>
                        Your lectures, with room to think. Pick up a concept and
                        make it yours.
                      </p>
                    </div>
                    <div className="semester-note">
                      <img
                        src="/nsu-logo.svg"
                        alt="North South University"
                        className="semester-nsu-img"
                      />
                      <div className="semester-copy">
                        <span>THE LECTURE COLLECTION</span>
                        <strong>North South University</strong>
                        <span>
                          {selectedSemester === "fall2026"
                            ? "Prof. Dr. Md. Mahbubul Morshed · Fall 2026"
                            : "Dr. Md. Rakibul Islam · Fall 2025"}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="dashboard-top">
                    <section className="continue-card">
                      <div className="continue-copy">
                        <span className="small-caps">
                          <span className="live-dot" />
                          {progress.lastModule
                            ? "PICK UP WHERE YOU LEFT OFF"
                            : "A GOOD PLACE TO BEGIN"}
                        </span>
                        <p className="lecture-line">
                          {resume.lectureLabel} <span>•</span> {resume.category}
                        </p>
                        <h2>{resume.title}</h2>
                        <div className="continue-progress">
                          <span>
                            {percent(
                              resume,
                              progress.modules[resume.id] || blankModule(),
                            )}
                            % explored
                          </span>
                          <span>{resume.slides.length} slides</span>
                        </div>
                        <ProgressBar
                          value={percent(
                            resume,
                            progress.modules[resume.id] || blankModule(),
                          )}
                        />
                        <button
                          className="button dark"
                          onClick={() => open(resume)}
                        >
                          {progress.lastModule
                            ? "Continue learning"
                            : "Start exploring"}
                          <ArrowRight size={17} />
                        </button>
                      </div>
                      <div className="continue-art">
                        <img
                          src={resume.cover || resume.slides[0]?.image}
                          alt={`Original lecture visual from ${resume.title}`}
                        />
                        <span className="art-caption">
                          <span /> FROM YOUR LECTURES
                        </span>
                      </div>
                    </section>
                    <section className="pace-card">
                      <div className="card-label">
                        YOUR COURSE, AT A GLANCE
                        <TrendingUp size={17} />
                      </div>
                      <div className="pace-stat">
                        <strong>
                          {completed}
                          <span> / {course.modules.length}</span>
                        </strong>
                        <span>topics explored</span>
                      </div>
                      <ProgressBar
                        value={(completed / course.modules.length) * 100}
                      />
                      <div className="pace-bottom">
                        <div>
                          <strong>{reviewed}</strong>
                          <span>slides reviewed</span>
                        </div>
                        <div>
                          <strong>{known}</strong>
                          <span>cards recalled</span>
                        </div>
                      </div>
                      <button
                        className="text-button"
                        onClick={() => go("progress")}
                      >
                        View your progress
                        <ArrowUpRight size={15} />
                      </button>
                    </section>
                  </div>
                  <div className="section-title">
                    <div>
                      <span className="page-eyebrow">THE LEARNING PATH</span>
                      <h2>Explore your course</h2>
                    </div>
                    <span className="quiet">
                      {course.modules.length} topics · {course.stats.slideCount}{" "}
                      lecture slides
                    </span>
                  </div>
                </>
              )}
              {screen === "library" && (
                <>
                  <div className="page-eyebrow">THE LEARNING PATH</div>
                  <div className="page-heading">
                    <div>
                      <h1>
                        Your course,
                        <br />
                        <em>one concept at a time.</em>
                      </h1>
                      <p>
                        Read the explanation, study the original graphic, then
                        test your recall.
                      </p>
                    </div>
                  </div>
                </>
              )}
              {(screen === "dashboard" || screen === "library") && (
                <>
                  <div className="course-controls">
                    <div className="filters" aria-label="Filter topics">
                      {categories.map((c) => (
                        <button
                          key={c}
                          onClick={() => setCategory(c)}
                          aria-pressed={category === c}
                          className={category === c ? "active" : ""}
                        >
                          {c}
                        </button>
                      ))}
                    </div>
                    <label className="search-field">
                      <Search size={16} />
                      <span className="sr-only">Search course topics</span>
                      <input
                        placeholder="Find a concept…"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                      />
                      {query && (
                        <button
                          aria-label="Clear search"
                          onClick={() => setQuery("")}
                        >
                          <X size={14} />
                        </button>
                      )}
                    </label>
                  </div>
                  <div className="module-grid">
                    {filtered.map((m) => (
                      <ModuleCard
                        key={m.id}
                        module={m}
                        progress={progress.modules[m.id] || blankModule()}
                        onOpen={() => open(m)}
                      />
                    ))}
                  </div>
                  {!filtered.length && (
                    <div className="empty-state">
                      <Search size={28} />
                      <h2>No topics found</h2>
                      <p>Try a lecture title or a different topic filter.</p>
                      <button
                        className="button secondary"
                        onClick={() => {
                          setQuery("");
                          setCategory("All topics");
                        }}
                      >
                        Clear filters
                      </button>
                    </div>
                  )}
                  <div className="learning-footnote">
                    <BookOpen size={19} />
                    <div>
                      <strong>Understanding comes first.</strong>
                      <span>
                        Every topic starts with your lecture explanations.
                        Flashcards and quizzes unlock once you’ve reviewed them.
                      </span>
                    </div>
                    <span className="footnote-tag">
                      LEARN → RECALL → PRACTICE
                    </span>
                  </div>
                </>
              )}
              {screen === "progress" && (
                <>
                  <div className="page-eyebrow">YOUR STUDY RECORD</div>
                  <div className="page-heading">
                    <div>
                      <h1>
                        Small steps.
                        <br />
                        <em>Visible progress.</em>
                      </h1>
                      <p>
                        Saved in this browser. Keep returning to the concepts
                        that need another look.
                      </p>
                    </div>
                    <button
                      className="button secondary"
                      onClick={downloadProgress}
                    >
                      <Download size={16} />
                      Export progress
                    </button>
                  </div>
                  <div className="progress-stats">
                    <Stat
                      label="Slides reviewed"
                      value={`${reviewed} / ${total}`}
                    />
                    <Stat
                      label="Topics unlocked"
                      value={`${completed} / ${course.modules.length}`}
                    />
                    <Stat
                      label="Cards recalled"
                      value={`${known} / ${course.stats.flashcardCount}`}
                    />
                  </div>
                  <div className="progress-table">
                    {course.modules.map((m) => {
                      const p = progress.modules[m.id] || blankModule();
                      return (
                        <button
                          key={m.id}
                          onClick={() => open(m)}
                          className="progress-row"
                        >
                          <span className="row-number">{number(m.number)}</span>
                          <span className="progress-topic">
                            <strong>{m.title}</strong>
                            <span>{m.lectureLabel}</span>
                          </span>
                          <span className="progress-visual">
                            <ProgressBar value={percent(m, p)} />
                            <small>{percent(m, p)}% reviewed</small>
                          </span>
                          <span className="quiz-score">
                            {p.bestScore === null
                              ? "Quiz not taken"
                              : `${p.bestScore}% best quiz`}
                          </span>
                          <ArrowUpRight size={17} />
                        </button>
                      );
                    })}
                  </div>
                  <div className="progress-actions">
                    <p>
                      Progress stays on this device and browser; it does not
                      sync between devices.
                    </p>
                    {!resetting ? (
                      <button
                        className="text-button"
                        onClick={() => setResetting(true)}
                      >
                        Reset progress
                      </button>
                    ) : (
                      <div className="reset-confirm">
                        <span>Clear all saved progress?</span>
                        <button
                          className="text-button"
                          onClick={() => {
                            setProgress(fresh());
                            setResetting(false);
                          }}
                        >
                          Yes, clear progress
                        </button>
                        <button
                          className="text-button"
                          onClick={() => setResetting(false)}
                        >
                          Cancel
                        </button>
                      </div>
                    )}
                  </div>
                </>
              )}
              {screen === "sources" && (
                <>
                  <div className="page-eyebrow">THE ORIGINAL MATERIAL</div>
                  <div className="page-heading">
                    <div>
                      <h1>
                        Always close
                        <br />
                        <em>to the source.</em>
                      </h1>
                      <p>
                        All learning content comes from these local NSU BIO103
                        lecture files.
                      </p>
                    </div>
                  </div>
                  <div className="source-policy">
                    <FileText size={23} />
                    <div>
                      <h2>Your slides set the syllabus.</h2>
                      <p>
                        Explanations preserve slide wording and original
                        graphics. Flashcard answers are exact excerpts; quiz
                        answers link back to their slide. The course outline is
                        a reference, not a practice source.
                      </p>
                    </div>
                  </div>
                  <div className="source-list">
                    {[...course.modules, ...course.references].map((m, i) => (
                      <a
                        key={m.id}
                        href={m.source.url}
                        target="_blank"
                        rel="noreferrer"
                        className="source-row"
                      >
                        <span className="row-number">{number(i + 1)}</span>
                        <FileText size={22} />
                        <span>
                          <strong>{m.source.file}</strong>
                          <small>
                            {m.source.pageCount} pages ·{" "}
                            {m.source.kind.toUpperCase()} · Original source
                          </small>
                        </span>
                        <ArrowUpRight size={18} />
                      </a>
                    ))}
                  </div>
                  <p className="source-honesty">
                    Slide wording is preserved as provided, including its
                    original terminology and spellings. This is a study
                    companion for this lecture collection.
                  </p>
                </>
              )}
              <footer>
                <span>
                  <Leaf size={14} />
                  fieldnotes · BIO103
                </span>
                <span>Made for understanding.</span>
              </footer>
            </>
          )}
        </main>
      </div>
    </MotionConfig>
  );
}

function ProgressBar({ value }: { value: number }) {
  return (
    <div
      className="progress-track"
      role="progressbar"
      aria-valuenow={Math.round(value)}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label="Learning progress"
    >
      <div style={{ width: `${value}%` }} />
    </div>
  );
}
function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="stat">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
function ModuleCard({
  module: m,
  progress: p,
  onOpen,
}: {
  module: Module;
  progress: ModuleProgress;
  onOpen: () => void;
}) {
  const pct = percent(m, p);
  return (
    <motion.button
      layout="position"
      transition={spring}
      onClick={onOpen}
      className={`module-card tone-${(m.number - 1) % 4}`}
      aria-label={`Open ${m.title}`}
    >
      <div className="module-cover">
        <img loading="lazy" src={m.cover || m.slides[0]?.image} alt="" />
        <span className="module-number">{number(m.number)}</span>
        {pct === 100 && (
          <span className="completed-label">
            <Check size={13} />
            Explored
          </span>
        )}
      </div>
      <div className="module-body">
        <span className="module-category">{m.category}</span>
        <h3>
          {m.title}
          <ArrowUpRight size={18} />
        </h3>
        <p>
          {m.lectureLabel} <span>·</span> {m.slides.length} slides
        </p>
        <div className="module-bottom">
          <span>{pct > 0 ? `${pct}% explored` : "Ready to explore"}</span>
          <span>{m.flashcards.length} recall cards</span>
        </div>
        <ProgressBar value={pct} />
      </div>
    </motion.button>
  );
}

function cleanMathSymbols(text: string): string {
  return text
    .replace(/\$4\^3\s*=\s*64\$/g, "4³ = 64")
    .replace(/\$(\w+)\^(\w+)\$/g, "$1^$2")
    .replace(/4\^3/g, "4³")
    .replace(/5'/g, "5′")
    .replace(/3'/g, "3′")
    .replace(/\$5'\$/g, "5′")
    .replace(/\$3'\$/g, "3′")
    .replace(/\$CO_2\$/g, "CO₂")
    .replace(/CO_2/g, "CO₂")
    .replace(/\$O_2\$/g, "O₂")
    .replace(/O_2/g, "O₂")
    .replace(/\$Na\^\+\$/g, "Na⁺")
    .replace(/\$K\^\+\$/g, "K⁺")
    .replace(/\\rightarrow/g, "→")
    .replace(/\\approx/g, "≈")
    .replace(/\\ge/g, "≥")
    .replace(/\\le/g, "≤")
    .replace(/\\Delta G/g, "ΔG")
    .replace(/\\mu m/g, "µm")
    .replace(/\\circ\\text\{C\}/g, "°C")
    .replace(/\\circ\\text\{F\}/g, "°F")
    .replace(/\$([^\$]+)\$/g, "$1");
}

function renderInline(rawText: string): React.ReactNode {
  const text = cleanMathSymbols(rawText);
  const tokens: React.ReactNode[] = [];
  const regex = /(\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`)/g;
  let lastIdx = 0;
  let match: RegExpExecArray | null;
  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIdx) {
      tokens.push(text.slice(lastIdx, match.index));
    }
    if (match[2]) {
      tokens.push(
        <strong key={match.index} className="polished-strong">
          {match[2]}
        </strong>
      );
    } else if (match[3]) {
      tokens.push(<em key={match.index}>{match[3]}</em>);
    } else if (match[4]) {
      tokens.push(
        <code key={match.index} className="polished-code">
          {match[4]}
        </code>
      );
    }
    lastIdx = regex.lastIndex;
  }
  if (lastIdx < text.length) {
    tokens.push(text.slice(lastIdx));
  }
  return tokens.length ? tokens : text;
}

function renderLinesBlock(lines: string[]) {
  const elements: React.ReactNode[] = [];
  let currentTopBullets: { text: string; subBullets: string[] }[] = [];
  let currentPara: string[] = [];

  const flushPara = () => {
    if (currentPara.length) {
      elements.push(
        <p key={`p-${elements.length}`} className="polished-p">
          {renderInline(currentPara.join(" "))}
        </p>
      );
      currentPara = [];
    }
  };

  const flushBullets = () => {
    if (currentTopBullets.length) {
      elements.push(
        <ul key={`ul-${elements.length}`} className="polished-list">
          {currentTopBullets.map((item, idx) => (
            <li key={idx}>
              <div>{renderInline(item.text)}</div>
              {item.subBullets.length > 0 && (
                <ul className="polished-sublist">
                  {item.subBullets.map((sub, sIdx) => (
                    <li key={sIdx}>{renderInline(sub)}</li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ul>
      );
      currentTopBullets = [];
    }
  };

  for (const rawLine of lines) {
    const isSubBullet = /^\s{2,}[-*•]\s+/.test(rawLine);
    const isTopBullet = /^\s*[-*•]\s+/.test(rawLine);
    const isNumbered = /^\s*\d+\.\s+/.test(rawLine);

    if (isSubBullet && currentTopBullets.length > 0) {
      const cleaned = rawLine.replace(/^\s+[-*•]\s+/, "");
      currentTopBullets[currentTopBullets.length - 1].subBullets.push(cleaned);
    } else if (isTopBullet) {
      flushPara();
      const cleaned = rawLine.replace(/^\s*[-*•]\s+/, "");
      currentTopBullets.push({ text: cleaned, subBullets: [] });
    } else if (isNumbered) {
      flushPara();
      flushBullets();
      const cleaned = rawLine.replace(/^\s*\d+\.\s+/, "");
      elements.push(
        <ol key={`num-${elements.length}`} className="polished-numbered">
          <li>{renderInline(cleaned)}</li>
        </ol>
      );
    } else {
      flushBullets();
      currentPara.push(rawLine.trim());
    }
  }
  flushPara();
  flushBullets();

  return <>{elements}</>;
}

function FormattedNote({ text }: { text: string }) {
  const blocks = text.trim().split(/\n\n+/);
  return (
    <div className="polished-note-content">
      {blocks.map((block, bIdx) => {
        const rawLines = block.split("\n").filter((l) => l.trim().length > 0);
        if (!rawLines.length) return null;

        if (rawLines[0].trim().startsWith("### ")) {
          const headingText = rawLines[0].trim().replace(/^###\s+/, "");
          const remainingLines = rawLines.slice(1);
          return (
            <div key={bIdx} className="polished-section">
              <h3 className="polished-h3">{renderInline(headingText)}</h3>
              {remainingLines.length > 0 && renderLinesBlock(remainingLines)}
            </div>
          );
        }

        if (rawLines[0].startsWith("> ")) {
          const calloutText = rawLines
            .map((l) => l.replace(/^>\s*/, ""))
            .join(" ");
          return (
            <blockquote key={bIdx} className="polished-callout">
              {renderInline(calloutText)}
            </blockquote>
          );
        }

        return <div key={bIdx}>{renderLinesBlock(rawLines)}</div>;
      })}
    </div>
  );
}

function LearningModule({
  module: m,
  progress: p,
  update,
  back,
}: {
  module: Module;
  progress: ModuleProgress;
  update: (fn: (p: ModuleProgress) => ModuleProgress) => void;
  back: () => void;
}) {
  const [mode, setMode] = useState<Mode>("concepts");
  const [index, setIndex] = useState(p.lastSlide || 0);
  const [finished, setFinished] = useState(false);
  const [outline, setOutline] = useState(false);
  const [showOutline, setShowOutline] = useState(true);
  const [layoutMode, setLayoutMode] = useState<"split" | "stacked">("split");
  const [zoom, setZoom] = useState<Slide | null>(null);
  const [noteView, setNoteView] = useState<"polished" | "source">("polished");
  const dialog = useRef<HTMLDialogElement>(null);
  const heading = useRef<HTMLHeadingElement>(null);
  const reduced = useReducedMotion();
  const unlocked = isUnlocked(m, p);
  const slide = m.slides[index];

  useEffect(() => {
    try {
      const savedLayout = localStorage.getItem("bio103-lesson-layout");
      if (savedLayout === "split" || savedLayout === "stacked") {
        setLayoutMode(savedLayout);
      }
      const savedOutline = localStorage.getItem("bio103-outline-open");
      if (savedOutline !== null) {
        setShowOutline(savedOutline === "true");
      } else if (typeof window !== "undefined" && window.innerWidth < 1200) {
        setShowOutline(false);
      }
    } catch {}
  }, []);

  const changeLayoutMode = (nextMode: "split" | "stacked") => {
    setLayoutMode(nextMode);
    try {
      localStorage.setItem("bio103-lesson-layout", nextMode);
    } catch {}
  };

  const toggleOutline = () => {
    setShowOutline((prev) => {
      const next = !prev;
      try {
        localStorage.setItem("bio103-outline-open", String(next));
      } catch {}
      return next;
    });
  };

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [m.id]);

  useEffect(() => {
    if (zoom) dialog.current?.showModal();
    else dialog.current?.close();
  }, [zoom]);

  const select = (i: number) => {
    setIndex(i);
    setFinished(false);
    setOutline(false);
    update((old) => ({ ...old, lastSlide: i }));
    heading.current?.focus();
  };

  const advance = () => {
    update((old) => ({
      ...old,
      read: [...new Set([...old.read, slide.id])],
      lastSlide: Math.min(index + 1, m.slides.length - 1),
    }));
    if (index < m.slides.length - 1) {
      setIndex(index + 1);
      heading.current?.focus();
    } else setFinished(true);
  };

  useEffect(() => {
    if (mode !== "concepts" || zoom) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      if (e.key === "ArrowRight") {
        advance();
      } else if (e.key === "ArrowLeft" && index > 0) {
        select(index - 1);
      }
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [mode, zoom, index, m.slides.length]);
  return (
    <>
      <button onClick={back} className="back-link">
        <ArrowLeft size={15} />
        Back to your course
      </button>
      <div className="lesson-heading">
        <div>
          <span className="page-eyebrow">
            {m.lectureLabel} / {m.category}
          </span>
          <h1>{m.title}</h1>
        </div>
        <span className="lesson-progress-label">
          {p.read.length} / {m.slides.length} slides reviewed
        </span>
      </div>
      <div className="lesson-tabs" aria-label="Learning stages">
        {(
          [
            { id: "concepts", label: "Understand", icon: BookOpen },
            { id: "flashcards", label: "Recall", icon: Layers3 },
            { id: "quiz", label: "Practice", icon: Target },
          ] as const
        ).map(({ id, label, icon: Icon }, i) => (
          <button
            key={id}
            onClick={() => setMode(id)}
            disabled={id !== "concepts" && !unlocked}
            aria-current={mode === id ? "step" : undefined}
            title={
              id !== "concepts" && !unlocked
                ? "Review every explanation to unlock practice"
                : undefined
            }
            className={mode === id ? "active" : ""}
          >
            {mode === id && (
              <motion.span
                className="active-tab"
                layoutId="lesson-tab"
                transition={spring}
              />
            )}
            <span className="tab-content">
              <span className="step-number">0{i + 1}</span>
              <Icon size={17} />
              {label}
              {id !== "concepts" && !unlocked && <LockKeyhole size={13} />}
            </span>
          </button>
        ))}
      </div>
      {mode === "concepts" && (
        <div className={`lesson-layout ${showOutline ? "with-outline" : "outline-collapsed"}`}>
          {showOutline && (
            <aside className={`lesson-outline ${outline ? "expanded" : ""}`}>
              <button
                className="outline-toggle"
                onClick={() => setOutline(!outline)}
                aria-expanded={outline}
              >
                IN THIS TOPIC <Menu size={16} />
              </button>
              <div className="outline-content">
                <div className="outline-title">
                  IN THIS TOPIC <span>{m.slides.length}</span>
                </div>
                <div className="outline-list">
                  {m.slides.map((s, i) => (
                    <button
                      className={index === i ? "current" : ""}
                      key={s.id}
                      onClick={() => select(i)}
                      aria-current={index === i ? "step" : undefined}
                    >
                      <span
                        className={`slide-num ${p.read.includes(s.id) ? "done" : ""}`}
                      >
                        {p.read.includes(s.id) ? (
                          <Check size={12} />
                        ) : (
                          number(i + 1)
                        )}
                      </span>
                      <span>
                        {s.polishedTitle || s.title || `Slide ${s.number}`}
                      </span>
                    </button>
                  ))}
                </div>
                <div className="outline-footer">
                  <ProgressBar value={percent(m, p)} />
                  <span>
                    {unlocked
                      ? "Recall & practice unlocked"
                      : `${requiredSlides(m).filter((s) => !p.read.includes(s.id)).length} explanations until practice`}
                  </span>
                </div>
              </div>
            </aside>
          )}
          <section className={`explanation-panel ${layoutMode === "split" ? "is-split-panel" : "is-stacked-panel"}`}>
            {finished && unlocked ? (
              <div className="unlock-state">
                <span className="unlock-icon">
                  <CheckCheck size={31} />
                </span>
                <span className="page-eyebrow">EXPLANATIONS COMPLETE</span>
                <h2>
                  You’ve made the connections.
                  <br />
                  <em>Now make them stick.</em>
                </h2>
                <p>
                  You’ve reviewed this topic’s lecture material. Your recall
                  cards and practice questions are ready.
                </p>
                <button
                  className="button dark"
                  onClick={() => setMode("flashcards")}
                >
                  Start active recall
                  <ArrowRight size={17} />
                </button>
                <button
                  className="text-button"
                  onClick={() => {
                    setFinished(false);
                    setIndex(0);
                  }}
                >
                  Revisit the explanations
                </button>
              </div>
            ) : (
              <>
                <div className="explanation-topline">
                  <div className="topline-meta-group">
                    <button
                      type="button"
                      className={`outline-toggle-pill ${showOutline ? "active" : ""}`}
                      onClick={toggleOutline}
                      title={showOutline ? "Hide topic outline to widen reading area" : "Show topic outline"}
                    >
                      {showOutline ? <PanelLeftClose size={13} /> : <PanelLeftOpen size={13} />}
                      <span>{showOutline ? "Hide Topics" : "Show Topics"}</span>
                    </button>
                    <span className="small-caps">
                      EXPLANATION {number(index + 1)} / {number(m.slides.length)}
                    </span>
                  </div>

                  <div className="topline-controls-group">
                    <div className="layout-toggle-pills" role="tablist" aria-label="Layout view mode">
                      <button
                        type="button"
                        className={`layout-pill ${layoutMode === "split" ? "active" : ""}`}
                        onClick={() => changeLayoutMode("split")}
                        title="Side-by-side: view slide and explanation together"
                        aria-selected={layoutMode === "split"}
                      >
                        <Columns2 size={13} />
                        <span>Side-by-side</span>
                      </button>
                      <button
                        type="button"
                        className={`layout-pill ${layoutMode === "stacked" ? "active" : ""}`}
                        onClick={() => changeLayoutMode("stacked")}
                        title="Stacked: traditional single column view"
                        aria-selected={layoutMode === "stacked"}
                      >
                        <Rows2 size={13} />
                        <span>Stacked</span>
                      </button>
                    </div>

                    <a
                      href={`${m.source.url}${m.source.kind === "pdf" ? `#page=${slide.number}` : ""}`}
                      target="_blank"
                      rel="noreferrer"
                      className="source-slide-link"
                    >
                      Source slide {slide.number}
                      <ArrowUpRight size={14} />
                    </a>
                  </div>
                </div>

                <div className="explanation-view-bar">
                  <div className="view-toggle-pills" role="tablist" aria-label="Explanation view mode">
                    <button
                      type="button"
                      className={`view-pill ${noteView === "polished" ? "active" : ""}`}
                      onClick={() => setNoteView("polished")}
                      role="tab"
                      aria-selected={noteView === "polished"}
                    >
                      <Sparkles size={13} />
                      <span>Polished Note</span>
                    </button>
                    <button
                      type="button"
                      className={`view-pill ${noteView === "source" ? "active" : ""}`}
                      onClick={() => setNoteView("source")}
                      role="tab"
                      aria-selected={noteView === "source"}
                    >
                      <FileText size={13} />
                      <span>Original Slide Text</span>
                    </button>
                  </div>
                  {noteView === "polished" && (
                    <span className="view-note-caption">
                      ✨ AI-polished pedagogical synthesis · Grounded in slide {slide.number}
                    </span>
                  )}
                </div>

                <AnimatePresence mode="wait" initial={false}>
                  <motion.div
                    key={slide.id}
                    initial={{
                      opacity: 0,
                      transform: reduced ? "none" : "translateY(5px)",
                    }}
                    animate={{ opacity: 1, transform: "none" }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.14 }}
                  >
                    <div className={`lesson-content-layout ${layoutMode === "split" ? "layout-split" : "layout-stacked"}`}>
                      <div className="stage-visual-col">
                        <figure className="slide-figure">
                          <button
                            className="slide-image-button"
                            onClick={() => setZoom(slide)}
                            aria-label={`Enlarge original slide ${slide.number}`}
                          >
                            <img
                              src={slide.image}
                              alt={`Original slide ${slide.number}: ${slide.title}. Its extracted text appears in the explanation.`}
                            />
                            <span className="image-expand">
                              <Expand size={14} />
                              Enlarge slide
                            </span>
                          </button>
                          <figcaption>
                            <span>THE ORIGINAL LECTURE VISUAL</span>
                            <span>
                              {m.lectureLabel} · Slide {slide.number}
                            </span>
                          </figcaption>
                        </figure>
                      </div>

                      <div className="stage-explanation-col">
                        <h2 ref={heading} tabIndex={-1} className="concept-title">
                          {noteView === "polished" && slide.polishedTitle
                            ? slide.polishedTitle
                            : slide.title || `Slide ${slide.number}`}
                        </h2>
                        <div className="source-copy">
                          {noteView === "polished" && slide.polishedExplanation ? (
                            <FormattedNote text={slide.polishedExplanation} />
                          ) : slide.paragraphs.length ? (
                            slide.paragraphs.map((t, i) => <p key={i}>{t}</p>)
                          ) : (
                            <p className="quiet">
                              This slide explains the concept through its original
                              visual. Study the figure beside.
                            </p>
                          )}
                        </div>
                        {slide.ocrText && (
                          <details className="ocr-disclosure">
                            <summary>Text recognized from the slide image</summary>
                            <p className="ocr-notice">
                              Automatically read from the original image. Small labels
                              may be misread; compare with the slide. Practice uses
                              verified source text.
                            </p>
                            <p>{slide.ocrText}</p>
                          </details>
                        )}
                      </div>
                    </div>
                  </motion.div>
                </AnimatePresence>
                <div className="explanation-actions">
                  <button
                    className="button secondary"
                    disabled={index === 0}
                    onClick={() => select(index - 1)}
                  >
                    <ArrowLeft size={16} />
                    Previous
                  </button>
                  <span>
                    {p.read.includes(slide.id) ? (
                      <>
                        <Check size={14} />
                        Reviewed
                      </>
                    ) : (
                      "Take your time. Then move forward."
                    )}
                  </span>
                  <button className="button dark" onClick={advance}>
                    {index === m.slides.length - 1
                      ? "Finish explanations"
                      : "Mark reviewed & continue"}
                    <ArrowRight size={16} />
                  </button>
                </div>
                {!unlocked && (
                  <p className="lock-note">
                    <LockKeyhole size={13} />
                    Review each explanation to unlock recall and practice.
                  </p>
                )}
                {finished && !unlocked && (
                  <div className="inline-note">
                    A few explanations are still unread.{" "}
                    <button
                      onClick={() =>
                        select(
                          m.slides.findIndex(
                            (s) => !s.isReferenceOnly && !p.read.includes(s.id),
                          ),
                        )
                      }
                    >
                      Continue from the first unread slide
                      <ArrowRight size={14} />
                    </button>
                  </div>
                )}
              </>
            )}
          </section>
        </div>
      )}
      {mode === "flashcards" && unlocked && (
        <Flashcards
          module={m}
          progress={p}
          update={update}
          practice={() => setMode("quiz")}
          source={(page) => {
            select(m.slides.findIndex((s) => s.number === page));
            setMode("concepts");
          }}
        />
      )}
      {mode === "quiz" && unlocked && (
        <Quiz
          module={m}
          progress={p}
          update={update}
          source={(page) => {
            select(m.slides.findIndex((s) => s.number === page));
            setMode("concepts");
          }}
        />
      )}
      <dialog
        ref={dialog}
        className="image-dialog"
        onCancel={() => setZoom(null)}
        onClick={(e) => {
          if (e.target === e.currentTarget) setZoom(null);
        }}
        aria-label="Original lecture slide"
      >
        <div className="dialog-top">
          <span>
            {zoom?.title} · Slide {zoom?.number}
          </span>
          <button
            className="icon-button"
            aria-label="Close slide viewer"
            onClick={() => setZoom(null)}
          >
            <X size={22} />
          </button>
        </div>
        {zoom && (
          <img
            src={zoom.image}
            alt={`Full original slide ${zoom.number}: ${zoom.title}`}
          />
        )}
      </dialog>
    </>
  );
}

function Flashcards({
  module: m,
  progress: p,
  update,
  practice,
  source,
}: {
  module: Module;
  progress: ModuleProgress;
  update: (fn: (p: ModuleProgress) => ModuleProgress) => void;
  practice: () => void;
  source: (page: number) => void;
}) {
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [done, setDone] = useState(false);
  const [keyboard, setKeyboard] = useState(false);
  const reduced = useReducedMotion();
  const card = m.flashcards[index];
  const rate = (known: boolean) => {
    update((old) => ({
      ...old,
      known: known
        ? [...new Set([...old.known, card.id])]
        : old.known.filter((id) => id !== card.id),
    }));
    if (index === m.flashcards.length - 1) setDone(true);
    else {
      setIndex(index + 1);
      setFlipped(false);
    }
  };
  if (!card)
    return (
      <div className="practice-empty">
        <h2>No unambiguous definition pairs in this topic.</h2>
        <p>The original lecture explanations are available to review.</p>
        <button className="button dark" onClick={practice}>
          Continue to practice
          <ArrowRight size={16} />
        </button>
      </div>
    );
  return (
    <section className="recall-section">
      <div className="practice-intro">
        <span className="page-eyebrow">ACTIVE RECALL</span>
        <h2>
          {done
            ? "One more layer of understanding."
            : "Bring the idea to mind."}
        </h2>
        <p>
          {done
            ? "You’ve worked through this deck. Revisit it anytime, or try the practice questions."
            : "Think of the definition, then turn the card. The answer uses your slide’s exact wording."}
        </p>
      </div>
      {done ? (
        <div className="deck-finished">
          <CheckCheck size={38} />
          <strong>
            {p.known.length} / {m.flashcards.length}
          </strong>
          <span>cards marked as recalled</span>
          <div>
            <button
              className="button secondary"
              onClick={() => {
                setIndex(0);
                setFlipped(false);
                setDone(false);
              }}
            >
              <RotateCcw size={16} />
              Review deck again
            </button>
            <button className="button dark" onClick={practice}>
              Try practice
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      ) : (
        <>
          <div className="recall-meta">
            <span>
              CARD {number(index + 1)} OF {number(m.flashcards.length)}
            </span>
            <span>
              {p.known.includes(card.id)
                ? "Previously recalled"
                : "Exact words. Stronger recall."}
            </span>
          </div>
          <div className="flip-scene">
            <motion.button
              key={card.id}
              className={`flashcard ${flipped ? "flipped" : ""}`}
              animate={{ rotateY: flipped && !reduced ? 180 : 0 }}
              transition={keyboard || reduced ? { duration: 0 } : spring}
              onClick={(e) => {
                setKeyboard(e.detail === 0);
                setFlipped(!flipped);
              }}
              aria-label={
                flipped
                  ? `Definition: ${card.definition}. Turn to term.`
                  : `${card.term}. Reveal definition.`
              }
            >
              <span
                className="flashcard-face flashcard-front"
                aria-hidden={flipped}
                style={
                  reduced
                    ? { visibility: flipped ? "hidden" : "visible" }
                    : undefined
                }
              >
                <span className="small-caps">THE CONCEPT</span>
                <strong>{card.term}</strong>
                <span className="flip-hint">
                  <RotateCcw size={14} />
                  Click or press Enter to reveal
                </span>
              </span>
              <span
                className="flashcard-face flashcard-back"
                aria-hidden={!flipped}
                style={
                  reduced
                    ? {
                        transform: "none",
                        visibility: flipped ? "visible" : "hidden",
                      }
                    : undefined
                }
              >
                <span className="small-caps">FROM YOUR SLIDE</span>
                <span className="definition">{card.definition}</span>
                <span className="flip-hint">
                  {m.lectureLabel} · Slide {card.page}
                </span>
              </span>
            </motion.button>
          </div>
          <div className="recall-actions">
            <button
              className="button secondary"
              disabled={!flipped}
              onClick={() => rate(false)}
            >
              <RotateCcw size={16} />
              Needs another look
            </button>
            <button
              className="button dark"
              disabled={!flipped}
              onClick={() => rate(true)}
            >
              <Check size={16} />I recalled it
            </button>
          </div>
          <div className="recall-navigation">
            <button
              className="text-button"
              disabled={index === 0}
              onClick={() => {
                setIndex(index - 1);
                setFlipped(false);
              }}
            >
              <ArrowLeft size={15} />
              Previous card
            </button>
            <button className="text-button" onClick={() => source(card.page)}>
              Revisit source slide {card.page}
              <ArrowUpRight size={14} />
            </button>
          </div>
        </>
      )}
    </section>
  );
}

function Quiz({
  module: m,
  progress: p,
  update,
  source,
}: {
  module: Module;
  progress: ModuleProgress;
  update: (fn: (p: ModuleProgress) => ModuleProgress) => void;
  source: (page: number) => void;
}) {
  const availableSizes = [
    10,
    25,
    ...(m.quiz.length >= 50 ? [50] : []),
    m.quiz.length,
  ].filter((n, idx, arr) => n <= m.quiz.length && arr.indexOf(n) === idx);

  const [sessionSize, setSessionSize] = useState<number>(() =>
    Math.min(10, m.quiz.length),
  );
  const makeQuestions = (count = sessionSize) => {
    const shuffled = [...m.quiz];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled.slice(0, Math.min(count, m.quiz.length));
  };
  const [questions, setQuestions] = useState(() => makeQuestions(sessionSize));
  const [index, setIndex] = useState(0);
  const [answer, setAnswer] = useState<number | null>(null);
  const [checked, setChecked] = useState(false);
  const [correct, setCorrect] = useState(0);
  const [done, setDone] = useState(false);
  const question = questions[index];
  const check = () => {
    if (answer === null || checked) return;
    setChecked(true);
    if (answer === question.correctIndex) setCorrect((c) => c + 1);
  };
  const next = () => {
    if (index === questions.length - 1) {
      const score = Math.round((correct / questions.length) * 100);
      update((old) => ({
        ...old,
        bestScore: Math.max(old.bestScore ?? 0, score),
        attempts: old.attempts + 1,
      }));
      setDone(true);
    } else {
      setIndex(index + 1);
      setAnswer(null);
      setChecked(false);
    }
  };
  if (!question)
    return (
      <div className="practice-empty">
        <h2>No source-safe questions for this topic.</h2>
        <p>Use the original explanations and recall cards to review.</p>
      </div>
    );
  return (
    <section className="quiz-section">
      <div className="practice-intro">
        <span className="page-eyebrow">A QUICK KNOWLEDGE CHECK</span>
        <h2>
          {done
            ? "A clearer picture of what you know."
            : "Let’s see what stayed with you."}
        </h2>
        <p>
          {done
            ? "Use the explanations to revisit anything that felt uncertain."
            : `Practicing ${questions.length} questions drawn strictly from this lecture.`}
        </p>
        {availableSizes.length > 1 && !done && index === 0 && !checked && (
          <div
            className="quiz-size-toggle"
            role="group"
            aria-label="Session length"
          >
            {availableSizes.map((sz) => (
              <button
                key={sz}
                type="button"
                className={`size-btn ${sessionSize === sz ? "active" : ""}`}
                onClick={() => {
                  setSessionSize(sz);
                  setQuestions(makeQuestions(sz));
                  setIndex(0);
                  setAnswer(null);
                  setChecked(false);
                  setCorrect(0);
                }}
              >
                {sz === m.quiz.length ? `Full Deck (${sz})` : `${sz} Questions`}
              </button>
            ))}
          </div>
        )}
      </div>
      {done ? (
        <div className="quiz-result">
          <span className="result-icon">
            <Target size={30} />
          </span>
          <strong>
            {correct}
            <span> / {questions.length}</span>
          </strong>
          <h3>
            {correct === questions.length
              ? "Everything connected."
              : "A useful step forward."}
          </h3>
          <p>
            {Math.round((correct / questions.length) * 100)}% this round ·{" "}
            {p.bestScore}% best score
          </p>
          <div className="quiz-result-actions">
            <button
              className="button dark"
              onClick={() => {
                setQuestions(makeQuestions(sessionSize));
                setIndex(0);
                setAnswer(null);
                setChecked(false);
                setCorrect(0);
                setDone(false);
              }}
            >
              <RotateCcw size={16} />
              Practice again ({sessionSize} questions)
            </button>
            {availableSizes.length > 1 && (
              <div
                className="quiz-size-toggle"
                role="group"
                aria-label="Change session length"
              >
                {availableSizes.map((sz) => (
                  <button
                    key={sz}
                    type="button"
                    className={`size-btn ${sessionSize === sz ? "active" : ""}`}
                    onClick={() => {
                      setSessionSize(sz);
                      setQuestions(makeQuestions(sz));
                      setIndex(0);
                      setAnswer(null);
                      setChecked(false);
                      setCorrect(0);
                      setDone(false);
                    }}
                  >
                    {sz === m.quiz.length ? `Full (${sz})` : `${sz} Qs`}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="question-card">
          <div className="question-meta">
            <span>
              QUESTION {number(index + 1)} / {number(questions.length)}
            </span>
            <span>{correct} correct</span>
          </div>
          <ProgressBar value={(index / questions.length) * 100} />
          <h3>{question.prompt}</h3>
          <div
            className="answer-options"
            role="group"
            aria-label="Answer choices"
          >
            {question.options.map((option, i) => (
              <button
                key={i}
                className={`answer-option ${answer === i ? "chosen" : ""} ${checked && i === question.correctIndex ? "correct" : ""} ${checked && answer === i && i !== question.correctIndex ? "incorrect" : ""}`}
                aria-pressed={answer === i}
                disabled={checked}
                onClick={() => setAnswer(i)}
              >
                <span className="option-letter">{"ABCD"[i]}</span>
                <span>{option}</span>
                {checked && i === question.correctIndex && <Check size={18} />}
              </button>
            ))}
          </div>
          {checked && (
            <div
              className={`answer-feedback ${answer === question.correctIndex ? "success" : "review"}`}
              role="status"
            >
              <strong>
                {answer === question.correctIndex
                  ? "That’s right."
                  : "Let’s reconnect this to the slide."}
              </strong>
              <p>{question.explanation || question.sourceQuote}</p>
              <button
                className="text-button"
                onClick={() => source(question.page)}
              >
                Review source slide {question.page}
                <ArrowUpRight size={13} />
              </button>
            </div>
          )}
          <div className="question-footer">
            <span>
              <FileText size={14} />
              Based on {m.lectureLabel}
            </span>
            {checked ? (
              <button className="button dark" onClick={next}>
                {index === questions.length - 1
                  ? "See results"
                  : "Next question"}
                <ArrowRight size={16} />
              </button>
            ) : (
              <button
                className="button dark"
                disabled={answer === null}
                onClick={check}
              >
                Check answer
                <ArrowRight size={16} />
              </button>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
