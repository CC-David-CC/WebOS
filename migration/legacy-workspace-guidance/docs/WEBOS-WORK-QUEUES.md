# WebOS work queues and progress ledger

This is the operational queue for the complete WebOS program. **Use and update this file whenever work is started, tested, integrated, deployed, blocked, or handed off.** Preserve the full scope below. Add discovered work to the appropriate queue; do not remove an unfinished item merely because a prototype exists.

## Queue notation and operating rule

- `[x]` means the exact stated outcome is complete and supported by evidence.
- `[~]` means partial, scoped, or research-only; it remains in the queue.
- `[ ]` means not complete or not yet verified.
- `LIVE`, `RESEARCH`, and `NOT STARTED` describe where a result stands; tests must name their actual boundary.
- Pop an item only when every part of its acceptance criteria is verified. Split a broad item before checking off a smaller result. Push newly discovered issues into the relevant section. Record date, commit/release, evidence, tests and remaining limitations in the ledger below. Do not use checked-box counts as a percentage of the overall vision.
- At each handoff reconcile this ledger against actual source, tests and live state. Maintain parallel work in isolated worktrees, integrate reviewed results, preserve user changes and back up source and notes.

## Scheduling: bounded work, parallel lanes and serial gates

Keep the complete program below as the backlog, not one enormous active task.
The lead selects a small active set based on current evidence and resources.
Each package names one observable result, exact base, owned paths, acceptance
tests, boundaries and a stopping point. Record status as ready, active, review,
blocked or done; add newly discovered work to the backlog rather than silently
expanding an agent's assignment. A failed test returns the package to active or
blocked with evidence; it does not become done merely because time expired.

**Can run independently:** app-specific UX/lifecycle fixes in separate
worktrees; documentation and inventory; independent security, accessibility,
and test reviews; CAD solver, geometry and manufacturing-model research behind
agreed interfaces. These lanes must not edit the same shared files. Tests that
need the same browser, port, CPU, disk or server use a scheduled resource slot.

**Must be ordered:** agree on a shared storage or host contract before dependent
implementations; implement server and browser sides in parallel after that;
integrate and test the actual combined workflow; independently review it; then
one designated operator stages, validates and deploys with rollback. Account,
file-format and service-worker migrations require compatibility and recovery
proof before a cutover. The CAD/3MF enclosure follows its necessary geometry,
material identity and export contracts; physical studies depend on qualified
models and a forward solver. App work can continue while these gates are open.

**Shared ownership:** one integration owner serializes edits to shared desktop,
storage contracts, hosting configuration and release pointers. Workers propose
changes and return exact commit, tests and limitations; the owner integrates and
tests them without overwriting other work. A release does not wait for unrelated
backlog items, but must meet the safety and compatibility gates for its scope.

**Current planning order on resume: storage first.** Make dependable account
storage the first major integration gate before broad app integration or CAD
delivery. The gate is met only when actual browser/server workflows preserve
saved data and account isolation, safely handle versions/conflicts, interruption
and recovery, keep heavy work off the UI thread, and demonstrate bounded
resources and responsive behavior at stated limits. Include the notebook's
committed-working-file protection, efficient transfer and compatible rollout;
do not claim a complete changed-chunk system merely because capture works.

After storage, integrate shared session/lifecycle safety and test cross-app
failures, then qualify apps one workflow at a time, classroom load, and the
parametric enclosure and material-aware 3MF slice. App investigation, design,
isolated fixes and independent tests may proceed in parallel when they do not
depend on unsettled storage contracts; do not release a dependent workflow or
create an app-specific competing storage system to bypass the storage gate.
Refine the ordering when actual evidence shows a dependency is different.

## Progress ledger — 2026-11-02 (paused)

- [x] LIVE: File-service non-JSON HTTP error status classification deployed and scoped two-account smoke passed. It does not fix server contention or guarantee exactly-once writes. See `evidence/file-http-status-errors-20261102.md`.
- [x] LIVE: G-code Preview rejects a stale file-session result; isolated race and live sync/isolation smokes passed. See `evidence/gcode-session-live-candidate-20261102.md`.
- [x] LIVE: Calculator cannot close while its file operation is pending; scoped live smoke passed. This does not fix logout/account-switch races. See `research/calculator-close/live-activation-20261102.md`.
- [x] LIVE: Excalidraw rejects stale file-chooser results; scoped live sync/isolation smoke passed. See `research/excalidraw-chooser/live-activation-20261102.md`.
- [~] RESEARCH: changed-data transfer and 128 MiB worker capture/upload demonstrated. Not live; large snapshots still consume substantial memory, and managed mixed-version rollout, crash recovery and full bidirectional incremental sync remain open.
- [~] RESEARCH: RAM-only Jupyter models, widgets and Jupytext formats have prototypes. Not live; an isolated copy of the live notebook reproduced a browser-local working-file stale-handle overwrite. Avoid opening the same Python working file in two notebook windows; back up with File → Save working file to My files. User accepts losing unsaved edits, not overwriting saved data.
- [~] RESEARCH: shared session-lifecycle work protects selected apps in isolated tests. The live logout/account-switch data-loss risks and multi-app qualification remain open.
- [~] RESEARCH: CAD/3MF and physical-system work is partial; no general material-aware 3MF or qualified physics workflow is claimed.
- [~] LIVE: separate /desktop/ sizing prototype remains reserved; do not overwrite it as incidental work.
- [ ] Queue next: safe notebook saved-data protection and RAM model; worker-based bounded file capture/sync; versioned asset/service-worker migration and rollback; session recovery; app-by-app My files and lifecycle qualification; classroom load and failure tests.

The following is the complete underlying checklist. Its unchecked boxes are acceptance gates, including items with partial progress above.

## Current bounded storage milestone

User priority: saved data, account isolation, conflicts, interruption and
recovery, with heavy processing in workers. Work on these as one real
browser-to-server flow, including existing-file updates and fresh-session
reopening; other app and platform work waits unless needed for this flow.

Latest direction: establish `beta.ksu.codes` as the test environment for
iteration; after beta is established, qualify an upgrade path to the main
`ksu.codes` site separately. DNS currently resolves both names to the same
address, but HTTPS routing and any beta services/state must be verified and
kept separate before beta is considered ready. The current site has no real
users, so preserving an old-user upgrade path is not a prerequisite for
replacing its test services. Preserve existing on-disk data and configuration
unless specifically authorized otherwise.

