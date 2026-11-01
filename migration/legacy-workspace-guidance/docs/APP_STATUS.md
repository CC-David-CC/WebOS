# App review status

Updated 2026-11-01. This is a compact index of the current review, not a claim
that every feature has been tested. “Workflow checked” means the listed primary
workflow has desktop and emulated-phone evidence; most also have live account
checks. Physical touch is not established by emulation. The detailed test scope,
known failures and release history are in [the review tracker](APP_UNIFICATION_PROGRESS.md)
and [handoff](../SIMPLIFIED_HANDOFF.md). The [student guide](APP_USER_GUIDE.md)
explains how to start. Third-party features are a [partial inventory](DEFERRED_APP_FEATURES.md).

| App | Status | Main remaining boundary |
| --- | --- | --- |
| Files | Workflow checked | Folder moves unavailable; 100-user capacity unqualified. |
| Terminal | Workflow checked | Guest files are temporary; more interactive programs need testing. |
| Text | Workflow checked | Large files and further editing modes need review. |
| Help | Static information checked | Not a full manual. |
| Calculator | Workflow checked | Floating-point results; notes restore the recorded result but not previous Ans history. |
| Browser | Experimental | Lowest priority; temporary profile and no audio. |
| Document Editor | Workflow checked | Not a Word editor; more complex reports need review. |
| PDF Viewer | Workflow checked | Read-only; no OCR for image-only scans. |
| Spreadsheet | Workflow checked | Advanced Excel compatibility is limited; mathematical exponent precedence differs from Excel. |
| Data Explorer | Workflow checked | Large datasets can exceed device memory; injected restore failures now pass without the previously observed worker error, but other failure and resource-pressure cases remain unverified. |
| Python Notebook | Workflow checked | Untrusted notebooks are not isolated; other kernel or resource-pressure failures remain possible. |
| Image Editor | Workflow checked | Animated image editing unsupported; annotation images use a temporary gallery; embedded tools need further audit. |
| Audio Editor | Workflow checked | Other AudioMass tools may omit desktop beat/snap metadata; long names may shorten; physical microphone behavior remains unverified. |
| diagrams.net | Workflow checked | SVG/PNG export tested; other export types and provider entry points need review. |
| Excalidraw | Workflow checked | File and folder choices are serialized; reusable library features and provider audit remain partial. |
| SVG Editor | Workflow checked | Complex SVG and physical touch remain unverified. |
| Replicad | Workflow checked | Limited model generator, not general CAD; validate output. |
| Kiri:Moto | Workflow checked | Printer profiles, output and physical touch need independent verification. |
| Mesh:Tool | Workflow checked | Undo history is not saved; manufacturing correctness unverified. |
| G-code Preview | Workflow checked | Supports a subset, assumes an initial state, and does not validate machine safety. |
| Arduino Simulator | Workflow checked | Not electrical simulation; browser compilation unavailable; reload does not preserve serial output. |
| Pico Simulator | Workflow checked | Firmware/peripheral support partial; unsaved flash cannot be recovered after a crash. |
| Digital Logic | Workflow checked | Feed-forward combinational JSON circuits only; no timing or hardware validation. |
| Circuit Simulator | Workflow checked | Divider simulation, upload, sync and recovery checked; simulation is not hardware validation. |
| Electronics Design | Workflow checked | Component coverage, physical touch and board validation remain open. |
| Embroidery Studio | Workflow checked | Pre-release; physical sewing, machine formats and provider audit remain open. |
| Stitch Converter | Workflow checked | SVG support and machine compatibility remain partial; test-sew output. |
| Falling Blocks | Preview | Emulated multitouch tested; physical phone and audible speakers unverified. |
| Owl Companion | Preview | Authored Rive artwork and physical-device testing remain open. |
| Snake Garden | Preview | Authored Rive artwork and physical-device testing remain open. |
| Physics Playground | Preview | XR and complete challenge acceptance remain open. |
| Clockwork Room | Preview | Four mechanisms and save recovery checked; physical-device review and final artwork remain. |
| Chess Study | Preview | Actual AI, save and reopen checked; AI strength and physical touch unverified. |
| Solitaire | Preview | Rules, seeded invariants and near-win recovery checked; full deal-to-win and physical touch remain. |
| Sky Courier | Preview | Steering and firing checks passed; full campaign and physical touch unverified. |
| Marble Works | Preview | Pause/resume, account sync and reopen checked; all eight puzzles, physical touch and final artwork remain. |
| Stack & Balance | Preview | Further interaction and physical-device review; final artwork pending. |
| Crystal Defense | Preview | Further interaction and physical-device review; final artwork pending. |
| Drone Circuit | Preview | Further interaction and physical-device review; final artwork pending. |
| Reactive Control Desk | Preview | Further interaction and physical-device review; final artwork pending. |
| Story Cards | Preview | Account sync and isolation checked; complete story and physical touch remain. |
| Expression Puppet | Preview | Further interaction and physical-device review; final artwork pending. |
| Rhythm Garden | Preview | Further interaction and physical-device review; final artwork pending. |
| Lantern Leap | Preview | Further interaction and physical-device review; final artwork pending. |
| Garden Defense | Preview | Further interaction and physical-device review; final artwork pending. |
| Pocket Rally | Preview | Focus/input, account save and isolation checked; full races and physical multitouch remain. |
| Sling Targets | Preview | Further interaction and physical-device review; final artwork pending. |
| Gravity Pinball | Preview | Account save/reopen and input-focus checks passed; physical touch remains. |
| Kinetic Relay | Preview | Further interaction and physical-device review; final artwork pending. |
| Tabletop Bot Arena | Preview | Account match save/reopen and input-focus checks passed; physical touch remains. |
| Pocket Golf | Preview | Further interaction and physical-device review; final artwork pending. |
| Target Garden | Preview | Further interaction and physical-device review; final artwork pending. |
| Orbital Courier | Preview | Further interaction and physical-device review; final artwork pending. |
| Clockwork Quest | Preview | Further interaction and physical-device review; final artwork pending. |
| Memory Garden | Preview | Further interaction and physical-device review; final artwork pending. |
| Circuit Lab | Research candidate, not deployed | ngspice source/relink distribution review and model licensing remain open. |
| PCB Design | Research prototype, not deployed | Browser packaging, dependency notices and usable design workflow remain open. |
| Personal template | App-author example | Not an end-user app. |

The 24 additional game previews passed individual builds and available unit tests; this does not establish a complete interactive review of each game. Most final artwork/audio remains pending; see [game asset gaps](GAME_ASSET_GAPS.md).

Shared tools in the menu are capabilities, not standalone user apps; their
consumer coverage is tracked in the detailed review. None of these rows closes
the broader requirement to audit all optional integrations, lifecycle paths,
formats, accessibility, physical devices and account isolation.
