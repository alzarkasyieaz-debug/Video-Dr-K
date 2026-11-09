#!/usr/bin/env python3
"""deliverables/subtitles.srt from data/words.json (sentence cues, <= 8 words, max 2 lines of ~42 chars).
Usage: python3 srt.py [project_dir]"""
import json, os, sys

P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
words = json.load(open(os.path.join(P, "data/words.json")))


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
    end = c[-1]["end"] + 0.25
    if i < len(cues):
        end = min(end, cues[i][0]["start"] - 0.02)
    text = " ".join(w["text"] for w in c)
    if len(text) > 42:
        mid = len(text) // 2
        cut = min((k for k, ch in enumerate(text) if ch == " "), key=lambda k: abs(k - mid))
        text = text[:cut] + "\n" + text[cut + 1:]
    out.append(f"{i}\n{ts(c[0]['start'])} --> {ts(end)}\n{text}\n")
os.makedirs(os.path.join(P, "deliverables"), exist_ok=True)
open(os.path.join(P, "deliverables/subtitles.srt"), "w").write("\n".join(out))
print(len(cues), "cues -> deliverables/subtitles.srt")
