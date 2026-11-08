"""Boss HM-2 Heavy Metal (MIJ) model for ngspice, original values.

Values and topology from the Boss service schematic (IC1-IC3 M5218L/NJM4558, Q6 2SC2240-GR,
Q7 2SA970-GR, D3-D5/D8/D9 1S2473, D6/D7 1S188FM germanium):
  - pre-gain: two transimpedance stages, Q6 (NPN) and Q7 (PNP), 22k in / 470k feedback, each
    behind a 47 nF coupling capacitor (high-pass near 150 Hz);
  - DIST (VR4 250k D): ends to Q6's collector (through 150 ohm + 10 uF) and to the ground leg of
    IC1b (47k + 47 nF), wiper grounded: one pot sets both the pre-gain and the op-amp gain;
  - IC1b: non-inverting, 220k || 100 pF || asymmetric diodes (1 one way, 2 the other);
  - two germanium diodes in anti-parallel in series with the signal (dead zone), then two silicon
    diodes to ground and 1 nF, buffer IC1a;
  - COLOR MIX: IC3a non-inverting, 3.3k in / 3.3k || 470 pF feedback, pots L and H (10k G) strung
    between its (+) and (-) inputs, wipers to series-resonant gyrators: L 1.5 uF with
    330 ohm x 100k x 68 nF (87 Hz), H 0.15 uF with 330 x 82k x 6.8 nF (958 Hz) and 0.1 uF with
    330 x 100k x 4.7 nF (1.28 kHz);
  - LEVEL (VR1 10k A) behind 10k.
The input buffer and the electronic bypass (Q1-Q5, Q8-Q10) are left out: the clone is fed by the
head's input buffer and is always on.

Pot positions are fractions of rotation, 0 = fully CCW (lug 1), 1 = fully CW (lug 3), with a
linear law (the Boss D and G laws are not documented); a clone uses trimmers set by ear anyway.
"""
import os
import subprocess
import tempfile

import numpy as np

from ts import OPAMP, run

HERE = os.path.dirname(os.path.abspath(__file__))

MODELS = """
.model D1S2473 D(IS=2.52n N=1.752 RS=0.568 CJO=4p)
.model DGE D(IS=2e-7 N=1.3 RS=7 CJO=1p BV=60 IBV=1e-5)
.model Q2SC2240 NPN(IS=7.05f BF=380 NF=1 VAF=60 IKF=0.1 ISE=1.4e-14 NE=1.5 BR=8 RB=20 RE=0.5 RC=1
+ CJE=11.5p CJC=5.3p TF=0.5n TR=10n)
.model Q2SA970 PNP(IS=1e-14 BF=350 NF=1 VAF=50 IKF=0.08 ISE=1e-14 NE=1.5 BR=8 RB=20 RE=0.5 RC=1
+ CJE=13p CJC=8p TF=0.6n TR=10n)
"""


def _r(x):
    return f"{max(x, 1.0):g}"


