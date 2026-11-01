# App workflow review

For a concise app-by-app index, see [App review status](APP_STATUS.md).

This is the working checklist for the Simplified desktop's app-by-app review.
“Prior evidence” refers to existing checks, not completion of the new review.
The primary audience is high-school seniors and college STEM students. Clear
onboarding should remain approachable to beginners while preserving the detail
needed for advanced work; avoid a child-directed presentation.

Every interactive app still needs a fresh review of its primary workflow,
account-backed open/save where applicable, first-run experience, desktop and
phone-sized interaction, cleanup, and an honest user-facing explanation.
Physical-device testing is separate. Shared tools need a tested consumer rather
than a standalone editor workflow. See `APP_USER_GUIDE.md` for concise student-facing workflows, `APP_WORKFLOW_CHECKS.md` for earlier
check scope and `SIMPLIFIED_HANDOFF.md` for dated deployment details.

Data Explorer now opens CSV and TSV in My files, with quoted TSV fields, SQL and saved analysis projects. Local desktop and emulated-phone account workflows and a live emulated-phone workflow passed sync, fresh-session reopening and changed-source warnings. Files also opens TSV directly in Data Explorer; desktop and emulated-phone account tests and a live emulated-phone test cover the handoff. Physical touch and large TSV inputs remain unverified. Live release `02f54a8c560d6b181ce8b6735d0aa0e7bcd36e023202cc03bb34eb6c64c3667f`.

Notebook now warns before closing during a save of an unchanged document; desktop and emulated-phone account tests and a live emulated-phone test cover held writes, cancellation, edits during the write and subsequent sync. Arduino Simulator keeps its status visible while scrolling and announces status changes; its firmware, serial, account sync, fresh-session and independent-window workflows passed locally on desktop and emulated phone and on the live emulated phone. G-code Preview accepts additional `.g`, `.gc`, `.ngc` and `.tap` filenames in its own picker; local desktop and emulated-phone and live emulated-phone tests cover supported paths, rejection of an unsupported coordinate system and account reopening. The filename alone does not establish controller compatibility. All changes are live in `fbb906a284e4072b8704dbffc41eb6eadba360057ac7bc4da68d6aaa99262e96`. Physical touch and physical hardware remain unverified.

Files now offers Open in Text for account files, allowing a CSV to be edited, synced, and reopened in Data Explorer; local desktop and emulated-phone and live emulated-phone account workflows passed. Temporary Linux files are excluded and invalid UTF-8 is rejected by Text. Spreadsheet prevents overlapping open choosers; local desktop/phone and live phone-sized checks cover cancellation, edit, sync, reopen, and a late chooser result after close. Digital Logic labels a diagram that no longer matches its JSON draft, including after truth-table calculation or a failed Run; local desktop/phone full workflows and a focused live phone check passed. Grid.Space rejects an export filename inconsistent with its format and preserves the pending export; local desktop/phone and live phone checks used real STL and G-code exports, sync, and recovery. Filename matching does not validate fabrication safety. All are live in `39a1c8053f6d266e600503050cbb8b217ce660a036a888ea7fd025031d95c129`; physical touch and hardware remain unverified.

Files asks before replacing an existing account file during upload; local desktop/phone and live phone-sized tests cover skipping, concurrent modification and successful server sync, and the existing location-binding check passes. Document Editor orders file-change checks so an older result cannot erase a newer warning; local desktop/phone and live phone checks cover delayed metadata, changes during save and reopening. Arduino now protects unsaved serial output before firmware changes and window close; local desktop/phone real AVR tests and live phone checks cover cancel, save and close. A full page reload still does not preserve serial output. Pico warns after a firmware worker failure and blocks saving or restarting an uncertain flash snapshot until recovery; local desktop/phone and live phone account tests inject a worker failure, and separate local real Blink tests passed. Unsaved flash after a crash cannot be recovered. Live release `5ffef0e6907ec08f2b5b0610e3ed2a60c5b2fb36fe44e28b44b4acb51604c3d8`. Physical touch, physical hardware and real emulator crash behavior remain unverified.

diagrams.net routes its local export save API to My files; local desktop/phone and live phone tests cover actual SVG/PNG export, cancellation, changed-target protection and server sync. Other upstream export types remain unverified. Text rechecks after an open/reload so a change during the read remains visible; delayed-read desktop/phone and live phone tests cover notice, saving a copy, sync and reopen. Circuit Simulator guards New Blank and the built-in circuit library against discarding edits or overwriting the old account file; local desktop/phone and live phone tests cover cancel, blank round-trip, saved library circuit and sync. Digital Logic integrates the contributor review at `abe8507b6`: new saves require `.logic.json` for Files routing while previously opened `.json` files can save in place; local desktop/phone and live phone tests cover both paths. Excalidraw hides its unintegrated shape library, including external library browsing; drawing and account save remain tested, and removed features are tracked in `DEFERRED_APP_FEATURES.md`. These UI controls are not a network security boundary. The tested release is `d28af034a752ab15ba9844a027b1923ce892940c8b5fdd8626cbc6c848d5a69a`. Physical touch and untested provider entry points remain open.

Applications → Games now contains previews of Falling Blocks, Owl Companion, Physics Playground and Snake Garden. Falling Blocks has per-window synthesized sound, muted by default; a real-browser live test checked enable, mute and cleanup, while local tests checked independent windows. All four pause when their desktop window loses focus and require an explicit resume. Live account tests covered Owl, Snake and Physics save/sync, paused reopen and isolation; local desktop/phone tests covered save races, close guards and focus behavior. Owl and Snake use labeled procedural placeholders; their authored Rive art is not yet available. Physics XR and full game acceptance remain incomplete. Physical-phone input, audible speakers and broad performance remain unverified. The live release is `9b70b08178d92db0dac97f73ffc5c54e70feac54a593c8f1468a01e72173d854`.

PDF Viewer now clears stale search status when page navigation cancels a search; desktop/phone local and live phone account tests cover pending and completed searches and fresh-session reopen. Electronics Design updates its desktop restore reference when opening or saving another project and clears it on New; local desktop/phone and live phone tests cover project switching, refresh, server sync and preservation of the prior project. Unsaved work still must be saved before refresh. Both changes are live in `406b901f8bc52427dcb3c8d477008af992d5f33579c6dd00da414604547136cb`; physical touch remains unverified.

Image Editor now selects watermark images from My files and provides a My files-backed temporary gallery for image annotations. Local desktop/phone and live emulated-phone tests cover both paths, invalid watermark rejection, saved pixels, server sync and no observed third-party requests in the tested flows. The separate computer Upload image remains. Annotation requires dismissing the gallery before Save; physical touch, large images and other provider paths remain unverified. Live release `97a6b241a1fc91823c2e636c27c8264f4f48e2ec8578a5b9b219d922b766090d`.

Spreadsheet commits an active cell before deciding whether a delayed open may replace the sheet; local desktop/phone and live phone account tests cover cancel, retained edit and server sync. G-code Preview rejects M218 hotend-offset commands and retains the previous preview; local desktop/phone and live phone tests cover commands, comments, sync and rejection. Audio Editor imports MultiTrack audio from My files; local desktop/phone and live phone tests cover two decoded tracks, invalid audio and pending-import close protection. At that release, MultiTrack session save and export were unavailable. That release was `0f90d663ff9904555603380fc5a00fa085afa3a5ae6c08be87ba290798217763`; physical touch and machine compatibility remain unverified. A later historical KLU relink receipt was found on box-git: its retained WASM marker and matching baseline inputs were verified, but the runtime experiment was not rerun and Circuit Lab remains unshipped pending distribution review.

Audio Editor can export a stereo MultiTrack WAV to My files; the editable session remains unsaved. Desktop and emulated-phone local tests and a live emulated-phone test checked rendered samples, overlapping timing, mute, server sync, error handling and the 128 MiB output limit. Replicad now restores the most recently opened or saved project after reload; local desktop and emulated-phone and live emulated-phone account tests covered project switching, preview, saving and recovery. Broader local tests also covered STL and STEP. Physical touch, real equipment and memory behavior with large audio remain unverified. Live release `25975f80bb9e3dace021b6e253535e20355336314078c810d4f28e9451224108`.

Document Editor project switching and recovery passed additional local desktop and emulated-phone account tests; no code change was required in that review.

Calculator can reopen its own calculation notes from My files, restoring the expression, angle unit and recorded result; it labels that result as not recalculated and sets Ans to it. Local desktop/phone and live phone-sized account tests covered synchronization, fresh-session recovery, account isolation, cancellation, malformed files and edits during the picker. Previous Ans history cannot be recovered from a note. Excalidraw’s hidden library was investigated locally: forcing it visible showed a shape added in one window in a second window; normal disabled controls and account drawing/sync passed desktop and phone-sized checks. Cross-account library persistence was not tested. Live release `d8f1c1166b62055088567fe4cef6d42ae697faf41c8d4a0a9f3222e0f9eb62cd`. Physical touch remains unverified.

PDF Viewer keeps the displayed page and page number aligned if a later page is too large to show; local desktop/phone and live phone-sized tests cover a three-page PDF and recovery to another page. Digital Logic clears a stale desktop restore reference when its initial circuit cannot open; desktop/phone local and live phone-sized account checks cover invalid-file preservation, simulation, save and refresh. A missing-file phone-sized test passed locally. Other rendering failures, physical touch and real hardware remain unverified. Live release `babaddc475c9cfc385015311e108b7f94ddce4beadb0347a228bc05ba788f734`.

Audio Editor now saves editable MultiTrack `.amss` projects to My files and opens them from Files. Local desktop/phone and live emulated-phone tests cover track audio, timing and mixer round trips, server sync, separate accounts, close guards, malformed files, stale-target conflicts and injected load/rollback failures. On failed undo clearing or rollback, the editor warns and marks the session unsaved. Single-track and mixdown regressions passed locally. The underlying format omits beat/snap state and can shorten long names; save warns about both. Decoding can consume more memory than the file size. Physical touch and audio hardware remain unverified. Live release `0124ca7eb4edf1f626e583e60eb6dee766c3c814f2b5c3f1a622a8d0941f625d`.

Spreadsheet marks an active cell edit unsaved before Jspreadsheet commits it; local desktop/phone and live phone-sized tests cover close cancellation, saving, server sync and reopening. A broader old open-safety regression initially stopped without output in a bundle without Data Explorer; it later passed desktop and phone-sized runs with Data Explorer included. Arduino Simulator clears a stale initial firmware association when opening fails; desktop/phone local and live phone-sized tests cover simulated Blink, save/sync and refresh. Audio Editor marks beat control changes unsaved; local desktop/phone and live phone-sized tests cover the close guard and saved tempo recovery. Beat/snap enabled state is still not retained. Physical touch, audio hardware and physical boards remain unverified. Live release `6d91f437fecae8a12c9be3a55191012d42ecbe689db9c17b231fdad24d2a6766`.

SVG Editor clears a stale restore reference when the original SVG cannot open; local desktop/phone and live phone-sized tests cover fallback, saving, sync and refresh. Pico updates the restore reference on opening or saving another project; local desktop/phone and live phone-sized tests cover project switching, sync, refresh and invalid launch using synthetic projects and a fake worker. A separate local phone-sized real Blink worker test passed; a real firmware project round trip and physical hardware remain unverified. Notebook’s lifecycle test now answers the desktop close dialog and passed local desktop and phone-sized multi-window, Python execution, sync and working-copy cleanup. These runs do not resolve earlier intermittent kernel allocation failures. Live release `95c87a6d38931fc7233fca62ba35c952efed09ce08b497f4b1919b856d8a1d33`. Physical touch remains unverified.

Audio Editor now stores beat/snap enabled state in an additional project metadata record. Local desktop/phone and live phone-sized account tests cover tempo and snap restoration, compatibility with projects lacking the record, malformed flags and acceptance by the native AudioMass decoder. Other AudioMass tools may discard this extra record; long names may still shorten. Image Editor clears a failed initial image association; local desktop/phone and live phone-sized tests cover fallback, preserving the original file, save/sync and refresh. Physical touch and audio hardware remain unverified. Files folder moves remain unavailable: a server-only prototype test demonstrates that a deliberately stalled tree hash blocks another account’s file listing, and browser journaling/recovery and direct-host-writer consistency are unfinished. Live release `463ea092b4f9923c2f933d97d7ea12dd897564fd2a0ea4874ad3ae1068e375b2`.

Data Explorer clears a failed initial analysis-file reference; local desktop/phone and live phone-sized account tests cover source preservation, example, save/sync and refresh. Kiri:Moto and Mesh:Tool clear a failed initial workspace reference; local desktop/phone and live phone-sized tests cover real model import, workspace save/sync and refresh for each. Local phone-sized missing-file fallback passed; one earlier Kiri missing-file full workflow timed out after fallback, cause unverified. These do not validate manufacturing output or physical touch. Live release `0d4b09d5bf2b8816cfa55b83102ab3be9f7ff677f9a04273b33472e35927aef6`.

