# Primary references consulted for v0.3.0 (2026-10-21)

The architecture and budgets are design choices, not claims made by these sources.
Pin exact revisions of any adopted library at the implementation-selection gate.

- WebRTC W3C specification: https://www.w3.org/TR/webrtc/
  Peer connections/data channels, Window ownership, optional dedicated-worker data
  channel transfer, message sizing and transport behavior. Do not infer universal
  deployed support from a specification alone.
- WebRTC project, peer connections: https://webrtc.org/getting-started/peer-connections
  Signaling exchange and ICE/STUN/TURN roles.
- TURN, RFC 8656: https://www.rfc-editor.org/rfc/rfc8656.html
  NAT cases requiring a relay; relay is a real continuing resource cost.
- libp2p Kademlia spec: https://github.com/libp2p/specs/blob/master/kad-dht/README.md
  Client/server distinction for restricted peers and bounded query concurrency.
- GossipSub v1.0: https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/gossipsub-v1.0.md
- GossipSub v1.1: https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/gossipsub-v1.1.md
  Sparse topic meshes, peer exchange, scoring, backoff and attack resilience.
  This handoff does not implement or claim conformance with these protocols.
- Chrome Page Lifecycle: https://developer.chrome.com/docs/web-platform/page-lifecycle-api
  Freeze/discard/termination, including unreliable leave events.
- WHATWG Storage: https://storage.spec.whatwg.org/
  Quotas, persistence and local storage lifecycle.
- MLS, RFC 9420: https://www.rfc-editor.org/rfc/rfc9420
  Authentication/delivery separation and reviewed group-key protocol candidate.
- Multicast key management, RFC 2627: https://www.rfc-editor.org/rfc/rfc2627
  Hierarchical key-management context for earlier Titan LKH direction.

Provenance: previous chat retrieval recovered pyramid-hybrid/tier and Titan/Mutt
intent, but no exact complete current tree schema. The examples here are explicitly
new proposed fixtures. The v0.2 ZIPs are the concrete source baseline; existing
source code is preserved except release instructions/integrity tooling. No library
search snippet was treated as proof that networking or v86 had executed.
