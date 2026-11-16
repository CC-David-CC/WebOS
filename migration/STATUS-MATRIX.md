# Current source and rebuild status matrix

Git links select exact revisions. The assembly has124 independent source repositories:
85 apps (33 system/CAD,17 Craft,35 games including7 planned cores),9 engines,
7 platform components,19 libraries,2 shared asset projects,1 shared tooling project
and1 preserved legacy repository. Source placement and scoped component checks
do not prove all124 components build or work.

**PASS** covers the stated check. **OPEN** means incomplete or unverified.
Retained baseline tests are separate from new runtime acceptance.

| Gate | Current result |
|---|---|
| Registered component source layout | PASS:124 independent repositories listed below |
| Entire original source-area reconciliation | OPEN: preserved backend, scripts, research, tests and WIP still need final disposition |
| Calculator → Files → Text → WordCraft | PASS local/clean workflows and disposable-account checks on ksu.codes |
| Server account files | PASS signed persistence, conflicts, restart and second clean browser context |
| Physical second-machine acceptance | OPEN; browser contexts are not a second machine |
| Human/agent operations | Live routing and Accounts core checks PASS; authenticated transport, consent and scoped agent file authority OPEN |
| Remaining15 Craft apps and old app/game integration | OPEN; source presence is not app support |
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
| acad | `apps/acad/` | PASS | OPEN - no component behavior qualification claimed; phase44 Node reference 214 pass/3 captured fail | OPEN: complete browser build and new host integration not qualified |
| arduino-simulator | `apps/arduino-simulator/` | PASS | OPEN - no component behavior qualification claimed; phase44 Node reference 2 pass/0 captured fail | OPEN: complete browser build and new host integration not qualified |
| audio-editor | `apps/audio-editor/` | PASS | OPEN - no component behavior qualification claimed; phase44 Node reference 6 pass/0 captured fail | OPEN: complete browser build and new host integration not qualified |
| browser | `apps/browser/` | PASS including separate backend extraction | PASS56 Python tests and installed-wheel isolation; JS93 PASS/1 pre-existing host-contract failure; phase44 Node reference 9 pass/0 captured fail | OPEN: complete browser build and new host integration not qualified |
| calculator | `apps/calculator/` | PASS | PASS selected first-slice component and actual browser workflows | PASS local/clean composition; see deployment status for the earlier hosted pins |
| circuit-lab | `apps/circuit-lab/` | PASS | PASS retained extraction/domain probes; browser and distribution qualification OPEN | OPEN: complete browser build and new host integration not qualified |
| circuitjs | `apps/circuitjs/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| data-explorer | `apps/data-explorer/` | PASS | OPEN - no component behavior qualification claimed; phase44 Node reference 7 pass/0 captured fail | OPEN: complete browser build and new host integration not qualified |
| diagrams-net | `apps/diagrams-net/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| digital-logic | `apps/digital-logic/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| document-editor | `apps/document-editor/` | PASS | OPEN - no component behavior qualification claimed; phase44 Node reference 6 pass/0 captured fail | OPEN: complete browser build and new host integration not qualified |
| electronics-design | `apps/electronics-design/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| embroidery-studio | `apps/embroidery-studio/` | PASS | OPEN - no component behavior qualification claimed; phase44 Node reference 1 pass/0 captured fail | OPEN: complete browser build and new host integration not qualified |
| excalidraw | `apps/excalidraw/` | PASS | OPEN - no component behavior qualification claimed; phase44 Node reference 3 pass/0 captured fail | OPEN: complete browser build and new host integration not qualified |
| files | `apps/files/` | PASS | PASS selected first-slice component and actual browser workflows | PASS local/clean composition; see deployment status for the earlier hosted pins |
| gcode-preview | `apps/gcode-preview/` | PASS | OPEN - no component behavior qualification claimed; phase44 Node reference 7 pass/0 captured fail | OPEN: complete browser build and new host integration not qualified |
| grid-tools | `apps/grid-tools/` | PASS | OPEN - no component behavior qualification claimed; phase44 Node reference 3 pass/0 captured fail | OPEN: complete browser build and new host integration not qualified |
| help | `apps/help/` | PASS | PASS:5 boundary checks and signed Desktop lifecycle | PASS local/clean; not in hosted phase15 release |
| image-editor | `apps/image-editor/` | PASS | OPEN - no component behavior qualification claimed; phase44 Node reference 8 pass/0 captured fail | OPEN: complete browser build and new host integration not qualified |
| legacy-jsketcher | `apps/jsketcher/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| linux | `apps/linux/` | PASS including optional guest backend history | PASS34 installed-wheel Python tests and12 module imports; static base inputs retained | OPEN optional host port; excluded from minimum dependencies |
| microduck | `apps/microduck/` | PASS | FAIL - 200 pass / 11 missing-fixture failures; baseline and extraction match | OPEN: complete browser build and new host integration not qualified |
| notebook | `apps/notebook/` | PASS | OPEN - no component behavior qualification claimed; phase44 Node reference 6 pass/0 captured fail | OPEN: complete browser build and new host integration not qualified |
| pdf-viewer | `apps/pdf-viewer/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| pcb-design | `apps/pcb-design/` | PASS | PASS retained extraction/domain probes; browser and distribution qualification OPEN | OPEN: complete browser build and new host integration not qualified |
| personal-template | `apps/personal-template/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| pico-simulator | `apps/pico-simulator/` | PASS | PASS - four configured simulator test commands; phase44 Node reference 2 pass/0 captured fail | OPEN: complete browser build and new host integration not qualified |
| replicad | `apps/replicad/` | PASS | OPEN - no component behavior qualification claimed; phase44 Node reference 1 pass/0 captured fail | OPEN: complete browser build and new host integration not qualified |
| spreadsheet | `apps/spreadsheet/` | PASS | OPEN - no component behavior qualification claimed; phase44 Node reference 13 pass/0 captured fail | OPEN: complete browser build and new host integration not qualified |
| stitch-converter | `apps/stitch-converter/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| svg-editor | `apps/svg-editor/` | PASS | OPEN - no component behavior qualification claimed; phase44 Node reference 1 pass/0 captured fail | OPEN: complete browser build and new host integration not qualified |
| terminal | `apps/terminal/` | PASS | PASS three original startup-output assertions; VM reference only | OPEN legacy host/guest APIs, xterm build and lifecycle/agent integration; optional outside minimum |
| text | `apps/text/` | PASS | PASS selected first-slice component and actual browser workflows; phase44 Node reference 5 pass/0 captured fail | PASS local/clean composition; see deployment status for the earlier hosted pins |

