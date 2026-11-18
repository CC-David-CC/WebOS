> **Active decisions — 2026-11-18 UTC**
>
> The user approved parallel GridCraft/DeckCraft implementation after the guide
> and plans were reviewed; both branches now contain implementation WIP. The
> current private checkpoint linked from START-HERE owns their actual status.
> The user subsequently selected all17 Craft apps for eventual integration.
> Every app must be represented in the menu, disabled until qualified. Earlier
> planning-only and proposed-candidate text below is historical, not exclusion.
> Complete the two current apps, then assess each remaining app against C01–C20
> and implement its first usable account-backed workflow. Do not retire legacy
> apps or add a separate preview initiative before the user decides.

# Next Craft integration branches

Current phase: site integration from the completed organized source tree.

Decision, 2026-11-17: finish the current PdfCraft follow-up and the shared guide
first. Prepare both plans before considering parallel implementation. No
GridCraft/DeckCraft implementation, merge, build or deployment is authorized by
this planning record. Read-only source inspection supplied the findings below.

The PdfCraft follow-up is now deployed and verified, and the common guide and
these plans are ready. See [the completed PdfCraft report](../deploy/PDFCRAFT.md).
Neither proposed next-app branch has started implementation. PhotoCraft was
suggested as a possible third app; that choice and its specific plan remain open.

Use [the shared contract](CRAFT-INTEGRATION-GUIDE.md) and
[build execution plan](CRAFT-BUILD-EXECUTION.md). GridCraft is the proposed next
implementation: spreadsheets add a distinct everyday workflow alongside Text,
WordCraft and PdfCraft. DeckCraft follows, or can run separately after the user
chooses parallel implementation and the shared boundaries are stable.

## Branch and ownership rules

Each app already has an independent repository. A branch belongs to that repo;
changing only a parent branch does not isolate edits in an app checkout.

| Owner | Proposed working branch | Base to review before creating it | Delivery |
|---|---|---|---|
| GridCraft | `webos/gridcraft-document-host` | Existing fork `2f52ae5c7eeb147a539dfc74612be4e49de328ff` | Native hooks, app-owned adapter/build inputs, native/adapter tests. |
| DeckCraft | `webos/deckcraft-document-host` | Existing fork `45463e6ba33aea1cdd664a27c4afd017ba35275a` | Complete existing account adapter against the current document contract. |
| Parent integration | `webos/craft-office-assembly` | Accepted parent after current PdfCraft follow-up | Public composition, Files associations, whole-system tests and selected child pins. |

These are proposed names, not claims that the branches/worktrees were created.
If parallel work is approved, give each app one owning agent and its own
source-only worktree outside the live assembly. The integration owner alone
changes shared Desktop/Runtime/Storage contracts and parent composition. App
agents report a concrete contract gap rather than editing those shared owners
concurrently. Shared-library changes get their own review/qualification before
either app depends on them. Do not copy target directories into worktrees.

Local inspection found both app checkouts clean on `webos/integration`.
Their local `main` refs match their recorded `upstream/main` refs, but neither
`main` is an ancestor of the selected fork. Thus "already organized" does not
mean "merged with current recorded upstream". The recorded upstream refs are:

- GridCraft: `1476d4e7abef470886aeb5a1a7d870c9377a3050`.
- DeckCraft: `6c52db01727b4d3cfb2e122770ce76de6a6fa71e`.

No network freshness claim is made. At implementation start, inspect the
divergence and fetch verified public upstream if needed. Choose and record the
base; merge an upstream update on a separate review branch if needed. Do not
reset the accepted fork, blindly merge all PRs, or combine upstream reconciliation
with an unreviewable host-integration diff. Preserve `main` as upstream tracking.

## GridCraft plan

Source: `apps/gridcraft/`. Version at selected fork: 0.19.1. Important definitions:
`apps/gridcraft-web/src/host.rs`, `prefs.rs`, `web.rs`;
`crates/ui-egui/src/services.rs`, `control.rs`, `formula_bar.rs`;
`crates/engine/src/lib.rs`; `crates/ui-egui/build.rs`.

