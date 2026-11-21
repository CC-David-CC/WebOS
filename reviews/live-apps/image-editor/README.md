# Image Editor (Filerobot)

Create a blank PNG, change its dimensions and save it to My files.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed with editor picker. Files opened CodeMirror. | [desktop](desktop.png), [Files route](files-route.png) |
| 3,840 × 2,160 | Mouse | Passed | [4k](4k.png) |

The compact toolbar exposes Resize through its unlabeled menu button. In a fresh desktop browser, Files opened CodeMirror and failed to decode the PNG. Image Editor’s own Open from My files loaded the exact 320 × 240 phone PNG. The editor then saved a 360 × 270 copy.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical touch and virtual keyboard behavior remain to be checked.
