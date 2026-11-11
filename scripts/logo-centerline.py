"""Extract the +soma logo centerline (skeleton) as polylines -> src/SomaCGI/logoPaths.json.
The logo is a constant-width line, so a tube along its centerline rebuilds it in 3D."""
import json, sys
import numpy as np
from PIL import Image
from skimage.morphology import skeletonize
from skimage.measure import approximate_polygon

src, out = sys.argv[1], sys.argv[2]
a = np.array(Image.open(src).convert("RGBA"))[:, :, 3] > 100
H, W = a.shape
# stroke width estimate
from scipy.ndimage import distance_transform_edt
dt = distance_transform_edt(a)
sk = skeletonize(a)
width = float(np.median(dt[sk]) * 2)
pts = set(zip(*np.nonzero(sk)))
def nb(p):
    y, x = p
    return [(y+dy, x+dx) for dy in (-1,0,1) for dx in (-1,0,1) if (dy or dx) and (y+dy, x+dx) in pts]
deg = {p: len(nb(p)) for p in pts}
used_edges = set()
paths = []
def walk(start, nxt):
    path = [start, nxt]; used_edges.add(frozenset((start, nxt)))
    prev, cur = start, nxt
    while deg[cur] == 2:
        cand = [q for q in nb(cur) if q != prev and frozenset((cur, q)) not in used_edges]
        if not cand: break
        q = cand[0]; used_edges.add(frozenset((cur, q)))
        prev, cur = cur, q; path.append(cur)
        if cur == start: break
    return path
nodes = [p for p in pts if deg[p] != 2]
for n in nodes:
    for q in nb(n):
        if frozenset((n, q)) not in used_edges:
            paths.append(walk(n, q))
# pure loops
for p in pts:
    for q in nb(p):
        if frozenset((p, q)) not in used_edges:
            paths.append(walk(p, q))
res = []
for pth in paths:
    if len(pth) < 6: continue
    arr = np.array([(x, y) for y, x in pth], float)
    arr = approximate_polygon(arr, tolerance=0.8)
    res.append(arr.round(1).tolist())
json.dump({"width": W, "height": H, "stroke": width, "paths": res}, open(out, "w"))
print(W, H, "stroke", width, "paths", len(res), [len(r) for r in res])
