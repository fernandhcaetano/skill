"""Monta o corte: escolhe os trechos de fala, gera o áudio limpo e o src/edit.json.

Uso: python3 -I scripts/build-edit.py  (rodar na raiz do projeto)
"""
import json
import os
import subprocess
import wave
import array

FPS = 30
PAD = 0.08  # respiro antes/depois de cada trecho (s)

# Trechos (índices de raw/segs.json) que ficam. Os demais são silêncio,
# ruído ou falas erradas/repetidas.
# Vídeo atual: Reserva 1P5P (raw/1p5p/fala.mov = entrada + só audio tb + só audio + final).
# 1: "Sim" curto e seco entre dois cortes (soava como um ruído no 0:04).
# 11: ruído no começo do segundo "só audio".
KEEP = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20,
        21, 22, 23, 24, 25]

# Ajustes dentro de um trecho: lista de (início, fim) em segundos da fonte.
# Micro-pausas dentro das frases (só nos trechos cobertos por B-roll, 14–58 s do vídeo):
# corta o miolo de cada pausa e deixa ~50 ms de cada lado.
PAUSES = {4: [(19.27, 19.50)], 5: [(21.71, 21.90)], 8: [(31.17, 31.41), (32.05, 32.27)],
          10: [(37.33, 37.59)], 13: [(44.78, 45.05)], 17: [(59.74, 59.97)]}
SPLIT = {i: [(None, ps[0][0] + 0.05)] + [(a[1] - 0.05, b[0] + 0.05) for a, b in zip(ps, ps[1:])]
         + [(ps[-1][1] - 0.05, None)] for i, ps in PAUSES.items()}

# Trechos cobertos por B-roll: respiro menor entre as frases, para a fala ficar mais "colada".
TIGHT, TIGHT_PAD = set(range(4, 22)), 0.05

# Silêncio (s) inserido depois de um trecho: "respiro" de marca com o plano do logo.
# Versão curta: sem a frase "E esse ano, ele completa 10 anos." (o "há 10 anos" já foi dito).
# Termina o trecho 3 em "…para quem precisa." e emenda direto no "Oi, eu sou a Ludy" (sem tela vazia).
SEM_SEGUNDO_10_ANOS = os.environ.get("SEM_SEGUNDO_10_ANOS", "0") == "1"
if SEM_SEGUNDO_10_ANOS:
    SPLIT[3] = [(None, 13.04)]

# Respiro extra (s) no fim de um trecho, com o som ambiente original: a frase termina sem pressa.
END_EXTRA = {3: 0.5}  # "…ele completa 10 anos." antes do logo

GAP_AFTER = {25: 0.6}  # 25: respiro final antes do fim do vídeo

segs = json.load(open("raw/segs.json"))

# Energia do áudio para encaixar cada corte no ponto mais silencioso.
with wave.open("raw/audio16.wav") as w:
    sr = w.getframerate()
    pcm = array.array("h", w.readframes(w.getnframes()))
HOP = sr // 100  # 10 ms
rms = [sum(x * x for x in pcm[i:i + HOP]) / HOP for i in range(0, len(pcm) - HOP, HOP)]


def snap(t, radius=0.15):
    i0, i1 = int((t - radius) * 100), int((t + radius) * 100)
    i0, i1 = max(0, i0), min(len(rms) - 1, i1)
    best = min(range(i0, i1 + 1), key=lambda i: rms[i])
    return best / 100


def words_of(i):
    d = json.load(open("raw/chunks/c%03d.wav.json" % i))["transcription"]
    off = max(0, segs[i][0] - 0.1)
    out = []
    for t in d:
        txt = t["text"].strip()
        if not txt or txt.startswith("["):
            continue
        out.append({"text": txt, "start": off + t["offsets"]["from"] / 1000,
                    "end": off + t["offsets"]["to"] / 1000})
    return out


pieces = []  # (src_start, src_end, words, gap)
for i in KEEP:
    a, b = segs[i]
    parts = SPLIT.get(i, [(None, None)])
    for pa, pb in parts:
        pad = TIGHT_PAD if i in TIGHT else PAD
        s = a - pad if pa is None else snap(pa, 0.02)  # pausas já medidas: sem deslocar
        e = b + pad + END_EXTRA.get(i, 0) if pb is None else snap(pb, 0.02)
        ws = [w for w in words_of(i) if s - 0.05 <= (w["start"] + w["end"]) / 2 <= e + 0.05]
        pieces.append([max(0.0, s), e, ws, 0.0])
    pieces[-1][3] = GAP_AFTER.get(i, 0.0)

