"""Prolonga a música repetindo o último compasso (4 batidas) até a duração pedida.
Uso: python3 -I scripts/loop-beat.py <entrada.wav> <saida.wav> <duracao_s>
Grade da música da trend: batida em 5.72 + 0.57775*k (103,9 BPM); loop = 8.016–10.327 s (começa no bumbo forte)."""
import sys, wave, numpy as np
src, dst, total = sys.argv[1], sys.argv[2], float(sys.argv[3])
LS, LE, XF = 8.016, 10.327, 0.012            # início/fim do loop (s) e crossfade nas emendas
w = wave.open(src); sr, ch = w.getframerate(), w.getnchannels()
x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, ch).astype(np.float32)
s, e, xf = int(LS * sr), int(LE * sr), int(XF * sr)
out, loop = x[:e].copy(), x[s:e]
ramp = np.linspace(0, 1, xf)[:, None]
while len(out) < total * sr:
    out[-xf:] = out[-xf:] * (1 - ramp) + loop[:xf] * ramp   # emenda sem clique
    out = np.concatenate([out, loop[xf:]])
out = np.clip(out[: int(total * sr)], -32768, 32767).astype(np.int16)
o = wave.open(dst, "wb"); o.setnchannels(ch); o.setsampwidth(2); o.setframerate(sr); o.writeframes(out.tobytes()); o.close()
