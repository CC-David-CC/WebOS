# Gate 1 — foundational parametric CAD engine competency
## Independent ACAD source —2026-11-07

Current engine development is ACAD (Agent Computer-Aided Design), in
`box-git:/srv/data/git/ACAD.git` and `r730:/mnt/data10tb/git/ACAD.git`, branch main.
Its parentless source snapshot is c700cac; inherited JSketcher Git history is
not part of ACAD. Historical proofs retain their original producing revisions;
new ACAD results are qualified separately. See [cutover conditions](ACAD-CUTOVER-20261107.md).
The prior GitHub JSketcher webos-integration remains the previous project's
endpoint. Full Gate1 scope/requirements are unchanged.

## User-confirmed scope revision —2026-11-06

Gate1 now covers21 exercises: E01–E16 and E18–E22. E17 hinged assembly and
assembly-specific competency C10 move to Gate2; preserve original identifiers.
Multibody parts/material regions/core3MF and linked part drawings E22 stay in
Gate1. All other qualification, beta, handoff, backup and pause conditions remain.
This supersedes earlier22-exercise/12-competency scope statements below.


Current mechanical integration: [signed mechanical path, remaining integration and new P0 numerical gaps](evidence/CAD-MECHANICAL-INTEGRATION-20261106.md). This checkpoint supersedes older pending-export/integration statements below; full Gate1 remains open. Filesystem-race testing is cancelled.

Authoritative user acceptance gate, 2026-11-04. This is an engine for future
development, beyond ordinary JSketcher patches. The source fork is a candidate
implementation; merging fixes is not the gate's completion criterion.

Program index and backward design guidance: `CAD-ENGINE-GATES.md`. Later gates
must inform early identities, parameter/units semantics and representation
boundaries; their features remain separately qualified.

Current status: **OPEN / PARTIAL**. Files is accepted; CAD qualification continues.
The [current21-exercise Gate1 baseline](evidence/CAD-GATE1-BASELINE-20261106.md)
records the latest scoped passes, failures, missing shared workflows and active queue. Older implementation-status tables below are historical snapshots; use that matrix for current status.
The beta-and-hardcoded-agent prerequisite passes; the full gate does not.
Gate 2 is `CAD-ENGINE-GATE-2.md`; later gate descriptions remain separate.

## Representation and persistence contract —2026-11-06

User format decision: [our ZIP-based `.cad` project](CAD-NATIVE-FORMAT.md).
Archive implementation is pending; tested native fixtures are currently JSON.

The native project preserves the authoritative design: parameters, sketches,
constraints, feature dependencies/identities and material assignments. The
selected kernel evaluates its B-rep geometry for a specific design revision.
Display tessellation, manufacturing tessellation and interchange exports are
derived representations, with independent quality/tolerance requirements.
STEP hands off evaluated CAD geometry; core3MF hands off manufacturing geometry,
units, parts/groups and supported material information. Neither export replaces
our editable native project or promises recovery of its feature history. Native
project import/reopen is required; general STEP/3MF import is not this gate.
Every derived result must identify its source revision; stale/last-valid results
must remain distinguishable from successful regeneration of the current design.

Current exchange status (bounded qualification, not advertised engine potential):

| Format | Gate role | Current state |
|---|---|---|
| Native project | Required editable source and reopen | Tested authored workflow subsets pass |
| Core3MF | Required material-aware manufacturing export | Named generic plate, separate parts and32-hole workflows plus independent artifacts pass; same-part material interfaces remain open |
| STEP | Required evaluated CAD geometry export | Scoped shared export/reader and File-menu workflows pass; broader interchange qualification remains open |
| DXF | 2D sketch export | Supported bounded sketch subset |
| STL | Optional simple manufacturing mesh handoff | Legacy exporter exists; Worker solids explicitly refuse/unqualified |
| glTF/GLB | Later visualization/sharing | Not implemented in this CAD path; no feature-history promise |

Only native-project import is required now. Foreign imports and reconstructing
parametric history from geometry/mesh files are outside this milestone.


## Boolean contact acceptance

