# Files and CAD successor handoff

Checkpoint date: 2026-11-04. This is the starting plan for another integration
agent, including Sol. **Files and CAD Gate 1 are incomplete.** The new storage
and CAD work is development code, not a completed beta release. Writing this
handoff does not declare the active goal complete or paused.

The immediate job is to finish dependable saved data and safe dependent CAD
regeneration, then qualify useful parametric parts through the same UI and
agent commands. The long-term CAD 1.0–6.0 program informs these boundaries;
it is not the next agent's first implementation task.

## Read first

Read these in order; use the rest as references instead of restarting the
whole historical audit:

1. This handoff and `goals/FILES-CAD-NEXT-AGENT.txt`.
2. `CAD-CORE-SEPARATION.md` — current architecture and engine-mount requirements.
3. `ACTIVE-FILES-CAD-RELEASE.md` — the release acceptance audit.
4. `FILES-BETA-RELEASE-READINESS-2026-11-04.md` — exact observed beta boundary,
   storage migration, capacity and deployment gaps.
5. `WEBOS-WORK-QUEUES.md` — update this operational ledger as work progresses.

Then read JSketcher's `docs/HEADLESS-SKETCH-SOLVE.md`,
`test/webos/plate-parametric-README.md`, `docs/CRAFT-REPLAY-NORMALIZATION.md`
and `docs/WEBOS-REPRODUCIBLE-BUILD.md` for the first CAD task.
`CAD-ENGINE-GATE-1.md` and `JSKETCHER-FOUNDATION-MATRIX.md` define the larger
foundation acceptance; `CAD-ENGINE-GATES.md` indexes the later gates.
The complete original goal and amendments are preserved in
`goals/FILES-JSKETCHER-RELEASE-20261103.txt`.

## Repositories and exact starting points

| Repository | Integration branch | Code checkpoint before this handoff |
|---|---|---|
| `box-git:/srv/data/git/CodiServer-distro.git` | `integration/files-jsketcher-release-20261103` | `73c1e8b13` |
| `box-git:/srv/data/git/JSKetcher.git` | `integration/files-cad-release-20261104` | `7d08c15902de5bd7fcf3527a7b53842917b4e1a5` |

The desktop branch's later handoff commit adds documentation to that code
checkpoint. Verify branch tips with `git ls-remote` before starting; another
agent may have advanced them. Do not substitute `main`, `simplified`, an old
`webos-integration` tip, or an old research branch for these bases.

Backups use the same integration branch names at:

- `r730:/mnt/data10tb/git/CodiServer.git`
- `r730:/mnt/data10tb/git/JSKetcher.git`

Example fresh working copies:

```sh
git clone --branch integration/files-jsketcher-release-20261103 box-git:/srv/data/git/CodiServer-distro.git webos
git clone --branch integration/files-cad-release-20261104 box-git:/srv/data/git/JSKetcher.git jsketcher
git -C webos status --short --branch
git -C jsketcher status --short --branch
git -C webos rev-parse HEAD
git -C jsketcher rev-parse HEAD
```

Make new named worktrees/branches from verified bases. Preserve the user's
dirty `/home/dflanag3/CodiServer/desktop-preview/SIMPLIFIED` checkout. Current
integration worktrees on this workstation are `/tmp/codi-webos-cad-merge` and
`/tmp/codi-jsketcher-release-integration-20261104`; they are conveniences, not
the source of truth for another machine.

### Integrated since the initial handoff

JSketcher `2b3f2c0fdfd84bcda7db4f5244e1da40b4113813` now reconciles the
axis/admission work (`68e51e03`), private atomic replay (`35f3e2ef`), lifetime
and staging guards (`1be74426`, `274a361c`) and subsequent document/surfacing
boundary fixes (`aff1befe`). Do not merge the older `089ed178` tree again or
reintroduce its global registry overlay. Normalization and feature-ID allocation
remain integrated.

The lead's combined app build/typecheck, 11 real Chromium regression scripts
and 9 unit checks pass. Read the fork's
`docs/DOCUMENT-LIFETIME-REPLAY-20261104.md` and machine-readable
`test/webos/document-replay-evidence-20261104.json` for exact tested source,
asset hashes, negative controls, commands and limits. This is not the full CAD
gate. The newer package and research results below supersede the old
not-yet-packaged status.

