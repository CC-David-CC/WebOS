# Current functional gates: Files and CAD

Latest bounded acceptance: CAD runtime `b3ccb284b` / desktop `680f79d88`
closes the typed-editor and rigid-boundary defects and passes signed bracket,
shared parameters, role/rigid operations, material enclosure and core 3MF.
See `tests/jsketcher-b3-combined-signed-20261105.md` and current work queue.
Configurations, complete mutation/worker-performance and final beta remain open.
Older pending states below are superseded only within that receipt's scope.

The full objective in FILES-CAD-RELEASE-OBJECTIVE.txt remains intact. Scoped passes do not qualify an entire CAD feature family.

**Files foundation is accepted within its tested scope. CAD is the active work.** Signed tests cover persistence, account isolation, conflicts, changed-chunk sync and interruption/crash recovery through representative 128 MiB files. No new Files-service defect is established. Every-app compatibility, automatic GC, classroom capacity and power-loss guarantees are not implied.

| Order | Functional gate | State | Acceptance / next work |
|---|---|---|---|
| 1 | Reliable CAD replay, Save and reopen | Accepted bounded b3; final release open | Exact b3/680 signed bracket, typed parameters, menu, role/rigid and material enclosure workflows pass Save/sync/fresh Files reopen. See tests/jsketcher-b3-combined-signed-20261105.md. New configurations and reference repair need combined qualification. |
| 2 | Sketch correctness and persistence | Partial; carried regression passes | Exact b3 spline IDs/history/DXF/selection/touch and Worker/native controls pass, including invalid-Angle preservation. Not the full CAD1 primitive/profile catalogue or rank diagnostics. |
| 3 | Mechanical dimensions and parameters | Bounded listed-operation passes; configurations/performance open | X/Y/projected/diameter/concentric, collinear/axis symmetry, whole-entity fixing, rigid groups and physical length relations/reference-driving conversion have scoped UI/Worker/agent/native evidence. b3 adds shared rectangle/hole/enclosure propagation; configurations are under signed test. Full mutation inventory/worker-first capture remain. |
| 4 | Dependable parametric parts and reference repair | Bracket/enclosure bounded pass; explicit repair gap | Public edits preserve parameters, materials, undo and signed Files. Review768c9985d/e68eb13f9 demonstrates missing-parent navigation but no successful existing hole-parent reselection; guarded full-suffix repair and failed-state undo are in development. |
| 5 | Shared human/agent operations | Accepted bounded b3; configuration/repair adapters pending | Public operations create/edit/reject/undo/save bracket and enclosure; native UI shares model operations. Signed rigid/line tests helper-seed geometry, so do not prove public primitive creation. Configuration adapter9a passes61 command tests; signed proof pending. |
| 6 | Material-aware core 3MF | Accepted bounded b3; configuration export pending | Three b3 signed outputs independently verify two objects, three regions, units, grouping, transforms, materials and closed geometry. Not arbitrary bodies, rendered lettering, printing or physics. |
| 7 | Final combined app and beta | Open | Finish configurations, reference repair, measured worker/mutation boundary and final affected regressions; then source/runtime delivery and managed beta. Carried tests cover both engines/windows; f546 has desktop orbit/resize and emulated touch orbit/pinch. No physical-device claim. |

**User direction: source packaging comes after the functional gates.** The pending packaging edit was discarded. Defer archives, packaging/provenance expansion and new command-catalogue diversions. Final source/runtime delivery and managed beta activation remain in the full objective afterwards; neither is complete.

November 5 update: combined d6253ea9 is promoted after actual rectangle fault/no-op controls, the held-dialog autosave control and the independently repeated signed command-only bracket pass. Native authored Undo/Redo actions are also integrated through 24d52ae8 after actual menu/key/focus/busy controls, signed menu save/reopen and reentrant reset checks repeated by root. Broader M02/M03/M04 coverage remains open. No new deployment.

Intermediate/advanced CAD, assemblies, physics, inverse design and XR remain in later queues. This does not declare the entire CAD 1–6 program complete.
