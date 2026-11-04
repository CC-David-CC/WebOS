# Files-only beta release readiness — 2026-11-04

**Decision: do not activate the OPFS Files candidate yet.** This is a staging and qualification plan, not an activation instruction. The integrated research tree includes unrelated desktop and CAD changes; it must not be deployed wholesale. No live state, routes, services or accounts were changed for this assessment.

## Candidate progress after the baseline assessment

Desktop `2e312b797` adds reproducible sealed candidate `3ad04c48…`, keeping the
full non-Files catalog and guarded version floor. The isolated signed test
covers an old controlled tab, v1 metadata migration, Files/Text save/reopen,
sign-out cancel/save failure/stale worker and a second account. The lead verified
the closed 87-file inventory. The earlier `feaa1c6f…` candidate had a layout
return-value bug and is superseded.

Separate issuer/guest tests exercise derived native release `853c12e5…`
from pinned `1666491d…`, preserving issuer config/identity except opt-in OPFS
metadata. Later checkpoint `b391e259b` proves actual signed account/file
continuity across that issuer restart and adds a filesystem/process-tested
forward floor journal. The lead independently passed four `c2d6f696` inventory,
managed-binding, copied-controller/real-Caddy and maintenance tests. Thus this
work is no longer only a pure recovery model. It still is not an assembled
production transition. See `../research/beta-opfs-release/README.md` and the
current successor handoff for exact boundaries.

The separate `research/beta-files-operator-20261104` branch now contains exact
route and normalization checks, retained issuer recovery state, local systemd
and Caddy process-death fixtures. A protected launcher with combined signed
service health, capacity and public beta acceptance remains unfinished. Do not
merge its unrelated hosting base wholesale. Recovery after the floor may gate
or advance to v2, never restore a v1 writer. Normal unrelated-site maintenance
must remain available while preserving beta. Nothing was activated.

Later read-only capacity was about 204 MiB above the required 5 GiB reserve.
A disposable run of the exact issuer stage consumed about 115 MiB allocated;
another 128 MiB stage at the same time would exceed that headroom. Measure the
complete transaction working budget. The proposed 256 MiB extra margin is not
the reserve itself. Do not lower the reserve or move account data implicitly.
The plan-only launcher hash below was subsequently rechecked and matched.

## Observed beta baseline

Read-only public HTTPS and service checks on 2026-11-04 found:

- Beta, main and `/desktop/` returned HTTP 200. Beta issuer, frontend and gateway services were active; the frontend and gateway remain distinct beta service identities and state roots. The earlier `codi-beta-guest` name is not the active unit; the frontend unit is `codi-beta-frontend`.
- The **actual bootstrap request includes a query**: `desktop-apps.js?simplified=1` SHA-256 `0d1cbcb4e6b23beb0c6b7eecce8b35244438fb4341c2e325203c739c64118b81`. It imports `storage/browser/mirror.cbfafe53eae1afdac1f2a9af0bfdbd26cae59b1be8f5d96f6bebec2a56c158ed.mjs`, whose bytes hash to the filename. The bare `desktop-apps.js` and bare `storage/browser/mirror.mjs` return **different, older bytes**; do not use those as the selected beta floor. Preserve the existing guarded loader, both retained versioned asset sets and their exact routing.
- Beta `app.js?simplified=1` is `6965a2a27da3fa1d3318c0ac845924136ad9a2e09cf9ca2d624d2f94f5441df6`; bootstrap is `bf8de57e9f8a0388d51821d4e0be68400ddda40c0f96e5f27826e68fe689475f`. Public gateway SDK is `44da83bdccf43a2b36ae4b3f48eaf94fc1006b88180456e26faba61aae344869`; running beta gateway release is `dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1`. Its advertised signed binary read, chunk batch and delta capabilities were present. `fileStorage` was absent from public beta configuration: current beta remains IndexedDB v1, not the OPFS candidate.
- Current beta catalog SHA-256 is `c5b79a365135d73c939c0afdc7a97864ea00ba24379d179d8cca06843644cd22`. Its Files bundle is `bd33bb70885171501dec4cc5ac7cc2c0551304e88345235432e2a6e30bd5bd88`; Text is `4cb2adbf206d5e78f89d9344a2ffe8d367a9b8f77bab59dd1ec9b717ad526b2b`; CodeMirror is `c61da9af5b23236d13903f04d906d83aff0cc93156f02d77ec8beefedc34b679`. Cache manifest SHA-256 `18140be41c4f6cd3a1fcdbee39998e00c363ed677223eeffc8cc97c450ba4720` identifies release `0965a0cbdd022f588061cdc23e10eb6b18fa5977cc3f6a05569439eaf11d2020`; service-worker SHA-256 is `e49a8667db0e20b8fca90ee3e19eec17b70b964846b916d734391dda93c3f69c`. Query-bearing loader requests bypass that worker's normal asset cache. A controlled-tab transition must nonetheless test the complete worker/cache behavior, not assume this alone makes it safe.
- `/var/lib/codi-user-files/beta` and `/` were on the same filesystem with 5,597,564,928 bytes available: only 228,855,808 bytes (about 218 MiB) above the participating gateway's 5 GiB reserve before other writers. Actual concurrent staging requirements can exceed that headroom. Recheck immediately before any candidate work; free space does not guarantee an admission. Do not delete or move account data as part of this plan.

