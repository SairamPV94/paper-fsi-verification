import numpy as np, matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection

plt.rcParams.update({"font.size": 8, "font.family": "serif",
                     "mathtext.fontset": "cm", "axes.linewidth": 0.6})
sec = np.load("section_x0.npz")

# Mid-plane slice of the feF1 fluid mesh (legacy VTK polydata)
L = open("feF1_x0.vtk").read().split("\n")
i = 0
while not L[i].startswith("POINTS"):
    i += 1
n = int(L[i].split()[1])
vals = []
i += 1
while len(vals) < 3*n:
    vals += L[i].split()
    i += 1
P = np.array(vals, float).reshape(-1, 3)*1e3
while not L[i].startswith("POLYGONS"):
    i += 1
m, tot = map(int, L[i].split()[1:3])
tok = []
i += 1
while len(tok) < tot:
    tok += L[i].split()
    i += 1
tok = list(map(int, tok))
polys = []
k = 0
for j in range(m):
    nv = tok[k]
    polys.append(P[tok[k + 1:k + 1 + nv]][:, [2, 1]])   # (z, y)
    k += 1 + nv


def flap(ax):
    ax.add_patch(plt.Rectangle((0, -1), 65, 2, fc="#e08a2c", ec="k",
                               lw=0.5, zorder=5))


cols = {"wall": "k", "upperInlet": "#1f5fbf", "lowerInlet": "#1f5fbf",
        "outlet": "#b22222", "interface": "k"}

fig, (a, b) = plt.subplots(2, 1, figsize=(6.3, 4.6),
                           gridspec_kw={"height_ratios": [1, 1.35],
                                        "hspace": 0.35})
for k, s in sec.items():
    if len(s) == 0:
        continue
    a.add_collection(LineCollection(s[:, :, ::-1], colors=cols[k],
                                    linewidths=1.4 if k in ("upperInlet", "lowerInlet", "outlet") else 0.7))
flap(a)
a.set_xlim(-48, 352)
a.set_ylim(-48, 48)
a.set_aspect("equal")
a.set_xlabel(r"$z$ (mm)")
a.set_ylabel(r"$y$ (mm)")
for y0 in (27.15, -27.15):
    a.annotate("", xy=(-28, y0), xytext=(-47, y0),
               arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#1f5fbf"))
a.text(-44, 27.15 + 14, "upper inlet", color="#1f5fbf", fontsize=7)
a.text(-44, -27.15 - 18, "lower inlet", color="#1f5fbf", fontsize=7)
a.text(344, 0, "outlet", color="#b22222", rotation=90, va="center",
       ha="left", fontsize=7)
a.annotate("flap", xy=(45, 1.2), xytext=(62, 18), fontsize=7,
           arrowprops=dict(arrowstyle="-", lw=0.5))
a.annotate("", xy=(120, -32), xytext=(120, -12),
           arrowprops=dict(arrowstyle="-|>", lw=0.8))
a.text(124, -26, r"$\mathbf{g}$", fontsize=8)
a.annotate("", xy=(95, -38.1), xytext=(95, 38.1),
           arrowprops=dict(arrowstyle="<->", lw=0.5))
a.text(98, 12, r"$\varnothing\,76.2$", fontsize=7)
a.text(165, 18, "outlet pipe extended by 250 mm", fontsize=7)
a.text(-14, 27.15, r"$\varnothing\,21.9$", fontsize=6, ha="center",
       va="center")
a.set_title(r"(a) flow domain, mid-plane $x = 0$", fontsize=8, loc="left")

b.add_collection(PolyCollection(polys, facecolors="none", edgecolors="0.35",
                                linewidths=0.15, rasterized=True))
for k, s in sec.items():
    if len(s):
        b.add_collection(LineCollection(s[:, :, ::-1], colors=cols[k],
                                        linewidths=0.9))
flap(b)
cl = np.loadtxt("phaseI_centreline.csv", delimiter=",", comments="#",
                skiprows=4)
b.plot(cl[:, 2], cl[:, 1], "--", color="#c0392b", lw=1.0, zorder=6,
       label="measured centreline, Phase I")
b.legend(loc="lower right", fontsize=6.5, frameon=True, framealpha=1.0, edgecolor="0.7")
b.set_xlim(-31, 100)
b.set_ylim(-39.5, 39.5)
b.set_aspect("equal")
b.set_xlabel(r"$z$ (mm)")
b.set_ylabel(r"$y$ (mm)")
b.set_title(r"(b) fluid mesh feF1 ($2.3\times10^{5}$ cells) at $x = 0$, "
            r"undeformed flap", fontsize=8, loc="left")
fig.savefig("hessenthaler-geometry.pdf", bbox_inches="tight", dpi=600)
fig.savefig("hessenthaler-geometry.png", dpi=200, bbox_inches="tight")
