#!/usr/bin/env python3
"""Write a Kratos input set for the lid-driven cavity with a flexible bottom at any level.

The meshes follow the pattern of the shipped GiD meshes exactly: structured fluid triangles with
the '/' diagonal, counter-clockwise elements, boundary conditions traversed with the domain on
their left, a structured Q1 solid of thickness 0.002 m below y = 0, the same SubModelPart names
and node sets. Only the node and element numbering differs.

Usage:
  python make_case.py <template dir> <out dir> --n 64 --dt 0.025
         [--solid-x N] [--solid-y 2] [--nl-tol 1e-6] [--tight] [--outlet-uy0] [--fix-openings] [--dynamic-tau 1] [--vtk-every 1.0]

<template dir> holds ProjectParameters.json and the two materials files of the level-1 port.
--solid-x defaults to --n, so the interface nodes of fluid and solid coincide.
--tight tightens the fluid, solid, mesh and linear-solver tolerances by two decades.
--outlet-uy0 adds u_y = 0 on the outlet nodes (outlet sensitivity check, not the benchmark).
--dynamic-tau sets the weight of the 1/dt term in the VMS stabilisation parameter (the example uses 1;
  0 makes the stabilisation independent of the time step).
--fix-openings fixes the mesh motion of the opening nodes in y too, so the inlet and outlet stay at
  0.875 <= y <= 1 as the group-B definition states (the shipped mesh lets them slide along the walls).
"""
import argparse
import json
import os
import shutil

H_SOLID = 0.002
Y_OPENING = 0.875
FLUID_MDPA = "fsi_lid_driven_cavity_Fluid"
SOLID_MDPA = "fsi_lid_driven_cavity_Structural"


def fmt(v):
    return f"{v:.17g}"


def write_smp(f, name, nodes, elements=(), conditions=()):
    f.write(f"Begin SubModelPart {name}\n    Begin SubModelPartNodes\n")
    for i in nodes:
        f.write(f"        {i}\n")
    f.write("    End SubModelPartNodes\n    Begin SubModelPartElements\n")
    for i in elements:
        f.write(f"        {i}\n")
    f.write("    End SubModelPartElements\n    Begin SubModelPartConditions\n")
    for i in conditions:
        f.write(f"        {i}\n")
    f.write("    End SubModelPartConditions\nEnd SubModelPart\n")


