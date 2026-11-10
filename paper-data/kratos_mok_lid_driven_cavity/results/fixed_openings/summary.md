# Kratos 10.3.0 cavity refinement, statistics over t = 20-70 s

Openings fixed in space at 0.875 <= y <= 1 (group-B definition).

## All runs

| run | fluid | solid | dt (s) | coupling tol | peak (m) | trough (m) | mean (m) | phase (s) | solves mean/max | steps over tol | max residual (m) | wall (min) | threads |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| n016_dt0.0125_sy2_fixopen | 16² fixed openings | 16x2 | 0.0125 | 1e-06 | 0.28458 | 0.21465 | 0.25052 | 4.365 | 2.01/4 | 0 | 1.0e-06 | 3.7 | 1 |
| n016_dt0.2_sy2_fixopen | 16² fixed openings | 16x2 | 0.2 | 1e-06 | 0.28752 | 0.20523 | 0.24583 | 4.400 | 3.28/4 | 0 | 1.0e-06 | 0.4 | 1 |
| n032_dt0.0125_sy2_fixopen | 32² fixed openings | 32x2 | 0.0125 | 1e-06 | 0.28591 | 0.20858 | 0.24674 | 4.440 | 2.02/4 | 0 | 1.0e-06 | 14.0 | 1 |
| n032_dt0.1_sy2_fixopen | 32² fixed openings | 32x2 | 0.1 | 1e-06 | 0.28820 | 0.20779 | 0.24733 | 4.400 | 2.62/4 | 0 | 1.0e-06 | 1.2 | 8 |
| n032_dt0.1_sy2_outletuy0_fixopen | 32² outlet u_y=0 fixed openings | 32x2 | 0.1 | 1e-06 | 0.28826 | 0.20939 | 0.24812 | 4.410 | 2.60/4 | 0 | 1.0e-06 | 2.1 | 1 |
| n064_dt0.0125_sy2_fixopen | 64² fixed openings | 64x2 | 0.0125 | 1e-06 | 0.28453 | 0.20634 | 0.24472 | 4.486 | 2.03/4 | 0 | 1.0e-06 | 54.5 | 1 |
| n064_dt0.0125_sy2_fixopen_dtau0 | 64² fixed openings dynamic_tau 0 | 64x2 | 0.0125 | 1e-06 | 0.28516 | 0.20622 | 0.24496 | 4.479 | 2.03/4 | 0 | 1.0e-06 | 44.8 | 1 |
| n064_dt0.025_sy2_fixopen | 64² fixed openings | 64x2 | 0.025 | 1e-06 | 0.28483 | 0.20630 | 0.24484 | 4.478 | 2.05/4 | 0 | 1.0e-06 | 27.8 | 1 |
| n064_dt0.025_sy2_fixopen_dtau0 | 64² fixed openings dynamic_tau 0 | 64x2 | 0.025 | 1e-06 | 0.28516 | 0.20623 | 0.24497 | 4.478 | 2.03/3 | 0 | 1.0e-06 | 22.9 | 1 |
| n064_dt0.025_sy2_outletuy0_fixopen | 64² outlet u_y=0 fixed openings | 64x2 | 0.025 | 1e-06 | 0.28631 | 0.20970 | 0.24731 | 4.475 | 2.04/3 | 0 | 1.0e-06 | 25.8 | 1 |
| n064_dt0.025_sy4_fixopen | 64² fixed openings | 64x4 | 0.025 | 1e-06 | 0.28483 | 0.20630 | 0.24484 | 4.478 | 2.05/4 | 0 | 1.0e-06 | 27.9 | 1 |
| n064_dt0.025_sy8_fixopen | 64² fixed openings | 64x8 | 0.025 | 1e-06 | 0.28483 | 0.20630 | 0.24484 | 4.478 | 2.05/4 | 0 | 1.0e-06 | 29.4 | 1 |
| n064_dt0.05_sy2_fixopen | 64² fixed openings | 64x2 | 0.05 | 1e-06 | 0.28500 | 0.20633 | 0.24492 | 4.500 | 2.12/3 | 0 | 1.0e-06 | 14.6 | 1 |
| n064_dt0.05_sy2_fixopen_dtau0 | 64² fixed openings dynamic_tau 0 | 64x2 | 0.05 | 1e-06 | 0.28517 | 0.20629 | 0.24499 | 4.500 | 2.15/3 | 0 | 1.0e-06 | 13.1 | 1 |
| n064_dt0.1_sy2_fixopen | 64² fixed openings | 64x2 | 0.1 | 1e-06 | 0.28515 | 0.20660 | 0.24506 | 4.500 | 2.58/4 | 0 | 9.9e-07 | 10.1 | 1 |
| n064_dt0.1_sy2_fixopen_dtau0 | 64² fixed openings dynamic_tau 0 | 64x2 | 0.1 | 1e-06 | 0.28524 | 0.20659 | 0.24509 | 4.500 | 2.57/4 | 0 | 1.0e-06 | 8.9 | 1 |
| n096_dt0.025_sy2_fixopen | 96² fixed openings | 96x2 | 0.025 | 1e-06 | 0.28393 | 0.20588 | 0.24420 | 4.500 | 2.05/4 | 0 | 1.0e-06 | 45.5 | 2 |
| n128_dt0.0125_sy2_fixopen | 128² fixed openings | 128x2 | 0.0125 | 1e-06 | 0.28348 | 0.20574 | 0.24392 | 4.501 | 2.03/4 | 0 | 1.0e-06 | 102.9 | 4 |
| n128_dt0.0125_sy2_tight1e-8_fixopen | 128² fixed openings | 128x2 | 0.0125 | 1e-08 tight | 0.28348 | 0.20574 | 0.24392 | 4.501 | 2.05/3 | 0 | 1.0e-08 | 117.5 | 4 |

