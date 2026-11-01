# One document, explicit semantics

No invented `host.files.saveGame` API appears here. Integrator: bind the existing authorized file service after inspecting it. If no suitable service exists, the app can implement ordinary user-selected import and browser download as its document I/O. Choose that boundary explicitly; do not maintain two hidden durable databases and call it synchronization.

## Save envelope proposal

This is an app-owned document format, not a desktop schema:

```json
{
  "format": "ksu.game.save",
  "schemaVersion": 1,
  "appId": "falling-blocks",
  "kind": "logical-snapshot",
  "gameBuild": "integrator-binds-version",
  "contentVersion": "integrator-binds-assets",
  "dependencies": {},
  "payload": {}
}
```

Payload is defined by each game's SAVE.md/spec.json. Never serialize `host`, DOM nodes, cameras from the headset, raw XR anchors, workers, AudioContexts, engine pointers or Rive objects. User placement and device tracking are transient. Optional preferences such as preferred table height are ordinary data, not a saved physical anchor.

## Snapshot versus checkpoint

An exact logical snapshot restores the current logical game at a committed tick. A checkpoint restores a known safe level/phrase/lie. Both are valid, but the Save UI must state which one it writes. In-flight saves for Sky Courier, Lantern Leap, Pocket Rally, Pocket Golf and Rhythm Garden must not pretend to offer exact mid-frame resume. Their own SAVE.md defines the safe point.

**XR transitions do not use file saves.** Even a checkpoint-save game keeps its current live state when entering/exiting immersion. Do not throw away a rolling ball because the exported file format is checkpoint-based.

## Transactional load

Pause and cancel transient input. Read bounded bytes, validate schema/app id/version, parse finite values, caps, ids and invariants. Build the replacement logical state/world off to the side. Commit only after validation and preparation succeed; otherwise retain the original game unchanged and explain the error. Dispose the superseded instance resources only after the successful swap. This preparation does not justify running two simulations.

Check before overwrite against the file service's actual conflict facilities. Do not invent atomic rename, compare-and-swap or locking guarantees. When unavailable, use explicit Save As or a visible conflict choice. Keep document revision separate from game tick.

Suggested import limits to bind/test: 8 MiB for ordinary logical saves, 32 MiB for qualified physics snapshots, bounded entity counts and ghost traces. These are initial budgets, not measured requirements. Reject non-finite numbers, excessive nesting/counts, duplicate ids, unknown assets and executable content.

## Physics snapshots

Rapier's API supports binary world snapshots [S07]. For this handoff they are accepted only with exact tested engine/build fingerprint plus matching logical metadata and stable body/joint ids. This is not a claim of cross-version snapshot compatibility. Never blindly feed arbitrary downloaded bytes into a native/WASM deserializer without size/version validation and failure isolation appropriate to the engine.

Stable app ids are not engine handles. Restore world state, reconstruct id mappings and verify required bodies/joints before committing. Portable build layouts are a different explicit document kind from an exact engine snapshot; no silent conversion between them.

## Evidence

For each game demonstrate mutate → save → mutate further → load → verify actual rules/outcomes. Compare RNG/order/timers/history when relevant. Chess must retain repetition-relevant move history, not only FEN. Test corrupt, wrong-app, oversized and unsupported-version files. Test two windows editing the same destination without silent overwrite.
