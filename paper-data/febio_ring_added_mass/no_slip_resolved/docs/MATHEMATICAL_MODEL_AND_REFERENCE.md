# Mathematical model and reference physics (moderate regime unless stated)

## 1. Continuum problem
Plane-strain elastic ring (inner 0.95 m, outer 1.05 m, E 1e6 Pa, nu 0.3, rho_s 1000) inside a fluid annulus 1.05 < r < 1.5 bounded by a rigid wall. Fluid: Newtonian, nu_f = 1e-7 m^2/s, rho_f 14, 140 or 1400, no-slip on the wall and on the moving ring, incompressible in the benchmark. Mode n = 2: u_r = U(r) cos2t e^{st}, u_t = V(r) sin2t e^{st}.

## 2. Reference values (verified by running `ring_exact_frequencies.py --check` and an independent boundary-layer estimate)
| Quantity (moderate) | Value | Source |
|---|---|---|
| Dry omega | 2.555042 rad/s | JSON |
| Inviscid wet omega, ratio | 1.804513 rad/s, 0.7062557 | JSON |
| Viscous (finite-nu) omega | 1.804039 rad/s | JSON, re-derived |
| Viscous frequency shift | -2.6291e-4 relative | JSON |
| Viscous damping ratio zeta = -Re(s)/\|s\| | 2.6320e-4 | JSON |
| **Displacement-amplitude decay rate alpha = zeta \|s\|** | **4.7483e-4 s^-1** (energy decays at 2 alpha = 9.497e-4 s^-1; per-period amplitude loss 1.652e-3 at T = 3.4828 s) | script and independent estimate |
| Stokes layer delta = sqrt(2 nu / omega) | 3.329e-4 m (weak 2.87e-4, strong 5.10e-4); delta / gap = 7.4e-4 | JSON |
Conventions: eigenvalue s with displacement ~ exp(s t); omega = Im s, alpha = -Re s, amplitude not energy. Verified independently: the thin-Stokes-layer estimate of the cycle-averaged dissipation, with tangential velocity mismatch between the exact potential flow and the ring's own tangential motion at the interface (ring tangential amplitude about 0.77 versus potential 2.94 in units of U_r(Ro) = 1), gives alpha = 4.744e-4 s^-1, within 0.08 % of the script. The interface layer supplies about 78 % and the rigid wall about 22 %. Ignoring the ring's own tangential motion would give 3.36e-4 (29 % low), so the interface condition matters. The earlier preregistration value 4.7483e-4 is correct; no conflicting estimate was found in the project documents.

## 3. What the solids4foam data contain
- The tutorial's Stokes layer is not resolved at any mesh factor: delta/h = 0.0089, 0.018, 0.036 at factors 1, 2, 4 (uniform radial spacing 0.45/(12 f)).
- `decay_rate` is the displacement-amplitude rate (slope of ln |peak| against time) in s^-1, the same convention as alpha. Monolithic, factor 2, moderate: 7.7e-3, 1.07e-3, 1.22e-4 at 25, 50, 100 steps per period (falls about 7x then 9x per halving of dt: time-integration damping). The dry ring at n100 has 7.4e-5. So at n100 the measured decay is about 26 % of the physical alpha and is dominated by numerical damping; the S data do not contain the physical viscous damping, and this holds for n100 only (at n50 the numerical damping exceeds alpha).
- Ratio errors in the data are referenced to the inviscid ratio and are 1e-5 to 1e-4 in magnitude, so the viscous shift (2.6e-4) is below what they resolve.
- Consequence for comparison: "same finite-viscosity problem" cannot be judged from solids4foam's finite-mesh numbers. Each code must be compared with the continuum reference (inviscid for the frequency ratio at the 0.1 % tolerance; the viscous eigenvalue for damping and the small frequency shift) and with its own refinement behaviour. Disagreement between two under-resolved discrete solutions is not evidence of a defect in either.

## 4. Reference classes used
| Quantity | Reference | Class |
|---|---|---|
| ratio, omega | exact inviscid linear (JSON) | exact analytical, linear |
| damping, viscous shift | script eigenvalue with Bessel thin-layer expansions | exact analytical (asymptotic in delta/gap) |
| solids4foam values | PR #13 CSVs | published approximate / under-resolved |
| FEBio energy balance | stored fields (this work) | diagnostic, reconstructed |
