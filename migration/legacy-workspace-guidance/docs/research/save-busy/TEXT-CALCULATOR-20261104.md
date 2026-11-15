# Text and Calculator operation integration

The host must install `documentOperations` through `mountApp` (integration source `9fa27ad728fb9897abd7c365d8dd34b040cf558a`). Text and Calculator require that service and use `mirror:` plus the normalized mirror path. Text reserves initial open before CodeMirror loads, holds open/reload across discard/picker and nested read, and holds Save As across its dialog. A completed Save As retains the source and destination claims until local commit. Calculator holds open, folder and save work, and binds the visible buttons to the same operation state. Existing revision/version and local-storage semantics remain independently required.

`document-operations-apps-browser.test.mjs` ran against actual mounted app modules and actual bundled CodeMirror at 1366x900 and 390x844. It held initial file reads and local writes, checked a second loaded same-file Text window, an unrelated file, a busy Save menu, shortcut and agent command, Save As dialog cancellation, newer Text edits remaining dirty, Calculator held read/write failure, release when a Text view closes, and a separately held simulated background sync that did not disable Save. Storage, account, picker and prompts were test doubles; the write hold is deliberately non-cooperative and does not prove cancellation of an already dispatched backend write. No real signed backend, physical phone, actual background server sync, or all-app coverage is claimed. Primitive Node tests separately cover claim and abort semantics.

Example isolated fixture preparation (use private output and a free port):

```sh
PATH=/tmp/codi-files-move-node/bin:$PATH
ESBUILD=/tmp/codi-webos-cad-merge/active-system/tools/app-builder/node_modules/esbuild/bin/esbuild
mkdir -p /tmp/codi-docops-browser
"$ESBUILD" apps/system/text/index.mjs --bundle --format=esm --loader:.css=empty --outfile=/tmp/codi-docops-browser/text.mjs
"$ESBUILD" apps/system/calculator/index.mjs --bundle --format=esm --loader:.css=empty --outfile=/tmp/codi-docops-browser/calculator.mjs
"$ESBUILD" /tmp/codi-webos-cad-merge/apps/system/codemirror/index.mjs --bundle --format=esm --outfile=/tmp/codi-docops-browser/codemirror.mjs
cp active-system/assets/desktop/{app-instance,document-operations}.mjs /tmp/codi-docops-browser/
cp tests/fixtures/document-operations-apps.html /tmp/codi-docops-browser/index.html
python3 -m http.server 19962 --bind 127.0.0.1 --directory /tmp/codi-docops-browser
# In another terminal, with a private Chromium process:
PUPPETEER_CORE_PATH=/tmp/codi-occt-release-control/node_modules/puppeteer-core TMPDIR=/home/dflanag3/snap/chromium/common node tests/document-operations-apps-browser.test.mjs
```

The test closes its own Chromium. Stop the fixture server after testing. It is not a production build, and the CodeMirror dependency source must be matched to the target release before using it as release evidence.

The tested temporary bundle SHA-256 values were Text `047096e38c22f82f2f59dacc75855a13a786a517e0aa6c9bfc68d0faa2f27d4b`, Calculator `c5c97d20f015362e1ab6de9a65a74c7f6bd6dfe8950925f077f81649e20567dc`, CodeMirror `69c6a048e6fcf7a434d112ecb13f465abe882b42dcbb41a32559f43277317888`, app-instance `e26d7a4150321a3c95cb9c33846ee9ff006c633a8a2c883085133efcd8b88f9b`, and controller `168eb86fc69f20ffa027a97aef8a22d2f2282c9ad82432019d0e4e41472ab854`.
