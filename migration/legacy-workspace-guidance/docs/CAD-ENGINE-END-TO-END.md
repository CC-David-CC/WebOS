# CAD program end to end execution checklist

This is the execution map across the user-defined CAD gates. The detailed
feature checklists remain in `CAD-ENGINE-GATE-1.md` through
`CAD-ENGINE-GATE-5.md`; `CAD-ENGINE-GATES.md` indexes them. **Current active work
is dependable Files and Gate 1.** A recorded future step is not a working tool.

An end-to-end pass requires compatible inputs and outputs at every boundary,
not merely passing feature demos. Later gates constrain early identities,
transactions, units and evidence contracts without activating the whole backlog.

`CAD-CORE-SEPARATION.md` defines the computational/document boundaries and
current worker/regeneration packages. E03–E05 must consume explicit revisioned
model data without constructing an editor or fake UI. Human and agent callers
use the same validated commands; stale worker results cannot publish over a
different account, document or input revision. The saved goal's 2026-11-04
amendment authorizes replacing JSketcher internals to establish these boundaries.

## Ordered delivery gates

| Stage | Required output | Must be proven before relying on it |
|---|---|---|
| S0 Files | Account-scoped browser/server saved versions, conflicts and recovery. | Signed accounts, worker integrity, interruption/reconciliation, lifecycle and resources through stated limits. |
| S1 Foundation | Correct basic entities/constraints/regions, supported solids, identity and native persistence. | Gate 1 isolated matrix plus its coupled rectangle-edit workflow, through UI and API. |
| S2 Intermediate | Ordinary editable multi-feature parts and assemblies. | Gate 2 projects, substantial edits, failure recovery and reopen. |
| S3 Advanced engineering | Qualified surfaces, configurations, mechanisms and applicable studies. | Gate 3 reference checks and engine-specific boundaries. |
| S4 Production and automation | Verified interchange, manufacturing semantics and batch outcomes. | Gate 4 complete per-candidate reports, process-specific validation and provenance. |
| S5 Intent and synthesis | Requirements, decisions and evidence drive bounded design exploration. | Gate 5 slices independently qualified; research uncertainty remains explicit. |

This is dependency order, not a requirement to finish every specialty before a
smaller independent workflow. Material-aware core 3MF can follow its own
qualified geometry/identity/persistence dependencies before general CAM, FEA or
system synthesis. Modeling a simple part does not require an agent fleet.

## One complete design revision

For each supported workflow, keep these artifacts connected to the same account,
document, authored revision and declared model semantics. The conceptual record
names below are contracts to define and test, not an assertion that all APIs or
schemas are implemented today.

