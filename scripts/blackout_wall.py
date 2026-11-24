# Apaga letras claras de um painel escuro encostado na borda ESQUERDA do quadro.
# Para cada faixa de linhas, mede onde o painel escuro (que começa em x=0) termina,
# e só pinta de preto os pixels claros dentro dele.
# Teste:  python3 -I blackout_wall.py --test in.png out.png
# Filtro: python3 -I blackout_wall.py W H < rgb24 > rgb24
import sys, numpy as np, cv2
BAND = 24
def edges(gray, ymax):
    h, w = gray.shape
    E = np.zeros(h, np.int32)
    lim = int(w * 0.5)
    for y0 in range(0, ymax, BAND):
        band = gray[y0:y0 + BAND, :lim]
        # pixels escuros OU letras (claros) contam como painel se houver muito escuro ao redor
        darkfrac = (band < 50).mean(axis=0)
        sm = np.convolve(darkfrac, np.ones(41) / 41, mode='same')  # tolera letras
        if sm[:30].mean() < 0.45:
            continue
        bad = np.where(sm < 0.35)[0]
        e = bad[0] if len(bad) else lim
        E[y0:y0 + BAND] = e
    # suaviza a borda entre faixas
    E = cv2.blur(E.astype(np.float32).reshape(-1, 1), (1, BAND * 2 + 1)).ravel().astype(np.int32)
    return E
def process(img):
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    sat = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)[..., 1]
    ymax = int(h * 0.62)
    E = edges(gray, ymax)
    xs = np.arange(w)[None, :]
    panel = (xs < (E[:, None] - 6))
    panel[ymax:] = False
    letters = panel & (gray > 70) & (sat < 110)
    m = cv2.dilate(letters.astype(np.uint8) * 255, np.ones((5, 5), np.uint8))
    m &= (panel.astype(np.uint8) * 255)
    m = cv2.GaussianBlur(m, (3, 3), 0).astype(np.float32)[..., None] / 255
    base = np.array([14, 14, 16], np.float32)
    sel = panel & (gray < 50)
    if sel.sum() > 500:
        base = np.median(img[sel], axis=0).astype(np.float32)
    out = img.astype(np.float32) * (1 - m) + base * m
    return out.astype(np.uint8)
if sys.argv[1] == '--test':
    im = cv2.cvtColor(cv2.imread(sys.argv[2]), cv2.COLOR_BGR2RGB)
    cv2.imwrite(sys.argv[3], cv2.cvtColor(process(im), cv2.COLOR_RGB2BGR))
else:
    W, H = int(sys.argv[1]), int(sys.argv[2]); size = W * H * 3
    i, o = sys.stdin.buffer, sys.stdout.buffer
    while True:
        b = i.read(size)
        if len(b) < size: break
        o.write(process(np.frombuffer(b, np.uint8).reshape(H, W, 3)).tobytes())
