# Embroidery candidate dependency inventory

Generated from `cargo metadata --offline --locked --filter-platform wasm32-unknown-unknown` for the e5a88e0 candidate source and lockfile. This walks normal and build dependencies from vectorcraft-web; it is a conservative dependency graph, not proof every package is linked into the final WASM. Package license expressions are upstream declarations, not a legal conclusion. Dev-only edges are excluded.

317 packages were found. Upstream NOTICE includes references to epaint default fonts and the Independent JPEG Group. The four font license texts from epaint_default_fonts 0.36.2 are now explicitly packaged under `licenses/epaint-default-fonts-0.36.2/`; the upstream NOTICE includes the IJG binary acknowledgement. Verify the complete notices and applicable license texts for the actual shipped build before release. Apache-2.0 is an available choice for self_cell, which also offers GPL-2.0-only.

## Notice review

The browser package now includes `licenses/RUST_DEPENDENCY_NOTICES.txt`, a
conservative 317-package normal/build dependency notice collection. Its
SHA-256 is `ef95487f79c701aa06342e6c0b0ba0da91ad6d8cb029255c8bbb6686d9adb370`.
The 22 registry packages without root-level notices were matched to exact
`.cargo_vcs_info.json` revisions; the collection includes the upstream license
files from those revisions, including the Codeberg enum-map repository's
`LICENSES` directory. The four additional embedded font license files and
upstream notices remain in the app package. `collect_dependency_notices.py`
records source URLs and individual text hashes to support repeat review.

The candidate's `vendor/corresponding-source.zip` contains the 2,062 tracked
files from the pinned editor checkout, the five patched source files, and seven
reviewed desktop-integration files. Its SHA-256 is
`4c34bcd23a17dc8bf10c4677988352ff91fe09ce8fba6aada63f397e1457729c`.
A separate adjacent `vendor/prepare.py.txt` contains the exact packaging
script, which pins the archive. Generation was repeated with byte-identical
output, and a checkout with the older patch was rejected. The archive omits
dependency source and caches; Cargo.lock and the notice collection identify
them. It is not yet deployed.

This collection is evidence of included dependency license texts, not a legal
opinion or proof that every nested asset, modification notice, or distribution
obligation has been identified. Review bundled assets and source availability
against the actual build before publishing the candidate.

