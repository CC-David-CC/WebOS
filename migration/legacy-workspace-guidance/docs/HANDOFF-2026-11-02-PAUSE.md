# WebOS development handoff — 2026-11-02

The user requested a pause. The full WebOS goal remains unfinished. Resume only
on request; do not treat the research branch as a deployable release.

## Live

- `https://ksu.codes/` returned HTTP 200 at handoff. Latest verified static
  release is `0965a0cbdd022f588061cdc23e10eb6b18fa5977cc3f6a05569439eaf11d2020`.
- File-service HTTP error classification, the G-code session-context guard,
  Calculator pending-close guard, and Excalidraw chooser guard were deployed
  and had scoped live account smoke tests. They do not solve all session races.
- Notebook browser-local Python working files have a confirmed stale-handle
  overwrite risk in an isolated copy of the live bundle. Avoid opening the same
  working file in two notebook windows. Use Notebook's **File → Save working
  file to My files** for a backup; this cannot recover an overwritten version.
- The live My files Blob path materializes whole files. The efficient capture,
  changed-chunk synchronization and RAM-only notebook candidates are not live.
- The live desktop has an unsaved-work risk when logout completes while another
  app is being edited. Do not claim the Calculator close guard fixes logout.

## Where work is

- Combined research branch: `research/webos-cad-combined-20261102`, checkout
  `/tmp/codi-webos-cad-merge`, starting handoff head `b285d55eb`. Backed up to
  box-git-distro and R730. This includes unfinished work; do not deploy it whole.
- Main `SIMPLIFIED` checkout is `simplified` at `c78b40341` with pre-existing
  modified and untracked files. Do not reset, stash, delete, or overwrite them.
- Full long-term checklist: `docs/WEBOS-COMPLETE-PROGRAM-CHECKLIST.md` in
  `/home/dflanag3/codi-app-worktrees/program-handoff`.
- Notebook research: `research/notebook-committed-data` and
  `research/notebook-reconciliation-20261102`; version checks work in tested
  modern clients, but old writers can bypass them and legacy ABA can lose an
  intermediate version. Large-file memory, migration and normal operations
  remain unqualified. Unsaved notebook edits/output may be lost; already saved
  data must not be silently overwritten.
- Gateway contained-worker research: `research/gateway-native-contained-20261102`
  at `e93a52772`; independent review `research/gateway-native-independent-review-20261102`
  at `332825648`. Protected local candidate is under
  `/srv/codi-gateway-contained-research-20261102`; it is not installed live.
  Signed 104 MiB test passed, but full snapshot memory remained high. Protected
  staging, managed upgrade, interruption and rollback qualification remain.
- Versioned mirror/offline cache research: `research/calculator-versioned-live-20261102`
  at `35a05ea04`. The current bootstrap can unregister the service worker and
  delete public caches when worker and manifest identities disagree. Mixed old
  tabs, retained assets, controlled rollout and rollback remain unresolved.
- In isolated tests the current offline shell's query-bearing bootstrap bypasses
  the cache. An exact-alias prototype is incomplete; offline login is not
  available and must not be claimed.
- Shared account-transition research retains a known logout race in the live
  shell. See `research/session-transition-review/README.md` and
  `research/session-boundary-correction-20261102`; candidate is not deployed.

## Next steps

1. Recheck live pins and available space; select isolated worktrees. Do not
   deploy all research as a batch. Preserve current static/gateway rollback.
2. Resolve saved notebook working-file conflicts and migration with real old
   clients, durable data preservation, account isolation and bounded workers.
3. Finish efficient browser/server file handling with bounded memory, real
   version checks and crash recovery. Qualify 128 MiB and slow/concurrent users;
   128 MiB capture tests kept the UI responsive but sampled browser RSS was
   roughly 1.3–1.8 GiB. Sliced reads are not a hard memory bound.
4. Design versioned static assets/service-worker migration and safe rollback;
   prove mixed old/new tabs and offline behavior before changing the live route.
5. Continue app-by-app My files, lifecycle, touch and signed-account tests.
   Keep unimplemented simulation features and hardware validation honest.

Workstation `/` had about 6.1 GiB free at handoff. Large builds belong on R730;
clean only identified disposable artifacts. The live service's last confirmed
smokes used temporary accounts and receipt-bound cleanup. Three subagents were
terminal at pause; no active task was intentionally left running.
