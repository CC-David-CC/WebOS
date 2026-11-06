# Through-hole desktop host command boundary

**PASS12 new groups +27 retained edge/profile adapter groups**. These are mock
host/window/account protocol tests only. No geometry, genuine Worker, browser,
Craft publication/replay, save/sync, or public app qualification is claimed.

The new `registerThroughHoleCommands(host,context)` registers:

| Command | Craft method |
|---|---|
|inspect-through-holes|inspectWorkerThroughHoles|
|create-through-hole|createWorkerThroughHole|
|inspect-through-hole-history|inspectWorkerThroughHoleHistory|
|edit-through-hole|editWorkerThroughHole|

Create common fields are revision/version1/unitmillimeter/engineocc/
engineRevision/bodyId/sourceFeatureId/kind/diameter. Four-corner creation adds
both offsetX/Y; centered creation forbids them. Schemas require the common
fields and advertise optional offsets; callbacks enforce the exact kind union.
Edit admits exactly revision/index/featureId/diameter or that set plus both
offsets. It cannot change kind/source. The core validates the actual inspected
feature kind; the host does not guess from numeric feature IDs.

Every numeric dimension is a primitive finite positive millimeter value≤1e6.
IDs are bounded, runtime revision is explicit, getters/extra/native-handle/source
face fields refuse without evaluation, and forwarded argument/options records
are detached and frozen. No IDs are allocated and no fallback, auto-save,
geometry reconstruction or caller-authored history is introduced.

The lifetime wrapper is the unchanged existing settleScopedCommand. Core errors
and already-known committed outcomes propagate exactly. Pending cancellation
may have unknown outcome; the bridge never promises rollback or blindly retries.
Tests cover session/window/realm/signal loss, late inert replies, abort listener
cleanup, post-inspection ownership, partial-registration cleanup and idempotent
unregistration. Actual frame/session/geometry lifetime proof remains separate.

Run:

```sh
node --test test/agent-cad-corpus/through-hole-host/commands.test.mjs
node --test tests/jsketcher-edge-treatment-commands.test.mjs tests/jsketcher-selected-profile-commands.test.mjs
```

Both first executions passed. Source and output hashes are retained in evidence/.
Only the new adapter and this directory change; the parent owns index.mjs
registration, CAD implementation, builds and later actual signed qualification.
