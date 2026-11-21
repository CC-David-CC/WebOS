# CADCraft

Use the native command line to draw a line and circle, then save a DXF.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch and keyboard | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch and keyboard | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse and keyboard | Passed, including the exact phone project from Files. | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse and keyboard | Passed | [4k](4k.png) |

Both shapes were present in the confirmed server DXF at every size. The fresh desktop opened the exact phone drawing from Files, added a second circle and saved the new DXF. Phone and tablet used a keyboard for geometry and the toolbar Save icon. The navigation cube and narrow tool panels occupy much of the drawing area at the smaller sizes.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical touch precision and editing without a keyboard remain to be checked.
