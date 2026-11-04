# Gate 4 — advanced production, interoperability and automation

User-defined next gate, 2026-11-04. **QUEUED after Gates 1–3.** This contains
the original advanced outline's groups 11–16 and its specialist, capstone,
priority and architecture sections 17–20. Recording does not start this phase.
See `CAD-ENGINE-GATES.md` for the cross-gate architecture and scheduling rule.

## Shared acceptance

- [ ] UI and authorized automation use the same validated design operations,
  references, materials, revisions and account/document permissions.
- [ ] Preserve the five separate Gate 1 validation responsibilities. Add process-
  specific evidence without confusing valid geometry, manufacturability,
  simulation validity or machine readiness.
- [ ] Native projects preserve editable intent. STEP/3MF/mesh/toolpath/PMI
  exports are attributable handoffs with explicit supported semantics.
- [ ] Record assumptions, physical units, tool/process/material data, source
  revisions, software/settings and independently checked measurements.
- [ ] Heavy work is cancellable, revision-bound and worker-owned with measured
  resources; incremental persistence avoids resending unchanged large data.
- [ ] Ordinary approximation, visualization and interactive play remain useful
  paths but cannot be presented as qualified manufacturing or engineering proof.
- [ ] Unsupported/failing cases are reported, never silently skipped or replaced
  by unverified output. Preserve last valid authored state and recoverable work.

## M11 — Advanced manufacturing and CAM

- [ ] 2.5-axis pockets/contours/drilling, 3-axis surface work and supported
  4-axis rotary / simultaneous 5-axis motion.
- [ ] Adaptive/rest/high-speed clearing, tool orientation and trajectory quality.
- [ ] Tools/holders, workholding/fixtures, stock and multi-setup planning.
- [ ] Remaining-stock simulation and machine/tool/fixture collision checks.
- [ ] Turning/mill-turn, probing, supported post-processing, setup sheets and
  toolpath time/motion optimization.
- [ ] Exercise: aluminum housing, initial stock and fixtures, setups covering
  the required faces, verified cutter/holder/fixture clearance before producing
  machine instructions. Generic paths are not a qualified machine-specific post.

## M12 — Advanced additive manufacturing

- [ ] Orientation and support generation/optimization with removal assumptions.
- [ ] Lattice/graded/gyroid/conformal and lightweight structures.
- [ ] Multi-material regions/interfaces and print-in-place assemblies.
- [ ] Clearance/shrinkage compensation, build-volume partition and mesh repair.
- [ ] Supported 3MF materials/structure, process distortion where qualified.
- [ ] Exercise: lightweight robotic gripper with internal lattice and moving
  print-in-place joints. Independently verify parts, units and intended clearance
  through 3MF interchange. File validity does not prove printability; receiving
  processes/devices must support the actual structure/materials and constraints.

## M13 — Molds and plastic-part design

- [ ] Parting lines/surfaces, core/cavity and shutoff surfaces.
- [ ] Draft/undercut analysis, side actions, lifters and ejector placement.
- [ ] Gates/runners, cooling channels and supported sink/warpage assessment.
- [ ] Appropriate filling/process simulation, shrinkage and family molds.
- [ ] Exercise: injection-molded controller housing with attributable draft and
  undercut checks followed by supported core/cavity derivation.

## M14 — Reverse engineering and scan-to-CAD

- [ ] Point import/registration, mesh reconstruction/cleanup/hole filling and
  decimation, with units, alignment and error evidence.
- [ ] Analytic/freeform surface fitting; plane/cylinder/sphere/cone recognition.
- [ ] Hole/pocket/feature recognition, section extraction and mesh-to-B-rep.
- [ ] Deviation/comparison, dimensional inference and editable reconstruction.
- [ ] A triangle-faced B-rep is not recovery of the original parametric design.
  Preserve uncertainty and distinguish fitted geometry from measured samples.
- [ ] Exercise: import or scan a bracket, reconstruct meaningful major features
  and dimensions, produce an editable model and compare it with source evidence.

## M15 — Drawings, GD&T and model-based definition

- [ ] Datum frames, position/profile/flatness/perpendicularity/parallelism/runout
  and appropriate geometric tolerance meaning.
- [ ] Tolerance stacks, mating fits/clearances and surface finish.
- [ ] Weld symbols, MBD/PMI, associative annotations and inspection planning.
- [ ] Manufacturing BOM and controlled drawing/revision comparisons.
- [ ] Exercise: shaft/bearing assembly with stated dimensional tolerances,
  datum references and an inspection drawing tied to the actual feature revision.

## M16 — Automation, APIs and product lifecycle

- [ ] Macros/scripting, custom feature APIs/properties and rule-based design.
- [ ] Batch families, configuration automation, drawings and controlled exports.
- [ ] Design-rule scripts and repeatable automated geometric regression tests.
- [ ] PDM/PLM-compatible revisions/dependencies, change orders and comparisons.
- [ ] Authorized concurrent engineering, custom workbenches and plugins with
  the same consistency/lifecycle/file boundaries as built-in applications.
