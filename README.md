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
| `tools/` | `build.py` (jana HTML), `music.py` (gabung muzik + ducking), `srt.py` |

## Sunting & render

```bash
npx hyperframes preview --background   # Studio
npm run check
npm run render
```

Nama penceramah: isi `data-var-text="speakerName"` dalam `compositions/outro.html` (kosong = tidak dipaparkan).

`python3 tools/build.py` menulis semula `index.html` dan `compositions/` — selepas itu jalankan semula
`npx hyperframes media-treatment --selector video --grading '<lihat REVIEW.md>' --apply`.
