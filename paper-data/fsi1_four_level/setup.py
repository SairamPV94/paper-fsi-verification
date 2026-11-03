"""Prepare FSI1 four-level study copies of the TurekHron2006 tutorial.
Usage: setup.py SRC_TUTORIAL RUN_DIR"""
import json, re, shutil, sys
from pathlib import Path
src, run = Path(sys.argv[1]), Path(sys.argv[2])
# name -> (levels, dt)
variants = {"L1": (1, 0.00625), "L2": (2, 0.00625), "L4": (4, 0.00625),
            "L8": (8, 0.00625), "L4dt2": (4, 0.0125)}
cores = {"1": 1, "2": 4, "4": 16, "8": 64, "default": 4}
for name, (level, dt) in variants.items():
    dst = run / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, symlinks=True,
                    ignore=shutil.ignore_patterns("work", "postProcessing"))
    ref = dst / "verification/reference/HronTurek_verification_references.json"
    d = json.loads(ref.read_text())
    m = d["fsi1"]["mesh"]
    m["refinementFactors"] = [1, 2, 4, 8]
    m["deltaTs"] = [dt] * 4
    d["fsi1"]["cores"] = cores
    for q in d["fsi1"]["references"].values():
        q["tolerance"].setdefault("8", q["tolerance"]["4"])
    ref.write_text(json.dumps(d, indent=1) + "\n")
    p = dst / "constant/fsiProperties.iqnils"
    t = p.read_text()
    t, n = re.subn(r"^(\s*)(outerCorrTolerance\s+[^;]+;)",
                   r"\1\2\n\1requireAllResidualMeasures yes;\n\1outerCorrAbsoluteTolerance 1e-10;",
                   t, count=1, flags=re.M)
    assert n == 1, p
    p.write_text(t)
    print(name, level, dt)
