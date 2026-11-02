# Desktop game preview review

Reviewed 2026-11-01 against commit
`1c5845baa2c7779692381e08e7a2b98dab844ae9` (plus the review-only commit on top
of it), Chrome 156.0.8078.47, and a bundle rebuilt from that worktree. The
review covers all 28 games registered in the four desktop groups: 8 Arcade,
7 Physics, 7 World, and 6 Interactive previews. This version supersedes the
earlier review at `bc2e30b6` and folds in the five game changes made between
the two baselines.

This is a preview review, not a release qualification. “Reviewed” below means
the named evidence exists. It does not mean final art, every content branch in
the rendered UI, XR hardware, physical touch, or physical audio has passed.

## Evidence and result

- All 28 previews loaded in the real isolated desktop, rendered nonblank
  interactive windows, made no cross-origin requests, and had no page errors
  during the launch review.
- All 28 launched twice at the same time. Closing either window left the other
  mounted and usable; closing both removed their state and listeners without
  reviving a window.
- All 28 also passed an immediate close during startup. No app reattached after
  the close or produced a page error.
- All 28 account workflows passed save, account synchronization, paused
  reopen, and account-isolation checks. Individual tests also cover conflict,
  deleted-file, stale-operation, and changed-destination cases where those
  operations exist.
- The current source passed 24 TypeScript checks, 201 Vitest tests, plus the
  standalone Falling Blocks, Memory Garden, and Story Cards rule tests. The two
  packages without scripts have browser and account coverage.
- The game menu test passed all 28 stable IDs in the four groups. Registry,
  catalog-capacity, and invalid-game recovery tests also passed.
- Twenty-nine interaction regressions passed, covering pointer and keyboard
  ownership, touch cancellation, focus loss, pause, close protection, delayed
  saves, destructive confirmations, and focused text fields.
- Desktop screenshots were inspected for every preview. All have a visible
  playfield or activity surface, but most are purpose-built procedural
  presentation rather than production artwork.

The current bundle manifest SHA-256 was
`c4a52f93da339f148825b31edcbac9891bd514effafceebba566ebe61f6b24fe`.

## Changes in this baseline

- Solitaire now locks all board input, shortcuts, draw mode, touch controls,
  pause, and undo while a save is pending, and a solver-generated draw-one deal
  was replayed through all 126 actions to victory on desktop and emulated
  touch.
- Clockwork Quest corrects keyboard path movement (W/Up forward, S/Down back,
  forward through opened doors), marks movement as unsaved progress, and adds
  a dedicated XR controller with mock-tested entry, exit, external end, close
  during entry, failed exit retry, and disposal.
- Orbital Courier now reports dirty state to the desktop close guard, rejects
  recreation of deleted saves, and stops flight keys from consuming text in
  focused fields.
- Expression Puppet preserves the edited save destination during delayed
  writes, protects deleted saves, refreshes the challenge target on change,
  and clarifies that the displayed score is the last submitted match.
- Memory Garden keeps revealed tiles focusable with `aria-disabled` instead of
  ejecting keyboard focus from the board mid-play.

## Portfolio coverage gap

The 28-title catalog is still concentrated in real-time action, spatial
physics, toy interaction, and engine/XR demonstrations. Chess Study and
Solitaire are the only seated, turn-based strategy games. There is no
third-to-fifth-grade skills game, no math-facts or number-sense loop, no dice
or territory game, and no word, pattern, or science-game entry. The strongest
rule cores today are Chess, Solitaire, Snake, Falling Blocks, Marble Works,
Clockwork Room, and the three deterministic tower-defense/wave games; several
other titles lean on presentation rather than decisions.

Recommended additions are small, rule-first, DOM/Canvas games with no new
engine:

1. A 3rd–5th grade arithmetic or fraction game with generated problems,
   automatic difficulty, a number-line or visual model, and a short session
   loop (for example, an addition/multiplication or fraction path game).
2. A Risk-like territory game on a 20–40 region map: simple reinforcements,
   dice battles, region bonuses, seeded RNG, and a greedy one-ply local AI
   that uses the same legal-move interface as the player.
3. A pattern, word-building, or "guess the rule" game to cover verbal and
   logical reasoning, which the catalog currently omits entirely.

