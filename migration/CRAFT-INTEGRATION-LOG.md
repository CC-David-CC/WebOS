# Craft integration log

Updated: 2026-11-17. The [general Craft guide](CRAFT-INTEGRATION-GUIDE.md)
records the common host contract. WordCraft and PdfCraft now have deployed
integrations; each focused report retains its exact source, artifact, tests and
limits. This log distinguishes source changes from qualification and deployment.

PdfCraft follow-up is complete and deployed: clean untouched hosted blank,
explicit blank Save and top-right Discord removal with About/community/credits
preserved. Native gates,27 browser assertions each locally/hosted and10 local/11
hosted saved-PDF checks pass. The shared guide and
[two app branch plans](CRAFT-BRANCH-PLANS.md) are complete; neither next app has
started implementation. Existing local app sources remain the starting points; no fresh app copies are needed.

## Ownership

The Craft app owns its native editable document, undo/redo, selection, codecs,
formatting and serialization. WebOS owns account authentication, account storage
and desktop window placement. Files and the editor use the same Storage service.
The parent composes public component APIs; it does not copy app internals or
maintain another editable document model. Same-origin apps are trusted code.

## WordCraft change register

| ID | Change and reason | Source owner / entry | Current evidence and remaining work |
|---|---|---|---|
| WC-01 | Synchronous `mount` with explicit asynchronous readiness, cancellation and disposal. Allows the existing Desktop to host the real Rust/WASM editor. | [WordCraft adapter](../apps/wordcraft/webos/index.mjs), [parent composition](../assembly/viewer/account-app.mjs) | Local PASS: synchronous mount/ready/cancel/dispose, failure and same-view Retry; hosted PASS. |
| WC-02 | Read account files through shared Storage, pass their bytes to the native parser, and retain exact account-relative path plus server SHA-256. A basename alone cannot identify a user file. | WordCraft adapter and Storage public API | Local PASS: full path/server SHA, captions/layout, fresh-context retrieval and current-revision restoration; hosted PASS. |
| WC-03 | Identify a save at native serialization with document ID, native revision, operation, completion ticket and whether it saves the document or exports a copy. Posting bytes is not a successful save. | [Native service contract](../apps/wordcraft/crates/ui-egui/src/services.rs), [native command dispatch](../apps/wordcraft/crates/ui-egui/src/app/commands.rs), [Rust browser bridge](../apps/wordcraft/apps/wordcraft-web/src/host.rs) | Native CI and local actual-engine PASS: native serialization tickets, full requested paths and correlated durable outcomes; hosted PASS. |
| WC-04 | Confirm durable writes before adopting Save As identity; retain source identity on failure, preserve edits made during a delayed save, and keep exports separate. Return the confirmed canonical path to the native editor. | [Native save settlement](../apps/wordcraft/crates/ui-egui/src/app/files.rs), [completion outcomes](../apps/wordcraft/crates/ui-egui/src/async_saves.rs), WordCraft adapter | Local actual-engine PASS: confirmed canonical identity, collision/conflict/cancel, delayed newer edits, export and response loss after commit; hosted PASS. |
| WC-05 | Require explicit caller authority and exact instance/session/document/resource targets for public commands. Capture arguments before asynchronous authorization, and reject a target rebound during the wait. | WordCraft adapter; parent grants the human capability | 23 synthetic-engine host-boundary tests PASS with explicit caller/target and rebind/disposal guards. Human actual-engine workflows pass; delegated-agent transport/authentication remains deferred. |
| WC-06 | Report native document ID, revision, dirty state and pending saves on each state change. A dirty boolean alone cannot identify edits for recovery or detect changes during sign-out confirmation. | Native service contract, [native frame reporting](../apps/wordcraft/crates/ui-egui/src/app/frame.rs), Rust browser bridge | Native CI and local actual-engine PASS: typed/versioned native dirty/revision/pending state feeds Desktop and recovery; hosted PASS. |
| WC-07 | Pause native input and command mutations under a matching document/revision lease while the Desktop safely ends a session. Resumption must match the lease. | Native command/control handling and frame input | Local PASS: matching native pause, Cancel/Save/Discard session decisions, and refusal of edits after another view approved close. Text regressions pass; hosted PASS. |
| WC-08 | Capture and restore the full native rich document for browser-local crash/refresh recovery; never reduce it to plain text or treat a draft as an account save. | [Native recovery commands](../apps/wordcraft/crates/engine/src/recovery/hosted.rs), engine command registry | Five native recovery/import tests and local rich/media recovery PASS, including quota failure retaining prior committed draft, clean-target protection and minimized-window snapshot liveness; hosted PASS. |
| WC-09 | Scope local drafts to issuer/account, order writes and deletion, use a fresh writer identity, and preserve newer edits after a save. Storage mechanics are shared; payload schemas belong to each app. | [Runtime journal](../platform/runtime/src/local-recovery.mjs), [WordCraft codec](../apps/wordcraft/webos/drafts.mjs), [Text codec](../apps/text/webos/drafts.mjs) | Runtime/app journal tests and local named/untitled/orphan/A→B→A recovery PASS; ordered discard/save and late-edit preservation pass. Browser-local durability limitations remain; hosted PASS. |
| WC-10 | Opt into Desktop-owned document windows. Native New/Open/Close requests go to the host; opening another file must preserve the current native buffer, undo and selection. Hide/refuse duplicate-view New Window. | Native service/dispatch, native file dialog and ribbon, Rust browser bridge | Local actual-engine PASS: both Open routes reuse the native buffer, selection and undo; minimized/rolled/workspace activation, concurrent initial opens and independent documents pass; hosted PASS. |
| WC-11 | Restore account files using confirmed identity, offer retained local drafts, allow Retry for unavailable files, and require Save As when a recovered draft's saved base changed or cannot be verified. | WordCraft adapter, Desktop layout and parent recovery composition | Local PASS: actual current-revision restoration, unavailable-file Retry and changed-base recovery requiring Save As; hosted PASS. |
| WC-12 | Remove Discord controls from File, title bar and Help ribbon while retaining About's link. | Native Backstage, chrome, ribbon, keytips and tests | Native tests and actual File/View/Help/About image review PASS: requested controls absent; About link retained. Hosted image review PASS. |
| WC-13 | Scope native recent filenames and author/UI preferences to the account instead of the browser origin alone. Hosted mode must not fall back to unscoped preferences when its account profile is missing. | Native browser `prefs.rs` / `web.rs`, adapter host profile parameter | Four native preference tests and local actual A→B→A account/profile checks PASS; no hosted fallback to legacy global preferences. Hosted PASS. |
| WC-14 | Scope uploaded-font loading, persistence and deletion to the same validated account profile. Preserve legacy unscoped bytes without assigning them to an account. | Native browser `prefs.rs`, `web.rs`, `web/font_store.rs` | Local actual native font load/store/delete and account-switch checks PASS; old unscoped bytes retained unassigned. Browser namespaces are not server sync or a security sandbox. Hosted PASS. |
| WC-15 | Offer actual available fonts in Home, recent-font suggestions and Design Fonts; preserve requested fonts in existing documents and ship every embedded family's license notice. Repair native Shaded heading contrast when the theme accent changes. | Native preview/ribbon menus, native Design command, browser build notices | Local PASS: actual red contrast failure retained; all nine native CI stages pass (4,996 tests, eight pre-existing ignored), fresh pinned engine and six actual Design checks pass; rendered contrast/typography inspected. Hosted PASS6 and image review PASS; see deploy/WORDCRAFT-DESIGN-DEFAULTS.md. |
| WC-16 | Make Set as Default persist a bounded native formatting record through the authenticated account file service, apply it only to blank New, preserve saved/imported/recovered documents and explicitly report save failure/conflict/uncertainty. | Native default-formatting schema and commands, native host dispatch, WordCraft `webos/defaults.mjs` and adapter | User approved 2026-11-17. Native schema/blank/Open/recovery regressions, full native CI and 36 WordCraft JavaScript tests pass. Actual local defaults, A→B→A, fresh-browser and existing-file preservation checks pass locally and hosted. The server file is `Digital Projects/WordCraft/defaults-v1.json`; no browser-global or guessed-account fallback. |
| WC-17 | Default `.txt`/`.py` account files to CodeMirror 6 Text and `.dotx` to WordCraft. Keep app selection in parent composition and reuse native format codecs. | Parent `assembly/viewer/account-app.mjs`; existing CM6 Python grammar and WordCraft DOTX codec | Existing text/Python mapping verified; missing DOTX mapping added. Actual local Files launches for all three pass, including a valid native-saved DOTX. Calculator shared-wrapper mounting/calculation passes locally and hosted. |
| WC-18 | Return from File after confirmed Save/Save As/export; preserve cancellation/failure and unrelated-page/document state. Repair selected-page PDF delivery on wasm. | Native command/save settlement, browser host protocol | PASS: all nine native stages and 38 JS checks; fresh pinned full engine; eight output,19 document and15 recovery checks each locally/hosted, including confirmed navigation and restored typing focus. See deploy/WORDCRAFT-OUTPUT.md. |
| WC-19 | Real browser PDF print completion/errors/timeouts, narrowly scoped print CSP, and a single-row account/recovery footer with full hover text. | WordCraft web print hook/native print state/adapter; parent deployment policy | PASS: live CSP failure reproduced; final graphical Chromium preview opens/cancels twice locally and hosted with object-src disabled; six footer checks each locally/hosted; short print errors and actual images verified. Scoped policy and service continuity pass. |
| WC-20 | Route actual File › Save As › Browse through the account-owned destination command; qualify all13 visible export writers separately from copy semantics and naming. | Native save-dialog entrypoint and button regressions; parent actual-WASM account tests | PASS locally and hosted:all9 native stages (5,005 test executions; eight pre-existing ignored),38 JS and56 actual-browser checks each, plus13 export structure checks each. Actual images and249-file/service continuity verified. Export naming and seven Save As-identity entries remain explicit gaps; see deploy/WORDCRAFT-SAVEAS.md. |
| PDF-01 | Replace transport-success-as-save with native prepare/ack, exact document identity and saved-base checks; preserve later edits, undo and PDF rewrite/incremental rules. | PdfCraft engine and hosted UI save boundary | Native and local actual-browser PASS. Confirmed paths, delayed later edits, stale writes, collisions, cancellation and unknown outcomes are covered. Current source/build identities and hosted gate are in the PdfCraft report. |
| PDF-02 | Reuse mount/lifecycle, account Storage, Desktop activation and account-scoped preferences/recovery; capture native PDF plus live typed drafts. | PdfCraft `webos/` adapter, native UI, parent composition | Local PASS:17 document/account and5 lifecycle checks; shared-payload regression54 checks pass. Actual native PDF text/render checks retain unfinished and minimized typing. Hosted assertions PASS; final main-suite outer exit recorder interrupted. See deploy/PDFCRAFT.md for the exact distinction. |
| PDF-03 | Treat the untouched hosted starter page as a clean baseline; keep explicit blank Save/Save As; remove only the top-right Discord shortcut and its width. Preserve About/community/source/contributor/model information. | Native hosted document creation, chrome and geometry/link regressions | Local PASS:2,989 native UI test executions, five existing ignored probes; six quality gates, one complete WASM graph,27 actual-browser assertions and10 PDF content checks. Hosted PASS:27 browser assertions/11 PDF artifacts; actual About/render images inspected. Other app/Desktop payloads unchanged. |
| PDF-04 | Preserve distinct recovery/replacement/rescue artifacts and verify actual native pending text plus committed snapshot content. The conflict test intentionally overwrites the account PDF and previously reused its local evidence basename. | Parent browser acceptance and native PDF content oracle; no app recovery change | The initial content audit mistook that deliberate replacement for lost recovery text. Native rescue and focused pre-conflict proofs retain both texts. Final test names distinguish scenarios; failed investigation receipts remain evidence. |

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
| Historical finding, now qualified locally and hosted by WC-14: WordCraft uploaded fonts used one IndexedDB database/store (`wordcraft` / `fonts`), and `load_all` reads every stored font. | Account B on the same browser profile inherits Account A's uploaded fonts/names; deleting a stored font is also unscoped. Separate browsers do not share this database. | Closed for this scoped release by account-scoped font storage/loading and actual A→B→A checks; see WC-14. Preference keys alone were insufficient. Source: [font_store.rs](../apps/wordcraft/apps/wordcraft-web/src/web/font_store.rs). |
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

