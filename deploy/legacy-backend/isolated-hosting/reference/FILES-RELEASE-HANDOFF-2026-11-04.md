# Files beta operator handoff — 2026-11-04

Status: **research candidate, not release-ready and not installed**. The public beta remains on the guarded v1 mirror and dd8 gateway. The next release is a beta-only OPFS v2 graph, not a promotion of the research desktop tree or a change to `/desktop/` or main. Source head reviewed here is `ce4fd36abef3b8fd91a020aa215d8989d2be9b74`; this handoff is a later documentation-only commit. No live changes were made for this handoff. Treat older “not implemented” wording in `SIGNED-PROBE-NOTES.md` as historical where later sections describe the candidate launcher and its fixture.

## Exact integration candidate and history

The independently observed desktop integration head was `c6fbe38c3a58246e72fd0a9d8bc273bd820369af` (it may have moved since). Its common ancestor with this operator branch is `1b9b8c445789570c685bc9dfaeccf702e057ade9`; it does not contain `research/beta-isolated-hosting`. The exact final operator subtree is tree object `1d77c94f7efbb8945b5162c5f285ebbb3d7b0d95` at `ce4fd36ab`. The safest **review-only source integration** is to fetch that commit and restore only `research/beta-isolated-hosting` from it into an isolated integration worktree, inspect and test the resulting staged tree, then commit it. This avoids importing unrelated desktop and hosting history. It does not install any operator or change hosting. Before using this approach check that the destination has no independent work at this path; recheck the observed head and status.

If individual cherry-picks are specifically required, the exact chronological list of commits touching this subtree since the common ancestor follows. Apply only after inspecting each commit's full diff and dependencies: some touch paths outside this subtree, and `b101cd8b8`'s broad freeze is an intermediate state corrected by `d9fc0707f`, not a release state. Do not stop between dependent commits, do not assume every whole-commit pick applies cleanly to desktop, and do not install an intermediate result. The first 40 provide the hosting/transaction baseline through `c2d6f6962`; the remaining 30 add the Files candidate through `ce4fd36ab`.

```text
591b46995 Prototype isolated beta hostname routing
5a862d33e Exercise beta hostname with isolated TLS
9283d89e9 Keep beta guest network unavailable by default
c2163639d Record beta public desktop asset verification
961ef35d1 Exercise beta routes against isolated signed services
132e48adb Allow beta offline worker root scope
b0f394d2d Document beta managed rollout prerequisites
d03f20382 Document bounded beta maintenance timing and race
611482067 Exercise bounded beta maintenance transaction model
4bc892945 Exercise beta timer drift recovery refusal
5d057f86b Add managed beta transaction core
116932a9d Recover beta generated files after interrupted Caddy apply
d169cba78 Check renewal process is quiescent
56ac4254d Reestablish beta recovery maintenance window
d86c3066f Refuse timer drift before beta recovery
d6b374fd0 Verify main site health after beta recovery
0fa38aca8 Guard beta Caddy side effects and main health
48889c092 Record beta transaction review gaps
467d89985 Check beta generated render targets
136050552 Add pinned beta hosting launcher candidate
549ed59b1 Require durable backup before beta change
93f90c456 Bind beta launcher to isolated service preflight
d2b813e07 Bind recovery journal to pinned beta snapshots
c88bd5a8b Accept pinned native license filenames in beta preflight
8ce4f843a Record beta hosting activation and certificate recovery
49d83e3b9 Document main storage promotion safety gates
9f2ea9046 Update beta hosting preflight for incremental worker
e77a63bf4 Validate beta worker manifest shape
32f753c5a Rebase read-only beta hosting checks to active release
80673a64f Verify already active beta hosting inventory
8213ec5a4 Record refreshed beta hosting plan
4ff2dd7a3 Refresh read-only checks for current beta lifecycle release
f1ed9a9d1 Reject special files in refreshed beta audit
e4a6c2ec6 Bind v2 floor to existing managed host transactions
93d535de8 Capture malformed nested journal gating failure
ef08fe95b Gate known candidate on poisoned managed journal
de92b2005 Guard supported beta recovery against v2 floor
dc1b356bc Recover gate-only hosting journal forward to gate
817a9e88f Qualify gate recovery through copied hosting controller
c2d6f6962 Qualify pre-floor beta maintenance normalization
aa5ecd9ba Add pinned beta-only Files candidate routes
4f5ca242a Constrain beta Files routes to sealed manifest
f493d4c99 Stage forward-only beta issuer unit switch
bd80ad2b5 Test beta issuer recovery with disposable systemd units
2b75978f8 Restrict beta Files gate transitions in both directions
b101cd8b8 Stage locked legacy hosting floor freeze
a0f999980 Stage locked read-only beta Files preflight
a2ba96554 Retain issuer recovery record through outer route commit
ef1ec5dd6 Assemble Files floor and issuer recovery sequence
d9fc0707f Preserve unrelated hosting work under beta v2 floor
f0d78a31b Exercise assembled recovery against local Caddy
89ed54ed7 Pin normalization journal before assembled recovery
d8cb802de Record observed issuer public staging footprint
80491ca74 Keep baseline controller fixture pinned after route changes
d4d44c398 Exercise pinned gate and Files routes through controller
28b2abe73 Bind Files transition snapshots to exact release inputs
12c4271aa Use gate-only recovery for ordinary post-floor gating
bc91f1bfe Recover committed Files route transaction to gate
ee1b47f86 Bind exact Files snapshots to managed transaction router
bf0606af3 Exercise assembled Files recovery through managed Caddy
19403bf04 Prototype protected signed Files health probe
dde852a51 Exercise lock-bound signed health in floor recovery
76cbb2016 Add pinned host Files signed health binding
d147a1ee7 Draft protected Files transaction entrypoint
4cf818f73 Add protected launcher custody refusal controls
927684d6d Require signed baseline probe before Files transition
cae6c329a Guard normalization before any managed host writes
024b6d9ad Exercise protected Files launcher in isolated namespace
6fdc8d5a0 Make Files launcher namespace qualification reproducible
ce4fd36ab Qualify Files launcher with loopback Caddy and systemd
```

