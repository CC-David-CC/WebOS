# FigCraft

Use the Rectangle shortcut to place a 100 × 100 shape and save its editable native project.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch and keyboard | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch and keyboard | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse and keyboard | Passed, including the exact phone project from Files. | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse and keyboard | Passed | [4k](4k.png) |

The editor displayed the shape and the saved archive contained its rectangle record at each size. A fresh desktop opened the exact phone account file from Files, added a second rectangle and saved the updated design. The phone and tablet used the same keyboard shortcuts against their compact canvas.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Drawing shapes by physical touch, working with multiple pages and export remain to be checked.
