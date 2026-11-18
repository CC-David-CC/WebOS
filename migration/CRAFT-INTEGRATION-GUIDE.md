> **Current product scope, 2026-11-18 UTC.** Integrate all 18 selected Craft apps, including SketchCraft.
> The [integration matrix](CRAFT-INTEGRATION-MATRIX.md) tracks live and queued
> apps, including apps with upstream workflow gaps.
> Represent all 18 in the menu. Disabled entries indicate unqualified
> support. Preserve legacy apps as disabled entries until the user decides.
> Readiness comparisons do not authorize removing apps or replacing their source.

# Integrating a Craft application into WebOS

Current qualification (2026-11-17): WordCraft's document integration, Design/fonts/
account defaults, print/output and Save As Browse follow-ups are deployed to
ksu.codes. The latest selected WordCraft source is
`edeb4a090cd301cd7d4405e20af795007b37b69b`; the Save As release passed all nine
native stages (5,005 test executions; eight pre-existing ignored), 38 JavaScript
regressions and 56 actual-browser checks each locally and hosted, plus checks of
all 13 export files. See [the current focused report](../deploy/WORDCRAFT-SAVEAS.md)
for exact artifact, rollback and remaining export naming/identity limitations.
The [running integration log](CRAFT-INTEGRATION-LOG.md) records changes and
historical failures. The [document integration report](../deploy/WORDCRAFT-DOCUMENTS.md)
records the historical document-integration milestone. This guide does
not grant another application WordCraft's results or authorize deployment.

PdfCraft's clean-blank/community-chrome follow-up is deployed and verified on
ksu.codes. Current maintained and compiled source is
`a5b512846f59c6e5306821cdffdb448e54695ccd`;27 actual-browser assertions pass each
locally and hosted, and independent native checks pass10 local/11 hosted PDF
artifacts. About/community/contributor/model links remain. The other apps and
Desktop payloads are unchanged. See [the PdfCraft report](../deploy/PDFCRAFT.md)
for exact release/rollback and the separate clean-window/layout restoration gap.
The initial22+54 integration checks are historical evidence, not newly rerun
checks for this app-only follow-up.

## Common integration contract and planning coverage

Disk organization is complete. This guide governs site integration from those
existing independent repositories, including native source changes needed for
the host contract. It does not restart source extraction or reorganize the tree.

The common plan should settle at least80% of the recurring integration decisions
before app-specific implementation starts. That is a planning target, not a
claim that80% of each application's code is already written or tested. Native
models, transient edits, serializers and import/export semantics still require
source inspection and their own proof. WordCraft/PdfCraft are reference
implementations, not templates to copy wholesale.

For every app, fill this register with owner, existing public implementation,
specific native gap and required evidence. Use `reuse`, `extend`, `app-specific`
or `not applicable — reason`; no silent unassessed row. Most responsibilities
below are already defined, so the next app should not rediscover platform policy.

