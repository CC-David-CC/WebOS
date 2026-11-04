# WebOS: separate work silos

Planning decomposition, 2026-11-03. Development remains paused. This document
organizes the existing program; it does not start new work or declare a release.
Use `WEBOS-WORK-QUEUES.md` for the complete acceptance criteria and current
ledger, and `HANDOFF-STORAGE-BETA-2026-11-02.md` for the stopping point.
Statuses below describe that saved checkpoint, not a new live audit.

The sortable planning matrix is `docs/planning/SILO-MATRIX.html`, with Markdown,
CSV and JSON versions beside it. It estimates remaining implementation/proof
effort and coarse done/partial shares for each app/domain separately. These
are planning judgements, not acceptance evidence or a program completion score.

## Rules for keeping the silos separate

Each silo gets its own branch, owner, ordered checklist, tests and finish line.
An application owner owns that application, not a second file service. A solver
owner does not redesign desktop menus. An exporter does not redefine materials.
Shared contracts are agreed explicitly; the integration owner serializes shared
files and deployment. Independent work can continue behind those contracts.

The common application acceptance is Open/create → use/edit → save to My files
→ close → reopen, with two accounts, independent windows, cancellation and
phone/1080p/4K checks. Its own menus expose file actions; vendor accounts and
provider prompts are suppressed where requested; missing features stay listed
honestly. This common acceptance is repeated for each app, not one combined app
task. Do not treat a mock storage test as real signed-account integration.

## S01 — Account identity and permissions

Owns registration, credentials, signed identity, sessions, account IDs and
authorization. Existing beta registration/isolation workflows passed; full
recovery, classroom concurrency and session qualification remain partial.

1. Verify registration/login and the user's username/password rules.
2. Verify expiration, revocation, recovery and account changes.
3. Bind account IDs, permission records and authorized document operations.
4. Test forgery/replay, concurrent sessions, 10–30 sign-ins and honest failures.

Finish line: authenticated identity and permissions behave predictably across
services and sessions. It does not own file bytes or application UI.

## S02 — Local durable browser files

Owns account-scoped OPFS/IndexedDB data, verified generations, publication,
local versions, cleanup, quota/eviction and bounded worker processing. Latest
research checkpoint is `796a10f6`; it is not the desktop's deployed store.

1. Preserve committed bytes through local edits, worker failure and cancellation.
2. Publish verified generations with stale-version checks; keep recovery metadata.
3. Clean only eligible staged orphans; protect live writers and published data.
4. Qualify multiple tabs, account invalidation, crash points, quota and memory.
5. Provide the agreed Blob/stream/version interface to desktop and sync callers.

Finish line: a dependable local file store under documented limits. It does not
own the server, network protocol, application-specific formats or a general
claim of power-loss atomicity. Same-origin namespace separation is not a
security boundary against hostile same-origin code.

## S03 — Server file store

Owns account disk files, filesystem publication, permission checks, staging,
quotas, version checks, restart recovery and temporary-disk accounting. Beta
has tested operations; arbitrary host writers and global resource guarantees
remain outside what was proved.

1. Qualify account/path/permission boundaries and malformed requests.
2. Publish complete verified writes while preserving the prior file on failure.
3. Report uncertain post-publication outcomes truthfully.
4. Qualify rename/delete/folder operations separately; never assume atomicity.
5. Test restart, disk full, concurrent writers and resource reservations.

Finish line: a reliable server-side file contract. It does not own browser
cache layout, application editors or format-aware CAD changes.

## S04 — Synchronization and transfer protocol

Owns how S02 and S03 exchange versions and bytes. It may work on server and
browser implementations in parallel after its contract is agreed. Beta has a
working changed-chunk path; the complete capacity/memory gate is still open.

1. Define version/hash meaning, account/path binding, limits and test vectors.
2. Implement first/no-op/changed upload and download; measure byte changes,
   insertions and deletions, preserving exact final content.
