#!/usr/bin/env python3
"""Forensic analysis of an existing ringAddedMass FEBio run (post-processing only).
usage: forensic_energy.py <run_dir> <out_json> [<out_npz>]
Computes from the run's stored nodal and element output:
  * frequency / decay fits for several windows, zero-crossing frequency, envelope decay
  * energy history: ring KE (lumped mass), ring strain energy (hex8, small strain, E=1e6, nu=0.3, plane strain u_z=0),
    fluid KE of ABSOLUTE velocity (v_mesh + w, lumped mass), fluid compressive energy sum V p^2/(2K), mesh-regulariser bound,
    viscous dissipation rate integral 2 mu eps:eps (one-point element gradient of the absolute velocity)
  * pressure: n=0 / n=2 of layer 0 (as tools/pressure_modes.py), whole-fluid mean pressure vs time, radial profile of the n=0 content,
    mean(J-1) and the geometric fluid-area change from the stored nodal displacements
Lumped masses and gradients use the REFERENCE geometry (displacements are O(5e-4) of the radius). Nothing is tuned."""
import sys, json, math, os
import numpy as np
import xml.etree.ElementTree as ET
sys.path.insert(0, "<project-root>/tools")
import analyze_ring as AR

run = sys.argv[1].rstrip("/"); out_json = sys.argv[2]; out_npz = sys.argv[3] if len(sys.argv) > 3 else None
meta = json.load(open(run + "/model_meta.json")); tag = meta["tag"]
nrs, nt, nrf = meta["dims_nrs_nt_nrf"]
RHO_S, E, NU, RHO_F, K, EMESH = 1000.0, 1e6, 0.3, meta["rho_f"], meta["k"], meta["e_mesh"]
MU = RHO_F * (meta["nu_f"] if meta.get("nu_f") else 1e-7)
omega_ref = meta["omega_ref"]; T = 2 * math.pi / omega_ref

root = ET.parse(f"{run}/{tag}.feb").getroot()
X = {int(n.get("id")): np.array([float(v) for v in n.text.split(",")]) for n in root.find("Mesh/Nodes")}
def elems(name):
    for el in root.findall("Mesh/Elements"):
        if el.get("name") == name:
            return [(int(e.get("id")), [int(v) for v in e.text.split(",")]) for e in el]
    return []
ring_el, fl_el = elems("Ring"), elems("Fluid")

GP = 1 / math.sqrt(3)
SGN = np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]], float)
def dN(r, s, t):
    g = np.zeros((8, 3))
    for a in range(8):
        sr, ss, st = SGN[a]
        g[a] = [sr*(1+ss*s)*(1+st*t)/8, ss*(1+sr*r)*(1+st*t)/8, st*(1+sr*r)*(1+ss*s)/8]
    return g
def Nf(r, s, t):
    return np.array([(1+SGN[a,0]*r)*(1+SGN[a,1]*s)*(1+SGN[a,2]*t)/8 for a in range(8)])
NQ = np.array([Nf(r, s, t) for r in (-GP, GP) for s in (-GP, GP) for t in (-GP, GP)])   # 8 gp x 8 nodes
def hex_geom(conn):
    P = np.array([X[n] for n in conn]); vol = 0.0; B = []; w = []
    for r in (-GP, GP):
        for s in (-GP, GP):
            for t in (-GP, GP):
                g = dN(r, s, t); J = P.T @ g; dj = np.linalg.det(J); B.append(g @ np.linalg.inv(J)); w.append(dj)
    return P, np.array(B), np.array(w)

