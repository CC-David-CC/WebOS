# Independent branch-crossing coordinate accuracy intake

Source preparation and correction only. Version2 has not been executed, including against historical receipts. No production file, original driver, numerical threshold, geometry reference or historical receipt changes are included. Root executes the revised checker only after source review and a terminal complete workflow.

## Preserved first refusal

Version1 source e02d8186a / root9c74c3627 was executed once after whole orientation R12 completed. Its output is retained as `antiparallel-coordinate-oracle-r1.json` under that workflow. It refused `Full source/inspection endpoint mismatch`. This was an incorrect checker intake assumption: it required retained coordinates to equal cold inspection coordinates bit-for-bit.

Root's actual post-edit B observations were retained source(599.8480775055449,151.73648176481407) and inspection(599.8480775314083,151.7364817693745) mm. Reported observation differences were25.8634145212pmX and4.5604338084pmY. These are reconstruction differences, not independently established geometry errors. No Version2 numerical result is asserted here. The first refusal and producing source remain preserved; it is not relabeled PASS or a production-corruption finding.

## Actual production contract

The producing Core32ae9c8a10659e43a3c5a5f4f51602b8aad64161 contains this call chain:

- `web/app/sketcher/headless/closedSketchInspection.ts::inspectClosedSketchTransition` calls `replaySketchTransition(request)`, parses its `serializedSketch`, and calls `projectRenderSketch` on that solved replay to produce public points. It does not project the retained input directly. Public object identities, constraint references/constants and frame are taken from that same replay.
- `headless/sketchTransition.ts::replaySketchTransition` calls `solveSketch` on the captured stored sketch, validates the full solved result with `assertVerifiedReplayGeometry`, and returns the genuine solved serialized copy. Its source comment explicitly states inspection does not write that copy back into the captured document.
- `headless/verifiedReplayGeometry.ts` preserves exact authored non-geometric intent and membership, checks actual constraint evidence, requires exact unsupported/unrelated geometry, and permits previously supported connected physical coordinates to reconstruct within the current50pm budget. It separately preserves directed branches and domain rules. That guard is repeatability, not independent accuracy.
- `headless/coordinateTransition.ts` verifies the requested endpoint exactly in the candidate it publishes, then independently bounds its cold replays; it publishes the original-source/scoped-delta candidate, not a copy of those optimizer outputs. The temporary endpoint LockPoint does not remain in saved intent.
- `cad/craft/closedSketchTransitions.ts::inspectClosedSketch` exposes the Worker inspection read without publishing its geometry. `docs/HEADLESS-SKETCH-SOLVE.md` describes disposable reconstruction and original-equation verification, and distinguishes returned solved data from publication authority. `docs/reviews/PHYSICAL-COORDINATE-RECONSTRUCTION-POLICY-20261108.md` distinguishes the physical-coordinate repeatability policy from accuracy.

Consequently public inspection does NOT promise bit-identical coordinates, or exact retention of a former transient endpoint driver in its independently solved copy. Version2 still requires the retained post-edit A endpoint to equal the actual public requested source coordinates exactly. It reports exact requested-A equality separately for replay inspection, and requires that replay endpoint to meet the SAME50pm accuracy reference. This is contract alignment, not a tolerance waiver or source writeback.

API clarity gap: the current public inspection point rows have no explicit `coordinateObservation:'cold-replay'` qualifier. The source implementation/comment is clear, while the broad historical headless document does not specifically label public inspection points versus retained-source values. That deserves future API documentation/descriptor clarification; it is not by itself evidence of accepted-source corruption. This packet changes no public wire.

## Separate actual observations

The unchanged orientation driver records accepted source in `before.accepted.native.source`, the same face's `native.sketches` entry, and cold public `inspection.points/constraints`. Version2 retains two separate full A/B datasets for each pre/post phase: `retained-source` and `replayed-inspection`. It never substitutes, averages or collapses one into the other. Each dataset is checked independently against one reference per phase and the same50pm per-coordinate bound. It also reports and checks source-to-inspection displacement under the separately declared50pm reconstruction contract; such agreement is not used as an accuracy reference.