The latest documented protected beta hosting reconciler at `/srv/codi-connected/beta-hosting-plans/f1ed9a9d1/research/beta-isolated-hosting/ops/beta_launcher.py` is a **plan-only** reconciler; the recorded launcher SHA-256 is `9c1b32ecb71993649a2bd8e61f652486448543842a06c1654d685055959b9a95`. The root-owned file was not readable to this unprivileged inspection, so its live bytes were not independently rehashed here. Its receipt says `apply` and `recover` are deliberately refused. A newly reviewed, pinned operator with crash recovery is a prerequisite, not an existing deploy button.

## Candidate inputs, not a release

The tested integrated source used here is `e66cda39c`. Storage asset source hashes:

| Relative to `active-system/storage/browser/` | SHA-256 |
|---|---|
| `mirror.mjs` | `67962be43d99bd0bb22229fc8f30c309d0637f9440e9903c2a070b6d618fa187` |
| `account-context.mjs` | `dd19562a1a13e2ac79142b9cb7a2cf0a3cba77ff03fa5407c0ced4e5c6a518e9` |
| `verified-content.mjs` | `4503fade5803896a036430cba092ec5c90c15ba6cd0d1028c7b4fd0503eccc12` |
| `opfs/core.mjs` | `90b245475d95570135d4eba2b92717ac90350944e9ee7a5e6d595e275ebd5299` |
| `opfs/shared.mjs` | `7399a7fe440c202f1d645230654aa86c035ac4adf072452ac718cc44efb44d9d` |
| `opfs/store.mjs` | `65a74ef7439d530d766595834f70334bcfbe01d3fb31a9d906948a88cb334faf` |
| `opfs/worker.mjs` | `9d97301fb4e9e20173bc0c2f57aa2e23c479b5dac0b2b193b76d0716fef7ca1e` |
| `opfs/LICENSE.txt` | `2153bd2978793748fbe0eb8f838ae2ae19f03f9d4ee5473dd1628a0c0790e4ab` |

Files app source inputs include `apps/system/files/index.mjs` SHA-256 `7ecde441edf8ae80b01c6f1b8b6126bda796c24b643271f873422dc1f7d6adf5`, `files.css` `c7c6f11f145793e120183574a41fa8f449a2e41980d11b80de2b93fff072f086`, `app.json` `d8432fa4c4c3644cf7528a05230cd1fb8662d79c85859294a99ca5ac81c06905`, `download-snapshot.mjs` `3d313645093e867ba8875127cb1243f89d73c9905b53f76c3822a838fc10a718`, `move-selection.mjs` `9be68af589cc8214bd065e7d9b2b78033a0ba340e6c2fc2f6ca061ff4b4abaeb`, and `sync-status.mjs` `89b5711aee912ff86c3e0ffa41926b88a076c95866f7504c9b03a5268596d59f`. The bundle also contains reviewed third-party dependencies and assets, so those source hashes alone are insufficient to recreate or verify it.

