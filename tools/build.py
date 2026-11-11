#!/usr/bin/env python3
"""Build one political-speech clip from a spec.

  python tools/build.py specs/VIDEO_01.json [--html-only]

Produces
  assets/clips/<ID>.mp4      cut + graded 1080x1920 footage (muted in the composition)
  assets/clips/<ID>.m4a      final mix: cleaned speech + ducked score + SFX
  <ID>.html                  HyperFrames composition (render with -c <ID>.html)
  deliverables/<ID>/         EDL, SRT, transcript, production notes data
Source footage and transcripts live outside the repo (SRC_DIR, default /home/user/src).
"""
import json, os, re, subprocess, sys, html, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ.get("SRC_DIR", "/home/user/src")
PY = os.environ.get("PY", "/home/user/src/venv/bin/python")
SFX = os.path.join(ROOT, ".claude/skills/media-use/audio/assets/sfx")
W, H, FPS = 1080, 1920, 30

GLOBAL_FIX = {
    "FAS": "PAS", "Perkataan": "Pakatan", "perkataan": "Pakatan", "Perkaitan": "Perikatan",
    "muhafakat": "muafakat", "Muhafakat": "Muafakat", "Biasa": "Barisan", "berisai": "Barisan",
}

def sh(cmd):
    r = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-3000:]); raise SystemExit(f"failed: {cmd if isinstance(cmd,str) else ' '.join(cmd)[:300]}")
    return r.stdout

def esc(s): return html.escape(s, quote=True)

# ---------------------------------------------------------------- words / pieces
def load_words(src):
    segs = json.load(open(os.path.join(SRC, f"{src}.turbo.json")))
    out = []
    for s in segs:
        for w in s["words"]:
            t = w["w"].strip()
            if ((t.startswith("-") and out and w["s"] - out[-1]["e"] < 2.5) or (re.match(r"^[,.][\w]", t) and out and w["s"] - out[-1]["e"] < 0.8)):
                out[-1]["t"] = out[-1]["t"].rstrip(",.") + t; out[-1]["e"] = w["e"]; continue
            if t: out.append({"t": t, "s": w["s"], "e": w["e"]})
    return out

def split_range(words, a, b, gap):
    ws = [w for w in words if w["s"] >= a - 0.05 and w["e"] <= b + 0.3]
    if not ws: return [[a, b]]
    pieces, cur = [], [ws[0]]
    for w in ws[1:]:
        if w["s"] - cur[-1]["e"] > gap:
            pieces.append(cur); cur = [w]
        else: cur.append(w)
    pieces.append(cur)
    out = []
    for i, p in enumerate(pieces):
        s = max(a, p[0]["s"] - 0.14) if i else a
        e = min(b, p[-1]["e"] + 0.22) if i < len(pieces) - 1 else b
        out.append([round(s, 3), round(e, 3)])
    return out

def build_edl(spec, words):
    gap = spec.get("gap", 0.9)
    edl = []
    if spec.get("hook"):
        a, b = spec["hook"]
        edl.append({"a": a, "b": b, "kind": "hook"})
    for r in spec["ranges"]:
        for a, b in split_range(words, r[0], r[1], gap):
            edl.append({"a": a, "b": b, "kind": "body"})
    edl[-1]["b"] += spec.get("tail", 1.6)
    edl[-1]["tail"] = spec.get("tail", 1.6)
    o = 0.0
    for p in edl:
        p["o"] = round(o, 3); o += p["b"] - p["a"]
    return edl, round(o, 3)

def remap(words, edl, fix):
    out = []
    for p in edl:
        for w in words:
            if w["s"] >= p["a"] - 0.02 and w["s"] < p["b"] - (p.get("tail", 0)) and w["e"] <= p["b"] + 0.25:
                t = w["t"]
                core = re.sub(r"[^\w'-]", "", t)
                if core in fix: t = t.replace(core, fix[core])
                s = p["o"] + max(0, w["s"] - p["a"]); e = p["o"] + min(p["b"], w["e"]) - p["a"]
                out.append({"t": t, "s": round(s, 3), "e": round(max(e, s + 0.08), 3), "piece": edl.index(p)})
    return out

def find_phrase(ow, phrase, after=0.0):
    toks = [re.sub(r"[^\w]", "", x.lower()) for x in phrase.split()]
    seq = [re.sub(r"[^\w]", "", w["t"].lower()) for w in ow]
    for i in range(len(ow)):
        if ow[i]["s"] < after: continue
        if all(i + k < len(seq) and (seq[i + k] == toks[k] or (len(toks[k]) > 3 and seq[i + k].startswith(toks[k]))) for k in range(len(toks))):
            return i
    raise SystemExit(f"phrase not found: {phrase!r} after {after}")

# ---------------------------------------------------------------- media
def cut_media(spec, edl, D, cid):
    src = os.path.join(SRC, spec["source"] + ".mp4")
    os.makedirs(os.path.join(ROOT, f"episodes/{cid}/assets/clips"), exist_ok=True)
    tmp = os.path.join(SRC, "work", cid); os.makedirs(tmp, exist_ok=True)
    vparts, aparts, fc = [], [], []
    for i, p in enumerate(edl):
        dur = p["b"] - p["a"]
        fc.append(f"[0:v]trim={p['a']}:{p['b']},setpts=PTS-STARTPTS[v{i}]")
        af = f"[0:a]atrim={p['a']}:{p['b']},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={max(0,dur-0.03):.3f}:d=0.03"
        if p.get("tail"): af += f",afade=t=out:st={max(0,dur-p['tail']-0.1):.3f}:d={p['tail']:.3f}"
        fc.append(af + f"[a{i}]")
        vparts.append(f"[v{i}][a{i}]")
    n = len(edl)
    fc.append("".join(vparts) + f"concat=n={n}:v=1:a=1[vc][ac]")
    grade = spec.get("grade", "eq=contrast=1.06:brightness=0.012:saturation=1.07:gamma=0.98")
    fc.append(f"[vc]hqdn3d=1.2:1.2:4:4,scale={W}:{H}:flags=lanczos,{grade},unsharp=5:5:0.45:5:5:0,fps={FPS},format=yuv420p[vo]")
    fc.append("[ac]aresample=48000,highpass=f=85,lowpass=f=12500,afftdn=nf=-28:nr=10,"
              "equalizer=f=220:t=q:w=1.0:g=-1.5,equalizer=f=3200:t=q:w=1.2:g=2.5,"
              "acompressor=threshold=-21dB:ratio=3:attack=8:release=160:makeup=2,"
              "loudnorm=I=-16:TP=-1.5:LRA=9[ao]")
    vout = os.path.join(ROOT, f"episodes/{cid}/assets/clips/{cid}.mp4"); speech = os.path.join(tmp, "speech.wav")
    sh(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", ";".join(fc),
        "-map", "[vo]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-g", "30", "-an", vout,
        "-map", "[ao]", "-ac", "1", "-ar", "48000", speech])
    return vout, speech, tmp

