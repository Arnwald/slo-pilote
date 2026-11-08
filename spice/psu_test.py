"""Rectifier/transformer supply: idle voltages, ripple per node, hum at the speaker, sag at full power.

python3 psu_test.py <case>   (cases listed in CASES); results in res_psu_<case>.json
"""
import json
import os
import sys

import numpy as np

import sim

HERE = os.path.dirname(os.path.abspath(__file__))
VFS = 28.3  # peak volts at the 4 ohm tap for 100 W

NODES = ["b1", "b2", "b3", "b4", "b5"]
MOD_NODES = ["bf", "bw", "bx"]
IMB = {"a1": 0.3, "a2": 0.3, "b1": -0.3, "b2": -0.3}

CASES = {
    "orig_idle": dict(variant="orig"),
    "mod_idle": dict(variant="mod"),
    "modf_idle": dict(variant="mod", buf_filter=True),
    "modff_idle": dict(variant="mod", buf_filter=True, wcf_filter=True),
    "orig_imb": dict(variant="orig", bias_offsets=IMB),
    "modf_imb": dict(variant="mod", buf_filter=True, bias_offsets=IMB),
    "orig_m10": dict(variant="orig", master=1.0),
    "modf_m10": dict(variant="mod", buf_filter=True, master=1.0),
    "mod_m10": dict(variant="mod", master=1.0),
    "orig_sag": dict(variant="orig", drive_pi=True, sag=True),
    "modf_sag": dict(variant="mod", buf_filter=True, drive_pi=True, sag=True),
    "orig_sag_ideal": dict(variant="orig", drive_pi=True, sag=True, psu="ideal"),
    "modf_sag_ideal": dict(variant="mod", buf_filter=True, drive_pi=True, sag=True, psu="ideal"),
    "orig_sag_hard": dict(variant="orig", drive_pi=True, sag=True, amp=8.0),
    "modnf_idle": dict(variant="mod", buf_filter=False),
    "modnf_m10": dict(variant="mod", buf_filter=False, master=1.0),
}


def hum_lines(t, y, t0):
    sel = t >= t0
    tt, yy = t[sel], y[sel]
    out = {}
    for f in (50, 100, 150, 200, 300):
        a, _ = sim.tone(tt, yy - np.polyval(np.polyfit(tt, yy, 1), tt), f)
        out[f] = a
    return out


def run(case):
    p = dict(CASES[case])
    variant = p.pop("variant")
    sag = p.pop("sag", False)
    psu = p.pop("psu", "real")
    amp_sag = p.pop("amp", 5.0)
    probes = NODES + (MOD_NODES if variant == "mod" else []) + ["sec"]
    kw = dict(gain_od=0.7, master=0.3)
    kw.update(p)
    res = dict(case=case, variant=variant, params={k: str(v) for k, v in p.items()})
    if not sag:
        t, s, dt = sim.tran(variant, 4.0, 20e-6, probes, tstart=2.0, maxstep=50e-6, psu=psu, **kw)
        t0 = 3.5
        sel = t >= t0
        res["dc"] = {n: round(float(s[n][sel].mean()), 2) for n in probes if n != "sec"}
        res["drift_V_per_s"] = {n: round(float(np.polyfit(t[sel], s[n][sel], 1)[0]), 3) for n in probes if n != "sec"}
        res["ripple_100Hz_mVpk"] = {n: round(1e3 * hum_lines(t, s[n], t0)[100], 3) for n in probes if n != "sec"}
        h = hum_lines(t, s["sec"], t0)
        res["hum_sec_mVpk"] = {str(f): round(1e3 * a, 4) for f, a in h.items()}
        tot = np.sqrt(sum(a * a for a in h.values()))
        res["hum_total_dB_re_100W"] = round(20 * np.log10(tot / VFS), 1)
    else:
        f, amp, td, tend = 400.0, amp_sag, 1.2, 1.8
        t, s, dt = sim.tran(variant, tend, 25e-6, probes, tstart=1.0, maxstep=25e-6, psu=psu,
                            vin_spec=f"SIN(0 {amp} {f} {td})", **kw)
        if t[-1] < tend - 1e-3:
            raise RuntimeError(f"simulation stopped at {t[-1]:.4f} s")
        idle = t < td
        full = t >= tend - 0.1
        res["idle"] = {n: round(float(s[n][idle].mean()), 2) for n in probes if n != "sec"}
        res["loaded"] = {n: round(float(s[n][full].mean()), 2) for n in probes if n != "sec"}
        y = s["sec"][full]
        res["p_total_W"] = round(float(np.mean((y - y.mean()) ** 2) / 4.0), 1)
        h = sim.spectrum(t, s["sec"], f, 32, nh=15, pts=32 * 64)
        res["p_harm_W"] = round(float(sum(a * a for a in h) / 2 / 4.0), 1)
        res["fund_Vpk"] = round(h[0], 2)
        res["p_fund_W"] = round(h[0] ** 2 / 2 / 4.0, 1)
        res["thd_out"] = round(float(np.sqrt(sum(a * a for a in h[1:])) / h[0]), 3)
        # 100 Hz products riding on the output (supply ripple intermodulation)
        a100, _ = sim.tone(t[full], y, 100.0)
        res["ripple100_out_Vpk"] = round(a100, 3)
        res["b1_min"] = round(float(s["b1"][t >= td].min()), 1)
    res["cpu_s"] = round(dt, 1)
    json.dump(res, open(os.path.join(HERE, f"res_psu_{case}.json"), "w"), indent=1)
    print(json.dumps(res))


if __name__ == "__main__":
    for c in sys.argv[1:]:
        run(c)
