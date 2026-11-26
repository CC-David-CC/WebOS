# Active ksu.codes release

## MatCraft touch scripting and editable M files

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `7f2ef5f0e62b1db0ac50341b6e8c7243a6af722fb4f25716e236b4e4eaf5351f` | `574193485e8027452701c252d96f489e4629a658` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

MatCraft's WebOS wrapper gives narrow windows a script editor, visible results and the same Files toolbar as Studio. The WASM engine is pinned at `9e0f03ba304b9fcd941bb63bf9d671762b8e3d59`. On ksu.codes the Galaxy S10+ and desktop Chromium calculated matrix determinants, recovered from invalid syntax, saved a bare filename with the `.m` extension, reopened the editable script through Files and saved another revision. The Moto G 5G and emulated touch tablet repeated the guest workflow in isolated WebOS. Desktop also reopened server-backed work from a fresh disposable session and passed the app's Open picker, draft preservation on cancellation, resizing between editing views and a 2D plot in Studio. MatCraft passed 8 of 10 documented desktop workflows.

All 18 overlay paths matched over HTTPS. On box-webhost, `sudo python3 -I -B /var/backups/webos-matcraft-phone-7f2ef5f0e62b/deploy-viewer.py rollback` restores viewer `6676a3842adb988f7d75b32d9d4470914ca5ac5362a1f25876452c6922b0b23d`.

## Kiri:Moto touch menus and editable file cycle

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `6676a3842adb988f7d75b32d9d4470914ca5ac5362a1f25876452c6922b0b23d` | `10525098a86384491db948ac46ccf398c5d2a97c` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

