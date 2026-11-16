# Reviewed host templates and Microduck policy ownership

Three additional source records are organized with their proper owners:

| Owner | Preserved source | New location |
|---|---|---|
| Parent deployment | `beta_service_operator.py` | `deploy/legacy-backend/isolated-hosting/` |
| Parent deployment | `beta_signed_probe.py` | `deploy/legacy-backend/isolated-hosting/` |
| Microduck | `microduck_hosting.py` | `apps/microduck/legacy/hosting/` |

The first two files were held by the initial bounded credential scanner. Exact
AST/context review resolves those markers: a systemd `LoadCredential` expression
constructs a credential-file reference from a supplied configuration path; the
signed probe constructs a `Codi-File` header from a runtime grant and signature.
Neither flagged expression supplies fixed credential bytes. Each complete
selected file history has one source addition. The exact reviewed expressions
are approved only for these source blobs, with the remaining source independently
screened. The scanner itself and all source bodies are unchanged; no general
credential-pattern exception was introduced. Actual credential files, grants,
tokens, account state and keys were not copied or logged.

Microduck's profile validation and document/frame hosting policy belong to its
independent component. Parent-owned host operators remain deployment composition;
the app-specific source is not duplicated there. This changes the Microduck pin
for inactive source/documentation only. Its existing200-pass/11-missing-fixture
baseline and broader browser/host qualification remain unchanged and OPEN.

Source-only mechanical commits precede documentation. All three bodies/Git modes
match capture, scoped original index/working bytes and self-contained recovery;
original/recovery filesystem permissions match. Independent extracted repositories
pass integrity checks, selected-path tree and author/committer/message checks.
All three files parse and restored offline with the old workspace and assembly
hidden. No operator or module was imported/executed or enabled as an entrypoint.

Path-limited full-history export initially retained unrelated empty merge
metadata. Fresh separate targets explicitly pruned empty/degenerate commits while
preserving the complete one-addition history for each source. Earlier private
review targets remain preserved; no accepted history was rewritten. Source,
commit and exact context maps, commands and exit codes remain in private phase84.

Required configuration/manifests and public-interface/side-effect/authority ports
remain unqualified. Do not install services or use historical host locators.
Microduck policy remains inactive pending actual browser/asset/frame qualification.
This is preservation, not functional or complete external-publication clearance.

Tracked-source reconciliation now has1,830 unresolved dispositions. That is not
a missing-file count, completion percentage or app-support claim. Only Microduck's
source pin changes; all other123 component pins, runtime and existing deployment
remain unchanged.
