"""Stepped versions of the pedal controls: resistor strings tapped by ADG406 / ADG408 multiplexers.

Each pot of the TS808 and HM-2 becomes a string of 1 % resistors whose taps go to the inputs of a
16:1 multiplexer (ADG406, +/-15 V, 50 ohm typical on-resistance, 80 ohm max); the multiplexer output
takes the place of the wiper. The gate release uses an 8:1 ADG408. Taps are chosen for even steps
in dB of the quantity the control acts on, then rounded to E96 increments, and the result is
re-simulated with the multiplexer on-resistance in the wiper:

  - TS drive (rheostat, 0 to 500k): gain of the clipping stage above 720 Hz, 1 + (51k + R) / 4.7k;
  - TS tone (20k pot): response of the tone stage at 4 kHz relative to 200 Hz;
  - HM-2 Dist (250k pot, wiper grounded): small-signal gain to the clipping op-amp output at 750 Hz;
  - HM-2 Color Mix L and H (10k pots): equaliser gain at 84 Hz and at the H peak, 15 taps so that the
    middle one is flat;
  - gate release (rheostat in series with 47k, 220 nF): time constant from 10 to 450 ms, 8 taps.

python3 steps.py   ->  tables printed, taps written to steps.json (read by kicad/slo_sch.py)
"""
import json
import os

import numpy as np

import hm2
import ts

HERE = os.path.dirname(os.path.abspath(__file__))
RON = 50.0                       # ADG406 typical at +/-15 V
R8 = 169.0                       # TS tone wiper resistor, 220 ohm less the on-resistance
R49 = 100.0                      # HM-2 resistor to the Dist pot, 150 ohm less the on-resistance
E96 = np.array([1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30, 1.33, 1.37, 1.40, 1.43,
                1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10,
                2.15, 2.21, 2.26, 2.32, 2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
                3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12, 4.22, 4.32, 4.42, 4.53,
                4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49, 5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65,
                6.81, 6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76])


def e96(x):
    d = 10 ** np.floor(np.log10(x))
    v = E96 * d
    v = np.concatenate([v, [10 * d]])
    return float(v[np.argmin(abs(np.log(v / x)))])


def string(cum):
    """Cumulative tap resistances (first tap = 0) -> E96 increments and the cumulative values they give."""
    inc = [e96(b - a) for a, b in zip(cum[:-1], cum[1:])]
    return inc, np.concatenate([[0.0], np.cumsum(inc)])


def invert(xs, ys, targets):
    """Positions where a monotonic curve y(x), sampled finely, reaches each target."""
    order = np.argsort(ys)
    return np.interp(targets, ys[order], xs[order])


def db(h):
    return 20 * np.log10(abs(h))


def at(f, h, f0):
    return db(h[np.argmin(abs(f - f0))])


# ---- TS drive: analytic gain of the clipping stage above the 720 Hz corner --------------------------
def ts_drive():
    g = lambda r: 20 * np.log10(1 + (51e3 + r) / 4.7e3)
    targets = np.linspace(g(0), g(500e3), 16)
    cum = 4.7e3 * (10 ** (targets / 20) - 1) - 51e3
    cum[0] = 0
    inc, real = string(cum)
    return dict(name="TS Drive", unit="dB de gain", inc=inc, cum=list(real), target=list(targets),
                got=[g(r + RON) for r in real])


# ---- TS tone: tone stage alone, 4 kHz vs 200 Hz ---------------------------------------------------
def ts_tone_metric(x=None, rpair=None, ron=0.0, r8=220.0):
    kw = dict(stage="tone", ron=ron, r8=r8)
    if rpair is None:
        kw["tone"] = x
    else:                                 # explicit halves: Rtp1 (ta-tw) and Rtp2 (tw-tn)
        kw["tone"] = rpair[1] / (rpair[0] + rpair[1])
    f, h = ts.ac("o2", **kw)
    return at(f, h, 4000) - at(f, h, 200)


def ts_tone():
    g = np.geomspace(1e-4, 0.5, 60)
    xs = np.concatenate([[0.0], g, 1 - g[::-1][1:], [1.0]])
    ys = np.array([ts_tone_metric(x) for x in xs])
    targets = np.linspace(ys[0], ys[-1], 16)
    pos = invert(xs, ys, targets)
    cum = 20e3 * pos                     # distance from lug 1 (TS_TN side), tone = x
    cum[0] = 0
    inc, real = string(cum)
    tot = real[-1]
    got = [ts_tone_metric(rpair=(tot - c, c), ron=RON, r8=R8) for c in real]
    return dict(name="TS Tone", unit="dB à 4 kHz / 200 Hz", inc=inc, cum=list(real), target=list(targets), got=got,
                ref=list(ys[[0, -1]]))


