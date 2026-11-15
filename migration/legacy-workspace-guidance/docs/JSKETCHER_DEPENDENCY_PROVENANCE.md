# jSketcher local candidate: dependency provenance research

2026-11-02. This is evidence for the **local-only** 117-asset candidate whose
`BUILD-RECEIPT.json` SHA-256 is
`e9825ddbd733ebba05452b591fc92440a2894dbfcaa92adb8464cb7e1539d76c`, built
from fork commit `bb9648c750cda5e85c5d516fc28aa8fe76e2f569`. It is not a
complete software bill of materials, legal opinion, or approval to deploy.
The webpack module-ID scan is a heuristic: it found 45 candidate npm package
roots and no unmatched IDs, but does not prove execution, cover all webpack
loader inputs or cover separately served `web/lib` assets. Exact npm tarballs
were downloaded from the registry without executing their contents and compared
with the matching local package files. The package metadata and supplied
notices are in the candidate's `dependency-notices.zip`; that archive also
includes build-only packages and flags missing notices for review.

## Packages without standalone notices in their published tarballs

| Package and runtime file | Evidence | Notice status and remaining work |
| --- | --- | --- |
| `@icons/material` 0.2.4, `CheckIcon.js` and `UnfoldMoreHorizontalIcon.js` | Their npm file SHA-256 values are `84d3bd80ad91d5a57461b748ef08c3a998f4be9ecf8ed635aaa591cf2412de9d` and `69b678ce8fe312211bca124ea26e8726bba3386f581b0f9d330fafdf9adca907`; both match the local installed files. npm `gitHead` and [upstream v0.2.4](https://github.com/at-icons/material/tree/47a3170f27d1c1061e69b1b68f7dfd8d4d7845f3) resolve to `47a3170f27d1c1061e69b1b68f7dfd8d4d7845f3`. Its source JSX path data for these icons matches `mdi-svg` 2.2.43 SVG path data; the package declares `mdi-svg` as a range, so this does not establish the exact generation install. | Package metadata says MIT but its tarball and tagged tree have no standalone license text. `mdi-svg` 2.2.43's upstream commit `3d4b88fe29957905217a95577f855c4fa44d1a71` includes an MIT [LICENSE](https://github.com/Templarian/MaterialDesign-SVG/blob/3d4b88fe29957905217a95577f855c4fa44d1a71/LICENSE): SHA-256 `3d3124173572322b4dd2d04a1895e2b20079e473e40bc837189c43f0a5f271ec`; npm's copy differs only by CRLF line endings. This is useful icon-source evidence; review the wrapper and icon attribution before deciding what to ship. |
| `clipper-lib` 6.2.1, `clipper.js` | npm file SHA-256 `7b5f0993132342745915a54bebabaed842b7b5e13fb1f8f9fcbcefc5311c5845` is byte-identical to local installation and [upstream tag 6.2.1](https://github.com/junmer/clipper-lib/blob/f6d03c790a9ad81c7206a1c848d4c35ba514ac56/clipper.js), commit `f6d03c790a9ad81c7206a1c848d4c35ba514ac56`. | Source header and README identify Boost Software License 1.0, but no complete license file accompanies the tarball. The [Boost license text](https://www.boost.org/LICENSE_1_0.txt) fetched for review has SHA-256 `c9bff75738922193e67fa726fa225535870d2aa1059f91452c411736284ad566`. Include the source attributions and reviewed license text as appropriate. |
| `emitter-component` 1.1.1, `index.js` | npm file SHA-256 `d2e2f52d26bf98e8fe2e5bbe1d367b7a8da61397a670c8a24a380447463159ce` matches installed file and [upstream tag 1.1.1](https://github.com/component/emitter/tree/a5631018f6984f585b44c0ac7982b0ff9686086f), commit `a5631018f6984f585b44c0ac7982b0ff9686086f`. | That 2013 tag has neither declared license nor standalone notice. A [2014 descendant](https://github.com/component/emitter/commit/2999c522a07ba3a95106530e1c1e194d2c7a266c) adds MIT `LICENSE`, SHA-256 `0f0b408b8b871d983e767528c6dc51e0ad7efaa022890c449fe2e1ee24dbb7`, without changing `index.js`. Review applicability to the earlier version; do not infer clearance solely from the later file. |
| `regenerator-runtime` 0.10.5, `runtime.js` | npm file SHA-256 `c79f77316587802b9788b06f4b1a69caac03367a20ee27c984e3767082aaa9ca` exactly matches [version-bump commit](https://github.com/facebook/regenerator/tree/74c76264bf3be1f2bf60082c2e03dec522c96816) `74c76264bf3be1f2bf60082c2e03dec522c96816`. | Its npm `package.json` says MIT, but the runtime header references the repository's BSD-style `LICENSE` and `PATENTS`. At that exact commit their SHA-256 values are `acacd15e10610fc0aca63c3e09ba85910c302f17f4175ec3e5bb76ab5cba0de8` and `5663cbf7746947ee91d02c6d45163694238bd07ceadcfc3f6dab2fbe23b85b86`. Preserve both and resolve the discrepancy rather than asserting MIT alone. |
| `stream` 0.0.2, `index.js` | npm file SHA-256 `efc3877be3bfd5173024bff07b42dd1fa8a0bc1f4615e37f1d299c2dbb3bd044` matches the local installation and [upstream v0.0.2](https://github.com/juliangruber/stream/tree/3faf89f7b8770fe41b41b6f0bb1e08bb9367fc9f) commit `3faf89f7b8770fe41b41b6f0bb1e08bb9367fc9f`. | `index.js` contains a Joyent/Node contributors MIT-style notice. Its README contains a separate Julian Gruber MIT notice; upstream README SHA-256 is `bf8da9e464b8fd963a591893bb290496de06bed507caa0cf306cca79bed83e68`. Both are supplied in the local candidate's supplemental notice evidence. |
| `timers` 0.1.1, `index.js` | npm file SHA-256 `477d35ce3e5332afed82f83b597977317eb32c99e018e6a08053306bccb8ab71` matches installed file and [upstream 0.1.1](https://github.com/popomore/timers/tree/d400ce94b22686faf0b717259040e6b0615250e6), commit `d400ce94b22686faf0b717259040e6b0615250e6`. | npm metadata and README say MIT but contain no full standalone license text. The `browser-xml2js` parser requires `timers.setImmediate`, which this cron-like package does not export; its async mode would fail. The observed jSketcher FCStd import calls `parseString(xml, callback)` with no options, and xml2js defaults to synchronous mode. A real FCStd import and other potential callers remain untested; this does not establish a visible failure or prove safety. |
| `numeric` 1.2.6 | The npm input SHA-256 `5dcaba2016fd237091e3a17b0dc272fb21f0e2b15d7628f95a0ad0cd4cdf4020` equals concatenated `src/numeric.js`, `src/seedrandom.js`, `src/quadprog.js`, and `src/svd.js` from [upstream v1.2.6](https://github.com/sloisel/numeric/tree/656fa1254be540f428710738ca9c1539625777f1), commit `656fa1254be540f428710738ca9c1539625777f1`. The build precompiles this input for CSP; the resulting code is transformed. | The candidate contains the pinned source archive, upstream `license.txt` SHA-256 `0e94aada97f12dee6118064add9170484c55022f5d53206ee4407143cd36ddcd`, and `resources/LICENSE.quadprog` SHA-256 `a96e914967c28cbfed070a5a94fa7c670205a657751fa7dd707df8e922d2d904`. Seedrandom's BSD notice is in its source. The npm tarball omitted the two separate upstream license files. |

## Separately served vendored scripts

- `web/lib/pnltri.js` has SHA-256
  `216d497c825d96a4c03ff387fa80feb0696b063ef8f3d76ab9521a5c6fcd129f`.
  It matches [PNLTRI tag 2.1.1's build](https://github.com/jahting/pnltri.js/tree/72f162d39da3a84c78ff16181940da79f3f50ba9)
  at commit `72f162d39da3a84c78ff16181940da79f3f50ba9` except two
  whitespace-only differences. Upstream build SHA-256 is
  `2cf910fa142d137070a003af93a21d6b11ef0cf4dd53974dd48aa07adbec83be`;
  upstream MIT `LICENSE` SHA-256 is
  `3898350fd0df396d2045f5cabb7c9b52859ca6ec274ff2f6e0d30b3ef97b3a75`.
- `web/lib/diff_match_patch.js` SHA-256
  `aac7655a215d8448d95d9871e8d8a40ac3d9aaf38d81ab2ccc43c1cd267b8fa3`
  is byte-identical to the [initial Google GitHub import](https://github.com/google/diff-match-patch/tree/0ae308daa77aeddb089cd6b7b0a443fca026266e),
  commit `0ae308daa77aeddb089cd6b7b0a443fca026266e`. The commit's
  Apache-2.0 `LICENSE` SHA-256 is
  `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`.
  The fork included the identical bytes in 2015, before that 2018 GitHub
  import; the match alone does not establish the exact earlier provenance.
- `web/lib/verb.js` is a modified Haxe-built Verb NURBS library. The current
  candidate SHA-256 is
  `55f13091a656c635d1ebe3931a9b52236c65023549b7b69bc8278362f87686f3`;
  the fork's 2017 first copy differs by 38 insertions and 30 deletions from
  [Verb 2.0.0's generated build](https://github.com/pboyer/verb/tree/1a5c14a9e104feb90ef5a237f9065193bce1e411),
  and its 2018 and 2026 fork changes further modify it. Verb's tagged MIT
  `LICENSE` SHA-256 is
  `ecb6d0b090a248f5e3845fad33da9ed29aa170fd624e107d16a95f0e18b81e01`.
  None of 66 available upstream `build/js/verb.js` history revisions matched
  the fork's first, pre-CSP, or current files byte-for-byte; exact upstream
  build/source and other embedded components remain to be established.
- The setImmediate polyfill embedded in the fork's original `verb.js` is
  identical to [YuzuJS setImmediate source](https://github.com/YuzuJS/setImmediate/tree/36266e8350d12200613be383eeb9fb0df10dd67c)
  commit `36266e8350d12200613be383eeb9fb0df10dd67c` except for its last
  global-object invocation and an additional semicolon. Its source SHA-256
  is `fc5d7a651031397ac7018085503f742b3d78bfceb8de852e70a26f3bda42d1b8`,
  and its `LICENSE.txt` SHA-256 is
  `c4b4ad3a5746f1f5249a6dd90396ec519264e1bb02e01e48a6522c48a3a97cb4`.
  The current fork additionally changes the global invocation and rejects
  string callbacks for CSP.
- The candidate's `web/lib/numeric-1.2.6.js` SHA-256
  `92ea65859a91363757dede0728221f82fe8bf27d169a42236111ffee397406b0`
  matches the verified npm numeric input after CRLF-to-LF normalization.

The embedded entry explicitly loads `verb.js` and `pnltri.js`. The local
candidate also packages the vendored numeric and diff scripts. A text search
found no literal references to their filenames in staged HTML/JS/CSS; that is
not proof that no dynamic access exists. Remove only after a real workflow
review, and keep their notices while distributing those assets.

## Release gate

The candidate's fork, OCCT interpreter and numeric source archives, package
metadata and supplied notices are useful evidence, not a complete corresponding
source package or a legal-clearance statement. In particular, the OCCT npm
package version incorporates interpreter commit
`5efaf53accb45bac475155fc4d5552642c19e91e`, but the exact published WASM has
not been independently reproduced from that source. Resolve the remaining
seven npm notice candidates, bundled external dependencies, runtime behavior
and source obligations before distribution. Obtain an appropriate review of
license and attribution obligations, preserve exact license texts alongside
any distributed binaries, and repeat the inventory against the final build.

## Later local candidate

The experimental host pin was later advanced to `ceac5a1bd1b4b9907963a9b38cbf47eef2384a04` to include the fourth-power correction from [upstream PR #216](https://github.com/xibyte/jsketcher/pull/216) and its regression test. The new local build receipt SHA-256 is `96f8a7178e611c69de33e17ad8a987ec5db7c52a5d0a3cfef7ea06e23312a326`. The detailed inventory above was made against the earlier build; it is not a fresh complete audit of the new bundle. The same provenance and distribution gates remain.