Desktop `73c1e8b13` packages fork `d3d36bc5`, including ordinary OCC fillet/
chamfer guards and visible errors, with both required worker assets. Nine lead
browser runs pass: two signed host workflows at phone/1080p/4K plus the three
fillet/chamfer/refusal regressions. The dependent plate is opened through Files,
saved through My files with exact server bytes, then reopened in a fresh signed
session. See `evidence/cad-packaged-workers-20261104.md` and its JSON receipt.

Fork `7d08c159` additionally merges `1a6e5b77` engine-mount research, which is
not connected to the application or selected by the package. Real Manifold
and OCI worker boxes pass independent lead checks. The selected interpreter
does not export the legacy SPI box/dispose functions. Its original wrapper
requires `window`; the research wrapper uses a portable exchange callback.
Whole-worker termination is its current cleanup boundary. Broad bindings,
trusted installation, resource budgets and production integration remain open.

Desktop `2e312b7975d92882c9ff74803066abe089d9ca59` integrates the Files-only
beta candidate builder and tests. Candidate `3ad04c48…` supersedes `feaa1c6f…`,
which had a real session-layout return-value defect. The agent exercised signed
controlled-tab migration, Files/Text, sign-out cancellation/failure/stale worker
and second-account login; the lead independently verified the sealed 87-file
inventory. Actual derived issuer/guest config tests pass separately. These are
isolated fixtures, not a durable managed activation/recovery operator. See
`../research/beta-opfs-release/README.md`.

Files checkpoint `b391e259b` adds signed account/file continuity across the exact
issuer restart and a filesystem/process-tested forward-only floor journal.
Lead journal fault tests pass. Managed adapter prototype `e4a6c2ec6` stays on
`research/beta-opfs-managed-bind-20261104`, based on hosting `cf04068aa`; do not
merge/deploy that unrelated hosting branch wholesale. Damaged-journal re-gating,
actual protected launcher/issuer switching, custody and host capacity remain
unqualified. The account volume had 208.8 MiB above its 5 GiB reserve at the
recorded check. Read `../research/beta-opfs-release/CAPACITY-2026-11-04.md`.

## What works and what is still open

These are bounded results. A passing small model is not a completed CAD gate;
one worker is not a browser-wide RAM guarantee.

| Area | Demonstrated | Open or failing |
|---|---|---|
| Saved files | Opt-in OPFS My files; signed operations; sealed candidate/controlled-tab migration; actual signed continuity across issuer restart and tested floor journal. | Qualified managed transition/recovery operator, headroom and full app compatibility. |
| Conflicts | Two independent Chromium processes/profiles, actual Files/Text offline edits, cancellation, a newer edit during resolution, keep-both and fresh reopen. | Final assembled release and broader failure matrix. |
| Interrupted transfer | Real committed-upload reply cut reconciles without blind duplicate write; actual download cuts preserve complete verified generations and earlier bytes. | Crash during publication, physical power loss, exact release transition. |
| Changed data | A signed 128 MiB file's one-byte edit sent 71,470 request-body bytes in the recorded run; final local/server hashes agreed. | This excludes responses and HTTP/TLS overhead. SDK still builds a Blob before OPFS capture; no complete zero-copy or total-memory claim. |
| File worker resources | One cooperating VerifiedContent worker across tabs; queue, cancellation, timeout and renderer-crash recovery. | SDK/app workers and allocations are outside that cap. Sampled summed Chromium RSS was about 1.32 GiB in the large-file run, with shared pages counted multiple times. |
| Temporary Linux | Real v86 boot; Files can browse guest home; identically named My files stays separate; guest reboot resets temporary content. | This is not a synchronized Linux Account mount. All-app compatibility remains. |
| CAD host integration | Packaged fork `d3d36bc5`: actual signed small-model and dependent-plate save/reopen with both workers, independent OCC/Native windows, account denial and closed-command rejection at simulated phone, 1080p and 4K. | Large-model resource qualification, shared agent workflow, heavy snapshot/stringification and public release remain. |
| Headless sketch solve | Actual IO/solver in a real worker, no canvas/DOM/fake editor; restricted plate fixtures, residual and finite-geometry checks. | Not all entity/constraint families, exact general DOF, arbitrary region extraction or all kernels. |
| Dependent plate | 100×50×20 → 150×30×20 with centered Ø10 hole and four constrained corner holes, ordinary OCC fillet/chamfer; undo/redo, geometry rays, native-v2 and signed reopen. | Feature patterns, inch display and full shared-agent workflow remain. Native sketch extrusion and fillets are explicitly unsupported in these paths. |
| Rejected CAD regeneration | Impossible 15×15 edit retains last complete plate, marks it stale and refuses save/3MF; correcting it regenerates. Held replay leaves accepted registry/model intact. | Broader operation-context/native-handle isolation, full feature chain and resource bounds. |
| Document lifetime | Monotonic generation plus exact service/storage ownership; held validator/replay reset, staged rollback, late reply, service replacement and surface cleanup/reload controls pass. | All async services and noncooperative kernel interruption are not qualified. |
| Material-aware 3MF | Existing research and independent limited lib3mf fixtures. | Full editable enclosure/body/lid/inset workflow and manufacturing handoff remain unqualified. |

