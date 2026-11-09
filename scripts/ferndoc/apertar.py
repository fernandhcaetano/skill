"""Tira TODO intervalo sem voz de dentro dos trechos de fala: suspiros, respirações, pausas lendo o iPad.

Uso: python3 -I scripts/ferndoc/apertar.py raw/ferndoc/corte.json [min_pausa=0.25]   (reescreve; guarda .bak2)

Para cada trecho {"id","ini","fim"}: mede a energia na faixa da voz (120–1000 Hz, 10 ms). Onde ela fica abaixo de
piso_de_ruído + 30 dB por pelo menos `min_pausa` segundos, o trecho é partido e esse intervalo sai (deixa 70 ms
antes e 90 ms depois da voz para não comer sílaba). Voz falada fica 55–60 dB acima do piso; suspiro e respiração
ficam até ~26 dB. As pontas do trecho também são aparadas. Inserções (clipes/espaços) não são tocadas.
"""
import json
import shutil
import sys
import wave

import numpy as np
from scipy.signal import butter, sosfilt

p = sys.argv[1]
MIN = float(sys.argv[2]) if len(sys.argv) > 2 else 0.25
PRE, POS, LIM = 0.07, 0.09, 30
c = json.load(open(p))
ch = {k["id"]: k for k in json.load(open("raw/ferndoc/chunks.json"))}
env = {}


def envelope(parte):
    if parte not in env:
        with wave.open(f"raw/ferndoc/p{parte}_48.wav") as w:
            x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
        y = sosfilt(butter(4, [120, 1000], "band", fs=48000, output="sos"), x)
        e = 10 * np.log10(np.convolve(y ** 2, np.ones(480) / 480, "same")[::480] + 1)
        env[parte] = (e, np.percentile(e, 10))
    return env[parte]


shutil.copy(p, p + ".bak2")
novos, tirado = [], 0.0
for x in c["cortes"]:
    if "id" not in x:
        novos.append(x)
        continue
    e, piso = envelope(ch[x["id"]]["parte"])
    a, b = int(round(x["ini"] * 100)), int(round(x["fim"] * 100))
    voz = e[a:b] > piso + LIM
    # junta "ilhas" de voz separadas por menos de MIN segundos
    idx = np.where(voz)[0]
    if len(idx) == 0:
        tirado += x["fim"] - x["ini"]
        continue
    blocos, s0, prev = [], idx[0], idx[0]
    for i in idx[1:]:
        if (i - prev) / 100 >= MIN:
            blocos.append((s0, prev)); s0 = i
        prev = i
    blocos.append((s0, prev))
    for s0, s1 in blocos:
        if (s1 - s0) / 100 < 0.06:      # estalo isolado, não é fala
            continue
        ini = max(x["ini"], (a + s0) / 100 - PRE)
        fim = min(x["fim"], (a + s1) / 100 + POS)
        novos.append({**x, "ini": round(ini, 2), "fim": round(fim, 2)})
    tirado += (x["fim"] - x["ini"]) - sum(min(x["fim"], (a + s1) / 100 + POS) - max(x["ini"], (a + s0) / 100 - PRE)
                                          for s0, s1 in blocos if (s1 - s0) / 100 >= 0.06)
# Fragmentos muito curtos (< 0,6 s) entre dois cortes dão sensação de "trava" (ele reclamou em 09/11).
# Se a pausa até o vizinho for pequena (≤ 0,5 s), junta com ele; senão, só avisa para decidir na mão.
junt = []
for x in novos:
    if junt and "id" in x and "id" in junt[-1] and x["id"] == junt[-1]["id"]:
        a_, b_ = junt[-1], x
        curto = (a_["fim"] - a_["ini"] < 0.6) or (b_["fim"] - b_["ini"] < 0.6)
        if curto and b_["ini"] - a_["fim"] <= 0.5:
            a_["fim"] = b_["fim"]
            continue
    junt.append(x)
novos = junt
for x in novos:
    if "id" in x and x["fim"] - x["ini"] < 0.6:
        print(f"ATENÇÃO fragmento curto {x['id']} {x['ini']}-{x['fim']} ({x['fim'] - x['ini']:.2f}s): decidir na mão")
c["cortes"] = novos
json.dump(c, open(p, "w"), ensure_ascii=False, indent=1)
print(f"{sum(1 for k in novos if 'id' in k)} trechos de fala, {tirado:.1f}s sem voz removidos")
