#!/usr/bin/env python3
"""Generate the HyperFrames composition for the 'Perpaduan UMNO-PAS' speech edit.

Inputs (data/):
  words.json   - forced-aligned caption words on the output timeline
  camera.json  - per-clip camera keys [t, x, y, scale] (smoothed speaker tracking)
  music.json   - optional: score file + ducking levels (written by tools/music.py)

Outputs: index.html and compositions/*.html (plain HTML/CSS/GSAP, editable in Studio).
Re-running overwrites those files, so prefer editing the HTML directly once you start
hand-tuning in Studio, or edit this script and re-run.
"""
import json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920
TOTAL = 84.5

CLIPS = [  # id, output start, duration, source in/out (seconds in 1101.mp4)
    ("a", 0.00, 6.34, 960.66, 967.00),
    ("b", 6.34, 27.42, 130.88, 158.30),
    ("c", 33.76, 13.00, 199.40, 212.40),
    ("d", 46.76, 13.30, 232.30, 245.60),
    ("e", 60.06, 10.39, 481.96, 492.35),
    ("f", 70.45, 10.26, 1134.82, 1145.08),
]
CUTS = [c[1] for c in CLIPS[1:]]

words = json.load(open(os.path.join(ROOT, "data/words.json")))
camera = json.load(open(os.path.join(ROOT, "data/camera.json")))
music = None
if os.path.exists(os.path.join(ROOT, "data/music.json")):
    music = json.load(open(os.path.join(ROOT, "data/music.json")))


def w_at(text, after=0.0):
    for w in words:
        if w["start"] >= after - 1e-6 and w["text"].strip(".,?!").lower() == text.lower():
            return w["start"]
    raise KeyError(text)


FONT_FACE = """
      @font-face { font-family: "Anton"; src: url("assets/fonts/anton-latin-400-normal.woff2") format("woff2"); font-weight: 400; }
      @font-face { font-family: "Bebas Neue"; src: url("assets/fonts/bebas-neue-latin-400-normal.woff2") format("woff2"); font-weight: 400; }"""

TOKENS = """
      #root {
        --navy: #0a1630; --navy-deep: #050b1a; --gold: #d9a93a; --gold-bright: #f4c95d;
        --ink: #ffffff; --hl: #ffd84a;
        position: absolute; inset: 0; overflow: visible;
      }"""


def scene(cid, body, script, extra_css="", motion_blur=False):
    mb = ' data-motion-blur="on"' if motion_blur else ""
    return f"""<template>
  <style>{FONT_FACE}{TOKENS}{extra_css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}"{mb}>
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{script}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""


def r(x):
    return round(x, 3)


# Shared card css -----------------------------------------------------------------
CARD_CSS = """
      .dim { position: absolute; left: 0; top: 0; width: 1080px; height: 860px;
        background: linear-gradient(180deg, rgba(5,11,26,.88) 0%, rgba(5,11,26,.74) 55%, rgba(5,11,26,0) 100%); opacity: 0; }
      .kicker { font-family: "Bebas Neue", sans-serif; font-size: 44px; letter-spacing: .14em; color: var(--gold-bright); }
      .gline { height: 4px; background: linear-gradient(90deg, var(--gold-bright), var(--gold) 70%, rgba(217,169,58,0)); transform-origin: 0 50%; }
      .hl { font-family: "Anton", sans-serif; color: var(--ink); line-height: 1.02; text-transform: uppercase;
        text-shadow: 0 6px 30px rgba(0,0,0,.55); }
      .gold { color: var(--gold-bright); }
      .w { display: inline-block; }
      .mask { display: block; overflow: hidden; padding: 0 6px 6px 0; }
      .sub { font-family: "Montserrat", sans-serif; font-weight: 600; font-size: 34px; line-height: 1.3; color: rgba(255,255,255,.9); }
      .src { font-family: "Montserrat", sans-serif; font-weight: 500; font-size: 28px; color: rgba(255,255,255,.72); }
