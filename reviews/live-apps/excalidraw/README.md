# Sketch Board (Excalidraw)

November 22 follow-up: native Files launch and editing in both account modes passed on ksu.codes. [Updated checks and screenshots](../drawing-workspace-files/README.md)

Draw a rectangle and save an editable Excalidraw drawing.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed with editor picker. Files opened CodeMirror. | [desktop](desktop.png), [Files route](files-route.png) |
| 3,840 × 2,160 | Mouse | Passed | [4k](4k.png) |

With a shape selected, the first press on the compact menu sometimes left it closed. A second press opened the save actions during the phone and tablet checks. Files opened the phone drawing in CodeMirror. The Sketch Board picker reopened it with its original rectangle, and the desktop added a second rectangle and saved.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical touch and virtual keyboard behavior remain to be checked.

## November 22 compact menu verification

On ksu.codes, Sketch Board now opens its file menu on the first tap immediately after a drawing gesture. The menu scrolls within the app window on a tablet. Before the fix the tablet menu measured 874 pixels tall inside a 460-pixel editor and placed Save above the window.

Chromium completed eight consecutive **draw rectangle → tap menu once → Save drawing as → verify saved scene** cycles at 390 × 844 and eight at 820 × 1180. A swipe across the menu button did not activate it. Keyboard focus and Enter opened and closed the same menu. The desktop native edit, Files reopen, account promotion and fresh signed-in edit also passed, with zero private requests while Anon. A stale selection still produced the recovery prompt. Physical touchscreen testing remains open. [Phone](save-menu-390.png) · [Tablet](save-menu-820.png)

Deployed viewer `96934975f3bfd49048f41225c28fbfd1fd63f2230c44c850420e0eaa213c2819` uses `release/compact-menu-touch`. Only the Excalidraw submodule pin changed from the preceding release. WebOS `main` still carries the earlier pin. [WebOS b06e5d64](https://github.com/CC-David-CC/WebOS/commit/b06e5d649ae7a4e0801a3fbb5676c3da90f991da) · [Excalidraw c7a504de](https://github.com/CC-David-CC/excalidraw/commit/c7a504dea1cc4529fcf71f982a9da3fbd9ab608f)
