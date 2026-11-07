# V3 drawing persistence host component

Source4347211b9 from Desktop35918d0d4. Paired Core custody source87ddaf9b9 +
1a3988fef and codec54472a8b4 are required before application integration. No
drawing publication/menu/UI, real filesystem/browser save or Native geometry
qualification is claimed by this packet.

Actual index.mjs supportedEnvelope accepts drawing-free v2 and v3 with exactly
one canonical-mm/version1 definition. It returns the complete envelope unchanged;
the existing normal Save outcome/coordinator/association handling serializes it.
The actual readonly dirty serializer includes complete current drawing metadata,
materials and optional inch presentation. Missing metadata access on an older
runtime fails closed for a v3 baseline. Full drawing schema validation remains
inside the Core validation Worker; this host does not implement another schema
or resolve source/native references.

Seven new host controls plus70 retained native-Save settlement/disposal controls
pass. They extract the actual host functions and use the real coordinator and
public Save adapter with explicitly synthetic manager/storage/metadata receipts.
Successful storage receipts are protocol doubles, NOT native CAD or real My
files writes. Complete v3 serialized bytes/baseline/dirty state and rejected
malformed envelopes are checked; acknowledged-write failure handling is unchanged.

before-key-order/ preserves the first synthetic fixture failure: it appended
material/display keys AFTER drawings, unlike the actual codec's canonical order.
Only that baseline construction was corrected to match the real codec; product
comparison logic and assertions were unchanged. Full initial source/log retained.
Final source-pinned77 PASS is under evidence-r1/. No product file changed during
the proof. No generated runtime, account/session/private service data is included.

```sh
/tmp/codi-files-move-node/bin/node --test test/agent-cad-corpus/drawing-persistence/host.test.mjs test/agent-cad-corpus/native-save-outcomes/regressions.test.mjs test/agent-cad-corpus/native-save-outcomes/dispose.test.mjs
```

Root must compose host and Core custody before a real signed native Save/fresh
Open proof. Linked reference realization/dimensions/export, drawing edits and
shared-journal publication remain separate work. Full Gate1 remains unfinished.
