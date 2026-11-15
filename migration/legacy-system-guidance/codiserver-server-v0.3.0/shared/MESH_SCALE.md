# Ten-billion-device design envelope and falsification plan

## Scope

Population N is addressable devices, not guaranteed simultaneous online browsers.
Let A=N×online_fraction. Login requests, initial asset bootstrap and authority
renewal capacity are outside this P2P model at the user's request; that is not an
assertion that those have no cost. P2P rendezvous, topology maintenance, retained
objects and relay bytes remain IN scope even when no server saves chat history.

### Required complexity boundaries

| Operation | Required dependency |
|---|---|
| Ordinary browser resident network state | Its bounded hot memberships, neighbors, queues and retained data |
| Discovery | Capped lookup in sharded steward directory; no enumeration of N |
| One room event | Actual receivers and bounded redundancy; not unrelated rooms |
| Root namespace update | Interested cached descriptor holders, amortized pull/caches |
| Lease maintenance | Active memberships and replica factor, partitioned across stewards |
| Blob delivery | Bytes actually consumed; peer distribution shifts who pays, not total |
| Key change | Chosen group's membership and chosen key protocol; not all devices |

A sparse neighbor graph has bounded degree, not automatically good paths, Byzantine
resilience or high availability. Production must prove connectivity/recovery under
its real membership algorithm. The included graph model is an idealized centralized
construction, not a distributed discovery implementation or a deployment benchmark.

## Explicit accounting equations

Let g be hot memberships per online device, C the cell target, r routing-record
replicas, b bytes per routing record, T seconds between renewals, q relay fraction,
u average per-device offered P2P bits/sec, K measured supported connection slots
per support process, U usable egress fraction and B bits/sec per relay link.

```
active_memberships = A * g
minimum_full_cells = ceil(A * g / C)        # balanced ideal, not hot-key prediction
routing_record_bytes = A * g * r * b        # aggregate, excludes indexes/overhead
renewal_bytes_per_second = A * g * r * b / T
relay_egress_bits_per_second = A * q * u    # given offered-send-rate convention
relay_hosts_by_bandwidth >= ceil(relay_egress / (B * U))
```

Receive-side ingress for those relayed bytes is of similar magnitude; don't double
count it as egress, but do budget both directions and framing/encryption overhead.
K and u must be measured; for A browser sockets each with s support links, connection
slot lower bound is A×s/K, independent of how little payload is saved. A single local
process can fulfill several roles at small scale but not evade its aggregate caps.

In a room of R subscribers, one B-byte broadcast needs at least (R-1)×B bytes at
recipients besides the source. Gossip redundancy, retries and headers add to it.
Every extra recipient still consumes bandwidth. R=10^10 and B=1024 is roughly
10.24 TB for ONE delivery to everyone, before overhead. It is not logarithmic total
work merely because the fan-out tree has logarithmic depth.

## Reference scenarios (not benchmarks)

`python3 shared/capacity.py` produces arithmetic for N=10^10 with 1% online and with
100% online, g=2, C=256, r=3, b=256 bytes, T=120 sec, q=0.10 and u=64,000 bit/sec.
The deliberately simple b excludes certificates, hash indexes, allocator overhead
and databases. These values are inputs for sensitivity analysis, not predictions
of real usage or a hardware purchase recommendation. Vary online fraction, churn,
relay fraction, record size and upload consent before provisioning.

At 1% online: 100 million browsers, 200 million hot memberships, at least 781,250
full cells, 153.6 GB of replicated record payload, 10.24 Gbit/sec of aggregate
renewal payload and 640 Gbit/sec of relay egress under these assumptions. At 100%
online those quantities are 100× larger (except rounding). This is distributed
work; putting it on one box contradicts the scaling design.

## Churn is workload

A peer disappearing causes expiry, neighbor repair and possibly missing-history
work. Test churn as a rate and as correlated loss (whole operator/LAN/region), not
just uniform independent dropout. Reconnect with exponential backoff + jitter and
bounded candidate work. Track control bytes and signature attempts per successful
join. Old hints must not trigger unlimited retry storms. Never assume every browser
uploads enough to fund all its requested downloads; constrained clients may be
net consumers, which must be covered by willing peers/providers or denied capacity.

## What counts as evidence

1. Unit/model invariants: allocations, queue/replay bounds, ID stability, negative
   admission, numeric accounting. These prove only the named pure functions.
2. Real browsers: distinct processes/profiles, actual RTCStats, byte captures,
   candidate types, CPU/memory and UI latency. BroadcastChannel is not WebRTC proof.
3. Network faults: LAN/WAN, NAT/relay-only, suspension, sleep, partition, packet
   reorder and reconnect. Explicit evidence per topology.
4. Load: real small deployments plus event simulations at stated sizes; measure
   delivered denominator, missing items, p50/p95/p99 latency, control/total bytes,
   queues, retries, peer counts, GC and peak memory. No cherry-picked success paths.
5. Extrapolation: state measured range, workload distribution and unsupported
   assumptions. Never label analytical N=10^10 arithmetic as a 10^10-device test.

Avoid absolute 'eventually under arbitrary churn' promises: delivery requires some
connected honest path, available data holders and adequate capacity before expiry.
Within those declared assumptions, define and test bounded repair and visible loss.
The earlier willingness to tolerate about eleven metadata hops is a preference,
not a proven maximum routing diameter or permission to delay games by eleven hops.
