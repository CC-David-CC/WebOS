# Prepared public R4 Agent tools acceptance

Status: **PREPARED, PUBLIC FUNCTIONAL EXECUTION NOT RUN**. Root must authorize
the browser/account run after activation. The only public requests made here
are read-only code preflight GETs proving current BBC refuses safely. No CDP
connection, browser context, account registration or model/file authoring ran.

## Exact target and prepared drivers

- Origin: `https://beta.ksu.codes/`, ordinary trusted TLS.
- Artifact: `337b69de24aa84f726a5d3cedb8f16f7ade026baa206b4faa31281ff380d827e`.
- Desktop: `29fea20659f27f0cb212bf520b210f0311ad962f`.
- Bundle: `d90e75bbb67daa69ca1479ecb21165bfb0f0762dc87cf2caf7a5f2265db465ac`.
- Registry: exact2ea source, asset43a7b8cf….
- Core: e5f603b6…, inner appd78d5333….

`prepare.py` reads the accepted originals with git show, requiring their exact
hashes before changing anything:

| Driver | Accepted source | Source SHA256 |
|---|---|---|
| Agent tools18-row workflow | ec4da121d / research/beta-cad-agent-tools-20261106/browser.cjs | e79278314e52cdd8fd5b35d5f8e110fbf94668c8689a54994f2682697062ba3e |
| Exact two README recipes |6ff4261b1 / research/beta-cad-agent-recipes-20261106/browser.cjs |50e23ce5f772951d46d241bc41f996a6d57ff703096823b896f6b2480a25a32a |

It resolves the installed Puppeteer package with an explicit supplied path,
requires version24.35.0, resolves its require export inside that package, pins
the actual module hash and writes that absolute module path into each generated
driver. No bare /tmp dependency lookup or environment-selected arbitrary module
is used. Reprepare on another machine with that machine's qualified dependency.

Every replacement is recorded and reversible. `audit.py` reconstructs the
entire generated bodies from the accepted originals and checks exact equality,
not merely assertion counts. All original modeling/file/refusal/lifetime
assertions remain: Agent tools38→40 assertion references; recipes32→34. Added
assertions check real Applications→3D Printing→CAD navigation and actual window
title. The two README code fences are still extracted unchanged from committed
42e8f3ce5 at execution. No geometry, material, parameter or file seed is added.

Changes are limited to exact HTTPS admission, local-CDP restriction, explicit
dependency/helper resolution, fixed R4 source/hash labels and helper bundle,
pre-account hash gate, actual Applications launch/title and read-only runtime
pin evidence. Normal native Save/sync/fresh Files Open/export semantics, dirty
New/Open confirmations, rejected changes, sibling Close and own-context cleanup
retain the originals. No browser.close(), certificate exception, fake UI,
private writer or fake successful output is introduced.

## Before any browser or account

Both drivers require the fixed source/artifact/origin settings and run
`assertPublicCandidate()` before `puppeteer.connect`. It performs three exact
GET/hash checks: public simplified app.js, desktop-apps.js and versioned
registry43a7. Redirects refuse; payloads are bounded to2MiB. Node's normal TLS
validation remains on, and NODE_TLS_REJECT_UNAUTHORIZED=0 refuses explicitly.
The recipes driver also retains its original independent preflight assertions,
updated to the same R4 bytes rather than silently deleting them.

Once future execution is authorized, the actual mounted iframe must reference
the exact D90 bundle. Its inner app is streaming-hashed through ordinary HTTPS
once per driver process (64MiB bound) and must equal d78; subsequent fresh
windows in the same run recheck their exact bundle URL without repeating the
immutable33MiB app transfer. This records actual served runtime bytes instead
of treating a source label as proof. This positive path has not run publicly.

## Actual current-BBC refusal proof

`probe.py` ran both final prepared drivers with denial-only guards. Real public
GETs determine the outcome; no successful response is fabricated. The guards
allow only the three public code URLs and forbid all browser connections.
Current BBC app.js SHA04b5c1e1… differs from required R4e0915d88…, so both
drivers return their explicit candidate-not-active refusal before connecting:

- CDP/browser connection attempts:0.
- Browser contexts:0.
- Accounts created:0.
- Requests per final driver: one genuine accountless HTTPS static GET.

The preload observes bounded streamed clones of responses only to record their
real hashes; it returns the original real response unchanged. This is a gate
test, not a functional browser test or a positive activation test. Once R4 is
active this negative probe is expected to stop being applicable and must not
be used to manufacture a refusal. Two initial probe harness mistakes are
retained: duplicate environment keyword before any child/network operation,
and expecting a custom error code from the recipes driver's existing
message/stack-only error formatter. The final oracle checks the exact refusal
message plus observed real bytes and0 connections. No product assertion changed.

## Prepared paths and execution after authorization

Final local generated packet:
`/tmp/codi-beta-cad-agent-public-drivers-20261106-r4-final`.
It contains agent-tools-public.cjs, recipes-public.cjs, driver-pins.json and
public-test-env.json (nonsecret settings). Intermediate preparation evidence
is retained separately as *before-runtime-pin*; final records are in
evidence/prepared-pins.json, body-audit.json and gate-final/.

Reproduce preparation only:

```sh
python3 prepare.py --repo DESKTOP_CHECKOUT \
 --puppeteer-package QUALIFIED_PUPPETEER_CORE_DIRECTORY --out FRESH_PACKET
python3 audit.py --repo DESKTOP_CHECKOUT --drivers FRESH_PACKET \
 --manifest EXACT_R4_MANIFEST --output body-audit.json
```

When root authorizes execution after activation, load public-test-env.json into
the process environment, choose fresh CODI_RECEIPT files and CODI_OUTPUT_DIR,
then run the two .cjs drivers sequentially with qualified Node24 and exclusive
foreground CDP19329. They create only their fresh owned registered test accounts
and close their own contexts/disconnect; they never restart or close shared
Chrome. The existing independent recipe oracles remain available in
research/beta-cad-agent-recipes-20261106/check-native.py and check-3mf.py;
run them on the actual new exported files after the recipes driver, not on
older retained binaries. Keep exports outside Git.

Nothing in this directory installs, selects or mutates hosting. These prepared
drivers and source audits are not evidence that the public R4 workflow passed.
