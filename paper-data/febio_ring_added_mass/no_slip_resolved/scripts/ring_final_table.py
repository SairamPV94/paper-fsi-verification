#!/usr/bin/env python3
"""Final ringAddedMass table for the overnight-2 production runs, from stored reports (reproducible).
Writes results/ring_final_table.csv / .md / .json inside this package."""
import json, math, csv, os
import os
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"; REF = os.path.dirname(PKG.rstrip("/")) + "/reference/"; O = PKG + "results/"
J = json.load(open(REF + "s4f_ringAddedMass/verification/reference/ringAddedMass_verification_references.json"))["exact"]["levels"]
REG = {"w": "weak", "m": "moderate", "s": "strong"}
def refs(level):
    v = J[level]; s = v["viscousOmega"]; z = v["viscousDampingRatio"]
    return dict(A=v["ratio"], V=v["ratio"] * (1 + v["viscousFrequencyShift"]), alpha=z * s / math.sqrt(1 - z * z), omega=v["omega"], shift=v["viscousFrequencyShift"])
dry = {"f1": O + "dry/B1_dry_f1.json", "f2": O + "dry/D1_dry_f2.json", "dt": O + "dry/C1_dt200_dry_f1.json"}
runs = [("Pw1", "w", "f1", "rest", 100), ("Pw2", "w", "f2", "rest", 100), ("Pwt", "w", "f1", "rest", 200),
        ("Pm1", "m", "f1", "rest", 100), ("Pm2", "m", "f2", "rest", 100), ("Pmt", "m", "f1", "rest", 200),
        ("Ps1", "s", "f1", "rest", 100), ("Ps2", "s", "f2", "rest", 100), ("Pst", "s", "f1", "rest", 200),
        ("Ds", "s", "f1", "compat", 100)]
rows = []
for rid, rg, mesh, ic, spp in runs:
    p = O + f"runs/{rid}/report.json"
    if not os.path.exists(p):
        continue
    r = json.load(open(p)); ref = refs(REG[rg]); T = 2 * math.pi / ref["omega"]
    dk = "dt" if spp == 200 else mesh
    d = json.load(open(dry[dk]))["omega_fit"]; ratio = r["omega_fit"] / d
    a = -math.log(1 - r["amp_loss_per_period"]) / T
    tr = O + f"analysis/{rid}.traction.json"; t = json.load(open(tr)) if os.path.exists(tr) else {}
    rows.append(dict(id=rid, regime=REG[rg], mesh=mesh, ic=ic, steps_per_period=spp, omega=r["omega_fit"], dry_omega=d, ratio=ratio,
                     ratio_A=ref["A"], ratio_V=ref["V"], errA_pct=(ratio / ref["A"] - 1) * 100, errV_pct=(ratio / ref["V"] - 1) * 100,
                     alpha=a, alpha_V=ref["alpha"], alpha_over_V=a / ref["alpha"],
                     shear_n2_Pa=t.get("viscous_tangential_traction_n2_amp_Pa"), shear_thin_layer_est_Pa=t.get("thin_layer_shear_estimate_Pa"),
                     shear_meas_over_est=t.get("measured_over_estimate"), pressure_n2_Pa=t.get("pressure_traction_n2_amp_Pa"),
                     steps=r.get("steps_completed"), newton=r.get("avg_newton_iters_per_step")))
json.dump(rows, open(O + "ring_final_table.json", "w"), indent=1)
with open(O + "ring_final_table.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
md = "| ID | regime | mesh | IC | steps/T | omega | err vs A % | err vs V % | alpha/alpha_V | shear n=2 (Pa) | meas/thin-layer |\n|---|---|---|---|---|---|---|---|---|---|---|\n"
for x in rows:
    md += "| %s | %s | %s | %s | %d | %.5f | %.4f | %.4f | %.3f | %s | %s |\n" % (x["id"], x["regime"], x["mesh"], x["ic"], x["steps_per_period"], x["omega"], x["errA_pct"], x["errV_pct"], x["alpha_over_V"],
        "%.2e" % x["shear_n2_Pa"] if x["shear_n2_Pa"] else "n/a", "%.2f" % x["shear_meas_over_est"] if x["shear_meas_over_est"] else "n/a")
open(O + "ring_final_table.md", "w").write(md); print(md)