- [ ] Exercise: generate **50 enclosure variants**. For every requested variant:
  regenerate, validate geometry, check walls/clearances, calculate volume/mass,
  export STEP, export 3MF and produce an attributable validation report.
- [ ] Account for all 50 outcomes. A failed variant is recorded with its reason;
  it cannot disappear from the report or be counted successful without outputs.
  Missing/unsupported material density cannot silently become an invented mass.

## S17 — Specialist capabilities

Track these as individual future packages, with appropriate domain references
and evidence. A single general geometry engine does not establish all of them.

| Specialty | Scope |
|---|---|
| Weldments/structures | Members, joint treatments, cut lists and frame analysis. |
| Piping | Routes, fittings, bend limits and qualified pressure calculations. |
| Electrical routing | Harnesses, paths, connectors and bend-radius intent. |
| PCB/MCAD | Board/component envelopes, clearance and enclosure synchronization. |
| Optics | Ray models, lens geometry and optical clearance. |
| Composites | Plies, orientations, draping and applicable laminate analysis. |
| Aerospace | Aerodynamic surfaces and structural integration. |
| Automotive | Surface quality, packaging and mechanisms. |
| Robotics | Kinematics, workspaces and collision envelopes. |
| Metrology | Inspection, registration/deviation and tolerance verification. |
| Digital twins | Versioned connection of engineering models and operating data. |
| Design optimization | Bounded exploration under explicit feasibility constraints. |

These are capability targets, not claims every commercial edition supplies them
or that this project has installed/licensed particular external implementations.

## C18 — Advanced learning projects and capstone

| Project | Primary competency |
|---|---|
| Ergonomic mouse | Surfaces and controlled continuity. |
| Gearbox family | Configurations, equations and shared design intent. |
| Robotic arm | Components, mechanisms and motion. |
| Optimized aerospace bracket | Verified structural study and topology search. |
| Molded controller | Surfaces, draft and mold tooling. |
| Sheet-metal chassis | Bends, reliefs and manufacturing. |
| Cooling system | Verified thermal/flow behavior. |
| Lightweight printed gripper | Lattices and additive constraints. |
| Scanned mechanical component | Reconstruction and mesh/CAD error evidence. |
| Automated configurator | Scripting, parameter generation and validation. |

- [ ] Capstone: robotic gripper with mechanical-load evaluation, structural
  optimization, verified permitted movement and manufacturing handoff. Preserve
  separate evidence for every discipline and reanalyze the final reconstructed
  geometry. No single attractive result establishes this full workflow.

## P19 — Browser-platform implementation priorities

These guide package selection, not a promise to implement an entire level in a
single phase or a reason to postpone infrastructure needed by earlier gates.

| Priority | Capabilities |
|---|---|
| High | Robust configurations, complex surfaces/continuity inspection, advanced blends/shells, mesh/B-rep interoperability, automated validation, scripting, complex assemblies, kinematics and STEP/3MF interoperability. |
| Medium | Sheet metal, FEA, lattices, topology optimization, advanced drawings/GD&T and mold tooling. |
| Lower initially | Simultaneous five-axis CAM, CFD expansion and enterprise PLM as substantial independent specializations. |

Prior gate scope still applies. This matrix refines future depth and sequencing;
it does not erase already-required representative checks from Gates 1–3.

## R20 — Representation boundaries and independent maturity measures

| Representation | Responsibility |
|---|---|
| Parametric design graph | Authored intent, features, parameters and dependencies. |
| Sketch/constraint model | 2D entities, equations and geometric relationships. |
| B-rep | Exact or tolerance-controlled geometric faces, edges and solids. |
| Mesh | Purpose-specific tessellation for viewing, fabrication or analysis. |
| Assembly | Part/component instances, transforms and mechanical relationships. |
| Analysis | Material/physical assumptions, conditions, discretization and solver state. |

These are different mathematical responsibilities, **not six competing copies
of one document**. The graph drives geometry; derived B-rep/meshes preserve
source identity/revision and declared approximation. Assemblies compose parts;
studies attach assumptions to meaningful geometry. Planar regions bridge sketch
geometry and selected feature inputs. Define these interfaces early so later
domains do not repeatedly replace the foundation.

Evaluate maturity independently:

1. **Modeling breadth:** which geometry/operations can be authored?
2. **Parametric reliability:** which edits preserve intent, dependencies and
   supported history, and which failures are explicit and recoverable?
3. **Engineering validity:** which outputs/analyses/interchanges are independently
   verified under stated units, assumptions and tolerances?

A complex loft without reliable regeneration does not outrank dependable basic
mechanical modeling. The final advanced test is a manufacturable design that
remains correct through substantial parameter/configuration changes and
downstream operations. Command counts alone cannot establish that maturity.
