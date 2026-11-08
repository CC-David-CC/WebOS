# Independent branch-crossing coordinate accuracy intake

Source preparation only. The checker has not been executed, including against historical receipts. Run it only after the complete original orientation workflow is terminal. No production file, driver, acceptance threshold, old checker or historical receipt changes are included.

## Sufficient and missing observations

The unchanged orientation driver records the necessary accepted full vectors in its `... raw` rows: `before.accepted.native.source`, the same face's entry in `native.sketches`, and public `inspection.points/constraints`. The source includes the real datum LockPoint, ordered SignedDistanceX/Y anchor equations, factor-zero LengthRelation offsets and ordered Parallel180 row. The receipt retains actual public append results, genuine inspected endpoint bindings and exact endpoint-edit request arguments. The first successful crossing has distinct pre/post raw labels.

R11's failed crossing has no full post-edit accepted snapshot. Its single Y field diagnostic cannot supply the missing X or anchors. This checker refuses `ORACLE_OBSERVATION_UNAVAILABLE`; it does not invent a warm/cold vector from that historical failure. A terminal run that fails later may still provide a scoped check of an earlier completed crossing; the output prominently retains its whole-workflow FAIL status. A RUNNING receipt is refused without any accuracy result.

Inspection revision and evaluated-solids revision are different token domains in the real captured schema. They are recorded separately, never equated. The actual endpoint request revision must equal the pre-state sketch inspection revision. Public inspected point IDs, public append-returned Segment IDs and explicit source references are compared verbatim: no opaque-ID grammar, ordinal endpoint reconstruction or nearest-coordinate identity lookup is used.

## Independent truth and fixed budget

The frozen per-coordinate budget is exactly 50 pm = 0.05 nm = 5e-8 mm. Literal constants and public source/request numbers are interpreted as their actual represented binary64 values, not as an unclaimed arbitrary-precision decimal-intent model. Exact rational arithmetic retains those values. A Decimal100 square-root approximation supplies a candidate enclosure; exact rational square comparisons certify the enclosing positive bounds. All coordinate pass/fail comparisons then use rational interval error bounds, without converting the reference back to binary64 or rounding before a decision. Unresolved reference intervals refuse instead of rounding into a pass.

For the first A170-to190 edit, the public request fixes A's endpoint. The checker requires the accepted source endpoint to equal that request exactly. It verifies a real LockPoint fixes the common datum at(0,0), and the actual ordered signed-distance rows independently fix A's anchor at(560,150) and B's at(590,150). Both anchor coordinates and both full endpoints are checked against the finite budget, with source/inspection equality corroboration. The B reference is

`B_end = B_anchor - fixed_length_B * (requested_A_end - A_anchor) / |requested_A_end - A_anchor|`.

No production solver/trigonometry/reduction helper is imported. This derives both B coordinates, rather than checking replay agreement or comparing two kernels. Actual vector dot/cross and the requested A norm versus its separately stored fixed length are reported. The latter discrepancy must remain within50pm for this fixture; it is not falsely called an exact joint solution of slightly different represented inputs. The actual directions must cross the left angular chart and retain the opposed branch.

Before that endpoint request, the pair has a free angular degree of freedom. Its pre-state A direction is explicitly conditional reference input for the B equation, not an independent A-angle accuracy proof from the append's nominal170 degrees. The initial public append endpoint is retained in the output, and all datum/anchor/length/branch requirements must match between pre/post states. Other constraints incident on either pair member put the fixture outside this bounded oracle domain rather than being ignored.

## Custody and use after the whole run

Use a fresh output path. Supply exact expected runtime pins and frozen producer commits; they may be different commits. The checker verifies the receipt's five source pins against actual Git objects for the original three orientation files and the two Desktop agent/helper files. It never assumes the current mutable checkout contains the producing files. Source hashes must also match the original driver's after-run hashes. The complete receipt SHA and both observed source SHAs are reported.

```sh
python3 test/agent-cad-corpus/orientation-precision/check_antiparallel.py \
  /path/to/TERMINAL-WHOLE-RUN/receipt.json \
  --runtime-core FULL_ACTUAL_CORE_COMMIT \
  --runtime-desktop FULL_ACTUAL_DESKTOP_COMMIT \
  --core-repo /tmp/codi-acad-main-20261107 \
  --producer-core FULL_COMMIT_CONTAINING_THE_PINNED_ORIENTATION_DRIVER \
  --desktop-repo /tmp/codi-desktop-mechanical-candidate-20261105 \
  --producer-desktop FULL_COMMIT_CONTAINING_THE_PINNED_AGENT_AND_HELPER \
  > /fresh/output/antiparallel-coordinate-oracle.json
```

Exit0 means the two stated observations meet this scoped oracle, not whole Gate1 or general50pm accuracy. Exit1 is an actual measured coordinate/branch/length-compatibility failure. Exit2 is unsupported/missing/badly bound intake or an unresolved reference. Preserve every first output and investigate its exact cause without loosening the frozen budget. Intake is bounded to128MiB of receipt and1MiB per accepted source, independent of account file policy.

This is a recorded-data check through an independently derived equation. It is not a fresh Native point certificate or a cryptographic/adversarial proof that arbitrary supplied JSON came from the running application. Native/BRep, all other orientation stages, nanoscale material, atomistic behavior, fabrication and universal solver accuracy remain outside its claims.
