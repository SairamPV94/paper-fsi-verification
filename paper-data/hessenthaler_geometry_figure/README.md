# Hessenthaler geometry figure (`figures/hessenthaler-geometry.pdf`)

- `section.py` cuts the published fluid-domain surface (solids4foam
  `tutorials/fluidSolidInteraction/hessenthalerFsi/constant/triSurface/fluidDomain.stl.gz`,
  development branch) at x = 0, giving `section_x0.npz` (segments per patch, mm).
- `feF1_x0.vtk` is the feF1 fluid mesh cut at x = 0.3 mm (OpenFOAM v2512
  `surfaces` function object, `cuttingPlane`, no interpolation); the plane is
  offset from x = 0 so that it does not coincide with octree cell faces.
- `phaseI_centreline.csv` is the measured Phase I deformed centreline
  (Hessenthaler et al. 2017, CC0; copied from the tutorial's `validation/reference`).
- `fig.py` draws the figure (matplotlib); run it in this directory.
