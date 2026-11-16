# 830c asset transition — isolated research, not an operator

Inputs: exact parent 3ad and corrected target 830c. The target keeps every old
path and preserves the old global apps.json; four old files differ (cache
manifest, offline worker, desktop loader and unserved patch), with 84 added
paths. Generator SHA-256 `e06fc8aa018ff048138fb2585ddb34ab9c6f1b061fb0022b06b14dca7df55928`;
route-table SHA-256 `32ad4a8b79bfa3886f5a16b29e6b55e04d17268230ba449c967a344283a720c1`.
The guard builder produces SHA-256
`ca25bb27799f0f306d7d901188d894d39ad22ea99ea2c1f1d224a2c6446ab8b9`.
The derived render-inventory builder produces SHA-256
`49e99fe32497149ee6f89d840f36afc152e4176414dd6978a0f72457b24d37d3`.

`generator.test.py` binds both original and e7 main families, confirms exact
old and gated Caddy bytes, non-beta equality and unknown selector rejection.
`caddy.test.py` tests all 166 asset routes, exact shell queries, retained old
overlays, backend routing and maintenance denial on real loopback Caddy.
The isolated baseline fixture is not the whole live site; browser/account
compatibility is a separate test.

`asset-floor.py` reuses the existing FloorJournal with separate asset journal
and asset floor names. Every lock check verifies that the original OPFS floor is
still the exact e7a5/3ad record. It gates before a new asset floor is durable;
a pre-floor interruption may restore 3ad, and a post-floor interruption returns
to the gate then forward to 830c. A finalized recovery with unavailable 830c
leaves the gate selected. Five SIGKILL model tests cover those outer phases.
`asset-router.py` binds only pinned 3ad, gate and 830c snapshots for the exact
old/e7 main families to the existing transaction and inventory. It rejects
unreviewed endpoints and old-route restoration after asset floor.
`controller.test.py` uses the pinned copied managed controller and real
loopback Caddy against e7 for SIGKILL at outer gated/floor/forward stages and
inside the Caddy reload before and after asset floor. It checks a 503 gate,
correct recovered endpoint and unchanged original floor. The test translates
production hostnames/paths to loopback; timer, service checks, signed health,
backup and main health use fixture callbacks. Forking with its HTTP fixture
thread causes Python's documented warning; no deadlock was observed.

The generated guard rejects a pending asset journal and after the asset floor
accepts only 830c with its exact beta route block. The current live fb27 guard
and bc9 recovery successor do **not** understand that floor. A protected,
reviewed combined successor/guard installation and quiescence fence is required
before asset transition. The snippets here do not establish supported entrypoint
fencing, privileged custody, actual backend/signed health, production ingress,
old-client persistence, or release safety. No live changes were made.

Example tests, with verified input trees and Caddy:

```
python3 -B research/main-qualified-release/beta-asset-830c/generator.test.py OLD NEW
python3 -B research/main-qualified-release/beta-asset-830c/router.test.py OLD NEW
python3 -B research/main-qualified-release/beta-asset-830c/guard.test.py OLD NEW
python3 -B research/main-qualified-release/beta-asset-830c/asset-floor.test.py
CODI_ASSET_KILL=inner-after python3 -B research/main-qualified-release/beta-asset-830c/controller.test.py OLD NEW CADDY
```

## Protected actor and installation candidate

The derived e7/3ad recovery actor checks for either asset journal or asset
floor **under the hosting lock before route changes**. It uses the new guard
pin and refuses when 830c recovery owns the state. Its source inventory SHA is
`753812dfc1848d344e36e5bab53ae455c1cdb262d8b538040e0245f6a99637cc`;
its executable SHA is
`6128839236b4d8286b13fc76e9ad43e55a9024f2b4606289eb2e7fe8af05e113`.
An isolated R730 namespace used its literal bytes with a signed disposable
beta account and real translated Caddy: ordinary 3ad recovery passed and each
asset marker caused refusal without changing hosting source, manifest or Caddy
bytes. Timer/systemd/production-health behavior was simulated. The first run
failed when the test tried to read a root-owned fixture Caddyfile without sudo;
that fixture-only defect was corrected and the run passed. The proposed new
guard additionally pins the original floor baseline exactly.