- **2026-11-17 — scoped release qualified:** packaged parent `81828dc0ede2d5dcdac09657e4b027e3c4b62c77` as
  release `86457f2da2b3b9ed0e6b57ed76fdd17ad114d42237554604fe0d72bee1e50716`. All 92 hosted browser checks pass with the same source-
  pinned native engine and strict console/page/HTTP expectations. Actual hosted
  native menus and assembled classic-viewer images were inspected. The guarded
  static operator retained backend instance/issuer, beta index hash and peer PIDs.
  Caddy reload changed only the ksu.codes static root. Exact rollback is recorded
  in [WORDCRAFT-DOCUMENTS.md](../deploy/WORDCRAFT-DOCUMENTS.md). No other Craft app
  was enabled; no external Git publication or original-workspace write occurred.
  The general guide distinguishes reusable contracts from app-specific models
  and unqualified capacity/agent transport. Historical pending entries above
  remain as the actual record of earlier stages.

- **2026-11-17 — hosted runner bookkeeping:** the first outer driver exited143
  after its final viewer wrote a 15-check PASS report, before capturing that
  child's exit. The first seven completed suite receipts were retained. Only
  the final viewer suite was rerun; its complete15 checks and process exit0 are
  now recorded. Current qualification selects those eight successful receipts,
  totaling92 distinct checks. No completed WordCraft/Login/Text suite was repeated
  and no source/test assertion changed for this infrastructure interruption.

