#!/usr/bin/env python3
"""Cut edit.json clips out of the source speech video and clean the voice.

Writes assets/footage/clip-<id>.mp4 (H.264 CRF 15, keyframe every 0.5 s for seek-safe preview,
voice: highpass 85 Hz + FFT denoise + gentle compression + loudnorm -15 LUFS, 30/60 ms edge fades)
and data/vo/<id>.wav (16 kHz mono, for alignment).

Usage: python3 prep.py [project_dir]
"""
import json, os, subprocess, sys

P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
E = json.load(open(os.path.join(P, "edit.json")))
os.makedirs(os.path.join(P, "assets/footage"), exist_ok=True)
os.makedirs(os.path.join(P, "data/vo"), exist_ok=True)
for c in E["clips"]:
    d = round(c["out"] - c["in"], 3)
    af = ("highpass=f=85,afftdn=nf=-28:nr=10,acompressor=threshold=-22dB:ratio=2.2:attack=8:release=150:makeup=2,"
          f"loudnorm=I=-15:TP=-1.5:LRA=8,afade=t=in:d=0.03,afade=t=out:st={round(d - 0.06, 3)}:d=0.06")
    dst = os.path.join(P, f"assets/footage/clip-{c['id']}.mp4")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(c["in"]), "-i", E["source"], "-t", str(d),
                    "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-g", "15", "-pix_fmt", "yuv420p",
                    "-af", af, "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", dst], check=True)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", dst, "-vn", "-ac", "1", "-ar", "16000",
                    os.path.join(P, f"data/vo/{c['id']}.wav")], check=True)
    print(f"clip-{c['id']}  {c['in']:.2f}-{c['out']:.2f}  {d}s")
