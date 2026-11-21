# VectorCraft

Draw a rectangle with the native tool and save its editable vector project.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch and keyboard | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch and keyboard | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse and keyboard | Passed, including the exact phone project from Files. | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse and keyboard | Passed | [4k](4k.png) |

The account project contained the expected editable paths at all four sizes. A fresh desktop opened the byte-identical phone project through Files, added a second rectangle and saved the updated project. It opened at the small saved zoom. The first 4K run timed out taking a screenshot, and the standalone retry completed the task and capture. The phone path used emulated touch for drawing and keyboard shortcuts for tool selection and saving. Physical touch, editing without a keyboard and 4K performance on hardware remain open.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`.
