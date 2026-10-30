## Workspace split

- **[desktop-lab](desktop-lab/README.md)** — standalone desktop proportion controller; no application backend. Run `python3 desktop-lab/serve.py --port 8131`.
- **[active-system](active-system/README.md)** — full-window computer, v86, guest Internet and networking; no proportion controller. Run `python3 active-system/run.py` (port 8130).

These are independent development targets. The root implementation below is the preserved pre-split baseline.

Live URLs: **https://ksu.codes/desktop/** remains the sizing prototype;
**https://ksu.codes/hidden/** is now the connected development preview. The homepage
is unchanged. See [current preview evidence and remaining work](active-system/evidence/live-hidden-preview.md).

# CodiServer desktop lab

A small functional browser desktop using the existing Xfce-style theme, an ephemeral local identity, and a real v86 Linux terminal. No JavaScript
framework, npm, FastAPI, package installation, external CDN, or backend API.
Python's standard-library HTTP server serves the static files.

From the CodiServer repository, prepare the already retained v86 guest assets once and start the static server:

    cd desktop-preview
    ./scripts/prepare-v86-assets.sh
    python3 serve.py

Open **http://127.0.0.1:8097/** in the host computer's browser. The VM is not
required to use the viewer. The server listens on loopback only. A different
port can be selected with `--port`.

The ongoing version progression and network/login-first priorities are recorded in [ROADMAP.md](ROADMAP.md). Proposed games will start as simple text-chat/notation interfaces; graphical games are deferred.

## Browser guest milestone status

The desktop opens directly into a randomly named local user. The header labels it **Local / not server validated**. Each page load creates a non-extractable P-256 signing key in browser memory; the account menu shows its public-key fingerprint. Nothing is sent to an account service, and neither the identity nor key survives reload or logout. There is no signin page or account backend.

One pinned v86 0.5.472 instance boots the prepared Debian 6.1.0-54-686 kernel and BusyBox initramfs. The matching VirtIO/9p modules are included in the initramfs and loaded before mounting a browser-memory filesystem at `/home/guest`. The shell runs as `guest` (UID/GID 1000) with a controlling serial TTY. Every terminal view attaches to this one guest. No host filesystem is mounted, and guest writes disappear when the page closes or reloads.

Files and Text Editor operate on the same `/home/guest` as the shell. Files supports folders, text creation, file import, downloads, Trash and restore. Text Editor supports Save, Reload, Ctrl+S and downloads, with drafts preserved across desktop rerenders. Calculator and Help are functional apps. The simulated Chromium window and captured application launchers have been removed; use normal browser tabs for websites.

This guest includes BusyBox tools such as `vi`, `awk`, `sed`, `grep`, `cp`, `mv` and `mkdir`; the full Debian root, Python, SQLite and GCC are not bundled. Loopback ICMP works with `ping -c 2 127.0.0.1`. The interactive shell remains UID 1000; a fixed-command setuid helper allows only BusyBox ping. The default static server leaves guest Internet networking disabled. An optional private home-host relay has passed real guest ping, DNS and HTTP checks; see [guest Internet evidence](evidence/guest-internet.md). v86 runtime, kernel and BIOS files are locally prepared under ignored `.build/v86/`; `scripts/prepare-v86-assets.sh` verifies pinned hashes and rebuilds that bundle from the retained sibling cache. The static HTTP server only serves page/runtime assets; it does not create accounts or run guest commands.

Sizing settings are in memory. Save/load JSON presets are explicit downloads/imports.

## Try it

- Start with **Shipped**, **Touch**, or **Roomy**. All sliders update immediately.
- Open Applications for Terminal, Files, Text Editor, Calculator, or Help.
- In Files, create a folder or text file, import a file from your computer, download it, or move it to Trash and restore it.
- In Terminal, try `ls`, `cat Documents/README.txt`, `echo hello > notes.txt`, or `vi notes.txt`. Terminal-created files appear in Files. Arrow keys, Ctrl+C, Ctrl+D, Ctrl+L and paste are supported.
- Edit a document and press Ctrl+S to save it in the guest. Download important files before End session.
- Drag title bars and resize windows from their bottom-right corner. Try roll-up,
  minimize, maximize/restore, close, and grouped terminal selection on the panel.
- Switch workspaces. Right-click a task icon, or open its grouped picker, to pin
  or unpin it. Reopen a minimized window from the picker.
- **Window logo size**, **Window control width**, and **Window control symbols**
  are independent. Touch/Roomy keep the shipped logo and title area unchanged
  while enlarging the control symbols and their horizontal hit areas.
