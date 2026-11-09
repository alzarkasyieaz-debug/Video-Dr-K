# REVIEW — Perpaduan UMNO–PAS (9:16, 84.5 s)

## Creative calls
- **Story:** hook (16:00, "politik persepsi… yang rugi rakyat") → issue (02:11, UMNO + PAS) → evidence (02:22, 3.6 + 1 = 4.6 juta, labelled as the speaker's figures) → argument (03:19 and 03:52, Hijrah: masjid, then persaudaraan) → climax (08:02, "tuntutan Allah SWT") → close (18:55, "bukan perpaduan untuk politik semata-mata").
  The hook is out of chronological order; it is a self-contained statement from the RCI/Tabung Haji passage. Everything after it is chronological.
- **Not built:** a cut around the Ayer Molek / Hang Tuah Jaya seat arithmetic (05:18–05:47), and one around the RCI and Tabung Haji claims (08:48–16:00). Both are contested factual claims that would need verification before being shown as cards.
- **Dropped on purpose:** "Kita padu bukan hanya kerana ___" (08:00). Three passes disagreed on the last word (politik/kualiti), so the climax starts on the next sentence.
- **Camera:** OpenCV HOG person tracking at 5 fps, Gaussian-smoothed (σ≈1 s). The head is placed at y≈940 px (hook 900), with zoom capped at 1.8× because the source is 720p. Clamped so frame edges never show.
- **Look:** `deep-contrast` at 0.45 with highlights −0.30 (the tent lamp), shadows +0.14, slightly cool; vignette 0.36, grain 0.12, all via `media-treatment`. Navy legibility gradients top and bottom; gold accent lines; Anton / Bebas Neue / Montserrat.
- **Music:** original, made with local MusicGen-medium, because HeyGen sign-in did not complete (two device codes expired). Four cues are crossfaded (dark → building → climax → resolution) and ducked by a volume lane computed from the word timings.

## Measured vs looked at
- `npx hyperframes check`: 0 errors; 1 warning kept (`composition_file_too_large` on captions.html, which holds all 45 caption groups so Studio shows them on one track).
- Rendered file: H.264 1080×1920 30 fps + AAC 48 kHz, 84.5 s. First render: −14.4 LUFS integrated, true peak −1.0 dBTP, no clipping. Delivered v2 (music bed +~3 dB): −14.7 LUFS integrated, true peak −1.0 dBTP, no clipping; speech ≈ −13…−15 LUFS momentary, music-only gaps ≈ −18…−22.
- Frames looked at: two snapshot passes plus a strip across every cut of the render (−0.2 / +0.2 s).
- **Not heard by anyone.** The sound was measured, not listened to. Listen to the music cues and SFX before publishing.

## Weakest shot
- Climax (60–70 s): he stands far right in the source, so at 1.8× the clamp keeps him right of centre. With more time I'd use a bigger lead-room shift or a split layout.
- 720p source at 1.5–1.8× is soft on the face. An AI upscale of the six clips would help.

## Kept on purpose
- The hook headline overlaps captions in meaning ("yang rugi rakyat" appears in both). That's the viral convention: the headline is for muted viewers, the captions for every word.
