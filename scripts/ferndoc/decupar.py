"""Decupagem de um ou mais vídeos brutos (partes da mesma gravação).

Uso: python3 -I scripts/ferndoc/decupar.py raw/ferndoc/parte1.mov raw/ferndoc/parte2.mov ...
     (na ordem de gravação; rodar na raiz do projeto)

Gera em raw/ferndoc/:
  pN_48.wav / pN_16.wav   áudio de cada parte
  chunks.json             trechos de fala [{id, parte, ini, fim, texto, palavras:[{w,s,e}]}]
  chunks.txt              lista legível para decidir os cortes, com marcação de trechos parecidos
                          ("≈ 1.04" = fala muito parecida com o trecho 1.04: repetição/nova tentativa)
"""
import difflib
import json
import os
import re
import subprocess
import sys
import unicodedata
import wave

import numpy as np

OUT = "raw/ferndoc"
os.makedirs(OUT, exist_ok=True)
videos = sys.argv[1:]
if not videos:
    sys.exit(__doc__)


def run(*a):
    return subprocess.run(a, capture_output=True, text=True)


def norm(t):
    t = unicodedata.normalize("NFKD", t.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", " ", t).split()


from faster_whisper import WhisperModel  # noqa: E402
model = WhisperModel(os.environ.get("WHISPER", "medium"), device="cpu", compute_type="int8")

chunks = []
for p, v in enumerate(videos, 1):
    a48, a16 = f"{OUT}/p{p}_48.wav", f"{OUT}/p{p}_16.wav"
    run("ffmpeg", "-v", "error", "-y", "-i", v, "-map", "0:a:0", "-ac", "1", "-ar", "48000", a48)
    run("ffmpeg", "-v", "error", "-y", "-i", a48, "-ar", "16000", a16)
    dur = float(run("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a48).stdout)
    with wave.open(a16) as w:
        pcm = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    # Pausas: limiar adaptado ao ruído de fundo (carro, rua, ar-condicionado), não um valor fixo.
    db = 20 * np.log10(np.sqrt(np.convolve(pcm ** 2, np.ones(320) / 320, "same")[::160]) + 1e-6)  # 10 ms
    thr = min(np.percentile(db, 15) + 9, -30)
    quiet = db < thr
    segs, k0 = [], None
    for i, q in enumerate(np.append(quiet, True)):
        if not q and k0 is None:
            k0 = i
        elif q and k0 is not None:
            # só fecha o trecho se o silêncio durar >= 0,25 s
            if i + 25 >= len(quiet) or quiet[i:i + 25].all():
                if (i - k0) / 100 > 0.15:
                    segs.append((k0 / 100, i / 100))
                k0 = None
    merged = []
    for a, b in segs:  # junta trechos separados por menos de 0,25 s
        if merged and a - merged[-1][1] < 0.25:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    segs = merged
    for k, (a, b) in enumerate(segs):
        o = max(0.0, a - 0.1)
        piece = pcm[int(o * 16000):int((b + 0.1) * 16000)]
        # Cada trecho isolado e sem contexto: repetições e erros aparecem em vez de serem "limpos".
        res, _ = model.transcribe(piece, language="pt", word_timestamps=True, condition_on_previous_text=False,
                                  vad_filter=False, beam_size=5)
        words = [{"w": x.word.strip(), "s": round(o + x.start, 2), "e": round(o + x.end, 2)}
                 for s in res for x in s.words if x.word.strip()]
        chunks.append({"id": f"{p}.{k:02d}", "parte": p, "ini": round(a, 2), "fim": round(b, 2),
                       "texto": " ".join(x["w"] for x in words), "palavras": words})
    print(f"parte {p}: {len(segs)} trechos, {dur:.1f}s", file=sys.stderr)

# Repetições: compara FRASE a frase (sequências de 3 palavras em comum), dentro da mesma parte e entre partes.
def grams(t):
    return {tuple(t[i:i + 3]) for i in range(len(t) - 2)}


frases = []  # (chunk_id, ini, fim, texto)
for c in chunks:
    cur = []
    for w in c["palavras"]:
        cur.append(w)
        if w["w"][-1:] in ".?!" or w is c["palavras"][-1]:
            frases.append((c["id"], cur[0]["s"], cur[-1]["e"], " ".join(x["w"] for x in cur))); cur = []
G = [grams(norm(f[3])) for f in frases]
grupos, visto = [], set()
for i in range(len(frases)):
    if i in visto or len(G[i]) < 2:
        continue
    g = [i]
    for j in range(i + 1, len(frases)):
        if len(G[j]) >= 2 and len(G[i] & G[j]) / min(len(G[i]), len(G[j])) >= 0.5:
            g.append(j); visto.add(j)
    if len(g) > 1:
        grupos.append(g)
for c in chunks:
    c["repete_em"] = sorted({frases[j][0] for g in grupos for i in g if frases[i][0] == c["id"]
                             for j in g if frases[j][0] != c["id"]})

json.dump(chunks, open(f"{OUT}/chunks.json", "w"), ensure_ascii=False, indent=1)
with open(f"{OUT}/chunks.txt", "w") as f:
    f.write("TRECHOS DE FALA (id = parte.trecho, tempos da fonte)\n")
    for c in chunks:
        mark = ("   ≈ repete em " + ", ".join(c["repete_em"])) if c["repete_em"] else ""
        f.write(f"{c['id']} [{c['ini']:7.2f}-{c['fim']:7.2f}] {c['texto'] or '(sem fala)'}{mark}\n")
    f.write("\nFRASES REPETIDAS (escolher a melhor tomada de cada grupo)\n")
    for n, g in enumerate(grupos, 1):
        f.write(f"grupo {n}:\n")
        for i in g:
            cid, a_, b_, t = frases[i]
            f.write(f"   {cid} [{a_:7.2f}-{b_:7.2f}] {t}\n")
print(open(f"{OUT}/chunks.txt").read())
