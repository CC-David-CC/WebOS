# Desktop preview workspace

## WebOS work queues

For WebOS development, use `docs/WEBOS-WORK-QUEUES.md` as the operational
checklist. Update its progress ledger and relevant queue when work starts, is
tested, integrated, deployed, blocked, or handed off. Check off a broad item
only when its complete acceptance criteria are verified; record partial and
research-only results honestly. Preserve the full program and newly discovered
work. A paused goal remains paused until the user requests resumption.

The user split this workspace into two independent targets:

- desktop-lab/: backend-free desktop proportion controller and local browser VM.
- active-system/: actual full-viewport computer UI, v86, guest Internet relay,
  shared chat/chess networking and optional issuer/steward development.

Future functional system work belongs in active-system. Proportion/sizing lab
work belongs in desktop-lab. Do not automatically synchronize either target or
reintroduce lab controls into the active site. Root files and supplied versioned
packages are preserved baseline/reference inputs. No private service state or
real account/key material should be copied between targets or into public assets.

## Public prototype boundary

The user explicitly reserves https://ksu.codes/desktop/ for the sizing prototype.
It must have no account backend, server-side user-file persistence, or guest
Internet/ping relay through the host. P2P is optional for this prototype.
Keep active-system backend/network experiments separate from that live URL.
Static boot assets are permitted; visitor files and identity stay ephemeral in
browser RAM unless explicitly downloaded. Do not deploy active-system over the
prototype as part of ordinary goal continuation.

## Next-version external preview path

The user designated https://ksu.codes/hidden/ for the next version if an external
preview is needed. Keep https://ksu.codes/desktop/ live and unchanged while the
upgrade is being developed and verified. /hidden/ is a staging path, not an
authentication boundary. This path decision does not request immediate deployment
or resume the paused goal.

## Resume and external testing — 2026-10-22

The user explicitly resumed development and authorized /hidden/ for any tests
needed for the external preview. This supersedes the earlier paused status.
Use https://ksu.codes/hidden/ for external next-version tests; keep /desktop/
unchanged. Prefer the existing 80/443 ingress; report any additional router-port
requirement before changes. Preserve clear development identity labels.

## Final production URL — 2026-10-22

