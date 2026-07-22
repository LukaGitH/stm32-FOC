# Symmetry and sourcing review — 2026-07-22

This is a second pass over the 120 fitted references in the KiCad production
package. The source comparison spreadsheet remains the one-to-one record of
every original Altium reference, value, package, and current KiCad selection:
`original_vs_kicad_component_comparison.csv`.

## Result

- All 120 fitted references have an LCSC assignment and corresponding CPL row.
- All repeated phase-channel components use the same value, footprint, and LCSC
  selection within their group.
- The KiCad footprints preserve the original nominal package sizes for the
  reviewed passives: 0402, 0603, 2512, and the 2525 inductor land pattern.
- P6–P9 remain intentionally DNP because the available JST-style parts did not
  provide the required rear-facing SMD contact geometry.

## Matched electrical groups

| References | Function | Current selection | Review result |
|---|---|---|---|
| Q1–Q6 | Three half bridges | FDMS8820, `C236897`, PDFN56 | Six identical MOSFETs. Keep the selected Extended part. |
| R14–R16, R20–R22 | Gate resistors | 10 Ω, 0603, `C22859` | Six identical parts. |
| R17–R19 | Phase-voltage divider upper legs | 33 kΩ, 0402, `C25779` | Three identical parts. |
| R25–R27 | Phase-voltage divider lower legs | 2 kΩ, 0402, `C4109` | Three identical Basic parts; MPN corrected to `0402WGF2001TCE`. |
| R23, R24 | Phase-current shunts | 10 mΩ, 2512, `C316229` | Matched pair. |
| C41, C42 | CAN filter capacitors | 220 pF, 0402, `C1530` | Matched pair. |
| C33–C35 | Bulk ceramic decoupling | 2.2 µF, 0603, `C23630` | Matched trio. |
| D3–D11 | Signal diodes | 1N4148WT, SOD-523, `C917006` | Matched nine-part group. |
| P1, P2 | Power connectors | XT30PW-M, `C431092` | Matched pair. |

## Divider check

### Phase-voltage and VBUS dividers

Each phase-voltage divider is 33 kΩ / 2 kΩ (R17/R25, R18/R26, and R19/R27),
giving a divider factor of 2 / (33 + 2) = **0.05714**. These are symmetric and
already use Basic resistors.

The VBUS divider R12/R13 is also 33 kΩ / 2 kΩ, using 0603 Basic selections
`C4216` and `C22975`. Its factor is therefore the same. Firmware has already
been set to the matching conversion constant; changing either VBUS resistor
requires updating that firmware constant.

### DRV8302 OC_ADJ divider

R7/R8 is 39 kΩ / 1 kΩ, so:

`V_OC_ADJ = 3.3 V × 1 / (39 + 1) = 82.5 mV`.

This is a hardware current-limit threshold, not a firmware scaling factor.
Changing only R7 to a nearby 36 kΩ Basic candidate would produce 89.2 mV,
an **8.1% higher** current trip. Changing the pair to 36 kΩ / 910 Ω would
produce 81.3 mV, **1.4% lower** than the current design, but the exact proposed
Basic stock pair needs confirmation at order time.

Recommendation: retain 39 kΩ `C163424` and 1 kΩ `C21190`. One Extended resistor
does not avoid Extended-part handling on this board because L1, the power
MOSFETs, and specialised IC/connector selections already require it.

## Remaining Extended selections

| References | Part | Why it remains |
|---|---|---|
| L1 | 22 µH SL0650-220M, `C22463831` | Correct 7.1 × 6.6 mm footprint, current rating, and saturation-current requirement. |
| Q1–Q6 | FDMS8820, `C236897` | Power MOSFET electrical and package match. |
| D12 | M7 / 1N4007 SMA, `C2972759` | 1 kV rectifier requirement; do not replace with a lower-voltage Basic diode. |
| R7 | 39 kΩ 0603, `C163424` | Exact OC_ADJ ratio. A Basic substitution shifts hardware over-current trip unless the pair is redesigned. |
| X1, USB1, ICs, P1/P2 | Specialised package-specific parts | No passive Basic substitution is applicable. |

## Deliberate value changes from the imported design

The comparison spreadsheet records 40 value-text differences. Most are
notation normalisation (`µF` to `uF`) or already-approved sourcing changes.
The electrically relevant reviewed changes are C10 (4.7 µF), C11 (22 nF),
C41/C42 (220 pF matched pair), the 33 kΩ / 2 kΩ phase and VBUS divider groups,
and the 39 kΩ / 1 kΩ OC_ADJ pair. No additional value changes are recommended
by this review.
