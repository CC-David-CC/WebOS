# Live app fix queue

| App | Impact and reproduction | Status and retest |
|---|---|---|
| SoundCraft | High. With an armed track, browser recording lacks an audio input path. | The hosted editor now reports the missing input and survives Record. Verify real microphone capture and audible playback on hardware. |
| SoundCraft | High. Press Close and Discard after attempting Record. The edited window took 23.7 seconds to close on software-rendered Chromium. | Open. Profile the delay through the two clicks and repeat on hardware. [Hosted review](soundcraft/README.md) |
| Weather Maps | The layer panel intercepted the start of the forecast slider at several tablet widths. | Fixed on ksu.codes. Seven touch-emulated widths passed. Physical iPad confirmation is open. |
| WordCraft | Open Office → WordCraft in a 390 × 844 touch viewport. The rightmost ribbon group clips, and footer text and controls overlap. [Phone screenshot](wordcraft/phone.png) | Open. Retest compact writing controls, readable status, virtual keyboard, and opening the same saved document on desktop. |
