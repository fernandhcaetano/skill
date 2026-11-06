"""Apara respirações/suspiros nas pontas de cada trecho de fala do corte.json.

Uso: python3 -I scripts/ferndoc/aparar.py raw/ferndoc/corte.json   (reescreve o arquivo; guarda .bak)

Para cada trecho ({"id", "ini", "fim"}), procura onde a VOZ começa e termina: energia na faixa 120–1000 Hz
(onde está a fundamental e os primeiros harmônicos da fala) acima de piso_de_ruído + 35 dB (voz fica 55–60 dB acima; suspiro até ~26). Respiração e suspiro
são ruído largo e fraco nessa faixa, então ficam de fora. Mantém 60 ms de folga antes e 100 ms depois.
Só mexe até 1,2 s para dentro de cada ponta (não corta palavras no meio do trecho).
"""
import json
import shutil
import sys
import wave

import numpy as np
from scipy.signal import butter, sosfilt

p = sys.argv[1]
c = json.load(open(p))
ch = {k["id"]: k for k in json.load(open("raw/ferndoc/chunks.json"))}
env = {}


def envelope(parte):
    if parte not in env:
        with wave.open(f"raw/ferndoc/p{parte}_48.wav") as w:
            x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
        y = sosfilt(butter(4, [120, 1000], "band", fs=48000, output="sos"), x)
        e = 10 * np.log10(np.convolve(y ** 2, np.ones(480) / 480, "same")[::480] + 1)  # 10 ms
        env[parte] = (e, np.percentile(e, 10))
    return env[parte]


shutil.copy(p, p + ".bak")
for x in c["cortes"]:
    if "id" not in x:
        continue
    e, piso = envelope(ch[x["id"]]["parte"])
    a, b = int(x["ini"] * 100), int(x["fim"] * 100)
    voz = np.where(e[a:b] > piso + 35)[0]
    if len(voz) == 0:
        continue
    ini = max(x["ini"], min(x["ini"] + 1.2, (a + voz[0]) / 100 - 0.06))
    fim = min(x["fim"], max(x["fim"] - 1.2, (a + voz[-1]) / 100 + 0.10))
    if ini - x["ini"] > 0.05 or x["fim"] - fim > 0.05:
        print(f'{x["id"]}: {x["ini"]:.2f}-{x["fim"]:.2f} -> {ini:.2f}-{fim:.2f}')
    x["ini"], x["fim"] = round(ini, 2), round(fim, 2)
json.dump(c, open(p, "w"), ensure_ascii=False, indent=1)
