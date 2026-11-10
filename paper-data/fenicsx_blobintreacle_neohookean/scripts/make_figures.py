"""Figures S1 and S2 of the neo-Hookean blobInTreacle supplement, from data/*.csv.
Usage (from this directory): python3 -B -I scripts/make_figures.py   (needs numpy and matplotlib; writes figures/*.pdf and *.png)"""
import csv, os, sys
sys.dont_write_bytecode = True
os.environ.setdefault("SOURCE_DATE_EPOCH", "1767225600")   # fixed PDF dates: byte-identical output
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.size": 8, "mathtext.fontset": "cm", "font.family": "serif", "pdf.fonttype": 42, "pdf.compression": 0, "svg.hashsalt": "nh"})
here = os.path.dirname(os.path.abspath(__file__))
data, figs = os.path.join(here, "..", "data"), os.path.join(here, "..", "figures")
rd = lambda n: list(csv.DictReader(open(os.path.join(data, n))))
BL, OR = "#0072B2", "#D55E00"
LV = ["0.5", "1", "2", "4"]; N = {"0.5": 150, "1": 600, "2": 2400, "4": 9600}
fe = {r["level"]: r for r in rd("fe_steady_levels.csv")}; s4 = {r["level"]: r for r in rd("s4f_rerun_steady.csv") if r["level"] in LV}
conv = {r["obs"]: r for r in rd("steady_convergence.csv")}
diff = rd("steady_matched_differences.csv")

fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.25))
h = [N[l] ** -0.5 for l in LV]
ax[0].plot(h, [float(fe[l]["ux"]) for l in LV], color=BL, marker="o", lw=1, ms=4, label="FEniCSx (steady, $t=6$)")
ax[0].plot(h, [float(s4[l]["ux"]) for l in LV], color=OR, marker="s", ls="--", lw=1, ms=4, label="solids4foam #694 rerun ($t=3$)")
ax[0].plot([0], [float(conv["ux"]["FE_limit"])], color=BL, marker="o", mfc="none", ms=6, ls="none")
ax[0].plot([0], [float(conv["ux"]["s4f_limit"])], color=OR, marker="s", mfc="none", ms=6, ls="none")
ax[0].set_xlabel(r"$h=N_\mathrm{cells}^{-1/2}$"); ax[0].set_ylabel("apex $u_x$ (m)"); ax[0].set_xlim(-0.005, 0.085); ax[0].grid(alpha=0.25, lw=0.4); ax[0].legend(frameon=False, fontsize=6.5, loc="lower left")
ax[0].set_title("(a) open symbols: estimated limits", fontsize=8)
mk = {"ux": ("o", "-"), "uy": ("s", "--"), "Fx": ("^", "-."), "Fy": ("v", ":"), "dp": ("D", "-")}
col = {"ux": "#0072B2", "uy": "#D55E00", "Fx": "#009E73", "Fy": "#CC79A7", "dp": "#555555"}
lab = {"ux": "$u_x$", "uy": "$|u_y|$", "Fx": "$F_x$", "Fy": "$|F_y|$", "dp": "$\\Delta p$"}
for k in ["ux", "uy", "Fx", "Fy", "dp"]:
    y = [abs(float([r for r in diff if r["level"] == l and r["obs"] == k][0]["diff_FE_t6_vs_s4f_pct"])) for l in LV]
    ax[1].loglog([N[l] for l in LV], y, color=col[k], marker=mk[k][0], ls=mk[k][1], lw=1, ms=4, label=lab[k])
ax[1].set_xlabel("cells $N$ (x0.5, x1, x2, x4)"); ax[1].set_ylabel("|difference| (%)"); ax[1].grid(alpha=0.25, lw=0.4, which="both"); ax[1].legend(frameon=False, fontsize=6.5, ncol=2, loc="lower left")
ax[1].set_title("(b) matched-level difference", fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(figs, "nh_steady.pdf")); fig.savefig(os.path.join(figs, "nh_steady.png"), dpi=200); plt.close(fig)

fet = rd("fe_time_study_t1.csv"); s4t = rd("s4f_rerun_time.csv"); ts = rd("time_study_t1.csv")
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.25))
x = [float(r["dt"]) for r in fet[1:]]; y = [float(r["dux"]) for r in fet[1:]]
ax[0].loglog(x, y, color=BL, marker="o", lw=1, ms=4, label="FEniCSx")
xs = [float(r["dt"]) for r in s4t[1:]]; ys = [float(r["dux"]) for r in s4t[1:]]
ax[0].loglog(xs, ys, color=OR, marker="s", ls="--", lw=1, ms=4, label="solids4foam rerun")
xx = np.array([0.0078125, 0.125]); ax[0].loglog(xx, 0.0003 * (xx / 0.125) ** 2 * 1.5, "k:", lw=0.8, label="slope 2")
ax[0].set_xlabel("finer $\\Delta t$ of the pair (s)"); ax[0].set_ylabel("$|\\Delta u_x(1)|$ between successive $\\Delta t$ (m)"); ax[0].grid(alpha=0.25, lw=0.4, which="both"); ax[0].legend(frameon=False, fontsize=6.5)
ax[0].set_title("(a) change of $u_x(t=1)$ (x1)", fontsize=8)
dts = [float(r["dt"]) for r in ts if r["ux_FE_vs_s4f_pct"] != ""]
ax[1].semilogx(dts, [float(r["ux_FE_vs_s4f_pct"]) for r in ts if r["ux_FE_vs_s4f_pct"] != ""], color=BL, marker="o", lw=1, ms=4, label="$u_x$")
ax[1].semilogx(dts, [float(r["uy_FE_vs_s4f_pct"]) for r in ts if r["uy_FE_vs_s4f_pct"] != ""], color=OR, marker="s", ls="--", lw=1, ms=4, label="$u_y$")
ax[1].semilogx(dts, [float(r["Fx_FE_vs_s4f_pct"]) for r in ts if r["Fx_FE_vs_s4f_pct"] != ""], color="#009E73", marker="^", ls="-.", lw=1, ms=4, label="$F_x$")
ax[1].set_ylim(0, 3); ax[1].set_xticks([0.03125, 0.0625, 0.125, 0.25]); ax[1].set_xticklabels(["0.03125", "0.0625", "0.125", "0.25"], fontsize=6.5); ax[1].minorticks_off(); ax[1].set_xlabel("$\\Delta t$ (s)"); ax[1].set_ylabel("FEniCSx vs solids4foam at $t=1$ (%)"); ax[1].grid(alpha=0.25, lw=0.4); ax[1].legend(frameon=False, fontsize=6.5)
ax[1].set_title("(b) difference at equal $\\Delta t$ (x1)", fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(figs, "nh_time.pdf")); fig.savefig(os.path.join(figs, "nh_time.png"), dpi=200); plt.close(fig)
