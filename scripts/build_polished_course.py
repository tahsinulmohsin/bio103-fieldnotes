#!/usr/bin/env python3
"""Build polished titles and rich explanations for all 439 slides in course.json."""

import json
import os
import sys
from pathlib import Path

# Add scripts directory to sys.path
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from polished.engine import auto_polish_slide, clean_title
from polished.mod01_intro import CURATED_SLIDES as MOD01_SLIDES
from polished.mod04_central_dogma import CURATED_SLIDES as MOD04_SLIDES
from polished.mod08_homeostasis import CURATED_SLIDES as MOD08_SLIDES
from polished.mod13_diabetes_lipids import CURATED_SLIDES as MOD13_SLIDES
from polished.mod_systems import CIRCULATION_SLIDES, DIGESTION_SLIDES
from polished.mod_all_curated import (
    CHEMISTRY_SLIDES,
    MACROMOLECULES_SLIDES,
    CELLS_SLIDES,
    ENERGY_SLIDES,
    DIVISION_SLIDES,
)

COURSE_FILE = SCRIPTS_DIR.parent / "data" / "course.json"

MODULE_CURATED_MAP = {
    "introduction": MOD01_SLIDES,
    "chemistry": CHEMISTRY_SLIDES,
    "macromolecules": MACROMOLECULES_SLIDES,
    "molecular-biology": MOD04_SLIDES,
    "cells": CELLS_SLIDES,
    "energy": ENERGY_SLIDES,
    "cell-division": DIVISION_SLIDES,
    "homeostasis": MOD08_SLIDES,
    "circulation": CIRCULATION_SLIDES,
    "digestion": DIGESTION_SLIDES,
    "diabetes-lipids": MOD13_SLIDES,
}

def main():
    print(f"Loading {COURSE_FILE}...")
    with open(COURSE_FILE, "r", encoding="utf-8") as f:
        course = json.load(f)

    total_slides = 0
    curated_count = 0
    auto_count = 0

    for m in course["modules"]:
        mod_id = m["id"]
        curated_dict = MODULE_CURATED_MAP.get(mod_id, {})

        for s in m["slides"]:
            total_slides += 1
            num = s["number"]

            if num in curated_dict:
                s["polishedTitle"] = curated_dict[num]["title"]
                s["polishedExplanation"] = curated_dict[num]["explanation"]
                curated_count += 1
            else:
                title, explanation = auto_polish_slide(s, m)
                s["polishedTitle"] = title
                s["polishedExplanation"] = explanation
                auto_count += 1

    print(f"Processed {total_slides} slides across {len(course['modules'])} modules.")
    print(f"Curated in-depth explanations: {curated_count}")
    print(f"Auto-polished NLP synthesis explanations: {auto_count}")

    # Write back to course.json
    with open(COURSE_FILE, "w", encoding="utf-8") as f:
        json.dump(course, f, indent=2, ensure_ascii=False)

    print(f"Successfully wrote polished data to {COURSE_FILE}!")

if __name__ == "__main__":
    main()
