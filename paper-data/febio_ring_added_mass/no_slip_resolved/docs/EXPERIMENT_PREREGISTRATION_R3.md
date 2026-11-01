# Experiment preregistration, round 3 (controlled sensitivity tests at the resolved near-wall level)

Hashed before any round-3 input is run. Round-2 outcomes (fixed in `NUMERICAL_RESULTS.md`) were: F1 (first cell delta) Gamma 3.12e-3, decay 0.556 alpha_V; F2 (first cell delta/4) Gamma 2.58e-3, decay 1.021 alpha_V, ratio error -0.0249 % against A and +0.0014 % against V; F3 (tangential and ring resolution doubled at 4 delta) identical to G1 (Gamma 1.39e-2, decay -0.444 alpha_V). H-res SUPPORTED (F1, F2); H-tan REFUTED. All of this is exploratory/diagnostic and nothing is reinterpreted.

## Reference configuration
F2: moderate regime, both boundaries no-slip, radial grading first cell delta/4 = 8.3229e-5 m (52 radial cells), ring 4 x 48, 48 tangential fluid cells, K 1e8, E_mesh 1e-3, rhoi 1, 100 steps per period, 4 periods, compatible initial velocity, pristine v4.13. Reference values: omega 1.85068, error against V +0.0014 %, decay 1.021 alpha_V (alpha_V = 4.7483e-4 s^-1), Gamma 2.58e-3. One parameter differs per run. Role: **confirmatory sensitivity tests** (predictions fixed now, controlled single changes).

| ID | Change relative to F2 | Question | Prediction (pass condition) |
|---|---|---|---|
| K1 | `--ic impulsive` (fluid at rest: the tutorial's initial fluid state) | is the result compatible with the tutorial's initial condition once the layers are resolved | decay within 0.7 to 1.3 alpha_V and the ratio error against V within 0.1 % |
| K2 | dt halved (200 steps per period) | temporal error | change in the ratio error against V at most 0.01 pp and change in decay at most 5 % |
| K3 | ring and tangential resolution doubled (mesh factor 2: ring 8 x 96, 96 tangential cells), same radial grading | tangential and ring resolution | change in the ratio error against V at most 0.02 pp and change in decay at most 5 % (ratio against the matched f2 dry run D1) |
| K4 | first cell delta/16 = 2.0807e-5 m, 62 radial cells | convergence under further near-wall refinement | decay within 10 % of alpha_V, ratio error against V at most 0.02 % in magnitude, Gamma at most 3e-3 |
| K5 | K = 1e7 | compressibility | change in the ratio error against V at most 0.02 pp |
| K6 | E_mesh = 1e-2 (ten times larger) | mesh-regulariser contribution | change in the ratio error against V at most 0.02 pp (then the 1e-3 value contributes at most about 0.002 pp by linear scaling) |
Ratio for K1, K2, K4, K5, K6 uses the matched dry run B1 (same ring mesh, material and integrator; its own dt is T_dry/100, a known ratio effect of 9e-5 %). Rules: a prediction that holds is reported as met; one that fails is reported as failed with the measured change and is not retuned. Energy creation Gamma, n = 0 and n = 2 pressure, kinetic-energy history, leakage (zero by construction) and Newton statistics are reported for all runs. A non-converged run is reported and not rerun with changed settings. Budget for the round: at most 6 CPU-h; no source change.
