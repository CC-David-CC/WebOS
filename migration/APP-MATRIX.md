# WebOS source and application matrix

All locations are relative to `/home/dflanag3/Projects/WebOS/`. Each row is one independent Git repository selected by the parent. **124 source owners: 85 app repositories and 39 supporting repositories.** The app total includes 7 planned game cores, 1 PCB research prototype and 1 application template; it is not 85 finished apps.

The original Desktop/Workspace viewer is `platform/desktop/active-system/`. All 92 files matched the captured original at source correction. Later authorized test-site integration changes bootstrap/account/app wiring; CSS, reference data and artwork remain unchanged. The unsolicited replacement is removed. See deploy/VIEWER-TEST.md for the scoped running composition; this inventory is not an all-app deployment claim.

Priority measures contribution to a functional personal WebOS, not popularity. These are reviewed planning priorities, not a dependency resolver. A specialized app still needs its own lower-priority engine. Categories describe ownership and purpose; the interfaces column separately describes human use, browser work, server authority and cross-app/file interaction.

| Priority | Meaning |
|---|---|
| P0 | Foundation: authority, storage, runtime and policy |
| P1 | Essential usable desktop and file/edit workflow |
| P2 | General productivity or a dependency needed for it |
| P3 | Specialized capability or optional environment/service |
| P4 | Games, activities and their supporting/planned code |
| P5 | Unused historical source |

Every row has source on disk. The state distinguishes what remains before producing or integrating it:

| State | Meaning |
|---|---|
| S | Source and declared build/entry located; not build-qualified this pass |
| Q | Later scoped current-viewer release qualified; see its report for scope and limits |
| B | Source organized; composition/interface port remains |
| I | Source organized with an explicit external-input/rebuild gap |
| P | Planned model core; no completed app |
| X | Research prototype; no completed browser app |
| T | App template |
| H | Unused historical source |

**S does not mean built, runnable in the current desktop, account synchronized, agent complete or deployed.** Full builds were deliberately not run for this organization pass. Required dependency acquisition and historical build evidence are distinct from this source check.

| Category | Repositories |
|---|---|
| WebOS core | 4 |
| WebOS desktop and essential apps | 6 |
| Office and document apps | 7 |
| Creative and media apps | 18 |
| Engineering and developer apps | 17 |
| Optional execution environments | 3 |
| Shared browser tools and engines | 19 |
| Shared native and guest engines | 5 |
| Craft shared source, assets and build tools | 5 |
| Optional platform services and policy | 2 |
| App templates | 1 |
| Games and interactive activities | 28 |
| Games shared code | 1 |
| Planned game cores | 7 |
| Unused legacy source | 1 |

## WebOS core

| Priority / state | Component and purpose | Source location | Existing interfaces | Source/build entry | Remaining qualification or gap |
|---|---|---|---|---|---|
| P0 / S | accounts — Account identity, sign-in policy and file grants | [platform/accounts/](../platform/accounts/) | Server authority; browser client; Runtime protocol; Storage grants | [src/webos_accounts/service.py](../platform/accounts/src/webos_accounts/service.py)<br>[browser/client.mjs](../platform/accounts/browser/client.mjs)<br>Recipe: python-js | Not build-qualified in this source-only pass. |
| P0 / S | network-policy — Reusable login/egress/proxy policy source | [libraries/network-policy/](../libraries/network-policy/) | Accounts/login and Browser relay policy; library only, installing starts no firewall or service | [pyproject.toml](../libraries/network-policy/pyproject.toml)<br>[README.md](../libraries/network-policy/README.md)<br>Recipe: python | Not build-qualified in this source-only pass. |
| P0 / S | runtime — App lifecycle, launcher, commands and document contracts | [platform/runtime/](../platform/runtime/) | Desktop; app hosting; shared human/agent operation primitives; browser cache; account-file wire protocol | [active-system/assets/desktop/app-instance.mjs](../platform/runtime/active-system/assets/desktop/app-instance.mjs)<br>[active-system/assets/desktop/apps.mjs](../platform/runtime/active-system/assets/desktop/apps.mjs)<br>Recipe: python-js | Not build-qualified in this source-only pass. |
| P0 / S | storage — Account file persistence, revisions, transfer and browser mirror | [platform/storage/](../platform/storage/) | Server filesystem/SQLite; Accounts proofs; browser file client; app file access | [src/webos_storage/__init__.py](../platform/storage/src/webos_storage/__init__.py)<br>[src/webos_storage/client.mjs](../platform/storage/src/webos_storage/client.mjs)<br>Recipe: python-js | Not build-qualified in this source-only pass. |

## WebOS desktop and essential apps

