"use client";

import { useEffect, useRef, useState } from "react";
import { ArrowLeft, ArrowRight, ArrowUpRight, Expand, Info, RotateCcw, X } from "lucide-react";
import { Practise } from "@/components/practise";
import { Recall } from "@/components/recall";
import { Prose, SlideText } from "@/components/text";
import { Mark, SlideStrip, typing } from "@/components/ui";
import { readCount, teachingSlides } from "@/lib/progress";
import { useModule } from "@/lib/use-module";
import type { Module, ModuleProgress, ModuleSummary, Semester, Slide } from "@/lib/types";

export type Stage = "read" | "recall" | "practise";
export type LectureRoute = { id: string; slide?: number; stage: Stage };
type Update = (fn: (p: ModuleProgress) => ModuleProgress) => void;

/** How long a slide must stay on screen before it counts as read. */
const READ_AFTER_MS = 2000;

export function Lecture({
  semester,
  summary,
  progress: p,
  update,
  route,
  go,
}: {
  semester: Semester;
  summary: ModuleSummary;
  progress: ModuleProgress;
  update: Update;
  route: LectureRoute;
  go: (route: LectureRoute) => void;
}) {
  const { module, error, retry } = useModule(semester, summary.id);
  const total = teachingSlides(summary).length;
  const read = readCount(summary, p);
  const stages: { id: Stage; label: string; count?: number }[] = [
    { id: "read", label: "Read", count: summary.slides.length },
    { id: "recall", label: "Recall", count: summary.flashcardIds.length },
    { id: "practise", label: "Practise", count: summary.quizCount + summary.shortAnswerCount },
  ];
  return (
    <>
      <div className="lecture-top">
        <a className="back" href="#/">
          <ArrowLeft size={16} aria-hidden="true" />
          Contents
        </a>
        <span className="lecture-meta">
          {summary.lectureLabel}
          <span className="lecture-category"> · {summary.category}</span>
        </span>
        <span className="lecture-read">
          <span className="num">{read}</span> of <span className="num">{total}</span> slides read
        </span>
      </div>
      <header className="lecture-head">
        <h1>{summary.title}</h1>
        <nav className="stages" aria-label="Study stage">
          {stages.map((s) => (
            <button
              key={s.id}
              type="button"
              aria-current={route.stage === s.id ? "step" : undefined}
              onClick={() => go({ id: summary.id, stage: s.id, slide: route.slide })}
            >
              {s.label}
              <span className="count num">{s.count}</span>
            </button>
          ))}
        </nav>
      </header>
      {error ? (
        <div className="empty" role="alert">
          <p>This lecture didn’t load ({error}). Check your connection and try again.</p>
          <button className="btn" type="button" onClick={retry} style={{ marginTop: 16 }}>
            <RotateCcw size={16} aria-hidden="true" />
            Try again
          </button>
        </div>
      ) : !module ? (
        <div className="spread" aria-busy="true">
          <div className="skeleton" />
          <div className="skeleton" />
          <span className="sr-only" role="status">
            Opening {summary.title}
          </span>
        </div>
      ) : route.stage === "read" ? (
        <Read module={module} progress={p} update={update} route={route} go={go} />
      ) : route.stage === "recall" ? (
        <Recall key={module.id} module={module} progress={p} update={update} go={go} unread={total - read} />
      ) : (
        <Practise key={module.id} module={module} progress={p} update={update} go={go} unread={total - read} />
      )}
    </>
  );
}

function pageLink(m: Module, slide: Slide) {
  const url = m.source.previewUrl ?? m.source.url;
  return url.toLowerCase().endsWith(".pdf") ? `${url}#page=${slide.number}` : url;
}

