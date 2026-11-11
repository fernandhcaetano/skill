"""Trilha + efeitos sintetizados (sem direitos autorais) do filme CGI +soma -> public/soma/cgi/trilha.wav.
Marcos (s): cortes 4.0 / 8.5 / 13.0, paraquedas abre 5.2, pouso 16.2, fim 20.0."""
import wave
import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
DUR = 20.0
N = int(SR * DUR)
rng = np.random.default_rng(3)
t = np.arange(N) / SR

def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)
def lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)
def env_ar(n, a, r):
    e = np.ones(n); na = int(a * SR); e[:na] = np.linspace(0, 1, na)
    e *= np.exp(-np.arange(n) / (r * SR)); return e
def place(buf, x, at, gain=1.0):
    i = int(at * SR); j = min(len(buf), i + len(x)); buf[i:j] += x[: j - i] * gain
def seg(a, b):  # janela suave para um trecho
    w = np.zeros(N); i, j = int(a * SR), int(b * SR); w[i:j] = 1
    k = int(0.25 * SR); return np.convolve(w, np.ones(k) / k, "same")

L = np.zeros(N); Rr = np.zeros(N)
# ---------- música: pad quente + violão/pluck bossa, 96 bpm ----------
bpm = 96; beat = 60 / bpm
chords = [[48, 55, 59, 64], [45, 52, 55, 60], [50, 57, 60, 65], [43, 50, 53, 59]]  # Cmaj7 Am7 Dm7 G7
m2f = lambda m: 440 * 2 ** ((m - 69) / 12)
pad = np.zeros(N)
bar = 4 * beat
for k in range(int(DUR / bar) + 1):
    ch = chords[k % 4]; st = k * bar
    n = int(bar * SR * 1.1); tt = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * m2f(m + 12) * tt * (1 + d)) for m in ch for d in (-0.002, 0.002))
    e = np.minimum(1, tt / 0.6) * np.minimum(1, (bar * 1.1 - tt) / 0.5)
    place(pad, s * e, st)
pad = lp(pad, 1800)
pluck = np.zeros(N)
pattern = [0, 1.5, 2, 3, 3.5]  # síncope de bossa
for k in range(int(DUR / bar) + 1):
    ch = chords[k % 4]
    for j, b in enumerate(pattern):
        at = k * bar + b * beat
        if at >= DUR: break
        n = int(0.6 * SR); tt = np.arange(n) / SR
        notes = ch[1:] if j % 2 else [ch[0] - 12]
        s = sum(np.sin(2 * np.pi * m2f(m + 12) * tt) + 0.3 * np.sin(4 * np.pi * m2f(m + 12) * tt) for m in notes)
        place(pluck, s * env_ar(n, 0.004, 0.18), at)
music = pad * 0.5 + pluck * 0.6
# entra suave, cresce no pouso, sai no fim
mvol = np.interp(t, [0, 1.5, 12.5, 16.2, 18.5, 20], [0.0, 0.55, 0.6, 0.95, 0.9, 0.0])
music *= mvol
# ---------- ambiente ----------
noise = rng.standard_normal(N)
wind = bp(noise, 200, 1400) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.17 * t) ** 2)
amb = wind * (seg(0, 13.0) * 0.35 + seg(8.5, 13.0) * 0.6)
waves = lp(rng.standard_normal(N), 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.12 * t + 1) ** 2)
amb += waves * seg(13.0, 20) * 0.9
# hélice do dirigível (cena 1)
prop = (np.sign(np.sin(2 * np.pi * 38 * t)) * 0.4 + np.sin(2 * np.pi * 76 * t)) * (1 + 0.3 * np.sin(2 * np.pi * 6 * t))
amb += lp(prop, 400) * seg(0, 4.0) * 0.25
# ---------- efeitos ----------
fx = np.zeros(N)
def whoosh(d=0.6):
    n = int(d * SR); tt = np.arange(n) / SR
    x = rng.standard_normal(n); f = 300 + 2500 * np.sin(np.pi * tt / d)
    y = np.zeros(n)
    for a in range(0, n, 480):  # filtro varrendo
        lo = max(50, f[a] * 0.5); hi = min(SR / 2 - 100, f[a] * 1.5)
        y[a:a + 480] = bp(x[a:a + 480 + 2000], lo, hi)[:len(y[a:a + 480])]
    return y * np.sin(np.pi * tt / d) ** 2
for at in (3.75, 8.25, 12.75):
    place(fx, whoosh(0.55), at, 0.7)
# paraquedas abrindo: "fwump" de tecido
n = int(0.5 * SR); tt = np.arange(n) / SR
fw = bp(rng.standard_normal(n), 80, 900) * env_ar(n, 0.02, 0.12) + np.sin(2 * np.pi * 70 * tt) * env_ar(n, 0.005, 0.08)
place(fx, fw, 5.15, 0.9)
# pouso: baque grave + borrifo
n = int(0.8 * SR); tt = np.arange(n) / SR
thump = np.sin(2 * np.pi * (55 + 40 * np.exp(-tt * 20)) * tt) * env_ar(n, 0.002, 0.18)
splash = bp(rng.standard_normal(n), 1500, 8000) * env_ar(n, 0.01, 0.25)
place(fx, thump, 16.2, 1.3); place(fx, splash, 16.22, 0.5)
# brilho final (logo completo)
n = int(2.5 * SR); tt = np.arange(n) / SR
ch = sum(np.sin(2 * np.pi * m2f(m) * tt) * np.exp(-tt * (1.2 + i * 0.3)) for i, m in enumerate([84, 88, 91, 96]))
place(fx, ch * env_ar(n, 0.005, 3), 16.45, 0.35)

def norm(x): return x / (np.max(np.abs(x)) + 1e-9)
mix = norm(music) * 0.55 + norm(amb) * 0.22 + norm(fx) * 0.75
# estéreo leve: ambiente/whoosh decorrelacionados
d = int(0.012 * SR)
left = mix; right = np.concatenate([np.zeros(d), mix[:-d]]) * 0.5 + mix * 0.5
st = np.stack([left, right], 1)
st = st / np.max(np.abs(st)) * 10 ** (-1 / 20)
fade = np.minimum(1, (DUR - t) / 0.4)[:, None]
st *= fade
with wave.open("public/soma/cgi/trilha.wav", "w") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print("ok")
