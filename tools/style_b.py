"""Style Kuliah Versi 2 (Konsep B "Mihrab Emas"): alternative cover + more animated overlay for build_clip.py.

Selected per clip with  "style": "V2"  (or the older "B") in the spec. Same palette (emerald / gold / navy) and fonts
as the approved style; adds a mihrab-arch cover, progress bar with chapter dots, numbered cards with
word-by-word reveals and a countdown bar, word-by-word Arabic, drifting light particles and an
interactive CTA outro (suka / simpan / kongsi / ikuti).
"""
import html

W, H = 1080, 1920
OUTRO_B = 4.4   # seconds of CTA outro after speech


def esc(s):
    return html.escape(s, quote=True)


def words_html(text, cls):
    return " ".join(f'<span class="{cls}">{esc(w)}</span>' for w in text.split())


STAR8 = ('<svg viewBox="-50 -50 100 100" width="{s}" height="{s}"><g fill="none" stroke="#D5B36A" stroke-width="{sw}">'
         '<rect x="-30" y="-30" width="60" height="60"/><rect x="-30" y="-30" width="60" height="60" transform="rotate(45)"/>'
         '<circle r="15"/></g></svg>')

ICON = {
    "suka": '<path d="M0 14 C-22 -2 -16 -20 -6 -20 C-2 -20 0 -16 0 -14 C0 -16 2 -20 6 -20 C16 -20 22 -2 0 14Z"/>',
    "simpan": '<path d="M-12 -18 H12 V20 L0 10 L-12 20Z"/>',
    "kongsi": '<path d="M-14 6 V16 H14 V6 M0 8 V-16 M-9 -8 L0 -17 L9 -8"/>',
}


