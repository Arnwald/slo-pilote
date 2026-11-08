"""Minimal KiCad 7 schematic writer: symbols, placed parts with net labels, hierarchical sheets.

Coordinates in mm. Library symbols use KiCad's Y-up convention; the sheet uses Y-down.
Every pin of a placed part gets a short wire stub and a net label (or a power symbol, or a
no-connect flag), so connectivity is explicit and can be checked from the exported netlist.
"""
import math
import uuid

NS = uuid.UUID("6f1d3c1e-0000-4000-8000-534c4f313030")


def U(*parts):
    return str(uuid.uuid5(NS, "/".join(str(p) for p in parts)))


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def f(v):
    v = round(float(v), 4)
    return ("%.4f" % v).rstrip("0").rstrip(".") if v != int(v) else str(int(v))


FONT = "(effects (font (size 1.27 1.27)))"
FONT_HIDE = "(effects (font (size 1.27 1.27)) hide)"


# ----------------------------------------------------------------------------------------------
# symbol library
# ----------------------------------------------------------------------------------------------
class Pin:
    def __init__(self, num, name, x, y, ang, length=2.54, etype="passive", hide=False):
        self.num, self.name, self.x, self.y, self.ang, self.length = str(num), name, x, y, ang, length
        self.etype, self.hide = etype, hide

    def sexpr(self):
        h = " hide" if self.hide else ""
        return (f"(pin {self.etype} line (at {f(self.x)} {f(self.y)} {self.ang}) (length {f(self.length)}){h} "
                f"(name {q(self.name)} {FONT}) (number {q(self.num)} {FONT}))")


class Unit:
    def __init__(self, pins, graphics=()):
        self.pins = list(pins)
        self.graphics = list(graphics)


class Sym:
    def __init__(self, name, ref, units, common=(), power=False, pin_names_hidden=False, pin_numbers_hidden=False,
                 ref_at=(3.81, 2.54), val_at=(3.81, 0.0), desc=""):
        self.name, self.ref, self.units, self.common = name, ref, units, list(common)
        self.power, self.pnh, self.pnum_h = power, pin_names_hidden, pin_numbers_hidden
        self.ref_at, self.val_at, self.desc = ref_at, val_at, desc

    def pin(self, unit, num):
        for p in self.units[unit - 1].pins:
            if p.num == str(num):
                return p
        raise KeyError(f"{self.name}: unit {unit} has no pin {num}")

    def sexpr(self, lib="slo"):
        n = self.name
        head = f"(symbol {q(lib + ':' + n)}"
        if self.power:
            head += " (power)"
        if self.pnum_h:
            head += " (pin_numbers hide)"
        head += " (pin_names (offset 0.508)" + (" hide)" if self.pnh else ")")
        head += " (in_bom " + ("no" if self.power else "yes") + ") (on_board " + ("no" if self.power else "yes") + ")"
        props = [
            f'(property "Reference" {q(self.ref)} (at {f(self.ref_at[0])} {f(self.ref_at[1])} 0) {FONT_HIDE if self.power else FONT})',
            f'(property "Value" {q(n)} (at {f(self.val_at[0])} {f(self.val_at[1])} 0) {FONT})',
            f'(property "Footprint" "" (at 0 0 0) {FONT_HIDE})',
            f'(property "Datasheet" "" (at 0 0 0) {FONT_HIDE})',
        ]
        if self.desc:
            props.append(f'(property "ki_description" {q(self.desc)} (at 0 0 0) {FONT_HIDE})')
        body = [head] + props
        if self.common:
            body.append(f"(symbol {q(n + '_0_1')} " + " ".join(self.common) + ")")
        for i, u in enumerate(self.units, start=1):
            g = " ".join(u.graphics)
            ps = " ".join(p.sexpr() for p in u.pins)
            body.append(f"(symbol {q(n + '_' + str(i) + '_1')} {g} {ps})")
        return " ".join(body) + ")"


def rect(x1, y1, x2, y2, w=0.254, fill="none"):
    return f"(rectangle (start {f(x1)} {f(y1)}) (end {f(x2)} {f(y2)}) (stroke (width {f(w)}) (type default)) (fill (type {fill})))"


def poly(pts, w=0.254, fill="none"):
    p = " ".join(f"(xy {f(x)} {f(y)})" for x, y in pts)
    return f"(polyline (pts {p}) (stroke (width {f(w)}) (type default)) (fill (type {fill})))"


def dashed(pts, w=0.254):
    p = " ".join(f"(xy {f(x)} {f(y)})" for x, y in pts)
    return f"(polyline (pts {p}) (stroke (width {f(w)}) (type dash)) (fill (type none)))"


def circle(x, y, r, w=0.254, fill="none"):
    return f"(circle (center {f(x)} {f(y)}) (radius {f(r)}) (stroke (width {f(w)}) (type default)) (fill (type {fill})))"


def arc(sx, sy, mx, my, ex, ey, w=0.254):
    return f"(arc (start {f(sx)} {f(sy)}) (mid {f(mx)} {f(my)}) (end {f(ex)} {f(ey)}) (stroke (width {f(w)}) (type default)) (fill (type none)))"


def text(s, x, y, size=1.27, ang=0):
    return f"(text {q(s)} (at {f(x)} {f(y)} {ang * 10 if False else ang}) (effects (font (size {f(size)} {f(size)}))))"