# ---- ring stiffness (plane-strain energy from 3D hex8, uz = 0) and lumped masses
lam = E*NU/((1+NU)*(1-2*NU)); mu_s = E/(2*(1+NU))
Dm = np.zeros((6, 6)); Dm[:3, :3] = lam; Dm[0, 0] = Dm[1, 1] = Dm[2, 2] = lam + 2*mu_s; Dm[3, 3] = Dm[4, 4] = Dm[5, 5] = mu_s
ring_ids = sorted({n for _, c in ring_el for n in c}); ridx = {n: i for i, n in enumerate(ring_ids)}
import scipy.sparse as sp
rows, cols, vals = [], [], []; mass_r = {n: 0.0 for n in ring_ids}; mrows, mcols, mvals = [], [], []
for _, conn in ring_el:
    P, B, w = hex_geom(conn); Ke = np.zeros((24, 24))
    for q in range(8):
        Bm = np.zeros((6, 24)); b = B[q]
        for a in range(8):
            Bm[0, 3*a] = b[a, 0]; Bm[1, 3*a+1] = b[a, 1]; Bm[2, 3*a+2] = b[a, 2]
            Bm[3, 3*a] = b[a, 1]; Bm[3, 3*a+1] = b[a, 0]
            Bm[4, 3*a+1] = b[a, 2]; Bm[4, 3*a+2] = b[a, 1]
            Bm[5, 3*a] = b[a, 2]; Bm[5, 3*a+2] = b[a, 0]
        Ke += Bm.T @ Dm @ Bm * w[q]
    dof = np.array([3*ridx[n]+c for n in conn for c in range(3)])
    rows += list(np.repeat(dof, 24)); cols += list(np.tile(dof, 24)); vals += list(Ke.ravel())
    for n in conn: mass_r[n] += w.sum() / 8
    Me = np.einsum("q,qa,qb->ab", w, NQ, NQ) * RHO_S
    nodes_ = [ridx[n] for n in conn]
    mrows += list(np.repeat(nodes_, 8)); mcols += list(np.tile(nodes_, 8)); mvals += list(Me.ravel())
Kr = sp.coo_matrix((vals, (rows, cols)), shape=(3*len(ring_ids),)*2).tocsr()
mr = np.array([mass_r[n] for n in ring_ids]) * RHO_S
Mr = sp.coo_matrix((mvals, (mrows, mcols)), shape=(len(ring_ids),)*2).tocsr()

# ---- fluid masses and element volumes
fl_ids = sorted({n for _, c in fl_el for n in c}); fidx = {n: i for i, n in enumerate(fl_ids)}
mass_f = np.zeros(len(fl_ids)); Vel = []; Bg = []; Bq = []; Wq = []
for _, conn in fl_el:
    P, B, w = hex_geom(conn); Vel.append(w.sum()); Bq.append(B); Wq.append(w)
    for n in conn: mass_f[fidx[n]] += w.sum() / 8
    # one-point gradient at the element centre
    g = dN(0, 0, 0); J = P.T @ g; Bg.append(g @ np.linalg.inv(J))
mass_f *= RHO_F; Vel = np.array(Vel); Bg = np.array(Bg); Bq = np.array(Bq); Wq = np.array(Wq)
fl_conn = np.array([[fidx[n] for n in c] for _, c in fl_el])
fl_eid = [e for e, _ in fl_el]

# ---- read histories
t_p, d, v = AR.series(run + "/probes.txt")
rb = AR.read_blocks(run + "/ring_nodes.txt"); fb = AR.read_blocks(run + "/fluid_nodes.txt"); eb = AR.read_blocks(run + "/fluid_elems.txt")
t = np.array([b["t"] for b in rb]); nT = len(t)
def table(blocks, ids, cols):
    out = np.zeros((len(blocks), len(ids), cols)); pos = None
    for k, b in enumerate(blocks):
        r = np.array(b["rows"]); order = {int(x): i for i, x in enumerate(r[:, 0])}
        if pos is None: pos = [order[n] for n in ids]
        out[k] = r[pos, 1:1+cols]
    return out
