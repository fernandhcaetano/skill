"""Trend "Pinch & Zoom": texto minúsculo surge no centro na hora da pinça e cresce quando a mão abre.
Uso: python3 -I scripts/pinch-zoom.py <video> <audio> <saida.mp4>
Ajuste START/END/AUDIO_START e KEYS (tempo absoluto do vídeo bruto -> largura do texto em px, 1080x1920)."""
import math, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC, AUDIO, OUT = sys.argv[1:4]
START, END, AUDIO_START = 7.08, 17.33, 0.5   # pinça (10.40) cai no rufo da música (3.82 no áudio)
FPS, W, H, CX, CY = 30, 1080, 1920, 540, 960
F = "public/fonts/playfair-display-latin-"
LINES = [("A nossa", F + "600-italic.woff", 0.62), ("Black Friday", F + "800-normal.woff", 1.0),
         ("começa amanhã", F + "600-italic.woff", 0.62)]
# (t, largura) — pinça fecha 10.40, abre 10.65–11.05, re-pinça 11.35 e abre até 12.20
KEYS = [(10.40, 40), (10.65, 70), (11.05, 330), (11.35, 300), (12.20, 940)]

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

def width(t):
    if t < KEYS[0][0]: return None
    for i in range(len(KEYS) - 1):
        (ta, wa), (tb, wb) = KEYS[i], KEYS[i + 1]
        if t <= tb:
            k = (t - ta) / (tb - ta); return wa + (wb - wa) * (ease_back(k) if i == len(KEYS) - 2 else ease(k))
    return KEYS[-1][1] * (1 + 0.012 * math.sin((t - KEYS[-1][0]) * 3.2))

txt = render_text(); dur = END - START
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-ss", str(START), "-t", f"{dur:.3f}", "-i", SRC,
    "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-ss", str(AUDIO_START), "-t", f"{dur:.3f}", "-i", AUDIO,
    "-filter_complex", f"[0:v]scale={W}:{H}:flags=lanczos,fps={FPS},setsar=1[v];[v][1:v]overlay=format=auto,format=yuv420p[o];"
                       f"[2:a]afade=t=in:d=0.05,afade=t=out:st={dur-0.35:.3f}:d=0.35[a]",
    "-map", "[o]", "-map", "[a]", "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for n in range(round(dur * FPS)):
    frame = Image.new("RGBA", (W, H)); w = width(START + n / FPS)
    if w:
        h = max(1, round(txt.height * w / txt.width)); im = txt.resize((max(1, round(w)), h), Image.LANCZOS)
        frame.paste(im, (round(CX - im.width / 2), round(CY - h / 2)), im)
    ff.stdin.write(frame.tobytes())
ff.stdin.close(); sys.exit(ff.wait())
