# Terminal, ACAD and Craft updates

The approved goal covers the existing ksu.codes viewer and the 20 currently registered Craft editors. The legacy JSketcher fork and the optional PCBCraft packager have separate source owners.

## Terminal

Live release `9866ceba34bcbaebd863de4fc8289fe4df28e293732c8064c0f3f358d0537654`, verified in Chromium with an isolated test account. Local source-built assembly and hosted browser checks passed. Sign-in and Files issue zero guest asset requests. Two concurrently open windows get independent PTYs on one v86 Worker. Closing shells removes their sessions, reopening retains temporary guest home, and stopping the guest terminates its Worker and clears the filesystem handle. An account upload retains exact bytes on the server and stays separate from guest files.

- Terminal `a6bae78831c5f9218147c0253d295fa4981a4879`, Desktop `22c1b12bd6a972208a818657970f9efc6d857ecf`, Linux `584bbeaee1e15f36b603ed20bcb2cc6dd58b38dd`, v86 `c2c6a3296c631746fbc2f55c6c34bb5739c36784`.
- Parent source commit `f9fda5ea59734c1dfe97eebdfaf443d56833f93c`. App bundle `991370da47e178b8dcff2ed3feb2aa807ab4206a2e063184a1f0a1612f592c28`.
- Rollback release `d4fd27d18355de03418e69cba19e2f903824bf3f34f7e2f3d0e13134f81c3239`. Root-owned operator and routing backup `/var/backups/webos-terminal-20261120-01`.
- All 20 previous Craft binary pins and the 71 existing app entries were verified. The static promotion retained 6,587 existing files by hardlink. The operator verified the backend and beta continuity checks.

## ACAD Modeler

Source owner `apps/acad`. The R730 build used legacy OCCT WASM `a2b2f7daf6a4eb98b975f8aec136f6cbaf2720295ea32e71edb13ff4c5ceaecb` produced from the recorded interpreter sources. The six prepared runtime artifacts and source archive were verified in place. The current preparer marks this source-built runtime local-only. Resolve recipient-accessible corresponding source and the separate wrapper modification terms for each shipped OCCT runtime. See the [source build record](../apps/acad/docs/WEBOS-REPRODUCIBLE-BUILD.md) and [wrapper notices](../apps/acad/docs/occt-source-rebuild-20261102/LICENSE-EVIDENCE.md).

The complete R730 build passed with the source-built legacy OCCT input and emitted **19 WASM files**. The hash inventory is in the private checkpoint. Polynomial, sketch history, and selection tests passed. The strict sketch fixture now verifies that the native decoder rejects arbitrary passive spline point IDs and preserves valid IDs through save and reload. The corrected test passed. ACAD test revision `855b61c9bf43b97e7bc1a23b002d2fc1b0ef6e63` changes only that test fixture.

ACAD `bd798c90a418a6c13c03e368660eabb8ac7c6fdb` and the Files launcher passed the private assembled browser workflow. A rectangle and extrusion were saved in a native archive and independently read from the account server. The Files Open operation reopened the archive in a fresh Chromium context, with identical model history and no dirty state, and a second open reused the existing window. Three association tests and eight Files browser regressions passed. The candidate uses the current site script policy. The hosted profile still excludes ACAD.

