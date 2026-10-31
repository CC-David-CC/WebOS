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

`tests/fixtures/avr-compiler-probe/patch-candidate.py` applies three **hash-checked research patches** to that pinned release's browser example and `recipe.js`: include the extensionless header, stop on recognized compiler-error diagnostics, and provide the original sketch as a virtual file for accurate source lines. The error check is an English-diagnostic heuristic because the example's Emscripten exit-status handling did not reliably expose the nonzero compiler status. It is not a comprehensive error-detection guarantee; successful-build warnings are not yet surfaced.

The patched worker rejected a deliberately invalid sketch with the correct source line, accepted a warning containing the word `error`, and compiled a sketch using C++ `new` whose HEX drove the simulated LED. `tests/avr-candidate-diagnostics.test.mjs` repeats these checks on localhost. To prepare it, copy the tagged `examples/arduino-web/arduino-pipeline.js` and `index.html` into a disposable served directory, extract the hash-verified release into its `dist-web/`, run `python3 tests/fixtures/avr-compiler-probe/patch-candidate.py DISPOSABLE_DIRECTORY`, copy `tests/fixtures/avr-compiler-probe/worker.js` there as `probe-worker.js`, and build `arduino-simulator` under its `simulator/` directory. Serve only on loopback, start disposable Chromium debugging, and run the test with `CODI_AVR_PROBE_URL` and `CODI_TEST_CDP` as needed. The patch script refuses changed inputs.

These changes are not part of the desktop or live site. Packaging, exact corresponding-source verification, useful warnings, robust exit status, cancellation, resource bounds and account-backed sketch integration still need to be completed before release.
