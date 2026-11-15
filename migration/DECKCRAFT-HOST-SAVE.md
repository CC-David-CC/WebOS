# DeckCraft host-save regression

The selected DeckCraft source `772219838e2807f0d5b0270f8993421499717f58`
passes its standalone browser baseline but fails the new host-save durability
regression. It stays disabled in the minimum desktop.

Run the owned browser test against a source-built browser package:

```sh
node tests/deckcraft_host_save_browser.mjs /path/to/deckcraft/browser /path/to/private/result.json
```

It uses the parent's pinned Puppeteer dependency and Chromium (set
`CHROMIUM_PATH` for another executable). The test creates a fresh browser and a
local same-origin framing page. The fixture deliberately neither stores the
presentation nor sends a saved acknowledgement. It is not an account backend.
All server/browser processes close when the test completes.

## Observed result: FAIL, exit 1

The exact nine-file source-built package from
[the standalone baseline](DECKCRAFT-BROWSER-BASELINE.md) was tested with the old
workspace hidden and networking disabled. The real app was hosted in an iframe,
a text shape was inserted, and its ordinary `file.save` command was invoked.

| Observation | Actual |
|---|---|
| Dirty before Save | `true` |
| Host received generated presentation bytes | 5,240 |
| Save correlation ID | absent |
| Host stored a file | no |
| Host sent a saved acknowledgement | no |
| Dirty immediately after dispatch | **`false` — incorrect** |
| Page errors / external requests | 0 / 0 |

The assertion requires dirty to remain true until durable acknowledgement; it
fails against the selected source. The test also requires a nonempty save ID.
Its failure is retained as a real unqualified boundary. It does not invalidate
the earlier render/insert/undo pass and does not concern the currently enabled
WordCraft account-file path.

## Owning code and next change

`apps/deckcraft/crates/ui-egui/src/app/files.rs::save_to_host` calls its host
callback and immediately invokes `deckcraft_engine::cmd::file::mark_saved`.
`apps/deckcraft/apps/deckcraft-web/src/host.rs` sends `post_save` with no ID and
its listener handles only Open messages. The shared `craft-web-host` crate
already supplies `post_save(..., Some(id), ...)` and `Message::Saved { id }`.

The application needs explicit pending saves with captured document identity,
serialized snapshot and revision, bound to each save ID. Confirmation must
update the originating document's saved snapshot, preserving newer edits and
remaining independent of whichever document is active when the reply arrives.
Unknown, duplicate, closed-document and stale acknowledgements must not mark
another document saved. Failed, cancelled and uncertain outcomes must retain
edits and have visible state. Save As identity changes and close behavior need
separate tests. Use the existing shared positive-ack protocol; place genuinely
new generic transport behavior in craft-libs when needed. Do not add a second
file model to Desktop to conceal premature save completion.

No app implementation, lockfile, component pin, account data, deployment or
original workspace was changed by this regression phase. This test is a known
failing command until the owning source change is implemented and qualified.
