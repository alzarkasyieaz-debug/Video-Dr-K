#!/usr/bin/env python3
"""Ceramah Politik style engine.

Reads <project>/edit.json + data/words.json + data/camera.json (+ data/music.json) and writes
index.html and compositions/*.html in the Ceramah Politik look: navy/gold broadcast cards,
Anton/Bebas Neue/Montserrat type, kinetic word captions, tracked digital camera, dip cuts with
light sweeps.

Usage: python3 build.py [project_dir]
"""
import html, json, os, sys

PROJECT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
W, H = 1080, 1920
GRADE = {"preset": "deep-contrast", "intensity": 0.45,
         "adjust": {"exposure": 0.06, "highlights": -0.3, "shadows": 0.14, "temperature": -0.08,
                    "saturation": -0.05, "blacks": -0.03},
         "details": {"vignette": 0.36, "vignetteFeather": 0.7, "grain": 0.12, "grainSize": 0.3}}
SFX_PEAK = {"impact-bass-1": 0.073, "whoosh-cinematic": 2.503, "whoosh": 0.162, "whoosh-short": 0.162, "riser": 3.472}
SFX_LEN = {"impact-bass-1": 2.0, "whoosh-cinematic": 3.2, "whoosh": 0.5, "whoosh-short": 0.5, "riser": 3.8}


def load(p, default=None):
    p = os.path.join(PROJECT, p)
    return json.load(open(p)) if os.path.exists(p) else default


EDIT = load("edit.json")
WORDS = load("data/words.json", [])
CAMERA = load("data/camera.json", {})
MUSIC = load("data/music.json")

# timeline: clips play back to back
CLIPS, t = [], 0.0
for c in EDIT["clips"]:
    d = round(c["out"] - c["in"], 3)
    CLIPS.append({**c, "start": round(t, 3), "dur": d})
    t += d
SPEECH_END = round(t, 3)
TOTAL = round(SPEECH_END + EDIT.get("end_card", 3.8), 3)
CUTS = [c["start"] for c in CLIPS[1:]]


def r(x):
    return round(float(x), 3)


def esc(s):
    return html.escape(s, quote=False)


def word_time(text, after=0.0):
    for w in WORDS:
        if w["start"] >= after - 1e-6 and w["text"].strip(".,?!“”\"").lower() == text.lower():
            return w["start"]
    raise KeyError(f"word '{text}' after {after}s not found in data/words.json")


def at(a, default=None):
    """Resolve a time anchor to output seconds.
    number | {"word": w, "after": s, "offset": d} | {"cut": n, "offset": d} | {"speech_end": true, "offset": d}"""
    if a is None:
        return default
    if isinstance(a, (int, float)):
        return float(a)
    off = a.get("offset", 0.0)
    if "word" in a:
        return word_time(a["word"], a.get("after", 0.0)) + off
    if "cut" in a:
        return CUTS[a["cut"] - 1] + off
    if a.get("speech_end"):
        return SPEECH_END + off
    raise ValueError(a)


# --------------------------------------------------------------------------------------- style
FONT_FACE = """
      @font-face { font-family: "Anton"; src: url("assets/fonts/anton-latin-400-normal.woff2") format("woff2"); font-weight: 400; }
      @font-face { font-family: "Bebas Neue"; src: url("assets/fonts/bebas-neue-latin-400-normal.woff2") format("woff2"); font-weight: 400; }"""

TOKENS = """
      #root {
        --navy: #0a1630; --navy-deep: #050b1a; --gold: #d9a93a; --gold-bright: #f4c95d;
        --ink: #ffffff; --hl: #ffd84a;
        position: absolute; inset: 0; overflow: visible;
      }"""

CARD_CSS = """
      .dim { position: absolute; left: 0; top: 0; width: 1080px; height: 860px;
        background: linear-gradient(180deg, rgba(5,11,26,.88) 0%, rgba(5,11,26,.74) 55%, rgba(5,11,26,0) 100%); opacity: 0; }
      .kicker { font-family: "Bebas Neue", sans-serif; font-size: 44px; letter-spacing: .14em; color: var(--gold-bright); }
      .gline { height: 4px; background: linear-gradient(90deg, var(--gold-bright), var(--gold) 70%, rgba(217,169,58,0)); transform-origin: 0 50%; }
      .gline.c { transform-origin: 50% 50%; background: linear-gradient(90deg, rgba(217,169,58,0), var(--gold-bright), rgba(217,169,58,0)); }
      .hl { font-family: "Anton", sans-serif; color: var(--ink); line-height: 1.02; text-transform: uppercase;
        text-shadow: 0 6px 30px rgba(0,0,0,.55); }
      .bebas { font-family: "Bebas Neue", sans-serif; letter-spacing: .04em; }
      .gold { color: var(--gold-bright); }
      .w { display: inline-block; }
      .mask { display: block; overflow: hidden; padding: 0 6px 6px 0; }
      .sub { font-family: "Montserrat", sans-serif; font-weight: 600; font-size: 34px; line-height: 1.3; color: rgba(255,255,255,.9); }
      .src { font-family: "Montserrat", sans-serif; font-weight: 500; font-size: 28px; color: rgba(255,255,255,.72); }
      .party { position: absolute; top: 40px; width: 360px; height: 180px; display: flex; align-items: center; justify-content: center;
        font-family: "Anton", sans-serif; font-size: 118px; color: #fff; letter-spacing: .02em;
        background: linear-gradient(180deg, rgba(10,22,48,.92), rgba(5,11,26,.92)); border: 3px solid var(--gold); border-radius: 10px;
        box-shadow: 0 18px 50px rgba(0,0,0,.5), inset 0 0 0 1px rgba(244,201,93,.25); }
      .row { display: flex; align-items: baseline; justify-content: space-between; height: 104px; }
      .lab { font-family: "Bebas Neue", sans-serif; font-size: 70px; letter-spacing: .06em; color: #fff; }
      .num { font-family: "Anton", sans-serif; font-size: 92px; color: #fff; }
      .num small { font-family: "Bebas Neue", sans-serif; font-size: 50px; letter-spacing: .08em; }
      .tot { height: 150px; }
      .tot .num { font-size: 116px; }
      .sweepbox { position: absolute; left: -14px; right: -14px; top: 18px; bottom: 6px; background: rgba(244,201,93,.18);
        border-left: 6px solid var(--gold-bright); transform-origin: 0 50%; }
      .card { position: absolute; left: 108px; top: 312px; width: 864px; display: flex; gap: 30px; align-items: center; }
      .card .cnum { font-family: "Anton", sans-serif; font-size: 150px; line-height: 1; color: var(--gold-bright); min-width: 150px; }
      .card .t { font-size: 96px; }
      .hlword { position: relative; display: inline-block; }
      .hlword .bar { position: absolute; left: -8px; right: -8px; top: 6px; bottom: 2px; background: var(--gold); transform-origin: 0 50%; opacity: .55; }
      .dust { position: absolute; border-radius: 50%; background: rgba(255,226,140,.9); box-shadow: 0 0 10px 3px rgba(244,201,93,.45); }
      .spk-name:empty { display: none; }
"""