Notebook’s pinned Pyodide proxy now handles both synchronous and asynchronous `Atomics.waitAsync` results. A deterministic test reproduced the original synchronous-result exception and passed both cases with the patch. Before the patch, two of three bounded simultaneous two-window runs timed out; after it, two desktop and two phone-sized local cycles and two live phone-sized cycles completed with independent kernels. This addresses the observed race, not every possible kernel or resource-pressure failure; physical devices remain unverified. A folder-lock source candidate is backed up separately at box-git `research/folder-lock-20261101` commit `65018616e95277df39c2fba1ca4bbf41eda13d54`; it is not deployed and folder moves remain unavailable pending recovery, direct-host-writer and operational work. Notebook live release `98d92d5a71d74e7db9b210ff76ee60370f4ae027383cb0696245420fe7dcdd9c`.

Files can move multiple selected files through one folder picker. Moves remain individual; a stopped batch reports completed moves. Local desktop/phone and live phone-sized account tests cover two files, sync and close; a local single-file regression covers cancellation, collisions and changed files. Folder moves remain unavailable. Data Explorer ignores an older chooser result after another open begins; local desktop/phone and live phone-sized tests inject delayed picker results and cover sync/reopen and close. Embroidery Studio now updates its restore reference when switching or saving a project and clears it on example or failed startup; local desktop/phone and live phone-sized tests cover project switch, save, sync, refresh and stitch export. Machine compatibility and physical touch remain unverified. Live release `8f2c44d28c626a87faf97c77933dec6f9b7d3321523a11c6232942fbb5aef542`.

Circuit Simulator and Stitch Converter clear failed initial-file references without modifying the original; local desktop/phone and live phone-sized tests cover example or artwork, save, server sync and refresh. Text ignores an older delayed metadata failure after a newer successful check; local desktop/phone and live phone-sized tests inject ordering and verify the draft saves and syncs. Physical touch, electronics hardware and sewing compatibility remain unverified. Folder-move research additionally matches canonical browser/server manifests including Unicode ordering; its branch `research/folder-lock-20261101` is at `d4a6a092d357ffded79a2998958cbca9493d0632` and remains undeployed. Live release `a5636f2d1035ba802339d82f383ec9362e5eaacd59605803e444411f159e68fc`.

diagrams.net updates its restore reference when opening or saving another diagram and clears it after a failed initial open. Local desktop/phone and live phone-sized account tests cover diagram switching, save/sync and refresh; invalid and missing initial-file fallback passed locally at phone size and invalid fallback passed live. Physical touch remains unverified. Live release `904a286a95f706e66977edb1f7d0f8d73d317627ef3fd2df936b0955dab62891`. Folder-move research now includes an isolated browser journal and two-tab/reload test, backed up on `research/folder-lock-20261101` at `facbde0b7df29abe2a58289bdf275a32871492e5`; receipt recovery, production mirror integration, direct host writers and the UI remain unfinished.

## Current goals and progress — 2026-10-31

The goal is a dependable browser-based desktop for high-school senior and
college STEM students. Apps should use the signed-in desktop identity and the
desktop's **My files** workflow: changes are saved in browser storage first and
synchronized with the account's server files. Students should not need a second
provider account just to open or save their work. The app-by-app table below is
the detailed evidence log; this section records the shared release goals and
their current gates.

| Goal | Progress now | What still gates completion |
| --- | --- | --- |
| Integrate every app with My files and the browser-backed account workflow. | Substantial Files, Text, document, spreadsheet, engineering and simulation workflows already have local and live evidence in the table below. Live releases integrate file actions into the native menus of Electronics Design, Circuit Simulator, diagrams.net, SVG Editor and Audio Editor. Embroidery Studio also has its My files actions in its File menu. The review also addresses duplicate wrappers and desktop title-bar sizing. | Finish an app-by-app review of open, upload, save, export, overwrite, conflict, account isolation, cleanup and phone/desktop behavior. Remove duplicate outer wrappers where an app has a native file menu; integrate storage into the app's own interface where it does not. Audit the remaining embedded apps for similar wrappers. |
| Remove app-level registrations and provider-account dependencies. | The Electronics Design GitHub account/history controls are hidden. Embroidery starts in a local workflow, and eight identified provider/account commands are blocked in the rebuilt live editor. Confirmed dependencies and removed or unsupported features are recorded in `DEFERRED_APP_FEATURES.md`. | The inventory is not complete. Review every app for sign-up prompts, API-key forms, provider login, cloud storage, analytics or other service calls. Verify that hiding an entry point actually prevents the request; do not call a feature removed based only on covering its sign-in button. |
| Keep third-party-dependent features blocked until an internal server-backed replacement is ready. | No internal replacement service is implemented for the deferred Embroidery AI features. The rebuilt live Embroidery editor removes provider transport and rejects eight identified provider/account commands, including Design from prompt, Redraw image and Ask about embroidery. A complete audit remains. | Audit the pinned app bundle for every entry point and outbound request, then keep these actions unavailable until a reviewed internal service supports the desktop identity, per-account limits, clear data disclosure and consent, abuse controls, and failure handling. The ordinary local editor must continue working without the service. |
| Make the app shell feel integrated, not like a collection of embedded web pages. | Electronics Design and several other editors have live wrapper cleanup; Embroidery cleanup is also live. Title-bar sizing has also been reviewed. | Review each app's menus, dialogs, status and responsive layouts. Replace browser-native prompts with themed dialogs where app workflows still use them. Check touch and large-screen layouts without sacrificing usable targets. |
| Keep the Browser app experimental and lower priority. | It remains marked “in development” in the launcher. | Do not let browser polishing delay the STEM app and file-workflow integration gates above. |

The rebuilt live Embroidery editor removes the MakerFoundry startup-link importer; local desktop and emulated-phone checks observed no MakerFoundry request. Its iframe CSP is a separate restriction. The dependency graph and packaged notice collection are recorded in `EMBROIDERY_DEPENDENCY_INVENTORY.md`; nested asset and source-availability review remains.

The live Arduino Simulator replaces native firmware, example-source and serial-output replacement prompts with desktop dialogs. Desktop, phone-sized and 4K checks cover cancellation and files changed during confirmation; the full local example/serial/GPIO, file-sync and Text-reopen workflows also passed. A public phone-sized collision and cancellation test passed. Physical touch remains unverified.

The live Replicad CAD app uses desktop confirmations for discard and replacement. Local desktop, phone-sized and 4K tests cover cancellation and changes during confirmation; a real STL geometry, sync, conflict and fresh-session workflow passed locally; a public phone-sized cancellation and changed-target test passed. Physical touch remains unverified.

The Embroidery candidate preserved edits made during discard confirmations and prevented overlapping Save As prompts. Desktop, emulated-phone and 4K local checks covered discard and replacement races, two-session file-change warnings, sync, reopen and listener cleanup; example and Stitch Converter workflows passed desktop and phone-sized tests. A later build is live; remaining network and dependency review continues.

The Embroidery candidate now bundles a reproducible archive of the exact
patched editor source and desktop integration, with a File-menu link. Its
archive and separate packaging script match the reviewed inputs; local
desktop and emulated-phone tests fetched the ZIP successfully and exercised
the provider restrictions and My files workflow. The existing public static
asset route serves a known Circuit Simulator source ZIP without login (HTTP
200); the `/browser-sources` page itself returns 401 signed out. Do not claim
that direct source-asset URLs require login. Review the user's login requirement
and the intended source distribution route before activating the candidate.

A rebuilt Embroidery candidate routes the editor's own Open and Place requests
to My files and adds a Place entry to its File menu. Real desktop, emulated-phone
and 4K account tests exercised both Open entry points, Place, inserted SVG
objects, project save, server sync and fresh-session reopen. One early phone
run began Place before the preceding Open finished; the test now waits for the
editor to finish and the app displays a wait message if a file action is busy.
The phone-sized local policy, export and save-safety regressions also passed.
The matching patched-source archive was regenerated and checked against host
sources. The update is live in release `0eb7730ce9b2c17fcab679da996c99406f2dc1878662ee27d0da7a531664e3e6`;
public emulated-phone file workflow and provider-policy checks passed. Physical
touch and physical sewing are unverified. Direct source-asset URLs are public
as described above; the separate `/browser-sources/` page requires login.

The live Pico Simulator uses desktop confirmations for board
replacement, simulated-flash reset, and project and serial-output overwrites.
Desktop, emulated-phone and 4K tests use synthetic firmware/fake worker for
cancellation and changes while confirming; separate local desktop/phone tests
cover serial sync, Text reopen and cleanup, and a phone-sized test runs the
real Blink worker. Public phone-sized tests passed the confirmation flows with synthetic firmware and the real Blink worker. Physical hardware and phone touch are unverified.

Digital Logic replaces native discard and overwrite prompts with desktop
dialogs in live release `f12200887e11ab34f34308ddb4d11692b5ff38192bdcfec8a2457b42b57868f1`.
Registered-account desktop, emulated-phone and 4K checks cover cancellation
and edits or file changes while confirmation is open; the real full-adder and
save-race regressions also passed locally. A local registered-account workflow
passed upload, sync, invalid-file recovery, Files open, fresh-session reopening
and truth-table CSV handoff to Data Explorer. A public emulated-phone account
test passed the confirmation protections. Physical touch remains unverified.

Stitch Converter replaces native discard and overwrite prompts with desktop
dialogs in live release `e08faf59b0760145cf69f118e71451724dd2958f35ece57fb4598b200c45a2c4`. Desktop, phone-sized and 4K account tests cover
cancelled prompts and edits or file changes during confirmation. The local
upload, save, conversion, sync and fresh-session workflow and delayed-save
regression passed. A public phone-sized account safety test passed. Physical
touch and machine compatibility remain unverified.

Data Explorer replaces discard, changed-source and replacement browser prompts
with desktop dialogs in live release `08ffb5ed31f300e3f180ccf690a459e11082ab31b41dd33a6765f40afb8f953f`. Desktop, phone-sized and 4K
account tests cover cancellation, SQL edits and file changes during confirmation,
including a source CSV changing while a project replacement is pending. A local
phone-sized example/SQL/export/reopen workflow and public phone-sized safety
test passed. Physical touch remains unverified.

Calculator replaces its browser overwrite prompt with a desktop dialog in live
release `29f8d8842c696d45664de4666d21dbe76504d3550a7b4d468bab91ace9dcfc41`. Desktop, phone-sized and 4K account checks cover cancel,
changed-file protection, snapshot saving, server sync and reopening in Text.
Arithmetic unit tests and the public phone-sized account workflow passed.

Falling Blocks uses desktop discard and replace dialogs in live release
`973ed6d4ed69f6729f272b563b1ec0f8b9ea2dd19f9228fdc020ea32c7477513`.
It pauses before a discard decision, guards changed progress and saved files,
and leaves the game paused on cancellation. Desktop, phone-sized and 4K
account tests cover cancellation, changed progress, file replacement, sync and
exact save reopening; local delayed-save, Files routing and game-model tests
passed. A public phone-sized account test passed; physical touch remains unverified.

Image Editor uses desktop Open, New and Save As confirmations in live release
`5a567ebae384f7bd4f18c3ca0d95be8514825a12a8c6746952343d572f78ac7c`. It waits for the editor's deferred change notification and
protects edits or files changed during confirmation. Desktop, phone-sized and
4K account tests cover cancellation, injected edit races, changed-file protection,
sync and reopening; real local resize, invalid-image recovery and Save As tests
also passed. A public phone-sized safety test passed. Its outer file toolbar
now has New, Open and Save As in a File menu in the
editor's own top bar. Desktop, phone-sized and 4K account tests cover pointer
actions, menu dismissal, save, sync, reopen and a simulated missing-toolbar
fallback. The File-menu update is live in release
`bc12051a9156f0d0f047ae0008fa52a3a1881fe8cf88f73417e0530e496df46f`;
a public phone-sized account test passed. Physical touch remains unverified.

Excalidraw moves My files open, image insertion,
drawing save and PNG export into its own main menu and removes the duplicate
outer toolbar. The menu keeps search, canvas controls and help; the native
computer-file image button is disabled in favor of My files. Desktop,
emulated-phone and 4K account tests cover menu input, image insertion, save,
export, conflict, reload after signing back in and fresh-session reopen. Local
phone-sized drawing, upload, image undo and delayed-save regressions passed.
Release `99afe9bd80ff4b9fcc006a4d588fd754cb525a482a810ce8c336c4aa9befd4e0`
is live, and the public phone-sized account workflow passed. Physical touch and
the full set of Excalidraw features remain unverified.

The third-party feature register is intentionally a **partial inventory**, not a
claim that every provider feature has already been removed from every bundled
app. See `DEFERRED_APP_FEATURES.md` for the exact known entries and replacement
gate.

The Electronics Design working copy now queues generated exports and drops a
cancelled export rather than reopening its save dialog. Local registered-account
desktop and emulated-phone-sized runs passed upload, editing, save and reopen,
queued export cancellation, conflict handling and a fresh-session reopen. The
phone-sized run used automated keyboard and pointer input; physical touch is
unverified. These changes have not been deployed. Earlier runs exposed test
setup issues: Snap Chromium could not read the temporary fixture, a simulated
editor message came from the wrong frame, and the close-dialog test predated the
themed dialog. The test now uses a shared fixture path and the actual frame and
dialog.

