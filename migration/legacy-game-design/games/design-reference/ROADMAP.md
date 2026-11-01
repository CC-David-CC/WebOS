# Delivery waves — finish small games, not 28 placeholders

## Gate 0: integration and one asset

Inspect actual desktop contract and bind files/focus/build. Pin engine/runtime versions. Author one original Rive asset and prove canvas-to-engine texture + input mapping. Record phone and Galaxy XR runtime features. No production registry changes until an app actually runs.

## Wave 1: four lighthouse apps

**Falling Blocks** proves a complete Phaser loop and phone controls. **Physics Playground** proves one Three/Rapier world across window and XR. **Clockwork Room** proves Babylon's authored scene/interaction/XR flow. **Owl Companion** proves Rive-first state and lifecycle. Each is small but complete before promoting its pattern.

## Wave 2: breadth without new infrastructure

Add Snake Garden, Chess Study, Solitaire Table and Sky Courier; Marble Works and Stack & Balance; Crystal Defense and Drone Circuit; Reactive Control Desk, Story Cards and Expression Puppet. Every app gets its own instance state and original asset brief. Shared code extraction is permitted only after a real repeated boundary is proven.

## Wave 3: deeper engine capabilities

Add Lantern Leap's Rive-rendered hero, Garden Defense and Pocket Rally; Kinetic Relay, Sling Targets and Gravity Pinball; Pocket Golf, Target Garden and Orbital Courier; Rhythm Garden and Memory Garden. Qualify high-speed contacts, physics scheduling, dynamic textures and audio-clock timing rather than broadening content prematurely.

## Wave 4: capstones

Tabletop Bot Arena combines small-robot physics, bounded AI, contacts and a match loop. Clockwork Quest combines authored environments, glTF animation and Rive face/dialogue integration. These should reuse understanding from earlier apps, not introduce a new desktop framework.

## Per-app implementation ladder

Rules/model and pure tests → desktop game loop → phone controls → Rive assets/composition → save/load and errors → XR (where required) → sound/accessibility/polish → lifecycle/performance/device evidence. Some work overlaps, but no app skips the final gates because its title screen is attractive.

No time estimates or promise that all 28 are cheap. The catalog is a deliberate product tree; completion is tracked per app in `spec.json` and actual evidence. Network multiplayer, online rankings, user scripting and large open worlds are out of scope.
