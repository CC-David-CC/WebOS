# CAD core separation and implementation checklist

Active direction, 2026-11-04. The user authorizes using JSketcher as inspiration
and replacing coupled internals where needed. Preserve useful tested components;
the goal is an engineering engine that can grow through the recorded CAD gates,
not just a collection of upstream patches. The user explicitly favors worker
silos without a canvas or fake browser UI, and authorizes extending this
checklist when implementation exposes further core requirements. Every added
requirement needs an observable acceptance test and a bounded owner/package.

The latest user clarification makes **every JSketcher feature suspect**.
Treat the upstream implementation as reference/inspiration. Preserve or reuse
code only after its explicit semantics and independent acceptance tests earn
that choice; there is no requirement to retain an incorrect inherited behavior
or preserve the old architecture. Our fork's existing tests also confer only
their recorded scope, not trust in adjacent features. Future-layer interfaces
inform the core now, while unimplemented physics/features remain visibly deferred.

This refines `goals/FILES-JSKETCHER-RELEASE-20261103.txt`. Maintain status in
`WEBOS-WORK-QUEUES.md` and `ACTIVE-FILES-CAD-RELEASE.md`. The larger feature
program and handoffs remain in `CAD-ENGINE-GATES.md` and
`CAD-ENGINE-END-TO-END.md`. Later physics, autonomous design and XR inform the
contracts below but remain queued. No complete Files or CAD gate is declared
passed by this architectural decision.

## Current checkpoint — shared Worker dimensions and R11 integration, 2026-11-05

**Files remains accepted within its recorded scope; full CAD1/Gate1 and CAD2 remain open.** The [qualification ledger](evidence/CAD1-GATE-LEDGER-2026-11-05.md) separates the full gate from bounded drawing, parametric and native-file passes. Root combined runtime607b1ea42 (private direct20614) integrates Worker signed X/Y/projected dimensions and exact planar display preparation. Root production-browser controls pass signed dimensions, live datum edits, refusal/cancellation, exact travel/native reopen (74 main-phase Workers terminated) and13 plane/corner cases with extension fallbacks and selection. CAD test/combined-r11 holds these matching receipts. App88d65535, sketch Worker9fa5dd2f, project validator134e945d. No public deployment or default change.

Signed host20394 independently passes the public signed-distance route through Save/server sync, another-account denial, fresh Files reopen, real Open/Close cancellation and late-reply recovery; [receipt](../test/agent-cad-corpus/signed-distance/signed-r2-receipt.json). Its signed-distance-only appd79b runtime has the same numerical Worker, but predates the new plane rendering optimization. Root combined signed host20395 now also passes those controls using the exact R11 app88d65535 and matching Workers; [combined signed receipt](../test/agent-cad-corpus/signed-distance/signed-r11-receipt.json) includes authenticated served-byte pins. No public deployment. Prior R10 numeric-source/Script and native Arc/DXF scopes retain their exact pins and proofs; they do not qualify every command. Initial numeric formula bindings in that lane remain labeled native seeds.

The plane display optimization retains all2,000 models/history/views while avoiding2,000 temporary display NURBS allocations. Its separately pinned full-restore comparison measures sibling gaps311/291ms→267/261ms, not a hard general latency guarantee. ARC25 remains partial, including first full rendering cost. New signed-distance validation recomputes a bounded private candidate in a separate disposable Worker before replay; this binds native bytes/intent but adds measured Worker wall time. No claim of all active-editor processing being off the main thread.

Collinear now passes the actual Worker core and signed host20396 with app91c921bb: consumed construction geometry, signed X/Y/projected dimensions, duplicate no-op, contradiction/refusal, exact travel, genuine Open/Close cancellation and late-reply recovery, Save/server sync, account denial and fresh Files reopen. See [scoped Collinear evidence](../test/agent-cad-corpus/line-relations/README.md). Independent-axis symmetry is next in its own bounded core lane; this public adapter still refuses it. Existing UI mathematics is reused, while legacy active-editor processing remains outside these Worker proofs. General regions, broader primitives/constraints, typed/reference dimensions, persistent references, the full original-rectangle chain and remaining Gate1 exercises stay queued. Final delivery/beta follows functional qualification; source packaging remains deferred.