3. Preserve conflicts; reconcile attempted writes after uncertain replies.
4. Handle retries, missing/corrupt chunks, cancellation, cache eviction and devices.
5. Qualify pacing, batching, 128 MiB and concurrent accounts without blind write
   replay or unbounded hashing/RAM/disk work.
6. Add optional format-aware adapters only where their reconstruction is sound.

Finish line: eventual convergence or explicit conflict without losing saved
versions. Network byte savings do not imply changed-block-only disk writes.

## S05 — Desktop shell and window experience

Owns window/workspace placement, taskbar, launcher, focus, responsive layout,
clock, settings and user-facing desktop interactions. Existing shell is usable;
individual lifecycle and device behaviors remain to qualify.

1. Correct focus, minimize/restore, multiple windows and workspace independence.
2. Practical phone fullscreen, ordinary desktop tiling and large-display layouts.
3. Consistent menus, themed dialogs, keyboard/touch and resize behavior.
4. Restore intentionally saved state and present honest network/maintenance status.

Finish line: predictable desktop behavior. It does not own each app's internal
toolbars or a separate document persistence implementation.

## S06 — Shared application host, lifecycle and commands

Owns mount/dispose, session-bound operations, shared file dialogs and typed
commands used by people and agents. Scoped fixes exist; logout/account-switch
and whole-desktop qualification remain partial.

1. Define one host contract for files, dialogs, commands and operation ownership.
2. Cancel/stale-reject asynchronous work on disposal or account change.
3. Preserve pending saves and clearly distinguish cancelled versus uncertain writes.
4. Test repeated open/close, simultaneous windows and shared resource cleanup.
5. Expose validated per-app commands with revision/permission checks; external
   agent transport is a separate authorized feature.

Finish line: apps can use the same services safely without implementing their
own accounts/storage. It does not implement a CAD solver or editor engine.

## S07 — Browser Python Notebook

Owns JupyterLite/Pyodide, notebook working models, script formats, widgets and
its phone/desktop UI. A stale saved-working-file risk was reproduced; RAM-only
and version-aware research exists but is not fully qualified.

1. Protect already-saved working files from stale handles and multiple windows.
2. Keep transient outputs/counts in RAM; default to metadata-free `py:light`.
3. Qualify `py:percent`, explicit `.ipynb`, code/Markdown round-trip and widgets.
4. Test image/chart rendering, independent kernels, packages and cleanup.
5. Provide minimal phone UI while retaining useful split views on large screens.

Finish line: a student can write/run/save/reopen scripts without output-only
changes resyncing source or one window silently overwriting another.

## S08 — Browser Linux, terminal and Linux Notebook

Owns the resettable v86 guest, shell sessions, xterm behavior and optional
guest-backed notebook execution. Test terminal and notebook as separate apps.

1. Qualify independent shells, xterm interaction, touch scrolling and key controls.
2. Keep Linux files temporary; Files may expose the guest home for exploration.
3. Demonstrate Python subprocesses, executable/package tools and POSIX behavior.
4. Qualify authenticated networking/SSH policy and destination-only audit records
   where enabled; beta guest Internet is currently disabled.
5. Test reset, crashes, guest/kernel teardown and supported notebook transport.

Finish line: honest usable Linux capabilities, distinct from the saved account
drive. Linux guest data must not become a hidden mirror of My files.

## S09 — Individual applications: one assignment per app

Every row below is its own silo. The numbered steps are an app's sequence,
followed by the common acceptance at the top. These are planned acceptance
tasks, not a claim that every row is unstarted or every listed engine is live.
Use that app's actual README and source to select its next bounded task.

