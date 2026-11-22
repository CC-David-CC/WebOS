# CADCraft

Open **CAD → CADCraft**. In a narrow window, tap **Line**, tap twice in the drawing and tap **Enter**. **Select** ends the current command. Tap a line to select it and **Erase** to remove it. **Pan** lets you drag the drawing. **Zoom Extents** fits its contents. **Save** writes an editable DXF to Files.

| Browser viewport | Verified interaction | Screenshot |
|---|---|---|
| 390 × 844 | Touch-only drawing, selecting, erasing, panning, fitting the drawing and toggling the palettes. Saved a line and circle, reopened from Files and added a second circle. | [Drawing](draft-phone.png) · [Layers](draft-phone-layers.png) · [Properties](draft-phone-properties.png) |
| 820 × 1,180 | The drawing retained its full width with Layers or Properties open. The same touch editing and native Files workflow passed. | [Tablet](draft-tablet.png) |
| 1,920 × 1,080 | The full desktop command line and docks remained available. Pressing on a line while moving selected it. Delete removed that line and left the circle in the saved DXF. | [Desktop](draft-desktop.png) · [Window selection](moving-pick.png) |
| 3,840 × 2,160 | Repeated the moving selection, saved the drawing, reopened it from Files and added a second circle. | [4K](draft-4k.png) |

Anon used browser Files without issuing any private file requests. On phone and desktop, signed-in users reopened their drawings through Files in fresh browser sessions and saved further edits. Native DXF entities were checked in both account modes.

A 336 × 776 phone canvas provided a 336 × 645 drawing area. Opening a palette reduced its height to 415 pixels. On the tablet, the 766 × 981 drawing area became 766 × 751 with a palette open. Touch pan changed the world center and Zoom Extents fitted the drawing. CADCraft supports 2D plan views. The engine reports 3D orbit as unavailable. [Engine implementation](https://github.com/CC-David-CC/cadcraft/blob/f6052b39d0ca5415a4536d8060681c84b40d084a/crates/engine/src/cmd/exchange.rs#L68)

One automated desktop replay entered `circle`, `20,12` and `3` while running a second software-rendered 4K browser. The circle prompt still requested its center. A retry using the mouse for the center and radius completed and saved both circles. An isolated anonymous 1080p retry with the original typed coordinates also passed, as did the independent signed desktop and anonymous 4K runs. Fast numeric entry on physical hardware remains an open check.

Physical phone or iPad check remains open. Draw a short line, tap it with a finger or pen, erase it, and drag in Pan mode. Check the selected line matches the target and the drawing follows the gesture.

Production viewer `58ff315973a29fcc5d1c330ee87a334f7837903d7ca611415a3b3dc266c1f468` runs WebOS `release/cadcraft-compact-drawing`. At verification, WebOS `main` at `3f541eb6e556` still pinned CADCraft `816d428e8a33`. [CADCraft source](https://github.com/CC-David-CC/cadcraft/commit/f6052b39d0ca5415a4536d8060681c84b40d084a) · [WebOS release](https://github.com/CC-David-CC/WebOS/commit/6cbb75d15dfb43911ebf78b219814a5e33872d06)

## Earlier release

Use the native command line to draw a line and circle, then save a DXF.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch and keyboard | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch and keyboard | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse and keyboard | Passed, including the exact phone project from Files. | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse and keyboard | Passed | [4k](4k.png) |

Both shapes were present in the confirmed server DXF at every size. The fresh desktop opened the exact phone drawing from Files, added a second circle and saved the new DXF. Phone and tablet used a keyboard for geometry and the toolbar Save icon. The navigation cube and narrow tool panels occupy much of the drawing area at the smaller sizes.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical touch precision and editing without a keyboard remain to be checked.
