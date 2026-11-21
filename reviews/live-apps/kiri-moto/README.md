# Fabrication Studio (Kiri:Moto)

Add a 20 mm cube, run the slicer and save a workspace.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed through the editor picker. Files opened CodeMirror. | [desktop](desktop.png), [Files route](files-route.png) |
| 3,840 × 2,160 | Mouse | Passed | [4k](4k.png) |

The size check matched 20 mm on each axis. The test used the real in-app File menu to add the cube and save the workspace. It started the normal slice command through the editor API and verified the completion event. The desktop opened the exact phone workspace through the in-app picker, matched both saved objects by their dimensions, added a cube, sliced and saved a new workspace. Files sent the .kiri file to CodeMirror. The toolstrip and open File menu compete with the build plate at phone width.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical touch slicing controls, printer profiles and generated toolpaths remain to be reviewed.