- Compare with the shipped layout. **Real VM** shows the actual reference screen.
- Use **100%** or fullscreen to judge targets. Fit scales down everything,
  including the touch targets. CSS pixels are not a physical millimetre guarantee;
  device pixel density and desktop/browser scaling still matter.
- Save/load a JSON sizing preset. Settings remain in memory unless explicitly exported.

### Previous layout choices

**Previous layout choices** recalls earlier experimental settings, not an
approved or locked design. These remain subject to change: 48 px panel,
31 px icons, 17 px panel text, three 82 px workspace buttons, 41 px menu rows
with 16 px text, a 44 px title bar, 96 px control buttons and 17.3333 px title
text. The logo remains 24 px and control symbols remain 24 px; both can still
be adjusted independently. Applications and the account label are bold.
Older saved presets retain their previous automatic logo size when migrated
to the independent logo-size control.

Rolled-up windows must lose the normal window's minimum-height constraint.
They show only the selected title height plus the native 12 px bottom frame:
56 px for this proposal, or 98 px for the shipped 86 px title. The 98 px
native shaded height was inspected on the installed Surface Book 2. Unrolling
restores the previous full height; the resize handle is hidden while shaded.

## Reference and limits

The reference comes from the running
`CodiServer-fleet-dev-ready-20261020-amd64.iso` VM at 1920×1080. Its real Garcon
menu hierarchy, installed icons, fonts and Xfce wallpaper are bundled locally,
with package copyright notices under `assets/licenses/`. The shipped model uses
34 px panel height, 20 px panel icons, three workspaces, approximately 60 px
workspace miniatures, 27 px menu rows and the CodiServer-Touch 86 px title theme.
`reference.json` retains the inspected Xfce settings; `reference.js` makes the
same data available without fetching a backend. The original distro sources
remain in CodiServer's existing source/cache inventories.

The desktop windows are browser-native views, and the terminal runs real Linux inside v86. This is not an X server or a pixel-perfect GTK renderer. The session and network panels report browser/guest state rather than simulated battery or Ethernet values. Guest commands execute inside the browser guest; no host configuration or ISO settings are changed. Some
runtime icons were already missing in the VM and retain its fallback appearance.
The optional volume button is a proposal, not part of the captured panel.
The 44 px overlay is a sizing guide, not a claim of accessibility certification.

## Approval flow

1. Iterate and approve this HTML prototype on the host PC.
2. Translate the approved proposal to the live test VM and obtain approval there.
3. Only then rebuild the ISO using the existing pipeline.

This viewer never applies settings to the VM or ISO. A saved preset is a design
proposal, not an installable Xfce configuration. Native workspace-button sizing,
menu spacing and independent Xfwm control geometry may require CSS, plugin or
XPM theme changes beyond straightforward xfconf settings. Preserve the current
known-good desktop while implementing and testing that translation.

## Refresh the reference

Run `scripts/capture-session.py` **inside the disposable VM**, as its logged-in
desktop account, with DISPLAY and XAUTHORITY set. It writes
`/tmp/codiserver-preview-reference.tar.gz` containing public menu data and assets.
Copy that archive to the host and extract into this directory. It exports both
reference data files. Capture the real screen with QMP or the existing VNC helper
and save a menu-open image to `assets/vm-menu-reference.png`. Do not capture
private windows or credentials. The capture is a design reference, not a test
receipt or a replacement ISO-building pipeline.

## Browser checks

The current end-to-end harness uses only Python's standard library and ChromeDriver. Start a loopback driver in a separate terminal after installing Chromium:

    chromium.chromedriver --port=19515

With the static server running, execute:

    python3 scripts/functional-check.py

Use `--chrome-binary` for a non-Snap Chromium installation. The driver is a development tool; visitors need only a current Chrome/Chromium browser. The harness creates and closes a disposable browser session and writes its receipt, browser logs, downloads and screenshot under ignored `.build/checks/`.

The fresh Chromium run passed 13 integration groups covering actual Linux boot, guest UID, serial commands, loopback ping, shared files in both directions, `vi`, Ctrl+C, GUI editing, import/download, Trash/restore, calculator, draft preservation, terminal scroll colors, pointer drag/resize, window controls, workspaces, one VM across comparison, logout ephemerality and missing-asset failure handling. It executed v86 on the host machine. No uncaught JavaScript errors were found.

`scripts/browser-check.py` is the older geometry-prototype CDP harness. Its historical 22 passes are separate from this new functional coverage; it has not been rerun against the reduced application menu.

## Future hosting: ksu.codes

