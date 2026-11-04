# Files beta installation readiness — 2026-11-04

**Review packet, not installation authorization or an activation receipt.** The Files-only beta candidate is not installed. No production state, credentials or account contents were copied or changed for this packet. This supersedes the stale capacity and missing-service-fixture statements in `FILES-RELEASE-HANDOFF-2026-11-04.md`; retain its source history and remaining controls. Do not deploy the full research desktop, change main, `/desktop/`, or the prototype.

## Pin set and public artifacts

Operator source reviewed here: `ba65151d2f2ab182e58220b5711bb6da6d64be64`; exact launcher SHA-256 `aa34f6c9e53f049d012a45da35989d1aab4797ef983d270ab498d01037fbfd82`. Lead integrated the previously reviewed operator subtree through `f6deb3251` into desktop `8dc0331bd`; later fixture commits must not be confused with a live installation. Recheck the chosen integration commit, all module pins embedded in the launcher, working-tree cleanliness and review status before assembling a bundle.

| Input | SHA-256 of its sealed manifest, or exact public asset |
| --- | --- |
| Public base | `0965a0cbdd022f588061cdc23e10eb6b18fa5977cc3f6a05569439eaf11d2020` |
| Files-only candidate | `3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc` |
| Old issuer | `1666491de4fe097285f02a5b6f7602fe57e4b9d3b2995bf016d4a9e809e36a51` |
| New issuer | `853c12e581c9f89fc3d78507f43941dd16cd0b4b894b28cdb8317e8a58340f21` |
| Existing gateway | `dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1` |
| Retained guarded overlays | `bc3c7e659d40f853ed31bfec257079d65cd92c86011b1b1b86e80f32dd7a9c1c`, `1d6b8f4e72e4c3f533afeea10589ac931a3dfe56d4bbaf03abec6d7d99a55d5a` |
| Currently selected loader | `0d1cbcb4e6b23beb0c6b7eecce8b35244438fb4341c2e325203c739c64118b81` |
| Currently selected mirror | `cbfafe53eae1afdac1f2a9af0bfdbd26cae59b1be8f5d96f6bebec2a56c158ed` |
| Candidate route table | `773dcdfa559d9ad5b5012bb4363248e8434e97dc33d2677bdd376d099c87fc1a` |
| Proposed guarded webctl | `84c09e08e64dadc02fe396b529f1a380ee2ab724eca877f108be0490c92caa6e` |

R730 public backups: `/mnt/data10tb/codi-beta-opfs-release-6db06c6c3/candidate-3ad04c48.tar.gz` (archive SHA-256 `93a5c701eec04c473779f6b981d87920c17958ed1d00c93c87a1924d88af7974`), `/mnt/data10tb/codi-beta-issuer-base-1666491d`, `/mnt/data10tb/codi-beta-issuer-opfs-853c-sealed`, and `/mnt/data10tb/codi-beta-client-44da-dd8cbea7`. Manifest hashes were rechecked for the latter three and the archive hash for 3ad. A matching manifest alone is **not** proof that every archived file is intact: unpack a disposable copy and run the complete inventory checks from `SIGNED-PROBE-NOTES.md` and the desktop-side `research/beta-opfs-release` packaging instructions. Do not mutate a shared archive. Do not use production state as fixture input.

## Observed installed state, read-only

On 2026-11-04 the beta issuer, frontend, gateway and Caddy were active; beta units were enabled and systemd reported no pending reload. Issuer uses sealed 166 on 28118 without the OPFS flag; its unit hash was `e6b8279c32a89f38ee4a3b2ba6c27777413c13b1b98611e78ff9b0d52dca1244`. Frontend unit hash `4b909882dfd879235e10bf3cbb004bd3e61db1786cfd99e122b7abbd39be5f78`; gateway unit hash `f7fe40291ed89df101e511673b201b5606ba526333b1f55743fdec8ed069b47e`. Gateway dd8 manifest matched its pin. Beta `/`, the selected loader and mirror, main `/`, and `/desktop/` returned HTTP 200. These are point-in-time observations, not current health guarantees.

Installed hosting controller `/home/dflanag3/webhost-sites/ops/webctl.py` hashes to `e012fb1d838e06c6a2e382c85d249fc10a3f8753f0b9f9abd3247230e7f40d0c`, **not** the proposed floor-aware controller. `common.py` was `d4f05bbb709e056354a5d2eb4d3a78741cbd044e4d100b965b91ec9a428a5ad0`, manifest `9bf8afdaab7d321940cc01b9275af81ba2b1ad558a3b966f24e05c6561a317b5`, generated Caddyfile `bf6b6d67c33640f10f0b023ded8d38e6352ab3d54e10b3f9ee01b225ed9d5031`. The intended `/srv/data/codi-beta-opfs/3ad04c48…/manifest.json`, `/srv/data/codi-beta-native/853c12e5…/connected-release.json`, `/var/lib/webhost-ops/opfs-floor.json`, `/var/lib/webhost-ops/opfs-transition.json`, and `/var/lib/webhost-ops/beta-files-probe/probe.json` were absent. Absence of one journal is not proof that all journals are absent; inspect all named journal paths under the hosting lock before any preparation.

