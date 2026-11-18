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
enables WordCraft and PdfCraft. Unqualified entries use the disabled state when
listed in a candidate menu. Legacy entries remain separate.

The [local Office candidate](CRAFT-INTEGRATION-LOG.md#local-office-release-candidate)
passed 87 exact-package browser checks and a 444-file archive verification.
It enables GridCraft and DeckCraft alongside the two hosted Craft editors.
The other 13 Craft entries remain disabled in that profile.

See [build inputs](CRAFT-BUILD-INPUTS.md) for cache locations, verified pins and
installation details, and the [integration guide](CRAFT-INTEGRATION-GUIDE.md)
for the acceptance contract.

| Category | Application and source | Native workflow | Browser build entry | Menu and qualification |
|---|---|---|---|---|
| Office | [wordcraft](../apps/wordcraft/) `webos/integration` at `edeb4a090cd3` | Rich text and document layout | `webos/build.py` | Live. Signed browser authoring, file round trip and recovery evidence in [WordCraft report](../deploy/WORDCRAFT-DOCUMENTS.md). Apply and qualify the shared AutoSave policy. |
| Office | [pdfcraft](../apps/pdfcraft/) `webos/pdfcraft-blank-chrome` at `a5b512846f59` | PDF editing | `webos/build.py` | Live. Signed browser editing, recovery and verified PDF content in [PdfCraft report](../deploy/PDFCRAFT.md). Apply and qualify the shared AutoSave policy. |
| Office | [gridcraft](../apps/gridcraft/) `webos/gridcraft-document-host` at `fd80ce897bce` | Spreadsheets with formulas and formatting | `webos/build.py` | Locally qualified XLSX workflow. Ten native gates, 27 adapter tests and the combined browser suite pass. A recovered cell remains in formula edit mode until explicit entry. The browser test confirmed retry timing, uncertain-write handling, and exact workspace restoration. Signed inspect and cell operations pass in the separate loopback developer profile. |
| Office | [deckcraft](../apps/deckcraft/) `webos/office-agent-dispatch` at `5b065c4ef93c` | Slides and embedded assets | `webos/build.py` | Locally qualified PPTX workflow at `f8353c0dae8e`. Pending notes recover as unfinished edits. Saved files retain slides, notes, theme and images. The separate agent profile passes eight native gates, 41 adapter tests and actual signed inspection and stable-ID notes editing. Browser-uploaded fonts are session-only. |
| Office | [designcraft](../apps/designcraft/) `webos/integration` at `59c6fa1b4947` | Page layout and publication | `designcraft-web` | Disabled. Build and browser integration pending. Verify workspace references and linked assets. Qualify the page layout workflow. |
| Graphics | [photocraft](../apps/photocraft/) `webos/integration` at `2fec95b0d91b` | Layered raster images and embedded smart objects | `packaging/web/package.sh` | Disabled in release profiles. Development fork `webos/photocraft-document-host` at `d7fba4774bb1` passed 24 signed browser checks, including one warning per dirty refresh, pending Type recovery, Save/Discard/Cancel, timed AutoSave, fresh-browser embedded asset retrieval and same-browser account profile isolation. All 15 classic Desktop checks passed. Active IME and other unfinished tools, external smart-object links and authorized agent operations remain open. |
| Graphics | [vectorcraft](../apps/vectorcraft/) `webos/integration` at `4830ea0e833f` | Vector paths and text | `vectorcraft-web` | Disabled. Build and browser integration pending. Verify font bundle, native project serialization and SVG round-trip limits. |
| Graphics | [figcraft](../apps/figcraft/) `webos/integration` at `bad07e443324` | Interface layouts and components | `figcraft-web` | Disabled. Browser crate resolves offline. Build and browser integration pending. Verify fonts and embedded versus linked assets. |
| Graphics | [lightcraft](../apps/lightcraft/) `webos/integration` at `09a3d20bd722` | Non-destructive photo adjustments | `lightcraft-web` | Disabled. Build and browser integration pending. Verify browser support for source images, adjustment recipes and linked assets. |
| Animation and video | [anicraft](../apps/anicraft/) `webos/integration` at `4e2a2af303d8` | Timeline and vector animation | `anicraft workspace wasm32` | Disabled. Build and browser integration pending. Use the root WASM target. Verify plug-in assets and native project boundaries. |
| Animation and video | [filmcraft](../apps/filmcraft/) `webos/integration` at `e6df31865bc5` | Video timeline and linked media | `filmcraft-web` | Disabled. Build and browser integration pending. Check browser codecs, media references and portable projects. |
| Animation and video | [effectcraft](../apps/effectcraft/) `webos/integration` at `dc2380b070fa` | Compositing and motion graphics | `effectcraft-web` | Disabled. Build and browser integration pending. Verify media, render providers and serialization of referenced compositions. |
| Audio | [soundcraft](../apps/soundcraft/) `webos/integration` at `2688ccac8859` | Multitrack audio projects | `soundcraft-web` | Disabled. Build and browser integration pending. Check audio engine, browser I/O and portable project/session formats. |
| CAD | [cadcraft](../apps/cadcraft/) `webos/integration` at `67514021aedf` | Drafting and drawing documents | `cadcraft-web` | Disabled. Build and browser integration pending. Verify drawing formats, renderer and supported editing/export workflows. |
| CAD | [solidcraft](../apps/solidcraft/) `webos/integration` at `a5b35abd133e` | Parametric solid modeling | `solidcraft-web` | Disabled. Build and browser integration pending. Verify kernel, browser renderer and parametric project fidelity. |
| Materials and textures | [texturecraft](../apps/texturecraft/) `webos/integration` at `8c82502c3261` | Texture editing with geometry and maps | `texturecraft-web` | Disabled. Build and browser integration pending. Verify translation pin and project geometry, textures and linked resources. |
| Materials and textures | [materialcraft](../apps/materialcraft/) `webos/integration` at `6f19501a4bcc` | Procedural material graphs | `materialcraft-web` | Disabled. Build and browser integration pending. Verify graph inputs, project format and renderer. CLI 0.2.130 verified locally. |