The user clarified that /hidden/ is temporary staging only. The finished system
will be the main site at the domain root (https://DOMAIN/), not a subdomain or
/desktop/ or /hidden/ path. Keep mount-prefix support configurable with root as
the default. This is a future cutover requirement, not authorization to replace
the current homepage/prototype during development.

## Live hidden preview — 2026-10-23 UTC

The connected development preview is now live at https://ksu.codes/hidden/.
Keep /desktop/ unchanged. Current native controller and issuer/steward/guest
binaries on box-webhost are /srv/codi-connected/releases/f2fbd4d, with the
existing venv and managed config. Three online roles run; bootstrap is stopped.
Native units remain disabled for boot. Guest GID1001 has scoped unprivileged ping
permission alongside administrator GID1000 (range 1000 1001); forwarding is off.
The managed hosting generator/manifest now carry the KSU-only codi_preview flag.
Use the hosting controller workflow for any route/CSP/rollback changes.

Default-trusted public Chrome tests pass identity, v86, guest ping/DNS/HTTP,
RTC chat and separate chess moves from the development network. Independent
WAN/NAT and public TURN are not verified/configured. See
active-system/evidence/live-hidden-preview.md for current paths, exact hashes,
caps, receipts, rollback backups and remaining work. Older historical documents
describing /hidden as unpublished or guest as stopped are superseded by this state.

## Certificate hostname and canonical entry fix — 2026-10-23 UTC

turn.ksu.codes DNS and trusted Caddy certificate are live, generic404 only.
Public TURN/shared443 ingress remain off; all native roles/controller still
f2fbd4d/schema2 with unchanged PIDs and disabled boot state. Managed generator
now includes KSU-only codi_turn_certificate=true and correctly redirects /hidden
(without slash) to /hidden/ via `redir * /hidden/ 308`. GET/HEAD and fresh public
Chrome through both addresses pass Linux ready. Preserve this redirect syntax:
Caddy otherwise treats /hidden/ as an optional matcher and yields empty200.

Current generator/manifest/Caddy hashes are recorded in the latest HANDOFF
entry and evidence/managed-turn-policy.md. /desktop remains byte-identical;
all eight sites pass. A tested profile9/schema3 TURN policy candidate was pushed
as source5e364fe, not installed or activated. Current operator remains f2fbd4d.


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


## Guest-network R2 integration LOCAL ONLY — 2026-10-23 13:24 UTC

Live stays native11/schema4/R15; registered Files and /desktop are unchanged.
The signed own-WAN guest access policy is STILL NOT LIVE. New source is private
foundation R2 a398727e7045ab909f4f2fe0c195e5431a71f436c96987aee4d41e39049436e6
(31 source/evidence/receipt files), at active-system/.build/network-foundations/
guest-auth-egress-r2 and private Git tools/codiserver/guest-network/foundations/
<manifestSHA>. This is NOT a standalone runtime, installer or native12 release.
R1 remains immutable/historical; its separate-test-only aggregate is superseded
for current sources by guest-network-integration-milestone-result.json.

Implemented coordinator.py retains one public WebSocket across private Unix
worker changes. Legacy binary clients stay anonymous without unsolicited text;
registered grants/key proofs are connection/policy/session bound. Reset/expiry/
account switch destroys old QEMU/NAT, not Linux. client.mjs keeps control text
outside VirtIO, discards delayed old-identity authorization and renews HttpOnly
cookie on reconnect without VM reload. Candidate app.js5f7e7306a7ecb1b799c40e8344bca6523f935b0d280bf94e1dc4eb0e5926d87b
wires this only behind explicit server metadata, synchronizes account/renewal
and destroys it at session end. Legacy/offline paths never request SDK; malformed
metadata fails closed and stops the failed VM. Chrome HTML username pattern
corrected; valid hyphenated and invalid slash names tested through real form.

unix_transport.py validates root-immutable parents, frontend-owned0600 socket,
explicit GID, inherited AF_UNIX listening descriptor/bound path and peer UID/GID.
Root requests restricted to exact health path. Production candidate nft mode
uses Unix workers, so frontend IPv4 initiations permit only fixed issuer8118,
not worker TCP ports. Narrow gateway/DNS ARP replies now accepted: actual expiry
found fresh QEMU ARPs for retained Linux, and rejecting reply stranded the wire.
All other ARP source/target/opcode denies remain. Policy fixture SHA nowe3f3dd0b2933100234781b9c5d5594156cc1534d72913e7847429bd427277888.

Current exact-source proof PASS:28 grant tests;161 policy checks+84 real native
socket probes;63 actual HTTP/WSS/QEMU worker checks;18 coordinator checks;
35 COMBINED real UID-confined coordinator+distinct-UID workers/QEMU+Unix+nft+
Linux Ethernet client checks including actual ping/HTTP/trusted TLS/DNS, own-IP
role distinction, LAN/metadata/port denial, direct native bypass refusal, expiry
retiring QEMU and usable anonymous recovery on SAME public connection. Actual
protected listener custody/path/descriptor refusal and root health restrictions
included. Numeric fixture UIDs60231..60234 are not production users. Distinct
worker UIDs use processGID1001/no caps; private fixture only sets ping range.
Host namespace/firewall inventory/resolver/ping/forwarding unchanged; cleanup PASS.

Separate real Chrome/v86 root+hidden adapter checks PASS (real HTTP/WebCrypto,
QEMU ARP and Linux NIC receive counters, shell/shared file, cookie reconnect,
stale identity response). Full desktop five cases PASS: root/desktop controlled,
hidden/390px touch controlled, legacy relay, offline and bad metadata. Actual
account-menu register/signin/signout preserves VM/9p, independent shell variables,
workspace windows and editor DOM/draft. No severe console errors in valid cases.
These separate browser fixtures do NOT prove browser+installed services+kernel
as one chain. No private Files GUI+new network gateway, physical Android or WAN
proof yet. Retained failed receipts describe fixture checksum offload/import/
selector/serial-observer mistakes and actual ARP/pattern fixes; no guard weakened.

V11 native allowlist now explicitly frozen apart from current NATIVE alias;
legacy public/network/runtime sets are literal immutable contracts, independent
of future serve.py.16 release tests prove real frozen V10/V11, future allowlist
isolation and mutation refusal. No native12/schema5 added. New SDK not in old
PUBLIC allowlist. Fresh webhost-files-preview-health PASS native11/R15, private
storage boundary, generated hosting, all10sites and all133 prototype files;
new grant endpoint404 and authorization metadata absent. No service restart,
account mutation or personal file reads. Existing own-IP anonymous access remains.
Current root1 expiry22:36:39UTC; explicit renewal only. All native units disabled
boot; forwarding0, range1000..1001 and current cookie/keys/DBs/config preserved.

NEXT: protected persistent root operator (locked distinct users, immutable runtime,
root-reserved socket units/peer checks, per-role LoadCredential, public-only
resolv bind, strict units/cgroups, durable per-account usage/permissions and scoped
atomic nft journal/recovery/drift); then default-off native12/schema with Files/
TURN rollback, actual installed lifecycle/fault/downgrade tests and Chrome full
chain. Existing frontendUID nft restriction also affects old same-UID QEMU:
coordinate kernel/native enable; restore old kernel before restarting old relay
on rollback. Do not stage these rules uncoordinated. Recheck own WAN IP/hosting
pins before rollout. No new router ports, firewall blanket flush or boot changes.
Keep /desktop, user tabs/RAM, account/file data, authority and cookie intact.
Full roadmap remains active; see evidence/guest-network-integration.md for scope
and remaining shares/resource broker, network quotas/durable sessions, direct ICE,
independent WAN and supplied v0.1/v0.2/v0.3 audit. No graphical games/root cutover.

Private Git source 55db0cb09433b31383fdeea845cdf95607a303e5; source-only server checkout fast-forward verified.


## Durable guest workers R3 LOCAL ONLY — 2026-10-23 13:56 UTC

Live remains native11/schema4/R15; no new worker/operator/native profile or
frontend was installed on box-webhost. /desktop unchanged. Own-WAN anonymous
deny/registered ICMP+80/443 allow remains NOT LIVE. No service restart, private
account mutation/file read, router/port/firewall/boot change in this work.

Current private foundation5467a68068cbcaf2c4146e40403a2794fdc2c5224bf24e53224c8eb5f548a16b
(47 source/evidence/receipt files), local active-system/.build/network-foundations/
guest-durable-workers-r3; runnable worker runtime7f5de0c7525b81391448069708ee972cca304792baaf274b4aa1151e181a9759
(12 files), local active-system/.build/guest-workers/guest-wire-r1. Private Git
paths tools/codiserver/guest-network/foundations/<foundationSHA> and workers/
<runtimeSHA>. These are not a production installer or native12. R1/R2 immutable.
See evidence/guest-durable-workers.md and guest-durable-workers-milestone-result.

usage.py adds root-controlled permissions SQLite separate from worker-owned
usage ledgers. Registered counters bind canonical user:UUID, not session/name.
Anonymous has one aggregate, no account/visitor home. Bytes, speed/packet token
buckets, starts, concurrent reservations and clock high-water persist across
reconnect/restart. SQLite immediate transactions/FULL sync; no silent reset of
missing/corrupt/linked/wrong-role state. Crashed slots expire within30s. Close
releases slot without erasing counters/starts. Permission withdrawal is checked
on charge/renewal and one-second lease check; denial reaps QEMU/NAT. Account
limits do not identify a physical person across anonymous browsers.

Configurable candidate defaults: UTC24h windows,64MiB/account,262144bytes/sec,
200packets/sec,4concurrent,20starts/minute; service caps64MiB anonymous and192MiB
registered (256MiB combined). Existing preview wire/process/coordinator bounds
remain. These are NOT changes to live limits. Both-direction Ethernet and
post-auth control count to account; bounded pre-auth control counts to role cap.
Root permissions are read-only to workers; each UID writes only its own ledger.
No login credential/private-file data in these databases or source exports.

installation.py + serve-guest-wire.py validate root-owned/pinned runtime/settings,
public issuer/egress policy, fixed service UID/GID, QEMU hash and exact inherited
Unix listener. CLI always requires durable accounting; optional usage=None stays
only in library/legacy fixtures. Static socket units reserve root-parented0600
frontend-owned sockets and enforce peer UID/GID. LoadCredential secret, empty
worker capabilities/NoNewPrivileges, strict FS/private devices/temp/home denial,
only own writable usage dir, public-only resolver bind and resource caps. Root
ExecStartPre validates scoped nft semantic fingerprint and namespace; changed
settings/rules/extra runtime files refuse startup. This is startup preflight,
NOT continuous kernel guarding or an atomic lifecycle/rollback operator.

PASS exact current proof:28 real SQLite concurrency/custody/restart/rollback-clock/
quota tests;8 real export/mutation/secret-exclusion tests;13 actual installed
systemd milestones, including copied manifest hashes BEFORE execution, locked
unique users/Unix sockets/credentials, actual QEMU ARP, native cross-ledger/policy/
source-secret DAC refusal, quota reaping, fresh grant after restart cannot erase
usage, real SIGKILL/automatic recovery retains counters, distinct-account quota,
idle permission withdrawal and startup rule/settings/runtime drift+restoration.
All fixture accounts/units/private files/namespaces removed; host firewall,
resolver/ping/forwarding unchanged. Power-loss crash was NOT simulated.
Retained fixture failures were passwd-lock query missing sudo and reset-failed
before loading a new unit; fixture cleanup succeeded, product guards unchanged.

Full current Chrome desktop root+390px hidden touch now uses real ledger and
passes quota fallback/restoration while keeping signed registered identity,
public socket, VM/9p, independent shells, workspace windows and editor DOM/draft.
Legacy/offline/malformed metadata cases and standalone real v86 root/hidden
adapter also PASS.63worker/18coordinator/35combined UID/QEMU/coordinator/nft/Linux
client tests refreshed PASS; latter prove real ping/HTTP/TLS/DNS/native bypass
refusal but are not installed-unit/browser proof. Current aggregate explicitly
keeps installed browser+kernel whole-chain, private Files GUI+new networking,
continuous guard, production operator/native12/public rule/WAN/Android FALSE.

Fresh webhost-files-preview-health and aggregate verify native11/R15, private
file worker, generated hosting, all10sites and133 prototype files. New guest grant
endpoint404/no auth metadata. Existing live shared-cookie relay STILL permits
own WAN to anonymous. All native units remain disabled boot; bootstrap stopped;
issuer240953/steward239112/guest239113 and file worker236763/proxy236765 unchanged.
Root1 expires22:36:39UTC, explicit renewal only; preserve cookie/keys/DBs/files.

NEXT: protected persistent root controller/guard: explicit locked production users,
immutable runtime+venv/credential/settings/unit custody, root locks and atomic
kernel lifecycle journal. Compute EXPECTED scoped nft fingerprint from generated
policy before mutation; do not trust/adopt arbitrary existing table. Recover
start/stop/failed activation safely and refuse unmanaged drift; delete only owned
table, never host-wide flush. Monitor/guard failure must stop private workers;
startup checks alone are insufficient. Actual installed crash/rollback/drift tests
required. Keep disabled boot. Separate frontend UID restriction also blocks old
same-UID QEMU: coordinate frontend stop, kernel apply, worker/new frontend start;
on rollback restore old kernel BEFORE old relay restart, preserving user data.
Then default-off native12/schema and Files4/TURN3 downgrade with real full-chain
Chrome/public proof. Frozen V10/V11 contracts already pass. No new ingress ports.
Remaining resource broker/selected shares, durable issuer sessions, direct ICE,
independent WAN and v0.1/v0.2/v0.3 audit stay in full active goal; no games/root cutover.

Private Git source a3310248aa5501a917acef4b4fc5921f05c6a358; source-only server fast-forward and both artifact manifests verified.


## Guest network controller R4 — inactive webhost preparation, 2026-10-23

Root operator8411c84aab2b284418951371b2ee9822797a70599c016c375bb409cb40f641d1 and
worker7f5de0c7525b81391448069708ee972cca304792baaf274b4aa1151e181a9759 are now
INSTALLED INACTIVE on box-webhost. This supersedes R3's source-only installation
notes. They are separate sealed10/12file packages at /srv/codi-guest-network/
operators/<operatorSHA> and workers/<workerSHA>. Existing protected Python is
/srv/codi-connected/venvs/517179c/bin/python. No package install was necessary.
Private Git source27f94e44c9814575a4d6b912a8dc196820761d87 staged them Git-first.

New config /etc/codi-guest-network/ksu/managed.json (codi-guest-managed/1),
SHA5bef7160dca8db409f2c5f9309d295b62ed8e87994c5c348b8ede95a9a37c8ba.
Instance codi-net-ksu-hidden. New dedicated locked users codi-net-anonymous UID976
and codi-net-registered UID975; future process GID1001, existing frontend
codi-guest UID980. Private worker state /var/lib/codi-guest-network/ksu/{anonymous,
registered}/usage.sqlite3, both EMPTY. Root permissions at configDir/policy/
permissions.sqlite3; root credential sources configDir/credentials/{role}.secret.
Do not copy actual managed config/credentials/journals/ledgers into source/public.
The configure journal can contain credential material and is root600.

ALL FIVE NEW UNITS ARE INACTIVE/STATIC, no processes or bound sockets:
codi-net-ksu-hidden-guard.service, -anonymous.service/.socket and
-registered.service/.socket. NO host codi_guest_egress table exists. NO native12,
new grant endpoint, frontend or new guest policy is active. Live remains
native11/schema4/R15, issuer240953/steward239112/guest239113, file-worker236763/
proxy236765. Native/file configs, cookies, accounts/private data, existing website,
shared443/TURN, /desktop, forwarding0 and ping1000..1001 unchanged. Anonymous
own-WAN access STILL works through the old live shared-cookie relay; user-approved
anon deny/registered ICMP+80/443 allow remains NOT LIVE until native12 integration.

Prepared egress policy SHAaa1aa08dc3a8f45c3d30c6d5565a87f82495624f7353077c8a81827c21663e67.
Fresh server WAN reflection and domain DNS both104.180.210.33; protected own list
[104.180.210.33], public DNS1.1.1.1/9.9.9.9. Recheck real addresses before enable.
Root preparation receipt /srv/codi-guest-network/standby-8411c84aab2b284418951371b2ee9822797a70599c016c375bb409cb40f641d1-result.json.
Local guest-network-standby-{plan,install}-result.json bind exact source/package,
inactive/static units, empty counters, unchanged native/files PIDs, hosting pins,
website and all133 declared prototype files. Source sync alone is not installation;
these actual configure/status/post-health checks establish inactive preparation.

operator.py + manage-guest-network.py implement root-only locked/journaled
configure/start/stop/recover/monitor. Fixed public issuer+effective egress pins,
immutable packages/protected dependency venv/QEMU, disjoint persistent roots,
static unit/drop-in custody, locked unique UIDs and private credentials verified.
Configure is default-off; repeating same inputs preserves state/credentials.
Actual start requires existing frontend DOWN before applying its UID restrictions.
Expected nft witness compiled from generated policy in fresh private namespace
BEFORE target mutation. Exclusive create+complete rules share one transaction.
Ownership comment binds instance/config path and compilation checks kernel kept
it. Teardown uses exact semantic fingerprint plus inspected GENERATION HANDLE,
not just table name. Unknown/pre-existing/replacement/other-instance tables are
retained; never flush host firewall. Start rollback stops new units/removes owned
table; committed healthy recovery keeps live wire/QEMU. Stop recovery finishes
stop. No usage or account/file data reset/restore. Boot remains disabled/static.

Notify guard polls kernel/protected inputs at0.5s, has only effective NET_ADMIN;
workers have no capabilities, NoNewPrivileges, processGID1001 and private Unix IPC.
Fault stops workers/sockets and configured frontend. BindsTo also stops workers
on guard death. Polling does NOT promise instantaneous protection during arbitrary
root firewall changes. Source input/root control plane is trusted; guest parser
and scoped kernel egress are independent required boundaries.

Exact local guest-operator-result PASS20 installed-systemd milestones: copied
worker/operator hashes verified BEFORE execution; configure-prepared recovery and
idempotence; pre-existing table refusal; real exits at start prepared/kernel/guard/
workers/committed and stop units/kernel; committed and healthy recovery retain
actual QEMU PID/wire; actual guard4096/worker0 cap witnesses; kernel deletion and
guard SIGKILL stop actual workers/QEMU; unknown rule/unit-drop-in drift stops and
blocks recovery; genuine worker readiness failure rolls back without resetting
bad usage; create/name-reuse races and identical-policy second controller cannot
remove another table/live QEMU. All fixture accounts/units/namespaces/files removed,
host firewall/resolver/sysctls unchanged.8 exporter mutation/custody tests PASS.
The tests found nft1.0.9 discards comment in declaration AFTER separate create:
owner tag now goes in CREATION statement and explicit readback checks it. Retain
failed receipts; no ownership guard relaxed. Earlier failed grant was fixture's
placeholder policy digest, not a product signer failure (initial clock suspicion
was wrong). Child helpers no longer inherit NOTIFY_SOCKET to avoid false notices.

Current aggregate guest-operator-milestone-result binds these exact local tests,
R3 real durable quota/Chrome desktop evidence and actual inactive webhost stage
plus fresh webhost-files-preview-health: all10sites/133 prototype files, public
TLS, private-file boundary, native11/R15 preserved. Runtime activation, native12,
complete installed browser+kernel, private Files GUI+new networking, independent
WAN, physical Android and full roadmap remain FALSE/unfinished. Native root1
expires22:36:39UTC; explicit renewal only. No new ports/router/firewall/boot changes.

NEXT: default-off native12/schema5 integration. Preserve frozen V10/V11 contracts
and Files4/TURN3/code rollback; stop old frontend before new UID rules, restore
old kernel before restarting old same-UID relay on rollback. Use sealed external
operator SUBPROCESSES, not importlib into native's guest_service package (avoid
cross-package module cache/relative import confusion). Add issuer GuestAuthority,
feature-gated explicit SDK route, GuestCoordinator, same-origin cookie and account
sync with actual old/new frontend compatibility. No SDK/private source in old
PUBLIC allowlists. Test actual browser+installed controller/workers/kernel with
ping/DNS/HTTP/own-WAN role distinction/LAN denial, logout/expiry/reconnect, private
Files GUI, voice, independent PTYs/workspaces, RTC chat/separate chess/PGN and
all-site/prototype preservation BEFORE /hidden activation. Keep user tabs/RAM.
Production operator code/config upgrades and credential rotation are explicit
future migrations, not silent configure overwrites. Remaining shares/resource
broker, durable issuer sessions, direct ICE, independent WAN and full supplied
v0.1/v0.2/v0.3 audit stay in the full active goal. No games/root-domain cutover.