Read-only preflight commands, with no private file contents emitted:

```sh
ssh box-webhost 'df -B1 /var/lib/codi-user-files/beta /srv/data /'
ssh box-webhost 'sha256sum /home/dflanag3/webhost-sites/ops/webctl.py /home/dflanag3/webhost-sites/ops/common.py /home/dflanag3/webhost-sites/sites.toml /etc/caddy/Caddyfile'
ssh box-webhost 'systemctl is-active codi-beta-issuer.service codi-beta-frontend.service codi-beta-gateway.service caddy.service'
ssh r730 'sha256sum /mnt/data10tb/codi-beta-opfs-release-6db06c6c3/candidate-3ad04c48.tar.gz /mnt/data10tb/codi-beta-issuer-base-1666491d/connected-release.json /mnt/data10tb/codi-beta-issuer-opfs-853c-sealed/connected-release.json /mnt/data10tb/codi-beta-client-44da-dd8cbea7/files-service.json'
```

Confirm manifest location against the host before relying on the example command; do not print private managed configuration or probe credentials. Revalidate all route, unit, file, timer, custody and lock pins immediately before a proposed operation; stop on drift.

## Capacity

The account volume and gateway private `/tmp` are on `/dev/sda2` (root); `/srv/data` is a separate `/dev/sdb1`. Observed free bytes: root/account `7,293,505,536`; separate volume `318,442,221,568`. The unchanged 5 GiB floor is `5,368,709,120`, leaving `1,924,796,416` bytes above it at observation. This is not a concurrency guarantee and separate-drive free bytes do not enlarge the account filesystem. Stage the public 3ad/853 trees on the intended separate volume only after reviewed custody checks. A prior 853 public-tree measurement was `120,774,656` allocated bytes; launcher, backups, logs and filesystem overhead are additional.

An isolated 128 MiB full create needs at least `268,435,456` bytes of gateway reservation above the floor; a retained 128 MiB file followed by a delta requires at least `402,653,184` bytes plus patch and overhead. These are lower bounds, not safe 100-user sizing or a guarantee against concurrent host writes. Measure full working set and enforce reserve immediately before test or activation. Do not silently reduce the floor.

## Protected installation and operation sequence — review required

There is **no qualified installed bundle or safe one-line installer yet**. The concrete next step is to assemble the reviewed pinned operator and its required `ops/beta_files_candidate.json` and `OPFS-ROUTE-TABLE.json` in a disposable root-owned tree, verify every embedded module pin and the complete artifact inventories, and review an atomic protected installation plus the guarded hosting-controller replacement under the existing lock. `/srv/data` itself was owned by `dflanag3`, whereas launcher `safe()` requires root-owned, non-group/other-writable ancestors: it is not suitable as the protected launcher bundle parent without changing custody. A reviewed root-owned path under `/srv/codi-connected` is a possible small bundle location, subject to exact ancestry/ACL verification and root-volume capacity; the public artifact preflight has its own explicit trusted-ancestor checks. Do not modify all hosting ownership or assume trusted-administrator bypass is prevented.

After that independent review, the intended order is:

1. Verify all current pinned source, complete artifacts, route snapshots, service units, managed timer state, account and probe custody, disk headroom, lock identity, and no unresolved journal; preserve both old guarded asset URLs. Install and verify the floor-aware guard for **every supported beta-changing legacy entrypoint**, with operative manifest and source read under the same hosting lock. Ensure unrelated-site operations remain possible while preserving beta. No generic freeze or direct edit of derived Caddy.
2. Stage 3ad and 853 immutable public artifacts at the exact pinned destinations, with full inventory and root-owned artifact checks. Install the reviewed root-protected launcher bundle and private dedicated probe using the existing managed authority. Verify the existing dd8 and 166 inventories and restore only originally active dependent beta units under their pinned unit files. Never copy user accounts or keys.
3. Under the existing hosting lock run the installed launcher `plan`, inspect the resulting baseline, then apply only the reviewed exact transition. The exact executable form, **not runnable until the protected bundle is actually installed and independently qualified**, is:

   ```sh
   sudo -n /srv/codi-connected/venvs/517179c/bin/python -I -B /ROOT_OWNED_REVIEWED_BUNDLE/ops/beta_files_launch.py plan
   sudo -n /srv/codi-connected/venvs/517179c/bin/python -I -B /ROOT_OWNED_REVIEWED_BUNDLE/ops/beta_files_launch.py apply
   sudo -n /srv/codi-connected/venvs/517179c/bin/python -I -B /ROOT_OWNED_REVIEWED_BUNDLE/ops/beta_files_launch.py recover
   ```

   Replace the placeholder only with the reviewed installed path. The plan must pass; it is not proof that apply is safe if pins subsequently drift. The same lock, controller, generator, custody and health checks apply to recovery.