R = table(rb, ring_ids, 4); Fn = table(fb, fl_ids, 6); Pe = table(eb, fl_eid, 2)   # R: ux uy vx vy; Fn: ux uy vx vy wx wy; Pe: p J
ux_r = np.zeros((nT, 3*len(ring_ids))); ux_r[:, 0::3] = R[:, :, 0]; ux_r[:, 1::3] = R[:, :, 1]
KEr = 0.5 * RHO_S * 0 + 0.5 * np.einsum("tai,ab,tbi->t", R[:, :, 2:4], Mr.toarray(), R[:, :, 2:4])      # consistent mass
PEr = 0.5 * np.einsum("ti,ti->t", ux_r, (Kr @ ux_r.T).T)
vab = Fn[:, :, 2:4] + Fn[:, :, 4:6]                                   # absolute fluid velocity = mesh velocity + relative velocity
p = Pe[:, :, 0]; J = Pe[:, :, 1]
PEc = (Vel[None, :] * p**2 / (2*K)).sum(1)
KEf = np.zeros(nT); Diss = np.zeros(nT); KEf_lumped = 0.5 * (mass_f[None, :] * (vab ** 2).sum(2)).sum(1)
for t0 in range(0, nT, 25):
    sl = slice(t0, min(nT, t0 + 25)); vc = vab[sl][:, fl_conn, :]           # t, elem, 8, 2
    vq = np.einsum("qa,teai->teqi", NQ, vc)
    KEf[sl] = 0.5 * RHO_F * (Wq[None, :, :] * (vq**2).sum(3)).sum((1, 2))
    G = np.einsum("eqaj,teai->teqij", Bq, vc)                             # d v_i/d x_j, j over x,y,z; i over x,y
    L3 = np.zeros(G.shape[:4] + (3,)); L3[..., :, :2 + 1] = 0
    Lg = np.zeros(G.shape[:3] + (3, 3)); Lg[..., :2, :] = G
    eps = 0.5 * (Lg + np.swapaxes(Lg, -1, -2))
    Diss[sl] = (2 * MU * (eps**2).sum((-1, -2)) * Wq[None, :, :]).sum((1, 2))
Wdiss = np.concatenate([[0.0], np.cumsum(0.5 * (Diss[1:] + Diss[:-1]) * np.diff(t))])
Etot = KEr + PEr + KEf + PEc

# ---- pressure diagnostics
NT = nt; dth = (math.pi / 2) / NT; th = (np.arange(NT) + 0.5) * dth
Pl = p.reshape(nT, NT, nrf)                                          # element ordering: j (tangential) outer, i (radial) inner
L0 = Pl[:, :, 0]
n0 = L0.mean(1); n2 = (L0 * np.cos(2 * th)).sum(1) * dth / (math.pi / 4)
pmean_all = (p * Vel[None, :]).sum(1) / Vel.sum()
Jmean = ((J - 1) * Vel[None, :]).sum(1) / Vel.sum()
n0_layers = Pl.mean(1)                                                # t, radial layer
# fluid area change from geometry: interface nodes (k=0 plane) polygon and wall polygon, via shoelace on the quarter + axes
def quarter_area(ids):
    pts = np.array([[X[n][0] + 0, X[n][1]] for n in ids])
    return None
pad = lambda k, ids: np.array([[X[n][0] + k[i, 0], X[n][1] + k[i, 1]] for i, n in enumerate(ids)])
# interface nodes = ring outer nodes (reference radius 1.05), k = 0 plane
ifc = [n for n in ring_ids if abs(math.hypot(X[n][0], X[n][1]) - 1.05) < 1e-9 and abs(X[n][2]) < 1e-12]
ifc.sort(key=lambda n: math.atan2(X[n][1], X[n][0]))
ii = [ridx[n] for n in ifc]
def area_interface(k):
    xy = np.array([[X[n][0] + R[k, ridx[n], 0], X[n][1] + R[k, ridx[n], 1]] for n in ifc])
    xy = np.vstack([[0.0, 0.0], xy]) if False else xy
    # quarter region bounded by the curve and the two axes: close through the origin
    pts = np.vstack([[0, 0], xy])
    x, y = pts[:, 0], pts[:, 1]
    return 0.5 * abs(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))
A_if = np.array([area_interface(k) for k in range(nT)]); dA_if = (A_if - A_if[0]) / (math.pi * 1.05**2 / 4)

# ---- fits
def windows():
    res = {}
    for name, (a, b) in {"0-4T": (0, 4*T), "T-4T": (T, 4*T), "0-3T": (0, 3*T), "0-2T": (0, 2*T), "2T-4T": (2*T, 4*T), "T-3T": (T, 3*T)}.items():
        if b > t_p[-1] + 1e-9: continue
        f = AR.fit_damped(t_p, d, a, b, omega_ref); wz, nz = AR.zero_crossing_omega(t_p, d, a, b)
        res[name] = dict(omega_fit=f["omega"], decay_rate=f["decay_rate"], amplitude0=f["amplitude0"], rms_resid=f["rms_resid"], omega_zc=wz)
    return res