def scene_file(cid, body, script, css=CARD_CSS, motion_blur=False):
    mb = ' data-motion-blur="on"' if motion_blur else ""
    return f"""<template>
  <style>{FONT_FACE}{TOKENS}{css}
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


def reveal(sel, t, stagger=0.08, y=40, blur=8):
    return (f'    tl.fromTo("{sel}", {{ opacity: 0, y: {y}, filter: "blur({blur}px)" }}, '
            f'{{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.42, ease: "expo.out", stagger: {stagger} }}, {r(t)});\n')


def exit_blur(sel, t, d=0.28):
    return f'    tl.to("{sel}", {{ opacity: 0, filter: "blur(10px)", duration: {d}, ease: "power3.in" }}, {r(t)});\n'


def fade(sel, t, to, d=0.4, ease="power2.out", frm=0):
    return f'    tl.fromTo("{sel}", {{ opacity: {frm} }}, {{ opacity: {to}, duration: {d}, ease: "{ease}" }}, {r(t)});\n'


def kicker_in(sel, t):
    return f'    tl.fromTo("{sel}", {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "expo.out" }}, {r(t)});\n'


def line_in(sel, t, d=0.6):
    return f'    tl.fromTo("{sel}", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {d}, ease: "power3.inOut" }}, {r(t)});\n'


def spans(text, cls, gold_all=False):
    return " ".join(f'<span class="w {cls}{" gold" if gold_all else ""}">{esc(x)}</span>' for x in text.split())


def rich(text):
    """'*word*' -> gold span."""
    out = []
    for tok in text.split():
        g = tok.startswith("*") or tok.endswith("*")
        out.append((tok.strip("*"), g))
    return out


# ------------------------------------------------------------------------------ overlay types
# Each returns (body, script, (abs_start, abs_end)); `o` is the scene's absolute start.
class Ctx:
    def __init__(self, sid, o):
        self.sid, self.o, self.track = sid, o, 0

    def tr(self):
        self.track += 1
        return self.track - 1


def ov_headline(ov, ctx, k):
    o, p = ctx.o, f"{ctx.sid}{k}"
    end = at(ov["end"])
    qa, ans = ov.get("question"), ov.get("answer")
    lines = "".join(
        f'      <div class="mask"><div id="{p}-l{i}" class="hl{" gold" if ln.get("gold") else ""}" style="font-size:{ln.get("size", 150)}px;">{esc(ln["text"])}</div></div>\n'
        for i, ln in enumerate(ov["lines"]))
    qa_html = ""
    if qa:
        qa_html = f"""      <div style="position:relative;height:126px;">
        <div id="{p}-q" data-layout-allow-overlap class="hl bebas" style="position:absolute;left:0;top:10px;font-size:96px;">{spans(qa["text"], p + "-qw")}</div>
"""
        if ans:
            qa_html += f"""        <div id="{p}-a" data-layout-allow-overlap class="hl" style="position:absolute;left:0;top:0;font-size:110px;white-space:nowrap;">
          <span class="bebas" style="font-size:96px;">{esc(ans["lead"])}</span>
          <span style="position:relative;display:inline-block;margin-left:8px;"><span id="{p}-sw" style="position:absolute;left:-10px;right:-10px;top:14px;bottom:4px;background:linear-gradient(90deg,var(--gold),var(--gold-bright));transform-origin:0 50%;"></span><span id="{p}-aw" class="w" style="position:relative;color:var(--navy-deep);padding:0 8px;">{esc(ans["word"])}</span></span>
        </div>
