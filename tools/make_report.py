#!/usr/bin/env python3
"""Write a lecture report from its clip specs and a meta file.

usage: make_report.py [clips/report_meta.json]   (meta "_lecture" holds header, topics, glob, out)
"""
import json, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
META = sys.argv[1] if len(sys.argv) > 1 else "clips/report_meta.json"
meta = json.load(open(os.path.join(ROOT, META)))
LEC = meta["_lecture"]


def ts(t):
    t = int(round(t)); return f"{t // 3600:02d}:{t % 3600 // 60:02d}:{t % 60:02d}"


def mmss(t):
    t = int(round(t)); return f"{t // 60:02d}:{t % 60:02d}"


specs = {}
for p in sorted(glob.glob(os.path.join(ROOT, LEC["glob"]))):
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
for h in LEC["header"]:
    A(h)

A("## 1. Analisis keseluruhan kuliah — segmentasi topik\n")
A("| Masa | Topik | Kategori |\n|---|---|---|")
for t, topic, cat in LEC["topics"]:
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
    tl = [(0.0, "Cover — poster tajuk (bingkai pertama = thumbnail), subtitle bermula")]
    tl.append((2.6, "Cover terangkat → close-up; tajuk mampat di atas; lower-third (5.6–11 s)"))
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
for t, isi, why in LEC["not_rendered"]:
    A(f"| {t} | {isi} | {why} |")
A("")

A("## 5. Kawalan ketepatan & perkara untuk semakan manusia\n")
for n in LEC["notes"]:
    A(n)
A("## 6. Audio & eksport\n")
A("- Suara: high-pass 80 Hz, pengurangan hingar (afftdn), kompresor ringan, loudness −16 LUFS.")
A("- Muzik: pad ambien instrumental **original** dijana sendiri (`tools/make_music_bed.py`, tiada vokal/lirik/hak cipta pihak ketiga), dimainkan sekitar −24 dB di bawah suara dengan fade in/out. Tiada kesan bunyi atau suara tambahan.")
A("- Eksport: MP4 H.264, 1080×1920 (9:16), 30 fps, AAC stereo 48 kHz, 60–120 s.")
A("- Rakaman sumber hanya 432×768, jadi gambar dibesarkan (lanczos) ke 1080×1920 — ketajaman terhad oleh sumber.\n")

A("## 7. Cara sunting & render semula\n")
A("```bash\n# 1. letak rakaman asal (tidak disimpan dalam git) dan bina projek klip\npython3 tools/build_clip.py clips/KULIAH_01.json --source /path/to/lecture.mp4\n```\n")
A("```bash\n# 2. pratonton / semak\ncd videos/KULIAH_01 && npx hyperframes preview\n```\n")
A("```bash\n# 3. render ke exports/\ntools/render_all.sh 01\n```\n")
open(os.path.join(ROOT, LEC["out"]), "w").write("\n".join(L))
print("written", len(L), "lines")