## Craft apps (17)

| Component | Directory | Source/history | Checks | New assembly |
|---|---|---|---|---|
| anicraft | `apps/anicraft/` | PASS | OPEN - selected source baseline only | OPEN: complete browser build and new host integration not qualified |
| cadcraft | `apps/cadcraft/` | PASS | OPEN - selected source baseline only | OPEN: complete browser build and new host integration not qualified |
| deckcraft | `apps/deckcraft/` | PASS | PASS selected45463e6b: all8 CI stages,2,291 native and15 host tests; clone-built release/receipt; actual Desktop/Files account save/reopen, independent views, second-context and stale-write checks; [scope](DECKCRAFT-ACCOUNT-INTEGRATION.md) | Optional verified --deckcraft artifact; OPEN exports, unknown reconciliation, delegated agents, physical second machine |
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
| falling-blocks | `apps/falling-blocks/` | PASS | OPEN - no original package suite; coach render/rebuild not run; phase44 Node reference 2 pass/0 captured fail | OPEN: complete browser build and new host integration not qualified |
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

## Engines (9)

| Component | Directory | Source/history | Checks | New assembly |
|---|---|---|---|---|
| engine-ffmpeg | `engines/ffmpeg/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| engine-manifold | `engines/manifold/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| engine-onnx-runtime | `engines/onnx-runtime/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| engine-opencascade | `engines/occt-interpreter/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| engine-opencascade-js | `engines/opencascade-js/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| engine-smlib-wasm | `engines/smlib-wasm/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| engine-usd-brep | `engines/usd-brep/` | PASS | OPEN - no component behavior qualification claimed | OPEN: complete browser build and new host integration not qualified |
| engine-speech | `engines/speech/` | PASS6 original source/legal/provenance paths and history | PASS34 verified inputs, offline graph build,4 transcript tests and real WASM spoken fixture; no external requests | OPEN Desktop/microphone/scoped-agent wiring and release notices; optional for minimum |
| engine-v86 | `engines/v86/` | PASS | PASS engine source/history and optional static inputs | OPEN optional guest integration; excluded from minimum dependencies |

## Shared libraries and tools (19)

| Component | Directory | Source/history | Checks | New assembly |
|---|---|---|---|---|
| codemirror | `libraries/codemirror/` | PASS | PASS selected first-slice component and actual browser workflows | PASS local/clean composition; see deployment status for the earlier hosted pins |
| craft-libs | `libraries/craft-libs/` | PASS | Selected94981849 passes workspace fmt/Clippy/tests (3,008 passes,81 ignored),12 Node/WASM host tests; correlated adoption and explicit save identity/outcomes | Selected shared history; WordCraft dependency pins are explicit, other consumers OPEN |
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
| craft-fonts | `assets/craft-fonts/` | PASS | PASS selected9ffb3a7: 66 font entries hashed,42 tests, fmt/Clippy/embed checks; DeckCraft font crate and browser target compile for wasm with required fonts | WordCraft generated font inputs unchanged; DeckCraft release/browser protocol and optional Desktop/account IO PASS; broader gates OPEN |
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

