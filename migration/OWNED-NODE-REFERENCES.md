# Owned Node reference tests and frozen vectors

Twelve original test sources and one frozen vector fixture now have source owners established by imports and read targets. Five Storage hashing/capture/chunk tests and two Linux guest-client lifecycle tests live with those components. Browser owns its source-launcher unit and two unported relay units. Desktop owns its historical negative-control source. The parent owns the cross-Desktop/Linux cleanup reference.

| Owner | Original sources | Selected component |
|---|---|---|
| platform/storage | 6 | `b009d24eead61ce461cc4f03aab076b2aab06692` |
| apps/linux | 2 | `66abd8b2f9b8f2224923b490f442a947b9739000` |
| apps/browser | 3 | `09a4d57fde2ae5d4ecf9c4d62a7764994546a994` |
| platform/desktop | 1 | `34a53539ccf99bfa8d66667db8f255aad4a7382d` |
| parent | 1 | `f129ad86b61988644e51d83dde6c75ffd008e919` |

## Original baseline and current qualified scope

The exact captured-source baseline reports26 Node subtests:25 pass and one existing failure. The Desktop negative-control harness omits closeAccountMirror and fails before its intended cancellation assertion. No assertion or supplied stub was changed to make it green. It remains unchanged with a .source suffix, outside the qualified command. This is not evidence of current Desktop cancellation behavior.

The private baseline initially omitted strict-json.mjs, SHA shared.mjs and frozen chunk-sync/v1.json. Those exact tracked inputs were added and hashes recorded; initial missing-fixture outcomes remain in the evidence. They are not labelled product regressions. The frozen vectors are deterministic synthetic hash/chunk data, not account files or user documents.

Eight qualified test files now run against their own repository modules:15 Node subtests pass with no failures/skips/cancellations. Only module-source locators change, and full test AST comparison preserves all assertions except the mapped locators. Each referenced owned module matches the original captured blob. The runnable command is npm run test:owned-reference in Storage, Linux and Browser; existing commands and dependencies remain unchanged.

The two Browser relay tests require old Accounts/Runtime imports from a legacy client, so their unchanged source remains inert until a deliberate public-interface port. No private cross-repository import or copied Accounts/Runtime implementation was added. The cross-Desktop/Linux cleanup source also remains inert in the parent. The one stale Desktop control is not hidden inside an all-green suite.

## Limits and independence

Both baseline and qualified Node runs hide all /home and disable external networking, binding only the exact source fixture or component plus Node. Supplied Worker/popup doubles test actual component logic; no real Worker, browser, v86/Linux guest, backend account storage or agent transport ran. These results do not qualify account synchronization, browser downloads, guest startup, current account-switch UI or application integration.

Mechanical extraction/author history precedes locator-only test port commits. No component implementation or dependency changed; only tests, the original fixture, test commands and qualification notes changed. Four child pins update and120 remain unchanged; all124 independent repositories remain represented. Seven source-assembly checks and clean-clone qualified runs pass. Original source, unrelated WIP/index and deployment remain unchanged.

Private phase56 retains filtered commit/ref maps, original/selected commits, original fixture hashes, baseline outcomes including failures, full assertion-AST proofs, qualified Node results and clean-source provenance. Full suite ownership/integration and real physical second-machine/agent acceptance remain incomplete.
