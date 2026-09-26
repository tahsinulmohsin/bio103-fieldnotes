#!/usr/bin/env python3
"""Validate both semesters: source coverage and hashes, source-only notes, literal cards,
and fair quiz questions.

    python3 scripts/validate_course.py              # standard library only
    python3 scripts/validate_course.py --reextract  # also re-read every source file (needs Poppler + Pillow)

Fairness rules checked for every question (these are what the old generator broke):
- four distinct options of the same kind: four slide terms, or four slide descriptions;
- the answer never appears in the prompt, and no distractor appears in the prompt;
- no option contains another ("ER" vs "Rough ER");
- if a word of the answer shows in the prompt, at least two distractors share prompt words too;
- in "which line describes" questions, either every option has a blank or none does;
- the explanation is a literal line from the cited slide.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP / "scripts"))
from build_course import (BLANK, blank_term, complete, key, mentions, overlapping, plain,  # noqa: E402
                          stems, term_key, variants, ws)

EXPECTED = {
    "fall2025": {"modules": 13, "slides": 439, "references": 8},
    "fall2026": {"modules": 14, "slides": 411, "references": 0},
}

parser = argparse.ArgumentParser()
parser.add_argument("--reextract", action="store_true",
                    help="Re-read every copied source file and compare its text with the recorded extraction.")
args = parser.parse_args()
checks = 0


def require(condition, message):
    global checks
    checks += 1
    if not condition:
        raise AssertionError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reextracted(module: dict, original: Path) -> list[str] | None:
    if original.suffix == ".pdf":
        out = subprocess.run(["pdftotext", str(original), "-"], check=True, capture_output=True, text=True).stdout.split("\f")
        return out[:-1] if not out[-1].strip() else out
    if module["source"]["url"].startswith("/sources/fall2026/"):
        from extract_fall2026 import pptx_slides, raw_text
        ooxml = original if original.suffix == ".pptx" else APP / ".cache" / "fall2026" / f"{Path(module['source']['file']).stem}.pptx"
        if not ooxml.exists():
            print(f"  (skipped re-extraction of {original.name}: run extract_fall2026.py to create {ooxml.name})")
            return None
        return [raw_text(s) for s in pptx_slides(ooxml)]
    from extract_course import get_pptx_text
    return get_pptx_text(original)


def validate(semester: str) -> dict:
    course = json.loads((APP / "data" / f"course-{semester}.json").read_text())
    expected = EXPECTED[semester]
    require(course["semester"] == semester, f"{semester}: wrong semester field")
    all_cards = [c for m in course["modules"] for c in m["flashcards"]]
    card_keys = {term_key(v) for c in all_cards for v in variants(c["term"])}
    shown_defs = {key(blank_term(c["definition"], c["term"])[0]): c for c in all_cards}
    seen_slides: set[str] = set()
    hinted_questions = 0

    for module in course["modules"] + course["references"]:
        source = module["source"]
        original = APP / "public" / unquote(source["url"]).lstrip("/")
        require(original.is_file(), f"Missing source: {original}")
        require(sha(original) == source["sha256"], f"Source hash mismatch: {original}")
        if "previewUrl" in source:
            preview = APP / "public" / unquote(source["previewUrl"]).lstrip("/")
            require(preview.is_file(), f"Missing PDF preview: {preview}")
            if "previewSha256" in source:
                require(sha(preview) == source["previewSha256"], f"Preview hash mismatch: {preview}")
        require(len(module["slides"]) == source["pageCount"], f"Incomplete coverage: {module['id']}")
        if "coverSource" in module:
            cover = APP / "public" / module["cover"].lstrip("/")
            require(cover.is_file() and sha(cover) == module["coverSource"]["imageSha256"], f"Cover mismatch: {cover}")
        else:
            require((APP / "public" / module["cover"].lstrip("/")).is_file(), f"Missing cover: {module['cover']}")
        if args.reextract:
            pages = reextracted(module, original)
            if pages is not None:
                require(len(pages) == len(module["slides"]), f"Re-extraction page count: {original}")
                for slide, raw in zip(module["slides"], pages):
                    require(slide["rawText"] == raw, f"Raw text differs from source: {slide['id']}")

        slides = {s["id"]: s for s in module["slides"]}
        for page, slide in enumerate(module["slides"], 1):
            require(slide["number"] == page, f"Slide order: {slide['id']}")
            require(slide["id"] not in seen_slides, f"Duplicate slide: {slide['id']}")
            seen_slides.add(slide["id"])
            image = APP / "public" / slide["image"].lstrip("/")
            require(image.is_file() and sha(image) == slide["imageSha256"], f"Visual missing or changed: {image}")
            require(slide["width"] > 0 and slide["height"] > 0, f"Visual size: {image}")
            text = plain(slide["rawText"])
            # Notes and titles are the slide's own words; only whitespace, bullet glyphs and page numbers change.
            require(slide["title"] == f"Slide {page}" or ws(slide["title"]) in text, f"Title not from slide: {slide['id']}")
            for note in slide["notes"]:
                require(ws(note) in text, f"Note is not slide text: {slide['id']}: {note[:60]!r}")
            if "noteLevels" in slide:
                require(len(slide["noteLevels"]) == len(slide["notes"]), f"noteLevels length: {slide['id']}")
            require("extraNotes" not in slide, f"Old extraNotes field: {slide['id']}")
            if semester == "fall2026" and not slide["isReferenceOnly"]:
                require(len(slide.get("explanation", "").split()) >= 8, f"Missing explanation: {slide['id']}")
            for key_name in ("polishedExplanation", "polishedTitle"):
                require(key_name not in slide, f"Unlabelled generated text remains: {slide['id']}")

        cards = {c["id"]: c for c in module["flashcards"]}
        for card in cards.values():
            require(card["slideId"] in slides, f"Card slide: {card['id']}")
            slide = slides[card["slideId"]]
            require(card["page"] == slide["number"], f"Card page: {card['id']}")
            texts = (ws(slide["rawText"]), plain(slide["rawText"]))
            require(any(ws(card["term"]).lower() in t.lower() for t in texts), f"Card term not on slide: {card['id']}")
            require(any(ws(card["definition"]) in t for t in texts), f"Card definition not on slide: {card['id']}")
            if "termSource" in card:
                for field, span in (("term", card["termSource"]), ("definition", card["definitionSource"])):
                    require(ws(slide["rawText"][span["start"]:span["end"]]) == card[field], f"Span mismatch: {card['id']}")
            require(len(card["definition"].split()) >= 1, f"Empty definition: {card['id']}")
            require(key(card["definition"]) != key(card["term"]), f"Definition only repeats the term: {card['id']}")
            if semester == "fall2026":
                require(complete(card["definition"]), f"Definition cut off: {card['id']}: {card['definition'][-40:]!r}")

        for q in module["quiz"]:
            qid = q["id"]
            options = q["options"]
            require(len(options) == 4, f"Not four options: {qid}")
            require(0 <= q["correctIndex"] < 4, f"correctIndex: {qid}")
            require(len({key(o) for o in options}) == 4, f"Duplicate options: {qid}")
            require(q["slideId"] in slides and q["page"] == slides[q["slideId"]]["number"], f"Question slide: {qid}")
            raw = slides[q["slideId"]]["rawText"]
            require(ws(q["sourceQuote"]) in ws(raw) or ws(q["sourceQuote"]) in plain(raw), f"Explanation not slide text: {qid}")
            require(q["explanation"] == q["sourceQuote"], f"Explanation differs from quote: {qid}")
            require(q["sourceCardId"] in {c["id"] for c in all_cards}, f"Unknown source card: {qid}")
            answer = options[q["correctIndex"]]
            asked = q["prompt"] + " " + q.get("quote", "")
            if q["type"] in ("term", "cloze"):
                require(BLANK in q.get("quote", "") or q["type"] == "term", f"Cloze without blank: {qid}")
                for option in options:
                    require(term_key(option) in card_keys, f"Option is not a slide term: {qid}: {option!r}")
                for a in range(4):
                    for b in range(a + 1, 4):
                        require(not overlapping(options[a], options[b]), f"Overlapping options: {qid}")
                require(not mentions(q.get("quote", ""), answer), f"Answer shown in prompt: {qid}")
                for i, option in enumerate(options):
                    if i != q["correctIndex"]:
                        require(not mentions(q.get("quote", ""), option), f"Distractor shown in prompt: {qid}")
                words = stems(q.get("quote", ""))
                if stems(answer) & words:
                    hinted_questions += 1
                    sharing = sum(bool(stems(o) & words) for i, o in enumerate(options) if i != q["correctIndex"])
                    require(sharing >= 2, f"Answer is the only option sharing a prompt word: {qid}")
            elif q["type"] == "definition":
                card = next(c for c in all_cards if c["id"] == q["sourceCardId"])
                for option in options:
                    require(key(option) in shown_defs, f"Option is not a slide description: {qid}")
                    require(not mentions(option, card["term"]), f"Asked term appears in an option: {qid}")
                require(key(answer) == key(blank_term(card["definition"], card["term"])[0]), f"Wrong answer: {qid}")
                require(len({BLANK in o for o in options}) == 1, f"Only some options have a blank: {qid}")
                if stems(card["term"]) & stems(answer):
                    sharing = sum(bool(stems(card["term"]) & stems(o)) for i, o in enumerate(options) if i != q["correctIndex"])
                    require(sharing >= 2, f"Only the answer shares a word with the asked term: {qid}")
            else:
                require(False, f"Unknown question type: {qid}")
        for sa in module.get("shortAnswers", []):
            require(sa["slideId"] in slides and sa["page"] == slides[sa["slideId"]]["number"], f"Short answer slide: {sa['id']}")
            raw = slides[sa["slideId"]]["rawText"]
            texts = (ws(raw), plain(raw))
            answer = sa["answer"]
            parts = answer.get("points") or [c for row in answer.get("rows", []) for c in row if c] or [answer.get("text", "")]
            for part in parts:
                require(any(ws(part) in t for t in texts), f"Short-answer model answer is not slide text: {sa['id']}")
            require(sa["prompt"].strip().endswith((".", "?")), f"Short-answer prompt: {sa['id']}")
        if module["id"] == "course-outline":
            require(not cards and not module["quiz"], "The course outline must not generate practice")

    stats = course["stats"]
    require(stats["moduleCount"] == len(course["modules"]) == expected["modules"], f"{semester}: module count")
    require(stats["slideCount"] == sum(len(m["slides"]) for m in course["modules"]) == expected["slides"], f"{semester}: slide count")
    require(stats["referencePageCount"] == sum(len(r["slides"]) for r in course["references"]) == expected["references"], f"{semester}: references")
    require(stats["flashcardCount"] == len(all_cards), f"{semester}: flashcard count")
    require(stats["quizCount"] == sum(len(m["quiz"]) for m in course["modules"]), f"{semester}: question count")
    require(stats["shortAnswerCount"] == sum(len(m["shortAnswers"]) for m in course["modules"]), f"{semester}: short-answer count")
    require(stats["explanationCount"] == sum(1 for m in course["modules"] for s in m["slides"] if "explanation" in s), f"{semester}: explanation count")
    for m in course["modules"]:
        require(len(m["quiz"]) >= 5, f"{m['id']}: too few questions to practise")
    return {"semester": semester, **stats, "questionsWithSharedPromptWord": hinted_questions}


if semester_args := [a for a in sys.argv[1:] if not a.startswith("-")]:
    raise SystemExit("usage: validate_course.py [--reextract]")
reports = [validate(s) for s in EXPECTED]
if (APP / "data/source-ocr.json").exists():
    course = json.loads((APP / "data/course-fall2025.json").read_text())
    ocr = json.loads((APP / "data/source-ocr.json").read_text())
    slides = {s["id"]: s for m in course["modules"] + course["references"] for s in m["slides"]}
    for sid, record in ocr.items():
        require(sid in slides and record["sourceImageSha256"] == slides[sid]["imageSha256"], f"OCR visual mismatch: {sid}")
        require(slides[sid].get("ocrText") == record["text"], f"OCR text mismatch: {sid}")
print(json.dumps({"status": "passed", "assertions": checks, "semesters": reports}, indent=2))
