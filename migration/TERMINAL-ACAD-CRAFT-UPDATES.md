# Terminal, ACAD and Craft updates

The approved goal covers the existing ksu.codes viewer and the 20 currently registered Craft editors. The legacy JSketcher fork and the optional PCBCraft packager have separate source owners.

## Terminal

Live release `9866ceba34bcbaebd863de4fc8289fe4df28e293732c8064c0f3f358d0537654`, verified in Chromium with an isolated test account. Local source-built assembly and hosted browser checks passed. Sign-in and Files issue zero guest asset requests. Two concurrently open windows get independent PTYs on one v86 Worker. Closing shells removes their sessions, reopening retains temporary guest home, and stopping the guest terminates its Worker and clears the filesystem handle. An account upload retains exact bytes on the server and stays separate from guest files.

- Terminal `a6bae78831c5f9218147c0253d295fa4981a4879`, Desktop `22c1b12bd6a972208a818657970f9efc6d857ecf`, Linux `584bbeaee1e15f36b603ed20bcb2cc6dd58b38dd`, v86 `c2c6a3296c631746fbc2f55c6c34bb5739c36784`.
- Parent source commit `f9fda5ea59734c1dfe97eebdfaf443d56833f93c`. App bundle `991370da47e178b8dcff2ed3feb2aa807ab4206a2e063184a1f0a1612f592c28`.
- Rollback release `d4fd27d18355de03418e69cba19e2f903824bf3f34f7e2f3d0e13134f81c3239`. Root-owned operator and routing backup `/var/backups/webos-terminal-20261120-01`.
- All 20 previous Craft binary pins and the 71 existing app entries were verified. The static promotion retained 6,587 existing files by hardlink. The operator verified the backend and beta continuity checks.

### Offline Linux guest verification

The hosted image manifest and the local 31,033,507-byte initramfs matched SHA-256 `e571ca17c12f1b392851b1cc1144aa14abc185c3bac7380d7c24821073e6e389`. The hosted config advertised no `guestNetwork`. The owner-only checkpoint contains `linux-offline-smoke.cjs` and its exit-zero `linux-offline-smoke.log`. Headless Chromium booted the pinned guest on a loopback-only fixture using the real guest Worker and PTY. UID 1000 ran CPython, queried SQLite, spawned a Linux child process, and wrote a guest file that the Worker read back. The harness recorded no guest default route, external requests, or WebSockets and closed the Worker. This check required no hosted configuration changes.

The pinned guest has no `xclock`, `Xorg`, or `Xvfb` on its executable path. Terminal remains the serial-console application in `apps/terminal`. A future X11 application gets its own Git repository, image, build outputs and runtime disk storage. It can reuse the engine in `engines/v86`. Its first graphics smoke test would use a compatible image with an X server and `xclock`, plus a v86 VGA view for visible output and input. Local ISO boot and persistent VM storage are future options.

The separate X11 package preflight downloaded 102 MB of Debian Bookworm i386 packages, including Xorg, VESA and evdev drivers, and xterm. The owner-only `linux-x11-current.txt` pointer locates the package selection and download logs. The X11 repository, guest image, and Desktop entry are pending. First verify a prepackaged guest under the existing network policy, with visible xclock and a usable xterm, keyboard and mouse focus, close/reopen, and Worker cleanup. Then try Chromium in that guest as a separate experiment. Confirm package and guest compatibility, boot and application memory use, and launch performance before considering it for the default X11 image.

Guest Chromium serves local files for both Anon and signed-in users. The owner wants `dflanag3` to be able to browse externally from guest Chromium through the configured `.33` route. Bind that capability to the verified owner account at the server. Verify real guest Chromium access for the owner and local-file access with external guest networking denied for a separate signed-in account and Anon. Keep the exact route and runtime settings in the private checkpoint.

The CLI and X11 apps form the foundation for a development and gaming environment. Record the supported languages, file types, and applications as they pass. Qualify a representative edit, run, and reopen workflow for each supported development runtime, plus offline game launch, input, and cleanup. Keep those checks distinct from the network entitlement tests.

