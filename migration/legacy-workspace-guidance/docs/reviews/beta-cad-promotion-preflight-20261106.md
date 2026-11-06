# Beta CAD promotion preflight — 2026-11-06

**The live baseline is identified. There is no installed generic CAD/catalog promotion command.** The current actor recovers the exact 3ad→830 Files transition; a new CAD graph needs a narrowly reviewed successor binding after the final combined CAD artifact qualifies.

Read-only review from desktop `19396b4bee0fb99dfc330ce2b465cfb1175c2913`. Nothing was deployed, packaged, restarted or reconfigured; no actor was invoked. No accounts, keys, session state or protected probe credentials were read/copied. Accepted Files functional tests were not repeated. Exact observations are in [host metadata](beta-cad-promotion-preflight-20261106/observed-host.json) and [public GET hashes](beta-cad-promotion-preflight-20261106/observed-public.json). Recheck these pins immediately before later mutation.

## Authoritative current selection

| Surface | Current binding |
|---|---|
| Main | `f2e2ed4d3b75e8c40992a18bf83db7937fe90615bf1151e1b51ed3b0a8012f4a`; supersedes the older 0366 main handoff |
| Beta base | `0965a0cbdd022f588061cdc23e10eb6b18fa5977cc3f6a05569439eaf11d2020` |
| Beta OPFS/static selector | `830ca4f174a37cd499a05e07c373a0412fd94c3e6f232234a87645662170a1f0`, under `/srv/data/codi-beta-opfs/`; maintenance=false |
| Beta storage graph | `3daf09a753455be1dc07ce183097b6535a999d2cc2124f9d0e6df25c7180be3a` |
| Beta host/catalog graph | `f8a27d0e69ecbd99cc7dee55b3664dd18f703cb3b90cfa7b904eda7aa514f17f` |
| Catalog path | `assets/desktop/apps-files-<hostGraph>.json` |
| Catalog SHA | `553416ebb4d0043c96e31bb559acd915ca33b7102945c910b89f151ffcc2d8fd`: 74 entries, **no jsketcher entry** |
| Actual beta query loader | `/desktop-apps.js?simplified=1`, SHA `192f4a989b50523f360e1e90705203e569ecf286632bc09a3e9165012e856135` |
| Beta Files bundle | `b7e943c563ea83ad91988e595e1afcada8f31d71eda01e9915d104f32774d7b7` |
| Beta Text bundle | `241776677999e79b759ab00e077569a93f081ccb1cc9c04e42a192e9e6b9bcb3` |
| Beta CodeMirror bundle | `c61da9af5b23236d13903f04d906d83aff0cc93156f02d77ec8beefedc34b679` |
| Beta issuer | `853c12e581c9f89fc3d78507f43941dd16cd0b4b894b28cdb8317e8a58340f21` |
| Beta gateway | `dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1` |
| Beta frontend service | Existing `microduck-issuer-1666491de4fe097285f02a5b6f7602fe57e4b9d3b2995bf016d4a9e809e36a51` backend; this is not the static selector |
| Prototype | `/desktop/`: trusted HTTPS 200, 3318 bytes, SHA `fbf4b940d1ce481d856742561007a8b15be747c0e43307792db481b75be6cf1b` |

The catalog and query-loader hashes were independently fetched through trusted public HTTPS. Main and beta root pages also return 200. Historical `notDeployable` wording inside the 830 build manifest does not describe its later activation: current managed selectors and served hashes establish the actual selection. Its full catalog retains games and older apps; adding qualified CAD does not qualify those other apps.

## Current managed code and configuration

