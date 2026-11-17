# WordCraft document integration

Status: 2026-11-17 — local qualification passed; static rollout and hosted
qualification pending. This is not yet a claim about the served ksu.codes release.

The change integrates the real native WordCraft editor with the existing
Desktop, account Storage and Files. Unsaved rich documents have account-scoped
browser-local recovery; confirmed Save/Save As updates native identity, titles
and restoration; Files and WordCraft Open activate the same live document.
Different documents remain independent. Requested Discord controls are removed
from File, title bar and Help; About retains its link. Desktop styling, beta,
backend/account state and the original workspace remain unchanged.

| Selected component | Commit |
|---|---|
| WordCraft | `fbc4bb73fbc177c9adcfbb705c9a9a05212a7ae9` |
| Desktop | `1e0a94ffcfc54fd06fd1b2b958377303d48fdf82` |
| Runtime | `a54e08dc80fd132911a2bd679f1cd16caea43f2b` |
| Text | `0c34b0e1c36881963d4bdf98e282dab1df56785f` |

The parent release receipt will record its source commit, every selected source
component and file hash. WordCraft's accepted local fork branch points at the
qualified commit; its upstream-tracking main remains separate. No external Git
publication has occurred.

| Gate | Result |
|---|---|
| All nine native CI stages | PASS, including 4,989 tests; eight pre-existing ignored |
| Fresh complete offline source-pinned browser engine | PASS, 27 files, 92,652,321 bytes; development profile |
| JavaScript tests | PASS, 68; synthetic engine explicitly distinguished |
| Actual local browser document workflows | PASS, 19 |
| Actual local rich recovery/session boundaries | PASS, 15 |
| Actual local profile/recent/font isolation | PASS, five |
| Local Login/Text/viewer/Files/Calculator regressions | PASS, 53 |
| Actual local image review | PASS, classic viewer and native File/View/Help/About |
| Scoped static rollout and hosted browser/image review | Pending |

Document checks include actual heading/paragraph/list authoring and server round
trips, full-path titles, same-file native selection/undo preservation, concurrent
Open, conflict/collision/cancel, delayed saves with newer edits, and lost response
after confirmed server commit without unsafe retry. Recovery checks include rich
model/media, untitled/orphan drafts, refresh, changed saved bases, quota failure,
a new snapshot requested after minimizing, account switching, completed versus
cancelled session end and a late edit invalidating an earlier close approval.

Browser-local drafts recover the last committed checkpoint; they are not account
saves, server backups, undo/session reconstruction, immunity to browser eviction
or a guarantee of zero-loss power failure. All unfinished UI/IME states are not
exhaustively qualified. Profile-scoped preferences/fonts are browser-local and
same-origin code remains trusted. No physical second-machine, all-format parity,
multi-user capacity, shared-service contention/fairness or per-window RAM claim
follows from the functional checks. Delegated-agent transport remains separate.

Only Calculator, Files, Text, WordCraft and Help are enabled. Other organized
Craft repositories, including GridCraft and PdfCraft, have not inherited these
results and are not enabled by this release. See the
[general integration guide](../migration/CRAFT-INTEGRATION-GUIDE.md) and
[running change register](../migration/CRAFT-INTEGRATION-LOG.md).

Before rollout the known previous release is
`7544838dbca89c9a2ddd4abcebc02006c98e5c44c008e4f004813020ba28e123`.
The reviewed operator will stage on the data filesystem, fence that exact
previous root, back up configuration privately and change only the ksu.codes
static root with a Caddy reload. No backend or beta service restart is included.
