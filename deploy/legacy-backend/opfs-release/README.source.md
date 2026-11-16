# Beta-derived Files/OPFS candidate — isolated, not deployable

This directory builds a reproducible public-asset candidate from the exact observed beta guarded-v1 baseline and source checkpoint `6db06c6c3`. It is **not** a hosting operator, a live release, or an instruction to deploy. The existing beta plan-only reconciler still refuses apply/recover. No private state is an input.

## Reproduce

Prerequisites: Python 3; Node 24.22.1; the checked-in app-builder dependency lock and reviewed Chonky/CodeMirror dependencies; an isolated Chromium and Caddy for browser testing; Python aiohttp, argon2 and cryptography for the fixture. The actual beta gateway package is backed up at `r730:/mnt/data10tb/codi-beta-client-44da-dd8cbea7`: `files-service.json` SHA-256 `dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1`, SDK `gateway_service/client.mjs` SHA-256 `44da83bdccf43a2b36ae4b3f48eaf94fc1006b88180456e26faba61aae344869`. Fetch public/test artifacts to a disposable directory; do not copy the server's real issuer database, keys or user files.

```
python3 research/beta-opfs-release/prepare-baseline.py /tmp/opfs-public-baseline
python3 active-system/scripts/build-public-apps.py --apps files --node /path/to/node --output /tmp/opfs-files-bundle
python3 research/beta-opfs-release/build.py --baseline /tmp/opfs-public-baseline/candidate-inputs --files-bundle /tmp/opfs-files-bundle --out /tmp/opfs-candidate
python3 research/beta-opfs-release/verify.py /tmp/opfs-candidate 3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc
python3 research/beta-opfs-release/packaging-test.py /tmp/opfs-public-baseline/candidate-inputs /tmp/opfs-files-bundle
python3 research/beta-opfs-release/recovery-model-test.py
```

`prepare-baseline.py` fetches only public files required by the isolated desktop test and verifies the cache manifest and each selected file. It stops if the observed beta pins change; it must not silently accept new live bytes. Its root keeps the unmodified bare loader for the old worker; `candidate-inputs/desktop-apps.js` contains the distinct selected `?simplified=1` guarded loader. It is a reduced baseline, not a complete backup of the site. A public-only archive containing the verified test baseline, Files bundle and candidate is on R730 at `/mnt/data10tb/codi-beta-opfs-release-6db06c6c3/public-candidate-fixture.tar.gz`, SHA-256 `1565e26712dda66c638852c9e464cca36b52820e44e9014179f31a27f7139282`; the dd8 gateway is the separate pinned artifact above.

## Candidate boundaries

The candidate manifest is `3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc`. It seals 87 regular files, including a whole content-addressed storage graph under `storage/browser/releases/0ea94092ebb6cd6120433c49cd4fe1284842e334b6313dc9945ed3d6cf87011a/`; relative imports and worker code stay within that immutable graph. `verify.py` rejects altered files, extras, symlinks and hardlinked candidate files. The builder verifies selected beta inputs, every storage/host source pin, and the complete pinned Files bundle inventory. It emits `patches/app.diff` and `patches/desktop-apps.diff` against beta, rather than replacing beta with the unrelated integrated desktop tree. The diff carries the tested session-lifecycle/teardown pieces because beta's older sign-out otherwise has no equivalent protection. These changes still require independent review against every beta app lifecycle.

The beta catalog keeps all non-Files entries structurally identical and substitutes Files bundle `12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244`; existing beta Text and CodeMirror entries are retained. The derived cache manifest has ID `66b864076c7f618b8c1f1f52128247498f82e84834924f41c6d7838f00c35485`; old app asset records remain. The output `config/fileStorage.json` is only a desired OPFS configuration fragment, **not** a deployable issuer configuration or an approved way to modify the real beta issuer.