NVIDIA findings/fixes remain separate LAN-only issue branches, with no application kernel rollout or GitHub push: transform tolerances, mirror analytic types, sampled coincidence tuples, UV-metric validation and sphere pole/seam tessellation. CAD docs/AGENT-CAD-ISSUES.md records their separate evidence and limitations. The latter investigations are not substitutes for CAD1 qualification. Earlier checkpoint scopes below remain historical evidence.

## Current bounded Worker-first follow-up — 2026-11-05

The many-constraint test in CAD `test/capture-concurrency/README.md` now gives a concrete ARC06 blocker. In an actual pinned a9daf Chrome app, 514 segments/512 accepted locks occupy139,364 serialized bytes but LengthRelation admission and undo/redo take roughly515/676/767ms. Sampled stacks include synchronous solver reconstruction plus redraw. The separately measured one/two-sketch project capture is about10–14ms. Moving only JSON capture would leave the measured stall. A separate CAD browser context stayed responsive; this is not proof that all windows in one desktop renderer do.

| Package | Ordered outcome | Owner / dependency | Current evidence |
| --- | --- | --- | --- |
| ARC17 | Preserve and reproduce the actual many-constraint counterexample, profile and bounded resource observations. | Resource lane, before choosing a fix. | [x] CAD ed87ef7ec, actual pinned app/profile/receipt. No implementation claim. |
| ARC18 | Data-only candidate sketch transitions and validated native history replay in a disposable Worker, sharing the same LengthRelation admission semantics as UI. | Core lane plus pure operation owner; parallel with caller design. | [x] Bounded replay/LengthRelation core and shared admission helper integrated, independently reviewed and real-Worker tested; shape policy and missing-hint limitations explicit. No DOM/canvas/fake editor/window or ToolManager. This does not close live publication or all mechanical commands. |
| ARC19 | Revision/lifetime-bound async transport, bounded queue/bytes/deadlines/cancellation and one-use owned result publication. | Lead after ARC18 response contract. | [~] Existing headless lock/deadline/cancel transport now carries immutable transition requests and bounded frozen replies; actual Worker and protocol controls pass, including final-callback cancellation. Live revision/owner publication remains open; a public `validated:true` flag cannot authorize a commit. |
| ARC20 | Hydrate or project an accepted candidate without repeating its heavy numerical solve on the UI thread; measure construction, notifications and repaint separately. | Lead and UI adapter owner after ARC18/19. | [~] Closed-sketch agent results project through private full-history candidate replay without opening the2D viewer (cb4 actual/signed tests). New d177 Worker drawing/selection view, including bounded spline polylines, projects without a main-thread numerical cache. Legacy active2D strict load still solves; tool/cache migration is open. No unvalidated skip-solve/import option. |
| ARC21 | Wire both UI and agent mechanical commands and native undo/redo to that same asynchronous transition, preserving atomic rejection, exact intent and disposal. | Integration, serial after ARC20. | [~] Closed LengthRelation, Concentric, ordinary point edits, Diameter, primitive creation, dependent rectangle dimensions and generic exact-byte journal travel have scoped actual/signed currentness/refusal/close evidence. UI active-editor migration and full operation coverage remain. Callback-owned changes must not be rolled back. |
| ARC22 | Prove the combined path on the measured many-constraint sketch and ordinary bracket/enclosure/File/export workflows, with independent windows and cancellation/fault cases. | Browser/independent review after integration. | [~] Signed closed relationship/resize/refusal/Save and root five-hole/multi-plane regressions pass;53/53 Workers release in the latter. New Worker-view514-segment/512-lock observations pass with limitations recorded; legacy mutation, memory scope, wider acceptance and final beta remain. |
| ARC23 | Detach feature-history input for every asynchronous candidate; bind it to authored revisions and test transient-record ABA separately from stream/key versions. | Core owner; audit all replay/new-feature/direct-pipeline entry points. | [~] 5f8 central owned/frozen history plus pointer capture fixes actual prepared/new-feature/timeline mismatches; all three real-Worker fault comparisons and empty/rewound/native replay pass. Broader raw-input provenance and cooperative comparison conditions remain explicit; immutability is privately branded, not caller-attested. |
| ARC24 | Keep large authoring data out of unbounded main-thread inventory/copy work; preserve incremental revisions and owned immutable data through native/remote input admission. | Core data/transport owner after measured ownership foundation; no fake UI. | [ ] Current cooperative helper avoids a giant canonical string and matches native bounds, but Reflect.ownKeys of a single huge container is synchronous. Measure/container-proof or worker-owned streamed data is required; do not treat cooperative comparison as an atomic lock on arbitrary mutable inputs. |
| ARC25 | Bound revision-owned derived scene/view preparation and drawing independently of authored history size; preserve full model identity/counts with truthful visibility/detail state. | View/worker adapter owner after the measured native replay issue. | [~] Actual2,000-record timeline virtualization preserves all models/history/root and face views, exact travel and selection;22–28 mounted rows and unmount observer/frame controls pass. CAD test/arc25-view-preparation records native software-compositor readback waits and a remaining approximately1.3s sibling gap. Backed readback probes find no application readback calls; browser software compositing explains the native wait, while an isolated composited run still has about340ms JavaScript gaps. Derived-view allocation/publication and broad scene qualification remain open; do not hide/drop authored models or claim hardware-wide latency from software-rendered samples. |
| ARC26 | General selected-region Worker extrusion through the common kernel interface; preserve access to unselected source regions. | Geometry owner; pure planner/kernel first, then lead shared history/discovery integration. | [~] Actual counterexample CAD02447b82f proves two disjoint rectangles are advertised but execution refuses whole-sketch support; Circle/nested regions exist but are not offered. Proposed contract is CAD test/public-region-worker-contract/CONTRACT.md. New OCC generic-profile component is in progress; no replacement or general-extrusion qualification yet. |
| ARC27 | Durable authored constraint identity before broad parameter binding and constraint editing. | Core/model owner after current shared operation; serialize IO/format changes. | [ ] Source ANConstraints.ts assigns Counter-based IDs explicitly for debugging and omits them from write/read. Current stage/index and source revision are scoped handles, not durable constraint identity. Define persisted identity and binding ownership; test add/reorder/remove/recreate, rejected edits, undo/redo, Worker reconstruction and native reopen without silently rebinding a different constraint. No IDs or new format are implemented by this checklist row. |
| ARC28 | Preserve mathematical rejection causes separately from numerical failure and geometry-domain rejection. | Solver owner, with independent diagnostics and lead command-contract review. | [~] Actual feasible live-axis edits expose early fine-solve refusal and a separate collapsed-axis root. Existing admission discards failed solveStatus/domainError and reports the new distance as conflicting. Keep representability, satisfiability, region, kernel and dependency failures distinct. Retain original equations/domain checks and last-valid state; certify algebraic contradictions separately from failed convergence/degeneracy. Current Axis gate remains open. |
| ARC29 | Revoke owned scene animation, controls and renderer on component disposal, including late callbacks and cleanup exceptions. | Presentation-resource owner; independent of numerical core and model authority. | [~] Actual Viewer component disposal in a retained Chromium realm still evaluates controls, schedules frames and can render again; it neither removes controls nor its canvas. Producta36a6b259/evidence71a588c71 passes nine real retained-realm teardown controls, same-container sibling ownership, delivered late callback, injected post-real-cleanup exception,13 plane/selection regressions and full TypeScript check. Full host teardown remains a separate scope. Ordinary host iframe destruction may release that realm; this is not a proved host-window leak or forced-GC claim. Views retain ownership of their own geometry/materials. |


