# WordCraft Design, fonts and account defaults

Status: 2026-11-17 UTC — native, fresh WASM and all 20 focused local
browser checks pass; static rollout and hosted acceptance are pending. ksu.codes still serves the prior
[document-integration release](WORDCRAFT-DOCUMENTS.md).

The maintained WordCraft source is `e5446e6058e2ad8fefd1b5d0fc455602fdf7f4a5`
on `webos/design-presets-fonts`. Upstream-tracking `main` is unchanged. This
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
| Scoped static release and hosted checks | Pending |

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
The final release identity, packaged parent commit, static operator tag and
rollback plan will be recorded after actual artifact qualification.
