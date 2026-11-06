"""Monta o vídeo final no Estilo ferndoc a partir da decupagem aprovada.

Uso: python3 -I scripts/ferndoc/montar.py raw/ferndoc/corte.json SAIDA.mp4 parte1.mov parte2.mov ...

corte.json:
{
  "cortes": [                       # na ordem final do vídeo
    {"id": "1.03"},                 # trecho inteiro de raw/ferndoc/chunks.json
    {"id": "2.07", "ini": 12.40},   # corta o começo (tempo da fonte, em s)
    {"id": "2.08", "fim": 20.10},   # corta o fim
    {"id": "3.01", "zoom": 1.12},   # força zoom (por padrão alterna 1.00 / 1.12 entre cortes da mesma câmera)
    {"espaco": "meia noite", "dur": 6},          # espaço reservado (tela escura + aviso) p/ inserir algo depois
    {"clipe": "raw/x.mp4", "ini": 30, "dur": 6, "vol": -8,   # clipe em TELA CHEIA 9:16 com o próprio áudio (vol em dB)
     "enquadre": [[0, 0.45], [1.55, 0.52, 1.4, 0.4]]}  # por plano: [t (s, relativo ao ini), centro x, zoom, centro y]
  ],
  "lettering": "raw/ferndoc/lettering.json",  # opcional (ver lettering.py); tempos no vídeo FINAL
  "sfx": [{"arq": "clique/clique-1.wav", "t": 12.3, "db": -9, "dur": 1.5}]  # opcional; banco public/sfx/ferndoc,
}                                     # t = início no vídeo final, db = ganho, dur = corta o som (ex.: teclado)
Também grava raw/ferndoc/palavras_final.json (palavras com o tempo no vídeo final) para posicionar o lettering.
"""
import json
import os
import subprocess
import sys
import wave

import numpy as np

PAD, FPS = 0.08, 30
cfg_path, saida, videos = sys.argv[1], sys.argv[2], sys.argv[3:]
cfg = json.load(open(cfg_path))
chunks = {c["id"]: c for c in json.load(open("raw/ferndoc/chunks.json"))}

# Energia (10 ms) de cada parte para encaixar cada corte no ponto mais silencioso.
rms = {}
for p in range(1, len(videos) + 1):
    with wave.open(f"raw/ferndoc/p{p}_16.wav") as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
    rms[p] = np.sqrt(np.convolve(x ** 2, np.ones(160) / 160, "same")[::160])


def snap(p, t, r=0.12):
    i0, i1 = max(0, int((t - r) * 100)), min(len(rms[p]) - 1, int((t + r) * 100))
    return (i0 + int(np.argmin(rms[p][i0:i1 + 1]))) / 100


def hdr(v):
    t = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_transfer",
                        "-of", "csv=p=0", v], capture_output=True, text=True).stdout.strip()
    # o ffprobe pode devolver "arib-std-b67," (vírgula extra por causa dos dados do Dolby Vision): comparar por conteúdo
    return any(x in t for x in ("arib-std-b67", "smpte2084"))


pieces, palavras, out_t, last_p, z = [], [], 0.0, None, 1.0
for c in cfg["cortes"]:
    if "espaco" in c or "clipe" in c:   # inserções em tela cheia: não usam a fala nem o zoom alternado
        d = round(c["dur"] * FPS) / FPS
        pieces.append(("ins", c, d, None)); out_t += d; last_p = None; z = 1.0
        continue
    ch = chunks[c["id"]]; p = ch["parte"]
    s = snap(p, c["ini"]) if "ini" in c else max(0.0, ch["ini"] - PAD)
    e = snap(p, c["fim"]) if "fim" in c else ch["fim"] + PAD
    s, e = round(s * FPS) / FPS, round(e * FPS) / FPS
    if "zoom" in c:
        z = c["zoom"]
    elif last_p == p:
        z = 1.12 if z == 1.0 else 1.0
    else:
        z = 1.0
    last_p = p
    for w in ch["palavras"]:
        if s - 0.05 <= (w["s"] + w["e"]) / 2 <= e + 0.05:
            palavras.append({"w": w["w"], "s": round(out_t + w["s"] - s, 2), "e": round(out_t + w["e"] - s, 2)})
    pieces.append((p, s, e, z)); out_t += e - s

