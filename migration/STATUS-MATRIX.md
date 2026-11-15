# Complete source status matrix

Observed source snapshot: `c4fad31a760d8f59f86accae497168ee5ffbd3c7`. All107 selected repositories passed fresh recursive local-clone/source checks; all six assembly tests passed. This is a point-in-time report, not a release manifest or a claim that107 apps work.

**PASS** means evidence exists for the stated scope. **OPEN** means incomplete or unverified. **FAIL** means an actual check failed; pre-existing failures are retained. The original workspace and deployment remain unchanged.

| Area | Organized source | Required assets/build | New assembled runtime |
|---|---|---|---|
| 17 Craft apps | PASS17/17 | WordCraft baseline PASS; others OPEN | OPEN |
| Shared Craft projects | PASS craft-libs, egui, fonts, translations, common actions | Pinned data/history PASS; wiring OPEN | OPEN |
| 28 old registered games | PASS28/28 | Declared new-game assets PASS; full browser builds OPEN | OPEN |
| Remaining registered editors/tools | PASS source placement | Partial; external asset organization OPEN | OPEN |
| 75 source registry entries / 74 live beta entries | PASS source owners assigned | Complete static/build asset sweep OPEN | OPEN |
| Platform plus Files | PASS independent source | Earlier signed slice passed; post-layout runtime retest OPEN | Full minimum OPEN |
| Linux/v86 optional app | OPEN - requested; source/asset boundaries being derived | OPEN - pull static base assets from example.invalid | OPEN; not a minimum dependency |
| Nonregistered source and platform leftovers | OPEN | OPEN | OPEN |

These categories overlap. The actual107 repositories are75 apps,7 engines,5 platform components,17 libraries,2 shared asset projects and1 shared tooling project. The75 app-repository count is not the75-entry old catalog.

Craft provenance: the selected17 are16 ArtCraft first-party projects plus Tangency Labs community SolidCraft. See [the complete source/provenance list](CRAFT-APPS.md).

## Full per-component matrix

The source column below is PASS for selected source presence, retained/extracted history, correct ownership and independent Git retrieval. It does not mean complete functionality. WordCraft also has separately retained newer review work in the primary checkout; the parent selects its preserved baseline.

### Craft apps

| Component | Actual directory | Source | Component checks | Assets/build | New host |
|---|---|---|---|---|---|
| anicraft | `apps/anicraft/` | PASS | OPEN - selected source baseline only | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| cadcraft | `apps/cadcraft/` | PASS | OPEN - selected source baseline only | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| deckcraft | `apps/deckcraft/` | PASS | OPEN - selected source baseline only | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| designcraft | `apps/designcraft/` | PASS | OPEN - selected source baseline only | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| effectcraft | `apps/effectcraft/` | PASS | OPEN - selected source baseline only | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| figcraft | `apps/figcraft/` | PASS | OPEN - selected source baseline only | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| filmcraft | `apps/filmcraft/` | PASS | OPEN - selected source baseline only | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| gridcraft | `apps/gridcraft/` | PASS | OPEN - selected source baseline only | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| lightcraft | `apps/lightcraft/` | PASS | OPEN - selected source baseline only | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| materialcraft | `apps/materialcraft/` | PASS | OPEN - selected source baseline only | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| pdfcraft | `apps/pdfcraft/` | PASS | OPEN - selected source baseline only | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| photocraft | `apps/photocraft/` | PASS | OPEN - selected source baseline only | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| solidcraft | `apps/solidcraft/` | PASS | OPEN - selected source baseline only | OPEN - complete build/asset graph not verified; distribution license/brand gate OPEN | OPEN - new host integration not qualified |
| soundcraft | `apps/soundcraft/` | PASS | OPEN - selected source baseline only | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| texturecraft | `apps/texturecraft/` | PASS | OPEN - selected source baseline only | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| vectorcraft | `apps/vectorcraft/` | PASS | OPEN - selected source baseline only | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| wordcraft | `apps/wordcraft/` | PASS | PASS - native checks and real baseline editor browser test | PASS baseline - complete editor artifact; hosted review build remains OPEN | OPEN - account-save integration pending |

### Existing games

