"use client";

import { useEffect, useMemo, useState } from "react";
import { ArrowRight, Check, RotateCcw } from "lucide-react";
import { Mark, typing } from "@/components/ui";
import type { LectureRoute } from "@/components/lecture";
import type { Flashcard, Module, ModuleProgress } from "@/lib/types";

type Update = (fn: (p: ModuleProgress) => ModuleProgress) => void;

export function Recall({
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
  const cards = useMemo(() => new Map(m.flashcards.map((c) => [c.id, c])), [m.flashcards]);
  const dueIds = p.again.filter((id) => cards.has(id));
  const [onlyDue, setOnlyDue] = useState(false);
  const [queue, setQueue] = useState<string[]>(() => m.flashcards.map((c) => c.id));
  const [pos, setPos] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [instant, setInstant] = useState(false);
  const [requeued, setRequeued] = useState<string[]>([]);
  const [tally, setTally] = useState({ got: 0, again: 0 });
  const card: Flashcard | undefined = cards.get(queue[pos]);
  const done = pos >= queue.length;

  const start = (ids: string[], due: boolean) => {
    setOnlyDue(due);
    setQueue(ids);
    setPos(0);
    setFlipped(false);
    setRequeued([]);
    setTally({ got: 0, again: 0 });
  };
  const flip = (fromKeyboard: boolean) => {
    setInstant(fromKeyboard);
    setFlipped((f) => !f);
  };
  const rate = (got: boolean) => {
    if (!card || !flipped) return;
    update((old) => ({
      ...old,
      known: got ? [...new Set([...old.known, card.id])] : old.known.filter((id) => id !== card.id),
      again: got ? old.again.filter((id) => id !== card.id) : [...new Set([...old.again, card.id])],
    }));
    setTally((t) => ({ got: t.got + (got ? 1 : 0), again: t.again + (got ? 0 : 1) }));
    // A missed card comes back once at the end of this session.
    if (!got && !requeued.includes(card.id)) {
      setQueue((q) => [...q, card.id]);
      setRequeued((r) => [...r, card.id]);
    }
    setInstant(true);
    setFlipped(false);
    setPos((i) => i + 1);
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (typing(e) || done) return;
      if (e.key === " " || e.key === "Enter") {
        e.preventDefault();
        flip(true);
      } else if (flipped && (e.key === "ArrowRight" || e.key === "2")) {
        e.preventDefault();
        rate(true);
      } else if (flipped && (e.key === "ArrowLeft" || e.key === "1")) {
        e.preventDefault();
        rate(false);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  if (!m.flashcards.length)
    return (
      <div className="empty">
        <p>This lecture has no clear term and definition pairs to recall. Practise instead.</p>
        <button className="btn btn-primary" type="button" style={{ marginTop: 16 }} onClick={() => go({ id: m.id, stage: "practise" })}>
          Go to practice
          <ArrowRight size={16} aria-hidden="true" />
        </button>
      </div>
    );

  return (
    <div className="deck">
      {unread > 0 && pos === 0 && !onlyDue && (
        <p className="nudge">
          <span>
            You have <span className="num">{unread}</span> slides still unread. Recall works best after reading.
          </span>
          <button className="btn btn-quiet" type="button" onClick={() => go({ id: m.id, stage: "read" })}>
            Continue reading
          </button>
        </p>
      )}
      {dueIds.length > 0 && pos === 0 && !onlyDue && (
        <p className="nudge">
          <span>
            <span className="num">{dueIds.length}</span> cards are waiting for another look.
          </span>
          <button className="btn btn-quiet" type="button" onClick={() => start(dueIds, true)}>
            Review only those
          </button>
        </p>
      )}
      {done ? (
        <div className="result" style={{ marginTop: 24 }}>
          <h2>Deck finished</h2>
          <p>
            Got it <span className="num">{tally.got}</span> · Again <span className="num">{tally.again}</span>
          </p>
          <div className="row">
            {p.again.length > 0 && (
              <button className="btn" type="button" onClick={() => start(p.again.filter((id) => cards.has(id)), true)}>
                <RotateCcw size={16} aria-hidden="true" />
                Review the {p.again.length} again
              </button>
            )}
            <button className="btn" type="button" onClick={() => start(m.flashcards.map((c) => c.id), false)}>
              Whole deck again
            </button>
            <button className="btn btn-primary" type="button" onClick={() => go({ id: m.id, stage: "practise" })}>
              Practise
              <ArrowRight size={16} aria-hidden="true" />
            </button>
          </div>
        </div>
      ) : (
        card && (
          <>
            <div className="deck-meta">
              <span>
                Card <span className="num">{pos + 1}</span> of <span className="num">{queue.length}</span>
                {onlyDue && " · review"}
              </span>
              <span className="deck-tally num">
                <span aria-hidden="true">
                  <Mark kind="right" still />
                  {tally.got}
                </span>
                <span aria-hidden="true">
                  <Mark kind="wrong" still />
                  {tally.again}
                </span>
                <span className="sr-only">
                  Got it {tally.got}, again {tally.again}
                </span>
              </span>
            </div>
            <div className="card-scene">
              <button
                type="button"
                className={`card${instant ? " instant" : ""}`}
                data-flipped={flipped}
                onClick={(e) => flip(e.detail === 0)}
                aria-label={flipped ? `${card.definition}. Show the term.` : `${card.term}. Show what the slide says.`}
              >
                <span className="card-face card-front" aria-hidden={flipped}>
                  <span className="card-head">Term</span>
                  <span className="card-main">
                    <span className="card-term">{card.term}</span>
                  </span>
                  <span className="card-foot">
                    <span>Think of what the slide says, then turn the card.</span>
                    <span className="kbd-hint" aria-hidden="true">
                      <kbd>Space</kbd>
                    </span>
                  </span>
                </span>
                <span className="card-face card-back" aria-hidden={!flipped}>
                  <span className="card-head">From slide {card.page}</span>
                  <span className="card-main">
                    <span className="card-def">{card.definition}</span>
                  </span>
                  <span className="card-foot">
                    <span>{card.term}</span>
                    <span>{m.lectureLabel}</span>
                  </span>
                </span>
              </button>
            </div>
            <div className="deck-actions">
              <button className="btn" type="button" disabled={!flipped} onClick={() => rate(false)}>
                <RotateCcw size={16} aria-hidden="true" />
                Again
                <kbd className="kbd-hint" aria-hidden="true">←</kbd>
              </button>
              <button className="btn btn-primary" type="button" disabled={!flipped} onClick={() => rate(true)}>
                <Check size={16} aria-hidden="true" />
                Got it
                <kbd className="kbd-hint" aria-hidden="true">→</kbd>
              </button>
            </div>
            <p className="deck-meta" style={{ justifyContent: "center", marginTop: 12 }}>
              <button className="btn btn-quiet" type="button" onClick={() => go({ id: m.id, stage: "read", slide: card.page })}>
                See slide {card.page}
              </button>
            </p>
          </>
        )
      )}
    </div>
  );
}