# Junta trechos que se encostam e alinha tudo em frames.
merged = []
for s, e, ws, gap in pieces:
    if merged and s - merged[-1][1] < 0.12 and not merged[-1][3]:
        merged[-1][1] = max(merged[-1][1], e)
        merged[-1][2] += ws
        merged[-1][3] = gap
    else:
        merged.append([s, e, ws, gap])

segments, words, out_t = [], [], 0
gaps = []  # (outStart, dur) dos silêncios inseridos
for s, e, ws, gap in merged:
    fs, fe = round(s * FPS), round(e * FPS)
    s, e = fs / FPS, fe / FPS
    for w in ws:
        words.append({"text": w["text"],
                      "start": round(out_t + max(0, w["start"] - s), 3),
                      "end": round(out_t + min(e - s, w["end"] - s), 3)})
    segments.append({"srcStart": s, "srcEnd": e, "outStart": round(out_t, 3)})
    out_t += e - s
    if gap:
        gaps.append((round(out_t, 3), gap))
        out_t += gap

# Limpeza do texto das legendas: erros do Whisper, reticências e maiúsculas.
FIXES = {("vai", "ressaltar"): "vale", ("caber", "a"): "cabe"}
PROPER = {"lula", "bolsonaro", "rio", "janeiro", "pt", "senado", "câmara", "deputados", "ruas"}
for k, w in enumerate(words):
    nxt = words[k + 1]["text"].strip(",.?!").lower() if k + 1 < len(words) else ""
    t = w["text"].replace("...", "").replace("…", "")
    t = FIXES.get((t.lower(), nxt), t)
    if t.strip(",.?!").lower() not in PROPER:
        t = t.lower()
    elif t.lower() == "pt":
        t = "PT"
    else:
        t = t[0].upper() + t[1:]
    w["text"] = t

json.dump({"fps": FPS, "duration": round(out_t, 3), "segments": segments, "words": words,
           "gaps": [{"outStart": a, "dur": d} for a, d in gaps]},
          open(os.environ.get("EDIT_OUT", "src/edit.json"), "w"), ensure_ascii=False, indent=1)

# Áudio: cortes com micro-fade (evita estalos), redução de ruído e volume -14 LUFS.
chains, labels = [], []
# segmento k seguido de silêncio inserido
GAP_AFTER_OUT = {k: d for k, sg in enumerate(segments) for a, d in gaps
                 if abs(sg["outStart"] + sg["srcEnd"] - sg["srcStart"] - a) < 1e-3}
for k, sg in enumerate(segments):
    d = sg["srcEnd"] - sg["srcStart"]
    chains.append(f"[0:a]atrim={sg['srcStart']}:{sg['srcEnd']},asetpts=PTS-STARTPTS,"
                  f"afade=t=in:d=0.01,afade=t=out:st={max(0, d - 0.015)}:d=0.015[a{k}]")
    labels.append(f"[a{k}]")
    g = GAP_AFTER_OUT.get(k)
    if g:
        chains.append(f"anullsrc=r=48000:cl=mono,atrim=0:{g}[g{k}]")
        labels.append(f"[g{k}]")
# DENOISE=0 gera public/voice_raw.wav: mesmos cortes, só volume ajustado, sem mexer no ruído.
DENOISE = os.environ.get("DENOISE", "1") != "0"
# 1P5P: externa com ronco grave (vento/trânsito). RNNoise (arnndn) tira ~15 dB a mais que só o afftdn.
# Modelo: curl -L -o raw/models/sh.rnnn https://raw.githubusercontent.com/richardpl/arnndn-models/master/sh.rnnn
clean = "highpass=f=100,arnndn=m=raw/models/sh.rnnn,afftdn=nr=10:nf=-45:tn=1,lowpass=f=12000," \
    "acompressor=threshold=-20dB:ratio=3:attack=5:release=80," if DENOISE else ""
graph = ";".join(chains) + ";" + "".join(labels) + f"concat=n={len(labels)}:v=0:a=1," \
    + clean + "loudnorm=I=-14:TP=-1.5:LRA=7[out]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "raw/audio48.wav", "-filter_complex", graph, "-map", "[out]",
                "-ar", "48000", "public/voice.wav" if DENOISE else "public/voice_raw.wav"], check=True)

print(f"{len(segments)} cortes, {len(words)} palavras, duração final {out_t:.1f}s ")
