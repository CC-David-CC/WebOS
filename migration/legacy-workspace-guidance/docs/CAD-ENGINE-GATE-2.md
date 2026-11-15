# Gate 2 — intermediate mechanical CAD

## E17 hinged assembly transferred from Gate1 —2026-11-06

The user moved E17 and assembly-specific C10 here. Gate1 no longer requires
an assembly solver or joint persistence. Preserve original IDs.

- [ ] Two reusable part/component instances with stable IDs and rigid placements.
- [ ] Ground one instance; a revolute joint retains one relative rotational freedom.
- [ ] Shared UI/agent operations author joint frames/references, angle and limits.
- [ ] Motion derives poses without changing part geometry definitions.
- [ ] Missing/ambiguous references and infeasible changes fail explicitly, preserving accepted state.
- [ ] Undo/redo and native Save/fresh Open retain instances, joint intent, references, limits and editable motion.

This is kinematic qualification. Later forces/contact/friction/dynamics remain
separate. Inherited code and the host rejection are not a passing E17 result.


User-defined next gate, 2026-11-04. **QUEUED behind Gate 1**, not implemented or
declared passing by this document. `CAD-ENGINE-GATE-1.md` is the preceding
foundation gate. The user will define a further gate separately.

Outcome: ordinary mechanical parts and small assemblies remain editable and
reusable across multi-feature changes, without rebuilding everything manually.
This gate extends Gate 1 representative operations into useful intermediate
controls, edge cases and complete projects. It does not require advanced
surfacing, FEA, CAM toolpaths, generative design or XR.

## Shared acceptance and architecture

- [ ] Use the same validated operations for UI and authorized agents, the same
  native design/parameters/references and the shared account file service.
- [ ] Preserve separate geometry, solver, planar-topology, kernel and dependency
  outcomes. Record supported, failed, unsupported and untested per engine.
- [ ] Substantial edits, failure/recovery, undo/redo and native save/reload pass
  for every qualified feature/project, with independent measurable invariants.
- [ ] User-facing skills and internal implementation complexity remain separate.
  A 3 mm edge fillet is an ordinary operation even though its implementation
  needs adjacency, offsets/intersections, face replacement and reference repair.
  Selecting a nested region remains basic interaction despite algorithmic cost.
- [ ] Heavy processing uses owned workers/bounded resources; derived geometry,
  approximate interactive views and authoritative design intent stay distinct.

## Twelve competency groups

### I01 — Intermediate sketching

- [ ] Offset/chain offset; open/closed chains, collapse and self-intersection.
- [ ] Trim/extend/split; tangent/multiple/no/ambiguous intersections and endpoints.
- [ ] Sketch fillet/chamfer, excessive/zero distances and unavailable geometry.
- [ ] Mirror, rectangular/circular patterns, coincident axes, zero/overlap/counts.
- [ ] Projection/intersection from solids, invalidated references and tangencies.
- [ ] Construction/regular geometry conversion, centerlines and ambiguous axes.
- [ ] Equations/dependency errors and reusable rigid sketch blocks with clear
  internal versus external constraints.
- [ ] Exercise: four-hole mounting plate controlled by construction geometry
  and dimensions; resize while preserving symmetric intended placements.

### I02 — Profiles and regions

- [ ] Individual/multiple bounded-region selection and explicit exclusions.
- [ ] Nested contours, islands, orientation, mixed open/closed contributors.
- [ ] Supported thin/open-profile features; repair gaps/duplicates/overlaps.
- [ ] Preserve meaningful selected regions through edits or require repair.
- [ ] Exercise: outer rectangle, two circular openings, rectangular opening and
  a disjoint rectangle; extrude the plate/openings, then the separate region.
  Change dimensions until openings touch; report topology changes/reselection
  explicitly rather than silently inventing user intent.

### I03 — Extrusions and revolves

- [ ] Blind/symmetric/two-sided directions, reversal and zero-depth domains.
- [ ] Through-all, up-to-face/body and offset termination, including curved or
  disappearing targets and cuts through multiple bodies.
- [ ] Drafted/thin/multi-profile extrusions with explicit join/cut/intersect/
  new-body and result grouping policies.
- [ ] Partial/cut/thin revolves; axis touching/crossing and disconnected regions.
- [ ] Exercise: stepped revolved shaft, then an extruded keyway cut.

### I04 — Engineered holes

- [ ] Blind/through, counterbore/countersink, tapped and clearance holes.
- [ ] Sourced standard sizes, drill-point angle and thread designation (nominal
  size, pitch, handedness); do not invent standards or infer intent from color.
- [ ] Point/sketch placement, multiple-hole features, patterns, curved supports,
  up-to-object termination and associated callouts.
- [ ] Exercise: four M4 clearance holes, two countersunk holes, one counterbore
  and a blind tapped hole. Edit plate thickness: through-holes stay through;
  blind holes retain authored depth. Document modeled versus annotated thread.

### I05 — Fillets, chamfers and edge treatments

- [ ] Constant/multiple/variable radius, face/full-round fillets and tangent chains.
- [ ] Equal-distance, distance-angle and two-distance chamfers.
- [ ] Corner blending, edge chains and deliberate feature ordering.
- [ ] Excessive radii, consumed faces, shared vertices, hole interactions,
  meeting chamfers and disappeared edge references fail/recover explicitly.
- [ ] Exercise: rounded enclosure with small mounting-hole chamfers.

### I06 — Patterns, mirrors and repetition

