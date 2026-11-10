"""Run the Kratos FSI lid-driven cavity and record a per-step history.

Based on MainKratos.py of KratosMultiphysics/Examples
(fluid_structure_interaction/validation/fsi_lid_driven_cavity, commit fb900a5).
Additions:
  - history.csv: time, midpoint displacement at (0.5, 0), coupling solves per step,
    whether the coupling test was met, the RMS interface residual at acceptance, wall time
  - run_info.json: Kratos version, threads, host, total wall time
The FSI solver accepts a step when nl_max_it is reached without meeting nl_tol,
so the converged flag and the residual at acceptance are recorded for every step.

Usage: python MainKratos.py [ProjectParameters.json] [--end-time T]
"""
import sys
import os
import json
import math
import time
import socket
import platform
import importlib

import KratosMultiphysics as KM

MIDPOINT = (0.5, 0.0)


def load_parameters(argv):
    path = "ProjectParameters.json"
    end_time = None
    args = list(argv)
    if "--end-time" in args:
        i = args.index("--end-time")
        end_time = float(args[i + 1])
        del args[i:i + 2]
    if args:
        path = args[0]
    with open(path) as f:
        parameters = KM.Parameters(f.read())
    if end_time is not None:
        parameters["problem_data"]["end_time"].SetDouble(end_time)
    return path, parameters


def stage_class(parameters):
    module_name = parameters["analysis_stage"].GetString()
    class_name = "".join(x.title() for x in module_name.split(".")[-1].split("_"))
    return getattr(importlib.import_module(module_name), class_name)


def create_stage(cls, model, parameters):

    class RecordedFsiAnalysis(cls):

        def Initialize(self):
            super().Initialize()
            solver = self._GetSolver()

            # Structure node at the monitored point (wetted face of the membrane)
            structure = self.model.GetModelPart("Structure")
            self.probe = min(structure.Nodes,
                             key=lambda n: (n.X0 - MIDPOINT[0])**2 + (n.Y0 - MIDPOINT[1])**2)
            dist = math.hypot(self.probe.X0 - MIDPOINT[0], self.probe.Y0 - MIDPOINT[1])
            if dist > 1e-10:
                raise RuntimeError(f"no structure node at {MIDPOINT}, nearest is {dist} away")

            # Per-step coupling record, filled by wrapping the solver methods
            self.step_rec = {}
            check = solver._CheckFSIConvergence
            def recorded_check(nl_it, residual_norm):
                ok = check(nl_it, residual_norm)
                self.step_rec["checked_it"] = nl_it
                return ok
            solver._CheckFSIConvergence = recorded_check

            interface = solver._GetFSICouplingInterfaceStructure()
            compute = interface.ComputeResidualVector
            def recorded_compute(*a, **k):
                norm = compute(*a, **k)
                self.step_rec["solves"] = self.step_rec.get("solves", 0) + 1
                self.step_rec["last_norm"] = norm
                return norm
            interface.ComputeResidualVector = recorded_compute

            solve = solver.SolveSolutionStep
            def recorded_solve():
                ok = solve()
                self.step_rec["converged"] = bool(ok)
                return ok
            solver.SolveSolutionStep = recorded_solve

            self.n_dofs = solver._GetPartitionedFSIUtilities().GetInterfaceResidualSize(
                solver._GetStructureInterfaceSubmodelPart())

            self.history = open("history.csv", "w")
            self.history.write("time,ux_mid,uy_mid,coupling_solves,converged,"
                               "rms_residual_at_acceptance,wall_step_s\n")
            self.t_wall0 = time.time()
            self.t_step0 = self.t_wall0
            sys.stdout.flush()

        def InitializeSolutionStep(self):
            self.step_rec = {}
            self.t_step0 = time.time()
            super().InitializeSolutionStep()

        def FinalizeSolutionStep(self):
            super().FinalizeSolutionStep()
            r = self.step_rec
            rms = r.get("last_norm", float("nan")) / math.sqrt(self.n_dofs)
            self.history.write("{:.10g},{:.12e},{:.12e},{:d},{:d},{:.6e},{:.4f}\n".format(
                self.time,
                self.probe.GetSolutionStepValue(KM.DISPLACEMENT_X),
                self.probe.GetSolutionStepValue(KM.DISPLACEMENT_Y),
                r.get("solves", 0), int(r.get("converged", False)), rms,
                time.time() - self.t_step0))
            self.history.flush()
            sys.stdout.flush()

        def Finalize(self):
            super().Finalize()
            self.history.close()
            self.wall_total = time.time() - self.t_wall0

    return RecordedFsiAnalysis(model, parameters)


def kratos_version():
    for getter in (lambda: KM.Kernel.Version(), lambda: KM.KratosGlobals.Kernel.Version()):
        try:
            return getter()
        except Exception:
            pass
    return "unknown"


if __name__ == "__main__":
    params_path, parameters = load_parameters(sys.argv[1:])
    model = KM.Model()
    simulation = create_stage(stage_class(parameters), model, parameters)
    t0 = time.time()
    simulation.Run()
    info = {
        "kratos_version": kratos_version(),
        "python": platform.python_version(),
        "host": socket.gethostname(),
        "cpu": next((l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo")
                     if l.startswith("model name")), "unknown"),
        "omp_num_threads_env": os.environ.get("OMP_NUM_THREADS"),
        "kratos_threads": KM.ParallelUtilities.GetNumThreads(),
        "parameters_file": params_path,
        "end_time": parameters["problem_data"]["end_time"].GetDouble(),
        "wall_total_s": round(time.time() - t0, 3),
        "wall_solution_loop_s": round(getattr(simulation, "wall_total", float("nan")), 3),
    }
    with open("run_info.json", "w") as f:
        json.dump(info, f, indent=2)
    print(json.dumps(info, indent=2))