def build_library():
    S = {}
    # ---- passives -------------------------------------------------------------------------
    S["R"] = Sym("R", "R", [Unit([Pin(1, "~", 0, 3.81, 270, 1.27), Pin(2, "~", 0, -3.81, 90, 1.27)],
                               [rect(-1.016, -2.54, 1.016, 2.54)])], pin_names_hidden=True, pin_numbers_hidden=True,
                 ref_at=(2.54, 1.27), val_at=(2.54, -1.27))
    S["C"] = Sym("C", "C", [Unit([Pin(1, "~", 0, 3.81, 270, 3.048), Pin(2, "~", 0, -3.81, 90, 3.048)],
                               [poly([(-2.032, 0.762), (2.032, 0.762)], 0.508), poly([(-2.032, -0.762), (2.032, -0.762)], 0.508)])],
                 pin_names_hidden=True, pin_numbers_hidden=True, ref_at=(2.794, 1.27), val_at=(2.794, -1.27))
    S["CP"] = Sym("CP", "C", [Unit([Pin(1, "+", 0, 3.81, 270, 3.048), Pin(2, "-", 0, -3.81, 90, 3.048)],
                                 [poly([(-2.032, 0.762), (2.032, 0.762)], 0.508),
                                  rect(-2.032, -0.508, 2.032, -1.016, 0.254, "outline"),
                                  poly([(-1.778, 2.286), (-0.762, 2.286)], 0.2), poly([(-1.27, 1.778), (-1.27, 2.794)], 0.2)])],
                  pin_names_hidden=True, pin_numbers_hidden=True, ref_at=(2.794, 1.27), val_at=(2.794, -1.27))
    S["L"] = Sym("L", "L", [Unit([Pin(1, "1", 0, 6.35, 270, 1.27), Pin(2, "2", 0, -6.35, 90, 1.27)],
                               [arc(0, 5.08, 1.27, 3.81, 0, 2.54), arc(0, 2.54, 1.27, 1.27, 0, 0),
                                arc(0, 0, 1.27, -1.27, 0, -2.54), arc(0, -2.54, 1.27, -3.81, 0, -5.08),
                                poly([(2.286, 5.08), (2.286, -5.08)], 0.254), poly([(2.794, 5.08), (2.794, -5.08)], 0.254)])],
                 pin_names_hidden=True, pin_numbers_hidden=True, ref_at=(3.81, 1.27), val_at=(3.81, -1.27))
    S["D"] = Sym("D", "D", [Unit([Pin(1, "A", -3.81, 0, 0, 2.54), Pin(2, "K", 3.81, 0, 180, 2.54)],
                               [poly([(-1.27, 1.27), (-1.27, -1.27), (1.27, 0), (-1.27, 1.27)], 0.254, "outline"),
                                poly([(1.27, 1.27), (1.27, -1.27)], 0.254)])],
                 pin_names_hidden=True, pin_numbers_hidden=True, ref_at=(0, 2.54), val_at=(0, -2.54))
    S["LED"] = Sym("LED", "D", [Unit([Pin(1, "A", 0, 3.81, 270, 2.54), Pin(2, "K", 0, -3.81, 90, 2.54)],
                                   [poly([(-1.27, 1.27), (1.27, 1.27), (0, -1.27), (-1.27, 1.27)], 0.254, "outline"),
                                    poly([(-1.27, -1.27), (1.27, -1.27)], 0.254),
                                    poly([(1.778, 0.508), (3.048, -0.762)], 0.15), poly([(1.778, -0.508), (3.048, -1.778)], 0.15)])],
                   pin_names_hidden=True, pin_numbers_hidden=True, ref_at=(3.81, 1.27), val_at=(3.81, -1.27))
    S["FUSE"] = Sym("FUSE", "F", [Unit([Pin(1, "~", -3.81, 0, 0, 1.27), Pin(2, "~", 3.81, 0, 180, 1.27)],
                                     [rect(-2.54, -1.016, 2.54, 1.016), poly([(-2.54, 0), (2.54, 0)], 0.15)])],
                    pin_names_hidden=True, pin_numbers_hidden=True, ref_at=(0, 2.54), val_at=(0, -2.54))
    pot_g = [rect(-1.016, -2.54, 1.016, 2.54), poly([(2.54, 0), (1.27, 0)], 0.254),
             poly([(1.27, 0), (1.905, 0.508), (1.905, -0.508), (1.27, 0)], 0.254, "outline")]
    S["POT"] = Sym("POT", "RV", [Unit([Pin(3, "3", 0, 5.08, 270, 2.54), Pin(2, "W", 5.08, 0, 180, 2.54),
                                       Pin(1, "1", 0, -5.08, 90, 2.54)], pot_g)],
                   pin_names_hidden=True, ref_at=(-3.81, 1.27), val_at=(-3.81, -1.27))
    # motorized ALPS RK168: audio gang(s), sense gang, motor
    motor_g = [circle(0, 0, 2.54), text("M", 0, 0, 1.778)]
    # top pin = clockwise end (3), bottom = counter-clockwise end (1): R(1-W) grows clockwise
    gang = lambda a, b, c: Unit([Pin(c, "3", 0, 5.08, 270, 2.54), Pin(b, "W", 5.08, 0, 180, 2.54),
                                 Pin(a, "1", 0, -5.08, 90, 2.54)], pot_g)
    S["ALPS_2G"] = Sym("ALPS_2G", "RV", [gang(1, 2, 3), gang(4, 5, 6),
                                         Unit([Pin("M+", "M+", 0, 5.08, 270, 2.54), Pin("M-", "M-", 0, -5.08, 90, 2.54)], motor_g)],
                       pin_names_hidden=True, ref_at=(-3.81, 1.27), val_at=(-3.81, -1.27),
                       desc="ALPS RK16812MG motorise : A piste audio, B piste capteur, C moteur ; 1 = extremite anti-horaire")
    # ---- tubes ----------------------------------------------------------------------------
    tri_g = [circle(0, 0, 6.35), poly([(-2.54, 3.81), (2.54, 3.81)], 0.254), poly([(0, 3.81), (0, 6.35)], 0.254),
             dashed([(-2.54, 0), (2.54, 0)]), poly([(-6.35, 0), (-2.54, 0)], 0.254),
             poly([(-2.54, -2.54), (2.54, -2.54)], 0.254), poly([(0, -2.54), (0, -6.35)], 0.254)]
    tri = lambda p, g, k: Unit([Pin(p, "P", 0, 10.16, 270, 3.81), Pin(g, "G", -10.16, 0, 0, 3.81),
                                Pin(k, "K", 0, -10.16, 90, 3.81)], tri_g)
    heat_g = [circle(0, 0, 3.81), arc(-1.27, -0.635, 0, 0.635, 1.27, -0.635)]
    heat = Unit([Pin(4, "F1", -6.35, 0, 0, 2.54), Pin(5, "F2", 6.35, 0, 180, 2.54), Pin(9, "CT", 0, -6.35, 90, 2.54)], heat_g)
    for t in ("12AX7", "12AU7"):
        S[t] = Sym(t, "V", [tri(1, 2, 3), tri(6, 7, 8), heat], pin_names_hidden=True, ref_at=(7.62, 5.08), val_at=(7.62, -5.08),
                   desc=f"{t} double triode noval : A broches 1-2-3, B 6-7-8, C chauffage 4-5-9")
    pent_g = [circle(0, 0, 7.62), poly([(-3.81, 5.08), (3.81, 5.08)], 0.254), poly([(0, 5.08), (0, 7.62)], 0.254),
              dashed([(-3.81, 1.27), (3.81, 1.27)]), dashed([(-3.81, -0.635), (3.81, -0.635)]),
              poly([(-7.62, 1.27), (-3.81, 1.27)], 0.254), poly([(7.62, -0.635), (3.81, -0.635)], 0.254),
              poly([(-3.81, -3.81), (3.81, -3.81)], 0.254), poly([(0, -3.81), (0, -7.62)], 0.254)]
    S["6L6GC"] = Sym("6L6GC", "V", [Unit([Pin(3, "P", 0, 11.43, 270, 3.81), Pin(5, "G1", -11.43, 1.27, 0, 3.81),
                                          Pin(4, "G2", 11.43, -0.635, 180, 3.81), Pin(8, "K", 0, -11.43, 90, 3.81)], pent_g),
                                     Unit([Pin(2, "F1", -6.35, 0, 0, 2.54), Pin(7, "F2", 6.35, 0, 180, 2.54)], heat_g)],
                     pin_names_hidden=True, ref_at=(8.89, 6.35), val_at=(8.89, -6.35),
                     desc="6L6GC octal : P 3, G2 4, G1 5, K 8, chauffage 2-7")
    # ---- LDR optocoupler (cell unit + LED unit) ------------------------------------------------
    ldr_g = [rect(-1.016, -2.54, 1.016, 2.54), poly([(-3.556, 2.032), (-1.778, 0.508)], 0.15),
             poly([(-3.556, 0.508), (-1.778, -1.016)], 0.15)]
    S["VTL5C1"] = Sym("VTL5C1", "LDR", [Unit([Pin(3, "R", 0, 5.08, 270, 2.54), Pin(4, "R", 0, -5.08, 90, 2.54)], ldr_g),
                                        Unit([Pin(1, "A", 0, 5.08, 270, 3.81), Pin(2, "K", 0, -5.08, 90, 3.81)],
                                             [poly([(-1.27, 1.27), (1.27, 1.27), (0, -1.27), (-1.27, 1.27)], 0.254, "outline"),
                                              poly([(-1.27, -1.27), (1.27, -1.27)], 0.254),
                                              poly([(1.778, 0.508), (3.556, -0.508)], 0.15)])],
                      pin_names_hidden=True, pin_numbers_hidden=True, ref_at=(3.81, 1.27), val_at=(3.81, -1.27),
                      desc="Xvive VTL5C1 : A cellule (3-4), B LED (1 anode, 2 cathode) ; brochage a verifier")
    # ---- relay: two SPDT contact units + coil --------------------------------------------------
    cont_g = [circle(-2.54, 0, 0.508), circle(2.54, 2.54, 0.508), circle(2.54, -2.54, 0.508),
              poly([(-2.032, 0.254), (2.286, 2.286)], 0.254)]
    cont = lambda c, nc, no: Unit([Pin(c, "C", -5.08, 0, 0, 2.032), Pin(nc, "NC", 5.08, 2.54, 180, 2.032),
                                   Pin(no, "NO", 5.08, -2.54, 180, 2.032)], cont_g)
    coil = Unit([Pin(7, "+", 0, 5.08, 270, 2.54), Pin(8, "-", 0, -5.08, 90, 2.54)],
                [rect(-1.905, -2.54, 1.905, 2.54), poly([(-1.905, -2.54), (1.905, 2.54)], 0.15)])
    S["RELAY_2C"] = Sym("RELAY_2C", "K", [cont(1, 2, 3), cont(4, 5, 6), coil], pin_names_hidden=True,
                        ref_at=(0, 5.08), val_at=(0, -5.08),
                        desc="Relais signal 2 inverseurs (type Omron G6K-2, bobine 5 V) ; numerotation generique")
    # ---- magnetics --------------------------------------------------------------------------
    def coils(x, y0, n, side):
        g = []
        for i in range(n):
            ya, yb = y0 - 2.54 * i, y0 - 2.54 * (i + 1)
            g.append(arc(x, ya, x + side * 1.27, (ya + yb) / 2, x, yb))
        return g
    pt_pins = [Pin(1, "0V", -12.7, 5.08, 0, 5.08), Pin(2, "230V", -12.7, -5.08, 0, 5.08),
               Pin(3, "HT1", 12.7, 25.4, 180, 5.08), Pin(4, "HT_CT", 12.7, 20.32, 180, 5.08), Pin(5, "HT2", 12.7, 15.24, 180, 5.08),
               Pin(6, "BIAS", 12.7, 10.16, 180, 5.08),
               Pin(7, "6V3_A1", 12.7, 2.54, 180, 5.08), Pin(8, "6V3_ACT", 12.7, -2.54, 180, 5.08),
               Pin(9, "6V3_A2", 12.7, -7.62, 180, 5.08),
               Pin(10, "6V3_B1", 12.7, -15.24, 180, 5.08), Pin(11, "6V3_BCT", 12.7, -20.32, 180, 5.08),
               Pin(12, "6V3_B2", 12.7, -25.4, 180, 5.08)]
    S["PT_SLO"] = Sym("PT_SLO", "T", [Unit(pt_pins, [rect(-7.62, -27.94, 7.62, 27.94), poly([(0, 27.94), (0, -27.94)], 0.254),
                                                    text("230 V", -3.81, 0, 1.0), text("360-0-360 V", 3.81, 22.86, 0.9),
                                                    text("prise 60 V", 3.81, 12.7, 0.9),
                                                    text("6,3 V 7,5 A", 3.81, 0, 0.9), text("6,3 V 3 A", 3.81, -17.78, 0.9)])],
                      pin_names_hidden=True, ref_at=(0, 30.48), val_at=(0, -30.48),
                      desc="TT-SLO100 : 230 V ; HT 360-0-360 V 400 mA avec prise 60 V (polarisation) ; 6,3 V PM 7,5 A ; 6,3 V PM 3 A")
    ot_pins = [Pin(1, "PA", -12.7, 7.62, 0, 5.08), Pin(2, "CT", -12.7, 0, 0, 5.08), Pin(3, "PB", -12.7, -7.62, 0, 5.08),
               Pin(4, "COM", 12.7, -7.62, 180, 5.08), Pin(5, "4", 12.7, -2.54, 180, 5.08), Pin(6, "8", 12.7, 2.54, 180, 5.08),
               Pin(7, "16", 12.7, 7.62, 180, 5.08)]
    S["OT_SLO"] = Sym("OT_SLO", "T", [Unit(ot_pins, [rect(-7.62, -10.16, 7.62, 10.16), poly([(0, 10.16), (0, -10.16)], 0.254),
                                                    text("2,2 k", -3.81, 0, 1.0), text("4/8/16", 3.81, 0, 1.0)])],
                      pin_names_hidden=False, ref_at=(0, 12.7), val_at=(0, -12.7),
                      desc="TT-SLO100 transfo de sortie 2,2 kOhm a-a, 4/8/16 Ohm")
    S["T_LV"] = Sym("T_LV", "T", [Unit([Pin(1, "0V", -12.7, 5.08, 0, 5.08), Pin(2, "230V", -12.7, -5.08, 0, 5.08),
                                        Pin(3, "S1", 12.7, 7.62, 180, 5.08), Pin(4, "S1'", 12.7, 2.54, 180, 5.08),
                                        Pin(5, "S2", 12.7, -2.54, 180, 5.08), Pin(6, "S2'", 12.7, -7.62, 180, 5.08)],
                                       [rect(-7.62, -10.16, 7.62, 10.16), poly([(0, 10.16), (0, -10.16)], 0.254),
                                        text("2 x 15 V", 3.81, 0, 1.0)])],
                  pin_names_hidden=False, ref_at=(0, 12.7), val_at=(0, -12.7))
    # ---- switches and connectors ------------------------------------------------------------
    S["SW_SPST"] = Sym("SW_SPST", "SW", [Unit([Pin(1, "~", -5.08, 0, 0, 2.54), Pin(2, "~", 5.08, 0, 180, 2.54)],
                                              [circle(-2.032, 0, 0.508), circle(2.032, 0, 0.508), poly([(-1.524, 0.254), (1.778, 1.778)], 0.254)])],
                       pin_names_hidden=True, pin_numbers_hidden=True, ref_at=(0, 3.175), val_at=(0, -2.54))
    S["SW_DPST"] = Sym("SW_DPST", "SW", [Unit([Pin(1, "~", -5.08, 0, 0, 2.54), Pin(2, "~", 5.08, 0, 180, 2.54)],
                                              [circle(-2.032, 0, 0.508), circle(2.032, 0, 0.508), poly([(-1.524, 0.254), (1.778, 1.778)], 0.254)]),
                                         Unit([Pin(3, "~", -5.08, 0, 0, 2.54), Pin(4, "~", 5.08, 0, 180, 2.54)],
                                              [circle(-2.032, 0, 0.508), circle(2.032, 0, 0.508), poly([(-1.524, 0.254), (1.778, 1.778)], 0.254)])],
                       pin_names_hidden=True, pin_numbers_hidden=True, ref_at=(0, 3.175), val_at=(0, -2.54))
    S["SW_1P3T"] = Sym("SW_1P3T", "SW", [Unit([Pin("C", "C", -7.62, 0, 0, 2.54), Pin(1, "1", 7.62, 2.54, 180, 2.54),
                                              Pin(2, "2", 7.62, 0, 180, 2.54), Pin(3, "3", 7.62, -2.54, 180, 2.54)],
                                             [circle(-4.572, 0, 0.508), circle(4.572, 2.54, 0.508), circle(4.572, 0, 0.508),
                                              circle(4.572, -2.54, 0.508), poly([(-4.064, 0.254), (4.064, 2.286)], 0.254)])],
                       pin_names_hidden=False, ref_at=(0, 5.08), val_at=(0, -5.08))
    jack_g = [rect(-2.54, -2.54, 2.54, 2.54)]
    S["JACK_TS"] = Sym("JACK_TS", "J", [Unit([Pin("T", "T", 7.62, 1.27, 180, 5.08), Pin("S", "S", 7.62, -1.27, 180, 5.08)], jack_g)],
                       ref_at=(0, 3.81), val_at=(0, -3.81))
    S["JACK_TSN"] = Sym("JACK_TSN", "J", [Unit([Pin("T", "T", 7.62, 1.27, 180, 5.08), Pin("S", "S", 7.62, -1.27, 180, 5.08),
                                                Pin("TN", "TN", 7.62, 3.81, 180, 5.08)], [rect(-2.54, -2.54, 2.54, 5.08)])],
                        ref_at=(0, 6.35), val_at=(0, -3.81))
    S["JACK_TRS"] = Sym("JACK_TRS", "J", [Unit([Pin("T", "T", 7.62, 2.54, 180, 5.08), Pin("R", "R", 7.62, 0, 180, 5.08),
                                                Pin("S", "S", 7.62, -2.54, 180, 5.08)], [rect(-2.54, -3.81, 2.54, 3.81)])],
                        ref_at=(0, 5.08), val_at=(0, -5.08))
    S["IEC"] = Sym("IEC", "J", [Unit([Pin("L", "L", 7.62, 2.54, 180, 5.08), Pin("N", "N", 7.62, 0, 180, 5.08),
                                      Pin("PE", "PE", 7.62, -2.54, 180, 5.08)], [rect(-2.54, -3.81, 2.54, 3.81)])],
                   ref_at=(0, 5.08), val_at=(0, -5.08))
    S["DIN5"] = Sym("DIN5", "J", [Unit([Pin(4, "4", 7.62, 2.54, 180, 5.08), Pin(2, "2", 7.62, 0, 180, 5.08),
                                        Pin(5, "5", 7.62, -2.54, 180, 5.08)], [circle(0, 0, 3.81)])],
                    ref_at=(0, 5.08), val_at=(0, -5.08))
    # chassis bolt: lug (1) bolted to the chassis (2)
    S["BOLT"] = Sym("BOLT", "E", [Unit([Pin(1, "~", 0, 3.81, 270, 1.27), Pin(2, "CH", 0, -3.81, 90, 1.27)],
                                       [circle(0, 1.27, 1.27), poly([(-2.54, -1.27), (2.54, -1.27)], 0.254),
                                        poly([(-2.54, -1.27), (-3.302, -2.54)], 0.254), poly([(0, -1.27), (-0.762, -2.54)], 0.254),
                                        poly([(2.54, -1.27), (1.778, -2.54)], 0.254)])],
                    pin_names_hidden=True, pin_numbers_hidden=True, ref_at=(3.81, 1.27), val_at=(3.81, -1.27),
                    desc="Vis de masse sur le chassis : cosse (1), chassis (2)")
    # power flag: tells the electrical rules check that a net is supplied (no part, not in the BOM)
    S["PWR_FLAG"] = Sym("PWR_FLAG", "#FLG", [Unit([Pin(1, "pwr", 0, 0, 90, 0, "power_out")],
                                                 [poly([(0, 0), (0, 1.27), (-1.016, 1.905), (0, 2.54), (1.016, 1.905), (0, 1.27)], 0.254)])],
                        power=True, pin_names_hidden=True, pin_numbers_hidden=True, ref_at=(0, 1.905), val_at=(0, 3.81),
                        desc="Drapeau d'alimentation pour le controle des regles electriques")
    return S


