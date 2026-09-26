---
name: fieldnotes
description: BIO103 lecture slides as a practical-copy spread, with recall and practice marked in the margin.
colors:
  forest-ink: "#1f5a3d"
  forest-fill: "#1f5a3d"
  forest-fill-hover: "#17482f"
  on-forest: "#ffffff"
  right-ink: "#1d6b43"
  right-wash: "#e3f1e8"
  red-marking-ink: "#b3372c"
  red-wash: "#fbeae7"
  margin-red: "#d27a70"
  desk: "#eef1ec"
  practical-paper: "#fbfcfa"
  plain-page: "#ffffff"
  quiet-fill: "#f3f6f2"
  blue-grey-rule: "#d3dce2"
  blue-grey-rule-strong: "#aebdc8"
  graphite: "#1f2522"
  graphite-soft: "#3a433e"
  graphite-muted: "#56615b"
  focus-graphite: "#1f2522"
  selection-blue-grey: "#c9d5de"
  forest-ink-dark: "#8fd3ad"
  forest-fill-dark: "#2c7a52"
  forest-fill-hover-dark: "#256a48"
  right-ink-dark: "#8fd3ad"
  right-wash-dark: "#16301f"
  red-marking-ink-dark: "#f29a8f"
  red-wash-dark: "#3a1c19"
  margin-red-dark: "#8a4640"
  bench-night: "#0b100e"
  practical-paper-dark: "#121a16"
  plain-page-dark: "#0f1512"
  quiet-fill-dark: "#18221d"
  blue-grey-rule-dark: "#26342d"
  blue-grey-rule-strong-dark: "#3a4c43"
  graphite-dark: "#e7eee9"
  graphite-soft-dark: "#c6d1ca"
  graphite-muted-dark: "#97a69e"
  selection-blue-grey-dark: "#2d3d47"
typography:
  display:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, Segoe UI, Roboto, sans-serif"
    fontSize: "2rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, Segoe UI, Roboto, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "-0.015em"
  title:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, Segoe UI, Roboto, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 700
    lineHeight: 1.2
  body:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, Segoe UI, Roboto, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  prose:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, Segoe UI, Roboto, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.65
  label:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, Segoe UI, Roboto, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.55
  caption:
    fontFamily: "Atkinson Hyperlegible Next, system-ui, Segoe UI, Roboto, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 400
    lineHeight: 1.55
  numeral:
    fontFamily: "Atkinson Hyperlegible Mono, ui-monospace, Consolas, monospace"
    fontSize: "0.875rem"
    fontWeight: 400
    fontFeature: "tnum"
rounded:
  sm: "4px"
  md: "6px"
  lg: "10px"
spacing:
  s1: "4px"
  s2: "8px"
  s3: "12px"
  s4: "16px"
  s5: "20px"
  s6: "24px"
  s8: "32px"
  s10: "40px"
  s12: "48px"
  s16: "64px"
components:
  button-primary:
    backgroundColor: "{colors.forest-fill}"
    textColor: "{colors.on-forest}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "0 16px"
    height: "40px"
  button-primary-hover:
    backgroundColor: "{colors.forest-fill-hover}"
    textColor: "{colors.on-forest}"
  button-secondary:
    backgroundColor: "{colors.practical-paper}"
    textColor: "{colors.graphite}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "0 16px"
    height: "40px"
  button-quiet:
    backgroundColor: "transparent"
    textColor: "{colors.graphite-soft}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "0 8px"
    height: "32px"
  button-quiet-hover:
    backgroundColor: "{colors.quiet-fill}"
  sheet:
    backgroundColor: "{colors.practical-paper}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.lg}"
    padding: "20px 24px 24px"
  figure-page:
    backgroundColor: "{colors.plain-page}"
    rounded: "{rounded.lg}"
    padding: "16px"
  option:
    backgroundColor: "{colors.practical-paper}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.md}"
    padding: "8px 16px 8px 12px"
    height: "52px"
  option-selected:
    backgroundColor: "{colors.quiet-fill}"
    textColor: "{colors.graphite}"
  option-right:
    backgroundColor: "{colors.right-wash}"
  option-wrong:
    backgroundColor: "{colors.red-wash}"
  strip-cell:
    backgroundColor: "{colors.practical-paper}"
    textColor: "{colors.graphite-muted}"
    typography: "{typography.numeral}"
    rounded: "{rounded.sm}"
    size: "30px"
  strip-cell-read:
    backgroundColor: "{colors.blue-grey-rule}"
    textColor: "{colors.graphite-soft}"
  input-search:
    backgroundColor: "{colors.practical-paper}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.md}"
    padding: "0 16px 0 40px"
    height: "44px"
  answer-box:
    backgroundColor: "{colors.plain-page}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.md}"
    padding: "12px 16px"
    height: "132px"
  flash-card:
    backgroundColor: "{colors.practical-paper}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.lg}"
    height: "300px"
