#!/usr/bin/env python3
"""Video MP — build a Malaysian Parliament speech short (1080x1920, HyperFrames) from one episode.json.

  python3 vmp.py init     <project_dir>   # folders, fonts, SFX, GSAP, hyperframes.json, episode.json stub
  python3 vmp.py segments <project_dir>   # cut + crop + level each speech clip, export the held last frame
  python3 vmp.py build    <project_dir>   # index.html, one scene per segment, end card, captions, SRTs

Every time in episode.json is SOURCE time (seconds into the original recording), the same clock as the
whisper transcript, so each card can be checked against the word it lands on. See ../SKILL.md.
"""
import html
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

# ── Design tokens (references/design.md) ────────────────────────────────────────
NAVY, GOLD, WHITE, GROUND, YELLOW = "#081A32", "#D6AC52", "#FFFFFF", "#080B13", "#FFD447"
COLORS = {"gold": GOLD, "yel": YELLOW, "white": WHITE}
PLATE_W, PLATE_H = 1080, 1440          # every speech clip is shown as a 3:4 plate
WIDE = 1.36                            # full-bleed framing of the plate
CAPTION_TOP = 1150                     # caption band 1150–1326 (TikTok safe, under the chin)
DIP = 0.1                              # dip-cut length before each seam

# ── helpers ─────────────────────────────────────────────────────────────────────
def load(project):
    with open(os.path.join(project, "episode.json")) as f:
        ep = json.load(f)
    t = 0.0
    for s in ep["segments"]:
        s["v0"] = round(t, 3)
        s["dur"] = round(s["src"][1] - s["src"][0], 3)
        t += s["dur"]
    ep["speech_end"] = round(t, 3)
    ep["total"] = round(t + ep["end"].get("duration", 6.5), 3)
    return ep


def v(seg, src_t):
    """source time → video time"""
    return round(src_t - seg["src"][0] + seg["v0"], 3)


def loc(seg, src_t):
    """source time → scene-local time"""
    return round(src_t - seg["src"][0], 3)


def esc(t):
    """escape text; a double space keeps its width (used around | and · in labels)"""
    return html.escape(t, quote=False).replace("  ", " &nbsp;")


def run(cmd):
    subprocess.run(cmd, check=True)


# ── init ────────────────────────────────────────────────────────────────────────
def cmd_init(project):
    for d in ("assets/source", "assets/fonts", "assets/sfx", "assets/vendor", "compositions", "deliverables"):
        os.makedirs(os.path.join(project, d), exist_ok=True)
    for sub in ("fonts", "sfx", "vendor"):
        for f in os.listdir(os.path.join(ASSETS, sub)):
            shutil.copy(os.path.join(ASSETS, sub, f), os.path.join(project, "assets", sub, f))
    name = os.path.basename(os.path.abspath(project))
    with open(os.path.join(project, "hyperframes.json"), "w") as f:
        json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                   "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
                   "media": {"autoProxy": True}}, f, indent=2)
    with open(os.path.join(project, "meta.json"), "w") as f:
        json.dump({"id": name, "name": name}, f, indent=2)
    ep_path = os.path.join(project, "episode.json")
    if not os.path.exists(ep_path):
        shutil.copy(os.path.join(HERE, "..", "examples", "pengezonan-padi.episode.json"), ep_path)
        print("episode.json copied from the example — replace every field for this speech.")
    print(f"initialised {project}")


# ── segments ────────────────────────────────────────────────────────────────────
def cmd_segments(project):
    ep = load(project)
    cw, ch, cx, cy = ep["crop"]
    if abs(cw / ch - 0.75) > 0.01:
        sys.exit(f"crop must be 3:4 (w/h = 0.75), got {cw}x{ch}")
    gain = ep.get("gain_db", 0)
    for s in ep["segments"]:
        a, d = s["src"][0], s["dur"]
        out = os.path.join(project, "assets", f"seg-{s['id']}.mp4")
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-i", os.path.join(project, ep["source"]), "-t", f"{d:.3f}",
             "-vf", f"crop={cw}:{ch}:{cx}:{cy}", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-g", "30",
             "-pix_fmt", "yuv420p", "-af",
             f"volume={gain}dB,afade=t=in:d=0.04,afade=t=out:st={max(0, d - 0.06):.3f}:d=0.06",
             "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])
        print(f"seg-{s['id']}.mp4  {d:.2f}s")
    last = ep["segments"][-1]["id"]
    run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.1", "-i", os.path.join(project, "assets", f"seg-{last}.mp4"),
         "-frames:v", "1", "-q:v", "2", os.path.join(project, "assets", "speech-last.jpg")])
    print("speech-last.jpg")


