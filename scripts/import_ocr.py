#!/usr/bin/env python3
"""Import optional Apple Vision extraction; never replace verbatim text or practice."""
import argparse
import hashlib
import json
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('jsonl_files', nargs='+', type=Path)
args = parser.parse_args()
course_path = APP / 'data/course.json'
course = json.loads(course_path.read_text())
slides = {s['id']: s for m in course['modules'] + course['references'] for s in m['slides']}
records = {}
for file in args.jsonl_files:
    for line in file.read_text().splitlines():
        data = json.loads(line)
        path = Path(data['path'])
        sid = f'{path.parent.name}-{path.stem}'
        if data.get('error'):
            raise RuntimeError(f'OCR failed for {sid}: {data["error"]}')
        if sid not in slides:
            raise ValueError(f'OCR has unknown source slide: {sid}')
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == slides[sid]['imageSha256'], f'OCR visual changed: {sid}'
        records[sid] = {'slideId': sid, 'engine': 'Apple Vision VNRecognizeTextRequest accurate; language correction disabled',
                        'sourceImageSha256': digest, 'text': data['text'], 'blocks': data['blocks']}
        slides[sid]['ocrText'] = data['text']
        slides[sid]['ocrBlockCount'] = len(data['blocks'])
course['ocrNotice'] = 'Text recognized locally from original slide images. OCR may misread small labels or symbols; use the original slide to verify. Flashcards and quizzes use exact source text layers, not OCR.'
course['stats']['ocrPageCount'] = len(records)
(APP / 'data/source-ocr.json').write_text(json.dumps(records, ensure_ascii=False, indent=2))
course_path.write_text(json.dumps(course, ensure_ascii=False, indent=2))
print(json.dumps({'ocrSlides': len(records), 'blocks': sum(len(r['blocks']) for r in records.values())}))
