#!/bin/bash
# usage: tools/render_all.sh 01 02 ...   -> exports/KULIAH_XX_<SLUG>.mp4
cd "$(dirname "$0")/.."
for id in "$@"; do
  slug=$(python3 -c "import json;print(json.load(open('clips/KULIAH_$id.json'))['slug'])")
  out="$PWD/exports/KULIAH_${id}_${slug}.mp4"
  start=$(date +%s)
  npx --yes hyperframes@0.9.26 render "videos/KULIAH_$id" -o "$out" --fps 30 --crf 21 > "exports/.render_$id.log" 2>&1 \
    && echo "rendered $id $(( $(date +%s) - start ))s" || echo "FAILED $id (see exports/.render_$id.log)"
  cp "videos/KULIAH_$id/KULIAH_$id.srt" exports/ 2>/dev/null
done
echo RENDER_DONE
