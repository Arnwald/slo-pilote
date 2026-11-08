"""V1B (first preamp stage) driving the two gain dividers.

Cases
  orig      : SLO-100 values, dividers 470k (|| 2 nF on OD) + 500k pot, unbuffered
  scaled    : dividers /5 (91k || 10 nF + 100k pot), unbuffered -> heavier load on V1B plate
  buffered  : dividers /5 driven by a DC-coupled 12AX7 cathode follower (Rk 100k)
Gain pots at maximum (wiper at top). Output = OD gain wiper.
"""
import os
import json

import numpy as np

from tubesim import Circuit, thd

BP = 359.0  # B+5
TUBE6 = "12AU7"


def v1b(c, src):
    c.v("bp", lambda t: BP)
    c.r(src, "g1", 68e3)
    c.triode("p1", "g1", "k1", "12AX7")
    c.r("bp", "p1", 220e3)
    c.r("k1", "gnd", 1.8e3)
    c.c("k1", "gnd", 1e-6)


def dividers(c, node, scale):
    rs, pot, cp = 470e3 / scale, 500e3 / scale, 2e-9 * scale
    # OD divider (treble peaker across series R), output at wiper (pot at max: wiper = top)
    c.c(node, "dOD", 0.02e-6 * scale)
    c.r("dOD", "od", rs)
    c.c("dOD", "od", cp)
    c.r("od", "gnd", pot)
    # crunch divider on the clean channel
    c.c(node, "dCL", 0.02e-6 * scale)
    c.r("dCL", "cl", rs)
    c.r("cl", "gnd", pot)


def build(case, amp, f):
    c = Circuit()
    c.v("in", lambda t: amp * np.sin(2 * np.pi * f * t))
    v1b(c, "in")
    g = dict(g1=0, k1=1.5, p1=190, dOD=0, od=0, dCL=0, cl=0)
    if case == "orig":
        dividers(c, "p1", 1)
    elif case == "scaled":
        dividers(c, "p1", 5)
    elif case == "buffered":
        c.triode("bp", "p1", "k6", "12AX7")
        c.r("k6", "gnd", 100e3)
        dividers(c, "k6", 5)
        g["k6"] = 192
    else:  # buffered_ac: AC-coupled CF, grid biased low by a divider -> no grid current
        c.v("bf", lambda t: 404.0)
        c.c("p1", "g6", 0.022e-6)
        c.r("bf", "g6", 1.2e6)
        c.r("g6", "gnd", 1e6)
        c.triode("bf", "g6", "k6", TUBE6)
        c.r("k6", "gnd", 47e3)
        dividers(c, "k6", 5)
        g.update(g6=184, k6=193)
    return c, g


def run(case, amp, f, fs=200e3, cycles=8):
    c, g = build(case, amp, f)
    sig = c.tran(cycles / f, fs, "od", g)
    t, a = thd(sig, fs, f)
    return t, a


if __name__ == "__main__":
    amps = [0.1, 0.3, 0.6, 1.0, 1.5, 2.0]
    res = dict(amps=amps, rows=[])
    for case in ("orig", "buffered_ac"):
        c, g = build(case, 0, 1000)
        v = c.dc(g)
        dcv = {n: round(float(v[c.ix[n]]), 1) for n in c.free if n in ("p1", "k1", "k6", "g6")}
        for f in (100.0, 1000.0):
            th, gain = [], []
            for a in amps:
                t, out = run(case, a, f)
                th.append(round(100 * t, 2))
                gain.append(round(20 * np.log10(out / a), 2))
            res["rows"].append(dict(case=case, f=f, dc=dcv, thd_pct=th, gain_db=gain))
            print(case, f, dcv, "THD", th, "gain", gain, flush=True)
    json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "v1b_buffer.json"), "w"), indent=1)
