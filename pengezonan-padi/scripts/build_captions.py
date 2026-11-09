#!/usr/bin/env python3
"""Captions + SRT for the Pengezonan Padi short.

Word timings: whisper large-v3 (ms) on assets/source/mp1.wav (source 0–228 s) and mp2.wav (source 837–968 s).
Each used segment has a hand-corrected text below, matched to whisper words BY POSITION
(the script stops if the word counts differ). "a|b" splits one whisper word into two.
Re-run after editing:  python3 scripts/build_captions.py
"""
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets/source")
mp1 = [{**w} for w in json.load(open(os.path.join(SRC, "mp1.json")))]
mp2 = [{**w, "start": w["start"] + 837, "end": w["end"] + 837} for w in json.load(open(os.path.join(SRC, "mp2.json")))]
ALL = mp1 + mp2

# (id, source start, source end, video start, corrected text)
SEGMENTS = [
    ("a", 196.40, 204.68, 0.0,
     "Pengezonan jelapang padi di Perak Tengah adalah langkah strategik untuk menjamin sekuriti makanan negara dan perlu direalisasikan segera."),
    ("b", 32.25, 56.42, 8.28,
     "Saya dimaklumkan sebanyak 15,392.8 hektar tanah sawah melibatkan 9,650 lot kini menjadi kawasan strategik pertanian "
     "di bawah seliaan IADA Seberang Perak. Sudah tiba masanya, zon padi Bota Kiri juga dimasukkan dalam kategori kawasan "
     "jelapang padi seperti kawasan Krian, Sungai Manik dan Seberang Perak."),
    ("c", 868.98, 892.62, 32.45,
     "Benih padi yang menjadi punca kepada penyakit di kawasan saya, di Titi Gantung, di Parit, di seluruh Perak Tengah. "
     "Lebih 50% ini hasil padi yang amat mengecewakan. Antara puncanya ialah saliran dan yang keduanya ialah benih padi."),
    ("d", 114.82, 129.44, 56.09,
     "Saya mencadangkan: pertama, insentif khas untuk petani. Subsidi khas untuk benih, baja dan racun. Menetapkan harga "
     "lantai stabil bagi memastikan pulangan adil dan lumayan. Telah|pun dilaksanakan baru-baru ini."),
    ("e", 204.68, 216.48, 70.71,
     "Saya berharap cadangan ini diberikan perhatian kementerian agar sektor pertanian negara lebih berdaya maju dan mampu "
     "mencapai sasaran 70% tahap sara diri (SSR) bagi beras negara."),
]

KEYWORDS = {
    "pengezonan", "jelapang", "strategik", "segera", "15,392.8", "hektar", "9,650", "lot", "iada", "bota", "kiri",
    "krian", "manik", "benih", "penyakit", "50%", "mengecewakan", "saliran", "insentif", "subsidi", "harga", "lantai",
    "stabil", "dilaksanakan", "berdaya", "maju", "70%", "ssr", "beras",
}


def norm(t):
    return "".join(c for c in t.lower() if c.isalnum() or c in ",.%-").strip(",.")


def build_segment(sid, s0, s1, v0, text):
    ws = [w for w in ALL if w["start"] >= s0 - 0.03 and w["end"] <= s1 + 0.05]
    toks = text.split()
    if len(toks) != len(ws):
        raise SystemExit(f"segment {sid}: {len(toks)} corrected words vs {len(ws)} whisper words\n"
                         + " ".join(w["text"] for w in ws))
    out = []
    for tok, w in zip(toks, ws):
        st, en = max(w["start"], s0), min(w["end"], s1)
        parts = tok.split("|")
        step = (en - st) / len(parts)
        for i, p in enumerate(parts):
            a, b = st + i * step, st + (i + 1) * step
            out.append({"text": p, "src": round(a, 3), "start": round(a - s0 + v0, 3), "end": round(b - s0 + v0, 3)})
    return out


