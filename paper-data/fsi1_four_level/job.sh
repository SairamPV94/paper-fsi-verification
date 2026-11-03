#!/bin/bash -l
#SBATCH --account=p201287
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks=101
#SBATCH --time=24:00:00
#SBATCH --output=/project/home/p201287/philip/qm-a421/runs/fsi1/slurm-%j.out
# Verification paper: Hron-Turek FSI1 levels 1x-8x at a fixed pseudo-time step,
# strict coupling test with an absolute tolerance, build a421f063d.
source /project/home/p201287/philip/qm-a421/env.sh >/dev/null 2>&1
export PATH=/project/home/p201287/philip/qm-head/campaign/pybin:$PATH
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
export SOLIDS4FOAM_ROOT=/project/home/p201287/philip/qm-a421/solids4foam
D=/project/home/p201287/philip/qm-a421/runs/fsi1
run() { ( cd $D/$1/verification && ./Allverify --benchmark fsi1 --levels $2 > $D/log.$1 2>&1; echo "rc $? $1 $(date)" ) & }
run L8 8; run L4 4; run L4dt2 4; run L2 2; run L1 1
wait
echo "done $(date)"
