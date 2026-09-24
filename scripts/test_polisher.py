import json
import re

data = json.load(open('data/course.json'))
m = data['modules'][0]

def polish_slide(s, module):
    num = s['number']
    title = s['title']
    raw = s['rawText'].strip()
    ocr = s.get('ocrText', '').strip()
    
    # Specific curated polishes for key slides
    curated = {}
    
    curated[1] = {
        "title": "Introduction to Biology: Course Overview",
        "explanation": """**BIO 103: Introduction to Biology** serves as the foundational exploration into the science of living systems.

### Lecture Scope & Instructor
- **Course Series:** Lectures 1–2
- **Instructor:** Md. Rakibul Islam, PhD
- **Academic Focus:** Establishes core biological principles, structural hierarchies, the characteristics of life, and scientific classification."""
    }
    
    curated[2] = {
        "title": "The Scope & Definition of Biology",
        "explanation": """**Biology** is formally defined as the scientific study of life and living organisms, encompassing their structure, physiological mechanisms, chemical foundations, and evolutionary development.

### Scope & Core Biological Inquiries
The discipline explores how living systems arise, sustain themselves, and adapt to their environments, answering fundamental questions:
- **Physiological Mechanisms:** Why viral infections and common colds elevate body temperature (inducing fever).
- **Taxonomic Distinctions:** Why spiders belong to the class *Arachnida* rather than insects based on anatomical features.
- **Photosynthetic Adaptations:** Why plant foliage appears green due to specialized light-absorbing chlorophyll pigments.
- **Prebiotic Origins:** How prebiotic chemistry transitioned into self-replicating biological organisms."""
    }

    curated[3] = {
        "title": "Hierarchical Levels of Biological Organization",
        "explanation": """Living systems exhibit a hierarchical architecture spanning from subatomic particles to the global biosphere. Each ascending tier reveals **emergent properties** that do not exist at lower levels:

1. **Biosphere:** The global sum of all ecosystems; all regions of Earth's crust, waters, and atmosphere inhabited by living organisms.
2. **Ecosystem:** A biological community of interacting organisms together with their abiotic physical environment.
3. **Community:** Interacting populations of different species inhabiting a particular geographic area.
4. **Population:** A group of individuals belonging to the same species coexisting in a specific area.
5. **Organism:** An individual living being composed of coordinated organ systems.
6. **Organ System:** Two or more organs working cooperatively to carry out vital physiological tasks.
7. **Organ:** A specialized structural unit composed of distinct tissues working together for a specific function.
8. **Tissue:** A coordinated group of specialized cells with common structure and function.
9. **Cell:** The fundamental structural and functional unit of all life.
10. **Molecule:** The chemical union of two or more atoms bound together.
11. **Atom:** The smallest unit of matter, composed of protons, neutrons, and electrons."""
    }

    if num in curated:
        return curated[num]["title"], curated[num]["explanation"]
    
    # Clean title
    clean_title = re.sub(r'^\d+[\.\s]+', '', title).strip().rstrip(':')
    if not clean_title or clean_title.startswith('Source slide'):
        clean_title = f"Slide {num}: Key Concepts"
        
    return clean_title, raw

for num in [1, 2, 3]:
    s = m['slides'][num - 1]
    pt, pe = polish_slide(s, m)
    print(f"=== {pt} ===")
    print(pe)
    print()
