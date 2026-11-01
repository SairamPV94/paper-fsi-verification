# ringAddedMass no-slip graded-mesh pilot: results

**Classification (per the preregistered rule): 4. NOT ESTABLISHED.** The pilot stopped after G1 on a preregistered soundness stop (N1). G2 and G3 were not run, so the finest-case criteria N3 to N6 were never assessed. No like-for-like claim is made. The free-slip results of PR #26 are unchanged and remain a separate analytical-limit study.

Preregistration: `FEBIO_RING_NOSLIP_GRADED_PREREGISTRATION.md`, sha256 `69e207ad9ff1d6af65908f1eda5b23829976e9ddc48345d282279d0852d86303`, hashed 2026-11-01T01:50:17Z before any input was run (`runs/ring_noslip_graded/PREREGISTRATION.sha256`). No criterion was changed afterwards.

## 1. Physical equivalence (Gate 0)
Full table: `runs/ring_noslip_graded/GATE0_EQUIVALENCE.md`. Summary: geometry, ring mesh, densities, viscosity (nu 1e-7), ring material parameters, symmetry constraints, no external load, and no-slip on both boundaries match the tutorial. They differ in:
- **Initial fluid velocity (model form, not removed):** FEBio uses a compatible potential-plus-correction flow; the tutorial starts the fluid at rest. It is compatible with no-slip at both walls by construction. `--ic impulsive` exists but was never run in this campaign and would be an uncontrolled change, so identical initial-boundary value problems are **not** claimed.
- Fluid compressibility (K = 1e8 versus incompressible), the mesh-motion device (massless solid E_mesh 1e-3 Pa versus mesh diffusion), and the solid kinematics (finite-strain hex8 versus small-strain linear) differ.
- The tutorial imposes no-slip weakly through the viscous flux on an unresolved uniform mesh; FEBio imposes it as a hard nodal constraint. This is a discretisation difference of the same physical condition.
Exact continuum equivalence is therefore not shown, and it was not claimed.

## 2. Exact input differences and mesh
Inputs differ only in radial fluid-node spacing and, between G0 and G1 to G3, the wall/interface condition and the matching initial-velocity correction. G0 and G3 differ only in the BC node sets (and the IC wall coefficient). Generator change: `fluid_radii` and flags `--fluid-grading`, `--h1`, `--nrf` in `tools/make_ring_feb.py`; the pre-change copy is kept, and the regenerated baseline (C2 M1) input is byte-identical (sha256 `3c769ab3...`). Common settings: moderate regime, K 1e8, E_mesh 1e-3, rhoi 1, dt 0.0348193, ring 4 x 48, 48 tangential fluid cells.

| Run | BCs | First cell | Radial cells | Growth | Max aspect | Nodes | Min scaled Jacobian |
|---|---|---|---|---|---|---|---|
| G0 | free-slip | delta/4 = 8.32e-5 m | 52 | 1.2927 | 413 | 5586 | 0.99987 |
| G1 | no-slip | 4 delta = 1.332e-3 m | 32 | 1.2720 | 26 | 3626 | 0.99987 |
| G2 | no-slip | delta = 3.329e-4 m | 42 | 1.2850 | 103 | 4606 | not run |
| G3 | no-slip | delta/4 | 52 | 1.2927 | 413 | 5586 | not run |

delta = 3.3292e-4 m. Mesh quality was computed from the generated nodes before submission (`mesh_quality_precheck.json`); conditioning was not estimated.

## 3. Jobs and measured cost
| Run | Slurm job | Cores | Elapsed | Allocated CPU-s | CPU-h | Status |
|---|---|---|---|---|---|---|
| G0 | 14551 | 2 | 13:47 | 1654 | 0.4594 | COMPLETED, normal termination, 400/400 steps |
| G1 | 14552 | 2 | 07:41 | 922 | 0.2561 | COMPLETED, normal termination, 400/400 steps |
| G2, G3 | not submitted | | | | | stopped at N1 |
| **Total** | | | | **2576** | **0.7156 of the 3.0 CPU-h cap** | |
Counted from sacct elapsed x allocated CPUs for these job IDs only. Unrelated account jobs are not charged. Peak memory 356 MB (G0), 250 MB (G1). Newton iterations per step 4.01 and 4.00. No failed job.

