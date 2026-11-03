"""Merge a restart's postProcessing (start time T0) into the original run's files:
original rows with t <= T0 plus restart rows with t > T0."""
import sys, re
from pathlib import Path
case, t0 = Path(sys.argv[1]), sys.argv[2]
bak, pp = case / "postProcessing.part1", case / "postProcessing"
def rows(p):
    head, data = [], []
    for line in p.read_text(errors="replace").splitlines():
        f = line.split()
        if f and re.fullmatch(r"[-+0-9.eE]+", f[0]):
            data.append((float(f[0]), line))
        else:
            (head if not data else []).append(line)
    return head, data
for orig in bak.rglob("*.dat"):
    rel = orig.relative_to(bak)
    parts = list(rel.parts)
    new = pp.joinpath(*[t0 if p == "0" else p for p in parts])
    if not new.is_file():
        new = pp / rel
    head, a = rows(orig)
    _, b = rows(new) if new.is_file() else ([], [])
    T = float(t0)
    out = head + [l for t, l in a if t <= T + 1e-9] + [l for t, l in b if t > T + 1e-9]
    (pp / rel).parent.mkdir(parents=True, exist_ok=True)
    (pp / rel).write_text("\n".join(out) + "\n")
    print(rel, len(a), len(b), "->", len(out) - len(head))
for d in list(pp.rglob(t0)):
    if d.is_dir():
        import shutil; shutil.rmtree(d)
