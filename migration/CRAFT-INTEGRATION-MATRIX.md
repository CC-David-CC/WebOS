# Craft integration matrix

All 17 selected source repositories are present, with every tracked path at
its selected pin. All 17 passed locked offline Cargo fetch for browser WASM
and native Linux using the existing laptop SDK. GridCraft and DeckCraft show
the reviewed local component commits selected in the parent.

The listed workflow for a pending app is its first acceptance target. Each app
must prove native content fidelity, account saves, recovery and fresh browser
retrieval before it is enabled. A passing dependency fetch does not exercise
build scripts, assets, linking or browser behavior.

The classic Desktop source contains all 17 entries. The current hosted release
enables WordCraft, PdfCraft, GridCraft, DeckCraft and PhotoCraft. The other 12 Craft entries
use the disabled state. Legacy entries remain separate.

The [PhotoCraft release](CRAFT-INTEGRATION-LOG.md#photocraft-release-on-ksucodes)
passed 28 browser account workflow checks and 463-file hosted verification.
Hosted Chromium compiled its WASM. VectorCraft and FigCraft are being prepared in parallel.

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
| Office | [designcraft](../apps/designcraft/) `webos/integration` at `59c6fa1b4947` | Page layout and publication | `designcraft-web` | Disabled. Build and browser integration pending. Verify workspace references and linked assets. Qualify the page layout workflow. |
| Graphics | [photocraft](../apps/photocraft/) at `403994fc5f41` | Layered raster images and embedded smart objects | `packaging/web/package.sh` | Live `.pcraft` workflow. Passed 19 native account tests and 28 actual browser workflow checks, including nested recovery, embedded layers and IME protection. Scoped inspection and layer rename were verified in the separate signed loopback profile. |
| Graphics | [vectorcraft](../apps/vectorcraft/) `webos/integration` at `4830ea0e833f` | Vector paths and text | `vectorcraft-web` | Disabled. The isolated integration branch passed four native account regressions. Linked WASM packaging and browser qualification are underway. |
| Graphics | [figcraft](../apps/figcraft/) `webos/integration` at `bad07e443324` | Interface layouts and components | `figcraft-web` | Disabled. The isolated integration branch passed four native account regressions and a locked WASM compile check. Linked packaging and browser qualification are underway. |
| Graphics | [lightcraft](../apps/lightcraft/) `webos/integration` at `09a3d20bd722` | Non-destructive photo adjustments | `lightcraft-web` | Disabled. Build and browser integration pending. Verify browser support for source images, adjustment recipes and linked assets. |
| Animation and video | [anicraft](../apps/anicraft/) `webos/integration` at `4e2a2af303d8` | Timeline and vector animation | `anicraft workspace wasm32` | Disabled. Build and browser integration pending. Use the root WASM target. Verify plug-in assets and native project boundaries. |
| Animation and video | [filmcraft](../apps/filmcraft/) `webos/integration` at `e6df31865bc5` | Video timeline and linked media | `filmcraft-web` | Disabled. Build and browser integration pending. Check browser codecs, media references and portable projects. |
| Animation and video | [effectcraft](../apps/effectcraft/) `webos/integration` at `dc2380b070fa` | Compositing and motion graphics | `effectcraft-web` | Disabled. Build and browser integration pending. Verify media, render providers and serialization of referenced compositions. |
| Audio | [soundcraft](../apps/soundcraft/) `webos/integration` at `2688ccac8859` | Multitrack audio projects | `soundcraft-web` | Disabled. Build and browser integration pending. Check audio engine, browser I/O and portable project/session formats. |
| CAD | [cadcraft](../apps/cadcraft/) `webos/integration` at `67514021aedf` | Drafting and drawing documents | `cadcraft-web` | Disabled. Build and browser integration pending. Verify drawing formats, renderer and supported editing/export workflows. |
| CAD | [solidcraft](../apps/solidcraft/) `webos/integration` at `a5b35abd133e` | Parametric solid modeling | `solidcraft-web` | Disabled. Build and browser integration pending. Verify kernel, browser renderer and parametric project fidelity. |
| Materials and textures | [texturecraft](../apps/texturecraft/) `webos/integration` at `8c82502c3261` | Texture editing with geometry and maps | `texturecraft-web` | Disabled. Build and browser integration pending. Verify translation pin and project geometry, textures and linked resources. |
| Materials and textures | [materialcraft](../apps/materialcraft/) `webos/integration` at `6f19501a4bcc` | Procedural material graphs | `materialcraft-web` | Disabled. Build and browser integration pending. Verify graph inputs, project format and renderer. CLI 0.2.130 verified locally. |

## Added after the initial queue

| Category | Application and source | Native workflow | Upstream entry | Qualification |
|---|---|---|---|---|
| CAD | [SketchCraft](../apps/sketchcraft/) at `3a895db54c8a` | Push/pull 3D modeling, `.sketchcraft` projects | React/Tauri `app/`, Rust `core/` and [local browser development](../apps/sketchcraft/docs/dev/building.md) | Source checkout verified. Position 18, after the initial 17. WebOS integration and browser tests are pending. |
