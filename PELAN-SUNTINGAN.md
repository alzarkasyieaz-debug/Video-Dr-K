# PARLIAMENT CINEMATIC IMPACT — “Suara Pesawah Parit”

**Wakil rakyat:** YB Haji Muhammad Ismi bin Mat Taib (nama seperti pada plat meja di Dewan)
**Jawatan:** Ahli Parlimen Parit, Perak
**Sumber:** 2 rakaman dari folder Google Drive (720×1280, HEVC)
- **Klip A** `6748990028085637131.MP4` (111.3 s): pengangguran belia dan kualiti pekerjaan
- **Klip B** `-7279502545541225489.MP4` (130.8 s): potongan harga padi, pengairan dan pengezonan jelapang padi

**Output:** MP4 H.264, 1080×1920, 30 fps, **119.6 s** → `renders/suara-pesawah-parit-1080x1920.mp4`

---

## A. Isi paling penting (dengan timestamp asal)

Video ini memfokuskan **satu isu: Klip B (pesawah padi)**. Klip B ada bukti fizikal (bil belian padi yang ditunjukkan di Dewan), angka yang konsisten dan satu tuntutan yang jelas. Klip A ialah isu berasingan, jadi ia disimpan untuk episod kedua (lihat bahagian I) dan tidak dicampur, supaya konteks tidak terkeliru.

| # | Isi | Timestamp asal (Klip B) | Petikan |
|---|-----|-------------------------|---------|
| Hook | Luahan pesawah | 01:57.25 – 02:02.45 | “YB, kalau tiga musim… tiga musim kami tak tanam padi, habislah kami. Matilah kami.” |
| 1 | Bukti bil & lokasi | 00:00.75 – 00:16.3 | “Berkaitan dengan masalah sawah padi. Bersama sahabat saya ini ada… bil belian padi, oleh Saudara Muhammad Nasir bin Kamarudin. Pesawah di tempat saya, Batu 13 Bota Kiri.” |
| 2 | 7,600 kg dituai, 72% dipotong | 00:16.3 – 00:37.95 | “…dia mendapat 7,600 tan… 7,600 kilo. Tetapi potongan yang dikenakan ialah 72 peratus, iaitu 5,472 dipotong. Hanya yang dikira ialah 2,128 kilo.” |
| 3 | RM11,400 → RM3,192; 65% → 72% | 00:37.95 – 00:59.27 | “Sepatutnya Encik Muhammad Nasir ini dapat RM11,400, tapi dia hanya mendapat RM3,192. Dulu saya dah bawa satu bil belian padi, 65% potongan. Malangnya terdapat potongan yang lebih teruk lagi, iaitu 72%. Potongan pemutuan ini.” |
| 4 | Punca utama: pengairan | 01:13.40 – 01:24.20 | “Saya telah membuat sesi libat urus kepada beberapa pihak yang berkenaan, menyatakan bahawa yang antara puncanya ialah pengairan. Punca utamanya ialah pengairan.” |
| 5 | Pengezonan: Bajet pertama → Bajet kelima, belum dilaksanakan | 01:28.87 – 01:48.55 | “Yang Amat Berhormat Tambun, Perdana Menteri telah pun menyebut tentang pengezonan jelapang padi bagi Parit ini pada pembentangan Bajet yang pertama. Sekarang dah Bajet kelima… malangnya masih lagi tidak dilaksanakan sehinggalah ke hari ini, menyebabkan nasib pesawah ini menjadi lebih teruk.” |
| 6 | Kemuncak & tuntutan | 01:48.55 – 02:10.45 | “Dah ada yang dua musim padi tidak menanam padi. Dua musim. Mereka menyatakan kepada saya, ‘YB, kalau tiga musim…’ … Tuan Yang di-Pertua, saya mohon supaya pengezonan jelapang padi disegerakan di kawasan saya.” |

**Bahagian yang dibuang (tanpa mengubah maksud):** 00:59.3–01:13.4 (rayuan kepada kementerian: “turunlah, lihatlah pesawah… kenang jasa mereka”) dan 01:24.2–01:28.9 (“Jadi minta ambil perhatian perkara ini” serta jeda). Kedua-duanya rayuan umum yang tidak menambah fakta. Ia boleh dikembalikan jika had 2 minit ditarik.

**Semakan angka (dalaman, daripada ucapan sahaja):** 72% × 7,600 = 5,472 ✓ · 7,600 − 5,472 = 2,128 ✓ · 11,400 ÷ 7,600 = 3,192 ÷ 2,128 = 1.50 ✓. Angka ini konsisten antara satu sama lain. Tiada angka luar ditambah, dan harga sekilo tidak dipaparkan kerana tidak disebut.

