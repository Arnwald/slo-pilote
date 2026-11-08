"""Every switchable mode: small-signal response at the speaker and large-signal levels/THD.

python3 modes_test.py <test> [<test> ...]  -> res_modes_<test>.json
"""
import json
import os
import sys

import numpy as np

import sim

HERE = os.path.dirname(os.path.abspath(__file__))

TESTS = {
    "od_base": (["orig", "mod"], dict()),
    "crunch": (["orig", "mod"], dict(channel="normal", crunch=True, gain_n=0.5)),
    "clean": (["orig", "mod"], dict(channel="normal", crunch=False, gain_n=0.7)),
    "bright_cr": (["orig", "mod"], dict(channel="normal", crunch=True, gain_n=0.5, bright_n=True)),
    "bright_cl": (["orig", "mod"], dict(channel="normal", crunch=False, gain_n=0.7, bright_n=True)),
    "clip10k": (["mod"], dict(clipper="10k")),
    "clip4k4": (["mod"], dict(clipper="4k4")),
    "bypass_red": (["mod"], dict(bypass="reduced")),
    "cc2n2": (["mod"], dict(cc_v2a="2n2")),
    "push": (["mod"], dict(push=True)),
    "extra": (["mod"], dict(extra=True)),
    "tight": (["mod"], dict(bypass="reduced", cc_v2a="2n2", clipper="4k4")),
    "clip4k4_ac": (["mod"], dict(clipper="4k4", clipper_mode="ac")),
    "clip10k_ac": (["mod"], dict(clipper="10k", clipper_mode="ac")),
    "depth_lin50": (["mod"], dict(depth=0.5, depth_net="lin100k")),
}
FREQS = (100.0, 1000.0)
AMPS = (0.05, 0.3)


def large(variant, f, amp, **kw):
    cyc_settle, cyc = (30, 8) if f < 500 else (60, 8)
    tstop = (cyc_settle + cyc) / f
    t, s, dt = sim.tran(variant, tstop, 1 / f / 256, ["sec"], tstart=cyc_settle / f, maxstep=1 / f / 256,
                        vin_spec=f"SIN(0 {amp} {f})", **kw)
    h = sim.spectrum(t, s["sec"], f, cyc, nh=10)
    thd = float(np.sqrt(np.sum(np.square(h[1:]))) / h[0])
    return dict(v1=round(h[0], 3), thd=round(thd, 4), h2=round(h[1] / h[0], 4), h3=round(h[2] / h[0], 4))


def run(name):
    variants, kw = TESTS[name]
    base = dict(gain_od=0.7, master=0.3, master_n=0.3)
    base.update(kw)
    res = dict(test=name, params={k: str(v) for k, v in kw.items()}, ac={}, large={})
    for v in variants:
        f, H = sim.ac(v, "sec", 10, 20e3, 20, **base)
        res["ac"][v] = dict(f=[round(x, 2) for x in f], db=[round(float(20 * np.log10(abs(h))), 3) for h in H])
        res["large"][v] = {}
        for fr in FREQS:
            for a in AMPS:
                res["large"][v][f"{fr:.0f}Hz_{a}V"] = large(v, fr, a, **base)
                print(name, v, fr, a, res["large"][v][f"{fr:.0f}Hz_{a}V"], flush=True)
    json.dump(res, open(os.path.join(HERE, f"res_modes_{name}.json"), "w"))


if __name__ == "__main__":
    for n in sys.argv[1:]:
        run(n)
