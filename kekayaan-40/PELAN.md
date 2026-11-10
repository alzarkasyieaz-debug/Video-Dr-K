# "Selepas Umur 40 Tahun, Kekayaan Sebenar Adalah…"

Video 9:16 (1080×1920, 30 fps, H.264), **57.5 saat**. Gaya sama seperti video *Hati-hati Memilih
Bahagia*: biru malam, emas lembut, amber dan krim; Montserrat untuk teks bacaan dan Playfair
Display italik untuk perkataan bermakna; gerakan perlahan, dissolve ke biru malam dan animasi
simbolik bagi setiap poin.

Semua teks diambil **verbatim** daripada infografik yang dibekalkan. Gambar keluarga daripada
infografik yang sama (dipotong tanpa panel teks: `assets/img/keluarga.jpg`).

Output: `renders/kekayaan-sebenar-selepas-40_1080x1920.mp4`

## Timeline

| Masa | Babak | Teks | Animasi simbolik |
| --- | --- | --- | --- |
| 0:00–0:05.5 | Hook | SELEPAS UMUR **40** TAHUN, *kekayaan sebenar adalah…* | Angka 40 besar (emas) dalam cincin jam yang berputar perlahan; frame pertama sudah jadi thumbnail |
| 0:05.5–0:10.5 | 01 | ***Kesihatan*** yang masih baik | Garisan degupan jantung (ECG) dilukis, cahaya berdenyut pada setiap degupan |
| 0:10.5–0:15.5 | 02 | Hati yang ***tenang*** | Setitis air jatuh, riak air berkembang dan semakin reda |
| 0:15.5–0:20.5 | 03 | Rezeki yang ***cukup dan berkat*** | Bekas cahaya terisi **tepat** hingga garisan "CUKUP" (tidak melimpah), percikan berkat |
| 0:20.5–0:25.5 | 04 | Keluarga yang ***bahagia*** | Gambar keluarga dalam bingkai emas, push-in dan sapuan cahaya |
| 0:25.5–0:30.5 | 05 | Anak-anak yang ***sihat*** | Dua anak pokok tumbuh dan daun terbuka di bawah cahaya matahari |
| 0:30.5–0:35.5 | 06 | Sahabat yang ***ikhlas*** | Dua cahaya berjalan seiring di jalan yang sama hingga ke ufuk |
| 0:35.5–0:40.5 | 07 | Hidup ***tanpa beban hutang*** | Batu "HUTANG" tergantung pada cahaya; tali terlepas, batu jatuh, cahaya naik bebas |
| 0:40.5–0:45.5 | 08 | Masa untuk mendekatkan diri ***kepada Allah*** | Langit malam, bulan sabit, bintang berkelip, cahaya naik di sebalik siluet masjid |
| 0:45.5–0:51.0 | Penutup | Bila usia semakin meningkat, *hidup yang sederhana tetapi tenang* terasa jauh lebih berharga. | Gambar keluarga sebagai latar lembut (dimalapkan) |
| 0:51.0–0:57.5 | Rumusan | Senarai 01–08 + @NakSeeHeart | Senarai muncul satu demi satu dan ditahan, sesuai untuk di-screenshot atau disimpan |

## Audio

Video ini **tanpa bunyi** (tiada suara penyampai dan tiada sumber muzik berlesen dalam
persekitaran ini). Semasa memuat naik, pilih muzik daripada pustaka platform (cari "soft
emotional piano" / "calm reflective piano"). Tempo perlahan sesuai dengan babak 5 saat.

## Kapsyen media sosial

> Selepas umur 40 tahun, kekayaan sebenar adalah… 🤍
>
> 01 Kesihatan yang masih baik
> 02 Hati yang tenang
> 03 Rezeki yang cukup dan berkat
> 04 Keluarga yang bahagia
> 05 Anak-anak yang sihat
> 06 Sahabat yang ikhlas
> 07 Hidup tanpa beban hutang
> 08 Masa untuk mendekatkan diri kepada Allah
>
> Bila usia semakin meningkat, hidup yang sederhana tetapi tenang terasa jauh lebih berharga.
>
> 🎙️ @NakSeeHeart
> #nasihat #muhasabah #keluarga #bahagia #fyp

**Tajuk alternatif:** "Kekayaan Sebenar Selepas 40" · "Apa Yang Lebih Berharga Dari Wang?"

## Sunting dan render semula

Semua babak dijana daripada `tools/build.py` (teks dalam senarai `POINTS`):

```bash
cd kekayaan-40 && python3 tools/build.py && npx hyperframes check .
```

```bash
npx hyperframes render . -q delivery -f 30 -o renders/kekayaan-sebenar-selepas-40_1080x1920.mp4
```
