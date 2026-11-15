# App locations and served status — 2026-11-08

Read-only inventory of selected box-webhost serving roots, menus and catalogs. Presence is not qualification. Historical per-app tests and known limitations remain in [APP_STATUS.md](APP_STATUS.md), [APP_UNIFICATION_PROGRESS.md](APP_UNIFICATION_PROGRESS.md) and [GAME_PREVIEW_REVIEW.md](GAME_PREVIEW_REVIEW.md). Their older jSketcher not-deployed row is superseded by actual beta R4 here.

## Source locations

| Purpose | Path |
|---|---|
| Fixed plain review snapshot | `/home/dflanag3/CodiServer/desktop-preview/CURRENT-CODE/` — desktop/ and acad/; exact heads in SNAPSHOT.json; never auto-updated |
| Current desktop development on this PC | `/tmp/codi-desktop-mechanical-candidate-20261105/` |
| Current ACAD development on this PC | `/tmp/codi-acad-main-20261107/` |
| Stable R730 desktop source checkpoint | `/mnt/data10tb/workspaces/webos-desktop/` |
| Stable R730 ACAD source checkpoint | `/mnt/data10tb/workspaces/acad/` |
| R730 actual build checkout | `/mnt/data10tb/codi-acad-build-20261107-r2/` — test/build pin, not necessarily latest source |
| Older original checkout | `/home/dflanag3/CodiServer/desktop-preview/SIMPLIFIED/` — simplified@c78b40341, nine tracked local edits preserved |

`served_apps_public/` and other older copies are separate historical/reference or unfinished inputs, not proof of the latest integrated version. Do not automatically synchronize them. Server hash directories are built serving assets; edit app source instead.

Current desktop integration contains the committed simplified history. Uncommitted SIMPLIFIED edits are separate preserved work. CURRENT-CODE stays fixed. R730 source worktrees are detached inspection checkpoints, updated only when clean; dependencies are separate. App folders contain source/adapters and pinned dependency specifications, not necessarily complete upstream libraries. ACAD core is independent.

## Git locations

| Repository | box-git | R730 | Active branch |
|---|---|---|---|
| Desktop + apps | `/srv/data/git/CodiServer-distro.git` | `/mnt/data10tb/git/CodiServer.git` | `integration/desktop-mechanical-candidate-20261105` |
| ACAD engine | `/srv/data/git/ACAD.git` | `/mnt/data10tb/git/ACAD.git` | `integration/point-line-runtime-20261108` |

Original simplified is c78b40341. ACAD qualified main is d102e5217; active integration is ahead. The rolled-back JSKetcher fork is not current ACAD source.

## Actual sites

**ksu.codes: five enabled launchers** — Files, Text Editor, Terminal, Calculator, Help. Voice input / Keyboard lock are shell controls. CodeMirror is a dependency. No game launchers.

**beta.ksu.codes: 56 enabled launchers /75 bundle records.** Libraries, providers and templates account for the difference. Browser and Linux Notebook are disabled; seven learning games are disabled plans. Eighteen grayed-out tools are libraries. Per-account user apps are dynamic and excluded.

Immutable built releases on box-webhost, not editable source:

- Main: `/srv/codi-connected/simplified/f2e2ed4d3b75e8c40992a18bf83db7937fe90615bf1151e1b51ed3b0a8012f4a`
- Beta R4 overlay: `/srv/data/codi-beta-opfs/337b69de24aa84f726a5d3cedb8f16f7ade026baa206b4faa31281ff380d827e`
- Beta underlying assets: `/srv/codi-connected/simplified/0965a0cbdd022f588061cdc23e10eb6b18fa5977cc3f6a05569439eaf11d2020`

Exact entry files/hashes and menu source hashes are in [JSON evidence](evidence/app-inventory-20261108.json). Every catalog entry exists in the selected overlay or underlying root. No routes or deployments changed. Private newer CAD qualification is not automatically deployed.

## Every bundled entry

