#!/usr/bin/env python3
"""Build ep3-seri-iskandar/<isu>/compositions/captions.html for one per-issue video cut from clip C.

Usage: python3 tools/build_captions_isu.py isu1-pasar|isu2-jalan|isu3-dataran|isu4-rumah

Source words: tools/words-c.json  ([start, end, text] in SOURCE seconds,
whisper large-v3-turbo + DTW, Malay). Text is corrected against a second
whisper large-v3 pass (see tools/b-l3.srt) and targeted snippet re-checks.

The edit (CUTS) maps source time -> output time. Only words that fall
inside a cut are captioned. Run:  python3 tools/build_captions.py
"""
import json, html, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "ep3-seri-iskandar", sys.argv[1] if len(sys.argv) > 1 else "")
words = json.load(open(os.path.join(ROOT, "tools", "words-c.json")))

import sys
# One video per issue, all cut from clip C (the Seri Iskandar speech).
# (src_in, src_out, out_start) — keep in sync with each project's index.html <video> clips
SPECS = {
    "isu1-pasar": dict(total=74.37, skip=[(0.0, 3.40)], cuts=[
        (67.45, 70.85, 0.00), (46.95, 57.82, 3.40), (61.40, 67.10, 14.27), (71.95, 87.20, 19.97),
        (89.15, 101.75, 35.22), (103.10, 114.50, 47.82), (115.30, 120.45, 59.22), (159.72, 169.72, 64.37)]),
    "isu2-jalan": dict(total=70.97, skip=[(0.0, 6.00)], cuts=[
        (213.10, 219.10, 0.00), (187.90, 213.00, 6.00), (221.42, 253.45, 31.10), (254.98, 262.82, 63.13)]),
    "isu3-dataran": dict(total=38.88, skip=[], cuts=[(264.68, 303.56, 0.00)]),
    "isu4-rumah": dict(total=53.88, skip=[(0.0, 4.15)], cuts=[
        (341.50, 345.65, 0.00), (304.72, 306.80, 4.15), (308.65, 356.30, 6.23)]),
}
ISU = sys.argv[1]
CUTS = SPECS[ISU]["cuts"]

