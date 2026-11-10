"""Generate the scenes and root of "Selepas Umur 40 Tahun, Kekayaan Sebenar Adalah…".

Same look as the first film: midnight blue, warm gold, amber, cream; Montserrat for
reading text, Playfair Display italic for the meaningful word; slow eases, dissolves.
All copy is verbatim from the supplied infographic.

Run:  python3 tools/build.py   (from kekayaan-40/)
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCENE = 5.0  # seconds per point
HOOK = 5.5
QUOTE = 5.5
RECAP = 6.5

# (number, [(text, "lead" | "key")], illustration id)
POINTS = [
    ("01", [("Kesihatan", "key"), ("yang masih baik", "lead")], "pulse"),
    ("02", [("Hati yang", "lead"), ("tenang", "key")], "ripple"),
    ("03", [("Rezeki yang", "lead"), ("cukup dan berkat", "key")], "vessel"),
    ("04", [("Keluarga yang", "lead"), ("bahagia", "key")], "family"),
    ("05", [("Anak-anak yang", "lead"), ("sihat", "key")], "sprout"),
    ("06", [("Sahabat yang", "lead"), ("ikhlas", "key")], "path"),
    ("07", [("Hidup", "lead"), ("tanpa beban hutang", "key")], "release"),
    ("08", [("Masa untuk mendekatkan diri", "lead"), ("kepada Allah", "key")], "night"),
]

BASE_CSS = """
    #root { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
    #root .bg { position: absolute; inset: 0;
      background: radial-gradient(110% 70% at 50% 42%, #1a3663 0%, #0b1a30 58%, #050c18 100%); }
    #root .chip { position: absolute; left: 0; right: 0; top: 232px; text-align: center; }
    #root .chip span { display: inline-block; padding: 12px 30px; border: 1.5px solid rgba(226,189,114,.75);
      border-radius: 40px; background: rgba(8,18,34,.55); font-family: "Montserrat", sans-serif;
      font-weight: 600; font-size: 28px; letter-spacing: .24em; color: #f6eedf; }
    #root .chip b { color: #e2bd72; font-weight: 700; }
    #root .head { position: absolute; left: 0; right: 0; top: 352px; padding: 0 90px; text-align: center; }
    #root .lead { font-family: "Montserrat", sans-serif; font-weight: 600; font-size: 56px; line-height: 1.2;
      color: #f6eedf; text-shadow: 0 3px 24px rgba(4,10,22,.8); }
    #root .key { font-family: "Playfair Display", serif; font-style: italic; font-size: 100px; line-height: 1.12;
      color: #f0cd84; text-shadow: 0 0 50px rgba(233,163,91,.45), 0 3px 24px rgba(4,10,22,.8); }
    #root .art { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
"""

# Illustration markup (SVG in a 1080x1920 frame; art lives between y≈760 and y≈1320)
# and its timeline (local seconds, 0 = scene start). `P` is the scene's id prefix.
ART = {
    "pulse": (
        """<svg class="art" viewBox="0 0 1080 1920">
          <defs><radialGradient id="P-glow"><stop offset="0" stop-color="#ffd99a" stop-opacity=".9"/>
          <stop offset="1" stop-color="#e9a35b" stop-opacity="0"/></radialGradient></defs>
          <circle id="P-halo" cx="540" cy="1040" r="230" fill="url(#P-glow)" opacity="0"/>
          <path id="P-ecg" d="M 90 1040 L 330 1040 L 370 1000 L 410 1040 L 455 1040 L 490 880 L 535 1190 L 575 1040
            L 640 1040 L 680 990 L 730 1040 L 990 1040" fill="none" stroke="#f0cd84" stroke-width="7"
            stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="1600" stroke-dashoffset="1600"/>
          <circle id="P-dot" cx="990" cy="1040" r="12" fill="#fff4dc" opacity="0"/>
        </svg>""",
        """tl.fromTo("#P-ecg", { attr: { "stroke-dashoffset": 1600 } }, { attr: { "stroke-dashoffset": 0 }, duration: 2.4, ease: "power1.inOut" }, 0.6);
        tl.fromTo("#P-dot", { opacity: 0 }, { opacity: 1, duration: 0.3 }, 2.9);
        [1.55, 2.75, 3.95].forEach((t) => tl.fromTo("#P-halo", { opacity: 0.15, scale: 0.85, svgOrigin: "540 1040" },
          { opacity: 0.9, scale: 1.1, duration: 0.45, ease: "sine.out", yoyo: true, repeat: 1, immediateRender: false }, t));""",
    ),
    "ripple": (
        """<svg class="art" viewBox="0 0 1080 1920">
          <defs><radialGradient id="P-moon"><stop offset="0" stop-color="#f6eedf" stop-opacity=".9"/>
          <stop offset="1" stop-color="#f6eedf" stop-opacity="0"/></radialGradient></defs>
          <rect x="0" y="1010" width="1080" height="330" fill="#0a1830" opacity=".55"/>
          <ellipse id="P-refl" cx="540" cy="1050" rx="140" ry="26" fill="url(#P-moon)" opacity=".5"/>
          <g id="P-rings" fill="none" stroke="#e2bd72" stroke-width="3">
            <ellipse cx="540" cy="1050" rx="400" ry="70"/><ellipse cx="540" cy="1050" rx="400" ry="70"/>
            <ellipse cx="540" cy="1050" rx="400" ry="70"/><ellipse cx="540" cy="1050" rx="400" ry="70"/>
          </g>
          <circle id="P-drop" cx="540" cy="820" r="10" fill="#fff4dc"/>
        </svg>""",
        """tl.fromTo("#P-drop", { attr: { cy: 760 }, opacity: 0 }, { attr: { cy: 1046 }, opacity: 1, duration: 0.8, ease: "power2.in" }, 0.5);
        tl.to("#P-drop", { opacity: 0, duration: 0.15 }, 1.3);
        document.querySelectorAll("#P-rings ellipse").forEach((e, k) => {
          // Each ring travels a little less: the water settles.
          tl.fromTo(e, { scale: 0.05, opacity: 0.95, svgOrigin: "540 1050" },
            { scale: 1 - k * 0.12, opacity: 0, duration: 2.6 + k * 0.3, ease: "sine.out" }, 1.3 + k * 0.45);
        });
        tl.fromTo("#P-refl", { opacity: 0.2, scaleX: 0.6, svgOrigin: "540 1050" }, { opacity: 0.9, scaleX: 1, duration: 3, ease: "sine.inOut" }, 1.6);""",
    ),
    "vessel": (
        """<div class="art">
          <div id="P-bowl" style="position:absolute;left:330px;top:820px;width:420px;height:420px;border-radius:50%;
            border:4px solid rgba(240,205,132,.9);overflow:hidden;box-shadow:0 0 60px rgba(233,163,91,.3), inset 0 0 40px rgba(11,26,48,.7)">
            <div id="P-fill" style="position:absolute;left:-10%;width:120%;bottom:0;height:100%;
              background:linear-gradient(180deg,#f6d28c,#e9a35b);transform-origin:50% 100%"></div>
          </div>
          <div id="P-mark" style="position:absolute;left:300px;width:480px;top:944px;border-top:3px dashed rgba(246,238,223,.85)"></div>
          <div id="P-label" style="position:absolute;left:790px;top:922px;font-family:Montserrat,sans-serif;font-weight:700;
            font-size:30px;letter-spacing:.2em;color:#f6eedf">CUKUP</div>
          <div id="P-spark"></div>
        </div>""",
        """tl.fromTo("#P-bowl", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.7, ease: "power2.out" }, 0.4);
        tl.fromTo(["#P-mark", "#P-label"], { opacity: 0 }, { opacity: 1, duration: 0.5 }, 0.9);
        // Fills exactly to the "enough" line, no further.
        tl.fromTo("#P-fill", { scaleY: 0.02 }, { scaleY: 0.705, duration: 2.0, ease: "power2.inOut" }, 1.1);
        const host = document.getElementById("P-spark");
        [[360, 860], [700, 830], [300, 1120], [770, 1110], [540, 770], [450, 1260], [640, 1250]].forEach(([x, y], k) => {
          const s = document.createElement("div");
          s.style.cssText = `position:absolute;left:${x}px;top:${y}px;width:26px;height:26px;background:#fff1cf;
            clip-path:polygon(50% 0,60% 40%,100% 50%,60% 60%,50% 100%,40% 60%,0 50%,40% 40%);`;
          host.appendChild(s);
          tl.fromTo(s, { opacity: 0, scale: 0.2, rotation: 0 }, { opacity: 1, scale: 1.2, rotation: 45, duration: 0.5, ease: "back.out(2)" }, 3.1 + k * 0.12);
          tl.to(s, { opacity: 0.35, scale: 0.8, duration: 0.6, ease: "sine.inOut" }, 3.7 + k * 0.12);
        });""",
    ),
    "family": (
        """<div class="art">
          <div id="P-frame" style="position:absolute;left:230px;top:760px;width:620px;height:560px;border-radius:22px;overflow:hidden;
            border:3px solid rgba(240,205,132,.85);box-shadow:0 30px 70px rgba(0,0,0,.55)">
            <img id="P-img" src="assets/img/keluarga.jpg" alt="" style="position:absolute;left:0;top:-90px;width:620px;height:796px"/>
            <div id="P-sweep" style="position:absolute;top:-60px;left:0;width:160px;height:700px;
              background:linear-gradient(90deg,rgba(255,245,225,0),rgba(255,245,225,.45),rgba(255,245,225,0))"></div>
          </div>
        </div>""",
        """tl.fromTo("#P-frame", { opacity: 0, y: 40, rotation: -2 }, { opacity: 1, y: 0, rotation: 0, duration: 1.0, ease: "power3.out" }, 0.4);
        tl.fromTo("#P-img", { scale: 1.0 }, { scale: 1.08, duration: 4.6, ease: "sine.inOut" }, 0.4);
        tl.fromTo("#P-sweep", { x: -220, rotation: 16 }, { x: 760, rotation: 16, duration: 1.4, ease: "power1.inOut" }, 1.6);""",
    ),
    "sprout": (
        """<svg class="art" viewBox="0 0 1080 1920">
          <defs><radialGradient id="P-sun"><stop offset="0" stop-color="#ffe2b0" stop-opacity=".85"/>
          <stop offset="1" stop-color="#e9a35b" stop-opacity="0"/></radialGradient></defs>
          <circle id="P-sunc" cx="540" cy="960" r="300" fill="url(#P-sun)" opacity="0"/>
          <path d="M 120 1240 Q 540 1205 960 1240 L 960 1290 L 120 1290 Z" fill="#0a1424"/>
          <line x1="140" y1="1238" x2="940" y2="1238" stroke="#e2bd72" stroke-width="3" opacity=".7"/>
          <g id="P-s1"><path d="M 430 1236 C 425 1150 445 1080 440 1010" stroke="#9fc58a" stroke-width="9" fill="none" stroke-linecap="round"/>
            <path id="P-l1a" d="M 440 1040 C 380 1020 360 975 380 950 C 420 965 440 1000 440 1040 Z" fill="#b8d99a"/>
            <path id="P-l1b" d="M 441 1070 C 500 1055 525 1010 505 985 C 465 1000 443 1035 441 1070 Z" fill="#9fc58a"/></g>
          <g id="P-s2"><path d="M 650 1236 C 655 1170 640 1120 648 1070" stroke="#9fc58a" stroke-width="8" fill="none" stroke-linecap="round"/>
            <path id="P-l2a" d="M 648 1095 C 595 1080 578 1040 595 1018 C 632 1030 648 1060 648 1095 Z" fill="#b8d99a"/>
            <path id="P-l2b" d="M 649 1120 C 700 1108 720 1070 703 1048 C 668 1062 650 1092 649 1120 Z" fill="#9fc58a"/></g>
        </svg>""",
        """tl.fromTo("#P-sunc", { opacity: 0, scale: 0.8, svgOrigin: "540 960" }, { opacity: 1, scale: 1.05, duration: 3.5, ease: "sine.out" }, 0.4);
        tl.fromTo("#P-s1", { scaleY: 0, svgOrigin: "440 1238" }, { scaleY: 1, duration: 1.8, ease: "power2.out" }, 0.7);
        tl.fromTo("#P-s2", { scaleY: 0, svgOrigin: "650 1238" }, { scaleY: 1, duration: 1.8, ease: "power2.out" }, 1.0);
        [["#P-l1a", "440px 1040px", 2.2], ["#P-l1b", "441px 1070px", 2.4], ["#P-l2a", "648px 1095px", 2.5], ["#P-l2b", "649px 1120px", 2.7]]
          .forEach(([id, o, t]) => tl.fromTo(id, { scale: 0, svgOrigin: o.replace(/px/g, "") }, { scale: 1, duration: 0.8, ease: "back.out(1.7)" }, t));""",
    ),
    "path": (
        """<svg class="art" viewBox="0 0 1080 1920">
          <defs><radialGradient id="P-o"><stop offset="0" stop-color="#fff6e6"/><stop offset=".3" stop-color="#f0cd84" stop-opacity=".8"/>
          <stop offset="1" stop-color="#e9a35b" stop-opacity="0"/></radialGradient>
          <linearGradient id="P-road" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1d3a63" stop-opacity=".2"/>
          <stop offset="1" stop-color="#1d3a63" stop-opacity=".9"/></linearGradient></defs>
          <path d="M 500 800 L 580 800 L 900 1320 L 180 1320 Z" fill="url(#P-road)"/>
          <path d="M 500 800 L 180 1320 M 580 800 L 900 1320" stroke="#e2bd72" stroke-width="3" opacity=".6"/>
          <g id="P-a"><circle cx="0" cy="0" r="70" fill="url(#P-o)"/></g>
          <g id="P-b"><circle cx="0" cy="0" r="70" fill="url(#P-o)"/></g>
        </svg>""",
        """// Two lights walk the same road together, side by side, into the distance.
        tl.fromTo("#P-a", { x: 440, y: 1280, scale: 1.2, opacity: 0 }, { x: 524, y: 860, scale: 0.35, opacity: 1, duration: 4.0, ease: "sine.inOut" }, 0.5);
        tl.fromTo("#P-b", { x: 640, y: 1280, scale: 1.2, opacity: 0 }, { x: 556, y: 860, scale: 0.35, opacity: 1, duration: 4.0, ease: "sine.inOut" }, 0.5);""",
    ),
    "release": (
        """<svg class="art" viewBox="0 0 1080 1920">
          <defs><radialGradient id="P-o"><stop offset="0" stop-color="#fff6e6"/><stop offset=".3" stop-color="#f0cd84" stop-opacity=".85"/>
          <stop offset="1" stop-color="#e9a35b" stop-opacity="0"/></radialGradient></defs>
          <line id="P-thread" x1="540" y1="1050" x2="540" y2="1190" stroke="#cfc4ae" stroke-width="3"/>
          <g id="P-stone"><path d="M 470 1190 L 610 1190 L 640 1300 L 440 1300 Z" fill="#2a3446" stroke="#465269" stroke-width="3"/>
            <text x="540" y="1258" text-anchor="middle" font-family="Montserrat" font-weight="700" font-size="30" letter-spacing="4" fill="#8e9ab0">HUTANG</text></g>
          <g id="P-orb"><circle cx="540" cy="1010" r="100" fill="url(#P-o)"/></g>
        </svg>""",
        """tl.fromTo(["#P-orb", "#P-thread", "#P-stone"], { opacity: 0 }, { opacity: 1, duration: 0.6 }, 0.3);
        // Weighed down, then the thread lets go.
        tl.fromTo("#P-orb", { y: 0 }, { y: 18, duration: 0.6, ease: "sine.inOut", yoyo: true, repeat: 1 }, 0.6);
        tl.to("#P-thread", { opacity: 0, duration: 0.15 }, 2.0);
        tl.fromTo("#P-stone", { y: 0, rotation: 0, svgOrigin: "540 1245" }, { y: 560, rotation: 8, opacity: 0, duration: 1.1, ease: "power2.in", immediateRender: false }, 2.0);
        tl.fromTo("#P-orb", { y: 0, scale: 1, svgOrigin: "540 1010" }, { y: -90, scale: 1.25, duration: 1.8, ease: "power2.out", immediateRender: false }, 2.05);""",
    ),
    "night": (
        """<svg class="art" viewBox="0 0 1080 1920">
          <defs><radialGradient id="P-col"><stop offset="0" stop-color="#ffe9c2" stop-opacity=".7"/>
          <stop offset="1" stop-color="#e9a35b" stop-opacity="0"/></radialGradient></defs>
          <g id="P-stars" fill="#f6eedf"></g>
          <g id="P-moon"><circle cx="760" cy="860" r="70" fill="#f0cd84"/><circle cx="790" cy="840" r="62" fill="#122a4c"/></g>
          <ellipse id="P-light" cx="540" cy="1150" rx="260" ry="320" fill="url(#P-col)" opacity="0"/>
          <path d="M 300 1300 L 300 1200 Q 300 1100 400 1080 Q 470 1040 470 990 L 470 980 L 476 970 L 482 980 L 482 990
            Q 482 1040 552 1080 Q 652 1100 652 1200 L 652 1300 Z M 700 1300 L 700 1050 L 715 1020 L 730 1050 L 730 1300 Z"
            fill="#060e1c" transform="translate(64 0)"/>
          <rect x="0" y="1296" width="1080" height="140" fill="#060e1c"/>
        </svg>""",
        """const st = document.getElementById("P-stars");
        let s = 4040; const r = () => ((s = (s * 1664525 + 1013904223) % 4294967296) / 4294967296);
        for (let i = 0; i < 26; i++) {
          const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
          c.setAttribute("cx", (60 + r() * 960).toFixed(0)); c.setAttribute("cy", (780 + r() * 360).toFixed(0));
          c.setAttribute("r", (1.5 + r() * 2.5).toFixed(1)); st.appendChild(c);
          tl.fromTo(c, { opacity: 0.15 }, { opacity: 0.95, duration: 0.7 + r() * 0.6, ease: "sine.inOut", yoyo: true, repeat: 3 }, 0.3 + r() * 0.8);
        }
        tl.fromTo("#P-moon", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 1.4, ease: "sine.out" }, 0.4);
        // Light rising from the place of prayer.
        tl.fromTo("#P-light", { opacity: 0, scaleY: 0.6, svgOrigin: "540 1300" }, { opacity: 1, scaleY: 1.1, duration: 2.6, ease: "sine.inOut" }, 1.4);""",
    ),
}


def point_scene(i, num, parts, art):
    sid = f"p{i + 1}"
    P = sid
    markup, js = ART[art]
    markup = markup.replace("P-", f"{P}-")
    js = js.replace("P-", f"{P}-")
    head = "\n".join(
        f'      <div class="{cls}" id="{P}-h{k}">{text}</div>' for k, (text, cls) in enumerate(parts)
    )
    return f"""<template>
  <style>{BASE_CSS}  </style>
  <div id="root" data-composition-id="{sid}" data-width="1080" data-height="1920">
    <div class="bg" id="{P}-bg"></div>
    <div id="{P}-art">
    {markup}
    </div>
    <div class="chip" id="{P}-chip"><span><b>{num}</b> / 08</span></div>
    <div class="head" id="{P}-head">
{head}
    </div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#{P}-bg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: "sine.out" }}, 0);
      tl.fromTo("#{P}-chip", {{ opacity: 0, y: -10 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }}, 0.15);
      {"".join(f'''tl.fromTo("#{P}-h{k}", {{ opacity: 0, y: 18, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.7, ease: "power2.out" }}, {0.3 + k * 0.35:.2f});
      ''' for k in range(len(parts)))}
      {js}
      // Dissolve to midnight before the next point.
      tl.to(["#{P}-art", "#{P}-chip", "#{P}-head"], {{ opacity: 0, duration: 0.4, ease: "sine.in" }}, {SCENE - 0.45:.2f});
      tl.set({{}}, {{}}, {SCENE});
      window.__timelines["{sid}"] = tl;
    }})();
  </script>
