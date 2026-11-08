"""Nonlinear transient simulation: cathode follower driving the tone stack.

Compares
  - original SLO-100: 12AX7 CF, Rk = 100k, original stack (250k/1M/25k, 47k slope, load 500k)
  - pilotable version: 12AU7 CF, Rk = 22k, stack /10 with ALPS values (load 50k)
Koren triode model; trapezoidal integration; Newton on the nonlinear cathode current.
Output: THD at the treble wiper vs input amplitude, for several frequencies and stack settings.
"""
import os
import json
import sys

import numpy as np

KOREN = {
    "12AX7": dict(mu=100.0, ex=1.4, kg1=1060.0, kp=600.0, kvb=300.0),
    "12AU7": dict(mu=21.5, ex=1.3, kg1=1180.0, kp=84.0, kvb=300.0),
}


def ip_koren(vgk, vpk, t):
    vpk = max(vpk, 1e-3)
    arg = t["kp"] * (1.0 / t["mu"] + vgk / np.sqrt(t["kvb"] + vpk * vpk))
    e1 = vpk / t["kp"] * np.logaddexp(0.0, arg)
    return 2.0 * e1 ** t["ex"] / t["kg1"] if e1 > 0 else 0.0


def log_taper(x, mid=0.15):
    s = (1 - mid) / mid
    b = s * s
    return (b ** x - 1) / (b - 1)


# unknown nodes (cathode = stack input S)
N = ["K", "T", "W", "B", "A", "M", "Mw"]
IX = {n: i for i, n in enumerate(N)}


def build(p, t, x, m):
    res, caps = [], []
    res += [("K", None, p["Rk"]), ("T", "W", (1 - t) * p["Rt"]), ("W", "B", t * p["Rt"]),
            ("B", "M", p["Rb"] * log_taper(x)), ("M", "Mw", (1 - m) * p["Rm"]),
            ("Mw", None, m * p["Rm"]), ("W", None, p["RL"]), ("K", "A", p["Rslope"])]
    caps += [("K", "T", p["C1"]), ("A", "B", p["Cb"]), ("A", "Mw", p["Cm"])]
    return [(a, b, max(r, 1.0)) for a, b, r in res], caps


def stamp(Y, a, b, y):
    ia, ib = IX.get(a), IX.get(b)
    if ia is not None:
        Y[ia, ia] += y
    if ib is not None:
        Y[ib, ib] += y
    if ia is not None and ib is not None:
        Y[ia, ib] -= y
        Y[ib, ia] -= y


def simulate(p, tube, vg_dc, amp, freq, t_set, x_set, m_set, fs=200e3, cycles=8):
    res, caps = build(p, t_set, x_set, m_set)
    n = len(N)
    G = np.zeros((n, n))
    for a, b, r in res:
        stamp(G, a, b, 1.0 / r)
    tb = KOREN[tube]
    bplus = p["Bplus"]
    ik = IX["K"]

    def solve(Ylin, Ieq, vg, v0):
        v = v0.copy()
        for _ in range(50):
            vk = v[ik]
            i0 = ip_koren(vg - vk, bplus - vk, tb)
            dv = 1e-4
            i1 = ip_koren(vg - vk - dv, bplus - vk - dv, tb)
            gk = -(i1 - i0) / dv  # d(Ip)/dVk (negative of slope), >= 0
            J = Ylin.copy()
            J[ik, ik] += gk
            rhs = Ieq.copy()
            rhs[ik] += i0 + gk * vk
            vn = np.linalg.solve(J, rhs)
            if np.max(np.abs(vn - v)) < 1e-7:
                return vn
            v = vn
        return v

    # DC operating point (caps open)
    v = solve(G, np.zeros(n), vg_dc, np.full(n, vg_dc))
    h = 1.0 / fs
    Ycap = np.zeros((n, n))
    for a, b, c in caps:
        stamp(Ycap, a, b, 2 * c / h)
    Ylin = G + Ycap
    icap = np.zeros(len(caps))

    def vbr(vv, a, b):
        return (vv[IX[a]] if a else 0.0) - (vv[IX[b]] if b else 0.0)

    steps = int(round(cycles * fs / freq))
    out = np.empty(steps)
    for k in range(steps):
        tt = (k + 1) * h
        vg = vg_dc + amp * np.sin(2 * np.pi * freq * tt)
        Ieq = np.zeros(n)
        for j, (a, b, c) in enumerate(caps):
            # trapezoidal companion: i = 2C/h * v - (2C/h * v_prev + i_prev)
            ieq = 2 * c / h * vbr(v, a, b) + icap[j]
            if a in IX:
                Ieq[IX[a]] += ieq
            if b in IX:
                Ieq[IX[b]] -= ieq
        vnew = solve(Ylin, Ieq, vg, v)
        for j, (a, b, c) in enumerate(caps):
            icap[j] = 2 * c / h * (vbr(vnew, a, b) - vbr(v, a, b)) - icap[j]
        v = vnew
        out[k] = v[IX["W"]]
    per = int(round(fs / freq))
    seg = out[-2 * per:]
    seg = seg - seg.mean()
    spec = np.abs(np.fft.rfft(seg))
    f1 = 2  # two periods -> fundamental at bin 2
    harm = [spec[f1 * kk] for kk in range(2, 11) if f1 * kk < len(spec)]
    thd = np.sqrt(np.sum(np.square(harm))) / spec[f1]
    vk_dc = None
    return float(thd), float(spec[f1] * 2 / len(seg))


ORIG = dict(tube="12AX7", Rk=100e3, Bplus=378.0, vg_dc=200.0,
            C1=470e-12, Rslope=47e3, Cb=20e-9, Cm=20e-9, Rt=250e3, Rb=1e6, Rm=25e3, RL=500e3)
NEW = dict(tube="12AU7", Rk=22e3, Bplus=378.0, vg_dc=190.0,
           C1=5.6e-9, Rslope=4.7e3, Cb=220e-9, Cm=220e-9, Rt=20e3, Rb=100e3, Rm=2.5e3, RL=50e3)


def op_point(p):
    tb = KOREN[p["tube"]]
    from scipy.optimize import brentq
    f = lambda vk: ip_koren(p["vg_dc"] - vk, p["Bplus"] - vk, tb) * p["Rk"] - vk
    vk = brentq(f, 0.0, p["Bplus"] - 1.0)
    i = vk / p["Rk"]
    return dict(Vk=round(vk, 1), Ik_mA=round(i * 1e3, 2), Pa_W=round((p["Bplus"] - vk) * i, 2))


def main():
    out = {"op": {"orig": op_point(ORIG), "new": op_point(NEW)}, "sweeps": []}
    settings = {"5-5-5": (.5, .5, .5), "10-0-0": (1., 0., 0.), "10-10-10": (1., 1., 1.)}
    amps = [5, 10, 15, 20, 25, 30, 40, 50]
    for name, p in [("orig", ORIG), ("new", NEW)]:
        for sname, (t, x, m) in settings.items():
            for f in [100.0, 1000.0, 4000.0]:
                row = dict(ver=name, setting=sname, f=f, thd=[], vout=[])
                for a in amps:
                    thd, vo = simulate(p, p["tube"], p["vg_dc"], a, f, t, x, m)
                    row["thd"].append(round(100 * thd, 3))
                    row["vout"].append(round(vo, 2))
                out["sweeps"].append(row)
                print(name, sname, f, row["thd"], file=sys.stderr, flush=True)
    out["amps"] = amps
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cf_drive.json"), "w"), indent=1)
    print(json.dumps(out["op"]))


if __name__ == "__main__":
    main()
