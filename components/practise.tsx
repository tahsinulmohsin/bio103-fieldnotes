"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { ArrowRight, ArrowUpRight, Check, Eye, RotateCcw, X } from "lucide-react";
import { ModelAnswer } from "@/components/text";
import { Mark, typing } from "@/components/ui";
import type { LectureRoute } from "@/components/lecture";
import type { Module, ModuleProgress, Question, ShortAnswer } from "@/lib/types";

type Update = (fn: (p: ModuleProgress) => ModuleProgress) => void;
type Mode = "mcq" | "short" | "mistakes";

function shuffled<T>(items: T[]): T[] {
  const out = [...items];
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

/** Random questions, each with its options in a fresh order. */
function session(quiz: Question[], count: number): Question[] {
  return shuffled(quiz)
    .slice(0, Math.min(count, quiz.length))
    .map((q) => {
      const order = shuffled(q.options.map((_, i) => i));
      return { ...q, options: order.map((i) => q.options[i]), correctIndex: order.indexOf(q.correctIndex) };
    });
}

export function Practise({
  module: m,
  progress: p,
  update,
  go,
  unread,
}: {
  module: Module;
  progress: ModuleProgress;
  update: Update;
  go: (route: LectureRoute) => void;
  unread: number;
}) {
  const ids = useMemo(() => new Set(m.quiz.map((q) => q.id)), [m.quiz]);
  const mistakes = p.missed.filter((id) => ids.has(id));
  const [mode, setMode] = useState<Mode>("mcq");
  const counts: Record<Mode, number> = { mcq: m.quiz.length, short: m.shortAnswers.length, mistakes: mistakes.length };
  const labels: Record<Mode, string> = { mcq: "Multiple choice", short: "Short answer", mistakes: "Mistakes" };
  return (
    <div className="practise">
      <div className="modes" role="group" aria-label="Practice type">
        {(["mcq", "short", "mistakes"] as Mode[])
          .filter((k) => k !== "mistakes" || counts.mistakes > 0 || mode === "mistakes")
          .map((k) => (
            <button key={k} type="button" aria-pressed={mode === k} onClick={() => setMode(k)} disabled={counts[k] === 0}>
              {labels[k]}
              <span className="num">{counts[k]}</span>
            </button>
          ))}
      </div>
      {unread > 0 && (
        <p className="nudge">
          <span>
            You have <span className="num">{unread}</span> slides still unread. Practice works best after reading.
          </span>
          <button className="btn btn-quiet" type="button" onClick={() => go({ id: m.id, stage: "read" })}>
            Continue reading
          </button>
        </p>
      )}
      {mode === "short" ? (
        <ShortAnswers key="short" items={m.shortAnswers} module={m} update={update} go={go} />
      ) : (
        <MultipleChoice
          key={mode}
          module={m}
          pool={mode === "mistakes" ? m.quiz.filter((q) => mistakes.includes(q.id)) : m.quiz}
          review={mode === "mistakes"}
          progress={p}
          update={update}
          go={go}
          done={() => setMode("mcq")}
        />
      )}
    </div>
  );
}

function MultipleChoice({
  module: m,
  pool,
  review,
  progress: p,
  update,
  go,
  done: leaveReview,
}: {
  module: Module;
  pool: Question[];
  review: boolean;
  progress: ModuleProgress;
  update: Update;
  go: (route: LectureRoute) => void;
  done: () => void;
}) {
  const sizes = [10, 25, pool.length].filter((n, i, all) => n <= pool.length && all.indexOf(n) === i);
  const [size, setSize] = useState(() => (review ? pool.length : Math.min(10, pool.length)));
  const [questions, setQuestions] = useState(() => session(pool, size));
  const [index, setIndex] = useState(0);
  const [choice, setChoice] = useState<number | null>(null);
  const [checked, setChecked] = useState(false);
  const [right, setRight] = useState(0);
  const [finished, setFinished] = useState(false);
  const sheet = useRef<HTMLElement>(null);
  const feedback = useRef<HTMLDivElement>(null);
  const q = questions[index];

  // Bring the marked answer into view, and the next question back to the top of the screen.
  useEffect(() => {
    if (checked) feedback.current?.scrollIntoView({ block: "nearest" });
  }, [checked]);
  useEffect(() => {
    const top = sheet.current?.getBoundingClientRect().top;
    if (top !== undefined && top < 0) sheet.current?.scrollIntoView({ block: "start" });
  }, [index]);

  const restart = (n: number) => {
    setSize(n);
    setQuestions(session(pool, n));
    setIndex(0);
    setChoice(null);
    setChecked(false);
    setRight(0);
    setFinished(false);
  };
  const check = () => {
    if (choice === null || checked || !q) return;
    const ok = choice === q.correctIndex;
    setChecked(true);
    if (ok) setRight((r) => r + 1);
    update((old) => ({
      ...old,
      missed: ok ? old.missed.filter((id) => id !== q.id) : [...new Set([...old.missed, q.id])],
    }));
  };
  const next = () => {
    if (index < questions.length - 1) {
      setIndex(index + 1);
      setChoice(null);
      setChecked(false);
      return;
    }
    setFinished(true);
    if (!review) {
      const score = Math.round((right / questions.length) * 100);
      update((old) => ({ ...old, bestScore: Math.max(old.bestScore ?? 0, score), attempts: old.attempts + 1 }));
    }
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (typing(e) || finished || !q) return;
      const k = e.key.toLowerCase();
      const pick = ["1", "2", "3", "4"].indexOf(k) >= 0 ? Number(k) - 1 : ["a", "b", "c", "d"].indexOf(k);
      if (!checked && pick >= 0 && pick < q.options.length) {
        e.preventDefault();
        setChoice(pick);
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (checked) next();
        else check();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  if (!pool.length) return <p className="empty">No questions here yet.</p>;

  if (finished) {
    const pct = Math.round((right / questions.length) * 100);
    return (
      <div className="session">
        <div className="result">
          <h2>
            <span className="num">{right}</span> of <span className="num">{questions.length}</span> right
          </h2>
          <p>
            {pct}% this round
            {!review && p.bestScore !== null && (
              <>
                {" "}
                · best <span className="num">{Math.max(p.bestScore, pct)}%</span>
              </>
            )}
          </p>
          <div className="row">
            {review ? (
              <button className="btn" type="button" onClick={leaveReview}>
                Back to multiple choice
              </button>
            ) : (
              <button className="btn" type="button" onClick={() => restart(size)}>
                <RotateCcw size={16} aria-hidden="true" />
                New round of {size}
              </button>
            )}
            <button className="btn btn-primary" type="button" onClick={() => go({ id: m.id, stage: "recall" })}>
              Recall cards
              <ArrowRight size={16} aria-hidden="true" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  const ok = checked && choice === q.correctIndex;
  return (
    <div className="session">
      {!review && index === 0 && !checked && sizes.length > 1 && (
        <div className="session-sizes" role="group" aria-label="Round length">
          <span>Round:</span>
          {sizes.map((n) => (
            <button key={n} type="button" aria-pressed={size === n} onClick={() => restart(n)}>
              {n === pool.length ? `All ${n}` : n}
            </button>
          ))}
        </div>
      )}
      <section className="sheet" aria-labelledby="q-prompt" ref={sheet}>
        <div className="sheet-margin">
          <p className="tally">
            <span className="right num" aria-hidden="true">
              <Mark kind="right" still />
              {right}
            </span>
            <span className="wrong num" aria-hidden="true">
              <Mark kind="wrong" still />
              {index + (checked ? 1 : 0) - right}
            </span>
            <span className="sr-only">
              {right} right, {index + (checked ? 1 : 0) - right} wrong so far
            </span>
          </p>
        </div>
        <div className="sheet-body">
          <p className="q-count">
            Question <span className="num">{index + 1}</span> of <span className="num">{questions.length}</span>
            {review && " · mistakes"}
          </p>
          <h2 id="q-prompt" className="q-prompt">
            {q.prompt}
          </h2>
          {q.quote && <blockquote className="q-quote">{q.quote}</blockquote>}
          <ul className="options">
            {q.options.map((option, i) => {
              const state = checked ? (i === q.correctIndex ? "right" : i === choice ? "wrong" : undefined) : undefined;
              return (
                <li key={i}>
                  <button
                    type="button"
                    className="option"
                    aria-pressed={choice === i}
                    data-state={state}
                    disabled={checked}
                    onClick={() => setChoice(i)}
                  >
                    {state && (
                      <span className="option-mark">
                        <Mark kind={state} />
                      </span>
                    )}
                    <span className="option-key">{"ABCD"[i]}</span>
                    <span>
                      {option}
                      {state && <span className="sr-only">{state === "right" ? " (correct answer)" : " (your answer, wrong)"}</span>}
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
          {checked && (
            <div className="feedback" role="status" ref={feedback}>
              <p className={`feedback-head ${ok ? "right" : "wrong"}`}>
                {ok ? <Check size={18} aria-hidden="true" /> : <X size={18} aria-hidden="true" />}
                {ok ? "Correct" : `Not quite. The answer is ${"ABCD"[q.correctIndex]}.`}
              </p>
              <p>
                Slide {q.page}: “{q.explanation}”
              </p>
              <button className="btn btn-quiet" type="button" onClick={() => go({ id: m.id, stage: "read", slide: q.page })}>
                Open slide {q.page}
                <ArrowUpRight size={14} aria-hidden="true" />
              </button>
            </div>
          )}
        </div>
      </section>
      <div className="bar">
        <span className="bar-status">
          <span className="kbd-hint" aria-hidden="true">
            <kbd>1</kbd>–<kbd>4</kbd> choose · <kbd>Enter</kbd> {checked ? "next" : "check"}
          </span>
        </span>
        {checked ? (
          <button className="btn btn-primary" type="button" onClick={next}>
            {index === questions.length - 1 ? "See result" : "Next question"}
            <ArrowRight size={16} aria-hidden="true" />
          </button>
        ) : (
          <button className="btn btn-primary" type="button" onClick={check} disabled={choice === null}>
            Check
            <ArrowRight size={16} aria-hidden="true" />
          </button>
        )}
      </div>
    </div>
  );
}

function ShortAnswers({
  items,
  module: m,
  update,
  go,
}: {
  items: ShortAnswer[];
  module: Module;
  update: Update;
  go: (route: LectureRoute) => void;
}) {
  const [index, setIndex] = useState(0);
  const [shown, setShown] = useState(false);
  const [draft, setDraft] = useState("");
  const [tally, setTally] = useState({ had: 0, missed: 0 });
  const sheet = useRef<HTMLElement>(null);
  const model = useRef<HTMLDivElement>(null);
  const item = items[index];
  const finished = index >= items.length;

  useEffect(() => {
    if (shown) model.current?.scrollIntoView({ block: "nearest" });
  }, [shown]);
  useEffect(() => {
    const top = sheet.current?.getBoundingClientRect().top;
    if (top !== undefined && top < 0) sheet.current?.scrollIntoView({ block: "start" });
  }, [index]);

  const mark = (had: boolean) => {
    if (!item) return;
    update((old) => ({
      ...old,
      shortMissed: had ? old.shortMissed.filter((id) => id !== item.id) : [...new Set([...old.shortMissed, item.id])],
    }));
    setTally((t) => ({ had: t.had + (had ? 1 : 0), missed: t.missed + (had ? 0 : 1) }));
    setIndex(index + 1);
    setShown(false);
    setDraft("");
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (typing(e) || finished) return;
      if (!shown && (e.key === " " || e.key === "Enter")) {
        e.preventDefault();
        setShown(true);
      } else if (shown && (e.key === "ArrowRight" || e.key === "2")) {
        e.preventDefault();
        mark(true);
      } else if (shown && (e.key === "ArrowLeft" || e.key === "1")) {
        e.preventDefault();
        mark(false);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  if (!items.length) return <p className="empty">No short-answer prompts for this lecture.</p>;
  if (finished)
    return (
      <div className="session">
        <div className="result">
          <h2>All {items.length} prompts done</h2>
          <p>
            Had it <span className="num">{tally.had}</span> · missed parts <span className="num">{tally.missed}</span>
          </p>
          <div className="row">
            <button
              className="btn"
              type="button"
              onClick={() => {
                setIndex(0);
                setTally({ had: 0, missed: 0 });
              }}
            >
              <RotateCcw size={16} aria-hidden="true" />
              Start again
            </button>
          </div>
        </div>
      </div>
    );

  return (
    <div className="session">
      <section className="sheet" aria-labelledby="sa-prompt" ref={sheet}>
        <div className="sheet-margin">
          <p className="tally">
            <span className="right num" aria-hidden="true">
              <Mark kind="right" still />
              {tally.had}
            </span>
            <span className="wrong num" aria-hidden="true">
              <Mark kind="wrong" still />
              {tally.missed}
            </span>
            <span className="sr-only">
              Had it {tally.had}, missed parts {tally.missed}
            </span>
          </p>
        </div>
        <div className="sheet-body">
          <p className="q-count">
            Prompt <span className="num">{index + 1}</span> of <span className="num">{items.length}</span> · write it as you
            would in the exam
          </p>
          <h2 id="sa-prompt" className="q-prompt">
            {item.prompt}
          </h2>
          <label className="sr-only" htmlFor="sa-draft">
            Your answer (not graded)
          </label>
          <textarea
            id="sa-draft"
            className="answer-box"
            placeholder="Write your answer here (optional, not graded). Then show the slide’s answer and compare."
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
          />
          {shown && (
            <div className="model" ref={model}>
              <h3>The slide’s answer</h3>
              <p className="model-src">
                From slide {item.page}.{" "}
                <button
                  className="btn btn-quiet btn-sm"
                  type="button"
                  onClick={() => go({ id: m.id, stage: "read", slide: item.page })}
                >
                  Open slide
                  <ArrowUpRight size={14} aria-hidden="true" />
                </button>
              </p>
              <ModelAnswer item={item} />
            </div>
          )}
        </div>
      </section>
      <div className="bar">
        {shown ? (
          <>
            <button className="btn" type="button" onClick={() => mark(false)}>
              <X size={16} aria-hidden="true" />
              Missed parts
            </button>
            <span className="bar-status kbd-hint" aria-hidden="true">
              <kbd>←</kbd> or <kbd>→</kbd> to mark it
            </span>
            <button className="btn btn-primary" type="button" onClick={() => mark(true)}>
              <Check size={16} aria-hidden="true" />
              Had it
            </button>
          </>
        ) : (
          <>
            <span className="bar-status kbd-hint" aria-hidden="true">
              <kbd>Space</kbd> show answer
            </span>
            <button className="btn btn-primary" type="button" onClick={() => setShown(true)}>
              <Eye size={16} aria-hidden="true" />
              Show the slide’s answer
            </button>
          </>
        )}
      </div>
    </div>
  );
}
