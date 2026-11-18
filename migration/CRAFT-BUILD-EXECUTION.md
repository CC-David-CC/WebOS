# Craft build execution plan

Decision, 2026-11-17: finish current PdfCraft qualification using its existing
compiler cache. Plan the LAN builder before starting GridCraft/DeckCraft.
No remote source transfer, toolchain installation or build has occurred during
this hardware assessment.

## Measured capacity

Read-only checks used the existing verified `r730` SSH alias, batch mode and
strict host-key checking. No network scan, guessed address, global SSH edit or
service change was needed.

| Machine | CPU | RAM | Available at inspection | Storage / readiness |
|---|---|---|---|---|
| Laptop | i7-8650U, 4 physical cores / 8 hardware threads | about 16 GiB | about 7 GiB | About 54 GiB free; existing pinned SDK and one current compiler cache. |
| R730 | Two Xeon E5-2697 v3, 28 physical cores / 56 threads, 2 NUMA nodes | about 252 GiB | about 195 GiB | About 100 GiB free on the boot SSD; two separate HDD mounts also observed. Rust/Cargo/Node not on inspected PATH; Git, C compiler, Python and bwrap available. |

These are point-in-time observations, not reservations. R730 swap was almost
fully allocated despite ample available RAM; inspect active workload and memory
pressure before benchmarking. Do not clear swap, stop workloads or infer current
thrashing solely from occupied swap. A missing PATH command does not prove no
installation exists anywhere on disk.

Cargo jobs control parallel crate compilations; nightly frontend threads control
parallel work within a crate. LLVM also has backend parallelism. More cores/RAM
allow more concurrent work, but serial dependencies, linking, I/O and older CPU
single-thread performance still matter. Never promise a 7× improvement from
56 versus 8 hardware threads. See the official
[Cargo configuration](https://doc.rust-lang.org/cargo/reference/config.html#buildjobs)
and [Rust parallel frontend explanation](https://blog.rust-lang.org/2026/11/16/enabling-parallel-frontend-on-nightly/).

The existing controlled laptop engine-leaf benchmark found stable median15.675s,
nightly one frontend thread14.632s, four11.634s and eight11.171s. These were warm
dependencies with the leaf rebuilt, not cold full-browser builds. The first
PdfCraft browser graph still took about19 minutes; a cached entrypoint-only edit
was about35 seconds end to end. Compare equivalent workloads.

## Proposed builder setup

1. Verify R730's working directory, ownership, free SSD space, current workloads
   and existing user-local tools. Choose a new private owner-only build root;
   refuse collisions. Keep compilation on SSD where practical. Do not move
   website/account data or provision a production service for this purpose.
2. Use an explicit user-local SDK pinned to the accepted compiler, target,
   Trunk/wasm-bindgen versions and checksums. No global default toolchain changes,
   no unreviewed latest-nightly drift and no copying an entire laptop migration
   directory. The present development compiler is nightly-2026-11-16.
3. Send only reviewed clean commits and required pinned inputs to that builder.
   Inventory tracked content before transfer: do not send secrets, private
   preservation history, account data, browser profiles or unrelated WIP. Do not
   copy laptop compiler target directories. Record verified public/local input
   provenance; keep remote Git publication distinct from a build snapshot.
4. Reuse one dependency download store and bounded current targets. With parallel
   apps, give each its own target/cache namespace and one active Cargo writer;
   a shared mutable target is not a distributed build system. Pin compiler,
   target, profile, lockfile, flags and asset inputs in receipts. Capacity for
   two targets is a later explicit retention decision, not permission to clone
   all historical caches. Keep the existing one-cache laptop policy meanwhile.
5. Build offline after a separate locked dependency/input preparation. Make source
   read-only and the original KSU.CODES unavailable. Use explicit fonts/models/
   translations paths. Never build against the live website directory.
6. Start with Cargo jobs8 and the nightly default frontend2, then measure jobs16
   and frontend4/8 on a representative native check and actual WASM build. Run
   trials sequentially with equivalent warm/cold state; flag changes invalidate
   cache comparisons. Log wall/CPU time, peak process-group RSS, memory pressure,
   disk growth and Cargo timings. Leave capacity for existing host workloads.
   Test-runner concurrency is a separate knob: the present laptop helpers use
   one Rust test thread. Benchmark bounded functional-test parallelism on the
   R730 too; keep GPU/frame-budget/performance probes isolated so contention is
   not mistaken for a product regression. More compiler jobs alone will not
   shorten a deliberately serial test suite.
7. Copy back only the candidate browser artifact, source/input receipt, notices,
   hashes and test results. Verify every payload against its receipt before
   assembly. Native Linux executables may need system-library compatibility
   checks; WASM portability does not prove browser/host integration correctness.
8. Perform actual browser/account workflows and visual review on the laptop/local
   test backend, then separately authorized hosted acceptance. A remote green
   native suite does not replace WebOS qualification.

## Efficient iteration and agent ownership

Use fast native checks and focused regression tests during edits. Once source is
stable, run the app's required gates, build one candidate and qualify the actual
WASM. Preserve passing evidence for byte-identical unaffected payloads; rerun
shared Desktop/Files/Text/WordCraft tests only when changed source/contracts or
new failures justify them. Compiler feature/profile switches and whole-workspace
sweeps can cause avoidable rebuilds; record why they are necessary.

Refresh tracked-file modification times in the verified private snapshot
before compiling against a reused Cargo target. The clean transfer archives
normalize mtimes. An older cached binary can otherwise pass a clean Git tree
check and appear in a new package. The Office builder records the number of
refreshed files and the timestamp, then rechecks the tree before starting the
isolated build. Check both the WASM digest and the browser regression when a
change is supposed to alter behavior in the native engine.

Sub-agents can inspect, implement and review independent app owners after the user
approves that round. They do not make a single compilation faster. The primary
integration owner coordinates shared APIs, cache budgets, test scope and parent
promotion. Parallel read/review work is cheap; two cold compiles on the laptop
would compete for its limited RAM. Use separate verified build hosts or bounded
R730 jobs after setup/benchmark instead of starting unrestricted jobs everywhere.

## Output retention

Compiler caches, targets, candidate sites, browser profiles and package archives
stay outside Git/web roots. Retain one current cache under the existing user
decision; keep only currently needed candidate/package outputs during a round.
After acceptance, remove owned superseded output according to the approved scope,
keeping small command/exit/hash receipts and required pinned source/assets.
Do not delete fonts, models, original/WIP preservation or active rollback assets
under the label "build output". If ownership or reproducibility is uncertain,
classify it first. An interrupted recorder must be recorded as interrupted;
never manufacture an exit code from a passing-looking log.
