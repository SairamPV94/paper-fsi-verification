"""mokLidDrivenCavity, one study member per process, legacy or strict
coupling test, for the verification paper (r1 audit: the legacy test
accepted ~98% of Mok steps with r1 above the tolerance). Wraps the tutorial
driver unchanged except for the work/output directories, the member
selection, an extra mesh128 member and, for the strict variants,
requireAllResidualMeasures yes in fsiProperties.iqnils. The variants ending
in 0 also set couplingReuse 0 (no reuse of earlier time steps' IQN-ILS
modes, as before solids4foam #587).
Usage: mok_var.py VARIANT STUDY MEMBER OUT_DIR [driver args]"""
import importlib.util, re, sys
from pathlib import Path
DRV = Path("/project/home/p201287/philip/qm-a421/solids4foam/tutorials/"
           "fluidSolidInteraction/mokLidDrivenCavity/verification/scripts/"
           "mok_lid_driven_cavity_verification.py")
spec = importlib.util.spec_from_file_location("mokv", DRV)
m = importlib.util.module_from_spec(spec); sys.modules["mokv"] = m
spec.loader.exec_module(m)
variant, study, member, out = sys.argv[1:5]; del sys.argv[1:5]
assert variant in ("legacy", "strict", "legacy0", "strict0")
out = Path(out); m.WORK_DIR = out / "work"; m.POST_DIR = out / "postProcessing"
m.POST_DIR.mkdir(parents=True, exist_ok=True)
EXTRA = {"mesh128": {"name": "mesh128", "nx": 128, "solid_ny": 8,
                     "delta_t": 0.01875, "solid": "highOrder"}}
orig_members = m.study_members
def study_members(config, s, quick):
    pool = orig_members(config, s, quick) + ([dict(EXTRA[member])] if member in EXTRA else [])
    return [x for x in pool if x["name"] == member]
m.study_members = study_members
orig_prepare = m.prepare_case
def prepare_case(run_dir, mem, end_time, cores):
    orig_prepare(run_dir, mem, end_time, cores)
    f = run_dir / "constant" / "fsiProperties.iqnils"
    s = f.read_text()
    if variant.endswith("0"):
        s, n = re.subn(r"^(\s*couplingReuse\s+)\d+;", r"\g<1>0;", s, count=1, flags=re.M)
        assert n == 1
    if variant.startswith("strict") and "requireAllResidualMeasures" not in s:
        s, n = re.subn(r"(^\s*outerCorrTolerance\s+[^;]+;\n)",
                       r"\g<1>    requireAllResidualMeasures yes;\n", s, count=1, flags=re.M)
        assert n == 1
    f.write_text(s)
m.prepare_case = prepare_case
sys.argv += ["--study", study, "--keep-going"]
sys.exit(m.main())