| Path | SHA-256 |
|---|---|
| `/home/dflanag3/webhost-sites/ops/common.py` | `e06fc8aa018ff048138fb2585ddb34ab9c6f1b061fb0022b06b14dca7df55928` |
| `/home/dflanag3/webhost-sites/ops/webctl.py` | `ca25bb27799f0f306d7d901188d894d39ad22ea99ea2c1f1d224a2c6446ab8b9` |
| `/home/dflanag3/webhost-sites/sites.toml` | `555c03041de1dd099f3d0e9d78c721ac1b1f5cc625a0bb0bba8bfc4284c13bb1` |
| Generated `/etc/caddy/Caddyfile` | `0a2cdcc3fe2913d55a7032a1258eb7c43952e14af6c9dfca39c074b678685cfb` |
| Actor `inventory.json` | `c5437979fca4f41075a9052fedc339a659f022e2ddeefb6699cc74439bfe89a8` |
| Actor `ops/asset-launch.py` | `5183facff1799a7b5a710ce7eba79924f4fbdaa3f381e56c1db028be25a40a40` |
| Actor `ops/asset_router.py` | `40a66ce656440c0db5ea7795c72c3cbebbac603c2774ab35072a414fdfe6af74` |
| Actor `ops/asset_select.py` | `eda5fa3af4a4b2618667a28dfaf47acff0d3b4ccd3537ef83dea7009ac012b80` |
| Actor `ops/beta_launcher.py` | `5b8a0fe4f330257698843fb14db76e2ab4c824bea26f6ad94057cf6fd5a6d14a` |

The actor root is **`/srv/codi-connected/operators/beta-files-main-f2-v3`**, superseding older 830c-v1 references. All 35 installed source entries matched its root-custodied inventory. Its advertised actions are plan/apply/recover, but its old apply admission cannot promote an arbitrary graph after the existing asset floor. Recovery recognizes the current f2 main family. This observation does not rerun deployment/recovery or authorize using this actor for CAD.

Relevant source contracts:

- [Main-compatible actor derivation](../../research/main-opfs-release/build-beta-binding.py).
- [Exact snapshot selection](../../research/main-qualified-release/beta-asset-830c/asset-select.py), [router](../../research/main-qualified-release/beta-asset-830c/asset-router.py), and [guard derivation](../../research/main-qualified-release/beta-asset-830c/build-guard.py).
- [Main activation receipt](../evidence/main-opfs-f2-activation-20261104.json) supersedes the earlier main-0366 state.

These paths implement pinned endpoint selection under the existing hosting lock. The generator/guard accept known endpoints and exact route blocks, not a general content-addressed app argument. Retired fixed entrypoints must not be restored. Never edit derived Caddy or overwrite an immutable selected file in place.

## Floors and rollback boundary

Both root-owned 0600 floor files remain exact:

| Record | SHA-256 / meaning |
|---|---|
| `/var/lib/webhost-ops/opfs-floor.json` | `90a476226aaaa2fe639c3642ef8d80be5a378e96b6c080345864b29db3ed596c`; e7a5→3ad |
| `/var/lib/webhost-ops/files-asset-floor.json` | `21feaae39622361b838fc59dd03195c43c62a06616011ece5faa51bb1ea91c1d`; 3ad→830 |

Full record values are in the observation. Eleven known transition/install journals are absent. A pending or mixed state discovered at execution time requires its phase-aware recovery, not blind replay.

Preserve current main selection and its generated block SHA `5012427db5de82346517cabf8fb5abcf23c005c0751bbe410710ede8d49c4ea7`. Beta's current block SHA `b25aa6d01471730a27a73ec85569704f59d20bc7b6c30cb1e371e9b0e570d61c` is the deliberate managed replacement baseline. Keep `/desktop/` byte-identical.

A CAD static release needs no account/key/data-root/service-identity/storage-schema replacement. Its reviewed code-only rollback should return to exact 830 (or a later explicitly qualified endpoint), retain saved files, and leave both Files floor records unchanged. Do not delete/reset floors or route clients below the accepted storage baseline.

Current routes/recovery still depend on base 0965, active overlay 1d6b8f4e…, both retained overlay records, 830/3ad artifacts and f2 main assets. Retain the required declared versioned URLs and inventories while that mechanism needs them. This is asset/recovery preservation, **not** a request to requalify old running windows: the user permits reload/replacement and rejects historical-window diversions.

## Artifacts and successor root must supply

