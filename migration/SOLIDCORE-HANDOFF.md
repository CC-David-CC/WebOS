# SolidCore repair discussion

SolidCraft remains disabled on ksu.codes. Keep its WebOS account branch and
its local qualification evidence available while researching the geometry.
TextureCraft is live as app 15 of 18. The general rollout is paused at the
MaterialCraft native checkpoint. SketchCraft remains queued.

## Editor and kernel source

SolidCraft is the parametric editor. Its `solidcore/` subtree contains the
Rust B-rep kernel derived from NVIDIA SMLib. Tangency Labs' `smlib` repo is
a C++ USD BRep fork. The standalone `solidcore` repository mirrors the Rust
subtree. The pinned contribution instructions route kernel-only changes
through SolidCraft's `kernel` branch.
[SolidCraft kernel source](../apps/solidcraft/solidcore/README.md)
[Tangency Labs SMLib](https://github.com/tangency-labs/smlib)

ACAD has its own C++ SMLib builds. The organized `engines/usd-brep/` repo
contains NVIDIA base `3fd5b9548d19`, our native binding `e854d6ced388`, and
experimental kernel `6c99bfcfe6c7`. The separate `engines/smlib-wasm/` repo
contains the older wrapper fork `c97a8e76e260`. All three owned commits were
verified in the local Git object stores. The direct provider has scoped
Chromium evidence for native Boolean results, voids and multiple material
regions. Its through-hole and variable-fillet equivalence for these fixtures
remains unverified.
[ACAD direct SMLib provider](../apps/acad/modules/engine/raw-smlib/README.md)
[Direct provider build pins and browser evidence](../apps/acad/test/raw-smlib-whole-void/README.md)

The source comparison used NVIDIA `main` at `3fd5b9548d19`. Tangency Labs'
C++ `smlib` main at `8eac63c439b2` was 665 commits ahead and zero behind.
ACAD's direct binding and experimental kernel were six and eight commits
ahead, respectively, and zero behind. The older `smlib-wasm` wrapper fork
was two commits ahead of its own wrapper upstream `1ffd5708dd19`.
[Public fork comparison](https://api.github.com/repos/NVIDIA-Omniverse/usd-brep/compare/3fd5b9548d19aa8c12c29bc9637a96d42a06f8a5...tangency-labs:main)

## ACAD C++ patch replay on Tangency SMLib

All eight commits from NVIDIA `3fd5b9548d19..6c99bfcfe6c7` cherry-picked
cleanly in order on Tangency `8eac63c439b2` in an isolated repository.
The result tree was `b87c15d724b0d9b32b67de03f4e4a07c23b24ba1`. Only
the last commit changes kernel source. The first seven supply ACAD bindings,
probes, tests and historical results.

The Linux x86-64 static archive from the matching upstream release passed its
published SHA-256 check. The ACAD union regression ran directly against SM_API
using that archive. For the candidate, the two changed translation units
were compiled with g++ and replaced in the archive. As a compiler control,
the same procedure using pristine source reproduced the original JSON byte
for byte. All three native probes exited zero.

| Union in the previously failing operand order | Tangency volume, mm³ | Tangency + ACAD patch, mm³ | Expected, mm³ |
|---|---:|---:|---:|
| Hollow cube and exact cavity fill | 0 | 1000 | 1000 |
| Same fill with a second disjoint cube present | 2000 | 2000 | 2000 |
| Hollow cube and enclosing fill | 0 | 1000 | 1000 |

For the two failing cases, the patch changes zero material regions and
one void to one material region and zero voids. The other 24 recorded
observations match across builds, including all three reverse operand orders.
The direct SM_API result establishes a reason to retain the patch on a
review branch. A complete WASM build and ACAD browser regressions are still
open before adopting this base. The Craft rollout remains paused.
Private receipts and native probe source are under
`smlib-tangency-replay-8eac63c4.RoVVkT/` beside the migration checkpoint.
[Pinned Tangency release](https://github.com/tangency-labs/smlib/releases/tag/prebuilt-8eac63c439b2670ecffcc2d7beaf2242849463bf)

### Upstream union fix prepared for review

The public fork already had a narrower version of the kernel fix on its
NVIDIA-based branch. The Tangency-based submission uses that fix, 23 lines
in the existing Boolean test executable and a changelog entry. Its two
commits end at `b00a52ae295c76d7cc0887ad10c480195bd9af31` on
`CC-David-CC/usd-brep:fix/retain-material-on-cavity-fill`. The new test
failed twice on upstream for volume and solid count. Both operand orders
passed on the candidate for exact and enclosing fills. The entire native
Boolean executable passed all 18 cases. Testing linked the upstream Linux
archive with the two modified kernel translation units rebuilt locally.
Evidence is in `smlib-union-pr-b00a52a.XNtjj0/` beside the private checkpoint.
[Open upstream PR 136](https://github.com/tangency-labs/smlib/pull/136)

Track Tangency PR 131 separately for ACAD's future C++ extrusion tests.
It handles a nearly straight spline whose extruded wall fails a geometry
check after export/import. It can be evaluated independently of the
box-only union correction. When adopting a Tangency kernel, check the
published merge status and exercise the round trip in the selected WASM build.
Independently tested PR 131's two source/test changes against the pinned
Tangency main. The native sweep executable failed on the baseline with
an invalid cylindrical wall and passed with the sweep change. The returned
body passed the validity check after export/import.
[Tangency PR 131](https://github.com/tangency-labs/smlib/pull/131)

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

For a staged WebOS integration, mount each editor independently and reuse
Files, account Storage, recovery and scoped commands. Each editor owns its
native projects and editing history. Compare engines using pinned builds
and identical geometry inputs before considering a provider change. Start
with a direct SolidCore taper test and a direct C++ SMLib Boolean on the
known plate and cutter. The latter bypasses ACAD's authored through-hole
clearance rule and can measure the native result. Exercise supported ACAD
workflows through its command stack separately.

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
