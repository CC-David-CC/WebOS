# DeckCraft correlated file adoption

The selected DeckCraft fork completes identified binary opens through its existing
native loading/adoption path. The shared craft-web-host interface advertises
`openResult: true`; an optional open request `id` produces `opened` only after
successful adoption, with actual `documentId`, editor `revision` and
`sourceRetained`. Invalid input returns `failed` with the same request ID.
Legacy unidentified opens retain their existing envelope.

Creation/adoption responses capture stable native identity before list-index or
focus changes. The untouched startup blank is replaced; an edited blank survives.
Native valid named presentations retain their source; unnamed, repaired or
converted input remains a new copy. `file.openBytes` remains source-less.
The host must bind the captured account resource to the matching returned ID,
never to whichever document is active after an asynchronous operation.

## Verification

The preceding selected browser build opened the bytes but failed the exact
regression because it returned no correlated identity. The same test SHA passes
against the new clean release, including back-to-back opens with distinct IDs,
focus changes, converted input and invalid bytes. The screenshot was inspected;
no page errors or external requests occurred. Five existing save, acknowledgement,
reopened-view, failure/unknown and document-target browser regressions also pass.

The app passes all eight required CI stages (2,291 tests, zero failures, five
existing ignored) and a separate complete WebAssembly browser-target check.
The shared library passes formatting, strict Clippy, 3,008 workspace tests
(zero failures, 81 existing ignored), and 12 Node/WASM transport tests.
Five engine and four UI identity regressions were added; the five engine cases
fail against the preceding response implementation and pass with the fix.

```sh
node tests/deckcraft_correlated_open_browser.mjs /path/to/browser /path/to/private/result.json
```

The private browser artifact uses Cargo release plus matching wasm-bindgen and
an explicit HTML bootstrap, without wasm-opt or a Trunk-equivalence claim.
Committed contributor inputs match the generated credits. Source is read-only
and the old workspace is hidden during build and browser execution.

## Remaining work

These are protocol tests with synthetic hosts, not account synchronization.
Native IDs/revisions are not server hashes or authorization grants. Real
Desktop/UserFiles binding, save/export authority, lifecycle integration,
multi-client persistence and authenticated scoped agent operations remain open.
DeckCraft is disabled in the minimum. No deployment changed.
