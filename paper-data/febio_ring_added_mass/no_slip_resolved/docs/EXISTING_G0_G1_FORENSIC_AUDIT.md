# Forensic audit of the existing G0 and G1 data (post-processing only; the G1 gate failure is preserved)

Scripts: `scripts/forensic_energy.py`; outputs `forensic/*.json`, `forensic/*.npz` (G0, G1, D4, C2, E1 to E5, F1 to F3). Energy accounting uses the consistent mass matrix and 8-point integration (first version with lumped mass kept in `forensic/lumped_v1/`; the lumped KE differs from the consistent value by 0.4 to 1.5 % at t = 0 and the conclusions below do not depend on the choice). Accounting check: on the free-slip runs (C2, G0) the creation measure Gamma = (E_tot + W)/E_0 - 1 is 1.3e-5 and 6.7e-6, so the bookkeeping is valid at the 1e-5 level.

## 1. Is the negative damping genuine?
Yes, in the stored fields of G1. The fitted decay is negative in every fit window (alpha, 1e-4 s^-1: 0-3T -2.23, 0-2T -2.35, T-3T -2.05; envelope of successive peaks -2.42), against a physical +4.75. It is not a fit-window artefact. Independently, E_tot(t)/E_0 rises monotonically from 1.0000 to 1.0057 while the integrated viscous dissipation W (8.4e-3 E_0, equal to the sum of the dissipation in the wall-only and interface-only runs E1 and E2 and about 65 % of the physical 1.3e-2) accrues, so Gamma = +1.41e-2: the system gains mechanical energy beyond what it dissipates. Mesh-regulariser energy is bounded by 1.2e-6 (bound from the largest nodal displacement and E_mesh 1e-3), the compressive energy sum V p^2/(2K) by 3.6e-6 E_0, so neither can account for a 1.4 % gain. A closed, unforced system cannot gain energy, so this is numerical.

## 2. Pressure
- The failed N1 metric (0.278) measures the residual of the first-layer pressure after removing the harmonics: the low-frequency n = 0 content (rms 0.090 Pa; no content above 20 rad/s; n = 2 residual 0.012 Pa, 3.6 % of signal).
- That n = 0 pressure is uniform across all radial layers (rms 0.099 Pa and mean offset -0.288 Pa in every layer) and equals -K times the mean volume ratio (correlation 0.99999999 between the fluid-mean pressure and -K mean(J-1)); the geometric change of the area enclosed by the interface nodes tracks the same quantity (5.4e-10 at omega against 5.3e-10 in mean(J-1)). So it is the compressibility response, amplified by K = 1e8, to a fluid-volume mismatch of about 5e-10 relative: a global mean (gauge-like) mode, not grid-scale checkerboarding.
- Its energy is negligible. It is therefore a poor proxy for energy injection, but it correlates with the no-slip case because with both boundaries strongly constrained no weak leakage can relieve the tiny volume mismatch. This is a diagnosis of what the metric detects; the original N1 threshold and the G1 failure are unchanged.
- At omega the free-slip G0 has n = 0 amplitude 8.5e-7 Pa; the 2 omega component (0.025 Pa) is the physical second-order effect in all runs.

## 3. Separation of effects (Phase 1 list)
| Item | Finding |
|---|---|
| Genuine physical oscillation | n = 2 pressure 0.33 Pa at omega, phase 178.1 deg, as in the slip runs |
| Nonphysical pressure modes | no checkerboard content (no residual above 20 rad/s) |
| Gauge / mean drift | the n = 0 mode above; harmless in energy |
| Initialization transient | the compatible IC is non-modal; E_tot steps from 0.9978 to 1.0000 over the first step in G1, afterwards a steady rise; with fluid at rest (E3) the decay is still negative |
| Fit artefact | excluded (all windows and the envelope agree in sign and size) |
| Time integration | excluded for this range: halving dt (E4) leaves Gamma (1.42e-2 versus 1.41e-2) and the decay (-2.24e-4) unchanged |
| Traction transfer | not found faulty in the source (SOURCE_DEFECT_AUDIT.md); the energy gain requires both boundaries no-slip (E1, E2 each conserve), so a fixed-w interface alone is not sufficient |
| Energy accounting | validated on the free-slip runs to 1e-5; the dissipation integral is one-sided (a one-point-per-gp gradient of nodal data) and overestimates in the resolved case F2 (W 1.58e-2 against a physical 1.3e-2), so Gamma has an uncertainty of order 1e-3 |

## 4. Root cause (established by the round-1 and round-2 runs; see NUMERICAL_RESULTS.md)
The energy creation and the negative damping are a near-wall radial-resolution artefact of the strongly imposed no-slip conditions: they require both boundaries to be no-slip, are independent of dt and tangential resolution, and disappear as the first cell is brought below the Stokes layer.
