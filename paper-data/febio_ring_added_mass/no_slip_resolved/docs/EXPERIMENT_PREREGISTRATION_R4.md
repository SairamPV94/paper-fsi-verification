# Experiment preregistration, round 4 (amplitude bound and third ring/tangential level)

Hashed before any round-4 input is run. Round-3 outcomes are fixed in `NUMERICAL_RESULTS.md`: K1 met, K3 met, K4 met, K5 met, K6 met; **K2 failed as registered** (ratio against the unpaired dry run B1 moved 0.0260 pp). The stated reason in that registration, a 9e-5 % dry-ratio effect, applied only to a paired dt change; a post hoc re-analysis with the existing paired dry run at half dt (`runs/phaseC/C1_dt200_dry_f1`) gives a ratio change of 0.0000 pp. Both statements stand; neither changes the other.

Reference configuration F2 (see round 3). Remaining open items for the like-for-like claim: (i) finite-amplitude and solid-kinematics terms, (ii) only two ring/tangential levels (F2 at factor 1, K3 at factor 2), so no order can be claimed.

| ID | Change relative to F2 | Question | Prediction |
|---|---|---|---|
| K7w, K7d | initial velocity amplitude halved (V0 = 0.75e-3 m/s) in both the wet run (F2 mesh) and its matched dry run (ring 4 x 48) | size of the O(amplitude^2) finite-amplitude / kinematics term in the no-slip ratio | ratio error against V changes by at most 0.01 pp relative to F2 (the free-slip moderate floor at full amplitude was 0.0075 %, so an A^2 term would give about 0.002 pp change) |
| K8 | ring and tangential resolution factor 4 (ring 16 x 192, 192 tangential cells), radial grading as F2 (first cell delta/4, 52 cells), four cores | third level for ring/tangential convergence | ratio error against V within 0.02 pp of K3's and decay within 5 % of K3's; matched dry run C1_M3_dry_f4 (same ring mesh and settings) |
Rules as in round 3: a prediction that holds is met, otherwise failed, nothing retuned; a non-converged run is reported and not rerun with changed settings. With F2, K3, K8 the differences between levels are reported; an observed order is stated only if the three-level differences are in the asymptotic ratio range and is otherwise declared undetermined. Budget: at most 12 CPU-h for the round; no source change.