- **2026-11-17 — Design/fonts/account defaults and DOTX released:** WordCraft
  `e5446e6058e2ad8fefd1b5d0fc455602fdf7f4a5` is accepted on the local
  `webos/integration` branch; upstream-tracking main is unchanged. Packaged parent
  `239d958648c626b3e861ef946b62a88fa088f3f1` selects that source. The current
  public release is `d7a8f6ae73223079e78013d5f7b3aae01ff8716758b1c14d969f5c22e0ff698b`.
  All nine native stages pass (4,996 tests, eight pre-existing ignored), 36
  WordCraft JavaScript regressions pass, and six Design + nine defaults/file
  association/shared-wrapper + five profile/font browser checks pass both locally
  and hosted. Actual Shaded, font rendering, fresh-browser account defaults and
  CM6 Python images were inspected. Earlier red/CI/harness/browser failures and
  exact retry selections remain in private evidence; no assertions, TLS checks or
  lint guards were weakened. The rollout changed the static root and reloaded
  Caddy; backend instance/issuer, beta hash and all six checked service PIDs are
  unchanged. Scoped payload comparison passes. Disposable build/browser/staging
  output and the superseded archive were removed; one current compiler cache is
  retained through this QA round per the user's explicit decision. The general
  guide, source matrix and current handoff now point to the [focused release
  report](../deploy/WORDCRAFT-DESIGN-DEFAULTS.md), including the exact rollback
  tag. Earlier milestones and pending entries remain historical evidence.

