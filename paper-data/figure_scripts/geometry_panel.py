"""Geometry sketches of the four 2-D/axisymmetric benchmarks without one in
the paper: ringAddedMass, womersleyTube, collapsibleChannel and
mokLidDrivenCavity (dimensions from the solids4foam tutorial READMEs).
Writes figures/benchmarks_geometry_panel.pdf.  Usage: geometry_panel.py OUT.pdf"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Wedge, Circle, FancyArrowPatch

plt.rcParams.update({"font.size": 8, "mathtext.fontset": "cm",
                     "font.family": "serif", "pdf.fonttype": 42})
FLUID, SOLID, EDGE = "#dbe8f5", "#d62728", "black"


def dim(ax, p, q, text, off=(0, 0), **kw):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="<->", mutation_scale=7, lw=0.6))
    ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], text,
            ha="center", va="center", **kw)


def ring(ax):
    ax.add_patch(Circle((0, 0), 1.5, fc=FLUID, ec=EDGE, lw=1.2))
    ax.add_patch(Wedge((0, 0), 1.05, 0, 360, width=0.1, fc=SOLID, ec="none"))
    ax.add_patch(Circle((0, 0), 0.95, fc="white", ec="none"))
    t = np.linspace(0, 2 * np.pi, 300)
    r = 1.0 + 0.08 * np.cos(2 * t)
    ax.plot(r * np.cos(t), r * np.sin(t), "--", color="#555555", lw=0.8)
    ax.plot([0, 1.5], [0, 0], color="#888888", lw=0.5)
    ax.plot([0, 0], [0, 1.5], color="#888888", lw=0.5)
    ax.text(0, 0.25, "vacuum", ha="center")
    ax.text(-0.95, -1.05, "fluid", ha="center")
    ax.annotate("ring", (-0.72, 0.72), (-1.2, 1.25), color=SOLID, ha="center", fontsize=8, arrowprops=dict(arrowstyle="-", lw=0.5, color=SOLID))
    ax.text(-1.25, -1.35, "rigid wall", ha="center")
    ax.text(0, -0.35, "$n=2$ mode (dashed,\nexaggerated)", ha="center", va="center",
            color="#555555", fontsize=7)
    dim(ax, (0, 0), (1.5 * np.cos(-0.7), 1.5 * np.sin(-0.7)), "", )
    ax.text(0.95, -0.55, "$b=1.5$ m", fontsize=7)
    ax.text(1.05, 1.25, "modelled\nquadrant", ha="center", fontsize=6.5, color="#555555")
    ax.set_xlim(-1.7, 1.7); ax.set_ylim(-1.7, 1.7)
    ax.set_title("(a) ringAddedMass: $a=1$ m, $h=0.1$ m", fontsize=8)


def tube(ax):
    L, R, h = 15.0, 1.0, 0.1
    s = 1.0  # radial scale for display
    ax.add_patch(Rectangle((0, 0), L, R * s * 3, fc=FLUID, ec="none"))
    ax.add_patch(Rectangle((0, R * s * 3), L, h * s * 3, fc=SOLID, ec="none"))
    ax.plot([0, L], [0, 0], "-.", color="#555555", lw=0.7)
    ax.text(L / 2, -0.25, "axis of symmetry (wedge)", ha="center", va="top", fontsize=7)
    ax.text(L / 2, R * s * 1.5, "fluid", ha="center", va="center")
    ax.text(L / 2, R * s * 3 + h * s * 3 + 0.12, "elastic wall, traction-free outer surface",
            ha="center", va="bottom", color=SOLID, fontsize=7)
    ax.text(-0.2, R * s * 1.5, "inlet:\nexact\n$p$", ha="right", va="center", fontsize=7)
    ax.text(L + 0.2, R * s * 1.5, "outlet:\nexact\n$p$", ha="left", va="center", fontsize=7)
    dim(ax, (0, -1.0), (L, -1.0), "$L=15$ m", off=(0, -0.3))
    dim(ax, (L + 2.3, 0), (L + 2.3, R * s * 3), "$R=1$ m", off=(0.0, 0), rotation=90, bbox=dict(fc="white", ec="none", pad=0.5))
    ax.set_xlim(-2.6, L + 3.6); ax.set_ylim(-1.7, 4.1)
    ax.set_title("(c) womersleyTube (axisymmetric): wall thickness $h=0.1$ m (radius $\\times3$)", fontsize=8)


def channel(ax):
    Lu, L, Ld, a, h = 5.0, 10.0, 10.0, 1.0, 0.05
    sy = 3.0  # vertical scale for display
    ax.add_patch(Rectangle((0, 0), Lu + L + Ld, a * sy, fc=FLUID, ec="none"))
    ax.plot([0, Lu + L + Ld], [0, 0], color=EDGE, lw=1.4)
    ax.plot([0, Lu], [a * sy] * 2, color=EDGE, lw=1.4)
    ax.plot([Lu + L, Lu + L + Ld], [a * sy] * 2, color=EDGE, lw=1.4)
    x = np.linspace(Lu, Lu + L, 200)
    w = -0.28 * sy * np.sin(np.pi * (x - Lu) / L) ** 2
    ax.fill_between(x, a * sy + w, a * sy + w + 0.12, color=SOLID, lw=0)
    ax.plot([Lu, Lu + L], [a * sy + 0.06] * 2, ":", color="#555555", lw=0.6)
    for xi in np.linspace(Lu + 2, Lu + L - 2, 4):
        ax.add_patch(FancyArrowPatch((xi, a * sy + 0.9), (xi, a * sy + 0.3),
                                     arrowstyle="->", mutation_scale=6, lw=0.6))
    ax.text(Lu + L / 2, a * sy + 1.05, "$p_{ext}$ (ramped)", ha="center", fontsize=7)
    ax.text(-0.3, a * sy / 2, "$p_{in}$,\nparallel", ha="right", va="center", fontsize=7)
    ax.text(Lu + L + Ld + 0.3, a * sy / 2, "$p=0$,\nparallel", ha="left", va="center", fontsize=7)
    ax.text(Lu + L + Ld / 2, a * sy / 2, "fluid", ha="center", va="center")
    ax.text(Lu + L / 2, a * sy * 0.35, "elastic wall (clamped ends)", ha="center",
            color=SOLID, fontsize=7)
    dim(ax, (0, -0.6), (Lu, -0.6), "$L_{up}=5$", off=(0, -0.4))
    dim(ax, (Lu, -0.6), (Lu + L, -0.6), "$L=10$", off=(0, -0.4))
    dim(ax, (Lu + L, -0.6), (Lu + L + Ld, -0.6), "$L_{down}=10$", off=(0, -0.4))
    ax.set_xlim(-3.0, Lu + L + Ld + 3.0); ax.set_ylim(-1.6, a * sy + 1.5)
    ax.set_title("(d) collapsibleChannel: width $a=1$ m, wall $h=0.05$ m (width $\\times3$)", fontsize=8)


def mok(ax):
    ax.add_patch(Rectangle((0, 0), 1, 1, fc=FLUID, ec="none"))
    ax.plot([0, 0], [0, 0.875], color=EDGE, lw=1.4)
    ax.plot([1, 1], [0, 0.875], color=EDGE, lw=1.4)
    ax.plot([0, 1], [1, 1], color="#1f77b4", lw=2.2)
    x = np.linspace(0, 1, 100)
    ax.fill_between(x, -0.02 - 0.0, 0.0, color=SOLID, lw=0)
    ax.plot(x, -0.25 * np.sin(np.pi * x) ** 2 - 0.01, ":", color=SOLID, lw=0.7)
    ax.plot(0.5, 0, "ko", ms=3); ax.text(0.53, 0.04, "A", fontsize=7)
    for y in (0.9, 0.94, 0.98):
        ax.add_patch(FancyArrowPatch((-0.12, y), (-0.01, y), arrowstyle="->",
                                     mutation_scale=5, lw=0.6, color="#2ca02c"))
    ax.add_patch(FancyArrowPatch((1.01, 0.94), (1.12, 0.94), arrowstyle="->",
                                 mutation_scale=5, lw=0.6, color="#9467bd"))
    ax.text(0.5, 1.06, r"lid $v_x=1-\cos(2\pi t/5)$", ha="center", fontsize=7)
    ax.text(-0.14, 0.82, "inflow", ha="right", fontsize=7, color="#2ca02c")
    ax.text(1.14, 0.82, "$p=0$", ha="left", fontsize=7, color="#9467bd")
    ax.text(0.5, 0.55, "fluid", ha="center")
    ax.text(0.5, -0.36, "membrane, $h=0.002$ m, $E_S=250$ Pa (clamped)",
            ha="center", color=SOLID, fontsize=7)
    dim(ax, (1.22, 0.875), (1.22, 1.0), "", )
    ax.text(1.27, 0.94, "0.125", fontsize=6.5, va="center")
    dim(ax, (0, -0.5), (1, -0.5), "1 m", off=(0, -0.06))
    ax.set_xlim(-0.5, 1.5); ax.set_ylim(-0.62, 1.15)
    ax.set_title("(b) mokLidDrivenCavity", fontsize=8)


fig = plt.figure(figsize=(7.0, 7.4))
gs = fig.add_gridspec(3, 2, height_ratios=[1.35, 0.75, 0.75])
for f, spec in ((ring, gs[0, 0]), (mok, gs[0, 1]), (tube, gs[1, :]), (channel, gs[2, :])):
    ax = fig.add_subplot(spec); f(ax); ax.set_aspect("equal"); ax.axis("off")
fig.tight_layout()
fig.savefig(sys.argv[1] if len(sys.argv) > 1 else "benchmarks_geometry_panel.pdf")
