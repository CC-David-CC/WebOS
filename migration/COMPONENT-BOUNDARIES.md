# Legacy component-boundary reference ownership

Four legacy cross-component tests and four shared browser-test helpers now have parent-owned source locations. All bodies/modes and selected histories are unchanged. Mechanical extraction precedes this metadata commit. All124 child component pins and all current implementation/build/deployment entrypoints remain unchanged.

| Original source | Retained parent source |
|---|---|
| `tests/files-local-write-close/component.test.mjs` | `tests/legacy-component-boundaries/files-local-write-close/component.test.mjs` |
| `tests/files-workflow.test.mjs` | `tests/legacy-component-boundaries/files-workflow.test.mjs` |
| `tests/jsketcher-rectangle-commands.test.mjs` | `tests/legacy-component-boundaries/jsketcher-rectangle-commands.test.mjs` |
| `tests/recipe-document-binding/document-token.test.mjs` | `tests/legacy-component-boundaries/recipe-document-binding/document-token.test.mjs` |
| `tests/audio-menu-helper.mjs` | `tests/legacy-desktop-browser/audio-menu-helper.mjs` |
| `tests/browser-choose-root.mjs` | `tests/legacy-desktop-browser/browser-choose-root.mjs` |
| `tests/files-public-beta-assert.cjs` | `tests/legacy-desktop-browser/files-public-beta-assert.cjs` |
| `tests/helpers/desktop-dialogs.mjs` | `tests/legacy-desktop-browser/helpers/desktop-dialogs.mjs` |

## Actual evidence

Three exact captured Node reference tests pass in private snapshots with original source hidden, reporting33 Node subtests and no failures, skips or cancellations. Runtime/ACAD/Files implementations remain owned by their components; private baseline copies are audit fixtures outside Git/web roots, not new application implementations. No current UI/kernel/permission/synchronization compatibility follows.

The fourth Files/Text/mirror reference has unresolved DOM/IndexedDB test dependencies and legacy host contracts, so it is retained unrun. The inspected captured app-builder lock supplies no pin for linkedom/fake-indexeddb. Current authoritative account storage must keep its actual server-backed tests; this reference cannot substitute for them.

Restored0 static helper-import edges used by already-retained legacy browser sources. The helpers still contain legacy selectors/behavior and were not executed against either site. This closes source/helper omissions, not browser acceptance.

## Public-interface port gates

Runtime already exposes commands/documents through its public package. App-specific command registration and recipe interfaces must be deliberately exposed/adapted before current cross-component tests consume them; do not import private implementation paths or copy shared implementation into apps. The old Files view/mirror model is not the new public Files/Text/account-storage contract. No hidden dual host semantics, global privileged bridge or simulated account confirmation should be introduced.

Mechanical baseline `e531f99d2b422ce585e9acc709b7085b274f9cb1`; source merge `e8af5452aae34664c29f7aeef4185411f45c90d1`. Current and earlier paths, copy notes, commit/ref maps, selected-history review, original byte/mode checks and exact baseline logs remain private under `/home/dflanag3/Projects/.webos-migration/run-20261115-45-cross-boundaries/`. Legacy files remain outside supported test commands until reviewed ports are made.
