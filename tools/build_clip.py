#!/usr/bin/env python3
"""Build one 9:16 HyperFrames project for a lecture clip from a JSON spec.

usage: python3 tools/build_clip.py clips/KULIAH_01.json --source <lecture.mp4> [--no-media]

Spec fields (times in the SOURCE lecture are seconds; everything else is clip-local):
  id, slug, category, title_lines[[{t,gold}]], header, speaker, series,
  start, end, points[{label,text,at,dur}], arabic[{ar,ms,ref,at,dur}],
  keywords[], words[{text,start,end}] (clip-local, from the medium transcript)
"""
import json, os, shutil, subprocess, sys, html, re, argparse

COVER_END = 2.6   # cover (poster) shows 0 -> 2.6 s; frame 0 is the thumbnail
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920
# speaker face in the source frame (432x768) scaled to 1080x1920
FACE_X, FACE_Y = 595, 1088


def esc(s):
    return html.escape(s, quote=True)


def cam(s, face_target_y):
    tx = 540 - FACE_X * s
    ty = face_target_y - FACE_Y * s
    tx = min(0, max(W - W * s, tx))
    ty = min(0, max(H - H * s, ty))
    return round(tx, 1), round(ty, 1)


def group_words(words, max_words=6, max_chars=36):
    groups, cur = [], []
    for i, w in enumerate(words):
        if cur:
            gap = w["start"] - cur[-1]["end"]
            chars = sum(len(x["text"]) + 1 for x in cur) + len(w["text"])
            prev = cur[-1]["text"]
            if (len(cur) >= max_words or chars > max_chars or gap >= 0.35
                    or re.search(r"[.?!]$", prev)):
                groups.append(cur); cur = []
        cur.append(w)
    if cur:
        groups.append(cur)
    merged = []
    for g in groups:   # no orphan single words
        if merged and len(g) == 1 and sum(len(x["text"]) + 1 for x in merged[-1] + g) <= 44 \
                and g[0]["start"] - merged[-1][-1]["end"] < 0.35 and not re.search(r"[.?!]$", merged[-1][-1]["text"]):
            merged[-1] = merged[-1] + g
        else:
            merged.append(g)
    return merged


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def norm(w):
    return re.sub(r"[^\w]", "", w.lower())


FONT_FACES = """
    @font-face { font-family: "Montserrat"; font-weight: 800; src: url("assets/fonts/montserrat-800.woff2") format("woff2"); }
    @font-face { font-family: "Montserrat"; font-weight: 900; src: url("assets/fonts/montserrat-900.woff2") format("woff2"); }
    @font-face { font-family: "Montserrat"; font-weight: 600; src: url("assets/fonts/montserrat-600.woff2") format("woff2"); }
    @font-face { font-family: "Amiri"; font-weight: 700; src: url("assets/fonts/amiri-700.woff2") format("woff2"); }
"""

STAR = ('<svg viewBox="-50 -50 100 100" width="{s}" height="{s}"><g fill="none" stroke="#D5B36A" stroke-width="{sw}">'
        '<rect x="-30" y="-30" width="60" height="60"/><rect x="-30" y="-30" width="60" height="60" transform="rotate(45)"/>'
        '<circle r="15"/><circle r="44" stroke-opacity=".5"/></g></svg>')