Paths are relative to the desktop source root: same path inside CURRENT-CODE/desktop/, R730 desktop source and the desktop Git repo. For deployed entry paths see JSON. Historical checks retain their original scope.

| App/tool | ksu.codes | Beta | Source directory | Status |
|---|---|---|---|---|
| Calculator (`calculator`) | launcher | launcher | `apps/system/calculator` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Files (`files`) | launcher | launcher | `apps/system/files` | Files foundation accepted within documented scope; main/beta serving graphs differ |
| Help (`help`) | launcher | launcher | `apps/system/help` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Browser (`browser`) | absent | disabled development | `apps/system/browser` | Disabled / in development; external relay disabled |
| Codemirror (`codemirror`) | dependency | shared disabled | `apps/system/codemirror` | Shared library: bundled, launcher disabled by design; consumer qualification required |
| Terminal (`terminal`) | launcher | launcher | `apps/system/terminal` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Text Editor (CodeMirror 6) (`text`) | launcher | launcher | `apps/system/text` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Document Editor (Tiptap) (`document-editor`) | absent | launcher | `apps/system/document-editor` | Historical primary-workflow checks; not freshly requalified by this inventory |
| PDF Viewer (PDF.js) (`pdf-viewer`) | absent | launcher | `apps/system/pdf-viewer` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Spreadsheet (Jspreadsheet CE + SheetJS CE) (`spreadsheet`) | absent | launcher | `apps/system/spreadsheet` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Data Explorer (Perspective + DuckDB) (`data-explorer`) | absent | launcher | `apps/system/data-explorer` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Ffmpeg (`ffmpeg`) | absent | shared disabled | `apps/system/ffmpeg` | Shared library: bundled, launcher disabled by design; consumer qualification required |
| Wavesurfer (`wavesurfer`) | absent | shared disabled | `apps/system/wavesurfer` | Shared library: bundled, launcher disabled by design; consumer qualification required |
| Tone (`tone`) | absent | shared disabled | `apps/system/tone` | Shared library: bundled, launcher disabled by design; consumer qualification required |
| Audio Editor (AudioMass) (`audio-editor`) | absent | launcher | `apps/system/audio-editor` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Zip (`zip`) | absent | shared disabled | `apps/system/zip` | Shared library: bundled, launcher disabled by design; consumer qualification required |
| G-code Viewer (G-code Preview) (`gcode-preview`) | absent | launcher | `apps/system/gcode-preview` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Grid Tools (`grid-tools`) | absent | provider | `apps/system/grid-tools` | Kiri:Moto / Mesh:Tool provider; historical checks, manufacturing validity incomplete |
| Mermaid (`mermaid`) | absent | shared disabled | `apps/system/mermaid` | Shared library: bundled, launcher disabled by design; consumer qualification required |
| Echarts (`echarts`) | absent | shared disabled | `apps/system/echarts` | Shared library: bundled, launcher disabled by design; consumer qualification required |
| Plotly (`plotly`) | absent | shared disabled | `apps/system/plotly` | Shared library: bundled, launcher disabled by design; consumer qualification required |
| Pdfme (`pdfme`) | absent | shared disabled | `apps/system/pdfme` | Shared library: bundled, launcher disabled by design; consumer qualification required |
| Maplibre (`maplibre`) | absent | shared disabled | `apps/system/maplibre` | Shared library: bundled, launcher disabled by design; consumer qualification required |
| Transformers (`transformers`) | absent | shared disabled | `apps/system/transformers` | Shared library: bundled, launcher disabled by design; consumer qualification required |
| Primitive 3D Modeler (Replicad) (`replicad`) | absent | launcher | `apps/system/replicad` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Diagram Editor (diagrams.net) (`diagrams-net`) | absent | launcher | `apps/system/diagrams-net` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Python Notebook (JupyterLite + Pyodide) (`notebook`) | absent | launcher | `apps/system/notebook` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Sketch Board (Excalidraw) (`excalidraw`) | absent | launcher | `apps/system/excalidraw` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Vector Editor (SVG-Edit) (`svg-editor`) | absent | launcher | `apps/system/svg-editor` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Arduino Simulator (AVR8js) (`arduino-simulator`) | absent | launcher | `apps/system/arduino-simulator` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Pico Simulator (RP2040js) (`pico-simulator`) | absent | launcher | `apps/system/pico-simulator` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Circuit Simulator (CircuitJS) (`circuitjs`) | absent | launcher | `apps/system/circuitjs` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Electronics Design (designElectronics) (`electronics-design`) | absent | launcher | `apps/system/electronics-design` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Digital Logic Simulator (DigitalJS) (`digital-logic`) | absent | launcher | `apps/system/digital-logic` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Embroidery Studio (StitchFoundry) (`embroidery-studio`) | absent | launcher | `apps/system/embroidery-studio` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Stitch Converter (tsembroidery) (`stitch-converter`) | absent | launcher | `apps/system/stitch-converter` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Personal Template (`personal-template`) | absent | template | `apps/individual/templates` | Author example; no default end-user launcher |
| Image Editor (Filerobot) (`image-editor`) | absent | launcher | `apps/system/image-editor` | Historical primary-workflow checks; not freshly requalified by this inventory |
| Trystero (`trystero`) | absent | shared disabled | `apps/system/trystero` | Shared library: bundled, launcher disabled by design; consumer qualification required |
| Tanstack Virtual (`tanstack-virtual`) | absent | shared disabled | `apps/system/tanstack-virtual` | Shared library: bundled, launcher disabled by design; consumer qualification required |
| Onnx Runtime (`onnx-runtime`) | absent | shared disabled | `apps/system/onnx-runtime` | Shared library: bundled, launcher disabled by design; consumer qualification required |
| Webtorrent (`webtorrent`) | absent | shared disabled | `apps/system/webtorrent` | Shared library: bundled, launcher disabled by design; consumer qualification required |
| Yjs (`yjs`) | absent | shared disabled | `apps/system/yjs` | Shared library: bundled, launcher disabled by design; consumer qualification required |
| Falling Blocks (`falling-blocks`) | absent | launcher | `apps/games/01-phaser-arcade/falling-blocks` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Owl Companion (`owl-companion`) | absent | launcher | `apps/games/04-rive-interactives/owl-companion` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Physics Playground (`physics-playground`) | absent | launcher | `apps/games/02-three-physics-xr/physics-playground` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Snake Garden (`snake-garden`) | absent | launcher | `apps/games/01-phaser-arcade/snake-garden` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Chess Study (`chess-study`) | absent | launcher | `apps/games/01-phaser-arcade/chess-study` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Clockwork Quest (`clockwork-quest`) | absent | launcher | `apps/games/03-babylon-xr-games/clockwork-quest` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Clockwork Room (`clockwork-room`) | absent | launcher | `apps/games/03-babylon-xr-games/clockwork-room` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Crystal Defense (`crystal-defense`) | absent | launcher | `apps/games/03-babylon-xr-games/crystal-defense` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Drone Circuit (`drone-circuit`) | absent | launcher | `apps/games/03-babylon-xr-games/drone-circuit` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Expression Puppet (`expression-puppet`) | absent | launcher | `apps/games/04-rive-interactives/expression-puppet` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Garden Defense (`garden-defense`) | absent | launcher | `apps/games/01-phaser-arcade/garden-defense` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Gravity Pinball (`gravity-pinball`) | absent | launcher | `apps/games/02-three-physics-xr/gravity-pinball` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Kinetic Relay (`kinetic-relay`) | absent | launcher | `apps/games/02-three-physics-xr/kinetic-relay` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Lantern Leap (`lantern-leap`) | absent | launcher | `apps/games/01-phaser-arcade/lantern-leap` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Marble Works (`marble-works`) | absent | launcher | `apps/games/02-three-physics-xr/marble-works` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Memory Garden (`memory-garden`) | absent | launcher | `apps/games/04-rive-interactives/memory-garden` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Orbital Courier (`orbital-courier`) | absent | launcher | `apps/games/03-babylon-xr-games/orbital-courier` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Pocket Golf (`pocket-golf`) | absent | launcher | `apps/games/03-babylon-xr-games/pocket-golf` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Pocket Rally (`pocket-rally`) | absent | launcher | `apps/games/01-phaser-arcade/pocket-rally` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Reactive Control Desk (`reactive-control-desk`) | absent | launcher | `apps/games/04-rive-interactives/reactive-control-desk` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Rhythm Garden (`rhythm-garden`) | absent | launcher | `apps/games/04-rive-interactives/rhythm-garden` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Sky Courier (`sky-courier`) | absent | launcher | `apps/games/01-phaser-arcade/sky-courier` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Sling Targets (`sling-targets`) | absent | launcher | `apps/games/02-three-physics-xr/sling-targets` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Solitaire (`solitaire`) | absent | launcher | `apps/games/01-phaser-arcade/solitaire` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Stack Balance (`stack-balance`) | absent | launcher | `apps/games/02-three-physics-xr/stack-balance` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Story Cards (`story-cards`) | absent | launcher | `apps/games/04-rive-interactives/story-cards` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Tabletop Bot Arena (`tabletop-bot-arena`) | absent | launcher | `apps/games/02-three-physics-xr/tabletop-bot-arena` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Target Garden (`target-garden`) | absent | launcher | `apps/games/03-babylon-xr-games/target-garden` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| Opencascade (`opencascade`) | absent | shared disabled | `apps/system/opencascade` | Shared library: bundled, launcher disabled by design; consumer qualification required |
| Gltf Transform (`gltf-transform`) | absent | shared disabled | `apps/system/gltf-transform` | Shared library: bundled, launcher disabled by design; consumer qualification required |
| Microduck (`microduck`) | absent | launcher | `apps/system/microduck` | Preview; historical checks only; physical-device/XR/full-content gates remain |
| CAD Modeler (JSketcher inspired) (`jsketcher`) | absent | launcher | `apps/system/jsketcher` | Beta R4 scoped public checks; newer private ACAD20/21 ordinary exercises; fullGate1 open |

