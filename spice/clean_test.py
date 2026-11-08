import os, subprocess, tempfile
import numpy as np
import slo, run
HERE = os.path.dirname(os.path.abspath(__file__))

def clean(variant, amp, f=1000.0, gain_n=0.5):
    out = tempfile.mktemp(suffix=".dat", dir=HERE)
    an = f""".control
tran {1/f/200:.4g} {60/f:.6g} {50/f:.6g}
wrdata {out} v(sec)
.endc"""
    net = slo.netlist(variant, vin_spec=f"SIN(0 {amp} {f})", analysis=an, master=0.3, gain_n=gain_n)
    net = net.replace(f"Rldr2 o3 jn {slo.LDR_ON}", f"Rldr2 o3 jn {slo.LDR_OFF}")
    net = net.replace(f"Rldr1 g2b 0 {slo.LDR_OFF}", f"Rldr1 g2b 0 {slo.LDR_ON}")
    net = net.replace(f"Rldr3 mw piin {slo.LDR_ON}", f"Rldr3 mw piin {slo.LDR_OFF}")
    net = net.replace(f"Rldr4 mnw piin {slo.LDR_OFF}", f"Rldr4 mnw piin {slo.LDR_ON}")
    cir = tempfile.mktemp(suffix=".cir", dir=HERE)
    open(cir, "w").write(net)
    subprocess.run(["ngspice", "-b", cir], cwd=HERE, capture_output=True, text=True, timeout=600)
    os.remove(cir)
    d = np.loadtxt(out); os.remove(out)
    h, thd = run.harmonics(d[:, 0], d[:, 1], f)
    return h[0], thd

for f in (100.0, 1000.0):
    for a in (0.05, 0.2, 0.6):
        r = [clean(v, a, f) for v in ("orig", "mod")]
        print(f, a, [(round(x, 2), round(100 * y, 1)) for x, y in r], "écart dB", round(20 * np.log10(r[1][0] / r[0][0]), 2), flush=True)
