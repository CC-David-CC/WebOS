# Frozen source silos

All work below is preserved separately. Do not merge branches wholesale merely because their handoffs exist. Review actual changed shared files, source rosters and prerequisites. Individual complete flows may be qualified while later work on the same branch remains unqualified.

| Repo / branch | Frozen tip | Disposition / restart note |
|---|---|---|
| ACAD `feature/arc-length-20261110` | `02786baf981e42c28d697bd5805b0866d11ea278` | Ordinary integrated R8 flow qualified separately; branch handoff `docs/handoffs/ARC-LENGTH-SILO-HANDOFF-20261110.md` |
| Desktop `feature/arc-length-20261110` | `c8a4304fd59ebf96ed5623d0648829891295f910` | Host silo handoff; avoid replaying integrated changes |
| ACAD `feature/typed-measurement-role-20261110` | `e730a756d817dacff7c3da0eb335edfb9279a5fd` | Source reviewed, unmerged; TYPED-MEASUREMENT-SILO-HANDOFF |
| Desktop `feature/typed-measurement-role-20261110` | `84526d1fc7009a1adaf90cfef1847d49427b0cfc` | Matching Host adapter; TYPED-MEASUREMENT-HOST-SILO-HANDOFF |
| ACAD `test/typed-measurement-role-whole-20261110` | `74f67208006fcd96a58a80df959c4b49ce7304ce` | No acceptance drafted; only WIP handoff/checkpoint |
| ACAD `tooling/projection-after-wrapper-20261110` | `3953e11c4813d3c13719976249bc56b09a57b1ce` | Original checker unchanged; integrated exact R8 proof is in main integration; PROJECTION-AFTER-SILO-HANDOFF |
| ACAD `test/drawing-composed-queue-20261110` | `31890327abe4924a86052195f91ce399a808e233` | D5 source WIP, unreviewed corrections, unexecuted/unqualified; D5-DRAWING-SILO-HANDOFF |
| ACAD `fix/saved-content-unicode-padding-20261110` | `f952104edb43f2ba3bb8adbf3741fc040348f859` | Corrected fixture already integrated/qualified in exact R8 scope; DIRTY-TRACKING-AGENT-HANDOFF |
| ACAD `feature/c06-principal-plane-split-20261110` | `57077c52a8769146662249e6dffefd58c220f42d` | Source draft only; not integrated, compiled or tested. Commit text and C06 reconciliation document record boundaries |

Other owned dirty-tracking tips: ACAD `c2df7793`, Desktop `5c4cd6c0a`, and prior typed product originals ACAD `351199b3`/`7436db1f5b5d129e7ed51da846d84a67bbb28492`, Host `3e5608acf83e989c77bc18601af7549ceb8d01f8`. Current frozen refs are retained in all-ref backups, so use exact branches and inspect ancestry rather than guessing cherry-picks.

## Remaining contract-sensitive implementation

Typed measurements must preserve existing resolveQuantity length owner/name bindings, not flatten typed values to numbers or delete source parameters during demotion. Integrate strict Arc IO/history plus `measurementLengthBinding.mjs` and `measurementRoleTravel.mjs` into actual consumer/source rosters before a coherent build. Complete acceptance still needs writing.

D5 composes an oblique 6/8→9/12 triangle and 10→15 hypotenuse, explicit label collision/repair and travel, five native cycles, six actual SVGs and rendered images. Initial packet e8694948 plus correction fc56f250 needs independent review. check.py SVG root/group schema, source admission and renderer self-identity corrections must align with docs/reader. D1–D4 earlier scoped proofs do not qualify this changed layout planner.

Split requires one atomic multi-output operation. Use privately owned Native Common/Cut with authentic private cutting tools, source immutable, separate negative/positive side identities and two result ancestry indexes. A public intermediate Boolean invents phantom feature lineage and is unsuitable. Update shared Worker/ledger/history/replay/UI-agent paths for two outputs; bound tool+two-result allocations and triangle/lifetime budgets. Preserve regions/materials/grouping; splitting must not silently turn aligned material regions into independently arranged print objects. No new native compile has been proven necessary, but actual compatible cohort behavior must be tested.

## Parallelism

Independent source lanes: typed roles, D5 drawings, C06 finite operations, and isolated resource measurement design. One integrator owns common command registry, history/replay, source manifests, coherent Core/Host builds and the checkpoint ledger. Never allow concurrent writers in one worktree/shared file. Build/stage/pins and real browser whole workflows run serially. Qualify complete affected workflows, not every edit.

## Unrelated workspace WIP

The older SIMPLIFIED checkout has uncommitted folder-move/guest-policy/circuit work and tests. The parent checkout has hardware notes and 272 rough game source/spec files. Private `local-audit/{parent,simplified}-wip/` preserves a binary tracked patch, untracked source archive and manifest. These are UNREVIEWED backups, not CAD changes or deployable source. Nested repos and node_modules are excluded from the parent untracked archive and preserved via their own Git/runtime backups. Derived pycache files need not be kept. No private account/key/browser state is bundled. Do not overwrite these source trees with another checkout.
