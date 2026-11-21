# Electronics Design (designElectronics)

Move components in the Arduino LED example and save the changed native project.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch and keyboard | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch and keyboard | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse and keyboard | Passed through the app picker. Files opened CodeMirror. | [desktop](desktop.png), [Files route](files-route.png) |
| 3,840 × 2,160 | Mouse and keyboard | Passed in three-view mode | [4k](4k.png) |

Selected part positions changed at every size. The normal editor save operation produced a native project with matching placements on the account server. The test invoked the editor’s Open and Save As bridge and used the visible file dialogs to select paths. A fresh desktop reopened the exact phone design, verified its positions, moved parts again and saved a copy. Files sent the .dez to CodeMirror. The 4K test displayed breadboard, schematic and PCB together and edited the shared project. Phone toolbar captions run together below the PCB when the window is narrow.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical touch editing, simulation, and fabrication output remain to be checked.
