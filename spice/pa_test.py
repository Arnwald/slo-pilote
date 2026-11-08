import os, subprocess, tempfile, json
import numpy as np
import slo, run
HERE = os.path.dirname(os.path.abspath(__file__))

def pi_drive(variant, amp, f=1000.0):
    out = tempfile.mktemp(suffix=".dat", dir=HERE)
    an = f""".control
tran {1/f/200:.4g} {50/f:.6g} {40/f:.6g}
wrdata {out} v(sec) v(piin)
.endc"""
    net = slo.netlist(variant, vin_spec="0", analysis=an, master=0.0)
    net = "\n".join(l for l in net.split("\n") if not l.startswith("Rldr3"))
    net = net.replace(".end", f"Vpi pis 0 SIN(0 {amp} {f})\nRpis pis piin 1k\n.end")
    cir = tempfile.mktemp(suffix=".cir", dir=HERE)
    open(cir, "w").write(net)
    subprocess.run(["ngspice", "-b", cir], cwd=HERE, capture_output=True, text=True, timeout=600)
    os.remove(cir)
    d = np.loadtxt(out); os.remove(out)
    h, thd = run.harmonics(d[:, 0], d[:, 1], f)
    return h[0], thd

res = {}
for variant in ("orig", "mod"):
    rows = []
    for a in (1, 2, 3, 4, 5, 6, 7, 8, 10, 12):
        v1, thd = pi_drive(variant, a)
        rows.append((a, round(v1, 2), round(v1**2/2/4, 1), round(100*thd, 2)))
        print(variant, rows[-1], flush=True)
    res[variant] = rows
# full chain, OD channel, master at max
for variant in ("orig", "mod"):
    for a in (0.2,):
        t, s = run.tran(variant, 1000.0, a, gain_od=0.7, master=1.0, probes=("sec",))
        y = s["sec"][-2000:]
        p = np.mean(y**2) / 4
        h, thd = run.harmonics(t, s["sec"], 1000.0)
        res[variant + "_od_master_max"] = dict(p_rms_W=round(float(p), 1), v1=round(h[0], 2), thd=round(thd, 3))
        print(variant, "OD master max", res[variant + "_od_master_max"], flush=True)
json.dump(res, open(os.path.join(HERE, "res_pa.json"), "w"), indent=1)
