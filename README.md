# BIO103 Fieldnotes

A Next.js, React and Tailwind study app made exclusively from the supplied NSU BIO103 lecture collection. Start with explanations and original slide graphics, then unlock exact-wording flashcards and basic source-backed quizzes. Progress is saved in the current browser.

## Run locally

Requires Node.js 22.9+ (the container uses Node 24).

```sh
npm ci
npm run dev
```

Open http://localhost:3103. For production, run `npm run build` then `npm start`. Docker uses its generated standalone server on port 3000; Compose publishes loopback port 3103.

## What is included

- 13 lecture topics and every one of their 439 slides.
- 8-page course outline, listed separately as a reference.
- 167 literal source flashcards and 2,116 basic multiple-choice questions. A practice session supports Quick 10, Standard 25, Challenge 50, and Full Topic mastery.
- Original visuals for all 447 pages, including the PowerPoint's hidden slides.
- Search, topic filters, reading progress, per-topic recall tracking, quiz best scores and progress export.
- Accessible keyboard controls, responsive navigation, reduced motion, spring card flips and layout transitions.
- Reproducible extraction, source hashes and character-offset provenance.
- Standalone Docker build, unprivileged container, health check, and homelab routing configuration.

## Source-only contract

`data/course.json` contains the curriculum. Teaching text is extracted from the supplied files; it is not augmented with textbook knowledge. Every term, definition, quiz answer and distractor has a precise reference to an extracted source span. Questions use a basic matching template rather than an external model or API. Original wording, spellings and contradictions in explanations are preserved. Practice avoids known ambiguous statements.

`rawText` and `paragraphs` are the source text layer. The separately labeled image-text disclosure is local OCR and can misread small labels; OCR is never used to generate practice. `data/source-ocr.json` preserves its geometry and provenance. The original slide viewer remains authoritative.

Source files and full-resolution slide images are included in `public/sources` and `public/slides`. All links work without outside content services. The course outline does not generate practice.

## Checks

```sh
npm run typecheck
npm run verify:content
npm run build
```

The content validator is standard-library Python and verifies source hashes, original visual hashes, coverage and literal practice spans. Extraction itself needs the dependencies described in `docs/CONTENT_EXTRACTION.md` when that report is present and in `scripts/extract_course.py`; ordinary app use needs no Python or office tools.

Browser QA evidence is in `qa/`. The actual Playwright CLI was used to click through gating, explanation review, recall and scoring, with screenshots and a trace. See the QA report for the exact scope and findings.

## Project map

- `components/study-app.tsx`: dashboard, explanation-first flow, source viewer, flashcards, quizzes and local progress.
- `app/globals.css`: responsive editorial design and motion accessibility.
- `lib/types.ts`: curriculum and progress model.
- `data/course.json`: complete source-backed course.
- `scripts/extract_course.py`, `scripts/practice_spans.json`, `scripts/validate_course.py`: extraction and reproducible content validation.
- `Dockerfile`, `compose.yaml`, `deployment/`: homelab deployment and routing.
- `docs/DESIGN.md`: skill use, palette and interaction decisions.

## Progress and access

Progress is browser-local, not a server account, and is not synchronized across devices. Export saves a JSON copy; no import workflow is currently included. Reading completion is a learning sequence, not a security boundary. Source assets are served to everyone who can reach the application. To make access private, put the hostname behind an existing Cloudflare Access policy.

## Deployment

See `deployment/README.md` and the final deployment evidence for the verified homelab endpoint. Do not assume a deployment occurred merely from the presence of the configuration files.
