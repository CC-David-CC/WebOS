# Integrating a Craft application into WebOS

Status: WordCraft passes local and hosted qualification and is deployed to ksu.codes.
The [running integration log](CRAFT-INTEGRATION-LOG.md) records changes and
historical failures. The [document integration report](../deploy/WORDCRAFT-DOCUMENTS.md)
records selected commits, the exact release, rollback and limits. This guide does
not grant another application WordCraft's results or authorize deployment.

WordCraft `fbc4bb73fbc177c9adcfbb705c9a9a05212a7ae9` passes all nine native CI
stages, including 4,989 native tests (eight pre-existing ignored). Its fresh,
complete pinned browser artifact passes 92 actual-engine/local regression checks:
19 documents, 15 recovery/session, five profile/fonts, seven login persistence,
11 Text activation, nine Text binding, 11 Text recovery and 15 viewer/Files/
Calculator checks. Another 68 JavaScript tests pass; their synthetic-engine
fixtures are not substitutes for the actual-engine checks. Actual screenshots
were inspected for the classic viewer and requested Discord controls. The same 92 checks pass over hosted HTTPS against the exact selected release;
hosted native and Desktop screenshots were inspected.

Work from the organized sources in `apps/`, `platform/`, `engines/`, `libraries/`,
`assets/` and `tooling/`. Preserve the existing Desktop implementation in
`platform/desktop/active-system/`. Source organization is complete; restarting
extraction, copying beta or replacing the viewer is not the next task. The
[app matrix](APP-MATRIX.md), [source catalog](SOURCE-CATALOG.md) and
[upstream map](CRAFT-UPSTREAMS.json) identify the independent owners and inputs.

## Ownership and boundaries

| Owner | Responsibility |
|---|---|
| Craft application | Native editable model, document/project identity, undo, selection, codecs, serialization and app-specific recovery payload. |
| Runtime | Shared lifecycle and ordered local-journal mechanics; no second editable model. |
| Desktop | Window placement, focus, workspace, captions, restoration and activation of an already-open resource. |
| Accounts | Authentication, principal/session identity and authorization. An app does not authenticate itself. |
| Storage | Account-relative resources, server revisions, conditional writes and durable confirmation. |
| Files | Human file operations and launching through the same account Storage interface. |
| Parent assembly | Public API composition, selected Git links, whole-system tests and separately authorized releases. |

Repository separation establishes source ownership. Same-origin applications are
trusted code, not mutually isolated security compartments. Independently owned
client/server source does not require a fleet of separately deployed services.

## Hosting and identity

Retain synchronous `mount(host) -> { element, dispose }`. Opening may be
asynchronous: expose readiness, failure, cancellation and disposal explicitly.
An unavailable account file retains its intended identity and offers Retry in
the same view; it must not become an apparently successful empty document.

Keep these identities distinct:

| Identity | Meaning |
|---|---|
| Issuer and account | Owner of account resources and account-scoped local state. |
| Instance and session | Exact live app/capability target. |
| Native document/project ID | Native editable object inside that instance. |
| Native revision | In-memory state being inspected, captured or saved. |
| Full account-relative path | Account resource; a basename is insufficient. |
| Saved server SHA-256 | Revision of confirmed saved bytes, independent of native revision. |

WordCraft opts into Desktop-owned document windows. Files and WordCraft's own
account Open both activate an already-open resource, retaining its native buffer,
selection and undo. Reserve resource identity while opening so concurrent Opens
cannot create duplicate editors. Different documents and untitled documents get
independent windows. There is no duplicate-view New Window option in this mode.
Assess project/job applications separately: closing a view must not destroy an
independently running job or shared service.

## Save, Save As and export

Capture native document ID, revision, operation and completion ticket at
serialization. Send the actual serialized bytes through shared Storage.
Posting a message or starting an HTTP request does not confirm a save.

Use the saved server revision for replacement; use create-only semantics for a
new destination. After durable success, return the confirmed canonical path to
the native editor, then publish the new binding to Desktop captions and layout.
A failed Save As retains the previous identity. Edits after serialization remain
dirty even when the earlier save succeeds. Out-of-order replies cannot overwrite
a later confirmed path. Export writes a copy without rebinding or marking newer
document content saved.

Distinguish known failure from unknown outcome. A timeout may occur after the
server committed bytes; do not silently retry an unconditional overwrite or
announce success. Test conflict, collision, cancellation, delayed acknowledgement,
newer edits and ordinary keyboard Save as well as programmatic commands.

## Unsaved work and recovery

Expose native dirty/revision/pending-save state to the host. Before closing or
ending a session, coordinate Save/Discard/Cancel and recheck the exact state under
a matching native pause lease. Host UI visibility alone does not freeze edits.

Recovery payloads belong to the app. WordCraft snapshots its native rich model,
including styles, lists and embedded media; plaintext is not an adequate recovery
format. Runtime supplies ordered journal writes/removal, fresh writer identities
and generation checks. Scope records by issuer/account and app schema, discover
orphan drafts even when window layout is missing, and preserve the prior committed
checkpoint if a new write fails. A changed or unverifiable saved base requires
Save As rather than overwriting newer server content.

Recovery restores the last successfully committed browser-local checkpoint. It
does not promise zero-loss power failure, immunity to storage eviction, or native
undo-stack/session reconstruction. Scheduling intervals are not durability
guarantees. WordCraft snapshots cross its existing native comment-flush boundary;
all unfinished UI/IME/dialog states are not exhaustively qualified. Protected
documents refuse plaintext checkpoints. Version and test model compatibility
when merging upstream; WordCraft's native JSON is not a universal Craft schema.

