# Diagram Editor (diagrams.net)

Open the test diagram, edit its shape label and save an account draw.io file.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed with editor picker. Files opened CodeMirror. | [desktop](desktop.png), [Files route](files-route.png) |
| 3,840 × 2,160 | Mouse | Passed | [4k](4k.png) |

The label changed and the account save succeeded at all four sizes. Files opened the phone diagram in CodeMirror. Diagram Editor’s own file picker reopened the phone diagram with its saved label, and the desktop edited and saved it again.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical touch and virtual keyboard behavior remain to be checked.
