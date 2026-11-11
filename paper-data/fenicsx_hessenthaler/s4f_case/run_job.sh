#!/bin/bash
#SBATCH -J hess-s4frun3
#SBATCH -p main
#SBATCH -n 16
#SBATCH -c 1
#SBATCH --mem=60G
#SBATCH -t 02:30:00
#SBATCH --export=NONE
#SBATCH -o /home/sairam/work/s4f-hess-ref/run-%j.out
set -eo pipefail
export USER="${USER:-$(id -un)}"; export HOME="${HOME:-$(getent passwd "$USER" | cut -d: -f6)}"
R=/home/sairam/work/s4f-hess-ref/build
set +eu; . $R/env.sh; set -e
cd /home/sairam/work/s4f-hess-ref/runs/feF1_strict
if [ ! -d processor0 ]; then
  decomposePar -region fluid > log.decomposePar.fluid 2>&1
  decomposePar -region solid > log.decomposePar.solid 2>&1
fi
echo START $(date +%s)
mpirun -np 16 --bind-to none solids4Foam -parallel >> log.solids4Foam 2>&1
echo END $(date +%s)
