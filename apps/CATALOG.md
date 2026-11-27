# Component and launcher matrix

November 24, 2026. WebOS pins 184 component sources. The public viewer manifest lists 130 launcher IDs. Each source link opens its selected commit. The launch status comes from that manifest and the recorded access rules. Each build entry identifies a starting point. Native builds and browser workflow checks have their own release evidence. [Viewer manifest](https://ksu.codes/viewer-release.json) · [Server ownership](README.md)

Priority P0 covers platform foundations, P1 essential desktop workflows, P2 productivity, P3 specialized tools, P4 games and P5 historical source.

## WebOS core

| Priority | Source at selected commit | Interface or dependency | Entry or build input | Release status |
| --- | --- | --- | --- | --- |
| P0 | [apps/account-management](./account-management) | Signed-in My account and permission-scoped Manage users. | `app.mjs` and `style.css`, WebOS viewer option `--account-management enabled` | Chromium qualified with three account roles on staging. Mail settings record operator requests. Public activation pending. Source `91b3de0cfa87`. |
| P0 | [libraries/network-policy](https://github.com/CC-David-CC/network-policy/tree/5bba00d90a8aea770e2ffb73299c241a73812519) | Accounts/login and Browser relay policy · library only, installing starts no firewall or service | `pyproject.toml` · python | Component source |
| P0 | [platform/accounts](../platform/accounts) | Server authority · browser client · Runtime protocol · Storage grants | `src/webos_accounts/service.py` · python-js | Component source |
| P0 | [platform/runtime](../platform/runtime) | Desktop · app hosting · shared human/agent operation primitives · browser cache · account-file wire protocol | `active-system/assets/desktop/app-instance.mjs` · python-js | Component source |
| P0 | [platform/services](https://github.com/CC-David-CC/webos-services/tree/cf5cd77ae583ba3be61b48189cc189523ee693ff) | Worker installation, GPU and rendering services. | `install.py` | Worker service source. See the server index for ownership. |
| P0 | [platform/storage](https://github.com/CC-David-CC/storage/tree/d5d876894c890c1ee04667806079b8163d72b4b6) | Server filesystem/SQLite · Accounts proofs · browser file client · app file access | `src/webos_storage/__init__.py` · python-js | Component source |

## WebOS desktop and essential apps

| Priority | Source at selected commit | Interface or dependency | Entry or build input | Release status |
| --- | --- | --- | --- | --- |
| P0 | [apps/files](https://github.com/CC-David-CC/files/tree/10f30df75a8b0b7fa8c1bb678e6899e731605903) | Human file UI · Storage · upload/download/browser APIs · file associations · ZIP tool | `apps/system/files/index.mjs` · js | Live · files |
| P0 | [platform/desktop](../platform/desktop) | Human workspace/window controls · Runtime app launcher · account and file hooks · original optional guest bootstrap | `active-system/index.html` · js | Component source |
| P1 | [apps/calculator](https://github.com/CC-David-CC/calculator/tree/552d3b0767f309aaffc5ee4d06b176c922f90869) | Human mouse/keyboard input · Runtime window lifecycle · old source also has file hooks | `apps/system/calculator/index.mjs` · js | Live · calculator |
| P1 | [apps/gpu-monitor](https://github.com/CC-David-CC/gpu-monitor/tree/7359c89f50079ab85bd8867791a383d0be6fd3cb) | Browser display and server-side fleet probes. | `app.mjs` | Live · gpu-monitor |
| P1 | [apps/help](https://github.com/CC-David-CC/help/tree/5d51ef88ca4dcf8341d5c2f0452934f5d08750ad) | Human guide and contextual buttons · Runtime view lifecycle | `apps/system/help/index.mjs` · js | Live · help |
| P1 | [apps/remote-desktop](https://github.com/CC-David-CC/noVNC/tree/5bf4a8315e0346447cb8cacf66f120fb782f08ad) | Owner-authorized browser monitor and remote session relay. | `WEBOS.md` | Live for the owner |
| P1 | [apps/text](https://github.com/CC-David-CC/text/tree/0c34b0e1c36881963d4bdf98e282dab1df56785f) | Files open/save · Storage · CodeMirror · document/lifecycle hooks | `index.mjs` · js | Live · text |
| P1 | [apps/webos-chat](https://github.com/CC-David-CC/webos-chat/tree/d1cad10bada81b5b4e8df9414d7e850b514c039a) | Signed-in conversations, membership, read positions and live updates. | `registered.mjs` | Live for registered users. [Galaxy S10+ workflow](https://github.com/CC-David-CC/webos-chat/blob/webos/phone-chat-workflow/docs/webos-qa/PHONE.md). |
| P1 | [platform/login](https://github.com/CC-David-CC/login/tree/444e9e62e0bfa014ab3a3eedd5f339b42acdb312) | Human credential entry · Accounts client · public session result | `src/index.mjs` · js | Component source |

## App templates

| Priority | Source at selected commit | Interface or dependency | Entry or build input | Release status |
| --- | --- | --- | --- | --- |
| P3 | [apps/personal-template](https://github.com/CC-David-CC/personal-template/tree/b7c5259e4f0d34242cace8cc9f1fef23982ea3af) | Human-facing template with file hooks · starting material, not a completed end-user product | `index.mjs` · js | Source. No separate launcher in this manifest. |

## Communications

| Priority | Source at selected commit | Interface or dependency | Entry or build input | Release status |
| --- | --- | --- | --- | --- |
| P2 | [apps/rustirc](https://github.com/CC-David-CC/RustIRC/tree/a192061447538e0bd525d0eee3713dab32673a39) | Simulated IRC conversations in the browser. | `webos-demo.mjs` | Live browser simulation. [Galaxy S10+ workflow](https://github.com/CC-David-CC/RustIRC/blob/webos/phone-irc-simulation/docs/webos-qa/PHONE.md). |

## Craft shared source, assets and build tools

| Priority | Source at selected commit | Interface or dependency | Entry or build input | Release status |
| --- | --- | --- | --- | --- |
| P2 | [assets/craft-fonts](https://github.com/CC-David-CC/craft-fonts/tree/9ffb3a717e081a817470c5efe68fe314ca16c987) | Multiple Craft builds · explicit CRAFT_FONTS_DIR points here | `Cargo.toml` · cargo | Component source |
| P2 | [assets/craft-i18n](https://github.com/CC-David-CC/craft-i18n/tree/e56d26244bbac099bfd42e23fb12f78a4be418a7) | Multiple Craft builds · localization assets/source | `Cargo.toml` · cargo | Component source |
| P2 | [libraries/craft-libs](https://github.com/CC-David-CC/craft-libs/tree/94981849457596b032355f74144cdd91c04d5df5) | Used by multiple Craft apps · platform/atomic/doc/media/fonts/web-host and other crates · not just WordCraft | `Cargo.toml` · cargo | Component source |
| P2 | [libraries/egui](https://github.com/CC-David-CC/egui/tree/2d0ae4b4270e76c431fd62d3512237579ed6c26f) | Craft app rendering/UI dependency · browser/native targets | `Cargo.toml` · cargo | Component source |
| P2 | [tooling/craft-common-actions](https://github.com/storytold/craft-common-actions/tree/c8f4b6ec2a894285213c341611b6b023b0b3e469) | Build-time tooling · preserved workflow source does not authorize running publication jobs | `README.md` · cargo | Component source |
| P3 | [apps/pcbcraft-app](https://github.com/tangency-labs/pcbcraft-app/tree/35e03184c9e7e9673e0f832980a24b269a42749e) | Assembles the PCBCraft browser app and publishes the upstream Pages site | `assemble.sh` · pcb-web-package | Source. No separate launcher in this manifest. |

## Creative and media apps

| Priority | Source at selected commit | Interface or dependency | Entry or build input | Release status |
| --- | --- | --- | --- | --- |
| P3 | [apps/align](https://github.com/CC-David-CC/align/tree/24bf4ace3bc690261bff0d89a37ee9408d602764) | Measures video and audio sync offsets and exports timeline files. | `Cargo.toml` | Live · align |
| P3 | [apps/anicraft](https://github.com/CC-David-CC/anicraft/tree/b7549429a69e10521fdf078233a4e64b8829bc47) | Browser WASM · shared Craft formats/media/UI · file/host integration to qualify | `Cargo.toml` · craft-web | Live · anicraft |
| P3 | [apps/audio-editor](https://github.com/CC-David-CC/audio-editor/tree/6cec6674a0a1d442e44af076b2682b404074aa49) | Account WAV files · per-window frame · audio decode/export worker | `index.mjs` · js | Live · audio-editor |
| P3 | [apps/chromaforge](https://github.com/CC-David-CC/chromaforge/tree/a6d35a3777e2f01003144013be47f17b60f75676) | Edits and reopens photo catalogs. | `packaging/web/package.sh` | Live · chromaforge |
| P3 | [apps/chiralcraft](https://github.com/CC-David-CC/chiralcraft/tree/0a40e2edb5b8356fdfd4944e95d038f69f2e19c9) | Chemical structure editor · native Rust eframe workspace · WebOS browser and Files integration queued | `crates/chiralcraft-app/src/main.rs` · native | Source prepared · last in the integration queue. [Build and qualification scope](https://github.com/CC-David-CC/chiralcraft/blob/0a40e2edb5b8356fdfd4944e95d038f69f2e19c9/docs/webos-qa/INTEGRATION.md) |
| P3 | [apps/clothcraft](https://github.com/CC-David-CC/ClothCraft/tree/b82869da0358eae16a82b31c717a424327f268e6) | Browser garment and cloth design. | `Cargo.toml` | Live · clothcraft |
| P3 | [apps/cuepool](https://github.com/CC-David-CC/cuePool/tree/0379002fea037f1e7ae0b624b2191bb78daf24cd) | Show cue editing, preview and project files. | `Cargo.toml` | Live · cuepool |
| P3 | [apps/designcraft](https://github.com/CC-David-CC/designcraft/tree/cc32dbacb36278c0283538366db8d5a2dc522c16) | Browser WASM · shared Craft code/fonts · file/host integration to qualify | `apps/designcraft-web/Cargo.toml` · craft-web | Live · designcraft |
| P3 | [apps/diagrams-net](https://github.com/CC-David-CC/diagrams-net/tree/019db807059aeb1ed5d8ac0b4b12fb46aa891f49) | Account drawio files · per-window editor frame and file bridge | `index.mjs` · js | Live · diagrams-net |
| P3 | [apps/effectcraft](https://github.com/CC-David-CC/effectcraft/tree/5dd98eceb02b0c2557a4cbcf850342986799a0ca) | Browser WASM · shared Craft media/rendering code · file/host integration to qualify | `apps/effectcraft-web/Cargo.toml` · craft-web | Live · effectcraft |
| P3 | [apps/embroidery-studio](https://github.com/CC-David-CC/embroidery-studio/tree/c7476a36ea4e073317507cc7f5cfc60db060fc20) | Account project/machine files · local WASM editor build and frame/file bridge | `index.mjs` · js | Live · embroidery-studio |
| P3 | [apps/excalidraw](https://github.com/CC-David-CC/excalidraw/tree/c7a504dea1cc4529fcf71f982a9da3fbd9ab608f) | Account drawing files · browser React editor | `index.mjs` · js | Live · excalidraw |
| P3 | [apps/figcraft](https://github.com/CC-David-CC/figcraft/tree/db8862f37ffaaebe51bcdbd1ea042751a2ec1720) | Browser WASM · shared Craft code/fonts · file/host integration to qualify | `apps/figcraft-web/Cargo.toml` · craft-web | Live · figcraft |
| P3 | [apps/filmcraft](https://github.com/CC-David-CC/filmcraft/tree/b8bec7e92f1b85b6ffb6a6d84568d836e40fc4e7) | Browser WASM · shared Craft media code · file/host integration to qualify | `apps/filmcraft-web/Cargo.toml` · craft-web | Live · filmcraft |
| P3 | [apps/firecraft](https://github.com/CC-David-CC/FireCraft/tree/566cb826e6c16741145e419a37043f7e1604457c) | Browser editing for raster and vector graphics. | `Cargo.toml` | Live · firecraft |
| P3 | [apps/freedawm](https://github.com/CC-David-CC/FreeDAWm-upstream/tree/a469f3462ef72c16e6c5fbb6ffee2bb04cf70a6b) | Browser audio playback and editable project files. | `packaging/web/package.sh` | Live · freedawm |
| P3 | [apps/gusset-pattern-drafter](https://github.com/CC-David-CC/gusset-pattern-drafter/tree/6dd027ff5ff15038357c24e69fe981507e162982) | Sewing Pattern Drafter candidate · browser 2D drafting, 3D cloth preview and print exports · native .pdraft project | `drafter/pattern-drafter.html` · static JS and Three.js | Source prepared · WebOS packaging, account Files and phone layout queued. Standalone desktop passed. [Integration and device checks](https://github.com/CC-David-CC/gusset-pattern-drafter/blob/webos/integration/docs/webos-qa/INTEGRATION.md) |
| P3 | [apps/honeydew](https://github.com/CC-David-CC/honeydew/tree/25a83a3bf0cadbe966c94775bd596b85f2c2dbba) | Music sequencing with mobile-compatible project files. | `Trunk.toml` | Live · honeydew |
| P3 | [apps/humanmotioncraft](https://github.com/CC-David-CC/HumanMotionCraft/tree/f56aec8681eae9e764cd216b8c4eecbce443eff4) | Browser character posing and motion projects. | `Cargo.toml` | Live · humanmotioncraft |
| P3 | [apps/image-editor](https://github.com/CC-David-CC/image-editor/tree/5124a05c49b6b984677469513fa4e058ee1420a5) | Account image files · browser-local React/canvas processing | `index.mjs` · js | Live · image-editor |
| P3 | [apps/image-studio](https://github.com/CC-David-CC/image-studio/tree/2622e8ca07d8be645cb72f99048a7e5ae546f9de) | Browser UI, render gateway and workers. | `app.mjs` | Server adapter in the hosted backend. No separate launcher in this manifest. |
| P3 | [apps/lemon-studio](https://github.com/CC-David-CC/Lemon-Studio/tree/5b0943d5eeaf88094413814d5f0257f77206a5a6) | Browser sequencer, audio samples and project files. | `package.json` | Live · lemon-studio |
| P3 | [apps/lightcraft](https://github.com/CC-David-CC/lightcraft/tree/585054909ef7cdcf4b8b93cb4878cf7b85da424e) | Browser WASM · shared Craft image code · file/host integration to qualify | `apps/lightcraft-web/Cargo.toml` · craft-web | Live · lightcraft |
| P3 | [apps/materialcraft](https://github.com/CC-David-CC/materialcraft/tree/1f712a9504ea8d6ac1f313b5507130a7512c21d5) | Browser WASM, native material graph editing, account storage and recovery | `apps/materialcraft-web/Cargo.toml` · craft-web | Live · materialcraft |
| P3 | [apps/mixstudio](https://github.com/CC-David-CC/MixStudio/tree/e2b2cb7a4924de41b7b6f526770fe16821ca6feb) | DJ mix timelines, linked audio and WAV export. | `Trunk.toml` | Live · mixstudio |
| P3 | [apps/narrator](https://github.com/CC-David-CC/webos-narrator/tree/6d35e7adf773d654a9281a44d2b141259f39ed4e) | Browser narration workspace. | `app.mjs` | Live · narrator |
| P3 | [apps/oxiguitar](https://github.com/CC-David-CC/oxiguitar/tree/5956d5dc7b33c2647769bca1ba15b882ff9aaea0) | Guitar score editing, playback and Guitar Pro files. | `Trunk.toml` | Live · oxiguitar |
| P3 | [apps/oxybrush](https://github.com/CC-David-CC/OxyBrush/tree/5a82df164adae0409136e4a3b5814a194bb6ed30) | Sculpting and editable 3D projects. | `index.html` | Live · oxybrush |
| P3 | [apps/paint-rs](https://github.com/CC-David-CC/paint.rs/tree/6cd0e8f241340c0108ac510d2a7bceb4b356de00) | Layered raster editing. | `app.mjs` | Live · paint-rs |
| P3 | [apps/paintcraft](https://github.com/CC-David-CC/PaintCraft/tree/f7da925856406b8c27d9c634661ad6500e6aa700) | Browser drawing and painting. | `app.mjs` | Live · paintcraft |
| P3 | [apps/photocraft](https://github.com/CC-David-CC/photocraft/tree/3c2f04c5e7b6fc55349b478f62c8f90d942c9011) | Browser WASM · shared Craft image/fonts · file/host integration to qualify | `apps/photocraft-web/Cargo.toml` · craft-web | Live · photocraft |
| P3 | [apps/picasso-suite](https://github.com/CC-David-CC/Picasso-Suite/tree/57362a8ee5df59aef2ef91aea42eb7bc5727b743) | Video editing and timeline projects. | `Trunk.toml` | Live · picasso-suite |
| P3 | [apps/pixelcraft](https://github.com/CC-David-CC/PixelCraft/tree/2a2915c75f8aba9a5d34032bc6343447ac1c8fbf) | Sprite editing, animation playback and PNG export. | `index.html` | Live · pixelcraft |
| P3 | [apps/pro-wave](https://github.com/CC-David-CC/Pro-Wave/tree/75073d2481e8cd3381005481fc10192f830bc379) | Music timelines, WAV assets and project files. | `Trunk.toml` | Live · pro-wave |
| P3 | [apps/procraft](https://github.com/CC-David-CC/procraft/tree/0f7ab249f09a1598c26ab7bf982da99937d44c60) | Layered browser painting and PNG export. | `index.html` | Live · procraft |
| P3 | [apps/retake](https://github.com/CC-David-CC/altered-audio-editor/tree/28bb2c83b061be4350997bf07dd2dd95fbeacd8a) | Audio editing and WAV export. | `package.json` | Live · retake |
| P3 | [apps/soundcraft](https://github.com/CC-David-CC/soundcraft/tree/92ded9fdd09337864d219b49823efcbfb7659d98) | Browser WASM · shared Craft audio/media code · file/host integration to qualify | `apps/soundcraft-web/Cargo.toml` · craft-web | Live · soundcraft |
| P3 | [apps/stitch-converter](https://github.com/CC-David-CC/stitch-converter/tree/a82ed8a1278039f0e10dd4519a57342b8ecd5c26) | Account SVG and stitch files · local conversion · separate SVG-editor workflow | `index.mjs` · js | Live · stitch-converter |
| P3 | [apps/subcraft](https://github.com/CC-David-CC/subcraft/tree/05723060bb4bc9727d74002f0f8f62be26170cbc) | 3D surface painting and project files. | `Cargo.toml` | Live · subcraft |
| P3 | [apps/suhina](https://github.com/CC-David-CC/suhina-daw/tree/da1dd3f33e98768c72a97a7e8f354c905d98c494) | Browser audio sequencing and project files. | `Cargo.toml` | Live · suhina |
| P3 | [apps/svg-editor](https://github.com/CC-David-CC/svg-editor/tree/420bd0e32977eb6824f2aa8b7f915a463c94f80b) | Account SVG files · per-window SVG-edit frame and file bridge | `index.mjs` · js | Live · svg-editor |
| P3 | [apps/texturecraft](https://github.com/CC-David-CC/texturecraft/tree/9ad00bf8220175ae203afb033fc34527a45f050e) | Browser WASM · painting/baking/rendering source · file/host integration to qualify | `apps/texturecraft-web/Cargo.toml` · craft-web | Live · texturecraft |
| P3 | [apps/tracedraw](https://github.com/CC-David-CC/tracedraw/tree/2157436781bd9cebfa457cbb30c1ba0e8d4e5b50) | Vector illustration and native drawing files. | `Cargo.toml` | Live · tracedraw |
| P3 | [apps/transit](https://github.com/CC-David-CC/transit/tree/436d3ed7116aad87f430479544d56275cbb7e097) | Audio import, session editing and WAV export. | `Cargo.toml` | Live · transit |
| P3 | [apps/vectorcraft](https://github.com/CC-David-CC/vectorcraft/tree/480d7edb9c56b8527f8ce3515fcbf32c6fc0de3d) | Browser WASM · shared Craft format/fonts · file/host integration to qualify | `apps/vectorcraft-web/Cargo.toml` · craft-web | Live · vectorcraft |

## Engineering and developer apps

| Priority | Source at selected commit | Interface or dependency | Entry or build input | Release status |
| --- | --- | --- | --- | --- |
| P3 | [apps/acad](https://github.com/CC-David-CC/acad/tree/71ee2f30d6e13496b90e9e2affda413ca381b0fb) | CAD Modeler · source-built OpenCascade rectangle workbench · guest and account projects | `npm run build:webos-source` · `webos/prepare-source-package.py` | Live · jsketcher · [Phone and desktop workflow](https://github.com/CC-David-CC/acad/blob/0c8d2aaee47ba262f150aa3d6901f6d5630373b3/docs/webos-qa/PHONE.md) |
| P3 | [apps/arduino-simulator](https://github.com/CC-David-CC/arduino-simulator/tree/48e47f1b528ff5a76855724d3d1ee932791fab23) | Account HEX files · AVR8js worker · pin/serial display | `index.mjs` · js | Live · arduino-simulator · [Galaxy S10+ workflow](https://github.com/CC-David-CC/arduino-simulator/blob/webos/phone-uno-files/docs/webos-qa/PHONE.md) |
| P3 | [apps/cadcraft](https://github.com/CC-David-CC/cadcraft/tree/e44d26945579273e3406eea8d4488c1e160de138) | Browser WASM · CAD drafting · account DXF files | `apps/cadcraft-web/Cargo.toml` · craft-web | Live · cadcraft · [Galaxy S10+ workflow](https://github.com/CC-David-CC/cadcraft/blob/bc898737a7acdaad80eb9f0efad2ddbf1d7fc448/docs/webos-qa/PHONE.md) |
| P3 | [apps/circuit-lab](https://github.com/CC-David-CC/circuit-lab/tree/b483667868437194257be78c411205846455efdd) | Account netlists · bounded local worker · retained restricted research runtime | `index.mjs` · js | Live · circuit-lab |
| P3 | [apps/circuitjs](https://github.com/CC-David-CC/circuitjs/tree/0098960ad7198fb729efb65d72ef72a483ac35bc) | Account circuit files · per-window CircuitJS frame | `index.mjs` · js | Live · circuitjs |
| P3 | [apps/data-explorer](https://github.com/CC-David-CC/data-explorer/tree/ef5fe15a0d15483cc9ac5c9ead96c0366244f9fd) | Account data/results files · browser DuckDB-WASM and Perspective workers · no separate DB server | `index.mjs` · js | Source. No separate launcher in this manifest. |
| P3 | [apps/digital-logic](https://github.com/CC-David-CC/digital-logic/tree/ee5340f81bff7dd4895ed0664273bdf78f17842d) | Account logic JSON files · browser DigitalJS graph/editor | `index.mjs` · js | Live · digital-logic |
| P3 | [apps/drakon-bash](https://github.com/CC-David-CC/drakon-bash/tree/cf02726c613ede13b2924a4cb7614a6b1bad277d) | DRAKON diagrams · generated Bash · account files | `app.mjs` · `webos-files.json` | Live · drakon-bash · [Phone and tablet workflow](https://github.com/CC-David-CC/drakon-bash/blob/285d9c8fa321511eeb16ece37ec671c1c52943c4/docs/webos-qa/PHONE.md) |
| P3 | [apps/drakon-javascript](https://github.com/CC-David-CC/drakon-javascript/tree/556bdf98757ffb7fbf9af48b873a8fc142b41ff9) | DRAKON diagrams · JavaScript modules · account files | `app.mjs` · `webos-files.json` | Live · drakon-javascript · [Phone and desktop workflow](https://github.com/CC-David-CC/drakon-javascript/blob/f14b0877ef3bd045ee18c3f0c3b48d945b46eeb6/docs/webos-qa/PHONE.md) |
| P3 | [apps/drakon-python](https://github.com/CC-David-CC/drakon-python/tree/77c1f11c40abeba9de071b2228387350e4f53660) | DRAKON diagrams · Python scripts · account files | `app.mjs` · `webos-files.json` | Live · drakon-python · [Phone and desktop workflow](https://github.com/CC-David-CC/drakon-python/blob/f112027384924525cac853c0ca4498b42a8a0b88/docs/webos-qa/PHONE.md) |
| P3 | [apps/electronics-design](https://github.com/CC-David-CC/electronics-design/tree/1240d817db549235df279814ba81b5fac94af058) | Arduino example · PCB routing and simulation · account DEZ files | `index.mjs` · esbuild · retained source-pinned WebAssembly | Live · electronics-design · [Phone and desktop workflow](https://github.com/CC-David-CC/electronics-design/blob/7d141dc3ae2348f1fdf05306f820765a8ec56ede/docs/webos-qa/PHONE.md) |
| P3 | [apps/esp32sim](https://github.com/CC-David-CC/esp32sim/tree/e03de7f5813a9d820be90da9393438d64f2bab26) | Browser firmware simulator and project files. | `webos/README.md` | Live · esp32sim |
| P3 | [apps/fieldcraft](https://github.com/tangency-labs/fieldcraft/tree/b89311fca381752d871c2cd874128e79228b7e6b) | Modeler and solver with a Rust/WASM browser target | `apps/fieldcraft-web/Cargo.toml` · cargo | Live · fieldcraft |
| P3 | [apps/gcode-preview](https://github.com/CC-David-CC/gcode-preview/tree/703c2b44a106810b3e297a3a420b05e1d7c15b2c) | Account G-code files · browser worker/rendering | `index.mjs` · js | Live · gcode-preview |
| P3 | [apps/grid-tools](https://github.com/CC-David-CC/grid-tools/tree/cb3a5aefa1450c222ca4c8c5f4a583aa426a5012) | Grid.Space slicing and mesh editing · browser workers · guest and account project files | `index.mjs` · `prepare.py` | Live · kiri-moto, mesh-tool · [Kiri:Moto workflow](https://github.com/CC-David-CC/grid-tools/blob/2f6f3fc6bf782f54f98a8f0a5b8cfaa9541889d5/docs/webos-qa/PHONE.md) · [Mesh:Tool workflow](https://github.com/CC-David-CC/grid-tools/blob/1b892db9ccd158d647951a03b98a56599f5b346d/docs/webos-qa/MESH-TOOL.md) |
| P3 | [apps/hdl-workbench](https://github.com/CC-David-CC/verisim/tree/396ed7a9c12c5aea016988b1e51aa9859080e724) | Browser HDL design and simulation. | `index.html` | Live · hdl-workbench |
| P3 | [apps/jsketcher](https://github.com/CC-David-CC/jsketcher/tree/518a4666cfc5c94acb153f0cd315a2ca1625eb2f) | Standalone CAD browser build · OCCT interpreter dependency · integration separate from ACAD | `package.json` · cad | Standalone source |
| P3 | [apps/matcraft](https://github.com/CC-David-CC/matcraft/tree/f91d07b74a58b17a02850bbafde6fdaefe9072e6) | Edits and runs MATLAB-style scripts · account and guest M files · touch editor and full Studio | `Cargo.toml` · Rust/WASM | Live · matcraft · [Phone workflow](https://github.com/CC-David-CC/matcraft/blob/fbc48ea0be66eec4d71010b38760bbd8480fb011/docs/webos-qa/PHONE.md) |
| P3 | [apps/mathcraft](https://github.com/CC-David-CC/mathcraft/tree/f983f10c2a95d61b8efa0b02ef94fdb083a4d742) | Octave lab and editable workspace files. | `app.mjs` | Live · mathcraft · [Phone workflow](https://github.com/CC-David-CC/mathcraft/blob/778c6daa8191f23e2932d36a2ea58c4cb5af1519/docs/webos-qa/PHONE.md) |
| P3 | [apps/mathcraft2](https://github.com/CC-David-CC/MathCraft-upstream/tree/06ce75d2c9712169cb2a801becb2945eb135b45c) | Computational notebook editing and execution. | `Cargo.toml` | Live · mathcraft2 · [Phone workflow](https://github.com/CC-David-CC/MathCraft-upstream/blob/06ce75d2c9712169cb2a801becb2945eb135b45c/docs/webos-qa/PHONE.md) |
| P3 | [apps/microduck](https://github.com/CC-David-CC/microduck/tree/daabd956b96fe93a1bead77cdf23b1f7c770c417) | Account project files · MuJoCo/ONNX inputs · browser worker/rendering | `index.mjs` · microduck | Source. No separate launcher in this manifest. |
| P3 | [apps/notebook](https://github.com/CC-David-CC/notebook/tree/8d4b8a873d401411a61514a57fd04107375c4867) | Account notebook/text files · browser Python kernel/worker · optional guest terminal is separate | `index.mjs` · notebook | Live · notebook |
| P3 | [apps/opencadstudio](https://github.com/CC-David-CC/OpenCADStudio/tree/860481708ca81e1631a712a04802f589b1ac2d46) | Browser CAD editing. | `WebOS.Trunk.toml` | Live · opencadstudio |
| P3 | [apps/opencharts](https://github.com/dylanpersonguy/OpenCharts/tree/399e27538d8150796571dbdecbe920a54b771de4) | Independent charting application source. | `package.json` | Source. No separate launcher in this manifest. |
| P3 | [apps/pcb-design](https://github.com/CC-David-CC/pcb-design/tree/1dee68bb31ae678c395fce3a4e2dc56fd773dc01) | Node prototype only · browser app and complete dependency notices absent | `package.json` · prototype | Source. No separate launcher in this manifest. |
| P3 | [apps/pcbcraft](https://github.com/CC-David-CC/pcbcraft/tree/407944c8cc33b063cde24fcf48cc9ade8cfe5621) | Board editor and command-line interface with a Rust/WASM browser target | `apps/pcbcraft-web/Cargo.toml` · cargo | Live · pcbcraft |
| P3 | [apps/pico-simulator](https://github.com/CC-David-CC/pico-simulator/tree/32afc75ad8f118342e9c8952ccf16bb328c6282a) | Account firmware files · browser worker · simulated hardware/serial | `index.mjs` · js | Live · pico-simulator · [Galaxy S10+ workflow](https://github.com/CC-David-CC/pico-simulator/blob/webos/phone-blink-and-files/docs/webos-qa/PHONE.md) |
| P3 | [apps/replicad](https://github.com/CC-David-CC/replicad/tree/ac2f0290fe0870cf479dc1d8208dd6b62353eb4a) | Account source/model files · app-owned worker and independent kernel | `index.mjs` · js | Live · replicad |
| P3 | [apps/riscv-rust](https://github.com/CC-David-CC/riscv-rust/tree/7d23dfa90b56f03aa43a479793e9cb83d2707919) | Browser RISC-V machine simulator and image files. | `webos/README.md` | Live · riscv-rust |
| P3 | [apps/sketchcraft](https://github.com/CC-David-CC/sketchcraft/tree/b752e9d03967bca49cfe9417297942f6b9a101bf) | React/Vite and Rust/WASM modeling, account storage and scoped operations | `app/index.html` · native | Live · sketchcraft |
| P3 | [apps/softfpga](https://github.com/CC-David-CC/softfpga/tree/eaf3f6ecc72286617ab6a4344ab27f2e1b54fdef) | Browser FPGA simulation. | `index.html` | Live · softfpga |
| P3 | [apps/solidcraft](https://github.com/CC-David-CC/solidcraft/tree/789fce1bf17145b4086a175f552ce268c846f784) | Browser WASM, native parametric modeling, account storage and scoped operations | `apps/solidcraft-web/Cargo.toml` · craft-web | Live · solidcraft |

## Games and interactive activities

| Priority | Source at selected commit | Interface or dependency | Entry or build input | Release status |
| --- | --- | --- | --- | --- |
| P4 | [apps/chess-study](https://github.com/CC-David-CC/chess-study/tree/6de033ec21aa9a9c4ee0aaf1349f8c01d6eb6526) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · chess-study |
| P4 | [apps/clockwork-quest](https://github.com/CC-David-CC/clockwork-quest/tree/6ecb1a4e6a4df03ee3edd40b168dc5da371a9825) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · clockwork-quest |
| P4 | [apps/clockwork-room](https://github.com/CC-David-CC/clockwork-room/tree/73c29d3f5477e563b22d6ef5469077322ddc4b53) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · clockwork-room |
| P4 | [apps/crystal-defense](https://github.com/CC-David-CC/crystal-defense/tree/03d6d2eb9fc9a7905d47688a5b382d9a2e414cc1) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · crystal-defense |
| P4 | [apps/drone-circuit](https://github.com/CC-David-CC/drone-circuit/tree/653f3e3fab933313e7fe0ef0bd3cee4da972dc1a) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · drone-circuit |
| P4 | [apps/expression-puppet](https://github.com/CC-David-CC/expression-puppet/tree/9b42fa4cde8c315bc53f6c22e0d612bd9d99db18) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · expression-puppet |
| P4 | [apps/falling-blocks](https://github.com/CC-David-CC/falling-blocks/tree/7d5446b82c607c46e84ef2ddf4df03caf0836e74) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · falling-blocks |
| P4 | [apps/garden-defense](https://github.com/CC-David-CC/garden-defense/tree/81969906dd731c1d23b0f515440e6816ae838e29) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · garden-defense |
| P4 | [apps/gravity-pinball](https://github.com/CC-David-CC/gravity-pinball/tree/2120206d67fd73e306118201ed4dc555d22bf117) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · gravity-pinball |
| P4 | [apps/kinetic-relay](https://github.com/CC-David-CC/kinetic-relay/tree/dfa58d3032fcc7332b861da9d05f263990c883e0) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · kinetic-relay |
| P4 | [apps/lantern-leap](https://github.com/CC-David-CC/lantern-leap/tree/f40eb80b910af2d4eeb456164762d413bca632e9) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · lantern-leap |
| P4 | [apps/marble-works](https://github.com/CC-David-CC/marble-works/tree/ecba334c74e55b8f7440a73232666be2d091ee22) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · marble-works |
| P4 | [apps/memory-garden](https://github.com/CC-David-CC/memory-garden/tree/3e44eb02768f22bd1b9b309408abd70c169fa7f7) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · memory-garden |
| P4 | [apps/orbital-courier](https://github.com/CC-David-CC/orbital-courier/tree/1f0ea71f0606b2221f5969b77af9759914d631e6) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · orbital-courier |
| P4 | [apps/owl-companion](https://github.com/CC-David-CC/owl-companion/tree/b24e1743d16e9c0f9927a009dd3b0b86aa742857) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · owl-companion |
| P4 | [apps/physics-playground](https://github.com/CC-David-CC/physics-playground/tree/286858922b296dc9f704d8bc039ce9d52081d9ed) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · physics-playground |
| P4 | [apps/pocket-golf](https://github.com/CC-David-CC/pocket-golf/tree/737912f43fa5b2c7cdf12f9b938a53ebf34ee9ad) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · pocket-golf |
| P4 | [apps/pocket-rally](https://github.com/CC-David-CC/pocket-rally/tree/1c45238deac00386df16819438e18cde9735b88f) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · pocket-rally |
| P4 | [apps/reactive-control-desk](https://github.com/CC-David-CC/reactive-control-desk/tree/9f3561bb23dbb42278c3dbbb5850ed28259c8325) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · reactive-control-desk |
| P4 | [apps/rhythm-garden](https://github.com/CC-David-CC/rhythm-garden/tree/eaaf7bef069969cf703d9302bc57a24b160b1c25) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · rhythm-garden |
| P4 | [apps/sky-courier](https://github.com/CC-David-CC/sky-courier/tree/5612cfd20310f4950f48b400ed64ac6a89cb11b7) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · sky-courier |
| P4 | [apps/sling-targets](https://github.com/CC-David-CC/sling-targets/tree/4f576d2bc1f0ed71d7515ea04da6be0662758306) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · sling-targets |
| P4 | [apps/snake-garden](https://github.com/CC-David-CC/snake-garden/tree/9c8a57b0208f682361759801c67c9bd5b7666f79) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · snake-garden |
| P4 | [apps/solitaire](https://github.com/CC-David-CC/solitaire/tree/fdd6c008f6b3e17e01688421603168efbd6f17c0) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · solitaire |
| P4 | [apps/stack-balance](https://github.com/CC-David-CC/stack-balance/tree/75849862dcc4cbd06e7f56250b2d0c4d9b74af16) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · stack-balance |
| P4 | [apps/story-cards](https://github.com/CC-David-CC/story-cards/tree/e7fae3146a1bf95a380533306cfd5c183a1e474f) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · story-cards |
| P4 | [apps/tabletop-bot-arena](https://github.com/CC-David-CC/tabletop-bot-arena/tree/87807ed19e3aea3f33146b2e1d57f4a1e4206e39) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · tabletop-bot-arena |
| P4 | [apps/target-garden](https://github.com/CC-David-CC/target-garden/tree/e56eba10aab829c788374b5a25d1aa6f5ef7c5b6) | Human browser activity · Runtime lifecycle · existing account-file save/progress hooks | `index.mjs` · js | Live · target-garden |

## Games shared code

| Priority | Source at selected commit | Interface or dependency | Entry or build input | Release status |
| --- | --- | --- | --- | --- |
| P4 | [libraries/learning-game-core](https://github.com/CC-David-CC/learning-game-core/tree/a1f3db3987fa0a89aad6eab359d90c9f49f24454) | Source dependency of planned game cores · no user window | `core.mjs` · model | Component source |

## Learning and practice

| Priority | Source at selected commit | Interface or dependency | Entry or build input | Release status |
| --- | --- | --- | --- | --- |
| P2 | [apps/i-success](https://github.com/CC-David-CC/i-success/tree/a2cc1582f55c33d642dbe8d7fec8b8d23678221b) | Browser practice activities. | `Cargo.toml` | Live · i-success |

## Office and document apps

| Priority | Source at selected commit | Interface or dependency | Entry or build input | Release status |
| --- | --- | --- | --- | --- |
| P2 | [apps/deckcraft](https://github.com/CC-David-CC/deckcraft/tree/5a3c26a37576ce08b7d8943eb652b284c011c2ac) | Browser WASM app · shared Craft host crate/fonts · explicit file and document-operation integration on our branch | `apps/deckcraft-web/Cargo.toml` · craft-web | Live · deckcraft |
| P2 | [apps/document-editor](https://github.com/CC-David-CC/document-editor/tree/152a8acbe9074c924a3dd23abedaa509ca1bb2b6) | Account file JSON documents · PDF export and PDF Viewer launch · existing browser host | `index.mjs` · js | Source. No separate launcher in this manifest. |
| P2 | [apps/gridcraft](https://github.com/CC-David-CC/gridcraft/tree/757b11dce199db8b953363ad847cf45a36cd2687) | Browser WASM app · shared Craft code/fonts · host/account-file integration still to qualify | `apps/gridcraft-web/Cargo.toml` · craft-web | Live · gridcraft |
| P2 | [apps/lovecraft](https://github.com/CC-David-CC/LoveCraft/tree/47d45201b1d07c225c28a287d91806866b09c090) | Browser-local writing workspace. | `packaging/web/package.sh` | Live · lovecraft |
| P2 | [apps/mailcraft](https://github.com/CC-David-CC/mailcraft/tree/061ef3e20940622f04c749d082f71bdc7223ab9a) | WebOS sign-in, JMAP mailbox and server-enforced mail grants. | `packaging/web/package.sh` | Live for approved mailboxes |
| P2 | [apps/metriccraft](https://github.com/CC-David-CC/metriccraft/tree/33e801030ba0ab7d781362e6d9b94f9feaab4056) | Report editor, data imports and editable report files. | `Cargo.toml` | Live · metriccraft |
| P2 | [apps/notecraft](https://github.com/CC-David-CC/notecraft/tree/8a72dae6838966a21b7351804947d1d5aac53e05) | Notebook and note editing. | `app.mjs` | Live · notecraft |
| P2 | [apps/pdf-viewer](https://github.com/CC-David-CC/pdf-viewer/tree/dbf0ddebd75323e7f00311d5f7dfe7bcefb3ff9c) | Account files · browser rendering · PDF.js dependency · existing browser host | `index.mjs` · js | Source. No separate launcher in this manifest. |
| P2 | [apps/pdfcraft](https://github.com/CC-David-CC/pdfcraft/tree/1eab1a0327a9c37372b970ebbd09c7b0c8ae56d8) | Native browser PDF engine · shared account Storage · Desktop document activation · account-scoped recovery/preferences | `webos/build.py` · craft-web | Live · pdfcraft |
| P2 | [apps/projectcraft](https://github.com/CC-David-CC/projectcraft/tree/c2722d1651b147843cdab57f092f919c1a707c78) | Project planning and editable project files. | `Cargo.toml` | Live · projectcraft |
| P2 | [apps/scriobh](https://github.com/CC-David-CC/scriobh/tree/afc3feb3038781dc723d9342459d813d44fbf2eb) | Ordered Markdown writing projects with browser SQLite. | `Makefile` | Live · scriobh |
| P2 | [apps/spreadsheet](https://github.com/CC-David-CC/spreadsheet/tree/10f7c5b7ea2863fe4b4bdbafd8b9c60fcf6aab80) | Account files · XLSX worker · CSV import/export · existing browser host | `index.mjs` · js | Source. No separate launcher in this manifest. |
| P2 | [apps/textcraft](https://github.com/CC-David-CC/textcraft/tree/d84bf0a4cab44704fc3d607a23f000d7ad790389) | Plain-text editing and encoding-preserving saves. | `Cargo.toml` | Live · textcraft |
| P2 | [apps/wordcraft](https://github.com/CC-David-CC/wordcraft/tree/ddbef623161c88e1e6aa575d8684f9643fbef39d) | Browser WASM app · shared Craft crates/fonts · WebOS file/operation integration on our branch | `webos/build.py` · craft-web | Live · wordcraft |
| P3 | [apps/prosecraft](https://github.com/CC-David-CC/ProseCraft/tree/f33335573c63509b9f22de22ade87a02d588bac6) | Novel-writing editor · outlines, chapters, scenes and publishing · browser vault and project backups | `src/routes/+page.svelte` · SvelteKit static build | Source prepared · queued at the end for scoped My files and phone checks. [Standalone browser baseline](https://github.com/CC-David-CC/ProseCraft/blob/webos/integration/docs/webos-qa/INTEGRATION.md) |

## Optional execution environments

| Priority | Source at selected commit | Interface or dependency | Entry or build input | Release status |
| --- | --- | --- | --- | --- |
| P3 | [apps/browser](https://github.com/CC-David-CC/browser/tree/09a4d57fde2ae5d4ecf9c4d62a7764994546a994) | Worker engine · guest downloads to account files · separately owned authenticated network relay and policy | `index.mjs` · gecko | Source. No separate launcher in this manifest. |
| P3 | [apps/linux](https://github.com/CC-David-CC/linux/tree/27b01eb5c4a66e559d6c90da82cd4def2770b5b4) | v86 worker · temporary guest filesystem · optional guest networking server · distinct from account storage | `assets/desktop/guest-worker-client.mjs` · guest | Source. No separate launcher in this manifest. |
| P3 | [apps/linux-x11](https://github.com/CC-David-CC/linux-x11/tree/f76c5e19c0b53a689ecb9668c25a1e6923ec0c54) | Browser Linux X11 guest. | `app.mjs` | Live · linux-x11 |
| P3 | [apps/terminal](https://github.com/CC-David-CC/terminal/tree/ab5dfe145b6882f804beb939bfc110fce550262b) | Browser xterm.js · host-provided guest PTY · explicit file copies · no server shell | `index.mjs` · js | Live · terminal |

## Optional platform services and policy

| Priority | Source at selected commit | Interface or dependency | Entry or build input | Release status |
| --- | --- | --- | --- | --- |
| P3 | [platform/publication](https://github.com/CC-David-CC/publication/tree/d16fbb2fb4e7df64ec4813b1491f79bdb86c592d) | Chat/Chess history and registry source · separate from signaling · interface port pending | `src/webos_publication/__init__.py` · python | Component source |
| P3 | [platform/rendezvous](https://github.com/CC-David-CC/rendezvous/tree/ffdc50e680d57a637ec32f2d2e3a5a6e86623716) | Lease registry · signed protocol · optional WebSocket/TURN support · not required for files/desktop | `src/steward/__init__.py` · python | Component source |

## Planned game cores

| Priority | Source at selected commit | Interface or dependency | Entry or build input | Release status |
| --- | --- | --- | --- | --- |
| P4 | [apps/fraction-farm](https://github.com/CC-David-CC/fraction-farm/tree/5558c9adcdbc8eb3ce2cd67669a9bb3859610a6a) | Shared learning-game-core dependency · no desktop view | `model.mjs` · model | Live · fraction-farm |
| P4 | [apps/market-math](https://github.com/CC-David-CC/market-math/tree/2c2e56476c604c99f546e9c8f264fe42fd879882) | Shared learning-game-core dependency · no desktop view | `model.mjs` · model | Live · market-math |
| P4 | [apps/math-path](https://github.com/CC-David-CC/math-path/tree/bae89640abef45d0a7d65d704d754ed9d40e1a68) | Shared learning-game-core dependency · no desktop view | `model.mjs` · model | Live · math-path |
| P4 | [apps/pocket-conquest](https://github.com/CC-David-CC/pocket-conquest/tree/823a51dbe62121f39c2af2f09cb052acb3b85abd) | Shared learning-game-core dependency · no desktop view | `model.mjs` · model | Live · pocket-conquest |
| P4 | [apps/rule-detective](https://github.com/CC-David-CC/rule-detective/tree/0a6c3dde341e48e7c9e82116d86d810d96c8dac9) | Shared learning-game-core dependency · no desktop view | `model.mjs` · model | Live · rule-detective |
| P4 | [apps/tile-islands](https://github.com/CC-David-CC/tile-islands/tree/c297890852dfcd77b412d6a8e92549d1ae3a4592) | Shared learning-game-core dependency · no desktop view | `model.mjs` · model | Live · tile-islands |
| P4 | [apps/word-weaver](https://github.com/CC-David-CC/word-weaver/tree/c3fc00c1e8eec75a7ab0ca20a172b806e70caf8d) | Shared learning-game-core dependency · no desktop view | `model.mjs` · model | Live · word-weaver |

## Shared browser tools and engines

| Priority | Source at selected commit | Interface or dependency | Entry or build input | Release status |
| --- | --- | --- | --- | --- |
| P1 | [libraries/codemirror](https://github.com/CC-David-CC/codemirror/tree/1ad4f9a2176e62a1c3e26e05bbab0daaddbf57a0) | Lazy host tool · browser editor instances · no standalone window | `index.mjs` · js | Component source |
| P1 | [libraries/zip](https://github.com/CC-David-CC/zip/tree/c55e2e4ad840a055c61fb2c5ea328bb7723483f0) | Host tool · bounded browser ZIP create/extract · no standalone window | `index.mjs` · js | Component source |
| P2 | [engines/ffmpeg](https://github.com/CC-David-CC/engine-ffmpeg/tree/f076ef7e2a765721c9e858bf6c737f0d0c5391bb) | On-demand host tool · caller-owned browser WASM worker · no standalone app or server service | `index.mjs` · js | Component source |
| P2 | [libraries/echarts](https://github.com/CC-David-CC/echarts/tree/00073db60a098c5b567c2de788e52c71cb481dea) | Lazy library · consuming app owns data and view | `index.mjs` · js | Component source |
| P2 | [libraries/mermaid](https://github.com/CC-David-CC/mermaid/tree/21d0736b0fe7d266649ef3f951c688602ab37e9b) | Lazy library · browser caller-owned rendering · no standalone window | `index.mjs` · js | Component source |
| P2 | [libraries/pdfme](https://github.com/CC-David-CC/pdfme/tree/d92b28b8c14477c483c429feff1f55693ccc71b4) | Lazy library · consuming app supplies document data and output | `index.mjs` · js | Component source |
| P2 | [libraries/plotly](https://github.com/CC-David-CC/plotly/tree/ec47dcd4db61d2a3dde87e431ff9c38545cb9965) | Lazy library · consuming app owns data and view | `index.mjs` · js | Component source |
| P2 | [libraries/tone](https://github.com/CC-David-CC/tone/tree/db31ef6db34249c0f61d0a592b692340f4da62d8) | Lazy host tool · browser user-gesture audio context · consuming app owns nodes | `index.mjs` · js | Component source |
| P2 | [libraries/wavesurfer](https://github.com/CC-David-CC/wavesurfer/tree/1554e70ffebfc9060bf0c73c2a054d24a6d80c71) | Lazy host tool · consuming app owns view/lifecycle · no standalone window | `index.mjs` · js | Component source |
| P3 | [engines/onnx-runtime](https://github.com/CC-David-CC/engine-onnx-runtime/tree/2152e0412e8152bb75cc71a86aaef7d4293045a8) | Optional lazy engine · model supplied by consumer · no shared-copy consumer integrated | `index.mjs` · js | Component source |
| P3 | [engines/opencascade-js](https://github.com/CC-David-CC/engine-opencascade-js/tree/3adbbc6691b9ff5a40132e36522d335abe84ecd9) | Lazy host tool · browser WASM/worker module · Replicad and JSketcher use separate kernels | `index.mjs` · js | Component source |
| P3 | [engines/speech](https://github.com/CC-David-CC/engine-speech/tree/5e65c9a22b8de9865dedd96a00505e07bc917601) | Microphone/browser worker · pinned local models · user permission · current desktop integration not enabled | `client.mjs` · speech | Component source |
| P3 | [libraries/gltf-transform](https://github.com/CC-David-CC/gltf-transform/tree/eacdc40c223175a275b534d58d59e3de7e356945) | Lazy host tool · caller-owned documents · external resources must use authorized files | `index.mjs` · js | Component source |
| P3 | [libraries/maplibre](https://github.com/CC-David-CC/maplibre/tree/66a2fc39deb2fd45d813cfa69f4bf3421c9dae59) | Optional lazy library · consumer supplies map/data policy · no standalone app | `index.mjs` · js | Component source |
| P3 | [libraries/tanstack-virtual](https://github.com/CC-David-CC/tanstack-virtual/tree/2d36b30045bc258da1cb5caced35cfaca40850c5) | Optional lazy library · no shared-copy consumer integrated · no standalone app | `index.mjs` · js | Component source |
| P3 | [libraries/transformers](https://github.com/CC-David-CC/transformers/tree/b122b539a116b63964c95a7fee69914a3ea41067) | Optional lazy library · consumer must provide local models · remote model fallback disabled | `index.mjs` · js | Component source |
| P3 | [libraries/trystero](https://github.com/CC-David-CC/trystero/tree/7bac5673e32a6bf1665d30a9aee494ced8cdea82) | Explicit consumer signaling/connection policy required · no app uses shared copy by default | `index.mjs` · js | Component source |
| P3 | [libraries/webtorrent](https://github.com/CC-David-CC/webtorrent/tree/a53c2caf06b694ffbd550abf57c9a7a2df86a1dd) | Explicit trackers/authorization/transport required · no default peer transfer | `index.mjs` · js | Component source |
| P3 | [libraries/yjs](https://github.com/CC-David-CC/yjs/tree/8cb9c3b76b539ad5c8489bed4b572dabc63eb23e) | No transport, persistence or authorization provided by this copy · no current shared-copy consumer | `index.mjs` · js | Component source |

## Shared native and guest engines

| Priority | Source at selected commit | Interface or dependency | Entry or build input | Release status |
| --- | --- | --- | --- | --- |
| P3 | [engines/manifold](https://github.com/CC-David-CC/engine-manifold/tree/4f7e212191d0756428a44927ef82828243a2f23c) | C++/Python/JS-WASM build · CAD dependency · no user window | `CMakeLists.txt` · native | Component source |
| P3 | [engines/occt-interpreter](https://github.com/CC-David-CC/engine-opencascade/tree/1a3fe7de54bd1449f99682bdcce7588be91a38a2) | Container/OCCT source input and JS wrapper · separate from generic OpenCascade.js | `Dockerfile` · native | Component source |
| P3 | [engines/smlib-wasm](https://github.com/CC-David-CC/engine-smlib-wasm/tree/1ffd5708dd19bc10525dc3c99e6cf0019f41ff77) | Emscripten build of USD-BRep/SMLib · CAD worker boundary | `src/api.mjs` · native | Component source |
| P3 | [engines/usd-brep](https://github.com/CC-David-CC/engine-usd-brep/tree/3fd5b9548d19aa8c12c29bc9637a96d42a06f8a5) | Native build/toolchain · optional CAD engine dependency | `BUILDING.md` · native | Component source |
| P3 | [engines/v86](https://github.com/CC-David-CC/engine-v86/tree/9019aa65bf60578fb342830b36315e466d39fb51) | Browser WASM/JIT plus firmware · optional Linux dependency only | `Makefile` · native | Component source |
| P3 | [libraries/winit](https://github.com/UCS-Care-Group/winit/tree/758a50e35a928dbf72bf05ae91f12fee7a540a83) | Native and browser windowing dependency. | `Cargo.toml` | Component source |

## Unused legacy source

| Priority | Source at selected commit | Interface or dependency | Entry or build input | Release status |
| --- | --- | --- | --- | --- |
| P5 | [legacy/rooms](https://github.com/CC-David-CC/rooms/tree/23228947bf72f166937327ccd9faa8f0ba3eab30) | User-confirmed old code · no current service, listener or app dependency | `README.md` · historical | Component source |

## Weather and maps

| Priority | Source at selected commit | Interface or dependency | Entry or build input | Release status |
| --- | --- | --- | --- | --- |
| P2 | [apps/earthcraft](https://github.com/CC-David-CC/EarthCraft/tree/2cc8cc68ba478c6387c7892439f671cf3b343d68) | Globe viewer, geographic annotation and KML/KMZ files. | `Trunk.toml` | Live · earthcraft |
| P2 | [apps/isobar](https://github.com/CC-David-CC/isobar/tree/f208f1128f3997d43cb751a96fe259e7bef8a36c) | Browser weather maps. | `WEBOS.md` | Live · weather-maps |
| P2 | [apps/pohoda](https://github.com/CC-David-CC/pohoda/tree/f76f997926c330a2c5bf6065896d33cf1cdf2033) | Browser forecast UI and Weather service. | `WEBOS.md` | Live · weather |
