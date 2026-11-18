# Craft integration matrix

All 18 selected source repositories are present at their selected pins under
`/home/dflanag3/Projects/WebOS/apps/`. The
original 17 passed locked offline Cargo fetch for browser WASM and native Linux
using the existing laptop SDK. SketchCraft has since passed locked WASM
dependency fetch and a locked offline compile check for its Rust core.

The listed workflow for a pending app is its first acceptance target. Each app
must prove native content fidelity, account saves, recovery and fresh browser
retrieval before it is enabled. A passing dependency fetch does not exercise
build scripts, assets, linking or browser behavior.

Source organization is complete. The active phase integrates the 18 apps from
their independent repositories and rolls out each qualified app to ksu.codes
under the user's approval.

| Stage | Count | Applications |
|---|---:|---|
| Enabled on ksu.codes | 9 | WordCraft, PdfCraft, GridCraft, DeckCraft, PhotoCraft, FigCraft, VectorCraft, AniCraft, LightCraft |
| Native account integration underway | 1 | DesignCraft |
| Organized source, queued for integration | 8 | SoundCraft, FilmCraft, EffectCraft, CADCraft, SolidCraft, TextureCraft, MaterialCraft, SketchCraft |

The [live launcher profile](https://ksu.codes/viewer-profile.json) also enables
Files, Text (CodeMirror 6), Calculator and Help on the classic Desktop. The
[live release manifest](https://ksu.codes/viewer-release.json) identifies the
AniCraft release at parent commit `c180c37cd7d0`.
Ten Craft entries are disabled in the hosted Desktop, including SketchCraft in
the CAD menu. For the rest of the organized
project, see the [full source and application matrix](APP-MATRIX.md), which
covers the 86 app repositories, platform components, shared engines, tools,
libraries and games.

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
| Office | [designcraft](../apps/designcraft/) `webos/integration` at `59c6fa1b4947` | Page layout and publication | `designcraft-web` | Disabled. The R730 passed the native account Open, Save confirmation and draft recovery tests at `5b0e1ecc` on `webos/designcraft-document-host`. The earlier UI adoption commit `f470a35f` passed locked WASM compilation. Signed browser account wiring, linked artwork and PDF export remain. See the [branch plan](CRAFT-BRANCH-PLANS.md#designcraft-preparation). |
| Graphics | [photocraft](../apps/photocraft/) at `403994fc5f41` | Layered raster images and embedded smart objects | `packaging/web/package.sh` | Live `.pcraft` workflow. Passed 19 native account tests and 28 actual browser workflow checks, including nested recovery, embedded layers and IME protection. Scoped inspection and layer rename were verified in the separate signed loopback profile. |
| Graphics | [vectorcraft](../apps/vectorcraft/) `webos/integration` at `09ee69a08736` | Vector paths and text | `vectorcraft-web` | Live `.vectorcraft` workflow. The exact package passed native editing, Save/Save As, recovery, fresh-browser reopen and scoped layer rename with native Undo in the opt-in loopback profile. The selected tree passed 22,139 stable native tests and 16 remaining CI stages. |
| Graphics | [figcraft](../apps/figcraft/) `webos/integration` at `cf78eb22978c` | Interface layouts and components | `packaging/web/build-account.sh` | Live `.figcraft` workflow. The exact release passed 12 Desktop account checks and signed layer rename with native Undo in the opt-in loopback profile. The selected tree passed 5,877 stable native tests across R730 and the laptop, plus Clippy and the standard WASM gate. |
| Graphics | [lightcraft](../apps/lightcraft/) `webos/integration` at `ef00c97ec7f4` | Non-destructive photo adjustments | `cargo xtask web` from repo root | Live `.lightcraft` workflow. The native build passed 56 tests. Signed Chromium proved import, independent windows, scoped photo rating, account Save and Save As, and draft recovery. A fresh context reopened the copy from Files and rendered the original fetched from account storage. All 601 hosted files matched and hosted Chromium started the editor. |
| Animation and video | [anicraft](../apps/anicraft/) `webos/integration` at `04610927977e` | Timeline and vector animation | `scripts/build-web.sh` and root WASM target | Live `.anicraft` workflow. Browser qualification covered timeline edits, PNG/WAV media, Save and Save As, recovery, fresh-browser reopen, PNG export fidelity and scoped editing with native Undo. The native workspace passed 1,624 tests with two failures reproduced on upstream involving the timeline header width and system font names. |
| Animation and video | [filmcraft](../apps/filmcraft/) `webos/integration` at `e6df31865bc5` | Video timeline and linked media | `filmcraft-web` | Disabled. Build and browser integration pending. Check browser codecs, media references and portable projects. |
| Animation and video | [effectcraft](../apps/effectcraft/) `webos/integration` at `dc2380b070fa` | Compositing and motion graphics | `effectcraft-web` | Disabled. Build and browser integration pending. Verify media, render providers and serialization of referenced compositions. |
| Audio | [soundcraft](../apps/soundcraft/) `webos/integration` at `2688ccac8859` | Multitrack audio projects | `soundcraft-web` | Disabled. Build and browser integration pending. Check audio engine, browser I/O and portable project/session formats. |
| CAD | [cadcraft](../apps/cadcraft/) `webos/integration` at `67514021aedf` | Drafting and drawing documents | `cadcraft-web` | Disabled. Build and browser integration pending. Verify drawing formats, renderer and supported editing/export workflows. |
| CAD | [solidcraft](../apps/solidcraft/) `webos/integration` at `a5b35abd133e` | Parametric solid modeling | `solidcraft-web` | Disabled. Build and browser integration pending. Verify kernel, browser renderer and parametric project fidelity. |
| CAD | [sketchcraft](../apps/sketchcraft/) at `3a895db54c8a` | Push/pull 3D modeling, `.sketchcraft` projects | React/Tauri `app/`, Rust `core/` and [local browser development](../apps/sketchcraft/docs/dev/building.md) | Queued in position 18. The Rust core passed its baseline WASM compile check. The upstream Vite interface uses a local development bridge. Qualify the hosted browser engine, native commands and account document model before enabling the app. |
| Materials and textures | [texturecraft](../apps/texturecraft/) `webos/integration` at `8c82502c3261` | Texture editing with geometry and maps | `texturecraft-web` | Disabled. Build and browser integration pending. Verify translation pin and project geometry, textures and linked resources. |
| Materials and textures | [materialcraft](../apps/materialcraft/) `webos/integration` at `6f19501a4bcc` | Procedural material graphs | `materialcraft-web` | Disabled. Build and browser integration pending. Verify graph inputs, project format and renderer. CLI 0.2.130 verified locally. |