segs = {sid: build_segment(sid, s0, s1, v0, t) for sid, s0, s1, v0, t in SEGMENTS}
seg_end = {sid: v0 + (s1 - s0) for sid, s0, s1, v0, _ in SEGMENTS}


def group(ws, max_words, max_chars):
    groups, cur = [], []
    for i, w in enumerate(ws):
        cur.append(w)
        nxt = ws[i + 1] if i + 1 < len(ws) else None
        text = " ".join(x["text"] for x in cur)
        if (nxt is None or w["text"][-1] in ",.:!?" or nxt["start"] - w["end"] >= 0.3
                or len(cur) >= max_words or len(text + " " + nxt["text"]) > max_chars):
            groups.append(cur)
            cur = []
    return groups


G, win = [], []
for sid, *_ in SEGMENTS:
    hi = sid in ("a", "e")  # high energy: 3 words
    for g in group(segs[sid], 3 if hi else 4, 19):
        G.append(g)
        win.append([max(0.12, g[0]["start"] - 0.06), g[-1]["end"] + 0.25, seg_end[sid]])
for i in range(len(win)):
    if i + 1 < len(win) and win[i][1] > win[i + 1][0]:
        win[i][1] = win[i + 1][0]
    win[i][1] = min(win[i][1], win[i][2] - 0.04)  # clear before each cut


def size_for(text):
    n = len(text)
    return 70 if n <= 13 else 62 if n <= 16 else 54


parts, js = [], []
for gi, (g, (gs, ge, _)) in enumerate(zip(G, win)):
    text = " ".join(w["text"] for w in g)
    spans, jw = [], []
    for wi, w in enumerate(g):
        wid = f"cw{gi}-{wi}"
        spans.append(f'<span id="{wid}" class="cw">{html.escape(w["text"].upper())}</span>')
        jw.append([wid, w["start"], w["end"], 1 if norm(w["text"]) in KEYWORDS else 0])
    parts.append(f'    <div id="cg{gi}" class="cg"><div class="cbox" style="font-size:{size_for(text)}px">' + " ".join(spans) + "</div></div>")
    js.append([f"cg{gi}", round(gs, 3), round(ge, 3), jw])

