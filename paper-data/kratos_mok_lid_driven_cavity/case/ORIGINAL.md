# Original Kratos example

The inputs in this directory are a port of the Kratos Multiphysics example
`fluid_structure_interaction/validation/fsi_lid_driven_cavity` (R. Zorrilla), from
KratosMultiphysics/Examples commit `fb900a52ddd87d66d58ead28e48ae9a733688716`, fetched on
2026-11-09. The original files are not copied here, because the Examples repository has no licence
file. They can be fetched from that commit and checked against these sha256 sums:

```
23b484a9de0525ed927dd28326228871fe2801706b017001381d1fc98fd724e5  FluidMaterials.json
fa5057b128ed8a9326bd8fee5aeaa86193a6319891d690a8b232b92cdc8de12d  fsi_lid_driven_cavity_Fluid.mdpa
cdc220d8515d973166cec3b5251c24887d1acd6211214a06c39caa1a47bad7a9  fsi_lid_driven_cavity_Structural.mdpa
22f2bf0bddb62de18ffad46419fd70798960987bbb7a9d405b8e7894d5d2a38b  MainKratos.py
5ef58290a957b3148b929a12cb8fe57797150122690b21ff5b188edda30db81c  ProjectParameters.json
380efcbaf2078f3348f3b859f1614da617a278afd5adbb022c1e42c30e687d29  StructuralMaterials.json
```

The example was written for Kratos 7.0. The port to 10.3.0 changes input keys only, and the physics,
meshes and solver settings are unchanged:

- the fluid `dynamic_tau` moved into `formulation: {element_type: vms, dynamic_tau: 1.0}`;
- the fluid `volume_model_part_name`, `skin_parts` and `no_skin_parts` use full model-part names;
- the structure keys `problem_domain_sub_model_part_list`, `processes_sub_model_part_list` and
  `line_search` were removed (no longer read; Newton-Raphson is the default);
- the mesh solver type `mesh_solver_structural_similarity` is now `structural_similarity`;
- the `mesh_id` keys were removed, and GiD output was replaced by VTK output every 10 steps;
- the material law module prefix is now `StructuralMechanicsApplication.`.

The ported example reproduces the shipped result (the digitised Kratos curve in
`tutorials/fluidSolidInteraction/mokLidDrivenCavity/verification/reference/` of solids4foam) to 0.06%
in peak, trough and mean. The two `.mdpa` meshes are not needed: `scripts/make_case.py` writes meshes
at any level, and its 32² meshes are geometrically identical to the shipped ones
(`scripts/compare_mdpa.py`).
