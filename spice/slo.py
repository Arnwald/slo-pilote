"""Netlist generator for the SLO-100 and the pilotable variant.

variant: "orig" | "mod"

v2 adds every switchable mode, a rectifier/transformer supply model, time-varying LDR and
relay models (for switching transients), a loudspeaker load and equivalent tube noise.
With default arguments the netlist is identical to v1 (OD channel, crunch divider, ideal HT).

HT models
  psu="ideal" : DC source of 509 V behind 45 ohm feeding the SLO filter chain (v1 model).
  psu="real"  : centre-tapped secondary, two series diodes per leg, winding resistance and
                leakage inductance per half (psu_par overrides vpk, rw, ll).
"""
import math

LDR_ON, LDR_OFF = 1e3, 50e6
TAU_ON, TAU_OFF = 2.5e-3, 7.6e-3   # VTL5C1-like: 63 % of conductance in 2.5 ms; 1k -> 100k in 35 ms
RLY_ON, RLY_OFF = 0.1, 1e12

# equivalent shot-noise resistances (2.5 / gm) at the grids, for noise analyses only
REQ = {"12AX7": 1.6e3, "12AU7": 1.0e3, "12AT7": 0.5e3}


def log_taper(x, mid=0.15):
    s = (1 - mid) / mid
    b = s * s
    return (b ** x - 1) / (b - 1)


def pot(name, top, wiper, bot, R, x, law="lin"):
    f = x if law == "lin" else log_taper(x)
    up = max(R * (1 - f), 1.0)
    dn = max(R * f, 1.0)
    return [f"R{name}u {top} {wiper} {up:.6g}", f"R{name}d {wiper} {bot} {dn:.6g}"]


def switch(name, a, b, state, ron=LDR_ON, roff=LDR_OFF, tau_on=TAU_ON, tau_off=TAU_OFF):
    """Static or time-varying switch element (LDR by default).

    state: "on" | "off" | ("on", t0[, tau]) | ("off", t0[, tau])
    The conductance moves exponentially between the two states, which is how a VTL5C1
    behaves to first order (fast on, slower off).
    """
    if state == "on":
        return [f"R{name} {a} {b} {ron:g}"]
    if state == "off":
        return [f"R{name} {a} {b} {roff:g}"]
    gon, goff = 1.0 / ron, 1.0 / roff

    def seg(kind, t0, tau=None):
        if kind == "on":
            tau = tau or tau_on
            return f"{goff:g} + {gon - goff:g}*(1 - exp(-(time - {t0:g})/{tau:g}))"
        tau = tau or tau_off
        return f"{goff:g} + {gon - goff:g}*exp(-(time - {t0:g})/{tau:g})"

    if state[0] == "seq":
        # ("seq", initial_state, [(t1, "on"|"off"[, tau]), (t2, ...), ...]); transitions assumed complete
        init, steps = state[1], state[2]
        g = f"{gon:g}" if init == "on" else f"{goff:g}"
        for st in steps:
            t0, kind = st[0], st[1]
            tau = st[2] if len(st) > 2 else None
            g = f"(time > {t0:g} ? {seg(kind, t0, tau)} : {g})"
    else:
        kind, t0 = state[0], state[1]
        tau = state[2] if len(state) > 2 else None
        g = f"(time > {t0:g} ? {seg(kind, t0, tau)} : {goff if kind == 'on' else gon:g})"
    return [f"B{name} {a} {b} I = V({a},{b})*{g}"]


def relay(name, a, b, state):
    """Signal relay: 0.1 ohm / 1e12 ohm, 1 ms transition."""
    return switch(name, a, b, state, RLY_ON, RLY_OFF, 0.3e-3, 0.3e-3)


