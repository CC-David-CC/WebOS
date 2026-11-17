# WordCraft Save As Browse and export qualification

Status: 2026-11-17 UTC — deployed and qualified on https://ksu.codes.
All56 local and the same56 hosted browser checks pass. Actual chooser and
confirmed-document images were inspected locally and hosted.

## Scope

Hosted File → Save As → Browse must use the same account-owned `file.saveAs`
request as F12. The account chooser accepts the relative folder path and filename.
The native editor adopts the canonical destination only after Storage confirms
the write. Cancel, invalid paths, collisions and write failures preserve the
previous file identity and unsaved writing. Successful Save As returns to the
document with typing focus, and subsequent ordinary Save uses the chosen file.
Standalone file-dialog behavior is unchanged.

The earlier output report's Save As checks covered F12 and commands with explicit
paths. They did not qualify the actual Browse button. Its legacy fallback was
still using the suggested browser filename. This follow-up tests that button
directly; a passing command test alone is insufficient.

## Export assessment

Native qualification passes: all13 visible export buttons produce files; ten
formats reopen with heading/body text intact. All13 writers also deliver real WASM-generated account files with verified
server hashes and independent structure checks. The identity behavior below was
measured against those account writes.
The requested Browse correction does not redesign the export menu.

| Visible format | Extension | File-generation smoke | Current identity behavior |
|---|---|---|---|
| PDF | `.pdf` | PASS | Copy; retains source identity and dirty edits |
| Word | `.docx` | PASS | Save As; rebinds the document and marks serialized content saved |
| Word XML (Flat OPC) | `.xml` | PASS | Save As |
| Word 2003 XML | `.xml` | PASS | Save As; separate XML writer |
| OpenDocument Text | `.odt` | PASS | Save As |
| OpenDocument Text Template | `.ott` | PASS | Save As |
| Flat OpenDocument Text | `.fodt` | PASS | Save As |
| Rich Text Format | `.rtf` | PASS | Save As |
| Web page | `.html` | PASS | Copy |
| Markdown | `.md` | PASS | Copy |
| LaTeX | `.tex` | PASS | Copy |
| Plain text | `.txt` | PASS | Copy |
| Page image | `.png` | PASS | Copy of the first page |

Two separate integration gaps remain: the visible Export menu supplies its
suggested filename without the account chooser, and the seven Save As entries
above do not honor the menu's promise to save a copy. A writer producing valid
bytes does not fix those human-interface/identity problems. This report must not
be used to claim full Word/format parity or arbitrary-document fidelity.

Native button tests reopen the ten readable formats and check heading/body text;
PDF/PNG signatures and LaTeX text are checked separately. Browser qualification
uses the real WASM writers, account Storage, confirmed server hashes and
independent structural checks on every output. The browser writer assessment
does not substitute explicit-path commands for the native export-button tests.

## Evidence and continuity

Private work and resumable checkpoint:
`/path/to/workspace/Projects/.webos-migration/wordcraft-saveas-20261117-a6gvgome/`.
No external Git publication is authorized by this task. The original workspace,
beta, backend instance/issuer and unrelated working files are preserved. Reuse
the one approved compiler cache; remove this task's disposable output trees
after qualification and verified archive preservation.

Native source: `edeb4a090cd301cd7d4405e20af795007b37b69b`. All nine native CI
stages pass:5,005 test executions, zero failures, eight pre-existing ignored
(includes dedicated stage reruns). All38 adapter JavaScript checks pass.

Local actual-browser gates:22 Browse/export checks,19 document-identity checks
and15 rich-recovery/account-boundary checks pass on the same served build. The
actual chooser and confirmed saved-document images were inspected. Hosted
qualification also passes all56 checks. Existing native font-substitution warnings are outside
this narrowly scoped fix; file-generation smoke checks do not certify every
font or advanced-format feature.

## Release and continuity

Live release: `46a37155201fef7b5acbc86df1c3e80d6d48bd8c47d74b825991227e6cc69622`.
Packaged parent: `9eb2d11822c213d86123bc7d150870a4430c40af`.
Archive SHA-256: `1a6ccb3b0f0119fee6c8d523ee0b70d33e402e2886e1c14aff59a1f206f4b5b7`.
The archive is28,315,029 bytes; public payload97,886,628 bytes and249 files,
with96 JavaScript dependency notice records. The clean offline WASM build has
31 payload files (92,448,067 bytes) and uses the selected native commit above.

All249 deployed files match the release manifest. Both the new payload and the
rollback payload were fully verified. Byte changes are confined to the WordCraft
native engine/loader and build receipts. Desktop, Runtime, Files, Text, Calculator
and other app payloads are identical to the preceding release. Their independent
suites were not repeated. WordCraft's affected account-file paths, document
identity and recovery were tested. Existing backend instance/issuer, beta index,
all six service PIDs and print CSP remain unchanged. No backend restart, account
migration, beta edit or external Git publication occurred.

Rollback tag: `wordcraft-saveas-20261117-01`. Verified preceding release:
`a812d655798dcd4228b75e4a98ed2fec41210179431380f23d801a0808496174`.
Configuration/continuity backup:
`/var/backups/webos-wordcraft-saveas-20261117-01/`.

```bash
ssh -o BatchMode=yes example.invalid sudo -n python3 - rollback \
  --tag wordcraft-saveas-20261117-01 \
  --release 46a37155201fef7b5acbc86df1c3e80d6d48bd8c47d74b825991227e6cc69622 \
  < deploy/viewer_static_operator.py
```

The actual Browse regression failed on the old route (zero host requests), then
passed after the native dispatch correction. An initial test-only Path/string
comparison and prohibited `unreachable!` were corrected; complete passing CI
receipts are retained alongside those failures. Browser-harness setup corrected
an extra `tests/` path and added the existing Files-ready wait before selecting
its window; assertions were not weakened. The private browser wrapper now also
propagates its child exit status.

After qualification, both verified generated engine/candidate trees
(190,340,803 logical bytes), seven synthetic browser profiles, owned temporary
directories, the superseded local archive and this release's remote transfer
stage were removed. The owned local server was stopped. The exact current
archive, manifests, exported-file evidence, screenshots, failed-run evidence and
checkpoint remain outside Git/web roots. One approved compiler cache and all
required source/font inputs remain. The two unrelated parent working files are
unchanged. No build output was committed.

Next authorized work: benchmark a pinned newer compiler for development and
begin PdfCraft from its existing organized source. This release does not enable
PdfCraft or certify other Craft apps or full beta parity.
