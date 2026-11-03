# Provenance findings for tab:provenance (sectionVerificationMethodology.tex:145-177)

Compiled 2026-11-03. Read-only: nothing in either repository was changed.
Reference commits: PR #492 (predictor default) merge `e65fd4ed9` (2026-10-02T09:57Z); the
default change itself is `7709d76a4` (2026-09-27, branch fix-489-hronturek-fsi2).
PR #546 merge `978ffc8dd` (2026-10-13). All READMEs below were read from `origin/development`.

What #492 changed (`git show 7709d76a4`): the IQNILS `predictor` default went from
`false` to `true` (`lookupOrAddDefault<Switch>("predictor", true)`), and Aitken and
fixedRelaxation now honour `predictor`. Before that change, IQNILS already honoured
an explicit `predictor yes`. Cases with fixedRelaxation and relaxationFactor 1 are
unaffected.

## 1. README-recorded results: commit, and whether they predate #492

Method: `git log --all -S'<number>' -- '*README.md'` on table values, then
`git merge-base --is-ancestor`. The run happened at or before the recording commit. The
lower bound is the first commit of the case's `verification/` driver.

| Case | Numbers searched | First recorded in | Lower bound (driver) | #492 (7709d76a4 / e65fd4ed9) in ancestry? | Case settings at that commit | Confidence |
|---|---|---|---|---|---|---|
| ringAddedMass | 2.55254, 0.76843, 3.08290 | `0a3719424` 2026-09-29 12:57 (only commit that changes the README tables) | same commit | no / no | `fsiProperties.iqnils`: IQNILS, `predictor yes` (l.25), RF 0.05. `.robin`: fixedRelaxation, `predictor yes`, RF 1.0 | high |
| collapsibleChannel | -16.7%, -0.18511 → `8a7a13942` 2026-09-29 08:02; -0.21278 (solid study) → `c59dbf84a` 2026-09-29 13:01 | `8a7a13942` + `c59dbf84a` (only two commits that change the README tables) | `975fa9e4f` 2026-09-28 | no / no | iqnils: `predictor yes`, RF 0.005. robin: fixedRelaxation, `predictor yes`, RF 1.0 | high |
| TurekHron2006 FSI1 (then HronTurekFsi3) | 2.20672e-5, 7.82820e-4, 14.18027 | `223adae07` 2026-09-27 14:09 | `643a4bffb` 2026-09-26 | no / no | `fsiProperties.iqnils`: `predictor yes` (l.28), RF 0.05. Robin arm RF 1.0 | high |
| TurekHron2006 FSI2 | -11.643, 256.70, 216.04 | `18a052637` 2026-09-29 08:01 | `643a4bffb` | no / no | the same; README says "IQN-ILS with `predictor yes`" | high |
| mokLidDrivenCavity | tables | `ba5decc67` 2026-09-27 19:08 and `6e69ddb6c` 2026-09-27 21:08 (only two commits that change the README tables) | `d4afaec12` 2026-09-27 | no / no | iqnils: `predictor yes`. The `.aitken` variant also says `predictor yes`, which pre-#492 Aitken ignored, but README: "All members use the IQN-ILS coupling with the interface predictor" | high |
| blobInTreacle | tables | `287ab2019` 2026-09-27 and `14672e1d6` 2026-10-02 11:28 ("verification results with the consistent formulation"; 24 table lines) | `9a0c62568` 2026-09-27 | no / no (`14672e1d6` was committed 30 min after #492 merged, but its ancestry does not contain it; development was merged in 6 s later at `a6a5bd090`) | `fluidSolidInterface IQNILS`, `predictor yes` (l.48), RF 0.05 | high |

- All of these recording commits are ancestors of `7c928c55a` (the commit the table cites), and
  none contains #492 or #546.
- In every case the recorded coupling is IQNILS with an explicit `predictor yes`, or a Robin
  fixedRelaxation arm with RF 1.0, so the #492 default change does not affect the results. #492's
  own commit message lists RF 1 cases as unchanged.
- README text on platform:
  - ring: "Recorded with OpenFOAM v2412 on xenosim with `./Allverify --cores 32`".
  - collapsible: "OpenFOAM v2412 and PETSc 3.24 on Linux, one case per core on a Slurm node (the
    static study also on macOS with PETSc 3.22)". PETSc 3.24 exists only on xenosim (MeluXina has
    3.22.0), so "Linux" here is xenosim.
  - FSI1/FSI2: "OpenFOAM v2412 on an Apple M1 Ultra".
  - Mok: "OpenFOAM v2412 on an Apple Silicon Mac Studio".
  - blob: "OpenFOAM v2512 on Linux, with `--cores 4`".
