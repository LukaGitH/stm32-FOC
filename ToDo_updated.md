# To Do

## Schematic value display cleanup

- Change every component so the schematic displays the standard `Value` field instead of `ALTIUM_VALUE`.
- This is required because some displayed values are outdated, for example capacitors still shown as `560pF` even though their actual `Value` has changed.
- After the change, verify that the visible schematic values match each component's actual `Value` field.
- Keep the `ALTIUM_VALUE` field in the component data, but disable its visibility on the schematic.
- Enable visibility of the standard `Value` field instead.

## Connector sourcing

Use the following DigiKey parts:

- **P7, P8** — JST `SM02B-SRSS-TB`  
  DigiKey: https://www.digikey.si/en/products/detail/jst-sales-america-inc/SM02B-SRSS-TB/926708

- **P9, P10** — JST `SM04B-SRSS-TB`  
  DigiKey: https://www.digikey.si/en/products/detail/jst-sales-america-inc/SM04B-SRSS-TB/926710

- **P6** — JST `SM05B-SRSS-TB`  
  DigiKey: https://www.digikey.si/en/products/detail/jst-sales-america-inc/SM05B-SRSS-TB/926711

> **P10 note:** its existing PCB footprint is a 2.54 mm through-hole SWD
> header, not a 1.0 mm JST-SH footprint. Replacing it with
> `SM04B-SRSS-TB` requires a deliberate PCB footprint/layout change.

## Not fitted

- **R28, R29, R30** are not placed.
- Mark them as `DNP` / excluded from assembly and ensure they do not appear as fitted parts in the assembly BOM.

## Inductor verification

- **L1** — check whether the intended part is LCSC **C22463831** (`TECHFUSE SL0650-220M`).
- Verify its inductance, current ratings, dimensions, and footprint against the existing L1 schematic and PCB data before assigning it.

Verified 2026-07-23: `C22463831` is assigned as `SL0650-220M`, 22 µH, 3 A
rated current, 5 A saturation current, 98 mΩ DCR, 7.1 × 6.6 mm. It matches the
existing L1 footprint and its schematic requirements.