Key desktop evidence: `evidence/storage-product-integration-20261104.md`,
`evidence/cad-files-combined-20261104.md`,
`../tests/files-two-profile-conflict.md`,
`../tests/files-desktop-signed-fixture.md`,
`../research/opfs-storage/DOWNLOAD-TCP-CUT-20261104.md`, and
`../research/opfs-storage/WORKER-BUDGET-128-20261104.md`.

## Current decisions and guardrails

- Chromium is the supported browser target for this work. Phone layout tests
  are emulation unless explicitly identified as physical-device evidence.
- The user authorizes a deeper rewrite of coupled JSketcher internals. Preserve
  useful tested components and already integrated upstream features. Do not
  repeat the old upstream merge or replace working code just to start over.
- **OpenCascade is preferred; Native Mesh/Manifold is secondary.** Properly
  support each library's relevant capabilities, beyond today's menu subset.
  Use discoverable, versioned engine mounts/adapters; retain engine-specific
  capabilities rather than reducing everything to their common subset.
- Engine combination requires explicit representation conversion, tolerance,
  units, provenance, ownership and identity-loss rules. Never silently switch
  engines after a failed operation. A tessellated approximation is not an exact
  replacement for the authored B-rep. See ENG01–ENG08 in the core checklist.
- Production computation belongs in workers with explicit model data, not an
  invisible editor, fake `window`, canvas or ToolManager. The real UI may render
  to a canvas. Heavy hashing, parsing and geometry processing must not block it.
- Keep representability, constraint satisfaction, planar regions, kernel output
  validity and dependency meaning as five separate validation responsibilities.
- One revisioned authored model and one validated command path serve people and
  agents. Jobs cannot bypass account, expected-revision, disposal or stale-result
  checks. Content hashes are not authorization or edit/lifetime generations.
- My files is the shared account-bound storage authority. Preserve opaque local
  versions/CAS, create-only `expected=null`, conflicts and uncertain-write
  reconciliation. No app-private account mirror. Temporary Linux is separate.
- Keep production CSP; no `unsafe-eval` or test CSP bypass to make a library work.
- No GitHub publication for JSketcher now. Back up source/tests/notes to box-git
  and R730. The user authorizes new LAN repos and source clones where needed.
- R730 storage/compute and llm-60 compute/testing are authorized. R730 works.
  llm-60 access was not established: no verified SSH host-key pin was available.
  Do not bypass host verification; obtain a trusted fingerprint/username only if
  that machine becomes necessary. R730 lets current work continue.
- Preserve main `ksu.codes`, `/desktop/`, account data, keys and unrelated work.
  Beta is the iteration target. No new router ports are currently needed.
- Do not repeatedly ask permission for authorized tests, builds or scoped
  implementation. Review the concrete deployment artifacts and recovery path
  before any hosting mutation. Never hand-edit generated Caddy.

