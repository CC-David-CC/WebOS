# System fixture and reference source ownership

76 original source/configuration/reference files now have parent-owned archival locations.27 browser fixture HTML pages and operator/check sources accompany the previously retained JavaScript/Python operators. Host-operation definitions live under `deploy/legacy-backend/ops/`. Shared system/backend contracts, requirements and guidance remain under `migration/legacy-system-guidance/`.

## Actual verification

All76 current files match captured original blobs/modes and retain selected histories.82 selected source blobs pass UTF8/bounded literal screening. JSON parses, Python helper histories pass AST/context review, and shell wrappers pass `bash -n` with startup environment files disabled. No original operator, backup/build/G-code action, embedded script or service directive was executed. The systemd unit/timer files were not installed or started.

27 captured HTML source blobs were parsed for script tags; four inline JavaScript blocks passed Node syntax checks. Host/root-relative/external script targets remain unresolved runtime port requirements. Zero relative script-src references were proven in this set, so no helper/asset closure or new browser support follows. No page was opened and no URL fetched.

Two current JSON files remain private for unresolved literal review: the old shared fixture catalog and old goal-requirements file. Their markers are not automatically declared real credentials, and their values are omitted from audit output. The earlier57 Python holds remain private.

Seven source-assembly checks pass in the complete clean assembly with the original workspace and primary working tree hidden. All124 child pins, current source implementations, dependencies, supported entrypoints, services and deployment remain unchanged. Old contract/status/policy/checksum files are historical source, not current account-storage, agent authorization or functional proof. New ignored/external asset completeness remains a separate gate.

Mechanical filtered baseline `cbb80c5a4aebcfb033bc8f41495ffbe12659a9e0`; parent source merge `04234ecd198ff70721c9d297d33e6a42ccfc62b9`. Private phase54 retains path/copy histories, source structure checks, HTML script metadata, selected commit/ref maps, commands/exit codes, exact byte/mode proofs and unresolved holds.

