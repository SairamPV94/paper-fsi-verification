#!/usr/bin/env python3
"""Audit FSI coupling acceptance in a solids4Foam log.

Usage: grep -E '<filter>' log.solids4Foam | r1parse.py <logpath>
Prints one JSON line. Reads constant/fsiProperties next to the log (follows symlinks).
"""
import json, os, re, sys, statistics

log = sys.argv[1]
case = os.path.dirname(os.path.abspath(log))


def strip_comments(t):
    t = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
    return re.sub(r'//[^\n]*', '', t)


def fsi_props(case):
    p = os.path.join(case, 'constant', 'fsiProperties')
    out = {'fsiProps': None, 'type': None, 'tol': None, 'requireAll': None,
           'robinP': None, 'robinF': None, 'nOuterCorr': None}
    try:
        txt = strip_comments(open(p).read())
    except Exception:
        return out
    out['fsiProps'] = os.path.realpath(p)
    m = re.search(r'^\s*fluidSolidInterface\s+(\w+)\s*;', txt, re.M)
    typ = m.group(1) if m else None
    out['type'] = typ
    block = txt
    if typ:
        mb = re.search(typ + r'Coeffs\s*\{', txt)
        if mb:
            i, depth = mb.end(), 1
            while i < len(txt) and depth:
                depth += {'{': 1, '}': -1}.get(txt[i], 0)
                i += 1
            block = txt[mb.end():i]

    def get(key, src):
        mm = re.search(r'\b' + key + r'\s+([^;\s]+)\s*;', src)
        return mm.group(1) if mm else None
    for k, key in [('tol', 'outerCorrTolerance'),
                   ('requireAll', 'requireAllResidualMeasures'),
                   ('robinP', 'robinPressureTolerance'),
                   ('robinF', 'robinFluxTolerance'),
                   ('nOuterCorr', 'nOuterCorr')]:
        out[k] = get(key, block) or get(key, txt)
    return out


props = fsi_props(case)
logtype = None
steps = []  # list of (time, niter, r1, r2, passedBy)
cur = None
r1 = r2 = None
passed = None
nit = 0


def close():
    if cur is not None and r1 is not None:
        steps.append((cur, nit, r1, r2, passed))


num = re.compile(r':\s*([-+0-9.eEnaif]+)\s*$')
for line in sys.stdin:
    if line.startswith('Time = '):
        if ',' in line:
            continue
        close()
        cur = line[7:].strip()
        r1 = r2 = None
        passed = None
        nit = 0
    elif 'residual1 norm' in line:
        m = num.search(line)
        r1 = float(m.group(1)) if m else None
        nit += 1
        passed = None
    elif 'residual2 norm' in line:
        m = num.search(line)
        r2 = float(m.group(1)) if m else None
    elif 'passed by' in line:
        passed = line.strip()
    elif line.startswith('Selecting fluidSolidInterface'):
        logtype = line.split()[-1]
# last step: keep only if the log finished (we cannot know; flag it)
lastcur = cur
close()

res = {'log': log, 'logType': logtype, **props}
try:
    tol = float(props['tol'])
except Exception:
    tol = None
res['nSteps'] = len(steps)
if steps and tol is not None:
    # drop the final step (possibly incomplete) from statistics but report it
    body = steps[:-1] if len(steps) > 1 else steps
    r1a = [s[2] for s in body]
    r2a = [s[3] for s in body if s[3] is not None]
    a1 = [s for s in body if s[2] > tol]
    a2 = [s for s in body if s[3] is not None and s[3] > tol]
    r2only = [s for s in body if s[2] > tol and s[3] is not None and s[3] <= tol]
    unconv = [s for s in body if s[2] > tol and (s[3] is None or s[3] > tol)]
    n = len(body)
    t = [float(s[0]) for s in body]
    res.update({
        'nStepsUsed': n,
        'tEnd': t[-1] if t else None,
        'n_r1_gt_tol': len(a1), 'frac_r1_gt_tol': len(a1) / n,
        'n_r2_gt_tol': len(a2), 'frac_r2_gt_tol': len(a2) / n,
        'n_r2only': len(r2only), 'n_both_gt_tol': len(unconv),
        'max_r1_acc': max(r1a), 'median_r1_acc': statistics.median(r1a),
        'max_r2_acc': max(r2a) if r2a else None,
        'iter_mean': sum(s[1] for s in body) / n,
        'iter_max': max(s[1] for s in body),
        'n_passedBy_msg': sum(1 for s in body if s[4]),
    })
    try:
        nmax = int(props['nOuterCorr'])
    except Exception:
        nmax = None
    res['nIterHist'] = {}
    for s in body:
        res['nIterHist'][s[1]] = res['nIterHist'].get(s[1], 0) + 1
    if nmax:
        atmax = [s for s in body if s[1] > nmax]
        res['n_at_max'] = len(atmax)
        res['n_r1_gt_tol_below_max'] = sum(1 for s in a1 if s[1] <= nmax)
        res['n_r1_gt_tol_below_max_r2ok'] = sum(1 for s in r2only if s[1] <= nmax)
        res['n_r1_gt_tol_1iter'] = sum(1 for s in a1 if s[1] <= 1)
        sub = [s[2] for s in a1 if s[1] <= nmax]
        res['max_r1_acc_below_max'] = max(sub) if sub else None
    if a1:
        idx = [i for i, s in enumerate(body) if s[2] > tol]
        # distribution over run fraction deciles
        dec = [0] * 10
        for i in idx:
            dec[min(9, i * 10 // n)] += 1
        res['r1_exc_deciles'] = dec
        res['first_exc_t'] = body[idx[0]][0]
        res['last_exc_t'] = body[idx[-1]][0]
        imax = max(range(n), key=lambda i: body[i][2])
        res['t_max_r1'] = body[imax][0]
        res['iter_at_max_r1'] = body[imax][1]
        res['first10_steps_exc'] = sum(1 for i in idx if i < 10)
print(json.dumps(res))
