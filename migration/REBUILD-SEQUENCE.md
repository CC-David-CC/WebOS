# Historical functional rebuild sequence

This predates the source-only correction. It records a possible future test order, not the current assignment or authorization to deploy. The replacement-dependent Calculator browser harness mentioned below was removed with the unsolicited viewer. Use START-HERE.md and APP-MATRIX.md for current source ownership and limits.

The user has clarified that ksu.codes is the test location, with test users only.
Build a fresh system there. Historical assets and old-user/data migration are
not prerequisites. Keep the original laptop workspace and recovery material
preserved; stop chasing obsolete services and old generated bundles.

The full independent-repository suite remains accounted for. Bring up and
verify the fresh system in this order:

1. Calculator: mouse/keyboard input; move, resize, minimize, restore and focus;
   two independent instances; close one safely; reopen without duplicate input.
2. Files: correct account workspace; create folder; upload, rename, move,
   download and delete a disposable file; reload persistence; retrieve the
   same account file from a fresh browser environment. Account files use the
   platform Storage interface and server authority, never a second login model.
3. Text: Files → Open → Edit → Save → Close → Reopen for two documents; each
   save updates the intended file; ordinary Save As; unsaved-close handling;
   reload and reopen. Reuse the same storage path planned for WordCraft.
4. WordCraft: heading, paragraph and list; save/close/reopen; open from Files;
   content and formatting survive reload; second browser retrieves the saved
   account document.

Desktop + Files + WordCraft with real server account storage remains the first
useful product milestone. Calculator and Text qualify the foundations first.
Fresh browser contexts are automated evidence; a real second machine is a
separate acceptance check. Tests use disposable test accounts and files.

Calculator's initial real-browser hosting check runs the actual Desktop and
Calculator with a synthetic session, without a backend. This qualifies hosting
only, not sign-in, Files, deployment or the complete assembled product.

Run `node tests/calculator_browser.mjs` with a new owner-only external
`WEBOS_TEST_OUTPUT` directory. Run Calculator's existing arithmetic tests from
its own repository with `npm test`. The old view is retained as source evidence;
the new public entrypoint uses its arithmetic engine directly, without legacy
account-file or monolithic host dependencies.