---

# Design System: fieldnotes

## Overview

**Creative North Star: "The Practical Notebook"**

Every lecture slide is a practical-copy spread. The explanation sits on the ruled page: cool practical paper with blue-grey hairline rules, a ruled margin column and a thin red margin line. The lecturer's figure sits on the plain white page beside it. Answers are marked in the margin, with a tick or cross drawn in pencil, green or red, like a teacher marking a lab copy. Everything else is graphite on paper on a pale desk. At night the same notebook sits on a dark lab bench in the same green family, and it is just as complete as the light theme.

The system is calm, dense where studying needs it, and flat. Hierarchy comes from weight, hairline rules and the margin column, not from colour or shadow. Colour is saved for meaning: forest green means "go forward" or "correct", red ink means "correction", and graphite covers everything else, including every current or selected state. One face family carries the whole app. Atkinson Hyperlegible Next is used for anything read, and its Mono sibling for slide numbers, counts and keys. Motion is CSS only, short, and removed under reduced motion.

The world rejects the LMS dashboard of cards and the cream-paper serif reader. It uses no decorative shadows, no pill shapes and no second accent colour.

**Key Characteristics:**
- Ruled sheet (explanation) beside the plain figure page (slide), sized to fit one laptop viewport.
- A 56px margin column with a red margin line carries slide numbers, the pencil read-tick, drawn ticks and crosses, and tallies.
- Graphite ink for all state; forest green only for the one forward action and correct marks; red ink only for corrections.
- One type family: Atkinson Hyperlegible Next, with Hyperlegible Mono for numerals.
- Flat paper surfaces with hairline borders and 6px corners (10px for sheets).

## Colors

The palette is cool practical paper and graphite, with two inks (forest green and red) that each carry exactly one meaning.

### Primary
- **Forest Fill** (forest-fill): the background of the one forward action on each screen: Next, Start reading / Continue at slide N, Got it, Had it, Show answer, Check / Next question. It deepens to **Forest Fill Hover** on hover. In dark mode it becomes a brighter forest fill, and the hover state darkens so white text stays above 4.5:1.
- **Forest Ink** (forest-ink): the leaf in the wordmark. In dark mode it becomes a pale mint so the leaf reads on the bench.
- **Right Ink** (right-ink) with **Right Wash** (right-wash): correct marks, the drawn tick, the "Correct" feedback heading, and the border and wash of a correct option.

### Secondary
- **Red Marking Ink** (red-marking-ink) with **Red Wash** (red-wash): corrections only. That covers the drawn cross, the "wrong" feedback heading, a wrong option's border and wash, and the missed-count on Home's "Needs another look" items.
- **Margin Red** (margin-red): the thin red margin line down every ruled sheet and the heading rule of the recall index card. It is a ruling, not a signal, so it is softer than the marking ink.

