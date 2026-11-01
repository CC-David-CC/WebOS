# Small architecture, real boundaries

## One app, one model, one presentation owner

The desktop owns windows and shared services. The app owns its game, resources and immersive session. A game model owns rules, score, progression and simulation state. A renderer reads that state and supplies input intents; Rive is a view, not a second scoring engine.

For rigid-body games, Rapier/Havok owns physical body state while ordinary app data owns goals and metadata. These are different domains, not two competing copies of positions. Stable application ids connect them. Scene transforms are derived views. Never let a sprite tween update a body position without an explicit model command.

Input devices produce commands such as `move`, `grab`, `launch`, `select` and `pause`. Rule code validates them once. Pointer, touch, keyboard, gamepad and XR adapters do not implement different game rules. Keep this app-local; it is not a universal game protocol for the desktop.

## Async start without async mount

`mount` constructs a small shell, installs scoped listeners and returns `{element, dispose}`. Schedule heavy imports/startup afterward. First render a useful Loading/Retry state. Initialization must not block the desktop with synchronously decoding all assets.

Every async allocation must check ownership after resolving. A late engine, texture, worker or XR session created after disposal must be released rather than adopted. Use an instance lifetime flag/epoch plus AbortController for cancellable operations. AbortController does not cancel every library import or XR request; late-result cleanup is still necessary.

A renderer starts only after the app owns it and the canvas has non-zero dimensions. A collapsed/minimized window is not a divide-by-zero rendering size. Observe the host element, not the outer browser viewport. Scope CSS to the root; no global body/fullscreen resets.

## No extra runtime supervisor

Code in `pseudocode/` and `index.pseudo.mjs` is explanatory, not a framework you must implement. Translate its roles into direct local engine calls. Root `catalog.json` documents game requirements and never becomes a mandatory desktop manifest. Categories are folders, not base classes.

Engine modules and immutable asset bytes may be cached by ordinary module/HTTP mechanisms. Mutable physics worlds, scenes, Rive artboards, document state, sound buses and worker jobs must not be module-global. Do not call a package-global cleanup operation that invalidates another instance.

## Ownership and teardown

Stop accepting input, stop simulation and cancel scheduled work immediately on disposal. Clear held keys/pointers and release manipulation constraints. Disconnect observers and remove listeners. Stop app-owned audio. Terminate app-owned workers. Release Rive instances and textures, then engine objects in a tested order.

If XR is active/pending, mark the instance dead synchronously but end the owned session before destroying resources the session still uses. A late request resolution gets `end()` and teardown, never gameplay activation. Do not wait for the desktop to await `dispose()`; it returns synchronously. Observe/handle async cleanup errors internally and expose them in diagnostic evidence. Ending can be asynchronous; returning from dispose is not proof that the browser has already released all GPU memory.

## Focus and visibility

Keyboard shortcuts apply only while this app has focus and not while a text field is being edited. Capture gamepad inputs only for the active game or its owned XR session. Never prevent scrolling across the whole desktop. Pointer capture belongs to one gesture and must clear on cancel, blur and transition.

Use actual host notifications if they exist. `document.visibilityState` does not tell you which desktop window is covered by another window. Without an app visibility signal, use explicit pause and focus-loss pause; do not claim exact occlusion detection. In immersive mode, XR session visibility governs suspension: ordinary DOM blur caused by XR must not incorrectly pause a visible XR session.

## No authority expansion

These are trusted packaged game modules, not arbitrary-code execution environments. Saves are data only. No eval, arbitrary import URLs, scripts in save files or executable Rive events. Multiplayer and remote AI are outside scope. Use only granted document operations; never pass host services into artboard event payloads or worker messages.
