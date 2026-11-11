#!/usr/bin/env python3
"""Map a proof-read transcript onto whisper word timings.

usage: align_words.py <whisper.json> <window_start_s> <clip_start_s> <clip_end_s> <corrected.txt>
prints JSON [{text,start,end}] in clip-local seconds.

Whisper (-ml 1 -sow -oj) gives one word per segment. The corrected text is aligned to
those words with difflib: equal words keep their timings, replaced runs share the span
of the words they replace, so no timing is invented outside what was heard.
"""
import json, sys, re, difflib


def norm(w):
    return re.sub(r"[^\w]", "", w.lower())


def main():
    wj, win, cs, ce, txt = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
    segs = json.load(open(wj))["transcription"]
    raw = []
    for s in segs:
        t = s["text"].strip()
        if not t or t.startswith("[") or t.startswith("("):
            continue
        a = win + s["offsets"]["from"] / 1000
        b = win + s["offsets"]["to"] / 1000
        if b <= cs - 0.05 or a >= ce + 0.05:
            continue
        raw.append({"text": t, "start": max(a, cs) - cs, "end": min(b, ce) - cs})
    new = open(txt).read().split()
    A = [norm(w["text"]) for w in raw]
    B = [norm(w) for w in new]
    out = []
    sm = difflib.SequenceMatcher(a=A, b=B, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                r = raw[i1 + k]
                out.append({"text": new[j1 + k], "start": r["start"], "end": r["end"]})
        elif tag in ("replace", "insert"):
            if j2 == j1:
                continue
            if i2 > i1:
                a, b = raw[i1]["start"], raw[i2 - 1]["end"]
            else:  # pure insertion: squeeze between neighbours
                a = out[-1]["end"] if out else (raw[i1]["start"] if i1 < len(raw) else 0)
                b = raw[i1]["start"] if i1 < len(raw) else a + 0.3 * (j2 - j1)
                if b - a < 0.15 * (j2 - j1):
                    b = a + 0.15 * (j2 - j1)
            n = j2 - j1
            weights = [max(1, len(new[j1 + k])) for k in range(n)]
            tot = sum(weights); t = a
            for k in range(n):
                d = (b - a) * weights[k] / tot
                out.append({"text": new[j1 + k], "start": t, "end": t + d}); t += d
        # deletes: drop
    # whisper sometimes gives the first word of a segment zero length: share the
    # following words' span by character count so every word gets a visible highlight
    i = 0
    while i < len(out):
        if out[i]["end"] - out[i]["start"] < 0.1:
            j = i
            while j + 1 < len(out) and out[j]["end"] - out[i]["start"] < 0.1 * (j - i + 2) and j - i < 3:
                j += 1
            a, b = out[i]["start"], out[j]["end"]
            if b - a >= 0.1 * (j - i + 1):
                tot = sum(max(1, len(out[k]["text"])) for k in range(i, j + 1)); t = a
                for k in range(i, j + 1):
                    d = (b - a) * max(1, len(out[k]["text"])) / tot
                    out[k]["start"], out[k]["end"] = t, t + d; t += d
            i = j + 1
        else:
            i += 1
    # whisper word timings are contiguous: trim long holds so highlights don't linger
    for w in out:
        w["end"] = min(w["end"], w["start"] + 1.2)
        w["start"], w["end"] = round(w["start"], 3), round(w["end"], 3)
    json.dump(out, sys.stdout, ensure_ascii=False)


main()