The diagrams.net working copy uses themed confirmations for discarding edits
and replacing files. Local registered-account desktop and emulated-phone-sized
runs passed editing, failed-open recovery, cancellation and confirmation of
replacement, upload, server sync and fresh-session reopening. A separate desktop
save-safety run passed destination capture, newer edits, conflict notices and
reopening; its first parallel attempt timed out at the login screen, and the
individual retry passed. Phone-sized checks used automation, not physical
touch. The working copy now places Open from My files and Save As in the editor File
menu and removes the duplicate file wrapper. Desktop and emulated-phone-sized
account workflows and a desktop save-safety test pass locally. The integration
uses the pinned editor popup implementation and needs review on vendor upgrades;
physical touch is unverified. A phone-sized save-safety run also passed. The
menu matches translated editor labels, and desktop and phone-sized checks
simulated translated labels and a missing popup API; recovery controls saved
the diagram in the missing-API case. A changed menu structure has not been
simulated. These changes are not live.

The StitchFoundry WebAssembly has an unresolved source-provenance gap. The
previously recorded `e3b80b2...` commit lacks account and Ask source files whose
paths and text appear in the pinned archive's WebAssembly. Upstream commit
`e5a88e0...` predates the archive timestamp, contains those features and matches
its README, notices, assets list and licenses; this is useful review evidence,
not proof that it produced the binary. Resolve the provenance gap before
claiming a rebuild corresponds to the currently shipped binary. The upstream
documentation estimates approximately 30 GB for a build directory, so the
candidate build uses box-git's larger data disk instead of the workstation.

A source-only StitchFoundry candidate is being prepared from `e5a88e0...` on
box-git's isolated `/srv/data/codi-embroidery-candidate-e5` build directory.
`apps/system/embroidery-studio/prepare_local_source.py` removes the browser
provider transport and credential store, hides provider entries in menus and the
command palette, and rejects their command IDs for WebAssembly. The patch
applied to clean local and remote checkouts with matching changed-file hashes.
The no-startup-link candidate built successfully and its freshly prepared source matched the build tree. In an isolated local preview, desktop and emulated-phone tests verified startup, blocked cross-origin fetch, absence and rejection of eight provider/account commands, project save, server sync, DST export and fresh-session reopening. At that stage the older shipped binary and live site had not changed. The later File bridge build is live, and its WASM matches the current live bundle; broader network, physical touch and licensing review remain open.

### Current milestone and handoff

1. Finish each app's real workflow: open from My files, edit or run, save,
   close and reopen, with account isolation, conflict handling, cleanup and
   desktop, phone-sized and large-screen checks. Upload from the user's device
   remains an explicit separate action. Temporary Linux files are separate.
2. Integrate file actions into each app's own menus where practical, remove
   duplicated wrapper controls, and replace browser-native dialogs with desktop
   dialogs. The app-by-app evidence distinguishes live releases from local candidates;
   do not describe a candidate as live until deployed and verified.
3. Inventory and remove third-party sign-in, account, cloud and service
   dependencies app by app. Hiding a control alone is not proof that the
   underlying integration is disabled. Record each affected feature in
   `DEFERRED_APP_FEATURES.md` and test both its interface and network behavior.
4. Keep affected features unavailable until an internal server-backed
   replacement is designed, implemented and verified under the replacement
   gate in that register. No replacement currently exists for the listed
   Embroidery AI features. Their removal or blocking must not prevent the
   ordinary browser-local editor and My files workflow from working.

The release milestone is every interactive app having an honest status and a
consistent, tested primary workflow, not merely a successful launch. The
app-by-app inventory and external-service audit are incomplete. Physical phone
testing, some app workflows, and the classroom capacity target remain separate
verification work. Source and notes are backed up to box-git; generated builds,
dependencies, user files and account state are not source backups.

Live release `5ad6f63d07e88fb7bdce101b4404493b2b2d9aa6ed18b60b758c816ccce61ee2`:
Document Editor prevents an Open operation from
discarding edits made while either confirmation is displayed. Desktop,
emulated-phone and 4K account tests inject those races and cover open, edit,
save and sync; the phone-sized open-safety test also passed fresh-session
recovery. Data Explorer now separately reports changes, deletion or conflicts
in the saved analysis project and reports an immediate conflicting save
honestly. Desktop, emulated-phone and 4K two-session account tests cover
change, deletion, conflict, save copy and fresh-session recovery; an immediate
write-conflict response was injected in a phone-sized test. Both checks also
passed on the public site at phone size; physical touch remains unverified.

Spreadsheet clears a stale layout reference when importing
CSV or XLSX and rejects empty, plain-text and tested truncated XLSX inputs
without replacing the open draft. Desktop, emulated-phone and 4K account tests
cover invalid imports and CSV save, sync and reload; a valid XLSX and a separate
save-race regression passed at phone size. Unusual XLSX files and physical touch
remain unverified. PDF Viewer adds page-number navigation;
desktop, emulated-phone and 4K account checks cover My files open, navigation,
invalid numbers, search, resize and fresh-session reopening. Public phone-sized
account checks also passed both workflows.

Embroidery Studio's File menu places Open and Save first,
increases touch targets, and returns focus on Escape. Desktop, emulated-phone
and 4K menu tests, desktop/phone file workflows, and a phone-sized provider
command/CSP regression passed. Its corresponding-source archive was regenerated
and checked against the integration files; a clean isolated packaging run
passed with the updated pin. A public phone-sized menu test passed. Physical touch and
the complete upstream service surface remain unverified.

Audio Editor asks before closing during a WAV save or effect,
including when the track was previously clean. Desktop, emulated-phone and 4K
checks cover a held Save As, cancelling close, completion and sync; an effect
check simulated a clean state during processing. The phone-sized effect and
layout regression passed. Already-dispatched writes can still complete after a
close; a public phone-sized check passed and physical touch is unverified.

Text guards Open and Reload against CodeMirror edits arriving
during discard confirmations, including edits while the file picker is open.
Desktop, emulated-phone and 4K account tests use real editor transactions and
cover draft preservation, save, server bytes and fresh-session reopen; existing
confirmation regressions passed at all three sizes. A public phone-sized
workflow passed. Physical touch is unverified.

Live release `c893a35a981a2180ade8f67e01214c69f9bbb978e970a54f56a2b75976a11b6f`:
SVG Editor rechecks drawing changes
around discard prompts and the picker; concurrent-change tests were simulated
at desktop, emulated-phone and 4K, followed by save, sync and reopen. Calculator
reports exactly represented tangent poles as undefined; arithmetic and
desktop/phone/4K workflow checks include nearby valid angles. Circuit Simulator
clears an old layout reference when an example replaces a saved circuit;
desktop, emulated-phone and 4K account checks cover save, sync, reload and
account isolation, and the old code failed the targeted regression. Image
Editor warns before closing while saving even when initially clean; held-save
tests covered desktop, phone and 4K, while the failed-save edit was simulated.
Public phone-sized account checks passed for all four apps. Physical touch and
unusual cases remain unverified.

Arduino Simulator clears the saved HEX reference when a
bundled example replaces it; desktop, emulated-phone and 4K tests ran the real
AVR worker and covered refresh, save, sync, account isolation and cleanup. The
old source failed the targeted stale-reference test. Terminal
handles missing, synchronously throwing and rejected Clipboard API calls and
ignores late paste results after closure. Desktop, emulated-phone and 4K checks
used a real v86 shell with stubbed clipboard responses; the phone-sized
two-shell and nano regression passed. Public phone-sized tests passed for both;
physical hardware, actual clipboard permission prompts and touch are unverified.

Live release `8c8dd9f477bd8df8b0decc6aa9f59e61d5e892ea124140058370b0d0020011d7`:
Notebook prevents an explicit save from silently writing the
linked notebook when a different Jupyter tab is active, including a tab switch
during Save As. Desktop, emulated-phone and 4K tests use Jupyter's API to switch
tabs, verify server bytes and continued automatic saving; the phone-sized menu
regression passed. Stitch Converter clears the old machine
file association when an example is chosen, so replacing a prior PES requires
confirmation. Desktop, emulated-phone and 4K tests cover cancellation,
replacement, sync and reopen; the old code overwrote the PES without a dialog
in a negative control. Public phone-sized tests passed for both. Physical touch
remains unverified.

Files has a Select multiple mode for plain taps, plus clearer partial
upload/deletion results and conflict checks before deletion. Desktop,
emulated-phone and 4K tests cover selection, an actual upload collision and a
two-browser conflict; a second-delete failure was injected. Uploads and deletes
remain per-item, not atomic. Spreadsheet reports
exact tangent poles as errors and refuses CSV export of the invalid result;
desktop, emulated-phone and 4K account workflows cover correction, save, sync
and reopen. Public phone-sized tests passed for both; physical touch and unusual
numerical precision cases remain unverified.

Live release `06dbfc2a20a2ec4a343d549ac73282e196b9acd986b12f8ea29b0088c4d99f79`:
G-code Preview fits a tested
320×568 phone-sized viewport and keeps its visual-only warning visible; desktop,
phone and 4K account workflows cover opening and invalid-file preservation.
Replicad guards in-progress saves and exports; held-operation tests cover close
cancellation, real STL generation, sync and reopening at all three sizes.
Digital Logic explains incompatible wire widths before simulator construction,
preserving the prior circuit; matching and mismatched widths, correction, truth
table, sync and reopening were tested locally. Physical touch and actual
machine or board behavior remain unverified. Public phone-sized tests passed
for all three apps, including real STL generation and account sync.

Live release `1af8bd99a73a7773c7e6671a71f59a6f54840207bc22a4b8fdec1dfae3727dd9`:
Data Explorer restores the prior result
and viewer settings when switching to a new query result fails; an injected
failure after a real table switch and a real invalid query were tested at
desktop, emulated-phone and 4K sizes. PDF Viewer finds phrases spanning extracted
line breaks; a generated two-line PDF and existing search regressions passed at
those sizes. Pico Simulator retains the serial reading position while scrolled
up and provides Jump to latest; simulated packets were tested at those sizes,
with a separate real Blink-worker check. Physical touch, PDF extraction order
and real-firmware serial behavior for this change remain unverified. Public
phone-sized account checks passed for all three workflows.

Live release `d8c9c1f7074d037631c8075e85fc601a9ba3deb17a3e3f2641de47869769d13b`:
Circuit Simulator's XML import check rejects missing positions and
components silently skipped by the simulator, restoring the previous circuit.
Desktop, emulated-phone and 4K account tests cover invalid and valid imports;
phone-sized menu and export regressions also passed. The corresponding-source
archive was regenerated and checked against the host files. This check does not
fully validate parameters or legacy text imports. SVG Editor
routes focused Ctrl+S to My files and Ctrl+Shift+S to Save As, and prevents
overlapping actions during path prompts. Desktop, emulated-phone and 4K account
tests cover shortcuts, save, export, sync and reopen. Public phone-sized tests
passed for both. Physical touch and actual Mac shortcuts remain unverified.

Live release `04d51cf02682f7e8a6902489c29c7f1975d9f1433a9be7551a4eba41748c548b`:
Pico Simulator ignores Enter while an input method is
composing text, preventing a partial serial command from being sent. Desktop,
emulated-phone and 4K account tests used synthetic composition events and a fake
board worker; a separate real Blink-worker check passed. Physical keyboards and
MicroPython serial behavior for this change remain unverified. A public
phone-sized check passed.

Live release `0db4822d66dfa593aa266d615bf8a28d66b963d9762bcfd24d6b343e7440785c`:
PDF Viewer moves Previous, Next and Go to the
top of the selected page while Find continues to scroll to its match. Desktop,
emulated-phone and 4K tests used a real synced three-page PDF, and phone-sized
page-jump, search and reload regressions passed. The test set the prior scroll
position programmatically. A public phone-sized check passed; physical touch
remains unverified.

Replicad adds Cancel preview, terminating only the active
preview worker while keeping the previous canvas and allowing a retry. Desktop,
emulated-phone and 4K checks cover cancellation, worker cleanup, retry, save,
sync and reopening; the phone-sized STL workflow also passed. The test verifies
the prior canvas remains, not pixel-identical rendering. A public phone-sized
check passed; physical touch remains unverified.

Calculator's keypad enforces the 512-character expression
limit while still allowing a selected range to be replaced at the limit.
Desktop and emulated-phone keypad tests and existing calculation regressions
passed; the previous keypad could create an expression its parser rejected.
A public phone-sized test passed; physical touch remains unverified.

Digital Logic asks before closing while a circuit or truth
table CSV save is pending, even if the circuit was clean. Desktop,
emulated-phone and 4K tests held saves, cancelled close, then checked real
simulation output, sync and reopening. Operation delays were injected; writes
already dispatched to storage may still finish after closure. A public
phone-sized check passed; physical touch remains unverified.

