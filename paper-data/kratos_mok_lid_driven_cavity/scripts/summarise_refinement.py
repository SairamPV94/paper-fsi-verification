#!/usr/bin/env python3
"""Statistics, observed orders and differences for the Kratos cavity refinement runs.

Statistics use periodic_stats and history_difference from the solids4foam driver, so the
QoI definitions are identical to the paper's solids4foam study (t = 20-70 s, period 5 s).
Observed orders follow Celik et al. (2008, J. Fluids Eng. 130, 078001): three members,
general refinement ratios, Richardson extrapolation and the fine-grid GCI (safety factor 1.25).

Usage: summarise_refinement.py <driver.py> <runs dir> <solids4foam paper-data dir> <out dir> [--fix-openings]
--fix-openings summarises the runs with the openings fixed in space (the group-B definition); without it,
the runs on the shipped mesh, whose openings slide along the side walls with the mesh.
Missing runs are skipped, so it can be run while the campaign is still going.
"""
import csv
import importlib.util
import json
import math
import os
import re
import sys

START, END, PERIOD = 20.0, 70.0, 5.0
FIX = False   # set from --fix-openings in main()
QOIS = ("peak", "trough", "mean")
# Changes below this are treated as noise: ten times the 1e-6 m coupling tolerance, and above
# the 2.2e-6 m thread-count and solid-mesh differences seen at level 1
NOISE_M = 1e-5


