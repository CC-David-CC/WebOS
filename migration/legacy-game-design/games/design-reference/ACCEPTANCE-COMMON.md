# Common runtime gates — all NOT RUN

These gates apply to each implemented app. Document validation does not execute them.

| ID | Acceptance experiment | Initial status |
|---|---|---|
| C01 | mount returns a non-Promise {element, dispose} before expensive engine/asset startup. | not_run |
| C02 | Two mounts have independent models, RNG, progress, rendering, input, audio and Rive state. | not_run |
| C03 | Close during imports/asset decoding: late allocations are released and cannot attach to the old root. | not_run |
| C04 | dispose twice is safe; closing one window leaves adjacent windows functioning. | not_run |
| C05 | Keyboard/gamepad input belongs only to the focused app or its owned immersive session. | not_run |
| C06 | Touch release/cancel/blur clears held controls; two pointers retain independent ownership. | not_run |
| C07 | Narrow, wide, phone portrait and phone landscape layouts retain playable controls and readable UI. | not_run |
| C08 | Normal phone play requires no XR, camera, gamepad or orientation-lock support. | not_run |
| C09 | Complete title/tutorial/play/result-or-goal/retry loop with bounded, authored content. | not_run |
| C10 | Pause, settings, mute and reduced-motion behavior do not alter game rules unexpectedly. | not_run |
| C11 | Save/load restores the documented snapshot or checkpoint; no false exact-resume claim. | not_run |
| C12 | Wrong-app, invalid, oversized and unsupported-version saves leave current game unchanged. | not_run |
| C13 | Two windows saving to the same destination cannot silently overwrite under an invented locking guarantee. | not_run |
| C14 | Rive assets actually load; required artboards, typed properties and events are validated. | not_run |
| C15 | Rive is integrated at the specified character/menu/instrument location, not a placeholder badge. | not_run |
| C16 | One gesture cannot dispatch a Rive control command and an underlying game action twice. | not_run |
| C17 | Simulation/rules are independent of presentation refresh; only one owner advances each world. | not_run |
| C18 | Audio starts through user activation, pauses appropriately and stops on disposal. | not_run |
| C19 | Missing/failed assets or graphics context loss produce honest recoverable states, not a blank “ready” screen. | not_run |
| C20 | No runtime network dependency beyond chosen static assets/authorized files; no server-side game compute. | not_run |
| C21 | Resource evidence covers workers, listeners, timers, textures, audio and repeated open/close. | not_run |
| C22 | Performance/thermal evidence includes a real phone, not only desktop resizing. | not_run |
| C23 | Menus are labeled and keyboard accessible; information is not color/audio-only. | not_run |
| C24 | Release evidence identifies exact engine versions, asset hashes, devices and all remaining unrun tests. | not_run |

## Additional gates for all fourteen XR apps

| ID | Acceptance experiment | Initial status |
|---|---|---|
| X01 | The full window preview, settings, Load/Save and capability-aware Enter XR are present. | not_run |
| X02 | The session request is made from a user gesture after setup; denial returns to the same paused game. | not_run |
| X03 | One active/pending request per app; another app’s session is never ended or stolen. | not_run |
| X04 | The same game model/world identity survives entry; no parallel simulation or reloaded checkpoint. | not_run |
| X05 | App Exit and system end return to the original window with current progress and restored desktop camera. | not_run |
| X06 | Closing during a pending request ends a late session and releases resources without reviving the app. | not_run |
| X07 | Optional hands, hit test, anchors and DOM overlay are not assumed; supported fallback interaction is usable. | not_run |
| X08 | In-world Pause/Resume/Settings/Save/Exit controls are visible and operable without HTML DOM overlays. | not_run |
| X09 | Rive panel UV-to-artboard mapping works at corners and after resize/scale; no double selection. | not_run |
| X10 | One physics step per tick and one Rive advance per frame, not once per stereo eye. | not_run |
| X11 | Tracking/input loss clears held actions/grabs and never launches a canceled shot. | not_run |
| X12 | Placement/recenter changes presentation transform, not masses/gravity/collider sizes in model space. | not_run |
| X13 | Headset suspension clears time debt and resumes explicitly; ordinary XR-caused DOM blur is handled correctly. | not_run |
| X14 | File-picker-required actions explain exit, run in window mode, and do not auto-reenter immersion. | not_run |
| X15 | Seated, ray-driven play is complete; no mandatory physical room movement or raw camera access. | not_run |
| X16 | Ten entry/exit cycles and mixed app windows pass on the actual Galaxy XR with device/build recorded. | not_run |

Record evidence, not only a checkbox. A failure should identify the design invariant and smallest corrective change. Do not make the test easier to declare a flawed implementation complete.