# ── shared scene CSS / JS ───────────────────────────────────────────────────────
SCENE_CSS = """
    @font-face { font-family: "Anton"; src: url("assets/fonts/anton-latin-400-normal.woff2") format("woff2"); font-weight: 400; }
    #root { position: absolute; inset: 0; background: transparent; font-family: "Montserrat", sans-serif; color: #fff; }
    .blk { position: absolute; left: 72px; top: 196px; width: 936px; height: 300px; }
    .kicker { font-weight: 700; font-size: 28px; letter-spacing: 0.14em; color: #d6ac52; text-transform: uppercase;
      display: flex; align-items: center; gap: 16px; white-space: nowrap; }
    .kicker i { display: block; width: 64px; height: 4px; background: #d6ac52; transform-origin: 0 50%; }
    .pill { margin-left: auto; font-weight: 600; font-size: 28px; letter-spacing: 0.04em; color: #fff;
      border: 2px solid rgba(214, 172, 82, 0.8); border-radius: 6px; padding: 2px 10px; }
    .big { margin-top: 12px; font-family: "Anton", sans-serif; line-height: 1; text-transform: uppercase;
      text-shadow: 0 6px 28px rgba(0, 0, 0, 0.6); }
    .line { display: block; overflow: hidden; padding-top: 4px; white-space: nowrap; }
    .w { display: inline-block; }
    .small { margin-top: 14px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.01em; white-space: nowrap; }
    .small.italic { font-style: italic; text-transform: none; font-weight: 700; }
    .dim { opacity: 0.25; }
    .stats { margin-top: 14px; display: flex; gap: 56px; align-items: flex-end; }
    .num { font-family: "Anton", sans-serif; line-height: 0.95;
      text-shadow: 0 0 34px rgba(214, 172, 82, 0.4), 0 6px 24px rgba(0, 0, 0, 0.6); }
    .unit { margin-top: 4px; font-weight: 800; font-size: 30px; letter-spacing: 0.06em; text-transform: uppercase; }
    .numrow { margin-top: 6px; display: flex; align-items: flex-end; gap: 24px; }
    .numside { padding-bottom: 16px; font-weight: 800; font-size: 34px; line-height: 1.2; text-transform: uppercase; }
    .lead { font-family: "Anton", sans-serif; font-size: 64px; line-height: 1.2; text-transform: uppercase; }
    .list { position: relative; margin-top: 12px; }
    .row { width: 936px; height: 44px; margin-bottom: 6px; display: flex; align-items: center;
      background: rgba(8, 26, 50, 0.72); border-left: 4px solid #d6ac52; }
    .row .n { width: 64px; text-align: center; font-family: "Anton", sans-serif; font-size: 32px; color: #d6ac52; }
    .row .t { font-weight: 800; font-size: 30px; text-transform: uppercase; white-space: nowrap; }
    .chip { margin-top: 16px; display: inline-block; font-weight: 800; font-size: 30px; text-transform: uppercase;
      color: #081a32; background: #ffd447; border-radius: 6px; padding: 6px 14px; white-space: nowrap; }
    .foot { margin-top: 16px; font-weight: 700; font-size: 30px; color: #e8e8e8; white-space: nowrap; }
    .foot b { color: #ffd447; font-weight: 800; }
    .lt-bar { position: absolute; left: 0; top: 0; width: 8px; height: 196px; background: #d6ac52; transform-origin: 50% 0; }
    .lt-text { position: absolute; left: 34px; top: 0; width: 900px; }
    .lt-name { font-family: "Anton", sans-serif; font-size: 66px; line-height: 1.12; text-transform: uppercase; }
    .lt-seat { font-weight: 600; font-size: 36px; color: #e8e8e8; }
"""

SCENE_JS = """    const tl = gsap.timeline({ paused: true });
    const reveal = (sel, t) => tl.fromTo(sel, { yPercent: 105 }, { yPercent: 0, duration: 0.45, ease: "power4.out" }, t);
    const kick = (sel, t) => tl.fromTo(sel, { scaleX: 0 }, { scaleX: 1, duration: 0.6, ease: "expo.out" }, t);
    const light = (sel, t) => tl.to(sel, { opacity: 1, duration: 0.1, ease: "none" }, t);
    const blurIn = (sel, t) => tl.fromTo(sel, { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.18, ease: "power4.out" }, t);
    const pop = (sel, t) => tl.fromTo(sel, { opacity: 0, scale: 1.3, filter: "blur(10px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.42, ease: "expo.out", transformOrigin: "0% 100%" }, t);
    const chip = (sel, t) => tl.fromTo(sel, { opacity: 0, scale: 0.85 }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(1.6)", transformOrigin: "0% 50%" }, t);
    const out = (sel, t) => tl.to(sel, { opacity: 0, filter: "blur(8px)", duration: 0.2, ease: "power2.in" }, t);
"""