## 4. Gate 1: G0 free-slip graded control (all items passed)
| Item | Result | Criterion |
|---|---|---|
| G0.1 ratio change vs uniform M1 baseline | ratio 0.7062985, error +0.006061 % versus +0.006093 %: change -3.2e-5 pp | below 0.02 pp: pass |
| G0.2 steps, messages | 400/400, normal termination, 0 Jacobian/NaN/inversion messages, 0 max-iteration events | pass |
| G0.3 interface leakage | rms 0.335 %, max 0.428 % of V0, net flux 0.322 % | at most 2 / 10 / 1 %: pass |
| G0.4 volume, n = 0 pressure | max abs mean(J-1) 5.1e-10; n = 0 amplitude at omega 0.0000 Pa | pass |
| G0.5 pressure noise | 0.0587 versus 0.0620 for the baseline | within the limit: pass |
| G0.6 n = 2 force | added-mass ratio at layer 0 0.9990 and layer 1 0.9989 (the layer-0 centre lies about 4e-5 m from the interface) | within 5 %: pass (the check is the layer pressure amplitude, not a separately integrated force) |
| G0.7 scaled Jacobian | 0.99987 | at least 0.5: pass |
G0 fitted omega 1.851253 (zero-crossing 1.851253), window spread 2.3e-5 %, decay (fitted) alpha 1.2e-6 s^-1. Grading itself does not perturb the free-slip solution.

## 5. G1 results (no-slip, first cell 4 delta)
| Quantity | G1 | Note |
|---|---|---|
| wet omega (fit) | 1.848300 rad/s | window spread 0.0286 % (G0: 2.3e-5 %) |
| matched dry omega (B1) | 2.621063 | reuse justified: identical ring mesh, material, integrator, tolerances |
| ratio | 0.705172 | |
| ratio error vs A (exact inviscid 0.7062557) | **-0.1535 %** | baseline D4 (uniform M1, no-slip): -6.16 % |
| ratio error vs V (finite-viscosity linear 0.7060700) | -0.1272 % | |
| ratio difference vs solids4foam data (A-referenced errors, mesh 1/2/4) | QM -0.0158/-0.00156/-0.000093 %, IQN-ILS +0.0689/+0.0181/+0.0051 % | FEBio -0.1535 % lies 0.14 to 0.22 pp below these; compared as printed, a different discretisation |
| fitted decay rate | -2.25e-4 s^-1 (amplitude growing) | V target +4.7483e-4 s^-1: ratio -0.47 (reported only) |
| kinetic energy at integer periods / initial | up to 1.0063 (G0: 1.0016) | energy gain, not loss |
| n = 2 pressure amplitude, phase | 0.3326 Pa, 178.11 deg | profile ratio layer 0 / layer 1: 1.0003 / 0.9986 |
| n = 0 pressure at omega, 2 omega | 0.0527 Pa, 0.0230 Pa; n = 0 residual rms 0.0902 Pa, none above 20 rad/s | |
| n = 2 residual rms | 0.0119 Pa (3.6 % of signal) | |
| max pressure, first 5 steps / after 5 | 0.102 Pa / 0.739 Pa | G0: 0.089 / 0.394 |
| ring velocity vs du/dt (rms) | 0.166 % | |
| max mean(J-1) | 4.2e-9 | |
| interface leakage | n/a: w = 0 is enforced strongly | |
| viscous shear contribution | **not measured**: the logged data contain only pressure and volume ratio | |

