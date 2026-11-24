# Plano de enquadramento (tempos do arquivo original; z = aproximação; cx, cy = centro em fração do quadro)
SHOTS = [
    (7.50, 9.00, 1.8, 0.74, 0.62),   # Luísa, empilhadeira vindo ao fundo
    (9.00, 10.80, 2.0, 0.52, 0.55),  # empilhadeira chegando: Daniel + empilhadeira, à direita do paredão
    (10.80, 12.70, 2.0, 0.66, 0.60), # Luísa: "Gente, eu tô aqui com... Daniel"
    (12.70, 18.05, 1.15, 0.565, 0.565),  # os dois
    (18.05, 23.00, 1.7, 0.60, 0.60), # Luísa pergunta
    (23.00, 30.30, 1.7, 0.32, 0.60), # Daniel responde
    (30.30, 33.40, 1.15, 0.565, 0.565),
    (33.40, 36.40, 1.7, 0.32, 0.60), # Daniel
    (36.40, 39.30, 1.15, 0.565, 0.565),
]
W, H = 2160, 3840
def crop(z, cx, cy):
    w, h = round(W / z / 2) * 2, round(H / z / 2) * 2
    x = min(max(cx * W - w / 2, 0), W - w); y = min(max(cy * H - h / 2, 0), H - h)
    return w, h, int(x) // 2 * 2, int(y) // 2 * 2
if __name__ == '__main__':
    for a, b, z, cx, cy in SHOTS: print(a, b, *crop(z, cx, cy))
