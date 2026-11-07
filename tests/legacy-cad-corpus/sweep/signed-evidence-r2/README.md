R2 actual signed run FAIL, retained unchanged. Source141631288 on the same
9c6dc2eb2/50ffd4e69 runtime/private20934; only approved prior runner-baseline
correction. Straight disk and annulus complete PASS, including three Save/Open
checkpoints each, source/path UndoRedo and all refusals. Forward actual quarter
Arc baseline creation/creation UndoRedo/Save/server sync/fresh Open and independent
saved-source native volume/bounds PASS. Forward profile width edit accepted.
Path-radius edit setup then refused to guess missing discovered point IDs:
inspect-closed-sketch exposes the actual Arc object but points:[]; expected three
real endpoint/center IDs found zero. This is a missing shared inspection/edit
workflow, not a native geometry failure. See the final saved row pathInspection.

Root source readback: closedSketchInspection.ts filters native point discovery
to Point/Segment/Circle; coordinateTransition.ts nativePoint and actual parent
admission also exclude Arc. renderSketchProjection.mjs already has Arc handles.
No product edit or private ID/source workaround was applied. Reverse quarter and
RC01 were not executed in this run. Owned context closed; shared browser/root
fixture retained. Native point classification remains unqualified.