## B. Tajuk video

**Utama:** “Kalau Tiga Musim Tak Tanam Padi, Habislah Kami” — Ahli Parlimen Parit Desak Pengezonan Jelapang Padi Disegerakan

Alternatif: “7,600 Kilo Dituai, 72% Dipotong: Suara Pesawah Parit di Dewan Rakyat”

Kapsyen media sosial (cadangan): *Pesawah di Bota Kiri, Parit menuai 7,600 kg padi, tetapi 72% dipotong. Ahli Parlimen Parit membawa bil belian padi ke Dewan Rakyat dan memohon pengezonan jelapang padi disegerakan. #DewanRakyat #Parit #Pesawah #Padi*

## C–G. Timeline scene (output) + audio asal + arahan

Semua masa ialah masa output. Audio asal sentiasa menjadi audio utama (dibersihkan: high-pass 80 Hz, noise reduction FFT, kompresor lembut, loudnorm −16 LUFS).

| Scene | Masa output | Sumber (Klip B) | Kamera / Hyperframe | Grafik & kinetic typography (G) | Bunyi |
|---|---|---|---|---|---|
| **S1 Hook** | 0.00–5.20 | 01:57.25–02:02.45 | Close-up muka (skala 1.30→1.38), punch-in 1.5 pada “habislah”, 1.6 + gegaran halus pada “matilah” | Kicker “LUAHAN PESAWAH KEPADA YB · DEWAN RAKYAT”; “YB, KALAU TIGA MUSIM…” / “…KAMI TAK TANAM PADI,” / **HABISLAH KAMI.** / **MATILAH KAMI.”** (emas 3D, slam rotateX) | Impact pada frame 0, whoosh + impact pada setiap slam |
| **S2 Identiti** | 5.20–13.55 | 00:00.75–00:09.10 | Kilatan cahaya pada potongan, frame penuh, push-in perlahan 1.00→1.06, light sweep | Lower third premium: “DEWAN RAKYAT MALAYSIA” / **HAJI MUHAMMAD ISMI BIN MAT TAIB** / “AHLI PARLIMEN PARIT, PERAK” + kilauan; chip “ISU: MASALAH SAWAH PADI” | Whoosh pada potongan, pop pada lower third |
| **S3 Isi 1–2: Tuaian** | 13.55–42.40 | 00:09.10–00:37.95 | Punch-in 1.14, keluar untuk kad lokasi; **mod Hyperframe** dari 23.9 s: rakaman menjadi panel berbingkai emas “RAKAMAN ASAL” di atas, grafik di bawah | Chip “BUKTI: BIL BELIAN PADI”; kad lokasi “BATU 13, BOTA KIRI · PARIT · PERAK” (pin + gelang radar, tag ILUSTRASI); bar tuaian **7,600 KG** (kaunter naik semasa “7,600 kilo”), **−72%** (merah, semasa “72 peratus”), “5,472 KG DIPOTONG” (bahagian itu pecah dan hilang), “2,128 KG DIKIRA” (tag GRAFIK) | Pop pada pin, whoosh semasa split, impact pada “72”, whoosh semasa bar dipotong |
| **S4 Isi 3: Wang** | 42.40–63.72 | 00:37.95–00:59.27 | Split diteruskan hingga 51.2 s, kemudian frame penuh supaya **bil sebenar yang dipegang kelihatan**, punch-in 1.2 pada “72%” | “SEPATUTNYA RM11,400” (perak, dipangkah merah) → **“HANYA DITERIMA RM3,192”** (emas 3D); lajur kiri: “BIL TERDAHULU 65%” → “BIL TERKINI 72% ▲ LEBIH TERUK” | Impact pada RM3,192, pop pada 65% / 72% |
| **S5 Isi 4: Punca** | 63.72–74.52 | 01:13.40–01:24.20 | Potongan + sweep, split dari 67.0 s | Chip “SESI LIBAT URUS · PIHAK BERKENAAN”; ilustrasi sawah perspektif: air dalam terusan berhenti separuh jalan, petak bertukar kering, tanda ✕ → **“PUNCA UTAMA: PENGAIRAN”** (tag ILUSTRASI) | Whoosh potongan, impact pada “pengairan” |
| **S6 Isi 5: Pengezonan** | 74.52–94.20 | 01:28.87–01:48.55 | Frame penuh (bil dipegang ke atas), push-in 1.04→1.10; split dari 82.4 s | Chip “YAB TAMBUN · PERDANA MENTERI”; tajuk “JANJI YANG DISEBUT: PENGEZONAN JELAPANG PADI PARIT”; garis masa Bajet pertama (DISEBUT) → Bajet kelima (KINI); cop **“MASIH BELUM DILAKSANAKAN”** | Whoosh split, impact pada cop |
| **S7 Kemuncak** | 94.20–116.10 | 01:48.55–02:10.45 | Split (kad musim) hingga 102.8 s → frame penuh, push-in 1.12→1.18, punch 1.3/1.4 pada luahan, push-in 1.08→1.22→1.34 pada tuntutan + kilatan | Kad “MUSIM 1 / MUSIM 2: TIDAK DITANAM”, “MUSIM 3 ? JIKA BERULANG…”; luahan pesawah diulang dalam konteks asal; **“TUNTUTAN WAKIL RAKYAT PARIT · PENGEZONAN JELAPANG PADI · DISEGERAKAN”** | Pop kad, impact pada luahan, riser 4 s → impact pada “disegerakan” |
| **S8 Penutup** | 116.10–119.60 | Still akhir rakaman (dimalapkan) | Rakaman pudar ke latar navy | “SUARA PESAWAH PARIT”, nama, jawatan, “Rakaman ucapan sebenar. Grafik ialah ilustrasi.” | Whoosh sinematik |

