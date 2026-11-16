# DeckCraft document-target qualification

The parent selects fork `1dc39d6e8c7a3b7ec87d92985c367e2597705fdd`.
Its native control owner checks an explicit `documentId` immediately before
running a queued request. This is an active-document precondition: stale,
malformed or conflicting targets fail. It neither changes focus nor provides
background-document execution or account authorization.

## Reproduced failure and checks

The preceding fork `f0dd04e3ab7bf9a37d31a454d7f8dba5231b509a` ignored an
explicit target. In an isolated browser, a command captured for A ran after
focus moved to B: B gained a shape (2 to 3) and its revision changed (1 to 2).
The browser assertion failed. Three initial native regressions also failed:
stale/malformed targets were accepted and inspection lacked document IDs.
Those failures remain private evidence.

The selected source passes all eight required `cargo xtask ci` stages:
2,282 tests pass, zero fail and five existing cases remain ignored. Four target
regressions cover queued focus changes, malformed/unknown/conflicting targets,
matching and legacy calls, real inspection, and stale saves dispatching no host
bytes. The nested-conflict fixture names another real document; no assertion
was weakened.

A release WASM build from that clean commit passes the real browser regression,
including exact-document editing and inspection. The screenshot was inspected.
The existing no-ack, acknowledgement, reopened-view and explicit failure/unknown
save regressions also pass. Tests run with old source hidden and external
networking disabled. Test hosts store no account file.

```sh
node tests/deckcraft_document_target_browser.mjs /path/to/browser /path/to/private/result.json
```

## Interface and remaining gates

`ui.inspect` advertises `documentTargeting: "active-precondition-v1"`, and returns
the active and per-document IDs/revisions from the real Session/DocState.
A request may put its captured `documentId` in the method parameter object.
Calls omitting it retain current-focus behavior; the future account/authorized
host adapter must always supply its captured target after authorization waits.
Native identities and revisions are not account paths, server hashes or grants.

Real Desktop/UserFiles binding, exports and scoped authenticated agent transport
remain open. Creation/adoption results still need stable identity returned with
the operation, rather than a late active-document lookup. `file.openBytes` is
source-less by design; correct account adoption must preserve source identity
for valid presentations and protect repaired/converted copies. The app remains
disabled in the minimum. No deployment changed in this qualification.