## 6. Predeclared acceptance results
| Criterion | Result |
|---|---|
| N1 soundness (G1): steps, messages, mean(J-1) at most 1e-7, n = 0 at omega at most 0.1 Pa, p_noise at most 3 x G0 | steps, messages, volume and n = 0 pass (0.0527 Pa). **p_noise 0.2777 against the limit 3 x 0.0587 = 0.1760: FAIL.** N1 failure stops the series. |
| N2 monotone decrease of |ratio error vs A| | D4 6.16 % to G1 0.1535 %: holds so far; G2, G3 not run |
| N3 finest case at most 0.1 % (A and V) | not assessed (G3 not run) |
| N4 damping (G3) | not assessed; G1 reported only: wrong sign |
| N5, N6 (G3) | not assessed; G1 ring velocity consistency 0.166 %, Newton 4.0 per step |
The stop is triggered on the written criterion, and it coincides with the brief's own stop for growing pressure oscillations: the late-time pressure maximum is 0.74 Pa against 0.39 Pa in G0. I did not reinterpret N1 after seeing the value. What the failing quantity contains (post hoc, not a revision of any criterion): the residual is low-frequency (none above 20 rad/s), n = 0 content of 0.09 Pa rms, so it is not grid-scale odd-even noise as the metric name suggests. Whether it is a genuine pressure anomaly of the no-slip discretisation or a proxy defect of the metric is untested.

## 7. Scientific reading
- **Established by these runs:** at the same ring mesh, tangential resolution, K, dt, regulariser and initial-condition recipe, replacing the uniform 12-cell radial fluid mesh with a two-sided graded 32-cell mesh (first cell 4 delta) moved the no-slip wet/dry ratio error from -6.16 % (D4) to -0.153 %. The graded free-slip control is unchanged to 3e-5 pp. The no-slip error of the earlier runs is therefore largely a radial near-wall mesh effect, as hypothesised, at least in this one comparison.
- **Not established:**
  - Whether the G1 gain comes from near-wall resolution or from the larger number of radial cells (32 versus 12); bulk radial resolution had only a 0.01 pp effect in the slip family, which is indirect evidence for the former and not a test.
  - Whether the error continues to fall as first cell goes to delta and delta/4 (N2 beyond G1, N3).
  - The finite-viscosity damping and shear traction (G1 shows negative damping and kinetic-energy gain of 0.6 %, so the physical Stokes-layer dissipation is not reproduced at this resolution, whose first cell is still 4 delta).
  - Any like-for-like equivalence with the solids4foam problem, which also needs the initial condition and compressibility differences addressed.
- G1's -0.1535 % is outside the 0.1 % official ratio tolerance and differs from the solids4foam printed errors by 0.14 to 0.22 pp.

## 8. Feasibility and next step
Graded meshes need only a generator change and cost 0.26 to 0.46 CPU-h per run at 2 cores, so G2 and G3 would need about 0.8 CPU-h more (about 2.3 CPU-h of the cap remains). Continuing is not authorised by the preregistration, because N1 failed. If you want to continue, the honest route is a documented amendment, made after seeing G1, so G2 and G3 would be exploratory evidence and could not alone support a "supported" classification. The decision is yours.

If the pilot is closed here, the inviscid-limit study stands unchanged, and the manuscript can say: a graded no-slip mesh reduced the no-slip ratio error from -6.16 % to -0.15 %, with damping and shear traction not reproduced; further refinement was not tested.

## 9. Files
`runs/ring_noslip_graded/` holds inputs, logs, probes, reports, `GATE0_EQUIVALENCE.md`, `mesh_quality_precheck.json`, `PREREGISTRATION.sha256`, `INPUT_SHA256SUMS` and `RESULT_SHA256SUMS`. Ledger rows G0 and G1 are in `MULTIBENCHMARK_JOB_LEDGER.csv`. No FEBio source change, plugin, PR push or manuscript edit occurred, and no job other than G0 and G1 was submitted.