- **2026-11-17 — output/print/footer release qualified:** maintained WordCraft
  `626c74f99879fccef4c33f4385c3008505d9b695`, packaged parent
  `033d824d664176ff6b11c062ce7ff23c075956c8`, release
  `a812d655798dcd4228b75e4a98ed2fec41210179431380f23d801a0808496174`.
  All nine native stages and38 JS checks pass; all51 local and51 hosted checks
  pass (output8, footer6, graphical print3, documents19, recovery15), with exact
  served-build receipts and process exit0. Actual print/error/footer/document
  images were inspected. A failed native Enter-key assumption, shortcut/focus
  harness setup and print-target cleanup races remain documented in private
  evidence; product assertions/job counts were retained. Only WordCraft payload,
  catalog/cache/build metadata and its HTML frame CSP changed. Other app/viewer
  bytes, backend instance/issuer, beta hash and six service PIDs are unchanged.
  Original source and unrelated WIP were preserved; no external Git publication.
  Temporary outputs and profiles were removed, with one compiler cache retained
  for QA. Exact source, artifact and rollback: [output report](../deploy/WORDCRAFT-OUTPUT.md).

- **2026-11-17 — PdfCraft local qualification:** selected runtime browser source
  `670f257268545f585f8104928357cea33961e3bb`; maintained source
  `16e5c9b697a50e1e1ba39b1824344b65eb5ed3a1` adds README clarification only.
  Native engine/UI suites pass;22 actual PdfCraft and54 affected-app checks pass.
  Hosted beforeunload now belongs to Desktop, fixing a reproduced duplicate-panel
  error while preserving standalone behavior. Python3.14 packaging offsets and
  dependency-notice handling were corrected, and the portable build passes.
  Source, browser and packaging failures remain in private evidence. Harness
  corrections respect actual text-box Undo, conflict wording, blank-document
  close confirmation and session decision/finalization ordering. A focused
  lost-response probe corrected interception teardown before the accepted suite.
  No engine/UI rebuild was needed for the later browser-entrypoint warning fix.

