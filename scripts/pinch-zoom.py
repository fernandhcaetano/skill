"""Trend "Pinch & Zoom": texto no centro que nasce minúsculo e cresce em degraus, cada degrau NA batida,
com os momentos-chave do vídeo encaixados nas batidas por speed ramps (MAP).
Uso: python3 -I scripts/pinch-zoom.py <video> <audio> <saida.mp4>
Tempos: v = vídeo bruto, a = áudio da trend."""
import math, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC, AUDIO, OUT = sys.argv[1:4]
FPS, W, H, CX, CY = 30, 1080, 1920, 540, 960
A0, A1 = 0.45, 10.74                     # trecho do áudio usado (depois fica em silêncio)
# Mapa vídeo bruto (v) -> tempo da música (a). Entre âncoras o vídeo roda em velocidade constante,
# então cada momento-chave cai numa batida (grade de 0,58 s: ..., 4.56, 5.14, 5.67, 6.29, 6.88, 7.46, ...).
MAP = [(6.59, 0.45),
       (10.70, 4.56),   # 1ª abertura da mão  -> batida forte do rufo
       (11.72, 5.67),   # 2ª abertura         -> pancada mais forte (0,92x entre as duas)
       (12.70, 6.65),   # mão desce (normal)
       (14.20, 7.46),   # recua e o microfone chega no peito ~1,85x -> batida
       (16.65, 9.78),   # reação feliz com o microfone, velocidade ~normal; aceno -> batida
       (17.25, 10.38),  # normal
       (20.70, 13.83)]  # sai andando e escritório vazio, normal (a partir de 10,74 a música é sua)
def a2v(a):
    for (va, aa), (vb, ab) in zip(MAP, MAP[1:]):
        if a <= ab: return va + (a - aa) * (vb - va) / (ab - aa)
    return MAP[-1][0]
# Degraus do texto (largura em px) — cada um começa exatamente na batida
W_START = 80                             # texto pequenininho no centro desde o primeiro quadro
STEPS = [(3.98, 110), (4.56, 380), (5.67, 940)]  # rufo/drop | 1ª abertura | 2ª abertura (tamanho final)
HOLD = 4.0                               # segundos extras no fim: último quadro congelado, texto pulsando
PULSES = [5.67 + 0.578 * k for k in range(1, 22)]  # batidas seguintes (grade da música): pulsadinha leve
F = "public/fonts/playfair-display-latin-"
LINES = [("A nossa", F + "600-italic.woff", 0.62), ("Black Friday", F + "800-normal.woff", 1.0),
         ("começa amanhã", F + "600-italic.woff", 0.62)]

def render_text():
    base, pad = 300, 90
    fonts = [ImageFont.truetype(f, int(base * s)) for _, f, s in LINES]
    boxes = [f.getbbox(t) for (t, _, _), f in zip(LINES, fonts)]
    gaps = [int(base * 0.06), int(base * 0.10)]
    ws = [b[2] - b[0] for b in boxes]; hs = [b[3] - b[1] for b in boxes]
    tw, th = max(ws) + 2 * pad, sum(hs) + sum(gaps) + 2 * pad
    fill = Image.new("RGBA", (tw, th)); d = ImageDraw.Draw(fill); y = pad
    for i, ((t, _, _), f, b, w, h) in enumerate(zip(LINES, fonts, boxes, ws, hs)):
        d.text(((tw - w) / 2 - b[0], y - b[1]), t, font=f, fill="white")
        y += h + (gaps[i] if i < len(gaps) else 0)
    a = fill.getchannel("A"); out = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    for blur, k in ((45, 0.55), (12, 0.45)):  # sombra suave (sem contorno)
        s = Image.new("RGBA", (tw, th), (0, 0, 0, 0)); s.putalpha(a.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: v * k))
        out = Image.alpha_composite(out, s)
    return Image.alpha_composite(out, fill)

def ease_back(x, s=1.6): x -= 1; return x * x * ((s + 1) * x + s) + 1
SNAP = 0.12                               # duração do "pulo" de cada degrau

def width(a):
    w = W_START
    for t, target in STEPS:
        if a >= t: w = w + (target - w) * ease_back(min(1, (a - t) / SNAP)) if a - t < SNAP else target
    if a >= STEPS[-1][0] + SNAP:
        w *= 1 + sum(0.03 * math.exp(-(a - p) / 0.12) for p in PULSES if a >= p)
    return w

txt = render_text()
dur = A1 - A0; total = MAP[-1][1] - A0 + HOLD
segs = "".join(f"[s{i}]trim={va}:{vb},setpts=(PTS-STARTPTS)*{(ab - aa) / (vb - va):.5f}[t{i}];"
               for i, ((va, aa), (vb, ab)) in enumerate(zip(MAP, MAP[1:])))
k = len(MAP) - 1
vf = (f"[0:v]scale={W}:{H}:flags=lanczos,setsar=1,split={k}" + "".join(f"[s{i}]" for i in range(k)) + ";" + segs +
      "".join(f"[t{i}]" for i in range(k)) + f"concat=n={k}:v=1:a=0,fps={FPS},tpad=stop_mode=clone:stop_duration={HOLD}[v];"
      f"[v][1:v]overlay=format=auto,format=yuv420p[o];"
      f"[2:a]afade=t=in:d=0.05,afade=t=out:st={dur-0.35:.3f}:d=0.35,apad[au]")
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-i", SRC,
    "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-ss", str(A0), "-t", f"{dur:.3f}", "-i", AUDIO, "-filter_complex", vf,
    "-map", "[o]", "-map", "[au]", "-t", f"{total:.3f}", "-c:v", "libx264", "-crf", "17", "-preset", "slow",
    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for n in range(round(total * FPS)):
    frame = Image.new("RGBA", (W, H)); w = width(A0 + n / FPS)
    if w:
        h = max(1, round(txt.height * w / txt.width)); im = txt.resize((max(1, round(w)), h), Image.LANCZOS)
        frame.paste(im, (round(CX - im.width / 2), round(CY - h / 2)), im)
    ff.stdin.write(frame.tobytes())
ff.stdin.close(); sys.exit(ff.wait())
