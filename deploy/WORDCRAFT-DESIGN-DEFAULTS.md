# WordCraft Design, fonts and account defaults

Status: 2026-11-17 UTC — deployed to https://ksu.codes. All nine native CI stages,
36 WordCraft JavaScript tests and 20 actual-browser checks each locally and over
hosted HTTPS pass. Actual local and hosted screenshots were inspected.

The maintained WordCraft source is `e5446e6058e2ad8fefd1b5d0fc455602fdf7f4a5`
is accepted on `webos/integration`; the reviewed feature branch is retained.
Upstream-tracking `main` is unchanged. This
follow-up adds three related corrections:

- Shaded headings retain white text on the theme accent, including when colors
  change. The native command updates the background rather than overwriting the
  foreground with the same color. Existing saved formatting is not silently
  rewritten; reapplying Shaded repairs a heading saved with the earlier defect.
- Home, recent-font suggestions and Design Fonts offer actual loaded families,
  including current-account uploads. Existing/imported font requests remain
  truthful in the current-font field and substitution warning. The browser
  package includes the existing Source Sans 3, Source Serif 4, Inter and JetBrains
  Mono license notices alongside pinned craft-fonts notices. No new proprietary
  font is added. Theme presets and document font requests are not substituted
  automatically merely because their requested family is unavailable.
- Design → Set as Default writes native style definitions, default character/
  paragraph properties, theme fonts and theme colors through the current
  authenticated account-file capability to
  `Digital Projects/WordCraft/defaults-v1.json`. Blank New reads that server record.
  Existing files, imports, explicit templates and recovered drafts retain their
  formatting. Defaults contain no document body, sections, headers, comments,
  credentials or save identity; tracked style-edit history is excluded.

Defaults use a versioned schema capped at 256 KiB and 512 styles. Writes use
revision preconditions and require a server-confirmed result. Conflicts, failed
or uncertain writes are explicit. A failed native status update cannot relabel
a confirmed account write as a failure. Absent settings use built-ins; an
unavailable or corrupt existing record produces Retry instead of a global or
guessed-account fallback. Blank New does not create folders; an explicit defaults
save can create its missing settings path, while file collisions are preserved.
Closing or refreshing the source document never substitutes for saving that
document: storing defaults leaves its dirty state and file binding intact.

| Gate | Result |
|---|---|
| Native CI | All nine stages PASS: fmt, Clippy, tests, i18n report, language, doctests, assets, layers, WASM compatibility |
| Native test phase | 4,996 passed, zero failed, eight pre-existing ignored |
| WordCraft JavaScript regressions | 36 PASS; synthetic-engine host tests explicitly distinguished |
| Fresh pinned browser engine | PASS: 31 files, 92,629,674 bytes; complete development-profile graph |
| Actual local browser checks | PASS: six Design, nine defaults/associations/shared-wrapper cases, five profile/font cases |
| Actual local screenshots | PASS: Shaded, centered, available fonts, fresh-browser defaults, Python/CM6 and classic viewer |
| Scoped static release and hosted checks | PASS: exact release; six Design, nine defaults/associations/shared-wrapper and five profile/font checks |

The native defaults regressions cover session restoration, blank-only
application, unchanged loaded DOCX and recovered models, invalid/oversized
records and atomic refusal. Native UI tests cover actual available font choices,
keyboard autocomplete and host-routed default-save requests. The Shaded
regression failed on the actual original contrast assertion before the fix.
Earlier CI failures remain in private evidence: one oversized command handler
was factored without suppressing the guard; one autocomplete fixture relied on
an unavailable injected Aptos Display entry and now uses bundled Source Serif 4
with the keyboard and style assertions retained.

Desktop, Runtime, Files, Text and Storage source/pins are unchanged. Parent
account-app composition adds `.dotx` to WordCraft routing; `.txt` and `.py` already
route to CodeMirror 6 Text, with Python syntax support. Actual Files-to-editor
checks pass for all three, using a real `.dotx` produced by the native codec.
The common composition wrapper is bundled into Calculator, Files, Text and
WordCraft, so Calculator mounting/calculation is checked too. Unrelated feature
suites are not repeated. Previous release results remain
historical evidence and are not relabeled as tests of this artifact.