All 19 emitted WASM files matched their exact binary build inputs. That inventory includes modified interpreter variants. For example, the circular worker digest matches the native receipt for interpreter `7bf611ce`. It retains the Autodrop3d license, whose distribution conditions include upstream submission with a copyright assignment for modifications. Corresponding-source publication and the rights for these modified variants remain open. See the [exact upstream license](https://raw.githubusercontent.com/Autodrop3d/occt-interpreter/5efaf53accb45bac475155fc4d5552642c19e91e/LICENSE).

## Craft branch and release ledger

All 20 local tracking branches were advanced to the fetched public upstream main tips. The exact SHAs and preserved integration checkout IDs are in the private checkpoint. VectorCraft required a longer fetch for its upstream asset history.

| App | Previous local main | Refreshed main | Deployed source pin | Review |
|---|---|---|---|---|
| fieldcraft | `5db1a30ecb86` | `c1bec5b74f66` | `3bc9ca0565d6` | **Live and hosted-verified** |
| materialcraft | `b71c02cacd8d` | `4ff5af9af737` | `a0c356d2899c` | **Live and hosted-verified** |
| pcbcraft | `96f31b02442a` | `f839c74a5a20` | `00e78b1df0a7` | **Live and hosted-verified** |
| anicraft | `bcfea816478f` | `3ccb59e02b1a` | `04610927977e` | Pending |
| cadcraft | `2ccf5874b001` | `d3af2d5077e3` | `816d428e8a33` | Pending |
| deckcraft | `e4f86d11fe8a` | `6ebac8b9b3ad` | `5b065c4ef93c` | `eb26bc6945e3` Browser package built, account tests underway |
| designcraft | `c0721c08b4c4` | `4000591c6681` | `afca6f8d0f9a` | Pending |
| effectcraft | `b617ea08e544` | `c561e7352f60` | `78f11b7fc1ce` | Pending |
| figcraft | `559c952d107f` | `390e5f4e4b60` | `cf78eb22978c` | Pending |
| filmcraft | `9bac134d95b1` | `960a66100176` | `b7ba79c366e6` | Pending |
| gridcraft | `1476d4e7abef` | `c89d55036432` | `fd80ce897bce` | `321c7db9651b` Browser package verified, account tests underway |
| lightcraft | `c864637d44fb` | `c17badc68a96` | `ef00c97ec7f4` | Pending |
| pdfcraft | `271e479c5372` | `df18640982f6` | `a5b512846f59` | `4cbecb35cad2` Source review merged, build pending |
| photocraft | `d53b5edb600d` | `877d58844029` | `403994fc5f41` | Pending |
| sketchcraft | `561703d415af` | `86a742d6997f` | `89c6c11df97a` | **Live and hosted-verified** |
| solidcraft | `c22baab6e505` | `80e075ae6860` | `71a573e23441` | `aa69299267de` Upstream merge reviewed, reconcile current integration before testing |
| soundcraft | `5976545fe1dd` | `85623f28f99a` | `e196254ee15f` | Pending |
| texturecraft | `2951f3c3885a` | `2bbd2625bfb7` | `3ada1e30108a` | Pending |
| vectorcraft | `7452b6f383e3` | `063f55080244` | `09ee69a08736` | Pending |
| wordcraft | `6ef13b2cc8a6` | `fea7a9182e43` | `edeb4a090cd3` | Pending |

The owner-only checkpoint pointer is `~/Projects/.webos-migration/terminal-acad-craft-current.txt`. It identifies the exact release and browser evidence, Terminal builder reuse and R730 ACAD build inputs. The adjacent previous checkpoint includes the full 20-app audit with unabridged SHAs.

### Qualification details

- FieldCraft's first R730 run passed 494, failed four and ignored 18. The original no-home runner conflicted with three upstream home-redaction fixtures and a fourth crash-directory test. The two test files match upstream. With a private temporary home and crash directory, the focused rerun passed all seven tests, including the four original failures. The full rerun passed 498 with 18 ignored.
- MaterialCraft's dependency check now passes with the locked, offline cache inside the matching isolated runner. The integration retained a bitmap fixture that used the removed `materialcraft_image` crate. Its import now uses upstream's `craft_texture`, and the resource, engine and egui suites passed with the same assertions.
- PCBCraft's native app suite passed 1,143, failed 61 and ignored 10 in the no-network runner. The failures originate in tests that start the desktop loopback endpoint. The runner rejects socket calls, and subsequent UI assertions in those tests depend on successful endpoint setup. That native endpoint is outside the WebOS editor path. Five browser scenarios passed, including schematic and board editing, Undo, Save and Save As, existing-document activation, refresh recovery and fresh account reopen from Files.
- SketchCraft's review preserves the account viewport observer and the upstream Layout viewport pause. The upstream batch lifetime and drawing date use the existing browser-compatible Rust clock. The packaged-WASM check reproduced a crash in `sheet_ir`, which started native threads when drawing a viewport. The fixed engine renders sequentially in WASM and retains native parallel drawing. The browser regression passed initial drawing, cache invalidation after a geometry edit and redrawing with the unchanged application UI.
- DeckCraft's review preserves correlated document identity and adds upstream import warnings. GridCraft's review preserves WebOS's confirmed account save and the upstream save transport for ordinary embedded hosts. Each still needs a browser save and recovery pass.
- PdfCraft's review keeps confirmed-write receipts and applies the upstream object-identity invalidation when an acknowledged PDF rewrite renumbers objects. It retains the fork's existing trademark exclusions and regenerates the affected attribution table from its asset manifest.
- SolidCraft upstream includes the merged cornered-radius fillet PR `2d196b1c9e7e`. The review adopts the upstream fillet implementation and retains the downstream taper and through-hole regressions. The current local rebased integration has four corresponding patches. Its overlapping save, toolbar, browser and test-ledger changes still need reconciliation before running the native geometry suite.

### PCBCraft upgrade on ksu.codes

Release `2ad815cb2ff8094f35d9b6825d8150586a1329b83fc09f3ab5fe665236b140e6` runs PCBCraft `00e78b1df0a7a6b5cd516ec615c188cc27a166ca` from parent pin `1a9521a87f34b9e844c205a6547dc3d793d6d829`. The scoped overlay verified all 6,614 prior files and kept 6,574 by hardlink. A hosted Chromium session matched WASM digest `cd528cea24e8ad74f876b459a11d33f8ece696ad11efc01b23ec49693a28e7ab`, confirmed its MIME type and started the editor under the current policy. The operator verified backend and beta continuity.

Rollback is Terminal release `9866ceba34bcbaebd863de4fc8289fe4df28e293732c8064c0f3f358d0537654`. The root-owned plan is at `/var/backups/webos-pcbcraft-upstream-00e78b1df0a7/plan.json`.

### FieldCraft upgrade on ksu.codes

Release `808111f18406f1e5dd204fed2237ba93b935f286eb77f69cccbbbb21e0c86ba9` runs FieldCraft `3bc9ca0565d65a61a4e65db3eaedf09de720d238` from parent pin `caeb4187e3b6b72aa61880ce4baf11c00c7aa1f4`. All five account browser scenarios passed. The saved cantilever reopened in a fresh Chromium context and reproduced a displacement of 0.24456187149695957 mm with its original loads and constraints. The scoped overlay verified all 6,614 prior files, preserved 6,598 by hardlink and yielded hosted WASM digest `40b1767650a135bf69aa80bf6f9ed94c52cf6f6a14316f7d85a2841521f50ccb`. Chromium started the hosted editor and the operator verified backend and beta continuity.

Rollback is PCBCraft release `2ad815cb2ff8094f35d9b6825d8150586a1329b83fc09f3ab5fe665236b140e6`. The root-owned plan is at `/var/backups/webos-fieldcraft-upstream-3bc9ca0565d6/plan.json`.

### MaterialCraft upgrade on ksu.codes

Release `a72fa917ad29f76e877d2cd7856e63b36f67eab2ee0050f86b2c79a325898fef` runs MaterialCraft `a0c356d2899c84279816cc23fc76bc0d8199b1bc` from parent pin `6f2d6787f29010127636734c312735308e71c405`. All four account browser scenarios passed. Save and Save As preserved the embedded bitmap. Refresh recovered unsaved graph edits and the bitmap. A fresh account browser reopened and evaluated the saved graph, then confirmed a later server revision. The build includes the 14 tracked SBS resource files and the OFL Liberation Mono fallback from craft-fonts `9ffb3a717e08`. The native resource suite passed with that font.

The scoped overlay verified 6,614 prior files and preserved 6,603 by hardlink. Hosted Chromium matched WASM digest `b6bc8b615a987182a857b197dd4caec89bb646978d185a92817aceb5679337ad` and started the editor. The operator verified backend and beta continuity. Rollback is FieldCraft release `808111f18406f1e5dd204fed2237ba93b935f286eb77f69cccbbbb21e0c86ba9`. The root-owned plan is at `/var/backups/webos-materialcraft-upstream-a0c356d2899c/plan.json`.

### SketchCraft upgrade on ksu.codes

Release `4b44b40ba621f11231d0a72b61c44dab33ddf20e0e4ca23ce9f03564b2f77d80` runs SketchCraft `89c6c11df97a94709cbe804f75ed51ee47809253`, pinned by parent `aa58b4e03226c10f25a7d7316986b55864e4083e`. The runtime was built from `216d4ec7106e`. The later commit changes only the browser test fixture, so the runtime source is identical. TypeScript, 282 UI tests, 10 native drafting-cache tests and 37 engine and browser-model tests passed. All four WebOS account scenarios passed, including pointer-driven extrusion, Save As, refresh recovery and fresh Files reopen.

The overlay verified 6,629 prior files and preserved 6,568 by hardlink. Hosted Chromium matched WASM digest `54739c2507277f70a7f398b9e20035e5e7df68a7f341ca02c31f4602bd6ca89f` and started the editor. The operator verified backend and beta continuity. Rollback is MaterialCraft release `a72fa917ad29f76e877d2cd7856e63b36f67eab2ee0050f86b2c79a325898fef`. The root-owned plan is at `/var/backups/webos-sketchcraft-upstream-89c6c11df97a/plan.json`.

The four verified upgrades reclaimed their duplicate transfer archives after hosted verification. Immutable release files and rollback records are retained.