def netlist(dist=1.0, low=1.0, high=1.0, level=1.0, vcc=9.0, vin_spec="0", analysis="", probe_nodes=(),
            ron=0.0, rgyr=330.0, r49=150.0, rpots=None, kb=1.0):
    """ron: on-resistance of a multiplexer in series with the Dist and Color Mix wipers (0 = pots);
    rgyr: gyrator series resistors, kb: factor on their bias resistors (L = rgyr x rb x cg); r49: resistor between Q6's collector and the Dist pot;
    rpots: {"dist" | "low" | "high": (r12, r23)} to set the two halves of a pot explicitly."""
    rp = dict(dist=(250e3 * dist, 250e3 * (1 - dist)), low=(10e3 * low, 10e3 * (1 - low)),
              high=(10e3 * high, 10e3 * (1 - high)))
    rp.update(rpots or {})
    wd, wl, wh = ("wd", "wlm", "whm") if ron > 0 else ("0", "wl", "wh")
    L = ["* Boss HM-2 (MIJ), original values", OPAMP, MODELS,
         f"Vcc vcc 0 {vcc:g}", f"Vb vb 0 {vcc / 2:g}", f"Vin in 0 {vin_spec}",
         # pre-gain Q6
         "C6 in n6 47n", "R19 n6 b6 22k", "R21 b6 0 100k", "R16 c6 b6 470k", "C10 c6 b6 100p",
         "Q6 c6 b6 e6 Q2SC2240", "R18 e6 0 22", "R17 s c6 10k", "R10 vcc s 1k", "C5 s 0 47u",
         # DIST: lug 1 -> pin 7 (Q6 collector through 150 + 10u), lug 3 -> pin 10 (IC1b ground leg), wiper to 0
         f"R49 c6 n49 {r49:g}", "C31 n49 p7 10u",
         f"RD12 p7 {wd} {_r(rp['dist'][0])}", f"RD23 p10 {wd} {_r(rp['dist'][1])}",
         # pre-gain Q7
         "C11 c6 n11 47n", "R22 n11 b7 22k", "R26 s b7 100k", "R29 b7 c7 470k", "C14 b7 c7 100p",
         "Q7 c7 b7 e7 Q2SA970", "R28 s e7 120", "R27 c7 0 10k", "R25 vcc c7 68k",
         # IC1b clipping amplifier
         "X1b c7 n1m o1b vcc 0 OPA", "R20 o1b n1m 220k", "C9 o1b n1m 100p",
         "D3 n1m o1b D1S2473", "D4 o1b n45 D1S2473", "D5 n45 n1m D1S2473",
         "C22 n1m n22 47n", "R42 n22 p10 47k",
         # germanium dead zone, silicon clipper, buffer IC1a
         "C12 o1b n12 1u", "R23 n12 n23 10k", "D6 n23 n30 DGE", "D7 n30 n23 DGE", "R30 n30 n16 10k",
         "D9 n16 0 D1S2473", "D8 0 n16 D1S2473", "C16 n16 0 1n",
         "C15 n16 n1a 1u", "R24 n1a vb 68k", "X1a n1a o1a o1a vcc 0 OPA",
         # COLOR MIX: IC3a non-inverting, pots between (+) p14 (lug 1) and (-) p13 (lug 3)
         "R54 o1a p14 3.3k", "X3a p14 p13 o3a vcc 0 OPA", "R52 o3a p13 3.3k", "C33 o3a p13 470p",
         f"RL12 p14 {wl} {_r(rp['low'][0])}", f"RL23 {wl} p13 {_r(rp['low'][1])}",
         f"RH12 p14 {wh} {_r(rp['high'][0])}", f"RH23 {wh} p13 {_r(rp['high'][1])}",
         "C35 wl x1 1.5u", "C30 x1 g1 68n", f"R51 g1 vb {100e3 * kb:g}", f"R47 x1 o3b {rgyr:g}", "X3b g1 o3b o3b vcc 0 OPA",
         "C28 wh x2 0.15u", "C27 x2 g2 6.8n", f"R43 g2 vb {82e3 * kb:g}", f"R41 x2 o2a {rgyr:g}", "X2a g2 o2a o2a vcc 0 OPA",
         "C29 wh x3 0.1u", "C26 x3 g3 4.7n", f"R44 g3 vb {100e3 * kb:g}", f"R45 x3 o2b {rgyr:g}", "X2b g3 o2b o2b vcc 0 OPA",
         # LEVEL: 10k series, VR1 lug 3 -> wiper -> lug 1 = ground; light load
         "C34 o3a n34 10u", "R53 n34 lv3 10k",
         f"RV32 lv3 out {_r(10e3 * (1 - level))}", f"RV21 out 0 {_r(10e3 * level)}", "Rload out 0 1Meg",
         analysis, ".end"]
    if ron > 0:
        L[-2:-2] = [f"Rmd wd 0 {ron:g}", f"Rml wlm wl {ron:g}", f"Rmh whm wh {ron:g}"]
    return "\n".join(L)


def ac(probe="out", fstart=20, fstop=20e3, inject=None, **kw):
    """Small-signal response at the operating point. inject='eq' drives the colour-mix stage alone
    (source in series with C15, i.e. at the IC1a input) to see the equaliser on its own."""
    out = tempfile.mktemp(suffix=".dat", dir=HERE)
    an = f".control\nset wr_singlescale\nac dec 40 {fstart} {fstop}\nwrdata {out} v({probe})\n.endc"
    net = netlist(vin_spec="DC 0 AC 1" if inject is None else "DC 0", analysis=an, **kw)
    if inject == "eq":
        net = net.replace("C15 n16 n1a 1u", "C15 neq n1a 1u\nVeq neq 0 DC 0 AC 1")
    r, _ = run(net)
    if not os.path.exists(out):
        raise RuntimeError(r.stdout[-3000:])
    d = np.loadtxt(out)
    os.remove(out)
    return d[:, 0], d[:, 1] + 1j * d[:, 2]


def tran(f, amp, probes=("out",), cycles=30, **kw):
    out = tempfile.mktemp(suffix=".dat", dir=HERE)
    tstop = cycles / f
    step = 1 / f / 500
    vec = " ".join(f"v({p})" for p in probes)
    an = (f".options method=gear reltol=1e-4\n.control\nset wr_singlescale\n"
          f"tran {step:.4g} {tstop:.6g} {tstop * 0.6:.6g} {step:.4g}\nwrdata {out} {vec}\n.endc")
    r, _ = run(netlist(vin_spec=f"SIN(0 {amp} {f})", analysis=an, **kw))
    if not os.path.exists(out):
        raise RuntimeError(r.stdout[-3000:])
    d = np.loadtxt(out)
    os.remove(out)
    t = d[:, 0]
    return t, {p: d[:, i + 1] for i, p in enumerate(probes)}


def op(**kw):
    out = tempfile.mktemp(suffix=".txt", dir=HERE)
    nodes = ["s", "c6", "b6", "c7", "b7", "o1b", "n1m", "o1a", "o3a", "out"]
    an = ".control\nop\nprint " + " ".join(f"v({n})" for n in nodes) + f" > {out}\n.endc"
    r, _ = run(netlist(analysis=an, **kw))
    txt = open(out).read() if os.path.exists(out) else r.stdout
    if os.path.exists(out):
        os.remove(out)
    return txt
