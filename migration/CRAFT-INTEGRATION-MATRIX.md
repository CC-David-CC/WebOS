# Craft integration matrix

All 18 selected source repositories are present at their selected pins under
`/path/to/webos/apps/`. The
original 17 passed locked offline Cargo fetch for browser WASM and native Linux
using the existing laptop SDK. SketchCraft has since passed locked WASM
dependency fetch and a locked offline compile check for its Rust core.

The listed workflow for a pending app is its first acceptance target. Each app
must prove native content fidelity, account saves, recovery and fresh browser
retrieval before it is enabled. A passing dependency fetch does not exercise
build scripts, assets, linking or browser behavior.

Source organization is complete. The integration phase covers all 18 apps.
The rollout is paused at the MaterialCraft native checkpoint while we discuss
the SolidCore cases.

| Stage | Count | Applications |
|---|---:|---|
| Enabled on ksu.codes | 15 | WordCraft, PdfCraft, GridCraft, DeckCraft, PhotoCraft, FigCraft, VectorCraft, AniCraft, LightCraft, DesignCraft, SoundCraft, FilmCraft, EffectCraft, CADCraft, TextureCraft |
| Paused with a tested local candidate | 1 | SolidCraft |
| WASM check and focused native account tests passed, browser package pending | 1 | MaterialCraft |
| Organized source, queued for integration | 1 | SketchCraft |

