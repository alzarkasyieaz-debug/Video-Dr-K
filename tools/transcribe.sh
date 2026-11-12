#!/bin/bash
# Malay transcription with whisper.cpp (the runtime `npx hyperframes transcribe` builds).
#
#   tools/transcribe.sh full  <lecture.mp4> <outdir>            # whole lecture, model small -> <outdir>/full.srt
#   tools/transcribe.sh clip  <lecture.mp4> <from_s> <to_s> <out.json>   # word-level, model medium
#
# Models live in ~/.cache/hyperframes/whisper/models. Node inside the CLI cannot reach
# huggingface.co through the proxy, so models are fetched with curl here.
set -e
W=~/.cache/hyperframes/whisper
CLI=$W/whisper.cpp/build/bin/whisper-cli
model() {
  [ -f "$W/models/ggml-$1.bin" ] || { mkdir -p "$W/models"; curl -sSL -o "$W/models/ggml-$1.bin" "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-$1.bin"; }
}
if [ ! -x "$CLI" ]; then
  echo "whisper-cli missing: run once  npx hyperframes transcribe <any.wav> -e whisper -m small -l ms  (it builds whisper.cpp), then retry" >&2
  exit 1
fi
case "$1" in
  full)
    model small; mkdir -p "$3"
    ffmpeg -nostdin -v error -y -i "$2" -vn -ac 1 -ar 16000 "$3/full.wav"
    "$CLI" -m "$W/models/ggml-small.bin" -f "$3/full.wav" -l ms -t "$(nproc)" -mc 0 -osrt -of "$3/full" -pp
    ;;
  clip)
    model medium; tmp=$(mktemp --suffix .wav)
    ffmpeg -nostdin -v error -y -ss "$3" -to "$4" -i "$2" -vn -ac 1 -ar 16000 "$tmp"
    "$CLI" -m "$W/models/ggml-medium.bin" -f "$tmp" -l ms -t "$(nproc)" -ml 1 -sow -oj -of "${5%.json}" -np </dev/null >/dev/null 2>&1
    rm -f "$tmp"; echo "window starts at $3 s -> put  \"window\": $3  in the clip spec"
    ;;
  *) sed -n 2,7p "$0"; exit 1 ;;
esac
