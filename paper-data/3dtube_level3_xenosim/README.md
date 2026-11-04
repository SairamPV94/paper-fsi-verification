# 3dTube levels 1-3, second-platform replicate (2026-11-04)

- Host: xenosim (Ubuntu, 24 ranks direct), OpenFOAM v2512 (system package), GCC 11.4 `-O3`, PETSc 3.24.1.
- solids4foam: `b200718f4` (development, contains #546) plus the 3dTube verification directory from `c45b30b7e` (branch `verification/3dtube-level3`; probe shift `--probe-z-shift 7.8125e-5`; ported in solids4foam PR #660).
- Command: `./Allverify` mesh study, robin coupling, backward time scheme, levels 1-3, dt halved with the mesh.
- Wall clock: 268 s, 1689 s, 21184 s.

| Level | u_r,max (mm) | u_z,min (mm) | t_arr (ms) | c_p (m/s) | MeluXina c_p |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.15978 | -0.08819 | 5.873 | 4.654 | 4.654 |
| 2 | 0.15946 | -0.08659 | 5.843 | 4.635 | 4.635 |
| 3 | 0.15851 | -0.08571 | 5.825 | 4.598 | 4.594 |

The displacements and arrival time match the MeluXina run (OpenFOAM v2412, `-O2`, 128 ranks) to all reported digits on every level; c_p on level 3 differs by 0.09 %.
The driver returns rc 1 because of its monotonicity checks on u_r,max and c_p (the changes grow), as on MeluXina; this is not a run failure.
