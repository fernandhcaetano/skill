"""Trend "Pinch & Zoom": texto minúsculo surge entre os dedos e cresce quando a mão abre.
Uso: python3 -I scripts/pinch-zoom.py <video> <saida.mp4>
Ajuste START/END e os KEYS (tempo absoluto do vídeo bruto, centro x/y e largura do texto em 1080x1920)."""
import subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC, OUT = sys.argv[1], sys.argv[2]
START, END, FPS, W, H = 8.0, 18.4, 30, 1080, 1920
LINES = [("A NOSSA", 0.62), ("BLACK FRIDAY", 1.0), ("COMEÇA AMANHÃ", 0.62)]
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
# (t, cx, cy, largura) — pinça fecha 10.38, abre 10.62–11.05, re-pinça 11.35 e abre até 12.20
KEYS = [(10.40, 300, 930, 45), (10.65, 262, 872, 75), (11.07, 340, 890, 300),
        (11.35, 275, 835, 265), (12.20, 540, 960, 980)]

def render_text():
    base = 260
    fonts = [ImageFont.truetype(FONT, int(base * s)) for _, s in LINES]
    boxes = [f.getbbox(t) for (t, _), f in zip(LINES, fonts)]
    ws = [b[2] - b[0] for b in boxes]; hs = [b[3] - b[1] for b in boxes]
    gap, pad = int(base * 0.16), 60
    tw, th = max(ws) + 2 * pad, sum(hs) + gap * (len(LINES) - 1) + 2 * pad
    fill = Image.new("RGBA", (tw, th)); d = ImageDraw.Draw(fill)
    y = pad
    for (t, _), f, b, w, h in zip(LINES, fonts, boxes, ws, hs):
        d.text(((tw - w) / 2 - b[0], y - b[1]), t, font=f, fill="white",
               stroke_width=6, stroke_fill=(0, 0, 0, 255))
        y += h + gap
    a = fill.getchannel("A")
    shadow = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    shadow.putalpha(a.filter(ImageFilter.GaussianBlur(22)).point(lambda v: v * 0.55))
    return Image.alpha_composite(shadow, fill)

def ease(x): return 1 - (1 - x) ** 3
def ease_back(x, s=1.4): x -= 1; return x * x * ((s + 1) * x + s) + 1

def state(t):
    if t < KEYS[0][0]: return None
    for i in range(len(KEYS) - 1):
        a, b = KEYS[i], KEYS[i + 1]
        if t <= b[0]:
            k = (t - a[0]) / (b[0] - a[0]); e = ease_back(k) if i == len(KEYS) - 2 else ease(k)
            return [a[j] + (b[j] - a[j]) * e for j in (1, 2, 3)], min(1, (t - KEYS[0][0]) / 0.1)
    cx, cy, w = KEYS[-1][1:]
    return [cx, cy, w * (1 + 0.012 * __import__("math").sin((t - KEYS[-1][0]) * 3.2))], 1

txt = render_text()
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-ss", str(START), "-t", f"{END-START:.3f}", "-i", SRC,
    "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-f", "lavfi", "-t", f"{END-START:.3f}", "-i", "anullsrc=r=48000:cl=stereo",
    "-filter_complex", f"[0:v]scale={W}:{H}:flags=lanczos,fps={FPS},setsar=1[v];[v][1:v]overlay=format=auto,format=yuv420p[o]",
    "-map", "[o]", "-map", "2:a", "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-c:a", "aac",
    "-movflags", "+faststart", "-shortest", OUT], stdin=subprocess.PIPE)
for n in range(round((END - START) * FPS)):
    frame = Image.new("RGBA", (W, H)); s = state(START + n / FPS)
    if s:
        (cx, cy, w), op = s
        h = max(1, round(txt.height * w / txt.width)); im = txt.resize((max(1, round(w)), h), Image.LANCZOS)
        if op < 1: im.putalpha(im.getchannel("A").point(lambda v: v * op))
        frame.paste(im, (round(cx - im.width / 2), round(cy - h / 2)), im)
    ff.stdin.write(frame.tobytes())
ff.stdin.close(); sys.exit(ff.wait())
