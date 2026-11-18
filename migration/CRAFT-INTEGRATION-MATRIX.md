# Craft integration matrix

All 17 selected source repositories are present. The pinned Cargo graphs for
all 17 passed `cargo fetch --locked --offline --target wasm32-unknown-unknown`
after populating the existing laptop SDK. GridCraft and DeckCraft show the
reviewed local component commits selected in the parent.

The listed workflow for a pending app is its first acceptance target. Each app
must prove native content fidelity, account saves, recovery and fresh browser
retrieval before it is enabled. A passing dependency fetch does not exercise
build scripts, assets, linking or browser behavior.

The classic Desktop source contains all 17 entries. The current hosted release
enables WordCraft and PdfCraft. Unqualified entries use the disabled state when
listed in a candidate menu. Legacy entries remain separate.

See [build inputs](CRAFT-BUILD-INPUTS.md) for cache locations, verified pins and
installation details, and the [integration guide](CRAFT-INTEGRATION-GUIDE.md)
for the acceptance contract.

| Category | Application and source | Native workflow | Browser build entry | Menu and qualification |
|---|---|---|---|---|
| Office | [wordcraft](../apps/wordcraft/) `webos/integration` at `edeb4a090cd3` | Rich text and document layout | `webos/build.py` | Live. Signed browser authoring, file round trip and recovery evidence in [WordCraft report](../deploy/WORDCRAFT-DOCUMENTS.md). Apply and qualify the shared AutoSave policy. |
| Office | [pdfcraft](../apps/pdfcraft/) `webos/pdfcraft-blank-chrome` at `a5b512846f59` | PDF editing | `webos/build.py` | Live. Signed browser editing, recovery and verified PDF content in [PdfCraft report](../deploy/PDFCRAFT.md). Apply and qualify the shared AutoSave policy. |
| Office | [gridcraft](../apps/gridcraft/) `webos/gridcraft-document-host` at `7f6e3ff709f0` | Spreadsheets with formulas and formatting | `webos/build.py` | Local candidate. All 10 native CI gates and 27 host/recovery tests passed. The 26-file exact-source WASM package is verified. Complete the account browser run and combined-profile checks. |
| Office | [deckcraft](../apps/deckcraft/) `webos/deckcraft-document-host` at `d22ee90a8b5d` | Slides and embedded assets | `webos/build.py` | Local candidate. All 8 native CI gates passed again after the retry-delay fix. The preceding candidate passed account browser round trips with embedded media, stale and uncertain saves, refresh recovery, later edits and the presenter popup. Complete browser checks with the new retry behavior. |
| Office | [designcraft](../apps/designcraft/) `webos/integration` at `59c6fa1b4947` | Page layout and publication | `designcraft-web` | Disabled. Build and browser integration pending. Verify workspace references and linked assets. Qualify the page layout workflow. |
| Graphics | [photocraft](../apps/photocraft/) `webos/integration` at `2fec95b0d91b` | Layered raster images | `photocraft-web, photocraft-web-boot` | Disabled. Build and browser integration pending. Verify exact fonts, translations, worker packaging and layered-image project serialization. |
| Graphics | [vectorcraft](../apps/vectorcraft/) `webos/integration` at `4830ea0e833f` | Vector paths and text | `vectorcraft-web` | Disabled. Build and browser integration pending. Verify font bundle, native project serialization and SVG round-trip limits. |
| Graphics | [figcraft](../apps/figcraft/) `webos/integration` at `bad07e443324` | Interface layouts and components | `figcraft-web` | Disabled. Build and browser integration pending. Verify missing workspace declaration, fonts and embedded versus linked assets. |
| Graphics | [lightcraft](../apps/lightcraft/) `webos/integration` at `09a3d20bd722` | Non-destructive photo adjustments | `lightcraft-web` | Disabled. Build and browser integration pending. Verify browser support for source images, adjustment recipes and linked assets. |
| Animation and video | [anicraft](../apps/anicraft/) `webos/integration` at `4e2a2af303d8` | Timeline and vector animation | `anicraft workspace wasm32` | Disabled. Build and browser integration pending. Use the root WASM target. Verify plug-in assets and native project boundaries. |
| Animation and video | [filmcraft](../apps/filmcraft/) `webos/integration` at `e6df31865bc5` | Video timeline and linked media | `filmcraft-web` | Disabled. Build and browser integration pending. Check browser codecs, media references and portable projects. |
| Animation and video | [effectcraft](../apps/effectcraft/) `webos/integration` at `dc2380b070fa` | Compositing and motion graphics | `effectcraft-web` | Disabled. Build and browser integration pending. Verify media, render providers and serialization of referenced compositions. |
| Audio | [soundcraft](../apps/soundcraft/) `webos/integration` at `2688ccac8859` | Multitrack audio projects | `soundcraft-web` | Disabled. Build and browser integration pending. Check audio engine, browser I/O and portable project/session formats. |
| CAD | [cadcraft](../apps/cadcraft/) `webos/integration` at `67514021aedf` | Drafting and drawing documents | `cadcraft-web` | Disabled. Build and browser integration pending. Verify drawing formats, renderer and supported editing/export workflows. |
| CAD | [solidcraft](../apps/solidcraft/) `webos/integration` at `a5b35abd133e` | Parametric solid modeling | `solidcraft-web` | Disabled. Build and browser integration pending. Verify kernel, browser renderer and parametric project fidelity. |
| Materials and textures | [texturecraft](../apps/texturecraft/) `webos/integration` at `8c82502c3261` | Texture editing with geometry and maps | `texturecraft-web` | Disabled. Build and browser integration pending. Verify translation pin and project geometry, textures and linked resources. |
| Materials and textures | [materialcraft](../apps/materialcraft/) `webos/integration` at `6f19501a4bcc` | Procedural material graphs | `materialcraft-web` | Disabled. Build and browser integration pending. Verify graph inputs, project format and renderer. CLI 0.2.130 verified locally. |