# ---- HM-2 Dist: small-signal gain to o1b at 750 Hz ------------------------------------------------
def hm_dist_metric(**kw):
    f, h = hm2.ac("o1b", fstart=500, fstop=1000, **kw)
    return at(f, h, 750)


def hm_dist():
    xs = np.concatenate([[0.0], np.geomspace(1e-5, 1, 120)])
    ys = np.array([hm_dist_metric(dist=x) for x in xs])
    targets = np.linspace(ys.min(), ys.max(), 16)
    pos = invert(xs, ys, targets)
    cum = 250e3 * pos
    cum[0] = 0
    inc, real = string(cum)
    tot = real[-1]
    got = [hm_dist_metric(rpots={"dist": (c, tot - c)}, ron=RON, r49=R49) for c in real]
    spread = [[hm_dist_metric(rpots={"dist": (c, tot - c)}, ron=ron, r49=R49) for c in real] for ron in (30.0, 80.0)]
    return dict(name="HM-2 Dist", unit="dB de gain à 750 Hz", inc=inc, cum=list(real), target=list(targets), got=got,
                ref=[float(ys.min()), float(ys.max())], spread=spread)


# ---- HM-2 Color Mix ---------------------------------------------------------------------------------
def eq_metric(which, **kw):
    f, h = hm2.ac("o3a", inject="eq", fstart=40, fstop=4000, **kw)
    if which == "low":
        return at(f, h, 84)
    sel = (f > 700) & (f < 1800)
    g = db(h[sel])
    return g[np.argmax(abs(g))]          # largest boost or cut around the two H gyrators


def hm_eq(which):
    other = "high" if which == "low" else "low"
    xs = np.linspace(0, 1, 41)
    ys = np.array([eq_metric(which, **{which: x, other: 0.5}) for x in xs])
    targets = np.linspace(ys.min(), ys.max(), 15)
    targets[7] = 0.0
    pos = invert(xs, ys, targets)
    cum = 10e3 * pos
    cum[0] = 0
    inc, real = string(cum)
    tot = real[-1]
    comp = dict(ron=RON, rgyr=270.0, kb=330 / 270)
    got = [eq_metric(which, rpots={which: (c, tot - c), other: (5e3, 5e3)}, **comp) for c in real]
    return dict(name=f"HM-2 Color Mix {'L' if which == 'low' else 'H'}",
                unit="dB à 84 Hz" if which == "low" else "dB au pic de 0,95 à 1,3 kHz",
                inc=inc, cum=list(real), target=list(targets), got=got, ref=[float(ys.min()), float(ys.max())])


# ---- gate release -------------------------------------------------------------------------------------
def release():
    taus = np.geomspace(0.22e-6 * 47e3, 0.45, 8)
    cum = taus / 0.22e-6 - 47e3
    cum[0] = 0
    inc, real = string(cum)
    return dict(name="Fermeture du gate", unit="ms", inc=inc, cum=list(real), target=list(taus * 1e3),
                got=[0.22e-6 * (47e3 + r + RON) * 1e3 for r in real])


if __name__ == "__main__":
    out = {}
    for key, fn in (("ts_drive", ts_drive), ("ts_tone", ts_tone), ("hm_dist", hm_dist),
                    ("hm_low", lambda: hm_eq("low")), ("hm_high", lambda: hm_eq("high")), ("release", release)):
        r = fn()
        out[key] = r
        err = np.array(r["got"]) - np.array(r["target"])
        print(f"\n{r['name']} ({r['unit']}), {len(r['cum'])} positions, total {r['cum'][-1] / 1e3:.2f} k")
        if "ref" in r:
            print(f"  potentiomètre d'origine : {r['ref'][0]:+.2f} à {r['ref'][1]:+.2f}")
        print("  pos  cumul (Ω)   visé    obtenu")
        for k, (c, t, g) in enumerate(zip(r["cum"], r["target"], r["got"])):
            print(f"  {k:3d} {c:10.0f} {t:+8.2f} {g:+8.2f}")
        print("  incréments E96 :", ", ".join(f"{v:g}" for v in r["inc"]))
        print(f"  écart max {abs(err).max():.2f}")
        if "spread" in r:
            print("  avec 30 et 80 Ω :", ", ".join(f"{a:+.1f}/{b:+.1f}" for a, b in zip(*r["spread"])))
    json.dump(out, open(os.path.join(HERE, "steps.json"), "w"), indent=1)