def build(spec, source, media=True):
    global FACE_X, FACE_Y
    if "face" in spec:   # per-footage face position (x, y) in the 1080x1920-scaled source
        FACE_X, FACE_Y = spec["face"]
    cid = spec["id"]
    name = f"KULIAH_{cid}"
    out = os.path.join(ROOT, "videos", name)
    os.makedirs(os.path.join(out, "compositions"), exist_ok=True)
    os.makedirs(os.path.join(out, "assets", "fonts"), exist_ok=True)
    os.makedirs(os.path.join(out, "assets", "vendor"), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "assets/vendor/gsap.min.js"), os.path.join(out, "assets/vendor/gsap.min.js"))
    for f in os.listdir(os.path.join(ROOT, "assets/fonts")):
        shutil.copy(os.path.join(ROOT, "assets/fonts", f), os.path.join(out, "assets/fonts", f))
    shutil.copy(os.path.join(ROOT, "assets/music/pad.m4a"), os.path.join(out, "assets/music.m4a"))

    start, end = spec["start"], spec["end"]
    if "text" in spec:  # proof-read text aligned onto whisper word timings
        txt = os.path.join(out, "transcript.txt")
        open(txt, "w").write(spec["text"])
        res = subprocess.run([sys.executable, os.path.join(ROOT, "tools/align_words.py"),
                              os.path.join(ROOT, spec["whisper"]), str(spec["window"]), str(start), str(end), txt],
                             check=True, capture_output=True, text=True)
        spec["words"] = json.loads(res.stdout)
        json.dump(spec["words"], open(os.path.join(out, "words.json"), "w"), ensure_ascii=False, indent=0)
    words = [w for w in spec["words"] if w["start"] < end - start]
    last_word_end = max(w["end"] for w in words)
    speech_dur = round(min(end - start, last_word_end + 0.6), 2)
    D = round(min(120.0, max(min(speech_dur + 2.0, 120.0), speech_dur + 1.0)), 2)   # short outro, total kept <= 120 s

    if media:
        clip = os.path.join(out, "assets", "clip.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-i", source, "-t", str(speech_dur + 0.2),
                        "-an", "-vf", "scale=1080:1920:flags=lanczos,fps=30,format=yuv420p",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-g", "30", "-movflags", "+faststart", clip],
                       check=True)
        voice = os.path.join(out, "assets", "voice.m4a")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-i", source, "-t", str(speech_dur),
                        "-vn", "-af",
                        "highpass=f=80,afftdn=nr=12:nf=-30,acompressor=threshold=-20dB:ratio=3:attack=10:release=200,"
                        "loudnorm=I=-16:TP=-1.5:LRA=9,afade=t=in:d=0.08,afade=t=out:st=%.2f:d=0.4" % (speech_dur - 0.4),
                        "-ar", "48000", "-ac", "2", "-c:a", "aac", "-b:a", "192k", voice], check=True)

    # ---------- camera plan ----------
    # hook close-up, then medium while cards show, close-ups between cards
    shots = [(0.0, 1.22, 1010), (COVER_END, 1.50, 760)]
    card_windows = [(p["at"], p["at"] + p["dur"], 1.28, 860) for p in spec.get("points", [])] + \
                   [(a["at"], a["at"] + a["dur"], 1.16, 960) for a in spec.get("arabic", [])]
    card_windows.sort()
    t = 5.0
    for (a, b, cs_, cy_) in card_windows:
        if a > t + 4:
            shots.append((t, 1.30, 860))
            shots.append(((t + a) / 2, 1.48, 770))
        shots.append((max(a - 0.3, t), cs_, cy_))
        t = b + 0.2
    if speech_dur > t + 4:
        shots.append((t, 1.42, 790))
    cam_js = []
    for i, (st, s, fy) in enumerate(shots):
        en = shots[i + 1][0] if i + 1 < len(shots) else D
        tx, ty = cam(s, fy)
        s2 = s + min(0.06, 0.006 * (en - st))
        tx2, ty2 = cam(s2, fy - 10)
        cam_js.append(f'tl.set("#cam", {{x:{tx}, y:{ty}, scale:{s}}}, {st:.2f});')
        cam_js.append(f'tl.to("#cam", {{x:{tx2}, y:{ty2}, scale:{s2:.3f}, duration:{en - st:.2f}, ease:"none"}}, {st:.2f});')

    # ---------- index.html ----------
    index = f"""<!doctype html>
<html lang="ms">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #081726; }}
      #bg {{ position: absolute; inset: 0; background: #081726; }}
      #cam {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; transform-origin: 0 0; }}
      #v {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="{W}" data-height="{H}">
      <div id="bg"></div>
      <div id="cam">
        <video id="v" class="clip" src="assets/clip.mp4" data-start="0" data-duration="{speech_dur}" data-track-index="0" muted playsinline style="z-index:1"></video>
      </div>
      <audio id="voice" class="clip" src="assets/voice.m4a" data-start="0" data-duration="{speech_dur}" data-track-index="1" data-volume="1"></audio>
      <audio id="music" class="clip" src="assets/music.m4a" data-start="0" data-duration="{D}" data-track-index="2" data-volume="{spec.get('music_volume', 0.1)}" data-fade-in="2" data-fade-out="2.5"></audio>
      <div id="overlay" class="clip" data-composition-id="overlay" data-composition-src="compositions/overlay.html" data-start="0" data-duration="{D}" data-track-index="3" data-track-kind="graphics" data-width="{W}" data-height="{H}" style="z-index:5"></div>
      <div id="captions" class="clip" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{speech_dur}" data-track-index="4" data-track-kind="captions" data-width="{W}" data-height="{H}" style="z-index:6"></div>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join('      ' + c for c in cam_js).strip()}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    open(os.path.join(out, "index.html"), "w").write(index)

    # ---------- overlay.html ----------
    title_html = "<br/>".join(
        " ".join(f'<span class="{"g" if seg.get("gold") else "w"}">{esc(seg["t"])}</span>' for seg in line)
        for line in spec["title_lines"])
    def cover_line(line):
        txt = " ".join(seg["t"] for seg in line)
        # approx. Montserrat Black cap advance widths (em)
        em = sum(0.98 if c in "MW" else 0.36 if c in "I!:.,'" else 0.30 if c == " " else 0.72 if c in "?&" else 0.80 for c in txt)
        fs = int(min(136, 930 / max(em, 1)))
        segs = " ".join(f'<span class="{"g" if seg.get("gold") else "w"}">{esc(seg["t"])}</span>' for seg in line)
        return f'<div class="cv-line" style="font-size:{fs}px">{segs}</div>'
    cover_title = "".join(cover_line(l) for l in spec.get("cover_lines", spec["title_lines"]))
    cards, card_js = [], []
    for i, p in enumerate(spec.get("points", [])):
        cid_ = f"pt{i + 1}"
        cards.append(f"""
      <div id="{cid_}" class="clip card" data-start="{p['at']}" data-duration="{p['dur']}" data-track-index="{2 + i}">
        <div class="card-in">
          <div class="card-label">{esc(p.get('label', f'POIN {i + 1}'))}</div>
          <div class="card-text">{esc(p['text'])}</div>
        </div>
      </div>""")
        a, d = p["at"], p["dur"]
        card_js.append(f'tl.fromTo("#{cid_} .card-in", {{opacity:0, y:40, scale:.96}}, {{opacity:1, y:0, scale:1, duration:.5, ease:"power3.out"}}, {a + 0.02:.2f});')
        card_js.append(f'tl.fromTo("#{cid_} .card-label", {{opacity:0, x:-20}}, {{opacity:1, x:0, duration:.4, ease:"power2.out"}}, {a + 0.25:.2f});')
        card_js.append(f'tl.to("#{cid_} .card-in", {{opacity:0, y:-16, duration:.35, ease:"power2.in"}}, {a + d - 0.4:.2f});')
    for i, ar in enumerate(spec.get("arabic", [])):
        aid = f"ar{i + 1}"
        cards.append(f"""
      <div id="{aid}" class="clip card" data-start="{ar['at']}" data-duration="{ar['dur']}" data-track-index="{6 + i}">
        <div class="card-in ar-card">
          <div class="ar-text" dir="rtl" lang="ar" style="font-size:{62 if len(ar['ar']) < 45 else (50 if len(ar['ar']) < 75 else 42)}px">{esc(ar['ar'])}</div>
          <div class="ar-ms" style="font-size:{34 if len(ar['ms']) < 80 else 28}px">{esc(ar['ms'])}</div>
          {f'<div class="ar-ref">{esc(ar["ref"])}</div>' if ar.get('ref') else ''}
        </div>
      </div>""")
        a, d = ar["at"], ar["dur"]
        card_js.append(f'tl.fromTo("#{aid} .card-in", {{opacity:0, y:40, scale:.96}}, {{opacity:1, y:0, scale:1, duration:.55, ease:"power3.out"}}, {a + 0.02:.2f});')
        card_js.append(f'tl.to("#{aid} .card-in", {{opacity:0, y:-16, duration:.35, ease:"power2.in"}}, {a + d - 0.4:.2f});')

    lt_at, lt_dur = spec.get("lower_third_at", 5.6), 5.5
    overlay = f"""<template>
  <style>
    {FONT_FACES}
    #root {{ position: absolute; inset: 0; font-family: "Montserrat", "Amiri", sans-serif; color: #fff; }}
    #ov-topscrim {{ position: absolute; left: 0; top: 0; width: 1080px; height: 760px;
      background: linear-gradient(180deg, rgba(8,23,38,.92) 0%, rgba(8,23,38,.78) 38%, rgba(7,59,53,.25) 75%, rgba(8,23,38,0) 100%); }}
    #ov-botscrim {{ position: absolute; left: 0; top: 1080px; width: 1080px; height: 840px;
      background: linear-gradient(180deg, rgba(8,23,38,0) 0%, rgba(8,23,38,.55) 25%, rgba(8,23,38,.9) 60%, #081726 100%); }}
    #ov-pattern {{ position: absolute; left: 0; top: 1500px; width: 1080px; height: 420px; opacity: .14;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'%3E%3Cg fill='none' stroke='%23D5B36A' stroke-width='1.4'%3E%3Crect x='30' y='30' width='60' height='60'/%3E%3Crect x='30' y='30' width='60' height='60' transform='rotate(45 60 60)'/%3E%3Ccircle cx='60' cy='60' r='14'/%3E%3C/g%3E%3C/svg%3E");
      -webkit-mask-image: linear-gradient(180deg, transparent, #000 60%); mask-image: linear-gradient(180deg, transparent, #000 60%); }}
    .star {{ position: absolute; opacity: .55; }}
    #ov-star1 {{ right: 52px; top: 188px; }}
    #ov-star2 {{ left: 470px; top: 1640px; opacity: .5; }}
    #ov-light {{ position: absolute; left: -200px; top: 120px; width: 900px; height: 900px; border-radius: 50%;
      background: radial-gradient(circle, rgba(213,179,106,.20), rgba(213,179,106,0) 65%); }}
    /* cover */
    #cover {{ position: absolute; inset: 0; }}
    #cv-scrim {{ position: absolute; inset: 0;
      background: linear-gradient(180deg, rgba(8,23,38,.97) 0%, rgba(7,59,53,.93) 34%, rgba(7,59,53,.55) 52%, rgba(8,23,38,.15) 66%, rgba(8,23,38,.55) 82%, rgba(8,23,38,.95) 100%); }}
    #cv-frame {{ position: absolute; left: 34px; top: 150px; width: 1012px; height: 1640px; border: 3px solid #D5B36A; border-radius: 26px; }}
    #cv-frame2 {{ position: absolute; left: 48px; top: 164px; width: 984px; height: 1612px; border: 1px solid rgba(213,179,106,.5); border-radius: 20px; }}
    .cv-corner {{ position: absolute; }}
    #cv-c1 {{ left: 6px; top: 122px; }} #cv-c2 {{ right: 6px; top: 122px; }}
    #cv-c3 {{ left: 6px; top: 1702px; }} #cv-c4 {{ right: 6px; top: 1702px; }}
    #cv-top {{ position: absolute; left: 0; top: 220px; width: 1080px; text-align: center; }}
    #cv-kitab {{ color: #D5B36A; font-weight: 800; font-size: 30px; letter-spacing: .26em; }}
    #cv-chip {{ display: inline-block; margin-top: 22px; padding: 12px 30px; border-radius: 40px; background: #D5B36A; color: #081726;
      font-weight: 900; font-size: 30px; letter-spacing: .14em; }}
    #cv-title {{ position: absolute; left: 60px; top: 380px; width: 960px; text-align: center; }}
    .cv-line {{ font-weight: 900; line-height: 1.04; letter-spacing: -.01em; color: #fff;
      text-shadow: 0 6px 0 rgba(0,0,0,.35), 0 12px 40px rgba(0,0,0,.6); }}
    .cv-line .g {{ color: #FFE16B; }}
    #cv-rule {{ margin: 30px auto 0; width: 300px; height: 8px; background: #D5B36A; border-radius: 4px; }}
    #cv-bottom {{ position: absolute; left: 0; top: 1560px; width: 1080px; text-align: center; }}
    #cv-series {{ color: #fff; font-weight: 800; font-size: 34px; letter-spacing: .22em; }}
    #cv-sub {{ margin-top: 12px; color: #D5B36A; font-weight: 600; font-size: 26px; letter-spacing: .08em; }}
    /* hook */
    #hook {{ position: absolute; left: 60px; top: 196px; width: 960px; }}
    .chip {{ display: inline-block; padding: 10px 22px; border: 2px solid #D5B36A; border-radius: 40px; color: #D5B36A;
      font-weight: 800; font-size: 28px; letter-spacing: .14em; background: rgba(7,59,53,.55); }}
    #hook-title {{ margin-top: 26px; font-weight: 900; font-size: 74px; line-height: 1.08; letter-spacing: -.01em;
      text-shadow: 0 6px 24px rgba(0,0,0,.55); }}
    #hook-title .g {{ color: #FFE16B; }}
    #hook-rule {{ margin-top: 24px; width: 260px; height: 6px; background: #D5B36A; border-radius: 3px; transform-origin: 0 50%; }}
    /* compact header */
    #header {{ position: absolute; left: 60px; top: 192px; width: 820px; }}
    #header .chip {{ font-size: 22px; padding: 7px 16px; }}
    #header-title {{ margin-top: 14px; font-weight: 900; font-size: 44px; line-height: 1.12; text-shadow: 0 4px 16px rgba(0,0,0,.6); }}
    #header-title .g {{ color: #FFE16B; }}
    /* cards */
    .card {{ position: absolute; left: 60px; top: 372px; width: 960px; }}
    .card-in {{ background: rgba(8,23,38,.84); border: 1.5px solid rgba(213,179,106,.55); border-left: 8px solid #D5B36A;
      border-radius: 22px; padding: 26px 34px 30px; box-shadow: 0 18px 50px rgba(0,0,0,.45); }}
    .card-label {{ color: #D5B36A; font-weight: 800; font-size: 28px; letter-spacing: .16em; }}
    .card-text {{ margin-top: 10px; font-weight: 800; font-size: 44px; line-height: 1.18; }}
    .ar-card {{ text-align: center; }}
    .ar-text {{ font-family: "Amiri", serif; font-weight: 700; font-size: 62px; line-height: 1.5; color: #FFE16B; }}
    .ar-ms {{ margin-top: 8px; font-weight: 600; font-size: 34px; line-height: 1.3; }}
    .ar-ref {{ margin-top: 10px; font-weight: 800; font-size: 26px; color: #D5B36A; letter-spacing: .08em; }}
    /* lower third */
    #lt {{ position: absolute; left: 60px; top: 1004px; width: 900px; }}
    #lt-in {{ display: flex; align-items: stretch; }}
    #lt-bar {{ width: 8px; background: #D5B36A; border-radius: 4px; transform-origin: 50% 0; }}
    #lt-box {{ margin-left: 16px; padding: 10px 22px 12px; background: rgba(8,23,38,.86); border-radius: 10px; }}
    #lt-name {{ font-weight: 900; font-size: 36px; }}
    #lt-role {{ font-weight: 600; font-size: 24px; color: #D5B36A; letter-spacing: .06em; margin-top: 2px; }}
    /* outro */
    #outro {{ position: absolute; inset: 0; background: #081726; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
    #outro-series {{ margin-top: 34px; color: #D5B36A; font-weight: 800; font-size: 34px; letter-spacing: .2em; }}
    #outro-title {{ margin-top: 18px; width: 900px; text-align: center; font-weight: 900; font-size: 52px; line-height: 1.12; }}
    #outro-title .g {{ color: #FFE16B; }}
  </style>
  <div id="root" data-composition-id="overlay" data-width="{W}" data-height="{H}">
    <div id="ov-light"></div>
    <div id="ov-topscrim"></div>
    <div id="ov-botscrim"></div>
    <div id="ov-pattern"></div>
    <div id="ov-star1" class="star">{STAR.format(s=110, sw=2)}</div>
    <div id="ov-star2" class="star">{STAR.format(s=140, sw=1.6)}</div>

    <div id="cover" class="clip" data-start="0" data-duration="{COVER_END + 0.4}" data-track-index="0">
      <div id="cover-in" style="position:absolute;inset:0">
        <div id="cv-scrim"></div>
        <div id="cv-frame"></div><div id="cv-frame2"></div>
        <div id="cv-c1" class="cv-corner">{STAR.format(s=56, sw=4)}</div><div id="cv-c2" class="cv-corner">{STAR.format(s=56, sw=4)}</div>
        <div id="cv-c3" class="cv-corner">{STAR.format(s=56, sw=4)}</div><div id="cv-c4" class="cv-corner">{STAR.format(s=56, sw=4)}</div>
        <div id="cv-top"><div id="cv-kitab">{esc(spec.get('cover_kicker', 'KULIAH KITAB BAHRUL MAZI'))}</div><div id="cv-chip">{esc(spec['category'])}</div></div>
        <div id="cv-title">{cover_title}<div id="cv-rule"></div></div>
        <div id="cv-bottom"><div id="cv-series">{esc(spec['series'])}</div><div id="cv-sub">{esc(spec.get('cover_sub', 'Syarah Mukhtasar Sahih at-Tirmizi'))}</div></div>
      </div>
    </div>

    <div id="header" class="clip" data-start="{COVER_END - 0.1}" data-duration="{round(speech_dur - COVER_END + 0.1, 2)}" data-track-index="1">
      <div id="header-in">
        <div class="chip">{esc(spec['category'])}</div>
        <div id="header-title">{spec.get('header_html') or title_html}</div>
      </div>
    </div>
    {''.join(cards)}

    <div id="lt" class="clip" data-start="{lt_at}" data-duration="{lt_dur}" data-track-index="9">
      <div id="lt-in">
        <div id="lt-bar"></div>
        <div id="lt-box">
          <div id="lt-name">{esc(spec['speaker'])}</div>
          <div id="lt-role">{esc(spec['speaker_role'])}</div>
        </div>
      </div>
    </div>

    <div id="outro" class="clip" data-start="{speech_dur - 0.2}" data-duration="{round(D - speech_dur + 0.2, 2)}" data-track-index="10">
      <div id="outro-in" style="display:flex;flex-direction:column;align-items:center">
        <div id="outro-star">{STAR.format(s=150, sw=2.4)}</div>
        <div id="outro-series">{esc(spec['series'])}</div>
        <div id="outro-title">{title_html}</div>
      </div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    // ambient accents
    tl.fromTo("#ov-star1 svg", {{rotation: 0}}, {{rotation: 90, duration: {D}, ease: "none"}}, 0);
    tl.fromTo("#ov-star2 svg", {{rotation: 0}}, {{rotation: -60, duration: {D}, ease: "none"}}, 0);
    tl.fromTo("#ov-light", {{x: 0, opacity: .6}}, {{x: 260, opacity: 1, duration: {D}, ease: "sine.inOut"}}, 0);
    // hook
    // cover: complete at frame 0 (thumbnail), slow push, then lifts away
    tl.fromTo("#cv-title", {{scale: 1}}, {{scale: 1.04, duration: {COVER_END}, ease: "none"}}, 0);
    tl.fromTo("#cv-rule", {{scaleX: 1}}, {{scaleX: 1.5, duration: {COVER_END}, ease: "none"}}, 0);
    tl.fromTo(".cv-corner svg", {{rotation: 0}}, {{rotation: 45, duration: {COVER_END}, ease: "none"}}, 0);
    tl.to("#cv-title", {{y: -60, opacity: 0, duration: .4, ease: "power2.in"}}, {COVER_END - 0.3});
    tl.to("#cover-in", {{opacity: 0, duration: .45, ease: "power2.inOut"}}, {COVER_END - 0.15});
    tl.fromTo("#header-in", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: .45, ease: "power2.out"}}, {COVER_END + 0.3});
    {chr(10).join('    ' + c for c in card_js).strip()}
    // lower third
    tl.fromTo("#lt-bar", {{scaleY: 0}}, {{scaleY: 1, duration: .35, ease: "power2.out"}}, {lt_at + 0.02});
    tl.fromTo("#lt-box", {{opacity: 0, x: -30}}, {{opacity: 1, x: 0, duration: .45, ease: "power3.out"}}, {lt_at + 0.15});
    tl.to("#lt-in", {{opacity: 0, x: -20, duration: .35, ease: "power2.in"}}, {lt_at + lt_dur - 0.4});
    // outro
    tl.fromTo("#outro", {{opacity: 0}}, {{opacity: 1, duration: .6, ease: "power2.inOut"}}, {speech_dur - 0.2});
    tl.fromTo("#outro-star svg", {{scale: .6, rotation: -45}}, {{scale: 1, rotation: 0, duration: 1.2, ease: "power3.out"}}, {speech_dur});
    tl.fromTo("#outro-series", {{opacity: 0, y: 16}}, {{opacity: 1, y: 0, duration: .5, ease: "power2.out"}}, {speech_dur + 0.25});
    tl.fromTo("#outro-title", {{opacity: 0, y: 16}}, {{opacity: 1, y: 0, duration: .5, ease: "power2.out"}}, {speech_dur + 0.4});
    window.__timelines["overlay"] = tl;
  </script>
</template>
"""
    open(os.path.join(out, "compositions", "overlay.html"), "w").write(overlay)

    # ---------- captions ----------
    kw = set(norm(k) for k in spec.get("keywords", []))
    groups = group_words(words)
    gh, gj, srt = [], [], []
    for gi, g in enumerate(groups):
        gs = max(0.05, g[0]["start"] - 0.06)
        nxt = groups[gi + 1][0]["start"] - 0.02 if gi + 1 < len(groups) else speech_dur - 0.1
        ge = min(max(g[-1]["end"] + 0.25, g[-1]["end"]), nxt, speech_dur - 0.1)
        spans = []
        for wi, w in enumerate(g):
            k = " kw" if norm(w["text"]) in kw else ""
            spans.append(f'<span class="w{k}" id="c{gi}w{wi}">{esc(w["text"])}</span>')
        gh.append(f'      <div class="grp" id="c{gi}"><div class="line">{" ".join(spans)}</div></div>')
        gj.append(f'tl.fromTo("#c{gi}", {{opacity:0, y:18}}, {{opacity:1, y:0, duration:.14, ease:"power2.out"}}, {gs:.3f});')
        for wi, w in enumerate(g):
            ws = max(gs, w["start"])
            we = g[wi + 1]["start"] if wi + 1 < len(g) else ge
            pop = 1.2 if norm(w["text"]) in kw else 1.1
            gj.append(f'tl.set("#c{gi}w{wi}", {{color:"#FFE16B"}}, {ws:.3f});')
            gj.append(f'tl.fromTo("#c{gi}w{wi}", {{scale:1}}, {{scale:{pop}, duration:.09, ease:"power2.out", yoyo:true, repeat:1}}, {ws:.3f});')
            gj.append(f'tl.set("#c{gi}w{wi}", {{color:"#FFFFFF"}}, {max(ws + 0.05, we):.3f});')
        gj.append(f'tl.to("#c{gi}", {{opacity:0, duration:.1, ease:"power2.in"}}, {max(ge - 0.1, gs + 0.145):.3f});')
        ge = max(ge, gs + 0.25)
        gj.append(f'tl.set("#c{gi}", {{opacity:0, visibility:"hidden"}}, {ge:.3f});')
        srt.append(f"{gi + 1}\n{srt_time(g[0]['start'])} --> {srt_time(max(g[-1]['end'], g[0]['start'] + 0.3))}\n"
                   + " ".join(w["text"] for w in g) + "\n")
    captions = f"""<template>
  <style>
    {FONT_FACES}
    #root {{ position: absolute; inset: 0; }}
    .grp {{ position: absolute; left: 0; top: 1118px; width: 1080px; height: 200px; display: flex; align-items: flex-end;
      justify-content: center; opacity: 0; overflow: visible; }}
    .line {{ width: 920px; text-align: center; font-family: "Montserrat", sans-serif; font-weight: 800; font-size: 64px;
      line-height: 1.16; color: #fff; text-transform: none; }}
    .w {{ display: inline-block; -webkit-text-stroke: 12px #000; paint-order: stroke fill;
      text-shadow: 0 6px 18px rgba(0,0,0,.65); transform-origin: 50% 70%; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="{W}" data-height="{H}">
{chr(10).join(gh)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {chr(10).join('    ' + c for c in gj).strip()}
    window.__timelines["captions"] = tl;
  </script>
</template>
"""
    open(os.path.join(out, "compositions", "captions.html"), "w").write(captions)
    open(os.path.join(out, f"{name}.srt"), "w").write("\n".join(srt))
    json.dump({"id": name.lower(), "name": name}, open(os.path.join(out, "meta.json"), "w"), indent=2)
    shutil.copy(os.path.join(ROOT, "hyperframes.json"), os.path.join(out, "hyperframes.json"))
    print(name, "duration", D, "groups", len(groups))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--source", required=True)
    ap.add_argument("--no-media", action="store_true")
    a = ap.parse_args()
    build(json.load(open(a.spec)), a.source, media=not a.no_media)
