#!/usr/bin/env python3
"""Build the caption sub-composition and SRT files from the reviewed transcript.

Source: assets/source/transcript.json (whisper large-v3, language ms), with the
corrections below applied after a second listening pass on the unclear slice.
Re-run after editing CORRECTIONS or KEYWORDS:  python3 scripts/build_captions.py
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
words = json.load(open(os.path.join(ROOT, "assets/source/transcript.json")))

# Corrections (source time). "Timbalani" + "Betul," was a mis-hearing of
# "Timbalan Yang di-Pertua," (confirmed by a second whisper pass on 23–31 s).
CORRECTIONS = {
    ("Timbalani", 24.94): [("Timbalan", 24.94, 25.30), ("Yang", 25.30, 25.59)],
    ("Betul,", 25.90): [("di-Pertua,", 25.90, 26.22)],
    ("telahpun", 12.30): [("telah", 12.30, 12.80), ("pun", 12.80, 13.44)],
    ("parit,", 6.66): [("Parit,", 6.66, 7.22)],
    ("bandar", 8.69): [("Bandar", 8.69, 9.09)],
    ("universiti,", 9.09): [("Universiti,", 9.09, 10.02)],
}

src = []
for w in words:
    key = (w["text"], round(w["start"], 2))
    if key in CORRECTIONS:
        for t, s, e in CORRECTIONS[key]:
            src.append({"text": t, "start": s, "end": e})
    else:
        src.append({"text": w["text"], "start": w["start"], "end": w["end"]})

KEYWORDS = {
    "disegerakan", "klinik", "kesihatan", "sekolah", "menengah", "kompleks", "sukan",
    "senyap", "seribu", "bahasa", "penting", "inklusif", "denyut", "nadi", "akar", "umbi",
    "rmk13", "manfaat", "besar", "kemajuan", "menyeluruh", "perak",
}

def norm(t):
    return re.sub(r"[^\w-]", "", t.lower())

# Output timeline: cold open plays source 15.08–21.48 at 0–6.4; full speech at 6.4.
HOOK_FROM, HOOK_TO, HOOK_OFFSET = 15.08, 21.48, -15.08
MAIN_OFFSET = 6.4

def shifted(ws, offset, lo=-1, hi=1e9):
    out = []
    for w in ws:
        if w["start"] >= lo and w["end"] <= hi:
            out.append({**w, "start": round(w["start"] + offset, 3), "end": round(w["end"] + offset, 3)})
    return out

hook = shifted(src, HOOK_OFFSET, HOOK_FROM, HOOK_TO)
main = shifted(src, MAIN_OFFSET)

def group(ws, max_words, max_chars=24):
    groups, cur = [], []
    for i, w in enumerate(ws):
        cur.append(w)
        text = " ".join(x["text"] for x in cur)
        nxt = ws[i + 1] if i + 1 < len(ws) else None
        brk = (
            nxt is None
            or w["text"][-1] in ",.!?"
            or (nxt["start"] - w["end"]) >= 0.25
            or len(cur) >= max_words
            or len(text + " " + nxt["text"]) > max_chars
        )
        if brk:
            groups.append(cur)
            cur = []
    return groups

# High energy (3 words) for the hook and the climax, conversational (4) elsewhere.
G = group(hook, 3)
G += group([w for w in main if w["start"] < 40.2], 4, 19)
G += group([w for w in main if w["start"] >= 40.2], 3, 19)

# Group windows: open just before the first word, close at the next group's open.
win = []
for i, g in enumerate(G):
    start = max(0.12, g[0]["start"] - 0.06)
    end = g[-1]["end"] + 0.25
    win.append([start, end])
for i in range(len(win) - 1):
    if win[i][1] > win[i + 1][0]:
        win[i][1] = win[i + 1][0]
# The cold open's last group must clear before the dip cut.
for i, g in enumerate(G):
    if g[-1]["end"] <= 6.4:
        win[i][1] = min(win[i][1], 6.32)

def size_for(text):
    n = len(text)
    return 70 if n <= 13 else 62 if n <= 16 else 54

parts, js_groups = [], []
for gi, (g, (gs, ge)) in enumerate(zip(G, win)):
    text = " ".join(w["text"] for w in g)
    spans = []
    js_words = []
    for wi, w in enumerate(g):
        wid = f"cw{gi}-{wi}"
        key = norm(w["text"]) in KEYWORDS
        spans.append(f'<span id="{wid}" class="cw">{html.escape(w["text"].upper())}</span>')
        js_words.append([wid, round(w["start"], 3), round(w["end"], 3), 1 if key else 0])
    parts.append(
        f'    <div id="cg{gi}" class="cg"><div class="cbox" style="font-size:{size_for(text)}px">'
        + " ".join(spans)
        + "</div></div>"
    )
    js_groups.append([f"cg{gi}", round(gs, 3), round(ge, 3), js_words])

total = 53.0
doc = f"""<template>
  <style>
    #root {{
      position: absolute;
      inset: 0;
      background: transparent;
    }}
    /* Caption band: bottom of the TikTok-safe area (above y=1330), under the speaker's chin. */
    .cg {{
      position: absolute;
      left: 0;
      top: 1150px;
      width: 1080px;
      height: 176px;
      display: flex;
      align-items: flex-end;
      justify-content: center;
      text-align: center;
      overflow: visible;
      opacity: 0;
      visibility: hidden;
    }}
    .cbox {{
      display: inline-block;
      max-width: 940px;
      padding: 8px 26px 12px;
      border-radius: 14px;
      background: rgba(8, 11, 19, 0.5);
      font-family: "Montserrat", sans-serif;
      font-weight: 800;
      line-height: 1.16;
      letter-spacing: 0.01em;
      color: #ffffff;
      -webkit-text-stroke: 3px #000;
      paint-order: stroke fill;
      text-shadow: 0 4px 14px rgba(0, 0, 0, 0.55);
    }}
    .cw {{
      display: inline-block;
    }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{chr(10).join(parts)}
  </div>
  <script>
    // Generated by scripts/build_captions.py from assets/source/transcript.json. Edit there, then re-run.
    const GROUPS = {json.dumps(js_groups)};
    const tl = gsap.timeline({{ paused: true }});
    const YEL = "#FFD447";
    for (const [gid, gs, ge, ws] of GROUPS) {{
      const g = "#" + gid;
      tl.set(g, {{ visibility: "visible" }}, gs);
      tl.fromTo(g, {{ opacity: 0 }}, {{ opacity: 1, duration: 0.12, ease: "power2.out" }}, gs);
      tl.fromTo(g + " .cbox", {{ scale: 0.88 }}, {{ scale: 1, duration: 0.22, ease: "back.out(1.7)" }}, gs);
      for (const [wid, ws0, we, key] of ws) {{
        const w = "#" + wid;
        tl.set(w, {{ color: YEL }}, ws0);
        if (key) {{
          tl.fromTo(w, {{ scale: 1 }}, {{ scale: 1.14, duration: 0.1, ease: "power2.out" }}, ws0);
          tl.to(w, {{ scale: 1, duration: 0.2, ease: "power2.out" }}, ws0 + 0.1);
        }} else {{
          tl.set(w, {{ color: "#FFFFFF" }}, Math.min(we, ge - 0.02));
        }}
      }}
      tl.to(g, {{ opacity: 0, duration: 0.1, ease: "power2.in" }}, ge - 0.1);
      tl.set(g, {{ opacity: 0, visibility: "hidden" }}, ge);
    }}
    window.__timelines["captions"] = tl;
  </script>
</template>
"""
open(os.path.join(ROOT, "compositions/captions.html"), "w").write(doc)

def ts(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

os.makedirs(os.path.join(ROOT, "deliverables"), exist_ok=True)

# SRT synced to the edited video (output timeline).
with open(os.path.join(ROOT, "deliverables/subtitles-video.srt"), "w") as f:
    for i, (g, (gs, ge)) in enumerate(zip(G, win), 1):
        f.write(f"{i}\n{ts(gs)} --> {ts(ge)}\n{' '.join(w['text'] for w in g)}\n\n")

# SRT on the original footage's clock (source timeline): phrase cues, max two lines.
def phrases(ws, max_chars=64):
    out, cur = [], []
    for i, w in enumerate(ws):
        cur.append(w)
        nxt = ws[i + 1] if i + 1 < len(ws) else None
        text = " ".join(x["text"] for x in cur)
        if nxt is None or w["text"][-1] in ",.!?" and len(text) > 18 or len(text + " " + nxt["text"]) > max_chars:
            out.append(cur)
            cur = []
    return out

def two_lines(ws):
    text = " ".join(w["text"] for w in ws)
    if len(text) <= 36:
        return text
    best = min(range(1, len(ws)), key=lambda k: abs(len(" ".join(w["text"] for w in ws[:k])) - len(text) / 2))
    return " ".join(w["text"] for w in ws[:best]) + "\n" + " ".join(w["text"] for w in ws[best:])

src_groups = phrases(src)
with open(os.path.join(ROOT, "deliverables/subtitles-source.srt"), "w") as f:
    for i, g in enumerate(src_groups, 1):
        f.write(f"{i}\n{ts(g[0]['start'])} --> {ts(g[-1]['end'])}\n{two_lines(g)}\n\n")

print(f"{len(G)} caption groups; {len(src_groups)} source cues")
