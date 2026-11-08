"""Generic ngspice runners for the campaign (transient, AC, noise)."""
import os
import subprocess
import tempfile
import time

import numpy as np

import slo

HERE = os.path.dirname(os.path.abspath(__file__))


def _run(net, timeout=3600):
    cir = tempfile.mktemp(suffix=".cir", dir=HERE)
    open(cir, "w").write(net)
    t0 = time.time()
    r = subprocess.run(["ngspice", "-b", cir], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    os.remove(cir)
    return r, time.time() - t0


def tran(variant, tstop, tstep, probes, tstart=0.0, vin_spec="0", maxstep=None, **kw):
    """Transient; returns (t, {probe: array}). Probes are node names or expressions like 'v(a,b)'."""
    out = tempfile.mktemp(suffix=".dat", dir=HERE)
    vec = " ".join(p if p.startswith(("v(", "i(")) else f"v({p})" for p in probes)
    ms = f" {maxstep:.4g}" if maxstep else ""
    an = f""".control
set wr_singlescale
set wr_vecnames
tran {tstep:.4g} {tstop:.6g} {tstart:.6g}{ms}
wrdata {out} {vec}
.endc"""
    net = slo.netlist(variant, vin_spec=vin_spec, analysis=an, **kw)
    r, dt = _run(net)
    if not os.path.exists(out) or "aborted" in r.stdout + r.stderr:
        # retry once with a shunt conductance on every node (helps the 6L6GC screen-grid law near cutoff)
        if os.path.exists(out):
            os.remove(out)
        net = net.replace(".options method=gear", ".options rshunt=1e9 method=gear", 1)
        r, dt2 = _run(net)
        dt += dt2
    if not os.path.exists(out) or "aborted" in r.stdout + r.stderr:
        raise RuntimeError(r.stdout[-3000:] + r.stderr[-3000:])
    d = np.loadtxt(out, skiprows=1)
    os.remove(out)
    return d[:, 0], {p: d[:, 1 + i] for i, p in enumerate(probes)}, dt


def ac(variant, probe="sec", fstart=10, fstop=20e3, ppd=20, **kw):
    """Small-signal response from Vin (AC 1 V) to probe; returns (f, complex H)."""
    out = tempfile.mktemp(suffix=".dat", dir=HERE)
    an = f""".control
set wr_singlescale
ac dec {ppd} {fstart} {fstop}
wrdata {out} v({probe})
.endc"""
    net = slo.netlist(variant, vin_spec="DC 0 AC 1", analysis=an, **kw)
    r, dt = _run(net)
    if not os.path.exists(out):
        raise RuntimeError(r.stdout[-3000:] + r.stderr[-3000:])
    d = np.loadtxt(out)
    os.remove(out)
    return d[:, 0], d[:, 1] + 1j * d[:, 2]


def noise(variant, probe="sec", fstart=10, fstop=30e3, ppd=20, **kw):
    """Output noise density (V/rtHz) at probe and input-referred density, vs Vin."""
    out = tempfile.mktemp(suffix=".dat", dir=HERE)
    an = f""".control
set wr_singlescale
noise v({probe}) Vin dec {ppd} {fstart} {fstop}
setplot noise1
wrdata {out} onoise_spectrum inoise_spectrum
.endc"""
    net = slo.netlist(variant, vin_spec="DC 0 AC 1", analysis=an, noise_req=True, **kw)
    r, dt = _run(net)
    if not os.path.exists(out):
        raise RuntimeError(r.stdout[-3000:] + r.stderr[-3000:])
    d = np.loadtxt(out)
    os.remove(out)
    return d[:, 0], d[:, 1], d[:, 2]


def tone(t, y, f, t0=None, periods=None, fs=50e3):
    """Amplitude (peak) and offset of the component at f over [t0, t_end], least squares on a
    uniform grid (the simulator's adaptive time steps cluster around diode conduction, which
    would bias a fit made on the raw samples)."""
    ta = t0 if t0 is not None else t[0]
    if periods is not None:
        ta = max(ta, t[-1] - periods / f)
    n = int((t[-1] - ta) * fs)
    tt = np.linspace(ta, t[-1], max(n, 16), endpoint=False)
    yy = np.interp(tt, t, y)
    A = np.column_stack([np.cos(2 * np.pi * f * tt), np.sin(2 * np.pi * f * tt), np.ones_like(tt)])
    c, *_ = np.linalg.lstsq(A, yy, rcond=None)
    return float(np.hypot(c[0], c[1])), float(c[2])


def spectrum(t, y, f0, nper, nh=10, pts=4096):
    """Harmonics of f0 (peak amplitudes) over the last nper periods, uniform resampling."""
    T = nper / f0
    tu = np.linspace(t[-1] - T, t[-1], pts, endpoint=False)
    yu = np.interp(tu, t, y)
    yu = yu - yu.mean()
    sp = np.abs(np.fft.rfft(yu)) * 2 / len(yu)
    return [float(sp[nper * k]) for k in range(1, nh + 1)]
