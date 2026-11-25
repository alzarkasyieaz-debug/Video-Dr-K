#!/usr/bin/env python3
"""hfkit — build "UCAPAN DI DEWAN RAKYAT" style HyperFrames projects from a spec.

A spec lists source segments (file, in, out) in output order, a hook, timed
"cards" (graphics) keyed to SOURCE times, and an outro. hfkit:
  * snaps segment edges to quiet points in the source audio,
  * extracts each segment as 9:16 footage (crop around the speaker, cleaned voice),
  * writes index.html, scene files and captions (from whisper word timings).

Style matches episodes 1–3: bug "UCAPAN DI DEWAN RAKYAT", framed "RAKAMAN ASAL"
panel, GRAFIK / ILUSTRASI tags, navy + gold, Inter.
"""
import html, json, math, os, re, struct, subprocess, wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRCDIR = os.path.join(ROOT, "assets", "src", "d")
TXDIR = os.path.join(ROOT, ".hyperframes", "tx")

# ------------------------------------------------------------------ audio helpers
_wavs = {}


def _wav(f):
    if f not in _wavs:
        w = wave.open(os.path.join(SRCDIR, f + ".wav"))
        _wavs[f] = (w, w.getframerate())
    return _wavs[f]


def rms(f, a, b):
    w, sr = _wav(f)
    w.setpos(max(0, int(a * sr)))
    n = max(1, int((b - a) * sr))
    raw = w.readframes(n)
    n = len(raw) // 2
    if n == 0:
        return -120
    d = struct.unpack("<%dh" % n, raw)
    return 20 * math.log10(math.sqrt(sum(x * x for x in d) / n) / 32768 + 1e-9)


def snap(f, t, side, win=0.45):
    """Move a cut point to the quietest 40 ms window near t, never into the words:
    an in-point may move earlier (up to win) or 0.1 s later; an out-point the reverse."""
    lo, hi = (t - win, t + 0.1) if side == "in" else (t - 0.1, t + win)
    best = None
    x = lo
    while x <= hi + 1e-9:
        if x >= 0:
            v = rms(f, x, x + 0.04) + abs(x - t) * 4
            if best is None or v < best[0]:
                best = (v, x)
        x += 0.02
    x = best[1]
    return round(x + (0.03 if side == "in" else 0.02), 2)


# ------------------------------------------------------------------ words
_words = {}


def words(f):
    if f not in _words:
        d = json.load(open(os.path.join(TXDIR, f + "-words.json")))
        _words[f] = [(s["offsets"]["from"] / 1000, s["offsets"]["to"] / 1000, s["text"].strip())
                     for s in d["transcription"] if s["text"].strip()]
    return _words[f]


# Generic spelling fixes for whisper output on these speeches (lower-case key → text).
NORM = {
    "sri": "Seri", "skanda": "Iskandar", "skandar": "Iskandar", "skandar.": "Iskandar.", "iskandar": "Iskandar",
    "bilia": "belia", "parik": "Parit", "parit": "Parit", "parit,": "Parit,", "parit.": "Parit.",
    "pasal": "pasar", "kerjaan": "kerajaan", "pertua": "Pertua", "kuatis": "kuarters", "kuatis-kuatis": "kuarters-kuarters",
    "fekra": "FELCRA", "pampengairan": "pam pengairan", "skm": "SKM", "sjkc": "SJKC", "sspn": "SSPN", "mrsm": "MRSM",
    "tahfis": "tahfiz", "uitm,": "UiTM,", "uitm": "UiTM", "utp,": "UTP,", "kpkt": "KPKT", "jkr": "JKR",
    "sungai": "Sungai", "perak": "Perak", "bota": "Bota", "seluang": "Seluang", "lambor": "Lambor",
    "hektare": "hektar",
}


PROPER = {"Seri", "Iskandar", "Parit", "Perak", "Tengah", "Bandar", "Universiti", "Perdana", "Menteri", "Tronoh", "Allah", "Al-Quran",
          "Sungai", "Bota", "Kanan", "Kiri", "Lambor", "Seluang", "Pulai", "Changkat", "Lintang", "Melintang", "Manjung", "Lumut", "Ipoh", "Titi", "Gantung", "Korok", "Masjid",
          "Latifah", "Ufraniah", "Pengurusi", "Puan", "Tuan", "Datuk", "Dato'", "Yang", "Dipertua", "Pertua", "Kementerian", "Kerja", "Raya",
          "Pembangunan", "Kerajaan", "Tempatan", "Chung", "Hua", "Cina", "Melayu", "India", "Kampung", "Sadang", "Ranggam", "Pulau", "Tiga",
          "Teluk", "Bakung", "Padang", "Koba", "Ekor", "Lambat", "Taman", "Cempaka", "Sari", "Tuntung", "Layang", "Chopping", "Belanja",
          "Temerloh", "Ulul", "Albab", "Jagung", "Teknologi", "Dewan", "Rakyat", "Malaysia", "Persekutuan", "Pelancongan", "Seni", "Budaya",
          "Pertanian", "Mara", "Kebangsaan", "Jenis", "Sekolah", "Perdana", "Kerau", "Kuala", "Pekan"}


def norm(tok):
    k = tok.lower()
    if k in NORM:
        return NORM[k]
    return tok


