"""Tube Screamer models: TS808 (9 V, 4558-class op-amps) and the pilotable version
(+/-15 V, MCP41HV51 digital pots, rescaled drive network, 10k tone pot).

Topology after R.G. Keen, "The Technology of the Tube Screamer" (geofex) and ElectroSmash:
clipping stage = non-inverting op-amp, feedback (R6 + Rdrive) || 51 pF || 2 x 1N914, ground leg 4.7k + 47 nF;
tone = 1k / 220 nF low-pass, then 20k pot strung between the (+) and (-) inputs of the second
op-amp, wiper to 220 ohm + 220 nF, 1k feedback; volume 100k after 1 uF.
Input/output transistor buffers are taken as ideal.
"""
import os
import subprocess
import tempfile
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

OPAMP = """
.subckt OPA inp inn out vcc vee
Rin inp inn 1e12
Bgm 0 n1 I = 53e-6*tanh(V(inp,inn)/0.053)
R1 n1 0 1.9e9
C1 n1 0 53p
* rail clamps on the integrator node (no wind-up)
Bhi n1 0 I = (V(n1) > V(vcc)-1.5 ? (V(n1)-V(vcc)+1.5)*10 : 0)
Blo n1 0 I = (V(n1) < V(vee)+1.5 ? (V(n1)-V(vee)-1.5)*10 : 0)
Eo o0 0 n1 0 1
Ro o0 out 50
.ends
"""
# 1N914: small-signal silicon; LED red as an alternative clipper
DIODES = ".model D914 D(IS=2.52n N=1.752 RS=0.568 CJO=4p)\n.model DLED D(IS=1e-19 N=1.8 RS=3 CJO=20p)\n"


def netlist(version="ts808", drive=0.0, tone=0.5, level=1.0, vin_spec="0", analysis="", diode="D914",
            stage="all", tone_code=None):
    """version: "ts808" or "pilot"; drive/tone/level in 0..1 (pot fraction, i.e. after the firmware law).
    stage: "all", "clip" (output at o1), "tone" (tone stage driven directly, output at o2)."""
    pilot = version == "pilot"
    L = ["* Tube Screamer " + version, OPAMP, DIODES]
    if pilot:
        L += ["Vcc vcc 0 15", "Vee vee 0 -15", "Vb vb 0 0"]
        rs, rdmax, cf, rg, cg, rtone = 10e3, 100e3, 270e-12, 1e3, 220e-9, 10e3
    else:
        L += ["Vcc vcc 0 9", "Vee vee 0 0", "Vb vb 0 4.5"]
        rs, rdmax, cf, rg, cg, rtone = 51e3, 500e3, 51e-12, 4.7e3, 47e-9, 20e3
    if stage == "tone":
        L += [f"Vin ti vb {vin_spec}", "R7 ti ta 1k"]
    else:
        L += [f"Vin in 0 {vin_spec}", "Ebuf b0 vb in 0 1", "C2 b0 x1 1u", "R5 x1 vb 10k",
              "X1 x1 nf o1 vcc vee OPA",
              f"R6 o1 nd {rs:g}", f"Rdrv nd nf {max(rdmax * drive, 75):g}", f"C4 o1 nf {cf:g}",
              f"D1 o1 nf {diode}", f"D2 nf o1 {diode}",
              f"R4 nf ng {rg:g}", f"C3 ng vb {cg:g}", "R7 o1 ta 1k"]
    if stage != "clip":
        if tone_code is not None:            # digital pot: 256 taps, 75 ohm wiper
            x = tone_code / 255.0
        else:
            x = tone
        L += ["C5 ta vb 0.22u",
              f"Rtp1 ta tw {max(rtone * (1 - x), 1):g}", f"Rtp2 tw tn {max(rtone * x, 1):g}",
              "R8 tw tc 220" if not pilot else "R8 tw tc 150", "C6 tc vb 0.22u",
              "X2 ta tn o2 vcc vee OPA", "R9 o2 tn 1k",
              "C7 o2 vo 1u", f"Rlv1 vo out {max(100e3 * (1 - level), 1):g}", f"Rlv2 out vb {max(100e3 * level, 1):g}",
              "Rload out vb 1Meg"]
    L += [analysis, ".end"]
    return "\n".join(L)


def run(net):
    cir = tempfile.mktemp(suffix=".cir", dir=HERE)
    open(cir, "w").write(net)
    t0 = time.time()
    r = subprocess.run(["ngspice", "-b", cir], cwd=HERE, capture_output=True, text=True, timeout=600)
    os.remove(cir)
    return r, time.time() - t0


def ac(probe="out", **kw):
    out = tempfile.mktemp(suffix=".dat", dir=HERE)
    an = f".control\nset wr_singlescale\nac dec 30 20 20k\nwrdata {out} v({probe})\n.endc"
    r, _ = run(netlist(vin_spec="DC 0 AC 1", analysis=an, **kw))
    if not os.path.exists(out):
        raise RuntimeError(r.stdout[-2000:])
    d = np.loadtxt(out)
    os.remove(out)
    return d[:, 0], d[:, 1] + 1j * d[:, 2]


def tran(f, amp, probe="out", cycles=20, **kw):
    out = tempfile.mktemp(suffix=".dat", dir=HERE)
    tstop = cycles / f
    an = f".control\nset wr_singlescale\ntran {1 / f / 400:.4g} {tstop:.6g} {tstop / 2:.6g} {1 / f / 400:.4g}\nwrdata {out} v({probe})\n.endc"
    r, _ = run(netlist(vin_spec=f"SIN(0 {amp} {f})", analysis=an, **kw))
    if not os.path.exists(out):
        raise RuntimeError(r.stdout[-2000:])
    d = np.loadtxt(out)
    os.remove(out)
    return d[:, 0], d[:, 1]
