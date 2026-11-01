# Game preview asset gaps

Updated: 2026-11-01

The desktop game previews use authored UI and procedural local geometry and
audio when final content has not been supplied. These fallbacks let the game
workflows be integrated and tested, but they do not close the visual or audio
acceptance gates.

## Rive

Every future Rive asset must contain artboard `Main`, state machine
`Presentation`, and the exact properties, events and states in the matching
`RIVE.md` under
`apps/UNFINISHED-TO INTEGRATE-PARTIAL/game_tree/`.

Falling Blocks is the only game with a final compiled Rive artifact,
`apps/games/01-phaser-arcade/falling-blocks/coach/build/coach.riv`. Its source is
`apps/games/01-phaser-arcade/falling-blocks/coach/scene.rml` and `prepare.py` verifies the
built file.

| Game | Required final asset |
| --- | --- |
| Chess Study | `chess-guide.riv` |
| Garden Defense | `garden-advisor.riv` |
| Lantern Leap | `lantern-hero.riv` |
| Pocket Rally | `rally-dash.riv` |
| Sky Courier | `courier-pilot.riv` |
| Snake Garden | `garden-guide.riv` |
| Solitaire | `solitaire-host.riv` |
| Gravity Pinball | `pinball-marquee.riv` |
| Kinetic Relay | `relay-bell.riv` |
| Marble Works | `marble-gate.riv` |
| Physics Playground | `physics-coach.riv` |
| Sling Targets | `sling-gauge.riv` |
| Stack & Balance | `balance-meter.riv` |
| Tabletop Bot Arena | `bot-crew.riv` |
| Clockwork Room | `clockwork-guide.riv` |
| Crystal Defense | `crystal-command.riv` |
| Drone Circuit | `drone-telemetry.riv` |
| Pocket Golf | `golf-scoreboard.riv` |
| Target Garden | `target-marshal.riv` |
| Orbital Courier | `orbital-console.riv` |
| Clockwork Quest | `quest-faces.riv` |
| Owl Companion | `owl-companion.riv` |
| Reactive Control Desk | `control-desk.riv` |
| Rhythm Garden | `rhythm-flowers.riv` |
| Story Cards | `story-cast.riv` |
| Expression Puppet | `expression-puppet.riv` |
| Memory Garden | `memory-creatures.riv` |

## Other final content

- **Solitaire:** final 52-card face and card-back artwork.
- **Chess Study:** complete board and piece presentation.
- **Rhythm Garden:** three original music tracks with BPM and cue timing plus
  redistribution rights.
- **Story Cards:** final owl/robot artwork, environments and narration.
- **Lantern Leap:** final room backgrounds, tile sets and authored audio.
- **Sling Targets:** final environment artwork and audio.
- **Pocket Golf:** six-hole course art, sounds and level polish.
- **Orbital Courier:** final ship, hazards, docks and spatial audio.
- **Clockwork Quest:** rigged glTF bodies for the explorer and companion with
  idle, walk, turn/talk and reaction clips. Rive covers only faces and dialogue.
- **Memory Garden:** twelve final creature motifs and card-back artwork.
- **All games:** production environment art, effects, UI icons, licensed fonts,
  music and sound effects as needed for a finished release.

For every supplied asset, retain the authoring source, redistribution license,
provenance and content hash. Only final generated/runtime assets belong in Git;
`node_modules`, build directories and test browser/account state do not.