- No README states a commit hash or a date for its own results.
- On xenosim I found no surviving run directories for the September ring, collapsible or blob
  runs (only the 2026-10-09 PR #546 A/B copies under `~/scratch/pr546`).
- A xenosim build `~/OpenFOAM/philipc-v2412-verif` exists: system v2412, solids4foam
  `fc4304f0` (2026-09-25), built 2026-09-27 19:04. It is an ancestor of the ring and collapsible
  commits and probably served those runs, but no log ties it to them.

## 2. Compiler and flags

### (a) macOS (this Mac Studio)

Both v2512 and v2412 report:

```
WM_COMPILER=Clang  WM_COMPILE_OPTION=Opt  WM_OPTIONS=darwin64ClangDPInt32Opt  WM_COMPILE_CONTROL=(empty)  FOAM_EXTRA_CXXFLAGS=(empty)
```

- `General/Clang/c++` sets `c++OPT := -O2`, but it ends with
  `sinclude $(GENERAL_RULES)/common/c++$(WM_COMPILE_OPTION)`, and `General/common/c++Opt` sets
  `c++OPT := -O3`. `darwin64Clang` has no c++Opt of its own.
- `wmake -show-cxxflags` gives for v2512 (v2412 is the same with `-DOPENFOAM=2412`):
  `-std=c++17 -m64 -pthread -ftrapping-math -DOPENFOAM=2512 -DWM_DP -DWM_LABEL_SIZE=32 -Wall ... -O3 -DNoRepository -ftemplate-depth-100 -fPIC`.
  So the effective flags are **-O3**.
- The compiler today is Apple clang 21.0.0 (clang-2100.4.1.1) from Xcode 27.2, but Xcode.app was
  modified on 2026-10-31.
- The libraries used for the campaign record the toolchain in LC_BUILD_VERSION as
  `sdk 27.0, ld 27037.1`:
  - philipc-v2512 lib, 2026-09-25;
  - philipc-v2412 lib, 2026-09-26;
  - monoBuild/ring3 lib, 2026-10-15.
- They were therefore built with the **Xcode 27.0 Apple Clang**, not the current 27.2. The exact
  clang build string is not stored in the binaries. Confidence: high for -O3; medium for "Xcode
  27.0 Apple Clang".

### (b) womersleyTube (`a507bfd41`, PR #533)

Platform is xenosim (Linux), confirmed:

- `paper-data/r1_audit/r1_audit_cases.csv` rows 5-9 say "xenosim".
- The run directory exists on xenosim at
  `~/OpenFOAM/philipc-v2512/solids4foam.development/.claude/worktrees/bridge-cse_01AqCKp8LYUDtr4rN1ZcgPAw/tutorials/fluidSolidInteraction/womersleyTube/verification/work/`.
- Its logs give `Build : _87ed40d2-20251219 OPENFOAM=2512`, `Host : xenosim`, Date Oct 03 2026,
  start times 23:19:36-42.

Timing against the commits (xenosim reflog):

- The runs started after `e76f9cffc` (2026-10-03 22:58) and before `a507bfd41`
  (2026-10-04 07:53), which recorded them.
- `git diff --stat e76f9cffc a507bfd41 -- src applications` is empty, so the code that ran is the
  `a507bfd41` code, unless there were uncommitted edits.

Compiler and libraries:

- xenosim has gcc 11.4.0 (Ubuntu 11.4.0-1ubuntu1~22.04.3).
- `/usr/lib/openfoam/openfoam2512/wmake/rules/linux64Gcc/c++Opt` has `c++OPT = -O3`, and
  `General/common/c++Opt` has `-O3`.
- PETSc is 3.24.1 (see 3).

Answer: **GCC 11.4, -O3, xenosim.** Confidence: high.

### (c) v2512 on MeluXina (qm-a421 env: a421f063d tolerance sweeps, Mok and collapsible reruns; also FSI3 8x')

The env (`qm-a421/env.sh`) sources `openfoam-v2512/env-modules.sh`, which loads foss/2024a
and PETSc/3.22.0-foss-2024a, and then a source-built `OpenFOAM-v2512/etc/bashrc`. There is no
WM_COMPILE_CONTROL or FOAM_EXTRA_CXXFLAGS override; `etc/prefs.sh` only sets
`FOAM_CONFIG_ETC=etc/easybuild` and `WM_MPLIB=SYSTEMOPENMPI`.

WM_OPTIONS is `linux64GccDPInt32Opt`. The OpenFOAM-v2512 rule file has been edited:

- `wmake/rules/linux64Gcc/c++Opt` (mtime 2026-10-04 23:12; core libs built 23:36 that night)
  contains `c++OPT = -O2 -fno-tree-vectorize -march=znver2`.
- This overrides the OpenFOAM default -O3. It matches the EasyBuild OpenFOAM v2412 module's
  flags, which also add `-fno-math-errno`.

`wmake -show-cxxflags` gives:
`-std=c++17 -m64 -pthread -DOPENFOAM=2512 ... -O2 -fno-tree-vectorize -march=znver2 -DNoRepository -ftemplate-depth-100 -fPIC`.

- `readelf -p .comment` on qm-a421 `libsolids4FoamModels.so` (2026-10-29) shows
  `GCC: (GNU) 13.3.0`.
- `gcc --version` cannot run on the login node because the module command is not available
  in a non-interactive shell; the .comment section is the evidence.

FSI3 8x' build:

- `/project/home/p201136/philip-ht/env-ht8.sh` says "src = 30d6e22f3 + PR #562 / 541f5b008,
  source-built OpenFOAM v2512, foss-2024a (GCC 13.3)".
- It sources the same openfoam-v2512, so its flags are the same.
- Its `s4f-8x` lib (2026-10-14) shows GCC 13.3.0 and NEEDED libpetsc.so.3.22.

v2412 on MeluXina (EasyBuild `OpenFOAM/v2412-foss-2024a`, used by 3dTube, Hessenthaler and
beam): its `c++Opt` is `-O2 -fno-tree-vectorize -march=znver2 -fno-math-errno -std=c++14 -fuse-ld=bfd`,
and the solids4foam lib (2026-10-05) shows GCC 13.3.0. The table's "GCC 13.3 -O2" is correct,
but could say "-O2 -march=znver2 (EasyBuild)".

Confidence: high.

## 3. PETSc versions

- **Mac:**
  - `PETSC_DIR=/Users/philipc/code/petsc/`, `PETSC_ARCH=arch-darwin-c-opt` (git
    `v3.22.2-4-g745e2eeb5eb`; petscversion.h is 3.22.2).
  - Every solids4foam dylib links `.../arch-darwin-c-opt/lib/libpetsc.3.22.dylib (current version 3.22.2)`.
    This holds for v2512, v2412 and monoBuild/ring3.
  - `pkg-config --modversion PETSc` prints 3.23.2, but that is Homebrew's
    `/opt/homebrew/opt/petsc`, which is not linked. Ignore it.
  - **PETSc 3.22.2.** High.
- **MeluXina qm-a421 (v2512):** PETSc/3.22.0-foss-2024a from env-modules.sh;
  `libsolids4FoamModels.so` has NEEDED `libpetsc.so.3.22`. The login-node `PETSC_DIR` points to
  3.20.3-foss-2023a from the user's login profile and is not what the build used.
  **3.22.0.** High.
- **MeluXina s4f-verif-v2412:** `module load OpenFOAM/v2412-foss-2024a PETSc/3.22.0-foss-2024a`;
  lib NEEDED `libpetsc.so.3.22`. **3.22.0.** High.
- **xenosim:**
  - `/opt/petsc/current -> 3.24` (link dated 2025-11-06 11:59).
  - In `/opt/petsc/3.24/lib`, `libpetsc.so -> libpetsc.so.3.024.1`, file dated 2025-11-06 11:50.
  - `libpetsc.so.3.023.5` (2025-08-25) is still present, reachable only via the
    `libpetsc.so.3.023` soname link.
  - Every solids4foam build found on xenosim (2025-12 to 2026-11, including
    philipc-v2412-verif, ht_prod, philipc-v2512*) has NEEDED `libpetsc.so.3.024`.
  - So every xenosim run in this campaign (2026) used **PETSc 3.24.1**. 3.23.5 was current only
    from 2025-08-25 to 2025-11-06, before the campaign. High.
- ht_prod uses `source /etc/profile.d/petsc.sh`, which points to /opt/petsc, so 3.24.1.

## 4. OpenFOAM release of the FSI3 corrected 1x'-4x' runs

- `paper-data/hronturek_fsi3_4x_findings.md` §20 does not name the platform of the 1x'-4x'
  coupled runs. §21.1 implies xenosim ("platform (MeluXina against xenosim, coupled 1x' and 2x'
  to 6 s)").
- On xenosim, `~/ht_prod/work/c_{1x,2x,4x}_*` (exactly the case names in
  `hronturek_production_coupled_runs.csv`) have:
  - `log.solids4Foam` headers `Build : _87ed40d2-20251219 OPENFOAM=2512 version=2512`,
    `Host : xenosim`;
  - dates 2026-10-11 to 2026-10-13;
  - nProcs 4-24.
- `~/ht_prod/env_prod.sh` reads "Production build: solids4foam verification/hronturek-production
  (incl. PR #554), v2512, GCC 11.4 -O3, xenosim". Its `FOAM_USER_LIBBIN=~/ht_prod/build/lib`
  holds a lib built 2026-10-11 09:25 with GCC 11.4.0.
- The source tree `~/ht_prod/s4f` is at `30d6e22f3` (2026-10-11 09:19, "Merge PR #554
  branch ... into the HronTurek second-order study").
- So the runs used **`30d6e22f3`, not `636d567c6`**. The results were committed at
  `a2d9b94c5` (2026-10-13).
- `636d567c6` (2026-10-27) descends from it. Between the two, the only src change is
  `769640289` (#555, solid restart fix, 3 files). The rest is scripts and README. The 1x'-4x'
  runs are cold starts, so #555 is irrelevant to them.
- Neither commit contains #546. Both contain #492.
- Answer: **OpenFOAM v2512 (Ubuntu package 2512, build _87ed40d2-20251219), GCC 11.4 -O3,
  PETSc 3.24.1, xenosim, solids4foam 30d6e22f3.** High.
- The 8x' row: env-ht8.sh says "30d6e22f3 + PR #562 / 541f5b008"; README recorded at
  `636d567c6`.

## 5. cavityFlexibleBottom four-level study

### Commit and platform

- Partitioned four-level results were first recorded in solids4foam `5f6f7a6da` (2026-10-17,
  `verification/results/four_level_partitioned_monolithic.{csv,json}` plus README section
  "Partitioned four-level sequence ... (recorded 17 Oct 2026)").
- The README at that commit states: "macOS arm64 (Mac Studio), Apple Clang, OpenFOAM v2512
  (build 87ed40d256-20251219), solids4foam ... branch `feature-ring-monolithic-verification`
  at 0698d55cd (HEAD when the `ring3` library used by the recorded partitioned runs was built on
  15 Oct 2026; the working tree at build time is not independently verified)".
- Level 4 ran on 4 MPI ranks.
- `monoBuild/ring3/lib/libsolids4FoamModels.dylib` (2026-10-15 22:57) exists on this Mac. It has
  sdk 27.0 and links PETSc 3.22.2.
- `0698d55cd` contains both #546 (978ffc8dd) and #492.
- The CSV was carried unchanged for the partitioned rows into `f356c3242` (2026-10-20; that
  commit only reran the quasi-monolithic set with #597).
- Answer: **0698d55cd (results 5f6f7a6da), v2512, Apple Clang (Xcode 27.0) -O3, PETSc 3.22.2,
  macOS; #546: after.** High, with the README's own caveat about the working tree.

### The fourth-digit difference

Top-surface u_y (point A) from `f356c3242:.../four_level_partitioned_monolithic.csv` and the
5f6f7a6da README:

| Level | partitioned_legacy | partitioned_strict | QM pre-#597 (README "Quasi-monolithic uy, top") | QM #597 | QM #618 (paper-data/cavity_monolithic_618) |
|---|---:|---:|---:|---:|---:|
| 1 | -0.204563 | -0.204568 | -0.203607 / -0.20361 | -0.203597 | -0.203601 |
| 2 | -0.231412 | -0.231445 | -0.231431 / -0.23143 | -0.231074 | -0.231044 |
| 3 | -0.238396 | -0.238404 | -0.238445 / -0.23845 | -0.238211 | -0.238200 |
| 4 | -0.240118 | -0.240113 | -0.240142 / -0.24014 | -0.23999 | -0.239986 |

- The paper's set (-0.2046, -0.2314, -0.2384, -0.2401) is the partitioned top-surface set, and
  it is correct.
- The paper-data set (-0.2036, -0.2314, -0.2385, -0.2401) is the **quasi-monolithic pre-#597**
  top-surface sequence. The 5f6f7a6da README table, headed "Quasi-monolithic `uy`", lists it
  to 5 digits: -0.20361, -0.23143, -0.23845, -0.24014. Rounding those 5-digit values gives
  -0.2385 for level 3; the 6-digit value -0.238445 rounds to -0.2384.
- Paper history shows how the mixed set arose:
  - paper `4f8d630` (2026-10-17) printed that QM set as "the steady top-surface u_y";
  - paper `c53fe3f` (2026-10-20 00:45, "attribute the top-surface sequence to the partitioned
    solver") replaced levels 1 and 3 with the partitioned values;
  - `paper-data/cavity_plate_material_law_findings.md` (745c0c8, 2026-10-20) and
    `reference_levels.csv` / `reference_convergence.py` (640249e) kept the old QM-pre-#597 u_y
    values.
- Those paper-data rows also pair the pre-#597 QM u_y with the #597 QM F_y. The F_y values
  (-5.123, -5.228, -5.251, -5.256) are the `monolithic_597` column.
- Correct for the current definition (point A on the top surface, PR #584, merged 2026-10-19 as
  `f44b91451`), partitioned: **-0.2046, -0.2314, -0.2384, -0.2401**, i.e. the paper text. The
  partitioned F_y is -5.1528, -5.2388, -5.2566, -5.2599 (strict).
- If paper-data is meant to hold the current QM values, they are the #618 values: -0.2036,
  -0.2310, -0.2382, -0.2400.
- Either way, `reference_levels.csv`, `reference_convergence.py` l.46 and the findings tables
  (l.19-22, 94-97) should be regenerated. The Richardson value derived there (-0.24057, order
  2.15) comes from the mixed set.
- The partitioned three-finest Richardson value is about -0.2407. It is quoted in the paper
  and was not recomputed here.

## Proposed replacements for "README" / "n.r." cells

| Row | solids4foam | OpenFOAM | Compiler | Platform | #546 |
|---|---|---|---|---|---|
| ringAddedMass | `0a3719424` (README; pre-#492, explicit predictor) | v2412 | GCC 11.4 `-O3` | Linux (xenosim) | before |
| womersleyTube | `a507bfd41` (PR #533) | v2512 | GCC 11.4 `-O3` | Linux (xenosim) | before |
| collapsibleChannel | `8a7a13942`, `c59dbf84a` (README); mesh-study figure `a421f063d`† | v2412; v2512 | GCC 11.4 `-O3`; Apple Clang `-O3` (static); GCC 13.3 `-O2`‡ | Linux (xenosim); macOS (static); MeluXina | before; after |
| Hron–Turek FSI1, FSI2 | `223adae07`, `18a052637` (README) | v2412 | Apple Clang `-O3` | macOS | before |
| FSI3 corrected 1x'–4x' | `30d6e22f3` (cold starts; `636d567c6` adds only the restart fix #555) | v2512 | GCC 11.4 `-O3` | Linux (xenosim) | before; 2-D argument |
| FSI3 corrected 8x' | `30d6e22f3` + #562, recorded at `636d567c6` | v2512 | GCC 13.3 `-O2`‡ | MeluXina | before; 2-D argument |
| mokLidDrivenCavity | `ba5decc67`, `6e69ddb6c` (README); coupling test `a421f063d`† | v2412; v2512 | Apple Clang `-O3`; GCC 13.3 `-O2`‡ | macOS; MeluXina | before; after |
| cavityFlexibleBottom* | `0698d55cd` (results `5f6f7a6da`) | v2512 | Apple Clang `-O3` | macOS | after |
| blobInTreacle* | `14672e1d6` (README; pre-#492, explicit predictor) | v2512 | n.r. (GCC 11.4 `-O3` if xenosim) | Linux | before |
| Tolerance sweeps | `a421f063d` | v2512 | GCC 13.3 `-O2`‡ | MeluXina | after |

‡ For v2512 on MeluXina the full flags are `-O2 -fno-tree-vectorize -march=znver2`
(source-built, EasyBuild-style rules). For v2412 on MeluXina (EasyBuild) they are
`-O2 -fno-tree-vectorize -march=znver2 -fno-math-errno`. A footnote could state this once.

Suggested caption and footnote text:

- Replace "README: values recorded ... by commit 7c928c55" with "README: commit that recorded
  the values in the case's verification README (all precede PRs #492 and #546; every recorded
  run sets `predictor yes` explicitly or uses RF 1)".
- Add a PETSc line: "PETSc 3.24.1 (xenosim), 3.22.0 (MeluXina), 3.22.2 (macOS)".

## Genuinely unrecoverable (or only inferable)

- The exact working-tree state at run time for any README result. Commits are upper bounds;
  no logs survive on xenosim for ring, collapsible or blob, and the Mac runs were not checked
  for surviving logs.
- blobInTreacle platform host and compiler: the README says only "Linux". xenosim (GCC 11.4
  -O3, PETSc 3.24.1) is the likely host but is not confirmed by any log.
- Exact Apple clang build string for the macOS runs. Binaries record only SDK 27.0 / ld 27037.1;
  the current 21.0.0 (clang-2100.4.1.1) comes from Xcode 27.2, updated 2026-10-31, after those
  builds.
- Whether the ring and collapsible xenosim runs used the `philipc-v2412-verif` build
  (`fc4304f0`) or a build of the branch commit. Code identity between the two is not
  established.
- FEBio-ring row, solids4foam side: the s4f numbers are the README values (v2412, xenosim,
  `0a3719424`) per `febio_ring_added_mass/tools/phaseD_results.py:191`, so its OpenFOAM
  "n.r." can become v2412. `1576edcc` is the tutorial definition the FEBio model was built
  from, not the s4f run commit.