| Step | Consumes | Produces | Rejection or recovery behavior |
|---|---|---|---|
| E01 Define intent | User goal and available evidence. | Accepted requirements, assumptions, units, operating cases and open questions. | Ambiguity stays unresolved or becomes an explicit user-approved assumption. |
| E02 Author candidate | Accepted revision, validated operations and allowed decisions. | Transaction containing parameters, features, identities and functional relationships. | Invalid/stale/unauthorized changes leave accepted state intact. |
| E03 Solve sketch | Representable geometry and authored constraints/parameters. | Accepted consistent geometry plus truthful freedom/redundancy/numerical diagnostics. | Contradiction, degeneracy and nonconvergence are distinct; preserve prior valid state. |
| E04 Extract/select regions | Sketch geometry, intersections and declared region rules. | Explicit selected region identities and body-creation policy. | Missing, ambiguous, touching or unsupported arrangements fail explicitly. |
| E05 Regenerate features | Selected inputs, parameters, dependency graph and engine. | Supported valid bodies or surfaces with generated-reference provenance. | Report originating failure, stale descendants and missing/ambiguous references; no silent reassignment. |
| E06 Attach physical meaning | Named parts/regions/interfaces and material catalogue. | Material assignments, orientations, grouping, functions and applicable conditions. | Unknown properties stay unknown; removed regions leave unresolved assignments. |
| E07 Derive representations | Accepted geometric revision and declared purpose/quality. | Display, manufacturing or analysis geometry with units, approximation and identity mapping. | Reject invalid conversions or lost required semantics; never overwrite authored intent with a preview. |
| E08 Define/run study | Geometry, materials, sources, boundaries, operating cases and requested outputs. | Revision-bound job and attributable results/failure. | Missing physics data, cancellation, stale completion or failed solve cannot publish a current valid result. |
| E09 Verify evidence | Results, reference problems, convergence/uncertainty checks. | Evidence linked to exact inputs, tool/settings and applicable requirements. | Separate fast estimates, verified calculations and physical observations. |
| E10 Explore alternatives | Permitted variables, fixed requirements and evaluation method. | Accounted candidate set, feasibility and objective tradeoffs. | Every requested candidate has an outcome; no silent skipped failures or fictitious materials. |
| E11 Accept revision | Reviewable candidate, differences and supporting evidence. | Explicit accepted design transaction and decision rationale. | Rejecting a proposal retains the previous accepted revision; uncertainty cannot be silently accepted as proof. |
| E12 Save and reopen | Native authored model, accepted revision and necessary evidence references. | Verified My files generation and recoverable signed server state. | Conflicts preserve both; unknown commit outcome reconciles before retry; reopen retains intent. |
| E13 Export handoff | Particular design revision, selected parts/grouping/materials and export quality. | Core 3MF/STEP or supported output plus independent verification report. | Invalid/missing bodies, stale revision, bad units or unsupported required semantics block publication. |
| E14 Revisit | Changed requirement, parameter, material, observation or method. | New proposal/revision with affected evidence marked stale and checks rescheduled. | Nominal geometry, measured artifact and solved deformation remain distinct. |

- [ ] Define and version every boundary used by the selected slice.
- [ ] Run the whole slice from an empty project, not a hidden prepopulated state.
- [ ] Discover commands and stable geometry IDs through the browser API; repeat
  through the human interface using the same validated operations.
- [ ] Save, sync, close, reopen and verify authored parameters, relationships,
  accepted constraint state, feature inputs, materials and revision identity.
- [ ] Exercise rejection, cancellation, concurrent editing, account switch and
  interrupted I/O at the boundaries actually used by the slice.
- [ ] Independently check output quantities/structure and report exact scope.

## First concrete acceptance workflows

### W1 Saved data and two applications

- [ ] Registered account A creates a file/folder in Files.
- [ ] Open in Text, edit and save through My files; Files reflects the new saved
  version. Browser-local saved and server-acknowledged states are distinguished.
- [ ] Close/reopen and recover in a fresh signed session; verify exact bytes.
- [ ] Concurrent/offline edits preserve both versions until explicit resolution.
- [ ] Real lost reply reconciles without repeating an uncertain mutation;
  interrupted/corrupt downloads publish no partial data.
- [ ] Account B and stale A windows/workers cannot read or publish A's data.
- [ ] Exercise create/open/rename/move/copy/delete/upload/download, resource
  limits and 128 MiB transfers with changed-data measurements.
- [ ] Temporary v86 files stay separate. A guest stub proves no Linux behavior.

### W2 Foundational parametric part

- [ ] Pass the individual Gate 1 shapes, equations, profiles, kernel and history
  matrix for each declared geometry-engine capability.
- [ ] Create the 100 × 50 mm rectangle, 20 mm extrusion, centered 10 mm through-
  hole, four mounting holes, outer fillet and feature pattern.
- [ ] Change to 150 × 30 mm using intended relationships. Preserve supported
  dependencies or report a precise failure without corrupting the prior model.
- [ ] Change display units to inches without changing physical geometry.
- [ ] Reject contradictory/invalid edits; undo/redo; save/sync/close/reopen and
  independently check the complete model and its editable intent.
- [ ] Repeat via discoverable browser commands without an AI provider.

### W3 Material-aware manufacturing handoff

- [ ] Author editable enclosure, separate lid and contrasting inset label with
  stable parts/regions, units, placement and material identities.
- [ ] Distinguish two printable objects from the label region grouped with the
  lid. Material identity and appearance remain separate.
