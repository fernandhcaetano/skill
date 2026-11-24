# IMG_6949: J-cut na abertura, enquadramentos sem o paredão, painel de marcas rastreado e pintado de preto.
# Uso: python3 -I scripts/render6949.py            -> out/IMG_6949.mp4
#      python3 -I scripts/render6949.py --stills t1 t2 ...  -> quadros de conferência (tempo da fonte)
import cv2, json, subprocess, sys, numpy as np
T0, T1 = 1.50, 34.10
W, H = 2160, 3840
SHOTS = [  # (início, fim, zoom, cx, cy) em tempo da fonte
    (1.50, 6.60, 1.55, 0.47, 0.677),   # Luísa caminhando até o Isaque
    (6.60, 9.50, 1.2, 0.415, 0.585),   # os dois
    (9.50, 10.90, 2.0, 0.75, 0.50),    # Luísa
    (10.90, 11.55, 2.0, 0.36, 0.52),   # Isaque
    (11.55, 16.80, 1.2, 0.415, 0.585),
    (16.80, 20.10, 2.0, 0.70, 0.50),
    (20.10, 26.10, 2.0, 0.36, 0.52),
    (26.10, 30.50, 1.2, 0.415, 0.585),
    (30.50, 34.10, 1.2, 0.415, 0.585),
]
def crop(z, cx, cy):
    w, h = round(W / z / 2) * 2, round(H / z / 2) * 2
    x = min(max(cx * W - w / 2, 0), W - w); y = min(max(cy * H - h / 2, 0), H - h)
    return w, h, int(x) // 2 * 2, int(y) // 2 * 2
# rastreio (1080p, a partir de T0, 30 fps) suavizado
trk = np.array(json.load(open("raw/track6949.json")), float)
k = 5
pad = np.pad(trk[:, :2], ((k // 2, k // 2), (0, 0)), mode="edge")
sm = np.array([np.median(pad[i:i + k], axis=0) for i in range(len(trk))])
POLY = np.array([(704, -40), (806, -40), (760, 1150), (670, 1150)], np.float32)  # ref 1080p, tpl em (700,30)
def paint(img, i):
    t = T0 + i / 30
    if t < 6.0 or i >= len(sm):
        return img
    dx, dy = sm[i, 0] - 700, sm[i, 1] - 30
    poly = ((POLY + [dx, dy]) * 2).astype(np.int32)
    x0, y0 = max(poly[:, 0].min() - 8, 0), max(poly[:, 1].min(), 0)
    x1, y1 = min(poly[:, 0].max() + 8, W), min(poly[:, 1].max() + 8, H)
    roi = img[y0:y1, x0:x1]
    m = np.zeros(roi.shape[:2], np.uint8)
    cv2.fillPoly(m, [poly - [x0, y0]], 255)
    hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
    S_, V_ = hsv[..., 1], hsv[..., 2]
    # letras = claras e sem cor (traços finos); áreas brancas grandes (blusa) e pessoa (cabelo/pele) ficam protegidas
    letters = ((V_ > 85) & (S_ < 90)).astype(np.uint8) * 255
    big = cv2.morphologyEx(letters, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (71, 71)))
    big = cv2.dilate(big, np.ones((15, 15), np.uint8))
    person = cv2.dilate(((S_ >= 90) & (V_ > 70)).astype(np.uint8) * 255, np.ones((11, 11), np.uint8))
    keep = cv2.bitwise_not(cv2.bitwise_or(big, person))
    lm = cv2.bitwise_and(cv2.bitwise_and(letters, m), keep)
    lm = cv2.bitwise_and(cv2.dilate(lm, np.ones((7, 7), np.uint8)), keep)
    if lm.any():
        img[y0:y1, x0:x1] = cv2.inpaint(np.ascontiguousarray(roi), lm, 7, cv2.INPAINT_TELEA)
    return img
tone = ("zscale=w=2160:h=3840:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,"
        "zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=gamma=0.97:saturation=1.05:contrast=1.12,fps=30,format=rgb24")
dec = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(T0), "-to", str(T1), "-i", "raw/IMG_6949.MOV",
                        "-vf", tone, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
FS = W * H * 3
if sys.argv[1:2] == ["--stills"]:
    want = {round((float(t) - T0) * 30): t for t in sys.argv[2:]}
    i = 0
    while want:
        b = dec.stdout.read(FS)
        if len(b) < FS: break
        if i in want:
            img = paint(np.frombuffer(b, np.uint8).reshape(H, W, 3).copy(), i)
            t = T0 + i / 30
            z, cx, cy = next((z, cx, cy) for a, bb, z, cx, cy in SHOTS if a <= t < bb)
            w, h, x, y = crop(z, cx, cy)
            c = cv2.resize(img[y:y + h, x:x + w], (1080, 1920), interpolation=cv2.INTER_AREA)
            cv2.imwrite(sys.argv[0].replace("scripts/render6949.py", "") + f"/tmp/claude-0/-home-user-skill/c520df15-5a48-5ca9-aacf-3fc8385e2099/scratchpad/p49/st_{float(want.pop(i)):06.2f}.png", cv2.cvtColor(c, cv2.COLOR_RGB2BGR))
        i += 1
    dec.kill(); sys.exit()
n = len(SHOTS)
f = [f"[0:v]split={n}" + "".join(f"[s{i}]" for i in range(n))]
for i, (a, b, z, cx, cy) in enumerate(SHOTS):
    w, h, x, y = crop(z, cx, cy)
    f.append(f"[s{i}]trim=start={a - T0:.4f}:end={b - T0:.4f},setpts=PTS-STARTPTS,crop={w}:{h}:{x}:{y},scale=1080:1920:flags=lanczos,setsar=1[v{i}]")
f.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0,format=yuv420p,ass=raw/legendas6949.ass[v]")
# áudio: "Gente, aqui no ao vivo" (0.15–1.50) por cima do começo da caminhada, depois tudo sincronizado a partir de 2.85
f.append("[1:a]atrim=0.15:1.50,asetpts=PTS-STARTPTS[a0];[1:a]atrim=2.85:34.10,asetpts=PTS-STARTPTS[a1];"
         "[a0][a1]concat=n=2:v=0:a=1,afade=t=in:d=0.03,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
enc = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30",
                        "-i", "-", "-i", "raw/IMG_6949.MOV", "-filter_complex", ";".join(f), "-map", "[v]", "-map", "[a]",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                        "out/IMG_6949.mp4"], stdin=subprocess.PIPE)
i = 0
while True:
    b = dec.stdout.read(FS)
    if len(b) < FS: break
    enc.stdin.write(paint(np.frombuffer(b, np.uint8).reshape(H, W, 3).copy(), i).tobytes()); i += 1
enc.stdin.close(); enc.wait(); print(i, "quadros")
