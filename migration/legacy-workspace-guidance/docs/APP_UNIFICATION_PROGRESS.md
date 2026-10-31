# App workflow review

This is the working checklist for the Simplified desktop's app-by-app review.
“Prior evidence” refers to existing checks, not completion of the new review.
Every interactive app still needs a fresh review of its primary workflow,
account-backed open/save where applicable, first-run experience, desktop and
phone-sized interaction, cleanup, and an honest user-facing explanation.
Physical-device testing is separate. Shared tools need a tested consumer rather
than a standalone editor workflow. See `APP_WORKFLOW_CHECKS.md` for earlier
check scope and `SIMPLIFIED_HANDOFF.md` for dated deployment details.

| App | Role | Prior evidence / known boundary | New review |
| --- | --- | --- | --- |
| Files | Account and temporary Linux files | Account sync and Linux copy checked; drives are separate. Touch create/upload is live; a selected-file Open action is live; phone and desktop Text editing, sync, close/reopen, and fresh-context checks passed. | In progress |
| Text | Text and code editor | Files → Text edit, sync, close/reopen and fresh-context recovery checked; new-document naming, folder selection, collision handling, sync and recovery verified live on desktop and phone-sized views. | In progress |
| Terminal | Temporary v86 Linux | No automatic account-drive mount. | Pending |
| Help | Desktop help | No document workflow. | Pending |
| Calculator | Calculator | No document workflow. | Pending |
| Browser | Independent web browser | Experimental; temporary profile and no audio. Scroll fix verified in emulation. | In progress |
| Document Editor | Reports | Folder selection, invalid-file draft preservation and fresh-session recovery pass locally and on the live desktop. On the live phone-sized run those checks passed, but fixture cleanup hit a server request limit; test accounts were cleaned separately. Account project and PDF export checked locally; not a Word editor. | In progress |
| PDF Viewer | Read-only documents | Open, page navigation, resize and failed-open recovery checked locally and live on desktop and phone-sized views; report preview and PC upload checked locally. Canvas-only: no text selection, search or annotations. | In progress |
| Spreadsheet | Tables | Native save, XLSX import/export, folder selection and invalid-file draft recovery checked locally. The live desktop workflow passed; phone-sized checks reached fresh-session recovery but fixture cleanup hit the request limit. Advanced Excel compatibility limited. | In progress |
| Data Explorer | Data analysis | Desktop and phone-sized tests locally and live, plus local 4K-sized tests, cover CSV upload, SQL, chart, save to My files, cancelled overwrite, new-session recovery and reopening results. Query and chart settings remain temporary; physical touch remains unverified. | In progress |
| Python Notebook | Browser Python | Local Python/NumPy and same-browser account isolation checked. Save, automatic sync, invalid-file recovery and fresh session passed locally and live on desktop and phone-sized views; local 4K view emulated. Untrusted notebooks are not isolated. | In progress |
| Image Editor | Images | Local and live desktop and phone-sized tests cover opening, editing, save, rejected-image recovery and fresh-session recovery. Save As passes local desktop, phone-sized and 4K-sized checks and a live phone-sized check; animated GIF editing remains unsupported. Physical touch remains unverified. | In progress |
| Audio Editor | Audio | My files open, single-track edit, WAV save and reopen tested on desktop and emulated phone; an undecodable replacement preserves the current edit. Multitrack project saving and a physical phone test remain outstanding. | Partial |
| diagrams.net | Diagrams | Basic account save/reopen checked. | Pending |
| Excalidraw | Drawings | Basic account save/reopen checked. | Pending |
| SVG Editor | SVG artwork | Basic account save/reopen checked. | Pending |
| Replicad | Code-based CAD | Basic model generation and export checked; not a full CAD editor. | Pending |
| Grid tools: Kiri:Moto | 3D printing | Model import and G-code export checked; printer settings need independent review. | Pending |
| Grid tools: Mesh:Tool | Mesh editing | Import, union and account export checked. | Pending |
| G-code Preview | G-code viewer | Viewing checked; not an editor or printer connection. | Pending |
| Arduino Simulator | AVR firmware | Blink and independent windows checked; simulation is not hardware validation. | Pending |
| Pico Simulator | RP2040 firmware | Blink checked; flash and SSI support are partial. | Pending |
| Digital Logic | Gates | Basic gate and account save/reopen checked; no full schematic editor. | Pending |
| Circuit Simulator | CircuitJS | Divider simulation and account save checked; not ngspice. | Pending |
| Electronics Design | Electronics editor | Account project save/reopen checked; sample is not a production board. | Pending |
| Embroidery Studio | Stitch design | Example generation and account save checked; physical sewing unverified. | Pending |
| Stitch Converter | Stitch formats | Example conversion and account save checked; machine compatibility unverified. | Pending |
| Falling Blocks | Single-player game in development | Deterministic rules and exact logical snapshot have unit tests; no interface, account-file integration, Rive artwork or physical-device tests yet. Not registered or live. | In progress |
| Personal template | Per-user app example | Template, not a completed end-user tool. | Pending |
| CodeMirror | Shared editor capability | Used by apps; no standalone file workflow. | Pending consumer review |
| FFmpeg | Shared media capability | Programmatic conversion checked. | Pending consumer review |
| WaveSurfer | Shared waveform capability | Programmatic rendering checked. | Pending consumer review |
| Tone | Shared music capability | Programmatic synthesis checked. | Pending consumer review |
| ZIP | Shared archive capability | Files archive workflow checked. | Pending consumer review |
| Mermaid | Shared diagram capability | Programmatic capability. | Pending consumer review |
| ECharts | Shared chart capability | Programmatic capability. | Pending consumer review |
| Plotly | Shared chart capability | Programmatic capability. | Pending consumer review |
| pdfme | Shared PDF capability | Programmatic capability. | Pending consumer review |
| MapLibre | Shared map capability | Programmatic capability. | Pending consumer review |
| Transformers | Shared model capability | No model configured. | Pending consumer review |
| ONNX Runtime Web | Shared model capability | Separate CPU/WASM runtime; small local inference tested, no app integrated. | Pending consumer review |
| Trystero | Shared networking capability | Lazy library only; no signaling or app integration configured. | Pending consumer review |
| TanStack Virtual | Shared list/grid capability | Lazy framework-independent core; no app integrated. | Pending consumer review |
| WebTorrent | Shared peer transfer capability | Lazy browser library only; no tracker, transfers or app integration configured. | Pending consumer review |
| Yjs | Shared state capability | Lazy library only; no synchronization provider, persistence or app integration configured. | Pending consumer review |

New apps open full screen on phones and in alternating half-width, full-height tiles on desktop. Local and live viewport-emulation checks cover 1080p, 4K, maximization, resize, manual movement and phone/desktop transitions. Physical F11 and device behavior remain to be checked. Electronics Design’s three-view large-screen layout needs individual investigation.

During each app review, suppress optional third-party account and sign-up prompts where the local feature can work without them. The desktop account does not automatically grant access to an external provider; label any feature that genuinely needs one. Defer AI and other features that depend on removed account services for later integration; preserve working local features.

Deferred third-party service and AI features are tracked in `DEFERRED_APP_FEATURES.md`; those features are not implied to work through the desktop account.
