#!/usr/bin/env bash
# Corte + cor F + legenda pequena + som alto, em QUALIDADE MÁXIMA (fps original, CRF 14, AAC 320k).
# Uso: render_simple.sh ENTRADA INICIO FIM LEGENDA.ass SAIDA.mp4 [sem_cor]
set -euo pipefail
cd "$(dirname "$0")/.."
TONE="zscale=w=1080:h=1920:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=gamma=0.97:saturation=1.05:contrast=1.12"
[ "${6:-}" = "sem_cor" ] && TONE="format=yuv420p"
ffmpeg -nostdin -v error -y -ss "$2" -to "$3" -i "$1" -map 0:v:0 -map 0:a:0 \
 -vf "$TONE,ass=$4" \
 -af "afade=t=in:d=0.03,acompressor=threshold=-24dB:ratio=4:attack=5:release=120:makeup=3,alimiter=limit=0.89:level=false,loudnorm=I=-10:TP=-1.0:LRA=7" -ar 48000 \
 -c:v libx264 -preset slow -crf 14 -profile:v high -c:a aac -b:a 320k -movflags +faststart "$5"
echo "$5 $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$5")s $(du -h "$5" | cut -f1)"
