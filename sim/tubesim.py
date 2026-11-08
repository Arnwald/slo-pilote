"""Small nonlinear transient circuit simulator for tube stages (MNA, trapezoidal, Newton).

Elements: resistors, capacitors, fixed-voltage nodes (supplies / signal source), Koren triodes.
Fixed nodes are eliminated; 'gnd' is 0 V.
"""
import numpy as np

KOREN = {
    "12AX7": dict(mu=100.0, ex=1.4, kg1=1060.0, kp=600.0, kvb=300.0),
    "12AU7": dict(mu=21.5, ex=1.3, kg1=1180.0, kp=84.0, kvb=300.0),
    "12AT7": dict(mu=60.0, ex=1.35, kg1=460.0, kp=300.0, kvb=300.0),
}


def ip_koren(vgk, vpk, t):
    if vpk <= 0:
        return 0.0
    arg = t["kp"] * (1.0 / t["mu"] + vgk / np.sqrt(t["kvb"] + vpk * vpk))
    e1 = vpk / t["kp"] * np.logaddexp(0.0, arg)
    return 2.0 * e1 ** t["ex"] / t["kg1"] if e1 > 0 else 0.0


def ig_grid(vgk):
    # crude grid-current model (positive grid): ~1 mA at +1.5 V
    return 5.4e-4 * vgk ** 1.5 if vgk > 0 else 0.0


def log_taper(x, mid=0.15):
    s = (1 - mid) / mid
    b = s * s
    return (b ** x - 1) / (b - 1)


