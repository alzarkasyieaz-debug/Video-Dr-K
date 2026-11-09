#!/usr/bin/env python3
"""Score for the Ceramah Politik style.

1. (--generate) makes any missing edit.json music.cues[].file with local MusicGen-medium from the cue's
   prompt/seed (CPU: ~17 min per 30 s cue). Only when HeyGen's licensed catalog isn't available or the
   person asked for original music. MusicGen weights are CC-BY-NC 4.0.
2. Crossfades the cues at their `at` times (3 s), normalises to -18 LUFS -> assets/audio/score.m4a.
3. Writes data/music.json: a volume lane that ducks the bed under every spoken phrase
   (0.25 under speech, 0.34 under speech in the climax scene, 0.8 between phrases, 0.9 on the end card).

Usage: python3 music.py [project_dir] [--generate]
"""
import json, os, subprocess, sys

args = [a for a in sys.argv[1:] if not a.startswith("--")]
P = os.path.abspath(args[0] if args else ".")
E = json.load(open(os.path.join(P, "edit.json")))
M = E["music"]
words = json.load(open(os.path.join(P, "data/words.json")))
speech_end = round(sum(round(c["out"] - c["in"], 3) for c in E["clips"]), 3)
total = round(speech_end + E.get("end_card", 3.8), 3)

if "--generate" in sys.argv:
    for cue in M["cues"]:
        f = os.path.join(P, cue["file"])
        if os.path.exists(f):
            continue
        os.makedirs(os.path.dirname(f), exist_ok=True)
        code = f"""
import torch, soundfile as sf
from transformers import AutoProcessor, MusicgenForConditionalGeneration
torch.manual_seed({cue.get("seed", 1)}); torch.set_num_threads(os.cpu_count() or 4)
p = AutoProcessor.from_pretrained("facebook/musicgen-medium")
m = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-medium")
x = p(text=[{json.dumps(cue["prompt"])}], padding=True, return_tensors="pt")
a = m.generate(**x, max_new_tokens={int(cue.get("seconds", 30) * 50)}, do_sample=True, guidance_scale=3.5)
sf.write({json.dumps(f)}, a[0].cpu().numpy().T, m.config.audio_encoder.sampling_rate)
"""
        print("generating", cue["file"], flush=True)
        subprocess.run([sys.executable, "-c", "import os\n" + code], check=True,
                       env={**os.environ, "HF_HUB_DISABLE_XET": "1"})

XF = 3.0
inputs, filters, labels = [], [], []
for k, cue in enumerate(M["cues"]):
    st, ln, off = cue["at"], cue["length"], cue.get("offset", 0.0)
    inputs += ["-i", os.path.join(P, cue["file"])]
    fin = 0.05 if k == 0 else XF
    filters.append(f"[{k}:a]atrim={off}:{off + ln},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,"
                   f"afade=t=in:d={fin},afade=t=out:st={ln - XF}:d={XF},adelay={int(st * 1000)}|{int(st * 1000)}[c{k}]")
    labels.append(f"[c{k}]")
filters.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:duration=longest,apad,"
               f"atrim=0:{total},highpass=f=35,loudnorm=I=-18:TP=-2:LRA=11[out]")
os.makedirs(os.path.join(P, "assets/audio"), exist_ok=True)
dst = os.path.join(P, "assets/audio/score.m4a")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filters),
                "-map", "[out]", "-c:a", "aac", "-b:a", "256k", dst], check=True)

# climax window = the scene whose id is music.climax_scene -> its clip span
climax = None
if M.get("climax_scene"):
    sc = next((s for s in E["scenes"] if s["id"] == M["climax_scene"]), None)
    if sc and sc["overlays"][0].get("lead_clip"):
        t = 0.0
        for c in E["clips"]:
            d = round(c["out"] - c["in"], 3)
            if c["id"] == sc["overlays"][0]["lead_clip"]:
                climax = (t, t + d)
            t += d

spans = []
for w in words:
    if spans and w["start"] - spans[-1][1] < 0.6:
        spans[-1][1] = max(spans[-1][1], w["end"])
    else:
        spans.append([w["start"], w["end"]])


def level(t, speaking):
    if not speaking:
        return 0.9 if t > speech_end - 0.1 else 0.8
    if climax and climax[0] <= t < climax[1]:
        return 0.34
    return 0.25


pts = [{"t": 0, "v": 0.8}]
for a, b in spans:
    pts.append({"t": round(max(0, a - 0.15), 3), "v": level(a, False) if a > 0.2 else 0.8})
    pts.append({"t": round(a, 3), "v": level(a, True)})
    pts.append({"t": round(b, 3), "v": level(b - 0.01, True)})
    pts.append({"t": round(b + 0.3, 3), "v": level(b + 0.3, False)})
clean = []
for p in sorted(pts, key=lambda p: p["t"]):
    if clean and p["t"] <= clean[-1]["t"]:
        clean[-1] = p
    else:
        clean.append(p)
json.dump({"src": "assets/audio/score.m4a", "automation": clean}, open(os.path.join(P, "data/music.json"), "w"), indent=1)
print("score ->", dst, "|", len(clean), "ducking points |", total, "s")
