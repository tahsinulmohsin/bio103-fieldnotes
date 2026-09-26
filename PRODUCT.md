# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Any North South University student taking BIO103 (Biology I), not only the person who built it. Most readers will be strangers who open a shared link with no setup or explanation. They study on Windows laptops (Chrome/Edge), Macs (Safari/Chrome), Android phones (Chrome) and iPhones/iPads (Safari), often on a phone between classes and on a laptop the night before an exam.

Their job: understand each lecture slide by slide, then drill it until they can answer exam questions.

## Product Purpose

Fieldnotes turns the BIO103 lecture decks into a study space: each slide beside an explanation, then recall cards and practice drawn from the slides. Two lecture collections are included: Fall 2026, Prof. Dr. Md. Mahbubul Morshed (MBMD, 14 lectures, 411 slides), and Fall 2025, Prof. Dr. Md. Rakibul Islam (MRIs, 13 lectures, 439 slides).

Success means a student can open any lecture, understand it without the lecturer present, and walk into the exam ready for its question types.

## Positioning

Everything a student is tested on comes from their own lecturer's slides. Slide text, flashcards and practice questions are literal slide wording, traceable to a slide number. Explanations are written for every slide to make it understandable. They are labelled as explanations and never used as practice answers. A generic biology app or textbook cannot promise "this is exactly what your lecturer said".

## Operating Context

- Students work lecture by lecture, in the lecturer's slide order, and return to the same lecture several times before an exam.
- Exams mix multiple-choice questions with short answers: definitions, differences between two things (for example artery vs vein), and short explanations. Practice should cover both.
- Progress is kept in the browser, separately per semester. There are no accounts and no sync between devices.
- The app is self-hosted on the owner's homelab and may later be exposed to the internet.

## Capabilities and Constraints

- Per lecture: every slide as the original image, with its own text, tables, an explanation, and OCR text read from the image.
- Recall cards (term → slide wording) and practice questions (term, definition, fill-in), all generated from slide text by `scripts/build_course.py` and checked by `scripts/validate_course.py`. Short-answer practice is to be added from slide definitions and comparison tables.
- Original lecture files (PPTX, PDF) are downloadable.
- Content changes go through the extraction and build scripts, never by hand-editing `data/course-*.json`.
- Next.js 16, React 19, Lucide icons; one plain CSS file, no CSS framework or animation library; deployed as a Docker container.
- Undecided: whether the app will be public on the internet; if so, access control is needed because it serves the lecturers' files.

## Brand Commitments

- The name "fieldnotes" and its leaf mark.
- A forest-green identity (deep green brand colour family).
- The North South University logo, shown once rather than repeated.

## Evidence on Hand

- Fall 2026 lecture decks: `NSU Fall 2026/BIO103 MBMD/` (copies in `public/sources/fall2026/`).
- Fall 2025 lecture PDFs/PPTX and course outline: the folder containing this app (copies in `public/sources/`).
- Slide images: `public/slides-mbmd/`, `public/slides/`; Fall 2025 cover figures in `public/covers/`.
- NSU logo: `public/nsu-logo.svg`, `public/nsu-logo-full.svg`.
- No real usage data, testimonials or exam papers are on hand; none may be invented.

## Product Principles

1. The lecturer's slides are the source of truth. Anything written beyond them is labelled.
2. Understanding comes before drilling, but students are never locked out of practice.
3. The slide is the hero; interface chrome stays out of its way.
4. Practice matches the exam's real question types: MCQ, definitions, differences, short explanations.
5. A stranger with a shared link should know what to do within seconds.

## Accessibility & Inclusion

WCAG 2.2 AA. Readable on small phones and low-cost Windows laptops, with no text under 12px, 4.5:1 text contrast and 44px touch targets on phones. Fully keyboard-operable, with shortcuts for repetitive study actions. Respects reduced motion. Light and dark themes are equally complete.
