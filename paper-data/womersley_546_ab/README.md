# womersleyTube A/B across PR #546 (2026-11-04)

Rerun of the full verification study (`./Allverify --study all --cores 7`) on xenosim, OpenFOAM v2512, GCC 11.4 `-O3`, solids4foam `b200718f4` (development, after #546 and #598). Total wall time 35 min.

All six Robin-Neumann rows reproduce the README-recorded errors (PR #533 build `a507bfd41`, before #546) to every digit given, in all seven QoIs and in the iterations per step. #546 therefore has no visible effect on this case.

The IQN-ILS row changes slightly (flow_amp 5.38e-4 vs 5.48e-4; wallMid_amp -4.56e-4 vs -4.47e-4) and its mean iterations per step fall from 14.6 to 8.56, consistent with later IQN-ILS changes on development; Robin-Neumann and IQN-ILS now agree to 2.07e-4 (was 2.2e-4). All checks PASS.
