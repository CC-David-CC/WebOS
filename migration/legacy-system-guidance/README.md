# CodiServer active system

Current external preview: **https://ksu.codes/hidden/** uses native13/schema5,
frontend R16, registered private server files and optional Anon/Register/Sign in.
Files → My server files supports import, download, editor saves and explicit
copies to/from the temporary Linux filesystem. Anonymous files remain in RAM.
See [current file access and evidence](evidence/public-private-files.md).
Public TURN over shared443 is enabled with a forced relay policy. A native14/R18
candidate now preserves old cached clients while allowing signed modern ICE
preferences. Real installed-upgrade, account/file, cache, voice and peer checks
pass in the private VM; external rollout remains pending. See
[cached-client compatibility evidence](evidence/ice-preference.md).
Independent WAN remains unverified. /desktop is unchanged.

The actual desktop fills the browser viewport, without the lab header,
proportion sliders, sizing presets, comparison mode or preview scaling.
Includes real v86 Linux, shared Files/Text Editor, terminal, calculator, shared
peer networking, separate text chat/chess lanes and PGN. Backend development
sources for the guest relay, issuer and steward live here.

## Live development preview

The connected preview is now live at **https://ksu.codes/hidden/**. Two fresh
Chrome sessions passed default-trusted HTTPS/WSS, chat, separate chess moves,
Linux and ping/DNS/HTTP through box-webhost. Cross-network TURN/NAT verification
is still unfinished. **https://ksu.codes/desktop/** remains the unchanged sizing
prototype. See [current paths, limits, evidence and rollback](evidence/live-hidden-preview.md).

Current native controller/online code is `/srv/codi-connected/releases/native13-abb67a1f7a2e718c`,
with the existing `/srv/codi-connected/venvs/517179c/bin/python` and config
`/etc/codi-connected/ksu/managed.json`. Historical installation sections below
describe earlier states. All three online roles now run; bootstrap is stopped.

Phone support includes native terminal keyboard input, bottom terminal controls,
viewport following while typing, contained menus and a workspace chooser on
the top-bar computer icon. Network details are in the session-dot menu. See [touch frontend evidence](evidence/touch-preview.md).

## Local terminal voice input

The floating microphone works with the previously focused app input or terminal.
Tap to start; tap again to stop and insert at the saved cursor/selection.
The mic changes to a stop square while recording. Drag it to move the floating
overlay; no bottom strip is reserved. Keyboard is off by default for voice
mode; the floating ⌨ toggle or terminal Keyboard key re-enables it.
Voice uses English Whisper tiny.en on the visitor's CPU/WASM. The approximately
68MB model/runtime preload alongside Linux, without opening the microphone.
Recordings remain in browser memory. There is no server transcription/upload.
Text appears after stopping; interim/live captions are not implemented. Nothing
is submitted automatically. Phone terminal keys are Keyboard, Ctrl+C, Tab, Esc,
Enter. See [voice behavior, evidence and limits](evidence/terminal-voice.md).

Workspace switching and minimizing preserve app fields/drafts. Running task
counts and task pickers cover only the current workspace; each workspace has
independent windows and pins. The phone roll-up '^' button is restored. Applications
→ Terminal opens another independent guest shell (up to64 PTYs).
Workspaces live only in the top-bar computer-icon popup.

## Run with guest Internet

```sh
cd active-system
python3 run.py
```

Open http://127.0.0.1:8130/. Stop with Ctrl+C. The launcher starts a loopback
server and QEMU/libslirp guest Internet relay. Ping, DNS and HTTP leave through
the computer running this relay. Browser peers still use the shared WebRTC pool.
Default identity is **Local / not server validated**; sign-in stays disabled.
The issuer and steward are optional separate development services, not started
by this command.

