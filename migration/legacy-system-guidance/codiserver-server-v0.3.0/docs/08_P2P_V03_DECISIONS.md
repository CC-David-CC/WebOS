# Design changes and consequences — v0.3.0

1. **Tree is not physical wiring.** Per-node rooms and tiers remain; unrelated
   traffic no longer goes through the root. Costs: an explicit routing directory
   and independent stable IDs. Benefit: local failure/load does not recurse globally.
2. **One pooled multi-room runtime.** Per-window peer objects are replaced when
   implemented, not kept as a parallel group engine. Apps share budgets, not state.
3. **Origin event vs transport frame.** v0.2 link-bound packets cannot be forwarded
   as-is. The new draft is explicitly versioned; existing crypto/identity is not
   silently reinterpreted. Runtime migration is a gate, not completed in this ZIP.
4. **Automatic discovery is a support service.** The account server remains small,
   but scoped stewards provide signaling/leases; direct NAT failures may need TURN.
   These are honest new roles, possibly co-located initially, not hidden login APIs.
5. **Partition key changes freeze.** The earlier LKH/TGDH automatic canonical-room
   failover idea is not retained as a transparent fallback. One reviewed key profile
   per room; new autonomous partition groups get new IDs. This trades some membership
   availability for coherent revocation/epochs. Private-profile selection is unresolved.
6. **Few saved files != zero infrastructure.** Leases may be memory-only while
   consuming sockets/CPU/bandwidth. Durable history requires an explicit holder.
7. **Ten billion is an envelope, not a benchmark.** Bounded edge work and sharded
   aggregate capacity remove the global-list bottleneck. Actual global deployment
   also requires enough honest connected resources; a few owned machines cannot
   promise unlimited retention/relay for billions of concurrent clients.
8. **No implicit persistence expansion.** ANON stays ephemeral; persistent public
   cache and private retained data each require explicit consent. No device globally
   synchronizes every membership, cache, user or parent-node transcript.

Pure anonymous can mean server-certified temporary identities with no permanent
accounts, exactly as in the previous connected ANON flow. Self-signed local test
identity remains a distinct explicitly unvalidated deployment, never automatic
fallback when an official certificate is stale or rejected.

The old docs under 01/04/05/06 describe the preserved executable baseline. The new
shared MESH_* specifications and this decision record govern planned multi-group
work. The runtime source has not already implemented those new behaviors.
