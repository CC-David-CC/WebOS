# Current source and rebuild status matrix

This chart covers the parent selection at `58dd6244f449cd1f1a15647d7121c17bd9449bec`.
Git links select exact revisions. All112 pins match the clean first-slice source
proof and remain in local bare origins. That browser qualification initialized
eleven components; it does not prove all112 components build or work.

There are111 component repositories plus1 preserved legacy repository:
78 apps (33 system/CAD,17 Craft,28 games),8 engines,5 platform components,
17 libraries,2 shared asset projects and1 shared tooling project, plus legacy Rooms.

**PASS** covers the stated check. **OPEN** means incomplete or unverified.
Retained baseline tests are separate from new runtime acceptance.

| Gate | Current result |
|---|---|
| Registered component source layout | PASS:112 independent repositories listed below |
| Entire original source-area reconciliation | OPEN: preserved backend, scripts, research, tests and WIP still need final disposition |
| Calculator → Files → Text → WordCraft | PASS local/clean workflows and disposable-account checks on ksu.codes |
| Server account files | PASS signed persistence, conflicts, restart and second clean browser context |
| Physical second-machine acceptance | OPEN; browser contexts are not a second machine |
| Human/agent operations | Live routing and Accounts core checks PASS; authenticated transport, consent and scoped agent file authority OPEN |
| Remaining16 Craft apps and old app/game integration | OPEN; source presence is not app support |
| Native/font review | Math-font cause fixed in review; WordCraft main4,969 tests PASS; full application CI OPEN; shared default-workspace checks PASS in review |
| Historical assets and old-user migration | Not prerequisites for the fresh rebuild; preserve existing recovery |
| External Git publication | Not authorized or attempted; local origins are not off-machine backups |

The original workspace and beta site remain unchanged. ksu.codes is the fresh
test target; [deployment status](../deploy/TEST-STATUS.md) records what it serves.
Help and newer authority/routing/delegation changes remain local. The preserved
office substitute, ACAD and original JSketcher remain separate applications.
Hosted Rooms is unused historical code, not a new service.

## Platform (5)

| Component | Directory | Source/history | Checks | New assembly |
|---|---|---|---|---|
| accounts | `platform/accounts/` | PASS | PASS:21 retained-identity/delegation tests and signed browser regression | PASS human account policy; optional delegation core inactive, transport/file authority OPEN |
| desktop | `platform/desktop/` | PASS | PASS selected first-slice component and actual browser workflows | PASS local/clean composition; see deployment status for the earlier hosted pins |
| login | `platform/login/` | PASS | PASS selected first-slice component and actual browser workflows | PASS local/clean composition; see deployment status for the earlier hosted pins |
| runtime | `platform/runtime/` | PASS | PASS selected first-slice component and actual browser workflows | PASS local/clean composition; see deployment status for the earlier hosted pins |
| storage | `platform/storage/` | PASS | PASS selected first-slice component and actual browser workflows | PASS local/clean composition; see deployment status for the earlier hosted pins |

## System and CAD apps (33)

