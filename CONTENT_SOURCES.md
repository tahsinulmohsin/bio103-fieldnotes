# NSU BIO103 content provenance

The app uses only the files supplied in `BIO103 - Fall 2025 - MRIS`. No biological explanations, definitions, answer facts, or diagrams were fetched from the internet or added from model knowledge. Slide wording, including the source's spelling and inconsistencies, is retained. Generic navigation, question instructions, and organizational labels are application copy.

## Complete coverage

| Local source | Teaching slides | Exact-source cards | Basic questions |
|---|---:|---:|---:|
| Lecture 1-2 MRIs.pdf | 33 | 16 | 206 |
| Lecture 3-5 MRIs.pdf | 65 | 17 | 345 |
| Lecture 6-9 MRIs.pdf | 74 | 14 | 205 |
| Lecture 10 MRIs.pdf | 27 | 10 | 71 |
| Lecture 11-13 MRIs.pdf | 44 | 13 | 167 |
| Lecture 13-15 MRIs.pdf | 37 | 11 | 156 |
| Lecture 16 MRIs.pdf | 41 | 12 | 137 |
| Lecture 17 Homeostasis.pdf | 13 | 9 | 97 |
| Lecture 18 Blood.pdf | 19 | 13 | 145 |
| Lecture 19 DigS MRIs.pdf | 25 | 15 | 197 |
| Lecture 20_Respiratory _Excre.pdf | 17 | 12 | 105 |
| Lecture 21 Food _ Nutrition.pdf | 22 | 12 | 163 |
| Lecture 22_Diabetes_Lipid Profile.pptx | 22 | 13 | 122 |
| **Total** | **439** | **167** | **2116** |

The separate eight-page `BIO 103.38_outline_Fall 2025.pdf` is available as reference material and generates no practice. All 447 pages have a rendered visual, including original diagrams, tables, labels, and image-embedded text. The PowerPoint includes four hidden slides: all 22 were exported and retained in their original order.

## How the app data was produced

- `data/course.json` records every teaching slide and reference page, original source filenames and SHA-256 hashes, exact extracted text, slide-image hashes, and practice provenance.
- `public/slides/` contains the complete source visuals as 1,800-pixel WebP images. PDF pages are rendered directly; PowerPoint slides are first rendered by LibreOffice with hidden-slide export enabled.
- `public/covers/` contains 13 separately extracted original figures for dashboard artwork. Eleven are embedded source images (including the cell image's original transparency mask); two are rendered diagram regions that preserve overlaid source labels. Their extraction methods, page positions, and hashes are recorded in `data/covers.json`.
- `public/sources/` contains unchanged copies of the 14 supplied files, plus the PowerPoint's rendered PDF for preview.
- `scripts/practice_spans.json` selects terms and definition spans from the supplied slides. Each generated card records character offsets into its slide's `rawText`. The card's term and definition are literal substrings, preserving wording and line breaks.
- Questions are deterministically generated matching or cloze exercises. When a definition contains its own answer term, that term is replaced with a blank in the prompt; the answer explanation retains the complete exact quotation. Correct answers, alternatives, and explanations all come from the same lecture's extracted source text. No false biological statements are invented as distractors.
- All 112 option sets were reviewed against their source associations. Fifteen sets use reviewed distractors from `scripts/practice_distractors.json` to avoid presenting an overlapping category, subtype, or closely related process as a competing answer.
- Text from figures can also be read directly in the original slide visuals. Local Apple Vision OCR extracted 9,038 text blocks from all 447 page images with language correction disabled. `data/source-ocr.json` preserves recognized text, confidence, geometry and source-image hashes; each slide exposes optional `ocrText`. OCR may misread small labels and is explicitly separate from exact source text. It is never used to create practice.

Page citations mean the one-based page/slide position in the source file. A source may display a different printed slide number.

## Reproduce and verify

From this application directory:

```sh
python3 scripts/extract_course.py --source-dir '/path/to/BIO103 - Fall 2025 - MRIS'
python3 scripts/extract_covers.py
python3 scripts/validate_course.py --reextract
```

Extraction requires Python 3, Pillow, Poppler (`pdftotext`, `pdfinfo`, `pdftoppm`) and LibreOffice. The basic `validate_course.py` check only needs Python's standard library; `--reextract` additionally uses the extraction dependencies to compare every recorded text layer against the copied source files. The application itself does not need these tools at runtime.

Validation checks source and visual hashes, complete ordered slide coverage, exact card substrings, correct quiz answer indexing, four distinct options, source-only distractors, source-only explanations, and the outline's exclusion from practice.
