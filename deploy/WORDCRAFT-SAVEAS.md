# WordCraft Save As Browse and export qualification

Status: 2026-11-17 UTC — all56 local browser checks pass; the previous
release remains live pending guarded deployment and hosted qualification.

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

| Visible format | Extension | Current identity behavior |
|---|---|---|
| PDF | `.pdf` | Copy; retains source identity and dirty edits |
| Word | `.docx` | Save As; rebinds the document and marks serialized content saved |
| Word XML (Flat OPC) | `.xml` | Save As |
| Word 2003 XML | `.xml` | Save As; separate XML writer |
| OpenDocument Text | `.odt` | Save As |
| OpenDocument Text Template | `.ott` | Save As |
| Flat OpenDocument Text | `.fodt` | Save As |
| Rich Text Format | `.rtf` | Save As |
| Web page | `.html` | Copy |
| Markdown | `.md` | Copy |
| LaTeX | `.tex` | Copy |
| Plain text | `.txt` | Copy |
| Page image | `.png` | Copy of the first page |

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
qualification is pending. Existing native font-substitution warnings are outside
this narrowly scoped fix; file-generation smoke checks do not certify every
font or advanced-format feature.
