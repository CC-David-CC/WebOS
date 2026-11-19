> **Current Craft inventory** — 21 independent Craft repositories under `apps/` represent 20 applications. PCBCraft and FieldCraft join the queue after the original 18. The third addition, pcbcraft-app, owns the upstream browser packaging for PCBCraft. See the [integration matrix](migration/CRAFT-INTEGRATION-MATRIX.md) for paths and status.
>
> **18 of 20 distinct Craft apps are live.** All original 18 Craft applications are live on ksu.codes. SolidCraft passed both fillet regressions in the browser. Hosted release `22b0211e018ae27561ce943a666fb730f795a07e3c016bd084c77d415fb51f0f` matched all 773 files and started the native editor. [Release and rollback](migration/CRAFT-INTEGRATION-LOG.md#solidcraft-release-on-ksucodes)

> **Current SolidCraft source** — The assembly pins `webos/integration` at `030b30262ede` on upstream main `c22baab6e505`. The hosted release runs `71a573e23441`. [Source qualification](migration/SOLIDCORE-HANDOFF.md#qualified-source-rebase-on-november-19-2026-utc)

> **User scope decision — all 18 Craft integrations (2026-11-18 UTC)**
>
> All 18 selected Craft apps are integration targets, including SketchCraft.
> Readiness differences determine sequencing and acceptance work.
> Every selected app gets a visible entry in the existing Desktop menu; enable
> only qualified integrations through the release profile. Unsupported Craft and
> legacy apps stay grayed out. Keep their source. No legacy-editor retirement,
> replacement decision or new quick-preview project is authorized by this scope.

> **GridCraft and DeckCraft rollout**
>
> The user approved deployment to ksu.codes for each app as it qualifies.
> GridCraft `fd80ce89` and DeckCraft `f8353c0d` are live after passing all 87
> checks in the signed local release suite, verification of all 444 hosted
> files and hosted Chromium checks of both modules and their WASM. The
> release and immediate rollback are recorded in the
> [integration log](migration/CRAFT-INTEGRATION-LOG.md#office-release-on-ksucodes).
> Signed delegated document commands use a separate opt-in loopback profile.
> Delegated file operations remain open.
> Normal automatic writes wait 10 seconds after committed typing, at least 60
> seconds between confirmed writes; known no-write transient retries back off
> to 15 minutes. Conflict/uncertain outcomes pause. Manual Save remains immediate.
> Continue with the selected source and exact release qualification.
> Resume from the private checkpoint at
> `/home/dflanag3/Projects/.webos-migration/craft-office-20261117T234813Z-8a43bc/checkpoint.json`.

# WebOS — site integration from organized source

The [public GitHub release plan](migration/GITHUB-PUBLIC-RELEASE.md) identifies the owner, publication sequence, private status ledger and clean-machine verification.

Source organization is complete. Continue site integration from the 18
independent Craft repositories under `apps/`. The user approved rolling
deployments to ksu.codes as each app passes its release checks. Use the
classic Desktop and the existing account service. The
[rollout guide](migration/CRAFT-INTEGRATION-GUIDE.md#rolling-integration-queue)
defines the remaining order and gates.

CADCraft went live on 2026-11-18 UTC in release
`b30b3f0b70ef361eb66c84b544a45961e20331be512d9313713bc846d82fafa8`, bringing
the site to 14 of the 18 selected Craft apps. The exact package passed
112 Chromium checks. A fresh account browser reopened editable
DXF geometry and saved a later revision. Hosted verification matched all
664 files and started the published editor. EffectCraft is the immediate
rollback. See the [CADCraft release record](migration/CRAFT-INTEGRATION-LOG.md#cadcraft-release-on-ksucodes).
TextureCraft is live in release
`60cf68e83c32dc68684aff1dfde05da5dc493deb391784dd22faf4c13c11e581`.
It is the 15th enabled Craft app. A fresh account browser reopened editable
paint tiles and saved a later revision. CADCraft is the immediate rollback.
See the [TextureCraft release record](migration/CRAFT-INTEGRATION-LOG.md#texturecraft-release-on-ksucodes).
The classic Desktop hosts Calculator, Files, CodeMirror 6 Text, WordCraft,
PdfCraft, GridCraft, DeckCraft, PhotoCraft, FigCraft, VectorCraft, AniCraft,
LightCraft, DesignCraft, SoundCraft, FilmCraft, EffectCraft, CADCraft,
TextureCraft, MaterialCraft, SketchCraft, SolidCraft and Help.
PdfCraft's untouched blank closes quietly and can
still be explicitly saved. Its top-right Discord shortcut is removed; About,
community/source links and contributor/model credits remain.

PdfCraft: `a5b512846f59c6e5306821cdffdb448e54695ccd`.
WordCraft remains `edeb4a090cd301cd7d4405e20af795007b37b69b`.
Parent at the PdfCraft rollout: `2d08b293754f36e38b4366865b4ff5d6d64a8f4e`.
[PdfCraft qualification/rollback/limits](deploy/PDFCRAFT.md): all six native gates,
2,989 affected UI test executions (five existing ignored),27 actual-browser
assertions each locally and hosted,10 local/11 hosted PDF content checks and
actual image review pass. Other app/Desktop payloads, beta, backend instance/
issuer and service PIDs are unchanged. No recovery loss was demonstrated: a
later conflict test had overwritten its own evidence filename; artifacts are now
separated. Native content checks verify both recovered and rescued typing.

The earlier PdfCraft release found that clean PDF windows and their exact
placement were absent from saved-layout restoration. The Office release
qualifies restoration for GridCraft and DeckCraft. PDF-specific layout
restoration still needs its own check.

The [Craft integration matrix](migration/CRAFT-INTEGRATION-MATRIX.md) lists
all 18 source locations, native workflows and current qualification.
The [integration guide](migration/CRAFT-INTEGRATION-GUIDE.md) and
[GridCraft/DeckCraft branch plans](migration/CRAFT-BRANCH-PLANS.md) describe
the active work. The [build inputs](migration/CRAFT-BUILD-INPUTS.md) identify
the verified dependency cache, shared input revisions and remaining checks.

Last deployed release checkpoint:
`/home/dflanag3/Projects/.webos-migration/craft-office-20261117T234813Z-8a43bc/checkpoint.json`.
Superseded PhotoCraft development sites were removed after verification.
Keep current build inputs, the current release archive and private evidence.
Preserve unrelated WIP
in `artifacts/input-files.json` and `tests/wordcraft_baseline_browser.mjs`.
The original workspace remains read-only; beta stays live independently.

Independent owners, source/build entries and required inputs are mapped below.
Beta stays live separately.

## Where things belong

| Directory | Source ownership |
|---|---|
| apps/ | 86 application repositories, including 18 Craft, 33 system/tool/CAD and 35 game repositories with 7 planned cores |
| platform/ | 7 platform components: Runtime, Desktop, Login, Accounts, Storage, Rendezvous, Publication |
| engines/ | 9 reusable engines, including FFmpeg and optional v86 |
| libraries/ | 19 reusable libraries, including Craft libraries, egui and TanStack Virtual |
| assets/ | Shared Craft fonts and translations |
| tooling/ | Shared Craft build tooling |
| legacy/rooms/ | Unused old Rooms source; no service implied |
| scripts/, tests/ | Parent source inspection/composition utilities and clearly scoped tests |
| artifacts/ | Ignored, locked runtime/build inputs; never credentials or compiler caches |
| deploy/ | Existing definitions and historical deployment records; no authority to execute them |
| migration/ | Source ownership/catalogs and historical evidence; historical PASS text is not a current release claim |

The [full app/component matrix](migration/APP-MATRIX.md) lists every component by category and functional importance, with its location, interfaces, build entry and production gaps. The [CSV](migration/APP-MATRIX.csv) is suitable for sorting in a spreadsheet. The [source catalog](migration/SOURCE-CATALOG.md) and its [JSON form](migration/SOURCE-CATALOG.json) record actual source/build definitions and package dependencies. Git links select exact component versions. ACAD and original JSketcher are separate. Files and WordCraft are applications, not platform folders. FFmpeg is a shared engine, not a visible standalone app.

## Desktop source decision

The intended existing viewer is [platform/desktop/active-system/](platform/desktop/active-system/), with classic-script entry index.html, bootstrap.js, app.js, desktop-apps.js, reference.js and style.css. All92 source/assets matched the original during correction. Its code has not been rewritten.

The rejected replacement src/ viewer/controller/styles and associated tests were removed. The old parent frontend.mjs/build_development.mjs and its browser harnesses remain removed. The separately authorized test composition now uses scripts/build_viewer.mjs and public account/app services with the existing viewer. Only bootstrap.js, app.js and desktop-apps.js receive integration changes; CSS, reference data and artwork remain unchanged. Five app entries are enabled; broad suite integration remains separate.

## Craft branches

The [Craft integration log](migration/CRAFT-INTEGRATION-LOG.md) tracks WordCraft's
actual integration changes, their validation status and the responsibilities to
assess when integrating each other Craft app. It separates implemented source
from qualified behavior.

The17 Craft app repositories now use main as their verified public-upstream tracking branch and webos/integration for the parent-selected working source. All17 main branches were fetched from their verified upstream on2026-11-16. WebOS changes were not merged with newer upstream, and working files/pins were not changed by the alignment. WordCraft and DeckCraft modifications remain on our branch.

The5 shared Craft projects also have upstream-tracking main branches; their selected working pins stay on WebOS branches. The [verified upstream map](migration/CRAFT-UPSTREAMS.json) makes this reproducible after a clone. Run `python3 scripts/configure_craft_upstreams.py --configure` to restore missing upstream remotes and tracking configuration locally; it does not fetch, merge, switch branches or move pins. To inspect/update upstream later, use the existing upstream remote and fast-forward main deliberately while working on a WebOS branch. Review and merge upstream into a separate WebOS review branch only when desired. Never push to upstream. Local origin stores are separate from upstream and external publication is not authorized. See [Craft build inputs](migration/CRAFT-BUILD-INPUTS.md) for the organized fonts/shared-library locations.

## Source and inputs

Sources/manifests/locks and required input assets are retained. Intermediate compiler builds are disposable and must not be committed. The approved cleanup removed11 compiler-output directories and recovered66.56GiB. Do not retain repeated build trees as part of the deliverable. The older migration directory also contains private recovery and unique work; do not delete source/history/inputs by directory name alone.

[artifacts/README.md](artifacts/README.md) explains the ignored public reference and input payloads. A read-only check verified6230 locked files totaling1,115,334,296 bytes, including6143 reference files. This proves those bytes, not every app's complete build graph. Build recipes may still require public dependencies, separately locked inputs or further integration. Missing inputs and source-only planned cores must appear honestly in the final production-readiness matrix.

A source clone uses the trusted local bare origins and relative sibling URLs in .gitmodules. All124 selected child commits are verified present in their local bare origins; the corrected Desktop branch and Craft branch updates have reached those stores through explicit fast-forward/new-branch local writes. A new full checkout/build was not created for this pass. No private server address should be guessed. Original KSU.CODES remains read-only.

## Read-only inspection

- python3 scripts/inspect_assembly.py --require-core checks source Git-link/checkouts/ownership agreement.
- python3 scripts/catalog_sources.py describes source silos; --write refreshes the two source catalogs.
- python3 scripts/verify_artifacts.py verifies locked input bytes without network access.

These checks do not build or deploy. Follow each component's actual build definitions when future development requires a build, with output outside source and no automatic publishing/service actions. The category/importance matrix is the current inventory; the old runtime status matrix is historical. Seven game cores, the PCB prototype and the template are not finished apps. Explicit input/rebuild gaps and composition work remain listed rather than being hidden behind source-present labels.

The two pre-existing working-tree files artifacts/input-files.json and tests/wordcraft_baseline_browser.mjs remain in place and unchanged. Their authorship is not assumed. They are explicit unfinished working material, not an instruction to run or delete anything.