| Component | Actual directory | Source | Component checks | Assets/build | New host |
|---|---|---|---|---|---|
| chess-study | `apps/chess-study/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| clockwork-quest | `apps/clockwork-quest/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| clockwork-room | `apps/clockwork-room/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| crystal-defense | `apps/crystal-defense/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| drone-circuit | `apps/drone-circuit/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| expression-puppet | `apps/expression-puppet/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| falling-blocks | `apps/falling-blocks/` | PASS | OPEN - no original package suite; coach render/rebuild not run | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| garden-defense | `apps/garden-defense/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| gravity-pinball | `apps/gravity-pinball/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| kinetic-relay | `apps/kinetic-relay/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| lantern-leap | `apps/lantern-leap/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| marble-works | `apps/marble-works/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| memory-garden | `apps/memory-garden/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| orbital-courier | `apps/orbital-courier/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| owl-companion | `apps/owl-companion/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| physics-playground | `apps/physics-playground/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| pocket-golf | `apps/pocket-golf/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| pocket-rally | `apps/pocket-rally/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| reactive-control-desk | `apps/reactive-control-desk/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| rhythm-garden | `apps/rhythm-garden/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| sky-courier | `apps/sky-courier/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| sling-targets | `apps/sling-targets/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| snake-garden | `apps/snake-garden/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| solitaire | `apps/solitaire/` | PASS | PASS - configured independent domain/type checks | OPEN - complete browser asset build not verified | OPEN - new host integration not qualified |
| stack-balance | `apps/stack-balance/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| story-cards | `apps/story-cards/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| tabletop-bot-arena | `apps/tabletop-bot-arena/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |
| target-garden | `apps/target-garden/` | PASS | PASS - configured independent domain/type checks | PASS - tracked source and declared asset paths checked; full browser graph OPEN | OPEN - new host integration not qualified |

### Existing system and CAD apps

| Component | Actual directory | Source | Component checks | Assets/build | New host |
|---|---|---|---|---|---|
| acad | `apps/acad/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| arduino-simulator | `apps/arduino-simulator/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| audio-editor | `apps/audio-editor/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| browser | `apps/browser/` | PASS | FAIL - one unchanged pre-existing stale host-contract assertion | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| calculator | `apps/calculator/` | PASS | PASS - earlier extraction unit checks; current host port OPEN | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| circuitjs | `apps/circuitjs/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| data-explorer | `apps/data-explorer/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| diagrams-net | `apps/diagrams-net/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| digital-logic | `apps/digital-logic/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| document-editor | `apps/document-editor/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| electronics-design | `apps/electronics-design/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| embroidery-studio | `apps/embroidery-studio/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| excalidraw | `apps/excalidraw/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| files | `apps/files/` | PASS | PASS - earlier component/dev checks; post-layout runtime retest OPEN | OPEN - post-layout composition build/retest | Earlier Login/Desktop/Files signed-server slice passed; current full minimum OPEN |
| gcode-preview | `apps/gcode-preview/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| grid-tools | `apps/grid-tools/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| help | `apps/help/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| image-editor | `apps/image-editor/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| legacy-jsketcher | `apps/jsketcher/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| microduck | `apps/microduck/` | PASS | FAIL - 200 pass / 11 missing-fixture failures; baseline and extraction match | PASS - exact project/visual regeneration and qualified engine hashes; full app build OPEN | OPEN - new host integration not qualified |
| notebook | `apps/notebook/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| pdf-viewer | `apps/pdf-viewer/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| personal-template | `apps/personal-template/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| pico-simulator | `apps/pico-simulator/` | PASS | PASS - four configured simulator test commands | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| replicad | `apps/replicad/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| spreadsheet | `apps/spreadsheet/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| stitch-converter | `apps/stitch-converter/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| svg-editor | `apps/svg-editor/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| terminal | `apps/terminal/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| text | `apps/text/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |

### Platform

