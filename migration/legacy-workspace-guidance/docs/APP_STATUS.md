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
| Files | Workflow checked | Copies use an atomic local snapshot; unseen remote edits may arrive later. Folder moves unavailable; 100-user capacity unqualified. |
| Terminal | Workflow checked | Guest files are temporary; more interactive programs need testing. |
| Text | Workflow checked | File actions are serialized during confirmation and selection; the 128 MiB boundary remains unverified. |
| Help | Static information checked | Not a full manual. |
| Calculator | Workflow checked | New notes retain the Ans input for recalculation; older notes lack it and show a warning. Earlier Ans history is not retained. |
| Browser | Experimental | Lowest priority; temporary profile and no audio. |
| Document Editor | Workflow checked | Read failures offer retry and `/Untitled.doc` uses a separate scratch name; clipboard and animated images remain incompletely checked. |
| PDF Viewer | Workflow checked | Temporary restore failures retain the reference for Reload; confirmed invalid files clear it. Read-only, with no OCR for scans. |
| Spreadsheet | Workflow checked | Temporary restore failures offer guarded retry; native format and CSV are primary. Physical dragging remains unverified. |
| Data Explorer | Workflow checked | Temporary restore failures offer guarded retry; large datasets can exceed device memory and resource-pressure cases remain unverified. |
| Python Notebook | Workflow checked | Recovery, concurrent starts and early close passed limited reruns; earlier intermittent kernel errors remain unexplained. Untrusted notebooks are not isolated. |
| Image Editor | Workflow checked | Temporary restore failures offer guarded retry; animated images are unsupported and embedded tools need further audit. |
| Audio Editor | Workflow checked | Other AudioMass tools may omit desktop beat/snap metadata; long names may shorten; physical microphone behavior remains unverified. |
| diagrams.net | Workflow checked | Temporary restore failures offer guarded retry; the adapter must be requalified when diagrams.net changes. Other exports and provider entry points need review. |
| Excalidraw | Workflow checked | Temporary restore failures offer guarded retry; full imported image decoding and provider audit remain partial. |
| SVG Editor | Workflow checked | SMIL and common inline CSS animation are rejected to avoid data loss; other CSS and complex SVG remain unverified. |
| Replicad | Workflow checked | Temporary restore failures offer guarded retry; unknown fields are rejected. Limited model generator, not general CAD. |
| Kiri:Moto | Workflow checked | Temporary workspace read failures offer retry; printer profiles, output and physical touch need independent verification. |
| Mesh:Tool | Workflow checked | Temporary workspace read failures offer retry; undo history and manufacturing correctness remain unverified. |
| G-code Preview | Workflow checked | Temporary restore failures offer Reload; supports a subset and does not validate machine safety. |
| Arduino Simulator | Workflow checked | Temporary firmware restore failures offer retry; D13 shows driven-high output, not analog brightness. No electrical simulation or browser compilation. |
| Pico Simulator | Workflow checked | Folder choices reject stale selections; firmware/peripheral support partial and unsaved flash cannot be recovered after a crash. Physical hardware unverified. |
| Digital Logic | Workflow checked | Examples and truth tables are foremost; labeled binary controls support multi-bit signals. Combinational JSON only; no hardware timing validation. |
| Circuit Simulator | Workflow checked | Includes a voltage-divider lesson with expected 5 V output; simulation is not hardware validation. |
| Electronics Design | Workflow checked | Opened projects require Save As to protect the original; copies may omit unsupported parts. Component coverage and hardware validation remain open. |
| Embroidery Studio | Workflow checked | Temporary restore failures offer guarded retry; pre-release, with physical sewing, machine formats and provider audit open. |
| Stitch Converter | Workflow checked | Temporary restore failures offer guarded retry; SVG support and machine compatibility remain partial. Test-sew output. |
| Falling Blocks | Preview | Emulated multitouch tested; physical phone and audible speakers unverified. |
| Owl Companion | Preview | Authored Rive artwork and physical-device testing remain open. |
| Snake Garden | Preview | Authored Rive artwork and physical-device testing remain open. |
| Physics Playground | Preview | XR and complete challenge acceptance remain open. |
| Clockwork Room | Preview | Four mechanisms and save recovery checked; physical-device review and final artwork remain. |
| Chess Study | Preview | Actual AI, save and reopen checked; AI strength and physical touch unverified. |
| Solitaire | Preview | One seeded draw-one deal played to victory and reopened live; draw-three and physical touch remain. |
| Sky Courier | Preview | Steering and firing checks passed; full campaign and physical touch unverified. |
| Marble Works | Preview | Pause/resume, account sync and reopen checked; all eight puzzles, physical touch and final artwork remain. |
| Stack & Balance | Preview | Touch cancellation, save and reopen checked; full challenge set and physical devices remain unverified. |
| Crystal Defense | Preview | Deleted-save and busy-pause handling checked; full eight-wave playthrough and physical touch remain. |
| Drone Circuit | Preview | Overlapping inputs, focus loss, save and reopen checked; physical multitouch and full course remain unverified. |
| Reactive Control Desk | Preview | Pending-save state, sync and reopen checked; physical touch and all orders remain unverified. |
| Story Cards | Preview | Account sync and isolation checked; complete story and physical touch remain. |
| Expression Puppet | Preview | Challenge, poses and account reopen checked live; physical touch, assistive technology and authored artwork remain. |
| Rhythm Garden | Preview | Single touch/accessibility activations and save/reopen checked; physical audio latency and full medal runs remain. |
| Lantern Leap | Preview | Overlapping inputs, focus loss, save and reopen checked; physical touch and all rooms remain unverified. |
| Garden Defense | Preview | Map cancellation and pending-save path checks pass; physical touch and full wave progression remain. |
| Pocket Rally | Preview | Focus/input, account save and isolation checked; full races and physical multitouch remain. |
| Sling Targets | Preview | Dirty settings and interrupted aim checked; physical touch and all arrangements remain unverified. |
| Gravity Pinball | Preview | Account save/reopen and input-focus checks passed; physical touch remains. |
| Kinetic Relay | Preview | Single-step dirty tracking and deleted-save protection checked; physical touch and full puzzle sequence remain. |
| Tabletop Bot Arena | Preview | Overlapping inputs and file-operation guards checked; physical touch and full cup remain. |
| Pocket Golf | Preview | In-flight saves retain unsaved state and hole changes ask before discard; physical touch and all holes remain. |
| Target Garden | Preview | Pointer cancellation and independent input tested; full rounds and physical-device review remain, with final artwork pending. |
| Orbital Courier | Preview | Flight, saved progress and mission phases from controlled checkpoints checked live; uninterrupted mission, touch, XR and final artwork remain. |
| Clockwork Quest | Preview | Full quest and account reopen checked live; XR session lifecycle mocked only, with headset, touch and final artwork unverified. |
| Memory Garden | Preview | Full keyboard six-pair game and account reopen checked live; physical touch, assistive technology and final artwork remain. |
| Circuit Lab | Research candidate, not deployed | ngspice source/relink distribution review and model licensing remain open. |
| PCB Design | Research prototype, not deployed | Browser packaging, dependency notices and usable design workflow remain open. |
| Personal template | App-author example | Not an end-user app. |

The 24 additional game previews passed individual builds and available unit tests; this does not establish a complete interactive review of each game. Most final artwork/audio remains pending; see [game asset gaps](GAME_ASSET_GAPS.md).

Shared tools in the menu are capabilities, not standalone user apps; their
consumer coverage is tracked in the detailed review. None of these rows closes
the broader requirement to audit all optional integrations, lifecycle paths,
formats, accessibility, physical devices and account isolation.
