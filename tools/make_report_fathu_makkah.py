#!/usr/bin/env python3
"""Write LAPORAN_KERATAN_FATHU_MAKKAH.md from the clip specs (lecture = ismi_fathu_makkah) and clips/report_meta.json."""
import json, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
meta = json.load(open(os.path.join(ROOT, "clips/report_meta.json")))
OUTRO_B = 4.4


def ts(t):
    t = int(round(t)); return f"{t // 3600:02d}:{t % 3600 // 60:02d}:{t % 60:02d}"


def mmss(t):
    t = int(round(t)); return f"{t // 60:02d}:{t % 60:02d}"


rows = []
for p in sorted(glob.glob(os.path.join(ROOT, "clips/KULIAH_*.json"))):
    s = json.load(open(p))
    if s.get("lecture") != "ismi_fathu_makkah":
        continue
    i = s["id"]; m = meta[i]
    words = json.load(open(os.path.join(ROOT, f"videos/KULIAH_{i}/words.json")))
    speech = min(s["end"] - s["start"], words[-1]["end"] + 0.6)
    total = min(120.0, speech + OUTRO_B)
    rows.append((sum(m["score"]), i, s, m, speech, total))

L = []
A = L.append
A("# Laporan Keratan Kuliah — Sirah Fathu Makkah\n")
A("**Penceramah:** YB Ustaz Muhammad Ismi Mat Taib · **Tempat:** Pondok Pengajian Darul Mubarak  ")
A("**Sumber:** rakaman kuliah penuh (64:18, 432×768 menegak) dari folder Google Drive pengguna.  ")
A("**Gaya:** Konsep B \"Mihrab Emas\" (cover gerbang mihrab + lencana episod, bar progres, kad bernombor, kad Arab perkataan demi perkataan, outro CTA).  ")
A("**Kaedah:** transkripsi penuh (Whisper *small*) → transkripsi setiap keratan (Whisper *medium*, masa setiap perkataan) → semakan teks secara manual → HyperFrames.\n")

A("## 1. Analisis keseluruhan kuliah — segmentasi topik\n")
A("| Masa | Topik | Status |\n|---|---|---|")
for t, topic, st in [
    ("00:00–01:00", "Pembukaan, tahmid, selawat", "—"),
    ("01:00–04:30", "Fathu Makkah; Safwan bin Umayyah lari, diberi serban & tempoh 4 bulan", "EP 01"),
    ("04:30–06:30", "Penjara dalam Islam & ulasan isu semasa (kes mahkamah)", "Tidak dipilih — ulasan politik semasa"),
    ("06:30–08:40", "Yassiru wala tu'assiru; masuk Islam dengan syahadah", "EP 02"),
    ("08:40–09:15", "Perumpamaan pendenak & sebarau", "Sebahagian — loghat berat"),
    ("09:15–11:00", "Al-muslimu man salimal muslimun min lisanihi wa yadih", "EP 03"),
    ("11:00–12:00", "Safwan masuk Islam; nikah zaman jahiliah tidak perlu diulang", "Tidak dipilih — terlalu pendek (<60 s)"),
    ("12:00–13:10", "Fadalah bin Umair berniat membunuh Nabi ﷺ ketika tawaf", "EP 04"),
    ("13:20–15:00", "Khutbah: Makkah tanah haram", "EP 05"),
    ("15:00–18:40", "Wat-tini waz-zaitun; pertumpahan darah minimum ketika Fathu Makkah", "Tidak dipilih — bertindih dengan EP 05"),
    ("19:00–20:20", "Gandaan pahala di Makkah, Madinah & al-Aqsa", "EP 06"),
    ("20:20–27:30", "Umm al-Qura; rezeki Makkah; selamat daripada gempa; telaga Zamzam", "Tidak dipilih — lebih 2 minit, kisah peribadi"),
    ("27:30–29:05", "Bada'al Islamu ghariban", "EP 07"),
    ("29:05–30:40", "Contoh menteri & puasa (intermittent fasting)", "Tidak dipilih — rujukan individu"),
    ("30:40–31:50", "Allah memelihara kita 24 jam", "EP 08"),
    ("32:00–36:50", "Tahun Gajah: Abrahah, Abdul Muttalib & burung ababil", "EP 09 (bahagian unta & Kaabah)"),
    ("36:50–41:10", "Kebimbangan Ansar; al-mahya mahyakum", "EP 10"),
    ("41:10–42:50", "Cinta tanah air vs agama; 5 dharuriyyat", "EP 11"),
    ("43:00–46:00", "Bai'ah di Bukit Safa; Hindun & kisah Hamzah", "Tidak dipilih — butiran mutilasi sensitif"),
    ("46:00–47:30", "Wahsyi masuk Islam; pembunuh & yang dibunuh masuk syurga", "EP 12"),
    ("49:30–51:30", "Hindun & nafkah suami yang kedekut", "EP 13"),
    ("52:50–57:50", "Bai'ah: zina, membunuh anak; kisah Umar menanam anak", "Tidak dipilih — kisah Umar menanam anak tidak sabit sanadnya; perlu semakan"),
    ("58:00–1:01:20", "Bai'ah: dusta & maksiat; Hindun memecahkan berhala; ayat hati yang keras", "Tidak dipilih — bacaan teks panjang"),
    ("1:01:20–1:03:10", "Dakwah berhikmah; ulasan isu Selat Hormuz", "Tidak dipilih — bertindih dengan EP 02 / isu semasa"),
    ("1:03:10–1:04:18", "Doa penutup", "—"),
]:
    A(f"| {t} | {topic} | {st} |")