### Account-backed Terminal development

Use `--terminal account-home` for the local viewer candidate. A registered user's `/home/guest` is My files over VirtIO 9P. The browser uses the existing signed Storage client and exact prior revisions for commits. Credentials stay in the browser. The guest retains its temporary root and `/tmp`. The login page also offers an ephemeral **Anon** session with no private file authority. The local release derives the localhost mapping from the pinned initramfs with a reproducible build-time overlay.

The owner-only checkpoint's `account-home-preview-current.txt` locates the isolated assembled preview and `browser-v3.log`. Actual Chromium and the signed local Gateway passed Files upload → shell read, shell write → Files Refresh, fresh browser read, stale guest `fsync` refusal, hostname loopback and ordinary-account egress denial. Anon booted a separate guest and could not access the signed-in user's files or server authority. The standalone guest test also passed mkdir, file rename and removal. Folder rename and full POSIX metadata remain outside the current Storage mount capabilities. The hosted viewer has not been promoted to this build.

The requested existing-folder migration on the `ksu.codes` development account store moved both starter folders in 101 homes. Storage verified each recursive manifest after its no-overwrite move. The owner-only checkpoint records the operation journal location. Local Storage source seeds `3D-Objects` and `Digital-Projects` on new accounts. The live backend still needs that source update for accounts created after the migration.

Upcoming work is an owner-only network entitlement, then a separate packaged X11 app. No shared guest relay should be enabled for Anon or ordinary signed-in users. Server authorization must pin the verified owner subject and separately restrict any LAN destination by service and port. Use R730 SSH for the first LAN test. Host and service details belong in the private checkpoint. Terminal's core tools are the shell, nano, Python, SQLite and the bundled archive and text utilities. X11 starts with a window manager, `xclock`, and then `xterm` for keyboard, pointer, focus and disposal checks.

## ACAD Modeler

Source owner `apps/acad`. The R730 build used legacy OCCT WASM `a2b2f7daf6a4eb98b975f8aec136f6cbaf2720295ea32e71edb13ff4c5ceaecb` produced from the recorded interpreter sources. The six prepared runtime artifacts and source archive were verified in place. The current preparer marks this source-built runtime local-only. Resolve recipient-accessible corresponding source and the separate wrapper modification terms for each shipped OCCT runtime. See the [source build record](../apps/acad/docs/WEBOS-REPRODUCIBLE-BUILD.md) and [wrapper notices](../apps/acad/docs/occt-source-rebuild-20261102/LICENSE-EVIDENCE.md).

The complete R730 build passed with the source-built legacy OCCT input and emitted **19 WASM files**. The hash inventory is in the private checkpoint. Polynomial, sketch history, and selection tests passed. The strict sketch fixture now verifies that the native decoder rejects arbitrary passive spline point IDs and preserves valid IDs through save and reload. The corrected test passed. ACAD test revision `855b61c9bf43b97e7bc1a23b002d2fc1b0ef6e63` changes only that test fixture.

ACAD `bd798c90a418a6c13c03e368660eabb8ac7c6fdb` and the Files launcher passed the private assembled browser workflow. A rectangle and extrusion were saved in a native archive and independently read from the account server. The Files Open operation reopened the archive in a fresh Chromium context, with identical model history and no dirty state, and a second open reused the existing window. Three association tests and eight Files browser regressions passed. The candidate uses the current site script policy. The hosted profile still excludes ACAD.