The local `.venv` is ready. To recreate it:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
```

QEMU (`qemu-system-i386`) must be installed. Linux must permit ICMP echo sockets
for the relay user's group. On this development machine GID 1000 was enabled at
runtime with `sudo sysctl -w 'net.ipv4.ping_group_range=1000 1000'`; this setting
is not persisted across reboot. No forwarding, TAP or firewall change is needed.

For static desktop only: `python3 serve.py --port 8130` (guest Internet off).
The bundled browser guest/runtime is under `.build/v86/`. Guest files and keys
remain in browser RAM; download work before reload or End session. No prior
account database, private signing key, or old service state was copied here.

## Development boundary

Make functional desktop/network/login changes here. The sibling `desktop-lab`
is a separate sizing tool. Root-level files are the preserved pre-split baseline;
changes are not automatically synchronized between these directories. Existing
scripts that specifically test lab presets belong to the lab and are not active
site UI requirements. Public hosting has not been switched by this split.

## Optional combined identity + discovery + Internet fixture

For development only, generate TLS fixtures once with
`.venv/bin/python scripts/prepare-tls-preview.py`. In separate terminals:

```sh
.venv/bin/python scripts/serve-connected-discovery.py --instance full-computer
.venv/bin/python guest-relay/server.py --port 8132 --origin https://127.0.0.1:8446 --identity-config-port 8118
caddy run --config .build/checks/tls-preview/Caddyfile.active --adapter caddyfile
```

This uses an installed Caddy binary (the project-local tool is at
`../.build/tools/caddy`). The certificate is self-signed: automated tests use
only the explicit fixture CA/SPKI; this is not a public deployment. This mode
uses development issuer-backed identities, keeps public sign-in off, and retains
the guest Internet relay. End each process with Ctrl+C. See
[evidence](evidence/combined-identity-internet.md) for measured scope and limits.

## Shared HTTPS / TURN TLS listener experiment

`python3 scripts/turn-loopback-check.py --sni` runs a disposable loopback-only
fixture on 18443, using the project-local extracted Coturn and HAProxy binaries.
Generate fresh `.build/checks/tls-sni-preview` fixtures first with
`.venv/bin/python scripts/prepare-tls-preview.py --output-dir .build/checks/tls-sni-preview`.
It validates both real browser relay delivery and TLS hostname routing; it stops
its processes and removes credentials afterward. See
[measured scope](evidence/shared-tls-port.md). This is not a public 443 deployment.

For the expiring-credential variant, run
`python3 scripts/turn-loopback-check.py --sni --rest`. It tests expired/altered
credential rejection before real relay delivery. This is a private fixture,
not a public credential issuance service. See
[verification](evidence/turn-expiring-credentials.md).

`python3 scripts/turn-loopback-check.py --sni --session-rest` tests the optional
development issuer policy end to end: public config contains no TURN credential,
key-authenticated session issuance supplies temporary credentials, and renewal
preserves established peer connections. This is only fixture opt-in; the normal
launcher and public sign-in are unchanged. See
[verification](evidence/session-turn-issuance.md).

## Private TURN configuration (local development only)

Both `scripts/serve-connected.py` and `scripts/serve-connected-discovery.py`
accept `--turn-secret-file PATH --turn-url 'turns:HOST:PORT?transport=tcp'`.
The file must be outside public assets, in an owned private directory, with no
group/other permissions; use a 32..128 character URL-safe token without a newline.
Coturn must use that same secret. No credentials are put in public config.
Restart deliberately after changing the secret. Default launchers keep this off.
See [checks and limits](evidence/turn-private-file-launchers.md).

**Public boundary:** `ksu.codes/desktop/` is the sizing prototype. Do not deploy
these active-system backend services or guest Internet there.

## Temporary staging and final root URL

The final system will run at the main domain root. `/hidden/` is temporary
external staging; `/desktop/` remains the live sizing prototype. Development
launchers accept `--base-path /hidden`; omit the option for domain-root mode.
The steward endpoint must use the corresponding `/hidden/rendezvous` or
`/rendezvous` path. Configure the proxy to preserve that WebSocket path while
stripping the application prefix for issuer/guest/static routes.

Both layouts are exercised by `scripts/full-system-check.py` (add
`--base-path /hidden` for staging). See
[route and proof verification](evidence/configurable-mount.md). These commands
use temporary local TLS fixtures; they do not deploy the external site.

## Native release and private runtime

Both issuer launchers accept `--runtime-dir /absolute/private/path` to keep
writable state outside the application release. It is mutually exclusive with
the older local `--instance` option. The directory must be owned and 0700, with
safe ancestors, and cannot overlap the source tree. The launcher holds an
exclusive runtime lock. Issuer keys/accounts persist across restart; login
sessions stay in RAM. Default combined discovery remains disposable (at most
600 seconds). Explicit provisioned mode supports a stable scoped service and
operator-signed renewal; see below.

Build a new allowlisted connected release from this directory:

```sh
.venv/bin/python -B scripts/export-connected.py --output .build/releases/NEW_NAME
.venv/bin/python -B scripts/export-connected.py --verify .build/releases/NEW_NAME
```

The output includes native code and must not be mounted as a web document root.
Native launchers stage their own public tree separately from private state.
Existing destinations are never overwritten. Deployment installs the pinned
dependencies separately; no virtualenv or test credentials are exported.

For the actual immutable-release browser check, use
`scripts/full-system-check.py --read-only-release --release-dir PATH`, adding
`--base-path /hidden` for staging. This uses bubblewrap and private
`/run/user/UID` fixture state. See [evidence and deployment limits](evidence/immutable-connected-release.md).

## Stable provisioned development discovery

`scripts/provision-connected.py init` prepares an existing/new private issuer
runtime and a separate operator root directory. Run the connected launcher with
`--runtime-dir PATH --provisioned-steward` to retain the same root, realm, service
key, public scope and publisher ledger across restart. No root key is passed to
the online launcher. Explicit `renew` updates the signed provision; `export`
recovers already committed bytes after an interrupted output operation.

Delegation is bounded to 30..86400 seconds, default one hour. Expired discovery
stops until a valid operator renewal arrives; identity sessions remain available.
The existing bounded worker restart budget still applies. This is development
provisioning; separate production Unix roles and root custody are unfinished.

Add `--provisioned-steward` to the full-system checker to exercise actual operator
renewal while both browsers keep their VM, session and established peer link.
Read-only checks now protect the operator commands too and verify the exported
release again after execution. See [commands, evidence and limits](evidence/provisioned-discovery.md).

## Independently owned development services

The standalone issuer accepts paired `--discovery-policy PATH` and
`--discovery-bundle PATH` options. It reads operator-pinned public policy and
signed steward metadata. The steward retains its scoped key and publisher ledger;
the operator retains the root signing key. Provisioning can use an existing
issuer's public config through `provision-connected.py init --issuer-config PATH`.

`scripts/isolated-roles-check.py --release-dir PATH` exercises actual different
systemd DynamicUser accounts, native file-access denials and local HTTPS/WSS/RTC
browsers at `/hidden/`. Add `--base-path ''` for domain-root routing. It requires
the existing sudo authorization and creates disposable services only. See
[ownership, evidence and remaining deployment work](evidence/isolated-service-roles.md).

## Locked guest relay account

The operator tool `scripts/install-service-accounts.py --guest-gid GID --apply`
(run as root) prepares dedicated locked `codi-issuer`, `codi-steward` and
`codi-guest` accounts. Choose an unused GID on the target machine. Existing
incompatible accounts are refused rather than modified. No service or network
setting is enabled by this command. The relay's optional `--require-ping` refuses
startup unless its account can open an unprivileged ICMP echo socket.

`scripts/managed-roles-check.py --release-dir PATH --temporary-ping-group-policy`
tests those actual persistent identities with disposable systemd units/state,
private data boundaries and real guest ping/DNS/HTTP alongside RTC chat/chess.
It permits only an adjacent guest GID for the test, restores the original ping
policy, and preserves existing previews. Add `--base-path ''` for root routing.
This is local verification, not permanent service installation. See
[commands, evidence and external deployment gaps](evidence/managed-guest-role.md).

## Persistent native service operator

`scripts/manage-services.py` installs disabled systemd units and explicit private
state ownership from a root-owned profile-5 release and pinned virtualenv. It
provides one-time `provision`, bounded `renew`, committed `export`, readiness-checked
`start`, `stop` and `status`. Root authority is never passed to an online role.
The static bootstrap unit runs only for explicit provisioning. Missing managed
issuer keys/ledgers fail closed; existing authority is not reinitialized.

`scripts/persistent-services-check.py --release-dir PATH` tests actual installed
unit files and operator commands with disposable `/srv` state and real browsers.
It preserves existing previews, restores temporary ping policy and removes its
units/state afterward. See [installation evidence and remaining gates](evidence/persistent-service-operator.md).

The tested profile-5 package is now installed privately on box-webhost as KSU
source commit `517179c`. Issuer/steward run on loopback only; guest is stopped,
units are not boot-enabled, and `/hidden/` is not routed publicly. The live
`/desktop/` remains unchanged. See the installation evidence for exact paths,
the bounded delegation expiry and explicit renewal commands.

## Private checkpoint recovery

The profile-6 controller adds `backup`, `verify-backup`, `restore` and
`recover-operation`. Snapshots are root-only and include sensitive keys/password
hashes. Recovery preserves issuer/root identities, advances discovery authority,
rotates its scoped key and quarantines recovered credentials until reset. An
independent fence and journal block stale authority or partial recovery startup.

Box-webhost has a verified on-host checkpoint and config version 2. The initial
profile-6 installation is documented in
[checkpoint evidence](evidence/native-checkpoint-recovery.md); the current
controller and online services have since moved to profile 7 below.

## Private code upgrade and rollback

Profile 7 adds journaled `upgrade`, `rollback` and code-transition recovery while
preserving current accounts, signing keys and authority state. Failed startup
or a wrong identity policy automatically restores the preceding code. Local
installed-unit/browser checks cover `/hidden`, domain root, interrupted unit
writes and recovery after a successful commit whose journal could not be cleared.

At the profile-7 milestone box-webhost passed an actual upgrade → rollback →
upgrade round trip. Its controller and online issuer/steward code were
`/srv/codi-connected/releases/1db6187`. Current lifecycle/renewal commands use
the profile-8 controller listed in the live-preview section above, with the
same pinned environment and managed config.
Guest was stopped at that historical milestone. The current public preview uses
profile 8 and all three online roles, as documented at the top of this page. See
[exact code rollback tests](evidence/native-code-upgrade.md).