## First bounded work packages

Use one lead and three agents in isolated worktrees. Assign paths before edits.
The bounded implementation/test work in packages 1A–1C and the local combined
checks in package 2 have now passed the recorded controls. Extend unresolved
coverage and proceed to host packaging; do not redo completed merges.

Each agent returns a commit, tests/negative controls, limitations and evidence.
Shared contracts, merge decisions, release packaging and hosting have one owner.

| Order | Owner | Package and owned area | Acceptance and stopping point |
|---|---|---|---|
| 0 | Lead | Verify refs, candidate ancestry, resources and prerequisite artifacts. | Clean branches; reproducible dependencies or explicitly recorded gaps; no accidental deployment. |
| 1A | Lead | Document-lifetime contract: `projectBundle.ts`, `projectManager/projectManagerBundle.ts`; coordinate its API with replay owner. | Synchronous monotonic generation on document replacement/reset/restore entry; every async result checks captured generation and current owner. Reset/reopen of identical content cannot admit an old result. |
| 1B | CAD replay agent | Atomic replay: `craft/craftBundle.ts`, private evaluation registry, non-rendering sketch initialization, narrow same-ID scene replacement. | Complete candidate evaluated privately; publish once only when all required operations and guards pass. Failed replay retains the last complete accepted solid and inspectable failed intent. No mutation of accepted inputs. |
| 1C | CAD core agent | Review axis-domain/admission candidate, own `sketcher/headless/` and its tests. | H/V domains correct; single cooperating CAD worker, bounded queue/total deadline, queued cancel, renderer-crash progress. No overlapping edits to replay or project lifetime. |
| 1D | Files agent | Beta-derived immutable storage package and transition/operator work from the readiness plan. | Preserve selected guarded baseline and full catalog; prove v2 migration/forward recovery; no independent live mutation. Lead owns shared host changes. |
| 2 | Lead | Merge 1A–1C and rebuild the exact fork; review rather than assuming each isolated pass composes. | Run last-valid, stale/reset, successful five-hole edit, undo/redo, save/reopen and normalization/allocator controls on the combined build. |
| 3 | Lead plus independent review | Package new worker assets and exact fork in the desktop app; source/notices/CSP checks. | Real signed My files workflow at phone/1080p/4K; independent windows/account change/disposal; inspect actual served hashes. |
| 4 | Reassign agents | Gate 1 matrix and coupled rectangle chain, then bracket/enclosure through UI and discoverable commands. | Useful parametric part edits survive or fail explicitly; both engine statuses recorded. Unsupported and untested never count as pass. |
| 5 | Manufacturing owner after dependencies | Core 3MF body + separate lid + aligned label region. | Independent units/dimensions/transforms/materials: two print objects, three assigned regions; native project remains editable source. No physical printer/Bambu requirement. |

Engine capability inventory, provenance and adapter-contract design may run in
parallel on owned documents/modules when a lane is free. Do not make completion
of every engine capability a prerequisite for fixing today's rejected edit.
Conversely, do not close the broad engine-support queue after wrapping only the
few operations currently used by the desktop.

### Document generation and atomic replay details

The implemented API is `ctx.projectService.documentGeneration`,
`documentSignal`, `beginDocumentChange()`, `isDocumentCurrent(generation)` and
`dispose()`. The combined tests cover reset/reopen of identical content,
service replacement, old callbacks, staging ownership and surface domains.
Continue qualifying callers against this contract; do not recreate the API.
Account/window lifetime checks remain separate. A content hash, equal history
or re-created face ID cannot distinguish identical documents across lifetimes.

An occupied-workspace restore must reject **before** starting a replacement;
repeat the empty check after validation. `craftService.reset()` replaces craft
history, not all document domains. Use `projectService.empty()` for a new blank
document. Explicit same-project `loadStrict()` preserves its saved surface
sidecar; a new native envelope supplies its own surface section.

Guard both before and after worker/restore awaits. Restore must distinguish
its own intentional generation transition from an unrelated replacement; do
not update a guard opportunistically to whatever generation is current. Cover
JSON restore, Blob/worker restore, empty/reset, cancellation and disposal.

