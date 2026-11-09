#!/usr/bin/env python3
"""Write LAPORAN_KERATAN.md from the clip specs and clips/report_meta.json."""
import json, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
meta = json.load(open(os.path.join(ROOT, "clips/report_meta.json")))


def ts(t):
    t = int(round(t)); return f"{t // 3600:02d}:{t % 3600 // 60:02d}:{t % 60:02d}"


def mmss(t):
    t = int(round(t)); return f"{t // 60:02d}:{t % 60:02d}"


specs = {}
for p in sorted(glob.glob(os.path.join(ROOT, "clips/KULIAH_*.json"))):
    s = json.load(open(p)); specs[s["id"]] = s

rows = []
for i, s in specs.items():
    m = meta[i]; sc = sum(m["score"])
    words = json.load(open(os.path.join(ROOT, f"videos/KULIAH_{i}/words.json")))
    speech = min(s["end"] - s["start"], words[-1]["end"] + 0.6)
    total = min(120.0, max(min(speech + 2.0, 120.0), speech + 1.0))
    rows.append((sc, i, s, m, speech, total))
rows.sort(key=lambda r: (-r[0], r[1]))

L = []
A = L.append
A("# Laporan Keratan Kuliah — Bab Makruh Menguap dalam Solat\n")
A("**Sumber:** rakaman kuliah penuh (65:00, 432×768 menegak) dari folder Google Drive pengguna.  ")
A("**Kitab:** syarah Mukhtasar Sahih at-Tirmizi karangan Syeikh Muhammad Idris al-Marbawi (Bahrul Mazi) — siri ke-30, juzuk 3, muka surat 73.  ")
A("**Kaedah:** transkripsi penuh (Whisper *small*, Bahasa Melayu) untuk analisis keseluruhan kuliah → transkripsi semula setiap keratan (Whisper *medium*, masa setiap perkataan) → semakan teks secara manual → HyperFrames.\n")

A("## 1. Analisis keseluruhan kuliah — segmentasi topik\n")
A("| Masa | Topik | Kategori |\n|---|---|---|")
for t, topic, cat in [
    ("00:00–01:30", "Pembukaan, tahmid, selawat; pengenalan kitab & siri", "—"),
    ("01:30–04:42", "Bab makruh menguap: maksud *karahiyah*, larangan haram vs makruh, hadis at-Tirmizi", "Fiqh solat / usul"),
    ("04:42–06:02", "Apa itu menguap; tanda permulaan mengantuk", "Fiqh solat"),
    ("06:02–07:47", "'Fal-yakzim mastata'a' — tahan sedaya mampu; kaitan dengan *al-kazimin al-ghaiz*", "Hadis / tadabbur"),
    ("07:47–09:57", "Tutup mulut dengan tangan; syaitan masuk; syaitan mengalir dalam aliran darah", "Hadis / adab"),
    ("09:57–11:43", "Penghalang syaitan: zikrullah & basmalah (makan, mandi, bilik air); Surah al-A'raf: 27", "Zikir & adab"),
    ("11:43–12:24", "Riwayat-riwayat lain dalam bab; status hadis (hasan sahih)", "Hadis"),
    ("12:24–14:01", "Nabi ﷺ tidak menguap (mursal); mata tidur hati jaga", "Syamail"),
    ("14:01–16:38", "Aisyah & qarin; setiap orang ada syaitan; Allah bantu Nabi ﷺ", "Hadis / akidah"),
    ("16:38–20:33", "Nabi ﷺ & syaitan yang mengganggu solat; doa Nabi Sulaiman; jin menyerupai haiwan", "Sirah / akidah"),
    ("20:33–22:30", "Hadis al-Bukhari (syaitan ketawa) & Ibnu Majah (jangan melolong)", "Hadis / adab"),
    ("22:30–28:42", "Pendapat Ibrahim an-Nakha'i; hukum berdehem dalam solat (mazhab Syafi'i); khilaf ulama", "Fiqh solat"),
    ("28:42–31:00", "Beza Ibnu Arabi & Ibnul Arabi; kitab 'Aridhatul Ahwazi & Tuhfatul Ahwazi", "Biografi ulama"),
    ("31:00–33:59", "Perbuatan keji disandarkan kepada syaitan, yang baik kepada malaikat; kenyang & malas", "Akhlak"),
    ("33:59–37:32", "Doa berlindung daripada hamm, hazan, 'ajz, kasal, jubn, bukhl", "Doa / muhasabah"),
    ("37:32–38:20", "Kurangkan makan, puasa, cergas", "Akhlak"),
    ("38:20–45:42", "Solat duduk & baring: hadis 'Imran bin Husain; pembetulan teks syarah kitab", "Fiqh solat"),
    ("45:42–49:20", "Berkongsi pahala kerana uzur; sakit & musafir tetap ditulis pahala", "Hadis / niat"),
    ("49:20–55:05", "Buat yang terbaik; contoh haji & haid (audio kurang jelas)", "Fiqh / motivasi"),
    ("55:05–59:28", "Riwayat 'Imran; huraian Imam an-Nawawi: solat duduk sunat vs fardu", "Fiqh solat"),
    ("59:28–1:01:58", "Terawih sambil duduk; solat sunat atas kenderaan; *fattaqullah mastata'tum*", "Fiqh solat"),
    ("1:02:11–1:04:24", "Soal jawab: makmum masbuk", "Fiqh solat"),
]:
    A(f"| {t} | {topic} | {cat} |")