Current427 replay/contour/cancellation evidence is in CAD `test/replay-contour/README.md`; strict index batching and caller cancellation are qualified within that scope. Active2D hydration and large-model view publication remain separate.

The Worker input contract must bound UTF-8 bytes as well as string length, validate native entities/constraints/generators/parameters, preserve saved admission priority and reject unsupported or inconsistent intent. Replay must preserve the requested geometry and authored IDs, constants and relationships; numerical convergence alone is insufficient. Use the existing narrow legacy admission-hint rule rather than relaxing metadata generally. Keep a last-valid accepted state and machine-readable failures; do not silently reverse operands or choose another kernel.

The main-thread adapter retains presentation and bounded input/publication work. It must not redo heavy solver/admission work during hydration. Revision/identity/epoch checks remain necessary; the realm-local epoch alone is not an authoritative mutation inventory. Undo/redo must not move a pointer or discard recovery state until a current validated result is installed. Cancellation closes only the owned job, and other windows retain their accepted state. Native authored snapshots remain authoritative; display meshes, measurements and worker handles remain derived/transient.

ARC18 component tests do not close ARC20–22 or the release. This staged work addresses an observed existing workflow and keeps the original release objective and later CAD1–6 goals intact. No production/backend/default change is authorized by a test pass alone.

