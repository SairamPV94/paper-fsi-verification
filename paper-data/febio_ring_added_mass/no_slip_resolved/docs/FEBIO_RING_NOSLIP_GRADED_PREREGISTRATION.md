# Preregistration: ringAddedMass graded-mesh no-slip pilot (G0 to G3)

Written and hashed before any G-run exists. Nothing below may change after the first numerical result. Approved scope: at most four FEBio v4.13 runs, moderate regime (rho_f = 140), hard cap 3 allocated CPU-hours, no source change, plugin, PR push or manuscript edit.

## 1. Question and hypothesis
Principal hypothesis (not assumed true): the -6.16 % (D4, uniform M1, E_mesh 1e-3) no-slip wet/dry ratio error is predominantly a spatial-resolution artefact of the imposed no-slip conditions, so it should shrink systematically as the near-wall layers are refined towards the physical Stokes layer. Competing readings remain open (initial-condition vorticity, hard-constraint locking independent of resolution, compressibility interaction).

## 2. Models (everything except the radial fluid-node spacing and the wall/interface conditions is identical across runs)
Generator `tools/make_ring_feb.py` with the new options `--fluid-grading two-sided --h1 <m> --nrf <n>` (default behaviour unchanged; regeneration of the C2 M1 input must be byte-identical, verified before submission). Common flags as the C2 M1 baseline: `--rho-f 140 --k 1e8 --e-mesh 1e-3 --rhoi 1 --steps-per-period 100 --periods 4 --ic potential --ic-field compatible --ic-mode pernode`, dt = T_ref/100 with T_ref from the inviscid wet omega 1.80451344 (dt = 0.0348193 s), tolerances dtol = vtol = ftol 1e-6, etol 1e-8, rtol 1e-10, ring mesh 4 x 48, tangential fluid cells 48, nu_f = 1e-7 (mu = 1.4e-5 Pa s).

| Run | BCs | First fluid cell h1 | Radial fluid cells (nrf) |
|---|---|---|---|
| G0 | `--wall slip --interface slip` | delta/4 | 52 |
| G1 | `--wall noslip --interface noslip` | 4 delta | 32 |
| G2 | no-slip, no-slip | delta | 42 |
| G3 | no-slip, no-slip | delta/4 | 52 |

delta = sqrt(2 nu_f / omega_inviscid_wet) = 3.3292e-4 m (omega 1.80451344). Two-sided geometric grading: h1 at both the interface (r = 1.05) and the outer wall (r = 1.5), growth ratio solved for each case, meeting at mid-gap. Geometry and node-set definitions are unchanged. Two cores per run (the uniform M1 baselines used one core; the Newton path may differ at round-off, which is disclosed, not corrected for).

## 3. References, kept separate
- **A, exact inviscid:** omega_wet 1.8045131724, ratio 0.7062557226 (reference JSON).
- **V, exact finite-viscosity linear:** reference script `ring_exact_frequencies.py` (linearised incompressible Navier-Stokes, no-slip on both walls, thin-Stokes-layer Bessel expansions). Eigenvalue s with displacement ~ exp(s t); damped frequency 1.804038745 rad/s, frequency shift -2.6291e-4 relative to A, damping ratio zeta = -Re(s)/|s| = 2.6320e-4. Amplitude decay rate alpha = zeta |s| = 4.7483e-4 s^-1 (displacement amplitude e-folding rate; per-period loss 1 - exp(-alpha T) = 1.652e-3 at T = 3.4828 s). Viscous ratio target 0.7060700 = ratio_A x (1 - 2.6291e-4); the dry ring has no viscous term. These values were re-derived from the script's definitions above before use; the target applies to the linear problem, and FEBio is run at finite amplitude (V0 = 1.5e-3 m/s).
- **S, solids4foam data** (`reference/pr13_ringAddedMass`, moderate regime, standard solid): ratio errors against A of -0.0158 / -0.00156 / -0.000093 % (QM) and +0.0689 / +0.0181 / +0.0051 % (IQN-ILS) at mesh factors 1/2/4, 100 steps per period; fitted decay rate 1.22e-4 s^-1 (monolithic, factor 2, n100). These are printed as given, compared separately, and never substituted for A or V. The solids4foam decay rate is about a quarter of V's alpha, so the S data do not themselves contain the physical viscous damping; this is stated, not used to relax any criterion.
- Matched dry ring: B1 (hex8 ring 4 x 48, omega 2.621064). Reuse is justified because the ring mesh, material, integrator and tolerances are identical; the dry run has no fluid. The dry run's own dt is T_dry/100 (as in the existing matched-dry usage).
- Baselines on record: D4 (uniform M1, no-slip, E_mesh 1e-3) ratio error -6.16 %; C2 M1 (uniform M1, slip/slip, E_mesh 1e-3) omega_fit 1.851253855, ratio 0.7062987562, ratio error +0.0060930 %.