All 19 emitted WASM files matched their exact binary build inputs. That inventory includes modified interpreter variants. For example, the circular worker digest matches the native receipt for interpreter `7bf611ce`. It retains the Autodrop3d license, whose distribution conditions include upstream submission with a copyright assignment for modifications. Corresponding-source publication and the rights for these modified variants remain open. See the [exact upstream license](https://raw.githubusercontent.com/Autodrop3d/occt-interpreter/5efaf53accb45bac475155fc4d5552642c19e91e/LICENSE).

The follow-up on R730 rehashed all 19 retained inputs without copying them. It found 16 hash-bound build records and 6 outputs with source revisions in those matching records. The remaining records need further source mapping. The owner-only checkpoint holds the per-artifact inventory. Both corresponding-source availability and wrapper terms still need resolution before deployment.

## Craft branch and release ledger

All 20 local tracking branches were advanced to the fetched public upstream main tips. The exact SHAs and preserved integration checkout IDs are in the private checkpoint. VectorCraft required a longer fetch for its upstream asset history.

| App | Previous local main | Refreshed main | Deployed source pin | Review |
|---|---|---|---|---|
| fieldcraft | `5db1a30ecb86` | `c1bec5b74f66` | `3bc9ca0565d6` | **Live and hosted-verified** |
| materialcraft | `b71c02cacd8d` | `4ff5af9af737` | `a0c356d2899c` | **Live and hosted-verified** |
| pcbcraft | `96f31b02442a` | `f839c74a5a20` | `00e78b1df0a7` | **Live and hosted-verified** |
| anicraft | `bcfea816478f` | `3ccb59e02b1a` | `a803cd86cb01` | **Live and hosted-verified** |
| cadcraft | `2ccf5874b001` | `d3af2d5077e3` | `dc4ffcdf8211` | **Live and hosted-verified** |
| deckcraft | `e4f86d11fe8a` | `6ebac8b9b3ad` | `eb26bc6945e3` | **Live and hosted-verified** |
| designcraft | `c0721c08b4c4` | `4000591c6681` | `8e5f309bed61` | **Live and hosted-verified** |
| effectcraft | `b617ea08e544` | `c561e7352f60` | `cf2336ddfc00` | **Live and hosted-verified** |
| figcraft | `559c952d107f` | `390e5f4e4b60` | `2837cfdc32e3` | **Live and hosted-verified** |
| filmcraft | `9bac134d95b1` | `960a66100176` | `3d2796e01bdd` | **Live and hosted-verified** |
| gridcraft | `1476d4e7abef` | `c89d55036432` | `321c7db9651b` | **Live and hosted-verified** |
| lightcraft | `c864637d44fb` | `c17badc68a96` | `b1988c539ee9` | **Live and hosted-verified** |
| pdfcraft | `271e479c5372` | `df18640982f6` | `4cbecb35cad2` | **Live and hosted-verified** |
| photocraft | `d53b5edb600d` | `877d58844029` | `403994fc5f41` | Nine browser account scenarios passed. A close request was refused immediately before the finished edit released focus. Review `826ed8f590df` processes editor input before starting close and retains the hosted keyboard choices. Its WASM check passed. Packaging and the browser rerun are pending. |
| sketchcraft | `561703d415af` | `86a742d6997f` | `89c6c11df97a` | **Live and hosted-verified** |
| solidcraft | `c22baab6e505` | `82f65a2158b1` | `71a573e23441` | Review `19f0ed46af99` merges the next upstream fixes, including two fillet updates. R730 verified 17,298 tracked inputs and built the native CLI and test driver. The fillet suite is running. The prior review passed 10 browser checks and timed out in native geometry. |
| soundcraft | `5976545fe1dd` | `85623f28f99a` | `e738caf3c9aa` | **Live and hosted-verified** |
| texturecraft | `2951f3c3885a` | `2bbd2625bfb7` | `cd2c82345a8b` | **Live and hosted-verified** |
| vectorcraft | `7452b6f383e3` | `063f55080244` | `c54691a43f7a` | **Live and hosted-verified** |
| wordcraft | `6ef13b2cc8a6` | `fea7a9182e43` | `edeb4a090cd3` | 23 of 31 conflict files reconciled. The upstream file service now carries WebOS save identity and acknowledgement handling, scoped preferences and the one-window-per-document rule. Eight conflict files remain across the File menu, printing and tests. The merge still requires compilation and browser qualification. |

The owner-only checkpoint pointer is `~/Projects/.webos-migration/terminal-acad-craft-current.txt`. It identifies the exact release and browser evidence, Terminal builder reuse and R730 ACAD build inputs. The adjacent previous checkpoint includes the full 20-app audit with unabridged SHAs.

### Qualification details

- PdfCraft `4cbecb35cad291af0d580b51c3dc77beaef20a11` at source tree `45199ac6ab40b0d50a98e295d9228dbf9e0c3f29` is pinned by parent `e83a605ee7d0d145c694a3aebd4a6744b29bb349`. Five focused native save tests passed. All 17 signed-account browser checks passed both on the assembled private viewer and on `ksu.codes`. Independent PDF extraction verified authored, recovered and uncertain-save bytes as well as the saved 180-degree rotation. The hosted main and OCR WASM payloads matched the 66-file build inventory. Active release `6b20cb508528fe59181c812334f358b4f7576a2a6630e1bc19adfd115b5ac455` retained 6,705 prior files by hardlink, all 72 app entries, and the same backend instance and issuer. Rollback is `e91b4ff1697a6d98ef12b2b05f279f5468d6febf339a112eee688077eee048d5` with routing backup `/var/backups/webos-pdfcraft-upstream-4cbecb35cad2`. The two transfer copies were removed after the hosted checks. The checkpoint retains the full build, qualification and cleanup receipts.

- FieldCraft's first R730 run passed 494, failed four and ignored 18. The original no-home runner conflicted with three upstream home-redaction fixtures and a fourth crash-directory test. The two test files match upstream. With a private temporary home and crash directory, the focused rerun passed all seven tests, including the four original failures. The full rerun passed 498 with 18 ignored.
- MaterialCraft's dependency check now passes with the locked, offline cache inside the matching isolated runner. The integration retained a bitmap fixture that used the removed `materialcraft_image` crate. Its import now uses upstream's `craft_texture`, and the resource, engine and egui suites passed with the same assertions.
- PCBCraft's native app suite passed 1,143, failed 61 and ignored 10 in the no-network runner. The failures originate in tests that start the desktop loopback endpoint. The runner rejects socket calls, and subsequent UI assertions in those tests depend on successful endpoint setup. That native endpoint is outside the WebOS editor path. Five browser scenarios passed, including schematic and board editing, Undo, Save and Save As, existing-document activation, refresh recovery and fresh account reopen from Files.
- SketchCraft's review preserves the account viewport observer and the upstream Layout viewport pause. The upstream batch lifetime and drawing date use the existing browser-compatible Rust clock. The packaged-WASM check reproduced a crash in `sheet_ir`, which started native threads when drawing a viewport. The fixed engine renders sequentially in WASM and retains native parallel drawing. The browser regression passed initial drawing, cache invalidation after a geometry edit and redrawing with the unchanged application UI.
- DeckCraft's review preserves correlated document identity and adds upstream import warnings. GridCraft's review preserves WebOS's confirmed account save and the upstream save transport for ordinary embedded hosts. Both passed their exact account browser suites.
- PdfCraft's review keeps confirmed-write receipts and applies the upstream object-identity invalidation when an acknowledged PDF rewrite renumbers objects. It retains the fork's existing trademark exclusions and regenerates the affected attribution table from its asset manifest.
- SolidCraft upstream includes the merged cornered-radius fillet PR `2d196b1c9e7e`. The review adopts that implementation and retains the downstream taper and through-hole regressions. The prior local rebase's four patches were compared with the review. The new commit retains its unsigned account serialization and canonical file-command checks. R730 verified all 17,282 tracked inputs. Native SMLib passed 407 tests. Three full fillet runs timed out on `every-block-cylinder-crease-block-top-edge-r2-curvature`. The optimized WASM candidate passed all 10 local browser checks, including four fillet fixtures, and remains staged locally pending the native suite.

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

### GridCraft and DeckCraft upgrades on ksu.codes

GridCraft `321c7db9651b0b3762d7e336e224a86e3f43609b` is live from parent `1f4404fa41beeabd84260e60026d562587827348`. Release `1182bb8526339a8febc43cf09d806d0847176e821a08136e6a49c0259519c078` passed 13 exact browser checks. The overlay verified 6,633 prior files and preserved 6,606 by hardlink. Hosted Chromium started WASM `dea668479eb70767f66f46960dac43ee57fcd9af185b8fea6941c0ba459dd992`. Rollback is SketchCraft release `4b44b40ba621f11231d0a72b61c44dab33ddf20e0e4ca23ce9f03564b2f77d80`. The operator plan is at `/var/backups/webos-gridcraft-upstream-321c7db9651b/plan.json`.

DeckCraft `eb26bc6945e3a8469d11f817175eab3b1ebc768d` is live from parent `05a6d5fe50298eea0f8dc9ee0c3634fcc6480c06`. Release `e91b4ff1697a6d98ef12b2b05f279f5468d6febf339a112eee688077eee048d5` passed 14 exact browser checks, including paired presenter and audience window lifecycle. The overlay verified 6,633 prior files and preserved 6,525 by hardlink. Hosted Chromium started WASM `30c8836e162928ce5ca22641930c58a24b051baa6996e5b5dec6089a76210d2b`. Rollback is the GridCraft upgrade. The operator plan is at `/var/backups/webos-deckcraft-upstream-eb26bc6945e3/plan.json`.

Both account suites covered Save As, server acknowledgement, write spacing and Retry-After, stale and uncertain writes, draft recovery, and reopen in a fresh browser signed into the same account. The operator verified account service and beta continuity. All six upgrades reclaimed their duplicate transfer archives after hosted verification. Immutable release files and rollback records are retained.

### LightCraft upgrade on ksu.codes

Release `08afbdbac4f6fc502ce2567b59b3954fb905ad391f4bdc8c3261d8c0da2e53a6` runs LightCraft `b1988c539ee98c22cd392977ed6cc87bc101fad4` from parent pin `5702369b4815503eaaa23bc605d92b2c171e2cb6`. All seven local Chromium checks passed. They verified native PNG import and rating, Save and Save As, draft recovery, and a fresh browser opening the saved account catalog through Files with the detached original rendered. The signed account tests verified digest deduplication and cross-account denial.

The scoped overlay verified 6,773 prior files and preserved 6,760 by hardlink. Hosted Chromium verified WASM digest `ffad4af154823195db8e7fa7a28f54e7711db74be734f04552e5af45ba7af8d6` and started the editor under the site script policy. The operator verified account service and beta continuity. Rollback is the PdfCraft release `6b20cb508528fe59181c812334f358b4f7576a2a6630e1bc19adfd115b5ac455`. The operator plan is at `/var/backups/webos-lightcraft-upstream-b1988c539ee9/plan.json`.

### FilmCraft upgrade on ksu.codes

Release `4f81f0241862b7460ad02e5b741956af5c7d4907869c4992769633f16ce8a54a` runs FilmCraft `3d2796e01bdd30824b33478717bb3e54439b936a` from parent pin `06ff8241f5f4d1a6404efd128821521dd707a45b`. All seven local Chromium checks passed. They covered native editing and Undo, confirmed Save and Save As, activating an existing window for the same project, recovery of project and linked media, and a fresh browser decoding the video from account storage. A full-resolution frame exported from the reopened video matched the expected test pixels.

The scoped overlay verified 6,773 prior files and preserved 6,759 by hardlink. Hosted Chromium verified WASM digest `cfb4eed1c59e3e6a70abe64f9b61a56fbd5b937a7d29682961d3edaac06965b2` and started the editor. The operator verified account service and beta continuity. Rollback is the LightCraft release `08afbdbac4f6fc502ce2567b59b3954fb905ad391f4bdc8c3261d8c0da2e53a6`. The operator plan is at `/var/backups/webos-filmcraft-upstream-3d2796e01bdd/plan.json`. Both upgrades reclaimed their duplicate transfer archives after verification.

### SoundCraft upgrade on ksu.codes

Release `81bf3fbd8c41a311688b697cdda742ef18848036c43b40b06006944aef5b44b4` runs SoundCraft `e738caf3c9aa41faf7d9554e8ec708071071554e` from parent pin `5adce9158c57c3c0947c070b600fb6ee3ebb2b31`. Seven local Chromium checks covered native track editing and Undo, account Save and Save As, reuse of an open account project, revision advancement, and local draft recovery. A new browser opened the project from Files, played its expected signal through Chromium WebAudio, and saved all 4,800 original WAV samples.

The scoped overlay verified 6,773 prior files and preserved 6,761 by hardlink. Hosted Chromium verified WASM digest `1359c59ee3485f1fa3992097b32ffe4a045e1008d593d05c1d084e0964ae4af3` and started the editor. The operator verified account service and beta continuity. Rollback is release `4f81f0241862b7460ad02e5b741956af5c7d4907869c4992769633f16ce8a54a`. The operator plan is at `/var/backups/webos-soundcraft-upstream-e738caf3c9aa/plan.json`. Duplicate transfer archives were reclaimed.

### EffectCraft upgrade on ksu.codes

Release `06fe3593fd3c19b7d99eae124c98d20b33775d3206badf5577c8047442376aaa` runs EffectCraft `cf2336ddfc00c5490850a9e9913d4dde17f2e15a` from parent pin `2114cd888b34abebc8703298b66b7abdb21b7b7d`. Eight local Chromium checks covered native composition editing and Undo, linked-media import, confirmed Save and Save As, existing-window activation, and local draft recovery. A fresh browser reopened the composition through Files, retrieved the correct original and rendered its expected pixels. Closing the editor retired its browser frame workers.

The scoped overlay verified 6,773 prior files and preserved 6,757 by hardlink. Hosted Chromium verified WASM digest `97e9c067ae81344cf460b7434ef67bd658162af4a02f20df853250ea04ededf5` and started the editor. The operator verified account service and beta continuity. Rollback is release `81bf3fbd8c41a311688b697cdda742ef18848036c43b40b06006944aef5b44b4`. The operator plan is at `/var/backups/webos-effectcraft-upstream-cf2336ddfc00/plan.json`. Duplicate transfer archives were reclaimed.

### DesignCraft upgrade on ksu.codes

Release `89fdbeba9f370cedd83c639d15b618ac71cf4d1680e30c95e1bd945ad7bc5dfd` runs DesignCraft `8e5f309bed615d0d9203ff42225a830ba437869b` from parent pin `95d0c132c2577702a09cc540ee28e1dd038709e9`. All six local Chromium checks passed. They covered confirmed account Save and Save As, draft recovery, and reopening the publication from Files. A missing linked image was located through the account picker, embedded, and recovered in a full-resolution PDF export from a fresh browser.

The overlay verified 6,773 prior files and preserved 6,763 by hardlink. Hosted Chromium verified WASM digest `51490ad3b4c393909b240ed4ae7700f8de235ec0dd690802187f9180e4cc466d` and started the editor. The operator verified account service and beta continuity. Rollback is the EffectCraft release `06fe3593fd3c19b7d99eae124c98d20b33775d3206badf5577c8047442376aaa`. The operator plan is at `/var/backups/webos-designcraft-upstream-8e5f309bed61/plan.json`. Duplicate transfer archives were reclaimed.

### VectorCraft upgrade on ksu.codes

Release `709ad552e74fedec3be12f408d9cea9578bb39990e688e96f04d40a6cff36ee5` runs VectorCraft `c54691a43f7ab304f083121064bcbab8b7b33a7b` from parent pin `676c1fc204bee8afc617608425b2aee860ac2536`. All 12 local Chromium checks passed, including account Save and Save As, draft recovery, and reopening the saved project from Files in a fresh account session. Hosted Chromium verified WASM digest `2dcd6d90851bec7188e12ac2de6a18c426157be5eb4385c4add8f0503b028364` and started the editor under the site script policy.

The overlay verified 6,773 prior files and preserved 6,735 by hardlink. Rollback is release `89fdbeba9f370cedd83c639d15b618ac71cf4d1680e30c95e1bd945ad7bc5dfd`. The operator plan is at `/var/backups/webos-vectorcraft-upstream-c54691a43f7a/plan.json`. Both duplicate transfer archives were removed.

### FigCraft upgrade on ksu.codes

Release `488279e189f278086b32e630815b07cdfe1888bbb8bbd73d09851d822115f527` runs FigCraft `2837cfdc32e3f2ec9746e7c047189c7f09f540f6` from parent pin `989adb0b4a1f91e13898ea4b8413cfc3a2fe635f`. All 12 local Chromium checks passed, including account Save and Save As, draft recovery, and reopening the saved project from Files in a fresh account session. Hosted Chromium verified WASM digest `5b5a325c1ef37760ce4c82cf7702b9b604b79bdd38a83ac2c70db1779050189b` and started the editor under the site script policy.

The overlay verified 6,784 prior files and preserved 6,742 by hardlink. Rollback is release `709ad552e74fedec3be12f408d9cea9578bb39990e688e96f04d40a6cff36ee5`. The operator plan is at `/var/backups/webos-figcraft-upstream-2837cfdc32e3/plan.json`. Both duplicate transfer archives were removed.

VectorCraft used its pinned font catalog and verified all packaged fonts. FigCraft exceeded upstream’s 25 MiB portable hosting limit. Its exact 28,205,332-byte WebOS component fits the existing 64 MiB assembly limit and includes the original bundled font notices.

### TextureCraft upgrade on ksu.codes

Release `d01f19ac2e827c623e4758ec8605cc930a662b0f7508e34b70d31106c48e78a0` runs TextureCraft `cd2c82345a8b0f1a0d4b8795b8e4bf7a08b8e479` from parent pin `e7a9603842e99d992962d8d41a3be59a93f41e88`. Mesh import and UV paint, embedded asset Save and Save As, draft recovery and fresh account reopen passed in 5 Chromium checks. Hosted Chromium started the editor under the site script policy and verified WASM digest `abe5197995513529ba4d1be42a076621b9676d48e3cde3ea731f52aa5a47ac32`.

The overlay verified 6,784 prior files and retained 6,773 by hardlink. Rollback is release `488279e189f278086b32e630815b07cdfe1888bbb8bbd73d09851d822115f527`. The operator plan is at `/var/backups/webos-texturecraft-upstream-cd2c82345a8b/plan.json`. Both duplicate transfer archives were removed.

### CADCraft upgrade on ksu.codes

Release `dfc7d666c4d5665e0f6a0f65440f8bb8fb33b824352aa412111976a889376b73` runs CADCraft `dc4ffcdf8211357fdf60b4aaf2eece5c1f413aed` from parent pin `0339e7b5255814cd183d0ee8926e3a342aba18cb`. Native line, circle and dimension editing, editable DXF Save and Save As, draft recovery and fresh account reopen passed in 5 Chromium checks. Hosted Chromium started the editor under the site script policy and verified WASM digest `fd673912297974d3a99704ce6c6b27745bda9480cd4392dde049413b9d0ff186`.

The overlay verified 6,790 prior files and retained 6,779 by hardlink. Rollback is release `d01f19ac2e827c623e4758ec8605cc930a662b0f7508e34b70d31106c48e78a0`. The operator plan is at `/var/backups/webos-cadcraft-upstream-dc4ffcdf8211/plan.json`. Both duplicate transfer archives were removed.

### AniCraft upgrade on ksu.codes

Release `426b10a481616642d6e1afb94f5bfae3bc406464d2e005e9b2167fdf4d89b1f9` runs AniCraft `a803cd86cb0197161e141e0a23804f730c085e7d` from parent pin `4a6618dda1173c264a7410045a977e5fa5e30991`. Timeline editing, linked media, account Save and Save As, draft recovery and fresh account reopen passed in 14 Chromium checks. Hosted Chromium started the editor under the site script policy and verified WASM digest `91abbde5c765271fd09b8283cec735c09139c435eecf0948163f5cff944f8859`.

The overlay verified 6,797 prior files and retained 6,752 by hardlink. Rollback is release `dfc7d666c4d5665e0f6a0f65440f8bb8fb33b824352aa412111976a889376b73`. The operator plan is at `/var/backups/webos-anicraft-upstream-a803cd86cb01/plan.json`. Both duplicate transfer archives were removed.
