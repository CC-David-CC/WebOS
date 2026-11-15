# Complete assembled component chart

All paths are relative to /home/dflanag3/Projects/WebOS/. There are109 independent source repositories currently attached:76 apps (31 system/CAD,17 Craft,28 games),8 engines,5 platform components,17 libraries,2 shared asset projects and1 shared build-tool project. Source placement is not functional readiness. See STATUS-MATRIX.md for verification limits and failures.

## Platform (5)

| Component | Actual directory |
|---|---|
| accounts | `platform/accounts/` |
| desktop | `platform/desktop/` |
| login | `platform/login/` |
| runtime | `platform/runtime/` |
| storage | `platform/storage/` |

## System and CAD apps (31)

| Component | Actual directory |
|---|---|
| acad | `apps/acad/` |
| arduino-simulator | `apps/arduino-simulator/` |
| audio-editor | `apps/audio-editor/` |
| browser | `apps/browser/` |
| calculator | `apps/calculator/` |
| circuitjs | `apps/circuitjs/` |
| data-explorer | `apps/data-explorer/` |
| diagrams-net | `apps/diagrams-net/` |
| digital-logic | `apps/digital-logic/` |
| document-editor | `apps/document-editor/` |
| electronics-design | `apps/electronics-design/` |
| embroidery-studio | `apps/embroidery-studio/` |
| excalidraw | `apps/excalidraw/` |
| files | `apps/files/` |
| gcode-preview | `apps/gcode-preview/` |
| grid-tools | `apps/grid-tools/` |
| help | `apps/help/` |
| image-editor | `apps/image-editor/` |
| legacy-jsketcher | `apps/jsketcher/` |
| linux | `apps/linux/` |
| microduck | `apps/microduck/` |
| notebook | `apps/notebook/` |
| pdf-viewer | `apps/pdf-viewer/` |
| personal-template | `apps/personal-template/` |
| pico-simulator | `apps/pico-simulator/` |
| replicad | `apps/replicad/` |
| spreadsheet | `apps/spreadsheet/` |
| stitch-converter | `apps/stitch-converter/` |
| svg-editor | `apps/svg-editor/` |
| terminal | `apps/terminal/` |
| text | `apps/text/` |

## Craft apps (17)

| Component | Actual directory |
|---|---|
| anicraft | `apps/anicraft/` |
| cadcraft | `apps/cadcraft/` |
| deckcraft | `apps/deckcraft/` |
| designcraft | `apps/designcraft/` |
| effectcraft | `apps/effectcraft/` |
| figcraft | `apps/figcraft/` |
| filmcraft | `apps/filmcraft/` |
| gridcraft | `apps/gridcraft/` |
| lightcraft | `apps/lightcraft/` |
| materialcraft | `apps/materialcraft/` |
| pdfcraft | `apps/pdfcraft/` |
| photocraft | `apps/photocraft/` |
| solidcraft | `apps/solidcraft/` |
| soundcraft | `apps/soundcraft/` |
| texturecraft | `apps/texturecraft/` |
| vectorcraft | `apps/vectorcraft/` |
| wordcraft | `apps/wordcraft/` |

## Games (28)

| Component | Actual directory |
|---|---|
| chess-study | `apps/chess-study/` |
| clockwork-quest | `apps/clockwork-quest/` |
| clockwork-room | `apps/clockwork-room/` |
| crystal-defense | `apps/crystal-defense/` |
| drone-circuit | `apps/drone-circuit/` |
| expression-puppet | `apps/expression-puppet/` |
| falling-blocks | `apps/falling-blocks/` |
| garden-defense | `apps/garden-defense/` |
| gravity-pinball | `apps/gravity-pinball/` |
| kinetic-relay | `apps/kinetic-relay/` |
| lantern-leap | `apps/lantern-leap/` |
| marble-works | `apps/marble-works/` |
| memory-garden | `apps/memory-garden/` |
| orbital-courier | `apps/orbital-courier/` |
| owl-companion | `apps/owl-companion/` |
| physics-playground | `apps/physics-playground/` |
| pocket-golf | `apps/pocket-golf/` |
| pocket-rally | `apps/pocket-rally/` |
| reactive-control-desk | `apps/reactive-control-desk/` |
| rhythm-garden | `apps/rhythm-garden/` |
| sky-courier | `apps/sky-courier/` |
| sling-targets | `apps/sling-targets/` |
| snake-garden | `apps/snake-garden/` |
| solitaire | `apps/solitaire/` |
| stack-balance | `apps/stack-balance/` |
| story-cards | `apps/story-cards/` |
| tabletop-bot-arena | `apps/tabletop-bot-arena/` |
| target-garden | `apps/target-garden/` |

