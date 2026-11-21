# Live app fix queue

| App | Impact and reproduction | Status and retest |
|---|---|---|
| SoundCraft | High. With an armed track, browser recording lacks an audio input path. | The hosted editor now reports the missing input and survives Record. Verify real microphone capture and audible playback on hardware. |
| SoundCraft | High. Press Close and Discard after attempting Record. The edited window took 23.7 seconds to close on software-rendered Chromium. | Open. Profile the delay through the two clicks and repeat on hardware. [Hosted review](soundcraft/README.md) |
| Weather Maps | The layer panel intercepted the start of the forecast slider at several tablet widths. | Fixed on ksu.codes. Seven touch-emulated widths passed. Physical iPad confirmation is open. |
| WordCraft | Open Office → WordCraft in a 390 × 844 touch viewport. The rightmost ribbon group clips, and footer text and controls overlap. [Phone screenshot](wordcraft/phone.png) | Open. Retest compact writing controls, readable status, virtual keyboard, and opening the same saved document on desktop. |
| Files | Medium. Select one file in the default tablet window at 820 × 1180. The toolbar wraps and the selected row moves down 38 CSS pixels. | Open. Reserve consistent toolbar space at this window width and verify the row stays under the pointer on selection and deselection. [Tablet screenshot](files/tablet.png) |
| Linux X11 | Medium. On a cold launch the screen can sit at SeaBIOS with “Starting xterm and xclock…” and then turn black before the graphical clients appear. A desktop user reported the wait looked like a failed boot. | Open. Measure download, guest boot, Xorg and first usable xterm separately. Show the current stage during the display switch and retest on a slower device. |
