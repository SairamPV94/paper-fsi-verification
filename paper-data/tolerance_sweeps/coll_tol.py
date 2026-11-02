"""Coupling-tolerance sweep, collapsibleChannel fluid level 3 at the mesh
study's time step, Robin-Neumann and IQN-ILS, strict test, for the
verification paper's iterative-error check. Wraps the tutorial driver: adds
one study per (coupling, tolerance) and the strict test to every case.
Usage: coll_tol.py WORK_DIR [driver args]"""
import importlib.util, json, re, sys
from pathlib import Path
DRV = Path("/project/home/p201287/philip/qm-a421/solids4foam/tutorials/"
           "fluidSolidInteraction/collapsibleChannel/verification/scripts/"
           "collapsible_channel_verification.py")
spec = importlib.util.spec_from_file_location("ccv", DRV)
ccv = importlib.util.module_from_spec(spec); sys.modules["ccv"] = ccv
spec.loader.exec_module(ccv)
ccv.WORK_DIR = Path(sys.argv[1]); del sys.argv[1]
ccv.WORK_DIR.mkdir(parents=True, exist_ok=True)
orig_load = ccv.load_references
STUDIES = []

def load_references():
    refs = orig_load()
    mesh = refs["studies"]["mesh"]
    for coupling, tols in (("robin", ["1e-3", "1e-4", "1e-5", "1e-6"]),
                           ("iqnils", ["1e-3", "1e-4", "1e-5", "1e-6"])):
        for t in tols:
            s = dict(mesh); s["levels"] = [3]; s["quickLevels"] = [1]
            s["coupling"] = coupling
            fsi = {"outerCorrTolerance": t}
            if coupling == "robin":
                fsi["robinPressureTolerance"] = f"{float(t):g}"
            s["fsiProperties"] = fsi
            s["acceptance"] = {"finestMaxError": 1.0}
            name = f"tol_{coupling}_{t}"
            refs["studies"][name] = s
            if name not in STUDIES:
                STUDIES.append(name)
    return refs

ccv.load_references = load_references
orig_sc = ccv.study_cases

def study_cases(study, refs, quick):
    if study.startswith("tol_"):
        r2 = dict(refs); r2["studies"] = dict(refs["studies"])
        r2["studies"]["mesh"] = refs["studies"][study]
        return orig_sc("mesh", r2, quick)
    return orig_sc(study, refs, quick)

ccv.study_cases = study_cases
orig_conf = ccv.configure_case

def configure_case(run_dir, case, end_time):
    orig_conf(run_dir, case, end_time)
    fsi = run_dir / "constant" / f"fsiProperties.{case['coupling']}"
    s = fsi.read_text()
    if "requireAllResidualMeasures" not in s:
        s = re.sub(r"(^\s*writeResidualsToFile\s+yes;\n)",
                   r"\g<1>    requireAllResidualMeasures yes;\n", s, count=1, flags=re.M)
        fsi.write_text(s)

ccv.configure_case = configure_case
load_references()
if "--study" not in sys.argv:
    sys.argv += ["--study", ",".join(STUDIES)]
sys.exit(ccv.main())
