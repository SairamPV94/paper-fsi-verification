"""mokLidDrivenCavity figure for the verification paper (fig:mok_refs):
(a) membrane-midpoint histories over the last four lid periods: the
published group-A and group-B curves and the solids4foam group-B solutions
with the strict coupling test; (b) peak, mean and trough over t = 20-70 s
against the fluid cells per side, legacy and strict coupling test, with the
published group-B envelope.

Usage: mok_figure.py REF_DIR RUN_DIR OUT.pdf
  REF_DIR: the tutorial's verification/reference directory (published curves)
  RUN_DIR: {legacy,strict}-mesh{N}.csv, columns t, u_y (m); the legacy series
    is the paper's mesh study, the strict points the same levels with the
    strict coupling test (requireAllResidualMeasures)
Prints the statistics of every run as CSV on stdout."""
import csv, json, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.size": 8, "mathtext.fontset": "cm",
                     "font.family": "serif", "pdf.fonttype": 42})
ref_dir, run_dir, out = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
cfg = json.loads((ref_dir / "mokLidDrivenCavity_verification_references.json").read_text())
T0, T1 = cfg["comparison_window_s"]
PERIOD = cfg["lid_period_s"]


def read(path):
    rows = []
    for line in path.read_text().splitlines():
        if line.startswith("#"):
            continue
        try:
            rows.append(tuple(float(v) for v in line.replace(",", " ").split()[:2]))
        except ValueError:
            continue
    return sorted(rows)


def interp(c, t):
    if t <= c[0][0]:
        return c[0][1]
    if t >= c[-1][0]:
        return c[-1][1]
    lo, hi = 0, len(c) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if c[mid][0] <= t else (lo, mid)
    (a, u), (b, v) = c[lo], c[hi]
    return u + (v - u) * (t - a) / (b - a)


def stats(c, start=T0, end=T1):
    """As periodic_stats in the tutorial driver: mean per-period peak and
    trough, and the time-mean over the window."""
    end = min(end, c[-1][0])
    peaks, troughs, s = [], [], start
    while s + PERIOD <= end + 1e-9:
        w = [u for t, u in c if s <= t < s + PERIOD]
        if len(w) >= 10:
            peaks.append(max(w)); troughs.append(min(w))
        s += PERIOD
    mean = sum(interp(c, start + (end - start) * i / 2000) for i in range(2001)) / 2001
    return dict(peak=sum(peaks) / len(peaks), trough=sum(troughs) / len(troughs), mean=mean)


refs = {k: v for k, v in cfg["references"].items()}
curves = {k: read(ref_dir / v["file"]) for k, v in refs.items() if "file" in v}
group_b = {k: (stats(curves[k]) if k in curves else refs[k]["values"])
           for k, v in refs.items() if v["group_b"]}
env = {q: (min(s[q] for s in group_b.values() if q in s),
           max(s[q] for s in group_b.values() if q in s)) for q in ("peak", "trough", "mean")}

runs = {}
for f in sorted(run_dir.glob("*-mesh*.csv")):
    variant, mesh = f.stem.split("-")
    runs[(variant, int(mesh[4:]))] = read(f)
w = csv.writer(sys.stdout)
w.writerow(["variant", "nx", "peak", "trough", "mean"])
table = {}
for (variant, nx), c in sorted(runs.items()):
    s = stats(c); table[(variant, nx)] = s
    w.writerow([variant, nx] + [f"{s[q]:.5f}" for q in ("peak", "trough", "mean")])
for q, (lo, hi) in env.items():
    w.writerow(["groupB_envelope", q, f"{lo:.4f}", f"{hi:.4f}", ""])

fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.2, 3.5), gridspec_kw=dict(width_ratios=[1.6, 1]))
t_show = (T1 - 4 * PERIOD, T1)
GA = dict(Mok2001="Mok (2001)", Wall1999="Wall (1999)", GerbeauVidrascu2003="Gerbeau & Vidrascu (2003)")
for (k, lab), ls in zip(GA.items(), ("-", "--", ":")):
    c = [p for p in curves[k] if t_show[0] <= p[0] <= t_show[1]]
    if c:
        ax.plot(*zip(*c), ls, color="#9a9a9a", lw=0.8, label=f"{lab} (A)")
c = [p for p in curves["Kassiotis2011"] if t_show[0] <= p[0] <= t_show[1]]
ax.plot(*zip(*c), "-.", color="#7f7f7f", lw=0.8, label="Kassiotis et al. (2011)")
for k, lab, col in (("Valdes2007", "Vald\\'es (2007) (B)", "#1f77b4"), ("Kratos", "Kratos (B)", "#2ca02c")):
    c = [p for p in curves[k] if t_show[0] <= p[0] <= t_show[1]]
    ax.plot(*zip(*c), color=col, lw=1.0, label=lab.replace("\\'e", "é"))
finest = max(nx for v, nx in runs if v == "legacy")
c = [p for p in runs[("legacy", finest)] if t_show[0] <= p[0] <= t_show[1]]
ax.plot(*zip(*c), color="black", lw=1.4, label=f"solids4foam ${finest}^2$ (B)")
ax.set_xlim(*t_show); ax.set_xlabel("$t$ (s)"); ax.set_ylabel("midpoint $u_y$ (m)")
ax.set_title("(a) membrane midpoint, last four lid periods", fontsize=8)
ax.legend(fontsize=6, ncol=3, loc="upper center", frameon=False, bbox_to_anchor=(0.5, -0.17))

for q, mk in (("peak", "o"), ("mean", "s"), ("trough", "v")):
    lo, hi = env[q]
    bx.axhspan(lo, hi, color="#1f77b4", alpha=0.12, lw=0)
    for variant, style in (("legacy", dict(mfc="black", ls="-", color="black")),
                           ("strict", dict(mfc="#d62728", ls="none", color="#d62728"))):
        pts = sorted((nx, s[q]) for (v, nx), s in table.items() if v == variant)
        if pts:
            bx.plot([1 / nx for nx, _ in pts], [y for _, y in pts], marker=mk, ms=3.5, lw=0.8,
                    label=("legacy test" if variant == "legacy" else "strict test") if q == "peak" else None, **style)
bx.set_xscale("log"); bx.set_xlabel("$1/n$ (fluid cells per side)")
nxs = sorted({nx for _, nx in table})
bx.set_xticks([1 / n for n in nxs]); bx.set_xticklabels([f"1/{n}" for n in nxs]); bx.minorticks_off()
bx.set_ylabel("$u_y$ (m): peak, mean, trough")
bx.set_title("(b) statistics over $t = %g$\u2013$%g$ s" % (T0, T1), fontsize=8)
for q in ("peak", "mean", "trough"):
    y = table[("legacy", max(nx for v, nx in table if v == "legacy"))][q]
    bx.annotate(q, (1 / max(nxs), y), textcoords="offset points", xytext=(-4, 5), fontsize=6, ha="left")
bx.plot([], [], color="#1f77b4", alpha=0.25, lw=6, label="published group B range")
bx.legend(fontsize=6, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=1)
fig.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.36, wspace=0.32)
fig.savefig(out)
