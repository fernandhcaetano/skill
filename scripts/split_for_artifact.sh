#!/usr/bin/env bash
# Divide um vídeo em partes ≤19 MB para o Artefato (nenhuma parte pode começar com '<').
# Também gera uma prévia leve (≤19 MB). Uso: split_for_artifact.sh VIDEO.mp4 PASTA PREFIXO
set -euo pipefail
V=$1; D=$2; P=$3; mkdir -p "$D"; find "$D" -type f -delete
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V")
for sz in 18900000 18700000 18500000 18300000 18100000; do
  find "$D" -name "${P}_hq_*" -delete
  split -b $sz -d -a 2 --additional-suffix=.mp4 "$V" "$D/${P}_hq_"
  ok=1; for f in "$D/${P}_hq_"*; do python3 -I -c "import sys;sys.exit(1 if open(sys.argv[1],'rb').read(512).lstrip()[:1]==b'<' else 0)" "$f" || ok=0; done
  [ $ok = 1 ] && break
done
BR=$(python3 -c "print(int(min(6000, 18.5*8*1024/$DUR - 128)))")
ffmpeg -nostdin -v error -y -i "$V" -c:v libx264 -preset slow -b:v ${BR}k -maxrate $((BR*3/2))k -bufsize $((BR*2))k -c:a aac -b:a 128k -movflags +faststart "$D/${P}_preview.mp4"
ls -l "$D"; echo "SIZE $(stat -c%s "$V")"
