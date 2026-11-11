---
name: kuliah-cinematic
description: House style and pipeline for turning a full Islamic lecture (kuliah, ceramah, tazkirah) into 60–120 s vertical 9:16 knowledge clips — Premium Islamic Cinematic Documentary look (emerald/gold/navy), karaoke Malay subtitles, key-point and Arabic reference cards, cleaned voice and an original ambient bed. Use whenever the user asks to clip, cut, edit or style a lecture/kuliah video, or says "guna style yang sama / style kuliah".
---

# Kuliah Cinematic — gaya & aliran kerja tersimpan

Gaya ini diluluskan oleh pengguna (siri *Bahrul Mazi*, Nov 2026). Gunakan semula tanpa mereka bentuk baharu
melainkan pengguna minta. Contoh siap: `exports/KULIAH_01_*.mp4` … `KULIAH_12_*.mp4`, laporan `LAPORAN_KERATAN.md`.

## Gaya visual (jangan ubah tanpa diminta)

| Unsur | Nilai |
|---|---|
| Kanvas | 1080×1920, 30 fps, H.264 + AAC stereo, 60–120 s (jumlah ≤ 120 s) |
| Palet | Deep Emerald `#073B35`, Islamic Gold `#D5B36A`, Dark Navy `#081726`, White `#FFFFFF`, Subtitle Yellow `#FFE16B` |
| Fon | Montserrat 600/800/900 (`assets/fonts/`), Amiri 700 untuk Arab & ﷺ |
| Cover 0–2.6 s | Poster penuh pada bingkai 0 (= thumbnail): scrim navy→emerald, bingkai emas berganda + bintang di 4 penjuru, "KULIAH KITAB …" emas, cip kategori emas pejal, tajuk Montserrat 900 berpusat (saiz baris dimuatkan automatik, maks 136 px, kata kunci `#FFE16B`), garis emas, nama siri di bawah; penceramah kelihatan di tengah (×1.22). Baris cover boleh diatur dengan `cover_lines`. Keluar: tajuk naik & pudar 2.3–2.7 s, kemudian close-up ×1.50 |
| Header | Selepas cover (2.9 s) tajuk mampat 44 px di kiri atas (top 192, lebar 820) |
| Gambar cover | `exports/covers/KULIAH_XX_<SLUG>_COVER.jpg` (bingkai 0, 1080×1920) untuk thumbnail Reels/TikTok |
| Lower-third | 5.6–11.1 s, bar emas + kotak navy, `speaker` / `speaker_role` |
| Kad poin | top 372, lebar 960, navy 84%, border kiri emas 8 px, label emas 28 px + teks 44 px; masuk 0.5 s slide-up/scale, keluar 0.35 s |
| Kad Arab | Amiri kuning (62/50/42 px ikut panjang), terjemahan, rujukan emas; kamera melebar ×1.16 supaya wajah di bawah kad |
| Kamera | Close ×1.48–1.50 (wajah ~y770) ↔ sederhana ×1.28–1.30 (wajah ~y860) semasa kad poin; push-in perlahan dalam setiap shot |
| Subtitle | Montserrat 800 64 px, putih, outline hitam 12 px, max 2 baris, band y 1118–1318; perkataan aktif kuning `#FFE16B` + pop ×1.1 (kata kunci ×1.2); kumpulan ≤6 perkataan/36 aksara, tiada perkataan yatim |
| Hiasan | Scrim atas/bawah navy, cahaya emas lembut, bintang 8 penjuru berputar perlahan, corak geometri emas 14% di bawah |
| Outro | ~1–2 s navy: bintang emas, nama siri, tajuk |
| Audio | Suara: highpass 80, afftdn, kompresor, −16 LUFS. Muzik: `assets/music/pad.m4a` (original, `tools/make_music_bed.py`) volume 0.1 (~24 dB bawah suara), fade 2 s / 2.5 s |

Footage sumber menegak dianggap wajah di (595,1088) selepas dibesarkan ke 1080×1920 (`FACE_X/FACE_Y` dalam
`tools/build_clip.py`). Untuk rakaman lain, ambil satu bingkai dan kemas kini nilai ini dahulu.

## Rujukan visual

Sebelum mereka bentuk, lihat `reference/covers.jpg` (12 cover yang diluluskan) dan `reference/frames.jpg`
(cover → header + lower-third → kad poin → kad Arab → subtitle → outro). Hasil baharu mesti kelihatan sama.

## Wajib tukar untuk kuliah baharu

Medan ini bertulis untuk siri *Bahrul Mazi* — tukar dalam setiap spec, jangan biarkan nilai lalai:
`cover_kicker` (lalai "KULIAH KITAB BAHRUL MAZI"), `cover_sub` (lalai "Syarah Mukhtasar Sahih at-Tirmizi"),
`speaker`, `speaker_role`, `series`, dan `FACE_X/FACE_Y` dalam `tools/build_clip.py` jika sudut kamera berbeza.
Jika nama penceramah diketahui, letak dalam `speaker`.

## Aliran kerja

1. **Muat turun** rakaman (Drive: `drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t`).
   Jika rangkaian menyekat Drive, tukar sesi ke environment *Video-Dr-K* (ia membenarkan Drive & Hugging Face).
2. **Transkrip penuh** untuk analisis seluruh kuliah: `tools/transcribe.sh full <lecture.mp4> <dir>`.
3. **Analisis & skor** (25 ilmu / 25 kejelasan / 20 kesempurnaan / 15 relevan / 10 penyampaian / 5 keunikan);
   ambil ≥80, satu isi = satu video, mula & tamat pada sempadan ayat.
4. **Transkrip perkataan** setiap keratan (padding ±3 s): `tools/transcribe.sh clip <lecture.mp4> <from> <to> clips/whisper/wXX.json`.
   Whisper medium kadang-kadang tercicir petikan Arab — jika ya, cuba tetingkap yang dianjak sedikit.
5. **Spec** `clips/KULIAH_XX.json` daripada `clips/TEMPLATE.json`: tulis `text` yang disemak (loghat dinormalkan
   hanya jika maksud jelas; perkataan tak jelas ditinggalkan), poin 1–3, kad Arab hanya untuk lafaz yang disahkan.
   Kad tidak bertindih dengan hook (mula ≥ 5.6 s).
6. **Bina**: `python3 tools/build_clip.py clips/KULIAH_XX.json --source <lecture.mp4>` (`--no-media` untuk bina semula teks/grafik sahaja).
7. **Semak**: `cd videos/KULIAH_XX && npx hyperframes check` dan `npx hyperframes snapshot --at …` pada setiap kad — pastikan wajah tidak dilindungi.
8. **Render**: `tools/render_all.sh 01 02 …` → `exports/KULIAH_XX_<SLUG>.mp4` + `.srt` (dua runner selari muat pada 4 teras; jangan bunuh proses induk, render akan batal).
9. **Laporan**: tambah entri dalam `clips/report_meta.json` (skor, 5 tajuk, pengajaran, kapsyen, rujukan) dan jalankan `python3 tools/make_report.py`.

## Amanah ilmu (wajib)

- Jangan reka subtitle, lafaz hadis, rujukan atau nombor hadis; nombor hadis dalam laporan ditanda **[semak]**.
- Kekalkan status riwayat yang disebut penceramah (cth. *mursal*) pada kad.
- Jangan jana visual nabi, malaikat atau perkara ghaib; hanya rakaman asal, tipografi dan corak geometri.
- Bahagian yang terlalu kabur (loghat berat, audio rosak) → senaraikan untuk semakan manual, jangan render.
