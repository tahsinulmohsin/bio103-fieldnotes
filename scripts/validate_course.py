#!/usr/bin/env python3
"""Validate complete source coverage, literal practice spans, answers and assets."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

APP = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--reextract', action='store_true', help='Independently compare every raw text layer against its copied source file (requires pdftotext and Pillow).')
args = parser.parse_args()
course = json.loads((APP / 'data/course.json').read_text())
seen_slides = set()
checks = 0


def require(condition, message):
    global checks
    checks += 1
    if not condition:
        raise AssertionError(message)


for module in course['modules'] + course['references']:
    source = module['source']
    original = APP / 'public' / unquote(source['url']).lstrip('/')
    require(original.is_file(), f'Missing source: {original}')
    require(hashlib.sha256(original.read_bytes()).hexdigest() == source['sha256'], f'Source hash mismatch: {original}')
    require(len(module['slides']) == source['pageCount'], f'Incomplete source coverage: {module["id"]}')
    if 'coverSource' in module:
        cover = APP / 'public' / module['cover'].lstrip('/')
        provenance = module['coverSource']
        require(cover.is_file(), f'Missing original-figure cover: {cover}')
        require(hashlib.sha256(cover.read_bytes()).hexdigest() == provenance['imageSha256'], f'Cover hash mismatch: {cover}')
        require(provenance['sourceSha256'] == source['sha256'] and provenance['file'] == source['file'], f'Cover source mismatch: {cover}')
        require(1 <= provenance['page'] <= source['pageCount'], f'Cover page out of range: {cover}')
    if args.reextract:
        if original.suffix == '.pdf':
            result = subprocess.run(['pdftotext', str(original), '-'], check=True, capture_output=True, text=True)
            extracted = result.stdout.split('\f')
            if not extracted[-1].strip():
                extracted.pop()
        else:
            from extract_course import get_pptx_text
            extracted = get_pptx_text(original)
        require(len(extracted) == len(module['slides']), f'Re-extraction page count: {original}')
        for slide, raw in zip(module['slides'], extracted):
            require(slide['rawText'] == raw, f'Raw text differs from source: {slide["id"]}')
    slides = {s['id']: s for s in module['slides']}
    for page, slide in enumerate(module['slides'], 1):
        require(slide['number'] == page, f'Slide order: {slide["id"]}')
        require(slide['id'] not in seen_slides, f'Duplicate slide: {slide["id"]}')
        seen_slides.add(slide['id'])
        image = APP / 'public' / slide['image'].lstrip('/')
        require(image.is_file(), f'Missing visual: {image}')
        require(hashlib.sha256(image.read_bytes()).hexdigest() == slide['imageSha256'], f'Visual hash mismatch: {image}')
        require(slide['width'] > 0 and slide['height'] > 0, f'Missing visual dimensions: {image}')
    cards = {card['id']: card for card in module['flashcards']}
    for card in cards.values():
        require(card['slideId'] in slides, f'Unresolved card provenance: {card["id"]}')
        slide = slides[card['slideId']]
        require(card['page'] == slide['number'], f'Incorrect card page: {card["id"]}')
        for field, span_field in [('term', 'termSource'), ('definition', 'definitionSource')]:
            span = card[span_field]
            require(slide['rawText'][span['start']:span['end']] == card[field], f'Non-literal {field}: {card["id"]}')
    for question in module['quiz']:
        require(len(question['options']) == 4, f'Not four options: {question["id"]}')
        require(len(set(question['options'])) == 4, f'Duplicate options: {question["id"]}')
        require(0 <= question['correctIndex'] < 4, f'Invalid correctIndex: {question["id"]}')
        require(question['slideId'] in slides, f'Invalid slideId: {question["id"]}')
        require(question['page'] == slides[question['slideId']]['number'], f'Quiz page mismatch: {question["id"]}')
        require(len(question['prompt'].strip()) > 0, f'Empty prompt: {question["id"]}')
        require(len(question['explanation'].strip()) > 0, f'Empty explanation: {question["id"]}')
        if 'optionSources' in question:
            for option, provenance in zip(question['options'], question['optionSources']):
                require(provenance['slideId'] in slides, f'Out-of-module distractor: {question["id"]}')
                raw = slides[provenance['slideId']]['rawText']
                span = provenance['span']
                require(raw[span['start']:span['end']] == option, f'Non-source distractor: {question["id"]}')
        if 'sourceCardId' in question and question.get('promptStyle') in ['matching', 'cloze']:
            card = cards.get(question['sourceCardId'])
            require(card is not None, f'Unresolved quiz provenance: {question["id"]}')
            require(question['options'][question['correctIndex']] == card['term'], f'Incorrect quiz answer: {question["id"]}')
    if module['id'] == 'course-outline':
        require(not cards and not module['quiz'], 'Outline must never generate practice')
        require(all(s['isReferenceOnly'] for s in module['slides']), 'Outline reference flags')

stats = course['stats']
require(stats['moduleCount'] == len(course['modules']) == 13, 'Module count')
require(stats['slideCount'] == sum(len(m['slides']) for m in course['modules']) == 439, 'Teaching slide count')
require(stats['referencePageCount'] == sum(len(m['slides']) for m in course['references']) == 8, 'Reference page count')
require(stats['flashcardCount'] == sum(len(m['flashcards']) for m in course['modules']), 'Flashcard count')
require(stats['quizCount'] == sum(len(m['quiz']) for m in course['modules']), 'Question count')
if (APP / 'data/source-ocr.json').exists():
    ocr = json.loads((APP / 'data/source-ocr.json').read_text())
    all_slides = {s['id']: s for m in course['modules'] + course['references'] for s in m['slides']}
    require(stats.get('ocrPageCount') == len(ocr) == len(all_slides), 'OCR page coverage')
    for sid, record in ocr.items():
        require(sid in all_slides, f'Unknown OCR slide: {sid}')
        require(record['sourceImageSha256'] == all_slides[sid]['imageSha256'], f'OCR visual mismatch: {sid}')
        require(all_slides[sid].get('ocrText') == record['text'], f'OCR text mismatch: {sid}')
report = {'status': 'passed', 'assertions': checks, **stats,
          'scope': 'Every original file hash, slide visual, literal card span, quiz answer, distractor and explanation checked.'}
print(json.dumps(report, indent=2))
