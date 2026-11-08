"""NFB loop gain with the depth network in place: the loop is broken at the 4 ohm tap side of the
depth network (driven by a test source), T = -v(sec)/v(tst). python3 loop2.py -> res_loop2.json"""
import json
import os
import subprocess
import tempfile

import numpy as np

import slo

HERE = os.path.dirname(os.path.abspath(__file__))


def loop(variant, presence, depth, depth_net, load):
    out = tempfile.mktemp(suffix=".dat", dir=HERE)
    an = f""".control
set wr_singlescale
ac dec 40 2 2Meg
wrdata {out} vr(sec) vi(sec)
.endc"""
    kw = dict(master=0.3, presence=presence, depth=depth, depth_net=depth_net)
    if load == "spk":
        kw["load"] = "spk"
    elif load == "open":
        kw["rload"] = 1e6
    net = slo.netlist(variant, vin_spec="0", analysis=an, **kw)
    net = net.replace("Rdep sec nd", "Rdep tst nd").replace("Cdep sec nd", "Cdep tst nd")
    net = net.replace(".end", "Vtst tst 0 DC 0 AC 1\n.end")
    cir = tempfile.mktemp(suffix=".cir", dir=HERE)
    open(cir, "w").write(net)
    subprocess.run(["ngspice", "-b", cir], cwd=HERE, capture_output=True, text=True, timeout=300)
    os.remove(cir)
    d = np.loadtxt(out)
    os.remove(out)
    f = d[:, 0]
    T = -(d[:, 1] + 1j * d[:, 2])
    mag = 20 * np.log10(np.abs(T))
    i0 = int(np.argmin(np.abs(f - 1000.0)))
    ph = np.degrees(np.angle(T))
    up = np.degrees(np.unwrap(np.radians(ph[i0:])))
    dn = np.degrees(np.unwrap(np.radians(ph[:i0 + 1][::-1])))[::-1]
    ph = np.concatenate([dn[:-1], up])
    ph -= 360 * np.round(ph[i0] / 360)
    res = dict(T_1k_dB=round(float(mag[i0]), 1), T_100_dB=round(float(np.interp(100, f, mag)), 1))
    for side, idx in (("HF", range(i0, len(f))), ("LF", range(i0, -1, -1))):
        pm = gm = fc = None
        for j in idx:
            if fc is None and mag[j] < 0:
                fc = f[j]
                pm = 180 - abs(ph[j])
            if gm is None and abs(ph[j]) >= 180:
                gm = -mag[j]
        res[side] = dict(f_c=None if fc is None else round(float(fc)),
                         PM=None if pm is None else round(float(pm), 1),
                         GM=None if gm is None else round(float(gm), 1))
    return res


if __name__ == "__main__":
    allres = {}
    for variant, net, depths in (("orig", "orig", (0.0, 1.0)), ("mod", "lin100k", (0.0, 0.5, 1.0))):
        for d in depths:
            for pres in (0.0, 1.0):
                for load in ("r", "spk", "open"):
                    key = f"{variant}_d{d}_p{pres}_{load}"
                    allres[key] = loop(variant, pres, d, net, load)
                    print(key, allres[key], flush=True)
    json.dump(allres, open(os.path.join(HERE, "res_loop2.json"), "w"), indent=1)
