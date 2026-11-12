#!/usr/bin/env python3
"""words.py <src> <a> <b> : print words with start times in a source range."""
import json, sys
segs = json.load(open(f"/home/user/src/{sys.argv[1]}.turbo.json")); a, b = float(sys.argv[2]), float(sys.argv[3])
line = []
for s in segs:
    for w in s["words"]:
        if a <= w["s"] <= b: line.append(f'{w["w"].strip()}@{w["s"]:.2f}')
print(" ".join(line))