Live release `e87dc394762835f1510801a828fd7002b2cffc5b06837418f48d97aab13e620e`:
Calculator marks a calculation-note save as pending
for the desktop close guard. Desktop, emulated-phone and 4K account tests held
the save, cancelled close, changed the expression and verified the captured note
synced and reopened. Hold/failure timing was injected; storage was real. The
minimal host guard and Calculator update are live together; a public
phone-sized check passed. Physical touch remains unverified.

Image Editor updates the restore reference on open and
save and clears it for a new blank image. Desktop, emulated-phone and 4K tests
cover opening a second image, creating a blank, refreshing, then saving and
reopening; a phone-sized Save As and fresh-session test also passed. An unsaved
blank is not recovered on refresh. A public phone-sized check passed; physical
touch remains unverified.

G-code Preview strips balanced parenthesized comments
and rejects unmatched or nested parentheses. The previous worker interpreted
`X10 (X999)` as X999. Desktop, emulated-phone and 4K tests compare real-worker
geometry and rendered output, and verify malformed comments preserve the prior
preview; the large-file cancellation regression and a public phone-sized test
also passed. This does not establish controller or physical-machine behavior.

Notebook's Save As asks before replacing an existing notebook,
checks the observed version and cancels if the active tab changes during the
confirmation. Desktop, emulated-phone and 4K account tests cover cancellation,
both races, accepted replacement, sync and fresh-session reopen; a separate
desktop regression ran the real Pyodide example. The test switches tabs through
Jupyter's API. A public phone-sized test passed; physical touch remains unverified.

Arduino Simulator shows a persistent notice when its
opened or saved HEX changes, disappears or conflicts in My files, while keeping
the loaded firmware running. Desktop, emulated-phone and 4K checks exercised
real two-browser changes, deletion and conflict, plus AVR serial echo and
subscription cleanup. Spreadsheet warns before closing during workbook saves
or CSV/XLSX exports; desktop, emulated-phone and 4K checks held real conversion
and writes, cancelled close, then verified sync and reopening. Those delays were
injected and already-dispatched writes can still finish after closure. Public
phone-sized tests passed; physical touch and hardware remain unverified.

Arduino Simulator follows serial output while at the bottom,
pauses when the user scrolls up and resumes at the bottom. Desktop and 4K wheel
tests and an emulated-phone swipe used real AVR serial echo, then saved and
synced the log and reopened it in Text. Returning to the bottom was set
programmatically; physical touch remains unverified.

Excalidraw routes focused Ctrl/Command+S to My files
and Shift+Ctrl/Command+S to Save As; a browser test drew and saved a real shape,
and the phone-sized native-menu workflow passed. Pico Simulator warns before
closing while saving a project or serial output; desktop, emulated-phone and
4K tests used real account storage with a simulated board, and a separate phone
Blink worker test passed. Both changes are included in current live bundles;
physical phone and macOS shortcut behavior remain unverified.

Data Explorer cleans up and permits retry after an injected worker-constructor
failure; other initialization failures are not yet covered. Stitch Converter
keeps a changed preview when another file is opening; desktop, emulated-phone
and 4K account tests delay the file read, alter the preview, then verify it
remains open and retry works. Both are live: the public Data Explorer failure
injection used a desktop-sized viewport, and the Stitch test used a phone-sized
viewport and mouse clicks. Physical touch and sewing remain unverified.

Circuit Lab remains gated and is not deployed. Its local source candidate uses
desktop discard confirmation, reports immediate file conflicts and cancels
stale simulations. A simulated-worker/file-service guard test passed, as did
separate real ngspice divider, transient and MOSFET tests. The source-package
audit now binds packaged app inputs to the build. A matching private research
archive was rebuilt on box-git and its package and built-app audits passed; a
fresh extraction relinked modified numparam code and solved a 5 V circuit. The
PTM redistribution question remains unresolved; do not deploy or publish the
unreviewed models. A private fresh-extraction experiment modified KLU_defaults,
relinked it and observed its marker execute while solving a 5 V divider; the
original engine control solved it without the marker. This proves one relink
path, not a clean independent rebuild or all configurations. The archive is private research
material, not a completed distribution review.

G-code Preview rejects `M206` and `M428` home-offset changes rather than
silently ignoring them. Desktop, emulated-phone and 4K account tests exercised
the real parser and preview and verified that the prior view remains open. The
live phone-sized test used mouse clicks; physical touch, other controller-specific
behavior and physical machines remain unverified.

Digital Logic rejects multiple outputs wired to the same input before simulation
or truth-table generation, while keeping the prior diagram. Desktop,
emulated-phone and 4K account checks passed; the existing comparator also
passed all 16 combinations with supported output fan-out, sync and reopen. A
live phone-sized account check passed. Physical touch and electrical-bus
behavior remain unverified.

Notebook opens an editable starter when a directly opened file is invalid,
while keeping that file untouched and the error visible. Desktop, emulated-phone
and 4K tests cover invalid and valid direct launches; a live phone-sized account
check also passed. This test did not run Python. SVG Editor keeps an original
and a Save As copy in separate windows; a live desktop account regression and
local phone-sized shortcut regression passed. Physical touch remains unverified.

Document Editor resets Undo history when another report opens, preventing Undo
from erasing the new report or restoring the old one. Real browser editing,
Undo, Redo and server-synced save passed locally on desktop and phone-sized
viewports and in a live phone-sized account test. Physical touch remains
unverified.

Spreadsheet commits an active cell before a save or CSV/XLSX export; desktop
and phone-sized tests reproduced and fixed an old-value save. Electronics
Design preserves failed generated exports for retry and pauses its queue;
desktop, phone-sized and 4K tests used injected storage failure and simulated
generated bytes with real account sync. Stitch Converter rejects malformed SVG
on save while retaining the draft and previously saved file; valid empty SVG
still saves and reopens. Desktop and phone-sized tests passed, including the
existing phone-sized upload and PES workflow after its missing Files test
dependency was added. Public phone-sized account tests passed for Spreadsheet
and Electronics Design; Stitch passed desktop and phone-sized public checks.
Physical touch for Spreadsheet and Electronics Design and physical hardware
remain unverified.

Arduino Simulator has a pending-save close guard for firmware, source and
serial output. Desktop, emulated-phone and 4K account tests held writes open,
cancelled closing, then verified sync with a real AVR serial worker; a first
run hit the concurrent transfer limit when reading three files at once, and a
sequential rerun passed. The live phone-sized account check also passed.
Dispatched writes can finish after closure; physical touch and hardware remain
unverified.

G-code Preview rejects unsupported G commands with geometric or extrusion
parameters instead of silently omitting possible motion.
Real-worker desktop and phone-sized checks cover splines, probes, drilling,
dwell and comments; the prior preview remains open. Home-offset, modal and
arc regressions also passed. An initial arc run used an unavailable debugging
port; rerunning with the active port passed. A live phone-sized account check
passed. This does not establish machine compatibility or safety.

Digital Logic validates wire port existence and direction before simulation or
truth tables; invalid connections retain the previous diagram. Desktop and
phone-sized account tests and the phone multiple-driver and 16-case comparator
regressions passed. An initial comparator run used an unavailable debugging
port; rerunning with the active port passed. A live phone-sized account check
also passed; physical touch and hardware behavior remain unverified.

Image Editor supports focused Ctrl/Command+S and fixes a reproduced immediate
resize/save race. A same-turn test reproduced saving 800×600 rather than
320×240; the fix waits one event turn and snapshots the current editor state.
Desktop and phone-sized tests verify saved dimensions through the native Save
button and shortcut. The pending-close test passed; the account-switch test ran
before the last snapshot-order adjustment. A live phone-sized account test
verified saved dimensions. This does not prove timing for every image tool,
physical touch or Mac shortcuts.

Replicad disables the box-only depth field for cylinders and
allows a cylinder to be saved when the unused field is blank, retaining a box
depth when switching back. Desktop, phone-sized and 4K tests used the real CAD
preview worker and account sync. Pico Simulator rejects UF2 file containers,
which use file offsets instead of flash addresses, without replacing the
running board. Desktop and phone-sized account workflows used real Blink and
synthetic container data; Pico flash, machine-code Blink, project and serial
tests passed. Live phone-sized account checks passed both workflows; physical
touch, physical devices and manufacturing remain unverified.

Files reports how many files moved when a later item in a
multi-file drag fails. Desktop and phone-sized account tests used mouse-driven
multi-select/drag with a destination collision and confirmed both files; the
existing phone-sized move/sync/reopen workflow passed. Audio Editor routes
focused Ctrl/Command+S to its My files WAV save; desktop and phone-sized tests
verified synced WAV samples. CircuitJS warns before closing during pending
saves or image exports; desktop and phone-sized checks held a real account
write, cancelled close and verified sync, and the existing phone file-menu
workflow passed. The older CircuitJS file-safety test has a stale empty-root
assertion and did not complete. Its corresponding-source archive was rebuilt
and checked against the app source and README. Live phone-sized account checks
passed Audio Editor and CircuitJS. A subsequent Files release fixed the observed
intermittent drag issue as described below. Physical touch, Mac shortcuts and
closing during a real image export remain unverified.

The live Files bundle initially expected move-readiness fields absent from the
older live mirror module, disabling drag. The current mirror is now live; it
supplies those fields, serializes local moves with sync and supports moving a
new offline file. Its local storage suite, idle scheduling, phone-sized offline
move and account sync/reopen checks passed. A live phone-sized Move to… test
covered offline movement, collision, sync and fresh-session recovery; a separate
live conflict-resolution test passed. On the older build, multi-file drag passed in 4 of 8 live automated runs;
the browser sometimes changed the target drop effect to none before release.
A pinned Chonky patch is now live: a deterministic delayed-hover test, a
cross-window drag and three repeated phone-sized mouse-driven drags passed on
the served assets. Physical touch and broader drag scenarios remain unverified.

Terminal clears click suppression after a cancelled swipe. Desktop and
phone-sized tests used actual CDP touch cancellation and the real v86/Linux
guest, including a completed scrollback swipe; a live phone-sized test passed.
Physical touch remains unverified.

Image Editor rejects animated PNG and WebP before opening: the still-image editor would otherwise save just one frame. Desktop
and phone-sized tests used real two-frame files and static browser-generated
images, verifying preservation of the original file and current edits. A live
phone-sized account check passed. Physical touch and other image formats remain
unverified.

Text Editor preserves UTF-8 BOM and uniform CRLF,
CR and LF endings. Mixed endings require explicit confirmation before they are
normalized to LF; cancel preserves the draft and original. Desktop and
phone-sized account checks cover save, Save As, cancellation and server bytes;
first-save and concurrent-confirm regressions passed. A live phone-sized
account test verified server bytes and both confirmation paths. It does not
preserve individual endings in a mixed file; physical touch remains unverified.

Data Explorer protects project saves and CSV exports from window closure. It also tracks real Perspective viewer changes made during
those writes, so a later chart remains marked unsaved after an older snapshot
is saved. Desktop and phone-sized account tests held writes, used the viewer
API, checked close cancellation and verified subsequent server saves. Both
checks also passed live at a phone-sized viewport; physical touch and every
viewer configuration remain unverified.

Files has a pinned Chonky patch for a stale hover-state drag race. A
deterministic delayed-frame negative control failed on the old build and passed
with the patch; six candidate partial-drag and four cross-window tests passed
against the live account service using hash-verified intercepted assets. This is
live; deterministic stale-hover, cross-window and three repeated phone-sized
mouse-driven account checks passed. Physical touch and broader drag scenarios
remain unverified.
PDF Viewer has a fix that prevents slower, earlier metadata checks from
clearing a newer file-change warning. Desktop and phone-sized account tests
covered delayed checks and existing change/deletion/reload behavior; a live
phone-sized account check passed. Physical touch remains unverified.

The standard Files builder now stages its hash-checked Chonky dependency
automatically after shared builder dependencies are installed. A build with the
app-local package absent recreated it and produced the same Files index hash as
the live bundle. Custom source or entry overlays still prepare themselves.

Pico Simulator rejects UF2 blocks with conflicting
overlapping flash bytes, while allowing identical overlaps. Desktop and
phone-sized account checks used synthetic conflicting firmware and the real
Blink worker; unit checks cover both block orders, valid overlap and adjacent
blocks. The full Pico suite passed. A live phone-sized account test passed;
physical hardware and arbitrary firmware remain unverified.

diagrams.net cancels Open if the current diagram changes
while discard confirmation is displayed; desktop and phone-sized tests used a
delayed embedded autosave and the existing phone workflow passed after adding
its Files test dependency. Excalidraw now marks background and serialized grid
settings unsaved, while zoom and pan remain view-only; desktop and phone-sized
account tests cover background-only edit, close warning, save, sync and reopen.
Initial test failures were traced to a missing Files bundle and an already-open
menu respectively; corrected reruns passed. Live phone-sized account checks
passed both cases. Physical touch, concurrent Open invocations and UI-level grid
behavior remain unverified.

