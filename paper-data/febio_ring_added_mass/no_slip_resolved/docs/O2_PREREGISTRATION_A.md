# Overnight-2 preregistration A: ringAddedMass weak, moderate and strong regimes, no-slip, tutorial initial state

Hashed before any run of this stage. Inherits (does not reopen) the earlier campaign's findings and the failed G1 gate. All runs: pristine FEBio v4.13 (sha256 f5ae1ed6f347...), no source change, no-slip on the interface (w = 0) and the rigid wall (w = 0), nu 1e-7, K 1e8, E_mesh 1e-3, rhoi 1, ring 4 x 48 (f1) or 8 x 96 (f2), 48 or 96 tangential fluid cells, two-sided radial grading with first cell delta/4 at BOTH the interface and the wall and 52 radial cells (growth about 1.29), delta = sqrt(2 nu/omega_inviscid) recomputed per regime: weak 2.866e-4 m, moderate 3.329e-4 m, strong 5.101e-4 m (first cells 7.165e-5, 8.323e-5, 1.275e-4 m). Production initial state: **fluid at rest** (`--ic impulsive`), ring initial velocity as the tutorial. The compatible-potential start is run only as a separately labelled diagnostic (D runs). dt = T_wet/100; 4 periods; role of every run below: confirmatory unless labelled.

## References per regime (from the reference JSON; viscous values re-derived by the reference script)
| regime | rho_f | inviscid ratio A | viscous shift | ratio V = A(1+shift) | alpha_V = zeta |s| (s^-1) |
|---|---|---|---|---|---|
| weak | 14 | 0.9532582 | -4.123e-5 | 0.9532189 | 1.0053e-4 |
| moderate | 140 | 0.7062557 | -2.629e-4 | 0.7060700 | 4.7483e-4 |
| strong | 1400 | 0.3008383 | -7.308e-4 | 0.3006184 | 5.621e-4 (zeta 7.318e-4, |s| 0.76809) |
Dry ring: B1 (f1), D1 (f2), C1_dt200_dry_f1 (paired dry at half dt), same ring mesh, material, integrator.

## Runs and predictions
| ID | Regime | Mesh | Variation | Role |
|---|---|---|---|---|
| Pw1, Pm1, Ps1 | weak, moderate, strong | f1 | rest IC (production) | confirmatory |
| Pw2, Pm2, Ps2 | same | f2 | rest IC | confirmatory (ring/tangential level) |
| Pwt, Pmt, Pst | same | f1 | rest IC, dt halved (200 steps per period) | confirmatory (temporal) |
| Dw, Ds | weak, strong | f1 | compatible-potential IC | diagnostic (energy accounting, IC comparison; moderate diagnostic F2 exists) |
Criteria (fixed now; applied to each regime separately):
- C1 ratio: |ratio error against V| at most 0.1 % (the official ratio tolerance) for Pw1, Pm1, Ps1 and Pw2, Pm2, Ps2; reported against A and V separately.
- C2 damping: fitted displacement-amplitude decay rate within 0.7 to 1.3 times alpha_V for f1 and f2 runs. The fit uses the whole window 0-4T; the start-up transient is quantified by also fitting T-4T and reported, not removed from the criterion.
- C3 temporal: change of the ratio against V between Pw1/Pm1/Ps1 and Pwt/Pmt/Pst, with the matched paired dry run (C1_dt200_dry_f1 for the half-dt wet run), at most 0.01 pp; change of the decay at most 10 %.
- C4 ring/tangential: change of the ratio against V from f1 to f2 at most 0.02 pp (weak, moderate) and 0.05 pp (strong, where the free-slip amplitude floor was largest).
- C5 energy (diagnostic runs only; Gamma as before): Dw, Ds with Gamma at most 5e-3 and no negative decay.
- C6 soundness (all runs): 400/400 steps (800 for Pwt/Pmt/Pst), no Jacobian/NaN/inversion messages, mean(J-1) at most 1e-7.
The fluid-at-rest start launches an acoustic transient; it is not removed. A run that fails to converge is reported and not rerun with changed settings (a different parameter change would be a new registered study). A failed criterion is reported and not retuned.
Budget for this stage: at most 40 CPU-h; at most 16 concurrent cores (the cluster had 32 idle cores at start and other users' jobs are running).
