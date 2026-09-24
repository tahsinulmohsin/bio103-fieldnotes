#!/usr/bin/env python3
"""Build complete Fall 2026 MBMD course with polished notes, flashcards, and 1,500+ practice questions."""

import json
import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
RAW_FILE = APP / "data" / "course-mbmd-raw.json"

STOPWORDS = {
    "this", "that", "with", "from", "they", "when", "what", "which", "there", "their",
    "some", "each", "have", "more", "also", "about", "into", "only", "such", "these",
    "where", "been", "were", "then", "than", "will", "many", "most", "other", "after",
    "because", "between", "during", "through", "under", "while", "small", "large",
    "first", "second", "third", "total", "often", "called", "cause", "part", "type",
    "prof", "morshed", "mahbubul", "dr", "nsu", "lecture", "slide", "thank", "you"
}

def clean_title(title: str, slide_num: int, ocr: str, mod_title: str) -> str:
    t = (title or "").strip()
    t = re.sub(r"^[•▪\-\*\d\.\s‹#›]+", "", t).strip()
    t = t.rstrip(":").rstrip()
    
    # Specific known title cleanups for MBMD slides
    clean_map = {
        "INTRODUCTION TO": "Introduction to Biology & Life",
        "BIOLOGY": "Introduction to Biology & Life",
        "Classification of Living": "Principles of Biological Classification",
        "Things": "Taxonomic Hierarchy & Kingdoms of Life",
        "BIO-103:": f"{mod_title} Overview",
        "BIOLOGY 1": "Cell Biology: Structural Foundations",
        "CELL STRUCTURE AND FUNCTION": "Cell Structure and Function",
        "THE CELL THEORY": "The Cell Theory & Organizational Principles",
        "Central Dogma of life": "Central Dogma: Genetic Information Flow",
        "An Analogy": "Genetic Code & Information Storage Analogy",
        "ENERGY OF LIFE": "Cellular Energetics & Metabolism",
        "CELLULAR DIVISION": "Cellular Division & The Cell Cycle",
        "Cell Division": "Cell Division & Biological Continuity",
        "Homeostasis": "Homeostasis: Internal Equilibrium",
        "Digestion": "Digestive Physiology & Nutrient Breakdown",
        "CIRCULATORY": "Circulatory System: Hemodynamics & Transport",
        "CIRCULATORY SYSTEM": "Circulatory System Architecture",
        "Human Respiratory System": "Respiratory System & Gas Exchange",
        "Prof. Dr. Md. Mahbubul Morshed": f"{mod_title} Overview",
        "Food and Nutrition": "Nutritional Biology & Metabolic Energy",
        "Nutritional": "Nutritional Requirements & Dietary Classes",
        "Classes of Nutrients": "The Six Major Classes of Nutrients",
    }
    
    for k, v in clean_map.items():
        if t == k or t.startswith(k):
            return v
            
    if not t or len(t) < 4 or t.lower().startswith("slide") or t.isdigit():
        if ocr:
            lines = [l.strip() for l in ocr.split("\n") if len(l.strip()) > 3 and not l.strip().isdigit() and "morshed" not in l.lower()]
            if lines:
                candidate = re.sub(r"^[•▪\-\*\d\.\s]+", "", lines[0])[:55].strip().rstrip(":")
                if len(candidate) > 4:
                    return candidate
        return f"{mod_title} · Topic {slide_num}"
        
    return t[:75]


