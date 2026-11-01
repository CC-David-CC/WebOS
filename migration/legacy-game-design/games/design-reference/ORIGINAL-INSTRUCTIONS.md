# Integration handoff — read before writing runtime code

You are integrating external design/pseudocode into an existing desktop whose real code you can inspect. The author of this package did **not** inspect the live ksu.codes repository or validate its build and service APIs. Treat every internal helper and dependency choice as a reviewable best-effort proposal. Preserve the user's outcome and hard contract, not accidental placeholder names.

## Non-negotiable scope

- Each game is a silo app. Export synchronous `mount(host)` returning `{element, dispose}` immediately. A fresh call owns a fresh state/engine/scene/input/audio/Rive instance.
- `dispose()` is idempotent; closing an app cannot end another app's XR session or destroy shared desktop services.
- Desktop and phone play are required. All fourteen 3D apps own their own Preview → Settings/Load/Save → Enter XR → Exit → original window flow.
- Single-player only. Local AI is allowed. No lobby, account, matchmaking, remote rendering, mandatory cloud inference or new desktop subsystem.
- Include real Rive integration from each app's brief. Do not satisfy it with a CSS animation labeled Rive.
- Do not modify the browser, Linux, CAD, file manager, existing editor or neighboring apps to make an assumed API look real.

## Review the existing system first

Inspect one minimal installed app, one canvas-heavy app, its registration/build process, DOM/CSS conventions, mobile window behavior, close path, focus/visibility notifications, file grants and save conflict handling. Identify any established host signal or disposal hook. The only host method assumed here is the user's `host.ui.make`; all others are **unbound** until inspection.

Write a short integration note with actual paths and method signatures. If an existing service solves an operation, use it. Do not create parallel files/session/terminal/networking managers. Do not implement a compatibility layer merely to preserve a helper name in pseudocode. A small app-local boundary around real file I/O is reasonable; a new platform abstraction is not.

Confirm the actual desktop/phone/Android XR browser builds, HTTPS/CSP/Permissions-Policy, module/worker/WASM asset serving and deployment path rules. Do not change site-wide COOP/COEP just to satisfy an unmeasured optional package. None of the initial designs requires shared-memory threading. Host source may intentionally cache immutable bytes/modules; it must not cache mutable app state.

## Dependency and asset qualification

Pin explicit tested versions in the actual project lockfile before building a vertical slice. The live Phaser reference pages inspected for this handoff show a 4.x API family; do not paste older 3.x plugins into an unreviewed major version. This handoff deliberately does not claim a tested version matrix.

Build a tiny Rive asset through an authorized authoring workflow and test its exact artboard, data-binding and event contracts before making 28 assets. There is no generated `.riv` file here. Use original/licensed assets and record their provenance. Rive runtime licensing does not automatically license an editor service or marketplace artwork.

For Pocket Golf, review the Havok runtime package/license/source expectations first. The project documents MIT redistribution of the web runtime; this package does not claim that complete Havok engine source is available. If full source availability is mandatory, stop and deliberately choose/review one alternative physics binding for this game; do not hide a second solver underneath it.

## Implementation order

1. Bind a single app to real mount/close/focus/files behavior. Do not register placeholder apps as finished.
2. Implement one app's complete rules and tests with bounded content.
3. Deliver a real desktop+phone vertical slice, including save/load, Rive, settings and errors.
4. For a 3D app, qualify session entry/exit on the real Galaxy XR and verify state continuity. An emulator is useful but not headset evidence.
5. Demonstrate two instances and mixed-engine windows; close during loading, during AI work and during XR entry.
6. Only then use the successful pattern as reference for the next app. Extract a helper only after a genuine common boundary is demonstrated; never require inheritance.

Start from the four lighthouse slices in ROADMAP.md. The remaining games are a catalog, not an instruction to create 28 shallow scenes in one pass.

## Rules for deviations

If a proposed abstraction is wrong, explain the failed invariant and replace it with a smaller correct design. Preserve the app contract, independent state, local execution and user-facing feature goal. Do not weaken tests to fit broken behavior. Report version/API/platform blockers precisely and record what was actually measured.

## Evidence and completion

Keep document checks separate from runtime tests. For each app record dependency lock hash, asset versions, device/browser, date, screenshots/video where useful, test command, result, frame/memory observations and unresolved defects. Read the common gates plus game-specific cases; all begin `not_run`.

Do not claim “phone supported” after resizing a desktop tab only. Do not claim “Galaxy XR supported” after mocking navigator.xr. Do not claim “saves work” after serializing JSON without restoring gameplay. Do not call a title screen a complete game or a checkbox a Rive integration.

Suggested final integration report: apps implemented; actual paths; loader changes; chosen dependencies; tests run; devices tested; unrun gates; blockers; remaining work. Preserve the existing desktop when a capability is unbound.