- **2026-11-17 — final package review:** three epaint fallback-font notice files
  used nonstandard filenames and were omitted by the name filter. The packager
  now ships all seven documents from the declared licence directory, with a
  filesystem regression. Compiled runtime bytes and all76 local browser checks
  remain unchanged. The first staged package was never activated and its public
  and transfer trees were removed; only small private preparation evidence remains.


## GridCraft/DeckCraft implementation round — local WIP, 2026-11-18 UTC

The user authorized both planned branches with root-owned shared integration,
then approved browser-first recovery and debounced account AutoSave. This is
implementation/qualification, not a new hosted release. ksu.codes remains on
`1c4623b8403bd44b534722bf3db92f6c3bbd96d8e40add396623cb71c44c97db`.

- DeckCraft passed all eight native gates on the approved nightly using the
  task-local ALSA SDK. The test and doctest logs record 2,301 passes and five
  existing ignored cases. The reviewed tree is committed as `bdccaca64be8`
  and present in its local bare origin. The R730 built the exact commit in
  184 seconds with the pinned fonts and verified WASM toolchain. The 107-file
  package was rehashed locally.
  Ten browser checks passed against disposable Accounts and Storage, covering
  PPTX text, notes, theme and embedded picture, both Open routes, manual Save,
  automatic write spacing, fresh-context retrieval, stale-write conflict and
  Save As, concurrent accounts, recovery on refresh with close Cancel/Discard,
  and a lost confirmation after a committed write. Independent PPTX inspection
  confirmed the embedded image bytes and native document parts. The presenter
  popup rendered current and next slides with notes in the local browser.
- The parent candidate `008634e63ea1` pins the reviewed DeckCraft, Runtime and
  Desktop commits. Its seven-app static archive contains 416 verified files
  and 277,978,276 uncompressed bytes. Release ID
  `5e09bf248c15b025f33465ca319c0eec914e6b57d4f4e32998896b9d18d71f42`.
  The archive and the prior six-app release both passed read-only inventory,
  payload budget and per-file SHA-256 checks. The candidate was prepared locally.
- GridCraft passed all ten native gates with 3,909 tests and doctests passing
  and four existing ignored. The laptop supplied the loopback sockets required
  by the native test suite. The reviewed tree is committed as `7f6e3ff709f0`
  and available from its local bare origin. The parent workspace lock passed
  an offline install including both Office app links.
- The Storage client now retains the HTTP `Retry-After` delay. Both Office
  host adapters use Runtime's shared rule for retrying verified no-write
  failures. Toggle changes retain the delay. The WebOS scheduler, Storage
  and shared consumer tests pass. The older DeckCraft candidate reproduced
  the browser regression by sending the retry early. The combined candidate
  must pass that same browser assertion with the updated code.
- The first GridCraft browser package passed live menu gating, formula and
  formatting round trips, both Open routes, delayed and stale saves, account
  isolation and the 45-second server retry instruction. An independent XML
  check verified the stored XLSX contents. The unfinished-formula refresh
  test then exposed a missing field in the native recovery response. The Rust
  callback now returns `saved: false` and its native regression checks that
  exact response. Clean rebuild and browser rerun are required for acceptance.
- Viewer composition loads recovery code for the selected office components.
  With GridCraft and DeckCraft disabled, the assembled candidate passed 60
  browser checks against a disposable Accounts and Storage service. These cover
  classic Desktop, Calculator, Files, CodeMirror, PdfCraft and WordCraft. Both
  native engines were reused from the current release after verifying each file
  against the release and component receipts.

- Runtime `63d425b` adds a document-agnostic scheduler: ten-second committed-edit
  debounce, sixty-second confirmed-write interval, two-minute continuous eligible
  edit bound, and verified no-write retry backoff from thirty seconds to fifteen
  minutes with capped positive jitter. Manual Save stays direct. Unknown and
  conflict outcomes pause. Browser recovery and native editing remain independent.
  Eleven scheduler tests and all52 Runtime tests pass.
- Desktop `ad0f7dd` registers both app hosts in existing menus, account binding,
  activation, layout and session lifecycle. Clean PDF restoration is included.
  Three actual-class tests pass; actual assembled browser qualification remains.
- GridCraft branch `webos/gridcraft-document-host` and DeckCraft branch
  `webos/deckcraft-document-host` own native document/Save/recovery/pause/profile
  hooks and public adapters. Their selected parent checkouts are still the old
  accepted pins: neither branch is promoted or committed as qualified here.
