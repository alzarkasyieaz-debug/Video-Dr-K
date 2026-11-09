#!/usr/bin/env python3
"""Forced-align each clip's display text (edit.json clips[].text) to its audio.

Model: MahmoudAshraf/mms-300m-1130-forced-aligner (multilingual wav2vec2 CTC, Latin chars), downloaded
from Hugging Face on first run. Numbers and honorifics are aligned in their spoken form via
edit.json "spoken" (e.g. "3.6" -> "tiga perpuluhan enam", "SAW" -> "sallallahu alaihi wasallam").
Writes data/words.json on the OUTPUT timeline (clips back to back).

Needs: torch, transformers, soundfile, numpy.   Usage: python3 align.py [project_dir]
"""
import json, os, re, sys
import numpy as np, soundfile as sf, torch
from transformers import AutoTokenizer, Wav2Vec2ForCTC

P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
E = json.load(open(os.path.join(P, "edit.json")))
M = "MahmoudAshraf/mms-300m-1130-forced-aligner"
tok = AutoTokenizer.from_pretrained(M)
model = Wav2Vec2ForCTC.from_pretrained(M).eval()
V = tok.get_vocab()
spoken = E.get("spoken", {})


def norm(w):
    w = re.sub(r"[^\w\.'-]", "", w).strip(".")
    w = spoken.get(w, w).lower().replace("-", " ")
    return "".join(ch for ch in w if ch in V and ch != "'")


def viterbi(lp, tokens):
    T, S = lp.shape[0], 2 * len(tokens) + 1
    ext = [0] * S
    for i, t in enumerate(tokens):
        ext[2 * i + 1] = t
    dp = np.full((T, S), -1e9)
    bp = np.zeros((T, S), dtype=np.int32)
    dp[0, 0], dp[0, 1] = lp[0, 0], lp[0, ext[1]]
    for t in range(1, T):
        prev = dp[t - 1]
        a = prev
        b = np.concatenate([[-1e9], prev[:-1]])
        c = np.concatenate([[-1e9, -1e9], prev[:-2]])
        allow = np.array([s > 1 and ext[s] != 0 and ext[s] != ext[s - 2] for s in range(S)])
        c = np.where(allow, c, -1e9)
        stack = np.stack([a, b, c])
        arg = stack.argmax(0)
        dp[t] = stack.max(0) + lp[t, ext]
        bp[t] = np.arange(S) - arg
    s = S - 1 if dp[T - 1, S - 1] > dp[T - 1, S - 2] else S - 2
    path = [0] * T
    for t in range(T - 1, -1, -1):
        path[t] = s
        s = bp[t, s]
    return path


out, wid, start = [], 0, 0.0
for c in E["clips"]:
    dur = round(c["out"] - c["in"], 3)
    a, sr = sf.read(os.path.join(P, f"data/vo/{c['id']}.wav"))
    with torch.no_grad():
        x = torch.tensor(a, dtype=torch.float32)[None]
        x = (x - x.mean()) / (x.std() + 1e-7)
        lp = torch.log_softmax(model(x).logits[0], -1).numpy()
    fr = dur / lp.shape[0]
    disp = c["text"].split()
    toks, owner = [], []
    for k, w in enumerate(disp):
        for ch in norm(w):
            toks.append(V[ch])
            owner.append(k)
    path = viterbi(lp, toks)
    first, last = {}, {}
    for t, s in enumerate(path):
        if s % 2 == 1:
            k = owner[s // 2]
            first.setdefault(k, t)
            last[k] = t
    for k, w in enumerate(disp):
        out.append({"id": f"w{wid}", "clip": c["id"], "text": w,
                    "start": round(start + first[k] * fr, 3), "end": round(start + (last[k] + 1) * fr, 3)})
        wid += 1
    print(c["id"], " ".join(f"{o['text']}@{o['start']:.2f}" for o in out if o["clip"] == c["id"]))
    start = round(start + dur, 3)
json.dump(out, open(os.path.join(P, "data/words.json"), "w"), ensure_ascii=False, indent=0)
print(len(out), "words -> data/words.json")