Grid.Space wrapper `f36e83dfafb6dd9f532596cdefeec93934e8cc43` gives the File menu a usable width, refreshes the account picker after uploads, and supplies the expected extension for bare filenames. The Galaxy S10+ and desktop Chromium replayed the hosted cube slicing, native workspace reopen, in-place save, and G-code Preview handoff. The test cube yielded 81 slices. Isolated desktop testing verified signed-in STL import from a real Files upload, fresh server-backed reopen, and a 24 mm, 12-facet STL export. The Moto G 5G repeated the core workflow in landscape. The shared Mesh:Tool wrapper passed a native file regression on the S10+. [Screenshots and workflow coverage](https://github.com/CC-David-CC/grid-tools/blob/2f6f3fc6bf782f54f98a8f0a5b8cfaa9541889d5/docs/webos-qa/PHONE.md)

All 54 overlay paths matched over HTTPS. On box-webhost, `sudo python3 -I -B /var/backups/webos-kiri-moto-phone-6676a3842adb/deploy-viewer.py rollback` restores viewer `ec3deccd50677eda9ff2ab8e2b7181061c3ad6d68b42634e91ea87daf1ace736`.

## CAD Modeler phone menus and editable project files

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `ec3deccd50677eda9ff2ab8e2b7181061c3ad6d68b42634e91ea87daf1ace736` | `1403ba2cbc64cb477b4e6c48bf06cad0e0e34a53` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

The CAD Modeler launcher uses ACAD editor `71ee2f30d6e13496b90e9e2affda413ca381b0fb` and the source-built OpenCascade worker. On the Galaxy S10+, the menu wraps, status text follows the dark palette, and a bare Save As name takes the current project format. The hosted guest reopened a native project from My Files, edited the rectangle, and saved again. Hosted desktop Chromium created and reopened a six-faced 20 mm extrusion. In the isolated install, the Galaxy S10+, Moto G 5G, emulated touch tablet and desktop also passed the native file cycle. Desktop verified signed-in server reopen for both `.cad` and `.jsketcher.json`. [Phone workflow and screenshots](https://github.com/CC-David-CC/acad/blob/0c8d2aaee47ba262f150aa3d6901f6d5630373b3/docs/webos-qa/PHONE.md)

All 153 overlay paths matched over HTTPS. On box-webhost, `sudo python3 -I -B /var/backups/webos-cad-modeler-phone-ec3deccd5067/deploy-viewer.py rollback` restores viewer `118de96a1ce34be8046cec094e74570868e95f8ddd0e33ef828c2e24e2377627`.

## G-code Preview dark theme and My files opening

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `118de96a1ce34be8046cec094e74570868e95f8ddd0e33ef828c2e24e2377627` | `21bcb293c2ec707c75645a204e8420525e768410` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

G-code Preview `eaccff83f30da5ec2497a18249d39bf023dd8e8e` uses the dark WebOS palette. My files opens `.gcode`, `.gco`, and `.nc` in the viewer through the revision-aware Desktop pin `b954155738dca9a58f32eb090775ecdb6fd94fe1`. Open With keeps Text Editor available. The Galaxy S10+ and Moto G opened a synthetic two-layer path on ksu.codes, rotated and pinched the view, toggled travel, cancelled the picker and kept the preview when the parser rejected a different file. Desktop Chromium repeated the hosted workflow with mouse and keyboard. A real Android picker upload and fresh signed-in reopen with exact source bytes passed in the isolated build. Touch emulation at 820 × 1050 kept the app bar visible. The S10+ and desktop each covered eight of ten workflows. Source-change reload and automatic window restore still need checks for this release.

All 18 changed paths matched over HTTPS. On box-webhost, `sudo python3 -I -B /var/backups/webos-gcode-preview-phone-118de96a1ce3/deploy-viewer.py rollback` restores viewer `c30ba950829b`. [G-code phone screenshots](https://github.com/CC-David-CC/gcode-preview/blob/c53935e0009438570005c643096c0ce988be2e19/docs/webos-qa/PHONE.md) · [Public source pins](https://github.com/CC-David-CC/WebOS/tree/64ec80eb2a682c6eed2b0cad4c9775bcb68a86b2)

## Electronics Design touch and named project saves

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `c30ba950829b52fc2caf07349857e24f27abdcc7c83380f7cb2a29475338beff` | `b21c394e86758479b020dee6ef03102edca07ff2` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

Electronics Design runtime `1240d817db549235df279814ba81b5fac94af058` fits the editor controls and status in compact windows. The Galaxy S10+ portrait, Moto G landscape, and desktop Chromium passed the hosted guest autoroute, named DEZ save and Files reopen. The saved project retained seven parts and ten wires. Fresh isolated signed-in sessions reopened matching server-backed files on both phones and desktop. Sync took about 1.5 to 82 seconds after the local save and now has its own status. Desktop passed eight of ten workflows, including a two-state Arduino LED simulation, the design-rule check, three-view fallback, and protecting the opened original while saving and updating a copy. Touch emulation verified the Arduino lesson at 1024 × 768. The Moto canvas remains short, and the lesson can require scrolling when a warning is displayed.

All 24 changed paths matched over HTTPS. On box-webhost, `sudo python3 -I -B /var/backups/webos-electronics-design-phone-c30ba950829b/deploy-viewer.py rollback` restores viewer `51ee63af95a5`. [Phone screenshots](https://github.com/CC-David-CC/electronics-design/blob/7d141dc3ae2348f1fdf05306f820765a8ec56ede/docs/webos-qa/PHONE.md)

## DRAKON Python touch and Files

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `51ee63af95a5ee14d1326eaadbc69fe00a6f7bdb499bf294377f86d26cdc2641` | `af2694f8213bbe5f5da25ea55ce95b6576e27522` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

DRAKON Python runtime `77c1f11c40abeba9de071b2228387350e4f53660` uses the responsive DRAKON studio and Python's teal accent. Both physical phones passed the hosted guest edit, script export, and Files reopen workflow. Disposable signed-in sessions verified the same-path second save and fresh-session reopening. Python 3 compiled and ran the exported script. It returned `weak` for 12 and 69, and `webos_ok` for 70 and 71. The S10+ in portrait passed four of ten workflows. Desktop Chromium passed eight of ten, including Undo and Redo and importing a legacy Python DRAKON diagram. Touch emulation passed the 1024 × 768 Files cycle and opened Source in a 474 CSS-pixel split window. The Moto diagram area remains short in landscape.

All 21 changed paths matched over HTTPS. On box-webhost, `sudo python3 -I -B /var/backups/webos-drakon-python-portrait-51ee63af95a5/deploy-viewer.py rollback` restores viewer `bf0df3442489`. [Phone screenshots](https://github.com/CC-David-CC/drakon-python/blob/f112027384924525cac853c0ca4498b42a8a0b88/docs/webos-qa/PHONE.md)

## DRAKON JavaScript touch and Files

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `bf0df34424896616c7f119d347d0f61ee3cf8d5f31981d3a51dc9d57dc0965fe` | `469170ea182f0a95b824481d39b0e8181ed88699` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

DRAKON JavaScript runtime `556bdf98757ffb7fbf9af48b873a8fc142b41ff9` reuses the DRAKON phone and tablet layout fix with JavaScript's own colors. Both physical phones completed the hosted guest edit, module export, and Files reopen workflow. Disposable signed-in sessions verified a second save under the same project name and fresh-session reopening. The exported module passed Node's syntax check and returned `webos_ok` for 71 and `weak` for 12. The S10+ in portrait passed four of ten workflows. Desktop Chromium passed eight of ten, including Undo and Redo and legacy DRAKON import. Touch emulation passed the Files cycle at 1024 × 768 CSS pixels and opened Source at 474 CSS pixels in a split window. The Moto canvas remains short in landscape.

All 21 changed paths matched over HTTPS. On box-webhost, `sudo python3 -I -B /var/backups/webos-drakon-javascript-portrait-bf0df3442489/deploy-viewer.py rollback` restores viewer `c3ac341ebf80`. [Phone screenshots](https://github.com/CC-David-CC/drakon-javascript/blob/f14b0877ef3bd045ee18c3f0c3b48d945b46eeb6/docs/webos-qa/PHONE.md)

## DRAKON Bash touch and Files

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `c3ac341ebf800563a58f9eb96d564ae43d7380971a11fd6f8af3161148f67288` | `33b39cf3c198c44856e68d4c16909d28324e1aef` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

DRAKON Bash runtime `cf02726c613ede13b2924a4cb7614a6b1bad277d` fixes contrast and makes toolbar controls fit on phones and in a 474 CSS-pixel tablet split. Galaxy S10+ portrait and Moto G landscape passed the hosted guest edit, export and Files reopen. Disposable signed-in replay verified a second save and fresh-session persistence. The exported script returned `webos_ok` for 71 and `weak` for 12. On the Moto the keyboard left about 118 CSS pixels, and Apply stayed reachable. The diagram canvas remains cramped in phone landscape. Touch at an emulated 1024 × 768 CSS pixels passed the file cycle and the Source tab in the split window. Desktop Chromium passed eight of ten workflows.

All 21 changed paths matched over HTTPS. On box-webhost, `sudo python3 -I -B /var/backups/webos-drakon-bash-portrait-c3ac341ebf80/deploy-viewer.py rollback` restores viewer `ed31e1b4f1c6`. [Phone and tablet screenshots](https://github.com/CC-David-CC/drakon-bash/blob/285d9c8fa321511eeb16ece37ec671c1c52943c4/docs/webos-qa/PHONE.md)

## CADCraft portrait menu and DXF files

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `ed31e1b4f1c6ba81136ed5cea3740977b9b73abed675da6c408cf173496facac` | `d90166ba8af9eba3afd2599c952e87b37e07cc3f` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

CADCraft runtime `e44d26945579273e3406eea8d4488c1e160de138` wraps menu categories in compact windows. On the S10+ at 411 CSS pixels, **Window** and **Help** opened by touch and **Help → About CADCraft** displayed the dialog. Hosted guest drawing, cancel and retry, save and reopen passed. The isolated signed-in phone verified a second edit under the same DXF name, native Open and three exact drawing entities after a fresh sign-in. Desktop Chromium passed DXF reopen and PDF download at 1300 CSS pixels. The tablet layout at 820 CSS pixels displayed every menu category and the WebOS app bar. Native tests reported 328 passes and one ignored check.

All seven changed paths matched over HTTPS. On box-webhost, `sudo python3 -I -B /var/backups/webos-cadcraft-phone-menu-ed31e1b4f1c6/deploy-viewer.py rollback` restores viewer `60e3e542c4f9`. [Galaxy S10+ screenshots](https://github.com/CC-David-CC/cadcraft/blob/bc898737a7acdaad80eb9f0efad2ddbf1d7fc448/docs/webos-qa/PHONE.md)

## Linux X11 phone fit and Files

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `60e3e542c4f9a101ee16265ff57045f8a54ab3770192b01f645cfeee7caf93d9` | `05fd4e3b4c1d6633af23032e1694914ff5c17c5d` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

Linux X11 runtime `d64d9a87947bf5ee3c4c2abdfe9ad84ae5af4ffc` applies the Zoom menu in CSS pixels. S10+ Fit grew from 157 to 411 CSS pixels. The hosted guest booted xterm and xclock, used 100% zoom and touch panning, and opened the xterm-written file in Text Editor from temporary My files. A separate signed-in phone replay reopened the exact file after a fresh sign-in. Chromium passed native xterm input, 1300 and 820 CSS-pixel fit, and a fresh signed-in Files reopen. Five of eight phone workflows and four of eight desktop workflows passed. Broader desktop and guest Chromium work remain stretch goals.

All 14 changed paths matched over HTTPS. The Linux image, v86, Chromium disk and notices reused their verified bytes. On box-webhost, run `sudo python3 -I -B /var/backups/webos-linux-x11-phone-fit-60e3e542c4f9/deploy-viewer.py rollback` to restore Terminal viewer `0d6e25894d6c`. [S10+ screenshots at source revision `f76c5e19c0b5`](https://github.com/CC-David-CC/linux-x11/blob/webos/phone-x11-fit/docs/webos-qa/PHONE.md)

## Terminal phone shell and Linux files

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `0d6e25894d6c740ba41ef51035d930fa8c0587f75d2d2cca28fd86f67b69214e` | `604364f660052dd3543e17bffeb4d3a49f6e60a2` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

Terminal runtime `d8c2271dbbc5658c3ddcdc79a3b148271bfacf63` labels the guest Linux home as temporary and identifies the account workspace for signed-in users. The dark guide opens Files. The S10+ booted the real v86 Linux image, ran commands, wrote and reopened a signed-in Linux home file in Text Editor from a fresh browser, and scrolled with touch. Its 44 CSS-pixel Enter control remained above the keyboard. Chromium at 820 and 1300 tested the shell. Desktop also passed independent PTYs, `stty size` after resize, nano, interrupt and clear, exact guest Downloads and temporary home reset on reload. Phone passed five of twelve documented workflows and desktop passed ten of twelve. Clipboard and dictation remain open.

All 12 changed paths matched over HTTPS. The hosted S10+ verified the guest storage guide and a RAM file write and read. On box-webhost, run `sudo python3 -I -B /var/backups/webos-terminal-phone-files-0d6e25894d6c/deploy-viewer.py rollback` to restore Digital Logic viewer `651878ead137`. [S10+ screenshots at source revision `ab5dfe145b68`](https://github.com/CC-David-CC/terminal/blob/webos/phone-terminal-files/docs/webos-qa/PHONE.md)

## Digital Logic phone truth table and Files

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `651878ead1378ac2357ce062f982978ef1ac09474f7424096e55b64e0d578a73` | `9d3469dc78bb16a66603018c27999ae03aae5549` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

Digital Logic runtime `89b5f22e5f39f753d80493fb3c0dfcbe78f7c691` adds Save As, completes editable and CSV filenames, and gives the dark truth table 13.32:1 contrast. The physical S10+ and Chromium at 820 and 1300 toggled the four half-adder input pairs, exported the exact truth table and reopened a signed-in editable project. The latest label edit saved to the original path. An invalid draft left the simulation and the saved revision intact. Desktop passed ten of twelve workflow groups, including all basic and advanced examples and a two-bit input. The S10+ passed six of twelve.

All 18 changed paths matched over HTTPS. The hosted S10+ guest verified the editable and CSV save flows and ran the revised circuit. On box-webhost, run `sudo python3 -I -B /var/backups/webos-digital-logic-phone-files-651878ead137/deploy-viewer.py rollback` to restore Circuit Simulator viewer `bf112eb8a951`. [S10+ screenshots at source revision `ee5340f81bff`](https://github.com/CC-David-CC/digital-logic/blob/webos/phone-logic-files/docs/webos-qa/PHONE.md)

## Circuit Simulator phone editing and Files

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `bf112eb8a95190ee4c13ce4b3530e570d53ea5571dfc95b35e083e1e97a58948` | `30c1477c48865fe62daab8d354fca004933343d8` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

Circuit Simulator runtime `452a11543aab08bcd321cfed5e42bc82d1e031e9` adds bare-name completion, a compact Save As button and dark native menus. The S10+ and Chromium at 820 and 1300 CSS pixels used the real resistor editor and verified 5 V, 6.66667 V and 7.5 V. They saved an editable circuit, reopened it from My files in a fresh signed-in session and saved a later revision. The phone and 1300 CSS-pixel Chromium saved probe CSV, PNG and SVG. WebOS Keep editing preserves a pending change. Discard changes preserves the saved revision and closes the simulator. Desktop and phone each passed six of ten documented workflows.

All 418 changed paths matched over HTTPS and the guest S10+ replay passed the editable and export workflows. On box-webhost, run `sudo python3 -I -B /var/backups/webos-circuitjs-phone-files-bf112eb8a951/deploy-viewer.py rollback` to restore Circuit Lab viewer `8a8be0c8cf3b`. [S10+ screenshots at source revision `0098960ad719`](https://github.com/CC-David-CC/circuitjs/blob/webos/phone-circuit-files/docs/webos-qa/PHONE.md)

## Circuit Lab phone plot and Files

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `8a8be0c8cf3b1914d14fb1d3b5229e2dc59a95156c11d2527bdee5eeb655a705` | `4756dbfcd0971d0323b34170280504404d6c6569` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

Circuit Lab runtime `23c0d64e8d1b986f73e502928097aba97f538675` uses the desktop color scheme, renders output-voltage plots at the current width and completes bare filenames with `.cir`. The physical S10+ and Chromium at 820 and 1300 CSS pixels verified the 5 V divider, 4.96632 V RC transient and editable Files reopen and same-path save. Desktop also passed supported suffixes, native import, AC and DC sweeps, MOSFET, Stop, and a two-session revision conflict, reaching ten of ten documented groups. The released solver wrapper passed the app's native circuit tests. Eight audit tests and twelve Files association checks passed. The refreshed browser source archive matches the UI source, existing worker, vetted binary and notices.

All 11 changed paths matched over HTTPS. The hosted guest S10+ reopened a temporary circuit and reran the revised 7.5 V result. On box-webhost, run `sudo python3 -I -B /var/backups/webos-circuit-phone-files-8a8be0c8cf3b/deploy-viewer.py rollback` to restore Virtual FPGA viewer `6cf99fdb3286`. [S10+ screenshots at source revision `b48366786843`](https://github.com/CC-David-CC/circuit-lab/blob/webos/phone-spice-files/docs/webos-qa/PHONE.md)

## Virtual FPGA Board phone controls and Files

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `6cf99fdb32864e042400c0a0ff5a6a91a4ff1098062b763253771ab1509933eb` | `c3f89122bae095dea09a336890494f568f5748bf` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

Virtual FPGA runtime `0fc6de7ef384d294e75b4375a709f0aa649c6217` adds Board and Editor navigation, 36 × 44 CSS pixel switch targets, and dark Files status contrast of 13.32:1. The S10+ and Chromium at 820 and 1300 CSS pixels synthesized and routed the Yosys half-adder, verified all four switch inputs, saved both source files and reopened and resaved them in a fresh browser session. My files used Text Editor by default for Verilog and offered Virtual FPGA Board through Open With. Desktop also ran Blink, captured a logic analyzer trace and marker, exported the Verilog netlist, and saved and reopened iCEBreaker PCF. Desktop coverage reached eight of ten workflows.

All 45 changed paths matched over HTTPS. Hosted S10+ replay passed the half-adder and guest file cycle. On box-webhost, run `sudo python3 -I -B /var/backups/webos-fpga-phone-files-6cf99fdb3286/deploy-viewer.py rollback` to restore FPGA viewer `0dea144bcb26`. Then run `sudo python3 -I -B /var/backups/webos-fpga-phone-files-0dea144bcb26/deploy-viewer.py rollback` to restore HDL viewer `a898c954da9c`. [S10+ screenshots at source revision `eaf3f6ecc722`](https://github.com/CC-David-CC/softfpga/blob/webos/phone-fpga-files/docs/webos-qa/PHONE.md)

## HDL Workbench phone waveforms and Files

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `a898c954da9c31a40fe1c2f0936918bbe7cdbecf2d8a6821dd00515652cc3608` | `2935de5e851d2467e674b9c7347a9ff35975393b` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

HDL runtime `919db9a45464d8029764c9560cec56aac54f85cc` fits Run and the waveform to the phone width, raises the keyboard-open editor from 63 to 114 CSS pixels, and follows the WebOS color scheme. The binary studio wrapper suggests the compound `.hdl.json` suffix once. The S10+ and Chromium at 820 and 1300 CSS pixels verified Icarus half-adder results, signal selection, editable save, exact copy, fresh sign-in reopen and same-path resave. Desktop also downloaded VCD, rendered the Gates schematic and saved an exported Digital Logic circuit. Desktop covers seven of ten workflow groups.

The first hosted candidate was rolled back after two quick signal taps triggered Android page zoom. The touch fix kept browser scale steady, and the final viewer spaced the time labels by plot width. All 40 changed paths matched over HTTPS and the hosted guest repeated the project cycle. On box-webhost, run `sudo python3 -I -B /var/backups/webos-hdl-phone-projects-a898c954da9c/deploy-viewer.py rollback` to restore HDL viewer `ee80c48ee9ca`. Then run `sudo python3 -I -B /var/backups/webos-hdl-phone-projects-ee80c48ee9ca/deploy-viewer.py rollback` to restore the RISC-V viewer `f9c8cf22f559`. [S10+ screenshots at source revision `396ed7a9c12c`](https://github.com/CC-David-CC/verisim/blob/webos/phone-hdl-projects/docs/webos-qa/PHONE.md)

## RISC-V Machine Lab phone console and Files

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `f9c8cf22f5593ed315f4a0ab8ca8ea77c65ac1b324f3aa8d212519decc58cc87` | `7b059ea939ede65c23c596ebba2b1c166813e5da` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

RISC-V runtime `9a52b700071c2b0f5bb7db99075dbfab1b79b9a7` gives phone commands 44 CSS pixel targets, adds a direct Console button and completes bare project names with `.riscvlab.json`. The S10+ and Chromium at 820 and 1300 CSS pixels booted the real xv6 image, typed directly in the shell, ran an edited two-line script, saved a project and a copy, and reopened and revised the project at the same path in a fresh signed-in session. A cancelled picker and an invalid suffix preserved the script. The desktop covers four of seven workflow groups. Command limits, project round trips and 12 Files association checks passed.

All 27 changed paths matched over HTTPS. The hosted S10+ verified editable guest projects and the revised script in the real xv6 console. On box-webhost, run `sudo python3 -I -B /var/backups/webos-riscv-phone-projects-f9c8cf22f559/deploy-viewer.py rollback` to restore ESP32 viewer `0bdf8d505ab3`. [S10+ screenshots at source revision `7d23dfa90b56`](https://github.com/CC-David-CC/riscv-rust/blob/webos/phone-xv6-projects/docs/webos-qa/PHONE.md)

## ESP32 Firmware Lab phone startup and Files

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `0bdf8d505ab31aaed5349cf08f8d5162ff206044de4f316657dd36be4f198fc5` | `03e5bbbf7d87022dafb2454e2a40f17b2dc52132` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

ESP32 runtime `d72c20b54526d56ca203b8e9f38d0a4025bf322e` waits for the MicroPython prompt, makes UART output reachable with one tap, and uses the desktop color scheme in its program editor. The S10+ and Chromium at 820 and 1300 CSS pixels ran real MicroPython, saved and reopened `.esp32lab.json` and `.py` files in fresh signed-in sessions, and resaved changed code to the same project path. Generic Python opened in Text Editor after the bound Lab window was closed. The phone and desktop cover four of eight workflow groups. Twelve Files association checks passed. The WebAssembly engine, ROM and MicroPython inputs matched the previous package.

All 81 changed paths matched over HTTPS. The hosted S10+ ran the stock GPIO example and saved, reopened and reran an edited program as a guest. On box-webhost, run `sudo python3 -I -B /var/backups/webos-esp32-phone-programs-0bdf8d505ab3/deploy-viewer.py rollback` to restore Arduino viewer `a204a6b266d4`. [S10+ screenshots at source revision `e03de7f5813a`](https://github.com/CC-David-CC/esp32sim/blob/webos/phone-esp32-programs/docs/webos-qa/PHONE.md)

## Arduino Simulator phone controls and Files

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `a204a6b266d44028661852afd9b0d66ccee981b2df5bd139604e2eba7ae99547` | `860fbb52b9b392944896697e04ebda7cbde6f0d0` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

Arduino runtime `48e47f1b528ff5a76855724d3d1ee932791fab23` completes bare HEX, C and TXT filenames, shows save progress, and keeps the board and D13 label clear of the phone controls. The S10+ and Chromium at 820 and 1300 CSS pixels ran the ATmega328P Blink, D2, AND and Unicode serial examples, recovered from an invalid HEX, and saved and reopened all three formats in a fresh signed-in session. The desktop also passed independent worker state in two windows. Two reference tests and the retained worker and chunk comparisons passed.

All 24 changed paths matched over HTTPS. The hosted guest S10+ ran Blink, saved a bare HEX name in temporary My files and reopened it in Arduino. On box-webhost, run `sudo python3 -I -B /var/backups/webos-arduino-phone-files-a204a6b266d4/deploy-viewer.py rollback` to restore Pico viewer `b0d6980862c3`. [S10+ screenshots at source revision `65853479b501`](https://github.com/CC-David-CC/arduino-simulator/blob/webos/phone-uno-files/docs/webos-qa/PHONE.md)

## Pico Simulator phone Blink and Files

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `b0d6980862c325379f81cc3b3dc58de87f441dfd63b44e91a81917e617eb00a3` | `8a6c55cf7d15f0706398c3f5722bdc73d4805c80` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

Pico runtime `32afc75ad8f118342e9c8952ccf16bb328c6282a` keeps the board status visible, reports Blink stopping, and completes bare project and serial filenames. The S10+ ran actual RP2040 Blink instructions and observed GPIO 25 on and off. On the isolated account server, the phone and Chromium at 820 and 1300 CSS pixels booted MicroPython, exercised serial I/O, synchronized a `.pico` from a bare name, and reopened it through My files in a fresh sign-in. The physical phone resaved the same project with changed flash. All three layouts opened the serial snapshot in Text Editor. The Pico baseline, reference, MicroPython and 12 Files association checks passed.

The hosted S10+ confirmed Blink, its Stop status and launcher return. All eight changed paths matched over HTTPS. The ROM and MicroPython fixtures stayed in the private installation. Run `sudo python3 -I -B /var/backups/webos-pico-phone-files-b0d6980862c3/deploy-viewer.py rollback` on box-webhost to restore RustIRC viewer `2af400c3519e`. [S10+ screenshots at source revision `82b281687dd5`](https://github.com/CC-David-CC/pico-simulator/blob/webos/phone-blink-and-files/docs/webos-qa/PHONE.md)

## RustIRC phone simulator and dark transcript

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `2af400c3519e6cbecafa5ed6bd22586d27825dbb946eb1b214a05756fa52eaa7` | `0d56b76ba162c3da96e8fb33fff93b2d7862cce4` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

RustIRC runtime `a192061447538e0bd525d0eee3713dab32673a39` follows the desktop color scheme, gives phone controls 44 CSS pixels and describes the expected server response as a simulated reply. Its dark transcript measured 14.59:1 contrast. The S10+ and Chromium at 820 and 1300 CSS pixels connected, recovered from invalid names, exchanged exact messages in two simulated channels, disconnected, reconnected and minimized. The loopback browser test passed registration, PING/PONG, JOIN, message transport and cleanup. The current launcher hosts the browser simulation.

All eight changed assets matched over HTTPS. The hosted S10+ replay kept Send above the keyboard and confirmed the simulator's reply status. The viewer cutover preserved the backend process and issuer. On box-webhost, run `sudo python3 -I -B /var/backups/webos-rustirc-phone-simulation-2af400c3519e/deploy-viewer.py rollback` to restore the Chat viewer `fb0e264a3489`. [Hosted S10+ screenshots at source revision `6bd17f67febf`](https://github.com/CC-David-CC/RustIRC/blob/webos/phone-irc-simulation/docs/webos-qa/PHONE.md)

## WebOS Chat phone conversations and dark controls

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `fb0e264a3489529f206b664e518d0aeda76b9ee556387f975a83e370c4b9b468` | `4fb187e4b3b2528c84ca81beb00c7f477f69dd79` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

Chat `d1cad10bada81b5b4e8df9414d7e850b514c039a` gives narrow conversations a separate reading view with Back, preserves the wider sidebar, and applies the system dark scheme to the directory and messages. The Galaxy S10+ searched for the second account, exchanged exact messages and reopened both after refresh. History space with the keyboard open increased from 68 to 173 CSS pixels. Back and Send are 44 CSS pixels high. Conversation text measured 13.32:1 contrast. Chromium at 820 and 1300 CSS pixels passed the exchange and retained the app bar and conversation sidebar. All six Chat service tests passed, including expiry archives and username reuse.

All eight changed paths matched over HTTPS. The hosted S10+ found its disposable peer, sent and received matching messages, reopened the thread after refresh and minimized to the launcher. Box-webhost verified the existing backend process and issuer throughout the viewer deployment. Run `sudo python3 -I -B /var/backups/webos-chat-phone-workflow-fb0e264a3489/deploy-viewer.py rollback` to restore MailCraft viewer `20d3656b91f1`. [Galaxy S10+ evidence](https://github.com/CC-David-CC/webos-chat/blob/webos/phone-chat-workflow/docs/webos-qa/PHONE.md)

## MailCraft phone startup and compose

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `20d3656b91f1267ffbcd6e4e4a749bfeabac80fab85f1cce181561df0b1b5108` | `550a7915f04924ea8c32582e25ae6811d2f519a9` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

MailCraft `061ef3e20940` uses the WebGL adapter's supported texture size, fits the composer above the phone keyboard and keeps delivery status readable. The Galaxy S10+ restored both test inboxes after refresh, composed and delivered an exact message with the keyboard open, and verified that a receive-only reply was denied. Chromium at 820 and 1300 CSS pixels delivered the expected test subjects and bodies. Rapid scripted focus changes in headless Chromium remain a follow-up. All 14 repository checks, including 10,552 passing native tests, and three JMAP gateway tests passed.

All 18 changed paths matched over HTTPS. The hosted S10+ opened MailCraft for a disposable registered account, refreshed into the same JMAP mailbox and returned to the WebOS launcher on minimize. On box-webhost, `sudo python3 -I -B /var/backups/webos-mailcraft-phone-compose-20d3656b91f1/deploy-viewer.py rollback` restores viewer `8069281f64e8`. [Galaxy S10+ evidence](https://github.com/CC-David-CC/mailcraft/blob/webos/phone-mailbox-workflow/docs/webos-qa/PHONE.md)

## Scríobh manuscript files and picker contrast

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `8069281f64e82d68861f8df8f7b079ba240883afe0dc8afbe572395107984a44` | `113ab0e3d702f40748f98e8a226f1913b84918ca` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

Desktop `5def3aef9e819` gives the shared Files picker hint 8.08:1 contrast in dark mode. Scríobh `afc3feb30387` records three of ten workflow groups. The Galaxy S10+ and Chromium at 820 and 1300 CSS pixels edited two ordered chapters in rich text and Markdown, cancelled and retried Save as, saved a bare filename with `.scriobh`, reopened it directly from My files, and updated the same path. A fresh registered session matched the saved project bytes. Two SQLite store tests and 24 Desktop tests passed. The 18 rebuilt Scríobh assets matched the retained runtime.

All three changed assets matched over HTTPS. The hosted guest S10+ replay repeated the manuscript and file cycle. On box-webhost, `sudo python3 -I -B /var/backups/webos-scriobh-picker-contrast-8069281f64e8/deploy-viewer.py rollback` restores viewer `c2acfe055fdc`. [Galaxy S10+ evidence](https://github.com/CC-David-CC/scriobh/blob/webos/phone-manuscript-files/docs/webos-qa/PHONE.md)

## LoveCraft phone writing and backups

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `c2acfe055fdcdc1dbb74f50ca8de657542112cb6300454d89ca0571c47717870` | `b1e42313c656cd27e3f43b1174a79d9264f95931` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

LoveCraft `47d45201b1d0` fits the project dialogs and chapter outline into phone windows. The S10+ wrote a scene with the keyboard open, reopened it after refresh and restored an editable `.prosecraft` backup through the Android picker. Cancelling a second picker preserved the manuscript. Minimizing restored the WebOS launcher. Chromium at 820 and 1300 CSS pixels passed the edit, reopen and backup cycle. Desktop Chromium also exported the manuscript as plain text and reopened an edited outline summary in the preceding optimized preview. All five repository checks passed with 608 native tests passing and 7 existing ignored tests.

The hosted S10+ guest replay passed the manuscript and backup cycle. A desktop guest profile created on the previous viewer reopened the same browser library after the release. All 17 changed assets matched over HTTPS. On box-webhost, `sudo python3 -I -B /var/backups/webos-lovecraft-compact-writing-c2acfe055fdc/deploy-viewer.py rollback` restores viewer `e91a7ae19ef0`. [Galaxy S10+ evidence](https://github.com/CC-David-CC/lovecraft/blob/webos/compact-writing/docs/webos-qa/PHONE.md)

## Earlier November 25 walkthrough release

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `8a2b06a99ca2f9e5382f148991d86da6df1cff81be4d779b85b504f626e0cf5d` | `fe54b6d6b0dced335520726ba293a8ee732c99b3` |
| Backend | `13193818d7f70b10e01934b3e2ca4c2efdbdd2ede46bda671c1171cbfd87abcd` | `32abd64fcdf494a62ab874799b753d580b4933c2` |

The public viewer contains 135 launcher entries. Desktop and compact Chromium on ksu.codes verified Files recovery and retry in Document Editor, SheetJS Spreadsheet, Data Explorer and PDF.js. Anonymous and registered workflows preserved the original file bytes. The paired HTTPS cutover retained the account issuer and backend instance. Safari and physical-device checks are open.

The viewer and backend have independent source assemblies. The backend build uses the exact retained production Accounts and Runtime sources recorded in its manifest. GitHub carries the backend input assembly on `release/ksu-backend-20261125`. The build checkout on `main` includes the password reset validation change and the public source pins below.

## Public source pins for retained Craft inputs

| App | Packaged source | Public build checkout |
| --- | --- | --- |
| figcraft | `2837cfdc32e3f2ec9746e7c047189c7f09f540f6` | `db8862f37ffaaebe51bcdbd1ea042751a2ec1720` |
| lightcraft | `fab135fc4ffb5db1354e95a094b19b4cdaf1f872` | `b3eea00a67affbcb1141ac835be4da46420bb053` |
| vectorcraft | `c54691a43f7ab304f083121064bcbab8b7b33a7b` | `70b4dab5687d8923434240f32a5f1c797f7dee4a` |

FigCraft is tree-identical at both commits. LightCraft and VectorCraft use the same runtime source, with public-source documentation and branding differences. The packaged binaries and exact source are retained with the release.

Use the pinned source and the verified prepared app inputs for incremental builds. The commands in [README.md](../README.md#build-the-core-viewer-from-a-checkout) build the core viewer. The clean-checkout packaging check uses the published WordCraft component build and retains the notices for both transitive math dependencies. A full cold rebuild of all hosted apps remains open.

Hosted rollback restores viewer `e50026bd9dff8e0b7d852a10e2b95fe09ebb733af951f2f2cfae978f5c8c236d` and backend `b7f0816a7eddef49e96a4bfd2b3f8b88a0ddb2770228e4b348154dddf082cd1b` together.

[Live release manifest](https://ksu.codes/viewer-release.json)