class Scene:
    """Collects markup and timeline lines for one segment's graphics."""

    def __init__(self, seg, ep):
        self.seg, self.ep = seg, ep
        self.html, self.js = [], []
        self.n = 0

    def uid(self, tag):
        self.n += 1
        return f"{self.seg['id']}-{tag}{self.n}"

    def t(self, src_t):
        return loc(self.seg, src_t)

    def word(self, w, mode):
        """mode 'reveal' (mask rise), 'light' (dim → full), 'static'"""
        wid = self.uid("w")
        cls = ["w"]
        if w.get("c") in ("gold", "yel"):
            cls.append(w["c"])
        style = f' style="color:{COLORS[w["c"]]}"' if w.get("c") in COLORS else ""
        if "at" in w and mode == "light":
            cls.append("dim")
            self.js.append(f'    light("#{wid}", {self.t(w["at"])});')
        elif "at" in w and mode == "reveal":
            self.js.append(f'    reveal("#{wid}", {self.t(w["at"])});')
        return f'<span id="{wid}" class="{" ".join(cls)}"{style}>{esc(w["t"])}</span>'

    def row(self, r):
        k = r["kind"]
        if k == "big":
            size = r.get("size", 100)
            lines = []
            for ln in r["lines"]:
                lines.append('<span class="line" data-layout-allow-overflow>' + " ".join(self.word(w, "reveal") for w in ln) + "</span>")
            return f'<div class="big" style="font-size:{size}px">' + "".join(lines) + "</div>"
        if k == "small":
            size = r.get("size", 38)
            cls = "small italic" if r.get("italic") else "small"
            pre, post = ("“…", "”") if r.get("quote") else ("", "")
            return f'<div class="{cls}" style="font-size:{size}px">{pre}' + " ".join(self.word(w, "light") for w in r["words"]) + f"{post}</div>"
        if k == "stats":
            cells = []
            for it in r["items"]:
                nid, uidu = self.uid("n"), self.uid("u")
                self.js.append(f'    pop("#{nid}", {self.t(it["at"])});')
                if "unit_at" in it:
                    self.js.append(f'    blurIn("#{uidu}", {self.t(it["unit_at"])});')
                col = COLORS.get(it.get("c", "gold"))
                cells.append(f'<div><div id="{nid}" class="num" style="font-size:{r.get("size", 118)}px;color:{col}">{esc(it["num"])}</div>'
                             f'<div id="{uidu}" class="unit">{esc(it["unit"])}</div></div>')
            return '<div class="stats">' + "".join(cells) + "</div>"
        if k == "num":
            nid = self.uid("n")
            self.js.append(f'    pop("#{nid}", {self.t(r["at"])});')
            lead = ""
            if r.get("lead"):
                lid = self.uid("l")
                lead = f'<span id="{lid}" class="lead">{esc(r["lead"]["t"])}</span>'
                self.js.append(f'    blurIn("#{lid}", {self.t(r["lead"]["at"])});')
            side = ""
            if r.get("side"):
                side = '<div class="numside">' + " ".join(self.word(w, "light") for w in r["side"]) + "</div>"
            col = COLORS.get(r.get("c", "gold"))
            return (f'<div class="numrow">{lead}<div id="{nid}" class="num" style="font-size:{r.get("size", 180)}px;color:{col}">'
                    f'{esc(r["num"])}</div>{side}</div>')
        if k == "list":
            rows = []
            ids = []
            for i, item in enumerate(r["items"]):
                rid = self.uid("r")
                ids.append(rid)
                rows.append(f'<div id="{rid}" class="row"><div class="n">{i + 1:02d}</div><div class="t">{esc(item)}</div></div>')
            sel = ", ".join(f'"#{x}"' for x in ids)
            self.js.append(f'    tl.fromTo([{sel}], {{ opacity: 0, x: -36, clipPath: "inset(0% 100% 0% 0%)" }}, '
                           f'{{ opacity: 1, x: 0, clipPath: "inset(0% 0% 0% 0%)", duration: 0.5, stagger: 0.07, ease: "power4.out" }}, {self.t(r["at"])});')
            if "highlight" in r:
                h = r["highlight"]
                others = ", ".join(f'"#{x}"' for i, x in enumerate(ids) if i != h)
                ht = self.t(r["highlight_at"])
                self.js.append(f'    tl.to([{others}], {{ opacity: 0.5, duration: 0.2, ease: "power2.out" }}, {ht});')
                self.js.append(f'    tl.fromTo("#{ids[h]}", {{ backgroundColor: "rgba(8, 26, 50, 0.72)" }}, '
                               f'{{ backgroundColor: "rgba(214, 172, 82, 0.35)", duration: 0.2, ease: "power2.out" }}, {ht});')
            return '<div class="list">' + "".join(rows) + "</div>"
        if k == "chip":
            cid = self.uid("c")
            self.js.append(f'    chip("#{cid}", {self.t(r["at"])});')
            return f'<div id="{cid}" class="chip">{esc(r["t"])}</div>'
        if k == "foot":
            fid = self.uid("f")
            self.js.append(f'    blurIn("#{fid}", {self.t(r["at"])});')
            return f'<div id="{fid}" class="foot">{r["html"]}</div>'
        raise SystemExit(f"unknown row kind: {k}")

    def card(self, c, track):
        cid = self.uid("card")
        start, end = self.t(c["start"]), self.t(c["end"])
        start = max(start, 0.0)
        dur = round(end - start, 3)
        if c.get("type") == "lowerthird":
            mp = self.ep["mp"]
            bar, l1, l2, l3 = self.uid("bar"), self.uid("loc"), self.uid("name"), self.uid("seat")
            self.html.append(
                f'    <div id="{cid}" class="blk clip" data-start="{start}" data-duration="{dur}" data-track-index="{track}">\n'
                f'      <div id="{bar}" class="lt-bar"></div>\n      <div class="lt-text">\n'
                f'        <div class="line" data-layout-allow-overflow><span id="{l1}" class="w kicker">{esc(self.ep["location_lt"])}</span></div>\n'
                f'        <div class="line" data-layout-allow-overflow><span id="{l2}" class="w lt-name" data-var-text="mp-name">{esc(mp["name"])}</span></div>\n'
                f'        <div class="line" data-layout-allow-overflow><span id="{l3}" class="w lt-seat" data-var-text="mp-seat">{esc(mp["seat"])}</span></div>\n'
                f"      </div>\n    </div>")
            self.js.append(f'    tl.fromTo("#{bar}", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.5, ease: "expo.out" }}, {start});')
            self.js.append(f'    tl.fromTo(["#{l1}", "#{l2}", "#{l3}"], {{ yPercent: 110 }}, {{ yPercent: 0, duration: 0.6, stagger: 0.12, ease: "power4.out" }}, {round(start + 0.1, 3)});')
            self.js.append(f'    out("#{cid}", {round(end - 0.25, 3)});')
            return
        rule = self.uid("rule")
        kick = f'<div class="kicker"><i id="{rule}"></i><span>{esc(c.get("kicker", ""))}</span>'
        if c.get("pill"):
            kick += f'<span class="pill">{esc(c["pill"])}</span>'
        kick += "</div>"
        frame0 = self.seg["v0"] + start == 0
        if frame0:   # the thumbnail: everything already on screen, only the rule draws
            self.js.append(f'    tl.fromTo("#{rule}", {{ scaleX: 0.2 }}, {{ scaleX: 1, duration: 0.7, ease: "expo.out" }}, 0);')
        else:
            self.js.append(f'    kick("#{rule}", {start});')
        rows = "".join(self.row(r) for r in c["rows"])
        self.html.append(f'    <div id="{cid}" class="blk clip" data-start="{start}" data-duration="{dur}" data-track-index="{track}">\n'
                         f"      {kick}\n      {rows}\n    </div>")
        self.js.append(f'    out("#{cid}", {round(end - 0.25, 3)});')

    def render(self):
        for i, c in enumerate(self.seg.get("cards", [])):
            self.card(c, i % 3)
        sid = f"scene-{self.seg['id']}"
        mp = self.ep["mp"]
        variables = json.dumps([{"id": "mp-name", "type": "string", "label": "Nama Ahli Parlimen", "default": mp["name"]},
                                {"id": "mp-seat", "type": "string", "label": "Jawatan / kawasan", "default": mp["seat"]}])
        return (f"<template>\n  <style>{SCENE_CSS}  </style>\n"
                f"  <div id=\"root\" data-composition-id=\"{sid}\" data-width=\"1080\" data-height=\"1920\" data-composition-variables='{variables}'>\n"
                + "\n".join(self.html) + "\n  </div>\n  <script>\n    // Generated by Video MP (vmp.py build) from episode.json — local time = source time − "
                f"{self.seg['src'][0]}\n{SCENE_JS}" + "\n".join(self.js) + f'\n    window.__timelines["{sid}"] = tl;\n  </script>\n</template>\n')