The 35-file actor inventory SHA is
`142509906abcce599465417dcfd0430e80ab647f843b5aa42c9922d7fb152f63`;
its executable SHA is
`520327e7dc33fda477c13029ab12bc2c9f32622fed697d5e4e9199d69b0db392`.
It contains both the guard-aware 3ad recovery actor and the 830c actor, their
pinned modules, original table, and exact new manifest. Its protected actor
checks exact e7 route snapshots, source/asset inventories, original floor,
guard, existing account boundaries, 5 GiB account-volume floor, beta native
853 and gateway dd8, and signed known-file health. Gate closure deliberately
does not depend on the forward asset tree or signed backend health. An
isolated literal-actor R730 run with real translated Caddy and a signed
fixture account killed the process during the post-asset-floor Caddy reload;
recovery completed forward to 830c, retained the e7 main selector, preserved
the original floor byte hash and cleared its outer journal. Timer/systemd,
production main readiness and network translation remained fixture
substitutions; no live claim is made. Unknown/malformed mixed state is refused,
and such refusal does not itself prove the gate closed.

The new asset floor is a durable **rollout policy marker**, not a new browser
storage schema or a replacement for the original 3ad OPFS floor. It prevents
supported guard/recovery paths from reopening the older asset endpoint after
830c exposure. The original 3ad floor remains byte-identical. The 830c package
retains old immutable 3ad paths for existing tabs; route retention alone does
not prove their account/data compatibility.

The 830c installer is derived narrowly from the tested main installer: exact
fb27→ca25 guard replacement, one root-owned 35-file actor bundle, the same
hosting lock, original floor and shared main-restriction journal. Its four-file
installation manifest SHA is
`9d2b610c32aef9e694acdf329783ebe2e323ba65106fbf764417612db4645542`.
Five real primitive SIGKILL boundaries and a literal fixed-path namespace test
passed staging/guard-replacement interruption, recovery and idempotence; the
latter also checks active-timer, known-invoker and conflicting-journal refusal.
Timer unit hashes/state and service manager are fixture substitutions. A
trusted administrative maintenance freeze, stopped/recorded known timer,
drained loaded legacy jobs, protected source bootstrap, independently pinned
package and host custody checks are still required. The existing main e7
one-shot launcher pins fb27 and will refuse after ca25; it must be explicitly
retired after its completed cutover or replaced with a separately reviewed
binding. Do not treat that refusal as generic main recovery support.

Public-code-only review archive on R730:
`/mnt/data10tb/codi-830c-operator-review-20261104.tar.gz`, SHA-256
`060a22bf03b7716757bc8af45e4397c88c335457212a8fa734793055d03dceed`.
It is a review input, not a root-custodied installation. The 830c public asset
tree is separate. No private state, credentials or production files are in it.

Fixture tests (substitute actual paths) include:

```
python3 -B research/main-qualified-release/beta-asset-830c/asset-select.test.py
python3 -B research/main-qualified-release/beta-asset-830c/build-actor.test.py BASE_3AD_ACTOR TARGET_830C GENERATED_COMMON GENERATED_INVENTORY
sudo -n python3 -B research/main-qualified-release/beta-asset-830c/install.test.py ACTOR_BUNDLE INSTALLER_BUNDLE
sudo -n python3 -B research/main-qualified-release/beta-asset-830c/install-ns-runner.py ACTOR_BUNDLE INSTALLER_BUNDLE
```

Independent source review, actual protected bootstrap/installation,
full capacity/custody checks, supported old-process fencing, real service and
production ingress health, old-tab/account compatibility and public acceptance
remain required. The release is not installed by this checkpoint.