| ID | Required contract / decision | Reuse and owner | Required app evidence |
|---|---|---|---|
| C01 | Independent fork, upstream main, reviewed base, stable accepted history | Existing repo/submodule and upstream workflow | Exact source/base/lock refs; no unreviewed merges or lost WIP. |
| C02 | Explicit reproducible inputs and development toolchain | App-owned build recipe; shared asset/library owners | Source-pinned fonts/translations/models, notices, offline actual browser graph. |
| C03 | Synchronous mount, readiness/failure/cancel/retry/dispose | Public host interface; app adapter | Startup failure never becomes a successful blank; late callbacks fenced. |
| C04 | Account, instance, session, native document/revision and saved resource identity | Accounts/Storage/Desktop; native app IDs | Exact correlated adoption; no active-index/basename identity guesses. |
| C05 | One live editor per account resource; native New/Open/Close requests | Desktop activation and app hooks | Files plus native Open reuse buffer/undo; independent different documents. |
| C06 | Native semantic commands and inspection; explicit caller/target authority | App command domain and public host authorization | Stale/rebound targets denied; internal acknowledgements cannot be forged publicly. |
| C07 | Read account bytes and canonical identity from one shared file service | Storage; app-native parser | Correct full path/revision, unavailable-file Retry and fresh-context retrieval. |
| C08 | Prepare bytes/revision and identify Save/Save As/export before dispatch | Native serializer and shared identified-save transport | Save ticket captures originating document and actual bytes; dispatch is not persistence. |
| C09 | Durable conditional writes, canonical saved identity, title/layout updates | Storage plus native acknowledgement and Desktop | Failure retains old binding; later edits/undo remain correct after acknowledgement. |
| C10 | Explicit cancel/conflict/collision/failure/unknown outcomes | Storage outcomes plus native pending-save state | Lost response after server commit cannot trigger blind overwrite or false success. |
| C11 | Clean untouched starter document and explicit blank Save | Native creation/dirty baseline | Quiet close until edited; Save/Save As still writes a valid blank file. Imported/generated work assessed separately. |
| C12 | Native recovery payload with supported pending edits and assets | Native app codec; Runtime journal mechanics | Actual fidelity, unchanged live buffer, encryption/password handling, schema/version bounds. |
| C13 | Account-scoped ordered draft journal and restoration | Runtime + Desktop recovery UI | Minimized/orphan/refresh/A→B→A; changed base uses Save As; failed journal preserves earlier checkpoint. |
| C14 | Close/session-end Save/Discard/Cancel, revision recheck and finalization lease | Desktop/Runtime, native lease hook | Later edit invalidates approval; Cancel resumes; one hosted navigation warning. |
| C15 | Account-scoped preferences, recent paths, uploaded fonts and defaults | Accounts namespace; native preference schema | No global fallback or cross-account inheritance; defaults preserve existing files. |
| C16 | Human file dialogs, completion/focus and single-row truthful status | Native UI + app host dialogs | Actual menu/keyboard paths, failed/cancelled actions, focus and source identity; no transport-success UI. |
| C17 | Export and printing distinguished from document Save | Native codecs/output; browser-controlled printing | Per-format generation/delivery/fidelity/naming; actual graphical preview if print is claimed. |
| C18 | Parent associations/menu/composition without interface rewrite | Parent; classic Desktop public contracts | Register launch and saved-layout restoration; explicit format list; existing Text routes retained; changed shared consumers tested. |
| C19 | Community provenance, licences and requested chrome simplification | App About/credits/notices | Permitted About/community/source links retained; restricted fork artwork removed. |
| C20 | Native, adapter, actual-browser and hosted evidence; bounded build retention | App + integration owner | Separate receipts, affected regression scope, exact release/rollback, no outputs/private state in Git. |

Before implementation, every row must be assessed and each unresolved item must
name a source owner and acceptance test. Review the register against both
WordCraft and PdfCraft lessons, especially false save completion, transient
typing, account-global state and clean blank behavior. Count assessed decisions
if reporting coverage; do not convert checklist counts into a percentage of
engineering effort. Detailed prose below specifies these same contracts.

The [GridCraft/DeckCraft branch plans](CRAFT-BRANCH-PLANS.md) identify concrete
source gaps, proposed branches and phase gates. The
[build execution plan](CRAFT-BUILD-EXECUTION.md) records measured laptop/R730
capacity, cache ownership and the proposed benchmark/setup sequence. Finish
current work and these plans before starting either implementation. Parallel
agents and remote builds are future execution choices, not implied permission
to change both apps or publish a new assembly now.

## Account AutoSave policy — approved implementation round

The user authorized parallel GridCraft/DeckCraft integration after reviewing the
branch plans, and then approved browser-first recovery plus debounced account
AutoSave. This supersedes the earlier planning-only statements above. The current
round remains local implementation/qualification; it grants no external Git
publication or website/service changes. WordCraft/PdfCraft reference releases do
not acquire AutoSave merely because Runtime exports a scheduler.

Runtime owns `@webos/runtime/account-autosave`, not document serialization.
Each app must assess this policy under C08–C10, C12–C16 and C20:

- Browser recovery keeps native pending edits under the current account scope.
  It remains independent of account AutoSave and never implies server durability.
- A named, verified account resource becomes eligible after its first explicit
  Save/Save As. Untitled/imported work is never named or created by a timer.
- Wait10 seconds after committed edits; permit automatic server writes no more
  often than once per 60 seconds per view. Continuous eligible edits have a
  120-second maximum wait. Native transient editing/IME/dialogs/session leases
  remain ineligible: a timer must not settle drafts or steal focus.
- Existing native AutoSave controls must reflect the account scheduler, with
  truthful hosted help and account-scoped choices. Disable the old filesystem
  AutoSave writer in hosted mode. Keep local recovery active independently.
- Use the same identified native capture, conditional Storage revision and
  canonical native acknowledgement as manual Save. Keep manual Save immediate.
  Later edits remain dirty; no JavaScript shadow document is introduced.