def ic_symbol(name, ref, left, right, width=15.24, desc=""):
    """Generic box: left/right = lists of (num, name, etype) top to bottom (None = gap)."""
    pins = []
    n = max(len(left), len(right))
    h = 2.54 * (n + 1)
    top = h / 2
    for i, p in enumerate(left):
        if p:
            pins.append(Pin(p[0], p[1], -width / 2 - 5.08, top - 2.54 * (i + 1), 0, 5.08, p[2] if len(p) > 2 else "passive"))
    for i, p in enumerate(right):
        if p:
            pins.append(Pin(p[0], p[1], width / 2 + 5.08, top - 2.54 * (i + 1), 180, 5.08, p[2] if len(p) > 2 else "passive"))
    return Sym(name, ref, [Unit(pins, [rect(-width / 2, -h / 2, width / 2, h / 2, 0.254, "background")])],
               ref_at=(0, h / 2 + 1.27), val_at=(0, -h / 2 - 1.27), desc=desc)


def opamp_units(pa, pb, pw=(8, 4)):
    """Dual op-amp: A, B (in+, in-, out), C power (V+, V-)."""
    g = [poly([(-3.81, 5.08), (-3.81, -5.08), (5.08, 0), (-3.81, 5.08)], 0.254, "background")]
    mk = lambda inp, inn, out: Unit([Pin(inp, "+", -8.89, 2.54, 0, 5.08, "input"), Pin(inn, "-", -8.89, -2.54, 0, 5.08, "input"),
                                     Pin(out, "~", 10.16, 0, 180, 5.08, "output")], g)
    pwr = Unit([Pin(pw[0], "V+", 0, 7.62, 270, 3.81, "power_in"), Pin(pw[1], "V-", 0, -7.62, 90, 3.81, "power_in")],
               [rect(-2.54, -3.81, 2.54, 3.81)])
    return [mk(*pa), mk(*pb), pwr]


