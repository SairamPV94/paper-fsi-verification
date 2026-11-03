#!/bin/bash
# usage: analyze.sh <id> ...   (run inside a Slurm allocation) : run_report + forensic energy + traction audit per run
R=<project-root>; O=$R/OVERNIGHT2; cd $R; export OMP_NUM_THREADS=1
for id in "$@"; do
 ( dry=runs/phaseB/B1_dry_hex8_f1; case $id in *2) dry=runs/phaseB/D1_dry_f2;; *t) dry=runs/phaseC/C1_dt200_dry_f1;; esac
   python3 -I tools/run_report.py OVERNIGHT2/runs/$id $dry > $O/analysis/$id.report.txt 2>&1
   python3 -I $O/scripts/forensic_energy.py OVERNIGHT2/runs/$id $O/analysis/$id.energy.json $O/analysis/$id.energy.npz > $O/analysis/$id.energy.txt 2>&1
   python3 -I $O/scripts/traction_audit.py OVERNIGHT2/runs/$id $O/analysis/$id.traction.json $O/analysis/$id.traction.npz > $O/analysis/$id.traction.txt 2>&1 ) &
done; wait
