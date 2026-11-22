# Embroidery Studio (StitchFoundry)


## Workspace save status

Anonymous project saves and embroidery exports now say “in this browser tab.” The signed-in export reports that the local copy is syncing with the server. Chromium checked both messages on the hosted build, including a 1,073-byte DST in each role. The guest made zero private file requests. A fresh signed-in browser reopened the edited design and exported it again.

[Guest export](save-feedback-guest.png) · [Signed-in export](save-feedback-signed.png) · [StitchFoundry source](https://github.com/CC-David-CC/embroidery-studio/commit/c7476a36ea4e073317507cc7f5cfc60db060fc20) · [WebOS assembly](https://github.com/CC-David-CC/WebOS/commit/6bc24cfb19b81ec761890d0925b7815b55d08bd3)

Verified viewer `08ab239a55ccd5b26dfc87538630a1cc0fc54fb737509f19b9a6d476d2adb629`.

## Native Files on ksu.codes

Verified on November 22 in the production viewer `9a79203991300cb148012a9ff02da4fc4fb32bda57e789463d41c8a031ddca8c`. Both anonymous and signed-in users can reopen the editable project by double-clicking it in Files.

A guest saved the stitched rectangle example and reopened it from Files. Placing an SVG added two objects, taking the design from two to four. The guest saved the edited design, registered an account and reopened the same 28,510-byte native file from a fresh signed-in browser. Each export produced a 1,073-byte Tajima DST with a valid header.

The anonymous session made zero private file requests. Both roles completed without a browser page error. The readback SHA-256 of the signed project was `fa5976710b7f7daf1e5703f9daa6fa2262da81c68609e599fc1e18a09360f352`.

The preview or File menu was accessible in Chromium at 390 × 844, 820 × 1,180, 1,920 × 1,080 and 3,840 × 2,160. Physical touch placement and sewing the exported design remain unverified. The phone artboard layout has a separate follow-up.

[Guest workflow](native-guest.png) · [Signed-in workflow](native-signed.png) · [Phone viewport](native-phone.png)

[App source](https://github.com/CC-David-CC/embroidery-studio/commit/d281b23e3edeea48deda3f5b7763d0b6b032ce02) · [Desktop source](https://github.com/CC-David-CC/desktop/commit/ec6c8c93b31e6d191e9ca517054c8a2582038ad8) · [WebOS assembly](https://github.com/CC-David-CC/WebOS/commit/f3c156265094e856e6edce1d91fa12b785288b42)

## Initial review

Open the stitched rectangle example, save the native design, and export stitches.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed through the app picker. Files opened CodeMirror. | [desktop](desktop.png), [Files route](files-route.png) |
| 3,840 × 2,160 | Mouse | Passed | [4k](4k.png) |

All four sessions exported a 1,073-byte Tajima DST with a valid header. The desktop reopened the exact phone project through the studio picker, then saved a copy and exported stitches again. Files opened the native project in CodeMirror. The phone’s tools and side panels leave only a narrow strip of artboard in view.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical touch placement and drawing, resizing the artboard, and actual test sewing need separate checks.
