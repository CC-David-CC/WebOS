# CAD learning, constructive geometry, motion and deferred XR

User direction, 2026-11-04. This extends the program checklist; it does not
declare these experiences implemented or expand the current release into XR.

## Priority and branch boundaries

1. Finish dependable Files and the consolidated CAD/solver/host foundation.
2. Prove basic single-part exercises through the same human and agent operations,
   then the mounting bracket and enclosure/material-aware core-3MF milestone.
3. Improve the ordinary browser authoring experience and reusable CSG/motion
   workflow, with measured interactive performance and explicit approximations.
4. Develop qualified physical studies and mechanisms in their existing silos.
5. **Deferred stretch: spatial XR workshop.** Work in a separate fork branch,
   proposed name `research/xr-spatial-workshop`; this name is reserved planning,
   not an assertion the branch or an implementation exists. XR is below the
   preceding foundations and useful flat-screen workflows. It blocks none of
   the current Files, CAD, agent-command or 3MF release gates.

Fast exploration and qualified engineering studies are both eventual supported
paths. Neither requires waiting for XR, and neither can be declared complete
because a scene looks convincing.

## Single-part learning and agent acceptance

Use a representative progression rather than claiming one universal syllabus.
Each exercise has a written dimensional specification and checkable geometry.

| Queue | Exercise | Concepts and expected evidence |
|---|---|---|
| [ ] L01 | Dimensioned rectangular block | Units, datum, closed sketch, extrusion, dimensions, bounds and analytic volume. Start with 60 × 40 × 10 mm. |
| [ ] L02 | Washer/spacer | Concentric circles, independent diameter/thickness, through-hole and intended center. Example: 30 mm outside diameter, 10 mm bore, 4 mm thickness; volume 800π mm³. |
| [ ] L03 | Drilled mounting plate | Driving X/Y hole centers, repeated holes, symmetry and parameter changes. Check positions and retained holes after regeneration. |
| [ ] L04 | Stepped shaft/bushing | Revolved profile or deliberately united cylinders, coaxial steps, shoulders and bore. One authored solid with predictable size changes. |
| [ ] L05 | L-shaped mounting bracket | Extrusions/cuts, hole spacing, relevant fillets/chamfers and reference repair; existing A01 acceptance. |
| [ ] L06 | Slotted or ribbed support | Slot tangency, mirrored/repeated features, wall thickness and supported manufacturing details. Unimplemented operations remain explicit gaps. |
| [ ] L07 | Enclosure body and separate lid | Pocket/wall relationships; first author each as an intelligible single part, then preserve two separate print objects and the inset label; existing A02/E01–E04 acceptance. |

L01–L03 are the first basic C05 agent fixtures, followed by the existing bracket
and enclosure gates. L04/L06 extend the learning suite before optional XR work;
they do not silently make a complete advanced-feature catalogue a release gate.

For each qualified exercise:

- [ ] A person can create and edit it through the UI; an API client can discover
  operations and stable entity IDs and perform the same validated changes.
- [ ] Compare dimensions, body count, holes, bounds and supported volume against
  the specification, using engine/tessellation-appropriate tolerances.
- [ ] Substantially change dimensions and test a contradiction or invalid input;
  report failure honestly and preserve the previous valid authored model.
- [ ] Undo/redo, save/sync, close and reopen preserve parameters, relationships,
  part identities and supported material assignments under the correct account.
- [ ] Tests start from an empty document, not an unexplained prebuilt model.
  No AI provider is required to test the command client.

## Reuse the existing components

| Responsibility | Starting component | Current boundary |
|---|---|---|
| Sketch/history/parametric authoring | Consolidated JSketcher, OCC and Native Mesh | Candidate under test; unsupported operations stay explicit. |
| Precise scripted solid operations | Replicad/OpenCascade | Engine supports solid combinations; this desktop's existing Replicad UI is a limited worker-backed box/cylinder/hole preview, not a full scripting environment. |
| Fast mesh union/cut/intersection | Manifold-backed native geometry | Already present in candidate source; not a complete interactive modeling/physics workbench. |
| Interactive rigid-body motion | Existing Physics Playground's Three.js/Rapier foundation | Existing sandbox source and scoped tests; CAD import, shared design commands and engineering studies are unfinished. |
| Qualified field/deformation studies | Existing Gmsh/Elmer/GetDP roadmap | Future qualified solver integrations; an attractive animation is not this capability. |

