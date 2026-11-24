"""Apaga um logo claro (ex.: adidas na mochila do fundo) rastreando-o quadro a quadro e preenchendo com inpaint.
Uso: python3 -I scripts/remove-logo.py <entrada.mp4> <saida.mp4> <ref_t> <x0> <y0> <x1> <y1>
ref_t = tempo (s) de um quadro onde o logo aparece limpo; x0..y1 = caixa do logo nesse quadro (1080x1920)."""
import subprocess, sys
import cv2, numpy as np
SRC, OUT = sys.argv[1], sys.argv[2]
REF_T = float(sys.argv[3]); X0, Y0, X1, Y1 = map(int, sys.argv[4:8])
W, H, FPS, PAD, SEARCH, THR = 1080, 1920, 30, 8, 70, 0.55

def frames(path):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    while (b := p.stdout.read(W * H * 3)) and len(b) == W * H * 3:
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()

ref = next(f for i, f in enumerate(frames(SRC)) if i == round(REF_T * FPS))
tpl = cv2.cvtColor(ref[Y0 - PAD:Y1 + PAD, X0 - PAD:X1 + PAD], cv2.COLOR_BGR2GRAY)
th, tw = tpl.shape
sx0, sy0 = X0 - PAD - SEARCH, Y0 - PAD - SEARCH
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-i", SRC, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p",
    "-c:a", "copy", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
hits = 0
for f in frames(SRC):
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    area = g[sy0:sy0 + th + 2 * SEARCH, sx0:sx0 + tw + 2 * SEARCH]
    r = cv2.matchTemplate(area, tpl, cv2.TM_CCOEFF_NORMED); _, score, _, (mx, my) = cv2.minMaxLoc(r)
    if score > THR:                                   # mochila visível (ninguém na frente)
        x, y = sx0 + mx, sy0 + my
        box = g[y:y + th, x:x + tw]
        bag = np.median(box)
        mask = np.zeros((H, W), np.uint8)
        mask[y:y + th, x:x + tw] = (box > bag + 35).astype(np.uint8) * 255
        mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))
        f = cv2.inpaint(f, mask, 4, cv2.INPAINT_TELEA); hits += 1
    enc.stdin.write(f.tobytes())
enc.stdin.close(); enc.wait(); print("quadros corrigidos:", hits)
