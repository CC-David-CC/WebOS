# FilmCraft

## Original Files and timeline review

Place a WebM clip on an editable timeline and confirm the saved account project.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch and keyboard | Placed one editable video clip and saved the timeline. | [phone](phone.png) |
| 820 × 1,180 | Emulated touch and keyboard | Placed one editable video clip and saved the timeline. | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse and keyboard | Reopened the exact phone project and resaved the timeline with its linked clip. | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse and keyboard | Placed one editable video clip and saved the timeline. | [4k](4k.png) |

A synthetic file-drop event provided the known video. Emulated touch dragged the clip into the timeline on phone and tablet. The account file contained one video track item with the expected duration and unchanged original bytes. A fresh desktop opened the phone file through Files, exercised the playback shortcut and saved a copy. The screenshots show the linked video frame. An interrupted first 4K run was repeated by itself. The phone toolbar and timecode overlap and leave a narrow timeline. File picking by touch, long playback, trimming and export remain open.

Tested in Chromium with a disposable account on ksu.codes release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`.

## Compact timeline and playback

The deployed compact layout gives the selected Project or Preview pane and the timeline the full window width. Play, Save and Fit are visible, and the playhead timecode has its own row. On desktop the original panel layout remains available. [Earlier phone view](before-compact-phone.png)

| Chromium viewport | Storage verified | Deployed interaction and capture |
|---|---|---|
| 390 × 844 | Anon and registered account | Dragged the clip onto the timeline, trimmed its right edge by touch, played, saved and reopened the cut. [Phone](compact-phone.png) |
| 820 × 1,180 | Anon | Trimmed, played, and reopened the edited project using browser storage. [Tablet](compact-tablet.png) |
| 1,920 × 1,080 | Anon and registered account | Placed and saved a clip in the desktop workspace. Reopened the project and its linked media from Files. [Desktop](compact-desktop.png) |
| 3,840 × 2,160 | Anon | Reopened the editable full-size sequence and verified its linked media. [4K](compact-4k.png) |

All six browser runs used a synthetic WebM file supplied through a file-drop event. The emulated touch runs shortened a single clip from 240047520476 to 182893348934 project ticks, and Play advanced its visible timecode. Reopening preserved the clip's native timing and the original media bytes. Registered accounts reopened from a fresh browser session. The native UI library suite passed 361 tests with 1 existing diagnostic ignore.

FilmCraft source `b8bec7e92f1b85b6ffb6a6d84568d836e40fc4e7`, WebOS integration `955ab098710c1a8f5930dab89e3851a51039b028`, deployed viewer `0cd0df1d212b7e92cbfb58fb88fcd134ab263bed6d7349faa4c4058621a38d99`. The public topic descends from the project's existing source-only export and keeps its artwork exclusions and attribution. [FilmCraft source](https://github.com/CC-David-CC/filmcraft/commit/b8bec7e92f1b85b6ffb6a6d84568d836e40fc4e7) · [WebOS integration](https://github.com/CC-David-CC/WebOS/commit/955ab098710c1a8f5930dab89e3851a51039b028)

The hardware check remains open for a real phone or iPad. Use the native file picker, trim with a finger, check playback smoothness, and export the result.