| Candidate output | SHA-256 |
|---|---|
| `shell/app.js` | `df957ec69e3930a741a1680c637c88e98a74bdaaa0dcd4abfc64f5ff264dc932` |
| `shell/desktop-apps.js` | `38f02da4e7df4430361296175225044b8a2f3b579ce0ef33a8acd7e56868ff84` |
| `assets/desktop/apps.json` | `2b835e478b1a5e24015b7a353b32838e6026d7fe6f56bad71660f6f7ce83f07a` |
| `assets/desktop/cache-manifest.json` | `3c5d5a241231cb83eb62f71c7cb4ae632f3fa916b1892035cd68ee83a1a748d2` |
| `assets/desktop/offline-worker.js` | `d2c23435beac5ae0c354ee16eba9d708a975855e3538a4e36717b2900c9e2519` |
| `patches/app.diff` | `48baaeac1d73c7d19327aa0f90cf15b038d459481e59a310f5d3c50a09783138` |
| `patches/desktop-apps.diff` | `8d9b13a681283df0daa0a451167dab8a41826b04bd5ea8cfd96c859a66a721d5` |
| `config/fileStorage.json` | `5d24041f30f0a368d77cb0fe14606bde11568200a9e4f2c6a9b6c893cc292b5c` |

## Isolated controlled-tab test

Run the following only with disposable local state, never a live hostname:

```
CODI_GATEWAY_ROOT=/path/to/pinned-dd8 \
CODI_BASELINE=/tmp/opfs-public-baseline \
CODI_CANDIDATE=/tmp/opfs-candidate \
CODI_CANDIDATE_HASH=3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc \
CODI_CADDY=/path/to/caddy python3 research/beta-opfs-release/controlled-fixture.py
# Start isolated Chromium CDP on 127.0.0.1:19298, with puppeteer-core available.
node research/beta-opfs-release/controlled-tabs.test.cjs
```

On 2026-11-04 the actual pinned old service worker controlled a signed-in old tab. A pending v1 file with injected conflict/attempt metadata survived the test-only Caddy route/config switch, v2 open and explicit OPFS migration. A previously held old-v1 write and a subsequent old-v1 read both failed closed with `VersionError`. The candidate Files bundle was actually loaded; it created a file through the UI, opened it in the existing beta Text app, edited offline, synchronized via the pinned signed gateway, and reopened in a fresh signed session. The old worker remained active while a client remained controlled; after old pages closed, the candidate worker became active and reported the candidate cache ID. No arbitrary old tab can be assumed safe merely from this single fixture.

The first fixture omitted COEP/COOP headers from its static file-server routes; Chromium blocked the OPFS worker with `ERR_BLOCKED_BY_RESPONSE`. Adding the same isolation headers made the isolated rerun pass. Any future real overlay must preserve the actual beta CSP and isolation headers on every module and worker response. The fixture deliberately serves the guest image as 404 and omits irrelevant public icons and speech assets, so their 404s are expected. It uses a test-only localhost switch, **not** the production Caddy generator, maintenance gate or a durable transaction. It does not test a real issuer configuration upgrade, offline desktop startup, real service-worker tabs on other devices, a host restart or power loss, all unrelated applications, or disk exhaustion. Both selected shell scripts are query-bearing requests that bypass the old worker asset cache; this candidate makes no offline-startup guarantee.

`recovery-model.py` is a pure state-machine invariant sketch, tested for pre-floor guarded-v1 recovery and post-floor forward-or-remain-gated behavior. It has no filesystem journal, host adapters, custody, atomicity or service controls, and is not a reviewed managed transition/recovery operator. The actual operator, v2-safe recovery after interrupted activation, full retained-route and all-site validation, beta capacity headroom, final host diff review and actual config implementation are still open. The old guarded-v1 loader is not a functional downgrade after v2 opens the browser database; never clear account/browser data to force rollback.

### Issuer/config qualification and corrected shell candidate

The earlier `feaa1c6f…` package is **superseded**: beta's existing `saveLayout()` returned `undefined` on successful saves, so the transplanted teardown interpreted success as failure and prevented session changes. The corrected package above explicitly returns success/failure using the beta implementation; its `saveLayout()` returned `true` in a signed desktop session. The signed controlled-tab migration, Files/Text edit and reopen test was repeated on the corrected package; v1 pending/conflict data survived and old-v1 access failed closed. This did not exhaustively qualify beta app lifecycles or test every sign-out confirmation path.

The authoritative beta metadata is generated by the existing issuer and forwarded through the existing guest frontend. `config/fileStorage.json` remains a build input/intent description, not a config endpoint. `build-issuer.py` derives a sealed release from native manifest `1666491de4fe097285f02a5b6f7602fe57e4b9d3b2995bf016d4a9e809e36a51`; it verifies the exact complete inventory and generates a minimal opt-in issuer change only. Result with that exact release: native manifest `853c12e581c9f89fc3d78507f43941dd16cd0b4b894b28cdb8317e8a58340f21`, changed script SHA-256 `90c31ca9d363cc6c4bedb046ea591eb3a639849da279e960dd532dfc360010a3`. Default config remains unchanged. The opt-in requires user files and root mount on beta or loopback.

