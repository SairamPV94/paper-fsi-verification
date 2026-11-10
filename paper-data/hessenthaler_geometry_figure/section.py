import numpy as np
tris={};cur=None;buf=[]
for l in open("fluidDomain.stl"):
    if l.startswith("solid"): cur=l.split()[1]; tris[cur]=[]
    elif "vertex" in l:
        buf.append(list(map(float,l.split()[1:])))
        if len(buf)==3: tris[cur].append(buf); buf=[]
segs={}
for k,t in tris.items():
    t=np.array(t)*1e3  # mm
    out=[]
    for tri in t:
        s=tri[:,0]; 
        if s.min()>0 or s.max()<0: continue
        pts=[]
        for i in range(3):
            a,b=tri[i],tri[(i+1)%3]
            if (a[0]>0)!=(b[0]>0):
                w=a[0]/(a[0]-b[0]); pts.append(a+w*(b-a))
        if len(pts)==2: out.append([pts[0][1:],pts[1][1:]])
    segs[k]=np.array(out)
    print(k,len(out))
np.savez("section_x0.npz",**segs)
