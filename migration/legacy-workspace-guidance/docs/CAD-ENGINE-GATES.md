# CAD-engine gates and cross-gate design rule

User-defined program, 2026-11-04. These are qualification gates for a future
engineering engine in the browser WebOS, beyond a set of JSketcher patches.

| Gate | Outcome | State |
|---|---|---|
| [1](CAD-ENGINE-GATE-1.md) | Foundational engine: 12 areas, P0/P1/P2 priorities, 22 exercises, five validation responsibilities and Change the original rectangle. | Active; incomplete. |
| [2](CAD-ENGINE-GATE-2.md) | Intermediate CAD: 12 groups, ten ordinary mechanical projects and four specialist areas. | Queued. |
| [3](CAD-ENGINE-GATE-3.md) | Advanced modeling/engineering: original advanced groups 1–10. | Queued. |
| [4](CAD-ENGINE-GATE-4.md) | Production, interoperability, automation: original groups 11–16 plus specialist/project/priority/architecture sections 17–20. | Queued. |
| [5](CAD-ENGINE-GATE-5.md) | Requirements, functional intent, inverse design, experiments, evidence and system synthesis; six independently qualified slices including research. | Queued; not implemented by recording. |

**End-to-end execution:** [CAD-ENGINE-END-TO-END.md](CAD-ENGINE-END-TO-END.md)
defines the ordered delivery stages, 14 design-revision handoffs, five concrete
acceptance workflows, failures/resources and bounded agent packages. Do not let
future descriptions displace ongoing Files and Gate 1 implementation.

## Current capability and qualification status

Status checkpoint, 2026-11-04. Existing libraries and upstream features count as
available implementation, not automatically as verified WebOS workflows. A gate
can contain useful passing tests while remaining incomplete as a whole.

| Gate | Existing implementation/evidence | Remaining qualification |
|---|---|---|
| 1 Foundation | Browser-created sketch entities; primitives and transforms; selected constraints/parameter edits; bounded OCC region/Boolean cases; native snapshot and Files research tests. | Combined candidate integration, complete entity/domain and both-engine matrix, truthful DOF/redundancy, unit semantics, dependent edit-chain, UI/API equivalence and signed save/reopen. Active and partial. |
| 2 Intermediate | Existing JSketcher feature operations and related CAD apps supply a starting point. | Ten complete editable projects and the grouped controls, edge cases, references and persistence. No full project qualification claimed. |
| 3 Advanced modeling and engineering | Geometry, numerical, visualization and browser computation components are available in the project. | Qualified surface/configuration/mechanism/study workflows with appropriate reference and convergence evidence. Queued. |
| 4 Production and automation | Material/grouping and core 3MF research, existing export and command infrastructure. | Complete material-aware enclosure handoff, independent output checks and later manufacturing/batch/production packages. Queued; prototypes are partial. |
| 5 Intent and synthesis | Recorded requirements, conceptual objects, contracts and bounded future slices. | Implement and qualify requirements/decision/evidence workflows, then experiments and research capabilities. Planned; no autonomous engineering claim. |

**CAD 1.0 is not the same checklist as Gate 1.** The conceptual era emphasizes
geometry authoring; Gate 1 deliberately also requires dependable parametric,
units, topology, failure and persistence behavior. Six sketch entity kinds have
bounded browser creation/serialization evidence, not six fully qualified
geometry domains. There is no defensible overall validated percentage from the
current uneven test coverage. No gate is fully passed yet; that does not mean
there is no implementation. Use `JSKETCHER-FOUNDATION-MATRIX.md` for exact cases.

## Later gates inform earlier gates

**Design knowledge flows backward; qualification progresses through the gates.**
Later requirements constrain early data models, identities, operations and
interfaces. They do not automatically authorize implementing all later features
instead of finishing the current gate. Competency priority is not a rigid code
implementation order. Record which downstream need motivates an early decision
and its testable invariant.

| Later need | Earlier invariant |
|---|---|
| Configurations/automation | Typed parameters, explicit dependency semantics, deterministic validated commands and attributable revisions. |
| Manufacturing/multiple materials | Durable part/region IDs, distinct material/appearance, explicit grouping, physical units and controlled tessellation. |
| Assemblies/mechanisms | Part identity independent from instance transform; 2D constraints and 3D pose relationships have separate responsibilities. |
| Analysis/optimization | Meaningful regions/interfaces, material evidence, units and study/source revision; simulated state is not silently an authored design edit. |
| Surface/mesh/B-rep workflows | Explicit representation/conversion contracts, tolerances and provenance; no accidental independent document authorities. |
| Reverse engineering | Preserve measured/fitted/derived distinctions and uncertainty; a faceted B-rep is not recovered parametric intent. |
| Drawings/PMI/change management | Persistent semantic references, associative requirements, explicit missing/ambiguous references and durable revision history. |
| Batch agents/collaboration | Shared UI/agent consistency/permission checks, cancellation/stale-result guards and complete per-candidate success/failure accounting. |
| Intent and autonomous experiments | Requirements, functional relationships, decisions and evidence have distinct identities and applicability; proposals use reviewable transactions and the ordinary validated API. |
| Learning and physical feedback | Nominal design, observations, solved states and inferred model properties remain separate; evidence cannot silently become a design edit or universal certification. |
| Large models and XR previews | Worker/resource ownership, purpose-specific derived meshes, incremental file sync and separation of fast approximate display from authoritative results. |

Schemas may evolve deliberately; reject unsupported required semantics rather
than silently interpreting them under an older meaning. Do not maintain app-
private account mirrors or sync full derived geometry every animation frame.
Shared Files/account isolation and verified changed-data persistence underpin
all gates. Keep both geometry engines with honest capability boundaries.

## Operational checklist

- [ ] Use the current gate's explicit acceptance, not a convenient subset.
- [ ] Preserve future requirements in their own gate while tracing architectural
  implications into the current work.
- [ ] Qualify five separate outcomes: geometry representation, constraint
  satisfaction/freedom, planar region meaning, kernel result and dependency
  integrity. Add engineering/process evidence at the appropriate scope.
- [ ] Use modeling breadth, parametric reliability and engineering validity as
  separate maturity measures; no single passing shape or command count proves
  all three.
- [ ] Keep the engine-specific matrix and exact tests/evidence current; unsupported
  and untested remain distinct from passing and failing.
- [ ] Keep source, prerequisites, tests, notes and integration decisions backed
  up to box-git and R730. Only the integration owner changes shared release state.

Current implementation/audit: `ACTIVE-FILES-CAD-RELEASE.md`,
`JSKETCHER-FOUNDATION-MATRIX.md` and `WEBOS-WORK-QUEUES.md`. None of these
documents declares an unverified gate complete.

## Conceptual eras

| Era | Central activity |
|---|---|
| CAD 1.0 | Draw geometry |
| CAD 2.0 | Model parametric geometry |
| CAD 3.0 | Simulate and optimize designs |
| CAD 4.0 | Generate designs from requirements |
| CAD 5.0 | Autonomously investigate and validate engineering alternatives |
| CAD 6.0 | Discover and synthesize new physical systems |

These user-defined labels are a conceptual map, not industry standards or
guaranteed dates. Later capabilities retain the correctness obligations of
the earlier foundation.