# Text corrections (turbo words, checked against whisper large-v3; large-v3
# hallucinates repeats between 03:27 and 03:57, so turbo is used there).
FIX = {
    216: None, 224: "pasar", 235: "Iskandar", 296: "kenderaan", 561: "sebenar",
    37: "memiliki", 38: "UTP,", 39: "UiTM,", 40: "Kolej", 41: "Profesional", 42: "MARA,", 43: "IKBN,",
    48: "sekolah-sekolah", 56: "kerajaan.", 130: "peniaga", 134: "peniaga", 145: "berpatutan.",
    217: "apakah", 218: "piawaian", 228: "KPKT", 232: "kelayakan", 234: "Seri", 237: "PLANMalaysia?", 238: None,
    303: "datang,", 304: "kerana", 324: "Peruntukan", 325: "Kerajaan", 326: "Tempatan", 329: "RM69.8",
    333: "2027,", 335: "3.3%.", 336: "Manakala", 337: "SMK,", 342: "RM60.87", 345: "RM480.87", 346: "juta.",
    347: "Soalan", 348: "saya,", 351: "…", 355: "KPKT", 357: "PBT", 365: "KPKT", 372: "tersebut?",
    373: "Kedua,", 378: "Seri Iskandar", 387: "purata", 389: "penyelesaiannya?",
    409: "Hanya", 413: "jogging", 417: "sahaja.", 438: "Kemudian", 439: "OKU,", 444: "kecil.",
    445: "Soalan", 446: "saya,", 448: "KPKT", 451: "Dataran", 452: "Sungai", 453: "Seluang", 462: "ini?",
    517: "Soalan", 518: "saya,", 522: "PPR,", 523: "Rumah", 524: "Mesra", 525: "Rakyat", 527: "PRIMA",
    531: "Parlimen", 532: "Parit", 536: "ini?", 537: "Dan", 542: "pasti?", 543: "Kedua,", 545: "kuota",
    546: "Rumah", 547: "Mesra", 548: "Rakyat", 549: "SPNB", 552: "Perak", 556: "Perak", 557: "Tengah?",
    558: "Dan", 564: "sifar?", 565: "Ketiga,", 567: "KPKT", 572: "negeri", 584: "Seri Iskandar", 586: "Parit",
    592: "negeri?",
    25: "Iskandar", 60: "Iskandar", 79: "Iskandar", 266: "Iskandar", 320: "JKR",
    475: "B40", 477: "M40", 479: "Parlimen", 492: "Ipoh", 155: "di", 157: "Iskandar…?",
    24: "Seri", 28: "pentadbiran", 29: "daerah Perak", 30: "Tengah,", 34: "ilmu.",
    57: "Malangnya,", 59: "Seri", 66: "pasar", 67: "awam.", 68: "Penduduk", 71: "2020",
    73: "14,827.", 74: "Tapi", 78: "Seri", 84: "35,000", 85: "orang.", 86: "Namun",
    91: "pasar", 94: "Seri", 95: "Iskandar.", 96: "Untuk", 97: "makluman,", 103: "rumah,",
    104: "ikan,", 116: "sebagainya.", 117: "Jadi,", 121: "pasar", 124: "selesa,",
    127: "teratur,", 128: "moden,", 146: "Soalan", 147: "saya,", 153: "pasar", 156: "Seri",
    157: "Iskandar…?", 262: "Dato'", 263: "Pengerusi,", 265: "Seri", 276: "rosak,",
    283: "dibaiki.", 284: "Lubang", 294: "kemalangan,", 296: "kenderaan", 309: "Seri",
    310: "Iskandar.", 311: "Sebenarnya", 319: "PBT,", 322: "Kerajaan", 323: "Negeri.",
    390: "Ketiga,", 393: "Dataran", 394: "Sungai", 395: "Seluang,", 396: "Tuan",
    397: "Pengerusi,", 402: "hektar", 408: "taraf.", 418: "Ianya", 425: "didirikan",
    428: "kanak-kanak,", 432: "teduhan,", 434: "awam,", 437: "sebagainya.",
    463: "Yang", 464: "keempat,", 469: "rendah.", 470: "Tuan", 471: "Pengerusi,",
    480: "Parit", 487: "sendiri.", 488: "Mereka", 491: "Seri Iskandar,", 494: "Bota,",
    502: "mereka.", 503: "Yang", 516: "berhampiran.",
}
# DTW collapsed several runs of words onto one timestamp; spread them across
# the speech window measured from the audio envelope.
RETIME = {
    42: (56.85, 57.30), 43: (57.30, 57.78),
    373: (255.00, 255.20), 374: (255.96, 256.30), 375: (256.30, 256.55), 376: (256.55, 257.00),
    409: (273.70, 273.95), 410: (273.95, 274.40), 558: (341.54, 341.70), 559: (341.70, 341.95),
    68: (71.98, 72.30), 69: (72.30, 72.55), 117: (103.14, 103.30), 118: (103.30, 103.50),
    119: (103.50, 103.85), 155: (119.75, 119.88), 156: (119.88, 120.02), 157: (120.02, 120.42),
    262: (187.96, 188.15), 263: (188.15, 188.50), 264: (188.50, 188.85),
    390: (264.74, 265.10), 391: (265.10, 265.45), 392: (265.45, 265.70),
    465: (305.30, 305.60), 466: (305.60, 305.80), 467: (305.80, 306.10), 468: (306.10, 306.30),
    469: (306.30, 306.75), 503: (320.84, 321.00), 504: (321.00, 321.20), 505: (321.20, 321.60),
    24: (47.02, 47.25), 25: (47.25, 47.70), 26: (47.70, 47.95), 27: (47.95, 48.20),
    28: (48.20, 48.75), 29: (48.75, 49.20), 30: (49.20, 49.60), 31: (49.60, 49.80),
    32: (49.80, 50.20), 33: (50.20, 50.50), 34: (50.50, 51.00),
    86: (84.98, 85.20), 87: (85.20, 85.40), 88: (85.40, 85.55), 89: (85.55, 85.75),
    90: (85.75, 85.95), 91: (85.95, 86.20), 92: (86.20, 86.40), 93: (86.40, 86.55),
    94: (86.55, 86.75), 95: (86.75, 87.15), 96: (89.20, 89.45), 97: (89.45, 89.85),
    284: (198.76, 199.00), 285: (199.00, 199.15), 286: (199.15, 199.45),
    418: (279.60, 279.85), 419: (279.85, 280.05),
    463: (304.80, 304.95), 464: (304.95, 305.30),
    470: (308.72, 308.90), 471: (308.90, 309.30), 472: (309.30, 309.50), 473: (309.50, 309.70),
    474: (309.70, 309.90), 475: (309.90, 310.20), 476: (310.20, 310.30), 477: (310.30, 310.60),
    478: (310.60, 310.70), 479: (310.70, 311.00), 480: (311.00, 311.30), 481: (311.30, 311.50),
    488: (314.80, 315.00), 489: (315.00, 315.30), 490: (315.30, 315.40), 491: (315.40, 315.90),
    492: (315.90, 316.20), 493: (316.20, 316.35), 494: (316.35, 316.60),
}

