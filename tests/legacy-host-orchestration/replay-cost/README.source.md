# Measured saved32 full-history replay cost

**Audit only; no cache or product change.** On exact served CAD`594cc042b1482482c2afe600302de1265d023d46`/desktop`d63369feca4919ac8877efaf1b01509b57fe6e26`, one genuine Open of the already saved32-sweep project and one five-point read-only query passed. The original file stayed byte-exact SHA`62747420b840c230cdb3b6eb29b552b5eb3c4045cf9455d087d226d5f7292529`. No Save, authoring, account creation, fixture restart, Worker replacement, request interception or private model seed occurred. Existing account login and ephemeral Open were expressly authorized. Original full capacity R2 remains FAIL; its separate Open repair proof is unchanged.

| Actual command | Sketch Worker starts/retired | Semantic starts/retired | Native sweep starts/retired | Other | Observed command time |
|---|---:|---:|---:|---|---:|
| Saved32 Open |128/128|64/64|1/1|1 project validator, retired|44,685ms|
| Native point query32 |128/128|64/64|1/1|none observed|41,642ms|

These are **observed counts**, not32× extrapolations. Worker URLs are pinned actual assets. Each one-shot client's source corroborates the task attribution; request bodies were not intercepted. Solver median observed lifetimes were265ms(Open)/261ms(query); semantic medians67ms/66ms. A Worker lifetime includes startup/import/message/compute/teardown and CDP delivery overhead; it is not solver CPU time. Native Worker lifetime overlaps the other Workers; do not sum it with their lifetimes or infer proportional speedup. No cold-cache, other-machine, memory, phone or universal performance claim.

The sampler read only actual owned CAD frames, including the hidden staging frame during Open, every500ms. Per-frame sampled maxima were owners1/candidate1/mount1 during Open and owners2/candidate1/mount1/detached1 during query; cleanup failure stayed false. Short accepted-phase transitions can fall between samples, so sampled accepted0 does not mean no publication occurred. Open's old/new frames have distinct resource pools; these maxima are not a global RAM/owner census. All measured Workers returned to the retained guest-Worker baseline. Final readback found0 owned20937 targets after normal owned-context closure; shared Chrome/root fixture remained alive.

Public source discovery and detached source inspections used to construct the query oracle ran **outside** its measured interval. Pin preflight can warm cache. No initial source generation or signed-account/network cost is represented as replay-only work.

## Source-bound explanation

`source-pins.json` records exact Git objects/hashes at the served core commit; line references below refer to that commit, not mutable root HEAD.

- `craftBundle.ts:1071,1080,1133` creates one private owner/registry for a full start-to-tip replay and calls every saved operation in order. Here the actual file contains2 PLANE entries and32 separate sweep intents sharing the same2 actual source faces.
- `workerSelectedSweep.operation.ts:67,83,86` captures source/service/history/generation/frame/namespace/stream guards before awaiting. At92 it runs two independent Worker reconstructions of each source, comparing source/digest/evidence. At96 it runs two independent semantic preparations and compares complete signatures. Each of the32 features takes that same path; the observed128/64 starts match it.
- `headless/client.ts:87,94,99` and `prismSemanticClient.ts:23,27,31` hold their respective exclusive Web Lock across one new dedicated Worker/job and terminate it before resolving. The observation does not split import/startup cost from mathematical work.
- `solidLedger.mjs:88` reuses one native mount through the candidate owner. The32 features create distinct authored/native results in that mount. There are **not32 native-engine Workers per replay**. Do not deduplicate those distinct native outputs or their feature IDs/ownership/budget merely because this fixture's geometry repeats.
- `evaluationResources.mjs:50,61,66,90` owns native mounts and closes/detaches them. Open accepts then detaches native resources (`craftBundle.ts:1218,1244`). A point query constructs a new private full replay and closes its owner in finally before returning (`craftBundle.ts:1175,1197`). It does not borrow accepted retired handles.
- `workerSolidPointCommands.ts:39,41,47` retains the60s read deadline, immutable source inventory and captured operation/currentness fences. `solidLedger.mjs:194,203` binds the reconstructed output and compares validity/single-solid/exact native volume+six bounds against the accepted measured target before classifying. Every query in this audit passed five genuine native classes and exact before/after source/history/counters/journal/material/presentation/revisions/epoch/resource preservation.
- Publication checks remain live and cumulative (`evaluationResources.mjs:40`, operation:101). The source shows repeated guard traversal; this audit did **not** instrument/count those function invocations or attribute wall time to them. Their cost is an unmeasured follow-up, not an inferred percentage.