Files rechecks captured folder listings and file versions
after ZIP assembly and stops before writing if a change is detected. Tests
injected an added file during compression and verified a successful retry;
changes after the last check can still be missed and Linux guest fallback is
unverified. Spreadsheet opens an editable blank workbook after an invalid direct
launch while keeping the original untouched; account tests save and reopen the
recovered workbook. diagrams.net warns before closing during editor export or
account write, and restores prior dirty state after failure. Desktop and
phone-sized tests passed; the diagrams test uses a programmatic fallback Save
control. One Files parallel test and a diagrams registration run timed out;
sequential reruns passed. A broader Spreadsheet check lacked Data Explorer in
its isolated bundle and is not claimed. Live phone-sized account checks passed
all three; the Files drag stale-hover regression also passed on the new bundle.
Physical touch remains unverified.

G-code Preview rejects additional A/B/C/U/V/W axes instead
of silently omitting motion, including unsupported G commands and modal forms.
Real-worker desktop and phone-sized account tests covered all six axes,
comments and preservation of the prior preview. Notebook updates file identity
after Open and Save As; desktop and phone-sized account tests cover the original
and copy in separate windows and server sync. Notebook's Save As command was
invoked programmatically; an earlier menu attempt timed out. Live phone-sized
account checks passed both cases. Physical touch and machine safety remain
unverified.

Kiri:Moto and Mesh:Tool have a workspace-save close guard. Desktop and
phone-sized tests used real model import and account sync, held the workspace
write and injected a separate pending export to verify its warning remains.
The initial setup clicked before model load completed and timed out; reruns
waited for readiness. Actual export generation during the race, physical touch
and fabrication hardware remain unverified. Live phone-sized account checks
passed both editors.

Excalidraw reports an invalid direct open and starts an
independent Untitled drawing without changing the original. SVG Editor warns
before closing during SVG saves or image/PDF export, restoring prior dirty state
on failure. PDF Viewer checks a new PDF’s first-page display limit before
replacing the current document. Desktop and phone-sized account tests cover
these workflows, including real editor saves and PDF.js; one early PDF status
check saw a transient discrepancy, and subsequent runs passed. Live phone-sized
account checks passed all three. Physical touch, PDF export during close and
later PDF render failures remain unverified.

Document Editor recovers from an invalid direct open into
an independent editable Untitled report without changing the original. G-code
Preview rejects malformed or repeated coordinates in supported moves and G92
resets rather than silently parsing part of a value. Desktop and phone-sized
account checks covered recovery/sync and real-worker preview rejection. The
G-code check is not comprehensive syntax or machine validation. Live
phone-sized account checks passed both cases; physical touch remains unverified.

Image Editor checks image signatures before decode, preventing a GIF
renamed as PNG from bypassing animation protection and being overwritten as a
still image. Desktop and phone-sized real-editor/account tests used a two-frame
GIF and PNG/JPEG/WebP round trips; the phone resize/Save As test also passed.
An initial phone test hit a detached node and an initial round-trip test clicked
a disabled clean Save; corrected reruns passed. Live phone-sized account
checks passed both the mismatch and supported format round trips. Physical
touch and malformed files mimicking valid signatures remain unverified.

Text Editor recovers from an unreadable direct-open file:
it retains the error, starts an independent editable Untitled note and requires
a new save path without changing the original bytes. Desktop and phone-sized
account tests covered editing and server sync; existing first-save and line-
ending checks passed. A live phone-sized account check passed; physical touch
remains unverified.

Embroidery Studio has a pending-project-save close guard that starts
before account metadata checks. Real editor/account tests passed desktop and
phone-sized checks, including cancelling a close while a clean project saves.
The matching source archive was rebuilt and checked against the app integration;
a live phone-sized account check passed. Physical touch and sewing remain
unverified.

Data Explorer has a single-statement query check. A query beginning
with SELECT previously executed a second statement that changed the in-browser
working dataset while reporting success; the account CSV was unchanged. The
candidate scans one SELECT/WITH statement and uses a DuckDB prepared statement
for the result table. Desktop and phone-sized real-DuckDB/account tests reject
the injected query and project while retaining rows, and accept tested quoted,
dollar-quoted and comment semicolons. A temporary scanner-bypass test observed
DuckDB reject that specific multi-statement with an upstream error. A live
phone-sized account check passed the injected and legitimate query cases. This
is not a general SQL security sandbox.

G-code Preview rejects motion after M2/M30 rather than
assuming a controller dialect. Real-worker desktop and phone-sized checks cover
program-end variants, ordinary M20, comments and preservation of the previous
preview. A live phone-sized account check passed; this is not a machine-safety
validation.

Document Editor and Excalidraw hold their close guards during
saves and exports, even when the document was clean when the operation began.
Desktop and phone-sized real-editor/account tests covered delayed saves,
exports, cancellation and sync; the Document test also covered failure and
newer edits. An Excalidraw PNG regression initially omitted Image Editor and
passed after rebuilding with it. Live phone-sized account checks passed both.
Physical touch and accepting close during an already-dispatched write remain
unverified.

Text holds its close guard during pending saves, restoring
clean state on failure and retaining later edits. Arduino Simulator does not
send serial input when Enter completes an IME composition. Desktop and phone-
sized account tests covered delayed saves and real AVR serial echo with
synthetic composition events. Live phone-sized account checks passed both;
physical touch and physical IME behavior remain unverified.

Folder move and rename remain unsupported. The existing live gateway and browser
journal cover individual files, not a versioned subtree. An unrouted local
server experiment now tests a bounded manifest, no-replace rename and durable
receipt across injected process exits; 17 focused filesystem tests passed.
Out-of-band writes, orphan recovery, backup invariants, scalable limits and the
browser protocol remain unresolved. See `FOLDER_MOVE_DESIGN.md`; no folder
endpoint, UI or copy-and-delete substitute has been enabled.

Stitch Converter has a close guard for artwork saves and machine-file
exports. Desktop and phone-sized real-converter/account tests covered pending
saves, PES output and a simulated failure; existing save-race and conflict
regressions passed. A live phone-sized account check passed; physical touch
and sewing remain unverified.

Pico Simulator checks UF2 block counts: when a nonzero total is
declared, inconsistent, duplicate or incomplete numbered blocks are rejected
without replacing the running board. Zero-count legacy files remain accepted
without a completeness claim. Desktop and phone-sized real-Blink/account tests
and Pico regressions passed; an official MicroPython UF2 parsed but was not
executed. A live phone-sized account check passed; this is not physical
hardware validation.

### Embedded-app file-menu review

The screenshot issue is a cross-app review item, not an Embroidery-only fix.
These embedded apps currently have an outer Codi file toolbar or path panel;
review each against the engine's own menus before deciding where its actions
belong:

| App | Current status |
| --- | --- |
| Electronics Design | The live release removes the duplicate host file row; its editor File menu uses the My files adapter. The separate three-view layout action remains in the host shell. A real canvas menu check passed desktop mouse open/save but an emulated-phone tap selected the covered parent menu instead of the visible submenu. The pinned-source hit-testing patch was rebuilt on box-git; actual desktop mouse and emulated-phone tap open/save tests, desktop/phone account workflows and the 4K three-view account workflow pass locally. The tested binary is live in release `d1342bd85bc6fcf7f01871fc350509ad786f854caeeeff57ed7f661a8cea597c`; public desktop mouse and emulated-phone tap open/save checks passed. Physical touch remains unverified. |
| Embroidery Studio | Live File-menu integration replaces the outer file row and routes Open and Place to My files. Eight identified account/provider commands are blocked in the rebuilt editor, and its policy blocks direct third-party connections. A complete review of other provider entry points remains. |
| diagrams.net | The live release removes the duplicate file row and places Open from My files and Save As in the editor File menu. Native Save updates the current My files document. Local account workflows now pass real mouse clicks, emulated taps, keyboard activation and a 4K-sized viewport, plus desktop save-safety checks. Earlier tests used direct JavaScript clicks and missed upstream pointer interception. Static release `86f7fbc0e7c9610d641b96f0e0afa9f5f3ccb9f39599f4a42b065d3065058bb2` fixes it; public mouse and emulated-phone tap account workflows passed. Physical touch and vendor-update compatibility remain to be checked. |
| SVG-edit | The live release moves Open, example, Save and Save As into the SVG-Edit menu and removes the outer file row. Local desktop and emulated-phone-sized account tests cover examples, edits, upload, invalid files, replace cancellation and confirmation, syncing, conflicts, fresh-session reopening and opening the saved SVG in Stitch Converter. A local 4K-sized example check also passed, including keyboard activation of a menu item. Image export now saves PNG, JPEG and WebP to My files with overwrite and size checks; local desktop, emulated-phone and 4K-sized checks cover image signatures, decoded PNG artwork, PNG server sync, replacement cancellation/confirmation, size limits, no popup and the missing-menu fallback. PDF export uses a raster image and is not a vector document; local desktop, emulated-phone and 4K-sized checks save and sync the PDF and render its artwork in PDF Viewer. One initial desktop assertion sampled the canvas during a resize; waiting for rendered pixels passed. Public registered-account desktop and emulated-phone tests also passed the example, image and raster PDF exports, sync, reopen and fallback. File actions have 44 px targets. Complex SVG rendering and physical touch remain unverified. |
| Audio Editor / AudioMass | The live release replaces host-side discard and replace browser prompts with desktop dialogs and rechecks the file version after replacement confirmation; local desktop and emulated-phone tests cover cancellation, a changed target, saving and sync. The release puts the My files actions, WAV options and tone example into AudioMass's File menu, removes the duplicate row, and suppresses its delayed welcome screen. Local desktop, emulated-phone and 4K-sized menu tests cover save, sync and reopening; a separate phone retry passed after a parallel login timeout. The toolbar-based tests now use the menu; local desktop and emulated-phone checks passed upload, sample-checked editing, precision, fresh-session recovery and independent microphone cleanup. Desktop tests passed layout restoration, source conflicts and missing-menu fallback. AudioMass, Tone and WaveSurfer integration passed locally on desktop and emulated-phone views, and a file larger than 32 MiB opened and saved locally. The first audio-tools run timed out on the new themed discard dialog; its updated rerun passed. The preparation script now retains the WAV worker declaration after a fresh rebuild; desktop and phone-sized save/reopen tests passed on the resulting bundle. The phone menu has 44 px targets and passed emulated-tap checks. The Audio Editor bundle is now live in release `859caf0f2820d451752a6f213c7c5de4597a5f2c295813cb18efc2a9333ea9af`; public registered-account desktop and emulated-phone tests passed menu actions, replacement safety, Save As, sync and reopen. Physical touch remains unverified. |
| Circuit Simulator / CircuitJS | The live update uses themed discard and replace dialogs, rechecks changes while a dialog is open, and reports conflicting writes. Desktop and emulated-phone cancellation and stale-change tests passed, along with local example, upload, sync, reopen and simulation checks. The live build routes the native File → Open to My files and removes Dropbox menu, command-palette and startup import paths. Real mouse and emulated-tap menu tests and a packaged-source check pass. The live update moves My files open/save and the three examples into File, with a tested missing-menu fallback and a path prompt on first save. Desktop mouse, emulated-phone tap and 4K workflows pass, including PNG/SVG exports, sync, cancellation and stale-target checks. The initial PNG approach hit a CSP-blocked data URL fetch and was replaced with local chunked decoding. Public desktop and emulated-phone File-menu workflows passed; remaining upstream dialogs/services and physical touch still need review. |
| Python Notebook / JupyterLite | The live update replaces native discard prompts with desktop dialogs and preserves changes made while confirmation is open. Registered-account desktop, emulated-phone and 4K-sized tests cover cancellation, the edit race, Python example, sync and fresh-session reopen. A public phone-sized account workflow also passed. The live release places My files open/save and Linux Terminal in Jupyter's File menu, with the old toolbar as fallback. Desktop, emulated-phone touch and 4K account tests cover saving, sync, cancellation, reopening and duplicate-command cleanup. The initial phone test exposed an ignored touch; a targeted touch bridge passed the retest. A simulated missing menu preserved the fallback controls on desktop and emulated phone; two simultaneous notebook windows saved independently. A public phone-sized account test also passed. Physical touch and Jupyter upgrade compatibility remain unverified. |
| Grid Tools / Kiri:Moto and mesh:tool | The live release replaces workspace-open, workspace-replace and export-replace native confirmations with desktop dialogs. Desktop and phone-sized Kiri and Mesh account tests cover validation, cancellation, reopen and sync; Kiri also checks a settings edit during confirmation. Desktop, emulated-phone and 4K-sized export tests cover cancellation and a target changed during confirmation. A public phone-sized export collision test passed with a simulated export; native-menu integration remains to be reviewed, and physical touch and broader snapshot fidelity remain unverified. |

Grid Tools moves model and workspace actions into
both native File menus, redirects the native file input to My files, and keeps
the older desktop toolbar as a fallback. Mesh:Tool's About and Kiri:Moto's Help
no longer appear automatically on startup. Desktop, emulated-phone and 4K
account workflows cover menu interaction, model import, workspace save, sync
and reopen; a freshly rebuilt bundle passed the phone-sized workflow, startup
and export collision checks. A public phone-sized workflow passed. Mesh's About
action was invoked programmatically, not by actual touch. Physical touch and
wider format coverage remain unverified.