Final private source/server checkout 81edf23691381215990a8f8d41489b16309bbfda; source-only evidence update after inactive preparation, no runtime activation.


## Controlled guest frontend R5 — tested source only, 2026-10-23

New guest_service/runtime.py + frontend.py and explicit launcher flags connect
GuestAuthority, protected frontend descriptor, read-only wire credentials and
GuestCoordinator. Issuer --guest-network-policy-sha256 composes alongside the
existing file/discovery authorities. Guest --network-control and exact pin are
paired; configured input failures abort, never silently restore the legacy relay.
The SDK is served ONLY by the configured route; old public allowlists unchanged.
Default-off issuer/relay behavior remains. Candidate app network text distinguishes
durable account limits from the old restart-reset preview; app SHA59772641ec326f4d527eefc54f83810d4e6bfebd283d7961c906c1efc8ecb927.

Actual issuer CLI + real controlled Relay tests PASS: root/hidden off14checks each,
on32each, both on modes also fresh Chrome/v86 actual desktop/account menu tests
(hidden390px touch). Same public wire/VM/9p files/independent shell variables,
workspace windows/editor drafts survive sign-in/out, cookie loss/reconnect and
real durable quota fallback/restoration. Exact SDK/HEAD, private source404,
file+network challenge composition, mismatched issuer/key/policy/path/oversize/
outage refusals and binary-only legacy actual QEMU ARP covered. Before/after
hash pins include backend/browser dependencies and boot assets. This uses local
same-user workers, NOT installed native controller+workers+kernel as one chain.

16 actual systemd runtime checks PASS: unique locked UID, copied root-owned
source/venv, real read-only LoadCredential and frontend-owned Unix sockets;
changed/linked/writable descriptor, socket owner/mode/link, UID/NNP, missing/
oversized credentials and writable credential stand-in refused. Final checks
start ACTUAL guest CLI with the descriptor and three real mounted credentials,
serve matching config/exact SDK, refuse issuer mismatch. That phase uses a fake
loopback config responder, not installed worker/QEMU connections or nft rules.
Fixture units/users/sockets/secrets/stage cleaned. First fixture log read failed
because StandardOutput=file retained old bytes; changed to truncate and reran.
Original FAIL and earlier14check PASS receipts retained; product checks unchanged.

Fresh legacy relay87, authorization28 and release16 tests PASS, including real
frozen native10/11 artifacts. Current receipts guest-controlled-frontend-result,
guest-frontend-runtime-result, guest-controlled-frontend-milestone-result under
active-system/.build/checks. See evidence/guest-controlled-frontend.md for scope.
New aggregate binds exact fresh proofs, all10sites/133prototype/TLS/file boundary
health and sealed webhost operator status. Historical frozen aggregates retain
their original source scope; do not assert they freshly bind this changed app.