| App silo | Ordered app-specific work |
|---|---|
| Files | 1. Create/open/navigation. 2. Rename/move/copy/delete. 3. Upload/download/drag upload. 4. Conflicts, server changes and temporary Linux-home visibility. |
| Text | 1. Open/edit/encoding. 2. Revision-safe save. 3. Large-file behavior. 4. Phone selection and editor disposal. |
| Calculator | 1. Calculations/history. 2. Its supported file workflow. 3. Pending-operation close/account changes. 4. Touch/accessibility. |
| Help | 1. Truthful service/help content. 2. Usable navigation. 3. Accessibility. 4. Keep guidance aligned with actual features. |
| Doc | 1. Report editing/layout. 2. Native save/reopen. 3. PDF export/Unicode. 4. Failure/conflict and print-layout checks. |
| Spreadsheet | 1. CSV/TSV import. 2. Supported formulas/editing. 3. Correct export. 4. Large files/cells and memory; XLSX is not required. |
| PDF Viewer | 1. My files open. 2. Navigation/search/text. 3. Password/large-document behavior. 4. Worker cleanup and explicit scan/OCR limits. |
| Data Explorer | 1. Import/schema. 2. Query/pivot/chart. 3. Export/reproduce. 4. Exact integers, bad data and memory. |
| Image Editor | 1. Open/edit. 2. Conflict-safe native/export save. 3. Format/animation/metadata limits. 4. Low-copy image and URL cleanup. |
| Audio Editor | 1. Open/record where supported. 2. Edit/preview. 3. Export supported codecs/channels. 4. Independent windows and audio cleanup. |
| diagrams.net | 1. Own file menu/My files. 2. Edit/save/reopen. 3. Provider/account suppression. 4. Touch and native-format recovery. |
| Excalidraw | 1. Own file actions. 2. Edit/save/reopen. 3. Stale chooser/account handling. 4. Touch and multi-window cleanup. |
| SVG Editor | 1. Safe SVG open. 2. Edit/save. 3. Complex/unsupported SVG handling. 4. Touch and external-resource restrictions. |
| Embroidery Studio | 1. Local artwork/project. 2. Thread/hoop/preview. 3. Native and supported stitch exports. 4. Format validation and removed-provider feature list. |
| Stitch Converter | 1. Read supported machine formats. 2. Inspect conversion. 3. Save output. 4. Preserve units/stitches and report unsupported information. |
| Arduino Simulator | 1. Known compiled firmware. 2. GPIO/timers/UART examples. 3. Source/firmware/project saves. 4. Compiler benchmarks and emulation limits. |
| Pico Simulator | 1. Supported real firmware. 2. Serial/GPIO examples. 3. Simulated flash/reset and project saves. 4. Peripheral and fidelity limits. |
| Digital Logic | 1. Correct example/netlist. 2. Run/inspect logic. 3. Save/reopen. 4. Timing/supported-component and lifecycle tests. |
| Circuit Simulator | 1. Known circuit. 2. Solver/waveform behavior. 3. Save/reopen/results. 4. Reference cases and unsupported models. |
| Circuit Lab | 1. Supported schematic workflow. 2. Electrical simulation/results. 3. Project files. 4. Component/solver coverage and failures. |
| PCB Design | 1. Supported design input. 2. Placement/routing. 3. Manufacturing exports. 4. Independent structural checks. |
| Electronics Design | 1. Consistent breadboard/schematic/PCB representations. 2. Side-by-side desktop views. 3. Minimal phone UI. 4. Project and export correctness. |
| Replicad | 1. Script/model editing. 2. Regeneration/errors. 3. Native/geometry saves. 4. Heavy-engine lifecycle and unsupported cases. |
| Mesh:Tool | 1. Mesh import. 2. Supported edits. 3. Export. 4. Topology, cancellation and resource use. |
| Kiri:Moto | 1. Supported model/mode. 2. Setup/toolpaths. 3. Saved project/output. 4. Independent preview checks and machine limitations. |
| G-code Preview | 1. Read supported G-code. 2. Inspect paths. 3. File workflow. 4. Session guards, large-file workers and interpretation limits. |
| Microduck | 1. Controls/examples. 2. Saved project/reopen. 3. Runner disposal and phone UI. 4. Supported model/reference behavior and honest simulation limits. |
| Browser | 1. Document existing experimental renderer. 2. Relay/file access. 3. Enforce network policy. 4. Qualify only supported sites; lowest priority. |
| Each game preview | 1. Rules/full playthrough. 2. Controls/pause/audio. 3. Account save where applicable. 4. Multiple windows/touch. Preserve groupings; XR and unfinished learning interfaces are separate gates. |
| Each requested additional app | 1. Verify real source/runtime/license. 2. Define useful local workflow. 3. Integrate shared files. 4. Test its own lifecycle/device behavior. Inventory photos, media, books, news, maps and later apps individually. |