This list is an initial source audit; continue checking the remaining applications and their
bundled menus rather than assuming the listed set is exhaustive.

| App | Role | Prior evidence / known boundary | New review |
| --- | --- | --- | --- |
| Files | Account and temporary Linux files | Empty guest files created by the shell or browser can be listed and copied to My files; local desktop/phone/4K and live phone-sized tests verify the account copy survives guest reset. Account sync and Linux copy checked; drives are separate. A Move to… folder picker makes single-file moves available without dragging; local desktop, phone-sized and 4K, and live desktop and phone-sized tests cover cancellation, collisions, stale versions, server sync and fresh-session recovery. Copy to… and toolbar Rename provide touch-accessible single-file copy and rename; local desktop, phone and 4K and live desktop/phone-sized workflows cover cancellation, duplicate names, changed sources, sync and fresh-session recovery. Copy to… also copies nested account folders and empty folders as a local transaction followed by per-item server sync; local desktop, emulated-phone and 4K tests and a live emulated-phone test cover the UI, sync and fresh-session recovery, and storage tests cover offline copies, conflicts and account isolation. Simultaneous creation of the same remote folder can combine contents; conflicting files require resolution. ZIP extraction into My files now creates the local tree atomically after checking the source version; local desktop/phone/4K and live phone-sized account tests cover collisions, changed archives, nested folders, sync and recovery. Server sync remains per entry; temporary Linux extraction can remain partial on failure. Folder moves remain unsupported. New / Upload and Sync now are visible on desktop and touch; selected-file Open and explicit conflict recovery are live. Idle background polling is reduced while writes remain immediate. Browser uploads are snapshotted so removing the original computer file does not invalidate the saved copy. Local and live tests cover saving both conflicting edits, deletion conflicts, upload destination changes, Text editing, sync and fresh-context recovery. When the shared gateway limit is reached, subsequent local changes now wait for an automatic retry instead of restarting it; existing-file version checks can be batched. Local tests cover batching and conflicts; live desktop and emulated-phone tests injected two 429 responses and verified recovery. Files no longer claims a server check before its first successful sync, and a manual-sync error clears after automatic recovery; local desktop/phone/4K and live phone-sized tests verify a pending local edit reaches the server after injected limits. Account-scoped issuer admission and bounded combined inventory/version checks are live. Local and live tests verify isolation, same-size direct disk edits, older-gateway fallback, conflicts and retry; a local 100-account one-file fixture completed combined checks with three operations in flight. A bounded gateway queue smooths brief bursts; local 100-account mixed and live four-account parallel checks passed. The gateway still has shared limits, and 100-user end-to-end capacity remains unqualified. | In progress |
| Text | Text and code editor | Files → Text edit, sync, close/reopen and fresh-context recovery checked; new-document naming, folder selection, collision handling, sync and recovery verified live on desktop and phone-sized views. Local and live tests opened, edited and synced an 8 MiB document on desktop and phone-sized views; a local desktop test completed a 127 MiB document; large documents may be slow and memory intensive. A local save that still has a conflict is labeled for resolution rather than claimed to be syncing; Text also rechecks after a save for conflicts that arrived mid-operation. Local desktop/phone/4K and live phone-sized tests cover separate-browser conflicting edits, Files resolution and fresh-session recovery. Search caps stored matches at 50,000, supports next/previous and single replacements beyond the cap, and disables partial replace-all. The chooser supports C/C++ source, headers and `.ino`; C-family syntax highlighting updates immediately on save to a new path. Local desktop/phone/4K and live phone-sized account tests save Arduino example C, open and edit it in Text, sync and reopen, and verify `.ino` highlighting. | In progress |
| Terminal | Temporary v86 Linux | Local desktop, phone-sized and 4K-sized and live desktop and phone-sized checks cover independent shells, nano save/exit, shared guest files, the in-app storage guide and closing one shell while another continues. A local Files test confirms explicit account copy and Linux reset on reload. No automatic account-drive mount; physical touch and more interactive programs remain unverified. | In progress |
| Help | Desktop help | Static beta/support information and temporary Linux explanation; no document workflow. Local desktop, phone-sized and 4K and live desktop/phone-sized tests cover the email link, layout and repeated open/close. Physical touch remains unverified. | Reviewed |
| Calculator | Scientific arithmetic | A touch keypad, typed expressions, angle units and per-window Ans work locally and live on desktop and phone-sized views; local 4K view tested. The keypad supports inverse trigonometry and scientific notation; inverse results respect angle units. Local desktop, phone and 4K, and live desktop and phone-sized tests cover these controls. The evaluator rejects nonfinite intermediate results instead of allowing later operations to hide division by zero or overflow; failed calculations retain Ans. Local desktop/phone/4K and live desktop/phone-sized tests passed. A result is labeled as previous when the expression or angle unit changes; local desktop, phone and 4K and live phone-sized tests cover recalculation, keyboard/keypad edits and independent windows. The current calculation can be saved as a text note with expression, angle unit and result; local desktop/phone/4K and live phone-sized account tests cover stale-result prevention, overwrite cancellation, delayed saves, sync and Text reopen. Calculations use floating-point arithmetic; the note is not a restorable calculator session. Physical touch and advanced numerical methods remain unverified. | In progress |
| Browser | Independent web browser | Experimental; temporary profile and no audio. Scroll fix verified in emulation. Downloads support folder selection and version-checked replacement. Local real-engine clicked-download checks passed at desktop/phone size, including cancellation and concurrent-edit protection; the full interrupted-download regression passed after correcting its viewport. Live phone-sized tests covered clicked download into a subfolder and URL download, both synced to the account service. | In progress |
| Document Editor | Reports | Folder selection, invalid-file draft preservation and fresh-session recovery pass locally and on the live desktop. On the live phone-sized run those checks passed, but fixture cleanup hit a server request limit; test accounts were cleaned separately. Account project and PDF export checked locally; desktop and phone-sized local and live tests cover confirmed/cancelled replacement, stale saves and changing the name or editing during PDF export. Report conflict status stays visible while editing and is rechecked after saving; local desktop/phone/4K and live phone-sized account tests cover conflicts before and during writes, Files resolution and fresh-session recovery. Image insertion is cancelled if the report or insertion point changes during loading; local desktop/phone/4K and live phone-sized account tests cover editing, opening another report, insertion retry, PDF export, sync and fresh-session recovery. Injected image and PDF conflict responses were also checked locally and live at phone size. Not a Word editor. | In progress |
| PDF Viewer | Read-only documents | Open, page navigation, resize and failed-open recovery checked locally and live on desktop and phone-sized views; report preview and PC upload checked locally. Embedded text is selectable and searchable locally; desktop mouse selection, search cancellation and highlights pass locally and live. Search moves through individual matches on each page, including matches across text runs; scanned images need OCR. Local desktop/phone/4K and live desktop/phone tests cover metadata-only checks, persistent change/deletion notices, same-content versions and reopening. Reload checks account sync before opening the current PDF; separate-browser update, failed server check, delayed reload and missing-file recovery pass locally and live on desktop and phone-sized views, with a local 4K-sized check. Overlapping chooser and reload actions are ordered so an older selection cannot replace a newer one; local desktop/phone/4K and live phone-sized tests delay mocked chooser results, and a separate live phone-sized test uses the real picker. No annotations or PDF editing; physical touch remains unverified. | In progress |
| Spreadsheet | Tables | Native save, XLSX import/export, folder selection and invalid-file draft recovery checked locally. UTF-8 CSV can be imported as text into a separate workbook; local and live desktop/phone-sized tests covered edit, save, invalid CSV recovery and fresh-session reopen. One live phone-sized run timed out waiting for sync; a later fresh run passed. SUM, AVERAGE, COUNT, MIN and MAX ignore blanks and nonnumeric labels in referenced ranges; decimal numeric text is included. Local desktop/phone and live phone-sized tests check displayed and exported aggregate values. Current-sheet CSV export saves calculated values to My files in a worker; local desktop/phone and live phone-sized tests cover replacement cancellation, selected-sheet selection, invalid formula rejection and opening in Data Explorer. The live desktop workflow passed; phone-sized checks reached fresh-session recovery but fixture cleanup hit the request limit. Intermediate division by zero, non-real results and overflow now propagate as errors rather than producing misleading finite values; local desktop, phone and 4K and live desktop/phone tests cover display, blocked CSV overwrite, correction and fresh-session recovery. XLSX export captures destination and contents at export start; local desktop/phone/4K and live phone-sized tests cover changes during export, cancel, stale-save protection and sync. Local desktop/phone tests cover account switching during conversion. Native save captures the destination and workbook at the start, confirms replacement of a different file and preserves newer edits; local desktop/phone/4K and live phone-sized tests cover save races, and local desktop/phone tests cover account switches. Workbook conflict status persists while editing and is rechecked after saving; local desktop/phone/4K and live phone-sized account tests cover conflicts before and during writes, Files resolution and fresh-session recovery. PI, ABS, SQRT, SIN, COS and TAN now work in the bounded parser and CSV export, with in-app formula help; trigonometric inputs are radians and results use floating point. Local desktop/phone/4K and live phone-sized account tests cover displayed results, invalid-domain rejection, CSV, sync and fresh-session reopening. CSV and XLSX exports now report conflicts returned during the write and identify newer edits excluded from the snapshot; local desktop/phone/4K and live phone-sized account tests use competing server writes and verify both copies and workbook recovery. The saved-workbook warning is now separate from action status and rechecked after exports; local desktop/phone/4K and live phone-sized tests change the server workbook during CSV export, retain the export result and reopen a saved copy. Open-over-unsaved-work and replacement prompts now use themed desktop dialogs, and the target version is rechecked after confirmation; local desktop, phone and 4K tests cover cancellation, replacement and concurrent file changes during the dialog. On the live site, phone-sized save tests passed cancellation, a target changing during confirmation, stale-write protection and sync; desktop browser testing passed computer upload → Files → Spreadsheet import → My files save → XLSX export and server sync. The disposable test accounts were disabled after their server homes were verified empty. Advanced Excel compatibility limited. | In progress |
| Data Explorer | Data analysis | Desktop and phone-sized tests locally and live, plus local 4K-sized tests, cover CSV upload, SQL, chart, save to My files, cancelled overwrite, new-session recovery and reopening results. Analysis projects now save the source reference/hash, SQL and chart settings; local and live tests cover reopen, stale saves, changed-source confirmation and invalid-project rollback. Saving projects and checking existing CSV results use metadata instead of rereading the source or destination; local desktop/phone tests and a live phone-sized project workflow verified this and stale-source protection. Project and CSV export destinations are captured when saving starts; local desktop/phone/4K and live phone-sized account tests verify changes during preparation and fresh-session recovery. A persistent notice identifies changed, conflicting or unavailable source CSVs while preserving the loaded snapshot; local desktop/phone/4K and live phone-sized account tests cover change, conflict, deletion, reopen and project sync, with local subscription cleanup checked. Editing SQL now marks displayed results as stale and prevents exporting them until the current query runs; changes during an export are labeled. Local desktop/phone/4K and live phone-sized account tests check actual SQL result values, delayed export, sync and project reopening. A labeled synthetic resistor CSV and explained example SQL give a first-use analysis without an upload; local desktop/phone/4K and live phone-sized real-account checks cover collision protection, changes during creation, SQL result, CSV/project sync and fresh-session recovery. CSV input/output supports the 128 MiB file limit, with only >32 MiB locally tested; large-file memory and physical touch remain unverified. | In progress |
| Python Notebook | Browser Python | A runnable measurement-mean example and a collapsible browser-versus-Linux guide are provided. Local desktop, emulated-phone and 4K tests run the example and exercise an intentionally delayed file picker while autosave is due. Local Python/NumPy and same-browser account isolation checked. Save, automatic sync, invalid-file recovery and fresh session passed locally and live on desktop and phone-sized views; local and live settled-kernel desktop and phone-sized tests cover editing while the first save is in flight; local desktop, phone-sized and 4K-sized and live desktop and phone-sized tests cover working-copy cleanup, independent kernels and server copies; local 4K view emulated. A persistent notice reports linked-file changes and conflicts during automatic saves; local desktop/phone/4K and live phone-sized account tests cover conflicts before and during writes, fresh-session recovery and listener cleanup. A live phone-sized close and cleanup passed after removing a redundant iframe navigation that correlated with a renderer hang; intermittent multiple-kernel allocation errors remain unresolved. Untrusted notebooks are not isolated. | In progress |
| Image Editor | Images | Local and live desktop and phone-sized tests cover opening, editing, save, rejected-image recovery and fresh-session recovery. Save As passes local desktop, phone-sized and 4K-sized checks and a live phone-sized check; two accounts in one browser keep separate images, including when a delayed save crosses an account switch, in local desktop/phone/4K and live desktop/phone tests; metadata-only change and Save As collision checks avoid rereading the image; local desktop/phone/4K and live desktop/phone tests verify stale-save protection. A persistent notice reports changed, conflicting or unavailable image files, and saves recheck for conflicts that arrive during a write; local desktop/phone/4K and live phone-sized account tests cover conflict preservation and fresh-session recovery. New blank image creates an unsaved 800 × 600 canvas; local desktop/phone/4K and live phone-sized account tests cover close warning, existing-name protection, resize, save, sync and fresh-session recovery. Animated GIF editing remains unsupported. Physical touch remains unverified. | In progress |
| Audio Editor | Audio | OfflineAudioContext effects block open/replace/save until rendering completes, and starting an unsaved example clears the old window-restore file reference. Local desktop/phone/4K and live phone-sized tests hold a Reverse render, check the saved sample and both restored and unsaved states. Other effects remain unverified. Local and live desktop/phone-sized tests cover upload, sample-checked reverse, invalid-file recovery, close warning, stale-save protection, WAV sync and fresh-session Files open; local 4K-sized test also passed. WAV export offers 16-bit PCM, 24-bit PCM and 32-bit float; local desktop/phone/4K and live desktop/phone tests checked edited samples and fresh-session reopening. An earlier live phone-sized run hit the server request limit during consecutive rapid sync tests; a later run passed after the limit cleared. RIFF/WAVE input preserves its source sample rate when supported; unsupported or unknown rates fall back with a notice. A 32 kHz round trip passed locally and live on desktop and phone-sized views; a forced-fallback test passed locally. Input and WAV output have a 128 MiB cap; a >32 MiB open/save/sync and a separate 128 MiB worker conversion were tested locally. Recording and pending microphone permission now trigger the close warning; closing releases only that window’s streams. Local desktop/phone and live phone-sized simulated-microphone tests cover independent windows, New Recording and delayed permission. A persistent notice reports changes, conflicts or unavailability of the opened source or most recently saved WAV; local desktop/phone/4K and live phone-sized account tests cover source changes, a conflict during export, preserved samples and fresh-session recovery. A local close check verifies listener cleanup. A locally generated one-second 440 Hz tone provides a starting track without upload or microphone; local desktop/phone/4K and live phone-sized account tests cover reverse, WAV sample checks, sync and fresh-session recovery. Memory use, multitrack project saving, physical microphone and physical touch remain limitations. | Partial |
| diagrams.net | Diagrams | Local and live desktop and emulated-phone tests cover opening a document, editing a shape label, rejecting malformed XML without discarding edits, account sync, fresh-session recovery and upload through Files. Save captures its destination and edit revision before requesting XML; a separate notice reports file changes and conflicts. Local desktop/phone/4K and live phone-sized account tests cover delayed export, edits, conflict and fresh-session recovery. Broader touch, format and physical-device tests remain. | In progress |
| Excalidraw | Drawings | Local and live desktop and emulated-phone tests cover drawing a shape, rejecting invalid input without discarding work, account sync, fresh-session recovery and upload through Files. Save captures its destination and drawing snapshot, and a separate notice reports file changes/conflicts; local desktop/phone/4K and live phone-sized tests cover delayed saves, two drawn shapes, conflict and recovery. A unit check detects same-length embedded image data changes. PNG, JPEG and WebP images can be inserted from My files and embedded in the saved drawing; local desktop/phone/4K PNG and desktop JPEG/WebP tests, plus live phone-sized PNG tests, cover upload, invalid image, source deletion and visible fresh-session reopening. Opened drawings are centered to help when screen size changes. PNG export saves a separate snapshot in My files; local desktop/phone/4K and live phone-sized account tests cover changes during export, overwrite cancellation and reopening in Image Editor, plus embedded-image pixels in the PNG. File actions are disabled while an image is being decoded; local desktop/phone/4K and live phone-sized delayed-decoding tests cover concurrent canvas edits, Undo/Redo buttons, save and recovery. Embedded data increases document size and the 128 MiB file limit still applies; broad image variants, keyboard undo in this flow and physical touch remain unverified. | In progress |
| SVG Editor | SVG artwork | Local and live desktop and emulated-phone viewport tests draw a rectangle with pointer input, reject malformed SVG without losing it, sync, recover in a fresh browser session and upload through Files. A save snapshot retains its destination and newer edits, with separate change/conflict notices; local desktop/phone/4K and live phone-sized account tests cover two shapes, conflict and opening the saved SVG in Stitch Converter. Try example creates an editable rectangle-and-circles illustration; local desktop/phone/4K and live phone-sized account tests cover editing, declined replacement, save and fresh-session reopening. Complex SVG and physical-touch behavior remain unverified. | In progress |
| Replicad | Box/cylinder model generator | Supports an optional through-hole with X/Y offsets and displays computed volume and total surface area, including the through-hole wall. Analytical box and cylinder values passed local desktop/phone/4K and live phone-sized checks. Local desktop/phone/4K and live phone-sized account tests check offset hole vertices in box and cylinder STL, boundary validation and project recovery. Local desktop, phone-sized and 4K-sized tests, and live desktop and phone-sized tests, cover preview, legacy project upload/open/save and sync, exported STL dimensions and hole volume, STEP export and close/reopen. Project/model destinations and dimensions are captured at the start; local desktop/phone/4K and live phone-sized tests verify delayed saves, STL dimensions and sync. A separate notice persists for mirror-detected project changes and conflicts; local desktop/phone/4K and live phone-sized real-account tests cover a conflict during save, retaining parameters, saving a copy, measured STL geometry, fresh-session recovery and subscription cleanup. Physical touch, CAD scripting, assemblies and manufacturing validation remain unverified or unavailable. Preview requires WebGL. | Partial |
| Grid tools: Kiri:Moto | 3D printing | A separate notice reports mirror-detected workspace changes, deletion or conflicts; current work remains open. Local desktop/phone/4K and live phone-sized two-session tests cover a change during save, stale-save refusal, save copy, deletion and cleanup. Real model import, slice, export and account sync checked locally and live at desktop and phone-sized viewports. Kiri workspace snapshots now save models and slicing settings to My files and reopen in a fresh session; later edits require another save. Local desktop and fresh phone-sized, plus live desktop and fresh phone-sized tests cover sync, invalid-file recovery, slice and temporary validation cleanup. The shared export bridge captures its destination before waiting and uses metadata for overwrite checks; local desktop/phone/4K and live phone-sized account tests cover real sliced G-code, sync and recovery. Upstream controls and physical touch remain incompletely reviewed; printer profiles and output need independent review. | In progress |
| Grid tools: Mesh:Tool | Mesh editing | A separate notice reports mirror-detected workspace changes, deletion or conflicts; current work remains open. Local desktop/phone/4K and live phone-sized two-session tests cover a change during save, stale-save refusal, save copy, deletion and cleanup. Real model upload, import, union, export, account sync, pending-export close warning and separate-account smoke test checked locally and live at desktop and phone-sized viewports. Explicit workspace snapshots save mesh geometry, groups, sketches and metadata to My files; local desktop, phone and 4K-sized tests and a live desktop-to-phone-sized test cover sync, reopen, invalid project recovery, stale-save protection and temporary validation cleanup. Undo history is not in snapshots. The shared export bridge captures its destination before waiting; local desktop/phone/4K and live phone-sized account tests cover a real STL export, sync and recovery. Same-browser account switching, broad object coverage, physical touch and manufacturing correctness remain unverified. | In progress |
| G-code Preview | G-code viewer | Kiri:Moto heater commands with a T selector and final homing are accepted; homing itself is omitted, and later moves or coordinate resets are rejected. A real Replicad → Kiri → G-code Preview account workflow passed locally at desktop/phone/4K and live at phone size, including server sync and fresh-session reopening. A saved source change, deletion or conflict is reported without replacing the open preview; Reload checks the server first and preserves the previous view on failure. Desktop, emulated-phone and 4K local tests and a live emulated-phone two-session account test cover updates, deletion, failed checks, example and cleanup. Local and live desktop and phone-sized tests cover the example, upload through Files, sync, invalid-file recovery, visible travel toggle, and fresh-session reopening. Primarily interprets 3D-printer G-code; no hardware or safety validation. Parsing now runs in a cancellable worker; a local test completed 100,000 moves and cancelled a larger parse. Drawing still runs on the UI thread and can use substantial memory. Path coloring now handles tested M82/M83 extrusion deltas, retractions, G92 E and independent tools. G90/G91 relative XYZ moves are normalized before rendering; equivalent absolute and relative paths were compared locally for coordinates, layers and rendered pixels at desktop and phone sizes, and a live phone-sized account workflow reopened a relative file. E mode is treated independently via M82/M83. G20/G21 inch/metric changes and G92 XYZ resets are normalized to millimeters; local desktop, phone and 4K-sized and live phone-sized tests compare equivalent paths, including mixed units, extrusion and an XY arc. Unambiguous coordinate-only linear G0/G1 moves are supported after an explicit linear move; local and live worker checks compare normalized coordinates and local desktop/phone/4K account workflows compare the rendered path to explicit moves. A live phone-sized window rendered a shorthand fixture from mocked file bytes. Numbered commands, multiple commands on one line, modal arcs or moves after unrecognized commands, arc-center mode changes, full-circle arcs, coordinate-system selection, non-XY arcs and moves or coordinate resets after a later homing command are rejected. Positive- and negative-radius XY arcs are converted to center offsets so short and long arcs render consistently; invalid, ambiguous and multi-turn arc forms are rejected. I/J arcs whose start and end radii differ by more than the larger of 0.01 mm or 0.1% of starting radius are rejected; local desktop/phone/4K and live phone-sized tests cover rounding tolerance, inconsistent centers and preservation of the previous view. This is a viewer tolerance, not a controller rule. Local desktop/phone/4K and live phone-sized tests compare the rendered long arc with an equivalent center-offset arc and check previous-preview preservation. The worker also rejects overflowing arc geometry and files estimated to exceed 200,000 rendered arc segments before rendering; local desktop/phone/4K and live phone-sized tests cover excessive input and previous-preview preservation. The viewer assumes zero initial position and no stored offsets; controller compatibility and physical touch remain unverified. A full live fixture run hit the existing gateway request limit; a smaller account-file comparison passed. | In progress |
| Arduino Simulator | AVR firmware | A disposable v86 sketch UI now saves source, compiles and runs a minimal sketch, reports errors, cancels, rejects stale builds and reopens source/HEX in isolated real-account tests. This remains research only with incomplete Arduino core/library support and per-window resource limits. A local-only v86 bridge experiment now tests two independent builds, diagnostics, cancellation and temporary-file cleanup; it is not a shipped sketch UI or global resource policy. Local-only v86 research compiled a C example and a minimal Arduino-core C++ sketch with Debian i386 AVR tools, then ran the generated HEX in AVR8js; invalid C++ failed. This is not enabled, a complete sketch toolchain or hardware validation; see AVR_COMPILER_EVALUATION.md. Local and live desktop and phone-sized tests cover Blink, two-way serial echo, bounded input queue, upload, invalid HEX recovery, independent windows, saving, sync and fresh-session Files open; a local 4K-sized test also passed. Echo firmware save and fresh-session reopen passed locally and live at phone size. The visible serial output can be saved as text to My files; local desktop/phone and live phone-sized tests cover Unicode echo, replacement cancellation, output arriving during save, sync and reopening in Text. The monitor keeps a bounded tail, not a full raw log. Two browser-local AVR compiler candidates produced firmware that drove the existing simulator in isolated research; a local hash-checked candidate patch catches observed compiler errors, repairs a missing core header and reports the sketch source line. The candidate now checks numeric compiler/assembler/linker exit status and a packed-input worker was exercised through the generic app builder and restricted local desktop CSP; an isolated sketch UI also passed a real account sync, fresh phone-sized session reopen, close-warning and separate-account test. This remains research only; distribution/source review, broader exit testing, production integration and a v86 comparison remain outstanding (see AVR_COMPILER_EVALUATION.md). The research editor now preserves saved snapshots across document changes and account switches; isolated real-account desktop/phone/4K tests cover delayed saves and conflicting files, and the real compile/simulate workflow was rerun. The compiler is not live; source provenance and distribution review remain open. A driven D2 digital input and a compiled example let a student control D13; the example C source can be saved to My files. Local desktop/phone/4K and live phone-sized account tests cover D2, independent windows, stop/restart, source and HEX sync, fresh-session reopen and serial echo. This is logical input only, without electrical wiring or analog modeling. Firmware saves now capture image, destination and prior version before waiting; local desktop, emulated-phone and 4K and live phone-sized account tests cover changing the filename, loading another image or reloading the same example during save, synchronization and reopened D2 operation. Other peripherals, hardware validation and physical touch remain outstanding. All three bundled examples can save their matching C source to My files; local desktop/phone/4K and live phone-sized tests cover a delayed source save, firmware changes, serial/D2 execution and Text reopen. Source and serial-save conflict responses were injected in separate local/live phone-sized checks. Compilation remains unavailable. | In progress |
| Pico Simulator | RP2040 firmware | Serial saves report immediate conflicts and watch the saved log for later mirror-detected conflicts or changes. Run Blink clears the previous project layout association. Local desktop/phone/4K and live phone-sized tests cover a real two-session log conflict using simulated serial output and project layout, with a separate real Blink worker test. Local account test used real MicroPython to check ROM/UF2 in either order, serial commands and controls, flash persistence, invalid projects, competing saves, close warning and fresh phone-sized Files reopen. Serial buffer admission has a unit test. Live desktop/phone-sized Blink checks passed without uploading a private ROM; local 4K Blink tested. The app orders competing opens of the same type while allowing ROM and UF2 to load together, and uses metadata for overwrite checks; local desktop/phone/4K account tests use synthetic firmware and a fake worker. A real MicroPython account workflow and fresh phone-sized session recovery passed locally after a first test exposed and prompted correction of overly broad cancellation. The update is live; a public phone-sized Blink regression passed. Serial output can be saved as text in My files; local desktop/phone/4K and live phone-sized account tests inject worker output to cover snapshot timing, trimming, overwrite cancellation, sync, Text reopen and worker cleanup. A separate live phone-sized test ran the real Blink worker. The saved text is a bounded visible tail, not a raw log. Project destinations are captured before flash snapshots; a separate notice reports changed or conflicting saved projects. Local desktop/phone/4K and live phone-sized tests cover delayed snapshots and conflicts with synthetic firmware and a fake worker; separate local/live real Blink checks passed. SSI, firmware compatibility and physical touch remain partial. | In progress |
| Digital Logic | Gates | Separate persistent notices now report changes and conflicts in the circuit and the last saved truth-table CSV; loading a new example clears the old layout reference. Local desktop/phone/4K and live phone-sized two-session tests cover a real CSV conflict, retained table, circuit reopening and listener cleanup; immediate conflict results were injected. Seven selectable gate examples plus half-adder, full-adder, 2-to-1 multiplexer and 2-bit ripple-carry adder examples and a generated truth-table view for small one-bit combinational circuits passed local desktop and phone-sized checks, including interactive switches, undefined signals and cancellation. The half-adder was saved, synced, reopened and truth-table checked in a live phone-sized account workflow. The 2-bit adder truth table and interactive outputs match all 16 combinations in local desktop/phone/4K and live phone-sized account tests, including CSV and project sync and fresh-session reopening. A 2-bit magnitude comparator exposes greater/equal/less outputs; all 16 combinations in both the interactive diagram and truth table, CSV and project sync, and fresh-session reopening passed local desktop/phone/4K and live phone-sized account tests. The full-adder truth table and interactive outputs match all eight combinations locally; local desktop, phone-sized and 4K, and live desktop and phone-sized tests cover saving, sync, CSV and fresh-session recovery. Truth tables can be saved as CSV to My files; local and live phone-sized account tests opened the synced result in Data Explorer. Local tests cover CSV escaping, overwrite cancellation and changes during save. The live desktop account workflow reopened a saved circuit and calculated its table; the phone-sized workflow reached cleanup after those checks but hit the shared gateway limit; local desktop, phone-sized and 4K-sized checks and live desktop and phone-sized workflows cover upload, saving, sync and fresh-session recovery. A live phone-sized run hit a shared gateway rate limit during the final example sync; a later retry passed. Saved-circuit watch and overwrite checks use metadata; local desktop/phone/4K and live phone-sized account tests cover sync and stale-save protection. Saves capture the circuit and destination at the same time; local desktop/phone/4K and live phone-sized account tests cover changes while storage is delayed. JSON netlists only; no feedback, sequential devices or full schematic editor. Physical touch remains unverified. | In progress |
| Circuit Simulator | CircuitJS | Voltage divider, RC filter and half-wave rectifier examples; local desktop, phone-sized and 4K-sized and live desktop/phone-sized tests cover examples, changing output, save/sync, scope-change warnings and fresh-session reopen. Existing local account tests cover upload, bad-file recovery, close warning and disposal. A later live phone test hit the shared 429 limit during cleanup after its workflow checks. Save captures the circuit and destination before waiting; a separate warning keeps changed, conflicting or unavailable saved files visible while the current simulation continues. Local desktop/phone/4K and live phone-sized account tests cover save races, conflicts, copy and reopen with simulated output; detection depends on mirror sync. Running state is excluded from design comparisons; scope checks are conservative. Not ngspice or hardware validation; physical touch and broader formats remain unverified. | In progress |
| Electronics Design | Electronics editor | Direct My files save and native Ctrl+S capture the project; unsaved work, stale versions, invalid input and edits during save are guarded. Registered-account desktop and emulated-phone workflows pass locally, including a 9 MiB project. On the live site the complete workflow reached cleanup, where rapid requests hit the gateway limit; the test account was removed separately. Exports are saved separately. Standalone part import from My files passed registered-account local and live desktop and emulated-phone tests; a local desktop browser test placed an imported part, saved its definition with the design, and reopened it. Unused imported parts remain temporary. Optional three-view layout uses one shared design on sufficiently large windows; local 4K-sized tests cover pane selection, schematic edits, deletion and undo across views, saving and width/height fallback. A live 4K-sized account test covered schematic edit, sync, narrow resize and fresh phone-sized reopen. A persistent project notice reports mirror-detected changes, conflicts and unavailable files; local desktop/phone/4K and live phone-sized account tests cover change, conflict during save, metadata-only checks and fresh-session recovery. Physical touch, broad component/simulation coverage and production-board validation remain outstanding. | In progress |
| Embroidery Studio | Stitch design | Local and live desktop and phone-sized tests cover one-step project save, overwrite cancellation, invalid-project recovery, machine export, upload, sync and fresh-session Files reopen. Project change/conflict notices remain visible and save destinations are captured at action start; local desktop/phone/4K and live phone-sized account tests cover conflict, project save, DST export and fresh-session recovery. The editor is pre-release; native touch controls and physical sewing remain unverified. | In progress |
| Stitch Converter | Stitch formats | Local and live desktop and phone-sized tests cover editable SVG save, PES export, size-change preview invalidation, bad-file recovery, upload, sync and fresh-session Files open. Malformed SVG and machine files preserve the current artwork and preview; valid SVG that cannot produce stitches remains editable with an explanation. Local desktop/phone/4K and live phone-sized tests cover both SVG names, empty SVG, upload, sync and reopening. Artwork and machine saves capture their destination and format before waiting, preserve later edits, and do not attach an older save to a new example; local desktop/phone/4K and live phone-sized tests cover delayed saves and the unsaved-work warning. A persistent notice now reports mirror-detected artwork changes or conflicts; overwrite checks use metadata and both export types identify immediate conflicts. Local desktop/phone/4K and live emulated-phone account tests cover changed files, a write conflict, saving a copy, PES export and fresh-session reopening. Other format compatibility, physical touch and sewing remain unverified. | In progress |
| Falling Blocks | Single-player game in development | Rules and exact snapshot unit-tested; a Phaser prototype with help, next-piece preview and outcome messages passed isolated two-window play/save/load/disposal checks using mock storage at desktop, 4K and emulated phone sizes, including keyboard, emulated touch input, board resizing and rendered high-contrast outlines. The initial piece is visible and save-location controls are collapsed by default. A local desktop test verifies minimization pauses the game; the rules test covers lock delay when leaving a ledge. Real local account-file sync, fresh-session recovery, account isolation, close warning and same-browser save conflict checked; separate browser contexts also preserve both copies and show a conflict after a simulated gateway outage. Original Rive coach now runs locally in independent game windows; browser tests cover game-state colors, a line-clear reaction, local-only assets and disposal. Reduced motion follows the device setting and has a browser-tested per-window override. Full interface, real cross-device operation and physical-device tests remain. Live as a preview; a disposable live account passed menu launch, save and fresh phone-sized session recovery. Local desktop, emulated-phone and 4K and live emulated-phone tests also cover changing the filename, continuing play or starting a new game while a save is delayed; the captured game goes to its original destination and later progress stays unsaved. Files now routes recognized Falling Blocks saves back to the game; unknown game formats fall back to Text. Local desktop/phone/4K and live phone-sized account tests cover exact paused-state restoration, sync and fresh-session reopening. Physical-phone tests remain. | In progress |
| Personal template | Per-user app example | Template, not a completed end-user tool. | Pending |
| CodeMirror | Shared editor capability | Used by apps; no standalone file workflow. | Pending consumer review |
| FFmpeg | Shared media capability | Programmatic conversion checked. | Pending consumer review |
| WaveSurfer | Shared waveform capability | Programmatic rendering checked. | Pending consumer review |
| Tone | Shared music capability | Programmatic synthesis checked. | Pending consumer review |
| ZIP | Shared archive capability | Files archive workflow checked. | Pending consumer review |
| Mermaid | Shared diagram capability | Programmatic capability. | Pending consumer review |
| ECharts | Shared chart capability | Programmatic capability. | Pending consumer review |
| Plotly | Shared chart capability | Programmatic capability. | Pending consumer review |
| pdfme | Shared PDF capability | Programmatic capability. | Pending consumer review |
| MapLibre | Shared map capability | Programmatic capability. | Pending consumer review |
| Transformers | Shared model capability | No model configured. | Pending consumer review |
| ONNX Runtime Web | Shared model capability | Separate CPU/WASM runtime; small local inference tested, no app integrated. | Pending consumer review |
| Trystero | Shared networking capability | Lazy library only; no signaling or app integration configured. | Pending consumer review |
| TanStack Virtual | Shared list/grid capability | Lazy framework-independent core; no app integrated. | Pending consumer review |
| WebTorrent | Shared peer transfer capability | Lazy browser library only; no tracker, transfers or app integration configured. | Pending consumer review |
| Yjs | Shared state capability | Lazy library only; no synchronization provider, persistence or app integration configured. | Pending consumer review |

