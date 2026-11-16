# Preserved isolated-host test source

The parent now owns41 additional historical orchestration test/fixture sources
under `tests/legacy-host-orchestration/isolated-hosting/`. This is a mechanical
history extraction, separate from documentation and any future functional port.
No independently useful application was grouped into a test repository.

| Captured source | New parent location | Files |
|---|---|---:|
| `research/beta-isolated-hosting/tests/` | `tests/legacy-host-orchestration/isolated-hosting/` | 40 |
| `research/beta-opfs-release/native-continuity-fixture.py` | `tests/legacy-host-orchestration/isolated-hosting/historical-inputs/native-continuity-fixture.py` | 1 |

History inspection identified a copy between the native and signed fixtures,
not a rename. Keeping both paths preserves their distinct current identities.
The launch/successor bootstrap and runner paths also remain separate.

A path-limited full-history Git export was streamed into a new independent bare
filter target. The original checkout was hidden, private recovery was read-only,
and networking was disabled. No full monorepo clone, persistent raw export stream,
freshness-check bypass or reference-sharing clone was used. The resulting Git
repository passed integrity checks without alternates or shallow dependencies.

All41 current source bodies and Git modes match the capture and scoped original
index/working bytes; recovery retains the matching filesystem permissions. All52
retained commits match their source-path trees, authors, committers and messages.
All51 historical Python blobs pass syntax and bounded literal/context review.
Every current file restored from the extracted repository in an isolated
namespace with the old workspace and assembly hidden. Commit/path maps and
command exit codes remain in the private phase82 checkpoint.

These old tests have process, network, namespace, service and provisioning side
effects, including possible import-time actions. None was run or registered in
the supported test/build graph. Inputs, authority and interface ports remain
unqualified. Do not treat preservation or old assertions as current acceptance;
read the reference area's execution restrictions before porting a driver.

Tracked-source reconciliation now has1,859 unresolved dispositions. This is a
source-record count, not a missing-file count, whole-project completion percentage
or app-support claim. All124 component pins and runtime code remain unchanged.