json.dump(palavras, open("raw/ferndoc/palavras_final.json", "w"), ensure_ascii=False, indent=0)

# 1) Cada trecho vira um arquivo (busca direta com -ss: pouca memória mesmo com dezenas de cortes).
SEG = "raw/ferndoc/segs"
os.makedirs(SEG, exist_ok=True)
lista = []
FONTE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "BricolageGrotesque-500.ttf")
ENC = ["-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
       "-c:v", "libx264", "-preset", "fast", "-crf", "14", "-g", "1", "-c:a", "pcm_s16le"]
TAG709 = "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv"
for k, (p, s, e, z) in enumerate(pieces):
    if p == "ins":
        c, d = s, e
        out = f"{SEG}/s{k:03d}.mov"
        if "espaco" in c:
            txt = f"CLIPE · {c['espaco']} · {c['dur']:g}s".replace(":", "\\:")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=0x16161a:s=1080x1920:r={FPS}:d={d}",
                            "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", f"{d:.3f}",
                            "-vf", f"drawtext=fontfile={FONTE}:text='{txt}':fontcolor=white@0.85:fontsize=54:"
                                   f"x=(w-text_w)/2:y=(h-text_h)/2,format=yuv420p,setsar=1,{TAG709}", *ENC, out], check=True)
        else:
            # clipe em tela cheia 9:16. "enquadre": [[t, cx, zoom=1, cy=0.5], ...] — um item por plano do clipe:
            # centro horizontal (cx) e vertical (cy) do recorte em fração do quadro, e zoom (1 = altura inteira).
            # Cada plano vira um sub-trecho (recorte fixo); áudio contínuo, com fade só no começo e no fim.
            v = c["clipe"]
            tmc = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,"
                   "zscale=t=bt709:m=bt709:r=tv,format=yuv420p,") if hdr(v) else ""
            enq = c.get("enquadre", [[0, 0.5]])
            ini, sub = c.get("ini", 0), []
            for j, it in enumerate(enq):
                t0 = round(it[0] * FPS) / FPS
                t1 = d if j + 1 == len(enq) else round(enq[j + 1][0] * FPS) / FPS
                if t1 - t0 <= 0:
                    continue
                cx, zm = it[1], (it[2] if len(it) > 2 else 1.0)
                cy = it[3] if len(it) > 3 else 0.5
                ch_ = f"ih/{zm}"; cw_ = f"ih/{zm}*9/16"
                crop = (f"crop=w={cw_}:h={ch_}:x='clip({cx}*iw-({cw_})/2\\,0\\,iw-({cw_}))'"
                        f":y='clip({cy}*ih-({ch_})/2\\,0\\,ih-({ch_}))'")
                af = "aresample=48000,aformat=channel_layouts=mono," + f"volume={c.get('vol', -8)}dB"
                if j == 0:
                    af += ",afade=t=in:d=0.15"
                if j == len(enq) - 1:
                    af += f",afade=t=out:st={max(0, t1 - t0 - 0.3):.3f}:d=0.3"
                so = f"{SEG}/s{k:03d}_{j}.mov"
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ini + t0:.3f}", "-i", v, "-t", f"{t1 - t0:.3f}",
                                "-vf", f"{tmc}{crop},scale=1080:1920:flags=lanczos,fps={FPS},format=yuv420p,setsar=1,{TAG709}",
                                "-af", af, *ENC, so], check=True)
                sub.append(so)
            for so in sub:
                lista.append(f"file '{os.path.abspath(so)}'")
            continue
        lista.append(f"file '{os.path.abspath(out)}'")
        continue
    v = videos[p - 1]
    # HDR (HLG/Dolby Vision do iPhone) -> SDR. Escolhido por ele em 06/11 (opção "2 menos amarelo" de
    # preview-cor-mondepars.jpg): hable npl=100, saturação +8 %, temperatura 7300 K (tira o amarelo), contraste +6 %.
    # Rejeitados: mobius npl=203 (pele laranja, "cara de HDR") e gama 1.12 (pálido).
    # "cor": "neutra" no corte.json = só a conversão HDR->SDR, sem o ajuste de cor (pedido dele no vídeo da Anitta).
    grade = "" if cfg.get("cor") == "neutra" else \
        "eq=saturation=1.08,colortemperature=temperature=7300,eq=contrast=1.06,"
    tm = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,"
          "zscale=t=bt709:m=bt709:r=tv,format=yuv420p," + grade) if hdr(v) else ""
    W, H = round(1080 * z / 2) * 2, round(1920 * z / 2) * 2
    d = e - s
    out = f"{SEG}/s{k:03d}.mov"
    tag = f"{v}|{s:.3f}|{e:.3f}|{z}|{tm}|v709"
    if os.environ.get("REUSE") == "1" and os.path.exists(out + ".tag") and open(out + ".tag").read() == tag:
        lista.append(f"file '{os.path.abspath(out)}'"); continue   # trecho igual ao da última montagem
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.3f}", "-i", v, "-t", f"{d:.3f}",
                    "-vf", f"{tm}scale={W}:{H},crop=1080:1920:(iw-1080)/2:(ih-1920)*0.4,fps={FPS},format=yuv420p,setsar=1,"
                    # etiqueta de cor CERTA: sem isso o trecho herda "bt2020" do HDR e a junção reconverte as cores
                    # (imagem lavada/pálida/amarelada — o bug das v1/v2).
                    "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv",
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                    "-af", f"aresample=48000,aformat=channel_layouts=mono,afade=t=in:d=0.01,afade=t=out:st={max(0, d - 0.015):.3f}:d=0.015",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "14", "-g", "1", "-c:a", "pcm_s16le", out], check=True)
    open(out + ".tag", "w").write(tag)
    lista.append(f"file '{os.path.abspath(out)}'")