- Retry only explicitly verified no-write transient rejections, doubling from
  30 seconds to 15 minutes with positive jitter capped at15 minutes. Respect a
  longer explicit server Retry-After. Continued typing cannot reset backoff.
  Current Storage's two exact admission/allowance 429 errors are classified from
  its implementation; generic 429/408/5xx responses do not establish no-write.
- Conflicts, lost responses, invalid acknowledgements and uncertain writes pause
  automatic syncing. Preserve local drafts and ask for explicit resolution;
  never replay a possibly committed mutation. Successful explicit Save or Save
  As clears the pause only after both Storage and native adoption confirm.
- At most two automatic save callbacks run at once per browser page. This load
  smoothing is neither a server permission boundary nor a site capacity claim.
  Account/server limits remain authoritative; manual operations are unaffected.
- Fence asynchronous work to account/session/resource and the original native
  iframe Document. A reload can retain WindowProxy while resetting native IDs;
  fail unavailable with retained recovery instead of admitting a stale result.

Qualification requires deterministic scheduling/backoff/late-edit tests, actual
app-native eligibility and identified-save regressions, browser-local recovery,
real conditional server writes, conflict/uncertain injection, manual Save during
cooldown, account isolation and actual UI status/toggle checks. Shared scheduler
unit tests alone do not qualify either app or a hosted release.

## PdfCraft: applying the document contract

The existing synchronous mount, explicit ready/failure/disposal, account Storage,
Desktop resource activation, conditional writes, pause leases and account-scoped
Runtime journal are the same public boundaries used for WordCraft. PdfCraft owns
its integration entrypoint in `apps/pdfcraft/webos/`; its PDF model stays in Rust.
It uses the existing shared `craft-web-host` save context rather than introducing
another account service, file API or JavaScript document model.

The app-specific work differs from WordCraft:

| Boundary | PdfCraft requirement and current implementation | Qualification |
|---|---|---|
| Save confirmation | Capture an opaque native prepared save. Sending a message is not persistence. A confirmed write adopts its account path; newer model edits and typed drafts remain unsaved. Foreign, reloaded and obsolete saved-base tokens are rejected. | Native and local browser delayed/failed/conflicting/cancelled/unknown-save checks pass. |
| PDF fidelity | Keep incremental revisions for ordinary edits. Preserve the existing deliberate full rewrite for page deletion, redaction and security changes. Rebase matching undo states without replacing newer work. | Native incremental/rewrite regressions, actual browser reopening and native CLI text/render checks pass. |
| Recovery | Snapshot the native PDF and pending text/form edits in a disposable native session, without closing the live text box or running opening scripts again. Retain encryption and the existing password-field filtering. The recovery record contains no password or save token. | Native encryption/filtering regressions and local unfinished/minimized/A → B → A recovery pass; browser password prompts remain unqualified. |
| Window ownership | Route New/Open/import/Close through Desktop; identify actual native adoption, including password entry or cancellation. Repeated account Open activates the current editor. | Local Files/own Open activation, independent views, close decisions and finalization leases pass; not every generated/import workflow is browser qualified. |
| Account state | Hosted preferences use an account namespace with no unscoped legacy fallback. Reuse account-owned Storage and issuer/account-scoped local recovery. | Native scoped-profile tests and local A → B → A/fresh-browser retrieval pass. |

Native document IDs/revisions remain distinct from account paths/server hashes.
Unknown storage outcomes retain the pending write and unsaved work; they do not
authorize an automatic overwrite retry. PdfCraft's original browser Save marked
the model clean immediately after transport delivery; the hosted path now waits
for a native acknowledgement of the server-confirmed result. Its original
origin-global `pdfcraft`/`printcraft` preferences are not imported into an account.

The shared host protocol already provides identified saves and explicit failures.
Its generic `saved` message does not carry a canonical account path. The PdfCraft
adapter therefore returns that authorized result through the existing opt-in
native control channel, with the exact pending save ticket; a bare `saved` event
cannot finalize a hosted document save.

Hosted iframe applications must leave the navigation warning to Desktop. Keep a
standalone warning only outside document-host mode; two handlers produce
Chromium's blocked-duplicate-panel error. Verify the browser's actual console as
well as successful draft restoration. Minimized views must still service native
snapshot requests, and their draft must survive refresh/activation.

During session end, Desktop first collects close decisions while tracking native
revisions; a later edit invalidates earlier Discard approval. Native pause leases
apply during finalization after those decisions. Test both mechanisms at their
actual stage rather than expecting all commands to be frozen during every dialog.

