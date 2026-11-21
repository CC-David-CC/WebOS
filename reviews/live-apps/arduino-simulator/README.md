# Arduino Simulator (AVR8js)

Run Blink, observe both D13 LED states and save the loaded Intel HEX.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed using editor picker. Files opened CodeMirror. | [desktop](desktop.png), [Files route](files-route.png) |
| 3,840 × 2,160 | Mouse | Passed | [4k](4k.png) |

The firmware ran and saved at all four sizes. Files opened the phone HEX in CodeMirror. The simulator’s Open HEX from My files loaded the exact phone file on desktop, ran it again and saved a copy. On phone the control and help stack places the board below the initial viewport.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical touch and device performance remain to be checked.
