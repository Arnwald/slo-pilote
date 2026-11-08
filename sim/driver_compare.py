"""Compare tone-stack drivers into the /10 ALPS stack: 12AU7 CF vs 12AU7 White cathode follower.
Also the original 12AX7 CF into the original stack as reference."""
import json
import sys

import numpy as np

from tubesim import Circuit, add_stack, thd

BPLUS = 378.0
STACK10 = dict(C1=5.6e-9, Rslope=4.7e3, Cb=220e-9, Cm=220e-9, Rt=20e3, Rb=100e3, Rm=2.5e3, RL=50e3)
STACK0 = dict(C1=470e-12, Rslope=47e3, Cb=20e-9, Cm=20e-9, Rt=250e3, Rb=1e6, Rm=25e3, RL=500e3)


def ckt_cf(amp, f, setting, tube="12AU7", rk=22e3, vg=190.0, stack=STACK10):
    c = Circuit()
    c.v("bp", lambda t: BPLUS)
    c.v("g", lambda t: vg + amp * np.sin(2 * np.pi * f * t))
    c.triode("bp", "g", "out", tube)
    c.r("out", "gnd", rk)
    add_stack(c, "out", stack, *setting)
    return c, dict(out=vg + 5, W=0, T=vg, A=vg, B=0, M=0, Mw=0)


def ckt_wcf(amp, f, setting, ra=3.3e3, rk2=1e3, vg=185.0):
    c = Circuit()
    c.v("bp", lambda t: BPLUS)
    c.v("g", lambda t: vg + amp * np.sin(2 * np.pi * f * t))
    # upper triode: plate load ra, cathode = out
    c.r("bp", "p1", ra)
    c.triode("p1", "g", "out", "12AU7")
    # lower triode: plate = out, grid driven from p1, cathode bias rk2 bypassed
    c.c("p1", "g2", 0.47e-6)
    c.r("g2", "gnd", 1e6)
    c.triode("out", "g2", "k2", "12AU7")
    c.r("k2", "gnd", rk2)
    c.c("k2", "gnd", 220e-6)
    add_stack(c, "out", STACK10, *setting)
    return c, dict(p1=350, out=190, g2=0, k2=8, W=0, T=190, A=190, B=0, M=0, Mw=0)


def run(builder, amp, f, setting, **kw):
    fs = 200e3
    c, guess = builder(amp, f, setting, **kw)
    sig = c.tran(8.0 / f, fs, "W", guess)
    return thd(sig, fs, f)


def dcinfo():
    c, g = ckt_wcf(0, 1000, (.5, .5, .5))
    v = c.dc(g)
    d = {n: round(float(v[c.ix[n]]), 1) for n in ("p1", "out", "g2", "k2")}
    d["I_mA"] = round((BPLUS - d["p1"]) / 3.3, 2)
    return d


if __name__ == "__main__":
    print("WCF DC:", dcinfo(), flush=True)
    settings = {"5-5-5": (.5, .5, .5), "10-0-0": (1., 0., 0.)}
    amps = [10, 20, 30, 40]
    rows = []
    cases = [("orig_cf_12AX7", ckt_cf, dict(tube="12AX7", rk=100e3, vg=200.0, stack=STACK0)),
             ("cf_12AU7", ckt_cf, {}),
             ("wcf_12AU7", ckt_wcf, {})]
    for name, b, kw in cases:
        for sname, st in settings.items():
            for f in (100.0, 1000.0):
                th = [round(100 * run(b, a, f, st, **kw)[0], 3) for a in amps]
                rows.append(dict(driver=name, setting=sname, f=f, thd_pct=th))
                print(name, sname, f, th, flush=True)
    json.dump(dict(amps=amps, rows=rows), open("driver_compare.json", "w"), indent=1)