## Required boundaries

| Separation | Invariant | Current and future purpose |
|---|---|---|
| Authored document / editor | A revisioned document owns parameters, entities, constraints, selected regions, feature inputs, references and material assignments. Panels, selections and viewports are views/controllers. | Opening or cancelling a view must not change stored intent; batch work must not need an invisible editor. |
| Commands / interface | Humans and agents call the same typed, discoverable operations with permission, expected revision, validation and transaction outcomes. | No agent-only bypass of account, model or rejection checks. |
| Formulas / simultaneous constraints | Typed acyclic formulas evaluate in dependency order; relationships between free geometric unknowns solve together. | Prevent order-dependent measure/set/solve loops and support configurations. |
| Computational core / worker transport | Pure model computation takes explicit data and returns explicit results; a worker adapter provides isolation, transport and lifecycle. | **Production solving requires no canvas, DOM, editor, ToolManager, fake window or fake browser UI.** |
| Geometry / solver / topology / kernel / history | Representability, constraint satisfaction, planar regions, valid feature output and dependency integrity have separate validators and failures. | A valid sketch, valid region, valid solid and meaningful downstream reference are different claims. |
| Persistent intent / generated topology | Authored IDs persist; generated faces/edges use operation provenance and explicit selection semantics. Temporary indices and geometric similarity alone do not prove identity. | Supported edits regenerate; missing, split, merged or ambiguous references require explicit handling. |
| Design / derived representation | B-rep, meshes, render buffers, manufacturing tessellation and analysis meshes declare purpose, units, tolerance, engine and source revision. | Keep two engines useful without competing document authorities or treating previews as verified results. |
| Job / window | Jobs carry unique IDs and captured account/document/input revisions. A controller owns admission, deadlines, cancellation and publication. | Late results cannot alter closed/replaced windows or newer revisions. Future background work requires explicit ownership. |
| Saved files / caches | One account-bound My files service persists files. Immutable content uses leases and worker-based verification/changed-data sync; caches have separate lifetimes. | No app-private account mirrors or synchronization of transient counts/previews on every frame. |
| Results / evidence / decisions | Results identify inputs, method, software, tolerances and validity. Accepting a proposed design revision is a separate transaction. | Stale output, simulation deformation or observations cannot silently replace nominal design. |

The UI may still render to a canvas. Existing rendering and interaction can
remain adapters while computational coupling is removed. A test prototype that
shims a DOM can expose a bug, but is not the qualified production core.

## Bounded packages

`[x]` is complete for the exact scope; `[~]` is partial; `[ ]` is unqualified.
The current checkout and candidate map is in
`HANDOFF-FILES-CAD-2026-11-04.md`; that handoff does not close these gates.

