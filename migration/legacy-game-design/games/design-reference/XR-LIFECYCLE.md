# XR lifecycle — implemented by each 3D app

Sources: S05, S09, S12, S13 and S18 in [SOURCES.md](../SOURCES.md). The design below is a proposed lifecycle, not a tested engine adapter.

## States and transitions

Use one explicit lifecycle state, not independent `isXR`, `isLoading`, `isEntering` booleans that permit impossible combinations:

```
loading → window-paused ↔ window-playing
               ↓ Enter XR (explicit user gesture)
          xr-requesting
            ├── denied/error → window-paused + explanation
            └── xr-placement / xr-paused → xr-playing
                        ↓ Exit / system end / visibility handling
                    xr-ending
                        ↓ observed session end
                    window-paused
any state → disposing → disposed
```

A window already in transition cannot start a second request. Preload modules, build UI/materials and prepare engine XR support before enabling Enter XR. Perform the actual session request within the user gesture; do not await network fetches before it. Capability checks are hints, not guarantees of grant. Handle denial or another active immersive session without closing the other app or retrying in a loop. The browser arbitrates immersive ownership; no new desktop XR service is needed.

## Shared state, different view

At entry, finish the current simulation transaction, pause at a tick boundary, save desktop camera/control presentation, clear held input and release transient grabs. Keep the **same** model/world and scene. Attach the XR camera/session and set a model-to-XR presentation transform. Placement/recenter never changes game masses, gravity or game-coordinate geometry. Resume only after the user confirms placement/readiness.

On exit, preserve the latest game state, not the pre-entry snapshot. Remove XR interaction handles, reset timing accumulators, restore desktop camera and settings panels, focus the app and display Resume. Do not reload the game or serialize/deserialize the model merely to change presentation. No catch-up simulation after returning from a suspended headset.

## Engine-specific binding, one path each

Three.js: retain the same WebGL renderer/scene and use `renderer.setAnimationLoop`. Enable/configure the renderer's XR manager; prepare the layer/render target as required by the pinned version. A manual `navigator.xr.requestSession` path must register session end immediately and then bind to the renderer. Do not also instantiate a button helper that requests a second session.

Babylon: create the chosen XR experience helper ahead of time and use its request/enter/exit path, with observers installed before user entry. Verify that the prepared path does not consume the user activation before requesting. Do not manually attach a second session alongside the helper. Engine/session observer cleanup is app-owned.

Use WebGL as the initial release baseline. This is an implementation choice, not a claim that WebGPU XR cannot work. Adding a WebGPU profile requires a separate measured compatibility gate; do not swap engine type inside a live scene to hide a failed entry.

## Capability policy

Tabletop apps offer independently probed immersive AR and VR. VR remains meaningful on a virtual table. AR placement uses hit testing when granted; without it, use a deliberate manual placement/recenter UI. Never call a manually placed object a surface-locked anchor. Anchors are optional session features, not durable saved world coordinates.

Room and spectator apps explicitly declare their supported session mode in their own XR.md. Do not automatically label every 3D app AR-capable. Request only features needed by that app. Hand input is optional; `select` plus target-ray/controller interaction must work. Do not assume gripSpace exists or every input source has articulated hands. Loss of tracking cancels a pending manipulation/shot and clears actions safely.

Physical-world depth, meshing, anchors, eye tracking and raw cameras are separate capabilities. The base games need none of them for correctness. Passthrough is not a collision map or a safety guarantee. Do not run MediaPipe to replace native XR hand data.

## Immersive UI and Rive

Provide in-world Pause, Resume, Settings, Save checkpoint, Recenter and Exit controls that are readable and reachable. Rive is rendered into a scene panel/texture where required; a DOM overlay is optional and not the only path. The regular desktop settings are not assumed visible in XR.

File import/system pickers may not be usable in an immersive session. “Load file” explains that it will exit XR, performs the normal document action in the original window, and leaves re-entry to a new user gesture. Save to an already-authorized destination can happen inside XR; otherwise offer explicit exit/export. Never silently resume or auto-reenter XR after a picker.

## Closure, pending requests and failures

On dispose: make gameplay inert synchronously, invalidate the generation and stop input/audio/workers. If a request is pending, keep only the minimal cleanup continuation required to observe it. A late session is immediately ended and never adopted. When a live session ends (button, browser, system menu, runtime loss), run the same idempotent end handler. A stale end event cannot change a new session's state.

If end() rejects, retain an honest error/cleanup state; do not claim immersive control was released while it is still active. Do not end any other app's session as recovery. Cleanup order must be tested with the selected engine so freed render resources are not used by one last XR frame.

## Required transition experiments

Enter from active play, pause, settings and loaded state. Deny permission. Close before request resolves. Exit using the app and system UI. Lose/reacquire tracking. Suspend the headset. Recenter. Enter/exit ten times. Keep a second app open. Confirm same model/world identity across each transition and no duplicate physics stepping, lost progress or repeated score events.