A successful kernel call is not sufficient evidence of one usable solid.
Overlapping supported solids should produce valid manifold results where a
single-solid join is intended. Edge-only or point-only contact does not create
an ordinary manifold volumetric connection. Preserve separate touching bodies
or explicitly reject a single-solid join; never add an invented bridge or
silently weld unrelated vertices. Boolean union may return a container, an
empty result or several bodies, with truthful topology/validity metadata.

SMLib's explicit nonmanifold/no-volume result and Manifold's two accepted mesh
components are different representation reports. Mesh NoError/positive volume
alone does not prove one connected manufacturable part. Geometry representation,
constraint satisfaction, planar topology, kernel validity and dependency meaning
remain separate checks. Manufacturing qualification must independently establish
the intended object/region structure and geometry; the common edge-contact test
passes observation/persistence assertions, not single-solid printability.

Author decision: normal mechanical-CAD Join requests require one verified
manifold solid. Separate bodies require explicit intent. Persist that intent in
the authored feature, so regeneration cannot silently change one part into two.
No automatic geometric offsets, bridges, vertex welds or backend substitutions.
A failed Join leaves the accepted model intact and returns a specific,
machine-readable failure shared by UI and agent callers. If available evidence
cannot establish the requested validity, report it as unqualified rather than
mislabel numerical failure as proof of geometric impossibility.

- [ ] Shared Join/separate-result intent and capability discovery.
- [ ] Persisted result requirement in normal native feature history.
- [ ] Per-backend proof of requested connectivity/manifoldness; NoError alone is
      insufficient, and shell-component count alone cannot classify cavities.
- [ ] Accepted Join, edge/point-contact rejection, explicit separate-body results,
      failed-change preservation, UndoRedo and Save/Open on the same model API.

These are pending application-level checks. The current common union corpus
qualifies truthful result representation/persistence, not this strict Join gate.

## Current source-trust rule and immediate substep

Latest explicit user direction: **all JSketcher features are suspect and are
reference/inspiration, not trusted foundations.** Retain an implementation only
where the required mathematical contract and independent tests justify it;
replace it when that is the clearer route. Upstream compatibility, menu presence,
or a successful old demonstration must not override correct semantics. This
also applies to our adaptations: a scoped passing case is evidence only for
that case, not blanket qualification of a feature family.

The conceptual CAD 1.0 authoring era is narrower than this Gate 1, which also
requires trustworthy parametric editing, units, history and persistence. Later
features may inform identities, typed quantities, worker/engine interfaces,
materials and provenance now. Their implementations stay deferred; stubs and
contracts never count as passing feature acceptance.

Current integration adds legacy-consumer and failed-registration guards
(`e4a21e7c`), transient-reference/sketch guards (`7090a161`) and the authored
worker-prism adapter (`29c89c67`). Focused root guard tests/typecheck and owner
real-worker/reference tests pass. Registry guards (`9bb3eae0`) now reject worker
identity collisions, oversized durable IDs and unsupported stored face sketches.
Combined application qualification and worker-model/history publication remain open.
This does not qualify the entire gate or deploy a new public CAD runtime.

Close the immediate substep by proving the same worker-created solid through
dimension edit, explicit rejection, undo/redo and native/My files reopen. Then
extend that path to dependent holes/cuts/fillets/patterns. Continue the full
P0/P1/P2 matrix and21 in-scope exercises below; do not shrink the gate to one rectangle.

The following dated checkpoints retain their original test scope and are
historical where superseded by this section and the current handoff.

The 2026-11-04 combined fork `2b3f2c0f` passes the bounded five-hole plate
resize/reopen, failed-edit recovery and document-lifetime/surface controls.
Packaged fork `d3d36bc5` additionally passes ordinary OCC fillet/chamfer edits,
invalid-size and Native refusal controls. Desktop `73c1e8b13` passes signed
small-model and dependent-plate save/reopen at simulated phone, 1080p and 4K.
See the fork's `docs/DOCUMENT-LIFETIME-REPLAY-20261104.md` and this repository's
`evidence/cad-packaged-workers-20261104.md` for exact scope and receipts.
These are development tests, not a deployed release or the complete
rectangle/fillet/pattern/unit/agent chain below. The separate worker-engine
mount research is not selected by this application package.