| Component | Directory | Source/history | Checks | New assembly |
|---|---|---|---|---|
| acad | `apps/acad/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| arduino-simulator | `apps/arduino-simulator/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| audio-editor | `apps/audio-editor/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| browser | `apps/browser/` | PASS | FAIL - one unchanged pre-existing stale host-contract assertion | OPEN: complete browser build and new host integration not qualified |
| calculator | `apps/calculator/` | PASS | PASS selected first-slice component and actual browser workflows | PASS local/clean composition; see deployment status for the earlier hosted pins |
| circuit-lab | `apps/circuit-lab/` | PASS | PASS retained extraction/domain probes; browser and distribution qualification OPEN | OPEN: complete browser build and new host integration not qualified |
| circuitjs | `apps/circuitjs/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| data-explorer | `apps/data-explorer/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| diagrams-net | `apps/diagrams-net/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| digital-logic | `apps/digital-logic/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| document-editor | `apps/document-editor/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| electronics-design | `apps/electronics-design/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| embroidery-studio | `apps/embroidery-studio/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| excalidraw | `apps/excalidraw/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| files | `apps/files/` | PASS | PASS selected first-slice component and actual browser workflows | PASS local/clean composition; see deployment status for the earlier hosted pins |
| gcode-preview | `apps/gcode-preview/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| grid-tools | `apps/grid-tools/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| help | `apps/help/` | PASS | PASS:5 boundary checks and signed Desktop lifecycle | PASS local/clean; not in hosted phase15 release |
| image-editor | `apps/image-editor/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| legacy-jsketcher | `apps/jsketcher/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| linux | `apps/linux/` | PASS | PASS independent source/history and static base inputs | OPEN optional host port; excluded from minimum dependencies |
| microduck | `apps/microduck/` | PASS | FAIL - 200 pass / 11 missing-fixture failures; baseline and extraction match | OPEN: complete browser build and new host integration not qualified |
| notebook | `apps/notebook/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| pdf-viewer | `apps/pdf-viewer/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| pcb-design | `apps/pcb-design/` | PASS | PASS retained extraction/domain probes; browser and distribution qualification OPEN | OPEN: complete browser build and new host integration not qualified |
| personal-template | `apps/personal-template/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| pico-simulator | `apps/pico-simulator/` | PASS | PASS - four configured simulator test commands | OPEN: complete browser build and new host integration not qualified |
| replicad | `apps/replicad/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| spreadsheet | `apps/spreadsheet/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| stitch-converter | `apps/stitch-converter/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| svg-editor | `apps/svg-editor/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| terminal | `apps/terminal/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| text | `apps/text/` | PASS | PASS selected first-slice component and actual browser workflows | PASS local/clean composition; see deployment status for the earlier hosted pins |

## Craft apps (17)

| Component | Directory | Source/history | Checks | New assembly |
|---|---|---|---|---|
| anicraft | `apps/anicraft/` | PASS | OPEN - selected source baseline only | OPEN: complete browser build and new host integration not qualified |
| cadcraft | `apps/cadcraft/` | PASS | OPEN - selected source baseline only | OPEN: complete browser build and new host integration not qualified |
| deckcraft | `apps/deckcraft/` | PASS | OPEN - selected source baseline only | OPEN: complete browser build and new host integration not qualified |
| designcraft | `apps/designcraft/` | PASS | OPEN - selected source baseline only | OPEN: complete browser build and new host integration not qualified |
| effectcraft | `apps/effectcraft/` | PASS | OPEN - selected source baseline only | OPEN: complete browser build and new host integration not qualified |
| figcraft | `apps/figcraft/` | PASS | OPEN - selected source baseline only | OPEN: complete browser build and new host integration not qualified |
| filmcraft | `apps/filmcraft/` | PASS | OPEN - selected source baseline only | OPEN: complete browser build and new host integration not qualified |
| gridcraft | `apps/gridcraft/` | PASS | OPEN - selected source baseline only | OPEN: complete browser build and new host integration not qualified |
| lightcraft | `apps/lightcraft/` | PASS | OPEN - selected source baseline only | OPEN: complete browser build and new host integration not qualified |
| materialcraft | `apps/materialcraft/` | PASS | OPEN - selected source baseline only | OPEN: complete browser build and new host integration not qualified |
| pdfcraft | `apps/pdfcraft/` | PASS | OPEN - selected source baseline only | OPEN: complete browser build and new host integration not qualified |
| photocraft | `apps/photocraft/` | PASS | OPEN - selected source baseline only | OPEN: complete browser build and new host integration not qualified |
| solidcraft | `apps/solidcraft/` | PASS | OPEN - selected source baseline only | OPEN: complete browser build and new host integration not qualified |
| soundcraft | `apps/soundcraft/` | PASS | OPEN - selected source baseline only | OPEN: complete browser build and new host integration not qualified |
| texturecraft | `apps/texturecraft/` | PASS | OPEN - selected source baseline only | OPEN: complete browser build and new host integration not qualified |
| vectorcraft | `apps/vectorcraft/` | PASS | OPEN - selected source baseline only | OPEN: complete browser build and new host integration not qualified |
| wordcraft | `apps/wordcraft/` | PASS | PASS real WASM authoring, formatting, account persistence, conflicts and lifecycle | PASS local/clean and earlier hosted pin; newer native/font review and delegated agents OPEN |

## Games (28)

| Component | Directory | Source/history | Checks | New assembly |
|---|---|---|---|---|
| chess-study | `apps/chess-study/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| clockwork-quest | `apps/clockwork-quest/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| clockwork-room | `apps/clockwork-room/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| crystal-defense | `apps/crystal-defense/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| drone-circuit | `apps/drone-circuit/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| expression-puppet | `apps/expression-puppet/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| falling-blocks | `apps/falling-blocks/` | PASS | OPEN - no original package suite; coach render/rebuild not run | OPEN: complete browser build and new host integration not qualified |
| garden-defense | `apps/garden-defense/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| gravity-pinball | `apps/gravity-pinball/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| kinetic-relay | `apps/kinetic-relay/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| lantern-leap | `apps/lantern-leap/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| marble-works | `apps/marble-works/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| memory-garden | `apps/memory-garden/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| orbital-courier | `apps/orbital-courier/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| owl-companion | `apps/owl-companion/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| physics-playground | `apps/physics-playground/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| pocket-golf | `apps/pocket-golf/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| pocket-rally | `apps/pocket-rally/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| reactive-control-desk | `apps/reactive-control-desk/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| rhythm-garden | `apps/rhythm-garden/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| sky-courier | `apps/sky-courier/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| sling-targets | `apps/sling-targets/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| snake-garden | `apps/snake-garden/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| solitaire | `apps/solitaire/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| stack-balance | `apps/stack-balance/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| story-cards | `apps/story-cards/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| tabletop-bot-arena | `apps/tabletop-bot-arena/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |
| target-garden | `apps/target-garden/` | PASS | PASS - configured independent domain/type checks | OPEN: complete browser build and new host integration not qualified |

## Engines (8)

| Component | Directory | Source/history | Checks | New assembly |
|---|---|---|---|---|
| engine-ffmpeg | `engines/ffmpeg/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| engine-manifold | `engines/manifold/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| engine-onnx-runtime | `engines/onnx-runtime/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| engine-opencascade | `engines/occt-interpreter/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| engine-opencascade-js | `engines/opencascade-js/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| engine-smlib-wasm | `engines/smlib-wasm/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| engine-usd-brep | `engines/usd-brep/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| engine-v86 | `engines/v86/` | PASS | PASS engine source/history and optional static inputs | OPEN optional guest integration; excluded from minimum dependencies |

