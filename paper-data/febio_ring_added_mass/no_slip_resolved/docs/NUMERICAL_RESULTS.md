# Numerical results (all runs of this campaign; moderate regime, pristine FEBio v4.13, sha256 f5ae1ed6...)

Hash-dated preregistrations: `EXPERIMENT_PREREGISTRATION.md` (round 1, 02:48:08Z), `_R2.md` (03:06:14Z), `_R3.md` (03:25:52Z), `_R4.md` (04:02:35Z); hashes in `PREREG_ROUND*.sha256`. References: A = exact inviscid ratio 0.7062557; V = finite-viscosity linear ratio 0.7060700 (alpha_V = 4.7483e-4 s^-1). Gamma = (E_tot + W_diss)/E_0 - 1 at 4T (a conservative closed system has 0; accounting validated on free-slip runs to 1e-5, uncertainty about 1e-3 for resolved no-slip runs). Matched dry run: B1 (factor 1), D1 (factor 2), C1_M3_dry_f4 (factor 4); noted otherwise. Script `scripts/results_table.py`; CSV `results_table.csv`.

## 1. All runs
| ID | Change | omega | err vs A % | err vs V % | alpha/alpha_V | Gamma | n=0 amp (Pa) | p_noise | Newton/step | CPU-s |
|---|---|---|---|---|---|---|---|---|---|---|
| G0 | free-slip/free-slip, graded 52 cells, h1 d/4 | 1.85125 | 0.0061 | 0.0324 | 0.003 | 6.69e-06 | 0.0000 | 0.059 | 4.01 | 1654 |
| G1 | no-slip both, 4 d, 32 cells | 1.84830 | -0.1535 | -0.1272 | -0.473 | 1.41e-02 | 0.0527 | 0.278 | 4.00 | 922 |
| E1 | G1 with interface free-slip | 1.85100 | -0.0074 | 0.0189 | 0.092 | 1.20e-05 | 0.0000 | 0.063 | 4.00 | 1024 |
| E2 | G1 with wall free-slip | 1.85039 | -0.0405 | -0.0142 | 0.274 | 5.84e-04 | 0.0000 | 0.058 | 4.00 | 988 |
| E3 | G1 with fluid at rest (tutorial IC) | 1.84717 | -0.2144 | -0.1881 | -0.517 | -4.61e-02 | 0.0059 | 6.910 | 4.00 | 932 |
| E4 | G1 with dt/2 (ratio vs B1) | 1.84878 | -0.1276 | -0.1013 | -0.472 | 1.42e-02 | 0.0521 | 0.284 | 4.00 | 1806 |
| E5 | G1 with K=1e7 | 1.84721 | -0.2122 | -0.1860 | -0.532 | 1.17e-02 | 0.0053 | 0.069 | 4.00 | 936 |
| F1 | no-slip, h1 = d, 42 cells | 1.85106 | -0.0042 | 0.0221 | 0.556 | 3.12e-03 | 0.0098 | 0.132 | 4.01 | 1306 |
| F2 | no-slip, h1 = d/4, 52 cells | 1.85068 | -0.0249 | 0.0014 | 1.021 | 2.58e-03 | 0.0012 | 0.079 | 4.08 | 1664 |
| F3 | G1 with ring/tangential x2 | 1.81316 | -0.1476 | -0.1214 | -0.444 | 1.39e-02 | 0.0613 | 0.290 | 4.01 | 2070 |
| K1 | F2 with fluid at rest (tutorial IC) | 1.85056 | -0.0311 | -0.0049 | 0.984 | 3.65e-02 | 0.0001 | 6.931 | 4.00 | 1726 |
| K2 | F2 with dt/2 (ratio vs B1) | 1.85116 | 0.0011 | 0.0274 | 1.022 | 2.58e-03 | 0.0012 | 0.106 | 4.05 | 3322 |
| K2p | K2 with paired dry dt/2 (post hoc) | 1.85116 | -0.0249 | 0.0014 | 1.022 | 2.58e-03 | 0.0012 | 0.106 | 4.05 | 3322 |
| K3 | F2 with ring/tangential x2 | 1.81541 | -0.0239 | 0.0024 | 1.014 | 2.74e-03 | 0.0012 | 0.082 | 4.07 | 4048 |
| K4 | F2 with h1 = d/16, 62 cells | 1.85089 | -0.0134 | 0.0129 | 1.034 | -2.34e-03 | 0.0013 | 0.072 | 4.23 | 2198 |
| K5 | F2 with K=1e7 | 1.85063 | -0.0274 | -0.0011 | 1.020 | 6.17e-04 | 0.0001 | 0.073 | 4.09 | 1768 |
| K6 | F2 with E_mesh=1e-2 | 1.85071 | -0.0234 | 0.0029 | 1.021 | 2.57e-03 | 0.0012 | 0.079 | 4.07 | 1562 |
| K7 | F2 with V0 halved (dry V0 halved) | 1.85055 | -0.0317 | -0.0054 | 1.020 | n/a | n/a | 0.027 | 4.12 | 1500 |
| K8 | F2 with ring/tangential x4 | 1.80648 | -0.0237 | 0.0026 | 1.012 | 2.75e-03 | 0.0012 | 0.083 | 4.08 | 11664 |

K6 (E_mesh 1e-3 to 1e-2) uses the K1-K6 baseline F2. K1 and E3: Gamma is not interpretable (the fluid-at-rest start launches an acoustic transient, p_noise about 6.9, so E_0 is not the post-start energy); their frequency and decay fits are unaffected by the energy accounting. K7 uses a dry run at the same halved amplitude. E6 (K = 1e9, G1 mesh) failed at the first step on the dilatation convergence floor (20 CPU-s) and was not rerun with changed settings.