Atomic replay must preserve a separate last-complete result even across
deliberate history navigation. Evaluate against a private registry and avoid
mutating accepted bodies through shared references. Publish the completed
candidate only after validation and lifetime/revision checks. Scene views must
replace a changed model object even if its stable ID is unchanged. Label stale
geometry and failed/stale descendants; never save partial output as success.

The retained negative control is
`test/webos/plate-parametric-last-valid-browser.test.cjs`. Its impossible 15×15
edit must keep the previous complete 100×50 five-hole solid, not merely the
preceding plane or partial seven-face output. The successful resize must still
work; refusing every edit is not the fix. Add held-worker/reset/same-content
reopen, competing replay, failure-then-valid-edit and undo/redo tests.

## Reproduction and portability

Use Node 24.22.1, Chromium and `puppeteer-core` 24.35.0 for the recorded browser
checks. Python needs aiohttp, argon2 and cryptography; the repository's pinned
requirements and app-builder locks remain authoritative. Caddy is needed for
the isolated signed fixture. Use loopback and disposable profiles/accounts.
Choose unused ports; stop only processes owned by your fixture.

**A fully independent clean-machine release build is still an open gate.**
Source and recipes are backed up, but runtime provenance, some artifact
retrieval and final combined build qualification are incomplete. Do not claim
that cloning either repository alone supplies a ready release.

### CAD worker checks without a canvas or CAD engine build

On the current integrated fork, with locked dependencies installed:

```sh
CYPRESS_INSTALL_BINARY=0 npm ci --ignore-scripts
node build/precompile-numeric.cjs
./node_modules/.bin/webpack --config build/webpack.headless-sketch-worker.cjs
./node_modules/.bin/webpack --config test/webos/headless-sketch-client.config.cjs
./node_modules/.bin/webpack --config test/mechanical/webpack.axis-angle-domain.config.cjs
node /tmp/codi-axis-angle-domain/tests.cjs
```

The two test configurations intentionally generate disposable files under
`/tmp`. The source and configuration are in Git. `puppeteer-core` is not a
JSketcher dependency; install the test harness separately. Run from the fork:

```sh
npm install --prefix /tmp/codi-sketch-test-harness --no-save puppeteer-core@24.35.0
export PUPPETEER_CORE_PATH=/tmp/codi-sketch-test-harness/node_modules/puppeteer-core
export CHROMIUM_PATH=/snap/bin/chromium
mkdir -p /tmp/codi-headless-web/static /tmp/codi-headless-web/lib
cp .build/headless-sketch-worker/worker.js /tmp/codi-headless-web/static/worker.js
cp web/lib/verb.js /tmp/codi-headless-web/lib/verb.js
cp test/webos/headless-worker-{stall,wrong-revision,malformed,delayed}.js /tmp/codi-headless-web/static/
printf '<!doctype html><title>Sketch worker test</title>\n' > /tmp/codi-headless-web/index.html
python3 -m http.server 19340 --bind 127.0.0.1 --directory /tmp/codi-headless-web
```

Select the installed Chromium path on the new machine. Keep the static server
in its own terminal. It is the minimal worker harness, not the full-app strict
CSP qualification. Numeric execution does not need a rendered editor. See the
candidate's `docs/HEADLESS-SKETCH-SOLVE.md` and test headers for scope.

`headless-sketch-admission.test.cjs` launches and cleans its own browser. For
the other tests, start a disposable CDP browser in another terminal:

```sh
CAD_TEST_PROFILE=$(mktemp -d /tmp/codi-sketch-profile.XXXXXX)
"$CHROMIUM_PATH" --headless --disable-gpu --remote-debugging-address=127.0.0.1 --remote-debugging-port=19331 --user-data-dir="$CAD_TEST_PROFILE"
```

Keep this isolated from an everyday browser profile and close only this process
after testing. Use available ports; `CODI_TEST_CDP` and `JSKETCHER_TEST_URL`
override the default loopback CDP 19331 and fixture 19340 URLs. In a test terminal
with the harness environment exported, run:

