# Kratos 10.3.0 cavity refinement, statistics over t = 20-70 s

Shipped Kratos mesh: the opening nodes slide along the side walls with the mesh.

## All runs

| run | fluid | solid | dt (s) | coupling tol | peak (m) | trough (m) | mean (m) | phase (s) | solves mean/max | steps over tol | max residual (m) | wall (min) | threads |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| n016_dt0.0125_sy2 | 16² | 16x2 | 0.0125 | 1e-06 | 0.24933 | 0.19933 | 0.22418 | 4.578 | 1.98/4 | 0 | 1.0e-06 | 3.5 | 1 |
| n016_dt0.2_sy2 | 16² | 16x2 | 0.2 | 1e-06 | 0.26160 | 0.19716 | 0.22878 | 4.600 | 3.11/4 | 0 | 9.8e-07 | 0.4 | 1 |
| n032_dt0.0125_sy2 | 32² | 32x2 | 0.0125 | 1e-06 | 0.25683 | 0.20185 | 0.22836 | 4.606 | 2.02/4 | 0 | 1.0e-06 | 13.4 | 1 |
| n032_dt0.1_sy2 | 32² | 32x2 | 0.1 | 1e-06 | 0.26199 | 0.20319 | 0.23153 | 4.600 | 2.51/4 | 0 | 1.0e-06 | 1.2 | 8 |
| n032_dt0.1_sy2_outletuy0 | 32² outlet u_y=0 | 32x2 | 0.1 | 1e-06 | 0.26227 | 0.20420 | 0.23216 | 4.600 | 2.49/4 | 0 | 1.0e-06 | 2.0 | 1 |
| n064_dt0.0125_sy2 | 64² | 64x2 | 0.0125 | 1e-06 | 0.25704 | 0.20178 | 0.22840 | 4.633 | 2.01/4 | 0 | 1.0e-06 | 50.4 | 1 |
| n064_dt0.025_sy2 | 64² | 64x2 | 0.025 | 1e-06 | 0.25768 | 0.20203 | 0.22885 | 4.625 | 2.04/4 | 0 | 1.0e-06 | 26.4 | 1 |
| n064_dt0.025_sy2_outletuy0 | 64² outlet u_y=0 | 64x2 | 0.025 | 1e-06 | 0.25917 | 0.20481 | 0.23097 | 4.625 | 2.03/3 | 0 | 1.0e-06 | 23.0 | 1 |
| n064_dt0.025_sy4 | 64² | 64x4 | 0.025 | 1e-06 | 0.25768 | 0.20203 | 0.22885 | 4.625 | 2.02/3 | 0 | 1.0e-06 | 25.8 | 1 |
| n064_dt0.025_sy8 | 64² | 64x8 | 0.025 | 1e-06 | 0.25768 | 0.20203 | 0.22885 | 4.625 | 2.01/3 | 0 | 1.0e-06 | 26.7 | 1 |
| n064_dt0.05_sy2 | 64² | 64x2 | 0.05 | 1e-06 | 0.25810 | 0.20220 | 0.22914 | 4.635 | 2.08/3 | 0 | 1.0e-06 | 13.8 | 1 |
| n064_dt0.1_sy2 | 64² | 64x2 | 0.1 | 1e-06 | 0.25850 | 0.20235 | 0.22941 | 4.600 | 2.51/4 | 0 | 1.0e-06 | 9.3 | 1 |
| n096_dt0.025_sy2 | 96² | 96x2 | 0.025 | 1e-06 | 0.25700 | 0.20190 | 0.22843 | 4.645 | 2.03/3 | 0 | 1.0e-06 | 66.6 | 1 |
| n128_dt0.0125_sy2 | 128² | 128x2 | 0.0125 | 1e-06 | 0.25666 | 0.20191 | 0.22825 | 4.644 | 2.02/4 | 0 | 1.0e-06 | 89.2 | 4 |
| n128_dt0.0125_sy2_tight1e-8 | 128² | 128x2 | 0.0125 | 1e-08 tight | 0.25666 | 0.20191 | 0.22825 | 4.645 | 2.02/3 | 0 | 1.0e-08 | 106.5 | 4 |

## Studies

Changes are relative to the finest member of each study. Orders use the three members shown. 'below noise' means both changes are under 1e-5 m.

