# Physical-equivalence matrix: solids4foam ringAddedMass tutorial versus FEBio v4.13 models

Sources: tutorial case files (`0/fluid/U`, `0/fluid/p`, `0/solid/D`, `constant/*`, `system/*`, `setInitialVelocity.py`), reference JSON and script, `tools/make_ring_feb.py`, FEBio source audit (`SOURCE_DEFECT_AUDIT.md`), `runs/ring_noslip_graded/GATE0_EQUIVALENCE.md`. "Identical" means the same continuum condition; discretisation is allowed to differ.

| # | Item | solids4foam | FEBio | Physically identical? | Only numerics differ? | Approximation? | FEBio can implement exactly? | Source change? |
|---|---|---|---|---|---|---|---|---|
| 1 | Fluid domain | annulus 1.05 to 1.5 m, quarter, 0.1 m slab (1 cell), plane strain | same | yes | yes (chordal faceting, -0.018 % volume) | no | yes | no |
| 2 | Solid geometry | ring 0.95 to 1.05 m, 4 radial cells, same slab | same | yes | yes | no | yes | no |
| 3 | Solid constitutive law | `linearElastic`, E 1e6, nu 0.3, planeStress no | `isotropic elastic`, E 1e6, nu 0.3, plane strain via u_z = 0 | parameters identical; law is the finite-strain form versus linear | no | yes, O(strain); strain amplitude order 1e-3 | not exactly (no small-strain solver option verified) | not needed if the residual is bounded |
| 4 | Solid density | 1000 | 1000 | yes | n/a | no | yes | no |
| 5 | Fluid density | 140 (moderate) | 140 | yes | n/a | no | yes | no |
| 6 | Viscosity | nu = 1e-7 m^2/s | mu = rho nu = 1.4e-5 Pa s | yes | n/a | no | yes | no |
| 7 | Fluid compressibility | incompressible | K = 1e8 Pa, p = -K e | **no (model form)** | no | yes: acoustic and volume-mismatch terms; shift 1.4e-6 in the free-slip ratio between K 1e8 and 1e9 (strong M2), i.e. negligible there; untested in the no-slip family (E5, E6) | only as K to infinity (fluid-FSI has no incompressible option in v4.13) | no |
| 8 | Solid kinematics | small strain, total displacement | finite-strain | see 3 | no | yes, see 3 | no | no |
| 9 | Outer-wall velocity | `fixedValue` U = 0, weak (viscous flux) | nodal w = 0 with u fixed (strong); v_f = v_s = 0 | yes (source-verified: v_f = v_s + w) | yes | no | yes | no |
| 10 | Moving interface | `newMovingWallVelocity` (v_f = wall velocity) | w = 0 on the shared nodes, v_f = v_s in all components (source-verified) | yes | yes | no | yes | no |
| 11 | Supports, symmetry, constraints | symmetry planes in fluid and solid, inside traction-free, empty front/back | mesh normal displacement fixed, w normal fixed on the planes, u_z = 0, inside free | yes | yes | no | yes | no |
| 12 | Initial displacement | zero | zero | yes | n/a | no | yes | no |
| 13 | Initial solid velocity | n = 2 mode, V0 = 1.5e-3, imposed by old-time displacements (second-order start) | same field, direct nodal velocity | yes | yes | start-up consistency at O(dt^2) | yes | no |
| 14 | **Initial fluid velocity** | at rest | compatible potential flow plus stationary correction (KE 1.33 times the potential-flow value) in all runs so far; at rest available as `--ic impulsive` (not yet run before E3) | **no in G-runs; yes in E3** | no | n/a | yes (E3) | no |
| 15 | External forcing | none; g = 0 | none | yes | n/a | no | yes | no |
| 16 | Fluid-solid traction | Dirichlet-Neumann or monolithic coupling with face pressure and viscous traction | `fluid-FSI traction`: nodal-e pressure on the surface, element-mean viscous stress; the w-row reaction at fixed-w interface nodes is not sent to the ring (source audit, item 3) | continuum yes; discrete consistency of action and reaction is a hypothesis for the no-slip energy gain | partly | O(h) interface term (algebraic, unproven consequence) | the stock implementation is what it is | a fix would need a source change (not authorised before a reproducer) |
| 17 | Mesh motion / ALE | diffusion-based cell motion | massless neo-Hookean mixture solid, E_mesh = 1e-3 Pa; ALE through w | the regulariser is a numerical device; ratio effect 0.16 pp between E_mesh 1 and 1e-3 (free-slip), residual at 1e-3 unquantified | yes | yes | not removable (E_mesh to 0 is singular) | no |
| 18 | Pressure boundary conditions | zeroGradient at walls, gauge fixed at a point | none; level set by compressibility | yes for incompressible flow up to the gauge | yes | the n = 0 mode is K-amplified in FEBio | n/a | no |
| 19 | Symmetry planes | `symmetry` patches | see 11 | yes | yes | no | yes | no |
| 20 | Angular mode and amplitude | n = 2, V0 = 1.5e-3 m/s, linear theory (amplitude about 5e-4 a) | same initial field, finite amplitude | reference is linear; FEBio carries an O(amplitude^2) term (the free-slip ratio floor scaled as A^2, strong M2: 0.0399 % to 0.0097 % at half amplitude) | no | yes | no (finite-strain by construction) | no |

## Reading
- **Identical continuum model:** items 1, 2, 4, 5, 6, 9, 10, 11, 12, 13, 15, 19.
- **Model-form differences that cannot be removed in stock v4.13:** fluid compressibility (7), solid kinematics (3, 8, 20), mesh regulariser (17). Their size is bounded only where measured (free-slip family); they are untested in the no-slip family except through E5, E6.
- **Removable difference:** the initial fluid velocity (14), tested in E3.
- **Hypothesised discretisation inconsistency:** traction transfer at fixed-w interface nodes (16).
- Exact continuum equivalence is therefore not claimed for any FEBio run; the best achievable label is "qualified" with the residual model-form terms stated.