KEY = re.compile(
    r"^(pasar|14,827|35,000|letih|berlubang|berbulan-bulan|kemalangan|mengadu|19|hektar|"
    r"kanak-kanak|B40|M40|rendah|mampu|milik|bersih|moden|selesa|teratur|pencemaran|"
    r"tandas|lampu|parit|bota|ipoh|seluang|lama)$",
    re.I,
)

out_words = []
for ci, (src_in, src_out, o) in enumerate(CUTS):
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
        out_words.append([round(cs - src_in + o, 3), round(ce - src_in + o, 3), text, i, ci])

# Capitalise sentence starts that were lower-cased
prev_end_punct = True
for w in out_words:
    if prev_end_punct and w[2][0].islower():
        w[2] = w[2][0].upper() + w[2][1:]
    prev_end_punct = w[2].endswith((".", "”"))

# Hook (0–5.2) is set as kinetic type in s1-hook; the callback of the same
# line in the climax is shown big in s7 — both skip the caption track.
SKIP = SPECS[ISU]["skip"]

def skipped(t):
    return any(a <= t < b for a, b in SKIP)

groups, cur = [], []
for w in out_words:
    if skipped(w[0]):
        continue
    if cur:
        gap = w[0] - cur[-1][1]
        if cur[-1][3] in (-1,):  # "ada … bil belian padi": stumble removed, keep together
            gap = 0
        if (len(cur) >= 4 or gap > 0.35 or (w[4] != cur[-1][4] and w[4] not in (3,))
                or cur[-1][2].endswith((".", "”")) and len(cur) >= 1
                or (cur[-1][2].endswith((",", "…")) and len(cur) >= 2 )
                or len(" ".join(x[2] for x in cur + [w])) > 30):
            groups.append(cur); cur = []
    cur.append(w)
if cur:
    groups.append(cur)

# timing: open at first word start (or slightly before), close at next group start
TOTAL = SPECS[ISU]["total"]
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
with open(os.path.join(ROOT, "tools", f"edit-transcript-{sys.argv[1]}.txt"), "w") as f:
    for start, end, g in rows:
        f.write(f"{start:7.2f}-{end:7.2f}  " + " ".join(w[2] for w in g) + "\n")
print(len(rows), "caption groups")
