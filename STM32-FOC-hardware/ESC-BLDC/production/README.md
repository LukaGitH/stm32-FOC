# STM32 FOC JLCPCB production files

The KiCad schematics and PCB are the source of truth for this production
workflow.

## Run

From the `ESC-BLDC` project directory:

```bash
python3 production/scripts/export_jlcpcb_bom.py .
python3 production/scripts/export_jlcpcb_cpl.py .
python3 production/scripts/validate_production_files.py .
python3 production/scripts/export_component_comparison.py .
```

Outputs:

- `production/export/jlcpcb_bom.csv`
- `production/export/jlcpcb_cpl.csv`
- `production/export/validation_report.txt`
- `production/original_vs_kicad_component_comparison.csv`

## Current result

- 5 schematic sheets parsed successfully
- 131 placed non-power references found, including DNP/manual items
- 118 fitted references, all with LCSC assignments
- 49 grouped JLCPCB BOM rows and 118 matching CPL rows
- 0 validation errors or warnings

The BOM exporter reads `Value`, `Footprint`, `Manufacturer`, `MPN`, `LCSC`,
`JLCPCB Class`, and `DNP`. DNP parts and power symbols are excluded.

The CPL exporter reads the KiCad component-placement file
`ESC-BLDC-all.pos`, and includes only references present in the BOM. Generate a
replacement from KiCad PCB Editor using `File > Fabrication Outputs > Component
Placement`, in millimetres and with both sides enabled.

## Original-versus-current comparison

`original_vs_kicad_component_comparison.csv` is a one-row-per-reference
spreadsheet. It preserves the imported `ALTIUM_VALUE` and package metadata next
to the current KiCad value, footprint, selected manufacturer part, LCSC code,
and assembly state.

`symmetry_and_sourcing_review.md` records the second-pass check of matched
component groups, divider ratios, and the remaining Extended selections.

## Supporting decisions

- `component_sourcing_audit.md` is the current selected-part list and records
  the order-time checks.
- `symmetry_and_sourcing_review.md` checks matched component groups, original
  package sizes, and the divider-ratio decisions.
