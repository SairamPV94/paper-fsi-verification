"""Coupling-tolerance sweep, ringAddedMass strong level, mesh 2, 100 steps per
period, IQN-ILS and Robin-Neumann, strict test (all residual measures), for
the verification paper's iterative-error check. Uses the campaign driver
ma_run.py; the tolerance is set in the case's fsiProperties before Allrun."""
import importlib.util, re, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location(
    "ma", "/project/home/p201287/philip/qm-head/campaign/ma/ma_run.py")
ma = importlib.util.module_from_spec(spec); sys.modules["ma"] = ma
spec.loader.exec_module(ma)
TOLS = ["1e-4", "1e-5", "1e-6", "1e-7", "1e-8"]
runs = [dict(id="ts-ram-dry-m2-n100", item="ts", case="ram", kind="dry",
             solid="standard", factor=2, steps=100)]
for coupling, tag in (("iqnils", "iqn"), ("robin", "rn")):
    for t in TOLS:
        runs.append(dict(id=f"ts-ram-{tag}-strong-m2-n100-tol{t}", item="ts",
                         case="ram", kind="wet", level="strong",
                         coupling=coupling, solid="standard", factor=2,
                         steps=100, tol=t))
for r in runs:
    r["ranks"] = 1; r["batch"] = 9
byid = {r["id"]: r for r in runs}
ma.definitions = lambda: runs
orig = ma.run_cmd

def run_cmd(cmd, case, log, *a, **k):
    r = byid.get(Path(case).name)
    if r and r.get("tol"):
        t = float(r["tol"])
        for f in Path(case).glob("constant/fsiProperties.*"):
            s = f.read_text()
            s, n = re.subn(r"(^\s*outerCorrTolerance\s+)[^;]+;", rf"\g<1>{r['tol']};", s, flags=re.M)
            # Robin-Neumann: scale its pressure and flux tolerances with the
            # displacement tolerance (tutorial ratios 10 and 5000)
            s = re.sub(r"(^\s*robinPressureTolerance\s+)[^;]+;", rf"\g<1>{10*t:g};", s, flags=re.M)
            s = re.sub(r"(^\s*robinFluxTolerance\s+)[^;]+;", rf"\g<1>{5000*t:g};", s, flags=re.M)
            f.write_text(s)
    return orig(cmd, case, log, *a, **k)

ma.run_cmd = run_cmd
ma.main()
