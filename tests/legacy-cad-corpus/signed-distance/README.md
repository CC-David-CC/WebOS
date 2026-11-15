# Signed sketch-distance qualification — scoped PASS

Root combined R11 (CAD607b1ea42) now repeats the full same public signed workflow on20395, with authenticated served-byte pins matching app88d65535 / sketch9fa5dd2f / project134e945d. See [combined R11 receipt](signed-r11-receipt.json). This joins the plane-display optimization and signed-distance change on one tested host runtime. Prior r2 scope below remains its original proof; no public deployment or complete gate claim.

The actual public host route passed in a new isolated signed fixture20394 with
desktop `c30887c8e` (approved adapter `aaeea00623`) and CAD runtime `e1e7839e7`.
Exact app, Worker, host-bundle/catalog and file hashes, observed rows and limits
are in [signed-r2-receipt.json](signed-r2-receipt.json). This closes one bounded
mechanical command slice, not the whole CAD1/Gate1 matrix. The older active-editor
`sketch-signed-distance` route is unchanged and is not qualified by this result.

The request is exactly `{revision,faceId,axis,ids,distance}`. Axis is `x`, `y` or
`projected`; X/Y take two inspected point IDs, projection adds a live segment ID.
Distance is finite numeric sketch millimeters within ±1e6. Directed semantics:
B.x−A.x, B.y−A.y, and `dot(B−A, segment.B−segment.A)/length(segment.B−segment.A)`.
Success carries dimension `{axis,typeId,objects,distance,status}` plus the common
journal receipt. Repeating the same axis/ordered IDs/value deliberately adds a
redundant native constraint: `changed:true`, `status:'redundant'`, authored undo.
Unchanged geometry therefore does not imply an operation no-op.

The bounded control creates ordinary geometry entirely through public plane
and primitive commands, discovers real IDs via `inspect-closed-sketch`, and uses no
formula/native seeds. It independently measures directed signs, zero and
reversed cases, XZ sketch-local axes, point/segment-endpoint/circle-center targets,
live datum changes, rejection, authored travel, normal Save/sync/account denial,
fresh Files open and genuine held-response lifetime cancellation. All passed.

The live-datum test installs projection first, then constrains the datum
segment's endpoint X displacement to 0 and Y displacement to 10. The measured pair
still satisfies its original projection against that now-vertical live datum.
A three-point contradictory X-offset cycle supplies a genuine conflict without
assuming whether an existing dimension can be replaced. An unchanged point edit
supplies a true no-op control; repeated dimension insertion remains an authored
redundancy control. The two datum edits undo/redo to exact native snapshots.

Negative controls include stale revisions, missing/wrong-type/cross-face IDs,
wrong direction type, arity, axis, numeric type and public bound. They preserve
the previous native document and inspected geometry; only opaque inspector and
journal revision tokens may refresh after a failed replay. No-op and stale
refusal compare the complete captured state. Native Save retains dimension types
and ordered object IDs; a fresh Files reopen retains exact native sketch bytes.

Lifecycle tests retain a successful result produced by the actual Worker task
`sketch-transition-signed-distance`. Normal File → Open holds its real unsaved
confirmation until the host lifetime cancels the pending command, then Keep
editing preserves the accepted design. The original late event is released
untouched and remains inert; the next ordinary public operation succeeds.
Visible Close also cancels a held candidate and leaves the saved file unchanged.
No second-command implicit-preemption or public AbortSignal behavior is claimed.

Run against a fresh loopback signed fixture with matching reviewed runtime:

```sh
CODI_TEST_URL=http://127.0.0.1:20394/ \
CODI_TEST_CDP=http://127.0.0.1:19329/ \
node test/agent-cad-corpus/signed-distance/signed.test.mjs
node --test tests/jsketcher-closed-sketch-commands.test.mjs
```

The six adapter controls pass separately. `helpers.mjs` reuses the existing
numeric-expression lane's generic signed login/Files helpers; its hash is in the
receipt. Other captures in this lane are passive test-only read oracles.

Visible geometry UI equivalence, every solver/DOF case, generated/reference
objects, all stages and large-scale behavior remain separate qualifications.
Genuine Worker delay controls retain/release actual responses; no fake successful
reply, private geometry-authoring path or callback/source injection is allowed.
Prior fixtures, Files qualification and public sites stay unchanged. The test
uses own synthetic accounts, closes only its contexts and disconnects from the
shared browser. Account DBs/keys, dependencies and runtime output are not Git
artifacts. Existing qualified numeric/DXF receipts retain their original pins;
this new command result does not retroactively retest those full scopes.
