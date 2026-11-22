# AniCraft

Open **Animation & Video → AniCraft**. In a narrow window, tap **Rectangle**, drag on the white stage, then tap **+ Frame** to extend its exposure. **Timeline**, **Properties**, and **Tools** open beneath the stage. Tap the same button again to close its panel. **Play** runs the timeline and changes to **Stop**. **Save** writes an editable `.anicraft` project to Files.

| Browser viewport | Input and result | Screenshot |
|---|---|---|
| 390 × 844 | Emulated touch. Drew a rectangle, extended its exposure to 19 frames, opened the timeline and properties, saved, reopened from Files and drew another rectangle. | [Drawing](phone.png) · [Timeline](phone-timeline.png) · [Properties](phone-properties.png) |
| 820 × 1,180 | Tablet touch and native tool shortcuts. Used the docked workspace, saved with the File menu and continued drawing after reopening. | [Tablet](tablet.png) |
| 1,920 × 1,080 | Mouse and keyboard. Drew a rectangle, inserted a frame and saved. Reopened the same native file and added another rectangle. | [Desktop](desktop.png) |
| 3,840 × 2,160 | Mouse and keyboard. Used the full-size docked editor for the same two-edit workflow. | [4K](4k.png) |

The original review measured 52 pixels of white stage. The release replay measured 64 pixels before the fix and 272 pixels after it at the same 390-pixel viewport. The native canvas was 336 pixels wide. The compact layout starts below 560 logical pixels and retains the saved desktop dock arrangement. [Original phone layout](phone-default-panels.png)

Anon saved and reopened in the same browser tab with zero private file requests. A signed-in phone saved to account Files and reopened the exact bytes in a fresh browser session. Reopening preserved the 19-frame exposure. In both roles the editable native element count increased from five to ten after adding the second outlined rectangle. A separate playback check observed the **Play → Stop → Play** button transitions on a longer timeline.

Physical phone and pen targeting remain open. On a touch device, draw a rectangle, extend its exposure, tap **Play**, and tap **Stop** while it is playing. Check the drawing lands under the finger or pen and the stop control responds.

Verified on ksu.codes with viewer `c96e5ee2d75779768a381c49f119e0bb78bd412df6d917f1e57f3d1e73107459`. WebOS `release/anicraft-compact-stage` pins the native app on `webos/compact-stage`. [AniCraft source](https://github.com/CC-David-CC/anicraft/commit/b7549429a69e10521fdf078233a4e64b8829bc47) · [WebOS release](https://github.com/CC-David-CC/WebOS/commit/6f60e93ce781c8d0e44530406685fe2e6a434da7)
