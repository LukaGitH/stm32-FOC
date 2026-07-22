#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

PROPERTY_RE = re.compile(r'\(property "([^"]+)" "([^"]*)"')


def symbol_blocks(text: str):
    i = 0
    while True:
        start = text.find("\n\t(symbol\n", i)
        if start < 0:
            return
        start += 1
        depth = 0
        in_string = False
        escaped = False
        for j in range(start, len(text)):
            ch = text[j]
            if in_string:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    in_string = False
            else:
                if ch == '"':
                    in_string = True
                elif ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        yield text[start:j + 1]
                        i = j + 1
                        break
        else:
            raise ValueError("Broken KiCad S-expression structure")


def read_refs_from_bom(path: Path):
    refs = set()
    blank_lcsc_refs = set()
    rows = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            rows.append(row)
            row_refs = {
                ref.strip()
                for ref in row.get("Designator", "").split(",")
                if ref.strip()
            }
            refs |= row_refs
            if not row.get("LCSC Part #", "").strip():
                blank_lcsc_refs |= row_refs
    return refs, blank_lcsc_refs, rows


def read_refs_from_cpl(path: Path):
    refs = set()
    with path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            ref = row.get("Designator", "").strip()
            if ref:
                refs.add(ref)
    return refs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", nargs="?", default=".")
    args = parser.parse_args()

    root = Path(args.project_dir).resolve()
    export_dir = root / "production" / "export"
    export_dir.mkdir(parents=True, exist_ok=True)
    report_path = export_dir / "validation_report.txt"

    all_refs = set()
    lcsc_refs = set()
    schematic_count = 0

    for sch in sorted(root.glob("*.kicad_sch")):
        schematic_count += 1
        text = sch.read_text(encoding="utf-8")
        for block in symbol_blocks(text):
            props = dict(PROPERTY_RE.findall(block))
            ref = props.get("Reference", "").strip()
            if not ref or ref.startswith("#"):
                continue
            if re.search(r"\(in_bom\s+no\)", block) or re.search(r"\(dnp\s+yes\)", block):
                continue
            all_refs.add(ref)
            if props.get("LCSC", "").strip():
                lcsc_refs.add(ref)

    bom_path = export_dir / "jlcpcb_bom.csv"
    cpl_path = export_dir / "jlcpcb_cpl.csv"

    errors = []
    warnings = []
    missing = []

    bom_refs, blank_lcsc_refs, bom_rows = read_refs_from_bom(bom_path)

    if cpl_path.exists():
        cpl_refs = read_refs_from_cpl(cpl_path)
        for ref in sorted(bom_refs - cpl_refs):
            errors.append(f"BOM reference missing from CPL: {ref}")
        for ref in sorted(cpl_refs - bom_refs):
            errors.append(f"CPL reference missing from BOM: {ref}")
    else:
        cpl_refs = set()
        warnings.append("CPL file not found")

    for ref in sorted(blank_lcsc_refs):
        missing.append(f"BOM row has no LCSC assignment: {ref}")

    for ref in sorted(all_refs - lcsc_refs):
        if ref not in blank_lcsc_refs:
            missing.append(f"Schematic component has no LCSC assignment: {ref}")

    lines = [
        "STM32 FOC JLCPCB production validation",
        "========================================",
        f"Schematics checked: {schematic_count}",
        f"Assembled non-power references: {len(all_refs)}",
        f"References with LCSC: {len(lcsc_refs)}",
        f"BOM references exported: {len(bom_refs)}",
        f"CPL references exported: {len(cpl_refs)}",
        "",
        "Issue summary:",
        f"  ERROR: {len(errors)}",
        f"  WARNING: {len(warnings)}",
        f"  MISSING: {len(missing)}",
    ]

    if errors:
        lines += ["", "Errors:"] + [f"- {x}" for x in errors]
    if warnings:
        lines += ["", "Warnings:"] + [f"- {x}" for x in warnings]
    if missing:
        lines += ["", "Missing/unresolved:"] + [f"- {x}" for x in missing]

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {report_path}")
    print("\n".join(lines[:13]))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
