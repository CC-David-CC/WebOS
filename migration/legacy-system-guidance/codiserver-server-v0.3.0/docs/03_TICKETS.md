# Implementation tickets v0.3.0

Canonical dependencies: `requires` contains only ticket IDs; `gate_requires` contains only gate IDs.
Original mixed-type v0.2 registry is retained in provenance/v0.2.0/contracts/.

## G00-T01 — Source, authority boundaries and reproducible package / slice 1

Acceptance: G00-01, G00-02, G00-03. Predecessor tickets: none inside gate. Gate predecessors: none.

Implement and prove only these obligations. Do not deploy unrelated components.

## G00-T02 — Source, authority boundaries and reproducible package / slice 2

Acceptance: G00-04, G00-05, G00-06. Predecessor tickets: G00-T01. Gate predecessors: none.

Implement and prove only these obligations. Do not deploy unrelated components.

## W01-T01 — Backend-free anonymous entry and destruction / slice 1

Acceptance: W01-01, W01-02, W01-03. Predecessor tickets: none inside gate. Gate predecessors: G00.

Implement and prove only these obligations. Do not deploy unrelated components.

## W01-T02 — Backend-free anonymous entry and destruction / slice 2

Acceptance: W01-04, W01-05, W01-06. Predecessor tickets: W01-T01. Gate predecessors: G00.

Implement and prove only these obligations. Do not deploy unrelated components.

## W01-T03 — Backend-free anonymous entry and destruction / slice 3

Acceptance: W01-07, W01-08. Predecessor tickets: W01-T02. Gate predecessors: G00.

Implement and prove only these obligations. Do not deploy unrelated components.

## W02-T01 — Real peer transport and signed application packets / slice 1

Acceptance: W02-01, W02-02, W02-03. Predecessor tickets: none inside gate. Gate predecessors: W01.

Implement and prove only these obligations. Do not deploy unrelated components.

## W02-T02 — Real peer transport and signed application packets / slice 2

Acceptance: W02-04, W02-05, W02-06. Predecessor tickets: W02-T01. Gate predecessors: W01.

Implement and prove only these obligations. Do not deploy unrelated components.

## W02-T03 — Real peer transport and signed application packets / slice 3

Acceptance: W02-07, W02-08, W02-09. Predecessor tickets: W02-T02. Gate predecessors: W01.

Implement and prove only these obligations. Do not deploy unrelated components.

## W02-T04 — Real peer transport and signed application packets / slice 4

Acceptance: W02-10. Predecessor tickets: W02-T03. Gate predecessors: W01.

Implement and prove only these obligations. Do not deploy unrelated components.

## W03-T01 — Retained desktop and unified session lifetime / slice 1

Acceptance: W03-01, W03-02, W03-03. Predecessor tickets: none inside gate. Gate predecessors: W01.

Implement and prove only these obligations. Do not deploy unrelated components.

## W03-T02 — Retained desktop and unified session lifetime / slice 2

Acceptance: W03-04, W03-05, W03-06. Predecessor tickets: W03-T01. Gate predecessors: W01.

Implement and prove only these obligations. Do not deploy unrelated components.

## W03-T03 — Retained desktop and unified session lifetime / slice 3

Acceptance: W03-07. Predecessor tickets: W03-T02. Gate predecessors: W01.

Implement and prove only these obligations. Do not deploy unrelated components.

## W04-T01 — Bind and prove the real v86 Linux guest / slice 1

Acceptance: W04-01, W04-02, W04-03. Predecessor tickets: none inside gate. Gate predecessors: G00, W03.

Implement and prove only these obligations. Do not deploy unrelated components.

## W04-T02 — Bind and prove the real v86 Linux guest / slice 2

Acceptance: W04-04, W04-05, W04-06. Predecessor tickets: W04-T01. Gate predecessors: G00, W03.

Implement and prove only these obligations. Do not deploy unrelated components.

## W04-T03 — Bind and prove the real v86 Linux guest / slice 3

