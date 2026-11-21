# PCBCraft

Open the Dual LED example through account Files, place a resistor on the schematic and save the native project.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch and keyboard | Opened the Symbol tool and placed R5 in the visible part of the sheet. Docked panels left a small area for schematic editing. | [Phone](phone.png) · [Parts Catalog](phone-resistor-picker.png) |
| 820 × 1,180 | Emulated touch and keyboard | Placed R5 and verified the saved symbol, wires and footprints. | [Tablet](tablet.png) |
| 1,920 × 1,080 | Mouse and keyboard | Reopened the exact phone file through Files, placed R6 and saved a separate copy. | [1080p](desktop.png) |
| 3,840 × 2,160 | Mouse and keyboard | Placed and saved R5. The default zoom left the circuit small relative to the canvas. | [4K](4k.png) |

The native archive retained the existing wires and all 14 board footprints. The saved phone project had 17 symbols, and a fresh desktop saved 18 without changing the phone revision. The phone used the visible Symbol and Place buttons and an emulated keyboard to search for the resistor. A tap over the Properties panel did not place the symbol. Touch-only search, readable compact controls and board editing on actual hardware remain open.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`.