LIVE UNCHANGED: native11/schema4/R15, issuer240953/steward239112/guest239113,
file worker236763/proxy236765; public network grant metadata absent, SDK/challenge
404. New network operator8411/worker7f5 remain INSTALLED INACTIVE, all5staticunits
inactive/no sockets/processes, NO host codi_guest_egress table. Prepared config
5bef7160dca8db409f2c5f9309d295b62ed8e87994c5c348b8ede95a9a37c8ba unchanged.
No route/Caddy/firewall/port/boot/private data/cookie/key changes. /desktop and
current website unchanged. New anonymous own-WAN denial is STILL NOT LIVE.

NEXT: native12/schema5 lifecycle integration is NOT IMPLEMENTED/exported. Use
sealed external operator SUBPROCESSES (avoid guest_service import collisions),
root descriptor/backend/policy pins, extra issuer flag/repeated guest credentials
and guard dependencies. Journal enable/disable/recovery/start/stop, stop old
guest before UID restrictions and restore old kernel BEFORE old same-UID relay
restart. Preserve Files4/TURN3/code rollback, keys/cookies/accounts/files/usage.
Then actual browser+nativecontroller+installedworkers+kernel whole-chain ping/
DNS/HTTP/own-WAN role/private-deny/logout/expiry/reconnect, real private Files GUI,
voice/PTY/workspace/RTCchat/separatechess/PGN before hidden activation. No native12
installed; no full-chain, physical Android or independent WAN proof yet. Full
v0.1/0.2/0.3 goal remains active; resource shares/broker, durable login sessions,
direct ICE fallback/full plan audit/root cutover remain unfinished.

Private tested source/server checkout 181f85e07eec6e50bf8ca9c013356716c51ef689; source foundation4cab489c218f3ebec074c5cd6d93e131bc150fabd8209d938350534731489734 verified100files. Hosting note appended under lock; configs/pins/native+file PIDs unchanged. Runtime NOT activated.


## Native12 integration IN PROGRESS — 2026-10-23

Local network_management.py, manage-services schema5/profile12, Files/TURN/code/
recovery compatibility implemented as DRAFT, not installed on box-webhost. Export
active-system/.build/releases/connected-network-r1 has manifest
6965594615c296061ddea6cc16fe61654cb0d99c2d577860b5c1e7ffa1fd9a63 (206files).
Native network ordering/fault journal MODEL20, unit/input20, exporter18, existing
TURN/deployment metadata checks PASS. Actual installed native12 DEFAULT-OFF Files
regression PASS11 with real account/file API, faults/recovery, TURN credentials,
native10 downgrade/rollback, cookies/keys/files preserved and fixture cleanup.
Real enabled-policy VM lifecycle now PASS13 (actual exits, rollback, commit wire continuity and guard death); production remains unchanged.

A PRIVATE LOCAL KVM Ubuntu24.04 fixture is LIVE for full-chain tests, not a host
service deployment: private state active-system/.build/native-network-vm mode0700.
QMP/status via scripts/prepare-native-network-vm.py status (verify live process,
never restart based just on PIDfile). At creation PID3283572, SSH127:49747,
HTTPS127:57503, official image SHA
b3296484e362ba2e713489a5de6225c719d9500962bde25d15f2f21e512c7658.
Fixture SSH/TLS keys are ephemeral PRIVATE .build/VM state: NEVER copy them or
actual VM service state into source/public. No host directories shared. Host
firewall unchanged. Only host package genisoimage installed under prior approval.
VM includes actual native12/legacy11, sealed operator8411/worker7f5, existing
file packages, its own systemd/kernel/users/firewall and fake public/private
addresses. Native config in VM /etc/codi-native-fixture/managed.json is schema5;
frontend+issuer+steward and real file/network services running. VM package root
/srv/codi-network-fixture; installed-result.json is PUBLIC proof metadata.

Actual Chrome/v86 THROUGH native controller+installed workers+kernel PASS28/
17networkprobes including anon own-IP denial, registered own ping/HTTP, other
public ping/HTTP/DNS, private10/172/192 and metadata denial, actual private Files
GUI save/read, cookie renewal/reconnect, logout/signin, independent PTYs, RAM/
9p/editor/workspace retention. Certificate is fixture SPKI exception, NOT default
public TLS/WAN/physicalAndroid proof. Receipt native-network-vm-browser-result.
Initial test wget -T2 crashed139; no denial claim retained from that run. Known
supported wget syntax passes; unexpected crash now fails the checker. Earlier
setup omitted account --apply, then used wrong persistent file service username;
retained logs. Fixed test setup, narrowly resumed without resetting native state;
fixture OS file user renamed to required codi-gateway preserving UID/owned data.
Do not weaken file operator account validation or recreate issuer/VM to proceed.

VERIFIED in the same VM:54 direct native socket/kernel probes under3 real UIDs,
and13 actual native enable/disable/process-exit/recovery/commit/guard-death/code-
rollback milestones. Account/key/cookie/private files and counters preserved.
See evidence/native-network-managed.md and native-network-managed-milestone-result.
NEXT within the SAME QMP-confirmed VM:
Check cached SDK behavior across actual off/on transitions; may need capability
refresh to retain networking without VM reload (not yet tested). Need full voice/
RTC ordinary chat/separate chess regressions and phone viewport/full-chain before
webhost upgrade/activation. Native12 artifact and these new sources/proofs are
NOT YET in private Git/server source (still181f85e). Keep /desktop and current
native11/schema4/R15 untouched. Guest policy is NOT LIVE on ksu.codes. Full goal
and remaining resource broker/durable sessions/direct ICE/WAN/plan audit active.

Native12 source/candidate/evidence now private Git/server checkout 4a7d7b3a457bec5c73f7fcf6ac71e8b486910203; source only. Candidate69655946..., suite1bc5aa6c... verified. Root hosting note appended under lock, old native/files PIDs and both config/hosting pins unchanged, new operator still inactive/no nft table. VM remains QMP-confirmed live for next tests. No native12 production activation.


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

## Resumed release goal and authorized root cutover — 2026-10-24 UTC

The user replaced the earlier broad goal with completing the existing public
group-chat/history candidate, existing desktop/account/file/terminal/security/
lifecycle regressions, separate-Internet tests, documented persistence/recovery,
and a verified /hidden/ release with tested rollback. Development is active.
When that release is ready, the user explicitly authorizes moving the current
homepage to /blog/ and the desktop to https://ksu.codes/ at the domain root.
This supersedes the earlier prohibition on a final homepage cutover, conditional
on readiness. Keep /desktop/ unchanged. Include blog preservation, configurable
mount prefixes, old /hidden/ clients, browser cache and root/blog rollback in the
cutover verification; do not immediately replace the homepage during preparation.

The user clarified there are no existing users/tabs to preserve: this is being
built in public. Use a clean coherent release, explicit reload and tested rollback;
do not add infrastructure solely for seamless adoption by historical open tabs.
External test box: Tailscale moonpie, 100.105.243.29, SSH user maint (key works).
Its observed Internet egress is 24.126.137.85 versus this development network's
104.180.210.33. Use ordinary public HTTPS/ICE and inspect selected candidates;
Tailscale SSH/control reachability alone is not independent-WAN application proof.
User can also test a phone on cellular with Wi-Fi off. USB Samsung tether was
connected but Ethernet preferred; both observed egresses were home IP. User was
told it can be disconnected because no tests rely on it. Do not alter default
routes or expose remote ChromeDriver; it is loopback only through an SSH tunnel.

## Native16 integration in private VM — 2026-10-24 UTC

Live webhost is STILL native15 6789b29e... and unchanged. Current installed VM
candidate is native16 R5 814b97be709d9db970f447d8bbe28dce27c52acb1f8fee1f227adc9e80ad1b4b,
active-system/.build/releases/connected-routed-r5. Builder derives only from
sealed connected-document-r2, never canonical old native backend. One versioned
24-module network graph and five host scripts; verifier16 adds graph closure
without relaxing profiles1..15. Five native Python capability/launcher files
plus guest_service/client.mjs change. File service and Python guest enforcement
remain byte-identical to live. Controller native-rollout.py now accepts16.

Actual R1 red test proved closing Rooms during group creation reattached a view.
WeakMap view generations now cancel signing/verification before admission;
R2 passes both targeted stages, normal36group/23history/28xterm/20account/19doc/
11cache checks and182app cycles/26closed shell PID checks. Actual R2 checkpoint
process death/recovery, rollback to live15 and re-upgrade PASS; no data restore.
R2 is d231780f..., R1 3ffb3040..., immutable R3 969ffe6b... never installed.

