"""Gera os efeitos sonoros (sintetizados, sem direitos autorais) em public/sfx/.

whoosh.wav  - passagem de ar curta para entrar nas cartelas de motivo
hit.wav     - toque grave e suave quando o texto da cartela aparece
chime.wav   - sino natalino com brilho para a tela final com o logo
"""
import os
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(7)
os.makedirs("public/sfx", exist_ok=True)


def save(name, x, peak_db):
    x = x / (np.max(np.abs(x)) + 1e-9) * 10 ** (peak_db / 20)
    data = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(f"public/sfx/{name}", "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def t(dur):
    return np.arange(int(SR * dur)) / SR


def lowpass(x, cutoff):
    """Passa-baixa de 1 polo com corte variável (array ou escalar)."""
    cutoff = np.broadcast_to(cutoff, x.shape)
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


# Whoosh: ruído com filtro que abre e fecha + envelope em sino.
tt = t(0.55)
env = np.sin(np.pi * np.clip(tt / 0.55, 0, 1)) ** 2.5
sweep = 400 + 5000 * np.sin(np.pi * tt / 0.55) ** 2
noise = rng.standard_normal(len(tt))
w = lowpass(noise, sweep) - lowpass(noise, sweep * 0.25)
save("whoosh.wav", w * env, -9)

# Hit: grave curto (sine com queda de pitch) + clique leve.
tt = t(0.35)
f = 110 * np.exp(-tt * 9) + 55
hit = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 14)
click = lowpass(rng.standard_normal(len(tt)), 3000) * np.exp(-tt * 120) * 0.4
save("hit.wav", hit + click, -10)

# Chime: sino (parciais inarmônicos) em duas notas + brilho de guizos.
tt = t(2.6)
chime = np.zeros_like(tt)
for start, f0 in ((0.0, 1046.5), (0.12, 1568.0)):  # C6, G6
    tl = np.clip(tt - start, 0, None)
    on = (tt >= start).astype(float)
    for ratio, amp, dec in ((1, 1, 2.2), (2.76, 0.45, 3.5), (5.4, 0.25, 5.5), (8.93, 0.12, 8)):
        chime += on * amp * np.sin(2 * np.pi * f0 * ratio * tl) * np.exp(-tl * dec)
bells = np.zeros_like(tt)
for k in range(14):  # guizos: rajadas curtas de parciais agudos
    st = 0.05 + k * 0.07 + rng.uniform(0, 0.03)
    tl = np.clip(tt - st, 0, None)
    on = (tt >= st).astype(float)
    fb = rng.uniform(5000, 7500)
    bells += on * np.sin(2 * np.pi * fb * tl) * np.exp(-tl * 40) * (1 - k / 16)
save("chime.wav", chime + 0.35 * bells, -8)
print("sfx ok")
