# v0.3 P2P extension — controlling instructions

Read README, shared/MESH_ARCHITECTURE.md, MESH_WIRE.md, MESH_SUPPORT_SERVICES.md,
docs/08_P2P_V03_DECISIONS.md, the combined acceptance registry and evidence/STATUS.
The old AGENTS contract below still governs permissions and baseline code. Where
scope expands (multi-group/discovery/caches), follow the explicitly staged new plan.

The user asks to assume identity/v86 available; do not rewrite those working
subsystems. Bind real workspace evidence. No internet-scale deployment is assumed.
Implement one ticket at a time. Current next ticket: M00-T01. Every new browser app
uses one session-owned network pool; no per-feature independent P2P stack.

Private routed messaging must not be enabled until the reviewed crypto profile
gate passes. The pure model has no crypto/network authority. Never promote its
results into live browser, WAN, malicious-peer-resilience or scale evidence.

The 'server' handoff now plans delegated stewardship separately from codiauth.
It does not authorize exposing a port, adding a system service, installing packages
or connecting to David's machines. Native ISO/Surface work remains out of scope.

---

# Agent contract — server package

Work in the user's existing CodiServer worktree when available, otherwise in an
extracted workspace copy. Inspect first; do not overwrite unrelated work.
The previous native ISO/Surface/Xfce controller is a different project. Preserve
its sources, builds, host settings, logs and device state. box-webhost is a target
name supplied by David, not evidence of a reachable SSH session or authorization
to expose a service.

1. Read README, shared/PROTOCOL.md, the build/test ladder, and evidence/STATUS.md.
2. Select one bounded ticket whose predecessors are evidenced. Do not require a
   login daemon to work on the default browser ANON path.
3. State the invariant, add the failing acceptance case, make the smallest
   coherent change, run the target tests and regressions, record actual output.
4. A fake terminal, local echo, BroadcastChannel exchange or a crypto unit test
   does not prove v86 boot, WebRTC messaging or Internet NAT traversal.
5. Do not erase failed/blocked evidence or change required tests merely to pass.
   Record planned, passed, failed, blocked and not-applicable distinctly.
6. No CDN, npm framework, remote code injection, hidden network service, Docker,
   home-grown crypto, username-based owner privilege, or unvalidated official
   badge. Keep one session model and one peer packet format.
7. Browser code cannot hold the authority signing key. Certificates are public
   evidence of identity, never host-files authorization. Never expose secrets
   to the VM, peer, UI debug dump, logs, URL or public asset directory.
8. Preserve expired/invalid/offline distinctions. Never silently downgrade a
   failed official session into a guest. Local development is explicit and never
   a production escape hatch.

Allowed within the selected workspace: read/edit project files, git diff/status,
run tests in disposable state directories, generate fixtures without real keys,
start loopback-only temporary test servers, inspect known v86 assets read-only.
Require explicit authorization: package installation on the user's host, sudo,
opening ports, public network service setup, DNS/TLS/firewall changes, persistent
systemd changes, broad filesystem grants, destructive Git, privileged guest-image
builds, or writes outside the project. This handoff itself grants none of those.

Report what ran and where. Keep manual terminal transcripts, browser version,
selected RTC candidate type and evidence IDs. Do not report an entire gate passed
because one illustrative test passed. If a design invariant fails, correct the
abstraction rather than accumulating flags, fallback identities or parallel APIs.
