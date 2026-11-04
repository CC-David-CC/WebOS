# Document operation controller

`createDocumentOperationCoordinator()` is created once by the host for the current account/session. Pass it to each window's `createDocumentOperations({coordinator, signal, valid, documentKey})`. Keys are explicit, nonempty, canonical session-scoped strings chosen by the host, or null for an untitled document. Do not expose the coordinator as an untrusted authorization boundary. Windows can edit the same idle file, but active local operations hold claims; unrelated keys do not block. Cross-tab/device changes still require storage version checks.

`begin(kind)` reserves synchronously and returns null if blocked; there is no queue. The receipt has `signal`, `current()`, idempotent `finish()`, `claimDocument(key)`, and `setDocument(key)`. Save As retains its original claim and adds the destination before any target write; `setDocument` changes the window identity on successful commit. Its claims remain until `finish`. For a regular idle identity change, the controller has `setDocument(key)`. `state`/`busy` and `subscribe` expose availability; `bindControl(element,{disabled})` projects it to native disabled or aria-disabled and returns an unsubscribe function. An aria-disabled menu still needs event/keyboard command guards. Listener and disabled predicate exceptions cannot break operation cleanup.

Use `finally { token.finish(); }`. On window disposal abort the passed signal or call `dispose()`; the active token's signal is aborted and claims released. On account/session validity change the host must abort that signal or immediately call `refresh()` on affected controllers: `valid()` is checked synchronously during operations, not polled. No automatic storage wrapping, Save command interception, dirty tracking, operation payload storage, or network-sync waiting is provided. The app must keep its own snapshot revision/expected-version checks and reject stale completions. A failed acquisition must not trigger queued Save. Unknown destination is not a lock until explicitly claimed. Controller state is cooperative, not a cross-tab lock or security boundary.

Run `/tmp/codi-files-move-node/bin/node --test tests/document-operations.test.mjs`. Node controls verify the primitive; they do not qualify any app, browser menu, real storage, or window/session integration.

Folder reservations (`63271e457`) add `token.claimDocumentTree(key)`. The key
must be a namespace plus canonical absolute storage path, for example
`mirror:/Projects`; use `guest:` for temporary Linux. The tree includes its own
key and current/future slash-delimited descendants. Claims conflict in either
direction with other operations' exact or tree claims. Same-owner expansion is
allowed only when no other active claim overlaps; a later exact claim cannot
downgrade an existing tree. Source and destination remain held together until
finish/disposal. No directory enumeration or file bytes are retained. A failed
later acquisition does not roll back earlier claims: the caller must finish
without performing I/O. This does not make multi-file mutations atomic or
physically cancel already-dispatched storage calls.

The lead ran 15/15 primitive tests, including parent/child contention, newly
created descendant windows, sibling and namespace separation, root scope,
canonical-path refusal, exact-to-tree expansion, abort and reentrant disposal.
Text/Calculator real mounted-app tests passed again at 1366 and 390 with this
controller and Text correction `06e696262`; storage remains a test double.
Actual Files directory-action integration is a separate active package.
