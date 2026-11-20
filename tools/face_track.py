#!/usr/bin/env python3
"""Median face position for a clip window, in 1080x1920 space.

usage: face_track.py <lecture.mp4> <start_s> <end_s> [step_s=2]
prints  [x, y]  for the clip spec "face" field (and the spread, to judge how much the speaker moves).
"""
import sys, subprocess, statistics
import numpy as np, cv2

src, a, b = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
step = float(sys.argv[4]) if len(sys.argv) > 4 else 2.0
W, H = 432, 768
casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
prof = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", src,
                      "-vf", f"fps=1/{step},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                     capture_output=True, check=True).stdout
n = len(raw) // (W * H)
xs, ys = [], []
for i in range(n):
    g = np.frombuffer(raw[i * W * H:(i + 1) * W * H], np.uint8).reshape(H, W)
    found = []
    for c in (casc, prof):
        f = c.detectMultiScale(g, 1.1, 5, minSize=(28, 28))
        if len(f):
            found = f; break
    if len(found):
        x, y, w, h = max(found, key=lambda r: r[2] * r[3])
        xs.append((x + w / 2) * 2.5); ys.append((y + h * 0.45) * 2.5)
if not xs:
    print("no face found"); sys.exit(1)
mx, my = statistics.median(xs), statistics.median(ys)
print(f"[{round(mx)}, {round(my)}]  frames={n} detected={len(xs)} spread_x={round(np.percentile(xs,90)-np.percentile(xs,10))} spread_y={round(np.percentile(ys,90)-np.percentile(ys,10))}")
