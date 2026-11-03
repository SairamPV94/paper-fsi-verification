#!/bin/bash -l
#SBATCH --job-name=fsi1_L8r
#SBATCH --account=p201287
#SBATCH --qos=default
#SBATCH --partition=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --time=05:00:00
#SBATCH --output=/project/home/p201287/philip/qm-a421/runs/fsi1/slurm-L8r-%j.out
# FSI1 8x: continue from t = 28 (the 24 h job stopped at t = 29.16), merge the
# restart's monitors into the first part, then let the driver evaluate (--reuse).
source /project/home/p201287/philip/qm-a421/env.sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
D=/project/home/p201287/philip/qm-a421/runs/fsi1
export SOLIDS4FOAM_ROOT=$D/L8
W=$D/L8/verification/work/fsi1_iqnils_mesh_8x
cd $W
for p in processor*; do rm -rf $p/29* 2>/dev/null; done
[ -d postProcessing.part1 ] || cp -r postProcessing postProcessing.part1
[ -f log.solids4Foam.part1 ] || mv log.solids4Foam log.solids4Foam.part1
mpirun -np 64 solids4Foam -parallel > log.restart 2>&1; echo "solver rc $?"
grep -q "^End" log.restart || { echo "restart did not finish"; exit 1; }
python3 $D/merge.py $W 28
cat log.solids4Foam.part1 log.restart > log.solids4Foam
cd $D/L8/verification && ./Allverify --benchmark fsi1 --levels 8 --reuse > $D/log.L8r 2>&1; echo "rc $? L8 $(date)"
