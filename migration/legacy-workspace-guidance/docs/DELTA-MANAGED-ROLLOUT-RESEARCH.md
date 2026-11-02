# Account file delta release candidate — research only

This candidate has not been deployed. It combines the tested account-file delta implementation with the currently live Microduck source while preserving the live gateway's existing `user_store.py`, account data, configuration, flags, and authorization. No database, user files, service configuration, or live desktop assets are included in these artifacts. The experimental branch's separate unfinished folder-move changes to `user_store.py` are intentionally excluded.

## Reproducible artifacts

Build from a separately verified, code-only copy of the live gateway release using `active-system/scripts/build-delta-managed-candidate.py`. The builder checks the baseline manifest and pinned changed sources. The resulting worker manifest SHA-256 is `578fe7d30b84361e09ca7d686ff9addf604114a49fce19970f9ca707ee30631f`; operator manifest is `59c0563c664cc373c7ba2e5c2efa00358dafcdf235c17add1ed65d6951f30666`. The earlier build was reproducible; reproduce this revised worker before staging. The base worker manifest is `8d977a271a776fd7265a775bc5c74d818abed9136049af3ae8adfd04cd9c0257`.

Worker changes relative to that exact live baseline are `gateway_service/http.py`, `gateway_service/client.mjs`, and the explicitly authorized new `gateway_service/delta.py`. Live `gateway_service/user_store.py` is unchanged, SHA-256 `599895e898c21ab5551dddd846a7f8f6611a03ddd8f8eeb5ac4dfd42b29b3d6a`. The candidate operator changes only `file_service/operator.py`, SHA-256 `cc78d343b186d0374ed92c0b96de15c0d8deea273df0abb539a47ff80a5d2e58`: it permits exactly the existing worker inventory or that inventory plus the named delta file. Arbitrary extra paths are still rejected. It must be installed/configured before the delta worker, because the currently live operator rejects the additional path.

Example local build:

```sh
python3 active-system/scripts/build-delta-managed-candidate.py \
  --baseline /tmp/codi-live-gateway-release-8d977a \
  --worker /tmp/codi-delta-repro-worker \
  --operator /tmp/codi-delta-repro-operator
CODI_BASE_WORKER=/tmp/codi-live-gateway-release-8d977a \
CODI_DELTA_WORKER=/tmp/codi-delta-repro-worker \
python3 tests/delta-operator-allowlist-test.py
```

The baseline must be obtained and verified separately from the protected release; a path alone is not proof. Artifacts do not include private runtime data. These paths are local research locations, not installation paths.

## Evidence and boundaries

The allowlist test accepted exact baseline/candidate inventories and rejected extra, modified and symlinked files. The actual verifier also accepted root-protected copies of both worker releases. An isolated installed-systemd test using these exact two manifests passed signed HTTP and account isolation, worker/proxy recovery after process death, replay refusal, configuration drift checks, migration, retention and cleanup. The first fixture attempt failed because its test-generated usernames violated the current naming policy; the fixture was corrected, then passed. Nothing was installed on the live host by that test.

Against the exact candidate worker and preserved live storage implementation, isolated signed-browser tests passed a 16 MiB file and two simultaneous 8 MiB transfers, including changed/unchanged data, shifted insertion, binary/legacy behavior, malformed input, conflicts, isolation, and a deliberately interrupted request. In that interruption, the server had already completed the write; reconciling the resulting hash succeeded. These are local tests, not live/WAN qualification. A larger 104 MiB run was started but its result was lost from the test session; it is not counted as passed here.

The installed-systemd fixture exercised fresh configuration, not a production-shaped `configure-user-files` operator replacement or a code-upgrade interruption and rollback. The existing upgrade helper's handling of an error around its committed journal marker needs fault injection and independent review; do not treat normal successful tests as proof of crash-safe upgrades. Recheck the source, exact manifests, current native and gateway state, and user data before any rollout; these observations are time-specific, not permanent live pins.

## Proposed staged deployment and recovery (not executed)

1. Independently review the source, exact inventories, account authorization, service dependencies and recovery behavior. Qualify a production-shaped local operator switch and code upgrade, injecting failures around journal writes, service restart and recovery. Keep actual live issuer, desktop, gateway configuration, accounts and unrelated services unchanged while doing so.
2. Under the existing administrative workflow, verify current state and create protected content-addressed operator and worker releases matching the hashes above. Verify complete inventories and root ownership on the host. Confirm the current gateway has no pending operation and the current Microduck issuer and desktop are healthy. Save exact configuration and operation records with known protected snapshot paths; do not copy or roll back user databases or user files.
3. Using the existing native `configure-user-files` operation and its locks/journal/recovery, switch only the operator reference to the new operator while retaining the old worker and all other flags. Verify issuer health and that the old worker remains active. A failed or interrupted transition requires native operation recovery based on its recorded journal, not manually editing its config.
4. Use the existing managed private-file code upgrade helper to switch the worker to the candidate. Validate its result and resulting worker/operator/config hashes, running roles and HTTP capabilities; an exit status alone is insufficient. Recovery must follow the helper's actual journal and verified phase. Keep the live Microduck desktop and issuer release unchanged; the issuer service may restart during a managed change.
5. Run signed-account and simultaneous transfer smoke checks, cross-account refusal and interrupted-write reconciliation, verify Microduck and unrelated sites, and record exact release/config hashes. The served gateway client and server must be updated together; the desktop already obtains that client from the gateway.

If rollback is needed after a completed upgrade, first use a verified managed code upgrade back to the previously pinned worker while the new operator still accepts both inventories. Then use native `configure-user-files` to restore the prior operator reference. Resolve pending journals before either step. Preserve all account/database/file state and confirm service health; never restore an old data snapshot merely to roll back code. Interrupted or ambiguous operations require an independently reviewed exact recovery procedure before use.

## Collision budget and lock capacity follow-up

A malicious weak-checksum collision previously caused hundreds of thousands of strong hashes. The revised client stops after 64 unsuccessful SHA-256 matches, then requests an ordinary version-checked full upload. Successful matches do not consume that budget; the client also rechecks session validity immediately after each awaited digest. Node tests exercise the budget, a session change during a digest, and 2,048 successful hashes for a matching 128 MiB file. Real Chromium repeated the adversarial collision test and made exactly 64 hashes. Against the exact revised packaged worker and a real signed local account, an intentionally forged collision signature fell back to an ordinary full replacement and read back byte-for-byte. The signed 16 MiB account/legacy/isolation regression also passed. No production service was touched.

The preserved live `open_read_snapshot` hashes under the global storage lock; signature generation then happens outside it. In one warm-local-disk isolated sample, a 128 MiB snapshot held other account work for about 84 ms; the separate signature scan took 169 ms, and the unrelated account's first read waited 85 ms. This does not qualify cold disks or 100 parallel users, and the global lock can wait much longer under contention. Moving hashing outside the lock or caching signatures requires careful authorization, version, snapshot and invalidation design, especially for local in-place writes. This release intentionally leaves live storage semantics unchanged; capacity improvement remains follow-up work.
