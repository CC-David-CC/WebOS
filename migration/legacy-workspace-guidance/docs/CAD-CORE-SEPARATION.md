# CAD core separation and implementation checklist

Active direction, 2026-11-04. The user authorizes using JSketcher as inspiration
and replacing coupled internals where needed. Preserve useful tested components;
the goal is an engineering engine that can grow through the recorded CAD gates,
not just a collection of upstream patches. The user explicitly favors worker
silos without a canvas or fake browser UI, and authorizes extending this
checklist when implementation exposes further core requirements. Every added
requirement needs an observable acceptance test and a bounded owner/package.

This refines `goals/FILES-JSKETCHER-RELEASE-20261103.txt`. Maintain status in
`WEBOS-WORK-QUEUES.md` and `ACTIVE-FILES-CAD-RELEASE.md`. The larger feature
program and handoffs remain in `CAD-ENGINE-GATES.md` and
`CAD-ENGINE-END-TO-END.md`. Later physics, autonomous design and XR inform the
contracts below but remain queued. No complete Files or CAD gate is declared
passed by this architectural decision.

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

Current lanes: Files/resource qualification; headless solver; dependent-feature
regeneration. Agents use separate worktrees and owned paths. The lead owns
shared contracts, review, packaging, combined acceptance and deployment. Finished
lanes take another bounded package, without independently changing release state.

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
| ENG02 | Define engine mount lifecycle and capability discovery. | Stable engine/operation IDs and versioned request/result contracts; explicit representations, units/tolerances, ownership, limits and error classes. Mount/unmount/replacement invalidates owned handles and late jobs without altering saved intent. | [~] Unconnected versioned box/dispose contracts, owned handles and explicit refusals tested; broad schemas, trusted loading and actual document integration remain. |
| ENG03 | Separate engine computation from editor/rendering/transport. | Worker or other explicit compute runtime consumes data without DOM/canvas/fake UI. Render adapters consume derived results. Real mounted engine tests, not just mocks. | [~] Restricted sketch core and a real strict-CSP OCI box worker run without DOM/fake window; derivative wrapper and whole-worker cleanup are research only. General separation remains. |
| ENG04 | Expand the preferred OpenCascade adapter beyond current used calls. | Expose appropriate library capabilities through typed, discoverable operations in bounded families with semantic/edge-case tests. Missing bindings have explicit tasks; no false support claims. | [~] Existing OCC operations and bounded tests; full coverage unqualified. |
| ENG05 | Properly support Native Mesh/Manifold and its distinct strengths. | Preserve mesh/CSG/surfacing capabilities with actual precision, topology and lifetime rules. No pretend equivalence with OCC or implicit fallback. | [~] Existing native workflows and Boolean tests; broad coverage unqualified. |
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