- [ ] Edit width and wall thickness; preserve assignments or explicitly expose
  broken references. Native save/reopen preserves the accepted relationships.
- [ ] Generate core model 3MF from controlled model-derived geometry.
- [ ] Independently verify two objects, three material regions, transforms,
  dimensions, mesh validity and expected topology at the exported revision.
- [ ] Rejected/stale/cancelled export cannot replace an existing valid file.
  No Bambu project, printer or physical print is required for this milestone.

### W4 First magnetic design study

- [ ] Name fixture and surrounding regions, assign a small applicable material
  catalogue, orientations, interfaces, boundary conditions and operating cases.
- [ ] Preserve those assignments across supported geometry edits or expose
  unresolved references before solving.
- [ ] Run a reproducible appropriate forward model; evaluate a sensing region,
  not an arbitrary visually selected point.
- [ ] Verify reference behavior, convergence, mesh/domain sensitivity and data
  applicability; retain software/settings and input revision.
- [ ] Search only approved dimensions and candidate materials under packaging
  and other fixed requirements. Every failed solve is an invalid candidate.
- [ ] Regenerate and independently reanalyze the chosen final design; report
  what is established and which uncertainty remains.

### W5 Requirements and experimental engineering

- [ ] Begin with a bounded gripper or other approved functional requirement set.
- [ ] Human validates interpretations and permitted design changes.
- [ ] Compare traceable parameter/mechanism alternatives against common cases.
- [ ] Choose an experiment addressing a named uncertainty; retain its controls,
  observations and effect on the model.
- [ ] Accept/reject an explicit revision, repeat required verification and save
  the connected intent/decision/evidence history without losing native editing.
- [ ] Treat mechanism/system synthesis beyond demonstrated methods as research;
  failed searches must not be reported as universal infeasibility proofs.

## Cross-cutting failure and resource checks

- [ ] Separate geometry representability, solver satisfiability, planar region
  meaning, kernel validity and dependency integrity in tests and error results.
- [ ] Preserve the previous valid authored document after every rejected step;
  label last-valid displayed results when the current proposal fails.
- [ ] Bind asynchronous work to account/document/revision/window, cancel it and
  dispose workers/listeners/resources on close. Check before publication.
- [ ] Heavy hashing, decoding, meshing, solving and search run in bounded workers
  or isolated services; measure actual responsiveness, RAM, disk and concurrency.
- [ ] Persist incremental changes and transfer verified changed data where
  supported. Avoid app-private mirrors and full-file rewrites for run counts,
  previews or other RAM-only ephemeral state.
- [ ] Keep approximation, verified simulation, measured evidence and learned
  suggestions attributable and distinct; invalidation follows dependency changes.
- [ ] Native intent, manufacturing handoff, solved deformation, actual artifact
  measurements and inferred parameters cannot silently overwrite one another.
- [ ] Unsupported operations and untested cases remain different from passes
  and confirmed failures; both geometry engines keep honest capability matrices.

## Agent package handoff

Each bounded package must include:

1. Exact base/branch and owned paths or model operations; shared files have one
   owner, and dependent mutations integrate serially.
2. Observable user outcome, prerequisites, supported scope and exclusions.
3. Input/output/error contracts, units, identities and version/lifecycle guards.
4. Positive examples, independent negative controls and measurable acceptance.
5. Reproducible commands, required source/runtime assets and resource limits.
6. Exact commits, evidence and remaining failures, backed up to box-git and R730.
7. Independent integration review and combined regression before release.

Parallel lanes can own storage, solver semantics, region/kernel operations,
material/study definitions or bounded feature tests behind agreed contracts.
The lead owns shared contracts, model/schema integration and deployment. No
agent marks a broad gate complete from its own narrow passing fixture.

## Progress and completion rule

Use `WEBOS-WORK-QUEUES.md` for active/review/integrated/deployed state and
`JSKETCHER-FOUNDATION-MATRIX.md` for current engine findings. `[x]` requires the
stated complete observable acceptance, not a document, merge or visible menu.
Record exact tested source and actual deployment separately. Future research
needs its own bounded demonstration; an attractive generated shape is not a
verified engineering system.
