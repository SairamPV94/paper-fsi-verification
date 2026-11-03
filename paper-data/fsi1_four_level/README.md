# Hron–Turek FSI1: four-level study (November 2026)

- **Build:** solids4foam `a421f063d` (contains #546 and #492), OpenFOAM v2512, GCC 13.3 `-O2 -fno-tree-vectorize -march=znver2`, PETSc 3.22.0, MeluXina (`/project/home/p201287/philip/qm-a421`).
- **Case:** the TurekHron2006 tutorial driver, `./Allverify --benchmark fsi1 --levels N`.
  - `setup.py` sets refinement factors 1, 2, 4, 8 at a fixed Δt = 0.00625 s, plus a 4x run at 0.0125 s (`L4dt2`).
  - It adds the strict coupling test: `requireAllResidualMeasures yes`, `outerCorrTolerance 1e-5`, `outerCorrAbsoluteTolerance 1e-10`.
  - IQN-ILS, fluid tolerance 1e-9, pseudo-transient to t = 30 s, coupling from t = 2 s.
- **Jobs:** 5414227 (1x), then 5414290 (2x, 4x, 4x at double Δt, 8x). For job 5414290 the binding policy is `none`, so the four mpiruns don't share cores.
- **8x restart:** 8x reached t = 29.16 s at the 24 h limit. Job 5417839 continued it from the fields written at t = 28 s. `merge.py` joined the monitors (original rows to t = 28, restart rows after), and the driver evaluated with `--reuse`. In `fsi1_sweep.csv`, `execution_time` for 8x is the restart part only; the total is ≈ 24 h + 1.1 h on 64 ranks.
- **Data:** `fsi1_sweep.csv` is the driver output, one row per run. `*_spread` is the relative range over the last 20% of the run.

| Level | cells | u_x (m) | u_y (m) | drag (N/m) | lift (N/m) |
|---|---:|---:|---:|---:|---:|
| 1x | 5 966 | 2.21610e-5 | 7.04044e-4 | 14.18900 | 0.803432 |
| 2x | 23 864 | 2.25073e-5 | 7.82834e-4 | 14.26281 | 0.775593 |
| 4x | 95 456 | 2.26676e-5 | 8.08557e-4 | 14.28862 | 0.766626 |
| 8x | 381 824 | 2.27468e-5 | 8.15595e-4 | 14.29770 | 0.764138 |
| 4x, Δt × 2 | 95 456 | 2.26649e-5 | 8.08536e-4 | 14.28836 | 0.766619 |
| Featflow 6+1 | | 2.270493e-5 | 8.208773e-4 | 14.29426 | 0.763746 |

Observed orders (1x–2x–4x / 2x–4x–8x):

| Quantity | Orders | Richardson value (2x–4x–8x) | vs Featflow | 8x GCI (Fs 1.25) |
|---|---|---|---:|---:|
| u_x | 1.11 / 1.02 | 2.2824e-5 | +0.52% | 0.42% |
| u_y | 1.61 / 1.87 | 8.1825e-4 | −0.32% | 0.41% |
| drag | 1.52 / 1.51 | 14.3026 | +0.06% | 0.04% |
| lift | 1.63 / 1.85 | 0.76318 | −0.07% | 0.16% |

- **Featflow u_x** decreases with refinement over its six levels: 2.2871, 2.2774, 2.2732, 2.2716, 2.2708 and 2.2705e-5. Ours increases, so the two sequences approach the limit from opposite sides.
- **Δt:** doubling the pseudo-time step at 4x changes every quantity by at most 0.012%.
- **Steady state:** relative spread over the last 20% of each run is at most 2.2e-4 (lift, 8x) and ≤ 4e-6 for the displacements.
