# Gravity Pinball

Start, charge and release the plunger, use one nudge and pause.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Passed | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse | Passed | [4k](4k.png) |

The plunger charge, nudge count and pause status all updated. Touch users have to scroll between the table, status and flipper controls on phone. The Start/Pause and Nudge buttons keep their initial accessible names when their visible labels change.

Tested in Chromium using a disposable account on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Physical-device input and performance remain to be checked.
