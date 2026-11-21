# FilmCraft

Place a WebM clip on an editable timeline and confirm the saved account project.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch and keyboard | Placed one editable video clip and saved the timeline. | [phone](phone.png) |
| 820 × 1,180 | Emulated touch and keyboard | Placed one editable video clip and saved the timeline. | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse and keyboard | Reopened the exact phone project and resaved the timeline with its linked clip. | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse and keyboard | Placed one editable video clip and saved the timeline. | [4k](4k.png) |

A synthetic file-drop event provided the known video. Emulated touch dragged the clip into the timeline on phone and tablet. The account file contained one video track item with the expected duration and unchanged original bytes. A fresh desktop opened the phone file through Files, exercised the playback shortcut and saved a copy. The screenshots show the linked video frame. An interrupted first 4K run was repeated by itself. The phone toolbar and timecode overlap and leave a narrow timeline. File picking by touch, long playback, trimming and export remain open.

Tested in Chromium with a disposable account on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`.
