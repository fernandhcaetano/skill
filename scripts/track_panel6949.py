# Passo 1: acha o painel de marcas (Arezzo/Schutz/...) em cada quadro (1080p) por template matching.
import cv2, json, subprocess, numpy as np, sys
T0, T1 = 1.5, 34.1
ref = cv2.imread(sys.argv[1], 0)        # quadro de referência (t=20 s) em 1080x1920, já com a cor F
tpl = ref[30:560, 700:790]
tone = ("zscale=w=1080:h=1920:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,"
        "zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=gamma=0.97:saturation=1.05:contrast=1.12,fps=30,format=gray")
p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(T0), "-to", str(T1), "-i", "raw/IMG_6949.MOV",
                      "-vf", tone, "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
out = []
while True:
    b = p.stdout.read(1080 * 1920)
    if len(b) < 1080 * 1920: break
    g = np.frombuffer(b, np.uint8).reshape(1920, 1080)
    r = cv2.matchTemplate(g[:900], tpl, cv2.TM_CCOEFF_NORMED)
    _, mx, _, loc = cv2.minMaxLoc(r)
    out.append([loc[0], loc[1], round(float(mx), 3)])
json.dump(out, open("raw/track6949.json", "w"))
print(len(out), "quadros")
