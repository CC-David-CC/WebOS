# SolidCore repair discussion

The two required cornered radius-law regressions passed on WebOS commit
`71a573e234418b8f30106124505aabaaa1aac287`. The tests verified the rolling-ball
geometry, retained control-parameter identities, native save/reopen and
Undo/Redo. The production component was built on R730 and verified after transfer to the
laptop. Its 64,861,240-byte archive has SHA-256
`071cb3d5f8f583d63f64b29c382befe9573f984aec04045f7022b4345214c815`.
All 23 content files match the commit-bound build manifest.
The signed account suite reopened all four fillet fixtures with the expected geometry. SolidCraft is live in release `22b0211e018ae27561ce943a666fb730f795a07e3c016bd084c77d415fb51f0f`. [Release checks and rollback](CRAFT-INTEGRATION-LOG.md#solidcraft-release-on-ksucodes)

## Public SolidCraft fillet contribution

[SolidCraft PR #19314](https://github.com/tangency-labs/solidcraft/pull/19314) proposes the cornered-radius repair against Tangency Labs main `b695a9b35294`. The source branch is `CC-David-CC/solidcraft:fix/route-cornered-variable-fillets`, commit `db35c5adead7`. The five focused engine, kernel and adapter tests and workspace Clippy passed on that base. The WebOS account integration remains on `webos/solidcraft-account-fillet-repairs`. The PR description links a browser screenshot of the synthetic peak model from an evidence branch on the fork.

## Editor and kernel source

SolidCraft is the parametric editor. Its `solidcore/` subtree contains the
Rust B-rep kernel derived from NVIDIA SMLib. Tangency Labs' `smlib` repo is
a C++ USD BRep fork. The standalone `solidcore` repository mirrors the Rust
subtree. The current SolidCraft contribution guide on upstream main
`b695a9b35294` sends both application and kernel pull requests to
SolidCraft's `main` branch.
[Upstream contribution guide](https://github.com/tangency-labs/solidcraft/blob/b695a9b352949f3d14c5ac47c6b8a8f97a15830d/CONTRIBUTING.md)
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
open before adopting this ACAD base.
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
recovery and fresh-browser editing. The pinned upstream test list contains all four geometry cases. Its corrected-hole branch still reproduced all three fillet failures.
[Pinned upstream test list](https://github.com/tangency-labs/solidcraft/blob/6afe1611c62691337933c5b0e57b528d8f1618b2/tests/KNOWN_FAILING_TESTS)

| Case | Verified finding | Remaining work |
|---|---|---|
| `a_hole_wider_than_the_part_says_it_removes_all_of_it` | The 40 mm cutter through the 40 × 30 × 10 mm plate at (10, 10) leaves two solids where the bore touches the edge. Their combined volume is 4,031.9614 mm³. The native probe checked complete removal at 100 mm and restored a single solid at 5 mm. The corrected test passed independently on both WebOS `189330449f8a` and newer upstream `7e6605729d14`. | Optional upstream submission of the test correction. |
| `inserting_variable_fillet_control_preserves_parameters_at_existing_positions` and `chord_and_variable_fillets` | Both reproduce the cornered radius-law refusal documented in SolidCore issue #430. The 2 → 4 → 2 mm waist and the two-control-point law both have an abrupt slope change. The control-insertion test stops while creating the initial fillet. Refusal preserves the authored model and saved part. | Both original engine tests passed on WebOS `71a573e23441` after routing the unchanged controls to the vendored kernel. The inserted-control test also passed native save/reopen and Undo/Redo. [SolidCore issue](https://github.com/tangency-labs/solidcore/issues/430) |
| `fillet_fit_taper_closes_to_a_point` | The direct kernel wedge test passed with both upstream fix settings, as did the zero-radius box controls and radius-law evaluation. SolidCraft’s constant 16 mm radius fails to build the corner. Its fit command propagates that failure before trying the taper. Explicitly applying the app’s own generated spline to the same edge succeeds and reduces volume from 42,000 to 41,245.7293 mm³. | WebOS `d34f4440a55f` passed the fitted-wedge test, adjacent taper tests, both hole cases and account save/recovery. The same repair passed the wedge test on pinned newer upstream. |

The pinned Rust kernel already splits radius-law faces at their corners.
The WebOS and newer upstream kernel probes each applied four degree-one
laws with the original control positions, with both upstream fix settings.
Level 2 B-rep checks passed in all 16 cases. The 2 → 4 → 2 mm peak, its
3 mm revision, the two-control law and the inserted-control law yielded
8, 8, 9 and 10 faces. Removed volumes agreed with an independent rolling-ball
integration to within 0.0006 mm³. SolidCraft’s adapter had an explicit guard
that returned an error before passing such laws to this kernel. The
application-level repair removes that obsolete guard.

For all three fillet refusals in the original WebOS candidate, a native
account-container probe checked the complete authored document, measured
volume and clean state before and after the command. A second attempt from an already-dirty part also kept its pending edit and dirty flag. Opening a second
save produced the same document as opening the first. The part accepted
a subsequent edit and its recovery draft reopened. The in-memory revision
advanced by two on rejection. The account adapter reports dirtiness
separately. Private receipts are under `solidcraft-geometry-resume.qS91vLP4/`
in the checkpoint directory.

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
| `main` | `b695a9b35294` | Fast-forwarded to the verified Tangency Labs main used for the corner-law PR |
| `webos/solidcraft-account-part` | `7b7716fba56c` | Earlier WebOS account candidate |
| `fix/tangent-hole-regression` | `7e6605729d14` | Hole-test correction based on upstream main |
| `webos/solidcraft-tangent-hole-review` | `189330449f8a` | Same correction based on the WebOS integration |
| `webos/solidcraft-zero-tip` | `d34f4440a55f` | Verified tapered-wedge repair on the WebOS integration |
| `webos/solidcraft-account-fillet-repairs` | `71a573e23441` | Final geometry candidate with all 13 focused native tests passing |
| `fix/route-cornered-variable-fillets` | `db35c5adead7` | Six-file corner-law fix based directly on Tangency `b695a9b35294`; five native regressions and whole-workspace Clippy passed |

The private checkpoint linked from [START-HERE](../START-HERE.md) names the
native differential receipts, archived SolidCraft candidate, exact hole
probe, review patches and ACAD comparison. The two review commits are local.
The native geometry probe used the pinned engine. Fresh isolated R730 builds
ran the corrected hole test on both branches. Each selected one test and passed.
The four generated browser regression models live in
`solidcraft-geometry-resume.qS91vLP4/law-fixtures/` under the private checkpoint.
Their manifest records each model’s SHA-256, native volume in mm³, feature
count and solid count after saving and reopening it.

## Two thin-wall refusal diagnostics in upstream CI

The fillet rig ran on upstream main `b695a9b35294` and on PR head `db35c5adead7`. All 271 case names, statuses, error messages and refusal messages matched between the two result artifacts. Cases 1668 and 2852 refused rounds that would open a hollow wall. Their diagnostics omitted the largest radius that fits. This made the upstream gate fail on both commits. The three reported 1080 continuity cases are recorded in upstream’s known-failing list. [Upstream main run](https://github.com/tangency-labs/solidcraft/actions/runs/44435832894) · [PR run](https://github.com/tangency-labs/solidcraft/actions/runs/44439157727)

The independent WebOS component `71a573e23441` returned both required limits. It refused a 7 mm round on the 2 mm wall and reported 6.828 mm. It refused the 30 mm round on the 3 mm U-shell and reported 25.24 mm. The engine checks compared the authored features, solids and volume before rejection, after rejection and after saving and reopening each model. The separate upstream contribution continues to target variable-radius fillets.
