# Experiment preregistration, round 2 (diagnostic and exploratory)

Hashed before any round-2 input is run. Round 1 outcomes are fixed in `NUMERICAL_RESULTS.md`; none is reinterpreted here.

## Round-1 facts that motivate round 2 (existing data)
- Energy creation Gamma = (E_tot(4T) + W(4T))/E_0 - 1: G0 6.7e-6, E1 (wall no-slip, interface slip) 1.2e-5, E2 (wall slip, interface no-slip) 5.8e-4, G1 (both no-slip) 1.41e-2, E4 (dt halved) 1.42e-2, E5 (K 1e7) 1.17e-2. Neither boundary alone creates energy; the viscous dissipation of G1 (8.4e-3 E_0) equals the sum of E1 and E2 (1.9e-3 + 6.6e-3), at about 65 % of the physical dissipation 2 alpha_V T_4 = 1.3e-2. E3 (fluid at rest) kept the negative fitted decay (-2.46e-4 s^-1).
- Preregistered round-1 outcomes (literal): H-wall-only and H-interface-only NOT supported (neither alone exceeds 3e-3); H-dt REFUTED (ratio 1.0 against the threshold 0.5); the compatible initial field is not the cause of the negative decay; K 1e7 versus 1e9 test INCONCLUSIVE because E6 (K 1e9) failed at the first step on the convergence floor.

## Round-2 hypotheses (one parameter changed relative to G1 per run; moderate regime, E_mesh 1e-3, K 1e8, rhoi 1, 100 steps per period, compatible initial velocity, both boundaries no-slip, pristine v4.13, two cores)
| ID | Change relative to G1 | Hypothesis | Prediction |
|---|---|---|---|
| F1 | radial grading first cell delta (nrf 42), tangential and ring mesh unchanged | creation is a near-wall radial-resolution artefact | Gamma(F1) < 0.5 Gamma(G1) = 7.0e-3 |
| F2 | first cell delta/4 (nrf 52) | same | Gamma(F2) < Gamma(F1), Gamma(F2) < 3e-3, fitted decay positive |
| F3 | tangential and ring resolution doubled (mesh factor 2: ring 8 x 96, 96 tangential fluid cells), G1 radial grading (nrf 32, first cell 4 delta) | creation depends on tangential resolution | Gamma(F3) <= 0.5 Gamma(G1) |
Rules: a hypothesis is SUPPORTED if its prediction holds; REFUTED if Gamma stays at or above 0.7 times Gamma(G1) (F1, F3) or Gamma(F2) is at least 0.7 Gamma(G1); otherwise INCONCLUSIVE. These runs are diagnostic and exploratory and cannot alone support a verification claim. Ratio errors, damping and conservation are reported for every run without pass/fail. A run that fails to converge is reported and not rerun with changed settings. Budget for the round: at most 2.5 CPU-h; no source change.
