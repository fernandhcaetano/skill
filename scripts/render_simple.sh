#!/usr/bin/env bash
# Corte + cor F + legenda pequena. Uso: render_simple.sh ENTRADA INICIO FIM LEGENDA.ass SAIDA.mp4
set -euo pipefail
cd "$(dirname "$0")/.."
ffmpeg -nostdin -v error -y -ss "$2" -to "$3" -i "$1" -map 0:v:0 -map 0:a:0 \
 -vf "zscale=w=1080:h=1920:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=gamma=0.97:saturation=1.05:contrast=1.12,fps=30,ass=$4" \
 -af "afade=t=in:d=0.03,loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 \
 -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 192k -movflags +faststart "$5"
echo "$5 $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$5")s $(du -h "$5" | cut -f1)"