Important inputs: public candidate manifest `3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc`; issuer old `1666491de4fe097285f02a5b6f7602fe57e4b9d3b2995bf016d4a9e809e36a51` and new `853c12e581c9f89fc3d78507f43941dd16cd0b4b894b28cdb8317e8a58340f21`; gateway `dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1`; guarded v1 overlays `bc3c7e659d40f853ed31bfec257079d65cd92c86011b1b1b86e80f32dd7a9c1c` and `1d6b8f4e72e4c3f533afeea10589ac931a3dfe56d4bbaf03abec6d7d99a55d5a`. `research/beta-opfs-release` is a separate desktop-side packaging dependency; do not replace it with this subtree. Exact public artifact retrieval and full-inventory verification are in its README and `SIGNED-PROBE-NOTES.md`.

## Remaining gates and smallest useful next checks

The existing combined namespace runner with `--real-caddy --real-systemd` has exercised the exact entrypoint, durable floor, private temporary account directories, pinned public/native/gateway files, real signed fixture account, translated loopback Caddy and disposable named systemd stand-ins. It has not qualified all real host boundaries together. Run its documented command in `SIGNED-PROBE-NOTES.md` first to reproduce that baseline. Then resolve these distinct gates:

1. **Guard every supported old beta-changing entrypoint.** The observed live `/home/dflanag3/webhost-sites/ops/webctl.py` is `e012fb1d…`, not the proposed guarded `84c09e08…`. No guard installation is authorized by this handoff. The shortest proof is a disposable copied-host test invoking each supported old `apply`, `recover`, rollback, render and site-maintenance entrypoint while a v2 floor or interrupted journal exists: each must refuse selecting v1, while a normal unrelated-site change preserves exact beta v2 bytes. Include pre-lock manifest races and stale actors. Then independently review protected installation and verify the live installed pins before any floor is written. Deliberate root/administrator bypass is outside the guarantee.
2. **Actual beta units and timer.** The combined runner's systemd units are uniquely named sleep stand-ins, not the beta issuer/frontend/gateway; unit names and `FragmentPath` are mapped, and the timer is simulated. The next isolated check should run three uniquely named real service units with the sealed 166/853 and dd8 processes, distinct synthetic UIDs/state and the real `Requires`/`After` relation, plus an independently named disposable timer using `SystemdTimer`. Kill during unit write, daemon reload, issuer restart and dependent restoration; verify the recorded initially active/inactive state, private state continuity, timer restoration and recovery. Do not operate the production timer or unit names. This requires a test adapter for unique names; its mapping is a limitation, not production-unit proof.
3. **Actual Caddy/TLS and unmodified generated outputs.** The combined test validates/reloads a translated loopback config; it does not run the unmodified production file or production TLS. In an isolated root/mount/network namespace, run Caddy adapt/validate on the exact gate and candidate generated files and pinned auxiliary inventory, with disposable supporting imports and certificate material. Then run a disposable trusted-HTTPS virtual host with the exact 84 method/path/query mappings, old immutable guarded URLs, API/config/gateway and gate-denial controls, and verify non-beta rendered bytes remain identical. Production keys and hand-edited derived Caddy files must not be used. Existing `tests/opfs-route-controller-test.py`, `tests/opfs-generated-caddy-test.py` and the combined runner provide separate controls, not one unmodified production-ingress proof.
4. **Signed health provisioning and account continuity.** The exact launcher fixture substitutes beta's production policy/origin with a newly generated fixture issuer, and main readiness. It has real signed registration/read/create/delete and real old→new issuer processes, but no protected live probe account is installed. Use `tests/beta-signed-native-fixture.py` plus `tests/beta-signed-probe-test.py` with the exact public artifacts to reproduce continuity, then add kill/lost-reply tests around registration, creation and configuration publication: preserve the private 0700/0600 journal and reconcile explicitly, never blind-retry a mutation. Provision only a dedicated approved probe under the reviewed host lock after the operator and custody have been reviewed; keep credentials out of source, logs and public artifacts. Actual main config hashes and main unit states were separately checked read-only and matched on 2026-11-04; recheck at execution time without copying private state.
5. **Post-floor gate/recovery under broken prerequisites.** Source inspection: `beta_files_launch.artifacts()` requires full candidate and new-native inventories and main readiness, and is passed into `GateRescue`; the transition adapter also invokes beta readiness. Consequently loss of a forward artifact or a service may block an attempt to gate an already exposed candidate. Refusal alone does not prove the candidate is inaccessible. Add a disposable exact-launcher test with a durable v2 floor and active candidate, then make the new native/candidate unavailable or corrupt and independently fail signed/service health: verify whether exact-gate recovery succeeds or reports blocked with gate state truthful. Implement and review any narrow gate-first correction with exact trusted snapshots and existing lock/controller; do not relax custody, rewrite derived Caddy or restore v1. Separately test a pending pre-floor normalization journal with missing forward artifacts; current normalization recovery also requires `artifacts()`.
6. **Disk-full, interruption and 128 MiB real-client acceptance.** The runner's fault kills at issuer-unit write. Extend the exact protected fixture across normalization, gate, floor, issuer restart, candidate exposure and committed cleanup, including low space and simultaneous sessions; verify signed account isolation, old committed content, conflicts and recovery. Only after the explicit capacity gate below is met, run a signed 128 MiB initial create/read, one-byte edit and interrupted transfer with independent hashes, file/account isolation, changed-wire byte counts, memory and UI responsiveness. Avoid live beta for this large test until the launcher, reserve, custody and activation path are reviewed.
7. **Protected installation and review.** Build a root-protected immutable launcher bundle containing exact pinned source and route table; verify its manifest, Python environment, ancestry/ACLs, host lock inode, baseline snapshots, old/new complete inventories, probe-secret custody, paths and occupied ports under the existing hosting authority. Exercise the actual plan/apply/recover executable with production-equivalent units and certified operator rollback/forward recovery in disposable infrastructure. Review all supported service/controller entrypoints and unrelated-site behavior. The current source's `plan` is not an installed operator. Re-run the read-only plan after staging and guard preparation; an absent candidate/guard is a block, not a reason to loosen pins.

