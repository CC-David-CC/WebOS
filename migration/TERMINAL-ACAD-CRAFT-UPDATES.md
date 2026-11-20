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
| fieldcraft | `5db1a30ecb86` | `c1bec5b74f66` | `8f14daaa674c` | `3bc9ca0565d6` Native suite passed, browser build underway |
| materialcraft | `b71c02cacd8d` | `4ff5af9af737` | `b41e57dc787b` | `a0c356d2899c` Fixed stale test import, native qualification restarted |
| pcbcraft | `96f31b02442a` | `f839c74a5a20` | `2348195417bf` | `00e78b1df0a7` Browser package verified, account tests underway, native endpoint tests require loopback |
| anicraft | `bcfea816478f` | `3ccb59e02b1a` | `04610927977e` | Pending |
| cadcraft | `2ccf5874b001` | `d3af2d5077e3` | `816d428e8a33` | Pending |
| deckcraft | `e4f86d11fe8a` | `6ebac8b9b3ad` | `5b065c4ef93c` | Pending |
| designcraft | `c0721c08b4c4` | `4000591c6681` | `afca6f8d0f9a` | Pending |
| effectcraft | `b617ea08e544` | `c561e7352f60` | `78f11b7fc1ce` | Pending |
| figcraft | `559c952d107f` | `390e5f4e4b60` | `cf78eb22978c` | Pending |
| filmcraft | `9bac134d95b1` | `960a66100176` | `b7ba79c366e6` | Pending |
| gridcraft | `1476d4e7abef` | `c89d55036432` | `fd80ce897bce` | Pending |
| lightcraft | `c864637d44fb` | `c17badc68a96` | `ef00c97ec7f4` | Pending |
| pdfcraft | `271e479c5372` | `df18640982f6` | `a5b512846f59` | Pending |
| photocraft | `d53b5edb600d` | `877d58844029` | `403994fc5f41` | Pending |
| sketchcraft | `561703d415af` | `86a742d6997f` | `f40e10b06079` | `eee4eb767c27` Engine and UI merge reviewed, compile and browser tests pending |
| solidcraft | `c22baab6e505` | `80e075ae6860` | `71a573e23441` | Pending |
| soundcraft | `5976545fe1dd` | `85623f28f99a` | `e196254ee15f` | Pending |
| texturecraft | `2951f3c3885a` | `2bbd2625bfb7` | `3ada1e30108a` | Pending |
| vectorcraft | `7452b6f383e3` | `063f55080244` | `09ee69a08736` | Pending |
| wordcraft | `6ef13b2cc8a6` | `fea7a9182e43` | `edeb4a090cd3` | Pending |

The owner-only checkpoint pointer is `~/Projects/.webos-migration/terminal-acad-craft-current.txt`. It identifies the exact release and browser evidence, Terminal builder reuse and R730 ACAD build inputs. The adjacent previous checkpoint includes the full 20-app audit with unabridged SHAs.

### Qualification details

- FieldCraft's first R730 run passed 494, failed four and ignored 18. The original no-home runner conflicted with three upstream home-redaction fixtures and a fourth crash-directory test. The two test files match upstream. With a private temporary home and crash directory, the focused rerun passed all seven tests, including the four original failures. The full rerun passed 498 with 18 ignored.
- MaterialCraft's dependency check now passes with the locked, offline cache inside the matching isolated runner. The integration retained a bitmap fixture that used the removed `materialcraft_image` crate. Its import now uses upstream's `craft_texture`, and qualification restarted with the same assertions.
- PCBCraft's native app suite passed 1,143, failed 61 and ignored 10 in the no-network runner. The failures originate in tests that start the desktop loopback endpoint. The runner rejects socket calls, and subsequent UI assertions in those tests depend on successful endpoint setup. Full native endpoint qualification remains outstanding. Browser WASM digest `cd528cea24e8ad74f876b459a11d33f8ece696ad11efc01b23ec49693a28e7ab` matched the build receipt and passed initial schematic, board and Undo checks in the private preview.
- SketchCraft's review preserves the account viewport observer and the upstream Layout viewport pause. The upstream batch lifetime and drawing date use the existing browser-compatible Rust clock. Model edits invalidate kept drawings and the browser redraws on demand. The new browser regression checks that sequence against the packaged WASM. Browser and native qualification are still required for the drawing workspace and account saves.
