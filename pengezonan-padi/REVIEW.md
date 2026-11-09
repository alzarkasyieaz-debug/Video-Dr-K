# REVIEW: Kamar Khas, Pengezonan Padi (Parit)

## Creative calls
- 17:40 session cut to **89.0 s** from five complete sentences of the MP (from the opening speech and the follow-up question). Order is narrative (hook → facts → problems → proposal → target); the original timestamp of each clip is in `deliverables/PAKEJ-PRODUKSI.md` §6.
- The deputy minister is **not shown on camera**. His answer appears only as an attributed end-card box: 3 RMK13 irrigation projects; floor price RM1,300 → RM1,500/tan metrik. Both were re-checked with whisper large-v3. The `small` model had misheard RM2.6 bilion as "26 bilion"; that figure is not used on screen.
- "Lebih 50%… hasil padi yang amat mengecewakan" is shown as a quote with a "Petikan ucapan" tag, not as a statistic, because the speech does not say 50% of what.
- Same design system as the first video (navy band, Anton/Montserrat, gold/yellow) so the two read as one series.
- No music: no licensed source reachable (HeyGen not signed in). Bundled SFX only.

## Measured vs. looked at
- `check`: 0 errors. Kept warning `line_unread` on the floor-price card. It builds word by word over 7 s, and the final chip holds 2 s before the cut.
- Captions: hand-corrected text matched to whisper words by position; the script stops on any count mismatch. The full-speech SRT is automatic and only lightly corrected.
- Audio: segments gained +1.1 dB from −17.1 LUFS source. The mix was measured, not heard.

## Weakest shot
The Kamar Khas footage is soft and dim (a 4K file with SD-like detail). Close-ups at 1.8× look smeary. The grade lifts exposure and shadows slightly. With more time: B-roll of the actual paddy fields (Bota Kiri, Titik Gantung) from the person, and a music bed.
