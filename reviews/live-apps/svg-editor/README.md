# Vector Editor (SVG-Edit)

Draw a rectangle and save the SVG.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Saved example. Rectangle drag failed. | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Saved example. Rectangle drag failed. | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed with editor picker. Files opened CodeMirror. | [desktop](desktop.png), [Files route](files-route.png) |
| 3,840 × 2,160 | Mouse | Passed | [4k](4k.png) |

A drag produced no rectangle on the phone and tablet layouts. Both could open and save the bundled example. The phone view clips part of that example and compresses the right panel. Files opened the phone SVG in CodeMirror. The SVG editor’s file picker reopened it, and the desktop added a rectangle and saved.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical touch and virtual keyboard behavior remain to be checked.
