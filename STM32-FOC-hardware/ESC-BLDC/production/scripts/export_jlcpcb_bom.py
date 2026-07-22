#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

PROPERTY_RE = re.compile(r'\(property "([^"]+)" "([^"]*)"')
REF_RE = re.compile(r"^([A-Za-z]+)(\d+)(.*)$")


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


def natural_ref_key(ref: str):
    match = REF_RE.match(ref)
    if not match:
        return (ref, 0, "")
    return (match.group(1), int(match.group(2)), match.group(3))


def normalize_footprint_for_grouping(footprint: str) -> str:
    upper = footprint.upper()

    aliases = {
        "CAPC0603(1608)100_L": "0603",
        "CAPC0603(1608)100": "0603",
        "CAPC1608": "0603",
        "C_0603_1608METRIC": "0603",
        "RESC0402": "0402",
        "R_0402_1005METRIC": "0402",
        "CAPC0402": "0402",
        "C_0402_1005METRIC": "0402",
        "RESC0603": "0603",
        "R_0603_1608METRIC": "0603",
        "CAPC0805": "0805",
        "C_0805_2012METRIC": "0805",
        "AVAG-HSMX-C190": "0603",
        "LTST-C190KSKT": "0603",
    }

    for token, canonical in aliases.items():
        if token in upper:
            return canonical

    metric_aliases = {
        "1005": "0402",
        "1608": "0603",
        "2012": "0805",
        "3216": "1206",
        "3225": "1210",
        "6432": "2512",
    }

    if upper.startswith(("RESC", "CAPC")):
        for metric, imperial in metric_aliases.items():
            if metric in upper:
                return imperial

    for canonical in ("0201", "0402", "0603", "0805", "1206", "1210", "1812", "2512"):
        if canonical in upper:
            return canonical

    return footprint.strip()


def is_power_symbol(ref: str) -> bool:
    return ref.startswith("#")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export every assembled KiCad component to JLCPCB BOM format."
    )
    parser.add_argument("project_dir", nargs="?", default=".")
    parser.add_argument(
        "-o",
        "--output",
        default="production/export/jlcpcb_bom.csv",
    )
    args = parser.parse_args()

    root = Path(args.project_dir).resolve()
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)

    components = []

    for schematic in sorted(root.glob("*.kicad_sch")):
        text = schematic.read_text(encoding="utf-8")

        for block in symbol_blocks(text):
            props = dict(PROPERTY_RE.findall(block))

            ref = props.get("Reference", "").strip()
            if not ref or is_power_symbol(ref):
                continue

            dnp = props.get("DNP", "").strip().lower()
            if dnp in {"1", "yes", "true", "dnp"}:
                continue

            # Respect the KiCad symbol-level BOM exclusion flag.
            if re.search(r"\(in_bom\s+no\)", block):
                continue

            footprint = props.get("Footprint", "").strip()

            components.append(
                {
                    "Reference": ref,
                    "Value": props.get("Value", "").strip(),
                    "Footprint": footprint,
                    "Footprint Group": normalize_footprint_for_grouping(footprint),
                    "Manufacturer": props.get("Manufacturer", "").strip(),
                    "MPN": props.get("MPN", "").strip(),
                    "LCSC": props.get("LCSC", "").strip(),
                }
            )

    groups = defaultdict(list)

    for component in components:
        key = (
            component["Value"],
            component["Footprint Group"],
            component["Manufacturer"],
            component["MPN"],
            component["LCSC"],
        )
        groups[key].append(component)

    rows = []

    for (value, footprint_group, manufacturer, mpn, lcsc), items in groups.items():
        references = sorted(
            (item["Reference"] for item in items),
            key=natural_ref_key,
        )

        actual_footprints = sorted(
            set(item["Footprint"] for item in items)
        )

        known_packages = {
            "0201", "0402", "0603", "0805", "1206", "1210", "1812", "2512",
            "SOT-23", "SOT-223", "SOIC-8", "TSSOP-14", "QFN", "LQFP"
        }

        if footprint_group in known_packages:
            footprint_output = footprint_group
        elif len(actual_footprints) == 1:
            footprint_output = actual_footprints[0]
        else:
            footprint_output = footprint_group

        rows.append(
            {
                "Comment": value,
                "Designator": ",".join(references),
                "Footprint": footprint_output,
                "LCSC Part #": lcsc,
            }
        )

    rows.sort(
        key=lambda row: natural_ref_key(row["Designator"].split(",")[0])
    )

    with output.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "Comment",
                "Designator",
                "Footprint",
                "LCSC Part #",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    reference_count = sum(
        len(row["Designator"].split(","))
        for row in rows
    )
    blank_lcsc_rows = sum(
        1 for row in rows
        if not row["LCSC Part #"]
    )

    print(f"Wrote {output}")
    print(f"Grouped BOM rows: {len(rows)}")
    print(f"References exported: {reference_count}")
    print(f"Rows without LCSC: {blank_lcsc_rows}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
