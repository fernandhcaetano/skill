"""Trend "Pinch & Zoom": texto no centro que nasce minúsculo e cresce em degraus, cada degrau NA batida,
com as aberturas de mão do vídeo encaixadas nas batidas (micro câmera lenta entre elas).
Uso: python3 -I scripts/pinch-zoom.py <video> <audio> <saida.mp4>
Tempos: v = vídeo bruto, a = áudio da trend."""
import math, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC, AUDIO, OUT = sys.argv[1:4]
FPS, W, H, CX, CY = 30, 1080, 1920, 540, 960
A0, A1 = 0.45, 10.74                     # trecho do áudio usado
V_END = 20.70                            # vídeo segue até o fim (depois do áudio fica em silêncio)
# Encaixe vídeo x áudio: mão abre (v) -> batida (a). Entre as duas aberturas o vídeo roda um pouco mais lento.
SYNC = [(10.70, 4.56), (11.72, 5.67)]
(V1, B1), (V2, B2) = SYNC
def a2v(a):
    if a <= B1: return V1 + (a - B1)
    if a <= B2: return V1 + (a - B1) * (V2 - V1) / (B2 - B1)
    return V2 + (a - B2)
# Degraus do texto (largura em px) — cada um começa exatamente na batida
STEPS = [(3.98, 70), (4.56, 380), (5.67, 940)]   # rufo/drop: aparece | 1ª abertura | 2ª abertura (tamanho final)
PULSES = [6.29, 6.88, 7.46, 8.03, 8.62, 9.20, 9.78, 10.36]  # batidas seguintes: pulsadinha leve
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
    if a < STEPS[0][0]: return None
    w = 0
    for t, target in STEPS:
        if a >= t: w = w + (target - w) * ease_back(min(1, (a - t) / SNAP)) if a - t < SNAP else target
    if a >= STEPS[-1][0] + SNAP:
        w *= 1 + sum(0.03 * math.exp(-(a - p) / 0.12) for p in PULSES if a >= p)
    return w

txt = render_text()
s0, s1, s2, s3 = a2v(A0), V1, V2, V_END
dur = A1 - A0; total = dur + (V_END - a2v(A1))
slow = (B2 - B1) / (V2 - V1)
vf = (f"[0:v]scale={W}:{H}:flags=lanczos,setsar=1,split=3[x][y][z];"
      f"[x]trim={s0}:{s1},setpts=PTS-STARTPTS[p];[y]trim={s1}:{s2},setpts=(PTS-STARTPTS)*{slow:.5f}[q];"
      f"[z]trim={s2}:{s3},setpts=PTS-STARTPTS[r];[p][q][r]concat=n=3:v=1:a=0,fps={FPS}[v];"
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
