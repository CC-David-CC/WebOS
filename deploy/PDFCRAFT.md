# PdfCraft document integration

Status: the clean-blank/community-chrome follow-up is deployed and verified on
ksu.codes, release `1c4623b8403bd44b534722bf3db92f6c3bbd96d8e40add396623cb71c44c97db`.
Current PdfCraft source: `a5b512846f59c6e5306821cdffdb448e54695ccd`.
The initial integration and its historical receipts are recorded below.

The requested first milestone is native PDF reading/editing, account Open,
Save/Save As, document activation, unsaved-work protection and account recovery
inside the existing classic Desktop. It is not a claim of Acrobat parity or of
qualification of every tool displayed by upstream PdfCraft.

The native PDF object graph remains authoritative. Prepared saves capture the
serialized native state, and only a server-confirmed account write can adopt a
saved path/revision. Later edits remain dirty. Failed/cancelled/conflicting Save
As retains the previous binding; an unknown outcome retains the pending native
write and refuses blind retries. Browser-local recovery remains distinct from
an account save. A recovered unknown write can be reviewed after refresh and
saved as a separate copy; automatic reconciliation of unknown writes is not
provided by this milestone.

The adapter uses the existing Runtime recovery journal, account file service,
Desktop activation and shared Craft save context. Preferences and recovery are
account scoped. Desktop owns the single navigation warning in hosted mode;
standalone PdfCraft retains its own warning. Native finalization leases pause
input/commands, while edits during earlier close decisions invalidate those
approvals. New/Open/Close/import/generated copies use Desktop-owned views.

## Source and build

Initial integration compiled PdfCraft browser source:
`670f257268545f585f8104928357cea33961e3bb` on `webos/pdf-document-host`, based on
verified public upstream `271e479c53723b1b294c866d5cb2f27604601b29`.
Accepted maintained source is `16e5c9b697a50e1e1ba39b1824344b65eb5ed3a1` (the additional commits change README and licence packaging only); Desktop is `173e6aca5d48834a3fcc7a98eb0949492f593723`. Upstream main and the maintained fork remain separate. The existing WordCraft
engine is reused unchanged at `edeb4a090cd301cd7d4405e20af795007b37b69b`.

Pinned development compiler: nightly-2026-11-16,
rustc1.102.0-nightly(5f4effd57 2026-11-13), LLVM23.1.5; Trunk0.21.14 and
wasm-bindgen0.2.129. The portable recipe is `apps/pdfcraft/webos/build.py`.
The complete app/OCR-worker graph includes source-pinned fonts, translations,
models and their licence texts. Build output is outside source, built offline
with original KSU.CODES hidden and source read-only. One current compiler cache
is retained by the user's decision; compiler output is not committed.

The first cold browser graph compiled in17m25s (main Cargo build), plus worker,
packaging and hook time. A subsequent browser-entrypoint fix compiled that Rust
crate in4.50s using the same cache. These are different workloads; neither is a
general timing guarantee. The separate controlled engine benchmark is in the
private compiler receipt.

The Python3.14 parser-offset and asset-notice manifest mistakes were corrected
in the packaging recipe. The current portable builder completes end to end.
Earlier failed receipts remain evidence, not selected release artifacts.

## Qualification and limits

Native core qualification:794 engine unit tests,1,036 UI unit tests and1,932 UI
integration tests pass. Four browser-shell/profile tests and11 adapter/journal
checks pass. Scoped strict clippy, formatting, assets, layers and WebAssembly
checks pass. Existing upstream manual timing/raster probes remain ignored;
none was disabled to obtain these results. The later browser-warning change
reran the affected browser-shell/native and WASM checks; engine/UI source was
byte-identical and their passing receipts were reused.

Actual signed-account local qualification passes22 PdfCraft checks (17 document/account and5 lifecycle), plus54 affected-app regressions:19 WordCraft documents,11 Text recovery,9 Text binding and15 classic Desktop/Files/Calculator checks. Hosted runs recorded the same76 passing assertions. The final hosted main suite wrote17 PASS assertions and a PASS result, but its outer recorder was interrupted before recording the process exit; no exit0 is claimed for that run. The other five hosted suites completed with exit0. The unchanged WordCraft/Text/Files/Calculator/viewer
payloads already passed54 local checks; a byte comparison proves those payloads
are unchanged by the final PdfCraft-only warning fix.

Native CLI text extraction and rendering verify actual downloaded PDFs,
including both the original text and previously unfinished recovery text. The
minimized live snapshot and its saved account copy also retain the exact text.
Fresh browser contexts prove server-backed retrieval, not a physical second
machine or multi-user capacity.

This milestone does not qualify every upstream tool, arbitrary PDFs, browser
password prompts, printing, digital signatures, OCR review, all import/export
formats, or production delegated-agent transport. Encrypted save/recovery and
password-field filtering have native regression coverage. Recovery preserves a
native document snapshot and pending supported typing, not full undo history,
every unfinished tool workflow, storage eviction or zero-loss power failure.

Private checkpoint, exact commands/exits, failed and selected receipts:
`/path/to/workspace/Projects/.webos-migration/pdfcraft-nightly-20261117-7barkpzk/`.
The [general Craft guide](../migration/CRAFT-INTEGRATION-GUIDE.md) and running log
record responsibilities for the next application.

