#!/usr/bin/env python3
import json
from pathlib import Path

raw_modules = json.loads(Path("data/course-mbmd-raw.json").read_text())
ocr_lines = [json.loads(l) for l in Path("data/mbmd-ocr.jsonl").read_text().splitlines() if l.strip()]

ocr_by_relpath = {}
for entry in ocr_lines:
    p = Path(entry["path"])
    key = f"{p.parent.name}/{p.name}"
    ocr_by_relpath[key] = entry

matched = 0
for m in raw_modules:
    for s in m["slides"]:
        num = s["number"]
        key = f"{m['id']}/{num:03d}.webp"
        if key in ocr_by_relpath:
            rec = ocr_by_relpath[key]
            s["ocrText"] = rec["text"]
            s["ocrBlockCount"] = len(rec["blocks"])
            matched += 1

total = sum(len(m["slides"]) for m in raw_modules)
print(f"Matched OCR for {matched} / {total} slides.")
Path("data/course-mbmd-raw.json").write_text(json.dumps(raw_modules, ensure_ascii=False, indent=2))