| Component | Actual directory | Source | Component checks | Assets/build | New host |
|---|---|---|---|---|---|
| accounts | `platform/accounts/` | PASS | PASS - earlier component/dev checks; post-layout runtime retest OPEN | OPEN - post-layout composition build/retest | Earlier Login/Desktop/Files signed-server slice passed; current full minimum OPEN |
| desktop | `platform/desktop/` | PASS | PASS - earlier component/dev checks; post-layout runtime retest OPEN | OPEN - post-layout composition build/retest | Earlier Login/Desktop/Files signed-server slice passed; current full minimum OPEN |
| login | `platform/login/` | PASS | PASS - earlier component/dev checks; post-layout runtime retest OPEN | OPEN - post-layout composition build/retest | Earlier Login/Desktop/Files signed-server slice passed; current full minimum OPEN |
| runtime | `platform/runtime/` | PASS | PASS - earlier component/dev checks; post-layout runtime retest OPEN | OPEN - post-layout composition build/retest | Earlier Login/Desktop/Files signed-server slice passed; current full minimum OPEN |
| storage | `platform/storage/` | PASS | PASS - earlier component/dev checks; post-layout runtime retest OPEN | OPEN - post-layout composition build/retest | Earlier Login/Desktop/Files signed-server slice passed; current full minimum OPEN |

### Engines

| Component | Actual directory | Source | Component checks | Assets/build | New host |
|---|---|---|---|---|---|
| engine-ffmpeg | `engines/ffmpeg/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| engine-manifold | `engines/manifold/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| engine-onnx-runtime | `engines/onnx-runtime/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| engine-opencascade | `engines/occt-interpreter/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| engine-opencascade-js | `engines/opencascade-js/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| engine-smlib-wasm | `engines/smlib-wasm/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| engine-usd-brep | `engines/usd-brep/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |

### Shared libraries

| Component | Actual directory | Source | Component checks | Assets/build | New host |
|---|---|---|---|---|---|
| codemirror | `libraries/codemirror/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| craft-libs | `libraries/craft-libs/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| echarts | `libraries/echarts/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| egui | `libraries/egui/` | PASS | OPEN - no component behavior qualification claimed | PASS - selected LFS images and all 2144 historical payloads recovered/verified; consumer build wiring OPEN | OPEN - new host integration not qualified |
| gltf-transform | `libraries/gltf-transform/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| maplibre | `libraries/maplibre/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| mermaid | `libraries/mermaid/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| pdfme | `libraries/pdfme/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| plotly | `libraries/plotly/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| tanstack-virtual | `libraries/tanstack-virtual/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| tone | `libraries/tone/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| transformers | `libraries/transformers/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| trystero | `libraries/trystero/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| wavesurfer | `libraries/wavesurfer/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| webtorrent | `libraries/webtorrent/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| yjs | `libraries/yjs/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |
| zip | `libraries/zip/` | PASS | OPEN - no component behavior qualification claimed | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |

### Shared assets

| Component | Actual directory | Source | Component checks | Assets/build | New host |
|---|---|---|---|---|---|
| craft-fonts | `assets/craft-fonts/` | PASS | OPEN - no component behavior qualification claimed | PASS - pinned source data present; consumer build wiring OPEN | OPEN - new host integration not qualified |
| craft-i18n | `assets/craft-i18n/` | PASS | OPEN - no component behavior qualification claimed | PASS - pinned source data present; consumer build wiring OPEN | OPEN - new host integration not qualified |

### Build tooling

| Component | Actual directory | Source | Component checks | Assets/build | New host |
|---|---|---|---|---|---|
| craft-common-actions | `tooling/craft-common-actions/` | PASS | OPEN - no release workflow executed; top-level license review pending | OPEN - complete build/asset graph not verified | OPEN - new host integration not qualified |

## Remaining disk restart-point work

- Preserve and place required source/runtime inputs from example.invalid in the new organized layout, with hashes, provenance and build recipes. Public immutable Microduck assets and exact qualified engine inputs are recovered privately; placement/reproduction recipes remain separate work.
- Include Linux/v86 as an optional owned app/engine with static base images. Discover and separate VM code still embedded in the preserved old Desktop; do not make the minimum depend on it.
- Organize nonregistered Circuit Lab/PCB and other WIP, remaining platform tools, shared assets and every unmapped source area.
- Recover or explicitly gate one absent Microduck synthetic PNG fixture; preserve Browser’s existing stale assertion failure. No test assertion has been weakened.
- Complete an original-source-to-new-owner/asset reconciliation and verify the resulting restart point independently. Repository count alone does not close this gate.

Live account databases, credentials and private documents are not source assets. External publication, deployment changes and service restarts remain unperformed.
