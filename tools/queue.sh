#!/bin/bash
# queue.sh VIDEO_01 VIDEO_02 ... : build media, check, render each clip (skips clips already rendered)
cd "$(dirname "$0")/.."
mkdir -p renders logs
for id in "$@"; do
  slug=$(python3 -c "import json,re,unicodedata;t=json.load(open('specs/$id.json'))['topic'];t=unicodedata.normalize('NFKD',t).encode('ascii','ignore').decode();print(re.sub(r'[^A-Z0-9]+','_',t.upper()).strip('_'))")
  out="renders/${id}_${slug}.mp4"
  if [ -f "$out" ]; then echo "skip $out"; continue; fi
  echo "[$(date +%T)] build $id"
  python3 tools/build.py specs/$id.json > logs/$id.build.log 2>&1 || { echo "BUILD FAIL $id"; continue; }
  (cd episodes/$id && npx hyperframes check --json > ../../logs/$id.check.json 2>/dev/null)
  python3 -c "import json;d=json.load(open('logs/$id.check.json'));print('check ok' if d['ok'] else 'CHECK FAIL')"
  echo "[$(date +%T)] render $id"
  (cd episodes/$id && npx hyperframes render -o "../../$out.tmp.mp4" --crf 23 --max-bitrate 6M --quiet > ../../logs/$id.render.log 2>&1) && mv "$out.tmp.mp4" "$out" && echo "[$(date +%T)] done $out" || echo "RENDER FAIL $id"
done