# ------------------------------------------------------------------ CSS / snippets
SCENE_CSS = """
    #root { position: absolute; inset: 0; font-family: Inter, sans-serif; }
    .ill { position: absolute; padding: 4px 10px; border-radius: 5px; font-weight: 800; font-size: 28px; letter-spacing: .16em;
      color: #c9d2e0; border: 1px solid rgba(201,210,224,.5); background: rgba(7,17,31,.6); }
    .zone { position: absolute; left: 60px; top: 846px; width: 960px; height: 300px; }
    .zk { position: absolute; left: 0; top: 0; font-size: 28px; font-weight: 800; letter-spacing: .16em; color: #c9d2e0; white-space: nowrap; }
    .zone .ill { right: 0; top: -2px; }
    .gold3d { color: #f8d77e; text-shadow: 0 1px 0 #e0b04f, 0 2px 0 #d3a344, 0 3px 0 #c4953a, 0 4px 0 #b28430, 0 5px 0 #9c7226,
      0 6px 0 #845f1d, 0 7px 0 #6c4c16, 0 16px 28px rgba(0,0,0,.75); }
    .silver3d { color: #eef1f6; text-shadow: 0 1px 0 #c3cad6, 0 2px 0 #a9b2c0, 0 3px 0 #8e97a6, 0 4px 0 #747d8c, 0 14px 24px rgba(0,0,0,.6); }
    .chip { position: absolute; left: 44px; top: 262px; padding: 10px 18px; border-radius: 10px; background: rgba(242,197,92,.95);
      color: #17110a; font-weight: 900; font-size: 30px; letter-spacing: .08em; white-space: nowrap; }
    .src { position: absolute; left: 44px; top: 326px; padding: 6px 14px; border-radius: 8px; background: rgba(7,17,31,.85);
      border: 1px solid rgba(231,235,242,.4); color: #e7ebf2; font-weight: 800; font-size: 28px; letter-spacing: .1em; white-space: nowrap; }
    .pill { position: absolute; height: 56px; padding: 0 18px; border-radius: 12px; background: rgba(7,17,31,.92);
      border: 1px solid rgba(231,235,242,.35); color: #f4f6fa; font-size: 28px; font-weight: 900; letter-spacing: .03em; line-height: 56px; white-space: nowrap; }
    .pill.red { border: 2px solid rgba(224,68,58,.85); color: #ff8e83; }
    .pill.gold { background: #f2c55c; color: #17110a; border: none; }
    .bd { position: absolute; left: 0; top: 840px; width: 1080px; height: 330px;
      background: linear-gradient(180deg, rgba(4,8,16,0) 0%, rgba(4,8,16,.74) 20%, rgba(4,8,16,.8) 82%, rgba(4,8,16,0) 100%); }
    .qcard { position: absolute; left: 0; top: 46px; width: 960px; height: 254px; border-radius: 18px; background: rgba(7,17,31,.95);
      border: 2px solid rgba(242,197,92,.8); padding: 20px 28px; }
    .qcard small { display: block; font-size: 28px; font-weight: 900; letter-spacing: .2em; color: #f2c55c; }
    .qcard p { margin-top: 8px; font-size: 34px; font-weight: 800; line-height: 1.2; color: #f4f6fa; }
    .qcard p b { color: #f8d77e; }
    .stat { position: absolute; top: 50px; height: 250px; border-radius: 18px; background: rgba(13,29,51,.94);
      border: 1px solid rgba(242,197,92,.55); padding: 18px 22px; }
    .stat small { display: block; font-size: 28px; font-weight: 800; letter-spacing: .08em; color: #c9d2e0; line-height: 1.15; }
    .stat .v { display: block; margin-top: 8px; font-weight: 900; line-height: 1; white-space: nowrap; }
    .stat .d { display: block; margin-top: 10px; font-size: 28px; font-weight: 800; color: #f2c55c; line-height: 1.15; }
    .stat.red { border: 2px solid rgba(224,68,58,.85); }
    .stat.red .v { color: #ff6a5c; text-shadow: 0 1px 0 #d44c40, 0 2px 0 #b73d33, 0 3px 0 #982f27, 0 4px 0 #7a241d, 0 14px 24px rgba(0,0,0,.6); }
    .bigline { position: absolute; left: 0; width: 960px; text-align: center; font-weight: 900; line-height: 1.02; }
    .subline { position: absolute; left: 0; width: 960px; text-align: center; font-size: 36px; font-weight: 900; color: #f4f6fa; line-height: 1.15; }
"""

HOOK_CSS = """
    .h-kick { position: absolute; left: 0; width: 1080px; top: 862px; text-align: center;
      font-size: 28px; font-weight: 800; letter-spacing: .2em; color: #f2c55c; }
    .h-kick span { padding: 8px 18px; border: 1px solid rgba(242,197,92,.6); border-radius: 8px; background: rgba(7,17,31,.7); }
    .h-line { position: absolute; left: 30px; width: 1020px; text-align: center; font-weight: 900; color: #f4f6fa;
      font-size: 44px; white-space: nowrap; text-shadow: 0 4px 0 rgba(0,0,0,.45), 0 10px 30px rgba(0,0,0,.8); }
    .h-3d { position: absolute; left: 20px; width: 1040px; text-align: center; font-weight: 900; line-height: 1; white-space: nowrap;
      letter-spacing: -0.02em; color: #f8d77e;
      text-shadow: 0 1px 0 #e0b04f, 0 2px 0 #d3a344, 0 3px 0 #c4953a, 0 4px 0 #b28430, 0 5px 0 #9c7226,
        0 6px 0 #845f1d, 0 7px 0 #6c4c16, 0 8px 0 #5a3f12, 0 18px 30px rgba(0,0,0,.75), 0 0 60px rgba(242,197,92,.35); }
"""