Acceptance: W04-07, W04-08, W04-09. Predecessor tickets: W04-T02. Gate predecessors: G00, W03.

Implement and prove only these obligations. Do not deploy unrelated components.

## W04-T04 — Bind and prove the real v86 Linux guest / slice 4

Acceptance: W04-10. Predecessor tickets: W04-T03. Gate predecessors: G00, W03.

Implement and prove only these obligations. Do not deploy unrelated components.

## W05-T01 — Anonymous milestone acceptance / slice 1

Acceptance: W05-01, W05-02, W05-03. Predecessor tickets: none inside gate. Gate predecessors: W02, W03, W04.

Implement and prove only these obligations. Do not deploy unrelated components.

## W05-T02 — Anonymous milestone acceptance / slice 2

Acceptance: W05-04, W05-05, W05-06. Predecessor tickets: W05-T01. Gate predecessors: W02, W03, W04.

Implement and prove only these obligations. Do not deploy unrelated components.

## S00-T01 — Identity protocol and cryptographic reference / slice 1

Acceptance: S00-01, S00-02, S00-03. Predecessor tickets: none inside gate. Gate predecessors: G00.

Implement and prove only these obligations. Do not deploy unrelated components.

## S00-T02 — Identity protocol and cryptographic reference / slice 2

Acceptance: S00-04, S00-05, S00-06. Predecessor tickets: S00-T01. Gate predecessors: G00.

Implement and prove only these obligations. Do not deploy unrelated components.

## S00-T03 — Identity protocol and cryptographic reference / slice 3

Acceptance: S00-07. Predecessor tickets: S00-T02. Gate predecessors: G00.

Implement and prove only these obligations. Do not deploy unrelated components.

## S01-T01 — Minimal local registration service / slice 1

Acceptance: S01-01, S01-02, S01-03. Predecessor tickets: none inside gate. Gate predecessors: S00.

Implement and prove only these obligations. Do not deploy unrelated components.

## S01-T02 — Minimal local registration service / slice 2

Acceptance: S01-04, S01-05, S01-06. Predecessor tickets: S01-T01. Gate predecessors: S00.

Implement and prove only these obligations. Do not deploy unrelated components.

## S01-T03 — Minimal local registration service / slice 3

Acceptance: S01-07, S01-08. Predecessor tickets: S01-T02. Gate predecessors: S00.

Implement and prove only these obligations. Do not deploy unrelated components.

## S02-T01 — Session lifecycle, bounds and failures / slice 1

Acceptance: S02-01, S02-02, S02-03. Predecessor tickets: none inside gate. Gate predecessors: S01.

Implement and prove only these obligations. Do not deploy unrelated components.

## S02-T02 — Session lifecycle, bounds and failures / slice 2

Acceptance: S02-04, S02-05, S02-06. Predecessor tickets: S02-T01. Gate predecessors: S01.

Implement and prove only these obligations. Do not deploy unrelated components.

## S02-T03 — Session lifecycle, bounds and failures / slice 3

Acceptance: S02-07, S02-08, S02-09. Predecessor tickets: S02-T02. Gate predecessors: S01.

Implement and prove only these obligations. Do not deploy unrelated components.

## I01-T01 — Connected browsers, not just cross-runtime unit tests / slice 1

Acceptance: I01-01, I01-02, I01-03. Predecessor tickets: none inside gate. Gate predecessors: S02, W02.

Implement and prove only these obligations. Do not deploy unrelated components.

## I01-T02 — Connected browsers, not just cross-runtime unit tests / slice 2

Acceptance: I01-04, I01-05, I01-06. Predecessor tickets: I01-T01. Gate predecessors: S02, W02.

Implement and prove only these obligations. Do not deploy unrelated components.

## I01-T03 — Connected browsers, not just cross-runtime unit tests / slice 3

Acceptance: I01-07, I01-08. Predecessor tickets: I01-T02. Gate predecessors: S02, W02.