### Time step, 64² fluid, 2 solid elements through the thickness

| member | peak (m) | trough (m) | mean (m) | phase (s) | change in peak | change in trough | change in mean |
|---|---|---|---|---|---|---|---|
| dt 0.1 | 0.25850 | 0.20235 | 0.22941 | 4.600 |  |  |  |
| dt 0.05 | 0.25810 | 0.20220 | 0.22914 | 4.635 | -0.15% | -0.08% | -0.12% |
| dt 0.025 | 0.25768 | 0.20203 | 0.22885 | 4.625 | -0.17% | -0.08% | -0.13% |
| dt 0.0125 | 0.25704 | 0.20178 | 0.22840 | 4.633 | -0.25% | -0.12% | -0.19% |

| triple (dt) | QoI | observed order | extrapolated (m) | finest - extrapolated | GCI fine |
|---|---|---|---|---|---|
| dt 0.05, dt 0.025, dt 0.0125 | peak | 0.58 | 0.25576 | +0.50% | 0.62% |
| dt 0.05, dt 0.025, dt 0.0125 | trough | 0.60 | 0.20129 | +0.24% | 0.30% |
| dt 0.05, dt 0.025, dt 0.0125 | mean | 0.59 | 0.22752 | +0.39% | 0.48% |
| dt 0.1, dt 0.05, dt 0.025 | peak | 0.11 | 0.25213 | +2.20% | 2.69% |
| dt 0.1, dt 0.05, dt 0.025 | trough | 0.10 | 0.19978 | +1.13% | 1.39% |
| dt 0.1, dt 0.05, dt 0.025 | mean | 0.12 | 0.22542 | +1.52% | 1.87% |

### Fluid mesh, dt 0.0125 s, solid refined along the membrane with the fluid

| member | peak (m) | trough (m) | mean (m) | phase (s) | change in peak | change in trough | change in mean |
|---|---|---|---|---|---|---|---|
| 16² | 0.24933 | 0.19933 | 0.22418 | 4.578 |  |  |  |
| 32² | 0.25683 | 0.20185 | 0.22836 | 4.606 | +2.92% | +1.25% | +1.84% |
| 64² | 0.25704 | 0.20178 | 0.22840 | 4.633 | +0.08% | -0.03% | +0.02% |
| 128² | 0.25666 | 0.20191 | 0.22825 | 4.644 | -0.15% | +0.06% | -0.07% |

| triple (h) | QoI | observed order | extrapolated (m) | finest - extrapolated | GCI fine |
|---|---|---|---|---|---|
| 32², 64², 128² | peak | oscillatory | | | |
| 32², 64², 128² | trough | oscillatory | | | |
| 32², 64², 128² | mean | oscillatory | | | |
| 16², 32², 64² | peak | 5.16 | 0.25705 | -0.00% | 0.00% |
| 16², 32², 64² | trough | oscillatory | | | |
| 16², 32², 64² | mean | 6.78 | 0.22840 | -0.00% | 0.00% |

### Solid through the thickness, 64², dt 0.025 s

| member | peak (m) | trough (m) | mean (m) | phase (s) | change in peak | change in trough | change in mean |
|---|---|---|---|---|---|---|---|
| 2 elements | 0.25768 | 0.20203 | 0.22885 | 4.625 |  |  |  |
| 4 elements | 0.25768 | 0.20203 | 0.22885 | 4.625 | -0.00% | -0.00% | -0.00% |
| 8 elements | 0.25768 | 0.20203 | 0.22885 | 4.625 | -0.00% | -0.00% | -0.00% |

| triple (h_solid) | QoI | observed order | extrapolated (m) | finest - extrapolated | GCI fine |
|---|---|---|---|---|---|
| 2 elements, 4 elements, 8 elements | peak | below noise | | | |
| 2 elements, 4 elements, 8 elements | trough | below noise | | | |
| 2 elements, 4 elements, 8 elements | mean | below noise | | | |

### Combined refinement, same sequence as solids4foam

