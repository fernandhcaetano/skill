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
KEEP = [1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 26, 27,
        28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 45,
        46, 47, 48, 49, 50, 51, 52, 53, 54]

# Ajustes dentro de um trecho: lista de (início, fim) em segundos da fonte.
# 48: "o PT já tem uma..." -> corta depois de "PT" (ele se corrige no 49).
# 52: "pra ano que vem, não, né?" -> remove a correção.
SPLIT = {
    48: [(None, 162.47)],
    52: [(None, 175.46), (177.51, None)],
}

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


pieces = []  # (src_start, src_end, words)
for i in KEEP:
    a, b = segs[i]
    parts = SPLIT.get(i, [(None, None)])
    for pa, pb in parts:
        s = a - PAD if pa is None else snap(pa)
        e = b + PAD if pb is None else snap(pb)
        ws = [w for w in words_of(i) if s - 0.05 <= (w["start"] + w["end"]) / 2 <= e + 0.05]
        pieces.append([max(0.0, s), e, ws])

# Junta trechos que se encostam e alinha tudo em frames.
merged = []
for s, e, ws in pieces:
    if merged and s - merged[-1][1] < 0.12:
        merged[-1][1] = max(merged[-1][1], e)
        merged[-1][2] += ws
    else:
        merged.append([s, e, ws])

segments, words, out_t = [], [], 0
for s, e, ws in merged:
    fs, fe = round(s * FPS), round(e * FPS)
    s, e = fs / FPS, fe / FPS
    for w in ws:
        words.append({"text": w["text"],
                      "start": round(out_t + max(0, w["start"] - s), 3),
                      "end": round(out_t + min(e - s, w["end"] - s), 3)})
    segments.append({"srcStart": s, "srcEnd": e, "outStart": round(out_t, 3)})
    out_t += e - s

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

json.dump({"fps": FPS, "duration": round(out_t, 3), "segments": segments, "words": words},
          open("src/edit.json", "w"), ensure_ascii=False, indent=1)

# Áudio: cortes com micro-fade (evita estalos), redução de ruído e volume -14 LUFS.
chains, labels = [], []
for k, sg in enumerate(segments):
    d = sg["srcEnd"] - sg["srcStart"]
    chains.append(f"[0:a]atrim={sg['srcStart']}:{sg['srcEnd']},asetpts=PTS-STARTPTS,"
                  f"afade=t=in:d=0.01,afade=t=out:st={max(0, d - 0.015)}:d=0.015[a{k}]")
    labels.append(f"[a{k}]")
# DENOISE=0 gera public/voice_raw.wav: mesmos cortes, só volume ajustado, sem mexer no ruído.
DENOISE = os.environ.get("DENOISE", "1") != "0"
clean = "highpass=f=80,afftdn=nr=14:nf=-30:tn=1,lowpass=f=12000," \
    "acompressor=threshold=-20dB:ratio=3:attack=5:release=80," if DENOISE else ""
graph = ";".join(chains) + ";" + "".join(labels) + f"concat=n={len(labels)}:v=0:a=1," \
    + clean + "loudnorm=I=-14:TP=-1.5:LRA=7[out]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "raw/audio48.wav", "-filter_complex", graph, "-map", "[out]",
                "-ar", "48000", "public/voice.wav" if DENOISE else "public/voice_raw.wav"], check=True)

print(f"{len(segments)} cortes, {len(words)} palavras, duração final {out_t:.1f}s (original 187.8s)")
