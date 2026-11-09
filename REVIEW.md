# REVIEW: Parliament speech short (Parit, RMK13)

## Creative calls
- **Source:** of the four Drive videos, I built from `Projek-Projek Parit .mp4`. It is the only one whose subject matches the brief's drainage/development example, and the only Dewan Rakyat clip small enough to work on quickly. Not built: `Kamar Khas - Pengezonan Padi`, `Industri Seri Iskandar`, `Bahas Ucapan Muktamar 69` (the last is a party muktamar, not Parliament).
- **Length 60.0 s** against a 47 s source. Nothing is invented: a 6.4 s cold open repeats the speaker's own strongest line (source 15.08–21.48 s), the speech then plays **uncut** (6.4–53.44 s), and a 6.6 s end card follows on the held last frame. The 60–90 s target is met at its minimum. Anything longer would need padding or fabrication.
- **Framing:** the 16:9 4K plate is recomposed as a 1620×2160 crop around the speaker. A navy information band at the top holds every card, the face sits in the middle, and captions sit under the chin (y 1150–1326). No card touches the face.
- **Scene mapping vs. the brief:** brief scenes 2 and 4 are merged (the "facts" are the three projects he names, shown as they are spoken). The speech has **no numbers or statistics**, so no stat cards were made.
- **No date** on screen (not verified). No Parliament logo or crest. Credit "Rakaman: RTM" on the end card.
- **Music:** none (no licensed source reachable: HeyGen not signed in). Sound effects only, from the bundled HyperFrames library. The slot and levels are documented in `deliverables/PAKEJ-PRODUKSI.md` §8.

## Measured vs. looked at
- `npx hyperframes check`: 0 errors. Kept warning: `line_unread` on the RMK13 card. It builds word by word from 2.2 s and is on screen about 3.6 s in total, but the final word holds only 1.5 s because the speaker moves straight on.
- Speech audio normalised to −16.8 LUFS integrated, −1.2 dBFS peak (measured). Sound effects at 0.16–0.3 gain; the bundled files clip internally. **The mix was measured, not heard.**
- Snapshots read: beats sheet, phone sheet (360 px), seams, and spot checks at the edited moments.
- Transcript: whisper large-v3 (ms) plus a second pass on 21–31 s. "Puan Timbalan Yang di-Pertua" was corrected by model, not by ear.

## Weakest shot
The source is a single locked-off broadcast shot of a man reading, so all motion comes from punch-ins and graphics. Close-ups at 1.7–1.78× are upscaled about 1.3× and look soft. With more time: add a licensed orchestral bed (the biggest gap), and use B-roll of the actual sites (Klinik Kesihatan Parit, Bandar Universiti) if the person has real footage.