## Additional launchers/plans

| Entry | Availability/status | Source |
|---|---|---|
| Fabrication Studio (Kiri:Moto) | Beta enabled; historical workflow, manufacturing/device validation open | `apps/system/grid-tools/` |
| Mesh Editor (Mesh:Tool) | Beta enabled; historical workflow, undo/manufacturing correctness incomplete | `apps/system/grid-tools/` |
| Python Notebook — Linux | Beta disabled/in development | `apps/system/notebook/` + guest integration |
| Math Path | Beta disabled, rules core only; no finished GUI/storage/assets | `apps/games/05-core-learning-strategy/math-path/` |
| Fraction Farm | Beta disabled, rules core only; no finished GUI/storage/assets | `apps/games/05-core-learning-strategy/fraction-farm/` |
| Word Weaver | Beta disabled, rules core only; no finished GUI/storage/assets | `apps/games/05-core-learning-strategy/word-weaver/` |
| Rule Detective | Beta disabled, rules core only; no finished GUI/storage/assets | `apps/games/05-core-learning-strategy/rule-detective/` |
| Market Math | Beta disabled, rules core only; no finished GUI/storage/assets | `apps/games/05-core-learning-strategy/market-math/` |
| Pocket Conquest | Beta disabled, rules core only; no finished GUI/storage/assets | `apps/games/05-core-learning-strategy/pocket-conquest/` |
| Tile Islands | Beta disabled, rules core only; no finished GUI/storage/assets | `apps/games/05-core-learning-strategy/tile-islands/` |

Circuit Lab (`apps/system/circuit-lab/`) and PCB Design (`apps/system/pcb-design/`) are research source absent from selected catalogs. `apps/UNFINISHED-TO INTEGRATE-PARTIAL/` is reference/planning work, not a second deployed tree. Games remain previews; shared tools need qualification through actual consumers. Main's small set is essential integration targets, not universally finished software. Details and per-app limitations remain in the linked historical review.