## Superseding review candidate: entrypoint retirement and two main families

The earlier `bdf72e2e1` operator archive is **blocked and superseded**: the
installed old bc9 actor can write `opfs-transition.json` from the shared gate
before checking its old guard pin, and two original ce18 launch copies are also
callable. The revised installer publishes the exact new actor closure, writes
the existing main-restriction journal, then moves all four exact executable
files (bc9 recovery, ce18 bundle launcher, ce18 input launcher, completed main
e7 one-shot) by no-replace rename to a root-only data quarantine with no old
dependency tree. It fsyncs both directories and normalizes archived files to
0400; bytes remain unchanged. It then installs ca25 and verifies all four paths
remain absent before clearing the journal. All source and quarantine parents
must be on the same filesystem. A trusted coordinated administrative freeze,
known timer quiescence and draining of already-loaded processes remain required;
deliberate invocation of archived data or privileged bypass is outside this
boundary. Retiring the ce18 input launcher intentionally changes that input
closure; the individual pinned helper modules used by the new installer remain.
The completed main one-shot is retired only when the shared journal was absent
at installation start. The new actor's 3ad recovery path is fenced by either
asset marker under lock.

The literal fixed-path installer fixture passed active-timer/known-invoker and
foreign-journal refusal, SIGKILL after staging, after each of the four durable
retirements, and after guard replacement, with forward/idempotent recovery.
At each retirement/guard boundary an unexpectedly present asset floor made
recovery refuse before further changes; removing the fixture marker permitted
recovery. The standalone retirement test also checks wrong journal, exact
bytes/modes, idempotence and simulated cross-device refusal. Timer state and
unit hashes are fixture substitutions, not live systemd qualification.

A combined R730 fixture then executed the literal installer, guard-aware 3ad
actor and 830c actor with a signed disposable beta account and real translated
Caddy. After the asset floor and interrupted 830c reload, 830c was temporarily
unavailable; recovery established an actual 503 shared gate. All four former
fixed paths were executed at that gate and failed before running code; the old
`opfs-transition.json` was not created and hosting source/manifest/Caddy bytes
were unchanged. Restoring 830c recovered forward, retaining the e7 main
selector and original 3ad floor hash. The original attempted combined fixture
had a test-only timer-file permission error; that was corrected before the pass.
Fixture processes, ports and namespace files were removed afterward. Production
main health, timer, systemd, ingress and trusted operator freeze remain outside
this test.

The actor now supports only exact e7 and proposed 0366 main families. Applying
830c initially still requires e7; recovery may select either family after an
independently reviewed main change. It rejects cross-family mixtures even during
nested-journal recovery. The 0366 family is a proposed main capability fix, not
an authorization to change main. Pinned-controller/real-loopback-Caddy tests
passed 0366 asset-floor and inner-reload kills; actual 0366 asset installation
and literal 0366-family actor recovery require separate qualification.

Final review candidate pins:

- Guard `ca25bb27799f0f306d7d901188d894d39ad22ea99ea2c1f1d224a2c6446ab8b9`.
- Two-family actor `fecffaed2a83d50b8178b016a9b625fea4dca986f449e565531a58d4a0f3143a`, 35-file inventory `76a7cff14def855ba9dfcdc4a03916772c931df81c9cdafac34653348f4b83b7`.
- Five-file installer inventory `89b0b188b4b337ef67a6cce22faf7e3f05e7947d19eea6bd0d17f0ef886de18d`.
- Public-code-only R730 archive `/mnt/data10tb/codi-830c-retirement-review-20261104.tar.gz`, SHA-256 `be6c61467ee1d9e29451c2b95b2866fcd44f57e0520b77efbe9dbfe0b0eba905`.

The original asset floor remains a policy marker: it does not change browser
schema or replace the 3ad OPFS floor. This package and staged 830c assets are
not authorization to activate; independent reviewer, protected bootstrap and
live custody/quiescence/health checks remain required.
