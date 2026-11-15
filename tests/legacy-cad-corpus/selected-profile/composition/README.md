# Existing mechanical workflows on the selected-profile runtime

Scoped result: **PASS** on CAD `a0b363bce15e8533be17c9332b46a7e51ddeea5d`,
desktop `478970d72f5af22ea8315b03ca20265e8303319f`, app `8ae3ddc83e706829761c66ddc573fae42f9d746171ee09c1ee3b0f0744d98965`.

| Actual check | Result |
|---|---|
| Existing five-hole bracket create/edit/refuse/undo/redo/Save/sync/reopen | PASS |
| Typed bracket and real Parameters UI/agent/persistence/Close control | PASS |
| Public enclosure, material UI, configurations/rebind, native persistence and File/3MF export | PASS |
| Independent initial and edited 3MF ZIP/XML geometry/group/material oracle | PASS both files |
| Exact driver reuse and unchanged independent checker | PASS |

This bounded regression reuses the three established signed drivers from
`../../combined-alias-mechanical/` on the immutable r4/20406 fixture documented
in the parent directory. Each driver creates fresh synthetic accounts. Product
source, prior tests, public authoring paths and assertions remain unchanged.

Only import depth, the current mandatory runtime-pin helper, a provenance
comment, and the enclosure receipt's desktop-source label were adapted.
`verify-driver-reuse.py` checks that exact transformation against the existing
drivers and byte equality of the independent 3MF checker. It does not reinterpret
or omit any assertion.

The bracket driver exercises the genuine public five-hole plate, dimensional
propagation from100×50×20 to150×30 with35mm depth, hole offsets, refusals,
authored undo/redo, native Save/sync, account denial and fresh Files reopen.
The typed variant adds real Parameters UI, agent parameter commands, dimensional
validation, exact travel and its inherited pre-execution task-suppression Close
control. That old control is not presented as a held successful Worker reply;
the parent selected-profile receipt separately proves genuine-success disposal.

The enclosure driver uses public V2 creation, the actual material dialog, shared
agent material operations, typed bindings/configurations, explicit material
rebind, native persistence and visible File/Export3MF with the themed host prompt.
It requires separately arrangeable BODY and grouped LID/LABEL:2 print objects,
3 material regions. It rejects stale assignments, invalid tokens, overwrites,
and unsupported exports without creating the refused output file.

`check-v2-3mf.py` is unchanged from the independent CAD ZIP/XML oracle, SHA256
`74e350b7163d030b40d381fd3d617aa54906bfc4aa031920ede022dddded625a`.
It checks units, grouping, materials, bounds, oriented volume, closed mesh edges,
84 triangles and the paired920mm² lid/label interface for both initial and
width120 edited exports. Native projects preserve editable design intent;
3MFs are derived manufacturing handoffs.

Run the three drivers sequentially with the parent's mandatory exact source and
all four runtime hash variables, loopback fixture/CDP and a new CODI_RECEIPT per
driver. The enclosure run also requires an isolated CODI_OUTPUT_DIR. Then run:

```sh
python3 -B test/agent-cad-corpus/selected-profile/composition/verify-driver-reuse.py
python3 -B test/agent-cad-corpus/selected-profile/composition/check-v2-3mf.py "$CODI_OUTPUT_DIR/initial.3mf" "$CODI_OUTPUT_DIR/edited.3mf"
```

Own contexts are closed and shared Chromium is disconnected, never terminated.
Do not replace the retained fixture or copy any account state. Source/receipt
pins and raw logs are recorded alongside these drivers. Generated binary 3MFs
remain outside Git. This checks the existing mechanical milestone against the
new transport/adapter integration; it does not qualify new selected-profile
3MF support, the whole CAD1 matrix, or any public deployment.

No failures occurred in these composition runs. Raw receipts/logs are retained
here and at `/mnt/data10tb/codi-selected-profile-signed-evidence-20261106`.
Synthetic binary outputs are retained there under `composition-outputs/` and
locally under `/tmp/codi-selected-profile-composition-20261106`; their SHA256
pins are recorded without committing the binaries.
