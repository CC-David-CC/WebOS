# Beta-derived Files/OPFS candidate — isolated, not deployable

This directory builds a reproducible public-asset candidate from the exact observed beta guarded-v1 baseline and source checkpoint `6db06c6c3`. It is **not** a hosting operator, a live release, or an instruction to deploy. The existing beta plan-only reconciler still refuses apply/recover. No private state is an input.

## Reproduce

Prerequisites: Python 3; Node 24.22.1; the checked-in app-builder dependency lock and reviewed Chonky/CodeMirror dependencies; an isolated Chromium and Caddy for browser testing; Python aiohttp, argon2 and cryptography for the fixture. The actual beta gateway package is backed up at `r730:/mnt/data10tb/codi-beta-client-44da-dd8cbea7`: `files-service.json` SHA-256 `dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1`, SDK `gateway_service/client.mjs` SHA-256 `44da83bdccf43a2b36ae4b3f48eaf94fc1006b88180456e26faba61aae344869`. Fetch public/test artifacts to a disposable directory; do not copy the server's real issuer database, keys or user files.

```
python3 research/beta-opfs-release/prepare-baseline.py /tmp/opfs-public-baseline
python3 active-system/scripts/build-public-apps.py --apps files --node /path/to/node --output /tmp/opfs-files-bundle
python3 research/beta-opfs-release/build.py --baseline /tmp/opfs-public-baseline/candidate-inputs --files-bundle /tmp/opfs-files-bundle --out /tmp/opfs-candidate
python3 research/beta-opfs-release/verify.py /tmp/opfs-candidate feaa1c6fc273ca0b46c49827e20089218f11762973e20961625a8fc80e13f8ba
python3 research/beta-opfs-release/packaging-test.py /tmp/opfs-public-baseline/candidate-inputs /tmp/opfs-files-bundle
python3 research/beta-opfs-release/recovery-model-test.py
```

`prepare-baseline.py` fetches only public files required by the isolated desktop test and verifies the cache manifest and each selected file. It stops if the observed beta pins change; it must not silently accept new live bytes. Its root keeps the unmodified bare loader for the old worker; `candidate-inputs/desktop-apps.js` contains the distinct selected `?simplified=1` guarded loader. It is a reduced baseline, not a complete backup of the site. A public-only archive containing the verified test baseline, Files bundle and candidate is on R730 at `/mnt/data10tb/codi-beta-opfs-release-6db06c6c3/public-candidate-fixture.tar.gz`, SHA-256 `1565e26712dda66c638852c9e464cca36b52820e44e9014179f31a27f7139282`; the dd8 gateway is the separate pinned artifact above.

## Candidate boundaries

The candidate manifest is `feaa1c6fc273ca0b46c49827e20089218f11762973e20961625a8fc80e13f8ba`. It seals 87 regular files, including a whole content-addressed storage graph under `storage/browser/releases/0ea94092ebb6cd6120433c49cd4fe1284842e334b6313dc9945ed3d6cf87011a/`; relative imports and worker code stay within that immutable graph. `verify.py` rejects altered files, extras, symlinks and hardlinked candidate files. The builder verifies selected beta inputs, every storage/host source pin, and the complete pinned Files bundle inventory. It emits `patches/app.diff` and `patches/desktop-apps.diff` against beta, rather than replacing beta with the unrelated integrated desktop tree. The diff carries the tested session-lifecycle/teardown pieces because beta's older sign-out otherwise has no equivalent protection. These changes still require independent review against every beta app lifecycle.

The beta catalog keeps all non-Files entries structurally identical and substitutes Files bundle `12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244`; existing beta Text and CodeMirror entries are retained. The derived cache manifest has ID `66b864076c7f618b8c1f1f52128247498f82e84834924f41c6d7838f00c35485`; old app asset records remain. The output `config/fileStorage.json` is only a desired OPFS configuration fragment, **not** a deployable issuer configuration or an approved way to modify the real beta issuer.