# ── end card ────────────────────────────────────────────────────────────────────
def end_scene(ep):
    e, mp = ep["end"], ep["mp"]
    dur = e.get("duration", 6.5)
    name_lines = mp.get("name_lines", [mp["name"]])
    names = "".join(f'<span class="line" data-layout-allow-overflow><span id="fin-n{i}" class="w">{esc(n)}</span></span>' for i, n in enumerate(name_lines))
    box = ""
    if e.get("box_title"):
        items = "".join(f"<li>{b}</li>" for b in e.get("bullets", []))
        box = f'<div id="fin-box"><div class="kicker">{esc(e["box_title"])}</div><ul>{items}</ul></div>'
    quote = f'<div id="fin-quote">{e["quote"]}</div>' if e.get("quote") else ""
    nsel = ", ".join(f'"#fin-n{i}"' for i in range(len(name_lines)))
    fade = round(dur - 0.9, 3)
    return f"""<template>
  <style>{SCENE_CSS}
    #fin-scrim {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(8, 26, 50, 0.92) 0%, rgba(8, 11, 19, 0.88) 100%); }}
    #fin-card {{ position: absolute; left: 72px; top: {e.get("top", 330)}px; width: 936px; height: 990px; }}
    #fin-name {{ margin-top: 24px; font-family: "Anton", sans-serif; font-size: 88px; line-height: 1.04; text-transform: uppercase; }}
    #fin-seat {{ margin-top: 10px; font-weight: 600; font-size: 38px; color: #ffd447; }}
    #fin-quote {{ margin-top: 40px; padding-left: 28px; border-left: 5px solid #d6ac52; font-weight: 600; font-style: italic;
      font-size: 34px; line-height: 1.38; color: #f2f2f2; }}
    #fin-quote b {{ font-style: normal; font-weight: 800; color: #ffd447; }}
    #fin-box {{ margin-top: 40px; padding: 26px 28px; background: rgba(8, 26, 50, 0.85); border-left: 5px solid #d6ac52; }}
    #fin-box ul {{ margin-top: 14px; padding-left: 0; list-style: none; }}
    #fin-box li {{ position: relative; padding-left: 30px; margin-top: 12px; font-weight: 600; font-size: 32px; line-height: 1.32; color: #f2f2f2; }}
    #fin-box li::before {{ content: ""; position: absolute; left: 0; top: 16px; width: 12px; height: 12px; background: #d6ac52; }}
    #fin-box b {{ color: #ffd447; font-weight: 800; }}
    #fin-credit {{ margin-top: 30px; font-weight: 600; font-size: 28px; color: #b9c0cc; }}
  </style>
  <div id="root" data-composition-id="final" data-width="1080" data-height="1920">
    <div id="fin-scrim" class="clip" data-start="0" data-duration="{dur}" data-track-index="0"></div>
    <div id="fin-card" class="clip" data-start="0.4" data-duration="{round(dur - 0.4, 3)}" data-track-index="1">
      <div class="kicker"><i id="fin-rule"></i><span>{esc(ep["location"])}</span></div>
      <div id="fin-name">{names}</div>
      <div id="fin-seat">{esc(mp["seat"])}</div>
      {quote}{box}
      <div id="fin-credit">{esc(e.get("credit", "Petikan ucapan asal"))}</div>
    </div>
  </div>
  <script>
{SCENE_JS}    tl.fromTo("#fin-scrim", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.9, ease: "power2.inOut" }}, 0);
    kick("#fin-rule", 0.45);
    tl.fromTo([{nsel}], {{ yPercent: 105 }}, {{ yPercent: 0, duration: 0.55, stagger: 0.12, ease: "power4.out" }}, 0.8);
    blurIn("#fin-seat", 1.25);
    {'blurIn("#fin-quote", 1.7);' if quote else ''}
    {'blurIn("#fin-box", 1.7);' if box else ''}
    tl.fromTo("#fin-credit", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, ease: "power2.out" }}, 2.1);
    tl.to(["#fin-card", "#fin-scrim"], {{ opacity: 0, duration: 0.9, ease: "power2.in" }}, {fade});
    window.__timelines["final"] = tl;
  </script>
</template>
"""