## Studies

Changes are relative to the finest member of each study. Orders use the three members shown. 'below noise' means both changes are under 1e-5 m.

### Time step, 64² fluid, 2 solid elements through the thickness

| member | peak (m) | trough (m) | mean (m) | phase (s) | change in peak | change in trough | change in mean |
|---|---|---|---|---|---|---|---|
| dt 0.1 | 0.28515 | 0.20660 | 0.24506 | 4.500 |  |  |  |
| dt 0.05 | 0.28500 | 0.20633 | 0.24492 | 4.500 | -0.06% | -0.13% | -0.06% |
| dt 0.025 | 0.28483 | 0.20630 | 0.24484 | 4.478 | -0.06% | -0.01% | -0.04% |
| dt 0.0125 | 0.28453 | 0.20634 | 0.24472 | 4.486 | -0.10% | +0.02% | -0.05% |

| triple (dt) | QoI | observed order | extrapolated (m) | finest - extrapolated | GCI fine |
|---|---|---|---|---|---|
| dt 0.05, dt 0.025, dt 0.0125 | peak | 0.80 | 0.28414 | +0.14% | 0.17% |
| dt 0.05, dt 0.025, dt 0.0125 | trough | oscillatory | | | |
| dt 0.05, dt 0.025, dt 0.0125 | mean | 0.47 | 0.24440 | +0.13% | 0.16% |
| dt 0.1, dt 0.05, dt 0.025 | peak | 0.10 | 0.28248 | +0.83% | 1.03% |
| dt 0.1, dt 0.05, dt 0.025 | trough | 3.29 | 0.20630 | +0.00% | 0.00% |
| dt 0.1, dt 0.05, dt 0.025 | mean | 0.65 | 0.24468 | +0.06% | 0.08% |

### Time step, 64², dynamic_tau = 0 (stabilisation independent of dt)

| member | peak (m) | trough (m) | mean (m) | phase (s) | change in peak | change in trough | change in mean |
|---|---|---|---|---|---|---|---|
| dt 0.1 | 0.28524 | 0.20659 | 0.24509 | 4.500 |  |  |  |
| dt 0.05 | 0.28517 | 0.20629 | 0.24499 | 4.500 | -0.03% | -0.14% | -0.04% |
| dt 0.025 | 0.28516 | 0.20623 | 0.24497 | 4.478 | -0.00% | -0.03% | -0.01% |
| dt 0.0125 | 0.28516 | 0.20622 | 0.24496 | 4.479 | -0.00% | -0.01% | -0.00% |

