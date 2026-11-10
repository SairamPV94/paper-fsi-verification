"""Compare two mdpa files by geometry: element and condition connectivity as coordinate tuples
(conditions keep their direction, elements their cyclic order), SubModelPart node sets.
Usage: python compare_mdpa.py a.mdpa b.mdpa"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mdpa_inspect import read_mdpa

def entities(path, nodes):
    out, cur, smp_ent, stack, sec = {}, None, {}, [], None
    for raw in open(path):
        line = raw.split("//")[0].strip()
        if not line:
            continue
        w = line.split()
        if w[0] == "Begin" and w[1] in ("Elements", "Conditions"):
            cur = (w[1], w[2]); out.setdefault(cur, {}); continue
        if w[0] == "End" and w[1] in ("Elements", "Conditions"):
            cur = None; continue
        if w[0] == "Begin" and w[1] == "SubModelPart":
            stack.append(w[2]); continue
        if w[0] == "End" and w[1] == "SubModelPart":
            stack.pop(); continue
        if w[0] == "Begin" and w[1] in ("SubModelPartElements", "SubModelPartConditions"):
            sec = w[1]; continue
        if w[0] == "End":
            sec = None; continue
        if cur:
            pts = [tuple(round(c, 9) for c in nodes[int(v)][:2]) for v in w[2:]]
            k = pts.index(min(pts))
            out[cur][int(w[0])] = (int(w[1]), tuple(pts[k:] + pts[:k]) if len(pts) > 2 else tuple(pts))
        elif sec and stack:
            smp_ent.setdefault((stack[-1], sec), set()).add(int(w[0]))
    return out, smp_ent

def canon(path):
    nodes, _, smp = read_mdpa(path)
    ent, smp_ent = entities(path, nodes)
    blocks = {k: sorted(v.values()) for k, v in ent.items()}
    allent = {}
    for (kind, _), v in ent.items():
        for i, g in v.items():
            allent[(kind[:-1], i)] = g
    smpe = {k: sorted(allent[(("Element" if s == "SubModelPartElements" else "Condition"), i)]
                      for i in v) for (k, s), v in smp_ent.items() for _ in [0]}
    smpn = {k: sorted(tuple(round(c, 9) for c in nodes[i][:2]) for i in v) for k, v in smp.items()}
    return blocks, smpe, smpn

a, b = canon(sys.argv[1]), canon(sys.argv[2])
ok = True
for label, x, y in (("blocks", a[0], b[0]), ("smp entities", a[1], b[1]), ("smp nodes", a[2], b[2])):
    for k in sorted(set(x) | set(y), key=str):
        same = x.get(k) == y.get(k)
        ok &= same
        print(f"{label:13s} {str(k):60s} {'same' if same else 'DIFFERENT'} ({len(x.get(k, []))} vs {len(y.get(k, []))})")
print("IDENTICAL GEOMETRY" if ok else "DIFFERENCES FOUND")
