# Current functional gates: Files and CAD

The full objective in FILES-CAD-RELEASE-OBJECTIVE.txt remains intact. Scoped passes do not qualify an entire CAD feature family.

**Files foundation is accepted within its tested scope. CAD is the active work.** Signed tests cover persistence, account isolation, conflicts, changed-chunk sync and interruption/crash recovery through representative 128 MiB files. No new Files-service defect is established. Every-app compatibility, automatic GC, classroom capacity and power-loss guarantees are not implied.

| Order | Functional gate | State | Acceptance / next work |
|---|---|---|---|
| 1 | Reliable CAD replay, Save and reopen | Partial; current blocker | Bracket edits, rejection and undo/redo must consistently save exact bytes and reopen. Diagnose intermittent prism/four-corner deadlines without simply increasing them; preserve the last valid model. Current traces implicate fixture/browser request delivery before native execution; cause is not yet proven. |
| 2 | Sketch correctness and persistence | Partial | Stable IDs across drawing, undo/redo and reload; geometry validity, constraint consistency and region topology stay distinct. Spline fix a22859f5 passes focused/strict-IO and rebuilt desktop/phone replay; corrupted duplicate-ID samples stay rejected. This does not close every primitive/constraint case. |
| 3 | Mechanical dimensions and parameters | Partial; required coverage open | Qualify driving X/Y/projected dimensions, diameter, concentric/collinear, entity fixing, rigid groups, axis symmetry, equality/ratio/difference and driving/reference roles. Typed quantities, formulas, dependency errors and configurations must support the acceptance designs. Focused solver passes do not close UI/part coverage. |
| 4 | Dependable parametric parts | Partial | Block/washer, then bracket and enclosure/lid. Change dimensions, hole spacing/depth; reject impossible edits; preserve dependencies, references, undo/redo and native persistence. Block/washer have bounded core/replay passes. Enclosure signed workflow passes; bracket reliability remains open. |
| 5 | Shared human/agent operations | Partial | Discover operations/entities; create/edit/inspect/reject/undo/save/reopen through the same validated operations. Existing rectangle, extrusion, hole and material commands are partial evidence. No AI provider is required. |
| 6 | Material-aware core 3MF | Bounded pass | Native design stays editable. Body is a separate print object; recessed lid and rectangular insert form another, with distinct material/appearance regions. Signed initial/edited exports pass independent units, grouping, mesh, bounds/volume and interface checks. Not arbitrary geometry, lettering or physical printing. |
| 7 | Final combined app and beta | Open | Qualify affected carried features, selection/DXF/camera/touch, independent windows, accounts, cancellation/disposal, CSP and signed files on the final build. Keep OCC preferred and Native Mesh honestly supported. Reuse unaffected evidence; fix actual failures, then qualify beta. |

**User direction: source packaging comes after the functional gates.** The pending packaging edit was discarded. Defer archives, packaging/provenance expansion and new command-catalogue diversions. Final source/runtime delivery and managed beta activation remain in the full objective afterwards; neither is complete.

Intermediate/advanced CAD, assemblies, physics, inverse design and XR remain in later queues. This does not declare the entire CAD 1–6 program complete.