The124-row chart does not close original-source reconciliation. The tracked-source
ledger now has 1,152 unresolved entries plus zero unqualified blob candidates, after
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

Phase41 assigns53 remaining legacy backend/configuration/documentation paths across seven existing components and parent deployment composition, preserving source/history and keeping all old entrypoints inactive. Current implementations and minimum dependencies are unchanged. See [backend ownership](BACKEND-OWNERSHIP.md).

Phase42 adds the independent local speech engine with34 verified static inputs (97,100,582 bytes), an offline graph builder and successful real CPU/WASM spoken-sample recognition. Inputs live at `artifacts/inputs/speech/`; no user audio is copied and Desktop voice is not enabled. See [speech engine](SPEECH-ENGINE.md).

Phase43 retains Terminal’s original PTY/startup glue, unchanged three-assertion reference test and historical notes. Real guest/current host/agent integration remain OPEN, and no optional guest dependency is enabled. See [terminal source](TERMINAL-SOURCE.md).

Phase44 assigns79 original Node reference-test files to18 application owners, porting only owned imports/fixture URLs with unchanged assertions. Original/current totals match:296 pass,3 captured ACAD failures retained, no skipped/cancelled cases. This is unit/reference scope, not new app hosting. See [app reference tests](APP-REFERENCE-TESTS.md).

Phase45 retains four legacy cross-component references and four shared browser-test helpers in the parent, restoring0 source import edges without copying component implementations. Three original Node reference tests pass in private snapshots; one old DOM/mirror reference remains unrun and all current interface ports remain explicit. See [component boundaries](COMPONENT-BOUNDARIES.md).

Phase46 retains 35 additional original cross-component browser test sources with histories, resolving 41 relative helper imports. Node syntax and exact byte/mode checks pass; no legacy browser driver was executed and no application integration status changed. See [browser helper consumers](BROWSER-HELPER-CONSUMERS.md).

Phase47 retains 145 original CAD case notes beside the archived cross-component test source, with original bytes/modes and selected histories. Historical PASS claims do not qualify the new build; old run outputs remain private and required test-input closure is still open. See [CAD case documentation](CAD-CASE-DOCUMENTATION.md).

Phase48 retains eight statically referenced original CAD review inputs, closing12 known read sites. Three original offline recorded-data reviewer tests pass in isolated snapshot and clean assembly; no native/browser/account-storage acceptance is claimed. Required fixture closure remains open for dynamic and Python paths. See [CAD reference inputs](CAD-REFERENCE-INPUTS.md).

Phase49 retains79 original JavaScript operator/browser-fixture sources with their selected histories, after language-specific syntax and bounded literal screening. No old operator or driver executed and no component functionality changed. See [legacy JavaScript operations](LEGACY-JS-OPERATIONS.md).

Phase50 retains350 original Python operator/check sources after bounded AST/literal and selected-history review.57 other current Python sources remain private for context review. No old operator/driver ran and no app functionality changed. See [context-reviewed Python source](LEGACY-PYTHON-CONTEXT.md).

Phase52 organizes33 original game design sources: seven rule documents in their individual game repositories and26 shared integration/experience references in the parent. Source bodies/histories retained; no gameplay or current rule/API compatibility claim. See [game design ownership](GAME-DESIGN-OWNERSHIP.md).

Phase53 organizes106 original guidance sources: seven lifecycle/file-operation notes in their app repositories and99 shared catalogs/workspace/cross-component references in the parent. All bodies/modes/histories retained; current behavior and historical instruction safety are separate gates. See [app guidance ownership](APP-GUIDANCE-OWNERSHIP.md).

Phase54 retains76 original system fixture/operator/guidance sources and selected histories, including27 HTML pages and disabled host-operation definitions. Four inline scripts parse, wrappers/Python/JSON pass source checks; no old operator/page/service ran. Two JSON literal-context cases and earlier57 Python holds remain private. See [system reference ownership](SYSTEM-REFERENCE-OWNERSHIP.md).

Phase55 retains283 original test/fixture sources with histories. Python/JS/HTML source checks and exact byte/mode/assembly checks pass; old routes/dependencies/fixture/generated compiler inputs remain explicit ports.13 more current Python literal cases remain private. No old test, fixture, app module, browser, Worker, compiler or guest ran. See [test orchestration source](TEST-ORCHESTRATION-SOURCE.md).