These are source hashes, not a sealed deployed package. `active-system/origin_service/public_storage.py` stages precisely that closed list, rejecting symlinks and unsafe hardlinked destinations. The integrated source's `app.js` is `027734f88b87cc99e23acdda97bac15d596386e8280127fc6afe297c6bd2ba94`; its `desktop-apps.js` is `e21a9646fcbec695d1f3237bae1c6dd71a1a7aba23a0f2ce572552d5f40b4444`. They differ materially from beta and include unrelated work; they are **not** approved whole-file replacement pins. Produce a minimal beta-derived host patch for account-context creation, explicit teardown/suspension and the Files API requirements, review each changed hunk, and retest the exact resulting host hashes. The new import graph must use an immutable/versioned namespace containing all sibling modules and worker assets; a hashed mirror that imports an unversioned mutable sibling is not a sealed release.

A disposable `build-public-apps.py --apps files text` build from this checkout, with Node 24.22.1, the pinned builder dependencies, the hash-checked Chonky preparation and the app-local CodeMirror dependencies, produced:

- Files bundle `12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244`, entry `684bfe19edaf7cce3de3986c87d95cd1e05f6b4b76976218359934137d6d17cb`.
- Text bundle `1e29e2b3fd4b97bf2d1890eaa25f3da119208b8fcf54790d1db5a38eb09e5958`, entry `db8a0cb4a9523ae804eb6ab1d57611d73b4d66fd4353b04a34de036b41002bb8`.
- CodeMirror bundle `c61da9af5b23236d13903f04d906d83aff0cc93156f02d77ec8beefedc34b679`, entry `117c3b7c9718655ab7dc7cc7531f81a8fb2a522bcadfd5515b516be4acad630a`, identical to beta's listed version.

The three-app catalog hash is `262b2c125120fc95bec34ad2645febe115cf608bff04be0c430f79f109b604ad`; **never publish that catalog as the complete site catalog**, because it omits the other applications. Reproduce from clean pinned dependencies; assemble a reviewed beta-derived catalog/cache manifest that retains every other existing entry and all needed old immutable URLs. Qualify whether Text replacement is necessary for the Files milestone rather than silently publishing it. Build outputs and node_modules are not source backups.

## Data-safety and transition gates

1. Secure adequate beta filesystem headroom and obtain exact current root-protected service, static, generator, manifest and Caddy pins with read-only preflight. Check the service identities, all sites, main/prototype hashes, retention floor and configuration again immediately before any candidate transaction.
2. Decide and implement a beta-only way to advertise `fileStorage: {version: 'codi-browser-file-content/1', backend: 'opfs', databaseVersion: 2}`. The current beta issuer command has `--user-files` but no OPFS flag; public configuration is the authority for this observation. A new beta-only issuer artifact/operator or another reviewed configuration path is required; no such deployable path is established here. Never copy issuer keys, databases, account folders or browser data between origins.
3. Qualify the exact assembled immutable host, catalog, cache worker and storage package against the actual beta guarded-v1 baseline, 44da/dd8, actual strict CSP and disposable signed accounts. Exercise old controlled tabs, queued/waiting service workers, maintenance gate, active operations, versionchange/blocked opens, reload, fresh sessions, conflicts, uncertain commits, interrupted upload/download and storage-full. Retain old URLs and reject unsupported old writers; an existing old tab cannot be assumed safe merely because files remain reachable.
4. Treat opening the mirror database at v2 as a **forward-only writer floor**: the v1 client cannot open it and cannot read OPFS references. Do not present an old guarded-v1 rollback as a usable rollback for a v2-upgraded origin. Recovery after v2 exposure must keep a tested v2-capable client and data intact, or explicitly stop safely until a reviewed repair path exists. Never delete browser storage, local pending edits, conflict/attempt metadata or server files to make rollback appear successful. The earlier protected route journal was tested for guarded-v1 overlays, not this v2 config/asset transition.
5. Supply a separately reviewed beta-only transaction with preconditions, maintenance/forward gate, retained sealed assets, pinned config, durable journal, safe recovery and all-site/main/prototype verification. It must cover an interrupted transition and a failure after v2 has been observed. Only the release owner should choose whether to apply it after those concrete artifacts and tests exist. Preserve the currently active SDK/gateway unless a separately reviewed requirement changes them.
6. Run public beta acceptance on disposable accounts after activation, if eventually authorized: actual Files/Text create, edit, save, sync, reopen, two-profile conflicts, session cancellation, retry after interrupted transfer and real guest separation. Verify main and `/desktop/` remain unchanged. Record actual served hashes, account-state boundaries, test results and recovery receipt; never claim success on source hashes alone.