The turn-based candidate fits the proven Chess Study pattern: a pure state
model and a bounded AI behind revision-guarded workers, then presentation.
The concrete catalog plan is in [GAME_CATALOG_GAP_PLAN.md](GAME_CATALOG_GAP_PLAN.md).

## Verdict

The 28 previews are coherent, independently mountable development games with
working rules, representative interaction, account persistence, and lifecycle
cleanup. The release and art-readiness claim is not met: only Falling Blocks
ships an authored `.riv` file. The other 27 apps either show explicitly labeled
procedural substitutes or expose only a future Rive contract. None of the
fourteen planned XR experiences has physical Galaxy XR evidence, and no game
has physical-device, thermal, or final-art acceptance across its full content
set.

### Arcade games

| Preview | Gameplay review | Interaction and lifecycle | Persistence | Art readiness |
| --- | --- | --- | --- | --- |
| Falling Blocks | Tutorial, 40-line sprint, and endless rules; movement, rotation, hold, drops, line clears, lock reset, top-out, and exact snapshots have rule coverage. Runtime covers play, score/coach reactions, and invalid launch recovery. | Desktop keyboard and emulated multitouch; independent held pointers, focus pause, close cancellation, reduced motion, and synthesized audio were checked. | Save, changed-file rejection, conflicting copies, Files launch, exact paused restore, and fresh-session reopen passed. | **Strongest preview:** the bundled 2,146-byte `coach.riv` is an authored Rive asset and rendered in the desktop frame. Final polish and physical-device review remain open. |
| Chess Study | `chess.js` rules, three bounded AI levels, undo/revision guards, promotion, and eight tactical solutions have rule coverage. A real browser AI worker played a turn and reopened the saved history. | Board keyboard/pointer input, editable-field isolation, AI-turn locking, pending undo, and focus behavior were checked. | Save, sync, optional Files route, fresh phone-sized reopen, and malformed-history rejection passed. | The guide is a development fallback; `chess-guide.riv` is absent. AI strength measurements remain open. |
| Solitaire | Klondike draw modes, legal pile moves, undo, recycle order, auto-foundation, seeded invariants, and a solver-generated 126-move draw-one deal-to-win path passed on the rendered board. Desktop pointer, keyboard, and emulated touch were exercised. | Long piles, multi-card moves, focus, close protection, save-time input locking, and input ownership were checked. | Save, sync, paused reopen, changed-file handling, and completed-deal restore passed. | The table host is procedural; the final host Rive artboard and completion sequence are absent. |
| Sky Courier | Three-stage route, checkpoint, projectile pool, collisions, lives, shield, pause, and stage transition rules passed. Runtime steering and firing were exercised; a complete stage-three campaign run is not automated. | Keyboard and emulated touch steering/fire, focus loss, held-input release, and dirty close were checked. | Checkpoint save, sync, Files route, paused restore, and invalid-file preservation passed. | The cockpit panel is a labeled fallback; `courier-pilot.riv`, final environments, and final audio are absent. |
| Snake Garden | Six campaign gardens and endless mode, queued turns, rocks, tail vacation, food placement, full-board victory, and save reconstruction passed. Runtime start and account save were exercised. | Direction controls, save-boundary close protection, desktop focus suspension, and independent windows were checked. | Save, sync, paused reload, account isolation, and invalid/missing fallback passed. | The seedling guide is procedural; `garden-guide.riv` and final presentation are absent. |
| Lantern Leap | Six-room movement model covers one-way and moving platforms, coyote/buffered jumps, checkpoints, deaths, lanterns, and best times. Runtime representative-room movement and restoration passed; all six rooms were not played end-to-end in one rendered run. | Keyboard plus emulated movement/jump touch, overlapping input, focus loss, reduced motion, and pending close were checked. | Checkpoint save, sync, Files route, paused reopen, and malformed-file recovery passed. | The hero is a labeled shape. `lantern-hero.riv`, final room art, and audio are absent. |
| Garden Defense | Three maps with ten-wave queues, three tower roles, upgrades, projectiles, speed controls, currency, and checkpoint state have broad rule coverage. Representative building, wave, save, and map-switch flows passed; all 30 map-wave combinations were not rendered end-to-end. | Build controls, pointer/keyboard alternatives, map-change confirmations, focus pause, and dirty close were checked. | Mid-wave save, sync, Files route, paused restore, changed destination, and invalid-state rejection passed. | The advisor is procedural; `garden-advisor.riv` and final map/enemy/tower art are absent. |
| Pocket Rally | Three tracks, three laps, ordered checkpoints, penalties, ghosts, medals, and start-line restoration have model coverage. Runtime driving, focus release, and save/reopen were checked; full medal runs are not automated. | Keyboard, independent gas/brake touch holds, focus loss, and close protection were checked. | Save, sync, Files route, paused restore, and account isolation passed. | The speed/lap/medal panel is a labeled fallback; `rally-dash.riv`, final vehicles/tracks, and audio are absent. |