Beta provisioning progress: `https://beta.ksu.codes/` is publicly routed and
trusted HTTPS returned 200 on 2026-11-02. The initial activation rolled back
cleanly while its certificate was issuing; retry passed, the renewal timer was
restored, and existing sites passed health checks. Activation evidence is in
`research/beta-isolated-hosting/ACTIVATION-2026-11-02.md` on branch
`research/beta-hosting-isolation` at `8ce4f843a`. An isolated signed-browser fixture verified separate beta
accounts and files, host-only secure cookies, and rejection of cross-origin
tokens. A managed-route fixture also verified file create/read/replace and
conflict handling against the corrected guest source. Beta
guest Internet is intentionally disabled pending a separately controlled relay.
The route fixture used a shared service UID. A separate real-process fixture
ran the three services as distinct unprivileged UIDs and verified signed
file operations and denied cross-role and main-fixture filesystem reads. A
separate service operator is under development; these processes share loopback
network access. Three beta services are now installed and running on private
loopback ports with separate locked users, keys and data; signed file operations,
cross-account denial and service restart were tested against these real
services. Their units are enabled at boot, though an actual host reboot has
not been tested. Public Chromium registration, file creation/edit/save, sync,
fresh-context sign-in/reopen, cross-account read denial and v86 shell readiness
passed; the disposable test file was deleted, while two test accounts remain.
The beta candidate does not yet implement
changed-chunk synchronization.

