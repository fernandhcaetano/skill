#!/usr/bin/env bash
# Baixa vídeos do Drive (pares NOME:ID), extrai áudio 16k e transcreve com whisper (palavra a palavra).
set -u
cd "$(dirname "$0")/.."
mkdir -p raw/lote
for pair in "$@"; do
  n=${pair%%:*}; id=${pair#*:}
  [ -s raw/lote/$n.MOV ] || curl -sSL -o raw/lote/$n.MOV "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t" &
done
wait
for pair in "$@"; do
  n=${pair%%:*}
  ffmpeg -nostdin -v error -y -i raw/lote/$n.MOV -ac 1 -ar 16000 raw/lote/$n.wav
  (cd whisper.cpp && ./main -m ggml-medium.bin -l pt -t "$(nproc)" -ml 1 -sow -ojf -of ../raw/lote/$n -f ../raw/lote/$n.wav >/dev/null 2>&1)
  echo "== $n $(ffprobe -v error -show_entries format=duration -of csv=p=0 raw/lote/$n.MOV)s $(ffprobe -v error -select_streams v:0 -show_entries stream=color_transfer -of csv=p=0 raw/lote/$n.MOV)"
  python3 -I - "$n" <<'PY'
import json,sys
n=sys.argv[1];line='';k=0
for s in json.load(open(f'raw/lote/{n}.json'))['transcription']:
    t=s['text'].strip()
    if not t: continue
    line+=f"[{k}]{t}({s['offsets']['from']/1000:.1f}) ";k+=1
    if t[-1] in '.?!': print(line); line=''
print(line)
PY
done