SLAM = '{ opacity: 0, scale: 1.9, rotationX: -55, transformPerspective: 900 }, { opacity: 1, scale: 1, rotationX: 0, duration: 0.22, ease: "expo.out" }'
POP_L = '{ opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 0.35, ease: "expo.out" }'
POP_U = '{ opacity: 0, y: 18, scale: 0.92 }, { opacity: 1, y: 0, scale: 1, duration: 0.32, ease: "back.out(1.8)" }'
RISE = '{ opacity: 0, y: 22, rotationX: -40, transformPerspective: 900 }, { opacity: 1, y: 0, rotationX: 0, duration: 0.38, ease: "expo.out" }'
FADE_IN = '{ opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.4, ease: "expo.out" }'
BLUR_IN = '{ opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.25, ease: "power3.out" }'


def esc(s):
    return s  # specs are authored HTML-safe (use &amp; where needed)


def scene_html(sid, css, body, js):
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


# ------------------------------------------------------------------ project build
# vertical face centre (source px, 0–720) per file; used to frame the face
FACE_Y = {}
HOOK_S, BASE_S = 1.28, 1.08   # 720p sources are already enlarged ~2.7×: keep extra zoom modest


def cam_y(f, mode):
    c = FACE_Y.get(f, 240) * 1920 / 720
    if mode == "hook":
        return round(420 - (640 + (c - 640) * HOOK_S))
    target = 470 if mode == "full" else 450
    y = target - (640 + (c - 640) * BASE_S)
    if mode == "full":   # keep the footage covering the whole frame
        y = min(max(y, 1920 - (640 + 1280 * BASE_S)), 640 * BASE_S - 640)
    return round(y)