"""
        qa_html += "      </div>\n"
    dur = r(end + 0.32 - o)
    body = f"""    <div id="{p}-dim" class="dim clip" data-start="0" data-duration="{dur}" data-track-index="{ctx.tr()}"></div>
    <div id="{p}" class="clip" data-start="0" data-duration="{dur}" data-track-index="{ctx.tr()}"
         style="position:absolute;left:100px;top:236px;width:880px;">
{lines}      <div id="{p}-line" class="gline" style="width:520px;margin:18px 0 22px;"></div>
{qa_html}    </div>"""
    s = fade(f"#{p}-dim", 0, 0.8, 1.2, frm=0.55)
    s += f'    tl.fromTo("#{p}-l0", {{ scale: 1.1, opacity: 1, filter: "blur(3px)", transformOrigin: "0% 60%" }}, {{ scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.55, ease: "expo.out" }}, 0);\n'
    for i in range(1, len(ov["lines"])):
        s += f'    tl.fromTo("#{p}-l{i}", {{ yPercent: 105 }}, {{ yPercent: 0, duration: 0.6, ease: "expo.out" }}, {r(0.32 * i)});\n'
    s += line_in(f"#{p}-line", 0.55, 0.7)
    if qa:
        s += reveal(f".{p}-qw", at(qa["at"]) - o - 0.05, stagger=qa.get("stagger", 0.2), y=26, blur=6)
    if ans:
        ta = at(ans["at"]) - o
        s += f'    tl.set("#{p}-a", {{ opacity: 0 }}, 0);\n    tl.set("#{p}-a", {{ opacity: 1 }}, {r(ta - 0.02)});\n'
        s += f'    tl.to("#{p}-q", {{ opacity: 0, filter: "blur(8px)", duration: 0.12, ease: "power2.in" }}, {r(ta - 0.14)});\n'
        s += f'    tl.fromTo("#{p}-sw", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.22, ease: "power3.out" }}, {r(ta - 0.02)});\n'
        s += f'    tl.fromTo("#{p}-aw", {{ scale: 1.35, filter: "blur(8px)", opacity: 0 }}, {{ scale: 1, filter: "blur(0px)", opacity: 1, duration: 0.3, ease: "expo.out", transformOrigin: "0% 50%" }}, {r(ta)});\n'
    s += exit_blur(f"#{p}", end - o, 0.24)
    s += f'    tl.to("#{p}-dim", {{ opacity: 0, duration: 0.3, ease: "power2.in" }}, {r(end - o - 0.03)});\n'
    return body, s, (o, end + 0.32)


def ov_keypoint(ov, ctx, k):
    o, p = ctx.o, f"{ctx.sid}{k}"
    t0 = at(ov["at"]) - o
    hold = ov.get("hold", 4.0)
    lines = "".join(
        f'      <div class="hl" style="font-size:{ln.get("size", 92)}px;">{spans(ln["text"], p + "-w", ln.get("gold"))}</div>\n'
        for ln in ov["lines"])
    body = f"""    <div id="{p}-dim" class="dim clip" data-start="{r(t0 - 0.3)}" data-duration="{r(hold + 0.65)}" data-track-index="{ctx.tr()}"></div>
    <div id="{p}" class="clip" data-start="{r(t0 - 0.2)}" data-duration="{r(hold + 0.55)}" data-track-index="{ctx.tr()}"
         style="position:absolute;left:108px;top:236px;width:864px;">
      <div class="kicker" id="{p}-k">{esc(ov["kicker"])}</div>
      <div id="{p}-gl" class="gline" style="width:640px;margin:12px 0 22px;"></div>
{lines}    </div>"""
    s = fade(f"#{p}-dim", t0 - 0.3, 1)
    s += kicker_in(f"#{p}-k", t0 - 0.2) + line_in(f"#{p}-gl", t0 - 0.15)
    s += reveal(f".{p}-w", t0, stagger=0.11)
    s += exit_blur(f"#{p}", t0 + hold, 0.3)
    s += f'    tl.to("#{p}-dim", {{ opacity: 0, duration: 0.35, ease: "power2.in" }}, {r(t0 + hold + 0.05)});\n'
    return body, s, (o + t0 - 0.3, o + t0 + hold + 0.4)


def ov_versus(ov, ctx, k):
    o, p = ctx.o, f"{ctx.sid}{k}"
    tl_, tr_ = at(ov["left_at"]) - o, at(ov["right_at"]) - o
    hold = ov.get("hold", 1.8)
    body = f"""    <div id="{p}" class="clip" data-start="{r(tl_ - 0.4)}" data-duration="{r(tr_ - tl_ + hold + 0.4)}" data-track-index="{ctx.tr()}"
         style="position:absolute;left:108px;top:300px;width:864px;height:260px;">
      <div id="{p}-l" class="party" style="left:0;">{esc(ov["left"])}</div>
      <div id="{p}-x" class="hl gold" style="position:absolute;left:0;width:864px;top:58px;text-align:center;font-size:120px;">{esc(ov.get("join", "+"))}</div>
      <div id="{p}-r" class="party" style="right:0;">{esc(ov["right"])}</div>
    </div>"""
    s = f'    tl.fromTo("#{p}-l", {{ x: -420, filter: "blur(14px)", opacity: 0 }}, {{ x: 0, filter: "blur(0px)", opacity: 1, duration: 0.5, ease: "expo.out" }}, {r(tl_ - 0.05)});\n'
    s += f'    tl.fromTo("#{p}-r", {{ x: 420, filter: "blur(14px)", opacity: 0 }}, {{ x: 0, filter: "blur(0px)", opacity: 1, duration: 0.5, ease: "expo.out" }}, {r(tr_ - 0.05)});\n'
    s += f'    tl.fromTo("#{p}-x", {{ scale: 0.4, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.35, ease: "back.out(1.6)" }}, {r(tr_ + 0.15)});\n'
    s += exit_blur(f"#{p}", tr_ + hold, 0.3)
    return body, s, (o + tl_ - 0.4, o + tr_ + hold + 0.3)


def ov_stat(ov, ctx, k):
    o, p = ctx.o, f"{ctx.sid}{k}"
    st, end = at(ov.get("start", o)) - o, at(ov["end"]) - o
    rows = ""
    for i, row in enumerate(ov["rows"]):
        rows += f'      <div class="row" id="{p}-r{i}"><span class="lab">{esc(row["label"])}</span><span class="num">{esc(row["value"])} <small>{esc(row.get("unit", ""))}</small></span></div>\n'
    tot = ov.get("total")
    tot_html = ""
    if tot:
        tot_html = f"""      <div id="{p}-div" class="gline" style="width:864px;margin:8px 0 6px;"></div>
      <div class="row tot" id="{p}-rt"><span class="lab gold">{esc(tot["label"])}</span>
        <span class="num gold" style="position:relative;"><span class="sweepbox" id="{p}-sw"></span><span style="position:relative;">{esc(tot["value"])} <small>{esc(tot.get("unit", ""))}</small></span></span></div>
