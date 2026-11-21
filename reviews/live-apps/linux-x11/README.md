# Linux X11

Launch Programming → Linux X11, check xclock, and use xterm to write a file to the account home.

| Viewport | Input | Guest display | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated tap and keyboard | 336 × 252 CSS pixels. Both guest windows fit, with small terminal text. | [Phone](phone.png) |
| 820 × 1,180 | Emulated tap and keyboard | 766 × 575 CSS pixels. Both guest windows fit. | [Tablet](tablet.png) |
| 1,920 × 1,080 | Mouse and keyboard | 800 × 600 CSS pixels. | [1080p](desktop.png) |
| 3,840 × 2,160 | Mouse and keyboard | 800 × 600 CSS pixels, centered in the larger window. | [4K](4k.png) |

The signed guest reached xterm and xclock after about 68 seconds. Resizing the open window kept the shell session. At each size a pointer or emulated tap focused xterm and a typed command saved a separate file. After closing X11, a fresh Chromium desktop context signed into the same disposable account and verified the exact bytes of all four files. Chromium reported zero page errors.

Physical touchscreen input, the phone software keyboard, cold boot on mobile hardware, and viewport adjustments for readability remain open. See the [fix queue](../FIX-QUEUE.md).

Tested in Chromium on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`.