## Account state and authorized operations

Scope recent paths, preferences and uploaded fonts to the validated account
profile. Hosted mode must not fall back to global state when that profile is
missing. Retain old unscoped stores without guessing their owner. Test A to B to A
in the same browser profile, including actual font loading and deletion.
Account-namespaced browser settings/fonts are not server synchronization across
machines and are not a barrier against trusted same-origin code.

Human, test and authorized agent actions must reach the same native/domain
operations. Public execution requires an explicit caller and exact target tuple.
Capture bounded arguments before asynchronous authorization; refuse execution if
the instance, session, document or resource changes during the wait. Never expose
authentication secrets in ordinary inspection. Current human mount authority is
not delegated-agent authentication; that separate transport remains deferred.

## Builds, upstream maintenance and evidence

Keep upstream-tracking `main`/`master` separate from `webos/...` branches. Review
upstream merges on a review branch, qualify the resulting fork, then promote an
explicit component commit and parent pin. Fetching upstream does not authorize
merging, changing parent pins or publishing. Never push to upstream.

Use each app's real recipe and locked dependency graph. WordCraft's entry is
`apps/wordcraft/webos/build.py`; it requires pinned fonts/translations and records
toolchain, source, dependency and artifact hashes. Cargo can use a canonical
GitHub source identifier while resolving that exact revision from a local bare
provider/cache. That differs from both downloading current HEAD and compiling an
editable shared-library checkout.

Keep one owned disposable build cache outside source and public roots. Check disk
capacity first. Never commit compiler outputs, private profiles, account state,
credentials or raw recovery material. Required inputs and licensed runtime
payloads are distinct from intermediate builds. No arbitrary 1 GiB app-suite
budget follows from account-file quotas.

Record each gate separately:

1. Source inventory and independent ownership.
2. Native quality gates and meaningful regression tests; retain actual failures.
3. Adapter tests, explicitly identifying synthetic engine fixtures.
4. Fresh source-pinned complete browser engine, with required inputs and notices.
5. Actual-engine browser authoring, file round trips, faults, recovery, activation,
   account boundaries and existing Desktop/Text/Files/Login regressions.
6. Visual inspection of actual screenshots; a build is not a fidelity test.
7. Separately authorized scoped hosted checks, exact release and rollback record.

Fresh browser contexts demonstrate server-backed retrieval, not a physical
second-machine test or all-format parity. Do not reuse an old WASM payload or old
PASS count to qualify a changed native protocol. Local bare Git copies preserve
commits locally; they are not an off-machine backup.

## Choosing the next task

All 17 selected Craft sources are organized. WordCraft is the current integration
target; the other 16 do not inherit its qualification. Historical DeckCraft work
is evidence, not a qualified current-viewer release.

| Candidate family | Assess before selecting |
|---|---|
| GridCraft, DeckCraft, PdfCraft | Native document identity, formats, recovery and actual browser/host protocol. Likely to exercise the document contract, but inspect each implementation. |
| PhotoCraft, VectorCraft, DesignCraft, FigCraft | Media/resource graphs, fonts, linked assets, project recovery and memory footprint. |
| AniCraft, FilmCraft, EffectCraft, SoundCraft, LightCraft | Media size, streaming/cache needs, long-running work and view/job lifetime. |
| CADCraft, SolidCraft, TextureCraft, MaterialCraft | Native project/engine dependencies, renderer, linked assets and serialization/recovery. SolidCraft has a distinct community upstream. |

Files, Accounts, Storage and Runtime reliability outrank adding games or another
editor for functional WebOS. Each account already has a separate server home;
Storage still has a shared critical section containing scans/hashing/writes.
Measure contention before narrowing locks, retaining conditional-write, atomicity
and quota guarantees. Shared admission/transfer fairness, multi-user capacity and
per-document browser memory remain unqualified. The organized Accounts source
also includes separate delegation/policy work beyond the retained deployed
backend; do not accidentally deploy it during a static frontend release.

With WordCraft qualified, choose explicitly between another Craft app and
these platform gaps. Do not turn that choice into an automatic whole-catalog
build, backend rewrite, upstream PR cleanup or beta-parity project.

## Browser qualification lessons from WordCraft

Use the app's registered keyboard shortcuts (WordCraft's non-macOS Save As is
F12), await asynchronous mount and public readiness, and call the editor's public
focus operation after activating its Desktop window. Run concurrent opening tests
through two independent Files instances; one Files view intentionally rejects
overlapping operations while busy. Test minimized native snapshot liveness after
minimizing, rather than accepting a checkpoint captured while visible.

When injecting a lost save response, correlate the exact request after the server
commits; unrelated cancelled network requests are not proof of the injected fault.
Assert user-visible handled errors and unchanged account bytes without requiring
a console error that the implementation does not emit. Keep strict unexpected
console/page/HTTP assertions. Recovery dialogs use the browser's actual top layer;
focus is not proof of which modal is visible. Use short owned browser temporary
paths to stay within Linux Unix-socket limits. Retain failed receipts and explain
harness corrections rather than rewriting their results as passes.

Desktop records each view's exact approved lifecycle state while collecting
Save/Discard/Cancel decisions, and rechecks it before revoking authentication.
A later edit invalidates the earlier approval. Publicly approved views do not
receive a second legacy warning; views without this lifecycle contract retain
the legacy check. This contract is shared with Text and is not app-specific UI.
