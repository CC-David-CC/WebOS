# Build, run, test and deployment

## Verified environment and input custody

Read the private verification receipt for actual successful commands and final hashes. The checkpoint uses R730 Linux and Chrome for Testing 155.0.8059.79. Chrome archive is retained at `/mnt/data10tb/codi-restart-runtime-20261110/chrome-linux64.zip`, SHA256 `bcd9a79130d7e44d70f93be87042e9bcee7fe0f0b3898e06b8c9bed5fb619dcd`; official URL/provenance are next to it. It runs on R730, not through the old PC CDP tunnel. The isolated test may require `--no-sandbox` for this host's container/userns setup; never apply that to the normal user browser or public service. SwiftShader is a software GPU and is not a physical-device performance qualification.

Node: `/mnt/data10tb/codi-3mf-qualification-SrUmue/node/bin/node`. Build dependencies: `/mnt/data10tb/codi-acad-build-20261107-r2/node_modules`. App builder dependencies: `/mnt/data10tb/codi-agent-bracket-desktop-20261105/active-system/tools/app-builder/node_modules`. Puppeteer24.35.0: `/mnt/data10tb/codi-acad-acceptance-deps-20261109/node_modules/puppeteer-core`. Fixture Python: `/mnt/data10tb/codi-mirror-sync-venv/bin/python`. Independent streaming reader has a separate pinned ijson environment under `/mnt/data10tb/codi-evidence-reader-20261110-r1`.

The native inputs and exact six cache hashes are in ACAD `docs/handoffs/cad1-build-assembled-20261110.sh`. Additional inputs are finite/circular/mechanical/analytic portable directories plus `.build/arrangement-native-inputs` under the dependency checkout. These paths are R730 storage, not a requirement for this PC. The private runtime-input backup materializes their symlink closure. Restore absolute path structure on R730 or deliberately rewrite the build recipe to a new input root and verify every resulting hash. Never silently substitute a fresh npm/native version.

## Exact fresh build recipe

Choose a NEW absolute output. Do not reuse the original qualified build or evidence directories.

```sh
# Run ON R730; get the script from the integration checkout.
bash acad/docs/handoffs/cad1-build-assembled-20261110.sh   4fa264907c9bf44a6a0d857aa5495bc2c3cc6073 /mnt/data10tb/NEW-CAD-BUILD
# Fresh desktop checkout at 64e70e9b548e41006f8334d7b349654f88459732.
# Temporarily link its app-builder node_modules to the retained builder deps.
python3 /mnt/data10tb/NEW-CAD-BUILD/test/native-cad-container/stage.py   --desktop-source /mnt/data10tb/NEW-DESKTOP   --cad-dist /mnt/data10tb/NEW-CAD-BUILD/dist --output /mnt/data10tb/NEW-STAGE
/mnt/data10tb/codi-3mf-qualification-SrUmue/node/bin/node   /mnt/data10tb/NEW-DESKTOP/active-system/tools/app-builder/build.mjs   /mnt/data10tb/NEW-STAGE/builder-config.json
# Remove only the temporary app-builder dependency symlink before source custody.
/mnt/data10tb/codi-mirror-sync-venv/bin/python   /mnt/data10tb/NEW-DESKTOP/active-system/scripts/run-simplified-local.py   --port 21110 --isolated --apps-bundle /mnt/data10tb/NEW-STAGE-apps   --runtime-root /mnt/data10tb/NEW-PRIVATE-STATE
```

Do not add `--browser-relay`. Choose unused loopback ports and new private state. Existing R3–R8 fixtures use 21064–21069. The checkpoint verification uses 21110 and R730-owned Chrome CDP19610. Its temporary accounts/state are private fixtures and excluded from source/portable public assets. Preserve actual saved artifacts and receipts before normal controlled cleanup.

For changed product source, do NOT keep old pins. ACAD `test/assembled-fixture-pins/README-next.md` specifies derive→review exact contract→commit→pins against clean separate Core/Host/acceptance checkouts. Original R8 contract is `test/assembled-fixture-pins/reviewed/assembled-r8.json` SHA256 `eb9c133238ae45d3ebd3788507a956959f7a112cb540a96905f37d66d49910dd`. Original R8 pins `/mnt/data10tb/codi-acad-assembled-pins-20261110-r8.json` SHA256 `50a83469e596641fee99342efababa093aae555dcc27cbb0b1384ae914c693d3`; corrected acceptance pins end `-r8-unicode.json` SHA256 `c6184bc2810e4fa0abbca1612b171dc0294745a678d8eeab92a4588178e9a91a`. Stage/build byte equality must actually be verified, not inferred from same source.

Saved-content driver: `test/saved-content-lifecycle/desktop-driver.mjs`, independent `run-artifact-oracle.py`. Set its required CODI_* variables from actual tuple/pins. Source custody rejects dirty roots; acceptance is distinct from compiled source. Other full flows and contracts are in the ACAD test dirs cited in STATUS. Read the original whole contract before running it. Keep original evidence immutable; no independent PASS claim for a failed whole.

## Where public deployment actually is

Read-only observation during this handoff found `codi-beta-frontend.service`, `codi-beta-gateway.service`, `codi-beta-issuer.service` running on box-webhost. This is separate from R730 private fixtures. Beta frontend currently invokes `/srv/codi-connected/releases/microduck-issuer-1666491de4fe097285f02a5b6f7602fe57e4b9d3b2995bf016d4a9e809e36a51/guest-relay/server.py` on28132 with `--no-guest-network`. Beta gateway is `/srv/codi-gateway/releases/dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1/scripts/serve-user-files.py` on28140. Beta issuer uses `/srv/data/codi-beta-native/853c12e581c9f89fc3d78507f43941dd16cd0b4b894b28cdb8317e8a58340f21/scripts/serve-connected.py` on28118. Private credentials are systemd-managed and must not be exported into Git. Service state is not proof that current ACAD integration has been deployed.

Use Desktop `docs/HANDOFF-FILES-CAD-2026-11-04-CURRENT.md` and actual hosting controller state to reconstruct the managed deployment chain. Operators live under `/srv/codi-connected/operators/`; read-only unit/manifest/pin inspection comes first. Do not hand-edit Caddy, replace all beta apps with this two-app fixture, copy issuer state between sites, activate an old source-only guard, or equate staged code with selected serving code. Preserve root main/prototype and existing accounts according to current user direction. No deployment occurred during this handoff; new final beta remains a pending Gate1 task.

## Recovery scope

All source refs and standalone native source repos have private bundles plus verified restores. Frozen source worktree patches are separate. Runtime inputs and selected original whole/AFTER artifacts have private archives/manifests. This is enough to resume on R730 without the PC after verification passes; it is not a backup of public service account state, DNS control or all historical desktop runtime assets. Provision authorized access separately. Unrelated apps may have build requirements not covered by this CAD-focused restart test.