def mix_audio(spec, D, speech, tmp, cid, cues):
    music = os.path.join(tmp, "music.wav")
    sh([PY, "-I", os.path.join(ROOT, "tools/score.py"), f"{D:.3f}", spec.get("mood", "serious"), str(spec.get("seed", 7)), music])
    inputs = ["-i", speech, "-i", music]
    fc = ["[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,asplit=2[sp][key]",
          # music: base level, ducked under speech, lifted in the final stretch
          f"[1:a]aresample=48000,volume='0.30+0.30*clip((t-{D-14:.2f})/10,0,1)':eval=frame[mu]",
          "[mu][key]sidechaincompress=threshold=0.02:ratio=7:attack=40:release=650:makeup=1[duck]"]
    labels = ["[sp]", "[duck]"]
    for k, (name, t, vol) in enumerate(cues):
        inputs += ["-i", os.path.join(SFX, name)]
        ms = int(max(0, t) * 1000)
        fc.append(f"[{k+2}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol},adelay={ms}|{ms}[s{k}]")
        labels.append(f"[s{k}]")
    fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first,volume=0.78,alimiter=limit=0.89,"
              f"afade=t=out:st={D-0.6:.3f}:d=0.6[out]")
    out = os.path.join(ROOT, f"episodes/{cid}/assets/clips/{cid}.m4a")
    sh(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[out]",
        "-t", f"{D:.3f}", "-c:a", "aac", "-b:a", "192k", out])
    return out

# ---------------------------------------------------------------- captions
def caption_groups(ow, maxw=4, maxc=26):
    groups, cur = [], []
    for i, w in enumerate(ow):
        if cur:
            prev = ow[cur[-1]]
            chars = sum(len(ow[j]["t"]) + 1 for j in cur) + len(w["t"])
            if (w["s"] - prev["e"] > 0.35 or len(cur) >= maxw or chars > maxc or w["piece"] != prev["piece"]
                    or re.search(r"[.?!]$", prev["t"])):
                groups.append(cur); cur = []
        cur.append(i)
    if cur: groups.append(cur)
    return groups

