# ArcCAD ideas for the unified jSketcher desktop

The user wants useful ArcCAD ideas carried into the unified jSketcher, with a
minimal phone interface, a comfortable 1080p workspace and effective use of 4K.
They want iterative review based on actual use, not a static checklist. The
source reference inspected on 2026-11-02 is Pesicp/ArcCAD `4669ab90497f5f383127c79f8daae29936204894`,
backed up on box-git as `reference/arccad-20261102`. It is a divergent fork of
jSketcher; an entire-branch replacement would discard unrelated webOS,
geometry, history and storage work. Its README is a feature guide, not proof
that every feature works or is suitable for our host. Preserve contributors and
review applicable source/third-party terms when adapting code.

Carry these areas forward and record actual current behavior, source chosen,
validation, and limitations for each. Do not assume an item is missing or done
until it has been checked in our combined branch.

- **Workspace and navigation:** adjustable toolbar sizing and themes;
  contextual controls; collapsible scene, history, projects, objects and
  constraints; draggable or resizable panels; a navigation cube, camera and
  pan/zoom controls. On phone prioritize the canvas, selection and essential
  commands, with advanced actions reachable. On large displays allow useful
  panels side by side and ensure fullscreen windows respond to resizing.
- **Modeling:** move, rotate, split, measure, direct push/pull and sketch on a
  chosen face. Keep existing OCCT features and the native mesh workflow,
  communicate incompatible operands, validate geometry and preserve model
  references through history and save/reopen. Direct XYZ move and OCC axis
  rotation have focused Chromium tests; neither has complete feature coverage.
  ArcCAD's older split implementation documented limits; test rather than
  assume it safely handles every result.
- **Sketching:** grid and snap controls, persistent tools, cancel behavior,
  angle and dimension hints, editable constraints, grouped rectangles, trim
  previews and object visibility. Coordinate input must work with pointer,
  keyboard and touch, preserve undo and never silently damage existing sketches.
- **Files and outputs:** use My files for projects and supported DXF, STEP and
  STL flows. Test actual open/edit/save/reopen with real accounts and separate
  upload. Geometry previews and exports are not proof of manufacturing safety.
- **Technical quality:** selection priority, coordinate handling, snapping,
  tessellation, window/worker cleanup, no hidden vendor accounts and correct
  failure messages. Avoid silent fallback that could omit model geometry.

For every carried feature test the specific behavior on desktop and phone-sized
layouts, plus 4K where useful, including independent windows, undo/redo,
account isolation, sync, close and reopen. Record physical-phone, complex-model,
license/provenance and live-site limitations separately. The current research
candidate is not yet the live ksu.codes application and must retain the existing
production CSP rather than weakening it.