| Candidate output | SHA-256 |
|---|---|
| `shell/app.js` | `7dd809b16b4a74ccd7c99097f5078f10ccd30cd14b14578e576a97a11948e057` |
| `shell/desktop-apps.js` | `38f02da4e7df4430361296175225044b8a2f3b579ce0ef33a8acd7e56868ff84` |
| `assets/desktop/apps.json` | `2b835e478b1a5e24015b7a353b32838e6026d7fe6f56bad71660f6f7ce83f07a` |
| `assets/desktop/cache-manifest.json` | `3c5d5a241231cb83eb62f71c7cb4ae632f3fa916b1892035cd68ee83a1a748d2` |
| `assets/desktop/offline-worker.js` | `d2c23435beac5ae0c354ee16eba9d708a975855e3538a4e36717b2900c9e2519` |
| `patches/app.diff` | `937ba6fa3ac8e4522d9305c8b37edea47d9d6cfb5e253730d78f04bb7942a5a7` |
| `patches/desktop-apps.diff` | `8d9b13a681283df0daa0a451167dab8a41826b04bd5ea8cfd96c859a66a721d5` |
| `config/fileStorage.json` | `5d24041f30f0a368d77cb0fe14606bde11568200a9e4f2c6a9b6c893cc292b5c` |

## Isolated controlled-tab test

Run the following only with disposable local state, never a live hostname:

```
CODI_GATEWAY_ROOT=/path/to/pinned-dd8 \
CODI_BASELINE=/tmp/opfs-public-baseline \
CODI_CANDIDATE=/tmp/opfs-candidate \
CODI_CANDIDATE_HASH=feaa1c6fc273ca0b46c49827e20089218f11762973e20961625a8fc80e13f8ba \
CODI_CADDY=/path/to/caddy python3 research/beta-opfs-release/controlled-fixture.py
# Start isolated Chromium CDP on 127.0.0.1:19298, with puppeteer-core available.
node research/beta-opfs-release/controlled-tabs.test.cjs
```

On 2026-11-04 the actual pinned old service worker controlled a signed-in old tab. A pending v1 file with injected conflict/attempt metadata survived the test-only Caddy route/config switch, v2 open and explicit OPFS migration. A previously held old-v1 write and a subsequent old-v1 read both failed closed with `VersionError`. The candidate Files bundle was actually loaded; it created a file through the UI, opened it in the existing beta Text app, edited offline, synchronized via the pinned signed gateway, and reopened in a fresh signed session. The old worker remained active while a client remained controlled; after old pages closed, the candidate worker became active and reported the candidate cache ID. No arbitrary old tab can be assumed safe merely from this single fixture.

The first fixture omitted COEP/COOP headers from its static file-server routes; Chromium blocked the OPFS worker with `ERR_BLOCKED_BY_RESPONSE`. Adding the same isolation headers made the isolated rerun pass. Any future real overlay must preserve the actual beta CSP and isolation headers on every module and worker response. The fixture deliberately serves the guest image as 404 and omits irrelevant public icons and speech assets, so their 404s are expected. It uses a test-only localhost switch, **not** the production Caddy generator, maintenance gate or a durable transaction. It does not test a real issuer configuration upgrade, offline desktop startup, real service-worker tabs on other devices, a host restart or power loss, all unrelated applications, or disk exhaustion. Both selected shell scripts are query-bearing requests that bypass the old worker asset cache; this candidate makes no offline-startup guarantee.

`recovery-model.py` is a pure state-machine invariant sketch, tested for pre-floor guarded-v1 recovery and post-floor forward-or-remain-gated behavior. It has no filesystem journal, host adapters, custody, atomicity or service controls, and is not a reviewed managed transition/recovery operator. The actual operator, v2-safe recovery after interrupted activation, full retained-route and all-site validation, beta capacity headroom, final host diff review and actual config implementation are still open. The old guarded-v1 loader is not a functional downgrade after v2 opens the browser database; never clear account/browser data to force rollback.