| ID | Package | Owner and order | State / evidence |
|---|---|---|---|
| ARC01 | Record rewrite authority, core boundaries and acceptance in the goal/checklist. | Lead, now. | [x] This document and linked goal/audit amendments; documentation only. |
| ARC02 | Data-only sketch workspace and production worker using actual IO/solver. | Solver owner, parallel with Files and caller. | [~] Integrated through `2b3f2c0f`: actual worker/caller, axis domains and cooperating admission. Lead combined five-hole resize/reopen and invalid-axis controls pass; broader entities remain. |
| ARC03 | Capture immutable sketch/boundary/parameter inputs; solve dependencies and publish only current validated results. | Regeneration owner after ARC02 contract. | [~] Combined five-hole edit/reopen and impossible-edit last-complete preservation pass. Explicit lifetime guards and private replay are implemented; all operations/references remain unqualified. |
| ARC04 | Normalize commands before execution/history and reserve feature identities across edits/replay/cancel/reload. | History changes integrated by lead. | [~] Normalization/feature allocation retained; combined history/deletion/reopen controls pass. Complete shared-agent command workflow remains. |
| ARC05 | Qualify whole-part editing, rejection, undo/redo and reopen through UI and discoverable commands. | Serial after core/caller; then host. | [ ] Full Gate 1 rectangle-edit, bracket and enclosure workflows remain. |
| ARC06 | Migrate remaining editor-dependent computation behind document/command/representation boundaries as workflows require. | Separate bounded follow-ups. | [ ] Direction recorded; no claim all existing operations already meet it. |
| ARC07 | Qualify budgets/cancellation across jobs and windows. | Resource owner plus independent review. | [~] Files admission and 128 MiB controls pass. Integrated CAD admission has owner queue/deadline/cancel/renderer-crash evidence; combined caller tests pass. No total RAM or OS-reclamation claim. |
| ARC08 | Back up exact contracts, source, prerequisites, tests and evidence. | Lead after each reviewed slice. | [~] Ongoing box-git/R730 checkpoints; verify both refs. No GitHub publication. |
| ARC09 | Monotonic document lifetime and current-owner guards across load/reset/restore and async work. | Lead owns project service/manager; callers consume agreed API. | [~] Implemented generation/abort and owner guards. Lead real validator, reset, service replacement, staged cleanup, occupied-open and surface-lifetime tests pass. All async services remain to audit. |
| ARC10 | Atomic full-history replay and explicit last-complete geometry. | Replay owner, after agreeing ARC09; lead integrates. | [~] Reconciled private replay integrated and built. Lead impossible-edit, stale save/export refusal, valid correction, held registry/model and feature-ID history controls pass. Whole-kernel context/handle isolation and full Gate 1 remain. |
| ARC11 | Prepare a plane/sketch privately, then publish bytes and matching history/model/registry/status under one lifetime guard. | Lead owns shared publication; factory owner supplies worker output. | [~] `07316f8f`, receipt `ec2e0156`, composes the actual plane/rectangle worker, private workspace and evaluated state. Lead build/typecheck, core/coordinator and nine Chromium scripts pass. Whole-document formulas/materials/surfaces remain open. |
| ARC12 | Expose inspected plane/rectangle creation through authorized desktop commands and a human action, then edit and durably reopen through My files. | Host/UI owners after ARC11 core; lead owns package/promotion. | [~] Desktop `64becedd8`, CAD code `9bde6b29`: lead scoped-command/menu and real signed create/save/close/fresh-session reopen/editor dimension edit/second save/account denial tests pass. Test-only package; final provenance/package/release qualification remains. |
| ARC13 | Extract bounded authored-profile preparation for worker extrusion. | Extrusion owner; new module/tests only, ahead of ARC14. | [x] Bounded research slice `00e82cd7`, lead qualification `505fbcc4`: seven data tests and a strict-CSP Chromium test using the real sketch worker plus a separate profile worker pass. Explicit selected region, authored edge identity, captured millimeter frame/direction/depth and source digest; no viewer, DOM, canvas, native pointer or kernel. Caller still validates accepted solver/native data and actual document/account lifetime. No installed mount or public command is implied. See fork `test/extrude/README.md` and its evidence JSON. |
| ARC14 | Connect authored extrusion to a real engine worker, model/provenance bridge and accepted-history publication. | Engine/bridge owners after ARC13 contract; lead serializes shared model/craft changes. | [~] `4b6528e9`: actual authored OCC prism, strict headless reader, live mount binding and structured authored face/perimeter-edge roles pass combined independent checks. Ordinary calls omit the 16 KiB research descriptor. `efb96770` now qualifies candidate/accepted ownership with nine pool and six actual-browser tests. Private projection `d6f7dfb0` now has owner/independent/lead proof at `91c8d95c`. Consumer gates, current document/mount association, atomic worker-solid history and edit/undo/reopen remain. Connector edges/vertices have no qualified durable identity. Existing wizard is still synchronous. Mesh checks are not BRepCheck or manufacturing certification; no BOX substitution or silent fallback. |
| ARC15 | Correct model vertex ID types and qualify their reference semantics. | Model owner; isolated from engine worker edits. | [~] `228cde72` fixes object-as-ID with shell-scoped strings and duplicate/malformed-label refusal. Lead fresh build/typecheck and actual OCC/Native Mesh registry, replay, rectangle extrusion and craft-publication tests pass. Producer identity remains unqualified; ordinal fallback unstable. Actual vertex picking and saved vertex-dependent feature tests remain queued. See fork `test/webos/brep-vertex-ids-evidence-20261104.json`. |
| ARC16 | Make shared geometric value-type imports explicit about computation-library dependencies. | Geometry-core owner after bounded reader; no unrelated model/craft edits. | [~] `ae27a6ba`, qualified at `e74843fb`: analytic Shell/Face imports and actual reader work without Verb or fake DOM/canvas; real preloaded/late Verb NURBS controls pass. Actual NURBS still uses the ambient global library and cache, and the reader pulls numeric/lodash. Explicit dependency/bootstrap contracts and broader import separation remain; preserve the full library. |

