# Files-only beta staging and main-renew inspection — 2026-11-04

**Historical pre-install runbook:** the lead subsequently completed protected
installation, probe provisioning, staging and actual beta activation. Current
state and exact pins are in `../../evidence/files-beta-activation-20261104.json`
and `../../docs/HANDOFF-FILES-CAD-2026-11-04.md`. The floor now exists; do not
repeat pre-floor install/provision/plan/apply steps. The main-renew investigation
below remains separate and was not deployed.

This is a runbook for the existing reviewed candidates, not an activation receipt. Source basis: desktop integration `1dc60b460a4804e946a5e2abee66d24ccc746bf0`. It does not promote that desktop tree. Keep main, `/desktop/`, beta account data, keys and current dd8 gateway separate from public artifact staging. No live change was made for this document.

## Before staging

Recheck current pins and protected custody using the existing `FILES-INSTALL-READINESS-2026-11-04.md` and `FILES-BOOTSTRAP-REVIEW-2026-11-04.md`; follow the supported-CLI quiescence procedure in the latter. The host currently has legacy webctl `e012fb1d…`, not guarded candidate `84c09e08…`; the fixed-path installer and its bootstrap remain candidates requiring their protected placement and independent qualification. No v2 floor may be written until supported old CLI invocations are quiescent and the floor-aware path is verified. The two historical Codi one-off scripts and production-disallowed acceptance script are unsupported administrator bypasses, not commands to run.

Read-only health/capacity commands:

```sh
ssh box-webhost 'df -B1 /var/lib/codi-user-files/beta /srv/data /'
ssh box-webhost 'systemctl is-active codi-beta-issuer.service codi-beta-frontend.service codi-beta-gateway.service caddy.service'
ssh box-webhost 'for u in https://ksu.codes/ https://ksu.codes/desktop/ https://beta.ksu.codes/ https://beta.ksu.codes/config.json; do curl --noproxy "*" -sS -o /dev/null -w "%{http_code} %{url_effective}\n" --max-time 10 "$u"; done'
ssh box-webhost 'sudo -n sha256sum /etc/codi-user-files/beta/issuer-policy.json /srv/codi-gateway/releases/dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1/files-service.json'
```

On 2026-11-04, these returned four active services, four HTTP 200s, beta policy `71a7f2d380051ecde367bfc2517a77e2570d3797621e3e8f1cb4a141f8cd6dca` and dd8 manifest `dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1`. These checks do **not** prove signed login. Root/account filesystem free was `7,295,614,976` bytes; separate `/srv/data` free was `318,442,221,568` bytes. The mandatory account reserve remains `5,368,709,120` bytes. R730 853 tree was `120,095,131` apparent / `121,819,136` allocated bytes there; compressed 3ad archive was `1,706,175` bytes and contained 88 regular files totaling `7,874,932` apparent bytes. Destination allocation differs by filesystem. Add scratch, tree metadata, staging copies, logs, backups, probe and concurrent reservations; measure immediately before use. The 3ad and 853 destinations are on `/srv/data`, but its free space does not add to account capacity. One fresh 128 MiB create alone requires at least `268,435,456` bytes above the account floor; follow-up delta and concurrency need more. Never change the floor.

The parent directories `/srv/data/codi-beta-opfs`, `/srv/data/codi-beta-native`, `/srv/codi-connected/operators` and private probe directory were absent in this read-only snapshot. Create only reviewed paths with the ownership/ACL rules expected by the existing verifier and launcher; never use an existing different generation as scratch. Input-tree bootstrap and guard installation use the exact protected source and procedures already documented; do not run a checkout script as root.

## Recover and verify the public artifacts

Use a clean working directory on a volume with sufficient space, and the pinned checkout. These commands copy only public artifacts and are suitable for an isolated preparation machine; do not include private runtime, accounts, keys, credentials or probe files.

```sh
mkdir -m 700 /tmp/codi-files-prep-3ad
scp r730:/mnt/data10tb/codi-beta-opfs-release-6db06c6c3/candidate-3ad04c48.tar.gz /tmp/codi-files-prep-3ad/
printf '%s  %s\n' 93a5c701eec04c473779f6b981d87920c17958ed1d00c93c87a1924d88af7974 /tmp/codi-files-prep-3ad/candidate-3ad04c48.tar.gz | sha256sum -c -
tar -xzf /tmp/codi-files-prep-3ad/candidate-3ad04c48.tar.gz -C /tmp/codi-files-prep-3ad
python3 -B research/beta-opfs-release/verify.py /tmp/codi-files-prep-3ad/codi-beta-opfs-transition-candidate 3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc
scp -r r730:/mnt/data10tb/codi-beta-issuer-base-1666491d /tmp/codi-files-prep-3ad/base166
PYTHONDONTWRITEBYTECODE=1 python3 -B research/beta-opfs-release/build-issuer.py /tmp/codi-files-prep-3ad/base166 /tmp/codi-files-prep-3ad/derived853
sha256sum /tmp/codi-files-prep-3ad/derived853/connected-release.json
```

The build verifies all input 166 inventory bytes and creates a new derived tree. Require the printed derived manifest `853c12e581c9f89fc3d78507f43941dd16cd0b4b894b28cdb8317e8a58340f21`, then use the existing `beta_files_preflight.tree` or equivalent full 853 manifest/inventory verifier on the derived tree and again after transfer. The R730 prebuilt sealed `/mnt/data10tb/codi-beta-issuer-opfs-853c-sealed` is also available; compare all files to its manifest, not just that manifest's hash. Do not use `/mnt/data10tb/codi-beta-opfs-release-6db06c6c3/public-candidate-fixture.tar.gz` as the candidate: it contains superseded `feaa` code.