| Package | Version | Declared license |
| --- | --- | --- |
| accesskit | 0.24.1 | MIT OR Apache-2.0 |
| adler2 | 2.0.1 | 0BSD OR MIT OR Apache-2.0 |
| aes | 0.8.4 | MIT OR Apache-2.0 |
| ahash | 0.8.12 | MIT OR Apache-2.0 |
| alloc-no-stdlib | 2.0.4 | BSD-3-Clause |
| alloc-stdlib | 0.2.4 | BSD-3-Clause |
| arrayref | 0.3.9 | BSD-2-Clause |
| arrayvec | 0.7.8 | MIT OR Apache-2.0 |
| autocfg | 1.5.1 | Apache-2.0 OR MIT |
| base64 | 0.22.1 | MIT OR Apache-2.0 |
| base64 | 0.23.1 | MIT OR Apache-2.0 |
| bit-set | 0.10.0 | Apache-2.0 OR MIT |
| bit-vec | 0.9.1 | Apache-2.0 OR MIT |
| bitflags | 1.3.2 | MIT/Apache-2.0 |
| bitflags | 2.13.2 | MIT OR Apache-2.0 |
| block-buffer | 0.10.4 | MIT OR Apache-2.0 |
| brotli | 8.0.4 | BSD-3-Clause AND MIT |
| brotli-decompressor | 5.0.3 | BSD-3-Clause/MIT |
| bumpalo | 3.20.3 | MIT OR Apache-2.0 |
| bytemuck | 1.25.2 | Zlib OR Apache-2.0 OR MIT |
| bytemuck_derive | 1.12.1 | Zlib OR Apache-2.0 OR MIT |
| byteorder-lite | 0.1.0 | Unlicense OR MIT |
| cfg-if | 1.0.5 | MIT OR Apache-2.0 |
| cfg_aliases | 0.2.2 | MIT |
| cipher | 0.4.4 | MIT OR Apache-2.0 |
| codespan-reporting | 0.13.1 | Apache-2.0 |
| color | 0.3.3 | Apache-2.0 OR MIT |
| color_quant | 1.1.0 | MIT |
| core_maths | 0.1.1 | MIT |
| craft-docpath | 0.1.0 | MIT OR Apache-2.0 |
| craft-pdf | 0.1.0 | MIT OR Apache-2.0 |
| craft-ui | 0.1.0 | MIT OR Apache-2.0 |
| crc32fast | 1.5.2 | MIT OR Apache-2.0 |
| crossbeam-channel | 0.5.17 | MIT OR Apache-2.0 |
| crossbeam-deque | 0.8.8 | MIT OR Apache-2.0 |
| crossbeam-epoch | 0.9.21 | MIT OR Apache-2.0 |
| crossbeam-utils | 0.8.23 | MIT OR Apache-2.0 |
| crypto-common | 0.1.7 | MIT OR Apache-2.0 |
| cursor-icon | 1.2.0 | MIT OR Apache-2.0 OR Zlib |
| data-url | 0.3.2 | MIT OR Apache-2.0 |
| digest | 0.10.7 | MIT OR Apache-2.0 |
| displaydoc | 0.2.7 | MIT OR Apache-2.0 |
| document-features | 0.2.12 | MIT OR Apache-2.0 |
| dpi | 0.1.2 | Apache-2.0 AND MIT |
| ecolor | 0.36.2 | MIT OR Apache-2.0 |
| eframe | 0.36.2 | MIT OR Apache-2.0 |
| egui | 0.36.2 | MIT OR Apache-2.0 |
| egui-wgpu | 0.36.2 | MIT OR Apache-2.0 |
| egui_extras | 0.36.2 | MIT OR Apache-2.0 |
| egui_glow | 0.36.2 | MIT OR Apache-2.0 |
| either | 1.18.0 | MIT OR Apache-2.0 |
| emath | 0.36.2 | MIT OR Apache-2.0 |
| enum-map | 2.7.3 | MIT OR Apache-2.0 |
| enum-map-derive | 0.17.0 | MIT OR Apache-2.0 |
| epaint | 0.36.2 | MIT OR Apache-2.0 |
| epaint_default_fonts | 0.36.2 | (MIT OR Apache-2.0) AND OFL-1.1 AND Ubuntu-font-1.0 |
| equivalent | 1.0.2 | Apache-2.0 OR MIT |
| euclid | 0.22.14 | MIT OR Apache-2.0 |
| fastrand | 2.5.0 | Apache-2.0 OR MIT |
| fax | 0.2.7 | MIT |
| fdeflate | 0.3.7 | MIT OR Apache-2.0 |
| fearless_simd | 0.4.1 | Apache-2.0 OR MIT |
| flate2 | 1.1.10 | MIT OR Apache-2.0 |
| float-cmp | 0.9.0 | MIT |
| foldhash | 0.1.5 | Zlib |
| foldhash | 0.2.0 | Zlib |
| font-types | 0.11.3 | MIT OR Apache-2.0 |
| font-types | 0.12.5 | MIT OR Apache-2.0 |
| fontdb | 0.24.0 | MIT |
| futures-core | 0.3.34 | MIT OR Apache-2.0 |
| futures-macro | 0.3.34 | MIT OR Apache-2.0 |
| futures-sink | 0.3.34 | MIT OR Apache-2.0 |
| futures-task | 0.3.34 | MIT OR Apache-2.0 |
| futures-util | 0.3.34 | MIT OR Apache-2.0 |
| generic-array | 0.14.7 | MIT |
| getrandom | 0.3.4 | MIT OR Apache-2.0 |
| gif | 0.14.2 | MIT OR Apache-2.0 |
| glifo | 0.2.0 | Apache-2.0 OR MIT |
| glifo | 0.3.0 | Apache-2.0 OR MIT |
| glow | 0.17.0 | MIT OR Apache-2.0 OR Zlib |
| guillotiere | 0.7.0 | MIT/Apache-2.0 |
| half | 2.7.1 | MIT OR Apache-2.0 |
| harfrust | 0.12.0 | MIT |
| harfrust | 0.13.3 | MIT |
| hashbrown | 0.15.5 | MIT OR Apache-2.0 |
| hashbrown | 0.17.1 | MIT OR Apache-2.0 |
| hayro-ccitt | 0.3.0 | Apache-2.0 OR MIT |
| hayro-cmap | 0.1.0 | Apache-2.0 OR MIT |
| hayro-interpret | 0.7.0 | Apache-2.0 OR MIT |
| hayro-jbig2 | 0.3.0 | Apache-2.0 OR MIT |
| hayro-jpeg2000 | 0.3.5 | Apache-2.0 OR MIT |
| hayro-postscript | 0.1.0 | Apache-2.0 OR MIT |
| hayro-syntax | 0.7.2 | Apache-2.0 OR MIT |
| i_float | 5.0.0 | MIT |
| i_key_sort | 0.12.0 | MIT |
| i_overlay | 9.1.0 | MIT OR Apache-2.0 |
| i_shape | 5.0.0 | MIT |
| i_tree | 0.20.0 | MIT |
| icu_collections | 2.3.0 | Unicode-3.0 |
| icu_locale_core | 2.3.0 | Unicode-3.0 |
| icu_locale_fallback | 2.3.0 | Unicode-3.0 |
| icu_locale_fallback_data | 2.3.0 | Unicode-3.0 |
| icu_provider | 2.3.1 | Unicode-3.0 |
| icu_segmenter | 2.3.0 | Unicode-3.0 |
| icu_segmenter_data | 2.3.0 | Unicode-3.0 |
| image | 0.25.10 | MIT OR Apache-2.0 |
| image-webp | 0.2.4 | MIT OR Apache-2.0 |
| imagesize | 0.13.0 | MIT |
| imagesize | 0.14.0 | MIT |
| imagesize | 0.15.0 | MIT |
| indexmap | 2.14.2 | Apache-2.0 OR MIT |
| inout | 0.1.4 | MIT OR Apache-2.0 |
| itertools | 0.15.0 | MIT OR Apache-2.0 |
| itoa | 1.0.18 | MIT OR Apache-2.0 |
| jpeg-encoder | 0.6.1 | (MIT OR Apache-2.0) AND IJG |
| js-sys | 0.3.106 | MIT OR Apache-2.0 |
| krilla | 0.8.2 | MIT OR Apache-2.0 |
| kurbo | 0.11.3 | Apache-2.0 OR MIT |
| kurbo | 0.13.1 | Apache-2.0 OR MIT |
| libm | 0.2.16 | MIT |
| linebender_resource_handle | 0.1.1 | Apache-2.0 OR MIT |
| linesweeper | 0.5.0 | MIT OR Apache-2.0 |
| litemap | 0.8.3 | Unicode-3.0 |
| litrs | 1.0.0 | MIT OR Apache-2.0 |
| lock_api | 0.4.14 | MIT OR Apache-2.0 |
| log | 0.4.34 | MIT OR Apache-2.0 |
| md-5 | 0.10.6 | MIT OR Apache-2.0 |
| memchr | 2.8.3 | Unlicense OR MIT |
| miniz_oxide | 0.8.9 | MIT OR Zlib OR Apache-2.0 |
| miniz_oxide | 0.9.1 | MIT OR Zlib OR Apache-2.0 |
| moxcms | 0.8.1 | BSD-3-Clause OR Apache-2.0 |
| naga | 30.0.1 | MIT OR Apache-2.0 |
| naga-types | 30.0.1 | MIT OR Apache-2.0 |
| nohash-hasher | 0.2.0 | Apache-2.0 OR MIT |
| num-traits | 0.2.19 | MIT OR Apache-2.0 |
| once_cell | 1.21.4 | MIT OR Apache-2.0 |
| ordered-channel | 1.2.0 | MIT OR Apache-2.0 |
| ordered-float | 5.5.0 | MIT |
| parking_lot | 0.12.5 | MIT OR Apache-2.0 |
| parking_lot_core | 0.9.12 | MIT OR Apache-2.0 |
| pdf-writer | 0.15.0 | MIT OR Apache-2.0 |
| peniko | 0.6.1 | Apache-2.0 OR MIT |
| percent-encoding | 2.3.2 | MIT OR Apache-2.0 |
| phf | 0.13.1 | MIT |
| phf_generator | 0.13.1 | MIT |
| phf_macros | 0.13.1 | MIT |
| phf_shared | 0.13.1 | MIT |
| pico-args | 0.5.0 | MIT |
| pin-project | 1.1.13 | Apache-2.0 OR MIT |
| pin-project-internal | 1.1.13 | Apache-2.0 OR MIT |
| pin-project-lite | 0.2.17 | Apache-2.0 OR MIT |
| png | 0.17.16 | MIT OR Apache-2.0 |
| png | 0.18.1 | MIT OR Apache-2.0 |
| polycool | 0.4.0 | MIT OR Apache-2.0 |
| potential_utf | 0.1.6 | Unicode-3.0 |
| proc-macro2 | 1.0.107 | MIT OR Apache-2.0 |
| profiling | 1.0.18 | MIT OR Apache-2.0 |
| pxfm | 0.1.30 | BSD-3-Clause OR Apache-2.0 |
| quick-error | 2.0.1 | MIT/Apache-2.0 |
| quote | 1.0.47 | MIT OR Apache-2.0 |
| raw-window-handle | 0.6.2 | MIT OR Apache-2.0 OR Zlib |
| rayon | 1.12.0 | MIT OR Apache-2.0 |
| rayon-core | 1.13.0 | MIT OR Apache-2.0 |
| read-fonts | 0.39.2 | MIT OR Apache-2.0 |
| read-fonts | 0.41.0 | MIT OR Apache-2.0 |
| read-fonts | 0.43.3 | MIT OR Apache-2.0 |
| read-fonts | 0.44.0 | MIT OR Apache-2.0 |
| resvg | 0.45.1 | Apache-2.0 OR MIT |
| rfd | 0.17.2 | MIT |
| rgb | 0.8.53 | MIT |
| roxmltree | 0.20.0 | MIT OR Apache-2.0 |
| roxmltree | 0.21.1 | MIT OR Apache-2.0 |
| rustc-hash | 1.1.0 | Apache-2.0/MIT |
| rustc-hash | 2.1.3 | Apache-2.0 OR MIT |
| rustversion | 1.0.23 | MIT OR Apache-2.0 |
| rustybuzz | 0.20.1 | MIT |
| ruzstd | 0.9.1 | MIT |
| ryu | 1.0.23 | Apache-2.0 OR BSL-1.0 |
| scopeguard | 1.2.0 | MIT OR Apache-2.0 |
| self_cell | 1.3.0 | Apache-2.0 OR GPL-2.0-only |
| serde | 1.0.229 | MIT OR Apache-2.0 |
| serde_core | 1.0.229 | MIT OR Apache-2.0 |
| serde_derive | 1.0.229 | MIT OR Apache-2.0 |
| serde_json | 1.0.151 | MIT OR Apache-2.0 |
| serde_spanned | 1.1.1 | MIT OR Apache-2.0 |
| sf-core | 0.14.0 | MIT OR Apache-2.0 |
| sf-dwg | 0.14.0 | MIT OR Apache-2.0 |
| sf-formats | 0.14.0 | MIT OR Apache-2.0 |
| sf-photo | 0.14.0 | MIT OR Apache-2.0 |
| sha2 | 0.10.9 | MIT OR Apache-2.0 |
| simd-adler32 | 0.3.10 | MIT |
| simplecss | 0.2.2 | Apache-2.0 OR MIT |
| siphasher | 1.0.4 | MIT OR Apache-2.0 |
| skrifa | 0.42.1 | MIT OR Apache-2.0 |
| skrifa | 0.44.0 | MIT OR Apache-2.0 |
| skrifa | 0.47.0 | MIT OR Apache-2.0 |
| slab | 0.4.12 | MIT |
| slotmap | 1.1.1 | Zlib |
| smallvec | 1.16.2 | MIT OR Apache-2.0 |
| smol_str | 0.2.2 | MIT OR Apache-2.0 |
| spin | 0.9.9 | MIT |
| spirv | 0.4.0+sdk-1.4.341.0 | Apache-2.0 |
| stable_deref_trait | 1.2.1 | MIT OR Apache-2.0 |
| static_assertions | 1.1.0 | MIT OR Apache-2.0 |
| strict-num | 0.1.1 | MIT |
| string-interner | 0.19.0 | MIT/Apache-2.0 |
| stringprep | 0.1.5 | MIT/Apache-2.0 |
| subsetter | 0.2.6 | MIT OR Apache-2.0 |
| subtle | 2.6.1 | BSD-3-Clause |
| svgtypes | 0.15.3 | Apache-2.0 OR MIT |
| svgtypes | 0.16.1 | Apache-2.0 OR MIT |
| syn | 2.0.119 | MIT OR Apache-2.0 |
| syn | 3.0.6 | MIT OR Apache-2.0 |
| synstructure | 0.14.0 | MIT |
| termcolor | 1.4.1 | Unlicense OR MIT |
| thiserror | 2.0.21 | MIT OR Apache-2.0 |
| thiserror-impl | 2.0.21 | MIT OR Apache-2.0 |
| thread_local | 1.1.10 | MIT OR Apache-2.0 |
| tiff | 0.11.3 | MIT |
| tiny-skia | 0.11.4 | BSD-3-Clause |
| tiny-skia-path | 0.11.4 | BSD-3-Clause |
| tiny-skia-path | 0.12.0 | BSD-3-Clause |
| tinystr | 0.8.4 | Unicode-3.0 |
| tinyvec | 1.13.3 | Zlib OR Apache-2.0 OR MIT |
| toml | 1.1.6+spec-1.1.0 | MIT OR Apache-2.0 |
| toml_datetime | 1.1.1+spec-1.1.0 | MIT OR Apache-2.0 |
| toml_parser | 1.1.3+spec-1.1.0 | MIT OR Apache-2.0 |
| toml_writer | 1.1.2+spec-1.1.0 | MIT OR Apache-2.0 |
| tracing | 0.1.44 | MIT |
| tracing-attributes | 0.1.31 | MIT |
| tracing-core | 0.1.36 | MIT |
| ttf-parser | 0.25.1 | MIT OR Apache-2.0 |
| twox-hash | 2.1.5 | MIT |
| type-map | 0.5.1 | MIT/Apache-2.0 |
| typenum | 1.20.1 | MIT OR Apache-2.0 |
| unicode-bidi | 0.3.18 | MIT OR Apache-2.0 |
| unicode-bidi-mirroring | 0.4.0 | MIT/Apache-2.0 |
| unicode-ccc | 0.4.0 | MIT/Apache-2.0 |
| unicode-general-category | 1.1.0 | Apache-2.0 |
| unicode-ident | 1.0.26 | (MIT OR Apache-2.0) AND Unicode-3.0 |
| unicode-normalization | 0.1.25 | MIT OR Apache-2.0 |
| unicode-properties | 0.1.4 | MIT/Apache-2.0 |
| unicode-script | 0.5.8 | MIT OR Apache-2.0 |
| unicode-segmentation | 1.13.3 | MIT OR Apache-2.0 |
| unicode-vo | 0.1.0 | MIT/Apache-2.0 |
| unicode-width | 0.2.2 | MIT OR Apache-2.0 |
| usvg | 0.45.1 | Apache-2.0 OR MIT |
| usvg | 0.48.1 | Apache-2.0 OR MIT |
| utf8_iter | 1.0.4 | Apache-2.0 OR MIT |
| uuid | 1.26.1 | Apache-2.0 OR MIT |
| vectorcraft-affinity | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-brush | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-cad | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-color | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-doc | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-effects | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-embroidery | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-engine | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-eps | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-format | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-geom | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-metafile | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-pathops | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-pdf | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-plugins | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-render | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-scriptcheck | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-svg | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-text | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-three-d | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-tools | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-trace | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-ui-egui | 0.14.0 | MIT OR Apache-2.0 |
| vectorcraft-web | 0.14.0 | MIT OR Apache-2.0 |
| vello_common | 0.1.0 | Apache-2.0 OR MIT |
| vello_common | 0.2.0 | Apache-2.0 OR MIT |
| vello_cpu | 0.1.0 | Apache-2.0 OR MIT |
| vello_cpu | 0.2.0 | Apache-2.0 OR MIT |
| version_check | 0.9.5 | MIT/Apache-2.0 |
| wasm-bindgen | 0.2.129 | MIT OR Apache-2.0 |
| wasm-bindgen-futures | 0.4.79 | MIT OR Apache-2.0 |
| wasm-bindgen-macro | 0.2.129 | MIT OR Apache-2.0 |
| wasm-bindgen-macro-support | 0.2.129 | MIT OR Apache-2.0 |
| wasm-bindgen-shared | 0.2.129 | MIT OR Apache-2.0 |
| wasmi | 2.0.0 | MIT/Apache-2.0 |
| wasmi_collections | 2.0.0 | MIT/Apache-2.0 |
| wasmi_core | 2.0.0 | MIT/Apache-2.0 |
| wasmi_ir | 2.0.0 | MIT/Apache-2.0 |
| wasmparser | 0.228.0 | Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT |
| web-sys | 0.3.106 | MIT OR Apache-2.0 |
| web-time | 1.1.0 | MIT OR Apache-2.0 |
| weezl | 0.1.12 | MIT OR Apache-2.0 |
| wgpu | 30.0.1 | MIT OR Apache-2.0 |
| wgpu-core | 30.0.1 | MIT OR Apache-2.0 |
| wgpu-core-deps-wasm | 30.0.1 | MIT OR Apache-2.0 |
| wgpu-hal | 30.0.1 | MIT OR Apache-2.0 |
| wgpu-naga-bridge | 30.0.1 | MIT OR Apache-2.0 |
| wgpu-types | 30.0.1 | MIT OR Apache-2.0 |
| winit | 0.30.13 | Apache-2.0 |
| winnow | 1.0.4 | MIT |
| write-fonts | 0.48.1 | MIT OR Apache-2.0 |
| writeable | 0.6.4 | Unicode-3.0 |
| xmlwriter | 0.1.0 | MIT |
| xmp-writer | 0.3.3 | MIT OR Apache-2.0 |
| yoke | 0.8.3 | Unicode-3.0 |
| yoke-derive | 0.8.3 | Unicode-3.0 |
| zerocopy | 0.8.59 | BSD-2-Clause OR Apache-2.0 OR MIT |
| zerocopy-derive | 0.8.59 | BSD-2-Clause OR Apache-2.0 OR MIT |
| zerofrom | 0.1.8 | Unicode-3.0 |
| zerofrom-derive | 0.1.8 | Unicode-3.0 |
| zerotrie | 0.2.5 | Unicode-3.0 |
| zerovec | 0.11.8 | Unicode-3.0 |
| zerovec-derive | 0.11.6 | Unicode-3.0 |
| zlib-rs | 0.6.8 | Zlib |
| zmij | 1.0.23 | MIT |
| zune-core | 0.5.3 | MIT OR Apache-2.0 OR Zlib |
| zune-jpeg | 0.5.15 | MIT OR Apache-2.0 OR Zlib |
