"""Switching transients ("pops") with time-varying LDR / relay models, no input signal.

Each case switches at T0 and reports the peak speaker voltage after T0 (V and dB re 100 W),
plus the time after which the output stays below 10 mV.
python3 pops_test.py <case> ...  -> res_pops_<case>.json
"""
import json
import os
import sys

import numpy as np

import sim

HERE = os.path.dirname(os.path.abspath(__file__))
T0 = 0.3
VFS = 28.3


def mute_seq(t_on, t_off, keep="ldr3"):
    """Mute = shunt LDR at the PI input on + series master LDR off, between t_on and t_off."""
    return {"mute": ("seq", "off", [(t_on, "on"), (t_off, "off")]),
            keep: ("seq", "on", [(t_on, "off"), (t_off, "on")])}


CASES = {
    "clip4k4": dict(sw={"cl2": ("on", T0)}),
    "clip4k4_back": dict(clipper="4k4", sw={"cl2": ("off", T0)}),
    "clip10k": dict(sw={"cl1": ("on", T0)}),
    "clip4k4_slow": dict(sw={"cl2": ("on", T0, 0.15)}),
    "clip4k4_mute200": dict(sw={"cl2": ("on", T0), **mute_seq(T0 - 0.005, T0 + 0.2)}),
    "clip4k4_mute400": dict(sw={"cl2": ("on", T0), **mute_seq(T0 - 0.005, T0 + 0.4)}),
    "clip4k4_mute700": dict(sw={"cl2": ("on", T0), **mute_seq(T0 - 0.005, T0 + 0.7)}, tstop=1.4),
    "clip4k4_ac": dict(clipper_mode="ac", sw={"cl2": ("on", T0)}),
    "clip4k4_early300": dict(sw={"cl2": ("on", T0), **mute_seq(T0 - 0.05, T0 + 0.3)}),
    "clip4k4_early500": dict(sw={"cl2": ("on", T0), **mute_seq(T0 - 0.05, T0 + 0.5)}, tstop=1.2),
    "cc_relay": dict(sw={"cc20": ("off", T0 + 0.001), "cc22": ("on", T0)}),
    "cc_relay_nobleed": dict(nobleed=True, sw={"cc20": ("off", T0 + 0.001), "cc22": ("on", T0)}),
    "push": dict(sw={"push": ("on", T0)}),
    "channel": dict(sw={"ldr1": ("on", T0), "ldr2": ("off", T0), "ldr3": ("off", T0), "ldr4": ("on", T0)}),
    "extra": dict(sw={"dir": ("off", T0), "ext": ("on", T0), "ldrx": ("off", T0)}),
    "bypass": dict(sw={"bp1": ("off", T0), "bp2": ("off", T0)}),
    "bright": dict(channel="normal", sw={"br": ("on", T0)}),
    "crunch_clean": dict(channel="normal", sw={"cr1": ("off", T0), "cr2": ("on", T0)}),
    "mute_only": dict(sw=mute_seq(T0, T0 + 0.2)),
}


def run(case):
    p = dict(CASES[case])
    tstop = p.pop("tstop", 1.0)
    nobleed = p.pop("nobleed", False)
    kw = dict(gain_od=0.7, master=0.3)
    kw.update(p)
    probes = ["sec", "jn", "piin"]
    if nobleed:
        # unselected 2.2 nF left floating since power-up (no bleeder): uncharged, so its grid side
        # sits at the plate voltage (258 V). Emulated by holding n22 at 258 V until just before T0.
        import slo
        orig_netlist = slo.netlist

        def patched(*a, **k):
            n = orig_netlist(*a, **k)
            hold = "\n".join(slo.switch("fl", "n22", "nfl", ("off", T0 - 0.0005), ron=4.7e6, roff=1e12,
                                         tau_off=1e-5))
            return n.replace("Rbl22 n22 0 4.7Meg", "Vfl nfl 0 258\n" + hold)
        sim.slo.netlist = patched
    t, s, dt = sim.tran("mod", tstop, 20e-6, probes, maxstep=50e-6, **kw)
    y = s["sec"]
    pre = np.abs(y[(t > T0 - 0.1) & (t < T0 - 0.06)]).max()
    post = np.abs(y[t >= T0 - 0.06])
    ta = t[t >= T0 - 0.06]
    pk = float(post.max())
    above = np.where(post > 0.01)[0]
    settle = float(ta[above[-1]] - T0) if len(above) else 0.0
    res = dict(case=case, pre_mV=round(1e3 * float(pre), 3), peak_V=round(pk, 4),
               peak_dB_re_100W=round(20 * np.log10(max(pk, 1e-9) / VFS), 1),
               settle_10mV_s=round(settle, 3), jn_peak_V=round(float(np.abs(s["jn"][t >= T0]).max()), 3),
               piin_peak_V=round(float(np.abs(s["piin"][t >= T0]).max()), 3), cpu_s=round(dt, 1))
    # downsampled trace for plots
    tt = np.linspace(T0 - 0.05, tstop, 600)
    res["trace_t"] = [round(x, 4) for x in tt]
    res["trace_sec"] = [round(float(x), 4) for x in np.interp(tt, t, y)]
    json.dump(res, open(os.path.join(HERE, f"res_pops_{case}.json"), "w"))
    print(json.dumps({k: v for k, v in res.items() if not k.startswith("trace")}), flush=True)


if __name__ == "__main__":
    for c in sys.argv[1:]:
        run(c)
