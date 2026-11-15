# Legacy JavaScript operator and browser-fixture source

79 original JavaScript files now have parent-owned locations under `deploy/legacy-operations/`, beside the previously retained Python operators. They include test pages, worker/host bootstrap fixtures, source-level checks and composition helpers. The small fixture applications are test tooling, not additional supported user apps or reusable product engines.

## Why these were held

The earlier phase39 extraction intentionally selected Python AST-checked sources; these JavaScript files were held for language-specific review. Python parsing is not a valid JavaScript syntax test. The later redacted audit evaluated407 actual Python files plus79 JavaScript files; its79 Python-parser failures are language mismatches, not established JavaScript defects.

All79 current sources now parse with the JavaScript parser and pass Node syntax checks. Selected original histories contain79 distinct source blobs; each also passes the bounded credential/opaque-literal screen and Node syntax check. No assertions, source bodies, modes or dependencies changed. This screen is not complete external-publication clearance; unresolved Python credential/literal cases remain private.

## Reuse gates

No original operator, embedded page, browser driver, worker, host command, SSH action or service operation was executed. No current build/test/deployment entrypoint was changed to consume these files. Their imports, environment, assets, account fixtures, old service globals and side effects need explicit review before any port. Static structure records321 import declarations and37 dynamic imports; this is not dependency closure or a browser build. The files remain legacy source, outside supported default test discovery.

All124 component pins remain unchanged. Exact byte/mode checks and seven source-assembly checks passed from the complete clean clone with the original workspace and primary working tree hidden. This qualifies extraction/assembly only, not application functionality, account persistence, physical second-machine acceptance or agent authority.

Mechanical filtered baseline `f73f8f769bdec3750a51a870ae7b5d3c74777781`; parent source merge `de15cd511d634c1e265431f36f80bbb9ec7be504`. Private phase49 retains path histories, copy/collision review, selected-history syntax results, literal-free audit summaries, commit/ref maps and clean-source proofs.