Observed gaps, not assumptions:

- No app-owned `webos/` adapter/portable recipe exists at this selected source.
- The web bridge installs a download callback without an identified save ticket.
  `Bridge::sync` sets the active document's saved workbook snapshot after posting
  bytes, before durable server confirmation. It keeps only a basename, treats
  `saveAs` as false and cannot identify which save/export binds a document.
- Browser preference keys are origin-global. Hosted account state must be
  scoped without importing another account's legacy preferences.
- The native cell/formula-bar editor has pending edits outside the committed
  workbook. Saving/recovery must handle that native state deliberately.
- The root manifest uses craft-libs `bb57d422…`, while the browser host dependency
  uses `aa84415b…`. Inspect actual lockfile/API compatibility; do not replace all
  pins or reuse WordCraft's build graph by assumption. Fonts are an explicit
  build input; no top-level font/translation revision files were found.

| Phase | Concrete work | Exit evidence |
|---|---|---|
| G0 — baseline | Read app rules, choose source base, record lock/input pins and actual native/browser commands; capture pre-existing failures. | Reproducible input manifest and baseline receipts. |
| G1 — native contract | Add exact document/revision inspection, correlated adoption and prepared saves; preserve later edits and undo. Route native New/Open/Close to Desktop. | Native tests for stale/foreign/duplicate replies, delayed edits, Save As identity, clean blank and explicit blank Save. |
| G2 — account adapter | App-owned synchronous mount/ready/retry/dispose using public Accounts/Storage/Runtime interfaces; conditional Save/Save As, copy exports, exact authorization. | Adapter tests for changed targets, conflict/collision/cancel/unknown outcomes and disposal; no alternate account store. |
| G3 — recovery/profile | Snapshot workbook plus pending cell/formula edits natively; restore sheets, formulas, formats and required embedded content. Account-scope preferences/recent paths/fonts if present. | Refresh/minimized/orphan recovery, A→B→A isolation, changed saved base requiring Save As, failure retaining earlier checkpoint. |
| G4 — browser production | Pin font/assets, keep notices, package the actual WASM graph under existing CSP; add explicit parent composition and `.xlsx` default. Preserve `.txt`/`.py` Text routes. | Offline build receipt without original source access; actual account workbook opened from Files and native Open. |
| G5 — qualification | Build a two-sheet workbook with formulas referencing both sheets, formatting and ordinary edits. Save/Save As/reopen in a fresh context; verify values/formulas/sheet identity and later-edit recovery. | Native parse/round-trip evidence plus actual rendered browser checks and strict console/network checks. |

First milestone is usable account-backed XLSX creation/editing, not a rewrite of
the calculation engine or a promise that every format/tool works. Separately
classify CSV/TSV import/export, XLS/XLSB/ODS imports, password handling, PDF export
and browser printing. CSV must not become the recovery format for a multi-sheet
workbook. Recalculation and long-running work need cancellation/resource limits;
do not enable arbitrary script execution or delegated agent authority implicitly.

## DeckCraft plan

Source: `apps/deckcraft/`. Important definitions:
`webos/index.mjs`, `account-files.mjs`, `HOST-SAVES.md`, `ACCOUNT-FILES.md`,
`package-browser.mjs`; `apps/deckcraft-web/src/host.rs`;
`crates/ui-egui/src/host_save_tests.rs`, `host_open_tests.rs`;
`crates/engine/src/host_save_tests.rs`.

Existing work worth retaining:

- Identified native save confirmation, bounded pending/unknown saves, correlated
  binary adoption and captured native command targets already exist.
- A synchronous human-authorized account view/domain and CSP packaging helper
  have historical isolated native/browser/signed-account evidence documented in
  the repo. Those results are not qualification of today's classic Desktop.
