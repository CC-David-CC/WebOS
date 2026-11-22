# Primitive 3D Modeler (Replicad)

## Native Files on ksu.codes

Verified on November 22 in the production viewer `9a79203991300cb148012a9ff02da4fc4fb32bda57e789463d41c8a031ddca8c`. Both anonymous and signed-in users can reopen the editable project by double-clicking it in Files.

A guest built a 47 × 40 × 20 mm box, saved its native parameters, and reopened the project by double-clicking it in Files. The guest changed the width to 53 mm. After account registration, the user changed it to 67 mm. A fresh signed-in browser reopened the same 154-byte file and calculated a solid volume of 53,600 mm³.

The anonymous session made zero private file requests. Both roles completed without a browser page error. The readback SHA-256 of the signed project was `d8395525f52ee4563928e6433abab4c075fd0f28c9b7d15b9810642300590679`.

The preview or File menu was accessible in Chromium at 390 × 844, 820 × 1,180, 1,920 × 1,080 and 3,840 × 2,160. Physical touch rotation and CAD exchange remain unverified. The wide-window preview height is tracked separately.

[Guest workflow](native-guest.png) · [Signed-in workflow](native-signed.png) · [Phone viewport](native-phone.png)

[App source](https://github.com/CC-David-CC/replicad/commit/005c746c66290fbdd64cb6e4f1b72ff9c1db474f) · [Desktop source](https://github.com/CC-David-CC/desktop/commit/ec6c8c93b31e6d191e9ca517054c8a2582038ad8) · [WebOS assembly](https://github.com/CC-David-CC/WebOS/commit/f3c156265094e856e6edce1d91fa12b785288b42)

## Initial review

Change the width and hole diameter, build a model, and save editable dimensions.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed through the app picker. Files opened CodeMirror. | [desktop](desktop.png), [Files route](files-route.png) |
| 3,840 × 2,160 | Mouse | Passed | [4k](4k.png) |

The browser CAD preview matched the analytical volume of each box with a 10 mm through-hole. The desktop reopened the exact phone project through the app picker, verified the dimensions, changed the width, and saved a copy. Files sent the native project to CodeMirror. On phone the preview and save controls require scrolling. At 4K the preview stays in a shallow strip near the top of the maximized window.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical touch rotation, export handling and CAD exchange need separate checks.