The initial integration graph and its then-immediate rollback were verified file by file; the
backend instance/issuer, beta index, six service PIDs and scoped WordCraft print
CSP remained unchanged. Static content is on the data SSD. That historical release's
rollback configuration is `/var/backups/webos-pdfcraft-20261117-02/`; its previous
release is `46a37155201fef7b5acbc86df1c3e80d6d48bd8c47d74b825991227e6cc69622`.
The user's separately approved retired-build cleanup recovered68.9GiB on the boot
SSD while preserving beta's active build. See [disk evidence](example.invalid-DISK.md).

## Untouched blank and community chrome follow-up

Local and hosted qualification passed; this follow-up is deployed.
Accepted PdfCraft source: `a5b512846f59c6e5306821cdffdb448e54695ccd`.
An untouched hosted starter page now uses a clean native baseline and closes
without a save prompt. Explicit Save and Save As still create valid account PDF
files; real edits prompt, and Undo of the first edit restores the clean baseline.
Generated/imported PDFs keep their existing unsaved semantics.

Only the prominent top-right Discord shortcut and its reserved width were
removed. About, its community/source links, contributor/model tabs, Help and Home
links remain. Actual About imagery was inspected. An existing tab geometry test
still named the removed shortcut; its bounds assertions now use the remaining
utility controls, including the macOS-only expectation. Linux native tests ran;
this is not a new macOS graphical qualification.

The affected native UI suites pass2,989 test executions, with five existing
ignored probes. Formatting, strict scoped clippy, assets/layers and all32 WASM
crate checks pass. One actual complete browser graph was built using the same
current compiler cache. No engine or shared Desktop/Runtime/Storage change was
needed for this follow-up.

Actual-browser qualification passes27 assertions each locally and hosted:5
blank/chrome,17 document/account and5 lifecycle, all with recorded exit0.
Independent native parsing verifies10 local and11 hosted saved PDF artifacts
and their expected text; genuine blank files have one page and no text. Hosted
evidence preserves the extra before-conflict artifact explicitly.
Browser profiles, synthetic accounts and output stay private outside Git.

The content investigation initially audited the wrong artifact: the later
stale-save test intentionally replaces `Recovered.pdf` with older fixture bytes
and downloads it again. That overwrote the local recovery sample. The original
recovered content survives in `Conflict-rescue.pdf`; focused full-path probes
also confirm the pre-conflict result. There was no demonstrated recovery loss.
The test now preserves `Recovered-before-conflict.pdf` separately, verifies
actual pending native text and stored snapshot bytes, and the checked-in native
content oracle distinguishes recovery, deliberate replacement and rescue. Failed
investigation receipts and the incorrect intermediate diagnoses remain private
evidence; they are not application regressions or passing artifact receipts.

One separate Desktop gap was identified by source review: PdfCraft is missing
from the classic saved-layout allow-list. Draft discovery restores dirty PDFs
as recovery views, but exact saved-window geometry and clean-PDF window
restoration are not qualified. This follow-up leaves Desktop unchanged and
records that gap for a scoped integration change with affected regressions.

Current private checkpoint and commands/exits:
`/path/to/workspace/Projects/.webos-migration/pdfcraft-blank-chrome-20261117-iutgpol3/`.


## Current release, continuity and rollback

- Release: `1c4623b8403bd44b534722bf3db92f6c3bbd96d8e40add396623cb71c44c97db`.
- Packaged parent: `c0f00cba25f85e055cb8c45a333a57dd2340609b`; later handoff-only commits do not change the public graph.
- Archive SHA-256: `2cb91a6cfea757f2abb36342a22fc90972635c7c681b889453f3e141c22bbf74` (72,146,297bytes;308 public files).
- Static root: `/srv/data/webos-viewer-releases/1c4623b8403bd44b534722bf3db92f6c3bbd96d8e40add396623cb71c44c97db/public`.
- Current rollback configuration: `/var/backups/webos-pdfcraft-blank-20261117-01/`.
- Immediate rollback release: `60e809a6e453af680b8fa1e2b6df557eb50b1369380ab711aec355fdd33d9a54`.

All308 files and the immediate rollback were verified. The other247 public
payloads, including Desktop and the other apps, are byte-identical. Only PdfCraft
and its build metadata changed. Backend instance/issuer, beta, six service PIDs
and WordCraft's scoped print CSP remained unchanged. No backend restart or
external Git publication occurred. Local bare origins retain accepted commits.

The owned temporary engine/candidate/profile/transfer outputs and the superseded
local archive were removed after qualification. One current compiler cache,
one current release archive, required pinned source/assets and small private
receipts/screenshots/synthetic PDFs remain. The reused WordCraft engine was
verified against all32 current archived WordCraft files before deleting its
redundant extracted tree. No original or unrelated WIP was deleted.

Guarded rollback uses the retained operator and private plan, with no rebuild:

```sh
cd /path/to/workspace/Projects/.webos-migration/pdfcraft-blank-chrome-20261117-iutgpol3
python3 run_operator.py rollback
```

Do not use the historical initial-release rollback directory for this release.
