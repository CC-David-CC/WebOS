# CAD-engine gates and cross-gate design rule

User-defined program, 2026-11-04. These are qualification gates for a future
engineering engine in the browser WebOS, beyond a set of JSketcher patches.

| Gate | Outcome | State |
|---|---|---|
| [1](CAD-ENGINE-GATE-1.md) | Foundational engine: 12 areas, P0/P1/P2 priorities, 22 exercises, five validation responsibilities and Change the original rectangle. | Active; incomplete. |
| [2](CAD-ENGINE-GATE-2.md) | Intermediate CAD: 12 groups, ten ordinary mechanical projects and four specialist areas. | Queued. |
| [3](CAD-ENGINE-GATE-3.md) | Advanced modeling/engineering: original advanced groups 1–10. | Queued. |
| [4](CAD-ENGINE-GATE-4.md) | Production, interoperability, automation: original groups 11–16 plus specialist/project/priority/architecture sections 17–20. | Queued. |

The user is ready to describe another gate separately. Do not invent its scope
or let future descriptions displace ongoing Files and Gate 1 implementation.

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