For PdfCraft's Add text UI, finish with its actual Done adding text control before
testing document Undo. Undo while a text box remains open intentionally handles
that box's typing first. Use page-fit/actual native geometry for pointer tests.


## WordCraft reference and source ownership

Historical baseline: WordCraft `fbc4bb73fbc177c9adcfbb705c9a9a05212a7ae9` passes all nine native CI
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

PhotoCraft, VectorCraft and FigCraft use the native account packet contract in
`assembly/viewer/craft-account-native.mjs`. The shared connector admits each
app's own namespace, exact iframe document, origin and generation. The shared
layer-editor mount supplies account Open and Save As, conditional storage,
browser journaling, AutoSave and scoped `document.inspect`/`layer.rename`
dispatch. Register the app ID, display name and native extension. Confirm the
native account hooks before reusing the mount.

Verify which layer owns dirty-close review. PhotoCraft presents its native
review while VectorCraft and FigCraft delegate the whole-project decision to
Desktop. The shared session coordinator binds Discard to the reviewed revision
and to either window close or sign-out. The app provides its own serializer,
editable revision and native commands. Capture a separate recovery revision
when child edits can change without advancing the saved parent revision.

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

For each human destination command, test the actual button as well as the
keyboard shortcut and explicit-path API. File › Save As › Browse can retain a
legacy picker even when `file.saveAs` and F12 correctly ask the host. Hosted
WordCraft now routes its Browse entrypoint through the same domain command;
standalone file dialogs keep their existing implementation.

Assess each Export menu entry separately. File generation, account delivery,
formatting fidelity, destination choice and source-identity preservation are
independent gates. WordCraft's DOCX, two XML, ODT/OTT/FODT and RTF Export entries
currently use Save As identity semantics, and its menu supplies an automatic
filename. PDF/PNG copy checks never qualified those other entries. See
[the Browse/export follow-up](../deploy/WORDCRAFT-SAVEAS.md) for the current matrix.

## Unsaved work and recovery

Expose native dirty/revision/pending-save state to the host. Before closing or
ending a session, coordinate Save/Discard/Cancel and recheck the exact state under
a matching native pause lease. Host UI visibility alone does not freeze edits.
Acquire the lease while the account is valid. Final sign-out can revoke the
account before disposing views. If native cleanup is needed after revocation,
limit it to the leased frame and its own resources. Keep account operations
subject to the normal session check.

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

Qualify the exact checkpoint being claimed. An already-visible "draft updated"
message can describe an earlier edit; it is not a write barrier for newly typed
content. Verify the intended native text, capture the actual native snapshot,
and verify that automatic journal storage committed that exact snapshot before
reloading. Then inspect recovered native content or saved output, not only dirty
state and a recovery dialog. These are stronger test preconditions, not a claim
of zero-loss durability at arbitrary navigation times.

In a native editor with per-window UI state, adopt the recovered document's
window before installing its pending editor state. Exercise recovery after the
startup window has rendered. Also exercise hidden and minimized iframe states.
They can report a zero-sized viewport while the editor still handles commands.

Keep scenario evidence immutable. PdfCraft's stale-write test intentionally
replaces the recovered account file with older fixture bytes, then downloads it
to verify rejection of an obsolete save. A shared basename overwrote the earlier
local recovery evidence and made a later content audit incorrectly look like
recovery data loss. Preserve a distinct before-conflict file and check the
replacement and conflict-rescue files separately. Record failed investigation
receipts truthfully; do not relabel the intentional replacement as a lost draft.

## File associations

Default account-file routing belongs to parent composition. `.txt` and `.py`
open CodeMirror 6 Text; `.py` uses the actual Python language extension. `.dotx`
opens WordCraft alongside the existing DOCX/ODT/RTF routes. Qualify a genuine
native-generated template, rather than renaming an arbitrary ZIP or text fixture.
An explicit Open inside WordCraft can still import its supported text formats.
Changes to the shared account-app wrapper require checks of affected Files/Text
routes and a Calculator mount/calculation smoke check; they do not imply changes
to those independent application repositories or to Desktop styling.

## Account state and authorized operations

Scope recent paths, preferences and uploaded fonts to the validated account
profile. Hosted mode must not fall back to global state when that profile is
missing. Retain old unscoped stores without guessing their owner. Test A to B to A
in the same browser profile, including actual font loading and deletion.
Account-namespaced browser settings/fonts are not server synchronization across
machines and are not a barrier against trusted same-origin code.