Implement and prove only these obligations. Do not deploy unrelated components.

## S03-T01 — Deployment design and static-resource boundary / slice 1

Acceptance: S03-01, S03-02, S03-03. Predecessor tickets: none inside gate. Gate predecessors: S02.

Implement and prove only these obligations. Do not deploy unrelated components.

## S03-T02 — Deployment design and static-resource boundary / slice 2

Acceptance: S03-04, S03-05, S03-06. Predecessor tickets: S03-T01. Gate predecessors: S02.

Implement and prove only these obligations. Do not deploy unrelated components.

## S04-T01 — Explicitly authorized public deployment / slice 1

Acceptance: S04-01, S04-02, S04-03. Predecessor tickets: none inside gate. Gate predecessors: I01, S03.

Implement and prove only these obligations. Do not deploy unrelated components.

## S04-T02 — Explicitly authorized public deployment / slice 2

Acceptance: S04-04, S04-05, S04-06. Predecessor tickets: S04-T01. Gate predecessors: I01, S03.

Implement and prove only these obligations. Do not deploy unrelated components.

## S04-T03 — Explicitly authorized public deployment / slice 3

Acceptance: S04-07. Predecessor tickets: S04-T02. Gate predecessors: I01, S03.

Implement and prove only these obligations. Do not deploy unrelated components.

## P01-T01 — Real Internet peer availability / slice 1

Acceptance: P01-01, P01-02, P01-03. Predecessor tickets: none inside gate. Gate predecessors: W02.

Implement and prove only these obligations. Do not deploy unrelated components.

## P01-T02 — Real Internet peer availability / slice 2

Acceptance: P01-04, P01-05. Predecessor tickets: P01-T01. Gate predecessors: W02.

Implement and prove only these obligations. Do not deploy unrelated components.

## H01-T01 — Owner-only real host files, read-only first / slice 1

Acceptance: H01-01, H01-02, H01-03. Predecessor tickets: none inside gate. Gate predecessors: S04.

Implement and prove only these obligations. Do not deploy unrelated components.

## H01-T02 — Owner-only real host files, read-only first / slice 2

Acceptance: H01-04, H01-05, H01-06. Predecessor tickets: H01-T01. Gate predecessors: S04.

Implement and prove only these obligations. Do not deploy unrelated components.

## H01-T03 — Owner-only real host files, read-only first / slice 3

Acceptance: H01-07. Predecessor tickets: H01-T02. Gate predecessors: S04.

Implement and prove only these obligations. Do not deploy unrelated components.

## H02-T01 — Explicit host writes after read-only correctness / slice 1

Acceptance: H02-01, H02-02, H02-03. Predecessor tickets: none inside gate. Gate predecessors: H01.

Implement and prove only these obligations. Do not deploy unrelated components.

## H02-T02 — Explicit host writes after read-only correctness / slice 2

Acceptance: H02-04, H02-05. Predecessor tickets: H02-T01. Gate predecessors: H01.

Implement and prove only these obligations. Do not deploy unrelated components.

## M00-T01 — Bind the new domain and preserve existing evidence / slice 1

Acceptance: M00-01, M00-02, M00-03. Predecessor tickets: none inside gate. Gate predecessors: G00.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M00-T02 — Bind the new domain and preserve existing evidence / slice 2

Acceptance: M00-04, M00-05, M00-06. Predecessor tickets: M00-T01. Gate predecessors: G00.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M01-T01 — Tree nodes with their own explicitly subscribed chats / slice 1

Acceptance: M01-01, M01-02, M01-03. Predecessor tickets: none inside gate. Gate predecessors: M00.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M01-T02 — Tree nodes with their own explicitly subscribed chats / slice 2

Acceptance: M01-04, M01-05, M01-06. Predecessor tickets: M01-T01. Gate predecessors: M00.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M02-T01 — One bounded pool of physical peer connections / slice 1