When deployment is requested, host this under `ksu.codes` on `box-webhost`. Use HTTPS on port **443**, with port **80** only for HTTP-to-HTTPS redirects. Future guest networking/live communication should use a same-origin **WSS** endpoint behind the HTTPS reverse proxy; keep its internal service port on loopback. No additional router forwards are expected. No hosting, DNS, firewall or router changes have been made in this phase.

Production needs only the app's static HTML/CSS/JS, public assets and prepared v86 bundle; do not publish the entire repository or build/test caches. Serve over HTTPS so Web Crypto and browser clipboard features work on visitors' computers. The current application has no account backend. The optional guest Internet relay is a separate service, currently tested through a private SSH tunnel; it is not part of the static deployment.

## Browser-native architecture notes

The browser project is separate from the installed Surface desktop and the
CodiServer ISO. The native Desktop Lab controls the real Xfce session; this
project explores a desktop-like application inside a browser.

Design direction supplied by David:

> If you recreate processes, file descriptors, pipes, sockets, signals,
> permissions, and a Unix filesystem exactly, you'll spend a considerable
> amount of effort emulating interfaces that don't naturally fit browser
> security and lifetimes.
>
> Instead, use a simpler internal design:
>
> - Workers or WASM instances for execution.
> - Message passing for communication.
> - Shared buffers where genuinely necessary.
> - OPFS for persistent application data.
> - Browser APIs as the device and network interface.
>
> That lets the browser's existing infrastructure do the hard work.
>
> You don't need to implement a memory allocator for the OS, a network stack,
> or graphics drivers.
>
> Those layers already exist below your application.

Use these principles for the browser application's own architecture. The
separately selected, locally served v86 Linux guest provides compatibility for
existing Linux tools; it is not a requirement to reproduce Unix abstractions
throughout the frontend. Browser-native apps can use Workers, messages, OPFS
and browser capabilities directly. These are design notes, not a claim that
those features have already been implemented. A Linux guest still brings its
own kernel and internal memory/network abstractions, even though the browser
application does not need to implement them itself.

### Direct peer chat foundation

Open **Applications → Chat** in two browser sessions. Create an invitation in one,
paste it into the other and choose **Answer invitation**, then paste the returned
code into the first and choose **Accept answer**. Once both report `ready`, use
**Send chat**. Codes contain connection metadata: exchange them deliberately.
The default configuration has no STUN/TURN service, so Internet traversal is not
guaranteed. Identity is explicitly local and unvalidated. Closing a Chat window
keeps the session connection; Disconnect or End session closes it.

`python3 scripts/peer-check.py --visible` opens and leaves two isolated Chromium
windows connected for inspection (requires loopback ChromeDriver on port 19515).
Chat history is bounded and temporary. Chess moves will use a separate logical
channel and PGN record; they are not implemented by this chat milestone.

### Connected identity (loopback development)

Run `.build/auth-venv/bin/python scripts/serve-connected.py` and open
`http://127.0.0.1:8098/`. The launcher stages an explicit set of public files under
`.build/connected-public`; issuer keys and the account database are separately
stored under `.build/connected-state`. It binds only to loopback. It reuses the
supplied v0.3 Python identity service and adds HEAD support for guest asset checks.
Restart the launcher to stage updated source files.

This entry still opens directly as anonymous, now with **Test server validated**
identity. It is not an official authority. The desktop renews certificates near
expiry; failed renewal is shown without switching to a local identity. End session
revokes its server session. The sign-in page remains disabled. Registered account
entry is exercised by the integration checker, with no alternate browser account
store. No chat, move record, guest file, or signaling code is stored by the issuer.

`python3 scripts/identity-check.py` checks real Chromium against the loopback
issuer and records `.build/checks/identity-result.json`. Requires ChromeDriver on
19515 and the connected launcher on 8098. Its random test accounts are stored in
the development database; never run it against a real account service.

Both development servers restrict public paths. The static 8097 server now serves
only desktop runtime files, `assets/`, listed network modules, and the six guest
boot assets; it does not expose the workspace, scripts, dependency environments,
or connected issuer state. `python3 scripts/public-boundary-check.py` checks both
8097 and 8098 using status-only HEAD requests.

Multiple Chat windows share one live subscription and draft. Closing the last
Chat window releases the subscription; the peer connection stays until Disconnect
or End session. Reopening restores bounded session history. Incoming messages
while unsubscribed are not retained. Reconnecting starts a fresh conversation
scope. The registry keeps at most 16 histories and marks discarded older messages.

### Text rooms and moves