def netlist(variant="orig", gain_od=0.7, gain_n=0.5, treble=0.5, bass=0.5, mid=0.5,
            master=0.3, presence=0.5, vin_spec="0", bias=-55.0, extra=False, push=False,
            analysis="", rload=4.0,
            channel="od", crunch=True, bright_n=False, master_n=0.3,
            clipper="39k", bypass="full", cc_v2a="20n", depth=None, depth_net=None,
            psu="ideal", psu_par=None, sw=None, load="r", noise_req=False, buf_filter=None,
            wcf_filter=False, bias_offsets=None, gain_od_law="lin", drive_pi=False, clipper_mode="dc", push_net="dc0",
            cex="1n", rex1="1Meg", rex2="330k", rwat="300k", bypass_sw="relay",
            rwa="3.3k", rwk="1k", rdw="10k", rwb1="820k"):
    """sw: dict overriding any switch state, keys among
    ldr1 ldr2 ldr3 ldr4 ldrx mute push br cr1 cr2 cl1 cl2 bp1 bp2 dir ext cc20 cc22
    """
    m = variant == "mod"
    if buf_filter is None:
        buf_filter = m          # filtered grid bias for the V1B buffer is part of the final design
    sw = dict(sw or {})
    L = [f"* SLO {variant}", ".include tubes.lib",
         ".model DX D(IS=1n RS=0.5 BV=1500)",
         ".model DR D(IS=10n RS=0.05 N=1.7 BV=1200 CJO=20p TT=5u)",
         ".options method=gear reltol=1e-3 abstol=1e-9 vntol=1e-5 gmin=1e-12 itl4=200"]

    def tube(inst, p, g, k, kind):
        if noise_req and kind in REQ:
            L.append(f"Rnq{inst} {g} {g}nq {REQ[kind]:g}")
            g = f"{g}nq"
        L.append(f"X{inst} {p} {g} {k} {kind}")

    # ---------------- supply ----------------
    if psu == "ideal":
        L += ["Vraw raw 0 509", "Rsrc raw b1 45"]
    else:
        pp = dict(vpk=538.0, rw=40.0, ll=0.02, f=50.0)
        pp.update(psu_par or {})
        # phase 72 deg: the operating point starts near the loaded steady state, short settling
        L += [f"Vs1 s1 0 SIN(0 {pp['vpk']} {pp['f']} 0 0 72)", f"Vs2 0 s2 SIN(0 {pp['vpk']} {pp['f']} 0 0 72)",
              f"Rw1 s1 s1r {pp['rw']}", f"Lw1 s1r s1l {pp['ll']}", f"Rw2 s2 s2r {pp['rw']}", f"Lw2 s2r s2l {pp['ll']}",
              "D1a s1l s1m DR", "D1b s1m b1 DR", "D2a s2l s2m DR", "D2b s2m b1 DR"]
    L += ["Cb1 b1 0 200u", "Rbl b1 0 440k", "Lch b1 b2x 10", "Rch b2x b2 90", "Cb2 b2 0 100u"]
    L += ["Rd3 b2 b3 13k"] if m else ["Rd3 b2 b3 10k"]
    L += ["Cb3 b3 0 40u", "Rd4 b3 b4 15k", "Cb4 b4 0 10u", "Rd5 b3 b5 15k", "Cb5 b5 0 10u"]
    if bias_offsets:
        for side in "ab":
            for n in (1, 2):
                L.append(f"Vbias{side}{n} bias{side}{n} 0 {bias + bias_offsets.get(side + str(n), 0.0)}")
    else:
        L.append(f"Vbias bias 0 {bias}")
    if m:
        L += [f"Rdw b2 bw {rdw}", "Cbw bw 0 47u",       # dedicated feed for the White CF
              "Rdf b2 bf 22k", "Cbf bf 0 47u"]       # dedicated feed for the V1B buffer

    # ---------------- input + V1B ----------------
    if drive_pi:   # source moved to the PI input (power amp + NFB studies); guitar input grounded
        L += ["Vgin in 0 0", "Rin in 0 1Meg", "Rgs1 in g1b 68k"]
        sw.setdefault("ldr3", "off"); sw.setdefault("ldr4", "off")
    else:
        L += [f"Vin in 0 {vin_spec}", "Rin in 0 1Meg", "Rgs1 in g1b 68k"]
    tube("1b", "p1b", "g1b", "k1b", "12AX7")
    L += ["Rp1b b5 p1b 220k", "Rk1b k1b 0 1.8k"]
    if m:
        L += ["Ck1b k1b 0 0.47u", "Ck1bx k1b kbx1 0.47u", "Rkbx1 kbx1 0 1Meg"]
        sel = relay if bypass_sw == "relay" else switch
        L += sel("bp1", "kbx1", "0", sw.get("bp1", "on" if bypass == "full" else "off"))
    else:
        L += ["Ck1b k1b 0 1u"]
    s = 5.0 if m else 1.0
    if m:
        # AC-coupled 12AU7 buffer (V6A), grid biased by a divider from its own feed
        if buf_filter:
            L += ["Cbuf p1b g6a 0.047u", "Rbuf1 bf gbt 1.2Meg", "Rbuf2 gbt 0 1Meg", "Cbuft gbt 0 0.47u",
                  "Rbufg gbt g6a 1Meg"]
        else:
            L += ["Cbuf p1b g6a 0.022u", "Rbuf1 bf g6a 1.2Meg", "Rbuf2 g6a 0 1Meg"]
        tube("6a", "bf", "g6a", "k6a", "12AU7")
        L += ["Rk6a k6a 0 47k"]
        src = "k6a"
    else:
        src = "p1b"
    # OD divider: series 470k || 2nF, pot 500k lin, bright 1nF top->wiper
    L += [f"Cc1 {src} c0 {0.02e-6 * s:.4g}", f"Rat1 c0 odt {470e3 / s:.6g}", f"Cpk1 c0 odt {2e-9 * s:.4g}"]
    L += pot("god", "odt", "odw", "0", 500e3 / s, gain_od, gain_od_law)
    L += [f"Cbr odt odw {1e-9 * s:.4g}"]
    # Normal (clean channel) divider: crunch = 470k + pot ; clean = 470k + 470k with 39k || pot
    rs = 470e3 / s if not m else 91e3
    rsh = 39e3 if not m else 8.2e3
    cbn = 470e-12 if not m else 2.2e-9
    if not m:
        if crunch:
            L += [f"Rat2 c0 cnt {rs:.6g}"]
        else:
            L += [f"Rat2a c0 cn1 {rs:.6g}", f"Rat2 cn1 cnt {rs:.6g}", f"Rcl39 cnt 0 {rsh:.6g}"]
        top = "c0" if crunch else "cn1"
        if bright_n:
            L += [f"Cbn {top} cnt {cbn:.4g}"]
    else:
        # LDR version of the crunch/clean DPDT and of the bright switch
        L += [f"Rat2a c0 cn1 {rs:.6g}", f"Rat2 cn1 cnt {rs:.6g}", f"Rcl39 cnt cr2 {rsh - LDR_ON:.6g}"]
        L += switch("cr1", "c0", "cn1", sw.get("cr1", "on" if crunch else "off"))
        L += switch("cr2", "cr2", "0", sw.get("cr2", "off" if crunch else "on"))
        L += [f"Cbn cn1 brn {cbn:.4g}"]
        L += switch("br", "brn", "cnt", sw.get("br", "on" if bright_n else "off"))
    L += pot("gn", "cnt", "cnw", "0", 500e3 / s, gain_n)
    # clean preamp 2 (V1A)
    tube("1a", "p1a", "cnw", "k1a", "12AX7")
    L += ["Rp1a b5 p1a 100k", "Rk1a k1a 0 2.2k", "Cc1a p1a c1a 0.02u"]
    # OD preamp 2 (V2A)
    L += ["Rgs2 odw g2a 470k"]
    tube("2a", "p2a", "g2a", "k2a", "12AX7")
    L += ["Rp2a b4 p2a 100k", "Rk2a k2a 0 1.8k"]
    if m:
        L += ["Ck2a k2a 0 0.47u", "Ck2ax k2a kbx2 0.47u", "Rkbx2 kbx2 0 1Meg"]
        sel = relay if bypass_sw == "relay" else switch
        L += sel("bp2", "kbx2", "0", sw.get("bp2", "on" if bypass == "full" else "off"))
    else:
        L += ["Ck2a k2a 0 1u"]
    # coupling after V2A (20 nF, or 2.2 nF by relay in the mod) and optional extra stage
    if not m:
        L += ["Cc2a p2a a1 0.02u"]
    else:
        # both caps stay charged through 1M bleeders; relays select which one feeds a1
        L += ["Cc2a p2a n20 0.02u", "Rbl20 n20 0 4.7Meg", "Cc2s p2a n22 2.2n", "Rbl22 n22 0 4.7Meg"]
        big = cc_v2a == "20n"
        L += relay("cc20", "n20", "dsel", sw.get("cc20", "on" if big else "off"))
        L += relay("cc22", "n22", "dsel", sw.get("cc22", "off" if big else "on"))
        # direct path / extra stage (V6B) selection by two LDRs
        # input attenuator of the extra stage at 10x the first design's impedance: it hangs on the
        # V2A plate permanently and 62k there cost 4 dB of OD gain with the stage switched off
        L += [f"Cex p2a ex0 {cex}", f"Rex1 ex0 g6b {rex1}", f"Rex2 g6b 0 {rex2}",
              "Rdx b2 bx 68k", "Cbx bx 0 10u"]
        tube("6b", "p6b", "g6b", "k6b", "12AU7")
        L += ["Rp6b bx p6b 100k", "Rk6b k6b 0 3.3k", "Ck6b k6b 0 0.68u", "Cc6b p6b e1 0.02u", "Rble e1 0 4.7Meg"]
        L += switch("dir", "dsel", "a1", sw.get("dir", "off" if extra else "on"))
        L += switch("ext", "e1", "a1", sw.get("ext", "on" if extra else "off"))
    # cold clipper input attenuator, LDR1 and V2B
    L += ["Rat4 a1 g2b 470k", "Rat5 g2b 0 1Meg"]
    L += switch("ldr1", "g2b", "0", sw.get("ldr1", "off" if channel == "od" else "on"))
    tube("2b", "p2b", "g2b", "k2b", "12AX7")
    L += ["Rk2b k2b 0 39k", "Rp2b b4 p2b 100k", "Cp2b b4 p2b 1n", "Cc2b p2b o3 0.02u", "Rap o3 0 2.2Meg"]
    if m:
        # cold clipper cathode: 39k, || (12k + LDR) -> ~9.7k, || (3.9k + LDR) -> ~4.4k
        if clipper_mode == "dc":
            L += ["Rcf1 k2b kc1 12k", "Rcf2 k2b kc2 3.9k"]
        else:
            # AC-coupled variant: the extra resistors only change the AC degeneration, the
            # cold bias set by 39k stays put (1M bleeders keep the 4.7 uF charged)
            L += ["Rcf1 k2b kc1a 12k", "Ccf1 kc1a kc1 4.7u", "Rbcf1 kc1 0 1Meg",
                  "Rcf2 k2b kc2a 3.9k", "Ccf2 kc2a kc2 4.7u", "Rbcf2 kc2 0 1Meg"]
        L += switch("cl1", "kc1", "0", sw.get("cl1", "on" if clipper == "10k" else "off"))
        L += switch("cl2", "kc2", "0", sw.get("cl2", "on" if clipper == "4k4" else "off"))
    L += switch("ldr2", "o3", "jn", sw.get("ldr2", "on" if channel == "od" else "off"))
    # clean contribution into the junction; muted by LDRx when the inverting extra stage is in
    if m:
        L += ["Rat3 c1a jx 2.2Meg", "Cpk3 c1a jx 120p"]
        L += switch("ldrx", "jx", "jn", sw.get("ldrx", "off" if extra else "on"))
    else:
        L += ["Rat3 c1a jn 2.2Meg", "Cpk3 c1a jn 120p"]
    # OD4 (V3B) + DC-coupled cathode follower (V3A)
    L += ["Rgl jn 0 330k", "Rgs3 jn g3b 220k"]
    tube("3b", "p3b", "g3b", "k3b", "12AX7")
    L += ["Rp3b b3 p3b 220k", "Rk3b k3b 0 1.8k", "Ck3b k3b 0 1u"]
    tube("3a", "b3", "p3b", "k3a", "12AX7")
    if not m:
        L += ["Rk3a k3a fx1 100k", "Rrl fx1 0 1k", "Cfx fx1 g4b 1u", "Rgl4 g4b 0 1Meg"]
        tube("4b", "p4b", "g4b", "k4b", "12AX7")
        L += ["Rp4b b3 p4b 220k", "Rk4b k4b 0 2.2k", "Ck4b k4b 0 25u"]
        tube("4a", "b3", "p4b", "ts", "12AX7")
        L += ["Rk4a ts 0 100k"]
        st = dict(C1=470e-12, Rslope=47e3, Cb=20e-9, Cm=20e-9, Rt=250e3, Rb=1e6, Rm=25e3, Rmv=1e6)
    else:
        if push_net == "dc0":
            # attenuator moved between two coupling caps: the push LDR sits at 0 V DC
            L += ["Rk3a k3a 0 100k", "Cw0 k3a w0 0.1u", "Rbw0 w0 0 220k", f"Rwat w0 w1 {rwat}", "Cw1 w1 gw 0.1u"]
            L += switch("push", "w0", "w1", sw.get("push", "on" if push else "off"))
        else:
            L += ["Rk3a k3a 0 100k", "Cw0 k3a w0 0.1u", "Rwat w0 gw 330k"]
            L += switch("push", "w0", "gw", sw.get("push", "on" if push else "off"))
        if wcf_filter:
            L += ["Rwb1 bw gwb 1Meg", "Rwb2 gwb 0 1Meg", "Cwb gwb 0 0.47u", "Rwbg gwb gw 470k"]
        else:
            L += [f"Rwb1 bw gw {rwb1}", "Rwb2 gw 0 1Meg"]
        # White cathode follower, 12AU7 (V4)
        L += [f"Rwa bw pw1 {rwa}"]
        tube("4a", "pw1", "gw", "ts", "12AU7")
        L += ["Cwc pw1 gw2 0.47u", "Rwg gw2 0 1Meg"]
        tube("4b", "ts", "gw2", "kw2", "12AU7")
        L += [f"Rwk kw2 0 {rwk}", "Cwk kw2 0 220u"]
        st = dict(C1=5.6e-9, Rslope=4.7e3, Cb=220e-9, Cm=220e-9, Rt=20e3, Rb=100e3, Rm=2.5e3, Rmv=100e3)
    # tone stack
    L += [f"Ctr ts tt {st['C1']:.4g}", f"Rsl ts ta {st['Rslope']:.6g}", f"Cbs ta tb {st['Cb']:.4g}",
          f"Cmd ta tmw {st['Cm']:.4g}"]
    L += pot("tr", "tt", "tw", "tb", st["Rt"], treble)
    L += [f"Rbs tb tm {max(st['Rb'] * log_taper(bass), 1):.6g}"]
    L += pot("md", "tm", "tmw", "0", st["Rm"], mid)
    # masters (both load the stack), selected by LDR3 / LDR4; mute LDR shunts the PI input
    L += pot("mod", "tw", "mw", "0", st["Rmv"], master, "log")
    L += pot("mn", "tw", "mnw", "0", st["Rmv"], master_n, "log")
    L += switch("ldr3", "mw", "piin", sw.get("ldr3", "on" if channel == "od" else "off"))
    L += switch("ldr4", "mnw", "piin", sw.get("ldr4", "off" if channel == "od" else "on"))
    if m or "mute" in sw:
        L += switch("mute", "piin", "0", sw.get("mute", "off"))

    # ---------------- phase inverter (V5) and NFB network ----------------
    scaled10 = depth is not None and depth_net == "scaled10"
    rtail = "14.3k" if scaled10 else "10k"
    if drive_pi:
        L += [f"Vin pis 0 {vin_spec}", "Rpis pis piin 1k"]
    L += ["Cpi piin g5b 0.02u", "Rgl5b g5b pt 1Meg", "Rgl5a g5a pt 1Meg"]
    tube("5b", "p5b", "g5b", "pk", "12AX7")
    tube("5a", "p5a", "g5a", "pk", "12AX7")
    L += ["Rpk pk pt 470", f"Rtail pt nfb {rtail}",
          "Rp5b b3 p5b 82k", "Rp5a b3 p5a 100k", "Csn p5b p5a 47p", "Csh g5a nfb 0.1u"]
    L += ["Rnfg nfb 0 470"] if scaled10 else ["Rnfg nfb 0 4.7k"]
    if scaled10:
        L += ["Cpr nfb pr 1.2u", f"Rpres pr 0 {max(2e3 * (1 - presence), 0.1):.6g}"]
    elif m:
        L += ["Cpr nfb pr 0.12u", f"Rpres pr 0 {max(20e3 * (1 - presence), 1):.6g}"]
    else:
        L += ["Cpr nfb pr 0.1u", f"Rpres pr 0 {max(25e3 * (1 - presence), 1):.6g}"]
    if depth is None:
        L += ["Rnfb sec nfb 39k"]
    else:
        net = depth_net or ("orig" if not m else "mod47")
        rmax, cdep, cdc, rnfb, law = dict(
            orig=(1e6, 4.7e-9, 0.1e-6, 39e3, "log"),
            mod47=(100e3, 47e-9, 0.1e-6, 39e3, "log"),
            mod4n7=(100e3, 4.7e-9, 0.1e-6, 39e3, "log"),
            lin100k=(100e3, 4.7e-9, 0.1e-6, 39e3, "lin"),
            scaled10=(100e3, 47e-9, 1e-6, 3.9e3, "log"))[net]
        f = log_taper(depth) if law == "log" else depth
        L += [f"Rnfb nx nfb {rnfb:g}", f"Cdc nd nx {cdc:g}",
              f"Rdep sec nd {max(rmax * f, 1):.6g}", f"Cdep sec nd {cdep:g}"]

    # ---------------- power stage (2 x 2 6L6GC) ----------------
    for side, pin, plate in (("a", "p5b", "pa"), ("b", "p5a", "pb")):
        if bias_offsets:
            # individual bias: one coupling cap and one grid leak per tube (same load on the PI)
            for n in (1, 2):
                L += [f"Cpo{side}{n} {pin} gl{side}{n} 0.022u", f"Rgl{side}{n} gl{side}{n} bias{side}{n} 440k"]
        else:
            L += [f"Cpo{side} {pin} gl{side} 0.047u", f"Rgl{side} gl{side} bias 220k"]
        for n in (1, 2):
            k = "0"
            if m:
                k = f"ks{side}{n}"
                L += [f"Rsense{side}{n} {k} 0 1"]
            gl = f"gl{side}{n}" if bias_offsets else f"gl{side}"
            L += [f"Rgst{side}{n} {gl} g{side}{n} 2.2k", f"Rscr{side}{n} b2 s{side}{n} 470",
                  f"X{side}{n} {plate} s{side}{n} g{side}{n} {k} 6L6GC"]
    # output transformer 2.2k a-a : 4 ohm tap (Lp = 18.5 H)
    lp, ratio = 18.5, 2200.0 / 4.0
    L += [f"L1 pa1 ct {lp / 4:.6g}", f"L2 ct pb1 {lp / 4:.6g}", f"L3 sec 0x {lp / ratio:.6g}",
          "R1w pa pa1 45", "R2w pb1 pb 45", "R3w 0x 0 0.15",
          "K12 L1 L2 0.999", "K13 L1 L3 0.996", "K23 L2 L3 0.996",
          "Rct ct b1 0.01",
          # winding capacitance of each half-primary (as in loop.py): physical, and it keeps the
          # leakage inductance from producing unbounded spikes when a tube cuts off
          "Cot1 pa1 ct 470p", "Cot2 ct pb1 470p"]
    if load == "spk":
        # 4 ohm cabinet equivalent: Re, voice-coil L, closed-box resonance 90 Hz with Q = 4 (peak ~23 ohm)
        L += ["Rload sec spk1 3.2", "Lvc spk1 spk2 0.25m", "Rres spk2 0 20", "Lres spk2 0 8.8m", "Cres spk2 0 0.35m"]
    else:
        L += [f"Rload sec 0 {rload}"]
    L += [analysis, ".end"]
    return "\n".join(L)