- Native eligibility must be rechecked at capture: background Save cannot commit
  unfinished cell/formula/notes/IME editing. Visible AutoSave choices are scoped
  per account and reflect actual scheduling; the old filesystem writers remain
  disabled. Browser checkpoints keep working while account syncing is disabled.
- Eligibility changes during a native close lease are scheduling state, not
  document edits. Including them in the Discard fingerprint wrongly invalidates
  a valid close; both adapters now distinguish those states and test the boundary.
- The original iframe Document fences native requests and acknowledgements.
  WindowProxy survives a reload while numeric native IDs can restart. On an
  unexpected reload, reject old pending requests, preserve the journal, mark
  unavailable and allow closing the unavailable view without clearing recovery.
- Durable Storage success and native adoption are separate phases. DeckCraft's
  file session now optionally awaits exact native adoption before publishing a
  new binding or releasing its pending guard. Native failure after a returned
  server revision becomes unknown, retaining the previous binding. Four added
  regressions cover this and manual-conflict pauses, including toggle bypasses.
- Both native compile checks pass. DeckCraft's ten focused native tests pass
  after a real lower-bound preference validation fix in the native engine;
  the initial failing assertion is retained. Its39 JavaScript tests pass.
  GridCraft's27 host/recovery and five packaging tests pass; native test execution
  is still pending at this checkpoint. The first root JS invocation omitted
  Node's required VM module flag; the corrected invocation passes unchanged tests.
- Two bounded, offline WASM builds passed concurrently on the R730 in176s and
  216s. A later native DeckCraft fix rebuilt in14s in the same current target.
  These were explicitly unqualified WIP snapshots, not clean-source release
  receipts. No artifact has been promoted or deployed.
- Both app agents were stopped by automated safety review with only the generic
  reason “Potentially unintended activity.” Root reviewed and continued scoped
  source/tests; no agent was restarted. The specific trigger was not supplied.

The private round checkpoint records exact worktrees, commands, exits, builder
ownership and remaining gates. Native CI, clean source artifacts, actual browser
and whole-assembly account qualification must complete before release approval.
Generated outputs, test state and compiler caches remain outside source control.

## Office browser follow-up

DeckCraft `85c82199` finalizes only its leased native frame after Accounts
revokes the session. Regular commands still require that session. All eight
native gates, 40 adapter tests and 14 actual browser checks pass for the exact
107-file package. The saved PPTX files independently verify the slide text,
speaker notes, Ember theme and the exact embedded image. This is evidence from
the local profile with DeckCraft enabled. The two-app profile still needs a run.

GridCraft `c9c4f33` fixes the recovery response so the browser recognizes the
restored workbook as unsaved. A further run verified the exact formula in the
browser journal before reload and exposed its loss during the native window
transition. A separate test reproduced a negative formula-bar width while
minimized. The next native CI run covers assignment to the recovered window and
the narrow viewport case. Both require a fresh exact build and browser test.

GridCraft `ad0ebfe2` now passes the pending-formula and minimize checks on
the exact WASM package. The browser verified the stored A1 formula, found it
still unfinished after reload, and computed 42 only after explicit entry.
The signed session also restored both Office files to their original workspaces.
The broader suite caught a missing explanation when the server accepted a
write and the browser lost its response. GridCraft's adapter fix retains the
pending write, pauses automatic saves and tells the user to verify the file.

DeckCraft `f8353c0d` keeps unfinished formatted notes in their own recovery
record. The actual notes editor can resume the draft after refresh while the
slide model still holds its previous notes. Native CI and the focused browser
test pass. The first build reused identical WASM bytes after the native change.
Refreshing tracked-file timestamps in the isolated snapshot forced the
intended rebuild. Its new digest and actual recovery behavior were verified.

## Local Office release candidate

- Packaged parent `2d08b293754f36e38b4366865b4ff5d6d64a8f4e`.
- Release ID `5e0d0b3bbb69b09814deb79daac988261578003174f89b4c58a916cd420c0566`.
- Archive SHA-256 `33d5fde9c599d467f7f0fb9ce9fc0552068713801004b874fe50c3b58b22b6f5`.
- The archive inventory and payload digests passed verification for all 444 files.
  It occupies 108,496,106 bytes compressed and includes 96 JavaScript package
  notices and the four native engine notice sets.

