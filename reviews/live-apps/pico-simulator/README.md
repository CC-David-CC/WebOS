# Pico Simulator (RP2040js)

Run the built-in Blink example, observe GPIO 25 on and off, and stop the board.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse | Passed | [4k](4k.png) |

Blink and Stop passed at all four sizes. The bundled example runs without a ROM. Saving a Pico project requires user-provided firmware and ROM. That workflow and physical-board timing were outside this check. On phone the text above the LED separates it from Run and Stop.

Tested in Chromium with disposable accounts on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical touch and device performance remain to be checked.
