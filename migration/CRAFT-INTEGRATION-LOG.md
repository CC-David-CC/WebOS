# Craft integration log

Updated: 2026-11-17. This is the running record of the WordCraft integration
and the checklist to assess when integrating another Craft app. It records
existing behavior separately from source changes still being implemented.
Source changes alone do not qualify a built application or a deployed release.

The [general Craft integration guide](CRAFT-INTEGRATION-GUIDE.md) collects the
contracts to assess for the next application. It currently labels WordCraft's
local qualification as passed and hosted qualification as pending; use the evidence below rather than assuming a release.

## Ownership

The Craft app owns its native editable document, undo/redo, selection, codecs,
formatting and serialization. WebOS owns account authentication, account storage
and desktop window placement. Files and the editor use the same Storage service.
The parent composes public component APIs; it does not copy app internals or
maintain another editable document model. Same-origin apps are trusted code.

## WordCraft change register

| ID | Change and reason | Source owner / entry | Current evidence and remaining work |
|---|---|---|---|
| WC-01 | Synchronous `mount` with explicit asynchronous readiness, cancellation and disposal. Allows the existing Desktop to host the real Rust/WASM editor. | [WordCraft adapter](../apps/wordcraft/webos/index.mjs), [parent composition](../assembly/viewer/account-app.mjs) | Local PASS: synchronous mount/ready/cancel/dispose, failure and same-view Retry; hosted pending. |
| WC-02 | Read account files through shared Storage, pass their bytes to the native parser, and retain exact account-relative path plus server SHA-256. A basename alone cannot identify a user file. | WordCraft adapter and Storage public API | Local PASS: full path/server SHA, captions/layout, fresh-context retrieval and current-revision restoration; hosted pending. |
| WC-03 | Identify a save at native serialization with document ID, native revision, operation, completion ticket and whether it saves the document or exports a copy. Posting bytes is not a successful save. | [Native service contract](../apps/wordcraft/crates/ui-egui/src/services.rs), [native command dispatch](../apps/wordcraft/crates/ui-egui/src/app/commands.rs), [Rust browser bridge](../apps/wordcraft/apps/wordcraft-web/src/host.rs) | Native CI and local actual-engine PASS: native serialization tickets, full requested paths and correlated durable outcomes; hosted pending. |
| WC-04 | Confirm durable writes before adopting Save As identity; retain source identity on failure, preserve edits made during a delayed save, and keep exports separate. Return the confirmed canonical path to the native editor. | [Native save settlement](../apps/wordcraft/crates/ui-egui/src/app/files.rs), [completion outcomes](../apps/wordcraft/crates/ui-egui/src/async_saves.rs), WordCraft adapter | Local actual-engine PASS: confirmed canonical identity, collision/conflict/cancel, delayed newer edits, export and response loss after commit; hosted pending. |
| WC-05 | Require explicit caller authority and exact instance/session/document/resource targets for public commands. Capture arguments before asynchronous authorization, and reject a target rebound during the wait. | WordCraft adapter; parent grants the human capability | 23 synthetic-engine host-boundary tests PASS with explicit caller/target and rebind/disposal guards. Human actual-engine workflows pass; delegated-agent transport/authentication remains deferred. |
| WC-06 | Report native document ID, revision, dirty state and pending saves on each state change. A dirty boolean alone cannot identify edits for recovery or detect changes during sign-out confirmation. | Native service contract, [native frame reporting](../apps/wordcraft/crates/ui-egui/src/app/frame.rs), Rust browser bridge | Native CI and local actual-engine PASS: typed/versioned native dirty/revision/pending state feeds Desktop and recovery; hosted pending. |
| WC-07 | Pause native input and command mutations under a matching document/revision lease while the Desktop safely ends a session. Resumption must match the lease. | Native command/control handling and frame input | Local PASS: matching native pause, Cancel/Save/Discard session decisions, and refusal of edits after another view approved close. Text regressions pass; hosted pending. |
| WC-08 | Capture and restore the full native rich document for browser-local crash/refresh recovery; never reduce it to plain text or treat a draft as an account save. | [Native recovery commands](../apps/wordcraft/crates/engine/src/recovery/hosted.rs), engine command registry | Five native recovery/import tests and local rich/media recovery PASS, including quota failure retaining prior committed draft, clean-target protection and minimized-window snapshot liveness; hosted pending. |
| WC-09 | Scope local drafts to issuer/account, order writes and deletion, use a fresh writer identity, and preserve newer edits after a save. Storage mechanics are shared; payload schemas belong to each app. | [Runtime journal](../platform/runtime/src/local-recovery.mjs), [WordCraft codec](../apps/wordcraft/webos/drafts.mjs), [Text codec](../apps/text/webos/drafts.mjs) | Runtime/app journal tests and local named/untitled/orphan/A→B→A recovery PASS; ordered discard/save and late-edit preservation pass. Browser-local durability limitations remain; hosted pending. |
| WC-10 | Opt into Desktop-owned document windows. Native New/Open/Close requests go to the host; opening another file must preserve the current native buffer, undo and selection. Hide/refuse duplicate-view New Window. | Native service/dispatch, native file dialog and ribbon, Rust browser bridge | Local actual-engine PASS: both Open routes reuse the native buffer, selection and undo; minimized/rolled/workspace activation, concurrent initial opens and independent documents pass; hosted pending. |
| WC-11 | Restore account files using confirmed identity, offer retained local drafts, allow Retry for unavailable files, and require Save As when a recovered draft's saved base changed or cannot be verified. | WordCraft adapter, Desktop layout and parent recovery composition | Local PASS: actual current-revision restoration, unavailable-file Retry and changed-base recovery requiring Save As; hosted pending. |
| WC-12 | Remove Discord controls from File, title bar and Help ribbon while retaining About's link. | Native Backstage, chrome, ribbon, keytips and tests | Native tests and actual File/View/Help/About image review PASS: requested controls absent; About link retained. Hosted review pending. |
| WC-13 | Scope native recent filenames and author/UI preferences to the account instead of the browser origin alone. Hosted mode must not fall back to unscoped preferences when its account profile is missing. | Native browser `prefs.rs` / `web.rs`, adapter host profile parameter | Four native preference tests and local actual A→B→A account/profile checks PASS; no hosted fallback to legacy global preferences. Hosted pending. |
| WC-14 | Scope uploaded-font loading, persistence and deletion to the same validated account profile. Preserve legacy unscoped bytes without assigning them to an account. | Native browser `prefs.rs`, `web.rs`, `web/font_store.rs` | Local actual native font load/store/delete and account-switch checks PASS; old unscoped bytes retained unassigned. Browser namespaces are not server sync or a security sandbox. Hosted pending. |

