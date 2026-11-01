# Engine-specific implementation guidance

## Phaser

Bind the existing bundler to an explicit supported Phaser major version. The current documentation inspected here includes a 4.x API family; examples/plugins from 3.x need review. A Phaser.Game belongs to one app's canvas/container. Avoid automatic page-wide fullscreen and global keyboard capture. Resize from the app root, not window.innerWidth.

Board games (blocks/snake/chess/cards) need logical grids or piles, not rigid-body solvers. Sky Courier and Lantern Leap benefit from Arcade Physics. Garden Defense and Pocket Rally use simple deterministic game kinematics. Let exactly one scheduler advance each domain: never combine an automatic physics update with a manual second step. Keep pure rule functions testable outside Phaser.

Rive hero/menu textures are proposed application integration, not a bundled Phaser plugin. Pin the CanvasTexture method signatures and show a tiny proof before expanding art. Closing a scene is not necessarily closing the entire game; dispose the per-window Game, input, audio and companion resources. Sources S01–S03.

## Three.js + Rapier + WebXR

A WebGLRenderer, scene, presentation cameras and one Rapier World live per window. Three's setAnimationLoop owns presentation. A fixed-step accumulator (initial target 1/60 s, bounded catch-up) advances Rapier exactly once per tick. Interpolate display if useful; no physics derived from refresh rate. On suspension/transition, clear elapsed-time debt rather than running hundreds of catch-up ticks.

The real game coordinates stay in meters. XR table scale/placement maps model space into reference space; pointer/hand targets map back by the inverse transform. Never rescale physical bodies when the user resizes the virtual table. A collider's physical size must not depend on device pixel ratio.

Start on the main thread with strict small-world budgets; add a worker only after profiling proves a benefit and a tested state/input exchange is defined. Do not preemptively split every engine into multiple queues. Rapier snapshots need matching logical ids and tested engine versions; determinism includes initial-state/order/math constraints [S07,S08].

Dispose materials/geometries/textures and Rapier allocations deliberately; removing a mesh is not freeing its GPU resources. Handle context loss by pausing and showing recovery; do not continue pretending to render. Sources S04–S08.

## Babylon.js + WebXR

One Engine, Scene, app model and prepared XR helper per window. Use native Babylon animation groups, cameras, picking, instancing and spatial audio where they serve the game. Most catalog games do not need a rigid-body library. Pocket Golf is the explicit Havok qualification case.

Select the engine's scheduling mode once. If physics is enabled, prove exactly which Babylon/physics scheduler owns a world step and align game updates with it. Do not call render-driven automatic physics and a second custom world.step. A fixed-step or deterministic-lockstep setting alone is not proof of replay equivalence. Test 30/60/90-ish presentation schedules against the same game commands.

Prepare the XR helper before enabling entry, use its one session path and make all in-world menus usable without optional DOM overlays. Keep the non-XR camera and the scene; switching to XR should not construct a second game. Sources S09–S13,S21.

## Rive-first applications

JavaScript is the authoritative model. Rive animates its view and can emit validated UI intents. Prefer data-binding contracts and an app-owned low-level loop for multi-artboard activities. For a single high-level runtime, understand its own loop and pause/cleanup lifecycle rather than stacking another animation loop on it.

Rive's visual state machine is not the save format. Persist semantic pose, activity, score and story values; reconstruct the artboards. Use one owned AudioContext where audio is needed, created/unlocked after interaction. No universal audio manager or desktop modification is required. Sources S14–S17.
