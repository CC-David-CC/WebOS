# Folder moves: design and verification needed

Folder move and rename remain unavailable in Files. The current account mirror
and gateway support version-checked **file** moves, not directories: a folder's
local version does not establish that its descendants are unchanged, and the
existing two-path journal and lost-response recovery describe a single file.
Copying a tree and then deleting its source is not a safe substitute.

A complete implementation needs coordinated browser and gateway work:

1. Handle local-only trees in a single browser-storage transaction. For synced
   trees, reject destinations inside the source, occupied destinations, and
   subtrees with pending changes, conflicts or moves until they are resolved.
2. Define a bounded, canonical manifest of relative paths, types and file
   hashes. Under the account mutation lock, validate the tree and destination,
   reject symlinks, perform a no-replace directory rename, and sync the parent
   directories. Decide how to handle out-of-band writes on the host: they do
   not obey the gateway lock and must not be assumed impossible.
3. Journal the operation and all affected browser rows atomically, block
   conflicting subtree writes, and recover after interruption or a lost reply.
   Use a durable operation receipt or equivalent idempotency mechanism so an
   unrelated identical destination cannot be mistaken for our own move. On an
   ambiguous result, preserve both sides and ask for resolution.
4. Expose folder Move and Rename only after the protocol is supported, with
   understandable pending and conflict states on desktop and touch layouts.

Tests must cover nested and empty folders, local-only/offline work, collisions,
self-descendant moves, pending and conflicting children, multiple accounts and
tabs, out-of-band edits, interruption before and after server rename, lost
responses, restart and idempotence, symlink/path escape, authorization and a
bounded large tree. Existing file-move checks do not establish folder safety.

## Server-only experimental primitive

The source now contains an **unrouted, unreleased** server experiment:
`gateway_service.folder_manifest` and `UserStore.folder_manifest` /
`UserStore.move_folder`. They are not callable through the public gateway and
Files still cannot move folders. A manifest excludes the root and orders
relative paths by Unicode code point; entries contain a path, directory flag,
and a SHA-256 for files. Its digest is SHA-256 over compact UTF-8 JSON with
sorted object keys and unescaped Unicode. The current bound is 4,096 entries,
128 MiB of file data, 16 path components, and existing gateway path limits.
These are experimental bounds, not a chosen product limit: aggregate folder
size needs a scalable, bounded-memory design before rollout so ordinary
folders containing multiple large files are not arbitrarily excluded.
The move validates the destination depth, subtree manifest, ownership and
private modes, authorizes read/list/rename, holds the existing storage lock,
uses no-follow descriptors and no-replace rename, and fsyncs both parents.

A full-synchronous SQLite prepared/done receipt is scoped by account and
operation UUID. A random 32-byte `user.codiserver.folder_move` directory xattr
is fsynced before the prepared receipt; recovery requires the same marker,
directory device/inode and manifest. A completed receipt can be retried without
performing another rename. A matching marker left after receipt completion is
cleaned when the folder is next moved. The marker does not appear in normal
Files listings or manifest entries. Existing or unresolved markers block a new
move without being overwritten. Filesystems lacking user xattrs fail before
rename. `tests/folder-move-server-test.py` exercises process exits at preparation,
rename and commit, no-replace conflicts, account permissions, marker collisions,
a backup copy with a different inode, path/depth bounds and symlink rejection.

This is **not release-ready**. The gateway lock covers gateway mutations only;
direct host writers must be quiesced because metadata checks cannot establish
an atomic snapshot against arbitrary concurrent host writes. A crash after the
marker is fsynced but before its receipt commits leaves an orphan marker; it
fails closed and currently needs an operator recovery procedure. A prepared
move whose source changes, whose marker is missing, or whose destination is
ambiguous likewise preserves data but needs an explicit cancellation or recovery
workflow. Backup/restore must retain both the permission database and the user
filesystem including xattrs, and restore them consistently; a backup that strips
xattrs or changes inodes cannot automatically prove a prepared move succeeded.
The implementation conservatively rejects such recovery instead of adopting a
possibly unrelated destination. Recovery of a full machine snapshot, host power
loss durability, unsupported deployment filesystems, browser tree journaling,
signed HTTP capability, cancellation, upgrades/rollback, and cross-device
convergence remain unverified. Receipts currently have a per-account bound of
10,000 with no retention/compaction policy; resolving that bound is required
before rollout. Do not enable the route or UI until these invariants and the
rest of this design are implemented and reviewed together.
