# Terminal session source ownership

Terminal now owns its original PTY/session/startup/render glue and unchanged startup test, plus four historical upgrade/scroll/touch/voice notes. Six added file bodies/modes and their selected histories are retained exactly. The original three startup-output assertions pass with original/primary/recovery source hidden. They execute the reference functions in a Node VM; no real shell/PTY/guest or browser was started.

Selected Terminal `7041257d48f232a5908b5ed3ff54c1312edf2465`; mechanical baseline `4d15d6f44c48a616a291a83e4ad0e2f14d6b0c37`. Existing view and CSS remain unchanged. The view still expects old host terminal/UI/window APIs, and the glue uses old guest/global state. Public Runtime/Desktop/Linux session interfaces, assets/dependencies and actual guest/host lifecycle must be ported before activation. Human/agent actions must reach the same explicit instance/session/resource operations; view disposal must not implicitly kill shared services/jobs.

Historical documentation is old evidence, not new acceptance or permission to execute commands. No microphone, clipboard, touch, account synchronization or agent acceptance was run. Terminal and Linux/v86 are still optional, outside the minimum. No new service or dependency is enabled.

Private maps, source/history checks and checkpoint: `/home/dflanag3/Projects/.webos-migration/run-20261115-43-terminal/`.

## ksu.codes readiness check on November 20

The live profile has `guest:false` and omits the Terminal app. The live viewer's `app.js`, `desktop-apps.js` and `terminal.js` match organized source byte for byte. The viewer already exposes the Terminal host API. Its live app manifest has no xterm bundle, and the guest worker, boot manifest, WASM, firmware and kernel URLs return HTTP 404. Beta serves those inputs. The organized worker runtime matches beta's bytes, and the organized Worker client adds failure and termination handling.

The guest image and kernel have verified build inputs, and a rebuilt image passed the R730 boot check. A Terminal candidate needs the pinned xterm bundle and notices, Linux/v86 assets and profile registration. Use the organized sources and beta as a browser behavior reference. Qualification should exercise real PTY input, independent terminal windows, close/reopen, failure cleanup and separation from account files. The viewer currently starts a guest on sign-in when the profile enables it, with 256 MiB of guest memory per browser tab. Launch on demand avoids that cost for accounts using other apps.

The Terminal entry is `apps/terminal/index.mjs` with its CSS and pinned xterm.js 6.0.0, Fit 0.11.0 and Serialize 0.14.0 packages. These are the versions named by beta's bundle notices. Register the module and styles through `assets/desktop/apps.json`. The guest needs `assets/desktop/guest-worker-client.mjs`, `assets/desktop/guest-worker-runtime.js`, `assets/terminal/v2/image.json` and the initramfs named by that manifest. The current worker reads `.build/v86/libv86.js` and the viewer boots with `.build/v86/v86.wasm`, `seabios.bin`, `vgabios.bin` and `vmlinuz` from the same runtime directory. Keep the matching v86, firmware and Linux notices with the bundle.

## Terminal rollout

Terminal is live on ksu.codes. The source assembler enables the optional
guest with \`--terminal enabled\` and the pinned Runtime app-builder dependencies.
The viewer starts the guest on Terminal mount and uses the public
\`assets/terminal/v86/\` directory. This guest shares a temporary home across
its shell windows and is separate from the Files app's account storage.
See [release, tests, and rollback](TERMINAL-ACAD-CRAFT-UPDATES.md#terminal).
