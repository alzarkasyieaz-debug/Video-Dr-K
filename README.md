# Video-Dr-K — Perpaduan UMNO–PAS (HyperFrames, 9:16)

Suntingan sinematik 84.5 s daripada rakaman ceramah PRN Melaka (`1101.mp4`, Google Drive).

| Fail | Isi |
|---|---|
| `deliverables/perpaduan-umno-pas-9x16.mp4` | Video akhir 1080×1920, 30 fps, H.264/AAC |
| `deliverables/subtitles.srt` | Subtitle Bahasa Malaysia (forced-aligned) |
| `deliverables/RINGKASAN.md` | Isi utama, headline, kapsyen sosial, garis masa suntingan, QC |
| `REVIEW.md` | Nota semakan & keputusan kreatif |
| `index.html`, `compositions/*.html` | Projek HyperFrames yang boleh disunting |
| `assets/footage/clip-*.mp4` | Enam klip sumber (sudah dipotong, suara dibersihkan) |
| `assets/audio/score.m4a` | Muzik asli (MusicGen), `assets/sfx/` kesan bunyi |
| `data/` | `words.json` (masa perkataan), `camera.json` (jejak kamera), `music.json` (ducking) |
| `edit.json` | Fail suntingan style **Ceramah Politik**: klip, teks, kad, SFX, muzik |
| `.claude/skills/ceramah-politik/` | Style **Ceramah Politik** (`/ceramah-politik`): panduan gaya + skrip pipeline |

## Sunting & render

```bash
npx hyperframes preview --background   # Studio
npm run check
npm run render
```

Nama penceramah: isi `speaker.name` dalam `edit.json`, kemudian bina semula (kosong = tidak dipaparkan).

## Style "Ceramah Politik"

Video ini kini satu style yang boleh diguna semula: taip `/ceramah-politik` dalam Claude Code bersama video ceramah baharu.
Untuk membina semula projek ini daripada `edit.json`:

```bash
S=.claude/skills/ceramah-politik/scripts
python3 $S/build.py .        # index.html + compositions/
python3 $S/srt.py .          # deliverables/subtitles.srt
```

Langkah penuh (potong klip, forced alignment, jejak kamera, muzik) ada dalam `.claude/skills/ceramah-politik/SKILL.md`.