function Read({
  module: m,
  progress: p,
  update,
  route,
  go,
}: {
  module: Module;
  progress: ModuleProgress;
  update: Update;
  route: LectureRoute;
  go: (route: LectureRoute) => void;
}) {
  const clamp = (i: number) => Math.max(0, Math.min(m.slides.length - 1, i));
  const index = clamp(route.slide ? route.slide - 1 : p.lastSlide);
  const slide = m.slides[index];
  const [view, setView] = useState<"explanation" | "slide">("explanation");
  const [zoom, setZoom] = useState(false);
  const dialog = useRef<HTMLDialogElement>(null);
  const heading = useRef<HTMLHeadingElement>(null);
  const shownView = slide.explanation ? view : "slide";
  const last = index === m.slides.length - 1;

  const markRead = (id: string) =>
    update((old) => (old.read.includes(id) ? old : { ...old, read: [...old.read, id] }));
  const select = (i: number) => {
    go({ id: m.id, stage: "read", slide: clamp(i) + 1 });
    heading.current?.focus({ preventScroll: true });
    // After reading to the bottom of a long explanation, bring the next slide back into view.
    requestAnimationFrame(() => {
      const strip = document.querySelector(".strip");
      if (strip && strip.getBoundingClientRect().top < 0) strip.scrollIntoView({ block: "start" });
    });
  };
  const next = () => {
    markRead(slide.id);
    if (last) go({ id: m.id, stage: "recall" });
    else select(index + 1);
  };

  // Remember the position, and count the slide as read once it has been on screen a moment.
  useEffect(() => {
    update((old) => (old.lastSlide === index ? old : { ...old, lastSlide: index }));
    const timer = window.setTimeout(() => markRead(slide.id), READ_AFTER_MS);
    return () => window.clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slide.id]);

  useEffect(() => {
    if (zoom) dialog.current?.showModal();
    else dialog.current?.close();
  }, [zoom]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (typing(e) || zoom) return;
      if (e.key === "ArrowRight") {
        e.preventDefault();
        next();
      } else if (e.key === "ArrowLeft" && index > 0) {
        e.preventDefault();
        select(index - 1);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  return (
    <>
      <SlideStrip slides={m.slides} current={index} read={p.read} onSelect={select} />
      <div className="spread">
        <section className="sheet" aria-labelledby="slide-title">
          <div className="sheet-margin">
            <span className="slide-no num">{slide.number}</span>
            <span className="slide-of num">/{m.slides.length}</span>
            {p.read.includes(slide.id) && (
              <span className="margin-tick" key={slide.id}>
                <Mark kind="read" />
                <span className="sr-only">Read</span>
              </span>
            )}
          </div>
          <div className="sheet-body">
            <h2 id="slide-title" className="slide-title" ref={heading} tabIndex={-1}>
              {slide.title}
            </h2>
            {slide.explanation && (
              <div className="textview" role="group" aria-label="Show">
                <button type="button" aria-pressed={shownView === "explanation"} onClick={() => setView("explanation")}>
                  Explanation
                </button>
                <button type="button" aria-pressed={shownView === "slide"} onClick={() => setView("slide")}>
                  Slide text
                </button>
              </div>
            )}
            <div className="textpane">
              {shownView === "explanation" && slide.explanation ? (
                <Prose text={slide.explanation} />
              ) : (
                <SlideText slide={slide} />
              )}
            </div>
            {shownView === "slide" && slide.ocrText && (
              <details className="ocr">
                <summary>Text read from the slide image</summary>
                <p>{slide.ocrText}</p>
              </details>
            )}
            <p className="provenance">
              <Info size={14} aria-hidden="true" />
              {shownView === "explanation"
                ? "Explanation written for this slide. Flashcards and practice use only the slide’s own words; if anything differs, go by your lecture."
                : "The slide’s own words. Text inside the picture is read automatically and may contain small errors."}
            </p>
            {/* On a phone the figure has no caption row; its actions sit here, under the reading. */}
            <p className="figure-actions-inline">
              <button type="button" className="btn btn-quiet btn-sm" onClick={() => setZoom(true)}>
                <Expand size={14} aria-hidden="true" />
                Enlarge slide
              </button>
              <a className="btn btn-quiet btn-sm" href={pageLink(m, slide)} target="_blank" rel="noreferrer">
                Original file
                <ArrowUpRight size={14} aria-hidden="true" />
              </a>
            </p>
          </div>
        </section>
        <figure className="figure-page">
          <button type="button" onClick={() => setZoom(true)} aria-label={`Enlarge slide ${slide.number}`}>
            <img
              src={slide.image}
              width={slide.width}
              height={slide.height}
              alt={`Slide ${slide.number}: ${slide.title}`}
            />
          </button>
          <figcaption>
            <span>
              {m.lectureLabel}, slide {slide.number}
            </span>
            <span className="figure-actions">
              <button type="button" className="btn btn-quiet btn-sm" onClick={() => setZoom(true)}>
                <Expand size={14} aria-hidden="true" />
                Enlarge
              </button>
              <a className="btn btn-quiet btn-sm" href={pageLink(m, slide)} target="_blank" rel="noreferrer">
                Original
                <ArrowUpRight size={14} aria-hidden="true" />
              </a>
            </span>
          </figcaption>
        </figure>
      </div>
      <div className="bar">
        <button className="btn" type="button" onClick={() => select(index - 1)} disabled={index === 0}>
          <ArrowLeft size={16} aria-hidden="true" />
          Previous
        </button>
        <span className="bar-status">
          <span>
            Slide <span className="num">{slide.number}</span> of <span className="num">{m.slides.length}</span>
          </span>
          <span className="kbd-hint" aria-hidden="true">
            <kbd>←</kbd>
            <kbd>→</kbd>
          </span>
        </span>
        <button className="btn btn-primary" type="button" onClick={next}>
          {last ? "Finish: recall" : "Next"}
          <ArrowRight size={16} aria-hidden="true" />
        </button>
      </div>
      <dialog ref={dialog} className="zoom" onClose={() => setZoom(false)} aria-label={`Slide ${slide.number}`}>
        <div className="zoom-top">
          <span>
            Slide {slide.number}: {slide.title}
          </span>
          <button className="btn btn-icon" type="button" onClick={() => setZoom(false)} aria-label="Close">
            <X size={18} aria-hidden="true" />
          </button>
        </div>
        {zoom && <img src={slide.image} alt={`Slide ${slide.number}: ${slide.title}`} />}
      </dialog>
    </>
  );
}
