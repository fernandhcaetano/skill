"""Painel de cores sobre fundo simulado (parede marrom + cortina preta).
uso: python3 colorboard.py <saida.jpg> <titulo> nome=#hex ... (grupos separados por '|')"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = "/tmp/claude-0/-home-user-skill/2f4d99df-1e46-5286-b2d1-43781193319c/scratchpad"; F = S + "/font"
W, H = 1080, 1920
out, title, args = sys.argv[1], sys.argv[2], sys.argv[3:]

rng = np.random.default_rng(1)
x = np.arange(W)[None, :]; y = np.arange(H)[:, None]
wall = np.array([94, 62, 42], float)[None, None, :] * (0.9 + 0.12 * np.exp(-((x - 300) ** 2 + (y - 700) ** 2) / 6e5))[..., None]
wall = wall + rng.normal(0, 3, (H, W, 1))
cur = np.repeat(((10 + 9 * (0.5 + 0.5 * np.sin(x / 38.0 + np.sin(x / 90.0) * 2))) * np.ones((H, 1)))[..., None], 3, 2)
bg = np.where((x > 560 + 20 * np.sin(y / 200.0))[..., None], cur, wall)
base = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
sil = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(sil)
d.ellipse([400, 620, 680, 960], fill=(150, 110, 90, 255)); d.rounded_rectangle([230, 980, 850, 1920], radius=200, fill=(30, 30, 35, 255))
base.alpha_composite(sil)

BIG = ImageFont.truetype(F + "/ArchivoBlack.ttf", 112); SM = ImageFont.truetype(F + "/Bricolage5.ttf", 54)
LAB = ImageFont.truetype(F + "/Bricolage5.ttf", 64); HEAD = ImageFont.truetype(F + "/Bricolage5.ttf", 40)


def center(dr, yy, parts):
    xx = (W - sum(f.getlength(t) for t, f, c in parts)) / 2
    for t, f, c in parts:
        dr.text((xx, yy), t, font=f, fill=c); xx += f.getlength(t)


def tile(name, c):
    im = base.copy(); L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(L)
    center(dr, 170, [("você sabia que tem", SM, "#FFFFFF")])
    center(dr, 245, [("DRIVE-THRU", BIG, c)]); center(dr, 395, [("DE SUSHI", BIG, c)])
    center(dr, 545, [("no rio de janeiro?", SM, "#FFFFFF")])
    center(dr, 1180, [("na ", SM, "#FFFFFF"), ("linha amarela", SM, c)])
    sh = Image.merge("RGBA", [Image.new("L", (W, H), 0)] * 3 + [L.getchannel("A").point(lambda v: int(v * .55))]).filter(ImageFilter.GaussianBlur(6))
    im.alpha_composite(sh, (0, 4)); im.alpha_composite(L)
    dd = ImageDraw.Draw(im); dd.rectangle([0, H - 150, W, H], fill=(18, 18, 18, 255)); dd.text((40, H - 126), f"{name}  {c}", font=LAB, fill=c)
    return im.convert("RGB").resize((270, 480))


groups, cur_g = [], None
for a in args:
    if a.startswith("#group:"):
        cur_g = [a[7:], []]; groups.append(cur_g)
    else:
        n, c = a.split("="); cur_g[1].append((n, c))
cols = max(len(g[1]) for g in groups)
TW, TH, GAP, HH = 270, 480, 10, 56
sheet = Image.new("RGB", (cols * (TW + GAP) + 30, 70 + len(groups) * (TH + HH + GAP)), "#f4f2ee")
ds = ImageDraw.Draw(sheet); ds.text((20, 14), title, font=HEAD, fill="#222")
yy = 70
for gname, items in groups:
    ds.text((20, yy + 8), gname, font=HEAD, fill="#444"); yy += HH
    for i, (n, c) in enumerate(items):
        sheet.paste(tile(n, c), (20 + i * (TW + GAP), yy))
    yy += TH + GAP
sheet.save(out, quality=90)