| triple (dt) | QoI | observed order | extrapolated (m) | finest - extrapolated | GCI fine |
|---|---|---|---|---|---|
| dt 0.05, dt 0.025, dt 0.0125 | peak | below noise | | | |
| dt 0.05, dt 0.025, dt 0.0125 | trough | 2.02 | 0.20621 | +0.00% | 0.00% |
| dt 0.05, dt 0.025, dt 0.0125 | mean | 2.28 | 0.24496 | +0.00% | 0.00% |
| dt 0.1, dt 0.05, dt 0.025 | peak | 3.26 | 0.28516 | +0.00% | 0.00% |
| dt 0.1, dt 0.05, dt 0.025 | trough | 2.31 | 0.20622 | +0.01% | 0.01% |
| dt 0.1, dt 0.05, dt 0.025 | mean | 2.05 | 0.24496 | +0.00% | 0.00% |

### Fluid mesh, dt 0.0125 s, solid refined along the membrane with the fluid

| member | peak (m) | trough (m) | mean (m) | phase (s) | change in peak | change in trough | change in mean |
|---|---|---|---|---|---|---|---|
| 16² | 0.28458 | 0.21465 | 0.25052 | 4.365 |  |  |  |
| 32² | 0.28591 | 0.20858 | 0.24674 | 4.440 | +0.47% | -2.95% | -1.55% |
| 64² | 0.28453 | 0.20634 | 0.24472 | 4.486 | -0.49% | -1.09% | -0.83% |
| 128² | 0.28348 | 0.20574 | 0.24392 | 4.501 | -0.37% | -0.29% | -0.33% |

| triple (h) | QoI | observed order | extrapolated (m) | finest - extrapolated | GCI fine |
|---|---|---|---|---|---|
| 32², 64², 128² | peak | 0.39 | 0.28004 | +1.23% | 1.52% |
| 32², 64², 128² | trough | 1.91 | 0.20553 | +0.10% | 0.13% |
| 32², 64², 128² | mean | 1.35 | 0.24341 | +0.21% | 0.26% |
| 16², 32², 64² | peak | oscillatory | | | |
| 16², 32², 64² | trough | 1.44 | 0.20502 | +0.64% | 0.80% |
| 16², 32², 64² | mean | 0.90 | 0.24239 | +0.96% | 1.19% |

### Solid through the thickness, 64², dt 0.025 s

| member | peak (m) | trough (m) | mean (m) | phase (s) | change in peak | change in trough | change in mean |
|---|---|---|---|---|---|---|---|
| 2 elements | 0.28483 | 0.20630 | 0.24484 | 4.478 |  |  |  |
| 4 elements | 0.28483 | 0.20630 | 0.24484 | 4.478 | -0.00% | +0.00% | +0.00% |
| 8 elements | 0.28483 | 0.20630 | 0.24484 | 4.478 | +0.00% | +0.00% | -0.00% |

| triple (h_solid) | QoI | observed order | extrapolated (m) | finest - extrapolated | GCI fine |
|---|---|---|---|---|---|
| 2 elements, 4 elements, 8 elements | peak | below noise | | | |
| 2 elements, 4 elements, 8 elements | trough | below noise | | | |
| 2 elements, 4 elements, 8 elements | mean | below noise | | | |

### Combined refinement, same sequence as solids4foam

| member | peak (m) | trough (m) | mean (m) | phase (s) | change in peak | change in trough | change in mean |
|---|---|---|---|---|---|---|---|
| 16²/0.2 | 0.28752 | 0.20523 | 0.24583 | 4.400 |  |  |  |
| 32²/0.1 | 0.28820 | 0.20779 | 0.24733 | 4.400 | +0.24% | +1.24% | +0.61% |
| 64²/0.05 | 0.28500 | 0.20633 | 0.24492 | 4.500 | -1.13% | -0.71% | -0.98% |
| 96²/0.025 | 0.28393 | 0.20588 | 0.24420 | 4.500 | -0.38% | -0.22% | -0.30% |

