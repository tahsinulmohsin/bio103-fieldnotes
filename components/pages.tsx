"use client";

import { useState } from "react";
import { Download, FileText } from "lucide-react";
import { Line, pad } from "@/components/ui";
import { percentRead, readCount, reviewCount, teachingSlides } from "@/lib/progress";
import { blankModule, type CourseIndex, type Progress, type Semester } from "@/lib/types";

export function ProgressPage({
  course,
  progress,
  semester,
  reset,
}: {
  course: CourseIndex;
  progress: Progress;
  semester: Semester;
  reset: () => void;
}) {
  const [confirming, setConfirming] = useState(false);
  const of = (id: string) => progress.modules[id] ?? blankModule();
  const totals = course.modules.reduce(
    (t, m) => {
      const p = of(m.id);
      return {
        read: t.read + readCount(m, p),
        slides: t.slides + teachingSlides(m).length,
        known: t.known + p.known.length,
        cards: t.cards + m.flashcardIds.length,
        review: t.review + reviewCount(p),
      };
    },
    { read: 0, slides: 0, known: 0, cards: 0, review: 0 },
  );
  const exportProgress = () => {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([JSON.stringify({ semester, ...progress }, null, 2)], { type: "application/json" }));
    a.download = `fieldnotes-bio103-${semester}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  };
  return (
    <>
      <h1 className="page-title">Your progress · {course.term}</h1>
      <p className="page-lede">
        <span className="num">{totals.read}</span> of <span className="num">{totals.slides}</span> slides read,{" "}
        <span className="num">{totals.known}</span> of <span className="num">{totals.cards}</span> cards recalled
        {totals.review > 0 && (
          <>
            , <span className="num">{totals.review}</span> items waiting for another look
          </>
        )}
        . Saved in this browser only.
      </p>
      <div className="section table-page">
        <table className="table">
          <thead>
            <tr>
              <th scope="col">No.</th>
              <th scope="col">Lecture</th>
              <th scope="col">Slides read</th>
              <th scope="col">Cards</th>
              <th scope="col">Best practice</th>
              <th scope="col">To review</th>
            </tr>
          </thead>
          <tbody>
            {course.modules.map((m) => {
              const p = of(m.id);
              return (
                <tr key={m.id}>
                  <td className="num">{pad(m.number)}</td>
                  <td>
                    <a href={`#/lecture/${m.id}`}>{m.title}</a>
                    <div className="quiet">{m.lectureLabel}</div>
                  </td>
                  <td>
                    <Line value={percentRead(m, p)} label={`${m.title} slides read`} />
                    <div className="line-label">
                      <span>
                        <span className="num">{readCount(m, p)}</span>/<span className="num">{teachingSlides(m).length}</span>
                      </span>
                    </div>
                  </td>
                  <td>
                    <span className="num">{p.known.length}</span>/<span className="num">{m.flashcardIds.length}</span>
                  </td>
                  <td>{p.bestScore === null ? <span className="quiet">not yet</span> : <span className="num">{p.bestScore}%</span>}</td>
                  <td>
                    {reviewCount(p) > 0 ? (
                      <a href={`#/lecture/${m.id}/${p.missed.length ? "practise" : "recall"}`}>
                        <span className="num">{reviewCount(p)}</span> to review
                      </a>
                    ) : (
                      <span className="quiet">none</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <div className="actions-row">
        <button className="btn" type="button" onClick={exportProgress}>
          <Download size={16} aria-hidden="true" />
          Export progress
        </button>
        {!confirming ? (
          <button className="btn btn-quiet" type="button" onClick={() => setConfirming(true)}>
            Reset {course.term} progress
          </button>
        ) : (
          <>
            <span>Clear all saved {course.term} progress on this browser?</span>
            <button
              className="btn"
              type="button"
              onClick={() => {
                reset();
                setConfirming(false);
              }}
            >
              Yes, clear it
            </button>
            <button className="btn btn-quiet" type="button" onClick={() => setConfirming(false)}>
              Cancel
            </button>
          </>
        )}
      </div>
    </>
  );
}

export function SourcesPage({ course }: { course: CourseIndex }) {
  const rows = [...course.modules, ...course.references];
  return (
    <>
      <h1 className="page-title">Sources · {course.term}</h1>
      <div className="policy" style={{ marginTop: 12 }}>
        <p>
          Everything here comes from the lecture files by {course.instructor}. Each slide is shown as the original image next to
          its own text. Flashcards, multiple-choice questions and short-answer model answers use only the slides’ own words,
          and each links back to its slide.
        </p>
        <p>
          {course.stats.explanationCount > 0
            ? `${course.stats.explanationCount} slides also have a written explanation to make them easier to understand. Explanations are labelled as such, are never used as practice answers, and if one ever differs from your lecture, go by the lecture.`
            : "This semester has no written explanations."}
          {course.references.length > 0 && " The course outline is listed for reference and is not used for practice."}
        </p>
      </div>
      <ul className="sources section">
        {rows.map((m, i) => (
          <li key={m.id}>
            <span className="contents-no num">{pad(i + 1)}</span>
            <span>
              <span className="file">{m.source.file}</span>
              <span className="quiet" style={{ display: "block", fontSize: 14 }}>
                {m.title} · {m.source.pageCount} pages
              </span>
            </span>
            <span className="links">
              {m.source.previewUrl && (
                <a className="btn" href={m.source.previewUrl} target="_blank" rel="noreferrer">
                  <FileText size={16} aria-hidden="true" />
                  View PDF
                </a>
              )}
              <a
                className="btn"
                href={m.source.url}
                target="_blank"
                rel="noreferrer"
                download={m.source.kind === "pdf" ? undefined : m.source.file}
              >
                <Download size={16} aria-hidden="true" />
                {m.source.kind === "pdf" ? "Open PDF" : `Download .${m.source.kind}`}
              </a>
            </span>
          </li>
        ))}
      </ul>
    </>
  );
}
