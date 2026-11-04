# Silo planning matrix

Planning estimates dated 2026-11-03, based on the saved 2026-11-02
checkpoint and existing app review notes. These percentages are rounded scope
judgements, not audited measurements or a project completion score. Done means
supported by the recorded scoped evidence; partial means implemented/research
work with acceptance still open. The remainder is missing or unverified.
The three shares are mutually exclusive and total 100%; do not add done+partial
and call it complete. Do not average rows into an overall percentage.

Times are rough remaining focused engineering effort for each documented
bounded finish line: one day = 8 hours. Finish excludes the separate prove
column; prove includes additional testing, independent review and fixing
defects found there. Dependencies, build/device access and waiting are excluded.
Expect estimates to move after a bounded audit. They are not agent runtime or
calendar delivery promises. Future solver/mesher rows cover a first qualified
workflow, not every physics formulation. The qualification row covers the
current baseline, not all future apps; avoid double-counting it with per-app QA.

Difficulty 1–5 also expresses expected first-implementation rework risk:
1 low, 2 moderate, 3 high, 4 very high, 5 research-heavy/very high. These are
judgement bands, not statistically measured failure probabilities. Proof means
passing the agreed acceptance, not mathematical proof or hardware safety.
Game effort assumes final assets and required devices become available;
external artwork, hardware acquisition and content licensing are not included.

Sorted by midpoint of remaining implementation effort, then proof effort.
This is a shortest-job list, not the recommended execution order. A dependent
enclosure or physics task may be short itself but cannot start before its inputs.
Development remains paused. This report does not perform a fresh live audit.