| Original source | Parent source |
|---|---|
| `active-system/scripts/account-version-scheduler-check.mjs` | `deploy/legacy-operations/account-version-scheduler-check.mjs` |
| `active-system/scripts/compact-replay-page.mjs` | `deploy/legacy-operations/compact-replay-page.mjs` |
| `active-system/scripts/device-credit-transient-retry-check.mjs` | `deploy/legacy-operations/device-credit-transient-retry-check.mjs` |
| `active-system/scripts/device-history-page.mjs` | `deploy/legacy-operations/device-history-page.mjs` |
| `active-system/scripts/fixtures/app-lifecycle-probe.js` | `deploy/legacy-operations/fixtures/app-lifecycle-probe.js` |
| `active-system/scripts/fixtures/browser-files-bootstrap.js` | `deploy/legacy-operations/fixtures/browser-files-bootstrap.js` |
| `active-system/scripts/fixtures/browser-files-page.mjs` | `deploy/legacy-operations/fixtures/browser-files-page.mjs` |
| `active-system/scripts/fixtures/device-archive-page.mjs` | `deploy/legacy-operations/fixtures/device-archive-page.mjs` |
| `active-system/scripts/fixtures/device-archive-race-page.mjs` | `deploy/legacy-operations/fixtures/device-archive-race-page.mjs` |
| `active-system/scripts/fixtures/device-cache-offers-isolation-page.mjs` | `deploy/legacy-operations/fixtures/device-cache-offers-isolation-page.mjs` |
| `active-system/scripts/fixtures/device-cache-offers-page.mjs` | `deploy/legacy-operations/fixtures/device-cache-offers-page.mjs` |
| `active-system/scripts/fixtures/device-history-app/index.mjs` | `deploy/legacy-operations/fixtures/device-history-app/index.mjs` |
| `active-system/scripts/fixtures/device-history-host-bootstrap.js` | `deploy/legacy-operations/fixtures/device-history-host-bootstrap.js` |
| `active-system/scripts/fixtures/device-history-host-page.mjs` | `deploy/legacy-operations/fixtures/device-history-host-page.mjs` |
| `active-system/scripts/fixtures/device-history-network-case.mjs` | `deploy/legacy-operations/fixtures/device-history-network-case.mjs` |
| `active-system/scripts/fixtures/device-index-cache-page.mjs` | `deploy/legacy-operations/fixtures/device-index-cache-page.mjs` |
| `active-system/scripts/fixtures/device-session-bootstrap.js` | `deploy/legacy-operations/fixtures/device-session-bootstrap.js` |
| `active-system/scripts/fixtures/device-session-page.mjs` | `deploy/legacy-operations/fixtures/device-session-page.mjs` |
| `active-system/scripts/fixtures/device-traffic-ledger-page.mjs` | `deploy/legacy-operations/fixtures/device-traffic-ledger-page.mjs` |
| `active-system/scripts/fixtures/guest-worker-network.js` | `deploy/legacy-operations/fixtures/guest-worker-network.js` |
| `active-system/scripts/fixtures/guest-worker-proof.js` | `deploy/legacy-operations/fixtures/guest-worker-proof.js` |
| `active-system/scripts/fixtures/member-notice-concurrency-check.mjs` | `deploy/legacy-operations/fixtures/member-notice-concurrency-check.mjs` |
| `active-system/scripts/fixtures/official-content-browser-parity.mjs` | `deploy/legacy-operations/fixtures/official-content-browser-parity.mjs` |
| `active-system/scripts/fixtures/official-history-fetch-check.mjs` | `deploy/legacy-operations/fixtures/official-history-fetch-check.mjs` |
| `active-system/scripts/fixtures/official-offer-scan-check.mjs` | `deploy/legacy-operations/fixtures/official-offer-scan-check.mjs` |
| `active-system/scripts/fixtures/official-page-installer-check.mjs` | `deploy/legacy-operations/fixtures/official-page-installer-check.mjs` |
| `active-system/scripts/fixtures/official-recovery-vote-page.mjs` | `deploy/legacy-operations/fixtures/official-recovery-vote-page.mjs` |
| `active-system/scripts/fixtures/official-replay-browser-verifier.mjs` | `deploy/legacy-operations/fixtures/official-replay-browser-verifier.mjs` |
| `active-system/scripts/fixtures/recovery-real-archive-page.mjs` | `deploy/legacy-operations/fixtures/recovery-real-archive-page.mjs` |
| `active-system/scripts/gateway-version-client-check.mjs` | `deploy/legacy-operations/gateway-version-client-check.mjs` |
| `active-system/scripts/hosted-agent-host.mjs` | `deploy/legacy-operations/hosted-agent-host.mjs` |
| `active-system/scripts/hosted-agent-loader.mjs` | `deploy/legacy-operations/hosted-agent-loader.mjs` |
| `active-system/scripts/hosted-client-page.mjs` | `deploy/legacy-operations/hosted-client-page.mjs` |
| `active-system/scripts/hosted-recovery-workflow-page.mjs` | `deploy/legacy-operations/hosted-recovery-workflow-page.mjs` |
| `active-system/scripts/hosted-snapshot-page.mjs` | `deploy/legacy-operations/hosted-snapshot-page.mjs` |
| `active-system/scripts/member-contact-cache-browser.mjs` | `deploy/legacy-operations/member-contact-cache-browser.mjs` |
| `active-system/scripts/member-contact-victim-check.mjs` | `deploy/legacy-operations/member-contact-victim-check.mjs` |
| `active-system/scripts/member-inline-boundary-check.mjs` | `deploy/legacy-operations/member-inline-boundary-check.mjs` |
| `active-system/scripts/member-reciprocal-legacy-page.mjs` | `deploy/legacy-operations/member-reciprocal-legacy-page.mjs` |
| `active-system/scripts/member-route-browser.mjs` | `deploy/legacy-operations/member-route-browser.mjs` |
| `active-system/scripts/member-route-capacity-browser.mjs` | `deploy/legacy-operations/member-route-capacity-browser.mjs` |
| `active-system/scripts/member-route-discovery-browser.mjs` | `deploy/legacy-operations/member-route-discovery-browser.mjs` |
| `active-system/scripts/member-route-failover-compiled-page.mjs` | `deploy/legacy-operations/member-route-failover-compiled-page.mjs` |
| `active-system/scripts/member-route-isolation-compiled-page.mjs` | `deploy/legacy-operations/member-route-isolation-compiled-page.mjs` |
| `active-system/scripts/member-route-isolation-old-page.mjs` | `deploy/legacy-operations/member-route-isolation-old-page.mjs` |
| `active-system/scripts/member-route-post-sdp-compiled-page.mjs` | `deploy/legacy-operations/member-route-post-sdp-compiled-page.mjs` |
| `active-system/scripts/member-route-webrtc-compiled-page.mjs` | `deploy/legacy-operations/member-route-webrtc-compiled-page.mjs` |
| `active-system/scripts/member-route-webrtc-legacy-page.mjs` | `deploy/legacy-operations/member-route-webrtc-legacy-page.mjs` |
| `active-system/scripts/member-route-webrtc-page.mjs` | `deploy/legacy-operations/member-route-webrtc-page.mjs` |
| `active-system/scripts/member-scout-compiled-page.mjs` | `deploy/legacy-operations/member-scout-compiled-page.mjs` |
| `active-system/scripts/member-scout-credits-compiled-page.mjs` | `deploy/legacy-operations/member-scout-credits-compiled-page.mjs` |
| `active-system/scripts/member-scout-credits-page.mjs` | `deploy/legacy-operations/member-scout-credits-page.mjs` |
| `active-system/scripts/member-scout-guard-compiled-page.mjs` | `deploy/legacy-operations/member-scout-guard-compiled-page.mjs` |
| `active-system/scripts/member-scout-mobile-size-compiled-page.mjs` | `deploy/legacy-operations/member-scout-mobile-size-compiled-page.mjs` |
| `active-system/scripts/member-scout-mobile-size-page.mjs` | `deploy/legacy-operations/member-scout-mobile-size-page.mjs` |
| `active-system/scripts/member-scout-revoke-page.mjs` | `deploy/legacy-operations/member-scout-revoke-page.mjs` |
| `active-system/scripts/member-scout-routing-compiled-page.mjs` | `deploy/legacy-operations/member-scout-routing-compiled-page.mjs` |
| `active-system/scripts/network-default-check.mjs` | `deploy/legacy-operations/network-default-check.mjs` |
| `active-system/scripts/network-memory-policy-check.mjs` | `deploy/legacy-operations/network-memory-policy-check.mjs` |
| `active-system/scripts/official-author-names-batching-check.mjs` | `deploy/legacy-operations/official-author-names-batching-check.mjs` |
| `active-system/scripts/official-controller-recovery-certificate-check.mjs` | `deploy/legacy-operations/official-controller-recovery-certificate-check.mjs` |
| `active-system/scripts/official-controller-recovery-parity-corpus.mjs` | `deploy/legacy-operations/official-controller-recovery-parity-corpus.mjs` |
| `active-system/scripts/official-controller-recovery-policy-check.mjs` | `deploy/legacy-operations/official-controller-recovery-policy-check.mjs` |
| `active-system/scripts/official-controller-recovery-proposal-check.mjs` | `deploy/legacy-operations/official-controller-recovery-proposal-check.mjs` |
| `active-system/scripts/official-history-yield-check.mjs` | `deploy/legacy-operations/official-history-yield-check.mjs` |
| `active-system/scripts/official-recovery-genesis-check.mjs` | `deploy/legacy-operations/official-recovery-genesis-check.mjs` |
| `active-system/scripts/official-recovery-genesis-parity-corpus.mjs` | `deploy/legacy-operations/official-recovery-genesis-parity-corpus.mjs` |
| `active-system/scripts/operation-index-parallel-candidate-check.mjs` | `deploy/legacy-operations/operation-index-parallel-candidate-check.mjs` |
| `active-system/scripts/operation-node-cache-profile.mjs` | `deploy/legacy-operations/operation-node-cache-profile.mjs` |
| `active-system/scripts/operation-tree-cache-check.mjs` | `deploy/legacy-operations/operation-tree-cache-check.mjs` |
| `active-system/scripts/public-directory-client-check.mjs` | `deploy/legacy-operations/public-directory-client-check.mjs` |
| `active-system/scripts/public-directory-signed-fixture.mjs` | `deploy/legacy-operations/public-directory-signed-fixture.mjs` |
| `active-system/scripts/public-listing-cache-check.mjs` | `deploy/legacy-operations/public-listing-cache-check.mjs` |
| `active-system/scripts/routed-history-unit-check.mjs` | `deploy/legacy-operations/routed-history-unit-check.mjs` |
| `active-system/scripts/server-route-history-fixture.mjs` | `deploy/legacy-operations/server-route-history-fixture.mjs` |
| `active-system/scripts/server-route-live-fixture.mjs` | `deploy/legacy-operations/server-route-live-fixture.mjs` |
| `active-system/scripts/stockfish-browser-fixture.mjs` | `deploy/legacy-operations/stockfish-browser-fixture.mjs` |
| `active-system/scripts/templates/device-cache-worker.js` | `deploy/legacy-operations/templates/device-cache-worker.js` |
| `active-system/scripts/traffic-control-pacing-check.mjs` | `deploy/legacy-operations/traffic-control-pacing-check.mjs` |