The [live launcher profile](https://ksu.codes/viewer-profile.json) also enables
Files, Text (CodeMirror 6), Calculator and Help on the classic Desktop. The
[live release manifest](https://ksu.codes/viewer-release.json) identifies the
TextureCraft release at parent commit `f256e740a415`.
Three Craft entries are disabled in the hosted Desktop, including SketchCraft in
the CAD menu. For the rest of the organized
project, see the [full source and application matrix](APP-MATRIX.md), which
covers the 86 app repositories, platform components, shared engines, tools,
libraries and games.

After the remaining Craft integrations, the next approved priority is Files
previews. Load the original account file through Storage and render it in
the current browser. Keep preview data in memory and release it on close
or sign-out. Previewing creates no account file or shared saved state.

The [TextureCraft release](CRAFT-INTEGRATION-LOG.md#texturecraft-release-on-ksucodes)
passed 104 exact-package Chromium checks and matched 675 hosted files. The
account round trip preserved the original mesh and editable paint tiles.

The [CADCraft release](CRAFT-INTEGRATION-LOG.md#cadcraft-release-on-ksucodes)
passed 112 exact-package Chromium checks and matched 664 hosted files.
The native DXF round trip kept editable line, circle and dimension geometry.

The [EffectCraft release](CRAFT-INTEGRATION-LOG.md#effectcraft-release-on-ksucodes)
passed 200 exact-package browser checks. Hosted verification matched 653 files
and started the native editor. A fresh account browser retrieved hashed
footage and rendered the expected pixels. Closing the editor stopped its workers.

The [FilmCraft release](CRAFT-INTEGRATION-LOG.md#filmcraft-release-on-ksucodes)
passed 117 exact-package browser checks. Hosted verification matched 637 files
and started the native editor. The linked-video workflow retrieves the original
from account storage and exports the expected full-resolution PNG.

The [SoundCraft release](CRAFT-INTEGRATION-LOG.md#soundcraft-release-on-ksucodes)
passed 185 exact-package browser checks and two focused native tests. Hosted
verification matched 623 files and started the native editor.

The [DesignCraft release](CRAFT-INTEGRATION-LOG.md#designcraft-release-on-ksucodes)
passed 178 exact-package browser checks and 39 native linked-media and UI
checks. Hosted verification matched 611 files and started the native editor.

The [AniCraft release](CRAFT-INTEGRATION-LOG.md#anicraft-release-on-ksucodes)
passed 33 final-candidate browser checks. Byte comparison verified continuity
of the prior candidate's retained editor regression results. Hosted
verification matched 588 files and confirmed native editor startup.

The [VectorCraft release](CRAFT-INTEGRATION-LOG.md#vectorcraft-release-on-ksucodes)
passed 42 exact-package browser checks and 543-file hosted verification.
Hosted Chromium started the editor with the exact published WASM.

The [FigCraft release](CRAFT-INTEGRATION-LOG.md#figcraft-release-on-ksucodes)
passed 140 exact-package browser checks and 505-file hosted verification.
Hosted Chromium compiled its WASM and received the native ready packet.

The [PhotoCraft release](CRAFT-INTEGRATION-LOG.md#photocraft-release-on-ksucodes)
passed 28 browser account workflow checks and 463-file hosted verification.
Hosted Chromium compiled its WASM.

The [Office release](CRAFT-INTEGRATION-LOG.md#office-release-on-ksucodes) passed
87 exact-package browser checks locally, 444-file verification on the host,
and a hosted Chromium check of the login, both editor modules and their WASM.

See [build inputs](CRAFT-BUILD-INPUTS.md) for cache locations, verified pins and
installation details, and the [integration guide](CRAFT-INTEGRATION-GUIDE.md)
for the acceptance contract.

| Category | Application and source | Native workflow | Browser build entry | Menu and qualification |
|---|---|---|---|---|
| Office | [wordcraft](../apps/wordcraft/) `webos/integration` at `edeb4a090cd3` | Rich text and document layout | `webos/build.py` | Live. Signed browser authoring, file round trip and recovery evidence in [WordCraft report](../deploy/WORDCRAFT-DOCUMENTS.md). Apply and qualify the shared AutoSave policy. |
| Office | [pdfcraft](../apps/pdfcraft/) `webos/pdfcraft-blank-chrome` at `a5b512846f59` | PDF editing | `webos/build.py` | Live. Signed browser editing, recovery and verified PDF content in [PdfCraft report](../deploy/PDFCRAFT.md). Apply and qualify the shared AutoSave policy. |
| Office | [gridcraft](../apps/gridcraft/) `webos/gridcraft-document-host` at `fd80ce897bce` | Spreadsheets with formulas and formatting | `webos/build.py` | Live XLSX workflow. Ten native gates, 27 adapter tests and the combined browser suite pass. A recovered cell remains in formula edit mode until explicit entry. The browser test confirmed retry timing, uncertain-write handling and exact workspace restoration. Signed inspect and cell operations pass in the separate loopback developer profile. |
| Office | [deckcraft](../apps/deckcraft/) `webos/office-agent-dispatch` at `5b065c4ef93c` | Slides and embedded assets | `webos/build.py` | Live PPTX workflow. Pending notes recover as unfinished edits. Saved files retain slides, notes, theme and images. Signed inspection and stable-ID notes editing pass in the separate loopback profile. Browser-uploaded fonts are session-only. |
| Office | [designcraft](../apps/designcraft/) `webos/integration` at `afca6f8d0f9a` | Page layout and publication | `designcraft-web` | Live `.designcraft` workflow. Signed Chromium proved frame edits and Undo, account Save and Save As, refresh recovery, Files Open, full-resolution artwork embedding and a verified PDF export after fresh-browser reopen. |
| Graphics | [photocraft](../apps/photocraft/) at `403994fc5f41` | Layered raster images and embedded smart objects | `packaging/web/package.sh` | Live `.pcraft` workflow. Passed 19 native account tests and 28 actual browser workflow checks, including nested recovery, embedded layers and IME protection. Scoped inspection and layer rename were verified in the separate signed loopback profile. |
| Graphics | [vectorcraft](../apps/vectorcraft/) `webos/integration` at `09ee69a08736` | Vector paths and text | `vectorcraft-web` | Live `.vectorcraft` workflow. The exact package passed native editing, Save/Save As, recovery, fresh-browser reopen and scoped layer rename with native Undo in the opt-in loopback profile. The selected tree passed 22,139 stable native tests and 16 remaining CI stages. |
| Graphics | [figcraft](../apps/figcraft/) `webos/integration` at `cf78eb22978c` | Interface layouts and components | `packaging/web/build-account.sh` | Live `.figcraft` workflow. The exact release passed 12 Desktop account checks and signed layer rename with native Undo in the opt-in loopback profile. The selected tree passed 5,877 stable native tests across R730 and the laptop, plus Clippy and the standard WASM gate. |
| Graphics | [lightcraft](../apps/lightcraft/) `webos/integration` at `ef00c97ec7f4` | Non-destructive photo adjustments | `cargo xtask web` from repo root | Live `.lightcraft` workflow. The native build passed 56 tests. Signed Chromium proved import, independent windows, scoped photo rating, account Save and Save As, and draft recovery. A fresh context reopened the copy from Files and rendered the original fetched from account storage. All 601 hosted files matched and hosted Chromium started the editor. |
| Animation and video | [anicraft](../apps/anicraft/) `webos/integration` at `04610927977e` | Timeline and vector animation | `scripts/build-web.sh` and root WASM target | Live `.anicraft` workflow. Browser qualification covered timeline edits, PNG/WAV media, Save and Save As, recovery, fresh-browser reopen, PNG export fidelity and scoped editing with native Undo. The native workspace passed 1,624 tests with two failures reproduced on upstream involving the timeline header width and system font names. |
| Animation and video | [filmcraft](../apps/filmcraft/) `webos/filmcraft-account-project` at `b7ba79c366e6` | Video timeline and linked media | `filmcraft-web` | Live `.fcproj` workflow. The native editor saved and reopened linked video, recovered local edits, decoded the original in a fresh Chromium context and exported a verified PNG. |
| Animation and video | [effectcraft](../apps/effectcraft/) `webos/effectcraft-account-composition` at `78f11b7fc1ce` | Compositing and motion graphics | `effectcraft-web` | Live editable `.ecproj` composition with linked still images. Scoped native composition edit and Undo, manual Save and Save As, browser draft recovery, fresh-browser rendering and worker disposal passed. |
| Audio | [soundcraft](../apps/soundcraft/) at `e196254ee15f` | Multitrack audio projects | `soundcraft-web` | Live portable `.scraftz` workflow. Signed Chromium confirmed native track edits, Save and Save As, local recovery, reopening from Files, exact sample fidelity and playback through WebAudio. |
| CAD | [cadcraft](../apps/cadcraft/) `webos/cadcraft-account-drawing` at `816d428e8a33` | Drafting and drawing documents | `cadcraft-web` | Live editable 2D DXF. Scoped native geometry and Undo, Save and Save As, local recovery, Files activation and a fresh-browser account round trip passed. |
| CAD | [solidcraft](../apps/solidcraft/) `webos/solidcraft-account-part` at `7b7716fba56c` | Parametric solid modeling | `solidcraft-web` | Paused by user request. The local candidate passed six browser account checks for editable `.sc` parts. Four native geometry failures produced identical results on the original source. The hosted menu entry remains disabled. |
| CAD | [sketchcraft](../apps/sketchcraft/) at `3a895db54c8a` | Push/pull 3D modeling, `.sketchcraft` projects | React/Tauri `app/`, Rust `core/` and [local browser development](../apps/sketchcraft/docs/dev/building.md) | Queued in position 18. The Rust core passed its baseline WASM compile check. The upstream Vite interface uses a local development bridge. Qualify the hosted browser engine, native commands and account document model before enabling the app. |
| Materials and textures | [texturecraft](../apps/texturecraft/) `webos/texturecraft-account-project` at `3ada1e30108a` | Mesh painting and embedded texture data | `texturecraft-web` | Live. The tested account project kept the original mesh bytes, paint layers and editable tiles. Save, Save As, recovery and fresh-browser editing passed. Broader mesh, bake and export workflows still need qualification. |
| Materials and textures | [materialcraft](../apps/materialcraft/) from `6f19501a4bcc` | Procedural material graphs with embedded bitmaps | `materialcraft-web` | The `webos/materialcraft-account-graph` worktree passed locked WASM compilation with native graph editing and the `.mcraft` account adapter. Native checks and an exact browser round trip are pending. |
