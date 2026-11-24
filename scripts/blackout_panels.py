# Apaga letras brancas de painéis pretos na parte de cima do quadro.
# Painel = região escura grande (fecha os buracos das letras); letra = pixel claro e pouco saturado dentro dela.
# Teste: python3 -I scripts/blackout_panels.py --test in.png out.png [ymax]
# Filtro: python3 -I scripts/blackout_panels.py W H [ymax] < rgb24 > rgb24
import sys, numpy as np, cv2
def process(img, ymax=0.5):
    h, w = img.shape[:2]
    Y = int(h * ymax)
    top = img[:Y]
    gray = cv2.cvtColor(top, cv2.COLOR_RGB2GRAY)
    sat = cv2.cvtColor(top, cv2.COLOR_RGB2HSV)[..., 1]
    dark = (gray < 40).astype(np.uint8) * 255
    k = max(15, w // 30) | 1
    panel = cv2.morphologyEx(dark, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(panel)
    keep = np.zeros_like(panel)
    for i in range(1, n):
        if st[i, 4] > 0.01 * w * Y and (dark[lab == i] > 0).mean() > 0.55:
            keep[lab == i] = 255
    letters = (keep > 0) & (gray > 75) & (sat < 70)
    m = cv2.dilate(letters.astype(np.uint8) * 255, np.ones((5, 5), np.uint8)) & keep
    m = cv2.GaussianBlur(m, (3, 3), 0).astype(np.float32)[..., None] / 255
    sel = (dark > 0) & (keep > 0)
    base = np.median(top[sel], axis=0).astype(np.float32) if sel.sum() > 500 else np.array([12, 12, 14], np.float32)
    out = img.copy()
    out[:Y] = (top.astype(np.float32) * (1 - m) + base * m).astype(np.uint8)
    return out
if sys.argv[1] == '--test':
    ym = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
    im = cv2.cvtColor(cv2.imread(sys.argv[2]), cv2.COLOR_BGR2RGB)
    cv2.imwrite(sys.argv[3], cv2.cvtColor(process(im, ym), cv2.COLOR_RGB2BGR))
else:
    W, H = int(sys.argv[1]), int(sys.argv[2]); ym = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
    size = W * H * 3; i, o = sys.stdin.buffer, sys.stdout.buffer
    while True:
        b = i.read(size)
        if len(b) < size: break
        o.write(process(np.frombuffer(b, np.uint8).reshape(H, W, 3), ym).tobytes())
