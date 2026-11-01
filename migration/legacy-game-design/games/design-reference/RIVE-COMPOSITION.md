# Rive inside the games

Sources: S03, S06, S10 and S14–S18. This is a proposed composition design; there is no tested official Phaser/Three/Babylon Rive adapter supplied here.

## Three meaningful placements

1. **Window UI:** a Rive canvas in the app root for menus, mission portraits and results, paired with semantic HTML actions. Good for flat screens; not automatically visible in immersive XR.
2. **Engine texture:** render an artboard into a bounded offscreen/source canvas and upload it to Phaser CanvasTexture, Three.js CanvasTexture or Babylon DynamicTexture. Use for 2D heroes, character face panels, in-world instruments and XR controls.
3. **Rive-first app:** one owned runtime/renderer draws the activity; ordinary JavaScript owns rules and saved state. No Phaser or Babylon dependency needed merely to show an owl.

The last two are the main implementations for the requested in-game Rive capability. Do not load a 3D engine into an ordinary Rive toy without a real need.

## One clock owner

For an integrated texture, use the low-level API or a verified manual-advance mode. The host game's frame loop advances the appropriate artboards, draws them, marks the texture dirty and renders the scene. Never start an uncontrolled Rive requestAnimationFrame loop for every sprite. Do not advance a state machine twice because WebXR renders two eyes.

Simulation time decides gameplay. Presentation delta animates menus/poses. A paused game can still animate its settings panel without advancing physics or score. Rhythm Garden uses the audio clock for judgment and uses animation as feedback, never as the time source.

## Data and intents

The game writes typed view-model properties (or an explicitly mapped supported API in the pinned runtime). Use each RIVE.md as the asset contract. Verify names/types at load; missing artboard/property is an actionable asset-version error, not a silent fake animation. Avoid relying on deprecated stateMachineInputs APIs by accident.

Rive events may request an allowlisted UI intent such as Start or ToggleMute. The application validates it. They cannot award score, execute URLs/scripts, access host, choose a save path or mutate physics directly. A click passing through the Rive panel must not also fire into the scene. One gesture gets one interaction owner. Semantic HTML and Rive listeners must not dispatch duplicate commands.

## Texture and hit mapping

Choose a proven renderer per asset profile. Canvas2D is a straightforward source-canvas bridge and avoids an additional WebGL context, but does not match every authored Rive feature. WebGL2 offers stronger editor fidelity but adds context/compositing tradeoffs. Test the actual artboard; do not use “highest quality” as permission to ignore phone/XR budgets [S16].

Phaser: create/update a canvas texture using the chosen major-version API, upload after drawing, and reuse it. Avoid allocating a new texture each frame. Hero art is a view of a simple physics body.

Three.js: create a CanvasTexture once, set its update flag only after new pixels, and attach it to an appropriate material/mesh. Verify alpha, color space, filtering and premultiplication. No mipmap regeneration every frame unless required and measured.

Babylon: use one DynamicTexture sourced from the artboard canvas and explicitly update after drawing. Verify Y orientation, alpha and color space. Do not assume both engines use identical UV conventions.

XR interaction: ray hit → panel-local UV → invert texture/fit transform → artboard coordinates. Account for letterboxing, crop, mirrored UVs and device pixel ratio. For simple menus, explicit mesh hit zones that emit the same UI command may be smaller than full pointer emulation. Use one approach per panel, not overlapping active hit systems. Provide visible focus/hover/pressed state. Test corner taps and aspect changes.

Rive faces on a 3D model are animated 2D material panels. They do not replace Babylon skeletal locomotion, Three.js mesh rigs or physics collision geometry. That boundary is deliberate.

## Asset production and ownership

Each app includes a filename, artboard name, property types, triggers and authoring brief. No `.riv` binaries are present. Author original artwork via an authorized Rive editor/CLI workflow available to the integrator; validate actual tool support rather than inventing a file format or command. Package fonts/images/audio with explicit rights, relative URLs and runtime versions. Do not fetch arbitrary remote art at run time.

Start with one bounded surface per app, and an atlas/multiple artboards where useful. Initial targets: 512×512 character texture or 1024×512 panel, 15–30 Hz dirty updates for secondary UI, full visual rate only where measured worthwhile. These are profiling candidates, not a fidelity guarantee. Freeze offscreen/idle artboards and reduce motion without changing game logic.

Each mount owns its mutable artboards/state machines/textures. Shared immutable file bytes do not imply shared animation state. Clean up low-level instances in the documented order, then the source renderer/texture. Do not call a shared global runtime shutdown from one game's dispose.
