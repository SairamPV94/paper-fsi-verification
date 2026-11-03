# Final physical-equivalence matrix, ringAddedMass FEBio no-slip production runs (updated 2026-11-01)

Superseded rows 7, 14, 17, 20 and the reading of the earlier matrix (`PHYSICAL_EQUIVALENCE_MATRIX.md`) after the overnight-2 production runs.


Sources: tutorial case files (`0/fluid/U`, `0/fluid/p`, `0/solid/D`, `constant/*`, `system/*`, `setInitialVelocity.py`), reference JSON and script, `tools/make_ring_feb.py`, FEBio source audit (`SOURCE_DEFECT_AUDIT.md`), `runs/ring_noslip_graded/GATE0_EQUIVALENCE.md`. "Identical" means the same continuum condition; discretisation is allowed to differ.

| # | Item | solids4foam | FEBio | Physically identical? | Only numerics differ? | Approximation? | FEBio can implement exactly? | Source change? |
|---|---|---|---|---|---|---|---|---|
| 1 | Fluid domain | annulus 1.05 to 1.5 m, quarter, 0.1 m slab (1 cell), plane strain | same | yes | yes (chordal faceting, -0.018 % volume) | no | yes | no |
| 2 | Solid geometry | ring 0.95 to 1.05 m, 4 radial cells, same slab | same | yes | yes | no | yes | no |
| 3 | Solid constitutive law | `linearElastic`, E 1e6, nu 0.3, planeStress no | `isotropic elastic`, E 1e6, nu 0.3, plane strain via u_z = 0 | parameters identical; law is the finite-strain form versus linear | no | yes, O(strain); strain amplitude order 1e-3 | not exactly (no small-strain solver option verified) | not needed if the residual is bounded |
| 4 | Solid density | 1000 | 1000 | yes | n/a | no | yes | no |
| 5 | Fluid density | 140 (moderate) | 140 | yes | n/a | no | yes | no |
| 6 | Viscosity | nu = 1e-7 m^2/s | mu = rho nu = 1.4e-5 Pa s | yes | n/a | no | yes | no |
| 7 | Fluid compressibility | incompressible | K = 1e8 Pa, p = -K e | **no (model form)** | no | yes: quantified at the resolved level (moderate, fluid at rest): K 1e7 / 1e9 change the ratio error by -0.0011 / +0.0063 pp and the decay by <= 0.4 %; the incompressible limit is bracketed to K = 1e9, not reached | only as K to infinity (fluid-FSI has no incompressible option in v4.13) | no |
| 8 | Solid kinematics | small strain, total displacement | finite-strain | see 3 | no | yes, see 3 | no | no |
| 9 | Outer-wall velocity | `fixedValue` U = 0, weak (viscous flux) | nodal w = 0 with u fixed (strong); v_f = v_s = 0 | yes (source-verified: v_f = v_s + w) | yes | no | yes | no |
| 10 | Moving interface | `newMovingWallVelocity` (v_f = wall velocity) | w = 0 on the shared nodes, v_f = v_s in all components (source-verified) | yes | yes | no | yes | no |
| 11 | Supports, symmetry, constraints | symmetry planes in fluid and solid, inside traction-free, empty front/back | mesh normal displacement fixed, w normal fixed on the planes, u_z = 0, inside free | yes | yes | no | yes | no |
| 12 | Initial displacement | zero | zero | yes | n/a | no | yes | no |
| 13 | Initial solid velocity | n = 2 mode, V0 = 1.5e-3, imposed by old-time displacements (second-order start) | same field, direct nodal velocity | yes | yes | start-up consistency at O(dt^2) | yes | no |
| 14 | **Initial fluid velocity** | at rest | **at rest in the final production runs (`--ic impulsive`, weak, moderate, strong)**; the compatible potential-flow start is a separately labelled diagnostic | **yes in the production runs** | no | the start is impulsive: a weakly compressible acoustic transient follows, and the response amplitude after the first step is about 1/(1+m*) of V0/omega (0.89, 0.49, 0.088 of V0/omega) | yes | no |
| 15 | External forcing | none; g = 0 | none | yes | n/a | no | yes | no |
| 16 | Fluid-solid traction | Dirichlet-Neumann or monolithic coupling with face pressure and viscous traction | `fluid-FSI traction`: nodal-e pressure on the surface, element-mean viscous stress; the w-row reaction at fixed-w interface nodes is not sent to the ring (source audit, item 3) | continuum yes; discrete consistency of action and reaction is a hypothesis for the no-slip energy gain | partly | O(h) interface term (algebraic, unproven consequence) | the stock implementation is what it is | a fix would need a source change (not authorised before a reproducer) |
| 17 | Mesh motion / ALE | diffusion-based cell motion | massless neo-Hookean mixture solid, E_mesh = 1e-3 Pa | the regulariser is a numerical device; tenfold E_mesh changes the moderate ratio by +0.0015 pp | yes | yes, bounded | not removable (E_mesh to 0 is singular) | no |
| 18 | Pressure boundary conditions | zeroGradient at walls, gauge fixed at a point | none; level set by compressibility | yes for incompressible flow up to the gauge | yes | the n = 0 mode is K-amplified in FEBio | n/a | no |
| 19 | Symmetry planes | `symmetry` patches | see 11 | yes | yes | no | yes | no |
| 20 | Angular mode and amplitude | n = 2, V0 = 1.5e-3 m/s, linear theory | same n = 2 and V0; finite amplitude | reference linear; halving the amplitude (moderate, potential-flow start) changes the ratio by -0.0068 pp | no | yes, bounded | no (finite-strain solver) | no |

## Reading
- **Identical continuum model:** items 1, 2, 4, 5, 6, 9, 10, 11, 12, 13, 15, 19.
- **Model-form differences that cannot be removed in stock v4.13:** fluid compressibility (7), solid kinematics (3, 8, 20), mesh regulariser (17). Their size is now bounded in the moderate regime of the resolved no-slip family (K 1e7-1e9, E_mesh x10, amplitude x0.5).
- **Initial fluid velocity (14):** matched in the final production runs (fluid at rest).
- **Hypothesised discretisation inconsistency:** traction transfer at fixed-w interface nodes (16).
- Exact continuum equivalence is not claimed: the final production runs match items 1, 2, 4-6, 9-15, 19 (including the fluid-at-rest start), and the remaining differences (compressibility, finite-strain solid, regulariser, finite amplitude, discretisation of the no-slip condition) are quantified at the 0.01-percentage-point level in the moderate regime. Label: qualified independent comparison.
