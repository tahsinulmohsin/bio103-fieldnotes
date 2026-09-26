---
target: BIO103 Fieldnotes UI
total_score: 23
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 3
target_identity: "file:/Users/tahsinulmohsin/NSU Fall 2026/BIO103 - Fall 2025 - MRIS/the-agentic-coding-prompt-act-as/outputs/bio103/components/study-app.tsx"
target_fingerprint: "sha256:7ca04334c9c26f7fc052019e785b3d615471a5f028336e872512475cb6404ef5"
target_path: /Users/tahsinulmohsin/NSU Fall 2026/BIO103 - Fall 2025 - MRIS/the-agentic-coding-prompt-act-as/outputs/bio103/components/study-app.tsx
timestamp: 2026-09-25T06-04-41Z
slug: components-study-app-tsx
---
⚠️ DEGRADED: single-context (design review and detector/browser evidence ran in one session, not two isolated sub-agents; the design review was finished from screenshots before the detector ran)

Target: BIO103 Fieldnotes app shell, lesson reader, flashcards, quiz, progress, sources (Fall 2026 and Fall 2025, light and dark, 1440px and 390px).

## Design Health Score (Nielsen)
| # | Heuristic | Score | Key issue |
|---|---|---|---|
| 1 | Visibility of system status | 3 | Progress bars and "reviewed" ticks are clear; topic loading is plain text, no skeleton |
| 2 | Match system / real world | 2 | Same progress called "explored", "unlocked" and "reviewed" on different screens |
| 3 | User control and freedom | 2 | Practice locked until every slide is clicked through (30 for Cells, 46 for Circulation) |
| 4 | Consistency and standards | 2 | Dark mode changes typeface and accent; 39 font sizes, 13 corner radii |
| 5 | Error prevention | 3 | Reset asks for confirmation; Check is disabled until a choice is made |
| 6 | Recognition rather than recall | 3 | Outline and slide references help; ALL-CAPS and "Slide N" titles slow scanning |
| 7 | Flexibility and efficiency | 1 | No shortcuts in cards or quiz, missed cards never return, search only matches titles |
| 8 | Aesthetic and minimalist design | 2 | Slogan heroes, 4 logos, ~10 small-caps labels per screen crowd out the study surface |
| 9 | Error recovery | 3 | Topic load error has Retry; wrong answers link back to the slide |
| 10 | Help and documentation | 2 | Unlock rule explained only in a hover tooltip and a small footnote |
| | **Total** | **23/40** | **Acceptable** |

## Design specificity
Partly authored. The original slide images, slide-literal notes and honest "not from your lecture" labelling are specific to this product. The frame around them is generic editorial template: every screen opens with the same small-caps label plus a two-line serif headline with an italic second line; small-caps labels, status dots and middle-dot separators are everywhere; the sidebar carries a motto. Nothing in the chrome is about biology or about studying (no next exam, no weak topics, no cards due).
Detector: 4 findings. Side-tab left borders at globals.css:1430, :3860, :4303 (the last is the quiz quote added last round); width transition at globals.css:658. No false positives. The larger problems (type scale, contrast, theme drift) came from browser measurement and axe, not the detector.

## Priority issues
1. [P1] The explanation layer is missing where it matters. Fall 2026 slides show only their own bullets; picture slides say "This slide teaches through its picture." Fall 2025's 146 explanations are collapsed and styled like a warning. For a study tool the explanation is the product. Fix: a first-class Explanation block beside every slide, written from that slide and labelled, open by default, with the slide's own text one tap away. Command: /impeccable shape.
2. [P1] Text is too small, unscaled and OS-dependent. 110 visible text elements under 12px on the dashboard (labels at 7-9px; 6-7px on phone); 39 font sizes in CSS; no web fonts load, so Windows/Android get Arial + Georgia and Mac Chrome shows serif headings in light but sans in dark. Georgia's old-style numerals render "0 / 14" as "O / 14" and "BIO 103" as "1o3". Light mode fails WCAG AA contrast in 83 places on the dashboard and 46 in a lesson (muted sage #66745f-#7c886c at 3.3-4.4:1). Fix: one family via next/font with lining figures, a 6-step scale (12/14/16/20/28/40), 16px body, nothing under 12px, muted text at 4.5:1 or more. Commands: /impeccable typeset, /impeccable polish.
3. [P1] Chrome crowds out the study surface. In a 1440px lesson the app sidebar (234px) and topic outline (220px) leave the slide image about 455px wide and the notes about 350px. The first ~300px of every screen is a slogan. The dashboard shows the NSU logo 4 times and the semester in 4 places. Fix: compact page titles, one logo, one semester switch, collapsible app nav in lessons, slide at 60%+ width with a sticky image beside the explanation. Commands: /impeccable distill, /impeccable layout.
4. [P2] Study-flow friction. Slides must be clicked through one by one, including title and thank-you slides; Recall/Practice look disabled. Cards and quiz have no keyboard shortcuts; "Needs another look" cards never come back; "Next question" falls below the fold at 900px; wrong-answer feedback repeats the whole option ("The answer is Many ribosomes are attached ... production..") and marks the wrong choice by colour only. Fix: mark slides read as they are viewed, practice always available with a nudge, Space/arrow/1-4 shortcuts, re-queue missed cards, sticky Check/Next bar, "Correct answer: C" plus an X icon. Commands: /impeccable shape, /impeccable clarify.
5. [P2] Dark mode is a different product. Headings switch typeface, the accent jumps from forest #24583b to neon mint #34d399 (bright CTA, neon italic headline). Built from 188 separate .dark overrides and 207 distinct hex values rather than token swaps. Fix: semantic tokens (surface, text, muted, accent, line) with one light/dark mapping that keeps the forest family. Command: /impeccable colorize.

## Persona red flags
- Alex, cramming the night before the midterm: 46 clicks through Circulation before one question; no shortcuts; search cannot find a term inside slide text; no "review my mistakes"; Progress shows totals, not weak topics.
- Casey, on an Android phone on the bus: 6-9px labels; targets under 44px (menu 26x35, theme 34x34, tabs 38px tall, "10 questions" 94x29); Next button at the bottom of a long page, not sticky; a Side-by-side/Stacked toggle that does nothing on a phone; semester pill wraps to two lines; continue-card thumbnail cropped mid-word ("TRODUCTION TO").
- Sam, low vision with a screen reader: 83 contrast failures in light mode; topic cards are buttons whose aria-label ("Open X") hides progress and card counts; navigation items are buttons, not links; wrong answers signalled by colour.

## Minor observations
- Outline rows overlap when a title wraps to three lines (Cells slide 11 over slide 12).
- "LATEST Fall 2026" wraps to two lines in the sidebar switch.
- Sticky top bar lets scrolled text show through in some renders.
- Fall 2026 covers are screenshots of text slides ("Take home points"), so the topic grid is 14 near-identical thumbnails.
- 5 `transition: all` rules; 53 hover rules with 1 gated behind (hover: hover).
- Reduced motion uses a global 0.01ms kill (globals.css:2995) that also removes useful state feedback.
- Tailwind is imported but effectively unused (one utility class in components) beside a 4,322-line stylesheet.

## Questions to consider
- What if the lesson reader were the home screen, opening straight to the next unread slide?
- Does a study tool need a hero at all, or would "Next up: Cells, slide 14 of 30" do more?
- What would the app look like if it had to fit a 13-inch Windows laptop with the slide readable without enlarging?