```sh
node test/webos/headless-sketch-admission.test.cjs
node test/webos/headless-axis-domain-negative.cjs
node test/webos/headless-axis-domain.test.cjs
node test/webos/headless-sketch-worker.test.cjs
node test/webos/headless-sketch-lifecycle.test.cjs
node test/webos/headless-sketch-deadline.test.cjs
```

The axis negative control previously failed at `e20e27bd`; the current fix
must satisfy the intended invariant. The admission tests establish Web Lock
release, disappearance of the old dedicated Worker target and queued progress
after renderer crash, **not OS memory reclamation**. There is no separate
committed execution receipt for that candidate; rerun for fresh evidence.

### Full CAD build and integration checks

Follow JSketcher's `docs/WEBOS-REPRODUCIBLE-BUILD.md`. Prepare exact source-built
OCCT/Manifold artifacts through `build/prepare-webos-runtime.cjs`, then run:

```sh
CODI_EMBED_NUMERIC=1 CODI_EMBED_MANIFOLD=1 npm run build
CODI_EMBED_NUMERIC=1 CODI_EMBED_MANIFOLD=1 ./node_modules/.bin/webpack --config test/webos/webpack.config.cjs
npm run check-code
```

The exact eight preparer runtime inputs are also preserved, independently
content-verified, at `r730:/mnt/data10tb/codi-cad-runtime-inputs-ced603b99f8d`.
Its `manifest.json` SHA-256 is
`ced603b99f8d27577ba43256e6c391627a7e52f7465784a28ebf63b6b01aa6a5`.
Copy it to a private local directory, verify the closed file inventory and
every recorded size/hash, then pass its `manifold/` and `occt/` directories to
the desktop preparer. `evidence/cad-runtime-inputs-20261104.json` records paths
and hashes. This is a LAN backup of selected research prerequisites, not public
distribution clearance or a guarantee of a fully offline build; locked npm
dependencies still require installation. No generated app/dependency tree is
committed to Git.

Serve `dist` with production-style CSP, permitting WebAssembly but not
JavaScript `unsafe-eval`. Use the plate README and actual browser tests,
including `plate-parametric-centered-browser.test.cjs`, the last-valid control,
the document/surface/service replacement controls and `axis-domain-project-restore.test.cjs`.
Inspect assertions and their scope, not only the test's filename or exit code.

OCCT source archive is on R730 at
`/mnt/data10tb/CodiServer/source-archives/occt-interpreter/5efaf53accb45bac475155fc4d5552642c19e91e/source.tar.gz`,
SHA-256 `86ccaa4d1974b15a1ee8a26e69db20e7c04f5000ffd4924008cebcd1a82fb9e4`.
Read `docs/occt-source-rebuild-20261102/RESULTS.md` and
`third_party/occt-interpreter/README.md`. Independent complete OCCT builds are
not proven bit reproducible; a matching hash alone does not close source/notice
requirements. Manifold's CSP-safe source build is documented in
`test/webos/README-surfacing-research.md`. Do not substitute unverified npm
binaries or publish runtime inputs before the recorded distribution gaps close.

The desktop preparer at `apps/system/jsketcher/prepare.py` now pins `d3d36bc5`,
including both content-addressed workers. Further updates require an exact
commit, emitted worker graph and notice/source inventory, followed by preparer/package
tests and signed host tests. A stale `dist` can pass old tests while new source
remains untested: always record the built commit and served asset hashes.

### Files tests

Start with the staged storage tests documented in
`evidence/storage-product-integration-20261104.md`, then use the signed fixture
in `../tests/files-desktop-signed-fixture.md` for actual UI and authorization.
Build Files/Text with pinned app-builder and CodeMirror dependencies. That test
catalog contains only Files/Text/CodeMirror and must never replace the full site
catalog. CAD host fixtures add JSketcher but still are not full catalogs.

`tests/files-desktop-signed-fixture.py` accepts `CODI_GATEWAY_ROOT`, `CODI_SDK`,
`CODI_APPS_BUNDLE`, `CODI_CADDY`, `CODI_DESKTOP_FIXTURE_PORT`; override machine-local
defaults. It requires gateway manifest SHA-256
`c0465afeb10dac4a761b274eb6871a8af750fccc5523a333da2c98dac8b90960`
and SDK SHA-256
`44da83bdccf43a2b36ae4b3f48eaf94fc1006b88180456e26faba61aae344869`.
These are candidate fixture inputs; beta's gateway is still `dd8cbea7…`.
Recover/rebuild and verify these inputs before testing; do not remove the pins
to make a fresh machine pass. Their complete clean-build retrieval remains
part of package 0 if the named artifacts are unavailable.