### Neutral
- **Desk** (desk): the app background behind the pages, the sticky top bar, and the bottom margin bar. In dark mode this is **Bench Night**.
- **Practical Paper** (practical-paper): ruled sheets, buttons, options, contents list, flash cards, inputs.
- **Plain Page** (plain-page): the figure page and the short-answer writing box. Slide images always sit on pure white, even in dark mode, because the lecturer's slides are white.
- **Quiet Fill** (quiet-fill): a quiet fill inside a page. Used for table headers, contents group rows, quoted slide lines, feedback panels, hover rows, and selected segment or option fills.
- **Blue-Grey Rule** (blue-grey-rule): every hairline divider and sheet border. It is also the shading of a read cell in the slide strip, like a pencilled-in box.
- **Blue-Grey Rule Strong** (blue-grey-rule-strong): the borders of controls (buttons, inputs, strip cells, option keys, `kbd`).
- **Graphite** (graphite): primary text, and every current or selected state (nav underline, stage underline, strip current outline, selected option ring, selected mode border).
- **Graphite Soft** (graphite-soft) and **Graphite Muted** (graphite-muted, 5.9:1 on paper): body prose and secondary text, then meta, counts, placeholders and captions.
- **Focus Graphite** (focus-graphite): the 2px focus ring, offset 2px.
- **Selection Blue-Grey** (selection-blue-grey): the text selection highlight.

### Named Rules
**The One Green Action Rule.** Forest fill appears on exactly one control per screen: the forward action. If two green buttons are visible, one of them is wrong. The only other greens are the correct mark and the wordmark leaf.

**The Red Pen Rule.** Red marking ink means "this was a miss" and nothing else. It never decorates, never marks the current state, and never styles a heading. The red margin line is a separate, softer ruling.

**The Graphite State Rule.** Current and selected states (nav, stage tabs, semester, practice mode, session size, strip current, selected option) use graphite ink: an underline, outline or ring, plus a quiet fill. They never use green.

## Typography

**Display Font:** Atkinson Hyperlegible Next (with system-ui, Segoe UI, Roboto, sans-serif)
**Body Font:** Atkinson Hyperlegible Next
**Label/Mono Font:** Atkinson Hyperlegible Mono (with ui-monospace, Consolas, monospace), for slide numbers, counts, option keys and keyboard hints

**Character:** A single face family built for legibility. Its open, distinct letterforms suit a stranger reading biology on a cheap laptop or a small phone. The Mono sibling gives numbers the tabular feel of a lab record.

### Hierarchy
- **Display** (700, 2rem, 1.2, -0.02em): the page title ("BIO103 · Fall 2026", Progress, Sources) and the recall card term. It drops to 1.5rem on phones.
- **Headline** (700, 1.5rem, 1.25, -0.015em): the lecture title, the slide title on the ruled sheet, the "Next up" lecture name, the practice prompt (line-height 1.3), and result headings. On phones it drops to 1.375rem for the lecture title and 1.25rem for the slide title and prompt.
- **Title** (700, 1.25rem, 1.2): section headings ("Needs another look", "Lectures") and the wordmark (-0.01em).
- **Body** (400, 1rem, 1.55): default UI text. **Prose** (1rem, 1.65, graphite soft, max 68ch) is used for explanations, with graphite-bold terms. Quoted slide lines on practice questions set at 1.125rem.
- **Label** (600, 0.875rem): buttons, nav, stage tabs, segmented controls, meta rows.
- **Caption** (400, 0.75rem): progress-line labels, provenance notes, the "/30" under a slide number, stage counts, `kbd`. This is the floor.
- **Numeral** (Mono, tabular numerals): every slide number, count and score, including inline ones inside a sentence.

### Named Rules
**The One Family Rule.** Atkinson Hyperlegible Next for words, Atkinson Hyperlegible Mono for numbers. There is no display face, no serif and no third family.

**The 12px Floor Rule.** No text is set below 0.75rem (12px), including captions, counts and keyboard hints.

## Layout

The app is a single column inside a centred wrap (max 1200px, padding 32px 24px 64px). The lecture reader widens to 1440px with a tighter top. Spacing follows a 4px base scale (4, 8, 12, 16, 20, 24, 32, 40, 48, 64). Sections are 48px apart.

**The spread.** The Read stage is a two-column grid: the ruled sheet (minmax(340px, 2fr)) beside the figure page (3fr), with a 20px gap. The figure page is sticky under the 56px top bar. Its image is capped at `max(240px, 100dvh − 380px)`, where 380px is the measured chrome (top bar, lecture header, strip, figure padding and caption, bottom bar). This keeps the whole spread and the Next button inside one viewport at 1440×900 and 1366×768. A sticky bottom margin bar holds Previous, "Slide 11 of 30" with arrow-key hints, and the green Next.

