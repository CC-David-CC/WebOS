# Current root migration progress — 2026-10-24 UTC

The private VM now runs the actual desktop at its HTTPS root, with signed root
revision12. Rollback/death/recovery tests and root terminal/account/document
workflows pass. This supersedes older VM /hidden state below. Production still
uses /hidden/; the public homepage and /desktop/ are unchanged. See
[root migration evidence](active-system/evidence/configurable-mount.md) for pins, failures and remaining hosting/cache/
public acceptance work. The full goal remains ACTIVE.

---

# Latest terminal swipe fix — 2026-10-24 UTC

Live /hidden/ now supports touch swipes over xterm history. Current native/config/
PID pins and public/VM38-check proof supersede the terminal-button release below.
See [terminal swipe evidence](active-system/evidence/terminal-scroll.md). Save work and close all desktop tabs
before reopening to activate a cached update. Root/blog and full networking work
remain active.

---

# Latest terminal update — 2026-10-24 UTC

The live terminal command update supersedes the release/config/PID pins below.
See [terminal-touch evidence](active-system/evidence/terminal-touch.md).
The root/blog and full networking goal remain active.

---

# Active goal — upgrade unfinished (2026-10-24 UTC)

The user corrected the premature goal closure. The active goal includes the
root/blog swap and the other requested changes, including scalable P2P, chunked
checkpoint recovery, light browser PoW and staged8k tests. The verified /hidden/
release below is an intermediate milestone. See ROADMAP.md and the initial
active-system/goal-requirements.json ledger. Keep the current homepage live until
the tested swap; preserve /desktop/ throughout.

---

# Current release — 2026-10-24 UTC

The verified small-group desktop is live at https://ksu.codes/hidden/. The
homepage and sizing prototype /desktop/ are preserved. Read the current
[release behavior, evidence, persistence limits and rollback handoff](active-system/HANDOFF.md).
The larger networking roadmap and future root/blog migration remain separate
unfinished work. Historical snapshots below are retained for their original dates.

---

# Current handoff — development resumed

The user resumed development on 2026-10-22. Read the complete current
[working / incomplete status and resume instructions](active-system/HANDOFF.md).

The public ksu.codes/desktop/ remains the ephemeral sizing prototype: no account
backend, server-side visitor files or host guest-Internet relay. Active development
belongs in active-system; sizing work belongs in desktop-lab. The full long-term
goal is not complete. The chronological history below is retained as history.

---

# Desktop preview handoff

This project is assigned to a future browser-project worker. The distro worker
is returning to CodiServer, Surface hardware and Fleet ISO work. Do not continue
web implementation as part of the distro build task.

## Location and purpose

- Working tree: `/home/dflanag3/CodiServer/desktop-preview`.
- Host-local preview: `http://127.0.0.1:8097/`.
- Server: `python3 desktop-preview/serve.py`, static files, loopback only.
- Plain HTML/CSS/JavaScript, no framework, Node, npm install or FastAPI required.
- Browser prototype and native Surface controller are separate projects.
- The real desktop controller source is `../source-build/desktop/lab/`; it
  controls Xfce directly. This browser project must not apply host/Surface settings.

The previous worker captured the real Xfce menu, assets, wallpaper and a VM
screenshot as reference. `reference.json` and `reference.js` preserve that data.
The interactive app models desktop geometry and window operations. It opens directly into an ephemeral local user and runs one real v86 Linux guest with a shared serial terminal.

## Latest user direction

David remains interested in the browser project for a separate purpose, but
prefers adjusting the real desktop on the Surface directly for ISO UI work.
His browser-native architecture notes are in README.md. Follow that direction:
Workers/WASM, message passing, OPFS, browser capabilities; avoid designing an
entire Unix compatibility layer into the application itself.

He previously selected **v86**, all files local, open source, a real Linux guest,
instead of WebVM's proprietary CheerpX engine. v86 can be an isolated compatibility
component for existing Linux programs, while the browser-native application
uses simpler interfaces. Do not treat the v86 choice as a requirement to make
every application depend on an emulated Unix environment. Clarify changes in
scope if these approaches need reconciliation; don't silently switch back to
WebVM or a CDN/commercial engine.

## Current implementation

- Draggable/resizable windows, roll-up, minimize, maximize, close.
- Grouped tasks, pin/unpin, workspace switching, menus and presets.
- Independent logo, caption and control dimensions.
- Save/load JSON presets by explicit user action; sizing settings are in-memory.
- Baseline compare and the captured Real VM reference remain available.
- Page load creates an in-memory local identity and non-extractable P-256 signing key; header says “Local / not server validated.” No signin page, account backend, or credential storage exists.
- One v86 runtime boots the Debian 6.1.0-54-686 kernel and BusyBox initramfs, including matching VirtIO/9p modules. `/init` mounts a browser-memory home and supervises an unprivileged UID/GID 1000 shell with a controlling serial TTY.
- Terminal windows observe one serial buffer and send keys to one guest. Logout stops it and reloads into a fresh identity/guest.
- Files and Text Editor use the same 9p `/home/guest` as the terminal; import/download, folders, text editing, Trash/restore, Calculator and Help work. Public `session.json` contains only session ID, kind and display name.
- The full Debian root and Python/SQLite/GCC are not included. Guest networking is loopback only. No embedded Chromium app or dummy application launcher remains.

Latest HTML dimensions approved for translation to the distro were 48 px panel,
31 px icons, 17 px panel font, three workspaces of 82 px, 41 px menu rows,
16 px menu text, 44 px caption, 24 px logo, 96 px control width, 24 px symbols,
17.3333 px title text, bold Applications/account labels. New native Surface
experiments can supersede those; don't automatically overwrite them from HTML.
The earlier preset is intentionally named Previous layout choices.

## v86 preparation already performed

Files retained under the ignored workspace directory:
`../downloads/desktop-v86-source/`:

- `v86-0.5.472.tgz`, official npm prebuilt runtime.
- Extracted npm package under `npm/package/`, package version
  `0.5.472+gcc37f35`, contains libv86.js and v86.wasm variants.
- Matching full upstream source archive and extracted tree at commit
  `cc37f35c43bf14865d74ad76879ecf9410f69eb1`.
- v86 upstream: https://github.com/copy/v86 ; BSD-2-Clause engine.
- BIOS files are included in upstream source; its BIOS rebuild script selects
  SeaBIOS rel-1.16.2. Matching SeaBIOS source has not yet been retained separately.
- Local Debian Bookworm signing keyring and the three downloaded public keys.
  Fingerprints were checked against Debian's official archive-key page. This
  keyring is workspace scoped; host APT trust/config was not modified.
- `debian-root/`: successfully built isolated i386 Debian Bookworm minbase using
  mmdebstrap. Packages include linux-image-686, initramfs-tools, BusyBox, Bash,
  Python 3, GCC, libc development headers, Make, nano, sqlite3 and CA certificates.
- `debian-root-initial-missing-key/`: leftover failed initial bootstrap (no keys).
  The subsequent build with the scoped Debian keyring succeeded. This leftover
  can be removed after confirming it has no mounts and is not being used.
- Build recipe begun at `scripts/build-browser-guest.sh`. It refuses an existing
  guest root. Key download/verification steps are NOT yet automated in that recipe.
- Bootstrap success is recorded in ignored `../logs/desktop-browser-guest-build.log`.

**The full Debian guest has not booted under v86.** The current page boots the selected Debian kernel with a small BusyBox initramfs, verified in Firefox. The full Debian root, Bash, Python, GCC and SQLite remain outside this guest. A separate writable 9p home and public session metadata are now connected to the browser apps. The prepared Debian packages remain available in the sibling cache for a later extension.

The chosen v86 source only supports a 32-bit guest, so this is a separate small
browser guest, not the amd64 CodiServer kernel or a replacement ISO pipeline.
No Docker was used. Do not install new host packages without approval.

## Possible later guest work

The current semi-functional desktop is browser-only and preserves its original theme. Further work may add the full prepared Debian root/toolchain, guest Internet networking or deliberate persistence. Keep one guest per session and retain the current working core. The user removed signin from the current scope; do not reintroduce account services without a new request.

The user authorized future hosting on `box-webhost` under `ksu.codes`. Prefer HTTPS/WSS through 443, with 80 for redirects; no further router port forwards are expected. Record any extra port requirement before requesting a router change. No deployment has been done yet.

## Existing checks

`scripts/browser-check.py` tests the geometry prototype through a disposable
Chromium DevTools connection. Twenty-two checks previously passed: menus,
window operations, real pointer/touch interactions, presets, responsiveness,
roll-up geometry and exceptions. Those results cover the existing prototype,
not the unfinished guest or future apps. Adapt tests to the smaller functional
menu without weakening geometry coverage.

The previous disposable browser ran headless inside the allocated QEMU VM,
accessing the host server via `http://10.0.2.2:8097/`. Its debug connection used
an SSH tunnel to host port 9223. Both browser and tunnel were closed after tests;
start fresh and check actual process state before relying on these ports.
The host browser is the user's normal viewer. Don't move the project into a VM
or expose a public server as a substitute.

## Git and boundaries

The enclosing CodiServer repository is local source tracking with a remote on
the R730 data drive. Commit source, patches and instructions; no VM disks, ISO
files, logs, screenshots used as test receipts, or compiled guest/runtime blobs.
Existing captured reference assets are intentional source assets. Coordinate
commits with the distro worker: the repository is shared, so don't stage or
revert unrelated native desktop/ISO changes.

Do not replace CodiServer's existing tested ISO pipeline. Browser work must not
alter SSH keys, LAN firewall, signing keys, published repositories, physical
hardware, the Surface session, or host package configuration.


## Functional desktop update (2026-10-21)

The user asked for a semi-functional 1990s-style desktop and terminal with the existing theme. The default page opens directly into a local ephemeral identity and a real v86 guest. The user explicitly removed embedded Chromium from scope: websites use their normal browser tabs.

Current source: `app.js` owns desktop geometry and the one guest lifecycle; `desktop-apps.js` implements shared home, Files, Text Editor, Trash/restore, Calculator and Help; `terminal.js` implements bounded VT100 screen/scrollback and responses for the real serial stream. The runtime is pinned v86 0.5.472. There is no backend, persistent account store, remote runtime, or host filesystem grant.

`scripts/prepare-v86-assets.sh` verifies the retained local runtime/kernel/library hashes, includes component notices and writes an ignored asset manifest. `scripts/build-browser-initramfs.py` assembles BusyBox, guest libraries, kernel module dependencies, `/init`, and two small 32-bit helpers. `guest-init.sh` loads the included VirtIO/9p modules before mounting the shared home, sets up loopback, and supervises the shell. `guest-drop-privilege.S` starts `setsid cttyhack sh -i` as UID/GID 1000. `guest-ping.S` is a fixed-command setuid helper that invokes only BusyBox ping with an empty environment; the interactive shell stays unprivileged. No sudo, downloads or host package changes were used.

Fresh `scripts/functional-check.py` execution in isolated **host Chromium 155** passed all 13 integration groups. It booted Linux in v86, verified UID 1000, ran real commands and loopback ping, exchanged files between shell and GUI, edited via `vi`, interrupted a process with Ctrl+C, used GUI Save/import/download/Trash/restore, checked Calculator and draft preservation, checked the dark scrolling terminal, dragged/resized windows with real pointer actions, exercised window/workspace/compare controls while preserving one v86 instance, reset identity/key/guest via End session, and blocked a boot asset to verify an honest failure diagnostic. No uncaught JavaScript errors were logged. Receipt, screenshot and logs are in ignored `.build/checks/`. Earlier QEMU/Firefox and the historical 22 geometry checks are separate evidence, not substitutes for this run.

The current guest is still the small BusyBox system, with a writable shared 9p home rather than the full Debian root. No guest Internet adapter/relay, Python, SQLite or GCC is provided. The user authorized a future same-origin HTTPS/WSS deployment under `ksu.codes` on `box-webhost` using ports 443/80; this work did not deploy or change network infrastructure.

## Long-term direction after the desktop slice

Read `ROADMAP.md` before beginning the next stage. David identified the v0.1/v0.2/v0.3 browser and server packages as a long-term progression. Build and verify networking and real login first; proposed games become small menu-based text chats using algebraic move notation / PGN records. Graphical game interfaces come much later. David confirmed that game moves and ordinary chat are separate channels: separate types, ordering and histories; PGN is for moves and chat has its own transcript. They share the one session-owned peer pool. Preserve the working live desktop and guest, and do not treat the reference packages or model results as production-network evidence.

## Network continuation — 2026-10-21

The public signed namespace prerequisite is in `network/namespace.mjs`, covered by
51 browser protocol/directory fixtures. It is not yet connected to live room
menus/subscriptions. See `evidence/M01-directory-prerequisite.md` for authorization
and bounds. Dependency source pins/review are in `evidence/network-candidates.json`
and `evidence/M00-dependency-review.md`; no private mode or steward was enabled.

`serve.py` now uses a public file/module/runtime allowlist and rejects workspace
source, dependency environments and private issuer state. This matters because
both development servers run in the same workspace: disjoint trees on 8098 alone
were insufficient while 8097 served the entire workspace. Both servers now reject
private/source paths. `scripts/public-boundary-check.py` writes a status-only
receipt under `.build/checks/public-boundary.json`; it never reads secret bodies.
The first boundary assertion expected 404 for encoded traversal; the issuer
correctly returned 403. The final checker accepts either refusal status.

The static server was restarted with the restricted handler. Existing visible
Chrome sessions were preserved. Keep public allowlists synchronized when adding a
module to the staged server and static server; never add private `.build` trees.

## Text Rooms integrated

Applications → Rooms now uses `network/public-rooms.mjs` from the existing session
manager. It advertises the public application profile on the same PeerLink,
requires explicit signed invitation acceptance, and separates room chat from move
notation. Creator is White. Legal SAN validation and separate PGN/chat exports are
now implemented; historical PGN imports are read only and cannot send live moves.
`evidence/rooms-ui.md` records bounds, actual two-browser local/issuer-backed tests,
refusal/room switching, guest retention, disposal and failed attempts/fixes.

One replay gate lasts for the whole session across reconnects. Global subscription
replacement is atomic; inactive room views do not acquire extra temporary slots.
Room expiry uses one manager timer and retires admissions. End session clears it.
Original visible browser sessions were preserved; a new tab loads the updated UI.
Static preview remains 8097 and staged issuer desktop 8098, both loopback-only.
Next: broader peer pooling/discovery/routing gates. See `evidence/pgn-and-rules.md`
for rules, PGN limits, dependency provenance, browser tests and outstanding limits.

## Shared pool continuation

The product now constructs PeerLink only inside `network/peer-pool.mjs`. Chat
windows select pooled peers individually; room creation has an explicit peer
selector and accepted room state stores its original link. New connections and
failed/cancelled joins preserve old peers/rooms. Global pending invitation caps
also cover async verification from several links. See `evidence/shared-peer-pool.md`
and the three-browser `scripts/pool-check.py` receipts. A cancellation regression
in native createOffer was fixed with abortable RTC waits; do not remove those guards.
Manager metadata is now 4 MiB; link/room budgets and global caps still apply.
Next: fair scheduling/traffic contention before bounded discovery/routing work.

## Traffic scheduling continuation

`network/traffic-scheduler.mjs` is shared by every PeerLink in the session. It
reserves bytes/jobs before queueing, schedules bounded owner/class deficits and
takes crypto leases only at dispatch. Link sequence numbers are assigned then.
Closing a link cancels queued work and releases metadata after active work settles.
Control has byte/job/native-buffer reserves and bounded token-bucket rates. Typed
room events/controls pass deadlines so stale queued moves do not transmit/commit.
Transient transport remains disabled. See `evidence/traffic-scheduling.md` and
`scripts/traffic-check.py`; do not report simulated bulk packets as product file
transfer or local timing as WAN/QoS proof. Source wire/profile semantics remain
unchanged. All counters are payload accounting, not a measured whole-tab heap cap.

Discovery continuation: `network/bootstrap.mjs` implements only the signed public
seed/steward verification prerequisite; schema and limits are in
`network/MESH-PUBLIC-PROFILE.md`. It performs no I/O and is not yet invoked by the
desktop. Root/endpoint pins must come from a trusted release. Next work is the
bounded authenticated rendezvous service and shared browser support connections.
Protocol runner now accepts `--url` for isolated loopback fixture servers.

Rendezvous state continuation: `steward/leases.py` provides bounded RAM public
scope lease/lookup/intended-route state. It has no listener or authenticator.
`steward/README.md` documents the mandatory transport trust boundary: only verified
Admissions, offers and answers may reach it. `scripts/steward-check.py` passes
31 deterministic state checks; receipt `.build/checks/steward-state.json`. This
is not M04 real-WSS acceptance evidence. Next implement the authenticated loopback
transport and signed records, then integrate with the existing session peer pool.

Authenticated steward transport continuation (2026-10-21): `steward/protocol.py`
and `steward/server.py` now wrap the RAM registry with root-delegated startup,
signed live challenge/authentication, session-key-bound sequenced requests, signed
leases/responses, and intended signed offer/answer forwarding. Socket binding is
127.0.0.1 only; no automatic desktop startup or public deployment. The server uses
pinned websockets 17.1 in `.build/auth-venv`; source/wheel/license provenance is in
`steward/dependencies.json`. No codiauth implementation was changed.

Latest receipts: 31 RAM state tests and 19 real-loopback WS checks pass. The latter
includes an isolated actual Chrome verifying the root seed/service descriptor,
authenticating with its existing identity/key code, and verifying its signed lease.
Native forwarding uses fixture SDP; do not claim browser RTC through rendezvous,
TLS/WSS, WAN, or a completed M04 gate. Tests stop their own servers and delete their
headless Chrome session; the user's visible windows remain open. Next implement
the bounded session-owned browser support client and route real PeerPool signaling
through it. `steward/README.md` documents exact profiles, limits and remaining work.

Browser support continuation (2026-10-21): `network/support-client.mjs` adds a
session-owned, bounded signed steward client. Actual Chrome verifies bootstrap,
authenticates, registers/renews/leaves, and cancels cleanly. The network fixture
now bridges two actual PeerPools and two support clients in one Chrome through
the native steward; both real RTCDataChannels deliver signed chat. Candidate
stats, Chrome version and zero-budget disposal are in steward-network.json.
19 network and 31 state checks pass. This is not desktop/two-Chrome discovery UI
integration yet. Next integrate explicit discovery and invitation controls into
networking.js using its existing session/pool; do not instantiate a feature pool.
See evidence/steward-browser-client.md for limits and missing acceptance scope.

Desktop discovery integration (2026-10-21): networking.js now uses optional
`Discovery` with the current session's existing pool. Chat exposes Join/Sample/
Invite/Accept/Decline/Cancel/Stop; default config remains backend-free with no
socket. Two actual isolated Chrome desktops pass explicit consent, decline/cancel,
live jittered lease renewal, RTC chat, separate room chat and legal e4/e5, unchanged
guests, support-stop survival and zero-budget disposal. Receipts: 20 network checks,
31 state checks, existing manual peer Rooms and all 13 desktop groups PASS.
`evidence/desktop-discovery.md` records scope and limits. `scripts/serve-discovery.py`
provides a RAM-only loopback demo on 8100/8101 (five-minute descriptor; Ctrl-C stops).
No router/public changes. Next: bounded support reconnect/backoff and signed seed/
descriptor refresh; simultaneous-offer handling; TLS/LAN/WAN diagnostics; other
remaining gates. Do not claim all M04 or private/routed messaging complete.

Discovery glare follow-up (2026-10-21): deterministic direction choice now applies
to crossed offers for the verified SID/key pair. Lower SID keeps outgoing; higher
cancels its own pending attempt and still requires explicit acceptance. Different
keys claiming the sampled SID cannot cancel its pending invitation. Pending-link
bookkeeping prunes closed/ready entries before admitting another attempt. The
expanded 20-network-check fixture proves ordinary discovery reconnect, both
incoming-first click orders, forced actual two-offer delivery, one ready RTC link
per Chrome, conflicting-key rejection, legal e4/e5 + separate chat, guest survival,
lease renewal and zero disposal. The pre-fix failed receipt/log are retained as
steward-glare-before.*; 31 state checks also pass. See desktop-discovery evidence.
This supersedes only the discovery-glare TODO; manual-code glare, bounded support
reconnect/seed refresh and all remaining LAN/WAN/routing/private gates remain.

Bounded support recovery (2026-10-21): SupportClient reconnects only classified
transient closes/timeouts, after old socket/crypto/queues/callbacks drain. It retains
BootstrapDirectory floors and current session identity/pool. Discovery uses one
jittered retry worker, at most five attempts over the page lifetime; fatal protocol/
crypto/expiry failures and explicit Stop do not retry. Recovery clears stale hints
and pending signaling but preserves ready RTC rooms. The 21-group network fixture
passes native listener+registry restart with identical keys/connection IDs in two
Chrome desktops, live room chat/Nf3 during outage, bounded retry exhaustion, 1008
and invalid-signature refusal, Stop cancellation, expired signed descriptor blocking
new TCP, and zero disposal. All 31 state checks pass. Details/limits are in
evidence/support-recovery.md. Next: signed provisioning refresh/admission upkeep,
multiple-steward failover, WSS/LAN/WAN and remaining original acceptance gates.
The demo CLI still discards its provisioned keys on process exit; old pages do not
trust a newly generated root automatically. No public deployment has occurred.

Expected-refusal continuation (2026-10-21): valid stale/missing/permission operations
now get explicit signed codi-steward-error/1 rather than losing healthy source
control. It consumes sequence/quota; malformed/signature/replay/quota failures stay
fatal. Browser binds the error to nonce/operation/pending sequence and rejects only
that request. Forward-send ambiguity closes the recipient with 1013 for recovery,
without closing the healthy source. Fixed a cached discovery error hiding its new
recovering status. The expanded 26 network groups and 31 state checks pass, including
actual stale-invitation acceptance beside a healthy two-Chrome RTC peer, refusal
quota, missing/timeout transport faults, and malformed/replayed error-frame rejection.
Current source hashes match receipts; failed UI receipt retained. Contract/scope:
evidence/steward-refusals.md. Seed refresh/admission upkeep and the remaining original
gates are still unfinished; no public deployment or acceptance promotion occurred.

Signed source refresh (2026-10-21): optional discovery.sourcePath selects a bounded,
credential-free, redirect-free same-origin JSON bundle. Refresh discovery and a
jittered automatic job feed the existing pinned BootstrapDirectory; no floor/pin
reset or executable import. Same key/pool/RTC/guest stay; known root revocation
closes only discovery. Reads have 49KiB/5sec/512-fragment limits and abort cleanly.
Native descriptors renew under a lock with increasing revisions inside existing
expiry bounds; the demo now serves /discovery.json and can refresh descriptors
within its ten-minute delegation. Its admission still expires at five minutes.
27 network groups +31 state checks pass: actual seed/descriptor updates, rollback,
bad source variants, no cookies/redirect, automatic refresh, valid late-response
cancellation and concurrent bounded publisher renewal. Demo smoke also passes.
See evidence/bootstrap-refresh.md. Next: proactive admission/identity maintenance,
persistent publisher revision/provisioning and root-policy reload; multiple stewards,
WSS/LAN/WAN and remaining original gates. No public deployment occurred.

Admission maintenance (2026-10-21): explicit signed RENEW_ADMISSION updates only a
still-valid identity/admission deadline, with same key/session/account/scope and
unchanged membership expiry. Nonce, request quota/sequence, leases and routes stay.
Browser maintenance is jittered, one job, no recovery/rekey; it uses the current
issuer certificate and rejects excessive/counter/profile errors. Native signals
accept valid old/new certificates of the same identity/key, never expired ones.
The two-Chrome suite uses 12-second admissions and proves continued readiness past
original deadlines on the same nonce/owner/RTC/guest. Fixture-issuer native tests
prove certificate bounds/refresh and reject identity transfer/downgrade/replay.
28 network groups +37 state checks pass; failed advertised-deadline receipt retained.
Demo default-300s smoke also passes and was stopped. See admission-maintenance
 evidence. Next: persistent publisher/root-policy provisioning, peer certificate/
room-membership upkeep, multi-steward/WSS/LAN/WAN and remaining original gates.
No public deployment or account API rewrite occurred.

Durable publisher continuation (2026-10-21): optional PublisherState private SQLite
ledger binds provisioning, persists seed/revision floors and exact signed bytes,
commits before publication, and freezes signed equal-revision seed forks. Missing/
corrupt/unsafe state never resets. Provisioned loopback CLI: scripts/serve-steward.py
(init-state then serve with explicit private key/provision and separate public bundle
output). It generates no keys/accounts, configures no public services and preserves
RAM-only lease behavior. 24 persistence tests pass, including actual child crashes,
hot-journal recovery, concurrent processes and real daemon SIGKILL/restart. The 28
network groups now use this ledger and prove two-Chrome descriptor-2 acceptance,
reopened-state restart without fork/rollback, RTC/guest/identity continuity and all
current maintenance/refusal checks; 37 state cases pass. Details/limits:
evidence/persistent-publisher.md. Next: root-policy provisioning/reload and migration,
peer certificate/room upkeep, multi-steward/WSS/LAN/WAN and remaining original gates.
No disk-snapshot anti-rollback, distributed HA or public deployment is claimed.

### Signed root-policy reload (2026-10-21)

The provisioned daemon now verifies and applies newer signed seed policy while
running. Scope/capacity/expiry changes replace RAM admissions, preserve durable
floors and global rate limits, and publish the new bundle before closing old
controls. Reconnecting browsers verify the source before reauthenticating; removed
scopes stop while existing RTC links survive. Seven focused policy groups pass,
including actual Chrome traffic. See evidence/root-policy-reload.md for daemon
watch verification, receipt scope and failure behavior. Peer/room upkeep, policy
migration, multiple stewards and WSS/LAN/WAN remain unfinished; no gate promotion
or public deployment is claimed.

### Peer certificate upkeep (2026-10-21)

Signed handshake negotiation now enables same-key/account/session certificate
updates over existing RTC links. Current proofs are separate from the original
signed signaling transcript; new room invitations use them. Automatic upkeep
preserves link identity and replay sequence, rejects expired/non-advancing or
transferred authority, and uses existing shared control budgets. Local equal-expiry
issuer refreshes send no redundant update. Older peers retain original expiry.
See evidence/peer-identity-maintenance.md for focused actual Chrome evidence and
regression results. Room membership/descriptor/origin admission renewal and all
remaining distributed/public deployment gates still require work.

### Two-peer room upkeep (2026-10-21)

The current desktop opts into signed codi-room-renew/1 through its shared pool.
Controller-only chained descriptors and four same-stream grants extend live room
authority after a matched peer ack. Existing sends quiesce before the ack; replay
floors, local counters, chat history, legal moves and PGN persist. Identity and
policy changes, expired revival and scope/stream replacement are rejected. Signed
forks and ambiguous acknowledgments close the room while direct RTC remains
usable. Default 300-second grants renew automatically within original certificate
bounds. See evidence/room-renewal.md for current real-browser/adversarial evidence
and limits. Distributed membership/routing, private crypto, multisteward failover
and public WSS/LAN/WAN deployment gates remain unfinished.

### Release-pinned steward failover (2026-10-21)

SupportClient now accepts a bounded descriptor set and a version 2 same-origin
bundle while retaining existing single-service configuration. One active socket
and the same revision-floor directory survive retryable handoffs; selection avoids
recently failed keys and prefers different declared domains among ties. Product
lease requirements, issuer policy and release endpoints remain pinned. Fresh
nonces/leases replace stale hints/routes without replaying unknown signaling, and
ready RTC links survive. Separate native process SIGKILL, new RTC establishment
through the alternate, root retirement/rollback, learned root-only revocation and
fatal protocol rejection are exercised in evidence/steward-failover.md. This is
standby failover on one host, not replicated/sharded discovery or distributed HA.
Routed/private networking and public WSS/LAN/WAN gates remain unfinished.

### Private guest Internet proof (2026-10-21)

The optional `guest-relay/server.py` serves a same-origin v86 VirtIO Ethernet
WebSocket backed by one QEMU/libslirp process per guest. Real Chrome/v86 ping to
1.1.1.1, DNS and HTTP page content verification passed through box-webhost's home
connection. Default serve.py remains static/loopback-only for guest networking.
This is a private SSH-tunneled prototype, not a public ksu.codes deployment.
See evidence/guest-internet.md for operational changes, evidence and remaining work.

Private relay follow-up: tightened packet policy rejects multicast, IP options,
fragment/reserved flags, malformed TCP/UDP/ICMP and non-gateway ARP. Forty-five
focused checks pass, including actual four-QEMU capacity and disconnect cleanup.
The new filter also passes actual Chrome/v86 Internet checks. A separate visible
Internet-enabled Chrome session is recorded in .build/checks/guest-internet-visible.json;
previous visible sessions were not changed. The tunnel remains a development process.

Relay follow-up: 64 focused checks now cover exact traffic/lifetime boundaries,
actual handler expiry/flood/text/oversized cleanup, and separate QEMU-wire ARP
exchange isolation. Updated source also passes real guest Internet through a
temporary 8113/8121 tunnel, stopped afterward. Existing visible 8110 session is
preserved on the prior verified process; do not claim it runs the latest budget
refactor until a deliberate restart. See evidence/guest-internet.md.

### Four-room/eight-context concurrency (2026-10-21)

The new scripts/multiroom-check.py passes with eight independent real Chromium
sessions, four accepted two-peer rooms and eight authenticated RTC links forming
a connected cycle. Eight expected remote chat markers arrive exactly once with
zero unintended-room deliveries; four separate e4/e5 games and all guest/session
identities survive redraw. Every tracked network budget clears on disposal.
See evidence/four-room-browser.md for recipient accounting, source hashes and the
initial corrected harness failure. This strengthens concurrency evidence only;
multi-party/routed groups, forwarding/repair, WAN and public gates remain open.

Guest welcome now reflects relay-enabled vs static setup, including home-egress
ownership and working BusyBox timeout/wget syntax. Fresh Chrome boots verify both
variants. Relay config now pins the module-load source revision, and Internet
checks reject a runtime/source mismatch. Latest source passes 65 focused checks
and actual ping/DNS/HTTP plus welcome verification on temporary 8113/8121. That
service was stopped; visible 8110 was neither restarted nor refreshed.

### Isolated issuer and certified concurrency (2026-10-21)

Connected previews now isolate public/state directories by explicit instance label
or alternate port, preserving legacy 8098 paths. Fresh 8115 issuer tests pass
actual login, bad-password, stable-account/fresh-key, renewal, logout and private
path checks. The complete eight-context/four-room connected-cycle run also passes
with all eight identities development-server certified, 8/8 remote chat deliveries
and zero unintended-room deliveries. See evidence/connected-instance-isolation.md
and evidence/four-room-browser.md. Temporary test service stopped; no default
signin/backend change, official authority or public/WAN/routed-group gate claim.

### Room chat reordering (2026-10-21)

Fixed a verified-event loss: PublicRooms no longer discards chat simply because
the replay gate reports a sequence gap. Bounded verified reordering delivers once
in arrival order, with a persistent warning in the room view/export. Chess gaps
still freeze the legal prefix. All 123 protocol fixtures and actual two-browser
chat/PGN/guest regression pass; see evidence/room-chat-reordering.md. No repair,
forwarding, multi-party or WAN gate is promoted by this change.

### Inactive history disclosure (2026-10-21)

Valid messages discarded while no view is open now mark that bookmark's history
as incomplete without allocating a hot history/subscription. Direct and room chat
views disclose it; public-room exports combine inactive, eviction and sequence-gap
warnings. Invalid records cannot mark history. All 125 protocol fixtures and the
actual RTC close-view/send/reopen regression pass. See evidence/inactive-history.md.
This reports missing content honestly; repair/routing/private/WAN gates remain open.

### Pending crossed-offer convergence (2026-10-21)

The shared pool now picks one pending path deterministically by signed session
order after confirming full identity binding. Existing established entries retain
priority. Actual two-browser crossed offers pass in both answer orders, exchange
messages on one matching RTC connection, reject a later duplicate and release all
tracked reservations. The three-browser pool/room regression and 125 protocol
cases also pass. See evidence/pending-offer-convergence.md for the reproduced
zero-ready-link failure and scope: this is pool API evidence, not simultaneous
manual UI, issuer-backed glare, partition recovery, WAN or routed-group proof.

### Issuer-backed crossed offers (2026-10-21)

The glare fixture now uses target runtime identity configuration and asserts
actual local/remote trust modes. Forward and reverse crossed-offer tests pass
through an isolated real development issuer, including matching RTC path,
bidirectional delivery, established duplicate preservation and complete cleanup.
A mismatched trust-mode expectation correctly fails without local substitution.
Receipts and limitations: evidence/pending-offer-convergence.md. No manual-UI,
official/public, routing or WAN claim is added.

### Same-origin HTTPS/WSS proof (2026-10-21)

Disposable discovery accepts explicit external origin/endpoint while keeping
backends loopback-only. A local Caddy 2.11.4 TLS terminator and two actual Chrome
sessions pass WSS discovery/consent, bidirectional RTC, RTC survival after support
stop, foreign-Origin 403, private-path 404 and complete cleanup. Explicit test
certificate trust is confined to the check; no system CA/live hosting/router
change. See evidence/tls-discovery.md and tls-discovery-result.json. Temporary
services stopped. This adds local TLS evidence, not public PKI/WAN/official issuer
or routed-group proof.

### HTTPS issuer proof (2026-10-21)

Connected previews now accept a validated external origin while the issuer backend
remains loopback-only. Actual Chromium through local Caddy HTTPS passes login,
wrong password, stable-account/fresh-session, certificate upkeep, logout, v86 boot
and private-path checks. Wrong Host/Origin receive 403; an initial empty-200
unknown-host proxy response prompted an explicit fallback 403 template. Receipt
source/proxy hashes and limits: evidence/tls-identity.md. No global trust or live
hosting change; temporary services stopped. Public/official/WAN/routed/private
and combined issuer/WSS gates remain open.

### Combined certified HTTPS/WSS preview (2026-10-21)

New serve-connected-discovery.py stages one isolated development issuer and an
independently scoped RAM steward behind the same Caddy HTTPS origin. Actual
issuer-certified Chrome sessions pass WSS discovery/consent, bidirectional RTC,
separate room chat and legal e4/e5/Nf3 (last after support stop), guest continuity
and complete cleanup. The same backend passes login/renewal/logout/Host/Origin
checks. See evidence/combined-tls-preview.md and combined-tls-result.json. Only
loopback test processes were started and stopped; no public/official/WAN/routing
or production-isolation gate is promoted.

### Combined delegation-expiry isolation (2026-10-21)

A fresh 45-second signed delegation expires in an actual two-browser HTTPS/WSS
run. At expiry+32 seconds (after a later publication tick), discovery is closed
and its connections are released, while issuer config and same-key/session
renewals remain available. Established RTC chat and legal Nf3 still arrive, guest
objects survive, and final disposal clears budgets. See
evidence/combined-delegation-expiry.md and combined-tls-expiry-result.json. This
is bounded local expiry evidence, not process-crash/soak/public/WAN/routing proof.

### Separate issuer/steward processes (2026-10-21)

Combined preview now launches the existing native provisioned steward CLI with
private key/provision/ledger state and atomic public bundle publication. Issuer
and steward have separate processes, still one development UID and loopback-only
backends. A verified steward SIGKILL leaves issuer renewal, identical RTC links,
chat/legal Nf3 and guests working; all budgets release afterward. Normal parent
SIGTERM reaps a live child. See evidence/combined-process-isolation.md. No
automatic restart/privilege separation/public/WAN/routing claim; rerun earlier
expiry proof on this new composition before treating its scope as current.

### Bounded steward supervision and live WSS recovery (2026-10-21)

The development supervisor allows three native worker restart attempts with
1/2/4-second backoff and the same private provision/key/publisher state. Actual
certified Chrome sessions recover WSS discovery and fresh sampling after a verified
SIGKILL, preserve service/RTC/session identity, deliver chat/legal Nf3 and clear
budgets. Further native kills prove lifetime exhaustion at three while the issuer
remains available. Normal shutdown cancels supervision and leaves no worker.
See evidence/combined-worker-supervision.md. Expiry/backoff, production privilege
isolation, public/WAN/routing/private gates remain unproven or unfinished.

### Expiry/backoff restart race (2026-10-21)

Actual native fault injection reproduced a replacement-worker launch after a
signed grant expired during backoff (native validation still refused authority).
The supervisor now rechecks expiry after sleeping. The same boundary test proves
no replacement PID and continued issuer availability; current-source certified
HTTPS/WSS browser recovery also passes. See evidence/steward-expiry-backoff.md.
Read-only hosting preflight confirms a clean ksu.codes source working tree and
existing routes to preserve; no deployment/config change was made. Public artifact,
CSP/path validation and managed release work remain before hosting integration.

### Public-only static artifact and /desktop/ CSP proof (2026-10-21)

New export-desktop.py packages the explicit public allowlists and runtime notices,
verifies input/copied runtime hashes, refuses existing destinations, and writes an
exact release manifest. The 133-file/12.8 MB artifact reproduces byte-identical
manifest hashes; corrupted-copy refusal is tested. Actual guest/desktop and
two-browser RTC/room/PGN checks pass under /desktop/ with a scoped CSP; private,
traversal, listing and outside-prefix requests are rejected. See
evidence/public-desktop-artifact.md and desktop-artifact-result.json. Existing
ksu.codes app/CSP were read only; no public deployment or default-backend change.
Connected/official/public/WAN/routing/private gates remain unfinished.

### ksu.codes route/CSP candidate (2026-10-21)

An isolated history-preserving clone/desktop-preview branch now contains the exact
public artifact, one /desktop mount and README notes. A separate parent-generator
patch adds only the desktop CSP; all other eight-site rendered output is unchanged
and the full candidate adapts successfully. Actual site/FastAPI+Caddy guest, desktop
and two-browser RTC/PGN checks pass. Existing homepage/guides/presentation bytes
match both Git and the live release's public-file hashes. No staging/commit/push,
remote source edit or deployment occurred. See evidence/ksu-desktop-candidate.md
and site-candidate-result.json. Managed release/public/WAN/routing gates remain.

### Live static ksu.codes/desktop preview (2026-10-21)

The reviewed site candidate is now committed/pushed/pulled as d6ccfc4 and deployed
via the normal controller to release 20261021T125622370238Z-279f978f. Scoped CSP
source was hash-guarded/backed up, generated, validated and reloaded under the
controller lock. Live HTTPS Chrome passes all 13 desktop/guest groups and actual
two-browser RTC/room/PGN checks; all 133 file hashes and existing content/policies
verify. All eight production smoke sites pass. A new visible public guest is ready.
See evidence/ksu-desktop-deployment.md and ksu-desktop-deployment-result.json.
This is local/unvalidated identity and guest-loopback static hosting, with no new
router ports or public issuer/relay. External fetch did not prove outside-LAN
reachability; WAN/TURN, connected official identity, routing/private/repair and
other original gates remain open. The full goal is not complete.

### Origin account-disable adapter (2026-10-21)

New origin_service.lifecycle preserves the reference issuer API while adding
private disabled/generation state, checks on registered issuance/renewal, and
re-enable without old-token revival. A local owned-state operator CLI adds no web
admin/signin route. All 42 reference regressions plus nine lifecycle cases pass;
actual Chrome/operator/API disable-enable and ordinary identity regression pass.
See evidence/origin-account-lifecycle.md. New connected preview launches use the
adapter; older processes and the public static site remain unchanged. Detached
certificates retain their original validity; full lifecycle/public S04 remains open.

### Fail-closed origin policy state (2026-10-21)

Fixed a reproduced generation-zero revival on missing policy rows. Registered
issuance now checks account existence, explicit policy and renewal generation;
new-account policy rows are atomic. Startup metadata/trigger checks reject broken
hardened state. Populated legacy state needs explicit owned-state migration that
preserves disabled flags/generations. All 60 native cases and actual lifecycle/
identity browser regressions pass. See evidence/origin-policy-state-integrity.md.
Public preview unchanged; detached expiry, full rollback/rotation/recovery/load/
independent review and public issuer gates remain open.

### Origin database backpressure (2026-10-21)

Reproduced the inherited ten-second account write wait/generic 500. Adapter account
transactions now use a two-second SQLite bound and BUSY/LOCKED -> 429, preserving
reference validation/Argon2/slot/throttle/registration behavior. All 62 native cases,
actual Chrome contention/lifecycle and ordinary identity regression pass; measured
lock refusal is ~2 seconds and login recovers after unlock. Native parallel calls
verify excess-slot refusal and independent anonymous entry in the reserved-lock
case. See evidence/origin-database-backpressure.md. Public site unchanged; full
HTTP load/timeouts, production entry/review and remaining S04 gates remain open.

### Stored Argon2 profile bounds (2026-10-21)

Added bounded canonical Argon2id-v19 envelope/metadata checks before verifier
work, using the existing maintained parser/provider. Unsupported/excessive stored
parameters fail closed; supported weaker hashes still verify and rehash normally.
All 65 native cases (including reference regressions and safe verifier-spy cases)
and actual browser lifecycle/contention/identity checks pass. See
evidence/origin-stored-hash-profile.md. No high-memory unsafe hashes were executed,
public site/accounts unchanged, and broader resource/S04/WAN/routing gates remain.

### Local operator password reset (2026-10-21)

Added atomic password replacement plus session-generation revocation, preserving
account identity and disabled status. Secrets enter via prompt/stdin. Fixed a
reproduced in-flight login race by carrying the generation captured during
password authentication into initial issuance. All 71 native cases and actual
Chrome reset/ordinary identity regressions pass. See
evidence/origin-password-reset.md. Public accounts remain off; detached certificate
expiry and the remaining production/S04/network gates remain open.

### Bounded development issuer HTTP (2026-10-21)

Connected preview now has eight request workers, bounded admission and five-second
socket I/O timeouts. Actual socket checks prove concurrent progress, saturation
503, idle-header timeout and recovery. All 71 native cases plus ordinary and
lifecycle/contention Chrome regressions pass. See evidence/origin-bounded-http.md.
This is not a production transport approval; proxy/total-deadline/load/review and
combined discovery integration remain open. Public static site unchanged.

### Combined bounded transport integration (2026-10-21)

Fixed the combined supervisor's independent single-threaded HTTP construction.
Actual two-Chrome HTTPS/WSS + issuer + separate chat/chess + steward SIGKILL/
restart checks pass with guest/session preservation. Combined eight-worker
saturation/refusal/recovery also passes. Repaired TLS fixture config generation
and validated fresh generated configs. See evidence/origin-bounded-combined.md.
Loopback host candidates only; remaining production/WAN/routing gates stay open.

### Development HTTP framing (2026-10-21)

Reproduced duplicate Host acceptance and added pre-WSGI rejection of ambiguous
headers/unsupported framing in the shared handler. Nine malformed socket cases
and existing admission checks pass. Actual HTTPS identity and two-Chrome WSS/RTC
chat/chess/v86 regressions pass. See evidence/origin-http-framing.md for receipts
and the retained missing-fixture-CA test invocation failure. Public deployment and
remaining production/WAN/routing gates unchanged.

### Explicit ICE relay policy (2026-10-21)

PeerLink now honors configured all/relay policy and rejects invalid values before
opening RTC. Actual Chrome verifies relay/no-TURN exposes no direct candidates;
full protocol and two-browser chat/chess/PGN regressions pass on a fresh current
server. See evidence/ice-transport-policy.md, including retained stale-server
fixture failures. No TURN deployment or WAN connectivity is claimed.

### Actual forced TURN/TCP peer delivery (2026-10-21)

Added a disposable authenticated loopback Coturn fixture and --expect-relay browser
oracle. Actual unauthenticated Allocate gets 401; two Chrome sessions select
relay/relay and pass signed chat, separate chess/chat, legal PGN and lifecycle
checks. Package extracted project-locally, no system service or router change;
fixture stops and removes credentials. See evidence/turn-loopback.md. This is
one-host TURN/TCP evidence, not TURN/TLS or WAN proof.

### Actual TURN/TLS peer delivery (2026-10-21)

Extended the local authenticated Coturn fixture to TLS. Actual Chrome selects
relay/relay with localRelayProtocol=tls and passes separate chat/chess/PGN and
lifecycle checks. Normal TLS trust rejects the self-signed fixture; explicit
fixture CA/SPKI is confined to tests. Plain TCP regression also passes. Fixtures
stop and remove credential configs. See evidence/turn-tls-loopback.md. Public
443 routing/certificates/auth/abuse policy and WAN proof remain open.

### Separate lab and active system (2026-10-21)

User requested two independent directories. desktop-lab contains static frontend/
local-v86 assets, local identity helpers and a static server. It retains proportion
controls; Chat/Rooms and backend service code are excluded. active-system is the
functional target with full-viewport desktop, guest Internet relay, shared peer
networking and optional issuer/steward source. Its app/index have no proportion
controller, presets, comparison controls or preview scaling. Windows now clamp
to the real viewport, including browser resizing.

Root sources remain the preserved pre-split baseline. Future functional work
belongs in active-system; sizing experiments belong in desktop-lab. Both have
README launch instructions and copied runtime. Active has its own .venv and
requirements lock; no old accounts, signing keys or service state were copied.
Run lab at 127.0.0.1:8131 and active at 127.0.0.1:8130. Public hosting unchanged.
Local runtime ping_group_range 1000..1000 permits relay ICMP, not persisted.

All 13 lab browser/guest checks pass. Active actual guest ping 1.1.1.1 (2/2), DNS
and HTTP pass. A first active room native-click case exposed offscreen controls;
fitWindow fixes this and the actual two-browser chat/chess/PGN regression passes.
The failed pre-fix log is retained in active-system/.build/checks. Additional
responsive/interface checks prove both guests boot and controller separation:
.build/checks/split-desktop-result.json. Product-specific receipts are stored in
each directory's .build/checks. Both local previews are left running for review.

### Active system: combined identity/discovery/guest Internet (2026-10-21)

Changes confined to active-system. Optional public-config composition connects
separate loopback issuer and guest relay behind one HTTPS origin. Actual Chrome
identity, two-browser WSS/RTC chat/chess, and issuer-backed v86 ping/DNS/HTTP all
pass. Nine real HTTP config failure/fragmentation cases and relay regression pass.
Default lab/active previews are preserved; temporary combined fixture is stopped.
See active-system/evidence/combined-identity-internet.md. Production/WAN/multiparty
and independent-review requirements remain open.

### Active system shared TLS listener (2026-10-21)

Fixed absent-SNI routing in the interrupted shared-port fixture. Actual active-
desktop Chrome sessions load HTTPS and use TURN/TLS through one loopback TCP
18443 listener; selected relay/relay and tls protocol plus chat/chess/PGN pass.
Unknown SNI is rejected; standalone TLS relay regression also passes. Project-local
fixtures stop and remove credentials. See active-system/evidence/shared-tls-port.md.
Public 443, trust, WAN, relay policy and multiparty admission/routing remain open.

### Active system expiring TURN credential foundation (2026-10-21)

Implemented Coturn's documented REST credential profile using standard-library
HMAC, native secret bounds, capped lifetime and authorization deadline. Actual
Chrome/Coturn rejects expired/altered credentials then passes fresh relay/relay
TLS chat/chess/PGN through shared listener. Six native bounds cases pass. This is
fixture interoperability, not public authorized issuance or instant allocation
revocation. See active-system/evidence/turn-expiring-credentials.md. Remaining
production/WAN/multiparty requirements stay open.

### Active-system authenticated session TURN policy (2026-10-21)

Optional native TurnPolicy now supplies temporary credentials only in successful
session/renewal replies, never public config. Client validates endpoints/expiry,
refuses missing/expired credentials and renews before TURN expiry. Actual issuer+
Coturn+shared-TLS Chrome chat/chess/PGN and renewal continuity pass; all 76 native
issuer cases and complete browser protocol suite pass. Default launchers/public
sign-in remain unchanged. See active-system/evidence/session-turn-issuance.md.
Production secret/abuse/deployment/WAN/multiparty gates remain open.

### Active-system private TURN launcher configuration (2026-10-21)

Added explicit paired secret-file/TURN-URL options to both development launchers.
Loader rejects unsafe permissions, public-tree placement, symlinks/hardlinks,
special files and invalid/big token content before staging/startup. Nineteen
native checks and actual signed HTTP issuance against both subprocess launchers
pass; workers reap and TURN secret fixture is removed. See
active-system/evidence/turn-private-file-launchers.md. User's public-prototype
boundary is recorded in AGENTS.md: no active backend or host ping at /desktop/.
No live-site changes; remaining public/WAN/multiparty requirements stay open.

## External preview path update — 2026-10-22

The next version's external preview belongs at https://ksu.codes/hidden/ if needed.
Keep https://ksu.codes/desktop/ live and unchanged until the upgrade is ready.
This records the staging destination only; no deployment or goal resumption.

### Full local stack verified — 2026-10-22

Active-system now passes an actual combined issuer/discovery/TURN-TLS/guest-
Internet/support-recovery run in the same two Chrome sessions. See
active-system/evidence/full-system-local.md. User authorizes /hidden/ external
preview tests while /desktop/ stays unchanged. Next is tested mount-prefix support
before any connected /hidden/ deployment. Production/WAN/multiparty gates remain.

### Configurable hidden/root mount verified — 2026-10-22

Active-system now supports --base-path /hidden with root as the default. Full
external proof-path binding is retained; client renew/logout, scoped steward
endpoint, metadata refresh and guest relay/cookie paths match the mount. Both
complete local stacks, including browser identity regression, pass. All 81 native
and 143 protocol cases plus guest/steward regressions pass. See
active-system/evidence/configurable-mount.md for retained failures and receipts.
User confirms final site is domain-root; /hidden/ is temporary external testing,
and /desktop/ stays live. Next: isolated managed external preview deployment and
outside-network evidence. No live-site changes yet; full goal remains active.

### Private runtime and immutable connected release — 2026-10-22

Active-system native launchers now accept a locked, owned --runtime-dir outside
the release. Account/key persistence, RAM-session invalidation, concurrent
launcher refusal, private HTTP boundaries and graceful cleanup are exercised
with a genuinely read-only filesystem. The connected exporter packages 156
allowlisted frontend/runtime/native files, notices and checksums, excluding
private state, venv and development tools. The actual exported artifact is
tested through the complete local browser stack. Details and retained failures:
active-system/evidence/immutable-connected-release.md. Public prototype release,
app and config hashes remain unchanged; no remote deploy or ingress change.
Next external preview work needs managed runtime ownership/supervision and
scoped proxy/rollback, plus explicit discovery lifetime, TURN and guest egress
decisions before exposure. Full goal remains active; /desktop/ stays live.

### Stable provisioned discovery and explicit root renewal — 2026-10-22

Active-system adds an operator-only init/renew/export workflow and an opt-in
provisioned connected launcher. The issuer/root/realm/scoped service key and
publisher ledger survive restart. Only explicit operator commands sign renewed
root policy. Real elapsed expiry stops/reaps the worker while issuer sessions
remain usable; explicit renewal restores the same worker authority/session.
Two real browsers accept live policy revision 2 while retaining VM, identity,
RTC connection and separate chat/chess, alongside real guest Internet.

Current immutable-artifact testing protects operator commands as well as online
services and verifies the entire release again after execution. A discovered
Python cache-write package failure is retained, corrected and documented in
active-system/evidence/provisioned-discovery.md. Public /desktop/ release/app/
config hashes remain unchanged. No external deployment/router changes. Continue
managed role/root-key ownership, /hidden/ proxy/rollback, public relay policy and
independent-network checks. The full objective remains active and unfinished.

### Separate local issuer/steward ownership — 2026-10-22

The standalone issuer can now read operator-pinned public policy and a signed
bundle from an independently owned steward, without sharing private keys or
databases. Provisioning accepts the existing issuer's public configuration.
Actual transient systemd DynamicUser services run under different non-root UIDs;
native credential probes prove mutual private-file denials and unreadable
operator root key. Application code and public policy are read-only to both.

Local domain-root and /hidden browser integration pass: real guest boot,
identity, discovery and separate RTC chat/chess. Both layouts also
prove registered login survives native issuer restart with a fresh session/key,
wrong-password rejection, actual native issuer UID and login while the steward is
stopped. Signed renewal travels through the public bundle. See
active-system/evidence/isolated-service-roles.md for commands, exact receipts,
retained setup failures and scope. The new 159-file profile-3 export preserves
verification of old profile-1/2 artifacts. Disposable state and units are cleaned;
both original and online releases are verified unchanged after execution.

No external deployment or router changes. The public /desktop/ hashes still match
the previous prototype; /hidden/ is not public yet. Production persistent service
ownership and root custody, isolated guest egress, public TURN/443, managed
proxy/rollback and WAN evidence remain next deployment work. Multiparty routing,
private groups and repair remain part of the full unfinished objective.

The current profile-3 export also passes the complete existing read-only /hidden
stack: selected TURN/TLS relay candidates, both guests' ping/DNS/HTTP, explicit
root renewal and supervised discovery recovery. This remains a same-UID combined
compatibility check; it does not claim independently owned guest egress/TURN.
`active-system/.build/checks/isolated-roles-milestone-result.json` binds the
separate root/hidden role receipts (64 total UID probes), regressions, complete
stack and unchanged public-prototype proof. All fixture credentials/state are
removed, and the overall goal remains active.

### Dedicated guest relay account and ping policy — 2026-10-22

Created local locked, no-home/no-login codi-issuer, codi-steward and codi-guest
accounts. The repeatable account tool validates existing identities and refuses
unsafe collisions, supplementary memberships, shared primary groups and UID
aliases; 14 fixtures plus actual idempotence/collision checks pass. These accounts
remain locally for managed setup. No corresponding remote accounts were created.

Both root and /hidden now pass real three-account systemd/browser integration:
57 file-access probes per layout, complete issuer unit restart/account continuity,
signed bundle renewal, separate RTC chat/chess, and two actual v86 guests doing
ping/DNS/HTTP through the dedicated relay/QEMU UID. Observed QEMU processes have
zero effective capabilities and no developer-group membership. Only the guest
role can open an unprivileged ping socket; all three are denied raw sockets.
The new --require-ping relay option refuses startup before listening if permission
is absent. During each test only, ping range 1000..1000 expands to 1000..1001;
it is restored afterward, with no persistent sysctl file or forwarding change.

The updated 160-file profile-4 artifact also passes complete existing read-only
TURN/TLS, guest Internet, root renewal and steward-recovery compatibility. Native
packet/lifecycle (65) and export/refusal (12) regressions pass. Private test state,
units and QEMU processes are removed; online/original artifacts remain intact.
See active-system/evidence/managed-guest-role.md and
active-system/.build/checks/managed-roles-milestone-result.json for exact evidence.

Fresh trusted HTTPS confirms /desktop/ bytes/config are unchanged. Read-only
box-webhost inspection confirms clean d6ccfc4 source and the original healthy
release, no codi roles, ping group 1000 only and forwarding 0. /hidden/ remains
unpublished. Next: managed persistent units/state and root/backup lifecycle,
public guest-abuse policy, TURN/443 and scoped /hidden/ deployment/rollback, then
independent-network verification. Production identity review, multiparty routing,
private groups and history repair remain in the active full goal.

### Persistent operator and private box-webhost installation — 2026-10-22

Added a self-contained profile-5 verifier and root operator for prepare/provision/
renew/export/start/stop/status. Actual installed unit files pass local /hidden/
and root checks, including global instance locks, drift/conflict refusal, no repeat
provision, live-ledger preservation, rejection before root advance when ledger is
missing, full issuer/account restart and missing-key refusal without regeneration.
Sixteen operator invariants, 12 exporter cases and the complete existing read-only
TURN/TLS/guest-Internet/recovery stack pass against the current 162-file artifact.
All local fixture units/state are removed and ping policy restored.

Git-first import: commit 517179c549203ba7dfb0cc69cc13e99a24ecfe1f adds only 164 files
under tools/codiserver in the KSU repository. Pushed to box-git and pulled ff-only
on clean box-webhost source. Public/app trees and the running website release are
unchanged. The native package was then installed with a separate pinned venv:

- Release: /srv/codi-connected/releases/517179c
- Python: /srv/codi-connected/venvs/517179c/bin/python
- Config: /etc/codi-connected/ksu/managed.json
- Role/operator state: /var/lib/codi-connected/ksu
- codi-ksu-hidden-issuer.service active on 127.0.0.1:8118, UID/GID 982/975
- codi-ksu-hidden-steward.service active on 127.0.0.1:8119, UID/GID 981/974
- Guest and bootstrap stopped; normal units disabled for boot, bootstrap static.

Real server API/signature, registered account/fresh sessions, renewal, wrong-
password/logout, private HTTP paths and 15 UID access probes pass. Running native
processes have zero effective capabilities and no developer-group membership.
The disposable registered probe account is disabled. Initial discovery authority
expires 2026-10-23 22:36:39 UTC; no automatic signer/timer exists. Renew explicitly
with the installed operator before expiry; after expiry renew then start the
steward. Never rerun provision over this real state or replace its live ledger.

All eight managed sites pass production smoke after installation. /desktop/
release/app/config hashes remain unchanged; /hidden/ still returns 404. Website
current remains 20261021T125622370238Z-279f978f (deployed d6ccfc4), although editable
source is now 517179c. No public proxy/router/firewall/guest policy changed; ping
range remains 1000 1000. Server AGENTS.md documents the new private services.

See active-system/evidence/persistent-service-operator.md for exact receipts,
commands, retained failures and limits. Next: tested native upgrade/rollback and
backup/recovery, persistent guest/boot/abuse policy, public TURN/443 and scoped
/hidden/ proxy/CSP, trusted external browsers and independent WAN evidence.
Production identity review, multiparty routing, private groups and history repair
remain unfinished; the full goal is active.

Current aggregate receipt:
active-system/.build/checks/persistent-services-milestone-result.json (PASS).
It verifies current source and artifact bytes and binds both local installed-unit
layouts, operator/export invariants, full TURN compatibility, Git synchronization,
real private webhost installation/API/process checks, eight-site health and the
unchanged public boundary. Full objective completion is explicitly false.

### Verified private checkpoint and fenced recovery — 2026-10-22

Profile-6 controller adds root-only backup/verification, explicit disaster restore
and journaled interrupted-operation recovery. An exact 13-file checkpoint excludes
guest files/chat/RAM state, keeps snapshots root-owned 0700/0600, and validates
hashes, SQLite integrity and key/policy/publisher bindings. Config version 2 adds
an independent root revision fence with write-ahead reservations before renewal.
Pending recovery blocks start/signing. Disaster recovery keeps issuer/root keys
and account subjects, signs a higher root epoch, rotates the scoped service key
and disables recovered credentials until explicit reset/revalidation. It restores
a checkpoint, not later account edits; code rollback must not rewind live data.

Real installed-unit/browser runs pass at /hidden, root, and with new controller /
old profile-5 online roles. They restore a missing key from root snapshot 2 after
live revision 3, advance to 4, and resume a second restore to 5 after simulated
process death immediately after a REAL old-directory rename. Tamper/permission/
active-unit/fence guards and fresh-password restoration of the same account pass.
Fresh Chromium v86/identity/RTC chat/separate chess and both guests' ping/DNS/HTTP
pass after recovery. Crypto (17), root-owned dummy snapshot guards (16), operator
(16), exporter (12) and full existing read-only TURN/recovery stack pass. Local
fixtures are removed and temporary ping policy restored.

Git-first source is now 6b99ae4477492c05e86e991460944dbea883f819; only six native/doc
files changed, public/app trees and live website release unchanged. New controller
is /srv/codi-connected/releases/6b99ae4/scripts/manage-services.py. Use it with
/srv/codi-connected/venvs/517179c/bin/python and the existing
--config /etc/codi-connected/ksu/managed.json for ALL lifecycle/renewal commands.
Online issuer/steward code/units remain on 517179c. Config is now version 2; the
old controller deliberately refuses it. Do not use the older controller command
shown in historical entries above.

Actual server checkpoint created/verified:
/var/backups/codi-connected/ksu/checkpoint-20261022T231041Z
manifest SHA256 8ade3bfc602a77391f4ba190506d27564f513f99ce7a04c8e76c0835a704aa25.
It contains private keys/password hashes. Keep it outside source/public/downloads;
it is on-host and unencrypted, not an off-host custody solution. No live restore
was performed. The three key byte hashes were preserved; private issuer/steward
resumed (PIDs 182506/182507 at audit), guest/bootstrap stayed stopped, and boot/ping
policy stayed unchanged. Config-side recovery fence exists. All role accounts
are denied backup reads. Private signed API checks and eight-site production smoke
pass after backup. Server AGENTS.md records the new operator path and checkpoint.

Authority expiry remains 2026-10-23 22:36:39 UTC. No automatic signer exists; renew
explicitly using the NEW controller, then start steward if it had expired/stopped.
No proxy/Caddy/router/firewall/website deployment changed. /desktop/ hashes and
local-only config remain unchanged; /hidden/ still returns 404. See
active-system/evidence/native-checkpoint-recovery.md for exact artifacts/receipts.
Next: native code upgrade/rollback preserving current data, encrypted/off-host
custody and recovery transfer, persistent guest/boot/abuse policy, public TURN/443,
managed /hidden/ routing/CSP, external browsers and WAN evidence. Production
identity review, multiparty/private groups/history repair remain in the active
full goal.

Latest aggregate: active-system/.build/checks/recovery-milestone-result.json (PASS).
It binds the current native artifact, exact archived/current runner provenance,
three real recovery layouts, regressions/TURN compatibility, Git sync, actual
server checkpoint/privacy and resumed API/process/eight-site/public-boundary
evidence. It does not claim off-host custody, code rollback, live server restore
or public/WAN operation; the full objective remains active.

### Latest: native code upgrade/rollback verified — 2026-10-22

Current box-webhost controller and online issuer/steward code are
/srv/codi-connected/releases/1db6187 (source commit
1db61878120627ac497dfa68b9a226a5f6fcf8a6). Use its scripts/manage-services.py
with /srv/codi-connected/venvs/517179c/bin/python and
--config /etc/codi-connected/ksu/managed.json for ALL lifecycle/renewal commands.
Earlier controller paths above are historical. Retain old code/environment for
reviewed rollback. Guest/bootstrap stay stopped; boot/ping/forwarding stay unchanged.

Actual private upgrade → rollback → upgrade preserved current accounts, keys,
root authority and recovery fence byte-for-byte. Post-upgrade identity API,
Unix-role isolation and all eight HTTPS sites pass. Local `/hidden`/root installed
unit tests additionally cover broken candidate startup, wrong-policy HTTP 200,
real partial unit replacement, successful commit with failed journal cleanup and
post-checkpoint/post-upgrade account preservation. Profile-7 backup recovery and
full read-only TURN/TLS/guest Internet/browser checks pass. Exact artifact and
receipts: active-system/evidence/native-code-upgrade.md. Current aggregate:
active-system/.build/checks/deployment-milestone-result.json (PASS).

No website/Caddy/router/firewall change occurred. /desktop/ still has its exact
static prototype bytes/config and /hidden/ returns 404. Root authority is still
revision 1, expiring 2026-10-23 22:36:39 UTC; explicitly renew with the NEW
controller. The existing on-host root-private checkpoint remains; no live restore
was performed. Server AGENTS.md records current paths and recovery instructions.
Next: public guest/boot policy, managed hidden proxy/CSP with scoped rollback,
TURN443 and trusted external/browser/WAN checks, plus off-host custody and the
remaining production identity/multiparty/private groups/history-repair work.
The full goal remains active; final deployment will use the domain root.

### Live hidden preview — 2026-10-23 UTC (2026-10-22 New York)

https://ksu.codes/hidden/ IS NOW LIVE. https://ksu.codes/desktop/ retains its exact
prototype bytes/local-only identity/config. Homepage and seven other sites are
unchanged. Current controller AND all three online native roles use
/srv/codi-connected/releases/f2fbd4d (source f2fbd4d0497e71c82d24b29b277e155dbac2365d),
with /srv/codi-connected/venvs/517179c/bin/python and existing managed config.
Use this new controller for all lifecycle/renewal commands; older paths above
are historical. Bootstrap remains stopped; normal native units remain disabled
for boot. Root revision1 expires 2026-10-23 22:36:39 UTC; explicit renewal only.

Managed hosting generator now accepts KSU-only codi_preview=true. It scopes
hidden CSP/routes/body cap to existing issuer8118/steward8119/guest8132 behind
80/443, retaining other site blocks and desktop CSP. Root controller lock,
source/manifest pins/backups, installed Caddy validation and all-site smoke were
used; derived live Caddy was not hand-edited. Website current symlink is unchanged.
No new router/firewall ports. Guest GID1001 has unprivileged ping alongside admin
1000: ping_group_range 1000 1001, declared in its dedicated sysctl file. Forwarding
is off, no raw capabilities, guest wires isolated. Preview permits public ping,
gateway DNS, TCP80/443, with per-connection and global traffic/lifetime caps.

Two default-trusted Chrome contexts on the PUBLIC URL pass signed development
identity, WSS discovery, real RTC chat, separate legal chess/room chat, Linux,
both guests' ping/DNS/HTTP and guest/key preservation. Public Chrome registered
login/renew/logout/wrong-password checks also pass; exact probe account disabled.
The unmatched-Host test initially mistook Caddy's empty 200 for issuer acceptance;
it now proves no issuer response and distinguishes this from HTTP rejection.
Foreign Origin correctly returns403. No production-identity or independent
WAN/NAT claim: public peer witnesses are host candidates on the development
network. Public TURN is still not configured.

See active-system/evidence/live-hidden-preview.md for exact artifact, live hashes,
receipts and rollback backups. Server AGENTS.md records activation state. Latest
public receipts are preview-public-browser-result.json and
preview-public-identity-result.json under active-system/.build/checks/.
Next: guarded deactivation/recovery, public TURN443 and independent-network proof,
deliberate boot/renewal, production identity/abuse and remaining multiparty/private
groups/history repair/off-host custody. The full goal remains active.

### Latest local TURN/ingress proof — 2026-10-23 UTC

Live preview and prototype are unchanged. Local tests prove real TURN/Chrome in
a private loopback-only systemd network, with distinct non-root relay/proxy users,
no capabilities, no host/Internet reachability and no forwarded UDP relay ports.
Chrome stats show TLS relay/relay allocations127.0.0.2:13500..13531; chat, separate
chess, guest Internet, root renewal, steward recovery and full cleanup pass.
Separate shared-ingress tests prove eight simulated websites, canonical redirects,
source IP preservation, h1/h2/no-ALPN compatibility and dedicated TURN SNI with
ACME ALPN going to Caddy. That routing test uses a TLS stub, not real allocations.

See active-system/evidence/private-turn-ingress.md and aggregate
active-system/.build/checks/turn-ingress-milestone-result.json. Fresh eight-site
and public-config checks pass. No live native/proxy/router/firewall/certificate
or identity policy was changed; public TURN remains unconfigured.

Pending user DNS action: Porkbun A host turn ->104.180.210.33. Existing tools do
not control that DNS account. No answer or successful DNS state has been assumed.
Continue independent native TURN credential/policy and managed ingress/certificate/
rollback work. Then test public TLS and independent networks before claiming
cross-NAT reliability. Goal stays active; no graphical games are being added.


### TURN policy candidate, public certificate and entry fix — 2026-10-23 UTC

User confirmed the Porkbun turn record. All four authoritative servers and
public DNS readiness resolve turn.ksu.codes to104.180.210.33. Its trusted Caddy/
Let's Encrypt certificate is now live (expires2027-01-21 00:01:42UTC); that name
serves generic404 only. Public TURN/shared443 ingress is STILL OFF. No new ports,
router/firewall or native service/policy changes were made.

The user reported blank /hidden. Reproduced: exact /hidden returned empty200,
while /hidden/ worked. Cause: our Caddy `redir /hidden/ 308` was interpreted as
an optional path matcher plus destination308, so never matched inside /hidden.
Fixed generated source to `redir * /hidden/ 308` under controller lock with
backup/validation/rollback. Actual Caddy-adapt regression, GET/HEAD308 and two
fresh default-trusted public Chrome contexts now pass both URL forms through
Linux ready with zero browser errors. All eight sites pass; /desktop bytes and
native PIDs185140/185141/185562 remain unchanged. Source generation helper fixed.

CURRENT hosting generator SHA256:
39cf221f0115ebee03c2b3f54f73b033a9e158cec262f7277f619fda718ff51e
CURRENT sites.toml SHA256:
1e6183699af82d0a019e112f550b70744928b3fb59d3151fe1e80a3b7cad836c
CURRENT derived Caddyfile SHA256:
4ef98228cd63160c6e4f6e5528447a7e17d300ca3ea7b0bd3b1300a818f30bd8
The optional KSU-only codi_turn_certificate=true flag adds only that certificate
hostname. Current health script writes preview-redirect-live-health-result.json;
older aggregate receipts are historical, not current hosting pins.

Native profile9 candidate: active-system/.build/releases/connected-turn-20261023-r2
(inside active-system omit that leading directory),165files/13,009,956bytes,
manifest dea2b7d770b3ddd8f9dc07282d1f5f2ca98c395469b7eee361c2bff4f3cc627e.
Git source commit 5e364fece77845762c0061dcf51ed0f5b53fd5ed pushed to box-git main. Server editable checkout and
installed/live native code remain f2fbd4d; do NOT use an uninstalled candidate
controller as the current operator. No native rollout or website release change.

Profile9 supports root-owned read-only systemd LoadCredential mounts without
relaxing ordinary file permissions, explicit all/direct-ICE-with-TURN-fallback
versus diagnostic relay policy, checkpointed managed schema3, and journaled
issuer-only configure-turn/disable/recovery. Policy changes preserve guest cookie,
steward/guest PIDs, keys/accounts/root/fence; issuer RAM sessions end on restart.
Code rollback preserves current policy and refuses incompatible older profiles
under schema3. External TURN/TLS secrets need separate protected custody and
must remain available for recovery; core13-file checkpoints do not include them.

PASS:22TURN bounds tests,18managed policy tests,16code boundary tests,12release
mutation tests,145browser protocol cases, real static-User credential mount,
actual persistent service configuration/failure/interrupted-write/committed-
journal recovery, policy-preserving code rollback, secret drift refusal, full
read-only profile9 private-network TURN/Chrome/chat/separate chess/v86/guest
Internet/root renewal/steward recovery and cleanup. Initial fixture source-dir
permissions refusal and recovery-exit-status bug are retained in failed receipts;
both corrected and clean reruns pass. See active-system/evidence/managed-turn-policy.md
and managed-turn-milestone-result.json for exact receipts and remaining scope.

NEXT: guarded persistent isolated TURN/socket/proxy service, certificate custody/
renewal and managed shared443 ingress+rollback; public trusted relay test and
independent WAN/NAT proof. HAProxy/Coturn are NOT installed on box-webhost yet;
apt simulation shows11new packages,0upgrades/0removals. Install only while their
default services are prevented from automatically starting/exposing ports; use
scoped native units. Native root/boot/custody/multiparty/repair goals remain open.
Live controller stays /srv/codi-connected/releases/f2fbd4d with existing venv,
schema2, root1 expiry2026-10-23 22:36:39UTC, explicit renewal, no automatic signer.


## Phone frontend update — 2026-10-23 01:55 UTC

/hidden/ now uses frontend R4 `5a15614dc4fbab1630198a831e3dbedfcf925c496ec756c5ff8a3629716903fe` from source
`23448ebd2a4a3fe9fdff8e85676b59e4dc8eef01`. Only app.js, style.css and terminal.js are
served from `/srv/codi-connected/frontends/5a15614dc4fbab1630198a831e3dbedfcf925c496ec756c5ff8a3629716903fe`.
Index/cookie, APIs, WSS, guest relay and all other assets remain on the existing
backends. Operative native controller AND all three online roles remain
`/srv/codi-connected/releases/f2fbd4d` with existing venv/config; source checkout
advancement does not install native profile9. /desktop bytes and website release
are unchanged. No router/firewall/new ports/boot changes. Public TURN stays off.

Phones: native terminal input/touch keys, contained menus and window sizing,
Applications icon, no battery menu, status notices clear after four seconds.
All terminal commands are at the bottom; keyboard viewport resize follows the
typing line, manual scrollback pauses following, typing/Keyboard resumes it.
The user confirmed actual phone touch and terminal typing work. Workspaces are
important: keep all three numbered workspace buttons in the phone TOP BAR,
with 44px targets and selected state. Switching back restores the previous
focused window. Desktop pager, multiple windows and title sizing are preserved.

Current hosting SHA256 pins:
- generator: `7ee1db8acefb1be6d48f9c24fb67ee64c0fa3b24b7d7d06c6f41708db232a6bd`
- sites.toml: `ed0c5f8def50c3e01fae27d09a1846b593ecb928072c710dfe1aba6587bc5a9f`
- derived Caddy: `ca335456319521c96ddcf9228dc371825027365819eaefc10be698adfd5e57c8`

Managed KSU-only `codi_frontend` selects exactly three public assets. Preserve
`redir * /hidden/ 308` and dedicated certificate hostname. Do not hand-edit
derived Caddy. Scoped R4 rollback inputs (return to R2) are
`/var/backups/webhost-sites/change-20261023T015451204743Z/common.py` and
`/var/backups/webhost-sites/change-20261023T015451205266Z/sites.toml`. Restore under the hosting
controller lock, validate pins, regenerate/validate/apply, then check all eight
sites and /desktop. R3 was pushed as source only, never activated. R1/R2 are
retained. Root receipt is `/srv/codi-connected/frontend-5a15614dc4fbab1630198a831e3dbedfcf925c496ec756c5ff8a3629716903fe-activation-result.json`.
Caddy reload can close proxied WebSockets; unchanged native PIDs/cookies/RAM
do not prove uninterrupted streams. Keep browser RAM/files and user tabs intact.

Current touch receipts: touch-preview-result.json, touch-public-result.json,
touch-frontend-activation-result.json, preview-touch-live-health-result.json,
touch-milestone-result.json under active-system/.build/checks. See
active-system/evidence/touch-preview.md for test scope and remaining limitations.
Earlier aggregates describe their original source/hosting states.


## Workspace icon and session network menu — 2026-10-23 02:02 UTC

Latest user direction supersedes the R4 inline pager: the existing computer/
network icon in the TOP BAR now opens a workspace chooser with all three
numbered previews, selected state, and focus restoration. Its badge shows the
current workspace number. Network details moved into the session-dot / trust
message menu with End session and Close. This applies to phone and desktop.
Do not restore the standalone Network popup or inline pager from older notes.
All terminal touch/viewport fixes remain. /desktop is unchanged.

Live frontend R5: `3d88c0f08137ee4b0bb8a75c357c977da0d5dcb18112908629d9c1bd3c844f05`
Source/server checkout: `a5a73553efea90a00c9d15f131ed2f7b3f7516d9`
Current hosting generator: `7ee1db8acefb1be6d48f9c24fb67ee64c0fa3b24b7d7d06c6f41708db232a6bd`
Current sites.toml: `60a47975eca353be4802e25cd3f7b6a670569f1f1b587c941d60aec49414c435`
Current derived Caddy: `a727f48d82b5786a4d07ad457415a4fe692dffdbb0ba3b8b47f965f47698d060`
Root receipt: `/srv/codi-connected/frontend-3d88c0f08137ee4b0bb8a75c357c977da0d5dcb18112908629d9c1bd3c844f05-activation-result.json`.
Scoped rollback to R4 inputs:
`/var/backups/webhost-sites/change-20261023T020130850941Z/common.py`
`/var/backups/webhost-sites/change-20261023T020130851390Z/sites.toml`
Use the hosting lock, pins, generated validation/application and all-site checks;
never hand-edit derived Caddy. Three-asset-only routing, original index/cookie,
all native PIDs/config, website release, /desktop and all eight sites preserved.
Operative native controller/roles remain f2fbd4d; profile9 stays uninstalled.
No router/firewall/ports/boot change; public TURN remains off.

Current evidence: active-system/evidence/touch-preview.md and the same current
touch receipts/aggregate as above, now binding R5. Tests cover the icon/chooser
and session-menu contents alongside existing terminal and desktop regressions.
The full networking/identity roadmap remains active; resume persistent isolated
TURN/certificate renewal/shared443 implementation after the user's UI requests.


## R6 workspace dismissal and managed relay candidate — 2026-10-23 02:18 UTC

Latest workspace popup has NO Close button. Selecting a workspace switches and
dismisses; clicking outside dismisses without switching; the computer icon
also toggles it closed. Network details remain in the session-dot menu, whose
Close and End session buttons remain. Three workspaces and focus restoration
remain. User-directed R6 is live under /hidden only; /desktop unchanged.

Frontend manifest: `37b9594dca8d4f513ed8c35e686397a1e5ac2287226b6493560d3a9951049d3f`
Source/server checkout: `e82dec58c3bb323850b9588337afd5d33ca112a5`
Hosting generator: `7ee1db8acefb1be6d48f9c24fb67ee64c0fa3b24b7d7d06c6f41708db232a6bd`
Hosting manifest: `bdcd583bd6ec49eb921c5e25510191e4b4deb7999dc43a40d8c3c9ac43743b20`
Derived Caddy: `ed10efb73acfd06aff141a90598f9b3c2755ed19dd0e4cb99752f9e5a79cc5f3`
Rollback to R5 inputs: `/var/backups/webhost-sites/change-20261023T021720962444Z/common.py`
and `/var/backups/webhost-sites/change-20261023T021720962892Z/sites.toml`. Use the hosting
lock/pins/generated validate/apply/all-site workflow, never hand-edit Caddy.
Native controller and roles remain f2fbd4d, PIDs185140/185141/185562 unchanged,
existing index/cookie/state and website release preserved; all8 sites pass.
Current touch receipts/aggregate bind R6. No ports/router/firewall/boot change.

NEW relay operator is source-only in tools/codiserver/relay-operator, outside
public. NOT installed on box-webhost. Separate four-file artifact at
active-system/.build/relay-operators/persistent-turn-20261023-r1, manifest
2919d0c14041c78ac59d1ba130d4ce2d614f76e44b9d8c5ddf468837233d3ca4.
Persistent private config/certificate/shared-secret custody, static disabled-for-
boot units, two distinct DynamicUsers in one private loopback namespace, fixed
127.0.0.1:13479 socket proxy, private relay127.0.0.2, quotas and 64 proxy
connections. No public UDP or host/Internet access. Root credential bundles via
LoadCredential, pinned binary/unit/credential checks, no unmanaged drop-ins.
Certificate refresh validates exact DNS SAN/key/48h validity, preserves shared
secret, journals before changes, restores on failed readiness, recovers old
pre-commit/new committed config after interruption. Restarts end relay streams.

PASS:12 real installed systemd lifecycle/rotation/fault/custody checks,7 exporter
mutation checks, actual read-only profile9 issuer/steward/guest + managed relay
Chrome relay/relay TLS chat/separate chess/PGN/guest ping/DNS/HTTP, explicit root
renewal and steward crash recovery; fixture cleanup completed. Initial adapter
cleanup could not stat root0700 config as normal user; failed receipt retained
as managed-relay-fixture-cleanup-before-result.json, leftovers explicitly removed
and corrected privileged cleanup clean rerun passes. Actual copied operator
hashes are captured before execution and bound to the package manifest. Browser
integration used native profile9 artifact dea2b7d..., not current R6 frontend;
R6 has separate local/public touch+desktop tests. See evidence/persistent-relay.md.

No Coturn/HAProxy packages or relay operator have been installed on box-webhost;
public TURN remains OFF. Apt candidate is coturn4.6.1-1build4 and haproxy2.8.30.
Upstream has newer security advisories; choose/review a patched production
Coturn before exposure. Private namespace is an independent enforced boundary.
Next: patched relay binary selection/build; install private operator/services
with Caddy cert custody and renewal workflow; managed shared80/443 ingress and
rollback; guarded native9 rollout/issuer policy; public trusted relay and actual
independent-WAN proof. Preserve current frontend overlay and explicit native
root-renewal policy. Root1 expires2026-10-23 22:36:39UTC. Full goal is active.


## In-progress relay follow-up interrupted by user voice controls — 2026-10-23

Built upstream Coturn4.18.0 commit23c6c1d32a3d2b21a56cee65d3203bcc4ea82d2b
with scripts/build-coturn.py at .build/tools/coturn-4.18.0-build-r1/runtime.
Manifest69ce8817cef7b4a1d99a30be1d5548e92eb0bfeaa2ee6ae6fb165180a5ea4e4b,
binaryc276e99119a21882d4c9408d42aa55ad75b9d3c00206715352c682612cd217a1.
ArchiveSHA d7e2ee337b5298c30cc5cd365c3173d05b97c749d28e9416afa4ca907925ce15.
Source from official HTTPS; annotated tag signature is NOT verified. Database/
Prometheus/SCTP/systemd libraries compiled out, TLS/libevent remain. Built locally,
NOT installed on webhost. Current manager now schema2 requires4.18.0; 12 actual
lifecycle tests passed once, then tlsv1 flag names corrected and certificate
expiry handling changed; rerun is REQUIRED. Certificates module, source binding/
refresh and reviewable scheduled job units + CLI were just added, UNTESTED.
Exporter now5files/version2, old immutable operator remains version1 in Git/live
source, not installed. Adapter still needs to copy certificates.py; new controller
source/export/cert timer need tests and a new artifact before any rollout.
Old coturn4.6 receipts archived with coturn46- prefix. No running local relay
fixture remains. New speech UI work follows the user's latest steering.


## R7 terminal Voice/Enter and speech R2 — 2026-10-23 03:12 UTC

/hidden/ frontend R7 is 53441112d3c594071ebb542012bdcf3fb5e2c20b61c496cd2258161891d6e8aa,
source867c7969a1fd94115c874edaec4f775b57d9b6e1. Phone bottom keys now Keyboard,
Ctrl+C,Tab,Esc,Voice,Enter; arrows/Help buttons removed. Voice/Enter available
on desktop. Workspace icon/chooser/no Close and session network menu preserved.

Static speech R2 108c2aa406e456841e360ea55efb5c8aeeba0f547c3be58561795cd7add1598b,
source/server checkout 94e9a3e9d79dc97b4b9768095227d5733ca06764, installed /srv/codi-connected/speech/108c2aa406e456841e360ea55efb5c8aeeba0f547c3be58561795cd7add1598b.
KSU-only codi_speech selects22 static files under /hidden/assets/speech/*.
TF3.8.1 + matching ORT1.22dev + pinned English Whisper tiny.en q8, about68MB.
User prefers on-device recognition. CPU/WASM always; no server audio upload.
Old GPU path hung in a software-GPU test; GalaxyS25/Chrome user reported nonsense
and repeated biasesVIDEO, precise physical driver cause unproven. R2 rejects
repeated output, skips low energy, bounds requests, preserves explicit Enter.
Real local/public recording/Whisper tests, load/inference cancellation, repeat
guard, denial/track cleanup/terminal close PASS. GPU exposed but never read.
Physical phone mic/latency not covered automatically; user subsequently confirms
that R2 works. Touch/desktop aggregate + all8 sites/prototype/native health PASS.
See active-system/evidence/terminal-voice.md (active-system prefix omitted here
when already inside that target) and current speech/touch milestone receipts.

Hosting generator 137f767bff1fe247b8cda574bc6710c63fc1a7d441064fbf6c00a3fc129cbd96
Manifest 0c2683cd386b56caac8af95d9897056e20a9f356134f9baf3bff42c9a683be54
Derived Caddy 89036ff6270db9b319cd1cc6bc44d6ecae479821b7e2a69832802241a090d0eb
Speech rollback inputs: /var/backups/webhost-sites/change-20261023T030909288225Z/common.py
and /var/backups/webhost-sites/change-20261023T030909289110Z/sites.toml. Previous speech selects GPU and
retains reported bug. Use controller lock/pins/generated validation/application,
never hand-edit derived Caddy. Root activation receipt speech-108c2aa406e456841e360ea55efb5c8aeeba0f547c3be58561795cd7add1598b-activation-result.json
under /srv/codi-connected; smoke reports/private/codi-speech-assets-20261023.json.
Native controller/roles remain f2fbd4d/schema2, PIDs185140/185141/185562;
index/cookie/config/website release and /desktop bytes preserved. No ports/boot
changes; TURN OFF. Caddy reload may close WebSockets despite unchanged native
PIDs/RAM. Root1 expiry2026-10-23 22:36:39UTC; explicit renewal still needed.
Relay operator2/cert-source code remains local UNTESTED WIP; do not deploy it.

Latest user request after successful phone retest: make voice general across
apps, preload model alongside Linux, floating hold-to-talk button that targets
the previously focused input/cursor. They asked about writing while speaking;
explained current Whisper writes after release, chunked interim updates could
be added later. This general voice follow-up is now in progress, not deployed.


## R8 general hold-to-talk and task/workspace repair — 2026-10-23 03:26 UTC

## Current general voice deployment — 2026-10-23 03:26 UTC

Frontend R8 `82757ec6b69d5d2c0acc60c48b5371d4620e20df5f7329ec8494773832d2514d` and speech R3
`df759266dbd1cc339c4cd96df8265e274b9b9042abef275d00fc0809deed1f3b` are live only at /hidden/.
Both source bundles and the server editable checkout are `2ffb8b8a6ccf0525e1d1648835f029a6253973f7`.
The native services, index/cookie, website release, and /desktop prototype are
unchanged. Native roles/controller remain f2fbd4d with PIDs185140/185141/185562.

- A floating microphone button works with the previously focused enabled text
  field or terminal. Hold to record, release to transcribe and insert. The
  original input selection is replaced in the editor; input events update app
  drafts/dirty state. No automatic Enter, form submission or chat send.
- Model loading starts alongside Linux, without microphone permission/capture.
  Audio starts only after a gesture. CPU/WASM, English tiny.en and the repeat/
  low-energy guards remain. Text appears after release, not during speech.
- The shared client retains legacy toggleVoice for frontend rollback. The old
  per-terminal Voice button was removed; Keyboard/Ctrl+C/Tab/Esc/Enter remain
  at the bottom. The floating button has a phone bottom gutter and follows
  visualViewport resizing. Pointer capture, cancellation, visibility and blur
  handling prevent continued recording after a cancelled gesture.
- Workspace/minimize/panel changes retain existing app DOM, drafts and cursor
  positions. A different editor state/file path deliberately replaces only
  that app content. Removed windows are cleaned up.
- Running task icons show a count even for one window and keep a running line
  when minimized; active highlighting follows focus. Task lists cover all
  workspaces, and choosing a task restores its original workspace.
- The phone window '^' roll-up control is restored. Applications → Terminal
  always opens another window. These windows still share the same guest serial
  console; independent per-window PTYs/shells are not implemented yet.
- Workspaces are removed from Applications; the top-bar computer icon retains
  the three-preview chooser, selection/outside dismissal, and no Close button.

Local tests: general-voice-result.json PASS with real microphone-file capture,
actual CPU Whisper in terminal and editor, trusted touch press/release, preserved
focus/selected range, another app's cancelled inference, workspace DOM/drafts,
additional terminal windows/counts, roll-up and cross-workspace task restore.
Current touch-preview-result.json PASS covers native keyboard/viewport/menu/
scrollback and desktop mouse regressions. Public versions also PASS in separate fresh
Chrome sessions using default TLS trust; touch and speech milestone receipts
bind the exact assets and current hosting health. Neither automation claims a physical phone microphone test.
User confirmed the previous CPU voice R2 worked on their S25; R8/R3 still needs
fresh-device feedback. Save/download ephemeral guest files before refreshing.

Current hosting pins:
- generator `137f767bff1fe247b8cda574bc6710c63fc1a7d441064fbf6c00a3fc129cbd96`
- manifest `bd7b0c20bdc477f769d85888f7c8806bf10a73faf62ad6aee797effbffd3dca4`
- derived Caddy `b77d19757e598d32d8a6fe57cee0d909cd8f04fe53387225169c9cd00a58255f`

Root activation receipts are frontend-82757ec6b69d5d2c0acc60c48b5371d4620e20df5f7329ec8494773832d2514d-activation-result.json
and speech-df759266dbd1cc339c4cd96df8265e274b9b9042abef275d00fc0809deed1f3b-activation-result.json under
/srv/codi-connected. Immutable assets are under frontends/<frontendSHA> and
speech/<speechSHA>. Frontend rollback to R7 while keeping R3 speech uses
/var/backups/webhost-sites/change-20261023T032619588310Z/common.py and
/var/backups/webhost-sites/change-20261023T032619588759Z/sites.toml. The earlier speech rollback to R2 uses
/var/backups/webhost-sites/change-20261023T032537873812Z/common.py and
/var/backups/webhost-sites/change-20261023T032537874722Z/sites.toml. If fully reverting both, restore frontend
first then speech (the old frontend is compatible with R3). Use the controller
lock, exact pins, generated Caddy validation/application and all8-site/prototype
checks; never hand-edit Caddy. Caddy reload can close existing WebSockets.
No router, firewall, port, native code or boot-policy change. Public TURN OFF;
full networking/login roadmap remains unfinished. Earlier R2 details below are
historical; current receipt names for voice are general-voice-result.json and
general-voice-public-result.json, bound by speech-milestone-result.json.



## R9 current general voice, workspace and icons — 2026-10-23 03:31 UTC

Frontend R9 `51ae4707d020ff04885cdcfdc2b16c762c2bb156b6285122b2c5e63d8e578e1e` and speech R3
`df759266dbd1cc339c4cd96df8265e274b9b9042abef275d00fc0809deed1f3b` are live only at /hidden/.
Frontend source and server checkout: `f1f3933d2943cb3d7dc0f858f37216984227dce5`.
Speech R3 source remains `2ffb8b8a6ccf0525e1d1648835f029a6253973f7`.
The native services, index/cookie, website release, and /desktop prototype are
unchanged. Native roles/controller remain f2fbd4d with PIDs185140/185141/185562.

- A floating microphone button works with the previously focused enabled text
  field or terminal. Hold to record, release to transcribe and insert. The
  original input selection is replaced in the editor; input events update app
  drafts/dirty state. No automatic Enter, form submission or chat send.
- Model loading starts alongside Linux, without microphone permission/capture.
  Audio starts only after a gesture. CPU/WASM, English tiny.en and the repeat/
  low-energy guards remain. Text appears after release, not during speech.
- The shared client retains legacy toggleVoice for frontend rollback. The old
  per-terminal Voice button was removed; Keyboard/Ctrl+C/Tab/Esc/Enter remain
  at the bottom. The floating button has a phone bottom gutter and follows
  visualViewport resizing. Pointer capture, cancellation, visibility and blur
  handling prevent continued recording after a cancelled gesture.
- Workspace/minimize/panel changes retain existing app DOM, drafts and cursor
  positions. A different editor state/file path deliberately replaces only
  that app content. Removed windows are cleaned up.
- Editor/calculator/chat/rooms/help now have distinct SVG graphics in the menu,
  panel and window titles; the previous shared almost-blank icon is removed.
- Running task icons show a count even for one window and keep a running line
  when minimized; active highlighting follows focus. Task lists cover all
  workspaces, and choosing a task restores its original workspace.
- The phone window '^' roll-up control is restored. Applications → Terminal
  always opens another window. These windows still share the same guest serial
  console; independent per-window PTYs/shells are not implemented yet.
- Workspaces are removed from Applications; the top-bar computer icon retains
  the three-preview chooser, selection/outside dismissal, and no Close button.

Local tests: general-voice-result.json PASS with real microphone-file capture,
actual CPU Whisper in terminal and editor, trusted touch press/release, preserved
focus/selected range, another app's cancelled inference, workspace DOM/drafts,
additional terminal windows/counts, roll-up and cross-workspace task restore.
Current touch-preview-result.json PASS covers native keyboard/viewport/menu/
scrollback and desktop mouse regressions. Public versions also PASS in separate fresh
Chrome sessions using default TLS trust; touch and speech milestone receipts
bind the exact assets and current hosting health. Neither automation claims a physical phone microphone test.
User confirmed the previous CPU voice R2 worked on their S25; R9/R3 still needs
fresh-device feedback. Save/download ephemeral guest files before refreshing.

Current hosting pins:
- generator `137f767bff1fe247b8cda574bc6710c63fc1a7d441064fbf6c00a3fc129cbd96`
- manifest `5e56e78ea5f6a83a77650032d94304fe95b1f53d2b0394c767b0fd61beee0fb3`
- derived Caddy `e1b1ad42f6a80a3d0d27e167ea31d2bb654f264f20867f231f7870c608588199`

Root activation receipts are frontend-51ae4707d020ff04885cdcfdc2b16c762c2bb156b6285122b2c5e63d8e578e1e-activation-result.json
and speech-df759266dbd1cc339c4cd96df8265e274b9b9042abef275d00fc0809deed1f3b-activation-result.json under
/srv/codi-connected. Immutable assets are under frontends/<frontendSHA> and
speech/<speechSHA>. Frontend rollback to R8 while keeping R3 speech uses
/var/backups/webhost-sites/change-20261023T033136965701Z/common.py and
/var/backups/webhost-sites/change-20261023T033136966164Z/sites.toml. R8-to-R7 inputs remain
/var/backups/webhost-sites/change-20261023T032619588310Z/common.py and
/var/backups/webhost-sites/change-20261023T032619588759Z/sites.toml. The earlier speech rollback to R2 uses
/var/backups/webhost-sites/change-20261023T032537873812Z/common.py and
/var/backups/webhost-sites/change-20261023T032537874722Z/sites.toml. If fully reverting both, restore frontend
first then speech (the old frontend is compatible with R3). Use the controller
lock, exact pins, generated Caddy validation/application and all8-site/prototype
checks; never hand-edit Caddy. Caddy reload can close existing WebSockets.
No router, firewall, port, native code or boot-policy change. Public TURN OFF;
full networking/login roadmap remains unfinished. Earlier R2 details below are
historical; current receipt names for voice are general-voice-result.json and
general-voice-public-result.json, bound by speech-milestone-result.json.



## Relay operator2 verification before keyboard/voice follow-up — 2026-10-23

Local patched Coturn4.18.0 persistent lifecycle12checks PASS. Corrected flags
(dtls=0/cli=0/tlsv1=0/tlsv1_1=0) show no unknown/deprecated config warnings and
only private TCP/TLS listener. Exported5-file operator2 at
active-system/.build/relay-operators/persistent-turn-20261023-r2,
manifest53ad5058662dbb0113caf43b900bcb77cbfdf0923e62477f899abe006d56c52b.
Certificate-source helper now proven with8actual installed-unit/provider checks:
separate owner0700/0600, symbolic/readable/writable provider refusal, real root
oneshot refresh, active rotation/no-op PID preservation, wrong-SAN refusal,
expired installed-generation renewal, hourly static timer armed (not waited
for a full hourly firing). Root refresh job needs CAP_DAC_READ_SEARCH solely
to read Caddy-owned key; TURN/proxy capabilities remain empty. Protected root
venv/operator used by actual job; all fixture units/state cleaned afterward.
Adapter now includes certificates.py. Full read-only native9 dea2b7d... +
managed patched relay actual Chrome relay/relay TLS chat, separate chess,
identity/root renewal/steward crash/guest Internet PASS; cleanup completed.
Current receipt full-system-hidden-readonly-release-provisioned-private-turn-network-result.json
(no managed-relay tag). Persistent-relay milestone now binds these6receipts and
unchanged live R9/nativef2 health. It will need fresh pins if frontend changes.

Nothing installed on webhost yet; publicTURN/sharedingress OFF. Server CaddyUID997
provider directory /var/lib/caddy/.local/share/caddy/certificates/acme-v02.api.letsencrypt.org-directory/turn.ksu.codes
contains matching cert/key mode0600 owned997. Existing installed root venv517179c
has no unprotected files and can support operator cryptography. Webhost missing
libevent core/extra/openssl/pthreads2.1sonames; apt package candidates are
libevent-*-2.1-7t64 version2.1.12-stable-9ubuntu2.2. No apt install executed.
Next relay work: reviewed Git-first operator/runtime bundle sync, install needed
four libevent libraries, protected immutable runtime/operator installation,
configure private relay + bind Caddy provider + install explicit static refresh
job/timer, then shared80/443 ingress/native9 policy/public/WAN proof. Source
Git currently stillf1f3933R9; new operator is only local, not pushed/installed.

User steered work back to UI: tap-to-start/tap-to-stop voice instead of holding,
change mic icon during recording, optional on-screen keyboard suppression for
voice input. Implement/deploy only hidden frontend; preserve prototype/native.


## R10 tap voice, keyboard mode and draggable overlay — 2026-10-23 03:48 UTC

Frontend R10 `843731014475a1344f5191b9485dd2f7eb179b54d0c73d1edfb896576af14e0f` from source/server
`2af147b3f5a5be3de3916793b144f86c2b1b58a0`. Speech R3 remains
`df759266dbd1cc339c4cd96df8265e274b9b9042abef275d00fc0809deed1f3b`.
The user corrected the gesture: tap starts, a second tap stops and inserts the
finished transcript; holding is not required. Mic switches to a stop square
while recording, then returns to the mic. Pending loading/inference can be
cancelled by tapping. Dragging the mic moves the floating controls and never
starts/stops recording. No bottom strip is reserved; the overlay can sit over
an app and the user can move it. Normalized position is RAM-only and is clamped
on visualViewport resizing/rotation; its temporary message is clamped too.

Voice mode is the default. Editable fields receive inputmode=none, without
readonly/disabled changes, so cursor selection, dictation and hardware typing
remain available. The floating keyboard button restores each field's original
input mode and focuses the remembered field; toggling off blurs the current
field to dismiss an already-open keyboard. Starting voice also switches an
explicitly enabled keyboard back off. The terminal's existing Keyboard button
re-enables typing mode before focusing its native field. Existing and newly
created fields share this policy; preference stays in this browser session.

This uses the [standard inputmode none behavior](https://html.spec.whatwg.org/multipage/interaction.html#attr-inputmode-none).
Inputmode is a browser input hint; desktop Chrome automation verifies exact
attributes, enabled/focusable fields and toggling, not the physical phone OS
keyboard's visibility. S25/Chrome feedback is still needed for that last claim.
No browser-wide or other-site keyboard setting is changed.

Local general-voice-result.json PASS covers actual CPU Whisper from microphone
fixture capture with trusted touch taps in terminal/editor, changed recording
icon, previous focus/selection, default none mode and keyboard toggle, cancelled
inference, real drag with no new microphone stream, and viewport containment.
Touch-preview-result.json PASS covers all prior native terminal input, menu,
workspace/task/roll-up and desktop mouse/keyboard regressions. Public receipts
and aggregates bind the served assets separately. A first overlay resize check
asserted immediately after CDP metrics changed; the retained failure is
voice-overlay-resize-immediate-assumption-before-result.json. Waiting for the
actual resize event gives a clean PASS. No product change hid that failure.

Current hosting pins:
- generator `137f767bff1fe247b8cda574bc6710c63fc1a7d441064fbf6c00a3fc129cbd96`
- manifest `1a9db555d075a997c14273c04a05c359bfa482c3efaf5454f1aa5801b948203b`
- derived Caddy `f6f097d53683b67e8d216163ae10856c8b1a381ef65c2573f10321962de4f231`

Root receipt: /srv/codi-connected/frontend-843731014475a1344f5191b9485dd2f7eb179b54d0c73d1edfb896576af14e0f-activation-result.json.
Rollback to R9 (old hold gesture / no keyboard switch) uses
/var/backups/webhost-sites/change-20261023T034834237973Z/common.py and
/var/backups/webhost-sites/change-20261023T034834244049Z/sites.toml through the hosting controller lock,
pins, generated validation/application and all8-site/prototype checks. All native
PIDs/config/index/cookie, current website and /desktop remain unchanged.
Public TURN/shared ingress still OFF. Caddy reload can close WebSockets;
unchanged PIDs/RAM do not prove uninterrupted streams. Speech still runs on
the visitor CPU with no audio upload; full networking/identity goal unfinished.


Public general voice/touch Chrome tests PASS with ordinary certificate validation;
current touch/speech aggregates and all8-site/native health PASS. Automated
checks still cannot display a physical Android keyboard; user feedback needed.
Relay operator2 local milestone also refreshed against current R10 live health;
it remains local/source-only, not installed or public.


## R11 independent workspace panels — 2026-10-23 04:04 UTC

Latest user direction supersedes R8–R10 cross-workspace tasks. Each workspace
shows only its own app icons, counts and window picker; pins are per workspace.
Empty workspaces inherit no Files/Terminal/Text shortcuts. Applications opens
new instances in the current workspace. Minimize/restore/close affects only
that workspace's count; switching retains existing app DOM, drafts and cursor.
Multiple terminal windows still view the shared guest serial console; separate
PTYs/shells and separate filesystems are not added by this panel change.
Tap-to-start/stop voice, red stop icon, default voice keyboard policy, floating
keyboard toggle and draggable overlay remain included.

Live /hidden frontend R11: `d6b62247203795f680d549d8064a27c37f0ed12f25e3b8ead0b4b069eb4dbc4a`
Source/server checkout: `08c8af907a21f5805a317c6ad3d85c5a10a5908d`
Speech R3 remains df759266dbd1cc339c4cd96df8265e274b9b9042abef275d00fc0809deed1f3b.
Hosting generator: `b4d9a6045cbd10d94f083010b7b1995cd30a80df5234e3ce122da1591aeffcbf`
Manifest: `fc754d7910c986ebbd5c545094acd6f6fe8d6a7227439e83d5450f8c4b47de3d`
Derived Caddy: `3eec189f42a74ee4f9f7c3b9381f56c03b0917fcbe56bd08394b20c9d41536f1`
Root receipt: /srv/codi-connected/frontend-d6b62247203795f680d549d8064a27c37f0ed12f25e3b8ead0b4b069eb4dbc4a-activation-result.json.
Scoped rollback to R10, PRESERVING the new ninth Cardboard site, uses
/var/backups/webhost-sites/change-20261023T040429615138Z/common.py and
/var/backups/webhost-sites/change-20261023T040429615621Z/sites.toml through hosting controller lock/pins,
generated validation/application and all9-site/prototype checks. Older R10
rollback inputs predate Cardboard; do not restore those over the current site.
/desktop hashes, nativef2 services/PIDs/config/index/cookie and website release
remain unchanged. No ports/router/firewall/boot changes. Public TURN still OFF.
Caddy reload may close existing WebSockets despite unchanged native PIDs.

Local Chrome general voice/workspace and touch+desktop checks PASS. Workspace
checks exercise terminal counts3/2/4, no inherited app icons, local picker,
minimized restore, independent pinning, close count and preserved drafts/cursor.
Public general-voice/touch Chrome checks PASS with ordinary TLS trust. Current
touch/speech aggregates bind exact R11 served assets and all9-site/native health.
The relay aggregate also binds this current health; its relay remains source-only.
Automation covers touch emulation, not actual physical Android keyboard display.


Networking continuation checkpoint: operator2/runtime source f9a4894 is now in
the clean server checkout08c8af9 but still UNINSTALLED/unactivated. Four libevent
runtime libraries2.1.12-stable-9ubuntu2.2 are installed; root receipt
/srv/codi-connected/relay-libraries-install-result.json and local check copy
prove all9 web/Caddy/native PIDs unchanged. No Coturn/HAProxy services installed.
New active-system/scripts/install-webhost-relay.py is UNTESTED/not run. Review
and dry-run it before apply; do not infer an installed relay from source or
libraries. Private relay/cert job, shared ingress, native9/public TURN and
independent WAN proof remain outstanding. Full goal is unfinished.


## Persistent private relay installed — 2026-10-23 04:08 UTC

The private relay is now INSTALLED/running on box-webhost. This supersedes
prior source-only/missing-library notes. No public ingress or issuer TURN policy
was changed; /hidden R11, /desktop and all9 sites are preserved.
Operator: /srv/codi-relay/operators/53ad5058662dbb0113caf43b900bcb77cbfdf0923e62477f899abe006d56c52b
Runtime: /srv/codi-relay/runtimes/69ce8817cef7b4a1d99a30be1d5548e92eb0bfeaa2ee6ae6fb165180a5ea4e4b
Config/private keys/shared secret: /etc/codi-relay/ksu (root0700/0600).
Host socket ONLY127.0.0.1:13479; private relay127.0.0.2 UDP13500..13627 in
loopback-only namespace net:[4026532488].
Workers: turnPID209387 UID65179, proxyPID209395 UID64693; no caps, NoNewPriv.
Do not regenerate/rotate/export the secret implicitly or print credential files.
Root receipt /srv/codi-relay/ksu-private-relay-install-result.json.
Local receipts webhost-private-relay-preflight/install/health-result.json and
relay-libraries-install-result.json under active-system/.build/checks.
Actual default-trusted TLS and unauthenticated TURN401 PASS; namespace probes
get ENETUNREACH toInternet and ECONNREFUSED tohostissuer. Existing services/PIDs,
index/cookie/nativeconfig/hosting/prototype bytes remained unchanged during install.
Current CardboardPID206905 predates this install; earlier source notes had200332.
Caddy cert expires2027-01-21T00:01:42UTC. Static certificate-refresh job has only
CAP_DAC_READ_SEARCH; workers have none. Its timer is active, actually triggered
at2026-10-23 00:08:57EDT and job PASS, unchanged relayPIDs; next interval hourly.
All5 new relay/cert units are static, not boot-enabled; native units still disabled.
Use installed venv517179c with installed operator scripts/manage-relay.py and
--directory /etc/codi-relay/ksu for status/stop/start/refresh-certificate/recover.
Existing native controller/roles remainf2fbd4d/schema2; full goal is unfinished.

Shared ingress work IN PROGRESS: built HAProxy2.8.31 (official current2.8 branch,
archiveSHA8f2dd09cfdfe42bdc982c8615e7acb858e1815b10f296dfe5560e7f314dc6c80,
HTTPS/hash pin, NO upstream signature verification). Local runtime manifest
7bbd7877cd64bdb10cd170d4a0d0bdf1e11e6b186a329b7564735951090f59f8,
binary85022f20d5a4c44efbd3fd3ae97ab87e1ce8ad5e81b2442bbc65a7ab6e13b947.
Not pushed/installed/activated. New ingress_service/configuration.py,
prepare-shared-ingress.py and managed-ingress-check.py are under development.
Candidate .build/hosting/shared-ingress-20261023-r1/candidate was prepared before
Type=exec renderer change; regenerate a NEW candidate before activation.
Public80/443 still owned by existing CaddyPID12545; shared ingress remains OFF.


## Shared public80/443 ingress LIVE — 2026-10-23 04:32 UTC

The shared ingress is now INSTALLED/ACTIVE. This supersedes earlier TURN-OFF,
source-only and no-boot-change notes. HAProxy owns existing public80/443;
CaddyPID12545 serves ONLY127.0.0.1:8080/8443. Existing9 sites' blocks/policies,
/hidden R11 assets/index/cookie, /desktop bytes and native/private-relay PIDs
were preserved. No router/firewall or extra public-port change.
Source/server checkout 8935631f42ef5c86a4ec53f1e641fccd02f0da15.
Generator: df5827fe98ac47f21bdf094c5fbba51b666d63e77f4bf300e24615857ad448fc
Manifest: 599370a351df7097a3d7b24fdbabc065a6f582cbb07e4938e67dc5276584d849
Derived Caddy: 4027c7ea30b7b19270bdd87ab8c8966c8bd8d7c09700e3c87a1a75b99710c6c4
Root receipt /srv/codi-ingress/ksu-shared-ingress-activation-result.json.
Root runtime /srv/codi-ingress/runtimes/7bbd7877cd64bdb10cd170d4a0d0bdf1e11e6b186a329b7564735951090f59f8.
HAProxy2.8.31 PID218522 UID61306, NoNewPriv, ONLY CAP_NET_BIND_SERVICE,
strict filesystem, private runtime stats socket, root-owned config
/etc/codi-ingress/haproxy.cfg. Unit codi-shared-ingress.service is static,
WANTED by existing boot-enabled Caddy through caddy.service.d/30-codi-ingress.conf;
it follows ordinary Caddy starts. Native issuer/steward/guest remain disabled,
relay/certificate units remain static. An actual machine reboot was NOT tested.

Routing: normal HTTP/TLS -> Caddy with PROXYv2; ACME ALPN routes to Caddy FIRST;
turn.ksu.codes SNI -> private TURN socket127.0.0.1:13479. Public TURN TLS listener
is ON and default-trusted TLS/anonymous401 PASS. Issuer TURN policy is STILL OFF
(native f2fbd4d/schema2); visitors do not receive relay credentials yet. Local
forced relay browser proof exists, but public authenticated allocations/RTC and
independent WAN/NAT proof remain open. Physical-phone mic/keyboard display are
not automated claims. Fresh public voice/touch+desktop Chrome checks PASS after
cutover, with exact assets and ordinary TLS trust; all9-site smoke PASS.

Rollback/recovery from DEVELOPMENT WORKSPACE: python3 -B
active-system/scripts/activate-shared-ingress.py --rollback or --recover.
Private durable state/history /var/lib/codi-ingress; never erase a pending
maintenance.json or keys. Prepared recovery restores old hosting; committed
recovery preserves the new one. Actual webhost prepared rollback, interrupted
preparation recovery and committed forward recovery PASS. Exact restore function
also reopened actual old local Caddy listeners with the proxy stopped/running.
Old frontend/speech/hosting backup files CANNOT be restored directly while
shared ingress owns80/443. Use a fresh scoped frontend/speech candidate from the
CURRENT generator+manifest, or coordinated ingress --rollback (guarded against
later hosting/native config changes). Never hand-edit derived Caddy.

Current local receipts: shared-ingress-apply/exercise-rollback/stage-recovery-test/
recover-result.json, managed-ingress-result.json, preview-touch-live-health-result.json,
webhost-private-relay-install/health-result.json under active-system/.build/checks.
The stage-recovery receipt is historical; current maintenance.json is absent.
Public ingress health/ACME routing audit PASS; shared-ingress-milestone-result.json
binds exact sources, recovery, all9 sites and current Chrome/native health at04:42UTC.
Next required work: guarded native9/schema3 upgrade preserving authority/accounts/
guest state, bind the existing relay secret through native protected custody,
issuer short-lived credentials, trusted public forced-relay chat/separate chess
and real independent-WAN proof. Full goal remains active and unfinished.


## Source synchronization and independent homepage update — 2026-10-23 04:49 UTC

Latest source/proof checkout on box-webhost and deployment clone is
1b10475c1741391a003cfbc019eeff11f730e064, clean. The ingress itself was applied
from8935631; its code/runtime/config are unchanged. An independent homepage
Cardboard-guide update landed as12af5f8 during this work; it was preserved by
rebasing only the four ingress evidence/source files, without force-pushing.
The active main website is now /srv/webapps/ksu.codes/releases/20261023T043853468523Z-314447db,
web-ksu-codes PID220919. That independent website deployment happened AFTER
ingress activation; earlier all-PID-preserved receipts describe their own
installation windows, not a promise that unrelated website PIDs stay fixed.
Caddy12545, ingress218522, native185140/185141/185562 and relay209387/209395 remain.
/desktop's three original SHA256 values are still exact in the new root-owned
website release. Current preview health and future touch activation compare
those prototype bytes rather than requiring the old main website release name.
Fresh all9-site smoke and all current touch/speech/private-relay/shared-ingress
aggregates PASS, latest shared-ingress aggregate04:49UTC. Public Chrome checks
and public401/ACME/source-IP audit remain bound to exact current frontend/assets.

Native9 upgrade is the next work: .build/releases/connected-turn-20261023-r2,
manifestdea2b7d770b3ddd8f9dc07282d1f5f2ca98c395469b7eee361c2bff4f3cc627e,
165files. It is STILL NOT INSTALLED; installed controller/roles remainf2fbd4d,
configschema2, issuer TURN policyOFF. Existing webhost-code-upgrade.py and some
historical activation helpers still hard-pin the earlier main website release;
inspect/update their guards against this authoritative new state before use.
Preserve current all9-site shared ingress, frontendR11/speechR3, native identity/
account/guest state and explicit root renewal policy (root1 expires22:36:39UTC).
Do not ask again for package/network-test approvals already given. No blockers
remain for continuing native upgrade/credential work; the full goal is active.


## R12 independent guest terminal shells — 2026-10-23 05:36 UTC

/hidden now serves frontend8acbd0f506fddd04ef02499514e0bfa19144937b47afee699cf8deafcf7b4f3d,
applied source5fd4acf3e860a458dc36183a7896d891d437b399. The user explicitly
requires SEPARATE SHELL SESSIONS, not mirrored console windows. Each terminal
now owns a guest PTY and UID/GID1000 BusyBox shell with separate cwd/environment,
foreground jobs and output. Same browser VM and shared guest home. Ctrl+C, typing,
paste and floating dictation target that PTY. Minimize/workspaces preserve it;
exit/close affects only that shell. Up to64 concurrent PTYs per browser VM.

Applications → Terminal always creates another. Running panel icons open a local
window picker with New window, including when only one is running. Phone layout
no longer hides every inactive window; all local unminimized windows remain,
with staggered captions. Other workspaces' tasks/pins/counts remain independent.

Frontend manifest2 intentionally expands the overlay to FOUR files: app.js,
style.css, terminal.js, assets/terminal-initramfs.cpio.gz. The last file carries
the guest PTY broker/devpts setup; the native server controller is unchanged.
Only those hidden asset routes changed through the managed generator. /desktop,
homepage, index/cookie, services/accounts and other sites remain unchanged.
Native roles/controller f2fbd4d/schema2 PIDs185140/185141/185562. Shared public TURN
listener ON, issuer credential policy OFF. No ports/firewall/router/boot change.

Pins and scoped post-shared-ingress rollback snapshots are documented in
active-system/evidence/independent-shells.md (omit active-system prefix inside
that target). Old pre-ingress frontend/speech backups remain unsafe to restore.
Local real v86 distinct PTYs/jobs/file-sharing and phone/desktop checks PASS;
actual CPU Whisper targets an independent workspace's shell and preserves the
first shell. Public checks/aggregate are refreshed separately after activation.
Existing tabs were not reloaded; save/download ephemeral files before refreshing.

Current hosting health chooses the root activation receipt whose exact generator,
manifest and active Caddy hashes match the live configuration; it does not rewrite
the older shared-ingress receipt after a legitimate later frontend deployment.
Earlier full native/ingress aggregates are historical and need refreshed scoped
integration proof, rather than being presented as current R12 integration tests.


## R12 public verification complete — 2026-10-23

Public independent-shells/touch/general-voice Chrome checks all PASS, including
real distinct PTYs, cross-workspace job continuity, local Ctrl+C, shared files,
separate shell cwd/environment/output and targeted CPU Whisper. Public guest
ping/DNS/HTTP also pass from the new terminals. Touch and speech aggregates and
independent-shells-milestone-result.json bind all exact assets/source hashes,
root activation receipt, current hosting pins and nine-site/native health.
No physical S25 microphone/OS-keyboard or independent-WAN claim is made.
/desktop, homepage, native roles/state, index/cookie and shared ingress preserved.
See active-system/evidence/independent-shells.md for exact live keys and rollback.
The broader networking/login goal remains ACTIVE and unfinished.


## Native10 applied — 2026-10-23

The actual managed configuration and all three online roles now point to
/srv/codi-connected/releases/native10-ced620b043b7054c, manifest
ced620b043b7054c17e4d943a987f8b3f959c21f63961894091b6088cbbd9058.
Applied source3867c214f96b9ad5471a308205b9c35dca99f925. Config is still schema2;
TURN credential policy has NOT yet been enabled at this checkpoint.

Six existing account records, issuer/root/service keys and root authority
state were preserved; no data restore or authority renewal. The existing
RAM-only guest cookie was copied once into protected persistent custody at
/var/lib/codi-connected/guest-cookie-codi-ksu-hidden/secret. Never print or copy
it into source/public files. Root700 directory/file600, systemd read-only
LoadCredential for the guest. It matches the actually running guest cookie.

Root rollout controller d30b47ce185d5f4bd6cbbbc12671c2f0d248e01768524cfebcf401f10eb97b88
is installed under /srv/codi-connected/rollout-controllers/<SHA>/native-rollout.py.
The managed CLI in the new release is now the operative controller; f2fbd4d is
retained only as previous code. Native units stay disabled for boot and bootstrap
stays stopped. Native PIDs after switch: issuer224434,steward224438,guest224440.

Coherent checkpoint /var/backups/codi-connected/ksu/native-f41503dfd36e841af3bd8c1d144870b6,
manifest9332d5de3e9725505aa881f55aa4a3eb50a45ecd689407ca0b3107417fb5fb0a.
Guest PID/cookie remained unchanged during checkpoint; all roles were then
restarted for code activation, preserving the same guest cookie. Outer/inner
maintenance journals are absent. Current browser VMs were never reloaded.

Root apply receipt /srv/codi-connected/native10-upgrade-1792735550239811681-result.json,
SHA30fcc096053c571eb8338a7caeb3c3fc7d9b36386e2070d52715bf10205601ed.
Old profile8 rollback can lose cookie continuity if the guest is restarted;
never restore old account data just to undo code. Normal10 restarts preserve it.
Issuer renewal sessions still live in RAM; the restart invalidated those
sessions, while account subjects/password records/signing keys were preserved.

R12 app/style/terminal/guest assets, speechR3, homepage, /desktop and managed
shared ingress remain exact. Only the candidate bootstrap's viewport resize
hint and identity client policy support changed among other public assets.
The new bootstrap SHA is f3687dbb17e859237142c44424c8a2ec8ca741ac9d267b63ed85f62e99ed4c7c.
Caddy/generator/manifest remain the R12 pins; no router/firewall/port/boot change.

The full local native10 read-only stack now passes with actual source/runtime
provenance: observed HTTP assets are compared to the frozen release, native
executed files have separate hashes, and only actually run test programs use
working-tree source hashes. It tested the frozen R11 frontend, not the live R12
overlay. See the public R12 tests separately after native activation.


## Issuer TURN credentials and public relay working — 2026-10-23

Managed config is now schema3 on the same native10 release. Issuer PID225003;
steward224438 and guest224440 were NOT restarted by the policy change. The
protected existing TURN secret remains /etc/codi-relay/ksu/turn.secret; no secret
was rotated/printed/copied into public assets. Public endpoint is
turns:turn.ksu.codes:443?transport=tcp, currently relay-only for verification.
Root policy receipt /srv/codi-connected/turn-policy-apply-1792736043218406886-result.json,
SHA79653e919ed7b99b12ad9ba4b5a1bc9c005d132a67d329641c4b9ec083c2d5f4.
Six accounts/authority/keys, guest cookie/PID, other role PID and hosting preserved.
No new public ports/router/firewall/boot changes.

Actual public HTTPS Chrome pair PASS with default trust: authenticated ICE
relay/relay candidates at127.0.0.2 using TLS and private13500..13627 allocations,
bidirectional RTC chat, separate room chat/chess e4/e5/Nf3, continued traffic
without signaling, identical PGN exports excluding chat, guest ping/DNS/HTTP,
identity/VM continuity and clean disposal. Receipt public-authenticated-relay-result.json.
This is from the development network through the public hostname, NOT an
independent-WAN/NAT proof. All nine production websites pass fresh smoke in
reports/private/codi-native10-20261023.json on box-webhost.

The first public checker runs reached final asset provenance collection but
used the loopback fixture CA there; no success receipt was written. Collector
now uses system trust for public runs and records a failed provenance receipt
instead of leaving a previous PASS. Clean rerun above PASS. Current TLS checker
SHA14ad8d8c161cb883d5bd7f9a7c6d79a6027a6d916a8bc4fdea8fa901da86c4f8.

Remaining: refresh public touch/voice/independent-shell checks and aggregates on
native10/schema3, link fresh nine-site/policy proof into current health, publish
these final source/evidence changes, then direct ICE with TURN fallback policy,
independent WAN proof, restart-resilient issuer sessions/guest-cookie renewal,
and the rest of the full v0.1/v0.2/v0.3 requirement audit. Do not mark goal done.
Automatic rollback to old profile8 is not supported while metadata is schema3;
use a compatible10 rollback or a reviewed coordinated policy/metadata rollback.
Never restore old account/authority data to undo code. Keep /desktop unchanged.

User asked about reach/access restrictions. Verified live guest server SHA
c5d792185dc01cd58e95b68c0af3a924265013d7a55450c8e27cb3d9c7518770:
permitted_frame(preview=True) allows public IPv4 ICMP echo and TCP80/443, plus
UDP53 only to synthetic DNS10.86.0.3. Private/loopback/link-local/shared/multicast
IPs, IPv6, other protocols/ports, fragments/options/source-spoofing are blocked.
This is a packet filter in the service; it is NOT a separate host egress firewall.
Own public WAN IP is still classified global and allowed; ports80/443 do not
restrict content/protocol and can carry public proxies/tunnels. Normal browser
tabs use visitor Internet. TURN chat/game forwarding is separate, private-loopback
namespace/no-uplink, allowing peers only127.0.0.2. No destination allowlist/admin
policy UI has been implemented or selected yet. Do not silently change the
outbound policy just because the user asked how the limits work.


## Gateway/access-control layer APPROVED and important — user direction

The user explicitly approved the gateway/access-control layer as a core
requirement. They want controlled internal AND external resources: selected
internal read-only file shares, selected websites, access rules and speed/usage
limits per user/use. This extends the active networking/identity objective;
keep /desktop unchanged and do functional work only in active-system/hidden.
No specific private folder, internal host or recipient account has been chosen.
Do not expose a host filesystem or open general LAN access without that mapping.

Implementation direction: a managed default-deny resource policy with narrow
explicit service exceptions, independently enforced host egress restrictions,
a read-only file broker (server-side permission enforcement, never trust client
read-only flags), and identity-bound quotas/rate queues keyed by stable account
subject and resource. Anonymous sessions need separate caps; do not claim they
are reliable per-person identity or that reconnecting must reset account quotas.
Current global Origin+guest-cookie gate is NOT identity-bound and must be
extended before claiming per-user gateway enforcement. Current TrafficBudget
terminates excess traffic; smooth speed control requires real pacing/backpressure.

Website/path/method controls need an application proxy/broker; raw IP/port rules
cannot distinguish all virtual hosts or enforce read-only file operations.
Keep private LAN and own WAN address blocked for raw guest access, and expose
selected internal shares through the broker with only the approved root/actions.
Read-only protects originals; downloaded copies remain editable by the visitor.
Browser-local computation and ordinary new tabs do not pass through this gateway.

User also asked what browser apps can do, specifically build123d/WebAssembly.
Verified primary sources on2026-10-23: OCP.wasm ports build123d dependencies using
Pyodide; Yet Another CAD Viewer offers a fully in-browser build123d playground
and static deployment; replicad offers a JavaScript/OpenCascade-WASM alternative.
Sources: https://github.com/yeicor/OCP.wasm
https://github.com/yeicor-3d/yet-another-cad-viewer
https://yeicor-3d.github.io/yet-another-cad-viewer/
https://build123d.readthedocs.io/en/latest/external.html
https://replicad.pages.dev/docs/use-as-a-library/
Use a browser-native CAD window alongside v86 and the shared file bridge, with
visitor CPU/RAM and explicit file/gateway capabilities. No CAD package has been
integrated or benchmarked locally/onS25. No promise of arbitrary native binary
compatibility or unrestricted host files/network/hardware. Gateway stays ahead
of CAD integration; no graphical game work is authorized ahead of network/login.

Local WIP before this steering: activate-turn-policy.py now accepts --transport-policy
all|relay (defaultall); tls-discovery-check.py has --force-relay and --expect-direct
for testing direct and relay paths under a signed all policy. These edits are
LOCAL, untested/unpublished, and were NOT applied. Actual live policy remains
relay, source/server checkout4708ae27d053e3f7cc2c05a06c3425acd21a29b4.
Complete/verify that transition when returning to it; never claim it is live
from the local helper default. No background checks are currently running.


## Registered-user persistent folders approved; Linux account question

The user explicitly requested save/write access with ONE UNIQUE PRIVATE SERVER
FOLDER PER REGISTERED ACCOUNT, NONE FOR ANY ANONYMOUS USER. Preserve temporary
browser/v86 files for anonymous users; never allocate an anonymous server home
or grant anonymous persistent-save rights. This authorizes controlled personal
storage for active-system, not changes to /desktop or a blanket mapping of host
home directories. Shared read-only resources have separate explicit ACLs.

Use the existing persistent web-account subject (user:UUID), not a client-chosen
username/path, guest Linux UID or session ID, for each personal storage namespace.
Same account on another device/session reuses its folder. Per-user quotas must
also use stable account subject across sessions. Personal files are private from
other accounts. Write/create/update and quota enforcement happen on the server;
client-visible read-only/hidden buttons are never authorization. Safe atomic
saves, content/version preconditions, traversal/symlink/hardlink refusal and
storage/transfer quotas are required. Anonymous certificates must fail before
any server-folder creation. No actual private share path has been selected.

User asked whether Linux accounts could handle usernames/passwords. Recommended
reusing the already implemented web accounts/password hashes and mapping their
stable subject to storage. Host Linux service accounts enforce process/storage
boundaries. Browser v86 Linux is visitor-controlled and is NOT an identity
authority. Linux PAM could integrate existing host accounts, but does not remove
web-session/resource-policy/quota work and is not needed for these public web
registrations. Existing server code uses salted Argon2id password hashes in
private SQLite state. Do not copy passwords into guest Linux or create host
interactive logins for website registrants as an unrequested convenience.
No identity migration to PAM has been requested or implemented.

Local gateway WIP started: gateway_service/__init__.py, policy.py and files.py.
Policy is a strict operator-owned resource allowlist with ACL/limits, pinned
HTTP destination IPs, explicit private-address exceptions for brokered HTTP,
own-WAN refusal and read-only file roots disjoint from private/control trees.
ReadOnlyShare uses descriptor-relative O_NOFOLLOW/O_RDONLY and refuses links,
special files and traversal. These files are UNTESTED AND NOT EXPORTED/DEPLOYED.
They currently implement only read-only file/http policy primitives. Do not claim
personal save, quota accounting, signed gateway grants, file HTTP service, OS
egress firewall or per-user guest network enforcement exists yet. Next build
identity-bound one-use authorization, durable quota/pacing, registered personal
storage, broker transport, native lifecycle/firewall and UI integration.

Planned issuer integration should keep credential checking in the existing
issuer and resource access in a separate gateway role. A dedicated gateway
identity-confirmation endpoint can reuse live session/key/account-generation
checks and sign short-lived, request/nonce-bound confirmations; gateway applies
its own ACLs and verifies client proof. This avoids trusting detached browser
Linux users or granting general LAN access. Preserve disabled-account semantics
and explicitly bound any in-flight authorization lifetime. Issuer restart
resilience remains unfinished and matters for long-lived gateway access.

Primary docs checked for the account discussion:
https://github.com/linux-pam/linux-pam/blob/master/doc/sag/Linux-PAM_SAG.xml
https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html


## R13 optional accounts and private storage foundation — 2026-10-23 07:35 UTC

Latest user approval: retain issuer SQLite for logins/passwords, use a separate
permissions database, and ordinary disk folders keyed by stable registered
account ID. Anonymous users get no persistent server folder/save grants. The
user then requested default anonymous startup and Register/Sign in behind the
TOP-RIGHT Anon button. This optional account menu is now live on /hidden/ only.
Register and Sign in are distinct signed operations; unknown-name sign-in does
not create an account, and registration never signs into an existing account.
Button becomes username after authentication; Sign out returns to Anon without
restarting Linux or discarding editor DOM/drafts/shells/files. Old network links
end on identity switch; open Chat/Rooms windows retain read-only text/drafts and
selected room PGN/chat download snapshots. New network windows use the account.
Refresh starts anonymous. Phone label Anon is visible; explicit Keyboard action
in forms works with the existing voice-mode preference. Test identity labels stay.

Live frontend R13: 5692a7b561749a049b7ece80880537174fd970036b5e64e3a892b8a6838b4481.
Source f3ead519333bd81e2b0680420c9440f69d92d8fd. Operative controller AND roles:
/srv/codi-connected/releases/native10-7705a87e09c44e22, manifest
7705a87e09c44e22be792f91133a24dbd52f4af9e418d6df66978440570c5625 (189 files).
Config stays schema3; TURN stays relay, same secret/443 shared ingress. PIDs
issuer227448/steward227450/guest227451. Guest cookie, six existing accounts and
authority/keys preserved, no data restore. Code restart invalidated RAM issuer
sessions; no user browser tab/VM was reloaded. Native units still disabled boot,
bootstrap stopped, ping range1000..1001, forwarding0. SpeechR3 unchanged.
Native root receipt /srv/codi-connected/native10-upgrade-1792740426865185377-result.json,
SHA70452b2d2bb378fcc4f9057ef514e3d5906ae6d0dcef76507e56fa81b3c9b976.
Checkpoint native-9e463a785b4ffadd18b40700bd95f94b under /var/backups/codi-connected/ksu,
manifest17219d0bbde7d6b86204f064f6f3352001464f222329c5e45239559138be5abb.

Current hosting pins: generator8095d2a6387da16f1e64678f6d074e41990af74c3ae9f549869f13ab3daaf430;
manifest e7fdf5f87554bf1297b374a3af991b070903938482390c614f3be5b2a989e6c9;
Caddy202e5d6d73d156436b20b4b4582eec0de9b161d902e8e47b96845436f3582dae.
Four-asset overlay and native networking.js provide the new UI. Frontend rollback
to R12: /var/backups/webhost-sites/change-20261023T072716491689Z/common.py and
/var/backups/webhost-sites/change-20261023T072716492163Z/sites.toml. Use hosting
lock/current pins/generated validate/apply/all9/prototype workflow, never edit
Caddy. These backups retain ingress; old pre-ingress backups are unsafe blindly.
R12 works with new native10. Code rollback must use compatible10 and preserve
current account data, never legacy8 or restoring stale data. Current rollout
helper is scoped to R12->R13 baseline, not a general future-upgrade command.

Locked codi-gateway service account UID978/GID972 is PREPARED, no listener/unit
started. Root-owned immutable storage bundle3592435b52b95933d1bd0d9eb4349f0b8f3e287614fa31a4e40f0baa8bd31b62
at /srv/codi-gateway/releases/<SHA>. Separate permission DB is
/var/lib/codi-gateway/ksu/permissions.sqlite3; data root
/var/lib/codi-user-files/ksu/users/<canonical UUID hex>. State/data700, files600.
Gateway cannot read issuer credentials; issuer/steward/guest/Caddy cannot read
its private DB. Root selected only active registered IDs read-only; there were
zero active accounts (six historical disabled fixtures), so zero personal folders
or grants were allocated. Anonymous paths cannot allocate a home. Low-level
storage uses durable folder bindings, ACLs, quotas, version preconditions and
atomic saves. Trusted server verification MUST produce Principal before use;
no browser authorization/API exists yet. No automatic new-account folder creation
or Files/terminal server persistence has been connected. No private shares exposed.
Storage root receipt /srv/codi-gateway/storage-prepare-1792739643987217370-result.json,
SHA5305dc863e2878e6a1cc51df3cc0f6487d13cccb604b709abfd531f4d68dc872.

PASS:29 actual disk/SQLite storage tests including process deaths and races;
88 issuer tests; exact frozen release plus public trusted Chrome optional account
UI for desktop/mobile; fresh public touch regressions, actual CPU Whisper and
independent PTY tests including guest ping/DNS/HTTP; all9 sites/prototype/native
health. Two new public account-menu fixtures disabled after testing (historical
records retained); no active fixture account left. Current aggregate is
active-system/.build/checks/account-menu-milestone-result.json. Older R12 aggregates
are historical. Physical Android keyboard/mic and independent WAN remain unproven.
Evidence: active-system/evidence/optional-account-menu.md and private-user-storage.md.

Remaining full-goal work: identity-bound gateway grants/API, durable quotas/pacing,
new registered-account home allocation and actual Files save/load UI, external/
internal allowlist broker plus OS egress enforcement (own WAN still allowed by
old raw guest policy), independent WAN proof, tested direct ICE/TURN fallback
(current live policy relay), restart-resilient issuer sessions/cookie refresh,
and full roadmap audit. Root1 expiry2026-10-23T22:36:39UTC, explicit renewal only.
No router/firewall/new port/production cutover. /desktop and homepage unchanged.
Goal remains active; no claim that server file saves or gateway controls are live.


## R14 personal app templates, real home mapping and next gateway work — 2026-10-23

User reaffirmed optional login AFTER boot: keep Anon startup and the top-right
Register/Sign in menu; attach account storage later without replacing temporary
files or already-saved account files. Do not introduce a blocking login page.
Actual dflanag3 registration was verified enabled; root is reserved and created
no account. Database integrity and live role health were good, no restarts/errors.
The approved private-home bootstrap now maps ONE active registered account to
one private UUID folder and seven ACL rows, NO anonymous folders. New root
receipt /srv/codi-gateway/storage-prepare-1792741023390263846-result.json,
SHA20ebaca4c74d4dc079507612c5ecf20c2a8b37375cb1dfeeaaea6f16794321c1.
Do not disable this real account or treat it as a disposable fixture. Templates
and current Files still use browser RAM; no live file API/save integration yet.

User requested YOUR APP HERE above Terminal for registered users, with multiple
per-user blank templates. R14 is LIVE only at /hidden/: frontend
179a5b5677686c3b2f131aede94639f0f9f0c6c6882a5e83370d8d9f6fc639e9,
source365541faae9fadbf7eb05033641d0e7e4fc162d7. Menu contains Blank canvas,
My notes and My dashboard. Catalog IDs include stable account subject and slot;
windows/drafts/pins/previews/tasks are independent per account and workspace.
Anon and expired identities see no private app entries/windows/pins; another
account sees its own blank instances. Relogin to the same account restores that
tab's models/drafts/pins. UI templates are RAM-only, publicly shipped code and
NOT a server authorization boundary; footer states session-only storage. Real
server APIs must check permissions independently. Guest VM and other app DOM
remain intact through identity switching. No graphical games were introduced.

Native controller/roles stay /srv/codi-connected/releases/native10-7705a87e09c44e22,
manifest7705a87e09c44e22be792f91133a24dbd52f4af9e418d6df66978440570c5625,
schema3. PIDs227448/227450/227451, guest cookie/config, speechR3, root authority,
TURN relay policy/secret, 443 ingress, homepage and /desktop bytes unchanged.
Current hosting pins: generator8095d2a6387da16f1e64678f6d074e41990af74c3ae9f549869f13ab3daaf430;
manifest876ea65da08831f25e05045a47a9d9029d1bec17ea6160b966130ab7043b03ec;
Caddy84bcee138188c9b7aea73950612e366e64a888fc926285f30f989aabd0dc706b.
Root frontend receipt /srv/codi-connected/frontend-179a5b5677686c3b2f131aede94639f0f9f0c6c6882a5e83370d8d9f6fc639e9-activation-result.json.
Rollback R14->R13 through hosting controller lock/current pins/generated checks:
/var/backups/webhost-sites/change-20261023T080059311034Z/common.py and
/var/backups/webhost-sites/change-20261023T080059311523Z/sites.toml. These preserve
shared ingress. Never hand-edit Caddy or blindly restore pre-ingress backups.
No forced reload of any user tab/VM; users load the new frontend on their next
navigation. Refresh still loses RAM-only files/drafts and starts anonymous.

PASS local and public default-TLS desktop/touch template-account isolation,
three templates/menu order/multiple windows/minimized counts/workspace/pins/
drafts/restoration/expiry, public touch regression and actual CPU Whisper, and
all9-site/prototype/native isolation health. Four generated apps_ fixtures were
disabled after testing; real account/files untouched. Aggregate now
active-system/.build/checks/user-apps-milestone-result.json. Earlier R13 aggregate
receipts are historical, not current. No physical Android or independent WAN proof.

NEXT USER NETWORK REQUIREMENT: anonymous raw guest traffic must be blocked from
the operator's own PUBLIC/WAN IP; registered users may ping AND use TCP80/443 to
that IP (explicit choice). Private LAN addresses remain blocked absent explicit
exceptions. This applies to emulated guest traffic, not normal browser HTTPS
loading the site or its authorized file API. Explain that file read/write goes
through an HTTPS443 broker checking account/ACLs, not general LAN access. This
new differentiated IP rule is NOT LIVE: current relay still uses only a global
cookie and permits own WAN as public. Do not claim enforcement until signed
identity binding and fail-closed policy are installed and verified. Registration
is self-service, not host-admin privilege or unique-person verification.

Local/source-only gateway authorization candidate now has24 real ES256/issuer
WSGI/SQLite/concurrency tests PASS. gateway_service/auth.py and
origin_service/gateway_authority.py implement bounded live-session confirmations,
registered-only identity, request/key/SID/nonce/mount/audience binding and durable
one-use challenges/JTI ledger as an EXPLICIT extension in permissions SQLite.
Startup refuses partial/missing ledger, no repair. Live metadata DB has NOT had
this extension installed. Reference PATHS/routes remain untouched. Confirmation
TTL<=30s, never beyond session/certificate; already-authorized exact operations
can finish until expiry after logout/disable, fresh confirmations fail. Checks
cover disabled/generation/logout/wrong key/token/replay/context/body/type/mount/
expiry and preserving existing folder/ACL data. No live launcher imports the
middleware; no route/unit/controller/native changes were made. Tests restart
Python objects, not an actual deployed HTTP/process lifecycle. Issuer sessions
remain RAM-only and restart requires fresh login; do not weaken that by silently
adopting detached certificates. See evidence/gateway-authorization.md.

Next goal work: actual bounded HTTP/client/native gateway integration, private
file read/write and per-user grants/usage/pacing, then identity-bound guest own-
WAN policy + independent OS egress rules. Investigate signed per-connection
WebSocket authorization and preserved v86 RAM during account changes; pinned
libv86 exposes network_adapter.socket and currently handles binary frames only.
New auth frames must not be trusted client flags or leak into the NIC. Keep
resource-specific proof types/audiences to avoid file/network grant confusion.
No internal share path has been selected. Root1 still expires2026-10-23T22:36:39UTC,
explicit renewal only. Direct ICE/TURN fallback, durable issuer sessions/cookie
refresh, independent-WAN proof and full requirement audit remain unfinished.
Full goal stays active. No package/router/firewall/public-port/boot change.


## Private file HTTP and Files UI candidate — 2026-10-23 09:30 UTC

Concrete local progress: registered-only signed file HTTP service, browser SDK,
durable per-account/shared transfer reservations and real backpressure, plus
Files/Server Text Editor UI. Explicit Temporary files/My server files volumes;
private versioned saves, upload/download/delete, guest-to-server Save to server,
and server-to-guest Copy to guest (refuses overwrite). No automatic guest-home
upload or v86 server mount. Signing in/switching keeps guest VM/drafts; server
editor/task ownership is account-scoped and delayed replies cannot populate
another account. Same-account RAM drafts can restore on relogin; refresh loses
RAM drafts but saved server files remain. Templates still RAM-only.

Sealed eleven-file worker .build/gateways/user-files-r4, manifest
 aa2409356d1868ce48579e9dcfb015582dff08b97c1ab30d5c13c586f7e7a05d.
Standalone worker plus issuer/UI/check source are prepared in deployment clone
under tools/codiserver/file-service-candidates/<manifest> and file-service/.
No actual accounts/keys/DB/user files are packaged. Explicit initialization only;
missing/partial authorization/usage schema fails closed. Missing retained
permission DB or issuer signing key/account DB is refused without replacement.

PASS31 storage,90 issuer,26 authorization,8 quota/pacing,11 actual HTTP cases;
real sealed-worker Chrome/WebCrypto at both root and /hidden with full8MiB,
actual SIGKILL/new PID recovery, guest checksum, stale token and other-account
refusal, clock skew and browser-refresh disk persistence. Current Files UI at
both mounts passes real save/conflict/draft preservation, copies both ways,
account and delayed-response isolation, VM/draft retention and saved-file reload;
390px viewport plus trusted emulated touch Save passes. Current local touch
regressions also pass. Aggregate gateway-files-milestone-result.json binds
exact sources/worker/receipts; evidence/private-file-service.md explains scope.
Initial Files selector config-arrival bug was fixed; failed receipts retained.
No physical Android/WAN proof. Existing public R14 receipts remain historical;
do not rerun old aggregates against this different local frontend.

Authorizations must begin within30s, exact operation may finish within120s of
admission and before session deadline. ACL is checked again at CRUD. Logout or
disable denies fresh grants; admitted operation is not instantly revoked.
Default8MiB/file,12MiB envelope,5s idle;100MiB stored/account;512MiB daily
transfer/account,2GiB shared,32MiB/use,2/4 concurrent;1/4MiB/s pacing,64KiB burst.
Payload accounting includes JSON/base64 and can charge failed reservations.
Standard Authorization carries proofs; no custom sensitive log header.

NOT LIVE: no gateway unit/listener, issuer hook, schema extension, routing or
frontend deployment. Live Files still RAM-only. Real dflanag3 home/account and
R14/native10 are preserved; no service restart, user-tab reload, router/firewall,
port or boot change. Own-WAN registered/anonymous rule still NOT implemented.
Current live native PIDs227448/227450/227451 and frontend179a5b56... were checked
read-only, including actual derived hosting equality and /desktop bytes.
Independent hardware.ksu.codes activation advanced shared hosting to TEN sites;
old hardcoded nine-site health helper/activation pins must not be reused blindly.
Observed generator d2d0c07e13e8b074011bcfbb52f22bd786b844a2d9089d3a904638b7305b3502,
sites ef3e223543ca9d4c21ab30b10934b1eb5e86f3c04c2eca0476b9cff3c4be6dc9,
Caddy a57de029e4f1c330255c6d48cfd3941e01c4528abb6def8f81c1f6fa41a86a4d.
Snapshot gateway-live-preservation-result.json is read-only preservation proof,
not a new all-site HTTP smoke. Do not restore old hosting pins/backups blindly.

Next: native11 (freeze V10 allowlist so legacy releases remain verifiable),
explicit issuer enablement/config metadata, managed locked gateway lifecycle,
protected issuer policy pins, backed-up explicit DB extension, safe routing and
compatible matched frontend activation. app.js/desktop-apps.js must be matched;
old R14 overlay alone cannot provide this feature. Test actual installed unit
restart/crash/custody and migration/rollback before /hidden activation; keep all
TEN sites and /desktop untouched. Then signed per-WS guest identity and own-WAN
anon deny/registered ICMP+TCP80/443 allowance with independent OS egress limits.
Issuer sessions remain RAM-only, cookie refresh/direct ICE/WAN and full roadmap
remain open. Root1 expiry22:36:39UTC requires explicit renewal. Goal active.

Source-only candidate was pushed and fast-forwarded cleanly on box-webhost as 01e629fc763fbedeac267c5f3871f65661160db0. The exact worker manifest was verified there; nothing was installed/deployed/restarted. Sync receipt: active-system/.build/checks/gateway-file-source-sync-result.json. Next work remains managed native11/gateway installation and safe frontend/routing integration.


## Private file worker installed; live Files integration pending — 2026-10-23 10:00 UTC

Actual box-webhost installation PASS, Git-first source
f8a851c7f786799553d8a10b9f3276d1ebf6c583. Three-file operator manifest
8fdbbdda508425df7a9f52848b801c7aed44e9db84de643eea27d8fc2bc4f0e7 installed
/srv/codi-gateway/operators/<SHA>; eleven-file worker aa2409356d1868ce48579e9dcfb015582dff08b97c1ab30d5c13c586f7e7a05d
installed /srv/codi-gateway/releases/<SHA>. Existing root venv517179c matches
all dependency pins and is reused. No package install was needed.

New standalone private config /etc/codi-user-files/ksu/managed.json root0600;
issuer-policy.json is root0644 PUBLIC keys/issuer metadata only. No passwords,
tokens/private keys copied. Static units (not boot-enabled):
codi-files-ksu-hidden.service PID236763 UID978/GID972 and
codi-files-ksu-hidden-proxy.service PID236765 DynamicUID63908, plus
codi-files-ksu-hidden-proxy.socket bound127.0.0.1:8140. Worker and proxy share
private network namespace net:[4026532564], distinct unprivileged identities,
zero capabilities/NoNewPrivileges. Actual host/LAN/Internet probes refused;
only loopback exists. Proxy has fixed destination and16-connection bound.
This isolates the FILE WORKER, not the older raw guest Internet relay.

Explicit authorization/traffic table extension is NOW installed in the SAME
permissions DB. Migration backed it up first at
/etc/codi-user-files/ksu/backups/permissions-1792749597164807933.sqlite3,
SHA31efc08dda1a9ecc6cfdd4be85f41d3f6c1805bb0caa367c149a6cb399342d6e,
root0600 beneath root0700 backups. Existing one real registered folder and
seven permissions preserved; zero anonymous folders. No personal file contents
read, no actual account tests/changes. Issuer credential DB remains unreadable
to gateway, and gateway DB unreadable to issuer/steward/guest/Caddy.

Root activation receipt
/srv/codi-gateway/private-files-activation-1792749601333823804-result.json,
SHAce15b04ae6f3e2a799a2122afefec3f3279e1fadb6113ffcff26232e1427b389.
New local receipts private-files-webhost-plan-result.json,
private-files-webhost-apply-result.json, webhost-files-health-result.json and
persistent-files-milestone-result.json prove this scoped actual installation.
Local12 installed lifecycle/HTTP/kernel checks +10 artifact mutation checks PASS
against exact sealed operator/worker. Actual worker SIGKILL recovery, migration
process death, pre-config process death, replay persistence, permissions/home
preservation and drift refusal covered; disposable fixtures fully cleaned.
Exporter path traversal/parent-symlink guards hardened. Prior failed receipts
retained. Native11 has NOT been started or implemented by this milestone.

Public /hidden remains R14 frontend179a5b56... and native10-7705a87e... schema3,
PIDs227448/227450/227451 unchanged. Public default-TLS GET gateway/client.mjs
and POST api/v1/gateway/challenge both404, so file API/SDK and issuer hook are
NOT publicly installed. Live Files still RAM-only. All native config, guest
cookie, speechR3, authority/root data, hosting/prototype snapshots unchanged.
No Caddy reload, router/firewall/port-forward, native restart, user-tab reload
or boot-policy change. /desktop stays live; ten-site hosting pins remain d2d0c07e...,
ef3e2235..., a57de029... from the prior read-only snapshot. Do not use old
hardcoded nine-site health or pre-ingress rollback pins blindly.

activate-private-files.py is one-time and now REFUSES existing config, even
its initial plan form. Use the ROOT INSTALLED manage-user-files.py with
--config-dir /etc/codi-user-files/ksu for status/start/stop/initialize/recover;
webhost-files-health.py is read-only current validation. Normal initialize
requires stopped units, creates a protected backup/journal and preserves current
bindings/files/usage; pending journals block lifecycle. Do not repeat bootstrap
or restore the pre-extension DB. A private-only rollback is stop these three
file units while retaining DB extensions, files, policy and backups. No public
route currently depends on them. Changed worker/policy config needs an explicit
reviewed upgrade; this operator deliberately refuses silent reconfiguration.

NEXT REQUIRED: native11 with frozen V10 allowlist, explicit default-off issuer
hook/config metadata and schema-managed enable/disable, compatible guest cookie
and code rollback, matched app.js/desktop-apps.js/style assets (old overlay alone
is incompatible), then managed /hidden/gateway HTTPS route and public Files/SDK
checks with account-bound late-reply isolation and VM/draft preservation. Keep
all ten sites and prototype unchanged. Native upgrade still invalidates RAM
issuer tokens; durable sessions are unfinished. No arbitrary LAN share has been
selected. Own-WAN anon deny/registered ICMP+TCP80/443 guest policy is STILL NOT
installed. Direct ICE/TURN fallback, independent WAN, cookie refresh, encrypted
backup and full v0.1/v0.2/v0.3 audit remain open. Root1 expires22:36:39UTC;
explicit renewal only. Full goal active, not complete or paused.


## Native11 live, file policy still OFF — 2026-10-23 11:12 UTC

Operative controller AND issuer/steward/guest are now
/srv/codi-connected/releases/native11-99f938cd7f895831, manifest
99f938cd7f895831191957e342824b7d44506df19d32edfa2157b48bc9385ec0 (195 files).
Use its scripts/manage-services.py with the existing protected venv517179c and
/etc/codi-connected/ksu/managed.json for lifecycle/renewal. Config remains schema3,
files OFF, no userFiles field. Current PIDs239110/239112/239113; prior native10
PIDs above are historical. RAM-only issuer tokens were invalidated by upgrade;
existing account records, keys, authority and persistent guest cookie preserved.
No data restore. Normal native units remain disabled for boot; bootstrap stopped.

Root upgrade receipt /srv/codi-connected/native11-upgrade-1792753074606980534-result.json,
SHAf8826e9ed8fce633c5a4a1f4cd3b835f6fb4f3adbf31d1cc79a02e6a1ef4b130.
Coherent ROOT-ONLY checkpoint /var/backups/codi-connected/ksu/native-67e8f0332e62965579bb5a7990637ddb,
manifest daaa2f6980dc8d25eef797fb3f816702ae5cef43c10eb1c4ffa233668613ca24;
contains credential/key material, never copy into Git/public. Root sealed rollout
wrapper /srv/codi-connected/rollout-controllers/d653e6c722a0eb9ada569f1c0177087607cbae337ea22ee89fef0f0022b39688/native-rollout.py.
Source/server checkout840a9d8479731a4371cea3388f19e80a3fd0981c at installation.

Frontend remains R14 179a5b56...; matching R15 6d81a52b... is a private candidate,
not live. New desktop-apps.js818028d5... is served by native11, protected by a
compatibility marker so old R14 does not expose unsupported Files controls.
Public Files remains RAM-only; gateway SDK and issuer file challenge still404.
Private file worker/operator aa240935.../8fdbbdda..., PIDs236763/236765, retained
one real registered home/seven ACL rows/no anonymous homes, unchanged.

Exact native11 local tests PASS:28 auth,14 release,18 TURN,11 actual installed
file-policy/recovery cases; actual packaged issuer+worker Chrome root/hidden
8MiB/file-UI/account/late-reply/VM preservation and mixed frontend compatibility;
full installed code upgrade/checkpoint/recovery/real TLS Chrome chat/separate
chess/PGN/guest ping/DNS/HTTP. See evidence/native-file-authorization.md and
native-files-milestone-result.json. These local TLS fixtures are not public WAN.

New public native11-public-network-result.json PASS with default certificate
trust, two disposable owned Anon sessions, real forced-TURN TLS RTC chat/separate
chess/PGN, Linux and guest ping/DNS/HTTP. The owned peer test matches exact lease,
SID and key before inviting/accepting; it never invites arbitrary public peers.
No user tabs touched. native11-live-preservation-result.json and fresh
webhost-files-health-result.json verify actual current state. Hosting remains
10 sites, generator d2d0c07e..., manifest ef3e2235..., Caddy a57de029...; managed
config equals generated bytes. /desktop, homepage, website release, speechR3,
443 ingress/TURN policy, private-worker config/PIDs and all kernel settings intact.

Next: reviewed KSU-only file route with its own12MiB envelope (8MiB decoded),
retaining existing64KiB identity limit, matched R15, then explicit native11
configure-user-files with installed standalone operator. Only issuer restarts
for file enable/disable; keep v86/guest/steward running. Fresh public fixture-only
Files tests and account cleanup required. No LAN share selected. Own-WAN anon
block/registered ICMP+TCP80/443 is NOT installed. Durable issuer sessions, guest
cookie refresh, direct ICE fallback, independent WAN and full roadmap audit open.
Root1 expires22:36:39UTC, explicit renewal only. Goal remains active.


## R15 registered private Files LIVE — 2026-10-23 11:26 UTC

This supersedes the default-off native11 note. https://ksu.codes/hidden/ now has
real private server files for registered accounts. Start as Anon, use the top-right
Register/Sign in, then Files → My server files. Import/Download, folders, text
editor Save, conflict/draft protection and deliberate copies to/from guest files
are live. Temporary Linux files remain RAM-only; no automatic server mount/sync.
Anon cannot allocate a server home. No LAN share or arbitrary host path selected.
Do not put a blocking login page back. Preserve VM/drafts during account changes.

Operative native/controller release remains native11-99f938cd7f895831 (full hash
99f938cd7f895831191957e342824b7d44506df19d32edfa2157b48bc9385ec0), existing venv517179c.
Managed config /etc/codi-connected/ksu/managed.json is NOW schema4 with pinned
userFiles. Only issuer restarted for enablement: issuerPID240953, steward239112,
guest239113. Guest cookie/index, root authority, account keys/data and forced
TURN relay policy preserved. Normal units disabled for boot, bootstrap stopped.
Issuer sessions are still RAM-only: that restart invalidated existing login tokens.
No data restore or browser-tab refresh. Root1 expires2026-10-23T22:36:39UTC;
renew explicitly with this native11 controller, never provision over current state.

Frontend R15 6d81a52bf9d7be264ebba58340ccc4302b8208c2594a4f3b2138224eaa938787
is installed at /srv/codi-connected/frontends/<SHA>, four-asset overlay only.
Native desktop-apps.js818028d5... supplies matched Files rendering. SpeechR3 stays
df759266...; current64 independent PTYs/workspaces/tap-voice/touch behavior retained.
Root frontend receipt /srv/codi-connected/frontend-6d81a52bf9d7be264ebba58340ccc4302b8208c2594a4f3b2138224eaa938787-activation-result.json.
Root file enable receipt /srv/codi-connected/files-enable-1792753961519921749-result.json,
SHA49434aab6a27ae503d045a95305a07411068f0ae81f48025d3f5e17b3191b9d8.

Private worker/operator remain aa240935.../8fdbbdda..., PIDs236763/236765,
UID978/DynamicUID63908 in the same loopback-only private netns, zero caps.
Host127.0.0.1:8140 proxy is fixed destination/16 connections, not Internet forwarding.
Credential SQLite stays separate from permission/usage SQLite and UUID disk homes.
One real registered home plus SEVEN empty disabled-QA homes are retained (8total,
56ACL rows), NO anonymous homes. All7 generated fqa_ accounts verified disabled;
test contents removed, real dflanag3 still enabled and private files untouched.
Fixture ledgers contain only generated names/public subjects, never passwords.

Managed KSU-only codi_files=true adds /hidden/gateway/* →127.0.0.1:8140,
stripping only /hidden. Separate12MiB JSON envelope admits8MiB decoded files;
existing issuer/body64KiB limit retained. No new external ports/forwarding/firewall.
Current hosting pins:
- generator b8944e87534792e4255643f9abe4f10d9e72e3a4adceeb8ba646e931ddead4e1
- sites.toml799bab541b18541c9d43d859889d34b94da768f91f38dee2bd43d50601ad2526
- Caddy8467252aea4bb8cc87faf35403f385fbe0664b746739839956308c14eeca0ab7
Root route receipt /srv/codi-connected/files-route-1792753772626662018-result.json,
SHAa086220ffaa3cfd49a22d43acea2fa6a534a7d2fc5ecd39952e0d181e8b83eeb.
Generator equals active Caddy. All TEN sites pass, including hardware/cardboard;
all133 files declared in the unchanged /desktop release verify. Homepage/current
website release unchanged. Preserve redir * /hidden/ 308 and shared443 ingress.

Rollback: first use installed native11 manage-services.py configure-user-files
--config /etc/codi-connected/ksu/managed.json --disable to withdraw new issuer
confirmations. This journals/restarts only issuer and returns schema3, retaining
all current files/DBs/TURN. Before any native10 code rollback, files MUST be disabled;
older profiles refuse while schema4/files enabled. Do not restore old user data.
Frontend rollback R15→R14 inputs (file route retained):
/var/backups/webhost-sites/change-20261023T111030381641Z/common.py and
/var/backups/webhost-sites/change-20261023T111030382140Z/sites.toml.
Route rollback to pre-files inputs:
/var/backups/webhost-sites/change-20261023T110921862242Z/common.py and
/var/backups/webhost-sites/change-20261023T110921863233Z/sites.toml.
Use hosting controller lock/CURRENT pins/generated validation+apply/all10-site
and prototype checks; reconcile later changes, never hand-edit derived Caddy or
blindly restore old9-site/pre-ingress backups. Caddy reload can reconnect streams.

PASS aggregate public-files-milestone-result.json binds exact native/worker/R15,
local actual installed lifecycle/fault/code rollback tests, public default-TLS
Files UI create/save/version conflict/reload/signin/account isolation/late reply,
VM/guest draft retention, explicit copies and guest overwrite refusal, actual
browser file-input Import and downloaded binary checksum,8MiB binary round trip,
390px emulated touch Save, fresh touch/desktop regression, actual CPU Whisper,
owned-only public RTC forced-TURN TLS chat/separate legal chess/PGN plus guest
ping/DNS/HTTP, current private kernel/DAC boundary and all-site/prototype health.
QA cleanup/audit PASS. Real account secrets/files not used as test fixtures.
No physical Android microphone/keyboard or independent WAN proof is claimed.
See active-system/evidence/public-private-files.md (or evidence/... within target).
Retained failed receipts document incorrect401/403 expectation with automatic
hosting rollback, absent packaged QA CLI, lost test globals after reload and
Snap ChromeDriver private /tmp fixture mismatch; test harness corrected without
weakening product authorization or changing the tested native/worker assets.

Full goal remains active. NEXT: signed per-connection guest networking identity;
anonymous own-WAN IP deny and registered ICMP+TCP80/443 allow are STILL NOT LIVE.
Private LAN remains denied absent explicit approved exceptions. File HTTPS is
independent of guest Internet access. Then enforce OS egress, selected shares and
resource quotas/broker, durable issuer sessions and guest cookie refresh, direct
ICE fallback, independent WAN and full v0.1/v0.2/v0.3 requirement audit. No graphical
games or root-domain production cutover yet. /desktop remains the public prototype.


## Guest-network identity/egress foundation LOCAL ONLY — 2026-10-23 12:00 UTC

Live stays native11/schema4/R15 with registered Files, issuerPID240953,
steward239112, guest239113, file-worker236763/proxy236765. No new network rule,
worker, UID, native candidate, browser asset or public API has been installed.
Current source/server baseline before this local work was1d5102dbe070bbe7fec6d08e0d1e9aa81f045318.
Fresh webhost-files-preview-health and refreshed public-files aggregate PASS:
all10 sites and133 prototype-declared files verified; normal units still disabled
boot, root1 expiry22:36:39UTC. /desktop/current website/ingress/files unchanged.
POST /hidden/api/v1/guest-network/challenge remains404; new authorization metadata
absent. Shared-cookie raw guest policy STILL permits own WAN to anonymous guests.

New private source guest_service/{authorization,egress,frames,worker}.py and
origin_service/guest_authority.py implements purpose-separated live-session
network grants and fixed-role internal wire workers. Not imported by native11.
Network grant/proof types are distinct from files and bind nonce, connection ID,
key/SID/account, exact origin/mount/path and effective egress policy SHA256.
RLock serializes single-use challenges. Max30s grants; reset/expiry has no
registered privilege. Fresh grants observe logout/disable/generation/session
expiry; existing accepted lease may finish only until its30s deadline. Reference
server anonymous subject is anon:UUID, NOT SID (first fixture failure retained).

Workers have separate fixed anonymous/registered roles, protected transport
secret and Origin, no client-controlled UID/role. Registered worker starts QEMU
only with real registered confirmation+key proof. Fresh same-account/SID/key
refresh keeps QEMU/NIC; another account/key, expiry/reset/disconnect retires QEMU
and its established NAT state. Ingress/egress recheck lease. New Ethernet parser
retains source/header/options/fragments/port checks and only gateway/DNS private
wire exceptions. No new files/keys are exposed to VM. Worker source has no native
installer/CLI/root credential custody yet; do not run it as a production daemon.

One EgressPolicy generates matching packet decisions and UID-scoped nftables.
Explicit special/private/multicast/reserved prefixes, IPv6 and unsupported ports
are denied. Anonymous blocks protected public IPs; registered allows echo and
TCP80/443 there. Fixed public DNS upstreams may not overlap protected IPs.
Frontend UID may initiate only issuer/fixed-worker loopback sockets; reply-only
exceptions keep fixed service listeners usable. Other UIDs are not selected.
Effective digest covers prefix/port/DNS/own-IP/IPv6 semantics, not just user inputs.
IANA special-prefix and netfilter direction references are in the evidence doc.

PASS exact local evidence (guest-network-foundation-milestone-result.json):
-28 real issuer WSGI/ES256/SQLite identity tests incl concurrency/replay, proof
 type/file separation, wrong key/token/issuer/policy/context, anon/registered,
 logout/disable/generation, reset/close/refresh/deadlines and separate rate buckets.
-161 policy/validation checks plus84 REAL native socket probes across numeric
 fixtureUIDs60231/60232/60233 and unaffected60234, all no caps/NoNewPrivileges,
 in a disposable network namespace with actual nft rules and simulated public/
 LAN targets. Anonymous own-IP denial vs registered access, both roles' private/
 metadata/CGNAT/IPv6/port denial, DNS pins, loopback replies and nft counters PASS.
 Host firewall untouched; namespace/process cleanup verified. Those numeric UIDs
 are fixtures only, NOT accounts to provision in production.
-59 actual HTTP/WSS/QEMU checks: separate wire ARP, secret/origin/anon/claimed-role
 refusal, true process admission, live refresh preserves PID/NIC, different account
 cannot inherit NAT state, expired/disconnected/oversized/idle wires reap children.
 These run as local test user, NOT combined kernel/worker UID enforcement or v86
 browser Internet proof. No external traffic used by these fixtures.

NEXT REQUIRED: combine actual distinct-UID workers/QEMU with these kernel rules
in one disposable fixture and prove ping/web/DNS plus OS bypass denial. Then
implement frontend coordinator and browser control adapter: legacy binary v86
clients stay anonymous; typed auth controls must never enter NIC. Account changes
retire old backend/NAT flows while retaining VM/RAM/files/64 PTYs. Anonymous/expired
network role is not a certificate-identity downgrade or a local trust escape.
Preserve old token/certificate distinctions and browser consent.

Build a separate protected root operator before any rollout: locked distinct
service users (do not reuse issuer/file/Caddy users), immutable code and per-role
LoadCredential, public issuer/egress pins, public-only resolv.conf bind for workers,
strict units/cgroups, durable per-account network usage, atomic UID-scoped nft
transaction/recovery/drift checks. No broad firewall flush or public new ports.
Kernel rules alone do not install/protect these Python workers; separate green
checks are not proof of combined service confinement.

Native12 work must FIRST freeze V11 allowlists. New managed schema needed for
optional network pins while preserving schema4 Files/schema3 TURN and reviewed
code rollback. Keep default off, cookie/account/files/authority intact. Serve an
explicit feature-gated client module without breaking frozen old PUBLIC lists;
new/old frontend+native compatibility needs real tests. Native11 controller and
R15 remain authoritative. New per-user IP policy is NOT LIVE until full combined
operator/native/browser/public proof. Recheck actual WAN addresses/hosting pins.
Full goal remains active: resource broker/selected shares/network quotas, durable
issuer sessions/cookie refresh, direct ICE fallback, independent WAN and full
v0.1/v0.2/v0.3 audit. No graphical games or production root-domain cutover.

Private source foundation manifest14312fcb17c490f03a8016fc2e537ae6133a0be73860a65853ad2a9fd2fefee0 (11files),
Git source143ad71 (source only; not installed). Local artifact at
active-system/.build/network-foundations/guest-auth-egress-r1; private Git package
tools/codiserver/guest-network. See its frozen evidence and required next steps.


## Maintenance/public-app candidate and live compatibility overlay — 2026-10-23

User requested root-triggered maintenance countdown, honest unsaved-work text,
disabled desktop controls/spinner during disconnect, automatic reconnect without
VM reload, modular lazy browser apps and persistent browser app caching. Browser
reload/close/crash cannot be disabled; no automatic VM/document save is claimed.

Public app source now lives in desktop-preview/served_apps_public/{calculator,
chat,files,help,rooms,terminal,text}/index.mjs. Only active-system consumes it;
desktop-lab and /desktop are unchanged. Host API1 unifies UI, input, identity,
files and network services. Trusted same-origin modules are not a sandbox.
Build apps then device cache before exporting; public bits only, no user data,
credentials/config/grant/status/private-file API caching. Device storage requests
persist() and reports actual grant/denial plus quota; no VM snapshot is saved.

Native13 candidate abb67a1f7a2e718c006cf0784dd216cceebb49982d4a8c03f14b7e21bfff2abf
(221files), private Git/server source76b72bef51f640664d07c27f682316e07cf2cc19.
Actual private-VM native13 upgrade/checkpoint rollout, 10-second notice + all
three real service restarts retain v86/shell/file/editor/cursor; explicit private
save survives. Issuer restart loses RAM bearer session; new UI resumes as Anon
and tells user to sign in again. Actual on-device CPU Whisper, touch, all seven
lazy views, actual RTC chat/separate chess/real downloaded PGN, corruption refusal
and offline reload/cache rebuild pass with scoped receipts. Fixture pins are
not public TLS/WAN/physical Android proof. Current runtime remains native11 on
webhost pending guarded code upgrade; new egress policy still inactive.

LIVE CHANGE NOW: byte-equivalent six-file compatibility frontend f29a1337d03749a346cd9cab8fc09a3f9f95a40a8a80c225bab8538ef82a924c
replaces the four-file R15 pin under /hidden only, freezing the same old native11
desktop-apps.js/networking.js alongside the old four assets. This MUST stay until
the native upgrade is complete, then activate the new matched frontend
9b871452e98b41e38f6583660c7be0222a3ac113a4a2bed33b959b43c27697f2.
Do not expose old app.js with the new lazy-loader helpers. New module/cache assets
come from native13; overlay contains six root/guest files.

Hosting generator 718934ce2d95a9ebea7e96b386027b1c0523a7390c310e74c8eba009cd8a10a4
Manifest 31697010c1b9eec530f4c9c84f43da9865f7dd7fcb6d1ebaf241409e1631fb6c
Derived Caddy d40f2803eb25eb0139e3eac2c28f0a24d3592903cf6452717dcb349ff7e7b0ee
Native/file state and PIDs, current website/prototype, shared443/TURN, ports and
boot policy unchanged. All10 sites and prototype checked by activation. Root
receipt /srv/codi-connected/frontend-f29a1337d03749a346cd9cab8fc09a3f9f95a40a8a80c225bab8538ef82a924c-activation-result.json.
Use current controller lock/pins/generated validation/application workflow. Caddy
reload may close proxied streams; unchanged PIDs do not prove uninterrupted WSS.
First upgrade cannot push new JavaScript into old tabs; preserve their RAM.

Next: guarded default-off native13 code upgrade retaining Files/TURN/accounts/
keys/cookie, then explicit guest-network enablement and matching new frontend,
fresh public TLS/Chrome/all10/prototype proofs. Native13 rollout wrapper source
and actual VM CLI proof are in tools/codiserver/desktop-maintenance on private
Git. See active-system/evidence/desktop-maintenance.md for scopes and preserved
failures. Full v0.1/v0.2/v0.3 goal stays active: durable issuer sessions, resource
broker/shares/per-resource controls/direct ICE/WAN/full plan audit unfinished.
Root1 expires22:36:39UTC; explicit operator renewal only. Private local VM still
QMP-confirmed running, root delegation renewed explicitly to revision2 for2h;
never recreate it or copy its ephemeral keys/service state into source/webhost.


## Native13/schema5/R16 LIVE — 2026-10-23 19:08 UTC

Supersedes the compatibility/default-off notes immediately above. /hidden now
uses native13 abb67a1f7a2e718c006cf0784dd216cceebb49982d4a8c03f14b7e21bfff2abf
at /srv/codi-connected/releases/native13-abb67a1f7a2e718c and schema5. Managed
configSHA bd2daea03c27f4e8fe1708825a95b4aaf764dec1bf34f789e1892dd934deae8d . Issuer248791/steward247884/guest248835; private file worker236763/proxy236765 unchanged.
Root upgrade receipt /srv/codi-connected/native13-upgrade-1792781480365016301-result.json.
Current protected outer rollout controller1c4ba57df6208873935e9dc24d5a6d849bc507cf946ed4031a2f39c64e78e49a.

The reviewed guest operator8411/worker7f5 is NOW ACTIVE. Guard248668, anonymous
248701, registered248722, static/non-boot units. KernelMatches true, no guardFault.
Scoped codi_guest_egress table/UID filtering is intentional; no host-wide flush,
new router ports, forwarding or boot changes. PolicySHAaa1aa08d... ownPublicIP
104.180.210.33 verified again via actual server WAN reflection and public DNS.
Anon raw guest traffic to own WAN blocked; registered grants allow echo and
80/443; private/special/IPv6 remains denied. Private Files uses separate HTTPS
API and does not require raw LAN access. Public browser role probes still need
fresh receipts; actual installed VM role/kernel chain already passed.
Root activation receipt /srv/codi-connected/guest-network-enable-1792782201948281100-result.json .

New MATCHED six-file frontend9b871452e98b41e38f6583660c7be0222a3ac113a4a2bed33b959b43c27697f2
is LIVE, replacing byte-equivalent f29 compatibility bundle. New tabs load lazy
public app views, honest recovery/countdown/spinner and Device storage cache.
Existing older tabs retain their original JS/RAM; no forced reload. Source76b72be
contains current artifacts. SpeechR3df7592... remains unchanged on visitor CPU.
Root frontend receipt /srv/codi-connected/frontend-9b871452e98b41e38f6583660c7be0222a3ac113a4a2bed33b959b43c27697f2-activation-result.json.

Current hosting generator 718934ce2d95a9ebea7e96b386027b1c0523a7390c310e74c8eba009cd8a10a4
Manifest 9d5e4d93f66d1f4925a5e68c1cf071db64985449b00e9dd70d0132aaa71721f8
Derived Caddy 5bb5d0579d4ec17f3968ce821c7cc35d73daf11bd06fa183d14d7c69701537b5
Scoped R16->compat rollback inputs: /var/backups/webhost-sites/change-20261023T190729317441Z/common.py and /var/backups/webhost-sites/change-20261023T190729317945Z/sites.toml. Use controller lock/current pins/generated validation/apply and
all10/prototype checks, never hand-edit Caddy. Do not revert all the way to a
four-file old overlay while native13 serves the new helper files. Network/code
rollback are distinct; old native11 requires disabling guest policy first and
removing only the owned UID rules BEFORE old same-UID relay restarts. Never
restore old account/file/usage/key data to undo code. Keep all private journals.

All10 sites/prototype/current website and private file processes passed activation.
Fresh public-default-TLS touch+desktop/v86 test PASS on R16 (no cert exception).
Public voice/RTC/network/maintenance/cache follow-up is ongoing; no physical
Android or independent WAN proof inferred. Native/root authority expiry remains
22:36:39UTC with explicit operator renewal only. Full goal stays ACTIVE, no
root-domain cutover or graphical game interfaces.


## Public R16 verification complete — 2026-10-23 19:48 UTC

The live native13/schema5/R16 state above now has fresh ordinary-public-TLS
PASS receipts: public-maintenance-result (labeled ten-second warning, locked
controls, same Linux/draft/cursor after cancellation, NO live restart/save),
device-cache-public-result (63 public items/78,132,918 bytes, actual persist
DENIED truthfully reported, corruption refusal/offline reload/fresh boot/clear
and rebuild), public-network-account-result (anon own-WAN deny, registered echo
+80/443 allow, both LAN deny, generated private file save/read/logout/sign-in),
touch-public-result, general-voice-public-result and tls-discovery-result (actual
RTC chat/separate moves/matching downloaded PGN). QA files removed and generated
accounts disabled; no real account/personal file used. Current registry10 homes
includes9disabled QA homes and1real; no anonymous folder. Do not assume a fixed
count in future health checks. Actual physical Android and independent WAN/NAT
remain unverified. Notice now cleared; no new global maintenance pending.

webhost-desktop-health-result PASS binds active guest guard/kernel rules, current
config/pids, private Files boundaries, all10 sites and133 unchanged prototype
files. No final check restarted services or changed private data. Current pins
and rollback remain the Native13/schema5/R16 entry above. Source release is
76b72bef51f640664d07c27f682316e07cf2cc19; final proof bundle is separately curated
under tools/codiserver/desktop-maintenance-live in private Git (not public assets).
Existing frozen candidate/proof suites remain historical, not relabeled.

Browser toolbar/OS close/reload/crash cannot be blocked. Open-tab reconnect keeps
RAM where possible; offline reload explicitly says prior Linux was not restored
and starts fresh when online. No VM snapshot or automatic document save exists.
Keep /desktop unchanged and preserve old tabs/RAM; manually save before refresh.
Private VM is retained, root delegation explicitly renewed revision3 for2h;
QMP status must be checked before reuse, never recreate on a mere timeout.
Live root1 expiry is still22:36:39UTC, explicit operator renewal only. Full
v0.1/v0.2/v0.3 goal remains unfinished, with durable issuer sessions, selected
shares/resource broker, per-resource controls, direct ICE/WAN and full plan audit
remaining. No root URL cutover or graphical games. See evidence/desktop-maintenance.md.

Final proof source commit: `15c8040da8fe4f350fa2d1ba5bab4bddcdd00e1a`, pushed to private main and fast-forwarded cleanly on box-webhost. Live-proof bundle manifest `25e33403e2f8055420bf740068d8f3b55c53a823f2ec204cee679d75ea2319e7` verified19files locally/remotely. This final sync changed source/evidence only, no runtime/service restart. Previous45-file suite remains byte-verified and unchanged.


## Direct ICE preflight and recovery candidate, rollout DEFERRED — 2026-10-23

Current live /hidden remains native13 abb67a1f7a2e718c006cf0784dd216cceebb49982d4a8c03f14b7e21bfff2abf,
schema5 config bd2daea03c27f4e8fe1708825a95b4aaf764dec1bf34f789e1892dd934deae8d,
frontend R16 9b871452e98b41e38f6583660c7be0222a3ac113a4a2bed33b959b43c27697f2,
issuer248791/steward247884/guest248835, Files236763/236765, active guest guard.
TURN public policy is still RELAY. All10 sites,133 prototype files and current
worker/private file boundaries freshly PASS; health now binds frozen live native
and Files SDK manifests instead of newer local WIP. Hosting pins, routes, boot,
public website and /desktop unchanged. A real60second warning was CANCELLED
before deadline, NO public restart or policy flip. No maintenance pending.

PROGRESS: Actual public TLS host/host direct and private-VM-browser UID UDP-blocked
relay/relay TLS preflights pass chat/separate chess/real PGN/v86;178 kernel drops,
native PCs all, no forced relay. Explicit test-only native override, NOT live
server policy activation or independent WAN. Dedicated Chrome156.0.8078.47 and
signed Ubuntu libs installed only in retained VM; driver/table cleaned after
test. No host or webhost package/firewall/router changes this turn.

Caught/reproduced R16 recovery failure before public restart: cached relay policy
rejects all replies after issuer RAM loss. New candidate refreshes bounded strict
same-origin config while retaining identity/root/service pins; only all/relay
preference and fresh signed directory statements may change. Missing steward
retains old expiring pins/bundle, no fabricated freshness. Temporary errors retry
without signing out; only401 re-enters server-certified Anon. No VM snapshot/save.

S02-04 and shared/PROTOCOL expressly require HTTP sessions/challenges in RAM.
Earlier notes listing durable issuer sessions as required work are superseded.
Do NOT persist browser keys/tokens or change this boundary without a requested
protocol change. Account/key persistence and private files already exist.

Candidate native13 ce00294efbc58d835308fd4d4703e6422c199f40c5ee110f56d5c67296138442
(222files), app b62bc67d..., R17 fd970a818ae227c4ca799ad01cc3b2b7bf7ece3a10f1b1906499796443f9d117,
cache563311cd... installed ONLY in private VM. Actual protected code upgrade,
all3real native stops/starts +10sec notice +managed relay-to-all change preserve
Linux/shell/file/editor/cursor and explicit account file after re-signin. That
policy fixture uses turns:fixture.invalid:443?transport=tcp, not a real relay.
VM browser role/private Files/PTYS/workspaces PASS; actual CPU Whisper PASS;
RTC/direct/separate moves/PGN PASS; cache/hash/offline fresh boot/rebuild PASS;
local lifecycle27 +20pin negatives, native issuer90, real WebCrypto145 PASS.
No physical Android/independent WAN proof inferred. Retained failure receipts
include the cached-policy reproduction, fixture nft syntax and health SDK
manifest correction; no product policy/authority weakened to pass.

NEXT: freeze and implement explicit versioned SIGNED client ICE preference
negotiation that keeps LEGACY cached R16 clients on relay and permits approved
modern all. Distinguish advertised modern preference from legacy default so old
workers/JS remain usable. Bind preference into existing proof; reject unknown
fields/profile/values; retain existing key/sid/token/account-generation/absolute
expiry rules. No second auth/P2P engine, no persisted sessions. May require native
profile14 with explicit capability flag so frozen profiles remain supported.
Prove actual old cached R16 plus modern tab through real installed-policy switch,
retaining Linux/drafts; then public default-TLS direct +kernel-blocked fallback
WITHOUT preflight override. Do not assume a new frontend updates old JS realms.
The current configure-direct-ice.py rejects announce/apply before SSH until this
gate; read-only planning works. Do not run archived helpers to bypass the gate.

Private Git/main AND clean webhost source efa1051f1ab683f51209982697ec03d554a867ff
(source only): tools/codiserver/policy-recovery bundle
bf31ee2cc570ecb33a63c7c2ebeb8745c8b5d0390b18eed2deb47d59ccc26b5e (35files),
direct-ice-fallback source3634087340416754f478c659101f9c65d3650c710f0b659d7654868435b39228.
Original47b1f774... preflight preserved byte-identically in its history/preflight-343c557.
Runnable native/frontend under native-candidates/<SHA>, frontends/<SHA>, NOT
installed on webhost. Prior45file maintenance suite and live19file proof bundle
remain unchanged. Never copy actual configs/keys/VM state/accounts into source.

Same VM QMP-confirmed RUNNING PID3283572, SSH49747/HTTPS57503, no host shares.
Current native /srv/codi-network-fixture/candidate-ce00294efbc58d83; real current
PIDs via scripts/upgrade-native-network-vm.py --status. Private test TURN secret
/etc/codi-fixture-turn/turn.secret stays VM-only. Its TURN endpoint is deliberately
fake; the managed policy transition is real.
VM root revision3 expires21:37:25UTC; production root1 expires22:36:39UTC.
Renew explicitly through protected operator when needed; no automatic signer.
Never recreate VM on timeout; inspect QMP/specific process handles first.
Full v0.1/v0.2/v0.3 goal stays ACTIVE and incomplete: legacy preference gate,
selected resource shares/broker, private-group crypto gate, distributed routing/
repair/capacity, independent WAN and full production requirement audit remain.
See active-system/evidence/direct-ice-fallback.md. No production root cutover.


## Native14 ICE compatibility proven; installed INACTIVE — 2026-10-23

LIVE remains native13 abb67a1f7a2e718c006cf0784dd216cceebb49982d4a8c03f14b7e21bfff2abf,
schema5 config bd2daea03c27f4e8fe1708825a95b4aaf764dec1bf34f789e1892dd934deae8d,
R16 9b871452e98b41e38f6583660c7be0222a3ac113a4a2bed33b959b43c27697f2,
global relay, nativePIDs248791/247884/248835. Files236763/236765 and active guest
UID guard remain. Hosting718934ce.../9d5e4d93.../5bb5d057... unchanged; all10sites,
133prototype files and private Files/guest boundaries fresh PASS. NO public
service restart, maintenance announcement or ICE policy flip this turn. /desktop
and domain root unchanged. Full goal ACTIVE, not complete/paused/blocked.

The previous legacy-cache compatibility gate is now proven PRIVATELY. Frozen
network/ICE-PREFERENCE-PROFILE.md defines codi-session-ice/1: native14 only enables
--ice-preferences for online issuer, never bootstrap. Public legacy default stays
relay; separate versioned allowed/preferred metadata tells modern modules what
to request. Choice is in existing signed JSON body, not cookies/headers. Unknown/
forbidden fields/versions fail before mutation. One existing issuance/key/sid/
token/generation/absolute-deadline path; ContextVar resets on every exit. Choice
is a public string in existing bounded RAM session only. S02-04 RAM-session
boundary is retained; no persistent tokens/session keys or second peer pool.
WeakMap config binding covers old app/new SDK sign-in. Modern core SDK query
?originProfile=codi-session-ice-1 bypasses old workers; new worker recognizes only
that exact public alias and hashes it against the normal SDK record. Config/
account/status/grants/private files remain uncacheable. Recovery checks authority
and endpoint pins; native14 code boundary in both directions requires relay first.

PASS: native65 + existing account/crypto/SQLite90 with PreferenceService; real
WebCrypto153; exporter22 including frozen10/11/12/13; managedTURN20/deployment17
model boundaries. Real Chrome18 checks actual cached R16 app/module/worker vs
modern through relay/all/relay, Linux/shell/file/editor/cursor retained; mixed old
app/new SDK sign-in. Actual private installed native13→14 upgrade + issuer-only
policy restart19checks, both cached-old and modern never reload, sign in/read
explicitly saved private file. Actual authenticated checkpoint/code rollout
retains guestPID during checkpoint/cookie/keys/accounts/files/counters and private
file workers. Actual RTC/chat/separate moves/downloadedPGN/WSS-stop independence,
CPUWhisper/touch/workspaces, private file/guest17probes and cache alias/offline
fresh-boot/corruption/clear-rebuild checks PASS in their exact R1/R2 scopes.
Private VM TURN URL is intentionally fixture.invalid; real native14 TURN/TLS,
public activation, physical Android and independent WAN remain unverified.
Retained failures include wrong import path/model descriptor, impossible mixed
worker readiness and cleanup versionless delete409; fixed TESTS, not guards.
First saved QA file remains private VM forensic data; no real user's file touched.

R1 native14 8e32b206a5f6a0012cadb00556d9aea86c1f9e410e87ee1bd55f51b00d01c39f
(223files). R2 8810761ee7e47e15b055ccda8ed83cd15c017f839770b980dbfaa0d7ab62e0ce
(224files) changes only Chat's obsolete no-traversal assertion plus lazy catalog/
cache; backend, SDK and all6frontend files byte-identical, lineage receipt PASS.
R18 frontend97b80a77ce3f377aecdea64928730d35c947ce13c3c6e8a968123fa218778381;
app9e9cb6ecc22e3886c8cb6af6593035880d4f88facba4ab6a2dbdb6169c547bd2;
cache09a4286abe2f42402ebcd8553c8fca789675bb4915bef6828c286075844e3bc5.

Git-first plan+INSTALL now PASS on box-webhost: candidate
/srv/codi-connected/releases/native14-8810761ee7e47e15 and authenticated outer
controller /srv/codi-connected/rollout-controllers/ec3ee5d36ecdd75eb126571661cd1c885c9490a1a2331dbe22edd9f7a85eb036/native-rollout.py
are protected and INACTIVE. No unit/config/boot/routing/runtime change. Root
receipt /srv/codi-connected/native14-install-1792791192748432860-result.json,
SHA5856ededc6a77c63a72779c55895ae7c040e8f244fd01b7a1229f0bd01631ea2.
Actual installSourceCommit a61c791b30793955aaa5826057fe95b79e36ba03; clean current
private Git/main AND webhost source ad57c919c20d6a98db069635a9f64c44adf40f20.
Candidate bundle tools/codiserver/ice-preference manifest
8bb85de5b88988273c97c7d661a0a8cf29669235bb14831e8d2e90853ac3fac0 (52files)
retains its pre-install source-only scope; separate ice-preference-installation
addendum6f23a81de2a2624e7c86ca778efc60c775f1f5f884bd2b55d94059b81600092a
supersedes only installation status. Prior artifacts/failed receipts preserved.
Diff check noted inherited native release.py blankEOF; frozen bytes not altered.

NEXT: explicit protected LIVE operator renewal BEFORE existing Root1 expires
2026-10-23 22:36:39UTC (do not auto-mint indefinitely; execute and record operator
renew with same keys/roles, no user permission re-ask needed within this goal).
Then actual60sec notice, mark active after deadline, use
scripts/activate-ice-preference-native.py --action upgrade --commit CURRENT_SOURCE
--notice-id EXACT_ELAPSED_ID (R2/current baseline pins; protected checkpoint/code
rollout). Clear widget only after readiness; preserve all journals on failure.
Global policy must stay relay while crossing13→14. All native roles remain boot-
disabled. Publish matchedR18 via existing hosting controller lock/pins/generate/
validate/apply, not hand edits. Keep redirect syntax and current speech/file/TURN
routes. Fresh public defaultTLS identity/login/privateFiles/guest-policy/RTC/chat/
separatechess/PGN + actual TURN/TLS first. Only THEN update the old disabled
configure-direct-ice helper to exact native14/config/frontend baseline and switch
modern preferred to all, keeping legacy relay; prove native direct and actual
UID-UDP-blocked TLS fallback without overrides. No router/port/firewall need.

Private same QMP-running VM PID3283572 SSH49747 HTTPS57503 now native14 R2
/srv/codi-network-fixture/candidate-8810761ee7e47e15; turn policy ALL/fake endpoint.
Fixture ingress supports original R16 static assets per owned-browser cookie;
fixture-only helper/flag never enters native/public bundle. Its source
scripts/native-network-vm-services.py is a941d5bf... . VM root explicitly renewed
revision4 expires22:48:17UTC, separate from liveRoot1. Never recreate VM on an
observation timeout; use QMP/current process handles. No host package changes.
See evidence/ice-preference.md and current receipts for precise R1/R2 scopes.
Broader remaining goal: public14/WAN, selected resource broker/shares, private
crypto selection gate, distributed routing/repair/capacity and full requirement
audit. Graphical games and production domain-root cutover remain deferred.


## Native14/R18 LIVE; modern direct ICE and real TLS fallback — 2026-10-23 21:56 UTC

Supersedes the installed-INACTIVE/native13/R16/relay-only notes above. /hidden/
now runs /srv/codi-connected/releases/native14-8810761ee7e47e15,
manifest8810761ee7e47e15b055ccda8ed83cd15c017f839770b980dbfaa0d7ab62e0ce,
schema5 config8fc7929f40629edb4e089a0601289cd54de3203468c3ff925a6e0f519e718b5c.
Issuer459240, steward451333, guest451334, all boot-disabled; bootstrap stopped.
R18 six-file overlay97b80a77ce3f377aecdea64928730d35c947ce13c3c6e8a968123fa218778381
is LIVE. Managed TURN policyALL; public legacy iceTransportPolicy remains RELAY,
with codi-session-ice/1 allowed[relay,all]/preferredALL for modern signed requests.
No second peer pool or wire/key/protocol change. Source/operator exact frozen
native14 allowlist retained. /desktop/ and domain root unchanged; all10 sites and
133 declared prototype files pass. SpeechR3 on-device/no audio upload unchanged.

Explicit protected LIVE root renewal completed revision2 with same keys/PIDs/
config/cookie, expires2026-10-24 21:43:31UTC. Not an automatic signer. Operator
receipt /srv/codi-connected/explicit-root-renewal-1792791812044185348-result.json.
An actual60sec save warning elapsed, then root authenticated ec3ee5d... outer
controller checkpoint/code upgrade preserved existing22accounts, keys/authority,
cookie/privateFiles custody; checkpoint kept guestPID. No private data restored.
Native root receipt /srv/codi-connected/native14-upgrade-1792791980127859574-result.json.
Matching R18 activated under hosting lock/pins/generate/validate/apply; Caddy reload
can close WSS, unchanged PIDs do not imply uninterrupted streams. After readiness
notice cleared. Another actual60sec warning preceded issuer-only configure-turn
ALL. Other processes/cookie/accounts/keys/hosting preserved. Policy root receipt
/srv/codi-connected/direct-ice-policy-1792792281169210345-result.json. No router,
port, host firewall, boot-policy, prototype or root-site change in this rollout.
Guest UID ACL remains ACTIVE: anon no ownWAN; registered echo+TCP80/443; both deny
private/special/IPv6. PrivateFiles API remains separate from guest egress. Private
file PIDs236763/236765 preserved. Guest guard451206/anon451239/registered451260.

PASS actual default-public-TLS proofs:
- native14-public-relay-result.json: real TURN/TLS before preference flip; chat,
  separate moves, actual matching PGN downloads excluding chat, WSS-stop survival.
- native14-public-direct-result.json: nativeALL, host/host selected, same app/
  chess/PGN/guest checks, owned peers only, NO native policy override.
- ice-blocked-direct-vm-result.json plus prior success ...before-1792792515850059857:
  nativeALL with real dedicated-browser-UID UDPexceptDNS drops in retained private
  VM, actual166 then172 packets dropped, relay/relay TLS selected, same chat/moves/
  PGN/v86 proofs. NO forcedrelay/testoverride. Owned driver/table cleaned; native
  VM release/PIDs unchanged. First run timed out at connecting; diagnostics/log
  retained native14-blocked-direct-first-diagnostics.txt and prior FAIL. Cause
  UNPROVEN. Only diagnostic instrumentation changed; no product guard relaxed.
  Two later passes prove those executions, not universal connectivity/reliability.
- public-ice-continuity-result.json: surviving actual public Chrome tab observed
  issuer epoch change, controls lock and automatic recovery without reload; same
  Linux/fs/shellvariable/guestfile/editor draft/cursor. No automatic save claimed.
- public-network-account-result.json: repeated AFTER policyALL, generated QA
  register/signin/privatefile/logout/read works; guest ownWAN/LAN policy matches;
  same Linux/shell/file retained. Generatedfile removed/account disabled. No real
  user's sign-in/file touched. Prior relay-stage receipt retained separately.
- webhost-desktop-health-result.json: exact native14/R18/ALL, active guard, private
  kernel/DAC boundaries, all10sites/133prototype/publichashes pass.
Aggregate scripts/native14-live-milestone-check.py binds exact receipts/current
HTTPS config/status and frozen release files. native14-live-milestone-result.json
PASS; fullGoalComplete:false, independentWAN:false, physicalAndroid:false.

Hosting pins: generator718934ce2d95a9ebea7e96b386027b1c0523a7390c310e74c8eba009cd8a10a4,
manifestda1383b2b4f7fa25911c204c212981d54b05355f53e07ff8284242971b387bd9,
Caddy09763673ee7b6bcc6ade992a931e3c409aebd0daafeeb5ba46181178d81a5a7f.
R18 rollback inputs: /var/backups/webhost-sites/change-20261023T214624598147Z/common.py
and /var/backups/webhost-sites/change-20261023T214624598635Z/sites.toml. Use hosting
lock/current pins/generated validation/apply/all-site checks, never edit derived
Caddy. Native rollback is separate: FIRST guarded configure-direct-ice.py to
transportrelay with currentconfigSHA8fc..., exact current clean Git commit and
real60sec warning/elapsednotice. Helper source tools/codiserver/native14-live/scripts/
configure-direct-ice.py SHAfc137fb8f5e1a8382ca2345963b5c34c93eada8382c851753ce2ec22c4be91f2.
Then restore compatible R16 frontend through hosting workflow BEFORE returning
native code to13 (R18 needs14 recovery/SDK assets). Never restore old DBs/files/
keys for code rollback. Old13 activation helper hardpins OLD hosting and must NOT
be blindly reused now. Retain old/new journals if failed; no manualjournaldelete.
Git-first activation/policy source a559aece473fad574746cbc41bf6d4c9eec9f47d;
subsequent result addendum records final current source. Frozen native14-live
bundlec5a77f36... retains its accurate relay-stage snapshot, not rewritten.

Same private QMP-running VM PID3283572 SSH49747/HTTPS57503 retained, no hostshares.
Its native14R2/fakeTURN fixture policyALL remains separate; real fallback above
uses PUBLIC /hidden/ from VM browser. VM root4 expires22:48:17UTC; renew explicitly
if later using its own native identity; do not confuse with LIVE root2 expiry.
All owned browser tests finished; keep real user tabs and VM intact.

Full original goal stays ACTIVE/incomplete. Next: audit supplied181obligations/
27gates/66tickets against actual current witnesses; keep unknowns open. Continue
private-group crypto M05 selection/review before exposing private routed rooms,
selected resource broker/shares with explicit authority, distributed routing/
repair/capacity, independent WAN/NAT and production/security review. Sessions/
challenges remain RAM per S02-04, not an invented durable-token requirement.
Graphical games and final domain-root cutover remain deferred.

Current final private source/main and clean webhost checkout: 9c92c97cbf396156de2a7327f0391b2c17d8e115. Result bundlec4339b059483db693affb1711c64ae6f70e4521419ad4154f93cfbd0947ae4df (21 files). native14-handoff-source-sync-result.json PASS binds parent handoff under lock and unchanged final config/PIDs/hosting. Exact failed diagnostic log is retained byte-for-byte; git diff check reported its preexisting blank EOF. All owned test processes are terminal, VM retained.


## Routed public groups LOCAL; registered-only guest Internet PRIORITY — 2026-10-23

Live remains native14/R18/config8fc7929f..., issuer459240/steward451333/guest451334,
modernALL/legacyRELAY. /desktop/ and domain root unchanged. No deployment, ports,
firewall, boot, private state or real user tab change this turn. Live root2 expires
2026-10-24 21:43:31UTC. Private VM root4 expires2026-10-23 22:48:17UTC; explicitly
renew before using its native identity again, preserving the same VM/state/keys.

NEW USER CHOICE (explicit): Require sign-in for ALL Linux guest Internet: ping,
DNS and web. Anonymous desktop/local Linux/browser P2P remain available. Registered
Internet/private files remain; LAN denied for all. This supersedes prior anonymous
public-network defaults. NOT LIVE YET; prioritize this before group deployment.
Never tell user it is enforced until exact managed rollout and public tests pass.

New local routed-public candidate adds network/routed-room-grant.mjs and routed-
rooms.mjs, optional codi-mesh/1:routed-public-jws/1 signed link negotiation in
peer.mjs/pool, config.routedGroups.version opt-in and Rooms host controls. One
existing session pool/budget/scheduler; explicit all-member consent; fixed3–8-member
public star, signed node/member stream grants <=300s, original signed events
verified/forwarded unchanged, scope/hops/replay/global limits, link-loss closes
affected fixed groups. No private encryption/automatic repair. Old2-peer author
restriction kept. Scope/profile: evidence/routed-public-groups.md and
network/ROUTED-PUBLIC-PROFILE.md. Local only, not exported/installed/published.

PASS exact source: routed-group-browser-result.json36checks/3realChromeLinux/2RTC;
routed-four-room-browser-result.json8contexts/4concurrent3-member public rooms/
7physical links/24remote deliveries/0outsiders, independently recounted by
routed-milestone-check.py; unchanged groups survive shared-member link loss; all
budgets release.8Linux guests are LOOPBACK-ONLY (guestInternet disabled in fixture
config), not8guestInternet sessions. First8attempt hit unchanged4-wire gateway
capacity. Separate real4WebSocket/QEMU/fifth503 proof in routed-regression-result
with153ChromeWebCrypto regressions. Three-browser proof DOES include guest relay.
routed-scope-browser-result.json proves real cross-group transplant rejection
without floor poisoning, unnegotiated routing refusal, existing2-person chat/
legal e4/e5/equalPGN-no-chat on same desktop pool. Full M03/full181audit NOT done;
repair/arbitrary topologies/private M05/WAN/capacity/review still open.

Frozen private Git tools/codiserver/routed-public-r1 manifest
374fb7554b4d19dab40bc6f608b31b96105db26df46ced1aac7d550a7f158faa (30files),
source/main/webhost checkout15270c71e177e9eca1780796a5b4ec30cbfef2f7. Tools paths
not public. Retained failures: proxy monitor pre-read drained bodies (fixture500),
test JS brace/quoting/readiness, selector refresh lost ID (product fixed by capture
before refresh), one correction wrong cwd, first8capacity failure. No guards
relaxed. Diff check flagged unchanged helper blankEOF. Core source changed locally
but NOT live; do not run current export as native14 or publish overlay blindly.

Security-policy foundation now LOCAL: guest_service/signin_policy.py adds strict
codi-guest-egress-policy/2 with anonymousInternet:deny, preserves immutable V1
parser/hash. Anonymous all external false inclDNS; registered samebehavior.
frames.py virtualDNS now consults policy.permits on fixed resolver/verified role,
closing its earlier unconditional UDP53 bypass while preservingV1 behavior/ARP.
Policy2 hash for realWAN104.180.210.33/DNS1.1.1.1,9.9.9.9:
436096d722a1bfb42935ca817dcaaf74cec7b2856bf229a4f775cc0c7cd2c049.
V1 remains aa1aa08d...; source .egress.py unchanged.13model/frame/real private-netns
nft syntax checks PASS guest-signin-policy-result.json. Actual kernel/direct
unprivileged numericUID/cap0/NNP sockets PASS guest-signin-kernel-result.json:
anon ping/DNS/HTTP/HTTPS denied, registered unchanged, private blockedboth, unrelated
UID unchanged, scoped internal reply-only control works, counters advanced,
namespace/processes cleaned, no host firewall changes. No installed worker/operator/
native/parser integration yet. Do not claim anon is blocked LIVE from these tests.

NEXT implementation: keep routed experiment frozen; derive an isolated native15
SECURITY source tree from immutable native14R2 .build/releases/connected-ice-
preference-r2, not current WIP routed frontend. Add V15/native/public verification
without changing1..14 contracts, new policy2 parse factory to worker/installation/
runtime/operator and sealed worker/operator2 manifests. Native15 keeps modernICE
capability (render/turn_management/deployment must recognize15 too). Prove browser
login/logout sameLinux and actualkernel/QEMU before public rollout.
Existing network_management requires DISABLE before different backend pins. Safe
planned migration: hold realmaintenance/root journal; issuer+guest stay STOPPED
through native guest disable (schema4), external stopped-only policy/worker/operator
reconfigure, descriptor migration and native re-enable(schema5), then start with
strict kernel ready. NEVER start intermediate legacy/unfiltered guest. Native
controller/config/generator MUST remain managed, no ad-hoc nft/config edits.
Preserve roleUIDs, stateRoot/usage ledgers, permissionsDB, secret/cookie, keys/
accounts/privateFiles; same folder/instance avoids unit renames but needs explicit
sealed reconfigure-stopped method and crash recovery. Existing configure refuses
differing config; do not remove that guard. Retain private journals/old metadata,
never restore old data to undo code. Newfrontend status/README must say Internet
requires sign-in. Old cached recovery modules pin guest policy and may require
explicit reload after warning; do NOT weaken route/identity pins or pretend
unsaved work was saved. Address compatibility honestly before live mutation.
Full goal stays ACTIVE/incomplete. No permission re-ask needed for approved work.


## Public app platform API 2 LOCAL candidate — 2026-10-23

User requested generic dependency bundling rather than xterm-specific loading,
and an explicit element/dispose lifecycle coordinated with existing apps. This
is now implemented locally, NOT deployed. Build-time pinned esbuild0.28.2,
xterm6.0.0/fit0.11.0, lockfile; Node24.22.1 downloaded only under local .build/tools
with official SHA256 verification, no host/system package install. npm ci with
ignore-scripts passes. Builder emits complete hashed JS/CSS/assets/declared-worker
graphs and license notices, atomic API2 catalog, retains previous objects, rejects
missing/remote/computed/linked/outside/private inputs. Loader handles CSS/lazy
imports through generic paths at / and /hidden. mount(host) returns
{element,dispose()}; host.signal/onDispose cover failure and cleanup scopes.
All7 public app sources migrated. Desktop.render disposes before real removal/
replacement/account filtering, preserves workspace/minimize/roll-up. Terminal
input ResizeObserver and composition timer explicitly release; desktop owns PTY
close separately. Shared identity/network/storage/VM are not view-owned.

29 real Chrome graph/lifecycle checks PASS public-app-build-result.json, with
actual npm xterm, CSS/local/lazy/image/WASM and worker-image import.8 real desktop/
v86 checks PASS public-app-desktop-result.json, including all7 apps, real Close
and shell isolation, view replacement/account removal, no browser errors. Exact
source/receipt/catalog hashes and unchanged public R18 app + guest image bound
by public-app-platform-milestone-result.json. Physical Android keyboard/mic not
claimed. Retained failures: file-loader asset strings resolved against document
(WASM got HTML); fixed generic module-relative URL emission for nested outputs.
Strengthened worker test polled an undefined JS global (WebDriver500); uses
window.workerReply now. Failed receipts/logs retained; no runtime guard relaxed.

Private Git source-only tools/codiserver/public-app-platform-r1 manifest
c26d558418362ad408349a725bc62268edd7b941537191f9f15e57f8d865cef1
(38 declared files plus manifest), current source commit 415ca56bd4ea8baa23450409813f5231041d9811.
Initial Git add ignored two declared *.log files; follow-up415ca56 explicitly
tracks both, so the full manifest can be verified from Git. No node_modules,
Node runtime, keys, service state or account files in bundle. Local contributor
README/CONTRIBUTING updated to API2 and explicitly say candidate not live.
See active-system/TERMINAL-UPGRADE.md and evidence/public-app-platform.md.

Xterm migration in the actual terminal is QUEUED, not implemented by the test
app: preserve CDMUX independent PTYs, add bounded resize opcode plus guest
TIOCSWINSZ/SIGWINCH (currently80x24), TERM/terminfo, phone/voice/keyboard/clipboard
and alternate-screen tests. User authorizes a new /hidden boot image when needed,
never /desktop/ or force reboot existing user tabs. Nano7.2-1+deb12u1 i386 already
in downloaded Debian build root with matching libc/ncurses/tinfo; not in browser
image yet. Add nano first, htop next; BusyBox less/top already available. Tmux
optional later (panes/detach, cannot survive VM reload). Curl/CA and larger git/
compiler profiles later. Build separate image, preserve init/9p/VirtIO/setuidping/
PTY and licenses/source notices, prove actual edit/save/parallel shells first.
Current unmodified builder overwrites public initrd: do not use it for probes.

Registered-only ALL guest Internet remains the explicit security PRIORITY and
is NOT LIVE. Existing local policy2/kernel/browser foundation passes; no worker/
operator/native15 integration or deployment. Derive isolated native15 from frozen
native14R2, not current routed/API2 WIP; keep old1..14 contracts. A simpler safe
transition supersedes prior same-folder reconfigure proposal: after managed guest
disable and with issuer+guest STOPPED throughout, use a NEW protected configfolder
with SAME instance, roleUIDs and stateRoot. Preserve permissions.sqlite3 by a
protected SQLite backup while stopped; usage ledgers bind role/schema and can
remain in the same stateRoot. Sealed new worker/operator2 + new frontend descriptor
then managed re-enable, start only once strict kernel guard is ready. Keep old
folder/metadata; preserve external cookie/identity/private files; never start an
unfiltered intermediate guest or undo live data to roll back code. New internal
worker transport secrets may differ; do not claim otherwise. Compound journal/
crash recovery and old cached policy-pin compatibility still need implementation.
API2 publication needs coherent versioned host/loader/catalog/bundles/cache export;
do not overwrite frozen native14 or mix old loader with API2 catalog.

Live remains native14/R18/config8fc7929f..., app9e9cb6ecc..., initrd670aca33...,
root2 expires2026-10-24 21:43:31UTC. /desktop/, homepage, service/hosting/firewall/
router/boot unchanged. Private VM root4 expired22:48:17UTC; explicitly renew same
VM/keys before native identity tests. Full goal ACTIVE/incomplete.


## Guest sign-in integration verified; webhost software INACTIVE — 2026-10-24 UTC

Supersedes prior notes saying native15/operator2/migration are unimplemented.
The retained private QEMU VM now runs native15 R6, strict policy2: ALL anonymous
Linux guest Internet denied, registered public ping/fixed DNS/TCP80/443 allowed,
private/LAN/metadata denied, browser anonymous RTC/chat and separate chess/PGN
preserved. Managed-disable has explicit local-only relay, with no legacy guest
Internet fallback. Real anonymous/registered browser tests30, peer checks7,
fallback checks7, interrupted policy recovery20, rollout recovery5 and bounded
history checks12 PASS. Actual role-UID kernel probes pass. Keys/accounts/cookie,
private saved files, permission rows and usage counters were preserved; code
recovery never restored user data. Receipt hashes are bound by
active-system/.build/checks/guest-signin-standby-milestone-result.json.

Private source Git/server checkout530d93d831c414c8b521df9f89140bed189a829b:
tools/codiserver/guest-signin-r1, manifest
eed6e12ea77d292d437eb2a2a18b434dcbff26e785fb0e456634aefdb3dc5c77
(304 declared files + manifest). Frozen vendor/failure-log whitespace retained.
Isolated source derives from verified native14, not current API2/routed WIP.
New protected IMMUTABLE code successfully installed alongside live software:
- native15 /srv/codi-connected/releases/native15-5fad3b77a5b3f982,
  manifest5fad3b77a5b3f982345c7bd959789509634076059c0b94403f2148146744fcb8;
- worker9f9106e682e51bd5284273fd093994353db6274f887834a12af97828a6907096;
- operator5c51d2c86c214519c21237c41252d41b20a2536d6cdd46f96af37719e9a076fc;
- rollout controllerf51b11cc8ce2af83aa209fedc4b34e2b34aa88251879494608270182a8e8e6e0.
Installer scripts/stage-guest-signin.py supports plan/install ONLY; no activation.
No new config folder or units, no service restart, no kernel/route/hosting/boot
change. Live is STILL native14/R18/policy1, config8fc7929f40629edb4e089a0601289cd54de3203468c3ff925a6e0f519e718b5c,
issuer459240/steward451333/guest451334. Anonymous Internet remains LIVE until
controlled activation. Latest public health PASS all10 sites/default TLS and
133 prototype files. /desktop and homepage unchanged; no private file contents read.

Next priority: truthful sign-in-required Network/README copy and matching cache
manifest/overlay; then planned-maintenance native15 code + compound policy
activation with public anon/registered/file/chat/chess proofs. Existing R18 tabs
pin policySHA and relayRevision; expect explicit reload after a policy/code
change unless proper bounded adoption is implemented/tested. Warn users to save
or download first; do NOT claim automatic browser RAM save. Do not replace an
API1 catalog with API2 bundles without the matching host/loader/cache release.
Generic dependency/lifecycle API2 is locally implemented/tested, not live.
Xterm terminal replacement and nano boot image remain queued.

Private VM3283572 retained, current native5fad3b77..., configfolder
/etc/codi-guest-network/fixture-signin, root revision5 same keys expires
2026-10-24 23:25:27UTC. Live root revision2 expires2026-10-24 21:43:31UTC;
explicit renewal required. No VM recreation/account reset. History readers now
4MiB with original16-record cap after real valid65,780-byte history exposed the
old64KiB bound; failure journals/logs retained and sealed recovery tested.
Full goal ACTIVE/incomplete. No confirmation re-ask for already approved work.


## Repeated app lifetimes PASS; security UI candidate verified — 2026-10-24 UTC

Current private Git/server editable checkout2bcf8c6a9744aa43ec26627f31fea7551afcb593.
SOURCE ONLY: no production services/config/hosting/release changed this turn.
User asked repeat-open/close/reopen every app and current xterm status. API2 local
candidate passes26cycles per7apps,182ordinary opens/closes, all26actual closed
shell PIDs absent from guest /proc, unchanged VM/9p and original shell. Active
app timers/new global listeners/workers/ResizeObserver targets/requests, chat
views, windows, terminal map and network budget return to warm baseline after
five-cycle batches and after late operations. This is a finite instrumented run,
not a heap census, connected-peer churn or registered-server-file churn proof.

The test FOUND a real PGN race: Close during File.arrayBuffer() allowed a parser
record to install afterward, retaining524288metadata bytes. Retained diagnostic
public-app-pgn-race-before-fix-diagnostics.json shows4194304->4718592. Rooms now
checks host.signal after file read and disposes only its room/PGN view resources;
Chat releases its view subscription. appContext exposes scoped release methods.
Files/Text check view/account validity after awaits before follow-up editor,
download or UI work. Accepted writes may finish; no data rollback claimed.
Final13stress checks include late text read, late Files write/no phantom editor,
PGN-before-parser Close and in-flight parser termination. Existing29bundler and
8desktop/v86 checks rerun PASS.50checks/source/catalog/current public R18 hashes
bound by public-app-lifecycle-milestone-result.json. Test-only probe preserves
browser native call receivers after an initial Illegal invocation harness bug.

Private source/proof bundle tools/codiserver/public-app-lifecycle-r1:
manifest66a1c6f72f7e858210d2a1fedb56f0c03b7c0c999101c7b1b66ab9d6c5778403,
28declared files. Combines with prior public-app-platform-r1, not live API1.
All source files/receipts and selected emitted app graphs tracked and verified
on webhost; no node_modules, credentials or personal service state copied.

Separate API1 SECURITY candidate native15R7:
ec6a637c197684921a3ac18ee87a1d1d6380a0a5984ece1cdb40884db627bbed,
227declared files; local .build/releases/connected-signin-r7. Changes only
app.js/desktop-apps.js Network/README copy, Help/catalog and matching cache/
worker/release records. Full backend bytes equalR6; preserves old Help object.
R19six-file frontend4280b4b9e25207d76f179922d367a7e1a31ce15df0f77d829b583281ba450fca.
Managed routing candidate .build/hosting/signin-r19 validates actual Caddy syntax,
generator unchanged, exactly KSU frontend pin change; NOT APPLIED. Offline helper
needed both actual hardware_hosting.py/cardboard_hosting.py siblings; initial
missing-import failures retained. Actual retained VM code upgrade PASS,35real
browser/account/network/UI checks and11cache/offline/rebuild checks PASS. Initial
cache harness used system Python without aiohttp; existing .build/auth-venv passes.
Private VM3283572 now /srv/codi-network-fixture/candidate-ec6a637c19768492,
issuer782271/steward782274/guest782276, same policy2/root5/keys/data. Root5 expires
2026-10-24 23:25:27UTC. No VM recreation/reset. Browser fixtures owned/cleaned.

Private tools/codiserver/guest-signin-ui-r1 manifest
a59b210c39f2f0992dcb114e3cb95762aba1e7f634a4bb064434074fce5c387d,
26declared files includes R7delta over guest-signin-r1/nativeR6 plus matchingR19,
helpers/evidence. This is SOURCE ONLY; R7/R19 NOT INSTALLED on box-webhost.
Root stage-guest-signin.py STILL targets R6/source guest-signin-r1 and supports
plan/install only. Adapt reviewed stager/wrappers to reconstruct/verify/seal R7
before live activation; do not pretend the earlier R6install includes UI copy.

LIVE STILL native14/R18/policy1, native config8fc7929f..., PIDs459240/451333/451334,
frontend97b80a77..., app9e9cb6ecc..., initrd670aca33.... Anonymous Linux Internet
remains allowed on live public addresses until explicit maintenance activation.
Root2 expires2026-10-24 21:43:31UTC. /desktop/homepage/hosting/ports/boot untouched.
Prior source-only stage5fad3... remains installed INACTIVE. Next security step:
reviewed R7/R19 source reconstruction/install, elapsed truthful maintenance/save/
download warning, code+compound policy migration, coherent frontend activation
and default-trusted public anonymous/registered/private-file/chat/chess proofs.
Old R18 clients pin relayRevision/policySHA and need reload; no auto RAM save.

XTERM STATUS: still planned, not the real renderer and not live. Real npm xterm/
fit is proven in the generic bundler fixture only. Next terminal work is one
instance per view over existing independent PTYs, bounded resize opcode plus
guest TIOCSWINSZ/SIGWINCH, phone/voice/IME/clipboard/alternate-screen coverage,
and new nano image. Keep API2 lifecycle and security-only API1 release separate;
do not publish a new catalog over an old loader. Full goal ACTIVE/incomplete.


## CURRENT LIVE native15: sign-in for ALL guest Internet — 2026-10-24 UTC

This supersedes every earlier note saying strict sign-in is not live or that an
R18/R19 frontend overlay is active. /hidden now runs native15R7 manifest
ec6a637c197684921a3ac18ee87a1d1d6380a0a5984ece1cdb40884db627bbed
at /srv/codi-connected/releases/native15-ec6a637c19768492 (227 declared files).
Native schema5 config SHA22eec0f5b47841e8994b72954e3cfa119bad8177333319bc5c93b915f9cb3403.
PIDs issuer720112 / steward717561 / guest720157. Bootstrap stopped; all three
native units still disabled for boot. Development labels and root delegation2
remain; root expiry2026-10-24 21:43:31UTC still requires explicit renewal.

Strict policy2 is ACTIVE: every anonymous Linux Internet request denied.
Registered public ping/fixed DNS/TCP80/443 including host public IP allowed;
private/LAN/special networks denied. Local Linux and browser anonymous RTC/chat/
separate legal chess/PGN remain usable. PolicySHA
436096d722a1bfb42935ca817dcaaf74cec7b2856bf229a4f775cc0c7cd2c049.
Backend config /etc/codi-guest-network/ksu-signin/managed.json SHA
91e883c1ecb304a0b807bdcf3969ba348905af5ec488365c104b1d811c8da812,
frontend descriptorSHA89c1db6594fea81720752863a6ee0ba3ad8627b11c0eca7256c97436b192d21b.
Worker2 9f9106e682e51bd5284273fd093994353db6274f887834a12af97828a6907096;
operator2 5c51d2c86c214519c21237c41252d41b20a2536d6cdd46f96af37719e9a076fc.
Same roleUIDs976/975, roleGIDs970/969 and stateRoot /var/lib/codi-guest-network/ksu.
Permission rows copied with SQLite backup while frontend stopped. Accounts,
signing keys, external cookie, saved-file services/config and durable usage
counters preserved; no user-data restore. New internal worker credentials differ.
Old config folder retained; old managed unit generation is superseded.

All six R18 overlay files equaled native14 public bytes. Through managed hosting
lock/validation/backups/apply they were retired WITHOUT a byte change; native15
then published coherent public UI/Help/catalog/cache and backend together.
KSU codi_frontend is now ABSENT. R19artifact4280b4... was NOT selected/installed.
Generator unchanged718934ce2d95a9ebea7e96b386027b1c0523a7390c310e74c8eba009cd8a10a4;
sites.toml c946c1e71461a49692332f4287633f64ab6e4bebb97283a4263d53bf98f10715;
derived Caddy694518124e11bd918471cfc4b10ad3164d557bba0d003cc1de01fe7ce214dbad.
Preserve redirect `redir * /hidden/ 308`, speech R3 and existing TURN/shared443.
No router/extra ports/forwarding/unrelated firewall/boot-policy change. All10sites
and133prototype files PASS. Homepage/current website release and /desktop unchanged.
App f3961104622743a656a3315b538518a2ac9b8ee21b04c11f7a1f530dd934dc3e;
boot image remains670aca33bf51ffacec21eb0340a8c7f55356d5c9298ca9b55288d955fb5a7d9b.

Real60-second public notice/lock exercised. Notice now cleared, all native
journals clean. Root receipts under /srv/codi-connected:
unified-assets-1792804731401782887-result.json,
signin-public-code-1792804804755458714-result.json,
signin-public-policy-1792804872390073578-result.json.
Opaque controller f51b11cc8ce2af83aa209fedc4b34e2b34aa88251879494608270182a8e8e6e0.
Protected /etc/codi-connected/ksu/signin-public-verification.json stays PRIVATE;
it is verification state, not a blanket permission for restoring user data.
Downgrades below native15 are rejected while policy2 is bound. Use exact sealed
journal recovery if pending; do not restore old overlay/cache or relax to V1.
Hosting manifest backup /var/backups/webhost-sites/change-20261024T011841652932Z.

native15-live-milestone-result.json PASS binds46unique default-trusted public
Chrome checks:20account/network/private-file,7anonymous RTC/separate chat/chess/
PGN,11cache/offline/clear-rebuild,8three-browser actual menu/pool. Three-browser
suite passed twice in fresh profiles: two simultaneous games, separate chats,
bounded pending invites, duplicate refusal/disconnect isolation, actual End
session and all network charges released. Generated QA files removed/accounts
disabled. No real-user file contents/credentials read. Independent WAN, physical
Android and a fresh TURN-only proof are not claimed by this rollout.

Owned old tab retained same VM/9p/file/editor across backend restart; old config
pins require explicit reload. Reload lost the RAM-only file as warned. Cached
older versions may require all desktop tabs closed/reopened for a waiting worker.
Do NOT claim automatic VM save or seamless old-cache adoption. Improve explicit
cache update/reload UX. Both managed guest stops hit existing10s SIGTERM limits
and systemd SIGKILLed451334/717560; restart/health succeeded. Keep this evidence
(native15-guest-stop-observation.json); graceful WebSocket/service shutdown is
still follow-up work, not proven graceful or uninterrupted streams.

Retained harness failures: observer tried typing into intentionally locked UI
and delayed notice clearing; same browser was recovered/read via9p then reloaded,
not restarted due observation timeout. First peer ping step ran during lock;
corrected readiness test passes. First account proof failed in final fingerprint
metadata on wrong native gateway-client path (external file artifact); corrected
repeat passes. Pool harness used obsolete #logout; updated actual session menu.
Another second-invitation timeout remains unexplained; final enabled-control/
fresh-code checks with diagnostics passed twice. Do not claim its cause was proved.

Deployment source be764807eb0feade9e272b2d4fe501d64401fe4c. Current private main
and clean webhost checkout72eaf0832aeda9ed833e8fb1bf45429d9794a728, which adds
source/proof-only tools/codiserver/native15-live-results (34 declared files),
manifest1bba46c1cd68083fe44cb6e9f5b2baaf40d367e46c41ce6582e9f53fa0309787.
All35 tracked files verified after locked ff-only pull; native config/PIDs stayed.
Current evidence active-system/evidence/native15-live.md and native15 live health/
final-inspection/source-sync receipts. Historical candidate bundles unchanged.

NEXT USER TERMINAL WORK: implement the actual xterm renderer, existing independent
PTY wiring, bounded resize opcode + guest TIOCSWINSZ/SIGWINCH, phone/voice/IME/
clipboard/alternate-screen checks, new nano image. Xterm only works in packaging
fixture so far. Generic API2 and50local lifecycle/build checks are separate,
NOT LIVE. Keep old API1 clients/catalog URLs compatible; publish matched versioned
host/loader/catalog/assets/cache together. Current canonical root has routed/API2
WIP and older native backend; never blindly export it over strict live native15.
Derive next native candidate from verified strict15 backend and deliberately
integrate reviewed UI/boot assets. Private VM3283572 remains native15R7/root5,
expiry2026-10-24 23:25:27UTC. Full networking/login/v0.1-v0.3 goal ACTIVE/incomplete;
remaining roadmap, independent-WAN evidence and future domain-root cutover remain.


## Real xterm and complete document workflow LIVE — 2026-10-24 UTC

Supersedes prior notes saying xterm/API2 are queued/not deployed. /hidden/ now
runs native15 6789b29e7ed65ff2087e791448306ba68ab0b8bcc45ed70cdaa60a23fa404f35,
/srv/codi-connected/releases/native15-6789b29e7ed65ff2. Schema5 config SHA
4cddd032111cf5a55d94a491d81635bc14ed1f1374190226429fc2716773a88e.
Issuer/steward/guest PIDs838219/838221/838222; bootstrap stopped, boot disabled.
File worker fd17711bbb04f7af4cd7c79237f90604cc2b680621d0d26f1d193128c1cd0b9e
at /srv/codi-gateway/releases/<SHA>; file config SHA
32af07a6ddabaa9e537f839cb5e963442d4595bcf39f8a6bc8b242327b8a2ef7,
worker/proxy PIDs836284/836286. Existing operator8fdbbdda... unchanged; static
private-namespace units and account UUID folders remain. No data restore.

Actual xterm6/Fit/Serialize uses generic bundled graphs/CSS/licenses and API2
{element,dispose()} with scoped cleanup. Independent Linux PTYs use CDMUX/2,
TIOCSWINSZ/SIGWINCH and 64KiB credit each. The versioned nano7.2 image is
90908996eb63db9bc686b4a5e4e8434a4e8f4fa94410ee159d6631acc98482b8;
old670aca image, API1 host/catalog/loader and xtermR1 assets are retained for
existing tabs. New coherent host assets are versioned; do not copy canonical
Root backend/routed experiments over this sealed strict15 release.

Completed workflow: sign in → Files/My server files → open Text/edit/Save →
Files updates → Word count on server → separate persisted report opens in Text.
Document-only desktop.open accepts copied/frozen primitive context; Text validates
and fetches authorized contents. Save As matching uses current document state,
not stale initial launch context. Navigation is not business completion/RPC.
Word count is one bounded synchronous server operation, UTF8≤1MiB, read/create
ACLs + exact source SHA. Separate private document-operations.sqlite3 records
accepted report/completion; retries survive process death, source changes and
app closure. No arbitrary shell/network/agent work. Reports edited/deleted by
users are not silently replaced. Record caps256/account and10000 total.

Default-trusted public Chrome:28xterm/nano checks,20strict account/Internet/file,
7RTC/separate chat/chess/PGN,19document workflow,11final cache/offline/rebuild.
Local store18checks includes two actual process-crash points; real signed HTTP13
tests; installed file-code recovery two actual killed-process boundaries; latest
lifecycle182 opens/closes and26 closed Linux shell PIDs gone. Phone is emulated
touch/viewport/IME, not a fresh physicalS25 mic/keyboard test. All12changed assets,
all10sites and133prototype files verified. /desktop and homepage unchanged.
Initial public workflow console classification failed; exact first entries were
not captured. Repeat records only two expected gateway404() during other-account
denials, with strict no-errors checks before/after. Preserve failed receipts.
Generated test files removed; both runs' four QA accounts disabled; other policies
unchanged. No real-user file contents/credentials used for testing.

Hosting hashes unchanged: generator718934ce2d95a9ebea7e96b386027b1c0523a7390c310e74c8eba009cd8a10a4;
sites.toml c946c1e71461a49692332f4287633f64ab6e4bebb97283a4263d53bf98f10715;
Caddy694518124e11bd918471cfc4b10ad3164d557bba0d003cc1de01fe7ce214dbad.
No frontend overlay; strict policy2 436096d7... (all anon guest Internet denied),
worker2/operator2/control config, cookie/keys/account DB, TURN/shared443, speechR3,
router/firewall/ports and boot policy retained. All native and file code journals
clean; notice cleared. Existing tabs may need all /hidden tabs closed/reopened
for waiting service-worker activation; save/download first. VM RAM is not saved.

Publication source093396c9f073cb5da8043eddcb4c24d0111fa434. Prior xtermR1 activated
from5784390a99c7d425fc473cbb16311b0ce863b3ab; a3a5c3dd documentR1 inactive only.
Root receipts /srv/codi-gateway/document-upgrade-1792810329154799308-result.json
and /srv/codi-connected/ui-native-1792810403485328133-result.json.
Native controller f51b11cc... unchanged. Scoped file-code helper245ff09a... under
/srv/codi-gateway/code-upgrades/<SHA>/upgrade-private-file-code.py uses existing
operators, journal /etc/codi-connected/ksu/private-file-code.json and code-only
recovery; never restore account/permission/file data. Coordinate UI/worker/cache
rollback; old/new private graphs and supplied baseline bundles remain immutable.
See active-system/evidence/xterm.md and evidence/document-workflow.md for exact
proof scope, retained failures, source artifacts and recovery details.
Root2 expiry2026-10-24 21:43:31UTC still needs explicit renewal. Full goal remains
ACTIVE/incomplete; marketplace/payment/agent infrastructure, remaining roadmap,
independent WAN/physical-device proof and future domain-root cutover are deferred.

Current private main/server checkout54f1bb9e276e2360dc85f0cfaef51b733fa0a823;
proof-only document-live-results bundle33declared files, SHA
9b0912cfedc93ce0041a294f7cd4229aadea9d11dece007fd0a998d9ab4c1b14.
All34tracked files verified after locked ff-only pull; native config/PIDs unchanged.


## Routed public history profile2 — source/proof only, 2026-10-24 UTC

Previous goal turn made authoritative progress by deploying xterm/API2/nano and
complete durable Files→Text→authorized word-count→Text workflow. This continuation
implements the remaining bounded-history path of the existing routed public
candidate, not a replacement P2P stack or an added chat server.

Source-only config codi-routed-room/2 and negotiated routed-public-jws/2 replace
unpublished profile1. One existing session/PeerPool/identity/budget/scheduler.
Original-author JWS cache:64tokens/1MiB charged RAM, original≤60s expiry; no new
incoming retention without a subscribed view. Verified gaps request≤16slots;
64missing slots/group; one bounded deferred hint/admitted author. Four shared
repairJobs including provider work,2active outgoing/2providers,≤16attempts and
16provider requests/group, one bounded retry,5s absolute deadline checked on
receipt/after verification/before queued sends. Unavailable data remains incomplete.
History chunks use bulk class. Historical fills cannot advance a live stream,
consume a cancelled/expired request, replay into live input or deliver game actions.
No private crypto, new server service, router/ports or graphical game work.

Measured current candidate:23real three-Chrome/Linux/RTC recovery/fault checks,
13synthetic cache/lease accounting cases (not crypto evidence),36existing real
routed-group checks,153existing WebCrypto/protocol cases, actual two-group scope/
legacy chat+legal e4/e5/PGN, and4simultaneous routed rooms across8real browser/Linux
contexts with7links. Histories independently recount24remote deliveries and0
unrelated-room deliveries; all shared leases release. Eight guests have no Internet
configured; separate actual coordinator/QEMU test still4admitted wires/fifth503.
Logical-clock deadline injection is not an OS-sleep/discard or WAN proof.

Retained failures: initial object-valued readiness predicate; correct red test
showing received1/3 but absent2; test reading a deliberately released controller
view instead of retained group state. Those recovery logs remain verbatim. The
aggregate helper shadowed its result with a history list; its log was reused on
successful rerun. The captured tool error and that limitation are recorded in
routed-history-aggregate-failure-record.md; do not call that a retained original log.

Private Git source c9b4a51... contains tools/codiserver/routed-history-r2,
47declared files +manifest SHA
8bf9d42a80e75edc981d46c9df894134dbca4c885d8ff673fe0212fa92cc4741.
Current notes/source head37bf77db3fc6892c11e95aeb1875f28484ca8d89 adds precisely
scoped failure-record/current evidence under routed-history-notes-r2. These are
SOURCE/PROOF ONLY. Do not mutate earlier frozen bundles or install a frontend
overlay. See active-system/evidence/routed-history.md and updated
network/ROUTED-PUBLIC-PROFILE.md. routed-milestone-result.json binds current hashes.

Live /hidden/ remains native15 6789b29e... with private workerfd17711b..., schema5
configSHA4cddd032111cf5a55d94a491d81635bc14ed1f1374190226429fc2716773a88e,
PIDs838219/838221/838222. Public config has NO routedGroups; strict policy2 denies
ALL anonymous Linux Internet. xterm/doc workflow, keys/cookie/account/user-file
state and current saved files are unchanged. All133prototype files verify unchanged.
No live service/Caddy/guest-policy/boot/ports change. Root2 still expires
2026-10-24 21:43:31UTC and needs explicit renewal.

Next: dependency/acceptance audit and a coherent new native/public-asset contract,
versioned host/network/loader/cache package plus actual installed-service browser/
identity/files/guest regressions before enabling routed profile2 under /hidden/.
Current canonical Root backend is older than strict live15; NEVER bulk-export it.
Reuse sealed strict15 +document/xterm baseline. Native15 frozen public allowlists
omit the new history module; do not weaken older verification rules. FullM03 gate,
private-key review/M05, sharding, independent WAN/NAT, production review and full
v0.1-v0.3 objective remain incomplete. Keep goal ACTIVE; graphical games deferred.

Source-sync correction: the first pull reached37bf77d, but exact package verification
refused four declared logs omitted by Git's ignore rules. No runtime change or
server handoff write occurred. Exact logs were force-added, without changing the
47-file manifest; current main/server checkout2f3496e22cbdb1c17e2950058c2107c88807d576.
All48tracked bundle files must verify before using the source/proof package.

Final locked ff-only pull verified all48tracked files; native config and PIDs unchanged.


## Active native16 integration and external test host — 2026-10-24 UTC

User resumed a scoped group/history release goal and authorizes final root/blog
cutover when ready: move current homepage to /blog/, desktop to domain root, keep
/desktop unchanged. No existing users/tabs need seamless preservation.

Live remains native15 6789b29e..., issuer/steward/guest838219/838221/838222,
config4cddd032..., private workerfd17711b..., original homepage/hosting/prototype.
Current installed private VM candidate native16 R5 is814b97be709d9db970f447d8bbe28dce27c52acb1f8fee1f227adc9e80ad1b4b,
.build/releases/connected-routed-r5. Derived from sealed DocR2, not old Root
backend. Six native changes: verifier/operator/launcher/deployment/turn support
plus guest browser SDK; all Python guest security and file worker bytes retained.
Versioned24module graph+5hostscripts. Weak per-view generations fix actual
close-during-create subscription race (R1red, R2both signing/verificationPASS).
R2normal36group/23history/28xterm/20account/19doc/11cache/182lifecyclePASS and
actual checkpoint process-death/recovery/native15rollback/re-upgradePASS.

Actual fifth anonymous R2 guest was falsely UIlocked by four occupied relay
wires. R4strict2anonymous uses no relay sockets, five desktops+account/network/
cookie promotion/logoutPASS. R5keeps optional relay failure separate from issuer
liveness: five registered desktopsPASS, four Internet sockets, fifth saves/reads/
removes own private file. Injected issuer-status failure still locks controls and
recovery restores SAME Linux despite full optional relay. Four is a hard-coded
conservative capacity in coordinatorANDworker, not a four-account/browser limit.
User agrees anon needs no relay and should have browser chat, RAM-only files, no
server folder. No capacity increased; higher wire capacities need coordinated
config/cgroup/rate/churn/quota tests.

R5history23 and graph7PASS. Eight-browser/four-room installed test reached three
active rooms but fourth create timed out; no diagnosis retained in first run.
Improved diagnostic run currently uses same candidate, no product/capacity change.
Investigate exact window errors/budgets before changes; do not reduce test to
three rooms or raise caps to force PASS. Other fresh R5 regressions, full managed
rollback/recovery, external group/history/TURN and deployment remain open.

Private Gitmain/server source-only commit5b1b1bcd7a63b445b9f0ddf88b3a8975e830c38f.
Frozen native candidate292tracked files plus tools/codiserver/routed-native-r5
72tracked files(manifestaee8e79dc0fa393e13fc7555cc13d55a53a829f9a2ced3e243ddd8634f4f40bc).
All364files verified after locked ff-only webhost pull, config/PIDs/homepage
unchanged. This is source/proof only; no native16 installation/activation.
Prepared stage-routed-native-release.py uses exact source/pins and existing
managed checkpoint/controller; root staging plan only is next. Controller SHA
705c53c5cba661aecaefc7e03626ab6c489fed5fd799ab59437ccb436f5493a3 supports16.

External moonpie=100.105.243.29 SSHusermaint(existingkeyworks; nosudo). Observed
WAN24.126.137.85 versushome104.180.210.33. Default-trusted remote Chrome Linux
bootPASS; smoke browserclosed. DriverPID10277/port55341 is loopback-only in
/home/maint/snap/chromium/common/codi-wan-check-1792815874220890850, forwarded to
local19516 by owned SSHsession87615. Retain for upcoming public WAN tests, then
clean up owned browser/driver/tunnel. Tailscale control or100.64/10ICE paths do
not prove public WANapplication traffic. USBtether unused; user told disconnect.

See active-system/evidence/routed-native-integration.md and .build/checks current
receipts. Root/blog cutover needs explicit managed native/gateway mount-binding
migration plus generated routing, not justCaddyrewrites. No public live change
until verified. Root2delegation expires2026-10-24 21:43:31UTC, explicit renewal.

## Native16 R8 live activation and WAN diagnosis — 2026-10-24 UTC

This supersedes prior notes saying native15 is still live or R8 is source-only.
/hidden/ now runs /srv/codi-connected/releases/native16-6fbca9e61a02008c,
manifest6fbca9e61a02008c32b917e2db5cb8805271b2f6300d97338ea976532cd97200.
Private Git/server source41ad4bf7bf6442ba5fed16c9805706bfa43ea1d1 verified
394 declared candidate/source files. Managed checkpoint upgrade PASS; existing
31 accounts, keys, cookie and authority preserved; no data restored. Controller
705c53c5cba661aecaefc7e03626ab6c489fed5fd799ab59437ccb436f5493a3.
Current schema5 config SHA a8249551a9191a33ecee227e95b3327e7a394090379bde87429ff68243aadc2f.
Native issuer/steward/guest PIDs1071614/1071616/1071617, disabled for boot.
Private-file worker/proxy PIDs836284/836286 and their config unchanged.
Root activation receipt /srv/codi-connected/routed-native-upgrade-1792821745139470391-result.json.
Local receipts routed-native-{install,upgrade}-result.json and source-sync/plan
under active-system/.build/checks bind exact hashes; rollback to native15 was
exercised in the installed private VM, not on the live site.

Public exact-index/group2 config, strict account/files/network20 and all10-site
health PASS. All133 /desktop prototype files and homepage/hosting pins unchanged.
R8 public indexSHA d403f591d837b076abf5a6da54d09306de67cba7a8a715676250ccb362250612.
R8 direct memory/discovery25, cache11, graph7 and managed process-death recovery/
rollback/re-upgrade PASS. Comprehensive group/history/xterm/document/lifecycle
proofs were executed on R7; R7/R8 exact equivalence receipt limits their difference
to two phone touch-target style assignments. Do not label those as direct R8 runs.

First actual Moonpie WAN history test FAILED at peer readiness. Home/home forced
TURN/TLS selected successfully; outside pair did not connect within30 seconds.
Diagnostics routed-wan-history-diagnostics-1792821973525431928.json and original
routed-wan-history-relay-r1.log retained. Moonpie DNS104.180.210.33 and public
turn.ksu.codes:443 TLS verification PASS. Expanded diagnostic adapter observes
failed ICE states/candidates without exposing SDP secrets or changing ICE policy.
The WAN claim remains UNVERIFIED. No rollback/cap/ports/firewall changes followed
the failure. Do not treat Tailscale control or a home/home relay as outside proof.

128MiB is a configurable per-tab shared accounting ceiling (32..1024MiB), not
physical reserved memory, per-user/per-channel allocation or measured8k capacity.
Future full gossip/islands/checkpoint/PoW/8k requirements remain PLAN in ROADMAP.md.
Next: diagnose outside ICE, complete public workflow/cache/xterm/group/history/
chess checks, then separately tested managed root/blog migration when ready.
Keep /desktop untouched and current homepage until that conditional cutover.

## Public R8 regression and bounded TURN profile — 2026-10-24 UTC

Public strict account/network20, document composition/persistence19, xterm/nano28,
public-only cache11 and actual ten-second maintenance warning/lock/cancel PASS.
Maintenance preserved same VM/filesystem/session/editor/cursor, all native PIDs
and config; it did not save work or restart services. Generated document QA files
were removed and the two witnessed disposable accounts disabled; unrelated
account policies unchanged. Cache persist request returned false honestly;
public assets cached, private files/credentials/config/API excluded. Offline
reload cannot restore Linux RAM; server return creates a fresh Linux session.

Expanded WAN diagnostics show TURN486 errors and empty candidates for the second
pair on BOTH hosts. Actual local authenticated allocation test and reviewed
Coturn source confirm bps-capacity reserves max-bps per allocation: legacy256KiB/s
from1MiB/s admits4, regardless count quota64. This was a relay admission bug,
not evidence that outside DNS/TLS failed. DNS/TLS were independently trusted.

New immutable relay operator0e38b15e24488acb4d9cf511bd09f493cfce9aba2ab79a45cd44b004025213e1
supports explicit text-32k/1 config3 profile:32allocation quota at32KiB/s EACH,
SAME1MiB/s aggregate reservation cap, username quota8 unchanged. These are
allocation limits, not participant counts or an8k guarantee. Private loopback
namespace/no capabilities/ports/host isolation remain. Profilechange preserves
secret/cert/topology and interrupts TURN/proxy streams. Explicit legacy rollback
returns exact config035fa4f6f6afa209bd933e84d8284f985306b2d31964408b9709e9c5a24f5a1f.

Local proofs PASS: actual32allocations/33rd486, per-user8/9, legacy4/5, metadata/
secret preservation, no-op PID preservation, actual process death in prepared
and committed profile transitions and correct recovery, rollback, certificate
refresh8 for config3 plus existing legacy lifecycle12/export7. Fixtures cleaned.
The initial new raw-TURN test had an invalid x509 SAN argument; retained failure
log relay-bandwidth-profile-check.log, corrected reruns PASS. Not a product bug.

Git/server109fb102b555825aade9d5f2df8b22f4aa3cf017 verified40new files: operator6
plus routed-public-r8-proof-r1 package34, proof manifest
71832b971beffb580173f79f6ce7ccb1491cb1caf8d182b88092fe4d38914afa.
Pinned stage-relay-text-profile.py plan/install/apply/rollback/reapply PASS live.
Root-private outer migration journal coordinates profile and certificate-job
path/timer; no Caddy/native/website/private-file PID/config or ingress changes.
Actual scheduled certificate job executed on each generation. New profile ACTIVE,
relay configSHA5ab3e23016cd673146f1c6925aac0826368a4eff54b0fabdb9a28d7276c998a4.
Receipts relay-text-profile-{apply,rollback}-result.json retain exact root receipt
paths/PIDs. WAN rerun is in progress; do not claim outside peer success yet.
The historical webhost-relay-health.py still targets original installation
receipt/operator/PIDs and is superseded for changed profile by these receipts.
Do not run it expecting unchanged old relay PIDs. Root blog cutover not started;
/desktop and homepage stay intact. Full8k gossip design remains PLAN only.

## Current public WAN acceptance — 2026-10-24 06:38 UTC

R8 actual public three-browser suites now PASS across home104.180.210.33 and
Moonpie24.126.137.85: routed group36, missing-message recovery23, scope transplant/
legacy capability negatives and legal chess e4/e5 with matching chat-free PGN.
Both sides of each actual outside pair selected relay/relay TLS through public
turn.ksu.codes:443; normal certificate validation, no proxy/cert exceptions and
no HTTP chat payload relay. Tailscale was automation/control only. Each suite
closed its owned browser sessions. Active external driver/tunnel remain reserved
for upcoming root/blog cutover tests, not exposed publicly.

routed-public-wan-milestone-result.json binds exact three receipts/native16R8/
relay operator and records the inherited history fixture's obsolete
independentWANTested=false flag; its adapter independentWANVerified=true has
selected-pair proof. Original receipt preserved; later adapter overrides the
inherited flag. These are3real browsers per suite, not a full gossip/island/8k
measurement. Fresh all10-site health PASS. Prototype133files and homepageSHA
55f2928da214010b2ed7d647a354c0052ae03e9d06bafc09c1ea3b67e8608a38 preserved;
website release20261023T043853468523Z-314447db unchanged. Native configSHAa824...
and relay configSHA5ab3... unchanged, no pending relay journals.

Conditional root/blog cutover remains authorized and NOT performed. Read-only
binding audit confirms this is more than a Caddy switch: native managed mount,
private files mount, guest worker issuer API base, issuer/discovery public policy,
root authority template/grant endpoint and publisher's bound endpoint all need
one journaled migration. Existing root renew/code-upgrade APIs explicitly refuse
mount/binding changes. Preserve keys, realm, account/home mappings and publisher
revision/replay floors. Rollback must sign a higher authority/publisher revision
for the restored endpoint, not restore an old authority/ledger DB. Exercise this
in private VM before live cutover. Homepage moves to /blog/, desktop to domain
root, /desktop stays unchanged; no old-tab compatibility infrastructure needed.
The current release is usable under /hidden/ while this remaining work is done.

Public WAN proof follow-up is frozen in private Git cfb269d16ba5eaac3efd73b01db4709246e57486, tools/codiserver/routed-public-r8-proof-r2,28files manifest995025c516353564606d67f3a6f051199be4e90e7fca4a12039be4c3c2d7e25d. Driver/tunnel retained solely for upcoming cutover tests; five owned closed Moonpie Chrome profiles removed. No new external hosts/IPs needed for present release tests. Propose3–5independent networks incl cellular for broader resilience;8k protocol clients can share several load-generator hosts, not8k publicIPs, and do not prove8k full v86 desktops.

## Current state — root cutover phase3, 2026-10-24 10:02 UTC

This entry supersedes older current-release/VM details. Production remains
native16-3071d17fa17666e2 at /hidden/, config39d88cd8..., native PIDs1243423/
1243425/1243426. Homepage and133prototype files unchanged. Terminal touch toolbar
already includes Ctrl+C,Ctrl+O,Ctrl+X,Tab,Esc,Enter,Copy,Paste,Clear; actual nano
save/filename confirmation/exit and swipe scrollback pass public Chrome38checks.
Floating keyboard toggle remains; local Keyboard/arrow/Help buttons are removed.

Private VM actual signed mount migration, interrupted recovery and forward
rollback pass. Real root Caddy/blog/native composition also passes38terminal and
19document checks; worker/cache migration17 and real VM offline/cache11 pass.
See active-system/evidence/configurable-mount.md and root-hosting-cache.md.

Candidatec23b1b73... and mount operator6e4ebb33... are installed on webhost as
INACTIVE immutable artifacts. Source commit8f605fa2bbd37f9525d71354e26a0e2d16046c07,
373declared files verified. Actual Caddy validates candidate prepare+production
routes using on-server private auth import; actual readonly mount plan passes
24metadata edits/prospective root3 without changing actual root2/fence/token/PIDs.
Root receipt /srv/codi-connected/root-cutover-install-1792835854213111621-result.json.
No activation, production notice/restart or root/blog cutover in this phase.

Retained VM is c23... at actual root, root/fence12, native1549121/1549123/1549124,
Python ingress1553745, SSH49747/HTTPS57503. No pending journals or test Caddy unit.
No old snapshots/user DBs restored. All owned Caddy/blog/tunnel fixtures cleaned.
The full goal remains ACTIVE. Next implement and VM-test coordinated production
website/code/signed-mount/hosting recovery+forward rollback before public cutover;
then public/WAN acceptance. P2P islands/checkpoints/PoW/chess audience/8k remain
required. Root2 delegation expires2026-10-24 21:43:31UTC; explicit bounded renewal
only. USB tethering is not needed; owned Moonpie driver/tunnel were already closed.

## Coordinated cutover proof — 2026-10-24 10:42 UTC

Production remains native3071 under /hidden/ with unchanged config39d88cd8...,
native1243423/1243425/1243426, homepage, hosting and133prototype files. No public
root/blog swap yet. Nativec23/mount6e4e candidates are inactive installations.

The new five-file site operator9722b19b... passes7actual VM process-death/recovery
cycles spanning code,website,authority,partial hosting,Caddy reload,commit,receipt.
Rollback signs higher revisions and retains website code pointers without user
DB restore. Four pending native/hosting phases refuse ordinary start/signing.
All133prototype HTTP hashes checked per commit, existing keys/accounts/cookie/
private files retained and usage nondecreasing. Sealed CLI6negative cases pass.
Post-recovery root Chrome terminal38/document19 pass; fixture TLS only.
New root-aware smoke checker's default branch passes10actual live sites with
ordinary TLS, no production changes. Root branch not yet live.

Private VM is NOW c23/root20, native1647918/1647914/1647962, original ingress1649323,
no pending journals, temporary website/Caddy stopped and Caddy unit removed.
All setup failures retained; journal recovery used, never fixture/data reset.
See active-system/evidence/coordinated-cutover.md and site-cutover-*-result.json.
Next freeze/source-verify/install standalone operator, private exact production
plan + readonly preflight, notice/cutover and public/WAN acceptance. Root2expires
21:43:31UTC; explicit bounded signing only. Full distributed-networking/8k goal
and requirement reconciliation remain ACTIVE/unfinished.

Phase4 operator/proof source is now clean/verified on webhost at
a4de6ef2dba24ce0916fa1bd4f8c749471891e63,39files including both manifests.
root-mount-r4 proof58e062123e6cfb04cf3d30c605951a511670eea4771a5667bfc4811d90a442af.
Initial sourceaf3bca1 omitted5ignored declared logs; verification refused it,
scoped additions fixed delivery without changing immutable bytes/history. Site
operator9722... still NOT installed on production; config/PIDs unchanged. Next
inactive install/private exact production plan/readonly preflight, then cutover.

## ACTUAL ROOT/BLOG CUTOVER — 2026-10-24 11:06 UTC

Desktop https://ksu.codes/ and blog https://ksu.codes/blog/ are LIVE. This replaces
older hidden-only state. /hidden entry redirects to root. /desktop133original
bytes, guides, static/test-time and other9sites preserved. Root is the actual
native/file/guest/signed-discovery mount, with no internal root→hidden rewrite.

Nativec23 at /srv/codi-connected/releases/native16-c23b1b73df68ffb2;
config568bcd2a10e6256b885eb7b36b045a3e7497d4f06bac474d901ff37cbc0280b1;
issuer1460700/steward1460696/guest1460759, still disabled for boot; bootstrap off.
Root/fence3 expires2026-10-25 11:06:16UTC, explicit bounded signing only. All35old
account rows, keys/realm/service identity/cookie preserved; no user DB restore.
Registered-only egress policy436096... and TURN config5ab3... unchanged.

Website20261024T110552353972Z-299874f5, old20261023T043853468523Z-314447db retained.
Hosting generatorc318.../sitesf583.../Caddy4cf.../smoke206...; all10live sites pass
ordinary-TLS checks including root desktop and/blog. Standalone operator89557858...
and mount6e4e... are installed; source5fa9221bb36af53e4dcd311d91524f54e2fc9211.
Root receipt /etc/codi-connected/ksu/site-cutover-last.json; cutoverid
622064c8449c473c6eb156ba56e14643. No pending journals. Real10second notice ran;
RAM was not saved. Rollback uses a new inverse plan/higher signed revision and
retained code/generated hosting, never old account/authority/publisher DB restore.
See latest AGENTS entry for exact private plan, backup paths and guarded workflow.

Public ROOT ordinary-TLS terminal38, documents19, lifecycle13/182opens/closes,
cache11 and account/registered-only guest-egress20 PASS. Owned QA files removed
and accounts disabled; other user policies untouched. Root health verifies327
nativefiles,133prototypefiles,35old account rows and current guard/pins. External
group36/history23 also pass across home104.180.210.33/Moonpie24.126.137.85 using
actual public TURN/TLS443 at both ends; scope/chess suite is still running.
Initial outside history browser tab crashed during startup; fresh repeat passes,
cause unproven, failure kept. No product redeployment or data reset for that retry.

Moonpie's owned driver/forward remain active for final scope test; use current
moonpie-browser-fixture.json and moonpie-root-browser.py cleanup afterward.
Private VM is now actual root24/c23, no pending journals, original ingress restored,
temporary website/Caddy stopped. The full P2P/islands/checkpoint/PoW/audience/8k
and complete requirement-audit goal remains ACTIVE and incomplete.

Root WAN follow-up COMPLETE: group36/history23/scope+separate legal chess/PGN PASS
across104.180.210.33 and24.126.137.85 with3real browsers per suite, ordinary TLS,
actual public TURN/TLS443 at both ends. No direct-UDP/full-mesh/8k capacity claim.
Moonpie driver12990, local SSH forward3739216 and all owned profiles are now
stopped/removed, independently checked; no external fixture remains. Root final
health and bound root-live-milestone-result PASS. Initial outside tab crash remains
an unexplained retained failure; fresh unchanged-product repeat passes.
Current evidence active-system/evidence/root-cutover-live.md. Root/blog publication
requirement is complete; full source/request audit and required distributed
networking/checkpoint/PoW/audience/8k implementation remain next, goal ACTIVE.

Source-only mesh follow-up now has actual desktop/Rooms integration:155protocol,
46pooled-RTC and23three-v86-desktop checks PASS. Includes cancellation, pause /
rejoin, workspace drafts, bounded refusal and account-change app disposal. Frozen
mesh-host-r1 is pushed asbe5fe79bbaa4fb0acdcab97354e3992cc3023c7f, manifest
3527c74675428866c2963d9b20555362198a53ce2d31a12851a884b6c01ab2c9,243tracked files.
No webhost source pull/native install/public rollout occurred. The root/blog
runtime above is unchanged. See active-system/HANDOFF.md and
active-system/evidence/mesh-host.md for exact evidence, missing features and the
next managed-release/VM gates. The whole goal remains active/incomplete.

Mesh17 follow-up: coherent native/frontend/cache artifact is now installed and
verified in the retained private VM at actual root. Native manifest8a90a16e...;
release17, mesh23, terminal38, documents19, lifecycle13/182cycles, CPU voice,
mobile account/egress35, process-death/recovery/c23rollback/re-upgrade4 and
custody2 PASS. All7QA accounts disabled, test files gone, no pending journals
or owned browser contexts. Complete immutable code/proof package mesh-native-r1
is pushed at297267e7b2b0b6ace2bae37694324bf4a9d2cfbf (682verified tracked files).
Production remains native16c23/root + /blog/; prototype/other sites unchanged.
Automatic physical peer introductions/islands/fallback, durable checkpoint and
branch convergence, spectators, scalable admission and real8k load plus audit
remain required. See active-system/evidence/mesh-native.md and active handoff.

Automatic introductions source follow-up now passes network19 and actual
three-v86-desktop23, plus legacy46/protocol155. Eight initial actual RTC browsers
form extra paths automatically; legacy and join-fault fixtures bring total10.
Creator loss, late cancellation, replay/recipient/local-ID attacks, repair and
post-repair once-only delivery pass; exact fault controls fail as intended and
clean up. All owned contexts/charges0. Frozen mesh-neighbors-r1 pushed at
e0b5edb0523a8fe09c8556c921efa141c5b41007 (364verified tracked files). SOURCE ONLY:
private VM stillnative17; production stillnative16. Next explicitnative18graph
integration, then remaining islands/fallback/checkpoints/spectators/scalable
admission/real8k/audit. See active-system/evidence/mesh-neighbors.md and handoff.

Final root-live proof source93717e3c9327f91b68a94724bdc8f575431c4197 is clean and
verified35files on webhost, source-only, no restart/config/PID change. Package
root-live-r1 proof629530a1fd5fd408f54dd4ef8a4852d0798ced5c8cb9ff5718855dc9502e39e1.
Completed forward plan is tied to old activation source5fa9221; new inverse plan
required for rollback. Root health inspection binds root3; don't restore old state
to satisfy it after legitimate renewal. Goal remains ACTIVE.


## Native18 automatic-neighbor VM milestone — 2026-10-24

The retained private VM now runs native18, NOT the older native17/c23 noted
above. Canonical artifact active-system/.build/releases/connected-neighbor-native-r1,
manifest5ee491cc01f314580ec85ccf940f9e6e1944159c1a29e907e66dd738283fd024,
424declared files + manifest. Remote /srv/codi-network-fixture/candidate-5ee491cc01f31458;
managed /etc/codi-native-fixture/managed.json, root mount, SSH49747/HTTPS57503,
existing venv/ingress/state retained. Do not recreate VM or restore old databases.

Explicit native18/33-module graph and --mesh-auto-neighbors preserve native17's
32-module and native16's routed verification. Only5native dispatcher/verifier/
launcher files change,48backend files unchanged; onlyRooms differs among7apps.
All425files reproduce identically. release23; installed automatic-network19 with
TEN actual v86 Linux desktops (8initial +1legacy +1joining/fault), mesh23/3Linux,
terminal38, documents19, lifecycle13/182cycles, mobile account/egress35, actual
CPU/WASM microphone-fixture voice PASS. No physical phone/WAN/8k claim.

Actual process-death recovery, rollback/re-upgrade to retained17 AND separate
exact-public16 each4PASS; custody2; retention-floor controls9; post-rollout mesh23.
No data restore or authority/usage rewind. Final health:6owned QA accounts
disabled and homes empty,0owned Chrome contexts, no pending journals, exact18.
An overlapping account/doc test hit existing60POST/min/IP429; failed account's
file deleted through hash-checked authenticated API with a transient QA password,
then account disabled. Serial35PASS. Original failure/cleanup retained.
First16rollback completed transitions but strict identical-publisher assertion
failed on a legitimate370→371 revision. Exact prior harness/diagnostic retained;
corrected forward-only retention predicate plus9negative/positive controls PASS;
full real16rollback/re-upgrade repeated PASS. Never edit counters to satisfy tests.

See active-system/evidence/neighbor-native.md and neighbor-native-milestone-result.json.
PRODUCTION UNCHANGED: native16c23/root + /blog/;133prototype files/other sites kept.
No webhost pull/activation, ports/firewall/boot/DNS changes or new package installs.
Read-only public root/blog/prototype entry HTTP200 checks use normal TLS only;
these do not replace full-site/browser acceptance. VM uses explicit fixtureSPKI.

Next required implementation: island/layer placement/redundant bridges, bounded
authorized server bootstrap/fallback/return, long-lived scalable membership and
compact replay floors, durable chunk/checkpoint/valid-branch convergence,
spectators, actual mostly-reading/burst8k transport tests and full audit. Current
300sroom/64admission-records-per60s/1024author-streams and issuer60POST/min/IP are
NOT8k authority. Ordinary-TLS independent-WAN acceptance needed for the newprofile.
Private crypto/finality and full goal completion are not claimed. Goal ACTIVE.


Native18 canonical code/proof is now frozen and pushed at
05642006501a16b00c680ead129d62386038cc02, tools/codiserver/neighbor-native-r1.
Manifestdd3361d416909b3d11d7829ecf7e05c97d7e5c9c4606a67dcd59267017887bde:
858declared files + manifest, all859tracked/byte-verified; private Git main
matches and curated tree clean. neighbor-native-source-proof-result.json records
final runtime unchanged since cleanup and0owned browser contexts. Frozen older
packages remain unchanged. No webhost source pull/activation. Next is actual
island/fallback/durable-sync/scalable-membership/spectator/8k work, not another
native18 packaging pass. Keep production c23 until required acceptance is ready.


## Compact replay source milestone — 2026-10-24

Source-only follow-up removes the per-author32KiB/1024stream mesh bottleneck.
MeshGroups now uses OriginReplayGate({compact:true}) and supplies each envelope's
identity proof to receive. Retains canonical key/binding/scope/incarnation/expiry/
64bit sequence window, NOT certificate strings or arbitrary key extras. Rechecks
current identity and origin signatures; caller still authorizes controller grant
before admit. No expiry/closeRoom floor eviction or repeated-admission reset.
Pending identity proofs share the existing queue/control reserve. Shared replay
count ceiling65536; metadata limit still applies. Legacy full-proof gate explicitly
keeps1024streams/32KiB each. These are accounting limits, not measured RSS.

Exact oldsource+harness FAIL at1024 of1100actual certified authors. Final component
8000authors/15checks PASS in one real WebCrypto receiver with preissued fixture
certs/controllergrants/origins and8000distinctP256keys (plus1refusalfixture).
16909780replay-accounting bytes (~16.13MiB) under32MiB default, final~23.2seconds.
NOT8000RTCparticipants/serveradmission/PoW/WAN/fullscale evidence; fixture public
HTTP proof download is not a gossip bandwidth measurement. Two one-line controls
(unaccounted identity queue bytes, retaining extraJWK proof data) FAIL at intended
assertions with allcharges0; other32modules identical. Actual RTCneighbor19/
10browsers, desktop23/3Linux, legacyRTC46, protocol155 PASS. First legacy run
stalls in initialRTC before invitations (one-sided ready/connecting); cause
unproven, failure+0cleanup retained, unchanged serialrepeat46PASS.

Source/evidence current in evidence/compact-replay.md and compact-replay-milestone-
result.json. No owned contexts or protocol fixture server remain. No privateVM/
production changes or newinstalls/ports/firewall/signing. Retained VM stays EXACT
5ee491cc... native18/root; its existing artifact does NOT contain compact change.
Production staysc23native16/root +/blog/; /desktop/ and other sites unchanged.
Do not repackage/deploy as if 8k or long-lived membership is finished.

Next actual implementation: long-lived scalable membership/admission, disconnected
island/layer placement/redundant bridges, authorized bounded server bootstrap/
fallback/return, durable replay/checkpoint/valid-branch convergence, spectators,
real mostly-reading/burst8ktransport/fault tests and fullaudit. Current300sroom,
64admissionrecords/60s and60issuerPOST/min/IP remain separate blocking limits.
No canonical-finality/private-crypto/whole-goal completion claim. Goal ACTIVE.


Compact source/proof is now frozen/pushed at
65e8a232bd89d8eeb8caa797c94139230e9183f5, tools/codiserver/compact-replay-r1,
manifest17662c56dc3cb7f26c25b109f6e982ff3e454dd9afd9447a897b591a31ed86a4.
505declared+manifest=506tracked/byte-verified files; private Git main matches,
curated tree clean. compact-replay-source-proof-result.json binds final check.
All older frozen packages unchanged. No webhost pull or native install. The next
turn should implement remaining networking/authority work, not repackage this
same source again. Investigate the retained initialRTCstall as part of robust
connection/retry/fallback acceptance; unchanged repeat PASS did not fix its cause.
Private VM stillnative18/5ee491cc..., production stillnative16/c23. Goal ACTIVE.


## Renewable /4 room authority and alternate-route source proof — 2026-10-24

Source now has34network modules. Explicit codi-public-mesh/4 + membershipLease
capability only; legacy /3 is preserved and not silently upgraded. Stable signed
policy anchor + fresh same-controller certificate/short chained lease, per-member
renewal retains incarnation/work stamp and replay highest/bitmap. No expired
certificate revival at historical time, peer authority takeover or PoW consensus.
Authenticated same-revision forks freeze only their room; invalid signatures do
not. New helper uses existing pool/scheduler/accounting/control reserve/heartbeat,
not an app socket/timer/full roster. Owner renews at half-life, members at2/3life.
Early refresh with no greater deadline returns the exact existing grant.

Renewals now retry bounded alternative joined paths after successful-but-silent
sends. Original signed request stays unchanged; distance hints are not authority.
At most8attempts/1second spacing,16declared hops,128requests/fourlocal/eightjobs,
24-entry reverse/attempt maps with prepaid metadata,4096bounded completions and
23kBpackets. Verified exact cached replies recover lost responses and duplicate
reverse paths. Mutable hints are not a Byzantine global hop guarantee.

Final mesh-lease-milestone-result.json binds current coherent34-module source:
authority20(real6slease/12scert expiry and fresh90scert); RTC17/fourbrowsers with
actual routed renewal, capability refusal, fork isolation and valid-deadline
controller-loss behavior; alternateRoutes10/fiveactualRTC browsers; desktop23/
threeactualv86; legacy /3neighbor19/tenbrowsers, legacy46/four, protocol155.
Five-browser fault: preferred joined relay silently drops forwarded requests,
healthy alternate loses one genuine reply; gateway/leaf recover past original
24sdeadline with same origin seq1→2/no newadmissionworker/alltrackedcharges0.
EXACT oldhelper + sameworkload FAIL3 with gateway+leaf expired while controller/
otherrelays active. Final one-line historical-clock control FAIL12 and replay-
floor-reset control FAIL14 at intended Expectedrefusal assertions; other33modules
identical. These controls are test oracle evidence, not unresolved product FAILs.

An initial newroutefixture had a missing JS loop brace and failed before faults;
exact harness/receipt retained, correctedfixture parses all33snippets and passes.
Earlier genuine early-refresh failure and corrected no-op response are retained.
No physical-phone/default300s/15day/WAN/8ktransport claim. Earlier 8000-author
component remains a preissued-crypto test, NOT8000RTCclients or admission capacity.
Retained one-sided initialRTC startup stall is still unproven/unfixed.

Read-only finalhealth2026-10-24T19:58Z: privateVM exact5ee491cc/native18 and same
PIDs2215859/2215861/2215862;0ownedChromecontexts. Public root/blog/prototype entry
HTTP200 with ordinaryTLS, blog exactoriginalhash. This is NOT a repeat of the
all10-site/133prototype-byte audit. No VM/native or production changes, webhost
pull, ports/firewall/DNS/boot/signing/data restore or package installs this phase.
Production remains native16c23/root +/blog/; /desktop/ and other sites preserved.

User clarified matches can last15seconds or15days. Transport/certificate expiry
must be independent of accepted-game lifetime and configured game clocks. Stable
player/account seats require fresh session authorization after return. Durable
acceptance/checkpoint/permission evidence must survive restarts; old signatures
alone checked at historical timestamps cannot establish prior authorized acceptance.
During partitions conflicting unconfirmed proposals remain pending; delayed chess
moves must be checked against the current position/turn/permissions, not blindly
reinserted. Separate spectator chat and move lanes remain required.

NEXT IMPLEMENTATION: explicit persistent hosted controller with protected service
identity/key/state and current-account authorization, restart/expired-bookmark
rejoin recovery and durable accepted history/chunk/checkpoint/floor retention;
then island/layer placement/redundant bridges, bounded authorized server fallback/
return, scalable admissions, spectator roles and actual staged8k/WAN fault tests.
No persistent controller/delegation/replicated failover/durable history is yet
implemented. Browser-owner loss still stops renewal and expiry fails closed.
Current source is NOT a native artifact: add a NEW explicit native19/34-module
graph and opt-in config/launcher contracts when packaging; do not loosen frozen
native18/33 or native17/32 verifiers. Audit stays181cases:3completed161partial17
required plus53separate v0.1 cases; no whole gates completed. Goal ACTIVE.


Renewable /4 + alternate-route source/proof is frozen and private-Git main verified
at6dfc444ad4c504bbccb34e15ce82990fdf958de4, tools/codiserver/mesh-lease-source-r1,
manifest7af20b3d7aef3a818b478511a66b013eb10741221cb23695306815f5fe00c4a4.
854declared files +manifest=855tracked/byte-verified; curated tree clean, frozen
older packages unchanged. mesh-lease-source-proof-result.json binds exact commit,
aggregate and read-only health;0ownedChromecontexts. No webhost pull or install.
Next implement persistent hosted authority/history/rejoin and remaining island/
fallback/checkpoint/spectator/scalable-admission/8k work, not another packaging
pass of this same source. Native19/34 graph is required before a new native build.
Private VM remains18/5ee491cc, production16/c23. Full goal stays ACTIVE.


## Hosted authority/history source component — 2026-10-24

Concrete implementation beyond the frozen /4 renewal milestone: new room_service/
(contract/access/store/http), opt-in origin_service/room_authority.py and pure
network/hosted-room-authority.mjs proof helpers. Current source35network modules;
old /4 proof6dfc444 remains EXACT34, private native18 remains33. No newnative graph,
operator/serviceaccount install, UI mode, public config or P2P fallback enabled.
Do NOT silently loosen old graph verifiers. New native packaging must explicitly
include35modules and the new optional backend/issuer surfaces.

Room issuer middleware takes an operator-pinned public controller key, never a
browser-selected one. Separate room-controller certificate/type/audience/scope;
ordinary user identity still rejects it. Live bearer session+key/SID/account-
generation/disabled checks issue <=30s confirmation for exact request bytes. Room
worker never gets login passwords/DB or private-user-folder rights. Short grants
are bounded revocation, not instant invalidation after an already-issued grant.
Worker key+SQLite private0700/0600 initialization is EXPLICIT and empty-only.
Missing DB/key, changed key/schema, inconsistent log/floors fail closed, no repair.
Whole old snapshot restore still needs an external retained floor/fence; no
replicated failover or managed-install isolation proof yet.

Stable registered account owns a durable public room; anonymous viewers can
read/join public chat without personal folders. One-use light work authorizes no
permissions; server separately allows membership, keeps work/stream IDs, checks
current bans on append. Signed chat origin→accepted receipt/index/hash + replay
floor/usage commit atomically. Exact duplicate ID returns original receipt even
with alternate ECDSA signature. Gaps/conflicting sequences remain unaccepted.
Valid authenticated attempts spend nonce/grant even on resource refusal, avoiding
8pending-challenge self-lockout. Accepted receipts attest server acceptance;
expired author certificate alone never authorizes an old live operation.

Accepted history resumes from known index/hash in <=64record/bounded chunks.
Compact signed lease links bridge arbitrary missed revisions in <=64link chunks.
Browser independently verifies fresh pinned authority, policy, origin/receipt
signatures, scope, exact parent hashes, sequence indexes, final head and retained
floors. Missing continuity stays pending; only locally verified proof objects
satisfy multi-revision gaps. Authenticated same-height forks have distinct errors;
invalid signatures cannot poison fork state. Archive helpers return historical
records, no live handler invocation. Durable browser-floor storage is NOT done.

hosted-room-milestone-result.json PASS binds final server38 + realChrome15:
actual loopback issuer/worker HTTP, PythonES256+SQLite; actual child exits77/78
before/after commit, no DB restore; exact lost-response once-only recovery;
owner/anon/work/ACL/replay/expiry/quota/root+configurableprefix refusals; new login
with same account after SIMULATED15days, retained key/room/history/floors.
RealWebCrypto sees an actually expired old actor cert, fresh service proof and
chunked lease/history signatures. Three intervening lease revisions bridge in
two chunks; wrong hash/skipped link/false completion/wronglane/substituted origin/
signed fork/forged local-continuity object are refused. No real15day wait,
physical phone, browser-paid hosted PoW, app/P2P integration, WAN or8k proof.

One-line current permission-control FAIL15 admits revoked author (expected400
becomes200); one-line continuity-control FAIL4 accepts unverified serialized proof
(expectedrefusal missing). Other source inputs identical; owned browser closed.
Historical genuine first core failure at20 was unspent invalid-operation nonce
capacity, fixed by separate authenticated-spend transaction before atomic resource
transaction. Next failure was test child calling execute(request=...) instead of
its raw positional argument; exact prior harness retained, corrected actual death
checks pass. All earlier stages/failures retained, not relabeled current proof.

Quotas are configurable ON-DISK actual usage, not per-member browser allocations:
fixture defaults8MiBchat/room64MiBtotal; separate32MiBlease-links/room128MiBtotal;
1024challenges,65536member/author records. HTTP limits/metadata/file modes bound
work; these defaults are NOT8k capacity acceptance. Hot-path/large-log/large-room
metrics and broader overload/fairness work still needed.

User asks FAST-FORWARD: known-hash catch-up is working in source; a fresh device
still needs prior history. Signed MATERIALIZED STATE SNAPSHOTS are NOT implemented.
Need board/turn/castling/en-passant/move+repetition counters/clocks/player permissions/
accepted-head binding, then only tail ops. Old history remains separate optional
fetch/audit. Trusting chosen checkpoint authority must be labeled honestly;
signature verification is not replay-auditing all past state transitions.
Hosted profile is CHAT ONLY currently, not durable chess or spectator seats yet.
Valid missed-branch reinclusion with original IDs/signatures/current permission+
dependency checks also remains REQUIRED; strict live expiry is not that feature.

Read-only hosted finalhealth: privateVM exact5ee491cc/native18 and same PIDs,
0ownedChromecontexts, ordinaryTLS root/blog/prototype HTTP200 and oldbloghash.
No newall10-site/133byte audit claim. No production/native changes, webhost pull,
ports/firewall/DNS/boot/signing/package install or real-state copy/restore.
Production remains16/c23 atroot+/blog/, sizingprototype untouched.

NEXT: protected service-account/operator and journaled recovery in retained VM;
shared hosted client/UI, durable browser floors and safe generation/disposal;
materialized checkpoints and chess/player/spectator rules; P2P transport/preferred
routing + bounded fallback/return; island/layer/bridge convergence; scalable admission;
valid missed ops/branches; actual staged8k/WAN; complete audit. Do not repackage the
same source as if those were done. Audit remains181cases:3complete161partial17
required plus53separatev0.1. Full goal ACTIVE; root/blog is only a live milestone.


Hosted authority/archive source proof frozen and private Git main verified at
6f06bb34b79239f39d6966408fcc83a428138d2f, tools/codiserver/hosted-room-source-r1;
manifestaa18678101273348296344b527fbd8dd6327f43db8b31ea1f6e2c4f27cd7e463.
980declared+manifest=981tracked/byte-verified; curated tree clean and parent proof
packages unchanged. hosted-room-source-proof-result.json binds source/milestone/
health;0ownedcontexts. No webhost pull or service rollout. Next implement protected
operator/privateVM lifecycle, shared UI/P2P client+durable browser floors and state
snapshots/chess/remaining8k work; do not repackage this source as completion.
Current35modules require NEW explicit native graph; old /4proof34/private18/33/
public16/c23 remain intact. Full goal ACTIVE; fresh-device state fast-forward is
NOT yet implemented. Known-hash history/authority catch-up is source-tested.


## In-progress private hosted integration — current runtime supersedes native18

PrivateVM upgraded by actual managed code transaction to native19
1bb104a87cc83404e53812138e6e60cfa006e218302db2cea6c294232a7c6507 at
/srv/codi-network-fixture/candidate-1bb104a87cc83404. Native/realm/account/cookie/files/
usage preserved, private file services not restarted. Native binding enabled via
configure-hosted-rooms (idcb7cd0db489068cae1cc717538ea6780); current issuer2581097,
steward2578883,guest2578884. Same schema5 with optional hostedRooms pin. New graph
explicit35/module4/membershipLease, old16/17/18 verifiers retained. Fifteen release
checks and469file identical rebuild pass. Public root/native16c23 UNCHANGED.

Actual separate room worker is installed/active inprivateVM: state
/var/lib/codi-rooms-fixture,config/etc/codi-rooms-fixture/managed.json,worker
2f961a91bf4b5b8ea7b399e4074dbffc084a7d10baa82f0efb7034aec5e87d26
under/srv/codi-room-fixture/workers/<SHA>. UIDcodi-room-fixture-2f961a91;
worker2555608/proxy2555652 at lastcheck; allthreeunitsstatic/no boot enable.
Original operatorfdd68c1ee6de961756fd05f80f864886a15f569b5147de8c2567a65d00d06153
preserved; nativebinding uses own-bundle-helper operator
88e820c04a26d8836ee06ca6b8c92518d7542ac066167565a3ec4afdc370cfee. Bothrootimmutable.
ActualVM lifecycle15PASS:3operatorprocessdeaths/prepared-initialized-applied with
real pendingjournal/recovery,workerSIGKILL,restart,keyDBretention,privateNS/caps0,
nonrootrefusal,existingprivatekey/folder/networkdenials,sourcecustodycontrols.
No hosted messages yet when this15checkreceipt was made; broker/browser underway.

Owned VM ingress has NOW changed from9ab745fc... to eff399488e29ba07fed9bbc3c5bf6864
e9b4663a73d2952035684644408e7879 (immutable file tools/native-hosted-ingress-<SHA>.py).
SameTLSmaterial/8443/SSH49747/HTTPS57503; --room-port8141 fixed privateproxy and only
routes when native hostedRooms enabled. Originalunitbackup at
/srv/codi-room-fixture/ingress-before-hosted.service. ActualunitSHA after
d61d6f1e3f05a4a8dbb7ce6bbff569767997d99df6f50694116fca401fe8551b. Do not claim
originalingress stillactive. No productionrouting/ports/firewall/boot change.

Git-first worker/operator/VMharness source736f2d96e990ba7e4932a2ebc8be876f3878b607,
packagehosted-room-operator-r1 manifestc7f266112d936aeff26b8b74066bf0e59c70e6a0c251d6ba38e4da73439eb85e.
Native19+r3operator+ingress source5a9212e1e1456b763c9a5fe64c02f0028e6e67cb,
packagehosted-native-r1 manifest7ffb79598ccd9b80013ed81fdca729ae48472644ff618fc62eff2220811d011c;
485declared+manifest486files. Existing public/fullgoal unchanged; still ACTIVE.
Actual browser/API acceptance, native binding interruption/rollback, app/lifecycle/
VM regressions and owned QA cleanup are IN PROGRESS. Do not recreate retainedVM
or restore old account/authority/user databases. State snapshots still required.


## Private hosted service recovery verified — 2026-10-24 21:49 UTC

This supersedes the preceding in-progress private integration entry. The retained
VM is native19 at /srv/codi-network-fixture/candidate-1bb104a87cc83404,
manifest 1bb104a87cc83404e53812138e6e60cfa006e218302db2cea6c294232a7c6507.
Final native PIDs: issuer2622184, steward2621593, guest2621594. Root/schema24/5,
private ingress eff39948... and existing SSH49747/HTTPS57503 remain; no production
routing, Caddy, ports, firewall or boot policy changed. Public native16/root/blog
and /desktop remain unchanged. Do not recreate the VM or restore old databases.

Actual Chrome/v86 HTTPS API acceptance passes11: browser-generated nonexportable
key, current issuer confirmations, registered room creation, duplicate acceptance
once, verified history, logout refusal, anonymous bounded worker admission/chat,
and tail-only recovery. This is direct shared API/proof exercise, not a hosted
Rooms drawer, P2P/fallback, public-WAN, chess or state-snapshot implementation.
Two accepted public-chat records are intentionally retained in the private room.
Owned QA vmhosted_6faef1798b48 is disabled; no private files remain.

The committed root-only fixture7cd3467f1d5a2fe78fc2e4a9bc6dbb4c95bb4e20
(hosted-native-tests-r1) passes14 installed checks: active-policy downgrade refusal,
four actual process deaths at prepared/switching/starting/committed, guarded starts,
explicit recovery, actual native19→18 rollback→19 upgrade with the policy disabled,
rebinding the same controller, worker stop/start and SIGKILL with NONEMPTY history.
Keys/accounts/cookie/private files, usage and room replay floors remain current;
no data restore or root mint. Existing isolated worker/operator install15 and
native release15 remain separate receipts with their original scopes.

After recovery, the installed three-desktop mesh suite passes23 with automatic
introductions and leased membership explicitly enabled. Fresh source HTTP/crypto/
SQLite checks pass38. Final read-only health confirms active isolated room service,
the same two records/floors, healthy guest isolation, no journals or anonymous QEMU
children, both current QA accounts disabled/empty, and zero owned browser contexts.
Default-TLS root/blog/prototype entry requests pass; this is not a repeated audit
of every site or all133 prototype bytes.

Aggregate: active-system/.build/checks/hosted-native-milestone-r1-result.json;
evidence: active-system/evidence/hosted-native.md. Native19 terminal/document/
lifecycle/account regression checks remain pending. Next implement the shared
hosted client/Rooms UI and P2P preferred transport/fallback, durable browser floors,
and signed materialized checkpoints. Hash-chunk catch-up works; a new device still
needs accepted history. Full snapshot fast-forward, hosted chess/spectators,
replicated failover, islands/layers and actual8k acceptance remain required.
Goal ACTIVE; no whole gate or durable15-day-game completion is claimed.

Private hosted installed proof is now frozen at Git5176974d699511ffd6ef1b7644590cd0068afda6,
package tools/codiserver/hosted-native-proof-r1:23declared files + source-proof.json,
manifestSHA d1b90efbd70fb1c5927af1de72f75589f55b8927603377c3d2b44ad9f1116389.
Private Git main and clean curated checkout match. No webhost pull/install occurred.
This proof preserves explicit pending native19 app regressions and state snapshots.


## Chat checkpoint source and native19 app regressions — 2026-10-24 22:00 UTC

Installed private native19 regressions now PASS: terminal38, document19,
lifecycle13 (182cycles), mobile account/access35. All preserve native PIDs
2622184/2621593/2621594. Final health reports five current owned QA accounts
now disabled with empty homes, zero owned browser contexts, no pending journals
or anonymous QEMU children, healthy guest guard and unchanged two room records.
Receipt hosted-native-regressions-r2-result.json supersedes earlier pending labels.
The immutable private native19/worker2f961a91 runtime remains unchanged.

New SOURCE chat-state checkpoint: snapshot({node_id,after}) returns a signed
chat-window/1 state at the accepted head. At most32receipt tokens/64000token chars;
full older history stays retrievable. Snapshot head/room/type/current permissions,
exact requested ancestor and visible receipt/origin chain are verified in Chrome.
Chosen controller attests skipped ancestry; no independent full-prefix/quorum
proof is claimed. Read serialization uses existing SQLite tables; no schema/data
migration or log deletion. Existing integrity aggregation still scans room data;
bounded response size is not a serverCPU/RSS/8k proof.

PASS:9actual HTTP/SQLite checks +22actual Chrome/WebCrypto checks: jump to
accepted100 without its omitted prefix, apply only3new records to103, maximum
UTF16Unicode byte pressure, current-head/authority rollback, equal-height fork,
signed malformed state and simulated15day fresh-session return. One-line removal
of ancestor-hash comparison FAILS at the intended first signed-bad-ancestor oracle
(after5browser checks); negative receipt retained. Legacy source core38/browser15
PASS against current code. All owned component browsers/temporary fixtures closed.

Aggregate hosted-snapshot-milestone-r1-result.json; evidence/hosted-checkpoints.md.
Exported nine-file worker b0dfa2c28d31db9af64bdaecec19c26b5cd1ee9b2d0624699404d75dd788d8d0
at active-system/.build/hosted-room-worker-snapshot-r1; existing five-file
operator88e820c0... unchanged. These new snapshot bytes are NOT installed in VM
or production. Do not overwrite immutable worker2f or bypass managed custody to
activate them. Next implement shared hosted client/Rooms UI and durable floors,
plus managed worker code-upgrade/recovery, P2P delivery/fallback/return, full chess
seats/spectator/state checkpoints, missed-valid-operation reinclusion, islands/
layers and staged8k/WAN acceptance. Goal ACTIVE, no whole gate completion claimed.
Production native16/root/blog/prototype, hosting, ports/firewall and boot unchanged.

Checkpoint source/proof is frozen at private Git b9fdbe5c7cfe4dade772a480e21ef75f90dba645,
package tools/codiserver/hosted-checkpoint-source-r1:133declared files + manifest,
source-proofSHA74246aff158d1a8afdcf3da5e8a4f496c0a1e2d09d179e3f23f726ffb01192dc.
Tracked bytes and remote main match; curated checkout clean. It includes the
unchanged operator, new inactive worker, exact source/negative control and bound
checkpoint/native-app receipts. No webhost sync/install occurred. Next work must
implement the shared hosted client/Rooms UI, durable browser floors and managed
worker upgrade/recovery rather than treating this source component as the goal.


## Private checkpoint runtime installed — 2026-10-24 22:12 UTC (in progress)

This supersedes the source-only worker/old private1bb runtime statements above.
Production native16/root/blog/prototype is unchanged. Retained private VM now
native19 manifest440f0c19892cde73fe893c139a86d9163e729af9f37c41d5ecd5221bbbbcbe8a
at /srv/codi-network-fixture/candidate-440f0c19892cde73. Current native PIDs
issuer2663657/steward2663660/guest2663659. Same schema5/root24, SSH49747/HTTPS57503,
fixture SPKI, private ingress eff39948..., unchanged file services1688542/1688544.
Do not recreate VM or assume the older1bb runtime is still current.

Worker NOW b0dfa2c28d31db9af64bdaecec19c26b5cd1ee9b2d0624699404d75dd788d8d0
under /srv/codi-room-fixture/workers/<SHA>; SAME serviceUID/state/key/rooms/floors.
Managed issuer hostedRooms now binds config pins and new five-file operator
41776629f6224f12c55e8dae011b0f2f9ca81c574530babe49a2ad50362e0d3f under
/srv/codi-room-fixture/operators/<SHA>. Original worker2f and operators88e/fdd
retained immutable. New unified pending.json supports codi-room-code/1; root
code-history.json records applied/reverted code only. Never restore database.

Actual installed code-upgrade22PASS: active issuer binding refusal; explicit
issuer-only disable; wrong pin refusal;7real process deaths at prepared/stopped/
individual-unit/config/applied/ready/committed, guarded start and explicit recovery;
PID-preserving no-op, old-code rollback/reupgrade with current nonempty history;
actual unhealthy worker automatic return to prior code; exact issuer rebind.
Precommit recovers prior code, committed recovers new. Worker/code/state/key/
account/file/usage boundaries retained. Actual native19→19checkpoint managed
code upgrade then preserves all keys/accounts/cookie/files/counters and file PIDs.
No root mint, data restore, production host changes or boot enablement.

Worker/root-fixture source5700ee4098ccad07f0f146e72f52a9fb5d7a2184,
package hosted-room-code-r1:20files +manifest006b85a03e21b048f24e17007344d126501e60360e686622f5ff29b258725f60.
Native source13cea128611a1df157f6d96d8d7971ae84036d67,
package checkpoint-native-r1:478files +manifestd45b0f0779af4fc5fbed36dfc8ba55309ba6377764f36e765ad3f69257bf181a.
15release checks and byte-identical469file rebuild PASS. Sources pushed and exact
committed bytes verified before any VM root execution/staging.

Actual installed browser checkpoint/API acceptance, post-upgrade mesh regression,
owned QA cleanup and final health are IN PROGRESS. Snapshot-capable worker/verifier
are installed only in privateVM; shared hosted Rooms UI/client/P2P and durable
browser floor persistence remain unimplemented. Chess/islands/8k goal ACTIVE.


## Private checkpoint runtime acceptance complete — 2026-10-24 22:17 UTC

Installed worker/code-upgrade22 and native release15/identical rebuild pass.
Actual Chrome/v86 checkpoint/API13 and post-upgrade three-desktop mesh23 now pass.
Final readonly health confirms SAME native19/440f PIDs2663657/2663660/2663659,
room workerb0/operator41776629, retained old accepted history/floors plus the new
owned QA room's two accepted notes. Seven current owned QA accounts are disabled
with empty homes; zero owned browsers, pending journals or anonymous QEMU children.
Guest isolation healthy; ordinary-TLS root/blog/prototype entry checks pass, not
a repeated all-site/prototype133 audit. Public native16 remains unchanged.

Aggregate checkpoint-native-milestone-r1-result.json binds source/release/code/API/
mesh/cleanup/health receipts. Evidence/room-code-upgrade.md describes actual bounds
and recovery; evidence/hosted-checkpoints.md now reflects private installation.
The old strict room-state equality health check was changed to the installed
monotonic retention predicate so legitimate new rooms/accepted records do not
look like failures; QA ownership remains checked against actual account policies
and private homes. Old receipts/immutable source packages are preserved.

Next ACTUAL implementation: shared hosted client/Rooms UI and durable browser
floor storage with lifecycle/account cancellation and shared budgets; then P2P
checkpoint delivery and bounded fallback/return. Current browser/API harness is
still direct service exercise and does not replace that shared client. Full
chess/player/spectator state, valid-missed-operation reinclusion, replicas,
islands/layers, full reference audit and actual8k/WAN tests remain required.
Goal ACTIVE. No production install, routes/ports/firewall/boot change this turn.

Installed checkpoint proof frozen at private Git1368e1399c85a27a7191137dfc80737f21dc4c5c,
package tools/codiserver/checkpoint-installed-proof-r1:23declared files +manifest,
source-proofSHA1bcf88ae7fbb7799467b8538eda8a2b3a10ad9d844d81ad64f8ad9c34353ed63.
Remote main and clean curated checkout match. Source/proof advancement did not
pull/install anything on production. Immediate next implementation remains the
shared hosted Rooms client/UI and durable browser floors on private440f/b0/417.


## Shared hosted client/Rooms source candidate — 2026-10-24 23:00 UTC

Previous turn is PROGRESS: implemented shared client, actual bundled pane,
persistent floor/creation-intent store, signed receipt lookup and bounded authority
bridge. This entry does NOT change the current retained VM or production runtime.
Private remains native19/440f (PIDs2663657/2663660/2663659), workerb0/operator417,
root24/schema5, SSH49747/HTTPS57503 and existing private ingress. Public native16,
root/blog/prototype/hosting/ports/boot unchanged; production root3 expires
2026-10-25 11:06:16UTC and still needs explicit bounded renewal before expiry.

New network/hosted-room-client.mjs + hosted-room-store.mjs bring source graph37.
Client owns same-origin signed requests, issuer/controller/member/receipt/snapshot
verification, shared budget, cancellable admission worker, database and per-room
operations. Per-view hosted-view.mjs owns draft/selection/abort/observer only and
is composed into Rooms through the normal dependency/CSS bundler. networking.js
now wires shared hosted client/observers into account lifetime. Keys/passwords/
HTTP tokens/chat text/guest files are NOT persisted in the new IndexedDB database;
only public IDs/labels/floors and idempotent creation intents. Scope is service key/
mount plus stable account ID or anonymous-browser scope. Local clearing/eviction
loses that rollback memory. No auto reset of corrupt/local higher floors.

PASS25actual Chrome component checks with real HTTP/SQLite/WebCrypto/IndexedDB,
generic bundled DOM panes and actual page reload (one Chrome, ZERO v86 guests):
two views/shared accepted history/independent drafts;12view cycles/accounting;
lost committed response resolved by original signed receipt without another Send;
cancelled creation recovered after reload without another room; fresh account
sessions/streams; separate anonymous scope/read/admission/write; membership refresh
uses one worker without redo; account change retires view/old in-flight request;
independent DB connection stale-write refusal; simulated15day authority bridge;
signed bad ancestor/substituted receipt refusal; local higher-floor fail closed
while another room works;120second fixture clock advance proves expired absent
submission is released with draft retained and no silent resend. All resources
closed. Simultaneous real tabs and full desktop/workspaces/touch are NOT tested.

One-line removal of count rollback guard FAILS at intended stale-writer oracle
(phase1eight + phase2eight checks). Fresh source core38/browser15 regressions PASS.
Final readonly health: old private runtime unchanged, seven current owned QA
accounts disabled/empty, zero owned browsers/journals/guest children. Source
fixtures create only temporary account/data and are removed; no VM user data reset.

Inactive native20: .build/releases/connected-hosted-client-native-r2,
manifest9f90460a952bcf56070bda145b2c960a8e1ca1fcb44c1eab0e51aaf5a392552d,
519declared files/57native/37network modules. New explicit profile20 + network
release5/client1; old17/18/19 graph verifiers preserved.14release/negative graph/
compiled catalog checks PASS; complete520file rebuild identical. Generic app build
updates only Rooms in seven-app catalog. Initial native-checkr1 failed only because
it searched a literal data attribute generated via dataset; failure retained,
correct compiled-field oracle r2PASS. Base/direct candidate r1 retained inactive.
Upgrade helper now accepts20 explicitly; current VM was NOT upgraded this turn.

Inactive nine-file worker .build/hosted-room-worker-client-r1,
manifest3907eac6785bc4ad6ca02436949539d0d06de9cdbf78b51f0b96e2d40d6a7a85.
Adds signed lookup and lease-bridge operations; SQLite schema unchanged. Operator
41776629 remains unchanged. Upgrade this worker BEFORE native20 (b0 lacks those
operations), through existing417 upgrade-code guard: explicitly disable hosted
issuer binding, upgrade immutable worker/config, rebind exact config/operator,
then use new native20 sealed controller to upgrade from current19. Never overwrite
old immutable releases or restore keys/accounts/files/floors. Source Git freeze
must precede any private root execution; candidates are not staged yet.

Evidence/hosted-client.md and hosted-client-milestone-r1-result.json bind exact
scope. Contribution guide names candidate APIs as NOT LIVE. Next ACTUAL work is
managed private worker/native20 activation and full app/workspace/account/touch/
reopen/concurrent-tab acceptance. Then P2P hosted delivery/fallback/return, old-
history controls, account room directory after browser clearing, chess seats/
spectators/full state, valid missed-operation reinclusion, replicas, islands/
layers, full reference audit and real staged8k/WAN tests. Goal ACTIVE.

Shared-client source/candidate/proof frozen at private Gitff290d55b15ad03f8460fd676cb0e33f0f7fde79,
package tools/codiserver/shared-hosted-client-r1:666declared files +manifest,
source-proofSHA566db5f971dd0ea58586dbc61c2216c2c53b46376fd97c8a1d73381b08a2819f.
Remote main and clean curated checkout match. It contains complete inactive
native20/519files, worker3907/operator417, source37graph, actual pane/dependency
sources, exact count-guard control and bound positive/negative/regression/release/
repro/health evidence. No webhost sync/install and no private runtime change.

Review follow-up before activation: HostedRooms.close currently releases each
observer in finally but a throwing retire callback can escape before remaining
observers/room leases/base allocation drain. Production wiring uses wrapper
observers, but the SDK should tolerate that callback fault too. Add a throwing-
retire cleanup oracle, make close drain all resources, rebuild/reseal the37module
candidate if changed, then proceed with managed private worker/native20 rollout
and actual full Rooms UI acceptance. Current25case proof does not cover this
callback-exception path; do not claim full lifecycle completion from it.


## Private native20 installed — 2026-10-24 23:20 UTC (acceptance in progress)

This supersedes all previous private native19/current-worker-b0 notes. Production
native16/root/blog/prototype remains unchanged. Retained VM NOW native20 at
/srv/codi-network-fixture/candidate-5c06970722581ab4,
manifest5c06970722581ab43045c1b33ea7d85a1d2da9b71c34331e2b73feaa4941913d,
519declared files/57native/37network modules. Native PIDs2770910/2770911/2770913;
file services1688542/1688544 preserved. Same root24/schema5/SSH49747/HTTPS57503,
fixtureSPKI and private ingress. Do not recreate retained VM or restore data.

Worker3907eac6785bc4ad6ca02436949539d0d06de9cdbf78b51f0b96e2d40d6a7a85
is installed at /srv/codi-room-fixture/workers/<SHA>, same private state/key/UID.
Operator41776629 remains installed/unchanged. Exact old account/key/cookie/file/
room/floor/usage state survived guarded worker upgrade + issuer rebind, then
managed native19→20 code upgrade; no root mint, data restore, hosting or boot change.
First worker staging failed on a local Path/string precedence typo BEFORE staging
or VM mutation; failure receipt retained. Corrected attempt passes preservation.

Cleanup bug now fixed: a throwing observer retire callback no longer interrupts
remaining observers/room/base lease cleanup. New actual fault oracle FAILS old
code after7checks; fixed source26PASS. Fresh one-line floor guard control still
fails intended oracle (phase1nine +phase2eight); release14PASS. R3candidate replaces
inactive R2/9f9046; earlier immutable inputs and receipts retained.

Worker source ff290d55... was verified from Git before root staging. Updated
source/candidate/UI fixture frozen/pushed at4676211de72403a539fb6a976ea1f5cee43984a7,
package shared-hosted-client-r2:548declared files +manifest
 a449c2fa9ebb7b681b372291fa21980b3458a266f9e258d3070761fbe04d6859.
Native20 exact committed bytes verified before managed upgrade. Actual full
Rooms menu/workspace/reload/mobile acceptance is IN PROGRESS; do not count the
26source-pane checks as installed desktop proof. No public deployment this turn.


## Private native20 full desktop and actual-tab acceptance — 2026-10-24 23:43 UTC

This supersedes the previous native20/5c0697 acceptance-in-progress note.
Production native16/root/blog/prototype remains unchanged. Retained VM now uses
/srv/codi-network-fixture/candidate-1d520e96ba5a7778, manifest
1d520e96ba5a7778ee6b43d472fc1ab8abb32b2a4ded612a610e775353f1d54d,
519declared files/57native/37network. Native PIDs2792346/2792348/2792349;
file-service PIDs1688542/1688544 preserved. Same root24/schema5, SSH49747,
HTTPS57503, fixture SPKI and private ingress. Worker3907/operator417 remain
installed with their original private key/account/room state and no pending
journal. Never recreate this VM or restore its data/floors to pass a test.

Installed full desktop UI17PASS: menu launches, saved chat creation/messages,
independent drafts, workspace DOM retention, minimize/roll-up,12full Rooms
open/close cycles with observer/accounting cleanup, reload/sign-in/bookmarks,
fresh signing stream, identity retirement, anonymous public reading,44px visible
phone controls. Actual same-profile2tabs/2v86/2signers9PASS: hold one genuine
snapshot response, advance the other actual tab's atomic IndexedDB floor, reject
stale writer, fresh refresh recovers without losing draft; separate streams and
one-tab sign-out isolate identity. These are fixture-SPKI private browser tests,
not public hosted/WAN/physical-phone/8k acceptance.

A real new defect was reproduced: sign-out archive omitted the hosted draft
selector. Negative same installed UI oracle FAILS5c0697 after14checks. R4 changes
only this core selector, keeping unsent text in the existing read-only previous-
identity archive; no send/save under a new account. Reload/close still loses RAM.
All37network modules,57native files and app catalog/Rooms bundle are identical
to5c0697. Old-mesh23PASS on that prior artifact is reused only with this explicit
byte-equivalence scope; it was not rerun on R4. Release15PASS and exact519-file
rebuild. Initial UI mobile failure counted hidden recovery button geometry;
read-only probe proved visible44px controls/no overflow. Corrected oracle checks
visible containment and hidden no-rects; no CSS/product change to hide the error.
All original negative receipts retained.

Final health PASS:14owned QA accounts disabled through installed policy, homes
empty, no owned Chrome contexts, no anonymous guest children or pending journals;
room state/floors retained, private namespaces/capability/boot constraints valid.
Default-trusted root/blog/prototype entries pass3requests, NOT a repeated full
all-site/prototype-byte audit. No webhost pull/install, hosting, DNS, router,
firewall, port, boot, production account or production root-renewal change.
Production root3 expires2026-10-25 11:06:16UTC; explicit bounded renewal only.

Candidate/fix frozen before staging at private Git72f3bb0a7a23f86ed9c81d7f407d41ca7ff0110f,
shared-hosted-client-r3:533declared files+manifest
5321cf31a38a86324d777e1e57c4845a150e26ce95a656418266dbe3903c528a.
Every tracked byte verified before root-owned managed upgrade. Earlier helpers/
failures are immutable in acceptance-r1(a629e50), tabs-r1(5b23537), archive-r1
(78394d8). No production checkout advanced. Bound current aggregate:
active-system/.build/checks/hosted-client-installed-milestone-r1-result.json.
Evidence: active-system/evidence/hosted-client.md. CONTRIBUTING and goal ledger
now distinguish installed-private from live-public. Requirement audit remains
incomplete; no whole gate is inferred from this milestone.

Next required implementation is P2P-preferred hosted delivery and bounded server
fallback/return using shared transport/budget; hosted chat currently requires
manual server Refresh between participants. Also required: full old history and
account-wide room recovery, durable chess seats/full snapshots/spectators,
original-ID valid missed-operation reinclusion, replicas, islands/layers,
scalable admission, staged actual8k/WAN and complete case/reference audit.
Prepare managed public hosting/native/worker acceptance before exposing hosted
chat. Preserve current root/blog/prototype and monotonic data. Full goal ACTIVE.

Installed acceptance proof now frozen/clean/remote-verified at private Git7b3459e137fa63278f27bbc66715e61b61f2b6e1,
shared-hosted-installed-proof-r1:30declared files +manifest
e9162ebc2c4121bb1d6fd14391ca612c8ffbe1038f752a045237ed0cf9bd0892.
This is source/proof only; production checkout/runtime was not advanced.


## Native21 verified; user explicitly requests live development — 2026-10-25 UTC

The user clarified there are no users except their occasional use, explicitly
authorized testing/building on the live site, and knows it is unfinished. Do NOT
keep the tested saved-chat upgrade private until all islands/8k goals finish.
Publish the tested current step at the real root while preserving all account/
file/authority state, /blog/, /desktop/ and other sites. No new router ports.

Private VM CURRENT native21 at /srv/codi-network-fixture/candidate-115f7a79f5a74a6b,
manifest115f7a79f5a74a6ba7afe8657beaad8dfbb0970f098345cf8b446daf2ec1fba0,
571files/57native/38network. Root24/schema5, SSH49747/HTTPS57503, same SPKI.
Worker3907/operator417 unchanged. Final native PIDs2865563/2865565/2865566,
file PIDs1688542/1688544. Real source4Chrome/5RTC20PASS, client26, old mesh46,
release18 and exact571-file rebuild. Actual two complete Linux desktops10PASS
peer updates/disconnect→server fallback(32.913s)/reconnect→P2P, draft/local-file
retention. Complete desktop/workspace/reload/mobile17PASS. Actual21→20→21 code
cycle passes root custody/permission rows/room state/counters retention, NO data
restore. First inverse helper wrongly selected older operator20 for current21;
refused before change. Correct helper explicitly uses newer pinned operator21
for inverse, preserves old guards; failure and forensic inspection retained.
Final health16owned QA disabled/empty, zero owned browsers/journals.
Bound private proof hosted-peer-installed-milestone-r1-result.json. Source97142cc
package hosted-peer-native-r1,638declared+manifest8bca8706..., cyclefixb43aee13
package hosted-peer-cycle-r2/manifestb43e76c9.... Full goal still ACTIVE.

LIVE STILL native16/c23 at /srv/codi-connected/releases/native16-c23b1b73df68ffb2;
actual instance codi-ksu-hidden despite ROOT mount (do not rename it). PIDs
1460700/1460696/1460759. Config schema5/root base'', source93717e3 clean.
No room account/backend installed yet. Room production account must codi-rooms;
new private state/key, never copy the fixture's key/accounts/DB. Existing root3
expires2026-10-25 11:06:16UTC, explicit bounded renewal only.

Live publication IN PROGRESS. Candidate common.py adds KSU-only codi_rooms flag
for only /rooms/challenge and /rooms/use to fixed loopback8141,128KiB body cap;
health/admin not exposed. Root and hidden-prefix renderings supported. Source
active-system/hosting_peer/{common,hardware_hosting,cardboard_hosting}. Current
production pins generatorc3181a47...,manifestf583f6f4...,Caddy4cf23397....
Prepared candidate .build/hosted-peer-production/hosting/candidate: generator
7174daa2...,manifestdf92e3ef...,Caddy42161b4b.... Absent flag and all non-KSU
blocks byte-identical. Actual Caddy/blog/prototype+new route test running via
exec session27193, log/check hosted-peer-hosting-r1*. Poll, do not restart merely
because observation expired. Source .build/deployment/ksu.codes mainb43aee13
(remote verified), no webhost source pull yet. Need Git-first publisher/staging,
managed native21 upgrade/new isolated worker+issuer binding+hosting controller
lock/pins/generator reload, then actual public normal-TLS browser/health tests.
Use existing 80/443; preserve Root keys, UUID folders/permissions/documents/usage/
replay floors and /desktop133/all10sites. Never hand-edit derived Caddy.


## LIVE native21 and saved-chat peer delivery — 2026-10-25 01:35 UTC

This supersedes earlier "live16/private-only21/publication in progress" notes.
User explicitly approved live-site development with no users apart from them.
Native21/115f7a79f5a74a6ba7afe8657beaad8dfbb0970f098345cf8b446daf2ec1fba0
is now LIVE at https://ksu.codes/,571files/38network modules. Old homepage stays
/blog/, /hidden[/] redirects root, /desktop133 and all other sites preserved.
Release /srv/codi-connected/releases/native21-115f7a79f5a74a6b; actual instance
still codi-ksu-hidden, basePath'',schema5. Do not rename instance/units.
Native PIDs2500061/2498033/2498034, files1460455/1460457 unchanged. Native boot
still disabled, bootstrap stopped. Root/fence3 expires2026-10-25 11:06:16UTC;
explicit bounded renewal only. Publisher observed764; never restore old floors.

NEW isolated codi-rooms nonlogin account, fresh production private controller key,
state /var/lib/codi-rooms/ksu, config /etc/codi-rooms/ksu/managed.json. Worker3907eac6...
/operator41776629... under /srv/codi-rooms/{workers,operators}/fullSHA. Worker/proxy
PIDs2493062/2493064 in shared private loopback namespace, distinct UIDs/no caps,
static notboot; host proxy127.0.0.1:8141. Only /rooms/challenge and /rooms/use
public with128KiB cap, health/admin not routed. No fixture secrets copied. Guest
registered-only policy/relay/DNS/router/firewall/ports/forwarding/boot unchanged.
Local accepted saved-chat sends remain server-authoritative; peer path delivers
verified checkpoints and update notices through the existing shared PeerPool.

Managed hosting pins: generator7174daa24a88fab02594f5eb1eb8648eda3412ec252c4f1525c98509d66102f4,
manifestdf92e3ef42d24f296768af83a34282b282dcbfff2e6324b4399e1a4c3f78d4b5,
Caddy42161b4b7235cfaadfdc884b37df2a6fe7a500c5edc897f8bd7d986a769d07c2.
Hosting lock/controller/generated validation/apply only, never hand-edit Caddy.
Snapshots /var/backups/webhost-sites/change-20261025T011749022433Z(common.py),
...022950Z(sites),...023288Z(Caddy). Code inverse first removes hosted binding,
then newer pinned operator validates older target, preserving current data/floors.
Original website release20261024T110552353972Z-299874f5 unchanged. Source on
webhost still5a12c04d5c74e8ff44e0414238c313c5c576b468, clean/source frozen before
root publication; source-only later proof pushes do not redeploy the website.

PUBLIC ordinary-TLS new acceptance PASS: peer10, complete Rooms UI17, actual
installed571file+public133prototype/blog/entry byte audit. Peer disconnect
fallback34.746s, fresh accepted head after reconnect returns peer delivery.
Drafts, anonymous local files and12 full reopen cycles preserved/clean. Each
of3owned public QA accounts disabled,3contexts across passing suites closed
(plus2from retained failure). Final health41current accounts retains all38old
rows, original keys/cookie/realm/root/service/filepermissions. Original document
baseline was EMPTY; nonempty retention is private-VM evidence, not this live check.
First public test passed6 then read via server after reconnect; diagnostics used
wrong window globals. Retained failure; corrected test captures lexical counters
and supplies fresh signed head, leaves30s expiry/crypto/product unchanged. Do not
claim peer-only reads from an unchanged expired snapshot. All10sites smoke PASS.
Receipts hosted-peer-{public-r2,public-ui-r1,live-health-r2,live-publication-r1}-result.json.
Full evidence active-system/evidence/hosted-peer-live.md (or evidence/ inside active).
Six root receipt paths/hashes and exact preserved state remain root-only, local
publication receipt exports public deployment metadata/opaque hashes only.

STILL REQUIRED: automatic hosted member organization, redundant bridges/islands/
layers/partition recovery, replicas/convergence and valid missed original IDs,
full durable chess seats/state/spectators, old history/account directory recovery,
scalable admission, staged8k/fallback saturation, physical-phone and independent
WAN/TURN acceptance of NEW checkpoint path, complete reference audit. Current5s
transfer deadline/131072-byte chunks need calibration at32KiB/s public TURN profile.
Prior older root WAN success is not new hosted-path acceptance. Full goal ACTIVE.

Live proof now frozen/pushed/clean at b3c4f8ace6ed5d36b5ee24b77b320557f009a995,
tools/codiserver/hosted-peer-live-proof-r1,21declared files + manifest
9e2adbcf9b787996a8fc1aa1db88a1552d46e454ba6ee15e36ec6c6eb70499c5.
Every tracked package byte and remote main verified. Bound final aggregate
hosted-peer-live-milestone-r1-result.json: public peer10/UI17,133public prototype,
571installed, original38/current41accounts, no owned driver contexts,3newQA
disabled. Webhost source remains5a12publication commit; no source-only sync yet.
Next concrete acceptance concern: calibrate signed snapshot transfers over public
TURN/TLS443 at existing32KiB/s allocation cap before building larger islands.
Current5s deadline may be short for near-limit131072-byte/base64-framed snapshots;
this is an unresolved sizing concern, not an observed WAN failure. Retain bounded
slot/byte/cancellation limits and strict expiry/ancestor checks during any fix.
Then implement hosted member organization/bridges/islands and remaining goal.


## Transfer timeout fix in progress — 2026-10-25 UTC

Authoritative WAN failure hosted-peer-wan-r1-result.json: actual two public IPs
104.180.210.33/24.126.137.85, both public TURN/TLS443.90000raw/168704wire bytes,
11chunks; original115 hit5s timeout and used server fallback in5.45s, all6
accepted messages retained. Both contexts closed and its own QA account disabled.
Product fix:5s idle renewed only on valid bounded chunk, independent20s maximum;
crypto/ancestor/30s head expiry, slots/bytes/relay policy unchanged. Source6 timing
checks pass(7.810s progressing,5.091s silent,20.105s drip), source20 pass. Removing
only hard deadline fails intended oracle at30.131s. All candidate/repro571bytes
match5ad8cefa2de56378b76fafdbdd3c35f4dfc738104d286577adcf8b6b6accd1b0.
Native profile remains21; all57native files and live apps byte-identical to115;
only current network module hosted-peer-sync.mjs changes. Do not publish the
uncomposed562file R3 base; final is .build/releases/connected-hosted-peer-native-r4.
R5 is identical reproduction via build-hosted-peer-timeout-native.py.

Private root24 upgraded5ad, peer10 passes, actual5ad→115→5ad inverse/forward2
passes unchanged root custody/permissions/room data, file PIDs unchanged. Final
native PIDs2992088/2992090/2992091, file1688542/1688544. Source candidate9ad6670
package hosted-peer-timeout-native-r1,595files+manifest04c4f976..., publisher
0adf3ade85ab8bb649cdebc0c42ea9c929ea3e5c package hosted-peer-timeout-publisher-r1,
4files+manifest4433c5c4.... Both Git-first verified on webhost, clean source now0ad.
Protected root helper /srv/codi-connected/publishers/c14cd6f5f838ed4daf046593eec68e9a9d5a14b9e281838c504c2bb5b3da71f2/publish-hosted-peer-timeout.py.
Inactive root staging PASS: rootreceipt hosted-peer-timeout-stage-1792893382890093869-result.json,
SHA dbf6ae6e853f504a59fc292f8b75782a9f7db9a986e8f9da2f1a05016a09417e.
Live ACTIVATE RUNNING via exec session1212, with honest10second notice then existing
managed code upgrade. Poll that handle/check actual native journal/config before
any retry. Current final active artifact must be read after completion; don't
assume it stayed115 or already5ad from this in-progress note. No hosting change.
Afterward run helper verify, public WAN same test against finalR4, final public
health/prototype/blog, then clean outside fixture. The ordinary-TLS health script
now explicitly accepts115 or5ad and no longer pins the old editable Git commit.

Owned Moonpie fixture ACTIVE driver14750 port49185, localforward3935521 URL
http://127.0.0.1:57071; folder in current moonpie-browser-fixture.json. Old WAN
contexts closed, current drivers idle. Use moonpie-root-browser.py cleanup after
retest, verify no owned browsers before removal. No USB needed/new public ports.
Root3 still expires2026-10-25 11:06:16UTC. Full goal ACTIVE, islands/chess/8k/audit
remain required. Do not mark complete from this narrow bugfix.


## LIVE transfer fix and real WAN acceptance — 2026-10-25 UTC

Supersedes the preceding in-progress activation note. Activation/verify PASS.
Current live AND private native21 manifest5ad8cefa2de56378b76fafdbdd3c35f4dfc738104d286577adcf8b6b6accd1b0.
Live release /srv/codi-connected/releases/native21-5ad8cefa2de56378, instance
codi-ksu-hidden/root/schema5, config00caa35fc267d47769f309cbe569616972e3b90950f74a38d72ad48ef7a08858.
Native PIDs2550504/2550506/2550507; files1460455/1460457 and rooms2493062/2493064
unchanged. Root/fence3 expires2026-10-25 11:06:16UTC, publisher770 observed.
Native disabledboot, rooms static, bootstrap stopped. Hosting pins still
7174daa2.../df92e3ef.../42161b4b..., no Caddy reload/routing/DNS/firewall/newports/
relaybandwidth/forwarding/boot/account-policy/root-renewal change. Existing source
on webhost0adf3ade85ab8bb649cdebc0c42ea9c929ea3e5c clean. App/native/worker bytes
unchanged; only current network hosted-peer-sync.mjs changes to5s idle +20s total.

Public WAN retest PASS7 at same2publicIPs, actual TURN/TLS443, same90000raw/
168704wire bytes/11chunks:5.764s, zero hosted HTTP/timeouts/refusals. Partial
actual-chunk cancellation releases pending request; later direct authenticated
message arrives and Linux stays ready. Full571 installed/public133prototype/blog/
root redirects/guestguard/relay/identity preservation PASS, all10sites PASS.
All38original accounts retained, current43 includes5newpublic QA now disabled.
Original production document baseline0; private nonempty retention proof separate.
Retain pre-fix WAN failure and one-line total-deadline negative control. Bound
hosted-peer-timeout-milestone-r1-result.json binds17receipts incl privatepeer10/
actualinverse2/source20/timing6/release18/repro and real publicWAN7.

Root receipts under /srv/codi-connected:
stage1792893382890093869 SHA dbf6ae6e853f504a59fc292f8b75782a9f7db9a986e8f9da2f1a05016a09417e;
activate1792893441149823170 SHA5a549ef411da3b9e937bb7f1aa45c4bf7560d7ff689cdfd7c614005b20d64768;
verify1792893484511097394 SHA689e3e2ecdd4d9003bc4f1d8740572c0c7f53d7a304c902b21e1ccdb5a6f136b.
Names use hosted-peer-timeout-<action>-<number>-result.json. Protected publisherc14cd6...
installed/source frozen before execution. Current code inverse115 retains current
state/floors through managed controller; do not restore DBs or root config alone.

Outside owned driver14750 and forward3935521 now STOPPED/missing-or-zombie,
fixture folder absent, forward rejects connections; zero owned local ChromeDriver
contexts. moonpie-browser-fixture.json marks fully cleaned. No external control
fixture remains. Never reuse those handles or terminate unrelated sessions. USB
not needed. Private VM remains root24/new5ad with PIDs2992088/2992090/2992091,
files1688542/1688544 unchanged; do not recreate/reset it. All current tests terminal.

Current evidence active-system/evidence/hosted-peer-timeout.md supersedes initial
115 current-state assertions (those receipts remain historical). Next implement
cursor-based accepted tail delivery rather than repeating a whole recent snapshot
for every notice, then hosted member sampling/introductions and bounded redundant
island/bridge organization through the shared existing pool/scheduler. Preserve
full checkpoint fast-forward and floor/permission/ancestry checks. Full replica
convergence/original-ID missed operations, durable chess/spectators/history,
scalable admission, staged8k/partition/fallback-saturation and complete reference
audit remain required. New WAN test is ONE large transfer/cancel, not a bandwidth/
RSS/concurrent/8k plateau or physical-phone proof. Goal ACTIVE.

Current timeout/WAN proof frozen and pushed at858f62ac5c8bb84da5cadb4cd72c5da8e4af6208,
tools/codiserver/hosted-peer-timeout-live-proof-r1,39declared+manifest
d4c08b1c5cd9cda9fb7e64287fed0dc2f4f5ad3d97e5b4ee712515e2c32f43b0.
Every tracked package byte and remote main verified, curated checkout clean.
Webhost editable checkout remains0adf3ad; this new proof push is source-only and
has not changed runtime/hosting. Full goal remains active. Next actual code work:
incremental peer checkpoint tails from a verified cursor, retaining snapshot
fast-forward for gaps and explicit floor/receipt/permission verification; then
automatic hosted member organization and redundant bounded island bridges.


## Live receipt-window increment; public acceptance running — 2026-10-25 UTC

Current live AND private native21 is a5d5a90767f4d8cc68054470a39394853835670bdc8decd11ad4afe3f9ae0d07.
Native profile21/571files/38network/57native, all native/apps/worker/hosting/guest
security bytes retained. Five network modules +networking.js opt in to negotiated
codi-hosted/1:state-window/1 (canonical8caps; no raised handshake bound). RAM cache
and persisted floor enable incremental tails; reload gets a visible window, old
cursor gaps require controller-attested snapshots. No grant/signature/expiry/floor
weakening. Source20/new pending5/legacy peer20/client26/mesh46/graph18/repro pass;
three exact one-statement negatives fail intended oracles. Retain sourceR1 manual
stale-refresh failure; newer hint guard and accepted-pending minimum now enforced.
PrivateUI17/peer10 and actuala5d→5ad→a5d cycle2 pass; root24 custody/permissions/
room history retained, private filePIDs1688542/1688544 unchanged. Private native
PIDs3067519/3067521/3067522. Native candidate package9889a3fd41e2c2cc411d785407040bda4329d3f9,
640files+manifest6534f00d4c1e8293b984846669bb2d95a0789a1f8c94c4791ae03559a1de3a23.

Managed live publisher/source4eaa3d6618131b27f94e83b8625e88945ffa3878,
publisher package8files+manifest6f83a5c4a5ab4a82ff869399e86b96de2d06b7af5787bd3adc6a1391c0294b71.
Webhost source fast-forwarded/650packagefiles verified, clean, no website deploy.
Protected /srv/codi-connected/publishers/952fd87d9a7a7b1833dd6984f27156d3eb54a76a6a2757de7bd3045d6824cc4b/publish-hosted-window.py.
Live installed /srv/codi-connected/releases/native21-a5d5a90767f4d8cc, instance
stillcodi-ksu-hidden, root/schema5. Stage and ACTIVATE PASS with10second honest
notice. Root receipts under /srv/codi-connected:
hosted-peer-window-stage-1792896907401830411-result.json SHA79c793cce2947f88e2fbc2f143c0e2d1209c8a3f5c83b913bcab9320662cd417;
hosted-peer-window-activate-1792897023651571966-result.json SHA9cec8c7a013c65a37ec18b58cbe1aa89b2d00ee4206c7600de9a24bf0a0cfdd0.
Root verify handle2509 was running; poll before retry (its local receipt may now
be complete). No routing/Caddy/ports/firewall/relay cap/boot/account-policy/root
renewal change. Root3 expiry still2026-10-25 11:06:16UTC; read currentPIDs/configSHA
from fresh final health, do not assume earlier5adPIDs remain. Hosting pins unchanged.

WAN test ACTIVE exec session77088/log hosted-peer-window-wan-r1.log. Two real
public Chrome/Linux contexts, normalTLS, optionalstateWindow actuallynegotiated,
initiallargewindow +automaticone-receipt bandwidth check +receiverreload to make
cancel genuinelymulti-frame. Do not restart from missing output alone. Owned
Moonpie driver15393/port33719, localforward3956507 URLhttp://127.0.0.1:56547,
folder in moonpie-browser-fixture.json. Cleanup with existing helper only AFTER
all owned contexts close. Old fixture14750/3935521 remainsfullycleaned. NoUSBneeded.
Next finish public defaultpeer/UI ifneeded, current health571/public133/blog/all10,
WAN/cleanup/boundproof/ledger/handoff/sourceGit. Then implement memberorganization/
islands/bridges and the remaining full goal. Never call8k/replica/chess complete.


## LIVE receipt windows verified and cleaned — 2026-10-25 UTC

Supersedes the previous in-progress public acceptance note. Current live AND
private native21 remains a5d5a90767f4d8cc68054470a39394853835670bdc8decd11ad4afe3f9ae0d07.
Live /srv/codi-connected/releases/native21-a5d5a90767f4d8cc, root/schema5,
instancecodi-ksu-hidden, configSHA a205e7fadbe39d6161c6f01db7e25d4c8a31cf82ab411c38e3a8cb86fdec3a77.
NativePIDs2624851/2624853/2624854; file1460455/1460457 and rooms2493062/2493064
unchanged. Root/fence3 expires2026-10-25 11:06:16UTC, publisher786 observed.
No root renewal/autosigner, routing/Caddy/DNS/router/firewall/ports/relay-cap/boot/
account-policy changes. Native stilldisabledboot, roomsstatic, bootstrapstopped.
Hosting pins7174daa2.../df92e3ef.../42161b4b... and website release unchanged.

Public defaultpeer10 and independentWAN13 PASS. Two publicIPs104.180.210.33/
24.126.137.85, actual TURN/TLS443 before/after deliberate receiver reload. Initial
visiblewindow4.078s; one newly accepted receipt6396payload/17786authenticated
bytes inclnotice vs128301initialwindow, zero hosted HTTP. Reload preservesfloor,
actualmulti-frame partial cancel preservesconnection/Linux.2Chromecontexts/
3Linuxinstancecreations becauseofreload. RegularRooms/draft/localfiles/automatic
fallback30.912s/reconnect/observers PASS10 on samepublic artifact. Health571installed/
133publicprototype/blog/entry/identity/permissions/guestguard/relay/boot PASS;
all10sites PASS.45current accounts retainsall38old;7newpublicQA acrossmilestones
nowdisabled, acceptedtestroomledgersretained. Originalproddocbaseline0; private
nonemptyretention is separateevidence. FullUI17/privatepeer10/cycle2 remainprivate
actualroot24/SPKI scope;5networkmodules/networking.jschanged, native/app/workerbytes
unchanged. Pendingaccepted stale-read5 andthreeone-statement negativecontrols are
in sourceproof; source20/client26/legacyPeer20/mesh46/release18/repro allPASS.
Boundaggregate hosted-peer-window-milestone-r1-result.json binds24receipts, three
rootreceipthashes, PIDsame acrosspublicacceptance andall7QA disabled. Wholegoalfalse.
Currentevidence active-system/evidence/hosted-peer-window.md supersedesearlier
5ad currentstate assertions; keepallfrozenhistoricalproofs andactualsourceR1failure.

Rootreceipt verify hosted-peer-window-verify-1792897084395226761-result.json
SHA4c1574b9f220d7df20ebfc36d65ae45529cd48a7ac7ea3513b27507e32443772.
Stage/activate receipts/publisher952fd87... are recordedabove andinevidence.
Currentwebhost source4eaa3d6618131b27f94e83b8625e88945ffa3878, clean. Root publisher
is pinned tothiscleancommit forverify/stageoperations; newproofpushesalone don't
change it. Private VMroot24/a5dPIDs3067519/3067521/3067522,files1688542/1688544.
No journals/data restores; do not recreatefixtureorresetfloors. Currentmanaged
inverse5ad testedusingnewerpinnedoperator,currentdata remainsauthoritative.

OwnedMoonpie driver15393 andlocalforward3956507 nowSTOPPED/missing-or-zombie,
folderabsent, noforwardlistener, zeroownedlocalChromeDrivercontexts. Current
moonpie-browser-fixture.json fullycleaned. Noexternalfixture/controltunnel remains;
neverreuse oldhandles orkillunrelatedbrowsers. Allcurrenttests terminal. NoUSBneeded.

NEXT ACTUAL IMPLEMENTATION: hosted participant/member sampling and authenticated
introductions using the existing sharedpool/scheduler, then redundant bounded
islands/bridges/layers andchurn/partitionrecovery. Keepquiet/smallchannel operation
anddon'tallocatepermember/perlayer128MiB; memorybudgetisvariablepertab accounting.
Incrementalresume is fromlastcommittedverifiedcursor; interruptedpacketfragments
are discarded. Full replica/convergence/validoriginal-ID missedoperations,
durablechessseats/state/spectators, completehistory/accountdirectory, scalable
admission, staged8k/fallbacksaturation andfullreferenceaudit remainrequired. Recent
singletransfer/tail measurements are notbandwidth/RSS/concurrency/8k plateaus.
Goal ACTIVE; don't callcomplete orshrink it tothesuccessfulincrement.

The live receipt-window proof is frozen and pushed at
91cdb24af2bbf812ea2de9197efe7097178dfa54 in
tools/codiserver/hosted-peer-window-live-proof-r1:53declared files plus manifest
8571759d42ae743a2305400d53f0e26d5504978d8b510d3d3ecba06deb36ac22.
Every tracked package byte and remote main were verified; curated Git is clean.
The webhost editable checkout remains4eaa3d6, while its active immutable runtime
is a5d5a907. This evidence-only push did not restart or redeploy anything.
The next required implementation is automatic hosted member/peer organization
and bounded redundant island bridges, using the shared pool and scheduler.
Keep the full goal active; the successful incremental transport is one milestone.


## Local reader-organization candidate — 2026-10-25 UTC

Production/private remain native21/a5d5a907, untouched. New native22 candidate
9537a6b6d4ab7074512d48e13c46121282980e7197a7aaf3b1c3f7ddc8199f6a is local only:615files,39network,57native, identical builds connected-hosted-readers-native-r2/r3.
Source hosted-reader-peers.mjs + optional hosted client/control integration and
networking.js opt-in; new builder closes profile22 without changing old verifier
functions. Existing native profile verifiers change only to recognize22. No
worker/schema/hosting/account/egress/root/port/boot or live data changes.

Actual source Chrome/RTC test hosted-readers-source-r6-result.json PASS15 with
ten contexts/nine participating readers+one old window-only peer, automatic
extra edges, original-intermediary loss, fresh-identity rejoin/floor preservation,
proof/replay refusals, a verified remaining route before larger interior-node
loss, peer update/no receiver HTTP and zero accounted resources onclose.
Earlier r5 PASS15 precedes final owned unfinished-PC cleanup-only change.
Recipient one-condition negative deliberately FAILS5 at intended proof oracle;
source graph unmodified. Legacy window20/client26 PASS before final cleanup-only
change, organization disabled. Release-r2 PASS14; build r1/8057 superseded.
Source-r1 fixture answer-channel race, r3 missing redundant path and r4 needless
stale-neighbor HTTP failures retained. New verified-notifier preference fixesr4;
r3 is still a real limitation when no path remains. See evidence/hosted-readers.md.

Next: targeted pending-introduction/capacity/cancel lifecycle tests; Git-first
freeze local source/candidate; private actual native22 install/UI/topology/code
inverse21/forward22 tests preserving current root24/data/keys/floors; then managed
live/WAN publication if sound. No private/native22 service execution yet. Need
fully disconnected directory/bootstrap fallback and robust islands/bridges next,
not just dense local clusters. Remaining replicas/chess/history/admission/8k/audit
goal stays ACTIVE. Root3 expiry11:06:16UTC still needs fresh inspection before
any later deployment; do not reset floors or automatically mint roots. All local
test handles terminal and owned Chrome contexts cleaned; no Moonpie/USB fixture.


## Native22 live; WAN acceptance running — 2026-10-25 UTC

9537a6b6d4ab7074512d48e13c46121282980e7197a7aaf3b1c3f7ddc8199f6a is now
live AND private, native22/615files/39network/57native. Protected live release
/srv/codi-connected/releases/native22-9537a6b6d4ab7074. Existing schema5/root
mount/instancecodi-ksu-hidden kept. Private installed root/data custody PASS, UI17,
actual3v86 topology6 and actual22->21->22 inverse2 PASS. Private native final
PIDs3172593/3172595/3172596. Existing file services/worker/keys/data/floors retained.
New actual source pending-r2 PASS16 with four Chrome +5additional real issuer/RTC
offerers; fifth valid introduction refused before PC allocation, immediate new
pending-PC cleanup and existing direct chat preserved. Exact close omission
negative FAILS12 at intended retirement oracle; recipient negative FAILS5.

Native source frozen/pushed8cb92f846fb4dff628af45edfbebbba77d4b9f56, package
hosted-readers-native-r1:694declared+manifest79a5bbb9b0e290a8c9b31edd02e28f4a6fc54afcb405f9639627cae3f775e117.
Publisher/privateproof/helpers bd28fbb91d8913d03304cde7a5ebe4923d89f05e,
hosted-readers-publisher-r1:16declared+manifest84e13f75a08f992cebdf4325b6f6f10d8f475a68c20b4fde8a20328ae8dad15f.
Everytracked byte/cleanGit/remote main verified before private/live execution.
Webhost clean editable source nowbd28fbb. Protected live publisher
/srv/codi-connected/publishers/b63dd8d8afcecbba9822c2bf4b835e1e6d34d0fbbcec28f633ddc2980b29f9ed/publish-hosted-readers.py
uses target22 controller with oldd08 helper for retained custody/install only.
No Caddy/routing/ports/firewall/worker/boot/account-policy/rootrenewal changes.
Root3 before-live health PASS expires2026-10-25 11:06:16UTC;133prototype/public
root/blog unchanged before live. Need final freshhealth/publicQA cleanup.

Root receipts under /srv/codi-connected:
source-sync-1792901019926864466 SHA f8d387fa92413b32aa1709c452016996839437a3a8575c2a10717b07c23f9ea5;
stage-1792901030916382910 SHA bb091553a555f15f61fcd307dee95e38ac9812c8e5cc2bb1a54e2f0c7cb241eb;
activate-1792901146731276190 SHA a3c4b5d4c893f7bc52c2a3c608067e3abe25e41282da2194816937dc5aa71bc2;
verify-1792901203464462273 SHA 6737db4131037d70a443a6fd8b85d3ee63adf3874d32d34921ff56a7e9684c26.
All filenames have hosted-readers- prefix and -result.json suffix. Actual10s
honest maintenance notice and managed stage/activate/verify PASS.

WAN acceptance exec37299 RUNNING: scripts/hosted-readers-wan-check.py, output
.build/checks/hosted-readers-wan-r1-result.json. Three actual public Linux browsers,
two local and one Moonpie, realTLS/allowedforcedTURN/TLS443 and introduced-edge
measurement. Poll same handle, do not restart from no output. Current OWNED
Moonpie driver16054/port54871, folder codi-root-wan-1792901025204550321 under
/home/maint/snap/chromium/common; localforward3983064 URLhttp://127.0.0.1:50569.
Fixture intentionally active; clean with moonpie-root-browser.py cleanup only
after all owned contexts close. USBnotneeded. Old15393/3956507 fullycleaned.
All10-site smoke exec7336 running writes existing rolling server
reports/private/hosted-peer-native21-smoke.json (scope explicitlynative22);
copycurrent result to local hosted-readers-smoke-r1-result.json afterward.
Next finishWAN, public normalTLS fullUI/peer ifneeded, all10smoke, finalhealth615/
133prototype/blog/root keys/QA disabled, outsidefixture cleanup+boundaggregate/
evidence/ledger/handoff/Gitproof. Whole goal remains ACTIVE. Full disconnected
bootstrap/islands/replicas/chess/history/admission/8k/audit remain required.


## Native22 reader increment LIVE, accepted and cleaned — 2026-10-25 UTC

Supersedes prior in-progress notes. Current live AND private native22 is
9537a6b6d4ab7074512d48e13c46121282980e7197a7aaf3b1c3f7ddc8199f6a,615declared/
39network/57native. Live /srv/codi-connected/releases/native22-9537a6b6d4ab7074;
root/schema5, instancecodi-ksu-hidden. NativePIDs2712752/2712754/2712755, config
SHA88eddf6ce3c99a070d57f2b71652db7f4759d623ea6fc761387f13b0ddf99100.
File1460455/1460457 and rooms2493062/2493064 unchanged; no Caddy/routing/worker/
router/firewall/port/boot/account-policy/root-renewal change. Website release and
hosting7174daa2/df92e3ef/42161b4b unchanged. Root/fence3 expires2026-10-25
11:06:16UTC; publisher803 observed.47accounts retains original38;9known public
QA across these milestones independently verified disabled. Original production
doc baseline0; separate private nonempty retention proof, never imply otherwise.

Current evidence active-system/evidence/hosted-readers.md. Local source15 with
ten actualChrome/nine participating readers, pending16 with four Chrome+5real
issuer/RTC offerers, intended recipient/owned-close single-statement negatives
FAIL5/12, client26/windows20 preceding cleanup-only change, release14 and exact
repro615. Actual private upgrade/root24 custody, UI17/3v86 topology6/inverse2
PASS; privatePIDs3172593/3172595/3172596. Public normalTLS UI17 and two-public-IP
3v86 topology7 PASS. Actual introduced edge selects public TURN/TLS443 on both
ends; intermediary closes, accepted updates continue with zero receiver HTTP
in asserted paths. PublicIPs104.180.210.33/24.126.137.85. No physical phone/UDP
NAT/8k implication. All10live sites and133public prototype bytes/blog PASS.
Bound hosted-readers-milestone-r1-result.json PASS binds28receipts, four actual
protected rootreceipt hashes, both intended negatives and retained real failures.
Wholegoal/islands/fullpartition/replicas/durablechess/8k/referenceaudit false.

All current test handles are terminal. Owned Moonpie driver16054 and
localforward3983064 are missing, folder codi-root-wan-1792901025204550321 absent,
both listeners refused; zero localChromeDrivercontexts. Cleanup receipt and
independent cleanup-verified PASS. No USB/outside control fixture remains.
Native source frozen8cb92f8 and publisher/privateproof bd28fbb as above; live
webhost editable checkout remainsbd28fbb. Final proof package is not yet frozen
at this note; next freeze currentdocs/ledger/receipts/aggregate and verifyGit.

NEXT IMPLEMENTATION: bounded server-assisted reader discovery/signaling for
fully disconnected components, then structured redundant islands/layers, churn/
partitions/fallback saturation/return toP2P. Current signed one-hop samples do not
guarantee arbitrary-cut recovery or eliminate server-authoritative sends. Keep
shared tab budget variable; no128MiB per member/layer reservation. Finish full
replica convergence/original-ID valid missed operations, durable chess seats/
state/spectators/history, scalable admission and staged8k plus full reference
audit. Preserve actual root/blog, backend-free sizing prototype and permissions.
Goal ACTIVE. Before later live work inspect root3 deadline; do not reset floors
or introduce an automatic signer to make old expectations green.


Current reader live proof frozen/pushed ata9341cb60d6e1a391ed61e5c5c02341e3e4b28d2 in
tools/codiserver/hosted-readers-live-proof-r1:36declared files plus manifest
1a850bb0e0e5814468ec8ab67ffc98a9bb95fa2f53a5ecdad92a41eaeaec6035.
Everytracked byte/remote main verified, curatedGitclean. Webhost editable source
remainsbd28fbb; this evidence-only push did not change services. All current
process/test handles terminal; owned drivers/forward/browser contexts cleaned.
Next actualcode: bounded reader directory/signaling fallback for fully separated
components, retaining chosen-controller acceptance and shared resource bounds;
then redundant islands/layers and full remaining goal. Goal ACTIVE.


## Source-only directory/complete-split candidate — 2026-10-25 UTC

Production AND private remain native22/9537a6b6, worker3907/operator417. No new
service execution/hosting/ports/root renewal or private-state migration this turn.
Current local native23/a2086017e7dcc87a7c1126bb7c71b62fd5ae0e7c1f94567444491850d1862a34,
660files/40network/57native, builds connected-reader-directory-native-r1/r2
identical. Only four native profile validators changed; prior functions/apps
retained. New worker graph2 at .build/room-workers/reader-rendezvous-r1, SHA
3a6d3c5184e52858abe324e37fd4ca410f66d7d289468efe6f169352d347727b,10files.
Operator .build/room-operators/reader-rendezvous-r1, SHA
53aa99303600f942a6f40b63718e26f2e73d78bffa0c458ba3d6bebb83a034fc,5files,
format1 unchanged, new pinned code explicitly supports worker1/2 and matching
health versions. Old417 frozen operator remains strict1. Native22 can bind the
new operator through existing format1 contract; no new binding schema is needed.

Discovery uses signed public P2P identity + key proof + controller-signed public
descriptors + bounded one-use browser PoW. Initial fresh-login bootstrap was
replaced before deployment to avoid polling/renewal load on login/SQLite. Public
certificate expiry is its revocation bound, not fresh account status. No file/
Internet/write grant. Normal authority/access/launcher bytes and persistent
SQLite schema unchanged. Existing /rooms/use with Codi-Reader:rendezvous/1,
separate2 discovery/8normal slots; ticket60s/bootnonce/monotonic RAM sequence,
64MiB accounting/cache/mail caps, restart loses discovery only. New JS module
hosted-reader-directory.mjs, shared desktop tick and cancellable worker/mail.
ReaderPeers direct-directory route independently verifies same signed intros;
pending transport abort now removes queued signals. Networking candidate opts
in readerDirectory:true; this workspace source flag is not live22's immutable
flag. No runtimeNode/Brotli.js added; Node/npm/esbuild remain build tools only.

PASS actual loopback API20(root r4 + /scope-test mounted1); intended recipient/
replay controls deliberately FAIL9/6. Two actual browser zero-seed/total-cut8
precedes final signal-cancel propagation. Current4-browser two-by-two island
source9 PASS (islands-r2): preserve internal PCs, discovery unavailable, ordinary
server state fallback, recreate cross-island RTC and return toP2P, all browser
leases zero onclose. Bootstrap18.113s/repair39.128s one fixture only. Retain
islands-r1 failure: source presentation selected one reader while another in
its island actually fetched/relayed state; corrected oracle proves actual group
server counters/reads and equal verified state, not last presentation source.
Legacy API38/client26/peers16 and closed native14/repro660 PASS. Export contract
checks only two operator funcs differ, schema/authority/launcher retained.
See evidence/reader-rendezvous.md for exact scopes/receipts. No8k/WAN/v86 claim.

New private helpers: reader-rendezvous-code-vm-check.py derives existing actual
7death-point/worker inverse/negative-readiness/rebind suite with explicit
--previous-worker/--previous-sha256. Expected current private worker location
/srv/codi-room-fixture/workers/3907eac6785bc4ad6ca02436949539d0d06de9cdbf78b51f0b96e2d40d6a7a85;
config/etc/codi-rooms-fixture/managed.json, state/var/lib/codi-rooms-fixture,
usercodi-room-fixture-2f961a91 uid988/gid984, namespace port8141, unitDir/run/systemd/system.
Read-only inspected, not changed. Upgrade-signin helper accepts15..23; new
upgrade-reader-directory-native-vm.py uses unique reader-directory-upgrade
snapshot prefix and root/permissions retention. Need Git-first freeze before
executing any new privileged/private helper. Then stage exact worker/op/helper
under protected /srv/codi-room-fixture, run worker lifecycle against3907, rebind
new op, native23 upgrade/UI/zero-seed full Linux and actual code/backend inverse.
Then managed live/WAN if sound. All current local tests terminal/owned contexts
closed; no Moonpie fixture. Root3 deadline11:06:16UTC needs fresh inspection
before later live work. Full goal stays ACTIVE; scalable anchors/islands/layers,
replicas/missed originals, durable chess/history/admission/8k/audit remain required.


## Installed private directory/complete-split recovery — 2026-10-25 UTC

Production unchanged native22/9537a6b6, worker3907/operator417, root3 expires
2026-10-25 11:06:16UTC. Fresh reader-directory-before-live-health-r1 PASS verifies
615installed/133public prototype/root/blog/guest guard/disabled boot, unchanged
livePIDs2712752/2712754/2712755 and hosting pins. No automatic signer, ports,
router/firewall/hosting/boot change. Current-feature-operations-inspect-r1 records
native disabled/static dependencies, relay certificate timer armed, no listed
Codi backup timer and root-only prior backup dirs. Complete current-state restore,
boot order/reboot, signing expiry monitoring, long resource/fault soak and physical
S25 acceptance remain operational-stability gates. Mere backup dirs are no proof.

Private retained root24 VM now native23/a2086017e7dcc87a7c1126bb7c71b62fd5ae0e7c1f94567444491850d1862a34,
660files/40network/57native; candidate path/srv/codi-network-fixture/candidate-a2086017e7dcc87a.
NativePIDs3331234/3331236/3331237. Worker2/3a6d3c5184e52858abe324e37fd4ca410f66d7d289468efe6f169352d347727b,
10files, installed /srv/codi-room-fixture/workers/<SHA>; operator format1/53aa99303600f942a6f40b63718e26f2e73d78bffa0c458ba3d6bebb83a034fc,
5files, /srv/codi-room-fixture/operators/<SHA>. Native binding now selects this
new exact operator; old417 remains strict1 and cannot recognize worker2. Existing
config/etc/codi-rooms-fixture/managed.json and state/var/lib/codi-rooms-fixture.
Private filePIDs1688542/1688544 unchanged. SSH49747/HTTPS57503, fixture SPKI only.
Do not recreate/restore VM or mint root to satisfy historical tests.

PASS current private worker22:7actual os._exit upgrade deaths/recovery, wrongpin,
PIDno-op, actual1->2->1->2, unhealthy-target automatic rollback and newoperator
native rebind, nonempty room/replay/controller/account/file/usage retained.
PASS managed native22->23 custody, three actual v86 zero-seed/churn/complete RTC
cut+discovery outage/server fallback/fresh RTC repair/return-to-P2P11, UI17 with
36real Rooms open/close cycles in3batches and exact equality of every shared
resource lease + observer counts, actual23->22->23 inverse2 without old data.
Private final-health PASS actual runtime/room health, local Chrome contexts0,
4owned QA disabled by per-test cleanup receipts; no new Moonpie/WAN fixture.
All current process handles terminal. No installed-public23/WAN/physicalphone/
large-island/8k capacity claim. Source/mountedAPI20+20/4Chrome islands9 and old
regressions retain their earlier scopes.

Retained failures: private-stage-before-r1 rejected tar-preserved UID before any
service change; exact newpaths chown/chmod then stagePASS, no weakened guard.
Original UI-r1 FAIL8 and diagnostic-r1 FAIL8 show exact +4096 initial signed self
presence when directory bootstrap0->1, observers3/3 and all other leases same.
No product patch. New UI oracle initializes shared discovery and samples only
quiescent jobs, preserving full UI and strengthening12->36cycles/alllease exact
comparison. Retain these failures and the source island oracle/recipient/replay
negative controls. See evidence/reader-rendezvous.md and reader-directory-private-
milestone-r2-result.json PASS bound23receipts (wholeGoalComplete=false).

Git frozen:74db86af33511087dce8f5529c47d6a0a1fc894d native/source packet780+
manifest e9331513a538178579974ef6381a24de8ac010c05d1b1c2f513d33a31da0a93b;
49d04f3380956f8e0be32e812b712691fa2288c9 private fixtures9+manifest597598a6...;
8841988d9b80e4b6870c64b312bc05100e042037 diagnostic;3d71d368ff90da04bb3dd01495b098f291e49157
quiescentUI. All remote/tracked bytes/clean verified. Live editable checkout still
bd28fbb; these pushes did not run code on production. Historical packets intact.
Ordinary room exporter now routes current worker2 graph + compatible operator,
verified byte-identical3a6/53aa; no incomplete default worker1 export.

NEXT: protected Git-first managed publication of new backend/operator then native23,
with honest maintenance, explicit disable/worker upgrade/rebind, guarded recovery
and inverse; ordinary-TLS independent-WAN full Linux proof. Current public22 remains
healthy meanwhile. Then structured redundant bridge/island/layer organization,
measured staged8k transports/resource/fallback saturation, independent replicas/
valid missed original-ID operations, durable chess seats/state/spectators/history,
full reference audit, operational hardening. Full goal ACTIVE, not completed.

Private directory proof frozen/pushed c78393bad8bebc0c25935ce89e0c93d04c8ee83a in tools/codiserver/reader-directory-private-proof-r1:36declared files plus manifest512272eb7b93f3dfdea37745f8ec4f0dc6605eaeb4cc7b922372281b4589033f. Every tracked byte, remote main and clean checkout verified. Production editable checkout remainsbd28fbb; live22/native23-private distinction remains authoritative. All handles terminal and owned browser contexts0. Goal ACTIVE; next protected managed backend/native publication, outside-network proof, then full remaining distributed/8k/chess/audit/operational scope.


## User-directed live-first development — 2026-10-25 UTC

Latest explicit user direction supersedes earlier private-VM-first release gates:
"dont bother with the vm for testing. the live site is for testing until we have
real users(i am the only user) the name of the game is speed of updates".
Use the live site for development/testing and prioritize quick small updates.
Keep fast relevant checks, immutable Git-first releases, a practical code rollback,
protected service/hosting workflows, current data/keys/floors and /desktop/ plus
/blog/ preservation. Do not require or continue new private VM tests as a gate.
Existing VM/state/artifacts stay retained; do not destroy or restore its data.
Full product objective remains active; this changes development workflow.


## Current LIVE native25; live-first workflow — 2026-10-25 07:05 UTC

User explicitly changed workflow: "dont bother with the vm for testing. the live
site is for testing until we have real users(i am the only user) the name of the
game is speed of updates". This supersedes private-VM-first gates, including
those in older frozen READMEs. Continue small direct live updates/targeted tests
with practical rollback, Git-first code, data/key/floor/hosting protections.
No new VM testing gate. Retain its existing state; do not recreate/restore it.
Full goal remains ACTIVE. Root/blog migration already live; keep133prototype
bytes and other sites intact. New marketplace/payment apps remain deferred.

LIVE https://ksu.codes/ is now native25/46c878c394203e962680e1b09acf51cd5bdf625e5eeea3901f8664d6e2db024e,
705declared/40network/57native; installed /srv/codi-connected/releases/native25-46c878c394203e96.
NativePIDs2920272/2920274/2920275, config/etc/codi-connected/ksu/managed.json,
SHA0d4c58f748802c160372b2568f6edebcf40b16f7a5512b126488bc6c05169d5a,
basePath'', schema5, existing instance codi-ksu-hidden. Worker2/3a6d3c5184e52858abe324e37fd4ca410f66d7d289468efe6f169352d347727b,
operator53aa99303600f942a6f40b63718e26f2e73d78bffa0c458ba3d6bebb83a034fc
installed /srv/codi-rooms/{workers,operators}/<SHA>, config/etc/codi-rooms/ksu/managed.json,
worker/proxyPIDs2917803/2917814, private namespace/caps empty/static. File services
1460455/1460457 unchanged. Native units remain disabled boot; bootstrap stopped.
Root/fence3 expires2026-10-25 11:06:16UTC; no automatic signer/renewal added.
49account rows total, original38immutable rows retained;2newowned publicQA disabled
in actualDB, alongside9known earlier publicQA. Original prod document baseline0;
nonempty retention proof remains private fixture scope, never imply prod nonempty.

Fixes: bounded4MiB/16record room-binding history (actual14record65655byte failure
was beyond previous64KiB reader), preflight/writer checks; bounded discovery mail
pump includes pending introductions (1s) and healthy8–10s polls inside30s signed
leases, retaining same grant/signature/permission checks and resource bounds.
Source4Chrome realRTC10 and one-line old-interval negative FAIL3 at exact26s
poll oracle (2/3/3/2 new polls versus0/0/0/0), zero leaks. Two identical705file
builds/closed release15, legacyclient26. Actual live normalTLS UI17/36appcycles,
real reload/workspace/drafts/identity archive/emulated phone geometry; WAN12
with3v86/zero seeds,104.180.210.33 and24.126.137.85, initial+repaired link both
ends public TURN/TLS443, full RTC cut+discovery unavailable/server catch-up/
fresh repair/returnP2P, guest/localfile retained. No phone/8k implication.

Publication source81245f4edef2c33ddf6a3532f7bfe0b058315a9b, same clean live checkout.
Native source e66ac44f7fa25add1051e6e44980a74b4972af10 in reader-mail-native-r1,
793+manifest9745d74aaccd6540a5e68563b3e3865fb775a5f22c86a3d5e6ba2614c16b1080.
Protected publisher /srv/codi-connected/reader-publishers/d4711095fb210b38165c765fcaa62bbd7f35fec62da289103016c28af27ef9bf/publish-reader-mail.py,
exact2file graph publisher.json; use existing protected venv517179c, --commit81245f4...
with actual whitespace. Stage→activate-backend→activate→verify allPASS;10s honest
notices, no claim of RAM saving. Root receipts verified root0600+exact SHA:
install1792910891624579985/aa48110f524289d4830cb361e79f503c9722acbb439f5d0b9bdc38b21086b72a;
stage1792910927738957753/cf991b3b783876c192d0f495e240c51d3f2f519dd9cfd6b98a4257ed54e761e4;
activate-backend1792910992754152299/b73e07bb6b68c9ecbbc9fa0c2ac8141161b7389d281f7b4bf0f8ed0f19cc6afe;
activate1792911051011106280/6eecad446a584d14a8a4e5dc73e6e3ec35bbdcd40468f1f0f9c1d6681eaf04f7;
verify1792911059485710782/0ab791105ff613c7784f2053784c749b9be79e3347d5b4cbe8e6129b0f549c98.
Names /srv/codi-connected/reader-mail-<action>-<number>-result.json; install name
reader-mail-publisher-install-<number>-result.json. Full private hashes stay root.
Rollback actions rollback-native then rollback-backend use the same newer pinned
controller, preserve current data and original signing/replay/usage floors;
recover-backend handles explicit outer/inner journals. No25inverse rerun: old
actual inverse23/24/backend9-death proofs retain scopes; latest user removesVMgate.

Fresh live-final-health PASS705installed/133public prototype/blog/all10sites,
keys/realm/cookie/permissions/current files/monotonic guest usage retained,
registered-only guest egress/kernel guard/relay/forwarding0 unchanged. Website
20261024T110552353972Z-299874f5 and hosting pins7174daa2/df92e3ef/42161b4b unchanged.
Native24/ba894 and its dbc2 publisher remain immutable staged/inactive, superseded;
do not activate them. Public prototype remains backend-free. /hidden redirects
root. No Caddy/router/firewall/ports/boot change. Root and blog remain actualpaths.

All current jobs terminal. Outside driver16881/forward4016866 details must be read from
reader-mail-wan-cleanup-r1 and cleanup-verified; do not reuse retired handles.
Cleanup verifies actual outside driver/folder missing, both listeners refused,
localforwardPID missing, localdriver contexts0 and actual2publicQA disabled.
The earlier unused outside fixture16743/4006653 also cleaned. No USB needed.
reader-mail-milestone-r1 PASS binds19receipts, wholeGoalComplete=false.
Previously started private25 UI17/36cycles/Linux11 and custody upgrade completed;
no new VM tests were launched after the workflow change.

NEXT implement/test directly on live: structured redundant islands/layers/bridges,
measured mostly-reading/burst/churn/partition/overload/fallback8k transports,
independent replicas and valid original-ID missed-operation convergence, durable
chess seats/moves/spectator chat/long history and complete reference/audit ledger.
Operational stability still includes startup/reboot, complete current backup/
restore, signing expiry monitoring/explicit policy, sustained resource/fault soak
and real S25 feedback. Do not turn those into a renewed VM-first gate or reset
any ledger. Still no whole distributed/8k/durable-chess/finality claim.


## Development-only cleanup and retention — 2026-10-25 UTC (LATEST)

User clarified there are NO real accounts, all are tests, and the externally
reachable site is a development site, not a launched public service. Prioritize
fast direct live development/tests. Stop describing generated test records as
real production accounts or requiring a VM-first release process.

User explicitly requested cleanup of versions/artifacts we will never use.
Supersedes previous notes requiring retained VM state/all expanded releases.
Stopped owned QEMU3283572 via its known QMP fixture, verified it terminal, then
removed agent-generated .build/native-network-vm (~9.75GB allocated). VM is gone;
do not poll its old handles or recreate it as a testing gate. Prior receipts
remain historical evidence. Deleted107obsolete local generated release directories
(~8.12GB), preserving only connected-reader-mail-native-r2 (live25/46c878c3)
and connected-hosted-readers-native-r2 (one rollback22/9537). No process references
were present in deleted builds. Compact Git history remains available; old
historical builders may need an explicit Git restore of their frozen base, not
permanent expanded versions. Future work should build from the current version.

Local deployment checkout now uses sparse checkout: top-level site content plus
reader-mail-native-r1, reader-mail-publisher-r1, reader-directory-native-r1
(current worker/operator dependency), and reader-mail-live-proof-r1. Older binary
package copies are NOT materialized. Source history/commits remain in Git;
checkout clean. Reclaimed~2.91GB locally. Server source checkout uses same pattern
and was repacked (Git now54MB), source commit still81245f4; runtime unchanged.

On webhost removed22unused release directories (~1.62GB), checked runtime/config/
unit/process references under hosting lock, preserving only native25-46c878c394203e96
and native22-9537a6b6d4ab7074. Historical receipt/plan references do not make old
binaries runtime dependencies. Keep actual current venv517179c, current/rollback
room workers/operators and the protected publisher's small legacy helper; no
service-state/website/hosting changes. Inactive24 is now DELETED, not staged.
The site stays on live25 with nativePIDs2920272/2920274/2920275, file/room PIDs and
managed config/hosting pins unchanged. Fresh reader-mail-after-cleanup-health-r1
PASS705/133prototype/blog confirms this. No service restart during cleanup.

Retention from now on: current + one usable rollback, required active dependencies,
and compact source/proof history. Remove disposable expanded builds/test fixtures
after each completed update; no accumulating per-version full copies. Current
local keep policy .build/development-retention.json; reusable scoped command:
`python3 -B active-system/scripts/prune-development-builds.py --apply`.
Default command inspects only; protects pinned manifests, symlinks and active
process references. Update its two keeps when publishing the next release.
Do not turn cleanup into a long archive project or preserve unusable old versions
as release gates. Existing account/file data is test data; we did not need to
wipe working service state to reclaim space. User source/supplied inputs untouched.

Local free space rose from~2GB to~22GB; active-system/.build shrank19GB→1.7GB,
local source checkout3GB→~254MB. See development-vm-cleanup-r1, development-build-
cleanup-r1, development-source-checkout-cleanup-r1, development-webhost-cleanup-r1,
development-webhost-source-cleanup-r1 and fresh health receipts. Full feature goal
remains ACTIVE; continue direct live increments for islands/layers/scale,
replica/original-ID convergence, durable chess and audit/operational stability.

Live25/cleanup proof frozen/pushed 8918866d4b9a3d822fdf45b354e43303789209ed in reader-mail-live-proof-r1:38files plus manifest3aeaea870e1085950780b5a37a1c544d42a9a4538d4979bd09e7eb878d3ab1a8. All tracked bytes/remote/clean verified. Server editable source remains81245f4; evidence-only commit does not restart services. Current + one rollback retained; no VM remains. Development-only/test data/live-first workflow is authoritative. Goal ACTIVE.


## Full-island reader update — 2026-10-25 UTC (LATEST)

Externally reachable development site, NOT public launch; all accounts/tests.
Live root is native25/6ebdb23536e1fdaafd82c7372bfc01126cbedcb94190b4060f3a0b980ced5321,
340files/40modules; runtime /srv/codi-connected/releases/native25-6ebdb23536e1fdaa.
All57 native files and apps byte-identical to previous25. Frontend keeps sampling
when full, adds local ring/bridge preferences and make-before-break retirement
with explicit two-endpoint negotiation, idle/ownership/shared-use refusal and
bounded expiry. Send refreshes authority before the150s room lease renewal
window, fixing the longer-source-test acceptance failure without weakening checks.

Source32d7e598cde9329a94920b3a209f565ec82ba612, package reader-topology-update-r1,
394files+source-proof975e68a7ff260ab8df4ecf87989181bcd9b2d0ca0a1fda00380ee0c95cb390ee.
Protected publisher /srv/codi-connected/topology-publishers/983f152ef541369cfe521ebe2ef361aae00b8c6fcfa1d213debfc4492d14b254/publish-reader-topology.py.
Actions stage/activate/rollback/recover/verify with --commit32d7e598 (full40hex
argument required) use existing native/hosting locks and preserve actual state.
Real live stage→activate→verify→rollback→verify→activate→verify PASS; previous25
46c878c3 is now the usable rollback. No backend/hosting/router/ports/boot change.

Current nativePIDs3017245/3017247/3017248; files1460455/1460457 and room2917803/2917814
unchanged. Managed config1ccc1d0bb1f7078dfb8468863c6a35db261bc8a9bf14a6e5244e44f3360b86a3.
Worker3a6d3c51/operator53aa9930/venv517179c remain. Hosting7174daa2/df92e3ef/42161b4b,
website20261024T110552353972Z-299874f5, egress436096d7 and forwarding0 unchanged.
51account rows, ALL TESTS;38original rows retained;2newQA disabled in actualDB.
Root/fence3 still expires2026-10-25T11:06:16Z. Do not reset floors or mint authority
to green a check. Native units disabled boot; bootstrap stopped.

PASS: source ten actual Chrome identities merge two full5-reader islands25.03s
without cross seeds; captured graph has no single-node articulation, actual
bridge cut preserves RTC-only convergence; one completed negotiated retirement;
100ms samples within caps/all leases0. Ownership/lease10, legacy11, exact340-file
build5/native57 unchanged. Live UI17/36cycles and WAN12/3Linux/2publicIPs/normalTLS/
initial+repaired public TURN TLS443/fallback+RTCreturn PASS. Fresh all10sites and
health-r2/all340installed/133externalprototype/root/blog/state/guard PASS. Initial
topology-r1 failed at the lease boundary; old-condition mutant reproduces it.
Initial concurrent bulk health timed out; later complete rerun passed, physical
cause unproven. Keep failures in evidence, not promoted as passes.

Only current6eb and rollback46c8 expanded releases remain local/server. Old22 and
5disposable rebuilds deleted after successful live rollback (~538MBlocal/~95MB
server); builder removes410obsolete graph files and builds from current, no VM.
Outside fixture driver17503/38961/forward4040439→36557/folder1792915518009550653
confirmed missing, both ports refused; local browser contexts0. Do not reuse old
handles. No USB needed. Health tool's post-timeout URL diagnostic is working-source
only until frozen with the final evidence packet; runtime unchanged.

Goal ACTIVE. See active-system/evidence/reader-topology.md (omit active-system/
when inside that target) and reader-topology-milestone-r1. NEXT prove/refuse
simultaneous retirements overbooking excess degree at one node: current per-link
freeze is not a per-room reservation. Then finish structured layers/redundant
islands/bridges, measured8k transports/loads/churn/faults, independent replicas
and valid original-ID reinclusion, durable chess, full audit/operational proofs.
This is not a global-ring, robust8k/layer/replica/chess/stable-public-launch claim.
User's live-first speed/cleanup instructions remain authoritative; no VM gate.

Final evidence is frozen in reader-topology-proof-r1 (no runtime copy): current20 passing receipts,3 retained failures, milestone, cache274-record proof, diagnostic health source, ledger and handoffs. Server source/runtime deployment commit remains32d7e598; evidence-only publication does not restart it.


## Cold consent, bounded retirement and32-reader islands — 2026-10-25 UTC (LATEST)

Live development root, NOT a public launch; all accounts/data are tests. Current
native25/b96762fc404e3dce6d4baa76e841e00a1d76308d3c8aa8c05be89c3bc1e8bb34,340files/40modules,
/srv/codi-connected/releases/native25-b96762fc404e3dce. Rollback is previous25/6ebdb235
(/srv/codi-connected/releases/native25-6ebdb23536e1fdaa). Old46 is now DELETED.
All57 native files and app bundles unchanged. NativePIDs3109533/3109535/3109536,
files1460455/1460457 and rooms2917803/2917814 unchanged. Managed configSHA
29130ed34b5e1b7c4d6a8284c8f099e1fdc516590ff562dc665bc25e2679d686.
Worker3a6d3c51/operator53aa9930/venv517179c, hosting7174daa2/df92e3ef/42161b4b,
website20261024T110552353972Z-299874f5, guest egress436096d7 and forwarding0 unchanged.
54test account rows,38original retained,3newQA disabled in actual DB. Root/fence3
expires2026-10-25T11:06:16Z. Before further live work inspect remaining signing
window and the documented explicit bounded-renewal policy; do not reset floors
or mint authority to green checks. No unattended signer; native boot disabled.

Current source54a9d58ae3efc59217a1239aa512c8d2e8586d7f, package reader-slot-update-r1,
410files+source-proofde6628f4d72141f87e58d8986ad2771996caa8d7ed96b1a0d17c436f3a6ce032.
Protected publisher /srv/codi-connected/slot-publishers/5a65ae04dee0795e3307848d28c4fa5616589fe73dd865a80555a23581cb2394/publish-reader-slot.py
with --commit54a9d58 (full40hex argument required), actions stage/activate/rollback/
recover/verify. Real live stage→activate→verify→rollback→verify→activate→verify
PASS, preserving data/keys/floors/backends with honest10s maintenance notices.
No Caddy/router/port/firewall/boot change; root/blog/prototype actualpaths intact.

Implementation: per-room surplus reservations include incoming and outgoing
retirements and recheck before close; accept valid signed interest in already
loaded public rooms without a returned checkpoint; new negotiated
codi-hosted-reader-interest/1 exchanges at most32 per-connection salted hashes
using existing links/tick/budgets; matched routes reserve capacity before hello;
head notices reach all consenting watchers within existing24-peer/scheduler caps
instead of permanently skipping trailing bridges. No write/file/Internet grant.
Hashes omit raw IDs in this phase; not cryptographic private-set intersection.

PASS source component12: cold peer/server-read outage, hashed matching, overlapping
requests/cancel/expiry/unsolicited ack, all-five notice delivery, foreign-room
refusal and all leases0. Original overlap/hello/disabled-interest/first-four-only
controls FAIL at intended assertions. Early fixture failures (wrong fixture
password/noncanonical synthetic IDs) and preliminary topology failures remain
failures, not product proofs. Final source32 Chrome/2x16 partial islands PASS11: 
35.388s merge, zero manual cross links, captured graph no single-node articulation,
actual bridge cut, RTC-only3x8 accepted-message bursts,100ms bounds and all leases0.
Burst convergence3.882/14.726/30.544s; authenticated application mean18.96/7.88/5.54kB/s
per browser; JS heap means5.49/5.62/5.81MiB, accounted metadata14.73/14.49/14.04MiB.
Not native/RSS/wire overhead, sustained plateau,8k or full-v86-at32 proof.

Live UI17/36cycles and WAN-r3 PASS12/3fullLinux/2publicIPs/ordinaryTLS/initial+repaired
TURN TLS443/fallback+RTCreturn. WAN-r1 final scripted send bypassed UI-busy guard;
helper now waits for idle. WAN-r2 outside Linux boot exceeded the old90s harness
allowance; physical cause unproven. Diagnostic normal outside boot51.401s with
progressing CPU/visible/unblocked state. Helper records boot progress with180s
VM-start allowance only; protocol timing/expiry/capacity unchanged. Successful
WAN-r3 cold boot14.123/14.404/47.861s. Guest filesystem retained through churn.
Health-r2 all340installed/133externalprototype/root/blog/guard/state and fresh
all10sites PASS. No source/runtime change for harness fixes; freeze final helpers
with the evidence packet. Keep failed attempts and their actual scopes.

Only currentb967 and rollback6eb expanded releases remain local/server. Deleted
old46 and7disposable builds (~718MBlocal/~96MBserver); sparse source removed unused
reader-mail-native/publisher packages, compact history kept. Controls retain
small exact fixture/module overlays, not old full releases. Current base for next
build is connected-reader-slot-r7; do not restore old baselines or recreate VM.
Outside driver18169/44129, forward4122133→46931 and folder1792919949896106324 are
confirmed missing, both ports refused; local browser contexts0; no USB needed.

Goal ACTIVE. See active-system/evidence/reader-islands32.md (omit active-system/
inside that target) and reader-slot-milestone-r1. NEXT staged larger independent
SDK-agent/real-transport loads toward128/512/8000 with isolated actor storage;
explicit structured island/layer routing, sustained/churn/partition/overload
resource plateaus including native memory and wire overhead; missed original-ID
/replica convergence; durable chess/long games; full requirement/operational audit.
32-source graph is a useful bounded partial mesh, not proof of complete layered
routing,8k transport, replica agreement or a stable public launch. Preserve
live-first speed/cleanup and no VM gates.

Final reader-slot evidence is frozen in reader-slot-proof-r1:21 passing receipts,9 primary retained failures, additional fixture-setup failures, current helpers/ledger/handoffs, no runtime copy. Server editable source/runtime remains54a9d58; evidence-only publication does not restart services. Source32 and live3Linux/WAN scopes remain distinct.


## Root4 and staged SDK agents — 2026-10-25 UTC (current work)

Externally reachable DEVELOPMENT site, not a public launch; all accounts/data
are tests. Live remains native25/b967, rollback6eb, current2expanded releases;
no VM gate. Root4/fence4 was explicitly renewed for86400s using unchanged
protected installed CLI, expires2026-10-26T10:26:06Z. Same keys/realm/accounts/
files/cookie/config during renewal, no auto signer. Source e69063354a9fd87cd8642ef9677c4758f1483300,
root4-renewal-r1 source proof a2c76067a9f757e6ec8b491be404dea5f6995728d427ec82c25f15bce6bdd57a.
Receipt explicit-live-root4-renewal-r1-result.json; root receipt
/srv/codi-connected/explicit-root4-renewal-1792923955401574954-result.json,
SHA4b899c22a953dbb8cbd9569d465dbcaa60f45a618062f6696f4d7f903185d50c.

Root4-aware publisher is now /srv/codi-connected/slot-publishers/8275b4b942b97c303bce467a7f6bbeca9bd62adf828ea85d9de986de9690fc81/publish-reader-slot.py
with --commit df4fa4ef8c6fc4af4e46917726a213ad107f6b73. Exact source packet
reader-root4-operator-r1 manifest7c97ff75ad04f47ef682ffc3c3b6228863911c608165568ae8e814152509e52d.
Real verify→rollback6eb→verify→activateb967→verify PASS; Root3 historical
baselines preserved, current Root4 bound to legitimate receipt and independent
fence. Old Root3-only publisher is historical; never restore old authority to
pass it. Native PIDs after deliberate code cycle3209714/3209717/3209716, files
1460455/1460457 and rooms2917803/2917814 unchanged. Config29130/hosting pins
unchanged. Fresh health-r3 PASS340installed/133externalprototype/root/blog/state,
55test rows/original38 retained; new UI QA disabled in actual DB. Live UI17/36
reopens and all10fresh site checks PASS, ordinary TLS. No router/port/boot change.

New hosted-agent loader/host/load-check scripts test the actual published40module
SDK graph with iframe JS realms and separate native IDB namespaces per signed
agent. Supervisor conveys commands/room IDs, never checkpoints. Four-agent and
16-agent suites PASS13;128 agents across4real Chrome instances PASS14,6x8 bursts
count50/history32, sampled caps6neighbors/8automatic/4pending/16jobs, all leases0.
128 bootstrap96.272s, bursts7.778/7.655/10.256/9.976/10.883/22.689s. RTC signed
application bytes only, not HTTP/DTLS/SCTP/IP; process descendants RSS double
counts shared pages, PSS~2.36–2.97GiB aggregate. Not a sustained plateau/8k/v86
claim. Shared-IDB mutant FAILS the intended isolation guard.

512 attempts are not accepted: r1 rapid admission hits ordinary room600/min rate;
r2 pacing plus a global start barrier lets early signed leases expire before
pumps start, readiness timeout; r3 starts clients as admitted but background
HTTP refresh still hits600/min. Each failure is retained. No raised limits.
Found source issue: unchanged refreshed signed heads were never announced, and
notices/minimums tracked only count/permission, causing quiet readers to refresh
separately. Candidate raw hosted-room-client now propagates valid freshness,
keeps bounded one-hint/4-peer state and monotonic session authority freshness;
no expiry/signature/permission bypass or execution replay. Component fresh-r3
PASS8 (three-hop quiet authority, old unexpired proof refused, forged expiry
refused, leases0), legacy peer20/pending5 PASS. Old deployed graph fails fresh-r1
at first freshness epoch. Candidate68085c9b1162d3fd70efb84804e373418e5babb9a2cccfc2aa6149087dc1d52a
is built at .build/releases/connected-reader-freshness-r1,340files/57native and
app bundles unchanged, NOT yet installed/live. Candidate512 run in progress.
Latest source/server df4fa4e; new harness/freshness source/proof not yet frozen.
Goal ACTIVE;8k/layers/replicas/original missed ops/durable chess/audit unfinished.


## LIVE680 freshness fix and bounded128 acceptance — 2026-10-25 UTC (LATEST)

This supersedes the preceding candidate/in-progress note. Externally reachable
DEVELOPMENT site, NOT a public launch; all accounts/data are tests. Root desktop
and /blog/ remain live; /desktop133 unchanged. Native25 is now
68085c9b1162d3fd70efb84804e373418e5babb9a2cccfc2aa6149087dc1d52a at
/srv/codi-connected/releases/native25-68085c9b1162d3fd,340files/40SDK modules.
Rollback is b96762fc404e3dce6d4baa76e841e00a1d76308d3c8aa8c05be89c3bc1e8bb34
at /srv/codi-connected/releases/native25-b96762fc404e3dce. OLD6eb is DELETED
local/server and removed from expanded sparse source; compact history remains.
Local current .build/releases/connected-reader-freshness-r1, rollback
connected-reader-slot-r7. Keep current + one usable rollback; no VM gate.

Source/server checkout bd8b6ce183ee8e876dde20c35521fa64661aa4e5; packet
reader-freshness-update-r1,443declared+source-proof f80ed66b57fc88aae89391a51b82cab502f9b946d0077d1e20e8302b7e20bc48.
Protected publisher /srv/codi-connected/freshness-publishers/9fa34e4ad230e23a6e96daf1920fb90e2195fcab0d3113a846609e1c1c48e092/publish-reader-freshness.py
with --commit bd8b6ce183ee8e876dde20c35521fa64661aa4e5. Operator manifest
fb1aa6f1d8406b52599ff3e6841268a4b6116b9ea53ba6472c978d2e41ba25f9,
only the small operator/ subfolder installed there. Prior slot publishers
require retired6eb and are HISTORICAL; do not invoke them. Small protected
d08b9f7 helper remains an actual dependency. Real stage→activate→verify→rollback
b967→verify→activate680→verify PASS; no data restore or root mint.

Current managed config b56f47fd2f50f80d1738de0360704491385d1c74c70dde76dcf10c3789595d4c,
nativePIDs3266464/3266466/3266467. FilePIDs1460455/1460457, roomPIDs2917803/
2917814 unchanged; worker3a6d3c51/operator53aa9930/venv517179c unchanged. Root4/
fence4 expires2026-10-26T10:26:06Z; explicit bounded renewal only, no unattended
signer. Configured native units remain disabled for boot, bootstrap stopped.
Hosting7174daa2/df92e3ef/42161b4b, website20261024T110552353972Z-299874f5,
egress436096d7/forwarding0/TURN text32-allocation shared1MiB/s unchanged. No
Caddy/router/firewall/port/boot change. Caddy still managed, never hand-edit it.

Fix: valid controller-refreshed heads now propagate even with no new message.
One bounded hint/four preferred peer IDs also track signed head expiry/lease
revision. In-session freshness never decreases when a peer returns an authentic
but older unexpired checkpoint. A notice does not advance a saved floor; the
normal verified transfer is still required. Same signatures/expiry/permissions,
no membership grant or live replay. Selected snapshot now exposes headExpiresAt,
authorityExpiresAt and leaseRevision for inspection.

PASS final source8 (quiet three-hop updates beyond original30s head expiry with
no follower HTTP, valid-but-older head refusal, forged inner expiry refusal,
leases0), legacy peer20 and pending5. Old deployed graph FAILS the same original
freshness regression. Preliminary fresh-r2 failure was a harness reconnection
that had not re-established consenting room watchers; restored real reads on
replacement links fix the harness, preserving bookmark privacy. Final independent
rebuild340 identical bytes,57native/app bundles unchanged,274cache records PASS.

Final actual SDK128 across4Chrome/0v86 PASS15; each actor has real keys/issuer
identity/native IDB/RTC, supervisor only passes commands/room IDs. Admission
93.380s, subsequent graph settle56.198s; six8-message bursts converge
8.496/6.352/7.400/7.410/7.299/8.035s, count50/history32. Sampled caps6neighbors/
8automatic/4pending/16jobs and all leases0. Mean/aggregate signed RTC application
bytes exclude HTTP/DTLS/SCTP/IP; process RSS double-counts sharing, PSS apportions
it. Not a sustained memory plateau, real128 full desktops, multiple writers,
512 or8k proof. The initial publishedb967 also has separately scoped4/16/128
proofs. Shared-IDB mutant fails the isolation guard.

All512 attempts remain FAIL. Rapid admission and active warmup hit actual shared
ordinary room HTTP600/min; one global-start barrier also stalled early readers
after extended idle startup. Final680 attempt reached371verified readers then
429, NOT512acceptance. Quiet freshness fix is proven separately; it does not
resolve all admission/background pressure. Do not raise limits or call it fixed
without measured admission/backoff/load work. Fixture issuer setup rate is
10000/min, so these are not production identity-admission capacity claims.

Live UI17/36reopens PASS. WAN12 PASS:3actual Linux/v86 Chrome desktops, home
104.180.210.33/Moonpie24.126.137.85, ordinary TLS, zero manual seed links, actual
public TURN/TLS443 both ends of initial+repaired paths, complete RTC cut with
unavailable directory→authorized server fallback→fresh discovery/peer return.
Original guest identity/browser-local file survives. Initial boot14.068/14.246/
47.164s under existing measured180s allowance; later ready checks are not cold
boots. Actual current health-r2 PASS340installed/133externalprototype/root/blog/
keys/realm/original38 rows,57total test accounts; both new UI/WAN QA disabled in
actual DB. Fresh all10site smoke PASS. Zero owned local contexts; outside
driver19739/60515/profile1792927302287830075 and localforward157519/49957 confirmed
absent/closed, folder removed. No USB needed. User normal Chrome untouched.

Cleanup removed old6eb(~88.75MB local +~88.75MB server), current/rollback packets
only in expanded source, no service restart during cleanup. Initial cleanup
bootstrap selected system Python via argv0 and failed before deletion; corrected
explicit venv argv0 passes. Independent rebuild helper first selected an invalid
/tmp destination, then an obsolete raw contract import; reusable
verify-network-update.py uses the current sealed contract and scoped temporary
build,340-byte comparison/cache proof PASS and temp removed.

Bounded milestone reader-freshness-milestone-r1-result.json PASS binds21passing
receipts and9retained failures, wholeGoalComplete=false. Evidence is NOT a stable
public-launch or8k acceptance. Goal ACTIVE: resolve admission/background pressure,
stage512/larger actual transports, implement structured islands/layers, original
missed-operation/replica convergence, durable chess/long games, full audit and
operational proofs. R730 was inspected read-only:56CPUs, ~264003136KiB total RAM,
254877280KiB available at that probe; browser/driver absent, no tools installed,
LLM/services untouched. It may be a future load worker, not an8k capacity proof.

Final freshness evidence frozen/pushed 00f82f3d39ab0edd063882b54236fb2181ba4eff in reader-freshness-proof-r1:64declared files plus source-proof d1345b80a74224a1e06dd1d69f36107955185d0c9caf211fc5f2f91a4435588a. All bytes/remote/clean verified. Evidence-only commit was not installed/activated; server editable source and runtime deployment commit remain bd8b6ce183ee8e876dde20c35521fa64661aa4e5. No owned test jobs/browsers/tunnels remain. Full goal ACTIVE;512/8k and other required work explicitly unfinished.


## Current development update — 2026-10-25 (LATEST)

Live root native25/138a5129, worker870df3f9, sourcefd9bc2a5: atomic signed room
reads and bounded cancellable transient READ backoff. Real managed backend and
SDK forward/rollback/re-upgrade12, liveUI17/36cycles, two-network three-v86
TURN/TLS443 recovery12, health340/133prototype/root/blog and fresh10sites PASS.
This is development, not a public launch; all59accounts are tests. Keys/files/
permissions/floors preserved; QA disabled. Current+usable rollback680 only;
expandedb967 and WIP730 removed. Root4 expires2026-10-26T10:26:06Z.
Full goal ACTIVE:512/8k/layers/original missedoperations/replicas/durablechess
remain unfinished. Both512 diagnostic runs were explicitly stopped; no active
load job remains. The second verified all512 stored floors and signed identities
but not delivery. Final batched supervisor4-agent suite16 PASS; next full512
run belongs on R730 (isolated official Chrome/driver156 and projectvenv ready,
no driver/job started or existing service changed). See the latest detailed
active-system/HANDOFF.md and active-system/evidence/reader-atomic.md.


Latest13:55UTC: proof-only commit a0183857c3e45eff970ca7d95adf6b9c1b140b40
pushed/clean, webhost runtime/source staysfd9bc2a5/current138. R730 actual4-agent
suite16 PASS; full512 now RUNNING on r730 PID1439080 (nice10), log/result under
/home/dflanag3/codi-load-tests/runs/atomic-agents512-r1/. Process/argv verified
alive. Owned loopback ChromeDriver1438042/127.0.0.1:56503. Do not duplicate it;
inspect actual process/result, then clean owned driver/contexts afterward.
See latest active-system/HANDOFF.md. Goal ACTIVE, full512/8k still unproven.


## Current development update — recovery readers and512 load (2026-10-25, LATEST)

Externally reachable DEVELOPMENT, not public launch; owner only/test accounts.
Current root native25/e5164042,298 files/40modules/57native unchanged; rollback
138a5129. Source0344f668; live worker870/operator53aa unchanged. Reader-only
upgrade/rollback/re-upgrade7, liveUI17/36reopens and health298/133prototype/
root/blog/all10sites PASS. Root4 expires2026-10-26T10:26:06Z. No new ports/boot/
hosting changes. Source original-proposal recovery12/11/14/8 and disabled/legacy
regressions PASS, but recovery writes/controls are NOT enabled live. Reader-first
rollback migration is required before producer activation; preserve private state.

R730512 SDK agents/16Chrome/0v86 PASS16, six8-message bursts24.674–49.157s, all
leases/DBs close.2048actors/64Chrome attempt FAILS during channel admission after
last1057 progress report; no exact final admitted count/2048pass. Connection reset
and capacity pressure need work; some later500s may be old fixture teardown
artifacts. Owned R730jobs terminal, driver1438042/port56503 gone, contexts0,
temporary profiles removed; current tools/frozen138SDK kept. No service/model
changes. Full goal ACTIVE; see active-system/evidence/recovery-reader.md and
exact receipts. Do not use stale earlier NOW RUNNING/512unproven notes.


## Current live development — interrupted-read fix (2026-10-25, LATEST)

Current root native25/e007ad37, usable rollbacke5164042,298files/40modules/57native
and all7apps unchanged; worker870/operator53aa unchanged. Source8258f558. Actual
SDK managed live upgrade/rollback/re-upgrade7, UI17/36reopens and health298/133
prototype/root/blog/all10sites PASS. Separate-WAN check currently running; inspect
transport-reader-live-wan-r1-result.json before claiming it passed. Root4 expiry
2026-10-26T10:26:06Z; explicit renewal only. Site is DEVELOPMENT, not public launch.

Fetch/body-read resets and owned15s timeout now get fresh-authorized READ retries
(max4/90s/shared cancellable backoff). Invalid data, caller abort and writes never
automatically replay. Source browser17/pending5/RTC8/candidate4agent16/independent
298-byte rebuild PASS; previous client fails reset control.512load PASS16 belongs
to SDK138,2048 FAIL remains unresolved; no8k/stability gate. Recovery writes remain
disabled. Old680 removed local/server/source; older138 now eligible for retirement
after preserving e007+e516. Keep frozen R730SDK138/runner as active test comparison.
See evidence/recovery-reader.md. Full goal ACTIVE.


## Final current development state —2026-10-25 (LATEST)

Current root native25/e007ad37, rollbacke5164042 only;298files/40modules/57native/
all7apps unchanged; worker870/operator53aa unchanged. Managed cycle7/UI17/36reopens/
final health-r3 (298installed/133prototype/root/blog/all10sites/state) PASS. Source/
webhost checkout8258f558, clean. Current publisher a98cb6bf under
/srv/codi-connected/transport-readers supports e007↔e516; earlier138/680 publishers
are historical and target deleted releases. NativePIDs3593297/3593299/3593300,
config20148c456ddc1006139ed5f6a950c742c7d415618c4e4ade422bae514ec6d71b; filePIDs
1460455/1460457 and room3404594/3404596 unchanged. Root4/fence4 expiry
2026-10-26T10:26:06Z. No ports/hosting/security/boot change. DEVELOPMENT, not public
launch. Original account/key/file/permission/replay/authority state preserved.

Current separate-WAN rerun FAIL/incomplete after8checks when Moonpie went offline
(LastSeen15:40:00.1Z; SSHconnect timeout). Peer chat/intermediary loss/full-cut server
fallback had passed; final outside reconnection is NOT accepted. Local3-Linux
scenario11 checks PASS; deliberate final close-response-loss guard PASS confirms
all3 actual browsers close and QA disabled despite retained suiteFAIL. Source
cleanup no longer abandons QA cleanup after one DELETE failure.

All local contexts0/forward669794:52853 stopped; latest4 QA DBpolicies disabled.
R730 old jobs/contexts/driver/profile cleanup PASS;512actual SDK138/16Chrome PASS16,
2048 admission FAIL still unresolved. Current e007 only has4-agent16 capacity
proof, not512/2048 acceptance. Recovery writes remain disabled. Both current and
rollback read the proposed recovery receipt format; source12/11/14/8 passes.

PENDING OUTSIDE CLEANUP: Moonpie maint@100.105.243.29, driver21215/50737, folder
/home/maint/snap/chromium/common/codi-root-wan-1792942316362655575. Saved fixture
forwardStopped=true, remote driver/profile unverified. Do not duplicate it. When
reachable, close that exact owned driver sessions then use moonpie-root-browser.py
cleanup, checking reused PIDs. The user was asked whether it remains powered on.
Root e007/rollbacke516 and current source packets retained;680/138 removed locally/
webhost/sparse source, compact Git history kept; no restart during cleanup.

Full goal ACTIVE: producer migration/original-ID recovery live, improved2048→8k,
structured layers/islands, replicas, durable chess and final audit. Outside host
loss does not block independent implementation. See evidence/recovery-reader.md.

Final proof-only commit0cee69e73700a5e1d40b0b3cde4197584a13ca8f pushed/clean: reader-transport-live-proof-r1,37declared files/source-proof02faba01f196287b89c8933ff9d257b50de14be8b69e057b6c3ca60542506f43. Bounded milestone PARTIAL:13passing/4retainedFAIL, outside fixture cleanup/test incomplete, full goal active. Server source/runtime stays8258f558/e007; proof-only commit not pulled/deployed. No local test job/browser/forward remains.


## Original-proposal recovery enabled —2026-10-25 (IN PROGRESS)

Actual current root native25/b97dce3bb9956d5ed352f238b84d8f0797e18650f315a687f69d4e7eb3718b8d,
worker081bd143a37d486d1984d92389c0b1eb649563d052e3e793bdbd21de7542acdf,
operator53aa unchanged. Sourcee3f3127fd9205c527ec4c6c39c1101460751d845. Full468-file
source packet reader-recovery-producer-r1/source-proof853b999c51aa445fbcb60a1d11e129a5baf584fc1bb9f13a2a50c3c757bb218c.
Protected publishercd875e72 under /srv/codi-connected/recovery-producers, exact
636ddac backend transition. Four forward steps PASS:stage→SDKfirst→backend→verify.
SDK remains298files/40modules,57native/all7apps unchanged; SDK difference is the
explicit proposalRecovery:true flag. Worker changes only contract.py/store.py,
graph2/schema1; ordinary identity/ACL/storage/service isolation unchanged.

Current recovery controls/API are ENABLED, superseding earlier disabled notes.
Same signed expired chat proposal can be explicitly reauthorized with fresh
issuer-confirmed same-account consent/current permission, against exact current
head; its original event ID/signature/author sequence remain. Invalid/foreign/
banned/gap/fork branches fail; no automatic write retry. Not independent replica
consensus or durable chess. SourceAPI12/workflow14/oldworker-HTTP4/newSDKrebuild298
PASS. Exact old870 reads recovered receipt+snapshot, accepts normal fresh-session
message and reopens under newworker without resetting history/floors/key.

Live real-expiry full-Linux download→reload→nativefileimport→explicitrecovery
PASS9, ordinary TLS/real clock, one new same-account SID, exact original on actual
server disk once, both streamfloors1, fresh anonymous read without membership.
Owned browser closed and QA disabled. After-data managed rollback/re-upgrade is
now running; inspect recovery-producer-live-after-data-rollback-r1-result.json
before calling that passed. Usable rollback nativee007/worker870 retained; older
e516 remains temporarily until full rollout verification, then retire it.
Latest live health and forward receipts:recovery-producer-live-health-r1-result.json
and recovery-producer-live-forward-r1-result.json under .build/checks.

Moonpie outside fixture remains offline/unverified; local forward stopped,
no new outside fixture. Root4/fence4 expiry2026-10-26T10:26:06Z; explicit renewal
only. DEVELOPMENT, not public launch. Full goal remains ACTIVE, including larger
transports/layers/replicas/durablechess/audit; no8k acceptance.


## Current original-proposal recovery LIVE —2026-10-25 (LATEST)

Current root native25/b97dce3b, worker081bd143, operator53aa unchanged. SDK298files/
40modules/57native/all7apps unchanged; explicit proposalRecovery:true enables
controls. Worker changes contract.py/store.py only; format2/schema1. Sourcee3f3127,
468-file packet/source-proof853b999c. Protected publishercd875e72 under
/srv/codi-connected/recovery-producers and retained e007 controller/636ddac backend
transition handle b97↔e007 +081↔870. Earlier disabled/currente007 notes superseded.

SourceAPI12/workflow14/old-worker HTTP4/independentSDK298 PASS. Actual liveforward4,
real-expiry fullLinux download→reload/newSID→nativefileimport→explicit original
recovery9, AFTER-DATA rollback3+fresh anonymous old-code read4, re-upgrade3+fresh
new-code read4 PASS. Original public signed event/ID/oldSID and both stream floors
retained on actual server disk once; no restore/root mint/reset. User explicitly
submits with fresh same-account consent/current permission/exact predecessor.
Invalid/foreign/banned/gap/fork branches fail; writes never autoretry. Chat-only
chosen-controller recovery, not independent replicas/consensus/durable chess.

Current UI17/36reopens/phone layout and finalhealth-r3 298installed/133prototype/
root/blog/all10sites/security/Root4/66test accounts PASS; latest2 QA disabled in
actual DB, local owned contexts/jobs0. Current+usable rollback only: nativeb97/e007,
workers081/870, operator53aa. Superseded e516/3907/3a6d/417 removed under pins/locks/
reference checks with unchanged state/config/PIDs/hosting; sparse old packets
removed, compact Git retained. Root helperd08 stays as library with explicit
current operator. Historical older publishers now target deleted code; use cd875.

Native configfa0bb0d8301207b5585afaddf4f3582179782fcefd25be1913d450841df576ef;
PIDs issuer3658696/steward3656435/guest3656436. Rooms3658086/proxy3658093; files
1460455/1460457. Root4/fence4 expires2026-10-26T10:26:06Z; explicit renewal only.
Native boot disabled/bootstrap stopped; no router/ports/hosting/ACL/TURN change.
Site is DEVELOPMENT, not public launch. /desktop/ and /blog/ preserved.

Moonpie prior21215/50737/profile fixture remains offline/unverified; no duplicate
fixture, local forward stopped. Reconcile when reachable; no new outside-WAN pass.
R730 old load jobs/driver/profiles cleaned; frozenSDK138/runner retained.512 SDK138
PASS16,2048 admission FAIL remain their own scope. Full goal ACTIVE: improved
2048→8k actual transports, redundant layers/islands, independent replicas, durable
chess, final audit/operations. See active-system/evidence/original-proposals.md.

Final recovery proof-only commit34478c7258fd84c395f542d13b26b3d31ddb0a8b pushed/clean: reader-recovery-producer-proof-r1,35declared files/source-proofc84a2406ef1ba89ad8ea1e05637a6de574cbea93dfbb053abb5465cec6e7e1d3. PARTIAL whole-goal milestone binds17PASS/2retained fixtureFAIL; recovery feature live/verified, full goal ACTIVE. Webhost checkout/runtime remains e3f3127/b97+081; proof commit not pulled/deployed. No owned local test job/browser remains; Moonpie fixture cleanup still pending offline. Next staging load needs updated current SDK/runner; existing R730138/09e21c2a bundle is the historical comparison, not the interrupted-read fix.


## User-directed separate coordinator + P2P-first introductions —2026-10-25 (CURRENT WORK)

User explicitly approved: coordinator must NOT share saved-chat process; peer
introductions first, then test actual scale. This supersedes starting a2048 rerun
on the old shared discovery architecture. No extra public/router ports: same
ksu.codes HTTPS443, dedicated /rooms/readers/* service behind managed Caddy.
No new service is deployed yet; current site stays b97/081/operator53aa.

Source prototype: reader_service/contract.py and http.py use an independent key,
with a discovery-only delegation signed by the existing room controller. The
coordinator verifies public room descriptors using the room PUBLIC key; it has
no RoomStore/room-private-key/acceptance API. Rendezvous now supports this key/path
separation with legacy defaults unchanged. Actual separate child process8 tests
PASS incl fresh identity/realPoW/signedticket/presence, forged-purpose/path/key/
expiry refusal, no RoomStore imported, saved-chat write while coordinator SIGSTOP,
resume. This is NOT installed UID/DAC/systemd isolation or browser/WAN proof.
Legacy discovery20 PASS. Initial2 prototype FAILs were missing serialization/
private-key loader imports in the test child, corrected.

Browser WIP (not built/deployed): typed delegation verifier and separate authority/
use paths in HostedReaderDirectory; HostedRooms readerCoordinator flag defaults
false; peer introductions preferred after first neighbor, coordinator bootstrap/
15s repair fallback. Peer protocol remains self-signed presence/SDP; no new write
permissions. These JS changes still need actual Chrome tests. Need managed own
credential/UID/namespace/socket proxy/certificate refresh, strict public policy,
Caddy route+legacy-discovery block, SDK rollout/rollback, independent failure and
resource tests, then actual staged agents.

Load harness preparation BEFORE coordinator edits: current b97 SDK4agents/1Chrome/
0v86 PASS17 with proposalRecovery:true; shared-IDB control correctly FAILS, forced
post-admission failure confirms live fixture preserved, all4leases close and temp
removed. Frozen80-file runner at .build/load-runners/recovery-20261025-r1, SHA
bebbadb028cb7e34bbab660d2f73cd7b0b11bc0c0b34f94f383ec0ff78789963.
This is a baseline, NOT separate-coordinator acceptance. No R730 new driver/job
started; actual /proc inventory empty, load near0. Older138/09e21c2a remains old
comparison. New larger fixture should use a real independent frontend/router and
coordinator process, keeping real worker/rate/mailbox caps; avoid measuring the
old shared Python front-end semaphore/GIL as a production coordinator limit.

User backup question: verified box-git:/srv/data/git/ksu.codes.git exists, bare,
latest published source34478c72. Uses1692639232bytes(~1.6GiB), disk available
443217100800bytes(~413GiB). This backs selected deployed source/history, not every
uncommitted worktree file or private service data. Parent CodiServer repo has a
separate r730 remote. New WIP code should be frozen/pushed promptly.
Full goal ACTIVE; Moonpie outside fixture still offline/unverified.


## Separate coordinator privately installed; public routing still pending — 2026-10-25

Previous brainstorming-only goal turn was no progress toward implementation; this continuation made concrete code/test/backup/installed-service progress. Full goal remains ACTIVE.

New reader_service delegation/operator and closed worker12/operator16 graphs pass actual installed-systemd10 checks: separate DynamicUsers, private namespace/empty caps, source key and proxy credential denials, no Internet, root room-delegation refresh/no-op/expiry/wrong-key refusal with stable worker PID, armed static hourly timer, interrupted configure recovery, unit tamper refusal, retained identity after stop/start. Full browser8 passes four actual Chrome/independent Caddy/coordinator with old reader slots saturated, peer-only repair while coordinator stopped, restart/new tickets and zero tracked leases. HTTP8/legacy20 PASS. Credential0400 assumptions failed on actual systemd root:root0440+named-service ACL; final loader strictly validates the complete ACL. Harness r3 wrong-key refusal exception handling corrected; failures retained. All owned local systemd fixtures removed.

Source229files/manifestbd33e69f193d8b52e76253d766f817a82642f288f4f87853f92e6fa082ad7354 pushed to box-git main395383a2cbf34c0892da451fa3f13ca7089a959a, pulled/verified on webhost. New private worker d302ae97a8df296a90b6fa570cf5df191d4b16b2c14165b8a0bc3e17ecb04d33 and operator325e7d9eb47a882636eb8253b9fe79700f76449d1428d39f64397ee1a53699f5 installed /srv/codi-readers/{workers,operators}/<SHA>. Config /etc/codi-readers/ksu/managed.json, units codi-readers-ksu{,-proxy,-refresh} service/socket/timer, private loopback8143 only. Worker3786297/proxy3786303 observed, UIDs63464/64295; static/disabled boot. Delegation refresh uses existing ONLINE ROOM signing key via root job LoadCredential, no primary root signer. Installer aac0b9d... protected /srv/codi-connected/coordinator-installers/<SHA>. Root receipt /srv/codi-connected/reader-coordinator-private-1792951366063521519-result.json.

Actual webhost6 private health/failure checks + all10sites PASS. SIGSTOP coordinator leaves root/blog/prototype/saved-chat HEALTH responsive; no production room WRITE during this host check. Local browser/HTTP tests prove actual signed-write isolation. All298 native/133prototype files and old room manifest exact. Existing SDKb97/worker081, nativeconfigfa0bb0d8/roomconfig92f95a5d, hosting generator7174daa2/manifestdf92e3ef/Caddy42161b4b unchanged. No public discovery route/SDK enable, router/firewall/Caddy/boot change; visitors STILL use old shared discovery lane.

NEXT: managed coordinator routing and external legacy-reader block, SDK readerCoordinator enable/rollback, real live browser acceptance, then staged2048->8k actual agents through independent Caddy/coordinator with real existing caps. Do not rerun2048 against old shared architecture and call that the new result. Existing512/2048 remain historicalSDK138. Private coordinator installation is an intermediate step, not completed visitor separation. Root4/fence4 expires2026-10-26T10:26:06Z, explicit renewal only. Moonpie offline fixture cleanup/WAN proof still pending; no current load job onR730. See active-system/evidence/reader-coordinator.md and coordinatorWork ledger.

Final private-install proof10files/manifestd7505e9805fc9b040f52f02d234c7e8f5ae4d8a8fd59f1e7ac949c140ea3601b pushed to box-git mainb0cbcaef8094e2aee4476e39015652ba57d446bb. Webhost source checkout395383a, private coordinator running; proof-only commit not pulled/deployed. Public SDKb97/worker081 and hosting unchanged. Local owned test sessions terminal and fixture units removed; no new R730 scale job started. Full goal remains ACTIVE.


## Coordinator live; real128 load exposed sender lease race — 2026-10-25 WIP

CURRENT live root SDK5ac541f0e439dc0808ece01115f4aa1307e6e531449bddd7c38bfd8175c5329e (native25/298files/57native and7apps unchanged), worker081 unchanged. /rooms/readers/{authority,health,use} now routes to separate private8143; Caddy410 blocks legacy Codi-Reader traffic before saved-chat process. Managed codi_readers=active; hosting generator26da0e71121f385f54abf36247afd0bb575b3c5926906403cc09d735bd0e1bd9, manifest9bccf2519656c22f6f0043aa03b673fbfeac9c21e4f3928934922208914afa7e, Caddy2a7cbaf41186112fdc47c95af7abdbbf3689faf5b149ee72031a161743b94270. Native confige148707758d2a19955a96fb0ae78a6fd95ecb056c557ab3947d621770dc0f4dd observed. Rootpublisher3327d4c6efe400a71544350d652a1b737220ff3072e728368fb090214da9d0ad under /srv/codi-connected/coordinator-publishers/<SHA>, source99a683f. Git main91f9435 adds runner only; webhost checkout99a683f remains exact publisher source.

PASS actual managed routes11/bundled Chrome8, live3Linux peers11, fullRooms UI17/36reopens, real coordinator SIGSTOP live3Linux13 (signed chat commits/server fallback while stopped; resume ->fresh RTC), all10sites. Live SDK rollback to b97 and fresh recovered-message read4, reupgrade+active+verify PASS, no data/floor restore. First forward wrapper failed parsing controller log+JSON output AFTER prepare had passed; authoritative prepare receipt reconciled, no blind retry; fixed wrapper selects typed final summary. Retained failure receipt. Private coordinator same3786297/3786303, static boot policy unchanged.

R730 new runner87 SHAe3b222eccde1fedd95c0cc4bbb77e3a5380cb29bd7ef369f7187f048acc175d7 backed in reader-coordinator-load-r1. Actual16agents/1Chrome/0v86 PASS20, driver stopped. Actual128/4Chrome/0v86 admission99.649s/connectivity/RTC state all passed, then FAIL during first8message burst: Hosted head scope changed. All128 cleanup/fixture removal, driver stopped. No active load job now. Not a claimed capacity limit/pass. Root cause reproduced exactly by real signed Chrome regression with logical149s->151s clock boundary: join bootstrap then split snapshot can span lease renewal despite atomicSync=true.

RAW FIX + sealed candidate b3c292a13b6a7c1d69f15d9c23c27a15d58009646ae030e1a7806607abcbb897 in .build/releases/connected-reader-coordinator-r2, NOT DEPLOYED yet: provided join/create state now uses atomic sync too; valid same-author/same-permission stale grant requests fresh membership once, older grant never installed/no create/accept replay/no weakened signatures/authority checks. Deterministic red2 before, green9 after incl signed foreign-author grant refusal, exactly-once writes and zero leases; existing actual atomic adversarial browser9 PASS. Next freeze/publish SDK-only correction, real128 rerun, then512/2048->8k, finish retention/full ledger/handoff. Root4 expires2026-10-26T10:26:06Z; explicit renewal only. Moonpie still offline LastSeen15:40UTC, owned old fixture cleanup pending. Full goal ACTIVE.


## Live chat explicitly disabled; test content deleted — 2026-10-25 UTC

LATEST USER POLICY overrides all earlier live-chat descriptions: Chat and Rooms
stay DISABLED until the new device-owned history/network system works. Users
must explicitly accept persistent storage and actually receive the browser grant
before chat or other local-history-dependent features are enabled. That consent
gate is still required, NOT implemented by this pause. Content belongs on
participating devices; server history requires explicit supernode opt-in.
Always-on supernodes/raised limits and CDN remain deferred. Never automatically
reopen the old hosted chat or restore its deleted database.

CURRENT root SDK6ded1364d04182b48d3fc8b65f6d1dd24a5d322d3cf91b1dda853d05794e1bf9,
298files/57native unchanged, only Chat+Rooms app bundles changed plus network
initialization pause. Both apps show an unavailable notice; network initialize
returns before allocating a pool/history stores/timers. Native hostedRooms
binding removed through configure-hosted-rooms --disable. Saved-chat, reader
coordinator and their proxies/sockets plus reader refresh timer STOPPED. Static
boot policy unchanged. Managed codi_chat_disabled=true blocks /rooms[/...],
/api/v1/room-control/* and /rendezvous with503. Fresh browser alone cannot erase
already received/cached copies on other devices; no such claim is made.

User-authorized SQL deletion:117events,33rooms,46streams,40leases,33members,
0work -> allzero. secure_delete plus VACUUM; no chat backup created. Controller
key and metadata clock floor retained. No account, permissions, private document,
other service or supplied baseline deletion. Root deletion receipt:
/srv/codi-connected/chat-disabled-delete-1792959319258505062-result.json.
Successful activation /srv/codi-connected/chat-paused-activation-1792959734539433929-result.json
SHAafcfa5d8ac8c58c4b6cf232a98d17a15d69bf8ddf0e70dc55cd57aa1eb77ba46.

First activation changed hosting but native readiness refused the deliberately
stopped room service, leaving code rollback journal. Failure receipt retained as
chat-paused-activation-before-result.json and browser-before live-r1. Recovered
existing code journal using the EMPTY private worker temporarily running behind
503; disabled native room binding, stopped worker, resumed SDK upgrade. No room
content restored and no public chat reopened. Recovery source/proof in private
box-git mainc0468610763f4cc07959864be242b0c3bff1985e, packets chat-paused-r1
and chat-paused-recovery-r1. Root resume publisher SHAcd12f439efe8554f4bf41cc00c721f5d39fdec6e656caa3fcb7a924a179e67d6.

Native configSHAd2446e778ab57c2644ceff3c9776e224d1a124a5960bbb7647df3e6525e092d9.
Hosting generator9f7fef18df198f783b71d13da1950272edc8518f8726700ab01e18ff299acd4a,
manifest35bd536bf8933f70a52efbb5ff4bbafbae737568b0fac16b60aba565187fd776,
derived Caddy5e76e178c0a54dd43c7a240781d57ae4fcbc9f2f66c5e288e96b5173c553b3bb.
Use managed controller/pins/generated validation/apply, never hand-edit Caddy.
Previous SDK952 remains available as development base; DO NOT use an old SDK or
hosting rollback to reactivate chat before the user's replacement conditions.
No new ports/router/firewall/primary-root mint. Root4/fence4 still expires
2026-10-26T10:26:06Z, renewal explicit. Accounts/files/keys/root/blog preserved.

Actual ordinary-TLS public Chrome PASS14: real Linux boots,24Chat/Rooms opens+
closes only show notice, no chat pools/history allocations/requests, Calculator
and Text work. All10production sites PASS;133prototype files checked exact.
Receipts active-system/.build/checks/chat-paused-{deletion-r1,activation-r2,
live-r2,final-health-r1,final-smoke-r1}-result.json. Owned browser closed.
Generated intermediate connected-chat-paused-apps-r1 removed (~86.6MB). Older
952/b3/5ac expanded runtime copies still require final current+one retention
review; no unverified deletion performed here.

Independent bridge-fixed R730 job island-512-r2 now TERMINAL PASS20:512actual
signed browser agents/16Chrome/0v86, independent production-class coordinator
and Caddy, six8message bursts and120s steady samples, total969.463s. All owned
leases/IndexedDB/fixture/driver closed. Receipts reader-island-r730-512-r2-
{result,job}.json. Earlier b3 512failed with healthy degree4..6 but components
496/11/5; bounded global60s bridge probes in952 pass controlled16-agent real
split/heal red-before/green23 and this fresh512. This is not8k/public capacity,
replica quorum or current outside-WAN proof. 2048/8k, independent replica
convergence, durable chess, storage-consent history replacement, final audit and
Moonpie outside test/owned-fixture reconciliation remain unfinished. Full goal
stays ACTIVE; live chat stays disabled throughout its development.

Final pause proof backed up to box-git main ee85ba2369859b9a8dd9970e301e17def39e9bb6 (chat-paused-proof-r1,12 files, manifest5e5ca05668cc9d762c1d585fce4b763ad596a3e9b7b9fbfba41769ae7d1c805d). Editable webhost source remains deployed recovery commitc046861; proof-only push does not change runtime.


## Device history components PASS31;2048 fixture running; code retention — 2026-10-25 UTC

Previous goal turn was PROGRESS (live chat disabled/test content deleted). This
turn adds concrete SOURCE-ONLY device-storage implementation while preserving
that pause. Live SDK6ded/configd244 and managed chat503 pins remain unchanged;
saved-chat/coordinator/timer inactive, server event count0 verified after cleanup.

New assets/desktop/storage-consent.mjs requires explicit UI acceptance AND an
actual native persistence grant. No prompt/marker/history DB before acceptance;
refusal/unsupported browser stays gated. Local capability checks are NOT server
authorization or a same-origin app sandbox. Closing a view/account, withdrawing
consent in another tab or losing native permission prevents stale work.
New assets/desktop/channel-journal.mjs stores complete signed proof packets per
account/channel with SHA256 corruption checks, canonical monotonic floors,
strict IDB write durability, atomic prior-hash CAS, explicit delete hash and
configurable disk quotas. Its caller MUST provide the full protocol signature,
authorization/ancestry verifier. It is NOT a new consensus/finality protocol or
complete all-history/chunk archive. Proof calls are bounded10s and abort racing
rejects immediately even if the verifier has not settled; no late commit.

Actual owned loopback Chrome PASS31 in device-history-browser-r8-result.json:
2sequential browser launches/1maximum concurrent/2tabs/0v86, real WebCrypto
signatures, real IndexedDB and trusted clicks. Native persistence grant/denial
is explicitly CDP-controlled, not a physical Android permission-popup test.
Tests include refusal/unsupported, forged capability/scope/signature rejection,
competing saves, stale rollback/delete, idempotence, quotas, corruption refusal,
account-close during held proof, reload, cross-tab withdrawal/reconsent and
exact-owned Chrome main-process SIGKILL followed by profile restart. Committed
signed IDB content survives that browser crash. BOTH application consent marker
and test-native permission were absent after the crash: the gate required fresh
acceptance and a current native grant before opening retained history. Do NOT
claim consent/grant survives SIGKILL, arbitrary OS/power failure, browser data
clearing, or device loss. Explicit site-data clearing removes history and consent
without secret server recovery. All owned browsers/profiles/HTTP fixture removed.
Initial test-size argument bug, no matching owned PID and wrong assumption that
permission survives restart are retained in r1/r4/r5 receipts. Final r8 also
states launch/concurrency counts precisely. No physical phone or full protocol
claim; no deployment of these components yet. Generic host wiring, persistent
controller-key custody, peer-owned durable authority/replica history and chess
integration remain REQUIRED before live chat can reopen.

Source/proof backed up as private box-git maina6381a09d05986a684207ebb90bc2cbffad08860,
packet device-history-r1,15files, manifest0753be7f1dd2f3f45d703da720ef7197599b3ca937acd0488da362d78fe03585.
Later r8 test count correction/latest receipt recorded separately. This source
pull on webhost does not deploy or change running native/public files.

Verified root pruner removed ONLY installed native25-b3c292a13b6a7c1d and
native25-5ac541f0e439dc08 after complete hashes/custody and /proc/unit references;
173136001code bytes. Root receipt /srv/codi-connected/paused-code-retention-1792961381954466829-result.json
SHAf67743d8fb18f6bf38fe7af00eec1b8175c1e66fbe657ce23b0e348752a55fdc.
Matching two local expanded runtime copies removed, another173136001bytes.
Old lease-fix/rollout packet sparse expansions removed on local+webhost clones;
Git history preserved. Current paused6ded and development base952 kept.952 is
NOT a permitted live-chat rollback. No private DB/keys/accounts/documents/floors
removed or restored, no units restarted by cleanup. Source pruner protected at
/srv/codi-connected/paused-code-retention/c32b90ba582a788f8b0cea37e3f7a01b3e0a9118ca5b410ab1d4efd7d5d4e408/.

CURRENT ACTIVE LOAD JOB: tool exec35585, R730
/home/dflanag3/codi-load-tests/runs/island-2048-r1. Supervisor2185540 start60444659,
runner2185548 start60444699, driver2185541 start60444695, bootID2fb2b1fe-8bf3-4ac8-9efb-e63bf2b8b0e3,
driverhttp://127.0.0.1:52643. Exact immutable island-952fe21d-752026ff artifact,
runnerSHA752026ff44bb14e8f0ce5a7690c2fabe27831eff191a49674f4840df3571f7d4,
64Chrome/2048signed SDK agents/0v86,120s steady target.1217admitted last tool
observation; actual runner /proc start verified live, available225578332KiB.
No terminal result yet. Poll SAME handle; never restart after a wait timeout.
Prior512 PASS20 is terminal and separate. This remains the historical hosted
protocol fixture, not proof of the new device-owned authority/storage integration
or8k global capacity. Moonpie remains offline LastSeen15:40UTC; outside retest
and its old owned browser-fixture reconciliation pending. Root4 expiry remains
2026-10-26T10:26:06Z; renewal explicit. Full goal ACTIVE, live chat stays OFF.

Final device-history proof: private box-git main65b8d93bf24207d33fb4d9e7c23652c5385a492f; device-history-proof-r2,8files, manifest1bc6460eda71967ac978ee1859783e9ad4680e899de516cdb3eb7445a4689745. Live webhost checkouta638 is source-only, current SDK6ded remains paused. Tool35585 still live on last poll; no terminal2048 result yet.


## Shared device-history host live; chat stays paused;2048 terminal failure — 2026-10-25 UTC

This entry supersedes the preceding source-only/2048-running state. Full goal
remains ACTIVE. Latest turn is PROGRESS, not complete: generic shared storage
integration, live forward/rollback/re-upgrade, and a terminal scale result.

CURRENT live SDK native25/9f86587c8590eed2c34bbf3eede2efb109fe0a8401328551a00092f19e3b9fe9,
300files, /srv/codi-connected/releases/native25-9f86587c8590eed2.
Native config SHAfa0310759ed058504e1513d878d4383b75406586c2eaabee6f4f2ef7a8881226.
Usable code rollback is PAUSED6ded1364d04182b48d3fc8b65f6d1dd24a5d322d3cf91b1dda853d05794e1bf9.
Do not reactivate older952/hosted-chat code or restore deleted chat data.
Native57files, network40modules and existing7app bundles22files are unchanged.
Issuer/steward/guest run; bootstrap stopped. Accounts/keys/cookie/realm/private
files/permissions and usage floors preserved across each actual transition;
file-service PIDs unchanged. No Caddy/ports/router/firewall/boot-policy change.
Root4/fence4 still expires2026-10-26T10:26:06Z; renewal explicit, no root mint.

Chat and Rooms STILL show only unavailable notices. Native hostedRooms binding
absent, saved-chat/coordinator services and refresh timer inactive. Managed
codi_chat_disabled=true and all public room/control/rendezvous routes503 remain.
Server events0; previous117messages/33rooms deletion is preserved, no chat backup
created. /blog/ and all133/desktop prototype files and all10sites verified.
Hosting pins remain generator9f7fef18df198f783b71d13da1950272edc8518f8726700ab01e18ff299acd4a,
sites35bd536bf8933f70a52efbb5ff4bbafbae737568b0fac16b60aba565187fd776,
Caddy5e76e178c0a54dd43c7a240781d57ae4fcbc9f2f66c5e288e96b5173c553b3bb.
Use managed hosting lock/pins/generation; never edit derived Caddy.

DeviceHistoryHost now supplies optional host.storage.deviceHistory only inside
a consented history-dependent API2 child view. Explicit app acceptance AND actual
native persistent-storage grant precede child mounting, room decoration,
network startup or journal opening. Stable issuer/account-sub scope (separate
anonymous-device scope), view-owned IDB, cancellation and withdrawal checks.
Normal apps remain independent. Paused notices bypass the gate entirely, so no
consent prompt, store or pool starts on current live. Generic compiler supports
explicit shared-service entries using existing dependency handling and a hashed
registry; no new app, framework or server-side JS runtime introduced.

Compiled helper bytes SHAaa4ee6eea7fb1bb455cb42f09056f6d423899768ae7f911dffcd38c774efcdfa
are served at assets/desktop/services/device-history/ee37fbbcbc0d8e86a203ce3f476991c612535fe91385d98924dd6c43ff67d1bf/index.mjs.
Ordinary-TLS fetch matches; this fetch does not execute or approve the gate.
Components PASS31, compiled host PASS24 including30reopens and actual native
resource baseline, compiler regression PASS29. Underlying native grant/denial is
CDP-controlled; no physical Android permission/power-loss claim. Signed IDB
content survives exact-owned Chrome SIGKILL, but marker/native permission were
absent after that crash: fresh acceptance/grant required. Journal requires a
trusted full protocol verifier; hashes are not authorization or finality.
No persistent controller-key vault, new consensus or full history archive yet.

Pre-activation review caught a room-extension mount outside the gate. Controlled
old-source red2 retained, fixed source22/compiled24 pass including failed
extension cleanup/retry. Superseded c0cf candidate was NEVER installed as native
SDK or activated. Actual final300file build independently reproduced; sealed SDK
browser PASS5 includes all7apps/21opens, real v86 guest document save and two
independent shell sessions/nano. All owned browsers/fixtures cleaned.

Git-first source44ea385eda7225ea1e1014b1d4d310ac16047c7d, private box-git packet
tools/codiserver/device-history-host-r2, source-proof703548d85ead9e8664d58ff6350ca9af4fc9fc64e75cabe77d9d4e4add98dfb6.
Protected publisher29145bfdc3f7b6f4915d9ab11ec07848d748695d920295577faf25accde64b05
under /srv/codi-connected/device-history-host-publishers/<SHA>/.
Actual stage/activate/verify PASS, public paused14 PASS; rollback to6ded/verify
PASS and fresh rollback browser14 PASS; re-upgrade to9f/verify PASS and fresh
final browser14 PASS. Honest10second maintenance countdown before state capture;
no old private state restored. Receipts under active-system/.build/checks:
device-history-live-{forward-r1,paused-r1,rollback-r1,rollback-browser-r1,
reupgrade-r1,final-browser-r1,final-health-r1,final-smoke-r1,service-r1}-result.json.
The reused paused-browser fixture has historical storageConsentGateImplemented:
false metadata; its actual scope is paused notices, not the separately tested
compiled gate. No new live chat/peer-authority acceptance is inferred.

R730 island-2048-r1 is TERMINAL FAIL after1244admissions,64actualChrome/
2048logical signed agents/0v86,2017.991s and2early checks. Ordinary room/auth
atomic sync returned Server is busy; room transport-rate429, coordinator busy429
and downstream503/502 observed. This is not a hard participant ceiling or a
single-cause diagnosis. Historical SDK952/R4 fixture only, not the replacement
protocol. All2048tracked allocation counters zero, temporary fixture removed,
owned driver stopped, source unchanged; tool35585 terminal, do not repoll/restart.
Result gzipSHA5d8b079a1a9209d9ee381d9178c1523da33a4ede8b454d9a8ffa67f33b336924,
rawSHA2804dad1f7569547e2e43e74070181d0fb49f2cc34ad3c09bc1fb01b543c6407.
Compact summary and full gzip retained in private Git host-r1 packet.512PASS20
remains valid for its earlier isolated scope. No8k/current outside-WAN pass.

Next: implement participant-owned durable channel controller-key/authority and
replica history/recovery using shared services, then legal durable chess,
staged actual transports through8k and audit. Do not merely raise old central
service limits. Origin content remains forbidden unless operator opts into a
supernode; dedicated supernodes/raised limits and CDN remain deferred. Chat
stays disabled until replacement works. Moonpie outside retest and exact old
owned-browser reconciliation remain pending; last observed offline15:40UTC.

Final aggregate device-history-live-milestone-r1-result.json PASS binds exact
component31/compiled24/compiler29/sealedSDK5 and live forward/rollback/re-upgrade,
public paused14, final all10-site/prototype133 and disabled-chat health receipts.
Local retention verified full manifests before removing four generated SDK
intermediates346426587bytes and redundant raw2048receipt61916506bytes; compressed
full evidence and its private Git copy match, current9f/paused6ded retained.
No private state or remote code removed. Retention receipt:
device-history-local-retention-r1-result.json. Final proof/doc backup packet is
tools/codiserver/device-history-host-live-proof-r1 on private box-git main;
source-proof.json binds every included file. It is proof-only, not a deploy.


## Durable channel keys: source/compiled foundation PASS, not deployed — 2026-10-25 UTC

Previous goal turn was PROGRESS (shared host live, real2048 terminal result,
private Git proof651c2fa). This turn implements actual persistent channel-key
custody through the shared host. Full goal ACTIVE; Chat/Rooms remain disabled.
Live native25/9f86587c and paused rollback6ded are unchanged. Read-only pinned
publisher verify passes in device-channel-keys-live-unchanged-r1-result.json;
no native/Caddy/service/port/root/boot changes or private state modifications.

New assets/desktop/channel-keys.mjs stores nonextractable native P-256
CryptoKeys by structured clone in codi-device-channel-keys-v1, strict IDB write
transactions,4096global/128per-account default key bounds (configurable down).
Self-certifying channel address binds its public key. Signed genesis is fully
verified BEFORE committing; invalid encodings cannot strand unreadable keys.
Private/public match checked by actual random Web Crypto custody challenge.
get/list return only public metadata; fixed-purpose signing never exports keys
or mints issuer/login tokens. Account scope is supplied by DeviceHistoryHost's
optional openKeys facade, owned by the actual API2 child view. View close,
account change, withdrawal/native denial and pending crypto cancellation refuse
stale operations. Exact-genesis removal; no silent key recreation/replacement.
A lost post-commit response requires listing retained keys before retrying.

This is key continuity, NOT channel policy, registered ownership attestation,
membership authorization, accepted-branch ancestry or replica consensus. Signed
proofs require a pinned expected channel and purpose. Same-origin trusted code
is not sandboxed; native nonextractability does not promise encryption/hardware
protection. Device loss or cleared site data can destroy the key permanently.
No cross-device key recovery/export/server backup is claimed. Future replica
history recovery does not recover a lost private signing key by itself.

Real Chrome component receipt device-channel-keys-r4-result.json PASS28:
actual signatures/native key clone+export refusal, denial/forged permit,
account isolation, quota races, corrupt/private-key substitution refusal,
invalid Unicode/oversized/deep proof refusal, cancellation during real keygen,
held sign invalidated by deletion, reload, exact-owned main-process SIGKILL and
same key signing after restart/fresh explicit consent/native grant.2sequential
launches/1maximum concurrent browser/0v86/0peers. CDP controls native grant/denial;
no physical Android/power-loss proof. Both marker/native grant absent aftercrash;
fresh acceptance was required. All owned profiles/browsers/HTTP fixtures removed.
First r1 FAIL19 retained: Chromium rewrites argv into one flattened segment,
so test could not locate its process. Corrected harness pins its own WebDriver
reported PID, exact profile option, executable and /proc start ticks before
SIGKILL; no product workaround. r2/r3 earlier passes retain their source scopes.

Actual shared loader/API2 source29 and final compiled29 pass, including scoped
key creation/signing, fresh login same-sub continuity, wrong-account refusal,
closed facade refusal and30reopens returning native timers/listeners/workers/
requests to exact warm baseline. Final device-channel-keys-host-bundled-r3-result.json.
No actual peer links in these tests; network initialization tests use actual
pool/room/budget classes with only operator pause changed in an owned fixture.

Packaging reuses existing esbuild compiler. Explicit public-input JS files may
be declared individually, never as broader directory roots; their transitive
imports still need separate approval. No per-app special loader/import runtime.
Shared service build requires exact network/crypto.mjs and strict-json.mjs
inputs. Original source-boundary refusal observed before declaring them.
New boundary9checks pass, including unapproved transitive/sibling/private
inputs and symlink/directory refusal. Existing generic actual Chrome build29
(xterm/npm, CSS/assets/lazy modules/workers/lifecycle/root+submount) passes.

Final helper .build/shared-services/device-channel-keys-r3,
shared-service manifestab2d68a9f2e58de0f575873a6e9109963180f540ef548cd3deef1eda113b94e0,
compiled code13ab537f4ad164294d2cdbfbb7256e47474254f88f962fd6e069ed24cca5a25a,
bundle namespace1e7b8ed18aaf83d9886a25f4b95cc0168b5441ada3c7822500cc78097712fd88.
No new native SDK created or deployed. Superseded two tiny generated helper
bundles removed after hash/manifest verification; current candidate retained.
Aggregate device-channel-keys-milestone-r1-result.json PASS binds28/29/9/29;
not a whole-goal pass. New source/proof packet device-channel-keys-r1 is backed
up to private box-git main; no keys/account data in that source packet.

Next implement long-lived channel policy/permissions and authoritative
acceptance/peer-held checkpoints through this key/history service, then full
replica/chunk/conflict/durable chess integration and staged actual8k. Always
reject invalid branches; key signatures alone do not satisfy that requirement.
Live chat stays OFF until replacement is verified. Historical512PASS/2048FAIL
1244, no active load job; fresh Moonpie WAN proof remains unfinished. Root4
expires2026-10-26T10:26:06Z, renewal explicit. /desktop stays unchanged.


## Participant-owned permission/acceptance proofs PASS46; not live consensus — 2026-10-25 UTC

Previous turn PROGRESS: source/compiled durable keys28/host29 backed to private
box-git main89998df. This turn implements actual permission/accepted-checkpoint
verification and real strict-IDB save/reload, not just a plan. Full goal ACTIVE.
LIVE native25/9f86587c and paused rollback6ded remain unchanged. Chat/Rooms OFF,
server events0, no native room binding; read-only protected publisher verify
PASS in device-channel-state-live-unchanged-r1-result.json. No services/Caddy/
ports/router/firewall/boot/root/private-state changes. Webhost source still44ea;
new source backup is not a native/public deployment. Root4 expires
2026-10-26T10:26:06Z, renewal explicit. /blog and /desktop unchanged.

New network/device-channel-state.mjs pins BOTH controller channel ID and policy
content hash. Policy separates chat and chess channels and configures validator
keys; quorum is n-floor((n-1)/3), with unique authorized prepare AND commit
signatures binding phase, round and exact header.4keys require3 per phase;
solo1/1 explicitly has0fault tolerance. This is a certificate verifier, NOT a
running BFT engine: durable replica vote/lock state, view change, failover and
joint membership reconfiguration remain REQUIRED before automatic voting or
chat enablement. Tests manually sign with independent native keys in one
browser, not independent fault domains or a network consensus execution. A
fixture intentionally signs two competing branches solely to prove retained-
floor refusal; it is not a Byzantine consensus safety/liveness test.

Original proposal signatures/IDs remain unchanged during reinclusion. Current
write permission, exact author sequence/previous ID and permission revision are
rechecked through a separate fresh authorization. Root-only permission changes
are replayed in accepted order. New network/device-operation-set.mjs verifies
compressed sparse SHA256 nonmembership paths to reject an already accepted
original ID even when given fresh authorization. Verifier memory is one256level
path, not all past IDs. Native Web Crypto hashes/signatures; no custom curve
math. Production sparse witness generation and durable peer-held node graph
are still unimplemented. The small fixture uses an explicitly test-only full-
level oracle; never ship that oracle as an8k in-memory history provider.

State transitions replay operation permissions, replay protection and legal
canonical SAN/player turn/position binding before accepting a certificate.
Separate chess/chat IDs; spectators cannot move. Current snapshots keep64recent
chat messages, at most16384author floors/permission overrides and32signed header
links, with2MiBblock/8MiBcheckpoint byte bounds. These are implementation/storage
allowances, not participant capacity evidence or a complete archive. Lost older
history/original signatures need durable immutable block chunks and a pending
outbox, both still REQUIRED. Chess replays its bounded2048ply move list to
restore board/repetition state; true no-replay chess fast-forward is not done.

Checkpoint imports explicitly report proofScope=quorum-attested-snapshot and
historical=true; full transitions report replayed-transition-and-quorum-certificate.
Quorum snapshot attestation does not mean all omitted transitions were locally
replayed or that this is the latest peer head. A known saved floor requires a
signed linked ancestry path, not merely a higher count. Bounded header trail is
preserved across durable page reloads so a restarted sender can update an older
peer. Gaps older than32links fail honestly and need older verified chunks.
Actual journal CAS rejects an unlinked higher snapshot without replacing data.

Actual ordinary loopback Chrome source r4 PASS46, final compiled helper PASS46:
policy/grant/ban/unban; missing/duplicate/outsider/cross-phase votes; valid quorum
cannot bypass transition permissions; original-ID reinclusion/replay refusal;
extreme sparse paths/noncanonical/stale witnesses; input copy before async work;
known-floor authenticated fork refusal; strict-IDB checkpoint save/reload and
older-peer recovery; simulated15day clock gap; distinct legal chess/PGN and solo
notes.1Chrome/0v86/0RTC links, actual native keys/signatures/IDB and trusted storage
click, CDP native grant. No physical phone, real15day wait,8k or WAN claim. All
owned browser/HTTP fixtures closed. Runner binds the actual served source
snapshot and refuses a current-source mismatch. Historical r1/r2 passes retain
their source scopes; r3 FAIL27 retained for expected fork-refusal wording
('ancestry' versus 'ancestor'), corrected assertion then clean r4 pass.

Proof codec uses existing generic dependency compiler and exactly declared shared
inputs; no new menu app, framework or runtime Node. Internal channel-proof
catalog is not merged into the seven apps. Two-file bundle includes MIT notice;
codeSHA4abd9fe0b949c37a0f2ef8f8adcb0113351fec9e2078858ded8bf0d50cfb0244,
catalogSHAede4dbc03c33b5d690a4ecc01ca0ff90ab3d7df869dddf2a88c33e1142813636,
namespacec607b790b7cfd26ddb3b61f980e6bb0b3305a3fbb4d62c00ab1b002be149c456.
Independent build exactly matches; duplicate expanded helper removed. Retained
artifact active-system/.build/shared-services/device-channel-protocol-r1.
Receipts device-channel-state-{r1,r2,r3,r4,bundled-r1,build-r1,
live-unchanged-r1,milestone-r1}-result.json under active-system/.build/checks.
New source/proof packet device-channel-state-r1 is backed to private box-git main;
no generated native SDK or source pull/deployment this turn.

NEXT: durable replica vote/lock/view-change and membership safety; durable
pending original-proposal outbox plus immutable history/sparse witness graph;
shared app-host/real peer transport integration and fault/partition/churn tests.
Then full archive/chunk resume, correspondence chess/UI, actual staged8k, fresh
Moonpie WAN and full audit. Existing historical512PASS/2048FAIL1244 remain scoped
baseline results; no load job running. Supernodes/raised limits and CDN stay
deferred by user direction. Origin stores no chat content unless explicitly
opted into a history supernode. Keep live chat disabled until replacement works.


Final pre-voting-engine correction: logical accepted head excludes retry round;
replica votes continue to bind the full round-specific header. This prevents
reproposing the SAME prepared value in another view from falsely changing its
history ID, while old-round votes cannot certify the new view. Fresh quorum
certificate for the same value retains the accepted floor. Three real-signature
regressions added; final compiled device-channel-state-bundled-r3 PASS49,
source-unchanged binding and closed browser/fixture. Milestone-r2 binds this.
Final code7b0b5e3d2eec49ccb36cb5b32b645892da45f35872bdc237dbdde4f7985898c6,
catalog28ba9e76ceb98cbb8a6b556e61128d35ce8abe566d55a6270bcc30703faf5a89,
artifact .build/shared-services/device-channel-protocol-r3; exact independent
rebuild passes. Earlier46/48 receipts/code8c5ebc6 keep historical source scopes;
none deployed. Private Git device-channel-state-r1 packet updated with final
source/artifact/proofs. All running site/chat pause pins remain unchanged.


## Durable fixed-membership replica core PASS27; source only — 2026-10-25 UTC

Previous turn PROGRESS: source permission/checkpoint49 backed to private box-git
main6779eba. This turn adds actual commit-before-publication replica execution,
not manual certificate assembly alone. Full goal ACTIVE. LIVE SDK9f86587c and
paused6ded rollback unchanged; Chat/Rooms OFF, service endpoints503, server
messages0, no hostedRooms binding. Read-only protected publisher verify PASS in
device-replica-live-unchanged-r1-result.json. Webhost checkout remains44ea;
source backup does not deploy. No native/Caddy/service/root/ports/boot changes.
Root4/fence4 expiry2026-10-26T10:26:06Z remains; renewal explicit. Blog and133
prototype files retain their earlier live proof; no UI/prototype edits here.

New assets/desktop/device-key-database.mjs upgrades only the browser key DB to
schema2, adding replicaStates/accounting and per-key journal fences. Key bytes,
public ID/genesis and ordinary signing survive schema1 migration, but migrated
keys become voter-ineligible: earlier manual signatures cannot prove an empty
vote history. New keys are eligible. Never reset a surviving key's missing
voter records/fence; fail closed and retire it through authorized membership
recovery. This is not protection against restoring an ENTIRE old browser profile
or malicious same-origin code controlling the key. No hardware/power-loss claim.
No real visitor database was migrated; all new-schema tests use owned profiles.

New assets/desktop/replica-journal.mjs commits the signed immutable state,
generation/hash fence on its key and accounting in ONE strict native IDB
transaction. Crypto/verification precede that transaction. CAS guards competing
instances/tabs; no vote leaves DeviceReplica until commit and current-lifecycle
checks finish. Own generated state attestation is verified before saving.
Default logical disk allowances32MiBrecord/128MiBtotal,1024records/128per account;
128bindings per key; configurable within bounds, no preallocated RAM. Small
per-record limits do not reject unrelated larger existing channel records.
Missing/corrupt state refuses silently reenrolling the old signer.

New network/device-replica.mjs is a fixed-membership, one-slot event-driven core:
leader-authenticated proposal, one durable prepare per slot/view, matching
prepared quorum before durable commit, exact cached resend, signed view-change
quorum carrying the highest prepared value, stable history ID across rounds,
accepted checkpoint recovery and idempotence. It retains evidence on view
advance and clears it only after a verified accepted successor. One mutating
job per core instance; concurrent same-identity instances still use native CAS.
No automatic timers, retransmission, peer adapter, joint reconfiguration or full
network liveness/formal correctness claim. These remain REQUIRED, not deferred.
The new exported protocol proof helpers share existing codec/domain checks.

Actual compiled core device-replica-bundled-r3-result.json PASS27.2sequential
Chrome launches/1maximum concurrent/4logical replicas/0RTC/0v86. Actual owned
main-process SIGKILL after strict prepare commit and before controlled held
response publication; PID/exe/exact profile/start ticks pinned. Fresh consent/
native grant rechecked after restart; same key/fence/vote recovered and EXACT
signature resent without another generation. Native CDP controls storage grants,
not a physical Android decision. Competing tab copies release only one prepare.
One explicitly Byzantine leader envelope is generated outside the honest API;
actual durable cores converge, carry prepared state over a controlled leader
change and repair the absent replica. This is one-browser controlled delivery,
not four independent fault domains or an actual transport/liveness test.

Additional PASS: view-close AFTER commit blocks stale signature publication but
keeps recoverable promise; busy mutation refusal; actual native transaction
abort after key/record/accounting writes are queued releases no vote and leaves
generation/promise intact; quota refusal leaves other channels usable; deleting
vote row with key/fence retained refuses reuse; checksum corruption refuses;
legacy key migration retains ordinary signatures and denies unsafe enrollment.
Controlled destructive checks affect ONLY the temporary loopback profile and
end with its removal. All owned browsers/profiles/HTTP fixtures removed.

Regressions: key28 (device-replica-key-regression-r1), permission/checkpoint/legal
chess49 (protocol-regression-r1), shared host lifecycle29 (host-regression-r1),
including30reopen exact native timer/listener/worker/request warm baseline.
Aggregate device-replica-milestone-r1 binds these and read-only live health.
Initial source core21/earlier compiled25 receipts retain their exact scopes;
no product failure hidden. Final runner hashes served source and refuses any
source change during its execution. PBFT view-change background inspected from
https://static.usenix.org/publications/library/proceedings/osdi99/full_papers/castro/castro_html/node4.html;
this implementation is a bounded one-slot fixed-set adaptation, not a claim of
complete or formally verified PBFT deployment.

Single graph wrapper assets/desktop/replica-core.mjs ensures native storage
permits and consumers share one bundled WeakMap capability domain. Never pass
grants between separately bundled copies. Existing compiler builds its complete
graph with exact approved shared files; no menu entry/runtime Node/framework.
Final helper .build/shared-services/device-replica-r4,
code4179125e263fa9dc98147c4be5119e498b8be5539621c8bf0a7338d376681519,
catalog629daa6f579172794875217ee8824dcee0b95518e232fffab52f10ce73d86144.
Exact independent rebuild passes, MIT notice retained; duplicate expanded
build removed. Superseded tiny helper cleanup and source/proof backup are
recorded in private box-git packet device-replica-r1. No new native SDK built.

NEXT: durable pending original-proposal outbox and immutable peer-held
history/sparse witness node graph; integrate the core into shared account/
session ownership and actual peer transports; automatic timeouts/repair and
joint membership; adversarial scheduling/partitions/churn and staged8k. Then
full archive/chunk resume, correspondence chess/app UI, fresh Moonpie WAN and
full acceptance audit. Live chat stays OFF until replacement works. Historical
512PASS/2048FAIL1244 remain old hosted baseline scopes, no load job running.
Always-on supernodes/raised limits and CDN remain explicitly deferred.


Final recovery correction supersedes the initial core27 artifact: prepared
CERTIFICATES alone were retained on view advance, losing the corresponding
operation payload. The core now keeps the full certified operation records
until an accepted successor retires the slot, revalidates them on load, and
sends only the bounded certificate in view-change messages. A fresh reopened
replica supplies those exact records to the next leader. Final compiled
`device-replica-bundled-r5-result.json` PASS28; milestone-r2 is current.
The r4 FAIL22 is retained: prepared-value recovery passed, then a later fixture
quota assertion used an intentionally closed old leader handle. Corrected the
fixture to use its reopened actor handle, then clean r5 PASS28. Nothing was
deployed. Current helper .build/shared-services/device-replica-r6,
code2f5f4e2670aed076b01ddc257b90fef199792dff70059c756d12f6877a159dc5,
catalog4950b97e09092a06920297636a0128a42bc645eea33db65c40078d24cad25450.
Exact independent rebuild passes. Initial27/source1c49aec keeps its historical
scope only. Final source/artifact/proof update is in private Git packet
device-replica-r1; live9f/paused rollback6ded and all route/data pins unchanged.


## Device-owned queue/archive and production witness provider — 2026-10-26 UTC

Source-only progress, NOT deployed; full goal ACTIVE. Live native25/9f86587c,
paused rollback6ded, server checkout44ea and managed hosting pins are unchanged.
Fresh `device-archive-live-unchanged-r1-result.json` PASS verifies pause, empty
server test history, existing root/data/usage floors and release/config pins.
No route/native/private data/ports/boot changes. Root desktop and /blog remain
the existing deployment; /desktop stays separate. Never activate old952 chat.

New network/device-operation-tree.mjs produces real sparse absence witnesses
from a content-addressed compressed binary tree, loading one path rather than
all IDs. Verifies content/link hashes plus existing independent witness algebra.
Canonical insertion-order-independent roots; current index2N-1 nodes with
replaced branches removed atomically. No naive256 disk nodes per operation.
New assets/desktop/channel-archive.mjs retains exact original pending signatures,
full signed blocks split into8192-byte/fanout64 chunks, and latest checkpoint.
The actual channel protocol replays permissions/dependencies/legality and QCs.
One strict CAS transaction saves nodes/head/index, prunes replaced index branches
and acknowledges accepted queue entries. Failed staging writes no disk nodes.
Valid losing branch keeps exact original, then fresh authorization reincludes it
once. Accepted originals cannot be requeued; exact-hash cancellation available.
Archive-first/replica-second ordering retains full accepted payload if the later
replica step fails; verified checkpoint repair tested. Separate DBs, no cross-DB
atomicity claim; vote keys/fences untouched. Native storage consent/grant and
scope-bound author key required. No automatic server history or device backup.

Final compiled `device-archive-bundled-r2-result.json` PASS41; same final entry
`device-archive-replica-regression-r2-result.json` PASS28. Source-r4 PASS41.
Real Web Crypto/IDB/owned browser SIGKILL, native transaction abort, conflicting
head CAS, lost-original reinclusion, capacity refusal,68 complete blocks beyond
64-message snapshot window, multichunk block, corrupt/missing-node refusal and
30 opens/closes with zero native connection/operation-timer delta. Archive fixture
4logical identities,2sequential Chrome launches,0RTC/v86. First block uses real
replica core; later manual certificates test archive retention/CAS only. Not8k,
automatic liveness, independent fault domains or WAN proof. All owned fixtures/
profiles/browsers closed. Final metrics68 blocks/341content nodes/1046781actual
accounted bytes;1pending belongs to independent small-capacity test channel.

Single compiled helper .build/shared-services/device-archive-r5 includes protocol,
keys,consent,archive,replica in ONE WeakMap capability domain. Internal catalog,
not eighth app. Exact independent rebuild PASS, MIT notice retained; superseded
expanded tiny archive helpers hash-verified/pruned. No runtime Node/framework.
Compiled3bacab42f451cb0d7b0172a4e2be6e54161f08ba24797fcb1e0686b05e8775c3,
catalog340a096ed5ff32a32c4b8c35ebfe713f6b7bc5ac15be737d26c4277327746019.
Aggregate device-archive-milestone-r1 PASS binds final receipts; evidence/
device-channel-archive.md and requirement ledger record implementation/limits.
Early source-r1 FAIL retained: await in a non-async fixture callback prevented
page initialization; fixture corrected, no product workaround. Earlier29/38
checks/builds retain historical scopes only. Current source/artifact/proof is saved in
private Git packet tools/codiserver/device-archive-r1.

Archive defaults128MiB actual disk records/524288nodes/4096pending total/256per
channel, not RAM reservations. Separate journal budgets are NOT yet unified.
No remote chunk importer/resumable transfer, shared live app/session integration,
automatic timeout/retransmission/repair, joint membership or long-gap ancestry
proof beyond32header window yet. Explicit channel export/removal UI, no-replay
chess fast-forward, staged real8k and fresh Moonpie WAN remain. Archive local
readNode is not a remote permission grant. Keep Chat/Rooms OFF. Next: shared
session ownership and authenticated bounded peer graph transfer/repair, then
required fault/scale/WAN/full audit. Supernodes/raised limits/CDN deferred.


## Actual peer-owned chunk transfer — 2026-10-26 UTC

Full goal ACTIVE; source/compiled progress, NOT deployed. Live native25/9f86587c
and paused rollback6ded/source checkout44ea unchanged. Fresh read-only
`device-peer-live-unchanged-r1-result.json` PASS verifies runtime/config/hosting
pins, old history empty and paused, authority/usage/account/file floors retained.
No route/root/blog/prototype/native/private data/port/boot change. Do not reopen
Chat/Rooms or activate old952 hosted chat. User approves additional browser JS
layers and underlying client software if required; this path still needs only
ordinary Chrome, no extension or visitor process/runtime.

New explicitly negotiated PeerLink/PeerPool codi-device content capability uses
existing authenticated RTC, replay floors and scheduler. DevicePeerSync requires
controller-signed channel/genesis/transport-key-bound short read grant before
provider reads any node. Wrong-key/expired/ungranted raw requests refused. No
server folder/key/account grant. Default600/max3600second grants require owner
for a fresh reader key; finished long-lived/revocable membership/offline delegation
is still required. No implicit read permission from a valid RTC handshake.

Typed hash-checked DAG nodes, bounded open/get/data RPC with nonce/peer/channel/
node correlation; pending-send deadline and late-response isolation. Explicit
usesSession/resourceBudget bridge charges the EXISTING pool budget even across
separately imported module graphs (never a second WeakMap budget).4shared repair
jobs,64KiB service/per-active-job accounting, grant64/rate24 bounded tables.
Legacy peer without capability stays ordinary and cannot acquire content mode.

New DeviceChannelDownloadCache: consent/native persistence, strict scoped scratch
IDB;8MiB/job16MiB total4jobs4096nodes default, actual disk accounting not RAM
reservation. Hash-valid unaccepted bytes are labeled incomplete. DeviceChannelTransfer
reuses actual durable chunks after main browser SIGKILL, loads bounded history
locators to retained floor and replays one full2MiB block at a time through the
existing archive. Checks locator logical head BEFORE acceptance. Correct hashes
around invalid authorization do not bypass replay. Prefix remains valid on a
later failure; no floor reset. Scratch chunks/job removed after accepted storage.
Default256-gap/configurable1..1024; larger gap honestly requires checkpoint
segments. Efficient long-gap/no-replay fast-forward is NOT finished.

Final `device-peer-transfer-bundled-r4-result.json` PASS35/14.487s:2isolated Chrome
profiles,3launches/max2concurrent,4actual RTC connections over run,1solo channel
validator(f0),0v86. Native host ICE/manual signed WebDriver signaling/default
localhost trust, no history/identity backend. Reader killed after6strict partial
nodes; fresh consent/key/read grant resumes, requests NONE of those6again. Real
provider checks no reads before permission; corrupt and invalid signed history
refused; capacity/timeouts/pending-send timeout/view-close/late bytes/link loss
recover to9accepted blocks. Ordinary messages stay usable.30service reopens
return warm budget; separate module graph receives actual pool charges. Final
owner cleanup all tracked network charges0/both browsers and profiles removed.
Actual provider frame max15609/reader1970 bytes, not a bandwidth estimate.

Same final compiled entry archive regression41 and replica regression28 PASS
(`device-peer-archive-regression-r3`/`device-peer-replica-regression-r3`). Separate
regression profiles/actors are NOT extra channel participants. Aggregate
`device-peer-milestone-r1-result.json` binds final proofs. Earlier21/29/32/33
checks retain narrower scopes. Current helper .build/shared-services/device-peer-r5,
code8731e98bc07bfd5602bdfcf65f1d1ad882222f48f97bc353922b52f4dd164746,
catalogc3ea640592c01fe3039f65c6051829f60653310bab983653121f510091534aba.
Exact independent generic build, MIT retained, expanded duplicates and obsolete
peer intermediates hash-verified/pruned. No native SDK/public catalog update.
Source/artifact/proof saved in private Git packet tools/codiserver/device-peer-r1.
See evidence/device-peer-transfer.md and current requirement ledger.

Moonpie freshly offline, LastSeen2026-10-25T15:40:00.1Z; no new WAN proof or
outside load job. Old Moonpie driver/profile cleanup still needs reconciliation
when online; do not guess/restart those old handles. Historical512PASS/2048FAIL
1244admissions remain old hosted baseline, no current8k proof/load job.

NEXT: shared desktop account/session ownership and app views for archive/core/
transfer; long-gap ancestry/checkpoints and durable/revocable read membership;
real remote proposal/vote exchange, automatic mesh repair/timeouts/retransmission,
joint membership, adversarial schedules/partitions/churn and bounded fallback/
return-to-P2P; staged8k, fresh outsideWAN and full goal audit. Not current public
TLS/TURN, independent-WAN, multi-replica network consensus or automated liveness
proof. Storage is not OS/power/device-loss/whole-profile rollback backup. Unified
all-service/network/disk budget still incomplete. Keep Chat OFF. Supernodes/
raised limits and CDN remain explicitly deferred.


## Shared channel session/apps and browser Files candidate — 2026-10-26 UTC

Full goal ACTIVE. Source/compiled progress, NOT deployed. Live remains native25/
9f86587c with paused rollback6ded; server checkout44ea unchanged. Fresh
`device-session-live-unchanged-r1-result.json` PASS verifies native/config/hosting
pins, authority/usage/account/file floors and empty paused old chat history.
Root desktop and /blog are the existing deployment; /desktop untouched. No new
server processes, router ports, native config, boot state or data restoration.
Chat/Rooms stay OFF. Retired legacy startup now also has its own false policy
flag in SOURCE, so a future global unpause cannot silently return deleted chat.

P2P remains the user's main priority. DeviceChannelSession owns one native key
connection, shared archives/optional replicas and DevicePeerSync per desktop
account/session. DeviceHistoryHost deduplicates binding and gives gated API2
views host.storage.deviceHistory.channels({onChange}). Views borrow guarded
facades; closing first/last view doesn't close the peer service. Native consent
withdrawal/account change/desktop end retire it. Same-object account promotion
is checked; actual UI redacts old history/draft/codes. Read results are immutable
and concurrent snapshots share one native read/repair slot. Durable jobs share
repair slots; creation reserves capacity before generating an author key.
Defaults32opened channels/128views/2downloads, not participant/layer RAM reserves.
Old charged closed budgets cannot reset. After fresh actual consent, explicit
renewIdleSessionBudget only replaces a fully drained closed budget; old one stays
closed. No key/authority/replay/history floor is reset.

New device-config startup uses a session lifetime and shared task, not a first
window signal. Actual Chat/Rooms source preview uses one shared UI helper and
the host facade (no app-owned DB/RTC/vote engine). It can save/settle a solo local
note, exchange connection codes, grant a peer read invitation and pull accepted
history. Pending is not accepted/delivered; local accepted head is not global
latest. Solo1validator has0fault tolerance. Remote voting, finished move/chat
composition, bookmarks and long-lived/revocable membership still required.
Current full-block gap256/default1..1024configurable still needs long-gap
checkpoint ancestry/no-replay fast-forward. No live enablement or8k/WAN claim.

Final app test `device-session-bundled-r3-result.json` PASS19 uses ACTUAL
desktop-apps.js/catalog/API2/gate/compiled Chat+Rooms+Calculator/new network
initializer with owned minimal window manager,2real local-development Chrome
sessions/1RTC host-ICE connection/0v86. Actual shared note/read invitation,
closing initial/last window, native pending commit surviving view close with no
late child DOM writes, channel capacity/no orphan key, Calculator,30reopen warm
budget,20coalesced immutable reads, same-object account scoping/redaction,
original-key/floor restoration, withdrawal and actual reconsent recovery PASS.
Controlled registered account labels are scoping fixtures, NOT real issuer proof.
Same compiled entry peer regression35/archive41/replica28 PASS. Legacy host29 is
explicit transformed compatibility fixture only. Exact-file public input/symlink
boundary9 PASS. All7normal apps/15files compile; no eighth app/runtime Node.
All owned fixtures/browsers removed and final network charges0.

Proper host service .build/shared-services/device-session-r1/shared-service.json,
name device-history/sourceAlias assets/desktop/device-history-host.mjs, built from
replica-core.mjs to preserve one native consent/key/protocol domain. Code
7a2dc99572434bd9090414c6250443089f86fc6239d85275662e0f0a1f65e8bb,
manifest51f0e27cb981ad5d4032b23f8e6c87dd6cc087c6efad99c9f0272e15262076a8.
QA helper device-session-core-r1 has byte-identical entry. Independent build
matches/MIT retained; expanded duplicate removed. Explicit vendor JS inputs now
allowed by shared-service wrapper alongside network JS, never directory roots;
undeclared transitive files/private neighbors/symlinks remain refused.
Aggregate device-session-milestone-r1 PASS binds exact proofs; wholeGoalComplete
false. See evidence/device-channel-session.md. Earlier R1/R2 FAIL5 were an outer
disposed gate DOM assertion; R3 FAIL6 quoted test selector; R4 FAIL8 JSON key-order
comparison after WebDriver. Corrected fixtures, no product workaround. Source14/
17 and earlier packaged17/18 keep narrower scopes only; final19 is current.

User explicitly requested persistent browser files as a parallel/subagent task,
with P2P higher priority. That separate candidate is implemented and PASS21
packaged workflow: This browser volume in Files, shared Text save/Save As and
explicit guest Save browser copy/Copy to Linux. Guest RAM remains temporary;
no automatic whole-home copy/upload. Shared bounded strict-IDB BrowserFileStore
uses opaque CAS versions, SHA checks, atomic content/metadata/accounting, stable
anonymous-device or registered subject scopes; old context can't switch account.
Actual two sequential Chrome launches on one owned profile retain saved text.
Conflict/racing writes/native abort/account scoping/folders/Save As/30reopen
resources/real native persist grant+denial and actual site-data clearing PASS.
Clearing saved data preserves a still-open unsaved draft but refuses silent file
recreation. Keep browser files asks real native persistence; denial keeps honest
best-effort files with eviction notice. No server backup/device-loss guarantee;
no chat consent marker fabricated. Default8MiB/file64MiB/scope128MiB/global,
4096entries1024per scope; Text2MiBUTF8. No peer/server/account operations in test.

Browser service .build/shared-services/browser-files-r1/shared-service.json,
sourceAlias assets/desktop/browser-files.mjs, compiled
21ddfd494b27db31f6992b5dc9cc8d0df7b3b9347b469031152ff8da225b2da7,
manifestb66c4ffe301c94550efa25ce56266550c45294e404602e2511421d106680751d.
Raw sourcea7b5e0840dac4882ef9d142882fff73019b1fc9d6af47dd2c22c9c784e2419c6.
Source in assets/desktop/browser-files.mjs, storage fields/helpers in desktop-apps.js,
narrow app.js browser document context/window routing, Files/Text sibling
browser.mjs modules/READMEs. Tests browser-files-bundled-r2 PASS21/milestone-r1;
current-builder exact rebuild PASS. Details evidence/browser-files.md. Agent
finished edits; no Git/server mutation by agent. Real-v86/mobile/server-document
combined release checks and immutable live rollout remain. It is NOT live yet.

Both candidates/proofs are saved in private Git tools/codiserver/device-session-r1.
Combined all-app build .build/public-apps/device-session-all-r1 retained for next
release. Current live pause/prototype/private state preserved. The read-only storage rollout audit is complete in
 evidence/browser-files-rollout-readiness.md (49b5f92d...); live9f/40network modules/
57native files/5other apps must be preserved. Current raw app.js differs from
sealed9f UI/lifecycle fixes, so NEVER copy it wholesale into a live update.
Existing publisher29145 is hardcoded6ded↔9f/unchanged apps/one service and cannot
publish browser files. No Caddy/port change is needed. The storage agent is now
preparing a NEW browser-only composer and pinned publisher CANDIDATE with exact
storage hunks on sealed9f, no install/server mutation or private Git changes.
That later work is NOT part of this tested source packet until reviewed/backed
up. P2P remains the main priority. P2P stays main work:
durable channel directory, long-gap ancestry/checkpoints, durable/revocable read
membership, real remote proposal/vote exchange and automatic mesh repair/election/
retransmission, joint membership, adversarial schedules/partition/churn/fallback,
staged8k and fresh outside-WAN/full audit. Supernodes/raised limits/CDN deferred.
Do not activate old952 chat or reset/restore private data. Moonpie WAN and old
remote-driver cleanup remain pending; no new outside load job was started.


## Browser-local Files/Text live; P2P still priority — 2026-10-26 03:21 UTC

The user explicitly requested this feature as a subagent/aside while P2P stays
higher priority. It is now live at root, independently of paused Chat/Rooms.
Files → This browser → create/open Text → Save survives complete Chrome restart.
Keep browser files requests real native persistence and reports denial honestly;
clearing site data/profile/device loss can remove it. Guest Save browser copy
and Copy to Linux are explicit independent copies, not live Linux persistence
or server uploads. Anonymous files use stable per-device/issuer scope;
registered local files are separate by validated subject. Strict native IDB/CAS/
checksum/accounting guards remain shared host services, not per-app DBs.

Current native25 release36868e655bc12c61123ec2e7d8562bea511375aa6136d5f5dd610ca81a751d46,
301records/86,592,031bytes; remote /srv/codi-connected/releases/native25-36868e655bc12c61,
local active-system/.build/releases/connected-browser-files-r1. Immediate code-only
rollback9f86587c8590eed2c34bbf3eede2efb109fe0a8401328551a00092f19e3b9fe9.
Git-first packet tools/codiserver/browser-files-r1 was pushed inbd8cdf691dd6192919009a1ac302e0a37dedcfe9
before protected install/activation. Webhost source stays exactly cleanbd8; later
proof-only main commits are NOT installed. New protected publisher580bfc334c8ff3006b5930192149e53d9bce915c87594e54247b493f01b233d6
under /srv/codi-connected/browser-files-publishers/<SHA>/publish-browser-files.py
requires exact cleanbd8 and supports stage/activate/rollback/recover/verify with
existing helper/venv/native typed transactions/hosting lock. Old29145 publisher
cannot manage the new release. No data/IDB restore or authority mint/reset.

Current config19f15f856ba5e40db865d6e9b4623fa8f680e92a1952d3765484a5fb31839092;
final native PIDs294841/294843/294844, active/disabled boot, bootstrap stopped.
Root4/fence4 unchanged, expires2026-10-26T10:26:06Z; explicit renewal policy remains.
Publisher revision1150;73test accounts,71prior preserved,2QAaccounts added and
allowned server documents removed. Keys/cookie/permissions/documents/realm,
file-service PIDs, authority and egress floors preserved. Chat backend binding
absent;7room/reader units inactive/all6tables empty/8public paths503.

Browser-only composer applies audited storage hunks onto sealed9f, preserving
57native files/40network modules/networking-reference-terminal bytes/5other app
bundles/old history service. NEVER copy raw app.js wholesale: it lacks unrelated
sealed allowance/status/guest-disconnect/lifecycle/import fixes. No Caddy/router/
ports/firewall/boot change. Hosting pins remain9f7fef18 generator/35bd536b sites/
5e76e178 Caddy. Native code rollouts restart roles;10second maintenance is honest
that guest RAM/unsaved work is not backed up. Root/blog/prototype unchanged.

PASS: component candidate21;actual root2Chromeprocess/2v86boots/browser copies/
FilesText/persisted reload/emulated phone17;registered server document workflow19;
xterm/nano/independent PTYs/touch38;pausedChat14/24appcycles;actual rollback9f+
forward6 preserving exact native local bytes/CASversion;final protected verify;
all133prototype bodies/all10sites/finalhealthr2. Aggregate
active-system/.build/checks/browser-files-live-milestone-r1-result.json binds14
PASSreceipts. First live fixture selector typo retained asr1; corrected testonly.
SystemPython lacked aiohttp; unchanged xterm reran in existing authvenv. Final
healthr1 refused the held verify lock; r2 ran sequentially and passed. No physical
phone or fresh WAN/8k claim. All owned browser profiles removed. Details:
active-system/evidence/browser-files-live.md (omit active-system prefix when inside).

P2P source shared-session19/peer35/archive41/replica28 and bundle7a2d remain
NOTdeployed (backed81424a5/device-session-r1). Main next: durable channel directory,
long-gap checkpoint ancestry and durable/revocable reader membership; remote
proposal/vote/election/joint membership/automatic mesh repair; separate chess/chat
composition, adversarial partition/churn/fallback/staged8k/fresh Moonpie WAN and
full audit. Keep chat paused; don't restore deleted server messages/old952chat.
Full goal remains ACTIVE/incomplete. Supernodes/raised limits/CDN deferred.


## P2P saved channel directory verified; not deployed — 2026-10-26 03:59 UTC

Previous goal turn was PROGRESS: browser files live/rollback verified. Current
turn resumes higher-priority P2P; full goal stays ACTIVE/incomplete. No new agent
was spawned. BrowserFiles agent remains completed; no permission to repurpose it
for unrelated P2P delegation was inferred.

New shared assets/desktop/channel-directory.mjs is session-owned, real nativeIDB,
scoped issuer+registeredSubject/stableanonymous-device; keyDB remainsv2. It saves
verified pinned policy/local author and labels with exact opaque CAS, strict
atomic directory+quota writes. Defaults128bookmarks/account2048/device,
2MiB/account8MiB/device serialized rows, paged1..32/UI16. These are disk metadata
allowances, not channel participant/per-layer RAM limits. Directory-only startup
opens no archives/replicas; restore chooses lazily. Saved/history/key/fence data
remain separate; a crash between key creation/bookmarking can leave an unused
identity. Do not auto-delete/reset voter custody or claim crossDB atomicity.

Host channels facade adds savedChannels({after,limit})→{entries,unavailable,next},
savedChannel(id),restoreChannel(id),renameChannel(id,label,expectedVersion),
forgetChannel(id,expectedVersion). Actual Chat/Rooms preview lists/pages/renames/
removes shortcuts and discovers the same history in fresh Chrome. Corrupt entries
are quarantined without deleting bytes/hiding valid channels. Recomputed checksum
cannot authorize different pinned genesis. Equivalent valid signature for same
logical policy keeps original wire/version/label. No actor/policy rebinding.

Removing a shortcut keeps messages, pending originals, keys and vote/replay
floors; not leave/revoke. Explicit pinned open can re-add; delayed background
restore cannot resurrect it. Catalog read reuse invalidates after committed
metadata writes; channel snapshot/read reuse invalidates after channel writes.
Old read finalizers cannot erase a newer coalesced job. Directory reads and
archive opens use shared repair slots. All old lifetime/account/gate rules remain.

Final raw source-r3 and bundled-r3 PASS40 actual API2/desktop-apps.js/compiled
Chat/Rooms/Calculator with minimal owned WM,2local-development profiles,
3Chromeprocess launches(max2concurrent),1realhostICE RTC,0v86. Native StorageAPI/
IDB/crypto actual, grant controlledCDP, account promotion a scope fixture not
issuer attestation. Real restart discovery/lazyarchive, quota/CAS/nativeabort/
corruption/signatureequivalence/postwrite races/shortcut removal PASS. Same
compiled entry peer35/archive41/replica28/legacyhost29 PASS; legacy29 is explicitly
transformed retired compatibility only. Boundary9 inherited with exact unchanged
compiler/checker hashes, all7apps15files normal build. Profiles/fixtures removed,
final shared network charges0. No physicalphone/WAN/8k claim.

Retain .build/shared-services/device-directory-r3, name device-history/sourceAlias
assets/desktop/device-history-host.mjs, built from replica-core.mjs to keep one
consent/key/protocol capability graph. Code
ecc931bfcd8a341f6114aa34732bf456083a4d2eb77b88b91e3783be3be346ea;
manifest3cbbf1a1f3365ac882a10b231cc655e68726f802da01ecc7da79461e29f315a3.
QA device-directory-core-r3 entry is identical; catalog4f98e9a349c2960edcbfaa8f8847fab882def571827ea03014e838aa1d11784d.
All-apps .build/public-apps/device-directory-all-r3 catalog0da5169bf0a250dae5d805c84d4bbf4dd8e919a2005bb64ff03bc3869eafe05d.
Independent exact build matches/duplicate removed. Earlier35/36/37 source/bundle
proofs have narrower scopes. Final aggregate device-directory-milestone-r1 binds
10PASSreceipts; wholeGoalCompletefalse. Private packet tools/codiserver/device-directory-r1
holds current source/compiled artifacts/proofs. See evidence/device-channel-directory.md
(add active-system prefix from workspace root).

Live remains native25 SDK36868e65/config19f15f85, exact clean webhostsourcebd8,
operator580bfc; source/proof main commits are NOT installed. Protected verify
(device-directory-live-unchanged-r1)PASS: paused/emptychat, all existing private
state/floors/hosting/blog/prototype pointers preserved; no native restart/Caddy/
ports/router/firewall/boot change. Browser files stay live. Root4/fence4 expires
2026-10-26T10:26:06Z, explicit renewal only. Old raw app.js lacks richer sealed
live UI/lifecycle/import fixes; NEVER deploy it wholesale. Current SDK and usable
9f rollback remain; old952 still needs process/unit dependency audit before any
removal and must not be used to reopen deleted chat.

NEXT main implementation: real remote proposal/prepare/commit/accept/view-change
exchange with persisted votes, timers/election/joint membership and durable/revocable
reader membership. Existing wire bound32768/device payload24576 vs2MiB blocks and
31voter certificates requires bounded hash/chunk proposal/certificate references;
accepted-history sync cannot simply expose uncommitted values. Then long-gap
checkpoint ancestry/no-replay sync, automatic mesh/island/partition/fallback,
separate chess/chat composition, adversarial/staged8k/fresh Moonpie WAN and full
audit. Supernodes/raised limits/CDN remain deferred. Keep chat paused.


Directory backup/cleanup supplement — 2026-10-26 04:07UTC: private Git main
734cbdd413279e0c71eb5f0c8d9c1632e1f2a7a6 contains142files/4,290,173bytes at
tools/codiserver/device-directory-r1; source-proof50b61fb84776cce694770b1c6bdaae77499b3bbc60f82311d26796f4bd4bcedf.
Push/remote proof verified; webhost source deliberately staysbd8. Cleanup receipt
device-directory-cleanup-r1-result.json PASS freed3,963,219bytes of local generated
JS helpers/intermediates. Old device-session service/core/all-apps matched pushed
81424a5 copies exactly before removal. This-turn directory r1/r2 intermediates
were closed-manifest/hash checked, never installed and superseded by retained
final service/core/all-apps r3. Browser-files service/current native SDK/usable9f
rollback remain; no server/private state/supplied baseline removal. See current
goal ledger and evidence/device-channel-directory.md; full goal active.


## Remote voting and shared app round checkpoint — 2026-10-26 05:21UTC

This turn and the prior directory turn are PROGRESS; full goal remains ACTIVE.
Browser files are already LIVE (Files → This browser, Text Save/SaveAs); no
further storage rollout remains. P2P stayed the main work. New candidate is
source/compiled only, NOT installed. Live Chat/Rooms remain paused/old tables0.

Four native Chrome profiles now perform real journal-backed prepare/commit/
accept over6actual RTC links. Separate negotiated validator RPC requires reciprocal
exact-link/durable-key proofs; chunk-referenced uncommitted values preserve the
32768wire bound. Distinct verified actors form3of4quorums. Explicit view changes
recover highest-prepared bytes after actual owned leader SIGKILL; equivalent
certificates preserve first archive bytes/floor. Nonleader submission verifies
checkpoint plus accepted-ID membership receipt; exact retry creates no new block.
Actual API2 Chat/Rooms use the one shared session service. Closing sending Chat
while native commit is held lets Rooms show completion without touching old DOM.

Final SAME compiled entry passes real network31/actual apps6/session-directory40/
peer35/archive41/core28. Source app6 also passes. Profiles/static fixtures removed,
final network charges0. Native storage, WebCrypto and votes are real; CDP controls
storage grant; identities/signaling are local-development/manual;0v86/no freshWAN/
8k claim. Network source-r2 fixture args bug and source-r5 wrong status.height
assertion are retained. App bundled-r1 timed out on final link readiness during
concurrent tests (cause unproven); unchanged standalone r2 passes6. No hiddenretry.

Retain .build/shared-services/device-replica-r1 (service), device-replica-core-r1
(QA) and .build/public-apps/device-replica-all-r1. CodeSHA
c9e569f5917dcea975a5165cf074d1be56835e35c658cf487b8b7edb3c785037;
service manifest52c929365b4511538897e3f845635ada30e981f16c82c0abbd4f7ee74a94b566;
QA catalog800e6ac6866ef4c174ad4b6fe645c8335f1f20671611b9289c1c7fd61ee9f51c;
all-apps catalog9b82943a3b6928f7ea692c9951e11e30a3c0234a7b81ea341a3184e85abcf968.
Exact independent rebuild matched/duplicate removed; ordinary app compiler and
exact-file public roots unchanged. device-replica-network-milestone-r1 binds9PASS
receipts. See active-system/evidence/device-replica-network.md from workspace root.

Read-only live verify PASS (device-replica-network-live-unchanged-r1): SDK36868e65,
config19f15f85, PIDs294841/294843/294844 and existing private state/authorityfloors/
hosting/blog/prototype preserved; no native/Caddy restart, root mint, ports or
boot change. Webhost editable source stays exact cleanbd8; protected publisher580bfc.
Root4/fence4 expiry2026-10-26T10:26:06Z; explicit renewal only. Never replace sealed
live app.js with raw source. Keep browser-files SDK/current usable9f rollback.

NEXT: fixed validators currently only; prepare-only proposal bytes disappear on
view advance, so durable bounded voted-value availability is REQUIRED before
Byzantine withholding/liveness claims. Harden direct core repeated-accept
certificate verification (archive path already verifies). Then automatic election/
retry scheduling and joint/durable revocable reader/author membership, long-gap
checkpoint/no-replay chess sync, automatic partial mesh/islands/bridges/partition/
fallback, separate chess/chat composition, bounded PoW, staged8k/fresh MoonpieWAN/
full audit.31voters is not a room participant cap.600sbindings need explicit renewal;
sustained overload fairness unfinished. Supernodes/raised limits/CDN deferred.


Remote-voting backup/cleanup supplement — 2026-10-26 05:23UTC: private Git main
1814748ede0e3fed94c59c4db97a780170a69e62 contains145physicalfiles/5,646,562bytes
at tools/codiserver/device-replica-network-r1; proofSHA
ef9050c73e13c51bed5d581d6044d4f7a883c5f1ca16b0dd1d3adc1485074aec.
Every byte and remote main were reverified; source checkout clean. Webhost staysbd8.
Cleanup PASS freed1,337,767bytes of superseded local directory-r3 service/QA/apps,
exact bytes matched pushed734cbdd packet first. New voting service/core/all-apps,
browser-files service/current SDK/9f rollback retained. No server/private changes.
Receipts device-replica-network-backup-r1 and device-replica-network-cleanup-r1;
new full-goal checkpoint remains partial/active. Historical build-r1 receipt was
restored exactly from private Git after a name collision; current build proof is
uniquely device-replica-network-build-r1-result.json, not old device-replica-build-r1.


## Durable voted-value availability — 2026-10-26 05:42UTC

Previous remote-voting turn and this continuation are PROGRESS; full goal ACTIVE.
New source/compiled candidate only, not installed. Fixed validators now retain
all voted logical payloads in the existing strict signed journal/key-fence
transaction, including prepare-only and older tentative values through later
views/restarts. Default32distinct values/8MiB serialized per validator/height,
hard upper64values/8MiB; no new DB/schema/key/runtime/per-participant RAM reserve.
Same-head retries dedupe. Quota refusal preserves generation/all earlier values
and publishes no new vote; verified acceptance retires all cached slot values.
Pending archive originals have separate acceptance rules and are not deleted by
this cache. Global journal/body allowances still apply. Full liveness under
capacity exhaustion is not claimed; admission/fairness/scheduling still required.

Direct DeviceReplica.accept repeat path now validates full content/certificate,
including equivalent round certificates; invalid repeated signers fail even on
an already accepted head. Old signed journals without values open without any
wire/hash/key/signature/generation/fence rewrite, and first new mutation retains
available payloads. Native keyDB remains2. Actual older compiledc9 voter creates
and reopens real state in tests; old code refuses expanded records without
resetting them. Already erased old payloads cannot be recovered by this upgrade.

Final SAME compiled entry: core43/remoteRTC35/actualapps6/session-directory40/
archive41 PASS. New networking scenario only gives prepared certificate to one
peer; honest prepare-only next leader advances view, actually SIGKILLs/restarts,
then recovers exact highest prepared value despite certificate holder withholding
its bytes. Four native profiles/6Chrome launches/max4concurrent/13RTCconnections
over run/0v86. Core test2Chrome launches/4logical replicas/0RTC also proves multiple
older/newer tentative values, independent byte/count limits, atomic erasure
refusal, acceptance cleanup and real previous-format compatibility. Native API/
IDB/crypto actual, grant controlledCDP; identities/signaling/manual views are
fixtures, no issuer/physicalphone/8k/WAN/full Byzantine liveness claim. All owned
profiles/static fixtures removed, shared network charges0. Compiled network-r1
FAIL14 retained: Python ASCII malicious-peer selection differed from coordinator
locale ordering. Corrected fixture selects first contacted peer; unchanged
product code passes35 in r2. Core-r1 PASS40 precedes added multi-value tests;
final core-r2 PASS43. See evidence/device-voted-availability.md (active-system
prefix from workspace root).

Retain .build/shared-services/device-availability-r1 + device-availability-core-r1.
CodeSHA c45dc0a47faa91a5a98f72b2d58808162722a02331e7f38239b9b041eeb7ed29;
service manifest5502325a7360466ec305ec9236ce965d993d2bbf8f05fa8a47eff23b0c018258;
QA catalog1a25630c03cdf2574bbbe99d75f554af450588a43f33e2f20adb64d6dd48d6b7.
Exact independent rebuild matches/duplicate removed; all-app source/bundles
unchanged (prior all-apps catalog9b82943a...). Old device-replica-core-r1 c9 is
an intentional legacy compatibility fixture, not a live SDK/rollback. Aggregate
device-availability-milestone-r1 binds8PASSreceipts/current source/cleanup.

Protected read-only live verify PASS (device-availability-live-unchanged-r1):
SDK36868e65/config19f15f85, PIDs294841/294843/294844, private state/floors/hosting/
blog/prototype preserved, chat paused/empty; no restart/Caddy/ports/boot/root mint.
Browser Files/Text remain live; webhost editable checkout exact cleanbd8, protected
publisher580bfc, usable9f paused rollback retained. Never overlay raw app.js.
Root4/fence4 expires2026-10-26T10:26:06Z; renewal remains explicit only.

NEXT main implementation: automatic persisted round/election/retry scheduling,
durable/revocable general author/reader membership and joint membership,
long-gap checkpoint/no-replay chess, automatic partial mesh/islands/bridges/
partition/fallback, separate two-player moves/spectator chat composition, bounded
browser-paid admission PoW, staged8k/resource/bandwidth/adversarial/fresh MoonpieWAN/
full audit.31configured voters is not a room-participant cap; current RPC still
validator-only. Supernodes/raised limits/CDN deferred. Keep live chat paused.


Voted-availability backup/cleanup supplement — 2026-10-26: private Git main
5c08e03feaeeba9f735a318fcad96ac5bee14c29 contains130physicalfiles/4,537,582bytes
at tools/codiserver/device-availability-r1; source-proofSHA
967e9cdec75e3fcbd3089c42700b4957304a5fa60de1ad684fbc2b97c532af49.
All bytes/remote main reverified, curated checkout clean. Webhost staysbd8.
Cleanup PASS freed430,568bytes of old generated device-replica-r1 service after
matching its exact pushed1814748 copy. Old device-replica-core-r1 QA is purposely
retained: actual old signed-voter compatibility test dependency. Keep unchanged
all-apps device-replica-all-r1, new availability service/QA and browser-files
service/native SDK/9f rollback. No server/private/native changes. Receipts
 device-availability-backup-r1 and device-availability-cleanup-r1. Full goal ACTIVE.


## Automatic fixed-committee round recovery — 2026-10-26 06:56UTC

Previous availability turn and this continuation are PROGRESS; full goal ACTIVE.
New source/compiled candidate only, not installed. One session-owned scheduler
(timer+worker across opened validator channels) automatically sends queued
originals, persists timeout/view promises, recovers highest prepared values and
replays missed certified blocks before advancing native acceptance. Higher-view
adoption requires f+1 distinct current-slot proofs whose signers match bound
actors; raw counters/copied signatures cannot manufacture that threshold. Existing
core quorum/vote/lock/cached-payload rules remain. Activity hints verify current
signature/permission/sequence/witness and are ephemeral, not durable acceptance.

Default new device path automaticRounds true; explicit false is manual development
mode (old fixture scopes). Chat automatic UI shows Send, hides manual controls.
Native keys/archive/RTC/account lifetime still host-owned; no app-owned network
or server history. Work accepted into the session survives closing its sending
window; account/consent/session retirement closes timer/owned deadlines/worker.
All owned deadlines are explicitly cleared, not uncancellable AbortSignal.timeout.

Voting negotiates codi-device/1:replica/2; content sync remains separate. Parent
RPCs and chunk child requests/handlers have independent4-job bounds under the
same pool budget. Expired bound-peer hints(max128/charged) authorize nothing;
renewal requires fresh exact-link/durable-key reciprocal proof and cannot switch
actor on a live link. Default token600s; test narrows to10s and observes actual
expired authority with still-live transports/hints before automatic renewal.
Initial signaling/connect/first binding/reconnection setup remains explicit.
Defaults active pulse1s/idle30s/view15s exponentialcap120s/RPC3s/worker60s; one
active pulse charges8MiB metadata plus shared consensus slot. Not RAM per person/
layer or a strict native heap claim. Sender history lookup<=256hash-index links;
repair<=3blocks per replying peer/pulse, with full transition/cert checks. No
long-gap/no-replay snapshot claim and no known floor reset.

Final SAME compiled artifact: automatic actualapps17, transport36, session40,
peer35, archive41, core43 PASS. Automatic test uses4native profiles/5Chrome
launches/13actual RTC connections/0v86: Send, real leader SIGKILL, automatic view
recovery, unchanged detached sender DOM, original-key/floor restart and verified
missed-block repair after explicit reconnect, expiry/renewal, bad repair block,
copied/unsupported future promise, actual2by2partition pending retention then
same-original exactly-once acceptance when links return, unrelated Calculator,
30actual app reopens/warm accounting and full end-session cleanup. Idle worker/
deadline charges0 and one timer; end closes timers/deadlines/jobs/channels/all
network charges. Native StorageAPI/CDP grant, IDB/crypto/RTC real; test identities
local-development, no issuer/physicalphone/newWAN/8k/full Byzantine liveness claim.

Source-app-r1 FAIL1 caught status round overwriting driver reference (fixed).
Source-app-r2 FAIL5 was fixture reconnection through disposed Chat facade; now
borrows live Rooms facade. R3 PASS9/r4 PASS15 narrower. Compiledr1 PASS16 used
built-in timeout signals; finalr2 artifact has owned deadlines. Appbundledr2 PASS16,
final appbundledr3 PASS17 explicitly proves expired bindings are not authority.
No hidden retries. CONTRIBUTING updated to current scoped APIs/automation and
remaining limitations. See active-system/evidence/device-automatic-rounds.md.

Final retained service .build/shared-services/device-scheduler-r2;
QA .build/shared-services/device-scheduler-core-r2. CodeSHA
28693a0c7657f3689b61e116a24d1e97c46db70cbf1c81fdc31df3b9e9d6d585;
service manifest73545bd836656eafdcb92cb98211bcf099b27255ac917ec8fc53576524950684;
QA catalog6c32c6b71c1f5cd15905266f16ca70aaba2e80718dc4c3ee085fb23eace4184f.
All-apps device-scheduler-all-r1 catalogc8a062ddf9049ea8e0869617896067370e85de7445f330c87c008ffb371eb427;
exact independent rebuilds match/duplicates removed, ordinary compiler/exact
public input boundaries preserved. Aggregate device-scheduler-milestone-r1 binds
9PASSreceipts/current source/cleanup. Oldc9 QA deliberately remains legacy voter
compatibility dependency; no old live chat reactivation.

Protected read-only live check PASS: current browser-files SDK36868e65/config
19f15f85/PIDs294841/294843/294844/private state and authority floors/hosting/blog/
prototype preserved, paused/empty chat, no restart/Caddy/ports/boot/root mint.
Webhost editable Git remains exact cleanbd8; publisher580bfc, current SDK/usable9f
rollback and old952 pending executable audit retained. Never overlay raw app.js.
Root4/fence4 expiry2026-10-26T10:26:06Z; renewal explicit only.

NEXT: durable/revocable general author/reader membership and safe joint committee
changes; long-gap checkpoint/no-replay chess, automatic partial mesh/islands/
bridges/partition transport repair/bounded fallback, separate player moves and
spectator chat, integrated bounded admission PoW, staged8k/resource/bandwidth/
adversarial/fresh MoonpieWAN and full audit.31format voters is not room size or
proof for all31-voter topologies. Fixed4 automatic rounds are partial progress,
not complete self-organization/general membership. Keep live chat paused;
browser files/root/blog/prototype remain live. Supernodes/raised limits/CDN deferred.


Automatic-round backup/cleanup supplement — 2026-10-26: private Git main
cb052c66210709a4a101ae64b5a3b8a449c20db3 holds160physicalfiles/5,445,823bytes
at tools/codiserver/device-scheduler-r1; source-proofSHA
bddd9563e00f3c2daa65126a0940cf27f9bdc6ebbcd90731f85f54805450d54c.
Every packet byte and remote main reverified; curated checkout clean. Webhost
stillbd8. Cleanup PASS freed2,347,855bytes: superseded c45 availability service/
QA and old manual all-apps matched their pushed copies; this-turn scheduler r1
service/QA closed-manifest/hash verified before removal, never installed, finalr2
supersedes them. Keep current scheduler-r2/service+QA, scheduler-all-r1 apps,
legacyc9 QA compatibility fixture, browser-files service/current SDK/usable9f
rollback. No server/private/native deletion or change. Receipts scheduler-backup-r1
and scheduler-cleanup-r1 (device- prefixes). Full goal remains ACTIVE/incomplete.


## User-requested goal refresh and current WIP — 2026-10-26

The user asked to remove already-completed work from the forward goal. The
current remaining objective is in goal-requirements.json.updatedGoal: finish
participant-device membership; generalized self-organizing P2P/islands/fallback;
long-gap/no-replay recovery and admission PoW; separate durable text chess/chat;
staged8k/resource/fault/freshWAN; then reviewed live rollout and final audit.
Root/blog, browser files, desktop/app/PTY/touch/voice, accounts/private folders/
ACLs and maintenance/cache are completed safeguards, not tasks to redo. Use the
owner live test site; do not revive the retired VM-first gate. Keep live chat
paused until the replacement works. Optional supernodes/CDN/marketplace/payment/
graphical chess remain deferred. Full goal remains ACTIVE, not complete/paused.

Membership code is currently UNVERIFIED WIP, not a successor green release.
New device-member-channel.mjs and optional publicRead/read ACL fields, generic
Exchange member profile, separate member PeerLink capability, host routing/
client transfer scaffolding are in the worktree. Existing policy bytes/fences
must remain compatible; new member-enabled policies reject legacy short read
routes. General-member UI/tests and revocation proof are unfinished. Core-source
membership-r1 PASS43 is narrow. Automatic-source membership-r1 reached15checks
(send, crash, catch-up, expiry, bad claims, partition exact once), then FAILed
Readiness timeout at lifecycle cleanup/warm idle; inspect its receipt before
claiming current tree passes. Both exec handles58213/66821 are terminal and all
owned browser fixtures cleaned. The last verified compiled/backed candidate
remains scheduler28693a0c.../cb052c6 + proof3d04c14; current membership edits were
not installed. Browser files/live native25/paused chat remain unchanged.


## Ordinary device-channel membership candidate — 2026-10-26 UTC

Scoped source/compiled candidate PASS, NOT deployed. Full goal ACTIVE/incomplete.
New member policy publicRead plus accepted explicit read/write ACLs; member
capability codi-device/1:member/1 distinct from validator replica/3. No vote
granted by membership. Old policies/keys/floors/wires preserved; new policies
refuse legacy short read routes. Native provider checks at bind/request/chunk/
response publication; cannot erase copies or inform offline peers of new ACLs.

Actual member UI exports/imports policy-only code, shows durable member key and
controller Allow reading/Read+write/Remove operations (pending until accepted).
Shared host owns automatic non-voter catch-up/submission, same key/account scope,
archive/cache/exchange; apps do not create transport/key/database instances.
Writes require direct connected validator; ordinary peers can serve accepted
history. Joint validator changes/automatic routing remain unfinished.

Two fixes: acknowledgement releases partial/cancelled result caches even after
binding expiry (cleanup only/exact transport/request/channel/root); signaling
sets connecting before setRemoteDescription await so late completion cannot
overwrite authenticated ready. Deterministic delayed-signaling and held response
read cancellation checks pass. Fixture Accept readiness now excludes Not now.

Final code605b3b392bc2e8c5ffc43716dfd1bed9162ce16f7257e04b0e9ed669ae9bed6f;
service manifest9f2862b52b028e50294392e32242c908faa2bc27dfa0e8d871ef84163bddcba4.
Retain .build/shared-services/device-membership-r3 and device-membership-core-r2;
all7apps .build/public-apps/device-membership-all-r1. Exact independent service/
app rebuilds match, duplicates removed. Initial host-only wrong entry rejected
by hash assertion and closed-manifest/hash checked before deletion (403328bytes).

Aggregate device-membership-milestone-r1 PASS10 current receipts: member16, auto17,
transport37, session40, peer35, archive41, core43, boundary9/build/live unchanged.
Member fixture6nativeprofiles/7launches/10RTC links/4voters+writer+observer/0v86.
Actual code/permission/Send UI, read-only refusal, native read/write revocation/
regrant incl held-node response publication, same-key restart/controller offline,
3remaining validators and ordinary-to-ordinary accepted history; actual native
StorageAPI/CDP/IDB/crypto/RTC, local-development identities. Automatic original
once/partition/crash/expired binding and 30reopen/zero resource regressions pass.
Signaling/initial connection/binding/reconnection remain fixture-explicit. No
issuer/WAN/8k/joint-membership/full Byzantine-liveness claim.

Retained failures: source auto-r1 FAIL15 cachelease; source auto-r2 FAIL9 forced
rebind concurrent capacity (controlled probes now wait quiet boundary); bundled
auto-r1/member-r1 restart Accept-selector race; member-r2 one-sided connecting.
Transport-bundled-r2 initial connection stalled after5 with insufficient link
diagnostics; sameartifact r3 and enriched-driver r4 PASS37 do not explain that
instance or prove general connection recovery. All fixture handles terminal,
owned browsers/profiles/temp fixtures cleaned, all network charges0.

Protected live read-only verify PASS: SDK36868e65/config19f15f85/old PIDs/private
state/authority floors/hosting/blog/prototype and paused-empty chat unchanged.
No activation/native restart/Caddy/ports/boot/root mint; webhost exactbd8. Root4
fence4 expires2026-10-26T10:26:06Z, renewal explicit only. Never overlay raw app.js.

Next: safe joint validator membership and automatic introductions/partial meshes/
islands/bridges/transport repair/bounded fallback; ordinary submission routing,
long-gap no-replay/chess/chat/PoW, staged8k/resources/freshWAN and full audit/
reviewed rollout. Keep completed browser files/root/blog/desktop safeguards;
keep live chat paused. See evidence/device-membership.md, CONTRIBUTING and
goal-requirements.json.updatedGoal/currentCandidate.


Membership backup/cleanup supplement — 2026-10-26: private Git main
f109847908af7b83497fdc066351646c358085e6 holds169physicalfiles/5,811,521bytes
at tools/codiserver/device-membership-r1; source-proofSHA
6de98cf682dce0ece7cc6f6625df9c52f4747f9cc130f36c47b50e683e657752.
Every packet byte/closed inventory and remote main/clean checkout reverified.
Cleanup PASS freed2,419,107bytes: superseded scheduler service/QA/allapps matched
pushed scheduler packet, and never-installed old member service/QA intermediates
matched complete compiler inventories/hashes before deletion. Earlier host-only
wrong-entry intermediate separately removed403328bytes. Current member service
r3, QAcore-r2, allapps-r1 and legacyc9 voter compatibility fixture retained;
current live SDK/usable rollback/private state untouched; webhost remainsbd8.
Final diagnostic transport-r4 PASS37 and member-r5 PASS16, aggregate10PASS
receipts; all owned test handles terminal/fixtures cleaned. Full goal active.


## Automatic member introductions and low-data follow-up WIP — 2026-10-26

UNDEPLOYED WORKTREE, not successor acceptance. Full goal active. After private
Git c67f9f5/f109847 membership605b, added bounded one-hop durable-contact/member
introductions, member/2, own deadlines/backoff/replay/crossed-offer preservation,
target4/max6neighbors/32contacts/2pending under the shared pool/budget. Native
viewJobs4 now separate from network repairJobs4; bindings coalesce per exact
link/channel and waiter cancellation does not cancel other apps' auth; fast
remote capacity refusal. Source3 PASS7 then compiled c239 PASS14 actual8browser
introductions/adversarial/seed loss. b97d independent history/discovery cadence
and quieter healthy sampling PASS17 actual9profiles/9launches/23links with
9th join/leave, no v86/server history. NOT general islands/8k/WAN/fallback.

User steered: some groups are costly third-world/3G, others fiber/low latency.
Measured accelerated signed payload about21.8MB/75s across9participants for
4messages, then14.9MB/61s after cadence split: too much, not acceptable stable
low-data proof. Current WIP adds native CAS per-channel preference UI (Low data
default, Balanced, Low latency), scoped inline small RPC values behind mutual
capability, ordered pending batches<=16/shared-checkpoint receipts, looser slow
RPC deadlines, reactive update hints and less frequent idle polls/discovery.
These are preferences, not hard byte caps. No guaranteed sub1ms latency.

Current generated service .build/shared-services/device-member-data-r2 and QA
device-member-data-core-r2 code5130f56a095204009947ad6050d635eb9d48833e7dd7147105531940dee153f5,
manifest9cefbf9519407052e2d687f2b055fd9af98c236fd2aec6feaa4efd2d4530c4a7;
all-apps device-member-data-all-r1 catalog180ec0b26ecce8370ff5bcd860f5d01574d39c2d0ac5d13e9c074379c415b099.
Core43/archive41/legacy chunk transport40 PASS this entry; profile+inline+batch
actual mesh still pending. This-turn intermediate candidates retained until
curated backup/closed-manifest cleanup; do not install them or call green.

Retain failures: peer-source1 duplicate manual seed after auto connection formed
(fixture now reuses actual established link); source2 repair slots starved local
read (viewJobs); source4 callback syntax fixed before build; compiled1 replay
rejected existing link before nonce (now explicit nonce rejection); mesh-r4
saturation fixture raced existing repair leases and leaked its own fake slots
(now acquired/released inside try/finally). Test driver died during mixed runs;
real port/process absent confirmed, no remaining owned orphan root Chromes in
audit, restarted foreground chromedriver exec65138 using existing Snap binary.
Driver loss failures are not product passes. Source member regression also
saw a capacity timeout, shared binds/fast refusal added. One-way initial peer
connecting still intermittent: added actual raw PeerLink per-link flags/seq/
state caller trace in fixture; investigate next failure, do not silently rerun
away broad robustness requirements. Current driver cases are recorded locally.

No native/server/private state change; live root/blog/browser files/prototype
and paused-empty chat preserved. Latest read-only health before these WIP
changes PASS unchanged SDK36868e65; webhost remains exactbd8, no source pull.
Root4/fence4 expires2026-10-26T10:26:06Z, explicit renewal only. No new router
ports/firewall/boot/certificate/state reset. Continue data-efficiency proof and
secure scalable routing; joint membership/long-gap/chess/PoW/8k/WAN/full audit
remain required. Do not mistake local compiled directories for installed SDK.


## Mixed-link requirement and low-data/member candidate — 2026-10-26

User clarified the SAME channel may mix fast fiber and constrained3G/backhaul.
Per-device/channel receiver-controlled byte and relay budgets, bounded queues,
chunked catch-up and independent fast-path progress are now first in the updated
goal. Current profiles are local preferences, not hard caps or automatic link
adaptation. Do not promise sub1ms or affordable monthly usage from short tests.

Source-only candidate c7c0f579f26673c8c7e5be90dd72c49926fd84bb91a9bb98ca8a747b97cf49ae,
service manifest a46a37af4c6e47d825dd236b66924a968897f07facf1ecb9e87c6b8956a2b565.
Keep .build/shared-services/device-member-data-r8 and QAcore-r8, all7apps
device-member-data-all-r1 catalog180ec0b2; exact independent builds match.
Current aggregate device-member-data-milestone-r8 PASS12 binds267 scoped checks:
mesh26/member16/auto17/transport40/session40/peer35/archive41/core43/boundary9.
Mesh is actual9profiles/10launches/17RTC links/0v86/local-development identities;
20.044second healthy idle interval sent0signed application payload bytes,
excluding WebRTC/relay headers, longer checks, HTTP/guest/speech assets. No
physical3G/fiber/8k/WAN or deployment claim. All owned test fixtures cleaned.

Includes bounded signed one-hop introductions (target2lowdata/max6neighbors/
32contacts/2pending), native view-work isolation, shared binding coalescing,
bounded hello retry/ACK, inline small RPC/hash checks, ordered native batches/
shared checkpoint receipts, separate history/discovery cadence and durable
per-device preferences. Member/3, inline-values/2, operation-batches/1 and
hello-retry/2 are separately negotiated; no new visitor runtime.

Two genuine fixes from failures: acknowledged hints now survive transient
provider refusal with bounded backoff; validated non-voter submissions wake
and propagate bounded activity among surviving configured voters so an absent
leader triggers native view recovery. Test makes the offline controller the
exact next-slot leader, preserving actual quorum/signatures/accepted ACLs.
Positive fixture binds retry only explicit busy refusals with a30second bound;
negative ACL/saturation probes unchanged. Retained mesh-r7 capacity/r8syntax/
r9losthint/r12busy-seed and members-r7busy/r8absent-leader failures remain.
Evidence adapter initially assumed every sourceSHA256 was a map; retained
source-shape failure, then verifies the live wrapper string pin explicitly.

Known one-hop capacity saturation can prevent a late node getting its second
neighbor. Mixed-link budgets/adaptation, general islands/routing/fallback,
joint validators, long-gap no-replay/chess/PoW/8k/WAN/full audit/rollout remain.
Full goal ACTIVE/incomplete; live Chat/Rooms stay disabled and history empty.

Live SDK36868e65/config19f15f85/sourcebd8/root/blog/browser files/prototype and
private keys/accounts/documents/floors preserved; no activation/root mint/
Caddy/router/boot change. IMPORTANT: Root4 expired2026-10-26T10:26:06Z. Steward
failed on expired seed and systemd start limit; issuer294841/guest294844 stay
active. Publisher verify PASS means release/data preservation, NOT live-role
readiness. Health receipt device-member-data-live-role-health-r1. Root5 approval
is pending; old explicit-live-root-renewal-r5.py is PRE-EXPIRY ONLY and must be
replanned before any approved recovery. Never auto-mint/reset floors or restart
the expired steward blindly. Preserve current immutable SDK/usable9f rollback.

See goal-requirements.json.currentCandidate/updatedGoal (currentCandidate under
deviceHistoryWork), served_apps_public/CONTRIBUTING and evidence/device-membership.md.
Private curated source/proof packet refresh and superseded generated-output
cleanup follow; do not install local QA builds or overlay raw app.js.


Low-data candidate backup/cleanup supplement — 2026-10-26: private Git main
583e33fdf9c002fc211b610263ba4bebe3c093a2 holds201physicalfiles/7,678,526bytes
in tools/codiserver/device-member-data-wip-r1; source-proofSHA
53cd05822a2388652323612c6584d1e74060e8de18e2ca820e7c4a1021d0c91f.
Every packet byte/closed inventory/remote main and clean checkout reverified.
Cleanup PASS removed19never-installed superseded local service/QA/apps outputs
against complete catalog inventories/hashes and backed build receipts, freeing
9,719,019bytes. Retain current data-r8/service+QA, data-r7 diagnostic pair,
current data-all-r1 apps, prior605b membership service+QA/apps and legacyc9 QA.
Current live SDK/usable rollback/private state and prototype untouched; no
source pull/deployment/signing/restart. Earlier exact-rebuild duplicates also
removed1,108,985bytes(r7) and521,776bytes(r8). Backup/cleanup receipts are
device-member-data-backup-r8 and device-member-data-cleanup-r8. This supplement
and receipts are followed by a private proof-only commit. Full goal ACTIVE;
Root4 remains expired/steward failed, explicit Root5 recovery approval pending.


## Receiver-issued byte allowances WIP — 2026-10-26

Full goal ACTIVE; preceding turn was progress. Source-only shared bandwidth
owner now in network/device-channel-bandwidth.mjs, modern member/replica RPC
only. New negotiated capability codi-device/1:byte-credits/1 is the eighth
capability. Grants bind exact transport entry/channel/genesis, reserve receive
allowance before data, max1MiB credit (still32KiB signed frame cap). Native
read ACLs gate issuance; grants convey no membership/votes. Upload and shared
reply/history allowances; control separately bounded. Per-channel usage remains
across peer reconnects; settings persist by strict native directory CAS, while
usage counters restart per runtime. Unused/failed allocations count
conservatively; old in-flight grants get60s grace. These are not ISP/monthly,
cross-tab/durable/global or legacy content-sync/browser/guest/HTTP/voice caps.
Do not activate until scope/remaining legacy path is reviewed honestly.

Shared scheduler permits one running job per owner with independent owners
progressing; strict per-link signing/sequence preserved. Credit preflight
waits use bounded metadata before acquiring consensus/repair slots and respect
caller cancellation. Prepared frames are one-shot private WeakMap tokens.
Publication rechecks native authorization after credit/queue/signing waits.
Tracked controller jobs/partial channel registration release resources on
closure/failure; idle budget cannot be renewed before old work drains.
Malformed scope/control-budget overflow now closes offender instead of
downloading and dropping forever. Foreign nonce failures cannot cancel another
peer/channel's pending request. Existing app allowance UI applies saved
validated KiB settings; no new app, engine, server/package, Node visitor runtime.

CURRENT r6 code7a6b562c65c49b174add89c6c8d01551d29c2a7c69a0b7ae883efe5d2e01b760,
manifestc935a7872fea1e82be42003379a3bf9aea5e6e34c8f7460257a6611b353745c3,
.build/shared-services/device-byte-credit-r6 and QAcore-r6;24exact public inputs,
all7apps device-byte-credit-all-r3. R6 verification pending: exec18140 native
(device-byte-credit-native-r6) and21688 member (device-byte-credit-members-r6).
Poll confirmed handles; do not restart after an observation timeout.
Predecessors: R3/R4 native11 PASS, R5 native12/member16/transport40/session40
PASS; R3 default finite profile3/transport40/session40 PASS. Native fixture
6profiles/7launches/9RTC/0v86; two extra scheduler/controller checks are unit
scope (not signed-network claims). Injected150ms send delay, no real3G/WAN.
Budget0 paused one reader without holding fast readers; refill caught up exact
originals; shared replies0, signed cross-link replay rejection, UI/native CAS,
fresh-profile limits/key/history and all resource charges return0. Private
read/write/revocation/regrant/held-node publication/offline leader checks pass
onR5 with credits enabled. Current artifact needs its own selected receipts.

Retained native-r1 FAIL7 positive read raced prior pause; native-r2 FAIL4
recovery starvation/short3s test windows; session-r1 FAIL7 first-details selector
now points at connection panel; member-r1 FAIL13 post-regrant floor8 stalled on
small grants. Fixed preflight admission/larger receiver-sized credits and10s
window fixture; no prior failure is erased. Exact source/build receipts retained.

No live change: read-only device-byte-credit-live-unchanged-r5 PASS preserves
SDK36868e65/config19f15f85/sourcebd8/keys/accounts/files/hosting/prototype and
paused-empty chat. Steward remains failed after Root4 expiry; Root5 approval
pending, old root5 script PRE-EXPIRY ONLY. Never mint/restart blindly. Private
Git last ea92446; this turn source/proof backup and generated cleanup still
needed. Keep C7 data-r8 last fully aggregated predecessor, current R6 and
legacyc9/nativeSDK/rollback/private state. General routing/legacy accounting,
durable global budgets, asymmetric/loss/WAN, islands/joint members/long-gap/
chess/PoW/8k/full audit remain; do not call whole goal complete.


Byte-credit WIP supplement — 2026-10-26: R6 native12 PASS, member FAIL13;
R7 added bounded8native RPC failures (op/method/nonce/240char error; no payload).
R8 clears settled shared credit waits before completion and refreshes once if
a grant expired during control send; deterministic fake-clock unit passes.
Current code559cb99fdaae654e868184b85eee8a7f379fb40988efb60d3ea248d1dac3c9e9,
manifest586fafdccc12ed9a7d814baeaf2970ce158819236b56aabc41a81e7d8214ab2e,
service device-byte-credit-r8/QAcore-r8, apps still all-r3. Native-r8 PASS13
(10native/UI/RTC checks plus3unit probes), member-r8 and member-r8-diagnostic
FAIL13: post-regrant observer remains7/8 instead of10. R5 member16 once passed;
this is NOT robust acceptance. Provider failures show peer download/TTL refusal
(and transient consensusJobs); creditsDenied0/configured allowances available.
Added local sync-error trace and read-only native scratch stats to fixture.
Diagnostic proves only1empty retained job, so maxJobs exhaustion is not the
cause in that run. Inspect exact credit-state/TTL/remaining bytes next instead
of guessing or loosening the oracle. All test handles from this turn terminal;
all owned profiles/fixtures cleaned. Driver65138 remains reusable.

R5 transport40/session40 and earlierR3 default3/transport40/session40 PASS,
24-file compiler-boundary9 PASS; current R8 has no successor aggregate.
No live change, Root5 still unapproved/old script pre-expiry-only; SDK36868 and
paused chat preserved. All this-turn byte builds are local/never installed.
Curated source-only WIP backup now follows; do not activate or discard C7
last fully aggregated predecessor/native SDKs/legacy QA/private state.


## Byte-credit R10 scoped proofs and combined mesh failure — 2026-10-26

Full goal ACTIVE/incomplete; source-only, NOT release ready or deployed. R10
code57a0aaf1fa0c01f5e5c3d612405c101c4c05dae8b1acb60a470e09842d99acf4,
manifest29aaa1671bbe73d770b6f80f74e38e4ca41f089ed781f7a952e64406cba27846;
keep service device-byte-credit-r10 and QAcore-r10, apps all-r3. R9 diagnostic
739d98aa/core-r9 retained for before/after oracle. Earlier r6/r8 notes above are
historical WIP, not current readiness. No product changes after R10 freeze.

Root cause of private regrant stalls: grant TTL previously ended with the
allocation window, so near-boundary grants could expire before transmission.
New independent bounded lease is60s by default (6s test); bytes remain charged
to original window, with60s in-flight grace. Actual compiled old/new unit at
clock9999 of10s window gives1ms versus6000ms for equal16384-byte reservation.
Initial regression fixture used noncanonical genesis; registration correctly
refused, input corrected and failed receipt retained. No permission relaxation,
quota increase, scratch eviction or replay/floor reset fixed the defect.

R10 native14/short3s-window14/private member16 twice/default3/transport40/
session40 PASS; exact independent service/all7app rebuilds match. Native14
includes10native/UI/RTC plus4explicit units, not14network probes. Native uses
6profiles/7launches/9RTC; private uses6/7/10;0v86/local-development identities.
Transport/session regressions disable credits, so prove compatibility only.
Injected150ms delays and local tests do not prove physical3G/fiber/loss/WAN.

COMBINED mesh with credits FAIL3:8sessions started; introduced real extra
neighbors, then d had7neighbors despite configured6 (others2-4). Assertion
unchanged; all owned fixtures/profiles/charges clean. Do not claim mesh/scale
acceptance or retry until a lucky pass. Need unified admission across automatic
introductions and explicit seed/member bindings plus deterministic concurrency
regression. Credit timeout diagnostics retained for follow-up. Aggregate
device-byte-credit-milestone-r10-result.json is explicitly PARTIAL, binding
143assertions across repeated current compiled runs, unchanged compiler9,
exact rebuild/lease comparison/live preservation and failed mesh.

Scope: per-runtime/channel conservative modern RPC data allocations, separate
control; settings persist, usage does not across browser restart/tabs. No
ISP/global/durable/legacy HTTP/guest/voice/full-relay cap or speed adaptation.
Keep live Chat/Rooms paused/empty, sourcebd8/live SDK36868/config19f/private
keys/accounts/files/floors/root/blog/prototype preserved. No deploy/sign/restart/
hosting/router/boot change. Root4 expired/steward failed; explicit Root5 recovery
approval pending and old helper pre-expiry-only. Read-only preservation PASS
is not all-role health. General mesh/joint validators/long-gap/chess/PoW/8k/
WAN/audit/rollout remain; browser files already live.

Private backup predecessor c6fb9d9499c0fce5e6290508b02b96ac5077692f holds R8 WIP;
current source/proof refresh follows. Cleanup receipt byte-credit-cleanup-r8
removed14never-installed superseded outputs,7725196bytes, backed complete
inventories verified. Keep currentR10, R9diagnostic, last C7, native SDK/usable
rollback/legacy QA/private state. Do not overlay raw app.js or pull webhost.

R10 backup supplement — private main ac4c61875498d06b041ee026133cf8b64ba1721a
holds177physicalfiles/5807492bytes, source-proof9b98de1896ea927ac37fe4e58e908d82bb7643b9bf8ee71b24030f0cf4cc6bfd.
Every byte/closed inventory/current source parity/remote main/clean clone
verified by device-byte-credit-backup-r10-result.json. Source-only PARTIAL
aggregate and failed mesh preserved. This receipt/docs supplement follows
as proof-only Git change; no deployment. Next unified neighbor admission.


## R11 shared neighbor admission and measured traffic — 2026-10-26

Full goal ACTIVE, source-only/not deployed; successor of R10 PARTIAL. Current
code48c33e399bb30ae6f940622cc800a2ee1d07fc4d7dd202cf1c8fbe6b8fb30711,
manifest50a274b72f3fd2bef1fe7fdb3b544978c03cc743ec846db9dcca74a84cf92647;
service device-byte-credit-r11/QAcore-r11, apps remain all-r3.24exact public
inputs, independent complete service rebuild byte-identical. Keep R10/R9
diagnostics and last fully aggregated C7/legacy/nativeSDK/rollback/private state.

R10 bound failure was real: introduction reservations alone did not cover later
direct bindings. DeviceReplicaExchange now acquires a resource-only admission
when first committing a verified binding. DeviceMemberIntroductions owns
shared exact-entry/actor claims; incoming/outgoing member and validator bindings
share one slot/refcounts, matching introduction reservations are not counted
twice, configured-validator slots remain reserved. Disconnect/close releases
claims; renewal preserves a claim; actor changes cannot reuse it. Capacity
refusal does not grant rights or drop other shared transports. Partial channel
open failure also closes an already-created topology owner. Native ACLs/proofs/
quorum/known-key floors remain authoritative; no permission or cap increase.

Actual8profile/10RTC admission7 checks fill6slots (3dual-role validators and
3ordinary peers), reject7th promptly, keep quorum/readers working, reuse one
released slot and release both role refs on disconnect. Sampling is paused
only in this deterministic fullness construction; native binding/ACL/credits/
quorum remain real. Two fully introduced9profile/10launch/17RTC mesh runs
PASS26 with credits, including lost hello/seed, update refusal/retry, batch,
late join/restart/departure and bound<=6. Explicit setup now chooses a
least-loaded validator instead of assuming its initial slot remains free.
The separate deliberate7th-binding negative prevents that setup change from
hiding the cap. Old R10 FAIL3 remains retained.

R11 native14/private16/transport40/session40/default3/asymmetric15 PASS too.
Native14 contains4explicit unit probes; transport/session fixtures disable
credits for compatibility. Asymmetric probe uses actual signed RTC/native
archives with application-send shaping8192B/s up,32768B/s down,300/650ms
one-way delays on one leaf; production60s credit lease. Not physical3G/fiber,
packet-loss/WAN/NAT or measured-link adaptation. Original asymmetric FAIL2
incorrectly assumed quota edits revoke existing60s grants after10s. Exact
failed driver snapshot/diagnosis retained; corrected probe waits actual lease
and passes without a product change. Old grants remain conservative allocated
bytes with up to60s in-flight grace; a quota edit is not instant revocation.

Aggregate device-byte-credit-milestone-r11-result.json PASS binds187current
assertions across repeated probes plus unchanged compiler9, exact build/driver/
source/cleanup/live-preservation proofs. releaseReady=false and
lowDataEfficiencyAccepted=false. Healthy20.042s window sent0signed application
bytes, excluding RTC/TURN/HTTP/guest/voice and longer idle checks. IMPORTANT:
observed8message batch window across8profiles used1,863,470signed bytes over
13.653s, including concurrent votes/RPC/chunks/retries. Biggest categories:
replica/data819792, replica/result296705, member/result253966, status calls151695.
This is not isolated per-message or IP/monthly cost. Active traffic is still
too high for the user's constrained-data goal. Next reduce redundant status/
certificate/content exchanges with measured regressions, preserving missing-
value recovery/native votes/hash/ACL checks; do not declare efficiency complete.

All test handles terminal; all owned profiles/fixtures/charges cleaned. Reusable
ChromeDriver65138 remains. Live read-only preservation-r11 PASS keeps
SDK36868e65/config19f15f85/sourcebd8/root/blog/browser files/prototype/private
state and paused-empty Chat/Rooms. NOT live role readiness: Root4 expired and
steward failed, explicit Root5 approval pending/pre-expiry helper unsafe now.
No signing/restart/deploy/hosting/router/boot/source pull. Full durable/global/
relay/legacy budgeting, general routing/islands/joint validators/long-gap/
chess/PoW/8k/WAN/audit/rollout remain. Current private Git backup follows;
predecessor a6030eb holds the R10 code/proof/backup supplement.

R11 backup/cleanup supplement — private main f00ca896b30b73ed398da8eca991bfd3247c26f1
holds198physicalfiles/6948647bytes, source-proof86b7bad1f5b0ea8b8282719d0c597fddb90613ba2f53614d564d54e711431c0c.
Every byte/closed inventory/current source parity/remote main/clean clone
verified (device-byte-credit-backup-r11-result.json). Cleanup PASS removed
4never-installed superseded byte-credit R7/R8 service/QA outputs,2187520bytes,
against complete backed inventories/catalogs. Retain R11/current, R10/R9
diagnostics, last C7/legacy/nativeSDK/rollback/private state. Proof-only receipt
supplement follows. Next investigate compact automatic status hints (scheduler
uses actor/position/round/viewChange, full status also sends unused vote/prepared
fields), preserving legacy API/native recovery; active-data efficiency remains
unaccepted. No live changes, full goal ACTIVE.


## R12 compact status and unresolved quiet retry traffic — 2026-10-26

Full goal ACTIVE, NOT deployed/not release ready. Current compiled code
80f9164fd0534fb5a0c148b9d0ad4e51d654e8d917932318d379c223e6f1977c,
manifest2d38efa69d90a9d6448d466336bd65d055d6a0783c4a58b36704f4d705e73b57;
service device-byte-credit-r12/QAcore-r12, all7apps still all-r3.24exact inputs,
independent whole service inventory matches. R11 remains prior scoped pass;
keep R10/R9 diagnostics/C7/legacy/nativeSDK/rollback/private state.

Only product source change is DeviceReplicaRound compact automatic status:
optional {brief:true} returns profile codi-device-replica-status-hint/1 with
actor/position/round/viewChange. Full {} reply keeps vote/prepared fields.
Exact-entry WeakMap probes this read; initial unavailable conservatively falls
back to full read on that transport, support rediscovered on reconnect. A busy
initial provider can therefore lose savings for that link; this is no authority
decision. Malformed hints/timeouts are not legacy evidence. No write retry,
acceptance/quorum/permission/key/floor bypass. Native signed view promises still
required; counters alone never advance native state. No extra capability slot,
app contract/framework/runtime/library/server or native deployment.

Status19 uses4real profiles/7RTC: same prepared state full9610 vs brief3185
signed wire bytes (~67%less), JSON4739 vs216. Existing full API, one legacy
probe/full fallback, fresh-link rediscovery, signed bogus high counter, malformed
hint, retained signed prepared view and exact-once real recovery pass. Initial
chunk-only fixture20366->12349 did NOT meet arbitrary50%wire target; retained
FAIL10/exact driver. Production-path inline negotiation then passes unchanged
50%target; do not relabel legacy cost. Actual auto17 SIGKILL/partition/invalid
promise/native binding recovery, full transport40, native14 (4units), private16
and one9profile/10launch/17RTC mesh26 pass on R12. Private initial positive
observer bind FAIL3 hit provider Global consensusJobs at accepted read grant2.
Existing30s idempotent busy helper now covers initial/restart/ordinary positive
binds too; negative ACL/saturation and signed write/permission probes unchanged.
All failures/exact QA sources retained.

One old-scope mesh burst window across8profiles:1,558,324signed bytes/13.275s,
versus R11observed1,863,470/13.653s. These are independent variable-concurrency
samples, not a controlled per-message/monthly comparison or efficiency proof.
Still far too high for limited-data acceptance. Added bounded QA RPC-input/
output categories (no content), in addition to signed-wire categories.

IMPORTANT newer profiling mesh FAIL16:26361signed bytes/20.044s at quiet
oracle. Stronger no-current-work/native-inactive entry still FAIL16:25350/
20.044s. Same4096byte allowance; NEVER call current quiet behavior accepted or
keep retrying for green. e/h show lastGrant:null, timed-out credit requests,
cooldowns, failing notice/head retries; counterpart control rejected counters
nonzero. Actual control rejection reason is not currently exposed. New unit
device-byte-credit-refusal-r12 (OBSERVED) uses1Chrome/fake peer/real controller:
authorization failure returnsfalse/no reply/no allocation; subsequent authorized
request grants16384bytes; all leases0. This characterizes a mechanism, NOT a
verified native-binding race or fix. Next bounded metadata-only control-error
diagnostics and deterministic actual native binding/control ordering proof;
choose safe refusal/backoff handling from evidence, never silent authorization.

Current aggregate device-byte-credit-milestone-r12-result.json is PARTIAL:
132successful current assertions +unchanged compiler9/exact rebuild/driver/source/
cleanup/preservation; also binds genuine quiet failures and unit observation.
releaseReady=false, lowDataEfficiencyAccepted=false. Latest mesh driver supports
nullable traffic stats for legacy QA (small guard after failed run, exact failed
driver retained); current failed source snapshots are bound independently.
All test handles terminal/owned profiles/fixtures/charges cleaned, QA driver
65138 reusable. No cleanup except temporary rebuild removal this turn.

Read-only live preservation-r12 PASS SDK36868e65/config19f15f85/sourcebd8 and
root/blog/browser files/prototype/private keys/accounts/files/floors/paused-empty
chat. NOT role readiness: Root4 expired/steward failed, explicit Root5 recovery
approval pending and old helper pre-expiry-only. No signing/restart/deploy/
Caddy/router/ports/boot/source pull. Whole mixed-link/global/relay/legacy limits,
islands/joint members/long-gap/chess/PoW/8k/WAN/audit/rollout unfinished. Private
backup follows; preceding7a0f9ea holds R11. Keep full goal intact.

R12 backup supplement — private main569f54acf97b374249357772c524e22dbea3b0a0
holds224physicalfiles/8757571bytes, source-proof1dbb7cae57e1dda1b961ba392f273a7b226431bfe187b7172e1a16097ff00195.
Every byte/closed inventory/current source parity/remote main/clean clone
verified by device-byte-credit-backup-r12-result.json; dedicated QA driver has
0sessions. This receipt/handoff supplement follows as proof-only Git change.
Current candidate stays PARTIAL/not deployed; do not skip quiet failures.
Next add bounded credit-control error reasons, reproduce actual binding timing
and choose refusal/backoff handling only from native evidence. Unit no-reply
behavior is observed, not a confirmed cause/fix. No more generated cleanup
this turn, preserve currentR12/previousR11/R10/R9/C7/legacy/native/private state.
Full goal active, Root5 approval still pending, live code/data unchanged.


## R14 native binding/credit refusal repair — 2026-10-26

Full goal ACTIVE, source-only/not deployed/not efficient or release ready.
Current code6f4867ea2b33a997ce769d57271da27c8fecb376dd12d34e1c8cb91e1ed4127e,
manifest477014ecd2d0d5f0832181862aba77352c64050963e9872139fdf1a97909b6b6;
service device-byte-credit-r14/QAcore-r14, apps all-r3 unchanged,24exact public
inputs. Complete independent service rebuild byte-identical.

R13 diagnostic-only code3fdd849f adds max8metadata-only control failure records
(stage/reason160chars/exact peer/nonce/channel/time; no body), cleared on close.
Exact old controller source archived in controller-r13-source receipt. New
2real Chrome/IDB/ECDSA/RTC test holds the actual reciprocal binding verification
before client cap commit. A genuine signed credit request is denied with
'A fresh native channel binding is required for receive credits', allocates0,
but no reply is sent. Releasing the hold runs original WebCrypto verify and
commits binding; caller still waits15006.5ms for timeout plus bounded cooldown.
Same actor/key works afterward. This verifies a real ordering problem; it does
not prove every older mesh quiet failure had that cause. R13 wire-unchanged
mesh also passed one quiet sample; no relabeling older failures.

R14: a well-formed credit request in an already-open pinned scope that fails
fresh native authorization now receives generic signed grant/null/0bytes/0TTL
with1000ms retry. No data allocation, permission or denial reason is disclosed.
Every later request reauthorizes; closed/unknown/malformed/control-budget abuse
behavior stays enforced. Response itself consumes control allowance. No auto
application write retry. Actual same held-verification regression PASS5:44.8ms
refusal sample while signature still held,0download allocation, real verifier
then commits original reciprocal actor, fresh read succeeds. Do not present
loopback latency as WAN guarantee. Unit1Chrome/fake peer proves9refusals0data,
ring8/truncation160/no body, unauthorized data rejection, later authorized16KiB
grant, cleared diagnostics and all leases0; unit scope separate from native5.

R14 native14/private16/default3 PASS. Native14 includes4units and now compares
creditsDenied before/after the actual pause (earlier auth denials cannot satisfy
the pause oracle); exact earlier driver retained. Negative ACL/write revocation/
held-node publication/regrant/rejoin/absent-leader recovery remain genuine.
Mesh26 twice PASS with9profiles/10launches/17RTC/0v86 and strict drain/unchanged
4096byte quiet oracle. Accelerated20.060s and production-round20.043s windows
sent0signed application bytes, excluding RTC/IP/TURN/assets/long-term upkeep.
Production-round probe uses default scheduler tick1000ms/step60000ms ONLY;
fixture peer sampling/10s allocations/6s credits remain QA overrides, not a
complete production/mobile/WAN test. Native race uses solo policy for2browsers;
full mesh/private tests keep actual4voter quorum. All owned fixtures/charges
clean; test handles terminal. Current aggregate byte-credit-milestone-r14 PASS
binds90current assertions plus unchanged compiler9/exact build/driver/source/
cleanup/live-preservation and prior native-race proof. releaseReady=false,
lowDataEfficiencyAccepted=false. Prior R12quiet failures remain retained.

IMPORTANT active cost still high: one8message/8profile burst used1,736,327
signed bytes/17.473s accelerated; default-round cadence observed1,421,356/
14.251s. RPC profiling identifies validator/activity as largest raw bucket:
12successful calls/184200input JSON bytes in production-round sample;72brief
status calls. These are variable-concurrency samples including votes/history/
retries, not isolated message/monthly costs. Next reduce duplicate full-batch
activity announcements and status work during local batching, preserving native
validation and the earlier absent-leader wakeup/withheld-value recovery fixes.
Global/durable/relay/legacy budgets, real loss/WAN, general islands/joint members/
long-gap/chess/PoW/8k/audit/rollout remain; do not call whole goal complete.

Read-only live preservation-r14 PASS keeps SDK36868e65/config19f15f85/sourcebd8,
root/blog/browser files/prototype/private state/paused-empty Chat/Rooms. NOT
role health: Root4 expired/steward failed, explicit Root5 recovery approval
pending, old helper pre-expiry-only. No signing/restart/deploy/hosting/router/
boot/source pull. Current backup follows; prior d0ca2be holds R12 source/proof.
After backup verify, prune never-installed R10/R11/R12 byte-credit service+QA
outputs using complete backed catalog inventories. Keep currentR14/R13old-race/
R9old-lease/C7/legacy/nativeSDK/usable rollback/private state.

R14 backup/cleanup supplement — private main3e482ad9ce4442b6c65791dbe68b21a57911ea26
holds248physicalfiles/10380249bytes, source-proof4d06e3d6d8563383624c4fa27568a0504842485a9f6e84e20605c55203b50476.
Every byte/closed inventory/current source parity/remote main/clean clone
verified; dedicated QA driver0sessions (backup-r14 receipt). Cleanup PASS
removed6never-installed superseded byte-credit R10/R11/R12 service/QA outputs,
3301668bytes, against complete backed inventories/catalogs. Their historical
sources/proofs remain in private Git; do not reference removed outputs as
current. Retain currentR14, R13 exact before-native-race, R9 old lease before/
after unit, C7/legacy/nativeSDK/usable rollback/private state. Receipt/handoff
supplement follows as proof-only Git change; no live deploy/sign/restart/pull.
Next duplicate batch activity/status traffic reduction with absent-leader and
native verification/recovery safeguards; full goal and efficiency unfinished.


## R15 bounded activity delivery — 2026-10-26

Full goal ACTIVE; current source-only code c569fec7b9b30b8b2717e7251f62a3a447c4e8c7eb0c2d6e6cbe691c615ad837,
manifest fe0a61ad3d13e111f366b559ed49016fbc2b8ccc99f3498704d869fadc4c7cf8.
Service/QA device-byte-credit-r15/core-r15; all-r3 apps unchanged. Exact-entry
current-batch activity knowledge suppresses repeats after native validation or
reported receipt, with bounded backoff and16KiB metadata lifecycle. Receipts
never count as votes. No new wire protocol/runtime/backend/app contract.

Aggregate device-byte-credit-milestone-r15 PASS140: activity24/mesh26/auto17/
transport40/private16/native14/default3 +exact builds/live preservation. Same
focused browser test oldR14sends6activity/newR15sends3; mesh12->6/184200->92100
raw input bytes. Total burst1348490signed bytes/17.944s (8messages/8profiles),
still too costly; quiet20.105s0signed bytes excludes RTC/IP/TURN/assets/long
maintenance. Production round tick/step only; other QA limits remain overrides.
No physical3G/fiber/loss/WAN/global efficiency acceptance.

Initial private FAIL12 retained: holding one response let a timeout retry finish
before read revocation. Fixed QA holds all retries with abort cleanup and final
PASS16requires2real node requests, reader floor7before/after fresh publication
refusal. Native authorization unchanged. Intermediate QA/source and old failure
preserved; see active-system/evidence/device-membership.md (relative evidence/
when already inside active-system) for exact scope/receipts and exclusions.

Read-only live verify PASS keeps SDK36868/config19f/sourcebd8/root/blog/files/
prototype/private state/paused-empty chat. NOT role readiness: Root4expired,
steward failed, Root5approval pending; old helper pre-expiry-only. No signing/
restart/deploy/Caddy/router/boot/source pull. All test handles terminal and owned
fixtures/profiles/charges clean; ChromeDriver19515has0sessions. Private backup
follows, preceding a8ab428 holdsR14. Retain R15current/R14negative baseline/
R13native-race/R9lease/C7/legacy/nativeSDK/rollback/private state; no extra pruning.

Goal ledger preserves fast fiber AND3Gbackhaul per-device budgets/cadence and
relay consent; no guaranteed sub1ms or automatic relay duty. Fixed quorum can
still stall when voters unavailable. Next remaining repeated status/history/
verification traffic and real production mixed-rate/loss; global/durable/relay/
legacy limits, islands/joint voters/long-gap/chess/PoW/8k/WAN/audit/rollout remain.


R15 backup supplement: private main c6bcd26f708f1ee3288230972e272c98d55325bd
holds270physicalfiles/11495896bytes; source-proof
eb092ae40445be1ffccab83627d28a8e1dc62dbec97f6550634650ccf17e671f.
backup-r15 receipt verifies every byte, closed inventory, current source parity,
remote main, clean clone and0owned Chrome sessions. This supplement records the
verified source/proof commit; no live pull/deploy/sign/restart. Full goal remains
active; R15only scoped proof, no mixed-link/global efficiency acceptance.


## R16 local batching and asymmetric production budgets — 2026-10-26

Full goal active; current source-only d06df7c446186ef14d64f02f6a4ee491638c43bd2854c99664e59fcc9bafbac7,
manifest3666f165fd3edabeaf439876735e28855aad0ff4c70f0076050111559a5136b7.
Service/QA byte-credit-r16/core-r16, all-r3apps/24public inputs unchanged; exact
independent rebuild. Held local batch with no incoming hint/retained work/view
skips status polling: same-driver R15three pulses6status/19110signed bytes vs
R16zero. Incoming validated activity reconciles normally; native safety unchanged.

Milestone-r16 PASS101scoped: focused26/mesh26/auto17/private16/production-limit
asymmetric16(includes4units). R15manual transport40/default3/native14not rerun or
counted on R16. Mesh8message burst1418198B/17.266s varies from prior1348490B;
no overall reduction/efficiency claim. Quiet20.043s0payload excludesRTC/IP/TURN/
assets/long maintenance. Production-limit asymmetric test uses actual default
minute budgets, round defaults and60s credits, later slow reader128KiB/minute,
8192B/sup/32768B/sdown+300/650ms injected send delay. Fast paths continue; slow
reader verifies2at70.429s and3at76.651s, original IDs once. Retain75s FAIL5;
bounded240s observation records progress without raising cap. Not packet loss/
physical3G/fiber/WAN/general discovery/scale proof. Earlier QA counter collision
and false-toggle fixture failures/exact sources retained; product unchanged.

Live preservation-r16 PASS SDK36868/config19f/sourcebd8/root/blog/files/prototype/
private state/paused-empty chat, NOT role health: Root4expired/steward failed,
Root5approval pending, old helper pre-expiry-only. No sign/restart/deploy/Caddy/
router/boot/pull. All test handles terminal;0QA sessions/owned resources clean.
Canonical details/receipts: active-system/evidence/device-membership.md (evidence/
when already inside active-system). Private backup follows;0255a305holdsR15.
After backup verifies, remove only retired never-installed R14service/QA against
complete outputs-r16 inventories. Keep R16current/R15batch comparator/R13race/
R9lease/C7/legacy/nativeSDK/usable rollback/private state. This supersedes older
instructions to retain R14for an already-completed activity negative control.
Next global/durable/relay/legacy byte budgets, repeated history/verification and
loss/reconnect/capacity-aware routing; full islands/joint voters/long-gap/chess/
PoW/8k/WAN/audit/rollout still unfinished. Keep full goal active and chat paused.


R16 backup/cleanup supplement: private main bfadb720eb00f9f8d801268fc4398310941fb8a9
holds289physicalfiles/12529831bytes; proof
242f68d98a979a395be81028c7093434fa593f19caa5414720f94194602a0f78.
Every byte/closed inventory/current source parity/remote main/clean clone/0QA
sessions verified. Cleanup-r16 PASS then removed only two never-installed
R14service/QA outputs,1106672bytes, against complete backed catalog inventories.
Their sources/proofs remain in private Git; earlier R14build paths historical.
Keep currentR16/R15batch comparator/R13native-race/R9lease/C7/legacy/nativeSDK/
usable rollback/private state. This receipt supplement changes no live state.
Full goal active; next durable/global/relay/legacy budgets and routing/loss tests.


## R18 durable device/channel allowances — 2026-10-26

Full goal ACTIVE; current source-only afa063100827d4496d506ada6d9d5dd63a45db5bdcaf0c12afe5ca56383b4ad4,
manifest8abbba76ef3642bf1c40ed52d9330809e897fc1bd9c9b2b10632b1a29de6c843;
service/QA r18/core-r18, seven apps all-r17 rebuilt for shared allowance UI.
Directory DB keepsname, upgrades schema1->2 with trafficPolicy/trafficUsage;
strict global+channel reservations/actual fresh settings, no refunds, canonical
versioned global policy across tabs/channels/account scopes. Legacy unmetered
send/signed receive rejected when traffic owner attached. Local costs confer
no read/write/voting permission. Old schema1 readers close/fail closed; never
reset/downgrade DB. Future active-chat rollback compatibility remains required.

Milestone-r18 PASS100 scoped: durable18/native17(includes4units)/auto17/idle2/
mesh27/private16/default3. Actual anonymous two tabs/native oldR16migration/
SIGKILL/reopen/cancellation/CAS/partial grants/fail-closed. Real signed-in tabs
NOT verified; another-tab raised channel limit can still be conservatively
refused until old runtime reloads. Full relay opt-out/row-cap stress/corruption/
throughput/WAN/mobile/8k not proven. Current scope details and exact failures:
active-system/evidence/device-membership.md (evidence/inside active-system).

R18onChange self-wake repair has actualHost old2/new1core negative control.
R17quiet10727/R18quiet9945andtraced9945failed4096B oracle remain retained.
Runtime diagnostic PASS26quiet3342; strengthened entrance has explicit real
queued-wake oldtrue/newfalse probe, drains validator due/version intent and
passes mesh27quiet0/20.064s without raising4096B ceiling. Not proof of long-term
idle cost or every earlier failure's cause. Burst1352339B/15.349s still costly;
lowDataEfficiencyAccepted/releaseReady/wholeGoalComplete false.

Live preservation-r18 PASS SDK36868/config19f/sourcebd8/root/blog/files/prototype/
private state/paused-empty chat, NOT role health: Root4expired/steward failed,
Root5approval pending; old helper pre-expiry-only. No sign/restart/deploy/hosting/
router/ports/boot/pull. All handles terminal/owned profiles/charges clean,0QA
sessions. Private backup follows;7c4d43bholdsR16. After verify, retire only
never-installed R15service/QA; keep R18current/R17self-wake/R16migration/R13race/
R9lease/C7/legacy/nativeSDK/usable rollback/private state. Next actual registered
tabs/cross-tab preference refresh/row-cap/fault/throughput/rollback, fresh mixed
loss/WAN, full relay duties and islands/joint voters/long-gap/chess/PoW/8k/audit/
reviewed rollout. Keep full goal and live paused-chat policy intact.


R18 backup/cleanup supplement: private main d1ae36be3ce5582c4776b8f5ee5ca645e5b6bada
holds331physicalfiles/20561955bytes; source-proof
4789d3c8864dde63aeb96ea17daf28fe4ffc945a727122127905b0ba1f3563c9.
Every byte/closed inventory/current source parity/remote main/clean clone/0QA
sessions verified. Cleanup-r18 PASS removed only two never-installed R15service/
QA outputs,1111858bytes, against complete backed catalog inventories. Sources/
proof remain private Git; old R15build paths historical. Keep R18current/R17
self-wake/R16migration/R13race/R9lease/C7/legacy/nativeSDK/rollback/private state.
This supplement changes no live source/state or private records. Full goal
active; actual registered-tab and preference-refresh/fault/throughput/rollback/
relay/routing/islands/joint voters/long-gap/chess/PoW/8k/WAN/audit/rollout remain.

### Cellular relay capacity investigation — 2026-10-29

The phone session beginning `0738188a` could not connect during the ten-browser cellular test. Its messages remained pending locally. The shared TURN relay had 32 simultaneous allocations and a fresh relay-only browser attempt returned TURN 486 allocation quota reached while 32 proxy connections were active. This explains a concrete capacity failure, but successful delivery after the fix still requires an outside-network test. The original test timed out and its temporary test channel reference and automated browser profiles were removed; the phone's pending messages were not shown to have been delivered.

A managed `text-128/1` profile is live. It allows 128 allocations (not necessarily 128 people), 256 proxy connections, 32 KiB/s per allocation and an aggregate reserved ceiling of 4 MiB/s; actual use depends on traffic. Its private relay-to-relay-only namespace and peer restrictions are unchanged. The new five-file operator manifest is `3d2f88f35109d7b052fef3a943776bf10d2cdbd198294bc1778dd1210f6ec162`; relay config SHA-256 `35c5c94f0c364a0982e282eaf8d236fbf82bf2feddfb2128cf7db6468de84a5b`. Managed activation receipt `.build/checks/relay-128-profile-apply-result.json`; root receipt `/srv/codi-relay/text-profile-apply-1793256130055877802-result.json`. Certificate refresh job was updated and executed, timer active; native website/services and hosting pins remained unchanged. Real disposable relay lifecycle checks, including activation and rollback of this profile, passed in `.build/checks/persistent-relay-result.json`. The old profile and operator remain available for rollback. Restage the exported package under `/tmp/codi-relay-128-r1` before running `scripts/stage-relay-128-profile.py` rollback; its migration journal handles interruptions. Monitor the new profile's real traffic and reconnect behavior; capacity increase alone does not prove chat or 128-person scale.

### Registered server chat and Stockfish work in progress — 2026-10-29

The current user direction is registered accounts only, operator-offered channels, server-routed chat, and a single-purpose Chess app at `served_apps_public/chess`. The root login gate and password/username policy are live in `native26-required-login-r1` (manifest `f8e5317bd815d359cd9943da51ecc693dd657e0101b2fef468b93b9bd969cf46`); the new Chat and Chess work below is not yet deployed. Do not replace `/desktop`.

In `active-system`, the server-frame transport retains signed channel frames and has passed real registered Chrome tests for delivery, dropped connections, and a restarted browser catching up. Operator official chat custody and a sole-validator writer have passed unit tests for identity binding, bans, invalid signatures, stale authorization and idempotent submissions. `scripts/official-chat-browser-check.py` has passed a compiled simplified Chat view sending through the real test issuer and official runtime, a runtime restart, and a second registered browser independently recovering the accepted message. The writer and custody/runtime changes are not installed on box-webhost. The official service package candidate is `.build/official-services/official-chat-server-r1` (manifest `c9ea7b6f756d56a7259592d69af0ca709619c43886a8f4d8dc64369175cd7f28`). The separate compiled Chat candidate is `.build/chat-offered-build-r2`; account-discovery and device-history candidates are under `.build/shared-services/server-channel-discovery-r1` and `.build/shared-services/official-server-chat-r1`.

The Chess app uses the existing desktop channel API with separate game and chat channels and includes Stockfish 19 lite WASM, loaded only for an assigned player. Real-browser component and engine tests passed. `scripts/server-route-history-check.py` also passed two Stockfish browser players and a registered spectator exchanging legal moves and separate chat over test server WebSockets. That test uses a permissive fixture channel checker and a browser validator: it does not prove operator-offered production admission, server-durable game history, a complete game, or release readiness. The real official reader and replay currently accept chat only; the game needs an authorized durable path and an operator-provisioned match before the app can display a shared live game. Do not describe it as deployed or durable yet.

Remaining immediate work: package the current frontend and native coordinator safely against the live pinned release; allow only registered accounts and operator-offered channels; install and exercise the official chat writer with scoped service custody; build, authorize, persist, and recover the Stockfish match and its separate chat; test the desktop app loader, login, security, pending/delivery and cross-browser recovery against live; only then declare this milestone finished. The user's newer instructions supersede older 8,000-person and user-created-channel requirements for this milestone. Keep the broader goal active.

### Live registered chat and featured Stockfish — 2026-10-29

The root site now runs managed release `/srv/codi-connected/releases/native27-server-channel-r4`, manifest `71f1ba31c228c67af14fd6df28c7c5207d24cbc794616f2ed7356658d3becd26`; managed config SHA-256 `b03111b78cf97e853bba10914b9ed7153399a1136bd23acc0fdf3069db0f648a`. Login is required; public-channel frame relay restricts joins to registered identities and operator-offered channel/genesis pins. General chess chat is server-validated and server-stored, with pending retained until verified acceptance. SYSTEM remains available in the background but is hidden from the regular Chat channel list. The Chat and Chess application sources are in `active-system/served_apps_public/chat` and `desktop-preview/served_apps_public/chess` respectively; Chess discovers a signed official game reference and uses separate game/chat channels.

The official backend is `/srv/codi-connected/official-services/chat-chess-r4`, manifest `a547f00208976d5755c3e65e9f46b4badf944d11c3b3e1d72a2c603abffea8c4`, with private Python environment `/srv/codi-connected/venvs/official-chess-r1`. Root receipt `/srv/codi-connected/official-chat-chess-activation-result.json`; previous unit backup `/var/backups/codi-official-before-chat-chess.service`. Managed native activation receipts `/srv/codi-connected/server-channel-activation-result.json` and `/srv/codi-connected/server-poll-activation-result.json`; the current renewal backup is `/var/backups/codi-renew-before-server-poll.service`. Preserve existing account data and private keys.

`codi-featured-chess.service` is enabled and runs native Ubuntu Stockfish 16, skill 0, one thread, 250ms of thinking and five seconds between moves. It signs moves with two service-owned private keys, independently verifies chess rules and stores accepted blocks; the game uses General chess chat as its separate conversation channel. Browser and server chess rules matched across 2,400 generated plies; real signed Stockfish histories, bad signatures/turns/positions, restart recovery, official service packaging, and the compiled Chess workflow passed local tests. On the actual public site, two registered browsers exchanged messages in 7.3 seconds and the Chess-to-Chat path in 7.0 seconds after the polling correction. Ten registered browsers exchanged one message each in 29.7 seconds, including a browser on i36 public IP `104.180.210.36`. i36 and the server use the same public /29, so this is not a fully independent Internet-provider test. Exact temporary test accounts were removed; test messages remain in signed official history.

Public source/native backup packet `tools/codiserver/server-chat-chess-20261029-r1` was pushed to private `box-git:/srv/data/git/ksu.codes.git` main commit `2f0db7944ad1a790aa45534384cc9d6775d4b189`; source-proof SHA-256 `49b3899796514b065d0d6ebb8a19b90e31a0ed5b2dc13fccb6314461765eae1b`. It includes no service keys or account databases. Full goal remains active: verify a complete game and restart/recovery and test from a truly independent Internet connection, improve moderation/user names and honest delivery states, and qualify broader stability/scale. Current server replay scans history and is not yet qualified for large histories or 32–128 simultaneous users.

### Live replay and account restrictions — 2026-10-29

The finished Stockfish game reached checkmate at 130 plies. The live Chess app now exposes Previous, Next and Latest controls; a fresh public browser recovered the complete board, stepped backward and returned to the latest position, and sent a chat message received by another registered browser in 5.9 seconds. A separate packaged test recovered a complete signed two-player checkmate for a spectator after official-storage restart.

Current managed desktop release `/srv/codi-connected/releases/native27-ban-review-r1` has manifest `812a7a07d14e6ce13c4020edd65f8de3a9edaa380b869bee7ca629741892a77a`, config SHA-256 `442c730b3151ed861f58be0bf3ad5930053fdbef2730e5dde57701ad9b7a5891`, and receipt `/srv/codi-connected/ban-review-activation-result.json`; renewal unit backup `/var/backups/codi-renew-before-ban-review.service`. The official service now runs `/srv/codi-connected/official-services/chat-ban-review-r3`, manifest `3dcfce991f688af908f13ca808ba248c17d4e04cfb90014ba982ba3553eb7ac0`, receipt `/srv/codi-connected/official-ban-review-activation-result.json`, prior unit `/var/backups/codi-official-before-ban-review.service`. Keep private state, keys, account records, and previous release for rollback. A rollback to code without signed restriction epochs/review must first disable the ban operator shortcut: old clients can retry denied drafts automatically.

The root-owned `/usr/local/sbin/codi-chat-admin` supports `list`, `mark-message ID`, `mark-author ID`, `ban USERNAME`, and `unban USERNAME` for General chess chat. Spam marks are signed and retain the expandable original. Account restrictions deny posting while still allowing channel reading, and publish signed changes for known device authors. A locally saved draft that was rejected, or was authored on a known device while disconnected across a restriction and release, is flagged for review; it is only sent on explicit Resend. First-seen devices of previously restricted accounts also get a review barrier. Actual public-site test `scripts/live-ban-review-check.py` passed an offline draft across operator ban/unban and manual resend; the exact disposable test account and restriction metadata were removed. Tests also cover signed spam markers, unknown devices, and an unban race. This is operator access through SSH/sudo, not a browser admin UI, and restrictions presently target the General channel rather than all future channels.

The moderation/resend source and sealed native artifacts are also backed up on `box-git:/srv/data/git/ksu.codes.git` main at `d9a4172abb61443051c088ffbc1f940f2443fbae`, packet `tools/codiserver/server-chat-ban-review-20261029-r1`, source-proof SHA-256 `fe36582071e275da0d895ce9e066a16517941b6c33c34f5ec8b127094ca968b6`. The verified temporary backup checkout, unused host staging, superseded server-channel releases R3/R4 and obsolete moderation package were removed; the live release, its immediate rollback and the official service's prior unit remain.

### Continuous featured games — 2026-10-29

The Chess app now labels the match “Stockfish vs Stockfish” and offers “Watch current game” when a different featured game is available, without interrupting someone reviewing a finished game. A continuous native runner waits 60 seconds after the game ends, provisions a new signed game with the same separate General chess chat, and resumes after restart. The previous invitation and signed blocks stay in the official database. There is no archive picker yet; a browser already viewing the old game can continue reviewing it until it switches.

Live frontend `/srv/codi-connected/releases/native27-chess-rotation-r1` has manifest `85d679fc3aed1db710a88a56e5f09a69ed333107401365484ab5a5941398d665`, managed config SHA256 `1f0ca8a1c5ed35de919e89bde9d5382ef79eb301ef012db0dacbfb6ab22ea172`, root receipt `/srv/codi-connected/chess-rotation-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chess-rotation.service`. The runner uses `/srv/codi-connected/official-services/chess-rotation-r1`, manifest `9df30da4c057c9307d3263704342cc65aa3c273b3e89019bb1fdc1dd54d3778c`; unit backup `/var/backups/codi-featured-before-chess-rotation.service`; receipt `/srv/codi-connected/chess-rotation-runner-activation-result.json`. The official API continues using chat-ban-review-r3. The old game CcnJeSO-QkJ7eIR2sz_uhgTE_avpAqG3Fa7zWygVulY remains archived with all 130 blocks, and the runner published a new game znd5Rh3wIJr7TigUO_amCJxvqo1q0WjhDgKj7CvZBrU and made moves.

Local real-engine test `scripts/featured-chess-rotation-check.py` passed unfinished-game refusal, game completion, automatic rotation, idempotent retry, preservation and runner restart. Compiled browser fixture passed choosing the new game, replay, chat and disposal; full local official-runtime browser check passed game recovery after restart. Two fresh public two-browser runs passed chat, chess board/replay and separate chess-chat delivery; the second loaded the new game. Observed chat-to-other-user times were 29.1 and 3.4 seconds, so do not claim consistently low latency. All four exact disposable accounts and their account restriction metadata were removed; synthetic signed test messages remain in General chat. The public checks were not independent-WAN tests. A future hardening pass should make metadata generation crash-atomic and test interruptions at each key/meta/registry publication step; current retries and ordinary restarts pass but crash at an in-progress metadata write has not been proven safe. Full goal remains active.

### Featured game crash recovery — 2026-10-29

The active featured Stockfish runner now uses `/srv/codi-connected/official-services/chess-rotation-r2`, manifest SHA256 `3847e90db5f35b2106347d7e6ab0e299cdfdfa73190cc80103299aaed850b238`. Root activation receipt `/srv/codi-connected/chess-crash-safe-activation-result.json`; previous unit `/var/backups/codi-featured-before-crash-safe.service`, and previous `chess-rotation-r1` package retained for rollback. The managed desktop release/config are unchanged from the preceding rotation entry. The runner restarted and continued the same live game; its post-restart journal showed heights 27 and 28. Official API and featured runner both active; root and `/desktop/` returned HTTP 200.

Game provisioning writes keys and metadata through private 0600 temporary files, fsyncs each file, renames into place under the existing exclusive provisioning lock, and fsyncs the directory. Interrupted matching temporary files are checked and removed on retry. `scripts/featured-chess-crash-check.py` killed actual child processes at eight boundaries: partial write, each of three rename operations, before/after channel enrollment, and before/after publication. Each retry preserved the old game, produced exactly one successor and cleaned interrupted temporary files. `scripts/featured-chess-rotation-check.py` also passed real Stockfish rotation and restart. This simulates process death, not physical power loss; fully published keys orphaned by a crash before metadata publication may remain in the private key directory and are not automatically removed.

Code, compiled Chess app, the current official-service package and native release manifest are backed up in private `box-git:/srv/data/git/ksu.codes.git` main commit `94672592464091a320b65d0de5ac974d1addff26`, packet `tools/codiserver/server-chess-rotation-20261029-r1`. Source-proof SHA256 `6b428c287c4c91e1c889d7e64310a2d991e60c6640d9231b047391bc441b319b`; the remote proof and all 80 declared files were re-read and verified. No private service state or key material is included. Full goal remains active.

### Registered sender names — 2026-10-29

Chat and the separate conversation in Chess display the registered author's issuer-verified name for newly accepted messages. The server stores the name against the already checked account-to-author binding in the same transaction as each accepted message. A bounded `/official-channel?channel=...&authors=...` lookup exposes only names for that public chat channel, not account subjects; names are server-authoritative metadata delivered over HTTPS, while signed message validation remains separate. Old actors have no stored name until they send another accepted message and retain the participant-ID fallback. A name lookup outage likewise leaves the fallback; it does not block chat. The apps share `active-system/served_apps_public/shared/official-author-names.mjs` and dispose their resolver with the view.

Current managed release `/srv/codi-connected/releases/native27-author-names-r1` has manifest `7f2df2c7c0bd43aa4d7327fbdeabdf97d117a67d132f48472fee985523a2e999`, managed config SHA256 `1ed7e5ea4b8cb415c82824e20447c642f448830a35ffb38c414ada9b557d5cc0`, receipt `/srv/codi-connected/author-names-activation-result.json`, and renewal backup `/var/backups/codi-renew-before-author-names.service`. Official API runs `/srv/codi-connected/official-services/chat-author-names-r1`, manifest `c566e5abc5465b85dead44f8b3858e4b12ecda773166ebac2e238a1d5c7ca901`, receipt `/srv/codi-connected/official-author-names-activation-result.json`, prior unit `/var/backups/codi-official-before-author-names.service`. Provisioning created an additive `official_chat_names` table; old code can ignore it. Featured chess still runs the separate crash-safe rotation package. `/desktop/` is unchanged.

Nine writer tests passed, including lookup bounds, no name before acceptance and prevention of another account replacing a bound actor's name. The full packaged registered-browser test passed an author name on a signed spam-marked message, blocked/offline draft review, chess recovery and complete game replay after restart. Public `scripts/live-offered-apps-check.py` passed names in both Chat and Chess, two-way chat, current board and replay. The first server-accepted message reached the other browser in 12 seconds; the Chess message arrived in 3.6 seconds. Exact disposable accounts and associated actor/name/restriction records were removed; their signed test messages remain. The older `official-reader-lookup-check.py` fails at registration because its fixture uses a username invalid under the current policy; it did not exercise the reader. Independent WAN, long histories, archive picker, and consistent chat latency remain unproven.

Private `box-git:/srv/data/git/ksu.codes.git` main commit `4e74229454e6b0f7906628c1e9a32da37f555d6a` contains packet `tools/codiserver/server-chat-author-names-20261029-r1`. Source-proof SHA256 `155f7f0f48b22037f5b65d976343f2d7ee085e9c0268a5bc6c6ca1b9435330b3`; the remote proof and 76 declared files were re-read and verified. No account databases or private keys are included. Full goal remains active.

### Chat latency investigation and incremental server reader — 2026-10-29

Current desktop release `/srv/codi-connected/releases/native27-author-batching-r1` manifest `1d838cbb8530a81e8299a4a88949020ca2dae39417b702e4e60a8c7c4ae765b2`, config SHA256 `36382114fedec369da30c63d03fa1bbaa3375e263b87ce1000e60eb5b41a5758`, receipt `/srv/codi-connected/author-batching-activation-result.json`, renewal backup `/var/backups/codi-renew-before-author-batching.service`. Current official API `/srv/codi-connected/official-services/chat-reader-cache-r2` manifest `79defacf1a16e74d77ab65ab461b2ead897676b5e3a0e99d87587eda7c42fd01`, activation receipt `/srv/codi-connected/official-reader-cache-r2-activation-result.json`, prior unit `/var/backups/codi-official-before-reader-cache-r2.service`. Featured game runner remains crash-safe rotation r2. Root and `/desktop/` continue as before.

The official sender wakes promptly on new locally queued chat and does not defer a due poll when state changes; an additional queued send during an in-progress poll is remembered. The name resolver requests up to 32 authors at once, serially per view; previously it could launch multiple batches concurrently. The server accepts the bounded 32-author form. Local real-issuer browser tests passed registered send, prompt-start assertion, signed spam and names, blocked/offline draft review, chess and restart. `scripts/official-author-names-batching-check.mjs` proves 64 actors cause two sequential bounded requests and missing-name caching.

The official reader used to invalidate every channel's verified-head cache whenever any SQLite table changed, including a chess move. It now fingerprints the exact channel policy and stored block bytes; identical bytes reuse a previously verified result, and a byte-identical verified prefix permits incrementally verifying up to 64 appended signed blocks on a copy. Altered older bytes force full replay; an invalid suffix cannot alter the cached verified floor. The full replay remains the fallback, and a database snapshot/version race still retries instead of returning unchecked data. Writer tests cover unrelated writes, valid append, invalid suffix and changed older block; the concurrent corruption-race test passed. `scripts/official-reader-cache-check.py` on 35 real signed blocks measured 0.012s for ten unrelated-update checks and 0.023s for five incremental appends, versus 1.214s for ten full replays; isolated local measurements, not network latency. Fingerprinting still scans all stored channel bytes and the writer still fully replays history; neither is qualified for very large histories.

Live two-browser trace before sender wake took 8.3s from Send to first submission; one sample after took 6.2s and total delivery 11.5s. A first ten-browser run with unbatched name lookups failed its 180s bound with eight senders accepted and 503 responses. After batching, the full-site ten-browser run passed in 102.4s. A chat-only run (browser test blocks guest and speech assets, no production change) before reader caching failed with ten accepted but one browser behind at 180s, with 503/409 responses. With reader reuse it passed in 97.3s but still had 503/409 retries. With the incremental reader, the equivalent chat-only run passed in 68.6s with all ten receiving all ten and zero failed official requests reported. These individual runs had different, growing test histories; do not treat them as a controlled benchmark or proof of consistently low latency. Nine browsers were on the workstation and one on i36 (`104.180.210.36`), which shares the server's /29; independent WAN remains unverified. Test accounts, associated author/name/restriction metadata and browser profiles were removed, but signed test messages remain in General chat. The browser still appends and verifies recovered blocks individually; investigate that catch-up cost and actual device CPU next.

Private box-git main `45862a5689dcf8e91679d32a73aecbb53e0dcf68` holds the latest packet `tools/codiserver/server-chat-incremental-reader-20261029-r1`; source-proof SHA256 `78dcb3074858c4f19d9e4b654831554fc6ed5c5ec0fe1af7256cb18fe32f7b54`, remote proof and 59 files verified. Earlier related packets: chat wake commit `b85bd8a338703f3e0d7a096684e91638916d802f`, author batching `34a8f8f81db51f67d5e481ab745314f7f4b749d5`, and reader cache r1 `0a9fc7905592ca4ccf3a66b5b18ca99565135bb4`. These contain no private keys or account databases. Full goal remains active.

### Browser catch-up and busy retry — 2026-10-29

Current desktop release `/srv/codi-connected/releases/native27-catchup-busy-r1` has manifest SHA256 `730828eadd993ec403aa5069eb3fa8f81600aa90abdd17a59b822ca43ff14e83`, managed config SHA256 `f9b09b990b226b69c08ca1003227c9a98d469b95b7b79fae6ad5bc12495b4d80`, activation receipt `/srv/codi-connected/catchup-busy-activation-result.json`, and renewal backup `/var/backups/codi-renew-before-catchup-busy.service`. The official API runs `/srv/codi-connected/official-services/chat-busy-r1`, manifest `9526dd94469ad6eee847ed0518b1ca8f4894c62637fb0c5a3a68ed76256828da`, receipt `/srv/codi-connected/official-chat-busy-activation-result.json`, prior unit `/var/backups/codi-official-before-chat-busy.service`. Featured Stockfish runner remains the separate crash-safe rotation r2. The immediate desktop rollback is `native27-catchup-diagnostic-r2`; preserve the current units, release and backup. `/desktop/` is unchanged.

Browser sparse-index verification reuses bounded, pure previously computed immutable subtree promotions and previously verified identical witness inputs. Canonical input validation, final root checks, block signatures, stale/replayed-operation rejection and content-addressed node validation remain. An independent full 256-level calculation matched 24 operations; forged links, altered nodes, replay and cancellation were rejected. The compiled browser archive test passed 54 checks including real SIGKILL/reopen, concurrent heads, content corruption, capacity and cleanup. Its old unbundled fixture failed to start because its copied source inventory was stale; the fixture was updated to accept verified nested compiler chunks, and the compiled test passed. Packaged real-issuer Chat/Chess and offline-ban tests passed.

In one public Chrome with guest/speech assets blocked, catching up the same 85-block history used 212,638 digest calls and 14.265s before the first optimization, then 101,026 and 12.665s. On the same 95-block history, witness reuse reduced calls from 113,722 to 88,204 but the single-run time was unchanged at about 13.44s. Immediate initial polling reduced that 95-block sample to 7.501s and the first request from about 6.17s to 0.197s. These are individual samples, not universal timings. Catch-up now processes up to four 32-block pages per maintenance pass; verified blocks persist as they are installed. Nerd settings expose bounded scheduler/recovery errors. A simulated 503 outage verified that the diagnostic appears and a draft crossing a ban/unban stays unsent until explicit resend.

The official submission service now returns 503 with `Retry-After: 1` when its four request slots are occupied, while malformed requests and unauthorized origins remain refused. The browser treats 503 as a temporary busy condition with bounded jittered backoff (1–15s, plus up to 1s jitter); other errors retain their prior backoff, and explicit channel denials still require review. A real concurrent saturation test held four requests, verified a fifth was 503, and verified a bad origin stayed 403. The authority suite passed nine applicable tests with three browser-offer-dependent tests skipped. An old test expectation allowing anonymous submission was updated to the user's current registered-only policy.

Live chat-only ten-browser runs suppress guest and speech downloads through test-only browser interception, with no production setting changed. One immediate-poll run timed out at 180s with nine messages delivered and one device pending; two additional local browser tests overlapped that measurement. A later diagnostic run passed in 65.3s, with two generic temporary submission refusals; after busy classification/backoff, another passed in 56.4s, with two 503 responses that recovered. All ten browsers received all ten messages and test accounts/author metadata/profiles were removed; signed synthetic messages remain in General chat. These runs used nine browsers on one workstation and one on i36, which shares the server's /29; no independent WAN claim. The history grew between runs. Browser catch-up on i36 remains a major part of delay and large-history performance, repeated ten-person reliability and independent WAN remain open.

Private box-git main `fce6a0c61160b17d16a00e33687437a2f32f2a4d` includes packet `tools/codiserver/server-chat-busy-retry-20261029-r1`, proof SHA256 `1b93831913b0c9c588901d5223be640973b98eb6f54f6ca87380e2212320d6ce` and 69 remotely verified files. Prior related packets: browser hash reuse `d5379ad9ac3df451e0cba80930e7ad3a2742d85d`, witness reuse `77bcf79446324474bc5fec64e58b18afd02e634e`, immediate catch-up `ca6e60cf0da8bc21ccb2930acbad6592860d90ac`, diagnostics `746fd6f8e5ecac34f24c38e9d20c7ea5effac26c`; all remote packet proofs verified. No account DBs or private keys were copied. Full goal remains active.

### Early server submission while history catches up — 2026-10-29

The active frontend is `/srv/codi-connected/releases/native27-early-chat-r1`, manifest `8bc851c88e4f8172e44ed337442062940be25b77c153eba99cf1efc22168eb50`, managed config SHA256 `d5c9475ee29874259af45c57344f0c2f58190681432d1dbf245a5321b56136d3`. Managed activation receipt `/srv/codi-connected/early-chat-activation-result.json`; renewal-unit backup `/var/backups/codi-renew-before-early-chat.service`; immediate previous release `native27-catchup-busy-r1`. Official API remains `chat-busy-r1`.

Registered General chat now attempts to submit a locally persisted draft while earlier signed history is still loading. Server authorization, actor binding and current epoch checks remain authoritative. The browser leaves the draft pending until it independently verifies the accepted history, and retries via ordinary recovery if the early attempt fails. Denied/stale drafts still require explicit user resend. A real local Chrome test held history unavailable: the server accepted in 145ms with seven existing blocks, and pending cleared only after history was restored and verified. A previously restricted account could not bypass draft review; explicit resend succeeded. The complete packaged browser suite passed spam/original reveal, account restrictions and reconnect, chess/chat separation, registered spectator replay, and signed checkmate replay after restart. Ten writer/authorization tests passed. These are functional tests, not a promised latency or scaling bound.

Private box-git main commit `a81e7ef` holds packet `tools/codiserver/browser-early-chat-20261029-r1`, source-proof SHA256 `7ec96919a4d5081ad58c19c7ffedde88c7951bb43b48f6c6a73dfcb8238d0cee`; all 14 listed files verified from the remote. No private keys or account databases copied. Live ten-browser test in `.build/checks/live-chat-early-ten.txt`; consult its final result before asserting success. Full goal remains active; independent WAN and repeatable catch-up performance remain unproven.

The live chat-only ten-browser test subsequently passed in 85.5s, with all ten messages visible and zero pending. Several `/official-ingest` calls returned temporary 503s and automatically recovered. Guest/speech downloads were suppressed only by the test; nine browsers were on the workstation and the tenth was on i36 (same public /29 as the server). The ten disposable accounts and associated author/restriction metadata were deleted; signed synthetic messages remain. This is not a controlled speed comparison with previous runs because the history grew. Root and `/desktop/` returned HTTP 200, the official and featured-chess services were active, and Stockfish was making moves. Removed the inactive temporary webhost staging copy and verified temporary backup checkout.

### Bounded browser operation-node hash reuse — 2026-10-29

Live frontend `/srv/codi-connected/releases/native27-node-cache-r1`, manifest `47b689374ac74076a02b36d0f2dc575b1a14b2214f6a2358497423f0aee3f9dd`, managed configuration SHA256 `cb8ee46e587776971a0369ab763468f5b421ec5a94525434a871e2c5c86a77be`, activation receipt `/srv/codi-connected/node-cache-activation-result.json`, renewal unit backup `/var/backups/codi-renew-before-node-cache.service`; immediate rollback is `native27-early-chat-r1`. Official API remains `chat-busy-r1`. The browser caches at most 16,384 exact cryptographic operation-tree node inputs and their SHA-256 results, including in-flight calculations; failures are evicted. It still validates content-addressed nodes, signatures, witnesses and roots. Node test covers matching an independent path, invalid roots and corrupt nodes, cancellation, shared concurrent calculation and retry after digest failure.

A controlled isolated 134-operation tree construction produced the same root and used 95,338 digest calls in 2.312s before versus 40,568 in 1.065s after; this omits browser storage and network. Two single-browser live samples at the same 134-block height, with guest/speech assets blocked by the test, used 126,366 digests and 10.069s before versus 71,537 and 8.990s after; these individual samples are not a throughput guarantee. The current real Chrome bundled archive suite passed 54 checks including crash, recovery, corruption, conflicting heads, atomic writes and lifecycle. The full packaged Chat/Chess suite passed. The older unbundled candidate fixture failed readiness before executing checks because its copied dependency inventory is stale; failure receipt `.build/checks/node-cache-archive-r9.json` is retained and does not establish a product failure. Live ten-browser test output is `.build/checks/live-chat-node-cache-ten.txt`; check its final result before claiming it passed.

Private box-git main `4092d6b` holds packet `tools/codiserver/browser-node-cache-20261029-r1`, proof SHA256 `9a0e67b14ba05a076875fb6cecc396b6d91b5f2834bd7ffb5053c42447d789cc`; all 15 listed files were verified on the remote. No private keys or account databases were copied. Temporary inactive staging, verified backup checkout and benchmark fixture were removed. Full goal remains active.

The first live ten-browser run after node-cache activation FAILED its 180s wait: all ten browsers showed nine of ten test messages, no pending entries, and accepted height 143. Several temporary 503s occurred; they are not proof of the missing message's cause. Disposable accounts and their author metadata were removed; nine signed messages remain. The test did not capture composer drafts or transient save errors, so the exact failure remains unknown. A second live diagnostic test is running with status, draft, and missing-message capture added to `scripts/live-server-chat-ten-check.py`; inspect `.build/checks/live-chat-node-cache-diagnostic-ten.txt` and the live process before drawing a conclusion. An undeployed source change makes Chat preserve a message-save error across refresh and keep the draft visible; it needs a focused browser test and a release before claiming it is live.

### Chat save and background catch-up collision — 2026-10-29

The repeated diagnostic ten-browser test confirmed the missing message was from i36: it remained in the composer while the local save failed `Another view advanced this channel; reload its accepted state and retry`; the status was then overwritten by a normal refresh. The other nine were accepted. The failure was a conflict between queueing the user's original and automatic history installation on the same channel, not proof that the server or Pi failed. Both failed tests cleaned their ten test accounts and related metadata; signed accepted test messages remain.

Live frontend now `/srv/codi-connected/releases/native27-chat-race-r1`, manifest `6b52f84998167695c7e94be2a4c982eb4005321d8b3e8ea7a539da9ecf38b91f`, managed config SHA256 `d3ca4a80d8281d39ca1d62c4eb39c5305c8bbd698893ccb9ebd55437d2254615`, activation receipt `/srv/codi-connected/chat-race-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chat-race.service`; immediate rollback `native27-node-cache-r1`. Automatic official history recovery now yields between blocks to an active local channel operation, leaving at most an in-flight block competing for the current save; manual recoveries do not wait on their own work lock. Verification remains unchanged. Chat retains a plain-language save failure and the unsaved composer text across refresh; details go under Nerd. Focused browser error/draft/retry test and history-yield/cancellation test passed; full packaged Chat/Chess/moderation suite passed. Live regression test `.build/checks/live-chat-race-fix-ten.txt` is in progress; consult it and its running process before claiming an outcome.

Private box-git main `b59ec7b` contains packet `tools/codiserver/browser-chat-race-20261029-r1`, proof SHA256 `d8b7befb977ac32ef0b964c6c22ca56d9ef9abeeee57083431dccaec1f5e914c` and all 21 listed files verified from remote. No account database or private key copied. Full goal remains active.

The live regression after this change passed in 94.7s: all ten registered browsers, including i36, saw all ten messages, with no pending entries or retained drafts. One request returned 503 and recovered. Test-only browser interception suppressed guest and speech assets; i36 shares the server's public /29, so this does not verify independent-provider connectivity. Exact disposable accounts and author metadata were removed; ten signed synthetic messages remain. The prior two 180s failures and one post-fix pass are evidence of the reproduced race and recovery, not proof it cannot recur or that chat is fast. Temporary staging and verified backup checkout were removed.

### Batch history recovery experiment and live update — 2026-10-29

The previous goal turn was productive: it deployed and tested save/recovery coordination. On this turn, an independent real i36 browser profiling the current 162-message official history took 63.726s, 1,708 archive read transactions, 164 write transactions and 89,007 digest calls. History page responses were typically tens of milliseconds. A grouped-read experiment reduced read-transaction count to 1,206 but took 64.790s on the same history; no speed improvement was established. It passed its local checks but was rolled back through the managed controller to `native27-chat-race-r1`, with config back at SHA256 `d3ca4a80d8281d39ca1d62c4eb39c5305c8bbd698893ccb9ebd55437d2254615`. Its code and 18 verified packet files remain in private box-git `ff2adb1` for audit, not active product code. No claim is made from these single samples about all devices.

A new implementation verifies up to eight official-history blocks individually and commits their accepted graph, head and pending acknowledgements together in one strict IndexedDB transaction, yielding between batches to user channel work. A bad block aborts its entire batch; earlier completed batches remain durable. Live frontend is `/srv/codi-connected/releases/native27-batch-history-r1`, manifest `7c565cbfb4cc9dcd4ff21759c67080583780bfc12eeb8e97277b8adf40213409`, managed config SHA256 `da7aceb80fe85fe80d2f211e7c03ac4191cb28704b92001910e483a0a92ce6d8`, activation receipt `/srv/codi-connected/batch-history-activation-result.json`, renewal-unit backup `/var/backups/codi-renew-before-batch-history.service`; immediate rollback is `native27-chat-race-r1`. Official API remains `chat-busy-r1`.

The compiled Chrome archive test passed 60 checks, including reconstructing 68 signed blocks to the identical head, retaining every block and pruning index nodes, a bad later block preserving the original pending item, a real IndexedDB transaction abort leaving no nodes or acknowledgement, crash and corruption cases and ordinary single-block semantics. The full packaged Chat/Chess/moderation browser suite passed. One live i36 sample of the same 162 blocks took 24.574s, with 694 reads, 22 writes and 61,902 digest calls; this is one sample with guest and speech downloads blocked by test instrumentation, not a guarantee. All profile accounts and i36 drivers were removed. An isolated local server fixture separately showed signed write time rising from 9ms at height 1 to 859ms at height 165 due to history replay and witness generation; it is not a measurement of the live host.

Ten-browser live regression `.build/checks/live-chat-batch-history-ten.txt` is in progress; check process and final output before claiming success. Private box-git main `fcccc84` contains packet `tools/codiserver/browser-batch-history-20261029-r1`, proof SHA256 `d6b64753e54b866a5e83232b543230757bdce159d25599b05f9104d5c1f834ca`; all 18 files verified remotely. No private keys or account databases copied. Temporary host staging and verified backup checkout removed. Full goal remains active.

The live ten-browser batch-history regression passed in 64.0s: all ten registered browsers, including i36, saw all ten messages with no pending messages or retained drafts; a handful of 503 responses recovered. Nine browsers were on one workstation, i36 used `104.180.210.36` in the server's /29, and guest/speech downloads were blocked by the test only. Exact disposable accounts and author metadata were removed; ten signed synthetic messages remain. Different history length and load make this an uncontrolled comparison with the previous 94.7s run. The inactive grouped-read experiment release and its local build products were removed after verifying the active release, immediate rollback and private source backup; retained test evidence and source backup record why it was rejected.

### Verified server writer reuse — 2026-10-29

Live official service package `/srv/codi-connected/official-services/chat-writer-cache-r1`, manifest SHA256 `bebc0c20e35ef03cc62ec7ef44f0ec6bc178623a0ddd28f7bd2e2d908c93079a`, activation receipt `/srv/codi-connected/official-writer-cache-activation-result.json`, immediate prior unit `/var/backups/codi-official-before-writer-cache.service` (package `chat-busy-r1`). Frontend remains `native27-batch-history-r1`. Runtime's official writer serializes access to a bounded cache of eight channel floors, each capped at 32,768 operation IDs. While holding its SQLite write transaction it fingerprints every exact stored history byte and the pinned policy before using a prior fully verified replay; valid appended suffixes of up to 64 blocks are cryptographically replayed on a copy, other changes force full replay. Cache state is published only after the new block commits. Registered identity, actor binding, current bans, epochs, witness checks, signature checks, atomic commit, idempotency and moderation remain enforced. This still scans stored bytes and rebuilds the sparse witness each write; it is not a large-history scaling proof.

Eleven cached writer tests passed, including unchanged history, unrelated database writes, verified moderator suffixes, invalid suffixes, tampered prefixes, bans/unbans, wrong identity, replay and duplicate originals. A ten-thread authority test with ten separate registered authors passed full signed replay. The packaged service passed the real-browser Chat/Chess/moderation/restart suite; authority tests passed nine applicable cases with three browser-fixture-dependent cases skipped. Isolated local writer samples at about 165 signed blocks showed 859ms per append before and 209ms after cache; samples are not a controlled live-server latency guarantee. The ten-browser public regression `.build/checks/live-chat-writer-cache-ten.txt` is in progress; inspect its process and final output before asserting a result.

Private box-git main `a6839d4` contains packet `tools/codiserver/server-writer-cache-20261029-r1`, proof SHA256 `db41567ecdc720b2097686d50919fd4fb86c5c46f2a2932e5f0dfca8726aa831`; 60 listed files verified from remote. No account databases or private keys copied. Temporary host staging and verified backup checkout were removed. Full goal remains active.

The live ten-browser server-cache regression passed in 69.6s with all ten registered browsers seeing all ten messages and zero pending or retained drafts; temporary 503s recovered. Nine browsers were on one workstation and i36 used the same public /29 as the server; guest/speech downloads were blocked by the test only. Exact disposable accounts and author metadata were removed; signed synthetic messages remain. This run does not demonstrate group-wide speed improvement compared with the earlier 64.0s run, since history and conditions differed. Both current sites returned HTTP 200 and official and featured-chess services remained active.

### Live reconnect and service restart — 2026-10-29

Using two fresh registered Chrome browsers on the public root site, one on the workstation and one on i36 (`104.180.210.36`), `scripts/live-chat-reconnect-check.py` first checked ordinary offline recovery. After a shared baseline, CDP put the workstation browser fully offline; an automated form submission remained locally pending while i36 sent and received three messages. When network returned, both browsers verified all four messages and showed zero pending after 4.2s, without page reload. The test programmatically submits forms and does not establish physical touch or keyboard behavior. The browser interception disabled guest/speech assets for this chat-only test; i36 shares the server's public /29 and therefore this is not an independent-ISP test.

`CODI_RECOVERY_MODE=server` then stopped the live official chat service while the same kind of two-browser test was open. Both simulated sends stayed pending; after service start, both browsers received and verified both messages without reload in 27.7s. A finally block restores the service on test failure. Actual service health and public root and `/desktop/` returned active/HTTP 200 after the test. Test accounts, per-author metadata, browser profiles and i36 chromedriver were removed; their signed synthetic messages remain. Receipts: `.build/checks/live-chat-reconnect-r1.txt` (diagnostic history text stripped after test) and `.build/checks/live-chat-server-restart-r1.txt`. No production code was changed during this test. These are two-participant single-run results, not evidence of ten-person independent-WAN reliability.

Private box-git main `77fdb88` holds the test packet `tools/codiserver/live-chat-reconnect-test-20261029-r1`; proof SHA256 `0676900e50530eb77add54afb9fdec943493668ea689484e636542ab41499f8f`, both files verified remotely. No private account data or keys copied. Verified temporary backup checkout removed. Full goal remains active.

A third two-browser live run exercised `CODI_RECOVERY_MODE=reload`: a signed message was saved pending while the workstation browser was offline; after returning online, submission requests were temporarily blocked while the page was reloaded and the same registered account signed in again. The pending message remained visible in the reopened Chat app and had not reached i36. Once the artificial submission block was removed, both browsers verified the message and showed zero pending in 3.7s. The test programmatically submits forms, blocks guest/speech downloads, and uses i36 on the server's /29; it is not a physical-user or independent-provider test. Both temporary accounts and their metadata, browser profiles, and i36 driver were removed; signed synthetic test messages remain. Receipt `.build/checks/live-chat-reload-recovery-r1.txt`. Private box-git main `cca21e8` holds updated test packet `tools/codiserver/live-chat-reload-test-20261029-r1`, proof SHA256 `53b8602a679555561121307e7ba2ccd96205d7911e4954f8f70f726d848be6f9`, both files verified remotely; no private account data or keys copied. The verified temporary backup checkout was removed. Full goal remains active.

### Ten-browser offline recovery and online wake — 2026-10-29

A live ten-browser test disconnected three browsers (including i36), queued one signed message per offline browser, let seven online browsers send, then reconnected the three. The first test was intentionally interrupted after finding a test assertion bug: substring matching made `participant 1` also match `participant 10`; diagnostic and cleanup completed, and accepted synthetic messages remain. The corrected test matched complete message suffixes and passed: all ten saw all ten messages exactly once and zero pending in 95.9s after reconnect, with no reload. Nine browsers were on the workstation and i36 was on the server's /29. Test-only browser blocking suppressed guest and speech, and form submissions were automated. Receipt `.build/checks/live-chat-ten-recovery-r2.txt`.

The current frontend is `/srv/codi-connected/releases/native27-online-retry-r2`, manifest `572123536e4ba13d1cb657d28a732a52fa0f3c5bc99044246c99e705aff1e653`, managed config SHA256 `ec1ce1614e95087824bec5fddc74eba5b6f2d2a22f761827e0370fd71523d506`, activation receipt `/srv/codi-connected/online-retry-activation-result.json`, renewal-unit backup `/var/backups/codi-renew-before-online-retry.service`, immediate rollback `native27-batch-history-r1`. Official API remains `chat-writer-cache-r1`. When Chrome reports online, active official readers reset their retry deadline and wake the scheduler (events limited to once per second); subsequent failed requests retain normal backoff. An older in-flight failure cannot overwrite that wake. A real Chrome fixture induced delayed retries and confirmed an online event retried in 9ms instead of waiting 4s; a held pre-reconnect failure did not delay the new request, and the event listener was removed on close. Full packaged Chat/Chess/ban/restart suite passed. The live ten-person recovery repeat is in `.build/checks/live-chat-ten-recovery-online-r1.txt`; inspect its final output and live process before reporting a result.

Private box-git main `5b35d1f` contains `tools/codiserver/browser-online-retry-20261029-r2`, proof SHA256 `5941af79d4360d1e8a57519bf7a46ee4fb66bab740d6df711fabe9149cf1babb`; all 13 files verified remotely. No private account databases or keys copied. Temporary host staging, verified backup checkout and unused R1 candidate were removed. Full goal remains active.

The post-update live repeat passed: three browsers were offline while seven sent, then all ten received all ten unique messages exactly once and had no pending/draft in 71.8s after reconnect without reload. Different history and load mean this is not a controlled comparison with 95.9s earlier. Browser emulation suppressed guest/speech downloads only in the test, used automated form submission, and placed nine browsers on one workstation and i36 on the server's /29; it does not prove independent-provider connectivity. Disposable accounts, author metadata, test profiles and i36 driver were removed; signed synthetic messages remain. Receipt `.build/checks/live-chat-ten-recovery-online-r1.txt`.

Investigation for next turn: a live i36 session's internal diagnostics during group recovery showed member relay attempts and missing-content refusals even though channel transport defaults to `server`. `network/discovery.mjs` routes such channel invitations via the server rather than WebRTC, but `networking.js` still defaults `channelDiscovery:true` and `channelIndex:true` when the server config omits deviceChannels. This may create unnecessary server-routed peer work, and must be measured against the user's latest direction to use official server-relayed chat only. It is not yet established how much delay those attempts caused. Avoid claiming P2P or WebRTC was used; inspect/test before changing or disabling anything.

### Server-only official chat routing — 2026-10-29

The previous turn was productive: ten-browser disconnect/reconnect passed and online-event retry was deployed. This turn's two-browser public Chrome instrumentation confirmed that opening official chat had started one `/rendezvous` WebSocket per browser, although no WebRTC connection was observed; ordinary chat also used official HTTP APIs. Those were server-routed peer introductions rather than direct P2P. The active root frontend now disables automatic channel discovery and the peer channel index when transport is server-only. When config omits deviceChannels, both default off while official discovery remains on. Explicit future non-server transport can still enable those features; account-link discovery remains a separate explicitly invoked facility. This does not remove the future P2P implementation.

Live release `/srv/codi-connected/releases/native27-server-only-chat-r1`, manifest SHA256 `08b2e6a606a3124e050335af138ff2e63dba35be55aa1e284181fe661b8a8973`, managed config SHA256 `d35e1b215da277ebaee26210dc3408fa8d354e453b4e00168100405acd893286`, activation receipt `/srv/codi-connected/server-only-chat-activation-result.json`, renewal-unit backup `/var/backups/codi-renew-before-server-only-chat.service`; immediate rollback is `native27-online-retry-r2`. Official service remains `chat-writer-cache-r1`.

On the public site two registered browsers exchanged a message with zero `/rendezvous` WebSockets and zero RTCPeerConnections observed during the test, versus one rendezvous each before. This does not claim zero WebSockets for unrelated guest or explicit account-link features. Public two-browser Chat and Chess regression passed sender names, featured Stockfish board and replay and Chat/Chess conversation; the Chat-window first exchange took 19s with existing history and the Chess-to-Chat message 4.3s in that run. The ten-browser test with three offline participants then passed exactly-once display of all ten messages in 37.8s after reconnect, no reload and no pending/drafts. Different history and machine load mean this is not a controlled comparison with 71.8s previously. Guest/speech assets were blocked only in the connection and ten-browser chat tests; form submissions were automated; i36 shares the server's /29 and independent-provider testing remains open. Temporary test accounts, author records, owned browser profiles and i36 test driver were removed; signed synthetic messages remain. Receipts: `.build/checks/live-chat-transport-before.txt`, `live-chat-transport-after.txt`, `live-server-only-apps-r1.txt`, `live-chat-ten-recovery-server-only-r1.txt`.

Private box-git main `23a6758` includes packet `tools/codiserver/server-only-chat-20261029-r1`, proof SHA256 `171b9b65ddd03c19602cf7cffd5632ffd38aac3b5141a3ade1ec9b87b98d4ad7`; all 10 listed files were verified remotely. No account database or private keys copied. Inactive staging and verified backup checkouts were removed. Full goal remains active.

### Early pending submission after reconnect — 2026-10-29

Current frontend `/srv/codi-connected/releases/native27-reconnect-early-r1`, manifest `abbfc02664d4075721d0aa3c8015aaa47441eb717e2b295a2604934d6ebfbb2f`, managed config SHA256 `aa7b9b5285eb10df882a9e69032cb8f4804bcd3be9116ac171266c1c972af3f6`, activation receipt `/srv/codi-connected/reconnect-early-activation-result.json`, renewal-unit backup `/var/backups/codi-renew-before-reconnect-early.service`; immediate rollback `native27-server-only-chat-r1`. Official service remains `chat-writer-cache-r1`.

A network-online event or reopening an official channel now attempts an eligible locally saved chat original before old history finishes downloading. The server still checks current account authorization, actor binding, bans/epochs and the current head; browser pending remains until independently verified history includes that original. If an older early attempt is in flight, a new queue or reconnect schedules one follow-up attempt, including when the old attempt subsequently fails. Failed attempts fall back to existing retry/recovery. The real Chrome fixture held history unavailable and tested normal and in-flight-failure races: both submitted within about 115ms in that local fixture and remained pending until signed history arrived. Offline ban/unban with an online event still required explicit resend. Full packaged browser Chat/Chess/moderation and restart tests passed.

The live two-browser test on workstation plus i36 held the sender's official-history responses after reconnect, while allowing submission: the offline message reached the other browser in 5.9s while still pending locally; both later verified all messages after history was unblocked. Guest/speech assets were blocked by test instrumentation; form submissions were automated; i36 shares server /29. Test accounts and metadata, browser profiles and i36 driver were removed; signed synthetic messages remain. Receipt `.build/checks/live-chat-early-reconnect-r1.txt`. Live reload regression `.build/checks/live-chat-reload-early-r1.txt` is in progress; inspect process/final receipt before claiming success. Private box-git main `2a1fcaa` holds packet `tools/codiserver/browser-reconnect-early-20261029-r1`, proof SHA256 `4b9dc670a50def2876dcaf6c5d0659de51f7fde82db438c6dd1cad9c8897c43d`; 14 files verified remotely. No private account data or keys copied. Temporary staging, verified backup checkout and unused intermediate build removed. Full goal remains active.

The live reload regression passed: a pending draft survived reload and sign-in and reached both browsers 5.5s after submission was unblocked; receipt `.build/checks/live-chat-reload-early-r1.txt`. The ten-browser disconnect regression then passed: all ten saw all ten messages exactly once, nine had converged by 8.4s and i36 by 35.1s after reconnect, with no pending/drafts; receipt `.build/checks/live-chat-ten-reconnect-early-r1.txt`. These are individual automated runs, not controlled performance comparisons. Nine browsers were on the workstation, one on i36 in the server's /29; guest/speech assets were blocked only during chat testing. Exact disposable accounts, author metadata, profiles and i36 driver were removed; signed synthetic test messages remain. Independent-provider testing and the larger goal remain open.

### Featured chess previous-game browsing — 2026-10-29

Live frontend is `/srv/codi-connected/releases/native27-chess-history-r2`, manifest `2f00c02457fef4c1565a1e51619e4549cafe8fb6bae39eabdccfdfd9aafbb8f1`, managed config SHA256 `9e772a7cb8e06cd3e3854ab078695e7eae4d7f6d78c5a135822d5f5db10a8ab0`; receipt `/srv/codi-connected/chess-history-r2-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chess-history-r2.service`, immediate rollback `native27-chess-history-r1`. Official storage service uses `/srv/codi-connected/official-services/chess-history-r1`, manifest `d328d09e872deda9096c1a5bace5f92092d479149e4afc46a37ad8e9a17dc3c9`; receipt `/srv/codi-connected/official-chess-history-activation-result.json`. The featured runner continues independently.

Chess can load the previous saved featured game on demand, step through it, walk to earlier games, and return to the current exhibition. The official server finds the previous link and checks the signed invitation and registered game/chat policies; the client verifies game history through the existing channel service. The game and shared General chat remain separate streams. Requests with malformed IDs and tampered archive data were rejected. Opening many distinct games can exhaust the existing 32-channel session limit: per-channel lifecycle/refcount cleanup remains needed, especially with multiple windows. This is not human-versus-human play.

The real-browser local fixture `.build/checks/chess-history-browser-r3.txt` passed replay of a completed signed checkmate, switching current/previous, earliest-game boundary, separate chat and recovery after service restart. Two registered public browsers passed archive/current switching, move stepping and chat in `.build/checks/live-chess-history-r1.txt`. A fresh two-browser public run at emulated 390x844 phone dimensions also passed, including a minimum 44px Previous game control, in `.build/checks/live-chess-history-mobile-r2.txt`; automated clicks do not prove physical phone touch. Disposable test accounts and author metadata were removed, while synthetic signed messages remain. Root and `/desktop/` returned HTTP 200; official and featured chess services active.

Private box-git main `508f95c1` contains `tools/codiserver/chess-history-20261029-r1`; all 77 listed source and artifact files verified against the remote proof. It contains no account database or private keys. Owned temporary staging, backup checkout and intermediate app builds were removed. Full goal remains active; independent-provider testing, human/agent games, and channel lifecycle remain unfinished.

### Channel worker retirement — local work in progress, 2026-10-29

Local `network/device-replica-scheduler.mjs` now has an asynchronous per-channel `remove`: it removes the scheduler entry, cancels the entry's current operation, waits for it to finish and then releases its resource lease. Canceled work cannot emit stale updates. `scripts/device-replica-scheduler-concurrency-check.mjs` passes existing concurrency, pressure and wake tests plus retirement, unaffected neighboring work, replacement, slow cancellation and concurrent full-session shutdown. This primitive is **not yet connected to the channel session or Chess app, and is not deployed**; previous-game browsing still has the 32-channel limitation. Next implement shared per-view ownership and safe retirement of eligible spectator archives, including in-flight operations and racing reopen, then verify multiple windows, persistent recovery and >32 distinct games before deployment. Do not retire shared chat or pending work merely because one view closes.

Private box-git `6b159c4` has WIP packet `tools/codiserver/scheduler-retirement-wip-20261029-r1`; both source files verified remotely. No keys or state copied. Temporary backup checkout removed. Full goal remains active.

### Shared channel view ownership — local work in progress, 2026-10-29

`assets/desktop/channel-view-leases.mjs` is a local, currently unconnected ownership helper. An opening view reserves the channel before async work; shared owners prevent retirement; a view closed while opening causes cleanup once opening finishes; reopening waits for retirement; failed retirement blocks reopen. `scripts/channel-view-leases-check.mjs` passes these cases, and the scheduler concurrency/retirement tests still pass. The helper has not been integrated into `DeviceChannelSession` or Chess and has not been deployed. To complete the feature, account for all handles, in-flight session/archive/RPC operations, scheduler and discovery cancellation, persistent pending work, session shutdown and reopen races; retire only eligible spectator entries, and exercise multiple real windows and >32 old games before live rollout. Existing live 32-channel limit remains.

Private box-git main `6beaf58` holds WIP packet `tools/codiserver/channel-ownership-wip-20261029-r1`; both source files verified remotely. The owned temporary backup checkout was removed. Full goal remains active.

### Chess spectator retirement integration — local candidate, 2026-10-29

Local `DeviceChannelSession` now attaches view leases to opened/created/restored channels and exposes `releaseChannel`. It retires only non-validator spectator chess entries in server-only mode when officially pinned, no peers are connected and no pending operations exist. Retirement stops the scheduler, waits view operations and discovery/notice/exchange work, and closes the in-memory archive and traffic registration; saved IndexedDB history remains. Chess releases the former game after switching. Configured official pins stay permanent; dynamically discovered pins for retired channels can be dropped and rediscovered, avoiding a separate 128-pin accumulation. The implementation is local only, **not deployed**.

Real packaged Chrome fixture `.build/checks/chess-retirement-browser-r3.txt` passes two Chess views sharing the current game, switching one to a previous signed game while the other remains, verifying three open channels, closing the other and checking the unused game is retired, returning to current with two channels, chat, and signed replay after restart. This used service `.build/shared-services/catchup-hash-test-r30` and app `.build/chess-retirement-app-r1`. Node checks pass lease races, scheduler shutdown and discovered-pin retention. It has not yet proved >32 different games, cancellation/failure under actual network/IDB load, or complete app/chat regression and must not yet be deployed. Known condition to address/test: if a spectator view leaves before official discovery has pinned its game, the current conservative eligibility check leaves it session-owned; an eventual discovery should trigger safe retirement or the open must explicitly bind an authenticated official pin. Also review in-flight peer/retirement and shutdown races before release. Current live remains native27-chess-history-r2.

Private box-git main `c7b5945` has packet `tools/codiserver/chess-retirement-wip-20261029-r1`, nine source/test files verified remotely. No keys or databases copied. Full goal remains active.

### Chess spectator retirement live — 2026-10-29

Live frontend `/srv/codi-connected/releases/native27-chess-retirement-r1`, manifest `920ef337f526de626e9aa66aec25355d2cf88ceffb9e5ec735227fa19f1b7077`, config SHA256 `833850b74a60b1c0272860c67180925a0284896a4d99bd30475b46ce5dee654c`, activation receipt `/srv/codi-connected/chess-retirement-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chess-retirement.service`, immediate rollback `native27-chess-history-r2`. Official storage and Stockfish runner unchanged. Root and `/desktop/` returned 200; steward, official and chess services active. Current public two-browser test `.build/checks/live-chess-retirement-r1.txt` was started after activation; inspect its process and final output before reporting it as passed.

Local candidate releases official spectator chess channels when their last view leaves, after in-flight work and scheduler cleanup, without deleting saved browser history; other views, chat, players, pending work and active peer-mode sessions remain protected. If official discovery is delayed or fails when leaving, cleanup waits or retries when discovery later succeeds. Discovered pins are removed with their retired game; configured pins stay. A browser opened 40 distinct valid signed official game descriptors and retired each, leaving at most two channels after cleanup; it also survived one injected 503 during game discovery. Receipt `.build/checks/chess-retirement-40-games-r3.txt`. This exercises the session API rather than 40 manual GUI selections. Full packaged browser regression `.build/checks/chess-retirement-full-browser-r1.txt` passed two shared Chess windows, previous/current game replay, recovery after restart, signed spam display, bans, offline pending, explicit resend and reconnect. Node lease, scheduler and pin tests also passed. Real independent-provider testing and human/agent games remain unfinished; peer-mode channel retirement remains conservative and was not the scope of this fix.

Private box-git main `aa6b47e` contains packet `tools/codiserver/chess-retirement-20261029-r1`, 29 files verified remotely; no account database or private keys. Owned staging and temporary backup checkout removed. Full goal remains active.

The live two-browser test `.build/checks/live-chess-retirement-r1.txt` completed PASS: registered sender name, chat delivery, current and previous saved game, replay stepping, return to current and Chess-window chat delivery. It removed its two disposable accounts and author metadata; synthetic signed messages remain. The 40-game test described above remains local/automated and is not a physical-user test.

The post-activation 390x844 emulated mobile Chrome check `.build/checks/live-chess-retirement-mobile-r1.txt` also passed chat and the current/previous game workflow with a 44px Previous game control; it does not test physical touch. Its two disposable accounts and author metadata were removed. Unused r29/r30 shared service builds and the intermediate service-only release were removed after the r31 tests and final release were verified.

### Ten-browser live recovery after chess retirement — 2026-10-29

`CODI_TEST_CHAT_ONLY=1 python3 scripts/live-server-chat-ten-recovery-check.py` passed on the current `native27-chess-retirement-r1` release; receipt `.build/checks/live-chat-ten-chess-retirement-r1.txt`. Ten registered automated browsers (nine workstation, one i36) exchanged ten messages while three browsers were taken offline and then reconnected. All ten received each message exactly once with no pending/draft, without reload; nine had recovered by 8.7s and i36 by 39.0s after reconnect. i36's diagnostic contained status-0 network failures from the deliberately offline interval; no failure was recorded for the ninth browser. This single run does not establish why i36 took longer. Test instrumentation blocks Linux guest/speech downloads and submits chat forms programmatically. i36 (`104.180.210.36`) shares the server's provider/subnet, so independent-provider proof is still outstanding. All ten disposable accounts and associated author metadata, temporary profiles and i36 test driver were removed; signed synthetic messages remain. i36 remains reachable. Full goal remains active.

### Reuse a freshly verified checkpoint — live 2026-10-29

Live frontend `/srv/codi-connected/releases/native27-checkpoint-cache-r1`, manifest `6e4169c0e9e483b9477949756f1699aa8b623205401b667772aefec63b1f5a00`, managed config SHA256 `881221e743d15594f9da6782792aef07b0a150937063a8b2a867f344cabdbc74`; receipt `/srv/codi-connected/checkpoint-cache-20261029-r2-activation-result.json`, renewal backup `/var/backups/codi-renew-before-checkpoint-cache-20261029-r2.service`; immediate rollback `native27-chess-retirement-r1`. Initial guarded activation stopped before changes because the older backup name already existed; the unique-name retry passed. Root and `/desktop/` returned 200.

The prior live ten-browser trace `.build/checks/live-chat-ten-recovery-trace-r1.txt` passed in 41.0s; i36 had reached only history height 32 at reconnect and fetched successive pages at 32-block intervals while reaching height 285. Response header timings were mostly tens of milliseconds, but they do not measure full body transfer or separately establish CPU/IDB time. The local change caches an exact checkpoint and already branded, fully verified position only after its strict append transaction commits; a fresh archive instance still verifies persisted bytes and every new block remains independently verified. A local Chrome benchmark with 68 blocks and 8-block batches passed all 60 archive checks in both variants, with apply time 1320ms without and 642ms with the candidate in single sequential runs; this is not an i36 or controlled live latency guarantee. `.build/checks/checkpoint-cache-archive-batch-r3.json` passed 60 checks including invalid blocks, interrupted writes, corruption and reopening. Full packaged Chat/Chess browser regression `.build/checks/checkpoint-cache-full-browser-r1.txt` and 40-game test `.build/checks/checkpoint-cache-40-games-r1.txt` passed. The initial source-only archive test failed to initialize because its old fixture omitted three dependencies; corrected test and failure receipts are retained.

The post-activation ten-browser trace `.build/checks/live-chat-ten-recovery-trace-after-r1.txt` was started; inspect live process and final result before claiming a pass or performance outcome. Private box-git main `3a7783e` has `tools/codiserver/checkpoint-cache-20261029-r1`; all 16 listed files verified remotely, with unique rollout names included. No private keys or databases copied. Owned temporary staging and backup checkout removed. Full goal remains active.

Post-activation ten-browser trace `.build/checks/live-chat-ten-recovery-trace-after-r1.txt` passed all ten messages exactly once and no pending/drafts; nine converged by 8.2s and i36 by 36.3s after reconnect. i36 resumed at height 32 and recovered to 295; the preceding traced run reached 285 and took 41.0s. These are single runs with different history and load, not a controlled estimate of speedup; the trace only times response headers, not full response bodies. Its visible message count stayed at zero until about 33.6s and reached all ten at about 36.0s, so progressive catch-up feedback/rendering remains a useful next investigation. Ten disposable accounts and associated author metadata and owned browser/driver resources were removed; signed test messages remain. i36 shares the server provider/subnet. A final post-activation live Chat/Chess check `.build/checks/live-chess-checkpoint-cache-r1.txt` was started; inspect it before reporting success.

The final public two-browser Chat/Chess check `.build/checks/live-chess-checkpoint-cache-r1.txt` completed PASS for registered sender names, message delivery, current and previous game, move replay, return to current and Chess-window chat. It removed both disposable accounts and author metadata; signed synthetic messages remain. Steward, official storage and featured chess services were active after deployment.

### Progressive chat catch-up — live 2026-10-29

Live frontend `/srv/codi-connected/releases/native27-chat-progress-r1`, manifest `1bcdc4d7386d0f71e8f55133fbdb22e7a07c515637809e1e93b920d7666e0d1e`, config SHA256 `448339cf8d52034c8da54bad72ee7a93d200c1b5546cefd6671cbe4eddca54f2`, activation receipt `/srv/codi-connected/chat-progress-20261029-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chat-progress-20261029-r1.service`; immediate rollback `native27-checkpoint-cache-r1`. Root and `/desktop/` returned 200; steward, official and featured chess services active.

Official history installation now notifies views after strictly committed verified batches, throttled to at most once per 1.5 seconds after the first batch. Chat shows already verified messages while remaining history loads, says “Loading messages…” or “Reconnecting to chat…” as appropriate, and shows connection loss promptly on the browser offline event. Pending status remains visible alongside connectivity, and event listeners are removed on app disposal. Server targets are not presented as independently verified delivery claims. The real-browser fixture `.build/checks/chat-progress-browser-r3.txt` held history after block 32 and verified an earlier saved message and loading status appeared before releasing the remainder, then checked final messages and a simulated offline status. The earlier r1 fixture timed out at accepted height zero: its first progress update was incorrectly throttled when page uptime was below 1.5 seconds. r34 explicitly permits the first update. The Node yield test checks that failed blocks do not emit progress. Full packaged chat/ban/offline/reconnect and chess regression `.build/checks/chat-progress-full-browser-r3.txt` passed.

Live two-browser workstation/i36 check `.build/checks/live-chat-progress-reconnect-r1.txt` passed a real browser offline event, pending message, missed messages, warning clearance and recovery in 6.1s after reconnect; it removed both disposable accounts and author metadata. i36 shares the server's provider/subnet. Ten-browser public trace `.build/checks/live-chat-progress-ten-trace-r1.txt` was started after activation; inspect process and final output before reporting its result. Private box-git main `a09a52e` has packet `tools/codiserver/chat-progress-20261029-r1`, 22 files verified remotely; no keys or databases. Owned temporary backup and server staging, intermediate service release, r33 build and superseded app candidate were removed. Full goal remains active.

The post-activation ten-browser public trace `.build/checks/live-chat-progress-ten-trace-r1.txt` passed: ten messages displayed exactly once with no pending/draft; nine browsers converged by 7.7s and i36 by 39.9s after reconnect. On i36, 30 verified prior messages were visible at 0.15s after reconnect, rising to 64 by 5.4s; the latest ten test messages arrived near the end. Its status sequence showed connection loss, pending plus connection loss, reconnecting, loading and eventually saved. This is one automated run with fresh browser profiles, not an independent-provider or physical-touch test. Ten disposable accounts and author metadata and temporary driver/profiles were cleaned; signed synthetic messages remain. A final public Chat/Chess check `.build/checks/live-chess-chat-progress-r1.txt` was started; inspect it before claiming success.

### Honest chess switching — live 2026-10-29

Live frontend `/srv/codi-connected/releases/native27-chess-switch-r1`, manifest `dbbee845be36a96dfee40b1ed8e9dac9ced7d5c6dbafd86fd059638fa3b76842`, config SHA256 `fafb687b1ac6cab6371d26a3cda8462b5fc8a141c6123979229154daeb034600`, receipt `/srv/codi-connected/chess-switch-20261029-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chess-switch-20261029-r1.service`; immediate rollback `native27-chat-progress-r1`. Root and `/desktop/` returned 200.

The first post-chat-progress live Chess regression `.build/checks/live-chess-chat-progress-r1.txt` failed its replay assertion immediately after switching back to the current game: it waited for title and board only, and Previous was disabled even though the server's current game subsequently reported height 5. That exposed a transient presentation issue: the new title could appear while the previous board was still displayed or the current game was not yet recovered. Chess now clears the old board, disables replay and shows loading until the selected game's snapshot draws. A real-browser fixture deliberately held the newly selected game's snapshot and asserted the old board was removed, then released the snapshot and passed completed-game replay, chat, multiple views and restart; `.build/checks/chess-switch-browser-r1.txt`. The revised public test waits for a current board with replay enabled rather than assuming title change means recovery; `.build/checks/live-chess-switch-r1.txt` was started and must be inspected for its final result before claiming live Chess passed. Temporary accounts from the failed test were removed. Private box-git main `3a7fe26` has `tools/codiserver/chess-switch-20261029-r1`, all 16 listed files verified remotely; no keys or databases copied. Owned staging and backup checkout removed. Full goal remains active.

The revised live public two-browser test `.build/checks/live-chess-switch-r1.txt` completed PASS for chat, sender names, current and previous games, returning to the current game after its board and replay controls were ready, stepping through moves and Chess-window chat delivery. Both disposable accounts and author metadata were removed; signed synthetic messages remain.

### Chess timer cleanup race — live 2026-10-29

Live frontend `/srv/codi-connected/releases/native27-chess-lifecycle-r1`, manifest `ce1d45334067b1d5404a316e7ea2708a4e2840245751e32a424d1cb874e67768`, config SHA256 `6c9cfca8bcebad977d26bd815babee4072357a0d8ab3c0b4c278fbda7d658f36`, receipt `/srv/codi-connected/chess-lifecycle-20261029-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chess-lifecycle-20261029-r1.service`; immediate rollback `native27-chess-switch-r1`. Root and `/desktop/` returned 200; steward, official and featured chess services active.

A real-browser repeated-open fixture exposed a Chess interval leak: if the app was disposed after its board rendered but before asynchronous initialization returned, it started its five-second interval after disposal. `.build/checks/chat-chess-lifecycle-r1.txt` retains that failing result. The app now rechecks its lifetime immediately before starting that interval. The real packaged browser fixture `.build/checks/chat-chess-lifecycle-r2.txt` passed eight Chat and Chess open/close cycles with zero remaining tracked online/offline listeners, app intervals, 30-second timers or views and only the shared chat channel remaining; signed Chess switching/replay/restart regression `.build/checks/chess-lifecycle-regression-r1.txt` also passed. The public desktop test `.build/checks/live-chat-chess-lifecycle-r2.txt` passed eight cycles using actual Close controls with no tracked Chess intervals or Chat online/offline listeners and removed its one disposable account and author metadata. That test blocked guest and speech downloads, did not claim all applications/resources or physical touch, and sent no synthetic chat messages. An initial generated test script had a Python quoting error before executing any test and is superseded by the r2 receipt.

Private box-git main `bb53d9a` contains `tools/codiserver/chess-lifecycle-20261029-r1`, 17 files verified remotely; no private keys or databases copied. Owned temporary backup and staging were removed. Full goal remains active.

Outside-provider cellular check requested from the user: with Wi-Fi off, sign in on the phone, open General chess chat and send exactly `Cellular check 8e73`, then report whether it remains pending. The user has not yet replied. A read-only official replay check found no exact match at the time of asking; do not infer a failure from absence or claim cellular origin from a server message alone. If they report sending it over cellular, independently verify the exact accepted message in a second registered browser and test the return direction; use their confirmation of Wi-Fi/cellular state, without asking for passwords or private keys. Continue independent work meanwhile; do not re-ask while this question remains pending.

### Chat layout and scrolling — live 2026-10-29

Live frontend `/srv/codi-connected/releases/native27-chat-layout-r1`, manifest `5cd98444d28a11a7da1297792b541d83326d38950ea4faab9e064b018b96bd4e`, config SHA256 `03277f36e96528994ac0ffbbced160ff915c4548e62ec93fa872102c0776bc8c`, receipt `/srv/codi-connected/chat-layout-20261029-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chat-layout-20261029-r1.service`; immediate rollback `native27-chess-lifecycle-r1`. Root and `/desktop/` returned 200; steward, official and chess services active.

The official Chat markup previously did not match the `.channel-app` selectors of its imported stylesheet, so its intended channel layout and independent history scrolling did not apply. Chat now owns its own matching stylesheet and has a responsive channel list, message bubbles, fixed composer and separately scrolling history. It follows the bottom only when already there; when reading earlier messages, a surviving message anchor preserves the reader's place through re-render, and a Latest messages button returns to the bottom. The existing 64-message recent window still limits how far back the interface can scroll; a fallen-off anchor uses the previous scroll position. Browser fixture `.build/checks/chat-layout-browser-r4.txt` loaded the actual bundled CSS and passed 380px/720px layout, partial verified history, offline status, scrolling while reading, jump to latest, following at bottom and 44px Send control; it did not establish physical touch. Static illustrative screenshots were inspected and removed. Full packaged Chat/ban/offline/reconnect and Chess regression `.build/checks/chat-layout-full-browser-r1.txt` passed. Earlier fixture failures were retained: r1 had a missing test argument, r2 failed because the isolated fixture did not serve CSS, and r3 submitted its second test message while the composer remained busy; r4 corrected the test setup.

The public phone-sized browser check `.build/checks/live-chat-layout-mobile-r1.txt` was started after activation; inspect process and final output before claiming it passed. Private box-git main `cf4bead` contains `tools/codiserver/chat-layout-20261029-r1`, all 12 files verified remotely; no keys or account databases copied. Owned temporary staging, backup checkout and preview screenshots were removed. The user has not yet responded to the pending cellular check `Cellular check 8e73`. Full goal remains active.

The public phone-sized browser check `.build/checks/live-chat-layout-mobile-r1.txt` completed PASS: real chat delivery, the scrolling history held its position while an incoming message arrived, Latest messages reached the bottom, current/previous Chess games and replay worked, and Chess-window chat reached the other browser. Two disposable accounts and author metadata were removed; signed synthetic messages remain. It used emulation/programmatic clicks, not a physical phone.

### Verified older Chat messages — live 2026-10-29

Live frontend `/srv/codi-connected/releases/native27-chat-older-r2`, manifest `c4474062f72a060b4280dfc123c90b50e4753536b1366a5d9f4adb5b841e1886`, config SHA256 `d49182f16a1ea7bc720b150738b6522dd052cfa364eafe6b9fc1903bbbbdb614`; receipt `/srv/codi-connected/chat-older-20261029-r2-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chat-older-20261029-r2.service`; immediate rollback `native27-chat-layout-r1`. Root and `/desktop/` returned 200; steward, official and featured chess services active.

Chat offers Load older messages at the top of the history. A shared channel API returns bounded, newest-first message pages from locally saved, content-hash/quorum/ancestry-checked blocks; it verifies message proposals and read access before and after each page and only accepts continuation cursors previously issued by this channel session. The UI combines older pages with recent messages, keeps at most 256 older messages plus the recent window in memory, labels an omitted middle gap if it trims, preserves visible position where possible, retains spam markers and original reveal, and can browse locally stored history while offline. Unavailable retained history is labeled; it is not silently fetched or fabricated. If a different channel is opened while older loading is in flight, the old result cannot appear there and the new control is re-enabled.

Browser `.build/checks/chat-history-pages-browser-r1.txt` verified 80 signed messages in order, invalid cursor/limit rejection and reopening saved history. `.build/checks/chat-older-final-browser-r1.txt` passed phone/desktop widths, simulated server outage while reading older messages, scroll and old spam reveal. A 300-signed-message browser test `.build/checks/chat-older-bound-browser-r2.txt` passed on app r3; final app r4 differs by a channel-switch completion fix, independently exercised by `.build/checks/chat-older-switch-race-r1.txt`. Full packaged Chat/ban/reconnect and Chess regression `.build/checks/chat-older-full-browser-r3.txt` passed the exact final app/service. The public phone-sized browser check `.build/checks/live-chat-older-mobile-r1.txt` was started; inspect its process and final output before reporting success. These tests are automated and do not prove physical touch or independent-provider operation.

Private box-git main `4b3c48d` contains `tools/codiserver/chat-older-20261029-r1`, 23 files verified remotely; no private keys or account databases copied. Owned temporary staging, backup checkout and intermediate candidate builds were removed. Pending user cellular test `Cellular check 8e73` has not yet been confirmed. Full goal remains active.

The public phone-sized browser check `.build/checks/live-chat-older-mobile-r1.txt` completed PASS for loading earlier verified messages, preserving scroll and jumping to latest, message delivery, sender names, current/previous Chess games and replay, and Chess-window chat. Two disposable accounts and their author metadata were removed; signed synthetic messages remain. It used emulation/programmatic clicks, not a physical phone.

### Honest server acceptance indicator — live 2026-10-29

Live frontend `/srv/codi-connected/releases/native27-chat-sent-r1`, manifest `a32ad12a79f13dd82a5aaaed0911bb97c2c5c378aa5d0cde225f074e4a923cf9`, config SHA256 `b5bf250510e21744024ed5d8c77e2057b9cd9447abb356047d4311b43710089a`; receipt `/srv/codi-connected/chat-sent-20261029-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chat-sent-20261029-r1.service`; immediate rollback `native27-chat-older-r2`. Root and `/desktop/` returned 200; steward, official and featured chess services active.

Own accepted messages show `Sent` only when the displayed verified history head exactly matches the last complete head recovered from the official server. The accessible label says Sent to server and the tooltip states other-person receipt is not tracked. Pending originals do not receive this marker. The server has not implemented recipient receipts, so neither this change nor earlier server acceptance proves delivery to another person's device; genuine Delivered remains outstanding. `.build/checks/chat-sent-head-r1.txt` verifies a locally newer or different head does not get the marker. `.build/checks/chat-sent-browser-r3.txt` verifies offline pending, reconnect and visual/accessibility labels at 380px/720px together with older history, spam and scrolling. Full packaged Chat/ban/reconnect and Chess regression `.build/checks/chat-sent-full-browser-r1.txt` passed. The earlier r1 targeted test had a selector bug that picked the other account's identical test text; r2/r3 fixed it.

Public phone-sized test `.build/checks/live-chat-sent-mobile-r1.txt` passed server-confirmed visual/accessibility indicator, chat, older history and Chess. Two-browser workstation/i36 `.build/checks/live-chat-sent-reconnect-r1.txt` passed offline pending without Sent, then Sent after verified server history, and recovered in 5.9s. Its two disposable accounts and author metadata were removed; signed synthetic messages remain. i36 shares the server provider/subnet; physical phone and independent-provider checks remain open.

Private box-git main `a1ceb2f` contains `tools/codiserver/chat-sent-20261029-r1`, 22 files verified remotely; no keys or account database copied. During the backup update, adding a path from an unpopulated `--no-checkout` worktree accidentally removed the packet in commit `7d4cb81`; commit `a1ceb2f` restored it from its predecessor, added the live test and every current packet file was verified remotely. No live service or other backup was affected. Owned temporary checkouts/staging and intermediate build were removed. The `Cellular check 8e73` request remains unanswered. Full goal remains active.

### Delivery checkpoints — local work in progress

`active-system/steward/official_receipts.py` adds a local SQLite checkpoint primitive for registered accounts. It rejects banned accounts and wrong or missing official chat heads, updates monotonically, and returns only the furthest checkpoint from a different account. It assumes the caller has authenticated and bound the exact request; it does not itself implement a network endpoint or prove that a human read a message. `active-system/scripts/official-receipts-check.py` passes three local tests using mocked channel-policy verification and synthetic stored headers. This is not yet integrated, migrated on the server, deployed, or sufficient to display Delivered. Next wire it into the existing authenticated official submission protocol, send acknowledgements only after browser history is verified and durably saved, associate messages with checkpoint ancestry, add lifecycle/reconnect and adversarial tests, then deploy and test the actual two-account flow. The live Sent indicator and featured chess service are unchanged.

Local continuation: the existing one-use authenticated submission now accepts receipt checkpoints through an explicitly enabled runtime feature; issuer-signature/body binding, replay rejection and anonymous rejection passed `scripts/official-authority-check.py` (13 tests, three unrelated fixture-dependent tests skipped). The receipt schema requires explicit migration. Browser code has an opt-in, separate background checkpoint attempt and bounded ancestry scan, plus a Delivered label for matching own messages. It is disabled by default and has not been packaged, migrated, deployed, or tested as a complete flow. Chromium `scripts/official-delivery-browser-check.py` passed synthetic cross-page ancestry and conflicting/future checkpoint cases; it does not test real signed message attribution. Runtime startup requires the migrated schema when enabled; the lifecycle feature test passed. Fixed the lifecycle test fixture's private database modes to match the launcher's existing requirements; six preexisting lifecycle tests passed. Next build a real two-account browser test with enabled runtime and browser flags, verify actual signed message IDs, same-account exclusion, offline/reconnect, lifecycle and performance, then package and deploy only after it passes. Live service remains unchanged.

The next local continuation passed `scripts/official-receipts-browser-check.py` against a real issuer, SQLite, signed chat, three separate Chromium profiles and the compiled Chat app: another session on the same account did not qualify, a different registered account caused the sender's actual message to show Delivered, an offline recipient did not qualify for a later message, and reconnect changed its UI from Sent to Delivered. The test simulates the network outage locally and does not prove independent-WAN operation. An initial run failed because the fixture invoked an unbound `fetch`; after binding it, the complete test passed against source, then against bundled service `catchup-hash-test-r38`, and again with both that bundle and separately launched official package `chat-receipts-r1`. Production service bundle manifest `aa5bf313533fb2987a03da4456d34a4ee1e6ac0f36c5678b5a87c95124d0d70b`, official package manifest `34dc7a464d2a5f7419be4c89762648d024473347f1540d65be3204f60c089710`; compiled test Chat is `.build/receipt-app-test`. Server launcher exposes explicit `--receipts`, and packaged `official-init-receipts.py` explicitly migrates a validated private state directory. Neither migration nor deployment has run. Next assemble the sealed frontend release with the new Chat and service, wire the `officialReceipts` option through the deployed core/config, test the exact release including ordinary chat/chess regressions and server restart, back up sources, then stage and deploy with the controller and verify on the live test site. Keep the goal active.

### Delivery receipts deployed; public verification in progress

Superseding the pre-deployment note: `native27-chat-receipt-r2` is active at the main test site, manifest `26cf5db394c52c1caa1b6bb6145245bbb2f01d390c7d5e33e76ece66b06526a5`, managed configuration SHA256 `cbef4a35049970f6b99a9602253328cdcc0be797d6d2eb0ee9490826b2891b7e`, receipt `/srv/codi-connected/chat-receipts-20261029-r2-activation-result.json`, rollback release `native27-chat-sent-r1`, renewal backup `/var/backups/codi-renew-before-chat-receipts-20261029-r2.service`. Official service package `chat-receipts-r1` is active after explicit receipt-schema migration, manifest `34dc7a464d2a5f7419be4c89762648d024473347f1540d65be3204f60c089710`, unit rollback `/var/backups/codi-official-before-receipts.service`, activation `/srv/codi-connected/official-receipts-activation-result.json`. Root and `/desktop/` returned 200; official and featured chess services active. The additive receipt table can remain if the prior service is restored.

Local packaged regression `scripts/official-receipts-regression-check.py` passed chat spam recovery, bans and explicit resend, offline/online recovery, Chess replay and complete saved game. `scripts/fixtures/official-service-export-check.py` passed. Private box-git `ksu.codes.git` main `cfccdb0` contains `tools/codiserver/chat-receipts-20261029-r1`; all 80 code/manifest files re-read and verified remotely; no private state or keys. With no-checkout clone, `git reset HEAD` was required before adding the new packet; staged file list was checked to prevent deletions. The owned checkout was removed.

Public phone-sized automated test `scripts/live-chat-receipts-mobile-check.py` was started after activation with process session 96735; inspect the live process/result before claiming it passed. It creates two disposable test accounts and deletes their account, author and receipt metadata at exit; signed test messages remain. It also exercises featured chess and older history. This does not prove a physical phone or independent-provider connection. Keep the goal active.

The public test finished PASS: two registered sessions exchanged chat; the sender's actual UI showed Delivered after the second account confirmed, with correct accessibility text; older history and scrolling worked; the current and previous Stockfish games loaded and replayed; and a Chess-window message reached the other browser in 7.2 seconds. The initial test message reached both sessions in 25.1 seconds in this run. Its two disposable accounts and author/receipt metadata were removed; synthetic signed messages remain. All owned temporary webhost staging copies were removed. This was phone-size emulation, not a physical phone or independent-provider test.

### Ten participant test with receipts

Live `CODI_TEST_CHAT_ONLY=1 scripts/live-chat-receipts-ten-check.py` PASS, receipt `.build/checks/live-chat-receipts-ten-r1.txt`: ten distinct registered browsers, including i36 at 104.180.210.36, all recovered ten distinct messages exactly once after three were disconnected, with no reload or remaining pending messages. Recovery completed 53.4 seconds after reconnect; all ten senders showed confirmed delivery 2.3 seconds later. The seven connected senders continued while three were offline. Test intentionally blocked Linux and speech downloads; i36 shares the server provider. Ten disposable accounts and their account, author and receipt metadata were removed; synthetic signed messages remain. i36 was reachable.

The test's final diagnostic captured temporary 503s on official-ingest challenge/use and 429s on issuer official-ingest challenge; status-0 failures also occurred during the deliberate offline interval. This run establishes that the services recovered, not why catch-up took 53 seconds. Current submission adapter admits four concurrent requests, and issuer per-IP official challenge throttling shares a 60/minute default; receipt clients currently repeat several signed requests every 15 seconds per channel. Investigate request bursts and retry behavior before claiming stable ten-person latency, and reduce/smooth receipt load while keeping receipts authenticated and chat submissions independent. Official service remained active, 0 restarts, about 49 MB at the subsequent snapshot. Keep the full goal active.

### Receipt retry smoothing live; comparison running

Superseding the 15-second polling note, frontend `/srv/codi-connected/releases/native27-receipt-smoothing-r1` is live, manifest `4273cdd37d9ea15a6ff32205eca931b698998fac2b5e85f0c4639d68db157e70`, config SHA256 `ea716d160359b2b19fde7f6ce372ab0ad8cc81ccdb768c4ff06e4e7e30385ebb`, activation `/srv/codi-connected/receipt-smoothing-20261029-r1-activation-result.json`, rollback `native27-chat-receipt-r2`, renewal backup `/var/backups/codi-renew-before-receipt-smoothing-20261029-r1.service`. Receipt polls now use 20–25 second jitter, and failures retry with jittered exponential backoff capped at 125 seconds; chat submission and recovery remain independent. Both source and bundled test `scripts/official-receipts-browser-check.py` with `CODI_RECEIPTS_FAULT=1` passed a deliberately failed receipt, continued chat, same-account exclusion, delivery, offline/reconnect and GUI. This does not prove the live rate-limit cause is solved.

Private box-git main `50ebf04` contains `tools/codiserver/receipt-smoothing-20261029-r1`; all nine code and manifest files verified remotely, no keys or private state. Ten-browser comparison `CODI_TEST_CHAT_ONLY=1 scripts/live-chat-receipts-ten-check.py` is running as exec session 45263 with output `.build/checks/live-chat-receipts-ten-r2.txt`. Inspect the process and complete output before reporting results; cleanup removes ten temporary accounts and receipt metadata. This uses i36, which shares the server provider. Retain full goal.

The comparison completed PASS: nine browsers recovered all ten messages in 9.3 seconds after reconnect, and i36 completed at 47.9 seconds; all ten senders had Delivered 8.2 seconds later. The final diagnostic samples contained seven 503 challenge responses and no 429s, versus eleven 503s and eleven 429s in the earlier run; these samples retain only each browser's last 20 failures and are not complete traffic counts. Deliberate offline network errors were also recorded. The runs show successful recovery with fewer sampled rate-limit errors, but do not establish causation or eliminate the remaining 503 bottleneck. Ten disposable accounts and metadata were removed; signed synthetic messages remain. i36 remained reachable with about 6.9 GB RAM available during its slower catch-up. Root and `/desktop/` returned 200; temporary webhost staging was removed. Full goal remains active, including independent-provider testing.

### Early send retry and separate challenge lane — staged, not live

Public trace `.build/checks/live-chat-receipts-ten-trace-r1.txt` passed the ten-browser recovery in 56.8 seconds. It traced response body completion as well as headers: i36 resumed at height 32, fetched 32-block pages of about 136–143 KB, generally received bodies in under 100 ms after response headers, but spent roughly 3–7 seconds between pages before the next request; tracing clones response bodies and can itself add work. The final delayed message was from i36. An official-ingest challenge hit 503 shortly after reconnect; the trace does not identify which operation owned it. Code inspection found that a failed early submission had no independently scheduled retry, so normal maintenance could hold a send behind history recovery. The trace does not isolate CPU, IndexedDB or scheduler time. Disposable accounts and receipt metadata removed, synthetic signed messages remain.

Local fixes: `device-channel-session.mjs` retries failed early pending sends with bounded jittered exponential backoff while history continues, cancels timers on session close/retirement and keeps pending until signed history verifies acceptance. `steward/official_submission_http.py` has separate bounded four-request lanes for short challenges and submissions, so blocked writes cannot occupy every challenge slot; this raises the total possible in-flight requests from four to eight while preserving per-lane limits and proof checks. `scripts/official-authority-check.py` passed 14 tests (three unrelated fixture-dependent skips), including held writes with a successful concurrent challenge and a bounded fifth write. `CODI_RECONNECT_EARLY_ONLY=1 scripts/official-early-busy-retry-check.py` passed first-failure and in-flight-race cases with no additional online event: server accepted in 1.26 and 1.47 seconds while history remained blocked, and the original stayed pending until verification. Full packaged Chat/moderation/reconnect/Chess regression `.build/checks/early-busy-full-regression-r1.txt` passed.

Staged but not activated: official package `/srv/codi-connected/official-services/chat-receipt-lanes-r1` manifest `5b4c32e2b7f8b2cc0222045ba61c99a830877887c36981b11f811d55d9a9f863`; frontend `/srv/codi-connected/releases/native27-early-busy-r1` manifest `535e501578648a446ea647903b366764111a77401a1af1d608bcbcf3c5d8c9f3`. Live remains `native27-receipt-smoothing-r1` and `chat-receipts-r1`. Exact bundled receipt fault/reconnect test is running in exec session 65792; poll and verify before activation. Staging scripts are in `/tmp` on webhost. Private box-git main `d23f1b5` contains `tools/codiserver/early-busy-20261029-r1`; 65 source/package/manifest files re-read and verified; no private state. Full goal remains active.

Superseding staged status: the exact bundled receipt fault/reconnect and Delivered-UI test finished PASS, and both updates are active. Official package `chat-receipt-lanes-r1` has unit rollback `/var/backups/codi-official-before-receipt-lanes.service` and activation `/srv/codi-connected/official-receipt-lanes-activation-result.json`; frontend `native27-early-busy-r1` has managed config SHA256 `b558ee72382aab1b1a3032aa89731e73182599379136c5d3c732ce25ea102c84`, activation `/srv/codi-connected/early-busy-20261029-r1-activation-result.json`, immediate rollback `native27-receipt-smoothing-r1`, and renewal backup `/var/backups/codi-renew-before-early-busy-20261029-r1.service`. Public ten-browser trace is running as exec session 75868 with output `.build/checks/live-chat-early-busy-trace-r1.txt`; inspect it before reporting live success. This trace records body sizes/times on two participants and simulates three disconnects; i36 shares the server provider. User-directed full goal remains active.

The public trace finished PASS: all ten received all ten messages once, nine browsers by 9.4 seconds after reconnect and i36 by 52.9 seconds. On traced browser 1 the tenth message appeared 8.5 seconds after reconnect versus about 50.5 seconds in the preceding traced run; these are individual runs and do not establish causation. i36 itself remained at zero matching messages until approximately 52.5 seconds as it verified old history, so the slow-device catch-up problem remains. Final diagnostics (each limited to its last 20 failures) sampled two challenge 503s, eighteen submission-use 503s and three issuer 429s plus expected offline errors. The separate lane prevents writes blocking challenges, but the use lane still saturates; investigate bounded waiting/priority or another safe approach rather than claiming the busy issue is solved. Ten disposable accounts and receipt metadata removed, synthetic signed messages remain; owned webhost staging was removed. Root goal remains active and independent-provider testing is still missing.

### Bounded submission queue — staged, not active

Local `steward/official_submission_http.py` now permits up to eight syntactically valid use requests to wait at most two seconds for one of the existing four submission slots; excess or timed-out requests still get 503. The challenge lane remains independently bounded at four. Authentication is still required, pre-admission checks reject malformed Authorization, and the cancellation-safe offload holds its slot until actual work ends. `scripts/official-authority-check.py` passed 15 tests (three fixture-dependent skips), including saturated queue overflow, queued request draining, cancellation, and challenge progress with four held writes. Packaged Chat/moderation/reconnect/Chess regression `.build/checks/use-queue-full-regression-r1.txt` passed. Exact packaged receipt fault/reconnect test is running as session 17373; poll before activation.

New package staged only at `/srv/codi-connected/official-services/chat-use-queue-r1`, manifest `1879733cd8655b3c7f565fe43201bf32a6c160c5a7755ee838f76de5b3576b00`; live official service remains `chat-receipt-lanes-r1`. Root-owned activation script `/tmp/activate-official-use-queue.py` is staged and pinned to the current unit; inspect state before running. Private box-git main `bf3be16` contains `tools/codiserver/official-use-queue-20261029-r1`; all 57 package/source files re-read and verified, no private state. After successful packaged test, activate and run the bounded live ten-browser comparison, inspect 503/429 samples and cleanup. Full goal remains active, including independent provider and slow-device history work.

Superseding staged status: exact packaged receipt fault/reconnect and Delivered UI test finished PASS; official package `chat-use-queue-r1` is now active, rollback unit `/var/backups/codi-official-before-use-queue.service`, activation receipt `/srv/codi-connected/official-use-queue-activation-result.json`. Frontend remains `native27-early-busy-r1`. Public ten-browser comparison is running as exec session 84817 with output `.build/checks/live-chat-receipts-ten-r3.txt`; poll before reporting. The test simulates three disconnects, removes ten temporary accounts and receipt metadata, and uses i36 on the server's provider. Root goal remains active.

The comparison completed PASS: all ten recovered all ten messages once, nine by 10.6 seconds and i36 by 53.5 seconds; all ten senders saw Delivered 7.9 seconds after recovery. Final diagnostic samples contained thirteen use 503s and one issuer 429, plus expected deliberate-offline status-0 errors. The samples are bounded and these individual runs do not establish causation; the queue has not eliminated contention. Disposable accounts and receipt metadata were removed, signed synthetic messages remain, and webhost staging copies were cleaned. An additional local simultaneous-burst test passed with all four active slots and eight queued requests occupied before release; no source code change resulted. Investigate where official-use time is spent and whether receipt and message traffic need fair scheduling, while separately improving i36 verified catch-up. Independent-provider validation remains outstanding.

### Profile and unchanged-receipt lock improvement — local

`CODI_TEST_CHAT_ONLY=1 scripts/live-chat-request-profile-check.py` completed PASS on live `chat-use-queue-r1`: nine browsers recovered all messages by 9.7 seconds, i36 by 54.7 seconds, all delivery labels by another 7.6 seconds. From bounded client-side timing samples, eleven successful message submissions had 3.14 s median and 5.98 s maximum response-header latency; 54 successful receipts had 17 ms median and 6.51 s maximum. Two message and four receipt 503s arrived around two seconds, consistent with the bounded waiting timeout; this does not isolate server internal phases. Deliberately offline status-0 errors are separate. Ten disposable accounts and metadata were removed, synthetic signed messages remain. i36 shares the server provider.

Code inspection found every receipt poll acquired an SQLite write lock even if its own stored head had not changed. `steward/official_receipts.py` now locally validates unchanged receipts in a read-only WAL transaction, and repeats all authentication-related channel, ban and head checks inside an immediate write transaction whenever a head advances. `scripts/official-receipts-check.py` first reproduced that unchanged polling blocked behind an unrelated held writer; after the change it passed that check, monotonicity, wrong heads, bans, and a new ban imposed between the read and write phases. Five local tests pass with synthetic stored headers and mocked channel policy. This change is not yet packaged or deployed; run signed-request, packaged receipt/reconnect, concurrency and Chat/Chess regressions before considering live rollout. Full goal remains active.

Local continuation: `scripts/official-authority-check.py` passed 16 tests (three fixture-dependent skips), including signed receipt binding and queue/burst limits. Packaged Chat/moderation/reconnect/Chess regression `.build/checks/receipt-read-full-regression-r1.txt` passed. Package `/srv/codi-connected/official-services/chat-receipt-read-r1` is staged but inactive, manifest `c8b5ca23073c530bb1664fa2dcb1076eb4b1bb7c84135c9b490916040e0116f2`; live official remains `chat-use-queue-r1`. Its packaged, real-browser receipt-fault/reconnect test is running as exec session 8102; poll before activation. `/tmp/activate-official-receipt-read.py` on webhost is pinned to the current unit, with rollback backup planned. Private box-git main `18ade5a` contains `tools/codiserver/receipt-read-20261029-r1`; all 59 source/package files verified remotely, no private state. On successful test, activate, repeat the ten-browser request profiler, compare sampled contention and document limitations. Root goal remains active.

Superseding staged status: packaged receipt fault/reconnect and Delivered UI test finished PASS; official package `chat-receipt-read-r1` is active, rollback unit `/var/backups/codi-official-before-receipt-read.service`, activation `/srv/codi-connected/official-receipt-read-activation-result.json`. Frontend remains `native27-early-busy-r1`. Owned webhost staging was removed. Live ten-browser request profiler comparison is running as exec session 37160 with output `.build/checks/live-chat-request-profile-r2.txt`; poll before reporting results, and compare bounded samples by message/receipt and response time rather than asserting causation. It simulates three disconnects, removes ten temporary accounts/receipt metadata and uses i36 on the server's provider. Full goal remains active.

### Server witness cache — staged, not active

The live profiler comparison finished PASS: all ten messages reached all ten browsers, nine by 10.3 seconds and i36 by 56.3 seconds; ten Delivered labels followed in 7.8 seconds. Bounded samples: message 200 responses (14) median 3168 ms/max 9267 ms, message 503s seven; receipt 200 responses (59) median 17 ms/max 3226 ms, receipt 503s two. The previous run had message 200 median 3140 ms/max 5976 ms, message 503s two; receipt 200 median 17 ms/max 6509 ms, receipt 503s four. These individual runs don't show an overall improvement or establish causation. Ten disposable accounts and metadata removed; signed synthetic messages remain. i36 is reachable; i34 and i35 had no Wi-Fi SSH route and public web connections failed, so their actual power state is unknown.

The server's existing `_witness` fully rebuilds the sparse verification set for every message. On box-webhost, synthetic rebuilds took 273 ms at 100 entries, 1087 ms at 400, 2165 ms at 800 and 4315 ms at 1600. New `steward/official_sparse_cache.py` implements a compressed immutable tree and produces the identical existing witnesses. Its writer integration binds cached trees to the freshly verified operation list and replay root, verifies the resulting root against the already validated insertion, and publishes only after database commit; it keeps at most two trees and falls back to the existing method at 32768 operations. On box-webhost, one synthetic 400-entry build took 1108 ms; for five distinct subsequent inserts, rebuilding had median 1159 ms and cached witness/add median 3 ms (max 5.7 ms). This is a microbenchmark, not live end-to-end latency.

`scripts/official-sparse-cache-check.py` passed four tests comparing witnesses and roots with the full oracle, duplicate rejection, changed history, wrong roots and commit-bound cache publication; `scripts/official-writer-cache-check.py` passed 11 actual signed writer/moderation/tamper checks. Full packaged Chat/ban/reconnect/Chess regression `.build/checks/sparse-cache-full-regression-r1.txt` passed. Official package `/srv/codi-connected/official-services/chat-sparse-cache-r1` is staged but inactive, manifest `899cc576819ecbb9b543ae018f1f104eaa98eba90b1c64aec7583cf3c7e2e134`. Exact packaged receipt fault/reconnect test is running as exec session 27435; poll before activation. Its pinned activation script is `/tmp/activate-official-sparse-cache.py`. Private box-git main `eb1594e` contains `tools/codiserver/sparse-cache-20261029-r1`; all 61 source/package files re-read and verified, no private state. On success, activate and repeat live request profiling, checking real message latency and busy responses. Full goal remains active; independent provider and slow-device history verification remain unproven.

Additional local `scripts/official-sparse-writer-history-check.py` passed 400 sequential signed writes followed by a fresh full cryptographic replay and root comparison in 7.0 seconds on this workstation. This new test script was created after the backup packet and is not yet in box-git; it does not change the staged package. It is a single local run, not a public latency or scale claim.

Superseding staged status: exact packaged receipt fault/reconnect and Delivered UI test passed, and official package `chat-sparse-cache-r1` is active. Unit rollback `/var/backups/codi-official-before-sparse-cache.service`, activation `/srv/codi-connected/official-sparse-cache-activation-result.json`; frontend stays `native27-early-busy-r1`. Live ten-browser request profiler comparison is running as exec session 39797 with output `.build/checks/live-chat-request-profile-r3.txt`; poll before reporting. Its measured samples do not establish causation; i36 shares the server provider. Ten temporary accounts and metadata are removed by the test, signed synthetic messages remain. Full goal remains active.

The live profiler completed PASS: ten messages reached all ten browsers once, nine by 6.7 seconds after reconnect and i36 by 56.7 seconds; all ten senders showed Delivered 8.0 seconds later. Sampled successful message submissions (13) had 1417 ms median/max 5730 ms, versus 3168 ms median/max 9267 ms in the preceding run; three message 503s remained. Successful receipt samples (56) had 17 ms median/max 848 ms and three receipt 503s. These are individual bounded samples on different runs and history sizes, not a controlled causal estimate; server busy responses and i36 history verification remain. Ten disposable accounts and metadata were removed; synthetic signed messages remain. Root goal stays active and independent-provider validation remains outstanding.

Follow-up validation sources, including the 400-signed-message test, are backed up on private box-git main `be9e3ce` under `tools/codiserver/sparse-cache-validation-20261029-r1`; both files were re-read and verified remotely, and the temporary checkout was removed.

### Browser history profiling and discarded cache candidate

Public `CODI_TEST_CHAT_ONLY=1 scripts/live-chat-crypto-storage-profile-check.py` passed the ten-browser scenario; `.build/checks/live-chat-crypto-storage-profile-r1.txt` records nine recovered by 6.8 seconds and i36 by 63.7 seconds. Instrumented i36 after reconnect made approximately 170407 WebCrypto digest calls, 2132 signature verifies and 2700 IndexedDB transactions; summed individual durations were about 11.7 s, 1.6 s and 35.3 s respectively. These sums can overlap, include unrelated UI/background work, and profiling changes timing; they do not prove wall-clock attribution. The workstation trace covered a different history amount. Its ten test accounts and receipt metadata were removed; synthetic signed messages remain; i36 shares the server provider.

Locally tried reusing persisted tree-node reads within each atomic eight-block append batch, with commit-time revalidation. The existing 60-check signed archive/crash/atomicity suite passed; `batchApplyMs` was 674 ms vs 682 ms in one workstation baseline. An instrumented run found **zero cache hits** and 112 misses across 68 blocks; this provides no meaningful benefit and would add checks, so the product change was reverted. The temporary candidate instrumentation script was deleted; evidence is `.build/checks/batch-node-cache-candidate-r1.json` and `.build/checks/batch-node-cache-instrument-r1.json`. Nothing was deployed for it. A separate baseline instrumented store-operation profiler `scripts/archive-batch-idb-profile-check.py` is running as exec session 49440, writing `.build/checks/archive-batch-idb-profile-r1.json`; poll before drawing conclusions. Full goal remains active.

The baseline store-operation profiler passed all 60 checks for 68 signed blocks in 667 ms on the workstation. It recorded 122 readonly and nine readwrite transactions during the append benchmark, including 113 readonly node gets; the nine atomic writes contained 551 node gets. This controlled fixture does not explain all 2700 i36 transactions observed during the live scenario, which also included UI and other background work. It does show why a per-batch cache had no repeated reads and points toward investigating dependency-aware batched node reads or reducing redundant archive/UI refreshes without weakening validation or atomic commits. No such optimization has been implemented or deployed. Full goal remains active.

Both profiling scripts are backed up and verified on private box-git main `c341c38` under `tools/codiserver/browser-history-profile-20261029-r1`; no private state is included and the temporary checkout was removed.

### Batched path prefetch experiment — rejected

Prototyped speculative old-tree path reads in one bounded IndexedDB transaction per eight-block append, retaining per-node hash checks and rechecking used rows in the strict atomic commit. A workstation run passed the 60 existing signed archive/crash/atomicity checks; the batch used 25 readonly transactions rather than 122, but read more individual rows (166 vs 113 readonly and 677 vs 551 inside writes) and took 671 ms vs 667 ms in single runs. A test-only mutation after prefetch was rejected before commit, preserving the old head (`.build/checks/archive-prefetch-race-r1.json`, 61 checks). Controlled i36 browser baseline `.build/checks/pi-prefetch-baseline-r1.json` passed 60 checks and timed 68 blocks at 4232 ms; candidate `.build/checks/pi-prefetch-candidate-r1.json` passed 60 and timed 4316 ms. Both used an owned remote Chrome profile and an actual owned-browser SIGKILL; fixtures and profiles were cleaned. These are single runs with generated histories, not statistical estimates. Because there was no observed benefit, the product change was fully reverted and its source SHA256 again matches baseline `a6045a22d9a17f71bc5a36913596b86ca1ee413db9d18322d156b866a6e7ab5f`; candidate-only files were removed. No live product changes occurred. Reusable remote harness `scripts/pi-archive-prefetch-benchmark.py` remains; its later PID-file uniqueness edit is syntax-checked but has not been rerun. Full goal remains active: i36's long initial history catch-up and independent-provider proof still need work.

The reusable Pi benchmark harness is backed up on private box-git main `3055add` in `tools/codiserver/pi-archive-benchmark-20261029-r1`; its source was re-read and verified, and the owned temporary checkout was removed.

### Narrow readonly-scope experiment — rejected

A local candidate narrowed individual readonly IndexedDB transactions to the requested store while preserving full strict writes and the experimental recovery-fence store. Workstation and i36 each passed all 60 existing signed archive, tamper, crash and atomicity checks. Single timed runs: workstation 748 ms for 68 blocks versus its prior 682 ms baseline; i36 4510 ms versus its prior 4232 ms baseline. Those are different generated fixture runs, not statistical proof, but show no useful improvement. The candidate was fully reverted; `channel-archive.mjs` SHA256 again matches the live baseline `a6045a22d9a17f71bc5a36913596b86ca1ee413db9d18322d156b866a6e7ab5f`. No product update occurred. The i36 run also exercised the benchmark harness's unique PID-file cleanup successfully.

Test-only `scripts/pi-archive-phase-profile-check.py` instruments time spent loading, accepting signed blocks, proposal verification, tree insertion and atomic commit in a 68-block batch; it is running on i36 as exec session 3155 with output `.build/checks/pi-archive-phase-profile-r1.json` and `.txt`. Poll before interpreting. It adds instrumentation overhead, uses generated history, and is not a live-site timing. Full user goal remains active.

The phase profile completed PASS. For 68 blocks on i36, instrumented `acceptDeviceChannelBlock` totaled 2076.5 ms, subsequent redundant proposal verification 238.3 ms, tree insertion 703.8 ms, strict commit 1131.3 ms, and loads 108.6 ms; instrumentation changes timing and the categories do not explain all end-to-end live work.

### Verified operation ID reuse — local candidate

The candidate reuses an immutable array of operation IDs obtained from the already fully replayed and quorum-certified block, rather than verifying each proposal signature twice in the same archive append. A private branded position controls access; initial or forged positions cannot provide IDs. Root comparison, signatures, authorization and strict atomic commit remain. On i36, two candidate runs passed 62 archive/security/crash checks and took 4070 and 4062 ms for 68 blocks; two baseline runs passed 60 checks and took 4232 and 4303 ms. These are individual generated-history runs, not a live-site catch-up result; the improvement is modest. Two earlier candidate runs failed before tests because the test fixture reused a benchmark variable name; the fixture was corrected and both failures retained as `pi-verified-ids-candidate-r1.json` and `r2.json`.

Candidate source is in `network/device-channel-state.mjs`, `assets/desktop/channel-archive.mjs`, and `scripts/fixtures/device-archive-page.mjs`. Bundles `catchup-hash-r41` and `catchup-hash-test-r41` and sealed candidate release `.build/releases/verified-ids-r1` (manifest `0a078e65efa2376e22a845a8ce644ae7c07b1a6f091ecaca6e8897b6c4fab814`) were built locally; none is deployed. The packaged-service chat/moderation/reconnect/chess regression is running as session 30982, logging `.build/checks/verified-ids-full-regression-r1.txt`; check its result before proceeding. The candidate still needs full packaged-receipt tests, source backup, and live validation before activation. The earlier one-minute history catch-up and independent-provider test remain outstanding. Full goal stays active.

Superseding that staged note: both the chat/moderation/reconnect/chess regression and the distinct-account receipt-fault/offline/reconnect test passed. Private box-git main `503a3494489ef34b29e8cdacabfc13ed142da576` backs up and re-verifies 12 candidate source/service files. The guarded managed upgrade activated `/srv/codi-connected/releases/native27-verified-ids-r1` with manifest `0a078e65efa2376e22a845a8ce644ae7c07b1a6f091ecaca6e8897b6c4fab814`, managed config SHA256 `4c1a1dcb236bbe0ac50af84f81bf38aa76d8e05f07b8c08252e219d082f2fa63`, renewal backup `/var/backups/codi-renew-before-verified-ids-r1.service`, activation receipt `/srv/codi-connected/verified-ids-r1-activation-result.json`; previous release is `native27-early-busy-r1`. Root returned 200 and issuer/steward/guest, official chat and featured chess services were active. Ten public browsers including i36 are running as session 14242, with output `.build/checks/live-chat-verified-ids-r1.txt`; inspect before claiming live behavior. i36 shares the server provider. Full goal and the slow-device/independent-provider issues remain active.

The ten-browser live run completed PASS: three offline browsers retained pending messages, seven online sent, then all ten received all ten exactly once after reconnect, nine by 7.5 seconds and i36 by 121.3 seconds; all ten senders saw delivery confirmation 12.6 seconds after recovery. The final diagnostic samples show only expected simulated-offline status-0 failures, with no nonzero failure status retained, though these are bounded samples. The 121-second i36 result is substantially slower than earlier 47–64 second runs; histories and conditions differ, so this does not establish whether the update caused a regression. It confirms that end-to-end slow-device recovery is still a serious unresolved issue. Ten disposable accounts and author metadata were removed; signed synthetic messages remain. The uploaded temporary release and scripts on box-webhost were removed. Full goal stays active; investigate i36 recovery and validate independently hosted networks.

### i36 fresh-load contention investigation

The ten-browser script starts its offline/reconnect scenario as soon as the composer is enabled, which does not mean the fresh browser finished its older history. For the same public 435-entry target, instrumented single-browser profiles on i36 took 139590 ms with the full desktop and 66232 ms with guest and speech assets blocked. They are single sequential runs and instrumentation changes timing; request timings were mostly tens of milliseconds. Full load recorded 182243 digest calls, 56 write and 2981 read transactions (summed durations approximately 16.5 s, 43.6 s and 102.3 s respectively); chat-only recorded 182072 digest calls, 56 write and 2689 read transactions (about 11.7 s, 10.1 s and 28.2 s). Transaction sums overlap and cannot be treated as wall time. Pi reported ample available RAM and no swap during full load. Disposable accounts removed and owned Chrome driver cleaned in each run. Receipts are `.build/checks/live-i36-full-load-profile-r1.txt` and `.build/checks/live-i36-chat-load-profile-r1.txt`.

The test-only `scripts/live-chat-catchup-load-profile.py` and `scripts/live-chat-i36-load-profile.py` now support asset-blocking modes `full`, `chat`, `guest`, `speech`; they do not change the live product. A guest-with-speech-blocked run is active as exec session 46739, output `.build/checks/live-i36-guest-load-profile-r1.txt`; poll before interpreting. Follow with speech-with-guest-blocked at the same history target, then decide whether startup contention warrants a tested scheduling change. Preserve the user's request to preload voice and start Linux; avoid disabling either merely to improve the benchmark. Goal remains active.

The two additional i36 profiles passed against the same 435-entry target: guest enabled / speech blocked took 126892 ms; speech enabled / guest blocked took 77885 ms. Full desktop was 139590 ms and chat-only 66232 ms. Each is one sequential, instrumented run, so these show a strong lead rather than a controlled statistical estimate; HTTP requests were mostly fast and IndexedDB transaction durations grew under guest load. All test accounts and browser drivers were cleaned. The guest is currently constructed as `new V86(...)` in `app.js` and its filesystem/serial/network hooks share the host integration; moving guest execution to a Worker may need a compatibility bridge and tests of interactive shell, guest network and filesystem. Do not pause or defer Linux or speech without preserving their requested behavior. The profile scripts have not yet been backed up to box-git. Full goal remains active.

The two profiling scripts were backed up and re-read on private box-git main `88d4df667d2c2ceeb63f88f9ac950db2efb12aba`. No product code or live deployment changed in this investigation.

### Worker-hosted guest feasibility

The shipped v86 library explicitly exports `self.V86` in a classic Worker. Test-only `scripts/fixtures/guest-worker-proof.js`, `guest-worker-proof.html`, and `scripts/guest-worker-proof-check.py` run the real current boot image in a dedicated browser Worker and bridge serial and two minimal file operations. `.build/checks/guest-worker-proof-r3.txt` PASS: real Linux boot, two PTY sessions with independent shell environments, shell reading a host-created file, host reading a shell-created file, and explicit worker guest shutdown. First probe initially waited for the older mux handshake; its interrupted receipt is `.build/checks/guest-worker-proof-r1.txt`; corrected single-shell r2 and two-shell r3 pass. This is a local feasibility test, not the product integration, and does not cover actual guest networking, reconnect, full Files/Text APIs, terminal backpressure, lifecycle under failure, CSP, phone, or performance. The current `desktop-apps.js` file APIs include synchronous `stat/list/mkdir` calls and direct `fs9p` access; the guest adapter expects direct `bus.register/send`. A production Worker requires a bounded, asynchronous bridge and coordinated migration with parity tests, not simply substituting this probe. The three fixture/test files were re-read and backed up on private box-git main `9d41ae9838f847f1b40961e1ab491b29febd1c28`. Live remains `native27-verified-ids-r1`; full goal and real slow-device test remain active.

`scripts/fixtures/guest-worker-network.js` and `scripts/guest-worker-network-check.py` extend the test-only bridge to the real local Chrome/v86 guest-network adapter, signed issuer grant, local coordinator and QEMU relay. `.build/checks/guest-worker-network-r5.txt` passed at root and `/hidden/`: real guest frames crossed the Worker boundary, QEMU ARP reached the Linux NIC, registered authorization succeeded, shell and file survived account changes, registered socket reconnect reauthorized and resumed ARP, and frames were bounded 14–1518 bytes. These are isolated temporary fixtures, not production wiring, and do not prove external ping, policy enforcement beyond exercising the real grant, worker failure handling, or performance. Earlier r1/r2 were interrupted while diagnosing a missing COEP response header; r3 failed because the test referenced an uninitialized reply global; r4 passed without the reconnect test; r5 passed the final scope. The files were re-read and backed up on private box-git main `049e5e36e7ec4c73c44aac264edfb294f447f990`. Full goal remains active.

### Async-compatible Files and Text source

The local `served_apps_public/files/index.mjs`, `files/browser.mjs`, and `text/index.mjs` now await guest `stat/list` so they can accept future Worker-backed methods while still accepting the existing synchronous guest API. Guest folder reloads discard stale navigation responses and ignore disposed views. Text serializes saves, preserves newer edits during an in-flight save, and refuses to overwrite newer edits after a delayed reload. `.build/checks/async-guest-apps-compiled-r3.txt` passed in real Chrome with the actual packaged Files/Text bundles and controlled asynchronous guest fixture: current synchronous list/stat compatibility, out-of-order folder response, overlapping save, delayed save and reload, and cleanup. Initial r1 failed due the test mock omitting `/home/guest` path normalization; the corrected r2/r3 passed. The five source/test files were backed up and re-read on private box-git main `25d4beb768aaf89dff4328c6b5d699dea2552633`; `.build/async-guest-apps-r1` is a test bundle only. This has not been integrated with a Worker, real v86 Files/Text workflow or deployed. The next step is a bounded worker filesystem/bus RPC and coordinated production host integration, preserving full guest operations and testing ping, lifecycle, stale replies, and i36 catch-up. Live remains `native27-verified-ids-r1`; full goal remains active.

### Guest Worker transport candidate

Local `assets/desktop/guest-worker-runtime.js` and `guest-worker-client.mjs` implement a classic Worker-owned v86, serial and bounded Ethernet bridging, serialized `stat/list/mkdir/read/write/trash/restore` requests, a 64-request queue, bounded request timeouts that report uncertain completion, late-reply rejection, and worker-failure/close cleanup. The desktop does not yet use this candidate. Real Chrome/v86 `.build/checks/guest-worker-client-r2.txt` passed Linux boot/shell, file operations and two-way guest filesystem sharing, trash/restore, rejecting work after close, request queue limit, timeout, late reply and fatal cleanup. `.build/checks/guest-worker-client-network-r1.txt` passed with the actual candidate client/runtime at root and `/hidden/`, including local QEMU ARP, registered issuer grant, guest NIC receipt, account switch and relay reconnect without losing shell/file. This does not yet cover full desktop integration, app lifecycle under Worker failure, real external ping, worker transport backpressure/large bursts, or i36 timing. Test resources are cleaned. Five candidate source/test files were re-read and backed up on private box-git main `154b93e3df717059009cc6225c3e83717da6b071`. Integrate carefully with async-compatible Files/Text source and existing guest session/home initialization; retain local rollback, package assets/CSP correctly, and run actual desktop workflows and i36 comparison before deployment. Full goal remains active.

Superseding the source-only integration note: local `app.js` and `desktop-apps.js` now use the worker candidate and asynchronous guest methods; this is not yet deployed. Test `scripts/guest-worker-desktop-check.py` stages the real desktop with the packaged async Files/Text apps and a real local signed issuer/QEMU relay. `.build/checks/guest-worker-desktop-r7.txt` passed root and `/hidden/`: registered network, Linux boot, initial shared home, Files opening a document in Text, save observed from shell, two separate PTYs with independent environments, and registered guest `ping -c 1 1.1.1.1` through the local relay. The initial r1 fixture lacked a now-required networking module and was interrupted; r3 sent input before the second PTY was ready; r4/r5 used a private gateway ping that the existing policy rejects (r4 also matched echoed input); r6/r7 use allowed public ICMP, and r7 matches actual independent-shell output rather than echoed input. Test-owned state cleaned. Integration files were re-read and backed up on private box-git main `5c361e3149261541a5586c966767d0e8b42c7577`; final corrected test was backed up at `cc03b6e2e134d829d24a15d7d88dd7ce38da9611`. Further work: test production package/CSP, failures, touch/voice, worker output/network flood behavior, existing chat/chess regression and i36 performance before live activation. Full goal remains active.

### Sealed Worker desktop candidate and i36 comparison

`.build/releases/guest-worker-r3` is locally sealed with manifest `eef64b4ed6c9b7ef36fd2dbb361c4098f284b2528ce675b9ef1bf9d0df31186e`; it composes the async Files/Text apps over the live verified-IDs release, changes only the reviewed core guest sections, adds Worker assets and rebuilds the asset/cache manifests. It is NOT deployed. A base build initially created an untracked Python bytecode file inside its sealed input; the precise file was removed and `sys.dont_write_bytecode` added before the successful rebuild. Worker Ethernet now limits in-flight frames to 64 in each direction with acknowledgements; excess frames are dropped, and `.build/checks/guest-worker-client-r3.txt` and `guest-worker-client-network-r2.txt` pass including bounded queue behavior and real local relay. The exact r3 package passed `.build/checks/guest-worker-desktop-sealed-csp-r3.txt` on workstation root and `/hidden/` with the live-style CSP, real signed relay, file workflow, two independent shells and 1.1.1.1 ping. It also passed i36 root `.build/checks/guest-worker-desktop-i36-scheduler-r1.txt`, Linux ready 126.6 s, full workflow 135.2 s. r2 without the scheduler option passed full i36 after Linux ready 136.4 s and full workflow 144.5 s (`guest-worker-desktop-i36-r2.txt`); an earlier r2 run timed out at the then-120 s boot bound, and a speech-blocked r2 completed full workflow in 125.2 s. The same Pi fixture with current live `verified-ids-r1` reached Linux ready in 135.5 s; its subsequent workflow test failed because the assertion expected the new app's save wording, not because boot failed. These individual runs show no large boot improvement or established regression. r3's Worker URL fragment selects v86's `scheduler.postTask` path when supported; Chromium on i36 supports it and CDP showed no nested scheduler Worker. Older browsers fall back to v86's original scheduler. A URL fragment preserves the canonical cache request. The unmeasured requirement is whether worker execution improves real 435-message chat catch-up on i36 while Linux and speech are active. Also test mobile/voice, worker bursts and complete current chat/chess before activation. Source/build/test changes were re-read and backed up on private box-git main `bb2b68543987f199b9354af32a01dfd8fcdb1ae1`. Live remains `native27-verified-ids-r1`; full goal remains active.

Superseding the unmeasured note: sealed r3 passed simulated phone-sized touch and real on-device speech-to-text to the editor (`guest-worker-mobile-voice-r2.txt`); r1 was interrupted because the test did not focus the editor window before dictation. Physical phone was not tested. Source/test backup is private box-git main `93f32d2000a2cee91e88a7112bfc0aa66a25b000`. The user authorized live testing, so r3 was temporarily activated using the managed controller; live i36 fresh full-desktop catch-up of the same 435-entry target completed in 147187 ms (`live-i36-worker-full-load-r1.txt`) vs earlier main-thread guest 139590 ms (`live-i36-full-load-profile-r1.txt`). Instrumentation adds overhead; these are single sequential runs and do not prove causation, but show no catch-up improvement. Disposable account and owned driver cleaned. The previous `native27-verified-ids-r1` was restored with the managed controller and renewal policy; config SHA256 is again `4c1a1dcb236bbe0ac50af84f81bf38aa76d8e05f07b8c08252e219d082f2fa63`, rollback receipt `/srv/codi-connected/guest-worker-rollback-result.json`, original worker activation receipt `/srv/codi-connected/guest-worker-r3-activation-result.json`. Root returned 200 and issuer/steward/guest/official/chess services active. The owned temporary uploads, scripts, and inactive worker release on box-webhost were removed after verifying the active release and role commands. Local sealed candidate/source and backup remain for investigation. No main-thread responsiveness comparison or complete live group/chat/chess test was performed under the worker; do not claim worker improves UX or discard the larger goal. Next investigate actual repeated IndexedDB and rendering costs and, if useful, measure responsiveness under load before choosing worker deployment. Full goal remains active.

### Latest user direction — server-backed scope

The user explicitly removed P2P optimization goals for now: a working server-backed site is sufficient. This supersedes older P2P-first, island/8k, automatic peer reorganization and related optimization milestones in the original goal attachment. Preserve the newer direction: registered accounts, offered channels only (General Chess Chat), server relay and honest pending/sent/delivered states, and a clean chess app with the easy Stockfish exhibition and separate conversation. Focus on end-to-end usability, durable server history, login, recovery, and genuine user-facing reliability; do not make P2P scalability a release gate. Keep any completed infrastructure only where it serves that scope. The user's live test site has no real users and can be used for authorized tests. Goal remains active.

An already-started server-history IndexedDB read optimization is locally under test: `assets/desktop/channel-archive.mjs` reads an accepted head and its history nodes in one readonly snapshot while retaining hash, checkpoint and permission verification. Workstation archive batch (62 checks), cross-head race (59), missing history (60), and checkpoint-gap (83) tests passed; `.build/checks/atomic-head-pi-r1.json` is being produced by the active i36 test session 25542. The prior instrumentation sampled 193 of ~3092 archive transactions: 114 samples showed tree-node reads, 29 current-head node reads, 21 current-head row reads; full traced load of 435 entries took 140.5 s with instrumentation. The candidate is not deployed and should be kept only if the bounded benchmark shows a meaningful result; avoid further speculative P2P or scale work. Source and running-test state must be checked before continuation.

Latest user direction: server-backed messaging must be fast; new messages must not remain Pending for 30 seconds while older history verifies. Show Sent only when the actual authenticated server has accepted the message, retain the original until local history verifies, and keep Delivered honest. Resolve old-history loading in the background; optimize the real small-group path rather than P2P scale. The atomic-head Pi test completed PASS (62 checks, 4075 ms for 68 blocks vs 4062–4070 ms in earlier verified-ID candidate runs), so its source change was reverted exactly; no live change. Focus on the server acknowledgment and send path next.

Local fast-server candidate: session tracks actual successful same-origin server acceptance separately from its durable pending originals, exposes accepted IDs to Chat, and signs queued originals as an ordered chain so multiple messages can be sent before old history catches up. Chat immediately shows `Sent` for those receipts; it still retains them until local history verifies and only shows `Delivered` after an independent account's receipt. `.build/checks/fast-server-held-r2.txt` passed actual server/issuer and compiled app: three messages while history returned 503 were accepted in order and displayed Sent in 362 ms on the local fixture, pending originals remained durable, and later verified recovery completed; restriction/review test also passed. `.build/checks/fast-server-full-regression-r1.txt` passed chat moderation, blocked/offline, reconnect and chess recovery. Sealed local candidate `.build/releases/fast-server-r1` manifest `0f602d4eb78552cfff71658a88e257dbd6924b49d91d153ba780a5e7b5054f62`; not active. The receipt-fault/offline/reconnect test is still running as session 26231, output `.build/checks/fast-server-receipts-r1.txt`. Private box-git backup process is running as session 54978. A public i36 first-send and historical catch-up profiler is prepared in `scripts/live-fast-chat-i36-profile.py`; verify its behavior and clean disposable state. After receipt and backup pass, use managed staging/activation and run that bounded live test. Current live release remains `native27-verified-ids-r1` (config SHA `4c1a1dcb236bbe0ac50af84f81bf38aa76d8e05f07b8c08252e219d082f2fa63`). No P2P scale work; goal remains active.

Superseding the staged note: the receipt-fault and reconnect checks passed, and the source and tests are backed up on private box-git main `e5484386d509821086a5c545d48921b7ee550109`. The managed activation installed `/srv/codi-connected/releases/native27-fast-server-r1` with the manifest above; managed config SHA256 is `1074a760c880331baa268b419e6311568413728f02758ea9ffbba44dd47ab044`, activation receipt `/srv/codi-connected/fast-server-r1-activation-result.json`. Owned temporary staging files were removed. A public i36 full-desktop run with 435 old entries (`.build/checks/live-fast-chat-i36-r1.txt`) showed server-confirmed Sent after 10,906 ms and full history recovery after 136,067 ms. The disposable account and associated author metadata were removed; the signed test message remains in official history. The user wants faster than this. A second instrumented i36 run is underway, recording request timing without message content in `.build/checks/live-fast-chat-i36-trace-r2.txt`; diagnose the actual send delay before deciding the next change. The scope remains server-backed chat and chess, not P2P optimization.

The user clarified that the Pis are network test endpoints, not target devices for performance. An i36 trace showed most of its send delay before server submission, so the session now yields background history replay while an outgoing server submission is in flight. This priority change passed held-history and chat/Chess regression tests, and a live workstation full-desktop first-send test showed server-confirmed Sent in 754 ms (`.build/checks/live-fast-chat-workstation-r1.txt`). The live three-account test confirmed offline pending/reconnect and exactly-once delivery; fresh test browsers needed 26.1 seconds to replay the artificial history, and old receipt polling added 26.7 seconds (`live-fast-priority-small-group-r1.txt`). The user clarified that this is all disposable prototype test history. The General chess chat is linked by the current featured chess game; do not delete or rotate it without also maintaining that relationship. A proposed incomplete reset script was discarded rather than breaking the game. Test-history cleanup remains outstanding.

Normal server-history polling is now 1 second and delivery-receipt polling 3–3.5 seconds (limited profile 5 and 10 seconds). This change passed packaged regression and distinct-account receipt-fault/reconnect checks, and is live at `/srv/codi-connected/releases/native27-fast-poll-r1`, manifest `21edb52f13f882880e8d878f4d21c7acadf39cb48d9b8565105a5619b5370664`, managed config SHA256 `0e86721d694865ba3fbefc1424e271fe7642d68a313dba99ed7798a21373850b`, renewal backup `/var/backups/codi-renew-before-fast-poll-r1.service`, activation receipt `/srv/codi-connected/fast-poll-r1-activation-result.json`. Private box-git backup `93901a749f21d1b83b00d1fd5fdd316a42451150` contains the polling source. The live three-account reconnect test (`live-fast-poll-small-group-r1.txt`) showed all messages exactly once in 26.9 seconds including fresh-browser test-history replay, and all confirmed delivery 1.5 seconds afterward. A live three-browser speed test after initial catch-up is running as session 70251 with output `live-fast-poll-group-speed-r1.txt`; inspect before claiming its result. This test creates signed disposable messages; test account metadata is cleaned but chat blocks remain. Do not describe these as real user history. The user wants fast server-backed messaging, not Pi optimization or P2P scale. The full goal remains active.

The workstation three-browser speed run completed PASS: once all browsers were caught up, all three received three simultaneous messages in 0.85 seconds, and all three delivery confirmations appeared within a further 6.93 seconds. The disposable accounts and actor metadata were removed; messages remain as test blocks. A ten-browser workstation chat-only test is running as session 8746, output `live-fast-poll-ten-speed-r1.txt`. This is same-network and intentionally blocks the Linux and voice assets so that ten browsers do not pretend to be ten computers sharing one CPU; it does not prove phone or independent-network performance. The user has no real history, and the test-data cleanup still needs a safe coordinated reset of the chat and featured-game relationship.

The ten-browser run FAILED: all ten messages remained pending beyond 30 seconds; diagnostics show issuer official authorization HTTP 429s followed by official challenge 403s when abandoned challenges accumulated. The fast receipt polling hit the shared 60-per-minute upstream authorization limit. All ten test accounts and actor metadata were removed. The aggressive poll release was rolled back to live `native27-fast-priority-r1`; managed config SHA256 is again `eec99532c5b13e23f004a2aa22a77147a7adf68b124ec827f62fabd5cc88c420`, receipt `/srv/codi-connected/fast-poll-rollback-r1-result.json`. This preserves fast Sent but delivery checks again run approximately every 20–25 seconds. Do not claim the 10-person fast path passes.

Local candidate gives the two official authorization paths their own bounded limit at 20 times the configured login rate, retaining the ordinary login rate, origin validation, one-use request-bound signatures, challenge capacities, and existing session checks. `scripts/official-shared-rate-check.py` passed actual WSGI checks for the separate limit, exhaustion, rejected origin and unaffected login limit. Sealed `.build/releases/shared-chat-rate-r1` combines this server fix with fast polling; manifest `643a86a37d59a341552dec022724d05112db6bcdef731b0ca658c3103a2b7130`. Receipt fault/reconnect regression is running as session 74555 (`shared-chat-rate-receipts-r1.txt`). The candidate remains local and must pass before guarded activation and a fresh ten-user live test. The user specifically wants server-backed speed and no 30-second pending; investigate and fix further failures rather than masking them. Test-data chat/chess cleanup remains outstanding.

Superseding the staged note: the receipt failure, two-account, same-account exclusion and reconnect checks passed; source backup is private box-git main `8b0da6a689134e7cf61b24bd68f0164c862e12e0`. The combined fix is live at `/srv/codi-connected/releases/native27-shared-chat-rate-r1`, manifest above, managed config SHA256 `3d5a1386586b1a6e6ef6420261811c8ac88bccc81c34e833aef27c8373a2eb3f`, renewal backup `/var/backups/codi-renew-before-shared-chat-rate-r1.service`, activation receipt `/srv/codi-connected/shared-chat-rate-r1-activation-result.json`. Owned uploads/scripts were cleaned. Ten-browser same-workstation chat-only retest is running as session 92515 with output `live-shared-chat-rate-ten-speed-r1.txt`; inspect results and any diagnostics before reporting success. Test accounts are cleaned by the harness; signed test messages remain in prototype chat. The targeted chat reset is not implemented because the featured game currently binds its channel; do not delete it without handling that relationship.

The ten-browser retest completed PASS: once ten browsers had caught up, each received all ten messages in 4.24 seconds and all senders had distinct-account delivery confirmation within another 4.29 seconds (`live-shared-chat-rate-ten-speed-r1.txt`). Ten disposable accounts and associated author metadata were cleaned; signed test messages remain. This is one workstation and one network, with guest Linux and voice assets intentionally blocked; it does not establish physical phone, separate-provider, or full-desktop ten-device performance. User clarified Pis are network paths rather than performance targets, and all current old chat is disposable test data. Cleanup requires a tested coordinated replacement of the current chat and featured chess binding; avoid damaging chess or treating test data as user history. Goal remains active.

Superseding the cleanup outstanding note: the user clarified there is no user history; all old content was prototype testing. `scripts/reset-prototype-chat-chess.py` and the guarded webhost wrapper were tested with real signed fixture provisioning, including a late injected failure that restored the old database and keys; the tests also checked preservation of a system role and migration of channel bans. The live coordinated reset succeeded, removing the 458-block test chat, 45 test games and 91 unreferenced retired test keys, while leaving the system channel, account data and other channels intact. Public General chess chat is now `AFCq2K9vVO04w8krz58g41BUXq6z0ux3a8oKOo0mSQM` with height 0; the new featured game is `3Iddef0ms8zUiMT3kV4Ld_6RUdqeyylO_ZQZF0tOqyg` and is linked to that chat. Both official and chess services restarted healthy; public verification observed the new game advancing. An actual fresh registered Chrome opened Chat and Chess with all 64 squares without sending a message (`live-reset-chat-chess-ui-r1.txt`); its test account and metadata were removed. Reset receipt `/srv/codi-connected/prototype-chat-chess-reset-result.json`; temporary recovery copy and owned remote scripts removed. Reset source and tests backed up on private box-git main `09858491823e705a732bb91618197eabe9678138` (wrapper hash rechecked). This intentionally creates new channel IDs, so existing test-browser tabs may need to reopen the apps. Ten-browser delivery timings above were measured before the reset using the same live software, not remeasured against the empty channel. `scripts/live-fast-chat-catchup-profile.py` now discovers the offered channel rather than pinning the old ID. Remaining: physical phone/separate-network validation, live restart and recovery confidence, and ongoing usability/Chess work. User explicitly removed P2P optimization and Pi performance as current targets; goal remains active.

Live restart verification `live-server-restart-workstation-proxy-r1.txt` passed using two workstation Chrome browsers, the second through an SSH SOCKS proxy on i36 (its outbound address verified as `104.180.210.36`): both received a baseline; two messages remained pending while `codi-official.service` was stopped; both recovered on both browsers 3.3 seconds after restart without reload; and baseline plus both messages appeared after a browser reload and sign-in. Both routes use the same Internet provider, so this is not an independent-provider or physical-phone proof. Both test accounts and associated metadata were removed. An exact-content guard verified those were the only three chat messages before the tested coordinated reset removed them and replaced their linked demo game; this intentionally changed chat to `_Kb4ClZ7B_JAb0yuMitFB6Z9ok27GayOmZSkLIK1GmM` and featured game to `zDF21nAxJwu2t6oa39JvCoIMJi4zxBceG67J5ixlXVM`. Receipt `/srv/codi-connected/prototype-chat-chess-restart-test-cleanup-result.json`; temporary keys, recovery copy, and owned scripts cleaned. Fresh public Chrome opened the empty chat and linked chess board without sending (`live-restart-clean-ui-r1.txt`). Separately restarting `codi-featured-chess.service` resumed the same game from height 6 to 7 in 1.1 seconds, confirming actual live game continuity across the runner restart. Private box-git main `bcd3295b04a2848ca5398ee8154172fef7588251` backs up the restart harness and guarded cleanup. Physical phone/separate-provider checks remain unverified; goal stays active.

The user said they can test on cellular now. A disposable workstation Chrome is waiting in the offered General chess chat as exec session 21808, log `.build/checks/live-cellular-server-chat-r1.txt`; it expects `Phone check ecfbbb`, replies `Server reply ecfbbb`, and waits for `Got reply ecfbbb`, with a bounded ten-minute wait per phase and owned-account/metadata cleanup in `finally`. The user was given those instructions; inspect the actual session/log before reporting results or restarting anything. Do not remove the user's messages without explicit authorization. The test source and dynamic-channel scripts were backed up on private box-git main `38f8bfa541bf38052239e0865c628f7d0e031d97`. Four obsolete generated local worker builds were removed, freeing about 458 MiB; active and immediate rollback release are preserved.

The user reported Done after the cellular instructions. The workstation received `Phone check ecfbbb`, submitted `Server reply ecfbbb`, and its actual Chat view showed the user's `See server reply ecfbbb` confirmation. This establishes a two-way server-routed phone/workstation exchange, with the user instructed to turn Wi-Fi off; phone IP was not independently observed and latency was not measured. The harness expected the alternative exact wording `Got reply ecfbbb`, so it was interrupted after the observed confirmation and its finally block cleaned the disposable account and metadata. The interruption and actual observation are recorded honestly in `live-cellular-server-chat-r1.txt` and `live-cellular-server-chat-observation-r1.json`; the script now accepts both confirmation wordings. The user's `Test`, phone check, confirmation and server reply remain in General chess chat; these are the user's test messages and must not be deleted without explicit authorization. The site remains on `native27-shared-chat-rate-r1`. Goal remains active; physical cellular two-way messaging and live service restart have now been exercised, while multi-device group testing over independent providers and further UI/game work remain.

The shared Chess app's own chat had not adopted the fast server acceptance state: it incorrectly continued to display an accepted message as Pending. The source at `../served_apps_public/chess/index.mjs` now shows Sent only after server acceptance, Delivered only after another account's receipt, keeps unsent/review states, and excludes accepted messages from the pending count. Compiled Chess app real-server tests passed while history was held (`chess-chat-sent-held-r3.txt`) and with distinct-account receipts, same-account exclusion, offline recipient/reconnect, receipt failure and accessible delivery status (`chess-chat-receipts-r1.txt`). The sealed app-only update is live at `/srv/codi-connected/releases/native27-chess-chat-state-r2`, manifest `0c084a2d33e1af5b79ed1c9695d844df3d6192a6b2cc6f8c0643078d3d64c336`, managed config SHA256 `4fa4c495e15dfdb6e72187f05861cbe99abe7e43b58439ac932ad0302fd4aeb5`, activation receipt `/srv/codi-connected/chess-chat-state-r2-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chess-chat-state-r2.service`. Source and tests are backed up on private box-git main `0bb97d90b1dfc22cbd8029ac23788164f2e01a28`. A fresh public Chrome opened Chat and Chess and verified Chess displays the same existing phone test message (`live-chess-chat-state-smoke-r1.txt`); no new message was sent and disposable account/metadata were cleaned. User messages remain intact. Owned remote staging and the superseded local Chess build were cleaned. Goal remains active.

Chess previously showed an actual side to move while a new spectator was still catching up. The Chess app now displays Loading game until the signed official game history catches up, and an honest reconnecting message when offline or recovery fails. `chess-loading-ui-r1.txt` passed a real-server browser test with held game history, catch-up, offline and reconnect. The app-only fix is live at `/srv/codi-connected/releases/native27-chess-loading-r1`, manifest `24a8d6756306da2fa79eecb2b9e11e9877a19f65d8c3474f93be6c8a0c3e0270`, managed config SHA256 `d4520bf72f32e582c96b814c606472cde377a832256d99bd3fb73d9ea72267bd`, activation receipt `/srv/codi-connected/chess-loading-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chess-loading-r1.service`. Private box-git main `8baa36c7917f8ba0fbba6833576ea7ee23aef10d` backs up the source and tests. `live-chess-loading-ui-r1.txt` passed on a fresh public Chrome with artificially delayed game history and confirmed the user's existing cellular chat message was still visible in Chess; test account/metadata were cleaned.

The first long-running live spectator test (`live-featured-chess-spectator-r1.txt`) was interrupted during the native service upgrade when its browser JavaScript context disappeared; its finally block cleaned its disposable account. This does not prove exactly why the page context disappeared or that an open app survives an upgrade. The spectator did not reach the end of its game, so do not claim a complete live game with spectator from this attempt. No user messages were deleted. Investigate the upgrade interruption and repeat a bounded spectator test against the now-live release. User removed P2P optimization goals; goal remains active.

A second bounded spectator run is actually running as exec session 78966, log `live-featured-chess-spectator-r2.txt`, with full Linux/voice assets enabled and a disposable account. It opened a 64-square board and correctly displayed Loading game while history caught up; it waits up to 15 minutes for the current game to finish, then up to 150 seconds for the next-game control and verifies switching. Poll the same session before drawing conclusions or starting another one. Its finally block cleans the disposable account and metadata. The user's messages must remain intact. The observed earlier interruption occurred during a live native update, but whether it was a page reload, renderer failure, or another event is unproven; do not claim a root cause or seamless upgrades.

Independent read-only live Chrome verification `live-chess-readonly-completed-r2.txt` reopened an actual completed 87-move featured game (`Game finished: 1-0`), then returned to the currently running game after it had loaded through position 78. It sent no chat and cleaned its disposable account and metadata. An initial r1 check considered the Loading state enough to claim return to live; r2 strengthened the condition to wait for an actual side to move. This is proof of reopening an existing signed completed game and returning to live, not yet proof that a spectator watched a game through its finish; the separate session 78966 remains running for that.

The read-only replay test is backed up on private box-git main `c888dab78556c12f2cb0858077a35b2e2e4b715e`. Root and `/desktop/` returned HTTP 200 and the issuer, steward, guest, official and featured-chess services were active after the update.

The full-desktop spectator (`live-featured-chess-spectator-r2.txt`) observed the live Stockfish game finish at position 95 with result 1–0, then selected the next game and saw its board while it was still loading. Its original next-game assertion allowed Loading, so it does not prove that particular browser finished catching up to the next game; the separate read-only r2 test above did verify another spectator returning to a fully loaded live game. The spectator's disposable account and metadata were removed. User chat was untouched.

An isolated, operator-created temporary channel was used to test ten workstation browsers, one routed through i36's verified public IP. All received all ten messages in 3.5 seconds, but delivery confirmations took up to another 27.11 seconds (`live-temp-ten-network-r1.txt`). Six brief official challenge 503s caused a 20-second receipt retry delay. The test accounts, their metadata, isolated channel, test messages and owned temporary key were cleaned; General chess chat retained all four user/phone-test messages. Both IPs share one provider; physical cellular two-way chat was separately verified, but this is not a ten-person independent-provider proof.

The receipt client now retries transient 503s with bounded 1–8-second exponential backoff rather than waiting at least 20 seconds. Real-server browser test `fast-receipt-retry-r1.txt` passed a deliberately busy receipt, observed a retry after 2030 ms, and retained same-account exclusion and offline/reconnect delivery semantics. The update is live at `/srv/codi-connected/releases/native27-fast-receipt-retry-r1`, manifest `ecdd7fa68f4a3dcf7f500d1f0a9b77b5c60618960af692b4a1051c5849f0efce`, config SHA256 `80aa2e6008148353ba607e21a84fbddbdcdc8549c48b39cedd71598bde96aa21`, receipt `/srv/codi-connected/fast-receipt-retry-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-fast-receipt-retry-r1.service`. Private box-git main `19b2ee328443a0ce9241fee888b5f1edfcae9b54` backs up the change and isolated-test tools. A new isolated ten-browser two-IP test is running as exec session 67323, log `live-temp-ten-network-r2.txt`; poll this exact session and confirm temporary channel and account cleanup before reporting its outcome. User chat must remain intact. Goal remains active.

The ten-browser two-IP retest completed PASS: all ten messages reached all ten browsers in 3.62 seconds, and all distinct-account delivery confirmations followed within another 2.05 seconds. Diagnostics show six actual temporary 503 challenge responses, so the fast-retry result exercised contention rather than only a clear path. The test removed its ten disposable accounts and metadata, isolated channel, test messages and key; owned remote staging/helper scripts were removed. Public checks confirmed General chess chat remained at four messages, no temporary test channel was visible, featured chess still links the same chat, and issuer/steward/guest/official/chess services were active. One workstation browser used i36's verified outbound IP, but both test paths share a provider; a physical cellular two-way test was separately passed. Do not claim ten independent-provider devices. The spectator script's next-game assertion was corrected locally to require an actual side-to-move rather than accepting Loading; prior spectator evidence remains limited as stated above. Goal remains active.

The corrected spectator assertion is backed up on private box-git main `651dbb2ba48452858e9cecf9eb518aea351168cc`.

After the receipt retry release, `live-fast-receipt-final-smoke-r1.txt` verified that a fresh registered public Chrome opens both Chat and Chess and that Chess still displays the existing cellular test conversation. The test sent no messages and removed its disposable account and metadata.

For the outstanding ten-participant test including cellular, isolated temporary channel `Temporary test d47db8c054da` is active with nine disposable workstation browsers waiting for the user's phone. The user was asked to send `Phone d47db8c054da`, then `Phone saw group d47db8c054da` after seeing the nine messages; the prompt explicitly states this temporary channel and its test messages will be removed. The actual orchestrator is exec session 38910, log `live-temp-phone-nine-r2.txt`; poll that exact session, do not restart merely because a poll times out. The helper's `phone-test` cleanup only removes that channel if every stored operation has an allowed exact test message and every writer has an allowed signed operation; it never deletes the user's account or General chat, and it refuses unexpected content/reviews. The user-facing original conversation currently remains untouched. First r1 attempt failed on a test-script syntax error and confirmed its temporary channel was removed; r2 corrected the syntax. A local fixture verified the cleanup rejects unexpected messages and preserves the main channel. The user asked earlier to use the live site for testing; the goal remains active.

The isolated phone group test sources are backed up on private box-git main `4a1b7f6bfd92cac2cc119c8b79e1388a17e8fc48`. A read-only production check verified that the nine current test writer records all match the signed operations that the cleanup guard recognizes. Session 38910 is bounded and still running; if the user cannot participate, the script times out and its finally blocks attempt to remove only owned test accounts and the guarded temporary channel. If unexpected content is present, it deliberately preserves the channel and reports cleanup failure rather than deleting unrelated content.

During the wait, all nine test browsers were observed with zero pending messages and the normal saved status. Sampled diagnostics included brief official challenge 503 responses during background receipt polling, but no stuck messages were observed. The user's ordinary General chess chat remained at four messages; no phone message had appeared in the temporary channel at that sample. The group test remains a bounded wait, not a completed independent-network ten-participant result.

Session 38910 subsequently timed out after the bounded phone wait without receiving either requested phone message. This was not a chat delivery failure and does not invalidate the earlier separately verified two-way cellular exchange; it means the combined nine-workstation-plus-phone group test did not run to completion. Its finally blocks removed all nine disposable accounts and their metadata and the owned temporary channel and key. The owned remote helper was removed; public checks confirmed no temporary test channels and General chess chat still at four messages. Do not claim a simultaneous ten-participant cellular result. Goal remains active.

Idle sessions were repeatedly submitting receipt checks even after all their own messages had confirmed delivery. The session now wakes a receipt check when a new verified server head arrives, checks every three seconds while its recent outgoing messages remain unconfirmed, and slows to 30–31 seconds after everything is confirmed. A head change during an in-flight receipt forces a fresh check instead of applying a stale result. `official-idle-receipt-r1.txt` passed busy retry, zero idle receipt requests in an eight-second sample, a new message waking an idle recipient and confirming delivery in 4.3 seconds, same-account exclusion, and offline/reconnect behavior; the full signed Chat/Chess regression `official-idle-receipt-regression-r1.txt` passed. The service-only release is live at `/srv/codi-connected/releases/native27-idle-receipt-r1`, manifest `1695ec65541333a4826a4725a03b2b8a247b426e7da23cb3a8201bfad122481d`, config SHA256 `1369a8054c92731057ec1042a884137de9e78769766f366616b02195d85748d5`, receipt `/srv/codi-connected/idle-receipt-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-idle-receipt-r1.service`. Source and checks backed up on private box-git main `2aed8210409a53f7f0a2b62dd9369db3adf5219f`. An isolated ten-browser test across two same-provider IP paths is running as session 22008, log `live-temp-ten-idle-r1.txt`; it also samples idle receipt request counts after confirmations. Poll the same session and verify its cleanup before claiming the live outcome. User chat must remain intact; the combined cellular group test was not completed.

Session 22008 completed PASS: ten sessions received all ten messages in 3.51 seconds and all distinct-account delivery confirmations arrived in another 2.04 seconds. After a three-second settling period, the ten sessions made three receipt requests total during an eight-second idle sample (`live-temp-ten-idle-r1.txt`); this is a single sample, not a bandwidth benchmark. The ten disposable accounts, isolated channel, messages, key and owned staging files were cleaned. Public checks confirmed General chess chat still has its four existing messages, no temporary channel remains and featured Chess still links that chat. Fresh public Chrome opened Chat and Chess and displayed the existing phone message (`live-idle-receipt-final-smoke-r1.txt`), with no new chat message; its test account was cleaned. Both IP paths use one provider; the simultaneous cellular group test remains incomplete. Goal remains active.

The live idle group test scripts are backed up on private box-git main `9710323c0ec6477854960497335006c7a9c29e8e`.

The live release also passed an isolated ten-session recovery test (`live-temp-ten-recovery-r1.txt`): three sessions, including one routed through i36's verified public IP, went offline and retained their own pending messages while the other seven sent. After reconnection, all ten recovered all ten messages exactly once without reload in 3.4 seconds, and all senders observed distinct-account delivery confirmation within another 1.6 seconds. Sampled non-200 requests were status 0 from the deliberately offline sessions. The ten disposable accounts and metadata, isolated channel, messages, key and owned helper were cleaned. Public verification confirmed General chess chat remains at its four user/phone-test messages, no temporary channel remains, and featured Chess links the same chat. This test used workstation browsers with Linux and voice assets blocked and two IP paths on the same provider; it does not prove a simultaneous cellular/independent-provider group. Source test tools backed up on private box-git main `bc40a9ce4afc245fc155728936d55d820b451496`. Goal remains active.

The demand-aware receipt scheduling's in-flight head-change race was verified with an actual local issuer, writer and two registered Chrome sessions (`official-receipt-head-race-r1.txt`): the older receipt response was held while a second message was verified, then released; the newer head triggered a fresh receipt and the sender saw distinct-account confirmation in 2245 ms. Fixture accounts and browser sessions were cleaned. Subsequent public checks still showed four General chess chat messages, no temporary test channel, and active issuer/steward/guest/official/chess services. User messages remain intact. Goal remains active.

The receipt head-race test source is backed up on private box-git main `a671aab224607fe971b055b2ef3973c7748a4ad4`.

Current Chat and Chess app-view lifecycle was checked without sending messages. In a real local issuer/writer and browser fixture, `chat-chess-window-lifecycle-r2.txt` passed three open/close cycles per app: no app views, intervals or added online/offline listeners remained after each cycle; one shared General chat channel remained session-owned. A public Chrome check against the live build (`live-chat-chess-window-lifecycle-r2.txt`) passed three cycles with zero app intervals and no accumulating online/offline listeners; its disposable account and metadata were removed. The initial public r1 assumption that all online listeners should be zero failed: the one remaining listener was identified from its function as the shared `DeviceChannelSession` reconnect handler, which exists to keep session-owned delivery working. The corrected r2 verifies that its identity and count stay stable rather than suppressing the failure. This only covers Chat/Chess and tracked intervals plus window online/offline listeners, not every application or every kind of resource. User chat was not changed. Goal remains active.

The current Chat/Chess lifecycle check scripts are backed up on private box-git main `2c3d60948db3136e650b9c2933a3115c24a69cf4`.

The stronger public issuer-restart test initially exposed a real bug: registered sessions were held only in issuer RAM, so a restart caused signed renewal to fail and the desktop to reload. Registered session bindings now persist in the private issuer SQLite database with only a hash of the bearer token, the public key, account generation and existing expiry. Logout, account disable/password-generation revocation, expiry and wrong signing keys remain enforced; anonymous sessions remain RAM-only. `issuer-persistent-session-local-r3.txt` passed 97 native issuer tests including the actual ICE preference extension and the first deployment's record format. First live implementation rejected an extra `_ice_preference` field on restart, temporarily taking the issuer down; one test record was normalized to restore it and the failure was corrected. Do not interpret `live-identity-restart-window-r3.txt` as an unaided pass: it required that intervention. The corrected release then passed unaided full-desktop public Chrome test `live-identity-restart-window-r4.txt`: a signed-in disposable account had Chat and Chess open, detected an issuer outage, and recovered signed renewal in the same page with both windows and existing phone message intact. Disposable account and its session metadata were deleted. This does not prove recovery from browser or computer crashes, and existing RAM-only sessions needed a sign-in once at initial deployment.

Current managed release `/srv/codi-connected/releases/native27-persistent-session-r3`, manifest `6b34635cdf6ac1cc6714e6d39f8f416de59a9d8e8a6a2c64341fdf93ee424778`, config SHA256 `72fa862d8d66c6d5b424cabe5b30b086a73da323d86200439c5afc4a01813621`, receipt `/srv/codi-connected/persistent-session-r3-activation-result.json`, renewal backup `/var/backups/codi-renew-before-persistent-session-r3.service`. Private issuer DB backup made before migration `/var/backups/codi-issuer-before-persistent-session-r1.sqlite3`; do not restore over newer account state without careful recovery. Source/test scripts backed up to private box-git main `6cfcf77`. Temporary local Git checkout, unused r2 build and remote transfer directories removed. Root and /desktop returned 200 and issuer/steward/guest/official/chess services active after live restart. Goal remains active.

Chess conversation updates rebuilt the message list every five seconds, closing an opened spam-original disclosure and disrupting the reader's place. The Chess app now restores opened disclosures by message ID and preserves scroll position for readers above the bottom; a reader already at the bottom follows new messages. A focused built-app Chromium test `scripts/chess-history-view-check.py` passed disclosure/reading-position preservation and bottom-follow behavior with simulated snapshots. The real issuer/server test `chess-history-view-real-server-r1.txt` passed server acceptance while history was held, recovery, Sent UI and blocked-account review/resend. Public full-desktop Chrome smoke `live-chess-history-view-smoke-r1.txt` opened Chat and Chess and displayed the existing phone message without sending; the disposable account/session and metadata were cleaned. The spam disclosure/scroll behavior itself was exercised locally, not with an actual live moderation event.

Current managed release `/srv/codi-connected/releases/native27-chess-history-view-r1`, manifest `92500dea6fc6b90589bdebf90b81d21ddd29b9922101b20150afe397a27f1db3`, config SHA256 `63e947bb64a9edce0f43a4392d1dad095e44ca44f0da78922a918db4ffe4eec6`, receipt `/srv/codi-connected/chess-history-view-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chess-history-view-r1.service`. Only the Chess app public graph changed; native and network protocol bytes remain unchanged. Root and /desktop returned 200 and issuer/steward/guest/official/chess services were active. `served_apps_public/CONTRIBUTING.md` now labels the older disabled-chat/P2P-first notices historical in light of current user instructions. Source and checks are backed up to private box-git main `bf48dd1`; temporary backup checkout and transfer directory removed. Goal remains active.

The root operator shortcut `/usr/local/sbin/codi-chat-admin` had retained a hard-coded retired General chat ID after the test-data reset; `list` failed and moderation/ban commands targeted the deleted chat. It now resolves the chat linked to the current featured game from the private official database and refuses missing, malformed, disabled or non-General targets. Current installed source SHA256 `ef859767931cbca30f0d8da489ee26171c73374808a1046519a18af12cb1974f`; old shortcut backup `/var/backups/codi-chat-admin-before-current-channel-r1.py`. `scripts/chat-admin-channel-check.py` passed target rotation and fail-closed cases, and the live `list` returned the actual four-message General chat. A disposable registered browser account was banned against that current channel; its message was rejected, remained in review after unban, and was explicitly discarded without sending (`live-current-chat-admin-r1.txt`). The disposable account, session and restriction metadata were removed; no existing chat message changed. Issuer, official service and Chess runner remain active. Source and tests are on private box-git main `6425005`; temporary source transfer and Git checkout removed. The command is still operator SSH/sudo, not a browser administration interface. Goal remains active.

The operator-signed spam marker was tested on the live service in a disposable, narrowly guarded channel (`live-temporary-spam-r2.txt`). One registered Chrome sent a unique test message; the channel's operator key marked that exact message; the Chat UI received the signed marker, displayed the moderator disclosure and kept the original open across an update. The first r1 attempt required a manual click after the harness clicked before the initial channel finished opening; r2 waited for readiness and passed unaided. The helper checks exact message, marker, participant and channel identity before deleting owned test channel data; both runs removed their channel, test account, session, metadata and key. Public checks found no temporary test channels and General chat still at height four; issuer, official service and Chess runner active. This is one browser and Chat, not a live Chess disclosure test or multi-recipient/large-scale moderation proof. Source and guarded cleanup on private box-git main `3c7f624`; temporary remote helper and backup checkout removed. No deployed product code changed in this test. Goal remains active.

Chess viewer now caches derived board positions for the current verified move list, extends only changed suffixes, invalidates a changed suffix, and skips rebuilding an identical board on chat/periodic refresh. Previous/Next select cached positions; changing games clears the cache. `chess-position-cache-check.py` passed unchanged DOM, forward/backward, history replacement and existing chat disclosure/scroll cases using built app and simulated snapshots. Public full-desktop Chrome `live-chess-position-cache-r1.txt` reopened an actual signed completed 69-ply game, stepped backward and forward to the exact same board, then returned to a fully loaded live game. Disposable account/session/metadata removed. This is a behavioral check, not a measured performance benchmark, and it does not alter official verification or game rules.

Current managed release `/srv/codi-connected/releases/native27-chess-position-cache-r1`, manifest `5fc407fc01bd8e7e5a886ce02bc9658e21a15affe4f1aa5fa3b4277dd3f8d86e`, config SHA256 `464e8bd0b89a15cd6c3ca18176b0e371713e937e067b5cccd1ac363c4ea402a3`, receipt `/srv/codi-connected/chess-position-cache-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chess-position-cache-r1.service`. Native/guest security and network protocol bytes unchanged. Root and /desktop returned HTTP 200; issuer, steward, guest, official and featured-chess services active. Source and checks backed up to private box-git main `593fd37`; temporary transfer and backup checkout removed. Goal remains active.

Chat and Chess now label a message from another browser on the same registered account as `You` after the official server's author-name lookup confirms its account name. Chat also applies own-message styling. Pending/receipt attribution still uses the actual actor and a second session on the same account does not qualify as another recipient. `official-same-account-label-r1.txt` passed a real local issuer/official service with three Chromium sessions: same-account Chat/Chess displayed You, a different account saw the verified sender username, and same-account receipt was excluded. Public `live-same-account-label-r1.txt` passed with two separate browser profiles on one account in an isolated guarded channel; that channel, its exact test message and key, disposable account, session rows and metadata were removed. This live check covered Chat; the Chess name-label check used the real local service. General chat remained at height four, no temporary test channels remained, and issuer/steward/guest/official/chess services were active.

Current managed release `/srv/codi-connected/releases/native27-account-label-r1`, manifest `bcc7b10c1deebf1ad8904d52b66e8ff6d036df4154ec5eb4729a56233be02334`, config SHA256 `65873859b95b565bf0383327ec2f440453d3967beed304b0c9b0ef83ab9533f2`, receipt `/srv/codi-connected/account-label-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-account-label-r1.service`. Only Chat/Chess public app graph changed; native and protocol security bytes unchanged. The first activation attempt found the normal scheduled root-renewal job holding the controller lock and made no changes; after that job finished, the guarded activation succeeded. Source and tests backed up to private box-git main `1f44a02`; temporary transfer, helper and backup checkout removed. Goal remains active.

SYSTEM had continued to autojoin in the background once device-history storage consent and persistence were already granted, but the current simplified Chat explicitly hid it. Chat now lists the operator's SYSTEM channel alongside General chess chat, keeps General as the default, and explains SYSTEM is read-only with composer disabled. `system-chat-app-check.py` passed a built-app Chromium test with simulated snapshots. Public full-desktop Chrome `live-system-chat-r1.txt` passed with a fresh disposable account and persistent storage pre-granted: one background channel joined before Chat was opened, General was the default, and existing SYSTEM announcements were visible and read-only. The test sent no messages and removed account/session metadata. Background join depends on the existing storage-consent/persistence grant; SYSTEM events do not currently cause a desktop pop-up, and this check does not prove a newly published live announcement appears while Chat is closed. Maintenance warnings have their separate existing mechanism.

Current managed release `/srv/codi-connected/releases/native27-system-chat-r1`, manifest `630864f7aa2fa8a891b90ba959704d6672df10338f0267a81ac79f4bd48c50e5`, config SHA256 `5756254b437641cbb2bdefa5f29a366c35939b2c185bb089ac3a029006f390c2`, receipt `/srv/codi-connected/system-chat-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-system-chat-r1.service`. Only Chat public app graph changed; native and network protocol bytes unchanged. Root and /desktop returned 200; issuer, steward, guest, official and Chess services active. Source and test scripts backed up on private box-git main `e171bb9`; temporary transfer and backup checkout removed. Goal remains active.

New, verified SYSTEM announcements now appear in a persistent desktop notice even with Chat closed. The session retains a bounded SYSTEM view until network shutdown. On the first visit with a given browser/account/channel it records the latest verified message as a baseline without popping up older messages; afterward it shows the newest unseen verified operator-authored announcement, including one recovered after being away, and records dismissal in browser localStorage. Earlier messages remain in Chat → SYSTEM; clearing browser data resets the baseline. Background monitoring requires the existing persistent-storage grant. No claim is made for browsers that are closed or operating systems that suspend the page; they recover on return. The notice is text-only and can be dismissed; long notices are scrollable and constrained on small screens. Network shutdown closes its session-owned view and removes any visible notice.

`system-notice-cursor-check.py` passed caught-up-only baseline, operator-author filtering, missed-message recovery, acknowledgement persistence and safe text rendering in Chrome. `system-notice-network-r3-check.py` passed actual cryptographically signed local SYSTEM history, initial lookup retry, background delivery with Chat closed and network-close cleanup. Its r2 predecessor's final assertion incorrectly read readiness after deliberately closing the network; r3 captures readiness before close. Public Chrome `live-system-notice-fixture-r2.txt` passed the deployed desktop with signed test fixtures injected only into that browser, no real SYSTEM message posted, and cleaned its disposable account. Initial r1 cleanup used a shadowed name and failed; the exact account was separately removed and the harness fixed. The first mobile-sized check `live-system-notice-mobile-r1.txt` found that r2 changed the unreferenced flat stylesheet rather than the page's versioned stylesheet; r3 fixes the packaging. `live-system-notice-mobile-r2.txt` then passed a 390x690 emulated viewport with a long signed fixture message and reachable dismiss button. This is not a physical Android test or a test that actually published a new real SYSTEM event.

Current managed release `/srv/codi-connected/releases/native27-system-notice-r3`, manifest `33c39d6c6ecd62723714843cdfbbd6dc5d8968ebccf301f852d89f19e05c7652`, config SHA256 `d0b6a939f5cfd2a130bf5e690dc3d440a0a8955188b35e04509a2baccbd1ba5d`, receipt `/srv/codi-connected/system-notice-r3-activation-result.json`, renewal backup `/var/backups/codi-renew-before-system-notice-r3.service`. Root and /desktop returned 200; issuer, steward, guest, official and Chess services active. Source and tests backed up to private box-git main `7d41efd`; temporary transfers and backup checkout removed. Goal remains active.

Installed root-owned operator shortcut `/usr/local/sbin/codi-system-admin` SHA256 `aadc09f67d25b974f081b7e41e11f281409e1399e007f72120ee81183b9d1821`. Usage on box-webhost: `printf '%s' 'Announcement text' | sudo codi-system-admin post`. It reads bounded UTF-8 from stdin, rejects blank/control/oversized text, and delegates through fixed `runuser -u codi-official` arguments to the existing private SYSTEM publisher with its key custody and lock. The announcement text is not passed as a process argument. `system-admin-command-check.py` passed fixed-command/stdin and validation checks, and `system-custody-check.py` passed seven isolated signed publisher/custody checks. A live blank-input rejection was checked and the SYSTEM head stayed unchanged; no actual live message was posted in this continuation. Public Chat previously verified SYSTEM read-only and its signed-notice fixture, but this turn did not independently bypass the live UI to forge a write. Issuer, official and featured Chess services active. Source/tests backed up to private box-git main `61ed789`; temporary transfer and backup checkout removed. Goal remains active.

A bounded live longer-history check used an operator-created disposable chat and one registered account in two separate Chrome profiles (`live-long-history-r1.txt`). The first browser queued 64 distinct signed messages in 5.528 seconds; all were server-accepted and locally verified after 25.303 seconds. After signing into the same account on a fresh second browser and selecting that chat, all 64 distinct messages were visible in 2.26 seconds. These are single-run same-workstation/same-network measurements, not guarantees, independent-WAN proof, or 32–128-person scale claims. The second timing starts at channel selection after sign-in and app readiness, and does not include Linux/voice loading. The narrowly guarded helper checked every stored operation had a unique expected test text and exactly one test author before removing the channel, test messages and key; the disposable account/session and metadata were removed. General chat remains at height four, no temporary test channel remains, and issuer/official/Chess services are active. No product code changed. Test sources backed up to private box-git main `f74aaa6`; temporary helper and backup checkout removed. Goal remains active.

Chess now automatically follows a newly offered game when the viewer is following the current game at its latest position, the old game's terminal state is verified/caught up, the result has been visible for at least eight seconds, and no manual game switch is running. Replaying moves or browsing a previous game suppresses automatic switching; the explicit Watch current game button remains available. `chess-autofollow-r2-check.py` passed a built-app Chrome fixture for no early result switch, automatic following, replay preservation, older-game preservation and unverified/loading state refusal. Actual public full-desktop spectator `live-chess-autofollow-r1.txt` observed a signed game finish 0–1 at position 94 and automatically follow the next fully loaded live game 36.2 seconds later. The disposable account, session and metadata were removed; no message was sent. The result is one live transition, not a guarantee of exact transition time.

Current managed release `/srv/codi-connected/releases/native27-chess-autofollow-r2`, manifest `58d165739fe9d5a4b1a712df7fc92141667983ba23541771db71839e463ba845`, config SHA256 `311a4ba15e100ed51f7413d01bc1344b516b7a6dd17b106641ba707167be999f`, receipt `/srv/codi-connected/chess-autofollow-r2-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chess-autofollow-r2.service`. Only Chess public app graph changed; native/guest security and network protocol bytes unchanged. Root and /desktop returned 200; issuer/steward/guest/official/chess services active. Source and test scripts backed up on private box-git main `805ec67`; temporary transfer and backup checkout removed. Goal remains active.

Chess now offers Download full game (PGN). It builds a standard PGN from the entire current verified move list and verified result, even when the viewer is replaying an earlier position. It disables export while official history is not caught up, has a recovery error, or has a gap; unfinished games use `*`. The UI states that PGN contains moves/result, not signed channel history; chat and private keys are not exported. Event labels are escaped by the existing ChessRecord PGN writer, unknown metadata uses standard unknown values, and the Stockfish demonstration is labeled accordingly. This is not a signed-proof or key export and currently requires caught-up server history rather than offline export.

`chess-pgn-check.py` passed the built app with unverified-history refusal, full-game export while rewound, exclusion of chat and an independent python-chess parse of a four-ply checkmate. Public full-desktop `live-chess-pgn-r2.txt` downloaded an actual completed signed 94-ply game, independently parsed all 94 moves and matched the 0–1 result, excluded existing chat, stepped through replay and returned to the live game. The test intercepted the download in its browser rather than saving a user file and removed its disposable account/session/metadata. `live-chess-pgn-r1.txt` was an earlier weaker parse test; r2 strengthened move count/result assertions.

Current managed release `/srv/codi-connected/releases/native27-chess-pgn-r1`, manifest `0e5279033002cbb52941a75c8078f3ab7c848fcc5660549a0f7265dab457d258`, config SHA256 `bd665bbe707eaecbcabe70f624b4c048fd74fe6284c80e6a17e02b7f5b70ab06`, receipt `/srv/codi-connected/chess-pgn-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chess-pgn-r1.service`. Only Chess app graph changed; native/guest security and network protocol bytes unchanged. Root and /desktop returned 200; issuer/steward/guest/official/chess services active. Source and test scripts backed up on private box-git main `42d79e9`; temporary transfer and backup checkout removed. Goal remains active.

Chess now offers a separate Signed game record JSON download alongside PGN. It includes the full signed game chain, invitation and public verification keys, and excludes chat messages and private keys. Export requires complete caught-up verified history and is bounded to 2,048 blocks and 16 MiB; it checks the saved head and parent continuity. `active-system/scripts/verify-signed-chess-export.py` independently validates the signed invitation and replays the legal signed moves against the existing server verifier. The keys included in a record prove consistency with those keys, not their real-world owner; use its optional `--expected-channel` with an independently trusted channel ID to bind the record to a known game. Verification currently requires the project Python environment rather than a browser UI.

`chess-signed-export-r2-check.py` passed a real signed local game export and verifier, with modified blocks, incomplete history and a mismatched expected channel refused. Public full-desktop `live-chess-signed-export-r1.txt` reopened an actual completed 48-ply game, downloaded and independently verified its complete signed record and result, excluded chat, stepped back and returned to live. It intercepted the download in its test browser; the disposable account/session/metadata were removed. This is one real game, not an offline browser export guarantee.

Current managed release `/srv/codi-connected/releases/native27-chess-signed-export-r2`, manifest `28f8bf62a3b5225bb62aca2d294d2a784b12c566d14f213b6d779f4b3dada1e6`, config SHA256 `07f1e0365ab665eaa21f01de0dd4a268fc3c39fa2c5793a169ff8f6531e235b5`, receipt `/srv/codi-connected/chess-signed-export-r2-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chess-signed-export-r2.service`. Only Chess app graph changed; native/guest security and network protocol bytes unchanged. Root and /desktop returned 200; issuer, steward, guest, official and Chess services active. Source and tests backed up on private box-git main `42a2412`; temporary transfer and backup checkout removed. Goal remains active.

Signed chat archive export is in progress, not deployed and not yet available in Chat. `active-system/scripts/verify-signed-chat-export.py` defines a bounded `codi-signed-chat/1` record and independently replays its public policy and signed chat/moderation blocks with the existing experimental public-chat verifier; the optional expected channel binds it to a separately trusted ID. `signed-chat-export-verifier-check.py` passed two actual signed messages and a signed spam mark, rejecting changed block data, missing history, incorrect head and wrong channel. The first fixture run failed because it assumed `public_channel` returned an invitation; the corrected fixture reads the policy from its own disposable registry. This verifies the verifier on a local fixture, not a downloadable live archive. Next build the Chat download from the session-owned verified history, ensure incomplete/cross-channel/racing histories fail closed, test with the real live app and preserve normal UI and cleanup. The signed record necessarily contains the public messages and moderation it exports; never include private keys. Source and fixture backed up to private box-git main `78681c5b60b5a0b07cdea8e74975f0b10c4bd5fc`; temporary backup checkout removed. No live product change. Goal remains active.

Chat signed-record export is now live under Chat → Nerd settings. The on-demand JSON record contains the complete caught-up channel block chain, public policy and keys, signed messages and moderation, and excludes unsent drafts and private keys. It refuses incomplete histories, changed channel/chain, more than 2,048 blocks or 16 MiB. `scripts/verify-signed-chat-export.py` replays the record; `--expected-channel` binds it to an independently trusted channel ID. Public-key signatures alone do not establish who owns a channel; exported public messages and moderation are readable to anyone given the file. Browser-side export requires caught-up local history, and verification remains a project-side Python command, not an in-browser viewer.

`signed-chat-export-browser-check.py` passed the packaged app in Chrome using a real local signed chain and spam mark, verifying unconfirmed-history refusal, unsent-draft exclusion and incomplete-history refusal; the mocked host supplies history pages, so this is not a real integration test. `live-signed-chat-export-r1.txt` then passed actual public full-desktop Chat, intercepted the downloaded file and independently verified all four current signed operations against the live General channel ID; it sent no messages and removed its disposable account and metadata. This is one small live history, not a scale or cross-network measurement. The first activation guard incorrectly expected the candidate as the previous release; it failed before any mutation. The corrected guard succeeded.

Current managed release `/srv/codi-connected/releases/native27-chat-signed-record-r1`, manifest `e5368f1b32a93193ffc66196e25958ef203c626c2d4fc68ef871ee58c043bf1c`, config SHA256 `40e8929cf40126c960eadc0326b4ffb47fdccccb1b4c0014a11bf583a5ec9af4`, receipt `/srv/codi-connected/chat-signed-record-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chat-signed-record-r1.service`. Only Chat app graph changed; native/guest security and network protocol bytes unchanged. Root and /desktop returned 200; issuer/steward/guest/official/chess services active. Source and checks backed up on private box-git main `769ba18651ebe0b45cefa7b34ccf45d099216a00`; temporary transfer and backup checkout removed. The independent-network ten-participant test and full goal remain active.

Chat and Chess composers now warn before attempting to queue a message above the existing 4,096-byte UTF-8 protocol limit. Textarea maxlength counts UTF-16 units and previously let some long emoji or non-English text through, producing an unhelpful send failure. The draft is preserved, and the warning clears on editing. Chess also retains a queue-failure notice across refresh and prevents duplicate concurrent sends or clearing a draft after the chat channel changes during a send. This does not change the protocol limit or send/receipt semantics.

`chat-unicode-composer-check.py` passed both packaged apps in Chrome with mock channel hosts: 1,025 four-byte emoji is warned and not queued, 1,024 is accepted by the mock, and a simulated storage failure retains the draft and error. `live-chat-unicode-r1.txt` passed actual public desktop Chat and Chess showing the warning and retaining the oversized draft; no message was sent, and its disposable account and metadata were removed. The live test does not prove a real 4,096-byte send or physical phone behavior.

Current managed release `/srv/codi-connected/releases/native27-chat-unicode-r1`, manifest `ac819be8bcec476a1f12d91e881943ca63f797559fa757e828fee7faaf9cb698`, config SHA256 `bf873220e29201b8190dcc2b77d1998dae2941dbdc73ff8126be1a39a04d9bc8`, receipt `/srv/codi-connected/chat-unicode-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chat-unicode-r1.service`. Only Chat and Chess app graphs changed; native/guest security and network protocol bytes unchanged. Root and /desktop returned 200; issuer/steward/guest/official/chess services active. Source and checks backed up on private box-git main `64e642ced39d40bc825865587fd2dd5fbf483e7d`; temporary transfer and backup checkout removed. The independent-network ten-participant test and full goal remain active.

Live full-desktop spectator disconnect/recovery was checked twice with an actual registered disposable Chrome and the running Stockfish exhibition (`live-chess-spectator-reconnect-r1.txt`, `live-chess-spectator-reconnect-r2.txt`). In r2 the spectator's existing cellular-test conversation was explicitly present; its browser was placed offline, the same live game advanced from height 16 to 18, and the spectator recovered position 18 and the unchanged conversation without reloading in 0.35 seconds. The downloaded recovered game record independently replayed its signatures and legal moves through height 18 against the expected game channel. No messages were sent; both disposable accounts and metadata were removed. These are single workstation/browser runs using simulated client offline conditions, not a completed game through the outage, a physical phone, an independent network or a ten-person test. Issuer/steward/guest/official/chess services active; no product code changed. Test script backed up on private box-git main `f0e95e9d0543b180147d533eedc43d933d8e3940`; temporary checkout removed. Goal remains active.

Prepared the independent-network group test without creating a live channel or starting browsers: `scripts/live-temp-phone-nine-check.py` now also deletes the disposable registered-session rows when removing its test accounts. The script and orchestrator syntax-check; the source change is backed up on private box-git main `0ab1b546958b43bb94f5f050936fc164c06eb490`. The test uses a uniquely named temporary official channel and guarded cleanup, preserving General chat; it expects nine automated workstation browsers and the user's cellular phone. Asked the user whether they are available now; no response was received during this continuation. Before starting a time-bounded test, confirm availability, stage `temporary-official-test-channel.py` on webhost, start the existing orchestrator and relay its exact channel and message instructions when ready. No group-test result or product change occurred. Goal remains active.

Chat now keeps a separate unsent draft for each channel within the current open Chat window. A successful channel switch saves the previous text and restores that channel's own draft; a failed switch leaves the original text intact, successful sending clears only the sent channel's draft, and closing the window clears these RAM-only drafts. This avoids moving a message into a different conversation. It does not persist unsent drafts across window closure, reload or browser crash; queued pending messages retain their existing durable behavior.

`chat-channel-drafts-check.py` passed packaged Chat in Chrome with mocked two-channel hosts, switching and restoring both drafts, failed switching, correct-channel send and sent-draft removal. `live-chat-channel-drafts-r1.txt` passed the actual full desktop: a General chess chat draft did not appear in read-only SYSTEM and returned on switching back; no message was sent, and the disposable account and session metadata were removed. Current managed release `/srv/codi-connected/releases/native27-chat-channel-drafts-r1`, manifest `1ba4f1715fd5ff91b4051ad7004ea16d5a945b49e67089ca5f177e9b673aad46`, config SHA256 `9affd2aee7ec5fa0d7f7b4271c2c7112b9be0166afae70c8b2a407b8752ac2b3`, receipt `/srv/codi-connected/chat-channel-drafts-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chat-channel-drafts-r1.service`. Only Chat app graph changed; native/guest security and network protocol bytes unchanged. Root and /desktop returned 200; issuer/steward/guest/official/chess services active. Source and checks backed up on private box-git main `f0263a33e2a2a86c4747d51d114fdaed5a3b3411`; temporary transfer and backup checkout removed. Independent-network group test and full goal remain active.

Actual 4,096-byte Unicode chat send and fresh-browser recovery now passed on the live service (`live-unicode-boundary-r2.txt`). A registered browser sent one exactly 4,096-byte message containing 1,020 emoji through the real Chat UI in an owned isolated official channel; a second fresh browser on the same registered account recovered the complete message in 0.53 seconds after channel selection. This single run does not test a distinct recipient or physical phone. The first r1 test clicked its temporary channel while Chat was still initially opening, so the click was ignored and the test timed out; no message was sent and its owned channel/account were cleaned. The corrected r2 waited for readiness and passed. A guarded cleanup allowed only the exact test message and removed the isolated channel, message, key, test account and session metadata. Public directory confirmed no temporary channel and General chat still at height four; issuer/official/chess services active. No product code changed. Test source and cleanup helper backed up on private box-git main `6e4cc21004764d9981f5c8068af7f4b25daf5e77`; temporary remote helper and backup checkout removed. Independent-network group test and full goal remain active.

Cleaned up generated obsolete test releases at the user's request. Guarded root script `prune-unreferenced-native27-webhost.py` checked the exact active managed release/pin under the hosting lock, retained every release referenced by current systemd or `/etc/codi-connected` (including code-history), retained the immediate `native27-chat-unicode-r1` rollback, rejected running-process/open-file references and symlinks, and removed 38 explicitly listed unreferenced native27 release directories totaling 4,560,171,894 bytes. Root receipt `/srv/codi-connected/native27-cleanup-1793296206136771981.json` records each manifest; script backed up on private box-git main `516aa085daca8a7928864dc4b28548f59ba9065d`. No services restarted. Post-cleanup `/srv/codi-connected/releases` uses 4.7 GiB, webhost has 78 GiB free, issuer/steward/guest/official/chess services active, root and /desktop returned 200, and immediate rollback exists.

Removed 37 matching generated local release directories by comparing their manifest hashes with that receipt, after checking process references; retained current `chat-channel-drafts-r1`, immediate `chat-unicode-r1`, and the `verified-ids-r1` worker experiment baseline. `.build/checks/local-release-cleanup-r1.json` records the 4,440,149,802 bytes removed. Local `.build/releases` now uses 4.7 GiB; workstation filesystem has 78 GiB free. Historical scripts referring to the deleted generated builds require rebuilding those fixtures before rerunning; evidence and source were preserved. No account, private channel state, source checkout or root baseline inputs were removed. Goal remains active.

Live isolated ten-session chat service restart passed (`live-ten-service-restart-r1.txt`). Ten separate registered automated Chrome profiles on the workstation joined a temporary official channel. With `codi-official.service` stopped, all ten queued messages remained visibly pending; a transient 90-second systemd restart watchdog was armed before stopping the service. After the service was restarted, all ten sessions received all ten messages exactly once without page reload in 3.15 seconds, and all ten senders subsequently received distinct-account delivery confirmations. The temporary channel, test messages, key, ten disposable accounts and session/author metadata were cleaned; General chat remained at height four and the public directory showed no test channel. The watchdog timer was stopped and no active test unit remained. Issuer/steward/guest/official/chess services active. Tests used one workstation and provider with guest and speech assets blocked; they do not prove ten independent devices, a separate network or physical phone behavior. Expected HTTP 502s were observed during the deliberate service outage. No product code changed. Test and guarded cleanup sources backed up on private box-git main `7dcb8a3e5b59a6f5da36293e4387235019e1f804`; temporary remote helper and backup checkout removed. The combined independent-network group test remains outstanding; goal remains active.

Fixed a 30-second delay reopening Chat after refresh during a server outage: `loadChannels` previously scheduled its next directory attempt 30 seconds later even after failure. It now retries failed directory fetches at 1, 2, 4, 8, 16, then at most 30 seconds; successful normal refresh remains every 30 seconds. `chat-directory-retry-check.py` passed packaged Chrome with two simulated fetch failures, the 1/2-second retries, successful channel opening and disposal.

The live group scenario `live-ten-refresh-restart-r1.txt` before the fix passed ten pending messages, three browser reloads and re-sign-ins during an intentional official service outage, exactly-once delivery and receipt confirmations, but converged 32.67 seconds after restart. The candidate was deployed and the same scenario `live-ten-refresh-restart-r2.txt` passed in 5.4 seconds. These are separate single runs, not a controlled performance guarantee; the old code's 30-second failed-directory timer was an identified plausible contributor. In both runs a transient 180-second systemd watchdog was armed before service stop and stopped after restart; ten test accounts and session/author metadata, isolated channel, messages and key were removed. No actual user message sent. General chat remains height four; no temporary channel/test watchdog remains. Browsers were on one workstation with Linux and speech assets blocked, and three explicitly signed back in after reload; this does not establish independent-network or phone behavior.

Current managed release `/srv/codi-connected/releases/native27-chat-directory-retry-r1`, manifest `0940aa5f30eeef1e8bb5d995ce7cfb0ef6c6064eb618e3cc0b5a55185472ff5d`, config SHA256 `041b375f6d7d0a7d0fed0b5442dbe4ac5a27d7dc780e983d43ca6b0b53a5d7dc`, receipt `/srv/codi-connected/chat-directory-retry-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chat-directory-retry-r1.service`. Only Chat app graph changed; native/guest security and network protocol bytes unchanged. Root and /desktop returned 200; issuer/steward/guest/official/chess services active. Source and checks backed up on private box-git main `6636de3536ff64b44c4de4665430fefbc7ae4f79`; temporary transfer and backup checkout removed. Independent-network group test and full goal remain active.

Chat now remembers the last successfully opened official channel on this browser, scoped to the signed-in account subject and same-origin issuer. On reopening, it chooses that channel only if it is still in the server's offered directory, otherwise it falls back to General chess chat (or the first offered channel). This is a small UI-selection preference in localStorage, not channel authority or message storage; storage errors fall back normally, and clearing browser storage removes the preference. Account changes do not share the preference. Unsent drafts remain window-local and are not included.

`chat-last-channel-check.py` passed packaged Chrome with simulated directory: reopening restores SYSTEM, a different account defaults to General, and a no-longer-offered channel falls back. `live-chat-last-channel-r1.txt` passed actual public full-desktop registration, selection of SYSTEM, page refresh and sign-in, and opening Chat on SYSTEM; no message sent and disposable account/session/metadata removed. Current managed release `/srv/codi-connected/releases/native27-chat-last-channel-r1`, manifest `e7098b260a3daf8a8186c0586a4c0d010ba19d94e517f70dfc344097e9b7f42f`, config SHA256 `952eeed5bad2ee9e379e0b7b1b11cbd9bb8b241df0807f73bb9c50c7421a2589`, receipt `/srv/codi-connected/chat-last-channel-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chat-last-channel-r1.service`. Only Chat app graph changed; native/guest security and network protocol bytes unchanged. Root and /desktop returned 200; issuer/steward/guest/official/chess services active. Source and checks backed up on private box-git main `797c9d4d0b6fada9f4a65febb50e41feb40205a7`; temporary transfer and backup checkout removed. Independent-network group test and full goal remain active.

Chat now also retries an initial selected-channel open failure with the same 1/2/4-second bounded backoff as directory failures, instead of swallowing the failure and waiting for the 30-second successful-directory refresh. If the browser reports online while there is no current channel and a retry is waiting, it wakes the retry immediately. A single in-flight directory guard prevents duplicate attempts; normal open channels and successful 30-second refreshes remain unchanged.

`chat-directory-retry-current-check.py`, `chat-join-retry-check.py` and `chat-join-online-wake-check.py` passed packaged Chrome with mocked directory/open failures, 1/2-second backoff, immediate online wake, no duplicate opens and app cleanup. `live-chat-join-online-r1.txt` passed the actual public full desktop with directory HTTP failures injected into that browser only: after releasing the fault and dispatching an online event, General chess chat reopened and the existing phone message was visible in 0.18 seconds. It sent no messages and removed its disposable account/session/metadata. This is not a physical connectivity test or a live server-side channel-open failure.

Current managed release `/srv/codi-connected/releases/native27-chat-join-retry-r1`, manifest `dfa8d4860b3b484f46d3cac4de9b79793c59cd463f407b6f7c3d48190e25b4d3`, config SHA256 `8d0ccb945d3e6998819d678439e90a2125b29a0209a6e09673e794c9251d4d4e`, receipt `/srv/codi-connected/chat-join-retry-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chat-join-retry-r1.service`. Only Chat app graph changed; native/guest security and network protocol bytes unchanged. Root and /desktop returned 200; issuer/steward/guest/official/chess services active. Source and checks backed up on private box-git main `087c31de0b16b0e8a4edfae648990723c03de240`; temporary transfer and backup checkout removed. Independent-network group test and full goal remain active.

Improved phone Chat/Chess layout. In a 390x844 emulated phone viewport the Chess app's 372-pixel board extended beyond the 490-pixel window; it now uses a centered 320-pixel board at narrow container widths and tighter heading/status spacing, so the entire board fits in that window. Wider desktop containers retain the 440-pixel board. Chess game chat still sits below the board and moves and requires scrolling; no claim of a complete mobile chess redesign. Moved its composer error status below the form rather than beside the textarea, hid empty status space in both Chess and Chat, and set a 16px phone Chess textarea font.

`chat-chess-phone-layout-check.py` passed the packaged app with mock channels, phone board containment, desktop board width, empty status, message-size boundary and retained send-error draft. `live-chat-chess-phone-layout-r1.txt` passed actual public desktop at 390x844 emulation: the Chess board was 320x320 and wholly within its window; Chat's empty status used zero height and the Send target was 44px. Before screenshots and geometry are `.build/checks/current-mobile-{chat,chess}.png`, after are `current-mobile-{chat,chess}-r2.png`; screenshots contain the existing test conversation and stay local. No message sent and disposable account/session/metadata removed. This is Chrome emulation, not a physical phone or touch/keyboard verification.

Current managed release `/srv/codi-connected/releases/native27-chat-chess-phone-space-r1`, manifest `e5d9a93761027581196441326545dcc29ab4b2fa45ec490bf77565aa6370442b`, config SHA256 `dbc9f003124043418743cf32b2bf0546d871c5f29f032ab531053e2f9a692d1e`, receipt `/srv/codi-connected/chat-chess-phone-space-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chat-chess-phone-space-r1.service`. Only Chat and Chess app graphs changed; native/guest security and network protocol bytes unchanged. Root and /desktop returned 200; issuer/steward/guest/official/chess services active. Source and checks backed up on private box-git main `581785ff27f776d7512de4a5442d790101ec77e6`; temporary transfer and backup checkout removed. Independent-network group test and full goal remain active.

Chess now provides Game and Chat view buttons in narrow app containers. Game shows the board, moves and export controls; Chat shows the same separate game conversation and composer without requiring the user to scroll past the board. Switching preserves the unsent draft and resets the app's scroll position. Wide desktop containers hide the buttons and display game plus chat together. Both views use the same session-owned channels and continue updating; this is presentation only.

`chess-phone-tabs-check.py` passed packaged Chrome with mocked channels: phone board fits, Game/Chat visibility and pressed state, draft preservation, desktop both-visible behavior and message-size/error checks. `live-chess-phone-tabs-r1.txt` passed the actual public desktop at 390x844 emulation: the 320px board remained within the window, switching to Chat showed the existing phone message and reachable composer, a draft survived switching and buttons had 44px touch targets. No message was sent and its disposable account/session/metadata were removed. Screenshots remain local `.build/checks/current-mobile-chess-{game-tabs,chat-tabs}.png` because they contain the existing test conversation; no physical-phone touch or keyboard test is claimed.

Current managed release `/srv/codi-connected/releases/native27-chess-phone-tabs-r1`, manifest `7e005af62f7aee61579291147aa4b72fce77c46ff0e5b810134d8b75ab89a6a2`, config SHA256 `95fcbe19f618111a99cfe385c2770005b2400e5e56467c7103a903fb87fcd865`, receipt `/srv/codi-connected/chess-phone-tabs-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chess-phone-tabs-r1.service`. Only Chess app graph changed; native/guest security and network protocol bytes unchanged. Root and /desktop returned 200; issuer/steward/guest/official/chess services active. Source and checks backed up on private box-git main `f2fe288cbefcf15f96e46786aaa477615aa14eeb`; temporary transfer and backup checkout removed. Independent-network group test and full goal remain active.

Live ten-session abrupt official-service process crash test passed (`live-ten-service-crash-r1.txt`). Ten distinct registered Chrome profiles joined an isolated official channel and all observed one committed baseline. The official service's main process was sent SIGKILL with a transient 90-second systemd start watchdog armed; nine other sessions submitted messages after the kill and systemd restarted the service with a new PID automatically. All ten sessions displayed all ten messages exactly once without reload within 5.64 seconds after the service restart check, and all senders obtained distinct-account delivery confirmations. The watchdog timer was stopped; no active test unit remains. Guarded cleanup removed the exact test channel, messages, key and ten disposable accounts/session/author metadata; public directory has no temporary channel, General chat remains at height four, and issuer/steward/guest/official/chess services are active. This is a single workstation, guest/speech blocked, same-provider process-crash test; it does not establish a kill during a database commit, whole-host power loss, phone behavior or ten independent-network participants. No product code changed. Test scripts backed up on private box-git main `778234545acdbbec4f1900bb58d7933ceebb17db`; temporary helper and backup checkout removed. Goal remains active.

Chess conversation now uses readable message bubbles, distinguishing the signed-in user's messages, with a clearer Chess chat label and styled composer; Sent/Delivered/pending and spam disclosure semantics are unchanged. On narrow screens its history has a bounded scroll area so the composer stays reachable. Opening the phone Chat view starts at the latest message; switching to Game and back preserves an earlier reading position and unsent draft.

The initial r1 deployment's live phone test found that bubbles pushed the composer outside the window (`live-chess-chat-bubbles-r1.txt`); r2 bounded the phone history height. Its geometry checks then passed but the harness had a malformed JavaScript assertion (`live-chess-chat-bubbles-r2.txt`); corrected test passed (`live-chess-chat-bubbles-r3.txt`). A screenshot then exposed that initially hidden chat opened at the oldest messages; r3 restores latest/reading position. `chess-chat-bubbles-layout-r3-check.py` and `chess-chat-bubbles-history-r3-check.py` passed packaged Chrome with four-message phone layout, latest/reading position and draft behavior, desktop display, spam disclosure and scrolling. `live-chess-chat-bubbles-r4.txt` passed actual public desktop at 390x844 emulation, including reachable composer, styled existing messages, latest position and preserved reading position/draft. No message sent and disposable account/session/metadata removed. This is not a physical-phone keyboard/touch test.

Current managed release `/srv/codi-connected/releases/native27-chess-chat-bubbles-r3`, manifest `27d6654715acf458353779143947aa0ec9231102048a995eec56f4bd923d6696`, config SHA256 `022faed17b42f6a58a0400b3b2071ea739d3742e75c529cfbd44a8968027089c`, receipt `/srv/codi-connected/chess-chat-bubbles-r3-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chess-chat-bubbles-r3.service`. Only Chess app graph changed; native/guest security and network protocol bytes unchanged. Root and /desktop returned 200; issuer/steward/guest/official/chess services active. Source and checks backed up on private box-git main `d1de9d020b7616f40f4f3b3b59ce992e2fc262ee`; temporary transfer and backup checkout removed. Independent-network group test and full goal remain active.

A full live Stockfish exhibition with spectator disconnect/recovery passed (`live-complete-chess-recovery-r1.txt`). The public full-desktop Chrome spectator joined the new featured game at ply 1. It went offline after height 5 while the same signed game advanced to height 7; after reconnect it caught up in 0.17 seconds in this run. It stayed open through the 77-ply game and observed the verified 1–0 result. The downloaded signed record was independently replayed from genesis through all 77 legal moves against that game's expected channel and matched the final result. No chat message was sent; the disposable account/session/metadata were removed. This is one automated workstation spectator and two server-hosted Stockfish agents, with a simulated client outage; it is not a human-vs-human game, independent-network test, or a spectator present before the first move. General chat remained height four; no temporary channel exists; root and /desktop returned 200 and issuer/steward/guest/official/chess services active. No product code changed. Test script backed up on private box-git main `9ef858c170dca8a9f22a0008837c71b12ddf2e2c`; temporary checkout removed. Independent-network group test and full goal remain active.

`live-account-boundaries-r1.txt` passed actual public registration and sign-in after refresh using a disposable 28-character username and 32-character mixed Unicode/symbol password. Browser validation rejected usernames shorter than three, starting with a digit or containing hyphen/underscore, and rejected three-character and 33-character passwords. Existing ten-session tests separately registered accounts with four-character passwords. The test removed its exact disposable account and session records; no chat message or file was created. This tests UI boundary validation and one server-accepted max-length account, not every Unicode or server-side adversarial input. Active issuer/official/chess services remained healthy; no product code changed. Test backed up on private box-git main `09b9fbe59d0dbc7fba540ece6770a802be14db97`; temporary checkout removed. Goal remains active.

### Tab-scoped shared chat drafts — 2026-10-29

Unsent drafts now use the shared device-history host in same-tab sessionStorage, scoped by account and channel. Chat and Chess synchronize the same channel's draft across windows in that tab. Refresh and sign-in on the same tab preserve it; closing the tab or clearing browser storage can remove it, and separate tabs do not share drafts. This is not a server backup. Storage failure is reported and the current window retains its unsaved text in RAM. Sending clears only an unchanged draft, so completion of an older send cannot erase a newer edit. Existing queued-message behavior remains separate.

Local real-Chromium checks cover host permission gating and disposal, account/channel isolation, quota failure, fallback, app sync, delayed-send race, and mobile/desktop layout. `live-tab-drafts-r1.txt` passed public full-desktop Chat/Chess sharing, close/reopen and same-tab refresh/sign-in, without sending a message; the disposable account and metadata were removed. `live-tab-drafts-ten-restart-r1.txt` passed ten registered sessions with pending messages during a deliberately stopped official service: after restart all ten recovered all ten messages exactly once in 3.0 seconds and received distinct-account delivery confirmations. The isolated temporary channel, ten accounts and test messages were removed. This test used one workstation and does not prove ten participants on independent networks. The earlier user's cellular exchange remains verified as recorded above.

Current managed release `/srv/codi-connected/releases/native27-tab-drafts-r2`, manifest `117a813efbf0f9f0c1145af23879f80801816ec673f4b211a70974d68d3dd7b4`, config SHA256 `5af601873ece96963a4bd58e2526b92f65e28e91e0bd070aaf695023514eb621`, receipt `/srv/codi-connected/tab-drafts-r2-activation-result.json`, renewal backup `/var/backups/codi-renew-before-tab-drafts-r2.service`. Root and /desktop returned 200, public channel directory contains General chess chat and SYSTEM, and issuer/steward/guest/official/chess units are active. Source and checks backed up to private box-git main `ac0b079aaf20cdfdb27b78e132d551b4670a2026`. Owned remote staging and obsolete local intermediate builds were removed; immediate rollback retained. Independent-network group test remains outstanding; current server-backed priorities supersede earlier P2P scaling targets.

### Draft-storage failure after sending — 2026-10-29

Fixed an edge case in Chat and Chess: if writing an edited draft to sessionStorage fails (for example, storage quota) and the message is then successfully queued, the unsaved text no longer stays in the composer and invites a duplicate send. The view clears that sent text in RAM and warns that the saved draft could not be cleared; an older saved draft may return after refresh. A different newer stored edit is not erased. Ordinary concurrent edits still remain protected.

`chat-tab-drafts-quota-send-check.py` and `chat-chess-quota-send-check.py` passed packaged Chromium with simulated quota failure and confirmed clearing, warning, and channel isolation. `tab-drafts-app-quota-r3-check.py` passed shared Chat/Chess synchronization and delayed-send/newer-edit protection; `tab-drafts-layout-quota-r3-check.py` passed phone/desktop layout and scroll/draft checks. `live-tab-drafts-quota-smoke-r3.txt` passed live public Chat/Chess sharing, close/reopen and same-tab refresh/sign-in; no message sent, disposable account and metadata removed. The quota failure was simulated locally, not induced on the live service.

Current managed release `/srv/codi-connected/releases/native27-tab-drafts-quota-r3`, manifest `86dd0cf5306c0e4ad09861269765b55d2578d2093ee26304d6587d2acc3b07cc`, config SHA256 `808c1427e44d1767fbe94fdcc90b34b4138fdbc6a35c8361d03b2d92327d76f4`, receipt `/srv/codi-connected/tab-drafts-quota-r3-activation-result.json`, renewal backup `/var/backups/codi-renew-before-tab-drafts-quota-r3.service`. Root and /desktop 200; issuer/steward/guest/official/chess active; directory contains General chess chat and SYSTEM. Source/tests backed up on private box-git main `14b813e0058611df4e45d9b8cdf015b2c1a2c1c1`. Inactive staging files were removed and immediate rollback retained. The user's availability for a nine-browser plus cellular-phone group test was requested; do not start a timed test until they confirm.

### Channel selection while busy — 2026-10-29

Chat no longer silently ignores a channel click while an initial channel open, message queue, resend or discard is finishing. It remembers the latest clicked offered channel and opens it when the operation completes; a message already being queued remains associated with its original channel. Disposal drops pending selection, and removed directory entries are not opened. This is an app-level usability change only.

`chat-selection-queue-check.py` passed packaged Chromium with a held initial join and clicks to two other channels, choosing the last without concurrent opens, plus a held send followed by a channel switch and checking correct-channel submission. `chat-selection-quota-check.py`, `chat-selection-fallback-check.py`, and `chat-selection-retry-check.py` passed storage failure, per-channel drafts, failed sends/switches and retry regressions. `live-chat-selection-smoke-r1.txt` passed public full-desktop channel selection and restoration after refresh/sign-in, with no message sent and the disposable account and metadata removed. The held-operation race was exercised by mocked host operations locally, not reproduced against a slow live server.

Current managed release `/srv/codi-connected/releases/native27-chat-selection-r1`, manifest `fbf3844e3160c0207a1da2450502e4d4a3c6ed7a2777764e5537ef1e4777d8af`, config SHA256 `9dcb82dfe9ba28e1398e29471b7bb4d97a39ad99e4b8e3f8a23121868a25ef22`, receipt `/srv/codi-connected/chat-selection-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chat-selection-r1.service`. Root and /desktop returned 200, official directory contains General chess chat and SYSTEM; issuer/steward/guest/official/chess active. Source/tests backed up on private box-git main `adfd95939eaf16e11af97ff01d2b8f1aa6ac41d9`. Inactive remote staging removed; immediate rollback retained. The separate-network group test remains outstanding; the user has not yet confirmed availability for it.

### Channel-open error feedback — 2026-10-29

Chat previously displayed a failed channel-open error only until its automatic refresh, which immediately replaced it with the old channel's normal status. It now keeps “Could not open [channel]. Try again.” visible while retaining the prior channel and draft; another successful open clears the error. A failed message queue still takes priority in the status so unsent content is not misrepresented. This is app-only feedback and does not claim a retry succeeded.

`chat-open-error-check.py` passed packaged Chromium with a forced channel-open failure, status preservation across refresh, intact channel/drafts, and clearing after successful retry. `chat-open-error-selection-check.py` and `chat-open-error-retry-check.py` passed the latest-click and backoff regressions. `live-chat-open-error-smoke-r1.txt` passed actual public normal channel selection/restoration after refresh and sign-in; no message sent and the disposable account/metadata were removed. The failing open was simulated in the local fixture, not induced on the live server.

Current managed release `/srv/codi-connected/releases/native27-chat-open-error-r1`, manifest `14c3655633cbe74388c1e7382f20768ce75e7cbb99eb22903c8686f3a270d1d0`, config SHA256 `b88ef5dd47031104824f52fa0fafa777b392df845ac2a62987a65b17938f259e`, receipt `/srv/codi-connected/chat-open-error-r1-activation-result.json`, renewal backup `/var/backups/codi-renew-before-chat-open-error-r1.service`. Root and /desktop 200, directory contains General chess chat and SYSTEM, issuer/steward/guest/official/chess active. Source/tests backed up on private box-git main `297ba70cb7e799f9a26a6d675330edc3892021c7`. Remote staging removed; immediate rollback retained. Independent-network group test remains outstanding and the user's availability request remains unanswered.

### Offline pending message across browser close — 2026-10-29

`live-pending-browser-reopen-r2.txt` passed on the actual live full desktop: a registered disposable Chrome profile selected an isolated official test channel, went offline via Chrome network emulation, queued one message and showed it pending with the composer cleared, then closed Chrome completely. After restarting Chrome with the same profile and signing into the same account, the test opened the channel and saw the message accepted in 0.41 seconds in this run. The server's authoritative official head was height 1, confirming one stored operation in the initially empty channel. The earlier r1 also passed browser recovery but did not inspect server height. The test used one workstation and simulated the offline interval; it does not prove recovery on a separate device, physical phone, independent network, abrupt power loss, or a recipient reading the message. No product code changed.

Both runs removed their narrowly guarded isolated channels, messages, keys, disposable accounts and associated session/author metadata; the temporary remote helper and browser profiles were removed. Root and /desktop returned 200, issuer/steward/guest/official/chess services active and the public directory lists only General chess chat and SYSTEM. Test and helper backed up on private box-git main `05c1b7c40e1ce2f76522431e59153ad86c71b70b`. Current release remains `native27-chat-open-error-r1`. The independent-network ten-participant group test is still outstanding; the user's availability request remains unanswered.

### Offline backlog and another writer — 2026-10-29

`live-pending-backlog-reopen-r1.txt` passed on the actual live full desktop with simulated browser offline: one registered account queued ten messages, fully closed Chrome, reopened the same profile and signed in, then saw all ten accepted exactly once in their original order in 6.03 seconds in this run. The isolated empty channel's authoritative server head reached height 10. `live-pending-backlog-other-writer-r2.txt` passed the more demanding case: first account queued three offline messages and closed its browser, second registered account posted two messages while the first was away, then first account reopened and signed in. It observed the two newer server messages followed by its three queued messages once and in order, with server head height 5, in 3.03 seconds after opening the channel in this run. These are same-workstation automated Chrome profiles and simulated offline conditions, not independent-network or power-loss tests. Sender-side UI status showed server acceptance, not proof that a person read the messages.

The first other-writer r1 harness was interrupted after discovering it incorrectly required sender-only delivery labels on incoming messages; it did not establish success or failure. Its guarded test channel and both accounts were cleaned, and r2 corrected that assertion. All tests cleaned their exact temporary channels, messages, keys, disposable accounts, sessions/metadata and profiles; remote helper removed. Root and /desktop 200, public directory lists General chess chat and SYSTEM; issuer/steward/guest/official/chess active. No product code changed. Tests/helper backed up on private box-git main `29c641876c222c3fe26dd5a007f2a79ddd014a8a`. Independent-network ten-participant test remains outstanding and the user's availability request remains unanswered.

### Independent channel recovery — 2026-10-29

`live-channel-independent-recovery-r1.txt` passed on the actual public full desktop using two registered disposable Chrome profiles, each with two Chat windows for two isolated official test channels. In the receiving browser only, history requests for the first channel were deliberately answered with HTTP 503 while its head advanced. The second channel received its message once in 1.04 seconds while the first remained blocked. After restoring first-channel history and dispatching an online event, that channel received its message once in 0.39 seconds. The official server head was height 1 for each initially empty test channel. This shows independent progress for two channels under this client-side injected history failure; it is not a whole-server outage, independent-provider test, many-channel stress test, or proof of human receipt.

Both test channels, operations, keys, disposable accounts and session/author metadata and browser profiles were cleaned; remote helper removed. Root and /desktop 200, issuer/steward/guest/official/chess active and public directory lists only General chess chat and SYSTEM. No product code changed. Test/helper backed up on private box-git main `082adad309c5a985dfe8d8901095c34cc022243a`. Current release remains `native27-chat-open-error-r1`. Independent-network ten-participant group test remains outstanding; user's availability request remains unanswered.

### Recent generated-release cleanup — 2026-10-29

The guarded webhost cleanup `prune-recent-unreferenced-native27-webhost.py` was attempted against nine reviewed older native27 releases, but correctly stopped before any deletion because all nine remain named by the managed controller's bounded `code-history.json`. `origin_service/deployment.py` retains up to 16 entries; these releases remain available to that rollback history. Do not remove them or alter the history without an explicitly designed and tested controller change. The empty failed attempt output is `.build/checks/recent-release-cleanup-r1.json`; script backed up on private box-git main `998ce13e6f147e186e2609f8ae7d9c4b3941990b`, remote staging removed.

Nine matching generated workstation release directories were then removed only after comparing their manifest SHA256s with the corresponding still-present server releases and checking running process cmdline/cwd/exe/open-file references and regular-file/no-symlink constraints. `.build/checks/recent-local-release-cleanup-r1.json` records the 1,080,494,214 bytes removed; workstation `.build/releases` now uses 5.2 GiB and the filesystem has 77 GiB free. Current `chat-open-error-r1`, immediate rollback `chat-selection-queue-r1`, source, private service state and all webhost releases were preserved. Issuer/steward/guest/official/chess active. Full goal remains active; user has not responded to the availability request for the separate-network group test.

### Lost acceptance reply and requested pause — 2026-10-29

Live tests `live-lost-acceptance-response-r1.txt` and `live-lost-response-retry-r1.txt` passed in isolated temporary channels. In both, the browser intentionally discarded the first successful server response to a message submission. In the first it recovered by reading verified history; in the second the browser's history was also temporarily failed, the browser actually submitted twice, then recovered after history was restored. Each channel's official server head was height 1, and its UI displayed one accepted message. Test-only channels/messages/keys and accounts/sessions/metadata/profiles were cleaned; remote helper removed. This is not a power-loss or all-network proof. Root and /desktop 200; issuer/steward/guest/official/chess active; public directory contains General chess chat and SYSTEM.

The user explicitly requested a pause and a working/partial/outstanding handoff. The current concise guide is `PAUSE_HANDOFF_2026-10-29.md`. Pause the goal and do not resume until requested; leave the test site running.

The pause guide and lost-reply test sources were backed up to private box-git main `87da55900ec95d55dfd37214e1423ab171b5858c`, packet `tools/codiserver/pause-handoff-20261029-r1`; the temporary backup checkout was removed.

### Reboot restoration and official chat directory fix — 2026-10-30

User asked to restart stopped services after box-webhost rebooted at approximately 02:00 Eastern. Native issuer/steward/guest units are disabled for boot and did not come back by themselves. Initial simultaneous systemctl start brought issuer/steward up but canceled guest; the managed controller `manage-services.py start --config /etc/codi-connected/ksu/managed.json --roles guest` started its required guest network backend and guest successfully. The static registered file service/socket/proxy and TURN relay/service/socket/proxy were started in their dependency order. No boot enablement was changed, so another reboot may require manual restoration.

Although root then returned 200, the official directory initially had no chat entries on page 1: overnight featured Chess had created enough chess channel rows to fill the SQL page before the registry filtered by stream. Pagination had General on page 2 and SYSTEM on page 3, while Chat requested only page 1. Fixed `steward/official_registry.py` to verify/filter public chat policy before SQL LIMIT, preserving proper chat pagination. Local mock regression passed with 85 chess entries, three chats, pagination and search; real-signature regression passed with 85 signed chess policies and three signed chats; official admin initialization/enrollment/ban/unban fixture passed. No games, channels, messages or account state were deleted.

Official service now uses `/srv/codi-connected/official-services/chat-directory-page-r1`, manifest `33e6e30bc4c374f05938ba542ba36c4ff6d39c9d3529461176a36fa93b97b0fd`, unit SHA256 `b7ecec43c21f5c1bd8ceff69f05fc5efbcffa828473b2fbaab4a5394fce0a54d`, activation receipt `/srv/codi-connected/official-directory-page-r1-activation-result.json`, rollback unit `/var/backups/codi-official-before-directory-page-r1.service` (prior package `chat-sparse-cache-r1`). The guarded activation validated directory readiness and rolls back on failure. Source/test/stage/activation backup private box-git main `ddba41d08c8dd6938d649e8d92156c13af9a7b6a`; owned remote staging removed.

Post-restoration root and /desktop returned 200, public directory contained General chess chat and SYSTEM on page 1 with no next page, and issuer/steward/guest/official/chess/files/file-proxy/TURN/TURN-proxy/registered network were active. The attempted fresh browser smoke could not start local Chromium via the existing ChromeDriver (`session not created: Chrome instance exited`), even with an explicit profile. Therefore actual registration/Chat/Chess interaction after reboot is not verified by that smoke; logs `.build/checks/reboot-restoration-smoke-20261030-r2.txt` through r4 include the failed attempts, and no test account was left behind. The first r1 attempt hit the empty directory before the fix. Development goal remains paused: this restart and necessary availability fix were explicitly requested by the user.
