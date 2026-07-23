# STM32 FOC hardware

This fork's hardware source is KiCad-only.

- Open [`ESC-BLDC/ESC-BLDC.kicad_pro`](ESC-BLDC/ESC-BLDC.kicad_pro) in KiCad 10.
- The complete schematic hierarchy and PCB are in `ESC-BLDC/`.
- Ready-to-upload JLCPCB [BOM and CPL files](ESC-BLDC/production/export/) are
  in `ESC-BLDC/production/export/`.
- [original_vs_kicad_component_comparison.csv](ESC-BLDC/production/original_vs_kicad_component_comparison.csv) is the
  reference-by-reference comparison of original Altium values/packages and the
  current KiCad selections.
- [Project Outputs for ESC-BLDC.zip](Project%20Outputs%20for%20ESC-BLDC.zip) is the existing Gerber archive, retained
  unchanged for traceability.

For component selections and the checked JLCPCB production workflow, see the
[production README](ESC-BLDC/production/README.md).

The previous Altium source files are deliberately excluded from this repository.
