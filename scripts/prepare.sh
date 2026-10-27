#!/usr/bin/env bash
# Prepara um vídeo bruto para edição: proxy 1080p SDR, áudio, trechos de fala e transcrição.
# Uso: bash scripts/prepare.sh raw/MEU_VIDEO.MOV
set -euo pipefail
cd "$(dirname "$0")/.."
SRC="$1"
mkdir -p raw/chunks public

# 1. Proxy 1080x1920 @ 30 fps. O tonemap converte HDR (HLG do iPhone) para SDR; em vídeo SDR ele é inofensivo.
ffmpeg -v error -y -i "$SRC" -map 0:v:0 -an \
  -vf "zscale=w=1080:h=1920:t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=mobius:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,fps=30" \
  -c:v libx264 -preset veryfast -crf 18 -g 30 public/video_proxy.mp4 &
PROXY=$!

# 2. Áudio (48 kHz para o resultado final, 16 kHz para o Whisper).
ffmpeg -v error -y -i "$SRC" -map 0:a:0 -ac 1 -ar 48000 raw/audio48.wav
ffmpeg -v error -y -i raw/audio48.wav -ar 16000 raw/audio16.wav

# 3. Divide nos silêncios e transcreve cada trecho isolado (sem contexto),
#    para que repetições e falas erradas apareçam em vez de serem "limpas" pelo Whisper.
python3 -I scripts/split-chunks.py
(cd whisper.cpp && ./main -m ggml-medium.bin -l pt -t "$(nproc)" -mc 0 -ml 1 -sow -ojf -otxt \
  $(ls ../raw/chunks/c*.wav | sed 's/^/-f /') > /dev/null 2>&1)

python3 -I -c "
import json
segs = json.load(open('raw/segs.json'))
for i, (a, b) in enumerate(segs):
    t = open('raw/chunks/c%03d.wav.txt' % i).read().strip().replace('\n', ' ')
    print(f'{i:02d} [{a:6.2f}-{b:6.2f}] {t}')
" | tee raw/chunks.txt

wait $PROXY
echo "Pronto: revise raw/chunks.txt e preencha KEEP/SPLIT em scripts/build-edit.py"
