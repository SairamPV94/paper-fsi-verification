# Final scientific decision: ringAddedMass, FEBio v4.13 versus solids4foam, no-slip

Window: 2026-11-01 02:43Z to the writing time (about 2.5 h of the 8 h allowed). No source change, no plugin, no compilation, no PR push, no manuscript edit. All FEBio runs used the pristine binary (sha256 f5ae1ed6f347f875c392f93d847f2369f437345a9b785296d46b0bd6fbb72f02, verified in the 18 run records).

## Classifications (separate claims)
| Claim | Class | Basis |
|---|---|---|
| FEBio reproduces the finite-viscosity, no-slip linear ring problem when the near-wall layers are resolved | **B. QUALIFIED INDEPENDENT COMPARISON** | ratio error against the exact viscous reference +0.0014 to +0.0026 % (ring/tangential factors 1, 2, 4), against the inviscid reference -0.0249 to -0.0237 %; fitted damping 1.012 to 1.034 times the verified alpha_V; also with the tutorial's fluid-at-rest start (K1); sensitivities to dt, K, regulariser, amplitude all at most 0.026 % in omega and at most 0.007 pp in the ratio (paired) |
| The original uniform-mesh no-slip failures (-6.16 %, -2.7 %), the negative damping and the energy creation (Gamma 1.4e-2) of the unresolved graded case | **D. NUMERICAL LIMITATION**, root cause isolated to near-wall radial resolution of the strongly imposed no-slip conditions | controlled ladder (4 delta to delta/16), isolation runs E1/E2/E3/E4/F3, energy accounting validated to 1e-5 on the free-slip controls. The discrete mechanism by which under-resolved double no-slip creates energy is not established |
| A software defect in FEBio v4.13's no-slip, traction or time integration | **not demonstrated (not C)** | source audit found none; the single structural suspect (fixed-w interface reaction not passed to the ring) is an O(h) term whose consequence was not shown; no patch was justified |
| Strict like-for-like equivalence with the solids4foam tutorial | **not claimed (not A)** | FEBio: weak compressibility (K 1e7 vs 1e8 bounded at 0.0025 pp, incompressible limit untested), finite-strain solid (bounded only indirectly), mass-regulariser (bounded at about 0.0002 pp), a compatible initial field in the main runs (tutorial start tested in K1 only); solids4foam: Stokes layer unresolved at every tested mesh factor and measured decay (1.2e-4 s^-1 at n100) dominated by time-integration damping |
| Discrete agreement between the two codes | **E. NOT ESTABLISHED** | the two finite-mesh data sets approximate different limits (solids4foam's unresolved no-slip behaves as the inviscid reference, ratio errors -0.016 to +0.069 % against A; resolved FEBio reproduces the viscous shift -0.026 % against A); both agree with their continuum references within about 0.03 pp in the ratio, which is consistent but is not a test of equal discretisations |

## What FEBio can currently reproduce
The wet/dry frequency ratio of the moderate regime to better than 0.003 % against the finite-viscosity linear reference and 0.025 % against the inviscid one, with the correct sign and size of the viscous shift, and the viscous damping rate within 1.2 to 3.4 %, using stock v4.13 with a boundary-layer-graded fluid mesh (first cell at most delta/4, growth about 1.3), two-sided grading, K 1e7 to 1e8. Absolute frequency converges at difference-based order 1.98 in ring/tangential refinement (three levels, consistency check). Free-slip results of PR #26 are unchanged.

## What it cannot (yet) reproduce, or what is untested
Uniform meshes (and 4 delta first cells) with no-slip: ratio error -6.16 % (12 cells), -0.15 % (4 delta), negative damping, energy creation. Not tested: weak and strong regimes with graded no-slip (moderate only), interface shear traction (not logged), iterative-tolerance sensitivity at the resolved level, K 1e9 at the resolved level (failed on the G1 mesh), small-strain solid, exact incompressibility.

## Why (established versus hypothesised)
Established: resolution of the Stokes layer is required for the no-slip FEBio solution to approach the finite-viscosity solution; the failure is not a time-step, tangential-resolution or initial-field effect, and not wall-only or interface-only. Hypothesised: the precise discrete energy-creation mechanism (possibly the strongly constrained enclosed fluid interacting with the weak-form action-reaction mismatch at fixed-w nodes), untested.

## Fixed
Nothing in FEBio. In the project: the generator gained `--fluid-grading two-sided --h1 --nrf` (input generation only); regenerated baseline inputs are byte-identical.

## Is a like-for-like manuscript comparison justified now?
As a **qualified** entry, yes: "FEBio no-slip with a boundary-layer-graded fluid mesh reproduces the finite-viscosity eigenvalue (ratio) to 0.003 % and the damping to within 3 %, with the stated model-form differences". Not as "strict like-for-like": the solids4foam tutorial results are themselves not boundary-layer resolved and cannot discriminate the 0.026 % viscous shift or the viscous damping. The uniform-mesh no-slip result should be reported as a numerical limitation of unresolved layers in FEBio, not as an error of the benchmark.

## Smallest remaining checks before manuscript inclusion
1. Moderate regime only so far: run the weak and strong regimes at the F2 grading (the strong regime has the largest layer, delta 5.1e-4 m; the weak the smallest).
2. Log the interface traction (viscous stress) for one resolved case to compare shear with the Stokes-layer value (Figure 4).
3. One tolerance-sensitivity run at the resolved level (without the K 1e9 first-step convergence floor).
4. State the solids4foam comparison honestly: its tutorial-mesh results are consistent with the inviscid reference; a boundary-layer-resolved solids4foam run would be needed to compare viscous quantities.
5. Optional: reproducer for the interface action-reaction term (not required by the present evidence).

## Resources
11.4 CPU-h allocated in this campaign of the 240 CPU-h limit (all jobs: 18 FEBio runs including one failed (E6) and analysis jobs; see `SIMULATION_AND_RESOURCE_LEDGER.csv`), at most 6 cores concurrent, wall time about 2.5 h of 8 h. The earlier approved pilot (G0, G1: 0.716 CPU-h) is not included. Unrelated account jobs are not charged here.