| Original source | Retained parent source |
|---|---|
| `active-system/.gitignore` | `migration/legacy-system-guidance/.gitignore.source` |
| `active-system/HANDOFF.md` | `migration/legacy-system-guidance/HANDOFF.md` |
| `active-system/README.md` | `migration/legacy-system-guidance/README.md` |
| `active-system/codiserver-server-v0.3.0/.gitignore` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/.gitignore.source` |
| `active-system/codiserver-server-v0.3.0/AGENTS.md` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/AGENTS.source.md` |
| `active-system/codiserver-server-v0.3.0/CHECKSUMS.sha256` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/CHECKSUMS.sha256` |
| `active-system/codiserver-server-v0.3.0/CODEX_PROMPT.txt` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/CODEX_PROMPT.txt` |
| `active-system/codiserver-server-v0.3.0/README.md` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/README.md` |
| `active-system/codiserver-server-v0.3.0/VERSION` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/VERSION` |
| `active-system/codiserver-server-v0.3.0/contracts/acceptance.json` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/contracts/acceptance.json` |
| `active-system/codiserver-server-v0.3.0/contracts/tickets.json` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/contracts/tickets.json` |
| `active-system/codiserver-server-v0.3.0/docs/01_SERVICE_PLAN.md` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/docs/01_SERVICE_PLAN.md` |
| `active-system/codiserver-server-v0.3.0/docs/02_BUILD_TEST_LADDER.md` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/docs/02_BUILD_TEST_LADDER.md` |
| `active-system/codiserver-server-v0.3.0/docs/03_TICKETS.md` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/docs/03_TICKETS.md` |
| `active-system/codiserver-server-v0.3.0/docs/07_SUPERSESSION.md` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/docs/07_SUPERSESSION.md` |
| `active-system/codiserver-server-v0.3.0/docs/08_P2P_V03_DECISIONS.md` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/docs/08_P2P_V03_DECISIONS.md` |
| `active-system/codiserver-server-v0.3.0/docs/HOST_FILES_LATER.md` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/docs/HOST_FILES_LATER.md` |
| `active-system/codiserver-server-v0.3.0/docs/SOURCES.md` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/docs/SOURCES.md` |
| `active-system/codiserver-server-v0.3.0/provenance/inputs.json` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/provenance/inputs.json` |
| `active-system/codiserver-server-v0.3.0/provenance/v0.1-acceptance.json` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/provenance/v0.1-acceptance.json` |
| `active-system/codiserver-server-v0.3.0/provenance/v0.2.0/AGENTS.md` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/provenance/v0.2.0/AGENTS.source.md` |
| `active-system/codiserver-server-v0.3.0/provenance/v0.2.0/CODEX_PROMPT.txt` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/provenance/v0.2.0/CODEX_PROMPT.txt` |
| `active-system/codiserver-server-v0.3.0/provenance/v0.2.0/README.md` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/provenance/v0.2.0/README.md` |
| `active-system/codiserver-server-v0.3.0/provenance/v0.2.0/contracts/acceptance.json` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/provenance/v0.2.0/contracts/acceptance.json` |
| `active-system/codiserver-server-v0.3.0/provenance/v0.2.0/contracts/tickets.json` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/provenance/v0.2.0/contracts/tickets.json` |
| `active-system/codiserver-server-v0.3.0/provenance/v0.3-inputs.json` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/provenance/v0.3-inputs.json` |
| `active-system/codiserver-server-v0.3.0/reference/README.md` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/reference/README.md` |
| `active-system/codiserver-server-v0.3.0/requirements.txt` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/requirements.txt` |
| `active-system/codiserver-server-v0.3.0/shared/MESH_ARCHITECTURE.md` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/shared/MESH_ARCHITECTURE.md` |
| `active-system/codiserver-server-v0.3.0/shared/MESH_BROWSER.md` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/shared/MESH_BROWSER.md` |
| `active-system/codiserver-server-v0.3.0/shared/MESH_SCALE.md` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/shared/MESH_SCALE.md` |
| `active-system/codiserver-server-v0.3.0/shared/MESH_SOURCES.md` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/shared/MESH_SOURCES.md` |
| `active-system/codiserver-server-v0.3.0/shared/MESH_SUPPORT_SERVICES.md` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/shared/MESH_SUPPORT_SERVICES.md` |
| `active-system/codiserver-server-v0.3.0/shared/MESH_WIRE.md` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/shared/MESH_WIRE.md` |
| `active-system/codiserver-server-v0.3.0/shared/PROTOCOL.md` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/shared/PROTOCOL.md` |
| `active-system/codiserver-server-v0.3.0/shared/README.md` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/shared/README.md` |
| `active-system/codiserver-server-v0.3.0/shared/mesh-policy.json` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/shared/mesh-policy.json` |
| `active-system/codiserver-server-v0.3.0/shared/schemas.json` | `migration/legacy-system-guidance/codiserver-server-v0.3.0/shared/schemas.json` |
| `active-system/config.json` | `migration/legacy-system-guidance/config.json` |
| `active-system/ops/codi-browser-audit` | `deploy/legacy-backend/ops/codi-browser-audit` |
| `active-system/ops/codi-browser-policy` | `deploy/legacy-backend/ops/codi-browser-policy` |
| `active-system/ops/codi-ksu-live-root-renew.service` | `deploy/legacy-backend/ops/codi-ksu-live-root-renew.service` |
| `active-system/ops/codi-ksu-live-root-renew.timer` | `deploy/legacy-backend/ops/codi-ksu-live-root-renew.timer` |
| `active-system/requirement-audit.json` | `migration/legacy-system-guidance/requirement-audit.json` |
| `active-system/requirements.lock` | `migration/legacy-system-guidance/requirements.lock` |
| `active-system/scripts/codi-browser-policy` | `deploy/legacy-operations/codi-browser-policy` |
| `active-system/scripts/fixtures/async-guest-apps.html` | `deploy/legacy-operations/fixtures/async-guest-apps.html` |
| `active-system/scripts/fixtures/guest-worker-proof.html` | `deploy/legacy-operations/fixtures/guest-worker-proof.html` |
| `active-system/scripts/fixtures/official-directory-ui.html` | `deploy/legacy-operations/fixtures/official-directory-ui.html` |
| `active-system/scripts/fixtures/system-autojoin-empty.html` | `deploy/legacy-operations/fixtures/system-autojoin-empty.html` |
| `active-system/scripts/member-contact-cache-browser.html` | `deploy/legacy-operations/member-contact-cache-browser.html` |
| `active-system/scripts/member-contact-victim-check.html` | `deploy/legacy-operations/member-contact-victim-check.html` |
| `active-system/scripts/member-reciprocal-legacy-page.html` | `deploy/legacy-operations/member-reciprocal-legacy-page.html` |
| `active-system/scripts/member-route-browser.html` | `deploy/legacy-operations/member-route-browser.html` |
| `active-system/scripts/member-route-capacity-browser.html` | `deploy/legacy-operations/member-route-capacity-browser.html` |
| `active-system/scripts/member-route-discovery-browser.html` | `deploy/legacy-operations/member-route-discovery-browser.html` |
| `active-system/scripts/member-route-failover-compiled-page.html` | `deploy/legacy-operations/member-route-failover-compiled-page.html` |
| `active-system/scripts/member-route-isolation-compiled-page.html` | `deploy/legacy-operations/member-route-isolation-compiled-page.html` |
| `active-system/scripts/member-route-isolation-old-page.html` | `deploy/legacy-operations/member-route-isolation-old-page.html` |
| `active-system/scripts/member-route-post-sdp-compiled-page.html` | `deploy/legacy-operations/member-route-post-sdp-compiled-page.html` |
| `active-system/scripts/member-route-webrtc-compiled-page.html` | `deploy/legacy-operations/member-route-webrtc-compiled-page.html` |
| `active-system/scripts/member-route-webrtc-legacy-page.html` | `deploy/legacy-operations/member-route-webrtc-legacy-page.html` |
| `active-system/scripts/member-route-webrtc-page.html` | `deploy/legacy-operations/member-route-webrtc-page.html` |
| `active-system/scripts/member-scout-compiled-page.html` | `deploy/legacy-operations/member-scout-compiled-page.html` |
| `active-system/scripts/member-scout-credits-compiled-page.html` | `deploy/legacy-operations/member-scout-credits-compiled-page.html` |
| `active-system/scripts/member-scout-credits-page.html` | `deploy/legacy-operations/member-scout-credits-page.html` |
| `active-system/scripts/member-scout-guard-compiled-page.html` | `deploy/legacy-operations/member-scout-guard-compiled-page.html` |
| `active-system/scripts/member-scout-mobile-size-compiled-page.html` | `deploy/legacy-operations/member-scout-mobile-size-compiled-page.html` |
| `active-system/scripts/member-scout-mobile-size-page.html` | `deploy/legacy-operations/member-scout-mobile-size-page.html` |
| `active-system/scripts/member-scout-revoke-page.html` | `deploy/legacy-operations/member-scout-revoke-page.html` |
| `active-system/scripts/member-scout-routing-compiled-page.html` | `deploy/legacy-operations/member-scout-routing-compiled-page.html` |
| `active-system/scripts/official-delivery-check.html` | `deploy/legacy-operations/official-delivery-check.html` |
| `active-system/scripts/stockfish-browser-fixture.html` | `deploy/legacy-operations/stockfish-browser-fixture.html` |
| `tools/gcode-live-only-controller.py` | `deploy/legacy-operations/tools/gcode-live-only-controller.py` |
| `tools/gcode-post-activation-check.py` | `deploy/legacy-operations/tools/gcode-post-activation-check.py` |
| `tools/run-gcode-live-smoke.py` | `deploy/legacy-operations/tools/run-gcode-live-smoke.py` |