## S10 — Shared runtime libraries

Owns capabilities such as CodeMirror, ffmpeg, ZIP, Mermaid, chart libraries,
OpenCascade, AI runtimes and optional networking libraries. Each library has
its own packaging task; a disabled menu entry is not a user-facing app.

1. Inventory actual pinned source/runtime, license and reproducible build.
2. Provide lazy-loaded versioned resources and an explicit consumer contract.
3. Test worker/resource ownership and cleanup with one real consumer.
4. Keep unconfigured AI/provider features deferred; do not invent a backend.

Finish line: reusable tested capability. It does not own all consuming apps.

## J01 — JSketcher upstream feature integration

Owns reconciling carried-forward upstream features. See
`docs/JSKETCHER_UPSTREAM_WORK.md`; recheck actual refs before implementation.

1. Map main/dev/surfacing changes and PRs to coherent independent features.
2. Qualify polynomial fixes, spline tools, history/redo, selection and cancellation.
3. Qualify DXF, camera/touch, IDs and model reconstruction.
4. Replace upstream autosave assumptions with the agreed host file service.
5. Test every carried feature individually and in the combined Chromium app.

Finish line: a coherent fork with attributable tested features. It does not
claim solver robustness or manufacturing validity just from a successful merge.

## J02 — JSketcher constraints and parametric modeling

Owns the mechanical CAD upgrade. Authoritative detailed roadmap is
`docs/MECHANICAL-CAD-AUDIT.md` in the JSKetcher repository's
`research/mechanical-constraints-audit` branch.

1. Correct semantics/atomic constraint admission, midpoint, conflict/redundancy,
   numerical failure and persistence without changing geometry on rejection.
2. Add ordinary mechanical dimensions/relations, entity fix, rigid groups and
   axis symmetry; test a bracket and enclosure/lid.
3. Add typed parameters, dependency errors, reference/driving roles and configurations.
4. Qualify feature history/regeneration and repair of broken topology references.
5. Add advanced curves and continuity only after the mechanical foundation.
6. Leave mechanisms as J09 rather than quietly expanding this assignment.

Finish line: predictable editable mechanical designs under documented limits.
Constraint rejection/save-reload order and solver performance remain known gates.

## J03 — Geometry engines and build provenance

Owns OCC and Native Mesh capability boundaries, WASM builds, source/license
provenance, tolerances, topology and resource behavior. See
`docs/JSKETCHER_ENGINE_COMPARISON.md`.

1. Reproduce/distribute pinned runtimes under required notices and CSP.
2. Publish each engine's actual supported operations; no hidden substitution.
3. Test analytic primitives, booleans, curves, degeneracy, scale and persistence.
4. Qualify model-derived tessellation and stable authored/generated references.

Finish line: supported geometry is trustworthy within its stated scope. Engines
do not need identical answers, but differences/limits must be attributable.

## J04 — Native manufacturing document

Owns durable parts/regions, material identities, independent appearance,
placement, grouping and design revision in the editable native project.

1. Define versioned authored metadata independent from render meshes.
2. Distinguish a multi-region print object from separate print objects.
3. Preserve bindings through ordinary regeneration or flag split/merge ambiguity.
4. Test undo, save/reopen and parameter edits without inferring material from color.

