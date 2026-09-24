#!/usr/bin/env python3
"""Rebuild the course exclusively from the user-supplied local files.

Requires Python 3 + Pillow, pdftotext, pdfinfo, pdftoppm, and LibreOffice.
No network access, generative model, external textbook, or medical reference is used.
Text spans in flashcards are literal substrings of the recorded extraction.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import quote
from PIL import Image

APP = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path('/Users/tahsinulmohsin/NSU Fall 2026/BIO103 - Fall 2025 - MRIS')
MODULES = [
    ('introduction', 'Lecture 1-2 MRIs.pdf', 'Introduction to Biology', 'Lectures 1–2', 'Foundations', 3),
    ('chemistry', 'Lecture 3-5 MRIs.pdf', 'Chemistry of Life', 'Lectures 3–5', 'Foundations', 36),
    ('macromolecules', 'Lecture 6-9 MRIs.pdf', 'Biological Macromolecules', 'Lectures 6–9', 'Foundations', 6),
    ('molecular-biology', 'Lecture 10 MRIs.pdf', 'Central Dogma of Molecular Biology', 'Lecture 10–11', 'Cell & molecular biology', 6),
    ('cells', 'Lecture 11-13 MRIs.pdf', 'Cell Structure and Function', 'Lectures 11–13', 'Cell & molecular biology', 6),
    ('energy', 'Lecture 13-15 MRIs.pdf', 'Energy of Life', 'Lectures 13–15', 'Cell & molecular biology', 7),
    ('cell-division', 'Lecture 16 MRIs.pdf', 'Cellular Division', 'Lecture 16', 'Cell & molecular biology', 22),
    ('homeostasis', 'Lecture 17 Homeostasis.pdf', 'Homeostasis', 'Lecture 17', 'Human systems', 2),
    ('circulation', 'Lecture 18 Blood.pdf', 'Circulatory System', 'Lecture 18', 'Human systems', 3),
    ('digestion', 'Lecture 19 DigS MRIs.pdf', 'Digestive System', 'Lecture 19', 'Human systems', 5),
    ('respiration-excretion', 'Lecture 20_Respiratory _Excre.pdf', 'Human Respiratory and Excretion System', 'Lecture 20', 'Human systems', 8),
    ('nutrition', 'Lecture 21 Food _ Nutrition.pdf', 'Food and Nutrition', 'Lecture 21', 'Food & metabolism', 3),
    ('diabetes-lipids', 'Lecture 22_Diabetes_Lipid Profile.pptx', 'Diabetes & Lipid Profile', 'Lecture 22', 'Food & metabolism', 4),
]


def command(args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def split_pages(text):
    pages = text.split('\f')
    if not pages[-1].strip():
        pages.pop()
    return pages


def title_for(text, page):
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    lines = [x for x in lines if not re.fullmatch(r'\d{1,3}', x)]
    if not lines:
        return f'Source slide {page}'
    # A source heading is retained; no biological text is invented for illustrations.
    first = lines[0]
    return first if len(first) <= 110 else f'Source slide {page}'


def get_pptx_text(path):
    # OOXML paragraphs preserve table and group text as well as ordinary text boxes.
    import zipfile
    import xml.etree.ElementTree as ET
    ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
          'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
          'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
    with zipfile.ZipFile(path) as archive:
        rels = {r.attrib['Id']: r.attrib['Target'] for r in ET.fromstring(archive.read('ppt/_rels/presentation.xml.rels'))}
        pres = ET.fromstring(archive.read('ppt/presentation.xml'))
        result = []
        for sid in pres.find('p:sldIdLst', ns):
            target = rels[sid.attrib['{' + ns['r'] + '}id']]
            part = 'ppt/' + target.lstrip('/') if not target.startswith('/') else target.lstrip('/')
            root = ET.fromstring(archive.read(part))
            texts = [''.join(t.text or '' for t in p.findall('.//a:t', ns)) for p in root.findall('.//a:p', ns)]
            result.append('\n'.join(texts))
        return result


def literal_span(raw, requested):
    """Only whitespace differences are permitted when locating a curator-selected span."""
    words = re.split(r'\s+', requested.strip())
    pattern = r'\s+'.join(re.escape(w) for w in words)
    match = re.search(pattern, raw)
    if not match:
        raise ValueError(f'Source span not found: {requested!r}')
    return {'start': match.start(), 'end': match.end()}, match.group()


def extract_one(item, source_dir, work_dir, rerender):
    module_id, filename, title, lecture, category, cover = item
    original = source_dir / filename
    if not original.is_file():
        raise FileNotFoundError(original)
    sha = hashlib.sha256(original.read_bytes()).hexdigest()
    (APP / 'public/sources').mkdir(parents=True, exist_ok=True)
    shutil.copy2(original, APP / 'public/sources' / filename)
    pdf = original
    if original.suffix.lower() == '.pptx':
        pdf = work_dir / (original.stem + '.pdf')
        if not pdf.exists():
            command(['soffice', '--headless', '--convert-to', 'pdf:impress_pdf_Export:{"ExportHiddenSlides":{"type":"boolean","value":"true"}}', '--outdir', str(work_dir), str(original)])
        pages = get_pptx_text(original)
        layout_pages = split_pages(command(['pdftotext', '-layout', str(pdf), '-']))
        shutil.copy2(pdf, APP / 'public/sources' / pdf.name)
    else:
        pages = split_pages(command(['pdftotext', str(pdf), '-']))
        layout_pages = split_pages(command(['pdftotext', '-layout', str(pdf), '-']))
    count = int(re.search(r'^Pages:\s+(\d+)', command(['pdfinfo', str(pdf)]), re.M).group(1))
    assert len(pages) == count == len(layout_pages), (filename, count, len(pages))
    image_dir = APP / 'public/slides' / module_id
    image_dir.mkdir(parents=True, exist_ok=True)
    if rerender or len(list(image_dir.glob('*.webp'))) != count:
        with tempfile.TemporaryDirectory(prefix=module_id + '-', dir=work_dir) as render_dir:
            prefix = Path(render_dir) / 'page'
            command(['pdftoppm', '-jpeg', '-r', '150', '-scale-to', '1800', str(pdf), str(prefix)])
            for img in sorted(Path(render_dir).glob('page-*.jpg')):
                number = int(img.stem.split('-')[-1])
                with Image.open(img) as frame:
                    frame.save(image_dir / f'{number:03d}.webp', 'WEBP', quality=86, method=5)
    slides = []
    reference = module_id == 'course-outline'
    for index, raw in enumerate(pages):
        number = index + 1
        img_path = image_dir / f'{number:03d}.webp'
        with Image.open(img_path) as frame:
            width, height = frame.size
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', raw) if p.strip() and not re.fullmatch(r'\d{1,3}', p.strip())]
        slides.append({
            'id': f'{module_id}-{number:03d}', 'number': number,
            'title': title_for(layout_pages[index], number), 'rawText': raw,
            'paragraphs': paragraphs, 'image': f'/slides/{module_id}/{number:03d}.webp',
            'width': width, 'height': height, 'isReferenceOnly': reference,
            'textExtraction': 'pptx-ooxml' if original.suffix == '.pptx' else 'pdf-text-layer',
            'imageSha256': hashlib.sha256(img_path.read_bytes()).hexdigest(),
        })
    (work_dir / f'{module_id}.raw.json').write_text(json.dumps(pages, ensure_ascii=False, indent=2))
    source = {'file': filename, 'url': '/sources/' + quote(filename), 'sha256': sha,
              'kind': original.suffix.lstrip('.'), 'pageCount': count}
    if original.suffix == '.pptx':
        source['previewUrl'] = '/sources/' + quote(pdf.name)
    print(f'Extracted {filename}: {count} pages', flush=True)
    return {'id': module_id, 'title': title, 'lectureLabel': lecture, 'category': category,
            'description': ' · '.join(dict.fromkeys(s['title'] for s in slides[1:4])),
            'source': source, 'cover': f'/slides/{module_id}/{cover:03d}.webp',
            'slides': slides, 'flashcards': [], 'quiz': []}


def add_practice(module, specs):
    reviewed_options = json.loads((APP / 'scripts/practice_distractors.json').read_text())
    for i, spec in enumerate(specs):
        page, term, definition = spec
        slide = module['slides'][page - 1]
        try:
            term_span, literal_term = literal_span(slide['rawText'], term)
            def_span, literal_definition = literal_span(slide['rawText'], definition)
        except ValueError as exc:
            raise ValueError(f'{module["id"]}, slide {page}: {exc}') from exc
        module['flashcards'].append({
            'id': f'{module["id"]}-card-{i+1:02d}', 'term': literal_term,
            'definition': literal_definition, 'slideId': slide['id'], 'page': page,
            'termSource': term_span, 'definitionSource': def_span,
        })
    cards = module['flashcards']
    for index, card in enumerate(cards):
        alternatives = [other for other in cards if other['id'] != card['id'] and other['term'].lower() != card['term'].lower()]
        # Deterministic options make builds and validation reproducible; every distractor
        # is a literal term from this same source file, not an invented false fact.
        alternatives = alternatives[index % len(alternatives):] + alternatives[:index % len(alternatives)]
        distractors = alternatives[:3]
        question_id = f'{module["id"]}-quiz-{index+1:02d}'
        if question_id in reviewed_options:
            by_term = {' '.join(c['term'].split()): c for c in cards}
            distractors = [by_term[term] for term in reviewed_options[question_id]]
        correct = index % (len(distractors) + 1)
        selected = distractors[:]
        selected.insert(correct, card)
        term_pattern = r'(?<!\w)' + r'\s+'.join(re.escape(x) for x in card['term'].split()) + r'(?!\w)'
        prompt_quote, blanks = re.subn(term_pattern, '________', card['definition'], flags=re.I)
        question_stem = 'Which slide term completes this description?' if blanks else 'Which slide term matches this description?'
        module['quiz'].append({
            'id': question_id,
            'prompt': question_stem + '\n\n“' + prompt_quote + '”',
            'promptStyle': 'cloze' if blanks else 'matching',
            'options': [c['term'] for c in selected], 'correctIndex': correct,
            'explanation': card['definition'], 'slideId': card['slideId'], 'page': card['page'],
            'sourceQuote': card['definition'], 'sourceCardId': card['id'],
            'optionSources': [{'slideId': c['slideId'], 'page': c['page'], 'span': c['termSource']} for c in selected],
        })


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-dir', type=Path, default=DEFAULT_SOURCE)
    parser.add_argument('--work-dir', type=Path, default=APP.parent.parent / 'work/extraction')
    parser.add_argument('--rerender', action='store_true')
    args = parser.parse_args()
    args.work_dir.mkdir(parents=True, exist_ok=True)
    (APP / 'data').mkdir(exist_ok=True)
    outline = ('course-outline', 'BIO 103.38_outline_Fall 2025.pdf', 'Course outline', 'Fall 2025', 'Reference', 1)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(extract_one, item, args.source_dir, args.work_dir, args.rerender) for item in MODULES + [outline]]
        all_modules = [future.result() for future in futures]
    modules, references = all_modules[:-1], all_modules[-1:]
    specs = json.loads((APP / 'scripts/practice_spans.json').read_text())
    for number, module in enumerate(modules, 1):
        module['number'] = number
        add_practice(module, specs[module['id']])
    course = {
        'version': '1.0.0', 'title': 'NSU BIO103',
        'sourcePolicy': 'All biology content comes exclusively from the supplied NSU BIO103 files. Definitions and answer explanations are literal source text. Original slide images preserve diagrams and embedded labels. No external biology sources are used.',
        'extractionNotes': [
            'Page numbers refer to the PDF page or PPTX slide position; printed slide numbers may differ.',
            'Extracted text preserves source wording, spelling, symbols and line breaks. Diagrams and text embedded in images remain available in every original slide visual.',
            'The PPTX visuals are rendered by LibreOffice; editable slide text is extracted directly from its OOXML.',
            'The course outline is reference material only and does not generate practice.',
            'Module titles and categories organize the supplied topics; question stems are generic matching instructions and add no biology facts.',
        ],
        'stats': {'moduleCount': len(modules), 'slideCount': sum(len(m['slides']) for m in modules),
                  'referencePageCount': sum(len(m['slides']) for m in references),
                  'flashcardCount': sum(len(m['flashcards']) for m in modules),
                  'quizCount': sum(len(m['quiz']) for m in modules)},
        'modules': modules, 'references': references,
    }
    ocr_file = APP / 'data/source-ocr.json'
    if ocr_file.exists():
        ocr_records = json.loads(ocr_file.read_text())
        ocr_count = 0
        for module in modules + references:
            for slide in module['slides']:
                entry = ocr_records.get(slide['id'])
                if entry and entry['sourceImageSha256'] == slide['imageSha256']:
                    slide['ocrText'] = entry['text']
                    slide['ocrBlockCount'] = len(entry['blocks'])
                    ocr_count += 1
        course['ocrNotice'] = 'Text recognized locally from original slide images. OCR may misread small labels or symbols; use the original slide to verify. Flashcards and quizzes use exact source text layers, not OCR.'
        course['stats']['ocrPageCount'] = ocr_count
    cover_file = APP / 'data/covers.json'
    if cover_file.exists():
        cover_records = json.loads(cover_file.read_text())
        for module in modules:
            if module['id'] in cover_records:
                module.update(cover_records[module['id']])
    (APP / 'data/course.json').write_text(json.dumps(course, ensure_ascii=False, indent=2))
    print(json.dumps(course['stats']), flush=True)


if __name__ == '__main__':
    main()