For host staging, transfer the verified public trees to new private temporary directories **on `/srv/data`**, preserve no private state, verify every file and symlink/ACL/owner rule, fsync complete files and directories, and publish by a no-replace rename into exactly:

```text
/srv/data/codi-beta-opfs/3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc
/srv/data/codi-beta-native/853c12e581c9f89fc3d78507f43941dd16cd0b4b894b28cdb8317e8a58340f21
```

Never replace or remove an existing generation; verify it and stop on drift. The existing `beta_files_preflight.tree(root, manifest, pin)` performs full expected-file/hash and custody checks and is also bound in the protected Files launcher. It requires root-owned artifact entries and trusted protected ancestors, including ACL checks; `/srv/data` itself is administrator-owned, so use that verifier's actual trusted-ancestor contract rather than assuming the launcher's stricter root-only bundle ancestry applies to the artifact tree. The repository does not currently provide a separately qualified CLI for durable no-replace host artifact publication: use the existing managed protected staging procedure when established, not an ad hoc overwrite or a new deployment authority. Incomplete scratch does not become an active release. Run Python with `-B`; reverify complete inventories after any process execution.

## Probe and existing transition

The exact private probe path is `/var/lib/webhost-ops/beta-files-probe/probe.json`, with root-owned `0700` directory and root-owned `0600`, single-link config. `ops/beta_files_host_health.py` binds it to policy `/etc/codi-user-files/beta/issuer-policy.json` at `71a7f2d3…`, beta origin, issuer port 28118 and gateway port 28140; it checks service/unit pins, account subject, signed identity and known file digest. `ops/beta_signed_probe.py:provision_private(root, origin=..., issuer_port=..., gateway_port=..., policy=..., jose=...)` registers a dedicated new account, journals **before** registration/create, makes a known file, verifies it, writes private probe config, then clears the provisioning journal. It never requires real user credentials. A full acceptance uses `Probe.acceptance` for journaled create/read/delete; ordinary forward/recovery health reads the known record. An uncertain response retains a journal for explicit reconciliation, never blind retry.

**There is currently no qualified protected host CLI that invokes `provision_private`**. The isolated test `tests/beta-signed-probe-test.py` calls it directly with disposable issuer/gateway state; do not copy that fixture's credentials or improvise a root interactive invocation on production. The concrete remaining binding must load the pinned protected JOSE/policy and probe modules, hold/check the same hosting lock and private custody, register only the dedicated beta probe, suppress credentials from logs, and handle both `probe-provision.json` and `signed-probe-acceptance.json`. The launcher currently consumes but does not provision `probe.json`; until the binding and account exist, its signed health preflight correctly fails.

After protected bootstrap, supported-path quiescence/guard qualification, complete staged inventories and protected probe provisioning, use the existing fixed-path `beta_files_launch.py plan|apply|recover` documented in `FILES-INSTALL-READINESS-2026-11-04.md`; do not write Caddy output directly or replace unrelated site files. Its sequence is exact verified gate → durable forward-only v2 floor → issuer 166→853 and originally active dependent beta units → full artifacts and signed health → candidate exposure. `recover` follows the same authority; after the floor it must never restore v1. A failed verification of gate closure is reported as **unverified**, not closed. Recheck old retained immutable URLs, beta configuration, main and `/desktop/` after any change. An uncatchable death requires a recovery actor. The actual production-bound launcher, TLS paths, probe and host transition have not yet been qualified together.

## Main renewal: possible non-mutating inspection, not yet qualified

The main root-renew unit's recorded 0651…/0aaf… pins do not match current config `6d72467c…` and sealed issuer `1666491d…`; its last observed hourly attempt failed. See `MAIN-RENEW-PIN-REPAIR-2026-11-04.md` when available on the separate source branch. The existing `run.py inspect` is **not strictly read-only**: managed locks use `O_CREAT`, and `RootAuthority.connection()` opens authority SQLite with `mode=rw`. Do not run it under a no-write requirement or blindly substitute unit pins.

The real code's compatibility checks include pinned config/release and clean managed journals; root authority database schema version and signed authority binding; issuer authority-key and discovery-policy match; staged/live service-key and grant match; independent recovery fence and publisher-ledger binding; account-policy schema and missing-account-policy check; and a stable steward state. Root and scoped keys and database contents must not be printed, exported, or copied. At the observation time authority SQLite existed; its `-wal`, `-shm`, `-journal` and live renewal journal were absent. This observation may immediately become stale and does not prove consistency.

A possible bounded investigation is a separately reviewed inspector that acquires existing locks **without creation**, opens the actual database through a read-only mount namespace and SQLite `mode=ro` with `PRAGMA query_only=ON`, and reports only schema/version and boolean checks. It must refuse missing locks, journals, WAL/SHM conditions or SQLite operations needing writes, and must not use `immutable=1` to silently ignore a live WAL. Verify no persistent filesystem writes in a disposable fixture first. Schema-only success is not the full cryptographic, ledger, fence, key-custody or recovery-operator compatibility check and cannot justify repinning by itself. Existing operator `inspect` could be considered only under separately established controlled semantics; this document does not authorize a state mutation or claim it is harmless.
