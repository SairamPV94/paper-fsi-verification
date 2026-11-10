#!/usr/bin/env python3
"""Run a list of cavity cases under a thread budget.

Usage: python run_queue.py <jobs file> --budget 10 [--template <input dir>]
Each non-comment line of the jobs file is: <threads> <run name> [make_case.py options]
Paths are relative to the parent of this script's directory. Inputs are generated from --template
(default inputs/L1, use case/ in the paper-data package) into inputs/gen/<run name> and run into
runs/<run name> with run_case.sh from this script's directory. Jobs start in file order whenever their threads fit in the budget.
Existing run directories are skipped, never overwritten.
"""
import argparse
import datetime
import os
import shlex
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CASE = os.path.dirname(HERE)


def log(msg):
    print(f"{datetime.datetime.utcnow():%Y-%m-%dT%H:%M:%SZ} {msg}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jobs")
    ap.add_argument("--budget", type=int, default=10)
    ap.add_argument("--template", default="inputs/L1")
    args = ap.parse_args()
    jobs_file = os.path.abspath(args.jobs)
    os.chdir(CASE)
    jobs = []
    for line in open(jobs_file):
        line = line.split("#")[0].strip()
        if line:
            w = shlex.split(line)
            jobs.append((int(w[0]), w[1], w[2:]))
    running = {}
    while jobs or running:
        for name, (proc, threads) in list(running.items()):
            if proc.poll() is not None:
                log(f"done  {name} exit={proc.returncode}")
                del running[name]
        used = sum(t for _, t in running.values())
        for job in list(jobs):
            threads, name, opts = job
            if used + threads > args.budget:
                continue
            jobs.remove(job)
            run_dir = os.path.join("runs", name)
            if os.path.exists(run_dir):
                log(f"skip  {name} (run dir exists)")
                continue
            in_dir = os.path.join("inputs", "gen", name)
            if not os.path.exists(in_dir):
                subprocess.run([sys.executable, "-I", os.path.join(HERE, "make_case.py"), args.template, in_dir]
                               + opts, check=True, stdout=subprocess.DEVNULL)
            proc = subprocess.Popen([os.path.join(HERE, "run_case.sh"), in_dir, run_dir, str(threads)])
            running[name] = (proc, threads)
            used += threads
            log(f"start {name} threads={threads} opts={' '.join(opts)}")
        time.sleep(10)
    log("queue empty")


if __name__ == "__main__":
    main()