def srt_time(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

# ---------------------------------------------------------------- icons
ICON = {
 "money": '<rect x="6" y="18" width="52" height="30" rx="4"/><circle cx="32" cy="33" r="8"/><path d="M14 26v14M50 26v14"/>',
 "people": '<circle cx="22" cy="22" r="8"/><circle cx="44" cy="24" r="7"/><path d="M8 52c2-12 10-17 14-17s12 5 14 17M34 52c2-9 6-13 10-13s9 4 11 13"/>',
 "handshake": '<path d="M4 30l12-12 10 4 8-4 14 2 12 10"/><path d="M16 18l-4 22 14 14 6-4 6 4 12-14 6-10"/><path d="M24 30l10 10M30 26l10 10"/>',
 "scale": '<path d="M32 8v46M14 54h36M12 16h40"/><path d="M12 16l-8 18h16zM52 16l-8 18h16z"/>',
 "ballot": '<rect x="10" y="26" width="44" height="28" rx="3"/><path d="M22 26V10h20v16M27 18l4 4 7-8"/>',
 "flag": '<path d="M14 58V6M14 8h34l-8 10 8 10H14"/>',
 "warning": '<path d="M32 6l28 50H4z"/><path d="M32 24v14M32 46v2"/>',
 "chart": '<path d="M8 56h50M14 56V38M28 56V26M42 56V32M56 56V12"/>',
 "mosque": '<path d="M12 56V34c0-10 20-10 20-24 0 14 20 14 20 24v22z"/><path d="M6 56V24M58 56V24M26 56V44h12v12"/>',
 "house": '<path d="M6 30L32 8l26 22"/><path d="M12 26v28h40V26M26 54V38h12v16"/>',
 "road": '<path d="M22 58L28 6M42 58L36 6M32 12v6M32 26v6M32 40v8"/>',
 "flood": '<path d="M6 40c6-6 10 6 16 0s10 6 16 0 10 6 16 0M6 52c6-6 10 6 16 0s10 6 16 0 10 6 16 0"/><path d="M14 30V14l18-8 18 8v16"/>',
 "school": '<path d="M4 22L32 10l28 12-28 12z"/><path d="M14 27v14c8 8 28 8 36 0V27M58 23v18"/>',
 "quote": '<path d="M10 40c0-12 4-20 14-24M34 40c0-12 4-20 14-24"/><circle cx="16" cy="42" r="6"/><circle cx="40" cy="42" r="6"/>',
 "mic": '<rect x="24" y="6" width="16" height="30" rx="8"/><path d="M14 30c0 10 8 16 18 16s18-6 18-16M32 46v12M22 58h20"/>',
 "crown": '<path d="M6 46l6-30 14 14 6-18 6 18 14-14 6 30z"/><path d="M8 54h48"/>',
 "link": '<rect x="6" y="24" width="28" height="16" rx="8"/><rect x="30" y="24" width="28" height="16" rx="8"/>',
 "doc": '<path d="M14 6h26l12 12v40H14z"/><path d="M40 6v12h12M22 30h22M22 40h22M22 50h14"/>',
 "map": '<path d="M6 14l16-6 20 6 16-6v42l-16 6-20-6-16 6z"/><path d="M22 8v42M42 14v42"/>',
 "clock": '<circle cx="32" cy="32" r="24"/><path d="M32 18v14l10 6"/>',
 "shield": '<path d="M32 6l22 8v16c0 14-10 24-22 28C20 54 10 44 10 30V14z"/><path d="M22 32l8 8 14-16"/>',
}
def icon(name, size=88, cls="ic"):
    return (f'<svg class="{cls}" width="{size}" height="{size}" viewBox="0 0 64 64" fill="none" '
            f'stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round">{ICON[name]}</svg>')

# ---------------------------------------------------------------- composition
CSS = r"""
:root{--navy:#081634;--deep:#040b1e;--gold:#e2b84a;--gold2:#ffd76a;--blue:#2f9bff;--ink:#ffffff}
*{margin:0;padding:0;box-sizing:border-box}
html,body{margin:0;width:1080px;height:1920px;overflow:hidden;background:#000}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Montserrat,Inter,sans-serif;color:#fff}
#cam{position:absolute;left:0;top:0;width:1080px;height:1920px;transform-origin:540px 960px;will-change:transform}
#v{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover}
.layer{position:absolute;inset:0;pointer-events:none}
#vig{background:radial-gradient(ellipse 85% 70% at 50% 45%,rgba(0,0,0,0) 55%,rgba(2,6,20,.55) 100%)}
#scrimTop{background:linear-gradient(180deg,rgba(4,11,30,.86) 0%,rgba(4,11,30,.62) 22%,rgba(4,11,30,0) 38%)}
#scrimBot{background:linear-gradient(0deg,rgba(4,11,30,.9) 0%,rgba(4,11,30,.72) 30%,rgba(4,11,30,0) 50%)}
.kicker{font:700 30px/1 Montserrat;letter-spacing:.32em;color:var(--gold2);text-transform:uppercase}
/* hook */
#hook{position:absolute;left:0;top:0;width:1080px;height:1920px}
#hook .box{position:absolute;left:70px;right:70px;top:250px;text-align:center}
#hook .rule{height:4px;width:520px;margin:26px auto 0;background:linear-gradient(90deg,transparent,var(--gold2),transparent);transform-origin:50% 50%}
#hook h1{margin-top:26px;font:900 92px/1.04 Montserrat;text-transform:uppercase;letter-spacing:-.01em;
  text-shadow:0 2px 0 #b98a1d,0 4px 0 #8a6410,0 6px 0 #5e430a,0 14px 30px rgba(0,0,0,.75)}
#hook h1 .hl{color:var(--gold2)}
#hook h1 .ln{display:block}
#flash{position:absolute;inset:0;opacity:0;background:radial-gradient(circle at 50% 45%,rgba(120,190,255,.95),rgba(30,110,255,.55) 45%,rgba(4,11,30,0) 80%)}
/* lower third */
#l3{position:absolute;left:0;top:0;width:1080px;height:1920px}
#l3 .wrap{position:absolute;left:48px;top:948px;width:900px}
#l3 .bar{position:absolute;left:0;top:0;width:10px;height:196px;background:linear-gradient(180deg,var(--gold2),var(--gold));box-shadow:0 0 22px rgba(255,215,106,.7)}
#l3 .panel{position:absolute;left:10px;top:0;height:196px;width:860px;background:linear-gradient(90deg,rgba(8,22,52,.96),rgba(8,22,52,.86) 70%,rgba(8,22,52,0));transform-origin:0 50%}
#l3 .name{position:absolute;left:44px;top:30px;white-space:nowrap;font:800 43px/1.1 Montserrat;letter-spacing:.01em;text-transform:uppercase}
#l3 .name.short{font-size:64px;top:22px}
#l3 .role{position:absolute;left:46px;top:100px;font:600 30px/1.1 Poppins;color:#cfe2ff;letter-spacing:.02em}
#l3 .line{position:absolute;left:46px;top:146px;height:3px;width:560px;background:linear-gradient(90deg,var(--blue),rgba(47,155,255,0));transform-origin:0 50%}
#l3 .topic{position:absolute;left:10px;top:-62px;padding:12px 26px;background:var(--gold);color:#081634;font:800 30px/1 Montserrat;letter-spacing:.12em;text-transform:uppercase}
/* topic tag */
.tag{position:absolute;left:0;top:0;width:1080px;height:1920px}
.tag .pill{position:absolute;left:60px;top:186px;display:flex;align-items:center;gap:16px;padding:14px 26px 14px 20px;
  background:rgba(8,22,52,.88);border:2px solid rgba(226,184,74,.85);border-radius:6px}
.tag .dot{width:16px;height:16px;border-radius:50%;background:var(--blue);box-shadow:0 0 14px var(--blue)}
.tag .tx{font:800 30px/1 Montserrat;letter-spacing:.12em;text-transform:uppercase;color:#fff}
/* fact cards */
.card{position:absolute;left:0;top:0;width:1080px;height:1920px}
.card .in{position:absolute;left:60px;right:60px;top:276px;min-height:300px;padding:34px 40px;
  background:linear-gradient(160deg,rgba(10,30,72,.93),rgba(4,11,30,.93));border:2px solid rgba(226,184,74,.75);
  border-radius:14px;box-shadow:0 20px 50px rgba(0,0,0,.55),inset 0 0 40px rgba(47,155,255,.12)}
.card .glow{position:absolute;left:60px;right:60px;top:276px;height:4px;background:linear-gradient(90deg,transparent,var(--blue),transparent);transform-origin:50% 50%}
.card .lbl{font:700 28px/1.2 Montserrat;letter-spacing:.2em;color:var(--gold2);text-transform:uppercase}
.card .ic{color:var(--gold2);flex:none}
.card .row{display:flex;align-items:center;gap:30px}
.card .big{font:900 128px/1 Montserrat;color:#fff;letter-spacing:-.02em;
  text-shadow:0 3px 0 #b98a1d,0 6px 0 #6b4d0c,0 14px 26px rgba(0,0,0,.6)}
.card .big .u{color:var(--gold2)}
.card .sub{margin-top:14px;font:600 36px/1.25 Poppins;color:#e8f0ff}
.card .src{margin-top:18px;font:500 22px/1 Inter;color:#9fb6dd;letter-spacing:.06em;font-style:italic}
.card .kw{font:900 84px/1.02 Montserrat;text-transform:uppercase;color:#fff;
  text-shadow:0 3px 0 #b98a1d,0 6px 0 #6b4d0c,0 12px 24px rgba(0,0,0,.6)}
.card .kw .g{color:var(--gold2)}
.card .kw .b{color:#8cc8ff}
.card .kl{display:block;overflow:visible}
.card .q{font:700 50px/1.22 Poppins;color:#fff}
.card .q .g{color:var(--gold2)}
.card .who{margin-top:20px;font:600 28px/1.2 Montserrat;color:#9fc9ff;letter-spacing:.04em}
.card .bl{display:flex;align-items:center;gap:20px;margin-top:20px;font:700 44px/1.15 Poppins;color:#fff}
.card .bl .n{flex:none;width:52px;height:52px;border-radius:50%;background:var(--gold);color:#081634;font:900 30px/52px Montserrat;text-align:center}
.card .tl{display:flex;justify-content:space-between;align-items:flex-start;margin-top:26px;position:relative}
.card .tl .track{position:absolute;left:40px;right:40px;top:30px;height:4px;background:rgba(255,255,255,.18)}
.card .tl .fill{position:absolute;left:40px;right:40px;top:30px;height:4px;background:linear-gradient(90deg,var(--gold2),var(--blue));transform-origin:0 50%}
.card .tl .node{position:relative;width:200px;text-align:center}
.card .tl .node .pt{width:26px;height:26px;margin:17px auto 0;border-radius:50%;background:var(--gold2);box-shadow:0 0 18px rgba(255,215,106,.8)}
.card .tl .node .y{margin-top:16px;font:900 46px/1 Montserrat;color:#fff}
.card .tl .node .d{margin-top:10px;font:600 26px/1.15 Poppins;color:#cfe2ff}
.card .pair{display:flex;align-items:center;justify-content:center;gap:34px;margin-top:6px}
.card .pair .p{padding:22px 34px;border-radius:12px;font:900 76px/1 Montserrat;color:#fff;background:rgba(47,155,255,.18);border:3px solid var(--blue)}
.card .pair .p.alt{background:rgba(226,184,74,.16);border-color:var(--gold2)}
.card .pair .plus{font:900 80px/1 Montserrat;color:var(--gold2)}
.card .center{text-align:center}
.card .bars{margin-top:22px}
.card .br{display:flex;align-items:center;gap:18px;margin-top:16px}
.card .br .bn{width:200px;flex:none;font:800 34px/1 Montserrat;color:#fff;text-align:right}
.card .br .bt{position:relative;flex:1;height:58px;background:rgba(255,255,255,.08);border-radius:6px;overflow:hidden}
.card .br .bf{position:absolute;left:0;top:0;bottom:0;border-radius:6px;transform-origin:0 50%}
.card .br .bv{width:190px;flex:none;font:900 40px/1 Montserrat;color:var(--gold2)}
.ring{position:relative;width:250px;height:250px;flex:none}
.ring svg{position:absolute;inset:0}
.ring .pv{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font:900 64px/1 Montserrat;color:#fff}
/* captions */
#caps{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:visible}
.cg{position:absolute;left:40px;right:40px;bottom:592px;text-align:center;opacity:0;overflow:visible}
.cg .w{display:inline-block;margin:0 15px;font:800 66px/1.14 Montserrat;text-transform:uppercase;color:#fff;
  -webkit-text-stroke:10px rgba(4,11,30,.92);paint-order:stroke fill;text-shadow:0 6px 16px rgba(0,0,0,.65)}
.cg .w.k{font-size:74px;color:var(--gold2);-webkit-text-stroke:10px rgba(40,24,0,.95);
  text-shadow:0 2px 0 #c99a2a,0 4px 0 #9a7114,0 6px 0 #6e500b,0 8px 0 #4a3606,0 14px 22px rgba(0,0,0,.7)}
.cg .w.e{font-size:72px;color:#7cc4ff;-webkit-text-stroke:10px rgba(0,16,46,.95);
  text-shadow:0 2px 0 #2f7fd6,0 4px 0 #1f5fae,0 6px 0 #144185,0 14px 22px rgba(0,0,0,.7)}
/* conclusion & end */
#concl{position:absolute;left:0;top:0;width:1080px;height:1920px}
#concl .box{position:absolute;left:60px;right:60px;top:262px;text-align:center}
#concl .msg{margin-top:22px;font:900 78px/1.06 Montserrat;text-transform:uppercase;
  text-shadow:0 3px 0 #b98a1d,0 6px 0 #6b4d0c,0 14px 30px rgba(0,0,0,.75)}
#concl .msg .g{color:var(--gold2)}
#concl .rule{height:4px;width:640px;margin:26px auto 0;background:linear-gradient(90deg,transparent,var(--gold2),transparent)}
#end{position:absolute;inset:0}
#end .bg{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 42%,rgba(10,30,72,.9),rgba(4,11,30,.97) 70%)}
#end .box{position:absolute;left:60px;right:60px;top:640px;text-align:center}
#end .nm{font:900 76px/1.08 Montserrat;letter-spacing:.02em;text-transform:uppercase}
#end .rl{margin-top:20px;font:600 34px/1.2 Poppins;color:#cfe2ff}
#end .rule{height:4px;width:520px;margin:34px auto;background:linear-gradient(90deg,transparent,var(--gold2),transparent)}
#end .ms{font:800 50px/1.15 Montserrat;color:var(--gold2);text-transform:uppercase}
"""

def kw_html(text):
    """'[gold]' and '{blue}' markup -> spans, '|' -> line break."""
    lines = []
    for ln in text.split("|"):
        ln = esc(ln)
        ln = re.sub(r"\[(.+?)\]", r'<span class="g">\1</span>', ln)
        ln = re.sub(r"\{(.+?)\}", r'<span class="b">\1</span>', ln)
        lines.append(ln)
    return lines

def fact_html(i, f):
    fid = f"f{i}"
    src = f'<div class="src">{esc(f["src"])}</div>' if f.get("src") else ""
    lbl = f'<div class="lbl">{esc(f["label"])}</div>' if f.get("label") else ""
    t = f["type"]
    if t == "number":
        body = (f'{lbl}<div class="row" style="margin-top:14px">{icon(f.get("icon","money"),110)}'
                f'<div><div class="big"><span class="u">{esc(f.get("prefix",""))}</span><span id="{fid}n">0</span>'
                f'<span class="u">{esc(f.get("suffix",""))}</span></div></div></div>'
                f'<div class="sub">{esc(f.get("sub",""))}</div>{src}')
    elif t == "percent":
        body = (f'{lbl}<div class="row" style="margin-top:16px"><div class="ring">'
                f'<svg width="250" height="250" viewBox="0 0 250 250"><circle cx="125" cy="125" r="104" stroke="rgba(255,255,255,.15)" stroke-width="20" fill="none"/>'
                f'<circle id="{fid}r" cx="125" cy="125" r="104" stroke="#ffd76a" stroke-width="20" fill="none" stroke-linecap="round" '
                f'stroke-dasharray="653.5" stroke-dashoffset="653.5" transform="rotate(-90 125 125)"/></svg>'
                f'<div class="pv"><span id="{fid}n">0</span>%</div></div><div class="sub" style="margin:0">{esc(f.get("sub",""))}</div></div>{src}')
    elif t == "keyword":
        lines = "".join(f'<span class="kl">{ln}</span>' for ln in kw_html(f["text"]))
        ic = icon(f["icon"], 96) if f.get("icon") else ""
        body = (f'<div class="row">{ic}<div>{lbl}<div class="kw" style="margin-top:8px">{lines}</div></div></div>'
                f'{"<div class=sub>"+esc(f["sub"])+"</div>" if f.get("sub") else ""}{src}')
    elif t == "quote":
        lines = "<br>".join(kw_html(f["text"]))
        body = (f'<div class="row" style="align-items:flex-start">{icon("quote",80)}<div>{lbl}'
                f'<div class="q" style="margin-top:12px">{lines}</div><div class="who">{esc(f.get("who",""))}</div>{src}</div></div>')
    elif t == "bullets":
        items = "".join(f'<div class="bl" id="{fid}b{j}"><span class="n">{j+1}</span><span>{esc(b["text"] if isinstance(b,dict) else b)}</span></div>'
                        for j, b in enumerate(f["items"]))
        ic = icon(f["icon"], 70) if f.get("icon") else ""
        body = f'<div class="row" style="gap:20px">{ic}{lbl}</div>{items}{src}'
    elif t == "timeline":
        nodes = "".join(f'<div class="node" id="{fid}t{j}"><div class="pt"></div><div class="y">{esc(n["y"])}</div><div class="d">{esc(n["d"])}</div></div>'
                        for j, n in enumerate(f["items"]))
        body = f'{lbl}<div class="tl"><div class="track"></div><div class="fill" id="{fid}fill"></div>{nodes}</div>{src}'
    elif t == "bars":
        mx = max(it["value"] for it in f["items"])
        rows = "".join(f'<div class="br" id="{fid}r{j}"><div class="bn">{esc(it["label"])}</div><div class="bt"><div class="bf" id="{fid}f{j}" '
                       f'style="width:{100*it["value"]/mx:.1f}%;background:{it.get("color","linear-gradient(90deg,#2f9bff,#7cc4ff)")}"></div></div>'
                       f'<div class="bv">{esc(it["show"])}</div></div>' for j, it in enumerate(f["items"]))
        body = f'{lbl}<div class="bars">{rows}</div>{"<div class=sub>"+esc(f["sub"])+"</div>" if f.get("sub") else ""}{src}'
    elif t == "pair":
        a, b = f["items"]
        body = (f'{lbl}<div class="pair"><div class="p" id="{fid}a">{esc(a)}</div><div class="plus" id="{fid}p">+</div>'
                f'<div class="p alt" id="{fid}b">{esc(b)}</div></div><div class="sub center">{esc(f.get("sub",""))}</div>{src}')
    else:
        raise SystemExit("unknown fact type " + t)
    return (f'<div id="{fid}" class="clip card" data-start="{f["start"]:.3f}" data-duration="{f["dur"]:.3f}" data-track-index="{4 + i % 2}">'
            f'<div class="glow" id="{fid}g"></div><div class="in" id="{fid}i">{body}</div></div>')

def fact_js(i, f):
    fid = f"f{i}"; s = 0; d = f["dur"]; js = []
    js.append(f'tl.fromTo("#{fid}i",{{opacity:0,y:40,scale:.96}},{{opacity:1,y:0,scale:1,duration:.45,ease:"power3.out"}},{f["start"]:.3f});')
    js.append(f'tl.fromTo("#{fid}g",{{scaleX:0,opacity:1}},{{scaleX:1,duration:.6,ease:"power2.out"}},{f["start"]:.3f});')
    js.append(f'tl.to("#{fid}g",{{opacity:0,duration:.6}},{f["start"]+0.7:.3f});')
    st = f["start"]
    t = f["type"]
    if t in ("number", "percent"):
        dec = f.get("decimals", 0)
        js.append(f'(function(){{var o={{v:0}};tl.to(o,{{v:{f["value"]},duration:{f.get("count",1.4)},ease:"power2.out",'
                  f'onUpdate:function(){{document.getElementById("{fid}n").textContent=o.v.toFixed({dec}).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g,",");}}}},{st+0.25:.3f});}})();')
        if t == "percent":
            js.append(f'tl.to("#{fid}r",{{attr:{{"stroke-dashoffset":{653.5*(1-f["value"]/100):.1f}}},duration:{f.get("count",1.4)},ease:"power2.out"}},{st+0.25:.3f});')
    elif t == "keyword":
        js.append(f'tl.from("#{fid} .kl",{{opacity:0,y:50,rotationX:-60,transformOrigin:"50% 100%",duration:.5,stagger:.18,ease:"back.out(1.6)"}},{st+0.15:.3f});')
        js.append(f'tl.from("#{fid} .ic",{{scale:.4,opacity:0,duration:.5,ease:"back.out(2)"}},{st+0.1:.3f});')
    elif t == "quote":
        js.append(f'tl.from("#{fid} .q",{{opacity:0,y:24,duration:.6,ease:"power2.out"}},{st+0.2:.3f});')
        js.append(f'tl.from("#{fid} .who",{{opacity:0,x:-30,duration:.5,ease:"power2.out"}},{st+0.8:.3f});')
    elif t == "bullets":
        for j, b in enumerate(f["items"]):
            bt = b["t"] if isinstance(b, dict) and "t" in b else st + 0.3 + j * 0.45
            js.append(f'tl.from("#{fid}b{j}",{{opacity:0,x:-60,duration:.45,ease:"power3.out"}},{bt:.3f});')
    elif t == "timeline":
        n = len(f["items"])
        times = [it.get("t", st + 0.3 + j * 0.6) for j, it in enumerate(f["items"])]
        js.append(f'tl.fromTo("#{fid}fill",{{scaleX:0}},{{scaleX:1,duration:{max(0.6, times[-1]-st):.2f},ease:"none"}},{st+0.2:.3f});')
        for j in range(n):
            js.append(f'tl.from("#{fid}t{j}",{{opacity:0,y:30,duration:.45,ease:"back.out(1.8)"}},{times[j]:.3f});')
    elif t == "bars":
        for j, it in enumerate(f["items"]):
            bt = it.get("t", st + 0.3 + j * 0.35)
            js.append(f'tl.from("#{fid}r{j}",{{opacity:0,x:-40,duration:.35,ease:"power2.out"}},{bt:.3f});')
            js.append(f'tl.fromTo("#{fid}f{j}",{{scaleX:0}},{{scaleX:1,duration:.9,ease:"power3.out"}},{bt+0.1:.3f});')
    elif t == "pair":
        js.append(f'tl.from("#{fid}a",{{x:-300,opacity:0,duration:.6,ease:"power3.out"}},{st+0.15:.3f});')
        js.append(f'tl.from("#{fid}b",{{x:300,opacity:0,duration:.6,ease:"power3.out"}},{st+0.15:.3f});')
        js.append(f'tl.from("#{fid}p",{{scale:0,rotation:-180,duration:.5,ease:"back.out(2)"}},{st+0.6:.3f});')
    js.append(f'tl.to("#{fid}i",{{opacity:0,y:-20,duration:.35,ease:"power2.in"}},{st+d-0.4:.3f});')
    return "\n".join(js)

def build(spec_path, html_only=False):
    spec = json.load(open(spec_path))
    cid = spec["id"]
    words = load_words(spec["source"])
    edl, D = build_edl(spec, words)
    fix = dict(GLOBAL_FIX); fix.update(spec.get("fix", {}))
    ow = remap(words, edl, fix)
    norm = lambda x: re.sub(r"[^\w'-]", "", x.lower())
    for frm, to in spec.get("phrase_fix", []):     # ["wrong words", "right words"] same word count
        fw, tw = frm.split(), to.split()
        assert len(fw) == len(tw), frm
        for i in range(len(ow) - len(fw) + 1):
            if all(norm(ow[i + k]["t"]) == norm(fw[k]) for k in range(len(fw))):
                for k in range(len(fw)):
                    trail = re.search(r"[.,?!;]*$", ow[i + k]["t"]).group(0)
                    nt = tw[k].replace("_", " ")
                    ow[i + k]["t"] = "" if nt == "~" else nt + ("" if re.search(r"[.,?!;]$", nt) else trail)
    ow = [w for w in ow if w["t"]]
    if spec.get("lowercase"):
        PROPER = {"islam","melaka","malaysia","persekutuan","nabi","allah","barisan","nasional","pakatan","harapan","perikatan","tabung",
                  "haji","agung","agong","tuanku","johor","adam","adli","hang","tuah","jaya","alor","gajah","september","saw","dewan",
                  "bahasa","pustaka","melayu","yb","komoditi","menteri","perdana","ketua","anwar","ibrahim","zahid","hamidi","terengganu","sarawak","sabah","penang","jerman","perancis","eropah","abdul","hadi","awang","najib","takir","seberang","wtc","kelantan","pengkalan","batu","datuk","seri","sahabat","abu","bakar",
                  "hifzul","hifzun","maqasid","umayyah","asri'u","kifayah","fardu","dipertuan","parlimen","sakau","perlembagaan"}
        prev_end = True
        for w in ow:
            core = re.sub(r"[^\w'-]", "", w["t"])
            if core[:1].isupper() and not core.isupper() and core.lower() not in PROPER and not prev_end:
                w["t"] = w["t"].replace(core, core.lower())
            prev_end = bool(re.search(r"[.?!]$", w["t"]))
    for k, v in spec.get("word_fix", {}).items():   # "index": "new text"
        ow[int(k)]["t"] = v
    hook_end = edl[0]["b"] - edl[0]["a"] if edl[0]["kind"] == "hook" else 0.0

    # resolve fact times from spoken phrases
    facts = []
    for f in spec.get("facts", []):
        f = dict(f)
        if "at" in f:
            i = find_phrase(ow, f["at"], f.get("after", 0)); f["start"] = round(max(0, ow[i]["s"] - 0.12), 3)
        f.setdefault("dur", 6.0)
        if f["type"] == "bullets":
            items = []
            for b in f["items"]:
                if isinstance(b, dict) and "at" in b:
                    b = dict(b); b["t"] = round(ow[find_phrase(ow, b["at"], f["start"])]["s"] - 0.1, 3)
                items.append(b)
            f["items"] = items
        if f["type"] == "bars":
            for it in f["items"]:
                if "at" in it: it["t"] = round(ow[find_phrase(ow, it["at"], f["start"])]["s"] - 0.1, 3)
        if f["type"] == "timeline":
            for it in f["items"]:
                if "at" in it: it["t"] = round(ow[find_phrase(ow, it["at"], f["start"])]["s"] - 0.1, 3)
        facts.append(f)
    # never overlap two cards: trim earlier card
    facts.sort(key=lambda f: f["start"])
    for a, b in zip(facts, facts[1:]):
        if a["start"] + a["dur"] > b["start"] - 0.05: a["dur"] = round(b["start"] - 0.05 - a["start"], 3)

    concl = spec.get("conclusion")
    end_dur = 3.2
    if concl:
        ci = find_phrase(ow, concl["at"], concl.get("after", D * 0.6)); concl["start"] = round(ow[ci]["s"] - 0.1, 3)
        concl["dur"] = round(D - end_dur + 0.3 - concl["start"], 3)
        for f in facts:
            if f["start"] < concl["start"] < f["start"] + f["dur"]: f["dur"] = round(concl["start"] - 0.05 - f["start"], 3)
    l3s = round(hook_end + 0.6, 3); l3d = spec.get("l3_dur", 9.0)
    topics = spec.get("topics", [{"label": spec["topic"]}])
    tstarts = []
    for k, tp in enumerate(topics):
        ts = l3s + l3d + 0.4 if k == 0 else round(ow[find_phrase(ow, tp["at"], tstarts[-1])]["s"] - 0.1, 3)
        tstarts.append(ts)
    tend = (concl["start"] if concl else D - end_dur)
    # cards hide the topic pill? no: pill sits above cards.

    # ---- media + audio cues
    cues = [("impact-bass-1.mp3", 0.05, 0.55), ("whoosh-cinematic.mp3", max(0, hook_end - 0.55), 0.5),
            ("whoosh-short.mp3", l3s, 0.35)]
    for f in facts: cues.append(("whoosh-short.mp3" if f["type"] != "number" else "impact-bass-2.mp3", f["start"], 0.28 if f["type"] != "number" else 0.4))
    if concl: cues.append(("impact-bass-2.mp3", concl["start"], 0.5))
    cues.append(("whoosh-cinematic.mp3", D - end_dur - 0.3, 0.4))
    if not html_only:
        vout, speech, tmp = cut_media(spec, edl, D, cid)
        mix_audio(spec, D, speech, tmp, cid, cues)

    # ---- camera: alternate punch-in per piece, slow push within, hook tighter
    fr = spec.get("frame", {"x": 540, "y": 900, "s": 1.15})
    focus = spec.get("focus", [])  # [[src_t, x, y, s?], ...]
    def frame_at(src_t):
        cur = dict(fr)
        for ft in focus:
            if ft[0] <= src_t + 0.01:
                cur = {"x": ft[1], "y": ft[2], "s": ft[3] if len(ft) > 3 else fr["s"]}
        return cur
    target = (540, spec.get("face_y", 760))
    cam_js = []
    for k, p in enumerate(edl):
        f0 = frame_at(p["a"])
        s = f0["s"] * (1.18 if p["kind"] == "hook" else (1.0 if k % 2 == 0 else 1.10))
        dur = p["b"] - p["a"]
        def txy(s):
            tx = target[0] - 540 - s * (f0["x"] - 540); ty = target[1] - 960 - s * (f0["y"] - 960)
            lx, ly = 540 * (s - 1), 960 * (s - 1)
            return max(-lx, min(lx, tx)), max(-ly, min(ly, ty))
        s2 = s * 1.035
        x1, y1 = txy(s); x2, y2 = txy(s2)
        cam_js.append(f'tl.set("#cam",{{scale:{s:.4f},x:{x1:.1f},y:{y1:.1f}}},{p["o"]:.3f});')
        cam_js.append(f'tl.to("#cam",{{scale:{s2:.4f},x:{x2:.1f},y:{y2:.1f},duration:{dur:.3f},ease:"none"}},{p["o"]:.3f});')

    # ---- captions
    kws = [k.lower() for k in spec.get("keywords", [])]
    ekws = [k.lower() for k in spec.get("keywords_blue", [])]
    groups = caption_groups(ow)
    cap_html, cap_js, srt = [], [], []
    for gi, g in enumerate(groups):
        gs = ow[g[0]]["s"]; ge = ow[g[-1]]["e"]
        nxt = ow[groups[gi + 1][0]]["s"] if gi + 1 < len(groups) else D
        ge2 = min(max(ge + 0.25, gs + 0.6), nxt - 0.02, D - end_dur)
        if gs >= D - end_dur: continue
        spans = []
        for j in g:
            raw = ow[j]["t"]; low = re.sub(r"[^\w-]", "", raw.lower())
            cls = "w k" if low in kws else ("w e" if low in ekws else "w")
            spans.append(f'<span class="{cls}" id="w{j}">{esc(raw.strip(",;"))}</span>')
        cap_html.append(f'<div class="cg" id="cg{gi}">{"".join(spans)}</div>')
        cap_js.append(f'tl.set("#cg{gi}",{{opacity:1,visibility:"visible"}},{gs - 0.05:.3f});')
        cap_js.append(f'tl.from("#cg{gi}",{{y:18,scale:.94,duration:.16,ease:"power2.out"}},{gs - 0.05:.3f});')
        for j in g:
            cls_k = re.sub(r"[^\w-]", "", ow[j]["t"].lower()) in kws + ekws
            cap_js.append(f'tl.fromTo("#w{j}",{{opacity:.45,scale:{0.8 if cls_k else 0.94}}},{{opacity:1,scale:1,duration:{0.22 if cls_k else 0.12},ease:"{ "back.out(3)" if cls_k else "power2.out"}"}},{ow[j]["s"]:.3f});')
        cap_js.append(f'tl.to("#cg{gi}",{{opacity:0,duration:.1,ease:"power2.in"}},{ge2 - 0.1:.3f});')
        cap_js.append(f'tl.set("#cg{gi}",{{opacity:0,visibility:"hidden"}},{ge2:.3f});')
        srt.append((gs, ge2, " ".join(ow[j]["t"] for j in g)))

    # ---- assemble HTML
    hook_lines = "".join(f'<span class="ln">{ln.replace("class=\"g\"","class=\"hl\"")}</span>' for ln in kw_html(spec["hook_title"]))
    name = spec.get("speaker", "DR. KHAIRUDDIN AMAN RAZALI"); role = spec.get("role", "")
    fact_tags = "\n".join(fact_html(i, f) for i, f in enumerate(facts))
    tag_html = []
    for k, tp in enumerate(topics):
        te = tstarts[k + 1] if k + 1 < len(topics) else tend
        tag_html.append(f'<div id="tag{k}" class="clip tag" data-start="{tstarts[k]:.3f}" data-duration="{te - tstarts[k]:.3f}" data-track-index="3">'
                        f'<div class="pill" id="tag{k}p"><span class="dot"></span><span class="tx">{esc(tp["label"])}</span></div></div>')
    concl_html = ""
    if concl:
        msg = "".join(f'<span style="display:block">{ln}</span>' for ln in kw_html(concl["text"]))
        concl_html = (f'<div id="concl" class="clip" data-start="{concl["start"]:.3f}" data-duration="{concl["dur"]:.3f}" data-track-index="6">'
                      f'<div class="box" id="conclb"><div class="kicker">{esc(concl.get("kicker","MESEJ UTAMA"))}</div>'
                      f'<div class="msg">{msg}</div><div class="rule" id="conclr"></div></div></div>')
    endmsg = "".join(f'<span style="display:block">{ln}</span>' for ln in kw_html(spec.get("end_text", spec["topic"])))

    js = []
    js.append(f'tl.fromTo("#hookk",{{opacity:0,y:-16}},{{opacity:1,y:0,duration:.6,ease:"power3.out"}},0.05);')
    js.append(f'tl.fromTo("#hookr",{{scaleX:0}},{{scaleX:1,duration:.7,ease:"power3.out"}},0.15);')
    js.append(f'tl.from("#hook .ln",{{opacity:0,y:60,scale:1.25,duration:.55,stagger:.14,ease:"power4.out"}},0.12);')
    js.append(f'tl.to("#hookb",{{opacity:0,y:-30,duration:.35,ease:"power2.in"}},{hook_end - 0.35:.3f});')
    js.append(f'tl.fromTo("#flash",{{opacity:0}},{{opacity:.85,duration:.12,ease:"power2.out"}},{hook_end - 0.12:.3f});')
    js.append(f'tl.to("#flash",{{opacity:0,duration:.35,ease:"power2.in"}},{hook_end + 0.02:.3f});')
    # lower third
    js.append(f'tl.fromTo("#l3bar",{{scaleY:0,transformOrigin:"50% 0%"}},{{scaleY:1,duration:.35,ease:"power3.out"}},{l3s:.3f});')
    js.append(f'tl.fromTo("#l3pan",{{scaleX:0}},{{scaleX:1,duration:.55,ease:"power3.out"}},{l3s+0.15:.3f});')
    js.append(f'tl.from("#l3name",{{opacity:0,x:-40,duration:.5,ease:"power3.out"}},{l3s+0.35:.3f});')
    js.append(f'tl.from("#l3role",{{opacity:0,x:-40,duration:.5,ease:"power3.out"}},{l3s+0.5:.3f});')
    js.append(f'tl.fromTo("#l3line",{{scaleX:0}},{{scaleX:1,duration:.8,ease:"power2.inOut"}},{l3s+0.55:.3f});')
    js.append(f'tl.from("#l3topic",{{opacity:0,y:20,duration:.45,ease:"back.out(1.8)"}},{l3s+0.9:.3f});')
    js.append(f'tl.to("#l3w",{{opacity:0,x:-60,duration:.4,ease:"power2.in"}},{l3s+l3d-0.45:.3f});')
    for k in range(len(topics)):
        js.append(f'tl.from("#tag{k}p",{{opacity:0,x:-50,duration:.45,ease:"power3.out"}},{tstarts[k]:.3f});')
    for i, f in enumerate(facts): js.append(fact_js(i, f))
    if concl:
        cs = concl["start"]
        js.append(f'tl.from("#conclb .kicker",{{opacity:0,y:-16,duration:.5,ease:"power3.out"}},{cs:.3f});')
        js.append(f'tl.from("#conclb .msg span",{{opacity:0,y:50,scale:1.15,duration:.55,stagger:.16,ease:"power4.out"}},{cs+0.1:.3f});')
        js.append(f'tl.fromTo("#conclr",{{scaleX:0}},{{scaleX:1,duration:.8,ease:"power3.out"}},{cs+0.3:.3f});')
    es = D - end_dur
    js.append(f'tl.fromTo("#endbg",{{opacity:0}},{{opacity:1,duration:.6,ease:"power2.out"}},{es:.3f});')
    js.append(f'tl.from("#endb > *",{{opacity:0,y:30,duration:.5,stagger:.12,ease:"power3.out"}},{es+0.2:.3f});')

    doc = f"""<!doctype html>
<html lang="ms">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/vendor/gsap.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<div id="root" data-composition-id="{cid}" data-start="0" data-duration="{D:.3f}" data-width="1080" data-height="1920" data-fps="30">
  <div id="cam"><video id="v" class="clip" data-start="0" data-duration="{D:.3f}" data-track-index="0" src="assets/clips/{cid}.mp4" muted playsinline></video></div>
  <audio id="mix" class="clip" data-start="0" data-duration="{D:.3f}" data-track-index="1" src="assets/clips/{cid}.m4a"></audio>
  <div id="vig" class="layer"></div>
  <div id="scrimTop" class="layer"></div>
  <div id="scrimBot" class="layer"></div>
  <div id="hook" class="clip" data-start="0" data-duration="{hook_end + 0.05:.3f}" data-track-index="2">
    <div class="box" id="hookb"><div class="kicker" id="hookk">{esc(spec.get("hook_kicker", "PETIKAN UCAPAN"))}</div><div class="rule" id="hookr"></div><h1>{hook_lines}</h1></div>
  </div>
  <div id="flash" class="clip" data-start="{max(0, hook_end - 0.15):.3f}" data-duration="0.6" data-track-index="7"></div>
  <div id="l3" class="clip" data-start="{l3s:.3f}" data-duration="{l3d:.3f}" data-track-index="2">
    <div class="wrap" id="l3w"><div class="bar" id="l3bar"></div><div class="panel" id="l3pan"></div>
      <div class="name{" short" if len(name) <= 14 else ""}" id="l3name">{esc(name)}</div><div class="role" id="l3role">{esc(role)}</div>
      <div class="line" id="l3line"></div><div class="topic" id="l3topic">{esc(spec["topic"])}</div></div>
  </div>
  {"".join(tag_html)}
  {fact_tags}
  {concl_html}
  <div id="caps" class="clip" data-start="0" data-duration="{D - end_dur:.3f}" data-track-index="8" data-track-kind="captions">
    {"".join(cap_html)}
  </div>
  <div id="end" class="clip" data-start="{es:.3f}" data-duration="{end_dur:.3f}" data-track-index="9">
    <div class="bg" id="endbg"></div>
    <div class="box" id="endb"><div class="kicker">{esc(spec.get("end_kicker","PETIKAN UCAPAN"))}</div><div class="nm">{esc(name)}</div>
      <div class="rl">{esc(role)}</div><div class="rule"></div><div class="ms">{endmsg}</div></div>
  </div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(cam_js)}
{chr(10).join(js)}
{chr(10).join(cap_js)}
window.__timelines["{cid}"] = tl;
</script>
</body>
</html>
"""
    ep = os.path.join(ROOT, "episodes", cid); os.makedirs(os.path.join(ep, "assets/vendor"), exist_ok=True)
    open(os.path.join(ep, "index.html"), "w").write(doc)
    import shutil
    shutil.copy(os.path.join(ROOT, "assets/vendor/gsap.min.js"), os.path.join(ep, "assets/vendor/gsap.min.js"))
    json.dump({"id": cid.lower().replace("_", "-"), "name": cid}, open(os.path.join(ep, "meta.json"), "w"))
    shutil.copy(os.path.join(ROOT, "hyperframes.json"), os.path.join(ep, "hyperframes.json"))

    # ---- deliverables
    dd = os.path.join(ROOT, "deliverables", cid); os.makedirs(dd, exist_ok=True)
    with open(os.path.join(dd, f"{cid}.srt"), "w") as fh:
        for k, (a, b, tx) in enumerate(srt, 1):
            fh.write(f"{k}\n{srt_time(a)} --> {srt_time(b)}\n{tx}\n\n")
    with open(os.path.join(dd, "EDL.txt"), "w") as fh:
        fh.write(f"TITLE: {cid}\nFCM: NON-DROP FRAME\nSOURCE: {spec['source_name']}\n\n")
        def tc(t):
            f = int(round(t * FPS)); return f"{f//(3600*FPS):02}:{f//(60*FPS)%60:02}:{f//FPS%60:02}:{f%FPS:02}"
        for k, p in enumerate(edl, 1):
            fh.write(f"{k:03}  AX  AA/V  C  {tc(p['a'])} {tc(p['b'])} {tc(p['o'])} {tc(p['o']+p['b']-p['a'])}  * {p['kind'].upper()}\n")
    json.dump({"id": cid, "duration": D, "edl": edl, "words": ow, "facts": facts, "conclusion": concl,
               "topics": [dict(t, start=s) for t, s in zip(topics, tstarts)], "cues": cues, "hook_end": hook_end},
              open(os.path.join(dd, "build.json"), "w"), ensure_ascii=False, indent=1)
    with open(os.path.join(dd, "transkrip.txt"), "w") as fh:
        for a, b, tx in srt: fh.write(f"[{a:6.2f}] {tx}\n")
    print(f"{cid}: {D:.2f}s, {len(edl)} pieces, {len(groups)} caption groups, {len(facts)} facts")

if __name__ == "__main__":
    build(sys.argv[1], "--html-only" in sys.argv)
