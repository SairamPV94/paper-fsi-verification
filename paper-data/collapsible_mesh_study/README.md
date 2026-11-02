# collapsibleChannel fluid-mesh study (Fig. fig:collapsible_mesh)

Wall-midpoint histories (`F1.dat` to `F4.dat`, the `solidPointDisplacement_wallMid.dat`
of each level) and the driver's `mesh_study.csv`, from the tutorial driver
`collapsible_channel_verification.py --study mesh` (Robin–Neumann, solid 160×8 high
order, Δt = 0.00625 s, tutorial tolerances), unchanged except for the work directory.

- Build: solids4foam `a421f063d`, OpenFOAM-v2512, MeluXina, job 5411606 (2 Nov 2026).
- This run reproduces the paper's numbers, which were first computed on OpenFOAM-v2412:
  maximum error 4.650, 1.425, 0.531 and 0.496% of the reference peak (paper:
  4.65, 1.43, 0.53, 0.50%), and the finest first trough is −0.21610 m.
- Fluid cells: 3 200, 12 800, 28 800 and 51 200, so the refinement ratios are
  2, 1.5 and 1.33.

Figure: `python3 ../figure_scripts/collapsible_mesh_figure.py . REF_dt160.csv REF.csv out.pdf`,
where the two reference CSVs are `collapsibleChannel_oomph_dt160.csv` and
`collapsibleChannel_oomph_reference.csv` from the tutorial's `verification/reference/`.