`issuer-config-test.py` starts actual old and derived issuer processes consecutively against one disposable private runtime, then starts the existing disabled-network guest frontend. It verifies unchanged full issuer configuration and identity apart from the intended field, guest forwarding, and disallowed origins/mounts. It does not test signed-account continuity, systemd, Caddy managed routing, or authentication under actual beta. These are isolated candidate artifacts, not an installed issuer or rollout authorization. The real deployment needs a reviewed managed issuer release/flag and a durable gate with a verified forward-only floor, health checks, and recovery; the Python recovery model is not that operator.

`session-controls.test.cjs` additionally exercises the corrected shell with the actual account-menu Sign out control and the existing beta Text app. In a real signed fixture it verifies cancel preserves the dirty editor, account and mirror; an injected layout-save failure preserves them and performs no logout; and a successful real layout save terminates a deliberately stalled OPFS read before an intentionally withheld navigation (the read rejects `AbortError`). A second signed browser context signs out through the menu and signs in as another registered account through the login UI; the first account's file returns `File not found`. The registered-account menu does not expose direct account switching, so this verifies the actual sign-out/sign-in sequence. These tests use the controlled fixture's issuer, not the sealed native issuer restart. The first exploratory run raced Text's asynchronous file load; the qualified test waits until the file has loaded before editing.

With the controlled fixture running, switch it to the corrected candidate (`curl -fsS http://127.0.0.1:19991/on`), start isolated Chromium CDP on port 19298, then run `NODE_PATH=/path/to/node_modules node research/beta-opfs-release/session-controls.test.cjs`. Fixture ports and profiles must be disposable; do not run this against a live site.

## Public artifact backup and reproducibility

All of these are **research artifacts**, not live releases. They contain public application files only; do not place runtime directories, account databases, issuer private keys, or guest credentials in them.

- The previously shared R730 archive `/mnt/data10tb/codi-beta-opfs-release-6db06c6c3/public-candidate-fixture.tar.gz` (SHA-256 `1565e26712dda66c638852c9e464cca36b52820e44e9014179f31a27f7139282`) contains useful public baseline/Files inputs **and the superseded unsafe `feaa1c6f…` candidate**. Never use that candidate as the current release.
- The corrected candidate is `/mnt/data10tb/codi-beta-opfs-release-6db06c6c3/candidate-3ad04c48.tar.gz`, archive SHA-256 `93a5c701eec04c473779f6b981d87920c17958ed1d00c93c87a1924d88af7974`. Its unpacked 87-file manifest is `3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc`. The archive was separately extracted and fully checked against `verify.py` after transfer.
- Exact native baseline: R730 `/mnt/data10tb/codi-beta-issuer-base-1666491d`, manifest SHA-256 `1666491de4fe097285f02a5b6f7602fe57e4b9d3b2995bf016d4a9e809e36a51`.
- Exact derived native issuer: R730 `/mnt/data10tb/codi-beta-issuer-opfs-853c-sealed`, manifest SHA-256 `853c12e581c9f89fc3d78507f43941dd16cd0b4b894b28cdb8317e8a58340f21`. Both native directories passed full 520-file inventory and digest checks. The older exploratory directory `/mnt/data10tb/codi-beta-issuer-opfs-isolated-20261104` is **not sealed**: an execution rewrote Python bytecode; do not use it as an artifact.

Example retrieval/rebuild from a checkout containing these scripts:

```sh
scp r730:/mnt/data10tb/codi-beta-opfs-release-6db06c6c3/candidate-3ad04c48.tar.gz /tmp/
sha256sum /tmp/candidate-3ad04c48.tar.gz  # compare to 93a5c701… above
mkdir /tmp/codi-opfs-candidate-check
tar -xzf /tmp/candidate-3ad04c48.tar.gz -C /tmp/codi-opfs-candidate-check
python3 research/beta-opfs-release/verify.py /tmp/codi-opfs-candidate-check/codi-beta-opfs-transition-candidate 3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc
scp -r r730:/mnt/data10tb/codi-beta-issuer-base-1666491d /tmp/codi-issuer-base
PYTHONDONTWRITEBYTECODE=1 python3 research/beta-opfs-release/build-issuer.py /tmp/codi-issuer-base /tmp/codi-issuer-derived
# Check the printed derived manifest hash against 853c12e5… above.
```

