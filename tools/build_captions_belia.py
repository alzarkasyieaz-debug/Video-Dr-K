#!/usr/bin/env python3
"""Build ep2-belia/compositions/captions.html from the word-level transcript of clip A.

Source words: tools/words-a.json  ([start, end, text] in SOURCE seconds,
whisper large-v3-turbo + DTW, Malay). Text is corrected against a second
whisper large-v3 pass (see tools/b-l3.srt) and targeted snippet re-checks.

The edit (CUTS) maps source time -> output time. Only words that fall
inside a cut are captioned. Run:  python3 tools/build_captions.py
"""
import json, html, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "ep2-belia")
words = json.load(open(os.path.join(ROOT, "tools", "words-a.json")))

# (src_in, src_out, out_start) — keep in sync with ep2-belia/index.html <video> clips
CUTS = [
    (4.18, 9.28, 0.00),     # v1 hook: "Angka 3.0% adalah angka yang menipu realiti."
    (0.05, 4.14, 5.10),     # v2 "Berkaitan dengan pengangguran belia dan kualiti pekerjaan,"
    (9.28, 81.07, 9.19),    # v3 isi 1–4
    (81.81, 85.50, 80.98),  # v4 "Penyelesaian … dasar gaji progresif"
    (88.02, 111.02, 84.67), # v5 "menerusi insentif …" → end
]

# Text corrections by word index (None = drop). Checked against whisper large-v3
# and snippet re-runs: "30.0%" is spoken "tiga perpuluhan kosong peratus" (3.0%),
# "64%" is "enam perpuluhan empat peratus" (6.4%).
FIX = {
    3: "belia", 6: "pekerjaan,", 7: "Angka", 8: "3.0%", 13: "realiti.",
    14: "Walaupun", 22: "3%", 24: "520,300", 25: "penganggur,",
    34: "Kadar", 36: "belia", 38: "15", 40: "24", 45: "10%,", 48: "belia",
    49: "15", 51: "30", 54: "6.4%.", 55: "Statistik", 72: "Isu", 78: "muda,",
    83: "kerja,", 89: "Fenomena", 93: "stagnan,", 96: "underemployment",
    104: "perlindungan", 118: "minimum.", 119: "Di", 127: "Parit,",
    131: "kolar", 132: "putih", 143: "Parit.", 144: "Penyelesaian",
    146: "krisis", 152: "progresif,", 153: None, 154: None, 155: None, 156: None,
    163: "tempatan.", 164: "Pada", 167: "sama,", 169: "levi", 170: "bertingkat,",
    171: "multi-tier", 172: "levi", 183: "dilaksanakan.", 184: "Di", 188: "levi",
    201: "tempatan.",
}
RETIME = {152: (84.85, 85.22), 157: (88.04, 88.38), 158: (88.74, 89.10), 7: (4.20, 4.70), 8: (4.70, 6.59)}

KEY = re.compile(
    r"^(3\.0%|3%|520,300|10%|6\.4%|15|24|30|belia|menipu|realiti|kualiti|stagnan|"
    r"underemployment|gig|minimum|parit|keluar|progresif|levi|bertingkat|automasi|"
    r"penggajian|graduan|stabil|kualitatif|tempatan)$",
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
SKIP = [(0.0, 5.10)]

def skipped(t):
    return any(a <= t < b for a, b in SKIP)

groups, cur = [], []
for w in out_words:
    if skipped(w[0]):
        continue
    if cur:
        gap = w[0] - cur[-1][1]
        if cur[-1][3] in (152,):  # "ada … bil belian padi": stumble removed, keep together
            gap = 0
        if (len(cur) >= 4 or gap > 0.35
                or cur[-1][2].endswith((".", "”")) and len(cur) >= 1
                or (cur[-1][2].endswith((",", "…")) and len(cur) >= 2 and cur[-1][3] != 152)
                or len(" ".join(x[2] for x in cur + [w])) > 30):
            groups.append(cur); cur = []
    cur.append(w)
if cur:
    groups.append(cur)

# timing: open at first word start (or slightly before), close at next group start
TOTAL = 107.67
rows = []
for gi, g in enumerate(groups):
    start = max(0.0, g[0][0] - 0.05)
    end = g[-1][1] + 0.6
    if gi + 1 < len(groups):
        end = min(end, max(0.0, groups[gi + 1][0][0] - 0.05))
    end = min(end, TOTAL)
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
open(os.path.join(OUT, "compositions", "captions.html"), "w").write(doc)

# Also write a plain transcript of the edit (for the edit plan / QA)
with open(os.path.join(ROOT, "tools", "edit-transcript-belia.txt"), "w") as f:
    for start, end, g in rows:
        f.write(f"{start:7.2f}-{end:7.2f}  " + " ".join(w[2] for w in g) + "\n")
print(len(rows), "caption groups")
