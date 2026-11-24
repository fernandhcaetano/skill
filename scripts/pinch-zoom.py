"""Trend "Pinch & Zoom": texto minúsculo surge entre os dedos na pinça e cresce em degraus nas batidas até o centro.
Uso: python3 -I scripts/pinch-zoom.py <video> <audio> <saida.mp4>
Ajuste OFFSET (sincronia áudio x vídeo), KEYS e PULSES (tempos do vídeo bruto; posições em 1080x1920)."""
import math, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC, AUDIO, OUT = sys.argv[1:4]
AUDIO_START = 0.45
OFFSET = 6.49                     # tempo do vídeo bruto = tempo do áudio + OFFSET
START, END = AUDIO_START + OFFSET, 10.74 + OFFSET
def b(t): return t + OFFSET       # batida do áudio -> tempo do vídeo bruto
FPS, W, H = 30, 1080, 1920
F = "public/fonts/playfair-display-latin-"
LINES = [("A nossa", F + "600-italic.woff", 0.62), ("Black Friday", F + "800-normal.woff", 1.0),
         ("começa amanhã", F + "600-italic.woff", 0.62)]
# (t, cx, cy, largura, easing do trecho que TERMINA aqui). Cada degrau de zoom aterrissa numa batida forte:
# pinça fecha 10.40 -> batida 3.98 | mão abre -> 4.56 | re-pinça e abre -> 5.14 e 5.67 (centro, tamanho final)
KEYS = [(10.40, 345, 928, 40, None), (b(3.98), 325, 915, 78, "back"),
        (b(4.56) - 0.18, 305, 905, 82, "out"), (b(4.56), 340, 890, 330, "back"),
        (b(5.14) - 0.18, 300, 860, 320, "out"), (b(5.14), 420, 910, 580, "back"),
        (b(5.67) - 0.18, 430, 915, 590, "out"), (b(5.67), 540, 960, 940, "back")]
PULSES = [b(t) for t in (6.29, 6.88, 7.46, 8.03, 8.62, 9.28, 10.03)]  # batidas depois do texto pousar

def render_text():
    base, pad = 300, 90
    fonts = [ImageFont.truetype(f, int(base * s)) for _, f, s in LINES]
    boxes = [f.getbbox(t) for (t, _, _), f in zip(LINES, fonts)]
    asc = [f.getmetrics()[0] for f in fonts]
    gaps = [int(base * 0.06), int(base * 0.10)]
    ws = [b[2] - b[0] for b in boxes]; hs = [b[3] - b[1] for b in boxes]
    tw, th = max(ws) + 2 * pad, sum(hs) + sum(gaps) + 2 * pad
    fill = Image.new("RGBA", (tw, th)); d = ImageDraw.Draw(fill); y = pad
    for i, ((t, _, _), f, b, w, h) in enumerate(zip(LINES, fonts, boxes, ws, hs)):
        d.text(((tw - w) / 2 - b[0], y - b[1]), t, font=f, fill="white")
        y += h + (gaps[i] if i < len(gaps) else 0)
    a = fill.getchannel("A"); out = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    for blur, k in ((45, 0.55), (12, 0.45)):  # sombra suave para ler sobre fundo claro (sem contorno)
        s = Image.new("RGBA", (tw, th), (0, 0, 0, 0)); s.putalpha(a.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: v * k))
        out = Image.alpha_composite(out, s)
    return Image.alpha_composite(out, fill)

def ease(x): return 1 - (1 - x) ** 3
def ease_back(x, s=1.3): x -= 1; return x * x * ((s + 1) * x + s) + 1

def state(t):
    if t < KEYS[0][0]: return None
    for a, c in zip(KEYS, KEYS[1:]):
        if t <= c[0]:
            k = (t - a[0]) / (c[0] - a[0]); e = ease_back(k) if c[4] == "back" else ease(k)
            return [a[j] + (c[j] - a[j]) * e for j in (1, 2, 3)], min(1, (t - KEYS[0][0]) / 0.08)
    cx, cy, w = KEYS[-1][1:4]
    pulse = sum(0.035 * math.exp(-(t - p) / 0.12) for p in PULSES if t >= p)
    return [cx, cy, w * (1 + pulse)], 1

txt = render_text(); dur = END - START
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-ss", str(START), "-t", f"{dur:.3f}", "-i", SRC,
    "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-ss", str(AUDIO_START), "-t", f"{dur:.3f}", "-i", AUDIO,
    "-filter_complex", f"[0:v]scale={W}:{H}:flags=lanczos,fps={FPS},setsar=1[v];[v][1:v]overlay=format=auto,format=yuv420p[o];"
                       f"[2:a]afade=t=in:d=0.05,afade=t=out:st={dur-0.35:.3f}:d=0.35[a]",
    "-map", "[o]", "-map", "[a]", "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for n in range(round(dur * FPS)):
    frame = Image.new("RGBA", (W, H)); st = state(START + n / FPS)
    if st:
        (cx, cy, w), op = st
        h = max(1, round(txt.height * w / txt.width)); im = txt.resize((max(1, round(w)), h), Image.LANCZOS)
        if op < 1: im.putalpha(im.getchannel("A").point(lambda v: v * op))
        frame.paste(im, (round(cx - im.width / 2), round(cy - h / 2)), im)
    ff.stdin.write(frame.tobytes())
ff.stdin.close(); sys.exit(ff.wait())