doc = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; background: transparent; }}
    /* Caption band: bottom of the TikTok-safe area (above y=1330), under the speaker's chin. */
    .cg {{ position: absolute; left: 0; top: 1150px; width: 1080px; height: 176px; display: flex; align-items: flex-end;
      justify-content: center; text-align: center; overflow: visible; opacity: 0; visibility: hidden; }}
    .cbox {{ display: inline-block; max-width: 940px; padding: 8px 26px 12px; border-radius: 14px; background: rgba(8, 11, 19, 0.5);
      font-family: "Montserrat", sans-serif; font-weight: 800; line-height: 1.16; letter-spacing: 0.01em; color: #ffffff;
      -webkit-text-stroke: 3px #000; paint-order: stroke fill; text-shadow: 0 4px 14px rgba(0, 0, 0, 0.55); }}
    .cw {{ display: inline-block; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{chr(10).join(parts)}
  </div>
  <script>
    // Generated by scripts/build_captions.py. Edit there, then re-run.
    const GROUPS = {json.dumps(js)};
    const tl = gsap.timeline({{ paused: true }});
    const YEL = "#FFD447";
    for (const [gid, gs, ge, ws] of GROUPS) {{
      const g = "#" + gid;
      tl.set(g, {{ visibility: "visible" }}, gs);
      tl.fromTo(g, {{ opacity: 0 }}, {{ opacity: 1, duration: 0.12, ease: "power2.out" }}, gs);
      tl.fromTo(g + " .cbox", {{ scale: 0.88 }}, {{ scale: 1, duration: 0.22, ease: "back.out(1.7)" }}, gs);
      for (const [wid, ws0, we, key] of ws) {{
        const w = "#" + wid;
        tl.set(w, {{ color: YEL }}, ws0);
        if (key) {{
          tl.fromTo(w, {{ scale: 1 }}, {{ scale: 1.14, duration: 0.1, ease: "power2.out" }}, ws0);
          tl.to(w, {{ scale: 1, duration: 0.2, ease: "power2.out" }}, ws0 + 0.1);
        }} else {{
          tl.set(w, {{ color: "#FFFFFF" }}, Math.min(we, ge - 0.02));
        }}
      }}
      tl.to(g, {{ opacity: 0, duration: 0.1, ease: "power2.in" }}, ge - 0.1);
      tl.set(g, {{ opacity: 0, visibility: "hidden" }}, ge);
    }}
    window.__timelines["captions"] = tl;
  </script>
</template>
"""
open(os.path.join(ROOT, "compositions/captions.html"), "w").write(doc)


def ts(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def two_lines(ws):
    text = " ".join(w["text"] for w in ws)
    if len(text) <= 36 or len(ws) < 2:
        return text
    k = min(range(1, len(ws)), key=lambda k: abs(len(" ".join(w["text"] for w in ws[:k])) - len(text) / 2))
    return " ".join(w["text"] for w in ws[:k]) + "\n" + " ".join(w["text"] for w in ws[k:])


os.makedirs(os.path.join(ROOT, "deliverables"), exist_ok=True)
with open(os.path.join(ROOT, "deliverables/subtitles-video.srt"), "w") as f:
    for i, (g, (gs, ge, _)) in enumerate(zip(G, win), 1):
        f.write(f"{i}\n{ts(gs)} --> {ts(ge)}\n{' '.join(w['text'] for w in g)}\n\n")

# Source-clock SRT for the five used segments (hand-corrected text).
cues = []
for sid, *_ in SEGMENTS:
    for g in group(segs[sid], 12, 64):
        cues.append((g[0]["src"], g[-1]["src"] + (g[-1]["end"] - g[-1]["start"]), two_lines(g)))
cues.sort()
with open(os.path.join(ROOT, "deliverables/subtitles-source-segmen.srt"), "w") as f:
    for i, (a, b, t) in enumerate(cues, 1):
        f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n")

# Full speech of the MP (0:00–3:38 and the 14:00–16:06 follow-up): automatic transcript with
# common mis-hearings fixed. Only the five used segments were checked word by word.
FIX = {
    "Jalapang": "jelapang", "jelapan": "jelapang", "Pengesunan": "Pengezonan", "pengazonan": "pengezonan",
    "Perkaitan": "berkaitan", "Aida,": "IADA,", "hektare": "hektar", "pesawat": "pesawah", "pesawat-pesawat": "pesawah-pesawah",
    "pump": "pam", "petanian": "pertanian", "babau": "baru-baru", "Telahpun": "Telah pun", "telahpun": "telah pun",
    "pembinaan": "pembenihan", "titik": "Titi", "Titik": "Titi", "gantung": "Gantung", "Ali": "Ahli", "menghormat": "Berhormat", "Endi": "Yang", "Indi": "Yang", "Petua": "di-Pertua",
}
full = [w for w in mp1 if w["start"] < 218.5] + [w for w in mp2 if w["start"] < 966.5]
for w in full:
    w["text"] = FIX.get(w["text"], w["text"])
fg = []
cur = []
for i, w in enumerate(full):
    cur.append(w)
    nxt = full[i + 1] if i + 1 < len(full) else None
    if nxt is None or len(" ".join(x["text"] for x in cur + [nxt])) > 64 or nxt["start"] - w["end"] > 0.6:
        fg.append(cur)
        cur = []
with open(os.path.join(ROOT, "deliverables/subtitles-ucapan-penuh.srt"), "w") as f:
    for i, g in enumerate(fg, 1):
        lines = two_lines([{"text": x["text"]} for x in g])
        f.write(f"{i}\n{ts(g[0]['start'])} --> {ts(g[-1]['end'])}\n{lines}\n\n")

print(f"{len(G)} caption groups, {len(cues)} segment cues, {len(fg)} full-speech cues")
