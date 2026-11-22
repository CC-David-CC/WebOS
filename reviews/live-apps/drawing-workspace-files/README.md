# Drawing editors and WebOS Files

On November 22, 2026, ksu.codes served WebOS release `7d86ccfa3808b63d812b3526890f665810c29d4dc0238dd5836fc0409ebac75e`. A double-click in Files opened each saved drawing in its native editor. The four editors displayed a local save confirmation as Anon. After account registration, a new signed-in browser reopened the same bytes and could edit the project again. Chromium reported zero page errors and zero private file requests during the four guest workflows.

| Editor | Operation verified on ksu.codes | Published component | Screenshot |
|---|---|---|---|
| Image Editor | Resized a PNG to 320, 360 and 400 pixels across save and reopen. Also opened real JPEG files with both extensions and a WebP through Files, then inspected their decoded dimensions. | [5124a05c](https://github.com/CC-David-CC/image-editor/commit/5124a05c49b6b984677469513fa4e058ee1420a5) | [Image and resize tool](image-editor.png) |
| SVG-Edit | Drew a rectangle, reopened the SVG, added shapes and saved the editable vector file. | [420bd0e3](https://github.com/CC-David-CC/svg-editor/commit/420bd0e32977eb6824f2aa8b7f915a463c94f80b) | [Reopened SVG](svg-editor.png) |
| Excalidraw | Saved a native scene and added a rectangle after each reopen. The final file contained three rectangles. | [aef7e4a0](https://github.com/CC-David-CC/excalidraw/commit/aef7e4a04f5fc4e6ad8879b0854a081f98db8b88) | [Reopened scene](excalidraw.png) |
| diagrams.net | Edited the visible label in a native draw.io diagram, saved and reopened it from Files, and edited it again in a fresh signed-in session. | [019db807](https://github.com/CC-David-CC/diagrams-net/commit/019db807059aeb1ed5d8ac0b4b12fb46aa891f49) | [Reopened diagram](diagrams-net.png) |

In a separate check, each editor rejected a launch with an outdated file hash. Choosing Retry loaded the current file. Its saved bytes still matched the original.

## Compact layouts

On Chromium with emulated touch at 390 and 820 pixels wide, one tap selected Rectangle, dragging drew a shape, a second toolbar tap opened the alternatives, and choosing Square drew another shape. The built-in example fit entirely inside the visible drawing area at both widths. The Image Editor’s **Editing tools** button exposed **Resize** and its numeric field at 390 pixels. [Phone SVG](svg-example-phone.png) · [Tablet SVG](svg-example-tablet.png) · [Image Editor on phone](image-editor-phone.png)

On a physical phone or iPad, try those same two SVG tools. With VoiceOver or TalkBack enabled, open Image Editor, create a blank image and navigate to **Editing tools → Resize**. Physical touch and screen-reader speech remain unverified. Excalidraw’s separate compact menu issue reproduced on the second draw-and-save cycle at 390 × 844. Its desktop and Files results above passed. The [subsequent compact menu release](../excalidraw/README.md#november-22-compact-menu-verification) fixed this case.

## Build and source pins

The Desktop and WebOS commits are on `release/drawing-workspace-files`. Each application commit is on its own `webos/drawing-workspace-files` branch. Independent fetches matched all five submodule pins and Git mode 160000. WebOS `main` at `3f541eb6` still pinned the earlier components. [WebOS 98ce1562](https://github.com/CC-David-CC/WebOS/commit/98ce1562a765ded5c22a5222c9ee3a482c3b3b03) · [Desktop 9704de49](https://github.com/CC-David-CC/desktop/commit/9704de49eed2bfbb973e3e2ed022016dc539be3d)

The runtime app builder inventoried 3,712 files for the four applications. The normal viewer build supplied the updated Desktop shell and Files entry. All 16 routing and launch checks passed, as did the 12 existing component reference checks. Staging verified the changed payload hashes and reused 3,519 identical files from the preceding release. Production readback matched the manifest, all five component pins and 13 served payloads, including the five app entry points.

For a manual replay, open **Apps → Diagramming**, create and save a drawing, close its window, and double-click the saved file in **Files**. Add a shape and save it under a second name. Create an account from that Anon session, sign in in a fresh browser, then double-click the second file and continue editing.
