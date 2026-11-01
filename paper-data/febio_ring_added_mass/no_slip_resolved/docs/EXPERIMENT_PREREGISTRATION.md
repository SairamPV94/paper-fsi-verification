# Experiment preregistration, round 1 (diagnostic): what creates energy in the no-slip FEBio runs?

Hashed before any round-1 input is run. This is a NEW investigation; the verdict on the earlier graded pilot is unchanged: G1 FAILED its original gate N1 (p_noise 0.2777 versus limit 0.1760), G2 and G3 were not run, and none of that is reinterpreted here.

## 1. Evidence that motivates the round (existing data, `forensic/`)
Energy accounting from stored nodal and element output (`scripts/forensic_energy.py`): ring KE with the consistent mass matrix, ring strain energy (hex8, small strain), fluid KE of the absolute velocity (mesh velocity plus w) with the consistent mass matrix, compressive energy sum V p^2/(2K), and the time integral W of the viscous dissipation 2 mu eps:eps (8-point Gauss, absolute velocity). Creation measure Gamma = (E_tot(4T) + W(4T)) / E_0 - 1; a conservative closed system has Gamma = 0 (dissipation only lowers E_tot).
| Run | Gamma | max E_tot/E_0 | note |
|---|---|---|---|
| C2 (uniform, free-slip) | +1.3e-5 | 1.0001 | accounting validated: conserved to 1e-5 |
| G0 (graded, free-slip) | +6.7e-6 | 1.0001 | same |
| D4 (uniform, no-slip) | +2.6e-2 | 1.068 (min 0.956) | large swings |
| G1 (graded 4 delta, no-slip) | +1.41e-2 | 1.0057 | mechanical energy rises monotonically while viscous dissipation 8.5e-3 E_0 accrues |
So the negative fitted decay of G1 corresponds to a genuine energy imbalance in the stored fields, not an artefact of the damping fit or of the kinetic-energy sampling. (The accounting uses reference-geometry integration and a one-element-gradient dissipation; its residual on the free-slip runs is 1e-5.)

## 2. Competing hypotheses and the controlled tests
All runs: moderate regime (rho_f 140, nu 1e-7), ring 4 x 48, tangential fluid cells 48, fluid radial mesh = the G1 grading (32 cells, first cell 4 delta = 1.3317e-3 m), K 1e8, E_mesh 1e-3, rhoi 1, 100 steps per period, 4 periods, compatible initial velocity, tolerances unchanged, pristine v4.13, two cores, unless the row says otherwise. One parameter differs from G1 in each run. Role: **diagnostic** (none can by itself support final verification).

| ID | Change relative to G1 | Hypothesis tested | Prediction if the hypothesis is true |
|---|---|---|---|
| E1 | wall no-slip, interface free-slip | creation comes from the rigid-wall layer | Gamma(E1) at least 3e-3 and Gamma(E2) below 1e-3 |
| E2 | wall free-slip, interface no-slip | creation comes from the fixed-w interface (source audit: the w-row reaction at fixed-w interface nodes is not transmitted to the ring; the ring receives only the surface traction) | Gamma(E2) at least 3e-3 and Gamma(E1) below 1e-3 |
| E3 | no-slip both, `--ic impulsive` (fluid at rest, the tutorial's start) | the compatible initial field (stationary rotational correction, 1.33x analytic fluid KE) drives the creation | Gamma(E3) below 30 % of Gamma(G1) = 1.41e-2 (that is, below 4.2e-3) |
| E4 | no-slip both, dt halved (200 steps per period) | time-integration error of the midpoint rule | Gamma(E4) at most one half of Gamma(G1) |
| E5 | no-slip both, K = 1e7 | compressibility amplification | Gamma changes by a factor of at least 3 from E5 (K 1e7) to E6 (K 1e9) |
| E6 | no-slip both, K = 1e9 | same | same |
If E1 and E2 both exceed 3e-3, both walls contribute; if neither does, the creation requires the combination (or an unlisted cause).
Interpretation rules (fixed now): a hypothesis is called SUPPORTED only if its prediction holds and no other row's prediction contradicts it; otherwise INCONCLUSIVE. Failing a prediction REFUTES that hypothesis only for the tested change and range. Ratios use Gamma computed identically for every run. No threshold is changed after results.

## 3. Secondary measures reported for every run (no pass/fail)
omega_fit, wet/dry ratio against B1 and error against the inviscid A and the finite-viscosity V references, fitted decay rate against alpha_V = 4.7483e-4 s^-1 (verified: displacement-amplitude rate, eigenvalue convention s with exp(st); interface layer about 78 % and rigid wall about 22 % of the physical damping), energy history, n = 0 and n = 2 pressure components, and the geometric fluid-area change against the mean dilatation.

## 4. Controls and stop conditions
- Controls already on record: G0 (free-slip, Gamma 6.7e-6), G1 (no-slip), D4 (uniform no-slip). No new stock control is needed because the executable is unchanged (sha256 f5ae1ed6...).
- A run that fails to converge or logs Jacobian/NaN messages is reported as failed and is not rerun with altered settings.
- Round 1 costs at most about 1.5 CPU-h (six runs, two cores, 8 to 16 minutes each); a limit of 4 CPU-h is set for the round. Further rounds require a new preregistration based on the round-1 result.
- No source change is made in round 1.