New fork `bdc4ff2b` adds a bounded associative circular-cut pattern and
discoverable seed picker with independent combined/targeted Chromium checks.
Both isolated engine mounts now pass real box/Boolean controls with explicit
differences in empty/multi-body support. Desktop package remains `d3d36bc5`.
Original OCC native ownership defects are being repaired in a separate LAN
source fork; replacement-runtime and cleanup qualification remain open.
The actual agent registry still cannot start a sketch from an empty document;
the next data-only transaction slice addresses this. See the current handoff
and the fork's `combined-pattern-mount-evidence-20261104.json`.

Fork `5b77f71d` records the subsequent craft publication fix (`ccb66be7`).
Lead build/typecheck, stream checks and 12 browser scripts pass. Accepted
history/model/registry/status stay coherent, reset prevents stale notifications,
and rejected commands leave the accepted design valid and saveable. The next
boundary is an atomic plane/sketch-storage document command. This result does
not qualify the full competency matrix, both-engine feature parity, complete
agent workflow or a new release; see `CRAFT-PUBLICATION-20261104.md` in the fork.

## Gate definition and execution policy

- [ ] Qualify all11 in-scope competency areas and21 exercises; C10/E17 is Gate2.
- [ ] Pass the integrated Change the original rectangle test, supplemented by
  isolated edge cases so one demonstration cannot conceal deeper defects.
- [ ] Human UI and authorized agent commands use the same validated operations,
  document, parameters, entity identities, history and account-bound file service.
- [ ] Test OCC and Native Mesh separately. Publish each capability's supported,
  passing, failing, unsupported and untested states; never silently substitute
  engines or force identical topology. Every required exercise needs a qualified
  supported path; unsupported is not a passing exercise.
- [ ] An unsuccessful operation cannot silently corrupt the previous valid
  document. Preserve authored intent, distinguish stale last-valid results and
  expose missing/ambiguous dependencies with repairable failures.
- [ ] Record exact source/runtime, test cases, expected invariants, tolerances,
  actual outcomes and limits. No screenshot-only or menu-presence qualification.

P0/P1/P2 are **competency priorities, not a strict implementation sequence**.
Define persistent identity, units, parameter semantics and feature/reference
contracts early even when their complete user-facing competency is P1/P2.
Necessary architecture work can run in parallel; dependent release claims wait
for evidence. Incremental beta testing does not mean Gate 1 has passed.

## Five independent questions and responsible subsystems

| Question | Responsibility | Required distinction |
|---|---|---|
| Is the geometry representable? | Geometry model | Valid entity, degenerate representation, invalid domain and unsupported type. A zero-radius circle is not automatically a contradictory equation. |
| Are the constraints satisfiable? | Constraint solver | Satisfaction, local freedom, redundancy and numerical convergence are separate facts. Nonconvergence is not proof of impossibility. |
| What regions exist? | Planar topology | Intersections, arrangements, bounded regions, boundaries and selected regions; an inner boundary is not automatically a hole. |
| Can the feature produce valid geometry? | Modeling kernel | Empty, one-body, multi-body and invalid/non-manifold/failure outcomes under the requested operation. |
| Do dependencies remain meaningful? | Parametric history | Persistent references, recomputation, missing/ambiguous dependencies, stale results and recoverability. Geometric equality does not prove identity. |

Do not collapse these into a single validation Boolean. A sketch can be
underconstrained and extrudable, or fully constrained and unsuitable for a
particular solid feature. A valid solid can still have broken downstream
references. Preserve separate test outcomes and failure attribution. A solver
can be fully constrained and redundant at the same time; those are not mutually
exclusive enum values.

## Competency priority matrix