Do not execute Python out of an artifact tree without disabling bytecode writes, and check the entire manifest after any execution. The build requires the pinned source checkout and the old archive's exact public baseline and Files inputs; the controlled signed test additionally requires the pinned dd8 gateway package, Caddy, Chromium, Puppeteer and a Python environment providing the issuer/gateway dependencies. A portable archive of that Python environment is **not** included. The separate real issuer config test used `/tmp/codi-audio-upload-19584-venv/bin/python` on the workstation; this is a local test prerequisite, not a backed-up release dependency. Real managed transition/recovery and signed-account continuity across the native issuer restart remain unqualified.

The issuer config fixture now runs the issuer, guest frontend and negative controls with Python `-B`, and checks both native trees' complete pinned inventories and contents before **and after** the process tests. This was rerun successfully against fresh copies of the R730 baseline and sealed derived trees. The earlier config test demonstrated behavior but did not check post-run bytecode integrity and must not be used as sealed-artifact custody evidence.

Integration lead independently verified the complete 520-file baseline and fresh derived issuer inventories on R730, and the corrected candidate archive hash, on 2026-11-04. The local corrected candidate also passed the closed 87-file verifier. These checks are artifact custody, not deployment or signed-account upgrade evidence.

## Native issuer and signed-file continuity

`native-continuity-fixture.py` runs the exact sealed native issuer and disabled-network guest frontend as separate actual processes, along with the exact dd8 gateway and a loopback-only Caddy proxy. It gives the two issuer versions the same **disposable** private runtime. `native-continuity.test.cjs` uses Chromium to register through the real issuer, write/read a file using the signed gateway SDK, restart the issuer as `853c12e5…`, log in again, and check the same account subject, issuer keys, bytes, and SHA-256. The test passed, including full native and gateway inventories before and after the fixture and `-B` process launches. It does not test production issuer service installation, managed host transition, migration of browser storage, or a real user account.

The R730 `/mnt/data10tb/codi-beta-client-44da-dd8cbea7` gateway directory has unmanifested `__pycache__/*.pyc` from prior testing. It is **not an exact sealed inventory** even though its manifest's listed file hashes match. Make a disposable copy, remove only unlisted bytecode from that copy, and verify its *entire* inventory against `files-service.json` before using it; never clean the shared source directory as part of this procedure. The native continuity fixture checks exact inventories and refuses extras. Example copy preparation:

```sh
scp -r r730:/mnt/data10tb/codi-beta-client-44da-dd8cbea7 /tmp/opfs-dd8-copy
python3 -B - <<'PY'
import json,os
from pathlib import Path
root=Path('/tmp/opfs-dd8-copy'); keep=set(json.loads((root/'files-service.json').read_bytes())['files'])|{'files-service.json'}
for parent,dirs,files in os.walk(root,topdown=False):
 for name in files:
  p=Path(parent)/name
  if p.relative_to(root).as_posix() not in keep:
   if '__pycache__' not in p.parts or p.suffix!='.pyc':raise ValueError('Unexpected extra: '+str(p))
   p.unlink()
 for name in dirs:
  p=Path(parent)/name
  if p.name=='__pycache__' and not any(p.iterdir()):p.rmdir()
PY
```

`floor_journal.py` is a **non-CLI, unbound research component**, not a hosting operator. Its adapter contract requires the *existing* protected hosting lock, managed route/issuer transition, gate verification, exact baseline/forward artifact checks, issuer/account custody and disk-reserve checks. It journals and fsyncs before gating, fsyncs an irreversible floor before candidate exposure, and requires a recovery actor pinned to the same baseline and candidate. `floor-journal-test.py` exercises actual subprocess exit and filesystem journal boundaries, rename/fsync faults, stale actors, unavailable candidates, and re-gating after failed candidate health with a fixture adapter. This proves neither an actual managed-webctl gate nor crash/power-loss behavior of the production host. The existing hosting transaction's prepared-phase rollback must not run after this floor without a reviewed integration that preserves forward-only recovery. A concrete production adapter, lock composition, filesystem custody, disk reserve, managed generator changes, and independent review remain required before deployment.
