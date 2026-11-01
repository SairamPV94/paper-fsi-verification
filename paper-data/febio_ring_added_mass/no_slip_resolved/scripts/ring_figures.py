#!/usr/bin/env python3
"""Manuscript figures R1-R5 for the FEBio ringAddedMass comparison, from stored results only.
Run from anywhere: python3 -I ring_figures.py ; writes figures/ringAddedMass_febio_R{1..5}.png and a data dump."""
import json, math, csv, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"; REF = os.path.dirname(PKG.rstrip("/")) + "/reference/"; O = PKG + "results/"; OUT = PKG + "figures/"; os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.dirname(PKG.rstrip("/")) + "/tools"); import analyze_ring as AR
J = json.load(open(REF + "s4f_ringAddedMass/verification/reference/ringAddedMass_verification_references.json"))["exact"]["levels"]
LV = ["weak", "moderate", "strong"]
def refs(l):
    v = J[l]; s = v["viscousOmega"]; z = v["viscousDampingRatio"]
    return dict(A=v["ratio"], V=v["ratio"] * (1 + v["viscousFrequencyShift"]), alpha=z * s / math.sqrt(1 - z * z), omega=v["omega"], omegaV=s)
tab = {r["id"]: r for r in json.load(open(O + "ring_final_table.json"))}
# solids4foam ratio errors against A (PR #13 data supplied by P. Cardiff; QM = quasi-monolithic, IQN-ILS = partitioned)
s4f = {}
for x in csv.DictReader(open(PKG + "reference/ringAddedMass_monolithic_mesh_ff150e4.csv")):
    n = x["name"]
    if not n.startswith("wet_"): continue
    lvl = n.split("_")[1]; kind = "QM" if "monolithic" in n else "IQN-ILS"
    s4f.setdefault((lvl, kind), {})[int(x["factor"])] = 100 * float(x["ratio_error"])
plt.rcParams.update({"font.size": 9})

# ---- R1: ratio error per regime
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
x = np.arange(3); w = 0.16
for k, (rid, lab, col) in enumerate([("1", "FEBio f1", "#1b9e77"), ("2", "FEBio f2", "#66a61e")]):
    ax[0].bar(x + (k - 1.5) * w, [tab[f"P{l[0]}{rid}"]["errA_pct"] for l in LV], w, color=col, label=lab + ", no-slip, error vs inviscid A")
    ax[0].bar(x + (k + 0.5) * w, [tab[f"P{l[0]}{rid}"]["errV_pct"] for l in LV], w, color=col, alpha=0.45, hatch="//", label=lab + ", error vs finite-viscosity V")
for i, l in enumerate(LV):
    ax[0].plot([i - 2 * w, i + 2 * w], [100 * (refs(l)["V"] / refs(l)["A"] - 1)] * 2, "k:", lw=1)
ax[0].plot([], [], "k:", label="V relative to A (viscous shift)")
ax[0].set_xticks(x); ax[0].set_xticklabels(["weak\n$m^*=0.101$", "moderate\n$m^*=1.008$", "strong\n$m^*=10.08$"]); ax[0].axhline(0, color="gray", lw=0.5)
ax[0].set_ylabel("wet/dry frequency ratio error (%)"); ax[0].legend(fontsize=6.5, loc="lower left"); ax[0].set_title("FEBio, resolved no-slip, fluid at rest (tutorial start)")
for k, (kind, col, mk) in enumerate([("QM", "#555555", "^"), ("IQN-ILS", "#aaaaaa", "v")]):
    for fac, ls in ((1, "-"), (2, "--"), (4, ":")):
        ax[1].plot(x, [s4f[(l, kind)][fac] for l in LV], mk + ls, color=col, ms=5, label=f"solids4foam {kind}, mesh {fac}")
ax[1].set_xticks(x); ax[1].set_xticklabels(["weak", "moderate", "strong"]); ax[1].axhline(0, color="gray", lw=0.5)
ax[1].set_ylabel("ratio error vs inviscid A (%)"); ax[1].set_title("solids4foam (Stokes layer unresolved), standard solid", fontsize=9); ax[1].legend(fontsize=6.5)
fig.tight_layout(); fig.savefig(OUT + "ringAddedMass_febio_R1.png", dpi=200); plt.close(fig)

# ---- R2: mesh convergence: absolute wet frequency and wet/dry ratio
fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
cols = {"weak": "#1b9e77", "moderate": "#d95f02", "strong": "#7570b3"}
for l in LV:
    r = refs(l); ids = [f"P{l[0]}1", f"P{l[0]}2"]
    ax[0].plot([1, 2], [(tab[k]["omega"] / r["omegaV"] - 1) * 100 for k in ids], "o-", color=cols[l], label=f"FEBio, {l}", ms=6 if l != "moderate" else 4)
ax[0].set_xscale("log", base=2); ax[0].set_yscale("log"); ax[0].set_xticks([1, 2]); ax[0].set_xticklabels(["1", "2"])
ax[0].set_xlabel("ring and tangential refinement factor (first cell $\\delta/4$, 52 radial cells)"); ax[0].set_ylabel(r"wet $\omega$ error vs finite-viscosity $\omega$ (%)")
ax[0].set_title("Absolute frequency (the common error is the hex8 ring)", fontsize=9); ax[0].legend(fontsize=7)
for l in LV:
    r = refs(l); ids = [f"P{l[0]}1", f"P{l[0]}2"]
    ax[1].plot([1, 2], [tab[k]["errV_pct"] for k in ids], "o-", color=cols[l], label=f"FEBio {l}: error vs V")
    ax[1].plot([1, 2, 4], [s4f[(l, "QM")][f] for f in (1, 2, 4)], "^--", color=cols[l], alpha=0.55, ms=4, label=f"solids4foam QM {l}: error vs A")