def overlay(spec, speech_dur, D, cover_end, title_html, font_faces):
    ep = spec.get("episode")
    ep_txt = f"EP {int(ep):02d}" if ep else ""
    # ---- cover title lines (auto-fit like the approved cover, max 112 px) ----
    def line_html(line):
        txt = " ".join(seg["t"] for seg in line)
        em = sum(0.98 if c in "MW" else 0.36 if c in "I!:.,'" else 0.30 if c == " " else 0.72 if c in "?&" else 0.80 for c in txt)
        fs = int(min(112, 940 / max(em, 1)))
        segs = " ".join(
            (f'<span class="g"><i class="mk"></i><b>{esc(seg["t"])}</b></span>' if seg.get("gold")
             else f'<span class="w">{esc(seg["t"])}</span>') for seg in line)
        return f'<div class="cb-line" style="font-size:{fs}px">{segs}</div>'
    cover_lines = "".join(line_html(l) for l in spec.get("cover_lines", spec["title_lines"]))

    # ---- chapter dots on the progress bar ----
    beats = sorted([p["at"] for p in spec.get("points", [])] + [a["at"] for a in spec.get("arabic", [])])
    span = max(1.0, speech_dur - cover_end)
    dots, dot_js = [], []
    for i, t in enumerate(beats):
        x = 60 + 960 * max(0.0, min(1.0, (t - cover_end) / span))
        dots.append(f'<div class="pb-dot" id="pbd{i}" style="left:{x - 9:.1f}px"></div>')
        dot_js.append(f'tl.fromTo("#pbd{i}", {{scale:1, backgroundColor:"#22324A"}}, {{scale:1.45, backgroundColor:"#FFE16B", duration:.25, ease:"back.out(3)"}}, {t:.2f});')
        dot_js.append(f'tl.to("#pbd{i}", {{scale:1, duration:.3, ease:"power2.out"}}, {t + 0.3:.2f});')

    # ---- cards ----
    cards, js = [], []
    for i, p in enumerate(spec.get("points", [])):
        cid = f"pt{i + 1}"
        a, d = p["at"], p["dur"]
        cards.append(f"""
      <div id="{cid}" class="clip card" data-start="{a}" data-duration="{d}" data-track-index="{2 + i}">
        <div class="card-in">
          <div class="shine"></div>
          <div class="card-row">
            <div class="num"><span>{i + 1:02d}</span></div>
            <div class="card-body">
              <div class="card-label">{esc(p.get('label', f'POIN {i + 1}'))}</div>
              <div class="card-text">{words_html(p['text'], 'cw')}</div>
            </div>
          </div>
          <div class="timer"><div class="timer-fill"></div></div>
        </div>
      </div>""")
        js += [
            f'tl.fromTo("#{cid} .card-in", {{opacity:0, x:120, rotationY:-18}}, {{opacity:1, x:0, rotationY:0, duration:.55, ease:"power3.out"}}, {a + 0.02:.2f});',
            f'tl.fromTo("#{cid} .num", {{scale:0, rotation:-120}}, {{scale:1, rotation:0, duration:.5, ease:"back.out(2.2)"}}, {a + 0.18:.2f});',
            f'tl.fromTo("#{cid} .card-label", {{opacity:0, x:-24}}, {{opacity:1, x:0, duration:.35, ease:"power2.out"}}, {a + 0.3:.2f});',
            f'tl.fromTo("#{cid} .cw", {{opacity:0, y:26}}, {{opacity:1, y:0, duration:.3, ease:"power2.out", stagger:.055}}, {a + 0.4:.2f});',
            f'tl.fromTo("#{cid} .shine", {{x:-420}}, {{x:1250, duration:.9, ease:"power2.inOut"}}, {a + 0.45:.2f});',
            f'tl.fromTo("#{cid} .timer-fill", {{scaleX:1}}, {{scaleX:0, duration:{max(0.5, d - 0.6):.2f}, ease:"none"}}, {a + 0.2:.2f});',
            f'tl.to("#{cid} .card-in", {{opacity:0, x:-80, duration:.35, ease:"power2.in"}}, {a + d - 0.4:.2f});',
        ]
    for i, ar in enumerate(spec.get("arabic", [])):
        aid = f"ar{i + 1}"
        a, d = ar["at"], ar["dur"]
        fs = 62 if len(ar['ar']) < 45 else (50 if len(ar['ar']) < 75 else 42)
        cards.append(f"""
      <div id="{aid}" class="clip card" data-start="{a}" data-duration="{d}" data-track-index="{6 + i}">
        <div class="card-in ar-card">
          <div class="orn"><i class="ol"></i><span class="od"></span><i class="ol"></i></div>
          <div class="ar-text" dir="rtl" lang="ar" style="font-size:{fs}px">{words_html(ar['ar'], 'aw')}</div>
          <div class="ar-ms" style="font-size:{34 if len(ar['ms']) < 80 else 28}px">{words_html(ar['ms'], 'mw')}</div>
          {f'<div class="ar-ref">{esc(ar["ref"])}</div>' if ar.get('ref') else ''}
          <div class="timer"><div class="timer-fill"></div></div>
        </div>
      </div>""")
        n_ar = len(ar['ar'].split())
        js += [
            f'tl.fromTo("#{aid} .card-in", {{opacity:0, scale:.9, y:30}}, {{opacity:1, scale:1, y:0, duration:.55, ease:"power3.out"}}, {a + 0.02:.2f});',
            f'tl.fromTo("#{aid} .ol", {{scaleX:0}}, {{scaleX:1, duration:.6, ease:"power2.out"}}, {a + 0.2:.2f});',
            f'tl.fromTo("#{aid} .od", {{scale:0, rotation:0}}, {{scale:1, rotation:225, duration:.6, ease:"back.out(2)"}}, {a + 0.2:.2f});',
            f'tl.fromTo("#{aid} .aw", {{opacity:0, y:-18, scale:1.25}}, {{opacity:1, y:0, scale:1, duration:.4, ease:"power2.out", stagger:{min(0.35, 2.4 / max(1, n_ar)):.3f}}}, {a + 0.4:.2f});',
            f'tl.fromTo("#{aid} .mw", {{opacity:0}}, {{opacity:1, duration:.25, ease:"none", stagger:.04}}, {a + 0.9 + min(2.4, 0.35 * n_ar):.2f});',
            f'tl.fromTo("#{aid} .ar-ref", {{opacity:0, y:14}}, {{opacity:1, y:0, duration:.5, ease:"power2.out"}}, {a + 1.6 + min(2.4, 0.35 * n_ar):.2f});',
            f'tl.fromTo("#{aid} .timer-fill", {{scaleX:1}}, {{scaleX:0, duration:{max(0.5, d - 0.6):.2f}, ease:"none"}}, {a + 0.2:.2f});',
            f'tl.to("#{aid} .card-in", {{opacity:0, scale:.96, duration:.35, ease:"power2.in"}}, {a + d - 0.4:.2f});',
        ]

    # ---- drifting light particles (deterministic) ----
    parts, part_js = [], []
    for i in range(16):
        x = (i * 263 + 97) % 1000 + 40
        y = (i * 389 + 211) % 900 + 260
        s = 5 + (i * 7) % 9
        parts.append(f'<div class="pt" id="pp{i}" style="left:{x}px;top:{y}px;width:{s}px;height:{s}px"></div>')
        dy = -(140 + (i * 53) % 220)
        part_js.append(f'tl.fromTo("#pp{i}", {{y:0, opacity:0}}, {{y:{dy}, opacity:{0.35 + (i % 4) * 0.12:.2f}, duration:{D / 2:.2f}, ease:"sine.inOut", yoyo:true, repeat:1}}, 0);')

    lt_at, lt_dur = spec.get("lower_third_at", 5.6), 5.5
    o0 = speech_dur - 0.2
    cta_js = []
    for k, name in enumerate(["suka", "simpan", "kongsi"]):
        t = speech_dur + 0.9 + 0.32 * k
        cta_js += [
            f'tl.fromTo("#bt-{name}", {{scale:0, opacity:0}}, {{scale:1, opacity:1, duration:.4, ease:"back.out(2.4)"}}, {speech_dur + 0.5 + 0.1 * k:.2f});',
            f'tl.to("#bt-{name} .bc", {{scale:.84, duration:.09, ease:"power2.in"}}, {t:.2f});',
            f'tl.to("#bt-{name} .bc", {{scale:1, duration:.3, ease:"back.out(3)"}}, {t + 0.09:.2f});',
            f'tl.fromTo("#bt-{name} .rp", {{scale:.6, opacity:.9}}, {{scale:2.1, opacity:0, duration:.6, ease:"power2.out"}}, {t + 0.05:.2f});',
            f'tl.to("#bt-{name} .bc", {{backgroundColor:"#D5B36A", duration:.15}}, {t + 0.05:.2f});',
            f'tl.to("#bt-{name} svg g", {{fill:"#081726", stroke:"#081726", duration:.15}}, {t + 0.05:.2f});',
        ]
    tf = speech_dur + 2.0
    cta_js += [
        f'tl.fromTo("#follow", {{y:40, opacity:0}}, {{y:0, opacity:1, duration:.4, ease:"power3.out"}}, {speech_dur + 1.3:.2f});',
        f'tl.to("#follow", {{scale:.9, duration:.1, ease:"power2.in"}}, {tf:.2f});',
        f'tl.to("#follow", {{scale:1, backgroundColor:"#D5B36A", borderColor:"#D5B36A", duration:.35, ease:"back.out(3)"}}, {tf + 0.1:.2f});',
        f'tl.to("#fl-a", {{opacity:0, y:-20, duration:.2}}, {tf + 0.1:.2f});',
        f'tl.fromTo("#fl-b", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:.25}}, {tf + 0.15:.2f});',
        f'tl.fromTo("#follow-rp", {{scale:.8, opacity:.8}}, {{scale:1.6, opacity:0, duration:.7, ease:"power2.out"}}, {tf + 0.1:.2f});',
    ]
    btns = "".join(f"""
          <div class="bt" id="bt-{n}"><div class="rp"></div><div class="bc"><svg viewBox="-24 -24 48 48" width="58" height="58"><g fill="none" stroke="#D5B36A" stroke-width="3.4" stroke-linejoin="round" stroke-linecap="round">{ICON[n]}</g></svg></div><div class="bl">{n.upper()}</div></div>"""
                   for n in ["suka", "simpan", "kongsi"])

    return f"""<template>
  <style>
    {font_faces}
    #root {{ position: absolute; inset: 0; font-family: "Montserrat", "Amiri", sans-serif; color: #fff; }}
    #ov-topscrim {{ position: absolute; left: 0; top: 0; width: 1080px; height: 720px;
      background: linear-gradient(180deg, rgba(8,23,38,.94) 0%, rgba(8,23,38,.75) 36%, rgba(7,59,53,.2) 74%, rgba(8,23,38,0) 100%); }}
    #ov-botscrim {{ position: absolute; left: 0; top: 1060px; width: 1080px; height: 860px;
      background: linear-gradient(180deg, rgba(8,23,38,0) 0%, rgba(8,23,38,.55) 25%, rgba(8,23,38,.92) 60%, #081726 100%); }}
    #ov-pattern {{ position: absolute; left: 0; top: 1500px; width: 1080px; height: 420px; opacity: .16;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'%3E%3Cg fill='none' stroke='%23D5B36A' stroke-width='1.4'%3E%3Crect x='30' y='30' width='60' height='60'/%3E%3Crect x='30' y='30' width='60' height='60' transform='rotate(45 60 60)'/%3E%3Ccircle cx='60' cy='60' r='14'/%3E%3C/g%3E%3C/svg%3E");
      -webkit-mask-image: linear-gradient(180deg, transparent, #000 60%); mask-image: linear-gradient(180deg, transparent, #000 60%); }}
    .pt {{ position: absolute; border-radius: 50%; background: radial-gradient(circle, #FFE16B 0%, rgba(213,179,106,.0) 70%); opacity: 0; }}
    /* progress bar */
    #pb {{ position: absolute; left: 60px; top: 176px; width: 960px; height: 8px; }}
    #pb-track {{ position: absolute; inset: 0; border-radius: 4px; background: rgba(255,255,255,.16); }}
    #pb-fill {{ position: absolute; inset: 0; border-radius: 4px; background: linear-gradient(90deg, #D5B36A, #FFE16B); transform-origin: 0 50%; }}
    .pb-dot {{ position: absolute; top: -5px; width: 18px; height: 18px; border-radius: 50%; background: #22324A; border: 3px solid #D5B36A; }}
    /* header */
    #header {{ position: absolute; left: 60px; top: 212px; width: 960px; }}
    #hd-row {{ display: flex; align-items: center; gap: 14px; }}
    .ep {{ padding: 7px 14px; border-radius: 10px; background: #D5B36A; color: #081726; font-weight: 900; font-size: 26px; letter-spacing: .1em; }}
    .chip {{ padding: 7px 16px; border: 2px solid #D5B36A; border-radius: 40px; color: #D5B36A; font-weight: 800; font-size: 26px;
      letter-spacing: .14em; background: rgba(7,59,53,.55); }}
    #header-title {{ margin-top: 14px; width: 860px; font-weight: 900; font-size: 44px; line-height: 1.12; text-shadow: 0 4px 16px rgba(0,0,0,.6); }}
    #header-title .g {{ color: #FFE16B; }}
    /* cards */
    .card {{ position: absolute; left: 60px; top: 390px; width: 960px; perspective: 1200px; }}
    .card-in {{ position: relative; overflow: hidden; background: rgba(8,23,38,.86); border: 1.5px solid rgba(213,179,106,.6);
      border-radius: 24px; padding: 26px 30px 34px; box-shadow: 0 18px 50px rgba(0,0,0,.45); }}
    .shine {{ position: absolute; top: -40px; left: 0; width: 160px; height: 400px; transform: rotate(18deg);
      background: linear-gradient(90deg, rgba(255,225,107,0), rgba(255,225,107,.28), rgba(255,225,107,0)); }}
    .card-row {{ display: flex; gap: 24px; align-items: flex-start; }}
    .num {{ flex: 0 0 auto; width: 84px; height: 84px; border-radius: 50%; background: linear-gradient(135deg, #FFE16B, #D5B36A);
      color: #081726; font-weight: 900; font-size: 36px; display: flex; align-items: center; justify-content: center;
      box-shadow: 0 0 0 6px rgba(213,179,106,.22); }}
    .card-label {{ color: #D5B36A; font-weight: 800; font-size: 28px; letter-spacing: .16em; }}
    .card-text {{ margin-top: 8px; font-weight: 800; font-size: 44px; line-height: 1.18; }}
    .cw {{ display: inline-block; }}
    .timer {{ position: absolute; left: 30px; right: 30px; bottom: 14px; height: 5px; border-radius: 3px; background: rgba(255,255,255,.12); }}
    .timer-fill {{ position: absolute; inset: 0; border-radius: 3px; background: #D5B36A; transform-origin: 0 50%; }}
    .ar-card {{ text-align: center; padding-top: 18px; }}
    .orn {{ display: flex; align-items: center; justify-content: center; gap: 14px; }}
    .ol {{ display: block; width: 220px; height: 2px; background: #D5B36A; }}
    .orn .ol:first-child {{ transform-origin: 100% 50%; }} .orn .ol:last-child {{ transform-origin: 0 50%; }}
    .od {{ display: block; width: 16px; height: 16px; border: 2px solid #FFE16B; transform: rotate(45deg); }}
    .ar-text {{ margin-top: 8px; font-family: "Amiri", serif; font-weight: 700; line-height: 1.5; color: #FFE16B; }}
    .aw, .mw {{ display: inline-block; }}
    .ar-ms {{ margin-top: 6px; font-weight: 600; line-height: 1.3; }}
    .ar-ref {{ margin-top: 10px; font-weight: 800; font-size: 26px; color: #D5B36A; letter-spacing: .08em; }}
    /* lower third */
    #lt {{ position: absolute; left: 60px; top: 990px; width: 940px; }}
    #lt-in {{ display: flex; align-items: center; gap: 16px; }}
    #lt-icon {{ width: 74px; height: 74px; border-radius: 50%; background: #081726; border: 3px solid #D5B36A; display: flex; align-items: center; justify-content: center; }}
    #lt-box {{ position: relative; padding: 10px 22px 14px; background: rgba(8,23,38,.88); border-radius: 12px; overflow: hidden; }}
    #lt-name {{ font-weight: 900; font-size: 36px; }}
    #lt-role {{ font-weight: 600; font-size: 24px; color: #D5B36A; letter-spacing: .06em; margin-top: 2px; }}
    #lt-line {{ position: absolute; left: 0; bottom: 0; width: 100%; height: 4px; background: #D5B36A; transform-origin: 0 50%; }}
    /* cover B */
    #cover {{ position: absolute; inset: 0; }}
    #cb-vig {{ position: absolute; inset: 0;
      background: radial-gradient(ellipse 620px 760px at 540px 820px, rgba(8,23,38,0) 55%, rgba(8,23,38,.75) 100%),
                  linear-gradient(180deg, rgba(8,23,38,.92) 0%, rgba(8,23,38,.35) 16%, rgba(8,23,38,0) 30%); }}
    #cb-arch {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform-origin: 540px 800px; }}
    #cb-top {{ position: absolute; left: 0; top: 196px; width: 1080px; text-align: center; }}
    #cb-kicker {{ color: #D5B36A; font-weight: 800; font-size: 28px; letter-spacing: .26em; }}
    #cb-ep {{ position: absolute; right: 66px; top: 300px; width: 128px; height: 128px; border-radius: 50%;
      background: linear-gradient(135deg, #FFE16B, #D5B36A); color: #081726; display: flex; flex-direction: column;
      align-items: center; justify-content: center; box-shadow: 0 0 0 8px rgba(213,179,106,.25), 0 12px 30px rgba(0,0,0,.5); }}
    #cb-ep small {{ font-weight: 900; font-size: 28px; letter-spacing: .2em; margin-left: .2em; }}
    #cb-ep b {{ font-weight: 900; font-size: 52px; line-height: 1; }}
    #cb-panel {{ position: absolute; left: 0; top: 1090px; width: 1080px; height: 830px; }}
    #cb-panel-bg {{ position: absolute; inset: 0; }}
    #cb-chip {{ position: absolute; left: 0; top: 34px; width: 1080px; text-align: center; }}
    #cb-chip span {{ display: inline-block; padding: 12px 32px; border-radius: 40px; background: #D5B36A; color: #081726;
      font-weight: 900; font-size: 28px; letter-spacing: .16em; box-shadow: 0 8px 24px rgba(0,0,0,.4); }}
    #cb-title {{ position: absolute; left: 60px; top: 120px; width: 960px; text-align: center; }}
    .cb-line {{ font-weight: 900; line-height: 1.06; letter-spacing: -.01em; color: #fff; text-shadow: 0 6px 0 rgba(0,0,0,.3); }}
    .cb-line .g {{ position: relative; display: inline-block; color: #081726; padding: 0 .12em; }}
    .cb-line .g b {{ position: relative; font-weight: 900; }}
    .cb-line .g .mk {{ position: absolute; left: 0; right: 0; top: .1em; bottom: .02em; background: linear-gradient(90deg, #FFE16B, #D5B36A);
      border-radius: .14em; transform: skewX(-8deg); transform-origin: 0 50%; }}
    #cb-who {{ position: absolute; left: 0; top: 560px; width: 1080px; text-align: center; }}
    #cb-name {{ font-weight: 900; font-size: 34px; }}
    #cb-place {{ margin-top: 6px; color: #D5B36A; font-weight: 600; font-size: 24px; letter-spacing: .08em; }}
    #cb-play {{ position: absolute; left: 0; top: 680px; width: 1080px; text-align: center; }}
    #cb-play span {{ display: inline-block; padding: 12px 30px; border: 2px solid rgba(213,179,106,.8); border-radius: 40px;
      color: #FFE16B; font-weight: 800; font-size: 28px; letter-spacing: .18em; }}
    /* outro / CTA */
    #outro {{ position: absolute; inset: 0; background: radial-gradient(circle at 540px 760px, #0B3B37 0%, #081726 62%); }}
    #outro-in {{ position: absolute; left: 0; top: 420px; width: 1080px; display: flex; flex-direction: column; align-items: center; }}
    #outro-series {{ margin-top: 26px; color: #D5B36A; font-weight: 800; font-size: 30px; letter-spacing: .2em; }}
    #outro-title {{ margin-top: 16px; width: 900px; text-align: center; font-weight: 900; font-size: 50px; line-height: 1.12; }}
    #outro-title .g {{ color: #FFE16B; }}
    #btns {{ margin-top: 70px; display: flex; gap: 64px; }}
    .bt {{ position: relative; display: flex; flex-direction: column; align-items: center; }}
    .bc {{ width: 116px; height: 116px; border-radius: 50%; border: 3px solid #D5B36A; background: rgba(8,23,38,.6);
      display: flex; align-items: center; justify-content: center; }}
    .rp {{ position: absolute; left: 0; top: 0; width: 116px; height: 116px; border-radius: 50%; border: 3px solid #FFE16B; opacity: 0; }}
    .bl {{ margin-top: 12px; font-weight: 800; font-size: 28px; letter-spacing: .16em; color: #D5B36A; }}
    #follow {{ position: relative; margin-top: 60px; width: 420px; height: 92px; border-radius: 46px; border: 3px solid #FFE16B;
      background: rgba(8,23,38,.4); color: #081726; }}
    #follow-rp {{ position: absolute; inset: -3px; border-radius: 46px; border: 3px solid #FFE16B; opacity: 0; }}
    #fl-a, #fl-b {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
      font-weight: 900; font-size: 34px; letter-spacing: .18em; }}
    #fl-a {{ color: #FFE16B; }}
    #fl-b {{ opacity: 0; }}
  </style>
  <div id="root" data-composition-id="overlay" data-width="{W}" data-height="{H}">
    <div id="ov-topscrim"></div>
    <div id="ov-botscrim"></div>
    <div id="ov-pattern"></div>
    {''.join(parts)}

    <div id="pbw" class="clip" data-start="{cover_end}" data-duration="{round(speech_dur - cover_end, 2)}" data-track-index="11">
      <div id="pb"><div id="pb-track"></div><div id="pb-fill"></div>{''.join(dots)}</div>
    </div>

    <div id="cover" class="clip" data-start="0" data-duration="{cover_end + 0.4}" data-track-index="0">
      <div id="cover-in" style="position:absolute;inset:0">
        <div id="cb-vig"></div>
        <svg id="cb-arch" viewBox="0 0 1080 1920" width="1080" height="1920">
          <g fill="none" stroke="#D5B36A">
            <path d="M190 1150 V700 C190 520 330 400 540 290 C750 400 890 520 890 700 V1150" stroke-width="7"/>
            <path d="M216 1150 V706 C216 540 346 428 540 322 C734 428 864 540 864 706 V1150" stroke-width="2" stroke-opacity=".6"/>
            <circle cx="540" cy="262" r="16" fill="#D5B36A"/>
          </g>
        </svg>
        <div id="cb-top"><div id="cb-kicker">{esc(spec.get('cover_kicker', ''))}</div></div>
        {f'<div id="cb-ep"><small>EP</small><b>{int(ep):02d}</b></div>' if ep else ''}
        <div id="cb-panel">
          <svg id="cb-panel-bg" viewBox="0 0 1080 830" width="1080" height="830" preserveAspectRatio="none">
            <defs><linearGradient id="cbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0B3B37"/><stop offset=".45" stop-color="#081726"/><stop offset="1" stop-color="#081726"/></linearGradient></defs>
            <path d="M0 60 Q540 -40 1080 60 V830 H0Z" fill="url(#cbg)"/>
            <path d="M0 60 Q540 -40 1080 60" fill="none" stroke="#D5B36A" stroke-width="5"/>
          </svg>
          <div id="cb-chip"><span>{esc(spec['category'])}</span></div>
          <div id="cb-title">{cover_lines}</div>
          <div id="cb-who"><div id="cb-name">{esc(spec['speaker'])}</div><div id="cb-place">{esc(spec.get('cover_sub', ''))}</div></div>
          <div id="cb-play"><span>&#9654; TONTON SAMPAI HABIS</span></div>
        </div>
      </div>
    </div>

    <div id="header" class="clip" data-start="{cover_end - 0.1}" data-duration="{round(speech_dur - cover_end + 0.1, 2)}" data-track-index="1">
      <div id="header-in">
        <div id="hd-row">{f'<div class="ep">{ep_txt}</div>' if ep else ''}<div class="chip">{esc(spec['category'])}</div></div>
        <div id="header-title">{spec.get('header_html') or title_html}</div>
      </div>
    </div>
    {''.join(cards)}

    <div id="lt" class="clip" data-start="{lt_at}" data-duration="{lt_dur}" data-track-index="9">
      <div id="lt-in">
        <div id="lt-icon">{STAR8.format(s=50, sw=5)}</div>
        <div id="lt-box"><div id="lt-name">{esc(spec['speaker'])}</div><div id="lt-role">{esc(spec['speaker_role'])}</div><div id="lt-line"></div></div>
      </div>
    </div>

    <div id="outro" class="clip" data-start="{o0}" data-duration="{round(D - o0, 2)}" data-track-index="10">
      <div id="outro-in">
        <div id="outro-star">{STAR8.format(s=130, sw=2.6)}</div>
        <div id="outro-series">{esc(spec['series'])}</div>
        <div id="outro-title">{title_html}</div>
        <div id="btns">{btns}
        </div>
        <div id="follow"><div id="follow-rp"></div><div id="fl-a">+ IKUTI</div><div id="fl-b">&#10003; DIIKUTI</div></div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {chr(10).join('    ' + c for c in part_js).strip()}
    // cover: complete at frame 0 (thumbnail); marker sweeps, then the camera passes through the arch
    tl.fromTo("#cb-title", {{scale: 1}}, {{scale: 1.035, duration: {cover_end}, ease: "none"}}, 0);
    tl.fromTo("#cb-arch", {{scale: 1}}, {{scale: 1.03, duration: {cover_end - 0.5}, ease: "none"}}, 0);
    tl.fromTo("#cb-ep", {{rotation: -8}}, {{rotation: 6, duration: {cover_end}, ease: "sine.inOut"}}, 0);
    tl.to(".cb-line", {{y: 60, opacity: 0, duration: .35, ease: "power2.in", stagger: .06}}, {cover_end - 0.45});
    tl.to("#cb-panel", {{y: 860, duration: .5, ease: "power3.in"}}, {cover_end - 0.3});
    tl.to("#cb-arch", {{scale: 3.2, opacity: 0, duration: .6, ease: "power2.in"}}, {cover_end - 0.4});
    tl.to("#cb-top, #cb-ep, #cb-vig", {{opacity: 0, duration: .4, ease: "power2.in"}}, {cover_end - 0.3});
    // header + progress
    tl.fromTo("#hd-row > div", {{opacity: 0, y: -16}}, {{opacity: 1, y: 0, duration: .35, ease: "back.out(2)", stagger: .08}}, {cover_end + 0.2});
    tl.fromTo("#header-title", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: .45, ease: "power2.out"}}, {cover_end + 0.35});
    tl.fromTo("#pb", {{opacity: 0}}, {{opacity: 1, duration: .3}}, {cover_end + 0.05});
    tl.fromTo("#pb-fill", {{scaleX: 0}}, {{scaleX: 1, duration: {round(speech_dur - cover_end, 2)}, ease: "none"}}, {cover_end});
    {chr(10).join('    ' + c for c in dot_js).strip()}
    {chr(10).join('    ' + c for c in js).strip()}
    // lower third
    tl.fromTo("#lt-icon", {{scale: 0, rotation: -180}}, {{scale: 1, rotation: 0, duration: .5, ease: "back.out(2)"}}, {lt_at + 0.02});
    tl.fromTo("#lt-icon svg", {{rotation: 0}}, {{rotation: 90, duration: {lt_dur}, ease: "none"}}, {lt_at});
    tl.fromTo("#lt-box", {{opacity: 0, clipPath: "inset(0 100% 0 0)"}}, {{opacity: 1, clipPath: "inset(0 0% 0 0)", duration: .5, ease: "power3.out"}}, {lt_at + 0.2});
    tl.fromTo("#lt-line", {{scaleX: 0}}, {{scaleX: 1, duration: .6, ease: "power2.out"}}, {lt_at + 0.5});
    tl.to("#lt-in", {{opacity: 0, x: -20, duration: .35, ease: "power2.in"}}, {lt_at + lt_dur - 0.4});
    // outro CTA
    tl.fromTo("#outro", {{opacity: 0}}, {{opacity: 1, duration: .5, ease: "power2.inOut"}}, {o0});
    tl.fromTo("#outro-star svg", {{scale: .5, rotation: -90}}, {{scale: 1, rotation: 0, duration: 1.0, ease: "power3.out"}}, {speech_dur});
    tl.fromTo("#outro-series", {{opacity: 0, y: 16}}, {{opacity: 1, y: 0, duration: .4, ease: "power2.out"}}, {speech_dur + 0.15});
    tl.fromTo("#outro-title", {{opacity: 0, y: 16}}, {{opacity: 1, y: 0, duration: .4, ease: "power2.out"}}, {speech_dur + 0.25});
    {chr(10).join('    ' + c for c in cta_js).strip()}
    window.__timelines["overlay"] = tl;
  </script>
</template>
"""