Inspect framework persistence as well as app preferences. PdfCraft's eframe
version loads and saves an origin-global `egui_memory_ron` record separately from
the app's settings key. Hosted mode clears that inherited widget memory before
use and disables writing it; only its scoped application preference record is
restored. Preserve legacy unscoped data without guessing its owner or deleting
another application's state. Verify account switching with actual browser data.

Document defaults that must follow an account belong in authenticated server
storage. The current WordCraft follow-up uses a bounded, versioned native
formatting record at `Digital Projects/WordCraft/defaults-v1.json`, accessed
through the existing Storage capability. Capture formatting without document
contents, credentials, save identity or tracked style-edit history. Apply it only
on blank creation; saved files, imports, explicit templates and draft recovery
remain authoritative for their own formatting. Use revision preconditions and
durable acknowledgements for writes, with visible failures and no browser-global
fallback. Test A → B → A and the same account in a fresh browser environment.
This mechanism passes local and hosted qualification, including a fresh browser;
its results were independently collected for the current release. Other Craft apps need their own native schema and creation boundary.

Font menus should offer families actually loaded by the editor, including the
current account's uploaded fonts. Keep an imported document's requested family
and substitution warning truthful; hiding unavailable menu entries must not
rewrite the document. Package the actual licenses for every embedded font family.
Uploaded browser font bytes are a distinct persistence boundary from server-backed
document defaults; saving a family name does not synchronize those font bytes.

Human, test and authorized agent actions must reach the same native/domain
operations. Public execution requires an explicit caller and exact target tuple.
Capture bounded arguments before asynchronous authorization; refuse execution if
the instance, session, document or resource changes during the wait. Never expose
authentication secrets in ordinary inspection. Current human mount authority is
separate from delegated-agent authentication. The opt-in loopback development
profile connects the Accounts authority to mounted GridCraft and DeckCraft
editors. Other apps require their own bounded command policy and proof.

The development bridge lives under `desktopLab.agentOperations`. Start the
normal development launcher with `--agent-operations` to enable it on a direct
loopback origin. A trusted caller supplies the live application instance ID,
the independent agent's public key, the command list and the lifetime. Desktop
asks the signed-in owner to approve that exact scope through its modal. The
result carries the delegation credential once and includes the document
identity needed to construct the signed request.

GridCraft exposes `document.inspect`, `cell.get` and `cell.set` through this
bridge. Reads and edits to cells require an explicit sheet and address. The
editor refuses agent edits while native user input or another operation is
in progress. The browser
checks the account, view, native document and file binding before and after
the signed server consume. Changing the binding through Save As invalidates
the prior approval. The editor receives a one-use invocation capability. Its
native command, recovery and approved AutoSave behavior remain the same.
Delegations grant neither direct file transfer nor control of Save or Open.
DeckCraft exposes native presentation inspection and speaker-note edits. A
note edit takes a native slide ID and resolves it in Rust at execution. Moving
a slide preserves its identity. Deleting it makes the command fail. The native
host protects pending notes and composition before accepting the edit.
Origin-trusted app code can already reach browser APIs, so the bridge is a
boundary for external agents rather than a sandbox between integrated apps.

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

Choose regression scope from the changed code and contracts. Shared Desktop,
Runtime, Accounts or Storage changes require checks of the apps that use those
boundaries, including Text recovery when lifecycle/journal behavior changes.
App-local changes need that app's meaningful tests and affected integrations;
do not repeat unrelated viewer/Files/Calculator checks without an impact or an
unresolved concern. Documentation-only changes require no browser retest or
native rebuild. Reuse current evidence for unchanged source; after an execution
failure rerun only the affected suite when the other receipts remain valid.

Fresh browser contexts demonstrate server-backed retrieval, not a physical
second-machine test or all-format parity. Do not reuse an old WASM payload or old
PASS count to qualify a changed native protocol. Local bare Git copies preserve
commits locally; they are not an off-machine backup.

## Rolling integration queue

The [integration matrix](CRAFT-INTEGRATION-MATRIX.md) records live status and
source pins for all 18 selected apps. Each app can roll out independently once
its own native, account and browser gates pass. The sequence below groups the
remaining work by the behavior that needs qualification.

