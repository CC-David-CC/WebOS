# Native attachment command transport

Source-only branch `integrate/native-attachment-transport-20261108`, based on
Desktop142a2b0ef. Depends on ACAD's pending C08 Phase B source and runtime
composition; not independently functional or qualified. No build or test run.

Existing `create-source-frame` gains exactly one parent alternative:
`{kind:'native-planar-face',bodyId,featureId,selectionId}`. Null and the original
`{featureId,faceId}` earlier-source-plane alternatives remain. The compact
native request is resolved by Craft from current discovered actual geometry;
no native handles, engine/revision override, indices, guessed constructor,
region, frame or policy are accepted from the caller.

Two commands are added to the same existing synchronous app registration:

| Command | Exact arguments | Shared method |
|---|---|---|
| inspect-source-frame-attachments | revision, bodyId, featureId | inspectSourceFrameAttachments |
| repair-source-frame-parent | revision, index, featureId, faceId, parent | repairSourceFrameParent |

Inspection uses the current authored-journal revision and an actually inspected
body/producer. Repair accepts only the compact native parent above. Existing
registration disposal, captured host session/native signal/current target and
settleScopedCommand are retained. Schemas reject additional fields; own-data
checks and finite bounds remain enforced before shared dispatch. A transport
command never supplies an ownership capability or simulates native discovery.

Root must compose this transport with reviewed ACAD product/runtime source,
refresh exact Worker source pins, build normally, and execute the complete
native attachment/edit/repair/travel/save/freshOpen workflow with independent
post-run artifact analysis. No first success or broader C08 claim is inferred
from command registration. Main site, beta and /desktop remain untouched.
