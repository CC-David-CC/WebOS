# One authored CAD workflow for people and agents

This implements the current functional gate; it does not replace the unchanged
Files/CAD release objective with API discovery.

## Required acceptance path

1. Discover supported operations and current document/model/constraint IDs.
2. Create a dimensioned rectangle, extrude a plate and create five holes.
3. Inspect authored dimensions, IDs and measurable results.
4. Edit original rectangle width/height, extrusion depth and hole spacing.
5. Reject an impossible edit with the prior accepted document intact.
6. Undo the authored edit and redo it, restoring values and dependencies.
7. Save the inspected revision to My files through the common file operation.
8. Close and reopen through Files in a fresh signed session; verify intent and
   geometry, and verify another account cannot access the saved file.

The acceptance run uses supported commands for authoring and saving. Tests may
observe internal state to independently verify results. Private helpers must
not perform a missing authoring step and then qualify the entire agent path.
No AI provider is required.

## Common transaction boundary

UI and agent adapters submit the same typed operation to the document
coordinator. It names stable authored targets and an inspected revision, not
arbitrary history, callbacks or worker handles. The coordinator validates units,
domains, account/window lifetime and source revision, computes on private
worker candidates, checks the result and publishes only a current valid result.
Accepted source changes, sketch bytes and derived geometry must agree at
publication. Rejection/cancellation must leave no temporary live writes or
partly accepted changes.

Original-sketch edits need a candidate-only sketch read view during dependent
replay, then coordinated workspace/geometry publication. Temporarily changing
the live sketch and attempting rollback is insufficient. Keep geometry
validity, constraint satisfaction, region topology, kernel failures and broken
dependencies distinguishable.

Save uses the existing desktop file operation. Inspection tokens must also
change for material/appearance and surfacing edits; obtaining a token must not
hash/copy the entire project. Browser save and verified server synchronization
are distinct. Conflicts and uncertain writes follow existing Files recovery;
never retry a possibly committed write blindly.

## Undo is not a feature cursor

Feature-history rollback changes how much of the graph is evaluated and remains
useful. Authored undo reverses a completed change: after extrusion 20 → 35, undo
restores 20 while retaining the extrusion; redo restores 35. The same applies to
rectangle dimensions, hole spacing and materials. Moving the cursor before
the extrusion removes its result and does not satisfy this test.

Use a shared bounded authoring journal/transaction path with small reversible
intent changes, not copies of derived meshes or native handles. Failed changes
must not consume accepted journal entries. Inverse replay, sketch bytes, model
and journal cursor must be published together after validation.

## Current evidence and gaps

- Exact CAD d6253ea9 / desktop a5717a702 passed the complete bounded signed
  command-only bracket workflow, repeated independently by the integration
  lead. The test authors only through supported commands and checks native
  intent, measured BREP geometry, save/sync, another-account denial and fresh
  Files reopen. See tests/jsketcher-agent-bracket-signed-20261105.md.
- Visible 3D authored Undo/Redo menu/key actions are integrated through CAD
  24d52ae8. Actual menu/keyboard, editor focus, busy worker and contained error
  controls pass; owner and root repeated the signed bracket using real menu
  travel and fresh Files reopen. A synchronous update-observer reset also
  rejects stale work, drains processing and accepts a fresh operation.
  HistoryBackward/Forward still navigate the separate feature cursor. See
  tests/jsketcher-authored-menu-signed-20261105.md.
- Rectangle, worker extrusion, centered/four-corner hole creation and enclosure
  assignment commands have scoped browser evidence.
- The ordinary signed bracket passes model/file acceptance, but its private
  sketch/history edits do not prove the complete supported agent path.
- Full-tip depth editing now retains descendants and has actual-browser authored
  undo/redo evidence. Hole editing and its wizard share that path on source
  ef676d45; see CAD test/webos/README-authored-edit-history.md. Earlier rewound
  extrusion-only tests remain historical, not the current implementation.
- Host Save and cheap complete-document revision pass focused/type checks and
  a rebuilt strict-CSP signed account gate: occupied filename, material/surface
  stale tokens, changed file version, exact local/server bytes and fresh Files
  reopen. See tests/jsketcher-agent-save-signed-20261104.md. Default validator
  builds now force prepared numeric; root independently checked the actual
  default-built worker under strict CSP using the same saved native bytes.
- Original rectangle dimensions have actual host desktop/emulated-phone command
  and Edit-menu evidence. The combined sketch/depth/hole journal is integrated
  as d6253ea9 after actual worker fault checks and the signed gate above.
  Cancellation now reports AbortError while preserving accepted state. Same-size
  no-ops preserve the journal; cache autosaves do not stale the dialog. These
  bounded passes do not qualify all sketch types or material/parameter undo.
- Multi-window close/in-flight cancellation and repeated worker cleanup have
  bounded passes. An intermittent second-window startup timeout is unexplained;
  later passing runs do not establish a fix.

See CAD-FUNCTIONAL-GATES.md and the current handoff for ownership and commits.
No new live activation is claimed. Packaging follows functional qualification.