</template>
"""


HOOK_SCENE = """<template>
  <style>""" + BASE_CSS + """
    #hk-ring { position: absolute; left: 250px; top: 450px; width: 580px; height: 580px; border-radius: 50%;
      border: 2px solid rgba(226,189,114,.35);
      background: repeating-conic-gradient(from 0deg, rgba(226,189,114,.5) 0deg .8deg, rgba(0,0,0,0) .8deg 30deg);
      -webkit-mask-image: radial-gradient(circle, transparent 64%, #000 65%, #000 70%, transparent 71%);
      mask-image: radial-gradient(circle, transparent 64%, #000 65%, #000 70%, transparent 71%); }
    #hk-top { position: absolute; left: 0; right: 0; top: 330px; text-align: center; font-family: "Montserrat", sans-serif;
      font-weight: 700; font-size: 58px; letter-spacing: .14em; color: #f6eedf; }
    #hk-40 { position: absolute; left: 0; right: 0; top: 520px; text-align: center; font-family: "Playfair Display", serif;
      font-size: 360px; line-height: 1; color: #f0cd84; text-shadow: 0 0 90px rgba(233,163,91,.45); }
    #hk-tahun { position: absolute; left: 0; right: 0; top: 1070px; text-align: center; font-family: "Montserrat", sans-serif;
      font-weight: 700; font-size: 58px; letter-spacing: .3em; color: #f6eedf; }
    #hk-q { position: absolute; left: 0; right: 0; top: 1170px; text-align: center; font-family: "Playfair Display", serif;
      font-style: italic; font-size: 78px; color: #fbf6ec; text-shadow: 0 3px 24px rgba(4,10,22,.8); }
  </style>
  <div id="root" data-composition-id="hook" data-width="1080" data-height="1920">
    <div class="bg" id="hk-bg"></div>
    <div id="hk-ring"></div>
    <div id="hk-top">SELEPAS UMUR</div>
    <div id="hk-40">40</div>
    <div id="hk-tahun">TAHUN,</div>
    <div id="hk-q">kekayaan sebenar adalah…</div>
  </div>
  <script>
    (function () {
      const tl = gsap.timeline({ paused: true });
      // Frame 0 is the thumbnail: the age is already on screen.
      tl.fromTo("#hk-ring", { rotation: 0, opacity: 0.6 }, { rotation: 40, opacity: 1, duration: 5.0, ease: "none" }, 0);
      tl.fromTo("#hk-40", { scale: 1.06 }, { scale: 1, duration: 5.0, ease: "sine.out" }, 0);
      tl.fromTo("#hk-q", { opacity: 0, y: 20, filter: "blur(10px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.0, ease: "power2.out" }, 1.4);
      tl.to(["#hk-ring", "#hk-top", "#hk-40", "#hk-tahun", "#hk-q"], { opacity: 0, duration: 0.45, ease: "sine.in" }, 5.0);
      tl.set({}, {}, 5.5);
      window.__timelines["hook"] = tl;
    })();
  </script>
</template>
"""

QUOTE_SCENE = """<template>
  <style>""" + BASE_CSS + """
    #qt-img { position: absolute; left: 0; top: 0; width: 1080px; height: 1387px; opacity: .55; }
    #qt-shade { position: absolute; inset: 0;
      background: linear-gradient(180deg, rgba(11,26,48,.55) 0%, rgba(11,26,48,.78) 45%, #0b1a30 72%, #070f1d 100%); }
    #qt-text { position: absolute; left: 0; right: 0; top: 560px; padding: 0 100px; text-align: center; }
    .qt-a { font-family: "Montserrat", sans-serif; font-weight: 600; font-size: 52px; line-height: 1.25; color: #f6eedf;
      text-shadow: 0 3px 24px rgba(4,10,22,.8); }
    .qt-b { margin: 26px 0; font-family: "Playfair Display", serif; font-style: italic; font-size: 86px; line-height: 1.15;
      color: #f0cd84; text-shadow: 0 0 50px rgba(233,163,91,.4), 0 3px 24px rgba(4,10,22,.8); }
  </style>
  <div id="root" data-composition-id="quote" data-width="1080" data-height="1920">
    <div class="bg" id="qt-bg"></div>
    <img id="qt-img" src="assets/img/keluarga.jpg" alt="" />
    <div id="qt-shade"></div>
    <div id="qt-text">
      <div class="qt-a" id="qt-1">Bila usia semakin meningkat,</div>
      <div class="qt-b" id="qt-2">hidup yang sederhana tetapi tenang</div>
      <div class="qt-a" id="qt-3">terasa jauh lebih berharga.</div>
    </div>
  </div>
  <script>
    (function () {
      const tl = gsap.timeline({ paused: true });
      tl.fromTo("#qt-bg", { opacity: 0 }, { opacity: 1, duration: 0.4 }, 0);
      tl.fromTo("#qt-img", { opacity: 0, scale: 1.0 }, { opacity: 0.55, scale: 1.06, duration: 5.0, ease: "sine.out" }, 0);
      tl.fromTo("#qt-1", { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.7, ease: "power2.out" }, 0.4);
      tl.fromTo("#qt-2", { opacity: 0, y: 18, filter: "blur(8px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.0, ease: "power2.out" }, 1.4);
      tl.fromTo("#qt-3", { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.7, ease: "power2.out" }, 2.8);
      tl.to(["#qt-img", "#qt-text"], { opacity: 0, duration: 0.4, ease: "sine.in" }, 5.05);
      tl.set({}, {}, 5.5);
      window.__timelines["quote"] = tl;
    })();
  </script>
</template>
"""


def recap_scene():
    rows = []
    for k, (num, parts, _) in enumerate(POINTS):
        text = " ".join(t for t, _ in parts)
        rows.append(
            f'      <div class="rc-row" id="rc-r{k}" style="top:{470 + k * 98}px"><span class="rc-n">{num}</span>'
            f'<span class="rc-t">{text}</span></div>'
        )
    return """<template>
  <style>""" + BASE_CSS + """
    #rc-h1 { position: absolute; left: 0; right: 0; top: 236px; text-align: center; font-family: "Montserrat", sans-serif;
      font-weight: 700; font-size: 44px; letter-spacing: .16em; color: #f6eedf; }
    #rc-h2 { position: absolute; left: 0; right: 0; top: 300px; text-align: center; font-family: "Playfair Display", serif;
      font-style: italic; font-size: 92px; color: #f0cd84; text-shadow: 0 0 50px rgba(233,163,91,.4); }
    .rc-row { position: absolute; left: 130px; right: 110px; height: 80px; display: flex; align-items: center; }
    .rc-n { flex: 0 0 66px; height: 66px; border-radius: 50%; border: 2px solid rgba(240,205,132,.9); background: rgba(8,18,34,.6);
      font-family: "Montserrat", sans-serif; font-weight: 700; font-size: 28px; color: #f0cd84;
      display: flex; align-items: center; justify-content: center; }
    .rc-t { margin-left: 28px; font-family: "Montserrat", sans-serif; font-weight: 600; font-size: 38px; color: #f6eedf; }
    #rc-tag { position: absolute; left: 0; right: 0; top: 1272px; text-align: center; font-family: "Montserrat", sans-serif;
      font-weight: 600; font-size: 32px; letter-spacing: .08em; color: rgba(246,238,223,.8); }
  </style>
  <div id="root" data-composition-id="recap" data-width="1080" data-height="1920">
    <div class="bg" id="rc-bg"></div>
    <div id="rc-h1">SELEPAS UMUR 40 TAHUN,</div>
    <div id="rc-h2">kekayaan sebenar…</div>
""" + "\n".join(rows) + """
    <div id="rc-tag">#nasihatharini</div>
  </div>
  <script>
    (function () {
      const tl = gsap.timeline({ paused: true });
      tl.fromTo("#rc-bg", { opacity: 0 }, { opacity: 1, duration: 0.4 }, 0);
      tl.fromTo(["#rc-h1", "#rc-h2"], { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.7, ease: "power2.out", stagger: 0.2 }, 0.2);
      for (let k = 0; k < 8; k++) {
        tl.fromTo("#rc-r" + k, { opacity: 0, x: -24 }, { opacity: 1, x: 0, duration: 0.5, ease: "power2.out" }, 0.8 + k * 0.18);
      }
      tl.fromTo("#rc-tag", { opacity: 0 }, { opacity: 1, duration: 0.6 }, 2.5);
      tl.set({}, {}, """ + str(RECAP) + """);
      window.__timelines["recap"] = tl;
    })();
  </script>
</template>
"""


def main():
    comp = ROOT / "compositions"
    comp.mkdir(exist_ok=True)
    (comp / "hook.html").write_text(HOOK_SCENE)
    hosts = [("hook", 0.0, HOOK)]
    t = HOOK
    for i, (num, parts, art) in enumerate(POINTS):
        (comp / f"p{i + 1}.html").write_text(point_scene(i, num, parts, art))
        hosts.append((f"p{i + 1}", t, SCENE))
        t += SCENE
    (comp / "quote.html").write_text(QUOTE_SCENE)
    hosts.append(("quote", t, QUOTE))
    t += QUOTE
    (comp / "recap.html").write_text(recap_scene())
    hosts.append(("recap", t, RECAP))
    t += RECAP
    total = round(t, 2)

    host_html = "\n".join(
        f'      <div id="{h}" data-composition-id="{h}" data-composition-src="compositions/{h}.html" '
        f'data-start="{s:g}" data-duration="{d:g}" data-track-index="1" data-track-kind="graphics" style="z-index: 2"></div>'
        for h, s, d in hosts
    )
    index = f"""<!doctype html>
<html lang="ms">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #0b1a30; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
      #bg {{ position: absolute; inset: 0;
        background: radial-gradient(110% 70% at 50% 42%, #16305a 0%, #0b1a30 58%, #050c18 100%); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total:g}" data-width="1080" data-height="1920">
      <div id="bg"></div>
{host_html}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      tl.set({{}}, {{}}, {total:g});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    (ROOT / "index.html").write_text(index)
    print("total", total, "s;", len(hosts), "scenes")


if __name__ == "__main__":
    main()