A("")

A("## 2. Laporan pemilihan keratan\n")
A("Skor = Kepentingan ilmu (25) + Kejelasan (25) + Kesempurnaan dalam 1–2 minit (20) + Relevan (15) + Penyampaian (10) + Keunikan (5).\n")
A("| EP | Fail | Tajuk Keratan | Timestamp Asal | Durasi | Isi Utama | Skor |\n|---|---|---|---|---|---|---|")
for sc, i, s, m, speech, total in sorted(rows, key=lambda r: r[2]["episode"]):
    A(f"| {s['episode']:02d} | KULIAH_{i} | {m['titles'][0]} | {ts(s['start'])}–{ts(s['start'] + speech)} | {mmss(total)} | {m['topic']} | {sc}/100 |")
A("")

A("## 3. Butiran setiap video\n")
for sc, i, s, m, speech, total in sorted(rows, key=lambda r: r[2]["episode"]):
    A(f"### EP {s['episode']:02d} · KULIAH_{i}: {m['titles'][0]}\n")
    A(f"- **Fail:** `exports/KULIAH_{i}_{s['slug']}.mp4` · subtitle `exports/KULIAH_{i}.srt` · cover `exports/covers/KULIAH_{i}_{s['slug']}_COVER.jpg` · projek `videos/KULIAH_{i}/`")
    A(f"- **Timestamp asal:** {ts(s['start'])} – {ts(s['start'] + speech)} · **Durasi akhir:** {mmss(total)} (ucapan {speech:.1f} s + outro CTA)")
    A(f"- **Kategori:** {s['category']} · **Skor:** {sc}/100 ({' / '.join(str(x) for x in m['score'])})")
    A("- **Cadangan tajuk:**")
    for k, t in enumerate(m["titles"]):
        A(f"  {k + 1}. {t}{'  ← **terbaik (thumbnail)**' if k == 0 else ''}")
    A("- **Kad animasi:**")
    for p in s.get("points", []):
        A(f"  - *{p['label']}* — {p['text']} ({mmss(p['at'])})")
    for a in s.get("arabic", []):
        A(f"  - *{a['ref']}* — {a['ar']} — “{a['ms']}” ({mmss(a['at'])})")
    A(f"- **Pengajaran utama:** {m['lesson']}")
    A(f"- **Rujukan:** {m['refs']}")
    A(f"- **Kapsyen media sosial:**\n\n```\n{m['caption']}\n```\n")

A("## 4. Kawalan ketepatan & perkara untuk semakan manusia\n")
A("- **Subtitle** daripada Whisper *medium*, disemak secara manual. Loghat Kelantan (*unta* daripada 'untung', *takut* daripada 'kukut', *kedekut*, *laki*) dinormalkan hanya apabila maksudnya jelas; perkataan yang tidak dapat dikenal pasti **ditinggalkan, bukan direka** (terutama dalam EP 10 dan EP 13). Sila semak SRT dengan audio sebelum diterbitkan.")
A("- **Teks Arab** pada kad ialah lafaz hadis/athar yang dikenal pasti daripada kutipan penceramah. Nombor hadis dalam laporan ini bertanda **[semak]**; pada video hanya nama kitab dipaparkan.")
A("- **EP 06:** riwayat gandaan 500 kali di Masjid al-Aqsa diperselisihkan statusnya oleh ulama hadis — disebut seperti kata penceramah, perlu disemak sebelum diterbitkan.")
A("- **EP 12:** hadis 'Allah ketawa kepada dua lelaki' bersifat umum; penceramah mengaitkannya dengan Wahsyi dan Hamzah. Penerangan dikekalkan seperti kata penceramah.")
A("- **EP 09 & EP 01:** kata-kata Abdul Muttalib dan dialog Safwan adalah riwayat sirah (Ibnu Hisyam), bukan hadis — rujukan pada kad ditulis demikian.")
A("- **Tidak dirender:** ulasan isu politik/semasa (04:30–06:30, 1:02:30), kisah Umar menanam anak (tidak sabit — perlu semakan), dan butiran mutilasi jenazah Hamzah.")
A("- **Pemotongan:** kod QR DuitNow, nombor telefon dan banner Pondok Pengajian Darul Mubarak di bahagian bawah rakaman asal dibuang (pemotongan 9:16 bahagian atas, `src_crop`).")
A("- Tiada visual nabi, malaikat atau perkara ghaib dijana. Hanya rakaman asal, tipografi dan corak geometri.\n")

A("## 5. Audio & eksport\n")
A("- Suara: high-pass 80 Hz, afftdn, kompresor, −16 LUFS. Muzik: pad ambien original (`assets/music/pad.m4a`), ~24 dB di bawah suara.")
A("- Eksport: MP4 H.264, 1080×1920, 30 fps, AAC stereo, ≤ 120 s. Rakaman sumber 432×768 dibesarkan — ketajaman terhad oleh sumber.\n")
A("## 6. Bina & render semula\n")
A("```bash\npython3 tools/build_clip.py clips/KULIAH_14.json --source /path/to/kuliah_fathu_makkah.mp4\n```\n")
A("```bash\nFORCE=1 tools/render_all.sh 14\n```\n")
open(os.path.join(ROOT, "LAPORAN_KERATAN_FATHU_MAKKAH.md"), "w").write("\n".join(L))
print("written", len(L), "lines")
