#!/usr/bin/env python3
"""Build compositions/captions.html from the word-level transcript of clip B.

Source words: tools/words-b.json  ([start, end, text] in SOURCE seconds,
whisper large-v3-turbo + DTW, Malay). Text is corrected against a second
whisper large-v3 pass (see tools/b-l3.srt) and targeted snippet re-checks.

The edit (CUTS) maps source time -> output time. Only words that fall
inside a cut are captioned. Run:  python3 tools/build_captions.py
"""
import json, html, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
words = json.load(open(os.path.join(ROOT, "tools", "words-b.json")))

# (src_in, src_out, out_start) — keep in sync with index.html <video> clips
CUTS = [
    (117.25, 122.45, 0.00),   # v1 hook
    (0.75, 59.27, 5.20),      # v2 identity + isi 1 + isi 2
    (73.40, 84.20, 63.72),    # v3 isi 3 (punca: pengairan)
    (88.87, 130.45, 74.52),   # v4 klimaks + tuntutan
]

# Text corrections by word index (None = drop the token: stumble/duplicate)
FIX = {
    17: "Muhammad", 18: "Nasir", 25: "Batu 13", 55: "Muhammad", 56: "Nasir",
    148: "Perdana", 90: "menteri", 89: "kementerian,", 94: "ini.",
    0: "Berkaitan", 4: "padi.", 6: "sahabat", 10: None, 11: None, 12: "bil",
    14: "padi,", 15: "oleh", 16: "Saudara", 20: "Kamarudin.", 21: "Pesawah",
    24: "saya,", 26: None, 27: "Bota", 28: "Kiri.", 29: "Di", 32: "dia",
    34: "7,600", 35: "tan…", 36: "7,600", 37: "kilo.", 38: "Tetapi",
    42: "ialah", 44: "peratus,", 45: "iaitu", 46: "5,472", 47: "dipotong.",
    48: "Hanya", 50: "dikira ialah", 51: "2,128", 52: "kilo.", 54: "Encik",
    59: "RM11,400,", 60: "tapi", 64: "RM3,192.", 65: "Dulu", 69: "satu",
    73: "65%", 74: "potongan.", 78: "yang", 81: "lagi,", 83: "72%.",
    84: "Potongan", 85: "pemutuan", 86: "ini.", 112: "Saya",
    115: "sesi", 116: "libat", 117: "urus", 118: "kepada",
    119: None, 120: None, 121: None, 122: None,
    123: "beberapa", 126: "berkenaan,", 127: "menyatakan", 129: "yang",
    132: "ialah", 133: "pengairan.", 134: "Punca", 136: "ialah", 137: "pengairan.",
    144: "Yang", 145: "Amat", 146: "Berhormat", 147: "Tambun,", 149: "Menteri",
    150: "telah", 153: "tentang", 154: "pengezonan", 155: "jelapang", 157: "bagi",
    158: "Parit", 160: "pada", 162: "Bajet", 164: "pertama.", 165: "Sekarang",
    167: "Bajet", 168: "kelima.", 169: "Disebut", 171: "pengezonan", 172: "ini,", 173: "malangnya",
    176: "tidak", 177: "dilaksanakan", 178: "sehinggalah", 181: "ini,",
    182: "menyebabkan", 188: "teruk.", 189: "Dah", 192: "dua", 196: "menanam",
    197: "padi.", 198: "Dua", 199: "musim.", 200: "Mereka", 203: "saya,",
    204: "“YB,", 205: "kalau", 207: "musim…", 208: "tiga", 210: "kami",
    213: "padi,", 214: "habislah", 215: "kami.", 216: "Matilah", 217: "kami.”",
    218: "Tuan Yang", 219: "di-Pertua,", 220: "saya", 222: "supaya",
    224: "jelapang", 225: "padi", 226: "disegerakan", 229: "saya.",
}
# The silence detector shows speech resumes at 124.9 s after "kami." —
# DTW smeared these two tokens across the pause.
RETIME = {0: (0.84, 1.25), 1: (1.25, 1.50), 218: (124.92, 125.30), 219: (125.30, 125.80), 144: (88.90, 89.07)}

KEY = re.compile(
    r"^(padi|sawah|7,600|72|5,472|2,128|RM11,400|RM3,192|65%|72%|pengairan|"
    r"pengezonan|jelapang|pertama|kelima|dilaksanakan|habislah|matilah|"
    r"disegerakan|parit|bota|kiri|dipotong|teruk|dua|tiga|pemutuan)$",
    re.I,
)

out_words = []
for src_in, src_out, o in CUTS:
    for i, (s, e, t) in enumerate(words):
        if i in RETIME:
            s, e = RETIME[i]
        text = FIX.get(i, t)
        if text is None or not text.strip():
            continue
        if i not in FIX:
            text = text.lower() if text not in ("YB",) else text
        cs, ce = max(s, src_in), min(e, src_out)
        mid = (s + e) / 2
        if not (src_in <= mid < src_out):
            continue
        ce = max(ce, cs + 0.05)
        out_words.append([round(cs - src_in + o, 3), round(ce - src_in + o, 3), text, i])

