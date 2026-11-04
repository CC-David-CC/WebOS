# JSketcher basic foundation matrix

Active direction, 2026-11-04: qualify basic geometry and behavior before further
feature expansion. Files integration continues in parallel. XR, physics and
advanced feature catalogues are not tonight's implementation work.

Authoritative full Gate 1 scope is `CAD-ENGINE-GATE-1.md`: 12 competencies,
P0/P1/P2 priorities, 22 exercises, five validation responsibilities and the
coupled rectangle-change test. This document is its current findings matrix.
Gate 2 intermediate mechanical CAD is queued in `CAD-ENGINE-GATE-2.md`.

This is an acceptance inventory, not a declaration every feature exists. Each
advertised operation needs a mathematical/domain contract, executable examples,
negative cases and honest support status. Reuse existing evidence, then rerun
affected tests against the combined candidate. No row becomes complete from a
merge, a screenshot, a convenience command or one happy-path example.

## Ownership and test rules

- Lead owns this matrix, shared desktop/files integration and release decisions.
- Geometry owner repairs profiles/solids and supplies failing controls and fixes.
- Solver owner covers constraint semantics, branches, parameters and persistence.
- Independent geometry reviewer tests capabilities and assumptions without
  editing those production modules. Return evidence to the lead for this table.
- For OCC and Native Mesh, report supported/passing, failing, unsupported and
  unverified separately. Do not silently switch engines or require identical
  topology/tessellation. Compare dimensions/volume using stated tolerances.
- UI and agent paths must use the same validated operation. Test from an empty
  model and identify the exact source, engine artifact, fixture and limits.

## Basic shapes and profiles

| ID | Capability / invariant | Current evidence and next gate |
|---|---|---|
| G01 | Point/segment, endpoints and construction references | Solver point tests exist; rendered creation/edit/drag/delete, zero-length and non-finite domains need matrix qualification. |
| G02 | Rectangle/closed polyline, consistent closure and orientation | Unverified as a complete foundation row; test reversed winding, shared corners, gaps and repeated vertices. |
| G03 | Circle: center, radius/diameter, independent size | Concentric feature has real rendered/reopen evidence; zero/negative/non-finite/domain and full shape qualification remain. |
| G04 | Arc: center, endpoints, sweep and branch intent | Circle/arc selection covered narrowly; clockwise/major/minor and parent-circle versus finite-arc semantics remain. |
| G05 | Ellipse/elliptical arc, where advertised | Inventory actual supported creation/edit/persistence; do not imply full incidence or tangency support. |
| G06 | Basic Bezier/spline creation/control points | Carried spline/history checks exist; degenerate controls, valid edit/reopen and declared engine coverage remain. |
| G07 | One closed outer profile creates the intended face/solid | Single-profile extrusion evidence exists; test line, circle, arc and supported curve profiles independently. |
| G08 | Nested regions and selected-region intent | **Missing capability:** original `d319bd2f` selected the whole datum face, not an annulus. Disk/annulus/subset intent is not represented. Experimental parity cutting is not a general fix and is blocked from release. |
| G09 | Multiple disjoint profiles remain separate solids | Circle disjoint control passes in G08 fixture; rectangles/mixed supported profiles and identities remain. |
| G10 | Nested island, multiple holes and winding independence | Unverified; derive explicit containment/fill rules and test them. Unsupported classification must fail clearly. |
| G11 | Touching/intersecting/open/self-intersecting profiles | Unverified; explicitly reject ambiguous/unsupported input instead of silently changing filled regions. |

## Solids, operations and assumptions

| ID | Capability / invariant | Current evidence and next gate |
|---|---|---|
| S01 | Box, dimensions/bounds/volume | OCC block recipe passes scoped UI/command tests, including scale and reopen; independent full basic matrix pending. Native boxes have earlier scoped evidence. |
| S02 | Cylinder/sphere/cone where exposed | Inventory per engine; check analytic bounds/volume, units and valid parameter domains. |
| S03 | Extrude/revolve direction, profile interpretation and body count | Nested-profile failure is open; general sketch extrusion is not currently exposed by Native Mesh. Qualify supported paths explicitly. |
| S04 | Boolean union/cut/intersection | Earlier box comparisons are scoped evidence; test overlap, disjoint, containment, identical and tangent inputs without losing intended part/material identity. |
| S05 | Translation/rotation/scale and pivots | Prior source/rendered tests exist; test axis/order, negative/singular domains where allowed, model units and undo/reopen. |
| S06 | Hole/slot, fillet/chamfer, patterns where advertised | Check actual capability and canonical beginner examples individually; no inference from a visible menu. |
| S07 | Valid mesh/solid, orientation and degenerate output | Check body count, through-holes, faces/bounds/volume and supported validity flags. Empty result is distinct from a failed operation. |
| S08 | Stable authored IDs and generated references | Block ID/reopen evidence exists; qualify deletion, split/merge, failed regeneration and repair behavior. |

## Constraints, parameters and numerical meaning

| ID | Capability / invariant | Current evidence and next gate |
|---|---|---|
| K01 | Coincidence, horizontal/vertical, length and radius | Existing solver tests cover selected relations; ordinary UI/API, domain and edit cases are under systematic review. |
| K02 | Parallel/perpendicular orientation and angle units | **Suspected defect under reproduction:** radian/degree comparison and orientation branch. Do not mark passing until rendered controls verify behavior. |
| K03 | Midpoint, distance, equal measurements and tangency | Midpoint/rejection research exists; verify each advertised definition and supported entity pair, including finite versus supporting geometry. |
| K04 | Concentric circles/arcs | Scoped pass on combined solver, UI/history/reopen and guarded ID command; host registration and independent combined regression remain. |
| K05 | Locks, free motion and ordinary underconstraint | Selected actual solver cases pass; qualify freedom/dragging and diagnostics without calling nonconvergence proof of inconsistency. |
| K06 | Redundant/inconsistent/failed admission | Targeted rejection/rollback fixes pass; test ordinary and degenerate geometries, dependent stages and failure preservation. |
| K07 | Driving/reference dimensions, formulas and parameter edits | Audit actual capabilities and supported types/units; no fabricated substitute for missing driving relationships. |
| K08 | Numerical domains | Reject non-finite numbers, including JSON `1e309`; define null/string/zero/negative semantics per operation. Check small/large scale and tolerances. |

## Persistence and whole-part gates

| ID | Capability / invariant | Current evidence and next gate |
|---|---|---|
| P01 | Explicit unit and canonical native schema | Revision-one millimeter document/worker candidate exists; cross-realm Blob and material-unit disagreement fixes are being reviewed. |
| P02 | Edit/undo/redo/save/reopen retain intent | Scoped constraint/primitive tests pass; full combined UI/agent/My files paths remain. |
| P03 | Bad input/rejected operation preserves prior valid model | Targeted solver and staged-iframe recovery evidence; broader object/generator and arbitrary kernel failures remain. |
| P04 | Account, revision, window and worker lifetime | File/command boundary tests exist; combined signed host and repeated open/close tests remain. |
| P05 | Beginner block/washer/drilled plate, then bracket/enclosure | Follow `planning/CAD-LEARNING-CSG-XR.md`; basic features required by these parts must pass before the parts are called qualified. |

Every row remains open or partial until a matching integrated result is linked.
Unsupported output is acceptable as an honest capability limit; silently wrong
geometry, lost intent or a false success is a failure that must be repaired.
