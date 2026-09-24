import re

def clean_title(title: str, slide_num: int, ocr: str = "") -> str:
    t = (title or "").strip()
    
    # Strip leading bullets or numbers like "1. ", "5. ", "▪ "
    t = re.sub(r'^[•▪\-\*\d\.\s]+', '', t).strip()
    t = t.rstrip(':').rstrip()
    
    # Fix known fragmented slide titles
    replacements = {
        "Scopes": "The Scope & Definition of Biology",
        "What is Biology? (Cont.)": "Cellular Unity: Plant & Animal Cell Organization",
        "Scopes of Biology: (Cont…)": "Applied Scopes of Modern Biotechnology",
        "Only living things can produce offspring": "Reproduction: Passing Genetic Information",
        "Asexual": "Mechanisms of Asexual Reproduction",
        "Sexual Reproduction": "Sexual Reproduction & Fertilization Dynamics",
        "Differences between Sexual and Asexual reproduction are": "Differences Between Sexual and Asexual Reproduction",
        "Metabolism has two distinct": "Metabolic Pathways: Anabolism vs. Catabolism",
        "Taxonomy of living things": "Taxonomic Classification & The Tree of Life",
        "Source slide 30": "The Three Domains of Life (Phylogenetic Tree)",
        "Meet your human taxonomy": "Complete Taxonomic Hierarchy of Homo sapiens",
        "“You’re only here for a short visit. Don’t hurry, don’t": "Biological Stewardship & Life Appreciation",
        "Central Dogma of": "The Central Dogma of Molecular Biology",
        "Nuclear": "Nuclear Architecture & Chromatin Organization",
        "LOUIS PASTEUR": "Louis Pasteur & Germ Theory Foundation",
        "Source slide 4": "Microscopic Scale & Optical Resolution",
        "Source slide 5": "Comparative Dimensions of Cellular Structures",
        "Hypothalamus creates": "Hypothalamus & Osmoregulation (Thirst Reflex)",
        "Insulin secretion mechanism:                   Glucose Homeostasis": "Endocrine Glucose Regulation: Insulin Mechanism",
        "When you eat, your body breaks                 As blood glucose rises,": "Postprandial Blood Glucose & Insulin Response",
        "If insufficient/lack of insulin": "Pathophysiological Consequences of Insulin Deficiency",
        "Source slide 1": "Clinical Foundations of Diabetes & Lipid Profiles",
    }
    
    for key, repl in replacements.items():
        if t == key or t.startswith(key):
            return repl
            
    if not t or t.lower().startswith("source slide"):
        # Try inferring from first line of OCR
        if ocr:
            first_line = [l.strip() for l in ocr.split('\n') if len(l.strip()) > 3 and not l.strip().isdigit()]
            if first_line:
                candidate = first_line[0][:45].strip().rstrip(':')
                return candidate
        return f"Slide {slide_num}: Key Concept"
        
    return t

def format_bullet_points(lines):
    res = []
    for l in lines:
        l = l.strip()
        if not l:
            continue
        if re.match(r'^[•▪\-\*]\s*', l):
            cleaned = re.sub(r'^[•▪\-\*]\s*', '', l)
            res.append(f"- {cleaned}")
        elif re.match(r'^\d+[\.\)]\s*', l):
            cleaned = re.sub(r'^\d+[\.\)]\s*', '', l)
            res.append(f"1. {cleaned}")
        else:
            res.append(l)
    return res

def auto_polish_slide(slide: dict, module: dict) -> tuple[str, str]:
    num = slide["number"]
    title = clean_title(slide.get("title", ""), num, slide.get("ocrText", ""))
    raw = slide.get("rawText", "").strip()
    ocr = slide.get("ocrText", "").strip()
    
    # Identify associated flashcards
    cards = [c for c in module.get("flashcards", []) if c.get("slideId") == slide["id"]]
    # Identify associated quizzes
    quizzes = [q for q in module.get("quiz", []) if q.get("slideId") == slide["id"]]
    
    # De-hyphenate
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', raw)
    
    # Clean lines
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    # If text is too sparse, supplement with OCR
    if len(raw) < 70 and len(ocr) > len(raw):
        ocr_lines = [l.strip() for l in ocr.split('\n') if l.strip() and len(l.strip()) > 2]
        lines = ocr_lines
        
    # Build explanation blocks
    blocks = []
    
    # If cards exist, lead with them
    if cards:
        card_bullets = []
        for c in cards:
            card_bullets.append(f"- **{c['term']}:** {c['definition']}")
        blocks.append("### Key Definitions\n" + "\n".join(card_bullets))
        
    # Join non-bullet sentences into flowing prose
    flow_lines = []
    bullet_lines = []
    
    for l in lines:
        if l == slide.get("title", "").strip() or l == title:
            continue
        if re.match(r'^[•▪\-\*]\s*', l) or re.match(r'^\d+[\.\)]\s*', l):
            cleaned = re.sub(r'^[•▪\-\*\d\.\)]\s*', '', l)
            if cleaned:
                bullet_lines.append(f"- {cleaned}")
        else:
            flow_lines.append(l)
            
    if flow_lines:
        # Join short broken lines into cohesive sentences
        joined = " ".join(flow_lines)
        # Normalize multiple spaces
        joined = re.sub(r'\s+', ' ', joined).strip()
        if joined:
            blocks.insert(0, joined)
            
    if bullet_lines:
        blocks.append("### Core Takeaways\n" + "\n".join(bullet_lines[:8]))
        
    if quizzes and len(blocks) <= 1:
        quiz_note = quizzes[0].get("explanation", "").strip()
        if quiz_note:
            blocks.append(f"> **Lecture Insight:** {quiz_note}")
            
    explanation = "\n\n".join(blocks)
    if not explanation.strip():
        explanation = f"This slide presents the core visual evidence and diagrammatic framework for **{title}**. Study the original figure below for structural details."
        
    return title, explanation