Actual five-browser R2 red capacity proof showed fifth anonymous Linux booted
but whole UI locked behind four relay wires. R4 f1c3a880... makes strict-policy2
anonymous clients local-only with zero wires; five desktops and account/network/
cookie promotion/logout tests PASS. R5 additionally separates desktop authority
liveness from optional guest Internet failure. Five registered R5 browsers PASS:
four authorized relay sockets, fifth has no socket but saves/reads/removes own
private file. Injected issuer-status failure still locks controls; restoring
status unlocks the SAME Linux while its relay remains full. R5 history23 and
graph contract7 PASS. Further R5 four-room/eight-browser, full regressions and
fresh managed rollback/public WAN remain required before publication.

Four is a hard-coded preview resource cap in BOTH coordinator and worker, not
a fundamental four-account/WebRTC limit. User asked about >4 registered users;
explained resource planning/load testing and promised relay refusal must not
disable files/chat. No capacity increase executed. User agrees anonymous users
need no relay at all; they still have RAM-only guest files and browser chat/chess,
no server folder. Public caches hold code/boot assets, not user documents/keys.

Remote fixture: maint@100.105.243.29 (moonpie), driverPID10277/port55341,
folder /home/maint/snap/chromium/common/codi-wan-check-1792815874220890850;
loopback local19516 SSH forward. Owned public Chrome smoke browser was closed;
driver retained for upcoming WAN tests. Default-trusted external Linux boot PASS,
egress24.126.137.85 distinct from home104.180.210.33. Do not count Tailscale
control/ICE paths as public Internet P2P proof. No remote sudo is available or
needed for its installed Chromium155/ChromeDriver. USB tether not used.

New stage-routed-native-release.py is PREPARED, not executed: Git-first exact
candidate/controller, current schema5/config/hosting/prototype pins, root-owned
immutable install, existing checkpoint upgrade/rollback. See
active-system/evidence/routed-native-integration.md. Current full scope includes
external group/history/TURN proof, /hidden publication and later authorized
root/blog migration. Root cutover needs managed native/gateway mount bindings
as well as managed Caddy/website routing; do not improvise a proxy rewrite.

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

## Final /hidden/ release audit — 2026-10-24 UTC

Current explicit goal is the bounded /hidden/ integration release while preserving
/desktop/ and the homepage. Direct public release audit PASS covers all ten
requirement areas,15bound receipts,31live versioned assets and291installed files.
Actual public lifecycle13 PASS:182opens/closes across7apps,26closed guest shell
PIDs absent, all sampled resources/shared charges return to baseline, late read/
write/PGN worker operations cannot revive closed views. New group36 and scope/
chess reruns capture actual public TURN/TLS selected pairs on BOTH endpoints.
Earlier group/scope originals captured only the home endpoint; the first final
audit correctly refused that evidence. Those originals/audit log are retained.
History23 already had both endpoint captures. No weakened audit or product change
was used to obtain the stronger proof.

The previous note retaining Moonpie driver/tunnel is superseded: owned remote
driverPID10277, its fixture directory and local SSH forward19516 are now removed/
stopped after all sessions ended. Cleanup receipts moonpie-{browser,tunnel}-cleanup-
result.json confirm no unrelated browser/SSH processes touched. The reusable
private network VM and existing local ChromeDriver are retained.

Current handoff at active-system/HANDOFF.md now begins with live behavior, direct
evidence, rollback and honest persistence limits; older snapshots remain below.
Profile/history docs now describe liveR8 rather than an undeployed candidate.
Public prototype133files, homepageSHA55f2928da214010b2ed7d647a354c0052ae03e9d06bafc09c1ea3b67e8608a38 and all10sites are preserved.
The larger v0.1–v0.3 roadmap,8k gossip/PoW and separately authorized future root/blog
cutover remain unfinished. Current goal acceptance does not declare those done.
Do not replace the homepage as part of closing this preserve-homepage release.


## Active goal corrected by user — 2026-10-24 UTC

The user explicitly rejected treating the /hidden/ milestone as completion and
requested a rewritten goal covering the root/blog swap and other outstanding
changes. The active goal now includes the real domain-root cutover, required
mount/authority/publisher migration, remaining app/security regressions, scalable
P2P islands/gossip and fallback, chunked checkpoint synchronization, browser-paid
light PoW, player/audience separation and staged8k tests. Read the current goal
and initial requirement ledger before continuing. Existing passing /hidden/
checks remain milestone evidence, not proof of this whole goal.

This supersedes earlier agent-authored completion/deferment notes that excluded
the root/blog cutover or treated the requested networking work as planning-only.
Move the existing homepage to /blog/ and the active desktop to the domain root
when the migration is verified. Preserve /desktop/ byte-for-byte, other sites,
account IDs, keys, realm, UUID folders, permissions, saved files and monotonic
floors. Keep the current homepage live until the tested cutover transaction.
Do not weaken the goal to whatever subset currently passes. New marketplace/
payment apps are not prerequisites. The rewritten goal is ACTIVE.


## Root/blog migration implementation started — 2026-10-24 UTC

User corrected premature goal closure. Root/blog cutover and the requested larger
network changes are in the active goal; /hidden/ is an intermediate milestone.
Current live native16R8 and hosting remain unchanged.

New offline mount_operator/authority.py prepares and applies mount-bound root
plans using existing signing keys and durable ledgers. It preserves issuer trust,
realm, service key/scopes/quotas, cached descriptor and publisher counter. Root
commit is idempotent with the journaled signed bytes. Rollback signs a higher
revision for the old endpoint; no ledger/key recreation.19isolated real JOSE/SQLite
checks pass, including process deaths before/after commit, repeated adoption,
changed-origin/trust/scope/counter refusal, expired plans, frozen/missing state,
concurrent publisher progress and explicit unbound staging-ledger handling.
This helper is not exposed to HTTP or installed in live services.

Actual retained VM preflight PASS: root5 prepares6, runtime publisher214/215 keeps
its counter, root-owned staging and steward-owned online ledgers accept read-only
plans, origin/keys/realm preserved, target /api/v1 and /rendezvous. No plan applied;
no native VM service/config or live webhost change. New source overlay is
/srv/codi-network-fixture/tools/mount-authority-ef162df60d01bebf.

Blog source candidate adds explicit /blog→/blog/308 and /blog/GET/HEAD while keeping
current backend homepage for pre-cutover staging/rollback. Canonical blog URL and
all guide home links now point at /blog/. Content otherwise identical to prior
commitbc8ba8c;7actual isolated FastAPI HTTP checks pass, including link/asset HEADs,
all3guides, read-only/TrustedHost behavior and unchanged133prototype files.
The project-only test venv installs the site's declared pinned dependencies.
These source changes are not deployed.

Remaining coordinated work: stop native+file+guest protected services before
changing their policy/config/settings pins; update issuer public policy, root
provision exports, owner-separated publisher bindings/floors, native/file/guest
mount metadata and generated units/descriptors; restart and verify real root
account/file/terminal/network/RTC behavior; exercise interruption recovery and
forward-revision rollback in VM. Guest kernel rule ownership is based on the
unchanged instance/config directory and egress policy, but active.json binds the
full config hash, so do not edit settings under a running guard.

Old /hidden/ service worker serves verified public assets cache-first. Root
cutover tests must cover previously cached browsers, retire only owned old preview
registrations/public caches, and preserve prototype/private data. Do not assume a
Caddy redirect alone overrides an already installed worker. Caddy/manifest root
routing and safe atomic production cutover are not yet implemented.


## Terminal touch command update — 2026-10-24 UTC

The user requested removal of the terminal-local Keyboard button. Live /hidden/
now offers Ctrl+C, Ctrl+O (nano save; Enter confirms filename), Ctrl+X (nano exit),
Tab, Esc, Enter, Copy, Paste and Clear. The floating keyboard toggle remains.
No arrow/Help controls were restored. Only the terminal app and its generic
catalog/loader/cache graph changed; native/security and networking bytes match
R8. New native16 manifest b109768a09f1276047d74616d722f212bb12e261ff437fd1d1a6cccd4963b8cc,
release /srv/codi-connected/releases/native16-b109768a09f12760. Managed config SHA
is e4250512236ef5672f852db274402ce6d4fbb8add0a455bbf509b2ce2a44edfd;
issuer/steward/guest PIDs1211721/1211723/1211724, disabled for boot. Source commit
f44faa928f1c216015ba13df3e0ecac80e628592. Root activation receipt:
/srv/codi-connected/routed-native-upgrade-1792828065547662546-result.json.
Installed VM terminal/lifecycle/actual rollback/re-upgrade pass. All ten live
sites pass; homepage and133prototype files unchanged; no pending rollout or
maintenance. See active-system/evidence/terminal-touch.md for public-browser
acceptance, retained harness failures and exact proof. Existing cache-first
clients may need saved work and all desktop tabs closed/reopened for new assets.
Root/blog and the larger networking goal remain active and unfinished.

