#!/usr/bin/env python3
"""Assemble the original MusicGen cues into assets/audio/score.m4a and write data/music.json
(ducking automation derived from the speech intervals in data/words.json).

Usage: python3 tools/music.py <cue1.wav> <cue2.wav> <cue3.wav> [<cue4.wav>]
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOTAL = 84.5
cues = sys.argv[1:]

# placement: (file index, output start, source offset, length)
plan = [(0, 0.0, 0.0, 24.0), (1, 21.0, 0.0, 30.0), (2, 48.5, 0.0, 30.0)]
if len(cues) > 3:
    plan.append((3, 76.0, 0.0, TOTAL - 76.0 + 0.5))
else:
    plan.append((1, 76.0, 10.0, TOTAL - 76.0 + 0.5))

XF = 3.0
inputs, filters, labels = [], [], []
for k, (fi, st, off, ln) in enumerate(plan):
    inputs += ["-i", cues[fi]]
    fade_in = 0.05 if k == 0 else XF
    filters.append(
        f"[{k}:a]atrim={off}:{off+ln},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,"
        f"afade=t=in:d={fade_in},afade=t=out:st={ln-XF}:d={XF},adelay={int(st*1000)}|{int(st*1000)}[c{k}]")
    labels.append(f"[c{k}]")
filters.append(f"{''.join(labels)}amix=inputs={len(plan)}:normalize=0:duration=longest,"
               f"atrim=0:{TOTAL},highpass=f=35,loudnorm=I=-18:TP=-2:LRA=11[out]")
os.makedirs(os.path.join(ROOT, "assets/audio"), exist_ok=True)
dst = os.path.join(ROOT, "assets/audio/score.m4a")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filters),
                "-map", "[out]", "-c:a", "aac", "-b:a", "256k", dst], check=True)

# ducking lane
words = json.load(open(os.path.join(ROOT, "data/words.json")))
spans = []
for w in words:
    if spans and w["start"] - spans[-1][1] < 0.6:
        spans[-1][1] = max(spans[-1][1], w["end"])
    else:
        spans.append([w["start"], w["end"]])


def level(t, speaking):
    if not speaking:
        return 0.9 if t > 80.6 else 0.8
    if 60.0 <= t < 70.45:
        return 0.34  # climax: the score rises under the voice
    return 0.25


pts = [{"t": 0, "v": 0.8}]
for a, b in spans:
    pts.append({"t": round(max(0, a - 0.15), 3), "v": level(a, False) if a > 0.2 else 0.8})
    pts.append({"t": round(a, 3), "v": level(a, True)})
    pts.append({"t": round(b, 3), "v": level(b - 0.01, True)})
    pts.append({"t": round(b + 0.3, 3), "v": level(b + 0.3, False)})
# keep strictly increasing times
clean = []
for p in sorted(pts, key=lambda p: p["t"]):
    if clean and p["t"] <= clean[-1]["t"]:
        clean[-1] = p
    else:
        clean.append(p)
json.dump({"src": "assets/audio/score.m4a", "automation": clean}, open(os.path.join(ROOT, "data/music.json"), "w"), indent=1)
print("score ->", dst, "|", len(clean), "automation points")