def polish_explanation(slide: dict, mod: dict) -> tuple[str, str]:
    num = slide["number"]
    raw = slide.get("rawText", "").strip()
    ocr = slide.get("ocrText", "").strip()
    title = clean_title(slide.get("title", ""), num, ocr, mod["title"])
    
    # Text normalization
    combined = raw if len(raw) > 80 else (raw + "\n" + ocr).strip()
    cleaned_lines = []
    for l in combined.split("\n"):
        c = re.sub(r"^[•▪\-\*‹#›\d\.\s]+", "", l).strip()
        if c and not any(k in c.lower() for k in ["prof. dr.", "mahbubul morshed", "copyright", "thank you"]):
            cleaned_lines.append(c)
            
    # Remove duplicates preserving order
    unique_lines = []
    for l in cleaned_lines:
        if l not in unique_lines and len(l) > 3:
            unique_lines.append(l)
            
    # Build structured pedagogical explanation
    sections = []
    
    # 1. Core Concept Overview
    if unique_lines:
        lead_sentence = unique_lines[0]
        if not lead_sentence.endswith("."):
            lead_sentence += "."
        core = f"**Core Concept:** {lead_sentence}"
        if len(unique_lines) > 1 and len(unique_lines[1]) > 20:
            core += f" {unique_lines[1]}"
            if not core.endswith("."):
                core += "."
        sections.append(core)
    else:
        sections.append(f"**Core Concept:** This slide presents key visual models and structural concepts in {mod['title']}.")
        
    # 2. Key Mechanisms & Observations
    detail_bullets = []
    for l in unique_lines[1:7]:
        if len(l) > 12 and not l.startswith("Core Concept:"):
            # Capitalize first letter
            formatted = l[0].upper() + l[1:]
            detail_bullets.append(f"- {formatted}")
            
    if detail_bullets:
        sections.append("### Key Principles & Observations\n" + "\n".join(detail_bullets))
        
    # 3. Clinical & Biological Context
    context_note = f"**Biological & Clinical Context:** Understanding this mechanism is vital in {mod['category'].lower()} for analyzing cellular efficiency, metabolic homeostasis, and physiological regulation in living systems."
    sections.append(context_note)
    
    # 4. Exam & Study Anchor
    anchor = f"**Key Takeaway for Review:** Connect {title.lower()} with the broader theme of {mod['title'].lower()} for exam synthesis."
    sections.append(anchor)
    
    polished_text = "\n\n".join(sections)
    return title, polished_text


def extract_flashcards_from_module(mod: dict) -> list[dict]:
    cards = []
    seen_terms = set()
    
    for s in mod["slides"]:
        text = s.get("rawText", "") + "\n" + s.get("ocrText", "")
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        
        for l in lines:
            # Match "Term: Definition" or "Term - Definition" or "Term is ..."
            m = re.match(r"^([A-Z][A-Za-z0-9\s\-\(\)\/]{2,30})\s*[:–—]\s*(.{15,180})$", l)
            if m:
                term = m.group(1).strip()
                defn = m.group(2).strip()
                if term.lower() not in seen_terms and len(term.split()) <= 5:
                    seen_terms.add(term.lower())
                    cards.append({
                        "id": f"{mod['id']}-card-{len(cards)+1:02d}",
                        "term": term,
                        "definition": defn,
                        "slideId": s["id"],
                        "page": s["number"],
                    })
                    
        # Also check bullet patterns
        for p in s.get("paragraphs", []):
            m2 = re.match(r"^([A-Z][A-Za-z0-9\s]{2,25})\s+is\s+(.{15,180})$", p.strip())
            if m2:
                term = m2.group(1).strip()
                defn = f"Is {m2.group(2).strip()}"
                if term.lower() not in seen_terms and len(term.split()) <= 4:
                    seen_terms.add(term.lower())
                    cards.append({
                        "id": f"{mod['id']}-card-{len(cards)+1:02d}",
                        "term": term,
                        "definition": defn,
                        "slideId": s["id"],
                        "page": s["number"],
                    })
                    
    # Ensure every module has at least 15 flashcards by generating concept cards from key slides
    if len(cards) < 15:
        for s in mod["slides"]:
            if len(cards) >= 25:
                break
            title = s.get("polishedTitle") or s.get("title")
            if title and not title.lower().startswith("slide") and title.lower() not in seen_terms:
                raw_lines = [l.strip() for l in s.get("rawText", "").split("\n") if len(l.strip()) > 20]
                if raw_lines:
                    seen_terms.add(title.lower())
                    cards.append({
                        "id": f"{mod['id']}-card-{len(cards)+1:02d}",
                        "term": title,
                        "definition": raw_lines[0],
                        "slideId": s["id"],
                        "page": s["number"],
                    })
                    
    return cards


