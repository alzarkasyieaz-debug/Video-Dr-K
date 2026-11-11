#!/usr/bin/env python3
"""Write deliverables/LAPORAN_PRODUKSI.md from specs/, deliverables/<ID>/build.json and tools/sources.json."""
import json, os, re, glob, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOOD = {"serious": "Sinematik serius — rentetan string minor (Am–F–C–G), bass atmosfera, perkusi denyut lembut yang meningkat",
        "inspire": "Inspirasi dokumentari — string major (C–G–Am–F), arpeggio piano, perkusi heroik yang membina",
        "emotional": "Emosi kemanusiaan — piano lembut atas pad string (Dm–Bb–F–C), perkusi minimum"}

def tc(t):
    m, s = divmod(t, 60); return f"{int(m):02d}:{s:05.2f}"

def slug(t):
    t = unicodedata.normalize("NFKD", t.replace("–", " ").replace("&", " DAN ")).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Z0-9]+", "_", t.upper()).strip("_")

def plain(s): return re.sub(r"[\[\]{}]", "", s).replace("|", " ")

def fact_line(f):
    t = f["type"]
    if t == "number": what = f'Angka kiraan naik {f.get("prefix","")}0 → {f["value"]}{f.get("suffix","")} — {f.get("sub","")}'
    elif t == "percent": what = f'Cincin peratus 0% → {f["value"]}% — {f.get("sub","")}'
    elif t == "bars": what = "Carta bar: " + ", ".join(f'{i["label"]} {i["show"]}' for i in f["items"])
    elif t == "timeline": what = "Garis masa: " + " → ".join(f'{i["y"]} ({i["d"]})' for i in f["items"])
    elif t == "bullets": what = "Senarai berturutan: " + " / ".join(i["text"] if isinstance(i, dict) else i for i in f["items"])
    elif t == "pair": what = "Lencana bergabung: " + " + ".join(f["items"])
    elif t == "quote": what = f'Kad petikan: {plain(f["text"])} — {f.get("who","")}'
    else: what = f'Tipografi kinetik: {plain(f["text"])}' + (f' — {f["sub"]}' if f.get("sub") else "")
    src = f' _({f["src"]})_' if f.get("src") else ""
    return f'| {tc(f["start"])} | {f.get("label","")} | {what}{src} |'

