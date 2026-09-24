import json
import re

data = json.load(open('data/course.json'))

def clean_text(raw, ocr=''):
    raw = raw.strip()
    ocr = ocr.strip()
    
    # If raw text is too sparse but OCR exists, use OCR as primary or merge
    source = raw if len(raw) >= 60 else (ocr if ocr else raw)
    
    # Fix hyphenated words at linebreaks
    source = re.sub(r'(\w+)-\n(\w+)', r'\1\2', source)
    
    # Replace weird bullet chars
    source = source.replace('▪', '•').replace('–', '-').replace('—', '-')
    
    # Split by double newline or distinct bullet
    paragraphs = []
    lines = source.split('\n')
    current = []
    
    for line in lines:
        l = line.strip()
        if not l:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        
        # If starts with bullet or number
        if re.match(r'^(•|\-|\*|\d+\.)', l):
            if current:
                paragraphs.append(" ".join(current))
                current = []
            paragraphs.append(l)
        else:
            current.append(l)
            
    if current:
        paragraphs.append(" ".join(current))
        
    return paragraphs

for m in data['modules'][:3]:
    print(f"=== {m['title']} ===")
    for s in m['slides'][:3]:
        p = clean_text(s['rawText'], s.get('ocrText', ''))
        print(f"Slide {s['number']} ({s['title']}): {len(p)} blocks")
        for blk in p[:2]:
            print("  >", blk[:80])