# Capitalise sentence starts that were lower-cased
prev_end_punct = True
for w in out_words:
    if prev_end_punct and w[2][0].islower():
        w[2] = w[2][0].upper() + w[2][1:]
    prev_end_punct = w[2].endswith((".", "”"))

# Hook (0–5.2) is set as kinetic type in s1-hook; the callback of the same
# line in the climax is shown big in s7 — both skip the caption track.
SKIP = [(0.0, 5.2), (103.30, 108.25)]

def skipped(t):
    return any(a <= t < b for a, b in SKIP)

groups, cur = [], []
for w in out_words:
    if skipped(w[0]):
        continue
    if cur:
        gap = w[0] - cur[-1][1]
        if cur[-1][3] in (9, 203):  # "ada … bil belian padi": stumble removed, keep together
            gap = 0
        if (len(cur) >= 4 or gap > 0.35
                or cur[-1][2].endswith((".", "”")) and len(cur) >= 1
                or (cur[-1][2].endswith((",", "…")) and len(cur) >= 2 and cur[-1][3] != 203)
                or len(" ".join(x[2] for x in cur + [w])) > 30):
            groups.append(cur); cur = []
    cur.append(w)
if cur:
    groups.append(cur)

# timing: open at first word start (or slightly before), close at next group start
rows = []
for gi, g in enumerate(groups):
    start = max(0.0, g[0][0] - 0.05)
    end = g[-1][1] + 0.6
    if gi + 1 < len(groups):
        end = min(end, max(0.0, groups[gi + 1][0][0] - 0.05))
    end = min(end, 116.10)
    rows.append((start, end, g))

markup, script = [], []
for gi, (start, end, g) in enumerate(rows):
    spans = []
    for wi, w in enumerate(g):
        core = re.sub(r"[^\w,%.\-]", "", w[2]).strip(".,")
        cls = "w k" if KEY.match(core.replace("RM", "RM")) else "w"
        spans.append(f'<span class="{cls}" id="cw{gi}_{wi}">{html.escape(w[2])}</span>')
    markup.append(
        f'    <div class="cg" id="cg{gi}">' + " ".join(spans) + "</div>"
    )
    script.append(f"  [{start:.3f},{end:.3f},[" + ",".join(f"{w[0]:.3f}" for w in g) + "]]")

TOTAL = 116.10
doc = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    #cap-band {{ position: absolute; left: 0; width: 1080px; top: 1160px; height: 170px; }}
    .cg {{
      position: absolute; left: 70px; width: 940px; top: 0; height: 170px;
      display: flex; flex-wrap: wrap; align-content: center; justify-content: center;
      gap: 0 24px; text-align: center; opacity: 0; overflow: visible;
      font-family: Inter, sans-serif; font-weight: 800; font-size: 62px; line-height: 1.12;
      color: #f4f6fa; letter-spacing: -0.01em;
      text-shadow: 0 3px 0 rgba(4,8,20,.55), 0 6px 22px rgba(0,0,0,.75);
    }}
    .w {{ display: inline-block; opacity: .35; margin: 0 6px; transform-origin: 50% 70%; }}
    .w.k {{ color: #f2c55c; text-shadow: 0 3px 0 #6b4a0e, 0 0 26px rgba(242,197,92,.45), 0 6px 22px rgba(0,0,0,.8); }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
    <div id="cap-band">
{chr(10).join(markup)}
    </div>
  </div>
  <script>
    const G = [
{("," + chr(10)).join(script)}
    ];
    const tl = gsap.timeline({{ paused: true }});
    G.forEach(([s, e, ws], gi) => {{
      const g = "#cg" + gi;
      tl.fromTo(g, {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.16, ease: "power3.out" }}, s);
      ws.forEach((t, wi) => {{
        const el = "#cw" + gi + "_" + wi;
        const isKey = document.querySelector(el).classList.contains("k");
        tl.fromTo(el, {{ opacity: 0.35, scale: isKey ? 0.86 : 1 }},
          {{ opacity: 1, scale: isKey ? 1.06 : 1, duration: isKey ? 0.18 : 0.1, ease: isKey ? "back.out(2.2)" : "power2.out" }}, Math.max(s, t));
        if (isKey) tl.to(el, {{ scale: 1, duration: 0.22, ease: "power2.out" }}, Math.max(s, t) + 0.2);
      }});
      tl.to(g, {{ opacity: 0, duration: 0.1, ease: "power2.in" }}, e - 0.1);
      tl.set(g, {{ opacity: 0, visibility: "hidden" }}, e);
    }});
    tl.set({{}}, {{}}, {TOTAL});
    window.__timelines["captions"] = tl;
  </script>
</template>
"""
open(os.path.join(ROOT, "compositions", "captions.html"), "w").write(doc)

# Also write a plain transcript of the edit (for the edit plan / QA)
with open(os.path.join(ROOT, "tools", "edit-transcript.txt"), "w") as f:
    for start, end, g in rows:
        f.write(f"{start:7.2f}-{end:7.2f}  " + " ".join(w[2] for w in g) + "\n")
print(len(rows), "caption groups")
