# Beta hosting activation — 2026-11-02

The separately backed beta route is live at https://beta.ksu.codes/. The
reviewed hosting source and launcher are commit `c88bd5a8b` on
`research/beta-hosting-isolation`. The protected host copy is
`/srv/codi-connected/beta-hosting-plans/c88bd5a8b/research/beta-isolated-hosting/ops`;
its launcher SHA-256 is `e66638bdef3732dac861020b973e1b08005cdb29a0887516d6c4e18d2bdeedb5`.
The activated static release is
`0965a0cbdd022f588061cdc23e10eb6b18fa5977cc3f6a05569439eaf11d2020`.

The read-only plan passed. The first apply stopped before commit because its
immediate HTTPS test reached Caddy while Let's Encrypt was still issuing the
new certificate. The reviewed recovery rolled back to the pinned previous
hosting configuration, cleared its journal, and restored the active/enabled
renewal timer. Caddy's logs reported successful certificate issuance five
seconds after the first health check. A second apply of the same reviewed
bundle then passed, committed, cleared its journal, and restored the timer.
The respective root-private backups are
`/var/backups/webhost-sites/beta-hosting-_fi4z3oz` and
`/var/backups/webhost-sites/beta-hosting-weai42sx`. These are hosting source
snapshots; they are not user-data backups.

Current SHA-256 pins after activation:

- `ops/common.py`: `d0bcadbe57e351874ab3208849edc21a5812cf274f58e6c19486f8bc04d57c18`
- `sites.toml`: `a1da81c3fc92faf69203c680beb2be666cc79081ee0f5cc1b5c2f311068f3461`
- `/etc/caddy/Caddyfile`: `ce58f8e419a05a05561e0411ce9930e84367b0dd286c02aba617dbce7037ec52`

After activation, public HTTPS certificate verification succeeded for beta
and all ten existing site checks. Root requests returned 200 for beta,
python.coach, code.contractors, ksu.codes, arpa.net.ai, plastic.download,
official.bid, does.trade, codi.codes and cardboard.ksu.codes; hardware.ksu.codes
returned its expected 401. The beta issuer, gateway and frontend units were
active. Beta config names `https://beta.ksu.codes` as issuer and omits
`guestNetwork`; `/guest-network` returned 503. The renewal timer was active
and enabled, and `/var/lib/webhost-ops/beta-hosting-journal.json` was absent.
These checks do not establish a full public signed desktop/file workflow;
that separate browser test remains necessary.

The launcher retains the documented bounded race against an uncoordinated local
writer of the existing hosting files. The service preflight in this bundle
relies on the launcher's immediately preceding `verify_native()` call to
validate every native release file and its custody. Do not use that preflight
standalone. The health check has no certificate-issuance retry; a future new
hostname could repeat the safely rolled-back first-issuance timing failure.
No new router port was required.

## Subsequent beta gateway switch

After this route activation, the separately documented gateway switch
recovered safely from an initial listener-readiness race and then installed
worker manifest `c0465afeb10dac4a761b274eb6871a8af750fccc5523a333da2c98dac8b90960`.
The active beta gateway unit SHA-256 is
`d94a346a364538a33ed5f76403b6c4067b28c813dda469cc0a4b0a9655141fea`.
The switch receipt and the exact recovery evidence are maintained in the
server branch at `c50a91875`. An independent read-only check confirmed the
unit and manifest hashes, active service, clear worker-switch journal, and
public batch capability. A capability response by itself is not a data-path
or durability test.

The hosting launcher source has been updated to recognize this worker and
verify its expanded manifest inventory. It is a future-maintenance candidate,
not an installed operator or authorization to rewrite the live route. It has been rebased to the active hosting source and manifest; this baseline
launcher deliberately accepts only a read-only plan. Any future route change
requires a separately reviewed mutation and recovery candidate.

The refreshed plan-only reconciler at source commit `80673a64f` passed its
read-only host plan against the active beta route and c046 gateway. Its
protected host bundle is
`/srv/codi-connected/beta-hosting-plans/80673a64f/research/beta-isolated-hosting/ops`;
launcher SHA-256 is
`f0fd60d083f8969c378e3195b7e724782e6fdfedb36f87bac6140794d75f065b`.
It rejects `apply` and `recover`. The first refreshed plan attempt failed
safely because the inventory checker expected beta to be newly added; the
corrected, independently reviewed active-baseline check passed. No routing or
service state was changed by either attempt.