- Native save settlement retains later edits; exports/Print use an uncorrelated
  download callback. The adapter explicitly refuses to call those account saves.

| Phase | Concrete work | Exit evidence |
|---|---|---|
| D0 — baseline | Reconcile selected fork/upstream deliberately; reproduce relevant existing tests before replacing working hooks. Pin actual fonts, assets, toolchain and graph. | Reviewed gap report and baseline commands/exits. |
| D1 — contract completion | Confirm canonical saved paths reach native identity; audit the current active-document precondition and multi-document view. Adopt Desktop-owned document views and both Open activation routes. | Native/adapter tests for exact identity, asynchronous target changes and later edits; no duplicate editable instance of one account resource. |
| D2 — recovery/lifecycle | Add native presentation recovery including pending text/media references; use Runtime journal and current close approval/pause lease protocol; clean blank remains explicitly saveable. | Native fidelity plus refresh/minimized/orphan/Save-Discard-Cancel/account-switch tests. |
| D3 — file actions/profile | Complete account Save As destination UI and copy exports, account-scoped settings/fonts/recent state, native completion/focus, single host navigation warning. | Actual human File controls and delayed/failed/conflicting/unknown writes; About/credits preserved. |
| D4 — assembly/production | Connect current Desktop/Files and `.pptx`; replace implicit sibling build inputs with explicit pinned public inputs. Inspect the existing shared web-host path dependency before changing it. | Source-only portable build and exact payload/CSP/notice receipt; unchanged app payloads reused. |
| D5 — qualification | Edit at least two slides with title/body text, theme, image and notes; Save/Save As, close/reopen, Files/native Open, fresh-context retrieval and recovery. Verify presenter/fullscreen entry/exit independently. | Native presentation round-trip and actual browser rendering; no claim of every transition/media codec/export working. |

Existing DeckCraft account tests are a head start, not permission to skip present
recovery, profile or Desktop tests. Presentation/media lifetime differs from a
word-processing document: define whether closing a view ends playback, and do not
destroy an independently owned job by accident. Keep browser fullscreen and
clipboard user activation under the human's control. Qualify account-bound media
and export assets rather than saving broken local filesystem references.

## Integration and acceptance sequence

1. Finish PdfCraft follow-up and freeze its tested source/artifact references.
2. Finish common guide and agree the branch plans; verify build host readiness.
3. On an explicitly selected next scope, implement GridCraft through G0–G5.
4. If parallel implementation is later approved, DeckCraft may run D0–D5 in its
   own repo/worktree. No shared-owner edits or concurrent writes to one Cargo
   target directory. The integration owner reviews each child independently.
5. Promote qualified child commits separately, then pin them in a parent
   integration branch. Test interactions after composing both; a successful merge
   is not compatibility proof. Keep the live accepted release deployable.
6. Deploy only under explicit user authorization, with exact artifact hashes,
   backend/beta continuity guards, rollback and scoped hosted acceptance.

Do not make one unreviewable "all Craft apps" branch. Native domain behavior stays
with its app; common public host mechanics stay with their owner. Plans establish
the work to perform and the evidence needed, not completed features.

## VectorCraft and FigCraft preparation

Use the [shared acceptance contract](CRAFT-INTEGRATION-GUIDE.md) for both apps.
The existing Desktop owns windows, activation, launcher registration and close
approval. The existing Accounts and Storage components own authentication and
server revisions. Give each app a component worktree and a `webos/...` branch.
The main integration owner reviews launcher and file associations and qualifies
the assembled site. Reuse the existing pinned SDK and verify separate target
paths and free space before starting concurrent compiler jobs.

