"use client";

import { useState } from "react";
import { ArrowRight, ChevronRight, Search, X } from "lucide-react";
import { Line, pad } from "@/components/ui";
import { nextUnread, percentRead, readCount, reviewCount, teachingSlides } from "@/lib/progress";
import { blankModule, type CourseIndex, type ModuleSummary, type Progress } from "@/lib/types";

const lectureHref = (id: string, slide?: number, stage?: string) =>
  `#/lecture/${id}${stage ? `/${stage}` : slide ? `/${slide}` : ""}`;

function match(m: ModuleSummary, q: string) {
  if (!q) return { hit: true as const, note: "" };
  const inTitle = `${m.title} ${m.lectureLabel} ${m.category}`.toLowerCase().includes(q);
  const slide = m.slides.find((s) => s.title.toLowerCase().includes(q));
  const term = m.terms.find((t) => t.toLowerCase().includes(q));
  if (inTitle) return { hit: true as const, note: "" };
  if (term) return { hit: true as const, note: `Card: ${term}`, slide: undefined };
  if (slide) return { hit: true as const, note: `Slide ${slide.number}: ${slide.title}`, slide: slide.number };
  return { hit: false as const, note: "" };
}

export function Home({ course, progress }: { course: CourseIndex; progress: Progress }) {
  const [query, setQuery] = useState("");
  const q = query.trim().toLowerCase();
  const of = (m: ModuleSummary) => progress.modules[m.id] ?? blankModule();
  const resume =
    course.modules.find((m) => m.id === progress.lastModule) ??
    course.modules.find((m) => percentRead(m, of(m)) < 100) ??
    course.modules[0];
  const rp = of(resume);
  const started = progress.lastModule !== null;
  const nextIndex = started ? rp.lastSlide : nextUnread(resume, rp);
  const nextSlide = resume.slides[nextIndex] ?? resume.slides[0];
  const toReview = course.modules.filter((m) => reviewCount(of(m)) > 0);
  const categories = [...new Set(course.modules.map((m) => m.category))];

  return (
    <>
      <h1 className="page-title">BIO103 · {course.term}</h1>
      <p className="page-lede">
        {course.instructor.replace(/\s*\([^)]*\)$/, "")}. Read each lecture slide by slide with an explanation beside it, then
        recall and practise from the slides.
      </p>

      <section className="sheet nextup" aria-labelledby="nextup-title">
        <div className="sheet-margin">
          <span className="slide-no num">{pad(resume.number)}</span>
        </div>
        <div className="sheet-body">
          <div>
            <h2 id="nextup-title">{resume.title}</h2>
            <p className="nextup-slide">
              {resume.lectureLabel} · Slide <span className="num">{nextSlide.number}</span> of <span className="num">{resume.slides.length}</span>:{" "}
              {nextSlide.title}
            </p>
            <div style={{ marginTop: 16, maxWidth: 420 }}>
              <Line value={percentRead(resume, rp)} label={`${resume.title} slides read`} />
              <p className="line-label">
                <span>
                  <span className="num">{readCount(resume, rp)}</span> of <span className="num">{teachingSlides(resume).length}</span>{" "}
                  slides read
                </span>
                {rp.bestScore !== null && <span>best practice {rp.bestScore}%</span>}
              </p>
            </div>
            <div className="nextup-actions">
              <a className="btn btn-primary" href={lectureHref(resume.id, nextSlide.number)}>
                {started ? `Continue at slide ${nextSlide.number}` : "Start reading"}
                <ArrowRight size={16} aria-hidden="true" />
              </a>
              <a className="btn" href={lectureHref(resume.id, undefined, "recall")}>
                Recall cards
              </a>
              <a className="btn" href={lectureHref(resume.id, undefined, "practise")}>
                Practise
              </a>
            </div>
          </div>
          <a className="nextup-figure" href={lectureHref(resume.id, nextSlide.number)} aria-label={`Open slide ${nextSlide.number}`}>
            <img src={nextSlide.image} alt="" loading="eager" width={400} height={300} />
          </a>
        </div>
      </section>

      {toReview.length > 0 && (
        <section className="section" aria-labelledby="review-title">
          <h2 id="review-title">Needs another look</h2>
          <div className="review-list">
            {toReview.map((m) => {
              const p = of(m);
              return (
                <a key={m.id} className="review-item" href={lectureHref(m.id, undefined, p.missed.length ? "practise" : "recall")}>
                  <span>{m.title}</span>
                  <strong className="num">{reviewCount(p)}</strong>
                  <ChevronRight size={16} aria-hidden="true" />
                </a>
              );
            })}
          </div>
        </section>
      )}

      <section className="section" aria-labelledby="contents-title">
        <div className="contents-tools">
          <h2 id="contents-title" style={{ marginBottom: 0 }}>
            Lectures
          </h2>
          <div className="search" role="search">
            <Search size={16} aria-hidden="true" />
            <label className="sr-only" htmlFor="find">
              Find a lecture, slide or term
            </label>
            <input
              id="find"
              type="search"
              placeholder="Find a lecture, slide or term"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
        </div>
        <div className="contents">
          {categories.map((cat) => {
            const rows = course.modules.filter((m) => m.category === cat).map((m) => ({ m, hit: match(m, q) })).filter((r) => r.hit.hit);
            if (!rows.length) return null;
            return (
              <div key={cat}>
                <h3 className="contents-group">{cat}</h3>
                {rows.map(({ m, hit }) => {
                  const p = of(m);
                  const pct = percentRead(m, p);
                  return (
                    <a key={m.id} className="contents-row" href={lectureHref(m.id, "slide" in hit ? hit.slide : undefined)}>
                      <span className="contents-no num">{pad(m.number)}</span>
                      <span>
                        <span className="contents-title">{m.title}</span>
                        <span className="contents-sub">
                          {" "}
                          · {m.lectureLabel} · {m.slides.length} slides
                        </span>
                        {hit.note && <span className="contents-hit" style={{ display: "block" }}>{hit.note}</span>}
                        <span className="contents-mobile">
                          {pct}% read · {m.flashcardIds.length} cards
                          {p.bestScore !== null ? ` · best ${p.bestScore}%` : ""}
                        </span>
                      </span>
                      <span className="col-read">
                        <Line value={pct} label={`${m.title} slides read`} />
                        <span className="line-label">
                          <span>
                            <span className="num">{readCount(m, p)}</span>/<span className="num">{teachingSlides(m).length}</span> read
                          </span>
                        </span>
                      </span>
                      <span className="contents-stat col-cards">
                        <span className="num">{p.known.length}</span>/<span className="num">{m.flashcardIds.length}</span> cards
                      </span>
                      <span className="contents-stat col-practice">
                        {p.bestScore === null ? (
                          <span className="quiet">not practised</span>
                        ) : (
                          <>
                            best <span className="num">{p.bestScore}%</span>
                          </>
                        )}
                      </span>
                      <ChevronRight size={18} aria-hidden="true" className="quiet" />
                    </a>
                  );
                })}
              </div>
            );
          })}
          {!course.modules.some((m) => match(m, q).hit) && (
            <div className="empty">
              <p>Nothing matches “{query}”.</p>
              <button className="btn" type="button" style={{ marginTop: 12 }} onClick={() => setQuery("")}>
                <X size={16} aria-hidden="true" />
                Clear search
              </button>
            </div>
          )}
        </div>
      </section>
    </>
  );
}
