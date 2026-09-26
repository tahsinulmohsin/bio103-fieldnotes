"use client";

import { useEffect, useRef } from "react";

export const pad = (n: number) => String(n).padStart(2, "0");

export function Line({ value, label }: { value: number; label: string }) {
  const v = Math.max(0, Math.min(100, value));
  return (
    <div className="line" role="progressbar" aria-valuenow={Math.round(v)} aria-valuemin={0} aria-valuemax={100} aria-label={label}>
      <span style={{ transform: `scaleX(${v / 100})` }} />
    </div>
  );
}

/** Every slide as a numbered cell: read cells filled, the current one outlined. */
export function SlideStrip({
  slides,
  current,
  read,
  onSelect,
}: {
  slides: { id: string; number: number; title: string }[];
  current: number;
  read: string[];
  onSelect: (index: number) => void;
}) {
  const list = useRef<HTMLOListElement>(null);
  useEffect(() => {
    const el = list.current?.children[current] as HTMLElement | undefined;
    // On a phone the strip scrolls sideways; keep the current slide in the middle of it.
    el?.scrollIntoView({ block: "nearest", inline: "center" });
  }, [current]);
  return (
    <ol className="strip" ref={list} aria-label="Slides in this lecture">
      {slides.map((s, i) => {
        const done = read.includes(s.id);
        return (
          <li key={s.id}>
            <button
              type="button"
              aria-current={i === current ? "true" : undefined}
              data-read={done}
              aria-label={`Slide ${s.number}: ${s.title}${done ? ", read" : ""}`}
              title={`${s.number}. ${s.title}`}
              onClick={() => onSelect(i)}
            >
              {s.number}
            </button>
          </li>
        );
      })}
    </ol>
  );
}

/**
 * A tick or cross drawn in the margin, like a teacher marking a practical copy.
 * "read" is the pencil tick for a slide that has been read; `still` skips the drawing (tallies).
 */
export function Mark({ kind, still = false }: { kind: "right" | "wrong" | "read"; still?: boolean }) {
  return (
    <svg className={`mark ${kind}${still ? " still" : ""}`} viewBox="0 0 28 28" aria-hidden="true">
      {kind !== "wrong" ? (
        <path pathLength={1} d="M5 15.5 L11.5 22 L23.5 6.5" />
      ) : (
        <>
          <path pathLength={1} d="M7 7 L21 21" />
          <path pathLength={1} d="M21 7 L7 21" />
        </>
      )}
    </svg>
  );
}

/** True when a key press came from a text field, so shortcuts should stay out of the way. */
export const typing = (e: KeyboardEvent) =>
  e.target instanceof HTMLInputElement ||
  e.target instanceof HTMLTextAreaElement ||
  e.target instanceof HTMLSelectElement ||
  (e.target instanceof HTMLElement && e.target.isContentEditable) ||
  e.metaKey ||
  e.ctrlKey ||
  e.altKey;