open(f"{SEG}/lista.txt", "w").write("\n".join(lista) + "\n")

# 2) Junta, aplica lettering e efeitos, normaliza o áudio.
ins = ["-f", "concat", "-safe", "0", "-i", f"{SEG}/lista.txt"]
graph = []
sfx = cfg.get("sfx", [])
graph.append("[0:a]highpass=f=80,"
             "acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-14:TP=-1.5:LRA=7"
             + ("[voz]" if sfx else "[a]"))

extra, vout = [], "0:v"
n_in = 1
if sfx:
    mix = ["[voz]"]
    for k, fx in enumerate(sfx):
        extra += ["-i", f"public/sfx/ferndoc/{fx['arq']}"]
        ms = int(fx["t"] * 1000); cut = f"atrim=0:{fx['dur']},afade=t=out:st={fx['dur'] - 0.08}:d=0.08," if "dur" in fx else ""
        graph.append(f"[{n_in}:a]{cut}aresample=48000,aformat=channel_layouts=mono,volume={fx.get('db', -9)}dB,"
                     f"adelay={ms}|{ms}[fx{k}]")
        mix.append(f"[fx{k}]"); n_in += 1
    graph.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,alimiter=limit=0.9[a]")
if cfg.get("lettering"):
    ov = "raw/ferndoc/lettering.mov"
    here = os.path.dirname(os.path.abspath(__file__))
    letter = subprocess.Popen([sys.executable, "-I", f"{here}/lettering.py", cfg["lettering"], str(out_t)],
                              stdout=subprocess.PIPE)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", "1080x1920",
                    "-r", str(FPS), "-i", "-", "-c:v", "qtrle", ov], stdin=letter.stdout, check=True)
    extra += ["-i", ov]
    graph.append(f"[0:v][{n_in}:v]overlay=0:0:eof_action=pass,format=yuv420p[vf]"); vout = "[vf]"

subprocess.run(["ffmpeg", "-v", "error", "-stats", "-y", *ins, *extra, "-filter_complex", ";".join(graph),
                "-map", vout, "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high",
                "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", saida], check=True)
print(f"{len(pieces)} cortes, duração final {out_t:.1f}s -> {saida}")