The real source includes the datum LockPoint, ordered SignedDistanceX/Y anchor equations, factor-zero LengthRelation offsets and ordered Parallel180 row. Public append results and actual inspected endpoint bindings establish identity. Existing public/source identity, parent, stage, frame and equation/meaning guards remain. Datum ground binding retains its original explicit fixed-origin corroboration. No opaque-ID grammar, ordinal endpoint reconstruction, nearest-coordinate relabeling or new identity model is added.

R11's failed crossing has no full post-edit accepted snapshot. Its single Y diagnostic cannot supply missing X or anchors; this checker refuses `ORACLE_OBSERVATION_UNAVAILABLE` rather than inventing vectors. A terminal workflow that fails later may still provide a scoped earlier accuracy result; whole-workflow status stays visible. RUNNING receipts are refused without an accuracy result. Inspection revision and evaluated-solids revision are different token domains; they are recorded separately, never equated. The public endpoint request revision must equal the pre-state sketch-inspection revision.

## Unchanged independent truth and fixed budget

The frozen per-coordinate budget is exactly50pm=0.05nm=5e-8mm. Source/request numbers and literal constants use their actual represented binary64 values, not an unclaimed arbitrary-precision decimal-intent model. Rational arithmetic retains those values. A Decimal100 square-root approximation supplies candidate bounds, certified by exact rational square comparisons. All coordinate error decisions then use rational interval bounds without converting the reference back to binary64 or rounding before a decision. Ambiguous reference intervals refuse.

For the first A170-to190 edit, public requested A fixes the reference direction. The checker requires actual source LockPoint0 and ordered signed distances to fix A's ideal anchor at(560,150) and B's at(590,150). Both datasets' full anchors/endpoints are checked against these declared coordinates and the independently derived B endpoint:

`B_end = B_anchor - fixed_length_B * (requested_A_end - A_anchor) / |requested_A_end - A_anchor|`.

Neither production geometry math nor replay agreement defines this reference. Actual vector dot/cross and requested A norm versus its separately stored fixed length are reported. That slight represented-input discrepancy must remain within50pm for this fixture and is not called an exact joint solution. The directed vectors must cross the left angular chart while retaining the opposed branch.

Before that endpoint request, the pair has a free angular DOF. The retained pre-state A direction is explicitly conditional reference input for BOTH datasets, not an independent A-angle proof from the append's nominal170 degrees. Replay A is never used to define a separate reference that could conceal its error. The initial public append endpoint remains visible. Extra constraints incident on the pair put the fixture outside the bounded domain rather than being ignored.

## Custody and use after review / whole terminal run

Use a fresh output path; preserve r1. Supply exact expected runtime pins and frozen producer commits, which may differ. The checker verifies the receipt's five producer source pins against actual Git objects for the original three orientation files and two Desktop agent/helper files. It never assumes current mutable files are the producing versions. Original before/after producer hashes must match. The receipt SHA and retained source SHAs are reported; no replayed serialized sketch was captured publicly, so no replay-source hash is fabricated. The actual replay points remain bound by the receipt and its producing workflow.

```sh
python3 test/agent-cad-corpus/orientation-precision/check_antiparallel.py \
  /path/to/TERMINAL-WHOLE-RUN/receipt.json \
  --runtime-core FULL_ACTUAL_CORE_COMMIT \
  --runtime-desktop FULL_ACTUAL_DESKTOP_COMMIT \
  --core-repo /tmp/codi-acad-main-20261107 \
  --producer-core FULL_COMMIT_CONTAINING_THE_PINNED_ORIENTATION_DRIVER \
  --desktop-repo /tmp/codi-desktop-mechanical-candidate-20261105 \
  --producer-desktop FULL_COMMIT_CONTAINING_THE_PINNED_AGENT_AND_HELPER \
  > /fresh/output/antiparallel-coordinate-oracle-r2.json
```

Version2 emits four phase/view observations and two explicit reconstruction comparisons. Exit0 is scoped success, not whole Gate1/general50pm accuracy. Exit1 is measured coordinate/branch/length-compatibility or reconstruction failure. Exit2 is unsupported/missing/badly bound intake or unresolved reference. Preserve the first output without changing its budget. Intake remains128MiB receipt/1MiB accepted source, separate from account-file policy.

This is a recorded-data check, not a fresh Native point certificate or an adversarial authentication proof for arbitrary JSON. All other operation accuracy, Native/BRep, atomistic behavior, nanoscale materials, fabrication and universal solver accuracy remain outside its claim.
