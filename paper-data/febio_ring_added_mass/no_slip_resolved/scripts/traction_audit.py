#!/usr/bin/env python3
"""Interface traction and interface-work audit for a ringAddedMass run logged with --log-stress.
usage: traction_audit.py <run_dir> <out_json> [<out_npz>]
Reproduces, from logged data only, the load that `fluid-FSI traction` applies to the ring (FEFluidFSITraction.cpp:149-181):
  f = gt*p - sv*gt   (gt = outward-from-fluid area normal; p from the NODAL dilatation interpolated on the surface, p = -K e;
  sv = element-mean viscous stress of the attached fluid element).
Time level: midpoint of consecutive logged steps (alpha_f = 0.5 at rhoi = 1).
Outputs: pressure and viscous traction (total force, n=2 harmonics), interface power sum f.du/dt vs the ring energy change
(solid-side check), fluid-side energy change plus dissipation (from forensic_energy.py arrays if available), and an analytic thin-Stokes-layer
estimate of the n=2 shear amplitude. No claim is made beyond what is computed."""
import sys, json, math
import numpy as np
import xml.etree.ElementTree as ET
sys.path.insert(0, "<project-root>/tools")
import analyze_ring as AR
import make_ring_feb as M

run = sys.argv[1].rstrip("/"); out_json = sys.argv[2]; out_npz = sys.argv[3] if len(sys.argv) > 3 else None
meta = json.load(open(run + "/model_meta.json")); tag = meta["tag"]; nrs, nt, nrf = meta["dims_nrs_nt_nrf"]
K = meta["k"]; RHO_F = meta["rho_f"]; MU = RHO_F * 1e-7; omega = meta["omega_ref"]; Ro = 1.05; H = 0.1
root = ET.parse(f"{run}/{tag}.feb").getroot()
X = {int(n.get("id")): np.array([float(v) for v in n.text.split(",")]) for n in root.find("Mesh/Nodes")}
ring_ids = sorted({int(v) for el in root.findall("Mesh/Elements") if el.get("name") == "Ring" for e in el for v in e.text.split(",")})
iface = sorted([n for n in ring_ids if abs(math.hypot(X[n][0], X[n][1]) - Ro) < 1e-9], key=lambda n: (round(math.atan2(X[n][1], X[n][0]), 9), X[n][2]))
# faces: nodes (j,k0),(j+1,k0),(j+1,k1),(j,k1)
byj = {}
for n in iface: byj.setdefault(round(math.atan2(X[n][1], X[n][0]), 9), {})[round(X[n][2], 9)] = n
ths = sorted(byj); assert len(ths) == nt + 1
faces = [(byj[ths[j]][0.0], byj[ths[j + 1]][0.0], byj[ths[j + 1]][H], byj[ths[j]][H]) for j in range(nt)]
fl_first = min(int(e.get("id")) for el in root.findall("Mesh/Elements") if el.get("name") == "Fluid" for e in el)
face_elem = [fl_first + j * nrf for j in range(nt)]            # layer-0 fluid element of face j (j outer, radial inner)

rb = AR.read_blocks(run + "/ring_nodes.txt"); eb = AR.read_blocks(run + "/fluid_ef.txt"); sb = AR.read_blocks(run + "/fluid_stress.txt"); pb = AR.read_blocks(run + "/fluid_elems.txt")
t = np.array([b["t"] for b in rb]); nT = len(t)
def tab(blocks, ids, c):
    out = np.zeros((len(blocks), len(ids), c)); pos = None
    for k, b in enumerate(blocks):
        r = np.array(b["rows"]); o = {int(x): i for i, x in enumerate(r[:, 0])}
        if pos is None: pos = [o[n] for n in ids]
        out[k] = r[pos, 1:1 + c]
    return out
