# SolidCore repair discussion

SolidCraft remains disabled on ksu.codes. Keep its WebOS account branch and
its local qualification evidence available while researching the geometry.
TextureCraft is live as app 15 of 18. The general rollout is paused at the
MaterialCraft native checkpoint. SketchCraft remains queued.

## What we proved

The original selected SolidCraft source at `a5b35abd133e` and the WebOS
integration at `7b7716fba56c` reproduced the same four native cases. The
local account candidate also passed six browser checks with a live editable
parametric part, including confirmed Save and Save As, Files Open, draft
recovery and fresh-browser editing. The current upstream test list still
contains the four geometry cases.
[Pinned upstream test list](https://github.com/tangency-labs/solidcraft/blob/6afe1611c62691337933c5b0e57b528d8f1618b2/tests/KNOWN_FAILING_TESTS)

| Case | Verified finding | Remaining work |
|---|---|---|
| `a_hole_wider_than_the_part_says_it_removes_all_of_it` | The 40 mm cutter through the 40 × 30 × 10 mm plate at (10, 10) leaves two solids where the bore touches the edge. Their combined volume is 4,031.9614 mm³. The native probe checked complete removal at 100 mm and restored a single solid at 5 mm. | Run the corrected upstream test on the pinned newer main. Decide whether to share the small test correction upstream. |
| `inserting_variable_fillet_control_preserves_parameters_at_existing_positions` and `chord_and_variable_fillets` | Both encounter the cornered radius-law limitation documented in SolidCore issue #430. | Decide whether support for an explicit cornered law is useful enough to pursue. Preserve the requested law when evaluating a kernel change. [SolidCore issue](https://github.com/tangency-labs/solidcore/issues/430) |
| `fillet_fit_taper_closes_to_a_point` | The 16 mm fitted fillet closes toward zero radius and reports status 1001. | Run `taper_closing_to_a_point_rounds_the_wedge` at the kernel boundary. The pinned fixture checks the same wedge with both `Fixes::None` and `Fixes::All`. If it passes, compare the feature's body, chosen edge, radius law and flags with the passing fixture. The direct fixture has yet to be run for this investigation. |

The ACAD through-hole planner rejected that same cutter at its clearance
check with `HOLE_OUTSIDE_PROFILE`. A smaller cutter at the same position
passed the clearance check. The raw OCCT Boolean on the original shape is
still unverified. Compare direct geometry operations when assessing kernels.
Compare the editable history, stable identities, failure reporting, and the
human and agent command path when assessing the tools.
[ACAD kernel interface](../apps/acad/modules/engine/solid/SolidKernel.ts)

## Long-term CAD comparison

SolidCraft has an editable parametric browser candidate with a tested
account round trip. ACAD already models the design as an application-owned
feature history and runs geometry in worker adapters for OCCT, Manifold and
SMLib. Its documented workflows have prior qualification evidence. Its
current WebOS host wiring and full CAD qualification remain open.

Evaluate two layers independently on the same dimensioned parts. At the
geometry layer, compare Boolean and fillet results, native validity, body
count, dimensions and volume, with each representation's tolerances made
explicit. At the tool layer, change an earlier feature, replay the design,
check how references and failed edits are handled, and verify that UI and
agent commands hit the same transaction and Undo path. Rerun the same model
after saving and reopening it. Then decide which engine and editor choices
are justified for the workflows WebOS needs.
[ACAD scope](../apps/acad/README.md)
[SolidCore taper fixture](../apps/solidcraft/solidcore/crates/solidcore/tests/fillet_variable_radius_closes_onto_vertex.rs)

## Local source and evidence

| Branch in `apps/solidcraft` | Pin | Purpose |
|---|---|---|
| `main` | `6afe1611c626` | Fast-forwarded to the verified Tangency Labs main |
| `webos/solidcraft-account-part` | `7b7716fba56c` | Paused WebOS integration |
| `fix/tangent-hole-regression` | `7e6605729d14` | Hole-test correction based on upstream main |
| `webos/solidcraft-tangent-hole-review` | `189330449f8a` | Same correction based on the WebOS integration |

The private checkpoint linked from [START-HERE](../START-HERE.md) names the
native differential receipts, archived SolidCraft candidate, exact hole
probe, review patches and ACAD comparison. The two review commits are local.
The native geometry probe used our pinned engine. Validation on the newer
upstream binary is still open.