Representative tests, selected according to changed code:

- `tests/files-desktop-signed-workflow.test.mjs`
- `tests/files-two-profile-conflict.test.cjs`
- `tests/files-signout-worker-lifecycle.test.cjs`
- `tests/files-worker-budget.test.cjs` against a static checkout server;
  set `CODI_TEST_RENDERER_CRASH=1` for its renderer-crash variant.
- `tests/mirror-opfs-worker-budget-large.test.mjs` with the isolated R730
  fixture described in `../research/opfs-storage/WORKER-BUDGET-128-20261104.md`.
- `tests/files-real-linux-separation.test.mjs` with
  `CODI_TEST_REAL_LINUX=1`; the ordinary fixture deliberately blocks guest boot.

Do not reuse a running fixture after source or staging changes without checking
which bytes it serves. The lead-owned old fixtures on workstation ports 19976,
19885 and 19886 were stopped during handoff after checking their process
arguments and working directories. Recreate them for the source under test;
do not assume a port is still free or stop an unrelated process using it later.

## Beta release remains a separate serial gate

The last read-only observation found beta on guarded IndexedDB v1, SDK `44da`,
gateway `dd8`; the OPFS candidate is not live. Query-bearing bootstrap URLs
select different bytes from bare URLs. The readiness document contains exact
hashes and is the reference for the actual selected baseline.

Before any activation:

1. Recheck live pins, service identities, data roots, filesystem headroom and
   all-site/main/prototype health. The previous 5.3 GiB free space on root was
   only about 218 MiB above the gateway's 5 GiB reserve. `/srv/data` had much
   more space; that does not automatically give the account filesystem room.
2. Audit obsolete releases before any cleanup/move. Hardlinks invalidate naive
   sums of directory sizes. Preserve active/retained assets and account data.
3. Review the existing `3ad04c48…` beta-derived candidate and `853c12e5…` issuer, then complete the managed transition. Preserve a complete immutable
   module/worker graph and a full catalog preserving unrelated applications.
   The research integration tree is not a deployable whole-site replacement.
4. Qualify migration and recovery from the real guarded baseline, including old
   tabs, controlled service workers, pending writes, conflicts and interruption.
   Database v2 is a forward-only writer floor: v1 cannot read OPFS references.
   Recovery must retain a usable v2 client; deleting data is not recovery.
5. Supply and test a pinned managed transaction/recovery operator. The observed
   protected hosting reconciler is plan-only; its `apply`/`recover` refuse.
   Old guarded-v1 deployment journals do not prove v2 recovery.
6. Only the release owner applies the qualified beta change, then checks actual
   signed public behavior and served hashes, with main and `/desktop/` unchanged.

## Required result from every package

Return the exact base and commit, changed paths, capability/status changes,
commands and actual results, a preserved failing control where applicable,
test limitations, resource observations and remaining dependencies. Update the
operational queue and relevant matrix. Commit source, tests, recipes, needed
final runtime inputs under the existing repository policy, and notes; exclude
generated working builds, dependency directories, accounts and secrets.

Push the named branch to box-git and R730 and verify both remote refs. Mark
tested, integrated, packaged and deployed separately. Do not use passing test
counts as a percentage of CAD 1.0–6.0 or report a gate complete by weakening it.
When a package finishes, choose the next bounded dependency-ready item; keep
shared-file edits and deployment serial.

## Historical replay failure retained as a control

The original `089ed178` owner prototype followed a confirmed failure where an
impossible edit exposed only a partial solid. Its missing type declaration,
older normalization base and absent lifetime hook were real blockers at that
checkpoint. They are superseded by the integrated fixes and combined lead
results above; do not restart the old merge or quote that failure as current.
The full Gate 1 and release still remain open for the listed reasons.
