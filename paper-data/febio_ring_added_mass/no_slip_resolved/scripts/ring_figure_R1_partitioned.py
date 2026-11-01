#!/usr/bin/env python3
"""Figure ringAddedMass_febio_R1 (partitioned-only version) from stored results only.

Left : FEBio no-slip wet/dry frequency-ratio errors vs A (inviscid) and V (finite viscosity),
       read from results/ring_final_table.json.
Right: solids4foam IQN-ILS (partitioned) ratio errors vs A at mesh factors 1, 2, 4, read from
       reference/ringAddedMass_monolithic_mesh_ff150e4.csv (rows wet_*_iqnils_*; the
       quasi-monolithic rows in the same file are deliberately NOT used).

Expects the PR #26 package layout (this file in <pkg>/scripts/, <pkg>/results/, <pkg>/reference/) and the
parent package's reference/s4f_ringAddedMass/... JSON. No simulation is run.
Usage: python3 -I ring_figure_R1_partitioned.py [output.png]
Default output: <repository root>/figures/verification/ringAddedMass_febio_R1.png
"""
import csv, json, math, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"
PARENT = os.path.dirname(PKG.rstrip("/")) + "/"
REPO = os.path.dirname(os.path.dirname(PARENT.rstrip("/"))) + "/"
OUT = sys.argv[1] if len(sys.argv) > 1 else REPO + "figures/verification/ringAddedMass_febio_R1.png"
J = json.load(open(PARENT + "reference/s4f_ringAddedMass/verification/reference/ringAddedMass_verification_references.json"))["exact"]["levels"]
LV = ["weak", "moderate", "strong"]
tab = {r["id"]: r for r in json.load(open(PKG + "results/ring_final_table.json"))}

s4f = {}
for x in csv.DictReader(open(PKG + "reference/ringAddedMass_monolithic_mesh_ff150e4.csv")):
    n = x["name"]
    if n.startswith("wet_") and "iqnils" in n:
        s4f.setdefault(n.split("_")[1], {})[int(x["factor"])] = 100 * float(x["ratio_error"])  # fraction -> %
for l in LV:
    assert sorted(s4f[l]) == [1, 2, 4], l

plt.rcParams.update({"font.size": 9})
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
x = np.arange(3); w = 0.16
for k, (rid, lab, col) in enumerate([("1", "FEBio f1", "#1b9e77"), ("2", "FEBio f2", "#66a61e")]):
    ax[0].bar(x + (k - 1.5) * w, [tab[f"P{l[0]}{rid}"]["errA_pct"] for l in LV], w, color=col, label=lab + ", no-slip, error vs inviscid A")
    ax[0].bar(x + (k + 0.5) * w, [tab[f"P{l[0]}{rid}"]["errV_pct"] for l in LV], w, color=col, alpha=0.45, hatch="//", label=lab + ", error vs finite-viscosity V")
for i, l in enumerate(LV):
    v = J[l]
    ax[0].plot([i - 2 * w, i + 2 * w], [100 * v["viscousFrequencyShift"]] * 2, "k:", lw=1)  # V relative to A
ax[0].plot([], [], "k:", label="V relative to A (viscous shift)")
ax[0].set_xticks(x); ax[0].set_xticklabels(["weak\n$m^*=0.101$", "moderate\n$m^*=1.008$", "strong\n$m^*=10.08$"]); ax[0].axhline(0, color="gray", lw=0.5)
ax[0].set_ylabel("wet/dry frequency ratio error (%)"); ax[0].legend(fontsize=6.5, loc="lower left")
ax[0].set_title("FEBio, resolved no-slip, fluid at rest (tutorial start)")
for fac, ls in ((1, "-"), (2, "--"), (4, ":")):
    ax[1].plot(x, [s4f[l][fac] for l in LV], "v" + ls, color="#555555", ms=5, label=f"solids4foam IQN-ILS, mesh {fac}")
ax[1].set_xticks(x); ax[1].set_xticklabels(["weak", "moderate", "strong"]); ax[1].axhline(0, color="gray", lw=0.5)
ax[1].set_ylabel("ratio error vs inviscid A (%)")
ax[1].set_title("solids4foam IQN-ILS (partitioned), layer unresolved", fontsize=9)
ax[1].legend(fontsize=6.5)
fig.tight_layout(); os.makedirs(os.path.dirname(OUT), exist_ok=True); fig.savefig(OUT, dpi=200); plt.close(fig)
print("wrote", OUT)
for l in LV: print(l, {f: round(v, 5) for f, v in sorted(s4f[l].items())})
