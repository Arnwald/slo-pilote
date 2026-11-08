"""Depth (resonance) and presence networks: response from the PI input to the speaker terminals,
on a loudspeaker load (closed-box resonance 90 Hz), for the original and the candidate ALPS versions.

python3 depth_test.py  -> res_depth.json
"""
import json
import os

import numpy as np

import sim

HERE = os.path.dirname(os.path.abspath(__file__))

CASES = [
    ("orig_none", "orig", dict(depth=None)),
    ("orig_d0", "orig", dict(depth=0.0, depth_net="orig")),
    ("orig_d50", "orig", dict(depth=0.5, depth_net="orig")),
    ("orig_d100", "orig", dict(depth=1.0, depth_net="orig")),
    ("mod47_d50", "mod", dict(depth=0.5, depth_net="mod47")),
    ("mod47_d100", "mod", dict(depth=1.0, depth_net="mod47")),
    ("mod4n7_d50", "mod", dict(depth=0.5, depth_net="mod4n7")),
    ("mod4n7_d100", "mod", dict(depth=1.0, depth_net="mod4n7")),
    ("lin100k_d50", "mod", dict(depth=0.5, depth_net="lin100k")),
    ("sc10_d0", "mod", dict(depth=0.0, depth_net="scaled10")),
    ("sc10_d50", "mod", dict(depth=0.5, depth_net="scaled10")),
    ("sc10_d100", "mod", dict(depth=1.0, depth_net="scaled10")),
    # presence sweep at depth 0 (network present, shorted)
    ("orig_p0", "orig", dict(depth=0.0, depth_net="orig", presence=0.0)),
    ("orig_p100", "orig", dict(depth=0.0, depth_net="orig", presence=1.0)),
    ("mod_p0", "mod", dict(depth=0.0, depth_net="mod4n7", presence=0.0)),
    ("mod_p100", "mod", dict(depth=0.0, depth_net="mod4n7", presence=1.0)),
    ("sc10_p0", "mod", dict(depth=0.0, depth_net="scaled10", presence=0.0)),
    ("sc10_p100", "mod", dict(depth=0.0, depth_net="scaled10", presence=1.0)),
]

if __name__ == "__main__":
    res = {}
    for name, v, kw in CASES:
        args = dict(drive_pi=True, load="spk", presence=0.5)
        args.update(kw)
        f, H = sim.ac(v, "sec", 10, 30e3, 24, **args)
        res[name] = dict(f=[round(x, 3) for x in f], db=[round(float(20 * np.log10(abs(h))), 3) for h in H])
        idx = [int(np.argmin(abs(f - x))) for x in (50, 100, 200, 500, 1000, 3000, 6000)]
        print(name, [res[name]["db"][i] for i in idx], flush=True)
    # sweep of the depth knob, gain at 100 Hz relative to depth 0
    sweep = {}
    for net, v in (("orig", "orig"), ("mod4n7", "mod"), ("lin100k", "mod"), ("scaled10", "mod")):
        sweep[net] = []
        for d in np.linspace(0, 1, 11):
            f, H = sim.ac(v, "sec", 40, 400, 20, drive_pi=True, load="spk", presence=0.5, depth=float(d), depth_net=net)
            i = int(np.argmin(abs(f - 100)))
            sweep[net].append(round(float(20 * np.log10(abs(H[i]))), 3))
        print(net, sweep[net], flush=True)
    res["sweep100Hz"] = sweep
    json.dump(res, open(os.path.join(HERE, "res_depth.json"), "w"))
