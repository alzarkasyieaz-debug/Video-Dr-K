#!/bin/bash
# sheet.sh <src.mp4> <out.jpg> t1 t2 ... : frames scaled to 1080x1920 with a 120px grid (labels every 240px)
src=$1; out=$2; shift 2; ins=(); n=0
for t in "$@"; do
  ffmpeg -v error -y -ss $t -i $src -frames:v 1 -vf "scale=1080:1920,drawgrid=w=120:h=120:t=2:c=yellow@0.5,drawtext=text='$t':x=20:y=20:fontsize=60:fontcolor=red" /tmp/sh_$n.png
  ins+=(-i /tmp/sh_$n.png); n=$((n+1))
done
ffmpeg -v error -y "${ins[@]}" -filter_complex "hstack=inputs=$n,scale=iw*0.32:-1" $out