## Build and upstream requirements

Keep upstream-tracking `main` recognizable and WebOS changes on a separate
`webos/...` branch. No upstream PR backlog, language work or external publication
is part of this integration. Generic native fixes belong at their real interface;
WebOS composition belongs near the app's `webos/` entrypoint.

WordCraft's maintained build recipe is [webos/build.py](../apps/wordcraft/webos/build.py).
Earlier build work pins the complete WASM graph, fonts, translations and renderer,
retains notices and uses external disposable outputs. The current native build
uses organized WordCraft source and exact dependency revisions supplied by local
bare Git providers/Cargo cache. Canonical GitHub URLs in Cargo output do not mean
latest upstream was downloaded. The editable shared-library checkout is distinct
from Cargo's checkout of a locked revision.

An updated native interface requires a newly built, source-pinned engine. An old
WASM payload or a synthetic-engine host test cannot qualify it. Required checks
include the app's native quality-gate attempt, native regressions, actual browser
editing/formatting/undo, account-save round trips in a fresh browser context,
failed/conflicting/delayed saves, recovery and session boundaries, activation
through both entrypoints and unchanged Desktop appearance. Compiler outputs
remain outside Git and are disposable.

## Applying this to other Craft apps

| Area | Required assessment for each app |
|---|---|
| Hosting | Real native engine, public mount/readiness/disposal, correct renderer and build inputs. |
| File ownership | Full account-relative identity and saved revision; use shared Storage rather than private authentication or a competing file service. |
| Save completion | Correlate the exact native serialization with durable success, known failure or unknown outcome; distinguish save, Save As and export. |
| Document lifecycle | Native dirty/revision/pending state, unsaved-close protection, session pause and app-appropriate recovery. |
| Native data | Recovery must preserve the app's actual project model and required media. WordCraft's snapshot format is not a universal Craft format. |
| Desktop activation | Decide whether the app edits documents, hosts projects or runs jobs. Where document windows apply, reuse an already-open resource without replacing its live state. Closing a view must not accidentally destroy a shared job/service. |
| Authorized operations | Human and authorized programmatic actions use the same domain implementation with explicit target and permission checks. UI visibility grants no permission. |
| Qualification | Native and actual-engine browser tests for that app's behavior, formats and resource limits. Do not inherit another app's PASS claim. |

