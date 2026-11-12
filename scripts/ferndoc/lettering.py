"""Lettering do Estilo ferndoc -> frames RGBA crus em stdout (1080x1920, 30 fps).

Uso: python3 -I scripts/ferndoc/lettering.py lettering.json DURACAO | ffmpeg ... -f rawvideo -pix_fmt rgba ...

lettering.json (tempos no vídeo FINAL; use raw/ferndoc/palavras_final.json):
[
  {"ate": 4.8, "y": 175, "linhas": [            # gancho: só aqui entra a letra grande
     [["você", 0.0], ["sabia", 0.4], ["que", 0.7], ["tem", 0.9]],
     [["DRIVE-THRU", 1.3, "G"]],
     [["DE SUSHI", 1.9, "G"]],
     [["no", 2.2], ["rio", 2.4], ["de", 2.6], ["janeiro?", 2.8]]]},
  {"ate": 9.9, "y": 260, "linhas": [[["logo", 7.2], ["depois", 7.4], ["do", 7.7], ["pedágio", 7.9]]]}
]
Palavra = [texto, entra_em] ou [texto, entra_em, "G"] (grande; "G88" = grande com 88 px) ou [texto, entra_em, "D"] (digitado letra a letra,
2 frames por letra, sem pop — combine com o som de teclado). Cada palavra entra com um pop curto e todas
saem juntas em "ate". Regras do estilo: tudo branco, sombra suave, sem caixa de fundo.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(ROOT, "fonts")
items, DUR = json.load(open(sys.argv[1])), float(sys.argv[2])
FPS, W, H, SS = 30, 1080, 1920, 2
COR = tuple(int(x) for x in os.environ.get("FERNDOC_COR_TEXTO", "255,255,255").split(",")) + (255,)
PEQ = ImageFont.truetype(f"{FONTS}/BricolageGrotesque-500.ttf", 54)
GRD = ImageFont.truetype(f"{FONTS}/ArchivoBlack-Regular.ttf", 112)

layout = []
for it in items:
    y = it["y"]
    for linha in it["linhas"]:
        mk = linha[0][2] if len(linha[0]) > 2 else ""
        if mk.startswith("A"):   # "A120" = Anton condensada com contorno preto, ESTÁTICA (gancho estilo TikTok, 11/11)
            f = ImageFont.truetype(f"{FONTS}/Anton-Regular.ttf", int(mk[1:]))
            w0 = f.getlength(linha[0][0])
            layout.append((linha[0][1], it["ate"], (W - w0) / 2, y, linha[0][0], f, "A"))
            a, d = f.getmetrics(); y += a + d - 18
            continue
        # "G" = letra grande padrão (112 px); "G88" = grande com tamanho próprio (títulos longos)
        if mk.startswith("C") and mk[1:].isdigit():   # "C130" = Classic do TikTok (TikTok Sans Bold) grande, com pop
            f = ImageFont.truetype(f"{FONTS}/TikTokSans-Bold.ttf", int(mk[1:]))
        else:
            f = (ImageFont.truetype(GRD.path, int(mk[1:])) if mk[1:].isdigit() else GRD) if mk.startswith("G") else PEQ
        dig = [len(p) > 2 and p[2] == "D" for p in linha]
        big = f is not PEQ
        sp = 22 if big else 14
        ws = [f.getlength(p[0]) for p in linha]
        x = (W - (sum(ws) + sp * (len(linha) - 1))) / 2
        for p, wd, dg in zip(linha, ws, dig):
            layout.append((p[1], it["ate"], x, y, p[0], f, dg))
            x += wd + sp
        a, d = f.getmetrics()
        y += (a + d - 8) if big else (a + d + 6)

_c = {}


def img(w, f):
    if (w, id(f)) not in _c and "Anton" in f.path:
        f2 = ImageFont.truetype(f.path, f.size * SS); a, d = f2.getmetrics(); pad = 24 * SS
        im = Image.new("RGBA", (int(f2.getlength(w)) + pad * 2, a + d + pad * 2), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((pad, pad), w, font=f2, fill=(255, 255, 255, 255), stroke_width=max(2, f.size // 18) * SS,
                                stroke_fill=(0, 0, 0, 255))
        _c[(w, id(f))] = (im.resize((im.width // SS, im.height // SS), Image.LANCZOS), pad // SS)
    if (w, id(f)) not in _c:
        f2 = ImageFont.truetype(f.path, f.size * SS); a, d = f2.getmetrics(); pad = 20 * SS
        im = Image.new("RGBA", (int(f2.getlength(w)) + pad * 2, a + d + pad * 2), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((pad, pad), w, font=f2, fill=COR)
        sh = Image.merge("RGBA", [Image.new("L", im.size, 0)] * 3 + [im.getchannel("A").point(lambda v: int(v * .6))])
        sh = sh.filter(ImageFilter.GaussianBlur(6 * SS))
        o = Image.new("RGBA", im.size, (0, 0, 0, 0)); o.alpha_composite(sh, (0, 4 * SS)); o.alpha_composite(im)
        _c[(w, id(f))] = (o.resize((o.width // SS, o.height // SS), Image.LANCZOS), pad // SS)
    return _c[(w, id(f))]


def ease(x, s=1.9):
    x -= 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


ANIM, cache, out = 0.18, {}, sys.stdout.buffer
for fi in range(int(round(DUR * FPS))):
    t = fi / FPS
    vis = tuple((i, 1 if L[6] == "A" else round(min(1, (t - L[0]) / ANIM), 3) if not L[6] else min(len(L[4]), int((t - L[0]) * FPS / 2) + 1))
                for i, L in enumerate(layout) if L[0] <= t < L[1])
    if vis not in cache:
        fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for i, p in vis:
            t0, _, x, y, w, f, dg = layout[i]
            if dg == "A":  # estático, sem animação
                im, pad = img(w, f); fr.alpha_composite(im, (int(x - pad), int(y - pad))); continue
            if dg:  # digitação: mostra o prefixo, alinhado à esquerda
                n = min(len(w), int((t - t0) * FPS / 2) + 1)
                im, pad = img(w[:n], f)
                fr.alpha_composite(im, (int(x - pad), int(y - pad)))
                continue
            im, pad = img(w, f); fw, fh = im.size
            if p < 1:
                sc = max(.05, .75 + .25 * ease(p))
                im = im.resize((max(1, int(fw * sc)), max(1, int(fh * sc))), Image.BICUBIC)
                im.putalpha(im.getchannel("A").point(lambda v: int(v * min(1, p * 2.5))))
            cx, cy = x - pad + fw / 2, y - pad + fh / 2
            fr.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
        if len(cache) > 300:
            cache.clear()
        cache[vis] = fr.tobytes()
    out.write(cache[vis])
