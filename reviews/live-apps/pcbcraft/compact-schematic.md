# PCBCraft schematic on phones and 4K displays

Opening Dual LED now frames the circuit. On a narrow phone, the Browser, Properties and Selection filters panels start closed. The View ribbon reopens them. A wider window restores the wide layout. The Fit command frames the whole sheet.

| Production check | Result |
|---|---|
| 390 × 844, Anon and signed in | Opened the fixture through Files, tapped Symbol, searched for a resistor, tapped Place and placed R5. Green traces span 240 pixels on the phone canvas, up from 46. |
| 820 × 1180 and 1920 × 1080, Anon | Opened, edited, saved and reopened the native schematic. Each Anon run recorded zero requests for private account files. |
| 3840 × 2160, signed in | Trace width increased from 374 to 2499 pixels. The Browser, Properties and Selection filters remained visible. |
| Native storage | All five saved projects preserved the original wires and all 14 board footprints. Each stored schematic had 17 symbols and reopened with identical bytes. Signed-in tests reopened from a fresh browser context. |

The published WebOS release branch is `release/pcbcraft-compact-schematic`, with PCBCraft on `webos/compact-schematic-fit`. At verification, WebOS main still pinned PCBCraft at `2348195417bf`.

Tests used headless Chromium with emulated phone and tablet input. On a physical phone, the remaining checks are entering the part name with the on-screen keyboard and tapping the placement point.

[Phone](compact-phone.png) · [Part search](compact-parts.png) · [4K](compact-4k.png) · [Verification data](compact-schematic.json) · [PCBCraft source](https://github.com/CC-David-CC/pcbcraft/commit/8290b73bf17dc2b8c6608b326fe207f13dbefdce) · [WebOS release](https://github.com/CC-David-CC/WebOS/commit/bb4fd2c30890d7860c3a59faaa23e2320f3ea92e)
