"""Lettering 'Estilo ferndoc' v1 -> RGBA cru em stdout (1080x1920, 30 fps)."""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FD, DUR, FPS = sys.argv[1], float(sys.argv[2]), 30
W, H = 1080, 1920
MUST, WHITE = (227, 168, 28, 255), (255, 255, 255, 255)
SMALL = ImageFont.truetype(FD + "/tts500.ttf", 52)
BIG = ImageFont.truetype(FD + "/Anton.ttf", 150)

# Cada item: (t_out, y_topo, [linhas]); linha = [(palavra, t_in, fonte, cor)]
def s(w, t, c=WHITE): return (w, t, SMALL, c)
def b(w, t): return (w, t, BIG, MUST)

ITEMS = [
    (6.25, 175, [[s("você", 0.0), s("sabia", 0.46), s("que", 0.78), s("tem", 1.08)],
                 [b("DRIVE-THRU", 1.32)],
                 [b("DE SUSHI", 1.95)],
                 [s("no", 2.24), s("rio", 2.5), s("de", 2.7), s("janeiro?", 2.8)]]),
    (6.25, 1440, [[s("na", 4.45), s("linha", 4.6, MUST), s("amarela", 4.64, MUST)]]),
    (9.93, 260, [[s("logo", 7.2), s("depois", 7.44), s("do", 7.74), s("pedágio", 7.92)],
                 [s("sentido", 8.66), s("barra", 8.98, MUST)]]),
    (12.0, 260, [[s("muito", 10.34), s("rápido", 10.7, MUST)],
                 [s("super", 11.52), s("fresco", 11.96, MUST)]]),
    (13.87, 260, [[s("e", 12.96), s("muito", 13.04), s("bom!", 13.4, MUST)]]),
    (16.5, 230, [[s("uramaki", 14.36, MUST), s("+", 15.1), s("hot", 15.44, MUST), s("filadélfia", 15.58, MUST)]]),
    (19.75, 230, [[s("tem", 17.2), s("tutorial", 17.5), s("na", 17.7), s("embalagem", 17.78)]]),
    (21.3, 230, [[s("(fiz", 19.82), s("errado)", 19.94, MUST)]]),
    (25.2, 230, [[s("experiência", 23.96), s("única", 24.26, MUST)]]),
    (27.3, 200, [[b("TAVA MUITO", 26.6)], [b("BOM", 26.95)]]),
    (36.0, 230, [[s("nem", 34.6), s("esperei", 34.68), s("chegar", 34.98), s("em", 35.16), s("casa", 35.32, MUST)]]),
    (47.5, 230, [[s("valores", 45.72, MUST), s("no", 45.9), s("começo", 46.0), s("do", 46.1), s("vídeo", 46.2)]]),
    (52.6, 200, [[b("VALE A", 49.74)], [b("PENA", 49.98)]]),
]

SP_SMALL, SP_BIG = 14, 22
layout = []  # (t_in, t_out, x, y, palavra, fonte, cor)
for t_out, y, lines in ITEMS:
    for line in lines:
        f = line[0][2]
        sp = SP_BIG if f is BIG else SP_SMALL
        ws = [f.getlength(w) for w, *_ in line]
        x = (W - (sum(ws) + sp * (len(line) - 1))) / 2
        for (w, t, ff, c), wd in zip(line, ws):
            layout.append((t, t_out, x, y, w, ff, c, wd))
            x += wd + sp
        a, d = f.getmetrics()
        y += (a + d - 22) if f is BIG else (a + d + 4)

SS = 2
_cache = {}
def word_img(w, f, c):
    k = (w, id(f), c)
    if k not in _cache:
        f2 = ImageFont.truetype(f.path, f.size * SS)
        a, d = f2.getmetrics()
        pad = 20 * SS
        im = Image.new("RGBA", (int(f2.getlength(w)) + pad * 2, a + d + pad * 2), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((pad, pad), w, font=f2, fill=c)
        sh = Image.merge("RGBA", [Image.new("L", im.size, 0)] * 3 +
                         [im.getchannel("A").point(lambda v: int(v * .55))]).filter(ImageFilter.GaussianBlur(6 * SS))
        out = Image.new("RGBA", im.size, (0, 0, 0, 0))
        out.alpha_composite(sh, (0, 4 * SS)); out.alpha_composite(im)
        _cache[k] = (out.resize((out.width // SS, out.height // SS), Image.LANCZOS), pad // SS)
    return _cache[k]

def ease(x, s=1.9):
    x -= 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2

ANIM = 0.18
frame_cache = {}
out = sys.stdout.buffer
for fi in range(int(round(DUR * FPS))):
    t = fi / FPS
    vis = [(i, min(1, (t - L[0]) / ANIM)) for i, L in enumerate(layout) if L[0] <= t < L[1]]
    key = tuple((i, round(p, 3)) for i, p in vis)
    if key not in frame_cache:
        fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for i, p in vis:
            t0, t1, x, y, w, f, c, wd = layout[i]
            img, pad = word_img(w, f, c)
            fw, fh = img.size
            if p < 1:
                sc = max(.05, .75 + .25 * ease(p))
                img = img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.BICUBIC)
                img.putalpha(img.getchannel("A").point(lambda v: int(v * min(1, p * 2.5))))
            cx, cy = x - pad + fw / 2, y - pad + fh / 2
            fr.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))
        if len(frame_cache) > 400: frame_cache.clear()
        frame_cache[key] = fr.tobytes()
    out.write(frame_cache[key])