ax[1].set_xscale("log", base=2); ax[1].set_xticks([1, 2, 4]); ax[1].set_xticklabels(["1", "2", "4"]); ax[1].axhline(0, color="gray", lw=0.5)
ax[1].set_xlabel("mesh refinement factor (the two discretisations differ)"); ax[1].set_ylabel("wet/dry ratio error (%)"); ax[1].legend(fontsize=6.2, ncol=2)
ax[1].set_title("Wet/dry ratio", fontsize=9)
fig.tight_layout(); fig.savefig(OUT + "ringAddedMass_febio_R2.png", dpi=200); plt.close(fig)

# ---- R3: displacement histories and damping
fig, ax = plt.subplots(1, 3, figsize=(11, 3.4), sharey=True)
for i, l in enumerate(LV):
    r = refs(l); T = 2 * math.pi / r["omega"]; t, d, v = AR.series(O + f"runs/P{l[0]}1/probes.txt")
    k0 = int(np.argmax(np.abs(d[: int(len(d) / 4)]))); a0 = np.abs(d[k0])
    ax[i].plot(t / T, d / a0, color="#1b9e77", lw=0.8, label="FEBio f1, rest start")
    tt = np.linspace(t[k0], t[-1], 100); ax[i].plot(tt / T, np.exp(-r["alpha"] * (tt - t[k0])), "k--", lw=1, label=r"$\exp(-\alpha_V t)$ (exact viscous)")
    ax[i].plot(tt / T, -np.exp(-r["alpha"] * (tt - t[k0])), "k--", lw=1)
    ax[i].set_xlabel("t / T"); ax[i].set_title(f"{l}: fitted decay {tab[f'P{l[0]}1']['alpha_over_V']:.3f} $\\alpha_V$", fontsize=9)
ax[0].set_ylabel("D(t) / first peak"); ax[0].legend(fontsize=6.5)
fig.tight_layout(); fig.savefig(OUT + "ringAddedMass_febio_R3.png", dpi=200); plt.close(fig)

# ---- R4: interface traction: pressure, shear measured vs thin-layer estimate
fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
tj = {k: json.load(open(O + f"analysis/{k}.traction.json")) for k in ("Pw1", "Pm1", "Ps1", "Ds")}
names = ["Pw1", "Pm1", "Ps1", "Ds"]; lab = ["weak\n(rest)", "moderate\n(rest)", "strong\n(rest)", "strong\n(compatible)"]
x = np.arange(4); w = 0.27
ax[0].bar(x - w, [tj[k]["pressure_traction_n2_amp_Pa"] for k in names], w, label="pressure traction, n=2 (nodal e)")
ax[0].bar(x, [tj[k]["viscous_tangential_traction_n2_amp_Pa"] for k in names], w, label="viscous shear, n=2 (measured)")
ax[0].bar(x + w, [tj[k]["thin_layer_shear_estimate_Pa"] for k in names], w, label="thin-Stokes-layer shear estimate")
ax[0].set_yscale("log"); ax[0].set_xticks(x); ax[0].set_xticklabels(lab); ax[0].set_ylabel("traction amplitude on the ring (Pa)"); ax[0].legend(fontsize=6.5)
ax[0].set_title("Traction amplitudes (reconstructed from logged fields)", fontsize=9)
z = np.load(O + "analysis/Ds.traction.npz"); e = np.load(O + "analysis/Ds.energy.npz"); Er = e["KEr"] + e["PEr"]
ax[1].plot(z["t"], Er - Er[0], label="ring energy change", lw=1.6); ax[1].plot(z["t"], z["Wtr"], "--", label="work of reconstructed traction (pressure + shear)", lw=1.2)
ax[1].plot(z["t"], z["Wv"] * 50, ":", label="viscous part x 50", lw=1)
ax[1].set_xlabel("t (s)"); ax[1].set_ylabel("J per metre of slab thickness"); ax[1].legend(fontsize=6.5); ax[1].set_title("Strong regime, compatible start: ring energy against traction work", fontsize=9)
fig.tight_layout(); fig.savefig(OUT + "ringAddedMass_febio_R4.png", dpi=200); plt.close(fig)

# ---- R5: energy balance (compatible start, resolved)
fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
for a, (path, ttl) in zip(ax, [(O + "analysis/Ds.energy.npz", "strong, first cell $\\delta/4$ (Ds)"), (O + "earlier_pilot/F2.npz", "moderate, first cell $\\delta/4$ (F2)")]):
    q = np.load(path); t = q["t"]; E0 = q["Etot"][0]
    a.plot(t / t[-1] * 4, q["Etot"] / E0, label="E_tot / E0"); a.plot(t / t[-1] * 4, (q["Etot"] + q["Wdiss"]) / E0, label="(E_tot + W_diss) / E0")
    a.plot(t / t[-1] * 4, 1 - q["Wdiss"] / E0 * 0 - (q["Wdiss"] / E0), ":", color="gray", label="1 - W_diss / E0 (energy expected from dissipation alone)")
    a.set_xlabel("t / T (4 periods)"); a.set_title(ttl, fontsize=9); a.set_ylim(0.93, 1.02); a.legend(fontsize=6.5)
ax[0].set_ylabel("energy / initial energy")
fig.tight_layout(); fig.savefig(OUT + "ringAddedMass_febio_R5.png", dpi=200); plt.close(fig)
print("R1-R5 written")
