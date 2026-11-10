"""Kratos against solids4foam on the same refinement sequence (16²/0.2, 32²/0.1, 64²/0.05, 96²/0.025).

Three series: Kratos with the openings fixed in space (the group-B definition), Kratos on the shipped
mesh (its opening nodes slide up the side walls with the mesh) and solids4foam.
Top row: peak, trough and mean of the membrane midpoint over t = 20-70 s, with the published group-B
range and the Richardson extrapolation of the fixed-openings Kratos runs. Bottom: midpoint histories over
the last two lid periods at one level, and the relative difference to solids4foam at every level.

Usage: pvpython plot_comparison.py <runs.csv> <orders.csv of the fixed-openings runs>
           <s4f statistics.csv> <kratos fixed history.csv> <kratos sliding history.csv>
           <s4f history.csv> <level label> <out.png>
<runs.csv> must contain both sets (the fix_openings column tells them apart).
"""
import csv
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

INK, INK2, GRID, BAND = "#1f1f1e", "#5f5e5a", "#e4e3df", "#efeeea"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"   # categorical slots 1-3, validated
LEVELS = [(16, 0.2), (32, 0.1), (64, 0.05), (96, 0.025)]
QOIS = [("peak", "Peak"), ("trough", "Trough"), ("mean", "Mean")]
SERIES = {  # name: colour, line style, marker
    "fixed": (BLUE, "-", "o", "Kratos, openings fixed (group B)"),
    "sliding": (AQUA, ":", "D", "Kratos, shipped mesh (openings slide)"),
    "s4f": (ORANGE, "--", "s", "solids4foam"),
}


def read_kratos(path, fixed):
    out = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            if (r["name"].startswith("n") and r["solid_y"] == "2" and r["tight"] == "False"
                    and r["outlet_uy0"] == "False" and r.get("fix_openings", "False") == str(fixed)):
                out[(int(r["n"]), float(r["dt"]))] = {q: float(r[q]) for q, _ in QOIS}
    return [out[lv] for lv in LEVELS]


def read_extrapolated(path):
    out = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            if r["study"].startswith("Combined") and r["triple"].startswith("32²"):
                out[r["qoi"]] = float(r["extrapolated_m"])
    return out


def read_s4f(path):
    stats, env = {}, {}
    with open(path) as f:
        for r in csv.DictReader(f):
            if r["variant"] == "legacy":
                stats[int(r["nx"])] = {q: float(r[q]) for q, _ in QOIS}
            elif r["variant"] == "groupB_envelope":
                env[r["nx"]] = (float(r["peak"]), float(r["trough"]))
    return [stats[n] for n, _ in LEVELS], env


def read_curve(path):
    out = []
    with open(path) as f:
        for line in f:
            p = line.strip().split(",")
            try:
                out.append((float(p[0]), float(p[2] if len(p) > 3 else p[1])))
            except (ValueError, IndexError):
                continue
    return out


