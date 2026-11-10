"""collapsibleChannel fluid-mesh study figure for the verification paper
(fig:collapsible_mesh): (a) wall-midpoint vertical displacement for fluid
levels F1-F4 against the oomph-lib reference at the same time step; (b, c)
zooms at the first trough and the second peak; (d) maximum error against the
reference, as a percentage of the reference peak, against the number of
fluid cells, with the reference uncertainty marked.

Usage: collapsible_mesh_figure.py HIST_DIR REF_CSV REF_CONVERGED_CSV OUT.pdf [UNCERTAINTY [LABEL]]
  HIST_DIR: F1.dat ... F4.dat (solidPointDisplacement_wallMid.dat of each level)
    and mesh_study.csv of the tutorial driver (fluid cell counts)
  REF_CSV: oomph-lib solution at the same time step (collapsibleChannel_oomph_dt160.csv)
  REF_CONVERGED_CSV: converged reference (collapsibleChannel_oomph_reference.csv),
    whose peak normalises the error, as in the tutorial driver
  UNCERTAINTY: uncertainty of REF_CSV in % of the peak (default 0.3, the
    tutorial reference at --refine 1)
  LABEL: label of the shaded band in (d) (default "reference uncertainty")
Prints the per-level maximum error."""
import bisect, csv, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.size": 8, "mathtext.fontset": "cm",
                     "font.family": "serif", "pdf.fonttype": 42})
hist_dir, ref_csv, conv_csv, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
# Fluid cells per level from the driver's study CSV (the levels are not a
# uniform ratio-2 family: 3200, 12800, 28800, 51200)
CELLS = {int(row["fluidLevel"]): int(row["fluidCells"])
         for row in csv.DictReader(open(hist_dir / "mesh_study.csv"))}
REF_UNCERTAINTY = float(sys.argv[5]) if len(sys.argv) > 5 else 0.3   # % of the peak
BAND_LABEL = sys.argv[6] if len(sys.argv) > 6 else "reference uncertainty"


def ref(path):
    rows = list(csv.DictReader(l for l in open(path) if not l.startswith("#")))
    return [(float(r["time"]), float(r["wallMid"])) for r in rows]


def hist(path):
    v = {}
    for line in open(path):
        if line.startswith("#"):
            continue
        f = line.split()
        v[round(float(f[0]), 10)] = float(f[2])
    return sorted(v.items())


def interp(c, t):
    ts = [p[0] for p in c]
    i = min(max(bisect.bisect_left(ts, t), 1), len(c) - 1)
    (a, u), (b, w) = c[i - 1], c[i]
    return u + (w - u) * (t - a) / (b - a)


r = ref(ref_csv)
scale = max(abs(v) for _, v in ref(conv_csv))
runs = {l: hist(hist_dir / f"F{l}.dat") for l in CELLS}
err = {}
for l, c in runs.items():
    err[l] = 100 * max(abs(u - interp(r, t)) for t, u in c if t <= r[-1][0]) / scale
    print(f"F{l}: {CELLS[l]} cells, max error {err[l]:.3f}% of the reference peak")

fig = plt.figure(figsize=(7.2, 4.8))
gs = fig.add_gridspec(2, 3, height_ratios=[1.15, 1], hspace=0.42, wspace=0.42,
                      left=0.1, right=0.98, bottom=0.09, top=0.95)
ax = fig.add_subplot(gs[0, :])
cols = {1: "#c6dbef", 2: "#6baed6", 3: "#2171b5", 4: "#08306b"}
curves = [(r, "#d62728", 1.8, "oomph-lib (same $\\Delta t$)")] + [
    (runs[l], cols[l], 0.9, f"F{l} ({CELLS[l]} cells)") for l in sorted(runs)]
for c, col, lw, lab in curves:
    ax.plot(*zip(*c), color=col, lw=lw, label=lab)
ax.set_xlabel("$t$ (s)"); ax.set_ylabel("wall-midpoint $u_y$ (m)")
ax.set_xlim(0, r[-1][0])
ax.set_title("(a) wall-midpoint displacement, fluid levels F1–F4 (solid $160\\times8$, high order)", fontsize=8)
ax.legend(fontsize=6.5, frameon=False, loc="upper right", ncol=1)
trough_t = min(r, key=lambda p: p[1])[0]
peak_t = max((p for p in r if p[0] > trough_t + 0.2), key=lambda p: p[1])[0]
w = 0.05
for k, (t0, title) in enumerate(((trough_t, "(b) first trough"), (peak_t, "(c) second peak"))):
    zx = fig.add_subplot(gs[1, k])
    for c, col, lw, _ in curves:
        seg = [p for p in c if t0 - w <= p[0] <= t0 + w]
        zx.plot(*zip(*seg), color=col, lw=lw)
    ys = [p[1] for c, *_ in curves for p in c if t0 - w <= p[0] <= t0 + w]
    pad = 0.06 * (max(ys) - min(ys))
    zx.set_xlim(t0 - w, t0 + w); zx.set_ylim(min(ys) - pad, max(ys) + pad)
    zx.set_xlabel("$t$ (s)"); zx.set_title(title, fontsize=8)
    if k == 0:
        zx.set_ylabel("$u_y$ (m)")
    ax.axvspan(t0 - w, t0 + w, color="0.85", lw=0, zorder=0)
bx = fig.add_subplot(gs[1, 2])
n = [CELLS[l] for l in sorted(CELLS)]
e = [err[l] for l in sorted(CELLS)]
bx.axhspan(0.01, REF_UNCERTAINTY, color="#d62728", alpha=0.08, lw=0)
bx.axhline(REF_UNCERTAINTY, color="#d62728", lw=0.6, ls="--")
bx.text(n[-1], REF_UNCERTAINTY * 0.9, BAND_LABEL.replace(" ", "\n", 1), color="#d62728", fontsize=6,
        ha="right", va="top")
bx.loglog(n, e, "o-", color="black", ms=3.5, lw=0.9, label="max error")
bx.loglog([n[0], n[2]], [e[0], e[0] * n[0] / n[2]], ":", color="0.4", lw=0.8, label="order 2")
for l, x, y in zip(sorted(CELLS), n, e):
    bx.annotate(f"F{l}", (x, y), textcoords="offset points", xytext=(3, 4), fontsize=6)
bx.set_xticks(n); bx.set_xticklabels([f"{v // 1000}k" if v % 1000 == 0 else str(v) for v in n],
                                     fontsize=6); bx.minorticks_off()
bx.set_xlabel("fluid cells"); bx.set_ylabel("max error (% of peak)")
bx.set_ylim(0.02, 8)
bx.set_yticks([0.05, 0.1, 0.2, 0.5, 1, 2, 5])
bx.set_yticklabels(["0.05", "0.1", "0.2", "0.5", "1", "2", "5"])
bx.set_title("(d) error against oomph-lib", fontsize=8)
bx.legend(fontsize=6, frameon=False, loc="upper right")
fig.savefig(out)