## Engines (8)

| Component | Actual directory |
|---|---|
| engine-ffmpeg | `engines/ffmpeg/` |
| engine-manifold | `engines/manifold/` |
| engine-onnx-runtime | `engines/onnx-runtime/` |
| engine-opencascade | `engines/occt-interpreter/` |
| engine-opencascade-js | `engines/opencascade-js/` |
| engine-smlib-wasm | `engines/smlib-wasm/` |
| engine-usd-brep | `engines/usd-brep/` |
| engine-v86 | `engines/v86/` |

## Shared libraries and tools (17)

| Component | Actual directory |
|---|---|
| codemirror | `libraries/codemirror/` |
| craft-libs | `libraries/craft-libs/` |
| echarts | `libraries/echarts/` |
| egui | `libraries/egui/` |
| gltf-transform | `libraries/gltf-transform/` |
| maplibre | `libraries/maplibre/` |
| mermaid | `libraries/mermaid/` |
| pdfme | `libraries/pdfme/` |
| plotly | `libraries/plotly/` |
| tanstack-virtual | `libraries/tanstack-virtual/` |
| tone | `libraries/tone/` |
| transformers | `libraries/transformers/` |
| trystero | `libraries/trystero/` |
| wavesurfer | `libraries/wavesurfer/` |
| webtorrent | `libraries/webtorrent/` |
| yjs | `libraries/yjs/` |
| zip | `libraries/zip/` |

## Shared asset projects (2)

| Component | Actual directory |
|---|---|
| craft-fonts | `assets/craft-fonts/` |
| craft-i18n | `assets/craft-i18n/` |

## Shared build tooling (1)

| Component | Actual directory |
|---|---|
| craft-common-actions | `tooling/craft-common-actions/` |

## Organized artifact data

| Data | Actual directory |
|---|---|
| Frozen beta public app payloads:74 entries,6143 verified files,1,028,162,239 bytes | `artifacts/reference-beta/<catalog-key>/` |
| Recovered pinned Microduck source inputs and qualified engine files | `artifacts/inputs/microduck/` |
| Reference file lock | `artifacts/reference-beta.lock.json` |
| Immutable build-input file lock | `artifacts/input-files.json` |

Payloads are ignored by Git; locks/docs/verification commands are parent-owned. Private recovery, raw audits and local bare origins stay outside this tree.

## Still pending source organization

- Nonregistered Circuit Lab and PCB Design source, plus other historical WIP and source-area reconciliation.
- Remaining platform/backend, guest network, build/operations and legacy test/source areas. These are preserved in private recovery; their component ownership is not yet fully resolved.
- Linux/v86 source and runtime/base image are now placed. Its optional Desktop view and existing old global boot orchestration still need a deliberate port; it is not a minimum dependency.
- Additional packages such as Phaser, Three.js, Babylon.js, Rapier, Havok, Rive and MuJoCo are currently dependencies pinned by app/game manifests, not additional independent repositories in this chart. Existing owned engine build patches and required assets still need final reconciliation.
- Complete site/core assets, ignored inputs and source-to-owner coverage must still be verified before claiming the whole disk restart point complete.

Craft provenance:16 ArtCraft first-party projects plus community SolidCraft (Tangency Labs). Craft Anything and MailCraft are not selected.