4. The transaction establishes and verifies the exact maintenance gate, **durably writes the v2 floor before switching issuer/config**, installs the verified issuer transition, restores the recorded beta dependents, verifies complete candidate/native/gateway inventories and signed health, then exposes the reviewed candidate. Check actual generated Caddy, main response, beta service routing and selected asset hashes. Preserve journal and timer evidence.
5. After a floor exists, do not restore v1. On interruption use the protected `recover` entrypoint and its recorded snapshots. If candidate or forward services fail, attempt the exact managed gate, verify the gate independently, and recover forward only after all checks pass. If custody, routes, controller or gate verification is unknown, report **blocked; gate not verified**. A killed process cannot gate itself; a recovery actor is required. Never interpret a refusal as proof that access closed.

The probe is a dedicated disposable service account, provisioned only through a reviewed workflow, with private root-controlled `0700` parent and `0600` configuration under `/var/lib/webhost-ops/beta-files-probe`. No secret belongs in source, logs, public artifacts or real user accounts. The acceptance workflow must show signed write/read/cleanup and reconcile ambiguous writes via its private journal; routine recovery may use a narrower signed read of its pre-provisioned record. Do not blindly repeat uncertain registration or mutation.

## Evidence and remaining release gates

**Already demonstrated in isolated fixtures:** exact-launcher interruption and gate-only recovery with real loopback Caddy, actual distinct disposable systemd services running sealed 166/853 issuer, 166 frontend and dd8 gateway, signed synthetic account continuity, a real separately named timer, and process kills at unit-write, reload, restart and timer-stop. The parsed operator-written pinned unit drives the mapped fixture unit; old-unit/853-health and malformed-unit negative controls passed. Missing or partial forward assets, missing gateway, health failure and interrupted gate are covered separately. Independent review reran the unit-write case and gate-fault cases. See `SIGNED-PROBE-NOTES.md` for commands, source checkpoints and test limitations.

**Must pass before production installation or exposure:**

- Review and qualify actual protected bundle construction, atomic installation, trust/ACL ancestry and guarded-controller deployment; verify all supported old entrypoints cannot select v1 after floor while unrelated sites remain usable. No guard or package is presently installed.
- Run the actual production-equivalent generated routes and auxiliary render inventory with real TLS/Caddy and exact host inputs, not merely translated loopback Caddy. Preserve main and every non-beta generated byte, current asset authorization behavior and all old guarded URLs. Verify external main readiness and beta policy with production pins without copying private state.
- Qualify literal installed production beta unit paths and dependencies, original timer state and recovery, not only fixture name/path/policy mapping. Fixture timer stop/restore is real but its renewal job was not allowed to fire. Preserve main services.
- Provision and qualify the protected dedicated signed probe and real account/issuer continuity under operator custody. Fixture keys/accounts are synthetic. Validate lost-reply reconciliation and no credential disclosure.
- Independently verify exact installed-plan/apply/recover behavior and failure reporting, including known/unknown gate state, untrusted drift, interrupted writes, inadequate disk and forward-only post-floor recovery. Do not claim an unknown-state refusal closes the route.
- After the above and explicit release review, run bounded real-client Files acceptance, account separation/conflicts and interruption recovery, then the capacity-qualified 128 MiB changed-chunk test with independent hashes, wire bytes and resource observations. Existing fixture runs do not prove production 100-user capacity.

## Installer primitives: incomplete research checkpoint

`ops/files_install_candidate.py` and `ops/files_install_manifest.json` are an isolated first cut, **not an executable production installer**. The pinned manifest enumerates the launcher's exact embedded module pins, launcher, route table, candidate manifest and baseline site manifest. A root-owned disposable `/run` fixture exercises staging with `renameat2(RENAME_NOREPLACE)`, pin mismatch, existing generation refusal, symlink refusal, a prepared guard journal and forward completion, and floor refusal. Command from this branch: `sudo -n python3 -B research/beta-isolated-hosting/tests/files-install-candidate-test.py`. The first injected interruption raises in-process after journal persistence. A second test sends SIGKILL to a child immediately after the controller replacement and verifies journal-led forward completion. This is not power-loss durability or comprehensive crash-boundary evidence.

