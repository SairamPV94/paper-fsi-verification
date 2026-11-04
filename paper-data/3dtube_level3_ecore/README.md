# 3dTube levels 1-3, desktop replicate (2026-11-03)

Third independent platform for the `3dTube` mesh study (issue #57, Task 1), after MeluXina and xenosim (`../3dtube_level3_xenosim/`), and the only desktop machine.

## Platform

- Host: ECORE, a single desktop workstation (not a cluster node). AMD Ryzen Threadripper 9970X, 32 cores / 64 threads, 1 socket, 1 NUMA node, 128 MiB L3, 125 GiB RAM.
- OS: Ubuntu 24.04.4 LTS.
- Compiler and MPI: GCC 13.3.0 (`-O3`, OpenFOAM default `linux64GccDPInt32Opt`), Open MPI 4.1.6 (system).
- OpenFOAM v2512 (build `_87ed40d256-20251219`), compiled from source in `/opt/openfoam`.
- PETSc 3.21.2 (OpenFOAM ThirdParty `makePETSC`) with hypre 2.31.0, MUMPS and ScaLAPACK; BLAS/LAPACK: OpenBLAS 0.3.26 (Ubuntu `libopenblas-dev`).
- solids4foam: `b200718f4` (development, contains #546), built against the above, plus the 3dTube verification directory from `c45b30b7e` (branch `verification/3dtube-level3`, for `--probe-z-shift`).
- Environment: `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1` (recorded in `logs/log.environment`).

## Command

```bash
source scripts/env-task1.sh   # OpenFOAM v2512, PETSc, thread settings
./Allverify --levels 1,2,3 --cores 32 --probe-z-shift 7.8125e-5
```

`scripts/run-task1.sh` is the exact launcher (run in tmux). It was a mesh study with robin coupling and the backward time scheme, the time step halved with the mesh, and 32 MPI ranks on every level. The run went from 16:30 to 23:51 on 3 November 2026. The machine was otherwise idle (load average about 0.3 before the start), apart from light desktop applications.

## Results

| Level | u_r,max (mm) | u_z,min (mm) | t_arr (ms) | c_p (m/s) | MeluXina c_p | xenosim c_p |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.15978 | -0.08819 | 5.873 | 4.654 | 4.654 | 4.654 |
| 2 | 0.15946 | -0.08659 | 5.843 | 4.635 | 4.635 | 4.635 |
| 3 | 0.15851 | -0.08571 | 5.825 | 4.597 | 4.594 | 4.598 |

The displacements and arrival time match MeluXina and xenosim to all reported digits on every level. On level 3, c_p (4.5974 m/s) differs from MeluXina (4.5944) by +0.07 % and from xenosim (4.5984) by -0.02 %. All three platforms lie inside the c_p probe-sampling noise of about 0.5-1 % stated in the verification README. All 5600 time steps met the robin convergence criteria (0 unconverged steps).

The driver returns rc 1 because of its monotonicity checks on u_r,max and c_p (the changes grow from level 2 to 3), as on MeluXina and xenosim. This is not a run failure (see `verification_summary.md`).

Level 1 was also run on 16 ranks before the main run. With and without the probe shift, it gave the same four values to all reported digits (c_p 4.654 shifted, 4.663 unshifted).

## Cost (wall clock, 32 ranks)

| Level | Fluid / solid cells | Δt (s) | Steps | Mean FSI iter. | Wall clock (s) | MeluXina (s, ranks) | xenosim (s, 24 ranks) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 16 000 / 6 400 | 2.5e-5 | 800 | 4.78 | 123 | 454 (8) | 268 |
| 2 | 128 000 / 51 200 | 1.25e-5 | 1600 | 3.87 | 1 123 | 2 565 (32) | 1 689 |
| 3 | 1 024 000 / 409 600 | 6.25e-6 | 3200 | 3.18 | 25 166 (6 h 59 min) | 15 317 (128) | 21 184 |

Level 1 does not speed up from 16 to 32 ranks (121-126 s on 16), because 22 400 cells are too few per rank.

## Files

- `mesh_robin_backward_pz7.8125e-05.csv`: driver output, one row per level.
- `mesh_robin_backward_pz7.8125e-05.png`: point-A histories against the published curves.
- `verification_summary.md`: driver checks.
- `logs/log.Allverify`, `logs/log.environment`: the driver log and environment. The solver logs (about 100 MB uncompressed) are not included; they are available on request.
- `scripts/env-task1.sh`, `scripts/run-task1.sh`: environment and launcher.
