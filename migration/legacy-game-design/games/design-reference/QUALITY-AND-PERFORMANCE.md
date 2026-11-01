# What “polished” means here

A title screen and a cube do not meet these designs. A finished small game has a complete loop, clear goal or activity, understandable failure/success, tutorial affordances, settings, deliberate save behavior, restart, original coherent assets, feedback and measured reliability. Keep content small enough to finish, not so broad that everything becomes placeholder.

## Art/audio/input

Use one coherent style per game and a modest family resemblance across menus, not copied artwork. Provide readable contrast, original/licensed sounds and volume/mute. Success feedback must not block the next action unnecessarily. On phones, controls must work with real thumbs. Every interaction has a visible response even when invalid. No shader effect is worth hiding a score or making the headset uncomfortable.

Rive is required where specified and must be integrated into the actual game/UI. A placeholder cannot close that gate. Avoid putting Rive on every projectile or tile merely to increase usage; it belongs where expressive state matters.

## Initial budgets — hypotheses to measure

| Profile | Initial target |
|---|---|
| Screen | Smooth 60 Hz on the selected ordinary device; measured graceful quality reduction where slower |
| XR | Meet the active headset session's frame budget, not a hard-coded assumed refresh rate |
| Phone pixel ratio | Start capped around 1.5; measure text sharpness and render cost |
| Desktop pixel ratio | Start capped around 2, adjusted per app and viewport |
| Physics sandbox | Start with ≤96 bodies and a smaller active-body budget; bot arenas much smaller |
| Rive textures | Small fixed surfaces, dirty updates, no per-frame recreation |
| AI | Bounded time/node budget, cancelable worker jobs, no UI-thread search stalls |
| Content | Bundle only the opened game's requirements; no eager load of all engines |

These numbers are design starting points, not test results or guaranteed hardware capabilities. Record asset transfer sizes, cold/warm start, CPU/frame timings, p95 stalls, texture dimensions, active bodies, context counts and known live resources. Browser memory observations are approximate; do not report zero leaks just because one heap counter went down.

Quality controls may change resolution, shadows, particles and animation sampling. They must not silently remove collision bodies, change AI fairness, alter score or speed up the game. Performance adaptations are presentation changes unless explicitly exposed as a game rule.

## Stress tests

Open three instances of one game; then one Phaser, one Three, one Babylon and one Rive app. Verify input focus and independent state, pause covered/inactive apps using real signals, close the middle window and continue the rest. Repeat open/close while loading. Check no owned workers, listeners, ongoing audio or XR sessions remain after acknowledged cleanup. Allow the browser's resource release to be asynchronous and document observations.

Run phone and Galaxy XR sessions long enough to observe thermal/frame instability. Decide measured content limits before adding more effects. Do not optimize by inventing a global engine manager; simplify content and ownership first.
