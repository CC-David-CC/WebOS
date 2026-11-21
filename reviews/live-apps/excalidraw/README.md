# Sketch Board (Excalidraw)

Draw a rectangle and save an editable Excalidraw drawing.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed with editor picker. Files opened CodeMirror. | [desktop](desktop.png), [Files route](files-route.png) |
| 3,840 × 2,160 | Mouse | Passed | [4k](4k.png) |

With a shape selected, the first press on the compact menu sometimes left it closed. A second press opened the save actions during the phone and tablet checks. Files opened the phone drawing in CodeMirror. The Sketch Board picker reopened it with its original rectangle, and the desktop added a second rectangle and saved.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical touch and virtual keyboard behavior remain to be checked.