### Physics games

| Preview | Gameplay review | Interaction and lifecycle | Persistence | Art readiness |
| --- | --- | --- | --- | --- |
| Physics Playground | Real Rapier bodies, material changes, one-step ownership, grab bounds, six challenge cards, reset, and XR-model continuity have rule coverage. Runtime Run/Add/Material/Save/Reset were exercised; all six challenge outcomes are not a rendered end-to-end suite. | Pointer grabbing, keyboard alternatives, focus/minimize/workspace pause, explicit resume, pending close, and WebGL resource release were checked. | Exact Rapier checkpoint save, sync, Files route, paused restore, malformed state, stale confirmation, and conflicts passed. | The bench coach is a labeled fallback; no authored `physics-coach.riv`. An immersive session UI and headset evidence are absent. |
| Marble Works | Eight bounded puzzles, sub-stepped movement, placement atomicity, edit/reset, goal dwell, trace, and logical save reconstruction passed. Runtime shows the current Canvas2D presentation, not the group's planned Three.js/Rapier implementation. | Run/pause/resume, focus loss, pointer/keyboard controls, mutation guards, and pending save were checked. | Save, sync, Files route, running-save restore, and malformed-state rejection passed. | Presentation and coach are procedural. `marble-gate.riv`, 3D/Rapier models, and final pieces are absent. |
| Stack & Balance | Ten seeded sequences, support/dwell, one nudge, rotation footprint, release behavior, and saved block IDs passed. Desktop runtime exercised block interaction and outcome flow. | Keyboard and emulated touch, pointer cancellation, key-repeat guard, focus pause, and pending close were checked. | Save, sync, Files route, paused reopen, and malformed state passed. | The stability instrument is a labeled placeholder; `balance-meter.riv` is absent. Entered-XR lifecycle is not implemented. |
| Sling Targets | Twelve arrangements, three-shot limits, aim cancellation, bounded launch, swept scoring, and saved scored IDs passed. Runtime launch and recovery were exercised; all arrangements were not completed in the rendered UI. | Pointer/keyboard aim, interrupted touch, repeat guards, focus pause, and dirty close were checked. | Physics checkpoint save, sync, Files reopen, paused restore, and malformed state passed. | Power gauge is procedural; `sling-gauge.riv` and immersive XR controls are absent. |
| Gravity Pinball | Rapier table, launch/plunger, flippers, scoring cooldowns, bonus, ball drain, three-ball end, nudge limits, and checkpoint bytes passed. Runtime account save/reopen passed; all three table acceptance runs remain open. | Left/right/plunger holds, keyboard shortcuts, focus pause, account-scoped high score, and input focus were checked. | Save, sync, Files route, paused restore, and malformed state passed. | Score marquee is procedural; `pinball-marquee.riv`, final table art/audio, and immersive XR are absent. |
| Kinetic Relay | Eight layouts, transactional joints, one launch impulse, ordered gates, reset, XR state continuity, and exact Rapier restore passed. Runtime step/save/reopen passed; only a bounded default puzzle is known to complete end-to-end. | Mechanism selection, one-step control, focus pause, dirty close, and basic capability-aware XR entry were checked. | Save, sync, Files route, physics-build mismatch rejection, missing-file protection, and paused reopen passed. | Bell/checkpoint art is procedural; `relay-bell.riv` and all eight rendered puzzle runs are absent. Physical XR remains unverified. |
| Tabletop Bot Arena | Three robot classes, practice dummy, three AI opponents, cup rounds, shared drive/weapon rules, energy/cooldowns, ring-outs, and two save kinds passed model coverage. Runtime match save/reopen and input ownership passed; full 90-second cup play is not automated. | Overlapping emulated drive touches, keyboard, weapon/self-right, editable fields, focus release, and dirty close were checked. | Exact match snapshot, portable cup progress, sync, Files route, paused reopen, and isolation passed. | Robots and announcer are procedural; `bot-crew.riv` and final arena art/audio are absent. Immersive XR is not implemented. |