# envelope from successive same-sign extrema of D(t)
idx = [i for i in range(1, len(d)-1) if abs(d[i]) >= abs(d[i-1]) and abs(d[i]) >= abs(d[i+1]) and abs(d[i]) > 0.3*np.max(np.abs(d))]
env_t = t_p[idx]; env_a = np.abs(d[idx])
alpha_env = -np.polyfit(env_t, np.log(env_a), 1)[0] if len(env_t) > 3 else float("nan")

def harm(x, w):
    M = np.column_stack([np.sin(w*t), np.cos(w*t), np.sin(2*w*t), np.cos(2*w*t), np.ones_like(t)]); c, *_ = np.linalg.lstsq(M, x, rcond=None)
    return dict(amp_w=math.hypot(c[0], c[1]), amp_2w=math.hypot(c[2], c[3]), mean=c[4], resid_rms=float((x - M @ c).std()))
wfit = AR.fit_damped(t_p, d, 0, 4*T, omega_ref)["omega"]
iT = [int(np.argmin(abs(t - k*T))) for k in range(5)]
out = dict(run=run, tag=tag, omega_ref=omega_ref, T=T, nrf=nrf, rho_f=RHO_F, K=K,
           windows=windows(), alpha_envelope=alpha_env, n_envelope_peaks=len(env_t),
           energy=dict(E0=float(Etot[0]), KEr0=float(KEr[0]), PEr0=float(PEr[0]), KEf0=float(KEf[0]), PEc0=float(PEc[0]),
                       Etot_over_E0_at_kT=[float(Etot[i]/Etot[0]) for i in iT], E_max_over_E0=float(Etot.max()/Etot[0]), E_min_over_E0=float(Etot.min()/Etot[0]),
                       Wdiss_total=float(Wdiss[-1]), Wdiss_over_E0=float(Wdiss[-1]/Etot[0]),
                       Etot_plus_Wdiss_over_E0_at_end=float((Etot[-1]+Wdiss[-1])/Etot[0]),
                       KEf_over_KEr_t0=float(KEf[0]/KEr[0]), KEf_lumped_over_consistent_t0=float(KEf_lumped[0]/KEf[0]), PEc_max_over_E0=float(PEc.max()/Etot[0]),
                       mesh_regulariser_energy_bound=float(0.5*EMESH*(2*np.max(np.abs(Fn[:, :, 0:2])) / 0.01)**2*Vel.sum())),
           pressure=dict(n0_layer0=harm(n0, wfit), n2_layer0=harm(n2, wfit), pmean_all=harm(pmean_all, wfit),
                         Jmean=harm(Jmean, wfit), Jmean_max=float(np.abs(Jmean).max()),
                         pmean_over_K_vs_Jmean_corr=float(np.corrcoef(pmean_all, -K*Jmean)[0, 1]) if np.std(Jmean) > 0 else None,
                         dA_interface_harm=harm(dA_if, wfit),
                         n0_radial_rms=[float(x) for x in np.sqrt(((n0_layers - n0_layers.mean(0))**2).mean(0))],
                         n0_radial_mean_offset=[float(x) for x in n0_layers.mean(0)]),
           )
json.dump(out, open(out_json, "w"), indent=1)
if out_npz:
    np.savez_compressed(out_npz, t=t, KEr=KEr, PEr=PEr, KEf=KEf, PEc=PEc, Diss=Diss, Wdiss=Wdiss, Etot=Etot, n0=n0, n2=n2,
                        pmean_all=pmean_all, Jmean=Jmean, dA_if=dA_if, n0_layers=n0_layers, KEf_lumped=KEf_lumped, t_p=t_p, d=d)
print(json.dumps({k: out[k] for k in ("tag", "windows", "alpha_envelope")}, indent=1)[:1500])
print(json.dumps(out["energy"], indent=1))
