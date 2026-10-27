"""Divide raw/audio16.wav em trechos de fala (raw/chunks/cNNN.wav) e grava raw/segs.json."""
import json
import re
import subprocess

DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                            "raw/audio48.wav"], capture_output=True, text=True).stdout)
log = subprocess.run(["ffmpeg", "-i", "raw/audio48.wav", "-af",
                      "highpass=f=80,afftdn=nf=-25,silencedetect=n=-35dB:d=0.3", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]

segs, cur = [], 0.0
for a, b in zip(starts, ends):
    if a - cur > 0.15:
        segs.append((cur, a))
    cur = b
if DUR - cur > 0.15:
    segs.append((cur, DUR))

json.dump(segs, open("raw/segs.json", "w"))
for i, (a, b) in enumerate(segs):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(max(0, a - 0.1)), "-to", str(b + 0.1),
                    "-i", "raw/audio16.wav", "raw/chunks/c%03d.wav" % i], check=True)
print(f"{len(segs)} trechos de fala")