A("")

A("## 2. Laporan pemilihan keratan (disusun mengikut skor)\n")
A("Skor = Kepentingan ilmu (25) + Kejelasan (25) + Kesempurnaan dalam 1–2 minit (20) + Relevan (15) + Penyampaian (10) + Keunikan (5).\n")
A("| No. | Tajuk Keratan | Timestamp Asal | Durasi | Isi Utama | Skor |\n|---|---|---|---|---|---|")
for sc, i, s, m, speech, total in rows:
    A(f"| {i} | {m['titles'][0]} | {ts(s['start'])}–{ts(s['start'] + speech)} | {mmss(total)} | {m['topic']} | {sc}/100 |")
A("")

A("## 3. Butiran setiap video\n")
for sc, i, s, m, speech, total in rows:
    f = f"KULIAH_{i}_{s['slug']}.mp4"
    A(f"### VIDEO {i}: {m['titles'][0]}\n")
    A(f"- **Fail:** `exports/{f}` · subtitle `exports/KULIAH_{i}.srt` · komposisi boleh sunting `videos/KULIAH_{i}/`")
    A(f"- **Timestamp asal:** {ts(s['start'])} – {ts(s['start'] + speech)} · **Durasi akhir:** {mmss(total)} (ucapan {speech:.1f} s + outro)")
    A(f"- **Kategori:** {s['category']} · **Skor:** {sc}/100 ({' / '.join(str(x) for x in m['score'])})")
    A("- **Cadangan tajuk:**")
    for k, t in enumerate(m["titles"]):
        A(f"  {k + 1}. {t}{'  ← **terbaik (thumbnail)**' if k == 0 else ''}")
    A("- **Point sokongan (kad animasi):**")
    for p in s.get("points", []):
        A(f"  - *{p['label']}* — {p['text']} ({mmss(p['at'])})")
    for a in s.get("arabic", []):
        A(f"  - *{a['ref']}* — {a['ar']} — “{a['ms']}” ({mmss(a['at'])})")
    A(f"- **Pengajaran utama:** {m['lesson']}")
    A(f"- **Rujukan:** {m['refs']}")
    A("- **Timeline suntingan:**")
    tl = [(0.0, "Hook — tajuk besar + close-up penceramah, subtitle bermula")]
    tl.append((5.0, "Tajuk mampat di atas; lower-third kitab (5.6–11 s)"))
    for p in s.get("points", []):
        tl.append((p["at"], f"Kad '{p['label']}' (shot sederhana)"))
    for a in s.get("arabic", []):
        tl.append((a["at"], f"Kad teks Arab — {a['ref']} (shot lebar, wajah di bawah kad)"))
    tl.append((speech - 0.2, "Outro — logo bintang emas, siri & tajuk; muzik fade-out"))
    for t, d in sorted(tl):
        A(f"  - `{mmss(t)}` {d}")
    A(f"- **Kapsyen media sosial:**\n\n```\n{m['caption']}\n```\n")