The mechanisms may be reusable; these changes should not be blindly copied into
all 17 apps. Shared fixes should move into the appropriate common interface only
after their common boundary is demonstrated. Previous DeckCraft records under
`migration/DECKCRAFT-*.md` are additional historical evidence, not current release
qualification or authority to use their retired assembly commands.

## Running entries

- **2026-11-16 — initial register:** recorded existing hosting/account-save and
  authorization work separately from the current native recovery, lifecycle,
  path-acknowledgement and document-window changes. Shared journal tests: 10 pass.
  Native recovery test build is live; integration acceptance, rebuilt-engine
  checks and deployment for this change are outstanding. Neither beta nor the
  original workspace has been changed by this work.

- **2026-11-16 — host integration source:** connected WordCraft recovery,
  lifecycle/file-binding APIs and account Open routing to the parent and Desktop;
  added account draft discovery and confirmed-path layout/title updates. All 14
  synthetic-engine host-boundary tests now pass, including delayed-save/newer-edit
  rebasing, failed Save As identity, account Open activation and native pause
  dispatch. This is not actual-engine browser acceptance. The first native
  recovery run finished with three tests passing and one failing at its JSON
  representation comparison: `f32` values serialized directly into a JSON Value
  differ numerically from their shortest textual JSON representation. The next
  test must compare the decoded native Document, retaining exact typed model
  equality; the end-to-end recovery test has not passed yet.

- **2026-11-16 — native recovery gate:** the corrected typed-model comparison
  passes. All five native recovery/import tests pass, including rich formatting,
  transactional refusal, password protection and device-import unsaved identity.
  Native UI host regressions are compiling. Seventeen synthetic-engine host
  tests pass; the added cases cover Retry after startup read failure, explicit
  programmatic Save without a dialog, and a native edit invalidating approved
  close. Ordinary close now pauses the actual engine before teardown. The
  actual-engine browser acceptance suite is being prepared and has not run.

- **2026-11-16 — account isolation follow-up:** implemented profile-scoped
  uploaded-font database selection and instance-captured load/store/delete
  callbacks. Hosted editors never fall back to the legacy global font store.
  Existing unscoped stores are retained and are not automatically attributed to
  any account. Native/browser qualification remains outstanding. Backend
  concurrency/fairness changes remain a separate task; shared limits and locks
  were not modified.

## Multi-user readiness review — 2026-11-16

Read-only source review, not a hosted load test. No backend configuration or
service was changed. A browser-global key affects accounts sharing that browser
profile; it is not a single server-wide value shared by everybody.