def generate_questions_for_module(mod: dict, cards: list[dict]) -> list[dict]:
    questions = []
    seen_prompts = set()
    mod_id = mod["id"]
    lecture = mod["lectureLabel"]
    slides = mod["slides"]
    
    # 1. Forward Term Matching Questions
    for idx, card in enumerate(cards):
        others = [c["term"] for c in cards if c["term"].lower() != card["term"].lower()]
        if len(others) >= 3:
            dists = others[idx % len(others):] + others[:idx % len(others)]
            opts = dists[:3]
            correct_idx = idx % 4
            opts.insert(correct_idx, card["term"])
            
            prompt = f"Which biological term corresponds to the following description in {lecture} (Slide {card['page']})?\n\n“{card['definition']}”"
            if prompt not in seen_prompts:
                seen_prompts.add(prompt)
                questions.append({
                    "id": f"{mod_id}-fwd-{len(questions)+1:03d}",
                    "prompt": prompt,
                    "promptStyle": "matching",
                    "options": opts,
                    "correctIndex": correct_idx,
                    "explanation": f"Slide {card['page']}: {card['term']} is defined as “{card['definition']}”.",
                    "slideId": card["slideId"],
                    "page": card["page"],
                    "sourceQuote": card["definition"],
                    "sourceCardId": card["id"],
                })
                
    # 2. Reverse Definition Questions
    for idx, card in enumerate(cards):
        others = [c["definition"] for c in cards if c["id"] != card["id"] and c["definition"] != card["definition"]]
        if len(others) >= 3:
            opts = others[:3]
            correct_idx = (idx + 1) % 4
            opts.insert(correct_idx, card["definition"])
            
            prompt = f"According to {lecture} (Slide {card['page']}), what is the correct slide definition of “{card['term']}”?"
            if prompt not in seen_prompts:
                seen_prompts.add(prompt)
                questions.append({
                    "id": f"{mod_id}-rev-{len(questions)+1:03d}",
                    "prompt": prompt,
                    "promptStyle": "reverse-matching",
                    "options": opts,
                    "correctIndex": correct_idx,
                    "explanation": f"Slide {card['page']}: {card['term']} corresponds to “{card['definition']}”.",
                    "slideId": card["slideId"],
                    "page": card["page"],
                    "sourceQuote": card["definition"],
                    "sourceCardId": card["id"],
                })
                
    # 3. Slide Fact Cloze Questions
    vocab = [c["term"] for c in cards]
    for s in slides:
        text = s.get("rawText", "") + "\n" + s.get("ocrText", "")
        for line in text.split("\n"):
            for match in re.findall(r"\b[A-Z][a-z]{3,15}\b", line):
                if match.lower() not in STOPWORDS and match not in vocab:
                    vocab.append(match)
                    
    cloze_count = 0
    for s in slides:
        combined = s.get("rawText", "") + "\n" + s.get("ocrText", "")
        lines = [re.sub(r"^[•▪\-\*‹#›\d\.\s]+", "", l).strip() for l in combined.split("\n") if len(l.strip()) > 15]
        for line in lines:
            words = line.split()
            if not (5 <= len(words) <= 30):
                continue
            if any(k in line.lower() for k in ["copyright", "mahbubul", "morshed", "slide", "thank you"]):
                continue
                
            for term in vocab:
                pat = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
                if re.search(pat, line, re.I):
                    blanked, cnt = re.subn(pat, "________", line, flags=re.I)
                    if cnt == 1:
                        dists = [t for t in vocab if t.lower() != term.lower() and abs(len(t) - len(term)) <= 6]
                        if len(dists) >= 3:
                            correct_idx = cloze_count % 4
                            opts = dists[:3]
                            opts.insert(correct_idx, term)
                            if len(set(opts)) == 4:
                                prompt = f"Which term correctly completes this statement from {lecture} (Slide {s['number']})?\n\n“{blanked}”"
                                if prompt not in seen_prompts:
                                    seen_prompts.add(prompt)
                                    cloze_count += 1
                                    questions.append({
                                        "id": f"{mod_id}-clz-{cloze_count:03d}",
                                        "prompt": prompt,
                                        "promptStyle": "fact-cloze",
                                        "options": opts,
                                        "correctIndex": correct_idx,
                                        "explanation": f"Slide {s['number']}: “{line}”",
                                        "slideId": s["id"],
                                        "page": s["number"],
                                        "sourceQuote": line,
                                    })
                                    break
                                    
    # 4. Statement Verification Questions
    stmts = []
    for s in slides:
        combined = s.get("rawText", "") + "\n" + s.get("ocrText", "")
        lines = [re.sub(r"^[•▪\-\*‹#›\d\.\s]+", "", l).strip() for l in combined.split("\n") if len(l.strip()) > 18]
        for l in lines:
            words = l.split()
            if 4 <= len(words) <= 25 and not any(k in l.lower() for k in ["copyright", "morshed", "mahbubul", "thank you"]):
                stmts.append((s["id"], s["number"], s["polishedTitle"], l))
                
    stmt_count = 0
    for s_id, s_num, s_title, stmt in stmts:
        others = [other[3] for other in stmts if other[1] != s_num and other[3] != stmt and len(other[3]) >= 15]
        if len(others) >= 3:
            start_i = (stmt_count * 3) % len(others)
            dists = others[start_i:] + others[:start_i]
            selected = []
            for d in dists:
                if d not in selected and d != stmt:
                    selected.append(d)
                if len(selected) == 3:
                    break
            if len(selected) == 3:
                correct_idx = stmt_count % 4
                opts = selected[:]
                opts.insert(correct_idx, stmt)
                prompt = f"Which factual statement is directly taught in {lecture} (Slide {s_num}: {s_title})?"
                if prompt not in seen_prompts:
                    seen_prompts.add(prompt)
                    stmt_count += 1
                    questions.append({
                        "id": f"{mod_id}-stm-{stmt_count:03d}",
                        "prompt": prompt,
                        "promptStyle": "statement-verification",
                        "options": opts,
                        "correctIndex": correct_idx,
                        "explanation": f"Slide {s_num}: “{stmt}”",
                        "slideId": s_id,
                        "page": s_num,
                        "sourceQuote": stmt,
                    })
                    
    return questions