- [ ] Linear/circular, sketch/curve-driven and multi-direction feature patterns.
- [ ] Feature/body/component mirrors and direction reversal.
- [ ] Fixed spacing versus equal distribution, skipped instances and seed edits.
- [ ] Keep operation repetition distinct from duplication of resulting bodies.
- [ ] Exercise: 6 × 4 perforated plate; vary width and hole spacing independently,
  suppress two instances and verify dependent geometry/history after reload.

### I07 — Reference geometry

- [ ] Offset/angled/mid/three-point/tangent/curve-normal planes.
- [ ] Axes through cylinder/two points, construction points and center of mass.
- [ ] Local coordinate systems, projected edges and intersection curves.
- [ ] Exercise: angled plane through a cylinder axis, sketch and angled cut;
  preserve the intended original-cylinder definition and reference semantics.

### I08 — Sweeps and lofts

- [ ] Basic/guide/twist/taper/cut sweeps and profile/path alignment.
- [ ] Profile/guide-rail/centerline/closed/thin lofts and supported end conditions.
- [ ] Discontinuous/self-intersecting paths, unequal edge counts, unexpected
  twists, nonintersecting guides and point-collapse cases handled explicitly.
- [ ] Exercise: pipe elbow and rectangular-to-circular transition adapter.

### I09 — Shells, drafts and structural details

- [ ] Closed/open-face/multiple-opening shells and supported variable thickness.
- [ ] Neutral-plane/parting-line drafts; ribs, webs, gussets, bosses and standoffs.
- [ ] Mating lips and grooves with persistent relationships.
- [ ] Exercise: electronics enclosure with 2 mm walls, four bosses, two ribs,
  removable lid and lip/groove. Outer-size changes regenerate them without
  manual reconstruction, or identify the exact impossible dependency.

### I10 — Multi-body modeling

- [ ] Independent body creation; union/subtract/intersect and keep-tools policy.
- [ ] Split body/face, move/copy/derive, visibility and interference.
- [ ] Bodies versus independently managed components; deliberate conversion.
- [ ] Exercise: two-body hinged enclosure, one body used to create clearance in
  the other, then component conversion preserving intended placement/identity.

### I11 — Parametric modeling

- [ ] Named/user parameters, expressions, typed dependencies and reference values.
- [ ] Dimension equations, supported conditional values, suppression/reordering/
  rollback and parent-child failure propagation.
- [ ] Configurations/design tables and linked/external geometry with versions,
  permissions, missing references and deterministic evaluation.
- [ ] Exercise parameters: width=120 mm, length=80 mm, height=50 mm,
  wall_thickness=2 mm, hole_diameter=4 mm,
  boss_diameter=hole_diameter*2.5, rib_thickness=wall_thickness*0.75.
  Change only width/length/height; dependents follow intent. Introduce an invalid
  relationship and report it without silently changing unrelated parameters.

### I12 — Intermediate assemblies

- [ ] Insert/ground parts, rigid/revolute/slider/cylindrical/planar joints.
- [ ] Joint origins/alignment/offsets, limits and mate references.
- [ ] Component patterns, fasteners, interference, exploded views and permitted
  basic motion; moving one part cannot accidentally move the whole assembly.
- [ ] Exercise: base plate, two brackets, rotating shaft, four bolts and a
  sliding component; verify separate rotation/translation and supported limits.

## Ten required projects

| Project | Primary evidence |
|---|---|
| Mounting plate | Hole patterns, constraints and fillets survive resizing. |
| Shaft with keyway | Revolve, cut and chamfer remain coherent. |
| Pulley | Grooves, revolve and circular patterns remain editable. |
| Pipe elbow | Sweep and hollow geometry pass checks. |
| Transition duct | Loft/correspondence and supported guides behave predictably. |
| Electronics enclosure | Shell, bosses, ribs and draft retain dependency intent. |
| Hinged enclosure | Multi-body/component/joint identity and motion are correct. |
| Flanged pipe | Nested regions, holes and circular patterns remain valid. |
| Adjustable bracket | Slots, equations and reference geometry support adjustment. |
| Small linkage | Components, revolute joints and limits preserve mobility. |

Each remains **not qualified** until the full shared acceptance runs and evidence
is linked. A library having the operation is not completed product integration.

## Four additional intermediate areas

- [ ] **Sheet metal:** base/edge flanges, bends/radius/thickness, reliefs, corners,
  unfolding/refolding and flat-pattern export with stated assumptions.
- [ ] **Basic surfaces:** extruded/revolved/ruled surfaces, trim/extend,
  knit/stitch and valid watertight surface-to-solid conversion.
- [ ] **Inspection:** distance/angle/radius, area/volume/mass properties/center
  of mass, sections, minimum clearance and interference with explicit units.
- [ ] **Reuse/documentation:** derived parts, reusable features/configurations,
  ordinary part drawings/sections/dimensions and basic BOM.

## Boundary with later work

Complex Class-A surfacing, complex mold tooling, detailed process planning,
advanced curvature blends, large top-down assemblies, product-family automation,
multibody dynamics/contact FEA, complex sheet forming and geometry-driven search
belong to later goals. Ordinary lofts, fillets, joints, regions and basic
manufacturing communication do not become advanced merely because their
implementation is difficult. Interoperability is checked at the scope claimed;
a file extension alone does not establish semantic manufacturing equivalence.

The next supplied gate is `CAD-ENGINE-GATE-3.md`, advanced modeling and
engineering, containing ten groups. The user intentionally split the other six
groups into the following `CAD-ENGINE-GATE-4.md`. XR stays a
deferred separate-branch stretch, not a reason to skip Gates 1 or 2.
