"""OD path V2A -> (optional extra 12AT7 stage) -> 470k/1M attenuator -> V2B cold clipper.
Measures small-signal gain and THD at the cold-clipper plate vs signal at the V2A grid stopper."""
import os
import json

import numpy as np

from tubesim import Circuit, thd

BP4 = 350.0


def build(extra, amp, f, att_series=150e3, att_shunt=10e3):
    c = Circuit()
    c.v("bp", lambda t: BP4)
    c.v("in", lambda t: amp * np.sin(2 * np.pi * f * t))
    # V2A: OD Preamp 2
    c.r("in", "g2a", 470e3)
    c.triode("p2a", "g2a", "k2a", "12AX7")
    c.r("bp", "p2a", 100e3)
    c.r("k2a", "gnd", 1.8e3)
    c.c("k2a", "gnd", 1e-6)
    node = "p2a"
    g = dict(g2a=0, k2a=1.5, p2a=200)
    if extra:
        # extra stage: attenuator then 12AT7 gain stage (tight bypass)
        c.c(node, "ea", 0.022e-6)
        c.r("ea", "g6b", att_series)
        c.r("g6b", "gnd", att_shunt)
        c.triode("p6b", "g6b", "k6b", "12AT7")
        c.r("bp", "p6b", 100e3)
        c.r("k6b", "gnd", 1.0e3)
        c.c("k6b", "gnd", 0.68e-6)
        node = "p6b"
        g.update(ea=0, g6b=0, k6b=2, p6b=200)
    # coupling + attenuator 470k / 1M into cold clipper V2B
    c.c(node, "a1", 0.02e-6)
    c.r("a1", "g2b", 470e3)
    c.r("g2b", "gnd", 1e6)
    c.triode("p2b", "g2b", "k2b", "12AX7")
    c.r("k2b", "gnd", 39e3)
    c.r("bp", "p2b", 100e3)
    c.c("bp", "p2b", 1e-9)
    g.update(a1=0, g2b=0, k2b=10, p2b=250)
    return c, g


def run(extra, amp, f, fs=200e3, cycles=8):
    c, g = build(extra, amp, f)
    sig = c.tran(cycles / f, fs, "p2b", g)
    return thd(sig, fs, f)


if __name__ == "__main__":
    amps = [0.003, 0.01, 0.03, 0.1, 0.3, 1.0]
    out = dict(amps=amps, rows=[])
    for extra in (False, True):
        c, g = build(extra, 0, 1000)
        v = c.dc(g)
        dcv = {n: round(float(v[c.ix[n]]), 1) for n in c.free if n.startswith(("p", "k"))}
        th, gain = [], []
        for a in amps:
            t, o = run(extra, a, 1000.0)
            th.append(round(100 * t, 2))
            gain.append(round(20 * np.log10(o / a), 1))
        out["rows"].append(dict(extra=extra, dc=dcv, thd_pct=th, gain_db=gain))
        print("extra" if extra else "base", dcv, "THD", th, "gain", gain, flush=True)
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "extra_stage.json"), "w"), indent=1)