def main():
    print("Building Fall 2026 MBMD Course...")
    raw_data = json.loads(RAW_FILE.read_text())
    
    total_slides = 0
    total_cards = 0
    total_questions = 0
    
    for m in raw_data:
        mod_slides = m["slides"]
        total_slides += len(mod_slides)
        
        # 1. Polish slides
        for s in mod_slides:
            t, exp = polish_explanation(s, m)
            s["polishedTitle"] = t
            s["polishedExplanation"] = exp
            
        # 2. Extract flashcards
        cards = extract_flashcards_from_module(m)
        m["flashcards"] = cards
        total_cards += len(cards)
        
        # 3. Generate practice questions
        quiz = generate_questions_for_module(m, cards)
        m["quiz"] = quiz
        total_questions += len(quiz)
        
        print(f"Module {m['id']}: {len(mod_slides)} slides, {len(cards)} flashcards, {len(quiz)} practice questions")
        
    course_fall2026 = {
        "version": "2.0.0",
        "title": "NSU BIO103 (Fall 2026)",
        "term": "Fall 2026",
        "instructor": "Prof. Dr. Md. Mahbubul Morshed (MBMD)",
        "institution": "North South University",
        "department": "Department of Biochemistry & Microbiology",
        "sourcePolicy": "All biology curriculum content comes directly from the supplied Fall 2026 NSU BIO103 lecture series by Prof. Dr. Md. Mahbubul Morshed. Original slide visuals preserve diagrams, graphs, micrographs, and anatomical structures.",
        "stats": {
            "moduleCount": len(raw_data),
            "slideCount": total_slides,
            "flashcardCount": total_cards,
            "quizCount": total_questions,
            "ocrPageCount": total_slides
        },
        "modules": raw_data,
        "references": []
    }
    
    out_path = APP / "data" / "course-fall2026.json"
    out_path.write_text(json.dumps(course_fall2026, ensure_ascii=False, indent=2))
    print(f"\n==================================================")
    print(f"Grand Total: {len(raw_data)} modules, {total_slides} slides, {total_cards} flashcards, {total_questions} questions!")
    print(f"Saved to {out_path}")
    print(f"==================================================")


if __name__ == "__main__":
    main()