"""


def words_html(text, cls="w", gold=()):
    out = []
    for i, t in enumerate(text.split()):
        g = " gold" if t.strip(".,").upper() in gold else ""
        out.append(f'<span class="{cls}{g}">{html.escape(t)}</span>')
    return " ".join(out)


def word_reveal(sel, t, stagger=0.08, y=40, blur=8):
    return (f'    tl.fromTo("{sel}", {{ opacity: 0, y: {y}, filter: "blur({blur}px)" }}, '
            f'{{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.42, ease: "expo.out", stagger: {stagger} }}, {r(t)});\n')


def exit_blur(sel, t, d=0.28):
    return (f'    tl.to("{sel}", {{ opacity: 0, filter: "blur(10px)", duration: {d}, ease: "power3.in" }}, {r(t)});\n')


# ---------------------------------------------------------------------------------
# HOOK 0 - 6.34
def build_hook():
    rugi2 = w_at("rakyat")
    yang = w_at("yang")
    body = f"""    <div id="hk-dim" class="dim clip" data-start="0" data-duration="7.3" data-track-index="0"></div>
    <div id="hk-block" class="clip" data-start="0" data-duration="7.3" data-track-index="1"
         style="position:absolute;left:100px;top:236px;width:880px;">
      <div class="mask"><div id="hk-l1" class="hl" style="font-size:150px;">POLITIK</div></div>
      <div class="mask"><div id="hk-l2" class="hl gold" style="font-size:150px;">PERSEPSI</div></div>
      <div id="hk-line" class="gline" style="width:520px;margin:18px 0 22px;"></div>
      <div id="hk-qa" style="position:relative;height:126px;">
        <div id="hk-q" data-layout-allow-overlap class="hl" style="position:absolute;left:0;top:10px;font-size:96px;font-family:'Bebas Neue',sans-serif;letter-spacing:.04em;">
          <span class="w hk-qw">YANG</span> <span class="w hk-qw">RUGI</span> <span class="w hk-qw" id="hk-siapa">SIAPA?</span>
        </div>
        <div id="hk-ans" data-layout-allow-overlap class="hl" style="position:absolute;left:0;top:0;font-size:110px;white-space:nowrap;">
          <span style="font-family:'Bebas Neue',sans-serif;letter-spacing:.04em;font-size:96px;">YANG RUGI:</span>
          <span style="position:relative;display:inline-block;margin-left:8px;"><span id="hk-sweep" style="position:absolute;left:-10px;right:-10px;top:14px;bottom:4px;background:linear-gradient(90deg,var(--gold),var(--gold-bright));transform-origin:0 50%;"></span><span id="hk-rakyat" class="w" style="position:relative;color:var(--navy-deep);padding:0 8px;">RAKYAT.</span></span>
        </div>
      </div>
    </div>"""
    s = ""
    s += '    tl.fromTo("#hk-dim", { opacity: 0.55 }, { opacity: 0.8, duration: 1.2, ease: "power2.out" }, 0);\n'
    # frame 0 already shows the headline (thumbnail), landing from a bold scale-in
    s += '    tl.fromTo("#hk-l1", { scale: 1.1, opacity: 1, filter: "blur(3px)", transformOrigin: "0% 60%" }, { scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.55, ease: "expo.out" }, 0);\n'
    s += '    tl.fromTo("#hk-l2", { yPercent: 105 }, { yPercent: 0, duration: 0.6, ease: "expo.out" }, 0.32);\n'
    s += '    tl.fromTo("#hk-line", { scaleX: 0 }, { scaleX: 1, duration: 0.7, ease: "power3.inOut" }, 0.55);\n'
    s += word_reveal(".hk-qw", yang - 0.05, stagger=0.24, y=26, blur=6)
    s += '    tl.set("#hk-ans", { opacity: 0 }, 0);\n'
    s += f'    tl.set("#hk-ans", {{ opacity: 1 }}, {r(rugi2 - 0.02)});\n'
    s += f'    tl.to("#hk-q", {{ opacity: 0, filter: "blur(8px)", duration: 0.12, ease: "power2.in" }}, {r(rugi2 - 0.14)});\n'
    s += f'    tl.fromTo("#hk-sweep", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.22, ease: "power3.out" }}, {r(rugi2 - 0.02)});\n'
    s += f'    tl.fromTo("#hk-rakyat", {{ scale: 1.35, filter: "blur(8px)", opacity: 0 }}, {{ scale: 1, filter: "blur(0px)", opacity: 1, duration: 0.3, ease: "expo.out", transformOrigin: "0% 50%" }}, {r(rugi2)});\n'
    s += exit_blur("#hk-block", 6.98, 0.24)
    s += '    tl.to("#hk-dim", { opacity: 0, duration: 0.3, ease: "power2.in" }, 6.95);\n'
    return scene("hook", body, s, CARD_CSS, motion_blur=True)


# ---------------------------------------------------------------------------------
# ISSUE 6.34 - 18.54  (local)
def build_issue():
    o = 6.34
    perp = w_at("perpaduan", 6.3) - o
    umno = w_at("UMNO") - o
    pas = w_at("PAS", 15) - o
    body = f"""    <div id="is-dim" class="dim clip" data-start="{r(perp-0.3)}" data-duration="5.0" data-track-index="0"></div>
    <div id="is-kp" class="clip" data-start="{r(perp-0.2)}" data-duration="4.9" data-track-index="1"
         style="position:absolute;left:108px;top:236px;width:864px;">
      <div class="kicker" id="is-k">POINT 01 · ISU UTAMA</div>
      <div id="is-gl" class="gline" style="width:640px;margin:12px 0 22px;"></div>
      <div class="hl" style="font-size:120px;"><span class="w is-w gold">PERPADUAN</span></div>
      <div class="hl" style="font-size:92px;"><span class="w is-w">DUA</span> <span class="w is-w">PARTI</span> <span class="w is-w">TERBESAR</span></div>
      <div class="hl" style="font-size:92px;"><span class="w is-w">UMAT</span> <span class="w is-w">ISLAM</span></div>
    </div>
    <div id="is-vs" class="clip" data-start="{r(umno-0.4)}" data-duration="{r(pas-umno+2.2)}" data-track-index="2"
         style="position:absolute;left:108px;top:300px;width:864px;height:260px;">
      <div id="is-umno" class="party" style="left:0;">UMNO</div>
      <div id="is-x" class="hl gold" style="position:absolute;left:0;width:864px;top:58px;text-align:center;font-size:120px;">+</div>
      <div id="is-pas" class="party" style="right:0;">PAS</div>
    </div>"""
    css = CARD_CSS + """
      .party { position: absolute; top: 40px; width: 360px; height: 180px; display: flex; align-items: center; justify-content: center;
        font-family: "Anton", sans-serif; font-size: 118px; color: #fff; letter-spacing: .02em;
        background: linear-gradient(180deg, rgba(10,22,48,.92), rgba(5,11,26,.92)); border: 3px solid var(--gold); border-radius: 10px;
        box-shadow: 0 18px 50px rgba(0,0,0,.5), inset 0 0 0 1px rgba(244,201,93,.25); }"""
    s = ""
    s += f'    tl.fromTo("#is-dim", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: "power2.out" }}, {r(perp-0.3)});\n'
    s += f'    tl.fromTo("#is-k", {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "expo.out" }}, {r(perp-0.2)});\n'
    s += f'    tl.fromTo("#is-gl", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.6, ease: "power3.inOut" }}, {r(perp-0.15)});\n'
    s += word_reveal(".is-w", perp, stagger=0.11)
    s += exit_blur("#is-kp", r(perp + 4.35), 0.3)
    s += f'    tl.to("#is-dim", {{ opacity: 0, duration: 0.35, ease: "power2.in" }}, {r(perp+4.4)});\n'
    s += f'    tl.fromTo("#is-umno", {{ x: -420, filter: "blur(14px)", opacity: 0 }}, {{ x: 0, filter: "blur(0px)", opacity: 1, duration: 0.5, ease: "expo.out" }}, {r(umno-0.05)});\n'
    s += f'    tl.fromTo("#is-pas", {{ x: 420, filter: "blur(14px)", opacity: 0 }}, {{ x: 0, filter: "blur(0px)", opacity: 1, duration: 0.5, ease: "expo.out" }}, {r(pas-0.05)});\n'
    s += f'    tl.fromTo("#is-x", {{ scale: 0.4, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.35, ease: "back.out(1.6)" }}, {r(pas+0.15)});\n'
    s += exit_blur("#is-vs", r(pas + 1.8), 0.3)
    return scene("issue", body, s, css, motion_blur=True)


# ---------------------------------------------------------------------------------
# EVIDENCE 21.3 - 36.8 (local)
def build_evidence():
    o = 21.3
    n36 = w_at("3.6") - o
    n1 = w_at("1") - o
    ang = w_at("Angkanya") - o
    n46 = w_at("4.6") - o
    end = 36.55 - o
    body = f"""    <div id="ev-dim" class="dim clip" data-start="0" data-duration="{r(end+0.4)}" data-track-index="0"></div>
    <div id="ev-card" class="clip" data-start="0" data-duration="{r(end+0.4)}" data-track-index="1"
         style="position:absolute;left:108px;top:214px;width:864px;">
      <div class="kicker" id="ev-k">POINT 02 · KEAHLIAN MELAYU-ISLAM</div>
      <div id="ev-gl" class="gline" style="width:864px;margin:12px 0 18px;"></div>
      <div class="row" id="ev-r1"><span class="lab">UMNO</span><span class="num">3.6 <small>JUTA</small></span></div>
      <div class="row" id="ev-r2"><span class="lab">PAS</span><span class="num">1 <small>JUTA</small></span></div>
      <div id="ev-div" class="gline" style="width:864px;margin:8px 0 6px;"></div>
      <div class="row tot" id="ev-r3"><span class="lab gold">GABUNGAN</span>
        <span class="num gold" style="position:relative;"><span id="ev-sweep"></span><span style="position:relative;">4.6 <small>JUTA</small></span></span></div>
      <div class="src" id="ev-src" style="margin-top:14px;">Angka seperti disebut penceramah (minit 02:23&ndash;02:38). Belum disahkan secara bebas.</div>
    </div>"""
    css = CARD_CSS + """
      .row { display: flex; align-items: baseline; justify-content: space-between; height: 104px; }
      .lab { font-family: "Bebas Neue", sans-serif; font-size: 70px; letter-spacing: .06em; color: #fff; }
      .num { font-family: "Anton", sans-serif; font-size: 92px; color: #fff; }
      .num small { font-family: "Bebas Neue", sans-serif; font-size: 50px; letter-spacing: .08em; }
      .tot { height: 150px; }
      .tot .num { font-size: 116px; }
      #ev-sweep { position: absolute; left: -14px; right: -14px; top: 18px; bottom: 6px; background: rgba(244,201,93,.18);
        border-left: 6px solid var(--gold-bright); transform-origin: 0 50%; }"""
    s = ""
    s += '    tl.fromTo("#ev-dim", { opacity: 0 }, { opacity: 1, duration: 0.4, ease: "power2.out" }, 0);\n'
    s += '    tl.fromTo("#ev-k", { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 0.45, ease: "expo.out" }, 0.05);\n'
    s += '    tl.fromTo("#ev-gl", { scaleX: 0 }, { scaleX: 1, duration: 0.7, ease: "power3.inOut" }, 0.1);\n'
    for rid, t in (("#ev-r1", n36), ("#ev-r2", n1)):
        s += f'    tl.fromTo("{rid} .lab", {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "expo.out" }}, {r(t-0.35)});\n'
        s += f'    tl.fromTo("{rid} .num", {{ opacity: 0, yPercent: 60, filter: "blur(10px)" }}, {{ opacity: 1, yPercent: 0, filter: "blur(0px)", duration: 0.45, ease: "expo.out" }}, {r(t-0.04)});\n'
    s += f'    tl.fromTo("#ev-div", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.6, ease: "power3.inOut" }}, {r(ang)});\n'
    s += f'    tl.fromTo("#ev-r3 .lab", {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "expo.out" }}, {r(ang+0.2)});\n'
    s += f'    tl.fromTo("#ev-r3 .num", {{ opacity: 0, scale: 1.3, filter: "blur(10px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.4, ease: "expo.out", transformOrigin: "100% 60%" }}, {r(n46-0.03)});\n'
    s += f'    tl.fromTo("#ev-sweep", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.45, ease: "power3.out" }}, {r(n46+0.15)});\n'
    s += f'    tl.fromTo("#ev-src", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5, ease: "power2.out" }}, {r(n36+0.6)});\n'
    s += exit_blur("#ev-card", r(end-0.05), 0.3)
    s += f'    tl.to("#ev-dim", {{ opacity: 0, duration: 0.4, ease: "power2.in" }}, {r(end)});\n'
    return scene("evidence", body, s, css)


# ---------------------------------------------------------------------------------
# ARGUMENT 33.76 - 60.06 (local)
def build_argument():
    o = 33.76
    masjid = w_at("masjid", 33) - o
    menyat = w_at("menyatukan", 33) - o
    lamb = w_at("lambang") - o
    membina2 = w_at("membina", 46.8) - o
    agama = w_at("agama", 46) - o
    pers = w_at("persaudaraan") - o
    kek = w_at("kekuatan") - o
    end = 59.95 - o
    t_k = 36.7 - o
    body = f"""    <div id="ar-dim" class="dim clip" data-start="{r(t_k-0.1)}" data-duration="{r(end-t_k+0.5)}" data-track-index="0"></div>
    <div id="ar-head" class="clip" data-start="{r(t_k)}" data-duration="{r(end-t_k+0.4)}" data-track-index="1"
         style="position:absolute;left:108px;top:214px;width:864px;">
      <div class="kicker" id="ar-k">POINT 03 · TELADAN HIJRAH NABI SAW</div>
      <div id="ar-gl" class="gline" style="width:760px;margin:12px 0 0;"></div>
    </div>
    <div id="ar-c1" class="clip card" data-start="{r(masjid-0.3)}" data-duration="{r(menyat-masjid+0.1)}" data-track-index="2">
      <div class="num">01</div><div><div class="hl t">MEMBINA MASJID</div><div class="sub">Perkara awal yang dibuat Nabi SAW</div></div>
    </div>
    <div id="ar-c2" class="clip card" data-start="{r(menyat-0.2)}" data-duration="{r(4.6)}" data-track-index="3">
      <div class="num">02</div><div><div class="hl t">MENYATUKAN UMAT</div><div class="sub">Umat Islam di Madinah Al-Munawarah</div></div>
    </div>
    <div id="ar-c3" class="clip card" data-start="{r(membina2-0.1)}" data-duration="{r(agama-membina2+1.6)}" data-track-index="4">
      <div class="num">01</div><div><div class="hl t">MASJID</div><div class="sub" id="ar-c3s">Lambang menegakkan agama</div></div>
    </div>
    <div id="ar-c4" class="clip card" data-start="{r(pers-0.3)}" data-duration="{r(end-pers+0.3)}" data-track-index="5">
      <div class="num">02</div><div><div class="hl t">PERSAUDARAAN</div>
      <div class="sub" style="font-size:38px;font-weight:700;">Asas <span id="ar-kek" style="position:relative;display:inline-block;"><span id="ar-sw"></span><span style="position:relative;">kekuatan</span></span> mana-mana negara</div></div>
    </div>"""
    css = CARD_CSS + """
      .card { position: absolute; left: 108px; top: 312px; width: 864px; display: flex; gap: 30px; align-items: center; }
      .card .num { font-family: "Anton", sans-serif; font-size: 150px; line-height: 1; color: var(--gold-bright); min-width: 150px; }
      .card .t { font-size: 96px; }
      #ar-sw { position: absolute; left: -8px; right: -8px; top: 6px; bottom: 2px; background: var(--gold); transform-origin: 0 50%; opacity: .55; }"""
    s = ""
    s += f'    tl.fromTo("#ar-dim", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: "power2.out" }}, {r(t_k-0.1)});\n'
    s += f'    tl.fromTo("#ar-k", {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "expo.out" }}, {r(t_k)});\n'
    s += f'    tl.fromTo("#ar-gl", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.7, ease: "power3.inOut" }}, {r(t_k+0.05)});\n'
    for cid, t, dur in (("#ar-c1", masjid - 0.3, menyat - masjid + 0.1), ("#ar-c2", menyat - 0.2, 4.6),
                        ("#ar-c3", membina2 - 0.1, agama - membina2 + 1.6), ("#ar-c4", pers - 0.3, end - pers + 0.3)):
        s += f'    tl.fromTo("{cid} .num", {{ opacity: 0, scale: 1.4, filter: "blur(10px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.45, ease: "expo.out" }}, {r(t)});\n'
        s += f'    tl.fromTo("{cid} .t", {{ opacity: 0, clipPath: "inset(0 100% 0 0)" }}, {{ opacity: 1, clipPath: "inset(0 0% 0 0)", duration: 0.55, ease: "power3.out" }}, {r(t+0.08)});\n'
        s += f'    tl.fromTo("{cid} .sub", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "expo.out" }}, {r(t+0.3)});\n'
        s += exit_blur(cid, r(t + dur - 0.26), 0.24)
    s += f'    tl.fromTo("#ar-sw", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.4, ease: "power3.out" }}, {r(kek)});\n'
    s += f'    tl.fromTo("#ar-kek", {{ scale: 1 }}, {{ keyframes: [{{ scale: 1.12, duration: 0.12 }}, {{ scale: 1, duration: 0.13 }}], ease: "power2.out" }}, {r(kek)});\n'
    s += exit_blur("#ar-head", r(end - 0.05), 0.28)
    s += f'    tl.to("#ar-dim", {{ opacity: 0, duration: 0.35, ease: "power2.in" }}, {r(end)});\n'
    return scene("argument", body, s, css)


# ---------------------------------------------------------------------------------
# CLIMAX 60.06 - 70.45 (local)
def build_climax():
    o = 60.06
    ws = [w for w in words if w["clip"] == "e"]
    first6 = ws[:6]  # Bukan hanya untuk menang pilihan raya.
    tunt = w_at("tuntutan") - o
    allah = w_at("Allah", 60) - o
    meny = w_at("menyatukan", 66) - o
    yang = w_at("yang", 68) - o
    end = 70.3 - o
    l1 = "".join(f'<span class="w cl-w1" id="cl-w1-{i}">{html.escape(w["text"].strip(".").upper())}</span> ' for i, w in enumerate(first6))
    body = f"""    <div id="cl-glow" class="clip" data-start="{r(tunt-0.3)}" data-duration="{r(end-tunt+0.6)}" data-track-index="0"
         style="position:absolute;left:-200px;top:-80px;width:1480px;height:1100px;background:radial-gradient(ellipse at 50% 40%, rgba(244,201,93,.35), rgba(217,169,58,.08) 45%, rgba(0,0,0,0) 70%);mix-blend-mode:screen;opacity:0;"></div>
    <div id="cl-dim" class="dim clip" data-start="0" data-duration="{r(end+0.4)}" data-track-index="1"></div>
    <div id="cl-a" class="clip" data-start="0.05" data-duration="{r(tunt-0.4)}" data-track-index="2"
         style="position:absolute;left:108px;top:250px;width:864px;">
      <div class="kicker">POINT 04 · KEMUNCAK</div>
      <div class="hl" style="font-family:'Bebas Neue',sans-serif;font-size:92px;letter-spacing:.03em;margin-top:10px;">{l1}</div>
    </div>
    <div id="cl-b" class="clip" data-start="{r(tunt-0.05)}" data-duration="{r(end-tunt+0.2)}" data-track-index="3"
         style="position:absolute;left:60px;top:226px;width:960px;text-align:center;">
      <div class="hl gold" id="cl-tunt" style="font-size:184px;">TUNTUTAN</div>
      <div class="hl" id="cl-allah" style="font-size:118px;margin-top:-6px;">ALLAH SWT</div>
      <div id="cl-gl" class="gline" style="width:640px;margin:18px auto 14px;transform-origin:50% 50%;background:linear-gradient(90deg,rgba(217,169,58,0),var(--gold-bright),rgba(217,169,58,0));"></div>
      <div class="hl" style="font-family:'Bebas Neue',sans-serif;font-size:70px;letter-spacing:.06em;">
        <span class="w cl-m1">MENYATUKAN</span> <span class="w cl-m1">DUA</span> <span class="w cl-m1">KELOMPOK</span><br>
        <span class="w cl-m2">YANG</span> <span class="w cl-m2">BERTELINGKAH</span> <span class="w cl-m2">PANJANG</span></div>
    </div>"""
    s = ""
    s += '    tl.fromTo("#cl-dim", { opacity: 0 }, { opacity: 0.85, duration: 0.4, ease: "power2.out" }, 0);\n'
    for i, w in enumerate(first6):
        s += (f'    tl.fromTo("#cl-w1-{i}", {{ opacity: 0, filter: "blur(6px)" }}, '
              f'{{ opacity: 1, filter: "blur(0px)", duration: 0.13, ease: "power2.out" }}, {r(max(0.06, w["start"]-o-0.02))});\n')
    s += exit_blur("#cl-a", r(tunt - 0.7), 0.25)
    s += f'    tl.fromTo("#cl-tunt", {{ scale: 1.45, opacity: 0, filter: "blur(14px)" }}, {{ scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.32, ease: "expo.out" }}, {r(tunt)});\n'
    s += f'    tl.fromTo("#cl-allah", {{ opacity: 0, yPercent: 40, filter: "blur(8px)" }}, {{ opacity: 1, yPercent: 0, filter: "blur(0px)", duration: 0.4, ease: "expo.out" }}, {r(allah-0.02)});\n'
    s += f'    tl.fromTo("#cl-gl", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.6, ease: "power3.inOut" }}, {r(allah+0.2)});\n'
    s += f'    tl.fromTo("#cl-glow", {{ opacity: 0 }}, {{ keyframes: [{{ opacity: 1, duration: 0.18 }}, {{ opacity: 0.45, duration: 1.4 }}], ease: "power2.out" }}, {r(tunt-0.02)});\n'
    s += word_reveal(".cl-m1", meny - 0.02, stagger=0.3, y=20, blur=6)
    s += word_reveal(".cl-m2", yang - 0.02, stagger=0.25, y=20, blur=6)
    s += exit_blur("#cl-b", r(end - 0.12), 0.26)
    s += f'    tl.to("#cl-glow", {{ opacity: 0, duration: 0.4, ease: "power2.in" }}, {r(end-0.2)});\n'
    s += f'    tl.to("#cl-dim", {{ opacity: 0, duration: 0.3, ease: "power2.in" }}, {r(end)});\n'
    return scene("climax", body, s, CARD_CSS, motion_blur=True)


# ---------------------------------------------------------------------------------
# OUTRO 70.45 - 84.5 (local)
def build_outro():
    o = 70.45
    perp = w_at("perpaduan", 73) - o
    demi = w_at("demi") - o
    agama = w_at("agama", 74) - o
    allah = w_at("Allah", 75) - o
    speech_end = 80.71 - o
    fin = speech_end + 0.05
    end = TOTAL - o
    # seeded gold dust (deterministic)
    seed = 7
    dots = []
    for i in range(12):
        seed = (seed * 1103515245 + 12345) % 2**31
        x = 80 + seed % 920
        seed = (seed * 1103515245 + 12345) % 2**31
        y = 500 + seed % 900
        seed = (seed * 1103515245 + 12345) % 2**31
        sz = 3 + seed % 5
        dots.append((x, y, sz))
    dots_html = "\n".join(
        f'      <i class="dust" style="left:{x}px;top:{y}px;width:{s}px;height:{s}px;"></i>' for x, y, s in dots)
    body = f"""    <div id="ou-dim" class="dim clip" data-start="{r(perp-0.3)}" data-duration="{r(fin-perp+0.4)}" data-track-index="0"></div>
    <div id="ou-a" class="clip" data-start="{r(perp-0.15)}" data-duration="{r(speech_end-perp-0.75)}" data-track-index="1"
         style="position:absolute;left:108px;top:236px;width:864px;">
      <div class="kicker">POINT 05 · MESEJ PENUTUP</div>
      <div id="ou-gl" class="gline" style="width:640px;margin:12px 0 20px;"></div>
      <div class="hl gold" style="font-size:124px;"><span class="w ou-w1">PERPADUAN</span></div>
      <div class="hl" style="font-size:96px;"><span class="w ou-w2">DEMI</span> <span class="w ou-w3">AGAMA</span> <span class="w ou-w4">ALLAH</span></div>
    </div>
    <div id="ou-black" class="clip" data-start="{r(speech_end-0.35)}" data-duration="{r(end-speech_end+0.35)}" data-track-index="2"
         style="position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%, #0d1d3f 0%, #050b1a 60%, #000 100%);opacity:0;"></div>
    <div id="ou-dustwrap" class="clip" data-start="{r(fin)}" data-duration="{r(end-fin)}" data-track-index="3" data-layout-ignore
         style="position:absolute;inset:0;">
{dots_html}
    </div>
    <div id="ou-final" class="clip" data-start="{r(fin)}" data-duration="{r(end-fin)}" data-track-index="4"
         style="position:absolute;left:108px;top:560px;width:864px;text-align:center;">
      <div class="kicker" style="font-size:46px;">MESEJ PENUTUP</div>
      <div id="ou-gl2" class="gline" style="width:420px;margin:14px auto 34px;transform-origin:50% 50%;background:linear-gradient(90deg,rgba(217,169,58,0),var(--gold-bright),rgba(217,169,58,0));"></div>
      <div class="hl" style="font-size:112px;"><span class="w ou-f">&ldquo;INI</span> <span class="w ou-f">BUKAN</span> <span class="w ou-f gold">PERPADUAN</span></div>
      <div class="hl" style="font-size:112px;"><span class="w ou-f">UNTUK</span> <span class="w ou-f">POLITIK</span></div>
      <div class="hl gold" style="font-size:112px;"><span class="w ou-f">SEMATA-MATA.&rdquo;</span></div>
      <div id="ou-name" class="sub" style="margin-top:40px;font-size:40px;font-weight:800;color:#fff;" data-var-text="speakerName"></div>
      <div id="ou-role" class="src" style="margin-top:10px;font-size:32px;" data-var-text="speakerRole">Ceramah Perpaduan UMNO&ndash;PAS &middot; PRN Melaka</div>
    </div>
    <div id="ou-fade" class="clip" data-start="{r(end-0.9)}" data-duration="0.9" data-track-index="5"
         style="position:absolute;inset:0;background:#000;opacity:0;"></div>"""
    css = CARD_CSS + """
      #ou-name:empty { display: none; }
      .dust { position: absolute; border-radius: 50%; background: rgba(255,226,140,.9); box-shadow: 0 0 10px 3px rgba(244,201,93,.45); }"""
    s = ""
    s += f'    tl.fromTo("#ou-dim", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: "power2.out" }}, {r(perp-0.3)});\n'
    s += f'    tl.fromTo("#ou-a .kicker", {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "expo.out" }}, {r(perp-0.15)});\n'
    s += f'    tl.fromTo("#ou-gl", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.6, ease: "power3.inOut" }}, {r(perp-0.1)});\n'
    for sel, t in ((".ou-w1", perp), (".ou-w2", demi), (".ou-w3", agama), (".ou-w4", allah)):
        s += f'    tl.fromTo("{sel}", {{ opacity: 0, filter: "blur(8px)", y: 30 }}, {{ opacity: 1, filter: "blur(0px)", y: 0, duration: 0.4, ease: "expo.out" }}, {r(t-0.03)});\n'
    s += exit_blur("#ou-a", r(speech_end - 0.95), 0.28)
    s += f'    tl.to("#ou-dim", {{ opacity: 0, duration: 0.3, ease: "power2.in" }}, {r(speech_end-0.8)});\n'
    s += f'    tl.fromTo("#ou-black", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.7, ease: "power2.inOut" }}, {r(speech_end-0.35)});\n'
    s += f'    tl.fromTo("#ou-gl2", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.8, ease: "power3.inOut" }}, {r(fin+0.1)});\n'
    s += f'    tl.fromTo("#ou-final .kicker", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.7, ease: "expo.out" }}, {r(fin)});\n'
    s += word_reveal(".ou-f", fin + 0.35, stagger=0.1, y=36, blur=10)
    s += f'    tl.fromTo("#ou-name, #ou-role", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "expo.out", stagger: 0.15 }}, {r(fin+1.4)});\n'
    s += f'    tl.fromTo(".dust", {{ opacity: 0, y: 0 }}, {{ opacity: 0.8, y: -160, duration: {r(end-fin)}, ease: "none", stagger: 0.06 }}, {r(fin)});\n'
    s += f'    tl.fromTo("#ou-fade", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.85, ease: "power2.in" }}, {r(end-0.9)});\n'
    return scene("outro", body, s, css)


# ---------------------------------------------------------------------------------
# CAPTIONS 0 - TOTAL
KEYWORDS = {"rakyat", "persepsi", "perpaduan", "umno", "pas", "3.6", "1", "4.6", "juta", "masjid", "persaudaraan",
            "kekuatan", "tuntutan", "allah", "agama", "islam", "terbesar", "menyatukan"}


def caption_groups():
    groups, cur = [], []
    for i, w in enumerate(words):
        if cur:
            prev = cur[-1]
            gap = w["start"] - prev["end"]
            if (prev["text"][-1] in ".?!," or gap >= 0.35 or len(cur) >= 4 or w["clip"] != prev["clip"]
                    or (len(cur) >= 3 and gap >= 0.15)):
                groups.append(cur)
                cur = []
        cur.append(w)
    if cur:
        groups.append(cur)
    return groups


def build_captions():
    groups = caption_groups()
    body, s = [], []
    for gi, g in enumerate(groups):
        g0 = max(0.12, g[0]["start"] - 0.06)
        nxt = groups[gi + 1][0]["start"] - 0.06 if gi + 1 < len(groups) else g[-1]["end"] + 0.6
        clip_end = next(c[1] + c[2] for c in CLIPS if c[0] == g[0]["clip"])
        g1 = min(nxt, max(g[-1]["end"] + 0.45, g0 + 0.6), clip_end - 0.02)
        spans = []
        for w in g:
            key = w["text"].strip(".,?!").lower() in KEYWORDS
            spans.append(f'<span class="cw{" kw" if key else ""}" id="cap-{w["id"]}">{html.escape(w["text"])}</span>')
        body.append(f'    <div class="cg" id="cg-{gi}"><div class="cbox">{" ".join(spans)}</div></div>')
        s.append(f'    tl.set("#cg-{gi}", {{ opacity: 1, visibility: "visible" }}, {r(g0)});')
        for w in g:
            key = w["text"].strip(".,?!").lower() in KEYWORDS
            ws = r(max(g0, w["start"] - 0.03))
            sel = f'#cap-{w["id"]}'
            s.append(f'    tl.fromTo("{sel}", {{ opacity: 0, scale: 0.95 }}, {{ opacity: 1, scale: 1, duration: 0.15, ease: "power2.out" }}, {ws});')
            if key:
                s.append(f'    tl.to("{sel}", {{ keyframes: [{{ scale: 1.12, duration: 0.11 }}, {{ scale: 1, duration: 0.14 }}], ease: "power2.out" }}, {r(ws+0.02)});')
                s.append(f'    tl.set("{sel}", {{ color: "#f4c95d" }}, {ws});')
            else:
                s.append(f'    tl.set("{sel}", {{ color: "#ffd84a" }}, {ws});')
                s.append(f'    tl.set("{sel}", {{ color: "#ffffff" }}, {r(min(g1-0.01, max(w["end"], w["start"]+0.12)))});')
        s.append(f'    tl.to("#cg-{gi}", {{ opacity: 0, duration: 0.1, ease: "power2.in" }}, {r(g1-0.1)});')
        s.append(f'    tl.set("#cg-{gi}", {{ opacity: 0, visibility: "hidden" }}, {r(g1)});')
    css = """
      #cap-wrap { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
      .cg { position: absolute; left: 0; right: 0; bottom: 618px; text-align: center; opacity: 0; visibility: hidden; }
      .cbox { display: inline-block; max-width: 900px; padding: 10px 26px 14px; border-radius: 18px; background: rgba(5,11,26,.38);
        font-family: "Montserrat", sans-serif; font-weight: 800; font-size: 70px; line-height: 1.18; color: #fff;
        -webkit-text-stroke: 9px #000; paint-order: stroke fill; text-shadow: 0 4px 18px rgba(0,0,0,.6); }
      .cw { display: inline-block; transform-origin: 50% 70%; }"""
    body_html = '    <div id="cap-wrap" class="clip" data-start="0" data-duration="%s" data-track-index="0">\n%s\n    </div>' % (TOTAL, "\n".join(body))
    script = "\n".join(s) + "\n"
    return scene("captions", body_html, script, css), groups


# ---------------------------------------------------------------------------------
# FX 0 - TOTAL: legibility gradients, broadcast bug, cut dips and light sweeps
def build_fx():
    sweeps = "\n".join(
        f'    <div id="fx-sw-{i}" class="clip sweep" data-start="{r(t-0.35)}" data-duration="0.9" data-track-index="{3+i}" data-layout-ignore></div>'
        for i, t in enumerate(CUTS))
    dips = "\n".join(
        f'    <div id="fx-dip-{i}" class="clip dip" data-start="{r(t-0.12)}" data-duration="0.42" data-track-index="{10+i}" data-layout-ignore></div>'
        for i, t in enumerate(CUTS))
    body = f"""    <div id="fx-bug" class="clip" data-start="0.4" data-duration="{r(80.3-0.4)}" data-track-index="2"
         style="position:absolute;left:108px;top:178px;">
      <span id="fx-bug-bar" style="display:inline-block;width:8px;height:30px;background:var(--gold-bright);vertical-align:-4px;margin-right:12px;"></span><span id="fx-bug-t" style="font-family:'Bebas Neue',sans-serif;font-size:34px;letter-spacing:.2em;color:rgba(255,255,255,.92);">PRN MELAKA <span style="color:var(--gold-bright);">&middot;</span> CERAMAH PERPADUAN</span>
    </div>
{sweeps}
{dips}"""
    css = """
      .sweep { position: absolute; left: -700px; top: -200px; width: 600px; height: 2400px; transform-origin: 50% 50%;
        background: linear-gradient(90deg, rgba(255,232,170,0), rgba(255,232,170,.38) 45%, rgba(255,255,255,.55) 50%, rgba(255,232,170,.38) 55%, rgba(255,232,170,0));
        mix-blend-mode: screen; opacity: 0; }
      .dip { position: absolute; inset: 0; background: #000; opacity: 0; }"""
    s = ""
    s += '    tl.fromTo("#fx-bug-bar", { scaleY: 0 }, { scaleY: 1, duration: 0.4, ease: "expo.out" }, 0.4);\n'
    s += '    tl.fromTo("#fx-bug-t", { opacity: 0, x: -20 }, { opacity: 1, x: 0, duration: 0.5, ease: "expo.out" }, 0.5);\n'
    s += f'    tl.to("#fx-bug", {{ opacity: 0, duration: 0.3, ease: "power2.in" }}, {r(80.0)});\n'
    for i, t in enumerate(CUTS):
        s += (f'    tl.fromTo("#fx-sw-{i}", {{ x: 0, rotation: 18, opacity: 0.0 }}, '
              f'{{ x: 2500, rotation: 18, opacity: 1, duration: 0.85, ease: "power2.inOut" }}, {r(t-0.35)});\n')
        s += (f'    tl.fromTo("#fx-dip-{i}", {{ opacity: 0 }}, {{ keyframes: [{{ opacity: 0.45, duration: 0.1 }}, '
              f'{{ opacity: 0, duration: 0.3 }}], ease: "power2.out" }}, {r(t-0.12)});\n')
    return scene("fx", body, s, css)



def build_shade():
    body = f"""    <div id="sh-top" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="0" data-layout-ignore
         style="position:absolute;left:0;top:0;width:1080px;height:520px;background:linear-gradient(180deg,rgba(5,11,26,.78),rgba(5,11,26,.35) 55%,rgba(5,11,26,0));"></div>
    <div id="sh-bot" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="1" data-layout-ignore
         style="position:absolute;left:0;bottom:0;width:1080px;height:900px;background:linear-gradient(0deg,rgba(0,0,0,.82),rgba(5,11,26,.45) 45%,rgba(5,11,26,0));"></div>"""
    return scene("shade", body, "    tl.set({}, {}, 0);\n")


# ---------------------------------------------------------------------------------
def build_index(groups):
    vids, cam_js = [], []
    for i, (cid, st, du, si, so) in enumerate(CLIPS):
        vids.append(f"""      <div class="cam" id="cam-{cid}">
        <video id="clip-{cid}" class="clip" src="assets/footage/clip-{cid}.mp4" data-start="{st}" data-duration="{du}"
               data-track-index="{1 + (i % 2)}" data-has-audio="true" data-volume="1" playsinline
               data-color-grading='{{"preset":"deep-contrast","intensity":0.45,"adjust":{{"exposure":0.06,"highlights":-0.3,"shadows":0.14,"temperature":-0.08,"saturation":-0.05,"blacks":-0.03}},"details":{{"vignette":0.36,"vignetteFeather":0.7,"grain":0.12,"grainSize":0.3}}}}'></video>
      </div>""")
        keys = camera[cid]["keys"]
        cam_js.append(f'      tl.set("#cam-{cid}", {{ x: {keys[0][1]}, y: {keys[0][2]}, scale: {keys[0][3]} }}, 0);')
        for k0, k1 in zip(keys, keys[1:]):
            cam_js.append(f'      tl.to("#cam-{cid}", {{ x: {k1[1]}, y: {k1[2]}, scale: {k1[3]}, duration: {r(k1[0]-k0[0])}, ease: "none" }}, {r(st + k0[0])});')

    # music ducking from caption words
    audio = []
    if music:
        pts = music["automation"]
        auto = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": pts}]}).replace('"', "&quot;")
        audio.append(f'      <audio id="score" src="{music["src"]}" data-start="0" data-duration="{TOTAL}" data-track-index="9" '
                     f'data-volume="1" data-fade-in="0.05" data-fade-out="2.2" data-automation="{auto}"></audio>')
    sfx = [  # id, file, peak offset in file, hit time, volume, duration
        ("sfx-open", "impact-bass-1", 0.073, 0.08, 0.55, 2.0),
        ("sfx-rakyat", "impact-bass-1", 0.073, w_at("rakyat") + 0.03, 0.32, 1.8),
        ("sfx-cut1", "whoosh-cinematic", 2.503, CUTS[0] + 0.03, 0.30, 3.2),
        ("sfx-kp1", "impact-bass-1", 0.073, w_at("perpaduan", 6.3) + 0.03, 0.30, 1.8),
        ("sfx-vs", "whoosh", 0.162, w_at("UMNO") + 0.1, 0.22, 0.5),
        ("sfx-46", "impact-bass-1", 0.073, w_at("4.6") + 0.06, 0.36, 1.8),
        ("sfx-cut2", "whoosh-short", 0.162, CUTS[1] + 0.03, 0.22, 0.5),
        ("sfx-cut3", "whoosh", 0.162, CUTS[2] + 0.03, 0.20, 0.5),
        ("sfx-kp3", "impact-bass-1", 0.073, w_at("persaudaraan") + 0.03, 0.28, 1.8),
        ("sfx-cut4", "whoosh-cinematic", 2.503, CUTS[3] + 0.03, 0.26, 3.0),
        ("sfx-rise", "riser", 3.472, w_at("tuntutan") - 0.02, 0.18, 3.8),
        ("sfx-tunt", "impact-bass-1", 0.073, w_at("tuntutan") + 0.03, 0.38, 2.0),
        ("sfx-cut5", "whoosh-short", 0.162, CUTS[4] + 0.03, 0.2, 0.5),
        ("sfx-end", "impact-bass-1", 0.073, 80.8, 0.45, 2.0),
    ]
    for i, (sid, f, peak, hit, vol, dur) in enumerate(sfx):
        st = max(0.0, hit - peak)
        media_start = max(0.0, peak - hit) if hit < peak else 0.0
        ms = f' data-media-start="{r(media_start)}"' if media_start > 0 else ""
        audio.append(f'      <audio id="{sid}" src="assets/sfx/{f}.mp3" data-start="{r(st)}" data-duration="{r(dur)}"{ms} '
                     f'data-track-index="{11 + (i % 3)}" data-volume="{vol}" data-fade-out="0.25"></audio>')

    hosts = [("shade", 0, TOTAL, 20), ("fx", 0, TOTAL, 38), ("hook", 0, 7.3, 30), ("issue", 6.34, 12.2, 31), ("evidence", 21.3, 15.5, 32),
             ("argument", 33.76, 26.3, 33), ("climax", 60.06, 10.39, 34), ("outro", 70.45, TOTAL - 70.45, 35),
             ("captions", 0, TOTAL, 40)]
    host_html = []
    for i, (hid, st, du, z) in enumerate(hosts):
        kind = "captions" if hid == "captions" else "graphics"
        host_html.append(f'      <div id="{hid}" class="clip host" data-composition-id="{hid}" data-composition-src="compositions/{hid}.html" '
                         f'data-start="{r(st)}" data-duration="{r(du)}" data-track-index="{20+i}" data-track-kind="{kind}" '
                         f'data-width="{W}" data-height="{H}" style="z-index:{z};"></div>')
    return f"""<!doctype html>
<html lang="ms">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      :root {{ --navy: #0a1630; --gold: #d9a93a; --gold-bright: #f4c95d; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
      .cam {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; transform-origin: 0 0; z-index: 1; }}
      .cam video {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
      .host {{ position: absolute; inset: 0; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}">
{chr(10).join(vids)}
{chr(10).join(host_html)}
{chr(10).join(audio)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      // Digital camera: smoothed speaker tracking + per-scene push-in / pull-back (data/camera.json)
{chr(10).join(cam_js)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""


def main():
    os.makedirs(os.path.join(ROOT, "compositions"), exist_ok=True)
    files = {
        "hook": build_hook(), "issue": build_issue(), "evidence": build_evidence(), "argument": build_argument(),
        "climax": build_climax(), "outro": build_outro(), "fx": build_fx(), "shade": build_shade(),
    }
    cap, groups = build_captions()
    files["captions"] = cap
    for k, v in files.items():
        open(os.path.join(ROOT, f"compositions/{k}.html"), "w").write(v)
    open(os.path.join(ROOT, "index.html"), "w").write(build_index(groups))
    print("wrote", len(files), "scenes,", len(groups), "caption groups")


if __name__ == "__main__":
    main()
