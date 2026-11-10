#!/usr/bin/env python3
"""Level-1 comparison for the Kratos cavity runs.

Statistics use periodic_stats, interpolate and history_difference imported from the
solids4foam driver (tutorials/fluidSolidInteraction/mokLidDrivenCavity/verification/
scripts/mok_lid_driven_cavity_verification.py), so the definitions are identical.

Usage: compare_level1.py <driver.py> <reference dir> <run dir> [<run dir> ...]
"""
import csv
import importlib.util
import json
import math
import statistics
import sys
from pathlib import Path


def load_driver(path):
    spec = importlib.util.spec_from_file_location("mokdriver", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_history(run):
    with open(Path(run) / "history.csv") as f:
        rows = list(csv.DictReader(f))
    curve = [(float(r["time"]), float(r["uy_mid"])) for r in rows]
    return rows, curve


def per_cycle_peaks(curve, start, end, period):
    out = []
    c = start
    while c + period <= end + 1e-9:
        w = [p for p in curve if c <= p[0] < c + period]
        out.append((c, max(v for _, v in w), min(v for _, v in w)))
        c += period
    return out


def main():
    drv = load_driver(sys.argv[1])
    ref_dir = Path(sys.argv[2])
    runs = sys.argv[3:]
    cfg = json.load(open(ref_dir / "mokLidDrivenCavity_verification_references.json"))
    start, end = cfg["comparison_window_s"]
    period = cfg["lid_period_s"]

    kratos_ref = drv.read_curve(ref_dir / cfg["references"]["Kratos"]["file"])
    ref_stats = drv.periodic_stats(kratos_ref, start, end, period)

    print(f"window {start}-{end} s, period {period} s\n")
    print(f"{'source':34s} {'peak':>8s} {'trough':>8s} {'mean':>8s} {'phase':>7s} cycles")
    print(f"{'Kratos example plot (digitised)':34s} {ref_stats['peak']:8.4f} {ref_stats['trough']:8.4f}"
          f" {ref_stats['mean']:8.4f} {ref_stats['peak_phase']:7.3f} {ref_stats['cycles']}")

    curves = {}
    for run in runs:
        rows, curve = read_history(run)
        curves[run] = curve
        s = drv.periodic_stats(curve, start, end, period)
        print(f"{Path(run).name:34s} {s['peak']:8.4f} {s['trough']:8.4f} {s['mean']:8.4f}"
              f" {s['peak_phase']:7.3f} {s['cycles']}")
        print(f"{'':34s} rel. to digitised: peak {100*(s['peak']/ref_stats['peak']-1):+.2f}%"
              f"  trough {100*(s['trough']/ref_stats['trough']-1):+.2f}%"
              f"  mean {100*(s['mean']/ref_stats['mean']-1):+.2f}%")
        dmax = drv.history_difference(curve, kratos_ref, start, end)
        print(f"{'':34s} max |uy - digitised| over window = {dmax:.4f} m"
              f" ({100*dmax/ref_stats['peak']:.1f}% of peak)")

        solves = [int(r["coupling_solves"]) for r in rows]
        conv = [int(r["converged"]) for r in rows]
        res = [float(r["rms_residual_at_acceptance"]) for r in rows]
        wall = [float(r["wall_step_s"]) for r in rows]
        print(f"{'':34s} steps {len(rows)}, coupling solves mean {statistics.mean(solves):.2f}"
              f" max {max(solves)}, steps not meeting nl_tol {conv.count(0)},"
              f" max RMS residual at acceptance {max(res):.2e} m,"
              f" step wall sum {sum(wall):.1f} s")

        cyc = per_cycle_peaks(curve, start, end, period)
        print(f"{'':34s} per-cycle peaks: " + " ".join(f"{p:.4f}" for _, p, _ in cyc))
        print(f"{'':34s} per-cycle troughs: " + " ".join(f"{t:.4f}" for _, _, t in cyc))
        print()

    if len(runs) == 2:
        a, b = (curves[r] for r in runs)
        d = max(abs(x[1] - y[1]) for x, y in zip(a, b))
        dw = max(abs(x[1] - y[1]) for x, y in zip(a, b) if start <= x[0] <= end)
        print(f"thread invariance: max |uy({Path(runs[0]).name}) - uy({Path(runs[1]).name})|"
              f" = {d:.3e} m over all steps, {dw:.3e} m over the window")


if __name__ == "__main__":
    main()