| Priority | Capability | Acceptance standard | Current status |
|---|---|---|---|
| P0 | Geometry primitives | Correct valid/degenerate classification, with declared domains. | Partial; primitive domain/basis fixes under review. |
| P0 | Constraint solver | Distinguish underconstrained, fully constrained, redundant and contradictory; report numerical uncertainty. | Partial; physical DOF is honestly unknown; bounded local Jacobian diagnostics exist. Multi-stage diagnostics and broader solver qualification remain open. |
| P0 | Driving dimensions | Edits propagate consistently or fail while preserving prior intent. | Partial; five-hole plate 100×50×20 → 150×30×20 and impossible-edit recovery pass. General dimensional/typed-expression coverage and full chain remain open. |
| P0 | Units and expressions | Typed, dimensionally valid formulas; conversion/display changes preserve physical size. | Partial; explicit native mm does not establish inch display or a complete units system. |
| P0 | Planar region extraction | Disjoint, nested, intersecting and touching cases interpreted explicitly. | Incomplete; contour loops are not yet a complete arrangement/region model. |
| P0 | Sketch selection | Entities and individual/multiple regions selected unambiguously with durable intent. | Partial candidate for circles/axis-aligned rectangles; full selection/lifecycle scope remains open. |
| P1 | Extrude/revolve | Valid supported-profile solids, with direction and result/body policy. | Partial; explicit selected-region OCC candidate passes scoped cases; complete feature matrix open. |
| P1 | Boolean operations | Union/cut/intersection and correct empty/multi-body results. | Scoped tests exist; full boundary matrix open. |
| P1 | Feature dependency graph | Deterministic downstream recomputation and attributable failure propagation. | Partial; private full-history replay, dependent five-hole resize, fillet/chamfer and last-complete recovery pass. A bounded associative OCC cut pattern passes local resize/reopen/rejection controls; general patterns and the complete chain remain open. |
| P1 | Topological references | Survive supported changes or fail explicitly, never silently retarget. | Partial; complete change-chain test open. |
| P1 | Persistence | Native intent, references, units and history survive save/reload. | Partial; canonical v2, both packaged workers and actual signed My files/server save/reopen pass for small models and the dependent plate. Large models and all document domains remain open. |
| P1 | STEP/3MF export | Independently measurable geometry, units and intended structure preserved. | Partial research; complete coupled-model export open. |
| P2 | Fillet/chamfer/shell | Ordinary and limiting cases behave robustly. | Partial; ordinary 2 mm OCC corner fillet/chamfer, resize/reopen, invalid-size and Native refusal controls pass. Broad edge/limit coverage and shell remain unqualified. |
| P2 | Sweep/loft | Supported profiles/path correspondence and explicit failure cases. | Unqualified. |
| P2 | Drawings/GD&T | Consistent manufacturing documentation tied to model intent. | Not qualified. |

These are acceptance states, not percentages. Unknown/unsupported states cannot
be relabeled passing merely to close the gate.

## Twelve competency areas and required isolated coverage

1. **Sketch geometry.** Point, finite/construction/infinite lines, circle, arc,
   ellipse, rectangle, polygon, spline, slot, offset, trim, extend, mirror,
   patterns and projection where supported. Exercise coincidence/duplicates,
   zero length/radius/sweep/area, reversed arcs, collapsed axes/controls,
   self-intersections, overlapping entities, gaps and broken projections.
2. **Profiles, regions and topology.** Geometry → intersections → planar
   arrangement → bounded regions → explicit selected regions → solid operation.
   Test one loop, open chain, disjoint loops, nested disk/annulus/islands,
   selected subsets, crossing/tangent/coincident boundaries, overlapping edges,
   point/edge contacts, zero-area regions and tiny gaps. Open paths remain useful
   for supported sweep/thin/surface operations; do not call all open geometry
   invalid. Any tolerance repair must be documented and observable.
3. **Geometric constraints.** Coincident, horizontal/vertical, parallel,
   perpendicular, tangent, concentric, equal, symmetry, collinear, midpoint,
   fixed, distance, angle, radius, diameter and length. Define supporting versus
   finite domains, contact semantics, orientation and branch preservation.
   Test freedom, redundancy, contradictions, singularity and convergence
   separately, with meaningful residual/rank/conditioning limits.