New apps open full screen on phones and in alternating half-width, full-height tiles on desktop. Local and live viewport-emulation checks cover 1080p, 4K, maximization, resize, manual movement and phone/desktop transitions. Physical F11 and device behavior remain to be checked. Electronics Design provides an optional shared-document three-view layout in sufficiently wide and tall windows; individual tool behavior and physical monitors remain to be verified.

During each app review, suppress optional third-party account and sign-up prompts where the local feature can work without them. The desktop account does not automatically grant access to an external provider; label any feature that genuinely needs one. Defer AI and other features that depend on removed account services for later integration; preserve working local features.

Deferred third-party service and AI features are tracked in `DEFERRED_APP_FEATURES.md`; those features are not implied to work through the desktop account.

Historical review notes below describe earlier candidates; later live releases and
tests in this document supersede their deployment status.

The desktop-wide unsaved-window close warning has a locally tested themed dialog candidate. It is not live, and app-specific browser prompts for file names, replacing work and other actions still need migration. Desktop, emulated-phone and 4K tests cover an edited Text document, cancel, Escape and discard; physical touch is not yet verified.
Text's open/reload unsaved-change prompts also use a shared themed confirmation service in a local candidate. Desktop, emulated-phone and 4K registered-account tests cover both outcomes and abort cleanup. It is not live; other apps and prompt types remain to migrate.
Files' naming and confirmation prompts have a local desktop-dialog candidate. New file/folder, cancellation, rename, account sync and abort cleanup passed desktop, emulated-phone and 4K account tests. Copy, ZIP, delete and conflict actions need targeted regression checks before deployment; no live change yet.
Follow-up local account regressions for Files' new dialogs passed copy, ZIP extraction and real two-session conflict resolution at desktop, emulated-phone and 4K sizes. Create ZIP, delete, guest copy and physical touch still need direct testing; the candidate remains undeployed.
Additional local Files checks cover ZIP creation and cancel/confirm deletion with server sync at desktop, emulated-phone and 4K sizes, plus copying an empty guest file to My files across a Linux reset at desktop and emulated-phone sizes. The delete test used simulated right-click, not physical touch. These dialogs are not yet live.
Files also has a local touch-friendly Delete toolbar action. A registered-account phone-sized test uses emulated taps to select and delete, verifies cancellation and server sync, and checks the button is disabled without selection; desktop and 4K-sized tests passed too. Not yet live or verified on a physical phone.
The shared themed close confirmation, Text open/reload confirmations, Files naming/confirmation dialogs and Files Delete toolbar are live. A live emulated-phone registered-account smoke test covered Text cancellation/close and Files deletion cancellation; fuller Files actions were checked locally at desktop, phone-sized and 4K views. Other applications still use native browser prompts and remain to migrate; physical touch remains unverified.
Document Editor's link, open-over-unsaved-work, document replacement and PDF replacement dialogs have a local themed candidate. Desktop, emulated-phone and 4K workflow tests and desktop/phone open-safety regressions passed; the shared status line can still replace an earlier export message. Not yet live or verified on a physical device.
Document Editor's themed dialogs and separate file-change warning are live. Live emulated-phone account tests covered links, PDF overwrite cancel/confirm, failed-open recovery, a warning alongside the export result and fresh-session recovery. Physical touch and other apps' native prompts remain outstanding.
