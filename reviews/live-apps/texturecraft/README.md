# TextureCraft

Import a UV-mapped OBJ, paint its native 2D canvas and save the editable texture project.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch and keyboard | Saved the OBJ and visibly painted UV tiles with File → Save. | [phone](phone.png) |
| 820 × 1,180 | Emulated touch and keyboard | The project saved, but it contained zero paint tiles after the attempted stroke. | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse and keyboard | Opened the exact phone-saved project, added another stroke and verified changed paint tiles. | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse and keyboard | Saved the exact OBJ and one verified UV paint stroke. | [4k](4k.png) |

The test opened the visible device picker, used the F3 shortcut for 2D view and painted with pointer input. The phone saved through the native File menu. A fresh signed desktop opened the exact phone revision in Files and saved a copy with an additional stroke. Archive checks compared the original mesh and individual paint tiles. On tablet, the visible Save menu confirmed a project containing the OBJ and zero paint tiles, and the screenshot showed no stroke. Earlier touch keyboard shortcuts did not open the save picker after the canvas interaction. Physical touch and stylus painting, compact layouts without a keyboard and GPU-backed rendering remain open.

Tested in Chromium with a disposable account on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`.