4. **Dimensions and parametric edits.** Linear, signed X/Y, angular, radial,
   diameter, arc/center/offset distances, driving/reference roles, named values,
   expressions and tolerances. Rectangle width 100→120→1→0→−10→1e−6→1e6,
   height=width/2 and width=2*thickness. Distinguish an acyclic formula graph,
   cyclic formulas and simultaneous geometric equations; preserve accepted
   source and geometry on rejected edits.
5. **Degeneracy and numerical robustness.** Duplicate/sliver faces and edges,
   collinear/collapsed geometry, tangent/near-tangent contacts, tiny features,
   non-manifold/zero-thickness results, large offsets and numeric overflow
   (including JSON `1e309`). Attribute invalid input, unsatisfiable constraints
   and failed geometric operations separately.
6. **3D features.** Extrude/cut/revolve, sweep/loft, engineered holes,
   fillet/chamfer, shell/draft/rib, mirror/pattern, combine/split,
   offset/thicken and thread behavior where exposed. Test valid ordinary cases
   and domains: signed/symmetric directions, zero depth, excessive radii,
   unsupported contact and disappearing references. Hole intent includes blind,
   through-all, counterbore/countersink, tapped/clearance, pattern and placement;
   it is not automatically represented by an untyped cylinder subtraction.
7. **Parametric feature history.** Edit/suppress/unsuppress/reorder/rollback/
   delete, dependency tracking, affected recomputation, primary versus downstream
   failures, undo/redo, parameters and configurations. Test face/edge split,
   merge, renumbering and deletion; UUIDs or equal positions alone do not solve
   topological naming. Preserve last-valid authored state and explicit repair.
8. **Coordinate systems and transformations.** Global/local/sketch frames,
   principal/custom planes, translations/rotations, pivots, handedness, mirror,
   axis selection, attachments, alignment and local↔world conversion. Move and
   rotate a parent, edit its depth and plane, then verify attached sketch intent.
9. **Units, precision and parameters.** Length/angle/area/volume/dimensionless
   types and counts; mass/density where exposed. Separate stored physical units
   from display, exact numeric values from approximate classification, and
   solver/geometric/manufacturing tolerances. 25.4 mm displayed in inches is
   1 inch with unchanged physical geometry. Reject mixed dimensions and unknown
   units; one global epsilon is not a universal numeric policy.
10. **Moved to Gate2: assemblies and relationships.** Excluded from Gate1 acceptance; retain stable part identities/local frames for later assembly use.
11. **Drawings/manufacturing/exchange.** Orthographic/isometric/section/detail
    views, hidden/center lines, center marks, dimensions, baseline/ordinate
    callouts, datum/GD&T/finish, fits, BOM and manufacturing intent. Record
    STEP/IGES/STL/3MF/DXF/DWG/OBJ/glTF/native support honestly; import/export
    does not imply original history or metadata can be recovered.
12. **Validation, recovery and editing.** Useful errors for invalid entities,
    unsupported profiles/features, rejected constraints, ambiguous/broken refs,
    bad formulas/cycles and failed recompute. Preserve prior valid state,
    identify stale geometry, and restore exact supported history and references
    through undo/redo/save/reload. Never claim an unknown solve succeeded.

## The21-exercise Gate1 ladder (original IDs retained)

