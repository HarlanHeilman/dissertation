"""Fig. 3.6 (new), diffuse scattering around the specular beam and the size of the integration box, from the same CCD scan as the
reduction figure (ZnPc, CCD Scan 85302, 285.0 eV, s polarization, 2 x 2 binned frames).

Frames: 114 (direct beam, theta = 0), 124 (theta = 2.06 deg), 201 (theta = 13.56 deg). For each frame the background
per pixel is the mean of the two 13 x 13 boxes 28 pixels to either side of the spot, as in the reduction, and the net
counts are summed in square boxes of half width w centred on the spot.
"""
import json, os
from figlib import *
from matplotlib.patches import Rectangle
from matplotlib.colors import LogNorm

NPZ = os.environ.get('CCD_NPZ', os.path.expanduser('~/mnt/dissertation/_to_delete/figs-new/ccd_85302_285eV.npz'))
d = np.load(NPZ)
T = d['table']
FR = {114: ('direct beam', GRAY), 124: ('θ = 2.06°', BLACK), 201: ('θ = 13.56°', RED)}
R_BOX, BG_OFF = 6, 28
WS = np.arange(1, 27)
info = {}
for f in FR:
    r = T[T[:, 0] == f][0]
    img = d[f'frame{f}'].astype(float)
    ry, rx = int(r[4]), int(r[5])
    bpix = np.mean([img[ry - R_BOX:ry + R_BOX + 1, rx + dx - R_BOX:rx + dx + R_BOX + 1].mean() for dx in (-BG_OFF, BG_OFF)])
    net = []
    for w in WS:
        box = img[max(ry - w, 0):ry + w + 1, max(rx - w, 0):rx + w + 1]
        net.append(box.sum() - bpix * box.size)
    net = np.array(net)
    # projections through the 13-pixel-wide band of the integration box, which average down the pixel noise
    prof_v = (img[ry - 30:ry + 31, rx - R_BOX:rx + R_BOX + 1] - bpix).sum(axis=1)
    prof_h = (img[ry - R_BOX:ry + R_BOX + 1, rx - 30:rx + 31] - bpix).sum(axis=0)
    info[f] = dict(img=img, ry=ry, rx=rx, bpix=bpix, net=net, pv=prof_v, ph=prof_h, theta=float(r[1]))
FACTS = {str(f): dict(theta=v['theta'], frac_w6=float(v['net'][WS == 6][0] / v['net'][-1]),
                      frac_w12=float(v['net'][WS == 12][0] / v['net'][-1])) for f, v in info.items()}
# bias of the 13 x 13 box relative to the direct beam normalization
FACTS['ratio_w6_201_over_114'] = FACTS['201']['frac_w6'] / FACTS['114']['frac_w6']

BOXES = ((2, '-'), (6, (0, (3, 1.5))), (12, (0, (1, 1.2))))   # half widths: 5 x 5, 13 x 13, 25 x 25
for f in FR:
    n = info[f]['net']
    info[f]['frac'] = {w: float(n[WS == w][0] / n[-1]) for w, _ in BOXES}
FACTS['fractions'] = {str(f): info[f]['frac'] for f in FR}

fig = plt.figure(figsize=(6.5, 2.35))
gs = fig.add_gridspec(1, 3, wspace=0.06, left=0.005, right=0.995, top=0.91, bottom=0.01)
H = 16
axes = []
for k, (f, (lab, col)) in enumerate(FR.items()):
    ax = fig.add_subplot(gs[0, k]); axes.append(ax)
    v = info[f]; ry, rx = v['ry'], v['rx']
    crop = v['img'][ry - H:ry + H + 1, rx - H:rx + H + 1] - v['bpix']
    ax.imshow(np.clip(crop, 1, None), cmap='hot', norm=LogNorm(vmin=3, vmax=crop.max()), origin='upper',
              interpolation='nearest', extent=(-H - 0.5, H + 0.5, H + 0.5, -H - 0.5))
    for w, ls in BOXES:
        ax.add_patch(Rectangle((-w - 0.5, -w - 0.5), 2 * w + 1, 2 * w + 1, fill=False, ec='white', lw=1.0, ls=ls))
    ax.set_title(lab, fontsize=8, pad=2)
    ax.set_xticks([]); ax.set_yticks([])
grid_labels(fig, [[(axes[0], 'a'), (axes[1], 'b'), (axes[2], 'c')]])
save(fig, 'fig2-09b_offspecular')
json.dump(FACTS, open(os.path.join(OUT, 'fig2-09b_facts.json'), 'w'), indent=1)
print(FACTS['fractions'])