class Video:
    def __init__(self, spec, outdir, crops):
        self.s = spec
        self.dir = os.path.join(outdir, spec["id"])
        self.assets = os.path.join(outdir, "assets")
        self.crops = crops
        self.segs = []  # (file, in, out, out_start)
        t = 0.0
        for i, seg in enumerate(spec["segments"]):
            f, a, b = seg[:3]
            a2, b2 = snap(f, a, "in"), snap(f, b, "out")
            self.segs.append((f, a2, b2, round(t, 2)))
            t += b2 - a2
        self.speech_end = round(t, 2)
        self.total = round(t + 3.5, 2)

    # map a source time to output time (skip the hook segment unless asked)
    def o(self, f, t, allow_hook=False):
        for i, (sf, a, b, o) in enumerate(self.segs):
            if i == 0 and not allow_hook and len(self.segs) > 1:
                continue
            if sf == f and a - 0.6 <= t <= b + 0.3:
                return round(min(max(t, a), b) - a + o, 2)
        if not allow_hook:
            return self.o(f, t, True)
        raise ValueError(f"{self.s['id']}: {f}@{t} not inside any segment")

    # -------------------------------------------------------------- footage
    def extract(self):
        fd = os.path.join(self.assets, "footage", self.s["id"])
        os.makedirs(fd, exist_ok=True)
        for i, (f, a, b, o) in enumerate(self.segs):
            out = os.path.join(fd, f"s{i:02d}.mp4")
            if os.path.exists(out):
                continue
            x = self.s.get("crop", {}).get(i, self.crops[f])
            ss = max(0, a - 0.5)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.3f}", "-to", f"{b + 0.5:.3f}",
                            "-i", os.path.join(SRCDIR, f + ".mp4"),
                            "-vf", f"crop=405:720:{x}:0,scale=1080:1920:flags=lanczos,unsharp=5:5:0.6:5:5:0.0",
                            "-af", "highpass=f=80,lowpass=f=12000,afftdn=nf=-28,acompressor=threshold=-20dB:ratio=2.5:attack=10:release=200,loudnorm=I=-16:TP=-1.5:LRA=9",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-g", "30", "-keyint_min", "30",
                            "-sc_threshold", "0", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out], check=True)
        last = self.segs[-1]
        img = os.path.join(self.assets, "img", f"end-{self.s['id']}.jpg")
        os.makedirs(os.path.dirname(img), exist_ok=True)
        if not os.path.exists(img):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.6", "-i",
                            os.path.join(fd, f"s{len(self.segs) - 1:02d}.mp4"), "-frames:v", "1", "-q:v", "2", img], check=True)

    def seg_media_start(self, i):
        f, a, b, o = self.segs[i]
        return round(a - max(0, a - 0.5), 3)

    # -------------------------------------------------------------- scenes
    def hook(self):
        h = self.s["hook"]
        sid = "h-hook"
        f, a, b, _ = self.segs[0]
        t_big = round(h["t_big"] - a, 2)
        end = round(b - a - 0.18, 2)
        lines = h["lines"]
        body = ['    <div class="bd" id="hk-bd"></div>', '    <div id="hk-z">',
                f'      <div class="h-kick" id="hk-k"><span>{h["kick"]}</span></div>']
        top = 922
        for i, ln in enumerate(lines):
            fs = min(44, int(1000 / (max(1, len(ln)) * 0.66)))
            body.append(f'      <div class="h-line" id="hk-l{i}" style="top: {top}px; font-size: {fs}px">{ln}</div>')
            top += 66
        bl = len(re.sub("<[^>]+>|&amp;", "x", h["big"]))
        bfs = min(h.get("size", 110), int(1000 / (bl * 0.66)))
        body.append(f'      <div class="h-3d" id="hk-big" style="top: {top + 8}px; font-size: {bfs}px">{h["big"]}</div>')
        body.append('    </div>')
        js = [f'    tl.fromTo(["#hk-k", "#hk-l0"], {{ opacity: 1 }}, {{ opacity: 1, duration: 0.01 }}, 0);']
        for i, t in enumerate(h.get("t_lines", [])[1:], 1):
            js.append(f'    tl.fromTo("#hk-l{i}", {BLUR_IN}, {round(t - a, 2)});')
        js.append(f'    tl.fromTo("#hk-big", {SLAM}, {t_big});')
        if lines:
            js.append(f'    tl.to([{", ".join(chr(34) + "#hk-l" + str(i) + chr(34) for i in range(len(lines)))}], {{ opacity: 0.6, duration: 0.3 }}, {t_big});')
        js.append(f'    tl.to(["#hk-z", "#hk-bd"], {{ opacity: 0, filter: "blur(10px)", duration: 0.16, ease: "power2.in" }}, {end});')
        self.hook_big_out = t_big
        return sid, 0, round(b - a, 2), scene_html(sid, HOOK_CSS, "\n".join(body), "\n".join(js))

    def ident(self, start, dur, topic, src_label=None):
        sid = "h-id"
        out = round(dur - 0.35, 2)
        css = """
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
        body = f"""    <div class="chip" id="id-topic">{topic}</div>
    <div id="id-lt">
      <div id="id-card">
        <div id="id-bar"></div>
        <div id="id-name">HAJI MUHAMMAD ISMI<br />BIN MAT TAIB</div>
        <div id="id-role">AHLI PARLIMEN PARIT, PERAK</div>
        <div id="id-shine"></div>
      </div>
      <div id="id-chip">DEWAN RAKYAT MALAYSIA</div>
    </div>"""
        js = f"""    tl.fromTo("#id-card", {{ clipPath: "inset(0 100% 0 0 round 18px)" }}, {{ clipPath: "inset(0 0% 0 0 round 18px)", duration: 0.6, ease: "power3.inOut" }}, 0.35);
    tl.fromTo("#id-chip", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, 0.75);
    tl.fromTo("#id-name", {{ opacity: 0, x: -30, filter: "blur(8px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.45, ease: "expo.out" }}, 0.65);
    tl.fromTo("#id-role", {BLUR_IN}, 0.9);
    tl.fromTo("#id-shine", {{ x: 0, rotation: 18 }}, {{ x: 1700, rotation: 18, duration: 1.0, ease: "power2.inOut" }}, 1.2);
    tl.fromTo("#id-topic", {POP_L}, 1.1);
    tl.to("#id-lt", {{ opacity: 0, y: 20, duration: 0.3, ease: "power2.in" }}, {out});
    tl.to("#id-topic", {{ opacity: 0, duration: 0.25, ease: "power2.in" }}, {out});"""
        return sid, start, dur, scene_html(sid, css, body, js)

    def card(self, n, c, start, end):
        """One graphic card. Element times in c are source times (file, t)."""
        sid = f"c{n:02d}"
        dur = round(end - start, 2)
        L = lambda ft: round(self.o(*ft) - start, 2)
        body, js, css = [], [], ""
        split = c.get("mode", "split") == "split"
        kind = c["type"]
        if not split:
            body.append('    <div class="bd" id="bd"></div>')
            js.append(f'    tl.fromTo("#bd", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 0.05);')
        body.append(f'    <div class="zone" id="z">')
        if c.get("kicker"):
            kl = len(re.sub("<[^>]+>|&amp;", "x", c["kicker"]))
            kfs = min(28, int(770 / (kl * 0.78)))
            body.append(f'      <div class="zk" id="zk" style="font-size: {kfs}px">{c["kicker"]}</div>')
            js.append(f'    tl.fromTo("#zk", {FADE_IN}, 0.2);')
        if c.get("tag", "GRAFIK"):
            body.append(f'      <div class="ill" id="zt">{c.get("tag", "GRAFIK")}</div>')
            js.append(f'    tl.fromTo("#zt", {FADE_IN}, 0.25);')
        if kind == "pills":
            # rows of pills; each item: (text, (file,t), style)
            x, y, row_h = 0, 52, 66
            for i, (txt, ft, style) in enumerate(c["items"]):
                w = 40 + int(len(re.sub("<[^>]+>|&amp;", "x", txt)) * 19.5)
                if x + w > 960:
                    x, y = 0, y + row_h
                cls = "pill" + ({"gold": " gold", "red": " red"}.get(style, ""))
                body.append(f'      <div class="{cls}" id="p{i}" style="left: {x}px; top: {y}px">{txt}</div>')
                js.append(f'    tl.fromTo("#p{i}", {POP_U}, {max(0.3, L(ft))});')
                x += w + 14
        elif kind == "stats":
            n_ = len(c["items"])
            w = (960 - 20 * (n_ - 1)) // n_
            for i, it in enumerate(c["items"]):
                cls = "stat red" if it.get("red") else "stat"
                size = it.get("size", 64 if n_ > 1 else 96)
                body.append(f'      <div class="{cls}" id="s{i}" style="left: {i * (w + 20)}px; width: {w}px"><small>{it["label"]}</small>'
                            f'<span class="v {"" if it.get("red") else "gold3d"}" id="s{i}v" style="font-size: {size}px">{it["value"]}</span>'
                            f'<span class="d" id="s{i}d">{it.get("note", "")}</span></div>')
                js.append(f'    tl.fromTo("#s{i}", {RISE}, {max(0.3, L(it["t"]) - 0.35)});')
                js.append(f'    tl.fromTo("#s{i}v", {SLAM}, {max(0.4, L(it["t"]))});')
                if it.get("note"):
                    js.append(f'    tl.fromTo("#s{i}d", {BLUR_IN}, {max(0.5, L(it.get("t_note", it["t"])) + 0.3)});')
        elif kind == "q":
            body.append(f'      <div class="qcard" id="q"><small>{c.get("label", "SOALAN")}</small>')
            for i, (txt, ft) in enumerate(c["lines"]):
                body.append(f'        <p id="q{i}">{txt}</p>')
            body.append('      </div>')
            js.append(f'    tl.fromTo("#q", {{ opacity: 0, scale: 1.05 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "expo.out" }}, 0.15);')
            for i, (txt, ft) in enumerate(c["lines"]):
                js.append(f'    tl.fromTo("#q{i}", {BLUR_IN}, {max(0.3, L(ft))});')
            if c.get("size"):
                css += f"\n    .qcard p {{ font-size: {c['size']}px; }}"
        elif kind == "big":
            # big gold line + optional sublines, each keyed to its word
            top = 70
            longest = max(len(re.sub("<[^>]+>|&amp;", "x", p)) for p in re.split("<br ?/?>", c["big"]))
            size = min(c.get("size", 92), int(940 / (longest * 0.64)))
            c = dict(c, size=size)
            body.append(f'      <div class="bigline gold3d" id="b0" style="top: {top}px; font-size: {size}px; white-space: nowrap">{c["big"]}</div>')
            js.append(f'    tl.fromTo("#b0", {SLAM}, {max(0.3, L(c["t"]))});')
            sub_top = top + c.get("size", 92) * (c["big"].count("<br") + 1) + 14
            for i, (txt, ft) in enumerate(c.get("subs", [])):
                fs = min(36, int(940 / (max(1, len(txt)) * 0.56)))
                body.append(f'      <div class="subline" id="b{i + 1}" style="top: {sub_top + i * 50}px; font-size: {fs}px; white-space: nowrap">{txt}</div>')
                js.append(f'    tl.fromTo("#b{i + 1}", {BLUR_IN}, {max(0.4, L(ft))});')
        elif kind == "tiles":
            n_ = len(c["items"])
            cols = 2 if n_ > 2 else n_
            rows = math.ceil(n_ / cols)
            th = min(110, (250 - (rows - 1) * 10) // rows)
            tw = (960 - (cols - 1) * 20) // cols
            css += """
    .tile { position: absolute; border-radius: 14px; background: rgba(13,29,51,.94); border: 1px solid rgba(242,197,92,.55);
      padding: 0 16px 0 66px; display: flex; align-items: center; font-size: 28px; font-weight: 900; line-height: 1.1; color: #f4f6fa; }
    .tile em { position: absolute; left: 16px; top: calc(50% - 19px); width: 38px; height: 38px; border-radius: 10px; background: #f2c55c;
      color: #17110a; font-style: normal; font-size: 28px; font-weight: 900; text-align: center; line-height: 38px; }"""
            for i, (txt, ft) in enumerate(c["items"]):
                x = (i % cols) * (tw + 20)
                y = 48 + (i // cols) * (th + 10)
                body.append(f'      <div class="tile" id="t{i}" style="left: {x}px; top: {y}px; width: {tw}px; height: {th}px"><em>{i + 1}</em>{txt}</div>')
                js.append(f'    tl.fromTo("#t{i}", {RISE}, {max(0.3, L(ft))});')
        body.append('    </div>')
        if c.get("src"):
            body.append(f'    <div class="src" id="srcl">{c["src"]}</div>')
            js.append(f'    tl.fromTo("#srcl", {POP_L}, 0.1);')
        if c.get("chip"):
            body.append(f'    <div class="chip" id="chip">{c["chip"]}</div>')
            js.append(f'    tl.fromTo("#chip", {POP_L}, 0.05);')
        js.append(f'    tl.to(["#z"{", " + chr(34) + "#bd" + chr(34) if not split else ""}{", " + chr(34) + "#srcl" + chr(34) if c.get("src") else ""}{", " + chr(34) + "#chip" + chr(34) if c.get("chip") else ""}], '
                  f'{{ opacity: 0, filter: "blur(6px)", duration: 0.22, ease: "power2.in" }}, {round(dur - 0.25, 2)});')
        return sid, start, dur, scene_html(sid, css, "\n".join(body), "\n".join(js))

    def outro(self):
        sid = "h-outro"
        css = """
    #root { background: #07111f; }
    #o-still { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; opacity: .32; }
    #o-shade { position: absolute; inset: 0; background: radial-gradient(800px 900px at 50% 48%, rgba(7,17,31,.35), rgba(7,17,31,.95) 80%); }
    #o-box { position: absolute; left: 70px; top: 610px; width: 940px; height: 700px; text-align: center; }
    #o-rule { position: absolute; left: 370px; top: 0; width: 200px; height: 4px; background: #f2c55c; }
    #o-k { position: absolute; left: 0; top: 34px; width: 940px; font-size: 28px; font-weight: 800; letter-spacing: .2em; color: #c9d2e0; }
    #o-t { position: absolute; left: 0; top: 86px; width: 940px; font-size: 78px; font-weight: 900; line-height: 1.04; color: #f8d77e;
      text-shadow: 0 1px 0 #e0b04f, 0 2px 0 #d3a344, 0 3px 0 #c4953a, 0 4px 0 #b28430, 0 5px 0 #9c7226, 0 6px 0 #845f1d, 0 7px 0 #6c4c16, 0 20px 34px rgba(0,0,0,.8); }
    #o-n { position: absolute; left: 0; top: 330px; width: 940px; font-size: 44px; font-weight: 900; color: #f4f6fa; }
    #o-r { position: absolute; left: 0; top: 392px; width: 940px; font-size: 32px; font-weight: 800; letter-spacing: .14em; color: #f2c55c; }
    #o-src { position: absolute; left: 60px; top: 500px; width: 820px; font-size: 28px; font-weight: 500; line-height: 1.35; color: rgba(231,235,242,.78); }"""
        body = f"""    <img id="o-still" src="assets/img/end-{self.s['id']}.jpg" alt="" />
    <div id="o-shade"></div>
    <div id="o-box">
      <div id="o-rule"></div>
      <div id="o-k">{self.s.get("outro_kicker", "PARLIMEN PARIT, PERAK")}</div>
      <div id="o-t" style="font-size: {min(78, int(920 / (max(len(re.sub("<[^>]+>|&amp;", "x", p_)) for p_ in re.split("<br ?/?>", self.s["outro"])) * 0.68)))}px">{self.s["outro"]}</div>
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
        return sid, self.speech_end, 3.5, scene_html(sid, css, body, js)

    # -------------------------------------------------------------- captions
    def captions(self):
        out_words = []
        hook_end = self.segs[0][2] - self.segs[0][1] if len(self.segs) > 1 else 0
        fixes = self.s.get("fix", {})
        for ci, (f, a, b, o) in enumerate(self.segs):
            for i, (s, e, t) in enumerate(words(f)):
                key = (f, i)
                if key in fixes:
                    t = fixes[key]
                    if t is None:
                        continue
                else:
                    t = norm(t)
                mid = (s + e) / 2
                if not (a <= mid < b):
                    continue
                cs, ce = max(s, a), min(e, b)
                out_words.append([round(cs - a + o, 3), round(max(ce, cs + 0.05) - a + o, 3), t, ci])
        # whisper capitalises at its own segment starts: lower-case words that follow
        # a non-final token unless they are proper nouns / acronyms
        proper = set(PROPER) | set(self.s.get("proper", []))
        prev = "."
        for w in out_words:
            t = w[2]
            if t and t[0].isupper() and not prev.endswith((".", "?", "!", "”")) and t.strip(".,?!") not in proper \
                    and not (len(t) > 1 and t[:2].isupper()):
                w[2] = t[0].lower() + t[1:]
            prev = w[2] or prev
        # text substitutions on joined phrases (multi-word fixes)
        for pat, rep in self.s.get("subs", []):
            joined = "\x00".join(w[2] for w in out_words)
            joined = re.sub(pat, rep, joined, flags=re.I)
            parts = joined.split("\x00")
            if len(parts) == len(out_words):
                for w, p in zip(out_words, parts):
                    w[2] = p
        key_re = re.compile(self.s.get("keys", r"^$"), re.I)
        groups, cur = [], []
        for w in out_words:
            if w[3] == 0 and hook_end and len(self.segs) > 1:
                continue  # hook is set as kinetic type
            if not w[2].strip():
                continue
            if cur:
                gap = w[0] - cur[-1][1]
                if (len(cur) >= 4 or gap > 0.35 or w[3] != cur[-1][3]
                        or cur[-1][2].endswith((".", "?", "!")) or (cur[-1][2].endswith(",") and len(cur) >= 2)
                        or len(" ".join(x[2] for x in cur + [w])) > 30):
                    groups.append(cur)
                    cur = []
            cur.append(w)
        if cur:
            groups.append(cur)
        rows = []
        for gi, g in enumerate(groups):
            start = max(0.0, g[0][0] - 0.05)
            end = g[-1][1] + 0.6
            if gi + 1 < len(groups):
                end = min(end, max(0.0, groups[gi + 1][0][0] - 0.05))
            end = min(end, self.speech_end)
            if end - start < 0.12:
                end = start + 0.12
            rows.append((start, end, g))
        markup, script = [], []
        for gi, (start, end, g) in enumerate(rows):
            spans = []
            for wi, w in enumerate(g):
                core = re.sub(r"[^\w%.,\-]", "", w[2]).strip(".,")
                cls = "w k" if (key_re.match(core) or re.match(r"^(RM)?[\d][\d,.]*%?$", core)) else "w"
                spans.append(f'<span class="{cls}" id="cw{gi}_{wi}">{html.escape(w[2])}</span>')
            markup.append(f'    <div class="cg" id="cg{gi}">' + " ".join(spans) + "</div>")
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
    tl.set({{}}, {{}}, {self.speech_end});
    window.__timelines["captions"] = tl;
  </script>
</template>
"""
        with open(os.path.join(self.dir, "transcript.txt"), "w") as fh:
            for start, end, g in rows:
                fh.write(f"{start:7.2f}-{end:7.2f}  " + " ".join(w[2] for w in g) + "\n")
        return doc

    # -------------------------------------------------------------- index + write
    def build(self, head_html):
        os.makedirs(os.path.join(self.dir, "compositions"), exist_ok=True)
        link = os.path.join(self.dir, "assets")
        if not os.path.islink(link):
            os.symlink("../assets", link)
        json.dump({"id": self.s["id"], "name": self.s["id"], "createdAt": "2026-11-25T03:00:00.000Z"},
                  open(os.path.join(self.dir, "meta.json"), "w"), indent=2)
        json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                   "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
                   "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
                   "media": {"autoProxy": True}}, open(os.path.join(self.dir, "hyperframes.json"), "w"), indent=2)
        scenes = []
        multi = len(self.segs) > 1
        if multi:
            scenes.append(self.hook())
            hook_end = self.segs[0][2] - self.segs[0][1]
        else:
            hook_end = 0.0
        id_start = round(hook_end, 2)
        first_card = min([self.o(*c["at"]) for c in self.s["cards"]] + [self.speech_end])
        id_dur = round(min(6.0, max(3.5, first_card - id_start - 0.1)), 2)
        scenes.append(self.ident(id_start, id_dur, self.s["topic"]))
        # cards in order; each runs until the next card (or its own 'until')
        cards = sorted(self.s["cards"], key=lambda c: self.o(*c["at"]))
        timeline = []
        for k, c in enumerate(cards):
            st = max(self.o(*c["at"]), id_start + id_dur + 0.05)
            nx = self.o(*cards[k + 1]["at"]) if k + 1 < len(cards) else self.speech_end
            en = self.o(*c["until"]) if c.get("until") else nx
            en = min(en, nx, self.speech_end) - 0.05
            if en - st < 1.0:
                continue
            timeline.append((c, round(st, 2), round(en, 2)))
            scenes.append(self.card(len(timeline), c, round(st, 2), round(en, 2)))
        scenes.append(self.outro())
        for sid, st, du, doc in scenes:
            open(os.path.join(self.dir, "compositions", sid + ".html"), "w").write(doc)
        open(os.path.join(self.dir, "compositions", "captions.html"), "w").write(self.captions())

        # videos
        vids = []
        for i, (f, a, b, o) in enumerate(self.segs):
            fo = "0.25" if i == len(self.segs) - 1 else "0.05"
            vids.append(f"""          <video id="v{i}" class="clip" src="assets/footage/{self.s['id']}/s{i:02d}.mp4" playsinline data-has-audio="true"
            data-start="{o:.2f}" data-duration="{b - a:.2f}" data-media-start="{self.seg_media_start(i):.3f}" data-fade-in="0.04" data-fade-out="{fo}"
            data-volume="1" data-track-index="1"></video>""")
        hosts = []
        for sid, st, du, _ in scenes:
            z = 12 if sid == "h-outro" else 10
            hosts.append(f"""      <div id="{sid}" class="scene-host" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html"
        data-start="{st}" data-duration="{du}" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index:{z}"></div>""")
        # camera + sfx
        cam, sfx = [], []
        if multi:
            hb = self.hook_big_out
            cam += [f'      tl.set(cam, {{ scale: {HOOK_S}, x: 0, y: {cam_y(self.segs[0][0], "hook")} }}, 0);',
                    f'      zoom(0, {HOOK_S + 0.06:.2f}, {max(0.5, hb - 0.12):.2f}, "power1.inOut");', f'      zoom({hb:.2f}, {HOOK_S + 0.16:.2f}, 0.16); shake({hb:.2f});',
                    f'      flash({id_start:.2f}); cut({id_start:.2f}, BASE.s, {cam_y(self.segs[1][0], "full")}); sweep({id_start + 0.6:.2f});']
            sfx += [("impact-bass-2", 0, 0.11), ("impact-bass-1", round(hb, 2), 0.09), ("whoosh", round(max(0, id_start - 0.25), 2), 0.36)]
        else:
            cam += [f'      tl.set(cam, {{ scale: {BASE_S}, x: 0, y: {cam_y(self.segs[0][0], "full")} }}, 0);']
            sfx += [("impact-bass-2", 0, 0.1)]
        sfx.append(("pop", round(id_start + 0.75, 2), 0.35))
        cam.append(f'      zoom({id_start:.2f}, {BASE_S + 0.05:.2f}, {id_dur:.2f}, "power1.inOut");')
        # jump cuts: alternate framing
        # split windows from card modes
        on = None
        prev_end = None
        windows = []
        for c, st, en in timeline:
            if c.get("mode", "split") == "split":
                if on is None:
                    on = st
                elif prev_end is not None and st - prev_end > 1.2:
                    windows.append((on, prev_end))
                    on = st
                prev_end = en
            else:
                if on is not None:
                    windows.append((on, prev_end))
                    on = None
                    prev_end = None
        if on is not None:
            windows.append((on, prev_end))
        def seg_at(t):
            k = 0
            for i, (f, a, b, o) in enumerate(self.segs):
                if t >= o - 1e-6:
                    k = i
            return self.segs[k][0]
        in_split = lambda t: any(a_ - 0.15 <= t <= b_ + 0.6 for a_, b_ in windows)
        for a_, b_ in windows:
            on_t, off_t = max(0, a_ - 0.15), min(self.speech_end - 0.1, b_ + 0.05)
            cam.append(f'      splitOn({on_t:.2f}, {cam_y(seg_at(on_t), "split")}); splitOff({off_t:.2f}, {cam_y(seg_at(off_t + 0.8), "full")});')
            sfx.append(("whoosh-short", round(max(0, a_ - 0.3), 2), 0.28))
        alt = [BASE_S, BASE_S + 0.07]
        for i, (f, a, b, o) in enumerate(self.segs[1:], 1):
            if i > 1:
                sp = in_split(o)
                cam.append(f'      cut({o:.2f}, {BASE_S if sp else alt[i % 2]}, {cam_y(f, "split" if sp else "full")});')
                sfx.append(("whoosh", round(max(0, o - 0.2), 2), 0.3))
        # full-frame stretches between windows: slow push
        for c, st, en in timeline:
            if c.get("mode") == "full":
                cam.append(f'      zoom({st:.2f}, {BASE_S + 0.1:.2f}, {max(0.5, en - st):.2f}, "power1.inOut");')
            sfx.append(("pop", round(st + 0.3, 2), 0.3))
        sfx.append(("whoosh-cinematic", round(max(0, self.speech_end - 2.4), 2), 0.24))
        aud = []
        for n, (f, st, vol) in enumerate(sfx):
            dur = {"whoosh": 0.57, "whoosh-short": 0.57, "pop": 0.72, "impact-bass-1": 1.4, "impact-bass-2": 1.4, "whoosh-cinematic": 3.9}[f]
            extra = ' data-fade-out="0.7"' if f.startswith("impact") else (' data-fade-out="1.0"' if f == "whoosh-cinematic" else "")
            aud.append(f'      <audio id="sx{n:02d}" class="clip" src="assets/sfx/{f}.mp3" data-start="{st}" data-duration="{dur}"{extra} data-volume="{vol}" data-track-index="{5 + n % 5}"></audio>')
        head = head_html.replace("<title>4 Isu Seri Iskandar — Dewan Rakyat</title>", f"<title>{html.escape(self.s['title'])}</title>")
        body = f"""  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{self.total}" data-width="1080" data-height="1920">
      <div id="bg"></div>
      <div id="bg-fins"></div>

      <div id="mask">
        <div id="cam">
          <!-- Original Dewan Rakyat footage, cropped to 9:16 around the MP; cleaned voice baked in -->
{chr(10).join(vids)}
        </div>
      </div>
      <div id="pframe"><span id="pframe-tag">RAKAMAN ASAL</span></div>
      <div id="grade-vignette"></div>
      <div id="scrim"></div>

      <div id="bug"><i></i>UCAPAN DI DEWAN RAKYAT</div>

{chr(10).join(hosts)}

      <div id="captions" class="scene-host" data-composition-id="captions" data-composition-src="compositions/captions.html"
        data-start="0" data-duration="{self.speech_end}" data-track-index="3" data-track-kind="captions" data-width="1080" data-height="1920" style="z-index:15"></div>

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
      const BASE = {{ s: {BASE_S} }};

      function splitOn(t, y) {{
        tl.fromTo(mask, {{ clipPath: FULL }}, {{ clipPath: PANEL, duration: 0.7, ease: "power3.inOut", immediateRender: false }}, t);
        tl.to(cam, {{ y, scale: BASE.s, duration: 0.7, ease: "power3.inOut" }}, t);
        tl.fromTo(pf, {{ opacity: 0, scale: 1.04 }}, {{ opacity: 1, scale: 1, duration: 0.5, ease: "power2.out", immediateRender: false }}, t + 0.35);
        tl.to("#scrim", {{ opacity: 0.35, duration: 0.6, ease: "power2.inOut" }}, t);
      }}
      function splitOff(t, y, d = 0.5) {{
        tl.to(pf, {{ opacity: 0, duration: 0.2, ease: "power2.in" }}, t);
        tl.fromTo(mask, {{ clipPath: PANEL }}, {{ clipPath: FULL, duration: d, ease: "power3.inOut", immediateRender: false }}, t);
        tl.to(cam, {{ y, duration: d, ease: "power3.inOut" }}, t);
        tl.to("#scrim", {{ opacity: 1, duration: d, ease: "power2.inOut" }}, t);
      }}
      function sweep(t) {{
        tl.fromTo("#sweep", {{ x: 0, rotation: 18, opacity: 0 }}, {{ x: 2300, opacity: 1, duration: 0.9, ease: "power2.inOut", immediateRender: false }}, t);
        tl.set("#sweep", {{ opacity: 0 }}, t + 0.92);
      }}
      function flash(t, o = 0.55) {{
        tl.fromTo("#flash", {{ opacity: 0 }}, {{ opacity: o, duration: 0.06, ease: "power2.out", immediateRender: false }}, Math.max(0, t - 0.06));
        tl.to("#flash", {{ opacity: 0, duration: 0.35, ease: "power2.out" }}, t + 0.01);
      }}
      function zoom(t, s, d, ease = "expo.out") {{ tl.to(cam, {{ scale: s, duration: d, ease }}, t); }}
      function cut(t, s, y) {{ tl.set(cam, {{ scale: s, y }}, t); }}
      function shake(t) {{ tl.fromTo(cam, {{ x: 0 }}, {{ x: 8, duration: 0.05, ease: "none", yoyo: true, repeat: 3, immediateRender: false }}, t); }}

      tl.set(mask, {{ clipPath: FULL }}, 0);
      tl.set("#flash", {{ opacity: 0 }}, 0);
      tl.set("#sweep", {{ opacity: 0, x: 0, rotation: 18 }}, 0);
      tl.set(pf, {{ opacity: 0, scale: 1 }}, 0);

{chr(10).join(cam)}

      tl.to("#bug", {{ opacity: 0, duration: 0.3 }}, {self.speech_end - 0.2:.2f});
      tl.to("#cam", {{ opacity: 0, duration: 0.5, ease: "power2.in" }}, {self.speech_end - 0.3:.2f});
      tl.set({{}}, {{}}, {self.total});

      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
        open(os.path.join(self.dir, "index.html"), "w").write(head + body)
        return self