| Level | Exercise | Core acceptance / current evidence |
|---|---|---|
| 1 | Draw a line and circle | Real tool creation and native records; scoped creation evidence, edge cases open. |
| 2 | Fully constrain a rectangle | Scoped local-rank diagnostics exist; physical DOF remains unknown, with broader singular/redundant qualification open. |
| 3 | Edit rectangle dimensions | Geometry and accepted authored dimensions remain consistent; partial parameter evidence. |
| 4 | Two disconnected rectangles | Separate selectable regions and deliberate result-body policy; open. |
| 5 | Three nested circles | Scoped OCC circle-region selections pass in candidate; broader identity/selection qualification open. |
| 6 | Introduce a duplicate line | Classify overlap without inventing a valid extra region; open. |
| 7 | Contradictory dimensions | Truthful conflict, prior model/intent preserved, remove/recover/reload; partial. |
| 8 | Extruded plate | Measured solid, correct body count, units and selected profile; scoped evidence. |
| 9 | Four holes | Correct placement, hole/pattern semantics and measurable through geometry; partial audit. |
| 10 | Edit plate width | Scoped five-hole 100×50 → 150×30 edit, fillet/chamfer, undo/redo, failed-edit recovery and native reopen pass; general dependencies and the complete chain remain open. |
| 11 | Fillets and chamfers | Ordinary OCC corner operations through the wizard and invalid-size preservation pass; complete edge/limit matrix and both-engine support remain open. |
| 12 | Hollow enclosure | Shell/wall intent and valid ordinary limits; open. |
| 13 | Revolved stepped profile | Axis, profile and measurable rotational solid; open. |
| 14 | Sweep along a curve | Path/profile alignment and supported valid result; open. |
| 15 | Loft different profiles | Defined correspondence and explicit unsupported cases; open. |
| 16 | Join/subtract solids | Correct empty/connected/disconnected and tool/body policies; scoped evidence. |
| 18 | Parameter-driven geometry | Typed values, dependency graph, accepted edits and invalid-cycle recovery; partial. |
| 19 | Break a referenced face | Explicit missing/ambiguous dependency, no silent retargeting; open. |
| 20 | Export STEP and 3MF | Independent size, geometry, units and intended structure verification; partial research. |
| 21 | Reload saved native model | Signed Files → CAD → My files/server → fresh-session reopen passes for scoped native-v2 models, with exact bytes, IDs and geometry checks; broader document coverage remains partial. |
| 22 | Dimensioned manufacturing drawing | Views/dimensions/reference meaning stay tied to the model; unqualified. |

For each level record UI and agent paths, engine support, isolated failure cases,
dimension changes, undo/redo and account-backed persistence. Basic operation
complexity inside a kernel is not an excuse to reclassify a normal user skill as
advanced. Gate 2 broadens these representative competencies into intermediate
controls, variants and ordinary multi-feature projects.

## Main integrated test — Change the original rectangle

- [ ] Start an empty document; create a fully constrained 100 × 50 mm rectangle.
- [ ] Extrude 20 mm using explicit supported region/body intent.
- [ ] Add a centered Ø10 mm through-hole driven by the rectangle center.
- [ ] Add four corner mounting holes with dimensions/construction relationships.
- [ ] Fillet the intended outer edges.
- [ ] Pattern a feature with explicit seed/count/spacing dependencies.
- [ ] Change the original rectangle to 150 × 30 mm without manually rebuilding
  each dependent sketch, hole, cut, fillet or pattern.
- [ ] Change document **display** to inches without rescaling physical geometry.
- [ ] Undo and redo the dimensional changes, preserving feature/reference intent.
- [ ] Save/sync/close/reload and independently verify the complete model.

Record the dimensions/counts/radii chosen for unspecified feature details before
testing. Measure centers, offsets, body/hole counts, bounds, volume where
appropriate, feature/dependency IDs and solver/kernel outcomes. Test a variant
whose edit is impossible and require an explicit failure, not plausible-looking
replacement geometry. Repeat through the same authorized browser command path;
no AI provider is required.

## File-workflow prerequisite and evidence index

The desktop's shared Files gate remains required: registered-account isolation,
version/conflict protection, uncertain-write reconciliation, verified downloads,
interruption/crash/quota handling, worker/resource behavior and create/open/
rename/move/copy/delete/upload/download. Linux home stays temporary and separate.
Use `ACTIVE-FILES-CAD-RELEASE.md` for that audit, not an app-private CAD mirror.

Use `JSKETCHER-FOUNDATION-MATRIX.md` for individual current findings and
`WEBOS-WORK-QUEUES.md` for scheduling. Evidence is scoped; all unqualified rows
stay open. Tonight's implementation stays on Files and Gate 1 foundations.
