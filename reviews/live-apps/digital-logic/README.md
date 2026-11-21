# Digital Logic Simulator (DigitalJS)

Toggle the two AND inputs, observe output 0 then 1, and save the circuit.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed using editor picker. Files opened CodeMirror. | [desktop](desktop.png), [Files route](files-route.png) |
| 3,840 × 2,160 | Mouse | Passed | [4k](4k.png) |

The gate output and account save passed at all four sizes. Files opened the phone .logic.json in CodeMirror. The simulator’s own picker reopened the exact phone circuit on desktop and ran the same input check. The 4K circuit occupies a small area at the top left of the maximized window.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical touch and device performance remain to be checked.
