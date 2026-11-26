## DeckCraft presentation filenames and save footer

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `07803e135d2f51e17599a671a9af93ae92cd3b64aacf2bbd41d5427961b17118` | `b863136c09ad0a851a216501cd692c0d5e952226` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

DeckCraft `cb717c1d` adds the suggested extension to a bare name and removes the 14-pixel margins above and below the WebOS save footer. The retained native engine and shared host inputs at `8c120b55` reproduced the prior bundle. The S10+ typed a slide title with the Android keyboard, canceled Save As, saved the editable PPTX and reopened it from My files. Reading View displayed the saved slide, the Android document picker imported it, and File → Print saved a one-page PDF copy. Tablet and desktop Chromium passed the editable file cycle. The stored PPTX contained the title at all three widths.

Five changed assets matched over HTTPS. Hosted Chromium replayed the guest Files workflow. On box-webhost, `sudo python3 -I -B /var/backups/webos-deckcraft-phone-presentation-07803e135d2f/deploy-viewer.py rollback` restores viewer `227df9c7785b`. [DeckCraft phone evidence](https://github.com/CC-David-CC/deckcraft/blob/webos/phone-presentation-files/docs/webos-qa/PHONE.md)

