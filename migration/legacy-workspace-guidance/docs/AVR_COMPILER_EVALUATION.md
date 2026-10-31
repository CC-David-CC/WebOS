# Browser-local AVR compiler research

Arduino Simulator currently runs compiled ATmega328P HEX but does not compile sketches. The following is **local research, not an enabled feature**. It does not establish physical-hardware behavior or the suitability of either toolchain for distribution.

On 2026-10-31, Chromium 155 on this workstation compiled a simple Uno sketch that sets pin 13 high. The actual generated HEX was loaded into this project's existing AVR8js worker, which reported the simulated LED on. The source included `Arduino.h` for the first candidate; the second candidate's sketch preprocessor supplies it. These were isolated localhost tests with no compilation on the server.

| Candidate | Local result | Outstanding |
| --- | --- | --- |
| [`@horang-corp/avr-gcc-wasm` 0.2.0](https://github.com/horang-corp/avr-gcc-wasm/tree/e3a563f765b041623734991125d5640c7e56053e) | Real C++/AVR build in its own worker, about 1.04 s for this one small sketch; 5,072 flash bytes; simulated LED on. A deliberately invalid sketch failed and included a compiler error, although the leading message misleadingly reported a link failure. | npm tarball is about 11 MB compressed / 55 MB unpacked. Its [notices](https://github.com/horang-corp/avr-gcc-wasm/blob/e3a563f765b041623734991125d5640c7e56053e/THIRD_PARTY_NOTICES.md) identify GPL tool binaries and say corresponding source, patches and build scripts should accompany distribution. The inspected repository did not establish an explicit license for its own wrapper or contain a complete recipe for rebuilding those particular WASM tool binaries. Verify both before shipping. |
| [`wasm-toolchains` avr-v1.0.0](https://github.com/begeistert/wasm-toolchains/tree/23058387b320a133f36c701d55c5cde420caac42) | Its released build compiled the same sketch and the resulting HEX drove the simulated LED. The upstream example ran on the page thread; an experimental wrapper ran it in a worker in about 13.5 s while the page continued ticking. An invalid sketch failed, but reported missing `setup`/`loop` at link rather than the useful syntax error. | Release tar is about 107 MB uncompressed. Source and build recipes are public under GPL-3.0-or-later; review the exact release's corresponding sources, notices and reproducibility before redistribution. The build recipe includes mutable base images and package inputs. Improve diagnostics, package on-demand assets and run the compiler in an owned cancellable worker before considering the desktop integration. |

These are individual warm-cache observations on one machine, not a controlled benchmark or a phone/network measurement. The candidates use different core build strategies and outputs. No comparison to v86 compilation has been made. The current guest initramfs does not contain `avr-gcc`, `avr-as`, `avr-ld`, `avr-objcopy` or `apt-get`; using the v86 route would require a deliberate guest toolchain build and memory/performance tests.

## Repeat the local probe

The npm archive used had SHA-256 `88e724b33960d0f12116a31b1a6dbd4a447747f0262e1d095d4f1946464e0896`. The second release `avrwasm.tar` had SHA-256 `639a745994b00eb8d806f80c2302056f76403c9dc737df0676da81418c7ddd17`, matching its release catalog. Its annotated tag resolves to commit `23058387b320a133f36c701d55c5cde420caac42`. Verify source and archive contents before extracting or executing third-party code.

Prepare a disposable directory served **only on loopback** with:

- `package/`: extracted npm package above;
- `simulator/`: a locally built `arduino-simulator` public-app bundle;
- `test.html` and `test.mjs`: copy from `tests/fixtures/avr-compiler-probe/`;
- `alt-web/index.html` and `alt-web/arduino-pipeline.js`: the tagged upstream example; `alt-web/dist-web/`: extracted, hash-checked release; `alt-web/probe-worker.js`: copy of our `tests/fixtures/avr-compiler-probe/worker.js`.

Run `python3 -m http.server 18289 --bind 127.0.0.1` in that directory and start a disposable Chromium debugging endpoint on `127.0.0.1:19288`. From SIMPLIFIED, run `node tests/avr-compiler-probe.test.mjs`. `CODI_AVR_PROBE_URL` and `CODI_TEST_CDP` override those endpoints. This is a research harness with third-party executable code; it is not an authenticated desktop or release test. Remove the disposable assets after use; generated toolchains and dependencies do not belong in Git.

Next implementation work is to select a source-complete, distributable toolchain, preserve appropriate notices and source materials, integrate its compiler into a bounded per-window worker, surface useful errors and cancellation, and exercise My files → edit sketch → compile → simulate → save source/HEX → fresh-session reopen. Test independent windows, account switching, resource limits and real phone behavior. Benchmark browser compilation against an appropriately built v86 toolchain before claiming a speed comparison.

## Candidate diagnostic correction (local research)

A closer test of `avr-v1.0.0` found that the upstream browser example continued after `cc1plus` had printed errors and had emitted an empty or partial assembly file. Even the original successful LED test had silently skipped Arduino `new.cpp`: its extensionless `new` header was present in the release manifest but omitted by the example's file filter. The linker then failed to report sketch syntax errors clearly, or could succeed if the missing core code was unused.

`tests/fixtures/avr-compiler-probe/patch-candidate.py` applies three **hash-checked research patches** to that pinned release's browser example and `recipe.js`: include the extensionless header, invoke each tool explicitly and check its numeric exit status, and provide the original sketch as a virtual file for accurate source lines. The pinned assembler, linker, archiver and objcopy JavaScript wrappers did not expose `callMain`, so the research patch adds that export after verifying each wrapper hash. Successful-build warnings are not yet surfaced.

The patched worker rejected a deliberately invalid sketch with the correct source line, rejected a bad assembler opcode and an unresolved linker symbol using their nonzero exit statuses, accepted a warning containing the word `error`, and compiled a sketch using C++ `new` whose HEX drove the simulated LED. `tests/avr-candidate-diagnostics.test.mjs` repeats these checks on localhost. To prepare it, copy the tagged `examples/arduino-web/arduino-pipeline.js` and `index.html` into a disposable served directory, extract the hash-verified release into its `dist-web/`, run `python3 tests/fixtures/avr-compiler-probe/patch-candidate.py DISPOSABLE_DIRECTORY`, copy `tests/fixtures/avr-compiler-probe/worker.js` there as `probe-worker.js`, and build `arduino-simulator` under its `simulator/` directory. Serve only on loopback, start disposable Chromium debugging, and run the test with `CODI_AVR_PROBE_URL` and `CODI_TEST_CDP` as needed. The patch script refuses changed inputs.

These changes are not part of the desktop or live site. Packaging, exact corresponding-source verification, useful warnings, broader tool/exit tests, cancellation, resource bounds and account-backed sketch integration still need to be completed before release.

## Packed-input worker and generic app-bundle probe

The upstream browser example requests hundreds of individual headers and runtime files. For local research, `tests/fixtures/avr-compiler-probe/pack-inputs.py` puts the pinned candidate's manifest, headers, core, libraries and link inputs into one bounded gzip-compressed indexed asset. For this release, 429 files / 30,118,220 bytes became 4,934,010 bytes. This is only the input archive: the compiler tools are additional assets. The complete isolated Arduino app bundle, including the tools, was 48.22 MiB before HTTP compression. Nothing loads until a consumer creates the compiler worker.

`archive-worker.js` validates the input index and bounds decompression to 64 MiB, rejects sketches over 128 KiB, serves the packed input bytes to the compiler inside the worker, and allows no external fetches. It loads the pinned tools from same-origin files, runs the patched pipeline once, and can be terminated by its owner. `avr-archive-worker.test.mjs` exercised valid and invalid code, the actual AVR8js simulator, the size limit, worker termination and page responsiveness. `avr-worker-concurrency.test.mjs` terminated one compiling worker while another finished and drove the LED. Both passed against a loopback server with the desktop's restricted CSP; these do not establish real-device resource use or a production timeout policy.

`stage-candidate.py` makes a **research-only** copy of Arduino Simulator, verifies the current candidate asset hashes, and declares one compiler worker and 11 static assets through the existing generic app manifest. The regular app builder produced 28 files, bundle SHA-256 `61c559756e9c0973bb4e4948532896a1d79ca1bf9d41ae00e4b3d240c04d9cae`; a changed asset was refused before staging. An isolated registered-account desktop test (`tests/avr-bundled-worker.test.mjs`) loaded that exact bundle with the normal desktop CSP, compiled a valid and invalid sketch, and ran valid firmware in AVR8js. This test calls the worker directly; it does **not** yet provide a student-facing sketch editor or prove the complete My files workflow.

For reproducibility, prepare the patched candidate as above, run `pack-inputs.py DIST_WEB_DIRECTORY DISPOSABLE_WEB_DIRECTORY/compiler-inputs.data`, and copy `archive-worker.js` into that directory. `serve-research.py DISPOSABLE_WEB_DIRECTORY` serves it only on loopback with the restricted CSP. To test generic packaging, run `stage-candidate.py apps/system/arduino-simulator DISPOSABLE_WEB_DIRECTORY NEW_APP_DIRECTORY`, build the resulting app through `build-public-apps.py`, and start an isolated local desktop using that bundle. Do not point these tests at the live site. Archive bytes are hash-pinned by the research staging script; a different gzip/zlib implementation may need deliberate revalidation.

This is not a production distribution. The source and license materials for the exact compiler and runtime still need a reviewed, complete distribution path, and the UI must own cancellation, timeout, state, warnings and account-backed source/HEX saves. No toolchain binaries are committed.

### Isolated sketch editor experiment

The research staging script also overlays `sketch-editor.mjs` onto a disposable copy of Arduino Simulator. It provides an editable Blink sketch, open/save `.ino`, a cancellable worker build with a two-minute timeout, compiler output and automatic simulation of a successful current build. Editing during a build prevents an older result from being run. Firmware HEX and serial controls remain available. It is not part of the shipped app.

`tests/avr-sketch-research.test.mjs` uses an isolated registered desktop and the real packaged compiler and AVR simulator; its file service is a **mock**, so it does not establish real browser/server sync or account isolation. It exercises save/reopen, compilation and simulated LED, compiler diagnostics, cancellation, disposal, stale-build handling, and controls at desktop and narrow viewport sizes using programmatic clicks (not physical touch). A subsequent isolated real-account desktop test (`tests/avr-sketch-account-research.test.mjs`) verified the sketch close warning, browser-to-server sync, reopening in a fresh phone-sized browser context, separate-account isolation, real compilation, simulated LED, editing during an in-flight save, and a file arriving while the shared picker was open. The candidate still needs additional conflict and account-switch race tests, a fuller accessibility and physical-phone test, dependency/source and license review, and production integration before release. The example runs on a simulated Uno and does not validate physical hardware.

The shared My files picker now subscribes while open and refreshes its current directory after file changes, then unsubscribes on close. This was checked in the isolated account test; the fix is source-only and has not been deployed. An initial picker regression run used a preview staged before the fix, failed as expected, and passed after restarting the isolated preview with the changed frontend.

The shared picker update was refined after a 4K-sized test encountered a row being replaced during a redundant sync notification. In isolated account tests it now retains unchanged rows and focus, restores focus where possible after a real list change, and releases its subscription on abort or selection at desktop, narrow and 4K viewport sizes. The Text upload/open/edit/sync/reopen regression passed with the updated picker. These checks do not establish physical touch behavior, and this source change has not been deployed.

The shared picker fix was subsequently deployed in static release `50239271e19c042197b65efd7a1c7856f6860b60dd152d25f7d4b902b1e39242`. A signed-in public phone-sized browser smoke exercised picker update and cleanup using mocked file rows; real file service tests remain local. The compiler and sketch editor remain research only.

### Sketch save and account-switch research — 2026-10-31

The isolated sketch editor captures its source, destination and previous version before storage waits. Opening a different sketch during a save no longer attaches that earlier save to the newly opened document. `tests/avr-sketch-save-race-research.test.mjs` ran against real isolated registered-account storage at desktop, emulated-phone and 4K viewport sizes. It held storage, changed the filename and source, opened another sketch while a write was held, verified a competing local file was not overwritten, and switched accounts during a held save while preserving both accounts' files. The full isolated real-account test also compiled a sketch through the actual browser worker and ran the HEX in AVR8js after this change. These are research checks; they do not enable the compiler on the live site or establish physical phone behavior.

Corresponding-source provenance still needs work before distribution: at the pinned candidate commit, `src/avr-gcc/Dockerfile` fixes GCC 15.2.0 but pulls Debian target runtime packages without exact versions, while `src/binutils/Dockerfile` clones the moving `binutils-2_45-branch`. These recipes and their build environment do not by themselves prove the exact source of the published release artifacts. Review and preserve the exact toolchain source, dependencies, licenses and build instructions; do not represent these tests as permission to distribute the compiled toolchain.

### Partial release-source audit — 2026-10-31

The published [`avr-v1.0.0` release](https://github.com/begeistert/wasm-toolchains/releases/tag/avr-v1.0.0) identifies commit `23058387b320a133f36c701d55c5cde420caac42`. Its published archive hash matches our research copy. `tests/fixtures/avr-compiler-probe/audit-release-sources.py` checks that hash and revision, reads the archive without extracting it, and compares manifest-listed files against the committed Git blobs: all 47 Arduino core files and all nine distributed library source files match, covering EEPROM, SPI, SoftwareSerial and Wire. The check rejects an archive with a different hash. This proves those source-file matches only, not complete corresponding source or permission to distribute the full bundle.

The archive's `avr/version.h` reports avr-libc 2.0.0, and the assembler/linker JavaScript contains a Binutils 2.45.1 version string. Those version labels do not identify the exact source commits or distribution patches. The pinned [release workflow](https://github.com/begeistert/wasm-toolchains/blob/23058387b320a133f36c701d55c5cde420caac42/.github/workflows/release-avr.yml) uses moving branch/package inputs and Docker build caches; its public run `28085465875` is associated with the tagged commit, but unauthenticated GitHub log download returned HTTP 403. A cache hit can also complicate provenance. The archive contains no complete license or source bundle. Exact compiler/binutils source, system-library package sources/patches, associated notices, and a reviewed distribution method remain outstanding. Do not deploy the compiler on the strength of this partial audit.

Repeat with `python3 tests/fixtures/avr-compiler-probe/audit-release-sources.py /path/to/avrwasm.tar /path/to/wasm-toolchains-checkout`; the checkout must be at the pinned revision. Generated archives and toolchains are not committed.

### Sketch conflict handling — isolated research

The research-only sketch editor now keeps a separate file-change notice while
the student builds and runs code. If a mirror write returns a conflict, it
reports that condition and keeps the sketch marked dirty; saving an earlier
sketch after switching documents also reports an immediate conflict without
attaching the old save to the new document. The watcher is removed on close.
`tests/avr-sketch-conflict-research.test.mjs` uses the hash-checked research
bundle and isolated account service to arrange competing server and local
writes, verify both copies, build and run the retained draft on AVR8js, save a
separate copy, reopen it in a fresh session and check subscription cleanup. It
passed at local desktop, emulated-phone and 4K sizes. Existing isolated
account-switch/save-race and mock-storage compile/diagnostics tests also passed.
These are research checks only. Physical devices, full compatibility and the
compiler's exact corresponding-source and distribution requirements remain
unverified; the research compiler has not been deployed.

### Runtime-package byte audit — 2026-10-31

A narrower piece of the provenance is now identified. The 326 uncompressed
`sysroot/avr/` include and library files in the pinned `avrwasm.tar` match
byte-for-byte the corresponding files in Ubuntu Jammy's
[`avr-libc` 1:2.0.0+Atmel3.6.2-3 package](https://packages.ubuntu.com/jammy/avr-libc).
The ten bundled AVR5/AVR6 linker scripts match the corresponding files in its
[`binutils-avr` 2.26.20160125+Atmel3.6.2-4 package](https://packages.ubuntu.com/jammy/binutils-avr).
Compressed `.br` copies and the GCC runtime/WASM executables were not covered.
A byte match does not prove which repository the producer used; for example,
the Uno libc archive's 296 member contents also match Debian Bookworm's package,
although archive metadata differs. Ubuntu's Jammy archive itself is an exact
archive-byte match for that file.

The Ubuntu package hashes were authenticated against Jammy's signed `InRelease`
using the installed Ubuntu archive keyring (good signature by 2018 key ID
`871920D1991BC93C`). The signed `universe/binary-amd64/Packages.xz` SHA-256 was
`d29cb24c93fec5f43255706bce7eb46d4779952039d8c68ac1bb14a6f3655ce2`;
the `avr-libc` `.deb` hash is
`984d0c38ccdd08fd10761da5e7eb75f9f9572d9a804bc1c4a649051c3aaed09b`
and the `binutils-avr` `.deb` hash is
`ebae1564675109969b3dcc6a6d4cb73ee445997e1dc2be05717cdc1d01453e0c`.
The signed `universe/source/Sources.xz` hash was
`8f73d18065a4f05ee7362c50553ea4b26ca2b4b3786472676b6b1ee58b4cff72`.
The following source files and packaging patches were fetched from Ubuntu's
archive and checked against that signed index; these are candidate source
materials for the matching package contents, not a complete compiler source bundle:

| Package | File | SHA-256 |
| --- | --- | --- |
| avr-libc | `avr-libc_2.0.0+Atmel3.6.2-3.dsc` | `ee90f9b10ebfb5536b133df31dd89e25fda0ea13b6ee746b6dee8d6b919af8fc` |
| avr-libc | `avr-libc_2.0.0+Atmel3.6.2.orig.tar.gz` | `99f7218bd1fda680ad60d15d9a71cce7376201c6dce28acd813ea082009045eb` |
| avr-libc | `avr-libc_2.0.0+Atmel3.6.2-3.diff.gz` | `b28aae79b573dbc176770895a7962064b1306638df5fc1bc96b3d997cebc5508` |
| binutils-avr | `binutils-avr_2.26.20160125+Atmel3.6.2-4.dsc` | `f48ffa57e7d1f6a9c9be201ba74e41a460ae8ba3c2d35738562c7248a5b10e96` |
| binutils-avr | `binutils-avr_2.26.20160125+Atmel3.6.2.orig.tar.gz` | `a6bb9873cccaa39dc3a4ba821aa2274c3291bf397587aaf130d4faeb70ed7049` |
| binutils-avr | `binutils-avr_2.26.20160125+Atmel3.6.2-4.diff.gz` | `fafe85877eb8c97d25e5e493efcdc8ecaf05913219a185e2c09e39de0d1cf6b4` |

The package source directories are
`https://archive.ubuntu.com/ubuntu/pool/universe/a/avr-libc/` and
`https://archive.ubuntu.com/ubuntu/pool/universe/b/binutils-avr/`.
Package copyright notices are distributed inside the packages; individual
source-file notices and obligations still require review for any release.

Repeat the byte comparison without extracting archives using:

```
python3 tests/fixtures/avr-compiler-probe/audit-runtime-packages.py \
  /path/to/avrwasm.tar /path/to/avr-libc.deb /path/to/binutils-avr.deb
```

The script pins all three input hashes and rejects a substituted package. It
requires `dpkg-deb` and checks exactly 326 library/header files and ten linker
scripts. It does **not** establish exact sources or reproducibility for GCC,
its `libgcc`, the WASM Binutils executables, Emscripten or their dependencies.
Those items, corresponding-source review and a distribution plan remain open;
this does not authorize deploying the research compiler.
