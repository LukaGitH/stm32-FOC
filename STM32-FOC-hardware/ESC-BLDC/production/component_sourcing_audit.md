# Component sourcing audit — 2026-07-22

This audit separates verified JLCPCB purchasing selections from parts that need
an electrical-design decision or are presently unavailable. It does not change
the KiCad source files while the project is open in KiCad.

## Ready to apply

| References | Design value / required package | Selected manufacturer part | LCSC | JLCPCB status |
|---|---|---|---|---|
| D2 | 1N4148WS, SOD-323 | 1N4148WS (Jiangsu Changjing) | C2128 | In stock |
| D3–D11 | 1N4148WT, SOD-523 | 1N4148WT (JSMSEMI) | C917006 | In stock |
| U2 | LP2985-33DBVR, SOT-23-5 / DBV | LP2985-33DBVR (Texas Instruments) | C95414 | In stock |
| U6 | STM32F405RGT6, LQFP-64 10 × 10 mm | STM32F405RGT6 (STMicroelectronics) | C15742 | Verify live stock at order placement |
| C10 | 4.7 µF, 10 V, 0402 | CL05A475MP5NRNC (Samsung), X5R ±20% | C23733 | Basic, in stock |
| C11 | 22 nF, 50 V, 0402 | 0402B223K500NT (FH), X7R ±10% | C1532 | Basic, in stock |
| C32 | 10 nF, 50 V, 0402 | CL05B103KB5NNNC (Samsung), X7R ±10% | C15195 | Basic |

The diode selections retain the existing diode families and footprints. U2 and
U6 are exact manufacturer-part matches, not replacements.

## IC sourcing selections

| Reference | Selected part | LCSC | Decision |
|---|---|---|---|
| U1 | TI DRV8302DCA, HTSSOP-56 | C84672 | Exact manufacturer part. |
| U3 | AMS AS5047P-ATSM, TSSOP-14 | C962063 | Exact manufacturer part. |
| U4 | JSMSEMI MCP2551-I/SN-JSM, SOP-8 | C46596284 | 5 V, 1 Mb/s MCP2551-compatible CAN transceiver. |
| U5 | ST USBLC6-2SC6Y, SOT-23-6L | C2969755 | Exact manufacturer part; JLC may require an assembly fixture. |
| X1 | Murata CSTNE12M0G55Z000R0, SMD3213-3P | C2659482 | Selected 12 MHz resonator; verify live stock at order placement. |

## Connector sourcing selections

| References | Selected part | LCSC | Decision |
|---|---|---|---|
| P1, P2 | Amass XT30PW-M30.G.Y | C431092 | 2-pin male XT30 power connector; verify pad geometry against the board footprint before ordering. |

## Manual connector sourcing

These connectors remain DNP in the JLCPCB BOM/CPL and are to be bought and
fitted manually.

| References | Selected JST part | Source |
|---|---|---|
| P7, P8 | SM02B-SRSS-TB, 2-position, 1.0 mm, right-angle SMD | DigiKey 926708 |
| P9 | SM04B-SRSS-TB, 4-position, 1.0 mm, right-angle SMD | DigiKey 926710 |
| P6 | SM05B-SRSS-TB, 5-position, 1.0 mm, right-angle SMD | DigiKey 926711 |

P10 remains an unpopulated 2.54 mm through-hole SWD header. It cannot use the
SM04B-SRSS-TB without replacing its PCB footprint and revising the layout.

## Requires circuit decision before sourcing

- R7/R8: DRV8302 OC_ADJ divider selected for an approximately 20 A hot-device
  trip target: R7/RA = 39 kΩ (`C163424`, 0603, Extended), R8/RB = 1 kΩ
  (`C21190`, 0603, Basic). The second-pass review found no verified Basic
  39 kΩ 0603 replacement. Retain this pair: changing R7 alone to 36 kΩ would
  raise the OC_ADJ threshold by 8.1%; changing both to 36 kΩ / 910 Ω would
  keep it within 1.4%, but does not remove the order's Extended-part setup
  because L1, the MOSFETs, and specialised parts remain Extended. Both J1 and
  J2 solder bridges must be closed to connect the divider to OC_ADJ.
- R12/R13: VBUS ADC divider selected as 33 kΩ / 2 kΩ, both 0603 Basic parts
  (`C4216` / `C22975`). Firmware conversion is set to 0.01409912109375 V per
  ADC count for this divider.
- R23/R24: selected TA-I Tech RLP25FEER010, 10 mΩ, 1%, 2 W, 2512
  (`C316229`, Extended). Firmware remains calibrated for 10 mΩ. At 20 A RMS a
  shunt dissipates 4 W, exceeding this component's continuous rating.
- L1: selected SL0650-220M, 22 µH, 3 A rated, 5 A saturation, 98 mΩ,
  7.1 × 6.6 mm (`C22463831`). Exact land-pattern size match to the existing footprint.
- X1: selected Murata CSTNE12M0G55Z000R0, 12 MHz, 30 Ω, 33 pF built-in
  capacitors, SMD3213-3P (`C2659482`, Extended). Firmware HSE_VALUE is 12 MHz.
- USB1: selected GCT USB4105-GF-A-060, USB 2.0 Type-C receptacle, 12 contact,
  right-angle top mount with shell stakes (`C3025063`, Extended). Confirmed by
  user against the existing A40-00119 footprint.

## Excluded by design

J1 and J2 are solder jumpers. P3, P4, and P5 are solder pads; R28–R30 are
unpopulated zero-ohm links; P6–P9 are unpopulated connector footprints; and
P10 is not fitted. They are DNP/not in BOM and need no LCSC purchase assignment.

## CAN filter matching

| References | Selected part | LCSC | Decision |
|---|---|---|---|
| C41, C42 | 220 pF, 50 V, X7R ±10%, 0402 | C1530 | Matched pair for the CAN-H/CAN-L RC filter; Basic and in stock at review. |
