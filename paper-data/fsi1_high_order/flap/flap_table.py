#!/usr/bin/env python3
"""Tip displacement of the solid-only flap study: self-convergence per order."""
import math
import re
import sys
from pathlib import Path

out = Path(sys.argv[1])
data = {}
for case in out.glob("p*_n*"):
    p, n = map(int, re.match(r"p(\d+)_n(\d+)", case.name).groups())
    f = case / "postProcessing/0/solidPointDisplacement_tip.dat"
    rows = [l.split() for l in f.read_text().splitlines()
            if l.strip() and not l.startswith("#")] if f.exists() else []
    last = rows[-1] if rows else None
    t = re.findall(r"ExecutionTime = ([0-9.eE+-]+) s",
                   (case / "log.solids4Foam").read_text(errors="replace"))
    ok = last is not None and abs(float(last[0]) - 1.0) < 1e-9
    data[(p, n)] = (float(last[1]), float(last[2])) if ok else None, \
        float(t[-1]) if t else float("nan")

ref = {}
for p in sorted({k[0] for k in data}):
    ns = sorted(n for (q, n) in data if q == p and data[(q, n)][0])
    if len(ns) >= 3:
        a, b, c = (data[(p, n)][0][1] for n in ns[-3:])
        r = (b - a) / (c - b) if c != b else float("inf")
        order = math.log(abs(r), 2) if r > 0 else float("nan")
        ext = c + (c - b) / (2**order - 1) if order == order and order > 0 else float("nan")
        ref[p] = (order, ext)

best = ref.get(3, (None, float("nan")))[1]
print(f"Reference u_y (Richardson, p = 3): {1000*best:.5f} mm\n")
print("| p | cells thick | u_x (mm) | u_y (mm) | u_y error vs ref | CPU (s) |")
print("|---|---:|---:|---:|---:|---:|")
for (p, n) in sorted(data):
    vals, cpu = data[(p, n)]
    if not vals:
        print(f"| {p} | {n} | failed | | | {cpu:.1f} |")
        continue
    err = (vals[1] - best) / abs(best)
    print(f"| {p} | {n} | {1000*vals[0]:.4f} | {1000*vals[1]:.4f} | {100*err:+.3f}% | {cpu:.1f} |")
print()
for p, (o, e) in sorted(ref.items()):
    print(f"p = {p}: observed order of u_y (finest three) {o:.2f}, extrapolated {1000*e:.5f} mm")
