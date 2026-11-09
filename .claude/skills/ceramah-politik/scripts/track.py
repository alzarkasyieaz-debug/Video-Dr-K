#!/usr/bin/env python3
"""Speaker tracking -> digital camera keys (data/camera.json).

OpenCV HOG person detector at 5 fps (largest confident standing person = the speaker; head at
box top + 10% of its height), outlier rejection + Gaussian smoothing (sigma ~1 s), then each clip's
edit.json "zoom" profile:
  {"type": "push", "from": 1.22, "to": 1.40, "pow": 1}          slow push-in / pull (power curve)
  {"type": "ease", "from": 1.56, "to": 1.30}                    cosine ease (controlled zoom in/out)
  "punch": {"at": {"word": "x"}, "add": 0.08}                   hard punch-in from a spoken word
Head is placed at x=540, y=head_y (default 940: below the card zone, above the captions).
Scale is capped at 1.8 (720p sources go soft beyond that) and edges never show.

Needs: opencv-python-headless<5, numpy.   Usage: python3 track.py [project_dir]
"""
import json, os, sys
import cv2, numpy as np

P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
E = json.load(open(os.path.join(P, "edit.json")))
W, H, TX = 1080, 1920, 540
words = json.load(open(os.path.join(P, "data/words.json"))) if os.path.exists(os.path.join(P, "data/words.json")) else []
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())


def word_time(text, after=0.0):
    for w in words:
        if w["start"] >= after - 1e-6 and w["text"].strip(".,?!").lower() == text.lower():
            return w["start"]
    raise KeyError(text)


def detect(path):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    i, pts = 0, []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        if i % 6 == 0:
            h0, w0 = f.shape[:2]
            s = cv2.resize(f, (360, int(360 * h0 / w0)))
            rects, wts = hog.detectMultiScale(s, winStride=(4, 4), padding=(8, 8), scale=1.04)
            cand = [(rc, wt) for rc, wt in zip(rects, np.ravel(wts) if len(wts) else []) if rc[3] > s.shape[0] * 0.39]
            if cand:
                (x, y, w, h), _ = max(cand, key=lambda rw: rw[0][3] * rw[1])
                pts.append([i / fps, (x + w / 2) / 360, (y + 0.1 * h) / s.shape[0]])
            else:
                pts.append([i / fps, None, None])
        i += 1
    return pts


def clean(v):
    v = np.array([np.nan if x is None else x for x in v], dtype=float)
    idx = np.arange(len(v))
    ok = ~np.isnan(v)
    v = np.interp(idx, idx[ok], v[ok]) if ok.any() else np.full(len(v), 0.5)
    med = np.array([np.median(v[max(0, i - 3):i + 4]) for i in range(len(v))])
    bad = np.abs(v - med) > 0.08
    v[bad] = med[bad]
    k = np.exp(-0.5 * (np.arange(-10, 11) / 5.0) ** 2)
    k /= k.sum()
    return np.convolve(np.pad(v, 10, mode="edge"), k, "valid")


cam, start = {}, 0.0
for c in E["clips"]:
    d = round(c["out"] - c["in"], 3)
    z = c.get("zoom", {"type": "push", "from": 1.3, "to": 1.4})
    punch_t = None
    if z.get("punch"):
        a = z["punch"]["at"]
        punch_t = word_time(a["word"], a.get("after", 0.0)) + a.get("offset", 0.0) - start

    def scale(t):
        u = t / d
        if z["type"] == "ease":
            s = z["from"] + (z["to"] - z["from"]) * (0.5 - 0.5 * np.cos(np.pi * u))
        else:
            s = z["from"] + (z["to"] - z["from"]) * (u ** z.get("pow", 1.0))
        if punch_t is not None and t >= punch_t:
            s += z["punch"]["add"]
        return min(1.8, s)

    pts = detect(os.path.join(P, f"assets/footage/clip-{c['id']}.mp4"))
    ts = np.array([p[0] for p in pts])
    xs, ys = clean([p[1] for p in pts]), clean([p[2] for p in pts])
    ty = c.get("head_y", 940)
    keys = []
    times = list(np.arange(0, d, 0.4)) + [d]
    for t in times:
        hx, hy, s = np.interp(t, ts, xs), np.interp(t, ts, ys), scale(t)
        X = min(0, max(W * (1 - s), TX - s * hx * W))
        Y = min(0, max(H * (1 - s), ty - s * hy * H))
        keys.append([round(float(t), 2), round(float(X), 1), round(float(Y), 1), round(float(s), 4)])
    cam[c["id"]] = {"start": round(start, 3), "dur": d, "keys": keys}
    found = sum(p[1] is not None for p in pts)
    print(f"{c['id']}: speaker found in {found}/{len(pts)} samples, {len(keys)} keys")
    start += d
json.dump(cam, open(os.path.join(P, "data/camera.json"), "w"))
