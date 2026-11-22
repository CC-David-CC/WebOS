# Mesh Editor (Mesh:Tool)

[Updated production Files workflow and screenshots](../fabrication-files/README.md)

Add the example cube, verify its dimensions and save an editable mesh workspace.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed through the editor picker. Files opened CodeMirror. | [desktop](desktop.png), [Files route](files-route.png) |
| 3,840 × 2,160 | Mouse | Passed | [4k](4k.png) |

The cube measured 20 units on all axes, and the account snapshot contained the saved mesh. The desktop opened the same phone .meshproj through the editor picker, verified the restored model, added another and saved the result. Files opened the phone workspace in CodeMirror. On phone, the log and selection panels occupy part of a small build area. At 4K the initial view leaves the mesh small relative to the available canvas.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical touch transforms, mesh repairs and downstream STL exchange remain to be reviewed.