def main():
    sources = json.load(open(os.path.join(ROOT, "tools/sources.json")))
    out = ["# LAPORAN PRODUKSI — SIRI KLIP UCAPAN DR. K", "",
           "Dijana daripada `specs/*.json` oleh `tools/report.py`. Semua masa dalam format mm:ss.",
           "Transkripsi: Whisper large-v3-turbo (Bahasa Melayu) dengan semakan angka utama menggunakan Whisper large-v3.", ""]
    out += ["## A. ANALISIS KANDUNGAN", ""]
    specs = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "specs/VIDEO_*.json"))):
        s = json.load(open(p)); specs[s["id"]] = s
    for src in sources:
        ids = [i for i, s in specs.items() if s["source"] == src["key"]]
        out += [f'### {src["file"]}', "",
                f'- **Durasi asal:** {src["duration"]}',
                f'- **Latar:** {src["setting"]}',
                f'- **Bilangan klip dihasilkan:** {len(ids)} ({", ".join(ids) if ids else "—"})', "",
                "**Isu penting dikenal pasti:**", ""]
        out += [f"{k+1}. {x}" for k, x in enumerate(src["issues"])]
        if src.get("excluded"):
            out += ["", "**Segmen tidak dijadikan klip (dan sebabnya):**", ""]
            out += [f"- {x}" for x in src["excluded"]]
        out.append("")
    out += ["## B. SENARAI PRODUKSI KLIP", ""]
    for cid, s in specs.items():
        bj = os.path.join(ROOT, "deliverables", cid, "build.json")
        if not os.path.exists(bj): continue
        b = json.load(open(bj))
        name = f'{cid}_{slug(s["topic"])}.mp4'
        src = next(x for x in sources if x["key"] == s["source"])
        body = [e for e in b["edl"] if e["kind"] == "body"]
        hook = next((e for e in b["edl"] if e["kind"] == "hook"), None)
        words = b["words"]
        hook_txt = " ".join(w["t"] for w in words if w["s"] < b["hook_end"] - 0.05)
        out += [f"### {cid} — {plain(s['hook_title']).title()}", "",
                f"1. **Nombor klip:** {cid} → `output/{name}`",
                f"2. **Tajuk klip:** {plain(s['hook_title']).title()} | {s['topic']}",
                f"3. **Topik utama:** {s['topic']}" + (" → " + " → ".join(t["label"] for t in b["topics"][1:]) if len(b["topics"]) > 1 else ""),
                f"4. **Timestamp sumber ({src['file']}):** " +
                (f"hook {tc(hook['a'])}–{tc(hook['b'])}; " if hook else "") +
                "badan " + "; ".join(f"{tc(a)}–{tc(bb)}" for a, bb in s["ranges"]) +
                f" (dipotong kepada {len(body)} segmen; jeda >{s.get('gap',0.9)} s dibuang — lihat `deliverables/{cid}/EDL.txt`)",
                f"5. **Durasi output akhir:** {b['duration']:.1f} s",
                f"6. **Transkrip segmen:** `deliverables/{cid}/transkrip.txt` (sari kata: `deliverables/{cid}/{cid}.srt`)",
                f"7. **Ayat pembukaan (hook 0–{b['hook_end']:.1f} s):** “{hook_txt}”",
                "8. **Fakta untuk grafik animasi** (muncul serentak dengan perkataan yang disebut):", "",
                "| Masa | Label | Grafik |", "|---|---|---|"]
        out += [fact_line(f) for f in b["facts"]]
        if b.get("conclusion"):
            c = b["conclusion"]
            out.append(f'| {tc(c["start"])} | {c.get("kicker","")} | Penutup: {plain(c["text"])} |')
        out += ["",
                f"9. **Lower third:** {b['hook_end']+0.6:.1f}–{b['hook_end']+0.6+s.get('l3_dur',9):.1f} s — “{s.get('speaker','DR. K')}” / “{s.get('role','')}” / jalur topik “{s['topic'].upper()}”. "
                "Panel navy, garis emas menegak, garis biru elektrik dilukis; kemudian berubah menjadi Topic Lower Third (pil kiri atas): "
                + " → ".join(f'“{t["label"].upper()}” @ {tc(t["start"])}' for t in b["topics"]) + ".",
                f"10. **Hyperframe motion:** Cover 0–{min(2.6, b['hook_end']-0.6):.1f} s (bingkai 0 = thumbnail, `output/covers/{cid}_{slug(s['topic'])}_COVER.jpg`): bingkai emas berganda, "
                f"“PETIKAN UCAPAN”, cip emas “{s.get('hook_kicker','')}”, tajuk utama “{plain(s.get('cover_title', s['hook_title']))}” dengan sorotan emas, nama & jawatan di bawah; "
                "hiasan cover pudar, tajuk mengecil dan kekal hingga hook tamat; kilat biru + whoosh sinematik pada peralihan. "
                "Kamera: punch-in berselang 1.00×/1.10× pada setiap jump-cut, push-in perlahan 3.5% dalam setiap segmen, hook dizum 1.18×. "
                f"Penutup ~{tc(b['conclusion']['start']) if b.get('conclusion') else '-'}: mesej utama + garis emas, slate akhir navy 3.2 s.",
                f"11. **Muzik & audio:** {MOOD[s.get('mood','serious')]}. Skor asal dijana prosedural (bebas royalti) — `tools/score.py`. "
                "Suara asal: high-pass 85 Hz, denoise FFT, EQ (−1.5 dB @220 Hz, +2.5 dB @3.2 kHz), kompresor 3:1, loudnorm −16 LUFS. "
                "Muzik di-duck (sidechain 7:1) semasa ucapan, naik beransur dalam 14 s terakhir dengan riser & hentaman akhir. "
                "SFX (Pixabay): impact pada hook, whoosh pada peralihan/kad, impact-bass pada angka & penutup. Tiada sorakan palsu ditambah.",
                f"12. **Sari kata:** {len(open(os.path.join(ROOT,'deliverables',cid,cid+'.srt')).read().strip().split(chr(10)+chr(10)))} kumpulan, 2–4 perkataan, Montserrat ExtraBold huruf besar putih + stroke navy, "
                "pendedahan perkataan demi perkataan; kata kunci emas 3D (" + ", ".join(s.get("keywords", [])[:8]) + ") dan biru elektrik (nama parti/gabungan).",
                f"13. **Cadangan B-roll:** {s.get('broll', src.get('broll','Tidak diperlukan — wajah penceramah kekal fokus; grafik fakta menggantikan B-roll.'))}",
                ""]
        notes = s.get("notes")
        if notes: out += [f"> **Nota semakan:** {notes}", ""]
    out += ["## C. FAIL AKHIR", "",
            "| Fail | Durasi |", "|---|---|"]
    for p in sorted(glob.glob(os.path.join(ROOT, "output/VIDEO_*.mp4"))):
        if ".tmp" in p: continue
        import subprocess
        d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip()
        out.append(f"| `output/{os.path.basename(p)}` | {float(d):.1f} s |")
    out += ["", "Format: MP4 H.264 1080×1920 (9:16) 30 fps, audio AAC 48 kHz stereo.", ""]
    open(os.path.join(ROOT, "deliverables/LAPORAN_PRODUKSI.md"), "w").write("\n".join(out))
    print("written", len(specs), "clips")

if __name__ == "__main__":
    main()