Phase56 assigns12 original Node test sources and one frozen vector fixture to actual owners. Eight locator-only ports report15 passing Node subtests; the original baseline has25 passes and one pre-existing stale negative-control failure, retained unchanged and unqualified. Browser relay and cross-component references remain inert. See [owned Node references](OWNED-NODE-REFERENCES.md).

Phase57 verifies127 historical records in existing private recovery without copying them into Git/web roots.109 possible source/design/input/unclear records remain unresolved. Current tracked-source counts come from [the generated summary](SOURCE-RECONCILIATION-SUMMARY.json). A fresh minimum frontend build reuses fully rehashed WordCraft from unchanged selected source; no new browser or full-suite acceptance follows. See [private evidence retention](PRIVATE-EVIDENCE-RETENTION.md).

Phase58 retains nine original native build/design/prototype-control references with histories and exact source bodies. One engine pin changes by reference files only;123 other pins and all active implementations are unchanged. Six copied upstream records remain unqualified despite byte matches, and no old build/control/publisher ran. See [native reference ownership](NATIVE-REFERENCE-OWNERSHIP.md).

Phase59 owns seven legacy mirror cache-unit tests in Storage with locator-only assertion-preserving ports and a new explicitly pinned dev-only dependency environment. Captured, current and clean reference outcomes match:3 pass,4 fail, command exit1; no failing case is omitted or assertion weakened. This is not account synchronization or an all-green Storage claim. See [mirror reference outcomes](STORAGE-MIRROR-REFERENCES.md).

The [existing snapshot-reference review](OWNED-SNAPSHOT-REFERENCES.md) qualifies31 already-owned references and1 private empty output channel without copying raw material or changing component pins. Unresolved supporting-source dispositions remain1,152; byte-candidate guesses are now zero.

The [private terminal-reference review](PRIVATE-TERMINAL-REFERENCES.md) resolves62 captured output records without copying raw data or changing runtime/component pins. Seventy-six weaker terminal-like cases from that batch remain pending; current unresolved supporting records total1,152.

The [isolated-host test extraction](ISOLATED-HOST-TEST-SOURCE.md) preserves41 additional unchanged sources and52 relevant commits. All51 historical Python blobs were reviewed and all41 current files restored independently. Old namespace/service/operator drivers remain inert and unexecuted; no component pin or runtime change.

The [isolated-host deployment source](ISOLATED-HOST-OPERATOR-SOURCE.md) preserves26 additional unchanged helpers and47 relevant commits. All28 historical Python blobs were reviewed and all26 current files restored independently. Privileged host operators remain inactive/unexecuted; configuration/input closure and public-interface ports remain OPEN. No component pin or runtime change.

The [host-context and Microduck ownership review](HOST-CONTEXT-AND-MICRODUCK-SOURCE.md) preserves2 exactly reviewed template/probe sources under parent deployment and1 app-specific hosting policy in Microduck. All3 remain inactive; only Microduck's source/documentation pin changes. Existing missing-fixture failures and functional gates remain OPEN.

The [historical host reference inputs](HOST-REFERENCE-INPUTS.md) preserve24 more records:17 review documents,6 config/pin/manifests and1 inactive browser driver. All27 installer and31 bootstrap source hashes resolve to matching independently owned bytes. This is source-input preservation, not a runnable historical installer or current acceptance. All124 pins unchanged.

The [historical OPFS release source](OPFS-RELEASE-SOURCE.md) preserves15 additional candidate builder/test/model/document records and9 relevant commits. All25 historical blobs were reviewed; all15 files restored independently. Two existing journal/native-fixture owners remain distinct. One pre-existing whitespace warning is retained without changing source bytes; all124 pins/runtime unchanged.

The [private CAD data catalogue](PRIVATE-CAD-DATA-REFERENCES.md) assigns626 frozen records across38 owned historical test cases to private reference preservation. Inputs, native snapshots, containers, records and text channels remain distinct, outside Git/web roots. Twelve representative restores pass; per-file producer/use/privacy/geometry and current acceptance remain OPEN. The additional13 documentation-context records are catalogued after source-pin/inventory review. All124 pins unchanged.

The [remaining CAD case context](DEFERRED-CAD-CONTEXT.md) assigns13 further private references without inventing drivers. Nine historical source pins match; eight current files match and the different cad-agent example retains its exact old version in ACAD history. The303-file inventory is internally consistent, but runtime payload presence/acceptance remains unverified. All13 records restored privately; all124 pins/runtime unchanged.