| Finding | Consequence | Priority / next evidence |
|---|---|---|
| Historical finding, fixed locally by WC-14: WordCraft uploaded fonts used one IndexedDB database/store (`wordcraft` / `fonts`), and `load_all` reads every stored font. | Account B on the same browser profile inherits Account A's uploaded fonts/names; deleting a stored font is also unscoped. Separate browsers do not share this database. | Account isolation gap. Needs account-scoped font storage/loading and an A→B regression before claiming shared-browser isolation. Not fixed by the preference-key change. Source: [font_store.rs](../apps/wordcraft/apps/wordcraft-web/src/web/font_store.rs). |
| Storage uses one `.storage.lock` across account homes. Reads hash under that lock; saves check the previous content, walk storage usage, write and fsync while holding it. | Large files or many stored entries can delay other accounts even though transfers have separate concurrency slots. The lock also protects real atomicity/quota invariants and cannot simply be removed. | Shared-service contention to measure with concurrent users and large/small-file mixtures. Any fix needs narrower locking/accounting while retaining conflict, quota and atomic-write checks. Source: [user_store.py](../platform/storage/src/webos_storage/user_store.py). |
| File gateway request admission, transfer slots, bandwidth and daily totals have shared service limits. Request admission occurs before account authentication. | Bursty or abusive traffic can consume shared capacity and delay/reject otherwise independent users. Per-account transfer quotas alone do not prove fairness. | Record actual deployment settings and measure busy-account impact on another account. The local runner sets 4096 requests/minute and 8/account,16/shared transfer slots; these are configuration values, not a proven user capacity. Source: [http.py](../platform/storage/src/webos_storage/http.py), [transfers.py](../platform/storage/src/webos_storage/transfers.py), [runner](../scripts/run_development.py). |
| Local server defaults set 1 GiB/account and 10 GiB across account files, independently of available disk. | Saves can hit an intentional service quota while the disk still has free space. This is not a per-app build-size limit. | Capacity-policy decision; inspect actual deployed settings before claiming live headroom. Source: `UserStore.__init__`, local runner. |
| Every document window hosts a separate native WASM editor. Rich checkpoints serialize a full document. | Multiple large documents may exhaust one user's browser memory or make recovery expensive. This is primarily client capacity, not shared server rendering. | Measure actual browser memory, recovery latency and hidden/minimized-window behavior with realistic documents. Artifact byte size does not establish runtime RAM or a user limit. |
| No concurrent multi-user capacity test has qualified this new integration. | Separate functional browser tests cannot justify a promise about five or ten simultaneous users. | After document correctness, test independent accounts concurrently, including one busy account, overlapping writes, uploads, refresh/recovery and account boundaries. |

The reviewed server paths derive private homes from the authenticated principal,
check permissions, and require a prior SHA-256 for replacement. Recovery journals
are issuer/account-scoped; Desktop layouts are issuer/account-scoped. Accounts
stores one deliberately active browser-profile session per issuer/API scope and
guards against an old tab deleting a newer record. Those are different from an
unscoped recent-file or uploaded-font store. These observations do not replace
adversarial isolation tests or a complete security review.

- **2026-11-16 — native host gate:** 30 native UI host tests and 68 current JavaScript regressions pass. Remaining native profile/community checks, the full CI attempt, a fresh WASM artifact, actual-engine acceptance and scoped rollout remain outstanding. Browser suites are prepared for documents, rich recovery and account-specific actual font storage. No backend changes or new deployment have occurred.

- **2026-11-16 — current native recovery:** all five recovery/import tests pass after the canonical source-path change. The About retention test passes. The first Help test failed because custom-painted ribbon buttons do not expose the queried AccessKit labels; the revised test inspects actual painted text and requires visible Commands content. Current browser suites also include failed recovery storage, lost layout/orphan discovery, Save As cancellation, concurrent activation and PDF copy identity; these suites remain unrun.

- **2026-11-16 — startup recovery review:** found and fixed the native UI guard that rejected recovery when no document was open; recovery must itself open a document. Added a control-channel regression for hosted empty-startup recovery. Also refuse restore over UI-owned unconfirmed saves/comment drafts, which the engine-only clean-revision check cannot observe. These two new regressions require the next native host run; the earlier30-pass result does not qualify these later changes.

- **2026-11-16 — current native quality:** recovery/import5, preference4, About1, Help1 and the34-case host run pass. One newly added test initially misused an intentionally dirty fixture; the corrected setup saves and acknowledges it before the pending Save As scenario, retaining the refusal/identity assertions. CI found added dispatcher complexity33/30, then32/30; window-level admission and save/export serialization now have cohesive methods, without lowering lint thresholds. Current full CI passes formatting and full Clippy, and compiles workspace tests. The method extraction still needs current-source test results. No new WASM artifact or deployment exists yet.

- **2026-11-16 — continuation and backend fidelity:** the handoff brief now labels its original migration assignment historical and points to this active task's private checkpoint. Original brief bytes were preserved privately. Comparing10 organized Accounts Python modules with the retained backend fixture found8 identical modules and differences in delegation.py / policy_service.py, corresponding to existing separate delegation/policy work. Browser qualification will use the retained backend fixture; this task does not roll out that newer backend policy source.