Public default-trusted Chrome terminal acceptance now PASS30, including real
Ctrl+O/Enter/Ctrl+X nano save/exit, floating keyboard, 44px targets and actual
foreground-program SIGWINCH. The hardened test retains prior failed harness
logs and avoids the old missing-filename false positive. See terminal-touch.md.

Hardened VM30 also PASS. Follow-up proof source455d3b215895b60c729ad43d881182b2faf5c047
is pushed and verified in the clean webhost checkout (25files), source-only with
no additional service restart. Proof manifestcf3f140be2a252fb4d2a03a76b47fb7deca016f0e3c898ee5046b28a78c8ea24.
Current live config remains e4250512236ef5672f852db274402ce6d4fbb8add0a455bbf509b2ce2a44edfd.

## Terminal swipe scrolling — 2026-10-24 UTC

Latest live /hidden/ native16 manifest3071d17fa17666e2d9317e96e2e9a79d629e2a16be2e44b9afb0ed9947efd211
replaces b109. Release /srv/codi-connected/releases/native16-3071d17fa17666e2;
config SHA39d88cd8fd56d223d88efaa8291cbf0693f0105660f937e9c022765b136d2c51;
issuer/steward/guest PIDs1243423/1243425/1243426, disabled for boot. Source
73f6a01ec82eb07b888d05d172a16ec12d78f5ef; root activation receipt
/srv/codi-connected/routed-native-upgrade-1792829544632813817-result.json.

User-reported swipe failure reproduced on old public b109. Xterm6 uses a virtual
scrollbar without touch panning. Terminal-owned pointer gestures now scroll via
the public API: drag down for older history, up for newer. Only terminal text
handles the gestures, with threshold, cancellation/second-finger/capture-loss
cleanup and no keyboard command injection. No per-gesture timer or global
listeners; view disposal removes listeners and capture. Floating keyboard and
Ctrl+C/Ctrl+O/Ctrl+X/Tab/Esc/Enter/Copy/Paste/Clear remain.

VM and default-trusted public Chrome38checks PASS, including trusted swipes,
keyboard mode, cancellation, stable text while new output arrives, nano/PTY/IME.
Lifecycle13 PASS182cycles/26closed shells gone. Actual VM process-death recovery,
b109 rollback/re-upgrade PASS with accounts/keys/files/cookie/usage preserved.
Health verifies321releasefiles,133prototypefiles,all10sites, homepage andhosting
unchanged, no pending journals. No guest image/security/network/policy changes.
All previous public assets retained apart from mutable graph/cache metadata.

See active-system/evidence/terminal-scroll.md and terminal-scroll-*-result.json.
Automated phone emulation does not claim physical S25 validation. Save/download
RAM work before closing ALL desktop-site tabs and reopening to activate the new
cache; refresh alone can retain old code. Full root/blog/networking goal remains
ACTIVE. Current website and /desktop/ preserved.

Final touch-scroll public proof manifest6602e8064799352845ff0164b4d7ff22e8ec3cfd571580b7d97e552351e15d57
is verified at sourcecfca777963b2d3281b5ccb8fa23db82408ad99f7 (13files, source-only).
The live native/config pins above are unchanged by this source-only pull.

## Root migration phase2 — actual private VM verification (2026-10-24 UTC)

Production remains native16-3071d17fa17666e2 at /hidden/, unchanged homepage and
/desktop/; no production deployment in this phase. The private retained VM NOW
uses basePath="" and HTTPS https://127.0.0.1:57503/. Do not recreate it or infer a
failure from an old /hidden-only probe. Root/fence revision12; native PIDs
issuer1475407/steward1475389/guest1475450, ingress1479191. SSH49747 unchanged.
No pending VM native-maintenance/rollout journals.

New local/source-only mount_operator/backends.py+coordinator.py and explicit
scripts/migrate-desktop-mount.py coordinate24stopped-service metadata/unit edits,
signed root/publisher rebinding, public policy exports, file/guest contexts and
restarts. Separate helper interpreters hold existing backend locks. No user DB,
key, private folder, permissions or usage restore/reset. Rollback signs a higher
root revision. Publisher-plan2 binds canonical JSON.

PASS:21authority crypto/SQLite checks;18actual VM backend readonly/refusal/lock
checks;11actual root rollback/process-death/recovery checks (authority/backends/
committed phases), preserving21files/key/account/cookie state, permissions and
nondecreasing usage;38actual root HTTPS Chrome/v86/xterm checks with captured
request paths and no hidden dependency;35root account/file/registered-only guest
network checks;19root durable document workflow checks. Fixture-only cert SPKI,
not a public/WAN root claim. Cycle-tested operator overlay is
/srv/codi-network-fixture/tools/mount-d6b8be8808f4c2da; final local operator Python
bytes match its source records. VM-only ingress follows actual native mount,
source9ab745fc4d813afd00b9a26a9bad40fb04240688aa4cfd9ec3ccae6c37c34efe.

Retained failures: insertion-order JSON hash broke first fault recovery. A
fixture-only v1→v2 public journal-reference upgrade verified the original digest
and signed old/new rows, backed up root0600, then explicit recovery reused root8;
no private state/floor was restored. Corrected full cycles finish root12. Parallel
account+document suites hit the existing issuer60/minute per-IP cap; document19
passed and sequential account35passed after the window, with no quota changes.

Use mount-root-browser-check.py and mount-root-workflow-check.py for current VM
root tests. Native/guest/file code artifacts unchanged. See latest
active-system/evidence/configurable-mount.md and mount-*-result.json receipts.
Next required work: managed production root/blog route candidate + hosting
rollback/coordinated cutover, old-hidden SW/cache retirement + warm-cache tests,
production operator packaging/review, root public browser/WAN tests. The blog
HTTP source candidate is already in private Git, not deployed. Coherent current
hosting inputs are .build/hosting/root-mount-r1-inputs with existing718934ce.../
c946c1e7.../69451812...pins. Full P2P/checkpoint/PoW/chess-audience/8k goal ACTIVE.

Phase2 source/proof root-mount-r2 manifestf4a1aa1c37ac6f45c506e8b5eec67ec159d8fcc3a6effa121e619e6e354dda92
is verified at source1847ae9be1b8f1dafa563b26a298e8aa92a3d852 (34files, source-only).
Production config39d88cd8.../PIDs1243423/1243425/1243426 and hosting/homepage are
unchanged. Full goal remains active; next is managed root/blog hosting and cache
migration before coordinated production cutover and public/WAN acceptance.

## Root migration phase3 — routes/cache tested, inactive staging (2026-10-24 UTC)

Production is STILL native16-3071d17fa17666e2 at /hidden/, with the same config
39d88cd8... and native PIDs1243423/1243425/1243426. Homepage, website release,
hosting718934ce.../c946c1e7.../69451812... and all133prototype files remain unchanged.
Root2 still expires2026-10-24 21:43:31UTC; no renewal/automatic signing was enabled.

Managed hosting_root/common.py c3181a47... implements the real root desktop plus
reserved blog/guides/static/test-time/prototype routes. Missing codi_mount selector
renders existing Caddy bytes exactly; other9site blocks and ingress/TURN unchanged.
PASS:17real Caddy HTTP/WSS/body/CSP checks with actual blog/prototype source;
17authentic Chrome worker/cache mount+rollback checks preserving foreign/private
browser stores;11actual VM root cache/offline/clear-rebuild checks; generated Caddy
TLS with real native VM services and real blog backend passes38terminal/nano/PTY/
touch/IME and19durable document workflow checks. Fixture TLS uses exact SPKI,
not ordinary public trust. All owned test ingress/process/forward changes cleaned.

Final immutable native16 cache candidate c23b1b73df68ffb25da810a7db73074d09297f0ccc06c459e8bc9c0430ca30c1
has unchanged53native/security,24network modules, app bundles and Linux image.
New cache client retires only opposite owned root/hidden worker/caches after a
bounded uncached server mount confirmation; unrelated/prototype/private stores
are preserved. Root entry navigation is network-first so online rollback serves
the restored homepage, with verified public recovery shell only on offline/5xx.
No RAM snapshot/private-file caching is claimed. Old declared assets retained
apart from mutable entry/cache/graph metadata.

