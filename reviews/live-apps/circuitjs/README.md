# Circuit Simulator (CircuitJS)

Load the RC low-pass example, verify the simulation clock advances, and save the circuit.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Simulation and save passed. Menus obscured circuit. | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Simulation and save passed. Menus obscured circuit. | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed using editor picker. Files opened CodeMirror. Menus obscured circuit. | [desktop](desktop.png), [Files route](files-route.png) |
| 3,840 × 2,160 | Mouse | Simulation and save passed. Menus obscured circuit. | [4k](4k.png) |

Simulation time advanced and the account save passed at all four sizes. The menus appear as long lists and obscure the circuit drawing. This is visible even though the simulator canvas has positive dimensions. Files opened the phone circuit in CodeMirror. The simulator’s own picker reopened it on desktop, and the simulator ran and saved a copy.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical touch and device performance remain to be checked.
