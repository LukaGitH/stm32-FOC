#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


POS_HEADER_RE = re.compile(r"^#\s+Ref\s+Val\s+Package\s+PosX\s+PosY\s+Rot\s+Side\s*$", re.IGNORECASE)


def read_bom_refs(path: Path) -> set[str]:
    if not path.exists():
        return set()
    refs: set[str] = set()
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            for ref in row.get("Designator", "").split(","):
                ref = ref.strip()
                if ref:
                    refs.add(ref)
    return refs


def discover_pos_file(root: Path, explicit: str | None) -> Path:
    if explicit:
        path = (root / explicit).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Position file not found: {path}")
        return path

    files = sorted(root.glob("*.pos"))
    if not files:
        raise FileNotFoundError(
            "No .pos file found in the project directory. "
            "Export one from KiCad using PCB Editor > File > Fabrication Outputs > Component Placement."
        )
    if len(files) > 1:
        names = ", ".join(p.name for p in files)
        raise RuntimeError(f"Multiple .pos files found; use --pos to select one: {names}")
    return files[0]


def parse_kicad_pos(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    header_seen = False

    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            if POS_HEADER_RE.match(line):
                header_seen = True
            continue

        # KiCad .pos fields are whitespace separated. Values/packages in this
        # project do not contain literal spaces because KiCad prints underscores.
        parts = line.split()
        if len(parts) < 7:
            raise ValueError(f"Malformed .pos row: {raw!r}")

        ref, value, package, x, y, rotation, side = parts[:7]
        side_lower = side.lower()
        if side_lower == "top":
            layer = "Top"
        elif side_lower == "bottom":
            layer = "Bottom"
        else:
            raise ValueError(f"Unsupported PCB side {side!r} for {ref}")

        # Validate numeric data but preserve KiCad's decimal precision.
        float(x)
        float(y)
        float(rotation)

        rows.append(
            {
                "Designator": ref,
                "Mid X": f"{x}mm",
                "Mid Y": f"{y}mm",
                "Rotation": rotation,
                "Layer": layer,
            }
        )

    if not header_seen:
        raise ValueError(f"{path.name} does not look like a KiCad component position file")
    if not rows:
        raise ValueError(f"No placement rows found in {path.name}")
    return rows


def natural_ref_key(ref: str) -> tuple[str, int, str]:
    match = re.match(r"([A-Za-z]+)(\d+)(.*)", ref)
    if not match:
        return (ref, 0, "")
    return (match.group(1), int(match.group(2)), match.group(3))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert a KiCad .pos placement file into JLCPCB CPL format."
    )
    parser.add_argument("project_dir", nargs="?", default=".")
    parser.add_argument("--pos", help="Position file path relative to project_dir")
    parser.add_argument(
        "--bom",
        default="production/export/jlcpcb_bom.csv",
        help="BOM used to filter CPL references. Use --all-placements to disable filtering.",
    )
    parser.add_argument(
        "--all-placements",
        action="store_true",
        help="Export every reference in the .pos file instead of only BOM references.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="production/export/jlcpcb_cpl.csv",
    )
    args = parser.parse_args()

    root = Path(args.project_dir).resolve()
    pos_path = discover_pos_file(root, args.pos)
    output_path = root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    placements = parse_kicad_pos(pos_path)
    placement_by_ref = {row["Designator"]: row for row in placements}
    if len(placement_by_ref) != len(placements):
        raise ValueError("Duplicate references found in the position file")

    if args.all_placements:
        selected_refs = set(placement_by_ref)
    else:
        bom_path = root / args.bom
        selected_refs = read_bom_refs(bom_path)
        if not selected_refs:
            raise ValueError(
                f"No BOM references found in {bom_path}. "
                "Run export_jlcpcb_bom.py first or use --all-placements."
            )

        missing = sorted(selected_refs - set(placement_by_ref), key=natural_ref_key)
        if missing:
            raise ValueError(
                "BOM references missing from the position file: " + ", ".join(missing)
            )

    rows = [
        placement_by_ref[ref]
        for ref in sorted(selected_refs, key=natural_ref_key)
        if ref in placement_by_ref
    ]

    with output_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["Designator", "Mid X", "Mid Y", "Rotation", "Layer"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Read {len(placements)} placements from {pos_path}")
    print(f"Wrote {len(rows)} CPL rows to {output_path}")
    if not args.all_placements:
        print("CPL was filtered to references present in the generated BOM.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
