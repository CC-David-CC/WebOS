# Gate 3 — advanced CAD modeling and engineering

User-defined next gate, 2026-11-04. **QUEUED after Gates 1 and 2.** Recording
this scope does not start advanced implementation or claim any capability passes.
Current work remains Files and foundational CAD-engine qualification.

The user clarified that the original outline was deliberately split: the ten
groups below are Gate 3. Original groups 11–16 belong to the following Gate 4,
now recorded in `CAD-ENGINE-GATE-4.md`. They are not missing Gate 3 requirements.
Autodesk Fusion, Inventor and SolidWorks are capability references, not promised
dependencies, license entitlements or proof this engine already implements them.

## Three different concerns

1. **Advanced modeling:** geometry that ordinary extrude/cut/revolve/fillet
   workflows do not conveniently express.
2. **Advanced engineering:** evidence that a design meets its requirements,
   works under stated assumptions, is manufacturable and stays maintainable.
3. **CAD infrastructure:** kernel robustness, persistent topology, parameter
   semantics and reliable regeneration. These support basic operations too;
   they must not be postponed to Gate 3 merely because implementation is hard.

## Shared acceptance and foundations

- [ ] Preserve the five subsystem questions from Gate 1: representable geometry,
  satisfiable constraints, planar regions, valid kernel results and meaningful
  dependencies. Add study-specific numerical and physical evidence without
  collapsing these questions into a generic success Boolean.
- [ ] UI and authorized agents use the same validated operations, authored model,
  materials/references, versioned files and permissions. No private alternate
  model or unvalidated automation route.
- [ ] Geometry, materials, interfaces, conditions, study inputs, proposed design
  changes, simulated state and results remain distinct attributable records.
- [ ] Physical quantities have units; datasets, assumptions, applicable ranges,
  software/settings and source revisions remain attached to results.
- [ ] Use existing qualified kernels/meshers/solvers where appropriate. A library
  installation or attractive plot is not a qualified engineering workflow.
- [ ] Worker-owned processing, cancellation, revision checks, resource budgets
  and incremental/chunked persistence remain required at the relevant scope.
- [ ] Approximate interactive/game-style motion and rendering remain useful,
  explicitly approximate paths. They do not establish engineering verification.
- [ ] After edits, demonstrate supported intent preservation or explicit,
  repairable failure; preserve last-valid results and mark outdated results.

## A01 — Advanced parametric modeling

- [ ] Global variables, equation-driven features, conditional values and
  configuration/design tables with explicit supported domains.
- [ ] Master sketches, skeleton models, top-down/in-context references and
  derived/multi-body master parts without hidden circular dependencies.
- [ ] Reusable parametric feature libraries and compatible target definitions.
- [ ] Equation-driven curves with singularity/discontinuity handling.
- [ ] Variable-position patterns, parametric suppression and design families.
- [ ] Diagnose undefined variables, formula/reference cycles, suppressed parents,
  changed external sources, body identity changes, collisions and invalid
  configuration combinations without silently changing unrelated values.
- [ ] Exercise: one gearbox-housing definition driven by shaft_diameter,
  gear_diameter, bearing_diameter, wall_thickness, mounting_pattern,
  housing_length and housing_width. Generate several sizes; preserve mounting
  relations/clearances and identify sizes where walls, holes or fillets fail.

## A02 — Advanced surfaces

- [ ] NURBS/Bézier, boundary/filled/ruled/swept/multi-rail surfaces and lofts.
- [ ] Trim/extend/untrim, offset, knit/stitch, replace, morph, flatten and thicken.
- [ ] Surface intersections and coherent patch networks.
- [ ] Distinguish G0 position, G1 tangent, G2 curvature and G3 curvature-rate
  conditions from parameter-dependent C1/C2 continuity. Do not claim G2 from a
  merely tangent circular fillet.
- [ ] Zebra/reflection lines, curvature combs/maps, Gaussian/mean curvature,
  surface deviation, draft and continuity diagnostics with stated tolerances.
- [ ] Handle shared-position/non-tangent boundaries, singular parameterizations,
  incompatible loft mappings, offset self-intersections, unbounded curvature,
  trim slivers and failed stitching explicitly.
- [ ] Exercise: a smooth computer-mouse enclosure with controlled transitions,
  inspected using zebra/reflection and curvature evidence.

## A03 — Subdivision and freeform

- [ ] Subdivision surfaces, control cages, creases, local refinement and symmetry.
- [ ] Bridge, face extrusion/deletion and edge-loop insertion with valid topology.
- [ ] Evaluate T-spline-style locally refinable representations explicitly; do
  not assume proprietary software or a particular implementation is available.
- [ ] Supported conversion to B-rep and hybrid freeform/parametric modeling
  preserve declared approximation/error and feature/reference intent.
- [ ] Exercise: ergonomic controller grip plus dimensionally precise mounting
  bosses and screw holes; organic and mechanical geometry remain editable.

## A04 — Advanced solids and topology