# ── captions ────────────────────────────────────────────────────────────────────
def caption_words(ep, project):
    allw = []
    for tr in ep["transcripts"]:
        for w in json.load(open(os.path.join(project, tr["file"]))):
            allw.append({"text": w["text"], "start": w["start"] + tr.get("offset", 0), "end": w["end"] + tr.get("offset", 0)})
    out = {}
    for s in ep["segments"]:
        a, b = s["src"]
        ws = [w for w in allw if w["start"] >= a - 0.03 and w["end"] <= b + 0.05]
        toks = s["text"].split()
        if len(toks) != len(ws):
            sys.exit(f"segment {s['id']}: {len(toks)} words in 'text' but whisper has {len(ws)} in {a}–{b}:\n"
                     + " ".join(w["text"] for w in ws))
        res = []
        for tok, w in zip(toks, ws):
            st, en = max(w["start"], a), min(w["end"], b)
            parts = tok.split("|")
            step = (en - st) / len(parts)
            for i, p in enumerate(parts):
                x0, x1 = st + i * step, st + (i + 1) * step
                res.append({"text": p, "src": round(x0, 3), "start": v(s, x0), "end": v(s, x1)})
        out[s["id"]] = res
    return out


def group(ws, max_words, max_chars):
    groups, cur = [], []
    for i, w in enumerate(ws):
        cur.append(w)
        nxt = ws[i + 1] if i + 1 < len(ws) else None
        text = " ".join(x["text"] for x in cur)
        if (nxt is None or w["text"][-1] in ",.:;!?" or nxt["start"] - w["end"] >= 0.3
                or len(cur) >= max_words or len(text + " " + nxt["text"]) > max_chars):
            groups.append(cur)
            cur = []
    return groups


