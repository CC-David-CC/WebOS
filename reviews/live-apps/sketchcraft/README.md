# SketchCraft

[Production touch modeling, Files reopen and the updated screenshots](compact-solid.md)

## Earlier baseline

Draw a rectangle and use Push / Pull to extrude it 3 m. Save the native model.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Failed. The viewport had zero area. | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Failed. The saved model contained zero faces. | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse and keyboard | Passed | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse and keyboard | Passed | [4k](4k.png) |

Both desktop sizes produced six editable faces and a 3 m height in the account file. The phone canvas was 0 × 0 with the Outliner and Document panels filling the window. The tablet displayed a narrow viewport. The toolbar placed Push / Pull in its overflow, and a keyboard-assisted retry saved a model with zero faces. No phone-authored model was available for a desktop round trip.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. A usable phone view, touch precision on tablet, and phone-to-desktop authoring remain open.
