#!/usr/bin/env python3
"""Write deliverables/subtitles.srt from data/words.json (forced-aligned, output timeline)."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
words = json.load(open(os.path.join(ROOT, "data/words.json")))


def ts(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


cues, cur = [], []
for w in words:
    if cur:
        p = cur[-1]
        if p["text"][-1] in ".?!" or len(cur) >= 8 or w["clip"] != p["clip"] or (p["text"][-1] == "," and len(cur) >= 4):
            cues.append(cur)
            cur = []
    cur.append(w)
if cur:
    cues.append(cur)

out = []
for i, c in enumerate(cues, 1):
    start = c[0]["start"]
    end = c[-1]["end"] + 0.25
    if i < len(cues):
        end = min(end, cues[i][0]["start"] - 0.02)
    text = " ".join(w["text"] for w in c)
    if len(text) > 42:  # two lines max, split near the middle on a space
        mid = len(text) // 2
        cut = min((k for k, ch in enumerate(text) if ch == " "), key=lambda k: abs(k - mid))
        text = text[:cut] + "\n" + text[cut + 1:]
    out.append(f"{i}\n{ts(start)} --> {ts(end)}\n{text}\n")

os.makedirs(os.path.join(ROOT, "deliverables"), exist_ok=True)
open(os.path.join(ROOT, "deliverables/subtitles.srt"), "w").write("\n".join(out))
print(len(cues), "cues")
