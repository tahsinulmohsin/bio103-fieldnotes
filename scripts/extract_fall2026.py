#!/usr/bin/env python3
"""Extract the Fall 2026 (MBMD) lecture decks exclusively from the supplied files.

Requires Python 3 + Pillow, Poppler (pdfinfo, pdftoppm) and LibreOffice.
Editable slide text is read from each deck's OOXML; the legacy .ppt deck is first
converted to .pptx by LibreOffice. Visuals are rendered from LibreOffice's PDF export.
Output: data/extracted/fall2026.json (no notes, flashcards or questions; see build_course.py).
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
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

APP = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = APP.parents[3] / "BIO103 MBMD"
PUBLIC_SOURCES = APP / "public" / "sources" / "fall2026"
SLIDE_DIR = APP / "public" / "slides-mbmd"
OCR_FILE = APP / "data" / "mbmd-ocr.jsonl"
OUT_FILE = APP / "data" / "extracted" / "fall2026.json"

# (id, file, title, lecture label, category, cover slide)
MODULES = [
    ("intro-biology", "Lec-1,2_Introduction to Biology+Life (3).pptx", "Introduction to Biology & Life", "Lectures 1–2", "Foundations", 1),
    ("classification", "L - 3 Classification of Living Things.pptx", "Classification of Living Things", "Lecture 3", "Foundations", 2),
    ("chemistry", "Lec-4,5_Chemistry of life.pptx", "Chemistry of Life", "Lectures 4–5", "Foundations", 2),
    ("macromolecules", "Lec-6,7_Biological macromolecules.pptx", "Biological Macromolecules", "Lectures 6–7", "Foundations", 2),
    ("cells", "Lec-8,9_Cells.ppt", "Cell Structure and Function", "Lectures 8–9", "Cell & molecular biology", 2),
    ("central-dogma", "Lec-10_CDL.pptx", "Central Dogma of Life", "Lecture 10", "Cell & molecular biology", 2),
    ("energy", "Lec-11,12_Energy of Life.pptx", "Energy of Life", "Lectures 11–12", "Cell & molecular biology", 2),
    ("cell-cycle", "Lec-13,14_Cell Cycle.pptx", "Cell Cycle & Cellular Division", "Lectures 13–14", "Cell & molecular biology", 2),
    ("homeostasis", "Lec-15_Homeostasis.pptx", "Homeostasis", "Lecture 15", "Human systems", 2),
    ("digestion", "Lec-16_digestion.pptx", "Digestive System", "Lecture 16", "Human systems", 2),
    ("circulation", "Lec-17_Circulatory System.pptx", "Circulatory System", "Lecture 17", "Human systems", 2),
    ("respiration-excretion", "Lec-18_Respiratory & Excretory System.pptx", "Human Respiratory & Excretory System", "Lecture 18", "Human systems", 2),
    ("diabetes-lipids", "Lec-19_Diabetes_LP.pptx", "Diabetes & Lipid Profile", "Lecture 19", "Food & metabolism", 2),
    ("nutrition", "Lec-20_Food & Nutrition.pptx", "Food and Nutrition", "Lecture 20", "Food & metabolism", 2),
]

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
SKIPPED_PLACEHOLDERS = {"sldNum", "dt", "ftr", "hdr"}
TITLE_PLACEHOLDERS = {"title", "ctrTitle"}


def find_soffice() -> str:
    for candidate in (shutil.which("soffice"), "/Applications/LibreOffice.app/Contents/MacOS/soffice"):
        if candidate and Path(candidate).exists():
            return candidate
    raise FileNotFoundError("LibreOffice (soffice) is required to convert the decks")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def converted(original: Path, cache: Path, fmt: str, soffice: str) -> Path:
    """Convert with LibreOffice, reusing a cached result only for the same source bytes."""
    ext = fmt.split(":")[0]
    out = cache / f"{original.stem}.{ext}"
    marker = cache / f"{original.stem}.{ext}.source-sha256"
    digest = sha256(original)
    if out.exists() and marker.exists() and marker.read_text().strip() == digest:
        return out
    subprocess.run([soffice, "--headless", "--convert-to", fmt, "--outdir", str(cache), str(original)],
                   check=True, capture_output=True, text=True)
    if not out.exists():
        raise RuntimeError(f"LibreOffice produced no {ext} for {original.name}")
    marker.write_text(digest)
    return out


def paragraph_text(p: ET.Element) -> str:
    parts = []
    for node in p.iter():
        tag = node.tag.split("}")[1]
        if tag == "t":
            parts.append(node.text or "")
        elif tag == "br":
            parts.append("\n")
    return "".join(parts)


def paragraph_level(p: ET.Element) -> int:
    ppr = p.find("a:pPr", NS)
    return int(ppr.attrib.get("lvl", "0")) if ppr is not None else 0


def walk_shapes(tree: ET.Element, title: list[str], paragraphs: list[str], levels: list[int],
                tables: list[list[list[str]]]) -> None:
    """Visit shapes in document (z-)order, descending into groups."""
    for node in tree:
        tag = node.tag.split("}")[1]
        if tag == "grpSp":
            walk_shapes(node, title, paragraphs, levels, tables)
        elif tag == "sp":
            ph = node.find("p:nvSpPr/p:nvPr/p:ph", NS)
            kind = ph.attrib.get("type", "body") if ph is not None else "shape"
            if kind in SKIPPED_PLACEHOLDERS:
                continue
            found = [(paragraph_text(p), paragraph_level(p)) for p in node.findall("p:txBody/a:p", NS)]
            found = [(t, lvl) for t, lvl in found if t.strip()]
            if kind in TITLE_PLACEHOLDERS and not title:
                title.append(" ".join(t.strip() for t, _ in found))
            else:
                paragraphs.extend(t for t, _ in found)
                levels.extend(lvl for _, lvl in found)
        elif tag == "graphicFrame":
            for tbl in node.iter(f"{{{NS['a']}}}tbl"):
                rows = []
                for tr in tbl.findall("a:tr", NS):
                    cells = [" ".join(paragraph_text(p).strip() for p in tc.findall("a:txBody/a:p", NS)).strip()
                             for tc in tr.findall("a:tc", NS)]
                    if any(cells):
                        rows.append(cells)
                if rows:
                    tables.append(rows)


def pptx_slides(path: Path) -> list[dict]:
    with zipfile.ZipFile(path) as archive:
        rels = {r.attrib["Id"]: r.attrib["Target"] for r in ET.fromstring(archive.read("ppt/_rels/presentation.xml.rels"))}
        pres = ET.fromstring(archive.read("ppt/presentation.xml"))
        result = []
        for sid in pres.find("p:sldIdLst", NS):
            target = rels[sid.attrib[f"{{{NS['r']}}}id"]]
            part = target.lstrip("/") if target.startswith("/") else "ppt/" + target
            root = ET.fromstring(archive.read(part))
            title: list[str] = []
            paragraphs: list[str] = []
            levels: list[int] = []
            tables: list[list[list[str]]] = []
            walk_shapes(root.find("p:cSld/p:spTree", NS), title, paragraphs, levels, tables)
            result.append({"title": title[0] if title else "", "paragraphs": paragraphs, "levels": levels, "tables": tables,
                           "hidden": root.attrib.get("show") == "0"})
        return result


def raw_text(slide: dict) -> str:
    lines = ([slide["title"]] if slide["title"] else []) + slide["paragraphs"]
    for table in slide["tables"]:
        lines.extend("\t".join(row) for row in table)
    return "\n".join(lines)


def load_ocr() -> dict[str, dict]:
    records = {}
    if OCR_FILE.exists():
        for line in OCR_FILE.read_text().splitlines():
            if line.strip():
                entry = json.loads(line)
                p = Path(entry["path"])
                records[f"{p.parent.name}/{p.name}"] = entry
    return records


def extract_one(item, source_dir: Path, cache: Path, soffice: str, rerender: bool, ocr: dict) -> dict:
    module_id, filename, title, lecture, category, cover = item
    original = source_dir / filename
    if not original.is_file():
        raise FileNotFoundError(original)
    # Published under the topic id: names like "Biology+Life (3)" break static URL matching.
    PUBLIC_SOURCES.mkdir(parents=True, exist_ok=True)
    published = PUBLIC_SOURCES / f"{module_id}{original.suffix.lower()}"
    preview = PUBLIC_SOURCES / f"{module_id}.pdf"
    shutil.copy2(original, published)
    pdf = converted(original, cache, 'pdf:impress_pdf_Export:{"ExportHiddenSlides":{"type":"boolean","value":"true"}}', soffice)
    shutil.copy2(pdf, preview)
    ooxml = original if original.suffix.lower() == ".pptx" else converted(original, cache, "pptx", soffice)

    count = int(re.search(r"^Pages:\s+(\d+)", subprocess.check_output(["pdfinfo", str(pdf)], text=True), re.M).group(1))
    decks = pptx_slides(ooxml)
    if len(decks) != count:
        raise AssertionError(f"{filename}: {len(decks)} OOXML slides but {count} PDF pages")

    image_dir = SLIDE_DIR / module_id
    image_dir.mkdir(parents=True, exist_ok=True)
    rendered = False
    if rerender or len(list(image_dir.glob("*.webp"))) != count:
        for old in image_dir.glob("*.webp"):
            old.unlink()
        with tempfile.TemporaryDirectory(prefix=module_id + "-") as tmp:
            subprocess.run(["pdftoppm", "-jpeg", "-r", "150", "-scale-to", "1800", str(pdf), str(Path(tmp) / "page")], check=True)
            for img in sorted(Path(tmp).glob("page-*.jpg")):
                with Image.open(img) as frame:
                    frame.save(image_dir / f"{int(img.stem.split('-')[-1]):03d}.webp", "WEBP", quality=86, method=5)
        rendered = True

    slides = []
    for number, deck in enumerate(decks, 1):
        image = image_dir / f"{number:03d}.webp"
        with Image.open(image) as frame:
            width, height = frame.size
        slide = {
            "id": f"{module_id}-{number:03d}",
            "number": number,
            "sourceTitle": deck["title"],
            "rawText": raw_text(deck),
            "sourceParagraphs": deck["paragraphs"],
            "sourceLevels": deck["levels"],
            "tables": deck["tables"],
            "image": f"/slides-mbmd/{module_id}/{number:03d}.webp",
            "width": width,
            "height": height,
            "isReferenceOnly": False,
            "hiddenInDeck": deck["hidden"],
            "textExtraction": "pptx-ooxml" if original.suffix.lower() == ".pptx" else "ppt→pptx-ooxml (LibreOffice)",
            "imageSha256": sha256(image),
        }
        record = None if rendered else ocr.get(f"{module_id}/{number:03d}.webp")
        if record and not record.get("error"):
            slide["ocrText"] = record["text"]
            slide["ocrBlockCount"] = len(record["blocks"])
        slides.append(slide)

    print(f"Extracted {filename}: {count} slides", flush=True)
    return {
        "id": module_id,
        "title": title,
        "lectureLabel": lecture,
        "category": category,
        "source": {
            "file": filename,
            "url": "/sources/fall2026/" + published.name,
            "previewUrl": "/sources/fall2026/" + preview.name,
            "sha256": sha256(original),
            "previewSha256": sha256(preview),
            "kind": original.suffix.lstrip(".").lower(),
            "pageCount": count,
        },
        "cover": f"/slides-mbmd/{module_id}/{cover:03d}.webp",
        "slides": slides,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--cache-dir", type=Path, default=APP / ".cache" / "fall2026")
    parser.add_argument("--rerender", action="store_true", help="Re-render every slide visual (drops OCR until re-run)")
    args = parser.parse_args()
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    soffice = find_soffice()
    ocr = load_ocr()
    # LibreOffice cannot run several conversions against one profile at once, so convert serially first.
    for item in MODULES:
        original = args.source_dir / item[1]
        converted(original, args.cache_dir, 'pdf:impress_pdf_Export:{"ExportHiddenSlides":{"type":"boolean","value":"true"}}', soffice)
        if original.suffix.lower() != ".pptx":
            converted(original, args.cache_dir, "pptx", soffice)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        modules = list(pool.map(lambda item: extract_one(item, args.source_dir, args.cache_dir, soffice, args.rerender, ocr), MODULES))
    for number, module in enumerate(modules, 1):
        module["number"] = number
    course = {
        "semester": "fall2026",
        "term": "Fall 2026",
        "instructor": "Prof. Dr. Md. Mahbubul Morshed (MBMD)",
        "institution": "North South University",
        "modules": modules,
        "references": [],
        "stats": {
            "moduleCount": len(modules),
            "slideCount": sum(len(m["slides"]) for m in modules),
            "ocrPageCount": sum(1 for m in modules for s in m["slides"] if "ocrText" in s),
        },
    }
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(course, ensure_ascii=False, indent=2))
    print(json.dumps(course["stats"]))


if __name__ == "__main__":
    main()