Git-first source8f605fa2bbd37f9525d71354e26a0e2d16046c07 was verified373files in
the clean webhost checkout. Native candidate installed INACTIVE at
/srv/codi-connected/releases/native16-c23b1b73df68ffb2; cycle-tested mount operator
6e4ebb33e945ea8712dd72c56f5a9928a955af5b340ceaff6ef0221112ebe0dc installed INACTIVE
under /srv/codi-connected/mount-operators/<SHA>. Root install receipt:
/srv/codi-connected/root-cutover-install-1792835854213111621-result.json.
Actual production Caddy validates both candidate modes as caddy, keeping private
hardware auth import on-server. Actual readonly mount plan prepares24metadata
edits/prospective root3 but leaves actual root2/token/fence/config/PIDs unchanged.
No services restarted, live routes changed or maintenance notice published.

The retained private VM NOW runs c23... at basePath="", root/fence12, issuer1549121/
steward1549123/guest1549124 and restored Python ingress1553745. SSH49747/HTTPS57503
unchanged. No pending native or fixture-route journals/Caddy test unit. Do not
recreate the VM or use old hidden-only probes as health evidence.

Evidence active-system/evidence/root-hosting-cache.md; receipts root-hosting,
mount-cache-browser,root-cache-r2-native-vm,root-caddy-native-vm,root-caddy-vm-cleanup,
root-phase3-{final-state,source-sync},root-cutover-{plan,install,validation}.
Remaining before cutover: implement/test coordinated website/native/signed-mount/
hosting deployment/recovery and forward rollback; truthful notice; public root/
blog/all-site/prototype/default-TLS and independent-WAN acceptance. Existing
native/mount journals must remain the authority for unfinished operations; no
user data/key/ledger/floor restore. Full P2P/island/checkpoint/PoW/audience/8k goal
remains ACTIVE and unfinished. Terminal requested keys are already live/tested.

Phase3 inactive install/production validation follow-up is frozen at private Git
9531506c9ed3254d6946df2cbc0f9d296e0e9b78, tools/codiserver/root-mount-r3-staged,
8declared files, manifest93a10812d53b89e3785e66ecc9e53507bb70980d16a0a61137a262d2290e8128.
Clean webhost checkout fast-forwarded and verified under hosting lock; source-only,
no config/PID change. Receipt root-phase3-staged-source-sync-result.json.

## Root migration phase4 — coordinated real VM fault proof (2026-10-24 UTC)

Production STILL native3071 /hidden/, config39d88cd8..., PIDs1243423/1243425/1243426,
old homepage/website release/hosting and133prototype unchanged. Nativec23 and
mount operator6e4e remain installed INACTIVE. No production cutover or notice.

New site_cutover coordinator composes existing native code rollout, managed
website deployment, signed mount operator and managed hosting. Holding the
hosting lock, it changes hosting in the mount's committed callback before its
normal maintenance journal can clear. Failed hosting/reload/verification retains
the existing ordinary-native-start/signing guard. Early code/website steps leave
the old mount coherent. Receipt-only recovery verifies without another root mint.
Rollback is a new inverse plan, not old data/authority/publisher DB restore.

Five-file operator9722b19b49ff2f34123d6c7eacf05f9acea93e10475c349cf5d159f74c7f53b2
exported under active-system/.build/site-cutover-operators/<SHA>. Includes3modules,
sealed CLI and existing native-rollout.py. Exact bytes executed in retained VM.
Not yet installed on production. VM test subclass adapts runtime listener/TLS/
Host/static/log paths; production uses normal webctl Caddy/smoke. No public TLS
or all10real-backend claim for fixture runs.

PASS:7actual process-death/recovery cycles at code,website,mount-authority,
hosting-common.py,hosting-applied,committed,receipt;4pending phases refuse native
start/renew. Real systemd/native/file/guest/website/FastAPI/Caddy services. Existing
key/account/cookie/private-file hashes identical across cycles, usage nondecreasing;
all133prototype files checked by HTTPS per completed callback. Root/fence13→20,
inverse hidden/root endpoints and retained website pointers; no user state restore.
6actual sealed CLI refusal checks PASS for wrong pins,unlisted/symlink files/dirs,
nonprivate plan mode, no operation started and owned negative copies cleaned.

Final VM c23 at actual root20, native1647918/1647914/1647962, original Python ingress
1649323. Temporary website stopped/disabled and Caddy unit stopped/removed. No
pending native/site journals. SSH49747/HTTPS57503 unchanged; do not recreate VM.
Post-recovery actual Chrome terminal38 and document workflow19 pass at root; SPKI
fixture only. Owned QA document files removed, later QA account rows intentional.

Updated root-aware production-smoke.py206981ab... checks /blog/ plus actual root
desktop/config/CSP/cache/redirects when selector enabled. Default branch passes
all10current live sites with ordinary TLS, config/hosting unchanged. This does
not test the root branch live. No managed checker source was changed in prod.

Setup failures retained:0700fixture code parent blocked steward publisher imports;
existing journal stopped before authority change,0755public-code-parent fix +
explicit recovery advanced root13 without data restore. Minimal VM lacked Git;
approved install done only inside VM. Type=exec initial listener readiness race
fixed by bounded health observation; same live fixture reused, never recreated.

Evidence active-system/evidence/coordinated-cutover.md; receipts site-cutover-vm,
site-cutover-cli,site-cutover-root-{terminal,documents},site-cutover-final-state,
site-cutover-operator-export,root-smoke-candidate-before-cutover. Next freeze/push/
source-verify operator/proof, install inactive and create exact root-private plan,
production readonly preflight, authorized notice/cutover, public root/blog/all-site/
prototype/terminal/doc/cache/WAN tests. Root2expiry21:43:31UTC unchanged; explicit
bounded signing only, no auto-renewal. Full P2P/islands/checkpoints/PoW/audience/8k
and complete requirement reconciliation remain REQUIRED; goal stays ACTIVE.

Phase4 source/proof now verified at private Git/webhost clean checkout
a4de6ef2dba24ce0916fa1bd4f8c749471891e63. Package tools/codiserver/root-mount-r4
has32declared files, proof58e062123e6cfb04cf3d30c605951a511670eea4771a5667bfc4811d90a442af;
operator tools/codiserver/site-cutover-operators/9722b19b... has5files+manifest.
All39files including both manifests verified under hosting lock; source-only,
config39d88cd8.../native PIDs unchanged, no production pending journals. Operator
is NOT yet installed on production. Receipt site-cutover-source-sync-result.json.
Initial sourceaf3bca1 missed5Git-ignored declared .log files; verification refused
the incomplete package, explicit scoped additions landed in a4de6ef without
rewriting history or changing immutable bytes. Failure receipt retained as
site-cutover-source-sync-before-ignored-logs-result.json. Next: inactive operator
installation + private exact production plan/readonly preflight, then cutover.

## ROOT DESKTOP LIVE — 2026-10-24 11:06 UTC

This supersedes prior /hidden-only production state. Actual desktop is NOW
https://ksu.codes/ with basePath="" across native/file/guest/signed issuer/root/
publisher bindings. Former homepage is https://ksu.codes/blog/; guides/static/
test-time paths preserved. /hidden and /hidden/ redirect308to/. /desktop remains
backend-free and all133original files byte-identical. No internal root→hidden
rewrite. Keep configurable mount/root default; do not revert to older hardcoded
hidden probes or assume the homepage is still at root.

Native16 c23b1b73df68ffb25da810a7db73074d09297f0ccc06c459e8bc9c0430ca30c1
at /srv/codi-connected/releases/native16-c23b1b73df68ffb2; managed configSHA
568bcd2a10e6256b885eb7b36b045a3e7497d4f06bac474d901ff37cbc0280b1.
Issuer1460700/steward1460696/guest1460759 active, still disabled for boot;
bootstrap stopped. Root/fence3, expiry2026-10-25 11:06:16UTC. Explicit bounded
signing only, no auto-renewal loop. All35pre-cutover account rows and original
root/issuer/service keys, realm and connection cookie preserved; later QA accounts
are intentional. No user/authority/publisher database restore. Private folder,
service UID, egress policy436096... and relay config5ab3... constraints remain.

Website release20261024T110552353972Z-299874f5, previous20261023T043853468523Z-314447db.
Blog indexSHAd256863f38fbc41c58f56721487e58e1c9580a8ece09263bad55186bb49389be.
Managed hosting generatorc3181a47.../sitesf583f6f4.../Caddy4cf23397.../
smoke206981ab... active. All10site ordinary-TLS smoke checks, including actual
root desktop and /blog/, PASS; prototype133 HTTP bytes verified during commit.
Use hosting controller/lock/pins/generated Caddy workflow, never hand-edit Caddy.