**The margin column.** Every ruled sheet is a grid with a 56px margin column (40px at ≤760px) and a 1px red margin line at its edge. The same column width indents the contents rows and the sources list, so lecture numbers line up with the margin across pages.

**Responsive.**
- At ≤1100px the course name and the contents "practice" column drop.
- At ≤900px the spread stacks, with the figure first and no longer sticky, and "Next up" stacks with its figure first.
- At ≤760px the top bar collapses to the wordmark plus a 44px menu button that opens a sticky sheet (nav, semester switch, theme). Every button, strip cell, segment and mode control becomes at least 44px. The figure caption hides and its Enlarge / Original actions move under the reading. Keyboard hints hide, and the bottom bar buttons stretch.

**The One Viewport Rule.** On a laptop, the slide, its explanation and the Next action must all be visible without scrolling the page. Any new chrome above the spread must be paid for by adjusting the 380px chrome allowance.

## Elevation & Depth

The system is flat. Depth comes from layered paper tones: desk, then paper, then the quiet fill inside a page. Hairline blue-grey borders separate surfaces, and state never lifts anything. Selected segments are marked with an inset 1px graphite or rule ring, and current tabs with an inset 2px underline. Only one element truly leaves the page: the enlarged-slide dialog.

### Shadow Vocabulary
- **Sheet lift** (`box-shadow: 0 12px 40px rgba(24, 38, 31, 0.18), 0 2px 8px rgba(24, 38, 31, 0.08)`; dark: `0 12px 40px rgba(0,0,0,0.55), 0 2px 8px rgba(0,0,0,0.35)`): only for the zoom dialog, over a 72% dark-green backdrop.

### Named Rules
**The Paper-Flat Rule.** Pages lie on the desk. The only shadow is for the modal enlarged slide, which is lifted off the desk. Use borders, rules and tonal fills for everything else.

## Shapes

Corners are gently squared: 6px for controls, options, inputs, feedback panels and figure thumbnails; 4px for small inner parts (segment buttons, strip cells, option keys, `kbd`, the slide image, the focus ring); 10px for whole sheets (ruled sheet, figure page, contents list, flash cards, tables, results). Borders are 1px hairlines everywhere. The exceptions are the 2px current-slide outline and the 2px red heading rule on index cards. The progress line is a 4px bar with 2px ends. Slide-text bullets are 5px dots, and nested levels use hollow rings. Nudges use a dashed 1px border to read as a pencilled note. No control is pill-shaped.

## Components

### Buttons
Quiet and paper-like. The only filled button is the green forward action.
- **Shape:** gently squared (6px), minimum height 40px (44px on phones), 16px side padding, 600-weight 14px label, icon gap 8px.
- **Primary:** forest fill with white text, one per screen. Hover deepens the fill.
- **Secondary:** practical paper with a strong blue-grey hairline and graphite text. Hover shifts the border to graphite muted.
- **Quiet:** no border or fill, graphite-soft text, 8px padding. Hover adds the quiet fill. Used for Enlarge / Original and small inline actions (32px, 44px on phones).
- **Press / Disabled:** 0.97 scale on press (120ms, ease-out, removed under reduced motion). Disabled drops to 45% opacity.
- **Focus:** 2px graphite ring, 2px offset.

### Segmented controls (semester, Explanation / Slide text)
- **Style:** a 2px-padded tray with a 6px outer and 4px inner radius. Unselected segments are graphite-muted text on transparent.
- **Selected:** graphite text on a quiet fill (semester) or a paper fill (text view), marked with a hairline ring. Never green.

### Cards / Containers (the ruled sheet)
- **Corner Style:** 10px.
- **Background:** practical paper, with a 1px blue-grey rule border.
- **Structure:** a 56px margin column and a red margin line, then a body padded 20px 24px 24px (16px on phones).
- **Shadow Strategy:** none (see Elevation & Depth).
- **Uses:** the Read explanation, "Next up" on Home, and every practice question.

### Inputs / Fields
- **Style:** practical paper (search) or plain page (short answer), with a strong blue-grey hairline and a 6px radius. Search is 44px tall with a 16px graphite-muted icon inset 12px. The answer box is at least 132px tall, resizes vertically, and has line-height 1.6.
- **Focus:** the global 2px graphite ring.
- **Placeholder:** graphite muted.