Finish line: editable manufacturing intent survives the tested design changes.
It does not require physical property data, a slicer or a printer.

## J05 — Core 3MF exporter and validator

Owns manufacturing handoff from a specific revision, not the editable project.

1. Consume J03 geometry at explicit units/tessellation tolerance and J04 metadata.
2. Validate geometry, orientation, hierarchy, placement and material regions.
3. Write bounded cancellable core 3MF with build objects/components/resources.
4. Independently read and verify output; fail explicitly for invalid or uncertain
   contact/interference instead of emitting plausible unsupported results.

Finish line: supported models export correctly with independent validation.
Two disjoint boxes have scoped research evidence; the general enclosure does
not. Bambu projects, filament presets and real printing are optional.

## J06 — CAD application integration

Owns embedding the fork as a desktop app, not CAD mathematics or material models.

1. Mount isolated instances and render under actual CSP with app-owned resources.
2. Use My files and preserve account/revision boundaries and pending edits.
3. Expose the same validated domain commands to UI and authorized agents.
4. Qualify phone essentials, useful 1080p/4K panels, camera/touch and disposal.

Finish line: qualified CAD functions feel native to the desktop and save/reopen
through the common services. It depends on those services for release, not for
all isolated UI investigation.

## J07 — Enclosure acceptance project

This is a cross-silo integration test, not another geometry implementation.

1. Author parametric body, separately printable lid and aligned inset label.
2. Assign persistent parts/materials and deliberately group the label with the lid.
3. Change width/wall thickness, undo, save/sync and reopen the native project.
4. Export and independently validate core 3MF with two build objects and three
   assigned regions, correct scale/placement and explicit unsupported failures.

Finish line: one complete dependable mechanical/manufacturing workflow. Needs
J02–J06 capabilities relevant to this model and the qualified file contract;
does not require every future CAD feature or real printing.

## J08 — Advanced curves

1. Qualify ellipse/curve incidence, normals and path/arc length.
2. Qualify tangent directions, G0/G1/G2 and parameter versus arc-length fractions.
3. Add associative projection/intersection/pierce and explicit reference repair.
4. Prove a curved handle/cover through large edits and save/reopen/export.

Finish line: that supported curved-profile workflow, not every surfacing method.

## J09 — Assemblies and mechanisms

1. Persist instances, component transforms and durable references.
2. Qualify fixed, revolute, slider, cylindrical, planar and spherical relations.
3. Add limits/couplings and solve a linkage/slider through its intended motion.
4. Treat collision, dynamics and manufacturing clearances as separate extensions.

Finish line: a mechanism retains its intended mobility and survives reopening.
This follows dependable parts and assembly persistence, not OPFS internals.

## P01 — Physical-system document and material evidence

1. Define meaningful regions, material assignments/orientations and interfaces.
2. Define sourced physical properties, units, ranges, uncertainty and unknowns.
3. Persist operating conditions, study definitions and design requirements.
4. Track revisions/dependencies and use the same operations for UI and agents.

Finish line: an authored study has explicit meaning; no claim a solver exists.
Its schema can be designed in parallel with manufacturing metadata, without
requiring physical properties for the core 3MF milestone.

## P02 — Meshing

1. Qualify an actual supported mesher/runtime and license/distribution.
2. Derive a tagged mesh from revisioned geometry/regions/boundaries.
3. Test element quality, scale, surrounding domain, refinement and cancellation.
4. Preserve provenance and refuse unresolved assignments.

Finish line: a repeatable numerical mesh with attributable regions, not merely
a display tessellation. Consumes J03/P01 contracts.

## P03 — Forward solver integrations

Each solver/formulation is its own bounded task; do not assign all multiphysics
as one feature. Gmsh/Elmer/GetDP candidates require actual runnable integration.

