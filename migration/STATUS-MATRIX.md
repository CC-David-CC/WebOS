# Current source and rebuild status matrix

Git links select exact revisions. The assembly has123 independent source repositories:
85 apps (33 system/CAD,17 Craft,35 games including7 planned cores),8 engines,
7 platform components,19 libraries,2 shared asset projects,1 shared tooling project
and1 preserved legacy repository. Source placement and scoped component checks
do not prove all123 components build or work.

**PASS** covers the stated check. **OPEN** means incomplete or unverified.
Retained baseline tests are separate from new runtime acceptance.

| Gate | Current result |
|---|---|
| Registered component source layout | PASS:123 independent repositories listed below |
| Entire original source-area reconciliation | OPEN: preserved backend, scripts, research, tests and WIP still need final disposition |
| Calculator → Files → Text → WordCraft | PASS local/clean workflows and disposable-account checks on ksu.codes |
| Server account files | PASS signed persistence, conflicts, restart and second clean browser context |
| Physical second-machine acceptance | OPEN; browser contexts are not a second machine |
| Human/agent operations | Live routing and Accounts core checks PASS; authenticated transport, consent and scoped agent file authority OPEN |
| Remaining16 Craft apps and old app/game integration | OPEN; source presence is not app support |
| Native/font review | PASS selected WordCraft all9 CI stages, declared font input and clean browser workflows; broader-suite qualification OPEN |
| Historical assets and old-user migration | Not prerequisites for the fresh rebuild; preserve existing recovery |
| External Git publication | Not authorized or attempted; local origins are not off-machine backups |

The original workspace and beta site remain unchanged. ksu.codes is the fresh
test target; [deployment status](../deploy/TEST-STATUS.md) records what it serves.
Help and newer authority/routing/delegation changes remain local. The preserved
office substitute, ACAD and original JSketcher remain separate applications.
Hosted Rooms is unused historical code, not a new service.

## Platform (7)

| Component | Directory | Source/history | Checks | New assembly |
|---|---|---|---|---|
| accounts | `platform/accounts/` | PASS | PASS:67 layered tests (42 retained core,25 policy/delegation); historical policy differences documented | PASS human account policy; optional delegation core inactive, transport/file authority OPEN |
| desktop | `platform/desktop/` | PASS | PASS selected first-slice component and actual browser workflows | PASS local/clean composition; see deployment status for the earlier hosted pins |
| login | `platform/login/` | PASS | PASS selected first-slice component and actual browser workflows | PASS local/clean composition; see deployment status for the earlier hosted pins |
| publication | `platform/publication/` | PASS33 source/test histories plus28 unchanged legacy command/check files | PASS scoped unsigned reconstruction fixture; full imports/build OPEN | SOURCE ONLY: interface port, signed/runtime/browser-agent acceptance OPEN; disabled |
| rendezvous | `platform/rendezvous/` | PASS13 original files/history | PASS37 unchanged lease tests and9 installed-module imports with source hidden | OPEN: signed transport, root/publisher custody, browser/agent integration; disabled |
| runtime | `platform/runtime/` | PASS | PASS selected first-slice component and actual browser workflows | PASS local/clean composition; see deployment status for the earlier hosted pins |
| storage | `platform/storage/` | PASS | PASS selected first-slice component and actual browser workflows | PASS local/clean composition; see deployment status for the earlier hosted pins |

## System and CAD apps (33)

