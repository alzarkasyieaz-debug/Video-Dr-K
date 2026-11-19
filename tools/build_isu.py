#!/usr/bin/env python3
"""Generate the four per-issue HyperFrames projects cut from clip C (Seri Iskandar).

    python3 tools/build_isu.py            # writes ep3-seri-iskandar/isu*/index.html + compositions/*.html
    python3 tools/build_captions_isu.py <isu>   # captions (separate script)

Every on-screen fact is a phrase from the speech; times are output seconds
derived from the cut lists (same lists as tools/build_captions_isu.py).
Style matches episodes 1–3: "UCAPAN DI DEWAN RAKYAT" bug, "RAKAMAN ASAL" panel,
GRAFIK / ILUSTRASI tags, navy + gold, Inter.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP3 = os.path.join(ROOT, "ep3-seri-iskandar")
FOOT = "assets/footage/dewan-seri-iskandar.mp4"

# ---------------------------------------------------------------- shared CSS
SCENE_CSS = """
    #root { position: absolute; inset: 0; font-family: Inter, sans-serif; }
    .ill { position: absolute; padding: 4px 10px; border-radius: 5px; font-weight: 800; font-size: 28px; letter-spacing: .16em;
      color: #c9d2e0; border: 1px solid rgba(201,210,224,.5); background: rgba(7,17,31,.6); }
    .zone { position: absolute; left: 60px; top: 846px; width: 960px; height: 300px; }
    .zk { position: absolute; left: 0; top: 0; font-size: 28px; font-weight: 800; letter-spacing: .18em; color: #c9d2e0; }
    .zone .ill { right: 0; top: -2px; }
    .gold3d { color: #f8d77e; text-shadow: 0 1px 0 #e0b04f, 0 2px 0 #d3a344, 0 3px 0 #c4953a, 0 4px 0 #b28430, 0 5px 0 #9c7226,
      0 6px 0 #845f1d, 0 7px 0 #6c4c16, 0 16px 28px rgba(0,0,0,.75); }
    .silver3d { color: #eef1f6; text-shadow: 0 1px 0 #c3cad6, 0 2px 0 #a9b2c0, 0 3px 0 #8e97a6, 0 4px 0 #747d8c, 0 14px 24px rgba(0,0,0,.6); }
    .red3d { color: #ff6a5c; text-shadow: 0 1px 0 #d44c40, 0 2px 0 #b73d33, 0 3px 0 #982f27, 0 4px 0 #7a241d, 0 14px 24px rgba(0,0,0,.6); }
    .chip { position: absolute; left: 44px; top: 262px; padding: 10px 18px; border-radius: 10px; background: rgba(242,197,92,.95);
      color: #17110a; font-weight: 900; font-size: 30px; letter-spacing: .08em; }
    .pill { position: absolute; height: 56px; padding: 0 18px; border-radius: 12px; background: rgba(7,17,31,.92);
      border: 1px solid rgba(231,235,242,.35); color: #f4f6fa; font-size: 28px; font-weight: 900; letter-spacing: .04em; line-height: 56px; white-space: nowrap; }
    .pill.red { border: 2px solid rgba(224,68,58,.85); color: #ff8e83; }
    .pill.gold { background: #f2c55c; color: #17110a; border: none; }
    .stamp { position: absolute; text-align: center; border-radius: 10px; border: 5px solid #ff5a4c; color: #ff6a5c; white-space: nowrap;
      font-weight: 900; letter-spacing: .08em; line-height: 1.1; background: rgba(30,6,6,.85); box-shadow: 0 0 30px rgba(224,68,58,.45); }
    .bd { position: absolute; left: 0; top: 840px; width: 1080px; height: 330px; opacity: 0;
      background: linear-gradient(180deg, rgba(4,8,16,0) 0%, rgba(4,8,16,.74) 20%, rgba(4,8,16,.8) 82%, rgba(4,8,16,0) 100%); }
    .qcard { position: absolute; left: 0; top: 46px; width: 960px; height: 254px; border-radius: 18px; background: rgba(7,17,31,.95);
      border: 2px solid rgba(242,197,92,.8); padding: 22px 30px; }
    .qcard small { display: block; font-size: 28px; font-weight: 900; letter-spacing: .22em; color: #f2c55c; }
    .qcard p { margin-top: 10px; font-size: 36px; font-weight: 800; line-height: 1.2; color: #f4f6fa; }
    .qcard p b { color: #f8d77e; }
    .tile { position: absolute; border-radius: 14px; background: rgba(13,29,51,.94); border: 1px solid rgba(242,197,92,.55);
      padding: 0 16px 0 66px; display: flex; align-items: center; font-size: 28px; font-weight: 900; line-height: 1.12; color: #f4f6fa; }
    .tile em { position: absolute; left: 16px; top: calc(50% - 19px); width: 38px; height: 38px; border-radius: 10px; background: #f2c55c;
      color: #17110a; font-style: normal; font-size: 28px; font-weight: 900; text-align: center; line-height: 38px; }
"""

HOOK_CSS = """
    .h-kick { position: absolute; left: 0; width: 1080px; top: 862px; text-align: center;
      font-size: 28px; font-weight: 800; letter-spacing: .2em; color: #f2c55c; }
    .h-kick span { padding: 8px 18px; border: 1px solid rgba(242,197,92,.6); border-radius: 8px; background: rgba(7,17,31,.7); }
    .h-line { position: absolute; left: 40px; width: 1000px; text-align: center; font-weight: 900; color: #f4f6fa;
      font-size: 44px; white-space: nowrap; text-shadow: 0 4px 0 rgba(0,0,0,.45), 0 10px 30px rgba(0,0,0,.8); }
    .h-3d { position: absolute; left: 20px; width: 1040px; text-align: center; font-weight: 900; line-height: 1; white-space: nowrap;
      letter-spacing: -0.02em; color: #f8d77e;
      text-shadow: 0 1px 0 #e0b04f, 0 2px 0 #d3a344, 0 3px 0 #c4953a, 0 4px 0 #b28430, 0 5px 0 #9c7226,
        0 6px 0 #845f1d, 0 7px 0 #6c4c16, 0 8px 0 #5a3f12, 0 18px 30px rgba(0,0,0,.75), 0 0 60px rgba(242,197,92,.35); }
"""

SLAM = '{ opacity: 0, scale: 1.9, rotationX: -55, transformPerspective: 900 }, { opacity: 1, scale: 1, rotationX: 0, duration: 0.22, ease: "expo.out" }'
POP_L = '{ opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 0.35, ease: "expo.out" }'
RISE = '{ opacity: 0, y: 22, rotationX: -40, transformPerspective: 900 }, { opacity: 1, y: 0, rotationX: 0, duration: 0.38, ease: "expo.out" }'
FADE_IN = '{ opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.4, ease: "expo.out" }'
BLUR_IN = '{ opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.25, ease: "power3.out" }'


def scene(sid, css, body, js):
    return f"""<template>
  <style>{SCENE_CSS}{css}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="1080" data-height="1920">
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
"""


def hook(sid, kick, lines, big, big_size, t_lines, t_big, end):
    """Kicker + first line on screen at frame 0 (thumbnail); big gold line slams on its word."""
    body = [f'    <div class="bd" id="{sid}-bd" style="opacity:1"></div>',
            f'    <div id="{sid}-z">',
            f'      <div class="h-kick" id="{sid}-k"><span>{kick}</span></div>']
    top = 922
    for i, ln in enumerate(lines):
        body.append(f'      <div class="h-line" id="{sid}-l{i}" style="top: {top}px">{ln}</div>')
        top += 70
    body.append(f'      <div class="h-3d" id="{sid}-big" style="top: {top + 10}px; font-size: {big_size}px">{big}</div>')
    body.append('    </div>')
    js = [f'    tl.fromTo(["#{sid}-k", "#{sid}-l0"], {{ opacity: 1 }}, {{ opacity: 1, duration: 0.01 }}, 0);']
    for i, t in enumerate(t_lines[1:], 1):
        js.append(f'    tl.fromTo("#{sid}-l{i}", {BLUR_IN}, {t});')
    js.append(f'    tl.fromTo("#{sid}-big", {SLAM}, {t_big});')
    js.append(f'    tl.to([{", ".join(f"{chr(34)}#{sid}-l{i}{chr(34)}" for i in range(len(lines)))}], {{ opacity: 0.6, duration: 0.3 }}, {t_big});')
    js.append(f'    tl.to(["#{sid}-z", "#{sid}-bd"], {{ opacity: 0, filter: "blur(10px)", duration: 0.16, ease: "power2.in" }}, {end});')
    return scene(sid, HOOK_CSS, "\n".join(body), "\n".join(js))


def ident(sid, topic, lt_out):
    css = """
    #id-topic { position: absolute; left: 44px; top: 262px; padding: 10px 18px; border-radius: 10px;
      background: rgba(242,197,92,.95); color: #17110a; font-weight: 900; font-size: 30px; letter-spacing: .08em; }
    #id-lt { position: absolute; left: 44px; top: 905px; width: 992px; height: 230px; }
    #id-card { position: absolute; left: 0; top: 40px; width: 992px; height: 190px; border-radius: 18px; overflow: hidden;
      background: linear-gradient(100deg, rgba(7,17,31,.94) 0%, rgba(13,29,51,.9) 70%, rgba(13,29,51,.75) 100%);
      border: 1px solid rgba(242,197,92,.35); box-shadow: 0 24px 60px rgba(0,0,0,.6); }
    #id-bar { position: absolute; left: 0; top: 0; width: 12px; height: 190px; background: linear-gradient(180deg, #f8d77e, #b8892c); }
    #id-chip { position: absolute; left: 0; top: 0; padding: 6px 14px; border-radius: 6px; background: #f2c55c; color: #17110a;
      font-weight: 800; font-size: 28px; letter-spacing: .16em; }
    #id-name { position: absolute; left: 40px; top: 24px; width: 930px; font-weight: 900; font-size: 50px; color: #f4f6fa; line-height: 1.05; }
    #id-role { position: absolute; left: 40px; top: 136px; font-weight: 700; font-size: 34px; color: #f2c55c; letter-spacing: .1em; }
    #id-shine { position: absolute; left: -400px; top: -40px; width: 260px; height: 300px;
      background: linear-gradient(90deg, transparent, rgba(255,240,200,.35), transparent); }"""
    body = f"""    <div id="id-topic">{topic}</div>
    <div id="id-lt">
      <div id="id-card">
        <div id="id-bar"></div>
        <div id="id-name">HAJI MUHAMMAD ISMI<br />BIN MAT TAIB</div>
        <div id="id-role">AHLI PARLIMEN PARIT, PERAK</div>
        <div id="id-shine"></div>
      </div>
      <div id="id-chip">DEWAN RAKYAT MALAYSIA</div>
    </div>"""
    js = f"""    tl.fromTo("#id-card", {{ clipPath: "inset(0 100% 0 0 round 18px)" }}, {{ clipPath: "inset(0 0% 0 0 round 18px)", duration: 0.6, ease: "power3.inOut" }}, 0.4);
    tl.fromTo("#id-chip", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, 0.8);
    tl.fromTo("#id-name", {{ opacity: 0, x: -30, filter: "blur(8px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.45, ease: "expo.out" }}, 0.7);
    tl.fromTo("#id-role", {BLUR_IN}, 0.95);
    tl.fromTo("#id-shine", {{ x: 0, rotation: 18 }}, {{ x: 1700, rotation: 18, duration: 1.0, ease: "power2.inOut" }}, 1.3);
    tl.fromTo("#id-topic", {POP_L}, 1.2);
    tl.to("#id-lt", {{ opacity: 0, y: 20, duration: 0.3, ease: "power2.in" }}, {lt_out});
    tl.to("#id-topic", {{ opacity: 0, duration: 0.25, ease: "power2.in" }}, {lt_out + 0.05});"""
    return scene(sid, css, body, js)


def outro(sid, kicker, title, img):
    css = """
    #root { background: #07111f; }
    #o-still { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; opacity: .32; }
    #o-shade { position: absolute; inset: 0; background: radial-gradient(800px 900px at 50% 48%, rgba(7,17,31,.35), rgba(7,17,31,.95) 80%); }
    #o-box { position: absolute; left: 70px; top: 610px; width: 940px; height: 700px; text-align: center; }
    #o-rule { position: absolute; left: 370px; top: 0; width: 200px; height: 4px; background: #f2c55c; }
    #o-k { position: absolute; left: 0; top: 34px; width: 940px; font-size: 28px; font-weight: 800; letter-spacing: .22em; color: #c9d2e0; }
    #o-t { position: absolute; left: 0; top: 86px; width: 940px; font-size: 84px; font-weight: 900; line-height: 1.04; color: #f8d77e;
      text-shadow: 0 1px 0 #e0b04f, 0 2px 0 #d3a344, 0 3px 0 #c4953a, 0 4px 0 #b28430, 0 5px 0 #9c7226, 0 6px 0 #845f1d, 0 7px 0 #6c4c16, 0 20px 34px rgba(0,0,0,.8); }
    #o-n { position: absolute; left: 0; top: 330px; width: 940px; font-size: 44px; font-weight: 900; color: #f4f6fa; }
    #o-r { position: absolute; left: 0; top: 392px; width: 940px; font-size: 32px; font-weight: 800; letter-spacing: .14em; color: #f2c55c; }
    #o-src { position: absolute; left: 60px; top: 500px; width: 820px; font-size: 28px; font-weight: 500; line-height: 1.35; color: rgba(231,235,242,.78); }"""
    body = f"""    <img id="o-still" src="assets/img/{img}" alt="" />
    <div id="o-shade"></div>
    <div id="o-box">
      <div id="o-rule"></div>
      <div id="o-k">{kicker}</div>
      <div id="o-t">{title}</div>
      <div id="o-n">YB Haji Muhammad Ismi bin Mat Taib</div>
      <div id="o-r">AHLI PARLIMEN PARIT, PERAK</div>
      <div id="o-src">Rakaman ucapan sebenar. Grafik ialah ilustrasi.</div>
    </div>"""
    js = f"""    tl.fromTo("#o-still", {{ scale: 1.12 }}, {{ scale: 1.04, duration: 3.5, ease: "power1.out" }}, 0);
    tl.fromTo("#o-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.5, ease: "power3.inOut" }}, 0.15);
    tl.fromTo("#o-k", {FADE_IN}, 0.3);
    tl.fromTo("#o-t", {{ opacity: 0, scale: 1.4, rotationX: -40, transformPerspective: 900 }}, {{ opacity: 1, scale: 1, rotationX: 0, duration: 0.4, ease: "expo.out" }}, 0.4);
    tl.fromTo(["#o-n", "#o-r"], {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "expo.out", stagger: 0.1 }}, 0.8);
    tl.fromTo("#o-src", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 0.6);"""
    return scene(sid, css, body, js)


# ---------------------------------------------------------------- index.html
def index(isu, title, cuts, scenes, sfx, camera, total):
    head = open(os.path.join(EP3, "index.html")).read()
    head = head[: head.index("<body>")].replace("<title>4 Isu Seri Iskandar — Dewan Rakyat</title>", f"<title>{title}</title>")
    vids = []
    for i, (a, b, o) in enumerate(cuts, 1):
        fo = "0.25" if i == len(cuts) else "0.05"
        vids.append(f"""          <video id="v{i}" class="clip" src="{FOOT}" playsinline data-has-audio="true"
            data-start="{o:.2f}" data-duration="{b - a:.2f}" data-media-start="{a:.2f}" data-fade-in="0.04" data-fade-out="{fo}"
            data-volume="1" data-track-index="1"></video>""")
    speech_end = cuts[-1][2] + cuts[-1][1] - cuts[-1][0]
    hosts = []
    for sid, st, du in scenes:
        z = 12 if sid.endswith("outro") else 10
        hosts.append(f"""      <div id="{sid}" class="scene-host" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html"
        data-start="{st}" data-duration="{du}" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index:{z}"></div>""")
    aud = []
    for n, (f, st, vol) in enumerate(sfx):
        dur = {"whoosh": 0.57, "whoosh-short": 0.57, "pop": 0.72, "impact-bass-1": 1.4, "impact-bass-2": 1.4, "riser": 3.98, "whoosh-cinematic": 3.9}[f]
        extra = ""
        if f == "riser":
            extra = ' data-media-start="0.3" data-fade-in="0.6"'
        elif f.startswith("impact"):
            extra = ' data-fade-out="0.7"'
        elif f == "whoosh-cinematic":
            extra = ' data-fade-out="1.0"'
        aud.append(f'      <audio id="sx{n:02d}" class="clip" src="assets/sfx/{f}.mp3" data-start="{st}" data-duration="{dur}"{extra} data-volume="{vol}" data-track-index="{5 + n % 5}"></audio>')
    body = f"""  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920">
      <div id="bg"></div>
      <div id="bg-fins"></div>

      <div id="mask">
        <div id="cam">
          <!-- Original Dewan Rakyat footage (clip C, RTM 1280×720), cropped to 9:16 around the MP; cleaned voice baked in -->
{chr(10).join(vids)}
        </div>
      </div>
      <div id="pframe"><span id="pframe-tag">RAKAMAN ASAL</span></div>
      <div id="grade-vignette"></div>
      <div id="scrim"></div>

      <div id="bug"><i></i>UCAPAN DI DEWAN RAKYAT</div>

{chr(10).join(hosts)}

      <div id="captions" class="scene-host" data-composition-id="captions" data-composition-src="compositions/captions.html"
        data-start="0" data-duration="{speech_end:.2f}" data-track-index="3" data-track-kind="captions" data-width="1080" data-height="1920" style="z-index:15"></div>

      <div id="sweep"></div>
      <div id="flash"></div>

      <!-- Sound design (bundled Pixabay-licensed SFX). Voice stays on the <video> clips. -->
{chr(10).join(aud)}
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});

      const FULL = "inset(0px 0px 0px 0px round 0px)";
      const PANEL = "inset(150px 36px 1100px 36px round 28px)";
      const cam = "#cam", mask = "#mask", pf = "#pframe";
      const BASE = {{ s: 1.12, y: -150 }};   // source is 405×720 upscaled; this keeps the face clear of the lower band

      function splitOn(t) {{
        tl.fromTo(mask, {{ clipPath: FULL }}, {{ clipPath: PANEL, duration: 0.7, ease: "power3.inOut", immediateRender: false }}, t);
        tl.to(cam, {{ y: -230, scale: BASE.s, duration: 0.7, ease: "power3.inOut" }}, t);
        tl.fromTo(pf, {{ opacity: 0, scale: 1.04 }}, {{ opacity: 1, scale: 1, duration: 0.5, ease: "power2.out", immediateRender: false }}, t + 0.35);
        tl.to("#scrim", {{ opacity: 0.35, duration: 0.6, ease: "power2.inOut" }}, t);
      }}
      function splitOff(t, d = 0.6) {{
        tl.to(pf, {{ opacity: 0, duration: 0.2, ease: "power2.in" }}, t);
        tl.fromTo(mask, {{ clipPath: PANEL }}, {{ clipPath: FULL, duration: d, ease: "power3.inOut", immediateRender: false }}, t);
        tl.to(cam, {{ y: BASE.y, duration: d, ease: "power3.inOut" }}, t);
        tl.to("#scrim", {{ opacity: 1, duration: d, ease: "power2.inOut" }}, t);
      }}
      function sweep(t) {{
        tl.fromTo("#sweep", {{ x: 0, rotation: 18, opacity: 0 }}, {{ x: 2300, opacity: 1, duration: 0.9, ease: "power2.inOut", immediateRender: false }}, t);
        tl.set("#sweep", {{ opacity: 0 }}, t + 0.92);
      }}
      function flash(t, o = 0.55) {{
        tl.fromTo("#flash", {{ opacity: 0 }}, {{ opacity: o, duration: 0.06, ease: "power2.out", immediateRender: false }}, t - 0.06);
        tl.to("#flash", {{ opacity: 0, duration: 0.35, ease: "power2.out" }}, t + 0.01);
      }}
      function zoom(t, s, d, ease = "expo.out") {{ tl.to(cam, {{ scale: s, duration: d, ease }}, t); }}
      function cut(t, s, y = BASE.y) {{ tl.set(cam, {{ scale: s, y }}, t); }}   // a new framing on every jump cut
      function shake(t) {{ tl.fromTo(cam, {{ x: 0 }}, {{ x: 8, duration: 0.05, ease: "none", yoyo: true, repeat: 3, immediateRender: false }}, t); }}

      tl.set(cam, {{ scale: 1.42, x: 0, y: -260 }}, 0);
      tl.set(mask, {{ clipPath: FULL }}, 0);
      tl.set("#flash", {{ opacity: 0 }}, 0);
      tl.set("#sweep", {{ opacity: 0, x: 0, rotation: 18 }}, 0);
      tl.set(pf, {{ opacity: 0, scale: 1 }}, 0);

{camera}

      // outro
      tl.to("#bug", {{ opacity: 0, duration: 0.3 }}, {speech_end - 0.2:.2f});
      tl.to("#cam", {{ opacity: 0, duration: 0.5, ease: "power2.in" }}, {speech_end - 0.3:.2f});
      tl.set({{}}, {{}}, {total});

      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    d = os.path.join(EP3, isu)
    open(os.path.join(d, "index.html"), "w").write(head + body)


def write(isu, sid, html):
    open(os.path.join(EP3, isu, "compositions", sid + ".html"), "w").write(html)


# ================================================================= ISU 1 — PASAR AWAM
def isu1():
    isu = "isu1-pasar"
    cuts = [(67.45, 70.85, 0.00), (46.95, 57.82, 3.40), (61.40, 67.10, 14.27), (71.95, 87.20, 19.97),
            (89.15, 101.75, 35.22), (103.10, 114.50, 47.82), (115.30, 120.45, 59.22), (159.72, 169.72, 64.37)]
    write(isu, "p1-hook", hook("p1-hook", "SERI ISKANDAR, PARIT · DEWAN RAKYAT",
                               ["“MALANGNYA, DI SERI ISKANDAR INI", "MASIH LAGI TIDAK ADA"], "PASAR AWAM.”", 124,
                               [0, 1.3], 2.5, 3.22))
    write(isu, "p2-id", ident("p2-id", "ISU 1 · PASAR AWAM", 5.65))
    # p3: the town (abs 9.4–19.97) — split from 9.4
    T = 9.4
    items = [("UTP", 53.9 - 43.55), ("UiTM", 54.5 - 43.55), ("KOLEJ PROFESIONAL MARA", 55.1 - 43.55), ("IKBN", 57.3 - 43.55),
             ("SEKOLAH-SEKOLAH", 61.44 - 47.13), ("KILANG-KILANG", 63.6 - 47.13), ("PEJABAT KERAJAAN", 65.0 - 47.13)]
    pos = [(0, 52), (130, 52), (290, 52), (750, 52), (0, 124), (330, 124), (610, 124)]
    body = ['    <div class="zone" id="b-zone">', '      <div class="zk" id="b-k">SERI ISKANDAR · PESAT MEMBANGUN</div>',
            '      <div class="ill">GRAFIK</div>']
    js = [f'    tl.fromTo(["#b-k", "#b-zone .ill"], {FADE_IN}, 0.45);']
    for n, ((name, t), (x, y)) in enumerate(zip(items, pos)):
        cls = "pill gold" if n < 4 else "pill"
        body.append(f'      <div class="{cls}" id="b-i{n}" style="left: {x}px; top: {y}px">{name}</div>')
        js.append(f'    tl.fromTo("#b-i{n}", {{ opacity: 0, y: 16, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "back.out(1.8)" }}, {t - T:.2f});')
    body.append('      <div id="b-note">PUSAT PENTADBIRAN DAERAH PERAK TENGAH · BANDAR ILMU</div>')
    body.append('    </div>')
    js.append(f'    tl.fromTo("#b-note", {FADE_IN}, 1.0);')
    js.append('    tl.to("#b-zone", { opacity: 0, filter: "blur(8px)", duration: 0.25, ease: "power2.in" }, 10.32);')
    css = "\n    #b-note { position: absolute; left: 0; top: 214px; width: 960px; font-size: 30px; font-weight: 800; letter-spacing: .06em; color: #f2c55c; }"
    write(isu, "p3-bandar", scene("p3-bandar", css, "\n".join(body), "\n".join(js)))
    # p4: population (abs 19.97–35.22), split continues; local = src - 71.95
    css = """
    .p-row { position: absolute; left: 0; width: 960px; height: 100px; }
    .p-row b { position: absolute; left: 0; top: 4px; font-size: 28px; font-weight: 800; letter-spacing: .14em; color: #c9d2e0; }
    .p-row span { position: absolute; left: 0; top: 38px; font-size: 64px; font-weight: 900; line-height: 1; }
    .p-track { position: absolute; left: 330px; top: 48px; width: 630px; height: 42px; border-radius: 10px; background: rgba(231,235,242,.08); }
    .p-bar { position: absolute; left: 0; top: 0; height: 42px; border-radius: 10px; transform-origin: 0 50%; }
    #p-r1 { top: 50px; } #p-r2 { top: 160px; }
    #p-b1 { width: 267px; background: linear-gradient(180deg, #e8ecf3, #9aa3b2); }
    #p-b2 { width: 630px; background: linear-gradient(180deg, #ffe08f, #d9a641 60%, #a8781f); box-shadow: 0 0 26px rgba(242,197,92,.4); }
    #p-stamp { left: 130px; top: 960px; width: 820px; padding: 14px 0; font-size: 50px; }"""
    body = """    <div class="zone" id="p-zone">
      <div class="zk" id="p-k">PENDUDUK SERI ISKANDAR</div>
      <div class="ill">GRAFIK</div>
      <div class="p-row" id="p-r1"><b>BANCI 2020</b><span class="silver3d">14,827</span><div class="p-track"><div class="p-bar" id="p-b1"></div></div></div>
      <div class="p-row" id="p-r2"><b>TERKINI · LEBIH</b><span class="gold3d">35,000</span><div class="p-track"><div class="p-bar" id="p-b2"></div></div></div>
    </div>
    <div class="stamp" id="p-stamp">MASIH TIADA PASAR AWAM</div>"""
    js = f"""    tl.fromTo(["#p-k", "#p-zone .ill"], {FADE_IN}, 0.1);
    tl.fromTo("#p-r1", {POP_L}, 2.9);
    tl.fromTo("#p-b1", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.8, ease: "power3.out" }}, 3.0);
    tl.fromTo("#p-r2", {POP_L}, 9.1);
    tl.fromTo("#p-b2", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 1.0, ease: "power3.out" }}, 9.6);
    tl.set("#p-stamp", {{ opacity: 0, rotation: -5 }}, 0);
    tl.to(["#p-r1", "#p-r2"], {{ opacity: 0, duration: 0.2 }}, 13.45);
    tl.fromTo("#p-stamp", {{ opacity: 0, scale: 2.0, rotation: -14 }}, {{ opacity: 1, scale: 1, rotation: -5, duration: 0.2, ease: "power4.out", immediateRender: false }}, 13.55);
    tl.to(["#p-zone", "#p-stamp"], {{ opacity: 0, filter: "blur(8px)", duration: 0.25, ease: "power2.in" }}, 14.95);"""
    write(isu, "p4-penduduk", scene("p4-penduduk", css, body, js))
    # p5: shops (abs 35.22–47.82, full frame)
    css = "\n    .col { position: absolute; left: 44px; top: 860px; width: 600px; height: 290px; }"
    body = """    <div class="col" id="k-col">
      <div class="pill gold" id="k-p1" style="top: 0">KEPERLUAN RUMAH</div>
      <div class="pill" id="k-p2" style="top: 70px">IKAN</div>
      <div class="pill" id="k-p3" style="top: 70px; left: 130px">SAYUR</div>
      <div class="pill" id="k-p4" style="top: 140px">KEDAI-KEDAI BERSELERAK</div>
      <div class="pill red" id="k-p5" style="top: 210px">PENCEMARAN</div>
    </div>"""
    js = "\n".join(f'    tl.fromTo("#{p}", {POP_L}, {t});' for p, t in [("k-p1", 3.15), ("k-p2", 4.45), ("k-p3", 5.05), ("k-p4", 6.95)])
    js += f'\n    tl.fromTo("#k-p5", {{ opacity: 0, scale: 1.3 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, 10.65);'
    js += '\n    tl.to("#k-col", { opacity: 0, x: -30, duration: 0.3, ease: "power2.in" }, 12.3);'
    write(isu, "p5-kedai", scene("p5-kedai", css, body, js))
    # p6: the market that is needed + question 1 (abs 47.82–64.37); split from 47.7
    css = """
    .a-tile { position: absolute; top: 50px; width: 225px; height: 96px; border-radius: 14px; background: rgba(13,29,51,.92);
      border: 1px solid rgba(242,197,92,.55); text-align: center; }
    .a-tile i { display: block; margin: 12px auto 0; width: 34px; height: 34px; border-radius: 50%; background: #f2c55c;
      color: #17110a; font-style: normal; font-weight: 900; font-size: 26px; line-height: 34px; }
    .a-tile b { display: block; margin-top: 6px; font-size: 30px; font-weight: 900; letter-spacing: .08em; color: #f4f6fa; }"""
    body = """    <div class="zone" id="a-zone">
      <div class="zk" id="a-k">PASAR AWAM YANG DIPERLUKAN</div>
      <div class="ill">GRAFIK</div>
      <div class="a-tile" id="a-t1" style="left: 0"><i>✓</i><b>SELESA</b></div>
      <div class="a-tile" id="a-t2" style="left: 245px"><i>✓</i><b>BERSIH</b></div>
      <div class="a-tile" id="a-t3" style="left: 490px"><i>✓</i><b>TERATUR</b></div>
      <div class="a-tile" id="a-t4" style="left: 735px"><i>✓</i><b>MODEN</b></div>
      <div class="pill gold" id="a-b1" style="left: 0; top: 170px">TAPAK SAH UNTUK PENIAGA KECIL</div>
      <div class="pill" id="a-b2" style="left: 0; top: 238px">BEKALAN SEGAR · HARGA BERPATUTAN</div>
      <div class="qcard" id="a-q"><small>SOALAN</small><p>Adakah kementerian bersedia <b>meluluskan pembinaan pasar awam</b> di Seri Iskandar?</p></div>
    </div>"""
    js = [f'    tl.fromTo(["#a-k", "#a-zone .ill"], {FADE_IN}, 0.3);']
    js += [f'    tl.fromTo("#{t}", {RISE}, {at});' for t, at in [("a-t1", 2.0), ("a-t2", 2.6), ("a-t3", 3.2), ("a-t4", 3.9)]]
    js += [f'    tl.fromTo("#a-b1", {POP_L}, 4.9);', f'    tl.fromTo("#a-b2", {POP_L}, 7.7);',
           '    tl.set("#a-q", { opacity: 0 }, 0);',
           '    tl.to([".a-tile", "#a-b1", "#a-b2"], { opacity: 0, duration: 0.2 }, 11.3);',
           '    tl.fromTo("#a-q", { opacity: 0, scale: 1.06 }, { opacity: 1, scale: 1, duration: 0.35, ease: "expo.out", immediateRender: false }, 11.4);',
           '    tl.to("#a-zone", { opacity: 0, filter: "blur(8px)", duration: 0.2, ease: "power2.in" }, 16.35);']
    write(isu, "p6-perlu", scene("p6-perlu", css, body, "\n".join(js)))
    # p7: follow-up question (abs 64.37–74.37), split continues
    body = """    <div class="zone" id="s-zone">
      <div class="zk" id="s-k">SOALAN SUSULAN KEPADA KPKT</div>
      <div class="qcard" id="s-q"><small>SOALAN</small>
        <p id="s-a">Apakah <b>piawaian dan kos purata</b> pembinaan sebuah pasar awam?</p>
        <p id="s-b">Adakah KPKT bersedia membantu <b>kajian kelayakan</b> bagi Seri Iskandar melalui PLANMalaysia?</p>
      </div>
    </div>"""
    css = "\n    #s-q p { font-size: 32px; }"
    js = f"""    tl.fromTo("#s-k", {FADE_IN}, 0.1);
    tl.fromTo("#s-q", {{ opacity: 0, scale: 1.04 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "expo.out" }}, 0.25);
    tl.fromTo("#s-a", {BLUR_IN}, 0.4);
    tl.fromTo("#s-b", {BLUR_IN}, 4.45);
    tl.to("#s-zone", {{ opacity: 0, duration: 0.2 }}, 9.8);"""
    write(isu, "p7-soalan", scene("p7-soalan", css, body, js))
    write(isu, "p8-outro", outro("p8-outro", "ISU 1 · SERI ISKANDAR", "PASAR AWAM<br />SERI ISKANDAR", "end-isu1-pasar.jpg"))
    scenes = [("p1-hook", 0, 3.4), ("p2-id", 3.4, 6.0), ("p3-bandar", 9.4, 10.57), ("p4-penduduk", 19.97, 15.25),
              ("p5-kedai", 35.22, 12.6), ("p6-perlu", 47.82, 16.55), ("p7-soalan", 64.37, 10.0), ("p8-outro", 74.37, 3.5)]
    sfx = [("impact-bass-2", 0, 0.11), ("impact-bass-1", 2.5, 0.09), ("whoosh", 3.2, 0.36), ("pop", 4.0, 0.35),
           ("whoosh-short", 9.25, 0.28), ("pop", 10.35, 0.3), ("pop", 11.55, 0.3), ("pop", 13.75, 0.3), ("pop", 16.47, 0.3),
           ("pop", 22.87, 0.4), ("impact-bass-1", 29.07, 0.09), ("impact-bass-2", 33.5, 0.1), ("whoosh-short", 35.05, 0.26),
           ("pop", 38.37, 0.3), ("pop", 42.17, 0.3), ("pop", 45.87, 0.3), ("whoosh-short", 47.55, 0.28),
           ("pop", 49.82, 0.3), ("pop", 51.72, 0.3), ("riser", 55.3, 0.08), ("impact-bass-2", 59.25, 0.1), ("pop", 64.8, 0.3),
           ("pop", 68.82, 0.3), ("whoosh-cinematic", 71.6, 0.26)]
    camera = """      // 0–3.4 hook
      zoom(0, 1.5, 2.4, "power1.inOut");
      zoom(2.52, 1.62, 0.16); shake(2.52);
      // 3.4 cut → identity + the town
      flash(3.4); cut(3.4, BASE.s); zoom(3.4, 1.17, 5.6, "power1.inOut"); sweep(4.0);
      splitOn(9.25);
      cut(14.27, BASE.s, -230);
      cut(19.97, 1.16, -230);
      splitOff(34.95);
      // shops: full frame
      cut(35.22, 1.2); zoom(35.3, 1.26, 12.2, "power1.inOut");
      // what is needed + the questions
      splitOn(47.6);
      cut(59.22, 1.16, -230);
      cut(64.37, BASE.s, -230);
      splitOff(74.0, 0.3);"""
    index(isu, "Isu 1: Pasar Awam Seri Iskandar — Dewan Rakyat", cuts, scenes, sfx, camera, 77.87)


# ================================================================= ISU 2 — JALAN
def isu2():
    isu = "isu2-jalan"
    cuts = [(213.10, 219.10, 0.00), (187.90, 213.00, 6.00), (221.42, 253.45, 31.10), (254.98, 262.82, 63.13)]
    # hook with the three agencies
    css = HOOK_CSS + """
    .h-pill { position: absolute; top: 1086px; height: 76px; border-radius: 14px; background: rgba(7,17,31,.92); border: 2px solid rgba(231,235,242,.5);
      text-align: center; font-size: 36px; font-weight: 900; color: #f4f6fa; line-height: 72px; }
    .h-pill i { font-style: normal; color: #f2c55c; margin-left: 10px; }"""
    body = """    <div class="bd" id="j1-bd" style="opacity:1"></div>
    <div id="j1-z">
      <div class="h-kick" id="j1-k"><span>SERI ISKANDAR, PARIT · DEWAN RAKYAT</span></div>
      <div class="h-line" id="j1-l0" style="top: 916px">“SEBENARNYA RAKYAT TIDAK TAHU</div>
      <div class="h-3d" id="j1-big" style="top: 984px; font-size: 74px">DI MANA NAK MENGADU?</div>
      <div class="h-pill" id="j1-p1" style="left: 60px; width: 230px">PBT<i>?</i></div>
      <div class="h-pill" id="j1-p2" style="left: 310px; width: 230px">JKR<i>?</i></div>
      <div class="h-pill" id="j1-p3" style="left: 560px; width: 460px">KERAJAAN NEGERI<i>?</i></div>
    </div>"""
    js = f"""    tl.fromTo(["#j1-k", "#j1-l0"], {{ opacity: 1 }}, {{ opacity: 1, duration: 0.01 }}, 0);
    tl.fromTo("#j1-big", {SLAM}, 2.0);
    tl.fromTo("#j1-p1", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "back.out(1.8)" }}, 3.4);
    tl.fromTo("#j1-p2", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "back.out(1.8)" }}, 3.8);
    tl.fromTo("#j1-p3", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "back.out(1.8)" }}, 4.7);
    tl.to(["#j1-z", "#j1-bd"], {{ opacity: 0, filter: "blur(10px)", duration: 0.16, ease: "power2.in" }}, 5.82);"""
    write(isu, "j1-hook", scene("j1-hook", css, body, js))
    write(isu, "j2-id", ident("j2-id", "ISU 2 · JALAN BERLUBANG", 5.65))
    # j3: potholes (abs 12.0–31.1), split from 12.0; local = src - 181.9 - 12
    L = lambda src: round(src - 181.9 - 12.0, 2)
    css = """
    #j-road { position: absolute; left: 0; top: 50px; width: 450px; height: 250px; border-radius: 18px; overflow: hidden;
      background: rgba(13,29,51,.92); border: 1px solid rgba(231,235,242,.25); }
    #j-road svg { position: absolute; left: 0; top: 0; width: 450px; height: 190px; }
    .j-m { position: absolute; top: 200px; width: 54px; height: 34px; border-radius: 6px; background: rgba(231,235,242,.12);
      font-size: 28px; font-weight: 900; color: #c9d2e0; text-align: center; line-height: 34px; }
    #j-ml { position: absolute; left: 18px; top: 160px; font-size: 28px; font-weight: 900; letter-spacing: .1em; color: #f2c55c; }
    #j-inv { position: absolute; left: 490px; top: 50px; width: 470px; height: 250px; border-radius: 18px; background: rgba(7,17,31,.95);
      border: 2px solid rgba(224,68,58,.8); padding: 22px 24px; }
    #j-inv b { display: block; font-size: 40px; font-weight: 900; line-height: 1.1; color: #ff8e83; }
    #j-inv span { display: block; margin-top: 14px; font-size: 30px; font-weight: 800; line-height: 1.2; color: #f4f6fa; }"""
    body = f"""    <div class="zone" id="j-zone">
      <div class="zk" id="j-k">LUBANG DIBIARKAN BERBULAN-BULAN</div>
      <div class="ill">ILUSTRASI</div>
      <div id="j-road">
        <svg viewBox="0 0 450 190" fill="none">
          <path d="M0 120 H450" stroke="rgba(231,235,242,.35)" stroke-width="2" />
          <rect x="0" y="120" width="450" height="70" fill="#20242c" />
          <path d="M30 155 H90 M140 155 H200 M250 155 H310 M360 155 H420" stroke="#f2c55c" stroke-width="5" />
          <path id="j-hole" d="M170 120 Q 225 182 280 120 Z" fill="#05070b" stroke="#ff6a5c" stroke-width="3" />
          <path d="M150 128 L130 140 M298 128 L320 142 M226 166 L232 186" stroke="#ff6a5c" stroke-width="3" stroke-linecap="round" />
        </svg>
        <div id="j-ml">BULAN</div>
        <div class="j-m" id="j-m1" style="left: 120px">1</div><div class="j-m" id="j-m2" style="left: 182px">2</div>
        <div class="j-m" id="j-m3" style="left: 244px">3</div><div class="j-m" id="j-m4" style="left: 306px">4</div>
        <div class="j-m" id="j-m5" style="left: 368px">5+</div>
      </div>
      <div class="pill gold" id="j-c0" style="left: 490px; top: 50px">TERLALU LAMA DIBAIKI</div>
      <div class="pill" id="j-c1" style="left: 490px; top: 112px">MENYUSAHKAN</div>
      <div class="pill red" id="j-c2" style="left: 490px; top: 174px">MENGUNDANG KEMALANGAN</div>
      <div class="pill red" id="j-c3" style="left: 490px; top: 236px">MEROSAKKAN KENDERAAN</div>
      <div id="j-inv"><b>MENJEJASKAN KEYAKINAN PELABUR</b><span id="j-inv2">Kerana terdapatnya kilang-kilang di kawasan Seri Iskandar</span></div>
    </div>"""
    js = [f'    tl.fromTo(["#j-k", "#j-zone .ill"], {FADE_IN}, 0.4);',
          '    tl.fromTo("#j-road", { opacity: 0, rotationX: 35, transformPerspective: 1100 }, { opacity: 1, rotationX: 0, duration: 0.6, ease: "expo.out" }, 0.4);',
          '    tl.fromTo("#j-hole", { scale: 0.2, transformOrigin: "225px 120px" }, { scale: 1, duration: 0.5, ease: "back.out(2)" }, 0.7);',
          f'    tl.fromTo("#j-c0", {POP_L}, {L(196.6)});']
    for i in range(5):
        js.append(f'    tl.fromTo("#j-m{i + 1}", {{ backgroundColor: "rgba(231,235,242,0.12)", color: "#c9d2e0" }}, {{ backgroundColor: "#e0443a", color: "#ffffff", duration: 0.15 }}, {L(199.4) + i * 0.22:.2f});')
    js += [f'    tl.fromTo("#j-c1", {POP_L}, {L(201.3)});', f'    tl.fromTo("#j-c2", {POP_L}, {L(203.5)});',
           f'    tl.fromTo("#j-c3", {POP_L}, {L(205.3)});',
           '    tl.set("#j-inv", { opacity: 0 }, 0);',
           f'    tl.to(["#j-c0", "#j-c1", "#j-c2", "#j-c3"], {{ opacity: 0, duration: 0.2 }}, {L(206.2) - 0.1:.2f});',
           f'    tl.fromTo("#j-inv", {{ opacity: 0, scale: 1.08 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "expo.out", immediateRender: false }}, {L(206.2)});',
           f'    tl.fromTo("#j-inv2", {BLUR_IN}, {L(210.4)});',
           '    tl.to("#j-zone", { opacity: 0, filter: "blur(8px)", duration: 0.2, ease: "power2.in" }, 18.85);']
    write(isu, "j3-lubang", scene("j3-lubang", css, body, "\n".join(js)))
    # j4: allocations (abs 31.1–49.1), split continues; local = src - 221.42
    L = lambda src: round(src - 221.42, 2)
    css = """
    .m-box { position: absolute; top: 46px; width: 470px; height: 254px; border-radius: 18px; background: rgba(13,29,51,.94);
      border: 1px solid rgba(242,197,92,.55); padding: 18px 22px; }
    .m-box small { display: block; font-size: 28px; font-weight: 800; letter-spacing: .1em; color: #c9d2e0; line-height: 1.15; }
    .m-box .v { display: block; margin-top: 10px; font-size: 54px; font-weight: 900; line-height: 1; white-space: nowrap; }
    .m-box .d { display: block; margin-top: 12px; font-size: 28px; font-weight: 900; color: #f2c55c; }
    #m1 { left: 0; } #m2 { left: 490px; }"""
    body = """    <div class="zone" id="m-zone">
      <div class="zk" id="m-k">PERUNTUKAN 2027 · SEPERTI DISEBUT</div>
      <div class="ill">GRAFIK</div>
      <div class="m-box" id="m1"><small>KERAJAAN TEMPATAN</small><span class="v gold3d" id="m1v">RM69.8 JUTA</span><span class="d" id="m1d">▲ NAIK 3.3%</span></div>
      <div class="m-box" id="m2"><small>SMK · SUMBANGAN MEMBANTU KADAR</small><span class="v gold3d" id="m2v">RM480.87 JUTA</span><span class="d" id="m2d">▲ MENINGKAT RM60.87 JUTA</span></div>
    </div>"""
    js = f"""    tl.fromTo(["#m-k", "#m-zone .ill"], {FADE_IN}, 0.2);
    tl.fromTo("#m1", {RISE}, 0.6);
    tl.fromTo("#m1v", {SLAM}, {L(224.9)});
    tl.fromTo("#m1d", {BLUR_IN}, {L(228.8)});
    tl.fromTo("#m2", {RISE}, {L(230.9)});
    tl.fromTo("#m2d", {BLUR_IN}, {L(234.1)});
    tl.fromTo("#m2v", {SLAM}, {L(236.7)});
    tl.to("#m-zone", {{ opacity: 0, filter: "blur(8px)", duration: 0.2, ease: "power2.in" }}, 17.8);"""
    write(isu, "j4-peruntukan", scene("j4-peruntukan", css, body, js))
    # j5: questions (abs 49.1–70.97), full frame with backdrop; local = abs - 49.1
    css = "\n    #q-z { position: absolute; left: 60px; top: 846px; width: 960px; height: 300px; }\n    #q-z .qcard p { font-size: 32px; }"
    body = """    <div class="bd" id="q-bd"></div>
    <div id="q-z">
      <div class="qcard" id="q1"><small>SOALAN</small>
        <p id="q1a">Apakah <b>tempoh</b> yang ditetapkan KPKT bagi PBT <b>membaiki jalan selepas aduan</b> diterima?</p>
        <p id="q1b">Bagaimanakah KPKT memantau pematuhan majlis daerah?</p></div>
      <div class="qcard" id="q2"><small>KEDUA</small>
        <p id="q2a">Berapakah <b>aduan kerosakan</b> di Seri Iskandar yang diterima dan diselesaikan sejak 2025?</p>
        <p id="q2b">Berapakah <b>purata hari</b> penyelesaiannya?</p></div>
    </div>"""
    js = f"""    tl.fromTo("#q-bd", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 0.2);
    tl.fromTo("#q1", {{ opacity: 0, scale: 1.05 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "expo.out" }}, 0.3);
    tl.fromTo("#q1a", {BLUR_IN}, 1.2);
    tl.fromTo("#q1b", {BLUR_IN}, 9.4);
    tl.to("#q1", {{ opacity: 0, duration: 0.2 }}, 13.85);
    tl.fromTo("#q2", {{ opacity: 0, scale: 1.05 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "expo.out" }}, 14.05);
    tl.fromTo("#q2a", {BLUR_IN}, 14.95);
    tl.fromTo("#q2b", {BLUR_IN}, 19.4);
    tl.to(["#q-z", "#q-bd"], {{ opacity: 0, duration: 0.2 }}, 21.65);"""
    write(isu, "j5-soalan", scene("j5-soalan", css, body, js))
    write(isu, "j6-outro", outro("j6-outro", "ISU 2 · SERI ISKANDAR", "JALAN BERLUBANG<br />SERI ISKANDAR", "end-isu2-jalan.jpg"))
    scenes = [("j1-hook", 0, 6.0), ("j2-id", 6.0, 6.0), ("j3-lubang", 12.0, 19.1), ("j4-peruntukan", 31.1, 18.0),
              ("j5-soalan", 49.1, 21.87), ("j6-outro", 70.97, 3.5)]
    sfx = [("impact-bass-2", 0, 0.11), ("impact-bass-1", 2.0, 0.09), ("pop", 3.4, 0.3), ("pop", 3.8, 0.3), ("pop", 4.7, 0.3),
           ("whoosh", 5.8, 0.36), ("pop", 6.6, 0.35), ("whoosh-short", 11.85, 0.28), ("pop", 14.7, 0.3), ("pop", 19.4, 0.3),
           ("pop", 21.6, 0.3), ("pop", 23.4, 0.3), ("impact-bass-1", 24.3, 0.08), ("whoosh", 30.95, 0.34),
           ("impact-bass-2", 34.55, 0.09), ("pop", 38.4, 0.3), ("pop", 43.8, 0.3), ("impact-bass-2", 46.3, 0.09),
           ("whoosh-short", 48.85, 0.26), ("pop", 49.4, 0.3), ("whoosh", 62.95, 0.3), ("pop", 63.2, 0.3), ("whoosh-cinematic", 68.3, 0.24)]
    camera = """      // 0–6 hook
      zoom(0, 1.5, 1.9, "power1.inOut");
      zoom(2.02, 1.6, 0.16); shake(2.02);
      // 6.0 cut → identity
      flash(6.0); cut(6.0, BASE.s); zoom(6.0, 1.18, 5.8, "power1.inOut"); sweep(6.6);
      splitOn(11.85);
      cut(31.1, 1.16, -230);
      splitOff(48.9);
      cut(49.1, 1.18); zoom(49.2, 1.26, 13.8, "power1.inOut");
      cut(63.13, 1.22); zoom(63.2, 1.32, 7.6, "power1.inOut");"""
    index(isu, "Isu 2: Jalan Berlubang Seri Iskandar — Dewan Rakyat", cuts, scenes, sfx, camera, 74.47)


# ================================================================= ISU 3 — DATARAN
def isu3():
    isu = "isu3-dataran"
    cuts = [(264.68, 303.56, 0.00)]
    L = lambda src: round(src - 264.68, 2)
    # hook: name of the place at frame 0, 19 hektar on its word
    css = HOOK_CSS + """
    #d1-sub { position: absolute; left: 0; width: 1080px; top: 1150px; text-align: center; font-size: 40px; font-weight: 900; letter-spacing: .08em; color: #ff8e83;
      text-shadow: 0 4px 16px rgba(0,0,0,.9); }"""
    body = """    <div class="bd" id="d1-bd" style="opacity:1"></div>
    <div id="d1-z">
      <div class="h-kick" id="d1-k"><span>SERI ISKANDAR, PARIT · DEWAN RAKYAT</span></div>
      <div class="h-line" id="d1-l0" style="top: 916px">DATARAN SUNGAI SELUANG</div>
      <div class="h-3d" id="d1-big" style="top: 994px; font-size: 140px">19 HEKTAR</div>
      <div id="d1-sub">MASIH BELUM DINAIK TARAF</div>
    </div>"""
    js = f"""    tl.fromTo(["#d1-k", "#d1-l0"], {{ opacity: 1 }}, {{ opacity: 1, duration: 0.01 }}, 0);
    tl.fromTo("#d1-big", {SLAM}, {L(269.1)});
    tl.fromTo("#d1-sub", {BLUR_IN}, {L(271.0)});
    tl.to(["#d1-z", "#d1-bd"], {{ opacity: 0, filter: "blur(10px)", duration: 0.16, ease: "power2.in" }}, 8.6);"""
    write(isu, "d1-hook", scene("d1-hook", css, body, js))
    write(isu, "d2-id", ident("d2-id", "HANYA LALUAN JOGGING / BERJALAN KAKI", 5.55))
    # d3: upgrades (abs 14.8–30.5) + question (30.5–38.88), split from 14.8; local = abs - 14.8
    tiles = [("TAMAN PERMAINAN KANAK-KANAK", 283.7), ("TEMPAT DUDUK &amp; TEDUHAN", 286.5), ("TANDAS AWAM", 288.3),
             ("LAMPU", 289.2), ("KEMUDAHAN OKU", 291.7), ("GERAI PENIAGA KECIL", 292.1)]
    pos = [(0, 46), (490, 46), (0, 130), (490, 130), (0, 214), (490, 214)]
    body = ['    <div class="zone" id="u-zone">', '      <div class="zk" id="u-k">SESUAI DINAIK TARAF DENGAN</div>', '      <div class="ill">ILUSTRASI</div>']
    js = [f'    tl.fromTo(["#u-k", "#u-zone .ill"], {FADE_IN}, 0.4);']
    for n, ((name, src), (x, y)) in enumerate(zip(tiles, pos)):
        body.append(f'      <div class="tile" id="u-t{n}" style="left: {x}px; top: {y}px; width: 470px; height: 76px"><em>{n + 1}</em>{name}</div>')
        js.append(f'    tl.fromTo("#u-t{n}", {RISE}, {L(src) - 14.8:.2f});')
    body.append('      <div class="qcard" id="u-q"><small>SOALAN</small><p>Adakah KPKT bersedia mempertimbangkan <b>Dataran Sungai Seluang</b> sebagai <b>projek pembangunan taman awam</b> pada tahun 2027 ini?</p></div>')
    body.append('    </div>')
    js += ['    tl.set("#u-q", { opacity: 0 }, 0);',
           f'    tl.to(".tile", {{ opacity: 0, duration: 0.2 }}, {L(295.3) - 14.8 - 0.1:.2f});',
           f'    tl.fromTo("#u-q", {{ opacity: 0, scale: 1.06 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "expo.out", immediateRender: false }}, {L(295.3) - 14.8:.2f});',
           '    tl.to("#u-zone", { opacity: 0, duration: 0.2 }, 23.88);']
    # The stretch before the first tile ("Ianya sangat sesuai untuk dinaik taraf dengan didirikan …") gets a growth line.
    css = """
    #u-arrow { position: absolute; left: 0; top: 110px; width: 960px; text-align: center; font-size: 76px; font-weight: 900; line-height: 1; }"""
    body.insert(3, '      <div id="u-arrow" class="gold3d">▲ NAIK TARAF</div>')
    js += ['    tl.fromTo("#u-arrow", ' + SLAM + ', 0.5);', f'    tl.to("#u-arrow", {{ opacity: 0, duration: 0.2 }}, {L(283.7) - 14.8 - 0.2:.2f});']
    write(isu, "d3-naiktaraf", scene("d3-naiktaraf", css, "\n".join(body), "\n".join(js)))
    write(isu, "d4-outro", outro("d4-outro", "ISU 3 · SERI ISKANDAR", "DATARAN<br />SUNGAI SELUANG", "end-isu3-dataran.jpg"))
    scenes = [("d1-hook", 0, 8.8), ("d2-id", 8.8, 6.0), ("d3-naiktaraf", 14.8, 24.08), ("d4-outro", 38.88, 3.5)]
    sfx = [("impact-bass-2", 0, 0.1), ("impact-bass-1", L(269.1), 0.09), ("whoosh", 8.6, 0.34), ("pop", 9.4, 0.35),
           ("whoosh-short", 14.65, 0.28), ("impact-bass-1", 15.3, 0.07)] + \
          [("pop", round(L(s), 2), 0.3) for _, s in tiles] + [("riser", 26.6, 0.08), ("impact-bass-2", L(295.3), 0.1), ("whoosh-cinematic", 36.3, 0.24)]
    camera = """      // one continuous take: tight → base → panel
      zoom(0, 1.5, 4.3, "power1.inOut");
      zoom(4.42, 1.6, 0.16); shake(4.42);
      tl.to(cam, { scale: BASE.s, y: BASE.y, duration: 0.8, ease: "power2.inOut" }, 8.6);
      sweep(8.9);
      zoom(9.4, 1.18, 5.2, "power1.inOut");
      splitOn(14.65);
      splitOff(38.6, 0.25);"""
    index(isu, "Isu 3: Dataran Sungai Seluang — Dewan Rakyat", cuts, scenes, sfx, camera, 42.38)


# ================================================================= ISU 4 — RUMAH
def isu4():
    isu = "isu4-rumah"
    cuts = [(341.50, 345.65, 0.00), (304.72, 306.80, 4.15), (308.65, 356.30, 6.23)]
    L = lambda src: round(src - 302.42, 2)   # cut 3: out = src - 302.42
    write(isu, "r1-hook", hook("r1-hook", "RUMAH MESRA RAKYAT · DEWAN RAKYAT",
                               ["“DAN MENGAPA PERBELANJAAN SEBENAR", "2025 DICATATKAN"], "SIFAR?”", 150, [0, 1.95], 2.9, 3.97))
    write(isu, "r2-id", ident("r2-id", "ISU 4 · RUMAH KOS RENDAH", 4.3))
    # r3: young B40/M40 (abs 8.6–18.3), split from 8.6; local = abs - 8.6
    css = """
    .r-badge { position: absolute; top: 50px; width: 200px; height: 140px; border-radius: 18px; text-align: center;
      background: rgba(13,29,51,.94); border: 2px solid rgba(242,197,92,.7); }
    .r-badge span { display: block; margin-top: 18px; font-size: 76px; font-weight: 900; line-height: 1; }
    .r-badge b { display: block; margin-top: 6px; font-size: 28px; font-weight: 800; letter-spacing: 0; white-space: nowrap; color: #c9d2e0; }
    #r-txt { position: absolute; left: 450px; top: 60px; width: 510px; font-size: 40px; font-weight: 900; line-height: 1.15; color: #f4f6fa; }
    #r-no { position: absolute; left: 0; top: 214px; width: 960px; height: 70px; border-radius: 14px; border: 2px solid rgba(224,68,58,.85);
      background: rgba(30,6,6,.75); text-align: center; line-height: 66px; font-size: 36px; font-weight: 900; letter-spacing: .08em; color: #ff8e83; }
    #r-pins b { position: absolute; left: 0; top: 0; font-size: 28px; font-weight: 800; letter-spacing: .16em; color: #c9d2e0; }
    .r-pin { position: absolute; top: 40px; height: 60px; padding: 0 22px 0 52px; border-radius: 30px; background: #f2c55c; color: #17110a;
      font-size: 30px; font-weight: 900; letter-spacing: .06em; line-height: 60px; }
    .r-pin i { position: absolute; left: 18px; top: 18px; width: 24px; height: 24px; border-radius: 50% 50% 50% 0; background: #17110a; }
    .r-bar { position: absolute; left: 0; width: 960px; height: 64px; }
    .r-bar b { position: absolute; left: 0; top: 16px; width: 260px; font-size: 28px; font-weight: 900; letter-spacing: .1em; color: #f4f6fa; }
    .r-bar div { position: absolute; left: 270px; top: 8px; height: 48px; border-radius: 10px; transform-origin: 0 50%; }
    #r-h { top: 160px; } #r-i { top: 232px; }
    #r-h div { width: 690px; background: repeating-linear-gradient(135deg, #c8463c 0 14px, #9d3128 14px 28px); }
    #r-i div { width: 300px; background: linear-gradient(180deg, #ffe08f, #d9a641 60%, #a8781f); }"""
    body = """    <div class="zone" id="r-zone">
      <div class="zk" id="r-k">ANAK MUDA DI PARLIMEN PARIT</div>
      <div class="ill">GRAFIK</div>
      <div id="r-sec1">
        <div class="r-badge" id="r-b1" style="left: 0"><span class="gold3d">B40</span><b>ANAK MUDA</b></div>
        <div class="r-badge" id="r-b2" style="left: 220px"><span class="gold3d">M40</span><b>ANAK MUDA</b></div>
        <div id="r-txt">Ramai yang masih belum memiliki rumah sendiri</div>
        <div id="r-no">BELUM MEMILIKI RUMAH SENDIRI</div>
      </div>
      <div id="r-sec2">
        <div id="r-pins"><b>BEKERJA DI</b>
          <div class="r-pin" id="r-p1" style="left: 0"><i></i>SERI ISKANDAR</div>
          <div class="r-pin" id="r-p2" style="left: 362px"><i></i>IPOH</div>
          <div class="r-pin" id="r-p3" style="left: 540px"><i></i>BOTA</div>
        </div>
        <div class="r-bar" id="r-h"><b>HARGA RUMAH</b><div></div></div>
        <div class="r-bar" id="r-i"><b>PENDAPATAN</b><div></div></div>
      </div>
    </div>"""
    l3 = lambda src: round(L(src) - 8.6, 2)
    js = f"""    tl.fromTo(["#r-k", "#r-zone .ill"], {FADE_IN}, 0.35);
    tl.fromTo("#r-b1", {{ opacity: 0, scale: 1.5 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(1.8)" }}, 0.5);
    tl.fromTo("#r-b2", {{ opacity: 0, scale: 1.5 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(1.8)" }}, 0.8);
    tl.fromTo("#r-txt", {{ opacity: 0, x: 20 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "expo.out" }}, 1.0);
    tl.fromTo("#r-no", {{ opacity: 0, scale: 1.12 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "expo.out" }}, {l3(312.3)});
    tl.to("#r-sec1", {{ opacity: 0, filter: "blur(8px)", duration: 0.25, ease: "power2.in" }}, {l3(314.6)});
    tl.set("#r-k", {{ opacity: 0 }}, {l3(314.7)});
    tl.fromTo("#r-pins b", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {l3(314.75)});
    tl.fromTo("#r-p1", {{ opacity: 0, y: -20 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "back.out(2)" }}, {l3(315.4)});
    tl.fromTo("#r-p2", {{ opacity: 0, y: -20 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "back.out(2)" }}, {l3(315.9)});
    tl.fromTo("#r-p3", {{ opacity: 0, y: -20 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "back.out(2)" }}, {l3(316.35)});
    tl.fromTo(["#r-h", "#r-i"], {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, {l3(317.2)});
    tl.fromTo("#r-h div", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.7, ease: "power3.out" }}, {l3(317.3)});
    tl.fromTo("#r-i div", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.7, ease: "power3.out" }}, {l3(318.9)});
    tl.to("#r-zone", {{ opacity: 0, filter: "blur(8px)", duration: 0.25, ease: "power2.in" }}, 9.45);"""
    write(isu, "r3-belia", scene("r3-belia", css, body, js))
    # r4: what they need (abs 18.3–22.79), full frame
    l4 = lambda src: round(L(src) - 18.3, 2)
    css = """
    #c-k { position: absolute; left: 0; top: 872px; width: 1080px; text-align: center; font-size: 32px; font-weight: 800; letter-spacing: .22em; color: #f4f6fa; }
    #c-big { position: absolute; left: 0; top: 920px; width: 1080px; text-align: center; white-space: nowrap; font-size: 96px; font-weight: 900; line-height: 1; }
    #c-sub { position: absolute; left: 0; top: 1030px; width: 1080px; text-align: center; font-size: 56px; font-weight: 900; }
    #c-loc { position: absolute; left: 0; top: 1098px; width: 1080px; text-align: center; font-size: 36px; font-weight: 800; letter-spacing: .14em; color: #f2c55c; }"""
    body = """    <div class="bd" id="c-bd"></div>
    <div id="c-k">MEREKA MEMERLUKAN</div>
    <div id="c-big" class="gold3d">RUMAH KOS RENDAH</div>
    <div id="c-sub" class="silver3d">&amp; MAMPU MILIK</div>
    <div id="c-loc">DIBINA DI LOKASI BERHAMPIRAN</div>"""
    js = f"""    tl.fromTo("#c-bd", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 0.1);
    tl.fromTo("#c-k", {BLUR_IN}, {max(0.15, l4(320.9))});
    tl.fromTo("#c-big", {SLAM}, {l4(321.6)});
    tl.fromTo("#c-sub", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "expo.out" }}, {l4(322.3)});
    tl.fromTo("#c-loc", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {l4(323.3)});
    tl.to(["#c-bd", "#c-k", "#c-big", "#c-sub", "#c-loc"], {{ opacity: 0, duration: 0.2, ease: "power2.in" }}, 4.3);"""
    write(isu, "r4-perlu", scene("r4-perlu", css, body, js))
    # r5: three questions (abs 22.79–53.88), split from 22.6; local = abs - 22.79
    l5 = lambda src: round(L(src) - 22.79, 2)
    css = """
    .tabs { position: absolute; left: 0; top: 0; width: 960px; height: 40px; }
    .tab { position: absolute; top: 0; width: 120px; height: 38px; border-radius: 8px; text-align: center; line-height: 38px;
      font-size: 28px; font-weight: 900; color: #c9d2e0; background: rgba(231,235,242,.1); }
    .q { position: absolute; left: 0; top: 52px; width: 960px; height: 248px; border-radius: 18px; background: rgba(7,17,31,.95);
      border: 2px solid rgba(242,197,92,.8); padding: 20px 28px; }
    .q p { font-size: 32px; font-weight: 800; line-height: 1.2; color: #f4f6fa; }
    .q p + p { margin-top: 12px; }
    .q p b { color: #f8d77e; }
    #q2-zero { position: absolute; right: 26px; bottom: 18px; padding: 6px 18px; border-radius: 10px; border: 4px solid #ff5a4c;
      font-size: 44px; font-weight: 900; color: #ff6a5c; background: rgba(30,6,6,.85); letter-spacing: .06em; }"""
    body = """    <div class="zone" id="q-zone">
      <div class="tabs"><div class="tab" id="t1" style="left: 0">01</div><div class="tab" id="t2" style="left: 132px">02</div><div class="tab" id="t3" style="left: 264px">03</div>
        <div class="tab" style="left: 400px; width: 560px; background: none; text-align: left; color: #f2c55c">SOALAN KEPADA KPKT</div></div>
      <div class="q" id="q1"><p id="q1a">Berapakah unit <b>rumah PPR, Rumah Mesra Rakyat dan PRIMA</b> yang dirancang di Parlimen Parit pada tahun 2027?</p>
        <p id="q1b">Adakah tapak telah dikenal pasti?</p></div>
      <div class="q" id="q2"><p id="q2a">Berapakah <b>kuota Rumah Mesra Rakyat SPNB</b> bagi negeri Perak dan daerah Perak Tengah?</p>
        <p id="q2b">Mengapa perbelanjaan sebenar 2025 dicatatkan</p><div id="q2-zero">SIFAR?</div></div>
      <div class="q" id="q3"><p id="q3a">Adakah KPKT bersedia bekerjasama dengan kerajaan negeri untuk <b>menyediakan tanah</b> bagi rumah kos rendah dan mampu milik di Seri Iskandar dan Parit?</p>
        <p id="q3b">— memandangkan tanah ialah bidang kuasa negeri</p></div>
    </div>"""
    on = '{ backgroundColor: "rgba(231,235,242,0.1)", color: "#c9d2e0" }, { backgroundColor: "#f2c55c", color: "#17110a", duration: 0.2 }'
    off = '{ backgroundColor: "rgba(231,235,242,0.1)", color: "#c9d2e0", duration: 0.2 }'
    js = f"""    tl.fromTo(".tabs", {FADE_IN}, 0.2);
    tl.set(["#q2", "#q3", "#q2-zero"], {{ opacity: 0 }}, 0);
    tl.fromTo("#t1", {on}, 0.3);
    tl.fromTo("#q1", {RISE}, 0.3);
    tl.fromTo("#q1a", {BLUR_IN}, {l5(325.4)});
    tl.fromTo("#q1b", {BLUR_IN}, {l5(332.8)});
    tl.to("#q1", {{ opacity: 0, duration: 0.2 }}, {l5(335.2)});
    tl.to("#t1", {off}, {l5(335.2)});
    tl.fromTo("#t2", {on}, {l5(335.3)});
    tl.fromTo("#q2", {{ opacity: 0, y: 22 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "expo.out", immediateRender: false }}, {l5(335.3)});
    tl.fromTo("#q2a", {BLUR_IN}, {l5(335.4)});
    tl.fromTo("#q2b", {BLUR_IN}, {l5(341.6)});
    tl.fromTo("#q2-zero", {{ opacity: 0, scale: 2, rotation: -12 }}, {{ opacity: 1, scale: 1, rotation: -4, duration: 0.2, ease: "power4.out", immediateRender: false }}, {l5(344.4)});
    tl.to("#q2", {{ opacity: 0, duration: 0.2 }}, {l5(346.2)});
    tl.to("#t2", {off}, {l5(346.2)});
    tl.fromTo("#t3", {on}, {l5(346.3)});
    tl.fromTo("#q3", {{ opacity: 0, y: 22 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "expo.out", immediateRender: false }}, {l5(346.3)});
    tl.fromTo("#q3a", {BLUR_IN}, {l5(346.4)});
    tl.fromTo("#q3b", {BLUR_IN}, {l5(353.7)});
    tl.to("#q-zone", {{ opacity: 0, duration: 0.2 }}, 30.85);"""
    write(isu, "r5-soalan", scene("r5-soalan", css, body, js))
    write(isu, "r6-outro", outro("r6-outro", "ISU 4 · PARLIMEN PARIT", "RUMAH KOS RENDAH<br />&amp; MAMPU MILIK", "end-isu4-rumah.jpg"))
    scenes = [("r1-hook", 0, 4.15), ("r2-id", 4.15, 4.6), ("r3-belia", 8.6, 9.7), ("r4-perlu", 18.3, 4.49),
              ("r5-soalan", 22.79, 31.09), ("r6-outro", 53.88, 3.5)]
    sfx = [("impact-bass-2", 0, 0.11), ("impact-bass-2", 2.9, 0.11), ("whoosh", 3.95, 0.36), ("pop", 4.7, 0.35),
           ("whoosh-short", 8.45, 0.28), ("pop", 9.1, 0.3), ("pop", 9.4, 0.3), ("impact-bass-1", L(312.3), 0.08),
           ("pop", L(315.4), 0.3), ("pop", L(315.9), 0.3), ("pop", L(316.35), 0.3), ("whoosh-short", 18.1, 0.26),
           ("riser", L(321.6) - 3.9, 0.08), ("impact-bass-2", L(321.6), 0.12), ("whoosh-short", 22.45, 0.28), ("pop", 23.1, 0.3),
           ("pop", L(335.3), 0.3), ("impact-bass-2", L(344.4), 0.12), ("pop", L(346.3), 0.3), ("whoosh-cinematic", 51.3, 0.24)]
    camera = f"""      // 0–4.15 hook
      zoom(0, 1.5, 2.8, "power1.inOut");
      zoom(2.92, 1.62, 0.16); shake(2.92);
      // identity
      flash(4.15); cut(4.15, BASE.s); zoom(4.15, 1.16, 4.3, "power1.inOut"); sweep(4.7);
      cut(6.23, 1.2);
      splitOn(8.45);
      splitOff(18.1, 0.4);
      zoom(18.3, 1.3, 0.8, "power2.inOut");
      zoom({L(321.6)}, 1.4, 0.2); flash({L(321.6) + 0.02}, 0.3);
      splitOn(22.45);
      splitOff(53.6, 0.3);"""
    index(isu, "Isu 4: Rumah Kos Rendah Parit — Dewan Rakyat", cuts, scenes, sfx, camera, 57.38)


if __name__ == "__main__":
    isu1(); isu2(); isu3(); isu4()
    print("wrote 4 projects")
