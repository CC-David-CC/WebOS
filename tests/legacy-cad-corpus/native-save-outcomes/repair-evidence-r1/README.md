# Native Save settlement repair — component PASS

Source 5c4fa703a. All 181 combined tests pass: 70 native-Save/cleanup regressions
plus 111 retained export, STEP, coordinator, registry and command controls.
Frozen before observations remain: original 53 tests had 10 PASS and 43 FAIL.
All original assertions remain. Additional controls cover falsey watcher faults,
idempotent release and disposal continuing after unsubscribe failure.

Save shares no-write/pending/acknowledged settlement with exports. Validate own
data receipt fields before path/version/baseline publication; never invoke
receipt/error accessors. Preserve exact primary cause including falsey values.
Known browser acknowledgement survives later association/notice/finish/lifetime
failure. Submitted writes without valid acknowledgement remain uncertain.
Never infer server synchronization or retry automatically. Local-write admission
is rechecked before storage invocation. No added large buffers or hashing.

Watcher custody is retained before activation and removed only after successful
unsubscribe. Activation failure cannot lose the old watcher. A provider that
repeatedly throws is NOT proved released. Disposal reports unconfirmed release
and continues retiring frames/timers. Successful release is idempotent.

Actual host functions, real coordinator/public command adapter; synthetic manager,
storage and throwing providers. Not browser, Native or real persistence proof.
Fresh signed Save/server-byte/freshOpen proof is next. No filesystem race,
forced Close, account probe or deployment. First disposal fixture syntax error
and run are retained under ../fixture-syntax-before; assertions unchanged.
