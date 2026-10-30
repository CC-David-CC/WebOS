# CodiServer handoff — paused 2026-10-29

## Current direction

The project is a live **test site**, not a finished public service. The user is the only expected human user and has authorized testing and iterative updates on the live site. The current priority supersedes older P2P-first and 8,000-person goals: make registered-account, **server-routed** chat fast and dependable; offer only operator-provided channels; and provide a clean Chess app with an easy Stockfish exhibition. User-created rooms, anonymous chat, P2P optimization, and Pi performance are not current priorities. The longer-term goal remains recorded in the attached objective, but do not claim the deferred parts are finished. Do not replace the `/desktop/` sizing prototype.

## Where things are

- Live connected desktop: https://ksu.codes/; sign-in or registration required.
- Preserved sizing prototype: https://ksu.codes/desktop/.
- Functional source: `active-system/`; standalone Chess app: `served_apps_public/chess/` at the workspace root. Chat source: `active-system/served_apps_public/chat/`.
- Current managed frontend/native release: `/srv/codi-connected/releases/native27-chat-open-error-r1`; manifest SHA-256 `14c3655633cbe74388c1e7382f20768ce75e7cbb99eb22903c8686f3a270d1d0`; managed config SHA-256 `b88ef5dd47031104824f52fa0fafa777b392df845ac2a62987a65b17938f259e`. Managed activation receipt: `/srv/codi-connected/chat-open-error-r1-activation-result.json`. The prior release `native27-chat-selection-r1` is the immediate rollback.
- At pause, root and `/desktop/` returned HTTP 200; issuer, steward, guest, official-chat and featured-chess systemd services were active. The public channel directory contained General chess chat and SYSTEM, with no temporary test channel.
- `HANDOFF.md` in the workspace root has detailed chronological evidence and deployment receipts. Newer entries supersede old live-state statements in AGENTS.md and earlier handoff sections. The managed hosting/controller workflow and its lock/pins still apply; do not hand-edit generated Caddy configuration.

## Working now

- Registration and sign-in are available. Usernames are 3–28 ASCII letters/numbers and cannot begin with a number; passwords are 4–32 characters, including symbols. The user explicitly chose this simple password policy for the prototype. Anonymous visitors cannot use the offered chat.
- General chess chat is server-routed, signed and stored by the official service, with browser copies. SYSTEM is an operator announcement channel and is read-only to visitors. Messages show pending, Sent to the server, and Delivered when another distinct account has confirmed saving them; Delivered does not mean a person read them. Chat remembers the last offered channel used on that browser/account. Its Nerd settings include signed-history export.
- In one live ten-browser test on a single workstation, all ten messages survived an official-service restart, appeared once to every participant, and received distinct-account delivery confirmations. A separate crash/restart test also passed. These are useful test results, not guarantees about all networks or loads.
- In an actual phone/workstation exchange, the user's phone message, server reply and phone confirmation were seen in General chat; the user was instructed to use cellular, though the test did not independently observe phone IP or measure latency.
- Offline queued messages survive a same-profile browser close and subsequent sign-in in the tested scenarios. Ten queued messages were accepted once and in order; a separate two-account test also recovered after the other account posted while the first browser was away. Two channels continued independently when a receiving browser's history requests for one channel were deliberately failed.
- Two lost-server-reply tests passed: after an accepted response was deliberately dropped, the browser recovered the single saved operation; when its history was temporarily unavailable it retried, and the server still had one operation. Receipts: `active-system/.build/checks/live-lost-acceptance-response-r1.txt` and `live-lost-response-retry-r1.txt`. These are fault-injected live tests, not proofs against every crash timing.
- Chess shows a current easy Stockfish-vs-Stockfish game, a spectator board, move replay, previous games, separate shared chat, PGN export and signed record export. A live automated spectator saw a complete 77-ply game, disconnected and recovered; the signed record was independently replayed. Phone-sized emulation has Game/Chat tabs. This is an exhibition; do not imply ordinary users can already start or play arbitrary games.
- Browser-local files are available through Files → This browser and Text save. They remain dependent on browser storage and can be lost when site data is cleared. The application architecture also supports guest Linux and host-backed registered-user features; confirm their current behavior before promising an untested file workflow.
- Unsent Chat/Chess compose drafts share the same account/channel within one tab using sessionStorage. They survive a same-tab refresh and sign-in, but are not a server backup and can be lost on tab closure or browser-data clearing. Queued messages use separate persistent storage. A storage error is reported; newer edits are protected against an older send completing.
- Operator moderation exists for General chat through `/usr/local/sbin/codi-chat-admin`: list, signed spam marks, account bans and unbans. Marked originals remain expandable. Rejected messages require explicit review/resend after unban. See the recent `HANDOFF.md` entries for exact scope and live-test evidence.