## 2. Outcomes against the preregistered predictions
| Round | Run | Prediction | Result | Verdict |
|---|---|---|---|---|
| 1 | E1 | Gamma(E1) at least 3e-3 and E2 below 1e-3 (wall-only cause) | Gamma 1.2e-5 | not supported |
| 1 | E2 | Gamma(E2) at least 3e-3 and E1 below 1e-3 (interface-only cause, source-audit hypothesis) | Gamma 5.8e-4 | not supported |
| 1 | E1+E2 | if neither exceeds 3e-3: the creation needs the combination | G1 (both) 1.41e-2; W of G1 (8.4e-3) equals W(E1) + W(E2) | combination |
| 1 | E3 | Gamma(E3) below 4.2e-3 (initial field is the cause) | literally met (-4.6e-2) but the metric is not comparable (acoustic start-up); the fitted decay stays negative (-0.517 alpha_V) | not supported as cause of negative decay (metric caveat) |
| 1 | E4 | Gamma(E4) at most half of G1 | 1.42e-2 (ratio 1.0) | refuted |
| 1 | E5, E6 | factor of at least 3 in Gamma from K 1e7 to 1e9 | E6 failed; K 1e7 changed Gamma 1.41e-2 to 1.17e-2 | inconclusive |
| 2 | F1 | Gamma below 7.0e-3 | 3.12e-3 | supported |
| 2 | F2 | Gamma below F1 and below 3e-3, decay positive | 2.58e-3 (below F1, below 3e-3), 1.021 alpha_V | supported |
| 2 | F3 | Gamma(F3) at most 0.5 Gamma(G1) | 1.39e-2 | refuted |
| 3 | K1 | decay 0.7-1.3 alpha_V and error vs V within 0.1 % | 0.984 alpha_V, -0.0049 % | met |
| 3 | K2 | ratio error vs V changes at most 0.01 pp (B1 dry) and decay at most 5 % | ratio changed +0.0260 pp, decay +0.1 % | **failed as registered**; post hoc paired dry dt/2 (existing run C1_dt200_dry_f1): change 0.0000 pp. The omega phase error of 0.026 % is the same in the wet and dry rings and cancels in the ratio |
| 3 | K3 | change at most 0.02 pp, decay at most 5 % | +0.0010 pp, -0.7 % | met |
| 3 | K4 | decay within 10 %, |error vs V| at most 0.02 %, Gamma at most 3e-3 | 1.034, +0.0129 %, -2.3e-3 | met |
| 3 | K5 | change at most 0.02 pp | -0.0025 pp | met |
| 3 | K6 | change at most 0.02 pp | +0.0015 pp | met |
| 4 | K7 | change at most 0.01 pp | -0.0068 pp | met |
| 4 | K8 | within 0.02 pp of K3 and decay within 5 % of K3 | +0.0002 pp, -0.2 % | met |

## 3. What the data establish
1. **The large no-slip errors of the original uniform-mesh runs are a near-wall radial-resolution artefact of the strong no-slip constraints.** Controlled single-parameter ladder with first cell 4 delta, delta, delta/4, delta/16 (all else fixed): ratio error against V -0.127, +0.022, +0.0014, +0.0129 %; fitted decay -0.47, 0.56, 1.02, 1.03 alpha_V; n = 0 pressure amplitude 0.053, 0.0098, 0.0012, 0.0013 Pa; Gamma 1.41e-2, 3.1e-3, 2.6e-3, -2.3e-3. (Uniform 12-cell mesh, D4: -6.16 % against A.) The energy creation requires both boundaries no-slip (E1, E2 conserve), is independent of dt (E4) and of ring/tangential resolution (F3), and the initial field is not its cause (E3).
2. **At resolved near-wall level FEBio reproduces the finite-viscosity linear solution** in frequency ratio (+0.0014 to +0.0026 % against V from factor 1 to 4; -0.0249 to -0.0237 % against A, i.e. the viscous shift -0.0263 % is reproduced) and in damping (1.012 to 1.034 alpha_V), including with the tutorial's fluid-at-rest start (K1, 0.984 alpha_V, -0.0049 %).
3. **Ring/tangential refinement (three levels, factors 1, 2, 4):** the ratio error against V is +0.0014, +0.0024, +0.0026 % (differences 0.0010 and 0.0002 pp; an order is not claimed because these differences are at the fit precision). The absolute frequency error against the viscous omega 1.804039 is +2.585 %, +0.630 %, +0.135 % (difference ratio 3.95, difference-based order 1.98, a consistency check, not a formal order claim).
4. **Sensitivities at the resolved level:** compressibility K 1e8 to 1e7: -0.0025 pp; mesh regulariser 1e-3 to 1e-2 Pa: +0.0015 pp (so at most about 0.0002 pp at 1e-3 by linear scaling); time step halved: ratio change 0.0000 pp with paired dry (the absolute omega moves +0.026 %, a phase error equal in wet and dry); amplitude halved: -0.0068 pp (two amplitudes; an A^2 model extrapolates the linear-limit ratio error against V to about -0.008 %).

## 4. What they do not establish
Interface shear traction (the logged data contain only pressure and volume ratio, so the viscous traction applied to the ring was not measured; only energy dissipation and damping, which integrate it, were); the discrete mechanism by which under-resolved double no-slip creates energy; solids4foam's own boundary-layer-resolved behaviour (its Stokes layer is unresolved at every tested mesh factor and its measured decay is dominated by time-integration damping); the iterative-solver error at the resolved level (no tolerance sweep; E6-type tightening fails on the dilatation floor); the finite-strain versus small-strain term of the solid beyond the dry-ring bound and the amplitude extrapolation; incompressible-limit behaviour beyond K 1e7 to 1e8 (K 1e9 failed in E6 on the G1 mesh and was not retried).
