# Legenda pequena sincronizada só com a fala:
#  - tempo de início de cada palavra pelo DTW do whisper.cpp (-dtw medium)
#  - cada legenda some nas pausas (> GAP s sem voz) e não aparece antes da voz começar
# Uso: python3 -I scripts/make_ass_dtw.py dtw.json audio16k.wav frases.txt saida.ass [TRIM]
import json, sys, wave, struct, math
src, wav, frases, dst = sys.argv[1:5]
trim = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
GAP, THR, HOP = 0.6, -26.0, 0.05
P = []
for l in open(frases, encoding='utf-8'):
    l = l.rstrip('\n')
    if l.strip():
        n, t = l.split('|', 1); P.append((int(n), t.strip()))
W = []
for s in json.load(open(src))['transcription']:
    t = s['text'].strip()
    if not t or t == '-': continue
    dt = [tk['t_dtw'] / 100 for tk in s['tokens'] if tk.get('t_dtw', -1) >= 0 and not tk['text'].startswith('[_')]
    W.append([t, dt[0] if dt else s['offsets']['from'] / 1000, dt[-1] if dt else s['offsets']['to'] / 1000])
for i in range(1, len(W)):          # tempos monotônicos
    W[i][1] = max(W[i][1], W[i - 1][1])
for i in range(len(W)):
    nxt = W[i + 1][1] if i + 1 < len(W) else W[i][2] + 0.4
    W[i][2] = min(max(W[i][2] + 0.25, W[i][1] + 0.15), nxt)
# voz por energia
w = wave.open(wav); n = w.getnframes(); sr = w.getframerate()
d = struct.unpack('<%dh' % n, w.readframes(n)); hs = int(sr * HOP)
voiced = [20 * math.log10(math.sqrt(sum(x * x for x in d[i:i + hs]) / hs) / 32768 + 1e-9) > THR for i in range(0, n - hs, hs)]
def voice_runs(a, b):
    i0, i1 = max(0, int(a / HOP)), min(len(voiced), int(b / HOP) + 1)
    runs, s, last = [], None, None
    for k in range(i0, i1):
        if voiced[k]:
            if s is None: s = k
            elif last is not None and (k - last) * HOP > GAP:
                runs.append((s * HOP, (last + 1) * HOP)); s = k
            last = k
    if s is not None: runs.append((s * HOP, (last + 1) * HOP))
    return runs
i = 0; ev = []
for n_, p in P:
    ws = W[i:i + n_]; i += n_
    if not p: continue
    a, b = ws[0][1] - 0.15, ws[-1][2] + 0.1
    for ra, rb in (voice_runs(a, b) or [(ws[0][1], ws[-1][2])]):
        ev.append([max(ra - 0.05, 0), rb + 0.15, p])
assert i == len(W), f"usou {i} de {len(W)} palavras"
for k in range(len(ev) - 1):        # sem sobreposição; junta buracos curtos da mesma frase
    if ev[k][1] > ev[k + 1][0]: ev[k][1] = ev[k + 1][0]
    elif ev[k][2] == ev[k + 1][2] and ev[k + 1][0] - ev[k][1] < 0.35: ev[k][1] = ev[k + 1][0]
def ts(x): x = max(0, x - trim); return f"0:{int(x // 60):02d}:{x % 60:05.2f}"
hdr = open('raw/legendas.ass').read().split('[Events]')[0]
o = open(dst, 'w'); o.write(hdr + "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
for a, b, p in ev:
    if b - a >= 0.2: o.write(f"Dialogue: 0,{ts(a)},{ts(b)},Leg,,0,0,0,,{p}\n")
print(len(ev), "legendas")