### World games

| Preview | Gameplay review | Interaction and lifecycle | Persistence | Art readiness |
| --- | --- | --- | --- | --- |
| Clockwork Room | All four mechanisms, dependency rules, inventory, hints, one-shot exit, no-deadlock rule, and committed-state restoration passed. A complete four-mechanism desktop run was exercised. | Desktop/phone-sized buttons and keyboard shortcuts, repeated-key handling, focus pause, loading/error states, and idempotent disposal were checked. | Save, sync, Files route, paused restore, malformed launches, missing saves, and temporary read failures passed. | Clock face and room are procedural; `clockwork-guide.riv` and the full entered-XR control panel are absent. |
| Crystal Defense | Two routes, eight-wave model, three tower roles, upgrades, enemies, projectiles, and mid-wave economics passed. Representative runtime build/save flow passed; the complete boss/wave run remains unverified. | Socket/tower controls, Escape while busy, focus pause, dirty close, and phone-sized restore were checked. | Mid-wave save, sync, Files route, paused restore, deleted-save protection, and malformed state passed. | Command panel is a development fallback; `crystal-command.riv`, final models, and complete XR controls are absent. |
| Drone Circuit | Three courses, ordered directional gates, obstacles, fixed-step flight, penalties, ghost samples, and exact pose restoration passed. Overlapping controls and save/reopen were exercised; full medal runs remain open. | Keyboard and independent emulated touch axes, focus loss, camera modes, pending close, and input isolation were checked. | Flight snapshot save, sync, Files route, paused restore, and malformed values passed. | Telemetry is procedural; `drone-telemetry.riv`, entered-XR pedestal controls, and final course art are absent. |
| Pocket Golf | Six holes plus practice, bounded strokes, settle gating, cup capture, safe-lie rollback, penalties, and scorecards passed. Runtime save/reopen was exercised; all-hole visual tuning remains open. | Aim/power alternatives, pointer cancellation, pause, focus loss, hole-change confirmation, and rolling-save warning were checked. | Last-settled checkpoint, sync, paused restore, deleted files, and change confirmations passed. | Caddie/score stand are procedural; `golf-scoreboard.riv`, final course art, and Havok tuning are absent. XR is capability-probed but not hardware-tested. |
| Target Garden | Three-round model, deterministic targets, swept projectile collision, ammo cancellation, pause clock, practice, and exact checkpoint passed. Runtime aim/save paths were exercised; full three-round scoring was not a rendered pass. | Pointer/keyboard aim, overlapping touch ownership, interrupted aim, repeat guard, focus pause, and phone reopen were checked. | Save, sync, Files route, paused restore, and malformed state passed. | Marshal is procedural; `target-marshal.riv` and final targets/audio are absent. Hardware XR remains unverified. |
| Orbital Courier | Five-mission navigation, parcel collection/delivery, home-ring completion, hazard phases, bounds, energy, and checkpoint behavior passed. A complete representative mission and save/reopen were exercised; all five rendered missions remain open. | Keyboard and independent phone controls, editable-field focus isolation, pointer camera, focus/visibility pause, input clearing, and teardown were checked. | Mission save, sync, Files pause/reopen, malformed/oversized rejection, deleted-save protection, and account isolation passed. | Ship computer, ship, environment, and hazards are procedural; `orbital-console.riv`, final assets/audio, and immersive XR are absent. |
| Clockwork Quest | Three rooms, six mechanism interactions, two gated puzzles, NPC dialogue, inventory, companion rescue, reachability, and exact logical save passed. A complete adventure was exercised in the rendered desktop. | Forward/back path keyboard controls, pointer movement, interaction controls, explicit resume, focus pause, unsaved-movement close guard, editable field isolation, and disposal were checked. A mock-tested XR controller covers entry, exit, external end, interrupted entry, and failed exit. | Save, sync, Files reopen, paused restore, dialogue/inventory continuity, isolation, and malformed/oversized rejection passed. | Characters, rooms, cage, and faces are procedural; final glTF animation and `quest-faces.riv` are absent. Real Galaxy XR hardware and in-world file actions remain unverified. |

### Interactive games