CSG and joints have different meanings: unite primitives when they make one
part. Preserve separate bodies when they must rotate, slide or otherwise move
relative to one another. A Boolean union must not silently erase an authored
material interface needed by manufacturing or analysis.

## Interactive and engineering paths share authored intent

- [ ] Keep one versioned authored design with stable part/region identities,
  units, parameters, placements and material assignments. People and agents use
  the same operations. Simulation state is separate from design revisions.
- [ ] Derive a display mesh, collision representation and analysis mesh for
  their respective purposes; preserve mapping to the source revision and IDs.
- [ ] Interactive mode may use simplified/convex colliders, lower display detail,
  fixed-step physics with interpolated rendering, cached geometry and reduced
  numerical fidelity. Surface approximations and unsupported interactions.
- [ ] Move rigid parts by transforms during playback; do not rebuild exact CAD
  Booleans or regenerate engineering meshes every animation frame.
- [ ] Run expensive Boolean work, tessellation, collision preparation, physics,
  hashing and numerical processing in owned workers where supported; bound
  queues and cancel/discard results from outdated revisions. Keep the rendering
  path responsive and avoid full geometry copies or file sync each frame.
- [ ] Evaluate instancing, culling, reusable buffers, mesh detail and skinning
  independently of physical accuracy. A smooth rendered skin is not a solved
  deformation field. Rigid-body behavior does not establish material stress,
  thermal or electromagnetic correctness.
- [ ] Engineering mode records equations, units, material evidence, conditions,
  mesh/settings, convergence, relevant references and result provenance. Slow
  reproducible studies may reuse the design without blocking interactive work.
- [ ] Define and measure budgets on actual target hardware; do not promise
  universal real-time performance. Save authored edits and explicit checkpoints,
  not a stream of derived meshes or incidental simulation ticks.

## Deferred XR spatial workshop — separate branch, lowest priority here

- [ ] First load an existing design in browser WebXR at correct physical scale;
  provide inspect, orbit/approach, recenter and a clear way back to 2D.
- [ ] Place simple parts on a spatial work surface, combine them with supported
  operations, inspect dimensions and retain precise numeric editing controls.
- [ ] Support appropriate hand/controller selection and manipulation with
  snapping, axis/plane locks and one-handed alternatives; preserve mouse,
  keyboard and phone access to the same document operations.
- [ ] Present agent proposals, selections and measurements in the same scene.
  Preview/accept/reject and undo use the normal validated command history;
  no agent-only geometry representation or bypass of account/document checks.
- [ ] Keep visual manipulation temporary until an explicit modeling commit.
  During preview, use derived meshes and simplified physics; an unfinished
  spatial scene must not silently become an authoritative engineering result.
- [ ] Add optional immersive surroundings or passthrough placement only after
  the basic workshop works. Detect supported WebXR features and permission
  outcomes; preserve the ordinary browser experience when unavailable.
- [ ] Entry/exit, tracking loss, browser suspension, session interruption and
  window/account changes preserve saved designs and release session resources.
- [ ] Measure stereo frame timing, interaction latency, memory and comfort on
  the user's Galaxy XR. Emulation is development evidence, not headset proof.
- [ ] Do not assume every existing HTML app automatically becomes a usable 3D
  panel. Prototype the CAD work surface and minimal controls before spatializing
  the whole desktop or designing environments/assets.

## Primary references checked 2026-11-04

- [Replicad solid combinations](https://github.com/sgenoud/replicad/blob/main/packages/replicad-docs/docs/tutorial-overview/combinations.md): fuse, cut and intersect.
- [Manifold API](https://manifoldcad.org/docs/jsuser/classes/Manifold.html): solid triangle meshes, Boolean operations and input provenance.
- [Rapier](https://rapier.rs/) and [colliders](https://rapier.rs/docs/user_guides/javascript/colliders/): browser rigid-body motion, joints and collision representations.
- [WebXR on Android XR](https://developer.android.com/develop/xr/web): documented Chrome support and hand/spatial capabilities. Actual headset/browser feature availability still requires runtime and device checks.