def power_symbol(name, down=False):
    if down:   # ground-like: bar below the pin
        g = [poly([(0, 0), (0, -1.27), (1.27, -1.27), (0, -2.54), (-1.27, -1.27), (0, -1.27)], 0.254)]
    else:      # supply: bar above the pin
        g = [poly([(0, 0), (0, 1.27)], 0.254), poly([(-1.27, 1.27), (1.27, 1.27)], 0.254)]
    u = Unit([Pin(1, name, 0, 0, 90 if down else 270, 0, "power_in", hide=True)], g)
    return Sym(name, "#PWR", [u], power=True, pin_numbers_hidden=True, pin_names_hidden=True,
               ref_at=(0, -3.81 if down else 3.81), val_at=(0, -3.556 if down else 3.556))


# ----------------------------------------------------------------------------------------------
# placed parts and sheets
# ----------------------------------------------------------------------------------------------
def rot(px, py, deg):
    """Library point (Y up) -> sheet offset (Y down) for a symbol rotated by deg (counter-clockwise)."""
    t = math.radians(deg)
    c, s = round(math.cos(t)), round(math.sin(t))
    return px * c - py * s, -px * s - py * c


class Part:
    def __init__(self, ref, sym, value, at, unit=1, rotation=0, nets=None, fields=None):
        self.ref, self.sym, self.value, self.at, self.unit, self.rotation = ref, sym, value, at, unit, rotation
        self.nets = {str(k): v for k, v in (nets or {}).items()}
        self.fields = dict(fields or {})

    def pin_pos(self, p):
        dx, dy = rot(p.x, p.y, self.rotation)
        return self.at[0] + dx, self.at[1] + dy

    def pin_out_dir(self, p):
        """Outward direction (screen degrees: 0 right, 90 up, 180 left, 270 down) of a pin."""
        return (p.ang + 180 + self.rotation) % 360