| triple (h) | QoI | observed order | extrapolated (m) | finest - extrapolated | GCI fine |
|---|---|---|---|---|---|
| 32²/0.1, 64²/0.05, 96²/0.025 | peak | 1.00 | 0.28180 | +0.76% | 0.94% |
| 32²/0.1, 64²/0.05, 96²/0.025 | trough | 1.16 | 0.20515 | +0.36% | 0.45% |
| 32²/0.1, 64²/0.05, 96²/0.025 | mean | 1.17 | 0.24300 | +0.49% | 0.61% |
| 16²/0.2, 32²/0.1, 64²/0.05 | peak | oscillatory | | | |
| 16²/0.2, 32²/0.1, 64²/0.05 | trough | oscillatory | | | |
| 16²/0.2, 32²/0.1, 64²/0.05 | mean | oscillatory | | | |

### Coupling tolerance, 128², dt 0.0125 s

| setting | peak (m) | trough (m) | mean (m) | solves mean/max | max residual (m) |
|---|---|---|---|---|---|
| nl_tol 1e-6, default solver tolerances | 0.283480 | 0.205742 | 0.243922 | 2.03/4 | 1.0e-06 |
| nl_tol 1e-8, all tolerances 100x tighter | 0.283479 | 0.205743 | 0.243921 | 2.05/3 | 1.0e-08 |
| difference | +0.00% | -0.00% | +0.00% | | max history difference 4.9e-06 m |

### Outlet sensitivity, u_y = 0 imposed on the outlet

| level | peak change | trough change | mean change | max history difference (m) |
|---|---|---|---|---|
| 32²/0.1 | +0.02% | +0.77% | +0.32% | 1.7e-03 |
| 64²/0.025 | +0.52% | +1.65% | +1.01% | 3.5e-03 |

## Kratos against solids4foam at the same nominal levels

solids4foam values are recomputed from the paper-data histories with the same function. Difference = (Kratos - solids4foam) / solids4foam.

| level | code | peak (m) | trough (m) | mean (m) | phase (s) | max history difference (m) |
|---|---|---|---|---|---|---|
| 16²/0.2 | solids4foam (legacy0-mesh16.csv) | 0.29342 | 0.19421 | 0.24257 | 4.600 | |
| | Kratos | 0.28752 | 0.20523 | 0.24583 | 4.400 | 0.0125 |
| | difference | -2.01% | +5.67% | +1.34% | -0.200 | |
| 32²/0.1 | solids4foam (legacy-mesh32.csv) | 0.28893 | 0.19864 | 0.24268 | 4.500 | |
| | Kratos | 0.28820 | 0.20779 | 0.24733 | 4.400 | 0.0096 |
| | difference | -0.25% | +4.61% | +1.91% | -0.100 | |
| 64²/0.05 | solids4foam (legacy-mesh64.csv) | 0.28701 | 0.20223 | 0.24376 | 4.500 | |
| | Kratos | 0.28500 | 0.20633 | 0.24492 | 4.500 | 0.0044 |
| | difference | -0.70% | +2.03% | +0.48% | +0.000 | |
| 96²/0.025 | solids4foam (legacy-mesh96.csv) | 0.28612 | 0.20443 | 0.24451 | 4.478 | |
| | Kratos | 0.28393 | 0.20588 | 0.24420 | 4.500 | 0.0024 |
| | difference | -0.77% | +0.71% | -0.13% | +0.022 | |
| 64²/0.025 | solids4foam (strict-dt0.025.csv) | 0.28697 | 0.20203 | 0.24366 | 4.500 | |
| | Kratos | 0.28483 | 0.20630 | 0.24484 | 4.478 | 0.0045 |
| | difference | -0.75% | +2.11% | +0.48% | -0.022 | |