def style(ax):
    ax.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def main():
    a = sys.argv[1:]
    data = {"fixed": read_kratos(a[0], True), "sliding": read_kratos(a[0], False)}
    extra = read_extrapolated(a[1])
    data["s4f"], env = read_s4f(a[2])
    hist = {"fixed": read_curve(a[3]), "sliding": read_curve(a[4]), "s4f": read_curve(a[5])}
    level_label, out = a[6], a[7]

    plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                         "xtick.color": INK2, "ytick.color": INK2, "axes.linewidth": 0.6,
                         "font.family": "sans-serif"})
    fig = plt.figure(figsize=(12.5, 8.0), dpi=150)
    fig.patch.set_facecolor("white")
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 0.95], hspace=0.42, wspace=0.34,
                          top=0.88)

    x = list(range(len(LEVELS)))
    ticks = [f"{n}²\nΔt {dt:g}" for n, dt in LEVELS]
    for col, (q, title) in enumerate(QOIS):
        ax = fig.add_subplot(gs[0, col])
        style(ax)
        ax.axhspan(*env[q], color=BAND, zorder=0)
        for name in ("sliding", "s4f", "fixed"):
            color, ls, marker, _ = SERIES[name]
            ax.plot(x, [v[q] for v in data[name]], linestyle=ls, marker=marker, color=color,
                    linewidth=2, markersize=6, markeredgecolor="white", markeredgewidth=1.0, zorder=3)
        ax.plot([3.25, 3.75], [extra[q]] * 2, "-", color=BLUE, linewidth=2.4, solid_capstyle="butt")
        ax.annotate(f"{extra[q]:.4f}", xy=(3.75, extra[q]), xytext=(3, 0), textcoords="offset points",
                    color=INK2, fontsize=7.5, va="center")
        ax.set_xticks(x)
        ax.set_xticklabels(ticks, fontsize=7.5)
        ax.set_xlim(-0.3, 4.3)
        ax.spines["bottom"].set_bounds(0, 3)
        ax.set_title(f"{title} of midpoint $u_y$ (m)", loc="left", color=INK, fontsize=10)

    handles = [Line2D([], [], color=c, linestyle=ls, marker=m, linewidth=2, markersize=6,
                      markeredgecolor="white", label=lab) for c, ls, m, lab in
               (SERIES["fixed"], SERIES["sliding"], SERIES["s4f"])]
    handles += [Line2D([], [], color=BLUE, linewidth=2.4, label="Kratos (fixed) extrapolated, 32²-96²"),
                Patch(facecolor=BAND, label="published group-B range")]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.06, 0.985), ncol=3, frameon=False,
               fontsize=8.5, labelcolor=INK, columnspacing=1.6, handlelength=2.6)

    # Histories at one level
    ax = fig.add_subplot(gs[1, :2])
    style(ax)
    ax.axhspan(*env["peak"], color=BAND, zorder=0)
    ax.text(70.2, sum(env["peak"]) / 2, "group-B\npeak range", color=INK2, fontsize=7.5,
            va="center", linespacing=1.0)
    for name in ("sliding", "s4f", "fixed"):
        color, ls, _, lab = SERIES[name]
        seg = [(t, u) for t, u in hist[name] if 59.99 <= t <= 70.01]
        t, u = zip(*seg)
        ax.plot(t, u, color=color, linestyle=ls, linewidth=1.8)
    ax.set_xlim(60, 72.6)
    ax.spines["bottom"].set_bounds(60, 70)
    ax.set_xticks([60, 62, 64, 66, 68, 70])
    ax.set_ylim(0.195, 0.295)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("midpoint $u_y$ (m)")
    ax.set_title(f"Membrane midpoint over the last two lid periods, {level_label}", loc="left",
                 color=INK, fontsize=10)

    # Relative difference to solids4foam per level
    ax = fig.add_subplot(gs[1, 2])
    style(ax)
    ax.axhline(0, color=INK2, linewidth=0.8)
    sliding_peak = [100 * (k["peak"] - s["peak"]) / s["peak"] for k, s in zip(data["sliding"], data["s4f"])]
    ax.plot(x, sliding_peak, ":D", color=AQUA, linewidth=1.6, markersize=4.5, markeredgecolor="white",
            markeredgewidth=0.8)
    ax.annotate(f"peak, shipped mesh {sliding_peak[-1]:+.1f}%", xy=(3, sliding_peak[-1]), xytext=(-4, -12),
                textcoords="offset points", color=INK, fontsize=7.5, va="center", ha="right")
    markers = {"peak": ("o", BLUE, -9), "trough": ("s", BLUE, 9), "mean": ("^", BLUE, 0)}
    for q, title in QOIS:
        d = [100 * (k[q] - s[q]) / s[q] for k, s in zip(data["fixed"], data["s4f"])]
        m, c, dy = markers[q]
        ax.plot(x, d, "-" + m, color=c, linewidth=1.4, markersize=5, markeredgecolor="white",
                markeredgewidth=0.8, alpha={"peak": 1.0, "trough": 0.75, "mean": 0.5}[q])
        ax.annotate(f"{title.lower()} {d[-1]:+.1f}%", xy=(3, d[-1]), xytext=(7, dy),
                    textcoords="offset points", color=INK, fontsize=7.5, va="center",
                    bbox=dict(facecolor="white", edgecolor="none", pad=0.6))
    ax.set_xticks(x)
    ax.set_xticklabels(ticks, fontsize=7.5)
    ax.set_xlim(-0.3, 4.6)
    ax.spines["bottom"].set_bounds(0, 3)
    ax.set_ylim(-12.5, 7)
    ax.set_ylabel("Kratos vs solids4foam (%)")
    ax.set_title("Difference to solids4foam", loc="left", color=INK, fontsize=10)

    fig.text(0.01, 0.005, "Statistics over t = 20-70 s with the solids4foam driver's periodic_stats. "
             "Same sequence in both codes; extrapolation after Celik et al. (2008).",
             color=INK2, fontsize=7.5)
    fig.savefig(out, facecolor="white", bbox_inches="tight", pad_inches=0.15)
    print("wrote", out)


if __name__ == "__main__":
    main()