R = tab(rb, iface, 4)                                           # ux uy vx vy
EF = tab(eb, iface, 1)[:, :, 0]
S = tab(sb, face_elem, 6); P = tab(pb, face_elem, 2)            # fsxx fsyy fsxy fdxx fdyy fdxy | fp fJ
ipos = {n: i for i, n in enumerate(iface)}
x0 = np.array([X[n] for n in iface])
gp = [(-1 / math.sqrt(3), -1 / math.sqrt(3)), (1 / math.sqrt(3), -1 / math.sqrt(3)), (1 / math.sqrt(3), 1 / math.sqrt(3)), (-1 / math.sqrt(3), 1 / math.sqrt(3))]
def Hq(a, b): return 0.25 * np.array([(1 - a) * (1 - b), (1 + a) * (1 - b), (1 + a) * (1 + b), (1 - a) * (1 + b)])
def dHq(a, b): return 0.25 * np.array([[-(1 - b), -(1 - a)], [(1 - b), -(1 + a)], [(1 + b), (1 + a)], [-(1 + b), (1 - a)]])

nf = len(faces)
Fp = np.zeros((nT - 1, len(iface), 2)); Fv = np.zeros_like(Fp)       # nodal forces on the ring: pressure part, viscous part (per slab)
face_pn = np.zeros((nT - 1, nf)); face_tn = np.zeros((nT - 1, nf)); face_tt = np.zeros((nT - 1, nf)); face_area = np.zeros(nf)
for k in range(nT - 1):
    um = 0.5 * (R[k, :, 0:2] + R[k + 1, :, 0:2]); em = 0.5 * (EF[k] + EF[k + 1]); sm = 0.5 * (S[k] + S[k + 1]); pm = 0.5 * (P[k, :, 0] + P[k + 1, :, 0])
    for j, f in enumerate(faces):
        idx = [ipos[n] for n in f]; xy = x0[idx][:, :2] + um[idx]; z = x0[idx][:, 2]
        pos3 = np.column_stack([xy, z]); area = 0.0; pn = 0.0; tn = 0.0; tt = 0.0
        sv = np.array([[sm[j, 0] + pm[j], sm[j, 2]], [sm[j, 2], sm[j, 1] + pm[j]]])   # sigma = -p I + sv, so sv_xx = fsxx + p
        for (a, b) in gp:
            h = Hq(a, b); dh = dHq(a, b); gr = dh[:, 0] @ pos3; gs = dh[:, 1] @ pos3; n3 = np.cross(gr, gs)
            rc = h @ pos3; nr = n3[:2] if np.dot(n3[:2], rc[:2]) > 0 else -n3[:2]    # outward from the ring (into the fluid), length = area element
            dA = np.linalg.norm(n3); e_n = nr / (np.linalg.norm(nr) + 1e-300); p_gp = -K * (h @ em[idx])
            fp_ = -p_gp * nr; fv_ = sv @ nr                                       # force on the ring: -p n_r + sv n_r (n_r outward from the ring)
            for a_i, hh in enumerate(h): Fp[k, idx[a_i]] += hh * fp_; Fv[k, idx[a_i]] += hh * fv_
            e_t = np.array([-e_n[1], e_n[0]]); area += dA; pn += dA * (-p_gp); tn += dA * (e_t @ fv_ / (np.linalg.norm(nr) + 1e-300) * 1.0); tt += dA * (e_n @ fv_ / (np.linalg.norm(nr) + 1e-300))
        face_area[j] = area; face_pn[k, j] = pn / area; face_tn[k, j] = tn / area; face_tt[k, j] = tt / area
