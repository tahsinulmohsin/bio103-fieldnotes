#!/usr/bin/env python3
"""Extract Fall 2026 (MBMD) lecture slides, text, and metadata."""

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
SOURCE_DIR = Path("/Users/tahsinulmohsin/NSU Fall 2026/BIO103 MBMD")
PDF_DIR = Path("/Users/tahsinulmohsin/.gemini/antigravity/brain/139856a9-14b2-4e85-9f22-3a8b94f68dc1/work/mbmd_conversion")

MODULES = [
    {
        "id": "intro-biology",
        "file": "Lec-1,2_Introduction to Biology+Life (3).pptx",
        "pdf": "Lec-1,2_Introduction to Biology+Life (3).pdf",
        "title": "Introduction to Biology & Life",
        "lectureLabel": "Lectures 1–2",
        "category": "Foundations",
        "coverSlide": 1
    },
    {
        "id": "classification",
        "file": "L - 3 Classification of Living Things.pptx",
        "pdf": "L - 3 Classification of Living Things.pdf",
        "title": "Classification of Living Things",
        "lectureLabel": "Lecture 3",
        "category": "Foundations",
        "coverSlide": 2
    },
    {
        "id": "chemistry",
        "file": "Lec-4,5_Chemistry of life.pptx",
        "pdf": "Lec-4,5_Chemistry of life.pdf",
        "title": "Chemistry of Life",
        "lectureLabel": "Lectures 4–5",
        "category": "Foundations",
        "coverSlide": 2
    },
    {
        "id": "macromolecules",
        "file": "Lec-6,7_Biological macromolecules.pptx",
        "pdf": "Lec-6,7_Biological macromolecules.pdf",
        "title": "Biological Macromolecules",
        "lectureLabel": "Lectures 6–7",
        "category": "Foundations",
        "coverSlide": 2
    },
    {
        "id": "cells",
        "file": "Lec-8,9_Cells.ppt",
        "pdf": "Lec-8,9_Cells.pdf",
        "title": "Cell Structure and Function",
        "lectureLabel": "Lectures 8–9",
        "category": "Cell & molecular biology",
        "coverSlide": 2
    },
    {
        "id": "central-dogma",
        "file": "Lec-10_CDL.pptx",
        "pdf": "Lec-10_CDL.pdf",
        "title": "Central Dogma of Life",
        "lectureLabel": "Lecture 10",
        "category": "Cell & molecular biology",
        "coverSlide": 2
    },
    {
        "id": "energy",
        "file": "Lec-11,12_Energy of Life.pptx",
        "pdf": "Lec-11,12_Energy of Life.pdf",
        "title": "Energy of Life",
        "lectureLabel": "Lectures 11–12",
        "category": "Cell & molecular biology",
        "coverSlide": 2
    },
    {
        "id": "cell-cycle",
        "file": "Lec-13,14_Cell Cycle.pptx",
        "pdf": "Lec-13,14_Cell Cycle.pdf",
        "title": "Cell Cycle & Cellular Division",
        "lectureLabel": "Lectures 13–14",
        "category": "Cell & molecular biology",
        "coverSlide": 2
    },
    {
        "id": "homeostasis",
        "file": "Lec-15_Homeostasis.pptx",
        "pdf": "Lec-15_Homeostasis.pdf",
        "title": "Homeostasis",
        "lectureLabel": "Lecture 15",
        "category": "Human systems",
        "coverSlide": 2
    },
    {
        "id": "digestion",
        "file": "Lec-16_digestion.pptx",
        "pdf": "Lec-16_digestion.pdf",
        "title": "Digestive System",
        "lectureLabel": "Lecture 16",
        "category": "Human systems",
        "coverSlide": 2
    },
    {
        "id": "circulation",
        "file": "Lec-17_Circulatory System.pptx",
        "pdf": "Lec-17_Circulatory System.pdf",
        "title": "Circulatory System",
        "lectureLabel": "Lecture 17",
        "category": "Human systems",
        "coverSlide": 2
    },
    {
        "id": "respiration-excretion",
        "file": "Lec-18_Respiratory & Excretory System.pptx",
        "pdf": "Lec-18_Respiratory & Excretory System.pdf",
        "title": "Human Respiratory & Excretory System",
        "lectureLabel": "Lecture 18",
        "category": "Human systems",
        "coverSlide": 2
    },
    {
        "id": "diabetes-lipids",
        "file": "Lec-19_Diabetes_LP.pptx",
        "pdf": "Lec-19_Diabetes_LP.pdf",
        "title": "Diabetes & Lipid Profile",
        "lectureLabel": "Lecture 19",
        "category": "Food & metabolism",
        "coverSlide": 2
    },
    {
        "id": "nutrition",
        "file": "Lec-20_Food & Nutrition.pptx",
        "pdf": "Lec-20_Food & Nutrition.pdf",
        "title": "Food and Nutrition",
        "lectureLabel": "Lecture 20",
        "category": "Food & metabolism",
        "coverSlide": 2
    }
]


def split_pages(text):
    pages = text.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return pages


def get_pptx_text(path):
    ns = {
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    }
    with zipfile.ZipFile(path) as archive:
        rels = {r.attrib["Id"]: r.attrib["Target"] for r in ET.fromstring(archive.read("ppt/_rels/presentation.xml.rels"))}
        pres = ET.fromstring(archive.read("ppt/presentation.xml"))
        result = []
        sld_id_lst = pres.find("p:sldIdLst", ns)
        if sld_id_lst is not None:
            for sid in sld_id_lst:
                target = rels[sid.attrib["{" + ns["r"] + "}id"]]
                part = "ppt/" + target.lstrip("/") if not target.startswith("/") else target.lstrip("/")
                root = ET.fromstring(archive.read(part))
                texts = ["".join(t.text or "" for t in p.findall(".//a:t", ns)) for p in root.findall(".//a:p", ns)]
                result.append("\n".join(texts))
        return result