The 87 browser checks comprise 27 Office checks and regression suites for
Desktop, Files and Calculator (15), Text (9), PdfCraft (17), and WordCraft (19).
The Office suite exercised real signed account saves and both Open routes,
stale and uncertain writes, account separation, recovery of unfinished native
input, the presenter window, the longer server retry delay and restoration of
both workspaces across sign-out. An independent ZIP/XML inspection verified
four saved account files, including the worksheets' generated formula value
and style and the presentation's text, notes, theme and exact embedded image.

Private round evidence includes the archive
`office-viewer-final-fd80-f835.tar.gz`, its inventory
`office-release-final-inventory.json`, the browser results and the saved-file
audit. The local release awaits separate approval for deployment.

### GridCraft authorized operations on loopback

The separate development profile connects an independent P-256 agent key to a
single mounted GridCraft document. Desktop's trusted owner confirmation
displays the key fingerprint, the mounted window and resource, the exact
commands and the duration. The Accounts server signs and consumes one-use
intent confirmations. Desktop checks the session, instance and current binding
at dispatch. GridCraft processes the bounded request through its existing
`execute` contract. File commands require the separate human authority.

The actual assembled Chromium test used independently signed HTTP requests,
two live WASM workbooks and two isolated accounts. It verified that the
approved formula evaluated to 42 in the intended workbook only. It also
verified cancellation, synthetic-click rejection, rejection of a different
signing key, argument tampering, replay, other-account consumption, native
document and cell reads, protection of an unfinished user formula, direct-call
rejection, Save As during server consume and revocation before consume. The
newly saved workbook retained its correct formula. The launcher without the
explicit flag exposes no bridge.

See `office-agent-browser-r4/results.json` and
`office-agent-default-regression/results.json` in the private checkpoint.
The static Office release candidate remains independently identified.

### DeckCraft authorized notes on loopback

DeckCraft `5b065c4ef93c` adds stable slide-ID input to the native notes command.
The hosted editor refuses an agent note edit while the user has an unfinished
native edit. The app adapter permits only signed presentation inspection and
stable-ID notes edits. The ordinary save, activation and account recovery
routes retain their existing authority and document state.

All eight native gates and 41 adapter tests passed. The isolated R730 build
finished in 68 seconds. The laptop verified the 107-file component package
against its receipt. Seven signed browser scenarios passed in the merged agent
profile. DeckCraft accepted a grant for a moved slide and refused a fresh
grant for the same slide after deletion. The other slide's notes stayed empty.
Evidence is in `office-signed-notes-browser/results.json` and
`deckcraft-package-5b065c4ef93c-verified.json` in the private checkpoint.

Accounts' isolated `webos/office-operation-delegation` branch contains a
bounded same-origin HTTP adapter and a browser capability tied to the owner
session. The Accounts test suite passed 69 tests. A separate real loopback
signed HTTP run covered approval, scoped intent, single-use consumption,
revocation and logout fencing. The separately archived Office candidate uses
Accounts `c8229d6` and awaits deployment approval. The signed-notes development
assembly also passed 88 default-profile checks, including all 27 Office
workflows and the check that the default launcher exposes no agent bridge.
Delegated file grants remain open.

### PhotoCraft native browser baseline

The selected source `2fec95b0d91b` passed an offline WASM `cargo check` of
both the browser app and the boot crate with HEIF enabled. The command used
the pinned translation catalog, preserved the Cargo.lock checksum and reused
the existing compiler cache. The compiler check took 4 minutes 53 seconds.
See `photocraft-exact-browser-check-exit.json` in the private checkpoint.

The account worktree starts from this exact pin. PhotoCraft's native editable
format is a `.pcraft` ZIP containing the layered document. The existing web
save service initiates a browser download with no durable confirmation. The
account integration must correlate each encoded revision with Storage's
conditional write and receive native adoption before updating Desktop. The
browser preset database and preferences also require account-scoped keys.

The account worktree now sends `.pcraft` bytes with a native save ticket and
adopts the result only after matching the editor generation, document,
revision and destination. The development host also scopes preferences and
brush presets by account. The changed source passed the locked offline WASM
check in 52 seconds. Five Storage adapter tests now cover conditional Save,
create-only Save As, matching native adoption, conflicts and a lost write
receipt. Wiring that adapter into the classic Desktop and the full browser
workflow is still in progress.

The R730 input bundle contains four verified Git dependency trees and the
pinned translation catalogue. Its Binaryen optimizer and the portable Trunk
0.21.14 release pass version checks on that builder. The first Trunk copy
required a newer glibc. See [build inputs](CRAFT-BUILD-INPUTS.md) for the
verification scope and private receipts.

