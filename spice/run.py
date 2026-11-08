"""Transient runs of the SLO models with ngspice; harmonic analysis of the speaker voltage."""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

import slo

HERE = os.path.dirname(os.path.abspath(__file__))


def tran(variant, f=1000.0, amp=0.2, cycles_settle=40, cycles_meas=10, probes=("sec",), **kw):
    tstop = (cycles_settle + cycles_meas) / f
    step = 1.0 / f / 200
    out = tempfile.mktemp(suffix=".dat", dir=HERE)
    an = f""".control
set wr_singlescale
tran {step:.4g} {tstop:.6g} {cycles_settle / f:.6g} uic
wrdata {out} {' '.join(f'v({p})' for p in probes)}
.endc"""
    net = slo.netlist(variant, vin_spec=f"SIN(0 {amp} {f})", analysis=an, **kw)
    net = net.replace("tran ", "tran ").replace(" uic", "")
    cir = tempfile.mktemp(suffix=".cir", dir=HERE)
    open(cir, "w").write(net)
    r = subprocess.run(["ngspice", "-b", cir], cwd=HERE, capture_output=True, text=True, timeout=900)
    os.remove(cir)
    if not os.path.exists(out):
        raise RuntimeError(r.stdout[-2000:] + r.stderr[-2000:])
    d = np.loadtxt(out)
    os.remove(out)
    t = d[:, 0]
    sigs = {p: d[:, 1 + i] for i, p in enumerate(probes)}
    return t, sigs


def harmonics(t, y, f, n=9):
    # resample on a uniform grid over an integer number of periods
    T = 1.0 / f
    t0 = t[-1] - 8 * T
    tu = np.linspace(t0, t[-1], 8 * 256, endpoint=False)
    yu = np.interp(tu, t, y)
    yu -= yu.mean()
    sp = np.abs(np.fft.rfft(yu)) * 2 / len(yu)
    h = [sp[8 * k] for k in range(1, n + 1)]
    thd = float(np.sqrt(np.sum(np.square(h[1:]))) / h[0])
    return h, thd


if __name__ == "__main__":
    case = sys.argv[1]
    res = {}
    if case == "od":
        for variant, extra in (("orig", False), ("mod", False), ("mod", True)):
            key = variant + ("+extra" if extra else "")
            res[key] = {}
            for f in (100.0, 1000.0):
                for a in (0.05, 0.2, 0.6):
                    t, s = tran(variant, f, a, extra=extra, gain_od=0.7, master=0.3)
                    h, thd = harmonics(t, s["sec"], f)
                    res[key][f"{f:.0f}Hz_{a}V"] = dict(v1=round(h[0], 3), thd=round(thd, 4),
                                                        hrel=[round(x / h[0], 4) for x in h[1:]])
                    print(key, f, a, round(h[0], 3), round(thd, 3), flush=True)
    json.dump(res, open(os.path.join(HERE, f"res_{case}.json"), "w"), indent=1)
