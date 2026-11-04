#!/bin/bash
# Task 1: 3dTube levels 1-3 on 32 cores with the probe shift (paper-fsi-verification #57)
source ~/OpenFOAM/balis-v2512/env-task1.sh
cd ~/OpenFOAM/balis-v2512/solids4foam-b200718f4/tutorials/fluidSolidInteraction/3dTube/verification
{ date; hostname; env | grep -E 'OMP_NUM_THREADS|OPENBLAS_NUM_THREADS|PETSC_DIR|WM_PROJECT_VERSION'; } | tee log.environment
echo "Started: $(date)" | tee log.Allverify
./Allverify --levels 1,2,3 --cores 32 --probe-z-shift 7.8125e-5 2>&1 | tee -a log.Allverify
echo "Finished: $(date) (exit ${PIPESTATUS[0]})" | tee -a log.Allverify
exec bash
