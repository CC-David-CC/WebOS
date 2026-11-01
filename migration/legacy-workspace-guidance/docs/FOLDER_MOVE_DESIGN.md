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