1. Select supported physics and explicit assumptions/conditions/material laws.
2. Run a trusted analytical or numerical benchmark with attributable inputs.
3. Qualify convergence, mesh sensitivity, resource bounds and failures.
4. Persist results/provenance and mark stale or failed results accurately.

Finish line: one qualified forward study. Physical form finding and coupled
studies require their own acceptance; a plot is not validation.

## P04 — Magnetic design search

1. Specify a sensor fixture, sensing region, operating range and package limits.
2. Use a small evidence-backed catalogue and qualified forward formulation.
3. Search only declared dimensions/materials/orientations under bounded resources.
4. Regenerate a selected manufacturable result and independently reanalyze it.

Finish line: a reproducible better feasible candidate under stated assumptions.
Depends on a qualified forward study, not a universal multiphysics platform.
Never optimize arbitrary unrelated property sliders into a fictitious material.

## O01 — Hosting, release and recovery

1. Keep beta/main identities, data and assets separate with exact inventories.
2. Qualify service-worker/old-tab compatibility, staging, interruption and recovery.
3. Promote scoped releases while preserving committed files and the guarded floor.
4. Verify sites, service identities, disk and authentic workflows after change.
5. Design main promotion from its actual then-current state; never transplant beta data.

Finish line: repeatable deployment/recovery for a specified transition. It does
not own feature implementation or prove all release versions interchangeable.

## O02 — Independent qualification

1. Review exact commits/artifacts independently of implementation summaries.
2. Reproduce races, malformed data, permission errors and interruption boundaries.
3. Measure physical phone behavior, 128 MiB, slow clients, classroom login and
   roughly 100-user capacity in separately bounded tests.
4. Distinguish viewport emulation, injected stalls, local TCP cuts, process crash,
   real WAN and power loss. Return concrete failures to the owning silo.

Finish line: evidence for the selected milestone; no synthetic global completion
percentage. A QA owner does not unilaterally change shared production services.

## O03 — Reproducibility, inventory and student guidance

1. Keep source, tests, runtime inputs, notices and dependency/build recipes backed up.
2. Qualify checkout/build on a clean other machine; tracked refs alone are insufficient.
3. Maintain per-app status, a plain student guide and deferred provider-feature list.
4. Maintain task handoffs and exact references; keep credentials/data out of source.

Finish line: another authorized developer can reproduce the stated supported
workflow with documented dependencies and access, without this workstation.

## Parallel paths and required joins

| Parallel path | Work that can proceed | Where it must join |
|---|---|---|
| Files | S01–S04 after agreeing account/version/file contracts | Real signed browser/server workflow and desktop integration |
| Desktop/apps | S05/S06, S07/S08 and any individual S09 app | Shared file/session/lifecycle acceptance before release |
| CAD | J01/J02, J03, J04 and isolated J06 UI | J05 supported export, then J07 enclosure |
| Future studies | P01 schema and mesher/solver feasibility | Qualified geometry + tagged mesh + forward benchmark before P04 |
| Operations/QA/docs | O01–O03 alongside selected features | Independent release evidence; one designated deployment owner |

Select bounded tasks, not every silo at once. Current priority remains storage
qualification; independent app/CAD investigation may proceed without taking
over common files. Do not make the storage owner responsible for every app,
or block a solver-mathematics test on an unrelated desktop migration.

## What to resume first

1. S02/S04: integrate the tested OPFS experiment through the agreed file contract,
   preserving saved/pending/conflicting versions and measuring real memory.
2. S03/O02: qualify server limits, concurrency and recovery using the same contract.
3. S06/S07: close the session/notebook saved-data gaps without another storage stack.
4. If more independent agents are available, choose one S09 app or one bounded
   J02/J03/J04 task. These need separate owned paths and an explicit acceptance.
5. Converge through integration/review/beta; promote to main only after that scope
   passes its recovery and compatibility gates. Leave unrelated future silos open.
