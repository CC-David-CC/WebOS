# WordCraft

Type text into the document, save the DOCX to My files and reopen the phone revision in a fresh desktop browser. Append text and verify the original text remains.

| Viewport | Input | Result | Screenshot |
|---|---|---|---|
| 390 × 844 | Emulated touch | Edit and account save passed | [phone](phone.png) |
| 820 × 1,180 | Emulated touch | Edit and account save passed | [tablet](tablet.png) |
| 1,920 × 1,080 | Mouse | Edit and account save passed | [desktop](desktop.png) |
| 3,840 × 2,160 | Mouse | Edit and account save passed | [4k](4k.png) |

The phone capture still shows a clipped ribbon and a horizontally scrolling page. The review used the F12 and Ctrl+S shortcuts to verify the account workflow. Virtual keyboard, touch-only saving, and physical printing remain to be checked.

The browser used a disposable account and a fresh context at each size. Physical-device input, software keyboard and GPU performance still need hardware testing.

Desktop release `0234bfd516a2da8f4b78462518613c346c8027bf2689b04ee7a752d48726ae4b`. Tested app bundle `70c48174a24e6c8eedc4f55d4e0db53b3d0bbac64e3644804efc973238b5cbf7`.

## Browser dictation

On November 21, 2026, a disposable account on ksu.codes dictated into CodeMirror, then into a selected word in WordCraft in the same Chromium tab. WebOS Voice Input transcribed a prerecorded speech fixture locally. A mouse drag selected the word before the user opened System Tools → Voice input. That menu command started recording directly and the surrounding text stayed intact. Undo restored the selected word and Redo restored the transcript. Moving the caret during another recording discarded that recording. The filename field in Save As accepted dictation, and the saved DOCX reopened from account Files with the expected text. The microphone tracks ended and Chromium reported no page error. This run used an emulated microphone. Physical microphone and mobile keyboard behavior remain separate checks.

![WordCraft with the dictated sentence between the original surrounding words](dictation.png)
