"""NFB loop gain: break the loop at the 39k feedback resistor and drive it from a test source."""
import os, subprocess, tempfile
import numpy as np
import slo
HERE = os.path.dirname(os.path.abspath(__file__))

def loop(variant, presence, load="4", wcap=True):
    out = tempfile.mktemp(suffix=".dat", dir=HERE)
    an = f""".control
set wr_singlescale
ac dec 40 2 2Meg
wrdata {out} vr(sec) vi(sec)
.endc"""
    net = slo.netlist(variant, vin_spec="0", analysis=an, master=0.3, presence=presence)
    net = net.replace("Rnfb sec nfb 39k", "Rnfb tst nfb 39k\nVtst tst 0 DC 0 AC 1")
    if load == "open":
        net = net.replace("Rload sec 0 4.0", "Rload sec 0 1Meg")
    elif load == "spk":   # 4 ohm speaker-like: Re + Le, with resonance tank
        net = net.replace("Rload sec 0 4.0", "Rload sec spk1 3.2\nLvc spk1 spk2 0.25m\nRres spk2 0 20\nLres spk2 0 20m\nCres spk2 0 1.2m")
    if wcap:   # winding capacitance of the output transformer (estimate)
        pass  # winding capacitances (Cot1, Cot2) are now part of slo.netlist
    cir = tempfile.mktemp(suffix=".cir", dir=HERE)
    open(cir, "w").write(net)
    r = subprocess.run(["ngspice", "-b", cir], cwd=HERE, capture_output=True, text=True, timeout=300)
    os.remove(cir)
    d = np.loadtxt(out); os.remove(out)
    f = d[:, 0]; T = -(d[:, 1] + 1j * d[:, 2])
    mag = 20 * np.log10(np.abs(T))
    i0 = int(np.argmin(np.abs(f - 1000.0)))
    ph = np.degrees(np.angle(T))
    # unwrap outward from 1 kHz
    up = np.degrees(np.unwrap(np.radians(ph[i0:])))
    dn = np.degrees(np.unwrap(np.radians(ph[:i0 + 1][::-1])))[::-1]
    ph = np.concatenate([dn[:-1], up])
    ph -= 360 * np.round(ph[i0] / 360)
    res = dict(T_1k_dB=round(float(mag[i0]), 1))
    for side, idx in (("HF", range(i0, len(f))), ("LF", range(i0, -1, -1))):
        idx = list(idx)
        pm = gm = fc = None
        for j in idx:
            if fc is None and mag[j] < 0:
                fc = f[j]; pm = 180 - abs(ph[j])
            if gm is None and abs(ph[j]) >= 180:
                gm = -mag[j]
        res[side] = dict(f_c=None if fc is None else round(float(fc)),
                         PM=None if pm is None else round(float(pm), 1),
                         GM=None if gm is None else round(float(gm), 1))
    return res, (f, mag, ph)

if __name__ == "__main__":
    for variant in ("orig", "mod"):
        for pres in (0.0, 1.0):
            for load in ("4", "spk", "open"):
                r, _ = loop(variant, pres, load)
                print(variant, "presence", pres, "charge", load, r, flush=True)