| Component | Directory | Source/history | Checks | New assembly |
|---|---|---|---|---|
| acad | `apps/acad/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| arduino-simulator | `apps/arduino-simulator/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| audio-editor | `apps/audio-editor/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| browser | `apps/browser/` | PASS including separate backend extraction | PASS56 Python tests and installed-wheel isolation; JS93 PASS/1 pre-existing host-contract failure | OPEN: complete browser build and new host integration not qualified |
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
| linux | `apps/linux/` | PASS including optional guest backend history | PASS34 installed-wheel Python tests and12 module imports; static base inputs retained | OPEN optional host port; excluded from minimum dependencies |
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
| wordcraft | `apps/wordcraft/` | PASS | PASS selected source all9 CI stages, actual WASM math font, authoring, persistence, conflicts and lifecycle | PASS latest local/clean source; hosted release remains older, delegated agents OPEN |

## Games (35:28 registered,7 source-only planned cores)

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
| math-path | `apps/math-path/` | PASS | PASS: original domain/snapshot tests after independent public-package port | OPEN: planned core only; no Desktop view, renderer or server storage adapter |
| fraction-farm | `apps/fraction-farm/` | PASS | PASS: original domain/snapshot tests after independent public-package port | OPEN: planned core only; no Desktop view, renderer or server storage adapter |
| word-weaver | `apps/word-weaver/` | PASS | PASS: original domain/snapshot tests after independent public-package port | OPEN: planned core only; no Desktop view, renderer or server storage adapter |
| market-math | `apps/market-math/` | PASS | PASS: original domain/snapshot tests after independent public-package port | OPEN: planned core only; no Desktop view, renderer or server storage adapter |
| rule-detective | `apps/rule-detective/` | PASS | PASS: original domain/snapshot tests after independent public-package port | OPEN: planned core only; no Desktop view, renderer or server storage adapter |
| pocket-conquest | `apps/pocket-conquest/` | PASS | PASS: original domain/snapshot tests after independent public-package port | OPEN: planned core only; no Desktop view, renderer or server storage adapter |
| tile-islands | `apps/tile-islands/` | PASS | PASS: original domain/snapshot tests after independent public-package port | OPEN: planned core only; no Desktop view, renderer or server storage adapter |

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

## Shared libraries and tools (19)

| Component | Directory | Source/history | Checks | New assembly |
|---|---|---|---|---|
| codemirror | `libraries/codemirror/` | PASS | PASS selected first-slice component and actual browser workflows | PASS local/clean composition; see deployment status for the earlier hosted pins |
| craft-libs | `libraries/craft-libs/` | PASS | Selected3b3271f4 passes default workspace fmt, Clippy and tests | Selected shared history; WordCraft dependency pins are explicit, other consumers OPEN |
| echarts | `libraries/echarts/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| egui | `libraries/egui/` | PASS | PASS selected first-slice component and actual browser workflows | PASS local/clean composition; see deployment status for the earlier hosted pins |
| gltf-transform | `libraries/gltf-transform/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| maplibre | `libraries/maplibre/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| mermaid | `libraries/mermaid/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| network-policy | `libraries/network-policy/` | PASS11 paths/history, baseline retained | PASS core10 tests/1 existing optional GeoIP skip;8 installed-module imports and package isolation | OPEN actual GeoIP/proxy/guest wiring; not enabled |
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
| learning-game-core | `libraries/learning-game-core/` | PASS | PASS: shared validation/report/odds modules, original experience tests and parent cross-game tests | Public package used by7 planned cores; no independent Desktop view |

## Shared asset projects (2)

| Component | Directory | Source/history | Checks | New assembly |
|---|---|---|---|---|
| craft-fonts | `assets/craft-fonts/` | PASS | PASS selected e5f6cc5, clean glyph/MATH/license checks and actual WASM font | PASS selected WordCraft artifact; other consumers OPEN |
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

The123-row chart does not close original-source reconciliation. The tracked-source
ledger now has3,382 unresolved entries plus35 unqualified blob candidates, after
23 planned-game/metadata dispositions,16 Accounts/Storage history retentions and
10 Browser backend/test,16 optional guest backend/test and1 identity-test extractions,
plus4 identity-core history retentions,13 rendezvous and33 publication source/test/metadata
dispositions, plus28 publication command/test sources, were verified.
All44 original steward-area paths now have source owners;
this does not qualify either service as active. A further315 historical output records
are verified in private recovery, with three byte/mode restore samples. Their old
reported results are not new acceptance proof; possible fixture/input reuse remains
separate review. See [historical evidence](HISTORICAL-EVIDENCE.md). These counts do not mean
those files are missing. Baseline histories,
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

Seven planned game cores now have independent histories/packages and one shared
library. All57 original tests pass through public exports after separation.
They remain source-only prototypes, separate from the28 previously registered
games. See [their exact qualification and save-version limits](LEARNING-GAMES.md).
The inspected original prefix had no staged, unstaged or untracked work.

The [CAD corpus catalogue](CAD-CORPUS.md) records276 unchanged parent-owned legacy
acceptance source files and34 privately retained frozen build/catalog records.
Syntax and history are verified; no legacy CAD driver or qualification ran.
Helpers/inputs/target/runtime/authorization ports remain OPEN; the33 source reviews are resolved in phase35.

Phase35 retains the remaining33 reviewed synthetic-fixture source paths with history:276 total legacy CAD corpus code files, syntax checked and unexecuted. Runtime/API/fixture/input ports remain incomplete.

Phase36 retains760 unchanged historical desktop browser-test sources with selected histories, syntax checked and disabled pending deliberate ports. See [legacy desktop tests](LEGACY-DESKTOP-TESTS.md). No current app or browser qualification follows from this extraction.

Phase37 verifies nine previously unresolved identity/file-client/verifier/loader-test records already retained in selected component histories, using exact blob/mode and rename-lineage witnesses. No duplicate extraction or behavior change. See [history reconciliation](HISTORY-RECONCILIATION.md).

Phase38 adds independent shared network-policy source at `libraries/network-policy/`:11 retained source/config/test paths, original and installed-wheel10 passes/1 existing optional database skip. No firewall, listener or desktop policy enabled. See [network policy](NETWORK-POLICY.md).

Phase39 retains1075 unchanged historical operations/build/check Python sources and selected histories at `deploy/legacy-operations/`, disabled pending deliberate authorization/target/interface/side-effect ports. Syntax/history only; no old driver executed. See [legacy operations](LEGACY-OPERATIONS.md).

Phase40 retains85 original desktop visual/license inputs with history in Desktop, including74 launcher icons and wallpaper. Asset bytes/modes, PNG data and representative decoding are verified; active rendering is unchanged. See [desktop assets](DESKTOP-ASSETS.md).