def title_for(text, page):
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    lines = [x for x in lines if not re.fullmatch(r"\d{1,3}", x)]
    if not lines:
        return f"Slide {page}"
    first = lines[0]
    return first if len(first) <= 100 else f"Slide {page}"


def render_and_extract(mod_info):
    mod_id = mod_info["id"]
    pdf_path = PDF_DIR / mod_info["pdf"]
    original_path = SOURCE_DIR / mod_info["file"]
    
    assert pdf_path.exists(), f"PDF not found: {pdf_path}"
    assert original_path.exists(), f"Original not found: {original_path}"
    
    # Get slide count
    info = subprocess.check_output(["pdfinfo", str(pdf_path)]).decode()
    count = int(re.search(r"^Pages:\s+(\d+)", info, re.M).group(1))
    
    # Extract text
    if original_path.suffix.lower() == ".pptx":
        try:
            pages = get_pptx_text(original_path)
            if len(pages) != count:
                # Fallback to pdf text if OOXML count differs
                pages = split_pages(subprocess.check_output(["pdftotext", str(pdf_path), "-"]).decode())
        except Exception:
            pages = split_pages(subprocess.check_output(["pdftotext", str(pdf_path), "-"]).decode())
    else:
        pages = split_pages(subprocess.check_output(["pdftotext", str(pdf_path), "-"]).decode())
        
    layout_pages = split_pages(subprocess.check_output(["pdftotext", "-layout", str(pdf_path), "-"]).decode())
    
    # Ensure page counts match
    while len(pages) < count:
        pages.append("")
    while len(layout_pages) < count:
        layout_pages.append("")
        
    pages = pages[:count]
    layout_pages = layout_pages[:count]
    
    # Render images
    image_dir = APP / "public" / "slides-mbmd" / mod_id
    image_dir.mkdir(parents=True, exist_ok=True)
    
    existing_images = list(image_dir.glob("*.webp"))
    if len(existing_images) != count:
        with tempfile.TemporaryDirectory(prefix=mod_id + "-") as tmp_dir:
            prefix = Path(tmp_dir) / "page"
            subprocess.run(["pdftoppm", "-jpeg", "-r", "150", "-scale-to", "1800", str(pdf_path), str(prefix)], check=True)
            for img in sorted(Path(tmp_dir).glob("page-*.jpg")):
                num = int(img.stem.split("-")[-1])
                with Image.open(img) as frame:
                    frame.save(image_dir / f"{num:03d}.webp", "WEBP", quality=86, method=4)
                    
    slides = []
    for idx, raw in enumerate(pages):
        num = idx + 1
        img_path = image_dir / f"{num:03d}.webp"
        with Image.open(img_path) as frame:
            w, h = frame.size
            
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", raw) if p.strip() and not re.fullmatch(r"\d{1,3}", p.strip())]
        t = title_for(layout_pages[idx] if idx < len(layout_pages) else raw, num)
        
        slides.append({
            "id": f"{mod_id}-{num:03d}",
            "number": num,
            "title": t,
            "rawText": raw.strip(),
            "paragraphs": paragraphs,
            "image": f"/slides-mbmd/{mod_id}/{num:03d}.webp",
            "width": w,
            "height": h,
            "isReferenceOnly": False,
            "textExtraction": "pptx-ooxml" if original_path.suffix.lower() == ".pptx" else "pdf-text-layer",
            "imageSha256": hashlib.sha256(img_path.read_bytes()).hexdigest(),
        })
        
    cover_slide = mod_info["coverSlide"]
    cover_path = f"/slides-mbmd/{mod_id}/{cover_slide:03d}.webp"
    
    print(f"Extracted {mod_info['title']}: {count} slides", flush=True)
    
    return {
        "id": mod_id,
        "title": mod_info["title"],
        "lectureLabel": mod_info["lectureLabel"],
        "category": mod_info["category"],
        "instructor": "Prof. Dr. Md. Mahbubul Morshed (MBMD)",
        "term": "Fall 2026",
        "description": " · ".join(dict.fromkeys(s["title"] for s in slides[1:4])),
        "cover": cover_path,
        "source": {
            "file": mod_info["file"],
            "url": f"/sources/{mod_info['file']}",
            "kind": Path(mod_info["file"]).suffix.lstrip("."),
            "pageCount": count
        },
        "slides": slides,
        "flashcards": [],
        "quiz": []
    }


def main():
    print("Starting extraction of Fall 2026 MBMD course slides...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(render_and_extract, m) for m in MODULES]
        modules = [f.result() for f in futures]
        
    # Maintain original order
    order_map = {m["id"]: i for i, m in enumerate(MODULES)}
    modules.sort(key=lambda m: order_map[m["id"]])
    
    for idx, m in enumerate(modules, 1):
        m["number"] = idx
        
    out_file = APP / "data" / "course-mbmd-raw.json"
    out_file.write_text(json.dumps(modules, ensure_ascii=False, indent=2))
    
    total_slides = sum(len(m["slides"]) for m in modules)
    print(f"Successfully processed {len(modules)} modules with {total_slides} slides total!")
    print(f"Saved to {out_file}")


if __name__ == "__main__":
    main()
