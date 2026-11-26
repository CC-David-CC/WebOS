# PdfCraft on the Galaxy S10+

PdfCraft now adds `.pdf` to a bare save name and removes the margins around the dark file status footer. The S10+ opened a DeckCraft PDF from My files, zoomed, added text, canceled Save As, and saved and reopened a copy. Chromium at 820 and 1300 CSS pixels repeated the edit and file cycle. All three saved files contain the added text.

- Runtime source `c3f655e957604f11c227923c10d3578f64a2f0ee`, bundled in viewer `66dcd85df4ada4b3a50394167475c474ac29f00bf3e9f4646d0b1ca0d3912ccd`.
- Six assets matched over HTTPS. Hosted Chromium opened the edited PDF from guest My files.
- The native tool search palette still clips at 411 CSS pixels.
- On box-webhost, `sudo python3 -I -B /var/backups/webos-pdfcraft-phone-files-66dcd85df4ad/deploy-viewer.py rollback` restores the preceding NoteCraft viewer `1899c82ed7a8`.

[Physical-phone screenshot and workflow](https://github.com/CC-David-CC/pdfcraft/blob/webos/phone-pdf-files/docs/webos-qa/PHONE.md)