Server-backed defaults synchronize formatting names and definitions. Uploaded
font bytes still use their separate account-scoped browser store; saving a family
name does not synchronize those bytes across machines. Native/headless Set as
Default remains session-local outside the WebOS host and reports that truthfully.
This is not a full Normal-template/content/layout manager or a capacity benchmark.
Delegated-agent authentication and the independent Login component remain separate.

The [Craft guide](../migration/CRAFT-INTEGRATION-GUIDE.md) and
[running log](../migration/CRAFT-INTEGRATION-LOG.md) describe the reusable boundaries.

## Release and rollback

| Item | Identity |
|---|---|
| Packaged parent source | `239d958648c626b3e861ef946b62a88fa088f3f1` |
| WordCraft | `e5446e6058e2ad8fefd1b5d0fc455602fdf7f4a5` |
| Public release | `d7a8f6ae73223079e78013d5f7b3aae01ff8716758b1c14d969f5c22e0ff698b` |
| Archive SHA-256 | `647c5cc23de55abe841d0310d07c08fcfc49fc94fe5a947e7b1f702b8f7b3c3d` |
| Previous release | `86457f2da2b3b9ed0e6b57ed76fdd17ad114d42237554604fe0d72bee1e50716` |
| Static operator tag | `wordcraft-design-defaults-20261117-01` |

The archive contains 249 public files totaling 98,067,136 bytes; compressed size
is 28,311,081 bytes. All 96 JavaScript packages have notices. File hashes and
source inputs were verified. Payload comparison permits the native WordCraft
namespace, shared account-app wrapper bundles and their expected manifests;
Desktop CSS/artwork and other payloads remain byte-identical. Only the parent
assembly and WordCraft component identities changed. The complete development
profile is functionally qualified; optimized-release performance is separate.

The active root is
`/srv/data/webos-viewer-releases/d7a8f6ae73223079e78013d5f7b3aae01ff8716758b1c14d969f5c22e0ff698b/public`
on the verified example.invalid. The reviewed [static operator](viewer_static_operator.py)
changed only the ksu.codes static root and reloaded Caddy. Backend instance,
issuer, beta index hash and all six checked service PIDs are unchanged. Existing
account data and service configuration were retained; browser checks created
only their own synthetic accounts/documents. Login deadlines and transfer limits
remain unchanged. No external Git publication occurred.

The exact rollback plan is
`/var/backups/webos-wordcraft-design-defaults-20261117-01/`; the previous public
root remains available. From this parent source directory, the matching guarded
rollback command is:

```bash
ssh -o BatchMode=yes example.invalid sudo -n python3 - rollback \
  --tag wordcraft-design-defaults-20261117-01 \
  --release d7a8f6ae73223079e78013d5f7b3aae01ff8716758b1c14d969f5c22e0ff698b \
  < deploy/viewer_static_operator.py
```

This records the completed rollout and its recovery path; it grants no authority
for additional changes. Use this tag for this release rather than the older
WordCraft-documents tag.

## Evidence and retained build state

Private evidence/checkpoint is
`/path/to/workspace/Projects/.webos-migration/wordcraft-design-20261117-8hxd9044/`.
Selected hosted runs are Design1, Defaults1 and Profile4; all selected commands
exit zero with zero unexpected browser errors. The first profile run passed its
five functional cases but failed the strict console gate on Chromium
`ERR_CERT_VERIFIER_CHANGED`. Unchanged retries passed; collector/process-group
receipts and all earlier failures remain. Guards and certificate validation were
not relaxed. The initial local defaults harness clicked before asynchronous
folder listing completed; its wait was corrected and the same candidate bytes
passed. None of these harness corrections required a new engine or release.

Disposable engine/candidate/browser trees (22 directories, approximately 503 MB
logical contents), superseded local release archive and uploaded staging archive
were removed after verification. Source, required font/translation inputs,
receipts, screenshots and the current final archive remain. Per the user's
explicit decision, exactly one current compiler cache is retained through this
WordCraft QA round (8,676,677,116 logical bytes); remove it when that round ends.
Existing unrelated working files remain untouched.
