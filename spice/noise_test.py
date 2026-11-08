"""Thermal + shot noise (equivalent grid resistors 2.5/gm), output at the speaker, orig vs mod.
Tube 1/f noise is not modelled. python3 noise_test.py -> res_noise.json
"""
import json
import os
import re
import subprocess
import tempfile

import numpy as np

import slo

HERE = os.path.dirname(os.path.abspath(__file__))
VFS_RMS = 20.0  # 100 W into 4 ohm


def a_weight(f):
    f2 = f * f
    ra = (12194.0 ** 2 * f2 * f2) / ((f2 + 20.6 ** 2) * np.sqrt((f2 + 107.7 ** 2) * (f2 + 737.9 ** 2)) * (f2 + 12194.0 ** 2))
    return ra * 10 ** (2.0 / 20)


def run(variant, **kw):
    out = tempfile.mktemp(suffix=".dat", dir=HERE)
    an = f""".control
set wr_singlescale
noise v(sec) Vin dec 20 20 20k 1
print all > {out}.tot
setplot noise1
wrdata {out} onoise_spectrum inoise_spectrum
setplot noise2
print all >> {out}.tot
.endc"""
    net = slo.netlist(variant, vin_spec="DC 0 AC 1", analysis=an, noise_req=True, **kw)
    cir = tempfile.mktemp(suffix=".cir", dir=HERE)
    open(cir, "w").write(net)
    r = subprocess.run(["ngspice", "-b", cir], cwd=HERE, capture_output=True, text=True, timeout=1200)
    os.remove(cir)
    d = np.loadtxt(out)
    os.remove(out)
    txt = open(out + ".tot").read() if os.path.exists(out + ".tot") else r.stdout
    if os.path.exists(out + ".tot"):
        os.remove(out + ".tot")
    f, on, inn = d[:, 0], d[:, 1], d[:, 2]
    contrib = {}
    for mm in re.finditer(r"onoise_total_(\S+?)\s*=\s*([-+0-9.eE]+)", txt):
        name = mm.group(1)
        if name.endswith(("_1overf", "_thermal")):
            continue
        contrib[name] = float(mm.group(2))
    lf = np.log(f)
    tot = float(np.sqrt(np.trapezoid(on ** 2 * f, lf)))
    totA = float(np.sqrt(np.trapezoid((on * a_weight(f)) ** 2 * f, lf)))
    itot = float(np.sqrt(np.trapezoid(inn ** 2 * f, lf)))
    top = sorted(contrib.items(), key=lambda kv: -kv[1])[:8]
    return dict(out_uVrms=round(1e6 * tot, 2), out_A_uVrms=round(1e6 * totA, 2),
                snr_dB=round(20 * np.log10(VFS_RMS / tot), 1), snrA_dB=round(20 * np.log10(VFS_RMS / totA), 1),
                in_uVrms=round(1e6 * itot, 3),
                in_density_nV_1k=round(1e9 * float(np.interp(1000, f, inn)), 2),
                top=[(k, round(1e6 * v, 2)) for k, v in top])


if __name__ == "__main__":
    res = {}
    for name, kw in (("od", dict(gain_od=0.7, master=0.3)),
                     ("od_m10", dict(gain_od=0.7, master=1.0)),
                     ("crunch", dict(channel="normal", gain_n=0.5, master_n=0.3)),
                     ("clean", dict(channel="normal", crunch=False, gain_n=0.7, master_n=0.5))):
        for v in ("orig", "mod"):
            res[f"{name}_{v}"] = run(v, **kw)
            print(name, v, res[f"{name}_{v}"], flush=True)
    json.dump(res, open(os.path.join(HERE, "res_noise.json"), "w"), indent=1)