class Circuit:
    def __init__(self):
        self.R, self.C, self.T = [], [], []
        self.fixed = {"gnd": lambda t: 0.0}

    def r(self, a, b, val):
        self.R.append((a, b, max(val, 1.0)))

    def c(self, a, b, val):
        self.C.append((a, b, val))

    def v(self, node, fn):
        self.fixed[node] = fn

    def triode(self, p, g, k, tube):
        self.T.append((p, g, k, KOREN[tube]))

    def _index(self):
        nodes = []
        for a, b, _ in self.R + self.C:
            nodes += [a, b]
        for p, g, k, _ in self.T:
            nodes += [p, g, k]
        free = sorted({n for n in nodes if n not in self.fixed})
        self.free = free
        self.ix = {n: i for i, n in enumerate(free)}

    def _volt(self, v, fixed_v, n):
        return v[self.ix[n]] if n in self.ix else fixed_v[n]

    def _linear(self, h):
        n = len(self.free)
        Y = np.zeros((n, n))
        # contributions to rhs from fixed nodes are computed per step
        for a, b, val in self.R:
            self._stamp(Y, a, b, 1.0 / val)
        if h:
            for a, b, val in self.C:
                self._stamp(Y, a, b, 2 * val / h)
        return Y

    def _stamp(self, Y, a, b, y):
        ia, ib = self.ix.get(a), self.ix.get(b)
        if ia is not None:
            Y[ia, ia] += y
        if ib is not None:
            Y[ib, ib] += y
        if ia is not None and ib is not None:
            Y[ia, ib] -= y
            Y[ib, ia] -= y

    def _fixed_rhs(self, fixed_v, h):
        n = len(self.free)
        I = np.zeros(n)
        elems = [(a, b, 1.0 / val) for a, b, val in self.R]
        if h:
            elems += [(a, b, 2 * val / h) for a, b, val in self.C]
        for a, b, y in elems:
            if a in self.ix and b not in self.ix:
                I[self.ix[a]] += y * fixed_v[b]
            elif b in self.ix and a not in self.ix:
                I[self.ix[b]] += y * fixed_v[a]
        return I

    def _newton(self, Ylin, Ibase, fixed_v, v0):
        v = v0.copy()
        for _ in range(80):
            J = Ylin.copy()
            rhs = Ibase.copy()
            for p, g, k, tb in self.T:
                vp, vg, vk = (self._volt(v, fixed_v, x) for x in (p, g, k))
                i0 = ip_koren(vg - vk, vp - vk, tb)
                d = 1e-4
                dip_dvg = (ip_koren(vg + d - vk, vp - vk, tb) - i0) / d
                dip_dvp = (ip_koren(vg - vk, vp + d - vk, tb) - i0) / d
                dip_dvk = -(dip_dvg + dip_dvp)
                ig0 = ig_grid(vg - vk)
                dig = (ig_grid(vg - vk + d) - ig0) / d
                # plate current leaves plate node, enters cathode; grid current leaves grid, enters cathode
                for node, sign in ((p, -1.0), (k, +1.0)):
                    if node in self.ix:
                        r = self.ix[node]
                        # linearised: I = i0 + sum dI/dVx (Vx - vx0)
                        rhs[r] += sign * (i0 - dip_dvg * vg - dip_dvp * vp - dip_dvk * vk)
                        for xn, dd in ((g, dip_dvg), (p, dip_dvp), (k, dip_dvk)):
                            if xn in self.ix:
                                J[r, self.ix[xn]] -= sign * dd
                            else:
                                rhs[r] += sign * dd * fixed_v[xn]
                for node, sign in ((g, -1.0), (k, +1.0)):
                    if node in self.ix:
                        r = self.ix[node]
                        rhs[r] += sign * (ig0 - dig * (vg - vk))
                        for xn, dd in ((g, dig), (k, -dig)):
                            if xn in self.ix:
                                J[r, self.ix[xn]] -= sign * dd
                            else:
                                rhs[r] += sign * dd * fixed_v[xn]
            vn = np.linalg.solve(J, rhs)
            step = vn - v
            m = np.max(np.abs(step))
            if m > 20:
                step *= 20 / m
            v = v + step
            if m < 1e-7:
                break
        return v

    def dc(self, guess=None):
        self._index()
        fixed_v = {k: f(0.0) for k, f in self.fixed.items()}
        Y = self._linear(0)
        n = len(self.free)
        # tiny conductance to ground keeps cap-only nodes defined
        Y = Y + np.eye(n) * 1e-12
        v0 = np.array([guess.get(nn, 100.0) if guess else 100.0 for nn in self.free])
        return self._newton(Y, self._fixed_rhs(fixed_v, 0), fixed_v, v0)

    def tran(self, t_end, fs, probe, guess=None):
        v = self.dc(guess)
        h = 1.0 / fs
        Ylin = self._linear(h)
        icap = np.zeros(len(self.C))
        steps = int(round(t_end * fs))
        out = np.empty(steps)
        fixed_prev = {k: f(0.0) for k, f in self.fixed.items()}

        def vb(vv, fv, a, b):
            return self._volt(vv, fv, a) - self._volt(vv, fv, b)

        for s in range(steps):
            tt = (s + 1) * h
            fixed_v = {k: f(tt) for k, f in self.fixed.items()}
            I = self._fixed_rhs(fixed_v, h)
            for j, (a, b, val) in enumerate(self.C):
                ieq = 2 * val / h * vb(v, fixed_prev, a, b) + icap[j]
                if a in self.ix:
                    I[self.ix[a]] += ieq
                if b in self.ix:
                    I[self.ix[b]] -= ieq
            vn = self._newton(Ylin, I, fixed_v, v)
            for j, (a, b, val) in enumerate(self.C):
                icap[j] = 2 * val / h * (vb(vn, fixed_v, a, b) - vb(v, fixed_prev, a, b)) - icap[j]
            v, fixed_prev = vn, fixed_v
            out[s] = self._volt(v, fixed_v, probe)
        return out


def thd(sig, fs, f0, periods=2):
    per = int(round(fs / f0))
    seg = sig[-periods * per:]
    seg = seg - seg.mean()
    spec = np.abs(np.fft.rfft(seg))
    harm = [spec[periods * k] for k in range(2, 11) if periods * k < len(spec)]
    return float(np.sqrt(np.sum(np.square(harm))) / spec[periods]), float(spec[periods] * 2 / len(seg))


def add_stack(ckt, src, p, t, x, m, out="W"):
    """Tone stack fed from node `src`; output at node `out` (treble wiper)."""
    ckt.c(src, "T", p["C1"])
    ckt.r(src, "A", p["Rslope"])
    ckt.c("A", "B", p["Cb"])
    ckt.c("A", "Mw", p["Cm"])
    ckt.r("T", out, (1 - t) * p["Rt"])
    ckt.r(out, "B", t * p["Rt"])
    ckt.r("B", "M", p["Rb"] * log_taper(x))
    ckt.r("M", "Mw", (1 - m) * p["Rm"])
    ckt.r("Mw", "gnd", m * p["Rm"])
    ckt.r(out, "gnd", p["RL"])