After connecting in **Applications → Chat**, open **Applications → Rooms** on both
sides. Create a room on one side; choose its invitation and **Accept room** on the
other. Ordinary room chat and chess notation have separate inputs and histories.
The creator plays White. Both peers check move order, side and legal SAN moves
before applying them. Illegal local moves are rejected before being sent. **Decline room** refuses a pending invite.
Rooms expire after five minutes; all room state is ephemeral until End session.
**Download PGN** saves the legal move record; **Download chat** saves its separate
transcript. **Historical PGN** imports a legal main line as a read-only record,
without sending packets or changing the live game. Comments/variations are not
retained by that view. Imports are limited to 64 KiB and 2048 plies. No graphical
chess board is included.

`python3 scripts/peer-check.py --rooms` exercises the actual two-browser UI.
Add `--url http://127.0.0.1:8098/` to exercise issuer-backed anonymous identities.

The rules engine is pinned chess.js 1.4.0, served from `assets/vendor/chess/` with
its BSD-2-Clause license and hash manifest. `python3 scripts/vendor-chess.py`
reproduces those files from the integrity-checked package. No Node/npm or CDN is
needed by visitors. Room invitations now require the signed chess-standard/1
policy (invitation v2); reconnect both peers with current tabs when upgrading.

### Several peers in one session

Creating another connection invitation adds a peer without replacing existing
connections. Each Chat window has its own **Chat peer** selector; drafts/history
are shared only between views of that peer. **Cancel pending** stops a setup attempt;
**Disconnect selected** affects just the selected peer. Rooms choose **Peer for new
room** explicitly and stay bound to that peer afterward.

`python3 scripts/pool-check.py` exercises three browsers, two simultaneous games,
duplicate-join rejection, cancellation, isolated disconnect and End session. Add
`--url http://127.0.0.1:8098/` for issuer-backed identities. This is still manual
signaling with same-computer RTC evidence; automatic discovery and WAN traversal
are not yet implemented.

Outbound traffic now uses one session-wide byte scheduler. Control has reserved
queue/native-buffer space; ordinary chat/moves remain reliable with explicit send
errors on capacity/rate/backpressure. Expired queued game events are not sent.
`python3 scripts/traffic-check.py` checks actual signed RTC contention and explicit
retry/cancellation; add `--url http://127.0.0.1:8098/` for the development issuer.
The bulk test is a transport fixture, not a new file-transfer app or WAN benchmark.

### Optional local peer discovery demo

Run `.build/auth-venv/bin/python scripts/serve-discovery.py`, then open
http://127.0.0.1:8100/ in two Chrome page sessions. In Chat, choose **Join discovery**
in both, **Discover peers** and **Invite selected** in one, then **Accept peer**
in the other. Rooms carries separate ordinary chat and legal chess notation.
Stopping discovery preserves established RTC connections. Keys/leases live only
in RAM. Descriptors and control admissions renew while the current identity and the
ten-minute demo delegation remain valid. Ctrl-C stops the demo.
This uses internal loopback ports 8100/8101, with no router changes. The ordinary
8097 desktop remains backend-free. Details and test scope:
[evidence/desktop-discovery.md](evidence/desktop-discovery.md).

### Peer certificate upkeep

Peers using the current desktop negotiate certificate refresh over their existing
RTC connection. A renewed issuer proof keeps the same session/account/key and
advances expiry without resetting the connection or replay sequence. Local mode
stays server-free. Room grants retain their own deadlines. Verification and limits:
[evidence/peer-identity-maintenance.md](evidence/peer-identity-maintenance.md).

### Room renewal

The current desktop renews accepted two-peer rooms over their existing connection.
Chat, legal chess moves and PGN history continue across grant deadlines with the
same room and sequence state. Certificate bounds still apply; unsupported peers
retain the original expiry. [Contract and evidence](evidence/room-renewal.md).

### Optional discovery failover

A configured descriptor set can now recover through another release-pinned
steward while existing peer connections stay up. The browser keeps one active
control socket and its original session key. Default local mode stays server-free.
[Configuration, tests and limits](evidence/steward-failover.md).

### Isolated development issuer preview

The optional connected preview can run independently of the default local desktop:

```sh
.build/auth-venv/bin/python scripts/serve-connected.py --port 8115 --instance identity-audit
```

This uses `.build/connected-instances/identity-audit/public` and private sibling
`state`. It is a development issuer, not an official/public account service.
Omitting `--instance` on alternate ports selects separate state per port. The
original port 8098 retains its existing connected-public/connected-state paths.
Reuse an instance label to retain its test accounts/key; choose a new label for
a fresh issuer. No signin gate is added to the default local desktop.