Current lanes: Files remains accepted; shared Worker mechanical semantics and
numerical/domain correctness, selected-region/kernel support, and separately
isolated native issue branches are active. The lead owns host integration,
independent review, resource qualification, combined acceptance and deployment.
Agents use separate worktrees and owned paths; shared files and deployment are
serialized. Source packaging stays deferred until functional gates qualify.
Finished lanes take another bounded package without changing release state.

## Swappable and composable geometry engines

Latest explicit direction: **OpenCascade is preferred; Native Mesh/Manifold is
secondary.** Properly support both libraries where their capabilities apply,
including capabilities beyond the current app's used subset. Inventory the
installed versions and actual compiled bindings: an upstream feature is not an
available WebOS command merely because a library advertises it. Preserve
engine-specific operations instead of forcing a lowest-common-denominator API.

An engine mount is a versioned computational adapter with explicit initialization,
discovery, execution, result/handle ownership and disposal. It does not own the
authored document, user account, canvas or file-sync service. The document stores
the chosen engine/operation semantics and source intent; derived handles can be
recreated. New engine implementations can be installed under the contract without
rewriting file persistence or UI/agent authorization.

Composition is an explicit job graph, not silently running another engine after
failure. B-rep-to-mesh, mesh-to-B-rep and other conversions declare units,
tessellation/precision, source revision, provenance, supported metadata and lost
identity or information. Validate converted output for its intended use. Never
claim that a faceted B-rep recovered the original parametric or analytic model.