1. **Final combined association:** exact desktop adapter, CAD and native-provider commits/builds, plus source-matched signed/mounted functional receipts. Core Worker passes do not establish final hosted mount behavior. Keep corresponding-source packaging deferred until the functional gate permits it; this review creates no source archive.
2. **Closed public CAD bundle:** app entry/styles, all referenced chunks/imports, three content-addressed Workers, semantic/profile helpers, every exposed native Worker/glue/WASM and runtime manifest, and required static resources. Preserve pinned per-feature runtime through history/Boolean replay. Include default/secondary engines actually exposed. Record SHA/size for every file, total size and app bundle identity; exclude research harnesses, private fixtures, test-only authoring helpers, accounts and keys.
3. **Beta-derived catalog/host/cache graph:** preserve unrelated 74 entries and accepted Files/Text/CodeMirror/storage bytes unless a separately qualified change is necessary. Add jsketcher and its command metadata through the actual mounted host contract. If host modules must change, provide their immutable graph/loader and qualify it. Catalog, cache manifest, service-worker selection, loader and relative asset bases must agree. Never publish a one-app builder catalog as the entire catalog or copy the research desktop wholesale over live beta.
4. **Narrow managed successor:** bind exactly current 830→new CAD and intended code-only reverse/gate states, current f2 main, existing floors, generator/guard/render-inventory/actor pins and hosting lock. An additive app overlay is also viable if explicitly represented and qualified by these exact-state checks. Reuse the known transaction/recovery approach; do not add arbitrary-selector bypasses, reset floors or patch raw Caddy. Root will prepare this source for review only after final functional qualification.
5. **Immutable staging and rollback receipt:** stage final public runtime/catalog artifacts, preferably on `/srv/data`, verify closed inventories and custody, and retain both endpoints needed by recovery. Exact new plan/apply/recover invocations follow successor review; the current fixed actor is not a new CAD promotion command. A failed gate action does not prove closure: record observed endpoint/phase and use defined recovery.
6. **Bounded final delivery check:** fetch exact authenticated beta app/catalog/Worker/native URLs with actual CSP/MIME and exercise the qualified mounted agent build/edit/reject/travel/save/reopen/Close workflow. Verify main, prototype, floors and account isolation remain intact. Reuse accepted Files evidence; do not restart a full Files audit. No new DNS/router port/CSP expansion is established as necessary here.

At this desktop commit `apps/system/jsketcher/prepare.py` still pins CAD `67d3432921f2aa4256893a618cd8f11ec732aa51` and older emitted Worker/native filenames. Its `app.json` is likewise a historical bounded asset inventory, not the final current-candidate release recipe. Reconcile only the required final runtime inventory after qualification; do not blindly invoke the old pin or start deferred source-package work.

For orientation only, the current private combined artifact is CAD `15b9607a7880eeb7cf98f9de40a3563d19a3c5a6`, R730 `/mnt/data10tb/codi-cad-selected-profile-combined-20261106-r1`, app SHA `01f3eee8e2e0d0ccee253a33af40d47b704f04015b7f992e20a04f44ab0e27e6`. Root's final proof may supersede it. A private fixture's partial pin list is not a closed distribution manifest.

## Concrete prerequisites and capacity

- Final combined signed/mounted release proof and public catalog/runtime artifact remain required.
- Existing fixed-endpoint operator cannot select a new CAD graph; a narrowly reviewed successor binding is required.
- Final runtime inventory must supersede historical preparer pins, separately from deferred corresponding-source packaging.
- The beta account volume has 6,632,144,896 available bytes, 1,263,435,776 above its 5 GiB reserve; `/srv/data` has 318,298,349,568 available bytes. These are point-in-time observations. Keep large build/staging inputs off the account-volume reserve. Beta's three services and Caddy are active; the pre-existing renewal timer is inactive/disabled and outside this static CAD release.

No DNS/port blocker was identified. The release constraint is exact artifact composition and managed endpoint binding, not another storage implementation project or missing user permission.
