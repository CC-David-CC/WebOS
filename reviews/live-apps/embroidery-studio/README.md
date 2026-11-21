# Embroidery Studio (StitchFoundry)

Open the stitched rectangle example, save the native design, and export stitches.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed through the app picker. Files opened CodeMirror. | [desktop](desktop.png), [Files route](files-route.png) |
| 3,840 × 2,160 | Mouse | Passed | [4k](4k.png) |

All four sessions exported a 1,073-byte Tajima DST with a valid header. The desktop reopened the exact phone project through the studio picker, then saved a copy and exported stitches again. Files opened the native project in CodeMirror. The phone’s tools and side panels leave only a narrow strip of artboard in view.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical touch placement and drawing, resizing the artboard, and actual test sewing need separate checks.