| Next work | Acceptance milestone |
|---|---|
| VectorCraft | Finish exact selected-commit browser qualification and rolling activation. Verify scoped editing and Undo, Save As, conflict recovery and an account reopen in a fresh browser. |
| AniCraft | Use the existing `.anicraft` codec. Edit a native timeline, retain embedded art and sound, Save and recover the project, and verify a browser export independently. |
| LightCraft | Qualify an account-scoped catalog with originals, adjustment recipes and render workers. Verify that a fresh browser can retrieve an edited photo and its original. |
| DesignCraft | Preserve editable pages, typography and linked resources across Save, recovery and fresh-browser reopen. Verify publication export using an account project. |
| SoundCraft, FilmCraft and EffectCraft | Qualify native projects containing referenced media. Test browser codecs, large assets, rendering or playback and job ownership when a window closes. Use the existing shared media engines where applicable. |
| CADCraft and SolidCraft | Qualify native drawings and parametric parts in their own browsers and kernels. Verify precision and editable geometry after account reopen. |
| TextureCraft and MaterialCraft | Preserve geometry, maps and procedural graph inputs in account projects. Verify renderer availability and re-render after reopening. |
| SketchCraft | Connect the React modeling interface to the native Rust command model in a browser release. Prove push/pull, undo, scoped commands and a round trip of the editable `.sketchcraft` model through account Storage. The upstream Vite launch uses a local development bridge. |

Files, Accounts, Storage and Runtime reliability outrank adding games or another
editor for functional WebOS. Each account already has a separate server home;
Storage still has a shared critical section containing scans/hashing/writes.
Measure contention before narrowing locks, retaining conditional-write, atomicity
and quota guarantees. Shared admission/transfer fairness, multi-user capacity and
per-document browser memory remain unqualified. The organized Accounts source
also includes separate delegation/policy work beyond the retained deployed
backend; do not accidentally deploy it during a static frontend release.

Use affected-app regression tests when changing the shared Desktop, Files or
account boundaries. The current deployment path publishes a qualified static
assembly and checks continuity against the running backend and beta.

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

## File-action completion and browser printing

For the next Craft app, check the actual browser output path as well as the native
file command. A wasm command that calculates a PDF and skips filesystem writes
can return plausible metadata without saving anything. WordCraft's `file.printPdf`
now delivers the selected-page/copy/imposition bytes through its identified host
save protocol, as an export that preserves source identity and dirty edits.

Return from File/Backstage after confirmed delivery, not after posting bytes or
starting a picker. Keep cancellation/failure actionable. Retain the originating
document and page so a late completion cannot dismiss an unrelated view, and test
keyboard focus after the human Save As dialog. The native application owns this
completion behavior; the parent must not fake a successful engine save.

A host-owned Save As dialog can restore DOM focus without restoring the native
editor's caret focus. WordCraft's public view focus operation also requests its
native `ui.focus`; a path dialog returns focus to its owner when dismissed.
This operation does not close File, mark anything saved or alter file identity.
Do not restore focus later from a background save in a way that steals another
view's focus, or run focus restoration during disposal/session quiescence.

Printing needs a real graphical-browser check. Headless PDF generation and a
`printing:true` response do not prove that a print dialog opened. WordCraft uses
an asynchronous PDF-frame completion receiver, reports load/print errors and a
bounded timeout, and prevents an expired request from opening a late dialog.
Browser acceptance never proves physical printing; printer choice and cancel
remain browser/user operations. Tests open Chromium's real preview and cancel it
without sending a job.

The hosted CSP must match that actual path. WordCraft needs `blob:` in frame-src
on `/wordcraft/index.html`; the desktop/other apps retain their original policy,
and object-src remains disabled. Never disable CSP wholesale. Account-save and
local-recovery messages also remain distinct, readable states; narrow-window
ellipsis must retain complete accessible/hover text. These output changes are
qualified on the selected WordCraft source and deployed in the [output release](../deploy/WORDCRAFT-OUTPUT.md),
with 51 actual-browser checks each locally and hosted. Earlier release counts are
historical; another Craft app still needs its own model/interface qualification.

## Community attribution in the unified desktop

The user's policy is to build a useful personal WebOS on top of community work,
while making it available to others who want it. Preserve upstream authorship,
licences, contributor/model credits, source links, community history and About.
Streamlining application chrome must not hide that provenance or imply WebOS
created the underlying application.

For WordCraft, the separately requested ribbon/backstage Discord shortcuts were
removed while About was retained. For PdfCraft, the follow-up removes its
prominent top-right shortcut; About's community links, contributor information,
Help and Home links stay intact. Apply the actual requested scope to each app.
Brand artwork permissions are separate from plain-text attribution: observe the
fork's mark restrictions while retaining permitted credits and community links.
