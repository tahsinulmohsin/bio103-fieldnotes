---
version: 1
slug: "components-study-app-tsx"
primary_target: "components/study-app.tsx"
related_targets: ["components/home.tsx","components/lecture.tsx","components/recall.tsx","components/practise.tsx","components/pages.tsx","components/text.tsx","components/ui.tsx","app/globals.css"]
---

# Surface brief: Fieldnotes app (home, lecture reader, recall, practice, progress, sources)

Scope: the whole study app; mode: Operate (the lecture reader is Read-heavy inside it).
Audience and job: any NSU BIO103 student, on a phone or laptop, understanding a lecture slide by slide and drilling it for an exam that mixes MCQ with short answers.
Content: two semesters (Fall 2026 MBMD, 14 lectures, 411 slides; Fall 2025 MRIs, 13 lectures, 439 slides). Every slide has an image, its own text, and an explanation (Fall 2026 all slides; Fall 2025 146). Recall cards, MCQ and short-answer practice come from slide text only.
Constraints: keep "fieldnotes" + leaf, forest green, one NSU logo; WCAG 2.2 AA; light and dark equally complete; source-only rules from PRODUCT.md.

## Direction contract

THESIS: Every slide is a practical-copy spread: the lecturer's figure on the plain page, its explanation on the ruled page, answers marked in the margin. It refuses the LMS dashboard of cards and the cream-paper serif reader.

OWN-WORLD: Cool practical paper (#fbfcfa), pale blue-grey rules (#c9d5de) as dividers and a ruled margin column, a thin red margin line, pencil graphite text (#2b302d), forest-green ink (#1f5a3d) spent only on the one forward action and correct marks, red marking ink (#c8433a) only for corrections. Dark is the lab bench at night (#0e1512) in the same green family. One face family (Atkinson Hyperlegible Next, Mono for numbers and slide refs). 6px corners, hairline rules, no decorative shadows.

STORY: The student lands on "Next up", opens the spread at the next unread slide, reads figure plus explanation, steps with arrows, then recalls and practises; every answer is marked in the margin and misses come back.

FIRST VIEWPORT: Reader. Top: lecture title, stage switch (Read, Recall, Practise), numbered slide strip. Body: ruled page (explanation, slide text, OCR) about 40%, plain page (figure) about 60%. Bottom margin bar: previous, "14 / 30", green Next.

FORM: Practical Notebook, rank 4 of the ordered list, seed 4e74648e. Signature interaction: margin marking (a tick or cross drawn in the margin in 180ms, the tally kept in the margin column).

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