**Subtitle (F/G):** 57 kumpulan (3–5 perkataan), Inter 800 62 px, putih; kata kunci emas dengan punch-in (padi, 7,600, 72%, RM3,192, pengairan, pengezonan, jelapang, disegerakan, Parit, Bota Kiri…). Diletakkan pada y 1160–1330 px, di atas zon UI TikTok/Reels. Subtitle disembunyikan ketika luahan pesawah dipaparkan sebagai tipografi besar (hook dan 103.3–108.3 s) supaya teks tidak berganda. Teks penuh mengikut masa: `tools/edit-transcript.txt`.

**Pembezaan rakaman vs grafik:** Pepijat “● RAKAMAN DEWAN RAKYAT” sentiasa kelihatan. Panel split bertanda “RAKAMAN ASAL”. Setiap grafik bertanda “GRAFIK” atau “ILUSTRASI”. Wajah, pakaian, mulut dan gerakan wakil rakyat tidak diubah. Hanya zoom/crop digunakan.

## E. Prompt animasi bagi setiap isi (untuk direka semula / diperhalusi)

1. **Tuaian 7,600 kg** — “Bar mendatar emas metalik di atas latar midnight navy, mengisi dari kiri dalam 1.4 s sambil kaunter 0→7,600 KG naik. Pada perkataan ‘72 peratus’, 72% di sebelah kanan bertukar kepada corak jalur merah gelap dengan label 3D −72%. Pada ‘dipotong’, bahagian merah tercabut ke kanan bersama serpihan kecil. Hanya 28% emas yang tinggal, menyala, berlabel 2,128 KG DIKIRA.”
2. **RM11,400 → RM3,192** — “Angka perak RM11,400 masuk dengan blur, kemudian dipangkah garis merah ketika RM3,192 emas 3D jatuh dengan perspektif (rotateX −50° → 0) pada perkataan ‘RM3,192’.”
3. **65% → 72%** — “Dua kad bil bertindan di lajur kiri, tidak menutup bil sebenar di tangan wakil rakyat. Kad kedua berbingkai merah dan masuk dengan sedikit overshoot, berlabel ▲ LEBIH TERUK.”
4. **Pengairan** — “Ilustrasi sawah dalam perspektif 3D, dengan terusan utama di tengah. Air biru mengalir hanya separuh jalan, saluran cabang pudar, petak hijau bertukar coklat kering, dan tanda ✕ merah muncul. Tajuk 3D ‘PUNCA UTAMA: PENGAIRAN’ menghentam pada perkataan ‘pengairan’.”
5. **Bajet 1 → 5** — “Garis masa lima nod. Nod pertama emas berlabel ‘DISEBUT · BAJET PERTAMA’, garis emas berjalan ke nod kelima ‘KINI · BAJET KELIMA’. Cop merah condong ‘MASIH BELUM DILAKSANAKAN’ menghentam pada ‘tidak dilaksanakan’.”
6. **Musim** — “Tiga kad musim dengan putaran Y 3D. Musim 1 dan 2 menunjukkan ikon anak padi dipangkah merah, ‘TIDAK DITANAM’. Musim 3 bergaris putus-putus emas dengan ‘?’ dan ‘JIKA BERULANG…’.”

## H. Pelan teknikal (projek HyperFrames, dalam repo ini)

