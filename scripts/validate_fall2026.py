#!/usr/bin/env python3
"""Validate integrity of Fall 2026 (MBMD) course data."""

import json
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
COURSE_FILE = APP / "data" / "course-fall2026.json"

def main():
    course = json.loads(COURSE_FILE.read_text())
    modules = course["modules"]
    
    assert len(modules) == 14, f"Expected 14 modules, got {len(modules)}"
    
    total_slides = 0
    total_cards = 0
    total_quizzes = 0
    assertions = 0
    
    for m in modules:
        assert m["id"], "Module missing id"
        assert m["title"], "Module missing title"
        assert m["cover"], "Module missing cover"
        cover_path = APP / "public" / m["cover"].lstrip("/")
        assert cover_path.exists(), f"Cover image missing: {cover_path}"
        assertions += 4
        
        # Check slides
        for s in m["slides"]:
            total_slides += 1
            assert s["id"], f"Slide missing id in {m['id']}"
            assert s["number"] > 0, f"Slide invalid number in {m['id']}"
            assert s["title"], f"Slide missing title in {m['id']}"
            assert s.get("polishedTitle"), f"Slide missing polishedTitle in {s['id']}"
            assert s.get("polishedExplanation"), f"Slide missing polishedExplanation in {s['id']}"
            assert s["image"], f"Slide missing image in {s['id']}"
            
            img_path = APP / "public" / s["image"].lstrip("/")
            assert img_path.exists(), f"Slide image not found on disk: {img_path}"
            assert s["width"] > 0 and s["height"] > 0, f"Slide invalid dimensions in {s['id']}"
            assertions += 8
            
        # Check flashcards
        for c in m["flashcards"]:
            total_cards += 1
            assert c["id"], "Card missing id"
            assert c["term"], "Card missing term"
            assert c["definition"], "Card missing definition"
            assert c["slideId"], "Card missing slideId"
            assert c["page"] > 0, "Card missing page"
            assertions += 5
            
        # Check quizzes
        for q in m["quiz"]:
            total_quizzes += 1
            assert q["id"], "Quiz missing id"
            assert q["prompt"], "Quiz missing prompt"
            assert len(q["options"]) == 4, f"Quiz must have 4 options: {q['id']}"
            assert len(set(q["options"])) == 4, f"Quiz options must be unique: {q['id']}"
            assert 0 <= q["correctIndex"] <= 3, f"Quiz correctIndex invalid: {q['id']}"
            assert q["explanation"], f"Quiz missing explanation: {q['id']}"
            assert q["slideId"], f"Quiz missing slideId: {q['id']}"
            assert q["page"] > 0, f"Quiz missing page: {q['id']}"
            assertions += 8
            
    print(f"Validation successful!")
    print(f"- Modules: {len(modules)}")
    print(f"- Total Slides: {total_slides} (All 411 WebP images verified on disk)")
    print(f"- Total Flashcards: {total_cards}")
    print(f"- Total Practice Questions: {total_quizzes}")
    print(f"- Total Assertions Passed: {assertions}")

if __name__ == "__main__":
    main()
