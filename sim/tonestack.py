"""Linear AC model of the SLO-100 tone stack (Marshall/JCM800 topology, 47k slope)
and of impedance-scaled variants built from ALPS RK168 motorized pot values.

Topology (from R. Robinette's annotated SLO-100 schematic v1.6f):
  src --Rs-- S
  S --C1(treble)-- T ;  S --Rslope-- A
  A --Cb(bass)-- B   ;  A --Cm(mid)-- Mw (mid pot wiper)
  treble pot: T --(1-t)Rt-- W --t*Rt-- B      (W = output)
  bass pot (rheostat): B --Rb*f(x)-- M
  mid pot: M --(1-m)Rm-- Mw --m*Rm-- 0
  load (both masters in parallel): W --RL-- 0
"""
import os
import itertools
import json
import sys

import numpy as np

NODES = ["S", "T", "W", "B", "A", "M", "Mw"]
IDX = {n: i for i, n in enumerate(NODES)}


def log_taper(x, mid=0.15):
    """Audio taper: fraction of R at rotation x in [0,1]; `mid` = value at x=0.5."""
    s = (1 - mid) / mid  # from 1/(s+1) = mid
    b = s * s
    return (b ** x - 1) / (b - 1)


def response(p, f, t, x, m):
    """Return complex V(W)/Vsrc and Zin at node S for frequencies f."""
    rmin = 1.0
    out, zin = [], []
    for fk in f:
        w = 2 * np.pi * fk
        n = len(NODES)
        Y = np.zeros((n, n), dtype=complex)
        I = np.zeros(n, dtype=complex)

        def add(a, b, y):
            ia = IDX.get(a)
            ib = IDX.get(b)
            if ia is not None:
                Y[ia, ia] += y
            if ib is not None:
                Y[ib, ib] += y
            if ia is not None and ib is not None:
                Y[ia, ib] -= y
                Y[ib, ia] -= y

        def R(a, b, r):
            add(a, b, 1.0 / max(r, rmin))

        def C(a, b, c):
            add(a, b, 1j * w * c)

        # source: Norton equivalent of 1 V behind Rs into S
        add("S", None, 1.0 / p["Rs"])
        I[IDX["S"]] += 1.0 / p["Rs"]
        C("S", "T", p["C1"])
        R("S", "A", p["Rslope"])
        C("A", "B", p["Cb"])
        C("A", "Mw", p["Cm"])
        R("T", "W", (1 - t) * p["Rt"])
        R("W", "B", t * p["Rt"])
        R("B", "M", p["Rb"] * log_taper(x, p.get("bass_mid", 0.15)))
        R("M", "Mw", (1 - m) * p["Rm"])
        R("Mw", None, m * p["Rm"])
        R("W", None, p["RL"])
        V = np.linalg.solve(Y, I)
        out.append(V[IDX["W"]])
        i_src = (1.0 - V[IDX["S"]]) / p["Rs"]
        zin.append(V[IDX["S"]] / i_src)
    return np.array(out), np.array(zin)


ORIGINAL = dict(Rs=650, C1=470e-12, Rslope=47e3, Cb=20e-9, Cm=20e-9,
                Rt=250e3, Rb=1e6, Rm=25e3, RL=500e3)

VARIANTS = {
    # exact /10 scaling (not buildable: 25k treble, 2.5k mid are not ALPS values)
    "x10_ideal": dict(Rs=650, C1=4.7e-9, Rslope=4.7e3, Cb=200e-9, Cm=200e-9,
                      Rt=25e3, Rb=100e3, Rm=2.5e3, RL=50e3),
    # buildable /10: treble 20k lin, bass 100k log, mid = 4 gangs of 10k lin in parallel,
    # masters 2 x 100k log; nearest E-series caps
    "x10_alps": dict(Rs=650, C1=4.7e-9, Rslope=4.7e3, Cb=220e-9, Cm=220e-9,
                     Rt=20e3, Rb=100e3, Rm=2.5e3, RL=50e3),
    # buildable /10 with treble cap retuned for the 20k treble pot
    "x10_alps_c1_5n6": dict(Rs=650, C1=5.6e-9, Rslope=4.7e3, Cb=220e-9, Cm=220e-9,
                            Rt=20e3, Rb=100e3, Rm=2.5e3, RL=50e3),
}


def main():
    f = np.logspace(np.log10(40), np.log10(10e3), 120)
    band = (f >= 60) & (f <= 6000)
    settings = np.linspace(0, 1, 6)  # knob 0,2,4,6,8,10
    ref_cache = {}
    results = {}
    for name, p in VARIANTS.items():
        worst = 0.0
        worst_at = None
        rms_list = []
        for t, x, m in itertools.product(settings, settings, settings):
            key = (t, x, m)
            if key not in ref_cache:
                ref_cache[key] = response(ORIGINAL, f, t, x, m)
            h0, _ = ref_cache[key]
            h1, _ = response(p, f, t, x, m)
            d = 20 * np.log10(np.abs(h1[band]) / np.abs(h0[band]))
            dmax = np.max(np.abs(d))
            rms_list.append(np.sqrt(np.mean(d ** 2)))
            if dmax > worst:
                worst, worst_at = dmax, key
        # input impedance minimum over all settings
        zmin = min(np.min(np.abs(response(p, f, t, x, m)[1]))
                   for t, x, m in itertools.product(settings, settings, settings))
        results[name] = dict(worst_dev_db=round(float(worst), 2),
                             worst_at_knobs=[round(10 * v) for v in worst_at],
                             rms_dev_db=round(float(np.mean(rms_list)), 2),
                             zin_min_ohm=round(float(zmin)))
    zmin0 = min(np.min(np.abs(ref_cache[k][1])) for k in ref_cache)
    results["original"] = dict(zin_min_ohm=round(float(zmin0)))
    json.dump(results, sys.stdout, indent=2)
    print()

    # curves at a few settings for plotting: (treble, bass, mid) knob values
    curves = {}
    for label, (t, x, m) in {"5-5-5": (.5, .5, .5), "10-0-0": (1, 0, 0),
                             "0-10-10": (0, 1, 1), "8-6-3": (.8, .6, .3)}.items():
        h0, _ = response(ORIGINAL, f, t, x, m)
        h1, _ = response(VARIANTS["x10_alps_c1_5n6"], f, t, x, m)
        curves[label] = dict(orig=(20 * np.log10(np.abs(h0))).round(2).tolist(),
                             alps=(20 * np.log10(np.abs(h1))).round(2).tolist())
    json.dump(dict(f=f.round(1).tolist(), curves=curves),
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "curves.json"), "w"))


if __name__ == "__main__":
    main()