## 4. Metrics (all runs): omega_fit by the existing damped-harmonic fit over 0-4T, ratio against B1, ratio error against A and against V, fitted decay rate and implied alpha, n = 2 and n = 0 pressure harmonics (`tools/pressure_modes.py`), interface leakage (`tools/interface_leakage.py`; identically zero by construction for no-slip, so reported as n/a), ring velocity consistency, mean(J-1), kinetic energy at integer periods, integrated n = 2 interface force against the analytic loading with the layer-0 profile correction, viscous shear traction at the interface (reported, no pass/fail), Newton statistics, Jacobian and conditioning (minimum scaled Jacobian and maximum aspect ratio computed from the input mesh; no external conditioning estimate), wall time, CPU-seconds and RSS.

## 5. Gate 1 (G0, free-slip graded control). All must hold
- G0.1 |ratio error(G0) - 0.0060930 %| < 0.02 percentage points (absolute change in the ratio error).
- G0.2 400/400 steps converged, no Jacobian/NaN/inversion messages, no "max iterations reached" events.
- G0.3 Interface leakage rms (normalised by the ring's normal velocity) <= 2 %, max <= 10 % of V0, net flux <= 1 %.
- G0.4 max |mean(J-1)| <= 1e-7; n = 0 pressure at omega <= 0.03 Pa.
- G0.5 Pressure noise (`p_noise_rel`) not more than twice the C2 M1 value or 10 %, whichever is larger.
- G0.6 Integrated n = 2 force within 5 % of the analytic loading (profile-corrected).
- G0.7 Minimum scaled Jacobian of every element >= 0.5 in the generated mesh (orthogonal polar grid; checked before submission).
If any item fails: STOP; no no-slip run is launched.

## 6. Gate 2 (no-slip) and run order
G1 is launched only if G0 passes. G2 only if G1 is numerically sound (N1 below). G3 only if G1 and G2 are sound and N2 holds for D4 > G1 > G2 in magnitude of ratio error against A. If G2's |ratio error vs A| is not smaller than G1's, G3 is not launched without a new scientific justification and approval.

## 7. No-slip acceptance criteria (evaluated per run where applicable; G3 is the finest case)
- N1 (soundness, every run): 400/400 steps converged, no Jacobian/NaN/inversion messages, max |mean(J-1)| <= 1e-7, n = 0 pressure at omega <= 0.1 Pa, p_noise_rel <= 3 x the G0 value. Failure of N1 stops the series.
- N2 (monotone convergence): |ratio error vs A| strictly decreasing along D4 (6.16 %), G1, G2, G3.
- N3 (finest case): |ratio error vs A| <= 0.1 % for G3, and |(ratio - 0.7060700)/0.7060700| <= 0.1 % (V) for G3.
- N4 (viscous damping): G3 fitted decay rate within 0.7 to 1.3 times alpha_V = 4.7483e-4 s^-1. G1 and G2 are reported against the same target without pass/fail.
- N5 (consistency): ring velocity consistency rms(v - du/dt)/peak <= 1 % for G3; the integrated n = 2 interface force within 5 % of the analytic loading for G3.
- N6 (solver): mean Newton iterations per step <= 8 and no Jacobian/NaN messages for G3.

## 8. Classification rule (fixed now)
- LIKE-FOR-LIKE COMPARISON SUPPORTED: G0 passes and G3 passes N1 to N6 (including damping), with N2 monotone, and the initial-condition difference stated explicitly. Because the initial condition differs from the tutorial's (compatible potential-plus-correction flow here, fluid at rest there), the wording will say the boundary conditions, material and viscosity match and the initial condition does not.
- QUALIFIED COMPARISON: N2 and N3 pass but N4, N5 or N6 fail, or G3 was not run because of a numerically sound but earlier stop.
- DIAGNOSTIC DISCREPANCY: runs are numerically sound but N2 or N3 fails (the error does not decrease or stays outside 0.1 %).
- NOT ESTABLISHED: G0 fails, any run is unsound, or the budget or stop rule ends the pilot before N3 can be assessed.
Closeness of omega or ratio alone never yields the first class.

## 9. Resource rules
Slurm via `tools/submit_guarded.sh`, 2 cores per run, time limit 40 min per run, runs submitted sequentially (never all four at once), cap 3 allocated CPU-hours (counted from sacct elapsed x allocated CPUs for these job IDs only), ledger rows in `MULTIBENCHMARK_JOB_LEDGER.csv`. Allocated CPU-hours are verified after each run. Unrelated account jobs are not charged here and `campaign_budget.py`'s global result is not used.

## 10. Equivalence caveats declared in advance
Initial condition differs (see section 8); the fluid is weakly compressible (K = 1e8) versus incompressible; the mesh-motion device differs (massless neo-Hookean E_mesh = 1e-3 Pa versus mesh diffusion); the solid formulation differs (FEBio hex8 versus the high-order solid used for the published solids4foam results); the solids4foam no-slip is applied through the viscous flux on an unresolved uniform mesh. If exact continuum equivalence cannot be shown, the report states why and does not claim it.
