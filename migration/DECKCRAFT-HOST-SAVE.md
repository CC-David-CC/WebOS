# DeckCraft confirmed-save source qualification

Selected fork `f0dd04e3ab7bf9a37d31a454d7f8dba5231b509a` fixes the reproduced
premature-clean bug and binds asynchronous completion to its document and view.
It stays disabled in the minimum desktop pending account/host integration.

## Original failure retained

Baseline `772219838e2807f0d5b0270f8993421499717f58` sent 5,240 presentation bytes
without an id and cleared dirty immediately. The controlled host stored nothing
and sent no acknowledgement. The owned no-ack test genuinely failed, exit1.
A subsequent review also exposed an old acknowledgement closing a newly reopened
Save As view. Both failing results are retained privately; they were not hidden
or obtained by changing the live site.

## Selected source and checks

The engine captures an immutable version at serialization. A matching reply sets
the originating document's saved snapshot, preserving later edits and the active
document. Save As identity changes only on confirmation. Unknown, duplicate and
closed-document results do not retarget another document. Pending saves are
bounded; timeout retains an unknown outcome and blocks blind repetition.
Save-and-close targets its original document, and File-view completion checks the
precise view lifetime. `ui.inspect.pendingSaves` reports real native targets and
pending/unknown state; these identities confer no server authority.

The app's complete `cargo xtask ci` passed all8 required stages: formatting,
PDF dependency validation, strict Clippy, workspace tests, doctests, assets,
layering and wasm. Workspace results were 2,278 passes, zero failures and five
pre-existing ignored tests (three screenshot generators and two long soaks).
No tests were newly ignored and no production lint allowance or CI relaxation
was introduced. Native SDK preparation used a
verified matching development package privately and the existing OS runtime;
no system package was installed. Three existing boolean expressions were
simplified with short-circuit order preserved for Rust1.95 Clippy.

The palette-save test now checks an explicit pending result, keeps the original
destination check and requires dirty before acknowledgement, then the same path
and clean state after it. This is an intentional async contract change, not a
successful save inferred from dispatch.

A fresh release WASM build from the clean committed source was packaged with
matching wasm-bindgen0.2.129 and run in real Chromium, with original source hidden
and networking disabled. The unchanged no-ack regression, extended acknowledgement
cases and reopened-view regression pass with zero page/external errors. Visible
pending and confirmed states were inspected in screenshots.

Owned browser commands (parent Puppeteer dependency; `CHROMIUM_PATH` optional):

```sh
node tests/deckcraft_host_save_browser.mjs /path/to/browser /path/to/private/no-ack.json
node tests/deckcraft_host_ack_browser.mjs /path/to/browser /path/to/private/acks.json
node tests/deckcraft_reopened_view_browser.mjs /path/to/browser /path/to/private/view.json
```

The extended cases cover wrong/correct/duplicate acknowledgements, later edits,
undo back to the acknowledged version, document switching and reopened view
identity. Test hosts send synthetic acknowledgements and store no account file.
These results qualify the real engine/transport boundary, not account persistence.

## Shared save wire

The parent selects craft-libs `a9a7c46a7a1708f01a00a139265d24f71ea0a543`.
The public `craft-web-host` crate now carries captured request/document/editor
revision, operation and document-save intent. It parses bounded explicit
failed/cancelled/conflict/unknown replies. Unknown retains the no-retry guard;
definitive failures retain edits and release the guard. Editor revisions are not
account server hashes or authorization grants.

The shared source passes formatting, strict full workspace Clippy and tests
(3,007 passes, zero failures,81 existing ignores), plus9 Node/WASM bridge tests.
Optional FFmpeg/ffprobe oracles were unavailable; default workspace success is
not codec-fidelity evidence. Tests use explicit UTF-8 locale and writable fixture
storage with source mounted read-only. No assertions were relaxed.

DeckCraft consumes that public crate at the canonical assembly sibling path;
the parent Gitlink supplies the exact commit. All other entries in the625-package lockfile
retain their versions and sources. Existing post_save envelopes are unchanged;
Rust consumers matching the new enum exhaustively need deliberate updates.
Other apps retain their own historical dependency pins.

The real browser failure test first failed against19ed30b: its save message
lacked the captured document identity. It passes against the selected clean
release build, checking malformed replies, all four outcomes, blocked unknown
retry, late confirmation and preservation of newer edits. The three existing
browser regressions also pass. The rendered recovery screenshot was inspected.
All host replies are synthetic and store no account file.

```sh
node tests/deckcraft_host_failure_browser.mjs /path/to/browser /path/to/private/failures.json
```

The private browser package uses Cargo release plus matching wasm-bindgen,
explicit bootstrap HTML and no wasm-opt; Trunk equivalence or deployment readiness
is not claimed. A stale cached credit generator was rejected before packaging;
its recompilation uses unchanged source and restores all committed credit rows.

## Remaining integration

Accounts/Storage retain authority. The host must map exact instance/session/
document/account-file identity and expected server revision, and acknowledge only
confirmed writes. Desktop mount/dispose, exports, cancellation, resource binding,
real multi-client persistence and delegated-agent authorization remain open.
Native ids and same origin are not permission grants. DeckCraft stays disabled
in the minimum. No deployment changed in this qualification.