### PhotoCraft account project startup

The two focused native save tests passed on the recorded source. They verify
layered project bytes, exact save-ticket adoption, preservation of later edits
and retention of the previous binding on a known write failure. The wrapper
exit receipt was unavailable. The completed Cargo log and a separate comparison
of all recorded input hashes are in `photocraft-account-save-native-r1-recovered.json`.

The native account view now starts with the ordinary New command or opens a
`.pcraft` file through its native decoder, returning the admitted document and
revision. Both browser crates passed the locked offline WASM check with HEIF.
The classic API2 mount accepts replies from its own frame and publishes a file
binding after native adoption. Nine JavaScript tests cover the adapter, native
message correlation and the composed mount, with 33 shared Runtime regressions
also passing. The composed JavaScript test uses a fixture frame. Actual browser
execution and the File menu's account Open and Save As routes remain open.

All 19 native save-identity tests pass, including the two new startup routes
and two account-save cases. The tested native fork is `f26762c36b01` on
`webos/photocraft-document-host`. Its clean R730 snapshot matches the local
Git tree and passes locked offline WASM dependency resolution.

Trunk also runs workspace metadata commands that request archives outside the
filtered WASM graph. The first packaging attempts stopped at the missing
locked `alloca` archive. The builder now has all 55 remaining locked
workspace archives, verified against Cargo.lock, along with the 105 archives
and sparse indexes needed by the WASM preflight. Linked package and browser
qualification remain open.

### PhotoCraft account file dialogs

Native fork `e83591e0612a` routes File Open, Open Recent and editable-project
Save As through a dedicated account dialog service. Native exports retain
their local dialog path. The parent uses the classic account picker and
activates an existing PhotoCraft window for the selected project. A different
saved project receives its own window, using the server's current file
revision. Choosing a save destination performs no write until the native
editor sends its separately correlated save request.

The fork passes all 63 native file-dialog tests, including a regression that
checks the account and local-export routes. Both WASM crates compile with
the locked HEIF/translation inputs. The parent passes 44 JavaScript tests
across PhotoCraft, file associations and shared Runtime operations. The
classic Desktop routing commit is `77547ea8ba46`. The local test builds reuse
the verified WordCraft, PdfCraft, GridCraft and DeckCraft engines.

The R730 already has the dialog revision as a verified Git delta. Its checked
out source remains pinned to the earlier startup commit for the current
package run. PhotoCraft remains disabled while the linked package, live
browser account workflow and close/recovery behavior are under development.

### PhotoCraft browser packaging

The first R730 release-profile build of `f26762c36b01` produced a verified
17.2 MB archive and 42.0 MB of uncompressed app WASM. Chromium exposed a
missing generated eframe module. App glue is placed in `app/`, so the boot
crate's root `snippets/` directory leaves its relative import unresolved.
Native packaging commit `7876cdf484ae` now copies app snippets beside that
glue. The repaired loopback fixture used the exact generated module and
unchanged WASM. All four smoke scenarios passed, including real keyboard Save
and reopening the exact project bytes in a fresh native frame. The optional
served-font catalogue returned an expected 404 in that fixture.

The dialog snapshot `e83591e0612a` linked on R730. Packaging commit
`7876cdf484ae` produced a verified 17.2 MB archive from the unchanged
compiled files. The loopback assembly serves Trunk's generated startup
module from a same-origin file under the classic Desktop's existing CSP.
The release packager rejects this development profile.

### PhotoCraft signed account workflow

All eight Chromium checks passed with the real PhotoCraft WASM, the classic
Desktop and a signed loopback Accounts and Storage backend. The suite covered
keyboard Save, same-file activation from Files and native Open, Save As
cancellation and name collision, recovery of the saved layer from project
bytes, an independent window for a different project, fresh-browser retrieval
and cross-account denial. The collision produced its expected server 409.

The 87 Office regression checks passed with Desktop routing commit
`77547ea8ba46`. The PhotoCraft signed suite exercised the later account
picker at Desktop commit `32ad5d640d5a2`, which lists through the same
server authority that resolves and saves account files.

Fork commit `09933e867a98` routes the native New dialog through the Desktop
host into an independent clean project using the requested dimensions. The
exact revision passed 63 native dialog tests, 19 native save-identity tests
and an offline WASM check. Its assembled-browser test remains pending.
Close, recovery, AutoSave and authorized agent operations remain open.