| member | peak (m) | trough (m) | mean (m) | phase (s) | change in peak | change in trough | change in mean |
|---|---|---|---|---|---|---|---|
| 16²/0.2 | 0.26160 | 0.19716 | 0.22878 | 4.600 |  |  |  |
| 32²/0.1 | 0.26199 | 0.20319 | 0.23153 | 4.600 | +0.15% | +2.98% | +1.20% |
| 64²/0.05 | 0.25810 | 0.20220 | 0.22914 | 4.635 | -1.51% | -0.49% | -1.04% |
| 96²/0.025 | 0.25700 | 0.20190 | 0.22843 | 4.645 | -0.43% | -0.14% | -0.31% |

| triple (h) | QoI | observed order | extrapolated (m) | finest - extrapolated | GCI fine |
|---|---|---|---|---|---|
| 32²/0.1, 64²/0.05, 96²/0.025 | peak | 1.28 | 0.25539 | +0.63% | 0.79% |
| 32²/0.1, 64²/0.05, 96²/0.025 | trough | 1.21 | 0.20144 | +0.23% | 0.29% |
| 32²/0.1, 64²/0.05, 96²/0.025 | mean | 1.19 | 0.22729 | +0.50% | 0.63% |
| 16²/0.2, 32²/0.1, 64²/0.05 | peak | oscillatory | | | |
| 16²/0.2, 32²/0.1, 64²/0.05 | trough | oscillatory | | | |
| 16²/0.2, 32²/0.1, 64²/0.05 | mean | oscillatory | | | |

### Coupling tolerance, 128², dt 0.0125 s

| setting | peak (m) | trough (m) | mean (m) | solves mean/max | max residual (m) |
|---|---|---|---|---|---|
| nl_tol 1e-6, default solver tolerances | 0.256665 | 0.201910 | 0.228254 | 2.02/4 | 1.0e-06 |
| nl_tol 1e-8, all tolerances 100x tighter | 0.256663 | 0.201910 | 0.228253 | 2.02/3 | 1.0e-08 |
| difference | +0.00% | -0.00% | +0.00% | | max history difference 4.0e-06 m |

### Outlet sensitivity, u_y = 0 imposed on the outlet

| level | peak change | trough change | mean change | max history difference (m) |
|---|---|---|---|---|
| 32²/0.1 | +0.11% | +0.50% | +0.27% | 1.2e-03 |
| 64²/0.025 | +0.58% | +1.38% | +0.93% | 2.8e-03 |

## Kratos against solids4foam at the same nominal levels

solids4foam values are recomputed from the paper-data histories with the same function. Difference = (Kratos - solids4foam) / solids4foam.

| level | code | peak (m) | trough (m) | mean (m) | phase (s) | max history difference (m) |
|---|---|---|---|---|---|---|
| 16²/0.2 | solids4foam (legacy0-mesh16.csv) | 0.29342 | 0.19421 | 0.24257 | 4.600 | |
| | Kratos | 0.26160 | 0.19716 | 0.22878 | 4.600 | 0.0320 |
| | difference | -10.85% | +1.52% | -5.68% | +0.000 | |
| 32²/0.1 | solids4foam (legacy-mesh32.csv) | 0.28893 | 0.19864 | 0.24268 | 4.500 | |
| | Kratos | 0.26199 | 0.20319 | 0.23153 | 4.600 | 0.0285 |
| | difference | -9.32% | +2.29% | -4.60% | +0.100 | |
| 64²/0.05 | solids4foam (legacy-mesh64.csv) | 0.28701 | 0.20223 | 0.24376 | 4.500 | |
| | Kratos | 0.25810 | 0.20220 | 0.22914 | 4.635 | 0.0316 |
| | difference | -10.07% | -0.02% | -6.00% | +0.135 | |
| 96²/0.025 | solids4foam (legacy-mesh96.csv) | 0.28612 | 0.20443 | 0.24451 | 4.478 | |
| | Kratos | 0.25700 | 0.20190 | 0.22843 | 4.645 | 0.0318 |
| | difference | -10.18% | -1.24% | -6.58% | +0.168 | |
| 64²/0.025 | solids4foam (strict-dt0.025.csv) | 0.28697 | 0.20203 | 0.24366 | 4.500 | |
| | Kratos | 0.25768 | 0.20203 | 0.22885 | 4.625 | 0.0321 |
| | difference | -10.21% | +0.00% | -6.08% | +0.125 | |