Final standalone site operator89557858c046231e4fc7e61a567d13acf74cf3b4036d022ed0c1d1dfbaa7d0ce
installed at /srv/codi-connected/site-cutover-operators/<SHA>. Immutable mount
operator6e4ebb33... unchanged. Private plan:
/etc/codi-connected/ksu/site-cutover-plans/root-0fc388360583b742fd7f71995e7e4e7d1abd4d6a2889d773ba117d95948d62d6.json
(rawSHA0fc38836...; canonical planSHA9ae29229...). Source/webhost5fa9221bb36af53e4dcd311d91524f54e2fc9211.
Actual cutoverid622064c8449c473c6eb156ba56e14643; authoritative root receipt
/etc/codi-connected/ksu/site-cutover-last.json and site-cutover-<id>-result.json.
No pending native/site journals. A real10second notice ran; no RAM-save claim.
Rollback must use a NEW inverse plan + higher signed revision, retained website
pointer and generated hosting; do not restore old accounts/ledgers/config alone.

Hosting backups are /var/backups/webhost-sites/change-20261024T110644254457Z
(common.py),110644255305Z(smoke),110644256117Z(sites),110644257128Z(Caddy).
Full timestamps use the same20261024T prefix. Restore only through coordinated
inverse deployment/hosting workflow, with current data and monotonic floors.

Initial prod readonly CLI9722... failed before actions because hosting helpers
weren't on sys.path. Old artifact and private planfc4dd6... retained inactive.
Fixed import order; VM execution no longer preinjects the helper directory.
Operatorabb60... passed2fresh-import inverse/death/recovery cycles root20→22.
Final895... adds fd1/Python-log→stderr isolation so stdout is one JSON receipt;
actual sealed CLI with explicit VM adapters passes hidden/root readonly+apply,
root22→24, preserved keys/accounts/cookie/files. CLI custody6negatives PASS.
All failures retained, no fixture/data reset. Phase6proof61845cc0...,29files
including two operator manifests verified from Git. Production readonly preflight
895 passed before activation. Native SDK53/security,24network modules/app/image
bytes remain unchanged; c23 public cache/mount update only.

Public default-trusted Chrome at ROOT: terminal38, document19, lifecycle13
(182opens/closes,26shells gone), public-cache11 PASS. Two owned QA document homes
emptied/accounts disabled, unrelated account policies unchanged. Cache/offline
still cannot save/restore running Linux RAM; actual persist decision recorded.
Root health verifies327releasefiles,133prototypefiles, all35old account rows,
keys/realm and ordinary-TLS public assets, guest guard and unchanged relay policy.
See root-public-*-result.json,root-document-public-cleanup-result.json,
root-live-health-result.json,site-cutover-production-{stage,apply}-result.json.

Current checks: root account/egress suite and independent-WAN root P2P acceptance
are IN PROGRESS. Fresh owned Moonpie driver12990 port42685, folder
/home/maint/snap/chromium/common/codi-root-wan-1792840685500341538; local SSH
forward3739216 at http://127.0.0.1:60135. Only automation uses Tailscale; public
browser traffic remains HTTPS/RTC. Read current moonpie-browser-fixture.json and
use moonpie-root-browser.py cleanup after suites; never kill unrelated sessions.
Previous outside fixture10277 is stopped/removed. USB tethering remains unneeded.

Private VM now c23 at actual ROOT24 after the CLI tests, original ingress restored,
no pending journals, owned temporary website/Caddy stopped. SSH49747/HTTPS57503
unchanged. Do not recreate it or run old assumptions that expect root12/20.

The ROOT/BLOG milestone does NOT complete the goal. Required full self-organizing
P2P/islands/layers, checkpoints/valid-branch convergence, browser PoW, spectator
roles and real staged8k tests plus complete request/plan audit remain unfinished.

Root WAN acceptance is now COMPLETE for the current bounded profile: group36,
history23 and scope/chess/PGN PASS from104.180.210.33 and24.126.137.85,3actual
Chrome contexts per suite with normal public TLS. Both ends select public TURN/
TLS443; no HTTP chat relay. These are NOT direct-UDP/full gossip/8k claims.
First Moonpie history startup reported tab crashed; cause unproven, original
failure/diagnostics retained, fresh unchanged-product repeat PASS. Harness adds
owned browser logging and closes every owned context even after inherited cleanup
errors. Both drivers report no owned sessions. Moonpie12990 and local forward
3739216 are stopped (verified absent/zombie); owned fixture folder removed.
No external browser/control fixture remains active. USB tethering unneeded.

Root final health still PASS, config568bcd2a.../native PIDs unchanged, all35original
accounts retained; current38includes3owned QA accounts now disabled. Evidence
active-system/evidence/root-cutover-live.md; bound aggregate
root-live-milestone-result.json covers deployment, root browser, WAN and cleanup.
served_apps_public/CONTRIBUTING.md now names the actual root URL; ROADMAP's current
state note supersedes its early historical rows. Private VM remains root24/c23.
Next work is the full request/reference audit followed by required gossip/islands/
chunk-checkpoints/PoW/audience/8k implementation and staged tests. Goal ACTIVE.

Root live source/proof now frozen and clean/verified on webhost at
93717e3c9327f91b68a94724bdc8f575431c4197, tools/codiserver/root-live-r1,
34declared files + manifest629530a1fd5fd408f54dd4ef8a4852d0798ced5c8cb9ff5718855dc9502e39e1.
All35tracked files verified under hosting lock, source-only. Config568bcd2a...,
native1460700/1460696/1460759 and running website unchanged; no pending journals.
Receipt root-live-source-sync-result.json. Forward cutover plan0fc38836... remains
an already-completed operation tied to activation source5fa9221, NOT a reusable
rollback/start command after source advancement. Prepare a new inverse plan if
needed. Root-live-health.py currently binds the cutover's root3 snapshot; update
inspection expectations after a legitimate future bounded renewal, never restore
old authority state to satisfy an old check. Full goal remains ACTIVE.


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

## Development status clarification — 2026-10-25

The user explicitly clarified that the site is live but not yet public: it is
externally reachable development, not a public launch. The owner is the only
current user and existing accounts are tests. Continue the authorized live-first
development/testing workflow; no VM gate or production-user migration process is
required. Preserve security boundaries, /desktop/, /blog/ and other hosted sites.
Clean up obsolete generated artifacts as updates proceed, retaining the current
release and one usable rollback. Do not interpret test-only accounts as an
instruction to delete accounts, keys, documents or permission state.


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


## R15 source-only activity delivery — 2026-10-26

Current candidate c569fec7b9b30b8b2717e7251f62a3a447c4e8c7eb0c2d6e6cbe691c615ad837,
manifest fe0a61ad3d13e111f366b559ed49016fbc2b8ccc99f3498704d869fadc4c7cf8;
service/QA byte-credit-r15/core-r15, existing all-r3 apps unchanged. Exact-entry
current ordered batch delivery metadata/backoff suppresses repeat activity,
16KiB lease closed on normal/partial startup cleanup. No authority from receipts.
Milestone-r15 PASS140(scoped) includes same-driver old6/new3activity negative
control, nine-profile mesh12->6; burst1348490signed bytes/17.944s remains high.
Quiet20.105s0payload excludesRTC/IP/TURN/assets/long upkeep. No efficiency/
release acceptance or physical mixed-link/WAN/8k proof. Initial membership
FAIL12 retained; QA single-response hold permitted a timeout retry before ACL
revocation. Barrier now holds all retries with abort cleanup; final private16
requires2real requests, floor7before/after fresh denial. Product ACL unchanged.
See active-system/evidence/device-membership.md and milestone-r15 receipts.
Live preservation-r15 PASS keeps SDK36868/config19f/sourcebd8/paused-empty chat/
root/blog/files/prototype/private state. Root4expired/steward failed; explicit
Root5approval pending, old helper PRE-EXPIRY ONLY. No signing/deploy/restarts/
hosting/ports/boot/source pull. Private backup follows. Keep R15/R14negative
baseline/R13native-race/R9lease/C7/legacy/nativeSDK/rollback/private state.
Full goal active. Fast fiber and3Gbackhaul peers may share a channel; user cost/
relay consent must remain separate from measured capacity. General adaptation,
global/durable/relay/legacy limits, islands/joint voters/long-gap/chess/PoW/8k/
WAN/audit/rollout unfinished. Never lower quorum/verification to hide slow links.


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
