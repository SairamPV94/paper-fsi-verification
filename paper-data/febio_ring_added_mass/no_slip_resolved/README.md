# ringAddedMass: FEBio v4.13, finite-viscosity no-slip problem (resolved near-wall layers)

This directory is **separate from, and does not replace, the free-slip analytical-limit study** in the parent directory (free-slip walls, a different physical model; its results are unchanged). Here FEBio solves the problem of the solids4foam tutorial: no-slip on the moving ring and on the rigid wall, nu_F = 1e-7 m^2/s, fluid initially at rest, three added-mass levels.

**Classification: QUALIFIED INDEPENDENT COMPARISON.** FEBio reproduces the continuum finite-viscosity eigenvalue (wet/dry ratio and damping) for the three levels once the Stokes layer is resolved; it is not a demonstration that FEBio and solids4foam produce the same discrete solution, and the model-form differences below remain.

## Results (fluid at rest, first fluid cell delta/4 at both walls, 52 radial cells, 100 steps per period, pristine FEBio v4.13)
| Level | Mesh | err vs inviscid A | err vs finite-viscosity V | fitted decay / exact viscous rate |
|---|---|---|---|---|
| weak | f1 / f2 | -0.0010 / -0.0006 % | +0.0031 / +0.0035 % | 0.998 / 0.985 |
| moderate | f1 / f2 | -0.0311 / -0.0305 % | -0.0049 / -0.0043 % | 0.984 / 0.977 |
| strong | f1 / f2 | -0.0828 / -0.0821 % | -0.0097 / -0.0090 % | 0.983 / 0.974 |
f1, f2: ring 4x48 / 8x96 cells and 48 / 96 tangential fluid cells. V = A(1 + viscous shift) from the reference code (shifts -4.1e-5, -2.63e-4, -7.31e-4); exact viscous decay rates 1.005e-4, 4.748e-4, 5.621e-4 1/s (displacement-amplitude rates, verified by an independent thin-Stokes-layer estimate to 0.08 %).
Preregistered criteria (`docs/O2_PREREGISTRATION_A.md`, hashed before the runs): C1 ratio within 0.1 % of V: met (max 0.010 %); C2 decay within 0.7-1.3 of exact: met (0.974-0.998); C3 half time step (paired dry run) changes the ratio by at most 0.01 pp: met (max 0.0003 pp); C4 f1 to f2 change at most 0.02 pp (0.05 strong): met (max 0.0007 pp); C6 soundness: met (400/400 or 800/800 steps, no Jacobian/NaN messages, mean(J-1) at most 4e-9). **C5 (energy, diagnostic runs): Ds met (Gamma 2.8e-3); Dw (weak, potential-flow start) FAILED in the first step ("Max nr of reformations", a convergence-criterion floor with zero initial increment) and was not rerun.** Exploratory A2 (`Pm1K7`, `Pm1K9`, moderate): K 1e7 / 1e9 change the ratio error by -0.0011 / +0.0063 pp, decay within 0.985-0.987 of exact.

## Interface mechanics (reconstructed from logged fields, `scripts/traction_audit.py`; built-in FEBio log variables only, no source change)
Pressure traction (nodal dilatation on the face) and viscous traction (element-mean stress, as in `FEFluidFSITraction.cpp`) applied to the ring; work of the reconstructed traction equals the ring's kinetic plus strain energy change to 0.02-0.09 % of the swing (1.9 % for the strong level at rest); n=2 viscous shear amplitude 0.84-0.90 of the thin-Stokes-layer estimate; shear/pressure ratio 4e-4 to 8e-4; strong level, potential-flow start: fluid-side energy plus dissipation balances ring work to 0.5 % of the ring swing and the discrete energy balance closes to 0.3 % of the initial energy. These are reconstructions, not measured interface forces.

## Model-form differences between this FEBio model and the solids4foam tutorial (quantified, not removed)
Weak compressibility (K = 1e8; K 1e7-1e9: <= 0.006 pp), finite-strain solid versus small-strain (halved amplitude: -0.0068 pp, moderate), mass-regularised mesh motion (E_mesh 1e-3 Pa; tenfold: +0.0015 pp), finite amplitude, linear hex8 ring. Full table: `docs/PHYSICAL_EQUIVALENCE_MATRIX.md`. Initial state: fluid at rest as the tutorial; the response amplitude after the impulsive start is about 1/(1+m*) of V0/omega, and a weakly compressible acoustic transient follows.

## What this does not establish
Equality of discrete solutions with solids4foam (its tutorial mesh does not resolve the Stokes layer, its measured decay is dominated by time-integration damping, and it does not resolve the viscous shift); measured (not reconstructed) interface forces; the incompressible limit beyond K = 1e9; small-strain solid; the discrete mechanism of the energy gain found with an unresolved layer (`docs/EXISTING_G0_G1_FORENSIC_AUDIT.md`, `docs/NUMERICAL_RESULTS.md`).
The earlier graded pilot's failed gate (G1, pressure criterion N1 = 0.278 against 0.176) stays FAILED (`docs/FEBIO_RING_NOSLIP_GRADED_MESH_RESULTS.md`).

## Reproduce (no simulation)
`python3 -I scripts/ring_final_table.py` and `python3 -I scripts/ring_figures.py` (from this directory; they read `results/` and the parent package's `reference/` and `tools/`) regenerate `results/ring_final_table.*` and `figures/ringAddedMass_febio_R1..R5.png` byte-identically (checked). Inputs are gzipped in `inputs/`; run reports, probes, analysis outputs in `results/`; the generator is `scripts/make_ring_feb_v2.py` (adds `--fluid-grading two-sided --h1 --nrf --log-stress`; regenerated baseline inputs are byte-identical). Large raw nodal logs are not stored. Binary sha256 f5ae1ed6f347f875c392f93d847f2369f437345a9b785296d46b0bd6fbb72f02 (in every `run_meta_start.json`). Figures: R1 ratio errors, R2 convergence, R3 displacement histories, R4 interface traction, R5 energy balance.
Note: scripts that read raw nodal logs (forensic_energy.py, traction_audit.py, analyze.sh) contain the placeholder <project-root> for the workspace in which the runs were made; raw logs are not stored.
