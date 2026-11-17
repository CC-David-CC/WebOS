# WordCraft file actions, print and status footer

Status: 2026-11-17 UTC — local qualification passed; prepared for scoped deployment.
The running ksu.codes release is still the preceding Design/defaults release.
This report does not yet claim a deployment.

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
and discarded `print()` errors. The proposed server policy adds `blob:` only to
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
- Final local browser qualification: 51 checks pass, each with exit0 and a
  matching served-build receipt: output eight, footer six, graphical print three,
  documents 19 and rich recovery/session 15. Actual print/error/footer images were
  inspected. Hosted verification remains pending. Earlier-source/harness receipts
  are retained as historical evidence, not relabeled as final-source results.

The first full native run found one existing Enter-key test assuming Print stayed
open after success. Its setup now reopens Print between separate gestures, keeps
exact print-job counts and held-key/file-browser exclusions, and asserts return
to the document. Earlier harness failures and the unreadable debug-stack image
remain recorded. The final browser failure fixture requires the exact short error.

## Release and continuity

Deployment remains pending. The existing static operator's optional
`--wordcraft-print-policy` prepares mutually exclusive CSP matchers alongside its
usual exact static-root update. It validates both configurations, preserves a
root-only rollback, fences concurrent changes, checks backend instance/issuer,
beta index and all six service PIDs, and rolls back failed activation checks.
No backend restart, account migration, beta edit or external Git publication is
part of this release. Synthetic test accounts are used for browser checks.

Private evidence/checkpoint:
`/path/to/workspace/Projects/.webos-migration/wordcraft-statusbar-20261117-wu7sdmzg/`.
One existing compiler cache is retained through QA by explicit user decision;
intermediate build/browser outputs are disposable. Required font/source inputs
remain separate from compiler output. The original workspace and unrelated
parent working files remain preserved.
