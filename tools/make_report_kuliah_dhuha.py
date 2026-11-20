#!/usr/bin/env python3
"""Write LAPORAN_KERATAN_KULIAH_DHUHA.md from the clip specs (lecture = ismi_kuliah_dhuha) and clips/report_meta.json."""
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
    if s.get("lecture") != "ismi_kuliah_dhuha":
        continue
    i = s["id"]; m = meta[i]
    words = json.load(open(os.path.join(ROOT, f"videos/KULIAH_{i}/words.json")))
    speech = min(s["end"] - s["start"], words[-1]["end"] + 0.6)
    total = min(120.0, speech + OUTRO_B)
    rows.append((sum(m["score"]), i, s, m, speech, total))

L = []
A = L.append
A("# Laporan Keratan — Kuliah Dhuha (Sirah & Fiqh)\n")
A("**Penceramah:** YB Ustaz Muhammad Ismi Mat Taib · **Tempat:** Pondok Pengajian Darul Mubarak  ")
A("**Sumber:** rakaman \"Kuliah Dhuha\" (61:18, 432×768 menegak) dari folder Google Drive pengguna.  ")
A("**Gaya:** Style Kuliah Versi 2 \"Mihrab Emas\" (cover gerbang mihrab + lencana episod, bar progres, kad bernombor, kad Arab perkataan demi perkataan, outro CTA).  ")
A("**Kaedah:** transkripsi penuh (Whisper *small*) → transkripsi setiap keratan (Whisper *medium*, masa setiap perkataan) → semakan teks secara manual → HyperFrames.\n")

A("## 1. Analisis keseluruhan kuliah — segmentasi topik\n")
A("| Masa | Topik | Status |\n|---|---|---|")
for t, topic, st in [
    ("00:00–00:50", "Pembukaan, tahmid, selawat", "—"),
    ("00:50–03:50", "Nabi ﷺ memusnahkan lambang syirik selepas Fathu Makkah", "Tidak dipilih — riwayat 'patung dalam rumah' perlu semakan"),
    ("03:50–07:45", "Khalid al-Walid & berhala al-Uzza", "EP 01"),
    ("07:45–11:10", "Amr al-As & berhala Suwa'", "EP 02"),
    ("11:10–13:05", "Sa'ad bin Zaid & berhala Manat", "Tidak dipilih — kisah hampir sama dengan EP 01"),
    ("13:05–21:15", "Ummul Qura; tanah tumpah darah Nabi ﷺ; Abrahah & Tahun Gajah", "Tidak dipilih — bertindih dengan siri Fathu Makkah (EP 09)"),
    ("21:15–23:50", "Hudaibiyah: Islam mendahulukan perdamaian", "EP 03"),
    ("23:50–27:50", "Fathu Makkah dalam Ramadan; tempoh qasar (riwayat 'sallu arba'an')", "Tidak dipilih — riwayat lemah, perlu semakan"),
    ("27:50–29:55", "Puasa & qasar ketika musafir", "EP 04 (bahagian qasar)"),
    ("29:55–33:45", "Sebab-sebab jamak: musafir, hujan lebat, salji, sakit", "Tidak dipilih — sebahagian loghat berat"),
    ("33:45–35:56", "Jamak bukan kebiasaan; kisah jem ke Keramat", "EP 05"),
    ("35:56–38:05", "Makmum musafir & niat mengikut imam", "EP 06"),
    ("38:05–39:40", "Solat jenazah tidak tahu lelaki atau perempuan", "Tidak dipilih — pendek & bercampur"),
    ("39:40–41:45", "Jamak qasar bila tidak tahu bila urusan selesai", "EP 07"),
    ("41:45–43:05", "Orang sakit & nyanyuk: wajib solat?", "EP 08"),
    ("43:05–47:25", "Adab ziarah pesakit: jangan lama, buah tangan, jangan bertanya terperinci", "Tidak dipilih — loghat berat & gurauan, perlu semakan manual"),
    ("47:25–48:33", "Tenangkan pesakit; kisah yang sembuh; positif", "EP 09"),
    ("48:33–50:20", "Musafir 2 marhalah; niat; musafir maksiat", "EP 10"),
    ("50:20–54:55", "Ziarah: malaikat mendoakan; jangan tunggu open house", "EP 11"),
    ("54:55–58:30", "Silaturahim; minta maaf; jaga hubungan dengan manusia & Allah", "EP 12"),
    ("58:30–1:01:17", "Penutup & perbualan selepas kuliah", "—"),
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
A("- **Subtitle** daripada Whisper *medium*, disemak manual. Loghat Kelantan dinormalkan hanya bila maksud jelas (*unta* daripada 'untah', *maksiat* daripada 'masjid' dalam EP 10, *masyaqqah* daripada 'masyarakat' dalam EP 05); perkataan tidak jelas **ditinggalkan, bukan direka**. Sila semak SRT dengan audio.")
A("- **Lafaz Arab yang tercicir** dalam transkrip mesin diisi berdasarkan audio dan transkrip penuh: doa malaikat (EP 11), hadis silaturahim (EP 12), sabda Nabi kepada Khalid (EP 01). Masa subtitle bagi lafaz ini dianggarkan daripada jurang senyap.")
A("- **Nombor hadis** dalam laporan bertanda **[semak]**; pada video hanya nama kitab dipaparkan.")
A("- **EP 01:** kisah jelmaan al-Uzza diriwayatkan oleh an-Nasa'i (as-Sunan al-Kubra) — sila sahkan status riwayat.")
A("- **EP 05:** penceramah menyebut orang Syiah menjamak setiap hari — dikekalkan seperti kata penceramah.")
A("- **EP 10:** satu ayat ('bukan musafir yang disunatkan atau diwajibkan') tidak disubtitle kerana mungkin tersalah dengar dan boleh mengelirukan.")
A("- **EP 09:** dipendekkan kepada bahagian yang jelas (47:25–48:33); bahagian sebelumnya (43:05–47:25) berloghat berat dan bergurau — perlu semakan manual jika mahu dijadikan video.")
A("- **Pemotongan:** rakaman dipotong ke kawasan penceramah (`src_crop [145, 0, 810, 1440]`) kerana penceramah kecil dalam bingkai asal.")
A("- Tiada visual nabi, malaikat atau perkara ghaib dijana (termasuk kisah jelmaan jin) — hanya rakaman asal, tipografi dan corak geometri.\n")

A("## 5. Audio & eksport\n")
A("- Suara: high-pass 80 Hz, afftdn, kompresor, −16 LUFS. Muzik: pad ambien original (`assets/music/pad.m4a`), ~24 dB di bawah suara.")
A("- Eksport: MP4 H.264, 1080×1920, 30 fps, AAC stereo, ≤ 120 s. Rakaman sumber 432×768 dibesarkan — ketajaman terhad oleh sumber.\n")
A("## 6. Bina & render semula\n")
A("```bash\npython3 tools/build_clip.py clips/KULIAH_26.json --source /path/to/kuliah_dhuha.mp4\n```\n")
A("```bash\nFORCE=1 tools/render_all.sh 26\n```\n")
open(os.path.join(ROOT, "LAPORAN_KERATAN_KULIAH_DHUHA.md"), "w").write("\n".join(L))
print("written", len(L), "lines")
