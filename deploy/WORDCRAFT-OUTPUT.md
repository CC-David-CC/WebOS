# WordCraft file actions, print and status footer

Status: 2026-11-17 UTC — deployed and qualified on https://ksu.codes.
All 51 local and all 51 hosted browser checks pass. Actual hosted print-preview,
print-error, document and footer images were inspected.

## Behavior and source

Selected WordCraft source: `626c74f99879fccef4c33f4385c3008505d9b695`.
The local feature history retains the implementation commit `667e0bab8bc14e74579ce00dcd03a14ab25e8230`
and its final bounded-error-message follow-up. Upstream-tracking `main` is unchanged.

- Save, Save As and exports return from File to the document after confirmed
  delivery. Pending, cancelled and failed actions retain their state. A late
  completion cannot dismiss a different document or File page. Save identity,
  newer unsaved edits and export-as-copy semantics remain authoritative.
- Save As returns both browser DOM focus and native caret focus, so ordinary
  typing resumes in the document. Focus restoration does not claim a save or
  dismiss File before acknowledgement, and is skipped during disposal/pause.
- “Save these pages as PDF” now delivers the actual native selected-page/copy/
  imposition PDF through account Storage. The wasm engine's filesystem-free
  command alone previously returned metadata without persisting bytes.
- Browser printing reports asynchronous PDF-load/print outcomes through native
  print state, refuses overlapping requests, surfaces bounded readable errors,
  and times out after 25 seconds. A timed-out frame cannot print later. Browser
  acceptance never proves that a physical job printed rather than was cancelled.
- The account-save/local-recovery footer remains one line. Narrow windows use
  ellipsis with full hover/accessibility text; the two states remain distinct.

The live print failure was reproduced as a CSP violation: `frame-src 'self'`
blocked WordCraft's generated PDF blob frame while the old hook returned success
and discarded `print()` errors. The deployed server policy adds `blob:` only to
frame-src on `/wordcraft/index.html`. Desktop/other-app CSP remains identical;
`object-src 'none'`, script restrictions and cross-origin isolation remain.

## Verification

- Final `cargo xtask ci`: all nine stages pass; 5,003 passed test executions
  across those stages, zero failures, eight pre-existing ignored. The count
  includes dedicated audit/language/doctest executions, not 5,003 unique cases.
- WordCraft adapter: 38 JavaScript checks pass. Policy/origin fixtures: five
  Python checks pass. Read-only Caddy validation on example.invalid passes.
- Fresh complete WASM engine: 31 verified payload files, 92,447,863 bytes,
  built offline from the selected source using pinned local providers and inputs.
- Final browser qualification: 51 checks pass locally and the same 51 pass over
  hosted HTTPS. All ten process exits are zero; every suite verifies the same
  served build before and after execution. Earlier-source/harness receipts remain
  historical evidence and are not relabeled as final-source results.

| Actual-browser suite | Local | Hosted |
|---|---:|---:|
| Output completion, focus, failure and short print error | 8 | 8 |
| One-line account/recovery footer | 6 | 6 |
| Real Chromium print preview and cancellation, twice | 3 | 3 |
| Document identity, Open, Save As, conflicts and response loss | 19 | 19 |
| Rich recovery, account isolation and session-end decisions | 15 | 15 |
| Total | 51 | 51 |

Print tests opened and cancelled the real browser preview; they submitted no
physical print job. The actual PDF page and controls were inspected. Independent
Text, Files and Calculator suites were not repeated: their payload bytes and
shared Desktop/Runtime code did not change. The affected Files/WordCraft Open and
account-file paths were exercised by the document suite.

The first full native run found one existing Enter-key test assuming Print stayed
open after success. Its setup now reopens Print between separate gestures, keeps
exact print-job counts and held-key/file-browser exclusions, and asserts return
to the document. Earlier harness failures and the unreadable debug-stack image
remain recorded. The final browser failure fixture requires the exact short error.

## Release and continuity

The deployed release is `a812d655798dcd4228b75e4a98ed2fec41210179431380f23d801a0808496174`, packaged from parent `033d824d664176ff6b11c062ce7ff23c075956c8`. The existing static operator's optional
`--wordcraft-print-policy` prepares mutually exclusive CSP matchers alongside its
usual exact static-root update. It validates both configurations, preserves a
root-only rollback, fences concurrent changes, checks backend instance/issuer,
beta index and all six service PIDs, and rolls back failed activation checks.
Activation and final continuity checks pass: all 249 public files match their
manifest; backend instance/issuer, beta index hash and all six service PIDs remain
unchanged. Payload comparison limits byte changes to WordCraft's engine/bundle,
app catalog/cache metadata and build/release receipts. Other viewer/app payload
bytes are unchanged. No backend restart, account migration, beta edit or external
Git publication occurred. Browser tests used their own synthetic accounts.

Archive SHA-256: `3acaf75058504ab99337381697d59ac1a1cb557de1a17a0ce99d882b6923b655`.
The archive is 28,314,634 bytes; the public payload is 97,886,424 bytes including
its receipt, with 96 JavaScript dependency notice records.

Rollback tag: `wordcraft-output-20261117-01`. The previous release
`d7a8f6ae73223079e78013d5f7b3aae01ff8716758b1c14d969f5c22e0ff698b`
remains verified on the host. Root-only configuration/continuity backup:
`/var/backups/webos-wordcraft-output-20261117-01/`. From this repository, rollback
uses the guarded operator (it refuses an unknown concurrent configuration):

```bash
ssh -o BatchMode=yes example.invalid sudo -n python3 - rollback \
  --tag wordcraft-output-20261117-01 \
  --release a812d655798dcd4228b75e4a98ed2fec41210179431380f23d801a0808496174 \
  < deploy/viewer_static_operator.py
```

Private evidence/checkpoint:
`/path/to/workspace/Projects/.webos-migration/wordcraft-statusbar-20261117-wu7sdmzg/`.
Seven verified generated engine/candidate trees (668,897,824 logical bytes),
30 synthetic browser profiles, the superseded local release archive and this
release's remote transfer stage were removed after qualification. The exact new
archive, receipts, screenshots, failed-run reviews and resumable checkpoint remain.
One existing compiler cache is retained through QA by explicit user decision;
required font/source inputs remain separate and preserved. The original workspace
and both unrelated parent working files remain unchanged. Source organization
and the five enabled apps are unchanged; this release adds no other Craft app.