## Smallest proposed dedup slice — unimplemented

Store only a **verified pair of solved-source data** per distinct current source in one evaluation owner. On a first miss, still run2 actual independent Workers for that source and compare all existing source/digest/evidence checks. Later features in the *same candidate* may consume that bounded immutable verified pair if the complete captured key and all live guards still match. Keep both genuine semantic preparations per feature, all native operations/results, per-feature source bindings, publication checks, exact engine/build admission and full read-only replay.

Suggested key and lifetime:

1. A private owner-identity scope; never global, document-only, accepted-model or persistent storage. Within it, use actual candidate face identity plus face ID, namespace/document generation/epoch, source exact raw bytes, exact boundary and frame snapshots, untyped native task/version/options, solver URL+byte pin, empty external-parameter contract and captured expression/service/stream identities+versions. Hashes may index; exact bounded data/identity equality must corroborate a hit. No guessed region/curve parsing or UUID schema change.
2. A hit must call `owner.requireCurrent()` and the current source/service/history/frame/version predicate before **and after** consuming the result. A changed/stale source is a refusal, not a hit or repair. Reuse post-admission detached frozen data, not an old Worker envelope relabeled with a new revision, mutable `ReadSketch`/MSketch/model objects, live native handles or source writes.
3. Coalesce an in-flight same-key request only within that owner; the first miss still obtains two separate real Worker reconstructions. Remove failed/cancelled entries. Clear the owner map on abort/close/detach, refuse reuse after candidate lifetime, and create a fresh proof pair for a new Open/query/Undo/Redo candidate. An accepted detached owner can remain retained: weak-keying alone is insufficient cleanup.
4. Bound retained entries/bytes explicitly. An optional cache hitting its own cap should fall back to the unchanged independently solved path, preserving the existing project's admission limits. No additional rejection of formerly supported projects, giant duplicated history snapshot or new format framework.

For this actual two-source fixture, an implementation regression target would be4 solve Worker starts per candidate (2 independent reconstructions×2 distinct source inputs), with64 genuine semantic preparations and1 native Worker still required. That target is **unimplemented and unmeasured**, not a promised latency reduction. Whole-preparation caching is deferred: its signature includes the per-feature preparation revision, region ID, path references/direction, both source digests/frames and transport. Rewriting that envelope or skipping its second proof would weaken the current contract. Typed sources, other operations/builds and cross-candidate caching are outside this proposed slice.

Required regressions before any product adoption:

- Unchanged signed sweep four-case oracle/history/Save/Open and saved32 Open/query proofs; exact native/source/IDs/byte preservation; actual observed Worker counts distinguish paired proof from copying one reply twice.
- Two source faces with equal raw data remain separately bound; changed source/frame/boundary/namespace/epoch/services/stream versions cannot hit. Changed region/path order/reversal still receives fresh independent semantic validation.
- Cancellation while pending, failed/mismatched second Worker, cleanup failure, stale delivery and rejected native continuation never publish/reuse an entry; healthy subsequent candidate obtains fresh independent proofs.
- A retained result cannot be mutated to affect later features. Optional cache-cap fallback preserves uncached behavior/limits. A new candidate performs fresh solves; accepted/native resources and query baseline/cleanup remain unchanged.
- Existing typed/unsupported/old-build refusals remain explicit; no main-thread solver, native result aliasing, ordinal/handle exposure, weaker source publication guard or alternate model.

## Evidence/reproduction

`evidence-r1/receipt.json` contains raw lifecycle timestamps, per-URL counts, resource samples, full source/body/engine pins and actual oracle state. `independent-check.json` rechecks counts, retirement, saved native bytes/32 intents/output metrics and five native classes against actual saved source. `cleanup.json` records owned-target retirement. Runtime/profile/account state is not archived. `run.mjs`/`observe.mjs` were frozen at`28816742f` before execution; hashes remained exact.

Use the same root-owned fixture and prepared test account only with current root authorization. Env contract matches the repair runner (`CODI_TEST_URL`,CDP,pins,expected core/desktop,evidence,Puppeteer). Run `node test/full-history-replay-cost/run.mjs`; offline check is `node test/full-history-replay-cost/check.mjs evidence/receipt.json`. No product edits are included in this branch.