"""
    src = f'      <div class="src" id="{p}-src" style="margin-top:14px;">{esc(ov["source"])}</div>\n' if ov.get("source") else ""
    body = f"""    <div id="{p}-dim" class="dim clip" data-start="{r(st)}" data-duration="{r(end - st + 0.4)}" data-track-index="{ctx.tr()}"></div>
    <div id="{p}" class="clip" data-start="{r(st)}" data-duration="{r(end - st + 0.4)}" data-track-index="{ctx.tr()}"
         style="position:absolute;left:108px;top:214px;width:864px;">
      <div class="kicker" id="{p}-k">{esc(ov["kicker"])}</div>
      <div id="{p}-gl" class="gline" style="width:864px;margin:12px 0 18px;"></div>
{rows}{tot_html}{src}    </div>"""
    s = fade(f"#{p}-dim", st, 1) + kicker_in(f"#{p}-k", st + 0.05) + line_in(f"#{p}-gl", st + 0.1, 0.7)
    for i, row in enumerate(ov["rows"]):
        t = at(row["at"]) - o
        s += f'    tl.fromTo("#{p}-r{i} .lab", {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "expo.out" }}, {r(t - 0.35)});\n'
        s += f'    tl.fromTo("#{p}-r{i} .num", {{ opacity: 0, yPercent: 60, filter: "blur(10px)" }}, {{ opacity: 1, yPercent: 0, filter: "blur(0px)", duration: 0.45, ease: "expo.out" }}, {r(t - 0.04)});\n'
    if tot:
        td = at(ov.get("divider_at"), at(tot["at"]) - 0.6) - o
        tt = at(tot["at"]) - o
        s += line_in(f"#{p}-div", td)
        s += f'    tl.fromTo("#{p}-rt .lab", {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "expo.out" }}, {r(td + 0.2)});\n'
        s += f'    tl.fromTo("#{p}-rt .num", {{ opacity: 0, scale: 1.3, filter: "blur(10px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.4, ease: "expo.out", transformOrigin: "100% 60%" }}, {r(tt - 0.03)});\n'
        s += f'    tl.fromTo("#{p}-sw", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.45, ease: "power3.out" }}, {r(tt + 0.15)});\n'
    if src:
        s += fade(f"#{p}-src", at(ov["rows"][0]["at"]) - o + 0.6, 1, 0.5)
    s += exit_blur(f"#{p}", end - 0.05, 0.3)
    s += f'    tl.to("#{p}-dim", {{ opacity: 0, duration: 0.4, ease: "power2.in" }}, {r(end)});\n'
    return body, s, (o + st, o + end + 0.4)


def ov_numbered(ov, ctx, k):
    o, p = ctx.o, f"{ctx.sid}{k}"
    tk, end = at(ov["start"]) - o, at(ov["end"]) - o
    body = f"""    <div id="{p}-dim" class="dim clip" data-start="{r(tk - 0.1)}" data-duration="{r(end - tk + 0.5)}" data-track-index="{ctx.tr()}"></div>
    <div id="{p}" class="clip" data-start="{r(tk)}" data-duration="{r(end - tk + 0.4)}" data-track-index="{ctx.tr()}"
         style="position:absolute;left:108px;top:214px;width:864px;">
      <div class="kicker" id="{p}-k">{esc(ov["kicker"])}</div>
      <div id="{p}-gl" class="gline" style="width:760px;margin:12px 0 0;"></div>
    </div>"""
    s = fade(f"#{p}-dim", tk - 0.1, 1) + kicker_in(f"#{p}-k", tk) + line_in(f"#{p}-gl", tk + 0.05, 0.7)
    for i, cd in enumerate(ov["cards"]):
        cid = f"{p}-c{i}"
        t = at(cd["at"]) - o
        te = at(cd["until"]) - o if cd.get("until") else end
        sub = esc(cd.get("sub", ""))
        if "{" in sub:
            a, rest = sub.split("{", 1)
            word, b = rest.split("}", 1)
            sub = f'{a}<span class="hlword" id="{cid}-hw"><span class="bar" id="{cid}-hb"></span><span style="position:relative;">{word}</span></span>{b}'
        sub_style = ' style="font-size:38px;font-weight:700;"' if cd.get("sub_big") else ""
        body += f"""
    <div id="{cid}" class="clip card" data-start="{r(t)}" data-duration="{r(te - t)}" data-track-index="{ctx.tr()}">
      <div class="cnum">{esc(cd["num"])}</div><div><div class="hl t">{esc(cd["title"])}</div><div class="sub"{sub_style}>{sub}</div></div>
    </div>"""
        s += f'    tl.fromTo("#{cid} .cnum", {{ opacity: 0, scale: 1.4, filter: "blur(10px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.45, ease: "expo.out" }}, {r(t)});\n'
        s += f'    tl.fromTo("#{cid} .t", {{ opacity: 0, clipPath: "inset(0 100% 0 0)" }}, {{ opacity: 1, clipPath: "inset(0 0% 0 0)", duration: 0.55, ease: "power3.out" }}, {r(t + 0.08)});\n'
        s += f'    tl.fromTo("#{cid} .sub", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "expo.out" }}, {r(t + 0.3)});\n'
        if "{" in cd.get("sub", ""):
            th = at(cd["highlight_at"]) - o
            s += f'    tl.fromTo("#{cid}-hb", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.4, ease: "power3.out" }}, {r(th)});\n'
            s += f'    tl.fromTo("#{cid}-hw", {{ scale: 1 }}, {{ keyframes: [{{ scale: 1.12, duration: 0.12 }}, {{ scale: 1, duration: 0.13 }}], ease: "power2.out" }}, {r(th)});\n'
        s += exit_blur(f"#{cid}", te - 0.26, 0.24)
    s += exit_blur(f"#{p}", end - 0.05, 0.28)
    s += f'    tl.to("#{p}-dim", {{ opacity: 0, duration: 0.35, ease: "power2.in" }}, {r(end)});\n'
    return body, s, (o + tk - 0.1, o + end + 0.4)


def ov_slam(ov, ctx, k):
    o, p = ctx.o, f"{ctx.sid}{k}"
    end = at(ov["end"]) - o
    tb, t2 = at(ov["big_at"]) - o, at(ov["second_at"]) - o
    lead = [w for w in WORDS if w["clip"] == ov["lead_clip"]][: ov.get("lead_words", 0)]
    lead_html = "".join(f'<span class="w" id="{p}-lw{i}">{esc(w["text"].strip(".,").upper())}</span> ' for i, w in enumerate(lead))
    lines = ""
    for i, ln in enumerate(ov.get("lines", [])):
        lines += ("<br>" if i else "") + spans(ln["text"], f"{p}-m{i}")
    body = f"""    <div id="{p}-glow" class="clip" data-start="{r(tb - 0.3)}" data-duration="{r(end - tb + 0.6)}" data-track-index="{ctx.tr()}" data-layout-ignore
         style="position:absolute;left:-200px;top:-80px;width:1480px;height:1100px;background:radial-gradient(ellipse at 50% 40%, rgba(244,201,93,.35), rgba(217,169,58,.08) 45%, rgba(0,0,0,0) 70%);mix-blend-mode:screen;opacity:0;"></div>
    <div id="{p}-dim" class="dim clip" data-start="0" data-duration="{r(end + 0.4)}" data-track-index="{ctx.tr()}"></div>
    <div id="{p}-a" class="clip" data-start="0.05" data-duration="{r(tb - 0.4)}" data-track-index="{ctx.tr()}"
         style="position:absolute;left:108px;top:250px;width:864px;">
      <div class="kicker">{esc(ov["kicker"])}</div>
      <div class="hl bebas" style="font-size:92px;letter-spacing:.03em;margin-top:10px;">{lead_html}</div>
    </div>
    <div id="{p}-b" class="clip" data-start="{r(tb - 0.05)}" data-duration="{r(end - tb + 0.2)}" data-track-index="{ctx.tr()}"
         style="position:absolute;left:60px;top:226px;width:960px;text-align:center;">
      <div class="hl gold" id="{p}-big" style="font-size:184px;">{esc(ov["big"])}</div>
      <div class="hl" id="{p}-sec" style="font-size:118px;margin-top:-6px;">{esc(ov["second"])}</div>
      <div id="{p}-gl" class="gline c" style="width:640px;margin:18px auto 14px;"></div>
      <div class="hl bebas" style="font-size:70px;letter-spacing:.06em;">{lines}</div>
    </div>"""
    s = fade(f"#{p}-dim", 0, 0.85)
    for i, w in enumerate(lead):
        s += f'    tl.fromTo("#{p}-lw{i}", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.13, ease: "power2.out" }}, {r(max(0.06, w["start"] - o - 0.02))});\n'
    s += exit_blur(f"#{p}-a", tb - 0.7, 0.25)
    s += f'    tl.fromTo("#{p}-big", {{ scale: 1.45, opacity: 0, filter: "blur(14px)" }}, {{ scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.32, ease: "expo.out" }}, {r(tb)});\n'
    s += f'    tl.fromTo("#{p}-sec", {{ opacity: 0, yPercent: 40, filter: "blur(8px)" }}, {{ opacity: 1, yPercent: 0, filter: "blur(0px)", duration: 0.4, ease: "expo.out" }}, {r(t2 - 0.02)});\n'
    s += line_in(f"#{p}-gl", t2 + 0.2)
    s += f'    tl.fromTo("#{p}-glow", {{ opacity: 0 }}, {{ keyframes: [{{ opacity: 1, duration: 0.18 }}, {{ opacity: 0.45, duration: 1.4 }}], ease: "power2.out" }}, {r(tb - 0.02)});\n'
    for i, ln in enumerate(ov.get("lines", [])):
        s += reveal(f".{p}-m{i}", at(ln["at"]) - o - 0.02, stagger=ln.get("stagger", 0.25), y=20, blur=6)
    s += exit_blur(f"#{p}-b", end - 0.12, 0.26)
    s += f'    tl.to("#{p}-glow", {{ opacity: 0, duration: 0.4, ease: "power2.in" }}, {r(end - 0.2)});\n'
    s += f'    tl.to("#{p}-dim", {{ opacity: 0, duration: 0.3, ease: "power2.in" }}, {r(end)});\n'
    return body, s, (o, o + end + 0.4)


def ov_words(ov, ctx, k):
    """Kicker + lines whose words land on their own spoken times."""
    o, p = ctx.o, f"{ctx.sid}{k}"
    first = min(at(w["at"]) for ln in ov["lines"] for w in ln["words"]) - o
    end = at(ov["end"]) - o
    lines, s_words = "", ""
    n = 0
    for ln in ov["lines"]:
        parts = []
        for w in ln["words"]:
            parts.append(f'<span class="w" id="{p}-w{n}">{esc(w["text"])}</span>')
            s_words += f'    tl.fromTo("#{p}-w{n}", {{ opacity: 0, filter: "blur(8px)", y: 30 }}, {{ opacity: 1, filter: "blur(0px)", y: 0, duration: 0.4, ease: "expo.out" }}, {r(at(w["at"]) - o - 0.03)});\n'
            n += 1
        lines += f'      <div class="hl{" gold" if ln.get("gold") else ""}" style="font-size:{ln.get("size", 96)}px;">{" ".join(parts)}</div>\n'
    body = f"""    <div id="{p}-dim" class="dim clip" data-start="{r(first - 0.3)}" data-duration="{r(end - first + 0.65)}" data-track-index="{ctx.tr()}"></div>
    <div id="{p}" class="clip" data-start="{r(first - 0.15)}" data-duration="{r(end - first + 0.45)}" data-track-index="{ctx.tr()}"
         style="position:absolute;left:108px;top:236px;width:864px;">
      <div class="kicker" id="{p}-k">{esc(ov["kicker"])}</div>
      <div id="{p}-gl" class="gline" style="width:640px;margin:12px 0 20px;"></div>
{lines}    </div>"""
    s = fade(f"#{p}-dim", first - 0.3, 1) + kicker_in(f"#{p}-k", first - 0.15) + line_in(f"#{p}-gl", first - 0.1) + s_words
    s += exit_blur(f"#{p}", end, 0.28)
    s += f'    tl.to("#{p}-dim", {{ opacity: 0, duration: 0.3, ease: "power2.in" }}, {r(end + 0.15)});\n'
    return body, s, (o + first - 0.3, o + end + 0.35)


def ov_final(ov, ctx, k):
    o, p = ctx.o, f"{ctx.sid}{k}"
    se = SPEECH_END - o
    fin, end = se + 0.05, TOTAL - o
    seed, dots = 7, []
    for _ in range(12):
        seed = (seed * 1103515245 + 12345) % 2 ** 31
        x = 80 + seed % 920
        seed = (seed * 1103515245 + 12345) % 2 ** 31
        y = 500 + seed % 900
        seed = (seed * 1103515245 + 12345) % 2 ** 31
        dots.append((x, y, 3 + seed % 5))
    dots_html = "\n".join(f'      <i class="dust" style="left:{x}px;top:{y}px;width:{z}px;height:{z}px;"></i>' for x, y, z in dots)
    lines = ""
    for ln in ov["lines"]:
        lines += '      <div class="hl" style="font-size:112px;">' + " ".join(
            f'<span class="w {p}-f{" gold" if g else ""}">{esc(t)}</span>' for t, g in rich(ln)) + "</div>\n"
    spk = EDIT.get("speaker", {})
    body = f"""    <div id="{p}-black" class="clip" data-start="{r(se - 0.35)}" data-duration="{r(end - se + 0.35)}" data-track-index="{ctx.tr()}"
         style="position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%, #0d1d3f 0%, #050b1a 60%, #000 100%);opacity:0;"></div>
    <div id="{p}-dust" class="clip" data-start="{r(fin)}" data-duration="{r(end - fin)}" data-track-index="{ctx.tr()}" data-layout-ignore style="position:absolute;inset:0;">
{dots_html}
    </div>
    <div id="{p}" class="clip" data-start="{r(fin)}" data-duration="{r(end - fin)}" data-track-index="{ctx.tr()}"
         style="position:absolute;left:108px;top:560px;width:864px;text-align:center;">
      <div class="kicker" id="{p}-k" style="font-size:46px;">{esc(ov.get("kicker", ""))}</div>
      <div id="{p}-gl" class="gline c" style="width:420px;margin:14px auto 34px;"></div>
{lines}      <div id="{p}-name" class="sub spk-name" style="margin-top:40px;font-size:40px;font-weight:800;color:#fff;" data-var-text="speakerName">{esc(spk.get("name", ""))}</div>
      <div id="{p}-role" class="src" style="margin-top:10px;font-size:32px;" data-var-text="speakerRole">{esc(spk.get("role", ""))}</div>
    </div>
    <div id="{p}-fade" class="clip" data-start="{r(end - 0.9)}" data-duration="0.9" data-track-index="{ctx.tr()}" style="position:absolute;inset:0;background:#000;opacity:0;"></div>"""
    s = f'    tl.fromTo("#{p}-black", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.7, ease: "power2.inOut" }}, {r(se - 0.35)});\n'
    s += line_in(f"#{p}-gl", fin + 0.1, 0.8)
    s += f'    tl.fromTo("#{p}-k", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.7, ease: "expo.out" }}, {r(fin)});\n'
    s += reveal(f".{p}-f", fin + 0.35, stagger=0.1, y=36, blur=10)
    s += f'    tl.fromTo("#{p}-name, #{p}-role", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "expo.out", stagger: 0.15 }}, {r(fin + 1.4)});\n'
    s += f'    tl.fromTo("#{p}-dust .dust", {{ opacity: 0, y: 0 }}, {{ opacity: 0.8, y: -160, duration: {r(end - fin)}, ease: "none", stagger: 0.06 }}, {r(fin)});\n'
    s += f'    tl.fromTo("#{p}-fade", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.85, ease: "power2.in" }}, {r(end - 0.9)});\n'
    return body, s, (o + se - 0.35, TOTAL)


OVERLAYS = {"headline": ov_headline, "keypoint": ov_keypoint, "versus": ov_versus, "stat": ov_stat,
            "numbered": ov_numbered, "slam": ov_slam, "words": ov_words, "final": ov_final}
MOTION_BLUR = {"headline", "keypoint", "versus", "slam"}


def overlay_start(ov):
    """Earliest absolute time an overlay needs (to place the scene host)."""
    tp = ov["type"]
    if tp == "headline":
        return 0.0
    if tp == "keypoint":
        return at(ov["at"]) - 0.35
    if tp == "versus":
        return at(ov["left_at"]) - 0.45
    if tp in ("stat",):
        return at(ov["start"])
    if tp == "numbered":
        return min([at(ov["start"]) - 0.1] + [at(c["at"]) for c in ov["cards"]])
    if tp == "slam":
        clip = next(c for c in CLIPS if c["id"] == ov["lead_clip"])
        return clip["start"]
    if tp == "words":
        return min(at(w["at"]) for ln in ov["lines"] for w in ln["words"]) - 0.35
    if tp == "final":
        return SPEECH_END - 0.4
    raise ValueError(tp)


def build_scene(sc):
    o = r(min(overlay_start(ov) for ov in sc["overlays"]))
    if sc["overlays"][0]["type"] == "slam":
        o = next(c for c in CLIPS if c["id"] == sc["overlays"][0]["lead_clip"])["start"]
    ctx = Ctx(sc["id"], o)
    bodies, scripts, ends = [], [], []
    for k, ov in enumerate(sc["overlays"]):
        b, s, (a, e) = OVERLAYS[ov["type"]](ov, ctx, k)
        bodies.append(b)
        scripts.append(s)
        ends.append(e)
    mb = any(ov["type"] in MOTION_BLUR for ov in sc["overlays"])
    end = min(TOTAL, max(ends))
    return scene_file(sc["id"], "\n".join(bodies), "".join(scripts), motion_blur=mb), o, r(end - o)


# ---------------------------------------------------------------------------------- captions
def caption_groups():
    groups, cur = [], []
    for w in WORDS:
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
    keys = {k.lower() for k in EDIT.get("keywords", [])}
    groups = caption_groups()
    clip_end = {c["id"]: c["start"] + c["dur"] for c in CLIPS}
    body, s = [], []
    for gi, g in enumerate(groups):
        g0 = max(0.12, g[0]["start"] - 0.06)
        nxt = groups[gi + 1][0]["start"] - 0.06 if gi + 1 < len(groups) else g[-1]["end"] + 0.6
        g1 = min(nxt, max(g[-1]["end"] + 0.45, g0 + 0.6), clip_end[g[0]["clip"]] - 0.02)
        sp = []
        for w in g:
            key = w["text"].strip(".,?!").lower() in keys
            sp.append(f'<span class="cw{" kw" if key else ""}" id="cap-{w["id"]}">{esc(w["text"])}</span>')
        body.append(f'    <div class="cg" id="cg-{gi}"><div class="cbox">{" ".join(sp)}</div></div>')
        s.append(f'    tl.set("#cg-{gi}", {{ opacity: 1, visibility: "visible" }}, {r(g0)});')
        for w in g:
            key = w["text"].strip(".,?!").lower() in keys
            ws = r(max(g0, w["start"] - 0.03))
            sel = f'#cap-{w["id"]}'
            s.append(f'    tl.fromTo("{sel}", {{ opacity: 0, scale: 0.95 }}, {{ opacity: 1, scale: 1, duration: 0.15, ease: "power2.out" }}, {ws});')
            if key:
                s.append(f'    tl.to("{sel}", {{ keyframes: [{{ scale: 1.12, duration: 0.11 }}, {{ scale: 1, duration: 0.14 }}], ease: "power2.out" }}, {r(ws + 0.02)});')
                s.append(f'    tl.set("{sel}", {{ color: "#f4c95d" }}, {ws});')
            else:
                s.append(f'    tl.set("{sel}", {{ color: "#ffd84a" }}, {ws});')
                s.append(f'    tl.set("{sel}", {{ color: "#ffffff" }}, {r(min(g1 - 0.01, max(w["end"], w["start"] + 0.12)))});')
        s.append(f'    tl.to("#cg-{gi}", {{ opacity: 0, duration: 0.1, ease: "power2.in" }}, {r(g1 - 0.1)});')
        s.append(f'    tl.set("#cg-{gi}", {{ opacity: 0, visibility: "hidden" }}, {r(g1)});')
    css = """
      #cap-wrap { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
      .cg { position: absolute; left: 0; right: 0; bottom: 618px; text-align: center; opacity: 0; visibility: hidden; }
      .cbox { display: inline-block; max-width: 900px; padding: 10px 26px 14px; border-radius: 18px; background: rgba(5,11,26,.38);
        font-family: "Montserrat", sans-serif; font-weight: 800; font-size: 70px; line-height: 1.18; color: #fff;
        -webkit-text-stroke: 9px #000; paint-order: stroke fill; text-shadow: 0 4px 18px rgba(0,0,0,.6); }
      .cw { display: inline-block; transform-origin: 50% 70%; }"""
    b = f'    <div id="cap-wrap" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="0">\n' + "\n".join(body) + "\n    </div>"
    return scene_file("captions", b, "\n".join(s) + "\n", css), len(groups)


# ------------------------------------------------------------------------------- shade / fx
def build_shade():
    body = f"""    <div id="sh-top" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="0" data-layout-ignore
         style="position:absolute;left:0;top:0;width:1080px;height:520px;background:linear-gradient(180deg,rgba(5,11,26,.78),rgba(5,11,26,.35) 55%,rgba(5,11,26,0));"></div>
    <div id="sh-bot" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="1" data-layout-ignore
         style="position:absolute;left:0;bottom:0;width:1080px;height:900px;background:linear-gradient(0deg,rgba(0,0,0,.82),rgba(5,11,26,.45) 45%,rgba(5,11,26,0));"></div>"""
    return scene_file("shade", body, "    tl.set({}, {}, 0);\n", "")


def build_fx():
    bug = EDIT.get("bug", "")
    parts = [esc(x.strip()) for x in bug.split("·")]
    bug_html = ' <span style="color:var(--gold-bright);">&middot;</span> '.join(parts)
    bug_end = SPEECH_END - 0.4
    sweeps = "\n".join(
        f'    <div id="fx-sw-{i}" class="clip sweep" data-start="{r(t - 0.35)}" data-duration="0.9" data-track-index="{3 + i}" data-layout-ignore></div>'
        for i, t in enumerate(CUTS))
    dips = "\n".join(
        f'    <div id="fx-dip-{i}" class="clip dip" data-start="{r(t - 0.12)}" data-duration="0.42" data-track-index="{3 + len(CUTS) + i}" data-layout-ignore></div>'
        for i, t in enumerate(CUTS))
    body = f"""    <div id="fx-bug" class="clip" data-start="0.4" data-duration="{r(bug_end - 0.4)}" data-track-index="2"
         style="position:absolute;left:108px;top:178px;">
      <span id="fx-bug-bar" style="display:inline-block;width:8px;height:30px;background:var(--gold-bright);vertical-align:-4px;margin-right:12px;"></span><span id="fx-bug-t" style="font-family:'Bebas Neue',sans-serif;font-size:34px;letter-spacing:.2em;color:rgba(255,255,255,.92);">{bug_html}</span>
    </div>
{sweeps}
{dips}"""
    css = """
      .sweep { position: absolute; left: -700px; top: -200px; width: 600px; height: 2400px; transform-origin: 50% 50%;
        background: linear-gradient(90deg, rgba(255,232,170,0), rgba(255,232,170,.38) 45%, rgba(255,255,255,.55) 50%, rgba(255,232,170,.38) 55%, rgba(255,232,170,0));
        mix-blend-mode: screen; opacity: 0; }
      .dip { position: absolute; inset: 0; background: #000; opacity: 0; }"""
    s = '    tl.fromTo("#fx-bug-bar", { scaleY: 0 }, { scaleY: 1, duration: 0.4, ease: "expo.out" }, 0.4);\n'
    s += '    tl.fromTo("#fx-bug-t", { opacity: 0, x: -20 }, { opacity: 1, x: 0, duration: 0.5, ease: "expo.out" }, 0.5);\n'
    s += f'    tl.to("#fx-bug", {{ opacity: 0, duration: 0.3, ease: "power2.in" }}, {r(bug_end - 0.3)});\n'
    for i, t in enumerate(CUTS):
        s += f'    tl.fromTo("#fx-sw-{i}", {{ x: 0, rotation: 18, opacity: 0.0 }}, {{ x: 2500, rotation: 18, opacity: 1, duration: 0.85, ease: "power2.inOut" }}, {r(t - 0.35)});\n'
        s += f'    tl.fromTo("#fx-dip-{i}", {{ opacity: 0 }}, {{ keyframes: [{{ opacity: 0.45, duration: 0.1 }}, {{ opacity: 0, duration: 0.3 }}], ease: "power2.out" }}, {r(t - 0.12)});\n'
    return scene_file("fx", body, s, css)


# ------------------------------------------------------------------------------------ index
def build_index(hosts):
    grade = json.dumps(GRADE, separators=(",", ":"))
    vids, cam = [], []
    for i, c in enumerate(CLIPS):
        cid = c["id"]
        vids.append(f"""      <div class="cam" id="cam-{cid}">
        <video id="clip-{cid}" class="clip" src="assets/footage/clip-{cid}.mp4" data-start="{c["start"]}" data-duration="{c["dur"]}"
               data-track-index="{1 + (i % 2)}" data-has-audio="true" data-volume="1" playsinline
               data-color-grading='{grade}'></video>
      </div>""")
        keys = CAMERA.get(cid, {}).get("keys")
        if keys:
            cam.append(f'      tl.set("#cam-{cid}", {{ x: {keys[0][1]}, y: {keys[0][2]}, scale: {keys[0][3]} }}, 0);')
            for k0, k1 in zip(keys, keys[1:]):
                cam.append(f'      tl.to("#cam-{cid}", {{ x: {k1[1]}, y: {k1[2]}, scale: {k1[3]}, duration: {r(k1[0] - k0[0])}, ease: "none" }}, {r(c["start"] + k0[0])});')
    audio = []
    if MUSIC:
        auto = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": MUSIC["automation"]}]}).replace('"', "&quot;")
        audio.append(f'      <audio id="score" src="{MUSIC["src"]}" data-start="0" data-duration="{TOTAL}" data-track-index="9" '
                     f'data-volume="1" data-fade-in="0.05" data-fade-out="2.2" data-automation="{auto}"></audio>')
    lanes = []  # end time per SFX track, so overlapping sounds never share a track
    for i, fx in enumerate(EDIT.get("sfx", [])):
        f = fx["file"]
        hit, peak = at(fx["at"]), SFX_PEAK.get(f, 0.0)
        st, ms = max(0.0, hit - peak), (peak - hit if hit < peak else 0.0)
        ln = fx.get("length", SFX_LEN.get(f, 2.0))
        lane = next((k for k, e in enumerate(lanes) if e <= st), None)
        if lane is None:
            lanes.append(0.0)
            lane = len(lanes) - 1
        lanes[lane] = st + ln
        msa = f' data-media-start="{r(ms)}"' if ms > 0 else ""
        audio.append(f'      <audio id="sfx-{i}-{f}" src="assets/sfx/{f}.mp3" data-start="{r(st)}" data-duration="{r(ln)}"{msa} '
                     f'data-track-index="{11 + lane}" data-volume="{fx.get("volume", 0.3)}" data-fade-out="0.25"></audio>')
    host_html = []
    for i, (hid, st, du, z) in enumerate(hosts):
        kind = "captions" if hid == "captions" else "graphics"
        host_html.append(f'      <div id="{hid}" class="clip host" data-composition-id="{hid}" data-composition-src="compositions/{hid}.html" '
                         f'data-start="{r(st)}" data-duration="{r(du)}" data-track-index="{20 + i}" data-track-kind="{kind}" '
                         f'data-width="{W}" data-height="{H}" style="z-index:{z};"></div>')
    nl = "\n"
    return f"""<!doctype html>
<html lang="{EDIT.get("lang", "ms")}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>{esc(EDIT.get("title", ""))}</title>
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
    <!-- Ceramah Politik style · generated by .claude/skills/ceramah-politik/scripts/build.py from edit.json -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}">
{nl.join(vids)}
{nl.join(host_html)}
{nl.join(audio)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      // Digital camera: smoothed speaker tracking + per-clip zoom profile (data/camera.json)
{nl.join(cam)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""


def main():
    os.makedirs(os.path.join(PROJECT, "compositions"), exist_ok=True)
    hosts = [("shade", 0, TOTAL, 20), ("fx", 0, TOTAL, 38)]
    for i, sc in enumerate(EDIT["scenes"]):
        html_, st, du = build_scene(sc)
        open(os.path.join(PROJECT, f"compositions/{sc['id']}.html"), "w").write(html_)
        hosts.append((sc["id"], st, du, 30 + i))
    cap, n = build_captions()
    open(os.path.join(PROJECT, "compositions/captions.html"), "w").write(cap)
    hosts.append(("captions", 0, TOTAL, 40))
    open(os.path.join(PROJECT, "compositions/shade.html"), "w").write(build_shade())
    open(os.path.join(PROJECT, "compositions/fx.html"), "w").write(build_fx())
    open(os.path.join(PROJECT, "index.html"), "w").write(build_index(hosts))
    print(f"Ceramah Politik: {len(EDIT['scenes'])} scenes, {n} caption groups, {TOTAL}s "
          f"({len(CLIPS)} clips, speech ends {SPEECH_END}s)")


if __name__ == "__main__":
    main()