| App | Source and suggested branch | First work |
|---|---|---|
| VectorCraft | `apps/vectorcraft/` at `4830ea0e833f`, `webos/vectorcraft-document-host` | Verify the Trunk package and checked-in font manifest. Exercise ordinary `.vectorcraft` Save and the native recovery store. The web shell currently uses local download delivery to save files and an origin-wide recovery prefix. Trace the native save completion and recovery store before adding confirmed Storage writes and account-scoped journals. |
| FigCraft | `apps/figcraft/` at `bad07e443324`, `webos/figcraft-document-host` | Verify the Trunk package and its fonts. The same-origin bridge remembers a filename on `postMessage`; `save_download` treats delivery as success. Replace that acknowledgement in the hosted editor with an identified server-confirmed save. Reuse the native `.figcraft` recovery codec for documents, versions and branches. Scope the browser recovery and author preference to the active account. |

VectorCraft acceptance uses a layered drawing with an edited path, fill, text,
and embedded image. Check geometry and font fidelity after Save, Save As,
restoration, and a Files reopen in a fresh browser. Exercise SVG as a copy and
check that it preserves the active native account-file binding.

FigCraft acceptance uses frames, a reusable component and an instance, and an
embedded image. Check component relationships and native version history after
Save, Save As, restoration and fresh-browser retrieval. Exercise SVG/PDF copies
independently of the native file path. Determine which linked resources require
embedding before delivery across browsers.

For each app, select one stable native object ID and exercise an approved
inspection and a reversible edit through the editor's existing command path.
Verify that a grant for one view or resource cannot edit a second one, and that
the editor protects pending human input.

## DesignCraft preparation

The selected workflow passed and went live. See the
[DesignCraft release record](CRAFT-INTEGRATION-LOG.md#designcraft-release-on-ksucodes).

Start from `apps/designcraft/` at `59c6fa1b4947` on
`webos/designcraft-document-host`. Reuse Desktop window ownership and the shared
Craft account adapter. The native editor already has document identity,
revisions, ZIP serialization, byte Open and PDF export.

1. Capture the native document snapshot for Save and Save As. Bind the account
   path and mark that captured revision clean after the matching Storage
   acknowledgement. Apply the same rule to close-and-save. Keep export and
   Save a Copy independent of the current binding.
2. Give each account window one native project. Route New and Open through
   Desktop, and guard other paths that can create a native tab, including Data
   Merge, page-to-document, imports and drops. Persist recovery from the same
   native snapshot path. Test scoped inspection and a native frame edit with Undo.
3. Test a layout with editable text, style changes and embedded artwork. For an
   imported native project that references external artwork, show which links
   need attention and use account file selection to relink or embed full
   originals. Verify the artwork in a PDF produced after a fresh browser
   reopens the account project.
4. Run locked native CI and the browser build from the exact selected tree.
   The R730 can run offline compile and packaging using stable Rust, the
   portable Trunk executable, wasm-bindgen 0.2.129 and font pin
   `b076417b5880`. Keep the signed Chromium workflow on the laptop. If the R730
   runner blocks loopback, run the affected exact binaries in the laptop's
   loopback runner and record both results.

## SoundCraft preparation

The first account bridge is at `e196254ee15f` on
`webos/soundcraft-account-session`. It uses the native portable bundle
serializer for account Save, Save As and recovery. It adopts the account
binding after Storage confirms the captured session and preserves edits made
while the write is pending. Native Open, Save and recovery tests passed,
along with the account WASM compile check. Browser qualification is next.

`.scraft` projects can reference audio beside
the session file. Test them with explicit media selection and missing-file
feedback before adding their default association.

Qualify a two-track session with a short synthetic WAV and a native edit.
After fresh-browser reopen, verify audio samples, timing and an exported WAV.
Start and stop playback with a browser user gesture. Verify that closing or
signing out retires that view's player and preserves independent views.

The pinned dependencies and locked offline WASM compile checks passed on
the R730 for SoundCraft, FilmCraft and EffectCraft. Each app has its own
`Cargo.lock` and pins several revisions of the on-disk shared
[Craft libraries](../libraries/craft-libs/). Keep those revisions during
baseline testing, including where two apps use different media crate pins.
