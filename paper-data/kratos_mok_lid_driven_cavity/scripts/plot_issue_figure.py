"""One figure for the #36 comment: the membrane midpoint history over the last two lid periods at one
level, Kratos with the openings fixed (group B) against solids4foam.

Usage: pvpython plot_issue_figure.py <kratos history.csv> <s4f history.csv> <level label> <out.png>
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plot_comparison import INK, INK2, SERIES, read_curve, style  # noqa: E402


def main():
    kratos, s4f, level_label, out = read_curve(sys.argv[1]), read_curve(sys.argv[2]), sys.argv[3], sys.argv[4]
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                         "xtick.color": INK2, "ytick.color": INK2, "axes.linewidth": 0.6,
                         "font.family": "sans-serif"})
    fig, ax = plt.subplots(figsize=(8.0, 4.0), dpi=160)
    fig.patch.set_facecolor("white")
    style(ax)
    for name, data in (("s4f", s4f), ("fixed", kratos)):
        color, ls, _, _ = SERIES[name]
        label = "Kratos 10.3.0, openings fixed" if name == "fixed" else "solids4foam"
        seg = [(t, u) for t, u in data if 59.99 <= t <= 70.01]
        t, u = zip(*seg)
        ax.plot(t, u, color=color, linestyle=ls, linewidth=2.0, label=label)
    ax.set_xlim(60, 70)
    ax.set_xticks([60, 62, 64, 66, 68, 70])
    ax.set_ylim(0.195, 0.295)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("midpoint $u_y$ (m)")
    ax.set_title(f"Membrane midpoint over the last two lid periods, {level_label}", loc="left",
                 color=INK, fontsize=10.5)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2,
              frameon=False,
              fontsize=9.5, labelcolor=INK, handlelength=2.8, columnspacing=2.4)
    fig.savefig(out, facecolor="white", bbox_inches="tight", pad_inches=0.15)
    print("wrote", out)


if __name__ == "__main__":
    main()