A("## 4. Isi yang dikenal pasti tetapi tidak dirender\n")
A("| Masa | Isi | Sebab |\n|---|---|---|")
for t, isi, why in [
    ("1:00:35–1:01:54", "Solat sunat atas kenderaan ketika musafir; *bertakwalah sekadar mampu* (79 s, skor anggaran 80)", "Bahagian tengah dalam loghat Kelantan tidak dapat ditranskripsi dengan yakin — perlu semakan manusia sebelum subtitle dibuat"),
    ("14:01–16:07", "Aisyah r.a. & qarin: setiap orang ada syaitan, Allah bantu Nabi ﷺ (≈126 s)", "Melebihi 2 minit; sesuai video panjang"),
    ("16:38–19:24", "Nabi ﷺ menangkap syaitan & teringat doa Nabi Sulaiman (≈165 s)", "Melebihi 2 minit; sesuai video panjang"),
    ("36:09–37:32", "Doa bahagian kedua: lemah, malas, pengecut, bakhil (83 s, skor anggaran 82)", "Bertindih dengan VIDEO 10 — boleh dijadikan sambungan"),
    ("28:43–30:00", "Beza Ibnu Arabi (tasawuf) & Ibnul Arabi (fiqh Maliki)", "Skor 78 — terlalu khusus untuk penonton umum"),
    ("40:15–45:42", "Hadis 'Imran: pahala berdiri/duduk/baring + pembetulan teks syarah", "Lebih 5 minit dan sebahagiannya sudah dalam VIDEO 01"),
    ("51:04–55:05", "Contoh haji & haid", "Audio kurang jelas dan mengandungi penerangan perubatan yang perlu disahkan — dikecualikan"),
]:
    A(f"| {t} | {isi} | {why} |")
A("")

A("## 5. Kawalan ketepatan & perkara untuk semakan manusia\n")
A("- **Subtitle** dibina daripada transkrip Whisper *medium* dan disemak secara manual berdasarkan konteks. Loghat (contoh *tahang* → tahan, *rokok* → rukuk, *mari* dikekalkan) dinormalkan hanya apabila maksudnya jelas. Perkataan yang tidak dapat dikenal pasti **ditinggalkan, bukan direka**. Sila semak semua SRT dengan audio sebelum diterbitkan.")
A("- **Teks Arab** pada kad ialah lafaz hadis/ayat yang dikenal pasti daripada kutipan penceramah; lafaz penceramah kadang-kadang ringkas atau berbeza sedikit. Nombor hadis dalam laporan ini bertanda **[semak]** — sahkan dengan sumber asal (Sunnah.com / kitab) sebelum diterbitkan. Pada video hanya nama kitab hadis dipaparkan.")
A("- **VIDEO 12:** penceramah sendiri menyebut riwayat 'Nabi tidak menguap' sebagai **hadis mursal** — label itu dikekalkan pada kad.")
A("- **VIDEO 06:** nama sahabat buta didengar sebagai *Abdullah Ibnu Ummi Maktum* (transkrip mesin keliru dengan 'Ibn Umar') — sila sahkan dengan audio.")
A("- **VIDEO 01:** frasa 'maka Allah bagi pahala sama' sekitar 00:55 kurang jelas dalam audio.")
A("- **Nama penceramah** tidak disebut dalam rakaman, jadi lower-third memaparkan nama kitab. Beri nama penceramah dan ia boleh ditukar dalam `clips/KULIAH_XX.json` (`speaker`, `speaker_role`), kemudian bina & render semula.")
A("- Tiada visual nabi, malaikat atau peristiwa ghaib dijana. Hanya rakaman asal, tipografi dan corak geometri.\n")

A("## 6. Audio & eksport\n")
A("- Suara: high-pass 80 Hz, pengurangan hingar (afftdn), kompresor ringan, loudness −16 LUFS.")
A("- Muzik: pad ambien instrumental **original** dijana sendiri (`tools/make_music_bed.py`, tiada vokal/lirik/hak cipta pihak ketiga), dimainkan sekitar −24 dB di bawah suara dengan fade in/out. Tiada kesan bunyi atau suara tambahan.")
A("- Eksport: MP4 H.264, 1080×1920 (9:16), 30 fps, AAC stereo 48 kHz, 60–120 s.")
A("- Rakaman sumber hanya 432×768, jadi gambar dibesarkan (lanczos) ke 1080×1920 — ketajaman terhad oleh sumber.\n")

A("## 7. Cara sunting & render semula\n")
A("```bash\n# 1. letak rakaman asal (tidak disimpan dalam git) dan bina projek klip\npython3 tools/build_clip.py clips/KULIAH_01.json --source /path/to/lecture.mp4\n```\n")
A("```bash\n# 2. pratonton / semak\ncd videos/KULIAH_01 && npx hyperframes preview\n```\n")
A("```bash\n# 3. render ke exports/\ntools/render_all.sh 01\n```\n")
open(os.path.join(ROOT, "LAPORAN_KERATAN.md"), "w").write("\n".join(L))
print("written", len(L), "lines")
