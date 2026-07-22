#!/usr/bin/env python3
"""Export a reference-by-reference Altium-to-KiCad component comparison."""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from kicad_schematic import discover_schematics, is_power_symbol, read_symbols


REF_RE = re.compile(r"^([A-Za-z]+)(\d+)(.*)$")
PACKAGE_SUFFIX_RE = re.compile(r"\s*\([^)]*\)\s*$")


def natural_ref_key(reference: str) -> tuple[str, int, str]:
    match = REF_RE.match(reference)
    if not match:
        return reference, 0, ""
    return match.group(1), int(match.group(2)), match.group(3)


def original_value(symbol) -> str:
    return symbol.fields.get("ALTIUM_VALUE", "").strip() or symbol.value


def value_without_package(value: str) -> str:
    return PACKAGE_SUFFIX_RE.sub("", value).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", nargs="?", default=".")
    parser.add_argument(
        "-o", "--output", default="production/original_vs_kicad_component_comparison.csv"
    )
    args = parser.parse_args()

    root = Path(args.project_dir).resolve()
    rows = []
    for schematic in discover_schematics(root):
        for symbol in read_symbols(schematic):
            if is_power_symbol(symbol.reference):
                continue
            original = original_value(symbol)
            current = symbol.value
            dnp = symbol.fields.get("DNP", "").strip().lower() in {
                "1", "yes", "true", "dnp", "do not populate", "not assembled"
            }
            rows.append({
                "Sheet": schematic.name,
                "Reference": symbol.reference,
                "Original Altium value": original,
                "Original package": symbol.fields.get("CASE/PACKAGE", "").strip(),
                "Current KiCad value": current,
                "Current KiCad footprint": symbol.footprint,
                "Selected MPN": symbol.fields.get("MPN", "").strip(),
                "LCSC part": symbol.fields.get("LCSC", "").strip(),
                "JLCPCB class": symbol.fields.get("JLCPCB Class", "").strip(),
                "Assembly status": "DNP / manual" if dnp else "Fitted",
                "Value changed": (
                    "Yes" if value_without_package(original) != current else "No"
                ),
            })

    rows.sort(key=lambda row: (row["Sheet"], natural_ref_key(row["Reference"])))
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {output}")
    print(f"Component references: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