| Priority / state | Component and purpose | Source location | Existing interfaces | Source/build entry | Remaining qualification or gap |
|---|---|---|---|---|---|
| P1 / S | calculator — Arithmetic utility and app-hosting check | [apps/calculator/](../apps/calculator/) | Human mouse/keyboard input; Runtime window lifecycle; old source also has file hooks | [apps/system/calculator/index.mjs](../apps/calculator/apps/system/calculator/index.mjs)<br>[apps/system/calculator/math.mjs](../apps/calculator/apps/system/calculator/math.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P1 / S | desktop — The original Desktop/Workspace viewer | [platform/desktop/](../platform/desktop/) | Human workspace/window controls; Runtime app launcher; account and file hooks; original optional guest bootstrap | [active-system/index.html](../platform/desktop/active-system/index.html)<br>[active-system/app.js](../platform/desktop/active-system/app.js)<br>Recipe: js | Existing viewer has a qualified six-app composition including PdfCraft using unchanged CSS/reference/artwork. Broad app integration remains separate; see [PdfCraft qualification](../deploy/PDFCRAFT.md). |
| P1 / S | files — Account file browser and app file launcher | [apps/files/](../apps/files/) | Human file UI; Storage; upload/download/browser APIs; file associations; ZIP tool | [apps/system/files/index.mjs](../apps/files/apps/system/files/index.mjs)<br>[src/controller.mjs](../apps/files/src/controller.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P1 / S | help — Desktop/account-file usage guide | [apps/help/](../apps/help/) | Human guide and contextual buttons; Runtime view lifecycle | [apps/system/help/index.mjs](../apps/help/apps/system/help/index.mjs)<br>[webos/index.mjs](../apps/help/webos/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P1 / S | login — Sign-in and registration presentation | [platform/login/](../platform/login/) | Human credential entry; Accounts client; public session result | [src/index.mjs](../platform/login/src/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P1 / S | text — Plain text and code editing | [apps/text/](../apps/text/) | Files open/save; Storage; CodeMirror; document/lifecycle hooks | [index.mjs](../apps/text/index.mjs)<br>[webos/index.mjs](../apps/text/webos/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |

## Office and document apps

| Priority / state | Component and purpose | Source location | Existing interfaces | Source/build entry | Remaining qualification or gap |
|---|---|---|---|---|---|
| P2 / S | deckcraft — Presentation authoring | [apps/deckcraft/](../apps/deckcraft/) | Browser WASM app; shared Craft host crate/fonts; explicit file and document-operation integration on our branch | [apps/deckcraft-web/Cargo.toml](../apps/deckcraft/apps/deckcraft-web/Cargo.toml)<br>[Cargo.toml](../apps/deckcraft/Cargo.toml)<br>Recipe: craft-web | Not build-qualified in this source-only pass. |
| P2 / S | document-editor — Existing Tiptap rich document editor; retained beside WordCraft | [apps/document-editor/](../apps/document-editor/) | Account file JSON documents; PDF export and PDF Viewer launch; existing browser host | [index.mjs](../apps/document-editor/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P2 / S | gridcraft — Spreadsheet authoring | [apps/gridcraft/](../apps/gridcraft/) | Browser WASM app; shared Craft code/fonts; host/account-file integration still to qualify | [apps/gridcraft-web/Cargo.toml](../apps/gridcraft/apps/gridcraft-web/Cargo.toml)<br>[Cargo.toml](../apps/gridcraft/Cargo.toml)<br>Recipe: craft-web | Not build-qualified in this source-only pass. |
| P2 / S | pdf-viewer — Read and search PDFs | [apps/pdf-viewer/](../apps/pdf-viewer/) | Account files; browser rendering; PDF.js dependency; existing browser host | [index.mjs](../apps/pdf-viewer/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P2 / Q | pdfcraft — PDF authoring and manipulation | [apps/pdfcraft/](../apps/pdfcraft/) | Native browser PDF engine; shared account Storage; Desktop activation; account-scoped recovery/preferences | [webos/build.py](../apps/pdfcraft/webos/build.py)<br>[webos/index.mjs](../apps/pdfcraft/webos/index.mjs)<br>[Cargo.toml](../apps/pdfcraft/Cargo.toml)<br>Recipe: craft-web | Core account Open/edit/Save/Save As/recovery and window lifecycle deployed to ksu.codes. Advanced tools/capacity and clean-PDF window restoration remain separate; see [PdfCraft qualification](../deploy/PDFCRAFT.md). |
| P2 / S | spreadsheet — Existing Jspreadsheet/SheetJS spreadsheet app | [apps/spreadsheet/](../apps/spreadsheet/) | Account files; XLSX worker; CSV import/export; existing browser host | [index.mjs](../apps/spreadsheet/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P2 / Q | wordcraft — Rich document authoring | [apps/wordcraft/](../apps/wordcraft/) | Browser WASM app; shared Craft crates/fonts; WebOS file/operation integration on our branch | [webos/build.py](../apps/wordcraft/webos/build.py)<br>[apps/wordcraft-web/Cargo.toml](../apps/wordcraft/apps/wordcraft-web/Cargo.toml)<br>[Cargo.toml](../apps/wordcraft/Cargo.toml)<br>Recipe: craft-web | Qualified and deployed Browse/account filename selection; all9 native stages,38 JS and56 actual checks each locally/hosted. All13 export writers pass smoke checks; seven still rebind and the export menu uses automatic names. See [current Browse/export report](../deploy/WORDCRAFT-SAVEAS.md); prior print/Design qualification remains recorded. |

## Creative and media apps

| Priority / state | Component and purpose | Source location | Existing interfaces | Source/build entry | Remaining qualification or gap |
|---|---|---|---|---|---|
| P3 / S | anicraft — Animation authoring | [apps/anicraft/](../apps/anicraft/) | Browser WASM; shared Craft formats/media/UI; file/host integration to qualify | [Cargo.toml](../apps/anicraft/Cargo.toml)<br>[packaging/web/package.sh](../apps/anicraft/packaging/web/package.sh)<br>Recipe: craft-web | Not build-qualified in this source-only pass. |
| P3 / S | audio-editor — Existing AudioMass audio editor | [apps/audio-editor/](../apps/audio-editor/) | Account WAV files; per-window frame; audio decode/export worker | [index.mjs](../apps/audio-editor/index.mjs)<br>[prepare.py](../apps/audio-editor/prepare.py)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | designcraft — Page/layout design | [apps/designcraft/](../apps/designcraft/) | Browser WASM; shared Craft code/fonts; file/host integration to qualify | [apps/designcraft-web/Cargo.toml](../apps/designcraft/apps/designcraft-web/Cargo.toml)<br>[Cargo.toml](../apps/designcraft/Cargo.toml)<br>Recipe: craft-web | Cargo metadata previously passed; unused helper/testkit path declarations reference missing directories. Full browser build remains unqualified. |
| P3 / S | diagrams-net — Diagram editing | [apps/diagrams-net/](../apps/diagrams-net/) | Account drawio files; per-window editor frame and file bridge | [index.mjs](../apps/diagrams-net/index.mjs)<br>[prepare.py](../apps/diagrams-net/prepare.py)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | effectcraft — Visual effects authoring | [apps/effectcraft/](../apps/effectcraft/) | Browser WASM; shared Craft media/rendering code; file/host integration to qualify | [apps/effectcraft-web/Cargo.toml](../apps/effectcraft/apps/effectcraft-web/Cargo.toml)<br>[Cargo.toml](../apps/effectcraft/Cargo.toml)<br>Recipe: craft-web | Not build-qualified in this source-only pass. |
| P3 / I | embroidery-studio — StitchFoundry embroidery editor adapter | [apps/embroidery-studio/](../apps/embroidery-studio/) | Account project/machine files; local WASM editor build and frame/file bridge | [index.mjs](../apps/embroidery-studio/index.mjs)<br>[prepare.py](../apps/embroidery-studio/prepare.py)<br>Recipe: js | Adapter and pinned source build recipe retained; StitchFoundry source must be acquired separately. Historical archive WASM source provenance remains unresolved. |
| P3 / S | excalidraw — Sketch-style diagram editing | [apps/excalidraw/](../apps/excalidraw/) | Account drawing files; browser React editor | [index.mjs](../apps/excalidraw/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | figcraft — Interface and vector design | [apps/figcraft/](../apps/figcraft/) | Browser WASM; shared Craft code/fonts; file/host integration to qualify | [apps/figcraft-web/Cargo.toml](../apps/figcraft/apps/figcraft-web/Cargo.toml)<br>[Cargo.toml](../apps/figcraft/Cargo.toml)<br>Recipe: craft-web | Cargo metadata previously passed; unused helper/testkit path declarations reference missing directories. Full browser build remains unqualified. |
| P3 / S | filmcraft — Video editing | [apps/filmcraft/](../apps/filmcraft/) | Browser WASM; shared Craft media code; file/host integration to qualify | [apps/filmcraft-web/Cargo.toml](../apps/filmcraft/apps/filmcraft-web/Cargo.toml)<br>[Cargo.toml](../apps/filmcraft/Cargo.toml)<br>Recipe: craft-web | Not build-qualified in this source-only pass. |
| P3 / S | image-editor — Existing Filerobot image editor | [apps/image-editor/](../apps/image-editor/) | Account image files; browser-local React/canvas processing | [index.mjs](../apps/image-editor/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | lightcraft — Photo/light processing | [apps/lightcraft/](../apps/lightcraft/) | Browser WASM; shared Craft image code; file/host integration to qualify | [apps/lightcraft-web/Cargo.toml](../apps/lightcraft/apps/lightcraft-web/Cargo.toml)<br>[Cargo.toml](../apps/lightcraft/Cargo.toml)<br>Recipe: craft-web | Not build-qualified in this source-only pass. |
| P3 / S | materialcraft — Material authoring | [apps/materialcraft/](../apps/materialcraft/) | Browser WASM; node/evaluation/rendering source; file/host integration to qualify | [apps/materialcraft-web/Cargo.toml](../apps/materialcraft/apps/materialcraft-web/Cargo.toml)<br>[Cargo.toml](../apps/materialcraft/Cargo.toml)<br>Recipe: craft-web | Not build-qualified in this source-only pass. |
| P3 / S | photocraft — Image/photo editing | [apps/photocraft/](../apps/photocraft/) | Browser WASM; shared Craft image/fonts; file/host integration to qualify | [apps/photocraft-web/Cargo.toml](../apps/photocraft/apps/photocraft-web/Cargo.toml)<br>[Cargo.toml](../apps/photocraft/Cargo.toml)<br>Recipe: craft-web | Not build-qualified in this source-only pass. |
| P3 / S | soundcraft — Audio authoring | [apps/soundcraft/](../apps/soundcraft/) | Browser WASM; shared Craft audio/media code; file/host integration to qualify | [apps/soundcraft-web/Cargo.toml](../apps/soundcraft/apps/soundcraft-web/Cargo.toml)<br>[Cargo.toml](../apps/soundcraft/Cargo.toml)<br>Recipe: craft-web | Not build-qualified in this source-only pass. |
| P3 / S | stitch-converter — SVG/machine embroidery format conversion | [apps/stitch-converter/](../apps/stitch-converter/) | Account SVG and stitch files; local conversion; separate SVG-editor workflow | [index.mjs](../apps/stitch-converter/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | svg-editor — SVG editing | [apps/svg-editor/](../apps/svg-editor/) | Account SVG files; per-window SVG-edit frame and file bridge | [index.mjs](../apps/svg-editor/index.mjs)<br>[prepare.py](../apps/svg-editor/prepare.py)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | texturecraft — Texture authoring | [apps/texturecraft/](../apps/texturecraft/) | Browser WASM; painting/baking/rendering source; file/host integration to qualify | [apps/texturecraft-web/Cargo.toml](../apps/texturecraft/apps/texturecraft-web/Cargo.toml)<br>[Cargo.toml](../apps/texturecraft/Cargo.toml)<br>Recipe: craft-web | Not build-qualified in this source-only pass. |
| P3 / S | vectorcraft — Vector illustration | [apps/vectorcraft/](../apps/vectorcraft/) | Browser WASM; shared Craft format/fonts; file/host integration to qualify | [apps/vectorcraft-web/Cargo.toml](../apps/vectorcraft/apps/vectorcraft-web/Cargo.toml)<br>[Cargo.toml](../apps/vectorcraft/Cargo.toml)<br>Recipe: craft-web | Not build-qualified in this source-only pass. |

## Engineering and developer apps

| Priority / state | Component and purpose | Source location | Existing interfaces | Source/build entry | Remaining qualification or gap |
|---|---|---|---|---|---|
| P3 / I | acad — Maintained parametric CAD application and owned document operations | [apps/acad/](../apps/acad/) | Browser UI; worker geometry kernels; account files; shared human/agent CAD operations | [package.json](../apps/acad/package.json)<br>[README.md](../apps/acad/README.md)<br>Recipe: cad | Native generated worker/kernel inputs and host packaging require explicit reconstruction; historical CAD-host manifest has 130 absent build assets. See build/ scripts and CAD input notes. |
| P3 / S | arduino-simulator — ATmega328P firmware simulation | [apps/arduino-simulator/](../apps/arduino-simulator/) | Account HEX files; AVR8js worker; pin/serial display | [index.mjs](../apps/arduino-simulator/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | cadcraft — Craft CAD application | [apps/cadcraft/](../apps/cadcraft/) | Browser WASM; shared Craft source; host/file integration to qualify | [apps/cadcraft-web/Cargo.toml](../apps/cadcraft/apps/cadcraft-web/Cargo.toml)<br>[Cargo.toml](../apps/cadcraft/Cargo.toml)<br>Recipe: craft-web | Not build-qualified in this source-only pass. |
| P3 / I | circuit-lab — Text SPICE/netlist simulation candidate | [apps/circuit-lab/](../apps/circuit-lab/) | Account netlists; bounded local worker; retained restricted research runtime | [index.mjs](../apps/circuit-lab/index.mjs)<br>[build-source.sh](../apps/circuit-lab/build-source.sh)<br>Recipe: js | Local research runtime retained; exact rebuild/redistribution/model terms gate remains open. Not a distributable enabled app. |
| P3 / S | circuitjs — Interactive analog circuit simulation | [apps/circuitjs/](../apps/circuitjs/) | Account circuit files; per-window CircuitJS frame | [index.mjs](../apps/circuitjs/index.mjs)<br>[prepare.py](../apps/circuitjs/prepare.py)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | data-explorer — CSV/TSV exploration, SQL and visualization | [apps/data-explorer/](../apps/data-explorer/) | Account data/results files; browser DuckDB-WASM and Perspective workers; no separate DB server | [index.mjs](../apps/data-explorer/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | digital-logic — Digital circuit simulation | [apps/digital-logic/](../apps/digital-logic/) | Account logic JSON files; browser DigitalJS graph/editor | [index.mjs](../apps/digital-logic/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | electronics-design — Breadboard/schematic/PCB editor adapter | [apps/electronics-design/](../apps/electronics-design/) | Account design files; per-window upstream editor frame | [index.mjs](../apps/electronics-design/index.mjs)<br>[prepare.py](../apps/electronics-design/prepare.py)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | gcode-preview — G-code visualization | [apps/gcode-preview/](../apps/gcode-preview/) | Account G-code files; browser worker/rendering | [index.mjs](../apps/gcode-preview/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | grid-tools — Kiri:Moto slicer and Mesh:Tool mesh editor; two visible tools | [apps/grid-tools/](../apps/grid-tools/) | Account workspace/mesh files; lazy Grid.Space package; two launch entries in one upstream project | [index.mjs](../apps/grid-tools/index.mjs)<br>[prepare.py](../apps/grid-tools/prepare.py)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | jsketcher — Original JSketcher fork, distinct from ACAD | [apps/jsketcher/](../apps/jsketcher/) | Standalone CAD browser build; OCCT interpreter dependency; integration separate from ACAD | [package.json](../apps/jsketcher/package.json)<br>[README.md](../apps/jsketcher/README.md)<br>Recipe: cad | Not build-qualified in this source-only pass. |
| P3 / I | microduck — Robotics simulation and policy viewer | [apps/microduck/](../apps/microduck/) | Account project files; MuJoCo/ONNX inputs; browser worker/rendering | [index.mjs](../apps/microduck/index.mjs)<br>Recipe: microduck | Rig/mesh/policy input hashes verified; exact MuJoCo no-eval WASM cold rebuild remains unresolved. A retained runtime is not complete source reproducibility. |
| P3 / I | notebook — JupyterLite/Pyodide Python notebooks | [apps/notebook/](../apps/notebook/) | Account notebook/text files; browser Python kernel/worker; optional guest terminal is separate | [index.mjs](../apps/notebook/index.mjs)<br>[prepare.py](../apps/notebook/prepare.py)<br>Recipe: notebook | All manifest paths are covered by source, the locked reference and verified prepared inputs. Verify the full prepared runtime. |
| P3 / X | pcb-design — Node PCB construction/rendering experiment | [apps/pcb-design/](../apps/pcb-design/) | Node prototype only; browser app and complete dependency notices absent | [package.json](../apps/pcb-design/package.json)<br>[README.md](../apps/pcb-design/README.md)<br>Recipe: prototype | Node research prototype only. Browser packaging and an exact transitive dependency license remain unresolved. |
| P3 / S | pico-simulator — RP2040 firmware simulation | [apps/pico-simulator/](../apps/pico-simulator/) | Account firmware files; browser worker; simulated hardware/serial | [index.mjs](../apps/pico-simulator/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | replicad — Programmatic CAD editor | [apps/replicad/](../apps/replicad/) | Account source/model files; app-owned worker and independent kernel | [index.mjs](../apps/replicad/index.mjs)<br>[model.mjs](../apps/replicad/model.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | solidcraft — Tangency Labs community solid modeling app | [apps/solidcraft/](../apps/solidcraft/) | Browser WASM; independent upstream fork; host/file integration to qualify | [apps/solidcraft-web/Cargo.toml](../apps/solidcraft/apps/solidcraft-web/Cargo.toml)<br>[Cargo.toml](../apps/solidcraft/Cargo.toml)<br>Recipe: craft-web | Not build-qualified in this source-only pass. |

## Optional execution environments

| Priority / state | Component and purpose | Source location | Existing interfaces | Source/build entry | Remaining qualification or gap |
|---|---|---|---|---|---|
| P3 / I | browser — Experimental independent Gecko/WASM browser | [apps/browser/](../apps/browser/) | Worker engine; guest downloads to account files; separately owned authenticated network relay and policy | [index.mjs](../apps/browser/index.mjs)<br>Recipe: gecko | Gecko engine source is a separately pinned fetch via upstream.lock.json/tools; heavyweight engine build is not present/verified as a cold build here. |
| P3 / B | linux — Optional Linux guest source and base image | [apps/linux/](../apps/linux/) | v86 worker; temporary guest filesystem; optional guest networking server; distinct from account storage | [assets/desktop/guest-worker-client.mjs](../apps/linux/assets/desktop/guest-worker-client.mjs)<br>Recipe: guest | Guest/image/server sources retained. Privileged original build operators require an isolated toolchain and deliberate port; not a ready desktop app. |
| P3 / B | terminal — Terminal renderer for optional guest PTYs | [apps/terminal/](../apps/terminal/) | Browser xterm.js; host-provided guest PTY; explicit file copies; no server shell | [index.mjs](../apps/terminal/index.mjs)<br>Recipe: js | Existing renderer/guest PTY source retained; optional guest/host wiring remains separate work. |

## Shared browser tools and engines

| Priority / state | Component and purpose | Source location | Existing interfaces | Source/build entry | Remaining qualification or gap |
|---|---|---|---|---|---|
| P1 / S | codemirror — Code editor capability used by Text | [libraries/codemirror/](../libraries/codemirror/) | Lazy host tool; browser editor instances; no standalone window | [index.mjs](../libraries/codemirror/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P1 / S | zip — Archive capability used by Files | [libraries/zip/](../libraries/zip/) | Host tool; bounded browser ZIP create/extract; no standalone window | [index.mjs](../libraries/zip/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P2 / S | echarts — Chart rendering library | [libraries/echarts/](../libraries/echarts/) | Lazy library; consuming app owns data and view | [index.mjs](../libraries/echarts/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P2 / S | ffmpeg — Media conversion/transcoding capability | [engines/ffmpeg/](../engines/ffmpeg/) | On-demand host tool; caller-owned browser WASM worker; no standalone app or server service | [index.mjs](../engines/ffmpeg/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P2 / S | mermaid — Text-to-diagram renderer | [libraries/mermaid/](../libraries/mermaid/) | Lazy library; browser caller-owned rendering; no standalone window | [index.mjs](../libraries/mermaid/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P2 / S | pdfme — PDF generation library | [libraries/pdfme/](../libraries/pdfme/) | Lazy library; consuming app supplies document data and output | [index.mjs](../libraries/pdfme/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P2 / S | plotly — Interactive plotting library | [libraries/plotly/](../libraries/plotly/) | Lazy library; consuming app owns data and view | [index.mjs](../libraries/plotly/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P2 / S | tone — Audio synthesis and scheduling | [libraries/tone/](../libraries/tone/) | Lazy host tool; browser user-gesture audio context; consuming app owns nodes | [index.mjs](../libraries/tone/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P2 / S | wavesurfer — Audio waveform component | [libraries/wavesurfer/](../libraries/wavesurfer/) | Lazy host tool; consuming app owns view/lifecycle; no standalone window | [index.mjs](../libraries/wavesurfer/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | gltf-transform — glTF/GLB processing capability | [libraries/gltf-transform/](../libraries/gltf-transform/) | Lazy host tool; caller-owned documents; external resources must use authorized files | [index.mjs](../libraries/gltf-transform/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | maplibre — Map display library | [libraries/maplibre/](../libraries/maplibre/) | Optional lazy library; consumer supplies map/data policy; no standalone app | [index.mjs](../libraries/maplibre/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | onnx-runtime — Generic ONNX CPU/WASM inference capability | [engines/onnx-runtime/](../engines/onnx-runtime/) | Optional lazy engine; model supplied by consumer; no shared-copy consumer integrated | [index.mjs](../engines/onnx-runtime/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | opencascade-js — Shared OpenCascade.js CAD capability | [engines/opencascade-js/](../engines/opencascade-js/) | Lazy host tool; browser WASM/worker module; Replicad and JSketcher use separate kernels | [index.mjs](../engines/opencascade-js/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | speech — Local speech recognition engine | [engines/speech/](../engines/speech/) | Microphone/browser worker; pinned local models; user permission; current desktop integration not enabled | [client.mjs](../engines/speech/client.mjs)<br>Recipe: speech | Not build-qualified in this source-only pass. |
| P3 / S | tanstack-virtual — Large-list/grid virtualization capability | [libraries/tanstack-virtual/](../libraries/tanstack-virtual/) | Optional lazy library; no shared-copy consumer integrated; no standalone app | [index.mjs](../libraries/tanstack-virtual/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | transformers — Local-model Transformer inference wrapper | [libraries/transformers/](../libraries/transformers/) | Optional lazy library; consumer must provide local models; remote model fallback disabled | [index.mjs](../libraries/transformers/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | trystero — Optional WebRTC peer library | [libraries/trystero/](../libraries/trystero/) | Explicit consumer signaling/connection policy required; no app uses shared copy by default | [index.mjs](../libraries/trystero/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | webtorrent — Optional peer file-transfer library | [libraries/webtorrent/](../libraries/webtorrent/) | Explicit trackers/authorization/transport required; no default peer transfer | [index.mjs](../libraries/webtorrent/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P3 / S | yjs — Shared state/CRDT primitives | [libraries/yjs/](../libraries/yjs/) | No transport, persistence or authorization provided by this copy; no current shared-copy consumer | [index.mjs](../libraries/yjs/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |

## Shared native and guest engines

| Priority / state | Component and purpose | Source location | Existing interfaces | Source/build entry | Remaining qualification or gap |
|---|---|---|---|---|---|
| P3 / S | manifold — Solid geometry engine source | [engines/manifold/](../engines/manifold/) | C++/Python/JS-WASM build; CAD dependency; no user window | [CMakeLists.txt](../engines/manifold/CMakeLists.txt)<br>[pyproject.toml](../engines/manifold/pyproject.toml)<br>Recipe: native | Not build-qualified in this source-only pass. |
| P3 / S | occt-interpreter — JSketcher-specific OpenCASCADE build environment | [engines/occt-interpreter/](../engines/occt-interpreter/) | Container/OCCT source input and JS wrapper; separate from generic OpenCascade.js | [Dockerfile](../engines/occt-interpreter/Dockerfile)<br>[README.md](../engines/occt-interpreter/README.md)<br>Recipe: native | Not build-qualified in this source-only pass. |
| P3 / S | smlib-wasm — SMLib browser kernel build source | [engines/smlib-wasm/](../engines/smlib-wasm/) | Emscripten build of USD-BRep/SMLib; CAD worker boundary | [src/api.mjs](../engines/smlib-wasm/src/api.mjs)<br>Recipe: native | Not build-qualified in this source-only pass. |
| P3 / S | usd-brep — Native USD BRep solid geometry source | [engines/usd-brep/](../engines/usd-brep/) | Native build/toolchain; optional CAD engine dependency | [BUILDING.md](../engines/usd-brep/BUILDING.md)<br>[build.sh](../engines/usd-brep/build.sh)<br>Recipe: native | Not build-qualified in this source-only pass. |
| P3 / S | v86 — x86 emulator source | [engines/v86/](../engines/v86/) | Browser WASM/JIT plus firmware; optional Linux dependency only | [Makefile](../engines/v86/Makefile)<br>[src/browser/starter.js](../engines/v86/src/browser/starter.js)<br>Recipe: native | Not build-qualified in this source-only pass. |

## Craft shared source, assets and build tools

| Priority / state | Component and purpose | Source location | Existing interfaces | Source/build entry | Remaining qualification or gap |
|---|---|---|---|---|---|
| P2 / S | craft-common-actions — Reusable Craft CI/build workflows | [tooling/craft-common-actions/](../tooling/craft-common-actions/) | Build-time tooling; preserved workflow source does not authorize running publication jobs | [README.md](../tooling/craft-common-actions/README.md)<br>Recipe: cargo | Not build-qualified in this source-only pass. |
| P2 / S | craft-fonts — Shared font payloads, licenses and generation helpers | [assets/craft-fonts/](../assets/craft-fonts/) | Multiple Craft builds; explicit CRAFT_FONTS_DIR points here | [Cargo.toml](../assets/craft-fonts/Cargo.toml)<br>[README.md](../assets/craft-fonts/README.md)<br>Recipe: cargo | Not build-qualified in this source-only pass. |
| P2 / S | craft-i18n — Shared Craft translations | [assets/craft-i18n/](../assets/craft-i18n/) | Multiple Craft builds; localization assets/source | [Cargo.toml](../assets/craft-i18n/Cargo.toml)<br>[README.md](../assets/craft-i18n/README.md)<br>Recipe: cargo | Not build-qualified in this source-only pass. |
| P2 / S | craft-libs — Shared Craft crates, formats, UI and host integration | [libraries/craft-libs/](../libraries/craft-libs/) | Used by multiple Craft apps; platform/atomic/doc/media/fonts/web-host and other crates; not just WordCraft | [Cargo.toml](../libraries/craft-libs/Cargo.toml)<br>[README.md](../libraries/craft-libs/README.md)<br>Recipe: cargo | Not build-qualified in this source-only pass. |
| P2 / S | egui — Maintained shared Rust GUI fork | [libraries/egui/](../libraries/egui/) | Craft app rendering/UI dependency; browser/native targets | [Cargo.toml](../libraries/egui/Cargo.toml)<br>[README.md](../libraries/egui/README.md)<br>Recipe: cargo | Not build-qualified in this source-only pass. |

## Optional platform services and policy

| Priority / state | Component and purpose | Source location | Existing interfaces | Source/build entry | Remaining qualification or gap |
|---|---|---|---|---|---|
| P3 / B | publication — Signed content publication/history source | [platform/publication/](../platform/publication/) | Chat/Chess history and registry source; separate from signaling; interface port pending | [src/webos_publication/__init__.py](../platform/publication/src/webos_publication/__init__.py)<br>[README.md](../platform/publication/README.md)<br>Recipe: python | Source retained; public-interface port and real authority/signature/persistence integration remain pending. |
| P3 / S | rendezvous — Peer discovery and signaling source | [platform/rendezvous/](../platform/rendezvous/) | Lease registry; signed protocol; optional WebSocket/TURN support; not required for files/desktop | [src/steward/__init__.py](../platform/rendezvous/src/steward/__init__.py)<br>[pyproject.toml](../platform/rendezvous/pyproject.toml)<br>Recipe: python | Not build-qualified in this source-only pass. |

## App templates

| Priority / state | Component and purpose | Source location | Existing interfaces | Source/build entry | Remaining qualification or gap |
|---|---|---|---|---|---|
| P3 / T | personal-template — Starter application example | [apps/personal-template/](../apps/personal-template/) | Human-facing template with file hooks; starting material, not a completed end-user product | [index.mjs](../apps/personal-template/index.mjs)<br>Recipe: js | Template source only; not counted as a delivered end-user application. |

## Games and interactive activities

| Priority / state | Component and purpose | Source location | Existing interfaces | Source/build entry | Remaining qualification or gap |
|---|---|---|---|---|---|
| P4 / S | chess-study — Chess Study | [apps/chess-study/](../apps/chess-study/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/chess-study/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | clockwork-quest — Clockwork Quest | [apps/clockwork-quest/](../apps/clockwork-quest/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/clockwork-quest/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | clockwork-room — Clockwork Room | [apps/clockwork-room/](../apps/clockwork-room/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/clockwork-room/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | crystal-defense — Crystal Defense | [apps/crystal-defense/](../apps/crystal-defense/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/crystal-defense/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | drone-circuit — Drone Circuit | [apps/drone-circuit/](../apps/drone-circuit/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/drone-circuit/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | expression-puppet — Expression Puppet | [apps/expression-puppet/](../apps/expression-puppet/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/expression-puppet/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | falling-blocks — Falling Blocks | [apps/falling-blocks/](../apps/falling-blocks/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/falling-blocks/index.mjs)<br>[model.mjs](../apps/falling-blocks/model.mjs)<br>[prepare.py](../apps/falling-blocks/prepare.py)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | garden-defense — Garden Defense | [apps/garden-defense/](../apps/garden-defense/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/garden-defense/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | gravity-pinball — Gravity Pinball | [apps/gravity-pinball/](../apps/gravity-pinball/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/gravity-pinball/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | kinetic-relay — Kinetic Relay | [apps/kinetic-relay/](../apps/kinetic-relay/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/kinetic-relay/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | lantern-leap — Lantern Leap | [apps/lantern-leap/](../apps/lantern-leap/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/lantern-leap/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | marble-works — Marble Works | [apps/marble-works/](../apps/marble-works/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/marble-works/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | memory-garden — Memory Garden | [apps/memory-garden/](../apps/memory-garden/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/memory-garden/index.mjs)<br>[model.mjs](../apps/memory-garden/model.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | orbital-courier — Orbital Courier | [apps/orbital-courier/](../apps/orbital-courier/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/orbital-courier/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | owl-companion — Owl Companion | [apps/owl-companion/](../apps/owl-companion/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/owl-companion/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | physics-playground — Physics Playground | [apps/physics-playground/](../apps/physics-playground/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/physics-playground/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | pocket-golf — Pocket Golf | [apps/pocket-golf/](../apps/pocket-golf/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/pocket-golf/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | pocket-rally — Pocket Rally | [apps/pocket-rally/](../apps/pocket-rally/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/pocket-rally/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | reactive-control-desk — Reactive Control Desk | [apps/reactive-control-desk/](../apps/reactive-control-desk/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/reactive-control-desk/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | rhythm-garden — Rhythm Garden | [apps/rhythm-garden/](../apps/rhythm-garden/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/rhythm-garden/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | sky-courier — Sky Courier | [apps/sky-courier/](../apps/sky-courier/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/sky-courier/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | sling-targets — Sling Targets | [apps/sling-targets/](../apps/sling-targets/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/sling-targets/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | snake-garden — Snake Garden | [apps/snake-garden/](../apps/snake-garden/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/snake-garden/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | solitaire — Solitaire Table | [apps/solitaire/](../apps/solitaire/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/solitaire/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | stack-balance — Stack and Balance | [apps/stack-balance/](../apps/stack-balance/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/stack-balance/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | story-cards — Story Cards | [apps/story-cards/](../apps/story-cards/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/story-cards/index.mjs)<br>[model.mjs](../apps/story-cards/model.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | tabletop-bot-arena — Tabletop Bot Arena | [apps/tabletop-bot-arena/](../apps/tabletop-bot-arena/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/tabletop-bot-arena/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |
| P4 / S | target-garden — Target Garden | [apps/target-garden/](../apps/target-garden/) | Human browser activity; Runtime lifecycle; existing account-file save/progress hooks | [index.mjs](../apps/target-garden/index.mjs)<br>Recipe: js | Not build-qualified in this source-only pass. |

## Games shared code

| Priority / state | Component and purpose | Source location | Existing interfaces | Source/build entry | Remaining qualification or gap |
|---|---|---|---|---|---|
| P4 / S | learning-game-core — Reusable deterministic learning-game mechanics | [libraries/learning-game-core/](../libraries/learning-game-core/) | Source dependency of planned game cores; no user window | [core.mjs](../libraries/learning-game-core/core.mjs)<br>[experience.mjs](../libraries/learning-game-core/experience.mjs)<br>Recipe: model | Not build-qualified in this source-only pass. |

## Planned game cores

| Priority / state | Component and purpose | Source location | Existing interfaces | Source/build entry | Remaining qualification or gap |
|---|---|---|---|---|---|
| P4 / P | fraction-farm — Deterministic game model, not a completed app | [apps/fraction-farm/](../apps/fraction-farm/) | Shared learning-game-core dependency; no desktop view | [model.mjs](../apps/fraction-farm/model.mjs)<br>Recipe: model | App view, assets and desktop integration are not implemented here. |
| P4 / P | market-math — Deterministic game model, not a completed app | [apps/market-math/](../apps/market-math/) | Shared learning-game-core dependency; no desktop view | [model.mjs](../apps/market-math/model.mjs)<br>Recipe: model | App view, assets and desktop integration are not implemented here. |
| P4 / P | math-path — Deterministic game model, not a completed app | [apps/math-path/](../apps/math-path/) | Shared learning-game-core dependency; no desktop view | [model.mjs](../apps/math-path/model.mjs)<br>Recipe: model | App view, assets and desktop integration are not implemented here. |
| P4 / P | pocket-conquest — Deterministic game model, not a completed app | [apps/pocket-conquest/](../apps/pocket-conquest/) | Shared learning-game-core dependency; no desktop view | [model.mjs](../apps/pocket-conquest/model.mjs)<br>Recipe: model | App view, assets and desktop integration are not implemented here. |
| P4 / P | rule-detective — Deterministic game model, not a completed app | [apps/rule-detective/](../apps/rule-detective/) | Shared learning-game-core dependency; no desktop view | [model.mjs](../apps/rule-detective/model.mjs)<br>Recipe: model | App view, assets and desktop integration are not implemented here. |
| P4 / P | tile-islands — Deterministic game model, not a completed app | [apps/tile-islands/](../apps/tile-islands/) | Shared learning-game-core dependency; no desktop view | [model.mjs](../apps/tile-islands/model.mjs)<br>Recipe: model | App view, assets and desktop integration are not implemented here. |
| P4 / P | word-weaver — Deterministic game model, not a completed app | [apps/word-weaver/](../apps/word-weaver/) | Shared learning-game-core dependency; no desktop view | [model.mjs](../apps/word-weaver/model.mjs)<br>Recipe: model | App view, assets and desktop integration are not implemented here. |

## Unused legacy source

| Priority / state | Component and purpose | Source location | Existing interfaces | Source/build entry | Remaining qualification or gap |
|---|---|---|---|---|---|
| P5 / H | rooms — Unused former Hosted Rooms implementation | [legacy/rooms/](../legacy/rooms/) | User-confirmed old code; no current service, listener or app dependency | [README.md](../legacy/rooms/README.md)<br>Recipe: historical | Historical source only; no activation is intended. |

## Build and interaction notes

- **Files versus Storage:** Files is a human-facing application and file launcher. Storage owns account persistence/revision semantics; Accounts owns authentication and grants. An app file hook is not proof of a confirmed server save or cross-machine acceptance.
- **Runtime versus Desktop:** Runtime owns shared lifecycle/launcher/operation modules. Desktop owns the original workspace viewer. Its old relative bootstrap paths need assembly composition across the new owners; no substitute viewer is provided.
- **Human-only views:** Help is primarily presentation. Most games also contain account-file progress hooks, so calling them purely visual would be inaccurate. Shared engines/tools provide APIs rather than windows. App-specific human/agent parity is not qualified by this inventory.
- **Craft core:** `libraries/craft-libs/` owns many shared crates (documents, media, UI, platform, web-host, fonts and formats); `libraries/egui/`, `assets/craft-fonts/`, `assets/craft-i18n/` and `tooling/craft-common-actions/` have separate roles. Different apps pin different upstream crate revisions; the shared checkout does not silently replace those pins.
- **Craft branches:** all 17 apps and 5 shared Craft projects have an upstream-tracking main branch, with selected working source on a WebOS branch. Upstream heads were fetched on 2026-11-16. No newer upstream source was merged into selected WebOS pins. SolidCraft is the Tangency Labs community project; the other 16 selected apps are Storytold projects.
- **Visible entries versus repositories:** `apps/grid-tools/` contains both Kiri:Moto and Mesh:Tool from one owned upstream project. FFmpeg, TanStack Virtual, CodeMirror and other System Tools menu entries are capabilities, not separate end-user apps. Historical Chat/Chess publication service source is not a current chat app. `legacy/rooms/` is unused old code.
- **Optional guest:** Linux, Terminal and v86 are organized separately and are not dependencies of the minimum future file/editing workflow. The preserved original bootstrap still mentions them; changing that behavior is future integration work.

### Recipe keys

Recipes below identify source-owned instructions, not commands run during this pass. Read scripts before executing inherited preparation/build operators. Use new external build output directories. Never run deployment/publishing workflows as a source check.

| Key | Definition |
|---|---|
| js | Browser JS bundle; [platform/runtime/active-system/tools/app-builder/build.mjs](../platform/runtime/active-system/tools/app-builder/build.mjs) |
| python-js | Owned Python package and browser modules; [scripts/bootstrap_backend.py](../scripts/bootstrap_backend.py) |
| python | Owned Python package; see the row’s owned build definitions and README |
| craft-web | Upstream Cargo/browser packaging; parent supplies shared fonts; [scripts/craft_cargo.py](../scripts/craft_cargo.py) |
| cargo | Shared Cargo workspace or workflow source; see the row’s owned build definitions and README |
| native | Owned native/engine build definitions; see the row’s owned build definitions and README |
| model | JavaScript model/library source; component package test command; see the row’s owned build definitions and README |
| historical | Retained source; no activation recipe authorized; see the row’s owned build definitions and README |
| cad | Owned CAD worker/webpack build definitions; see the row’s owned build definitions and README |
| guest | Original guest image builders; isolated toolchain/port required; see the row’s owned build definitions and README |
| gecko | Pinned engine fetch/build plus adapter bundle; [apps/browser/tools/build_engine.sh](../apps/browser/tools/build_engine.sh) |
| notebook | JupyterLite/Pyodide preparation plus adapter bundle; [apps/notebook/prepare.py](../apps/notebook/prepare.py) |
| microduck | Pinned rig/policy/engine preparation plus adapter bundle; [apps/microduck/tools/build-runner.mjs](../apps/microduck/tools/build-runner.mjs) |
| prototype | Node research probe; no browser production recipe; [apps/pcb-design/probe.mjs](../apps/pcb-design/probe.mjs) |
| speech | Locked-input fetch and offline component build; [engines/speech/scripts/build.mjs](../engines/speech/scripts/build.mjs) |

The retained JS builder accepts an explicit JSON configuration with `source` set to the assembly root, selected `apps`, explicit `entries` relative to that root, and an external `output`. Its inherited defaults and `deploy/legacy-operations/build-public-apps.py` assume the former grouped layout and must not be used unchanged. Per-component pinned packages, prepare scripts, declared assets, workers, notices and hash-checked patches remain required. This is a located recipe, not a tested all-app production command.

The initial source pass checked metadata for 17 Craft workspaces, which was not browser build proof. WordCraft now has a separately qualified current-viewer release; see its Q row and report. The selected WordCraft and DeckCraft branches have historical build/operation evidence, but the rejected desktop’s acceptance does not qualify the original viewer. Read [Craft build inputs](CRAFT-BUILD-INPUTS.md).

[Declared asset coverage](ASSET-COVERAGE.md) accounts for all Notebook paths and identifies 130 missing generated paths in the historical ACAD-host build. Notebook and CAD still need runtime and rebuild qualification. See the [Craft build input audit](CRAFT-BUILD-INPUTS.md) for pinned dependencies and assets for the 17 Craft apps.

The parent also retains historical cross-system tests, deployment definitions and operator sources under `tests/legacy-*`, `deploy/legacy-*` and `migration/legacy-*`; they are not additional application repositories or an instruction to execute them. Private original recovery and unresolved historical records remain outside the source tree. This chart covers the 124 attached source owners, not every old recovery file.

Refresh from reviewed roles and current source paths with `PYTHONDONTWRITEBYTECODE=1 python3 scripts/report_components.py --write`. Exact selected revisions remain in the parent Git links. [Machine-readable roles](COMPONENT-ROLES.json), [full source catalog](SOURCE-CATALOG.json) and [CSV matrix](APP-MATRIX.csv) accompany this chart.
