# Gera legendas .ass pequenas (estilo trabalho) a partir do JSON do whisper.cpp.
# Uso: python3 -I scripts/simple-captions.py raw/X.json raw/X.ass TRIM_START FALA_INICIO
import json, sys
src, dst, trim, first = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
FIX = {}
words = []
for seg in json.load(open(src))['transcription']:
    t = seg['text'].strip()
    if not t or t == '-':
        continue
    a, b = seg['offsets']['from'] / 1000, seg['offsets']['to'] / 1000
    words.append([FIX.get(t, t), max(a, first), max(b, first + 0.2)])
blocks, cur = [], []
for i, w in enumerate(words):
    cur.append(w)
    nxt = words[i + 1] if i + 1 < len(words) else None
    end_punct = w[0][-1] in '.?!'
    comma = w[0][-1] == ','
    gap = nxt and nxt[1] - w[2] > 0.3
    if not nxt or (end_punct and len(cur) >= 2) or (comma and len(cur) >= 4) or len(cur) >= 7 or (gap and len(cur) >= 3):
        blocks.append(cur); cur = []
def ts(x):
    x = max(0, x); h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"
out = open(dst, 'w')
out.write("""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Leg,Inter Medium,40,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,2,190,190,420,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")
for k, b in enumerate(blocks):
    a = b[0][1]; e = b[-1][2] + 0.15
    if k + 1 < len(blocks) and blocks[k + 1][0][1] - e < 0.4:
        e = blocks[k + 1][0][1]
    text = ' '.join(w[0] for w in b)
    out.write(f"Dialogue: 0,{ts(a - trim)},{ts(e - trim)},Leg,,0,0,0,,{text}\n")
    print(f"{a - trim:5.2f}-{e - trim:5.2f} {text}")