The primitives deliberately require a supplied already-held lock checker, and the guard primitive additionally requires the caller to verify hosting target ancestry/custody with the existing `beta_files_preflight.protected_ancestors`. There is no fixed-path protected launcher, source bootstrap, reviewed target-owner pin, exact ACL/group check for the live target, backup or safe rollback command. No automatic cleanup of abandoned staging directories is implemented. The code has not received independent security review. Do not run it against the host, install the guard, or treat the fixture as release qualification. Before a candidate installer can be reviewed for use, bind the existing `HostLock` and exact protected production paths in a root-custodied entrypoint; validate all input and target metadata/ACLs and journal transitions; test real SIGKILL at staging, journal, replacement and synchronization boundaries; verify concurrent legacy entrypoints and floor behavior; independently review and test no-overwrite and no unintended changes. Preserve the existing unmodified launcher/operator pins and do not provision the probe as part of this helper.

## Fixed-path installer candidate — independent review required

This branch now adds `ops/files_install_launch.py`, an explicit `plan|install|recover` candidate for the existing hosting flock, together with `ops/files_install_candidate.py` and the exact `ops/files_install_manifest.json`. Source SHA-256 pins: launcher `f31853a6e385eafc7b66e99cd3ee4654a37cc521dc9e14f163013d79e210cc79`; helper `4c09350ea824e09a5596f70bdda1303b30242a2f6ccac5238314e1fcc107dd51`; manifest `ce18b7794adc247218cd99a85b44c0df27e224690a9709cdf9bd6a9d4da7f322`. The launcher checks its root-owned ancestors and extended ACLs, pins the helper and existing launcher/preflight modules, and uses the existing `HostLock` and locked metadata rechecks. It requires the observed controller owner/group `1000:1000`, mode `0644`, one link and no extended ACL; the lock must be `0:0`, mode `0644`, one link and no extended ACL. It uses `protected_ancestors` for hosting custody rather than changing ownership, checks for every listed existing Files transaction/floor before writes, verifies an exact manifest, refuses unknown controller hashes and never overwrites an existing bundle. A durable root-private journal drives forward completion of a guard replacement and is removed only after verification. It does not touch routes, services, probe accounts or public artifacts. Existing Files launcher/operator pins are unchanged.

The production paths are fixed in source: root-owned reviewed input `/srv/codi-connected/operators/files-install-input-ce18b7794adc2472`; bundle `/srv/codi-connected/operators/files-bundle-ce18b7794adc2472`; controller `/home/dflanag3/webhost-sites/ops/webctl.py`; hosting lock `/home/dflanag3/webhost-sites/.controller.lock`; private journal `/var/lib/webhost-ops/files-install-guard.json`. The input tree is a separately provisioned prerequisite, including the candidate guard, old controller source and reviewed installer sources; **a protected input-tree bootstrap/install procedure is not yet qualified**. Until independent review and trusted bootstrap, the following are the exact **proposed, not authorized or ready to run** invocations:

```sh
sudo -n /srv/codi-connected/venvs/517179c/bin/python -I -B /srv/codi-connected/operators/files-install-input-ce18b7794adc2472/ops/files_install_launch.py plan
sudo -n /srv/codi-connected/venvs/517179c/bin/python -I -B /srv/codi-connected/operators/files-install-input-ce18b7794adc2472/ops/files_install_launch.py install
sudo -n /srv/codi-connected/venvs/517179c/bin/python -I -B /srv/codi-connected/operators/files-install-input-ce18b7794adc2472/ops/files_install_launch.py recover
```

Disposable tests from this source tree:

```sh
sudo -n python3 -B research/beta-isolated-hosting/tests/files-install-candidate-test.py
sudo -n python3 -B research/beta-isolated-hosting/tests/files-install-launch-test.py
```

Both passed. They verify the pinned bundle, no-replace behavior, bad input, symlink, published bundle integrity, target ownership/mode, extended ACL, root-lock mode/contention, journal completion and floor refusal. The primitive fixture uses real SIGKILL during an unpublished copy, immediately after bundle rename/fsync, immediately after journal fsync and after controller replacement/fsync; it then verifies the corresponding safe state and recovery. The executable fixture runs the actual launcher logic with explicitly substituted disposable paths/hostname and a test-only injected helper fault/pin for one kill, restoring the original pinned helper before recovery. These do not demonstrate power-loss durability, literal live paths or production activation.

**Material gate still open:** replacing webctl while holding its flock does not fence a legacy Python process that loaded the old file before the replacement but attempts the nonblocking flock only afterward. Such an already-running old process could operate after installation and potentially after the v2 floor. The candidate does not resolve that scheduling race; a reviewed quiescence/fencing mechanism for all supported legacy invocations must be established before a floor is written. A deliberately privileged administrator bypass is outside the guarantee. Independent review must also audit bootstrap custody, crash points, inode races, concurrent legacy processes, old/new journal handling, ACL coverage, full manifest and no-overwrite semantics, and actual protected host lock/paths. No claim is made that this candidate is approved for installation.
