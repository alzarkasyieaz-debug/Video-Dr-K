#!/usr/bin/env python3
"""Copy finished renders to output/<ID>_<TOPIK>.mp4 (report naming), re-encoding to CRF 23 if the bitrate is high."""
import glob, json, os, re, subprocess, sys, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools")); from report import slug
os.makedirs(os.path.join(ROOT, "output"), exist_ok=True)
for p in sorted(glob.glob(os.path.join(ROOT, "renders/VIDEO_*.mp4"))):
    if ".tmp" in p: continue
    cid = re.match(r"(VIDEO_\d+)", os.path.basename(p)).group(1)
    s = json.load(open(os.path.join(ROOT, "specs", cid + ".json")))
    out = os.path.join(ROOT, "output", f"{cid}_{slug(s['topic'])}.mp4")
    if os.path.exists(out) and os.path.getmtime(out) > os.path.getmtime(p): continue
    for old in glob.glob(os.path.join(ROOT, "output", cid + "_*.mp4")): os.remove(old)
    br = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=bit_rate", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)
    if br > 4.5e6:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-maxrate", "6M", "-bufsize", "12M",
                        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "copy", out], check=True)
    else:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-c", "copy", "-movflags", "+faststart", out], check=True)
    print("output", os.path.basename(out), f"{os.path.getsize(out)/1e6:.1f} MB")
