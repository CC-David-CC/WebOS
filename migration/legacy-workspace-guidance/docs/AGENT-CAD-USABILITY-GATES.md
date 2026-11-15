# Agent authoring and human viewing: CAD1/CAD2 gates

These labels follow the user's conceptual CAD1–6 ladder. This is not a product-edition claim or a replacement for the original release objective, full Gate1 exercises or ARC18–22. Tested plate/enclosure examples already let agents create/edit/save/reopen and people view results; that is a bounded working slice, not general CAD.

## CAD1: geometry authored by agents, viewable by people

| Requirement | Current evidence / remaining work |
| --- | --- |
| Public create/inspect/edit/delete for basic sketch entities | Public rectangle, box/Boolean, plate/hole/enclosure factories exist. Closed-sketch Worker inspection now exposes entity/constraint IDs and public LengthRelation edits with native history. Many other relation commands operate on existing entities; some tests helper-seed line/circle geometry. Public empty-plane/Point/Segment/Circle/Arc creation now passes the same validated core API, shared undo/redo and signed fresh-login Save/reopen on1b2. Final997 signed creation/save/reopen also passes; independent997 readiness/projection controls also pass, including all three advertised planes and atomic unsupported-ancestry refusal. General entity editing/deletion remains open. Constraint-menu presence is not public primitive creation. |
| Profiles and explicit region selection | Authored rectangle/prism workflows pass. General disjoint/nested/intersecting/touching-region competency remains in the full Gate1 matrix; do not infer it from a rectangle factory. |
| Correct acceptance/refusal and usable failures | Bounded shared action/Worker and native engine controls pass; unknown/lower-dimensional/nonmanifold cases remain explicit. Keep geometry validity, solver consistency, planar regions, kernel validity and dependency identity separate. |
| Worker-first editing/history with current publication | Closed-sketch agent edits now publish through private full-history replay without opening the2D editor; real public relationship/resize/refusal/shared travel/Files tests pass on5f8. The active editor and concrete514-segment/512-lock stall remain; a Worker solve followed by the old synchronous solve is insufficient. |
| Human viewing | Existing viewers display the tested results. Read-only viewing should consume accepted geometry and identity, with coherent unavailable/stale status; a redesigned full human modeling UI is not a prerequisite for agent-driven authoring. |
| Files and lifecycle | Signed bounded My files save/sync/reopen/account/close controls pass. Final combined runtime/deployment qualification remains separate. |

## CAD2: dependable parametric changes

| Requirement | Current evidence / remaining work |
| --- | --- |
| Parameters, units, formulas and configurations | Bounded typed quantities/bindings/variants and invalid-value retention pass. Do not imply all dimensional domains, display-unit conversions or every expression family is qualified. |
| Downstream regeneration and references | Plate/enclosure edits and explicit centered-hole parent repair pass. General disappearing/split/ambiguous topology still requires repairable failure and broader qualification. |
| Whole-design undo/redo and persistence | Bounded public closed-sketch relationship plus dependent dimensional edits preserve intent across Worker-backed travel and signed reopen. Central immutable feature history fixes the reproduced prepared/new-feature/timeline faults; actual fault and fresh-native tests pass. Broader active-editor history, raw-input provenance and large-container processing remain. |
| Full acceptance part | Complete the user's original-rectangle exercise through dependent holes/cuts, fillets/patterns where supported, units, undo/redo and native reopen; retain separate edge-case tests. Prepared part factories alone do not close general modeling. |
| Manufacturing handoff | Bounded model-derived core3MF independently preserves2 objects/3 material regions. Generic STEP/3MF and arbitrary geometry remain separate qualification. |

Current427 additionally fixes delayed publication after cancelled native import, preserves signed primitive/family/material workflows, and improves the measured contour/index paths. The2,000-plane scene stall and active2D migration remain open; see CAD test/replay-contour/README.md.

Order: finish the Worker computation/publication foundation; expose basic authoring through that same core; qualify profile selection and ordinary parts; then broaden dependable feature dependencies. These are dependencies, not a request to postpone all useful tested slices until the entire CAD1–6 roadmap exists. No percentage or ETA follows from command counts.
