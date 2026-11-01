# Simplified branch handoff

## 2026-11-01 — Right-side desktop rail

Live static release `be9d65aec30f72d97f96d4411216f2e61eedd1576975607fc6debdec54d63bdd` moves the desktop panel to the right, places the account at the top and Applications at the bottom, uses a charcoal background and clean blue X icons, and sizes windows and popups around the rail. Local desktop/phone/4K and live desktop/phone-sized shell tests passed; a separate live phone-sized real v86 test exercised two independent shells and nano. Physical touch and real F11 remain unverified. Image Editor also fixes confirmed replacement of an existing same-name blank image; local desktop/phone and live phone-sized tests passed cancellation, changed-target refusal, replacement and sync. Four live test accounts were disabled with data retained. Staging preserved two pre-existing live stylesheet differences in window-control styling and pins both the old app and stylesheet hashes. Hosting manifest SHA-256 `7f2e228eaae10cc32d5b0d642fe95fb0c0d8ebfeb1ad355bb0538ecf89419c83`; rollback inputs `/var/backups/webhost-sites/change-20261101T083305320911Z` and `/var/backups/webhost-sites/change-20261101T083305321751Z`.

## 2026-11-01 — Data Explorer uncertain-view recovery

Live static release `7f6f28530d456219e37404966e5b5b15b93ff6d7e3e650f33af353c28a35a0a5` requires reopening the source if opening data and restoring the previous view both fail. Local desktop/phone and live phone-sized account tests inject both failures and check warnings, blocked query/export, reopening and sync. The existing query-restore regression reports Perspective `_setThrew is not defined` on unchanged baseline and candidate; it remains failing. Physical touch remains unverified. One live test account was disabled with data retained. Hosting manifest SHA-256 `fb0e1dfa352761feaf9a529d844bad77e2b6e90e5678ac847a0054484c46ddb8`; rollback inputs `/var/backups/webhost-sites/change-20261101T082233755455Z` and `/var/backups/webhost-sites/change-20261101T082233756235Z`.

## 2026-11-01 — Multi-file copy and SVG recovery

Live static release `75b49fea6129f2e90bc4164d316edc98d8edd8acbd2d536f0d8453af5f3d7e14` adds multi-file Copy to and guards SVG Editor when both an open and rollback fail. Local desktop/phone and live emulated-phone account tests cover sync, preserving originals and injected partial-copy or double-load failure. Copies are separate operations and report partial completion; folders copy one at a time. Physical touch and other upstream failure modes are unverified. Two live test accounts were disabled with data retained. Hosting manifest SHA-256 `0daea9e9ce6142117a560ec4caa500ef0aa308da40c26855bb60d7233d7429ce`; rollback inputs `/var/backups/webhost-sites/change-20261101T081952144947Z` and `/var/backups/webhost-sites/change-20261101T081952150806Z`.

Folder-move research is separately backed up at `research/folder-lock-20261101` commit `dd65e86b0fc45f466bdcf819964f3d140bef915c`. The isolated journal tests stable retry and externally verified receipt settlement against the Python server primitive; signed transport, authentication, production integration, direct host writers and UI remain unfinished.

## 2026-11-01 — PDF render and startup recovery

Live static release `478b750fbd2254d10026f273bf9ada9c4b5e0169b8a7a0e4ff699aa121d903d2` clears a failed initial PDF reference and stages page rendering before replacing the visible page or previous document. Failed search-result rendering clears the false match notice and allows retry. Local desktop/phone and live phone-sized account tests cover injected rendering failures, startup fallback, preservation and retry. One parallel oversized-open regression failed and a sequential rerun passed; the cause is unverified. Physical touch and other failure modes remain unverified. Three live test accounts were disabled with data retained. Hosting manifest SHA-256 `a926d148c169527d4b91129784f5547fa75cd9cece845d7de4b4368b43ceb879`; rollback inputs `/var/backups/webhost-sites/change-20261101T081532833082Z` and `/var/backups/webhost-sites/change-20261101T081532833531Z`.

## 2026-11-01 — Diagram restore references

Live static release `904a286a95f706e66977edb1f7d0f8d73d317627ef3fd2df936b0955dab62891` updates diagrams.net’s restore reference after open or Save As, and clears it if the initial file fails. Local desktop/phone and live emulated-phone account tests passed switching, save/sync and refresh; invalid fallback passed live and missing fallback passed locally. Physical touch remains unverified. Two live test accounts were disabled with data retained. Hosting manifest SHA-256 `70058cc6d42691584bc4ee127fe714743ab45a163e3573345018cdd36c62581b`; rollback inputs `/var/backups/webhost-sites/change-20261101T081051227955Z` and `/var/backups/webhost-sites/change-20261101T081051293963Z`.

Folder-move research is backed up separately on `research/folder-lock-20261101` at `facbde0b7df29abe2a58289bdf275a32871492e5`. Its isolated browser journal passes fake IndexedDB and Chrome two-tab/reload checks. It is not integrated with production storage; receipt reconciliation, direct host writers, server route and UI remain unfinished.

## 2026-11-01 — Circuit, stitch and Text recovery

Live static release `a5636f2d1035ba802339d82f383ec9362e5eaacd59605803e444411f159e68fc` clears failed initial-file references in Circuit Simulator and Stitch Converter, and orders Text file-status checks so a stale failure cannot replace a newer result. Local desktop/phone and live emulated-phone account tests passed save, sync and recovery; Text timing was injected. Physical touch, electronics hardware and sewing compatibility are unverified. Three live test accounts were disabled with data retained. Hosting manifest SHA-256 `a14dd73b18cf1afea169b260c9fbdba05f3922cb8728eba863b9b69186a54978`; rollback inputs `/var/backups/webhost-sites/change-20261101T080504438623Z` and `/var/backups/webhost-sites/change-20261101T080504439507Z`.

Folder-move source-only research is backed up on `research/folder-lock-20261101` at `d4a6a092d357ffded79a2998958cbca9493d0632`. Browser and server canonical manifests now match for tested Unicode paths; browser journaling, recovery, route and direct-host-writer consistency remain unfinished. Folder moves are not enabled. Three unused generated app bundles (`browser-app-build-check`, `simplified-apps-blocked-r1`, `circuit-audit-app`) were removed after checking their manifests and active process arguments, recovering roughly 1 GB; source and account data were not removed.

## 2026-11-01 — Multiple file moves and app recovery

Live static release `8f2c44d28c626a87faf97c77933dec6f9b7d3321523a11c6232942fbb5aef542` adds multi-file Move to, prevents stale Data Explorer picker results, and corrects Embroidery Studio restore references. Local desktop/phone and live emulated-phone account tests passed; file moves are individual and report partial completion on failure, while folder moves remain unavailable. The chooser-order test injects delayed results. Physical touch and embroidery machine compatibility are unverified. Three live test accounts were disabled with data retained. Hosting manifest SHA-256 `908c2ad779a7272383dbc37138be0bd3033c36fc424aa5e33e8c52011b070c27`; rollback inputs `/var/backups/webhost-sites/change-20261101T080122276174Z` and `/var/backups/webhost-sites/change-20261101T080122277028Z`.

## 2026-11-01 — Notebook kernel race

Live static release `98d92d5a71d74e7db9b210ff76ee60370f4ae027383cb0696245420fe7dcdd9c` patches a pinned JupyterLite Pyodide proxy to handle synchronous and asynchronous `Atomics.waitAsync` values. A deterministic test reproduces the previous synchronous-result error. Local desktop/phone and live phone-sized tests ran independent concurrent kernels and verified the surviving window after close. Before the patch, two of three bounded simultaneous runs timed out, one with the matching exception. This does not establish that all kernel failures share that cause; physical devices and resource pressure remain unverified. One live test account was disabled with data retained. Hosting manifest SHA-256 `1ab50546693b0a9902d1bdf13e1706d4b48678f87bde83030aec6329e6193b53`; rollback inputs `/var/backups/webhost-sites/change-20261101T075735864739Z` and `/var/backups/webhost-sites/change-20261101T075735865402Z`.

A separate source-only folder-lock candidate is on box-git branch `research/folder-lock-20261101` at `65018616e95277df39c2fba1ca4bbf41eda13d54`. It permits another account’s reads during a held folder hash while existing writes still wait. It is not deployed; folder moves and their browser recovery protocol are unavailable and direct host writers remain outside the lock.

## 2026-11-01 — Analysis and workspace recovery

Live static release `0d4b09d5bf2b8816cfa55b83102ab3be9f7ff677f9a04273b33472e35927aef6` clears failed initial-file references in Data Explorer, Kiri:Moto and Mesh:Tool. Local desktop/phone and live emulated-phone account tests passed invalid-file recovery, saving, server sync and refresh; the two grid tools used real model import. Local phone missing-file fallback passed; one earlier Kiri missing-file full workflow timed out after fallback, cause unverified. Manufacturing correctness and physical touch remain unverified. Three live test accounts were disabled with data retained. Hosting manifest SHA-256 `88fcfcdd16e280487f0d2fc4a7d88260b6ba4a084953a1ff62a8a5722ffa82bf`; rollback inputs `/var/backups/webhost-sites/change-20261101T075316059639Z` and `/var/backups/webhost-sites/change-20261101T075316060425Z`.

## 2026-11-01 — Audio beat settings and image recovery

Live static release `463ea092b4f9923c2f933d97d7ea12dd897564fd2a0ea4874ad3ae1068e375b2` preserves beat/snap enabled state in a desktop metadata record and clears Image Editor’s failed initial image association. Local desktop/phone and live emulated-phone tests passed; native AudioMass accepts the additional record, but other tools may discard it. Old projects without the record still open; long names may be shortened. Physical touch and audio hardware remain unverified. The folder-move prototype remains unavailable: a deterministic local test shows its global lock blocks another account during a held manifest calculation, and sync/recovery and direct-host-writer consistency remain unfinished. All 18 server-only prototype tests passed. Two live test accounts were disabled with data retained. Hosting manifest SHA-256 `6fd217340f49d956fccf7f0b66a733c0389fd68318e3005455c8be589b6e8993`; rollback inputs `/var/backups/webhost-sites/change-20261101T074810913239Z` and `/var/backups/webhost-sites/change-20261101T074810914079Z`.

## 2026-11-01 — SVG and Pico restore references

Live static release `95c87a6d38931fc7233fca62ba35c952efed09ce08b497f4b1919b856d8a1d33` clears SVG Editor’s failed initial file association and updates Pico Simulator’s association when switching or saving projects. Local desktop/phone and live emulated-phone account tests passed; Pico project checks used synthetic ROM/flash and a fake worker, while a separate local real Blink worker test passed. Real firmware project recovery, physical touch and hardware remain unverified. Notebook lifecycle passed local desktop/phone runs after its test began accepting the desktop discard dialog; prior intermittent kernel-allocation failures remain unresolved. The earlier Spreadsheet open-safety test passed desktop/phone with Data Explorer present. Two live test accounts were disabled with data retained. Hosting manifest SHA-256 `32bf81a45eceb030f4a255e55efeea81b95aae34fbf8008a14711fbeebca3476`; rollback inputs `/var/backups/webhost-sites/change-20261101T074512302563Z` and `/var/backups/webhost-sites/change-20261101T074512303276Z`.

## 2026-11-01 — Active cell and simulator recovery

Live static release `6d91f437fecae8a12c9be3a55191012d42ecbe689db9c17b231fdad24d2a6766` marks active Spreadsheet cell edits unsaved, clears stale failed Arduino firmware restore references, and marks Audio Editor beat-control changes unsaved. Local desktop/phone and live emulated-phone account tests passed focused close, save, sync and recovery workflows; Audio tempo survives project reload but beat/snap enabled state does not. A broader Spreadsheet open-safety regression was stopped after two minutes without output in a bundle without Data Explorer, so that test is unverified. Physical touch and hardware remain unverified. Three live test accounts were disabled with data retained. Hosting manifest SHA-256 `726af12efcd74eab166632c2cf410241163418c0e2e2c92f9b5d49aa6f6f68f8`; rollback inputs `/var/backups/webhost-sites/change-20261101T074011977329Z` and `/var/backups/webhost-sites/change-20261101T074011978167Z`.

## 2026-11-01 — Editable MultiTrack audio projects

Live static release `0124ca7eb4edf1f626e583e60eb6dee766c3c814f2b5c3f1a622a8d0941f625d` adds editable AudioMass `.amss` projects in My files, including Files routing and checked, rollback-capable project loading. Desktop and emulated-phone local tests and a live emulated-phone two-account test cover real audio/timing/mixer round trips, server sync, separate accounts, pending actions, malformed files, conflicts and injected failures. Upstream format omits beat/snap state and may shorten long names; the save dialog discloses both. Failed rollback or uncertain undo clearing warns and marks unsaved; decoding can use substantially more memory than file size. Physical touch and audio hardware are unverified. Two live test accounts were disabled with data retained. Hosting manifest SHA-256 `20e5f0de8ecfd74f2a4cc1f7fe16a82e9053f6323c31839fb6515da9836f1083`; rollback inputs `/var/backups/webhost-sites/change-20261101T073530650712Z` and `/var/backups/webhost-sites/change-20261101T073530651177Z`.

## 2026-11-01 — PDF and Digital Logic recovery

Live static release `babaddc475c9cfc385015311e108b7f94ddce4beadb0347a228bc05ba788f734` keeps PDF page controls on the visible page if a later page exceeds the rendering limit, and clears Digital Logic’s stale restored-file association when the initial circuit cannot open. Local desktop/phone and live emulated-phone account tests passed; a missing-file Digital Logic case passed locally. Other rendering failures, physical touch and hardware remain unverified. Two live test accounts were disabled with data retained. Hosting manifest SHA-256 `20240b9b317fb279a456fb9051deb6d1742f186e5a73a41ff659d734427e7d7c`; rollback inputs `/var/backups/webhost-sites/change-20261101T073012102649Z` and `/var/backups/webhost-sites/change-20261101T073012108591Z`.

## 2026-11-01 — Calculator note reopening

Live static release `d8f1c1166b62055088567fe4cef6d42ae697faf41c8d4a0a9f3222e0f9eb62cd` adds reopening of saved Calculator notes from My files. Local desktop/phone and live phone-sized account tests passed synchronization, fresh-session recovery, separate-account isolation, cancellation, invalid notes, and edits while choosing a file. The restored result is recorded, not recalculated; prior Ans history is not saved. Physical touch remains unverified. Two live test accounts were disabled with their data retained. Hosting manifest SHA-256 `8632a5f37e3d60ec285b959a4702fcdc556f9364403c083eeb661cc7bfc0efa4`; rollback inputs `/var/backups/webhost-sites/change-20261101T072637165660Z` and `/var/backups/webhost-sites/change-20261101T072637166386Z`.

## 2026-11-01 — Audio mixdown and CAD project recovery

Live static release `25975f80bb9e3dace021b6e253535e20355336314078c810d4f28e9451224108` adds a MultiTrack stereo WAV export to My files and fixes Replicad restoring an old project after opening or saving another. Local desktop and emulated-phone tests and live emulated-phone account tests passed; audio checks include rendered samples, clip overlap, mute, failures, sync and the 128 MiB output limit. CAD checks include project switch, preview, sync and refresh; broader local checks include STL/STEP. The editable audio session is not saved by WAV export; rendering may need substantially more RAM than the output size. Physical touch, real audio hardware and fabrication accuracy were not verified. Two live test accounts were disabled with their data retained. Hosting manifest SHA-256 `69550afd0c5cb8a2c1c0b4324708e2aaa895a443b9a42b3a7bde67a516bcce06`; rollback inputs `/var/backups/webhost-sites/change-20261101T072202097623Z` and `/var/backups/webhost-sites/change-20261101T072202099162Z`.

## 2026-11-01 — Stitch and Pico save/import safety

Live static release `c07254868618fd4a63983327a566356137fbdaf4462f2d89462b4ea467b8d052`
guards Stitch Converter artwork and machine-file saves against closure and
checks Pico UF2 numbered-block completeness when totals are declared. Live
phone-sized account tests passed with PES output, synthetic incomplete UF2 and
the real Blink worker. Zero-count UF2 files remain supported without a
completeness claim; physical touch and hardware remain unverified. Two test
accounts were disabled with data retained. Asset hashes and root, /desktop/ and
/blog/ checks passed. Source through `e7eebdab8` is on box-git. Hosting manifest
SHA-256 is `c05d78a68fbdffc293c85f555a29d3e6b967434b6abd798a2621b50de9a742af`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T060746511264Z`
and `/var/backups/webhost-sites/change-20261101T060746511679Z`.

## 2026-11-01 — Text save and Arduino composition

Live static release `838f71673dad6a6e3aa8b845a5b662cf3292f12fb386edc82bcf08acd972cb61`
guards Text while a save is pending and prevents Arduino serial Enter from
sending during IME composition. Live phone-sized account checks passed, using
synthetic composition events and real AVR serial echo. Physical touch and
physical IME behavior remain unverified. Two test accounts were disabled with
data retained. Asset hashes and root, /desktop/ and /blog/ checks passed. Source
`603965be6` is on box-git. Hosting manifest SHA-256 is
`9c9d33df6368257f0d2d724b213cfbb73079a9c4962de750c62459074aaaf55d`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T060422951302Z`
and `/var/backups/webhost-sites/change-20261101T060422951737Z`.

## 2026-11-01 — Additional generated release cleanup

Removed 15 obsolete generated static releases from this test sequence:
`fb76b9b0`, `1d6c24ec`, `7a87f1fd`, `0c8399c9`, `7afbf8fe`, `14d8c051`,
`1c8412af`, `29708dab`, `9f5f22f4`, `296d2211`, `230b64da`, `c6581dc5`,
`c3a2996a`, `43f517bf`, and `42f2fe05`. Under the hosting lock, each full ID
was checked against the active manifest and Caddy configuration; each release’s
manifest ID and exact file inventory were checked before deletion. Current
release `025b34a6` and two recent rollback releases `eb3fae98` and `72fe5ec7`
were retained. Server free space rose from approximately 36 GB to 48 GB.
Earlier rollback notes pointing to removed releases are historical and require
rebuilding those releases from source. Account data was not touched.

## 2026-11-01 — Program-end and pending-save protection

Live static release `025b34a6c390c8f540a5b911cffa4825e2e6c8da335d6e5865e81755184748be`
rejects motion after ambiguous M2/M30 program-end commands and guards Document
Editor and Excalidraw while saves or exports are pending. Live phone-sized
account checks passed; physical touch, accepting close during an already-
dispatched write and machine safety remain unverified. Three test accounts were
disabled with data retained. Asset hashes and root, /desktop/ and /blog/ checks
passed. Source through `8fd1c356d` is on box-git. Hosting manifest SHA-256 is
`7183e6033d559293a4173fe739b33f3a177de3c2f009cda72c682ca0771ab3d2`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T060110160190Z`
and `/var/backups/webhost-sites/change-20261101T060110161006Z`.

## 2026-11-01 — Generated release cleanup

Removed eight obsolete generated static releases created during these test
updates: `34be5d79`, `f4bc797d`, `e0117b30`, `e9949ff9`, `11431c97`,
`a7b37d4e`, `e1e1cc7b`, and `4cfea5fb`. Under the hosting lock, each full ID
was checked against the active manifest and Caddy configuration; each release’s
manifest ID and exact file inventory were checked before deletion. Current
release `eb3fae98` and its immediate rollback `72fe5ec7` were retained. Server
free space rose from approximately 29 GB to 36 GB. Earlier rollback notes that
point to the removed releases are historical and would require rebuilding those
releases from source; account data was not touched.

## 2026-11-01 — Data Explorer single-statement check

Live static release `eb3fae98f8ae96b87c19d57539cb207209127845b50426cb057fb024eb21b788`
rejects the tested multi-statement SELECT injection and uses a DuckDB prepared
statement for result-table creation. A live phone-sized account test checked
that the in-browser rows remain intact and tested legitimate quoted/commented
semicolons. This is not a general SQL security sandbox. The test account was
disabled with data retained. Asset hash and root, /desktop/ and /blog/ checks
passed. Source `665b28eda` is on box-git. Hosting manifest SHA-256 is
`6edc329e7514adb925d48d7c15b54de3531d254fa7826dcb50da34d2312ab76a`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T055632322847Z`
and `/var/backups/webhost-sites/change-20261101T055632323279Z`.

## 2026-11-01 — Embroidery pending-save guard

Live static release `72fe5ec7a17fadfc70c5c6a919c14ae19f668c7623ab0cff952de5c449d7750d`
guards a project save before account metadata checks. A live phone-sized
account test held the check and verified that cancelling close preserves the
window; physical touch and sewing remain unverified. The test account was
disabled with data retained. The shipped corresponding-source archive SHA-256
is `bc742f7ab0c8ebd17c6cb2fe7527fe8cca492c9a4ff6665260664ba6489a9f86`;
its app integration matches source `8d74e9022` on box-git. Asset hash and root,
/desktop/ and /blog/ checks passed. Hosting manifest SHA-256 is
`dca710355dcb9f724fac1a5021ed54f66219d582a5459d68bf03ad7089481e46`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T055255180390Z`
and `/var/backups/webhost-sites/change-20261101T055255180889Z`.

## 2026-11-01 — Text invalid-open recovery

Live static release `42f2fe05a2e071252431b116589dc52b6abd8c6013dd0c87a1020f07ed291708`
recovers from an unreadable direct-open file to an independent editable note.
A live phone-sized account test verified the original bytes remain untouched
and the new note saves; physical touch remains unverified. The test account was
disabled with data retained. Text and CodeMirror hashes and root, /desktop/ and
/blog/ checks passed. Source `7f90e0369` is on box-git. Hosting manifest SHA-256
is `ed671855c37962583864c11eda6ac6a22484e937fca26c9b90103f6ee9e8c406`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T055000805972Z`
and `/var/backups/webhost-sites/change-20261101T055000806665Z`.

## 2026-11-01 — Image format signature protection

Live static release `43f517bf406953873fa9bfc758b94baf09ebb9861a92cd1097749cb0482ed68c`
checks PNG/JPEG/WebP signatures before decoding, preventing a renamed animated
GIF from being overwritten as a still image. Live phone-sized account checks
covered that mismatch, retained edits and PNG/JPEG/WebP resize/save round trips.
Physical touch and malformed files mimicking valid signatures remain unverified.
Two test accounts were disabled with data retained. Asset hash and root,
/desktop/ and /blog/ checks passed. Source `bfc036c15` is on box-git. Hosting
manifest SHA-256 is
`a1ecc2d34dc89e15a624d2fe126d2ea93742334e36b8096ba70099e1044a7e9d`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T054726098095Z`
and `/var/backups/webhost-sites/change-20261101T054726098518Z`.

## 2026-11-01 — Report recovery and G-code coordinate validation

Live static release `c3a2996a14bfd394299e7627344a6bb160b1ce804f42b75c5d83e66aa49176a1`
opens an independent editable report after an invalid direct open and rejects
malformed or repeated supported G-code coordinate words. Live phone-sized
account tests passed both; physical touch and comprehensive machine validation
remain unverified. Two test accounts were disabled with data retained. Asset
hashes and root, /desktop/ and /blog/ checks passed. Source `54d567e8e` is on
box-git. Hosting manifest SHA-256 is
`91c19e5517b0cec778a25e819c4cabc189e4acaa27ab286e85f40fee8e4929e3`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T054615317702Z`
and `/var/backups/webhost-sites/change-20261101T054615318363Z`.

## 2026-11-01 — Drawing and PDF open/save protection

Live static release `c6581dc501bb2b7a60081e0587c132e55e065fd9ddebcc2a2d397f5dbb0d65bd`
recovers Excalidraw from an invalid direct open, checks a PDF’s first-page
limit before replacing the current document, and guards SVG saves and exports
against window closure. Live phone-sized account checks passed all three;
physical touch, PDF export during close and later PDF render failures remain
unverified. Three test accounts were disabled with data retained. Asset hashes
and root, /desktop/ and /blog/ checks passed. Source `12262f982` is on box-git.
Hosting manifest SHA-256 is
`62f8859d6cbad49ffe59c63ee2d4b20b74e12f90c634747969729c39e12e919c`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T054114344891Z`
and `/var/backups/webhost-sites/change-20261101T054114345539Z`.

## 2026-11-01 — G-code, Notebook and fabrication save protection

Live static release `230b64da6e50c3f38cb8833826ab612719ac8473eade1eaa922381dc32e8ef25`
rejects unsupported extra G-code axes, updates Notebook file identity after Open
and Save As, and guards Kiri:Moto and Mesh:Tool workspace saves against window
closure. Live phone-sized account checks passed for each editor; the concurrent
fabrication export event and notebook Save As command were invoked by the test.
Physical touch, actual export generation during that race and machine safety
remain unverified. Four test accounts were disabled with data retained. Asset
hashes and root, /desktop/ and /blog/ checks passed. Source through `563d14bce`
is on box-git. Hosting manifest SHA-256 is
`d18394a9f4ea2f3e5deb18b7193e3c290a9f4414a3f32030e7968ef5f74c42a1`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T053710254317Z`
and `/var/backups/webhost-sites/change-20261101T053710255134Z`.

## 2026-11-01 — Archive, spreadsheet and diagram recovery

Live static release `296d2211a02067d55435262225fbdecbb85c61f38cf053ed04f0a4ce834b3b51`
rechecks selected files and folders before writing a ZIP, opens a usable blank
spreadsheet after an invalid direct launch, and warns before diagrams.net closes
while a save is pending. Phone-sized account checks passed for each, and the
Files delayed-hover drag regression passed against the new bundle. The ZIP
check is not an atomic snapshot and Linux guest fallback remains unverified;
physical touch remains unverified. Four test accounts were disabled with data
retained. Asset hashes and root, /desktop/ and /blog/ checks passed. Source
`9cb2b30a8` is on box-git. Hosting manifest SHA-256 is
`f66b41a2645b56f97e0865f841b539cb81e807a996ed123b657e8ddea02e023f`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T053102310785Z`
and `/var/backups/webhost-sites/change-20261101T053102312574Z`.

## 2026-11-01 — Drawing change protection

Live static release `9f5f22f44246cf54ba643e1cb9df2878dd642424c0d31b6ff77577b2b95eea8e`
keeps diagrams.net edits made during an Open confirmation and marks Excalidraw
background and saved grid settings unsaved. Live phone-sized account tests
covered a delayed embedded autosave and a background-only edit, close warning,
sync and reopen; physical touch and overlapping Open invocations remain
unverified. Two test accounts were disabled with data retained. Asset hashes
and root, /desktop/ and /blog/ checks passed. Source `7571c6a25` is on box-git.
Hosting manifest SHA-256 is
`b3e10a6c4ad1529b8ec61e30fe78e68e1544cd4dac08842f284d42a3af96f10a`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T052558648426Z`
and `/var/backups/webhost-sites/change-20261101T052558649177Z`.

## 2026-11-01 — Pico UF2 overlap protection

Live static release `29708dabf4d7edf54e9a24ce6cd4a1aa9c675092e4476d1d6dd68eb01c86d620`
rejects conflicting overlapping firmware blocks without replacing the running
board. A live phone-sized account check used synthetic conflicting UF2 and the
real Blink worker; physical touch, arbitrary firmware and physical hardware
remain unverified. The test account was disabled with data retained. Asset hash
and root, /desktop/ and /blog/ checks passed. Source `b2d9db9c7` is on box-git.
Hosting manifest SHA-256 is
`cd6cc6f031196f3548977b1194afaf8547db5b529df301a7775e50ada72e2826`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T052438832827Z`
and `/var/backups/webhost-sites/change-20261101T052438834505Z`.

## 2026-11-01 — Files drag and PDF warning ordering

Live static release `1c8412afaedf7c90b96cc3bd608aafd684e403b09c37f3229184386c5d1ddb47`
uses a hash-pinned Chonky patch for the stale-hover drag race and orders PDF
file-change checks so an old response cannot clear a newer warning. A live
deterministic delayed-hover negative-control scenario, cross-window drag and
three repeated phone-sized mouse-driven partial-move checks passed; a live
phone-sized PDF metadata-order check also passed. The earlier unpatched build
had failed 4 of 8 automated drags. Physical touch and broader drag scenarios
remain unverified. Six test accounts were disabled with data retained. Asset
hashes and root, /desktop/ and /blog/ checks passed. Source `b6ffa5025` is on
box-git. The standard Files builder now runs `prepare.py` automatically after the
shared builder dependencies are installed; custom overlays prepare themselves. Hosting manifest SHA-256 is
`1ad499a156c162d39b4e2d7d9dbe7f121e6e3e8729e6e5b722c63ebe7070da74`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T052037982360Z`
and `/var/backups/webhost-sites/change-20261101T052037982777Z`.

## 2026-11-01 — Data Explorer save and chart protection

Live static release `14d8c05159178284e1268d25d48735394d32a324e32dcc654a256ed01ac5073c`
warns before closing while saving a project or CSV, and preserves the unsaved
state of chart changes made during a save. Live phone-sized account tests held
writes, used the actual Perspective viewer API and checked later server saves;
physical touch and all configurations remain unverified. Two test accounts were
disabled with data retained. Asset hash and root, /desktop/ and /blog/ checks
passed. Source `068389d68` is on box-git. Hosting manifest SHA-256 is
`a5844569dc754dd7669238aa96edb23558a094e737c1962f88670fdcb8017b36`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T051837036311Z`
and `/var/backups/webhost-sites/change-20261101T051837036776Z`.

## 2026-11-01 — Text line ending and BOM protection

Live static release `7afbf8fe95fe1e14a436fe98fd192db6317bf7ee70f68d35dcf4ca30db77b5ea`
preserves UTF-8 BOM and uniform CRLF/CR/LF line endings. Mixed endings require
confirmation before LF normalization. A live phone-sized account test checked
server bytes, ordinary save, Save As and cancellation; physical touch and
preserving each mixed ending remain unverified. The test account was disabled
with data retained. Text and shared CodeMirror hashes and root, /desktop/ and
/blog/ checks passed. Source `1a1bc26ae` is on box-git. Hosting manifest SHA-256
is `033fa8e3949cf9f30a173bf6184a07e3c5b428a80ad0b33579b2e30ca897a574`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T051601233923Z`
and `/var/backups/webhost-sites/change-20261101T051601234380Z`.

## 2026-11-01 — Image animation protection

Live static release `0c8399c9c7c90aa96f378c393872b9c8bddb94c332ee42b0489335730017e2cf`
rejects animated PNG and WebP before the still-image editor can save one frame.
A live phone-sized account test used actual two-frame images, static images and
unsaved edits; physical touch and other formats remain unverified. The test
account was disabled with data retained. Asset hash and root, /desktop/ and
/blog/ checks passed. Source `308e14975` is on box-git. Hosting manifest SHA-256
is `2389df35c0fd29b156864f910978ccbd28f0360dba034ea60c90380a9e6f961c`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T051456835000Z`
and `/var/backups/webhost-sites/change-20261101T051456835804Z`.

## 2026-11-01 — Files, audio, circuit and mirror

Live static release `7a87f1fdd0fd2c17aaf72e23ae2edff4446c1fab23e76003e40ad4c68943c484`
contains the Files partial-move message, Audio Editor Ctrl/Command+S, CircuitJS
pending-save guard, Terminal touch-cancel fix, and the current browser mirror.
The Files bundle had expected readiness fields missing from the older deployed
mirror; the current mirror supplies them and supports offline moves. Public
phone-sized account tests passed Audio Editor WAV save, CircuitJS pending save,
Terminal cancelled swipe with real Linux, Files offline Move to…/sync/reopen,
and Files conflict resolution. Multi-file drag passed in 4 of 8 further live
runs; a 700 ms dwell was inconsistent. Instrumentation observed the browser
change the target drop effect from move to none before release without replacing
the rows. The precise cause remains under investigation. Earlier drag
tests also failed while the old mirror was live. Physical touch, Mac shortcuts,
physical devices and closing during a real circuit image export are unverified.
The matching CircuitJS corresponding-source archive was verified before staging
(SHA-256 `94193d48033a433305d96577f0adb3782bf30a1785c80d6afce0ed350341d85f`).
Test accounts used in these checks were disabled with their data retained. App
and mirror hashes and root, /desktop/ and /blog/ checks passed. Source through
`f62721e4c` is on box-git. Hosting manifest SHA-256 is
`0ab5d87c7bb98d83add1fb71c54ae6fec0c8a9164a8c85b62b3e1407b670e154`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T050627901236Z`
and `/var/backups/webhost-sites/change-20261101T050627902078Z`.

## 2026-11-01 — Pico firmware and CAD input

Live static release `fb76b9b0917e748190b9d7475cad9028583c21c57ebc769e320ea96fc089192a`
rejects Pico UF2 file containers without replacing the running simulated board,
and allows cylinders in Replicad without the unused box depth. Live phone-sized
account checks passed with real Blink and CAD workers; the container was
synthetic. Physical touch, physical devices and manufacturing remain unverified.
Both test accounts were disabled with data retained. Asset hashes and root,
/desktop/ and /blog/ checks passed. Source `77758dd8d` is on box-git. Hosting
manifest SHA-256 is
`f294b6e5e6c689ba32552c83a6912c2da82ccc5211e8a130eb9a74ecff977547`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T045756035776Z`
and `/var/backups/webhost-sites/change-20261101T045756036197Z`.

## 2026-11-01 — Image resize and save

Live static release `4cfea5fb11ea97c4c78fbe8b303b8854168fdb1cc88fac656d4e1622a7814051`
adds focused Ctrl/Command+S and fixes a reproduced resize/save timing race. A
live phone-sized account test immediately resized and saved, then verified the
image dimensions on the server. Other image tools, physical touch and Mac
shortcuts remain unverified. The test account was disabled with data retained.
Asset hash and root, /desktop/ and /blog/ checks passed. Source `2ac3ccb13` is
on box-git. Hosting manifest SHA-256 is
`ce1be00677efa0be981b54b363301371da8b0bdf603d835c2689b456d7d33ef9`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T045653281416Z`
and `/var/backups/webhost-sites/change-20261101T045653282171Z`.

## 2026-11-01 — Digital Logic port validation

Live static release `e1e1cc7b971e4687c3775cb34535fcd260f012d425b7358a975a311e5c5ea8d3`
validates that wires connect existing outputs to existing inputs before running
or calculating truth tables. A live phone-sized account check verified invalid
ports are rejected and the previous simulation remains. Physical touch and
hardware behavior remain unverified. The test account was disabled with data
retained. Asset hash and root, /desktop/ and /blog/ checks passed. Source
`df3b0b03d` is on box-git. Hosting manifest SHA-256 is
`706bf05edc0eb22f9becff833601c6256b75c5f9c095e5e0b7cadeac48c9c975`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T045602433431Z`
and `/var/backups/webhost-sites/change-20261101T045602434225Z`.

## 2026-11-01 — G-code unsupported motion

Live static release `a7b37d4e49d969611834bd06ed4fe59c4e950e7afaca2d7cc13c1bc2777e15ca`
rejects unsupported G commands carrying motion-related parameters instead of
silently skipping them. A public phone-sized account check exercised the real
worker against spline, probe, drilling, dwell and comment examples and kept the
previous preview on rejection. This does not establish machine compatibility or
safety. The test account was disabled with data retained. Asset hash and root,
/desktop/ and /blog/ checks passed. Source `1ecacbce3` is on box-git. Hosting
manifest SHA-256 is
`45a37744fac7ce569ea315b1600cb4c3f9db77fc0c925fc1e550a05bf11e7fd2`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T045428090013Z`
and `/var/backups/webhost-sites/change-20261101T045428090800Z`.

## 2026-11-01 — Arduino save close guard

Live static release `11431c97ceab49b53a110b0220565a21a8e61e6d25988c2982f3490322cfc77b`
warns before closing Arduino Simulator during firmware, source and serial saves.
A live phone-sized account test held writes and verified cancel, AVR serial,
and server sync. It did not test physical touch or hardware. The test account
was disabled with data retained. Asset hash and root, /desktop/ and /blog/
checks passed. The live app.js received only the guard change, preserving its
existing sizing configuration. Source `240a0b5b0` is on box-git. Hosting
manifest SHA-256 is
`c411e464ac72eba8635b2a52d57eddeaacad8581eee59af92ad36d05a122ac27`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T045336610774Z`
and `/var/backups/webhost-sites/change-20261101T045336611464Z`.

## 2026-11-01 — Spreadsheet, electronics and SVG save safety

Live static release `e9949ff902d6c321cac4af1702e8aa5efa3c665df9972b31c94aeaee259cdd66`
commits active spreadsheet cells before saving/exporting, retains failed
Electronics Design exports for retry and rejects malformed Stitch Converter SVG.
Public account tests passed for Spreadsheet and Electronics Design on
phone-sized viewports and Stitch Converter on desktop and emulated touch. The
electronics test injected failure and simulated generated bytes. Physical
hardware remains unverified. Four test accounts were disabled with data
retained. Asset hashes and root, /desktop/ and /blog/ checks passed. Source
`a192927dc` is on box-git. Hosting manifest SHA-256 is
`7ea0df5265f7c93b0de58ff33346c6ebd78b26d70dc9185face48369a6a76e6d`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T045214505012Z`
and `/var/backups/webhost-sites/change-20261101T045214505962Z`.

## 2026-11-01 — Document Undo isolation

Live static release `e0117b30a3be72c17f46f6d814add407bc7e188021d5f1beefee70dc59a68247`
resets Undo history when a different report opens. A public phone-sized account
check covered opening, Undo, Redo and server-synced save; physical touch remains
unverified. The test account was disabled with data retained. Asset hash and
root, /desktop/ and /blog/ checks passed. Source `61a281425` is on box-git.
Hosting manifest SHA-256 is
`29f72cf77b1d7fd54cc15b620bf424323b02d1c35fca3969b98d980bbb3343ed`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T045054318423Z`
and `/var/backups/webhost-sites/change-20261101T045054318838Z`.

## 2026-11-01 — Notebook, SVG Editor and Digital Logic

Live static release `f4bc797d9b93bd8676aeb7082bad1b67c239228c4735deb86a50f033ba881623`
contains the notebook invalid-file recovery, SVG Save As identity and Digital
Logic multiple-driver rejection. Public registered-account tests passed on
phone-sized viewports for Notebook and Digital Logic, and desktop for SVG.
Notebook's test did not run Python; physical touch remains unverified. The
three test accounts were disabled with their data retained. Asset hashes and
root, /desktop/ and /blog/ checks passed. Source `8bbd33387` is on box-git.
Hosting manifest SHA-256 is
`6cac660cf16484f7ca73c43f2eb423c84671bc3efbd2084c7911d6927daeb36b`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T044940293180Z`
and `/var/backups/webhost-sites/change-20261101T044940293616Z`.

## 2026-11-01 — App recovery and G-code safety

Live static release `34be5d79ae697c1ddf17b654d6ad84a11128a87716b3188f92e0a91495360544`
contains the Data Explorer worker-start retry, Stitch Converter open-race guard,
and G-code home-offset rejection. Public registered-account tests passed: Data
Explorer used a desktop viewport and injected a worker-constructor failure; the
other two used phone-sized viewports with mouse clicks. Real physical touch,
other initialization failures and physical machines remain unverified. The
three test accounts were disabled with their data retained. Asset hashes and
root, /desktop/ and /blog/ checks passed. An initial G-code run mistakenly
targeted a stopped local preview; the test was corrected to honor its target
environment before the successful public run. Source commits `3eb93c5a0` and
`59e3af77a` are on box-git. Hosting manifest SHA-256 is
`2bd5e4cbb34fbbea9ef955d949150a3096b4c6837570a5ebca36d7ff91ac7567`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T044533613424Z`
and `/var/backups/webhost-sites/change-20261101T044533614099Z`.

## Circuit Lab private research candidate

The local candidate fixes discard, immediate-conflict and stale-simulation
handling; its source-package audit now rejects mismatched app inputs. Simulated
workflow guards and separate real ngspice examples passed. A matching private
archive at `/srv/data/codi-circuit-review-20261101/output/source-relink.zip` on
box-git has SHA-256 `5001e42d586b3d510465d1814d7190d58f654730d6853ccae818e8df98f88f86`.
Package and built-app audits passed; fresh extraction relinked modified
numparam and solved a 5 V circuit. A private fresh-extraction experiment modified KLU_defaults, relinked it, and
confirmed its marker ran while solving a 5 V divider; the original engine solved
the same control without the marker. Evidence is on box-git under
`/srv/data/codi-circuit-klu-review-20261101/evidence/`. This tests one KLU path,
not all configurations or a clean independent rebuild. PTM redistribution terms
remain unresolved. The candidate is not deployed and must not be published
until the documented distribution gate is satisfied.

## 2026-11-01 — Calculator and Pico input

Live static release `04d51cf02682f7e8a6902489c29c7f1975d9f1433a9be7551a4eba41748c548b`
includes the Calculator keypad length limit and Pico serial IME Enter guard.
Both public phone-sized account tests passed; assets and root, /desktop/ and
/blog/ checked. The Pico test used synthetic composition and board messages;
physical keyboards, touch and real MicroPython serial behavior remain unverified.
Three test accounts were disabled with data retained. Source through
`4cf242d05` is on box-git. Hosting manifest SHA-256 is
`954e54eab5dafbf48c263fa780afbae5911e2597aeeeaf9b497849c72750c0a0`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T043619169880Z`
and `/var/backups/webhost-sites/change-20261101T043619170306Z`.

## 2026-11-01 — Image, PDF, CAD and logic workflows

Live static release `0db4822d66dfa593aa266d615bf8a28d66b963d9762bcfd24d6b343e7440785c`
contains the documented Image Editor restore fix, PDF page navigation,
Replicad preview cancellation and Digital Logic pending-save guard. Four
public phone-sized account checks, asset hashes and root, /desktop/ and /blog/
checks passed. Some timing and scroll actions were injected; physical touch and
pixel-identical CAD rendering remain unverified. Four test accounts were
disabled with data retained. Source through `b929564df` is backed up to box-git.
Hosting manifest SHA-256 is
`7bbd5e3046286f9ad79b403300b5118098b6c5bce8c5ac66ad6ded678ba8b789`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T043404259673Z`
and `/var/backups/webhost-sites/change-20261101T043404260364Z`.

## 2026-11-01 — Calculator, G-code and Notebook safety

Live static release `e87dc394762835f1510801a828fd7002b2cffc5b06837418f48d97aab13e620e`
contains the documented Calculator pending-save guard, G-code parenthesized
comment parsing and Notebook Save As protection. Public phone-sized account
tests passed for all three, including server sync and recovery. The desktop
shell was based on the previous live version with only the one Calculator guard
change, and the served bytes were checked. Some race timings were injected;
physical touch and controller behavior remain unverified. Three test accounts
were disabled with data retained. Source through `acbc70930` is on box-git.
Hosting manifest SHA-256 is
`2c2feea1d1b82c0876051027ecc4cf1ab5ea5e223934c2506c9218944e664e83`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T043031515219Z`
and `/var/backups/webhost-sites/change-20261101T043031515631Z`.

## 2026-11-01 — Import, save and firmware safety

Live static release `d8c9c1f7074d037631c8075e85fc601a9ba3deb17a3e3f2641de47869769d13b`
includes the documented Circuit Simulator XML import protection, SVG save
shortcuts, Arduino firmware-change notices and Spreadsheet pending-save guard.
Public phone-sized account tests passed for all four; served assets and the
CircuitJS corresponding-source archive matched their hashes. Some delays and
concurrent changes were injected; physical touch and hardware remain unverified.
Five test accounts were disabled with data retained. Source through `d1f37a865`
is backed up to box-git. Hosting manifest SHA-256 is
`74b9c2d9559e24bf84b9194dc5964a2f76887079f36c44a2a15734ca6b4bd49e`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T042729343902Z`
and `/var/backups/webhost-sites/change-20261101T042729345020Z`.

## 2026-11-01 — Data, PDF and Pico review

Live static release `1af8bd99a73a7773c7e6671a71f59a6f54840207bc22a4b8fdec1dfae3727dd9`
includes the documented Data Explorer query recovery, PDF wrapped-phrase
search, and Pico serial scrollback improvements. Public phone-sized account
tests and asset hash checks passed. A query failure and serial packets were
injected; a separate real Blink-worker check passed locally. Physical touch,
PDF extraction order and real-firmware serial behavior remain unverified.
Three test accounts were disabled with data retained. Source `140ebb4e5` is
backed up to box-git. Hosting manifest SHA-256 is
`f776b2ec7601a51e9282f4fcaac8dd3527f65f9cc3f92bce92feaab54868981d`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T042346291642Z`
and `/var/backups/webhost-sites/change-20261101T042346292070Z`.

## 2026-11-01 — Engineering workflows

Live static release `06dbfc2a20a2ec4a343d549ac73282e196b9acd986b12f8ea29b0088c4d99f79`
includes the documented Digital Logic, G-code Preview and Replicad improvements.
Public phone-sized tests passed for width-error recovery, small-screen preview
and a real STL export with save protection; account sync and reopen were covered.
Asset hashes and root, /desktop/ and /blog/ checked. Physical touch and hardware
remain unverified. Three test accounts were disabled with data retained. Source
through `a5d85bd72` is backed up to box-git. Hosting manifest SHA-256 is
`827e1e9b4093b7ed9869d87b9d4c72b7301a6b36e6e97b92f0e6f3394688c086`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T042017453242Z`
and `/var/backups/webhost-sites/change-20261101T042017453650Z`.

## Fresh checkout: browser Linux runtime

The current v86 runtime and the one guest image selected by
`active-system/assets/terminal/v2/image.json` are checked in. A fresh checkout
uses `active-system/runtime/v86/` automatically when no complete local runtime
exists in `active-system/.build/v86/`. See the runtime README for hashes,
provenance, notices and the local-rebuild override. Older guest images and
intermediate builds remain excluded. A clean clone of `e32e132de` started the
real v86 shell with these files, without a local v86 cache. Build dependencies
and app bundles are still installed or generated as described in local verification.

## 2026-11-01 — Files, Notebook and stitch safety release

Live static release `8c8dd9f477bd8df8b0decc6aa9f59e61d5e892ea124140058370b0d0020011d7`
includes touch-friendly Files multiselect and partial-operation reporting,
Notebook tab-safe saves, Stitch Converter replacement protection, and the
Spreadsheet tangent-pole check. Four public phone-sized account tests passed;
asset hashes and root, /desktop/ and /blog/ checked. Some fault and concurrent
actions were simulated; physical touch and hardware remain unverified. Four
test accounts were disabled with data retained. Source through `72f41ea7d` is
backed up to box-git. Hosting manifest SHA-256 is
`7b3cdcf3a22a07b906dbc1123cf2e4797ec42be6e36a3b9bc3db25c124bca64b`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T041326291958Z`
and `/var/backups/webhost-sites/change-20261101T041326292712Z`.

## 2026-11-01 — Six-app safety release

Live static release `c893a35a981a2180ade8f67e01214c69f9bbb978e970a54f56a2b75976a11b6f`
contains the documented SVG Editor, Calculator, Circuit Simulator, Image
Editor, Arduino Simulator and Terminal changes. All six public phone-sized
account checks passed, including a real v86 shell and real AVR worker; asset
hashes and root, /desktop/ and /blog/ returned as expected. Clipboard responses
and some concurrent-edit timings were simulated; physical touch and hardware
remain unverified. Eight test accounts were disabled, with their data retained.
Source through `22bcced50` is backed up to box-git. Hosting manifest SHA-256 is
`1e8bb932da82f8a04271e91bbc9f178210ac6ebc02276f14916d10109e613f79`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T040952028402Z`
and `/var/backups/webhost-sites/change-20261101T040952029224Z`.

## 2026-11-01 — Eight-app integration release

Live static release `5ad6f63d07e88fb7bdce101b4404493b2b2d9aa6ed18b60b758c816ccce61ee2`
contains the documented Text, Document, Spreadsheet, Data Explorer, PDF Viewer,
Audio Editor, Embroidery Studio and Grid Tools improvements. All eight public
phone-sized account checks passed, as did asset hash checks and root, /desktop/
and /blog/ HTTP checks. Physical touch remains unverified. The first public Grid
check failed because new bundle directories were mode 0700; permissions were
corrected to the standard public 0755/0644 and the check passed on rerun. The
test accounts were disabled; their data was not deleted. Source through
`30c084b0f` is backed up to box-git. Hosting manifest SHA-256 is
`914eff9991fb2576af70d203fedc10b4234a5e5da0064b0e27a6608edcca7000`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T040449577297Z`
and `/var/backups/webhost-sites/change-20261101T040449578024Z`.

## 2026-11-01 — Excalidraw main menu

Live static release `99afe9bd80ff4b9fcc006a4d588fd754cb525a482a810ce8c336c4aa9befd4e0`
places My files actions in Excalidraw's own main menu and removes the duplicate
outer toolbar. Local desktop, emulated-phone and 4K account tests cover drawing,
image insertion, saving, PNG export, conflict handling, sync and reopening;
related phone-sized regressions and a public phone-sized account test passed.
The public test account was cleaned and disabled. Physical touch and the full
feature set remain unverified. Source `0e04ffc11` is backed up to box-git.
Hosting manifest SHA-256 is
`c294f204a0040e3c272dbc8f5269f0f548d55d82c2da14e58a5ad3aca45da668`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T034458326908Z`
and `/var/backups/webhost-sites/change-20261101T034458327325Z`.

## 2026-11-01 — Image Editor File menu

Live static release `bc12051a9156f0d0f047ae0008fa52a3a1881fe8cf88f73417e0530e496df46f`
moves New, Open and Save As from the outer toolbar into a File menu in the
editor's top bar; a fallback appears if that toolbar cannot be found. Local
desktop, phone-sized and 4K account tests cover mouse or emulated touch,
keyboard dismissal, save, sync, reopen, simulated toolbar loss and observer
cleanup. Local phone-sized image-safety, invalid-image and Save As regressions,
and a public phone-sized File-menu test passed. The disposable public account
was cleaned and disabled. Physical touch remains unverified. Source
`5f0e72509` is backed up to box-git. Hosting manifest SHA-256 is
`25a6ff181d9aa9475dfb0ac6560f3be2a8135553a3a7fc75362bdb973b87444f`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T032920455004Z`
and `/var/backups/webhost-sites/change-20261101T032920455425Z`.

## 2026-11-01 — Image Editor confirmations

Live static release `5a567ebae384f7bd4f18c3ca0d95be8514825a12a8c6746952343d572f78ac7c`
uses desktop confirmations for Open, New and Save As and waits for deferred
editor change notifications before deciding whether to discard edits. Local
desktop, phone-sized and 4K account tests cover cancellation, injected edit
races, changed-file protection, sync and reopening. Real local resize,
invalid-image recovery and Save As checks and a public phone-sized safety test
passed. The public test account was cleaned and disabled. Physical touch is
unverified; the outer file toolbar still needs native-editor integration review.
Source `2beb27b9e` is backed up to box-git. Hosting manifest SHA-256 is
`ea1db7aa7254c99be36e0032fa609589785765c6c175ae2f35a27549b2076e4d`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T032329984313Z`
and `/var/backups/webhost-sites/change-20261101T032329984723Z`.

## 2026-11-01 — Falling Blocks confirmation and pause

Live static release `973ed6d4ed69f6729f272b563b1ec0f8b9ea2dd19f9228fdc020ea32c7477513`
pauses before discard decisions and uses desktop dialogs for game replacement,
opening and starting over. It protects progress and files changed during a
confirmation; cancellation leaves the game paused. Local desktop, phone-sized
and 4K account tests cover cancellation, changed progress, save replacement,
sync and exact reopen. Local delayed-save, Files routing and game-model tests,
and a public phone-sized account test passed. The public test account was
cleaned and disabled. Physical touch remains unverified. Source `3e6da4927` is
backed up to box-git. Hosting manifest SHA-256 is
`eee25c98f4c865f40ecacd07226a2057fbb6b99b175f389c4f4cc321f44fc4a5`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T031741515704Z`
and `/var/backups/webhost-sites/change-20261101T031741516128Z`.

## 2026-11-01 — Calculator save confirmation

Live static release `29f8d8842c696d45664de4666d21dbe76504d3550a7b4d468bab91ace9dcfc41`
uses a desktop confirmation when replacing a calculation note. Local desktop,
phone-sized and 4K account tests cover cancellation, changed-file protection,
snapshot saving, sync and Text reopen; arithmetic unit tests and the public
phone-sized account workflow passed. The public test account was cleaned and
disabled. Physical touch remains unverified. Source `a86e91d07` is on box-git.
Hosting manifest SHA-256 is
`813d69e59fc1da13ce66844b92f41bade9981f5699585ed11eb6235bb45686ee`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T031416042570Z`
and `/var/backups/webhost-sites/change-20261101T031416042991Z`.

## 2026-11-01 — Data Explorer confirmations

Live static release `08ffb5ed31f300e3f180ccf690a459e11082ab31b41dd33a6765f40afb8f953f`
uses desktop dialogs for discard, changed CSV and file replacement and checks
that the source CSV still matches before saving a project. Local desktop,
phone-sized and 4K account tests cover edits or files changed while confirming;
a local phone-sized example/query/export/sync/reopen test and public phone-sized
safety test passed. The disposable public account was cleaned and disabled.
Physical touch remains unverified. Source `ad4c2c20a` is backed up to box-git.
Hosting manifest SHA-256 is
`22124895483818a7bbbddee5327bd138b233d975fd18c1ba845b74fb2ef8a7d4`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T031144013960Z`
and `/var/backups/webhost-sites/change-20261101T031144014383Z`.

## 2026-11-01 — Embroidery Studio My files bridge

Live static release `0eb7730ce9b2c17fcab679da996c99406f2dc1878662ee27d0da7a531664e3e6`
uses the rebuilt local-only StitchFoundry source, removes the outer file row,
routes the editor's Open and Place commands through My files, and blocks eight
identified provider/account commands. The source archive is matched against
the patched editor and desktop integration sources; Rust dependency notices
are included separately. Desktop, phone-sized and 4K local tests open SVG,
place it, save the design, synchronize and reopen; local phone-sized export,
file-safety and provider-policy checks passed. Public phone-sized file and
provider-policy tests passed, and both disposable accounts were disabled.
Physical touch, physical sewing and a complete provider-feature audit remain
unverified. The separate `/browser-sources/` page requires login, while direct
source-asset URLs are public; do not claim asset access is gated.
Source `e170ab1a5` is backed up to box-git. Hosting manifest SHA-256 is
`07e5b4009b22ad94e4f109274babd3c252520700a64b93ca5450690df8bc424c`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T030617767098Z`
and `/var/backups/webhost-sites/change-20261101T030617767517Z`.

## 2026-11-01 — Stitch Converter confirmations

Live static release `e08faf59b0760145cf69f118e71451724dd2958f35ece57fb4598b200c45a2c4`
uses desktop dialogs to confirm discard and replacement in Stitch Converter,
with guards for changes during confirmation. Local desktop, phone-sized and 4K
account safety tests passed, as did the full local upload, conversion, sync and
fresh-session workflow and delayed-save regression. A public phone-sized safety
test passed; its test account was disabled after its files were removed. Physical
touch and machine compatibility are not verified. Source `054154ad0` is backed
up to box-git. Hosting manifest SHA-256 is
`5fd574d0f2bcaee9848c7c5fbb12f1f696a1672a8366542196a79144957ddfe1`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T025931272751Z`
and `/var/backups/webhost-sites/change-20261101T025931273225Z`.

## 2026-11-01 — New-account starter folders

New account homes start with Documents, Digital Projects, 3D Objects, Games,
Pictures, Audio and Video. These are normal private account folders, not the
server's system root or the temporary guest Linux filesystem; deleted folders
are not recreated for ready accounts. Existing test accounts are untouched.
Worker `/srv/codi-gateway/releases/starter-folders-r1` is live with manifest
`8b9ea654f1c8f954c8fbade8c83046c388955d70eb2ed9d70991500bc6a854af`.
The guarded upgrade retained permission bindings; native config SHA-256 is
`4d67889b8ae2e978f40c9808b94fd4c7346d162c0eb47fa132e01d3317885e05`
and file config SHA-256 is
`df358b01c6cae919c476bbb23ae392abf5404ba229875188462f11afc3befff9`.
Three local storage tests cover account isolation, modes, deletion, interrupted
setup, unexpected data and quotas; 34 existing storage tests pass. Desktop and
phone-sized local and public phone-sized account checks verified synchronization
and fresh-browser reopening. The public test account was cleaned and disabled.
Physical touch remains unverified. Previous worker is `file-queue-r1`.

## 2026-11-01 — Digital Logic confirmations

Live release `f12200887e11ab34f34308ddb4d11692b5ff38192bdcfec8a2457b42b57868f1`
replaces Digital Logic's native discard and overwrite confirmations with
desktop dialogs and preserves edits or changed files during confirmation.
Local desktop, emulated-phone and 4K safety tests, full-adder and save-race
tests, and a registered-account upload/save/sync/reopen/CSV-to-Data-Explorer
workflow passed. A public emulated-phone safety test passed; its disposable
account was cleaned and disabled. Physical touch is not verified. Source commit
`ca771f0f6` is backed up to box-git. Hosting manifest SHA-256 is
`7342fb26f1e9d8e72eec1126bda21b5cc3fc668075da41ac092ca291b801dfd9`;
rollback inputs are `/var/backups/webhost-sites/change-20261101T024803418429Z`
and `/var/backups/webhost-sites/change-20261101T024803418852Z`.

## 2026-11-01 — app menu and storage candidates backed up

Source commit `b105dc5a467ab88bd2d0f9e2f1bd2ffab9188550` was pushed to the
`simplified` branch on box-git. It contains the current Files move changes,
compact desktop title bars, Embroidery Studio and Electronics Design file-menu
work, diagrams.net and SVG-edit file-menu integration, SVG image/PDF exports,
associated tests, and the app and deferred-feature notes. These are working-copy
candidates and have not been activated on the live site. The detailed test
scope and limitations are recorded in `docs/APP_UNIFICATION_PROGRESS.md` and
individual app READMEs; physical touch and the cross-app third-party-service
audit are still outstanding. The SVG PDF is rasterized.

Stopped isolated previews on ports 18192/18193 and removed only their generated
public trees and the `ui-file-menu-title-test` build output. Isolated account,
issuer and permission data were retained. Local free disk rose from about 3.6 GB
to 5.4 GB. Guest SSH work remained unstaged and was not included in this backup.


## 2026-10-31 — Arduino serial output capture

Live static release `ee3363f4b850dbec9ea235e4b72ed61f4311142309cedfffb19e057775ba493b`; previous `f8e2eafafd0422f0383603e2c814b2021c647b61397c457ba76f51a2ed432423`. Arduino Simulator can save the visible decoded serial output as a `.txt` snapshot in My files. The monitor keeps only the most recent 32,768 UTF-16 code units, avoids splitting surrogate pairs and warns after trimming; restart clears it. The save requires confirmation before replacing a file, checks versions, and distinguishes later serial output from the saved snapshot. Local desktop and emulated-phone tests and a live emulated-phone test cover Unicode echo, cancelled replacement, output during save, account sync and reopening in Text. The live disposable account was removed. This is not raw or timestamped serial recording; physical hardware and touch remain unverified.

## 2026-10-31 — Electronics Design shared three-view layout

Live static release `f8e2eafafd0422f0383603e2c814b2021c647b61397c457ba76f51a2ed432423`; prior stable `4092716a15ee79d1e7bb1d08cdd130af5f23d1317155eec943cc4a86e1d570ab`. On a sufficiently wide and tall window, **Show three views** displays breadboard, schematic and PCB panes using one native document and simulation. Clicking a pane selects it for editing; narrowing or shortening the window returns to single view. The pinned upstream source is patched by `prepare_source.py` followed by `prepare_split_source.py` and rebuilt; the new JS/WASM hashes are pinned in `prepare.py`. Local 4K-sized browser tests exercised selecting each pane, schematic edits, a deletion reflected in all three views, undo, save and width/height fallback; local desktop and emulated-phone account regression tests passed. A live 4K-sized account test covered schematic edit, server sync, narrow resize and reopening on an emulated phone-sized session. Disposable live accounts were removed. Physical monitors/touch, every editor tool and full electrical or manufacturing correctness are not validated.

## 2026-10-31 — Spreadsheet aggregate accuracy

Live static release `4092716a15ee79d1e7bb1d08cdd130af5f23d1317155eec943cc4a86e1d570ab`; previous `eccde7cf460139dd2d983acfcd08a473e0bdf25259d3996d9b9b2da4ad1b2a16`. Supported SUM, AVERAGE, COUNT, MIN and MAX now ignore blank and nonnumeric text cells in referenced ranges or standalone cell arguments; decimal numeric text is included because grid values may be stored as text. AVERAGE of no numeric values reports an error, while MIN and MAX return zero. This changes earlier average/count results for blank ranges. Formula evaluation remains bounded and supports only the documented subset. Unit tests cover mixed cells, cycles and bounds; local desktop and emulated-phone account tests and a live emulated-phone account test checked displayed values and CSV output. The live disposable account was removed. Physical touch and broad Excel compatibility remain unverified.

## 2026-10-31 — Spreadsheet CSV export

Live static release `eccde7cf460139dd2d983acfcd08a473e0bdf25259d3996d9b9b2da4ad1b2a16`; previous `b58c9c8e2e94545d6f4cb9ebb5cd51c1135fc645d607e6bcf2b42454d9a674cc`. Spreadsheet exports the selected worksheet’s calculated values to a separate CSV in My files; formulas, formatting and other sheets are not included. Export runs in the conversion worker, rejects unsupported formulas, limits output to 8 MiB, confirms replacement and protects formula-like text. Local desktop and emulated-phone account tests and a live emulated-phone test cover import/edit/export, cancelled replacement, multi-sheet selection, formula values, invalid-formula rejection and Data Explorer opening. Unit tests cover quoting and CSV text protection. The live disposable account was removed. Physical touch and full spreadsheet compatibility remain unverified.

## 2026-10-31 — Spreadsheet CSV import

Live static release `b58c9c8e2e94545d6f4cb9ebb5cd51c1135fc645d607e6bcf2b42454d9a674cc`; previous `72e97c0bf8047e7cbbbca80cc9c735cdd129f516324abbbd2828bd765593733c`. Spreadsheet can open UTF-8 comma-separated CSV from My files as a new workbook. Fields stay text and leading `=` receives an apostrophe to prevent accidental formula evaluation; the original CSV remains unchanged. CSV is limited to 8 MiB and a 10,000-cell grid, including minimum grid dimensions. Local unit tests cover quoting, embedded newlines, malformed input and limits; local and live desktop/emulated-phone account tests cover opening, editing, saving, sync and fresh-session recovery. One live phone-sized run timed out waiting for sync; a later fresh run passed, and all disposable accounts were removed. Local XLSX and formula regression tests passed. Physical touch, other delimiters and non-UTF-8 encodings remain unverified or unsupported.

## 2026-10-31 — Document save and PDF snapshot safety

Live static release `72e97c0bf8047e7cbbbca80cc9c735cdd129f516324abbbd2828bd765593733c`; previous `7deebe2bfd81bee4eddab89c6444942433358ee55790e5048ddcfe6535b5dca5`. Saving a different existing report now asks before replacement, checks its version and preserves the draft on cancellation or stale saves. PDF export captures the destination and document snapshot at the start and reports later edits; PDF conflict checks and the saved-file watcher use metadata. Local and live desktop/emulated-phone tests cover these cases and account recovery. A local formatted multipage PDF, image, PDF Viewer, offline sync and conflict workflow also passed; its first run used an outdated local PDF Viewer bundle and was rerun with current source. Live disposable accounts were removed. Physical touch and broader document/PDF compatibility remain unverified.

## 2026-10-31 — Digital Logic truth-table export

Live static release `7deebe2bfd81bee4eddab89c6444942433358ee55790e5048ddcfe6535b5dca5`; previous `91a9a4b45c5a6b0a4a4dca28badaa96494c344173067216e513a5f94b604d191`. A calculated truth table can now be saved as CSV in My files. Editing the circuit invalidates the calculated table; a save checks that it still represents the current draft. Existing files require confirmation and a version check, and formula-like headings receive an apostrophe for spreadsheet safety. Local desktop and emulated-phone browser tests cover quoting, cancelled overwrite and edits during save. Local and live emulated-phone account workflows calculated a half-adder table, synced its CSV and opened it in Data Explorer; the live disposable account was removed. A CSV is an exported snapshot; simulation and table limits and physical-touch caveats remain.

## 2026-10-31 — G-code relative movement

Live static release `91a9a4b45c5a6b0a4a4dca28badaa96494c344173067216e513a5f94b604d191`; previous `93a06328aae04a0873cc7d9eb59d413aa15e0c3e4814ed8d0e8f3f1d93942a2f`. The parser normalizes G90/G91 XYZ movements before grouping layers. It treats M82/M83 extrusion mode separately; firmware dialects can differ. It rejects multiple commands on one line, positioning-mode lines with coordinates, arc-center mode changes, and invalid numeric moves, in addition to previous unsupported cases. Local worker tests compared equivalent absolute/relative coordinates, extrusion and layers; desktop and emulated-phone account tests compared pixels at the same canvas size and recovered the file in a fresh session. A live emulated-phone workflow also passed; the disposable account was removed. An initial pixel comparison failed because status text changed canvas height; controlling the test canvas size produced matching images. Large-worker cancellation passed locally. This is a visual aid, not machine or safety validation, and physical touch and other controller dialects remain unverified.

## 2026-10-31 — Digital Logic combined-circuit examples

Live static release `93a06328aae04a0873cc7d9eb59d413aa15e0c3e4814ed8d0e8f3f1d93942a2f`; previous `b737b94d940239632dd62110f8260775ee56ed4316e62b10ed4f730e74264c39`. The example selector now offers a half-adder and a 2-to-1 multiplexer alongside the single gates. Local desktop and emulated-phone tests checked each truth-table row, interactive input changes, replacement, and disposal; local registered-account desktop and phone-sized workflows and a live phone-sized workflow saved, synced, reopened and checked the half-adder truth table. The live disposable account was removed. These are logic models, not timing, electrical, or hardware validation; physical touch remains unverified.

## 2026-10-31 — Data Explorer save checks

Live static release `b737b94d940239632dd62110f8260775ee56ed4316e62b10ed4f730e74264c39`; previous `46ceeb7e966bc0ae3cd50dbdcc8262bb10d308a901a9eeb9337a61b8ce3988f2`. Analysis saves check source hashes and project versions with My files metadata instead of rereading potentially large source files. CSV export overwrite checks also use metadata. Local desktop and emulated-phone tests covered saved analysis reopening, stale project and changed source protection, invalid-project rollback, CSV results, cancelled overwrite and no full-file reads for these checks. A live emulated-phone analysis workflow passed; its disposable account was removed. This does not prove a 128 MiB dataset works on every device or qualify physical touch.

## 2026-10-31 — Audio Editor WAV precision

Live static release `46ceeb7e966bc0ae3cd50dbdcc8262bb10d308a901a9eeb9337a61b8ce3988f2`; previous `92583c0e95dd3bf778fb6b209b4891cd7c8aa6ed9423eff7b260de12295df53e`. Save options now offers 16-bit PCM, 24-bit PCM and 32-bit float WAV. PCM clips values outside −1 to 1; float retains finite out-of-range values, although playback may clip. Existing version checks and the 128 MiB output limit apply.

Local desktop, emulated phone and 4K tests plus live desktop and emulated phone tests checked sample values, output format, rate, synchronization, fresh-session reopen and stale-save protection. An earlier live phone-sized run hit the server request limit during consecutive rapid sync tests; a later run passed after the limit cleared. Worker tests cover 24-bit interleaving and odd padding, float headers, nonfinite rejection and the 128 MiB limit. Physical phones, all codecs and effects, and multitrack persistence remain unqualified.

## 2026-10-31 — Audio Editor WAV sample rates

Live release `92583c0e95dd3bf778fb6b209b4891cd7c8aa6ed9423eff7b260de12295df53e` decodes conventional RIFF/WAVE files at their source sample rate when the browser supports it. If the rate is unavailable or unsupported, decoding uses the browser rate and reports that the original may differ. WAV output remains 16-bit and does not preserve source bit depth or compressed formats. Existing-output checks now use mirror metadata instead of rereading audio bytes. Local and live desktop and phone-sized tests round-tripped a 32 kHz WAV through reverse, save and fresh-session reopen; local 4K-sized and forced-fallback tests also passed. Physical audio-device behavior, all codecs and multitrack saving remain unverified.

## 2026-10-31 — broad text search navigation

Live release `4aa4e77e8401e50c6d306c7a077bdb5b77ae96be11eba70e3e9923308d063e8d` keeps the 50,000 stored-match limit but adds directional searches and single replacements beyond it, including wraparound. Replace all remains disabled for truncated result sets. Local and live desktop and emulated-phone tests cover a match after the limit, reverse/forward wrap, a single replacement, literal symbols, case matching and a chunk boundary. Large-document searches may still take time on the UI thread; physical touch remains unverified.

## 2026-10-31 — larger text documents

Live release `245696116948979eba6935624562050d8dc5e923c4c4f5ce200eeb30fd00035a` raises Text’s opening limit to the shared 128 MiB file limit. CodeMirror indexed lookups avoid rebuilding the document for cursor position and line navigation; word counts are omitted above 2,097,152 UTF-16 code units. Broad searches stop after 50,000 matches and disable Replace all until narrowed. The mirror exposes metadata-only `stat` for change checks. Local and live desktop and emulated-phone tests opened, edited and synced an 8 MiB file and checked the search limit and line navigation; a local desktop test completed an approximately 127 MiB round trip but was slow and memory intensive. Single very long lines, low-memory devices, the exact maximum and physical touch remain unqualified.

## 2026-10-31 — notebook working-copy cleanup

Live release `f76d2c172d3691c0f048cfb84124181ff1772fb53abaf5b1b33fd9dd844f3f09` requests best-effort removal of each closing window’s generated JupyterLite file and checkpoint keys from that account’s browser database, including pending replaced copies; account My files are separate. Unknown database layouts are left untouched. Local desktop, phone-sized and 4K-sized and live desktop and phone-sized tests closed and reopened windows, verified a second kernel still executed, checked both saved server copies, and verified old working-copy keys were absent. An initial live candidate emitted a Jupyter disposed-session error; the explicit widget shutdown was removed and the revised live tests passed without page errors. Browser crashes, interrupted startup, older copies and future storage-layout changes may leave temporary data.

## 2026-10-31 — notebook first-save race

Live release `c82e925ee2f7098eaffb40abbe0555082678d7676a6747d31760d63ded250d04` schedules a follow-up automatic save when the notebook changes while its first save is in flight, and captures the requested destination before asynchronous work. A regression test first waits for the Python kernel metadata to settle, pauses the first account-file write, edits the cell, and checks the newer edit syncs and reappears in a fresh session. It failed against the previous version and passed locally and live at desktop and phone-sized viewports. JupyterLite temporary working copies and lifecycle cleanup remain unfinished; untrusted notebooks are not isolated.

## 2026-10-31 — Digital Logic truth tables

Live release `c70938b7f52efdae36f714ea6219eb58c37d8b52933074642d5f5e2584b43e38` adds a truth table from the current JSON draft using a separate DigitalJS simulation. It supports 1–6 one-bit buttons and 1–16 one-bit lamps, reports undefined signals as X, and cancels old results when the draft changes. Local desktop, phone-sized and 4K-sized tests cover seven gates, a half-adder, undefined signals and cancellation. Registered-account local desktop and phone-sized and live desktop tests reopened saved circuits and generated their tables. The live phone-sized workflow reached cleanup after those checks but hit the shared gateway limit; its test account was removed separately. Physical touch, sequential logic and hardware validation remain outside this test.

## 2026-10-31 — G-code extrusion interpretation

Live release `c36d3910b40e2d7100ca7b81678272766fe67bac2fc6a93fd1566e093a9dfdec` classifies tested M82/M83 extrusion changes using per-tool E values and G92 E resets, so decreasing absolute E is shown as non-extruding travel. Numbered commands, coordinate-only modal moves and full-circle arcs are rejected instead of being silently omitted. Local desktop and emulated-phone workflows, a 100,000-move worker test and cancellation passed. The deployed worker passed registered desktop and emulated-phone tests, and the complete live viewer workflow passed at phone size. Controller semantics vary; this is not a hardware or safety validation.

## 2026-10-31 — account-file retry and batching

Live release `8789f1b5077fe40f25e19c96fef717510c5df91aff4a3a54457a8194f7ca7237` keeps automatic sync attempts from restarting for each local change after a 429, and batches up to 16 existing-file version checks. Individual writes and deletes retain server-side hash checks. Local unit tests cover 20 edited files and conflict preservation; a local registered-account Files test covers cross-device conflict resolution. Live desktop and emulated-phone tests injected two 429 responses and verified queued files reached the server. The issuer authorization budget is still shared behind the reverse proxy; no 100-user capacity or safe change to that limit is established.

## 2026-10-31 — PDF search occurrences

Live release `c49f945e61f50d41de8e87381a3cad3234a3df819db15105e3cba5c2fbae844d` updates PDF Viewer search to visit individual occurrences, wrap across pages, and highlight text that spans PDF text runs. Local and live registered-account tests passed at desktop and phone-sized viewports for repeated matches, reverse navigation, wraparound, cancellation, literal `+`, selection, resize and invalid-file recovery. The disposable live accounts were removed. The viewer still cannot OCR scanned pages; physical touch is unverified.

## 2026-10-31 — Electronics Design account files

The Simplified desktop is deployed at `https://ksu.codes/`; older statements below that this branch is not deployed are historical. Electronics Design release `8acb38f7676d4105c5c450c99cac59380ecce18239eb237169569bb987ece051` captures current projects directly to My files, checks for unsaved work and stale versions, and keeps editor exports separately until saved. Native Save uses the shared account workflow. A new design created during a save retains its own identity. The upstream GitHub account and history controls are disabled; see `docs/DEFERRED_APP_FEATURES.md`. The integration and its limitations are described in `apps/system/electronics-design/README.md`. Local registered-account workflows passed at desktop, emulated-phone and 4K sizes; a 9 MiB project passed locally. The live registered-account workflow reached its final cleanup before the gateway returned a request-limit error; the disposable account was then removed separately. Standalone part import from My files passed local and live desktop and emulated-phone checks; a local test placed an imported part, saved the design, and reopened the embedded definition. Unused imported parts are temporary. Independent physical-touch tests, broad simulation coverage, and hardware validation remain open. Do not treat this as completing the overall app review.


This branch is source development only. It has not been deployed. The old
live site is not modified. Historical handoffs and deployment manifests refer
to the original system and are not instructions for deploying this branch.

## Current implementation

- The desktop no longer loads the peer browser network and Chat, Chess and
  Rooms apps were removed. Signing and the browser-to-server guest relay remain.
- System app source is in `apps/system`, personal template source in
  `apps/individual/templates`, and the app builder compiles their explicit
  entries including dependencies.
- Account Files and Text use `active-system/storage/browser/mirror.mjs` to save
  into account-scoped IndexedDB and queue signed server synchronization. It
  retries, keeps unsynchronized changes and exposes divergent versions for a
  user choice. There is no PC download button. Browser storage can be cleared
  or evicted and Linux guest files are not part of this mirror.
- The server's file gateway checks each signed account and its permissions;
  the private files are owned by the service Unix user, not separate Unix users.
  See `active-system/storage/accounts/README.md`.

## Local verification

Install build and test dependencies locally (they are ignored by Git):

    npm ci --prefix active-system/tools/app-builder --ignore-scripts
    npm ci --prefix tests --ignore-scripts
    node tests/mirrored-files.test.mjs
    node tests/files-workflow.test.mjs
    python3 active-system/scripts/build-public-apps.py --output active-system/.build/simplified-apps

The Files/Text workflow test uses an in-memory server and a DOM simulation. The
mirror test covers offline writes, account scoping, two-tab version conflicts,
server conflicts, remote refresh, folders, deletion and lost replies. The
existing real loopback signed file-gateway HTTP suite also passed 13 tests using
its own disposable state, after updating an obsolete test password. These tests
do not establish end-to-end behavior in a real browser against a running
simplified deployment. The workstation's existing ChromeDriver failed to start
Chrome during this work. A local issuer staging smoke check served the login
page, signed-server configuration, app manifest and browser mirror; it did not
start a complete file gateway or test a browser login.

## Remaining before deployment

- Complete removal of old peer, chat and chess server/operator code and stale
  tests; some legacy scripts and origin/steward code remain intertwined with
  the issuer. Do not use old deployment scripts or release profiles as-is.
- Build a coherent standalone server configuration and release/serving path
  for the reorganized apps, mirror, issuer, gateway, and VM assets.
- Exercise login, mirror, account isolation, offline recovery, conflicts,
  browser restarts and two real browser devices with the actual signed gateway.
- Verify the VM and desktop apps in a real browser, and document operational
  backup/recovery of private account files and databases.

## Local preview on this workstation

`run-simplified-local.py` starts a loopback-only issuer, signed file gateway
and desktop at port 18130. It uses ignored `storage/accounts/data/` and
`storage/accounts/state/` directories for account files and permissions, and
`.build/simplified-local/issuer/` for its test login database and signing key.
These are real local preview state and are not included in Git backups. The
local Linux guest has no Internet relay configured. It requires rebuilt app
bundles and VM boot assets; `--speech-assets` optionally copies an existing
speech runtime/model into the ignored staging tree.

A real local Chrome smoke test registered a separate test account, opened the
desktop, created and edited a file, and confirmed it arrived in the correct
server account folder. The same test does not prove behavior across devices or
deployment readiness.

## Chonky Files and Text reload

Files uses Chonky with React bundled solely in the lazily loaded Files app.
The account mirror supports version-checked file moves and right-click file
rename; it journals the operation locally, uses atomic server rename, retries a
lost response and preserves conflicts. Only synced files and synced destination
folders can begin a move; folder moves/renames remain unsupported. Text Reload
checks the server first and an open editor reports changes detected by sync.
External files must be owned by the file service. Common 0644/0664 file modes
are automatically tightened to 0600 when read or scanned; restrictive owner
modes and unsafe links are rejected. One unreadable
server file no longer stops other files from syncing; its name is reported.

`tests/chonky-browser.test.mjs`, `tests/chonky-move.test.mjs` and
`tests/chonky-rename.test.mjs` exercise the
local preview with a disposable account and a running Chrome DevTools endpoint;
they need the explicit `CODI_TEST_USER`, `CODI_TEST_PASSWORD`, and, for the
first test, `CODI_TEST_FILE_ROOT` environment variables. Neither test should
be pointed at a real account.

## Image Editor

`apps/system/image-editor` wraps Filerobot with app-local React 18 and its own
pinned package lock; Files independently bundles React 19. PNG/JPEG/WebP images
open from Files, and Files offers an import button. The editor uses the shared
version-checked mirror, prevents the vendor's download action, disposes on
close, and disables backend translation and cloud image services. Images are
limited to 8 MiB and 20 megapixels. A real isolated-browser test covers opening,
resizing, saving to the account's server folder, closing and reopening without
external requests. Run `npm ci --prefix apps/system/image-editor --ignore-scripts`
before building the public apps.

The local launcher source now sets a larger per-minute gateway request limit to
avoid the earlier prototype limit being exhausted by directory synchronization.
The local preview was restarted with this limit; the gateway's default remains unchanged.


## Document Editor, PDF Viewer and Spreadsheet

The local preview includes three independent, lazily loaded system apps. The
Tiptap Document Editor writes `.doc` documents to the versioned account
mirror, exports a separate PDF and sends a preview to the PDF.js viewer. The
viewer also opens saved PDFs from Files. PDF output is for straightforward
reports; unsupported content or characters are reported, and it is not a
pixel-perfect document layout system. No DOCX or download-to-PC button is added.

Spreadsheet uses Jspreadsheet CE with an app-owned SheetJS worker and stores
`.codisheet` files; XLSX import makes a copy and export creates a separate file.
Basic arithmetic and a small set of functions use a bounded parser; unsupported
formulas show an error. Excel formatting, charts and advanced features are not
preserved. The vendor's dynamic formula evaluator is disabled under the existing
CSP. Each app has its own pinned lockfile; npm dependencies and built assets are
not committed. Run npm ci --ignore-scripts in each app before rebuilding.

Isolated Chrome tests cover document save/reopen, generated multi-page PDF and
viewer, server files, offline sync, conflicts, account separation and cleanup;
touch emulation covers editing and independent windows. A spreadsheet browser
test covers typing, formulas, native save/reopen, XLSX import and export; parser
tests cover malformed and hostile formulas. These are not physical-phone tests.
The tests use disposable accounts and the isolated local preview. The current
local preview at 127.0.0.1:18130 was updated; no public site was changed.


## Data Explorer

`apps/system/data-explorer` packages Perspective and DuckDB-Wasm together as a
lazy app. It opens account-mirrored CSV files, runs browser-local SELECT queries,
and provides Perspective grid, pivot and chart controls backed by DuckDB's
virtual-server adapter. Database contents, query text and viewer settings are
currently temporary; opening DuckDB database files and saving query results are
not implemented. CSV files are limited to 32 MiB. Automatic DuckDB extension
downloads are disabled. The app's first load is roughly 44 MiB; charts need
worker graphics support. The current Perspective virtual server logs an
unhandled unsubscribe request during viewer cleanup. The viewer, DuckDB connection and per-window database worker are disposed;
Perspective may retain a shared chart worker for reuse. The warning is an
upstream limitation.

`tests/data-explorer-browser.test.mjs` covers an isolated signed-in browser,
CSV import, aggregate SQL, grid, grouped bar chart and closing the window.
The loader and builder bundle-size limits were raised for the DuckDB WASM;
packages remain isolated and lazy. No external site was changed.

## FFmpeg background tool

Applications → System Tools shows a disabled FFmpeg item: the entry has no
window, but apps can call the lazy browser-local tool via `host.tools`. Each
caller has its own single-thread worker; no server process or external CDN is
used. A real browser test generated a WAV, converted it to MP3, verified the
menu and lazy loading, and checked app-view cleanup. The 31 MiB GPL-licensed
core loads only when used; review its source and distribution obligations
before publishing. See `apps/system/ffmpeg/README.md` for the API and limits.

## Audio tools

Applications → Audio Tools opens AudioMass as Audio Editor. Its host controls
open an account file and save single-track edits as a separate version-checked
WAV. Multitrack session persistence is not implemented. AudioMass's embedded
PC download actions are disabled; the host Save WAV button saves to Files.
The browser media CSP now permits local blob media for waveform playback.

WaveSurfer.js and Tone.js are lazy system libraries, not windows: app authors
use `host.tools.createWaveSurfer(options)` and `host.tools.loadTone()`. A real
browser test covers AudioMass opening, reverse editing and saving a WAV to the
account folder, Tone offline synthesis, and WaveSurfer rendering. AudioMass is
prepared from a pinned hash-verified upstream archive with `prepare.py`; its
untracked vendor files and all generated bundles stay out of Git. See each app's
README for limitations, dependencies and audio-resource cleanup.

## 3D printing and archives

Applications → 3D Printing contains Kiri:Moto, Mesh:Tool and G-code Preview.
Kiri and Mesh share a pinned, locally built Grid.Space bundle, with model import
and export connected to the account file mirror. Their internal workspace and
printer profiles remain local browser state, namespaced by account; exporting to
Files is needed for server sync. The G-code viewer's 220 × 220 × 250 mm grid is
illustrative and no physical printer is connected. Tests cover STL import, mesh
union and export to Files, Kiri slicing and G-code export, account workspace isolation and G-code
preview. Advanced modes and physical printers are untested.

Files offers Create ZIP and Extract ZIP on selections; extraction goes into a
new folder and checks paths, symlinks, CRCs and size limits. Folder trees can be archived recursively. zip.js is also a lazy shared system tool; see
`apps/system/zip/README.md`. Grid.Space requires the pinned npm dependencies and
`apps/system/grid-tools/prepare.py` before building. Vendor dependencies and
built assets stay out of Git. All work has been on the local preview.

### 2026-10-30 — account file chooser and engineering workflows

The local Simplified preview at `http://127.0.0.1:18130/` serves the shared My files chooser from source commit `a0a5814ec` (backed up to `box-git-distro`, branch `simplified`). The new student guide is `USER_GUIDE.md`; the app contract documents `host.storage.pickFile`. Text, document, spreadsheet, image, PDF, data explorer, notebook, audio, grid/printing, G-code, SVG-edit, diagrams.net and Excalidraw have chooser entry points. Not every chooser has been individually exercised. Keep PC upload as a separate import path.

Browser checks passed for account folder browsing and text save/reopen including chooser cancellation and window disposal; document editing, PDF preview/export, offline sync and conflicts; CSV → DuckDB query → Perspective chart; spreadsheet save/import/export; image resize and save; SVG, diagrams.net and Excalidraw save/reopen. These checks do not establish full third-party application coverage. The actual guest Linux notebook, production Debian guest and SSH relay remain unfinished. Browser notebook requires scoped `unsafe-eval` and shares the desktop origin; it is not an isolation boundary for untrusted notebooks.

SSH policy/audit implementation remains uncommitted local work in `active-system/guest_service/{coordinator,egress,worker,ssh_audit}.py` and `tests/guest_ssh_*`. It is **not deployed or configured**: in particular, the current experimental egress policy permits port 22 while audit is optional, so it must not be deployed before enforcing mandatory metadata logging and trusted source attribution, provisioning, and end-to-end checks. Private destinations remain intended to be denied; LLM hosts need separate controlled services. The experimental Debian root and test artifacts in `.build` are not a release image.

### 2026-10-30 — app workflow worktrees and temporary Linux boundary

Latest direction supersedes the previous Account-mount notes: Linux home is temporary and is not automatically synchronized. Files can browse `temp_linux`, and its explicit Copy to account action makes a separate My files copy; other apps open My files. A real v86 browser test confirmed no automatic transfer, explicit copy and reset on refresh. Files sees Linux home, not the entire Linux root filesystem. The local preview at 18130 serves this behavior.

App checks are recorded in `docs/APP_WORKFLOW_CHECKS.md` and source-only worktree branches are backed up to box-git: `simplified-apps-office`, `simplified-apps-creative`, and `simplified-apps-engineering` under `/home/dflanag3/codi-app-worktrees/`. Verified commits were cherry-picked into `simplified`. Tests discovered and fixed notebook file switching showing stale contents, Excalidraw treating a clean loaded drawing as edited, and Document Editor accepting but not saving `.codidoc`. Those fixes are staged in the local preview. The app matrix lists the different scope of viewers, generators and library-only tools. The checks do not prove all third-party features or production deployment. Existing uncommitted SSH policy/audit work is still incomplete and not deployed.

### 2026-10-30 — Simplified is live at the domain root

User authorized the cutover. `https://ksu.codes/` now serves the public-only
Simplified static release `/srv/codi-connected/simplified/f66430feb99b44df8de20261f617091c0b079c8441d324842ef63c399d97b07e` (payload source `f44b9f285`, full file-hash manifest beside it). Existing live issuer, signed file gateway/account data, guest network and speech services remain; no account state was copied from the local preview. Existing old backend P2P/chess services have not been retired even though Simplified does not use them. `/desktop/` and `/blog/` remain served by the existing website. The local preview is separate.

A temporary cookie-gated preview and then the actual root both passed real HTTPS Chrome login, signed file write/server-disk confirmation, Linux boot, Document Editor, and JupyterLite notebook. Guest `ping -c 1 1.1.1.1` passed through the existing server relay. The disposable deployment test account, its file and account metadata were removed. Cache migration was tested with an old root service worker. All ten server-loopback production smoke checks passed after updating the KSU root marker for the new entry page; independent WAN and physical-phone checks were not performed for this release.

Current hosting pins: generator `09247414f72e8507c582949c38cae3389cfc13ce50fb6b7118f9c6eaee207226`, manifest `2113960e01087f5f152ff9d29739edf179dd129e603d424164a3f71fd0d57406`, Caddy `741009873464573be63dffa1a913c5cfebde117cf904c9017b9e4f26d0f62ebf`. Use the hosting controller lock and `ops/webctl.py` to validate/regenerate/apply; never hand-edit generated Caddy. The pre-cutover generator and manifest backups are `/var/backups/webhost-sites/change-20261030T182347070194Z/common.py` and `/var/backups/webhost-sites/change-20261030T182347071559Z/sites.toml`. Restore both under lock after validating current pins, reload the corresponding generator, regenerate/validate/apply production Caddy, and rerun all-site smoke; preserve all account databases, keys and files. Caddy reload can interrupt WebSockets.

The browser notebook needs `unsafe-eval` scoped to the notebook bundle and shares the desktop origin; it is not isolated from untrusted notebooks. Linux SSH and its metadata audit are unfinished and not active; the preexisting relay policy allows public ping/DNS/web, not the local uncommitted SSH candidate. The live test reused existing identity/gateway services rather than deploying the local development launcher.

### 2026-10-30 — Text editor update live

Text app user update is live in Simplified release `400e94ae767a6119cb2f54bef1da2484590711a8e03f5191307f0242bad9ddf3`, Text bundle `408a69c9b7bb92fe646a1ed378044c8091d9abc0a7dc7bdac4cb73212cd1a315`, source `fa042ae0d`. Desktop and phone-sized touch browser tests passed for file open/edit/save, browser/server sync, search, Save As collision, dirty protection, in-flight edits, external reload and layout. The physical phone keyboard was not tested. Fixed status-bar clipping/resize-handle overlap and stale shell title. Live desktop and emulated touch sessions edited the same disposable account file, which was verified on server disk; test account/data were removed. All ten server-loopback production smoke checks passed.

The release updates the cache bootstrap/worker to identify release IDs and retire older Codi caches, avoiding a stale Text bundle after refresh. Current hosting pins: generator `09247414f72e8507c582949c38cae3389cfc13ce50fb6b7118f9c6eaee207226`, manifest `9296d551933a52ad2e691175f81f904af249fca6effb82cbe082b5245604c053`, Caddy `349ccc634af3a1a655c9225918adf564c23c89a0d06fa91f80a40bf36f7e5eef`. Previous release is `f66430feb99b44df8de20261f617091c0b079c8441d324842ef63c399d97b07e`; pre-update manifest backup `/var/backups/webhost-sites/change-20261030T204617466098Z/sites.toml`. Use the controller lock and generated validate/apply for rollback; preserve account state.

### 2026-10-30 — CodeMirror system tool and Text integration live

Source `3471d6330` is live as release `4553df94822a2ba98542d1bc5a4e975ba3d6ae458d97643e6817963fb1a85e28`. CodeMirror 6 is a lazily loaded disabled-looking System Tools capability. Text uses an independent view/history for each window; JupyterLite retains its own bundled CodeMirror as the user requested. Text supports line numbers, Python/JS/TS syntax highlighting, search/replace, undo/redo and indentation. Voice inserts via editor transactions. `docs/EXPERIENCE.md` records the interaction and ownership decisions.

Tests covered desktop and touch-sized Chrome layout, file saves/conflicts/Save As, in-flight edits, replacement/indentation undo, multiple independent editors, keyboard-mode attributes, mocked voice button and delayed-load disposal. JupyterLite ran NumPy locally and independently of Text; live HTTPS checks verified desktop/touch Text sync and a notebook Python calculation. The disposable live account and file were removed. Physical phone/IME/audio testing remains outstanding. All ten server-loopback site smoke checks passed.

Current hosting pins: generator `09247414f72e8507c582949c38cae3389cfc13ce50fb6b7118f9c6eaee207226`, manifest `107bcb578e6b29dee266148e0200149a6eae7533220094adc72d2fc48dae9288`, Caddy `bcab1fd046fce6facb199f394cc2c17a303eac5b123d04363a31c256b7f5fef6`. Previous release `400e94ae767a6119cb2f54bef1da2484590711a8e03f5191307f0242bad9ddf3` and pre-update manifest backup `/var/backups/webhost-sites/change-20261030T205910760103Z/sites.toml` provide rollback input; use the hosting controller lock and generated validate/apply, preserving all private state.

### 2026-10-30 — Text code-file chooser follow-up

Release `5f4584fc2f254106b39bfc25c779efcba47d73a7b1ebda15082bbe739b117f2e` includes source `221bbff77`, enabling JavaScript and TypeScript files in Text's Open chooser. Local Chrome verified opening and syntax highlighting JavaScript. Current hosting pins: generator `09247414f72e8507c582949c38cae3389cfc13ce50fb6b7118f9c6eaee207226`, manifest `fd14dd96dca1dc4656d2344113864dfb9e5da09689f4cf4e22fa6a44a40030ff`, Caddy `cc4c40540bba99014c0c9654dc8e6ef04209f3aaaaa3775f740a7142e0ddfdeb`. Previous release `4553df94822a2ba98542d1bc5a4e975ba3d6ae458d97643e6817963fb1a85e28` and manifest backup `/var/backups/webhost-sites/change-20261030T210154442803Z/sites.toml` are rollback inputs; use the hosting controller workflow.

### 2026-10-30 — desktop startup message

Release `2a30ac7ba344873fa8ce67feeb09beb2d5493a4f58c2c9b8cfea580f0eb10f5f` (source `5b4087d7f`) displays “Preparing desktop” during the initial network-link startup. Genuine offline events, repeated status failures, initial recovery, or a startup link that remains unavailable for 15 seconds still display “Connection interrupted”; maintenance retains its own message. Focused lifecycle checks cover preparation, connection, offline and failure. Current hosting pins: generator `09247414f72e8507c582949c38cae3389cfc13ce50fb6b7118f9c6eaee207226`, manifest `23c009af3cf8b89bf0c829b9b403df41d503bda803bac68ca9ddca13d75f2126`, Caddy `cdf7c1302a1c060cdd2f5888401447dfe343a8e231c1a8a473f1ee8873ad8b79`. Prior release `5f4584fc2f254106b39bfc25c779efcba47d73a7b1ebda15082bbe739b117f2e`; manifest backup `/var/backups/webhost-sites/change-20261030T210519632729Z/sites.toml`.

### 2026-10-30 — guest relay no longer locks desktop

Release `43691c72630d640ed36d150d3b394079e7da03746833263ffdc24bb10491577a`, source `02944cc05`, fixes a false “Connection interrupted”: the desktop status monitor no longer treats the independent Linux guest Internet WebSocket as the availability of the whole desktop. Guest relay has its own status/retry handling; real server status failures still use desktop recovery. A real live-account Chrome test with the candidate app loaded the v86 guest, verified the guest relay connection, deliberately destroyed the relay, and confirmed the desktop remained unblocked. Disposable account removed. Current hosting hashes: generator `09247414f72e8507c582949c38cae3389cfc13ce50fb6b7118f9c6eaee207226`, manifest `3bca884707095b6ea40262615957d8384f94f5b311ac801adb1778da5b38982b`, Caddy `27e7c4a6e1b5168da130bb6767cc7832de2aceda34bf9451ff4576558a19898d`. Prior release `2a30ac7ba344873fa8ce67feeb09beb2d5493a4f58c2c9b8cfea580f0eb10f5f`, manifest backup `/var/backups/webhost-sites/change-20261030T210745711711Z/sites.toml`.

### 2026-10-30 — live clock and Browser engine work

Root release `412c5947dac88fc885e55702dce6c15483f057a0a44e84b086693ab83524e29e`, source `f5d6761f9`, updates the desktop clock each second, showing HH:MM:SS and refreshing on focus/visibility. A Chrome simulated-clock check passed a second tick, midnight rollover and focus refresh. Hosting generator `09247414f72e8507c582949c38cae3389cfc13ce50fb6b7118f9c6eaee207226`, manifest `0f17637249c3efb517f262fceb967650258b945941e61a573bdb5ab24562f7f9`, Caddy `6652d24717b7e8fdab6f6009b66ccf8a7c1c30c5e2d0df512fc8686256094d6c`. Previous release `ff5217bffecfabfda063b36b9eec504cc4356095cd0fd4967cab93b263f64efb`, manifest backup `/var/backups/webhost-sites/change-20261030T212458767736Z/sites.toml`.

Browser source is backed up in `apps/system/browser`, with build/update instructions in its README. It is not yet registered or live: no functioning engine has been demonstrated. The 79 JS and 7 Python offline adapter tests passed; two packaged windows in Chrome showed the expected missing-engine error and disposed cleanly. Pinned Gecko build is running unprivileged on r730 at `/mnt/data2tb/codi-browser-engine`; `build-retry.log` records its progress. The initial build failed because the Emscripten compiler was not on PATH; source `db59b9944` fixes that. Live CSP currently blocks runtime blob imports, the app builder/catalog have size and extension limits for engine assets, and no Wisp relay is configured. Resolve and test those explicitly before claiming a usable browser or deployment. The build is independent of the live clock release.

The current seconds-clock release is `9e041eaadd8fdc46159a5f0f730e7b0c6c1960ca5882520cb97f39b549ef0b71` (source `eb8c8d0dc`); `h23` keeps midnight at `00:00:00`. Current manifest hash `69534561b98c0962c6e3fc73aeb24d4dc89818690cd8b787a420e12776461889`; Caddy `432e93b1e02afac80a17682d3571013f8c2e4782ea7f06697722a35603041ca5`; generator unchanged. Previous seconds release `412c5947dac88fc885e55702dce6c15483f057a0a44e84b086693ab83524e29e`, backup manifest `/var/backups/webhost-sites/change-20261030T212554315679Z/sites.toml`.

After the midnight release passed the live clock check, the intermediate minute-only release `ff5217bffecfabfda063b36b9eec504cc4356095cd0fd4967cab93b263f64efb` was removed to recover approximately 442 MiB. The current and previous seconds-clock releases remain. Older notes naming the removed intermediate as a rollback are historical.

### 2026-10-30 — pinned taskbar shortcuts

Live root release `3d2842f5c3e07905e95039074f28752047c58e80dd339ba86936152107d8bee6` (source `e1ac7070e`) defaults each workspace's taskbar to Files then Terminal immediately after Applications; running apps follow. The desktop Home icon was removed. Desktop and touch-sized Chrome checks covered workspace isolation, two terminal windows/count, ordering and visible 44px targets. Hosting generator `09247414f72e8507c582949c38cae3389cfc13ce50fb6b7118f9c6eaee207226`, manifest `3d443c40e93f73510f62d32404a6a027302292c77c987fdbd6ab527f242f2e51`, Caddy `af6abf48193eb26b4c505b079c3e1884570108186111a6475f24f9da10b3cd9e`. Rollback release `9e041eaadd8fdc46159a5f0f730e7b0c6c1960ca5882520cb97f39b549ef0b71`; manifest backup `/var/backups/webhost-sites/change-20261030T212807011384Z/sites.toml`.

Browser build supplement: the adapter's `native/embed-host.cpp` compiled by itself with the pinned Emscripten and generated Gecko headers. During that check an incorrect environment caused Emscripten to clear its shared sysroot while the main build was compiling, producing missing-header failures. The affected build group was stopped; incremental rebuild is running on r730, with log `/mnt/data2tb/codi-browser-engine/build-resume.log`. Native compile alone does not prove final linking or execution. The superseded release `412c5947dac88fc885e55702dce6c15483f057a0a44e84b086693ab83524e29e` was removed after the current taskbar release passed smoke tests; current release and `9e041eaa...` rollback remain.


### 2026-10-30 — Browser real-engine and relay prototype

Source work through the Browser app remains local/source-only, not live. The exact pinned Gecko/SpiderMonkey was built on r730 under `/mnt/data2tb/codi-browser-engine`, with generated 227 MiB WASM and 13 MiB data copied locally to ignored `apps/system/browser/engine/`; no binaries are tracked by Git. Isolated Chrome tests rendered an offline fixture, exercised click and typing, tested two independent windows and observed nested worker targets disappearing after close. The shared-memory TextDecoder bug was fixed. The isolated desktop test opened an account-mirror HTML file through the real chooser. A real Gecko fixture loaded an HTTP page through the source-only Wisp v1 relay; a YouTube request was rejected before DNS, while local signed device records included the requested domains. Fixture authentication and connector are test-only.

User chose server-relayed networking, a blacklist for named video/news/social domains, and a prefilled but disabled whitelist for engineering suppliers. `apps/system/browser/relay/policy.json` holds the lists. Device domain-request events are signed/hash-chained in IndexedDB per account by default and stay on the device until requested; cross-tab signature/tamper tests pass. Optional independent server-side signed ledger is off by default (`serverAuditEnabled: false`); tests verify per-user/all-user summaries and checkpoints. Neither report-request transport nor production account binding of device keys exists. The Wisp prototype requires injected authenticated registered identities and trustworthy client source; no production authenticator, service installation, live route, trusted certificate test or download-to-My-files exists. The current live CSP blocks worker blob imports; the local test allows them only on the worker. Do not publish the Browser app or claim enforcement until the production integration and risk checks are complete. Domain lists cannot block content rehosted on unrelated domains or indirect proxies.

### 2026-10-30 — independent IP and country rules

The user requested separate incoming-login and outgoing-destination IP/CIDR
and geographic blocks, including Linux guest and other relayed services.
`active-system/network_policy/` contains independent empty-default lists,
local DB-IP Country Lite lookup, a spoof-resistant ingress adapter requiring a
verified proxy-provided client IP, a guest policy composition adapter, and a
scoped nftables rules generator for explicit service UIDs. Browser Wisp tests
also enforce the outbound check before connect and during active streams.
Seven focused policy tests and nineteen Browser Python tests pass. A real local
issuer rejected a blocked loopback login despite a forged header and admitted
requests again after an atomic policy change. nft syntax and actual UID-scoped
blocking were verified in disposable network namespaces, as was a country
ruleset derived from the local October 2026 DB-IP data. Dataset SHA256 is
`dbd70ccfa2a13627eaf4913d19920a1a229f1b3c5439ac01c509995b6364202a`;
`maxminddb==2.8.2` is installed in the development venv and recorded in the
requirements lock, not installed on webhost. DB-IP attribution and updater
instructions are in the network-policy README. Country data is an estimate.

This remains prototype/source only: current ksu.codes login and outbound
services do not enforce these new lists. Before rollout, verify the existing
HAProxy PROXY protocol to Caddy chain and explicitly overwrite/verify the
trusted client-IP header, build/deploy a compatible issuer release without the
unrelated uncommitted SSH audit work, install a guarded atomic firewall table
and verify every relayed egress UID, arrange country database/key custody and
rollback, and test real registered logins, active connections and all sites.
Do not claim system-wide blocking from the existence of the adapters.

Browser usage-report source now includes a request-scoped coordinator and a
Python verifier for the browser's WebCrypto-signed hash chain. Local tests
verified a real Chrome-generated report in Python, detected modifications and
checkpoint truncation, enforced explicit administrator/account scope, and
combined two users while counting repeat device snapshots once. No network
transport, production session adapter, administrator UI or online request
exists yet; no browser usage is automatically stored on the server. Optional
independent server audit remains disabled by default.

### Network rule management — development only

`active-system/network_policy/manage.py` provides validated, locked, atomic
operator edits to independent incoming-login and outgoing IP/CIDR/country
lists. Focused tests cover separate rules, invalid edits and optional real
local country lookups. The feature is **not active on the live site**: trusted
client-IP ingress, production service wiring, coverage of every egress path,
and rollout/rollback remain required. Login rules do not revoke sessions.
The Browser relay and browser-local domain-report work also remain development
only; no device records are uploaded automatically and optional server audit is
off by default.

### Browser relay authorization and stream concurrency — development

A purpose-separated `browser_service.authorization` and issuer middleware
`origin_service.browser_authority` now issue and verify short-lived,
registered-account-only browser grants, bound to the signing key, connection
challenge and pinned policy. The reference issuer can enable the middleware
with an explicit `--browser-relay-policy-sha256`; it remains off by default.
The real issuer/ES256/SQLite test passes 28 cases including replay, key theft,
anonymous denial, service-token confusion, policy changes and durable session
recovery. This is not yet connected to Browser, the Wisp endpoint or live
services; admission, renewal, safe service deployment and browser end-to-end
checks remain. A grant is a short lease, so connection renewal and cleanup must
be designed and tested rather than silently extending it.

The Wisp prototype now starts connection requests concurrently with bounded
per-stream early-data buffering, instead of letting slow DNS/connect block
other streams. Tests check concurrent progress and cancellation/capacity
cleanup. Source is backed up; this relay is not live.

### Local Browser relay integration

The isolated launcher supports `--browser-relay` and advertises an explicitly
pinned Browser authorization policy. The desktop obtains a challenge, proves a
registered session to the issuer, and authenticates a purpose-bound grant to
the relay. The relay uses a per-window HttpOnly, SameSite=Strict, scoped cookie
(Secure on HTTPS); it renews a short lease, closes on expiry/revocation, and
invalidates admissions at restart. This does not put account keys or bearer
secrets in the renderer's URL. 31 real issuer/SQLite and local HTTP/WebSocket
authorization tests and the Browser offline/unit suite pass. The actual Gecko
engine rendered an external HTTPS page through this path in an isolated local
desktop; this is not a production or broad site-compatibility test. Traffic
policy, deployment, trusted external source attribution, stronger operational
limits, file downloads, report transport, license/source distribution and
mobile testing still require work. The local test state is disposable and the
live site remains unchanged.

### Explicit Browser URL downloads — local development

The local relay now supports a bounded, registered-session-only explicit
Download URL action. Every HTTP(S) request and redirect checks domain policy,
resolves once, rejects non-public/mixed answers, pins the connection to the
checked IP and checks outgoing IP policy during transfer. It enforces an 8 MiB
limit matching the account file service and does not copy Gecko cookies or
request headers. Downloaded bytes are written to the browser/server-backed
My files mirror; this is a URL action, not interception of ordinary Gecko
clicked downloads. The latter remains unfinished. Fixture tests exercise
redirect policy, IP denial, size and expired lease, and a real HTTPS download
was saved to My files in the isolated desktop. Production service wiring,
traffic controls, broader website behavior and phone tests remain outstanding.

### Phone windows and terminal startup — live

Root release `bfcccab6fcdfd33221aeb5e57dd59d8eb788217b0c0172bb1cf45b3c533a807b`
uses the prior live assets plus the tested phone window and terminal changes.
On compact screens all applications start maximized; the normal maximize
control still restores a movable window. Desktop window sizing is unchanged.
Each new independent PTY runs the real shell `help` command and suppresses
only the initial BusyBox ash banner. A local real-v86 phone-emulation test
verified the command output and absence of the banner; 12 app types were
checked at phone and desktop widths. Public asset hashes match and all ten
hosted sites passed loopback production smoke. Physical phone testing remains
separate. The previous release is
`3d2842f5c3e07905e95039074f28752047c58e80dd339ba86936152107d8bee6`;
manifest backup `/var/backups/webhost-sites/change-20261030T225146530854Z`.
Current hosting generator `09247414f72e8507c582949c38cae3389cfc13ce50fb6b7118f9c6eaee207226`,
manifest `8dbc923802a0fd3f66eaef45bf8105c6257ecb02a592de2956233ee1f369818b`,
and derived Caddy `525b9b8e4997c53fb5522659a80bb9f8497c63abf3c6b955d6204c1aef79b551`.
Use the hosting controller lock and generated configuration for rollback.

### 128 MiB file work — not live

Development raises the prior 8 MiB file limits to 128 MiB in the mirror,
gateway, Files, ZIP, Browser URL download and affected app adapters. The
encoded request allowance, transfer pacing and default account disk quota were
also adjusted. A real registered browser wrote and read back a 128 MiB file
with identical SHA-256; 128 MiB plus one byte was rejected by the client. The
response now streams base64 in bounded chunks and the browser codec avoids a
per-byte `Uint8Array.from` over a 128 MiB string. The isolated combined local
issuer/proxy/gateway reached approximately 759 MiB high-water RSS during the
round trip; the existing live gateway is capped at 384 MiB. Uploads still use
large JSON/base64 request buffers, so concurrency and memory need more work
before rollout. Current live config still advertises and enforces 8 MiB. Some
apps have independently lower format/processing limits (including Text,
Data Explorer and Audio Editor); they have not been raised by this change.

### Streaming account transfers — local development

The gateway now accepts a purpose-bound, account-signed binary upload with
small authenticated metadata, streams bytes to a private temporary file,
checks the exact declared length and SHA-256, and atomically publishes through
`UserStore.put_stream`. A separate capability endpoint permits older services
to keep using the legacy JSON/base64 client path. Reads use an authorized open
file descriptor and bounded base64 output chunks; an already-open descriptor
continues to read the selected version across atomic replacement. File
permissions, preconditions and quotas are checked before publication. Temporary
uploads are unlinked file objects and cannot become account files on failure.

Local results: 34 private storage tests, 16 HTTP/issuer/gateway tests including
corruption, replay, account isolation and concurrent separate-account uploads;
a real Chrome registered account wrote and read 128 MiB with matching SHA-256
and confirmed the binary endpoint was used. A 128 MiB plus one byte request was
rejected by the browser. The combined isolated issuer/gateway/proxy process
reported a high-water RSS of 115484 KiB on that round trip. This is a single
local measurement, not a production concurrency capacity claim; large reads
still use browser-side JSON/base64 buffers, and production ingress, service
memory limits, temporary-disk placement, interrupted uploads and multi-user
stress need validation. The live file service remains the older 8 MiB release.

A subsequent actual loopback test uploaded two 128 MiB files concurrently from
separate signed accounts in 35.1 seconds, verified each disk hash, and measured
115700 KiB high-water memory from `/proc/self/status`. A first version of the
test used `getrusage` and reported an inherited 1117892 KiB peak; the current
process's `VmHWM` exposed that measurement error, and the full test was rerun.
An additional test disconnects a partially sent authenticated upload and
confirms no partial account file is published. These are local tests; the 128
MiB changes are still not live, and production ingress/deployment remains.
The stopped disposable previews on ports 18137 and 18138 were removed only
after checking exact paths, owner, filesystem and absence of running services.

### Browser touch and keyboard — development

The Browser canvas translates touch taps into page clicks and touch drags into
wheel scrolling; the toolbar Keyboard button activates an app-owned text bridge
and asks the desktop to enable the on-screen keyboard. Unit tests cover touch,
text/editing keys and desktop mouse events. An isolated real-Gecko mobile
emulation test tapped a guest input, typed `abc`, confirmed the guest changed
its URL fragment in response, and observed a rendered page change after a
touch drag. This is not a physical Android keyboard or full IME, accessibility,
text selection or drag-and-drop test. Browser and relay are not live yet.

### Browser relay private ingress candidate — development

`active-system/scripts/serve-browser-relay.py` provides an operator entrypoint
for a protected Unix-socket service. It validates a pinned issuer policy,
requires a service-owned 0750 socket directory, sets the socket 0660, checks
Linux `SO_PEERCRED` for the configured proxy UID, and requires exactly one
well-formed ingress-provided client address. Runtime IP/country and domain
policies remain independent. The relay now bounds shared active streams,
tries alternative already-vetted addresses when an earlier address is
unreachable, and checks revised domain/IP policy during active traffic.
Browser URL downloads spool to private temporary disk and stream to the
client with per-window, per-account and shared concurrency caps.

Local tests include actual subprocess startup, pin rejection and socket
cleanup, wrong peer UID/address rejection, a registered real-issuer grant
through the Unix socket to an external HTTP endpoint, dynamic domain/IP
blocking, alternate-address fallback, stream-cap cleanup, and a real Gecko
HTTPS/download workflow. A separate loopback Caddy fixture on box-webhost ran
as the actual Caddy UID; PROXY v1 and v2 source addresses replaced duplicate
forged client-IP headers and the upstream observed that UID. This fixture did
not exercise an independent public network or activate the live route.

`prepare-browser-hosting.py` derives an opt-in managed generator candidate for
the private socket route, scoped Browser worker CSP, larger file body limit,
and trusted login header. With all flags absent it reproduces the captured
baseline byte-for-byte; KSU-only validation/round-trip tests pass and the
rendered production Caddy configuration validates. No candidate was installed
or activated. Before production, install and harden the service with the right
socket directory/group, prove the complete live HAProxy-to-Caddy address path,
secure the login filter against direct issuer-port spoofing, cover guest and
other server egress, arrange database and license/source custody, and perform
live rollback/restart and phone tests. The optional server audit is still off.

### Private relay staged on box-webhost — 2026-10-30

The isolated Browser relay is installed and running privately, with no public
route and no boot enablement. Its root-owned runtime manifest is
`fefb814d50b46db56a948e01a9f3879c6fc3d9287ae32ee3a7b9e9a09a49dc52`;
its separate dependency environment is pinned by lockfile SHA-256
`a5ee6aa9a1c18535aad36a52b7ec57ca9c1e1fca03cbb02d4c423fd7ec317326`.
The static `codi-browser-relay.service` runs as `codi-browser` with a private
socket in `/run/codi-browser`. A request from Caddy's UID received HTTP 200;
the same request from root was rejected with HTTP 403 by peer-credential
checking. After restart the socket became available and again returned 200;
an immediate probe raced startup and initially failed to connect. The public
relay route returns 404. This is only private-ingress verification, not a
live Browser release or a complete production security test. Configuration
is in `/etc/codi-browser`; the initially empty access-policy file matches
the checked-in default, and the separate domain policy retains its existing
blacklist and disabled whitelist. Geo-IP data is the DB-IP Country Lite
October 2026 snapshot; attribution and updates are still required.

### Issuer ingress protection candidate — 2026-10-30

The issuer currently listens on `127.0.0.1:8118`; the managed Caddy route is
the only configured local consumer found. The network-policy kernel module now
generates a separate atomic nftables table that permits a designated proxy UID
to connect to that loopback port and rejects other local socket UIDs. In an
isolated network namespace, real connections from two distinct unprivileged
UIDs worked before the rule; afterward only the designated UID worked, and
reapplying the ruleset twice preserved the restriction. A root socket was also
rejected. Removing the test table restored access. This does not defend against
an administrator who can alter firewall state. Both the namespace test and
the nine network-policy tests passed; the latter require the development venv
for the installed Geo-IP reader. An initial run with system Python failed only
because that interpreter lacks `maxminddb`.

That original whole-port proposal was not installed: subsequent inspection
found another consumer, leading to the split-port approach described below.
An actual public proxy-chain test, issuer integration and rollback are still
required before login IP restrictions can be considered live.

### Browser source snapshots staged — 2026-10-30

Seven hash-verified source artifacts now reside privately under
`/srv/codi-browser/source-staging/engine-6736dce5/` on box-webhost. They cover
the exact clean Firefox source revision, Firefox-WASM base and actual local
patch, the added native adapter, the patched Emscripten checkout without
dependencies or caches, the installed Wisp source/license, and the relevant
Codi app/integration source at commit `6749ae260`. The archive checksums,
scope and remaining licensing review are in
`apps/system/browser/docs/SOURCE_PROVISION.md`. Zstandard integrity and an
actual base-plus-patch byte comparison passed; the Firefox archive is 918 MiB.
Temporary transfer and duplicate archive staging directories were removed
after the copies were verified; the original build checkout remains. The
sources are not public yet, and this preparation does not establish complete
third-party license compliance or authorize distributing the engine without
the remaining notices and source review.

### Split login and Browser issuer candidate — 2026-10-30

Further inspection found that the existing Linux guest relay reads issuer
configuration directly from port 8118. Restricting that entire port to Caddy
would break the guest. The profile-28 candidate therefore keeps the existing
issuer port for configuration and other APIs, rejects `/api/v1/auth` there,
and binds a separate login-only listener on port 8117. The managed-hosting
candidate routes that exact path to the new listener and overwrites its client
IP header. The proposed nftables proxy-UID boundary applies to 8117 only.
`render-issuer-ingress-service.py` produces the atomic rules and a static
systemd unit; these have passed isolated nftables syntax and systemd unit
validation. The guard is now installed and active on box-webhost for port
8117 only; a real temporary socket test admitted Caddy UID 997 and denied a
root-owned client, and restarting the guard preserved the rule. The current
issuer remains on 8118 and the public site continued to answer. The candidate
issuer unit requires this guard before startup.

`build-browser-issuer-release.py` verifies the exact live profile-27 manifest
before producing an isolated profile-28 candidate. It preserves the existing
public asset tree, adds the registered Browser authority and the split login
listener, and retains the existing live guest and steward unit renderings. The
current candidate manifest SHA-256 is
`d09ddbbb04ce0e294a97b44ae1d8a8a555d302385c5d42b7fb7fd867bfab4878`,
installed privately at `/srv/codi-connected/releases/browser-issuer-profile28-r2`.
An isolated real issuer started, advertised the Browser policy, denied auth
on its ordinary port, accepted only login on the separate port, and enforced
an updated IP rule without restart. Unit and network policy tests pass. Caddy
validated the candidate hosting configuration, and its adapted route order
put the exact login path before the general API route. This is not a complete
registered-user, external-ingress or deployment test; no candidate hosting or
issuer change has been activated. The first candidate attempted a separate
issuer Python environment, but managed preflight rejected it because the
existing Linux guest backend is pinned to the original environment. The
revised candidate keeps that environment and reads `maxminddb` from the
root-owned, immutable Browser environment only after validating its package
path. Real server checks resolved test addresses through that path, and the
candidate passed the managed installation, guest binding, dependency and
systemd syntax preflight. A separate isolated run of the installed candidate
as the actual `codi-issuer` service account verified configuration, the
Browser challenge handler, split login and an IP block using the existing
Python environment. A test rejects user-writable fallback modules. The
superseded candidate and unused environment were removed. The later entry
records the subsequent file gateway upgrade.

### Additional trusted-ingress gap — 2026-10-30

The split login guard does not by itself protect the original address: a real
unprivileged local connection to Caddy port 8443 sent a fabricated PROXY
header, and Caddy recorded that fabricated `203.0.113.99` client address. Do
not enable or claim live client-IP login enforcement until this HAProxy-to-Caddy
boundary is fixed. HAProxy runs as `DynamicUser=codi-shared-ingress`; its UID
can change, so a permanent nftables rule cannot safely pin the currently
observed numeric UID.

`render_caddy_proxy_guard` and `render-caddy-proxy-guard.py` prepare a distinct
atomic nftables table, a root guard service and a Caddy startup dependency.
Namespace tests prove both Caddy ports accept only the specified UID. A
temporary real-host rule using the current UID blocked an unprivileged direct
connection while three sites remained available through HAProxy; it was then
removed. A separate systemd fixture verified that a service with
`DynamicUser=yes` uses a matching locked static account after restart. The
static account migration, durable guard installation, controlled rollback and
full live/independent-network tests have not yet been performed. Candidate
rules for UID 966 were rendered and syntax-checked; that UID must be confirmed
free again immediately before any migration.

### Trusted Caddy ingress guard active — 2026-10-30

The controlled transition was exercised with real services and rolled back
successfully before final application. It then installed a locked static
`codi-shared-ingress` account at UID/GID 966, preserving the existing ingress
unit and its restrictions, and installed the `codi_caddy_proxy_guard` nftables
table plus `codi-caddy-proxy-guard.service`. A Caddy dependency starts the
guard first. The operator and exact inputs are root-owned in
`/srv/codi-ingress/operators/caddy-guard-db05e87a4`; its result receipt is
`/var/lib/codi-ingress/caddy-proxy-guard-result.json`. Both the real rollback
exercise and the final apply preserved the expected status codes for all ten
sites, including hardware.ksu.codes' intentional 401. The old unprivileged
direct connection to Caddy port 8443 now fails. HAProxy and Caddy were each
restarted and the guard remained active; HAProxy retained UID 966. A request
from i36 over its independently addressed Ethernet connection was recorded by
Caddy as its correct public IP, `104.180.210.36`. This is address-chain
evidence, not yet a live login-filter test. Caddy's generated file remains
SHA-256 `525b9b8e4997c53fb5522659a80bb9f8497c63abf3c6b955d6204c1aef79b551`.

The private Browser relay is now also a `Wants`/`After` dependency of Caddy,
so a Caddy start pulls it in without making unrelated sites depend on its
success. The issuer and hosting candidate are still not active. The previous
paragraph records the discovery and temporary test before this installation.

### Coordinated backend transition exercise — 2026-10-30

The first actual issuer/hosting rollback exercise did not reach the hosting
switch: managed readiness detected that profile 28's TURN policy expectation
omitted the existing ICE preference. The native controller restored profile 27,
all three native services and the website; both transition journals cleared.
This exposed a missed profile list in `origin_service/turn_management.py`.
The candidate builder now updates that list, and a regression test compares
the old and new public TURN policies. The corrected local profile-28 r3
manifest is `957e6fec98101f5a57c7f8ebab633050d27759d5c0d673049b4da3527d39715d`.
It supersedes the r2 candidate; r3 has not yet been installed or tested in a
live managed transition. The live login and Browser routes remain unchanged.

### Browser backend and login IP filter live — 2026-10-30

The corrected profile-28 r3 and managed Caddy routing passed a real
coordinated upgrade/rollback exercise, then were activated. The issuer is
`/srv/codi-connected/releases/browser-issuer-profile28-r3`, manifest SHA-256
`957e6fec98101f5a57c7f8ebab633050d27759d5c0d673049b4da3527d39715d`.
The current hosting generator is
`25d58c0602e296aabce40c24d64d52408140e0c78e63347f6485aa240f39da64`,
manifest `a8ac8177967396495711247402ce6b346865d1d2aab84d7e7310817e0c9d7d1c`,
and derived Caddy file `ce813404d53fd8d9344eef3a49af868fbce53d70f01612cfd78c0e89e552edcd`.
The root-owned transition operator is
`/srv/codi-browser/operators/backend-b7c31de02`, with receipt
`/var/lib/codi-ingress/browser-backend-result.json`. The previous native
release remains available for managed rollback. The failed r2 candidate,
obsolete operator and temporary transfer directories were removed.

From the external address `104.180.210.36`, a temporary incoming-login block
returned 403 even with forged `X-Codi-Client-IP` and `X-Forwarded-For`
headers; the Browser relay challenge remained available. Restoring the empty
policy returned the same invalid login request to its expected 400 response.
The original policy hash was confirmed after restoration. A real headless
Chrome registered a disposable account, obtained a signed Browser relay grant,
downloaded an allowed HTTPS page, rejected YouTube, IPv4/IPv6 loopback literals
and a hostname resolving to loopback, and opened Wisp. It then signed in again
in a fresh browser context and removed its exact test account. The reproducible
check is `tests/live_browser_relay_account_check.py`.
After separate live relay and issuer service restarts, the same registered
account/relay test passed again; both guard units and services were active.

Only the backend, login filter and Browser outgoing policy are live. The
Browser app/engine are not yet published; ordinary clicked downloads remain
unfinished. Country blocking and an existing live transfer under a rule
change still need testing, as do the other server egress paths. The desktop
remains limited to 8 MiB pending the frontend/proxy rollout described below.
A login block does not revoke an existing session.

### Browser sources published and 128 MiB worker candidate — 2026-10-30

`https://ksu.codes/browser-sources/` now serves the Gecko-generated license
inventory, Emscripten/runtime and Wisp/adapter notices, and exact pinned
source archives through a fixed filename allowlist. Source downloads use
Caddy's file server and support byte ranges; they are not copied into the
desktop release or Git. The notice generator validates the original Gecko
notice and exact Emscripten/Wisp archive hashes. A real hosting rollback
exercise passed before activation, all ten sites preserved their expected
statuses, twelve public source/notice links responded to HEAD, and a separate
external host obtained a 32-byte range with HTTP 206. Unlisted paths returned
404. The prior small obsolete source archive and transfer fixtures were removed.
Current hosting generator SHA-256 is
`9bb5e958f27985891b8c927215e4927ddd514870309e271ec0f29790e2de8c68`,
manifest `3ff13521fdca82c339d39fff09be45258e41f132d893a9e7c9fc51796636d93f`,
and Caddy `a4d05c0e404188ddf2192dd5f9efb53076aa499f76d5dc2b36e87c6ee7e3df63`.
The root source-route operator is `/srv/codi-browser/operators/sources-37218ff39`.

The Browser app has a source/notice link and simplified startup/status text in
source, and its 83 focused tests pass; it is still not deployed. The engine
link log reports 37 unresolved functions, including file-picker and audio
functions. Its impact and the actual linked-component/license inventory need
review before claiming general website support or complete compliance.

`build-large-file-worker.py` verifies the exact currently deployed gateway
manifest, exports the six reviewed changes, preserves the existing live Python
dependency lock, and refuses uncommitted worker inputs. Its reproducible
candidate manifest SHA-256 is
`53588b25c06c7b88e038bcca4cca13b8de9bcabc35b952d463c1d7ff3727b5c0`.
A fresh local test streamed two signed 128 MiB uploads concurrently in 35.1 s
with approximately 115672 KiB process high-water memory. The worker passed
the existing root file operator's runtime and policy preflight, was upgraded,
rolled back to the previous worker and upgraded again through the journaled
private-file code helper. Each transition reported preserved permission and
folder bindings without restoring account/file data. The new worker is now
active at `/srv/codi-gateway/releases/53588b25c06c7b88e038bcca4cca13b8de9bcabc35b952d463c1d7ff3727b5c0`;
the previous worker remains available for rollback. Its public upload
capability reports 134217728 bytes. A real registered browser performed a
signed binary write, read with hash verification and delete; its exact empty
test folder, gateway records and disposable account were then removed. Issuer
metadata, browser mirror and proxy limits still restrict the desktop to 8 MiB,
so a live 128 MiB round trip remains unproven. The static release builder now
hashes files in chunks instead of reading the entire WASM asset into memory.

### Large-file ingress and notebook names — 2026-10-30

The assembled local desktop completed an authenticated 128 MiB binary
write/read with matching SHA-256. The live gateway ingress was then changed
using `activate-large-file-ingress.py`: its exact KSU-only flag change was
applied, rolled back and reapplied with all ten site statuses preserved.
Current hosting manifest is
`a287d968a80cb8387295a4a5fb6a23cb039efc6e127aaebb7e7cb7d699481260`
and Caddy is `0abb1284887d57115a48fc6c6a554207930294c0582c420cc1f13e168e5ad016`.
The earlier hosting pins above are historical. A real signed registered
browser directly used the live gateway to write, read and delete 128 MiB with
matching SHA-256 `fb3251b1618f009f9fb644d1302b668a65a131e58521ef86e4d5080625dd138a`;
its exact disposable account and folder were removed. The live desktop and
issuer still retain the earlier file limit, so the live desktop mirror's
end-to-end 128 MiB transfer has not been verified.

Notebook temporary names previously used the desktop window number; source now
uses a fresh random UUID per window. The new notebook build is only in the local
candidate, not live. JupyterLite config namespaces browser working storage by
the current account; server My files uses an authenticated account-to-folder
mapping. Browser storage namespaces are not a security boundary against a
person with access to that same browser profile. A real test with two accounts
open in separate tabs of the same browser profile passed: their notebook
storage namespaces and UUID names differed, the second notebook listing did
not show the first, and the second account could not read the first account's
My files test document. After accepting the notebook's browser leave-page
confirmation, signing out and back into the first account also passed; its
own saved test document remained available. An earlier test timed out because
it did not respond to that confirmation, not because isolation was verified.

The Browser source archive for the `0fc6bf9a7` desktop candidate is now
available at `/browser-sources/codi-browser-source-0fc6bf9a7.tar.zst` with
SHA-256 `47ac4d287646b42b808680e2be422e4a7a7bf62dcd928b6ae911bf4a2c91bbe4`.
The prior snapshot remains available, and the public index and notice manifest
include both. The exact allowlist addition was rollback-exercised and deployed
with all ten hosted site statuses preserved; the new source download's hash was
verified over HTTPS. The pre-update source-index files are retained in the
root-only `/var/lib/codi-ingress/browser-source-index-0fc-backup.json`.
Hosting generator is now
`d32c182fe5043a1671d460bd27325cf72750d94e771dbd070f523537eee407e8`,
manifest remains `a287d968a80cb8387295a4a5fb6a23cb039efc6e127aaebb7e7cb7d699481260`,
and Caddy is `c098afe8572a12105527e17773c14f551075c52854617838b5477ab136ea55a0`.
Browser desktop deployment and complete engine-license review remain pending.
The next assembled candidate, with the Arduino application, has cache ID
`4ac8781a92ed58b9fc0d878d927055d86d44fa3fe4aaadd4a2858757ce63d80a`.
Its matching `adece7482` Browser/source-integration archive has SHA-256
`2e64c1c3856f622af986157059eca6f8f14a8c73e275829d397372b70701c127`
and is published alongside the previous versions at `/browser-sources/`.
The archive's desktop source and the candidate `app.js` were compared by hash.
The source-allowlist update passed a rollback exercise and all-site checks.
Current hosting generator is
`6ac5e114fe7ed8949f2c8ce3876cafa1745353ef0409c4d2bc13600067ea3226`,
manifest remains `a287d968a80cb8387295a4a5fb6a23cb039efc6e127aaebb7e7cb7d699481260`,
and Caddy is `9de277b1a34fa28f76899a883fdf8fdb1d6d5478fdb9c33e6739ce12014b14ab`.
The candidate's Browser passed real desktop and phone-emulated Chromium tests
for authenticated networking, My files download, keyboard input and touch
scrolling. This does not qualify a physical phone or general website behavior.
`build-large-file-issuer.py` creates a profile-28 candidate from the exact
live issuer by updating the advertised file limit, its managed-policy health
check and the release manifest. Earlier candidates omitted rollback
compatibility and must not be deployed. Candidate `profile28-large-files-r3`
has manifest SHA-256 `0aaf61849fa03e41376d63a36496c83e83adbc97c14aeafe366100ff9e530af2`.
Its isolated tests passed, including advertised 128 MiB, metadata validation
against both old and new issuer releases, separate login listener, rule
updates and unchanged TURN policy. The root-owned release was staged from the
verified prior release, then its managed upgrade and rollback were exercised
before final activation. `/config.json` now advertises 134217728 bytes from
`/srv/codi-connected/releases/browser-issuer-profile28-large-r3`; all ten
site status checks passed. The live desktop remains on its old static release
and its mirror's 128 MiB end-to-end path has not yet been verified.

Real live signed-account tests then exercised outgoing CIDR and country rule
updates: each update closed an existing Wisp stream and rejected a new stream,
and traffic resumed after restoring the original rule file. The country test
blocked AU/CA, covering the selected host's resolved IPv4/IPv6 addresses. A
separate test from i36's public address (104.180.210.36, US in the installed
DB-IP database) added an incoming US login block: login returned 403 despite
forged client-IP headers, while an already signed-in Browser relay still
downloaded an allowed site. Login returned its normal 400 invalid-body response
after restore. Tests used an automatic two-minute conflict-safe recovery timer;
the original policy hash was verified, the timer and temporary helper removed,
and the exact disposable account cleaned up after each run. A login rule does
not revoke an existing session.

### Electronics apps — local work in progress

The requested electronics tools are tracked in `docs/ELECTRONICS_APPS.md` as
separate applications. `apps/system/arduino-simulator` is the first local
implementation: pinned AVR8js and Wokwi Elements, a compiled ATmega328P Blink
HEX and its C/Arduino source examples, a worker per window, pin 13 LED display,
serial output and opening HEX from My files. It does not compile sketches or
simulate analog circuits. Desktop and phone-emulated Chromium tests passed
real firmware-driven LED changes, opening firmware through My files and two
independent windows with one closed. It is not deployed. Pico, writable flash,
analog circuit simulation, PCB design and digital logic apps remain unfinished.
### Browser report relay activation — 2026-10-30

The Browser relay is running the root-owned runtime with manifest SHA-256
`6b2ea6b67591faf490e164dd79b80cabd2fd58f8e13c3f56998dc0947b3516c9`,
source commit `6078c8e18`. Requested reports are enabled on this service;
`dflanag3` is the only configured administrator, in root-owned
`/etc/codi-browser/report-admins.json`. Report data uses the service-owned
0700 `/var/lib/codi-browser-reports` directory and 0600 SQLite database.
No request is active merely because this service is enabled. The separate
continuous server-side access audit remains disabled. The prior unit is at
`/var/backups/codi-browser-relay-before-report-6078.service` for rollback.
After restart, a public challenge advertised report support and a new
disposable registered account passed signed relay admission, HTTPS download,
blacklist and private-address denial, Wisp connection, account-file
write/read/delete and a fresh-context login; the account was removed. The
report workflow passed against a local real Browser and two registered
accounts. The report UI and Browser desktop app are not deployed yet, and a
live end-to-end report and restart recovery test is still required.

### Updated Browser and relay source provision — 2026-10-30

Public `/browser-sources/` now includes the snapshot from commit `2ed6d0259`,
which contains the currently running report-enabled relay and tracked Browser
app source. Its archive SHA-256 is
`49f1c63f6160a58d9d6624d5baa35589fae1a74580f32cbb8883f71f9a203b0b`;
the public download was independently hash-checked. The managed source-route
update and rollback exercise passed all ten site status checks. Generator
SHA-256 is `3ac0cf3bc1dda9063c0cd3494c71d83a706681b7a8cdc682a0d8f77dcace8ff3`,
manifest `a287d968a80cb8387295a4a5fb6a23cb039efc6e127aaebb7e7cb7d699481260`,
and derived Caddy `9db5c7c717501259da4e969c930441bf74f66127ceb0720c03c4c5dc3f4d88d2`.
Index rollback data is `/var/lib/codi-ingress/browser-source-index-2ed-backup.json`.
The Gecko component and LGPL review remains incomplete; source availability
alone is not a finding that the engine's distribution obligations are met.

### Browser font notice — 2026-10-30

The Gecko resource package includes four Liberation Sans fonts. Their
SIL OFL 1.1 notice was missing from the browsable notices and is now appended
to `/browser-sources/emscripten-licenses.txt`, with the index updated. The
notice input is pinned to the exact Firefox checkout's license hash. The
public response matched SHA-256
`4b87b95e8c51dde5861703e11ce57c416f178497fab403b73033f6db48f550ad`.
Previous notices are retained in
`/var/lib/codi-ingress/browser-source-font-notice-backup.json`.
The source notice builder now requires this license explicitly. Link-script
inspection and symbol checks narrowed the LGPL questions but do not complete
the full third-party license review.

### Report-enabled desktop candidate — 2026-10-30

The static candidate `.build/simplified-release-reports-r1` contains the
report-enabled Browser bundle and has cache ID
`5d9f737d4fe4190f4edcd740ab4ac3b2c395a4a683ed23c1072ec438528ecd74`.
The Builder's optional `--desktop-app-source` supplied a reviewed `app.js`
snapshot from commit `2ed6d0259`, preserving the separate uncommitted Crafts
menu work. That file's SHA-256 is
`bc0da0094bc80c1cdd6524a9491b60209449d7fb2d82c7fdf24db646470e85e5`.
An independent Browser-only rebuild matched the candidate's full Browser
catalog entry and bundle SHA-256
`2af8a8f2a644daf6bd7039170ddef2dc93f9799f7c6bdc8238f5506cd97f8079`.
The candidate is not live; engine licensing and live end-to-end tests remain.

### Browser status and window sizing — 2026-10-30

An actual desktop Browser test exposed that `window-content` overrode the
desktop's title-bar height calculation, clipping Browser status and
diagnostics. It also found that navigation left the status on “Loading…”
after the native navigation command returned. The local Browser now respects
the desktop's content height, lets its viewport shrink, and reports
“Navigation requested.” after the command returns; that wording does not
claim the destination has finished loading. Both desktop and phone-emulated
tests now assert that status fits inside the window. The desktop test passed
account-file HTML open, relay request and renewal, visible non-stuck status,
and URL download with server synchronization. The phone-emulated test passed
status visibility, typing and touch scroll. These changes are not live. The
prior report-enabled static candidate is superseded. The replacement
`.build/simplified-release-reports-r2` has cache ID
`8138c0e892580c8aafc3637738b4d9d577898c923e9ceb108f7fd337477d6c27`
and Browser bundle SHA-256
`4b26e64f6b9edf41155cf206c4ee5b24ddf77bfb4011bb552ae6a12185beb9a2`.
The matching source archive from `0488c275e`, SHA-256
`841993d069a9d824942224b2e34012a1dc56ce6c24f3407b920adaa4f2d7e0cd`,
is published at `/browser-sources/` and its public download matched that hash.
The managed hosting change passed a rollback exercise and all ten site status
checks. Hosting generator SHA-256 is
`19b71614139100907f21c6b28383532a163c06aa8b951e5d540e5d241e4c37f6`,
manifest remains `a287d968a80cb8387295a4a5fb6a23cb039efc6e127aaebb7e7cb7d699481260`,
and Caddy SHA-256 is
`40df5f82ebbbf37ccc30d498a43a1a9f2480b120aad61d0f54b93b1affeef789`.
The previous notices are saved under
`/var/lib/codi-ingress/browser-source-index-0488-backup.json`. The prior
generated candidate and independent build were removed.

### Browser policy-denial feedback — local work, 2026-10-30

The existing live relay enforces blocked destinations but reported the same
generic Wisp close reason for a policy block, capacity limit, and network
failure. The local relay now emits Wisp's standard `HostBlocked` (0x48) and
`ConnThrottled` (0x49) reasons; active streams stopped by a new policy also
receive `HostBlocked`. The Browser worker reports these to the window, which
shows a plain message that a site or resource was blocked, or that the
connection limit was reached. A real local Gecko window navigating to
youtube.com displayed the block message. Ten relay tests passed, including
hostname and changed outbound-policy blocks and capacity behavior; report
HTTP and download tests also passed. This change is not live. Its new relay
runtime, Browser bundle and matching source snapshot must be published and
tested on the live path before this feedback can be considered live. They
supersede the earlier desktop candidate. The immutable relay manifest
SHA-256 is `2046bb480628f3124bba74b2cd249b00eee665709b15cc12e1eca7dbd5434cad`,
the desktop cache ID is
`2c386e8748f45b836a070bf336287275ae432b0003f362ad17645574e15e0539`,
and the prepared source archive from `802621ec2` has SHA-256
`128c33ee16a6dde95f5c594b19ef6c8a05cb9b251024e95ac859f888b3a26c90`.
The exact source archive is now public at `/browser-sources/` and its HTTPS
download was hash-checked. The new relay runtime is live and retains the
existing report configuration and private database. A signed disposable
account confirmed Wisp `HostBlocked` for YouTube, and a live temporary
outgoing rule closed an existing stream and denied a new one. The original
policy was restored and checked, the scheduled recovery timer stopped, and
the temporary test account and helper were removed. The Browser desktop UI
is still not deployed, so its user-visible feedback is not live. The previous
relay unit is saved at `/var/backups/codi-browser-relay-before-blocked-802.service`.
Source hosting generator SHA-256 is
`2329d2b8925501ea5b59c9a0182b24db66e076b6abc1d4305ad820da45a4079b`,
Caddy is `887fdcb7da1b2ba05c6d3204fa0c4cf38a8a8d4d4a9743cc3e269116283209c7`,
and notice rollback data is `/var/lib/codi-ingress/browser-source-index-802-backup.json`.

### Browser compiled-component notices — 2026-10-30

The actual Gecko link list contains 1,860 object inputs. Its identified
third-party groups include ICU, Abseil, msgpack, zstd and several media
libraries. The public runtime notice file now includes the exact pinned-source
license files for the named libraries, including the IJG text referenced by
libjpeg-turbo; the existing Gecko page supplies ICU's notice. The downloaded
combined notice SHA-256 is
`4d04c982f8713a75b6c787679e0f93ff7ac076b08c5fd5ce0d82da515bf6d35e`.
The pinned collection and notice-builder tests pass; previous notices remain
in `/var/lib/codi-ingress/browser-source-component-notice-backup.json`. This
does not prove a complete object-level, Rust dependency, or legal audit.

### Browser target-built Rust notices — 2026-10-30

The Gecko target build's Cargo fingerprints identified 477 distinct crate
names, of which 335 match vendored package names. The public runtime notice
file now includes the declared licenses and available top-level notice files
for matching vendored versions. This is a conservative target-build list,
not a claim those crates all survive final linking. There were 38 matching
vendored versions with no separate top-level notice file and 142 unmatched
names including workspace/toolchain crates; these need further review. The
collector and pinned notice-builder tests pass. The public combined file
SHA-256 is `0c225076a90714c0badf93424d3ae6ee8c57d2d773d17af6641af63643cb042a`;
previous notices are saved in
`/var/lib/codi-ingress/browser-source-rust-notice-backup.json`.

### Browser Rust standard library notices — 2026-10-30

A tracked-source scan matched 464 of the 477 target fingerprint names to
Firefox Cargo manifests; the other 13 include Rust standard-library and
compiler crates. It matched 131 names beyond the earlier vendored-package
scan. Some workspace packages omit a license field, so their source still
needs review. The exact build used Rust 1.95.0; its standard-library copyright
and dependency notice is appended unchanged to the public runtime notices.
The public response SHA-256 is
`b1a5cd60fa71ae515da2e05ffb88358b1f2d4925cba2d79ae4ee8b6e6b1eeb6c`.
The pinned notice tests pass, and prior notices are saved in
`/var/lib/codi-ingress/browser-source-rust-stdlib-notice-backup.json`.
This is target-build evidence, not a final-link or complete legal audit.

### Browser workspace headers and Pulse notice — 2026-10-30

The 22 target workspace manifests without a declared license have Mozilla
license headers on all 47 observed tracked Rust source file paths (some paths
overlap between manifests). `audit_workspace_headers.py` reproduces the
check; non-Rust files and final-link inclusion were not established. The
vendored `pulse` and `pulse-ffi` crates refer to a missing ISC license file;
the exact Cargo.lock-pinned upstream `cubeb-pulse-rs` LICENSE was retrieved
and added to the public notices. The combined public response SHA-256 is
`cfec82baaa9cc83eb238288f493d2116a14603c34aadebab15c7796c4d7cd9c3`;
prior notices remain in `/var/lib/codi-ingress/browser-source-pulse-notice-backup.json`.
Notice-generation tests passed. Other attribution and release checks remain.

### Private Browser desktop release staging — 2026-10-30

The tested static candidate with policy feedback is staged privately at
`/srv/codi-connected/simplified/2c386e8748f45b836a070bf336287275ae432b0003f362ad17645574e15e0539`.
All 4,941 cached files and both cache-control files were independently
hash-checked on the server; no account or service state was copied. The
current live desktop route was not changed. The staged candidate's source is
already published, while the remaining attribution review and live desktop
tests must be completed before calling the release ready. The active desktop
is still `bfcccab6fcdfd33221aeb5e57dd59d8eb788217b0c0172bb1cf45b3c533a807b`.

### Browser desktop active — 2026-10-31 UTC

`https://ksu.codes/` now serves Simplified desktop cache
`2c386e8748f45b836a070bf336287275ae432b0003f362ad17645574e15e0539`.
The managed hosting generator SHA-256 remains
`2329d2b8925501ea5b59c9a0182b24db66e076b6abc1d4305ad820da45a4079b`,
manifest is `517ebeb6523eea4c9ff61ee18a84f8e5dce3d81729fe679eda1706f72a94ace3`,
and Caddy is `bc4089a16acfebf62d6249cd9455d26c08f4d21f012e3fd93a0a3db97c2aa393`.
Hosting input snapshots are `/var/backups/webhost-sites/change-20261031T011746938217Z`
and `/var/backups/webhost-sites/change-20261031T011746938685Z`; the previous
desktop release remains `bfcccab6fcdfd33221aeb5e57dd59d8eb788217b0c0172bb1cf45b3c533a807b`.
Use the managed hosting lock and generated validation/apply workflow for rollback.

Fresh real HTTPS Chromium tests with disposable registered accounts passed
Browser launch, visible blocked-site feedback, HTML open from My files, relay
navigation, lease renewal, explicit URL download and server synchronization.
Phone-emulated Chromium passed visible status, typing and touch scrolling.
Those test accounts and their exact files were removed. The separate desktop
prototype and the other hosted sites returned their expected status codes.
These checks do not cover a physical phone, ordinary clicked downloads,
authenticated site downloads, general website compatibility, or audio.
The broader component/license review and live requested-report workflow are
not complete. Existing Linux guest egress is outside the new Browser IP rules.

### Live requested Browser report and restart — 2026-10-31 UTC

`CODI_TEST_REPORT=1 tests/live_browser_relay_account_check.py` used a fresh
registered account and actual live Browser to visit example.com. It checked
that the server held no report for that account before a test request,
created the explicit request through the coordinator as its service account,
observed the signed device report and domain summary, restarted the relay,
and confirmed the summary remained identical. It then removed the request,
its reports, and the disposable account. The relay is active and its report
database passed SQLite `quick_check`. This tests the real client and service
but creates the request as an operator rather than logging into the admin UI;
the admin UI workflow was tested separately in the local two-account fixture.

### Live Browser policy operator — 2026-10-31 UTC

`sudo codi-browser-policy` on box-webhost now manages incoming-login and
outbound IP/country rules, Browser blacklist/whitelist entries, and the
whitelist switch. It uses the protected live relay's pinned validation code,
a per-file lock and atomic validated replacement. It does not enable server
audit or cover Linux guest egress. See `apps/system/browser/docs/LIVE_POLICY.md`
for commands and scope. The installed source at
`/srv/codi-browser/operators/policy-1e7ae703d/manage.py` has SHA-256
`79870a7f49e4c3d1c66f82dcfda217acdb2b02e6bf8a1e6155da5237791ee5ef`;
the root-owned entrypoint is `/usr/local/sbin/codi-browser-policy`. Local
fixture tests passed; the installed operator successfully edited isolated
copies of the live policies, displayed the live rules, rejected an IP literal
as a domain, and left both live policy hashes unchanged. Live rule enforcement
and active-stream changes were tested separately using the guarded fixture.


## Browser and file mirror update

The live Simplified frontend is release `d360a4ef6c221d2f120b20bd1c38e89be100f62a514ff573a3130abe64ff34d8`.
The file mirror stores large browser records as Blobs and checks the server's
file version before downloading again. Local tests verify unchanged files do
not trigger another full download, and external same-size edits are detected.
A live 128 MiB mirror test timed out on its first attempt. A repeat passed
through browser storage, upload, verified server read, deletion, and sign-in
from a fresh browser context. The intermittent timeout remains unexplained.

The live gateway defaults are 50 GiB per account and 200 GiB shared per day;
the per-transfer and 128 MiB file limits remain separate. Gateway release is
`0685f9925f2d00cb2433d6d3d9066ee86da7f901a2c3302e3c1f1e1842ab2152`.
Browser routing and management details are in
`apps/system/browser/docs/LIVE_POLICY.md` and `DOMAIN_REPORTS.md`.

## Embroidery apps live

Release `bc92bb0d2f7f033b868b97d4d04b04204df8d2191d3216681c6f54052990832b`
serves Embroidery Studio and Stitch Converter under Applications → Crafts.
The prior release was `d360a4ef6c221d2f120b20bd1c38e89be100f62a514ff573a3130abe64ff34d8`.
Desktop and phone-sized local and live registered-account checks opened both
apps, generated PES and DST examples, and saved to My files. The live test
account and its files were removed. Physical-machine compatibility and sewing
remain unverified; StitchFoundry is an upstream pre-release.

The first deployment preserved app-builder temporary-directory modes (0700),
which gave the web server 403 responses for app assets. The release directory
permissions were corrected to public read/traverse, after which the live test
passed. `build-simplified-static.py` now normalizes public directory and file
permissions to prevent a repeat. Caddy generator SHA-256 remains
`bb88688bdb94c5921ec08187d4605075772c0187b401e8e33342be19184e60d5`;
manifest is `49c3d119bda77e7bd6fb93c487cf848f13e78a9c75edb47b73ad081f639d58ee`
and Caddy is `f8e953dd50445f2efb417af9290bca0bb7cd96aec70daa4b9ed20c3196468555`.
Hosting rollback snapshots are under `/var/backups/webhost-sites/` as
`change-20261031T014355641269Z` and `change-20261031T014355650311Z`.

The existing Arduino Simulator is also served by the current release under
Applications → Electronics. A live registered test ran its compiled Blink HEX,
observed the simulated LED change, opened firmware from My files, and verified
independent windows; its disposable account and file were removed. Pico remains
separate unfinished development.

A live registered-account mirror test also instrumented two subsequent syncs
of an unchanged file: both used version checks and neither requested a file
read. The disposable test account and its file were removed. Run the check with
`CODI_TEST_NO_REPEAT=1 ../active-system/.venv/bin/python tests/live_browser_relay_account_check.py`.

## Digital Logic and Pico live

Current release `fef98d4b459cf9b6e6e8d86c906143f5bf81d3b6fd404a0a866954851d470175`
adds Digital Logic and Pico Simulator under Applications → Electronics and
keeps open application submenus intact during desktop updates. Existing app
bundles are unchanged. All release files were hash-verified and public asset
permissions checked before activation. Rollback release is
`bc92bb0d2f7f033b868b97d4d04b04204df8d2191d3216681c6f54052990832b`;
hosting snapshots are `change-20261031T015446474999Z` and
`change-20261031T015446476222Z` under `/var/backups/webhost-sites/`.
Generator SHA-256 remains `bb88688bdb94c5921ec08187d4605075772c0187b401e8e33342be19184e60d5`,
manifest is `df3b55c5c353c438cce9137100e5451555d5bf1ebf67270382eff80cd2ababdf`,
and Caddy is `6f7000bafe0f6a0eea0afc54fa3983fbd404ffc4499369dd06e13d77f5c83131`.

Local desktop and phone-sized tests exercised Digital Logic's gate simulation
and actual account save/sync/reopen. Live registered testing repeated the save,
server read and reopen. It supports basic feed-forward gates in JSON, not a
schematic editor, sequential logic or analog circuits. Pico's live Blink test
passed. Its MicroPython save/sync/reload was tested locally using privately
supplied ROM and UF2; neither is distributed. Explicit project saves retain
simulated flash, not CPU state. SSI support is partial. Both test accounts used
on the live site were removed. See each app's README for test scope and terms.

The live Pico Blink and Digital Logic account save/reopen checks also pass in
an emulated phone viewport. Obsolete local generated release candidates were
removed after deployment; source and the live rollback remain. The Raspberry Pi
ROM and MicroPython firmware were not included in Git or the release.

## Circuit Simulator live

Release `a690fd6f65795434dd6e6ce7f44c53627462cfdd0b8dc91581d64c22d3940875`
adds Circuit Simulator (CircuitJS) under Electronics; existing app bundles
are unchanged. It includes the GPL corresponding-source archive and notices.
Local tests exercised the graphical divider at 5 V, editing it to 6.67 V,
account sync, phone-sized reopen and iframe cleanup. Live desktop and
phone-sized checks independently verified the 5 V simulation, source archive,
and server-backed save. Their disposable accounts and files were removed.
This is CircuitJS, not ngspice; complex circuits run on the browser main thread.

The previous release is `fef98d4b459cf9b6e6e8d86c906143f5bf81d3b6fd404a0a866954851d470175`.
Hosting snapshots are `change-20261031T020934080997Z` and
`change-20261031T020934086998Z` under `/var/backups/webhost-sites/`.
Generator SHA-256 remains `bb88688bdb94c5921ec08187d4605075772c0187b401e8e33342be19184e60d5`,
manifest is `0931fc48033969107f3fe18992926845a187f1cff4cecd39b0c14bb24cd5399a`,
and Caddy is `34218a7e4da124cb8085be7c8a109df53240876429dcd79c2440c5c022422f02`.
Two activation attempts with mistyped expected manifest hashes were rejected
before changes; the exact current pin then validated and activated normally.

## Electronics Design live

Release `67f4c5a44ab04a28147a895ec1d52a58fcb1a48dacbd5b24da9a646b4d1f6558`
adds Electronics Design under Electronics; previous app bundles are unchanged.
The editor's WASM was built locally from the pinned source inputs documented in
`apps/system/electronics-design/README.md`; notices are included. Registered
local and live desktop and phone-sized tests opened a project, captured Save As,
synced to the server, closed and reopened. A local 9 MiB project round-tripped;
the 128 MiB limit itself and physical touch were not tested. Use the editor's
Save As / Share and then the host's Save to My files; native Save alone is
transient. The example is not a production-ready board.

Previous release: `a690fd6f65795434dd6e6ce7f44c53627462cfdd0b8dc91581d64c22d3940875`.
Hosting backups: `change-20261031T021402839361Z` and
`change-20261031T021402839858Z` under `/var/backups/webhost-sites/`.
Generator SHA-256 remains `bb88688bdb94c5921ec08187d4605075772c0187b401e8e33342be19184e60d5`,
manifest is `8351825cf04e6b1b1ff0a36fabfb56bb2a6a35aca6180c4884ea55098713e851`,
and Caddy is `7e49a881f9ea0b6d46cc846ce270ec76f1aa996d91973c5513fc03893e014b42`.

## ngspice Circuit Lab research

The separate ngspice Circuit Lab remains unshipped. A clean build from pinned
ngspice 45.2 and wrapper sources passed divider and RC tests and an isolated
account sync and phone-sized reopen. A development-tree test modified and
relinked numparam and reran the solver. The portable corresponding-source,
relink materials and complete release notices are not yet verified. Build and
relink recipes and exact limits are recorded in `apps/system/circuit-lab/README.md`;
research build outputs and test accounts were removed. Live Circuit Simulator
continues to provide the separate CircuitJS engine.

The later ngspice candidate produced a 48,509,541-byte source/relink archive,
SHA-256 `194eb712ba6ad296baff16b1760ceefc67eab828e7df39555cd94125c018915a`.
It passed an independent-directory modified-component relink and the combined
app passed simulation, account sync, phone-sized reopen, and lazy source-link
tests. Two clean builds matched on the same Linux machine. Final distribution
review of source, notices and LGPL relinking sufficiency remains open, so
Circuit Lab is not live. The archive and SDK were generated test artifacts and
removed; the pinned recipes and tests are tracked for rebuilding.

## Signed upload pause handling

The live private-file worker now uses a 60-second idle timeout specifically
for authenticated binary upload metadata and content. Control requests retain
their 5-second timeout; the 900-second overall transfer deadline, transfer
quota, per-use size, and concurrency limits remain. The live worker is
`be4a9ef3a613c2e90517fae427d4d2256b97b74ee2134c10cafe263fc2440eac`,
with previous worker
`0685f9925f2d00cb2433d6d3d9066ee86da7f901a2c3302e3c1f1e1842ab2152`
available for rollback. The journaled code upgrade reported preserved account
and permission bindings. Local tests passed a real signed upload with a
5.2-second pause and a separate bounded idle-timeout case, plus all 18 gateway
HTTP tests. A live signed upload through ksu.codes survived a 5.5-second pause,
read back the exact content, and was removed with its disposable account.
This fixes a confirmed short timeout but does not prove that timeout caused the
previous intermittent 128 MiB failure. Longer upload idle time also means a
stalled authenticated upload can occupy one of the bounded slots longer.

After the upload-idle update, a fresh live 128 MiB browser-mirror upload,
server read with SHA-256 verification, synchronized deletion, and fresh-browser
sign-in all passed. The disposable account was removed. An unchanged-file
sync in the same run again made no redundant file downloads.

## Browser clicked downloads live

Release `f3681cd5867e0f779049812f9fc178db90d4c2f8169699a1d66b1fba69d35919`
adds Gecko clicked downloads to a per-window temporary queue. Users choose
Save to My files to retain one; the account mirror then synchronizes it to the
server. The queue permits three active/waiting files up to 128 MiB each and
warns on reset or close. Browser crashes can still lose temporary downloads.
Existing-name collisions do not overwrite files. The Browser's direct URL
download remains separate and does not share Gecko cookies.

Local real-Gecko desktop and emulated-phone tests passed a cookie-protected
delayed download, explicit save/cancel, server sync, collisions, empty files,
interruption, advertised and streaming size limits, reset, independent windows,
and worker termination. Live fresh-account desktop and emulated-phone tests
clicked a data-URL download and verified the saved server copy; they do not
prove a live third-party authenticated download or physical phone behavior.
The live signed relay, blocked destination, gateway write/read, unchanged-file
sync with zero repeat reads, and fresh-browser sign-in also passed. Disposable
accounts were removed. Source commit `29a71d717` is on box-git.

Public modified source and Mozilla modules are at
`/browser-sources/codi-browser-source-29a71d717.tar.zst`, SHA-256
`f231dfee54279c20c6bca77988b556d6fcad7c8886792eb78c63e1f9c10b680b`;
the source route rollback exercise passed. See Browser's `CLICKED_DOWNLOADS.md`
and `SOURCE_PROVISION.md` for limits and outstanding license-audit scope.
Previous release `67f4c5a44ab04a28147a895ec1d52a58fcb1a48dacbd5b24da9a646b4d1f6558`
is retained. Hosting backups are `change-20261031T031853664991Z` and
`change-20261031T031853665753Z`. Current generator SHA-256 is
`2d04ab00dc0e17003f94155b4f812b640ed2f9ed897e4f3685b8cb2bbbda41cb`,
manifest `1eff3c244aa5e528f0fe91962e835b2e551c77846a44a410d1066d6c606a7137`,
and Caddy `a34f149de23c2c88c61c3999035fb23fef758aca4ae6c33dface3ed75e3ece01`.

## Browser RLBox attribution

The shipped Gecko object's RLBox thread-local implementation includes
vendored RLBox headers. The Firefox license page named RLBox but the combined
notices lacked its exact pinned copyright text, so the Mozilla revision's
`third_party/rlbox/LICENSE` was added to the public combined notices.
The notice builder verifies its exact SHA-256 and has an input-rejection test.
The public notice SHA-256 is
`28b3c6267097ecfa2e40dc56de5715348ca011652a2b26817f7cbba15e2570b7`.
The source index was regenerated and the current source link is correctly
under Source code. Prior public notices were backed up under
`/var/lib/codi-ingress/browser-source-rlbox-notice-backup.json`. This closes
one identified attribution gap, not the full linked-component/legal review.

The next inventory pass found additional linked graphics and utility object
groups, including ANGLE, Skia, Cairo, FreeType, Brotli, HarfBuzz, WOFF2,
Graphite and Expat. Their pinned source licenses and FreeType 2.14.2's
upstream FTL text are now in the combined notice; the public index explicitly
credits FreeType. The generator and its tests verify both new input hashes.
The public combined notice SHA-256 is
`35258b272eca7cb0f23e53c847733c536197ee3ce8884b66d693b425433b6d1a`;
the prior files are in `/var/lib/codi-ingress/browser-source-graphics-notice-backup.json`.
See `SOURCE_PROVISION.md` for reproducible collection and audit limits.

## Identity renewal pin repair

The enabled hourly `codi-ksu-live-root-renew.timer` was repeatedly starting a
job pinned to the old issuer config and native release, so the guarded job
failed with `Managed config pin changed`. The current signed seed then expired
at 2026-10-31 20:00:39 UTC; this was a future expiry at the time of repair.
The issuer was serving normally. A read-only run of the protected operator
using the current config and release hashes validated the installed release
and reported root revision 10, `nextStep: wait`, and no pending journal.

`active-system/scripts/reconcile-browser-renewal-pins.py` took the managed
hosting lock, verified both current pins and the old unit, backed it up to
`/var/backups/codi-renew-before-browser-issuer-r3.service`, validated and
atomically installed the two pin changes, and reloaded systemd. A manual
`systemctl start codi-ksu-live-root-renew.service` then exited successfully
with `not-due`, root revision 10; the hourly timer remains active. A oneshot
unit appears inactive after a successful run, so check its `Result` and
`ExecMainStatus` rather than expecting it to remain running. Actual renewal
at the future due time was not forced or tested in this repair. Subsequent
issuer/config upgrades must reconcile this unit's config and release pins.

## Additional upstream Rust notices

Review of 26 checksum-verified registry crate archives found that 25 had no
root license file; `remove_dir_all` had two using the spelling `LICENCE`,
which the original collection script missed. For crates with an available original GitHub
source revision, 27 license files from 16 pinned revisions were collected,
hash-pinned and appended to the public Browser notices. The pinned source
list and reproducible collector are in `apps/system/browser/docs/` and
`apps/system/browser/tools/`; `prepare_notices.py` requires the exact input.
The public combined notice SHA-256 is
`a817feabfa8bc5cd56dd24619f0c9c3c9688fa58b69694c082c24d615cd37ea7`;
the prior public files are in
`/var/lib/codi-ingress/browser-source-rust-upstream-notice-backup.json`.
Some upstream packages lack separate license files or have unavailable
revisions, and non-GitHub sources were not resolved by this pass. The Rust
target-build set is conservative rather than a final-link inventory.

The registry audit was subsequently made reproducible in
`tools/audit_missing_rust_crates.py`, which verifies every package against the
pinned Cargo lockfile and detects both LICENSE and LICENCE. It caught the
collector's missed `remove_dir_all` files; the collector and public notice
were corrected. The two corrected files match the already published upstream
copies byte for byte. Only that crate's block changed in the combined notice,
whose current public SHA-256 is
`7775f6197a7a14a397ad6180b43b4c553aaacef77ac4e0136a34fc15f3f3f829`.
The prior file set is under
`/var/lib/codi-ingress/browser-source-licence-correction-backup.json`.

A real local Wisp WebSocket test now also exercises DNS rebinding between
streams: an allowed public answer connects using the exact vetted numeric IP,
then private IPv4, mixed public/private IPv6 and mapped IPv4-in-IPv6 answers
are rejected before the connector is called. All 11 Wisp tests passed. The
tested `wisp.py` and `policy.py` SHA-256 values matched the installed live
relay files. This is a local controlled-DNS test, not a claim that a real
external DNS provider performed the rebind during the live test.

## Optional server audit integration — source work in progress

The live Browser policy still has `serverAuditEnabled: false`; no server
metadata ledger was enabled. Review found that the existing `AuditLedger` and
Wisp hooks were not wired into the relay service, so simply turning the flag
on would fail startup rather than enable recording. Source work now adds
private credential/database arguments, constructs the ledger only when the
policy explicitly enables it, and includes its source in exported runtimes.
Local tests verify default-off makes no file, enabled mode requires a private
32-byte Ed25519 credential, and an enabled Wisp stream records metadata but
not payload. The URL downloader now also emits per-hop events for redirects,
completion and policy denials without recording paths or contents. Ledger
integrity is verified on startup. This work is **not deployed or ready to
enable**: protected systemd credential provisioning, operator controls,
end-to-end failure/recovery and live opt-in tests remain. Do not set
`serverAuditEnabled` on the live policy yet: the current live runtime has no
configured audit callback and would reject traffic.

The optional service renderer now adds a private `StateDirectory` and a
systemd `LoadCredential` only in explicit audit mode; the default unit has
neither. A real isolated systemd test found that its per-unit credential is
root-owned mode 0440 with directory/ACL isolation, not mode 0400. The key
validator now permits that layout only at the exact Browser service
credential path and requires root:root ownership and no writable/world bits.
An isolated transient unit using the actual service name and a disposable
key successfully opened and signed the test ledger. A real local process
test also started with audit disabled (no ledger created), enabled it, and
restarted with the same ledger. A local HTTP integration test verified signed
per-hop redirect metadata without paths or file contents. Temporary test key,
unit and database were removed. The live configuration remains off; safe
operator switching and live opt-in/recovery testing are not done.

The local candidate now includes an audit report tool that verifies the
ledger and reports either per-account or aggregate domain totals; it can check
an independently saved head for rollback. Tests cover account scope,
wrong heads, an absent or unrelated database, and a real transient systemd
reporter using a disposable credential. It also includes journaled switch
primitives with local tests for successful change, failed restart rollback,
process interruption and refusal to overwrite an independently changed
policy. The privileged wrapper, protected key provisioning, end-to-end live
recovery, and deployment remain outstanding. The primitive requires its
caller to hold the hosting and policy locks and validate ownership/units.

The source-only runtime candidate built from commit `f4a43b30e` has manifest
`c54118ec1a534860f8293d74cd92dbe0744d31c72fa602f52fef986437ae4b37`.
The exported, pinned process passed both default-off startup and an explicit
enabled startup with a private test key and ledger. It is not installed or
active on box-webhost. Any further source changes require a new candidate and
matching public source provision before activation.

The source-only privileged audit operator is built as a three-file protected
bundle with manifest SHA-256
`55b97370580f079fb0b644323f015d54d36e4767547b9ade1b90069fc20b4fe2`.
It pins the above runtime, validates root-owned operator/runtime content and
service units, holds the hosting and destination-policy locks, and preserves
keys and ledgers when disabling or rolling back. Fixture tests cover key
preservation and refusal of a tampered operator file. A test initially created
Python bytecode in the staged runtime; the verifier correctly rejected the
extra file. The test now disables bytecode, the test-only cache was removed,
and the corrected package check passed. This operator is not installed and
has not been exercised against real service transitions; live audit remains
disabled. The privileged wrapper and actual transition/rollback still require
an isolated installed-systemd exercise before any live switch.

The current rebuilt operator additionally disables Python bytecode before
importing pinned runtime files; its manifest SHA-256 is
`2fe3f429322c16adbe60890aa04ea2c95d67afbd3d94b9a3d4778e73c5615258`.
Its package and tampering checks passed. It supersedes the prior candidate;
the current runtime candidate is unchanged.

An isolated root-owned temporary systemd unit subsequently passed a real
enable transition, automatic rollback after a failed restart, and recovery
after a simulated process interruption; the fixture unit was removed. The
runtime `c54118ec…` and operator `2fe3f429…` have been copied to protected
`/srv/codi-browser/releases/` and `/srv/codi-browser/operators/` paths. The
operator's read-only `status` check passed and reported audit disabled,
no key or ledger, no pending journal, and `serviceMatchesMode: false` because
the live service still runs the previous runtime. Neither candidate has been
activated. A release-matched public source archive, guarded runtime upgrade,
live opt-in and rollback tests, and default-off restoration remain necessary.

The source archive for runtime `c54118ec…` is now public at
`/browser-sources/codi-browser-source-f4a43b30e.tar.zst`, SHA-256
`3e090e5a9508f0ff53aae97791ff21c71dc38afb5d84bc9cc2cc54f304aeb42c`;
its route was rollback-exercised and the public download hash checked. Current
hosting generator SHA-256 is
`29305c1d0d5387886816d156986dc53ad82e1e6b287ad6c7ea8b4b2559a8d7c2`,
manifest remains `1eff3c244aa5e528f0fe91962e835b2e551c77846a44a410d1066d6c606a7137`,
and Caddy SHA-256 is
`5a1052be870c92e98696464174e12f8b5faed66b8dfa535dd22e544a1b5a150f`.
The relay still uses the previous runtime with audit off.

## Optional server audit live, default off

The audit-capable relay runtime `c54118ec1a534860f8293d74cd92dbe0744d31c72fa602f52fef986437ae4b37`
is now live with recording disabled. Its protected operator is
`/srv/codi-browser/operators/ed662839765996e6f5138ddb1eaedce6b2c4f40c2d4ae9ec6e2d4c7a0dc7d374`;
`sudo codi-browser-audit` is the installed entrypoint. The first runtime
rollback exercise hit a readiness race: systemd became active before its Unix
socket. The old unit was restored, its journal recovered, and bounded routed
health retries were added. The second real upgrade/rollback exercise passed,
followed by the guarded upgrade. Previous unit backup is
`/var/backups/codi-browser-relay-before-audit-runtime.service`.

A live timed opt-in with automatic shutoff used a disposable account to test
signed Browser access, direct download, blocked domains and private targets.
The report verified seven signed events; after relay restart the independently
saved head matched. The audit was explicitly disabled, the shutoff timer was
stopped, and the test-only ledger and newly created test key were removed only
after checking the exact expected head, record count, domains, single deleted
test account, owners and file set. Current status reports audit disabled,
matching unit, no transition, no key and no ledger. A new enable creates a
fresh key and ledger; ordinary disable retains them. Later signed-account,
relay, blocked destination, file sync and fresh-login checks passed.

The live destination policy after the toggle is semantically identical to
the tracked default, though formatting changed its SHA-256 to
`31654ffd64073946ba9833a7594bf5fe4ef1f5bf575466e00984a6946f515433`.
The independent `codi-browser-policy` manager now validates against this
runtime using root-owned operator `policy-e36ed9571`, SHA-256
`e36ed957153e4390749c2192a8230f7ea52b24ae8fc44682233167f451e49b43`;
its previous wrapper is backed up at
`/var/backups/codi-browser-policy-before-audit-runtime`. See Browser
`LIVE_POLICY.md` for audit controls, key backup, checkpoint limits, and the
separate Linux guest egress boundary.

## Browser memory-growth fix — local candidate

Real live desktop and phone-sized checks loaded example.com, Grainger, and
McMaster. Grainger returned its own access-restriction page in both tests;
this was not a local blacklist decision. McMaster rendered on the phone-sized
viewport, while the desktop window failed with `Engine buffer outside WASM
memory`. The live example.com page also displayed missing-glyph boxes for
Arabic and CJK text; the currently packaged fonts do not cover those scripts.

The desktop failure was reproduced twice in an isolated preview. In the two
failures the engine had grown shared WASM memory from 536,870,912 bytes to
644,284,416 bytes, while Emscripten's exported typed-array view remained at
the old length; newly allocated frame pointers were valid in the grown memory
but outside that stale view. The local Browser adapter now holds the imported
`WebAssembly.Memory` and reacquires its views whenever its buffer changes.
A real shared-memory growth unit test passes, as do 93 Browser unit tests.
Two concurrent local desktop Browser windows each reloaded McMaster five times
without the prior error. These are limited examples, not a guarantee that all
websites or physical phones work. Deployment and download regressions remain
in progress; this fix is not yet live.

## Browser memory-growth fix — live

Release `0389a65b0a5bf8da3d0c26e714f6a79e05a0ba37d134c07130e54964248c3042`
is now live from source `ee1704dcd`; only the Browser app bundle changed in
the 38-app catalog. Its matching public source archive is
`/browser-sources/codi-browser-source-ee1704dcd.tar.zst`, SHA-256
`0ef62be5518d9cbd01543efd9bacafc22238ac6b4ca7a00719898753cfbab60a`.
Two fresh public desktop sessions and one phone-sized session each navigated
to McMaster five times without the former memory error; screenshots showed
the rendered site. A live phone-sized clicked-download/save/server-copy test
and isolated desktop/phone cookie-protected download regressions passed.
One of three simultaneous test registrations timed out before creating an
account; the same test registered successfully when rerun separately. Its
cause was not established. All test accounts were removed. Phone tests were
emulated; actual Android input and general website compatibility are not proven.

Grainger returned its own access restriction in the earlier test, and the
current fallback fonts do not cover Arabic or CJK characters. Those issues
are not resolved by the memory fix. Server audit remains disabled. Previous
frontend release is `f3681cd5867e0f779049812f9fc178db90d4c2f8169699a1d66b1fba69d35919`;
hosting snapshots are `change-20261031T035715125933Z` and
`change-20261031T035715126409Z`. Current generator SHA-256 is
`3cf1dca82b180122de30fdf44f9751941423281fdfdc5566418826be22525d0e`,
manifest `23203a7bc06b2743978a130e2d9eddf9af1c4eec54c767366fe701602fbee041`,
and Caddy `c1bd4ec92c21f152bb725ccd9c37128710f594974fa6f4dacaeeab4cff14142a`.

## Browser language-font candidate — local only

The candidate Browser now stages unmodified Noto Arabic and CJK fonts before
Gecko initializes, with SHA-256 integrity checks and bundled SIL OFL notices.
`apps/system/browser/tools/prepare_fonts.py` reproduces the exact font assets
from verified Ubuntu packages or matching installed fonts; the font binaries
are generated inputs, excluded from Git. This adds about 19 MiB per initial
Browser load. The desktop and phone-sized isolated Browser rendered Arabic and
Chinese on example.com rather than missing-glyph boxes; the phone-sized site
compatibility run also visited Grainger and McMaster. Browser offline tests
passed with the project Python environment. This candidate is not yet live;
prepare its corresponding source archive, perform release/hosting activation
and public regression before announcing it. Physical phones and full language
coverage are not verified. The previously documented live release is unchanged.

## Voice and keyboard menu controls — live

Simplified frontend release `affe246ba843cc62a41a77557171e254db33379ea0a24414e381d9b6dbb130e4` serves desktop source `ef070123a`. The microphone overlay starts hidden on desktop and visible on compact/touch layouts. Applications → System Tools → Voice input toggles it; Keyboard lock toggles the on-screen keyboard hint, with status feedback. The overlay contains no keyboard button. Desktop keyboard mode initially permits typing; the previous voice-mode default remains on compact screens. Desktop and emulated phone-sized tests passed both locally and on the public site; two disposable public accounts were removed. No physical-phone test was performed. All 5,462 release files passed hash verification before activation. This release retains the previously live Browser bundle: the font candidate above remains local only.

Hosting generator remains `3cf1dca82b180122de30fdf44f9751941423281fdfdc5566418826be22525d0e`; manifest `d05ef60376f13a66485f96a6822ca35d19b9a1d4b08ccfca51a44a15548b08a8`; Caddy `44be733ea39f778de37eb32ecb5c03735b4607dea6e5ed843087c5f684353001`. Previous release is `0389a65b0a5bf8da3d0c26e714f6a79e05a0ba37d134c07130e54964248c3042`; hosting backups `change-20261031T040729846308Z` and `change-20261031T040729846712Z`.

## Browser Arabic and CJK fonts — live

Simplified release `d20562ff8056d481ae9e7aadc4c5738a961179d01c51855be2e2afa388472be0` now serves Browser bundle `72d5f07565f4b0118deb99e722089d3de58bc6e9c6acbc6cbbd981c74848adb6` with verified Noto Arabic and CJK fonts. The runtime fetches and validates them only when Browser starts; they add approximately 19 MiB to the first load. Desktop and isolated phone-sized live example.com checks displayed readable Arabic and Chinese; a live phone-sized clicked download saved to My files and its server copy. The website compatibility run also visited Grainger and McMaster, but individual website compatibility is not guaranteed. Four disposable registered test accounts were removed. Phone testing was emulated, not physical. All 5,466 release assets passed checksum verification before activation. No backend or Browser relay policy changed.

The exact Browser source snapshot is published and indexed as `/browser-sources/codi-browser-source-f70a64aa3.tar.zst`, SHA-256 `1772fa4cc0e5ec205a163b9e6467ba18ffabf782e6c3a38f62316e9ad84f520d`. The host source-allowlist transition passed rollback exercise and all ten site health checks. The new source index SHA-256 is `ec1a78e44a50090d1f1eb98f02a5d59985fa7541537793f044bb0b757721c888`, notice-manifest SHA-256 `9a32b0901ea603c82bba5da24e598d4bf14b3f2eb7f00432bb7b8c2a7e66500a`. Generator SHA-256 `fef25364c7c5c2796e105c5379401c5681e45d5792448f317973619bbc49da7a`, hosting manifest `18a32de48f45a2584c334d37188a0d1dbe8351a4385c3ce1195e12dbfbd4722b`, Caddy `637f68109e7324fb8aad44b2cbe2adfa0d56d27a73f4e0e2fad8a66a85255aca`. Previous frontend `affe246ba843cc62a41a77557171e254db33379ea0a24414e381d9b6dbb130e4`; hosting backups `change-20261031T041104276143Z` and `change-20261031T041104276554Z`. The linked-component license inventory remains qualified as documented in Browser source provision.

## Live report administrator interface check

A disposable registered account was temporarily added to the report administrator list by `tests/live-browser-report-admin-guard.py`, whose root-only journal stores the exact original administrator configuration and allows guarded restoration. A fresh live desktop Browser recorded example.com locally, used the real administrator UI to request a report, and displayed its signed domain total. The guard removed requests belonging only to that account, restored the exact original administrator list, restarted the relay, and left no pending journal; the test account was removed. The first attempt encountered a transient 502 because the service reported active before its Unix socket accepted connections; the test guard now waits for actual socket readiness. This test did not use the real administrator's credentials and did not establish physical-phone behavior. Server-side traffic audit remains separately disabled.

## Beta Help text — live

Help now states that this is a beta service and links to `dflanag3@students.kennesaw.edu`; it retains the explanation that Linux terminal files are temporary and separate from account files. The former Files/Text Editor guidance was removed. Release `c1acaebb41326ea77d0ea0e7beaae01213454d1ab72c5aa62d3bc840717fccc0` contains Help source `9bd6227cd`; desktop and phone-sized live Help checks passed, and their disposable accounts were removed. Previous release `d20562ff8056d481ae9e7aadc4c5738a961179d01c51855be2e2afa388472be0`; hosting backups `change-20261031T041836425960Z` and `change-20261031T041836426399Z`. Generator SHA-256 `fef25364c7c5c2796e105c5379401c5681e45d5792448f317973619bbc49da7a`, manifest `c4c6246aba67b0f44adedb6d556a4ba136c9acd1d079185ae0b978c159ebbb6a`, Caddy `7c373d279c7f5f35ab099ed7ec9bcae94b2fd793726c996b4a4b3968a73b9c28`.

## Browser relay recovery message — live

Simplified release `6f94f5df3bcd9ca43cbbdd65544080e357e40d4489ec7ecb2b2f35d081157086` includes Browser relay client source `808fac040`. HTTP 502, 503 and 504 now say the Browser network is temporarily unavailable and instruct users to select Reset engine; ordinary policy denials retain their own messages. Local simulated-outage and real live tests passed: the live relay was intentionally stopped, a registered Browser displayed the message, the relay was started, and Reset engine reconnected. The test account was removed and relay health was verified. The source archive `/browser-sources/codi-browser-source-808fac040.tar.zst`, SHA-256 `8a5d4ee98efd14272379a54665dce2c3a21fd92aff4871281ab2ff674b4a4249`, is publicly indexed; source-route rollback was exercised and ten sites were checked. Before activation all 5,466 release assets were verified. Generator SHA-256 `1e3ca517ece6a2c9617f8a4728d24bf7605dbc805de23a2e2912e833c7a189ef`, hosting manifest `e0a7c48bec1a5495742514d5120f5ebcb6432fef91265f9df8cea55f97329a4a`, Caddy `48f77ec2a65f828c0eaea9d23d46df0087816396e6bf094babf6c73c38d571a7`; source-index SHA-256 `9831f53993bab0c241f2bc55506dbc225c44ca2ed2e21c4fa73e820529d076b9`, notice manifest `da1d21e5942c15408e34e7ed00f79009681714c88dc49ab035c894128fb35000`. Prior frontend `c1acaebb41326ea77d0ea0e7beaae01213454d1ab72c5aa62d3bc840717fccc0`; hosting snapshots `change-20261031T042054042156Z` and `change-20261031T042054042570Z`.

## Browser svg_fmt notice evidence

The previously unavailable `svg_fmt 0.4.1` package VCS revision remains unavailable, but the vendored crate's three Rust files and README match upstream `nical/rust_debug` commit `492600cac47f64bcadaf9ad037ed64c5fecc8e63` byte for byte; the original Cargo manifest differs only in version 0.4.0 versus 0.4.1, with the same author, repository and MIT/Apache-2.0 declaration. `apps/system/browser/tools/audit_svg_fmt.py` verifies the pinned lock checksum, vendored hashes and source comparison. The historical tree's MIT LICENSE was appended to the public combined notices with an explicit source-match qualification. The matching upstream collection and preparation scripts were updated; all 84 JS and 33 Python Browser offline checks pass. Public notice SHA-256 is `c2717cef7dd3d8485cd4ddfa39101b4ae893353cd63240d0078085b47bc9b05c`, and notice-manifest SHA-256 is `6fc94a25b454dccff8eb9af32f03eb15f6a376d60f8bad486ae8462689ee03e7`. The remaining uncertain Rust and final-link license inventory is not claimed resolved. Frontend and relay releases were unchanged.

## Browser enum-map notices

The exact `enum-map 2.7.3` Codeberg revision contains MIT and Apache-2.0 texts under `LICENSES/`, which the earlier GitHub-only upstream scan did not collect. The live combined Browser notice now includes both exact hash-checked texts and the distinct SPDX copyright lines from the Firefox-vendored crate; the MIT text itself uses placeholder copyright fields. `collect_enum_map_notices.py` reproduces the input from the pinned Firefox checkout and upstream revision. `prepare_notices.py` now requires it and includes the two newer Browser source archives in its generated index. The full combined notice was rebuilt from pinned inputs and matched the public file byte for byte; the notice test and 84 JS/33 Python Browser offline checks passed. Public combined notice SHA-256 `fbca71d13f022e85945e762d7cb5a9d9939ac7b25cbf803b0b1a24759b5d8329`, notice-manifest `2bbc58cc430284b074c112c8cf758c20f18390981500b79857dcf8eb17274916`. Other license and final-link uncertainties remain.

## Browser HTML import size — live

The Browser's former 2 MiB HTML file cap conflicted with the desktop's 128 MiB file limit. Browser source `1573b1ffc` now accepts HTML up to 128 MiB, passes input as a transferable byte buffer instead of converting and copying a large JavaScript string, and bounds the temporary per-window imported-page history at 256 MiB. It preserves imported page files for back/forward navigation until that budget is reached or the engine is reset. The existing My files mirror returns independent bytes; a partial view is copied before transfer to avoid detaching unrelated data. Large HTML still requires substantial device memory.

Live frontend `3b1012207d7b545be3c90a7ea3c85962ebf51cff5f326621e155196ae8ce95be` serves Browser bundle `09a8794331c71e52b5fd483ee0bd6dcb3e19753f844161ae3a6ba7838d0ae29e`. Actual local and live Gecko tests rendered a 128 MiB uploaded document, rejected 128 MiB plus one byte, and opened a 3 MiB file through My files; the account copy was still readable afterward. Live test data/account were removed. The Browser suite passed 85 JavaScript and 33 Python tests. Physical mobile behavior at 128 MiB has not been tested. Source snapshot `/browser-sources/codi-browser-source-1573b1ffc.tar.zst`, SHA-256 `4f376d5619d916adf902c7818bc2f8a577c2849a830db27790aa045d00f3f4a5`, is published and indexed; source route rollback was exercised and ten sites checked. All 5,466 release files were hash-verified before activation. Prior frontend is `6f94f5df3bcd9ca43cbbdd65544080e357e40d4489ec7ecb2b2f35d081157086`; hosting backups `change-20261031T043007806754Z` and `change-20261031T043007807176Z`. Current generator `f01b3fb88a37f15e130ce18a4afeabf785a59c3d76512ea558e344442aeb4dc6`, manifest `dce410e29dcc54ba74c945fa31ea289f08cf4a7605ffc1e6d9e2c6b43a9da0db`, Caddy `622280712346df6e8935f8d7bb0279ff214fda8eba0cf05ade8aefe14675dd8c`; source-index `7a63f2c2eb18b6bca3509aaf7a13059a7346b6cc492a2edfb04a814cbb1db5f7`, notice-manifest `e38ef23ff040349dca5170d5b994c74d47d32ef6cc9be234b49e863a388bd020`.

## Browser URL download memory — live

Simplified frontend `7b5c760dc28cf7fb58fe4d735a45a80810d8bd765483c779c976d65c546fd68f` uses relay-client source `b6b5d43e2`. For the relay's normal Content-Length response the Browser allocates one bounded destination buffer and writes incoming chunks into it, avoiding the previous retained-chunks plus second full-size buffer. Missing Content-Length still uses a bounded chunk fallback. It rejects invalid, oversized, shorter or longer responses and cancels a stream on error. This is a client-side memory improvement; the server continues its existing chunked response and private temporary-file fetch. Unit tests covered chunk boundaries, bad and missing lengths, cancellation, and an exact 128 MiB generated stream. Actual live desktop and phone-sized UI tests fetched example.com through the authenticated relay, saved it to My files, verified the server copy and removed the test files/accounts. A live 128 MiB remote URL transfer and a physical phone were not tested. Existing direct signed relay, public destination, blacklist and private-address checks also passed with the candidate source.

The exact source archive `/browser-sources/codi-browser-source-b6b5d43e2.tar.zst`, SHA-256 `574d6652461794e99cb746e90da5c50b168283e5e12b6cf2ab27f5851a9cb999`, is indexed and publicly verified; the source-route rollback exercise passed all ten site checks. All 5,466 static release files were hash-verified. Current generator SHA-256 `54530be6de2bde410ddfd3fb7930c0fff25b4bd2b926150cf5ebc9cdc2db2f74`, manifest `793c2f272ed5e1c4a3cdc237cc0b82b60b6e25ede6103a29a7678da3bcffe878`, Caddy `8f5c681627db9c12ac9b8821c12d649df15c67b557567fc872cf7a396bca21c6`, source-index `fc0511bd255a3f41f6273398b0d6e3fc85e7492a50d8b41ce2bb6580661b8476`, notice-manifest `79ccef204c0ffee3515bc3a6c631ffe68616fdf0219877625bf831db30ec2e45`. Previous frontend `3b1012207d7b545be3c90a7ea3c85962ebf51cff5f326621e155196ae8ce95be`; hosting snapshots `change-20261031T043257793819Z` and `change-20261031T043257794241Z`.

## Live 128 MiB remote download and clear size error

A temporary sparse fixture served from i36's public Ethernet address through a temporary `104-180-210-36.nip.io` Caddy route exercised the real signed Browser relay and account file service. A file of exactly 128 MiB reached My files and synchronized; browser and server SHA-256 both matched `254bcc3fc4f27172636df4bf32de9f107f620d559b20d760197e452b97453917`. A 128 MiB + 1 byte file was rejected, but initially gave only a generic network-policy error. The new typed size exception returns HTTP 413 with the bounded message `Download is larger than 128 MiB.`; other denial details remain generic. Local audit HTTP tests, 85 Browser JS/33 Python tests and 32 authorization checks passed. After deployment the live end-to-end 128 MiB, checksum, deletion and explicit over-limit-message checks all passed again. Disposable accounts and fixtures were removed; i36's original Caddy configuration was restored and its IP-echo endpoint checked. i34 and i35 were unreachable during this test; i36 remained online.

Relay runtime `7a046ff7b5f37d64cd8c921a9e429c268a8b99c121df4417d0cde020764763eb` from `1f6f3c159` is active; the guarded upgrade was rollback-exercised, with prior unit at `/var/backups/codi-browser-relay-before-size-runtime.service`. Audit and policy operator pins were updated to audit operator `0c1195dca65652181c0a32d4e6932e95de8903a97d0999f09b71105a73b9f19b` and policy operator `policy-ccb023f08`; both commands passed live status/read checks and audit remains disabled. The registered relay, HTTPS download, blacklist, private addresses and file-gateway regression passed on the new runtime. Source archive `/browser-sources/codi-browser-source-1f6f3c159.tar.zst` SHA-256 `e9dd5610d383abc8619c989b69dd3e0b470c1f403bbc5f3455fd97b4608c8fb9` is published and indexed after a source-route rollback exercise. Current host generator `8423607ec727d587a2140ca9e0157c982f1b38837496ffa48bdfb6c314444a45`, manifest `793c2f272ed5e1c4a3cdc237cc0b82b60b6e25ede6103a29a7678da3bcffe878`, Caddy `c3de6b467defabc6530ce349023ceba4fd1194d5aee02840d5bc2f6139d38d1d`, source index `b82a6f1c5c5e104a2d873a0836d9d4b3e46a6f281e4fa8078611135f7161fffe`, notice manifest `d90b13a3239ca8da1dbd3450d14f02ff177a9b7e90949751db8947b14f238616`. The website frontend remained `7b5c760dc28cf7fb58fe4d735a45a80810d8bd765483c779c976d65c546fd68f`.

## Slow Browser URL transfers — live, Moonpie tested

A prior server total timeout of 60 seconds and client timeout of 65 seconds could terminate valid downloads on slow links. Relay source `9fe78a273` now allows up to 30 minutes for each upstream fetch, with a 10-second connection timeout, 60-second read-idle timeout, 128 MiB limit, renewed account lease checks, unchanged destination policy and existing per-user/global connection limits. The browser's full request timeout is 35 minutes. Closing the Browser or losing its relay authorization aborts in-flight URL download fetches; an actual local desktop test confirmed close-triggered cancellation. Browser local tests passed 85 JS/34 Python checks plus stream and relay tests.

A fresh headless Chromium session on Moonpie (`maint@100.105.243.29`, pinned SSH host key, separate public network) loaded the live Browser. An i36 temporary fixture streamed 71 KiB over 70.8 seconds, beyond both old cutoffs. The UI saved it to My files; browser and server hashes matched, then the file and disposable account were deleted. i36's temporary Caddy route/service and Moonpie's isolated browser processes were stopped; i36's original Caddy route was restored and its endpoint verified. The Moonpie machine has roughly 2 GiB RAM; the Browser process peaked around 1.5 GiB during startup, so very low-memory devices remain a real limitation. This was one slow URL test, not a 30-minute or physical-phone qualification.

Live frontend `c53ab4c92df70ccba190b66dcaeb79472ab091e8a285df5dfb585291c1b5d118`; relay runtime `edfd7db342c856c66bf8a19fa50593aa3c08a7498be584d8fca34b86421b71ca`. The relay runtime upgrade and rollback were exercised; old unit backup `/var/backups/codi-browser-relay-before-slow-runtime.service`. Audit operator `d6d78b9eaf47258358511b562d70750936b82e2ff7d14145123f5a6e3c6ec49d` and policy operator `policy-a80a78e35` were repointed and live status/read checks passed. Server audit remains off. Signed relay, blacklist, private address denial and account-file regression passed on the live runtime. Browser source archive `/browser-sources/codi-browser-source-9fe78a273.tar.zst`, SHA-256 `eb1405b13bc172920170259ee87e59594b977ea2498fa3daa08ec705b2fa627f`, was indexed after the source-route rollback exercise; ten sites were checked and 5,466 release files were hash-verified. Previous frontend `7b5c760dc28cf7fb58fe4d735a45a80810d8bd765483c779c976d65c546fd68f`; hosting snapshots `change-20261031T044505798587Z` and `change-20261031T044505798999Z`. Generator `22e8ceb89f38aecb62f153311e31be13bc62f07bebdf4d0d420e5add661b8cfd`, manifest `9bf90f3a73822963631ae6257f70bc84474257d6304392dfb552111d156bad7e`, Caddy `efcbe83711309a91bc26381b500d8f411bf67ecc72c85d3069bff95fec5592a8`, source-index `d5ccdfbda943a016b40aa9603c41d0b3f69213468ab06a8969d4d634a52520c3`, notice-manifest `e08a14c3d19486f5335fd4f404c4927173d844a496617425dc67c9d53f205e55`.

## Moonpie Browser memory experiment

On Moonpie (about 2 GiB RAM), the live Gecko glue prestarts 20 pthread workers and imports a WebAssembly memory whose binary minimum is 8,192 pages (512 MiB). A temporary isolated candidate changed only the generated glue's prestarted worker count from 20 to 8; Emscripten's non-strict pool can grow on demand. With fresh headless Chromium runs on the same machine, the largest Chrome process at Browser readiness was approximately 1,463 MiB RSS for the live 20-worker build versus 1,472 MiB for the 8-worker candidate; after loading example.com the respective largest-process samples were approximately 1,081 and 1,100 MiB. These are individual RSS snapshots, not peaks or unique-process/PSS totals, and the live and isolated candidates used different origins and cache state; this does not establish a statistically meaningful difference. The smaller pool did not show a useful memory improvement and was not deployed. Chromium emitted D-Bus service-enumeration warnings in both headless runs; both Browser windows reached ready and navigated. Disposable accounts and candidate files/processes were removed. The minimum 512 MiB imported memory is encoded in the existing WASM module; lowering it would require a different engine build and qualification, not merely changing a runtime option.

## Lower Gecko initial-memory experiment

A separate r730 build linked the existing Gecko engine with 256 MiB instead of 512 MiB initial WebAssembly memory and passed local real-worker 128 MiB HTML, over-limit, My files, signed relay/download and five-navigation McMaster checks. Moonpie started it and loaded a page. The candidate grew to about 455 MiB WebAssembly memory by the first native sample; both the 256 and 512 MiB engines grew to about 2 GiB of WebAssembly address space in the artificial 128 MiB HTML test. These buffer sizes are not RSS. One Moonpie largest-process RSS snapshot was lower at startup for the candidate but similar after loading a page; differing origins/cache and single samples make that inconclusive. No engine was deployed. The first build attempt failed due to Node missing from PATH; the isolated retry succeeded. Reproduction details, hashes, and limitations are in `apps/system/browser/docs/MEMORY_EXPERIMENT.md`. Temporary candidate builds were removed; the original engine source and live release were not changed.
### Browser relay IPv6 transition-address protection — 2026-10-31 UTC

Relay runtime `d022d596bb2ab2d0fca8c4633b552f75b03b7483f72703886162c582ff646353`
from source `3a82d4665221beeb2745f16674479f82b1602d84` is active. Its
address validator rejects IPv4-mapped IPv6, well-known and local-use NAT64,
6to4 and Teredo ranges to prevent encoded destinations evading IPv4 rules.
Ordinary public IPv6 remains accepted. A network-specific NAT64 prefix cannot
be identified automatically and requires a separate network rule. Unit tests
and a real local Wisp session covered denial; the installed policy was checked
directly on box-webhost. The live registered-account test passed signed relay,
public download, blacklist, private-address denials, Wisp, file write/read/
delete and fresh-context sign-in; the disposable account was removed. This
does not claim a live end-to-end DNS translation test.

The guarded upgrade and rollback were exercised; old unit backup is
`/var/backups/codi-browser-relay-before-transition-runtime.service`. The
active unit SHA-256 is `4b1efe74f85f08cc97e3e50033bcc6cbb6dfa1ba49ac8ac125c9a88279ae10f6`.
Audit operator `7849f5502227f8a62b93d486ee8ba9cc1ef99fa934c878b42329604813ded935`
and policy operator `policy-17d95b771` now point to the new runtime. Audit
status confirms disabled, matching service, no key or ledger; both access
lists remain empty. The previous public Browser source archive predates this
relay-only patch; update the source index before treating distribution
provisions for the new source as fully reviewed.

The update is now published: `/browser-sources/codi-browser-source-3a82d4665.tar.zst`
has SHA-256 `e908debde58ac8280f4768593c73ba7099bf6bde3ca9365017a4b83aa2e1db39`.
An HTTPS download was hash-checked, and the archived relay policy matches the
deployed source commit. The managed hosting route rollback exercise passed;
the ten site checks were unchanged. Current generator SHA-256 is
`028554374cda0aebfb0c399ab9c473e88b45f69670dc03d06aeb8e081be3431c`,
manifest `9bf90f3a73822963631ae6257f70bc84474257d6304392dfb552111d156bad7e`,
Caddy `329297a7963bca9e9b8ed3d6635c1a915c959a01881aeef88175f8a5d67453c3`,
source index `64e06a7aed14a64f0a56d4e4f2e8dfc4eb98932c0aaf03204d5a9f4490227edd`,
and notice manifest `6285a85f3f8213064f38bb85c859f357e1586b17fdab634f281a859cd5ba15f4`.
The prior index is backed up at `/var/lib/codi-ingress/browser-source-index-3a82-backup.json`.
The previously documented uncertainty about the exact final-link license
inventory remains; publication of this source snapshot does not resolve it.

### Signed-in Browser source access — 2026-10-31 UTC

The public `/browser-sources` path and its files now return 401 with a sign-in
instruction. Signed-in users open Browser and choose **Licenses & source**;
the link uses the Browser relay's short-lived, registered-account lease and
path-scoped HttpOnly cookie. Closing Browser or losing that lease can end source
access; reopen Browser to obtain a new link. Public source paths are no longer
usable for unauthenticated automation or as permanent distribution links.
The protected source index and range download passed with a real disposable
account; missing cookies, unlisted files, and an anonymous lease are rejected.
The live UI test opened the link and verified the index. The test account was
removed. Source recipients still have access to notices and source; the wider
licensing inventory remains under review.

Frontend `c538220f32e70e55616f423e10d8e51af9bbf95b82d3bd510d64a29706feef03`,
Browser bundle `27c53dde04fd16189bcea2e8e56fa38881a1cd0cde2e6e09945dac8febf1f49a`,
and relay `953a58dc68dde9f1c988fa18857ea344347508f7e07e6c508eb256245e20764a`
are active. The relay rollback was exercised; the previous unit is at
`/var/backups/codi-browser-relay-before-source-auth-runtime.service`. Audit is
disabled, and audit operator `d4919a4b70b077b93037e1a4a4020d5a9c2056f653410ff2d8ab7fea54cb3aa6`
and policy operator `policy-8874c0118` point to the new relay. Hosting generator
SHA-256 `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`,
manifest `6945436b3856931831a757768c6a02d5222eb8d111136a95e4ce7556826ce65e`,
and Caddy `b28129f67e7a0c2ee50719bd1f87df300ce00248c856627f33a951348fa76731`.
Hosting rollback inputs are `/var/backups/webhost-sites/change-20261031T051342536271Z`
and `/var/backups/webhost-sites/change-20261031T051342536750Z`.

The first frontend staging run left the new app bundle directory mode 0700,
causing a 403 until corrected to public-readable modes. The staging script now
normalizes the copied bundle's permissions. A fresh public test after correction
passed; the exact reported module URL with `?retry=14` returned 200. Old tabs
that cached the failure may need a page refresh. Source-only scripts and tests
are backed up separately; unrelated guest SSH work remains untouched.

The authenticated index now includes `codi-browser-source-ed78ff4b3.tar.zst`,
SHA-256 `0b6f94ae5573bb80d430085cdad66bb3720fdb63d8e5883166412f5219b34139`,
covering the deployed protected-source implementation. The Firefox notice's
old absolute public link now points back to the protected index. A fresh real
registered-session test verified the UI, index, notice link, both source range
downloads and refusal without the session. Current source index SHA-256 is
`81955daf2abf8e4ce82743b5278d40862afd75bea462b251a9b5f720d5f1e614`,
Firefox notice `863ab7630592181f9c16be9f509cbc0b859c56124af4711d8a519c6b4c79fa0e`,
and notice manifest `b149d4c620611e8284a0920c5cc85ea69ce28a61bb3ac0e5ea0a2233c7c391dd`.
The prior files are backed up at `/var/lib/codi-ingress/browser-source-index-ed78-backup.json`.

The link input list and generated unified source identify Firefox's bundled
Content Analysis SDK. Its exact pinned license was added to the authenticated
combined notice; the registered live test reads it. Combined notice SHA-256
`ee553fd12a0e8ef825cae8661f19c86c6f15e83dbf0592caf8b5c249eeab7c01`,
notice manifest `1230180107f7157ba7b2be53d883c5a334d5057506d5e75019eaacb671c8e3a3`.
The previous files are at `/var/lib/codi-ingress/browser-content-sdk-notice-backup.json`.
The wider final-link license inventory remains incomplete.

A fresh live desktop site check rendered the example.com reference page and
the McMaster-Carr catalog. Grainger displayed its own “Access is temporarily
restricted” page; the reason for that site's response is not established.
The script checks engine failure status and saves screenshots for inspection;
it does not automatically establish that arbitrary sites are usable. The
disposable account was removed. `apps/system/browser/docs/TEST_STATUS.md`
now distinguishes current live evidence from its original source-only report.

The Browser's persistent “Navigation requested” message confirms only that
the engine accepted the command. The native control interface exposes the URL
and history state but no verified load-completion or HTTP-status signal. Avoid
turning this into a “loaded successfully” claim based solely on a changed URL
or painted frame; improving it requires an engine progress interface and
qualification of the resulting engine build.

An isolated native candidate compiled and linked with
`nsIWebProgress::GetIsLoadingDocument` exposed in the status JSON. In a real
local Gecko/Wisp fixture, the HTTP server confirmed receiving a request and
held its response for eight seconds; one-second status samples remained
`loading: false`. This candidate did not meet the intended loading-state test
and was not deployed. Its experimental WASM SHA-256 was
`3c3328968f0408977666e39f9f11fb3d46975c871ed400ce2dcd530a95e9665c`;
the live engine remains unchanged. Investigate a progress listener or another
authoritative signal before presenting a completion status. The first fixture
attempt also used a directory URL that the test server refused; it was rerun
against `/demo/index.html` before making the observation above.

A follow-up debug progress-listener candidate observed a stop event associated
with a delayed successful request after the response, and a nonzero result for
a blocked request. An HTTP 404 returned a zero Gecko network result, confirming
that network completion is not HTTP success. Rapid start/stop events also
occurred between status polls. It remains unshipped; source patch, test scope,
privacy caveat and remaining work are in `apps/system/browser/experiments/`.

The subsequent unshipped HTTP-channel candidate distinguished local 200,
404 and a redirect to 404; a zero Gecko network result alone still does not
mean HTTP success. A ten-second delayed-response fixture also demonstrated that
the **shipping** engine's Stop button remained queued after four seconds. Its
native `xul_load` spins until an interactive document while the worker serializes
commands, so cancellation needs a coordinated worker/native solution. The
prototype and remaining security, lifecycle and navigation tests are documented
in `apps/system/browser/experiments/`. Live source and engine are unchanged.

An isolated Stop prototype adds a matched worker/mailbox atomic signal and a
native event-loop check. Three delayed-response runs completed Stop in 68–85 ms;
immediate Stop and later navigation passed, and a two-window fixture showed
the other window remained usable. The three source patches and reproducible
local-only tests are retained, but the prototype is not deployed: ABI pairing,
build/source integration, idle-event-loop, overlapping-command, lifecycle,
phone and failure tests remain. The live Stop limitation still applies.

The pinned live WASM's name subsection has 367,777 named functions; a
reproducible scan found references to `svg_fmt::`, `seahash::`, `app_units::`
and `content_analysis::sdk::`. These may be type references, not a complete
component inventory. Exact Firefox-vendored SeaHash 4.1.0 package metadata,
which declares MIT and lists its authors, was added to the authenticated
combined notice; its exact upstream release has no separate license file.
The live registered-account test read the addition. Combined notice SHA-256
`3f2781508e089b26b8c9af60f0820bd8085aaa9bb9d77d4c21aef852266c519a`,
notice manifest `6a30ebc4b64a65acb01ca5345f677567d2da5769954110cca73ff237fb27f6e6`;
prior files are at `/var/lib/codi-ingress/browser-seahash-metadata-notice-backup.json`.

### Browser rule changes during connection setup — 2026-10-31 UTC

Relay `af8d81daf6fdda84d9b563ce6885f862a4d68c0a55bea194d0c9360c47b1092e`
from source `933db11eaef2b2d1a75630ee13af3f81888b4738` is live. It rechecks
current domain and network rules after DNS, immediately before Wisp connection
attempts, and after a connection completes; if blocked after connecting it
closes the socket before forwarding Wisp payload. Explicit downloads recheck
after DNS and before processing a response. Requests or TCP attempts already
sent cannot be retracted. Deterministic local tests cover rules changing while
DNS or a Wisp connect waits. The live registered-account suite passed, including
source access, outbound policy changes stopping an existing stream, denial of a
new stream, and access after restoration. Its first policy test attempt could
not start because the temporary guard had been cleaned up; the guard was
restored for the successful rerun, the test rule restored, its scheduled
timer stopped, and the guard removed. Audit remains disabled. The protected
source index still needs the new `933db11ea` source snapshot.

That snapshot is now listed on the authenticated source page as
`codi-browser-source-933db11ea.tar.zst`, SHA-256
`86a7231825d85de9199d5117ffe12d4f18f941161f75ad7351f4df00d0169836`.
A registered live session downloaded the complete file and verified its hash;
the test account was removed. The source index and manifest were regenerated
from the pinned notice inputs and now match the generator byte for byte.
Index SHA-256 `5aece1521b25cc96606d7805b0fd9836f37e55f043f1459aae7386c0b279d939`;
manifest `1cd10b58626614a584ebdc74e539ac7653fac56e1953c00a36a424bdd822a500`.
The prior files are at `/var/lib/codi-ingress/browser-source-reproducible-index-backup.json`.

Relay rollback was exercised; previous unit is
`/var/backups/codi-browser-relay-before-rule-race-runtime.service`. Current
audit operator is `c98a0663a48f646a6c4e88b78939b0021ac53e05674547d966e734be9f36bf2c`;
policy operator is `policy-9915463c7`. No unrelated guest SSH work was touched.

The live Browser **Download URL** workflow was rechecked after the relay
update in desktop and emulated phone-sized Chrome layouts. Each test saved an
HTML file to My files, synchronized it to the server, then signed in as the
same disposable user in a fresh browser context and recovered identical
contents. Both test files and accounts were removed. The second context is
separate browser storage on the same computer; this is not a physical-phone or
separate-network result. `tests/browser-live-url-download.test.mjs` now covers
this recovery and attempts scoped file cleanup even if its later checks fail.


### Integrated Browser Stop candidate — 2026-10-31 UTC

The responsive Stop prototype is now integrated into the pinned engine patch
and paired with the worker using `browser-gecko-mailbox-v2`; its source is
backed up at `6bd03a679`. A separate, locally staged engine build from the
pinned sources has WASM SHA-256
`23b02f87791ad87208faf3680c5269ce0a7dc77c7bf33c7f88986e52d2ea5e2b`.
Tests against that actual engine stopped a delayed load in 68 ms, navigated
again, handled immediate Stop, and preserved a second Browser window. A
phone-sized emulated viewport also passed Stop and close/reopen during a slow
load. Nine patch tests and 62 mailbox/policy tests passed. A completely stalled
Gecko event loop and a physical phone have not been verified. The candidate is
not live: the corresponding source provision and further release checks remain.
The live Browser remains on ABI v1; do not mix its engine with the v2 worker.

The integrated Stop candidate is now live at release
`8d5fe713698d4bb94781b10ef22c4815e48b1d046237730e23259945d2332f05`,
Browser bundle `a84f7a0611eb8cdec8406738a8b1afabe493ff9b20c94b6455642d6f9ba5a4eb`.
Its corresponding v2 source archive is listed on the authenticated source
page, SHA-256 `736e7a6694e50ab66d8fe77da9a666685a6753b7613a5b9cbac4e72ff90ca171`.
A registered live test downloaded and verified it; unauthenticated source
access returned 401. A separately packaged bundle stopped a 10-second fixture
response in 67 ms and accepted subsequent navigation. Live registered desktop
and emulated phone-sized sessions rendered example.com; the phone-sized
session's Stop control returned, and both tests exercised signed relay,
blocklist, private-address denial and signed file-gateway operations. The
screenshots were visually inspected. Test accounts were removed. Physical
phone behavior and a live slow-response Stop test were not checked. The status
still says “Navigation requested.” after successful rendering; accurate page
completion/error reporting remains unfinished, as does the complete engine
license and final-link inventory review. Hosting generator SHA-256
`fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`,
manifest `15384f69c1f69e4deacbb7b959fce2fda2ff2fbe245ff16004b937e0b59de90f`,
Caddy `75d50e4c780724f95d425350db300c6c171866a5e2f41cdc738a72b4740c4ba1`.
Hosting backups are `/var/backups/webhost-sites/change-20261031T060217965059Z`
and `/var/backups/webhost-sites/change-20261031T060217965535Z`; prior release
is `c538220f32e70e55616f423e10d8e51af9bbf95b82d3bd510d64a29706feef03`.

After activation, the Browser Download URL workflow also passed in separate
live desktop and emulated phone-sized sessions: each saved to My files,
synchronized the server copy and recovered it after signing into a fresh
browser context. Both test files and accounts were removed. Temporary build
copies on the workstation, r730 and box-webhost were removed; live assets,
source archives, rollback backups, screenshots and unrelated work remain.

### Browser navigation-status investigation — 2026-10-31 UTC

An isolated diagnostic engine tested page completion, HTTP errors, redirects,
Stop, a blocked host and a deliberately closed TLS connection. The network
result alone cannot distinguish 404 from 200, or the tested block from TLS
failure. A script redirect also produced an intermediate cancellation result,
and successful start and stop events used different request identifiers.
The findings and reproducible loopback-only fixture are in
`apps/system/browser/experiments/README.md`; no diagnostic code is live.
Accurate, race-safe navigation status remains outstanding. The first TLS test
fixture hung on a TLS handshake; the corrected fixture explicitly closes it,
and the full asserted test passed. Unrelated guest SSH work remains untouched.

### Browser navigation feedback — 2026-10-31 UTC

Release `1ce5edb5bb8312f9cf3ab6a793f809549b38628a28b7440b42058359e4e68117`
is live with Browser bundle
`88b0f26a45dffa7c2c6fe385059aad3fe6450eb52894de7ded40184bbc45d3e4`
and engine ABI v3. Gecko's top-level network events now report completed
loads, HTTP 4xx/5xx and generic connection failures; policy-block notices are
preserved separately. Redirect cancellation is not treated as an error, and
older Wisp stream notices are tagged to avoid replacing a newer navigation's
status. The native wait also exits after a verified non-cancellation network
failure, allowing later requests instead of waiting indefinitely for an
internal error page. These are not guarantees for every website or race.

Local real-engine tests covered HTTP 200/404, HTTP and scripted redirects,
stalled-load Stop, a blocked destination, TLS failure, later recovery,
overlapping navigation/Stop, a second independent window, and an emulated
phone-sized viewport. An initial test found the listener attached too early;
that ordering was fixed. A subsequent test found blocked loads could keep the
native command waiting; the failure exit fixed the tested case. The packaged
bundle passed the same navigation suite. Ten patch and 89 JS tests passed.
Live registered desktop and emulated phone-sized sessions rendered example.com;
the phone-sized session reported a real 404 and Stop. Both live layouts saved
a Browser download to My files, synchronized it and recovered it in a fresh
browser context. Test accounts and files were removed. Physical phone behavior
has not been checked. Source snapshot
`codi-browser-source-ac6ea5798-v3.tar.zst`, SHA-256
`318ef4997e96e9f862ecf53bfa9c61e8c7dac2fb507fc71004bf36dd23c86d92`,
is available on the authenticated source page and was downloaded and checked
by the live registered test. Direct unauthenticated access returns 401.

Previous release `8d5fe713698d4bb94781b10ef22c4815e48b1d046237730e23259945d2332f05`;
hosting rollback inputs `/var/backups/webhost-sites/change-20261031T061922276453Z`
and `/var/backups/webhost-sites/change-20261031T061922276862Z`. Current hosting
generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`,
manifest `4765ea3e77b329afb91aa9f03ea569aa2430e3ad4f8c4088c898aead325a8f7f`,
Caddy `8b8602566e96063bd0e22c623333153d75e62e853ab9cdb41e155c522e856cc0`.
The complete engine final-link/license inventory remains unresolved.

Temporary local, r730 and webhost build inputs for this release were removed;
live assets, source archives, rollback backups and unrelated work remain.

### Browser Rust metadata and live WASM review — 2026-10-31 UTC

The authenticated combined notice now includes exact package metadata from
Firefox's pinned sources for app_units, core_maths, debug_tree and void, whose
releases lack separate project license files. Metadata identifies declared
licenses and listed authors without inventing copyright statements. The live
registered-session test checked the added entries and the complete notice hash
`04dd62fdc18dc6b94bfa439f55b4103de6bb34394b53e8e6167264dd8d2b8ada`;
manifest `8f35548e9754f63a3fa201ef9698c5c55c93a39085dd2ef41fbcb8aed140240f`.
Prior files are in `/var/lib/codi-ingress/browser-rust-package-metadata-backup.json`.
A hash-pinned scan of the actual live ABI v3 WASM confirmed 367,819 function
names and the named crate/type references documented in SOURCE_PROVISION.md.
Name counts are not a complete final-link audit; remaining licensing questions
are not declared resolved. Unrelated guest SSH work remains untouched.

The updated notice generator and associated Browser source snapshot is
`codi-browser-source-9f99310f6.tar.zst`, SHA-256
`14f39b6438216f4ab3a99524255389594ec73682b392e30fe555780a04edd88b`.
The signed-in source page and complete archive download were verified with a
fresh disposable account; the account was removed. Current index SHA-256
`0750f7e555476aa7ed0389cbd9ecfc30bad573e80141bd1f4abb7886d9d186f2`,
notice manifest `b63a5c359fcd48774bf528ad652fae2d301d89756f214321cea6e38f49a00953`;
the index rollback backup is
`/var/lib/codi-ingress/browser-source-index-rust-metadata-backup.json`.

### Gecko Rust archive input inventory — 2026-10-31 UTC

A reproducible scan of the pinned Gecko `libgkrust.a` archive found 5,713
members, 470 crate/build pairs and 454 package names. The hash-checked live
combined notice includes the exact Rust input and headings for all 318 vendored
package/version manifests identified in that archive. The other names map to
tracked workspace manifests or nine Rust toolchain crates. Three additional
native archive members were traced to cubeb-core, mozglue and SWGL build
directories. The archive and report hashes, caveats, verification tools and
workspace/toolchain distinctions are in `apps/system/browser/docs/SOURCE_PROVISION.md`.
These are link inputs and heading coverage, not proof of final retained
objects or complete license compliance. No live runtime or notice changed.

### Live rule-manager and documentation check — 2026-10-31 UTC

Read-only live operator checks reported empty incoming-login and outgoing
IP/country block lists, the configured Browser domain blacklist, a populated
but disabled whitelist, and the independent server audit disabled with no
key or ledger present. The Browser and network-policy READMEs now correctly
identify the running relay and distinguish the historical trusted-proxy
finding from the active guard. The new IP/country outgoing list covers the
Browser relay, not the separate Linux guest or every server egress path;
login blocks do not revoke existing sessions. The focused policy and operator
tests passed (11 and 2 tests) with a scoped maxminddb 2.8.2 environment. The
first attempt used the shared auth venv, which lacked maxminddb, and failed
its local-country-database test; the isolated dependency environment fixed the
test setup. No live policy was changed for these read-only checks.

The corrected documentation and current Browser source are published for
signed-in users as `codi-browser-source-f15af44a6.tar.zst`, SHA-256
`27e670c3bdae08bfe550ca6d732fc483e22d5ca50704f3d18b26ec7f02b01d27`.
A registered live test downloaded and verified the complete archive alongside
the runtime source, exercised relay and file-gateway checks, and removed its
disposable account. Current source-index SHA-256
`784e0ca9614166e56a99d8487d6c7ef8046bc76907b07caf66c72d64e7c2fd6c`,
notice manifest `df4e896c4d37024e38e805b037f6402a90e7427c5a362f55fe950e83ac529252`;
prior index files are in
`/var/lib/codi-ingress/browser-source-index-doc-update-backup.json`.

### Live Browser relay recovery — 2026-10-31 UTC

With a disposable registered account, the current live Browser displayed an
unavailable message when its relay was stopped before launch. After the relay
started, Reset engine reconnected and loaded example.com. A second stop while
the Browser was open produced its connection-ended message; restarting and
resetting again loaded a page. The test account was removed. This is manual
recovery and does not restore the temporary Gecko profile. The test made no
administrator report request, avoiding uploads from other browsers. Relay,
issuer and file services were active afterward; the public site returned 200,
unauthenticated source access returned 401, access block lists remained empty,
and server audit remained disabled with no key or ledger. The socket readiness
probe initially saw a missing socket during startup before the later retry
succeeded; this did not cause a test failure.

The current live release was tested with `CODI_TEST_REPORT=local`: a
disposable registered account recorded example.com in its browser storage,
then remained open for 32 seconds without submitting a report or acquiring a
server report row while no administrator request was active. The test made
no report request affecting other browsers and removed the test account.
The explicit-request and report-persistence tests remain documented in
`apps/system/browser/docs/DOMAIN_REPORTS.md`; those earlier tests used the
then-current release. Server audit remains independently disabled.

### Live Browser files and Linux boundary — 2026-10-31 UTC

Two disposable registered accounts wrote different HTML contents under the
same My files path and synchronized their server copies. The second account
could not find the first account's file before writing its own, and each
account subsequently read its own version from the server. A fresh signed-in,
phone-sized browser context opened the first account's HTML via Browser →
Open from My files; its rendered pixels matched, and the browser and server
copies remained identical. Both test files and accounts were removed. This
is an account-isolation workflow check, not an exhaustive security audit.

A separate disposable live account confirmed that Files browses temporary
Linux home, Linux-only files do not appear in My files automatically, account
files do not appear in Linux's former Account mount, and explicit Copy to
account works. After refreshing and signing in again, the temporary Linux
file was gone and the account file remained. Test account files were removed
and synchronized before the disposable account was removed. This used browser
automation on one computer, not a physical phone or an independent network.

### Browser subresource and relay policy regression — 2026-10-31 UTC

A disposable registered account saved an HTML document in My files that
referenced a blacklisted embedded resource. The current live Browser opened
the document and displayed the network-policy block message for that resource;
the file and account were removed. This was one embedded-resource case, not a
claim about every website.

The local relay's current `wisp.py`, `download.py`, destination policy, and
shared network policy hashes matched the installed live runtime. Their focused
tests passed: 14 Wisp tests, five downloader tests, and six destination-policy
tests. These included controlled DNS answer changes, mixed/public-private and
IPv6 transition addresses, redirect target checks, changes during DNS/connect,
and closing existing traffic after a new rule. The DNS and redirect tests used
local fixtures; they did not change public DNS or demonstrate every external
resolver/network configuration. The separately documented network-specific
NAT64-prefix limitation remains.

### Reproduced Gecko intermediate link map — 2026-10-31 UTC

An isolated reproduction used the pinned upstream relocatable relink recipe
and a linker map, without replacing the retained libxul. The result matched
all retained library sections except the generated module name and build ID;
name subsections other than module name also matched. The map identified
5,269 distinct Rust archive members across 326 package names in the
intermediate link. Pinned comparisons, counts, scripts and limitations are in
`apps/system/browser/docs/SOURCE_PROVISION.md`. This is not the final Browser
WASM link and does not by itself resolve all licensing obligations. The first
attempt used the upstream ordinary `-shared` recipe and hit its documented
linker crash; the relocatable recipe succeeded. No live service was changed.

### Browser final-link symbol comparison — 2026-10-31 UTC

A mapped final Browser relink produced WASM byte-for-byte identical to the
live engine. Its final map and a regenerated, hash-matching intermediate map
were joined by symbol name using `tools/join_gecko_final_maps.py`. The join
found unambiguous direct matches to 315 Rust package names, while 637 matched
symbol names had multiple possible input categories and 2,955 final libxul
symbol names had no match. Hashes, reproducible parser, counts and caveats are
in `apps/system/browser/docs/SOURCE_PROVISION.md`. Inlining and symbol naming
mean this is not proof of package absence or complete license compliance.
No live runtime or notice changed. The compact summary is retained locally;
temporary engine and linker-map copies were removed.

### Browser embedded graphics notices — 2026-10-31 UTC

The signed-in Browser source page now includes the original embedded notices
from the pinned aa-stroke `bezierflattener.rs` and `tri_rasterize.rs`, as well
as the MIT license from the matching .NET WPF graphics implementation at
revision `3993645a2957293053ec8090eff1fd472a07cd65`. The exact WPF revision used
to produce the Rust port is not established. The collector pins the complete
Firefox source-file hashes and WPF license before extracting notices. The
component notice SHA-256 is
`02a2923ad8fc48e68cde3756ff4323b81e8bcff56101fb9bee4803061a5b942f`;
notice manifest SHA-256 is
`40736943c79faaecd3a0c2ead8247b78e388dc0eda1c9a252abfbe43f3a53a8c`.
Previous files are backed up on box-webhost under
`/var/lib/codi-ingress/browser-wpf-notice-backup.json`. Local generation and a
fresh registered live source/relay/files test passed; its test account was
removed. The broader linked-component license review remains open.

### Browser notice source snapshot — 2026-10-31 UTC

The authenticated source page now indexes
`codi-browser-source-8a7a3c43d.tar.zst`, SHA-256
`ecf9e1526400f863291849c8ddbb4594c6534fcc1ec070ba629d2e63a1dbd8de`,
including the updated aa-stroke notice collector and WPF license. A live
registered session downloaded the entire snapshot and verified the hash;
relay, file and access checks also passed and the test account was removed.
Index SHA-256 is `49167a41e6024920cbf20b8de2860c0c143ed4bc817cf6db733e77d453fa3541`;
notice manifest SHA-256 is `2ea88b61c485792dd6f156bca4b2f2e147ef4aa7c254f6ad412d7d4f95553525`.
Prior index files are saved at
`/var/lib/codi-ingress/browser-source-index-wpf-update-backup.json`.

### Rust source comment notices — 2026-10-31 UTC

A reproducible source scan of 195 Rust package candidates identified by
unambiguous final-link symbol matches collected 85 distinct copyright-bearing
comment blocks across 482 file references, including libm's Sun notices. It
only scans the first 100 lines of tracked source files and omits test/example
directories; attribution at package level does not prove a given file was in
the binary, and other files and dependencies still need review. The signed-in
component notice SHA-256 is
`953caeb7f1f698f875d5ef4675d81b31e6cb4c26b3665cebf4a3419d497c1ba0`;
the manifest SHA-256 is
`b9b05b549abac8c2abd5dbf91875f0951ff810acdeaa838c98f303817b7f560f`.
The old notices are backed up at
`/var/lib/codi-ingress/browser-linked-headers-backup.json`. Local notice
validation and registered live source/relay/files checks passed, and the
live disposable test account was removed. The new collector source is backed
up in Git; update the downloadable source snapshot before declaring the source
provision work complete.

### Linked notice collector source snapshot — 2026-10-31 UTC

The authenticated source page now includes
`codi-browser-source-7bc6719ed.tar.zst`, SHA-256
`4fe52eaa8a8c2450fae3683845eaa4480ab045e2f5f28faf4a2a40a69a049c80`.
It contains the new linked-Rust header collector and the two pinned compact
link-audit records needed to reproduce the candidate list. A registered live
session downloaded and hash-verified the complete archive; relay and file
checks passed, and the test account was removed. Index SHA-256 is
`f3ef45a667ea5973111110a177697704e6dc82f60a1380399aab02a34e534b30`;
manifest SHA-256 is
`e3c26d091d1dd303bedef382498b0961417575df826c5eed9ded54f1430fb470`.
Previous index files are backed up at
`/var/lib/codi-ingress/browser-source-index-linked-headers-backup.json`.

The link summary also lists three vendored package names only in ambiguous
matches (`ffi-support`, `mime`, and `rustc-demangle`), which were outside the
195-package direct-match source-header scan. A quick source search found
Mozilla copyright headers in `ffi-support`; the other two produced no matches
in their `src` trees with that search. This is a lead for further review, not a
claim that those packages are absent or that their notices are complete.

### Linked Rust notice coverage audit — 2026-10-31 UTC

A reproducible comparison of the pinned final-symbol and archive inventories
against the exact live notice text found headings for all 198 vendored
package/version candidates, including the three ambiguous-only candidates.
Twenty-six lack separate vendored license files; all have supplemental markers.
Three (`aa-stroke`, `debug_tree`, `seahash`) have package-level metadata rather
than a verified standalone upstream license, and `svg_fmt` uses a source-matched
historical license. A marker alone is not a legal determination or evidence of
exact per-file linkage. Report SHA-256:
`646833aaa6f9db6ff500f7f24929978c1bd2d384760dfc5de83866b02f7242ec`.
The live combined notice hash matched the audit input; the audit test passed.
No live files were modified by this review. Other license categories remain
under review.

### Current Browser supplier-site recheck — 2026-10-31 UTC

The live Browser release `1ce5edb5bb8312f9cf3ab6a793f809549b38628a28b7440b42058359e4e68117`
was exercised in fresh registered desktop and emulated phone-sized Chrome
contexts. In both, example.com reported loaded; Grainger returned HTTP 403 and
its own “Access is temporarily restricted” page; McMaster reported loaded
and displayed its catalog. The phone-sized McMaster canvas showed a desktop
layout wider than the viewport and a large supplier survey overlay; usability
of that page on a physical phone is not established. These checks do not test
login, purchasing, full site interactions or general site compatibility. Two
disposable test accounts were removed. The first test-runner attempt had no
Node executable and exited before registration; the rerun used a temporary Node
22.16.0 archive checked against the distribution's SHA-256 list. No live site
code or policy was changed.

### Browser horizontal phone touch check — 2026-10-31 UTC

A fresh registered live session in emulated 412px Chrome opened a controlled
1,600px-wide local HTML page in the actual Browser engine. A horizontal touch
drag caused the page's own `scrollX` observer to report a nonzero offset (53px),
so sideways panning works in this fixture. This does not establish pinch zoom,
inertial scrolling, precise drag distance, physical-phone behavior, or that a
specific third-party site permits horizontal scrolling. The test created no
user file and its disposable account was removed. The test source is
`tests/browser-live-phone-horizontal-scroll.test.mjs`.

### Phone horizontal drag measurement — 2026-10-31 UTC

The controlled horizontal-scroll test now waits for Browser controls rather
than matching a transient status message, and measures after queued updates
settle. Two fresh live runs with six 35px touch moves spaced 40ms apart reported
final page offsets of 92px and 91px. A listener in the latter run confirmed
that the outer canvas received all six move coordinates. This suggests that
more investigation is needed between input dispatch and the embedded engine's
scroll behavior; it does not establish the cause or prove physical-device
behavior. An intermediate diagnostic run's original test waited indefinitely
for a transient status; after verifying its controls were enabled, the test's
status text was changed locally to let that run finish. That run is not used
as an independent readiness result. All disposable accounts were removed; no
live product code changed.

### Browser scroll fix live — 2026-10-31 UTC

Simplified release `628cceb37a2bb3541390a87df258453ac0fc4a4b03fafac0a899f0784709c108`
serves Browser bundle `d4779962241ed074236cbbe00c29eeeb258f9859e736c8fa21b1ed76e7b5f5ee`
with engine WASM SHA-256 `4efd895c3ec20729ee738ab942e6fbc2fc798ced2f28b7d37b116668540758be`.
The software wheel fallback uses immediate scrolling so successive touch events
accumulate instead of restarting a smooth animation. A live registered
phone-sized Chrome test moved 210px for both a six-step and a single 210px
gesture; a registered desktop Browser rendered example.com. Signed-in source,
relay admission, deny policy, file gateway, and account re-login checks passed.
Test accounts were removed. Local real-engine tests also covered vertical touch;
physical-phone input and custom page scroll widgets still need testing.

Corresponding source is `codi-browser-source-7092c2e0d-scroll.tar.zst`, SHA-256
`bb21975085ee8552ac16c428a59c83aa014be955b18742e0336f37f0b5703cae`,
on the authenticated source page. Its combined patch passed a reverse dry run
against the experiment checkout. Previous frontend is
`1ce5edb5bb8312f9cf3ab6a793f809549b38628a28b7440b42058359e4e68117`;
hosting backups are `change-20261031T071928382832Z` and
`change-20261031T071928383307Z`. Generator SHA-256 remains
`fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`,
manifest is `02aefbcde5ecc43c9da2988e3ad8d10b7d5860f49c586ab9b0401a7ab07ba90b`,
and Caddy is `84647a587008adb146180c260a038c0310a011d2f317189ceb474a677faa16ab`.
The generic HTTP smoke script failed because it expects 200 on port 80 but
Caddy redirects to HTTPS; a separate local HTTPS status probe returned 200 for
nine sites and the configured Basic-auth 401 for hardware.ksu.codes. This
status probe does not replace full functional checks of the other sites.

### Maximized apps and Files touch menu live — 2026-10-31 UTC

Simplified release `00490a673b162911ef55b86c0e536ac555249957da212fd1bfbe4ca5c1aedf71`
uses Files bundle `96c5adddcef0b1710e63af9bde696ea25a3984fc6f25693850acb336d9d5d16d`.
New app windows open maximized within the desktop and maximized windows follow
viewport changes; the maximize control restores a smaller window. Layout
persistence records the maximized state. On touch/narrow screens, Files has a
New / Upload menu for its existing create-folder, create-file, and upload
actions. Desktop right-click remains available. A real live registered test
created and uploaded files via the phone-sized UI, waited for server sync,
recovered both in a fresh browser context, and removed its files and account.
Two open windows followed phone, 1080p and 4K emulated viewports; a restored
window stayed independent and both states survived reload. A fine-pointer
desktop launch was also checked. Local tests covered menu toggling, the file
chooser and disposal. Physical F11, real phone touch and all other applications'
individual responsive layouts remain to be tested. App-by-app work is tracked
in `docs/APP_UNIFICATION_PROGRESS.md`.

Previous frontend was `628cceb37a2bb3541390a87df258453ac0fc4a4b03fafac0a899f0784709c108`.
Hosting backups: `change-20261031T072742460126Z` and
`change-20261031T072742460532Z`. Generator SHA-256 remains
`fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`,
manifest is `4df245dbc575d0ee1b24b2f6dca368564f3ee635ed2494aae1f45da6f85778a3`,
and Caddy is `ed555313f1afe1e6cef074615ec1acdf85bc8a506a7419b94620648ef3c496a0`.

### Files Open action and Files → Text workflow — 2026-10-31 UTC

Simplified release `e4cec0d0b929cb5f6bdc41e146d433d2d8e99eb5314b5ce5a833ea2c0d280a2f`
serves Files bundle `070b263b69e8cc8c29954e111c24a7fef925db883365827913276fc34187eb1d`.
A selected file or folder now has an explicit Open action, so touch users need
not perform a mouse double-click. Linux guest files still require copying to My
files before opening in a desktop app. Live registered desktop and phone-sized
tests created a text file in Files, opened it in Text, edited and synchronized
it, closed and reopened it, then read the server-backed copy in a fresh browser
context. Both disposable accounts and their files were removed. The initial
local test revealed that a single phone tap only selected the file; an initial
reopen test tapped an already-selected file and deselected it. The corrected
test uses the visible Open action. Real-phone behavior and broader Files/Text
edge cases remain open.

Previous release: `00490a673b162911ef55b86c0e536ac555249957da212fd1bfbe4ca5c1aedf71`.
Hosting backups: `change-20261031T073255411340Z` and
`change-20261031T073255411743Z`; generator SHA-256 remains
`fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`,
manifest `273b361d38f7d7f48df27ad7d0b72dd5144b48e5922d6417049c8932a303fbb3`,
and Caddy `c455ebbc5d581d0180ec771a683c25756b7ade23fa29a15c4c349d472d71f5ac`.

### Text first-save naming — 2026-10-31 UTC

Simplified release `d5e3b44eb6e6f3d5038d0adbda6ea090455508f2dbb9e7fe236f3bef00849898`
serves Text bundle `0bfe806569aa98921bfef3274c8f9cee44ce9879bfc1f252f3395ecedc892f66`.
The first Save for an unsaved Text document asks for a path in My files. It
uses the existing version-checked create behavior, so an existing file is not
overwritten and the draft is preserved. Live registered desktop and phone-sized
tests checked naming, collision refusal, sync and fresh-context recovery;
test accounts were removed. Local desktop and phone-sized editor regressions
also passed for existing-file edits, conflicts, Save As and reload. The old
phone regression test was updated to use the current Keyboard lock menu.
The dialog still uses a path field rather than a visual destination picker;
physical phone keyboard behavior and broader app integration remain open.

Previous frontend:
`e4cec0d0b929cb5f6bdc41e146d433d2d8e99eb5314b5ce5a833ea2c0d280a2f`.
Hosting backups: `change-20261031T073619549120Z` and
`change-20261031T073619549552Z`. Generator SHA-256 remains
`fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`,
manifest is `0afb0763ef2f80c6ed583945eeb2f43d6dd249409809110fcce296e2a6bb4071`,
and Caddy is `25c0553f189c179dc00d8e83aa9612af3fb76de42635aaff840aaa7fcb1d79b8`.

### Text My files folder picker — 2026-10-31 UTC

Simplified release `099f46ea3c88af6866333d24508f6af6a7d07e1f403506529a704f35fd00d7a7`
serves Text bundle `0c8e1a9420c867d4c50ea4f06ed0dc3d0e271d13ed3ac89372174eebaa0590f3`.
Text's first-save and Save As dialog can now browse account folders using the
shared `host.storage.pickFolder` service. A typed path remains available;
existing destinations are not overwritten. The picker returns only My files
folders, checks the active account, and closes on app disposal. Its list and
buttons have 44px minimum targets. Registered live desktop and phone-sized
tests verified folder selection, cancel, collision refusal, sync, recovery in a
fresh browser context and cleanup; disposable accounts were removed. Local
existing-file, conflict, reload and shared open-picker regression tests passed.
Physical phone keyboard and accessibility testing remain outstanding.

Previous frontend:
`d5e3b44eb6e6f3d5038d0adbda6ea090455508f2dbb9e7fe236f3bef00849898`.
Hosting backups: `change-20261031T074116644050Z` and
`change-20261031T074116644458Z`; generator SHA-256 remains
`fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`,
manifest `ff9309da3ac2bcda972f88b34e7bc70b296ccbf92d0f2027aaf7e8822ba07703`,
and Caddy `d6f62938039e9718e8158994d8f35b9a6078f60eff925ac1d85b8a581a2a0081`.

### Document Editor account-file workflow (2026-10-31)

Live release `3da419b1cd6f33642b73ca9bfa64d5d3de338c698c508b65855f1a721a029787` adds Open from My files, Choose save folder, and preserves the current editable draft if a chosen document cannot be opened. Local desktop and phone-sized browser tests passed, including save, sync and fresh-session recovery; the broader desktop report/PDF and touch tests also passed. On the live site, the desktop test passed. The phone-sized run completed the same save/recovery checks but encountered a server request limit during fixture cleanup; its test account was then cleaned directly with path and content checks. Investigate request limits when reviewing sync behavior. This is not yet a complete Document Editor review.

Hosting generator SHA256 `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `68865ff3e73a2d3becc89d0b1de2cc46de7a50f56e5f92466e199770fd63ee42`; prior active release `099f46ea3c88af6866333d24508f6af6a7d07e1f403506529a704f35fd00d7a7`. The staging check found changes only in the Document Editor bundle and app catalog.

### Document image selection and storage capacity target

Live release `16a4f64d12e26500417df61f49edb6597869c3c2bf391b707bd3cece42163e12` makes Document Editor's Image button use the shared My files picker for PNG, JPEG and WebP. Local desktop report/PDF and touch insertion tests passed; the touch-sized image workflow also passed against the live site and its disposable account was removed. Hosting generator remains `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest is `455c5fd89539938acd51157a326a166a1fb877664d527af8e7aa5365bb43abdd`. Prior release is `3da419b1cd6f33642b73ca9bfa64d5d3de338c698c508b65855f1a721a029787`.

The user set a planning target of 100 simultaneous users, most not transferring at once. See `docs/ACCOUNT_STORAGE_CAPACITY.md` for current per-file polling and authorization bottlenecks, design direction and mixed-load test requirements. This target is not verified capacity, and the existing scan/retry design is not yet suitable to claim it.

### PDF Viewer review (2026-10-31)

Live release `74e9a439382583139cb01b212676bf6665b5a2cb507efc004ef92c357c3443a9` switches the viewer to Open from My files, adds larger controls and automatic width re-rendering, and retains the previously displayed PDF if opening a new file fails. The local desktop report/PDF/upload suite passed on rerun; the first attempt encountered a connection-interrupted timeout after its offline phase. Focused desktop and phone-sized open/navigation/resize/invalid-file tests passed locally and on the live site; isolated live accounts were removed. The viewer remains canvas-only, without text search, selection, editing or annotations. Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `e0f3550f91599bda4ecc872c49ae623d132d794ef4a5207c1d468413accac7d1`, prior release `16a4f64d12e26500417df61f49edb6597869c3c2bf391b707bd3cece42163e12`.

### Spreadsheet workflow review (2026-10-31)

Live release `7f0798683edc5e41e4515d62505d120fa883fadc90d1dc68aa26d848a14fd72c` adds Open from My files and Choose save folder, larger toolbar targets, and retains the current workbook after a failed open. Local tests passed formulas, XLSX import/export, upload, saving, fresh-session recovery and failed-open preservation; a phone-sized test used touch to enter a cell. The corresponding live desktop workflow passed. Phone-sized checks reached fresh-session recovery but cleanup hit the existing file-authorization request limit; both disposable accounts were then removed using guarded cleanup. This does not validate full spreadsheet touch accessibility or Excel parity. Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `eacb42f1f1efb8367a0edad75415226aa19ae06da62aa9a465c4030b6947e889`, previous release `74e9a439382583139cb01b212676bf6665b5a2cb507efc004ef92c357c3443a9`.

### Interrupted mirror scans (2026-10-31)

Live release `158720539a14493dbee33ee37d15045e1df3d19f88610c8701e6dc09555bbb3b` carries source `e0db6cd22` mirror SHA256 `3eefc87ae89c7be21a0c1a18b339c52c889bd855773d91e38237f7ac5fc193d1`. A scan remembers completed file checks across interrupted attempts within that mirror instance, invalidates an entry on local version change, and clears progress after a complete scan so later external changes remain discoverable. A deterministic 12-file fixture with a three-version limit per window proved eventual completion, later same-size external changes, and a local edit during interrupted scanning; existing mirror conflict/offline/rename tests passed. Baseline failed the 429 handling test. Local browser Document and Spreadsheet desktop/phone-sized save/reopen workflows passed; a live registered desktop Spreadsheet check passed and its disposable account was removed. The public module SHA matched the pinned source. This does not resume interrupted folder inventory, reduce idle scans, or validate 100 users; the batch/index and capacity work remains open in `docs/ACCOUNT_STORAGE_CAPACITY.md`.

Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `f635000df16a8cb46eab42a3f4a3b46e25cbebd68c9c41ac63c4d54aa168935e`, previous release `7f0798683edc5e41e4515d62505d120fa883fadc90d1dc68aa26d848a14fd72c`. Staging verified the mirror was the only changed asset before cache metadata regeneration.

### Local candidate: batched file versions (2026-10-31)

Source-only candidate adds optional gateway version-batch capability, at most 16 unique paths and 32 MiB hashed per request. It enforces registered account read permissions and private descriptor checks; oversized or missing files are deferred to individual version checks. Browser mirror falls back when capability is absent and retains partial-scan recovery on 429. Local signed browser/gateway check verified 20 files in two batch operations instead of 20 individual version operations, including same-size external disk modification and fallback to the old protocol. Python tests cover account isolation, disabled read access, malformed paths, symlinks, and restrictive modes; real signed issuer/gateway checks cover anonymous and cross-account access. Existing mirror/codec/version tests passed. Nothing in this candidate is deployed: verify guarded worker packaging, rollout/rollback, real concurrent behavior, and resource usage before treating it as production-ready. See `docs/ACCOUNT_STORAGE_CAPACITY.md`; batching alone does not establish 100-user capacity.

### Batched version checks live (2026-10-31)

Gateway worker `541d74f9042d34c3514a2b27cfee708104f0879194232720e864e9b3af329040` was built from verified live `be4a9ef3a613c2e90517fae427d4d2256b97b74ee2134c10cafe263fc2440eac`; only gateway client, HTTP dispatcher and user store changed, and the live dependency lock was preserved. Existing protected code-upgrade helper activated it, reporting preserved permission bindings and no account/file data restoration; the issuer and file service restarted. Live static release `12e690c7afda47f279a45642b6bc21f73cd2d2034170978ba4cda3179ca2c265` selects the batch-capable mirror. Public capability and a real registered browser scan of 20 files using exactly two signed batch calls passed. The disposable account and its exact fixture files were removed. Local mixed test used eight accounts, two simultaneous batch requests and a 2 MiB upload, passing in 0.825s total after setup (maximum batch 0.065s); this is one small fixture run, not a 100-user benchmark. See `docs/ACCOUNT_STORAGE_CAPACITY.md` for remaining load and efficiency work.

Native release pin `0aaf61849fa03e41376d63a36496c83e83adbc97c14aeafe366100ff9e530af2`; native config SHA256 after gateway upgrade `e7a36e37271b0ada77c05ad501f387d9fc4d532f73a068341d9e4f7c7cbf3bc3`, file config `16bac2187e18910cb704e94f8c603f550e523134afde07cbbef3bc98a6417a0d`. Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `7503a25ac29bf7e5c7cd626b877f7a9491c7893840c156da4b5c8a8ef008ce53`, prior static release `158720539a14493dbee33ee37d15045e1df3d19f88610c8701e6dc09555bbb3b`. Old gateway worker is retained for code rollback through the protected helper. No 100-user capacity claim.

### Data Explorer result saving (2026-10-31)

Live release `477888700cdd6204b669860bab43213a0e6f03780cb29b290fc44cb44335bf04` adds the shared My files opener and folder chooser, a CSV output path and Save results CSV. Export writes the current SQL result to the browser mirror with overwrite confirmation and server synchronization; it does not serialize Perspective chart settings, filters or pivots. The input CSV remains unchanged. Local desktop, phone-sized and 4K-sized browser tests covered PC upload, SQL aggregation, chart rendering, chosen folder, saved CSV contents, cancelled overwrite, fresh-session recovery, window close and reopening the result. Desktop and phone-sized tests passed against the live site, and their two isolated accounts were removed. Tests emulate viewport/inputs; physical phone touch and broader data/chart workflows remain unverified. SQL/query and chart settings are still temporary, and large queries may exceed device resources.

Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `85dd9b55238be1d1deb81547269bf0ec5f16c480e997f18490c8d00c21538325`, previous static release `12e690c7afda47f279a45642b6bc21f73cd2d2034170978ba4cda3179ca2c265`. Staged asset comparison found only Data Explorer bundle and catalog changes.

### Python Notebook file workflow (2026-10-31)

Live static release `a0eec8a0a284820b467244970f05eeb980949b656263fa923d088fb3d8cfbc06` adds Open from My files and a save-folder chooser. It prepares an opened notebook under a new temporary JupyterLite path and only replaces the active notebook after it loads; invalid notebook content leaves the existing path and draft intact. Local tests passed Python/NumPy execution, notebook upload/open, automatic save, two-account same-browser isolation, rejected-file recovery, and fresh-session recovery; desktop, phone-sized and 4K-sized viewports were emulated. Live desktop and phone-sized save/recovery checks passed; test accounts and their server fixtures were removed. Physical phone touch, all notebook formats and untrusted-code isolation are not established. The JupyterLite working copy may remain in browser storage after close; My files is the persistent account copy.

Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `0396531f11b500b905cf6f6f745b9502e4fe6f533c7ca3357a1f15b3b6f14819`, previous static release `477888700cdd6204b669860bab43213a0e6f03780cb29b290fc44cb44335bf04`; only the notebook bundle and catalog changed in staging.

### Image Editor failed-open protection (2026-10-31)

Live static release `a917daea9c878b4fd284be0a699b72a58e4a1e7fe329a5c167217f6d75193743` validates a chosen PNG/JPEG/WebP before replacing the current editor and preserves its edits when decoding fails. The My files action has clearer wording and a larger touch target. Local Files upload/resize/save/server PNG test and desktop/phone-sized failed-open/fresh-session tests passed; focused desktop and phone-sized checks passed live, and the disposable accounts and exact fixtures were removed. Physical touch, full image tooling and all formats remain unverified. Save currently updates the opened file; Save As and animated GIF editing remain unimplemented.

Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `5d5916be12033a02ef922254d136cc470813796b5108e3137ea7621970237e30`, previous static release `a0eec8a0a284820b467244970f05eeb980949b656263fa923d088fb3d8cfbc06`; staging changed only the Image Editor bundle and catalog.

### Desktop window sizing and shared tools (2026-10-31)

Live static release `34bf76afe9033469c4cb482a5eaeb79f5b91f63c7c200edc8d0946c4fcbb1ece` makes new desktop windows open in alternating half-width, full-height left/right tiles; phone windows still open full screen. Explicit maximize follows viewport changes, restores to its tile, and manually moving/resizing a tile clears its automatic placement. The tile side is saved per window. Local and live browser tests emulated phone, 1080p and 4K viewports, resizing, maximizing, manually moving and switching between phone/desktop widths. Existing manually restored windows retain their saved geometry. Physical F11 and hardware touch were not tested.

Trystero 0.26.0, TanStack Virtual core 3.19.9, ONNX Runtime Web 1.31.1 CPU/WASM, WebTorrent 3.0.21 and Yjs 13.6.33 are lazy shared bundles with disabled System Tools entries. No app consumes them yet. A real local and live browser test confirmed disabled menu items, lazy loads, Yjs state exchange in memory, WebTorrent creation/destruction with trackers disabled, and ONNX WASM inference on a tiny local model with no external requests. No actual peer, tracker, TURN allocation or multi-device collaboration test was made. ONNX's separate shared copy has CPU/WASM only; Transformers.js still retains its independent ONNX dependency. TURN service, proxy and shared ingress were active, DNS for turn.ksu.codes resolved and TLS verified; those checks do not prove relay allocation or NAT traversal.

Image Editor Save As was deployed in preceding release `1f1887d6b2a610ae42fa9ca8b39ebaf5bc7517168cba8fc40c3f872533fc964d`. One live phone-sized run saved the first copy but timed out after an immediate subsequent resize/save with the older size still present. This release exposes Unsaved changes on editor modifications; later local desktop, phone and 4K-sized checks and one live phone-sized check passed when waiting for that change signal. The earlier failure remains a limitation to investigate if it recurs; this is not physical touch validation.

User expanded scope to all listed non-game, non-XR/AR webOS applications and shared tools, while developing games and XR/AR separately. `docs/NON_GAME_EXPANSION.md` records current inventory, proposed categories and unfinished integration. The full app review and 100-user storage capacity objective remain active.

Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `a98f610bebc6c5fbe32af7feb205f1697eba8aadabd795ed5db1807f3ee0dfd9`, previous static release `1f1887d6b2a610ae42fa9ca8b39ebaf5bc7517168cba8fc40c3f872533fc964d`. Staging changed only the shell, app catalog, Image Editor and five new tool bundles. Disposable live test accounts/fixtures were removed.


## 2026-10-31 — Audio Editor open safety and game scope

Audio Editor validates browser decoding before replacing the current track, keeps the edited track and destination name when an invalid file is chosen, and avoids the upstream open-or-append modal for My files. Desktop, emulated phone and 4K local tests exercised upload through Files, reverse, invalid open, WAV save, server sync and reopen. A fresh registered live-site desktop test passed the same workflow, plus local Tone and WaveSurfer checks; its disposable account and test files were removed. Physical-phone behavior, large-file memory pressure, multitrack saves and full audio workflows are not qualified.

Live static release: `8de776337097c89fb9ae825db7e9e3bd9999522f518a4292716db5bf5bccde44`; previous release: `34bf76afe9033469c4cb482a5eaeb79f5b91f63c7c200edc8d0946c4fcbb1ece`. Hosting generator SHA: `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA: `c0db2952fa9972d366e559cb41b9075615bcf3d44535717a294090b490ed024f`.

The user authorized games and identified `../served_apps_public/game_tree` as the design starting point. It contains pseudocode and specifications, not playable games. Its own AGENTS.md requires independent apps, real Rive integration, and one finished vertical slice before expansion. XR/AR remains outside the newly authorized scope.


## 2026-10-31 — Falling Blocks live preview

Applications → Games → Falling Blocks (preview) is available at ksu.codes. It
contains the independent Phaser game and locally served Rive coach. Local
desktop tests cover multiple windows, account saves, stale versions, simulated
separate-browser gateway failure, minimize/restore and isolation. A disposable
live account passed menu launch, coach rendering, account save and recovery in
a fresh phone-sized browser session; that account and its one test file were
removed. This does not establish physical-phone operation or complete game
acceptance, and the app is labeled preview.

Live static release `d652a17c3d8144db943eeddd48b5bd11e8a66e7364797ab7e70003c9bd758e0c`;
previous release `8de776337097c89fb9ae825db7e9e3bd9999522f518a4292716db5bf5bccde44`.
Generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`;
manifest SHA `8fd3e6bc30d456bf31c28af2ed59314e45c2451b95b8e481f45b699aff5e2242`.
The reviewed release differs only in app.js, catalog and Falling Blocks assets.
The full build now includes Falling Blocks: run its pinned `prepare.py` with
Rive CLI 1.8.0 and install its npm dependencies before building.


## 2026-10-31 — diagrams.net file workflow

Live static release `1ba25a429096862853834d5eb47b83a13c5aece4b46917e0f5605684a0934c28`;
previous `d652a17c3d8144db943eeddd48b5bd11e8a66e7364797ab7e70003c9bd758e0c`.
Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`;
manifest SHA `8bb32e7d5e3f2e229a3aceb56b6ee1faf5823479173910d75f8d6a5a4c117af9`.
Only diagrams.net assets and app catalog changed. Open validates XML before
replacing the current diagram; save supports choosing a folder and confirms
replacement. Local and live desktop and emulated-phone tests opened a diagram,
edited its label, rejected malformed XML without losing that edit, saved and
synced it, recovered in a fresh browser session, and uploaded via Files. The
two disposable live test accounts and their files were removed. This does not
prove arbitrary compressed payloads, full touch UX or physical-phone behavior.


## 2026-10-31 — Excalidraw file workflow

Live static release `641af409e1602e8278c95ee22a06c8c7a01e06642d53e238ff40bdc70d336f41`;
previous `1ba25a429096862853834d5eb47b83a13c5aece4b46917e0f5605684a0934c28`.
Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`;
manifest SHA `74f77dda811ebacf8d24760ab3ca121e0e935b31a6b6924c55f825bc076e4310`.
Only Excalidraw assets and the app catalog changed. Open validates basic
document structure before replacing the drawing; Save location chooses a folder
and replacing an existing file requires confirmation. Local and live desktop
and emulated-phone tests drew a shape, rejected an invalid file without losing
the edit, synced it, recovered and resaved it from a fresh browser session, and
uploaded through Files. Disposable live accounts and test files were removed.
Physical touch, arbitrary embedded images and full upstream compatibility are
not established.


## 2026-10-31 — SVG-edit file workflow

Live static release `477085a902f1ec63021de1a0b8359985083f6891c82c1d0855a32f31f0cda896`;
previous `641af409e1602e8278c95ee22a06c8c7a01e06642d53e238ff40bdc70d336f41`.
Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`;
manifest SHA `51cb1071dc7bba7b0d0a6b8d91ccaaf574fc7a33e951b0e4bde4237c6a1b9b78`.
Only SVG-edit assets and app catalog changed. The editor checks XML and SVG
root before opening, attempts to restore the prior drawing if the editor rejects
a valid-looking file, offers a folder picker, and confirms replacements. Local
and live desktop and phone-sized viewport tests used the rectangle tool with
pointer input, rejected malformed SVG without losing it, synced to account disk,
reopened in a fresh browser session and uploaded through Files. Two disposable
live accounts and their files were removed. Physical touch and complex SVG
compatibility are not established.

## 2026-10-31 — Replicad primitive projects

Live static release `b2a0809a06bd3c316eb12c52ce8f6434a65ef31247c06074f3fa4b5e915229e7`; previous `477085a902f1ec63021de1a0b8359985083f6891c82c1d0855a32f31f0cda896`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `05e198f56bb0a6da1f7e3b4993d10d12c24b0fc14cd7e9fe08610377605afe32`. Changes are Replicad assets, the app catalog, and the desktop routing/close/layout changes needed for project files.

Replicad is a box/cylinder generator, not a complete visual or programmable CAD app. It now saves and opens editable `.replicad.json` projects in My files, validates dimensions and input, guards unsaved work and changed files, creates STL/STEP in a cancellable local worker, and opens its projects from Files. The local desktop and emulated-phone test verifies uploading through Files, invalid-file recovery, account/server sync, opening from a fresh browser session, STL dimensions, and a STEP file header. The same live desktop and emulated-phone tests passed before the upload case was added; a later live upload run was interrupted by HTTP 429 from the file gateway after rapid tests, so live upload was not verified. Disposable live test accounts were removed. Actual phone touch, geometry beyond the tested models, 3D preview, CAD source editing, and manufacturing validation remain outstanding.

## 2026-10-31 — G-code viewer workflow

Live static release `d216536a208de11e1cc72dea56978385d628724a8646493001e6d335340bcefe`; previous `b2a0809a06bd3c316eb12c52ce8f6434a65ef31247c06074f3fa4b5e915229e7`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `ecd6468317bef1113620a90cd53a7272bf00cb4ba047cce8fc63a018c2da6f78`. Only the G-code app assets and catalog changed.

The viewer now offers an example and a switch for non-extruding moves, makes My files the primary open action, and retains the existing view when an input cannot be previewed. Local and live desktop and phone-sized tests exercise the example, upload through Files, account/server sync, invalid-input recovery, a visible change when toggling travel, close/reopen and a fresh browser session. Disposable live accounts were removed. The library is intended primarily for 3D-printer G-code; it is not a full CNC or safety simulation. Large files currently parse on the UI thread, and physical touch and broad controller compatibility remain unverified.

## 2026-10-31 — Grid.Space export workflow

Live static release `79f13c13f38a130370f6484defb080f31a1549f4d11bca7472de24b1c85f3870`; previous `d216536a208de11e1cc72dea56978385d628724a8646493001e6d335340bcefe`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `a46a516266fe3f14533f4f4885e6aea5d93807ac1026f39ce12e7557cea3d17d`. Changes are Grid.Space app assets, the catalog and a desktop close guard.

Mesh:Tool and Kiri:Moto now offer an explicit save-to-My-files panel for exports, with folder choice, collision checks, cancellation and a close warning for pending exports. Local and live desktop and phone-sized automated tests upload a model, perform a mesh union, slice it in Kiri:Moto, save both exports, check account-server hashes and test a second account in a separate browser context. This separate-context test does not establish same-browser account-switch isolation. Upstream controls remain desktop-oriented and were driven partly through their APIs in automation; physical touch, broad format/profile coverage and hardware use remain unverified. Workspaces are browser-local until exported; exported files sync to the account. Disposable live accounts were removed.

## 2026-10-31 — Digital Logic file workflow

Live static release `b1f8fcb55abf011e081d984f5df11441ce96b940b9eddd1ae495aa289bfd0bfb`; previous `79f13c13f38a130370f6484defb080f31a1549f4d11bca7472de24b1c85f3870`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `3c0daf5a17b19b5972edac2f0f3bd020af3293705ec45b76451e3d2590e8fee2`. Changes cover Digital Logic assets, app catalog, desktop document routing, layout and close guard.

The JSON editor now saves `.logic.json` documents, opens them from Files, selects a save folder, warns about unsaved edits, checks file conflicts and preserves the current editor/simulation when a replacement fails. Local desktop and phone-sized tests checked the AND truth table; local and live tests checked upload, sync, bad-file recovery, close warning, direct Files open and fresh-session recovery. An initial live test failed due to a menu-element timing race; the adjusted test passed on desktop and phone-sized viewports. Disposable live accounts were removed. The app is still a bounded feed-forward JSON simulator, not a full schematic editor or hardware validation. Saving currently requires valid supported JSON, and physical touch remains unverified.

## 2026-10-31 — CircuitJS file workflow

Live static release `fc51848fd9c9786e802dc85610a5a7e4b36ed08fa0d136f08641990c28038dd1`; previous `b1f8fcb55abf011e081d984f5df11441ce96b940b9eddd1ae495aa289bfd0bfb`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `da7b14421c5cc85294e8d7d8b2ddd7fbbe494e1f269cc27010ca0f58f44e54a7`. Changes cover CircuitJS assets and its corresponding-source archive, app catalog, desktop file routing, layout and close guard.

The circuit simulator now opens `.circuit` files directly from Files, uses a folder picker and conflict-aware saves, warns on unsaved changes, and preserves the current simulation when an unrecognized file is rejected. Local and live desktop and phone-sized tests verify a 5 V divider, change a resistor to obtain about 6.67 V, save and sync, upload through Files, reject a bad input, cancel the close warning, reopen from a fresh phone-sized session, and dispose the iframe. The source archive includes matching desktop-integration source and the live test fetched it. An initial local reopen test exposed CircuitJS's `<cir>` XML root; import was corrected and retested. Disposable live accounts were removed. This is CircuitJS rather than ngspice, not a hardware validation; physical touch and broad circuit-format compatibility remain unverified.

## 2026-10-31 — Electronics Design output workflow

Live static release `b131c53090ecd3e905dae2009c4510438c84780ade18278ca93abaa45795f1e5`; previous `fc51848fd9c9786e802dc85610a5a7e4b36ed08fa0d136f08641990c28038dd1`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `d74a5882a31d11ac6ec85db30cbf8af9f843f95b82cff7dad003022fd0b4e90d`. Changes cover Electronics Design assets, app catalog, desktop file routing, layout and close guard.

Captured editor outputs are retained separately, can be saved or discarded individually, and prompt before closing while pending. Saves offer folder selection, replacement confirmation and version checks; `.dez` projects can open directly from Files after the editor starts. Local desktop and phone-sized tests and a live desktop test cover upload, two actual captures, selective discard through the bridge, close warning, account sync and fresh-session Files reopen. The live phone-sized run reached fresh-session local recovery but hit HTTP 429 on its final server sync; it is not a complete live phone pass. Disposable live accounts were removed. The host cannot detect uncaptured editor edits, which is stated in the UI. Phone tests used keyboard simulation; physical touch, broader design workflows and fabrication validation remain outstanding.

## 2026-10-31 — Storage rate-limit recovery

Live static release `7d482122147e5e72ecdcf22931945a6f7b3756b4461ebd39dfa9d7775d56c0e8`; previous `b131c53090ecd3e905dae2009c4510438c84780ade18278ca93abaa45795f1e5`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `419b34b85b2e4c55a967020a9c18a7a01bd91e2893199c81c54e21a037ce8c09`. The only changed application asset is `storage/browser/mirror.mjs`, SHA `4614ca9854364fdd6dbfedd761b87a2f8dbf88c10ead7e07ca1d8266c5eb58dc`.

The current live Caddy route forwards file-authorization requests directly to the loopback issuer; its file authority buckets `REMOTE_ADDR`, so visitors share that proxy-observed limit. The mirror now spreads automatic retries with jitter and bounded exponential backoff after 429; explicit sync and new local writes still attempt immediately. Node tests checked pending-write retention, eventual retry and timer cleanup, alongside existing offline/conflict tests. Local and live account-backed browser tests injected two 429 responses, accelerated timer durations for the fixture, and confirmed the signed write eventually reached the server; the disposable live account was removed. No issuer or gateway limits were changed. This reduces retry pressure only: idle polling, shared proxy buckets, server concurrency and the 100-user capacity target remain unresolved. See `docs/ACCOUNT_STORAGE_CAPACITY.md`.

## 2026-10-31 — Arduino firmware workflow

Live static release `2227cc5560f89e90ed0d80f52554ca0a508e402df3fc3e78067f06eb18543ba6`; previous `7d482122147e5e72ecdcf22931945a6f7b3756b4461ebd39dfa9d7775d56c0e8`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `a1b0ba49296069541be607b9c9d0978da3ada8ceeeb492a90ea45d9cbdc67577`. Changes cover Arduino assets, catalog, desktop document routing and layout.

The simulator now saves the loaded firmware to My files with a folder picker and conflict checks, and opens `.hex` files directly from Files. Invalid HEX leaves the prior simulation running. Local and live desktop and phone-sized tests cover real Blink LED transitions, upload, bad HEX, independent windows, save/sync and fresh-session Files reopening. Disposable live accounts were removed. This is a limited ATmega328P simulation; sketch compilation, other peripheral models, physical touch and validation on hardware remain outstanding.

## 2026-10-31 — Pico project workflow

Live static release `c2d66514aa5973267c544aa36d469f22ce2f1c28db169c9f3e4090542b152fb2`; previous `2227cc5560f89e90ed0d80f52554ca0a508e402df3fc3e78067f06eb18543ba6`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `c86b5675efff5e0b8a00d9ad2517fac88889bd830a12f3a6b9436a9683e78a3d`. Changes cover Pico assets, catalog, desktop routing, layout and close guard.

Pico projects open directly from Files; saves offer a folder picker, replacement confirmation and stale-version protection. Closing or replacing an active firmware board conservatively warns that flash may have changed; a board-generation check avoids applying an old save result to a replacement board. A local isolated-account test using private ROM and MicroPython firmware checked flash persistence, invalid-project recovery, a declined close, competing saves, reset isolation, fresh phone-sized Files reopening and worker disposal. Local and live desktop/phone-sized Blink tests passed without uploading the private ROM to the live site. Disposable live accounts were removed. SSI emulation, arbitrary firmware and physical touch remain incomplete or unverified.

## 2026-10-31 — Stitch Converter artwork workflow

Live static release `387d5a53a94fadb22d98fe196ead582767011f51802e0d293729e1a5f6f5b876`; previous `c2d66514aa5973267c544aa36d469f22ce2f1c28db169c9f3e4090542b152fb2`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `bba05b8cc7e55d50e75875a92e93c92ca6c5dad065cc6721ea7a6e4117f0f48b`. Changes cover Stitch Converter assets, catalog, desktop file routing, layout and close guard.

The converter separately saves editable `.stitch.svg` artwork and machine output, warns about unsaved artwork, checks versions, opens supported artwork and machine files from Files, and clears a stale preview when artwork or size changes. Local and live desktop and phone-sized tests cover editing SVG, PES export and reopen, bad-file recovery, upload, sync and fresh-session Files opening. Disposable live accounts were removed. This checks one example and one machine format, not full machine compatibility, physical sewing, or physical-phone touch.

## 2026-10-31 — Embroidery Studio project workflow

Live static release `a882cd06001539f180da5d557eaec47d4a3b30d5e3d6c5cb19885fb13c66fc1b`; previous `387d5a53a94fadb22d98fe196ead582767011f51802e0d293729e1a5f6f5b876`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `cfc36a6e69c3187b3de2a56e57f4e178f76bd38e9f417270c11aa91749f77431`. Changes cover Embroidery Studio assets, catalog, desktop document routing, layout and close guard.

The host now invokes the embedded editor's project Save As command directly and saves its captured project to My files in one step. It offers folder selection, version/overwrite checks, direct `.stitchfoundry` opening, basic project validation and warnings for known unsaved edits. Machine exports and separately captured files remain distinct. Local and live desktop and phone-sized tests create a design through the editor API, check project save/sync, overwrite cancellation, invalid-project recovery, machine export, upload and fresh-session Files reopen. A separate local test checked the editor Save As capture bridge and stitch export. Disposable live accounts were removed. The underlying editor is pre-release; full dirty-state detection, native UI/touch usability, machine-format compatibility and physical sewing remain unverified.

## 2026-10-31 — Audio Editor file workflow

Live static release `6e1d3e53140abf1d4047d920b827d5f17529254169baa7fa346c7109b5e8888f`; previous `a882cd06001539f180da5d557eaec47d4a3b30d5e3d6c5cb19885fb13c66fc1b`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `18462561c9a77cf0fb4f9875d26e677ff9af684e3fb5a79b16a26dd4a1d8eccf`. Changes cover Audio Editor assets, app catalog and desktop layout restoration.

The single-track editor now provides a folder picker and usable default WAV name, avoids saving while loading, checks the current file version before replacement, and remembers its opened or saved file for layout restoration. Local desktop, phone-sized and 4K-sized tests and live desktop/phone-sized tests cover upload, an actual sample-checked reverse, invalid-file recovery, close warning, stale-save refusal, sync and fresh-session Files reopen. Disposable live accounts were removed. Its existing 32 MiB input/output limit remains below the requested 128 MiB file-service limit; large-audio memory handling, multitrack project persistence, broader effect/codec coverage and physical touch remain unfinished.


## 2026-10-31 — Larger audio files

Live static release `4b5f72175898b56247e7dc2201a063fe37e00afdbded42ec5ad056d453ca6bf6`; previous `6e1d3e53140abf1d4047d920b827d5f17529254169baa7fa346c7109b5e8888f`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `e40bfce95dbed6337b70bea34108d746f4f94376a29894bb8299984afaf6c080`. Changes cover the Audio Editor and its asset catalog plus the shared browser file mirror.

Audio files and encoded WAV output now allow up to 128 MiB. Audio is decoded once at the editor's audio-context sample rate, and bounded sample chunks are encoded in a per-window worker. A save can be cancelled while encoding; closing the window terminates its worker. The file mirror accepts immutable Blobs without an additional eager byte-array copy. Local desktop and phone-sized and live desktop and phone-sized checks exercised the existing edit/save/reopen and conflict workflow. An isolated local account opened and saved a >32 MiB file, checked its samples, and synchronized its result with the server. A separate local worker test created a 128 MiB WAV and checked rejection above the cap. A full 128 MiB application-to-server workflow and physical phones have not been tested; decoded audio and effects can use much more memory than the source. Disposable live test accounts were removed.


## 2026-10-31 — Scientific calculator

Live static release `3e100710ab782e804a58c20988f823735d1d36786e98d5f515ecdf70362799d0`; previous `4b5f72175898b56247e7dc2201a063fe37e00afdbded42ec5ad056d453ca6bf6`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `8bd1586485915a2b0fc4fc6d907647a81c245411899323af2073db2dc1166ab1`. Only Calculator and catalog assets changed.

Calculator now has a touch keypad, powers, common scientific functions, scientific notation, angle-unit selection, and per-window Ans. Expressions are parsed with a bounded arithmetic grammar rather than executed as JavaScript. Calculations remain temporary, and results use floating-point arithmetic. Unit tests cover precedence, inputs and errors; local desktop, phone-sized and 4K-sized and live desktop and phone-sized tests check keypad and keyboard interaction, angles, error messages and independent windows. Physical-phone behavior and broader numerical requirements remain unverified. Disposable live accounts were removed.


## 2026-10-31 — Terminal filesystem guide

Live static release `5bc73539fbab22b64f9b6d776e060d7b339970601dc08bc76fd08602ea0ab657`; previous `3e100710ab782e804a58c20988f823735d1d36786e98d5f515ecdf70362799d0`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `04e2412bffe35c00387221ff0591452e225459d6c672a58ae439aecba1c5c0f2`. Changes cover the Terminal app, its catalog and `terminal.js`.

The terminal command bar opens an in-window guide explaining separate shells, the temporary shared Linux filesystem, copying a Linux file to My files, and basic nano commands. Startup-banner handling also recognizes an interleaved help echo; unit checks cover split and interleaved chunks. Real browser-hosted Linux tests on local desktop, phone-sized and 4K-sized viewports and live desktop and phone-sized viewports exercised separate environment variables, nano save/exit, a file shared between shells, and closing one shell while another continues. A separate local Files test checked explicit copying to account storage and the temporary Linux filesystem reset on reload. Physical-phone touch, arbitrary Linux programs and all startup timing cases remain unverified. Disposable live accounts were removed.


## 2026-10-31 — Selectable and searchable PDF text

Live static release `b51352baed6c388d17f7d1992db7235b8af6e4753a547db7307cb37c30c157fc`; previous `33b8c5196d79043f10e9aeffc517b7066854c181a8bdbc81a2929dfd44627246`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `327079eb233224758348e54df96e8e85f44b08a16cb3bf55115e44a7974c6aae`. Changes cover the PDF Viewer and its catalog.

The viewer uses PDF.js to place selectable embedded text over the rendered page and searches locally for matching pages, highlighting their first literal case-insensitive match. A changed query cancels the previous search; closing or replacing the document invalidates pending work. A visible message explains that scanned image-only pages cannot be searched. Local and live desktop and phone-sized tests cover selection, find, cancellation, navigation, resize, malformed-file recovery and close; desktop tests also use a mouse drag to select text. Disposable live accounts were removed. This is page-by-page search, not navigation between every occurrence; OCR, annotations, forms, physical-touch selection and broad complex-PDF compatibility remain unverified or unsupported.


## 2026-10-31 — G-code parsing and unsupported modes

Live static release `cf7adfc67c26b8ad32c24632a423e398ca9c5e373a380190a41119b457355696`; previous `b51352baed6c388d17f7d1992db7235b8af6e4753a547db7307cb37c30c157fc`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `b36860757f7b6e98906df125d5b083b3f3d0e6948f9865e7c16e8953595a3e1a`. Changes cover G-code Preview and its catalog.

The existing library parser runs in a cancellable worker; a hash-pinned build patch exports it without changing parsing behavior. A local visual parity test compared the example pixel-for-pixel with the prior live renderer. Local desktop, phone-sized and 4K-sized and live desktop and phone-sized tests cover example, upload, sync, unsupported files, travel toggle and fresh-session reopen. A separate local worker test checked 100,000 parsed moves and responsive cancellation of 500,000 moves while retaining the previous view. Relative positioning (G91), inch units (G20), numbered move commands and G92 XYZ resets are rejected rather than knowingly visualized incorrectly. These checks do not identify every unsupported controller command. Rendering and transferring parsed commands still use main-thread work and memory; the 128 MiB file-service limit is not a demonstrated device capacity. Physical touch and hardware/controller validation remain unverified. Disposable live accounts were removed.


## 2026-10-31 — Files conflict recovery and upload destination

Live static release `6b98de55cfe3d093a61e5cd228d079c1f2a7d3201495f79edab2e6077b270b1e`; previous `cf7adfc67c26b8ad32c24632a423e398ca9c5e373a380190a41119b457355696`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `0050dd558f5dba526793d4aee2257f4b508b8242f439fdd3b2176bd989ee58d3`. Changes cover Files and its catalog.

New / Upload is visible on desktop as well as touch. Upload binds to the chosen drive and folder; a location change before accepting a chooser requires choosing again, and navigation after upload begins cannot redirect it. Account uploads pass immutable browser Files to the mirror without an extra eager byte-array copy; temporary Linux uploads keep their existing byte path. For conflicting edits, users can save the device version under another name before resolving; replacing either side requires confirmation. Deletion conflicts explicitly offer restoring the server file or confirming deletion. Local desktop, phone-sized and 4K-sized and live desktop/phone-sized tests checked conflict preservation, cancelled replacement, deletion recovery and destination binding; the full two-winner conflict test also passed locally and live on desktop. Existing local Files → Text and context-menu workflows passed. One repeated live phone upload test hit the shared 429 request limit; a later retry reached the server. The 100-user capacity target remains unverified. Disposable live accounts were removed.


## 2026-10-31 — Reduced idle file polling

Live static release `c079370703f3f8b8251641019c26e6069263ea65605b498a7822940583fc1d0f`; previous `6b98de55cfe3d093a61e5cd228d079c1f2a7d3201495f79edab2e6077b270b1e`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `d37cc248b551539f65d6424bf5258c5570155aa49c47f9955bea28280ea6476d`. Changes cover the Files app, its catalog and the browser mirror.

Successful idle mirrors now poll at approximately 60 seconds in visible tabs or four minutes hidden, with jitter; pending or failed work retains the shorter retry schedule. A stale tab refreshes on becoming visible and writes still initiate sync immediately. Files provides Sync now (Refresh for temporary Linux) to explicitly discover server changes. Unit and real local/live browser checks cover scheduling, stale-tab refresh, manual server-change retrieval, pending retries and cleanup; local desktop, phone-sized and 4K-sized plus live desktop and phone-sized manual-sync checks passed. The live 429 retry fixture also passed. Disposable live accounts were removed. The shared issuer bucket and full directory scans remain; 100 visible idle users could still exceed the issuer limit before active work, so this is not a 100-user capacity result.


## 2026-10-31 — Data Explorer analysis projects

Live static release `481ce1de8fac535c0f632b6003c2ba08d51c9fd8e413a9be1bd03d15f6a0a8c6`; prior staged release `d03aeb5e4d6ba80a2259e36e333a915175edd839776939e14894861590e43f1e`; previous feature release `c079370703f3f8b8251641019c26e6069263ea65605b498a7822940583fc1d0f`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `f648c0a24f8b4c11431c3a88e8ead8ea5921a4d93b5476f1ce01578c03f3a2b8`. Changes cover Data Explorer, the shared picker/route, the desktop close guard and app catalog.

Analysis projects save SQL, Perspective settings and a source CSV path/hash in My files; they do not embed the CSV. Reopening confirms changed source content, checks versions before replacement and rolls back failed SQL/project loads while keeping the prior analysis. Unsaved query/chart changes warn on close or replacement. Save locations and CSV export are collapsed for screen space. Compound project extensions now work in the shared file picker. Local desktop, phone-sized and 4K-sized and live desktop/phone-sized tests cover project save/sync, fresh-session reopen, close cancellation, stale writes, changed-source confirmation and invalid-project recovery; the existing CSV export workflow passed locally. A local >32 MiB CSV with 140,000 rows opened and queried; 128 MiB is allowed but not proven in this app, and device memory may be limiting. One live phone run hit the known shared 429 limit; a later retry passed. Disposable live accounts were removed. Physical touch and large-file device coverage remain unverified.


## 2026-10-31 — Bounded account inventory

Gateway worker `8ed6e9ab142e00b58c5902bb0be8e8b608b43a4cd630dc86ee15477f9c0dc576` replaces `541d74f9042d34c3514a2b27cfee708104f0879194232720e864e9b3af329040`; the protected code-upgrade helper preserved permission bindings and file state while restarting the file service and issuer. The dependency lock was preserved from the existing worker. Live static release `5797493e5496138f2f513da997ffe616e6cf851c96ef7dbe44da2aeaf9250675` replaces `481ce1de8fac535c0f632b6003c2ba08d51c9fd8e413a9be1bd03d15f6a0a8c6`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `7fe22c03b7a6559c4ada7205cf6e87dfe0032257b7bbcfb`.

The signed account inventory returns a complete bounded directory tree or an empty incomplete result, which makes the browser fall back to ordinary per-directory listing. It retains the existing list permission and account isolation; the mirror rejects malformed or incomplete data rather than interpreting it as deletions. Local signed authorization tests cover separate accounts, revoked permission, anonymous denial, bounds and fallback. Local and live browser tests observed one inventory request instead of seven listings for six folders; both detected same-size changes, including a direct live disk edit. A local eight-account mixed test with an overlapping 2 MiB upload completed in 0.831 seconds after setup (max inventory 0.066 seconds); this is not a 100-user capacity result. Existing local file-conflict recovery and live manual sync passed. Disposable live accounts were removed. The shared 60-per-minute issuer bucket remains and can still limit 100 users even for empty accounts; fair admission and reduced authorization overhead require further work.

## 2026-10-31 — Replicad model preview

Live static release `e0545e2edfa82c963c07db4410e53bf685d69b4efb0822bf3a875f8a7813e204` replaces `5797493e5496138f2f513da997ffe616e6cf851c96ef7dbe44da2aeaf9250675`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `0002b30b8e6e5d21d9c792e531cccf93d4aec72ec89ff5e404009d6ee67f9a4f`. A rejected activation attempt had a mistyped manifest hash and made no hosting changes.

Replicad builds a rotatable and zoomable 3D preview from the actual worker-generated STL, with an explicit stale-preview notice after parameter or project changes. Each app window owns and releases its preview renderer, controls and worker. Local desktop, phone-sized and 4K-sized tests and live desktop and phone-sized tests verify rendered rotation, project upload/open/save, server sync, export geometry/STEP header and closing/reopening. Live disposable accounts and their files were removed. Tests use emulated screen sizes and mouse input; physical phone gestures and physical manufacturing validation are not proven. WebGL is required for preview; the app remains a box/cylinder generator with no general CAD scripting or assemblies.

## 2026-10-31 — Digital Logic gate examples and upload snapshot

Live static release `61be28a2d115b78ee0bbe9f94f846fc11f556a51d71459a15d9ca2e6254f8b0d` replaces `e0545e2edfa82c963c07db4410e53bf685d69b4efb0822bf3a875f8a7813e204`; the intervening release `14d7f1c2584334fb38c99f6e2f191ee5e33ed065158802a46fe0cdfae85994f2` introduced the gate examples before the storage fix. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `1387891dd66ab827853b89dea3bcd93e320d6fa18bd7a7e01362d1a1334735da`.

Digital Logic offers AND, OR, XOR, NAND, NOR, XNOR and NOT examples with descriptions. Loading an example creates a new unsaved circuit and does not overwrite the previously opened file. Local desktop, phone-sized and 4K-sized tests check every truth-table row, cancellation and disposal; local and live desktop and phone-sized account tests check upload, save, server sync, fresh-session reopening and preservation of the original. A live phone-sized test reached saving the XOR example but hit the shared 429 gateway limit during sync; a later retry passed. Physical touch and hardware behavior remain unverified.

The live test exposed an existing shared storage bug: saving an uploaded browser `File` directly to IndexedDB could leave it backed by the original computer file. If that source disappeared, the browser copy became unreadable. The mirror now snapshots the bytes used for hashing into a browser-owned Blob before saving. A controlled live negative test reproduced `NotFoundError` on the old code; the new code passed the same offline source-deletion/read/online-sync test locally and live. Local 32 MiB and 128 MiB source-deletion tests passed with hash-checked bytes and server sync, and mirror regression tests passed. This fix does not recover already-unreadable older copies. Snapshotting requires temporary memory proportional to file size; physical-phone memory behavior has not been measured. Eight disposable live accounts were removed.

## 2026-10-31 — Arduino serial monitor and desktop fonts

Live static release `f56968169f054fedb49bc0beae37cfb5a0056cee17297383ecf6fd68e0ac69f5` replaces `61be28a2d115b78ee0bbe9f94f846fc11f556a51d71459a15d9ca2e6254f8b0d`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `1b8828f181341a4d14bdaae9c7db79442a71a3425503a497cfc5025854bcbc03`.

Arduino Simulator has a two-way UTF-8 serial monitor and a bundled, compiled ATmega328P serial echo example with C source and rebuild instructions. A bounded 1,024-byte input queue waits for the emulated receive register and firmware to consume each byte; a full queue leaves unsent text in place, and stop/restart clears the queue. Queuing is not proof of delivery to firmware. Local desktop, phone-sized and 4K-sized and live desktop and phone-sized tests cover Blink, a 200-character echo, UTF-8, queue overflow, restart, independent window serial output, upload and existing account-file workflows. The echo example was saved, synced and reopened in a fresh session locally and live at phone size. Three disposable live accounts were removed. Tests do not prove physical touch, timing accuracy, every UART configuration, physical hardware or unmodeled peripherals.

The desktop CSS referenced three absent fonts, producing 404s and already falling back to browser system fonts. The stale declarations and names were removed, retaining the existing system-font fallback without adding bundled font dependencies. The browser tests check that those missing font requests no longer occur. A phone test initially clicked a covered first simulator window while a second fullscreen window was active; the test now focuses the intended window before interaction and passed. Two earlier checks raced the local server startup and failed with connection refused; reruns after readiness passed.

## 2026-10-31 — Pico firmware loading and serial console

Live static release `0fecbf06b9dbb3713c58bdb0316ab79204d9f2e93544f707c37701204c66fc4b` replaces `f56968169f054fedb49bc0beae37cfb5a0056cee17297383ecf6fd68e0ac69f5`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `273f0eee89974f3e5016ced9430fc31113ea911405f06c165e6ee5c506dad273`.

Pico now starts when ROM and UF2 are selected in either order. Serial commands are admitted atomically only when the USB device is ready and its 512-byte FIFO has room; too-long or rejected commands stay in the input. The console has Ctrl+C and Ctrl+D and streaming UTF-8 output decoding. Input is encoded as UTF-8, but the tested MicroPython 1.20 interactive REPL dropped non-ASCII input; Python escapes worked. A unit test fills the actual USBCDC FIFO and proves a rejected message does not alter it. Local real-firmware desktop account testing covers both loading orders, a 200-character command, Unicode output, interrupt and soft reset, flash save/sync, competing saves, invalid-project recovery and cleanup; a fresh phone-sized session reopens saved flash. Local phone-sized and 4K-sized Blink and live desktop/phone-sized Blink tests passed, including preservation of input when no serial firmware is running. Two disposable live accounts were removed. Private ROM and firmware were used only in the local test. This does not establish general firmware compatibility, physical touch, full SSI behavior or hardware timing.

Test development exposed that Puppeteer keyboard typing did not faithfully enter non-ASCII text and that MicroPython's tested interactive REPL dropped raw non-ASCII input. Tests now use explicit input values and Python escapes to check UTF-8 output; they do not claim that raw Unicode works in this REPL. A project-loading test also initially waited on an old prompt or a window title that was not refreshed; it now waits for the selected project path and the new prompt. One local test raced other registration tests and timed out at login; the isolated rerun passed.

## 2026-10-31 — Circuit Simulator examples and change detection

Live static release `41004df7cb57468467c03b54c29eecc44373ca21d90967a30d1d2cab9a35270f` replaces `0fecbf06b9dbb3713c58bdb0316ab79204d9f2e93544f707c37701204c66fc4b`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `b83e225b33bd9ada9fffab8bbfc398f988ab6723b938968762e1a45c45bce74d`.

The simulator now offers a voltage divider, RC low-pass filter and half-wave rectifier with short explanations. Loading one starts a new unsaved circuit; an asynchronous load refuses to overwrite a circuit edited while the example was loading. CircuitJS's full export includes changing capacitor/inductor state; an integration API now exposes its upstream design-only export for comparison, while full exports remain the saved files. Scope-only changes are protected by a conservative full comparison after iframe interaction. Consequently a non-editing interaction with a running circuit can sometimes cause a save warning; the design-only serializer omits scopes and is not a standalone scope-change detector.

Local desktop, phone-sized and 4K-sized example tests and live desktop/phone-sized tests cover component presence, changing RC output, cancellation, scope-change warnings, save/sync and fresh-session reopen. A local and live phone-sized delayed-example test preserves a concurrent resistor edit; the live test reached cleanup and then hit the shared gateway 429 limit, after its functional checks. Existing local account tests passed for 5 V and 6.67 V divider output, upload, failed-open preservation, Ctrl+S, close warning, independent windows and iframe cleanup. Corresponding source and GPL notices remain packaged; the served source archive was fetched in an authenticated live test and its integration source and manifest were checked against the build. Four exact disposable live accounts and their files were removed. Physical touch, broad circuit fidelity and hardware validation are not proven.


## Kiri:Moto workspace snapshots — 2026-10-31

Release `b1d263b34c9db8c4842f3119a814f3e2c2c8b5cadec0716db6daf24aab058a9e` adds explicit `.kiri` workspace snapshots to My files, including model geometry and slicing settings. Opening validates in an isolated temporary workspace before confirmation and replacement; stale file versions are checked. Later edits require another save. Local and live account tests passed save/sync, malformed-file rejection, fresh phone-sized session recovery, restored slicing, and closing while validation runs. A local phone-sized mesh/slicing regression also passed. Tests use upstream APIs for some operations and do not establish physical-touch usability, exhaustive file validation, printer profile correctness or physical fabrication safety. Mesh:Tool project state remains browser-local.


## Mesh:Tool workspace snapshots — 2026-10-31

Release `08c4eb2fdbd9ddfc950941007590c029845c135a1940c615bfe3e3b2813391c5` adds explicit `.meshproj` account-drive snapshots of the editable Mesh:Tool document. The format stores mesh geometry, groups, sketches and document metadata, but not revision history; changes after saving require another snapshot. Open validates in an isolated temporary editor before asking to replace the current work; stale saves are rejected. Local desktop, emulated-phone and 4K-sized tests and a live desktop-to-emulated-phone account test cover upload, a moved model and circle sketch, save/sync, corrupt-project recovery, stale saves, reopen and temporary validation cleanup. The shared Kiri snapshot regression passed locally. The exact disposable live account was removed. Tests use upstream APIs for some edits, so physical touch, broad sketch/model coverage and fabrication safety remain unverified.


## Audio Editor recording lifecycle — 2026-10-31

Release `afbc323e8af9fb294f002ce2c38f72bdad79479eb1574effd3a73b688cf696a3` warns before closing an Audio Editor window while its microphone is active or permission is pending, in addition to unsaved edits. Opening or saving is blocked while a microphone is active to avoid saving an incomplete recording. Window-owned media streams are stopped on disposal, including delayed permission results; the recorder is cancelled and waveform resources are destroyed. A local desktop and emulated-phone and live emulated-phone simulated-microphone test covers independent windows, the New Recording modal, declined and accepted close, and delayed permission. Local and live account tests cover upload, edit, WAV save, sync and fresh-session recovery. These tests do not establish physical microphone or phone touch behavior. Three exact disposable live accounts and their checked test files were removed.


## G-code units and coordinate resets — 2026-10-31

Release `b0721278def821abf6eb215d83dcf009cd48c2bdf0bcc1700f9377c1e475d4bd` converts G20/G21 units and G92 XYZ coordinate resets to millimeter paths, including switches between absolute/relative motion and extrusion; G92.1–G92.3, unsupported work offsets and non-XY arc planes are rejected. It starts at zero without stored machine offsets and does not simulate initial homing; homing after movement is rejected. Local desktop, phone-sized and 4K-sized account workflows compared equivalent rendered paths; worker tests compared mixed units, XYZ reset, extrusion and XY arc parameters, and large-file cancellation passed. On the live phone-sized test, two screenshot comparisons were obscured by the floating voice notification; the corrected large fixture then hit the existing gateway request limit. A reduced live account-file test without that overlay passed rendered metric/inch and reset/no-reset comparisons, and live worker parameter comparisons passed. Five exact disposable live accounts and checked fixtures were removed. Physical touch, controller compatibility and hardware safety remain unverified.


## Files sync status — 2026-10-31

Release `87f37964f1b08edec68d71acaffe2e0a6fe3358f81581c2f894b4cd4203cf113` distinguishes the initial server check, local changes waiting for sync, server-check failures and a completed check. A manual Sync now error no longer remains on screen after an automatic retry succeeds. Local desktop, phone-sized and 4K-sized tests and a live phone-sized test held the initial check, injected a 429, verified the message and automatic recovery, and verified a pending local edit arrived on the account server. Local Files → Text save/reopen and manual server-change sync regressions passed. Tests accelerated retry timers and injected the limits; physical touch and the 100-user capacity target are not proven. The existing shared proxy-observed issuer bucket and gateway concurrency limits remain unchanged. The exact disposable live account and checked fixture were removed.


## Local file admission candidate — 2026-10-31

An undeployed candidate separates file-issuer request budgets by live registered account while retaining a server-wide ceiling and a bounded legacy bucket. A token is used for admission only; signed one-use operation proof and account policy still decide access. A local browser test verified two independent accounts and credential-bearing challenge requests, and 35 issuer security tests plus the full HTTP gateway suite passed. In a bounded local 100-account, one-file-each fixture at concurrency three, all inventories passed (2.479 s total; p95 86 ms), but only 27 subsequent version checks passed before the gateway shared budget limited 73. The fixture used permissive account setup and is not a 100-user capacity claim. Source and tests need guarded packaging and live validation; login bursts, fairness under abuse, large transfers and the gateway budget remain outstanding.


## Account-scoped file admission live — 2026-10-31

Issuer `/srv/codi-connected/releases/file-admission-r1` manifest `037c6d174937f7f5df2f144e25d305b429a2b628b6b5eb62418ab06b6f111804` and file worker `/srv/codi-gateway/releases/file-admission-r1` manifest `6d5d37380cce9c40c259b55c8ad87f6c11836c55c76640dc93fd7ef9f43a6160` are active. Worker upgrade first retained permission bindings; a live two-account browser check verified compatibility with the previous issuer. The guarded issuer upgrade preserved state and restarted the previously active issuer, steward and guest roles. Afterward, a public browser test performed 62 signed inventories across two registered accounts and checked account-file isolation; four exact disposable test accounts and checked fixtures were removed. Managed config SHA256 values: native `4fa0934edfd6b2794ac9e516440c02efa959f833ae4da4630f72f8c89f62b8fb`, file `3556db9d9ec2777811f28801cb73f880185439bd0203a54ef81962ec0349215e`. Live client and issuer use per-account admission, bounded legacy and server-wide buckets; authorization still requires the existing one-use proofs, current session and permission checks. Local security, browser and bounded 100-account fixture results are recorded in `docs/ACCOUNT_STORAGE_CAPACITY.md`. The gateway shared 256-request/minute limit, four active requests, login bursts and 100-user end-to-end capacity remain unresolved.


## Local combined file inventory candidate — 2026-10-31

An undeployed candidate combines bounded account inventory and file hashes into one signed request, with a 64-file/32 MiB hashing budget and fallback for the rest. Local security and browser tests cover permission revocation, separate accounts, symlinks/hard links, direct same-size disk edits, invalid metadata, both older-protocol fallbacks and file-conflict preservation. A local 100-account fixture with one 4-byte file each and three concurrent requests completed all combined checks in 2.647 seconds after account setup, p95 91.08 ms, using 200 gateway requests; this is not a 100-user capacity claim. Live deployment and broader transfer/load checks remain.


## Combined file inventory live — 2026-10-31

File worker `/srv/codi-gateway/releases/combined-inventory-r1` manifest `2bd92f334f1a29407d33872396cddd51d12d938caa473d33471a5836a0d29084` and static release `fdee484702df0b88b6d032674b337bc937ec8850ec46d07f46269ae1021f320e` are active. Worker upgrade retained account/permission bindings and issuer state. The old mirror passed a two-account file workflow with the new worker before the static switch. The new mirror passed a live phone-sized six-folder combined-inventory test, both legacy-protocol fallbacks, a direct same-size disk edit and a simulated-429 local-edit recovery test. Four exact disposable live accounts and verified fixtures were removed. Native managed config SHA256 `38c688ddc832c04a9fc4861977aa3edbae8cd80dca586b8d72b6a6f25222024b`, file managed config `7a0d8170b5d9c64be5acc010a3ca5e4fe8137e8ccf069318aa8d971ff53b0587`. Local security and bounded 100-account fixture evidence is in `docs/ACCOUNT_STORAGE_CAPACITY.md`. The gateway 256-request/minute and four-active-request limits remain; the one-file fixture and live tests do not establish 100-user capacity.


## Local file gateway burst queue — 2026-10-31

An undeployed candidate keeps the gateway’s four active operations and 256-request/minute budget, but adds up to 128 bounded waiters with a five-second timeout. Local queue tests cover overflow, timeouts, cancellation, disconnect before admission, and releasing slots after a cleanup failure; 18 existing gateway HTTP regressions passed. A local unsmoothed 100-account, one-file-per-account workload with eight edits and one 8 MiB upload completed in 3.405 seconds after setup, inventory p95 2.534 seconds and 218 gateway requests. An issuer/gateway-only 100-check burst improved from 4 successes and 96 immediate limits to 100 successes in 2.241 seconds. The tests do not cover 100 browsers, large transfers, sustained load, or fairness when four slow transfers occupy all slots; see `docs/ACCOUNT_STORAGE_CAPACITY.md` for the memory observation. Candidate requires guarded packaging and live validation.


## File gateway burst queue live — 2026-10-31

File worker `/srv/codi-gateway/releases/file-queue-r1` manifest `3f2017b1bd608c38a13dc9a2d4d1d7e55846425d7611c6df90f2c8b6f17e3528` is active. The protected upgrade retained account and permission state and restarted the issuer and file worker; steward and guest were not restarted. Managed config SHA256 values: native `b395ba4dbb2f0ba6efdc53bae9fa2d6c4d1bacdfee607147c3756e047e5b4d7c`, file `b2ddae756286951b5d609de0aeb1fd5cc307cc0791245b96e26db8c0eb8e94d5`. Live browser checks passed eight parallel signed inventories across four accounts and phone-sized local-edit recovery after injected 429; five exact disposable live accounts and verified fixtures were removed. Local queue tests include disconnected-waiter proof preservation and cleanup-failure slot release; the bounded local 100-account mixed test is detailed in `docs/ACCOUNT_STORAGE_CAPACITY.md`. Four active slots, 128 waiters, a five-second queue timeout and the shared 256-request/minute budget remain. Four slow transfers can still occupy every slot; 100-user sustained capacity, login bursts, physical devices and large-transfer contention remain unqualified.


## 2026-10-31 — Replicad through-hole and volume

Live static release `4b83bfc39bd7ea81b19a890eed09aa465f81f699f880efefd561af9aedc9ce8a` replaces `fdee484702df0b88b6d032674b337bc937ec8850ec46d07f46269ae1021f320e`. Managed hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `180a4e55b59077cbb0b82094164da91061e2619635c648f5bd70eb073e075841`. Backups `/var/backups/webhost-sites/change-20261031T152659173940Z` and `/var/backups/webhost-sites/change-20261031T152659179862Z`.

Replicad now supports one optional centered vertical through-hole in box/cylinder models and reports the CAD solid volume. Older project files default to no hole. Shared model validation rejects invalid dimensions and holes. Local desktop, emulated phone and 4K, plus live desktop and emulated phone, passed upload/open/save, account sync, fresh-session reopening, preview, STL dimensions and measured mesh volume, STEP export, and close/reopen. A unit test covers validation and old project files. The test upload fixture must be in a visible home directory because snap Chromium cannot read its host's private `/tmp` or hidden home directories. Live test accounts and verified fixture files were removed. Physical touch and manufacturing remain unverified; this is still a limited primitive generator, not general CAD.


## 2026-10-31 — Calculator scientific keypad

Live static release `b6cbd988a87307b846e5b0dd6a53cd98317ad9169dac30f883dbf132f2ce8c4b`; prior release `5a66937dec8e3335609c0a0787a4d006ffda61f127cdb66bee2eeb4dd872489b`. Generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; hosting manifest SHA `9dcc02206b31bc618f6d2f5299b2c07e8adcc4d9acb19b5c6eaab4dd312b4852`. Managed rollback inputs `/var/backups/webhost-sites/change-20261031T152939977882Z` and `/var/backups/webhost-sites/change-20261031T152939978357Z`.

Calculator adds inverse sine, cosine and tangent (honoring angle units), exponential function and scientific notation keypad entry, with an EE explanation in the app. Unit tests cover inverse and domain behavior. Local desktop, emulated phone and 4K, plus live desktop and emulated phone, exercised keypad input, units, errors and independent windows; the final explanatory text was checked live at phone size. Disposable live accounts and empty homes were removed. Floating-point and physical-touch limitations remain.


## 2026-10-31 — Files Move to action

Live static release `a148b7bf4fbf77cc86f1b9cb677871d2ce589402402303aadde796bd723b788c` replaces `b6cbd988a87307b846e5b0dd6a53cd98317ad9169dac30f883dbf132f2ce8c4b`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; hosting manifest SHA `ed485f536701384dac056ff9fed4ff6d3fbfda137bcdf2034ea13c78c11568d8`. Managed rollback inputs `/var/backups/webhost-sites/change-20261031T153237950509Z` and `/var/backups/webhost-sites/change-20261031T153237950914Z`.

Files offers a Move to… action for a single file in My files, using the shared folder chooser and existing version-checked, server-journaled move. Cancel, same-folder choice, destination collision, source change during selection, successful sync and fresh-session reopening passed local desktop, emulated phone and 4K, and live desktop and emulated phone. Test fixtures/accounts were removed. Files and destination folders must finish syncing; folder moves and physical-device touch remain unverified or unavailable.


## 2026-10-31 — Digital Logic full-adder example

Live static release `28a74ac3d051cff4b30c48f9785c7ae092bfbe4544082adb8af2877d1e8024b3` replaces `a148b7bf4fbf77cc86f1b9cb677871d2ce589402402303aadde796bd723b788c`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `d5671ed2c4102a7dcbb5f3b094c011b3a7bf296b5d84dd56c1aa293497a04df1`; managed rollback inputs `/var/backups/webhost-sites/change-20261031T153541536243Z` and `/var/backups/webhost-sites/change-20261031T153541542174Z`.

Digital Logic includes a full-adder example using XOR, AND and OR gates. Local desktop and phone-sized tests compare generated truth tables and interactive outputs for all eight combinations. Local desktop, phone-sized and 4K and live desktop and phone-sized account tests cover project/CSV save, sync and fresh-session recovery. Disposable live accounts and verified fixtures were removed. Simulation is combinational logic only; it is not timing, electrical or hardware validation. Physical touch remains unverified.


## 2026-10-31 — Files copy and accessible rename

Live static release `20a32d10892ea4a5ac60a4680f0d5bd608729ab0a11a56f214aebaf9822f9339` replaces `28a74ac3d051cff4b30c48f9785c7ae092bfbe4544082adb8af2877d1e8024b3`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `76e0f64ed841a4f296d371e19a02a388f7c247cd5b26758a563f7cd8b3faff81`; managed rollback inputs `/var/backups/webhost-sites/change-20261031T153755719392Z` and `/var/backups/webhost-sites/change-20261031T153755719818Z`.

Files now exposes Rename on the toolbar and Copy to… for a single My files file. The chooser asks for a destination and name, rejects existing targets or stale/conflicting sources, and creates a separate browser-first copy for synchronization. Local desktop, phone-sized and 4K, plus live desktop and phone-sized checks cover cancellation, collision, stale source, same-folder and other-folder copies, rename, sync and fresh-session recovery. A phone-sized move regression also passed locally. Disposable live accounts and verified fixtures were removed. Copying and moving folders remain unsupported; physical touch is not yet tested.


## 2026-10-31 — Spreadsheet intermediate arithmetic errors

Live static release `4ccf87ee51d4f2fb0b579339abcc3a0ddd8d97452296fef75a903ac03bfadbef` replaces `20a32d10892ea4a5ac60a4680f0d5bd608729ab0a11a56f214aebaf9822f9339`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `88a89ee1a75700517d63f5088946c529cffb73a116cf0070878872dbe9333634`; managed rollback inputs `/var/backups/webhost-sites/change-20261031T154000455673Z` and `/var/backups/webhost-sites/change-20261031T154000456075Z`.

Spreadsheet now propagates intermediate nonfinite arithmetic results as errors; previously expressions such as `=1/(1/0)` could misleadingly display zero. Formula unit tests cover division by zero, non-real powers and overflow. Local desktop, phone-sized and 4K and live desktop/phone-sized account checks cover displayed error, preventing CSV overwrite, correction, sync and fresh-session reopening. Disposable live accounts and verified fixtures were removed. This remains a bounded formula subset, not full Excel compatibility.


## 2026-10-31 — Image Editor metadata checks

Live static release `44fc3629dc7512f85fb7d14f46f7c653429a36acc983127df2aeaf971bf1b5d7` replaces `4ccf87ee51d4f2fb0b579339abcc3a0ddd8d97452296fef75a903ac03bfadbef`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `aa7e3b74de16c69ea498549e6eefb7b847b24f443fd327c82e829e76e742414b`; managed rollback inputs `/var/backups/webhost-sites/change-20261031T154253781357Z` and `/var/backups/webhost-sites/change-20261031T154253781757Z`.

Image Editor watches versions and checks Save As destinations via metadata instead of reading the full image, and checks the original account before and after an ordinary save. Local desktop, phone-sized and 4K and live desktop/phone-sized tests instrumented reads, exercised collision cancellation and verified stale saves cannot replace a changed image. The existing Save As resize/sync/fresh-session regression passed locally and live at phone size. Disposable live accounts and verified fixtures were removed. Account switching during an in-flight save was guarded in code but not separately simulated; physical touch remains unverified.


## 2026-10-31 — Image Editor account-switch check

No production code or hosting change. Local desktop, emulated-phone and 4K and live desktop and emulated-phone tests registered two accounts in one browser, saved different same-named images, delayed the first account’s image encoding during an actual account change, resumed it, and confirmed neither stored image was changed. Both tabs retained their account-specific image; a return to the first account recovered its original. Four verified disposable live accounts and their fixtures were removed. This closes the specific account-switch test gap noted above, not a general multi-account security audit.


## 2026-10-31 — Desktop Help workflow review

No production source or hosting changes. Local desktop, phone-sized and 4K and live desktop and phone-sized registered-account checks verified the beta/support wording, exact mailto link, temporary Linux filesystem explanation, no horizontal overflow and three repeated open/close cycles. Disposable live accounts had no account-file homes and were removed. Help has no document or network workflow. Physical-device testing remains open.


## 2026-10-31 — Student guide coverage

Updated `USER_GUIDE.md` against the current Applications menu and app READMEs. It now covers the live interactive applications, touch-friendly file copy/move/rename, the lack of a general download action, editable projects versus exports, and relevant simulation/fabrication limits. A source check confirms every current interactive menu application is named. The guide is a repository document, not a newly added link in Desktop Help; no production assets or hosting were changed.


## 2026-10-31 — PDF Viewer file-change notice

Live static release `d4e14f1797a44a0e273e1ce4bd714072347ac264e01f2f182a02e9a795e0a19b` replaces `44fc3629dc7512f85fb7d14f46f7c653429a36acc983127df2aeaf971bf1b5d7`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `eada7409657eb2a9dfc3c72bec591ac47aad64db1fc0929e2a880622dd1eb2bf`; managed rollback inputs `/var/backups/webhost-sites/change-20261031T155240907448Z` and `/var/backups/webhost-sites/change-20261031T155240907857Z`.

PDF Viewer checks metadata and compares content hashes rather than rereading PDF bytes on every file notification. A changed, conflicting, missing or temporarily uncheckable file now has a separate notice that persists when paging; opening another copy resets it. A same-content version change does not produce a false change notice. Local desktop, phone-sized and 4K and live desktop and phone-sized tests instrumented reads and covered same-content changes, real changes, deletion, paging and reopening. The existing full phone-sized navigation/search/failed-open test passed locally and live. Disposable live accounts and verified fixtures were removed. Physical touch remains unverified.


## 2026-10-31 — PDF Viewer reload action

Live static release `dad82e4aef4aa848d143b32595c827e792867367983614375c9d66de5f142825` replaces `d4e14f1797a44a0e273e1ce4bd714072347ac264e01f2f182a02e9a795e0a19b`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `0637dab3bef742291cacbad8679c4d7d3754b189e335a1f6a7a1c32a24eba313`; managed rollback inputs `/var/backups/webhost-sites/change-20261031T155512469753Z` and `/var/backups/webhost-sites/change-20261031T155512470168Z`.

PDF Viewer offers Reload for an account-backed PDF. It reopens the saved file without a picker; a failed reload leaves the current page and file notice visible. Reload is disabled until an account file is opened, and for an unsaved preview. Local desktop, phone-sized and 4K and live desktop/phone-sized tests covered the action, changed and deleted files, and preserving the page on failed reload. Disposable live accounts and verified fixtures were removed. Physical touch remains unverified.


## 2026-10-31 — PDF reload checks the server

Live static release `b78903ccd9f59eeb6d7556bf60ef390c35d4ce76376fd3beadb130d61bcbb83b` replaces `dad82e4aef4aa848d143b32595c827e792867367983614375c9d66de5f142825`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `2bed6cd1cf6e9bf6bed0e63c94678a3c27458aa6632603038fcef90da9f58f45`; managed rollback inputs `/var/backups/webhost-sites/change-20261031T155757760839Z` and `/var/backups/webhost-sites/change-20261031T155757761253Z`.

Reload now runs account sync before reading the file, rather than relying on the browser’s potentially stale mirror. A failed sync leaves the current page visible and reports that the server could not be checked; a newer open invalidates an outstanding reload. Local desktop, phone and 4K and live desktop/phone tests used separate browser contexts for a server-side update, plus an injected sync failure. A delayed reload followed by opening another file was checked locally at phone size and live at both sizes. Existing missing-file/notice regression passed locally. Verified disposable live fixtures and accounts were removed. Sync checks the account mirror, so large accounts or a busy server may take longer; conflicts still require Files.


## 2026-10-31 — AVR browser compiler research

No live or app integration change. Two pinned browser-local AVR toolchain candidates compiled an Uno pin-13 sketch, and each resulting HEX drove the existing AVR8js simulated LED in a localhost-only probe. The first took about 1.04 seconds in its worker; the second took about 13.5 seconds using a research worker wrapper. These are single-machine, warm-cache observations with different build strategies, not a benchmark. Both invalid-sketch diagnostics need work. The first package’s own wrapper license and exact corresponding WASM build sources were not established; the second has public GPL source/build recipes but exact release source/reproducibility and notices still need review. Current v86 image lacks AVR build tools; no v86 timing was measured. See `docs/AVR_COMPILER_EVALUATION.md` and `tests/avr-compiler-probe.test.mjs`; no third-party binaries were committed or deployed.


## 2026-10-31 — AVR compiler candidate diagnostics

No live or app integration change. The `avr-v1.0.0` upstream browser example was found to ignore an actual `cc1plus` failure in Arduino `new.cpp`, because an extensionless header was omitted; it also continued after sketch compilation errors. A hash-checked research patch includes that header, rejects recognized compiler-error diagnostics, and exposes the original sketch at the line-directive filename so errors show the correct source. A localhost test rejected an invalid sketch at its source line, accepted a warning containing `error`, and compiled C++ `new` firmware that lit the existing AVR8js simulated LED. The test and patch script are in `tests/`; the exact vendor bundle and third-party binaries were not committed or deployed. The diagnostic check is a limited English-text heuristic, warnings are not yet surfaced, and distribution/source, robust exit handling and app workflow remain unfinished.


## 2026-10-31 — AVR candidate numeric exit status

No live or app integration change. The pinned Emscripten compiler exposes `callMain`, which returns the numeric tool exit status, while its four binutils wrappers did not export that function. The hash-checked research patch now exposes it in those exact wrappers and invokes each tool with `noInitialRun`, prepares its filesystem, checks the numeric result, then reads outputs. Local browser tests verified nonzero compiler, assembler and linker failures, a warning containing `error`, corrected sketch source lines, and successful C++ `new` firmware lighting the AVR8js LED. The patch was reproduced from fresh pinned inputs, and a changed input was refused. Successful warnings, other tool failures, lifecycle/resource bounds, app integration and exact distribution/source review remain open. No vendor binaries were committed or deployed. The pinned research archive and extracted candidate remain temporarily under `/tmp/codi-avr-exit` for the next integration step, to avoid repeated downloads; remove them after that work.


## 2026-10-31 — AVR compiler packed-input research

No live or student-facing app change. A local research worker loads 429 pinned compiler inputs from one 4,934,010-byte compressed indexed asset instead of individual header requests, bounds unpacking and source size, and uses same-origin tools. The candidate app bundle was 48.22 MiB total before HTTP compression. Under a loopback server with desktop CSP, tests compiled valid/invalid sketches, ran resulting HEX in AVR8js, exercised termination and showed one canceled worker did not stop another. The regular generic app builder packaged the compiler as one worker and 11 assets (28 total files), and an isolated registered-account desktop test exercised that exact bundle under normal CSP. Stage hashes reject modified inputs; an independently staged bundle matched the tested hash. This remains research: no sketch UI/My files workflow, production resource/timeout policy, complete corresponding-source review or distribution; no compiler binaries were committed/deployed. The temporary candidate cache remains `/tmp/codi-avr-exit` for ongoing work.

Arduino compiler follow-up: the disposable candidate now has a sketch editor with open/save, a cancelable build, diagnostics, stale-edit protection, and automatic simulated execution. See `docs/AVR_COMPILER_EVALUATION.md` for the precise mock-storage test scope and release blockers. This is research only: no live compiler or student-facing sketch UI was deployed, and vendor compiler assets are not in Git.

The isolated Arduino sketch research now uses the actual account-backed My files service in `tests/avr-sketch-account-research.test.mjs`; its desktop/frontend source adds a sketch unsaved-close guard and a live-updating shared picker. Tested locally only, not deployed. The compiler candidate remains unapproved for distribution. See the AVR evaluation for scope and remaining work.

Shared My files picker follow-up: the local source refreshes an open picker when the mirror changes, avoids rebuilding unchanged visible rows during sync, restores the focused row after a real list change when possible, and unsubscribes on completion/abort. `tests/shared-file-picker-updates.test.mjs` passed addition, removal, filter, focus and cleanup checks in isolated account sessions at 1366, 412 and 3840 CSS pixels. The actual Text upload, browse, edit, sync and reopen regression also passed locally; Chromium required the fixture under a snap-visible home directory, and that desktop-menu test now waits for the editor and uses an explicit desktop viewport. An earlier 4K run exposed a detached row during redundant list refresh and prompted the source correction. Changes are backed up as source only and are not deployed; physical-device tests remain open.

## Shared picker live update — 2026-10-31

Live static release `50239271e19c042197b65efd7a1c7856f6860b60dd152d25f7d4b902b1e39242` replaces `b78903ccd9f59eeb6d7556bf60ef390c35d4ce76376fd3beadb130d61bcbb83b`. The staging script verified every old asset and only `desktop-apps.js` plus the derived cache manifest and worker changed. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; hosting manifest SHA `3cdf5fcc540104d04d851047d14fa06cb7d50c61171c08bac917b0021cc59d19`; managed rollback snapshots `/var/backups/webhost-sites/change-20261031T163120549889Z` and `/var/backups/webhost-sites/change-20261031T163120550356Z`. Old release retained for rollback. Public source hash, root, `/desktop/` and `/blog/` checks passed. A signed-in phone-sized public Chrome smoke tested dynamically updated rows, selection and subscription cleanup with mocked file rows and no file writes; the exact disposable account and its sessions were removed, and it had no server file home. Real account storage, Text workflow and viewport tests passed locally as recorded above; physical touch remains unverified. No Arduino compiler or research editor was deployed.

G-code Preview local source supports a conservative subset of coordinate-only modal linear moves after an explicit G0/G1, preserving mode across supported positioning, units and extrusion settings. Other commands clear that mode; modal arcs are rejected. Worker checks compare the normalized output with explicit moves and verify numbered lines remain rejected. Local desktop, phone-sized and 4K account workflows compared rendered modal and explicit paths, saved/synced and reopened fixtures. One concurrent phone render comparison and a subsequent existing reset comparison failed at a 250 ms wait; the phone workflow passed after a 1 s render wait. These are emulated viewport tests, not hardware/controller validation. Not deployed yet.

## G-code modal linear move live update — 2026-10-31

Live static release `bb7bb15bef9a42b93a88195600f29641c83f522899ab81e8fbe60710a668db2c`, G-code bundle `733008efe38231753fed93bcb3d04ab535fe35527a4f66620b1d9c40e13d497d`, replaces `50239271e19c042197b65efd7a1c7856f6860b60dd152d25f7d4b902b1e39242`. Only the app bundle, catalog and cache metadata changed. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest SHA `fc1eb4b23989b1adcc980e94e50e04fafea7a1078c9e81b4cfcb850d24eb1eae`; rollback snapshots `/var/backups/webhost-sites/change-20261031T163640713715Z` and `/var/backups/webhost-sites/change-20261031T163640714183Z`. Public phone-sized registered worker tests compared modal and explicit paths and checked unsafe forms; a public phone-sized app-window smoke rendered shorthand from mock file bytes and closed. Local desktop/phone/4K workflows exercised real account file sync and equivalent rendered paths. Two disposable public accounts were removed; cleanup first stopped on an empty account home, then verified and removed that empty directory before deleting the accounts. Physical touch and controller/machine behavior remain unverified.

## Calculator intermediate-result fix — 2026-10-31

Live static release `662c08d6b901247b8a550f32cad6f5e3d9c04ea63329eb4f5467aac560119929`, calculator bundle `7298bb00457c256724277ec2563bfcf8e8f41fe2a54e5187a3391a93109a64ca`, replaces `bb7bb15bef9a42b93a88195600f29641c83f522899ab81e8fbe60710a668db2c`. Invalid intermediate results, including `1/(1/0)` or a hidden overflow, now report an error and retain the previous Ans. Unit tests cover division by zero, overflow, invalid function results and nonfinite literals; local desktop/phone/4K and live desktop/phone-sized workflows pass. A parallel local phone registration timed out; a separate run passed. Two disposable public accounts and sessions were removed. The hosting generator SHA is `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `0d7a8fabc580a32688223abdf5bda2a3288dd2b938d53bc9eb14d489aa6f3b4e`, and rollback inputs `/var/backups/webhost-sites/change-20261031T164014379467Z` and `/var/backups/webhost-sites/change-20261031T164014379921Z`. Physical-device testing remains open.

Pico Simulator source now invalidates older pending file opens when another open or board-control action takes precedence, and checks project metadata instead of rereading the full project before overwrite. Local desktop/phone/4K account tests cover delayed competing opens, sync, stale-save refusal, metadata-only overwrite and window disposal using synthetic UF2/ROM and a fake worker. Actual Blink still passed with the real worker. Real MicroPython firmware was not rerun for this change; physical touch remains unverified. Not deployed.

Pico ordering correction: the first local real-firmware test exposed that a single global open counter canceled complementary ROM and UF2 reads selected quickly. Opens are now ordered by kind; a project supersedes both, and board actions supersede pending opens. Local real MicroPython 1.20 account workflow passed flash save/sync, competing save, recovery and fresh phone-sized reopen; local desktop/phone/4K synthetic tests cover both competing UF2 and overlapping ROM/UF2. Boot ROM and firmware were used only as isolated local fixtures. This correction is source-only, not live.

## Pico file ordering live update — 2026-10-31

Live static release `4e26d0eb95d65f75d0c3dfb25274644863f6e4601dbe55d851c21303d204e31d`, Pico bundle `ee654a85b30b25c4e72278d88431206579349f6f5e2f404595893761f75ced66`, replaces `662c08d6b901247b8a550f32cad6f5e3d9c04ea63329eb4f5467aac560119929`. This is the corrected per-file-kind ordering and metadata-only overwrite check described above. Local real MicroPython and synthetic race tests passed, plus public phone-sized real-worker Blink and unsent-input checks; no private ROM or firmware was uploaded live. The disposable public account was removed. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `d237ae183eadd242c1cf32f7ea100c338d55665fd313e68d85c18b9827c8212a`; rollback snapshots `/var/backups/webhost-sites/change-20261031T164620445931Z` and `/var/backups/webhost-sites/change-20261031T164620446486Z`. Physical-device testing remains open.

## Digital Logic metadata update — 2026-10-31

Live static release `9f0d74f91bb54c58f5f1bc94d12d81ae8712588e1744a23658077b9696a64a2b`, Digital Logic bundle `b85f54d95eb9f1a0a9a34730252ad913f349755da98e56184d5cb933a1ea0f41`, replaces `4e26d0eb95d65f75d0c3dfb25274644863f6e4601dbe55d851c21303d204e31d`. Saved-circuit watching and overwrite checks use metadata when supported, retaining read fallback for older harnesses. Local desktop/phone/4K and live phone-sized registered-account tests verified no full reread for checks, sync and refusal to overwrite a changed file. The public fixture files and disposable account were removed. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `cfdc6965e940458c4b502be988c4d0a016cca954cec8a0795966a96e61828b65`; rollback snapshots `/var/backups/webhost-sites/change-20261031T164825235969Z` and `/var/backups/webhost-sites/change-20261031T164825236426Z`. Physical-device testing remains open.

Browser download folder integration (source only): clicked and explicit URL downloads use a common account-bound destination chooser, select a My files folder, confirm replacement and pass the checked version to the write. Cancels retain clicked downloads. Helper unit tests and local actual-engine clicked download folder/cancel/replace/server-sync tests passed at desktop and phone-sized views; the URL-path test used a stubbed response with real account sync. The full clicked-download regression later timed out waiting for its interrupted-download error; do not claim that check passed. The repo's ignored engine directory contains ABI v1 while current adapter requires v3; tests used a temporary hash-checked copy of live v3 assets. Do not deploy the stale source engine or this update without resolving the remaining test and reviewing the release.

Browser folder follow-up: the complete clicked-download regression passed with an explicit 1366 × 950 desktop viewport, including interrupted and oversized files; the earlier default 800 × 600 viewport put the fourth test link below the visible guest canvas. The focused real-engine test also verifies a concurrent file edit prevents replacement. The URL-path stub test verifies a declined replacement does not start another download and a confirmed replacement writes a new version. Before live deployment, update the authenticated corresponding-source archive and remaining download integration tests for the new folder chooser; do not ship the stale ABI v1 engine.

## Browser download folder live update — 2026-10-31

Live static release `d06b9ff22f707b2f68207689a8f54a2ebe576fc31db22845827ae7334032826c`, Browser bundle `14a746ed01eb0a55febc1d0e4c4cfbbea5d6356ae5c753d91c3e704763b77eea`, replaces `9f0d74f91bb54c58f5f1bc94d12d81ae8712588e1744a23658077b9696a64a2b`. Clicked and URL downloads now choose a My files folder and require confirmation plus a version check to replace a file. Local actual-engine desktop/phone tests covered clicked saves, cancel, replacement and concurrent edit; the full interrupted/oversized regression passed at a correct desktop viewport. Local URL test used a stubbed response. Live phone-sized tests passed actual URL download and fresh-context recovery, and clicked HTML download into a subfolder with server sync. The three exact public fixture accounts and files were removed. Signed-in source archive `codi-browser-source-15c9672ce-folder.tar.zst`, SHA-256 `00832167e24d5fffbccb4277a60e181eb5ade40c0b52a385076191ec2dfb9b04`, was checked through the authenticated source page; source index backup is `/var/lib/codi-ingress/browser-source-index-folder-15c-backup.json`. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `1297a03ad4eaac8762fd46fa523156db01150e3afbc7cbd7e183db4cce88eb12`, rollback snapshots `/var/backups/webhost-sites/change-20261031T170418692421Z` and `/var/backups/webhost-sites/change-20261031T170418692889Z`. No engine policy changed; physical touch and Browser security limitations remain as documented.

## Spreadsheet XLSX snapshot update — 2026-10-31

Live static release `a114949a67422368a94964bdb72cdcb649c0c0412e70faf8389034958d45be5f`, Spreadsheet bundle `8fd7cc78408705f40eddbaa8a40c0f73166846578a3b44fc32967c2c6f85ecf1`, replaces `d06b9ff22f707b2f68207689a8f54a2ebe576fc31db22845827ae7334032826c`. XLSX export captures its destination and values before asynchronous conversion, reports newer edits, uses metadata and a versioned overwrite, and rechecks account validity. Local desktop/phone/4K and live phone-sized tests cover changing the path and cells during conversion, canceled replacement, stale-write refusal and sync; local desktop/phone tests cover switching accounts while conversion is held. Live test fixture and account were removed. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `d95931624b48ac3084a2f0f19590d854165ff31b6f852658438fcc23971acf68`; rollback snapshots `/var/backups/webhost-sites/change-20261031T170802537510Z` and `/var/backups/webhost-sites/change-20261031T170802537998Z`. Physical touch remains unverified.

## Spreadsheet native save update — 2026-10-31

Live static release `fe64c3b3a01faa057a027548fd80ad4f653132c10f367b71f1448b9c28bf486f`, Spreadsheet bundle `aeaa6de101ff118f3fc3c4fc512e90a5b35893047a9e7233be3c5eb6a4d1420c`, replaces `a114949a67422368a94964bdb72cdcb649c0c0412e70faf8389034958d45be5f`. Native save snapshots its filename and workbook before async checks, confirms replacing a different workbook, preserves newer edits and refuses stale versions; saved-file notices use metadata. Local desktop/phone/4K and live phone-sized account tests cover delayed save, cancel, competing write, confirmed replacement and sync; local desktop/phone account-switch tests passed. The live account and fixtures were removed. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `71f7f2486a255f6ea4ed969f6f2183cbfbe4e657e5e3c0dc1a10c7bd03a159e7`; rollback snapshots `/var/backups/webhost-sites/change-20261031T171039856045Z` and `/var/backups/webhost-sites/change-20261031T171039856513Z`. Physical touch remains unverified.

## Replicad snapshot update — 2026-10-31

Live static release `d9e8d3aeb81f3cdb2b3ea4c3477a192328d771d4cefbfee0e48d7ddf341260a4`, Replicad bundle `b46ea4a3f5546b3c906d36b4844a76ca5a700b12a39f6cca1dc3994fff63a9c7`, replaces `fe64c3b3a01faa057a027548fd80ad4f653132c10f367b71f1448b9c28bf486f`. Project saves and STL/STEP builds capture destination and dimensions before asynchronous checks, retain later filename edits, report newer dimensions and use metadata for version checks. Local desktop/phone/4K and live phone-sized account tests held a metadata check while changing fields, verified saved project values, measured generated STL dimensions and checked server sync. The live account and fixtures were removed. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `1c4792ab068b3de14d85f6b1f93923cf18ae18b3107f88a95dd697135b16fc4d`; rollback snapshots `/var/backups/webhost-sites/change-20261031T171305530780Z` and `/var/backups/webhost-sites/change-20261031T171305601028Z`. Physical touch and manufacturing correctness remain unverified.

## Files folder copy — source only — 2026-10-31

My files can copy a folder, including nested files and empty folders, using Copy to…. IndexedDB commits the local snapshot together; the existing mirror synchronizes entries individually, so the server may temporarily have only part of the copy. Existing local names are protected; if another device independently creates the same server folder, contents can combine and conflicting files are retained for resolution. Moving folders remains unsupported. Local desktop, emulated-phone and 4K account workflows passed, including server sync and a fresh browser context. Storage tests cover offline copying, conflicts, invalid destinations and account isolation. A concurrent three-browser run timed out during one phone login; the phone workflow passed when run separately. This change is not deployed or tested on the live site; deploying it requires both the Files bundle and storage mirror module together. Physical phone touch remains unverified.

## Files folder copy live — 2026-10-31

Live static release `a56862281337c401a612a386748521eeb3aa3b2145cf29ed4eec27c3a052bda0`, Files bundle `36f7c079c7902e8eba002c35b737bfb46fedf1a28e3cd0a7e645f8ec5193c336`, replaces `d9e8d3aeb81f3cdb2b3ea4c3477a192328d771d4cefbfee0e48d7ddf341260a4`. Files and the storage mirror module were activated together. A live emulated-phone registered-account test covered cancellation, file conflicts, nested and empty folder copying, server sync, fresh-session recovery, and window close; exact fixture files were removed and the witnessed disposable account disabled. The earlier local desktop/phone/4K and storage tests are described above. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `b498bb429ba349a5eb24f2708fde182b351e3ea00355b6038ac570ccaec6f6c9`; rollback snapshots `/var/backups/webhost-sites/change-20261031T171759225968Z` and `/var/backups/webhost-sites/change-20261031T171759226430Z`. Root, /desktop/ and /blog/ returned HTTP 200. Folder sync and simultaneous destination limitations remain as described above; physical touch remains unverified.

## Calculator result status live — 2026-10-31

Live static release `b89faee1a69374bb846c2e9165ec652e668a18451929be98f3f96b57106a3e04`, calculator bundle `9c2805d9cde871dc74e45f2787c12728e493609d3bd32bb05ebde11fe787662a`, replaces `a56862281337c401a612a386748521eeb3aa3b2145cf29ed4eec27c3a052bda0`. The previous display is identified when the expression or angle mode changes; Calculate identifies the current result and errors leave Ans unchanged. Local desktop, emulated-phone and 4K tests and a live emulated-phone signed-in workflow covered keyboard and keypad edits, angle changes, recalculation, errors and independent windows. The witnessed test account was disabled and had no user files. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `f39894e79d1d91d16a101b029c0a417ea3630ed32363e6b20151443691703d83`; rollback snapshots `/var/backups/webhost-sites/change-20261031T172046645287Z` and `/var/backups/webhost-sites/change-20261031T172046645737Z`. Physical touch remains unverified.

## Falling Blocks save snapshot live — 2026-10-31

Live static release `223e8cbb03fc6b3e3515155087ca2536f3d45a21eb0a9b4a9cf67ccce94791af`, Falling Blocks bundle `21ffaa41aaa27c869c9a8d072e06b2f82d60a7faddcea5dce9f78e7123f4f505`, replaces `b89faee1a69374bb846c2e9165ec652e668a18451929be98f3f96b57106a3e04`. Save captures the game, path and prior version before waiting; starting another game does not attach the old save to it, and later play remains unsaved. The destination appears in the save notice. Local desktop, emulated-phone and 4K delayed-save account tests passed; a live emulated-phone test passed against the final bundle. The exact fixture files were removed and the witnessed disposable account disabled. Local model tests passed. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `efd553db0785998e7fdd4c55ec5eac458a743e35cd31f404ee6b1f9d8276d853`; rollback snapshots `/var/backups/webhost-sites/change-20261031T172333318456Z` and `/var/backups/webhost-sites/change-20261031T172333318936Z`. The game remains a preview; physical touch and hardware-specific performance are not verified.

## Digital Logic save snapshot live — 2026-10-31

Live static release `c44db35f7155e295e2b04b490d668be0d19037d6c1f82659d0dc514518094dad`, Digital Logic bundle `777fbc924582f833cadeb4c57c0afcad3c1f30265d46737c282b40c879bfcbd0`, replaces `223e8cbb03fc6b3e3515155087ca2536f3d45a21eb0a9b4a9cf67ccce94791af`. Circuit saves capture the destination together with the JSON draft before waiting for storage, report the actual destination and retain newer edits as unsaved. Local desktop, emulated-phone and 4K tests and a live emulated-phone account test delayed storage, changed the path and draft, verified both snapshots and server sync. The exact live fixture files were removed and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `225fe731d9979bfa35c4ef2cca0cece11daecba94f1040b1eae5c80ca568cbde`; rollback snapshots `/var/backups/webhost-sites/change-20261031T172558848282Z` and `/var/backups/webhost-sites/change-20261031T172558848746Z`. Physical touch and broader simulation validation remain open.

## Stitch Converter SVG open recovery live — 2026-10-31

Live static release `f4dc548d36256e7ce82e339ddaa5ac9cf334185dfeaf9ce0132c4f95ce088c1c`, Stitch Converter bundle `d0cf022472748c1b83b6eba99903e1226b071e6daf6717318834e1b4e5c6646a`, replaces `c44db35f7155e295e2b04b490d668be0d19037d6c1f82659d0dc514518094dad`. Malformed `.stitch.svg` and regular SVG are validated before replacing current artwork and preview. Valid SVG that cannot generate a preview remains editable with an explanation; machine export requires a generated preview. Local desktop, emulated-phone and 4K and live emulated-phone account workflows covered malformed files, empty valid SVG, artwork save, machine export, upload, sync and fresh-session reopen. The exact fixture files were removed and the witnessed account disabled. One initial local upload timed out because Chromium's Snap-private `/tmp` could not see the test fixture; moving that disposable fixture under the user home fixed the test. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `36fa49623caa9ebc97aed134916094201d0afd259b621d0d46a8a43b837011cf`; rollback snapshots `/var/backups/webhost-sites/change-20261031T172928700186Z` and `/var/backups/webhost-sites/change-20261031T172928700645Z`. No physical embroidery or touch validation is claimed.

## Stitch Converter save snapshot live — 2026-10-31

Live static release `7537e025cf7ffbc4a4289428c0d74e000623f19e5c31df5996a89f062006fb74`, Stitch Converter bundle `b4f5582b9306c416a3d6d23b23ce79094d9e72e9a5f6e2171ce76495ab539689`, replaces `f4dc548d36256e7ce82e339ddaa5ac9cf334185dfeaf9ce0132c4f95ce088c1c`. Artwork and machine saves capture path, format and version with the current content before waiting; starting another example does not attach the earlier save or clear its unsaved state. Local desktop, emulated-phone and 4K and live emulated-phone account tests delayed storage, changed artwork, file paths and PES/DST selection, checked the resulting PES header and server files, and confirmed the new example's close warning. Local phone-sized full open/upload/export regression passed. The exact live fixture files were removed and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `1693f354a25a639187ad9393179000de2febad0b195f56b55be47c9746e94fb2`; rollback snapshots `/var/backups/webhost-sites/change-20261031T173207200967Z` and `/var/backups/webhost-sites/change-20261031T173207201442Z`. Physical sewing and touch remain unverified.

## Pico serial output save live — 2026-10-31

Live static release `9d79e6e5f5c3e169455550cdf8d7b497098aa21cc218fada02bbccde20fc3137`, Pico bundle `eb4e07d1f748d582989397ad5fae58fe5a060792a0bf96418bc3cd7a055105dc`, replaces `7537e025cf7ffbc4a4289428c0d74e000623f19e5c31df5996a89f062006fb74`. Visible decoded serial output can be saved as text in My files. The monitor warns when its 65,536 UTF-16-code-unit tail has trimmed earlier output and avoids beginning with half a surrogate pair; it is not a raw or complete log. Local desktop, emulated-phone and 4K and live emulated-phone account tests injected worker messages and covered snapshot timing, folder selection, overwrite cancellation, trimming, sync, Text reopen and window disposal. A separate live phone-sized test exercised the real Blink worker and preserved unsent serial input. The exact live fixture files were removed and both witnessed test accounts disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `9848e71345ff7960f4b5f6adeae0c5f409d522b06dd6f46a4f24e7f6b58536e7`; rollback snapshots `/var/backups/webhost-sites/change-20261031T174030302574Z` and `/var/backups/webhost-sites/change-20261031T174030303063Z`. No physical hardware or phone validation is claimed.

## G-code signed-radius arcs live — 2026-10-31

Live static release `35fb57b52da5356e98c059bd909a2de639e9c8b48aa14a56c605abe8a85f173c`, G-code Preview bundle `e0de6328bd1034553003722781e8de23eba46862040eeefbeae08f526a62c42b`, replaces `9d79e6e5f5c3e169455550cdf8d7b497098aa21cc218fada02bbccde20fc3137`. The bundled renderer mishandled negative-radius long arcs; the worker now converts positive/negative R arcs to center offsets. Zero or too-small radii, mixed R/I/J, missing or zero centers, multi-turn parameters, and same-XY full-circle/helical arcs are rejected, preserving the prior preview. Local desktop, emulated-phone and 4K tests and a live emulated-phone account test checked both directions and radius signs, rejected cases, and identical rendered pixels for one long-radius arc and equivalent I/J form. Existing worker extrusion/units/position tests passed locally. The exact live fixture files were removed and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `f541d457cbe0e683aadce57573d3f6b6f80ad6aa8c33d7bca339d264a34f17c1`; rollback snapshots `/var/backups/webhost-sites/change-20261031T174423394321Z` and `/var/backups/webhost-sites/change-20261031T174423394783Z`. This is a preview, not controller or hardware validation.

## G-code arc geometry limit live — 2026-10-31

Live static release `666a489ad971de2fdb01e089ee422723f160877c527f4ea4eb030b276168ebb9`, G-code Preview bundle `0893b69c3eb539c6b9e9e9b2ef6b76289dd46df116e1c61977f6378381dab9be`, replaces `35fb57b52da5356e98c059bd909a2de639e9c8b48aa14a56c605abe8a85f173c`. The parsing worker estimates the renderer's actual arc subdivision and rejects nonfinite arc geometry and files estimated above 200,000 arc segments before the UI renderer allocates them. Local desktop, emulated-phone and 4K and live emulated-phone tests cover overflowing coordinates, cumulative segment excess, signed-radius parity and preservation of the prior preview. Existing worker unit and extrusion tests passed locally. The exact live fixture files were removed and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `95cd2e9362f15432890e61be280dc2cf2fb9b07308b1b9873095c6298662b392`; rollback snapshots `/var/backups/webhost-sites/change-20261031T174730150288Z` and `/var/backups/webhost-sites/change-20261031T174730150752Z`. This limits arc geometry only and does not guarantee large files fit a device or validate a toolpath for a machine.

## Text conflict status live — 2026-10-31

Live static release `ac9830a96254be75994cf03afa5c75f57ae7f8a7e5dec51d4f76f3b6e2d8f32d`, Text bundle `e6b466c36cbc972fc99acebe6de4a856e2fb9c698722c1cdc76ce6f09c60338a`, replaces `666a489ad971de2fdb01e089ee422723f160877c527f4ea4eb030b276168ebb9`. Text identifies conflict state when opening or saving a local copy and checks again after saving in case the conflict notification arrived while busy; it does not claim a conflicted copy is syncing. Local desktop, emulated-phone and 4K and live emulated-phone registered-account tests used separate browser contexts, created a real server conflict, saved the local draft, resolved it through Files, and verified fresh-session recovery. A second case introduced a conflict while the save was held and checked that the warning appeared after completion. Exact live test files were removed and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `a564c993ec1cb6f24edbe78b3ace2f470df33477cedfc200cd5ef9cd76e5b802`; rollback snapshots `/var/backups/webhost-sites/change-20261031T175131934927Z` and `/var/backups/webhost-sites/change-20261031T175131935460Z`. Physical touch remains unverified.

## Spreadsheet conflict status live — 2026-10-31

Live static release `3acc57e2c34fad76b6740f619c8a836f81f4750eac2ea2919d0f8d96401d42f4`, Spreadsheet bundle `4da5d04fe4172a7540d6d027c8522737f5094ff4d443a22e11c69734dc800950`, replaces `ac9830a96254be75994cf03afa5c75f57ae7f8a7e5dec51d4f76f3b6e2d8f32d`. Workbook saves report a conflict that appears between the version check and the write, recheck after save for notifications received while busy, and keep an attention message when editing. Local desktop, emulated-phone and 4K and live emulated-phone registered-account tests created conflicts before and during the write, checked preserved drafts and server contents, resolved one via Files and verified fresh-session recovery. Existing native save snapshot/replacement regression passed locally. Exact live fixture files were removed and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `799731f5d124ff09f4f7a55f83eafb91df2503fa5b7dd491644b08902e434927`; rollback snapshots `/var/backups/webhost-sites/change-20261031T175545841816Z` and `/var/backups/webhost-sites/change-20261031T175545842300Z`. Physical touch remains unverified.

## Document Editor conflict status live — 2026-10-31

Live static release `3798c7e6da8fdfa054c389e856f4c4b839467256b4d1722e4bc6ce7e8e736d8e`, Document Editor bundle `ef87aee7f924827992e761be948115965de15aba635d7e558669a04ac4631aa1`, replaces `3acc57e2c34fad76b6740f619c8a836f81f4750eac2ea2919d0f8d96401d42f4`. Report saves report conflicts that appear between the version check and write, recheck after saving for notifications received while busy, and keep an attention message while editing. Local desktop, emulated-phone and 4K and live emulated-phone registered-account tests created conflicts before and during the write, verified preserved drafts and server contents, resolved one via Files and checked fresh-session recovery. Existing desktop/phone open, save, PDF export and recovery regression passed locally. Exact live fixture files were removed and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `ce6a0a6ba526d6d1f07295cf235690993cb9a3b0f07e6402bfcd7fdf50010e72`; rollback snapshots `/var/backups/webhost-sites/change-20261031T175859405780Z` and `/var/backups/webhost-sites/change-20261031T175859406303Z`. Physical touch remains unverified.

## Data Explorer source notice live — 2026-10-31

Live static release `60a4a965439a6fcffffd7c198de1144319d33950ccc551bc2bfe52e21466d85c`, Data Explorer bundle `ab32d4dc968a0a425f0f45208cac64e9ef0b989280229895994a105f8edaad4b`, replaces `3798c7e6da8fdfa054c389e856f4c4b839467256b4d1722e4bc6ce7e8e736d8e`. A persistent notice shows when the account mirror detects that the open CSV is changed, conflicted or unavailable; analysis remains on its prior in-memory snapshot until reopened. Local desktop/phone/4K and live emulated-phone account workflows checked change, conflict, deletion, reopen and project sync; local phone-sized checks also verified the file-change subscription is released on close. Exact live fixture files were removed and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `7a441481acd41aabe5887f6ba5f3f0cd0448e7208f817160a838bbb0b6efa705`; rollback snapshots `/var/backups/webhost-sites/change-20261031T180226679443Z` and `/var/backups/webhost-sites/change-20261031T180226679895Z`. Detection depends on account-mirror synchronization; physical touch remains unverified.


## Data Explorer save destination live — 2026-10-31

Live static release `2b8e1f6d6fcf15e176557bceb3389baaf6a2f352cc808a59008f4d0d14de9586`, Data Explorer bundle `ca80f476432d3b0f6471f012136f3b75308f5d3839a8b5664099800ee558f375`, replaces `60a4a965439a6fcffffd7c198de1144319d33950ccc551bc2bfe52e21466d85c`. Project and CSV exports capture their destination before asynchronous preparation. Local desktop, emulated-phone and 4K and live emulated-phone account tests changed each path immediately after starting the save, verified the original files, synchronization and a fresh-session read. The live fixture files were deleted and the witnessed account disabled. An initial local test attempted to intercept a Perspective custom-element method, which could not be replaced as expected; the passing test uses a deterministic path change immediately after clicking Save instead. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `d1a0490cf97ecdf570e0d5da0f1a5a4c9d7d0f8f7ffbdf42e8ac1ccf7d796bcc`; rollback snapshots `/var/backups/webhost-sites/change-20261031T180730978327Z` and `/var/backups/webhost-sites/change-20261031T180730978791Z`. Physical touch remains unverified.


## Circuit Simulator file safety live — 2026-10-31

Live static release `2023bf205849921daf057bcf1e870b1c3289729a8f52a61739434792b8ac8ee5`, CircuitJS bundle `3c97ab388413c3f7b0ce5d363b22ce1840358b81670f5bf0ba4c77f639961bbc`, replaces `2b8e1f6d6fcf15e176557bceb3389baaf6a2f352cc808a59008f4d0d14de9586`. Save captures its destination alongside the circuit, preserving newer edits. A separate persistent notice reports mirror-detected saved-file changes, conflicts and unavailable files; watch and overwrite checks use metadata. Local desktop, emulated-phone and 4K and live emulated-phone account tests held a save, changed the destination and circuit, created a two-browser conflict, saved a copy, synchronized and reopened it, and checked its simulated 3.33 V output. The existing example regression also passed locally. Live fixture files were deleted and the witnessed account disabled. Initial tests exposed a missing local catalog entry, an incorrect expected output for the resistor changed by the fixture, and duplicate parallel fixture usernames; the test setup was corrected before passing. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `2df43708500ab0cdcb577574fe9a257d92ded255f6078f5b7962febc6461cfbc`; rollback snapshots `/var/backups/webhost-sites/change-20261031T181233510771Z` and `/var/backups/webhost-sites/change-20261031T181233511199Z`. Notifications depend on mirror synchronization; physical touch and hardware validation remain unverified.


## Arduino digital input example live — 2026-10-31

Live static release `67f758298d4fcfdd831b85859d34d460b2c048dbaf923637b12a83f797e14390`, Arduino bundle `868b45fe945d99572008469e264e089170f5cdc0408e346e14a2237e683063c2`, replaces `2023bf205849921daf057bcf1e870b1c3289729a8f52a61739434792b8ac8ee5`. Each window has a driven logical D2 high/low input. The included AVR C example and compiled HEX mirror that input to D13; source can be saved to My files for inspection, and firmware can be saved/reopened. Local desktop, emulated-phone and 4K and live emulated-phone account checks exercised both input levels, independent windows, stop/restart, source/HEX sync and fresh-session reopen; a local desktop and live phone-sized test also exercised serial echo. Exact live fixture files were deleted and the witnessed account disabled. One parallel phone registration hit the local password-service busy limit; a sequential retry passed. An older broad regression stopped waiting for its Applications menu in the older local test catalog; the focused serial check passed. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `452dcf3daf4a9f4ce3e0dddf379933df45caa65a88ce7889ef1100aeefa15d54`; rollback snapshots `/var/backups/webhost-sites/change-20261031T181626210101Z` and `/var/backups/webhost-sites/change-20261031T181626210516Z`. Electrical behavior, physical touch and hardware are not validated; compiling source in the browser remains unavailable.


## Digital Logic two-bit adder live — 2026-10-31

Live static release `2d746aa4835d71a058e64ffafb0a956cc7ee9e8ce1f7769a6260b8cd3a701dfe`, Digital Logic bundle `61f0de10a5e894bd9017b6a5aec5dde9a1fa9515f1b1004a6b22df6b83b35bce`, replaces `67f758298d4fcfdd831b85859d34d460b2c048dbaf923637b12a83f797e14390`. The new 2-bit ripple-carry example joins low- and high-bit logic and labels the result Carry out / Sum1 / Sum0. Local desktop, emulated-phone and 4K account tests and a live emulated-phone test checked all 16 truth-table and interactive input combinations against arithmetic, saved circuit and CSV, sync, and fresh-session reopen. The live fixture files were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `7a5e8f3d4c1648e9a3e2f2879ca634f1dd2aeb4b68ef32725ad406fe68910e03`; rollback snapshots `/var/backups/webhost-sites/change-20261031T181847800027Z` and `/var/backups/webhost-sites/change-20261031T181847800455Z`. Logic timing, physical hardware and physical touch remain unverified.


## Image Editor conflict status live — 2026-10-31

Live static release `6dbee27fe83ce1098ba4416d6dfef04a3c6729a28467181587d019b6e441194a`, Image Editor bundle `65f8b73579d985ecfd6b7a8ba6f573cc88494dfe115c7e2afe1bd2d9894d4b59`, replaces `2d746aa4835d71a058e64ffafb0a956cc7ee9e8ce1f7769a6260b8cd3a701dfe`. An independent notice stays visible as edits continue when the image is changed, conflicted or unavailable. Saves identify an immediate conflict and recheck after completion for a conflict that arrived while busy. Local desktop, emulated-phone and 4K and live emulated-phone account tests preserved conflicting image edits and server versions before and during saves and checked fresh-session recovery. Metadata-only stale-save regression passed locally. Live fixture files were deleted and the witnessed account disabled. One initial test raced the login mirror's first synchronization; awaiting that sync made its offline fixture deterministic. A 4K retry waited for the editor's unsaved-change event before saving. Local preview staging initially exhausted disk space; 15 GB of temporary public preview copies from these tests was removed without removing account data. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `fa6b16c96803c2c846ae4b71d9e6f08dc074b763da530b8c42fe1ae6deba875b`; rollback snapshots `/var/backups/webhost-sites/change-20261031T182334395651Z` and `/var/backups/webhost-sites/change-20261031T182334396083Z`. Detection depends on mirror sync; physical touch remains unverified.


## Audio Editor file notices live — 2026-10-31

Live static release `b225716e3029703a9ac66bf3865e1f87aec5a2491bc7a8b3077a63e1d5af5924`, Audio Editor bundle `3f6c90d2080b0856b68a869752054ce5adcb6ccb78f6756f6e5832215f9cc891`, replaces `6dbee27fe83ce1098ba4416d6dfef04a3c6729a28467181587d019b6e441194a`. A persistent separate notice identifies mirror-detected changes, conflicts and unavailability for the opened source or most recently saved WAV; the loaded audio stays open. Export reports immediate conflicts and rechecks via the new watch after writing. Local desktop, emulated-phone and 4K and live emulated-phone account tests covered an independently changed source, a two-browser conflict during WAV export, preserved reversed samples, and fresh-session recovery. A local phone-sized test checked file-listener disposal. Exact live fixtures were deleted and the witnessed account disabled. The first sample assertion was corrected to allow one integer step of PCM quantization. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `5b9bcd398fda88386d1fc930970247e3e9cba27e3f6917d8ea32a3bcd5acfe50`; rollback snapshots `/var/backups/webhost-sites/change-20261031T182610688496Z` and `/var/backups/webhost-sites/change-20261031T182610688904Z`. Detection depends on mirror sync; physical touch and microphone remain unverified.


## Python Notebook conflict notices live — 2026-10-31

Live static release `95085853e89352bfa733b470db625e84c7b37ca33f43f8d37079dd441b0ff64f`, Notebook bundle `ad9b1277cf655af525e25860558874b325c7402cda62d88b81292359ad230f62`, replaces `b225716e3029703a9ac66bf3865e1f87aec5a2491bc7a8b3077a63e1d5af5924`. A separate notice tracks mirror-detected changes, conflicts and unavailable linked notebooks, while keeping the working notebook open. Automatic saves report conflicting local copies instead of claiming sync and recheck after writes. Local desktop, emulated-phone and 4K and live emulated-phone account tests covered two-browser conflicts before and during writes, continued local automatic saving, preserved server content, fresh-session recovery and file-listener cleanup. Exact live fixtures were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `6a0dc1668281dd5365ca927f5ad257e3c5e7e808b58c63edb8bf40ece79cec0c`; rollback snapshots `/var/backups/webhost-sites/change-20261031T182917925751Z` and `/var/backups/webhost-sites/change-20261031T182917926200Z`. Detection depends on mirror sync; physical touch and untrusted-notebook isolation remain unverified.


## Electronics Design project notices live — 2026-10-31

Live static release `0329e1a6b052c0bc8e26fef92d477bbe884e6b636b0a9baa1e43e24355791dec`, Electronics Design bundle `5188b0b00177cac49aab5c82c0e53ff5865dcca75813c7972ca43b0c33ed5452`, replaces `95085853e89352bfa733b470db625e84c7b37ca33f43f8d37079dd441b0ff64f`. A persistent separate notice identifies mirror-detected project changes, conflicts and unavailable files while leaving the design open. Project and export overwrite checks use metadata; immediate conflicted writes report the local conflict. Local desktop, emulated-phone and 4K and live emulated-phone account tests covered a changed project, conflict during save, retained design, listener cleanup and fresh-session recovery. The existing local WebAssembly editor/part import/export regression also passed after bringing its mock file API up to date. Exact live fixtures were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `d27eb70a2f0c03de5b1f3b45b23a522df4e7667f1f753f7fcbf335f447a4c0d1`; rollback snapshots `/var/backups/webhost-sites/change-20261031T183224103613Z` and `/var/backups/webhost-sites/change-20261031T183224104088Z`. Detection depends on mirror sync; fabrication validation and physical touch remain unverified.


## Replicad hole offsets live — 2026-10-31

Live static release `633055054501db4bb9293250f14b6a6cf344fb07f487aeee4ad617d640535e64`, Replicad bundle `9fb07b320ce2956a0b0960f61da5f8052fe8df602f181f15774653e121ebf490`, replaces `0329e1a6b052c0bc8e26fef92d477bbe884e6b636b0a9baa1e43e24355791dec`. Optional X/Y offsets place the vertical through-hole relative to the center of a box or cylinder, with geometry validation to keep it inside the solid. Old projects default to zero offsets. Local desktop, emulated-phone and 4K and live emulated-phone account tests inspected exported STL hole vertices for both shapes, rejected a tangent hole, checked preview volume, sync and fresh-session project reopen. Exact live fixtures were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `7e412e7bcf5eea1a22da5cbad5166402cf84608c6d2938e39cf9a894f191000f`; rollback snapshots `/var/backups/webhost-sites/change-20261031T183444882279Z` and `/var/backups/webhost-sites/change-20261031T183444882686Z`. STL approximates geometry; fabrication and physical touch remain unverified.


## Files atomic local ZIP extraction live — 2026-10-31

Live static release `e13a8be7e55f6729d0cf93ff19c76c8a443cde4e7eca52c9827e34ed59cfdcb1`, Files bundle `62bd77d9df326d9df1152c914f7f49510f1dd2d52485da9f965c17a8605b3a1a`, mirror SHA `fdd45beb3a63801dbf9046fae4ca696d8c9dd1866545140071db69d3bc4639e9`, replaces `633055054501db4bb9293250f14b6a6cf344fb07f487aeee4ad617d640535e64`. ZIP extraction into My files creates a validated complete local tree in one IndexedDB transaction and checks the source archive version inside that transaction. Local desktop, emulated-phone and 4K and live emulated-phone account tests cover nested/empty folders, destination collisions, source changes, sync and fresh-session recovery; mirror tests cover atomic concurrent imports, invalid paths and offline sync. The first UI test repeated clicks rapidly enough to open the ZIP; the passing test reuses the selected item. Exact live fixtures were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `4b49cfbf20044a0a2297f7c36e2c6b9abc31c376cc3b7ca3cdddb7f148bd37c5`; rollback snapshots `/var/backups/webhost-sites/change-20261031T183843536842Z` and `/var/backups/webhost-sites/change-20261031T183843537264Z`. Server synchronization is per entry and can remain partial until retry; concurrent remote folder creation can combine contents. Temporary Linux extraction is still item by item.


## Embroidery Studio file safety live — 2026-10-31

Live static release `f88f33fd0892d2e12154a1a02b7f869a7f1a4f19523bc00faf1f5f53d98f05f6`, Embroidery Studio bundle `6f10349193c3d924a82e42bdf7df764db637f6c5bf4e80902893c72a7d0c875a`, replaces `e13a8be7e55f6729d0cf93ff19c76c8a443cde4e7eca52c9827e34ed59cfdcb1`. A separate notice reports mirror-detected project changes and conflicts, overwrite checks use metadata, and project/captured/export destinations are captured at action start. Local desktop, emulated-phone and 4K and live emulated-phone account tests cover changed and conflicted projects, delayed save and format changes, DST export, listener cleanup and fresh-session recovery. The existing local native captured project and stitch export regression passed. The first local test caught an undefined project-save variable introduced during the change; it was corrected and retested before deployment. Exact live fixtures were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `4217fe1111619c571c4781fa3fb96900583539198d2fcc57d7f7fecee15a8a2b`; rollback snapshots `/var/backups/webhost-sites/change-20261031T184156372043Z` and `/var/backups/webhost-sites/change-20261031T184156372459Z`. The upstream editor remains pre-release; detection depends on mirror sync, and physical sewing/touch are unverified.


## Pico project safety live — 2026-10-31

Live static release `6bb1733dd0d9cc0c387c859cce38dcef48b9e6c20d9705a7a93951190e426c01`, Pico Simulator bundle `ca2f64f56d32da696b386a7a7a4ee102e4f11e9e0154325ee599d8c130a67829`, replaces `f88f33fd0892d2e12154a1a02b7f869a7f1a4f19523bc00faf1f5f53d98f05f6`. Project destination is captured before requesting a flash snapshot; a persistent notice identifies mirror-detected project changes and conflicts while leaving the board open. Local desktop, emulated-phone and 4K and live emulated-phone account tests used synthetic project bytes and a fake worker for delayed snapshots, conflict during save, fresh-session recovery and cleanup. A separate actual Blink worker test passed locally and live, including retained unsent serial input. Exact live fixtures were deleted and both witnessed accounts disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `c882dd771b29425a0252419415d9ea68eda978b1c724da66873c924e7e24c5d8`; rollback snapshots `/var/backups/webhost-sites/change-20261031T184528712025Z` and `/var/backups/webhost-sites/change-20261031T184528712436Z`. Detection depends on mirror sync; physical touch and arbitrary firmware compatibility remain unverified.


## diagrams.net save safety live — 2026-10-31

Live static release `991c9da3672eb7e954d0b2333d7f7b1b49dd6be237f174b4ed2822b8bf64358a`, diagrams.net bundle `b52328e3a5a90f9f767ec15a7ad078e4fb432e9cd6220256d42a2069049a275d`, replaces `6bb1733dd0d9cc0c387c859cce38dcef48b9e6c20d9705a7a93951190e426c01`. Save requests capture destination and edit revision before asynchronous XML export; response IDs reject late unrelated exports, and a timeout releases the operation. A separate notice identifies mirror-detected saved-file changes and conflicts; version checks use metadata. Local desktop, emulated-phone and 4K and live emulated-phone account tests covered delayed real-editor export, a newer edit, conflict during save, fresh-session reopen and file-listener cleanup. Fresh background-tab test polling was switched from animation frames to timed polling after a timeout despite a rendered diagram. Exact live fixtures were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `e7b7e0994d493e60072b418d89fdb51f9f426a0693e1d79f473974b1ad68856b`; rollback snapshots `/var/backups/webhost-sites/change-20261031T185105832063Z` and `/var/backups/webhost-sites/change-20261031T185105832490Z`. Detection depends on mirror sync; broad format coverage and physical touch remain unverified.


## Excalidraw save safety live — 2026-10-31

Live static release `b7782151f7c64064a57941dfb85005b69a90223c0cb2c0e8f0ab1e95b46131ec`, Excalidraw bundle `811e29c5ed1069574abdef482a5311c996f32dfb2d64921b7d4cb94cae0d375b`, replaces `991c9da3672eb7e954d0b2333d7f7b1b49dd6be237f174b4ed2822b8bf64358a`. Saves capture the destination and serialized drawing before storage waits, retain newer edits, and use metadata checks. A separate notice tracks mirror-detected file changes and conflicts. Embedded image change detection compares exact data strings instead of lengths; a unit check covers same-length replacements without claiming full image-workflow coverage. Local desktop, emulated-phone and 4K and live emulated-phone account tests drew two shapes, delayed save, created a conflict, synced and recovered in a fresh session, and checked listener cleanup. An initial 4K test clicked the editor's style panel rather than the canvas; moving the test gesture to the canvas center passed. Exact live fixtures were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `76f9abbb0c79fa25210e223cad124013c100357befe9a86fe809e86dface59c9`; rollback snapshots `/var/backups/webhost-sites/change-20261031T185501631513Z` and `/var/backups/webhost-sites/change-20261031T185501631950Z`. Detection depends on mirror sync; physical touch and broader image workflows remain unverified.


## SVG Editor save safety live — 2026-10-31

Live static release `16e08ba030b345755aa3cbb4514777853c1c9b66908a403353696694213dc949`, SVG Editor bundle `1218072a23b758d173395c84c347002dec66515ba7b4253883272db93cb6b199`, replaces `b7782151f7c64064a57941dfb85005b69a90223c0cb2c0e8f0ab1e95b46131ec`. Saves capture the destination and SVG before waiting, preserve later edits and use metadata checks; a separate notice reports mirror-detected changes and conflicts. Local desktop, emulated-phone and 4K and live emulated-phone account tests created two rectangles, delayed a save, created a two-session conflict, synced and opened the recovered SVG in Stitch Converter. Listener cleanup was checked. The first test expected a transient save status that a later SVG-edit change event replaced; the corrected check verifies the saved snapshot and actual dirty state. Exact live fixtures were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `a45eaf7f198cb8d4fe53720eb03fd0cca412949605f6860942e7a355e349ea89`; rollback snapshots `/var/backups/webhost-sites/change-20261031T185848787369Z` and `/var/backups/webhost-sites/change-20261031T185848787774Z`. Detection depends on mirror sync; complex SVG, physical touch and stitch quality remain unverified.


## 2026-10-31 Stitch Converter file safety

Live static release `6b699564e53b59eb414799526e998c4caa8b0afc301d8804c90f188fa66375af`, app bundle `14d4a6773c13001b8f29e3c47ac4ef0ec5513858edb17c111b99c38c275a2b31`, replaces `16e08ba030b345755aa3cbb4514777853c1c9b66908a403353696694213dc949`. Saved-file change/conflict notices persist separately from ordinary status; overwrite checks use metadata. Artwork and machine exports report immediate write conflicts. Local desktop, emulated-phone and 4K and live emulated-phone real-account checks cover external changes, saving a copy, a conflict during a write, PES export and fresh-session reopening; the local full workflow and save-race regression also passed. An initial local full workflow ran without Files in its selected test bundle and timed out; rerunning with both apps passed. Exact live files were removed and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `3dfaf57c43c29064aff918bfa203654a56875412a8dcc55c86260ea213fbce0b`, Caddy SHA `6fc3b19a3331c0b0462fca085314963ebc9cc542783bd7a3e59cdd6150f70b0e`; rollback snapshots `/var/backups/webhost-sites/change-20261031T190214907711Z` and `/var/backups/webhost-sites/change-20261031T190214908139Z`. Notices depend on account mirror synchronization. Physical touch and sewing remain unverified. `docs/APP_USER_GUIDE.md` provides a concise app-by-app starting point and links to this ongoing review.


## 2026-10-31 Replicad project conflict notices

Live static release `17b21cadb41f957f6f6e04da63b7dfe77d355a39a573142f4a44e83604178db5`, app bundle `f2c2a6c1fccb7bb1108c7ddfb93eefd6020196614bd1f1cb42629be294114ae1`, replaces `6b699564e53b59eb414799526e998c4caa8b0afc301d8804c90f188fa66375af`. A separate project notice remains visible across other actions when synchronization detects a change, conflict or unavailable file. Project and model writes identify immediate conflicts. Local desktop, emulated-phone and 4K and live emulated-phone real-account tests cover remote change, saving a copy, conflict during save, resolution, real STL dimension checks, fresh-session reopening and subscription cleanup. The local offset-hole geometry regression also passed. Exact live fixtures were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `75a2732e8325ef1c2f46c387f25512907b51840e04779d6952520af8a9c76b37`, Caddy SHA `01686157603553bebab19c3b330c29b5c1d648056d6616debdf663936b8e8d0c`; rollback snapshots `/var/backups/webhost-sites/change-20261031T190446725713Z` and `/var/backups/webhost-sites/change-20261031T190446726131Z`. Detection depends on mirror sync; physical touch and manufacturing validation remain unverified.


## 2026-10-31 Digital Logic comparator

Live static release `be820659118f1b591ea90fd1a134f3b8b54b34cdbaa6f62ad1a56810660d2e0f`, Digital Logic bundle `46ab717783f377d24193234b22259a939348b9b2bd23197d815db5f1b78ccde1`, replaces `17b21cadb41f957f6f6e04da63b7dfe77d355a39a573142f4a44e83604178db5`. A two-bit unsigned comparator example exposes A > B, A = B and A < B using gates. Local desktop, emulated-phone and 4K and live emulated-phone registered-account tests exercise all 16 input combinations in both interactive simulation and calculated truth table, save the circuit and CSV, synchronize and reopen the project in a fresh session. Exact live fixtures were removed and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `6d6b368a815c2eac808bba0d4cb38376b7b311a783060920299ee539cd59b49a`, Caddy SHA `f1a0dd0920b33f95ff99f606f4237b4e6d40bb31c20969169b834967169f948e`; rollback snapshots `/var/backups/webhost-sites/change-20261031T190636388667Z` and `/var/backups/webhost-sites/change-20261031T190636389082Z`. This is idealized combinational logic, not timing or physical hardware validation; physical touch remains unverified.


## 2026-10-31 G-code arc center validation

Live static release `57489ab7d1ac9c3e694ce7e7b7e188ea61b74fed44e9c9563db220527744eb23`, G-code Preview bundle `ab91087f7969d97ce94ba336f0efb9b1901a8f361541d25116ef9f0f4ec703be`, replaces `be820659118f1b591ea90fd1a134f3b8b54b34cdbaa6f62ad1a56810660d2e0f`. I/J arc start and end radii must agree within the larger of 0.01 mm or 0.1% of start radius; rejected input preserves the previous preview. This is a deliberately stated viewer tolerance, not a machine or controller validation. Unit boundary tests and local desktop, emulated-phone and 4K and live emulated-phone real-account tests cover inconsistent and rounded centers, R/IJ rendered parity, unsupported geometry and previous-view recovery. Exact live files were removed and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `0c73d3bdcbb9c7bb4da05c24e250060e48be8eb11b494ebab2205f33c8d87856`, Caddy SHA `5016614469ffad6d24f4964c60934076397bcab45b6ef91cd4b15c8cc09d55d5`; rollback snapshots `/var/backups/webhost-sites/change-20261031T190808197193Z` and `/var/backups/webhost-sites/change-20261031T190808197640Z`. Physical touch and broad machine/controller behavior remain unverified.


## 2026-10-31 report image insertion safety

Live static release `45cad79483027e88ceaa22e4ad5208ddb614da67fb5693530604aefd1250afc8`, Document Editor bundle `6aea924548b6589d24a11ceed500e8368b64e9d80835cf0c049e59175af73b96`, replaces `57489ab7d1ac9c3e694ce7e7b7e188ea61b74fed44e9c9563db220527744eb23`. Insertion is cancelled if the report, its edits or insertion point change while an image loads. Conflicting image copies are rejected; PDF writes report an immediate conflict. Local desktop, emulated-phone and 4K and live emulated-phone real-account tests cover edits and opening another report during delayed image loading, retry, report save, PDF export, sync and fresh-session reopening. Image and PDF conflict responses were injected in the phone-sized local and live checks; these are not end-to-end concurrent conflict tests. Exact live fixtures were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `4118950d91df0d1647545b672c382ea4768f9e16e5efef6b396bb176b9fded71`, Caddy SHA `1ff6b9216065b26c1af68ae189439647194269070cc30c8040c8680293c81363`; rollback snapshots `/var/backups/webhost-sites/change-20261031T191002659049Z` and `/var/backups/webhost-sites/change-20261031T191002659457Z`. Physical touch and broad image/PDF compatibility remain unverified.


## 2026-10-31 Arduino firmware save safety

Live static release `4be9509920b9e06dfd0f91612faa5bd91742eef95d1606b0b03cde6b3bb4dd9d`, Arduino Simulator bundle `05dffcf2aa256e086bee6c90ff96ad1a2937e8eff9355abe7626ab6625706902`, replaces `45cad79483027e88ceaa22e4ad5208ddb614da67fb5693530604aefd1250afc8`. Firmware save captures the image, destination and previous version before storage waits, and identifies immediate conflicts. Local desktop, emulated-phone and 4K and live emulated-phone real-account checks cover changing destination, loading another firmware, same-example reload during a held save, sync and a fresh-session D2 simulation. The local existing D2/input isolation and serial echo regression passed. One initial test harness failed to delay the captured file-service function; a second 4K run waited on stale status text. Both harness issues were corrected before the passing tests. Exact live fixtures were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `ad585c52dc880f77a4387a0d2534ff8e1328da0f9e28be1fa0542b6dc009adae`, Caddy SHA `2a727b17fb39055c45247c4b41bc40b47fb62c3157ba8c1b74327d57e911c718`; rollback snapshots `/var/backups/webhost-sites/change-20261031T191306637653Z` and `/var/backups/webhost-sites/change-20261031T191306638090Z`. Sketch compilation remains research-only pending source/distribution work. This is not physical-hardware validation.


## 2026-10-31 Spreadsheet scientific formulas

Live static release `2918869647b80d52cbf060d5cf9592b5221d2fbd42d38d840cd662d92e4b8644`, Spreadsheet bundle `9362e9f81aa8ece83c8f93e9429a9071d98892f69ef1fb5c3b685e74428ecb09`, replaces `4be9509920b9e06dfd0f91612faa5bd91742eef95d1606b0b03cde6b3bb4dd9d`. Bounded parser and CSV calculation now support PI(), ABS, SQRT, SIN, COS and TAN; trigonometric arguments are radians, and a collapsed in-app help panel gives examples. Invalid domains and nonfinite intermediate results remain errors; results are floating point. Unit tests cover nesting, references, argument counts and errors; local desktop, emulated-phone and 4K and live emulated-phone real-account checks cover displayed results, blocked invalid CSV, correction, sync and fresh-session reopening. Parallel test accounts initially collided because timestamp-only usernames matched; a process-specific suffix fixed the harness and phone rerun passed. Exact live fixtures were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `d3040b6145b91edaafe7d5add73bab66d20d895b4ee9d91da202e17416718a91`, Caddy SHA `0ff7bf40104b1a38a3c1bcab4fd7352b1b86472aa49504ffd47c9f150d58f90b`; rollback snapshots `/var/backups/webhost-sites/change-20261031T191527199319Z` and `/var/backups/webhost-sites/change-20261031T191527199732Z`. This is a limited parser, not full spreadsheet compatibility; physical touch remains unverified.


## 2026-10-31 C/C++ and Arduino source in Text

Live static release `ee26dc4cab25b13f8b50fccbaad67348bbdaf002b258fe41eeb581c06bf0c7a2`, Text bundle `55ba2fb828db715148b3e217059dad8b59f01b9b296c3949fc508da2a07cff30` and CodeMirror bundle `900a96dd55cc0390ec35e13ec830070f6aedf804d884dd30662927a2159faa9b`, replaces `2918869647b80d52cbf060d5cf9592b5221d2fbd42d38d840cd662d92e4b8644`. Text's picker includes C/C++ source and headers and `.ino`; the shared CodeMirror tool uses pinned `@codemirror/lang-cpp` 6.0.3 for highlighting and reconfigures it after a successful save to a different path without replacing editor state. Local desktop, emulated-phone and 4K and live emulated-phone real-account checks save Arduino D2 example C, open via Text's chooser, edit, sync and reopen in a fresh session; a new `.ino` gains highlighting on first save. Existing local desktop and phone-sized first-save regression passed. Exact live fixtures were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `263247a9dd81ac977bc966bb6cfb22f3e1daa8625b913abb056717b6fd22381a`, Caddy SHA `36001ed6c0d596c1977ee4a6c8cda75771b9ed699f312059fea6ffb39cab8ab2`; rollback snapshots `/var/backups/webhost-sites/change-20261031T191754026645Z` and `/var/backups/webhost-sites/change-20261031T191754027048Z`. Highlighting is not compilation; the Arduino compiler remains research-only. Physical touch remains unverified.


## 2026-10-31 Data Explorer query/result consistency

Live static release `61f982a2c1bbd399efd31b10f4d46f0bcb83784368e2983f607b2c3aa0ae5004`, Data Explorer bundle `c3bcbea37ac32fc1729c74c86cdf5a70fdd99429335d05a3e22f979bd7ddca68`, replaces `ee26dc4cab25b13f8b50fccbaad67348bbdaf002b258fe41eeb581c06bf0c7a2`. A persistent notice identifies results from an older SQL query; CSV export requires the current query to have run, labels an earlier query if the text changes during export, and reports an immediate conflict. Local desktop, emulated-phone and 4K and live emulated-phone real-account tests cover the stale-query guard, actual aggregate CSV output, changed SQL during a held export, sync and fresh-session project reopening. An initial local test exposed that the rejection briefly left the app busy and ignored a rapid Run click; the guard was moved before starting export and retested. Exact live files were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `686e30cd2b69b615c24f4bbe865d05caa8eb5bcd7d5371e473554383a2ad2317`, Caddy SHA `d8e27cd23e59d315b2fa8644c0e7a1a4243ac91219b862fc193da4e2c2cbedc0`; rollback snapshots `/var/backups/webhost-sites/change-20261031T192037319814Z` and `/var/backups/webhost-sites/change-20261031T192037320287Z`. CSV remains the SQL result rather than viewer-only filters; large-file memory and physical touch remain unverified.


## 2026-10-31 Grid.Space export destination safety

Live static release `346461e0f54eea6d7ae183b91319c612d77610543c680f82dde152131b4bbe8d`, Grid tools bundle `858e7b707db88543e95f5db4c2132995d0d119fa137b054c7e8e85986e1e80cd`, replaces `61f982a2c1bbd399efd31b10f4d46f0bcb83784368e2983f607b2c3aa0ae5004`. The shared Mesh:Tool/Kiri:Moto bridge captures export destination before storage waits, uses metadata for replacement checks, and reports immediate export or workspace conflicts. Local desktop, emulated-phone and 4K and live emulated-phone real-account checks generate a real Mesh STL and Kiri sliced G-code, change each destination during a delayed save, verify server sync and fresh-session recovery. Immediate-conflict branches were not separately fault-injected in this test. Exact live files were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `be714b7cb0c4c2f8a04985841252c9e2b475ca2ca9362f38d859db782ea1da4e`, Caddy SHA `ffe6933828d8e6ed7bd914dc54f96b4c00ba08b10fb39ff646329053da7e96f4`; rollback snapshots `/var/backups/webhost-sites/change-20261031T192252219575Z` and `/var/backups/webhost-sites/change-20261031T192252219988Z`. Physical touch, printer profiles and physical fabrication remain unverified.


## 2026-10-31 Audio Editor starter tone

Live static release `711c99133436f84072e7644af2ca00e905b410efbbbfe6ee9fe7bb3baa2f1db7`, Audio Editor bundle `26deab9119f47dfd7e24666b91afb14b21d989bf0f06c04e90bc21b03dfa9dfa`, replaces `346461e0f54eea6d7ae183b91319c612d77610543c680f82dde152131b4bbe8d`. The app can generate a one-second mono 440 Hz tone at the browser audio rate, with short fades, without microphone or upload; it is unsaved work and prompts before discarding. Local desktop, emulated-phone and 4K and live emulated-phone real-account tests check waveform, reverse, close warning, saved WAV samples and rate, sync and fresh-session reopening. Exact live files were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `b8cd96a4fabc00e5742564cd233eb97a56a86bc83ed00171935d3ec2ca81eb02`, Caddy SHA `9d9251ce36339aacfad89dd7637a70ae0e9e1eb3085180f32d07a8883b53198e`; rollback snapshots `/var/backups/webhost-sites/change-20261031T192446884290Z` and `/var/backups/webhost-sites/change-20261031T192446884700Z`. Physical touch, microphone and playback hardware remain unverified.


## 2026-10-31 Image Editor blank canvas

Live static release `10757f08adfdb3a7e50e843fee1df17fe5bcb580cdd0c76dbce02d34fbf28c0d`, Image Editor bundle `c0cbbf9235bf457ec8566e6741f8e2d07022fbcd9c293604ae248be21ade3549`, replaces `711c99133436f84072e7644af2ca00e905b410efbbbfe6ee9fe7bb3baa2f1db7`. New blank image creates an unsaved white 800 × 600 canvas with `/Untitled.png` as its default My files destination; an existing file remains protected. A saved new canvas attaches the existing file watcher. Local desktop, emulated-phone and 4K and live emulated-phone real-account tests cover the close warning, existing-name protection, resize, save as, sync and fresh-session reopen; existing local desktop/phone Save As regression also passed. Exact live files were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `5ed02504da7edceb1417c7727971c2f8c0b89f94cfeecfa8057e4896a6f9b721`, Caddy SHA `b9fc8a47feb9c5c865ba66da48070fa05c0debc4db181ea6dd9ad7fca6fc496e`; rollback snapshots `/var/backups/webhost-sites/change-20261031T192651898186Z` and `/var/backups/webhost-sites/change-20261031T192651898595Z`. Physical touch remains unverified.


## 2026-10-31 Calculator notes

Live static release `1d9144ea9ee4eb3830a4017c306160a1397bb70c5a87b24be2ec96632fd0420e`, Calculator bundle `2e39e9e052e3611b458c54a28d0705aa6998805fb679fbed8866575b5a2ccc38`, replaces `10757f08adfdb3a7e50e843fee1df17fe5bcb580cdd0c76dbce02d34fbf28c0d`. The current calculation can be saved as a My files text note containing expression, angle unit and result. The user must recalculate after changing input or angle mode; the save captures its values and destination, protects existing files and identifies conflicts. Local desktop, emulated-phone and 4K and live emulated-phone real-account tests cover stale-result guard, overwrite cancellation, a delayed save with changed input/path, synchronization and fresh-session Text reopen; the local existing calculator workflow passed. One parallel phone run hit the login service busy limit and passed when rerun alone. Exact live files were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `b95732cde34c565040ca535f223817fb1133caa21eb81bba227283b26539f71c`, Caddy SHA `0eaa438b5a66c07da7de3b7897aa4073614fe72b2c639b720dfd27276998f6ae`; rollback snapshots `/var/backups/webhost-sites/change-20261031T192920119861Z` and `/var/backups/webhost-sites/change-20261031T192920120293Z`. Notes are not restorable calculator sessions; floating-point and physical-touch limits remain.


## 2026-10-31 Data Explorer synthetic starter data

Live static release `de66f1ee24705603d8c8cef3030980b202a20dbd06a60bedfe05423a0ddde10d`, Data Explorer bundle `e25c127f03d831124116f3521cf76a266d0a7d42b63536afc87f25d5d1bcdc2e`, follows intermediate release `5d3140e148915dfa309dd7a5323c29fb40033455ba5f4b2e96fb21f0f7e1e69e`, which followed `1d9144ea9ee4eb3830a4017c306160a1397bb70c5a87b24be2ec96632fd0420e`. Create example CSV writes labeled synthetic resistor data into My files without replacing an existing file. A contextual explanation and example SQL calculate 1,000 ohms; changes while creating the CSV remain open. Result-export completion is now reported after temporary-file cleanup so a following action is not ignored. Local desktop, emulated-phone and 4K and live emulated-phone real-account checks cover creation, a held write and edited draft, collision protection, actual SQL result, CSV/project sync and fresh-session reopening. An initial local test found an immediate follow-up click ignored during cleanup; the code and test were corrected. The prior local stale-query regression passed. Both live test accounts had their exact files deleted and were disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `bad3cc270515162f54b0c546f43d88cbb29124834355f9644b3dc88f4e0279e2`, Caddy SHA `c304fd23ef5c4c67a825e2f70f3838e03d13e7515cfd34cf33185aa375e3a7c7`; final rollback snapshots `/var/backups/webhost-sites/change-20261031T193343405649Z` and `/var/backups/webhost-sites/change-20261031T193343406060Z`. Synthetic values are not hardware validation; physical touch remains unverified.


## 2026-10-31 Falling Blocks Files reopening

Live static release `0115bfa3468e9c39e077784317ec922c55f16800800ac8d75cea4744a42a2927`, Falling Blocks bundle `878ee996258b82a7a90527be6f2dae549fdd527b6af25c7b3557b55d86b25b42`, replaces `de66f1ee24705603d8c8cef3030980b202a20dbd06a60bedfe05423a0ddde10d`. The shell admits Falling Blocks as a document app and identifies its bounded `.game.json` snapshots by format and app ID before routing; unknown game formats fall back to Text. The game accepts a launch path, restores paused, and records the saved/opened path for desktop layout; starting a new game clears that link. An immediate conflicting save is labeled and remains dirty. Local desktop, emulated-phone and 4K and live emulated-phone real-account tests use Files Open, compare the complete restored paused game, save a copy, check unknown-game fallback and fresh-session reopen; local model and delayed-save regressions passed. The initial Files test exposed the missing shell launch allowlist and was corrected; a parallel phone run hit the login service busy limit and passed alone. The already-published coach asset was copied for this build only after matching its reviewed SHA-256 `f1719c678e0b78b2c29f063d07872b301ff4cc577f819db3d13860424a6bd707`; generated assets and dependencies remain outside Git. Exact live fixtures were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `192d1a624429bf5586019c4415bb1e3b700acae21f23c8eff9cc036199d4b22c`, Caddy SHA `5e8cbdaa691969f8be112818db3829f828cd535e5d1820e8f6d93cafdbf70968`; rollback snapshots `/var/backups/webhost-sites/change-20261031T193852624266Z` and `/var/backups/webhost-sites/change-20261031T193852624679Z`. Physical touch and full game acceptance remain unverified.

Notebook audience update (work in progress): New source adds a measurement-mean starter cell and a collapsed guide explaining execution, My files, and the separate temporary Linux environment. A local Chromium/Pyodide run executed the example (Mean: 12.10), edited and saved a notebook, and reopened its edited version. The broader upload workflow timed out and emitted WebAssembly memory-allocation errors while multiple notebook kernels were being created; this does not establish its cause. The new changes have not been deployed. Re-test with a fresh browser and adequate memory, including phone and 4K, upload, sync and cleanup, before release.

## 2026-10-31 Notebook starter and picker coordination

Live static release `8ac4f24e8802f95aad746d43d96f3d507996294b9580592d3c822da2d485c79d`, notebook bundle `0ba4eaff226736e18884b88cdf98295397aebf3d4e047dc3cb6d05b01c22a7fd`, follows `0115bfa3468e9c39e077784317ec922c55f16800800ac8d75cea4744a42a2927`. The notebook includes a runnable measurement example and a collapsed guide explaining browser Python and temporary Linux. The file picker holds off autosave while a selection is pending, so a save starting during selection cannot silently consume the open action. Local desktop, emulated phone and emulated 4K tests execute the example, cover save races and re-open from a fresh account session; the phone/4K tests intentionally leave the picker open longer than the autosave delay. A live emulated-phone run reached example execution, delayed picker, saving and fresh-session recovery, but Chromium became unresponsive during cleanup and eventually disconnected; full live cleanup/lifecycle verification did not pass. From a separate fresh session the exact test fixture files and folder were removed and the witnessed test account disabled. The earlier multiple-kernel WebAssembly allocation errors and this browser disconnect have no confirmed cause; investigate on a fresh physical device/browser and repeat lifecycle and upload checks. Physical phone touch remains unverified. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `49d8187105840c43c35385a85d4a934829f5e528190520ecb726552da68277b4`, Caddy SHA `0a69fe0d7dd818b5221eb9c1f679d5edae67d598020711863a7af7f8bd206f5b`; rollback snapshots `/var/backups/webhost-sites/change-20261031T194546438615Z` and `/var/backups/webhost-sites/change-20261031T194546439036Z`. The root, `/desktop/` and `/blog/` returned 200 after activation.

## 2026-10-31 Notebook close investigation

Live static release `738ce0b1638ea0c2493e005964fc57f53c74b684eba22d04222ceae15cafcac0`, notebook bundle `1d9094c52e8c648fef2e6e854321880a634f29fdc52270005f14e00b6401e2f3`, replaces `8ac4f24e8802f95aad746d43d96f3d507996294b9580592d3c822da2d485c79d`. A second unmodified live emulated-phone workflow stalled at notebook close. The renderer stopped answering CDP and its main thread was waiting in native Chromium; native symbols were unavailable. A controlled run suppressing the notebook iframe's `about:blank` navigation before removal completed. The app now removes the iframe directly, avoiding that redundant navigation. Local emulated-phone lifecycle test passed two independent kernels, close/reopen, working-copy cleanup and saved account files. An unmodified live emulated-phone workflow then passed example execution, editing during save, delayed picker, fresh-session recovery, close and file cleanup; the witnessed test account was disabled. This supports the change but does not prove the browser's internal root cause or guarantee physical-phone behavior. Prior intermittent multi-kernel WebAssembly allocation errors remain unresolved. Test inputs and browser profiles were removed; user data was preserved. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `2ace3665424a3252717e78c19ff973a046844d7e2b71e6b87c6a43f05e81a95e`, Caddy SHA `531436806e9610e4fab0881fbfa8e2bf911d5c692b563f1440ed6045fdd5facb`; rollback snapshots `/var/backups/webhost-sites/change-20261031T195326442601Z` and `/var/backups/webhost-sites/change-20261031T195326443013Z`. Root, `/desktop/` and `/blog/` returned 200 after activation.

## 2026-10-31 PDF chooser ordering

Live static release `dbff3b2002c6e6c5450345d227edf04f3310c541f926c4f41cf91af5782a032f`, PDF Viewer bundle `ccb22a2be47b0186426476f8a3cfc90d87e4d81382d8a6085fbf80fc14b450ef`, follows intermediate release `7ca12364ede72322a35c690c490fbcfcc093643a591fc6048b62df3c9bfac6be`. Picker results are ordered against later choices, open and reload requests; cancelling restores the current page status. Local desktop, emulated phone and 4K, and live emulated-phone tests use controlled delayed chooser results to test the order and cancellation; a separate live emulated-phone test exercised the real My files picker, PDF search and failed-open recovery. The local cross-session reload regression passed. Exact test files were deleted and witnessed accounts disabled. Physical touch is unverified. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `7b135eca66c0be43b9e71bf5e1f9c9ab9c0dff413ed1a07a733641ba5b1903ab`, Caddy SHA `b0162d395ec0d05f12053f370af711c7a777a4a3a1cd5138162149abd4c3c15f`; final rollback snapshots `/var/backups/webhost-sites/change-20261031T195709596008Z` and `/var/backups/webhost-sites/change-20261031T195709596424Z`. Root, `/desktop/` and `/blog/` returned 200.

## 2026-10-31 CAD surface area

Live static release `7f035963451742bc87791af49fbf6155c8f448476d4cc27a5236505dc04dedb2`, Replicad bundle `dd92d2e44e493273e48192341760e480da58b6163092a341e97a18595f4d1b1f`, follows `dbff3b2002c6e6c5450345d227edf04f3310c541f926c4f41cf91af5782a032f`. The browser worker measures total surface area from the solid, including the wall of a through-hole, and the preview reports it alongside volume. Local desktop, emulated phone and 4K and live emulated-phone account tests compare offset-hole box and cylinder areas to analytic formulas, inspect exported hole vertices, save and reopen the project. The exact fixture files were deleted and witnessed test account disabled. This does not establish manufacturing accuracy; physical touch remains unverified. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `c5b791647f35b37f417aa2332a36f48ad8c6897d46e9d2bc407c5622a9575db9`, Caddy SHA `894b1842d9a62844d1bcbc74a22ce6d8ddf5a6deb76c8c93c35fbc0399d226fd`; rollback snapshots `/var/backups/webhost-sites/change-20261031T195906814198Z` and `/var/backups/webhost-sites/change-20261031T195906814599Z`. Root, `/desktop/` and `/blog/` returned 200.

## 2026-10-31 SVG editable example

Live static release `94f8e5af37e767c5e9dbb85c7287cfb75d3c21cbec8f1778864c02c0b7eee400`, SVG Editor bundle `c70ead0dd75f0430b30e7518b222970e2e154700725b0ab2158685af3e43b5a9`, follows `7f035963451742bc87791af49fbf6155c8f448476d4cc27a5236505dc04dedb2`. Try example loads an editable rectangle-and-circles illustration into a new unsaved document, asks before replacing unsaved work and leaves an earlier saved file intact. Local desktop, emulated-phone and 4K, and live emulated-phone account tests cover editing, declining replacement, saving, sync, fresh-session reopen, starting a new example after a save and close. The illustration is not fabrication validation; complex SVG and physical touch remain unverified. The exact test file was deleted and the witnessed test account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `18a0b89bc745fa511a3709078a33f1753fb1a7760b1f98a1512efbecd9dd317e`, Caddy SHA `fcad47a36087c12c6a945eac27b015b4115cf794a92cc82c9d38e14bdf042a91`; rollback snapshots `/var/backups/webhost-sites/change-20261031T200126231513Z` and `/var/backups/webhost-sites/change-20261031T200126231916Z`. Root, `/desktop/` and `/blog/` returned 200.

## 2026-10-31 Excalidraw images from My files

Live static release `20e9223dc753594a5070927306b9605d201a2370056f106166637bf2d24756d0`, Excalidraw bundle `779dd823b0e491f374c1d8f8f0bcfa1522fb901e038bbdebec164be0ca1a701d`, follows `94f8e5af37e767c5e9dbb85c7287cfb75d3c21cbec8f1778864c02c0b7eee400`. The app inserts decoded PNG, JPEG or WebP from My files and embeds the image data in the drawing. It checks the file signature, rejects conflicts and invalid files, and reports when the encoded image alone exceeds the 128 MiB document limit; total document size and device memory can still prevent a save. Opening a drawing brings its content into view; a 4K-to-smaller-window test exposed the previous off-screen result. Local desktop/phone/4K PNG and desktop JPEG/WebP account tests use Files upload, invalid-image recovery, insertion, saving, removal of the original, and visible fresh-session reopening; the PNG path passed live at emulated-phone size. Existing Excalidraw upload regression also passed locally after fixing its packaged-Chromium temporary-file path and position-dependent Save selector. Physical touch, all image variants and large-image memory remain unverified. Exact test files were deleted and witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `fd81a7571e56114a61d961c8d8e8cc6f0cc4b6ab0af897fdfc978fc4a046ca29`, Caddy SHA `8d7b29acf188599707ee1d542e4270188b9a76ec951e992fa99a5e56d6fa2ad0`; rollback snapshots `/var/backups/webhost-sites/change-20261031T201015071690Z` and `/var/backups/webhost-sites/change-20261031T201015072116Z`. Root, `/desktop/` and `/blog/` returned 200.

## 2026-10-31 Excalidraw image preparation

Live static release `f1184f6fd6f7fbdf489b0ea63bfd81148e7f7d98c06b0f46c000a3c18ec215ec`, Excalidraw bundle `266d5bb69329d2a394df281a42d163c397930d8eb2f2896606a783190c021c7f`, follows `20e9223dc753594a5070927306b9605d201a2370056f106166637bf2d24756d0`. Open, insert and save actions are disabled during image selection and decoding, with an adding-image status after selection; the canvas remains editable. Local desktop, emulated phone and 4K and live emulated-phone account tests hold image decoding while drawing a rectangle, check the disabled Save button, verify the rectangle and image survive saving, and test Undo/Redo buttons, source deletion and fresh-session visible reopen. An initial 4K test clicked a toolbar-covered canvas corner instead of drawing; a central canvas position corrected the test. Keyboard undo and physical touch were not established by these checks. The exact test files were deleted and witnessed test account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `124d1ce87812a80a0cdb9f31ed459f0084ab6fbec3d38e5c0c89a9838ed53f2f`, Caddy SHA `8e6e598f6f0a3eaf198f023842648555bddd6941caf517ca67677555848bee12`; rollback snapshots `/var/backups/webhost-sites/change-20261031T201418181262Z` and `/var/backups/webhost-sites/change-20261031T201418181679Z`. Root, `/desktop/` and `/blog/` returned 200.

## 2026-10-31 Excalidraw PNG export

Live static release `449652c66e2cf962eb0b46b58d946eae966bf268c9e90de1251d72af6460be4b`, Excalidraw bundle `6745d2b7bc42dc5b221a8b51ad1a4520dd5265bc015ade9ac44c68dc3e56aa68`, follows `f1184f6fd6f7fbdf489b0ea63bfd81148e7f7d98c06b0f46c000a3c18ec215ec`. Export PNG renders a captured drawing into My files, bounded to a longest dimension of 4096 pixels; the editable project is saved separately. Existing destinations require confirmation and version checking. Local desktop, emulated-phone and 4K and live emulated-phone account tests cover an edit and filename change during delayed export, overwrite cancellation, editable project save, sync and PNG reopen in Image Editor. Separate local and live phone-sized checks confirm pixels from an embedded image appear in the exported PNG. Large and complex scenes and physical touch remain unverified. Exact test files were deleted and witnessed test accounts disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `33e53579080e397510815ba5c23ca8079622eba19c483ad5f0de4184df4e68f0`, Caddy SHA `f73cd9dc68f9679305b0a8d51a2cf6df4e13d24379570b346513052726844280`; rollback snapshots `/var/backups/webhost-sites/change-20261031T201721996050Z` and `/var/backups/webhost-sites/change-20261031T201721996540Z`. Root, `/desktop/` and `/blog/` returned 200.

## 2026-10-31 Spreadsheet export conflict reporting

Live static release `d6b8b54af2a6e2f7643d917388458eee4da2deded9b15216d44ce6556452c4ad`, Spreadsheet bundle `78a28f6eaf60eb58ad1ffd6c9fa372dc7242370d2cd41c06796f8d196870c6c9`, follows intermediate release `1e4e9fef1584cf1819027c9fdf2096f08f4bb9e84fef953ecffb4f246c026caf`. CSV and XLSX exports inspect the mirror write result and report conflicts rather than claiming normal sync; the message also identifies newer edits omitted from the captured export. Local desktop, emulated-phone and 4K and live emulated-phone tests arrange competing server writes after the export version check, check both retained copies and open the separately saved workbook in a fresh session. Two exact test accounts were cleaned and disabled. Physical touch remains unverified. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `c7a16206859b196b02cc97a006694a889449f7adb56c2807906514bca18b6d44`, Caddy SHA `2d3ddd4487e316e5f7918a7aaa4fb8dcd50aef18996e6008a076e0df53817bbc`; final rollback snapshots `/var/backups/webhost-sites/change-20261031T202109332983Z` and `/var/backups/webhost-sites/change-20261031T202109333463Z`. Root, `/desktop/` and `/blog/` returned 200.

## 2026-10-31 Spreadsheet source warning during export

Live static release `d4a750be431a5c3a91efd52fd7afee64edbc9192623544195c915e662f1809be`, Spreadsheet bundle `ced66ee092db60163199424737ac96468efeecb6a70e0031fd8c995338d9d5e0`, follows `d6b8b54af2a6e2f7643d917388458eee4da2deded9b15216d44ce6556452c4ad`. A separate notice reports workbook changes, conflicts or an unavailable check while action status remains visible. The workbook is rechecked after open, save and export so a change arriving while busy is not missed. Local desktop, emulated-phone and 4K and live emulated-phone tests hold CSV conversion while another session changes the source, then check the notice, retained export result, saved copy and fresh-session recovery. A save-conflict regression initially exposed a status-message regression; the final version passed that regression locally and live, along with the export-conflict test locally. Two exact live test accounts were cleaned and disabled. Physical touch remains unverified. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `b016210e32b15cf69876faaabcb6cfacbf00d9d33c00d85ed872f8f9bbed6cc6`, Caddy SHA `62e6e5d9bcfa9e2848853fcd39440ac62a5c96ed23f7d5094fd512ec9aec5b69`; rollback snapshots `/var/backups/webhost-sites/change-20261031T202436525616Z` and `/var/backups/webhost-sites/change-20261031T202436526070Z`. Root, `/desktop/` and `/blog/` returned 200.

## 2026-10-31 Arduino example source workflow

Live static release `6a757fc4f87d0944c3301416bf607d647dd779f121629c70b19cf3b57fd718fc`, Arduino Simulator bundle `41215544e0767c29620757e47e0297aa4c4e8ce0d0c325b49110f1fdf7a85925`, follows `d4a750be431a5c3a91efd52fd7afee64edbc9192623544195c915e662f1809be`. Save example C now writes the matching source for the selected bundled Blink, serial echo or D2 firmware to a selectable My files location; it is disabled for arbitrary opened HEX, whose source is unknown. The source and destination are captured at save start, and source/serial output saves report immediate file conflicts. Local desktop, emulated-phone and 4K and live emulated-phone tests cover all three sources, switching firmware during a delayed save, serial echo, D2 LED behavior, firmware save and source reopening in Text. Separate local and live phone-sized checks inject conflict return values for source and serial saves; these are not end-to-end conflict races. A prior test assumption expected a USART label where the source uses UCSR0, and a local bundle omitted CodeMirror; both test issues were corrected. Compilation, physical hardware and physical touch remain unverified or unavailable. Exact test files were deleted and two witnessed accounts disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `2df0aaa31f4bde4d994a5d28ddb595ff1b4dfa37016082dcc66d7b3a0817ed56`, Caddy SHA `3801fe5f7c69db7dc3ddfb4ea5dd07187cb5d140f7978f07c6c1b8c40be7f637`; rollback snapshots `/var/backups/webhost-sites/change-20261031T202826415431Z` and `/var/backups/webhost-sites/change-20261031T202826415926Z`. Root, `/desktop/` and `/blog/` returned 200.

## 2026-10-31 AVR sketch conflict research only

The isolated compiler experiment now reports a conflict returned while saving a sketch and shows a separate persistent notice for file changes/conflicts; it retains the draft and removes its subscription on close. Local desktop, emulated-phone and 4K tests created real competing writes in the isolated account service, retained both copies, compiled and ran the local draft in AVR8js, saved a separate copy and reopened it in a fresh session. Existing isolated account-switch, save-race, compiler-diagnostics/cancellation and real-account integration regressions passed. A first test attempt changed a file behind the editor and correctly hit stale-version protection before its intended race; it was corrected to use the editor's own offline save. The compiler and sketch editor remain **research only**, not deployed: exact toolchain corresponding-source and license/distribution provenance, production integration and physical-device validation remain unresolved. Existing public site and account state were not changed.

## 2026-10-31 AVR runtime provenance audit

A research-only byte audit matched 326 uncompressed AVR libc headers/libraries and ten linker scripts from the pinned `avrwasm.tar` to authenticated Ubuntu Jammy `avr-libc` and `binutils-avr` packages. Ubuntu's signed package and source indices identify matching source archives and packaging patches, which were downloaded and hash checked; see `docs/AVR_COMPILER_EVALUATION.md` for hashes, links, reproducible comparison and limits. The new audit script refuses substituted inputs; an intentionally substituted Debian package was rejected. Exact provenance for GCC, libgcc, WASM Binutils and Emscripten and a complete reviewed distribution path remain unresolved. No compiler was deployed and no live service changed. Downloaded research copies were temporary, not committed.

## 2026-10-31 AVR GCC header provenance

All 19 GCC headers in the pinned research archive match files in the official GCC 15.2.0 source tarball, including renamed headers; the tarball matched GCC's published HTTPS SHA-512. The detached signature was not independently verified. The AVR5 and AVR6 libgcc archives each have 1,182 unique members and 944 GCC 15.2.0 version-string occurrences; these labels do not prove their exact source or build. The new hash-pinned audit script passed and rejected a substituted source archive. See `docs/AVR_COMPILER_EVALUATION.md` for mappings and hashes. GCC/libgcc/WASM binary provenance, dependency materials and release review remain unresolved; the compiler is not live. No live service changed, and the downloaded source archive was temporary.


### G-code source change notification and reload — 2026-10-31

Live static release `0f3326d032dbefa6cae069a5f4b8a860f9aa0d82c423a6018fa504dfe6db8a88`, G-code Preview bundle `441fc590b2406655eaf655c2639013f77ab618bc432f570ebc74c7200171fe34`, follows `6a757fc4f87d0944c3301416bf607d647dd779f121629c70b19cf3b57fd718fc`. An independent notice reports a changed, deleted, conflicting or unavailable saved file without replacing the current preview; Reload checks server sync and keeps the preview if checking or opening fails. Choosing the example removes the file subscription; closing the window unsubscribes. Local desktop, emulated phone and 4K and live emulated-phone two-session account tests cover update, deletion, failed sync, example and subscription cleanup. The existing example/upload/sync/unsupported-file/reopen regression passed locally after fixing its test fixture path for Snap Chromium and waiting for Files to initialize. The exact live test file was deleted and the witnessed account disabled. Physical touch and machine safety remain unverified. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `a7b08204f5bf5356e7c8fdb7a5454553f224b0c3e50cf50d0187004107580ef2`, Caddy SHA `8d43d65b0bc3031d5f2094fe7fa16e2789733e4b1bcc6e4ec0df5da7eca00418`; rollback snapshots `/var/backups/webhost-sites/change-20261031T204450815748Z` and `/var/backups/webhost-sites/change-20261031T204450816166Z`.


### Grid tools workspace notices — 2026-10-31

Live static release `0be97f487b0ba077c98c66d5cf890ff338fd4488cfda4c544f3a52cfdd6765ab`, Grid tools bundle `1c658c20c1a39bd15449caf787c0b235ac51988e478f9a8049c8e4a5ec34272c`, follows `0f3326d032dbefa6cae069a5f4b8a860f9aa0d82c423a6018fa504dfe6db8a88`. Kiri:Moto and Mesh:Tool show a separate notice when mirror synchronization finds a changed, missing, or conflicting workspace. They retain the current model and recheck after busy operations. Local desktop, emulated-phone and 4K, and live emulated-phone, two-session tests change the saved source while a save is held, check stale-save refusal and persistent notice, save a copy, delete it and verify model and subscription cleanup. The real Mesh export and Kiri slicing/export snapshot regression passed locally. Detection depends on mirror synchronization, not instantaneous server push; physical touch and manufacturing correctness remain unverified. The exact live files were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `93235671cb455f186c455c5c54da984dfff773779a4b2188416a8c4e88e0cacf`, Caddy SHA `7a5bff896aea31d5bb1185d8471e109a1c04876c44c10009e58c1baf6e67b2d2`; rollback snapshots `/var/backups/webhost-sites/change-20261031T204933606041Z` and `/var/backups/webhost-sites/change-20261031T204933606507Z`.


### CAD to slicer to toolpath — 2026-10-31

Live static release `fe4c43b979d0724e6b93c38684d1e84ea6c76653428888337d6f040b5689e3f7`, G-code Preview bundle `849a17d3052bfa31677511dee6c2636e2d63674dd3c3869c3a67221a9c98e246`, follows `0be97f487b0ba077c98c66d5cf890ff338fd4488cfda4c544f3a52cfdd6765ab`. A real Replicad-generated STL was sliced by Kiri:Moto and initially rejected by G-code Preview: the latter mistook the T parameter on heater commands for a second command and rejected end-of-file homing. It now accepts T on M104/M109/M140/M190 and permits terminal homing while continuing to reject further moves or coordinate resets after later homing. Homing is not drawn or simulated. Worker checks verify unchanged motion geometry for heater selectors and terminal home and reject ambiguous multi-command lines and later moves/resets. Real project/STL/G-code export, matching account/server files and fresh-session G-code reopen passed locally at desktop, emulated phone and 4K, and live at emulated phone size. An older extrusion test used an invalid arc and was corrected before its regression passed. This is not a printer safety or compatibility test; physical touch remains unverified. The exact live test files were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `12a8c40e3a7ddc92f43309b674059ab18dd4d72adc6176f1a9d8d823e63b8ced`, Caddy SHA `182924f90de627d74944d46abb5651534efbdeaa88a9917defe4408cea2b08d4`; rollback snapshots `/var/backups/webhost-sites/change-20261031T205427285198Z` and `/var/backups/webhost-sites/change-20261031T205427285600Z`.


### Audio processing and restored track — 2026-10-31

Live static release `456a4eef1c99c5cffd929c4dd5f24f35088fbcc75c0aaacba33368309908ef5f`, Audio Editor bundle `e00db22e0e9793e4599f08f6453dd8ec82b32708ab1c4a8d4969daf3ca44295d`, follows `fe4c43b979d0724e6b93c38684d1e84ea6c76653428888337d6f040b5689e3f7`. Starting a new unsaved track clears the previous restored-file reference; successful open/save identifies the current file for desktop restoration. A per-frame OfflineAudioContext render counter prevents open, example replacement and save while those AudioMass effects are processing. Local desktop, emulated-phone and 4K and live emulated-phone tests hold a Reverse effect pending, confirm the earlier track is not saved, verify a sample from the completed WAV, and check old-file and saved-file behavior after refresh. The existing tone/edit/sync/fresh-session regression passed locally after correcting its asynchronous-effect wait. Other effect implementations, physical microphone and physical touch are not covered. The exact live test file was deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `498c21e57972d90f08453e4ac32cb1a81962a56a9d777d90dc1dc57f5d1d44c7`, Caddy SHA `5c3fd70dd64cd0910cbc39604662d8cf256bc6ad9eee2271a92f11644228e3b2`; rollback snapshots `/var/backups/webhost-sites/change-20261031T205825917918Z` and `/var/backups/webhost-sites/change-20261031T205825918339Z`.


### Pico serial conflict notices and Blink layout — 2026-10-31

Live static release `24c3fbc430cbeee2776ecde7d48bd4d4aa5a2d9d871046d3f8a67443511b2e62`, Pico Simulator bundle `218bdc913d031a2e131e0f1f52383f2d0c351a9ad3c3eb8369394f7d9e82b4aa`, follows `456a4eef1c99c5cffd929c4dd5f24f35088fbcc75c0aaacba33368309908ef5f`. A serial-output save reports an immediate conflict and a separate watcher reports a later mirror-detected conflict, change or unavailable file. Run Blink and replacement UF2 clear a prior project layout association. Local desktop, emulated-phone and 4K and live emulated-phone account tests cover synthetic serial output, an injected immediate conflict, a real two-session later conflict, server-side resolution, Text reopen, project layout and worker/subscription cleanup. A separate real Blink worker test passed locally and live at phone size; no private ROM was uploaded. The exact live test files were deleted and all three witnessed accounts disabled. Physical touch and arbitrary firmware remain unverified. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `6aa8f21f24c7815350d31a7ff7a75b66b3737c8fe6b11bc86994bc98d2477a79`, Caddy SHA `80bbbf37e4ef700711f4ce0f5116f3fc91c1d141ca24946122e6265b78183d62`; rollback snapshots `/var/backups/webhost-sites/change-20261031T210248445996Z` and `/var/backups/webhost-sites/change-20261031T210248446463Z`.


### Digital Logic circuit and truth-table notices — 2026-10-31

Live static release `9010143a3246ed54ff6dcc9fd73c9db0173d2fcce209fbfc80dcc319d18c3dc3`, Digital Logic bundle `caa1a888afc87d418eddcbdccbc7c9d62471c5b7b96c849c2b71ef6c8d89b5d9`, follows `24c3fbc430cbeee2776ecde7d48bd4d4aa5a2d9d871046d3f8a67443511b2e62`. Distinct persistent notices report mirror-detected changes, missing files and conflicts for the saved circuit and last saved truth-table CSV. Immediate conflict return values are reported, and loading an example clears the old layout association. Local desktop, emulated-phone and 4K and live emulated-phone two-session checks cover a real CSV conflict, circuit change and fresh-session reopening, retained table, layout and subscription cleanup. Immediate conflict return values were injected. Local metadata/stale-save and two-bit adder truth-table and interactive regressions passed; the metadata test now looks for the separate notice. Detection depends on mirror synchronization; physical touch remains unverified. The exact live files were deleted and the witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `f313eb177f67bfe7b0f50e446e36b8b2cd61d27e1081da2f042839cbfc077e71`, Caddy SHA `d6a6648bd0a2d7f2c6e00c2bcd41e285ef18f3f3b5166566406a861a7b07ff8f`; rollback snapshots `/var/backups/webhost-sites/change-20261031T210640814491Z` and `/var/backups/webhost-sites/change-20261031T210640814895Z`.

### Arduino v86 compiler feasibility — 2026-10-31

Research only; no live release changed. A hash-pinned Debian i386 AVR toolchain was installed into the temporary v86 9p home of an isolated local desktop. The real guest compiled the bundled D2 C example, explicitly copied HEX to the account mirror, and the actual AVR8js worker drove D13 from D2. It also compiled a minimal Arduino-core C++ setup/loop sketch and drove D13; invalid C++ was rejected. The repeat using `prepare-v86-avr-probe.py` took 58.523 seconds to unpack 36.1 MB, 2.849 seconds for the C example and 18.039 seconds for the small sketch/core build on this workstation. This is not the full `.ino` preprocessor or library ecosystem and is not a physical-device or phone test. An initial run failed for missing `libdl`; adding the matching guest library fixed it. Debian package and corresponding-source index hashes, 47 checked Arduino core files, input pins, instructions and outstanding distribution/UI work are in `docs/AVR_COMPILER_EVALUATION.md`. Research test is loopback-only. No compiler has been deployed.


### Empty files in temporary Linux — 2026-10-31

Live static release `98c9e1ea94d513b291ff00b591745b8d6aadad9969e8565c77ead69cff9e5c90`, guest worker SHA `833223741122cbb6a30e3897fff1ac782ea0eb8f74266575ea967c7b87e7cc93`, follows `9010143a3246ed54ff6dcc9fd73c9db0173d2fcce209fbfc80dcc319d18c3dc3`. v86 returned a bare File not found error for a zero-byte guest-created file despite successful stat. The worker now returns zero bytes for an existing empty file while retaining normal directory and missing-file checks. Local desktop, emulated-phone and 4K and live emulated-phone tests create empty files from shell and browser, list Linux home through Files, explicitly copy an empty file to My files, synchronize, reload and verify the account copy survives while Linux home resets. Physical touch remains unverified. The exact live account file was deleted and its witnessed account disabled. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `0f66bb79d0d465548e37b255913f248f91b6fae311f998efa7e3a35625c70881`, Caddy SHA `7b265e1bc4e2711bd509008e2b6df81e72065fcbd9912ecc9e31d053e5fff865`; rollback snapshots `/var/backups/webhost-sites/change-20261031T213123924669Z` and `/var/backups/webhost-sites/change-20261031T213123925158Z`.

### v86 AVR bridge research — 2026-10-31

Research only; no compiler shipped. A narrow adapter in `tests/fixtures/avr-compiler-probe/v86-guest-compiler.mjs` writes source as data into unique temporary guest folders, uses dedicated multiplexer sessions and fixed build commands, and returns HEX/diagnostics. It bounds source, returned output, timeout and two concurrent builds per instance. `tests/avr-v86-bridge-research.test.mjs` passed on an isolated real v86/account mirror: two concurrent builds (valid and invalid), third-build refusal, source containing shell-like text remaining data, error reporting, HEX save and AVR8js LED, cancellation, a three-second process check, original terminal continuity and guest-folder cleanup. A previous run found zero-byte guest-file reads failed; the production worker fix is documented above. This is not a global resource limit or general process sandbox, and the sketch UI, preprocessing, libraries, account-change handling, full resource controls, release/source notices and phone tests remain outstanding. See `docs/AVR_COMPILER_EVALUATION.md` for setup and limits.

### Isolated v86 sketch UI — 2026-10-31

Research only; the live Arduino Simulator still does not compile sketches. A disposable app overlay and isolated host service now combine the v86 compiler adapter with the account-backed sketch editor. Local real-v86/account tests save source, compile and run LED firmware, save HEX, report a source-line error, cancel, reject stale builds, clean the temporary compiler on close, reopen source in a fresh emulated-phone session and check another account cannot read it. A separate fresh emulated-phone session reopened synced HEX and ran it without restoring the temporary compiler. The initial test accidentally reloaded the page while changing Chromium mobile emulation after a successful build; a corrected resize run passed. The implementation only prepends Arduino.h and supports a minimal core, not full .ino preprocessing, Serial or libraries. Toolchain installation and limits are per window; shared resource controls, release/source and license materials, broader lifecycle tests, physical touch and hardware validation remain open. See `docs/AVR_COMPILER_EVALUATION.md` for the research-only staging helpers and reproduction.

### Desktop close confirmation — local candidate

The desktop's window Close control now uses a themed, keyboard-accessible dialog for unsaved work, offering Keep editing and Discard changes; Escape keeps the window open. Local registered-account tests with a real edited Text document passed at desktop, emulated-phone and 4K sizes, including cancel, Escape, discard and absence of a native browser dialog. This candidate is not deployed. App-specific confirm/prompt/alert calls, including file naming and replacement, are separate and remain to be migrated; physical touch has not been tested. See `tests/desktop-close-dialog.test.mjs`.

### Text open/reload confirmation — local candidate

A shared asynchronous `host.ui.confirm` desktop service and Text's dirty-document open/reload flows now use themed dialogs in the isolated preview. Escape, cancel and app-abort settle without discarding; account validity is rechecked after each prompt. Local registered-account tests at desktop, emulated-phone and 4K sizes cover cancel/discard, opening a second My files document, reloading the saved document, and abort cleanup without a native browser dialog. This is not live. Other app-specific confirms, text prompts, vendor dialogs and physical touch remain to be addressed. See `tests/text-confirm-dialog.test.mjs` and `apps/system/CONTRIBUTING.md`.

### Files desktop dialogs — local candidate

Files now routes new file/folder, rename, copying, ZIP, deletion and conflict prompts through desktop-styled asynchronous dialogs in the local candidate. The text-entry service returns null on Escape, cancel or app abort; actions capture and recheck relevant drive/destination context after awaiting. Registered-account local desktop, emulated-phone and 4K tests cover new file/folder, cancellation, rename, server synchronization and abort cleanup without native dialogs. An initial rename test attempted to move a file before sync; the corrected test waits for sync. Copy, ZIP, delete and conflict flows still need targeted regression testing with these new dialogs before deployment. No live change; physical touch remains unverified. See `tests/files-dialogs.test.mjs`.

### Shared Arduino compiler research — local only

The isolated overlay shares one v86 AVR toolchain installation and the existing two-job cap among Arduino windows in one guest. The manager unit test and real-v86/account browser test passed one download/installation, cancel of one window during preparation, closing one during concurrent builds, surviving firmware execution, My files saves, terminal continuity and cleanup after the final window. Early test failures were a window selector mistake and an unhandled new themed close dialog; both were corrected before the pass. This remains research-only: no live compiler, no cross-tab limit, no proven complete resource/account-switch controls, minimal core without full Arduino preprocessing, Serial or libraries, and distribution/physical-device work remains. See `docs/AVR_COMPILER_EVALUATION.md`.

### Files dialog regressions — local candidate

The updated Files desktop dialogs passed local registered-account copy, ZIP extraction and real two-session conflict-resolution regressions at desktop, emulated-phone and 4K sizes. Coverage includes cancellation, collisions, stale files, nested folders, fresh-session recovery, retaining both conflicting versions, accepting/cancelling resolution and server sync. The first 4K conflict attempt timed out at login while three test suites ran concurrently; a separate sequential rerun passed. The native-dialog test handlers now flag unexpected browser popups. Create ZIP, delete, guest copy and physical touch still need direct tests; the candidate is not deployed.

### Remaining Files dialog actions — local checks

A registered-account test created a ZIP using the themed filename dialog, inspected its contents, cancelled deletion, then confirmed deletion and verified it on the server. This passed at desktop, emulated-phone and 4K sizes; the deletion menu was opened with a simulated right-click, so physical touch access was not established. A separate actual-v86 desktop test copied an empty shell-created Linux file through the themed prompt to My files, synced it and verified the account copy survived guest reset while the guest original did not. The same Linux-copy and reset test passed at an emulated-phone size. These changes remain local and other apps still have native dialogs. See `tests/files-archive-delete-dialog.test.mjs` and `tests/linux-empty-files.test.mjs`.

### Files touch deletion control — local candidate

Files adds a Delete toolbar action for the current selection on both drives, sharing the existing version-checked and themed-confirmation deletion path. It is disabled without a selection. Local registered-account desktop, emulated-phone and 4K tests created and inspected a ZIP, cancelled deletion, confirmed deletion and verified server sync; the phone test selected and activated Delete with emulated taps. Initial parallel test registrations collided or hit the issuer busy limit; separate reruns passed. This is not deployed and is not a physical-phone test. See `tests/files-archive-delete-dialog.test.mjs`.

### Classroom sign-in burst — local candidate

The live issuer currently allows two simultaneous Argon2 operations and immediately rejects further arrivals; its reverse-proxied issuer-IP allowance is 60 requests per minute. This is a concurrency/request-rate limitation, not a two-user session limit. The local candidate admits at most four password requests at once, waits up to three seconds for one of two 64 MiB Argon2 slots, reserves the other HTTP workers, and caps aggregate issuer peer traffic at 1,200 requests per minute while retaining the existing per-username throttle. The browser retries only explicit temporary 429 busy or 503 sign-in failures, with jitter and a fresh signed single-use challenge each attempt. It does not retry registration or wrong passwords. This raises the aggregate request ceiling and requires security/operational review alongside the bounded worker, password and username limits; it is not an unlimited queue or a capacity guarantee.

An isolated local issuer with the production per-username rate of 60 passed two consecutive batches of 30 simultaneous signed sign-ins from one browser/machine through the loopback proxy in 5.90 and 6.57 seconds; each batch had 96 temporary 429s handled by the client. Wrong password returned 401 after one attempt, and simulated 503 during registration was not retried. A separate real Argon2/SQLite unit test checks admission saturation, bounded waiting, correct sign-in, wrong-password failure and slot cleanup. A previous 600/minute candidate hit its shared limit on a repeated burst, prompting the 1,200 limit and clean retest. This is not a 30-device WAN or production-machine test, and no account-service or client changes are live. See `tests/classroom-signin-burst.test.mjs` and `tests/login_classroom_queue_test.py`.

### Classroom login UI and lifecycle recovery — local candidate

The 30-sign-in check now exercises 30 separate Chromium browser storage contexts and the real login form from one workstation/loopback address, with Linux boot deliberately disabled to avoid modeling 30 computers on one machine. Initial runs reached 26, 27 and 29 out of 30. One diagnostic showed a successful login followed by a 503 fetching the desktop lifecycle module, which caused `initializeWithRecovery` to discard the session and recreate a blank login form. The local candidate starts lifecycle monitoring in the background, keeps the authenticated session if its module load fails, and retries with bounded exponential delay and fresh module URLs. A corrected full run passed 30/30 in 6.59 seconds; a separate injected-503 browser test verified the session stayed signed in and monitoring recovered. An earlier test interception pattern failed to disable Linux boot and was corrected before this pass. Static files in the local issuer are served differently from live Caddy; this is not a 30-device, WAN, memory-capacity or physical-phone test. Neither the login queue nor this frontend change is deployed. See `tests/classroom-browser-contexts.test.mjs` and `tests/login-startup-lifecycle-retry.test.mjs`.

### Classroom issuer candidate on box-webhost — isolated probe

The live issuer runs with `MemoryMax=384 MiB`; observed current/peak were about 129/203 MiB. An eight-hash Argon2 probe on box-webhost measured 0.176–0.185 seconds and 77.8 MiB peak RSS for that isolated process. The real-live reference authentication source differs from the local source in a CSP header, so the candidate lifecycle was additionally tested with the exact live reference file. Its queue unit test passed, and `tests/login_classroom_host_probe.py` created 30 accounts in a temporary directory and passed a simultaneous 30-account sign-in probe on box-webhost in 6.13 seconds, with 120 temporary busy outcomes handled by the probe and 98.4 MiB peak RSS. This is not an HTTP/browser/WAN load test, does not use or change the live database, and does not prove sustained or concurrent workload capacity. Live service and client remain unchanged; guarded release packaging, rollback and production-equivalent checks remain before activation.

### Classroom issuer release staging

`/srv/codi-connected/releases/classroom-login-r1` is staged but not active; its verified manifest SHA-256 is `9d4bbe6dfe4f82e2dbb472e4ce8c1a7d0061f4466b4e5533d0b71a8ad8d22533`. It is copied from the exact live `file-admission-r1` baseline and changes only `origin_service/lifecycle.py` to the previously tested classroom candidate. Initial verification found six generated Python 3.12 cache files in the live release; an independent scan confirmed every other file matched the signed release manifest, and only those generated caches were removed. The existing live service runs with Python `-B` and remains on the old release. The staged release is not activation or a production-capacity result. Frontend packaging, operator exercise, guarded activation and live tests remain.

### Classroom deployment preparation

The desktop candidate `70a9306b59bee93a129acdc609cbf808aef5bb70ae79a7cc6e1e5e2a5dcc0647` is staged from live static `98c9e1ea94d513b291ff00b591745b8d6aadad9969e8565c77ead69cff9e5c90`, with only `app.js`, `desktop-apps.js`, `style.css`, `network/identity.mjs`, catalog and the Files/Text bundles changed; a manifest comparison found no other changes. Issuer `classroom-login-r1` is also staged. The pinned managed transition `exercise` upgraded then deliberately rolled back successfully, checked all hosted site statuses, restored the old issuer release and left no pending maintenance journal; issuer and guest returned active. Neither candidate is active yet. See `scripts/stage-classroom-frontend.py` and `scripts/activate-classroom-issuer.py`.

### Classroom and desktop dialogs live; gateway retry follow-up

Issuer `/srv/codi-connected/releases/classroom-login-r1` (manifest `9d4bbe6dfe4f82e2dbb472e4ce8c1a7d0061f4466b4e5533d0b71a8ad8d22533`) and static frontend `70a9306b59bee93a129acdc609cbf808aef5bb70ae79a7cc6e1e5e2a5dcc0647` are active. Managed issuer rollback exercise passed before apply; site status checks passed after apply. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `14a90f63af5784ac0071a0cd2f6ce46e3eaa28f0c819a76befd517ebf8bbe5f3`, Caddy SHA `73fabe0f6155402f5ed2ced57bf7b2127edf7fe14cb709c758931e6c606e826f` (verify actual hash before use); hosting rollback snapshots `/var/backups/webhost-sites/change-20261031T222337340067Z` and `/var/backups/webhost-sites/change-20261031T222337340563Z`. Live emulated-phone browser registration, fresh sign-in, Text dirty-close/reload cancellation and Files delete cancellation passed; the exact fixtures were removed and two witnessed accounts disabled.

A live 30-account signed sign-in burst returned 28 successes, two gateway HTTP 502s, 52 busy and 33 unavailable responses in 6.07 seconds. All 30 exact registered test accounts were disabled using the saved username/subject receipt. A follow-up frontend changes only sign-in retries to include HTTP 502 and 504, with fresh signed challenges; registration and wrong-password errors still do not retry. Explicit 502/504 can occur after a backend has processed sign-in, so a retry may leave an extra bounded, expiring session. A unit test covers 502/504, no registration retry and 401. Static candidate `31fb4e2c14a69a55e48d6db92ab820d3712567522d6c3fe75b58a48f0ce06726` is staged but not active yet. Full 30-user live test must be rerun and test accounts cleaned after activation. No physical-device or classroom-WAN capacity claim.

### Classroom live retry and burst check

Static release `31fb4e2c14a69a55e48d6db92ab820d3712567522d6c3fe75b58a48f0ce06726` is active after `70a9306b59bee93a129acdc609cbf808aef5bb70ae79a7cc6e1e5e2a5dcc0647`; it changes only the sign-in retry module, accepting 502/504 alongside 503 and bounded busy 429. The opt-in live signed-client test registered 30 disposable accounts, then all 30 signed in concurrently in 6.553 seconds from one browser/workstation, with 66 429 and 27 503 responses retried. All 30 exact receipt-matched accounts were disabled; no account files were created for this burst. The previous 28/30 attempt and its 30 disabled accounts remain documented above. This is a public-site server/API check, not 30 devices or a classroom WAN test; the local full-login UI check used 30 separate browser contexts. Issuer, guest and files services are active, no native maintenance journal remains, and root, `/desktop/`, `/blog/` return 200. Hosting manifest SHA `c5ed988b2b1ca6f7e68fcfb1960e34806421b9933f43b524a30c859c1fe7c5dd`, Caddy SHA `aa9895f7f215b9688fa02159947868a6104bd415cd14b335a9ba2e4fa24402e3`; rollback snapshots `/var/backups/webhost-sites/change-20261031T222621414141Z` and `/var/backups/webhost-sites/change-20261031T222621414643Z`. Exact disabled account receipts and temporary staging inputs should be removed after recording; unrelated accounts/state must remain untouched.

### Document Editor desktop dialogs — local candidate

Document Editor now uses shared themed dialogs for link entry, opening over unsaved work, replacing an existing document and replacing an existing PDF. Link entry captures the document revision and selection and refuses a stale target; file operations recheck the account after asynchronous prompts. Local registered-account desktop, emulated-phone and 4K tests cover selecting linked text, save, PDF overwrite cancel/confirm and sync. Existing desktop/emulated-phone tests passed failed-open draft preservation, document overwrite cancel/confirm, stale saves, export snapshot and fresh-session recovery after adapting them to themed dialogs. A first run timed out because a file-change notice replaced the transient PDF export status; the test now records the status when displayed. The underlying single status area can still replace an earlier message and remains a usability follow-up. No live deployment or physical-touch claim.

### Document Editor separate warning — staged candidate

Document Editor now keeps mirror-detected file changes/conflicts in a separate persistent notice so save/PDF export results remain visible. It rechecks after export, clears the notice when the observed saved version is current, and reports an unavailable check without claiming deletion. The tested dialogs and notice are packaged as static candidate `2be54aa8d118cc1d61b1f0c7ff2000ddc0f8bb0dabbddef9d85f05dadfd3dd3f` from live `31fb4e2c14a69a55e48d6db92ab820d3712567522d6c3fe75b58a48f0ce06726`, changing only Document Editor and catalog. Local registered-account desktop, emulated-phone and 4K open/export checks verify the warning and PDF result together; a real two-session conflict/resolution regression passed locally. The first conflict test still expected the old shared status location and was updated to check the separate warning. Physical touch remains unverified; this candidate is not live yet.

### Document Editor dialogs and warning — live

Static release `2be54aa8d118cc1d61b1f0c7ff2000ddc0f8bb0dabbddef9d85f05dadfd3dd3f`, Document Editor bundle `baba29d1e4438c3ed86af45d2f0d93fade08a4440266ed9a2c69021f0fa19b63`, follows `31fb4e2c14a69a55e48d6db92ab820d3712567522d6c3fe75b58a48f0ce06726`. Live emulated-phone registered-account tests passed link selection, save, PDF overwrite cancel/confirm, failed-open preservation, document replacement and a file-change warning alongside the PDF export result, sync and fresh-session recovery. Two exact test accounts' fixtures were removed and accounts disabled. Local desktop, emulated-phone and 4K checks and a two-session conflict regression also passed; physical touch remains unverified. Issuer, guest and files services are active; root, `/desktop/`, `/blog/` return 200. Hosting manifest SHA `2c070de954a1f9e386d65c5e00fc41e179b8c3b3a6cbeea965be44b546fead1d`, Caddy SHA `bc97365972d34510c9351ca74fe3f2a8009ae4d2007a49ed1de12daf8c904200`; rollback snapshots `/var/backups/webhost-sites/change-20261031T223157813727Z` and `/var/backups/webhost-sites/change-20261031T223157819737Z`.


### Spreadsheet themed file confirmations — local verification before live rollout

Spreadsheet open-over-unsaved-work and save/XLSX/CSV replacement now use the shared asynchronous desktop dialogs instead of browser-native confirm popups. The app rechecks the current account and target version after the answer; if the file changes while the dialog is open, it aborts without replacing that copy. Cancel preserves the existing sheet/file. The Files upload control now keeps its selected File objects alive until account storage has read them, then clears the picker; Linux uploads remain converted to bytes. A local upload probe initially failed because Snap Chromium could not read a WebDriver-injected file under `/tmp` (the File object reported size 0); moving the fixture under the browser-readable home directory let the actual Files → Spreadsheet → XLSX export/reopen workflow pass. This was a test sandbox restriction, not evidence of a production upload failure. Local registered-account tests passed desktop and phone-sized open/CSV import/invalid-file recovery/sync/fresh-session workflows, phone-sized save overwrite cancellation plus file changes during confirmation and during the write, 4K XLSX overwrite cancellation/stale-write protection, and a desktop upload/export/reopen workflow. The following live receipt records deployment and public-account checks; physical touch and the rest of Spreadsheet’s app review remain. Relevant tests: `tests/spreadsheet-open-safety.test.mjs`, `tests/spreadsheet-native-save-race.test.mjs`, `tests/spreadsheet-xlsx-snapshot.test.mjs`, and `tests/spreadsheet-browser.test.mjs`.


### Spreadsheet dialogs and Files upload — live, 2026-10-31

Static release `91d6e984f6a23f681da7fce41f90a501eca2c99c0bf51eaee21f24a46fc9528c` follows `2be54aa8d118cc1d61b1f0c7ff2000ddc0f8bb0dabbddef9d85f05dadfd3dd3f`. It updates only the app catalog and the Files/Spreadsheet bundles in the 5,578-file immutable release. Files bundle `f8a16f3e35d1851355c21c557d951994d6f8b1b649d636ee4d156fb1c1045447`; Spreadsheet bundle `0197bfceacfb06433e8af4c10359fd33fd89bdc23c0e590fcb3332be81992b94`. The shared themed dialogs now cover Spreadsheet open-over-unsaved-work and native, XLSX and CSV replacement. After an answer, the app checks the account and file version again before replacing; cancellation retains the workbook. Files upload keeps selected browser `File` objects alive until the storage write finishes, then clears the input.

Local registered-account browser checks passed desktop and phone-sized open/CSV import/recovery/sync/fresh-session workflows, phone-sized save overwrite cancellation and concurrent changes during confirmation/write, 4K XLSX overwrite and stale-write checks, and desktop Files upload/export/reopen. Public live Chrome checks passed a phone-sized account save with cancel, file change during confirmation, concurrent write protection and server sync; a separate desktop check uploaded an XLSX from the computer into Files, opened it in Spreadsheet, saved a native workbook to My files, exported XLSX and verified the server-synced result. A Snap Chromium attempt could not read a WebDriver-injected fixture in `/tmp`; moving the fixture under the user home directory fixed the test. This was a test harness restriction, not a production upload failure. Two exact disposable accounts were disabled after their My files homes were verified empty; account database integrity and all other account policies were unchanged.

Root, `/desktop/` and `/blog/` return 200. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `deb938fe0637100c89fc48557bc8061aea8b735ab4d87f587b97285f0db5e82a`, Caddy SHA `36be523e24a6442092b7a478973e1b7c63190dabe8ca1cbbc7cbaa402843b619`. Rollback snapshots: `/var/backups/webhost-sites/change-20261031T224956957675Z` and `/var/backups/webhost-sites/change-20261031T224956958215Z`. Physical touch remains unverified, and Spreadsheet’s broader app review is still in progress.

### Browser themed save dialogs — local candidate, deprioritized

Browser's clicked-download filename prompt, existing-file replacement confirmation and reset warning now use the desktop dialog service. Replacement rechecks the selected account and file version after the user answers, avoiding a stale overwrite. The save-target unit tests pass, and an isolated real Browser engine workflow passes at desktop, emulated-phone and 4K sizes, including cancel, replacement, concurrent-change refusal, account sync and reset without native browser dialogs. The user has since placed Browser below engineering, simulation, game and file-type app work. This candidate remains local and is not deployed. The temporary Browser bundle and test profile were removed after the run; current user Chrome cache and other active previews were preserved. See `apps/system/browser/docs/TEST_STATUS.md`.


### Browser launcher marked in development — live, 2026-10-31

Live static release `ec2a5de896b0bfcfde030009e90402effbb100270faf2c110bccc4ccce1eb4d9` follows `91d6e984f6a23f681da7fce41f90a501eca2c99c0bf51eaee21f24a46fc9528c`. Only `app.js` and `style.css` changed: the Applications entry now reads “Browser (in development),” is disabled, and remains gray on hover. The Gecko bundle and relay are still present; no Browser code or service was removed or deployed in this release. The local themed download-dialog candidate remains unshipped. Live manifest SHA `2111631f5392908cd5a9708d5e86b2bc0a471ba4dcc2aa8aa0168001116f7338`, Caddy SHA `66a9e2395fd8540052df63f162c268465e31a53b5182bbada17b5b429247738c`; rollback snapshots `/var/backups/webhost-sites/change-20261031T231537405588Z` and `/var/backups/webhost-sites/change-20261031T231537406088Z`. Root, `/desktop/`, and `/blog/` return 200. The served app source and CSS were checked; no account or user file was touched for this menu-only change.


### Audio Editor File menu — live, 2026-11-01 UTC

Static release `859caf0f2820d451752a6f213c7c5de4597a5f2c295813cb18efc2a9333ea9af` follows `ec2a5de896b0bfcfde030009e90402effbb100270faf2c110bccc4ccce1eb4d9` and changes only the catalog and Audio Editor bundle `da930607de6efd6378bd0d96d258379c3df3f15c0bd3bd318408e90151c36e1e`. File operations are in AudioMass's File menu; 44 px targets support phone-sized views and the automatic vendor welcome is suppressed. A fallback toolbar remains when its menu cannot be found. The prepare script now preserves the WAV worker entry; a fresh preparation and browser save tests verified the packaged worker.

Local desktop, phone-sized and 4K menu workflows and desktop/phone account, microphone and audio tools regressions passed; local >32 MiB save and missing-menu fallback passed. Public registered-account desktop and emulated-phone menu tests passed cancellation, concurrent-change protection, Save As, sync and reopen; phone menu uses emulated taps. Both disposable test accounts were disabled after their server folders were verified empty. A prior test failed because it did not answer the new themed dialog; its corrected rerun passed. Physical phone touch and full effect coverage remain unverified. Root, /desktop/ and /blog/ return 200; issuer, guest, files and Caddy services are active.

Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `cf95709da41c8514215fb69af464306d7c7e60638f0cdba6c789d05686b7abfc`, Caddy SHA `cdbba40303254c765fa4b404cd09ba5302000a03c508843a0c1d88dcce90eb7c`; rollback snapshots `/var/backups/webhost-sites/change-20261101T004938211526Z` and `/var/backups/webhost-sites/change-20261101T004938211935Z`.


### diagrams.net File menu — live, 2026-11-01 UTC

Static release `86f7fbc0e7c9610d641b96f0e0afa9f5f3ccb9f39599f4a42b065d3065058bb2` follows `859caf0f2820d451752a6f213c7c5de4597a5f2c295813cb18efc2a9333ea9af` and changes only the app catalog and diagrams.net bundle `db7b35aec8ea50d0eb53ff8bdd1797143ea831c43c0cb6593a4a5550f54de9ae`. The My files actions are in the editor File menu, with fallback controls if the upstream menu is unavailable. The new actions handle mouse and touch pointer interception, support keyboard activation, and have 44 px minimum targets.

Local desktop mouse, emulated-phone tap, keyboard and 4K account workflows passed, as did a local save snapshot/conflict regression. Earlier tests called DOM click directly and missed upstream pointer interception; actual mouse and emulated-tap checks exposed the problem and passed after correction. Public desktop mouse and emulated-phone tap account workflows passed editing, invalid-file recovery, upload, save, fresh-session reopen, fallback and no external requests. Both disposable accounts were disabled after their server folders were verified empty. Physical phone gestures and behavior after a diagrams.net vendor update remain unverified. Root, /desktop/ and /blog/ return 200; issuer, guest, files and Caddy services are active.

Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `073437d38af2f2cc4fb7c6b0344d768aa5f0ee3638a6e0e0d1f5c4e3062e9756`, Caddy SHA `2178f6a46212764cf8878df6e73e00e43aaccab2d088fddc98355c3ecbd3d8d9`; rollback snapshots `/var/backups/webhost-sites/change-20261101T005843215872Z` and `/var/backups/webhost-sites/change-20261101T005843216614Z`.


### SVG Editor File menu — live, 2026-11-01 UTC

Static release `8116f42affd3fb89e936830c5c77c0df6a2c76920e303c0f973eb795c8fdb36b` follows `86f7fbc0e7c9610d641b96f0e0afa9f5f3ccb9f39599f4a42b065d3065058bb2` and changes only the app catalog and SVG Editor bundle `2586c9b78247f1a452af0e35fb30637978d6cc8aaa0046af54eee3a37be400e5`. Open, example, save and export actions use the embedded SVG-Edit menu and have 44 px targets; fallback controls appear if the editor menu cannot be connected. PNG/JPEG/WebP and raster PDF export save to My files, with size and overwrite checks. PDF is not vector-editable.

Local desktop, emulated-phone and 4K registered-account workflows passed keyboard/menu activation, SVG editing, image and PDF export, sync, reopen and fallback. A separate save snapshot/conflict test passed including opening the saved SVG in Stitch Converter; its first attempt lacked Stitch Converter in the isolated preview and was rerun with it included. Public desktop and emulated-phone account checks passed the example, editing, save, image/PDF export, sync, fresh-session reopen and fallback; phone File-menu actions used emulated taps. The two disposable accounts were disabled after their server homes were confirmed empty. Physical phone touch, complex artwork, full format fidelity and all upstream features remain unverified. Root, /desktop/ and /blog/ return 200; issuer, guest, files and Caddy services are active.

Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `81091340371528b52471b7360c33357b984dbacc18a07a33c365a5e6b5dd8b39`, Caddy SHA `921a8fd8ab3500b517546df34020f7f3dda50048149f7b7ef787e6ee25bd7952`; rollback snapshots `/var/backups/webhost-sites/change-20261101T010234832307Z` and `/var/backups/webhost-sites/change-20261101T010234832719Z`.


### Electronics Design submenu — live, 2026-11-01 UTC

Static release `d1342bd85bc6fcf7f01871fc350509ad786f854caeeeff57ed7f661a8cea597c` follows `8116f42affd3fb89e936830c5c77c0df6a2c76920e303c0f973eb795c8fdb36b` and changes only the app catalog and Electronics Design bundle `9435dc41786f184c58c98640dda37f7416275b8e7b628b8a34499113d64e3b6a`. The duplicate host file row is removed and the app File menu uses My files. A source patch gives the visible submenu priority when it overlaps its parent, fixing an emulated-phone tap that previously selected a covered parent item.

The isolated box-git rebuild uses pinned designElectronics, SDL, SDL_ttf and nested submodule revisions; the six patched source hashes matched the local prepared source. Its JS SHA-256 is `8970e5070019ff4d9d82897d9d82554582815e7729b19dae4c0cb7dfd19ce7d5`, WASM `ad97043a7e58f0d17bf8607187b38c131e4e760714cb1616448854e9939cf631`, data `b47f7a58ff1e8768885267b349018d60932c535938a301c0f3b6a2b0c5f8a7ed`. Local real canvas desktop mouse and emulated-phone tap open/save tests passed; account workflows passed at desktop and phone size, and a 4K shared-view account test passed. An initial 4K test used the removed wrapper button, and its first adapted attempt sent a message from the wrong frame; the corrected test passed. Public desktop mouse and emulated-phone tap File-menu open/save and sync passed without external requests. Both test accounts were disabled after empty homes were confirmed. Physical touch, other editor tools, a full network audit and hardware validation remain open. Root, /desktop/ and /blog/ return 200; issuer, guest, files and Caddy services are active.

Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `48d19254a04435230fb080573a66c0c240b23370ab92b46e73460da60f2c65aa`, Caddy SHA `afba54ff40526b9fbf906cef83c44ddccb55844846258516352bc77e600dcb64`; rollback snapshots `/var/backups/webhost-sites/change-20261101T012358387312Z` and `/var/backups/webhost-sites/change-20261101T012358387801Z`.


### Circuit Simulator File menu — live, 2026-11-01 UTC

Static release `d08d4d27b7c8904b63d32d8ca3505ac8c7260e236a2e8e55fd7fae4fa4e5f10d` follows `d1342bd85bc6fcf7f01871fc350509ad786f854caeeeff57ed7f661a8cea597c` through intermediate `19624bc9a4e38eea4a949344e5b911ec7dedc7d1bd08cec86d562d889386dfcc`. It updates only the app catalog and Circuit Simulator bundle `5b931edcc20233857c07160698d504266d5f3f316cca08f8f1d91fd312dea23d`. Open, save, three examples and PNG/SVG exports use the simulator File menu and My files, with fallback controls if its menu cannot be identified. First save asks for a path. Dropbox File-menu, command-palette and startup-import paths were removed; other upstream dialogs and network actions remain to be audited. Desktop dialogs protect replacement and detect changes while confirmation is open.

Local desktop, emulated-phone and 4K tests covered menu open/save, examples, PNG/SVG signatures, sync, replacement cancellation and changed-target protection. Local account tests covered a 5 V divider, upload, invalid-file recovery, fresh-session reopen, conflict handling and lifecycle; one initial test preview lacked Stitch Converter for an unrelated SVG test and was corrected separately. A PNG export initially failed because CSP blocked fetching a data URL; chunked local decoding fixed it. Public desktop and emulated-phone account tests passed native-menu open/save, image exports, examples, cancellation, conflict protection and sync on the intermediate release. The final release differs only in the corresponding-source archive documentation; its public phone-sized workflow and authenticated ZIP fetch passed. Three disposable account homes were verified empty and their accounts disabled. Physical phone touch, broad circuit fidelity and other upstream integrations remain unverified.

Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest SHA `b72277e55290b63ebcdd6f1092fbb1c3723bc696e83a82048439c91ec3ccac16`, Caddy SHA `265965be0aee3cfcf50d1b947810549d1969964d48a0b142af9656a1b93f00e0`; final rollout rollback snapshots `/var/backups/webhost-sites/change-20261101T014223983216Z` and `/var/backups/webhost-sites/change-20261101T014223983640Z`.


## Python Notebook desktop discard dialogs — 2026-11-01 UTC

Static release `884c4505b8db4806480450e447c340cd132bbe22c9763d7838db600a39dc428f` updates the Notebook bundle and app catalog. Notebook open/discard confirmations use desktop dialogs, and an edit during a confirmation aborts the open instead of discarding the newer edit. Registered-account desktop, emulated-phone and 4K-sized tests passed cancellation, the edit race, the Python example, sync and fresh-session recovery. A public emulated-phone account workflow passed and its disposable account was disabled after its server home was verified empty. Physical touch remains unverified; Jupyter's outer file toolbar still needs native-menu integration. The bundled source README was generated before activation and describes this dialog update as local; the current repository corrects that stale release wording.

Hosting manifest `590693b049b7839a666c62f45c114ed8c65b18e9f24035a3286295b0dea22ceb`, Caddy `b3232697f6ab32672bbc00d90206e81d48dfc6f510f11c455af2a5ee912afaa1`; rollback inputs `/var/backups/webhost-sites/change-20261101T015058867393Z` and `/var/backups/webhost-sites/change-20261101T015058867813Z`.


## Python Notebook File menu — 2026-11-01 UTC

Static release `0129c55ec30be2e884e2e49bf709caf2e5b74feaba2095e250789b844c76806d` updates Notebook bundle `22e26ebf65253a30984dfb09c8998113b28f9a92cf7718b6427f21345a731a8c` and the catalog. My files open and save and the Linux Terminal launcher are in Jupyter's File menu. Its native save actions still address temporary Jupyter working copies; the guide explains the distinction. The old toolbar appears if the menu lookup fails. Desktop, emulated-phone and 4K-sized account tests cover save, existing-file refusal, sync, cancellation, reopen and command cleanup. A phone tap initially failed to activate Jupyter's inserted menu item; the touch bridge passed the retest. Simulated unavailable-menu desktop/phone tests saved and synced via fallback, and two notebook windows saved independently. A public phone-sized account workflow passed and its disposable account was disabled after its server home was verified empty. Physical touch and compatibility with later Jupyter versions remain unverified.

Hosting manifest `e01c6acb7b4783a1dd49fa5899ecf9d29051ac76e74cdb90290e49b479081e9e`, Caddy `4f5917759759b3ceb27f8bfe69428f322e0fe7f2169a563374fc2fd0aee106c0`; rollback inputs `/var/backups/webhost-sites/change-20261101T020021335609Z` and `/var/backups/webhost-sites/change-20261101T020021336022Z`.


## Fabrication replacement dialogs — 2026-11-01 UTC

Static release `8b51a0bc7fc207cda03c5c0f43ca4137860cd0f3d109b896de4933babaf502ab` updates Grid Tools bundle `eda6af7973120553e563804889f64f364c1f657e49f0e28fa87e924fb9039626` and the catalog. Workspace open, workspace replacement and export replacement use desktop dialogs. A workspace edit during confirmation prevents replacement; the comparison ignores camera motion and Kiri's automatic save timestamp. Actual desktop and phone-sized Kiri and Mesh project workflows passed locally, including cancellation, changed settings, sync and reopening; desktop/phone/4K export replacement checks covered cancellation and changed targets. An initial phone Kiri run falsely detected camera changes and another detected an automatic save timestamp; both were excluded from the comparison and the rerun passed. A public phone-sized simulated export test passed cancellation and concurrent target change. The test files were removed and the disposable account was disabled. Physical touch, other upstream dialogs, broader snapshot fidelity and native-menu integration remain open.

Hosting manifest `502285ace3c72ef81c19287a1f2307a4650aa47c14861f1fd7c3b923f2a40d1b`, Caddy `72606b3a950bd81645931d2b4fb433a0f27fc23bbb3234caea674c044ee380c3`; rollback inputs `/var/backups/webhost-sites/change-20261101T020852791479Z` and `/var/backups/webhost-sites/change-20261101T020852792269Z`.


## Arduino Simulator replacement dialogs — 2026-11-01 UTC

Static release `f8b1269fb67ffe691faba3321b16301d8eb58a38fa419934c9fc9dadb887d4c0` updates Arduino Simulator bundle `7440e9789f48eb5d840a070571db88c186330b6e9427a3e6f222a391a2475e44` and the catalog. Firmware, example source and serial-output replacement use desktop dialogs. Desktop, emulated-phone and 4K local account tests covered cancelling and changing each target during confirmation. Full local example/source/serial/GPIO, sync and Text-reopen workflows passed. The first source reopen attempt lacked the CodeMirror shared tool in the isolated preview; a complete preview passed. A separate first upload attempt used a path inaccessible to Snap Chromium; the fixture now uses a browser-readable home directory and the rerun passed. Public phone-sized collision and cancellation checks passed; the disposable account was disabled after its home was verified empty. Physical touch and hardware behavior remain unverified.

Hosting manifest `6c7e31986f8ed5cae70d628c7338b76b075169324e1e594391b3c4b079baaeb7`, Caddy `0a8dab612e490f44cee10cb1d6b7eede47296ba5336603ae5f3fa7eeceb3c4a6`; rollback inputs `/var/backups/webhost-sites/change-20261101T021344657930Z` and `/var/backups/webhost-sites/change-20261101T021344658350Z`.


## Replicad CAD replacement dialogs — 2026-11-01 UTC

Static release `d949833fdce471aa2e6044e36a4f5488dd8ea18b1c8b4afe93cd1ed55d05163a` updates Replicad bundle `49cc2fc0a03beb93006002fe785838069d54fbb2ac848d205a33cb4e5ac05828` and the catalog. Opening over unsaved parameters and replacing project/model files use desktop dialogs. Desktop, phone-sized and 4K local tests covered cancellation and edits or file changes during confirmation. A local real STL geometry, sync, conflict and fresh-session workflow passed; a public phone-sized dialog test passed and its disposable account was disabled after verifying its server home empty. Physical touch and hardware fabrication remain unverified.

Hosting manifest `b6b3469fefbfbb48d557ad8deff65770b2663ea1178951419b95534fb145cc77`, Caddy `ab63ee2a3f7e3be790a7df80b78bc128a02cc791b0a71e3e532f89e4912cb927`; rollback inputs `/var/backups/webhost-sites/change-20261101T021615227276Z` and `/var/backups/webhost-sites/change-20261101T021615227687Z`.


## Pico Simulator desktop confirmations — 2026-11-01 UTC

Static release `6abaf09acee10596bf4aa5bd1f88b3c8641b68fec2201944fc9a22a1a1e53ab3` updates Pico Simulator bundle `d89857ccb10448410b3c44a0cd72297de5493cf31aecb1a29b6f6b09737322ac` and the catalog. Board replacement, simulated-flash reset, project replacement and serial-output replacement use desktop dialogs. A board change during confirmation aborts the action; version checks prevent overwriting a file changed during confirmation. Local desktop, phone-sized and 4K checks used synthetic firmware and a fake worker for cancellation, changed-board and changed-file cases. Desktop and phone-sized serial sync, Text reopen and cleanup passed; a separate phone-sized test ran the real Blink worker. Public phone-sized checks passed the synthetic confirmation workflow and real Blink worker. Both disposable accounts were disabled after their homes were verified empty or absent. Actual phone touch and physical hardware remain unverified.

Hosting manifest `255dd1d6f5115344a0d6bff9ab7147ccca19c5bb0610597539445460cd92625d`, Caddy `d771736ad8dabc019e32e92b9f80bed3cf7cfedc205f8f8b726143d5ce4d3172`; rollback inputs `/var/backups/webhost-sites/change-20261101T023855059453Z` and `/var/backups/webhost-sites/change-20261101T023855065407Z`.

## 2026-11-01 — Data Explorer TSV and offline folder research

Live static release `02f54a8c560d6b181ce8b6735d0aa0e7bcd36e023202cc03bb34eb6c64c3667f`, replacing `c07254868618fd4a63983327a566356137fbdaf4462f2d89462b4ea467b8d052`, adds CSV/TSV selection, analysis and project restore. Local desktop and emulated-phone and live emulated-phone registered-account tests cover quoted tabs and commas, real DuckDB SQL, sync, fresh-session reopen and changed-source warning; the live test account was disabled. CSV example and source-watch regressions passed locally. Physical touch and large TSV files remain unverified. Hosting generator SHA `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`; manifest `65c5ce666e6a0377d36362854ed6ffa303a158444f364d5a54b7c86f14160b98`; Caddy `59b918c3219050dfd2b1de92b3366d9e951e861f6dae7a51e179a083566b262f`; rollback backups `/var/backups/webhost-sites/change-20261101T061642159344Z` and `/var/backups/webhost-sites/change-20261101T061642159789Z`.

Folder moves remain unavailable. An unrouted server-only experiment has a provisional 4 GiB aggregate hashing limit and local operator inspection and confirmed orphan-marker cleanup; recovery tests include process interruption and overlapping folder moves. It is not ready to enable: see `docs/FOLDER_MOVE_DESIGN.md` for unimplemented cancellation, host-writer quiescence, lock-held performance, browser sync, backup and review requirements.

## 2026-11-01 — Notebook, Arduino, G-code and Files handoff

Live static release `fbb906a284e4072b8704dbffc41eb6eadba360057ac7bc4da68d6aaa99262e96`, replacing `02f54a8c560d6b181ce8b6735d0aa0e7bcd36e023202cc03bb34eb6c64c3667f`. Files opens CSV and TSV in Data Explorer; local desktop and phone-sized and live phone-sized tests checked actual Files selection and parsed TSV values. Notebook uses a close guard during pending saves, including clean manual saves; local desktop/phone and live phone tests covered cancellation, edits during a held write, follow-up sync and injected failure. Arduino status remains visible during scroll and has a status role; local desktop/phone and live phone tests covered real firmware, serial, server sync, fresh-session recovery and independent windows. G-code Preview accepts `.g`, `.gc`, `.ngc`, and `.tap` inside the app; local desktop/phone and live phone tests cover account reopening and conservative rejection of unsupported commands. These are emulated phone tests, not physical touch or hardware validation. Four uniquely identified live test accounts were disabled.

Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `785b59db883f4192d2d0454a1dc172f1f3d506386aed1d15434f6d4d0e48e1a8`, Caddy `038994dfd54befb74cd8f655a7cd588e12e2dc5211ba3fe5e891f1acba8143cb`; rollback backups `/var/backups/webhost-sites/change-20261101T062239082368Z` and `/var/backups/webhost-sites/change-20261101T062239082791Z`.

## 2026-11-01 — Files text handoff and app reliability

Live static release `39a1c8053f6d266e600503050cbb8b217ce660a036a888ea7fd025031d95c129`, replacing `fbb906a284e4072b8704dbffc41eb6eadba360057ac7bc4da68d6aaa99262e96`. Files offers account files Open in Text; a CSV edited and synced in Text reopened with updated values in Data Explorer in local desktop/phone and public phone-sized tests. Spreadsheet blocks overlapping open pickers; desktop/phone and live phone checks used a delayed picker and account sync/reopen, with a separate real picker import test locally. Digital Logic labels a stale running diagram; desktop/phone full workflow and focused live phone checks cover successful and failed Run and truth tables. Grid.Space checks filenames against the exported format while retaining an export on rejection; desktop/phone and live phone tests used actual Mesh STL and Kiri G-code, synced and reopened. The check is not content or machine-safety validation. Phone tests used emulation; four uniquely identified live accounts were disabled.

Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `fdb02538e955c99152df5ee6744f5b0aaeb3677070aa6ec9dc7ee6ea8d032e3d`, Caddy `55c4ae5db5e15e4134283d2c75d837b4c9744fd73dcc783908386e8a9fd04027`; rollback backups `/var/backups/webhost-sites/change-20261101T062727932846Z` and `/var/backups/webhost-sites/change-20261101T062727933263Z`.

## 2026-11-01 — Upload replacement, document notices and simulation recovery

Live static release `5ffef0e6907ec08f2b5b0610e3ed2a60c5b2fb36fe44e28b44b4acb51604c3d8`, replacing `39a1c8053f6d266e600503050cbb8b217ce660a036a888ea7fd025031d95c129`. Files now offers Skip or version-checked Replace for account uploads; local desktop/phone and live phone-sized tests cover skip, intervening modification and successful server sync, and the local upload location-binding regression passes. Document Editor orders file-change checks and rechecks after operations; delayed-response and held-save tests passed locally at desktop/phone and live at phone size. Arduino warns before discarding unsaved serial on firmware replacement or window close; real AVR local desktop/phone and live phone checks cover cancellation and saving. Reload still does not preserve serial. Pico marks flash uncertain after a firmware worker failure, preventing stale snapshot save/restart until recovery; desktop/phone local and live phone account tests used synthetic firmware and an injected crash, and separate local real Blink tests passed. Lost flash changes cannot be recovered. Physical touch, physical hardware and real emulator crash behavior remain unverified. Four uniquely identified live test accounts were disabled.

Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `a8df967eca331204a0b1d27d40eadb56219ee07201318fd6019e5076f97a1729`, Caddy `1950eba0241ad8c9f6036a67c4989dedf77d2af5977aa786a16408e689dcebfa`; rollback backups `/var/backups/webhost-sites/change-20261101T063329234915Z` and `/var/backups/webhost-sites/change-20261101T063329235339Z`.

## 2026-11-01 — Diagram exports and app review integration

Live release `d28af034a752ab15ba9844a027b1923ce892940c8b5fdd8626cbc6c848d5a69a`, replacing `5ffef0e6907ec08f2b5b0610e3ed2a60c5b2fb36fe44e28b44b4acb51604c3d8`. diagrams.net redirects its local export API to My files; actual SVG/PNG export, cancellation, stale-target protection and server sync passed local desktop/phone and live phone-sized testing. Other formats and physical touch remain unverified. Text rechecks after open/reload; local desktop/phone and live phone delayed-read tests covered changed-file notice, save copy and sync. CircuitJS guards New Blank and library replacement and clears the old file association; local desktop/phone and live phone checks covered cancellation, save/reopen and sync, with separate final-source menu/export regression locally. Corresponding-source archive SHA-256 `71159e974fc7ee3a27cf1811d9761aea7b9f9068d44b754e9f8fd2387e12edac`; other upstream import/recovery paths remain unreviewed. Digital Logic incorporates contributor branch `app-review/digital-logic` (`abe8507b6`) naming insight with legacy `.json` in-place saves preserved; local desktop/phone and live phone tests cover save, sync and Files-compatible reopen. Contributor review retained as a historical document. Excalidraw hides unintegrated library entry points and records deferred features; local desktop/phone and live phone tested drawing and sync with no third-party requests observed in the tested flows. Hiding UI is not a network security boundary; broader provider audit remains. Five uniquely identified live test accounts were disabled.

Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `b452858723b361f85e279b4f2769cd7554b442127216522a2fa9b8335892ac5c`, Caddy `f2673c648d6e5d36d79a4ca5be7f09ac1bdb979d3665a9e0afbe53a504af0e18`; rollback backups `/var/backups/webhost-sites/change-20261101T064634432601Z` and `/var/backups/webhost-sites/change-20261101T064634433374Z`.

## 2026-11-01 — Four game previews integrated

Live release `9b70b08178d92db0dac97f73ffc5c54e70feac54a593c8f1468a01e72173d854`, replacing `d28af034a752ab15ba9844a027b1923ce892940c8b5fdd8626cbc6c848d5a69a`. Falling Blocks has a two-line tutorial and per-window synthesized audio, muted by default. A live phone-sized browser test enabled, muted and closed a real AudioContext; local tests covered independent audio contexts, model, account sync, conflicts and focus. Owl Companion, Physics Playground and Snake Garden are added as previews. Local desktop/phone tests covered save/close races, stale opens, account sync/isolation, lifecycle and focus pause; live account tests covered save, paused reopen, sync and isolation. Each pauses when its desktop window loses focus. Owl/Snake use labeled procedural placeholders; authored Rive art is absent. Physics XR, full challenge/acceptance, physical touch and audible speakers remain unverified. Physics is a simulation. Nine uniquely identified live test accounts were disabled (one audio test first used an incorrect test selector and was rerun successfully). Owl includes the MIT Rive notice for the bundled WASM. The final tracked Falling Blocks coach runtime has SHA-256 `f1719c678e0b78b2c29f063d07872b301ff4cc577f819db3d13860424a6bd707`.

The live desktop app.js also now matches the tested source desktop title metrics (30px title bar; phone remains 48px), replacing the previous live 44px desktop values. Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `1838bf3aeebc51088a12a7a24d0af1c2acec8753b3e900de72ff74543584fc38`, Caddy `2de5ab82258ea4f52818553c8d8031bcc2ee120f3c8b917cb07b75e80fdc64c3`; rollback backups `/var/backups/webhost-sites/change-20261101T065711923522Z` and `/var/backups/webhost-sites/change-20261101T065711924673Z`.

## 2026-11-01 — Scoped static-release cleanup

Under the hosting-controller lock, verified the manifest ID and exact file set,
rejected symlinks, and checked the hosting manifest and Caddy configurations
before removing unreferenced releases `02f54a8c560d6b181ce8b6735d0aa0e7bcd36e023202cc03bb34eb6c64c3667f`,
`fbb906a284e4072b8704dbffc41eb6eadba360057ac7bc4da68d6aaa99262e96`, and
`39a1c8053f6d266e600503050cbb8b217ce660a036a888ea7fd025031d95c129`.
The active `9b70b08178d92db0dac97f73ffc5c54e70feac54a593c8f1468a01e72173d854`
and recent rollback releases `d28af034a752ab15ba9844a027b1923ce892940c8b5fdd8626cbc6c848d5a69a`
and `5ffef0e6907ec08f2b5b0610e3ed2a60c5b2fb36fe44e28b44b4acb51604c3d8`
were retained. Other historical release directories were not removed in this pass.

## 2026-11-01 — PDF search and electronics restore

Live release `406b901f8bc52427dcb3c8d477008af992d5f33579c6dd00da414604547136cb` replaces `9b70b08178d92db0dac97f73ffc5c54e70feac54a593c8f1468a01e72173d854`. PDF Viewer clears stale search status on page navigation; local desktop/phone and live phone account tests cover pending/completed search, navigation, sync and fresh-session reopening. Electronics Design updates the desktop restore reference after opening or saving and clears it on New; local desktop/phone and live phone tests cover switching projects, refresh, New, sync and retaining the previous server file. The broad account workflow also passed locally. Unsaved work is not recovered after refresh; physical touch remains unverified. Both unique live test accounts were disabled.

Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `f1c29e6d13e254437b8aae40f4e1f34d83cb4ca97d0036932cb8eb46b6725ba7`, Caddy `b82d3434021e6e03fbb9b4c0ca0d5a07cd4339d2dfdaeec141dd04a76431dfad`; rollback backups `/var/backups/webhost-sites/change-20261101T070632692049Z` and `/var/backups/webhost-sites/change-20261101T070632693369Z`.

## 2026-11-01 — Image Editor account-backed overlays

Live release `97a6b241a1fc91823c2e636c27c8264f4f48e2ec8578a5b9b219d922b766090d` replaces `406b901f8bc52427dcb3c8d477008af992d5f33579c6dd00da414604547136cb`. The watermark hook selects from My files; File → Choose annotation image from My files fills a temporary gallery used by Annotate → Image. The separate computer-upload action remains. Desktop and emulated-phone local tests and live emulated-phone tests checked both paths, invalid watermark handling, actual saved pixels, server hash parity and no observed third-party requests in tested flows. The upstream annotation gallery must be dismissed before saving. Physical touch, large overlays and other provider paths remain unverified. Both live test accounts were disabled.

Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `bd31479b6f2bc0ed0a9679582904cbf5894df70496a6801327fdfdd0f9b8e1a5`, Caddy `a453e82aa904c0956c718ffae1964f57c6e7fa8f6950e7fbaac80f48bdc2f0ca`; rollback backups `/var/backups/webhost-sites/change-20261101T071018530671Z` and `/var/backups/webhost-sites/change-20261101T071018532127Z`.

## 2026-11-01 — Spreadsheet open, G-code offset and audio tracks

Live release `0f90d663ff9904555603380fc5a00fa085afa3a5ae6c08be87ba290798217763` replaces `97a6b241a1fc91823c2e636c27c8264f4f48e2ec8578a5b9b219d922b766090d`. Spreadsheet commits an active cell before applying a delayed open; local desktop/phone and live phone account tests cover the delayed-read race, cancellation and sync. G-code Preview rejects M218 hotend-offset commands rather than silently drawing a potentially misleading path; local desktop/phone and live phone tests cover variants, comments, normal heater commands and preserving the prior preview. Audio Editor imports MultiTrack audio from My files, protects an in-flight import from window close, and replaces an unavailable sample link with instructions; local desktop/phone and live phone tests cover decoded WAV tracks, invalid input and the explicit unsupported-save message. MultiTrack session save/export remains unavailable; physical touch, audio output and machine compatibility are unverified. Three unique live test accounts were disabled.

A later private KLU relink receipt was located on box-git. Its retained instrumented WASM hash and marker were checked, and the baseline solver, KLU source/archive and link Makefile match the local research archive; the recorded archive as a whole has a different hash. Runtime execution was reported in that receipt but not rerun here. `docs/evidence/circuit-lab-klu-relink-receipt.json` preserves the claim; Circuit Lab remains unshipped pending the remaining distribution and model-license review.

Hosting generator `fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935`, manifest `84aefe417cb98cb975ab8556130c10d8909ce5ef65aba28b02f9a65294f8accc`, Caddy `7695f30b050346c5f07e7d6117b58cf00a112f36919e125d44be4f6bcc12e82f`; rollback backups `/var/backups/webhost-sites/change-20261101T071657226536Z` and `/var/backups/webhost-sites/change-20261101T071657232515Z`.

## Right rail refinement — 2026-11-01

Live static release `0e62a8a061fd48a26d3ff3948916cd2e38d95ec6e0c3d42a3381d224b2ea4c40` places tasks above the X at the bottom of a dark charcoal rail, retains the light menus, aligns left-opening submenus, and displays larger MM/DD/YY and HH:MM:SS. Desktop, 4K, and emulated phone checks passed locally; desktop and emulated phone checks passed on the live site. Physical phone was not tested. The shell test mocks the guest image and is not a Linux boot test. Root, /desktop/ and /blog/ returned 200. Hosting manifest `712939329d08ea9030dbaa623aa811b2fd9de3826e3ce8c3fa0626dd5e78178a`; rollback inputs `/var/backups/webhost-sites/change-20261101T084011533366Z` and `/var/backups/webhost-sites/change-20261101T084011534150Z`.

## App recovery update — 2026-11-01

Live release `06e26892602f380d632d9b63e35a902ea0f697b384b84d587b256eeb0398d29e` includes Audio Editor invalid restored audio recovery and Data Explorer failed-open recovery and pinned DuckDB worker exception bindings. Local desktop/phone tests and live phone-sized audio and desktop Data Explorer tests passed; physical touch and arbitrary failures remain unverified. Hosting manifest `d3065b2607498cc6a44a65c5aa51a4e4abddf468d819bed33c61492301cba028`; rollback inputs `/var/backups/webhost-sites/change-20261101T084154514270Z` and `/var/backups/webhost-sites/change-20261101T084154514949Z`.

## Responsive launch and app updates — 2026-11-01

Live release `e7beb2cd2553f74f1f4ed7f35a3f5038413c91c5ef3aa4d004e104f77cd8d71e` adds responsive starting window geometry: compact devices use the full work area; ordinary new windows on large CSS viewports use quarter tiles, while engineering apps use wider/taller workspace and Electronics Design can start full width when needed for its three-pane mode. Users can move and resize; saved layouts remain. Local 1080p, 2560×1440, 4K and phone-sized tests and live 4K-sized sizing test passed, including 2560/4K Electronics Design three-pane tests locally. The panes are not independently detachable. Document Editor tested engineering PDF glyphs, Image Editor safe blank-image replacement, and G-code Preview explicit unsupported control-flow rejection passed local desktop/phone and live phone-sized tests. Physical device touch and actual machine execution remain unverified. Manifest `60c2de7dba8603595885ac3c035a1d367691acef55365f00ec0487c2232d25bd`; rollback inputs `/var/backups/webhost-sites/change-20261101T085112816258Z` and `/var/backups/webhost-sites/change-20261101T085112816962Z`.

## Files, spreadsheet and stitching — 2026-11-01

Live release `627a2c47a4965f25c02fa0ccac0f6401e7e53446ed95fb9dbaa013d1f42bf16f`: Files reports the destination and pending sync after copying temporary Linux files into My files; Spreadsheet rejects workbooks whose expanded rectangular grid exceeds 10,000 cells before replacing the current workbook; Stitch Converter saves and restores design size in an SVG comment and marks size changes unsaved. Local desktop and emulated-phone account tests passed; live phone-sized Files real-guest, Spreadsheet and Stitch Converter account tests passed. Physical touch remains unverified; SVG editors may remove size metadata, and sewing-machine compatibility was not tested. Circuit Lab save improvements are source-only and remain gated by the existing distribution/relinking review. Hosting manifest `dc0c879ec0e55fd78cb180cf5339eb72c44a35d4eaee31c8e5f9126856bdba45`; rollback inputs `/var/backups/webhost-sites/change-20261101T085705697830Z` and `/var/backups/webhost-sites/change-20261101T085705698565Z`.

## Files context menu and transfer — 2026-11-01

Live release `2d7298298f6abe5b6f541d06f7fa45cdbe2155c85ecf1ab411edcf34e9dcdd46` removes overlapping blank-space menus, adds Download for one selected file, and accepts external file drops into the current folder through the upload checks. Local desktop and emulated-phone tests cover actual downloaded bytes, stale/conflicting files, menu transitions and account/drive changes; local real v86 test covers downloading a temporary Linux file. Live desktop and phone-sized tests cover menu and download; live desktop CDP file-drop, replacement cancellation, unsupported folder rejection, internal move and drive-change checks pass. Physical OS drag and physical touch are not verified. Dragging outward to Linux remains experimental research, not implemented. Manifest `79904b796067d476396b9fd5fd348a47a0a9b277d77e108f56453762caf1a152`; rollback inputs `/var/backups/webhost-sites/change-20261101T090902918989Z` and `/var/backups/webhost-sites/change-20261101T090902919788Z`.

## Game preview source integration — 2026-11-01

Merged box-git `game-integration/all-previews` (`7a97ced9ec2282e158fe086cce7c5334b59ec6ee`) with the current shell and Files changes. Adds 24 game previews to the four existing games. All 24 passed individual builds and available unit tests; 22 have and passed typechecks. Catalog capacity/registry, menu scrolling and two account-backed game workflows passed in the isolated merge. Gravity Pinball high scores are account-scoped; Gravity Pinball and Tabletop Bot Arena keyboard handling respects focused windows. Combined real full catalog and all individual interactive workflows remain unverified; most final game artwork/audio are placeholders, see `docs/GAME_ASSET_GAPS.md`. Source integration is not yet live. The Python build list has 71 apps; JS builder defaults omit five tools, so use explicit app selection. Legacy native update scripts have smaller limits and are not qualified for this catalog.

## Game previews live — 2026-11-01

Live release `3c17a590c6f716ccef8cddc94dca5c34923561589df1f4e9fd2a5f35aa5c916d` preserves the 47 prior catalog entries and adds 24 game previews (71 apps total, including 28 games). Every new app passed its individual build and available unit tests; 22 passed available type checks. The batch assets were verified by hash and staged with pinned shell/loader inputs; the full real 71-entry catalog was verified. Live account workflows passed for Gravity Pinball and Tabletop Bot Arena, including sync and phone-sized fresh-session reopen; Files context/download/upload regression also passed. A first Pinball live attempt timed out during registration; a retry encountered a detached menu element during shell rerender; a bounded retry in the test then passed. This is not interactive verification of all games. Final art/audio remain placeholders in most previews. Manifest `a437ee928105d79c362a4607d6bd26d0785f1c9e011cfaba0629abc61f61baba`; rollback inputs `/var/backups/webhost-sites/change-20261101T091705025146Z` and `/var/backups/webhost-sites/change-20261101T091705025994Z`.

## APPs launcher label — 2026-11-01

Live release `e9178740fccb767666aac62c64d6e2e3587fac60292ccad87e1a4d318a58cf8a` displays APPs for the Applications launcher, retaining its accessible label. Local desktop/4K/phone-sized and live desktop/phone-sized shell checks passed. Manifest `baa5c9e3482b0ff4bebcbe1ffdc884a5554a51afcfa50cafe57c3d28cdfb7592`; rollback inputs `/var/backups/webhost-sites/change-20261101T092225853732Z` and `/var/backups/webhost-sites/change-20261101T092225854499Z`.

## Solitaire rules and app recovery — 2026-11-01

Live release `ab71505f9cc8bbbf47d9d6a9435afd47868a9af3be77c25f215d8d6ca2fa4ae8` fixes Solitaire tableau source columns, exposed waste, draw/redeal order, face-up tracking, long piles, keyboard destination and save validation. Model tests and local and live desktop/phone-sized account tests cover long-pile pointer/touch, a multi-card run, keyboard movement and saving; no full deal-to-win or physical touch test. Keyboard selection remains limited to top-card tableau moves. Prior release `ae06dce0269dd9a3edea38e5d258e511e1443c5afd813ca32d3a698a4feb1fc1` delivered Text temporary metadata recovery, Story Cards deleted-save protection, and Snake/Owl failed-restore recovery; live phone-sized and account-isolation workflows passed. Manifest `fa44a5cf133430ba32feb8725e77d61db57850933a1cee719ffd6d8d027ef362`; rollback inputs `/var/backups/webhost-sites/change-20261101T092521446090Z` and `/var/backups/webhost-sites/change-20261101T092521446933Z`.

## Chess, rally and report image checks — 2026-11-01

Live release `dc3b433751ca391fee1d20141049742f5ce6915b061b65e1b79a2d2a18303f63` prevents Chess Study moves during the AI turn, fixes pending/completed-turn undo and text-field shortcuts; releases Pocket Rally held inputs on focus loss and composes simultaneous input sources; rejects Document Editor images whose byte signature disagrees with their filename before modifying a report. Local desktop/phone-sized and live account workflows passed, including real local chess AI, phone-sized reopen, Rally sync/reopen/isolation, and PNG/JPEG/WebP report/PDF sync. Physical touch/multitouch, full races and chess AI strength remain unverified. Manifest `fbde9cfa9fcc26b94abc197e2429f813c553903e240baf4f22b5a61b9874cf08`; rollback inputs `/var/backups/webhost-sites/change-20261101T093003317147Z` and `/var/backups/webhost-sites/change-20261101T093003317920Z`.

## Serial, game touch and formula updates — 2026-11-01

Live release `c2e60eff11fe6f0d522ccfb93bd437daf04bba5b180f190f23f0c0ce9f57e36d` adds keyboard-focusable Arduino serial output with Jump to latest, fixes Falling Blocks simultaneous pointer ownership and invalid startup save recovery, and uses conventional mathematical exponent precedence in Spreadsheet. Local desktop/phone tests passed all three; live phone-sized Arduino serial and spreadsheet save/export/sync/reopen passed. Falling Blocks multitouch was tested through CDP locally, not on a physical device. Spreadsheet formulas such as `=-2^2` now yield -4 (unlike Excel); existing calculations may change and the app documents this. Manifest `85aaf2ee13fdb18b5265b514aadb8e8dd2520186b8737a812d728050bcbfa32d`; rollback inputs `/var/backups/webhost-sites/change-20261101T093809015512Z` and `/var/backups/webhost-sites/change-20261101T093809016258Z`.

## App display names — 2026-11-01

Live release `5d84a1c075f347c9eab3b71d83ed8346d7766b3fa8cd0d212fd66ab30103b9e5` uses task-first names with upstream software in parentheses for non-game apps. Menu, taskbar labels, task popup and captions share one presentation map; app IDs, personal app names and saved files remain unchanged. Local and live desktop/phone-sized tests cover all mapped menu labels and representative menu launch/taskbar/title behavior; a live menu click needed a bounded retry after shell rerender detached the element. Physical touch remains unverified. Manifest `78fc8798d407684dcdbc385d5a9dc9fdb65f793848be48abb3235256267e117b`; rollback inputs `/var/backups/webhost-sites/change-20261101T094041768330Z` and `/var/backups/webhost-sites/change-20261101T094041769123Z`.

## Sky Courier, CAD and Audio Editor — 2026-11-01

Live release `a1b2d21b6e1d991c15e687669fe2170485862e90129787f50c91dd4c88acf4bb` corrects Sky Courier held steering and firing input; Replicad clears missing/invalid restore references while preserving references on conflict or temporary read errors; Audio Editor limits Open to one pending chooser and discards stale or post-close choices. Local desktop/phone account workflows passed, as did live phone-sized CAD and Audio tests and a live Sky Courier input check. A single-frame live projectile assertion initially failed; repeated sampling showed brief visible shots, and bounded polling plus a post-release empty check passed. Physical touch, real audio hardware, complete campaign and broad CAD/hardware behavior remain unverified. Manifest `5e44b12b7a26b798a5f958e65fc6b989529ecd4e85591da08ce4c4694eccc0b5`; rollback inputs `/var/backups/webhost-sites/change-20261101T094543212550Z` and `/var/backups/webhost-sites/change-20261101T094543213293Z`.

## Digital Logic, Marble Works and G-code — 2026-11-01

Live release `559fce10976677336ceef80b91420ee13eb6e395c8ec4eaacffc9afa546a4772` preserves Digital Logic restore references on transient errors/conflicts, adds Marble Works pause/resume and prevents competing G-code Open choosers. Local desktop/phone and live account workflow tests passed. Digital Logic truth tables, sync/reopen, Marble Works pause/reopen and G-code chooser/close/reopen were exercised; physical touch, a complete marble campaign and machine safety remain unverified. Manifest `3d91ae388a01eff3daedeb4c902ca42d62defa1e775b592e740234dff567fa4a`; rollback inputs `/var/backups/webhost-sites/change-20261101T095044231758Z` and `/var/backups/webhost-sites/change-20261101T095044232490Z`.

## CircuitJS, Excalidraw and Clockwork Room — 2026-11-01

2026-11-01: Circuit Simulator preserves recoverable restore references during temporary errors and conflicts; Excalidraw prevents overlapping folder choices and file actions; Clockwork Room distinguishes invalid saves from temporary errors and ignores repeated shortcuts. Local and live account workflows passed, including a 5 V to 6.67 V circuit, upload and fresh phone-sized reopen; drawing folder/save/reopen; and all four room mechanisms, sync and recovery. CircuitJS corresponding source matches the integrated source. Tests used desktop and emulated phone; physical touch and electronics hardware remain unverified. Release `29d2fb10136f9304062e01507208fc4e3600b578fa10ff10bfa73d2842bb268b`. Files right-click Download was also checked live against exact binary bytes.

Hosting manifest `5c56437c24a9f3c81e1740b8d8c40aac22dd0c6e388572bc17636c6cdee4b005`; rollback inputs `/var/backups/webhost-sites/change-20261101T095745082380Z` and `/var/backups/webhost-sites/change-20261101T095745083648Z`. The CircuitJS test upload fixture uses the project build directory because Snap Chromium cannot access the test process’s private `/tmp`.

## Calculator, SVG, Stack and engineering recovery — 2026-11-01

2026-11-01: Calculator serializes folder choices with save/open and preserves a changed path; SVG Editor rejects unsupported SMIL animation before opening to avoid silent loss; Stack & Balance cancels interrupted touch gestures and ignores repeated placement shortcuts. Arduino, Replicad, Digital Logic and CircuitJS retain restore references when storage context becomes invalid. Local desktop and emulated-phone account tests passed. Live phone-sized Calculator and SVG tests and desktop/phone-sized Stack gesture, save, sync and reopen tests passed. SVG CSS animation and broader compatibility, full Stack challenges, physical touch and real electronics remain unverified. CircuitJS corresponding-source archive was rebuilt and checked. Live release `df1dcc67c7169791aeb55cc236bee3997a66717de0e4c9c91e805bffb90bc713`. SVG icons returned 503 in concurrent local preview sessions; later local single-session and one/two concurrent live launches passed, so cause and larger-load behavior remain unproven.

Hosting manifest `8f3fe46acc1e7f949fd41a529f1b0cb41da32e4950a6be59463a074428df683f`; rollback inputs `/var/backups/webhost-sites/change-20261101T100457369035Z` and `/var/backups/webhost-sites/change-20261101T100457369843Z`.

## Pico, Crystal Defense and Diagram Editor — 2026-11-01

2026-11-01: Pico Simulator retains project references through temporary storage errors, conflicts and invalid account contexts; confirmed missing or invalid projects clear stale references. Crystal Defense warns when an existing save was deleted and prevents pausing changes during a pending file operation. Diagram Editor validates compressed and uncompressed pages before changing file identity; its embedded editor still lacks a load acknowledgement, so other load failures remain possible. Desktop and emulated-phone account tests passed locally; the Pico account test used synthetic flash and a fake worker, while a separate Blink test used the real emulator. Live phone-sized corrupt diagram/upload/save/reopen and desktop/phone Crystal Defense deletion/busy/close tests passed. Physical devices, arbitrary firmware, the full game and large diagram decompression remain unverified. Live release `e3fc3cf68c9ce927396675e2794c24736c39189caa279d172b3f65a37c968c0d`.

Hosting manifest `670e9a7db82a9cea3b1e35a65e608c1da65baf9e12edf429d97386ce94798506`; rollback inputs `/var/backups/webhost-sites/change-20261101T101238059999Z` and `/var/backups/webhost-sites/change-20261101T101238060692Z`.

## Text and Drone Circuit — 2026-11-01

2026-11-01: Text keeps folder choices tied to their originating Save dialog and blocks Save until the choice finishes; stale results cannot alter a reopened dialog. Drone Circuit combines touch and keyboard inputs, clears held controls on focus loss, and prevents control changes during file operations. Local desktop and emulated-phone account checks passed, including actual first-save sync and touch-input regression. Live phone-sized Text and desktop/phone-sized Drone tests passed, including server sync and reopening. Physical multitouch and full course playthrough remain unverified. Live release `f6e004e427326685087002e1c208341eb7cb5ee6ad2b13fa7eb5ec0ebae113df`.

Hosting manifest `8af7900e36a9503dc205ba93593e9d640fa3e7097572c399cb52f7b13373ee29`; rollback inputs `/var/backups/webhost-sites/change-20261101T101708782252Z` and `/var/backups/webhost-sites/change-20261101T101708782991Z`.

## Diagram load confirmation — 2026-11-01

2026-11-01: Diagram Editor now requires a matching protocol response and successful pinned-editor load before changing file identity. Failure or a missing response locks the window and retains the previous file target. Local desktop and emulated-phone tests covered actual injected failure, delayed and withheld acknowledgement, late messages, closing during load and normal save/reopen; live phone-sized checks passed. The adapter depends on pinned draw.io internals and must be requalified on upgrade. Live release `da1ab48955b0998f5ae98923b4669be0735392d6918c5ab635b45b85b1fbd272`.

Hosting manifest `159f41345ad1edc349aa9fa901674e1a83dc4ccb47e62fb8ef841b50d6010db4`; rollback inputs `/var/backups/webhost-sites/change-20261101T102225496271Z` and `/var/backups/webhost-sites/change-20261101T102225497095Z`.

## Electronics project copy protection — 2026-11-01

2026-11-01: Electronics Design rejects unsupported future project versions and malformed wire or part structures. Actual WASM testing confirmed an unknown part can be silently omitted by its native loader, so every opened project protects its original and requires Save As to a different filename, with an explicit warning that the copy may omit unsupported parts. Local desktop, 4K and emulated-phone account tests, plus a live phone-sized unknown-part/real-editor/sync/reopen test passed. An older desktop-specific test fails when forced into phone mode at canvas selection; dedicated phone tests pass. Complete compatibility needs a native validation API or transactional loader; physical touch and hardware remain unverified. Live release `38942fbc696a40d0f61fb8e839b29b436fa4ec3615eb95cac35e1a157c185f0c`.

Hosting manifest `baa2892e47d003f56d9686278a21a7e8601034e4e190e62eb74ab235631334a7`; rollback inputs `/var/backups/webhost-sites/change-20261101T102606444134Z` and `/var/backups/webhost-sites/change-20261101T102606444911Z`.

## Text, Image Editor and Reactive Control Desk — 2026-11-01

2026-11-01: Text retains a temporarily unavailable restored file and offers Reload while keeping the editor read-only; confirmed invalid/missing files still open an independent blank note. Image Editor retains restore identity after temporary read failure and retries on reload. Reactive Control Desk compares saved and current snapshots so new stability progress remains dirty after a delayed save. Local desktop/emulated-phone account tests and live phone-sized Text/Image and desktop/phone Reactive save/sync/reopen checks passed. Image read errors were injected; physical touch and full game remain unverified. Live release `6fda3ccf7d0f207a8a8a0bf14201e6b9230293ca807d8aeb335e3dbb495bc351`.

Hosting manifest `0c4f4d001a4c8944f4def1dd85f791c89ece60d97147a9aef8e25633896413ea`; rollback inputs `/var/backups/webhost-sites/change-20261101T103023696846Z` and `/var/backups/webhost-sites/change-20261101T103023697610Z`.

## Android Chrome toolbar scroll — 2026-11-01

2026-11-01: Compact Android Chromium pages now offer a small top-level scroll range while keeping the desktop pinned, allowing Chrome an opportunity to collapse its toolbar. Local and live Android-emulated touch tests cover empty-desktop/rail scrolling, independent Text scrolling, save, viewport resize and desktop baseline. A physical S25/Chrome toolbar-collapse and keyboard test remains outstanding; app surfaces can consume swipes. No fullscreen API or button is used. Live release `764d33f3d8a65abdbd191cfe7081bd76d0f3c6a73969cfe89ebddb8f86388f4c`. The local preview launcher now reserves its port before staging to avoid replacing a running preview on a collision; a real-server collision test passed.

Hosting manifest `9976c90081666aae32939551b87e3a236e75b546eee88be5cfbd724bba0849b0`; rollback inputs `/var/backups/webhost-sites/change-20261101T103713574591Z` and `/var/backups/webhost-sites/change-20261101T103713575403Z`.

## PDF, document images, Kiri and Rhythm Garden — 2026-11-01

2026-11-01: PDF Viewer retains temporarily unavailable restore references and offers Reload while clearing confirmed invalid/missing files. Document Editor rejects animated APNG/WebP selected from My files to avoid silent flattening; existing report and clipboard images are outside that check. Kiri:Moto rejects 32-bit geometry overflow/underflow and verifies restored coordinates in a temporary editor; testing covered a cube, not all models or printer output. Rhythm Garden registers one judgment per activation and ignores repeated hit/pause keys. Local desktop/phone tests and live phone PDF, Document and Kiri account workflows plus desktop/phone Rhythm tests passed. A separate Document history test failed before assertions due to a detached DOM node; cause remains unresolved. Physical touch, full game and broad model support remain unverified. Live release `23457e54792a22371cb816df5b7c0d7d61ce25ec987754dcbcf63ef85cc7327c`.

Hosting manifest `a15d54bc27a57ea4abfff32578b42fe018a5fe287c29bbc2c6a2c2f701053c2f`; rollback inputs `/var/backups/webhost-sites/change-20261101T104153472883Z` and `/var/backups/webhost-sites/change-20261101T104153473988Z`.

## Game groups and source organization — 2026-11-01

2026-11-01: All 28 game sources were moved into the four original groups under `apps/games/`; the builder resolves their existing IDs from `apps/games/catalog.json`. The Games menu groups them as Arcade, Physics (XR planned), World (XR planned), and Interactive. All 28 bundles built; 26 available test suites and 24 typechecks passed. Account-backed desktop/phone smoke covered Falling Blocks, Stack & Balance, Clockwork Room, Rhythm Garden and Pocket Golf; Chess Study’s worker ran. Menu tests cover all IDs and phone navigation, locally and live. Bundle hashes changed due to source-path comments; selected Rive/Havok assets were byte-identical. Detailed build evidence is in `GAME_GROUP_MIGRATION_RESULTS.json`. Physical XR and touch remain unverified. Live menu release `19076cc5332e4a2007883a493519bab0a685a13e8b8a6e25b2fc09d0b5188f51` retains existing game bundles. A live menu test initially encountered a detached shell node; a bounded retry for that specific rerender condition passed.

Hosting manifest `f14bc870d00595aee56174e9b004a35bae2a6bd05a672a36bafb74901e73e12c`; rollback inputs `/var/backups/webhost-sites/change-20261101T104544857630Z` and `/var/backups/webhost-sites/change-20261101T104544858341Z`.

## Mesh, document clipboard and Lantern — 2026-11-01

2026-11-01: Mesh:Tool rejects typed-array values that would wrap, overflow or underflow before replacing a project. Document Editor rejects animated or oversized PNGs in pasted HTML with a notice, while tested static-image and text paste remain supported; other clipboard formats and previously saved images are not comprehensively checked. Lantern Leap maintains independent touch and keyboard controls and clears held input on focus loss. Local desktop/phone account tests and live phone-sized Document and Mesh plus desktop/phone Lantern tests passed; physical devices, broad Mesh schemas and full game remain unverified. Spreadsheet native format and CSV are now the priority; XLSX compatibility is optional. An already-tested XLSX literal preservation fix was included, without claiming full Excel compatibility. Live release `9da6c186a70f53f0043d00ac7f9b1c053b4bcc6c92cda6d666fbbdf2161c801e`.

Hosting manifest `5659ed330830812a79733d0a6d711f04dd160555e6eaa2d99a7c7a00ea658cc1`; rollback inputs `/var/backups/webhost-sites/change-20261101T105442944815Z` and `/var/backups/webhost-sites/change-20261101T105442945482Z`.

## Spreadsheet, G-code and Garden — 2026-11-01

2026-11-01: Spreadsheet now marks row/column moves, sort, undo and redo unsaved, preventing silent loss on close. G-code Viewer rejects Marlin M290/M293/M294 babystepping, which can move an axis without appearing in its tracked position; this is not complete machine validation. Garden Defense restores its actual map selection after cancellation and keeps a newer destination typed while a save is pending. Local desktop/phone and live phone-sized Spreadsheet and G-code, plus desktop/phone Garden account checks passed, including native save/sync/reopen. Spreadsheet grid operations were invoked through the real API, not physical drag. Physical touch, full game and real machine operation remain unverified. Live release `aeb5c5b8852bbad8b8c29cda3632e1713c03aaed39d230eb39fa3156aa3b36a0`.

Hosting manifest `e8fc34599aba98bc27487b9a81d82b5dcd5d0edceee9cd762027b8f4865116b1`; rollback inputs `/var/backups/webhost-sites/change-20261101T105845632550Z` and `/var/backups/webhost-sites/change-20261101T105845633358Z`. Two obsolete generated releases `764d33f3...` and `23457e54...` were removed to free space; historical rollback notes naming them no longer imply those artifacts are retained. Current release and immediate rollback `9da6c186...` remain.

## Audio, Digital Logic and Sling — 2026-11-01

2026-11-01: Audio Editor resets a stale load-failure flag before loading a new tone, so the result remains marked unsaved. Digital Logic rejects invalid or excessively large propagation delays (0–1024 integer ticks); this is a simulator bound, not a hardware timing claim. Sling Targets tracks unsaved settings, cancels interrupted aiming, and keeps a newer save destination during a delayed save. Local desktop/phone account workflows passed; live phone-sized Audio and Digital Logic and desktop/phone Sling checks passed. Audio failure was injected; physical devices and broad failure paths remain unverified. Live release `0f6ede882282925cb05ee76bec81bfa338fa88d31e98e8794dec362336599fc7`.

Hosting manifest `76938e1ed9d79e792438799034fff799ee0c46ea7af04b2a02bfb1f8a672d9eb`; rollback inputs `/var/backups/webhost-sites/change-20261101T110335631572Z` and `/var/backups/webhost-sites/change-20261101T110335632286Z`.

## Document retry, Stitch and Kinetic — 2026-11-01

2026-11-01: Document Editor retains its restored file and offers Retry after an initial read error; scratch edits are confirmed before retry, and saving a separate report changes the restore target safely. Stitch Converter keeps restored references after transient failures and exposes warnings for unsupported-only SVG artwork; unsupported artwork cannot be exported as stitches. Kinetic Relay marks physics Step dirty, blocks controls during file operations and refuses to recreate a deleted save. Local desktop/phone account checks passed; live phone-sized Document and Stitch checks and desktop/phone Kinetic save/sync/reopen checks passed. Read failures were injected; physical sewing, touch and full puzzle coverage remain unverified. Live release `cc0ce123dc3dee23da9f279107b286c40c3f01dbed6f2a297d5f93f9f9ecb4c5`.

Hosting manifest `d26fdc36331a73e5d21a2c3fda7959fa4a9b4f23345bc2802c6919979c027767`; rollback inputs `/var/backups/webhost-sites/change-20261101T110822747836Z` and `/var/backups/webhost-sites/change-20261101T110822748964Z`.

## Date, voice, launch feedback and app recovery — 2026-11-01

2026-11-01: The app bar now shows the date; selecting it opens a clock with seconds. Routine Opened-app toasts were removed, while useful feedback remains. Voice overlay is hidden by default on desktop and phone, keyboard input starts enabled, and Voice input remains available from System Tools. Text checks server sync before declaring an uncached restored file missing; Replicad rejects unknown project fields; Tabletop Bot Arena isolates overlapping inputs and guards file operations. Local and live desktop/phone-sized checks passed, including menu toggles and date dismissal, injected Text cache failures, Replicad sync/reopen and game input/save. One concurrent launch/voice test timed out at a second sign-in and passed when rerun separately. The phone fullscreen scroll was confirmed working by the user; physical touch and full game remain unverified. Live release `f53dbb9fe32005e43322085b6d7076faa74b5732642f050693c1ff51f9333df9`.

Hosting manifest `2a7fc0aba0c91f2946d428414fe25cf08acb48a843852d7fb521fa9ca2378115`; rollback inputs `/var/backups/webhost-sites/change-20261101T111438812015Z` and `/var/backups/webhost-sites/change-20261101T111438812854Z`. Obsolete generated releases `e3fc3cf6...` and `f6e004e4...` were removed to free disk; historical rollback notes referencing those artifacts no longer imply they are retained.

## Fabrication feedback, Arduino, Excalidraw and Golf — 2026-11-01

2026-11-01: Grid.Space export errors now appear in the desktop status area instead of a browser alert, with message-source validation. Arduino D13 reports a driven-high output rather than an input pull-up; actual AVR HEX passed. Excalidraw rejects drawings with missing visible embedded image data; imported image encodings are not exhaustively decoded. Pocket Golf keeps rolling shots dirty when only a settled checkpoint was saved and confirms before discarding an unsaved lie on a hole change. Local desktop/phone account tests and live desktop/phone grid and Golf plus phone Arduino/Excalidraw checks passed. Physical touch, all golf holes and real hardware remain unverified. Live release `a97883808565173fff6ade26fe2b1b86e3ba0a23ad8697ef75fe6ae35047faf4`.

Hosting manifest `af382dc90097bd42dc5e2fd2803b4b8607f43ef6f446c0b7f9d92f49f2cd6554`; rollback inputs `/var/backups/webhost-sites/change-20261101T112305791876Z` and `/var/backups/webhost-sites/change-20261101T112305792529Z`.

## Spreadsheet chooser, Pico flash and Target Garden — 2026-11-01

Spreadsheet discards stale folder selections, Pico page-program correctly wraps within its 256-byte buffer, and Target Garden isolates pointer input and cancels interrupted actions. Local desktop and emulated-phone tests passed; actual MicroPython file save, sync and reopen was tested locally. Live phone-sized Spreadsheet and desktop/phone-sized Target Garden account tests passed. Pico on the public site, physical hardware and touch, and full game rounds were not verified. Tests using Pico firmware require separately supplied ROM and UF2 inputs, not checked in.

Live release `ed3549fdf4abfd8b49a7218b0959fbaeb7c7d199549f2be6f5da3092b008f236`; manifest `ed1412c05813ddb51ca5f24ea5035faae3cc442d222cf4d283bd81e5bcce1203`; Caddy `bb191d3cba6bdda759fd6f23641dd67dabdffc3cd5545b233eb43edaca971612`; rollback inputs `/var/backups/webhost-sites/change-20261101T112839957902Z` and `/var/backups/webhost-sites/change-20261101T112839973400Z`. Obsolete generated releases `0f6ede882282925cb05ee76bec81bfa338fa88d31e98e8794dec362336599fc7` and `cc0ce123dc3dee23da9f279107b286c40c3f01dbed6f2a297d5f93f9f9ecb4c5` were deleted to free space; their historical rollback references are no longer usable. The isolated private local test state at `active-system/.build/simplified-local-test-18434` was retained because its prior contents could not be verified.

## Folder-choice guards live — 2026-11-01

Live release `49f374069eb0618689d79bcba17de79e777b3856e75f142d1f603e0ca87f10e9` contains the Data Explorer, Digital Logic and Image Editor folder-choice fixes. Public emulated-phone account tests passed stale selection, save, sync and fresh reopen for all three. Physical touch and other races are unverified. The three test accounts were disabled by matched username and subject; files retained. Root, `/desktop/`, and `/blog/` returned HTTP 200. Managed manifest `ebc10320b5325d3ead579cd905588765be7682729dac65fb4e525bfca8c293fd`, Caddy `33d50c8f3d868dfc48dfba896cb4d077db58fb27cf7d47e507c91cee385f403d`; rollback inputs `/var/backups/webhost-sites/change-20261101T113518646234Z` and `/var/backups/webhost-sites/change-20261101T113518647093Z`, prior release `ed3549fdf4abfd8b49a7218b0959fbaeb7c7d199549f2be6f5da3092b008f236`. Webhost has approximately 1.5 GB free. Document Editor and SVG Editor fixes in `0273d649f` remain source-only; SVG `/Untitled.svg` recovery special case has not had a browser test.

## Document and SVG recovery live — 2026-11-01

Release `aa7ac76797b68ec21e2c5549df74cbde2e4c54425d9ad59e3d77f14054bea0e8` is active from `49f374069eb0618689d79bcba17de79e777b3856e75f142d1f603e0ca87f10e9`. Public emulated-phone account tests passed Document folder concurrency/stale destination/save/sync/reopen and SVG Untitled.svg transient restore, separate blank scratch save, preserved server original and Retry. Physical touch and actual drawing in this recovery path remain unverified. Test accounts disabled after subject match; files retained. Root, `/desktop/`, `/blog/` HTTP 200. Manifest `c02a6dc6d74f4a22963ccfdfbac6821b23d4adfa3a06f7230139d4961f352584`; Caddy `cba9f1d1eceb5e7c8dd051cc3fb9e90a9e7ad345384b5920a543b82f807d36ba`; rollback inputs `/var/backups/webhost-sites/change-20261101T113956039889Z` and `/var/backups/webhost-sites/change-20261101T113956040652Z`. Inactive generated release `a97883808565173fff6ade26fe2b1b86e3ba0a23ad8697ef75fe6ae35047faf4` removed to free space; historical rollback references to it are unavailable. Box-webhost has approximately 1.5 GB available. PDF Viewer and Circuit Simulator changes remain source-only.

## PDF and Circuit recovery live — 2026-11-01

Live release `cbe2c6665631236986829fbf99c1cea651e96cef180dad2a38287829c52b2c5f`, previous `aa7ac76797b68ec21e2c5549df74cbde2e4c54425d9ad59e3d77f14054bea0e8`. Public phone-sized account tests passed PDF temporary failure and valid/invalid retry and circuit failure/cancel/confirm/sync/original recovery. Test accounts disabled by exact subject, files retained; physical touch and hardware unverified. Root, `/desktop/`, `/blog/` returned 200. Manifest `f62f770d7642dcd5fd984ca658e060d96fd512f972cea13911a86930f4287ca4`, Caddy `33e406057f5560332517d87dcc7d88057f8ee1dc405ca092136e21cdb6b89fbc`; rollback inputs `/var/backups/webhost-sites/change-20261101T114239855188Z` and `/var/backups/webhost-sites/change-20261101T114239855633Z`. Inactive release `ed3549fdf4abfd8b49a7218b0959fbaeb7c7d199549f2be6f5da3092b008f236` removed; historical rollback references to it are no longer usable. Box-webhost has about 1.5 GB free.

## Native release archival — 2026-11-01

Under the managed hosting lock, 54 manifest-verified inactive native release directories (5,616,474,081 bytes of source files) were copied to `/srv/data/codi-archived-native-20261101`, verified against manifests and by rsync checksum, rechecked against live references, and removed from the root filesystem. Active `classroom-login-r1`, `file-admission-r1` and all seven additional configuration-referenced release names remain. Receipt with exact mappings is `/srv/codi-connected/native-archive-result-1793533892135451177.json`. Root free space increased from approximately 1.5 GiB to 6.8 GiB; `/srv/data` has about 440 GiB free. Caddy, issuer, guest and file service remained active. The old native paths moved to the archive cannot be used directly as rollback paths without restoration. Simplified static releases have not been broadly cleaned.

## Replicad and G-code recovery live — 2026-11-01

Live release `a8b2362b5c16d36eb7e0201855c1a31024203c75b32eb4b7e2e4e2bd96852abe`, previous `cbe2c6665631236986829fbf99c1cea651e96cef180dad2a38287829c52b2c5f`. Public emulated-phone account tests passed Replicad transient read, edit preservation, cancel/confirm retry and unchanged synced original; G-code failed read, retained target, Reload, synced reopen and window close. Test accounts disabled by exact username/subject; files retained. Root, `/desktop/`, `/blog/` returned 200. Manifest `c9be948ddc6a9dae026a524b0e9d4c49c1c6e8b99d4afd936c42a3da4f4189d9`; Caddy `e49d1f9730cc07e4bee511ef57e01f70aeacefb0014c6dbbfa077e9ccd0d2819`; rollback inputs `/var/backups/webhost-sites/change-20261101T115224663171Z` and `/var/backups/webhost-sites/change-20261101T115224663866Z`. Box-webhost has about 5.9 GB free. Physical touch and hardware not tested.

## Simplified static archival first batch — 2026-11-01

Four verified unreferenced generated static releases (`00490a67…`, `0115bfa3…`, `0124ca7e…`, `0129c55e…`) were copied with link-dest reuse, checksum verified and removed from the root filesystem under the hosting controller lock after checking references. Full identifiers and mappings are in `/srv/codi-connected/simplified-archive-<hash>.json`. Archive location `/srv/data/codi-archived-simplified-20261101`; live release `a8b2362b…`, prior `cbe2c666…` and `aa7ac767…` plus other configuration references retained. Root free space rose approximately 5.9 to 6.7 GiB. Caddy, issuer, guest and file service remained active. Archived historical paths require restoration before use; further batches remain.

## Simplified static archival second batch — 2026-11-01

Ten more verified inactive static releases were archived to `/srv/data/codi-archived-simplified-20261101`, making 14 across both batches. Each has a checksum-verified copy and an individual `/srv/codi-connected/simplified-archive-<hash>.json` receipt. Active, two rollback and configured releases and account data were retained; Caddy, issuer, guest and file services remained active. Root free space increased from approximately 5.9 to 11 GiB across the two batches; the archive used 8.7 GiB with link-dest reuse and `/srv/data` had 431 GiB available. Archived old paths must be restored before use. Hundreds of historical releases remain; no further batch was started.

## Audio and Grid recovery live — 2026-11-01

Live release `7148c2f51b5dc379d4de1ec4a3b44b152166b9b65b4236be8591b6e497236e80`, previous `a8b2362b5c16d36eb7e0201855c1a31024203c75b32eb4b7e2e4e2bd96852abe`. Public emulated-phone account tests passed Audio stale chooser/save/sync/reopen, and Mesh:Tool and Kiri:Moto separate scratch save, preserved server originals and cancel/confirm retry. Five test accounts disabled after exact subject match; files retained. Root, `/desktop/`, `/blog/` returned 200. Manifest `4d0e0ef799a9c7290b51c7943901b70970a66ac762fbceef4cb4c8a86792c00f`; Caddy `89684fe6f59e79d76d274fec56ce0c6b7e94572a516790e17418f64649185062`; rollback `/var/backups/webhost-sites/change-20261101T115947527723Z` and `/var/backups/webhost-sites/change-20261101T115947530533Z`. Box-webhost has about 9.2 GB free. Physical touch and machine operation remain unverified.

## Text and Excalidraw live — 2026-11-01

Live release `aa1f21ee7c203c8b57d51cf60aac7fbd90ca465edadbfb69641bc7ef8624bf3d`, previous `7148c2f51b5dc379d4de1ec4a3b44b152166b9b65b4236be8591b6e497236e80`. Public emulated-phone account tests passed Text picker serialization, preserved edits, save/sync/reopen and Excalidraw transient restore, cancel, actual scratch drawing sync, original preservation and retry. CodeMirror builder dependency had the same hash as the prior release. Two exact test accounts disabled; files retained. Root, `/desktop/`, `/blog/` 200. Manifest `8607cd94af9725e2b09c8b3ce00be1247068a943137ea12135de65a0a4d685f6`; Caddy `db11e1f61760a2ae284eacd1a62f94ceef41e6717c154a3b30f26a63bd6d0bc6`; rollback `/var/backups/webhost-sites/change-20261101T120547868593Z` and `/var/backups/webhost-sites/change-20261101T120547869527Z`. Box-webhost about 8.3 GB free. Physical touch not tested.

## diagrams.net recovery live — 2026-11-01

Live release `d289dfcb61f16b832eaa3164cd97fb14054016b6ada12a2c102a6c9a27eee845`, previous `aa1f21ee7c203c8b57d51cf60aac7fbd90ca465edadbfb69641bc7ef8624bf3d`. Public phone-sized registered-account test passed injected failure, separate scratch save/sync, cancel/confirm retry and preserved original. Exact test account disabled; files retained. Root, `/desktop/`, `/blog/` 200. Manifest `5c873ea1683f0966a2521f3da905b69dd497bd47457f4142addca5e4802a22ef`; Caddy `e9462eab85f401f23e61d693cb96c9c913013648b44ad536f9bda8480682d5aa`; rollback `/var/backups/webhost-sites/change-20261101T121407927468Z` and `/var/backups/webhost-sites/change-20261101T121407928585Z`. Webhost 7.3 GB free. Physical touch and actual drawing in recovery test remain unverified.

## Notebook and Embroidery recovery live — 2026-11-01

Live release `3be0a02b7066207699be34c0aea84da104c3d136da19a53de067b1f0983d89aa`, previous `d289dfcb61f16b832eaa3164cd97fb14054016b6ada12a2c102a6c9a27eee845`. Public phone-sized Notebook and Embroidery recovery/scratch/sync/retry passed. Authenticated Embroidery source ZIP fetch matched pinned SHA `e35e6aa8ac02c313ca94b15df132451a9f55707565ae7b54696e2f6334ae84cf`; source ZIP asset also returns 200 unauthenticated and requires access-policy review. Direct `/browser-sources/` returned 401 in plain fetch with and without sign-in; special Browser-session navigation in an internally launched experimental Browser timed out waiting 120 seconds for Licenses & source to enable; cause unproven and access not demonstrated. Three exact test accounts disabled; files retained. Root, `/desktop/` and `/blog/` returned 200; webhost 6.4 GB free. Manifest `351661e871d61a2a19269a17ec4ae7cb2405e0f88793b9d8787e4d93946f2022`; Caddy `694344584d88c029a12ec295f35883bb2b3f3c600c0d42f07be2a8acf72d9745`; rollback `/var/backups/webhost-sites/change-20261101T121616939458Z` and `/var/backups/webhost-sites/change-20261101T121616940423Z`. Earlier intermittent Notebook startup errors remain unproven; physical touch and sewing unverified.

## Stitch Converter recovery live — 2026-11-01

Live release `47eb430c99c4b03ba88649fc9d5963ee9eb7d5321665792891a9e01f6968cf59`, previous `3be0a02b7066207699be34c0aea84da104c3d136da19a53de067b1f0983d89aa`. Public phone-sized account test passed transient failure, separate scratch sync, cancel/confirm retry and unchanged original. Exact test account disabled; files retained. Root, `/desktop/`, `/blog/` 200. Manifest `1775a04104703353e3570eab044c711f730239e2c64e2e04348c9880e334e92d`; Caddy `8eb042938ab272be9dd2a1cfabdde75d7a57f11e4d9c29eb637c46194860ac02`; rollback `/var/backups/webhost-sites/change-20261101T122255890953Z` and `/var/backups/webhost-sites/change-20261101T122255906322Z`. Webhost 5.5 GB free. Physical touch, conflict retry and sewing not tested.

## Calculator and protected Browser sources live — 2026-11-01

Live release `990d773a166c62841b5a4e763b2bd1b4360f02d571819e948519894e95d04ee5`, previous `47eb430c99c4b03ba88649fc9d5963ee9eb7d5321665792891a9e01f6968cf59`. Public desktop/phone Calculator mixed input, calculation and account sync passed. Public phone account menu opened signed Browser source index, no-cookie request returned 401, and tab close revoked the lease (subsequent 401). Embroidery corresponding-source ZIP remains a separate public static asset; this is not the protected Browser page. Three exact test accounts disabled, files retained. Root, `/desktop/`, `/blog/` 200. Manifest `fd5a6b206e48ec95f6edd4963e62bf806139d830ab14aaaf0ff574d5e1a6a75a`; Caddy `19455a5c87469dd9dfdab06e112d951d4349a427a9f7a2f238b7a534a5f12505`; rollback `/var/backups/webhost-sites/change-20261101T122534876279Z` and `/var/backups/webhost-sites/change-20261101T122534877006Z`. Webhost had 4.5 GB available before the next archive batch. Physical touch unverified.

## Simplified static archival third batch — 2026-11-01

Ten more verified inactive static releases were archived to `/srv/data/codi-archived-simplified-20261101`, making 24 across three batches, with individual `/srv/codi-connected/simplified-archive-<hash>.json` receipts. Active `990d773a…`, rollback `47eb430c…` and `3be0a02b…`, earlier protected rollbacks, configured paths and user data retained; Caddy, issuer, guest and file services active. Root free space rose from 4.5 to 5.5 GiB; archive uses 14 GiB with link-dest reuse; `/srv/data` has 426 GiB available. Archived old paths require restoration before use; more historical releases remain.

## Arduino and Pico fixes live — 2026-11-01

Live release `5a3605bbafde2e08132122a5dd54b75744f4dfe1e5d644f7adcbdce4bc096430`, previous `990d773a166c62841b5a4e763b2bd1b4360f02d571819e948519894e95d04ee5`. Public phone-sized account tests passed Arduino injected transient read, actual AVR Blink HEX retry, synced original and close/reopen; Pico stale folder, save/sync and worker disposal used a mocked worker. Two exact test accounts disabled; files retained. Root, `/desktop/`, `/blog/` 200. Manifest `8bb3ff8bfc5274acc458ef296f115ba1345c978ae0809fe2df3998690d7cb9a3`; Caddy `1e819ca9e5f354e5699416d33d3e97697f02d5385ecbb7c879f496ff6e6250d1`; rollback `/var/backups/webhost-sites/change-20261101T123302763486Z` and `/var/backups/webhost-sites/change-20261101T123302764218Z`. Physical touch, Pico firmware fidelity in this test and hardware remain unverified.

## Simplified static archival fourth batch — 2026-11-01

Ten more verified inactive static releases moved to `/srv/data/codi-archived-simplified-20261101`, making 34 receipts under `/srv/codi-connected/simplified-archive-<hash>.json`. Active `5a3605bb…`, rollbacks `990d773a…` and `47eb430c…`, referenced releases and user data remained. Root free 4.5 to 5.8 GiB; `/srv/data` 420 GiB available. Caddy, issuer, guest and files active. Archived paths require restoration before rollback; more historical releases remain.

## Spreadsheet recovery live — 2026-11-01

Live release `519e1f95902918098f703f63f6926f77ae365885c2615da29f5f2d932ccee8fa`, previous `5a3605bbafde2e08132122a5dd54b75744f4dfe1e5d644f7adcbdce4bc096430`. Public phone-sized account test passed transient restore failure, cancel, separate scratch sync, unchanged original and retry. Exact test account disabled; files retained. Root, `/desktop/`, `/blog/` 200. Manifest `c0fa25655237cba7809caa7c5d02a8da46573d6f74436d4f8aba82adf7719b4c`; Caddy `c2a8bdd2d498bea0c76d6f98be3ed2040f8fc09ec52d11164afd240ef9933a13`; rollback `/var/backups/webhost-sites/change-20261101T123653851606Z` and `/var/backups/webhost-sites/change-20261101T123653852354Z`. Webhost 4.9 GB available. Physical touch and import-conflict retry remain unverified.

## Simplified static archival fifth batch — 2026-11-01

Ten more verified inactive static releases moved to `/srv/data/codi-archived-simplified-20261101`, making 44 receipts under `/srv/codi-connected/simplified-archive-<hash>.json`. Active `519e1f95…`, rollbacks `5a3605bb…` and `990d773a…`, referenced releases and user data remained. Root free 4.9 to 6.7 GiB; `/srv/data` 413 GiB available. Caddy, issuer, guest and file services active. Archived paths require restoration before rollback; more historical releases remain.

## Document and Data Explorer recovery live — 2026-11-01

Live release `d9929c891b62152c520c17fbdf8ee7f9370b58d268e200bd50da1c1a96b62c38`, previous `519e1f95902918098f703f63f6926f77ae365885c2615da29f5f2d932ccee8fa`. Public phone-sized account tests passed Document separate scratch save/sync, preserved original/retry and Data transient project failure/cancel/retry, real SQL/sync and original preservation. Two exact test accounts disabled; files retained. Root, `/desktop/`, `/blog/` 200. Manifest `4c9b88b08603f483470ba98372d5b55356353158eff3885b8fb1c06ce1ccfa3c`; Caddy `4e25cd16bcfa8275870da98956e928f85772a8aeb6d3d179e0eae605e558d461`; rollback `/var/backups/webhost-sites/change-20261101T124142392051Z` and `/var/backups/webhost-sites/change-20261101T124142392805Z`. Webhost 5.8 GB available. Physical touch and broader failure modes unverified.

## Simplified static archival sixth batch — 2026-11-01

Ten verified inactive releases moved to `/srv/data/codi-archived-simplified-20261101`, bringing total receipts under `/srv/codi-connected/simplified-archive-<hash>.json` to 54. Active `d9929c89…`, rollbacks `519e1f95…` and `5a3605bb…`, referenced releases and user data retained. Root free 5.8 to 7.4 GiB; `/srv/data` 407 GiB available. Services active. Directory `/srv/codi-connected/simplified/2a30ac7ba344873fa8ce67feeb09beb2d5493a4f58c2c9b8cfea580f0eb10f5f` was left untouched because its embedded manifest ID is `37db369f7d71b426254bc7f5325231006466172d80488d38edcad2d64534e587`. Archived paths require restoration before use; more historical releases remain.

## Image and student logic live — 2026-11-01

Live release `422528f00e618ba746e3b21a8cc59d108bce5cb8c750034f88307727882b9106`, previous `d9929c891b62152c520c17fbdf8ee7f9370b58d268e200bd50da1c1a96b62c38`. Public phone-sized tests passed image retry/cancel, actual resize/save/sync/reopen and scratch preservation; Digital Logic example-first view, advanced editing, save/sync and all 16 two-bit comparator interactive/truth-table combinations with project/CSV fresh reopen. Three exact test accounts disabled; files retained. Root, `/desktop/`, `/blog/` 200. Manifest `b074c7e604a02181c7bba9ed346e90956468d046551366000e7b1d3607cf4725`; Caddy `57301f7506768e5ad4cb12d7efb785e2a4de524d949d46c2e2847d8a44ef1c2f`; rollback `/var/backups/webhost-sites/change-20261101T124705995423Z` and `/var/backups/webhost-sites/change-20261101T124705996175Z`. Webhost 6.4 GB free. Physical touch and hardware validation unverified.

## Report, audio and G-code student workflows live — 2026-11-01

Live release `c38b85b99408ced476c6fdd429ac49e520c79a20cae70c6afd64d901456e7fc8`, previous `422528f00e618ba746e3b21a8cc59d108bce5cb8c750034f88307727882b9106`. Public phone-sized account tests passed report heading/save/sync/PDF text/reopen, audio tone/edit/close warning/WAV sample checks/sync/reopen, and compact G-code render/details/status/failed-load preservation. Three exact test accounts disabled; files retained. Root, `/desktop/`, `/blog/` 200. Manifest `62b6cafdec7e9046b05aba6d5ea829894283b1e550b80d5eaaa2c3a828263d5f`; Caddy `d9fab9b53e13a611bfb29290607ea27e79edefd1092a78d2e1adddd4f1ecce06`; rollback `/var/backups/webhost-sites/change-20261101T125345527573Z` and `/var/backups/webhost-sites/change-20261101T125345528411Z`. Webhost 5.5 GB free. Physical touch, audio hardware and machine validation unverified.

## Simplified static archival seventh batch — 2026-11-01

Eight verified inactive releases were archived to `/srv/data/codi-archived-simplified-20261101`, bringing per-release receipts in `/srv/codi-connected/simplified-archive-<hash>.json` to 62. Root free 5.5 to 7.4 GiB; `/srv/data` 403 GiB free; services active and hosting lock released. Two directories were left untouched due to directory/manifest ID mismatch: `2a30ac7ba344873fa8ce67feeb09beb2d5493a4f58c2c9b8cfea580f0eb10f5f` vs `37db369f7d71b426254bc7f5325231006466172d80488d38edcad2d64534e587`, and `3d2842f5c3e07905e95039074f28752047c58e80dd339ba86936152107d8bee6` vs `7974df7f6fdef57521a808ee39d868c2c9010c54047ca831719218657ac3073f`. Archived historical paths must be restored before use.

## SVG animation guard and divider lesson live — 2026-11-01

Live release `5eb4d3bd75957010ffd8dfd3c9784061b0e7f2d44999e567e1a20284a2376a6f`, previous `c38b85b99408ced476c6fdd429ac49e520c79a20cae70c6afd64d901456e7fc8`. Public phone-sized SVG test passed inline CSS animation refusal, original/current preservation and static save/sync/reopen. CircuitJS actual divider yielded simulated 5 V, desktop save/sync and emulated-phone reopen with same output. Two exact test accounts disabled; files retained. Root, `/desktop/`, `/blog/` 200. Manifest `74c1d53cd57ee8eecd482da5747294f33b7524eb09cb9e160a2457d06dd81f49`; Caddy `db97dc8b7f126c44a4477127c6a6b669dc72fbb5b6e31e7880f8b0264c004b28`; rollback `/var/backups/webhost-sites/change-20261101T125942251935Z` and `/var/backups/webhost-sites/change-20261101T125942252596Z`. Webhost 6.5 GB free. Broader CSS, physical touch and hardware unverified.

## Student spreadsheet, model and drawing workflows live — 2026-11-01

Live release `3d552ea751f1983b0365d625a8926334cbd01a72717153ebc90a35c832787adc`, previous `5eb4d3bd75957010ffd8dfd3c9784061b0e7f2d44999e567e1a20284a2376a6f`. Public phone-sized account tests passed Spreadsheet formula edit/cancel/sync/reopen; Replicad project/upload/invalid recovery/sync/reopen and dimension-checked STL/STEP; Excalidraw actual rectangle drawing, matching/custom export, sync and reopen. Three exact test accounts disabled; files retained. Root, `/desktop/`, `/blog/` 200. Manifest `f3ef2340d9e9aa08fbab1c1b8c7aa3e2e020815281c52e5e522bd73a1a92d041`; Caddy `cb40c9b3a5fcd77a31de100a36a1c9f1dbccc3368e54b9a2b1457642f2bd0476`; rollback `/var/backups/webhost-sites/change-20261101T130612321849Z` and `/var/backups/webhost-sites/change-20261101T130612322542Z`. Webhost 5.5 GB free. Physical touch and manufacturing unverified.

## Pico, Stitch and PDF student workflows live — 2026-11-01

Live release `84fea19fcca8a92da2f04c0ce00fbf5173e0b42db3dcb437c2d863d91c1dd6fc`, previous `3d552ea751f1983b0365d625a8926334cbd01a72717153ebc90a35c832787adc`. Public phone-sized account tests passed actual Pico worker Blink transitions and LED text; Stitch edit/preview/save/machine export/upload/sync/reopen; PDF two-page search/match/page navigation/resize and failed-open recovery. Three exact test accounts disabled; files retained except two explicit PDF fixture files removed by their own test. Root, `/desktop/`, `/blog/` 200. Manifest `a912c5988d08083f318c616068e18ba51b2826a31c216dc71c7a35c6d2e1dbe9`; Caddy `b64721717b45087f13d441c607cfcfdcc77b1c1d05c8275da693183edfd524c4`; rollback `/var/backups/webhost-sites/change-20261101T131140839057Z` and `/var/backups/webhost-sites/change-20261101T131140839734Z`. Webhost 4.6 GB available. Physical touch, physical board and sewing unverified.

## Simplified static archival eighth batch — 2026-11-01

Ten more verified inactive releases archived to `/srv/data/codi-archived-simplified-20261101`, 72 total receipts under `/srv/codi-connected/simplified-archive-<hash>.json`. Active `84fea19f…`, rollbacks `3d552ea7…` and `5eb4d3bd…`, references and user data retained; services active. Root free 4.6 to 6.4 GiB; `/srv/data` 399 GiB free. Three more directory/manifest mismatches remained untouched: `400e94ae767a6119cb2f54bef1da2484590711a8e03f5191307f0242bad9ddf3` → `02f12caceb95e8e2fb2c2f80b4b901063d88a0714186f145483e35079037ca7e`; `43691c72630d640ed36d150d3b394079e7da03746833263ffdc24bb10491577a` → `301adf90b54cdff3b676ed3d20608a8e4ac58de9ca3ec9e734548383567f08cb`; `4553df94822a2ba98542d1bc5a4e975ba3d6ae458d97643e6817963fb1a85e28` → `dbfb7bb63819467674a9943e144d46a0d1faedf5cd53b3093fd26cabc160c422`. Earlier two mismatches also retained. Historical archived paths require restoration before use.
