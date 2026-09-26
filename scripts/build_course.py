#!/usr/bin/env python3
"""Build the app's course files from the extracted lecture text.

    python3 scripts/build_course.py            # both semesters
    python3 scripts/build_course.py fall2026   # one semester

Input:  data/extracted/<semester>.json   (extract_course.py / extract_fall2026.py)
Output: data/course-<semester>.json      (read by the app and validate_course.py)

Everything a student studies from is either literal slide text or clearly labelled:
- `notes` are the slide's own text, re-flowed into bullets (whitespace and bullet glyphs only).
- `explanation` is written for each slide (scripts/explanations/<semester>/<topic>.json; Fall 2025
  also keeps its earlier hand-written notes). The app labels it as an explanation, not lecture
  text, and it is never used for flashcards or questions.
- `shortAnswers` are exam-style written prompts whose model answers are literal slide text
  (comparison tables, definitions, and question-titled slides).
- Flashcards are literal slide spans. Fall 2025 uses the curated spans; Fall 2026 cards are
  found from defining sentences and pruned by scripts/card_review_fall2026.json.
- Questions only ever put like against like: four terms, or four slide descriptions, all from
  the same lecture. See `make_questions` for the fairness rules.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import sys
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
SCRIPTS = APP / "scripts"
BLANK = "_____"

SEMESTERS = {
    "fall2025": {"title": "NSU BIO103", "label": "MRIS"},
    "fall2026": {"title": "NSU BIO103", "label": "MBMD"},
}

SOURCE_POLICY = (
    "Slide notes, flashcards and quiz questions use only the text of the supplied lecture files. "
    "Original slide images preserve diagrams and embedded labels. "
    "Each slide's explanation is written to make the slide understandable; it is labelled as an explanation "
    "and never used as a practice answer."
)

# --------------------------------------------------------------------------- text helpers

GLYPH = re.compile(r"^[\s•▪◦●■□➢➤►▶✓✔❖◆◇○\-–—*]+(?=\S)")
GLYPH_ONLY = re.compile(r"^[\s•▪◦●■□➢➤►▶✓✔❖◆◇○\-–—*]*$")
NUMBERED = re.compile(r"^\s*(?:\(?\d{1,2}[.)]|\(?[a-hivx]{1,4}\)|[a-h]\.)\s+")
INSTRUCTOR = re.compile(r"mahbubul|morshed|rakibul islam|prof\.?\s*dr\.?", re.I)
FUNCTION_WORDS = {"a", "an", "the", "and", "or", "of", "to", "in", "for", "with", "&", "between", "into", "on", "by", "from"}
# A line ending in one of these (or a comma / open bracket) continues on the next line.
CONTINUES = FUNCTION_WORDS | {"is", "are", "was", "were", "be", "called", "that", "which", "as", "at", "its",
                              "their", "e.g.", "e.g.,", "i.e.", "i.e.,", "such", "than", "then", "its", "whose"}


# Symbol / Wingdings / Webdings characters stored in the decks' private-use area, shown readably.
# Checked against the slide fonts and OCR (e.g. Webdings U+F0E8 is the circled P for a phosphate).
SYMBOLS = str.maketrans({
    "\uf0e0": "→", "\uf044": "→", "\uf0e8": "Ⓟ", "\uf0be": "—", "\uf0a2": "′", "\uf02d": "−",
    **{c: "•" for c in "\uf06c\uf071\uf0a4\uf0a7\uf0a8\uf097\uf0b7\uf0d8\uf076\uf0fc\uf06e\uf0a1"},
})


def ws(text: str) -> str:
    """Collapse whitespace and show symbol-font characters as readable Unicode."""
    return re.sub(r"\s+", " ", text.translate(SYMBOLS)).strip()


def key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def strip_glyph(text: str) -> str:
    return GLYPH.sub("", text).strip()


def continues(prev: str, nxt: str) -> bool:
    """True when `nxt` is the rest of a sentence the slide wrapped onto a new line."""
    if not prev or NUMBERED.match(nxt) or re.search(r"[.!?;:]$", prev):
        return False
    last = prev.split()[-1].lower()
    return nxt[:1].islower() or last in CONTINUES or prev.endswith((",", "(", "-", "–", "/"))


def is_noise(line: str) -> bool:
    t = ws(line)
    return not t or GLYPH_ONLY.match(t) is not None or re.fullmatch(r"\d{1,3}", t) is not None or INSTRUCTOR.search(t) is not None


def plain(raw: str) -> str:
    """Slide text without page numbers, lone bullet glyphs or instructor footers: what notes are cut from."""
    return ws(" ".join(strip_glyph(line) for line in raw.splitlines() if not is_noise(line)))


def pdf_title_and_items(raw: str, extracted_title: str, number: int) -> tuple[str, list[str]]:
    """Fall 2025 PDF text layer: re-flow wrapped lines into bullet items."""
    blocks = [b.splitlines() for b in re.split(r"\n\s*\n", raw) if b.strip()]
    title = ""
    if blocks and not extracted_title.startswith("Source slide"):
        first = blocks[0]
        start = 0
        while start < len(first) and is_noise(first[start]):
            start += 1
        take = start + 1
        title = ws(strip_glyph(first[start])) if start < len(first) else ""
        while title and take < len(first) and len(title) < 90 and not is_noise(first[take]) and (
            not re.search(r"[?.!:]$", title)
        ) and (
            first[take][:1].islower() or title.split()[-1].lower() in FUNCTION_WORDS or title.endswith((",", "–", "-"))
        ):
            title = ws(title + " " + first[take])
            take += 1
        blocks[0] = first[take:]
    items: list[str] = []
    for block in blocks:
        current = ""
        last_line = ""
        pending_break = False
        for line in block:
            if is_noise(line):
                # A lone bullet glyph means the next text line starts a new item.
                pending_break = pending_break or bool(line.strip() and GLYPH_ONLY.match(line.strip()))
                continue
            text = strip_glyph(line) if GLYPH.match(line) else line.strip()
            starts_item = not (current and continues(current, text)) and (
                pending_break
                or bool(GLYPH.match(line))
                or bool(NUMBERED.match(line))
                or (current and re.search(r"[.!?;:]$", current) and re.match(r"[A-Z0-9(“\"]", text))
                or (current and len(last_line.split()) <= 3 and not re.search(r"[,]$", last_line) and re.match(r"[A-Z]", text))
            )
            if current and not starts_item:
                current = ws(current + " " + text)
            else:
                if current:
                    items.append(current)
                current = ws(text)
            last_line = text
            pending_break = False
        if current:
            items.append(current)
    seen: set[str] = set()
    unique = []
    for item in items:
        if key(item) and key(item) not in seen:
            seen.add(key(item))
            unique.append(item)
    if not title and unique and len(unique[0]) <= 80:
        title = unique.pop(0)
    return (title.rstrip(":").strip() or f"Slide {number}"), unique


def pptx_title_and_items(slide: dict) -> tuple[str, list[str], list[int]]:
    """PowerPoint text: one item per paragraph, re-joining lines the author broke by hand."""
    lines: list[tuple[str, int]] = []
    for paragraph, level in zip(slide["sourceParagraphs"], slide["sourceLevels"]):
        for line in paragraph.split("\n"):
            if not is_noise(line):
                lines.append((ws(strip_glyph(line)), level))
    joined: list[list] = []
    for text, level in lines:
        if joined and joined[-1][1] == level and continues(joined[-1][0], text):
            joined[-1][0] = ws(joined[-1][0] + " " + text)
        else:
            joined.append([text, level])
    items, levels, seen = [], [], set()
    for text, level in joined:
        if key(text) and key(text) not in seen:
            seen.add(key(text))
            items.append(text)
            levels.append(level)
    title = ws(slide.get("sourceTitle", "")).rstrip(":").strip()
    if INSTRUCTOR.search(title):
        title = ""
    if not title and items and len(items[0]) <= 80:
        title = items.pop(0).rstrip(":").strip()
        levels.pop(0)
    top = min(levels, default=0)
    return title or f"Slide {slide['number']}", items, [min(lv - top, 2) for lv in levels]


def sentences(item: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(])", item) if s.strip()]


# --------------------------------------------------------------------------- term forms

def singular(word: str) -> str:
    w = word.lower()
    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 4 and w.endswith("es") and w[-3] in "sxz":
        return w[:-2]
    if len(w) > 3 and w.endswith("s") and not w.endswith(("ss", "us", "is", "sis")):
        return w[:-1]
    return w


def term_key(term: str) -> str:
    words = key(re.sub(r"\([^)]*\)", " ", term)).split()
    return " ".join(words[:-1] + [singular(words[-1])]) if words else ""


def variants(term: str) -> list[str]:
    """Surface forms a term can take in a sentence: itself, singular/plural, abbreviation."""
    forms = {ws(term)}
    base = ws(re.sub(r"\s*\([^)]*\)", "", term))
    forms.add(base)
    for abbr in re.findall(r"\(([^)]{1,12})\)", term):
        forms.add(abbr.strip())
    for f in list(forms):
        words = f.split(" ")
        last = words[-1]
        if not last:
            continue
        stem = singular(last)
        for alt in {stem, stem + "s", stem + "es", stem[:-1] + "ies" if stem.endswith("y") else stem + "s"}:
            forms.add(" ".join(words[:-1] + [alt]))
    # Short forms like "S" (the S phase) are kept only as the term itself, never as derived variants.
    return sorted((f for f in forms if len(f) >= 2 or f == ws(term)), key=len, reverse=True)


def term_pattern(term: str) -> re.Pattern:
    alts = "|".join(r"\s+".join(re.escape(p) for p in v.split(" ")) for v in variants(term))
    return re.compile(rf"(?<![A-Za-z0-9])(?:{alts})(?![A-Za-z0-9])", re.I)


def mentions(text: str, term: str) -> bool:
    return term_pattern(term).search(text) is not None


def blank_term(text: str, term: str) -> tuple[str, int]:
    return term_pattern(term).subn(BLANK, text)


def display_term(term: str) -> str:
    """Consistent option casing so capitalisation never hints at the answer."""
    words = []
    for w in ws(term).split(" "):
        letters = re.sub(r"[^A-Za-z]", "", w)
        words.append(w.capitalize() if len(letters) >= 5 and letters.isupper() else w)
    text = " ".join(words)
    return text[:1].upper() + text[1:]


def overlapping(a: str, b: str) -> bool:
    """True when one term is contained in the other (e.g. 'ER' and 'Rough ER')."""
    ka, kb = set(term_key(a).split()), set(term_key(b).split())
    return not ka or not kb or ka <= kb or kb <= ka


# --------------------------------------------------------------------------- flashcards

TERM_STOP = {
    "example", "examples", "eg", "e g", "note", "notes", "function", "functions", "type", "types",
    "figure", "fig", "ans", "answer", "question", "step", "steps", "source", "sources", "definition",
    "conclusion", "summary", "introduction", "objective", "objectives", "feature", "features",
    "characteristic", "characteristics", "importance", "advantage", "advantages", "disadvantage",
    "disadvantages", "reference", "references", "it", "this", "that", "these", "those", "there",
    "they", "he", "she", "we", "you", "which", "what", "who", "where", "when", "how", "why", "here",
    "each", "every", "all", "some", "most", "many", "one", "both", "such", "result", "results",
    "role", "roles", "cause", "causes", "symptom", "symptoms", "treatment", "sign", "signs",
    "structure", "process", "life", "part", "parts", "the", "a", "an", "main", "total", "other",
}
LEAD_STOP = {"it", "this", "that", "these", "those", "there", "they", "he", "she", "we", "you", "each",
             "every", "all", "some", "most", "many", "one", "both", "such", "here", "in", "on", "at",
             "for", "if", "when", "as", "because", "during", "after", "before", "without", "with",
             "its", "their", "our", "his", "her", "no", "not", "only", "also", "so", "then", "thus"}


BAD_TERM_START = re.compile(r"^(?:part|one|some|space|first|last|second|third|two|three|four|five|mainly|important|"
                            r"collectively|term|table|example|based|differ|common|three|several|many|most)\b", re.I)


def clean_term(term: str) -> str:
    term = NUMBERED.sub("", term.strip(" ,"))
    return re.sub(r"^(?:the|a|an)\s+", "", term, flags=re.I).strip()


def complete(definition: str) -> bool:
    """Reject spans the slide cut off mid-sentence."""
    d = definition.strip()
    last = d.split()[-1].lower() if d.split() else ""
    return (
        bool(d)
        and last not in CONTINUES
        and not d.endswith((",", "(", "-", ":", "–"))
        and d.count("(") == d.count(")")
    )


def good_term(term: str) -> bool:
    words = key(term).split()
    return (
        not BAD_TERM_START.match(term)
        and not re.search(r"\d", term)
        and
        1 <= len(words) <= 5
        and key(term) not in TERM_STOP
        and words[0] not in LEAD_STOP
        and words[-1] not in FUNCTION_WORDS
        and re.search(r"[A-Za-z]{2}", term) is not None
        and not re.match(r"^\d", term)
        and "slide" not in key(term)
    )


def card_candidates(module: dict) -> list[dict]:
    found = []
    for slide in module["slides"]:
        for item in slide["notes"]:
            # "Term: definition" / "Term – definition"
            m = re.match(r"^(?P<term>[A-Za-z][A-Za-z0-9 \-'’/()+,]{1,48}?)\s*(?::|\s[–—-]\s)\s*(?P<definition>\S.*)$", item)
            if m and good_term(clean_term(m["term"])):
                d = m["definition"].strip()
                if 4 <= len(d.split()) <= 45 and complete(d):
                    # "Taxonomy: Taxonomy is the science …" keeps the full sentence as the definition.
                    rank = 1 if key(d).startswith(key(clean_term(m["term"]))) else 0
                    found.append({"term": clean_term(m["term"]), "definition": d, "slide": slide, "rank": rank})
                    continue
            for sentence in sentences(item):
                if len(sentence.split()) < 6 or len(sentence.split()) > 45 or not complete(sentence):
                    continue
                # "The X is a/an/the …", "X are …", "X refers to …"
                m = re.match(
                    r"^(?:The |An |A )?(?P<term>[A-Za-z][A-Za-z0-9\-'’ ]{1,40}?)(?: \([A-Za-z0-9 ,]{1,12}\))? "
                    r"(?:is|are) (?:a|an|the|defined as)\b"
                    r"|^(?:The |An |A )?(?P<term2>[A-Za-z][A-Za-z0-9\-'’ ]{1,40}?) (?:refers to|means)\b",
                    sentence,
                )
                if m:
                    term = m["term"] or m["term2"]
                    if good_term(clean_term(term)):
                        found.append({"term": clean_term(term), "definition": sentence, "slide": slide, "rank": 1})
                # "… called X" / "… known as the X (ABC)"
                m = re.search(
                    r"\b(?:called|known as|termed|referred to as)\s+(?:the |a |an )?"
                    r"(?P<term>[A-Za-z][A-Za-z\-]*(?: [A-Za-z][A-Za-z\-]*){0,2})(?: \((?P<abbr>[A-Za-z]{2,6})\))?"
                    r"(?=\s*(?:[.,;:)&]|$|or\b|and\b|which\b|that\b))",
                    sentence,
                )
                if m and good_term(m["term"]) and not re.match(r"(?:the|a|an|this|that|it)\b", m["term"], re.I):
                    term = m["term"] + (f" ({m['abbr']})" if m["abbr"] else "")
                    found.append({"term": term, "definition": sentence, "slide": slide, "rank": 2})
    return found


def select_cards(module: dict, review: dict) -> list[dict]:
    rejected = {key(t) for t in review.get("reject", {}).get(module["id"], [])}
    rejected_defs = [ws(d) for d in review.get("rejectDefinitions", {}).get(module["id"], [])]
    best: dict[str, dict] = {}
    slides_by_number = {s["number"]: s for s in module["slides"]}
    added = []
    for page, term, definition in review.get("add", {}).get(module["id"], []):
        slide = slides_by_number[page]
        text = ws(slide["rawText"])
        if ws(term).lower() not in text.lower() or ws(definition) not in text:
            raise ValueError(f"{module['id']} slide {page}: reviewed card is not literal slide text: {term!r}")
        added.append({"term": ws(term), "definition": ws(definition), "slide": slide, "rank": -1})
    for c in added + card_candidates(module):
        k = term_key(c["term"])
        if key(c["term"]) in rejected or k in rejected or any(r and r in ws(c["definition"]) for r in rejected_defs):
            continue
        n = len(c["definition"].split())
        score = (c["rank"], 0 if 6 <= n <= 30 else 1, n)
        if k and (k not in best or score < best[k]["score"]):
            best[k] = {**c, "score": score}
    seen_defs: set[str] = set()
    cards = []
    for c in sorted(best.values(), key=lambda c: (c["slide"]["number"], c["score"])):
        if key(c["definition"]) in seen_defs:
            continue
        seen_defs.add(key(c["definition"]))
        cards.append(c)
    cards = cards[:30]
    return [
        {
            "id": f"{module['id']}-card-{i:02d}",
            "term": c["term"],
            "definition": c["definition"],
            "slideId": c["slide"]["id"],
            "page": c["slide"]["number"],
        }
        for i, c in enumerate(cards, 1)
    ]


# --------------------------------------------------------------------------- questions

def seeded(*parts: str) -> random.Random:
    return random.Random(int(hashlib.sha256("|".join(parts).encode()).hexdigest()[:12], 16))


def content_words(text: str) -> set[str]:
    return {w for w in key(text).split() if len(w) > 3 and w not in FUNCTION_WORDS}


def jaccard(a: str, b: str) -> float:
    x, y = content_words(a), content_words(b)
    return len(x & y) / max(1, len(x | y))


def stems(text: str) -> set[str]:
    return {singular(w) for w in key(text).split() if len(w) > 2 and w not in FUNCTION_WORDS}


def pick(rng: random.Random, ranked: list, n: int = 3) -> list:
    """Choose n from the closest candidates, with a little variety."""
    pool = ranked[: max(n + 3, 6)]
    rng.shuffle(pool)
    return pool[:n]


def arrange(rng: random.Random, correct, distractors: list) -> tuple[list, int]:
    options = distractors + [correct]
    rng.shuffle(options)
    return options, options.index(correct)


def make_questions(module: dict, pool: list[dict], overrides: dict[str, list[str]]) -> list[dict]:
    """
    Three kinds, all fair by construction:
      term        slide description (answer blanked) -> choose among four slide terms
      definition  term -> choose among four slide descriptions (each option's own term blanked)
      cloze       another slide sentence with a term blanked -> choose among four slide terms
    Rules: the answer never appears in the prompt; no distractor appears in the prompt;
    distractors never overlap the answer ("ER" vs "Rough ER"); cloze distractors never come
    from the same slide (they could also fit); options are cased consistently.
    """
    cards = module["flashcards"]
    slides = {s["id"]: s for s in module["slides"]}
    questions: list[dict] = []

    def term_distractors(card: dict, prompt: str, rng: random.Random, avoid_slide: dict | None = None,
                         plural: bool | None = None) -> list[str] | None:
        # If part of the answer shows in the prompt ("ribosomes" for "Bound ribosomes"),
        # distractors must share prompt words too, or the shared word gives the answer away.
        prompt_words = stems(prompt)
        hinted = bool(stems(card["term"]) & prompt_words)
        if card["id"] in overrides:
            chosen = overrides[card["id"]]
            if not any(mentions(prompt, t) for t in chosen) and (
                    not hinted or sum(bool(stems(t) & prompt_words) for t in chosen) >= 2):
                return chosen
        candidates = []
        for other in pool:
            t = other["term"]
            if other["id"] == card["id"] or overlapping(t, card["term"]) or mentions(prompt, t):
                continue
            if avoid_slide is not None and mentions(avoid_slide["rawText"], t):
                continue
            if any(overlapping(t, c) for c, _ in candidates):
                continue
            same_module = 0 if other["id"].startswith(module["id"] + "-") else 1
            plural_miss = 0 if plural is None else int(singular(key(t).split()[-1]) != key(t).split()[-1]) != int(plural)
            words = abs(len(t.split()) - len(card["term"].split()))
            # Nearby slides usually hold terms of the same kind (organs with organs, enzymes with enzymes).
            distance = abs(other["page"] - card["page"]) // 3 if not same_module else 99
            shares = 0 if (not hinted or stems(t) & prompt_words) else 1
            candidates.append((t, (shares, same_module, plural_miss, distance, words, abs(len(t) - len(card["term"])))))
        if len(candidates) < 3:
            return None
        ranked = [t for t, _ in sorted(candidates, key=lambda x: x[1])]
        if hinted:
            sharing = [t for t in ranked if stems(t) & prompt_words]
            if len(sharing) < 2:
                return None
            return pick(rng, sharing, 2) + [t for t in ranked if t not in sharing][:1] if len(sharing) == 2 else pick(rng, sharing)
        return pick(rng, ranked)

    def unique_display(options: list[str]) -> bool:
        keys = [term_key(o) for o in options]
        return len(set(keys)) == len(keys) and not any(
            overlapping(a, b) for i, a in enumerate(options) for b in options[i + 1:]
        )

    # 1. term from description
    for card in cards:
        quote, blanks = blank_term(card["definition"], card["term"])
        if mentions(quote, card["term"]) or len(key(quote).split()) < 3:
            continue
        rng = seeded(module["id"], card["id"], "term")
        distractors = term_distractors(card, quote, rng)
        if not distractors:
            continue
        options, correct = arrange(rng, display_term(card["term"]), [display_term(t) for t in distractors])
        if not unique_display(options):
            continue
        questions.append({
            "id": f"{card['id']}-term", "type": "term",
            "prompt": "Which term completes this line from the slides?" if blanks else "Which term does this slide describe?",
            "quote": quote, "options": options, "correctIndex": correct,
            "explanation": card["definition"], "sourceQuote": card["definition"],
            "slideId": card["slideId"], "page": card["page"], "sourceCardId": card["id"],
        })

    # 2. description from term
    def shown(c: dict) -> str:
        return blank_term(c["definition"], c["term"])[0]

    for card in cards:
        correct_text = shown(card)
        if mentions(correct_text, card["term"]):
            continue
        rng = seeded(module["id"], card["id"], "definition")
        n = len(correct_text)
        ranked = []
        for other in pool:
            if other["id"] == card["id"] or overlapping(other["term"], card["term"]):
                continue
            text = shown(other)
            if mentions(text, card["term"]) or mentions(text, other["term"]) or jaccard(text, correct_text) > 0.45:
                continue
            ratio = len(text) / max(1, n)
            if not 0.4 <= ratio <= 2.5:
                continue
            same_module = 0 if other["id"].startswith(module["id"] + "-") else 1
            distance = abs(other["page"] - card["page"]) // 3 if not same_module else 99
            ranked.append((text, (same_module, distance, abs(1 - ratio))))
        distinct = []
        for text, _ in sorted(ranked, key=lambda x: x[1]):
            if all(key(text) != key(t) and jaccard(text, t) <= 0.45 for t in distinct):
                distinct.append(text)
        # A blank marks where a description named its own term. Every option must match the right
        # answer in this, or the one line with (or without) a blank gives the answer away.
        blanked = BLANK in correct_text
        distinct = [t for t in distinct if (BLANK in t) == blanked]
        if len(distinct) < 3:
            continue
        # If the right description shares a word with the term ("water" for "Water soluble
        # vitamins"), two distractors must share one too, or the shared word gives it away.
        term_words = stems(card["term"])
        chosen = pick(rng, distinct)
        if term_words & stems(correct_text):
            sharing = [t for t in distinct if term_words & stems(t)]
            if len(sharing) < 2:
                continue
            others = [t for t in distinct if t not in sharing]
            chosen = pick(rng, sharing, 2) + (others[:1] if len(sharing) == 2 and others else [])
            chosen = chosen if len(chosen) == 3 else pick(rng, sharing)
        options, correct = arrange(rng, correct_text, chosen)
        questions.append({
            "id": f"{card['id']}-definition", "type": "definition",
            "prompt": f"Which line from the slides describes “{display_term(card['term'])}”?",
            "options": options, "correctIndex": correct,
            "explanation": card["definition"], "sourceQuote": card["definition"],
            "slideId": card["slideId"], "page": card["page"], "sourceCardId": card["id"],
        })

    # 3. cloze from other slide sentences
    used_per_card: dict[str, int] = {}
    used_per_slide: dict[str, int] = {}
    card_defs = {key(c["definition"]) for c in cards}
    for slide in module["slides"]:
        for item in slide["notes"]:
            for sentence in sentences(item):
                words = sentence.split()
                if not 7 <= len(words) <= 40 or key(sentence) in card_defs or sentence.endswith(":"):
                    continue
                # "Term: definition" lines are already asked as term questions.
                if any(key(d) and key(d) in key(sentence) for d in card_defs):
                    continue
                hits = [c for c in cards if mentions(sentence, c["term"])]
                if len(hits) != 1:
                    continue
                card = hits[0]
                if used_per_card.get(card["id"], 0) >= 2 or used_per_slide.get(slide["id"], 0) >= 3:
                    continue
                matches = list(term_pattern(card["term"]).finditer(sentence))
                if len(matches) != 1:
                    continue
                surface = matches[0].group(0)
                quote = sentence[: matches[0].start()] + BLANK + sentence[matches[0].end():]
                if len(key(quote).split()) < 6:
                    continue
                rng = seeded(module["id"], slide["id"], sentence)
                last = key(surface).split()[-1]
                plural = singular(last) != last
                distractors = term_distractors(card, quote, rng, avoid_slide=slide, plural=plural)
                if not distractors:
                    continue
                options, correct = arrange(rng, display_term(surface), [display_term(t) for t in distractors])
                if not unique_display(options):
                    continue
                used_per_card[card["id"]] = used_per_card.get(card["id"], 0) + 1
                used_per_slide[slide["id"]] = used_per_slide.get(slide["id"], 0) + 1
                questions.append({
                    "id": f"{slide['id']}-cloze-{used_per_slide[slide['id']]}", "type": "cloze",
                    "prompt": "Which term completes this line from the slides?",
                    "quote": quote, "options": options, "correctIndex": correct,
                    "explanation": sentence, "sourceQuote": sentence,
                    "slideId": slide["id"], "page": slide["number"], "sourceCardId": card["id"],
                })
    return questions


# --------------------------------------------------------------------------- extra notes (Fall 2025)

QUESTION_TITLE = re.compile(
    r"^(what|why|how|which|functions?|roles?|types?|kinds?|characteristics|features|properties|importance|"
    r"causes?|symptoms?|differences?|difference between|comparison|advantages?|stages?|steps?|phases?)\b",
    re.I,
)


def make_short_answers(module: dict) -> list[dict]:
    """Exam-style written prompts; every model answer is literal slide text."""
    items: list[dict] = []
    seen: set[str] = set()

    def add(kind: str, slide: dict, prompt: str, answer: dict) -> None:
        k = key(prompt)
        if k in seen:
            return
        seen.add(k)
        items.append({"id": f"{slide['id']}-{kind}-{len(items) + 1}", "type": kind, "prompt": prompt,
                      "answer": answer, "slideId": slide["id"], "page": slide["number"]})

    for slide in module["slides"]:
        # "Difference between A and B" tables: two named columns compared row by row.
        for table in slide.get("tables", []):
            head = [ws(c) for c in table[0]]
            rows = [[ws(c) for c in r] for r in table[1:] if any(ws(c) for c in r)]
            named = [h for h in head if h and not re.fullmatch(r"[\d.%\s]+", h)]
            comparison = re.search(r"differen|\bvs\.?\b|versus|compar", slide["title"], re.I)
            if comparison and len(head) == 2 and len(named) == 2 and len(rows) >= 2 and all(len(r) == 2 for r in rows):
                add("compare", slide, f"Write the differences between {named[0]} and {named[1]}.",
                    {"columns": head, "rows": rows})
            # Row-labelled comparisons: a blank corner cell, then two named columns (e.g. DNA | RNA).
            elif (len(head) == 3 and not head[0] and len(named) == 2 and len(rows) >= 3
                  and all(len(r) == 3 and r[0] for r in rows)):
                add("compare", slide, f"Compare {named[0]} and {named[1]}.",
                    {"columns": ["", named[0], named[1]], "rows": rows})
        # Question-shaped slide titles with a short list of points.
        title = ws(re.sub(r"\((?:cont|contd)[^)]*\)", "", slide["title"], flags=re.I))
        notes = [n for n in slide["notes"] if len(n.split()) >= 2]
        vague = (
            "…" in title or ".." in title
            or len(content_words(title)) < 2
            or re.search(r"\b(they|it|this|these|those|them)\b", title, re.I)
        )
        if QUESTION_TITLE.match(title) and not vague and 2 <= len(notes) <= 8 and not title.startswith("Slide "):
            prompt = title.rstrip(" .:?") + ("?" if title.lower().startswith(("what", "why", "how", "which")) else "")
            if not prompt.endswith("?"):
                prompt = f"Write short notes: {prompt}."
            add("points", slide, prompt, {"points": notes})
    # Definitions from the recall cards whose slide wording is a full definition.
    slides = {s["id"]: s for s in module["slides"]}
    for card in module["flashcards"]:
        if len(card["definition"].split()) >= 6:
            add("define", slides[card["slideId"]], f"Define {display_term(card['term'])}.",
                {"text": card["definition"]})
    return items


def written_explanations(semester: str) -> dict[str, dict[int, str]]:
    """Per-slide explanations written for a semester: scripts/explanations/<semester>/<topic>.json."""
    found: dict[str, dict[int, str]] = {}
    folder = SCRIPTS / "explanations" / semester
    for file in sorted(folder.glob("*.json")) if folder.exists() else []:
        data = json.loads(file.read_text())
        found[file.stem] = {int(n): text.strip() for n, text in data.items() if text and text.strip()}
    return found


def curated_extra_notes() -> dict[str, dict[int, str]]:
    sys.path.insert(0, str(SCRIPTS))
    from polished.mod01_intro import CURATED_SLIDES as INTRO
    from polished.mod04_central_dogma import CURATED_SLIDES as DOGMA
    from polished.mod08_homeostasis import CURATED_SLIDES as HOMEO
    from polished.mod13_diabetes_lipids import CURATED_SLIDES as DIABETES
    from polished.mod_systems import CIRCULATION_SLIDES, DIGESTION_SLIDES
    from polished.mod_all_curated import (CELLS_SLIDES, CHEMISTRY_SLIDES, DIVISION_SLIDES,
                                          ENERGY_SLIDES, MACROMOLECULES_SLIDES)
    table = {
        "introduction": INTRO, "chemistry": CHEMISTRY_SLIDES, "macromolecules": MACROMOLECULES_SLIDES,
        "molecular-biology": DOGMA, "cells": CELLS_SLIDES, "energy": ENERGY_SLIDES,
        "cell-division": DIVISION_SLIDES, "homeostasis": HOMEO, "circulation": CIRCULATION_SLIDES,
        "digestion": DIGESTION_SLIDES, "diabetes-lipids": DIABETES,
    }
    return {mid: {n: v["explanation"].strip() for n, v in slides.items()} for mid, slides in table.items()}


# --------------------------------------------------------------------------- build

def build(semester: str) -> dict:
    extracted = json.loads((APP / "data" / "extracted" / f"{semester}.json").read_text())
    extra = curated_extra_notes() if semester == "fall2025" else {}
    for topic, notes in written_explanations(semester).items():
        extra.setdefault(topic, {}).update(notes)
    review_file = SCRIPTS / f"card_review_{semester}.json"
    review = json.loads(review_file.read_text()) if review_file.exists() else {}
    overrides_raw = json.loads((SCRIPTS / "practice_distractors.json").read_text()) if semester == "fall2025" else {}
    overrides = {qid.replace("-quiz-", "-card-"): terms for qid, terms in overrides_raw.items()}

    def build_slide(slide: dict, module_id: str) -> dict:
        levels: list[int] = []
        if "sourceParagraphs" in slide:
            title, notes, levels = pptx_title_and_items(slide)
        else:
            title, notes = pdf_title_and_items(slide["rawText"], slide["title"], slide["number"])
        out = {
            "id": slide["id"], "number": slide["number"], "title": title, "notes": notes,
            "rawText": slide["rawText"], "image": slide["image"], "width": slide["width"],
            "height": slide["height"], "isReferenceOnly": slide["isReferenceOnly"],
            "imageSha256": slide["imageSha256"], "textExtraction": slide["textExtraction"],
        }
        if any(levels):
            out["noteLevels"] = levels
        if slide.get("tables"):
            out["tables"] = slide["tables"]
        if slide.get("ocrText"):
            out["ocrText"] = slide["ocrText"]
        note = extra.get(module_id, {}).get(slide["number"])
        if note:
            out["explanation"] = note
        return out

    modules = []
    for m in extracted["modules"]:
        slides = [build_slide(s, m["id"]) for s in m["slides"]]
        module = {k: v for k, v in m.items() if k not in ("slides", "flashcards")}
        module["slides"] = slides
        described = [s["title"] for s in slides[1:6] if not s["title"].startswith("Slide ") and key(s["title"]) != key(m["title"])]
        module["description"] = " · ".join(dict.fromkeys(described[:3]))
        if semester == "fall2025":
            module["flashcards"] = [{**{k: c[k] for k in ("id", "slideId", "page", "termSource", "definitionSource")},
                                     "term": ws(c["term"]), "definition": ws(c["definition"])}
                                    for c in m["flashcards"]]
        else:
            module["flashcards"] = select_cards(module, review)
        modules.append(module)

    for module in modules:
        same_category = [c for other in modules if other["category"] == module["category"] for c in other["flashcards"]]
        pool = module["flashcards"] + [c for c in same_category if c not in module["flashcards"]]
        module["quiz"] = make_questions(module, pool, overrides)
        module["shortAnswers"] = make_short_answers(module)

    references = []
    for r in extracted.get("references", []):
        ref = {k: v for k, v in r.items() if k not in ("slides", "flashcards")}
        ref["slides"] = [build_slide(s, r["id"]) for s in r["slides"]]
        ref["flashcards"], ref["quiz"], ref["shortAnswers"] = [], [], []
        references.append(ref)

    course = {
        "version": "3.0.0",
        "semester": semester,
        "title": SEMESTERS[semester]["title"],
        "term": extracted["term"],
        "instructor": extracted["instructor"],
        "institution": extracted.get("institution", "North South University"),
        "sourcePolicy": SOURCE_POLICY,
        "stats": {
            "moduleCount": len(modules),
            "slideCount": sum(len(m["slides"]) for m in modules),
            "referencePageCount": sum(len(r["slides"]) for r in references),
            "flashcardCount": sum(len(m["flashcards"]) for m in modules),
            "quizCount": sum(len(m["quiz"]) for m in modules),
            "explanationCount": sum(1 for m in modules for s in m["slides"] if "explanation" in s),
            "shortAnswerCount": sum(len(m["shortAnswers"]) for m in modules),
            "ocrPageCount": sum(1 for m in modules + references for s in m["slides"] if "ocrText" in s),
        },
        "modules": modules,
        "references": references,
    }
    out = APP / "data" / f"course-{semester}.json"
    out.write_text(json.dumps(course, ensure_ascii=False, indent=1))
    by_type: dict[str, int] = {}
    for m in modules:
        for q in m["quiz"]:
            by_type[q["type"]] = by_type.get(q["type"], 0) + 1
    print(f"{semester}: {json.dumps(course['stats'])} questions by type {by_type}")
    return course


if __name__ == "__main__":
    for sem in sys.argv[1:] or list(SEMESTERS):
        build(sem)
