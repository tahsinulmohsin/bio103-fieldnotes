import type { ReactNode } from "react";
import type { ShortAnswer, Slide } from "@/lib/types";

/** Tidy the few LaTeX-style fragments in the older Fall 2025 explanations. */
function symbols(text: string): string {
  return text
    .replace(/\$4\^3\s*=\s*64\$/g, "4³ = 64")
    .replace(/\$?CO_2\$?/g, "CO₂")
    .replace(/\$?O_2\$?/g, "O₂")
    .replace(/\$Na\^\+\$/g, "Na⁺")
    .replace(/\$K\^\+\$/g, "K⁺")
    .replace(/\$5'\$/g, "5′")
    .replace(/\$3'\$/g, "3′")
    .replace(/\\rightarrow/g, "→")
    .replace(/\\approx/g, "≈")
    .replace(/\\ge/g, "≥")
    .replace(/\\le/g, "≤")
    .replace(/\\Delta G/g, "ΔG")
    .replace(/\\mu m/g, "µm")
    .replace(/\\circ\\text\{C\}/g, "°C")
    .replace(/\\circ\\text\{F\}/g, "°F")
    .replace(/\\%/g, "%")
    .replace(/\$([^$]+)\$/g, "$1");
}

function inline(raw: string): ReactNode[] {
  const text = symbols(raw);
  const out: ReactNode[] = [];
  const pattern = /\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`/g;
  let last = 0;
  let m: RegExpExecArray | null;
  while ((m = pattern.exec(text))) {
    if (m.index > last) out.push(text.slice(last, m.index));
    if (m[1]) out.push(<strong key={m.index}>{m[1]}</strong>);
    else if (m[2]) out.push(<em key={m.index}>{m[2]}</em>);
    else out.push(<code key={m.index}>{m[3]}</code>);
    last = pattern.lastIndex;
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}

/** A small markdown subset: paragraphs, bullet and numbered lists, ### headings, bold and italics. */
export function Prose({ text }: { text: string }) {
  const blocks: ReactNode[] = [];
  let list: { ordered: boolean; items: string[] } | null = null;
  let para: string[] = [];
  const flushPara = () => {
    if (para.length) blocks.push(<p key={`p${blocks.length}`}>{inline(para.join(" "))}</p>);
    para = [];
  };
  const flushList = () => {
    if (!list) return;
    const Tag = list.ordered ? "ol" : "ul";
    blocks.push(
      <Tag key={`l${blocks.length}`}>
        {list.items.map((item, i) => (
          <li key={i}>{inline(item)}</li>
        ))}
      </Tag>,
    );
    list = null;
  };
  for (const raw of text.split("\n")) {
    const line = raw.trimEnd();
    const bullet = /^\s*[-*•]\s+(.*)$/.exec(line);
    const numbered = /^\s*\d+[.)]\s+(.*)$/.exec(line);
    const heading = /^\s*#{2,4}\s+(.*)$/.exec(line);
    if (!line.trim()) {
      flushPara();
      flushList();
    } else if (heading) {
      flushPara();
      flushList();
      blocks.push(<h4 key={`h${blocks.length}`}>{inline(heading[1])}</h4>);
    } else if (bullet || numbered) {
      flushPara();
      const ordered = Boolean(numbered);
      if (list && list.ordered !== ordered) flushList();
      if (!list) list = { ordered, items: [] };
      list.items.push((bullet ?? numbered)![1]);
    } else if (list && /^\s{2,}/.test(raw)) {
      list.items[list.items.length - 1] += " " + line.trim();
    } else {
      flushList();
      para.push(line.trim().replace(/^>\s*/, ""));
    }
  }
  flushPara();
  flushList();
  return <div className="prose">{blocks}</div>;
}

export function DataTable({ rows, head }: { rows: string[][]; head?: string[] }) {
  const header = head ?? rows[0];
  const body = head ? rows : rows.slice(1);
  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            {header.map((cell, i) => (
              <th key={i} scope="col">
                {cell}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {body.map((row, r) => (
            <tr key={r}>
              {row.map((cell, c) =>
                c === 0 && !header[0] ? (
                  <th key={c} scope="row">
                    {cell}
                  </th>
                ) : (
                  <td key={c}>{cell}</td>
                ),
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** The slide's own words: its bullets (with sub-levels) and any tables. */
export function SlideText({ slide }: { slide: Slide }) {
  const levels = slide.noteLevels ?? [];
  if (!slide.notes.length && !slide.tables?.length)
    return <p className="quiet">This slide has no text of its own; it teaches through its picture.</p>;
  return (
    <div className="slidetext">
      {slide.notes.length > 0 && (
        <ul>
          {slide.notes.map((note, i) => (
            <li key={i} className={levels[i] ? `lvl-${levels[i]}` : undefined}>
              {note}
            </li>
          ))}
        </ul>
      )}
      {slide.tables?.map((table, t) => <DataTable key={t} rows={table} />)}
    </div>
  );
}

/** A short answer's model answer, always the slide's own words. */
export function ModelAnswer({ item }: { item: ShortAnswer }) {
  const { answer } = item;
  if (answer.rows) return <DataTable head={answer.columns} rows={answer.rows} />;
  if (answer.points)
    return (
      <div className="slidetext">
        <ul>
          {answer.points.map((p, i) => (
            <li key={i}>{p}</li>
          ))}
        </ul>
      </div>
    );
  return <blockquote className="q-quote">{answer.text}</blockquote>;
}
