#!/bin/bash
# cover_splice.sh VIDEO_01 ... : add the front cover to already-rendered clips.
# Only the opening changes (cover poster, hook camera, first captions), so render 0..T and join it to the
# existing render from T on (frame-exact, original audio kept). Writes renders/<ID>_<slug>.mp4 in place.
cd "$(dirname "$0")/.."
mkdir -p logs renders/work-cover
for id in "$@"; do
  old=$(ls renders/${id}_*.mp4 2>/dev/null | grep -v tmp | head -1)
  [ -f "$old" ] || { echo "NO RENDER $id"; continue; }
  if [ -f "renders/work-cover/$id.done" ]; then echo "skip $id"; continue; fi
  echo "[$(date +%T)] $id"
  python3 tools/build.py specs/$id.json --html-only > logs/$id.cover.build.log 2>&1 || { echo "BUILD FAIL $id"; continue; }
  (cd episodes/$id && npx hyperframes check --json > ../../logs/$id.check.json 2>/dev/null)
  python3 -c "import json,sys;d=json.load(open('logs/$id.check.json'));sys.exit(0 if d['ok'] else 1)" || { echo "CHECK FAIL $id"; continue; }
  # T: one second past the hook, on a frame boundary
  T=$(python3 -c "import json,math;b=json.load(open('deliverables/$id/build.json'));print(f'{math.ceil((b[\"hook_end\"]+1.0)*30)/30:.6f}')")
  NF=$(python3 -c "print(round($T*30))")
  head=renders/work-cover/$id.head.mp4
  (cd episodes/$id && npx hyperframes render --start 0 --end $T -o "../../$head" --crf 14 --quiet > ../../logs/$id.cover.render.log 2>&1) || { echo "RENDER FAIL $id"; continue; }
  tmp=renders/work-cover/$id.spliced.mp4
  ffmpeg -v error -y -i "$head" -i "$old" -filter_complex \
    "[0:v]trim=end_frame=$NF,setpts=PTS-STARTPTS[a];[1:v]trim=start_frame=$NF,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0,format=yuv420p[v]" \
    -map "[v]" -map 1:a -c:v libx264 -preset medium -crf 21 -maxrate 6M -bufsize 12M -profile:v high -r 30 -c:a copy -movflags +faststart "$tmp" \
    || { echo "SPLICE FAIL $id"; continue; }
  a=$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 "$old")
  b=$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 "$tmp")
  [ "$a" = "$b" ] || { echo "FRAME COUNT MISMATCH $id old=$a new=$b"; continue; }
  cp -n "$old" "renders/work-cover/$id.orig.mp4" && mv "$tmp" "$old" && touch "renders/work-cover/$id.done" && echo "[$(date +%T)] done $old (T=$T)"
  rm -rf /tmp/hyperframes-extract-cache-0   # decoded-frame cache grows ~200 MB per render
done
