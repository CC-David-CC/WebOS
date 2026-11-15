> v0.3 note: this document describes the preserved v0.2 baseline.
> For planned multi-group work and intentional changes, read
> `08_P2P_V03_DECISIONS.md` and `../shared/MESH_ARCHITECTURE.md`.

# Supersession of the v0.1 handoff

The prior 53-case acceptance registry is retained verbatim under
provenance/v0.1-acceptance.json as HISTORICAL INPUT, not current authority and
not a record of passed tests. Its IDs overlap the new registry; always qualify
historical IDs with v0.1. Only contracts/acceptance.json defines v0.2 obligations.

The retained desktop geometry/source remains the starting point. Existing
scripts inside public/desktop/scripts are historical integration material;
review their paths/privileges before use. They are not the current test runner
and no legacy script has been run against the user's workstation here.

Changes in authority and scope:

- Static browser execution, anonymous RAM-only lifetime, real v86 proof and the
  future actual-host-files requirement remain; the new W01/W03/W04/W05 and
  H01/H02 gates make their evidence boundaries explicit.
- Browser-only password accounts and encrypted local account storage are
  superseded, not silently half-implemented. A second authoritative username
  database would create conflicts with the official server namespace. SIGNIN
  now requires the real service; local development uses unvalidated ANON.
- Connected ANON is not an exception: it calls the same real authority, gets a
  random temporary identity and a short-lived certificate bound to its key.
- S00/S01/S02/I01 replace the local-account crypto/restore gates with server
  registration, key possession, expiry, password verification and independent
  browser-session contracts. Account persistence is server-side; guest state is
  still ephemeral. No automatic migration promotes local names to server users.
- W02 adds actual WebRTC transport with signed manual signaling and packets.
  P01 separately proves real Internet connectivity; source or same-machine tests
  cannot stand in for that proof.
- Every old fake terminal demonstration remains disallowed as guest evidence.
  The old desktop's fabricated Linux answers are replaced by a console launcher.
- Source font binaries are omitted and system font fallbacks retained. The
  original archive hashes establish provenance without redistributing them.

The two new archives are distinct work scopes, not alternative implementations.
Their shared protocol, schemas and public fixtures are byte-identical. Change
that contract deliberately in both packages and test interoperability before
changing either side's wire behavior.
