"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Leaf, Menu, Moon, Sun, X } from "lucide-react";
import { Home } from "@/components/home";
import { Lecture, type LectureRoute, type Stage } from "@/components/lecture";
import { ProgressPage, SourcesPage } from "@/components/pages";
import { fresh, restore, storageKeys } from "@/lib/progress";
import { blankModule, type CourseIndex, type ModuleProgress, type Progress, type Semester } from "@/lib/types";

type Route =
  | { page: "home" }
  | { page: "progress" }
  | { page: "sources" }
  | { page: "lecture"; lecture: LectureRoute };

const SEMESTER_KEY = "bio103-selected-semester";
const terms: Record<Semester, string> = { fall2026: "Fall 2026", fall2025: "Fall 2025" };

function parse(hash: string): Route {
  const h = hash.replace(/^#\/?/, "");
  const [head, id, extra] = h.split("/");
  if (head === "progress") return { page: "progress" };
  if (head === "sources") return { page: "sources" };
  if (head === "lecture" && id) {
    const stage: Stage = extra === "recall" || extra === "practise" ? extra : "read";
    const n = Number(extra);
    return { page: "lecture", lecture: { id, stage, slide: Number.isInteger(n) && n > 0 ? n : undefined } };
  }
  // Links from the first version of the app.
  if (head.startsWith("module")) return { page: "lecture", lecture: { id: h.replace(/^module\/?/, ""), stage: "read" } };
  return { page: "home" };
}

/** Which page is on screen; moving between slides of one lecture stays on the same page. */
const pageKey = (route: Route) =>
  route.page === "lecture" ? `lecture/${route.lecture.id}/${route.lecture.stage}` : route.page;

function format(route: Route): string {
  if (route.page !== "lecture") return route.page === "home" ? "#/" : `#/${route.page}`;
  const { id, stage, slide } = route.lecture;
  return `#/lecture/${id}${stage !== "read" ? `/${stage}` : slide ? `/${slide}` : ""}`;
}

export default function StudyApp({ courses, version }: { courses: Record<Semester, CourseIndex>; version: string }) {
  const [semester, setSemester] = useState<Semester>("fall2026");
  const [route, setRoute] = useState<Route>({ page: "home" });
  const [progress, setProgress] = useState<Progress>(fresh);
  // The storage key `progress` was read from; saving waits until it matches the semester.
  const [loadedFor, setLoadedFor] = useState<string | null>(null);
  const [storageError, setStorageError] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [menu, setMenu] = useState(false);
  const shownKey = useRef<string | null>(null);

  const course = courses[semester];
  const storageKey = storageKeys[semester];

  useEffect(() => {
    let initial: Semester = "fall2026";
    try {
      const saved = localStorage.getItem(SEMESTER_KEY);
      if (saved === "fall2026" || saved === "fall2025") initial = saved;
    } catch {}
    setSemester(initial);
    setProgress(restore(courses[initial], storageKeys[initial]));
    setLoadedFor(storageKeys[initial]);
    setTheme(document.documentElement.dataset.theme === "dark" ? "dark" : "light");
    // Links change the hash directly; opening a different page starts it from the top.
    const sync = () => {
      const next = parse(location.hash);
      if (shownKey.current !== null && pageKey(next) !== shownKey.current) window.scrollTo(0, 0);
      setRoute(next);
    };
    sync();
    window.addEventListener("hashchange", sync);
    window.addEventListener("popstate", sync);
    return () => {
      window.removeEventListener("hashchange", sync);
      window.removeEventListener("popstate", sync);
    };
  }, [courses]);

  useEffect(() => {
    shownKey.current = pageKey(route);
  }, [route]);

  useEffect(() => {
    if (loadedFor !== storageKey) return;
    try {
      localStorage.setItem(storageKey, JSON.stringify(progress));
      setStorageError(false);
    } catch {
      setStorageError(true);
    }
  }, [progress, loadedFor, storageKey]);

  /** Navigate. Moving between slides replaces the history entry; everything else adds one. */
  const go = useCallback(
    (next: Route) => {
      const sameLecture =
        next.page === "lecture" &&
        route.page === "lecture" &&
        next.lecture.id === route.lecture.id &&
        next.lecture.stage === route.lecture.stage;
      const url = format(next);
      if (url !== location.hash) {
        if (sameLecture) history.replaceState(null, "", url);
        else history.pushState(null, "", url);
      }
      setRoute(next);
      setMenu(false);
      if (!sameLecture) window.scrollTo(0, 0);
    },
    [route],
  );

  const switchSemester = (next: Semester) => {
    if (next === semester) return;
    setSemester(next);
    setProgress(restore(courses[next], storageKeys[next]));
    setLoadedFor(storageKeys[next]);
    try {
      localStorage.setItem(SEMESTER_KEY, next);
    } catch {}
    if (route.page === "lecture") go({ page: "home" });
    setMenu(false);
  };

  const toggleTheme = () => {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    document.documentElement.dataset.theme = next;
    try {
      localStorage.setItem("bio103-theme", next);
    } catch {}
  };

  const update = (id: string) => (fn: (p: ModuleProgress) => ModuleProgress) =>
    setProgress((p) => {
      const current = p.modules[id] ?? blankModule();
      const changed = fn(current);
      if (changed === current && p.lastModule === id) return p;
      return { ...p, lastModule: id, modules: { ...p.modules, [id]: changed } };
    });

  const lecture =
    route.page === "lecture" ? course.modules.find((m) => m.id === route.lecture.id) : undefined;
  const page = route.page === "lecture" && !lecture ? "home" : route.page;

  const navLinks = [
    { href: "#/", label: "Contents", active: page === "home" || page === "lecture" },
    { href: "#/progress", label: "Progress", active: page === "progress" },
    { href: "#/sources", label: "Sources", active: page === "sources" },
  ];
  const semesterSwitch = (
    <div className="semester" role="group" aria-label="Semester">
      {(Object.keys(terms) as Semester[]).map((s) => (
        <button
          key={s}
          type="button"
          aria-pressed={semester === s}
          onClick={() => switchSemester(s)}
          title={`${terms[s]}: ${courses[s].instructor}`}
        >
          {terms[s]}
        </button>
      ))}
    </div>
  );
  const themeButton = (
    <button
      className="btn btn-icon theme-toggle"
      type="button"
      onClick={toggleTheme}
      aria-label={theme === "dark" ? "Use light theme" : "Use dark theme"}
      title={theme === "dark" ? "Light theme" : "Dark theme"}
    >
      {theme === "dark" ? <Sun size={18} aria-hidden="true" /> : <Moon size={18} aria-hidden="true" />}
    </button>
  );

  return (
    <>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="topbar">
        <a className="brand" href="#/" aria-label="fieldnotes, contents">
          <Leaf size={22} aria-hidden="true" />
          fieldnotes
        </a>
        <span className="course-mark">
          <img src="/nsu-logo.svg" alt="North South University" width={26} height={26} />
          <span>BIO103 · North South University</span>
        </span>
        {semesterSwitch}
        <nav className="topnav" aria-label="Main">
          {navLinks.map((l) => (
            <a key={l.href} href={l.href} aria-current={l.active ? "page" : undefined}>
              {l.label}
            </a>
          ))}
        </nav>
        {themeButton}
        <button
          className="btn btn-quiet menu-toggle"
          type="button"
          aria-expanded={menu}
          aria-controls="mobile-menu"
          onClick={() => setMenu((m) => !m)}
        >
          {menu ? <X size={20} aria-hidden="true" /> : <Menu size={20} aria-hidden="true" />}
          <span className="sr-only">Menu</span>
        </button>
      </header>
      <div id="mobile-menu" className="mobile-menu" hidden={!menu}>
        {semesterSwitch}
        <nav aria-label="Main">
          {navLinks.map((l) => (
            <a key={l.href} href={l.href} aria-current={l.active ? "page" : undefined} onClick={() => setMenu(false)}>
              {l.label}
            </a>
          ))}
        </nav>
        <div className="mobile-menu-foot">
          <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
            <img src="/nsu-logo.svg" alt="" width={22} height={22} />
            BIO103 · NSU
          </span>
          {themeButton}
        </div>
      </div>
      <main id="main" tabIndex={-1} className={`wrap${page === "lecture" ? " wrap-wide" : ""}`}>
        {storageError && (
          <p role="status" className="storage-alert">
            This browser isn’t saving progress. It lasts until you close the tab; export it from Progress to keep a copy.
          </p>
        )}
        {loadedFor === null ? (
          <p className="loading" role="status">
            Opening your notes…
          </p>
        ) : page === "lecture" && lecture && route.page === "lecture" ? (
          <Lecture
            key={`${semester}/${lecture.id}`}
            semester={semester}
            summary={lecture}
            progress={progress.modules[lecture.id] ?? blankModule()}
            update={update(lecture.id)}
            route={route.lecture}
            go={(r) => go({ page: "lecture", lecture: r })}
          />
        ) : page === "progress" ? (
          <ProgressPage course={course} progress={progress} semester={semester} reset={() => setProgress(fresh())} />
        ) : page === "sources" ? (
          <SourcesPage course={course} />
        ) : (
          <Home course={course} progress={progress} />
        )}
        <footer className="footer">
          <span>
            fieldnotes <span className="num">v{version}</span> · BIO103, {terms[semester]}
          </span>
          <span>Progress is saved in this browser only.</span>
        </footer>
      </main>
    </>
  );
}