Next beta storage candidate: a minimal transfer server based on the deployed
beta worker was built reproducibly (`9db35b5ba`; artifact begins `2bb2e9af`).
Isolated signed tests cover changed-chunk transfer, account denial, conflict,
interruption and gateway process death before/after publication; a browser
fixture also covers interrupted/tampered reads and lost-reply retry. The
production CLI's 2,048-request/minute shared limit may throttle chunk reads
and multiple users (256 was the test fixture's class default);
large-file, concurrency, further conflict/recovery tests and beta deployment
remain open. These process-kill tests do not prove power-loss durability.
The browser test exposed a lost-reply followed by a later local edit that
preserved both versions but incorrectly raised conflict. A research fix records
the attempted hash durably and passed close/reopen and later-delete cases;
ordinary delete of an unresolved conflict is also being guarded. The newer
server candidate batches up to eight authenticated chunk reads and reserves
space for its own snapshot/write temporary files. Its 5 GiB admission floor is
per process, not a global guarantee against other processes or mount changes.

2026-11-02 research progress: ordinary writes now refuse to replace a local
version in an unresolved conflict; an isolated signed-account browser test
verified both versions and explicit resolution. A separate candidate reports
uncertainty if account validity changes after a local transaction commits;
an isolated signed-account Chromium test confirmed the local commit and
isolation, with simulated invalidation. Server sync required an explicit retry;
desktop-switch qualification and durable receipts remain. Neither change is
live. An isolated server test confirmed an external
host writer can still race publication; pre-publication revalidation reduces
the window but cannot guarantee atomicity against uncoordinated writers.
Signed gateway process-kill tests preserved old bytes before publication and
new bytes after rename plus directory fsync; they do not prove power-loss
durability. A real test-proxy TCP abort after server commit, combined with a
new local edit, preserved both versions and surfaced a conflict. Separately,
an injected directory-fsync failure after rename exposed a gateway bug: it
reported refusal despite the new file being visible. Phase-aware file and
folder mutation handling, plus cancellation-resistant bounded quota-cleanup
retries, are integrated in research and passed focused signed/fault tests;
they are not live. Persistent quota cleanup failures can still hold a slot
until expiry, and power-loss and arbitrary direct host writes remain unproven.

- [ ] Preserve previously committed bytes through saves, errors, concurrent
  writers, account changes, process interruption and lost acknowledgements.
- [ ] Enforce and test account isolation at browser, transport and server.
- [ ] Detect stale writes and preserve both versions or refuse without loss;
  report the actual state to the user.
- [ ] Recover interrupted work safely on restart, including uncertain commits;
  don't claim recovery where it hasn't been proven.
- [ ] Run heavy hashing and data processing in bounded, cancellable workers;
  measure actual memory and responsiveness rather than claiming a hard bound.
- [ ] Test the integrated path using real signed accounts, independent sessions,
  conflicting writes, fault injection and representative file sizes. Qualify
  rollout and rollback before changing live storage.

The previously paused broader program remains the backlog; this milestone does
not mark its other acceptance gates complete.

---

# Browser WebOS: complete program and handoff checklist

This is the user's long-term program, not a claim that all items are implemented. It is deliberately broad; new work discovered through use belongs on the list. Work in dependency order but combine tightly related implementation and tests into end-to-end slices. Parallelize independent apps/engines in isolated worktrees and integrate early. A milestone is complete only when its own tests and real workflow pass; a button, a package, a mock or a design document alone is not completion.

## Current starting point (2026-11-02)

- The current live system is the Simplified browser desktop at `https://ksu.codes/`. It is a test site and the user has authorized testing and updating it; do not assume that an authorization to delete unrelated data follows. `https://ksu.codes/desktop/` is a separate sizing prototype and should not be overwritten as incidental work.
- The current Simplified source/notes are in `/home/dflanag3/CodiServer/desktop-preview/SIMPLIFIED`; box-git backup is `box-git:/srv/data/git/CodiServer-distro.git`. The jSketcher fork is backed up at `box-git:/srv/data/git/JSKetcher.git`. Its GitHub remote was removed at the user's request: **use box-git only until the user changes that instruction**.
- The main Simplified worktree contains unrelated in-progress changes. Inspect `git status`, instructions and actual live state before every change; use a separate worktree/branch and never overwrite, stash, revert or delete someone else's work to make a test pass. Runtime state, credentials and real user files never belong in a source release. Generated intermediate builds and dependencies are disposable; final required public source/runtime assets and notes must be reproducible and backed up.
- Many apps have basic workflow evidence, not universal qualification; consult `docs/APP_STATUS.md`, `APP_UNIFICATION_PROGRESS.md`, app READMEs and live evidence, checking dates before relying on them. **Microduck is live**, and a real two-account public test covered running, server save/hash, denial to the second account and fresh-session reopen. It does not prove hardware fidelity, physical touch or complete simulation-state recovery.
- My files currently uses browser/account mirroring and a signed server gateway. A research candidate now exercises signed changed-chunk upload and download, including a 128 MiB browser test; see desktop branch `research/webos-cad-combined-20261102` and `docs/COMBINED-RESEARCH-CHECKPOINT.md` there. It is not deployed or a completed bidirectional incremental system: browser memory, incremental computation, external writers, recovery, packaging and concurrent-user limits remain open. An independent SQLite chunk model is also research only.
- jSketcher is a research candidate, not a deployed integrated CAD workflow. A browser host/export prototype has produced valid core 3MF for two disjoint assigned boxes using a stand-in file store. The enclosure's touching inset is deliberately refused pending qualified interference checks. This is not yet a qualified general manufacturing exporter. Solver midpoint/conflict fixes remain research-only; do not rely on them until the whole conflict/recovery path is qualified.
- User authorization covers necessary installs, downloads, live tests and changes; use scoped test accounts, remove only fixtures you created, and retain accounts/data if safe cleanup cannot be proved. Do not ask the user to approve routine reversible work or repeat permission already given. Communicate before disruptive changes, use established managed rollout/recovery, and never restore old account databases or files merely to roll back code.

## 0. Shared rules for every milestone

- [ ] Start from real current source, running configuration, related docs and app behavior; classify each statement as verified, partial, planned or unknown. Reproduce a reported bug before claiming a fix, unless the direct defect is already conclusive.
- [ ] Ship a complete vertical task: open/create -> change/use -> save -> close -> reopen -> inspect result; preserve two independent windows and account isolation. Use My files for account work, and label upload from the computer separately. Temporary v86 Linux files stay temporary and separate; Files may expose its Linux home for exploration.
- [ ] Make interface and workflows clear to a novice without removing expert controls. Test touch and accessibility, keyboard/mouse, phone, 1080p and 4K; genuine physical-device results must be distinguished from viewport emulation. Use sane default window sizes by viewport and resize responsive layouts after fullscreen/viewport changes.
- [ ] Preserve edits on failed open, save, cancellation, failed computation, stale version or account switch. Close dialogs should be app-themed, honest and cancelable. Repeated open/close must not accumulate listeners, workers, timers, audio, guest sessions or object URLs.
- [ ] Share desktop services, permission checks and documented commands; keep third-party UI frameworks and dependencies inside their app bundle where appropriate. Do not introduce a new global framework or an unnecessary wrapper when a native menu/file action suffices.
- [ ] Remove or suppress third-party account/provider prompts and telemetry where requested; maintain `DEFERRED_APP_FEATURES.md` with product and feature names that were disabled. Do not imply an AI/provider replacement exists. Preserve license/source notices and check distribution obligations for real dependencies.
- [ ] Check app/service boundaries with real registered accounts, malformed inputs, conflicts and resource limits; distinguish unit, browser-emulation, physical device, public network and real hardware evidence. Never claim a simulator, export, manufacturing file or optimization result proves real-world safety or accuracy.
- [ ] Keep app status, a plain student guide and a reproducible test recipe current. If a feature is incomplete, label it accurately instead of shipping a misleading success. Back up source/notes to box-git; clean only identified temporary fixtures and obsolete builds, monitoring local and server disk/RAM.

## 1. Accounts, storage and file-service baseline

- [ ] Verify login/register, session expiry, account switches, credential recovery and error handling on live and isolated services; enforce the user's current username/password rules. Visitors must authenticate to enter the desktop. Do not log passwords, private keys or file contents in diagnostics.
- [ ] Exercise account IDs -> permission records -> isolated server directories. Test two simultaneous accounts and an attacker using changed IDs, paths, symlinks, traversal, replayed proofs or another account's file; no foreign file, chunk-existence information or directory listing may leak.
- [ ] Verify My files browser-first save, pending/synced/conflict status, durable server write, fresh-session recovery and user-visible errors for quota, missing files, permissions, disk full, browser storage eviction, lost network and server restart. Ask for persistent browser storage where supported; explain that browser clearing can remove its copy.
- [ ] Retain normal account files as server disk files and a browser copy, while keeping temporary Linux guest data separate and resettable. File moves, copies, deletes and folder operations must be atomic or explicitly recoverable; sync deletion only with correct account/version checks.
- [ ] Test ordinary and interrupted uploads/downloads near the intended 128 MiB file limit without asserting every editor can open a 128 MiB file. Measure browser heap, server RSS, temporary disk, file descriptors and responsiveness; enforce documented, meaningful bounded resource limits.
- [ ] Capacity-test 10–30 simultaneous classroom sign-ins and prepare for roughly 100 parallel users, including a subset transferring large files, slow clients and unrelated small reads. Measure cold and warm disks and service recovery before claiming a capacity number.

## 2. Bidirectional changed-chunk synchronization

- [ ] Write a versioned protocol specification and executable test vectors. Define account/path/version binding, chunk size/content-defined boundary rules, chunk order and length, cryptographic hash domains, canonical manifest, version/CAS tokens, file rename/delete semantics, limits and error codes. A Merkle or manifest root is a **new version type**; it is not the existing flat SHA-256 and cannot be obtained by concatenating independent SHA-256 hashes.
- [ ] Preserve the existing normal signed challenge/proof and account authorization for manifest, chunk and commit operations. Scope chunk existence, staging, storage and caches per account. Test that an unrelated account cannot infer the existence or contents of a chunk from timing, error shape or an API response.
- [ ] On first sync transfer the required content; on later sync compare verified manifests and transfer only missing/changed chunks in **both** directions. Incremental hashing must reuse verified unchanged data when the storage layer provides trustworthy dirty ranges/versions. For inserts and deletes, measure resynchronization rather than assuming fixed boundaries preserve all following chunks.
- [ ] Support optional, versioned format-aware adapters where they save meaningful work: for example, document edits or CAD object/parameter changes. Define the adapter's supported versions, canonical representation, deterministic reconstruction and final integrity checks. Preserve the exact intended file and its metadata, account authorization, conflict recovery and rollback; use verified byte-based sync for unsupported, damaged or ambiguous formats. Test compressed containers and binary assets rather than assuming semantic edits always produce small byte changes. Do not make format-specific parsing a requirement for ordinary file access.
- [ ] Provide a safe transition from current full-file SHA and flat server files: build verified manifests on demand; maintain explicit legacy-client behavior and avoid changing the meaning of old version tokens. Full transfer may be necessary for first sync, a missing cache, a legacy peer or untrusted/corrupt metadata; document and test that exceptional path rather than treating it as normal changed-file sync.
- [ ] Stream bounded chunks with backpressure and bounded parallelism. Keep browser UI responsive; check cancellation/account identity after asynchronous work. Bound weak-hash/strong-hash candidate work (the old rolling prototype had a repeat-data collision flood) and prevent unbounded RAM, disk, timers, worker or file-descriptor growth.
- [ ] Run heavy file processing, hashing, simulation and similar computation in Web Workers or appropriately isolated worker processes, not on the UI thread. Verify responsiveness, bounded concurrency, cancellation, disposal and account/session changes, including multiple simultaneous app windows. Lightweight UI coordination may remain on the main thread.
- [ ] Stage private uploads, verify each chunk, order, size, full logical file and expected prior version, then atomically publish a complete file/manifest. Recover interruption before/after every journal, rename and fsync boundary; reconcile a lost reply that may already have committed. Never replace a newer version or publish a partial file.
- [ ] Persist browser chunk cache/manifest with transactionally bound generations and user/account isolation. Coordinate same-account tabs and devices; on conflicts preserve both edits until the user chooses. Download into a temporary verified snapshot and publish only after every required chunk is valid. A fresh device may need all chunks; a device with a valid prior copy should fetch only changes.
- [ ] Handle account logout, switch, deletion, file delete/rename, interrupted retry, missing chunk, cache eviction, quota and server restart. Garbage collection must not remove chunks referenced by committed files, in-flight transfers or recoverable journals. Existing host-disk edits must invalidate or rebuild stale metadata safely.
- [ ] Test first sync, no-op, one-byte changes in multiple chunks, insert/delete, rename, high-entropy and repeating/adversarial inputs, duplicate/out-of-order/corrupt/truncated chunks, forged manifests, account leakage, overlapping writes, lost reply, both-side crashes and expired sessions. Capture transferred application bytes both ways; for a 104 MiB file with a one-byte edit and a valid prior copy, demonstrate small changed-data transfer rather than a full file, and document measured overhead.
- [ ] Run real signed browser/server tests, 128 MiB boundaries, slow/cold disk, concurrent classroom load, two browsers/devices and a physical phone where available. Measure CPU, UI latency, memory and total peak disk; validate manifests and final bytes against independent full-file hashes. Only then stage a pinned release with exact operator inventories, crash-tested journal recovery and code-only rollback. Never wipe accounts/files to simplify the test.

## 3. Desktop, lifecycle and operations

- [ ] Keep the desktop as a unified application host: window/workspace state, focus, taskbar, launcher grouping, settings, themed errors, menus and keyboard/touch controls must remain consistent. Restore only intentionally saved state, not stale processes or another account's windows.
- [ ] Require per-window ownership and disposal for DOM listeners, workers, graphics contexts, audio, guest terminals and network requests. Test repeated open/close/reopen, multiple same-app windows, account changes during asynchronous work, minimizing, viewport rotation and stale completions.
- [ ] Support My files import/export in desktop dialogs without duplicate app-specific sign-ins. Integrate file actions into each application's own menu; remove redundant wrapper bars and transient 'opened' overlays. Upload remains explicit; use the requested Files right-click/download and drag-upload behaviors where supported.
- [ ] Make offline/connection status and maintenance honest: no claim of saved work without proof. Test reconnect, server restart, dropped Wi-Fi, interrupted save and explicit last-saved recovery. Users retain normal browser control; do not tell them that reloading necessarily accelerates peering.
- [ ] Maintain secure origin/CSP, cross-origin isolation and private runner policies only where needed. Verify executable dependencies, source/licensing, authentication for source/license pages and prevention of third-party credential/telemetry calls. Public network relay/browser is experimental and low priority; never imply arbitrary sites are rendered correctly or originate from the visitor's connection.
- [ ] Provide discoverable, typed, validated per-app operations for people and agents through the **same** model, authorization, file and lifecycle rules. A browser API is not automatically a remote-agent service. Require a separately authorized transport, per-user/instance permissions, revision checks, cancellation, limits and auditability before external invocation.

## 4. App-by-app delivery: core, office and programming

Apply all section 0 tests to each app; maintain a real status row and guide for each. Group related work but finish each app's primary user task.

- [ ] **Files:** discoverable create/rename/move/copy/delete/upload/download, sync/conflict feedback, safe folder behavior, browser/account storage and separate temporary Linux home. Test host disk changes, multi-tab, large files, interrupted moves and recovery; never pretend folder moves are done if not implemented.
- [ ] **Text/CodeMirror:** open/create/edit/save/reopen code and text with revision/conflict handling, large-file limits, encoding and touch selection; validate real desktop and phone. Shared editor library remains isolated/packaged correctly and resources release on close.
- [ ] **Terminal/v86:** independent shell sessions/windows, xterm scroll/touch controls and honest temporary-filesystem boundaries. Test supported BusyBox/nano/interactive behavior, guest reboot/reset, authenticated network/SSH policy and per-user destination-only logs. Do not claim guest files are the persistent account drive.
- [ ] **Calculator and Help:** complete the basic calculation/history and explanation flow; ensure help is truthful, concise and reflects the beta service.
- [ ] **Documents:** usable report-writing, proper My files open/save and PDF export, layout/print correctness and Unicode coverage; no DOCX/XLSX requirement unless the user requests one later. Distinguish document edits from flattened export.
- [ ] **Spreadsheets:** correct supported CSV/TSV round-trips, formulas, large-cell behavior and bounded large-file work; replace the existing 8 MiB restriction only after measuring a safe implementation. No requirement to support XLSX.
- [ ] **PDF Viewer:** safe opening, navigation, text/search where supported, password handling, large documents and explicit scan/OCR limitations; use My files and release workers/resources.
- [ ] **Data Explorer:** import, inspect, query/visualize and export using DuckDB/Perspective; test precision/large integers, malformed data, memory and reproducible results. Never silently round exact identifiers.
- [ ] **Browser Python Notebook:** isolate per-account notebooks, use stable non-enumerable IDs, test kernel startup/recovery, packages, autosave/conflicts, real account isolation and worker cleanup. Explain browser Pyodide limitations and treat untrusted notebook execution appropriately.
- [ ] **Notebook scripts and widgets:** default to metadata-free Jupytext `py:light`; offer `py:percent` and explicit `.ipynb` when notebook metadata or saved outputs are wanted. Running cells, changed execution counts or transient outputs alone must not trigger sync of the source file. Preserve authored code and Markdown, detect unsupported or lossy conversions, and test round-trip, conflicts and fresh-session reload. Bundle and test real `ipywidgets` Python and frontend support locally, including actual callbacks, phone touch, independent kernels and cleanup; do not claim support merely because a package imports.
- [ ] **Linux Notebook and terminal tools:** clearly label the separate v86-backed path; demonstrate supported subprocesses, executable tools and package behavior before claiming them. Preserve temporary Linux state semantics and avoid treating it as persistent My files.

## 5. Creative, media, diagrams and shared tools

- [ ] **Image Editor:** open/save from My files, Blob/object URL cleanup and conflict-safe saves; qualify animated/metadata/format limitations, low-memory devices and changes during long operations. The lower-copy candidate is research-only until exact live integration and account tests pass.
- [ ] **Audio Editor, waveform and Tone tools:** coherent open/edit/preview/export, independent audio windows and cleanup; disclose unsupported channels/codecs, measure latency on physical devices and prevent autoplay surprises.
- [ ] **diagrams.net, Excalidraw, SVG Editor:** use each program's own file menu with shared storage, no vendor account prompt, safe import/export, unsaved-change recovery and touch/4K layouts. Test complex SVG and unsupported provider integrations honestly.
- [ ] **Embroidery Studio and Stitch Converter:** local file workflow, material/thread settings, preview, explicit unsupported SVG and machine-format limits; remove provider routes while recording deferred AI features. Do not claim machine compatibility without independent validation.
- [ ] **Photos/video/music/books/news/maps and other requested apps:** inventory actual source and licenses; integrate only real working runtimes with shared storage, responsive layout and cleanup. For planned items—PhotoSwipe, Shaka/Video.js/hls.js/Mediabunny, Howler, foliate/PDF.js, Readability/RSS, MapLibre/OpenLayers/Leaflet—distinguish an included library from a usable app.
- [ ] **Shared system tools:** inventory CodeMirror, ffmpeg.wasm, zip.js, Mermaid, Plotly/ECharts, OpenCascade, ONNX Runtime, Transformers, MapLibre, WaveSurfer/Tone, TanStack Virtual, Trystero, WebTorrent and Yjs by actual bundled capability. Lazy-load with versioned resources, tests and disposal. A gray menu entry is a library reference, not proof of an integrated workflow; no P2P optimization is a current chat goal.
- [ ] Test browser-native media permissions, MediaDevices/MediaRecorder/WebCodecs and any provider/JMAP/MQTT integrations only when built and explicitly authorized. No user-supplied AI provider is currently configured; keep missing provider-dependent features on the running deferred list.

## 6. Electronics, fabrication and games

- [ ] **Arduino/AVR8js:** run actual firmware, GPIO/timers/UART examples, open/save source and firmware, distinguish simulation from physical execution. Evaluate and benchmark browser compiler vs v86 toolchain before promising either; Web Serial is separate and opt-in.
- [ ] **Pico/RP2040js:** load real supported firmware, serial and examples; accurately qualify peripherals, simulated flash and reset/save behavior. Warn about unsaved simulation state and never promise physical hardware fidelity.
- [ ] **Digital Logic/Circuit Simulator/Circuit Lab/PCB:** use honest examples and explain combinational/netlist vs analog simulation vs PCB design. Qualify supported components, solver, visual parts and My files separately. Circuit Lab/PCB research is not deployed merely because source exists.
- [ ] **Electronics Design:** provide breadboard, schematic and PCB views that can be arranged side-by-side on large monitors, with simplified touch on phones. Verify component coverage, consistency across views, imports/exports, versioned saves and failure when parts are unsupported.
- [ ] **Replicad, Mesh:Tool, Kiri:Moto and G-code Preview:** test actual model, mesh, slicing and preview workflows, supported formats and output; isolate heavy engines, avoid duplicate copies and report machine/printer limitations. A preview or simulated slice is not a verified physical print.
- [ ] **Game previews:** preserve the four on-disk/menu groupings. For each preview finish a complete ordinary playthrough, rules, controls, pause, account save/reopen where relevant, two windows, audio and actual touch. Add final art as available; XR is a separately tested capability, not implied by a folder name. Keep seven Learning & Strategy rule-only entries disabled until an interface and workflow exist.
- [ ] **Microduck:** preserve the live two-account save/reopen and isolation checks; continue qualification of actual controls, phone use, runner lifecycle, model/reference data and honest physical-simulation limits. Its current 64 MiB project opener is not the general 128 MiB file-service guarantee.

## 7. Native CAD: sketch and parametric foundation

- [ ] Audit each advertised relationship as an explicit mathematical contract: entity types; supporting vs finite geometry; units, signed/unsigned and orientation; endpoint/contact/branch selection; degeneracy; failure and persistence.
- [ ] Correct midpoint as `2P=A+B`, preserving the current midpoint-style Symmetry behavior without duplicate equations. Before release, solve the existing atomic-admission/redundancy/conflict problems: rejected constraints must not move geometry, contaminate later constraints or lose object links; removing a blocker must re-evaluate safely. Test stored constraint orders, repeated solves, invalid input, save/undo/reopen, exceptions and reasonable large connected sketches.
- [ ] Implement driving signed X/Y and projected distances, diameter, concentricity, collinearity, full-entity fix, rigid groups and independent-axis symmetry. Keep reference measurements separate from driving constraints; a radius readout must not be called diameter.
- [ ] Build shared typed measurement/relation operations for equality, ratio and difference of lengths/angles instead of separate inconsistent subsystems. Geometric unknowns solve together; formulas over existing parameters evaluate in dependency order. Define meaningful underconstrained, locally constrained, redundant, inconsistent, degenerate, failed-convergence and ambiguous-branch states.
- [ ] Preserve user intent for line/segment, circle/arc domains, directed/minor/supplementary angles, internal/external contact and zero-length geometry. Test tolerances at different scales, residuals, rank/singularity, warm starts, failed edit rollback and explicit repair. A failed solve is not automatically proof of impossibility.
- [ ] Add typed units, formulas, dependency/cycle errors, integer/boolean domains, reference/driving conversion and configurations. Do not silently round a dimension or invent a physical unit. The WebOS numeric parser differs from a standalone `eval` path; audit the actual mode and do not claim full unit/dependency support yet.
- [ ] Qualify real model history for datums, extrusion/revolve/booleans, holes, fillets/chamfers, patterns, shell/draft, sweep/loft and multiple bodies. Preserve authored input and clearly mark stale/failed geometry after regeneration. Test changes, undo/redo, save/reopen and failure recovery.
- [ ] Strengthen stable authored feature/part IDs and generated-topology provenance. A UUID or array index on a reconstructed face is not enough. On split, merge, disappearance or ambiguity, preserve intent and request repair rather than silently binding the wrong geometry. Support OCC and Native Mesh only for actually implemented operations; no parity claim.

## 8. Core model 3MF manufacturing milestone

- [ ] Native project is the editable source; the core 3MF is a manufacturing handoff from a specific design revision. The format is not fixed and the old importer is not required. Protect files from accidental overwrite and reject unsupported/corrupt formats clearly.
- [ ] Persist deliberate, named parts/regions, units, authored grouping, transforms, material identity and independent appearance. Ordinary parameter edits must preserve verified assignments or clearly mark missing/split/merged/ambiguous bindings for explicit repair. Color is not material identity.
- [ ] Represent **one printable object with multiple aligned material regions** separately from **multiple independently printable objects**. The author selects the grouping; do not infer it from color. Preserve source revision, build items, components and transforms. Do not require printer, filament, slicer or Bambu-project settings in core model 3MF.
- [ ] Generate model-derived geometry, not camera/display meshes. Request a controlled tessellation tolerance without modifying the live CAD model, retain orientation and placement, and ensure correct units. OCC's current `Interrogate` remeshes at a fixed tolerance; the research copied-shape path and exact-box indexing are not general curved/cavity solutions.
- [ ] Validate finite coordinates, triangle indices, closed/watertight orientation, non-manifold edges/vertices, degeneracy, self-intersection and inter-region overlap/contact. Preserve real shared interfaces and report uncertain cases; do not use a special rectangular-pocket exception as a substitute for general validation. Bound memory, time and cancellation.
- [ ] Write standards-conforming 3MF core ZIP, XML, resources, base materials, build objects/components and transforms to My files with conflict-safe save. Independently read/validate names, units, bounds, materials/colors, grouping, mesh and revision; measure resource use. No claim that color alone specifies physical properties or actual printer compatibility.
- [ ] End-to-end acceptance: create an enclosure body, separately printable lid and contrasting inset label grouped with the lid; change width and wall thickness; save/sync/reopen the native design; export 3MF; independently verify two build objects, three assigned regions, placements and dimensions. Test stale revision, split/missing body, invalid mesh, overlapping regions, cancellation, two accounts and interrupted output. Simulated manufacturing feedback can be used with stated assumptions. **Bambu Studio, physical filament assignment and a real print are optional, not gates.**

## 9. Curves and demanding profiles (after the mechanical vertical slice)

- [ ] Qualify ellipse axes/orientation, general point-on-curve, curve normals at a defined point, arc/path length and fraction-by-parameter versus fraction-by-arc-length.
- [ ] Add spline endpoint tangency and explicit G0/G1/G2 behavior with stable contact/branch choices, continuity diagnostics, degenerate derivatives and save/undo/reopen. A circular fillet tangent to lines is not automatically G2.
- [ ] Add associative projection, intersection and pierce with persistent references, explicit multiple-solution choices and failure repair; avoid silent rebinding. Start area/perimeter as measurements and add driving global constraints only for a demonstrated workflow.
- [ ] Prove a curved handle/cover through major parameter edits, continuity inspection, regeneration, export and honest limits across the engines that actually support it.

## 10. Physical-system document and materials

- [ ] Make the authored physical system a coherent model: geometry and meaningful regions, material definitions, assignments/orientations, interfaces, physical formulations, operating conditions and design requirements. A CAD body, material region, print object and surrounding analysis domain can differ.
- [ ] Keep a real material's supported physical properties together; represent scalar, directional/tensor, state-dependent and history-dependent laws where required. Store units, source/revision, applicable range, calibration and uncertainty. Unknown values stay unknown; do not silently insert attractive defaults.
- [ ] Separate a material definition from region assignment and orientation so two regions can use one material differently. Represent bonded/sliding/contact, thermal, electrical and field interfaces explicitly; a geometric union must not silently erase a needed interface.
- [ ] Version and persist sources/excitations, mechanical loads/supports, environmental/initial conditions, motion states and operating ranges. Test ordinary geometry edits and explicit unresolved references after topology changes. Distinguish modeled deformation from an authored design change.
- [ ] Reuse the same validated document operations for UI and authorized agents; enforce revision, permissions, cancellation and provenance in both. A model, an analysis mesh and a result are different artifacts with explicit dependencies.

## 11. Forward studies, form finding and solver tools

- [ ] Keep three workflows distinct: forward simulation predicts behavior for a specified system; physical form finding finds an equilibrium/evolving state; inverse design searches allowed design variables for better objectives. Do not turn a predicted deformation into permanent geometry without an explicit action.
- [ ] Qualify actual meshing/solver runtimes before exposing them as usable system tools: Gmsh may have a browser WASM path; Elmer and GetDP require verified ports or controlled backend execution. Review licensing, resources, sandboxing, cancellation, CSP, repeatability and source availability; a menu entry is not integration.
- [ ] Derive a tagged numerical mesh from the revisioned model and region/boundary assignments. Specify analysis domain—including surrounding air where relevant—formulation, units, boundary conditions, materials, operating cases, requested outputs, tolerances and software versions.
- [ ] Run and retain reproducible studies; record inputs, solver/mesh settings, convergence, failures, warnings and provenance. Validate against analytical or trusted reference cases, mesh refinement/sensitivity and material applicability. Label stale results and prohibit presenting a failed solve as a valid candidate.
- [ ] Test thermal, structural, electrical and magnetic extensions only as actually implemented; distinguish quasistatic/transient, nonlinear and coupled assumptions. Compare simulation with physical measurements only when such evidence is available and clearly identify uncertainty.

## 12. First magnetic design and inverse-search milestone

- [ ] Create a magnetic sensor fixture with named solid and surrounding regions, a meaningful sensing region, packaging/assembly constraints and operating positions/range. Define desired response and explicit allowed dimensional/material/orientation changes.
- [ ] Supply a small curated set of real material models with appropriate magnetic laws, units, sources, ranges and orientation; unknown properties remain unknown. Distinguish linear/nonlinear response, saturation, permanent magnets, anisotropy, hysteresis/loss and temperature only where the chosen study supports them.
- [ ] Show that changing geometry or material yields a reproducible, physically justified change in a region-based quantity, not just a color plot or single hand-picked point. Validate units, domain/boundary treatment and appropriate mesh refinement against a trusted reference.
- [ ] Run a bounded search over declared dimensions/materials/conditions, with resource budgets, cancellation, invalid-candidate handling, reproducible seeds and no unauthorized variable changes. Measure performance across required operating cases and preserve every candidate's input and evidence.
- [ ] Regenerate a selected manufacturable design and independently reanalyze it. Report a better feasible candidate, a local optimum or tradeoffs only as established; do not invent a material by independently tuning incompatible properties or imply a global optimum/physical validation.

## 13. Future mechanisms, materials research and additional domains

- [ ] Make assembly instances and saved references durable, then qualify fixed, revolute, prismatic, cylindrical, planar and spherical joints, limits and couplings with a linkage/slider and closed-loop tests. Current assembly registry and unsupported snapshot behavior are not a complete mechanism system.
- [ ] Separate kinematics from collision, physical dynamics, clearances and manufacturing tolerances. Couple structural deformation and magnetic fields only through an explicitly specified and validated study.
- [ ] Add material-distribution/topology optimization, advanced surfacing, sheet metal, routing, drawings and specialized analysis only against a concrete use case; maintain explainable assumptions, model-specific validation and provenance across scales.
- [ ] Defer provider-dependent AI, optional P2P/WebRTC features, CDN/distribution and optional real printing/slicer projects until separately selected. Preserve architecture hooks without treating any of them as prerequisites for the current 3MF milestone.

## 14. Release, testing, handoff and acceleration

- [ ] For every change, run focused unit and failure tests, then a representative end-to-end account/browser workflow. Test real generated artifacts with independent readers or implementations. Do not repeat broad tests without a reason; do not substitute mocks for the required real boundary.
- [ ] Stage code-only, content-addressed releases from clean source. Preserve current live flags, ports, account data, other sites and the /desktop prototype. Verify exact runtime/dependency/manifest hashes, CSP and service state. Test upgrade, interruption, recovery and code-only rollback before changing live; a committed-journal exception needs explicit phase-aware recovery.
- [ ] After an authorized live update, verify the changed workflow, login/files, account isolation, app/worker cleanup, unrelated sites and disk headroom. Capture truthful evidence and update guides/status; clean test files/accounts only by exact ownership, and leave no unnecessary old releases or build artifacts.
- [ ] Use independent worktrees/branches for parallel app, CAD, storage and validation work. Assign each agent concrete files, scope, tests and a no-overwrite rule. Integrate tested slices promptly, resolve actual conflicts deliberately, and back source/notes up to box-git. Never send data to GitHub while its remote is removed.
- [ ] Speed up through reusable fixtures, common app services, incremental hashing/sync, shared protocol test vectors, caching with correct invalidation, small representative designs, and parallel work that does not contend for heavy builds. Optimize measured bottlenecks without replacing the user's end goal with a permanently narrow special case.
- [ ] Re-evaluate the sequence as evidence improves. Keep this full list, the actual app inventory, deferred third-party features and specific acceptance examples current. An agent must stop and report a genuine external blocker; it must not declare the program finished merely because a single slice works.

## 15. Agent and subagent execution plan

### How to split the work

Use one integration lead and as many workers as are useful. A worker can delegate its own **non-overlapping** subtask when its tools and instructions permit. Smaller models should receive one bounded task with specific files, tests and expected output—not the whole program and a vague instruction to finish it. The lead remains responsible for the complete user-visible result, resolving conflicts, checking source and test evidence, and integrating approved, qualified work. The following lanes are opportunities for parallelism, not a requirement to start all tasks at once.

1. **Storage protocol lane:** one owner specifies/version-controls the chunk manifest, IDs, upload/download operations, integrity and compatibility test vectors. Subagents may separately investigate chunk boundary algorithms, adversarial behavior and protocol tests. Nobody changes production HTTP behavior until the contract is agreed in the candidate branch.
2. **Server storage lane:** implement signed/authorized per-account manifest/chunk operations, private staging, filesystem publication and recovery under the protocol contract. Delegate fault-injection/GC tests independently. Own `active-system/gateway_service/` and any necessary server release/operator files in a dedicated worktree. Coordinate exact shared interfaces with the protocol owner; never replace the production `user_store.py` with unfinished research wholesale.
3. **Browser storage lane:** implement persistent verified chunks/manifests, incremental hashing, bounded workers, download/upload, multi-tab locking, cancellation and conflict UX against the same protocol. Own `active-system/storage/browser/` and the browser gateway client; coordinate any edits to the shared client with the server owner. Delegate phone/memory and two-device tests.
4. **Storage integration/release lane:** merge protocol, server and browser candidates in an isolated integration branch; run real signed two-account, 104/128 MiB, inserted-byte, crash/recovery and simultaneous-tab tests. Independently inspect authorization, update/rollback and data integrity. The lead—or one designated operator—prepares and applies the managed live release after gates pass; do not have several agents changing server config at once.
5. **App lanes:** assign one app or tightly coupled group per worker, such as Files; Text; documents/PDF; spreadsheet/data; notebooks; image; audio; diagrams; electronics; fabrication; games. Each owns its `apps/system/<app>/` or `apps/games/<group>/<app>/` and app-specific tests/docs. A worker proposes changes to shared desktop services through the lead rather than editing the same shared file concurrently. Prioritize complete user workflows and real problems found during use.
6. **Desktop host lane:** one owner handles `active-system/app.js`, launcher/taskbar/workspaces, common file dialogs, application lifecycle, CSP and cross-app services. Other app agents request small interface changes with an example and test; the host owner integrates them and runs regression tests. Do not create a second desktop architecture for each app.
7. **CAD solver lane:** in the JSKetcher repository, qualify midpoint/constraint semantics, atomic failed admission, deterministic priority, parameters and persistent references. Independent reviewers add counterexamples and actual sketch/save/undo tests. Keep conflicting or slow research variants off the integration branch until proven.
8. **3MF geometry lane:** own model-derived tessellation, units/transforms, topology/mesh validation, core package writer and independent lib3mf/other-reader tests. One subagent may work on OCC and another on Native Mesh, but neither may claim support for the other's unsupported operations or substitute display meshes. Handle shared material-interface/contact uncertainty explicitly.
9. **Manufacturing-document lane:** own native project metadata for material identities, independent appearance, authored print objects/regions, grouping, placement and revision, with safe rebinding after edits. Coordinate a versioned contract with the geometry and desktop-host owners. Test actual save/reopen, current account, concurrent edits and split/merge ambiguity.
10. **Enclosure integration lane:** merge CAD, manufacturing metadata, file-host and 3MF work; implement the real enclosure/separate lid/grouped label workflow. Verify parameter changes and native My files save/reopen, then independently inspect core 3MF. Do not substitute a hard-coded rectangular-pocket exception for general interference handling. Bambu/real print are optional.
11. **Physical model and solver lanes, later:** separately design versioned physical-system/material/interface/study models and qualify actual Gmsh/Elmer/GetDP runtimes. Integrate only after a reproducible forward model and reference tests exist. The magnetic-fixture lane combines these with a bounded search and independent final reanalysis; do not start by claiming all physics or global optimization works.
12. **Cross-cutting QA/security lane:** review other workers' exact code/artifacts rather than trusting their summary. Add adversarial inputs, account isolation, interruption, concurrency, resource and lifecycle tests. Identify what is proven vs simulated vs unknown; independently test a representative end-to-end workflow before release. Report a concrete reproducer when a gate fails.
13. **Documentation/inventory lane:** maintain the app table, student guide, deferred provider/AI feature list, source/license notes, implementation decisions and this program. Documentation describes observed state; it never makes an unfinished tool appear complete or blocks independent implementation while waiting for prose.

### Dependency map and safe parallelism

- Storage protocol -> server and browser work **in parallel** -> signed end-to-end integration -> crash-tested rollout. Existing full-file saves remain the safety baseline during development.
- CAD semantic/solver qualification + manufacturing document + geometry extraction can advance **in parallel** behind explicit contracts -> combined native-project/3MF fixture -> real My files enclosure workflow -> independent 3MF verification. A partially working solver is not a reason to hide unsupported geometry.
- Each app worker can improve its own menu, UX, examples and lifecycle while the common file service advances. Integrate to the shared contract and rerun only the affected end-to-end tests after its interfaces change.
- Physical-system data design can proceed alongside 3MF, but reliable solver results and inverse search depend on qualified geometry, assignments, study definitions and reproducible forward models. The first magnetic fixture is a vertical gate, not a promise to implement every physics domain first.
- Tests and implementation for the same feature should run together, not in years-long isolated phases. Use one small golden workflow early and broaden to failures, device sizes and scale as evidence warrants. One project owner chooses which slice matters next and merges compatible work; avoid requiring all agents to wait for every other lane.

### Worktree and branch procedure for another machine

1. Check that the relevant repository/branch and intended base commit actually exist on box-git. Clone or fetch over the authorized LAN connection. Example for the desktop repository: `git clone box-git:/srv/data/git/CodiServer-distro.git codi-desktop`; for CAD: `git clone box-git:/srv/data/git/JSKetcher.git jsketcher`. The clone's `origin` then points to box-git. Do not configure or push a GitHub remote for jSketcher while the user has asked to keep it LAN-only.
2. Fetch and inspect the chosen base with `git fetch origin` and `git log -1 --oneline <base>`. Create a distinct branch/worktree per task, for example `git worktree add -b agent/<task> ../agent-<task> <base>`. Never choose a base solely from an old note; ask the integration lead which candidate contains the latest relevant work when branches differ.
3. Current reference points, **not permanent targets**: desktop `simplified` was `c78b40341`, while live Microduck source was on `research/microduck-desktop-integration-20261102` at `f6cc1ca55`; chunk research was `research/chunk-sync-prototype` at `f2402f81b`. JSKetcher `webos-integration` was `518a4666`; later 3MF, metadata and solver research are separate `research/*` branches. Fetch and recheck before starting; do not assume a live release equals the tip of `simplified`.
4. Read applicable `AGENTS.md`, app docs and test prerequisites. Install dependencies only in the isolated checkout/project environment as needed; user has authorized required installs/downloads. Keep source, manifests and notes in Git; do not commit generated build outputs, caches, private keys, credentials or test account data. Before and after heavyweight builds, inspect free disk/RAM; coordinate a single heavy build slot if resources are tight.
5. Commit focused source/test/doc changes to the task branch and push only that branch to the appropriate box-git repository. Give the lead the exact repository, branch, full commit hash and parent/base. The lead reviews and merges/cherry-picks into an integration worktree, resolves actual conflicts, reruns combined tests and backs up the resulting branch. Do not force-push or rewrite unrelated branches.

### A precise task template for any model

Give each worker this filled-in brief:

```text
Task: <one observable outcome>
Repository and box-git branch/base SHA: <exact values>
Owned paths: <app/service and tests; list shared files requiring coordination>
Inputs and current evidence: <source paths, known behavior, fixture>
Must preserve: <account data, APIs, other apps, version/conflict semantics>
Implement: <concrete changes and user-visible workflow>
Tests: <exact scenarios, actual browser/server/device boundaries, limits>
Not in scope: <explicit deferred work, e.g. no live deploy or no provider>
Done when: <observable end-to-end result and required evidence>
Return: <commit SHA, branch, files, commands, results, failures, limitations>
```

The worker should inspect the real code, run a bounded failing reproduction where appropriate, implement the change, test its actual behavior, document remaining limits and commit. If a test cannot run, report exactly why and continue independent work; do not invent success. A worker may make ordinary choices, install authorized dependencies and use synthetic accounts in its isolated fixture. It must not delete unrelated data, publish externally, alter a shared live service or overwrite another worker's uncommitted work unless that specific action is assigned. If live rollout is assigned, follow the already authorized managed workflow and verify it; do not create a new approval ceremony. The lead must not interpret a worker's completion message as proof without inspecting the diff and relevant evidence.

### First assignable work packages

- [ ] **C1 — Chunk specification:** write the versioned bidirectional protocol and browser/server test vectors, including content-defined boundaries, flat-SHA compatibility vs new Merkle roots, account scoping and ABA/version behavior. Deliver spec, reference encoder/decoder and corruption/adversarial tests; no live server changes.
- [ ] **C2 — Chunk server:** build signed per-account stage/read/commit, CAS, bounded storage, leases/GC and crash recovery against C1. Deliver isolated real-gateway tests for two accounts, fsync/rename failures, replay and unchanged-byte transfer; no private data copied into fixtures.
- [ ] **C3 — Chunk browser:** implement the matching IndexedDB cache, incremental hash/reuse, changed-only upload/download, two-tab and cancellation handling. Deliver Chromium real-account and memory tests for edits, insertion, conflict, cache eviction and fresh-device recovery.
- [ ] **C4 — Storage integration:** combine C1–C3; compare exact files and transferred bytes for 104 MiB/128 MiB cases, concurrent accounts, slow disk and interrupted/lost-acknowledgment recovery. Prepare managed operator upgrade/rollback against the **current** live worker; report any unqualified case before rollout.
- [ ] **A1…An — One app each:** choose an app from the current inventory; open/edit/save/reopen with My files; integrate its own file menu, suppress unwanted account flows, test touch/desktop and repeated disposal, and document real limitations. Each agent owns only its app-specific source/tests; shared-service changes route through the host lane.
- [ ] **M1 — CAD constraints:** start from actual JSKetcher integration candidate and the saved midpoint/cascade regressions. Make the corrected equations, rejection atomicity and save/reopen branch behavior correct, with rank/degeneracy warnings and bounded performance; no live release based on a single passing synthetic example.
- [ ] **M2 — Native manufacturing model:** implement versioned units, region/material/appearance identity, authored object grouping, transforms and revision; verify parameter edits, stale/split/merge behavior and real native project save/reopen. Do not pretend reconstructed face IDs are stable without evidence.
- [ ] **M3 — Geometry and 3MF:** obtain current model geometry at requested tolerance, validate supported solids/interfaces, write core 3MF and independently read it. Test separate build objects and grouped multiple-material regions, cavity/holes/curves, invalid meshes and cancellation; do not silently weld distinct nearby surfaces.
- [ ] **M4 — Enclosure vertical slice:** integrate M1–M3 with desktop/My files; build, edit and reopen the real enclosure/lid/label design, then export and independently verify the two-object 3MF. No Bambu or physical printer required. Record unsupported cases honestly.
- [ ] **P1 — Physical document:** define regions, evidence-backed materials, orientations, interfaces, conditions, studies and revision/provenance without claiming a solver exists. Use the same operations and authorization for people and agents.
- [ ] **P2 — Magnetic fixture:** after a qualified mesher and forward solver exist, implement the explicit bounded sensor-fixture study/search/reanalysis acceptance in section 12. Test known references and convergence; unknown data or failed solves are not valid candidates.
