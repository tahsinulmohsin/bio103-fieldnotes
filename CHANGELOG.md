# Changelog

All notable changes to BIO103 Fieldnotes. Versions follow [Semantic Versioning](https://semver.org/); each release is a git tag (`vX.Y.Z`) with a GitHub release. The running version is shown in the app footer and reported by `GET /api/health`.

## [Unreleased]

### Added
- MIT license for the code and documentation. The lecture materials are excluded (see the README).

### Changed
- `deploy.sh` reads the server settings from an untracked `.deploy.env` (see `.deploy.env.example`) and prints the deployed version.
- The deployment notes and reverse-proxy configuration target https://fieldnotes.tahsinulmohsin.me. The proxy scripts take the tunnel ID and origin as arguments.

### Fixed
- The Nginx Proxy Manager route now reaches the app:
  - `deployment/compose.proxy.yaml` joins the app to the `bio103-ingress` network as `bio103-fieldnotes`; `deploy.sh` uses it when `DEPLOY_PROXY_NETWORK=1`.
  - `configure-nginx.py` checks the real container (`bio103-fieldnotes-app`) and that network before changing anything.
- The proxy scripts' backups in `deployment/private/` are no longer deleted by the next `deploy.sh`.
- Backups from two proxy-script runs in the same second no longer collide.

## [2.0.0] - 2026-09-26

A rebuild of the study flow, the content pipeline and the interface, live at https://fieldnotes.tahsinulmohsin.me.

### Added
- **An explanation for every slide**: all 411 Fall 2026 slides and 146 Fall 2025 slides, written in plain language beside the slide. Each is labelled as an explanation, the slide's own words are one tap away, and explanations are never used for flashcards or answers.
- **Read → Recall → Practise** for each lecture, with a numbered slide strip that shows what has been read. A slide counts as read after two seconds on screen or on Next.
- **Short-answer practice** (175 Fall 2026, 146 Fall 2025 prompts) in the shape of the written exam: "Write the differences between…", "What are the functions of…", "Define…". The model answer is the slide's literal text; students mark themselves.
- A **Mistakes** round for missed questions; missed recall cards come back once in the same round and can be reviewed on their own later.
- Keyboard shortcuts for reading (← →), recall (Space, ← →) and practice (1–4 / A–D, Enter).
- Contents search across lecture titles, slide titles and terms; a "Next up" card that resumes where you stopped.
- Version in the footer and in `/api/health`.
- CI (content validation, type check, build, health check) and browser QA scripts in `tools/ui-qa`.

### Changed
- **New interface, "Practical Notebook"**: the explanation sits on a ruled page with a red margin line beside the original slide on a plain page. Practice answers are marked with a tick or cross drawn in the margin. Atkinson Hyperlegible Next and Mono throughout, light and dark themes, and at least 44px touch targets on phones. Forest green is used only for the one forward action and for correct marks. See `DESIGN.md`.
- The Read view fits one laptop screen (the whole slide and the start of its explanation above the bottom bar at 1280×720 and up).
- Recall and Practise are always open; unread slides get a gentle nudge instead of a lock.
- **Content pipeline rewritten** as extract → build → validate (`scripts/`). Slide text keeps its bullet levels and tables, Symbol/Wingdings glyphs become readable characters, and the validator checks 31,000+ assertions.
- **Fair multiple-choice questions**: four options of the same kind, drawn from nearby slides; the answer and distractors never appear in the prompt; no option contains another; shared prompt words never single out the answer. 418 Fall 2026 and 374 Fall 2025 questions (1.0.0 had 3,414 and 2,116, many of them unfair).
- Slide notes are the slide's literal text. The 1.0.0 "polished" notes that mixed outside facts into the default view without a label were removed.
- Only a small index loads with the page; each lecture's content is a prerendered static JSON file fetched when it is opened.
- Routes are `#/lecture/<id>[/<slide>|/recall|/practise]`; 1.0.0 `#module/<id>` links still work.
- The container runs with a read-only root filesystem, all capabilities dropped and `no-new-privileges`. `deploy.sh` keeps the replaced image as a rollback until the next deploy.

### Removed
- Tailwind CSS and Motion. Styling is one plain CSS file and all motion is CSS, turned off under "reduce motion".

### Fixed
- "Which line describes…" questions where only some options showed a blank, which pointed at the answer (164 questions).
- Pages opened from a link kept the previous page's scroll position.
- Dark-theme button hover contrast, and touch targets under 44px on phones.

## [1.0.0] - 2026-09-25

The first version, built from 2026-09-22, with the Fall 2026 import added on 2026-09-25. It is recovered from the backup `bio103-before-fixes-2026-09-25.tar.gz`, taken before the 2.0.0 work began. That snapshot has the source code and course data but not the slide images or lecture files.

- Fall 2025 (MRIs) course: 13 lectures and 439 slides, plus the course outline as a reference. 167 flashcards and 2,116 generated multiple-choice questions.
- A first import of Fall 2026 (MBMD): 14 lectures, 411 slides, 298 flashcards and 3,414 questions, with a semester switch.
- Explanation-first flow with practice unlocked after reading, original slide images, local OCR shown as a labelled supplement, progress in the browser with export.
- Next.js 16, React 19, Tailwind CSS 4 and Motion. Standalone Docker image and reverse-proxy configuration.

[Unreleased]: https://github.com/tahsinulmohsin/bio103-fieldnotes/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/tahsinulmohsin/bio103-fieldnotes/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/tahsinulmohsin/bio103-fieldnotes/releases/tag/v1.0.0