- `index.html`: komposisi utama (1080×1920, 119.6 s). Empat klip `<video>` daripada satu fail sumber dengan `data-media-start` (potongan di atas), rig kamera `#cam` (zoom/punch-in), `#mask` (clip-path untuk mod Hyperframe), 30 klip SFX.
- `compositions/s1-hook … s8-outro.html`: satu scene grafik bagi setiap babak. `compositions/captions.html` dijana oleh `tools/build_captions.py` daripada transkrip perkataan (`tools/words-b.json`).
- **Aset:** `assets/footage/dewan-padi.mp4` (Klip B: diskalakan semula ke 1080×1920 lanczos + unsharp, H.264 CRF 18, GOP 30, audio dibersihkan). Fail video tidak di-commit (`*.mp4` dalam `.gitignore`). Untuk bina semula:
  ```bash
  curl -L -o assets/src/b.mp4 "https://drive.usercontent.google.com/download?id=1by-KdCJCDgI9GXJkXFzKhlp4UKRG32FY&export=download&confirm=t"
  ffmpeg -i assets/src/b.mp4 -vf "scale=1080:1920:flags=lanczos,unsharp=5:5:0.4" -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -g 30 -keyint_min 30 -sc_threshold 0 -af "highpass=f=80,lowpass=f=12000,afftdn=nf=-28,acompressor=threshold=-20dB:ratio=2.5:attack=10:release=200,loudnorm=I=-16:TP=-1.5:LRA=9" -c:a aac -b:a 192k -ar 48000 -movflags +faststart assets/footage/dewan-padi.mp4
  ffmpeg -ss 130.3 -i assets/footage/dewan-padi.mp4 -frames:v 1 -q:v 2 assets/img/end-still.jpg
  ```
- **Semak & render:**
  ```bash
  npm run check
  npx hyperframes render -q delivery -o renders/suara-pesawah-parit-1080x1920.mp4
  ```
- **SFX:** fail Pixabay yang dibawa bersama skill HyperFrames (lesen Pixabay, boleh digunakan secara komersial).

## Muzik — belum ditambah

Tiada muzik dalam render ini. Katalog muzik HyperFrames memerlukan log masuk HeyGen (percuma), dan sesi ini belum log masuk. Untuk menambah muzik *cinematic orchestral hybrid* berlesen:
1. Jalankan `npx hyperframes auth login`, kemudian minta: “tambah muzik cinematic orchestral, build ke 110 s”.
2. Atau letakkan trek berlesen anda sendiri di `assets/music/bed.mp3` dan tambah `<audio id="music" class="clip" src="assets/music/bed.mp3" data-start="0" data-duration="119.6" data-volume="0.14" data-fade-out="2">`. Kekalkan bunyi sekitar 0.14 di bawah suara (ducking), dan naikkan ke ~0.22 pada 108–116 s untuk kemuncak.

## I. Episod kedua dicadangkan (Klip A: belia)

Isi kuat dari Klip A:
- 00:00.1–00:09.3 “angka 3.0% adalah angka yang menipu realiti”
- 00:09.3–00:24.5 kadar pengangguran 3%, 520,300 penganggur
- 00:25.2–00:35.9 belia 15–24 tahun 10%; 15–30 tahun **6.4%** (Whisper menulis “64%”, tetapi semakan sebutan memberi “enam perpuluhan empat”)
- 01:08.5–01:21.1 “kawasan saya di Parit… aliran keluar bakat-bakat belia”
- 01:21.8–01:51.0 gaji progresif, levi pelbagai peringkat, tabung automasi dan penggajian belia tempatan

**Perlu disemak dengan telinga sebelum digunakan:** perkataan selepas “peluang pekerjaan” pada 01:13.7 (Whisper: “Kuala Putih”, mungkin “berkualiti”) dan “PWS yang … mandatori” pada 01:26.

## Semakan kualiti (Fasa 8): perkara yang perlu anda sahkan

- **Nama pesawah** “Muhammad Nasir bin Kamarudin” dan lokasi “Batu 13, Bota Kiri” adalah daripada transkripsi automatik. Sila sahkan ejaan.
- Subtitle 00:03–00:09 sumber: “Bersama sahabat saya ini ada… bil belian padi”. Bahagian yang tergagap (“resit… beli”) dibuang daripada subtitle sahaja; audio tidak dipotong.
- “Potongan pemutuan” ditulis seperti yang didengar oleh dua model.
- Bunyi diukur dengan alat, bukan didengar oleh manusia. Sila dengar render sebelum diterbitkan.