def write_fluid(path, n, fix_openings=False):
    if (n * 7) % 8:
        raise SystemExit("n must be a multiple of 8 so that y = 0.875 is a grid line")
    j0 = n * 7 // 8

    def nid(i, j):
        return 1 + j * (n + 1) + i

    with open(path, "w") as f:
        f.write("Begin ModelPartData\nEnd ModelPartData\n\n")
        f.write("Begin Properties 0\nEnd Properties\n\n")
        f.write("Begin Properties 1\n    DENSITY 1.0\n    DYNAMIC_VISCOSITY 0.01\nEnd Properties\n\n")
        f.write("Begin Nodes\n")
        for j in range(n + 1):
            for i in range(n + 1):
                f.write(f"    {nid(i, j)} {fmt(i / n)} {fmt(j / n)} 0.0\n")
        f.write("End Nodes\n\n")

        f.write("Begin Elements Element2D3N\n")
        eid = 0
        for j in range(n):
            for i in range(n):
                bl, br, tr, tl = nid(i, j), nid(i + 1, j), nid(i + 1, j + 1), nid(i, j + 1)
                eid += 1
                f.write(f"    {eid} 1 {bl} {br} {tr}\n")
                eid += 1
                f.write(f"    {eid} 1 {bl} {tr} {tl}\n")
        n_elem = eid
        f.write("End Elements\n\n")

        cid = 0
        groups = {}

        def conditions(name, edges):
            nonlocal cid
            f.write("Begin Conditions WallCondition2D2N\n")
            ids = []
            for a, b in edges:
                cid += 1
                ids.append(cid)
                f.write(f"    {cid} 0 {a} {b}\n")
            f.write("End Conditions\n\n")
            groups[name] = ids

        # Outlet: x = 1, y from 0.875 up to 1
        conditions("outlet", [(nid(n, j), nid(n, j + 1)) for j in range(j0, n)])
        # No-slip: left wall downwards from 0.875 to 0, right wall upwards from 0 to 0.875
        conditions("noslip", [(nid(0, j + 1), nid(0, j)) for j in range(j0 - 1, -1, -1)]
                   + [(nid(n, j), nid(n, j + 1)) for j in range(j0)])
        # Interface: y = 0, left to right
        conditions("interface", [(nid(i, 0), nid(i + 1, 0)) for i in range(n)])

        all_nodes = [nid(i, j) for j in range(n + 1) for i in range(n + 1)]
        write_smp(f, "Parts_Fluid", all_nodes, range(1, n_elem + 1))
        write_smp(f, "Outlet2D_Outlet", [nid(n, j) for j in range(j0, n + 1)],
                  conditions=groups["outlet"])
        write_smp(f, "NoSlip2D_NoSlip",
                  sorted([nid(0, j) for j in range(j0 + 1)] + [nid(n, j) for j in range(j0 + 1)]),
                  conditions=groups["noslip"])
        write_smp(f, "VelocityConstraints2D_Inlet",
                  sorted({nid(i, n) for i in range(n + 1)} | {nid(0, j) for j in range(j0, n + 1)}))
        write_smp(f, "ALEMeshDisplacementBC2D_ALEMeshBCx",
                  sorted([nid(0, j) for j in range(n + 1)] + [nid(n, j) for j in range(n + 1)]))
        # Mesh y is fixed on the top; with fix_openings also on the opening nodes of the side walls
        # (y >= 0.875), which are in BCx already, so the openings cannot slide along the walls
        bcy = {nid(i, n) for i in range(n + 1)}
        if fix_openings:
            bcy |= {nid(i, j) for i in (0, n) for j in range(j0, n + 1)}
        write_smp(f, "ALEMeshDisplacementBC2D_ALEMeshBCy", sorted(bcy))
        write_smp(f, "FluidNoSlipInterface2D_FluidInterface", [nid(i, 0) for i in range(n + 1)],
                  conditions=groups["interface"])
    return (n + 1) ** 2, n_elem


def write_solid(path, nx, ny, node_offset, elem_offset):
    def nid(i, k):  # k = 0 on the wetted face y = 0, k = ny on y = -h
        return node_offset + 1 + k * (nx + 1) + i

    with open(path, "w") as f:
        f.write("Begin ModelPartData\nEnd ModelPartData\n\n")
        f.write("Begin Properties 0\nEnd Properties\n\n")
        f.write("Begin Nodes\n")
        for k in range(ny + 1):
            for i in range(nx + 1):
                f.write(f"    {nid(i, k)} {fmt(i / nx)} {fmt(-H_SOLID * k / ny)} 0.0\n")
        f.write("End Nodes\n\n")
        f.write("Begin Elements TotalLagrangianElement2D4N\n")
        eids = []
        for k in range(ny):
            for i in range(nx):
                eid = elem_offset + len(eids) + 1
                eids.append(eid)
                # top-left, bottom-left, bottom-right, top-right (counter-clockwise)
                f.write(f"    {eid} 0 {nid(i, k)} {nid(i, k + 1)} {nid(i + 1, k + 1)} {nid(i + 1, k)}\n")
        f.write("End Elements\n\n")
        f.write("Begin Conditions LineCondition2D2N\n")
        for i in range(nx):
            f.write(f"    {i + 1} 0 {nid(i, 0)} {nid(i + 1, 0)}\n")
        f.write("End Conditions\n\n")
        write_smp(f, "Parts_Structure", [nid(i, k) for k in range(ny + 1) for i in range(nx + 1)], eids)
        write_smp(f, "DISPLACEMENT_DisplacementBC",
                  sorted([nid(0, k) for k in range(ny + 1)] + [nid(nx, k) for k in range(ny + 1)]))
        write_smp(f, "StructureInterface2D_StructureInterface", [nid(i, 0) for i in range(nx + 1)],
                  conditions=range(1, nx + 1))
    return (nx + 1) * (ny + 1), nx * ny