Acceptance: M02-01, M02-02, M02-03. Predecessor tickets: none inside gate. Gate predecessors: M01, W02.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M02-T02 — One bounded pool of physical peer connections / slice 2

Acceptance: M02-04, M02-05, M02-06. Predecessor tickets: M02-T01. Gate predecessors: M01, W02.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M03-T01 — Origin-authenticated routed events for public groups / slice 1

Acceptance: M03-01, M03-02, M03-03. Predecessor tickets: none inside gate. Gate predecessors: M02.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M03-T02 — Origin-authenticated routed events for public groups / slice 2

Acceptance: M03-04, M03-05, M03-06. Predecessor tickets: M03-T01. Gate predecessors: M02.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M04-T01 — Delegated rendezvous without expanding the login service / slice 1

Acceptance: M04-01, M04-02, M04-03. Predecessor tickets: none inside gate. Gate predecessors: M03, S00.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M04-T02 — Delegated rendezvous without expanding the login service / slice 2

Acceptance: M04-04, M04-05, M04-06. Predecessor tickets: M04-T01. Gate predecessors: M03, S00.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M05-T01 — Reviewed private-group admission and rekey lifecycle / slice 1

Acceptance: M05-01, M05-02, M05-03. Predecessor tickets: none inside gate. Gate predecessors: M03.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M05-T02 — Reviewed private-group admission and rekey lifecycle / slice 2

Acceptance: M05-04, M05-05, M05-06. Predecessor tickets: M05-T01. Gate predecessors: M03.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M06-T01 — Verified local caches and explicit retention / slice 1

Acceptance: M06-01, M06-02, M06-03. Predecessor tickets: none inside gate. Gate predecessors: M03.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M06-T02 — Verified local caches and explicit retention / slice 2

Acceptance: M06-04, M06-05, M06-06. Predecessor tickets: M06-T01. Gate predecessors: M03.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M07-T01 — Sharded routing, cell split/merge and migration / slice 1

Acceptance: M07-01, M07-02, M07-03. Predecessor tickets: none inside gate. Gate predecessors: M04.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M07-T02 — Sharded routing, cell split/merge and migration / slice 2

Acceptance: M07-04, M07-05, M07-06. Predecessor tickets: M07-T01. Gate predecessors: M04.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M08-T01 — Games and app-scoped group capabilities / slice 1

Acceptance: M08-01, M08-02, M08-03. Predecessor tickets: none inside gate. Gate predecessors: M03.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M08-T02 — Games and app-scoped group capabilities / slice 2

Acceptance: M08-04, M08-05, M08-06. Predecessor tickets: M08-T01. Gate predecessors: M03.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M09-T01 — NAT, suspension, partitions and malicious peers / slice 1

Acceptance: M09-01, M09-02, M09-03. Predecessor tickets: none inside gate. Gate predecessors: M04, M05, P01.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M09-T02 — NAT, suspension, partitions and malicious peers / slice 2

Acceptance: M09-04, M09-05, M09-06. Predecessor tickets: M09-T01. Gate predecessors: M04, M05, P01.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M10-T01 — Measured load ladder and ten-billion-device accounting / slice 1

Acceptance: M10-01, M10-02, M10-03. Predecessor tickets: none inside gate. Gate predecessors: M06, M07, M08, M09.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M10-T02 — Measured load ladder and ten-billion-device accounting / slice 2

Acceptance: M10-04, M10-05, M10-06. Predecessor tickets: M10-T01. Gate predecessors: M06, M07, M08, M09.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M11-T01 — Explicitly approved staged public operation / slice 1

Acceptance: M11-01, M11-02, M11-03. Predecessor tickets: none inside gate. Gate predecessors: M10, S04.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

## M11-T02 — Explicitly approved staged public operation / slice 2

Acceptance: M11-04, M11-05, M11-06. Predecessor tickets: M11-T01. Gate predecessors: M10, S04.

Implement only these obligations in the existing worktree. Keep authentication/v86 baseline intact; no deployment side effect.