# face_pn: pressure traction on the ring, outward-normal component; face_tn: viscous traction tangential (e_theta); face_tt: viscous normal component
# --- power and work on the ring
dU = R[1:, :, 0:2] - R[:-1, :, 0:2]
dWp = (Fp * dU).sum((1, 2)); dWv = (Fv * dU).sum((1, 2)); dW = dWp + dWv
Wp = np.concatenate([[0], np.cumsum(dWp)]); Wv = np.concatenate([[0], np.cumsum(dWv)]); Wtr = Wp + Wv
# --- harmonics of face tractions (quarter model: weight by angle)
thc = np.array([0.5 * (ths[j] + ths[j + 1]) for j in range(nt)]); dth = ths[1] - ths[0]
def amp(x, basis):   # x: (time, faces)
    c = (x * basis[None, :]).sum(1) * dth / (math.pi / 4)
    M_ = np.column_stack([np.sin(omega * t[:-1]), np.cos(omega * t[:-1]), np.ones(nT - 1)]); cc, *_ = np.linalg.lstsq(M_, c, rcond=None)
    return float(math.hypot(cc[0], cc[1])), float(np.abs(c).max())
pn_amp = amp(face_pn, np.cos(2 * thc)); tn_amp = amp(face_tn, np.sin(2 * thc)); tt_amp = amp(face_tt, np.cos(2 * thc))
# --- analytic thin-Stokes-layer shear estimate: need tangential mismatch between potential flow and ring motion
A_, Bc = M.mode_expressions(1.5e-3, 1.5, Ro)[2]
qpot = (A_ * Ro + Bc / Ro**3) / (A_ * Ro - Bc / Ro**3)             # v_t^pot = -qpot * a sin2t when v_r = a cos2t
vx = R[:, :, 2]; vy = R[:, :, 3]; th_n = np.arctan2(x0[:, 1], x0[:, 0])
vr_n = vx * np.cos(th_n) + vy * np.sin(th_n); vt_n = -vx * np.sin(th_n) + vy * np.cos(th_n)
sel0 = [i for i, n in enumerate(iface) if abs(X[n][2]) < 1e-12]; o = np.argsort(th_n[sel0]); s0 = np.array(sel0)[o]
a_t = np.array([np.polyfit(np.cos(2 * th_n[s0]), vr_n[k, s0], 1)[0] for k in range(nT)])
b_t = np.array([np.polyfit(np.sin(2 * th_n[s0]), vt_n[k, s0], 1)[0] for k in range(nT)])
delta_t = -qpot * a_t - b_t                                       # coefficient of sin2t in (v_t^pot - v_t^ring)
Mfit = np.column_stack([np.sin(omega * t), np.cos(omega * t), np.ones(nT)]); cd, *_ = np.linalg.lstsq(Mfit, delta_t, rcond=None); d_amp = math.hypot(cd[0], cd[1])
ca, *_ = np.linalg.lstsq(Mfit, a_t, rcond=None); a_amp = math.hypot(ca[0], ca[1])
delta_sl = math.sqrt(2 * 1e-7 / omega)
tau_est = math.sqrt(2) * MU * d_amp / delta_sl
res = dict(run=run, tag=tag, n_faces=nf, qpot=qpot, omega=omega, stokes_layer=delta_sl,
           pressure_traction_n2_amp_Pa=pn_amp[0], viscous_tangential_traction_n2_amp_Pa=tn_amp[0], viscous_normal_traction_n2_amp_Pa=tt_amp[0],
           viscous_over_pressure=tn_amp[0] / pn_amp[0], interface_radial_velocity_amp=a_amp, mismatch_tangential_velocity_amp=d_amp,
           thin_layer_shear_estimate_Pa=tau_est, measured_over_estimate=tn_amp[0] / tau_est,
           work=dict(W_pressure_end=float(Wp[-1]), W_viscous_end=float(Wv[-1]), W_total_end=float(Wtr[-1]), W_abs_max=float(np.abs(Wtr).max()),
                     W_viscous_over_pressure_peak=float(np.abs(Wv).max() / max(np.abs(Wp).max(), 1e-300))))
if out_npz:
    np.savez_compressed(out_npz, t=t, Wp=Wp, Wv=Wv, Wtr=Wtr, face_pn=face_pn, face_tn=face_tn, face_tt=face_tt, thc=thc, d_t=delta_t, a_t=a_t, b_t=b_t)
json.dump(res, open(out_json, "w"), indent=1); print(json.dumps(res, indent=1))
