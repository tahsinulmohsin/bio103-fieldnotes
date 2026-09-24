import json

mods = json.loads(open("data/course-mbmd-raw.json").read())
for m in mods:
    print(f"=== Module {m['number']}: {m['title']} ({len(m['slides'])} slides) ===")
    for s in m["slides"][:3]:
        raw_snippet = s['rawText'].replace('\n', ' ')[:100]
        ocr_snippet = s.get('ocrText', '').replace('\n', ' ')[:100]
        print(f"  Slide {s['number']}: {s['title']}")
        print(f"    Raw: {raw_snippet}")
        print(f"    OCR: {ocr_snippet}")
