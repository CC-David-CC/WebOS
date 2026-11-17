# WordCraft document integration

Historical milestone: superseded by the [current Design/fonts/account-defaults
release](WORDCRAFT-DESIGN-DEFAULTS.md). The identities, checks and rollback tag
below describe the earlier release and remain as historical evidence.

Status: 2026-11-17 UTC — deployed to https://ksu.codes. All 92 actual-browser
checks pass locally and over hosted HTTPS; actual screenshots were inspected.

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

The public viewer-release.json records its source commit, every selected source
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
| Scoped static rollout and hosted browser/image review | PASS, 92 hosted checks and actual images |

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

## Release and rollback

| Item | Identity |
|---|---|
| Packaged parent source | `81828dc0ede2d5dcdac09657e4b027e3c4b62c77` |
| Public release | `86457f2da2b3b9ed0e6b57ed76fdd17ad114d42237554604fe0d72bee1e50716` |
| Archive SHA-256 | `189f0bc0183c682a53045919c6f7364933838c81d1d6635588b97b3f89b4967a` |
| Previous release | `7544838dbca89c9a2ddd4abcebc02006c98e5c44c008e4f004813020ba28e123` |
| Operator tag | `wordcraft-documents-20261117-01` |

The archive contains 245 public files including the release manifest, totaling
98,082,721 bytes; the gzip archive is 28,288,696 bytes. All 96 JavaScript packages
have notices. Every source input and payload is hash-verified. The complete fresh
native engine is from the selected WordCraft commit, rather than retained old
WASM. The development-profile engine is qualified for these functional checks;
startup and per-window memory are not performance-qualified.

The static root is
`/srv/data/webos-viewer-releases/86457f2da2b3b9ed0e6b57ed76fdd17ad114d42237554604fe0d72bee1e50716/public` on box-webhost.
The reviewed [static operator](viewer_static_operator.py) fenced the exact prior
root, verified the archive/files, validated Caddy and changed only the ksu.codes
static root. Caddy was reloaded; no backend or beta service restarted. Backend
instance/issuer, beta index hash and all checked peer PIDs are unchanged. Existing
file quotas, transfer limits and fixed eight-hour login deadline remain.

The root-only rollback plan is `/var/backups/webos-wordcraft-documents-20261117-01/`.
Run the same operator in `rollback` mode with that exact tag and this release ID,
through the verified box-webhost alias. It restores
`7544838dbca89c9a2ddd4abcebc02006c98e5c44c008e4f004813020ba28e123` with a Caddy reload, without account-file/backend
migration. Never replay init/stage/prepare over existing paths or substitute an
older release's plan. Inspect concurrent configuration changes instead of
bypassing the hash guard. The previous frontend does not offer the new WordCraft
rich-draft recovery; rollback retains those local records and all account files.
Save open work before any refresh.

All eight hosted suites passed against this exact engine/release, with strict
unexpected console/page/HTTP assertions. Actual File/View/Help/About images show
the requested Discord controls removed and About retained; the classic desktop
rail, palette and geometry were inspected. Private commands, receipts, historical
failures and screenshots remain in the owner-only task audit with a resumable
checkpoint. Generated output and test accounts are excluded from Git. Later
documentation-only commits do not change the packaged parent identity above.

Own disposable compiler outputs, superseded candidates and test browser profiles
were removed after successful qualification, recovering 11.31 GiB of actual free space.
The final verified archive, build/release receipts, source/required inputs, logs,
results, screenshots and rollback evidence remain. No broad migration or host
release cleanup was performed.