class Sheet:
    def __init__(self, name, filename, paper="A2", title=""):
        self.name, self.filename, self.paper, self.title = name, filename, paper, title
        self.parts, self.texts, self.frames, self.labels_extra = [], [], [], []

    def add(self, part):
        self.parts.append(part)
        return part

    def note(self, s, x, y, size=1.5, bold=False):
        self.texts.append((s, x, y, size, bold))

    def frame(self, x1, y1, x2, y2, title=None):
        self.frames.append((x1, y1, x2, y2, title))


STUB = 2.54


def _dir_vec(d):
    t = math.radians(d)
    return round(math.cos(t)), -round(math.sin(t))


class Project:
    def __init__(self, name, title, rev="0.1", date="2026-11-07", company="", comments=()):
        self.name, self.title, self.rev, self.date, self.company = name, title, rev, date, company
        self.comments = list(comments)
        self.lib = {}
        self.sheets = []
        self.root_uuid = U(name, "root")
        self.pwr_count = 0
        self.root_texts = []

    def symbol(self, sym):
        self.lib[sym.name] = sym
        return sym

    def sheet(self, sh):
        self.sheets.append(sh)
        return sh

    # -------------------------------------------------------------------------------------
    def global_nets(self):
        where = {}
        for sh in self.sheets:
            for p in sh.parts:
                for n in p.nets.values():
                    if n and not self.is_power(n):
                        where.setdefault(n, set()).add(sh.name)
        return {n for n, s in where.items() if len(s) > 1 or n.startswith(("B+", "+", "-"))}

    POWER = {"GND": True, "+3V3": False, "+5V": False, "+15V": False, "-15V": True, "+V_BRUT": False, "-V_BRUT": True,
             "+24V": False}

    def is_power(self, n):
        return n in self.POWER

    def _title_block(self, sheet_title):
        c = " ".join(f"(comment {i + 1} {q(t)})" for i, t in enumerate(self.comments[:4]))
        return (f"(title_block (title {q(sheet_title)}) (date {q(self.date)}) (rev {q(self.rev)}) "
                f"(company {q(self.company)}) {c})")

    def _part_sexpr(self, p, path, out, globs, sheetname, skip=frozenset()):
        sym = self.lib[p.sym]
        x, y = p.at
        uid = U(self.name, sheetname, p.ref, p.unit)
        # reference/value text positions (kept horizontal)
        rx, ry = rot(*sym.ref_at, p.rotation)
        vx, vy = rot(*sym.val_at, p.rotation)
        fa = 0
        if p.rotation in (90, 270):
            rx, ry, vx, vy = 0, -3.3, 0, 4.6
            fa = p.rotation        # field angles are stored relative to the symbol: compensate
        jr = " (justify right)" if rx < -0.1 else ("" if abs(rx) <= 0.1 else " (justify left)")
        jv = " (justify right)" if vx < -0.1 else ("" if abs(vx) <= 0.1 else " (justify left)")
        fields = [
            f'(property "Reference" {q(p.ref)} (at {f(x + rx)} {f(y + ry)} {fa}) (effects (font (size 1.27 1.27)){jr}))',
            f'(property "Value" {q(p.value)} (at {f(x + vx)} {f(y + vy)} {fa}) (effects (font (size 1.27 1.27)){jv}))',
            f'(property "Footprint" {q(p.fields.get("Footprint", ""))} (at {f(x)} {f(y)} 0) {FONT_HIDE})',
            f'(property "Datasheet" "" (at {f(x)} {f(y)} 0) {FONT_HIDE})',
        ]
        for k, v in p.fields.items():
            if k != "Footprint":
                fields.append(f'(property {q(k)} {q(v)} (at {f(x)} {f(y)} 0) {FONT_HIDE})')
        unit = sym.units[p.unit - 1]
        pins = " ".join(f'(pin {q(pp.num)} (uuid {U(uid, "pin", pp.num)}))' for pp in unit.pins)
        out.append(f'(symbol (lib_id {q("slo:" + p.sym)}) (at {f(x)} {f(y)} {p.rotation}) (unit {p.unit}) '
                   f'(in_bom {"no" if sym.power else "yes"}) (on_board {"no" if sym.power else "yes"}) (dnp no) (uuid {uid}) '
                   + " ".join(fields) + f" {pins} "
                   f'(instances (project {q(self.name)} (path {q(path)} (reference {q(p.ref)}) (unit {p.unit})))))')
        # connections
        for pp in unit.pins:
            net = p.nets.get(pp.num, "__missing__")
            px, py = p.pin_pos(pp)
            if net == "__missing__":
                raise KeyError(f"{sheetname}: {p.ref} unit {p.unit} pin {pp.num} ({pp.name}) has no net")
            if net is None:
                out.append(f"(no_connect (at {f(px)} {f(py)}) (uuid {U(uid, 'nc', pp.num)}))")
                continue
            d = p.pin_out_dir(pp)
            vx_, vy_ = _dir_vec(d)
            ex, ey = px + vx_ * STUB, py + vy_ * STUB
            out.append(f"(wire (pts (xy {f(px)} {f(py)}) (xy {f(ex)} {f(ey)})) (stroke (width 0) (type default)) "
                       f"(uuid {U(uid, 'w', pp.num)}))")
            if self.is_power(net):
                down = self.POWER[net]
                r = (d - (270 if down else 90)) % 360
                self.pwr_count += 1
                pref = f"#PWR{self.pwr_count:04d}"
                psym = self.lib[net]
                pu = U(uid, "pwr", pp.num)
                tx, ty = rot(0, -3.556 if down else 3.556, r)
                out.append(f'(symbol (lib_id {q("slo:" + net)}) (at {f(ex)} {f(ey)} {r}) (unit 1) (in_bom no) (on_board no) '
                           f'(dnp no) (uuid {pu}) '
                           f'(property "Reference" {q(pref)} (at {f(ex)} {f(ey)} 0) {FONT_HIDE}) '
                           f'(property "Value" {q(net)} (at {f(ex + tx)} {f(ey + ty)} 0) (effects (font (size 1.0 1.0)))) '
                           f'(property "Footprint" "" (at {f(ex)} {f(ey)} 0) {FONT_HIDE}) '
                           f'(property "Datasheet" "" (at {f(ex)} {f(ey)} 0) {FONT_HIDE}) '
                           f'(pin "1" (uuid {U(pu, "p")})) '
                           f'(instances (project {q(self.name)} (path {q(path)} (reference {q(pref)}) (unit 1)))))')
            elif (p.ref, p.unit, pp.num) in skip:
                continue
            else:
                ang = 180 if d % 360 == 180 else 0     # labels always read horizontally
                just = "right" if ang == 180 else "left"
                if net in globs:
                    out.append(f'(global_label {q(net)} (shape passive) (at {f(ex)} {f(ey)} {ang}) (fields_autoplaced) '
                               f'(effects (font (size 1.27 1.27)) (justify {just})) (uuid {U(uid, "gl", pp.num)}) '
                               f'(property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {f(ex)} {f(ey)} 0) {FONT_HIDE}))')
                else:
                    out.append(f'(label {q(net)} (at {f(ex)} {f(ey)} {ang}) (fields_autoplaced) '
                               f'(effects (font (size 1.27 1.27)) (justify {just} bottom)) (uuid {U(uid, "l", pp.num)}))')


    # -------------------------------------------------------------------------------------
    def _pin_table(self, sh):
        rows = []
        for p in sh.parts:
            sym = self.lib[p.sym]
            for pp in sym.units[p.unit - 1].pins:
                net = p.nets.get(pp.num)
                px, py = p.pin_pos(pp)
                d = p.pin_out_dir(pp)
                vx_, vy_ = _dir_vec(d)
                rows.append({"key": (p.ref, p.unit, pp.num), "net": net, "px": px, "py": py,
                             "ex": px + vx_ * STUB, "ey": py + vy_ * STUB, "d": d, "part": p})
        return rows

    def _bboxes(self, sh, rows):
        boxes = []
        for p in sh.parts:
            pts = [(r["px"], r["py"]) for r in rows if r["part"] is p]
            x, y = p.at
            m = 0.65 * max((math.hypot(a - x, b - y) for a, b in pts), default=2.0)
            xs = [a for a, _ in pts] + [x - m, x + m]
            ys = [b for _, b in pts] + [y - m, y + m]
            boxes.append((min(xs), min(ys), max(xs), max(ys)))
        return boxes

    def autowire(self, sh, maxgap=45.0):
        """Joins pairs of facing pins of the same net that sit on one horizontal or vertical line
        with a straight wire, when nothing lies in the way; returns (wires, pins whose label is dropped)."""
        rows = self._pin_table(sh)
        boxes = self._bboxes(sh, rows)
        sig = [r for r in rows if r["net"] and not self.is_power(r["net"])]
        cands = []
        for i, a in enumerate(sig):
            for b in sig[i + 1:]:
                if a["net"] != b["net"] or a["part"] is b["part"]:
                    continue
                if abs(a["ey"] - b["ey"]) < 0.01:
                    l, r = (a, b) if a["ex"] < b["ex"] else (b, a)
                    if l["d"] == 0 and r["d"] == 180 and 0 < r["ex"] - l["ex"] <= maxgap:
                        cands.append((r["ex"] - l["ex"], l, r))
                elif abs(a["ex"] - b["ex"]) < 0.01:
                    t, u = (a, b) if a["ey"] < b["ey"] else (b, a)
                    if t["d"] == 270 and u["d"] == 90 and 0 < u["ey"] - t["ey"] <= maxgap:
                        cands.append((u["ey"] - t["ey"], t, u))
        cands.sort(key=lambda c: c[0])
        done, wires = set(), []
        for gap, a, b in cands:
            if a["key"] in done or b["key"] in done:
                continue
            x1, y1, x2, y2 = min(a["ex"], b["ex"]), min(a["ey"], b["ey"]), max(a["ex"], b["ex"]), max(a["ey"], b["ey"])
            horiz = abs(y1 - y2) < 0.01
            ok = True
            for r in rows:
                if r is a or r is b:
                    continue
                for (ox, oy) in ((r["px"], r["py"]), (r["ex"], r["ey"])):
                    if horiz and x1 - 0.01 <= ox <= x2 + 0.01 and abs(oy - y1) < 1.3:
                        ok = False
                    if not horiz and y1 - 0.01 <= oy <= y2 + 0.01 and abs(ox - x1) < 1.3:
                        ok = False
            for (bx1, by1, bx2, by2) in boxes:
                if horiz and by1 - 0.6 <= y1 <= by2 + 0.6 and x1 < bx2 + 0.6 and x2 > bx1 - 0.6:
                    ok = False
                if not horiz and bx1 - 0.6 <= x1 <= bx2 + 0.6 and y1 < by2 + 0.6 and y2 > by1 - 0.6:
                    ok = False
            for (w1, w2) in wires:
                if horiz and abs(w1[1] - w2[1]) < 0.01 and abs(w1[1] - y1) < 0.01 and min(w1[0], w2[0]) < x2 and max(w1[0], w2[0]) > x1:
                    ok = False
                if not horiz and abs(w1[0] - w2[0]) < 0.01 and abs(w1[0] - x1) < 0.01 and min(w1[1], w2[1]) < y2 and max(w1[1], w2[1]) > y1:
                    ok = False
            if not ok:
                continue
            done |= {a["key"], b["key"]}
            wires.append(((a["ex"], a["ey"]), (b["ex"], b["ey"])))
        # every wired pair keeps one label (it names the net); the label goes on the upper or left pin
        skip = set()
        for (p1, p2) in wires:
            for r in rows:
                if (abs(r["ex"] - p2[0]) < 0.01 and abs(r["ey"] - p2[1]) < 0.01 and r["key"] in done):
                    skip.add(r["key"])
        return wires, skip

    def write(self, folder):
        import os
        os.makedirs(folder, exist_ok=True)
        globs = self.global_nets()
        # sub-sheets
        for i, sh in enumerate(self.sheets):
            suid = U(self.name, "sheet", sh.name)
            path = f"/{self.root_uuid}/{suid}"
            used = sorted({p.sym for p in sh.parts} | {n for p in sh.parts for n in p.nets.values() if n and self.is_power(n)})
            out = [f"(kicad_sch (version 20230121) (generator eeschema) (uuid {suid})",
                   f'(paper {q(sh.paper)})', self._title_block(f"{self.title} — {sh.title or sh.name}"),
                   "(lib_symbols " + " ".join(self.lib[s].sexpr() for s in used) + ")"]
            wires, skip = self.autowire(sh)
            self.wired = getattr(self, "wired", 0) + len(wires)
            for p in sh.parts:
                self._part_sexpr(p, path, out, globs, sh.name, skip)
            for (a, b) in wires:
                out.append(f"(wire (pts (xy {f(a[0])} {f(a[1])}) (xy {f(b[0])} {f(b[1])})) (stroke (width 0) (type default)) "
                           f"(uuid {U(sh.name, 'aw', a, b)}))")
            for (s, x, y, size, bold) in sh.texts:
                b = " bold" if bold else ""
                out.append(f'(text {q(s)} (at {f(x)} {f(y)} 0) (effects (font (size {f(size)} {f(size)}){b}) (justify left bottom)) '
                           f'(uuid {U(sh.name, "txt", s, x, y)}))')
            for (x1, y1, x2, y2, title) in sh.frames:
                pts = [(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)]
                for a, b in zip(pts[:-1], pts[1:]):
                    out.append(f"(polyline (pts (xy {f(a[0])} {f(a[1])}) (xy {f(b[0])} {f(b[1])})) (stroke (width 0.25) (type dash)) "
                               f"(uuid {U(sh.name, 'fr', x1, y1, a, b)}))")
                if title:
                    out.append(f'(text {q(title)} (at {f(x1 + 2)} {f(y1 + 5)} 0) (effects (font (size 2.2 2.2) bold) (justify left bottom)) '
                               f'(uuid {U(sh.name, "frt", title, x1, y1)}))')
            out.append(")")
            open(os.path.join(folder, sh.filename), "w").write("\n".join(out))
        # root
        out = [f"(kicad_sch (version 20230121) (generator eeschema) (uuid {self.root_uuid})", '(paper "A3")',
               self._title_block(self.title), "(lib_symbols)"]
        for i, sh in enumerate(self.sheets):
            suid = U(self.name, "sheet", sh.name)
            col, row = i % 3, i // 3
            x, y = 30 + col * 125, 60 + row * 70
            out.append(f'(sheet (at {f(x)} {f(y)}) (size 100 45) (fields_autoplaced) (stroke (width 0.1524) (type solid)) '
                       f'(fill (color 0 0 0 0.0000)) (uuid {suid}) '
                       f'(property "Sheetname" {q(sh.name)} (at {f(x)} {f(y - 1)} 0) (effects (font (size 1.8 1.8) bold) (justify left bottom))) '
                       f'(property "Sheetfile" {q(sh.filename)} (at {f(x)} {f(y + 46)} 0) (effects (font (size 1.27 1.27)) (justify left top))) '
                       f'(instances (project {q(self.name)} (path {q("/" + self.root_uuid)} (page {q(str(i + 2))})))))')
        for (s, x, y, size, bold) in self.root_texts:
            b = " bold" if bold else ""
            out.append(f'(text {q(s)} (at {f(x)} {f(y)} 0) (effects (font (size {f(size)} {f(size)}){b}) (justify left bottom)) '
                       f'(uuid {U("root", "txt", s, x, y)}))')
        out.append('(sheet_instances (path "/" (page "1")))')
        out.append(")")
        open(os.path.join(folder, self.name + ".kicad_sch"), "w").write("\n".join(out))
        # project file, symbol library and library table
        import json
        open(os.path.join(folder, self.name + ".kicad_pro"), "w").write(json.dumps(
            {"meta": {"filename": self.name + ".kicad_pro", "version": 1},
             "sheets": [[self.root_uuid, "Root"]] + [[U(self.name, "sheet", s.name), s.name] for s in self.sheets]}, indent=2))
        lib = ["(kicad_symbol_lib (version 20220914) (generator kicad_symbol_editor)"]
        lib += [self.lib[s].sexpr(lib="slo").replace('(symbol "slo:', '(symbol "', 1) for s in sorted(self.lib)]
        lib.append(")")
        open(os.path.join(folder, "slo.kicad_sym"), "w").write("\n".join(lib))
        open(os.path.join(folder, "sym-lib-table"), "w").write(
            '(sym_lib_table\n  (lib (name "slo")(type "KiCad")(uri "${KIPRJMOD}/slo.kicad_sym")(options "")(descr "Symboles du projet"))\n)\n')
