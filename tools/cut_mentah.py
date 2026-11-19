#!/usr/bin/env python3
"""Raw per-issue cuts (no graphics) from the cleaned 9:16 footage of clip C.
Same cut lists as tools/build_captions_isu.py. Usage: python3 tools/cut_mentah.py"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "ep3-seri-iskandar/assets/footage/dewan-seri-iskandar.mp4")
OUT = os.path.join(ROOT, "renders/seri-iskandar-ikut-isu/mentah")
SPECS = {
    "isu1-pasar": [(67.45, 70.85), (46.95, 57.82), (61.40, 67.10), (71.95, 87.20), (89.15, 101.75), (103.10, 114.50), (115.30, 120.45), (159.72, 169.72)],
    "isu2-jalan": [(213.10, 219.10), (187.90, 213.00), (221.42, 253.45), (254.98, 262.82)],
    "isu3-dataran": [(264.68, 303.56)],
    "isu4-rumah": [(341.50, 345.65), (304.72, 306.80), (308.65, 356.30)],
}
for isu, cuts in SPECS.items():
    parts, labels = [], []
    for i, (a, b) in enumerate(cuts):
        d = b - a
        parts.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];"
                     f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={d - 0.05:.3f}:d=0.05[a{i}];")
        labels.append(f"[v{i}][a{i}]")
    fc = "".join(parts) + "".join(labels) + f"concat=n={len(cuts)}:v=1:a=1[v][a]"
    out = os.path.join(OUT, f"{isu}-mentah-1080x1920.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", out], check=True)
    print(out)