## Partial, unverified, or not working

- **Ten participants across independent networks remains unproven.** The phone two-way test and ten-workstation-browser tests passed separately, but not together. The prepared `active-system/scripts/live-temp-phone-nine-check.py` test needs the user's availability before starting its timed temporary channel. User availability was requested but no answer has arrived. Do not tell the user the combined test passed.
- Fresh physical-phone testing is still needed for the current Chess layout, keyboard/touch behavior and general polish. Phone-size browser emulation does not prove physical touch. The user earlier confirmed desktop keyboard/mouse and phone terminal touch worked at earlier versions.
- Real people playing each other, multiple user-started concurrent games, and the broader game ecosystem are future work. The current featured Stockfish game and history do not establish those features.
- User-created channels and anonymous chat are intentionally unavailable under the latest direction. P2P-first routing, independent replicas/supernodes, 32–128-person qualification, global-scale optimization and 8k testing are deferred; don't re-enable them without reconciling current instructions.
- Tests cannot prove behavior across every browser, abrupt power loss during a database commit, or a full server disk. Current small-group timings are individual runs, not service-level guarantees. Longer histories and large groups still need performance and retention qualification.
- Browser-local data depends on browser persistence and user clearing; unsent drafts are only tab-scoped. Do not claim all open application state is automatically saved during maintenance or disconnection.
- Browser JavaScript cannot send raw ICMP through a visitor's own network. Guest Linux Internet uses a host-side relay for authorized signed-in users; any reachability or access-control promises should be checked against current live policy before changes.

## Resume checklist

1. Read this file, the recent end of `HANDOFF.md`, the user-supplied objective and latest user instructions. Inspect live state before relying on old hashes or unit names.
2. If the user is available, prepare the guarded temporary official channel and run the nine-browser plus cellular-phone test. Keep General chat and its existing user messages. Have the user turn Wi-Fi off, sign in and follow the exact unique test-channel instructions; verify receipt in both directions and clean only the exact temporary content. Do not start a timed run while waiting for an answer.
3. Continue with practical chat/Chess UX and reliability based on observed failures, and test actual server behavior. Preserve the separate move and chat channels and honest pending/receipt states. Do not count a single workstation or same-provider Pi as an independent Internet test.
4. Back up relevant source and test scripts to private box-git before live deployments. Current backup remote is `box-git:/srv/data/git/CodiServer-distro.git`, branch `main`; no private keys, account databases or visitor content in the source backup. For `--no-checkout` use an explicit `--branch main` and initialize the index before adding, to avoid deleting unrelated tracked files.
5. Use the managed controller's guarded release/pin/lock workflow; retain the immediate rollback and current `code-history.json` references. Do not delete server releases still named by that history. Recent local generated-release cleanup freed about 1.08 GB; workstation and webhost each had about 77 GiB free at pause.

## Pause

The user explicitly asked to finish current work, write this handoff and pause. Do not automatically resume development or testing until the user asks. The site and its existing services remain running; pause applies to the development goal, not shutting down the site.
