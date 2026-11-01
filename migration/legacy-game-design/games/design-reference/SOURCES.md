# Official source register

Reviewed 30 October 2026. URLs are documentation references, not a pinned tested dependency set. Author-created game mechanics, budgets and architecture proposals are design choices, not upstream guarantees.

## S01 — Phaser game lifecycle

https://docs.phaser.io/phaser/concepts/game

Game instances, scenes and destroy lifecycle. Bind the actual chosen Phaser version; do not mix major-version examples.

## S02 — Phaser input

https://docs.phaser.io/phaser/concepts/input

Pointer, touch, keyboard and gamepad input; application-window focus still needs integration.

## S03 — Phaser CanvasTexture

https://docs.phaser.io/api-documentation/class/textures-canvastexture

Candidate bridge from a rendered Rive canvas into a Phaser texture; not a claimed official Rive plugin.

## S04 — Three.js WebGLRenderer

https://threejs.org/docs/pages/WebGLRenderer.html

Use engine animation-loop ownership and explicit renderer disposal; verify signatures for pinned release.

## S05 — Three.js WebXRManager

https://threejs.org/docs/pages/WebXRManager.html

Session integration and XR camera/input access.

## S06 — Three.js CanvasTexture

https://threejs.org/docs/pages/CanvasTexture.html

A canvas can be the source for an in-scene texture.

## S07 — Rapier JavaScript serialization

https://rapier.rs/docs/user_guides/javascript/serialization/

takeSnapshot/restoreSnapshot exist. This design binds restoration to a tested exact engine build.

## S08 — Rapier JavaScript determinism

https://rapier.rs/docs/user_guides/javascript/determinism/

Determinism has initial-state, ordering and version preconditions; external input/math can break them.

## S09 — Babylon.js WebXR helpers

https://doc.babylonjs.com/features/featuresDeepDive/webXR/webXRExperienceHelpers/

Helpers provide session entry/exit and input setup. Prepare before the user presses Enter XR.

## S10 — Babylon.js dynamic textures

https://doc.babylonjs.com/features/featuresDeepDive/materials/using/dynamicTexture/

Existing canvases can feed dynamic textures; explicit update and UV handling remain necessary.

## S11 — Babylon.js Havok plugin

https://doc.babylonjs.com/features/featuresDeepDive/physics/havokPlugin/

Documents browser WASM physics and MIT runtime distribution. Does not establish public availability of complete Havok engine source.

## S12 — Android XR web development

https://developer.android.com/develop/xr/web

Chrome on Android XR documents WebXR support and hand-first adaptation. This is not a test of the user's headset/browser build.

## S13 — WebXR Device API

https://www.w3.org/TR/webxr/

Session ownership, security, feature negotiation, input, frame lifecycle and ending.

## S14 — Rive low-level web API

https://rive.app/docs/runtimes/web/low-level-api-usage

Low-level runtimes allow application-owned advancement/drawing and require explicit cleanup.

## S15 — Rive runtime parameters

https://rive.app/docs/runtimes/web/rive-parameters

Data binding, rendering and lifecycle reference. Verify exact binding API for chosen asset/runtime pair.

## S16 — Rive Canvas versus WebGL2

https://rive.app/docs/runtimes/web/canvas-vs-webgl

Fidelity/performance/context-count tradeoffs. Select one verified renderer per authored asset profile.

## S17 — Rive web runtime license

https://github.com/rive-app/rive-wasm/blob/master/LICENSE

Runtime MIT license; artwork, fonts, authoring service and third-party content have separate rights.

## S18 — WebXR DOM Overlays Module

https://www.w3.org/TR/webxr-dom-overlays-1/

DOM overlay is a separately negotiated XR feature, not a guarantee that desktop HTML appears in immersion.

## S19 — chess.js

https://github.com/jhlywa/chess.js

Rules/move-validation library under BSD-2-Clause; an opponent/search implementation is separate.

## S20 — Babylon.js Havok distribution

https://github.com/BabylonJS/havok

WASM/JS runtime package. Review exact package and notices before bundling.

## S21 — Babylon.js advanced animation/lockstep

https://doc.babylonjs.com/features/featuresDeepDive/animation/advanced_animations/

Engine scheduling and animation options; selecting a time step is not proof of cross-device deterministic replay.