### Navigation
- **Top bar:** 56px, sticky, desk background, hairline bottom rule. It holds the wordmark (leaf in forest ink plus the bold 20px "fieldnotes"), the NSU logo and course name shown once, the semester switch, the text nav, and an icon theme toggle.
- **Nav links:** 600-weight 14px graphite soft. The current link is graphite with an inset 2px graphite underline.
- **Stage switch (Read / Recall / Practise):** 16px 600-weight tabs with mono counts. The current tab is graphite with a 2px graphite underline sitting on the lecture header's rule.
- **Mobile:** a menu button opens a sticky panel with 44px rows. The current row gets the quiet fill and a 2px graphite left rule.

### Slide strip
Every slide is a numbered 30px mono cell (44px on phones) with a 4px corner and a strong hairline. A read slide is shaded with the rule tone, like a pencilled-in box. The current slide has a 2px graphite outline and bold numeral. On phones the strip scrolls sideways and keeps the current cell centred.

### Practice options
Each option sits on its own ruled line. It is at least 52px tall (56px on phones), with a 28px mono key box, a hairline border and a 6px corner. A selected option gets a graphite border, an inset graphite ring and the quiet fill. After checking, a correct option gets a right-ink border with the right wash, and a wrong one gets the red ink border with the red wash. Feedback follows in a quiet-fill panel with a coloured heading and the literal slide line.

### Flash card (Recall)
An index card: 10px corners, a strong hairline border, a heading line ("Term" / "From slide N") over a 2px margin-red rule, the term centred at display size, and a footer over a blue-grey rule. It flips on Y in 320ms ease-out, and flips instantly when triggered from the keyboard. Under reduced motion it cross-fades instead. Again (secondary) and Got it (primary) sit below.

### Margin marking (signature)
A tick or cross drawn in the sheet's margin column like a teacher marking a practical copy. Marks are 28px stroked SVG paths (3px, round caps). They draw with stroke-dashoffset in 180ms ease-out, and the cross's second stroke follows 90ms later. A correct option's tick is centred in the margin beside that option. On Read, a graphite-muted 22px pencil tick (2.5px stroke) appears under the slide number once the slide is read. Tallies are 14px still marks (4px stroke) with mono counts, kept in the margin column of practice sheets. Recall is the accepted exception: the card is not a ruled sheet, so its tally sits in the deck header row. Under reduced motion the marks appear without drawing.

### Progress line
A 4px rule-toned track with a graphite-soft fill, scaled on X (never animated width) over 200ms ease-out. A caption row sits below it. It is instant under reduced motion.

## Do's and Don'ts

### Do:
- **Do** give each screen exactly one forest-fill button, the forward action.
- **Do** mark current and selected states in graphite: a 2px underline, a 2px outline or an inset ring, with the quiet fill.
- **Do** put numbers, ticks, crosses and tallies in the 56px margin column of a ruled sheet, and set every number in Atkinson Hyperlegible Mono with tabular numerals.
- **Do** keep the Read spread inside one laptop viewport. Adjust the 380px chrome allowance if chrome is added.
- **Do** use 6px corners for controls, 4px for inner parts and 10px for sheets, with 1px blue-grey hairlines.
- **Do** keep motion in CSS, under 320ms, ease-out `cubic-bezier(0.23, 1, 0.32, 1)`, and remove it under `prefers-reduced-motion`.
- **Do** make every interactive target at least 44px at ≤760px, and keep text at 12px or larger.
- **Do** ship light and dark together. Every token has a dark counterpart, and slide images stay on white.

### Don't:
- **Don't** use green for current, selected, focus or hover states, or for links.
- **Don't** use red marking ink for anything but a miss or a correction count.
- **Don't** add shadows to pages, cards, buttons or hover states. The zoom dialog is the only lifted surface.
- **Don't** use pill-shaped buttons, chips or badges.
- **Don't** introduce a second typeface, a serif reader face, or cream paper.
- **Don't** add an animation library or animate layout properties such as width or height. Use transform, opacity and stroke-dashoffset.
