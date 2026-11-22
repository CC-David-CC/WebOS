# Electronics Design (designElectronics)

## Verified production release

On November 22, 2026, normal Files opened the selected native .dez design under both Anon and a disposable signed-in account. Each browser edited the project in the native application, used its Save As menu, and reopened the copy through Files. Each copy contained the saved placements and notes. The source file retained its original SHA-256. Both signed-in runs verified server bytes and reopened from an independent browser session. The anonymous runs observed zero requests to the private file endpoints.

| Browser viewport | Input and account | Verified | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch, Anon and signed in | PCB tools wrap into distinct buttons. Tap Schematic, add a note, use Share to save a copy, reopen it in Files. | [PCB toolbar](release-phone-anon-project.png), [signed-in reopen](release-phone-signed-reopened.png) |
| 820 × 1180 | Emulated touch, Anon | Schematic note editing and the native Save As menu work at tablet size. | [Tablet](release-tablet-anon-project.png) |
| 1920 × 1080 | Mouse and keyboard, signed in | Moved the selected geometry and reopened it after a fresh sign-in. In a separate mouse test, Edit → Select All followed by Rotate left and Rotate right changed and restored the part placements. | [Reopened project](release-desktop-signed-reopened.png), [Rotate controls](release-rotation-labels.png) |
| 3840 × 2160 | Mouse and keyboard, Anon | Show three views, switch back, move the geometry, save through the native Export menu, and reopen. | [Three views](release-4k-anon-three-views.png) |

The deployed viewer was `e898472b6adbbdefc52f4193bb94d0b84c4e1615bb7c067909906d3c90c43fe9`. All 20 assets in the public Electronics Design registry entry matched their recorded hashes. Five file-association tests passed. Registered submodules and release source are available at [Electronics Design b71de8e](https://github.com/CC-David-CC/electronics-design/commit/b71de8ea7407a30c71ba37a96b254c57abd7ad06), [Desktop 856f0ed](https://github.com/CC-David-CC/desktop/commit/856f0ed5ce65dd3830ad03625fb2c17ef5ed189e), and [WebOS 7f79885](https://github.com/CC-David-CC/WebOS/commit/7f7988575f674986a13c07a915c1f2cf133071b1).

The remaining hardware check is a physical phone or tablet touch target and legibility review. The native editor still asks for a different filename on Save As to protect original files containing unsupported parts.

## Previous review

Move components in the Arduino LED example and save the changed native project.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch and keyboard | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch and keyboard | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse and keyboard | Passed through the app picker. Files opened CodeMirror. | [desktop](desktop.png), [Files route](files-route.png) |
| 3,840 × 2,160 | Mouse and keyboard | Passed in three-view mode | [4k](4k.png) |

Selected part positions changed at every size. The normal editor save operation produced a native project with matching placements on the account server. The test invoked the editor’s Open and Save As bridge and used the visible file dialogs to select paths. A fresh desktop reopened the exact phone design, verified its positions, moved parts again and saved a copy. Files sent the .dez to CodeMirror. The 4K test displayed breadboard, schematic and PCB together and edited the shared project. Phone toolbar captions run together below the PCB when the window is narrow.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical touch editing, simulation, and fabrication output remain to be checked.