## Capacity and staging, measured read-only

On 2026-11-04, `/var/lib/codi-user-files/beta` and `/tmp` are on `/dev/sda2` (`/`, ext4); the gateway has `PrivateTmp=yes`, and a read-only `nsenter` stat of the actual gateway process reported the same device ID `2050` for its `/tmp` and beta account root. `/srv/data` is separate `/dev/sdb1` (ext4). Available bytes observed: account/root `5,580,742,656`; `/srv/data` `320,140,726,272`. With the required **5,368,709,120-byte (5 GiB)** floor, root has only **212,033,536 bytes above reserve** at that instant. Do not equate `/srv/data` free space with account capacity.

The measured 853 public stage uses `120,774,656` allocated bytes on the measured ext4 filesystem; the intended 853 and 3ad destinations are under `/srv/data`, so if staged directly there this component does not consume the account/root reserve. This is not the full staging footprint: protected launcher installation, backups, logs, temporary files, filesystem differences and concurrent work remain unmeasured. If the same 853 stage were instead placed on root, only `91,258,880` bytes would remain above reserve, before any 128 MiB test.

The deployed dd8 gateway's binary full create reserves `received_size + size`, so a fresh 128 MiB create requires **268,435,456 bytes above the floor** before accounting for other reservations. The observed margin is **56,401,920 bytes short** even when public stages are on `/srv/data`. A create followed by a small delta against that retained 128 MiB file needs, at a minimum, the retained `134,217,728` bytes plus a delta reservation of `2 × 134,217,728` bytes plus the patch: **402,653,184 bytes plus patch/overhead**, about **190,619,648 bytes short** from the observed starting margin. These are arithmetic lower bounds for one isolated test, not safe sizing for concurrency, existing snapshot reservations, metadata, logs, or 100 users. The cache's same-process reservation is not a global filesystem quota. Measure the full worst-case workflow and provide additional headroom above the unchanged 5 GiB floor; do not run the large test at the observed free space.

Read-only checks on 2026-11-04 found the exact 3ad and 853 manifest paths under `/srv/data` absent, and the guarded webctl not installed. The dd8 gateway manifest matched its pin. `/var/cache/apt/archives` was `90,705,920` bytes and `/var/cache/man` `2,195,456` bytes; these are regenerable cache candidates, but no deletion is authorized by this handoff and reclaiming them alone would not establish a safe large-test budget. Named `/tmp` review/build directories total about 3.50 GB, but ownership and current use have not been verified; do not remove them on this evidence. Recheck free space, mounts, processes, and exact installed hashes immediately before any reviewed action.