- **2026-11-16 — full native suite regression:** full CI passed formatting and
  Clippy, then exposed one introduced UI failure: a refused protected-comment
  draft prevented saving the accepted document. The UI suite reported1262 passed,
  one failed and three ignored; later CI stages were skipped. Save/export now
  retain the refused draft and its status while saving accepted document content,
  preserving existing behavior. The original test remains; an added programmatic
  regression also checks saved bytes and host dirty-state protection of the draft.
  The next full CI run is in progress. This is not a pre-existing failure or a
  completed browser qualification. No new engine artifact or rollout exists yet.

- **2026-11-16 — complete native gate:** the corrected source passes all nine
  `cargo xtask ci` stages: formatting, Clippy, native workspace tests, interface
  audit, language, doctests, assets, layering and the14-crate WASM check. Engine1468
  and UI1264 tests pass. Both the original refused-comment Save regression and
  the added programmatic Save/host-dirty regression pass. The new test initially
  referenced the wrong typed report field; it now inspects the active document
  within `HostDocumentState.documents`. No assertion or lint threshold was lowered.
  Two WASM warnings remain in unchanged native source. A complete browser artifact,
  actual-engine acceptance and rollout are still pending.

- **2026-11-16 — browser coverage review:** while the source-pinned browser build
  runs, extended actual-engine acceptance to cover a lost response after a
  committed Save As and dirty WordCraft session-end Cancel/Save/Discard. The
  response fault must demonstrate committed server bytes, unchanged prior binding,
  retained dirty content, an explicit unknown outcome and no automatic retry.
  Session tests must retain both drafts when one Discard is followed by Cancel,
  confirm both saves before logout, and clear only explicitly discarded drafts.
  The earlier waiting acceptance driver was stopped before creating any fixture
  or browser; the new driver preserves the same engine build and captures the
  updated test sources. Prepared counts are19 document,14 recovery/session,
  five account-profile and53 existing regression checks; these remain unrun.

- **2026-11-16 — fresh browser engine and local document gate:** the complete
  offline source-pinned browser build succeeds at WordCraft
  `fbc4bb73fbc177c9adcfbb705c9a9a05212a7ae9` (27 files,92,652,321 bytes).
  The19-case actual document suite now passes, including keyboard Save/Save As,
  native/caption/layout binding, both Open routes, preserved selection/undo,
  independent documents, concurrent independent Files launchers, PDF copies,
  conflicts, delayed newer edits, current-revision restoration, same-view Retry
  and an unknown outcome after an actual committed write. The injected transport
  failure is correlated by its exact CDP Network request identity; other global
  cancellation diagnostics are retained separately. Console/page/HTTP assertions
  remain strict. Earlier harness failures are retained: long temporary socket
  path, asynchronous Files mounting, wrong Save As shortcut, missing public editor
  focus, single-view Files busy protection and an invalid assumption about the
  scrubbed Desktop session projection. These required test corrections, not app
  rewrites or weaker behavior assertions. No app source changed after the clean
  engine commit. Actual File/View/Help/About images were read: requested Discord
  controls are absent and About's link remains. Rich recovery's first11 checks
  also pass; session-end cases, account fonts, existing regressions and hosted
  qualification remain outstanding. No new deployment has occurred.

- **2026-11-17 — all local gates passed:** WordCraft source
  `fbc4bb73fbc177c9adcfbb705c9a9a05212a7ae9` passes all nine native CI stages,
  including 4,989 tests (eight pre-existing ignored), and its fresh complete
  27-file pinned WASM engine was built offline. All 68 JavaScript tests pass.
  The current exact candidate passes 92 actual-browser checks: documents 19,
  recovery/session 15, profile/fonts five, login seven, Text activation 11,
  Text binding nine, Text recovery 11 and viewer/Files/Calculator 15. The earlier
  failed receipts remain preserved; current counts select the final successful
  suite receipts against unchanged source hashes. Actual screenshots were read.
  Desktop `1e0a94ffcfc54fd06fd1b2b958377303d48fdf82` fixes a duplicate legacy
  session warning after native close approval and refuses later edits before
  revocation. WordCraft's accepted local `webos/integration` branch was
  fast-forwarded to the tested source; upstream `main` stayed unchanged.
  Hosted rollout/qualification and final handoff remain pending. Backend, beta,
  Desktop styling and the original workspace have not changed.