| ID | Required work | Acceptance | State |
|---|---|---|---|
| ENG01 | Inventory both libraries, compiled bindings and existing integration. | Versioned per-operation matrix: upstream support, bound/unbound, exposed/unexposed, tested/unsupported, semantics and prerequisite. Include primitives, curves/surfaces, topology/Boolean, transformations, inspection, import/export and cleanup where provided. | [~] Prototype inventory distinguishes missing legacy SPI exports from active OCI and actual Manifold. Broad library/binding inventory remains. |
| ENG02 | Define engine mount lifecycle and capability discovery. | Stable engine/operation IDs and versioned request/result contracts; explicit representations, units/tolerances, ownership, limits and error classes. Mount/unmount/replacement invalidates owned handles and late jobs without altering saved intent. | [~] Unconnected versioned box/Boolean/dispose workers and shared controller pass real lead tests, with explicit engine differences, integrity checks and owned handles. Broad schemas, installed custody and document integration remain. |
| ENG03 | Separate engine computation from editor/rendering/transport. | Worker or other explicit compute runtime consumes data without DOM/canvas/fake UI. Render adapters consume derived results. Real mounted engine tests, not just mocks. | [~] Restricted sketch core and real OCI/Manifold Boolean workers run without DOM/fake window; isolated runtime/loading policies are research only. Native ownership repairs and document connection remain. |
| ENG04 | Expand the preferred OpenCascade adapter beyond current used calls. | Expose appropriate library capabilities through typed, discoverable operations in bounded families with semantic/edge-case tests. Missing bindings have explicit tasks; no false support claims. | [~] Existing OCC operations and worker Booleans have bounded tests. Separate owned-name source repairs pass scoped runtime checks; interrogation sessions and broad library coverage remain. |
| ENG05 | Properly support Native Mesh/Manifold and its distinct strengths. | Preserve mesh/CSG/surfacing capabilities with actual precision, topology and lifetime rules. No pretend equivalence with OCC or implicit fallback. | [~] Existing native workflows plus real Manifold worker Boolean/empty/disconnected-component and owned-deletion tests; no implicit equivalence with OCC. Broad coverage remains. |
| ENG06 | Typed representation conversions and identity/provenance mapping. | Round-trip or measured-loss tests appropriate to each direction; materials/regions/transforms retained or explicit refusal; stale inputs cannot overwrite newer results. | [ ] General conversion boundary unqualified. |
| ENG07 | Compose engines through explicit bounded jobs. | A real useful two-engine pipeline records conversions and evidence, survives cancellation/failure without corrupting the document, and preserves the final accept/reject transaction. | [ ] Future capability; not a blocker to repairing ordinary replay now. |
| ENG08 | Reproducible mount installation, validation and resource cleanup. | Pinned source/runtime/notices, strict CSP, worker/cancel/crash/disposal tests, multi-window independence, no unauthorized file access; substituting an adapter is qualified against declared capabilities. | [~] Existing build/provenance and scoped host tests; full mount suite remains. |

These packages broaden the implementation plan without replacing the first
Files/Gate 1 finish line. Work on inventory/contracts in parallel; integrate
capability families incrementally. Do not check ENG04/05 off after wrapping only
what today's UI calls. No new top-level app or universal geometry format is
required just to make adapters swappable.

R730 storage and compute, llm-60 compute/testing, and creating/cloning repositories
on box-git are authorized. Record dependencies and reproducible build inputs
there rather than relying on one workstation. R730 is usable; llm-60 needs a
trusted SSH host-key pin before access. No GitHub publication is authorized by
this resource expansion.

## Worker contract and acceptance

These are requirements for the current slice, not a claim all are implemented.

- [ ] Explicit input: supported strict sketch, exact referenced current boundary,
  finite shared parameters, stable IDs/types, accepted relation semantics and
  captured input revisions. Never read mutable editor globals inside the core.
- [ ] Validate input domains and limits before expensive work. Unsupported
  entities/constraints produce typed refusals; never silently omit equations.
- [ ] Preserve units and branch choices. Display units never change physical
  geometry. Distinguish numerical tolerance from design/manufacturing tolerance.
- [ ] Use the actual model equations. Independently evaluate finite output and
  every unreduced hard relation with declared length/angle tolerances. A solver
  `success` flag or reported zero error is insufficient on its own.