| Preview | Gameplay review | Interaction and lifecycle | Persistence | Art readiness |
| --- | --- | --- | --- | --- |
| Owl Companion | Blink, firefly, and expression activities have deterministic local rules; save codecs cover activity, RNG, score and settings. Browser/account checks covered activity progress and paused restore. | Buttons and phone-sized controls, focus pause, reduced motion, pending save, stale open, activity-restart confirmation, and disposal were checked. | Save, sync, fresh-session reopen, invalid/missing saves, and account isolation passed. | Main owl is procedural; `owl-companion.riv`, `Main`, `Presentation`, properties, and triggers remain to be authored and loaded. |
| Reactive Control Desk | Ten repair orders, clamped power/frequency/route, tolerance dwell, duplicate-submit guard, free play, and complete load mapping passed. Representative order and save interactions were exercised; all ten orders were not rendered end-to-end. | Range/keyboard alternatives, focus pause, disclosure behavior, pending save, stale open, and dirty close were checked. | Save, sync, Files route, paused restore, and malformed/duplicate-order rejection passed. | Desk is procedural; `control-desk.riv`, its artboard/state machine, and authored focus states are absent. |
| Story Cards | Twelve-node graph, choices, discovered endings, history validation, and three endings passed in model tests. The rendered desktop completed a light ending; transcript, restart, and save flows were exercised. | Semantic choice buttons, keyboard/accessibility flow, focus pause, restart/open confirmations, unsaved close, and deletion protection were checked. | Save, sync, Files route, paused restore, deletion handling, copy save, and account isolation passed. | Current scene is procedural; `story-cast.riv`, character/environment art, and narration audio are absent. |
| Expression Puppet | Eight challenges plus free play, clamped look/smile/brow/pose values, scoring, six saved pose slots, and Rive-view-model validation passed. Runtime slider/pose/save interactions were exercised. | Pointer and range controls, corrected pause/mute state, challenge target refresh, focus pause, pending save, stale open, dirty close, and teardown were checked. | Save, sync, Files route, preserved delayed-save destination, deleted-save protection, all pose values/slots, paused restore, and malformed ranges passed. | Main face and poses are procedural; `expression-puppet.riv` is absent. Only the typed contract exists. |
| Rhythm Garden | Three seeded gardens of four phrases, audio-clock judgment, independent simultaneous lanes, calibration, audio suspension, and phrase-boundary restore passed. Runtime lane taps and save/reopen were exercised; full medal runs and musical assets remain open. | D/F/J/K and four flower pads, single activation, held-key repeat guard, focus checkpoint, calibration, and focus pause were checked. | Save, sync, Files route, paused phrase restore, duplicate-note prevention, and malformed state passed. | Flowers are procedural; `rhythm-flowers.riv`, authored music, and final animations are absent. Physical audio latency is unverified. |
| Memory Garden | Practice/garden/grand sizes, seeded pairs, reveal gating, mismatch timing, win state, and exact save reconstruction passed. Runtime mismatch pause, restart, and save/reopen were exercised. | Pointer, keyboard focus movement, stable board focus during reveals via `aria-disabled`, 44px phone controls, focus-frozen mismatch timer, restart confirmation, and cleanup were checked. | Save, sync, Files route, paused restore, invalid files, and account isolation passed. | Creature tiles are procedural glyphs; `memory-creatures.riv` is absent. The shared immutable-asset strategy remains to be validated with authored art. |

## Remaining release work

The review closes the question of whether the previews can be exercised and
persisted. It does not close these release gates:

1. Supply and review authored assets for 27 previews. Only Falling Blocks has a
   bundled `.riv`; five Interactive previews have contracts but no artwork, and
   the other source groups generally have procedural panels or primitives.
2. Run every authored level, mission, wave set, track, exercise, and ending in
   the rendered desktop. Current rule suites prove the complete bounded models
   in most cases, while runtime suites intentionally exercise representative
   flows and persistence boundaries.
3. Complete immersive XR lifecycle, in-world controls, Rive panel behavior,
   and ten entry/exit cycles on Galaxy XR. Current evidence is local capability
   handling or model continuity, not hardware acceptance.
4. Test physical touch, multitouch cancellation, audible output, thermal and
   memory behavior on representative phones and headsets.
5. Finish the art direction pass. The screenshots show live, nonblank previews,
   but many playfields are sparse primitives or flat procedural panels rather
   than final production presentation.