| # | Silo | Working | Partial | Missing / not qualified | Done | Partial | Finish | Prove afterward | Difficulty / rework |
|---:|---|---|---|---|---:|---:|---:|---:|---|
| 1 | **Help** (APP-help) | Static help checked | Manual and feature accuracy | Complete concise supported-feature guide | 80% | 15% | 0.5–1 d | 0.25–0.5 d | 1/5 · Low |
| 2 | **Calculator** (APP-calculator) | Calculation/file workflow and pending-close guard | History and account/lifecycle edges | Complete physical-device and error acceptance | 70% | 20% | 1–3 d | 0.5–1.5 d | 2/5 · Moderate |
| 3 | **PDF Viewer** (APP-pdf-viewer) | Open/navigation/password primary workflow | Large files, search and restore failures | Device/worker/resource qualification; OCR excluded | 65% | 25% | 2–5 d | 1–3 d | 2/5 · Moderate |
| 4 | **Falling Blocks** (GAME-falling-blocks) | Rules, save/lifecycle, emulated touch; authored Rive art | Procedural presentation; selected interaction/account cases | Physical touch/audio and full play acceptance | 65% | 25% | 2–5 d | 2–4 d | 2/5 · Moderate |
| 5 | **Solitaire** (GAME-solitaire) | One draw-one victory and account reopen | Procedural presentation; selected interaction/account cases | Draw-three and broader deals/touch | 65% | 25% | 2–6 d | 2–5 d | 3/5 · High |
| 6 | **Excalidraw** (APP-excalidraw) | Files workflow and stale chooser guard | Complex SVG/images/provider audit | Resource and device/lifecycle qualification | 65% | 25% | 3–7 d | 2–4 d | 3/5 · High |
| 7 | **Text** (APP-text) | CodeMirror and scoped signed file workflow | Large files, encodings and touch | Full conflict/lifecycle/device acceptance | 65% | 25% | 3–7 d | 2–4 d | 3/5 · High |
| 8 | **Chess Study** (GAME-chess-study) | AI and saved-game workflow | Procedural presentation; selected interaction/account cases | Rules/AI limits, full playthroughs and physical touch | 60% | 30% | 3–7 d | 2–5 d | 3/5 · High |
| 9 | **Memory Garden** (GAME-memory-garden) | Full keyboard game and account reopen | Procedural presentation; selected interaction/account cases | Art, assistive technology and physical touch | 60% | 25% | 3–7 d | 2–5 d | 2/5 · Moderate |
| 10 | **Reproducibility and student guidance** (O03) | Remote source/notes, handoff and scoped build recipes | App inventory, deferred features and prerequisite documentation | Clean other-machine checkout/build and complete supported student guide | 55% | 30% | 3–7 d | 2–5 d | 3/5 · High |
| 11 | **SVG Editor** (APP-svg-editor) | Basic open/edit/export workflow | Complex SVG/CSS and external-resource behavior | Supported-format matrix and physical touch | 55% | 30% | 3–8 d | 2–4 d | 3/5 · High |
| 12 | **G-code Preview** (APP-g-code-preview) | Primary preview; session/visibility guards | Large-file and interpretation boundaries | Physical-device and supported-code qualification | 65% | 25% | 3–8 d | 2–5 d | 3/5 · High |
| 13 | **Gravity Pinball** (GAME-gravity-pinball) | Save/reopen and input focus | Procedural presentation; selected interaction/account cases | Complete play acceptance, art and physical touch | 55% | 25% | 3–8 d | 3–6 d | 3/5 · High |
| 14 | **diagrams.net** (APP-diagrams.net) | Primary file workflow and restore retry | Provider/export/version-update coverage | Qualified adapter and physical touch | 60% | 30% | 4–9 d | 2–5 d | 3/5 · High |
| 15 | **Account identity and permissions** (S01) | Signed registration/login; selected account-denial tests | Expiry/revocation and concurrent-session coverage | Complete recovery, classroom sign-ins and transition qualification | 60% | 25% | 4–9 d | 3–6 d | 3/5 · High |
| 16 | **Audio Editor** (APP-audio-editor) | Primary edit/file workflow; channel rejection | Unusual codecs, multiwindow audio | Physical audio and complete export/lifecycle coverage | 55% | 30% | 4–10 d | 3–6 d | 3/5 · High |
| 17 | **Snake Garden** (GAME-snake-garden) | Preview rules and account workflow | Procedural presentation; selected interaction/account cases | Final artwork and complete touch/play acceptance | 50% | 30% | 4–10 d | 3–6 d | 3/5 · High |
| 18 | **Expression Puppet** (GAME-expression-puppet) | Poses/challenge and account reopen | Procedural presentation; selected interaction/account cases | Art, assistive technology and physical touch | 50% | 30% | 4–10 d | 3–7 d | 3/5 · High |
| 19 | **Kinetic Relay** (GAME-kinetic-relay) | Step/save/deleted-file protection | Procedural presentation; selected interaction/account cases | All puzzles, art and physical touch | 50% | 30% | 4–10 d | 3–7 d | 3/5 · High |
| 20 | **Owl Companion** (GAME-owl-companion) | Interactive/account preview | Procedural presentation; selected interaction/account cases | Authored art and physical-device acceptance | 45% | 35% | 4–10 d | 3–7 d | 3/5 · High |
| 21 | **Reactive Control Desk** (GAME-reactive-control-desk) | Pending save and account reopen | Procedural presentation; selected interaction/account cases | All orders, art and physical touch | 50% | 30% | 4–10 d | 3–7 d | 3/5 · High |
| 22 | **Sling Targets** (GAME-sling-targets) | Aim interruption and dirty settings | Procedural presentation; selected interaction/account cases | All arrangements, art and physical touch | 50% | 30% | 4–10 d | 3–7 d | 3/5 · High |
| 23 | **Stack & Balance** (GAME-stack-&-balance) | Touch cancellation and saves | Procedural presentation; selected interaction/account cases | Complete challenge set, art and physical devices | 50% | 30% | 4–10 d | 3–7 d | 3/5 · High |
| 24 | **Story Cards** (GAME-story-cards) | Account workflow and isolation | Procedural presentation; selected interaction/account cases | Complete story, art and physical touch | 50% | 30% | 4–10 d | 3–7 d | 3/5 · High |
| 25 | **Clockwork Room** (GAME-clockwork-room) | Four mechanisms and save recovery | Procedural presentation; selected interaction/account cases | Full content, art and physical-device review | 55% | 30% | 4–10 d | 4–8 d | 3/5 · High |
| 26 | **Pocket Golf** (GAME-pocket-golf) | In-flight save and hole-change guards | Procedural presentation; selected interaction/account cases | All holes, art and physical touch | 50% | 30% | 4–10 d | 4–8 d | 3/5 · High |
| 27 | **Desktop shell and windows** (S05) | Windows, workspaces, taskbar and responsive layouts | Device polish, restoration and consistent themed failures | Full physical-device, focus and state-restoration acceptance | 65% | 25% | 5–12 d | 3–6 d | 3/5 · High |
| 28 | **Music Player** (NEXT-music-player) | Audio playback libraries identified | Inventory and integration design; user app not qualified | Actual local-file user workflow and lifecycle/device qualification | 0% | 20% | 5–12 d | 3–6 d | 3/5 · High |
| 29 | **Photo Gallery** (NEXT-photo-gallery) | Selected viewer/library candidates | Inventory and integration design; user app not qualified | Actual local-file user workflow and lifecycle/device qualification | 0% | 20% | 5–12 d | 3–6 d | 3/5 · High |
| 30 | **Digital Logic** (APP-digital-logic) | Combinational examples and truth-table files | Component coverage and UI polish | Qualified supported logic workflow; timing not implied | 55% | 25% | 5–12 d | 3–7 d | 3/5 · High |
| 31 | **Doc** (APP-doc) | Report editing, file workflow and PDF output | Complex scripts, clipboard and layout | Qualified Unicode, layout and conflict/lifecycle behavior | 55% | 30% | 5–12 d | 3–7 d | 3/5 · High |
| 32 | **Image Editor** (APP-image-editor) | Primary edit/file workflow; metadata warnings | Format coverage and low-copy saves | Supported-format, memory and device qualification | 55% | 30% | 5–12 d | 3–7 d | 3/5 · High |
| 33 | **Terminal** (APP-terminal) | xterm and independent-shell primary workflow | Interactive programs, touch and session teardown | Qualified supported terminal/device lifecycle; networking policy | 65% | 20% | 5–12 d | 3–7 d | 3/5 · High |
| 34 | **Crystal Defense** (GAME-crystal-defense) | Pause/deleted-save checks | Procedural presentation; selected interaction/account cases | Eight-wave playthrough, art and physical touch | 45% | 35% | 5–12 d | 4–8 d | 3/5 · High |
| 35 | **Drone Circuit** (GAME-drone-circuit) | Focus/input and file workflow | Procedural presentation; selected interaction/account cases | Full course, art and physical multitouch | 45% | 35% | 5–12 d | 4–8 d | 3/5 · High |
| 36 | **Garden Defense** (GAME-garden-defense) | Map/pending-save interactions | Procedural presentation; selected interaction/account cases | Full waves, artwork and physical touch | 45% | 35% | 5–12 d | 4–8 d | 3/5 · High |
| 37 | **Lantern Leap** (GAME-lantern-leap) | Overlapping input/focus/save guards | Procedural presentation; selected interaction/account cases | All rooms, artwork and physical touch | 45% | 35% | 5–12 d | 4–8 d | 3/5 · High |
| 38 | **Marble Works** (GAME-marble-works) | Pause/save/reopen | Procedural presentation; selected interaction/account cases | All eight puzzles, art and physical touch | 50% | 30% | 5–12 d | 4–8 d | 3/5 · High |
| 39 | **Mesh:Tool** (APP-mesh:tool) | Basic mesh/file workflow | Undo, geometry defects and memory | Supported-edit and export correctness qualification | 50% | 30% | 5–12 d | 4–8 d | 4/5 · Very high |
| 40 | **Pocket Rally** (GAME-pocket-rally) | Input/focus/account save | Procedural presentation; selected interaction/account cases | All races, artwork and physical multitouch | 45% | 35% | 5–12 d | 4–8 d | 3/5 · High |
| 41 | **Sky Courier** (GAME-sky-courier) | Steering/firing and saved preview | Procedural presentation; selected interaction/account cases | Full campaign, artwork and physical touch | 45% | 35% | 5–12 d | 4–8 d | 3/5 · High |
| 42 | **Tabletop Bot Arena** (GAME-tabletop-bot-arena) | Independent inputs and file guards | Procedural presentation; selected interaction/account cases | Full cup, art and physical devices | 45% | 35% | 5–12 d | 4–8 d | 3/5 · High |
| 43 | **Target Garden** (GAME-target-garden) | Pointer cancellation and independent inputs | Procedural presentation; selected interaction/account cases | Full rounds, art and devices | 45% | 35% | 5–12 d | 4–8 d | 3/5 · High |
| 44 | **Rhythm Garden** (GAME-rhythm-garden) | Input/save and accessibility activation | Procedural presentation; selected interaction/account cases | Full medal runs, art and physical audio timing | 45% | 35% | 5–12 d | 4–9 d | 4/5 · Very high |
| 45 | **Clockwork Quest** (GAME-clockwork-quest) | Full quest/account reopen; mocked XR lifecycle | Procedural presentation; selected interaction/account cases | Real headset, art and physical touch | 55% | 30% | 5–14 d | 5–12 d | 4/5 · Very high |
| 46 | **Files** (APP-files) | Primary file operations; account and temporary Linux home | Remote-change feedback, folder operations and interruption | Complete sync/conflict-safe file and folder workflow | 60% | 30% | 6–14 d | 4–8 d | 4/5 · Very high |
| 47 | **Stitch Converter** (APP-stitch-converter) | Supported conversion/file workflow | SVG loss cases and machine format fidelity | Independent format checks; physical sewing optional external test | 50% | 30% | 6–15 d | 5–10 d | 4/5 · Very high |
| 48 | **Hosting, release and recovery** (O01) | Separate beta; gated guarded rollout and recovery tests | Reusable promotion/update path and boot recovery | Qualified current main promotion and repeatable operator workflow | 60% | 25% | 7–15 d | 5–10 d | 4/5 · Very high |
| 49 | **Server file store** (S03) | Beta signed writes, permissions, version checks and process restart | Folder operations, quotas and concurrent disk accounting | Complete operation recovery and realistic capacity proof | 60% | 25% | 7–15 d | 5–10 d | 4/5 · Very high |
| 50 | **Replicad** (APP-replicad) | Starter script/models and geometry exports | Regeneration/UI/examples | Useful qualified script-CAD workflow; not general CAD | 45% | 35% | 7–16 d | 4–9 d | 4/5 · Very high |
| 51 | **Video Player** (NEXT-video-player) | Selected playback/runtime candidates | Inventory and integration design; user app not qualified | Actual local-file user workflow and lifecycle/device qualification | 0% | 20% | 7–18 d | 4–8 d | 3/5 · High |
| 52 | **Circuit Simulator** (APP-circuit-simulator) | Primary circuit/file workflow | Solver/probe semantics and reference cases | Qualified supported analyses; hardware validation excluded | 45% | 35% | 7–18 d | 5–10 d | 4/5 · Very high |
| 53 | **Linux guest runtime** (S08) | Temporary v86 boot and guest Python baseline | Kernel/tool assets and interactive executable coverage | Qualified supported tools, temporary files, reset and network policy | 45% | 30% | 7–18 d | 5–10 d | 4/5 · Very high |
| 54 | **Physics Playground** (GAME-physics-playground) | Interactive preview and account workflow | Procedural presentation; selected interaction/account cases | Complete challenges, art and separately tested XR | 40% | 35% | 7–18 d | 5–12 d | 4/5 · Very high |
| 55 | **Orbital Courier** (GAME-orbital-courier) | Controlled mission checkpoints and saves | Procedural presentation; selected interaction/account cases | Uninterrupted mission, art, touch and XR | 40% | 40% | 7–18 d | 6–12 d | 4/5 · Very high |
| 56 | **News Reader** (NEXT-news-reader) | Readability/feed candidates identified | Inventory and integration design; user app not qualified | Actual local-file user workflow and lifecycle/device qualification | 0% | 20% | 8–18 d | 4–9 d | 3/5 · High |
| 57 | **Spreadsheet** (APP-spreadsheet) | CSV/TSV workflow; long-cell preservation | Large files/formulas/memory | Measured higher limits and correct supported round trips | 50% | 35% | 8–18 d | 5–10 d | 4/5 · Very high |
| 58 | **Data Explorer** (APP-data-explorer) | Import/query/pivot/chart primary workflow | Precision and large-data resource use | Exact identifiers and reproducible resource-limited workflow | 50% | 35% | 8–18 d | 5–12 d | 4/5 · Very high |
| 59 | **Kiri:Moto** (APP-kiri:moto) | Primary workspace/file workflow | Printer/process/output profiles | Independent supported-output and device checks; no real print gate | 50% | 35% | 8–18 d | 5–12 d | 4/5 · Very high |
| 60 | **E-book Reader** (NEXT-e-book-reader) | Reader/runtime candidates identified | Inventory and integration design; user app not qualified | Actual local-file user workflow and lifecycle/device qualification | 0% | 20% | 8–20 d | 5–10 d | 4/5 · Very high |
| 61 | **Browser Python Notebook** (S07) | JupyterLite/Pyodide primary workflow and local packages | Jupytext/widgets/RAM models and phone layout | Saved-file stale-writer fix; qualified formats and lifecycle | 45% | 35% | 10–22 d | 6–12 d | 4/5 · Very high |
| 62 | **Shared app host, lifecycle and commands** (S06) | Mount/dispose and selected stale-operation guards | Account/logout cancellation and shared command contracts | Universal session safety and authorized typed operations | 40% | 40% | 10–22 d | 6–12 d | 4/5 · Very high |
| 63 | **Synchronization and transfer protocol** (S04) | Beta changed-chunk transfers, conflicts and lost-reply recovery | Two-device convergence, pacing, formats and bounded resources | Complete end-to-end OPFS adoption and load qualification | 50% | 35% | 10–22 d | 7–14 d | 4/5 · Very high |
| 64 | **Embroidery Studio** (APP-embroidery-studio) | Primary artwork/project workflow | Digitizing/thread/format/provider coverage | Qualified native/export and device workflow | 45% | 35% | 10–24 d | 7–15 d | 4/5 · Very high |
| 65 | **Fraction Farm** (LEARN-fraction-farm) | Pure rules model/tests; menu disabled | Rule core; no released game UI | Usable UI, assets, file adapter and playthrough/device acceptance | 10% | 25% | 10–25 d | 6–12 d | 4/5 · Very high |
| 66 | **Maps** (NEXT-maps) | Map library capability; map data/style not bundled | Inventory and integration design; user app not qualified | Actual local-file user workflow and lifecycle/device qualification | 0% | 20% | 10–25 d | 6–12 d | 4/5 · Very high |
| 67 | **Market Math** (LEARN-market-math) | Pure rules model/tests; menu disabled | Rule core; no released game UI | Usable UI, assets, file adapter and playthrough/device acceptance | 10% | 25% | 10–25 d | 6–12 d | 4/5 · Very high |
| 68 | **Math Path** (LEARN-math-path) | Pure rules model/tests; menu disabled | Rule core; no released game UI | Usable UI, assets, file adapter and playthrough/device acceptance | 10% | 25% | 10–25 d | 6–12 d | 4/5 · Very high |
| 69 | **Pocket Conquest** (LEARN-pocket-conquest) | Pure rules model/tests; menu disabled | Rule core; no released game UI | Usable UI, assets, file adapter and playthrough/device acceptance | 10% | 25% | 10–25 d | 6–12 d | 4/5 · Very high |
| 70 | **Rule Detective** (LEARN-rule-detective) | Pure rules model/tests; menu disabled | Rule core; no released game UI | Usable UI, assets, file adapter and playthrough/device acceptance | 10% | 25% | 10–25 d | 6–12 d | 4/5 · Very high |
| 71 | **Tile Islands** (LEARN-tile-islands) | Pure rules model/tests; menu disabled | Rule core; no released game UI | Usable UI, assets, file adapter and playthrough/device acceptance | 10% | 25% | 10–25 d | 6–12 d | 4/5 · Very high |
| 72 | **Word Weaver** (LEARN-word-weaver) | Pure rules model/tests; menu disabled | Rule core; no released game UI | Usable UI, assets, file adapter and playthrough/device acceptance | 10% | 25% | 10–25 d | 6–12 d | 4/5 · Very high |
| 73 | **Microduck** (APP-microduck) | Live two-account project workflow | Runner, physical touch and model coverage | Qualified controls/recovery with honest simulation limits | 50% | 35% | 10–25 d | 8–18 d | 4/5 · Very high |
| 74 | **Enclosure acceptance project** (J07) | Related box/metadata export experiments | Body/lid/inset fixtures and edit/regeneration path | Complete editable enclosure to independently verified 3MF | 10% | 30% | 12–25 d | 8–15 d | 4/5 · Very high |
| 75 | **Local durable browser files / OPFS** (S02) | Research verified generations, CAS, cleanup, upload/download crash cases | Signed sync; quota, memory and migrations | Desktop adoption; complete memory/eviction/recovery qualification | 35% | 45% | 12–25 d | 8–16 d | 4/5 · Very high |
| 76 | **Arduino Simulator** (APP-arduino-simulator) | Real AVR firmware and GPIO examples | Compiler options/peripheral models | Qualified source-build-run-save loop for supported board | 45% | 35% | 12–28 d | 7–15 d | 4/5 · Very high |
| 77 | **CAD desktop integration** (J06) | Scoped signed-account modeling/save/reopen and viewport tests | Full runtime packaging, commands and lifecycle | Qualified real CAD app on phone/1080p/4K | 40% | 35% | 12–28 d | 8–16 d | 4/5 · Very high |
| 78 | **Native manufacturing document** (J04) | Research material/region binding and assignment review | Authored grouping, transforms and regeneration references | Durable general assignments through edits/save/reopen | 25% | 40% | 12–28 d | 8–16 d | 4/5 · Very high |
| 79 | **Shared runtime library portfolio** (S10) | Several pinned/lazy-loaded library entries | Consumer coverage, notices and independent disposal | Complete capability inventory and one real tested consumer per capability | 40% | 40% | 12–30 d | 7–15 d | 3/5 · High |
| 80 | **Independent baseline qualification** (O02) | Many scoped browser/account/fault tests | Physical devices, capacity and sustained multi-device behavior | Complete baseline evidence at specified resource/device limits | 35% | 40% | 15–35 d | 8–18 d | 4/5 · Very high |
| 81 | **Linux Notebook** (APP-linux-notebook) | Guest Python/tools foundation; launcher disabled | Kernel bridge and browser-to-guest notebook transport | Working distinct kernel with subprocess/package and recovery proof | 5% | 25% | 15–35 d | 8–18 d | 5/5 · Research / very high |
| 82 | **JSketcher upstream feature integration** (J01) | Carried-forward fixes and scoped feature regressions | Spline/history/DXF/camera integration and combined behavior | Full feature-by-feature integrated validation | 40% | 40% | 15–35 d | 10–20 d | 4/5 · Very high |
| 83 | **Pico Simulator** (APP-pico-simulator) | Supported firmware/serial and file workflow | Flash/peripheral/reset behavior | Qualified real-firmware project lifecycle and explicit limits | 35% | 40% | 15–35 d | 10–20 d | 5/5 · Research / very high |
| 84 | **Core 3MF exporter and validator** (J05) | Two disjoint assigned boxes exported and independently validated | General tessellation and overlap/contact validation | Supported curved/cavity/material-region export acceptance | 30% | 40% | 18–40 d | 12–25 d | 5/5 · Research / very high |
| 85 | **Electronics Design** (APP-electronics-design) | Primary project workflow | Part coverage and cross-view consistency | Useful synchronized breadboard/schematic/PCB and exports | 35% | 40% | 18–40 d | 12–25 d | 5/5 · Research / very high |
| 86 | **Physical-system document and materials** (P01) | Written regions/material/interface/study design | Native manufacturing identities as a foundation | Implemented revisioned studies and evidence-backed material semantics | 5% | 25% | 20–45 d | 10–20 d | 4/5 · Very high |
| 87 | **Circuit Lab** (APP-circuit-lab) | Scoped solver/close-guard research | Runtime/model source and packaging | Distributed usable circuit study workflow | 20% | 40% | 20–45 d | 12–25 d | 5/5 · Research / very high |
| 88 | **PCB Design** (APP-pcb-design) | Research design/browser prototype | Dependency/build and fabrication workflow | Usable design-to-verified-fabrication-output baseline | 10% | 30% | 25–55 d | 15–30 d | 5/5 · Research / very high |
| 89 | **Geometry engines and provenance** (J03) | Focused OCC/native primitive and Boolean comparisons | Source/build provenance, scales, topology and tessellation | Qualified capability matrix and supported model-derived geometry | 35% | 35% | 25–60 d | 15–35 d | 5/5 · Research / very high |
| 90 | **Meshing** (P02) | Selected mesher candidates and feasibility notes | Runtime and tagged-domain feasibility | Runnable qualified mesher with stable region/boundary attribution | 5% | 15% | 25–60 d | 15–35 d | 5/5 · Research / very high |
| 91 | **Browser (experimental)** (APP-browser-(experimental)) | Experimental render/relay source | Compatibility, profiles, policy and file integration | Supported-site baseline; arbitrary website parity excluded | 20% | 35% | 30–75 d | 15–35 d | 5/5 · Research / very high |
| 92 | **JSketcher constraints and parameters** (J02) | Existing mechanical sketch/feature baseline | Midpoint, atomic constraint admission, dimensional relations and units | Dependable mechanical profile, configurations and rejected-edit recovery | 20% | 45% | 35–80 d | 20–45 d | 5/5 · Research / very high |
| 93 | **First qualified forward solver** (P03) | Existing solver projects identified; no integrated study claimed | Formulation/runtime selection | One reproducible benchmarked forward study and result provenance | 0% | 15% | 35–80 d | 25–60 d | 5/5 · Research / very high |
| 94 | **Advanced curves** (J08) | Existing curve/spline baseline | Incidence/tangency and authored contact behavior | Qualified ellipse/path/G2/projection curved-handle workflow | 10% | 30% | 40–100 d | 20–50 d | 5/5 · Research / very high |
| 95 | **Magnetic design search** (P04) | Authored acceptance problem | Fixture/objective/material catalogue design | Bounded search, manufactured-model regeneration and independent reanalysis | 0% | 10% | 40–100 d | 30–70 d | 5/5 · Research / very high |
| 96 | **Assemblies and mechanisms** (J09) | Small assembly constraint registry | Pose/reference model and incomplete persistence | Durable joints, limits, couplings and linkage acceptance | 5% | 20% | 60–150 d | 30–70 d | 5/5 · Research / very high |

Dependencies and evidence references are in the JSON/CSV and the expanded interactive report.

Scope: [separate silo checklists](../WEBOS-SILOED-WORK.md). Status: [handoff](../HANDOFF-STORAGE-BETA-2026-11-02.md).

Source reports: `docs/APP_STATUS.md`, `docs/GAME_PREVIEW_REVIEW.md`, `docs/WEBOS-WORK-QUEUES.md`, and the CAD research notes.
