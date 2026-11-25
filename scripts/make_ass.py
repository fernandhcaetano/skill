# Gera legenda pequena (.ass) a partir do JSON do whisper e de uma lista de frases (n_palavras, texto).
# Tokens "-" (troca de falante) são ignorados. Tempos deslocados por -TRIM.
# Uso: python3 -I scripts/make_ass.py raw/x.json frases.txt saida.ass TRIM [FIM]
import json, sys
src, frases, dst, trim = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
fim = float(sys.argv[5]) if len(sys.argv) > 5 else 1e9
P = []
for l in open(frases, encoding='utf-8'):
    l = l.rstrip('\n')
    if l.strip():
        n, t = l.split('|', 1); P.append((int(n), t.strip()))
W = []
for s in json.load(open(src))['transcription']:
    t = s['text'].strip()
    if t and t != '-':
        W.append((t, s['offsets']['from'] / 1000, s['offsets']['to'] / 1000))
i = 0; B = []
for n, p in P:
    ws = W[i:i + n]; i += n
    print(f"{' '.join(w[0] for w in ws):55s} | {p}")
    B.append([p, ws[0][1], ws[-1][2]])
assert i == len(W), f"usou {i} de {len(W)} palavras"
def ts(x): x = max(0, x); return f"0:{int(x // 60):02d}:{x % 60:05.2f}"
hdr = open('raw/legendas.ass').read().split('[Events]')[0]
o = open(dst, 'w'); o.write(hdr + "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
for k, (p, a, e) in enumerate(B):
    e += 0.25
    if k + 1 < len(B) and B[k + 1][1] - e < 0.6: e = B[k + 1][1]
    e = min(e, fim)
    o.write(f"Dialogue: 0,{ts(a - trim)},{ts(e - trim)},Leg,,0,0,0,,{p}\n")