def write_parameters(template, out, args):
    with open(template) as f:
        p = json.load(f)
    s = p["solver_settings"]
    st, fl, me, co = (s["structure_solver_settings"], s["fluid_solver_settings"],
                      s["mesh_solver_settings"], s["coupling_settings"])
    st["time_stepping"]["time_step"] = args.dt
    fl["time_stepping"]["time_step"] = args.dt
    co["nl_tol"] = args.nl_tol
    if args.dynamic_tau is not None:
        fl["formulation"]["dynamic_tau"] = args.dynamic_tau
    if args.tight:
        for key in ("displacement_relative_tolerance", "residual_relative_tolerance"):
            st[key] = 1e-8
        for key in ("displacement_absolute_tolerance", "residual_absolute_tolerance"):
            st[key] = 1e-10
        for key in ("relative_velocity_tolerance", "relative_pressure_tolerance"):
            fl[key] = 1e-8
        for key in ("absolute_velocity_tolerance", "absolute_pressure_tolerance"):
            fl[key] = 1e-10
        fl["maximum_iterations"] = 20
        st["max_iteration"] = 20
        fl["linear_solver_settings"] = {"solver_type": "amgcl", "tolerance": 1e-9,
                                        "max_iteration": 1000}
        me["linear_solver_settings"] = {"solver_type": "amgcl", "tolerance": 1e-10,
                                        "max_iteration": 1000}
        co["nl_max_it"] = 40
    if args.outlet_uy0:
        p["processes"]["fluid_boundary_conditions_process_list"].append({
            "python_module": "assign_vector_variable_process",
            "kratos_module": "KratosMultiphysics",
            "process_name": "AssignVectorVariableProcess",
            "Parameters": {
                "model_part_name": "FluidModelPart.Outlet2D_Outlet",
                "variable_name": "VELOCITY",
                "constrained": [False, True, False],
                "value": [None, 0.0, None],
                "interval": [0.0, "End"]}})
    every = max(1, round(args.vtk_every / args.dt))
    for proc in p["output_processes"]["vtk_output"]:
        proc["Parameters"]["output_interval"] = every
    with open(out, "w") as f:
        json.dump(p, f, indent=4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("template")
    ap.add_argument("out")
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--dt", type=float, required=True)
    ap.add_argument("--solid-x", type=int)
    ap.add_argument("--solid-y", type=int, default=2)
    ap.add_argument("--nl-tol", type=float, default=1e-6)
    ap.add_argument("--tight", action="store_true")
    ap.add_argument("--outlet-uy0", action="store_true")
    ap.add_argument("--vtk-every", type=float, default=1.0)
    ap.add_argument("--fix-openings", action="store_true")
    ap.add_argument("--dynamic-tau", type=float)
    args = ap.parse_args()
    args.solid_x = args.solid_x or args.n

    if os.path.exists(args.out):
        raise SystemExit(f"{args.out} exists, refusing to overwrite")
    os.makedirs(args.out)
    n_fn, n_fe = write_fluid(os.path.join(args.out, FLUID_MDPA + ".mdpa"), args.n, args.fix_openings)
    n_sn, n_se = write_solid(os.path.join(args.out, SOLID_MDPA + ".mdpa"),
                             args.solid_x, args.solid_y, n_fn, n_fe)
    write_parameters(os.path.join(args.template, "ProjectParameters.json"),
                     os.path.join(args.out, "ProjectParameters.json"), args)
    for name in ("FluidMaterials.json", "StructuralMaterials.json"):
        shutil.copy(os.path.join(args.template, name), args.out)
    case = dict(vars(args), fluid_nodes=n_fn, fluid_elements=n_fe, solid_nodes=n_sn,
                solid_elements=n_se, generator="make_case.py")
    with open(os.path.join(args.out, "case.json"), "w") as f:
        json.dump(case, f, indent=2)
    print(json.dumps(case))


if __name__ == "__main__":
    main()