## Evidence and remaining scope

| Gate | Existing bounded evidence | Still open for release |
|---|---|---|
| F01 saved data | OPFS save/reopen and actual guarded-v1 metadata migration tests | Controlled beta-derived transition now passes; actual managed transition/recovery remains, with no destructive downgrade |
| F02 account/session | Signed isolation and explicit teardown tests | Beta-derived sign-out/second-account controls pass; actual issuer upgrade continuity and all app consumers remain |
| F03 conflict | `2cec3e7e2` two actual browser profiles, offline UI edits, stale choice and keep-both | Final assembled release and broader conflict cases |
| F04 uncertain write | Actual committed-upload socket cut and reconciliation | Exact assembled release + route/issuer failures |
| F05 download integrity | `218536add` real signed cuts, OPFS refs, Chromium kill after failed transfers | Crash during publication/power loss and full release transition |
| F06 cleanup | Bounded explicit lease-aware collector tests | Automatic retention is intentionally disabled; orphan/published generations can accumulate and need a safe policy |
| F07 workers | `544480232` one VerifiedContent worker across cooperating tabs, cancel/timeout/renderer crash | SDK and app workers, browser RAM, broader load and final package |
| F08 transfers | `7064310e1` 128 MiB one-byte update, 71,470 request-body bytes in one run | Response/TLS overhead, slow links, load and overall RAM bounds |
| F09 Files UI | `99bc3ba06` bounded create/rename/move/copy/delete/upload/download and reopen | Full catalog, physical phone and actual release |
| F10 guest separation | `9f753a95c` real v86 guest-home reset and My files/server separation | All-app compatibility and production release |

Additional local Chromium check on this assessment used the exact guarded-v1 mirror hash `cbfafe53…`: an offline v1 row with injected conflict, pending, attempted and move metadata was upgraded, explicitly migrated into OPFS and read back with metadata and bytes intact; the old v1 client then failed closed with `VersionError`. `mirror-version-floor-browser.test.mjs` also passed an old in-flight write and blocked-upgrade test; `mirror-migration-metadata.test.mjs` passed its injected metadata case. These tests do not prove live rollout or every abandoned-tab and process-kill timing. Unknown worker/browser failure, quota exhaustion, user-cleared browser storage and uncoordinated host filesystem writers still require truthful recovery behavior; no snapshot or browser persistence permission guarantees physical power-loss durability.

## Read-only host capacity inventory

Webhost `/dev/sda2` is a 109 GiB ext4 root with about 5.3 GiB available; `/var/lib/codi-user-files/beta` is on that same filesystem. A separate `/dev/sdb1` ext4 filesystem is mounted at `/srv/data` with approximately 299 GiB available. R730 `/mnt/data10tb` has approximately 6.2 TiB available for isolated build and test work. Neither external staging capacity automatically increases the gateway's root-filesystem space. Moving active protected state or release roots would require a separately reviewed service, mount, ownership and recovery plan.

The unprivileged `du -x` inventory reported roughly 70 GiB under `/srv/codi-connected/simplified`, with 130 release-snapshot directories. The currently selected cache release `0965a0cb…` measures about 1.1 GiB by itself; an older snapshot `02041196…` measures about 957 MiB. Some files are hardlinked (the selected release's `app.js` has link count two), so adding per-directory sizes or assuming that removing a directory frees its apparent size is invalid. The older snapshot is an **audit candidate**, not a verified disposable release: protected manifests, active routes, retained old tabs, rollback floors, and archives must be checked before any disposition. The separate drive already contains root-only `/srv/data/codi-archived-native-20261101` and `/srv/data/codi-archived-simplified-20261101`; their contents and completeness were not inspected. `/srv/codi-connected/official-service-test` is a 332 KiB test artifact worth checking for references, but is too small to solve capacity pressure. No test artifacts, releases, account data, or keys were deleted or moved in this review.
