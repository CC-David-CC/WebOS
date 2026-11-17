# PdfCraft document integration

Status: local qualification passed; guarded ksu.codes deployment prepared. Hosted acceptance is pending.

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

Compiled PdfCraft browser source:
`670f257268545f585f8104928357cea33961e3bb` on `webos/pdf-document-host`, based on
verified public upstream `271e479c53723b1b294c866d5cb2f27604601b29`.
Accepted maintained source is `34c5920fe22937784bc16282852fc99a6926ca6c` (the additional commit changes README only); Desktop is `173e6aca5d48834a3fcc7a98eb0949492f593723`. Upstream main and the maintained fork remain separate. The existing WordCraft
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

Actual signed-account local qualification passes22 PdfCraft checks (17 document/account and5 lifecycle), plus54 affected-app regressions:19 WordCraft documents,11 Text recovery,9 Text binding and15 classic Desktop/Files/Calculator checks. Hosted results remain pending. The unchanged WordCraft/Text/Files/Calculator/viewer
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
`/home/dflanag3/Projects/.webos-migration/pdfcraft-nightly-20261117-7barkpzk/`.
The [general Craft guide](../migration/CRAFT-INTEGRATION-GUIDE.md) and running log
record responsibilities for the next application.