- [ ] Return solved data, preserved identities/constants/admission intent and
  attributable diagnostics. Do not report exact DOF or impossibility unless
  the method establishes it; nonconvergence is not proof of contradiction.
- [ ] Validate responses and recheck account, document, sketch, boundary and
  parameter revisions after asynchronous work. A content hash is not an edit
  revision and does not provide account authorization.
- [ ] Reject stale, late, cancelled, malformed and mismatched responses. Clean
  up on success, failure, deadline, cancellation, renderer death and disposal.
- [ ] Use temporary solved geometry for dependent evaluation. Preserve authored
  relationships and the previous valid result on failure, labeling stale/failed
  descendants honestly. Computation does not itself approve a new design edit.
- [ ] Bound input/output size, queue wait, execution time and concurrent work.
  Measure worker counts, responsiveness and memory at supported limits. One
  worker does not imply one bounded allocation or a total-memory guarantee.
- [ ] Avoid copying full file/model buffers unnecessarily. Transfer or lease
  immutable data and use incremental/format-aware work where supported. Back
  pressure must stop unbounded queued work and progress-event floods.
- [ ] Keep file handles, signing keys and network authorization out of numeric
  computation; the authorized command/storage controller publishes results.
- [ ] Record tool/version, semantics, tolerances and input identities for
  reproducibility. Tests cover repeat runs and order independence where promised;
  do not claim cross-engine bitwise equivalence.
- [ ] Inspect jobs/results/failures through the same discoverable API used by
  people and agents. A UI screenshot is not the only way to establish success.
- [ ] Extend this list when a real missing invariant is found, with a concrete
  failing control, owning package and downstream acceptance implications.

## First worker/regeneration proof

1. Use the production entry in a real dedicated worker without `document`,
   canvas, ToolManager, `window=self` or other fake UI. Test the same equations
   used by the editor rather than a substitute math implementation.
2. Resize 100 × 50 to 150 × 30. A circle constrained 10 mm from bottom/right
   moves (90,10) → (140,10). Four corners move to (10,10), (140,10), (140,20),
   (10,20), with all original accepted constraints retained and checked.
3. Explicitly author centering: a hole originally at (50,25) with centering
   relationships moves to (75,15), radius 5. Creation at fixed coordinates
   alone is not an authored promise to remain centered.
4. Exercise missing, split, ambiguous and wrong-type boundary references. No
   silent nearest-edge or kernel-index reassignment. Preserve repairable intent.
5. Exercise contradiction, degeneracy, unsupported relations, malformed output,
   revision changes, out-of-order completion, cancellation, deadlines and worker
   failure. The previous accepted model and account stay untouched.
6. Opening/cancelling a sketch must not rewrite saved boundary snapshots.
   Undo/redo and save/reopen retain intent. A temporary editor is not a save.
7. Inspect actual regenerated solids and all five through-holes, including the
   absence of holes at old positions. Authored cached coordinates need not be
   overwritten if all downstream evaluation and reopen re-solve correctly.
8. Rebuild/package all worker assets with source/license provenance and test
   under production CSP. Qualify OCC and Native Mesh for their actual supported
   operations; unsupported is distinct from untested, pass and failure.
9. Complete the full Gate 1 coupled workflow: fillet/pattern, unit display,
   contradictions, undo/redo, account-backed save/reopen and equivalent agent
   commands. The small worker fixture is necessary but does not prove this gate.

## Integration and longer-term use

Agree contract → implement core and caller independently → review negative
controls → combine/rebuild → prove real regeneration/rejection/reopen → package
and exercise signed WebOS flows → qualify beta. Preserve main and `/desktop/`;
never copy account data or keys between services.

Future assemblies, simulations, optimization and XR share document identities,
commands and revision-bound results while using their appropriate math and
runtime. They must not require a hidden GUI or a second authoritative document.
Keep abstractions driven by actual workflows; a universal entity framework or
an unqualified rewrite of every subsystem is not required for this milestone.
