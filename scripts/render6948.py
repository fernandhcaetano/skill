# Renderiza IMG_6948 com o plano de enquadramento (shots6948.py), cor F, legenda e áudio.
import subprocess, sys
sys.path.insert(0, 'scripts')
from shots6948 import SHOTS, crop
T0, T1 = SHOTS[0][0], SHOTS[-1][1]
tone = ("zscale=w=2160:h=3840:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,"
        "zscale=t=bt709:m=bt709:r=tv,format=yuv420p,fps=30")
n = len(SHOTS)
f = [f"[0:v]{tone},split={n}" + ''.join(f"[s{i}]" for i in range(n))]
for i, (a, b, z, cx, cy) in enumerate(SHOTS):
    w, h, x, y = crop(z, cx, cy)
    f.append(f"[s{i}]trim=start={a - T0:.3f}:end={b - T0:.3f},setpts=PTS-STARTPTS,crop={w}:{h}:{x}:{y},scale=1080:1920:flags=lanczos,setsar=1[v{i}]")
f.append(''.join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0,eq=gamma=0.97:saturation=1.05:contrast=1.12,ass=raw/legendas6948.ass[v]")
# conversa de bastidor antes de "Gente, eu tô aqui com..." fica baixinha (sem legenda)
duck = 10.75 - T0
f.append(f"[0:a]volume='if(lt(t,{duck - 0.15:.2f}),0.25,if(lt(t,{duck:.2f}),0.25+0.75*(t-{duck - 0.15:.2f})/0.15,1))':eval=frame,"
         "afade=t=in:d=0.03,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(T0), "-to", str(T1), "-i", "raw/IMG_6948.MOV",
       "-filter_complex", ';'.join(f), "-map", "[v]", "-map", "[a]",
       "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
       "out/IMG_6948.mp4"]
subprocess.run(cmd, check=True)
