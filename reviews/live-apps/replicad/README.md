# Primitive 3D Modeler (Replicad)

Change the width and hole diameter, build a model, and save editable dimensions.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed through the app picker. Files opened CodeMirror. | [desktop](desktop.png), [Files route](files-route.png) |
| 3,840 × 2,160 | Mouse | Passed | [4k](4k.png) |

The browser CAD preview matched the analytical volume of each box with a 10 mm through-hole. The desktop reopened the exact phone project through the app picker, verified the dimensions, changed the width, and saved a copy. Files sent the native project to CodeMirror. On phone the preview and save controls require scrolling. At 4K the preview stays in a shallow strip near the top of the maximized window.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical touch rotation, export handling and CAD exchange need separate checks.
