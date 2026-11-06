# blobInTreacle: second implementation (FEniCSx) and interface-formulation audit

Status: **draft supplementary evidence, same research group, not an independent verification by a different group.**
Text: `../../supplement_fenicsx_blobintreacle.tex` (builds alone with `latexmk -pdf supplement_fenicsx_blobintreacle.tex`). Related: issue #50 (this is *not* the FEBio run that issue asked for).

The wording follows an independent referee-style review of the evidence package (a further agent of the same model family; reviewed state of the code repository: master ee9379f plus uncommitted run directories). That review accepted the steady-state sequences, the M2 transmission loss and the limited BDF2 result, and rejected the claims listed in "What is not claimed" below.

## Contents
| file | content |
|---|---|
| `data/steady_levels.csv` | per-level steady values, four models (FEniCSx M2-BE, FEniCSx M1-BE, solids4foam M2 original, solids4foam E-AREA diagnostic), with source document per row (hand-transcribed from the signed-off run records) |
| `data/steady_convergence.csv` | observed order, Richardson limit, GCI (finest and coarsest triple) |
| `data/steady_crosscode.csv` | FEniCSx M2 against solids4foam M2: same level and limits |
| `data/modelform_M1_M2.csv`, `data/fourway_M1_M2.csv` | M1/M2 sensitivity; the four-way table |
| `data/time_values_t1_F1_M2.csv`, `time_orders_t1_F1_M2.csv`, `time_errors_vs_finer_reference_t1_F1_M2.csv`, `time_rms_history_t0_1_F1_M2.csv` | temporal study at t = 1, F = 1, M2 |
| `data/bdf2_transient_spatial_t1_M2.csv`, `bdf2_transient_spatial_t1_orders.csv`, `bdf2_transient_spatial_t1_crossF_ux.csv` | BDF2 transient spatial study at t = 1 (dt 0.005, F = 0.5 to 4; solver repo commit 7b4e4e1, code 1484d94), orders and limits, cross-F coincidence table |
| `data/earea_ratio_reconciliation.csv` | E-AREA / M2 ratios, like-for-like (same triple) against mixed-level |
| `data/s4f_time_sensitivity_t1.csv` | solids4foam time-step sensitivity at t = 1 (no order identified) |
| `data/interface_force_bins_M2_F4.csv` | M2 load on the solid per 15-degree bin, F = 4 / x4 (coupled and fixed-shape fluid) |
| `data/force_conservation_evidence.csv`, `data/uy_sensitivity_chain.csv` | closure, transmission and power evidence; the chain behind the 0.7% uy gap |
| `scripts/convergence.py` | the campaign's convergence routine, copied unchanged (67 lines of standard-library Python) |
| `scripts/analyze_steady.py` | regenerates `steady_convergence`, `steady_crosscode`, `modelform`, `fourway` CSVs from `steady_levels.csv` |
| `scripts/make_figures.py` | figures from the CSVs (numpy, matplotlib) |
| `figures/` | `fenicsx_blob_spatial`, `fenicsx_blob_temporal`, `fenicsx_blob_transient_spatial` (pdf, png) |

Not included: raw solver histories, state dumps, meshes (regenerated and hash-checked, see below), the solver source.

## Reproduce the tables and figures
```
cd paper-data/fenicsx_blobintreacle
python3 -I scripts/analyze_steady.py   # rewrites the derived CSVs (standard library only)
python3 -I scripts/make_figures.py     # needs numpy and matplotlib
```
The derived CSVs reproduce the sign-off values (e.g. M2 u_x p 1.414, limit 0.120286, GCI 0.0477 %; M1 u_x p 1.519, 0.129372, 0.0319 %). The transcribed inputs were spot-checked against raw histories by the reviewer (10+ values, no discrepancy).

