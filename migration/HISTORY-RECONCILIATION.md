# Selected-history reconciliation

Phase37 audited all122 selected component histories against4,597 pending original-source records. Fifty-four records have matching bytes somewhere in those histories; matches alone do not prove ownership. Nine files now have explicit original-path/rename lineage and exact historical tree witnesses. The remaining45 matches still require role/lineage review, including shared licenses, copied reports, fixture snapshots and an empty output.

No source was copied or rewritten. This resolves an accounting gap for source already retained by its correct component. The original source histories remain privately preserved. All component pins are unchanged.

| Captured original path | Owning component and current path |
|---|---|
| `active-system/network/crypto.mjs` | `platform/accounts/browser/crypto.mjs` |
| `active-system/network/identity.mjs` | `platform/accounts/browser/identity.mjs` |
| `active-system/gateway_service/client.mjs` | `platform/storage/src/webos_storage/client.mjs` |
| `active-system/gateway_service/experimental_admission_client.mjs` | `platform/storage/src/webos_storage/experimental_admission_client.mjs` |
| `active-system/gateway_service/vendor/js-sha256/LICENSE.txt` | `platform/storage/src/webos_storage/vendor/js-sha256/LICENSE.txt` |
| `active-system/gateway_service/vendor/js-sha256/core.mjs` | `platform/storage/src/webos_storage/vendor/js-sha256/core.mjs` |
| `active-system/gateway_service/vendor/js-sha256/shared.mjs` | `platform/storage/src/webos_storage/vendor/js-sha256/shared.mjs` |
| `active-system/gateway_service/vendor/js-sha256/verify-worker.mjs` | `platform/storage/src/webos_storage/vendor/js-sha256/verify-worker.mjs` |
| `tests/app-inventory-loader.test.mjs` | `platform/runtime/tests/app-inventory-loader.test.mjs` |

The original identity crypto/session modules are ancestors of the public Accounts browser modules. The signed file client and verification assets are retained by Storage, with later integration changes explicit in history. The legacy loader test is retained in Runtime history. The experimental admission client remains legacy source; this accounting proof does not enable it or certify its imports/behavior.

Private evidence: `/path/to/workspace/Projects/.webos-migration/run-20261115-37-history-reconciliation/`. `lineage-proof.json` records selected component pins, exact original blob/mode witnesses, ancestor commits and path aliases. `selected-history-candidates.json` retains all remaining candidates without assigning ownership from byte coincidence. No app, browser, agent or deployment acceptance ran in this phase.