## Shared libraries and tools (17)

| Component | Directory | Source/history | Checks | New assembly |
|---|---|---|---|---|
| codemirror | `libraries/codemirror/` | PASS | PASS selected first-slice component and actual browser workflows | PASS local/clean composition; see deployment status for the earlier hosted pins |
| craft-libs | `libraries/craft-libs/` | PASS | Pinned histories retained; review3b3271f4 passes default workspace fmt, Clippy and tests | Reviewed shared commit unselected; app dependency versions remain explicit |
| echarts | `libraries/echarts/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| egui | `libraries/egui/` | PASS | PASS selected first-slice component and actual browser workflows | PASS local/clean composition; see deployment status for the earlier hosted pins |
| gltf-transform | `libraries/gltf-transform/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| maplibre | `libraries/maplibre/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| mermaid | `libraries/mermaid/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| pdfme | `libraries/pdfme/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| plotly | `libraries/plotly/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| tanstack-virtual | `libraries/tanstack-virtual/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| tone | `libraries/tone/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| transformers | `libraries/transformers/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| trystero | `libraries/trystero/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| wavesurfer | `libraries/wavesurfer/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| webtorrent | `libraries/webtorrent/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| yjs | `libraries/yjs/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| zip | `libraries/zip/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |

## Shared asset projects (2)

| Component | Directory | Source/history | Checks | New assembly |
|---|---|---|---|---|
| craft-fonts | `assets/craft-fonts/` | PASS | PASS pinned build input; new STIX review passes clean font checks | Selected input used by WordCraft; e5f6cc5 math-font review unselected |
| craft-i18n | `assets/craft-i18n/` | PASS | PASS pinned WordCraft translation/proofing build input | PASS selected WordCraft composition; other consumers OPEN |

## Shared build tooling (1)

| Component | Directory | Source/history | Checks | New assembly |
|---|---|---|---|---|
| craft-common-actions | `tooling/craft-common-actions/` | PASS | OPEN - no release workflow executed; top-level license review pending | OPEN: complete browser build and new host integration not qualified |

## Preserved legacy source (1)

| Component | Directory | Source/history | Checks | New assembly |
|---|---|---|---|---|
| rooms | `legacy/rooms/` | PASS | PASS preserved source/history; user confirms unused | NOT IN SCOPE for active system; preservation only |

## Remaining organization and build work

The112-row chart does not close original-source reconciliation. An earlier
tracked-source ledger still had6,026 entries without verified final disposition.
That stale audit count is not proof that6,026 files are missing. Baseline histories,
new path maps, generated evidence and deliberately preserved historical material
must be compared explicitly. Backend/network/build/test/research areas and WIP
remain preserved privately. Required current source must get an owner; obsolete
evidence and sensitive data must not be copied into release roots.

Linux/v86 source and static inputs are organized at `apps/linux/` and
`engines/v86/`; their optional host port remains OPEN. FFmpeg is the shared engine
at `engines/ffmpeg/`; TanStack Virtual is at `libraries/tanstack-virtual/`.
Neither source repository is a claim of an enabled standalone app.

Frozen beta payloads and historical input locks are reference/recovery material,
not fresh build output or prerequisites for the first useful system. Existing
Browser/Microduck baseline failures remain evidence; no assertions were weakened.
Every additional app needs its actual asset graph, lifecycle, shared operations
and browser acceptance checked at the selected source revision.

The unresolved ledger also contains seven source-only planned game cores:
Math Path, Fraction Farm, Word Weaver, Market Math, Rule Detective, Pocket Conquest
and Tile Islands. They have rules and tests but no Desktop view. Their separate
repositories and shared-helper ownership still need extraction/review; they are
not included in the28 registered-game count above. The inspected source prefix
has no staged, unstaged or untracked work at the current audit boundary.
