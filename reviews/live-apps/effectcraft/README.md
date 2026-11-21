# EffectCraft

Create and save an editable composition from a small color plate, retaining the linked original in account storage.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch and keyboard | Imported the PNG, dragged it into Composition and saved the one-layer project. The Composition panel was a narrow strip and the preview was effectively unusable. | [Phone](phone.png) |
| 820 × 1,180 | Emulated touch and keyboard | Created and saved the same one-layer composition. The viewer and time ruler were crowded by the docked panels. | [Tablet](tablet.png) |
| 1,920 × 1,080 | Mouse and keyboard | Reopened the exact phone file through Files, verified the rendered colors, duplicated its layer and saved a separate two-layer copy. | [1080p](desktop.png) |
| 3,840 × 2,160 | Mouse and keyboard | Created, rendered and saved the one-layer composition in the maximized window. | [4K](4k.png) |

At every size, **New Composition From Footage** imported the PNG but left Composition empty. Dragging the Project item into the empty Composition panel created the editable layer. The saved document and its linked original were read back from the server. The desktop copy retained the same original digest and left the phone file byte for byte intact. Physical touch, visible compact Save controls and usable compact composition playback remain open.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`.