## Provenance
- Solver: monolithic ALE FSI, DOLFINx 0.10.0, unknowns (u Q2, p Q1, d Q2) on one mesh; PETSc SNES. The solver repository (`fenicsx-fsi-verification`) is not part of this PR; commits below refer to it.
- Frozen code commits: **c8a4b0a** (M2-BE, F = 0.5, 1, 2, dt 0.01, t = 10; BE time study); **1484d94** (M2-BE F = 4, dt 0.04, t = 6; BDF2 levels dt 0.04 to 0.005; differs from c8a4b0a only in options that default to the old behaviour); **6f85a48** (M1 via `run_blob_b1.py`, B1 study; consistent CN); **d17df8b** (BDF2 dt 0.0025 and 0.00125 references); **9f4b6e8** (CN with `--theta-pressure-geometry`); **722429d** (restart tests); solids4foam **1576edcc4**, OpenFOAM v2512 (E-AREA is a user library, upstream untouched: 26 md5 sums re-checked).
- Mesh sha256 (quad meshes `meshes/generated/blob_f*_quad.msh`):
  - F0.5 `39eebdbb51f85406dc6e252d5e452a5fddd947f130a0432b544b3129aa521a80`
  - F1 `2c8ce4d9fdc712a472c79562a2c6c518e96b321582735c8d1196f66e732d5c26`
  - F2 `599a81e64ca630c6356b1fe170570debcdde811b2b860d84cd8f490bb7147796`
  - F4 `50e9ac2d4e693dd1f1b5564cce2b60561895af3fcddeb6124fd10b7c30b6507e`
- Environment: micromamba env `fenicsx010` from an explicit lock (python 3.11.15, dolfinx 0.10.0, basix 0.10.0, ufl 2025.2.1, PETSc/petsc4py 3.25.6 real, MUMPS 5.8.2, hypre 3.2.0, numpy 2.4.6, MPICH 5.0.1, mpi4py 4.1.2); lock file sha256 prefix `72764221...b33`, wrapper `environment/run_in_env.sh` sha256 prefix `321dc817...006`.
- Launcher / Slurm: `slurm/submit_run.sh` -> `slurm/job.sbatch` (partition `main`, `-n N -c 1`, N = 2, 4, 8 for F = 1, 2, 4), `run_in_env.sh mpiexec -n N python3 -u slurm/launch_driver.py ...`, node xenosim (shared). Each run directory has `SUBMIT_CMD`, `HOST.txt`, `MANIFEST.json` (code commit, input hashes) and `EXIT` written by the driver (the driver status, not Slurm's, is authoritative: a Slurm "COMPLETED" job with solver rc 1 occurred once on the solids4foam side and is recorded).
- Example command (M2, F = 1, backward Euler): `run_blob.py --mesh blob_f1_quad.msh --dt 0.01 --t-end 10 --theta 1.0 --interface-measure M2 --diag`; M1 uses `run_blob_b1.py ... --interface-measure M1 --dt 0.04 --t-end 6`; BDF2 runs `--theta 0.5 --fluid-scheme bdf2`.
- Cost: FEniCSx campaign 46.9 CPU-h (all jobs including failed and cancelled; M1 mesh study 3.2 CPU-h, M2 backward-Euler family 13.2 CPU-h); solids4foam side runs about 2.2 CPU-h for the t = 1 time series plus the regenerated mesh series.
- Preregistrations (26, sha256 files all re-verified) are in the solver repository.
- Reproduction check: fresh archives of c8a4b0a and 6f85a48 reproduce the F = 1 runs to 4e-15 relative at every step.

## Mixed composition of the M2 sequence (disclosed)
F = 0.5, 1, 2: dt 0.01, t = 10, commit c8a4b0a; F = 4: dt 0.04, t = 6, commit 1484d94. The steady states are time-step independent to <= 4e-10 (8 printed digits), so the mixture does not enter the GCI at the printed level. Pinned and unpinned MPI wrappers were used (speed only). `git_dirty=true` in some manifests is from deleted environment symlink files only.

## What is not claimed
No second-order temporal convergence for blobInTreacle; no independent verification (different group); no statement that M1 or M2 is the correct model, or that solids4foam is defective; no uy agreement within a propagated uncertainty (it agrees to 0.7 %, not resolved below about 1 %); no cross-code transient agreement (the t = 1 u_x limits differ by 1.41 x combined GCI; u_y and F_x not accepted; the time error at dt = 0.005 is not isolated) and no interface-shape comparison; the x-force statement is a difference between the fluid-reported force on the current surface and the solid-applied force on the reference areas, not an unconditional physical force loss; E-AREA is a same-lineage diagnostic, not a verification of the coupling; no level-3 claim.

## Known open points (from the review)
Pointwise stress closure misses by 1.9 to 2.9 % (explained as a corner strong-form defect, about h^0.6; the fluid-side weak-vs-facet difference and the M2 correction-term share of the base reaction are not decomposed); x4 E-AREA level not run; Liu steady/transient values not obtained from the journal article; run directories `runs/a1_*` of the solver repository untracked at the review date and two R1 reference run directories (one used) not yet recorded in its failed-runs register; no review by a human outside the lineage.