def norm(t):
    return "".join(c for c in t.lower() if c.isalnum() or c in ",.%-").strip(",.")


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


def captions(ep, project):
    words = caption_words(ep, project)
    keys = {norm(k) for k in ep.get("keywords", [])}
    G, win = [], []
    for s in ep["segments"]:
        hi = s.get("energy") == "high"
        for g in group(words[s["id"]], 3 if hi else 4, 19):
            G.append(g)
            win.append([max(0.12, g[0]["start"] - 0.06), g[-1]["end"] + 0.25, s["v0"] + s["dur"]])
    for i in range(len(win)):
        if i + 1 < len(win) and win[i][1] > win[i + 1][0]:
            win[i][1] = win[i + 1][0]
        win[i][1] = round(min(win[i][1], win[i][2] - 0.04), 3)
        win[i][0] = round(win[i][0], 3)
    parts, js = [], []
    for gi, (g, (gs, ge, _)) in enumerate(zip(G, win)):
        text = " ".join(w["text"] for w in g)
        size = 70 if len(text) <= 13 else 62 if len(text) <= 16 else 54
        spans, jw = [], []
        for wi, w in enumerate(g):
            wid = f"cw{gi}-{wi}"
            spans.append(f'<span id="{wid}" class="cw">{esc(w["text"].upper())}</span>')
            jw.append([wid, w["start"], w["end"], 1 if norm(w["text"]) in keys else 0])
        parts.append(f'    <div id="cg{gi}" class="cg"><div class="cbox" style="font-size:{size}px">' + " ".join(spans) + "</div></div>")
        js.append([f"cg{gi}", gs, ge, jw])
    doc = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; background: transparent; }}
    .cg {{ position: absolute; left: 0; top: {CAPTION_TOP}px; width: 1080px; height: 176px; display: flex; align-items: flex-end;
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
    // Generated by Video MP (vmp.py build). Edit episode.json, then re-run.
    const GROUPS = {json.dumps(js)};
    const tl = gsap.timeline({{ paused: true }});
    for (const [gid, gs, ge, ws] of GROUPS) {{
      const g = "#" + gid;
      tl.set(g, {{ visibility: "visible" }}, gs);
      tl.fromTo(g, {{ opacity: 0 }}, {{ opacity: 1, duration: 0.12, ease: "power2.out" }}, gs);
      tl.fromTo(g + " .cbox", {{ scale: 0.88 }}, {{ scale: 1, duration: 0.22, ease: "back.out(1.7)" }}, gs);
      for (const [wid, w0, w1, key] of ws) {{
        const w = "#" + wid;
        tl.set(w, {{ color: "{YELLOW}" }}, w0);
        if (key) {{
          tl.fromTo(w, {{ scale: 1 }}, {{ scale: 1.14, duration: 0.1, ease: "power2.out" }}, w0);
          tl.to(w, {{ scale: 1, duration: 0.2, ease: "power2.out" }}, w0 + 0.1);
        }} else {{
          tl.set(w, {{ color: "#FFFFFF" }}, Math.min(w1, ge - 0.02));
        }}
      }}
      tl.to(g, {{ opacity: 0, duration: 0.1, ease: "power2.in" }}, ge - 0.1);
      tl.set(g, {{ opacity: 0, visibility: "hidden" }}, ge);
    }}
    window.__timelines["captions"] = tl;
  </script>
</template>
"""
    with open(os.path.join(project, "compositions", "captions.html"), "w") as f:
        f.write(doc)
    with open(os.path.join(project, "deliverables", "subtitles-video.srt"), "w") as f:
        for i, (g, (gs, ge, _)) in enumerate(zip(G, win), 1):
            f.write(f"{i}\n{ts(gs)} --> {ts(ge)}\n{' '.join(w['text'] for w in g)}\n\n")
    cues = []
    for s in ep["segments"]:
        for g in group(words[s["id"]], 12, 64):
            cues.append((g[0]["src"], g[-1]["src"] + (g[-1]["end"] - g[-1]["start"]), two_lines(g)))
    cues.sort()
    with open(os.path.join(project, "deliverables", "subtitles-source.srt"), "w") as f:
        for i, (a, b, t) in enumerate(cues, 1):
            f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n")
    return len(G)


# ── root ────────────────────────────────────────────────────────────────────────
def root_html(ep):
    fx, fy = ep["face"]
    vol = ep.get("speech_volume", 1)
    grade = html.escape(json.dumps(ep.get("grade", {"preset": "skin-soft", "intensity": 0.55,
                                                    "adjust": {"highlights": -0.08, "shadows": 0.06, "contrast": 0.04, "vibrance": 0.02},
                                                    "details": {"vignette": 0.05}})), quote=True)
    vids, hosts, cam, sfx = [], [], [], []
    for i, s in enumerate(ep["segments"]):
        vids.append(f'        <!-- {s["id"]} · source {s["src"][0]}–{s["src"][1]} s -->\n'
                    f'        <video id="seg-{s["id"]}" class="clip" src="assets/seg-{s["id"]}.mp4" data-start="{s["v0"]}" '
                    f'data-duration="{s["dur"]}" data-track-index="0" data-has-audio="true" data-volume="{vol}" '
                    f'data-color-grading="{grade}" playsinline></video>')
        hosts.append(f'      <div id="scene-{s["id"]}" class="scene" data-composition-id="scene-{s["id"]}" '
                     f'data-composition-src="compositions/scene-{s["id"]}.html" data-start="{s["v0"]}" data-duration="{s["dur"]}" '
                     f'data-track-index="{2 + i % 2}" data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index: 5"></div>')
        shots = s.get("camera") or [{"at": s["src"][0], "scale": WIDE, "to": WIDE + 0.1}]
        for j, sh in enumerate(shots):
            t0 = v(s, max(sh["at"], s["src"][0]))
            t1 = v(s, shots[j + 1]["at"]) if j + 1 < len(shots) else s["v0"] + s["dur"]
            f0 = sh.get("fy", 900 if sh["scale"] < 1.5 else 780)
            if sh.get("move"):
                cam.append(f'      tl.to("#cam", {{ ...frame({sh["scale"]}, {f0}), duration: {sh["move"]}, ease: "power2.inOut" }}, {t0});')
                t0 = round(t0 + sh["move"], 3)
            else:
                cam.append(f'      tl.set("#cam", frame({sh["scale"]}, {f0}), {t0});')
            if sh.get("to"):
                cam.append(f'      tl.to("#cam", {{ ...frame({sh["to"]}, {sh.get("fy_to", f0)}), duration: {round(t1 - t0, 3)}, ease: "none" }}, {t0});')
        if i > 0:
            cam.append(f"      dipCut({s['v0']});")
            sfx.append((s["v0"] - 0.16, "whoosh-short", 0.57, 0.24 if i % 2 else 0.2))
        for x in s.get("sfx", []):
            dur = {"impact-bass-1": 2.1, "impact-bass-2": 2.58, "whoosh-short": 0.57}[x["file"]]
            peak = {"impact-bass-1": 0.073, "impact-bass-2": 1.986, "whoosh-short": 0.162}[x["file"]]
            sfx.append((v(s, x["at"]) - peak + 0.033, x["file"], dur, x.get("volume", 0.2)))
    end = ep["end"]
    last = ep["segments"][-1]
    still_dur = round(ep["total"] - ep["speech_end"], 3)
    end_start = round(ep["speech_end"] - 0.1, 3)
    end_dur = round(ep["total"] - end_start, 3)
    sfx.append((end_start + 1.35, "impact-bass-1", 2.1, 0.15))
    audio = "\n".join(
        f'      <audio id="sfx-{k}" class="clip" src="assets/sfx/{f}.mp3" data-start="{max(0, round(t, 3))}" data-duration="{d}" '
        f'data-track-index="{6 + k % 2}" data-volume="{vol_}"></audio>' for k, (t, f, d, vol_) in enumerate(sfx))
    end_cam = end.get("camera_to", 1.9)
    return f"""<!doctype html>
<html lang="ms">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: {GROUND}; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
      #bg {{ position: absolute; inset: 0; background: {GROUND}; z-index: 0; }}
      /* Camera wrapper: punch-ins and pushes move this, never the media. Plates are {PLATE_W}x{PLATE_H} (3:4). */
      #cam {{ position: absolute; left: 0; top: 0; width: {PLATE_W}px; height: {PLATE_H}px; transform-origin: 0 0; z-index: 1; }}
      #cam video, #cam img {{ position: absolute; left: 0; top: 0; width: {PLATE_W}px; height: {PLATE_H}px; object-fit: cover; }}
      #band {{ position: absolute; left: 0; top: 0; width: 1080px; height: 640px; z-index: 2;
        background: linear-gradient(180deg, {NAVY} 0%, rgba(8, 26, 50, 0.95) 34%, rgba(8, 26, 50, 0.6) 64%, rgba(8, 26, 50, 0) 100%); }}
      #floor {{ position: absolute; left: 0; top: 1180px; width: 1080px; height: 740px; z-index: 2;
        background: linear-gradient(180deg, rgba(8, 11, 19, 0) 0%, rgba(8, 11, 19, 0.55) 35%, rgba(8, 11, 19, 0.85) 100%); }}
      #dip {{ position: absolute; inset: 0; background: #000; opacity: 0; z-index: 3; }}
      .scene {{ position: absolute; inset: 0; }}
    </style>
  </head>
  <body>
    <!-- Generated by Video MP (vmp.py build) from episode.json: "{esc(ep.get("title", ep.get("id", "")))}" -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{ep["total"]}" data-width="1080" data-height="1920">
      <div id="bg"></div>
      <div id="cam">
{chr(10).join(vids)}
        <img id="v-still" class="clip" src="assets/speech-last.jpg" alt="" data-start="{ep["speech_end"]}" data-duration="{still_dur}" data-track-index="0" data-color-grading="{grade}" />
      </div>
      <div id="band"></div>
      <div id="floor"></div>
      <div id="dip"></div>
{chr(10).join(hosts)}
      <div id="final" class="scene" data-composition-id="final" data-composition-src="compositions/final.html" data-start="{end_start}" data-duration="{end_dur}" data-track-index="4" data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index: 6"></div>
      <div id="captions" class="scene" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{round(ep["speech_end"] + 0.1, 3)}" data-track-index="5" data-track-kind="captions" data-width="1080" data-height="1920" style="z-index: 7"></div>
      <!-- Music bed slot: <audio id="music" class="clip" src="assets/music/bed.mp3" data-start="0" data-duration="{ep["total"]}" data-track-index="8" data-volume="0.14" data-fade-in="0.5" data-fade-out="1.5"></audio> -->
{audio}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      // Face centre in the {PLATE_W}x{PLATE_H} plate: ({fx}, {fy}). The plate always covers the frame.
      const FX = {fx}, FY = {fy};
      const frame = (s, fy = 900) => {{
        const y = Math.min(0, Math.max(1920 - {PLATE_H} * s, fy - FY * s));
        const x = Math.min(0, Math.max(1080 - {PLATE_W} * s, 540 - FX * s));
        return {{ scale: s, x, y }};
      }};
      const dipCut = (t) => {{
        tl.to("#dip", {{ opacity: 0.4, duration: {DIP}, ease: "power1.in" }}, t - {DIP});
        tl.set("#dip", {{ opacity: 0 }}, t);
      }};
{chr(10).join(cam)}
      tl.to("#cam", {{ ...frame({end_cam}, 770), duration: {still_dur}, ease: "none" }}, {ep["speech_end"]});
      tl.to("#dip", {{ opacity: 1, duration: 0.9, ease: "power2.in" }}, {round(ep["total"] - 0.9, 3)});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""


def cmd_build(project):
    ep = load(project)
    ep.setdefault("location_lt", ep["location"])
    os.makedirs(os.path.join(project, "compositions"), exist_ok=True)
    os.makedirs(os.path.join(project, "deliverables"), exist_ok=True)
    for s in ep["segments"]:
        with open(os.path.join(project, "compositions", f"scene-{s['id']}.html"), "w") as f:
            f.write(Scene(s, ep).render())
    with open(os.path.join(project, "compositions", "final.html"), "w") as f:
        f.write(end_scene(ep))
    n = captions(ep, project)
    with open(os.path.join(project, "index.html"), "w") as f:
        f.write(root_html(ep))
    print(f"built {len(ep['segments'])} scenes + end card, {n} caption groups, total {ep['total']} s")
    if not 60 <= ep["total"] <= 90:
        print(f"note: total {ep['total']} s is outside the 60–90 s target")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("init", "segments", "build"):
        sys.exit(__doc__)
    {"init": cmd_init, "segments": cmd_segments, "build": cmd_build}[sys.argv[1]](sys.argv[2])
