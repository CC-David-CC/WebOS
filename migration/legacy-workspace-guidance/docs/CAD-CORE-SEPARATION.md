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

| ID | Package | Owner and order | State / evidence |
|---|---|---|---|
| ARC01 | Record rewrite authority, core boundaries and acceptance in the goal/checklist. | Lead, now. | [x] This document and linked goal/audit amendments; documentation only. |
| ARC02 | Data-only sketch workspace and production worker using actual IO/solver. | Solver owner, parallel with Files and caller. | [~] `b448beaa` + `45dd89e1`: actual worker solves centered and four-corner plate fixtures, checks unreduced residuals and output geometry, no UI shims. Lead review/integration pending. |
| ARC03 | Capture immutable sketch/boundary/parameter inputs; solve dependencies and publish only current validated results. | Regeneration owner after ARC02 contract. | [~] Caller/boundary controls and open/cancel preservation fix exist. Automatic solid regeneration is being integrated. Stale-boundary refusal alone is not completion. |
| ARC04 | Normalize commands before execution/history and reserve feature identities across edits/replay/cancel/reload. | History changes integrated by lead. | [~] `e974cb76` includes normalization, feature IDs and typed constraint booleans; owner controls pass; combined rebuilt runtime qualification remains. |
| ARC05 | Qualify whole-part editing, rejection, undo/redo and reopen through UI and discoverable commands. | Serial after core/caller; then host. | [ ] Full Gate 1 rectangle-edit, bracket and enclosure workflows remain. |
| ARC06 | Migrate remaining editor-dependent computation behind document/command/representation boundaries as workflows require. | Separate bounded follow-ups. | [ ] Direction recorded; no claim all existing operations already meet it. |
| ARC07 | Qualify budgets/cancellation across jobs and windows. | Resource owner plus independent review. | [~] Files admission passes lead two-tab/crash tests; signed 128 MiB owner test passes. CAD and combined multi-app resource qualification remains. |
| ARC08 | Back up exact contracts, source, prerequisites, tests and evidence. | Lead after each reviewed slice. | [~] Ongoing box-git/R730 checkpoints; verify both refs. No GitHub publication. |

Current lanes: Files/resource qualification; headless solver; dependent-feature
regeneration. Agents use separate worktrees and owned paths. The lead owns
shared contracts, review, packaging, combined acceptance and deployment. Finished
lanes take another bounded package, without independently changing release state.

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