def load_driver(path):
    spec = importlib.util.spec_from_file_location("mokdriver", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_csv_curve(path):
    out = []
    with open(path) as f:
        for line in f:
            parts = line.strip().split(",")
            try:
                out.append((float(parts[0]), float(parts[1])))
            except (ValueError, IndexError):
                continue
    return out


def run_record(drv, run_dir):
    hist = os.path.join(run_dir, "history.csv")
    if not os.path.exists(hist) or not os.path.exists(os.path.join(run_dir, "run_info.json")):
        return None
    with open(hist) as f:
        rows = list(csv.DictReader(f))
    if not rows or float(rows[-1]["time"]) < END - 1e-6:
        return None
    curve = [(float(r["time"]), float(r["uy_mid"])) for r in rows]
    st = drv.periodic_stats(curve, START, END, PERIOD)
    info = json.load(open(os.path.join(run_dir, "run_info.json")))
    case = {}
    if os.path.exists(os.path.join(run_dir, "case.json")):
        case = json.load(open(os.path.join(run_dir, "case.json")))
    rss = None
    tt = os.path.join(run_dir, "time.txt")
    if os.path.exists(tt):
        m = re.search(r"Maximum resident set size \(kbytes\): (\d+)", open(tt).read())
        rss = int(m.group(1)) / 1024 if m else None
    solves = [int(r["coupling_solves"]) for r in rows]
    # Settling: spread of the per-cycle peaks over the last eight cycles
    cyc = []
    c = START
    while c + PERIOD <= END + 1e-9:
        w = [u for t, u in curve if c <= t < c + PERIOD]
        cyc.append(max(w))
        c += PERIOD
    return {
        "name": os.path.basename(run_dir.rstrip("/")),
        "n": case.get("n", 32), "dt": case.get("dt", 0.1), "solid_y": case.get("solid_y", 2),
        "nl_tol": case.get("nl_tol", 1e-6), "tight": case.get("tight", False),
        "outlet_uy0": case.get("outlet_uy0", False),
        "fix_openings": case.get("fix_openings", False),
        "dynamic_tau": 1.0 if case.get("dynamic_tau") is None else float(case["dynamic_tau"]),
        "peak": st["peak"], "trough": st["trough"], "mean": st["mean"],
        "phase": st["peak_phase"], "cycles": st["cycles"],
        "late_cycle_spread": max(cyc[2:]) - min(cyc[2:]),
        "steps": len(rows), "solves_mean": sum(solves) / len(solves), "solves_max": max(solves),
        "not_converged": sum(1 for r in rows if r["converged"] != "1"),
        "max_residual": max(float(r["rms_residual_at_acceptance"]) for r in rows),
        "wall_s": info["wall_total_s"], "threads": info["kratos_threads"], "rss_mb": rss,
        "curve": curve,
    }


def observed_order(levels):
    """levels: [(h, f)] ordered coarse to fine, exactly three. Returns dict."""
    (h3, f3), (h2, f2), (h1, f1) = levels
    r21, r32 = h2 / h1, h3 / h2
    e21, e32 = f2 - f1, f3 - f2
    out = {"e21": e21, "e32": e32}
    if abs(e21) < NOISE_M and abs(e32) < NOISE_M:
        out.update(kind="below noise", p=math.nan, ext=math.nan, gci=math.nan)
        return out
    if e21 == 0 or e32 == 0:
        out.update(kind="no change", p=math.nan, ext=f1, gci=math.nan)
        return out
    s = math.copysign(1.0, e32 / e21)
    if s < 0:
        out.update(kind="oscillatory", p=math.nan, ext=math.nan, gci=math.nan)
        return out
    p, q = 1.0, 0.0
    for _ in range(200):
        p_new = abs(math.log(abs(e32 / e21)) + q) / math.log(r21)
        q = math.log((r21 ** p_new - s) / (r32 ** p_new - s))
        if abs(p_new - p) < 1e-10:
            p = p_new
            break
        p = p_new
    ext = (r21 ** p * f1 - f2) / (r21 ** p - 1)
    gci = 1.25 * abs(e21 / f1) / (r21 ** p - 1)
    out.update(kind="monotone", p=p, ext=ext, gci=gci)
    return out


def pick(records, **kw):
    for r in records:
        if all((abs(r[k] - v) < 1e-12 if isinstance(v, float) else r[k] == v) for k, v in kw.items()):
            return r
    return None


def base(**kw):
    d = dict(solid_y=2, nl_tol=1e-6, tight=False, outlet_uy0=False, fix_openings=FIX, dynamic_tau=1.0)
    d.update(kw)
    return d


def fmt_pct(x, scale):
    return f"{100 * x / scale:+.2f}%"


def study_table(title, members, hkey, lines):
    """members: [(label, h, record)] coarse to fine."""
    members = [m for m in members if m[2] is not None]
    if not members:
        lines.append(f"\n### {title}\n\nno completed members yet\n")
        return []
    finest = members[-1][2]
    lines.append(f"\n### {title}\n")
    lines.append("| member | peak (m) | trough (m) | mean (m) | phase (s) | change in peak | change in trough | change in mean |")
    lines.append("|---|---|---|---|---|---|---|---|")
    prev = None
    for label, h, r in members:
        ch = ["", "", ""] if prev is None else [fmt_pct(r[q] - prev[q], finest[q]) for q in QOIS]
        lines.append(f"| {label} | {r['peak']:.5f} | {r['trough']:.5f} | {r['mean']:.5f} | {r['phase']:.3f} | "
                     + " | ".join(ch) + " |")
        prev = r
    orders = []
    if len(members) >= 3:
        lines.append("")
        lines.append(f"| triple ({hkey}) | QoI | observed order | extrapolated (m) | finest - extrapolated | GCI fine |")
        lines.append("|---|---|---|---|---|---|")
        for k in range(len(members) - 2, 0, -1):
            trip = members[k - 1:k + 2]
            tag = ", ".join(m[0] for m in trip)
            for q in QOIS:
                o = observed_order([(m[1], m[2][q]) for m in trip])
                if o["kind"] == "monotone":
                    lines.append(f"| {tag} | {q} | {o['p']:.2f} | {o['ext']:.5f} | "
                                 f"{fmt_pct(trip[-1][2][q] - o['ext'], o['ext'])} | {100 * o['gci']:.2f}% |")
                else:
                    lines.append(f"| {tag} | {q} | {o['kind']} | | | |")
                orders.append((title, tag, q, o))
    return orders


def main():
    global FIX
    argv = [a for a in sys.argv[1:] if a != "--fix-openings"]
    FIX = len(argv) < len(sys.argv) - 1
    drv = load_driver(argv[0])
    runs_dir, s4f_dir, out_dir = argv[1], argv[2], argv[3]
    os.makedirs(out_dir, exist_ok=True)
    records = []
    for name in sorted(os.listdir(runs_dir)):
        if name.startswith("n") or name == "L1_omp8":
            r = run_record(drv, os.path.join(runs_dir, name))
            if r:
                records.append(r)

    # All runs
    cols = ["name", "n", "dt", "solid_y", "nl_tol", "tight", "outlet_uy0", "fix_openings", "dynamic_tau", "peak", "trough", "mean",
            "phase", "cycles", "late_cycle_spread", "steps", "solves_mean", "solves_max",
            "not_converged", "max_residual", "wall_s", "threads", "rss_mb"]
    with open(os.path.join(out_dir, "runs.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in records:
            w.writerow([r[c] for c in cols])

    gen = [r for r in records if r["name"] != "L1_omp8" and r["fix_openings"] == FIX]
    L = []
    L.append("# Kratos 10.3.0 cavity refinement, statistics over t = 20-70 s\n")
    L.append("Openings fixed in space at 0.875 <= y <= 1 (group-B definition).\n" if FIX else
             "Shipped Kratos mesh: the opening nodes slide along the side walls with the mesh.\n")
    L.append("## All runs\n")
    L.append("| run | fluid | solid | dt (s) | coupling tol | peak (m) | trough (m) | mean (m) | phase (s) | "
             "solves mean/max | steps over tol | max residual (m) | wall (min) | threads |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in gen:
        tol = f"{r['nl_tol']:g}" + (" tight" if r["tight"] else "")
        extra = (" outlet u_y=0" if r["outlet_uy0"] else "") + (" fixed openings" if r["fix_openings"] else "")
        extra += " dynamic_tau 0" if r["dynamic_tau"] == 0 else ""
        L.append(f"| {r['name']} | {r['n']}²{extra} | {r['n']}x{r['solid_y']} | {r['dt']:g} | {tol} | "
                 f"{r['peak']:.5f} | {r['trough']:.5f} | {r['mean']:.5f} | {r['phase']:.3f} | "
                 f"{r['solves_mean']:.2f}/{r['solves_max']} | {r['not_converged']} | {r['max_residual']:.1e} | "
                 f"{r['wall_s'] / 60:.1f} | {r['threads']} |")

    L.append("\n## Studies\n")
    L.append("Changes are relative to the finest member of each study. Orders use the three members shown. 'below noise' means both changes are under 1e-5 m.")
    orders = []
    orders += study_table("Time step, 64² fluid, 2 solid elements through the thickness",
                          [(f"dt {dt:g}", dt, pick(gen, **base(n=64, dt=dt))) for dt in (0.1, 0.05, 0.025, 0.0125)],
                          "dt", L)
    if FIX:  # the dynamic_tau = 0 runs exist only with the openings fixed
        orders += study_table("Time step, 64², dynamic_tau = 0 (stabilisation independent of dt)",
                              [(f"dt {dt:g}", dt, pick(gen, **base(n=64, dt=dt, dynamic_tau=0.0)))
                               for dt in (0.1, 0.05, 0.025, 0.0125)], "dt", L)
    orders += study_table("Fluid mesh, dt 0.0125 s, solid refined along the membrane with the fluid",
                          [(f"{n}²", 1 / n, pick(gen, **base(n=n, dt=0.0125))) for n in (16, 32, 64, 128)],
                          "h", L)
    orders += study_table("Solid through the thickness, 64², dt 0.025 s",
                          [(f"{sy} elements", 1 / sy, pick(gen, **base(n=64, dt=0.025, solid_y=sy))) for sy in (2, 4, 8)],
                          "h_solid", L)
    combined_levels = ((16, 0.2), (32, 0.1), (64, 0.05), (96, 0.025))
    combined = [(f"{n}²/{dt:g}", 1 / n, pick(gen, **base(n=n, dt=dt))) for n, dt in combined_levels]
    orders += study_table("Combined refinement, same sequence as solids4foam", combined, "h", L)
    # Per-QoI values of the combined sequence and its extrapolation from 32², 64², 96², for a
    # level-by-level comparison with the solids4foam sequence
    if all(m[2] is not None for m in combined):
        with open(os.path.join(out_dir, "combined_sequence.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["qoi"] + [f"n{n}_dt{dt:g}_m" for n, dt in combined_levels]
                       + ["observed_order", "extrapolated_m", "gci_fine", "finest_minus_extrapolated"])
            for q in QOIS:
                o = observed_order([(m[1], m[2][q]) for m in combined[1:]])
                vals = [m[2][q] for m in combined]
                diff = (vals[-1] - o["ext"]) / o["ext"] if o["kind"] == "monotone" else math.nan
                w.writerow([q] + [f"{v:.6f}" for v in vals]
                           + [f"{o['p']:.3f}", f"{o['ext']:.6f}", f"{o['gci']:.5f}", f"{diff:.5f}"])

    # Coupling tolerance and outlet sensitivity, pairs
    L.append("\n### Coupling tolerance, 128², dt 0.0125 s\n")
    a = pick(gen, **base(n=128, dt=0.0125))
    b = pick(gen, n=128, dt=0.0125, solid_y=2, tight=True, fix_openings=FIX, dynamic_tau=1.0)
    if a and b:
        L.append("| setting | peak (m) | trough (m) | mean (m) | solves mean/max | max residual (m) |")
        L.append("|---|---|---|---|---|---|")
        for lab, r in (("nl_tol 1e-6, default solver tolerances", a), ("nl_tol 1e-8, all tolerances 100x tighter", b)):
            L.append(f"| {lab} | {r['peak']:.6f} | {r['trough']:.6f} | {r['mean']:.6f} | "
                     f"{r['solves_mean']:.2f}/{r['solves_max']} | {r['max_residual']:.1e} |")
        L.append(f"| difference | {fmt_pct(a['peak'] - b['peak'], b['peak'])} | {fmt_pct(a['trough'] - b['trough'], b['trough'])} | "
                 f"{fmt_pct(a['mean'] - b['mean'], b['mean'])} | | max history difference "
                 f"{drv.history_difference(a['curve'], b['curve'], START, END):.1e} m |")
    else:
        L.append("not complete yet")

    L.append("\n### Outlet sensitivity, u_y = 0 imposed on the outlet\n")
    L.append("| level | peak change | trough change | mean change | max history difference (m) |")
    L.append("|---|---|---|---|---|")
    for n, dt in ((32, 0.1), (64, 0.025)):
        a = pick(gen, **base(n=n, dt=dt))
        b = pick(gen, **base(n=n, dt=dt, outlet_uy0=True))
        if a and b:
            L.append(f"| {n}²/{dt:g} | {fmt_pct(b['peak'] - a['peak'], a['peak'])} | "
                     f"{fmt_pct(b['trough'] - a['trough'], a['trough'])} | {fmt_pct(b['mean'] - a['mean'], a['mean'])} | "
                     f"{drv.history_difference(b['curve'], a['curve'], START, END):.1e} |")

    # Kratos against solids4foam
    L.append("\n## Kratos against solids4foam at the same nominal levels\n")
    L.append("solids4foam values are recomputed from the paper-data histories with the same function. "
             "Difference = (Kratos - solids4foam) / solids4foam.\n")
    L.append("| level | code | peak (m) | trough (m) | mean (m) | phase (s) | max history difference (m) |")
    L.append("|---|---|---|---|---|---|---|")
    s4f_files = {(16, 0.2): "legacy0-mesh16.csv", (32, 0.1): "legacy-mesh32.csv",
                 (64, 0.05): "legacy-mesh64.csv", (96, 0.025): "legacy-mesh96.csv",
                 (64, 0.025): "strict-dt0.025.csv"}
    for (n, dt), fname in s4f_files.items():
        k = pick(gen, **base(n=n, dt=dt))
        sc = read_csv_curve(os.path.join(s4f_dir, fname))
        ss = drv.periodic_stats(sc, START, END, PERIOD)
        L.append(f"| {n}²/{dt:g} | solids4foam ({fname}) | {ss['peak']:.5f} | {ss['trough']:.5f} | {ss['mean']:.5f} | {ss['peak_phase']:.3f} | |")
        if k:
            L.append(f"| | Kratos | {k['peak']:.5f} | {k['trough']:.5f} | {k['mean']:.5f} | {k['phase']:.3f} | "
                     f"{drv.history_difference(k['curve'], sc, START, END):.4f} |")
            L.append(f"| | difference | {fmt_pct(k['peak'] - ss['peak'], ss['peak'])} | "
                     f"{fmt_pct(k['trough'] - ss['trough'], ss['trough'])} | {fmt_pct(k['mean'] - ss['mean'], ss['mean'])} | "
                     f"{k['phase'] - ss['peak_phase']:+.3f} | |")

    with open(os.path.join(out_dir, "summary.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(out_dir, "orders.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["study", "triple", "qoi", "kind", "order", "extrapolated_m", "gci_fine", "e21", "e32"])
        for study, tag, q, o in orders:
            w.writerow([study, tag, q, o["kind"], o["p"], o["ext"], o["gci"], o["e21"], o["e32"]])
    print("\n".join(L))


if __name__ == "__main__":
    main()