- [ ] Face replacement/deletion/healing and direct face move/offset/rotation.
- [ ] Variable-radius/curvature-continuous/multi-face blends.
- [ ] Complex and multi-thickness shelling; Boolean imprint and curved splitting.
- [ ] Local healing, defeaturing and simulation simplification.
- [ ] Multi-body Boolean operations and deliberate hybrid B-rep/mesh editing.
- [ ] If non-manifold modeling is supported, keep it distinct from qualified
  ordinary watertight solids and restrict incompatible operations/exports.
- [ ] Define B-rep versus CSG, orientability, open/closed shells, manifoldness,
  validity, tolerance, intersections and topology independently of display mesh.
  Exact/tolerance-controlled Booleans must construct/classify valid boundaries;
  adding/subtracting arbitrary triangles is not sufficient evidence.

## A05 — Advanced sheet metal

- [ ] Multi-bend sequences, hems, jogs, lofted/sketched bends and swept flanges.
- [ ] Closed corners, reliefs, forming tools, emboss/louver/stamp features,
  beads and drawn forms with stated process/material assumptions.
- [ ] Unfold/refold, sourced bend tables/K-factor, flat-pattern validation and
  supported bend-sequence/manufacturability checks.
- [ ] Exercise: chassis with multiple bends, ventilation louvers, corner reliefs
  and mounting tabs; verify unfolded dimensions after sheet-thickness changes.

## A06 — Advanced assemblies and top-down design

- [ ] Large assembly loading, lightweight representations and configurations.
- [ ] Top-down/in-context editing, skeleton assemblies and flexible subassemblies.
- [ ] Advanced coupled mates: gear, rack-and-pinion, screw, cam, belt/chain and
  path relationships, with declared freedom/branch/domain semantics.
- [ ] Collision/clearance, assembly envelopes, exploded configurations and
  compatible component replacement without silent reference retargeting.
- [ ] Exercise: robotic arm with rotating base, shoulder, elbow, wrist, gripper,
  reduction and joint limits. Change upper-arm length and verify relationships.

## A07 — Mechanisms and motion

- [ ] Forward/inverse kinematics, drivers and mechanical constraints.
- [ ] Supported contact/friction, springs, dampers, motors and actuators.
- [ ] Gear trains, cams/linkages, velocity/acceleration, reaction force/torque and
  reachable-motion envelopes under explicit physical/numerical assumptions.
- [ ] Diagnose singularities, redundant/overconstrained joints, collisions,
  conflicting couplings, multiple solutions and configuration boundaries.
- [ ] Exercise: drive a four-bar linkage through its permitted range, identifying
  singular configurations and preserving or reporting branch changes.

## A08 — Finite-element analysis

- [ ] Static/nonlinear stress, modes, buckling, thermal/thermal stress and fatigue.
- [ ] Contact, transient/dynamic/impact and frequency response where qualified.
- [ ] Composite/plastic material behavior appropriate to each study.
- [ ] Mesh refinement/adaptation and convergence studies with reproducible inputs.
- [ ] Record conditions, loads, materials/applicability, conditioning,
  singularities and contact definitions. Distinguish numerical verification,
  comparison with analytical results and validation against physical data.
- [ ] A colorful stress map cannot be presented as proof a design is safe.
- [ ] Exercise: loaded cantilever bracket; compare displacement with a stated
  beam-theory reference and refine the mesh to demonstrate convergence.

## A09 — Fluid and thermal engineering

- [ ] Fluid domains, inlets/outlets and conditions; velocity/pressure fields.
- [ ] Applicable turbulence models, conductive/convective and conjugate heat
  transfer, electronics cooling, pressure drop and flow separation.
- [ ] Transient flow, appropriate refinement and bounded design improvements.
- [ ] Treat fluid/thermal assumptions, model applicability and numerical
  evidence as their own specialization; do not infer it from structural FEA.
- [ ] Exercise: electronics cooling duct with attributable airflow distribution
  and pressure-drop measurements, checked for relevant convergence/conditions.

## A10 — Generative design and topology optimization

- [ ] Explicit allowable design space, preserved interfaces and obstacle regions.
- [ ] Defined load cases, supported real material choices and manufacturing limits.
- [ ] Mass/stiffness goals, parameter/shape/topology search as separate capabilities.
- [ ] Multi-objective exploration/Pareto tradeoffs, candidate feasibility and
  reproducible comparisons against the same requirements.
- [ ] Reconstruct usable final designs and independently reanalyze the resulting
  geometry; an approximate search score is not final design verification.
- [ ] Preserve invalid/failed candidate diagnoses. Do not invent physically
  realizable materials by independently choosing incompatible property sliders.
- [ ] Exercise: minimum-mass load-bearing bracket preserving mounting interfaces
  and clearance regions while meeting stiffness requirements; compare against a
  conventional bracket under the same assumptions and independent final checks.

## Following gate

Gate 4 is now recorded in `CAD-ENGINE-GATE-4.md`: the six separated groups plus
specialties, capstones, platform priorities and representation boundaries. Do
not fold it back into Gate 3. Gate 3 still requires implementation and evidence
for its ten groups. Later needs inform earlier interfaces according to
`CAD-ENGINE-GATES.md`, without starting later feature implementation by default.
